#!/usr/bin/env python3
"""
monad_combine.py -- the three language-center stores as ONE file, held
open in memory, plus the MIND'S EYE (rehearsal that is not feedback).

  1. combine()/read()/write() -- c_monad_wordnet.bin (C binary, 154k
     BoxKiteEntry) + monad_phonetic.bin (PHON, 123k) + monad_english.bin
     (pickle, 164k words + co-occurrence A-matrix) merged into one pickle,
     ~1 GB resident, one read().

  2. THE EARS vs THE MIND'S EYE
     - the EARS are real recursion: speak -> hear() -> deepen() -> speak.
       Uncapped, that stack-overflows. monad_english_io.ECHO_CAP (=5)
       bounds it: content that has looped back 5x stops being heard.
     - the MIND'S EYE is a flat held loop: rehearse a fixed phrase to set
       an alarm / hold a shopping list. It does NOT output, does NOT
       hear(), does NOT deepen() -- so it is not feedback and cannot
       overflow. "just repetition unphased by noise": deterministic, no
       RNG, no A-matrix mutation. Work is exchanged for a result
       (salience on a held intention), not for a change to the model.
"""
from __future__ import annotations

import os
import pickle
import struct
import tempfile
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import monad_english_io as _meio
from monad_english_io import MonadEnglish, hear, ECHO_CAP  # re-export

_HERE = os.path.dirname(os.path.abspath(__file__))
_PTOLC = os.path.join(_HERE, 'PtolC')
DEFAULT_WORDNET = os.path.join(_PTOLC, 'c_monad_wordnet.bin')
DEFAULT_PHONETIC = os.path.join(_PTOLC, 'monad_phonetic.bin')
DEFAULT_COMBINED = os.path.join(_PTOLC, 'monad3.bin')

_REL = None
_BK_STRUCT = struct.Struct('<32sB3xI19hf')   # BoxKiteEntry, 82 bytes


def _relation_names():
    global _REL
    if _REL is None:
        from wordnet_boxkite import RELATION_METHODS
        _REL = list(RELATION_METHODS)
    return _REL


def read_boxkite_c(path: str = DEFAULT_WORDNET) -> Dict[str, dict]:
    """c_monad_wordnet.bin: BXKT header + N * BoxKiteEntry. Returns
    {word: {'pos', 'offset', 'vec19', 'depth_weight'}}."""
    with open(path, 'rb') as f:
        magic, version, n, esize = struct.unpack('<4sIII', f.read(16))
        assert magic == b'BXKT', magic
        assert esize == _BK_STRUCT.size, (esize, _BK_STRUCT.size)
        out: Dict[str, dict] = {}
        blob = f.read(n * esize)
    for i in range(n):
        word_b, pos, offset, *rest = _BK_STRUCT.unpack_from(blob, i * esize)
        vec = list(rest[:19])
        dw = rest[19]
        word = word_b.split(b'\x00', 1)[0].decode('utf-8', 'replace')
        if word:
            out[word] = {'pos': pos, 'offset': offset,
                         'vec19': vec, 'depth_weight': dw}
    return out


def read_phonetic(path: str = DEFAULT_PHONETIC) -> Dict[str, list]:
    with open(path, 'rb') as f:
        assert f.read(4) == b'PHON'
        struct.unpack('<I', f.read(4))
        (nw,) = struct.unpack('<I', f.read(4))
        out = {}
        for _ in range(nw):
            (wl,) = struct.unpack('<B', f.read(1))
            w = f.read(wl).decode('utf-8')
            (npr,) = struct.unpack('<B', f.read(1))
            prons = []
            for _ in range(npr):
                (nph,) = struct.unpack('<B', f.read(1))
                ph = []
                for _ in range(nph):
                    (pl,) = struct.unpack('<B', f.read(1))
                    ph.append(f.read(pl).decode('ascii'))
                prons.append(ph)
            out[w] = prons
    return out


# --------------------------------------------------------------------------
# mind's eye
# --------------------------------------------------------------------------
@dataclass
class Intention:
    phrase: str
    purpose: str                       # 'alarm', 'shopping', 'reminder', ...
    trigger: Optional[str] = None      # a context cue that fires it
    salience: float = 0.0
    rehearsals: int = 0
    created: float = field(default_factory=time.time)


def rehearse(intention: Intention, times: int = 1,
             work_per_rep: float = 0.1) -> Intention:
    """Rethink a fixed phrase `times` times. A FLAT LOOP -- no self-call,
    no output, no hear(), no deepen(), no RNG. Cannot stack-overflow and
    is not feedback; it only raises salience on the held intention (work
    exchanged for a result). Deterministic: rehearse(i, n) is a pure
    function of (i, n)."""
    for _ in range(max(0, int(times))):
        intention.salience += work_per_rep
        intention.rehearsals += 1
    return intention


# --------------------------------------------------------------------------
# the combined store
# --------------------------------------------------------------------------
@dataclass
class CombinedMonad:
    english: MonadEnglish
    wordnet: Dict[str, dict]
    phonetic: Dict[str, list]
    intentions: List[Intention] = field(default_factory=list)
    path: Optional[str] = None
    _intentions_dirty: bool = False

    # ---- lifecycle: the SEDENION WINDOW owns these ----
    # The window loads the combined store once (read()), mutates it live
    # via hear()/hold()/rehearse_all() as the user interacts, and is the
    # sole caller of checkpoint()/close(). Nothing else writes
    # monad_combined.bin.
    @property
    def dirty(self) -> bool:
        return self.english.dirty or self._intentions_dirty

    def checkpoint(self, also_c: bool = False) -> Optional[str]:
        """Persist iff mutated. Called on the window's interval and on
        exit. Returns the path written, or None if clean."""
        if not self.dirty:
            return None
        p = write(self)
        if also_c:
            write_c(self)
        self.english.dirty = False
        self.english._touched = set()
        self._intentions_dirty = False
        return p

    def dirty_chunks(self, cap: int = 16):
        """The dirty delta as sedenion-shaped frames: up to `cap` (=16)
        word nodes, node[0] = e0 (the anchor -- highest co-occurrence
        degree, owns no edge in the frame), the rest linked by a 15-edge
        SPANNING TREE over their induced co-occurrence subgraph. The
        window persists these frames instead of re-serialising the whole
        store -- each frame IS a sedenion and the engine's sedenion ops
        apply to it directly."""
        eng = self.english
        stop = _meio.STOPWORDS
        touched = sorted((i for i in (eng._touched or ())
                          if eng.words[i] not in stop and len(eng.words[i]) >= 3),
                         key=lambda i: -len(eng.A[i]))
        frames = []
        for s in range(0, len(touched), cap):
            nodes = touched[s:s + cap]
            nset = set(nodes)
            e0 = nodes[0]                      # anchor: max-degree, no edge
            # 15-edge spanning tree by greedy max-weight from e0 outward
            tree, seen = [], {e0}
            frontier = list(nodes[1:])
            while frontier and len(tree) < cap - 1:
                best = None
                for a in seen:
                    for b in frontier:
                        w = eng.A[a].get(b, 0.0) or eng.A[b].get(a, 0.0)
                        if best is None or w > best[2]:
                            best = (a, b, w)
                if best is None:
                    break
                a, b, w = best
                tree.append((eng.words[a], eng.words[b], w))
                seen.add(b); frontier.remove(b)
            frames.append({'e0': eng.words[e0],
                           'nodes': [eng.words[i] for i in nodes],
                           'edges': tree})
        return frames

    # unified lookup
    def lookup(self, word: str) -> dict:
        w = word.lower().strip()
        rel = _relation_names()
        wn = self.wordnet.get(w)
        return {
            'word': w,
            'english_idx': self.english.idx(w),
            'cooccur': self.english.neighbors(w, k=10),
            'wordnet': ({**wn, 'relations':
                         {rel[i]: c for i, c in enumerate(wn['vec19']) if c}}
                        if wn else None),
            'phonetic': self.phonetic.get(w),
        }

    # the ears (capped recursion) -- delegate to monad_english_io.hear
    def hear(self, text: str, echo: int = 0):
        return hear(self.english, text, echo=echo)

    # the mind's eye (flat loop)
    def hold(self, phrase: str, purpose: str, trigger: str = None) -> Intention:
        it = Intention(phrase=phrase, purpose=purpose, trigger=trigger)
        self.intentions.append(it)
        return it

    def rehearse_all(self, times: int = 1):
        for it in self.intentions:
            rehearse(it, times)

    def to_dict(self) -> dict:
        return {
            'magic': 'MONAD3', 'version': 1,
            'english': self.english.to_dict(),
            'wordnet': self.wordnet,
            'phonetic': self.phonetic,
            'intentions': [it.__dict__ for it in self.intentions],
        }


def combine(out_path: str = DEFAULT_COMBINED,
            english: str = None, wordnet: str = DEFAULT_WORDNET,
            phonetic: str = DEFAULT_PHONETIC) -> str:
    """Read the three source stores, write one file."""
    eng = _meio.read(english, use_cache=False)
    cm = CombinedMonad(english=eng, wordnet=read_boxkite_c(wordnet),
                       phonetic=read_phonetic(phonetic), path=out_path)
    write(cm, out_path)
    return out_path


def read(path: str = DEFAULT_COMBINED) -> CombinedMonad:
    """Load the one combined file. Falls back to reading the three source
    stores in place if the combined file does not exist yet."""
    if not os.path.exists(path):
        eng = _meio.read(use_cache=False)
        return CombinedMonad(english=eng, wordnet=read_boxkite_c(),
                             phonetic=read_phonetic(), path=path)
    with open(path, 'rb') as f:
        d = pickle.load(f)
    assert d.get('magic') == 'MONAD3', d.get('magic')
    e = d['english']
    known = {'version', 'n', 'vocab', 'words', 'beta', 'E', 'A', 'age',
             'fire_count', 'stratum', 'psi_prev', 'word_count',
             'correction_mask'}
    eng = MonadEnglish(
        version=e.get('version', 'unknown'), vocab=e['vocab'], words=e['words'],
        beta=e['beta'], E=e['E'], A=e['A'], age=e['age'],
        fire_count=e.get('fire_count', [0] * len(e['words'])),
        stratum=e.get('stratum', [0] * len(e['words'])),
        psi_prev=e.get('psi_prev', [0.0] * 16),
        word_count=e.get('word_count', 0),
        correction_mask=e.get('correction_mask', {}),
        _extra={k: v for k, v in e.items() if k not in known},
    )
    cm = CombinedMonad(english=eng, wordnet=d['wordnet'],
                       phonetic=d['phonetic'], path=path)
    cm.intentions = [Intention(**it) for it in d.get('intentions', [])]
    return cm


MONAD3C_H = """\
/* monad3c.h -- the three language centers as ONE mmap-able file.
 * Low hardware bandwidth: mmap() it, cast, read structs in place.
 * No parse, no copy, no alloc on load. One bsearch on the word table
 * gives indices into all three stores at once.
 *
 *   [ Header ][ word blob ][ WordRec[n_words] ]
 *   [ eng: beta f64[nE] E f64[nE] age i32[nE] fire i32[nE] strat i32[nE] ]
 *   [ eng A-matrix CSR: rowptr u32[nE+1]  col u32[nnz]  w f32[nnz] ]
 *   [ wn: BoxKiteEntry[nW]  (82 bytes each, see boxkite_bin.h) ]
 *   [ phon: ix u64[nP+1]  blob (len-prefixed ARPAbet tokens) ]
 *
 * All sections 8-byte aligned; every offset is bytes from file start.
 */
#ifndef MONAD3C_H
#define MONAD3C_H
#include <stdint.h>
#define MONAD3C_MAGIC "MONAD3C\\0"
typedef struct {
    char     magic[8];
    uint32_t version;         /* 1 */
    uint32_t n_words;         /* unified word table rows */
    uint32_t n_eng, n_wn, n_phon, nnz;
    double   psi_prev[16];
    uint64_t off_wordblob, off_wordrec;
    uint64_t off_beta, off_E, off_age, off_fire, off_stratum;
    uint64_t off_rowptr, off_col, off_w;
    uint64_t off_wn, off_phon_ix, off_phon_blob;
} Monad3cHeader;
typedef struct {           /* sorted by name -- bsearch on the blob */
    uint32_t name_off;     /* NUL-terminated UTF-8 in the word blob   */
    int32_t  eng_idx;      /* -1 if absent */
    int32_t  wn_idx;
    int32_t  phon_idx;
} WordRec;
#endif
"""


def _pad8(f):
    while f.tell() % 8:
        f.write(b'\x00')


def write_c(cm: CombinedMonad, path: str = None) -> str:
    """Emit the mmap-able C-native combined file (see MONAD3C_H)."""
    import numpy as np
    path = os.path.abspath(path or (os.path.splitext(cm.path or DEFAULT_COMBINED)[0]
                                    + '_c.bin'))
    eng = cm.english
    n_eng = len(eng.words)

    # unified sorted word table over english U wordnet U phonetic
    eix = {w: i for i, w in enumerate(eng.words)}
    allw = sorted(set(eng.words) | set(cm.wordnet) | set(cm.phonetic))
    wn_keys = sorted(cm.wordnet)
    wn_pos = {w: i for i, w in enumerate(wn_keys)}
    ph_keys = sorted(cm.phonetic)
    ph_pos = {w: i for i, w in enumerate(ph_keys)}

    # CSR of the A-matrix
    rowptr = np.zeros(n_eng + 1, np.uint32)
    for i, nbrs in enumerate(eng.A):
        rowptr[i + 1] = rowptr[i] + len(nbrs)
    nnz = int(rowptr[-1])
    col = np.empty(nnz, np.uint32)
    w = np.empty(nnz, np.float32)
    p = 0
    for nbrs in eng.A:
        for j, ww in nbrs.items():
            col[p] = j; w[p] = ww; p += 1

    hdr = struct.Struct('<8s6I16d13Q')
    hsize = hdr.size + (8 - hdr.size % 8) % 8

    with open(path, 'wb') as f:
        f.seek(hsize)
        _pad8(f)
        off_wordblob = f.tell()
        enc = [wd.encode('utf-8') for wd in allw]
        name_off = np.empty(len(enc), np.uint32)
        acc = 0
        for k, b in enumerate(enc):
            name_off[k] = acc
            acc += len(b) + 1
        f.write(b'\x00'.join(enc) + b'\x00')
        _pad8(f)
        off_wordrec = f.tell()
        wr = np.empty(len(allw), dtype=[('n', '<u4'), ('e', '<i4'),
                                        ('w', '<i4'), ('p', '<i4')])
        wr['n'] = name_off
        wr['e'] = [eix.get(wd, -1) for wd in allw]
        wr['w'] = [wn_pos.get(wd, -1) for wd in allw]
        wr['p'] = [ph_pos.get(wd, -1) for wd in allw]
        f.write(wr.tobytes())
        _pad8(f); off_beta = f.tell();  f.write(np.asarray(eng.beta, np.float64).tobytes())
        _pad8(f); off_E = f.tell();     f.write(np.asarray(eng.E, np.float64).tobytes())
        _pad8(f); off_age = f.tell();   f.write(np.asarray(eng.age, np.int32).tobytes())
        _pad8(f); off_fire = f.tell();  f.write(np.asarray(eng.fire_count, np.int32).tobytes())
        _pad8(f); off_strat = f.tell(); f.write(np.asarray(eng.stratum, np.int32).tobytes())
        _pad8(f); off_rowptr = f.tell(); f.write(rowptr.tobytes())
        _pad8(f); off_col = f.tell();    f.write(col.tobytes())
        _pad8(f); off_w = f.tell();      f.write(w.tobytes())
        _pad8(f); off_wn = f.tell()
        wn_dt = np.dtype([('word', 'S32'), ('pos', 'u1'), ('pad', 'V3'),
                          ('offset', '<u4'), ('vec', '<i2', 19), ('dw', '<f4')])
        assert wn_dt.itemsize == _BK_STRUCT.size, (wn_dt.itemsize, _BK_STRUCT.size)
        wa = np.zeros(len(wn_keys), wn_dt)
        wa['word'] = [k.encode('utf-8')[:31] for k in wn_keys]
        wa['pos'] = [cm.wordnet[k]['pos'] for k in wn_keys]
        wa['offset'] = [cm.wordnet[k]['offset'] for k in wn_keys]
        wa['vec'] = [cm.wordnet[k]['vec19'] for k in wn_keys]
        wa['dw'] = [cm.wordnet[k]['depth_weight'] for k in wn_keys]
        f.write(wa.tobytes())

        _pad8(f); off_phon_ix = f.tell()
        blob = bytearray()
        ph_offsets = np.empty(len(ph_keys) + 1, np.uint64)
        for idx, k in enumerate(ph_keys):
            ph_offsets[idx] = len(blob)
            prons = cm.phonetic[k]
            blob.append(len(prons) & 0xFF)
            for pr in prons:
                blob.append(len(pr) & 0xFF)
                for tok in pr:
                    tb = tok.encode('ascii')
                    blob.append(len(tb) & 0xFF)
                    blob.extend(tb)
        ph_offsets[-1] = len(blob)
        f.write(ph_offsets.tobytes())
        _pad8(f); off_phon_blob = f.tell()
        f.write(blob)
        end = f.tell()
        # header
        f.seek(0)
        f.write(hdr.pack(
            b'MONAD3C\x00', 1, len(allw), n_eng, len(wn_keys), len(ph_keys), nnz,
            *[float(x) for x in eng.psi_prev],
            off_wordblob, off_wordrec, off_beta, off_E, off_age, off_fire,
            off_strat, off_rowptr, off_col, off_w, off_wn, off_phon_ix,
            off_phon_blob))
        f.seek(end)

    with open(os.path.join(os.path.dirname(path), 'monad3c.h'), 'w') as hf:
        hf.write(MONAD3C_H)
    return path


def read_c(path: str):
    """mmap the C-native file and return a tiny in-place accessor -- the
    Python mirror of what ptol.c would do: cast the header, bsearch the
    word table, index the sections. No copy."""
    import mmap
    import numpy as np
    f = open(path, 'rb')
    mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    hdr = struct.Struct('<8s6I16d13Q')
    vals = hdr.unpack_from(mm, 0)
    magic, ver, n_words, n_eng, n_wn, n_phon, nnz = vals[:7]
    psi = vals[7:23]
    (o_blob, o_rec, o_beta, o_E, o_age, o_fire, o_strat,
     o_rowptr, o_col, o_w, o_wn, o_phix, o_phblob) = vals[23:]
    assert magic.rstrip(b'\x00') == b'MONAD3C', magic

    rec = struct.Struct('<iiii')
    blob = mm

    def _name(off):
        e = blob.find(b'\x00', o_blob + off)
        return blob[o_blob + off:e].decode('utf-8', 'replace')

    def lookup(word):
        w = word.lower().strip()
        lo, hi = 0, n_words
        while lo < hi:
            mid = (lo + hi) // 2
            noff, ei, wi, pi = rec.unpack_from(blob, o_rec + mid * 16)
            nm = _name(noff)
            if nm < w:
                lo = mid + 1
            elif nm > w:
                hi = mid
            else:
                out = {'word': w, 'eng_idx': ei if ei >= 0 else None,
                       'wn_idx': wi if wi >= 0 else None,
                       'phon_idx': pi if pi >= 0 else None}
                if ei >= 0:
                    beta = struct.unpack_from('<d', blob, o_beta + ei * 8)[0]
                    rp0 = struct.unpack_from('<I', blob, o_rowptr + ei * 4)[0]
                    rp1 = struct.unpack_from('<I', blob, o_rowptr + (ei + 1) * 4)[0]
                    out['beta'] = beta
                    out['degree'] = rp1 - rp0
                if wi >= 0:
                    e = _BK_STRUCT.unpack_from(blob, o_wn + wi * _BK_STRUCT.size)
                    out['wn_pos'] = e[1]           # word, pos, offset, v0..v18, dw
                    out['wn_offset'] = e[2]
                    out['wn_vec19'] = list(e[3:22])
                if pi >= 0:
                    p0 = struct.unpack_from('<Q', blob, o_phix + pi * 8)[0]
                    npr = struct.unpack_from('<B', blob, o_phblob + p0)[0]
                    out['n_prons'] = npr
                return out
        return None

    return {'header': {'version': ver, 'n_words': n_words, 'n_eng': n_eng,
                       'n_wn': n_wn, 'n_phon': n_phon, 'nnz': nnz},
            'psi_prev': list(psi), 'lookup': lookup, '_mm': mm, '_f': f}


def write(cm: CombinedMonad, path: str = None) -> str:
    path = os.path.abspath(path or cm.path or DEFAULT_COMBINED)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if os.path.exists(path):
        os.replace(path, path + '.bak')
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix='.tmp')
    try:
        with os.fdopen(fd, 'wb') as f:
            pickle.dump(cm.to_dict(), f, protocol=4)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    cm.path = path
    return path


# ==========================================================================
if __name__ == '__main__':
    t = time.time()
    print("combine() the three stores ->", DEFAULT_COMBINED)
    combine()
    print(f"  built in {time.time()-t:.1f}s  "
          f"({os.path.getsize(DEFAULT_COMBINED)/1e6:.1f} MB)")

    t = time.time()
    cm = read()
    import resource
    print(f"read() in {time.time()-t:.1f}s   RSS "
          f"{resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024} MB")
    print(f"  english {len(cm.english.words):,} words / "
          f"{sum(len(a) for a in cm.english.A):,} edges | "
          f"wordnet {len(cm.wordnet):,} | phonetic {len(cm.phonetic):,}")

    for w in ('bank', 'physics', 'thaumaturge'):
        lu = cm.lookup(w)
        print(f"\n  lookup({w!r}):")
        print(f"    cooccur : {[x for x, _ in lu['cooccur'][:6]]}")
        print(f"    wordnet : {lu['wordnet']['relations'] if lu['wordnet'] else None}")
        print(f"    phonetic: {lu['phonetic'][0] if lu['phonetic'] else None}")

    print("\n  MIND'S EYE -- rehearse, no feedback, no overflow:")
    a_before = dict(cm.english.A[cm.english.idx('milk')]) if cm.english.idx('milk') else {}
    it = cm.hold("milk, eggs, bread", purpose='shopping', trigger='at the store')
    for n in (1, 10, 100, 5000):
        rehearse(it, n)
        print(f"    rehearsals={it.rehearsals:5d}  salience={it.salience:7.1f}")
    a_after = dict(cm.english.A[cm.english.idx('milk')]) if cm.english.idx('milk') else {}
    print(f"    A-matrix for 'milk' unchanged by rehearsal: {a_before == a_after}")
    print(f"    (contrast: hear() at echo>={ECHO_CAP} is the cap that stops the ears)")
