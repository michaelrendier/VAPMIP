"""
skills/config.py — Configuration layer for Ptolemy.

:description:
    Merges ptolemy.cfg (user, static, ! pins hard-lock keys) with
    .ptolrc (Ptolemy's live self-tuning state). Pinned keys in cfg
    cannot be overridden by .ptolrc. Ptolemy writes .ptolrc only.

:classes:
    PtolConfig
"""

import os
import threading
import configparser
from pathlib import Path

_PTOLEMY_DIR = Path(os.path.expanduser('~/.ptolemy'))
_CFG_PATH    = _PTOLEMY_DIR / 'ptolemy.cfg'
_PTOLRC_PATH = _PTOLEMY_DIR / '.ptolrc'

_DEFAULTS = {
    # ── Paths ────────────────────────────────────────────────────────────
    'checkpoint':         str(_PTOLEMY_DIR / 'monad_wordnet.bin'),
    'active_state':       str(_PTOLEMY_DIR / 'monad.bin'),
    'socket':             str(_PTOLEMY_DIR / 'ptolemy.sock'),
    'temp_dir':           str(_PTOLEMY_DIR / '.ptoltemp'),
    'cache_dir':          str(_PTOLEMY_DIR / 'cache'),
    'log_dir':            str(_PTOLEMY_DIR / 'logs'),
    # ── Network ──────────────────────────────────────────────────────────
    'tcp_port':           '7297',
    'udp_port':           '7298',
    # ── Crawler / acquisition ────────────────────────────────────────────
    'crawl_delay':        '1.5',
    'scholar_email':      'ptolemy@localhost',
    # ── System resource limits ───────────────────────────────────────────
    'max_cpu_percent':    '25',
    'max_ram_mb':         '512',
    'monitor_interval':   '30',
    'throttle_sleep':     '0.5',
    # ── Ingestion thresholds (BAO-adaptive — Ptolemy writes these) ───────
    'redundancy_min':     '0.15',
    'redundancy_max':     '0.85',
    'novelty_min':        '0.05',
    'noise_max':          '0.45',
    'chunk_min_words':    '8',
    # ── Session ──────────────────────────────────────────────────────────
    'field_save_interval':'300',
    'log_max_bytes':      str(10 * 1024 * 1024),
    # ── Sedenion operator target weights (Ptolemy self-tunes) ────────────
    # e_k = target activation weight for sedenion dimension k
    # Ptolemy writes actual UNS to [hamiltonian], targets here in [sedenion]
    'e0_identity':        '1.0000',   # identity / ground state
    'e1_negate':          '0.0000',   # negation / complement
    'e2_bind':            '0.5000',   # binding / association
    'e3_name':            '0.7500',   # naming / reference
    'e4_apply':           '0.6000',   # application / function call
    'e5_abstract':        '0.4500',   # abstraction / generalisation
    'e6_branch':          '0.3000',   # branching / conditional
    'e7_iterate':         '0.5500',   # iteration / sequence
    'e8_recurse':         '0.2500',   # recursion / self-reference
    'e9_allocate':        '0.4000',   # allocation / memory
    'e10_query':          '0.6500',   # query / lookup
    'e11_dereference':    '0.7000',   # dereference / anaphor
    'e12_compose':        '0.5000',   # composition / chaining
    'e13_parallelize':    '0.3500',   # parallelize / three-face
    'e14_interrupt':      '0.1000',   # interrupt / affect
    'e15_emit':           '0.8000',   # emission / output
    # ── BAO field state (Ptolemy writes these) ───────────────────────────
    'field_health':       '1.0',
    'bao_mean':           '0.56714',
    'bao_direction':      '0.0',
    'bao_adapt_count':    '0',
    # ── Sources (phase 1=on by default, phases 2-4 off until stable) ─────
    'wiktionary':         'on',
    'gutenberg':          'on',
    'archive_org':        'on',
    'sep':                'on',
    'ocw_intro':          'on',
    'ocw_upper':          'off',
    'arxiv':              'off',
    'pubmed':             'off',
    'semantic_sch':       'off',
    'patents_us':         'off',
    'caselaw':            'off',
    'foundation':         'off',
    # ── Drawing / reporting ──────────────────────────────────────────────
    'auto_bao_plot':      'off',     # write BAO ring PNG on each adapt
    'report_interval':    '3600',    # seconds between auto Hamiltonian Reports
}


class PtolConfig:
    """
    Thread-safe configuration merge.

    :param cfg_path: Path to ptolemy.cfg (user editable).
    :param ptolrc_path: Path to .ptolrc (Ptolemy writes here).
    """

    def __init__(self,
                 cfg_path: str = str(_CFG_PATH),
                 ptolrc_path: str = str(_PTOLRC_PATH)):
        self._cfg_path    = Path(cfg_path)
        self._ptolrc_path = Path(ptolrc_path)
        self._lock        = threading.RLock()
        self._effective   = {}
        self._pinned      = set()
        self._load()

    def _parse_cfg(self):
        """
        Parse ptolemy.cfg. Lines starting with '!' are pinned.

        :returns: (defaults dict, pinned dict)
        :rtype: tuple
        """
        defaults = dict(_DEFAULTS)
        pinned   = {}
        if not self._cfg_path.exists():
            self._cfg_path.parent.mkdir(parents=True, exist_ok=True)
            self._write_default_cfg()
        with open(self._cfg_path, encoding='utf-8') as fh:
            for raw in fh:
                line = raw.strip()
                if not line or line.startswith('#'):
                    continue
                is_pin = line.startswith('!')
                if is_pin:
                    line = line[1:].strip()
                if '=' not in line:
                    continue
                key, _, val = line.partition('=')
                key = key.strip().lower()
                val = val.strip()
                if is_pin:
                    pinned[key]   = val
                else:
                    defaults[key] = val
        return defaults, pinned

    def _parse_ptolrc(self):
        """
        Parse .ptolrc (INI sections flattened to key=value).

        :returns: flat dict of all .ptolrc values
        :rtype: dict
        """
        rc = {}
        if not self._ptolrc_path.exists():
            return rc
        cp = configparser.ConfigParser()
        cp.read(self._ptolrc_path)
        for section in cp.sections():
            for key, val in cp.items(section):
                rc[key] = val
        return rc

    def _load(self):
        defaults, pinned = self._parse_cfg()
        rc = self._parse_ptolrc()
        merged = dict(defaults)
        for key, val in rc.items():
            if key not in pinned:
                merged[key] = val
        merged.update(pinned)
        with self._lock:
            self._effective = merged
            self._pinned    = set(pinned.keys())

    def reload(self):
        """Re-read both files. Thread-safe."""
        self._load()

    def get(self, key: str, default=None):
        """
        Get effective config value.

        :param key: Config key (case-insensitive).
        :param default: Fallback if key absent.
        :returns: String value or default.
        """
        with self._lock:
            return self._effective.get(key.lower(), default)

    def getfloat(self, key: str, default: float = 0.0) -> float:
        """
        :param key: Config key.
        :param default: Float fallback.
        :returns: Float value.
        :rtype: float
        """
        try:
            return float(self.get(key, default))
        except (TypeError, ValueError):
            return default

    def getint(self, key: str, default: int = 0) -> int:
        """
        :param key: Config key.
        :param default: Int fallback.
        :returns: Int value.
        :rtype: int
        """
        try:
            return int(self.get(key, default))
        except (TypeError, ValueError):
            return default

    def set_ptolrc(self, section: str, key: str, value):
        """
        Ptolemy writes a value to .ptolrc. Pinned keys are silently ignored.

        :param section: INI section name.
        :param key: Key within section.
        :param value: Value to write.
        """
        key = key.lower()
        with self._lock:
            if key in self._pinned:
                return
            cp = configparser.ConfigParser()
            if self._ptolrc_path.exists():
                cp.read(self._ptolrc_path)
            if section not in cp:
                cp[section] = {}
            cp[section][key] = str(value)
            self._ptolrc_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._ptolrc_path, 'w', encoding='utf-8') as fh:
                cp.write(fh)
            self._effective[key] = str(value)

    def write_full_ptolrc(self, engine=None):
        """
        Write ALL settings to .ptolrc as their defaults.
        Called once on first teach startup. Gives Ptolemy full visibility
        of every tunable parameter. Pinned keys in ptolemy.cfg are skipped.

        :param engine: Optional Engine instance for live sedenion state.
        """
        sections = {
            'engine': {
                'window_size':      '16',
                'version':          '1.218',
                'started':          __import__('time').strftime('%Y-%m-%dT%H:%M:%S'),
            },
            'sedenion': {
                f'e{k}_{["identity","negate","bind","name","apply","abstract","branch","iterate","recurse","allocate","query","dereference","compose","parallelize","interrupt","emit"][k]}':
                    f"{_DEFAULTS.get(f'e{k}_'+["identity","negate","bind","name","apply","abstract","branch","iterate","recurse","allocate","query","dereference","compose","parallelize","interrupt","emit"][k], '0.0000')}"
                for k in range(16)
            },
            'thresholds': {
                'redundancy_min':  _DEFAULTS['redundancy_min'],
                'redundancy_max':  _DEFAULTS['redundancy_max'],
                'novelty_min':     _DEFAULTS['novelty_min'],
                'noise_max':       _DEFAULTS['noise_max'],
                'chunk_min_words': _DEFAULTS['chunk_min_words'],
            },
            'bao': {
                'field_health':    _DEFAULTS['field_health'],
                'bao_mean':        _DEFAULTS['bao_mean'],
                'bao_direction':   _DEFAULTS['bao_direction'],
                'bao_adapt_count': _DEFAULTS['bao_adapt_count'],
                'last_adapt':      __import__('time').strftime('%Y-%m-%dT%H:%M:%S'),
            },
            'monitor': {
                'cpu_max_pct':     _DEFAULTS['max_cpu_percent'],
                'ram_max_mb':      _DEFAULTS['max_ram_mb'],
                'monitor_interval':_DEFAULTS['monitor_interval'],
                'teach_wpm':       '0',
                'queue_depth':     '0',
            },
            'sources': {
                k: _DEFAULTS.get(k, 'off')
                for k in ['wiktionary','gutenberg','archive_org','sep',
                          'ocw_intro','ocw_upper','arxiv','pubmed',
                          'semantic_sch','patents_us','caselaw','foundation']
            },
            'hamiltonian': {
                'report_time':     __import__('time').strftime('%Y-%m-%dT%H:%M:%S'),
                'field_health':    _DEFAULTS['field_health'],
                'bao_mean':        _DEFAULTS['bao_mean'],
                'j_pos':           '1.0',
                'j_neg':           '0.0',
                'sigma_crit_dist': '0.5',
                'vocab_size':      '0',
                'dtcs':            'none',
            },
            'network': {
                'tcp_port': _DEFAULTS['tcp_port'],
                'udp_port': _DEFAULTS['udp_port'],
            },
            'acquisition': {
                'crawl_delay':       _DEFAULTS['crawl_delay'],
                'scholar_email':     _DEFAULTS['scholar_email'],
                'field_save_interval': _DEFAULTS['field_save_interval'],
                'auto_bao_plot':     _DEFAULTS['auto_bao_plot'],
                'report_interval':   _DEFAULTS['report_interval'],
            },
        }
        for section, kvs in sections.items():
            for key, val in kvs.items():
                self.set_ptolrc(section, key, val)

    def _write_default_cfg(self):
        """Write a starter ptolemy.cfg if none exists."""
        lines = [
            '# ptolemy.cfg — user configuration',
            '# Lines starting with ! are pinned — Ptolemy cannot override them.',
            '# Ptolemy reads this file but writes ONLY to .ptolrc.',
            '#',
            '# Pin any line with ! to prevent Ptolemy from changing it:',
            '#   !tcp_port = 7297',
            '#',
            f"checkpoint   = {_DEFAULTS['checkpoint']}",
            f"active_state = {_DEFAULTS['active_state']}",
            f"socket       = {_DEFAULTS['socket']}",
            f"tcp_port     = {_DEFAULTS['tcp_port']}",
            f"udp_port     = {_DEFAULTS['udp_port']}",
            '',
        ]
        with open(self._cfg_path, 'w', encoding='utf-8') as fh:
            fh.write('\n'.join(lines) + '\n')
