#!/usr/bin/env python3
"""monad_py.py — line-for-line Python port of the May-2026 C monad (PtolC/monad.c, state.c, tokenizer.c, filter.c at eb28ce8, "v1.215").

PURPOSE: documentation instrument.  Each function here carries the C function's name and is checked against the compiled C binary
(see notebooks/ and tools/verify_against_c.py).  It is not a replacement and it does not improve anything: bugs are ported on purpose and
marked  # AS-IS:  so the white paper can describe the mechanism that actually ran.

Float notes: Python float == C double; math.* call the same libm; (double)uint64 rounds to nearest-even in both.
"""
import math
import numpy as np

# ── ptolemy.h ────────────────────────────────────────────────────────────────
N_DEFAULT, L_GROUND, D_STAR, OMEGA_ZS = 25000, -1.888, 0.24600, 0.56714
PHI = 1.6180339887498948482
ALPHA_LEARN, LAMBDA, TAU = 0.01, 0.05, 5.0
SPREAD_RADIUS, SPREAD_DECAY, GAP = 3, 1.0, 0.000707
WINDOW_MIN, WINDOW_MAX, BETA_SAT, EMIT_THRESH, MAX_WORD_LEN = 7, 12, 7.552, 3.776, 256
NS_FT_PROSE, NS_FT_CODE, NS_FT_MARKUP, NS_FT_DOC, NS_FT_WORDNET = 0, 1, 2, 3, 4
M64 = (1 << 64) - 1

# ── monad.c: generate_zeros ───────────────────────────────────────────────────
_EXACT_ZEROS = [14.134725, 21.022040, 25.010858, 30.424876, 32.935062, 37.586178, 40.918719, 43.327073, 48.005151, 49.773832,
                52.970321, 56.446248, 59.347044, 60.831779, 65.112544, 67.079811, 69.546402, 72.067158, 75.704691, 77.144840]


def generate_zeros(N):
    """First 20 are tabulated; every later z[n] is a Newton solve of the Riemann–von Mangoldt count N(t)=n, NOT a tabulated zero."""
    z = [0.0] * N
    m = min(N, 20)
    for i in range(m):
        z[i] = _EXACT_ZEROS[i]
    if N <= 20:
        return z
    two_pi = 2.0 * math.pi
    for n in range(21, N + 1):
        t = z[n - 2] + (z[n - 2] - z[n - 3])
        for _ in range(30):
            if t < 2.0:
                t = n * 3.0
            nt = (t / two_pi) * (math.log(t / two_pi) - 1.0) + 0.875
            dnt = math.log(t / two_pi) / two_pi
            if abs(dnt) < 1e-15:
                break
            dt = (nt - n) / dnt
            t -= dt
            if abs(dt) < 1e-4:
                break
        z[n - 1] = t
    return z


# ── monad.c: monad_word_coords ────────────────────────────────────────────────
def word_coords(surface, N=N_DEFAULT):
    """surface -> (idx, E).  base-95 Horner over printable ASCII, fmod(v·φ, 1), idx = floor(seed·N), E = d* + seed·(Ω−d*)."""
    v = 0
    for c in surface.encode("utf-8"):
        ci = (c - 32 + 1) if 32 <= c < 127 else 0       # AS-IS: every non-ASCII byte contributes digit 0
        v = (v * 95 + ci) & M64                         # AS-IS: uint64 wraps; words of ~10+ letters overflow
    if v > 0:
        v -= 1
    seed = math.fmod(float(v) * PHI, 1.0)               # AS-IS: float(v) keeps 53 bits; v up to 2^64
    if seed < 0.0:
        seed += 1.0
    idx = int(seed * N)
    idx = N - 1 if idx >= N else (0 if idx < 0 else idx)
    return idx, D_STAR + seed * (OMEGA_ZS - D_STAR)


# ── tokenizer.c: tok_split ────────────────────────────────────────────────────
def _isalpha_c(c):                                       # C locale: ASCII letters only
    return (65 <= c <= 90) or (97 <= c <= 122)


def tok_split(text):
    out, buf = [], []
    b = text.encode("utf-8") + b"\0"
    for c in b:
        if _isalpha_c(c) or c == 39:
            buf.append(chr(c).lower())
        elif buf:
            tok = "".join(buf)
            if len(tok) >= 2 and tok[0] != "'":
                out.append(tok)
            buf = []
    return out


# ── filter.c: token_accept ────────────────────────────────────────────────────
_RULES = {NS_FT_PROSE: (24, 0, 0, 0, 0, 16, 1), NS_FT_CODE: (40, 0, 0, 1, 1, 0, 0), NS_FT_MARKUP: (24, 0, 0, 0, 0, 16, 1),
          NS_FT_DOC: (24, 0, 0, 0, 0, 16, 1), NS_FT_WORDNET: (24, 0, 0, 0, 0, 16, 1)}
_HEX = set("0123456789abcdefABCDEF")


def _is_hex_string(s):
    if len(s) >= 3 and s[0] == "0" and s[1] in "xX":
        return True
    return len(s) >= 6 and all(c in _HEX for c in s)


def _is_uuid(s):
    if len(s) != 36:
        return False
    for i, c in enumerate(s):
        if i in (8, 13, 18, 23):
            if c != "-":
                return False
        elif c not in _HEX:
            return False
    return True


def _is_base64_chunk(s, mn):
    if len(s) < mn or s[-1] != "=":
        return False
    ok = sum(1 for c in s if c.isascii() and (c.isalnum() or c in "+/="))
    return ok * 100 // len(s) >= 95


def _vowels(s):
    return sum(1 for c in s if (ord(c) | 0x20) in (97, 101, 105, 111, 117))


def token_accept(tok, ft=NS_FT_PROSE):
    mx, hexok, slash, hidig, caps, b64, needv = _RULES.get(ft, _RULES[NS_FT_PROSE])
    n = len(tok)
    if n < 2 or n > mx or tok.isdigit() and tok.isascii() or _is_uuid(tok) or "=" in tok or "://" in tok:
        return False
    if not hexok and _is_hex_string(tok):
        return False
    if not slash and ("/" in tok or "\\" in tok):
        return False
    if not hidig and sum(c.isdigit() for c in tok) * 100 // n > 50:
        return False
    if not caps and n > 6 and all(c == "_" or ("A" <= c <= "Z") or c.isdigit() for c in tok):
        return False
    if b64 > 0 and _is_base64_chunk(tok, b64):
        return False
    if needv:
        vc = _vowels(tok)
        if vc == 0 or (n >= 6 and vc * 100 // n < 15):
            return False
    if tok[-1] == "'":
        return False
    return True


# ── the Monad state (monad.h) ─────────────────────────────────────────────────
class Monad:
    def __init__(self, N=N_DEFAULT):
        self.N = N
        self.ground = abs(L_GROUND) / N
        self.zeros = generate_zeros(N)
        self.beta = [self.ground] * N
        self.age = [0] * N
        self.vocab = {}                  # idx -> dict(word, E, hs, gs, ps)
        self.wm = {}                     # word -> idx
        self.A = {}                      # (i<j) -> w
        self.word_count = 0
        self.affect = 0.0
        self.last_pointer = 0
        self.rejected = 0

    # state.c: state_load
    @classmethod
    def from_bin(cls, path):
        import ptol_bin
        d = ptol_bin.load(path)
        m = cls(d["N"])
        m.word_count, m.affect = d["word_count"], d["affect"]
        m.beta = d["beta"].tolist(); m.age = d["age"].tolist()
        for idx, w, E, hs, gs, ps in d["vocab"]:
            m.vocab[idx] = dict(word=w, E=E, hs=hs, gs=gs, ps=ps)
            m.wm[w] = idx
        e = d["edges"]
        m.Ai, m.Aj, m.Aw = e["i"].astype(np.int64), e["j"].astype(np.int64), e["w"].astype(np.float64)
        m.A = None                         # edges live in the three arrays until a learn() needs the dict
        return m

    def _A_dict(self):
        if self.A is None:
            self.A = {(int(i), int(j)): float(w) for i, j, w in zip(self.Ai, self.Aj, self.Aw)}
        return self.A

    # monad.c: monad_wm_get
    def wm_get(self, word):
        if word in self.wm:
            idx = self.wm[word]
            if idx < self.N and idx in self.vocab:
                return idx, self.vocab[idx]["E"], True
            return idx, word_coords(word, self.N)[1], True
        idx, E = word_coords(word, self.N)
        return idx, E, False

    # monad.c: monad_a_add
    def a_add(self, i, j, delta):
        if i == j:
            return
        if i > j:
            i, j = j, i
        if ((i << 15) | j) == 0:
            return
        A = self._A_dict()
        A[(i, j)] = A.get((i, j), 0.0) + delta

    # monad.c: dirac_pole / dirac_phase
    @staticmethod
    def dirac_pole(g):
        return 1 if math.sin(g * 0.5) * math.cos(g * 0.5) > 0.0 else -1

    # monad.c: monad_learn_ex
    def learn_ex(self, text, ft=NS_FT_PROSE):
        if text.startswith("-----BEGIN "):
            return
        # sentences split at . ! ? \n  (AS-IS: a sentence of < 2 bytes is skipped)
        sent, cur = [], []
        for ch in text:
            if ch in ".!?\n":
                sent.append("".join(cur)); cur = []
            else:
                cur.append(ch)
        if cur:
            sent.append("".join(cur))
        for s in sent:
            if len(s.encode("utf-8")) < 2:
                continue
            toks = tok_split(s)
            if not toks:
                continue
            sidx, sE = [], []
            for w in toks:
                if not token_accept(w, ft):
                    self.rejected += 1
                    continue
                idx, E, _ = self.wm_get(w)
                self.wm[w] = idx
                amp = abs(math.sin(self.zeros[idx])) * (math.pi * 0.5)
                nb = self.beta[idx] + E * E * ALPHA_LEARN * amp
                self.beta[idx] = BETA_SAT if nb > BETA_SAT else nb
                v = self.vocab.get(idx)
                if v is None or E > v["E"]:                       # AS-IS: the slot's displayed word is the highest-E arrival
                    v = self.vocab[idx] = dict(word=w[:MAX_WORD_LEN - 1], E=E, hs=1, gs=1, ps=0)
                if ft == NS_FT_WORDNET:
                    v["ps"] = 2
                elif ft in (NS_FT_PROSE, NS_FT_MARKUP, NS_FT_DOC):
                    if v["ps"] == 0:
                        v["ps"] = 1
                    elif v["ps"] == 2:
                        v["ps"] = 3
                sidx.append(idx); sE.append(E)
                self.word_count += 1
            nact = len(sidx)
            for i in range(nact):
                jmax = min(i + WINDOW_MAX, nact)
                for j in range(i + 1, jmax):
                    if sidx[i] == sidx[j]:
                        continue
                    d_zero = abs(self.zeros[sidx[i]] - self.zeros[sidx[j]]) + GAP
                    d_text = float(j - i)
                    couple = 2.0 if self.dirac_pole(self.zeros[sidx[i]]) == self.dirac_pole(self.zeros[sidx[j]]) else 1.0
                    w = sE[i] * sE[j] * couple / (d_zero * d_text)
                    self.a_add(sidx[i], sidx[j], w)

    def learn(self, text):
        self.learn_ex(text, NS_FT_PROSE)

    # ── hear / speak ──────────────────────────────────────────────────────────
    def _arrays(self):
        if self.A is not None:                      # a learn() happened: rebuild arrays from the dict
            ks = list(self.A.keys())
            self.Ai = np.array([k[0] for k in ks], dtype=np.int64)
            self.Aj = np.array([k[1] for k in ks], dtype=np.int64)
            self.Aw = np.array([self.A[k] for k in ks], dtype=np.float64)
        return self.Ai, self.Aj, self.Aw

    # monad.c: monad_hear_raw
    def hear_raw(self, query):
        act = []
        for t in tok_split(query):
            idx, E, known = self.wm_get(t)
            act.append((idx, E, known, t))
        return act

    # monad.c: surface_canonical
    @staticmethod
    def surface_canonical(w):
        b = w.encode("utf-8")
        n = len(b)
        if n < 3 or n > 15:
            return False
        vowels = digits = uppers = specials = 0
        for c in b:
            if 48 <= c <= 57: digits += 1
            if 65 <= c <= 90: uppers += 1
            if c in b"aeiouAEIOU": vowels += 1
            if c in (95, 45, 39) or c > 127: specials += 1
        if digits > 0 or uppers > 1 or specials > 1:
            return False
        if n >= 5 and vowels * 100 // n < 20:
            return False
        if n < 5 and vowels == 0:
            return False
        return True

    # monad.c: near_canonical  (4 passes, ±TRANSLATE_RADIUS=50)
    def near_canonical(self, idx, R=50):
        V = self.vocab
        def ok(i, ps):
            v = V.get(i)
            return v is not None and (ps is None or v["ps"] == ps) and self.surface_canonical(v["word"])
        for ps in (3, 1, 2):
            for r in range(R + 1):
                lo, hi = idx - r, idx + r
                if r == 0:
                    if ok(idx, ps): return V[idx]["word"]
                else:
                    if lo >= 0 and ok(lo, ps): return V[lo]["word"]
                    if hi < self.N and ok(hi, ps): return V[hi]["word"]
        for r in range(R + 1):                                   # pass 4: any canonical word in the radius
            lo, hi = idx - r, idx + r
            if lo >= 0 and ok(lo, None): return V[lo]["word"]
            if hi < self.N and ok(hi, None): return V[hi]["word"]
        return V[idx]["word"] if idx in V else ""

    # monad.c: fermat_space_utf8
    @staticmethod
    def fermat_space(norm_jn):
        third = [0x8B, 0x89, 0x88, 0x87, 0x86, 0x85, 0x84, 0x83]
        lvl = min(int(norm_jn * 8), 7)
        return bytes([0xE2, 0x80, third[lvl]]).decode("utf-8")

    # monad.c: monad_speak   (verbose output omitted; the same quantities are returned in `tr`)
    def speak(self, query, max_tokens=50, tr=None):
        N = self.N
        tr = tr if tr is not None else {}
        if query:
            act = self.hear_raw(query)
            psi = [(a[0], a[1]) for a in act]
            tr["hear"] = [(a[3], a[0], a[1], a[2]) for a in act]
        else:
            psi = [(i, self.vocab[i]["E"] if i in self.vocab else D_STAR) for i in range(min(N, 200))]
        n_act = len(psi)
        beta = np.array(self.beta); age = np.array(self.age, dtype=np.int64)
        phi_rot = float(np.float32(self.affect)) * (math.pi * 0.5)
        J = np.zeros(N)
        for idx, E in psi:
            J[idx] += beta[idx] * E * E * math.exp(-LAMBDA * age[idx])
        for idx, E in psi:                                       # spectral spread, sequential as in C
            Jc = J[idx]
            if Jc <= 0.0: continue
            for dn in range(1, SPREAD_RADIUS + 1):
                ws = math.exp(-SPREAD_DECAY * dn)
                if idx - dn >= 0: J[idx - dn] += Jc * ws
                if idx + dn < N: J[idx + dn] += Jc * ws
        Ai, Aj, Aw = self._arrays()
        J0 = J.copy()
        clamped = np.minimum(Aw, 1.0 / GAP)
        wt = np.exp(-LAMBDA * age)
        m0 = J0[Ai] > 0.0                                        # pass 0, Emerger i→j
        J += np.bincount(Aj[m0], weights=J0[Ai[m0]] * clamped[m0] * beta[Aj[m0]] * wt[Aj[m0]], minlength=N)
        m1 = J0[Aj] > 0.0                                        # pass 1, Reverse Emerger j→i
        J += np.bincount(Ai[m1], weights=J0[Aj[m1]] * clamped[m1] * beta[Ai[m1]] * wt[Ai[m1]], minlength=N)
        present = np.zeros(N, dtype=bool); Ev = np.zeros(N)
        for i, v in self.vocab.items(): present[i] = True; Ev[i] = v["E"]
        sum_V = float(np.sum(np.where(present, beta * Ev * Ev, 0.0)))
        sum_T = sum(E * E for _, E in psi)
        den = sum_T + sum_V
        lag = sum_T / den if den > 0.0 else 0.5
        actual_max = min(4 + int(max_tokens * lag), max_tokens)
        zeros = np.array(self.zeros)
        pointer = 0
        if n_act > 0:
            g = sorted(zeros[i] for i, _ in psi)
            pg = g[n_act // 2]
            pointer = int(np.argmin(np.abs(zeros - pg)))
        dp = abs(pointer - self.last_pointer)
        if dp > N // 2: dp = N - dp
        a = np.float32(self.affect) + np.float32(0.2 if dp < N // 20 else -0.1)
        self.affect = float(max(np.float32(-1.0), min(np.float32(1.0), a)))
        self.last_pointer = pointer
        J_max = float(J.max()); J_floor = max(J_max * 0.01, GAP)
        step = max(int(math.floor(N / (PHI * PHI) + 0.5)), 1)
        target_E = (sum_V / den) * OMEGA_ZS if den > 0.0 else OMEGA_ZS * 0.5
        dem, best = -1, 1e18
        for i in range(N):
            if i not in self.vocab or J[i] <= J_floor: continue
            if math.cos(zeros[i] * 0.5 + phi_rot) <= 0.0: continue
            if not token_accept(self.vocab[i]["word"], NS_FT_PROSE): continue
            dE = abs(self.vocab[i]["E"] - target_E)
            if dE < best: best, dem = dE, i
        out, written, emitted = "", 0, []
        if dem >= 0:
            out += self.near_canonical(dem); written += 1
            emitted.append(("demotic", dem, self.vocab[dem]["word"], out))
        w = pointer
        for _ in range(N):
            if written >= actual_max: break
            w = (w + step) % N
            if w == dem or w not in self.vocab or J[w] <= J_floor: continue
            if math.cos(zeros[w] * 0.5 + phi_rot) <= 0.0: continue
            word = self.vocab[w]["word"]
            if not token_accept(word, NS_FT_PROSE): continue
            surf = self.near_canonical(w)
            jn = J[w] / J_max if J_max > 0.0 else 0.0
            sp = self.fermat_space(jn)
            out += (sp if out else "") + surf; written += 1
            emitted.append(("walk", w, word, surf, float(J[w]), sp))
        self.age = [x + 1 for x in self.age]
        for i, _ in psi: self.age[i] = 0
        tr.update(dict(sum_V=sum_V, sum_T=sum_T, lag_ratio=lag, actual_max=actual_max, pointer=pointer, J_max=J_max, J_floor=J_floor,
                       golden_step=step, target_E=target_E, demotic=dem, emitted=emitted, phi_rot=phi_rot))
        return out

    # monad.c: monad_speak_wick
    def speak_wick(self, query, max_tokens=50, tr=None):
        saved = self.affect
        self.affect = -1.0
        out = self.speak(query, max_tokens, tr)
        self.affect = saved
        return out
