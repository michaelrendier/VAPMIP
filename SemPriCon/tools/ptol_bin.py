#!/usr/bin/env python3
"""ptol_bin.py — read-only reader for the PTOL state file (STATE_VERSION 1..4).

Layout is copied from PtolC/state.c at commit eb28ce8 (state_load), nothing inferred:

    magic[4]="PTOL"  version u32  N u32  vocab_size u32  A_size u32  word_count u32  threshold f64
    v>=4:  affect f32
    beta  f64[N]        age  i32[N]
    vocab × vocab_size: idx u32  wlen u16  E f64  [v>=2: home_stratum u8  gen_stratum u8]  [v>=3: prose_seen u8]  word[wlen]
    A     × A_size:     i u32  j u32  w f64

The file is only ever opened 'rb'.
"""
import struct
import numpy as np


def load(path, with_edges=True):
    with open(path, "rb") as f:
        raw = f.read()
    if raw[:4] != b"PTOL":
        raise ValueError(f"bad magic {raw[:4]!r}")
    ver, N, vc, ac, wc = struct.unpack_from("<5I", raw, 4)
    (thr,) = struct.unpack_from("<d", raw, 24)
    pos = 32
    affect = 0.0
    if ver >= 4:
        (affect,) = struct.unpack_from("<f", raw, pos)
        pos += 4
    beta = np.frombuffer(raw, dtype="<f8", count=N, offset=pos); pos += 8 * N
    age = np.frombuffer(raw, dtype="<i4", count=N, offset=pos); pos += 4 * N
    vocab = []
    for _ in range(vc):
        idx, wlen = struct.unpack_from("<IH", raw, pos); pos += 6
        (E,) = struct.unpack_from("<d", raw, pos); pos += 8
        hs = gs = ps = 0
        if ver >= 2:
            hs, gs = raw[pos], raw[pos + 1]; pos += 2
        if ver >= 3:
            ps = raw[pos]; pos += 1
        word = raw[pos:pos + wlen].decode("utf-8", errors="replace"); pos += wlen
        vocab.append((idx, word, E, hs, gs, ps))
    edges = None
    if with_edges:
        dt = np.dtype([("i", "<u4"), ("j", "<u4"), ("w", "<f8")])
        edges = np.frombuffer(raw, dtype=dt, count=ac, offset=pos)
    end = pos + 16 * ac
    return dict(version=ver, N=N, vocab_size=vc, A_size=ac, word_count=wc, threshold=thr,
                affect=affect, beta=beta, age=age, vocab=vocab, edges=edges,
                bytes_total=len(raw), bytes_consumed=end)


def write_ground(path, N=25000, ground_abs=1.888, threshold=3.776):
    """Write an empty (ground-state) PTOL v4 file: every β at |L_GROUND|/N, no vocab, no edges.  Used only to give the C binary a
    checkpoint path that exists, so that `-c <file> -l <text>` saves back to it instead of the protected monad_wordnet.bin."""
    with open(path, "wb") as f:
        f.write(b"PTOL" + struct.pack("<5I", 4, N, 0, 0, 0) + struct.pack("<d", threshold) + struct.pack("<f", 0.0))
        f.write(np.full(N, ground_abs / N, dtype="<f8").tobytes())
        f.write(np.zeros(N, dtype="<i4").tobytes())
