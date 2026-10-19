#!/usr/bin/env python3
"""monad_pyu.py — line-for-line Python port of the Unicode build (src/PtolC_unicode, STATE_VERSION 5).

It loads a private copy of monad_py.py (the port of the 2026-05 build) and replaces only what the Unicode build changed:
word_coords, tok_split, token_accept, the sentence splitter in learn_ex, and surface_canonical.  Everything else (zeros, the A table,
speak, near_canonical, the separators) is the same code as in the 2026-05 port, so a difference between the two ports is a difference
between the two C builds.  Character classes come from Python's unicodedata, the same source the C tables were generated from."""
import importlib.util, math, os, unicodedata as ud
from functools import lru_cache
HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("monad_pyu_base", os.path.join(HERE, "monad_py.py"))
mp = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(mp)

P61 = (1 << 61) - 1
PHI64 = 0x9E3779B97F4A7C15
HAN = [(0x3400, 0x4DBF), (0x4E00, 0x9FFF), (0xF900, 0xFAFF), (0x20000, 0x2A6DF), (0x2A700, 0x2EBEF), (0x30000, 0x323AF)]
SENT_END = {ord(c) for c in ".!?\n"} | {0x2026, 0x203C, 0x2047, 0x2048, 0x2049, 0x3002, 0xFF01, 0xFF1F, 0xFF0E}


@lru_cache(maxsize=None)
def u_is_word(cp): return not (0xD800 <= cp <= 0xDFFF) and ud.category(chr(cp))[0] in "LM"
def u_is_han(cp): return any(a <= cp <= b for a, b in HAN)
@lru_cache(maxsize=None)
def u_is_latin(cp): return not (0xD800 <= cp <= 0xDFFF) and ud.category(chr(cp))[0] == "L" and ud.name(chr(cp), "").startswith("LATIN")
@lru_cache(maxsize=None)
def u_is_vowel(cp):
    c = chr(cp)
    return u_is_latin(cp) and ud.category(c) == "Ll" and (ud.normalize("NFD", c)[0] in "aeiouy" or c in "æœø")
@lru_cache(maxsize=None)
def u_lower(cp):
    if 0xD800 <= cp <= 0xDFFF: return cp
    l = chr(cp).lower(); return ord(l) if len(l) == 1 else cp


def word_coords(surface, N=mp.N_DEFAULT):
    """Horner over code points mod 2^61-1, then the golden-ratio multiplicative hash in exact integers (see monad.c)."""
    v = 0
    for ch in surface:
        v = (v * 0x110001 + (ord(ch) + 1)) % P61
    seed64 = (v * PHI64) & mp.M64
    idx = (seed64 * N) >> 64
    idx = N - 1 if idx >= N else idx
    seed = float(seed64 >> 11) / 9007199254740992.0
    return idx, mp.D_STAR + seed * (mp.OMEGA_ZS - mp.D_STAR)


def tok_split(text):
    out, buf = [], []
    def flush():
        if len(buf) >= 2 and buf[0] != "'": out.append("".join(buf))
        buf.clear()
    for ch in text:
        cp = ord(ch)
        wc = u_is_word(cp) or cp == 0x27 or cp == 0x2019
        if wc and u_is_han(cp):
            flush(); out.append(ch)
        elif wc:
            if cp == 0x2019: cp = 0x27
            buf.append(chr(u_lower(cp)))
        else:
            flush()
    flush()
    return out


def _latin_vowels(s):
    letters = vc = 0
    for ch in s:
        if ch == "'": continue
        if not u_is_latin(ord(ch)): return None
        letters += 1; vc += u_is_vowel(u_lower(ord(ch)))
    return vc if letters else None


def token_accept(tok, ft=mp.NS_FT_PROSE):
    mx, hexok, slash, hidig, caps, b64, needv = mp._RULES.get(ft, mp._RULES[mp.NS_FT_PROSE])
    n = len(tok)
    if n < 1 or (n < 2 and not u_is_han(ord(tok[0]))) or n > mx or (tok.isdigit() and tok.isascii()) or mp._is_uuid(tok) or "=" in tok or "://" in tok:
        return False
    if not hexok and mp._is_hex_string(tok): return False
    if not slash and ("/" in tok or "\\" in tok): return False
    if not hidig and sum(c.isdigit() for c in tok) * 100 // n > 50: return False   # AS-IS (C counts ASCII digits; identical for ASCII digits)
    if not caps and len(tok.encode()) > 6 and all(c == "_" or ("A" <= c <= "Z") or c.isdigit() for c in tok): return False
    if b64 > 0 and mp._is_base64_chunk(tok, b64): return False
    if needv:
        vc = _latin_vowels(tok)
        if vc is not None and (vc == 0 or (n >= 6 and vc * 100 // n < 15)): return False
    if tok[-1] == "'": return False
    return True


mp.word_coords, mp.tok_split, mp.token_accept = word_coords, tok_split, token_accept


class MonadU(mp.Monad):
    @staticmethod
    def surface_canonical(w):
        n = len(w); vowels = digits = uppers = specials = latin = han = 0
        for ch in w:
            c = ord(ch)
            if 48 <= c <= 57: digits += 1
            if u_lower(c) != c: uppers += 1
            if u_is_vowel(u_lower(c)): vowels += 1
            if u_is_latin(c): latin += 1
            if u_is_han(c): han += 1
            if c in (95, 45, 39): specials += 1
        if n < (1 if han else 3) or n > 15 or digits or uppers > 1 or specials > 1: return False
        if latin == n:
            if n >= 5 and vowels * 100 // n < 20: return False
            if n < 5 and vowels == 0: return False
        return True

    def learn_ex(self, text, ft=mp.NS_FT_PROSE):
        if text.startswith("-----BEGIN "): return
        sent, cur = [], []
        for ch in text:
            if ord(ch) in SENT_END: sent.append("".join(cur)); cur = []
            else: cur.append(ch)
        if cur: sent.append("".join(cur))
        for s in sent:
            if len(s.encode("utf-8")) < 2: continue
            toks = tok_split(s)
            if not toks: continue
            sidx, sE = [], []
            for w in toks:
                if not token_accept(w, ft): self.rejected += 1; continue
                idx, E, _ = self.wm_get(w); self.wm[w] = idx
                amp = abs(math.sin(self.zeros[idx])) * (math.pi * 0.5)
                nb = self.beta[idx] + E * E * mp.ALPHA_LEARN * amp
                self.beta[idx] = mp.BETA_SAT if nb > mp.BETA_SAT else nb
                v = self.vocab.get(idx)
                if v is None or E > v["E"]: v = self.vocab[idx] = dict(word=w[:mp.MAX_WORD_LEN - 1], E=E, hs=1, gs=1, ps=0)
                if ft == mp.NS_FT_WORDNET: v["ps"] = 2
                elif ft in (mp.NS_FT_PROSE, mp.NS_FT_MARKUP, mp.NS_FT_DOC):
                    if v["ps"] == 0: v["ps"] = 1
                    elif v["ps"] == 2: v["ps"] = 3
                sidx.append(idx); sE.append(E); self.word_count += 1
            nact = len(sidx)
            for i in range(nact):
                for j in range(i + 1, min(i + mp.WINDOW_MAX, nact)):
                    if sidx[i] == sidx[j]: continue
                    d_zero = abs(self.zeros[sidx[i]] - self.zeros[sidx[j]]) + mp.GAP
                    couple = 2.0 if self.dirac_pole(self.zeros[sidx[i]]) == self.dirac_pole(self.zeros[sidx[j]]) else 1.0
                    self.a_add(sidx[i], sidx[j], sE[i] * sE[j] * couple / (d_zero * float(j - i)))

Monad = MonadU
