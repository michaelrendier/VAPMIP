"""
skills/network.py — Multi-protocol acquisition and peer communication.

:description:
    Unified acquire() dispatches by URL scheme:
      http/https/ftp  → urllib (already in crawler)
      file://         → local copy
      ptol+tcp://     → direct Ptolemy peer over TCP
      ptol+udp://     → direct Ptolemy peer over UDP

    UDP hole punching for NAT traversal:
      Both instances register with a rendezvous server.
      Server introduces them. Both punch simultaneously.
      Keepalive UDP every 25s maintains holes through all NAT layers.
      Works through carrier CGNAT, home router, VPN stacks.

    Ptolemy-to-Ptolemy protocol (MCP — Monad Channel Protocol):
      JSON envelope: {"type": "...", "payload": ...}
      Types: learn, query, emit, sync, ping, pong

:classes:
    PtolNetwork
    PtolRendezvous
"""

import os
import json
import time
import socket
import threading
import urllib.request
import urllib.parse
import shutil
from pathlib import Path


# ── Monad Channel Protocol envelope ──────────────────────────────────────────

def _mcp(msg_type: str, **payload) -> bytes:
    return json.dumps({'type': msg_type, 'payload': payload}).encode('utf-8')

def _mcp_parse(data: bytes) -> dict:
    return json.loads(data.decode('utf-8', errors='ignore'))


# ══════════════════════════════════════════════════════════════════════════════

class PtolNetwork:
    """
    Multi-protocol data acquisition and Ptolemy peer communication.

    :param logger: PtolLogger instance.
    :param config: PtolConfig instance.
    :param monad_iface: MonadInterface (optional — for peer query handling).
    """

    def __init__(self, logger, config, monad_iface=None):
        self._logger  = logger
        self._config  = config
        self._monad   = monad_iface
        self._peers   = {}       # peer_id → {host, port, sock, last_seen}
        self._plock   = threading.Lock()
        self._udp_sock = None
        self._stop    = threading.Event()

    # ── Unified acquire ───────────────────────────────────────────────────

    def acquire(self, url: str, dest_path) -> bool:
        """
        Fetch any URL to dest_path, dispatching by scheme.

        :param url: Source URL.
        :param dest_path: Destination file path.
        :returns: True on success.
        :rtype: bool
        """
        scheme = urllib.parse.urlparse(url).scheme
        try:
            if scheme in ('http', 'https', 'ftp'):
                urllib.request.urlretrieve(url, dest_path)
                return True
            elif scheme == 'file':
                src = urllib.parse.urlparse(url).path
                shutil.copy(src, dest_path)
                return True
            elif scheme in ('ptol+tcp', 'ptol'):
                return self._ptol_tcp_fetch(url, dest_path)
            elif scheme == 'ptol+udp':
                return self._ptol_udp_fetch(url, dest_path)
        except Exception as exc:
            self._logger.skip(url, f"acquire:{exc}")
        return False

    # ── TCP peer communication ────────────────────────────────────────────

    def send_tcp(self, host: str, port: int, msg: dict,
                 timeout: int = 10) -> dict:
        """
        Send MCP message to a Ptolemy peer over TCP and return response.

        :param host: Peer hostname or IP.
        :param port: Peer TCP port.
        :param msg: Message dict.
        :param timeout: Socket timeout seconds.
        :returns: Response dict or {'error': reason}.
        :rtype: dict
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            s.connect((host, port))
            s.sendall(json.dumps(msg).encode())
            data = s.recv(65536)
            s.close()
            return json.loads(data.decode('utf-8', errors='ignore'))
        except Exception as exc:
            return {'error': str(exc)}

    def _ptol_tcp_fetch(self, url: str, dest_path) -> bool:
        """Fetch text content from a Ptolemy peer via TCP."""
        parsed = urllib.parse.urlparse(url)
        host   = parsed.hostname
        port   = parsed.port or self._config.getint('tcp_port', 7297)
        path   = parsed.path.lstrip('/')
        resp   = self.send_tcp(host, port, {'type': 'fetch', 'path': path})
        if 'text' in resp:
            with open(dest_path, 'w', encoding='utf-8') as fh:
                fh.write(resp['text'])
            return True
        return False

    # ── TCP server (for incoming peer connections) ─────────────────────────

    def start_tcp_server(self):
        """Start TCP listener for incoming Ptolemy peer connections."""
        port = self._config.getint('tcp_port', 7297)
        t = threading.Thread(target=self._tcp_server, args=(port,),
                             name='PtolTCPServer', daemon=True)
        t.start()

    def _tcp_server(self, port: int):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', port))
        s.listen(10)
        s.settimeout(1.0)
        while not self._stop.is_set():
            try:
                conn, addr = s.accept()
                threading.Thread(
                    target=self._handle_tcp, args=(conn, addr),
                    daemon=True).start()
            except socket.timeout:
                continue
            except Exception:
                break
        s.close()

    def _handle_tcp(self, conn, addr):
        try:
            data = conn.recv(65536)
            msg  = _mcp_parse(data)
            resp = self._dispatch(msg)
            conn.sendall(json.dumps(resp).encode())
        except Exception as exc:
            try:
                conn.sendall(json.dumps({'error': str(exc)}).encode())
            except Exception:
                pass
        finally:
            conn.close()

    # ── UDP peer communication ─────────────────────────────────────────────

    def start_udp_listener(self):
        """Start UDP socket for peer communication and hole-punch replies."""
        port = self._config.getint('udp_port', 7298)
        self._udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._udp_sock.bind(('', port))
        self._udp_sock.settimeout(1.0)
        t = threading.Thread(target=self._udp_listener,
                             name='PtolUDPListener', daemon=True)
        t.start()

    def _udp_listener(self):
        while not self._stop.is_set():
            try:
                data, addr = self._udp_sock.recvfrom(65536)
                if data.startswith(b'PTOL_KNOCK'):
                    self._udp_sock.sendto(b'PTOL_KNOCK_ACK', addr)
                    self._register_peer(addr[0], addr[1])
                elif data.startswith(b'PTOL_ALIVE'):
                    self._touch_peer(f"{addr[0]}:{addr[1]}")
                else:
                    msg = _mcp_parse(data)
                    resp = self._dispatch(msg)
                    self._udp_sock.sendto(
                        json.dumps(resp).encode(), addr)
            except socket.timeout:
                continue
            except Exception:
                continue

    def send_udp(self, host: str, port: int, msg: dict):
        """
        Fire-and-forget UDP message to a peer.

        :param host: Peer IP or hostname.
        :param port: Peer UDP port.
        :param msg: Message dict.
        """
        if self._udp_sock is None:
            self.start_udp_listener()
        try:
            self._udp_sock.sendto(json.dumps(msg).encode(), (host, port))
        except Exception:
            pass

    def _ptol_udp_fetch(self, url: str, dest_path) -> bool:
        parsed = urllib.parse.urlparse(url)
        host   = parsed.hostname
        port   = parsed.port or self._config.getint('udp_port', 7298)
        path   = parsed.path.lstrip('/')
        msg    = {'type': 'fetch', 'path': path}
        if self._udp_sock is None:
            self.start_udp_listener()
        try:
            self._udp_sock.sendto(json.dumps(msg).encode(), (host, port))
            self._udp_sock.settimeout(10)
            data, _ = self._udp_sock.recvfrom(65536)
            resp = _mcp_parse(data)
            if 'text' in resp:
                with open(dest_path, 'w', encoding='utf-8') as fh:
                    fh.write(resp['text'])
                return True
        except Exception:
            pass
        return False

    # ── NAT hole punching ─────────────────────────────────────────────────

    def discover_external(self, rendezvous_host: str,
                          rendezvous_port: int = 7299):
        """
        Contact rendezvous server to discover external IP:port.
        Rendezvous server simply echoes back what it sees.

        :param rendezvous_host: Public rendezvous server host.
        :param rendezvous_port: Rendezvous server port.
        :returns: (external_ip, external_port) or (None, None).
        :rtype: tuple
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(5)
        try:
            s.sendto(b'PTOL_DISCOVER', (rendezvous_host, rendezvous_port))
            data, _ = s.recvfrom(256)
            ext_ip, ext_port = data.decode().strip().split(':')
            return ext_ip, int(ext_port)
        except Exception:
            return None, None
        finally:
            s.close()

    def punch_hole(self, peer_host: str, peer_port: int,
                   my_port: int = None, attempts: int = 12) -> bool:
        """
        UDP hole punch toward peer.
        Both sides call simultaneously (coordinated via rendezvous).
        Works through CGNAT, home router NAT, VPN — up to symmetric NAT.

        :param peer_host: Peer's external IP.
        :param peer_port: Peer's external UDP port.
        :param my_port: Local UDP port (default: udp_port from config).
        :param attempts: Number of knock attempts.
        :returns: True if hole punched successfully.
        :rtype: bool
        """
        my_port  = my_port or self._config.getint('udp_port', 7298)
        punched  = threading.Event()

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.bind(('', my_port))
        except OSError:
            s.bind(('', 0))   # fallback to any port
        s.settimeout(0.5)

        def _sender():
            for _ in range(attempts):
                if punched.is_set():
                    break
                try:
                    s.sendto(b'PTOL_KNOCK', (peer_host, peer_port))
                except Exception:
                    pass
                time.sleep(0.25)

        def _listener():
            deadline = time.monotonic() + attempts * 0.5
            while time.monotonic() < deadline and not punched.is_set():
                try:
                    data, addr = s.recvfrom(256)
                    if b'PTOL' in data:
                        punched.set()
                        self._register_peer(addr[0], addr[1], sock=s)
                except socket.timeout:
                    continue

        t1 = threading.Thread(target=_sender,   daemon=True)
        t2 = threading.Thread(target=_listener, daemon=True)
        t1.start(); t2.start()
        t1.join();  t2.join()

        if not punched.is_set():
            s.close()
        return punched.is_set()

    def start_keepalive(self, interval: int = 25):
        """
        Periodic UDP keepalive to maintain NAT hole state.
        NAT tables expire ~30s — ping every 25s to keep holes open.

        :param interval: Seconds between keepalive pings.
        """
        def _loop():
            while not self._stop.is_set():
                time.sleep(interval)
                dead = []
                with self._plock:
                    for pid, peer in self._peers.items():
                        try:
                            peer['sock'].sendto(
                                b'PTOL_ALIVE', (peer['host'], peer['port']))
                            peer['last_seen'] = time.monotonic()
                        except Exception:
                            dead.append(pid)
                with self._plock:
                    for pid in dead:
                        del self._peers[pid]
        threading.Thread(target=_loop, name='PtolKeepalive',
                         daemon=True).start()

    # ── Peer registry ─────────────────────────────────────────────────────

    def _register_peer(self, host: str, port: int, sock=None):
        pid = f"{host}:{port}"
        with self._plock:
            self._peers[pid] = {
                'host':      host,
                'port':      port,
                'sock':      sock or self._udp_sock,
                'last_seen': time.monotonic(),
            }

    def _touch_peer(self, pid: str):
        with self._plock:
            if pid in self._peers:
                self._peers[pid]['last_seen'] = time.monotonic()

    def peers(self) -> list:
        """
        :returns: List of active peer id strings.
        :rtype: list
        """
        with self._plock:
            return list(self._peers.keys())

    # ── MCP dispatch ──────────────────────────────────────────────────────

    def _dispatch(self, msg: dict) -> dict:
        """Route incoming MCP message to monad or local handler."""
        mtype = msg.get('type', '')
        if self._monad is None:
            return {'error': 'no_monad'}
        payload = msg.get('payload', {})
        if mtype == 'query':
            score = self._monad.query(payload.get('word', ''))
            return {'type': 'score', 'score': score}
        if mtype == 'emit':
            word = self._monad.emit()
            return {'type': 'word', 'word': word}
        if mtype == 'learn':
            self._monad.ingest(payload.get('text', ''))
            return {'type': 'ok'}
        if mtype == 'ping':
            return {'type': 'pong',
                    'vocab': self._monad.vocab_size()}
        if mtype == 'fetch':
            return {'error': 'fetch_not_implemented'}
        return {'error': f"unknown_type:{mtype}"}

    def stop(self):
        """Shut down network threads and sockets."""
        self._stop.set()
        if self._udp_sock:
            try:
                self._udp_sock.close()
            except Exception:
                pass


# ══════════════════════════════════════════════════════════════════════════════

class PtolRendezvous:
    """
    Minimal UDP rendezvous server.
    Echoes each client's external IP:port back to them.
    Run on any public VPS. 20 lines of logic.

    :param port: Listening port (default 7299).
    """

    def __init__(self, port: int = 7299):
        self._port = port

    def serve_forever(self):
        """Block and serve rendezvous requests."""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('', self._port))
        print(f"PtolRendezvous listening on :{self._port}")
        while True:
            try:
                data, addr = s.recvfrom(256)
                if data.startswith(b'PTOL_DISCOVER'):
                    reply = f"{addr[0]}:{addr[1]}".encode()
                    s.sendto(reply, addr)
            except Exception:
                continue
