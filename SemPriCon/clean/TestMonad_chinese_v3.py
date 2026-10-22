#!/usr/bin/env python3
"""TestMonad_chinese_v3.py — the v3 speaker for the chinese bin (naming: SpecTools/NAMING_CONVENTION.md). Reads test_chinese_v3.bin, read-only.

CHINESE mechanism: a slot holds one character (a morpheme with a stored form), so there are no spelling rules to apply. A candidate slot is accepted
only if its label is a single Han character (TESTMONAD-C1); the character is emitted as it stands, without the near-canonical spelling search
(C2); characters are joined with no separators (C3; J/J_max is kept in the trace). Hearing is by character through M4 (zh_uns).

Both v3 speakers are copies of the same engine step (monad_py.Monad.speak: hear, spread, golden walk), so that the two language mechanisms can be
observed side by side. Every deviation from the engine is marked  # TESTMONAD-Fn  and listed in clean/ notepad (wiki_notepad/v3/).
  TESTMONAD-F2  trace only: tr['funnel'] counts the candidates left after each gate.
  TESTMONAD-F1  the absolute floor GAP is dropped from J_floor (found 2026-10-22: all three v3 bins spoke '' because J_max < GAP).

    ../.venv/bin/python TestMonad_chinese_v3.py [--bin PATH] [--exact-zeros] [prompt ...]
"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, ".."))
for d in ("UNS", "Flat"):                                   # the mapping machinery is run from mappings/ (mirrors of tools/)
    sys.path.insert(0, os.path.join(ROOT, "mappings", d))
sys.path.insert(0, os.path.join(ROOT, "tools"))             # monad_pyu (the Unicode port of the monad) is shared machinery
import numpy as np
import monad_pyu as pyu
mp = pyu.mp                                                 # the monad_py instance MonadU actually uses (monad_pyu loads its own copy)
import monad_pyu as pyu
from uns_mech import en_uns, zh_uns
from zh_half_line import Table, zeros as exact_zeros
T = Table()
SEP = {chr(c) for c in range(0x200B, 0x2004)}


def uns_coords(surface, N=mp.N_DEFAULT):
    """The address of any word the bin does not already hold: M4 for a single Han character, M3 for everything else."""
    a = zh_uns(T, surface) if (len(surface) == 1 and pyu.u_is_han(ord(surface)) and surface in T.index) else en_uns(surface)
    return a["slot"], a["E"]


mp.word_coords = pyu.word_coords = uns_coords


class TestMonadChinese(pyu.MonadU):
    @staticmethod
    def _han(w): return len(w) == 1 and pyu.u_is_han(ord(w))

    def speak(self, query, max_tokens=50, tr=None):
        N = self.N
        tr = tr if tr is not None else {}
        if query:
            act = self.hear_raw(query)
            psi = [(a[0], a[1]) for a in act]
            tr["hear"] = [(a[3], a[0], a[1], a[2]) for a in act]
        else:
            psi = [(i, self.vocab[i]["E"] if i in self.vocab else mp.D_STAR) for i in range(min(N, 200))]
        n_act = len(psi)
        beta = np.array(self.beta); age = np.array(self.age, dtype=np.int64)
        phi_rot = float(np.float32(self.affect)) * (math.pi * 0.5)
        J = np.zeros(N)
        for idx, E in psi:
            J[idx] += beta[idx] * E * E * math.exp(-mp.LAMBDA * age[idx])
        for idx, E in psi:                                       # spectral spread, sequential as in C
            Jc = J[idx]
            if Jc <= 0.0: continue
            for dn in range(1, mp.SPREAD_RADIUS + 1):
                ws = math.exp(-mp.SPREAD_DECAY * dn)
                if idx - dn >= 0: J[idx - dn] += Jc * ws
                if idx + dn < N: J[idx + dn] += Jc * ws
        Ai, Aj, Aw = self._arrays()
        J0 = J.copy()
        clamped = np.minimum(Aw, 1.0 / mp.GAP)
        wt = np.exp(-mp.LAMBDA * age)
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
        J_max = float(J.max()); J_floor = J_max * 0.01      # TESTMONAD-F1: the engine's max(J_max*0.01, GAP) leaves nothing above the floor in a one-pass v3 bin (J_max 6e-4 < GAP 7.07e-4)
        step = max(int(math.floor(N / (mp.PHI * mp.PHI) + 0.5)), 1)
        _inJ = [i for i in self.vocab if J[i] > J_floor]                # TESTMONAD-F2: the candidate funnel, trace only
        tr["funnel"] = dict(vocab=len(self.vocab), J_above_floor=len(_inJ),
                            phase_ok=sum(1 for i in _inJ if math.cos(zeros[i] * 0.5 + phi_rot) > 0.0),
                            accepted=sum(1 for i in _inJ if math.cos(zeros[i] * 0.5 + phi_rot) > 0.0 and self._han(self.vocab[i]['word'])))
        target_E = (sum_V / den) * mp.OMEGA_ZS if den > 0.0 else mp.OMEGA_ZS * 0.5
        dem, best = -1, 1e18
        for i in range(N):
            if i not in self.vocab or J[i] <= J_floor: continue
            if math.cos(zeros[i] * 0.5 + phi_rot) <= 0.0: continue
            if not self._han(self.vocab[i]["word"]): continue          # TESTMONAD-C1: a Han character, not a spelling rule
            dE = abs(self.vocab[i]["E"] - target_E)
            if dE < best: best, dem = dE, i
        out, written, emitted = "", 0, []
        if dem >= 0:
            out += self.vocab[dem]["word"]; written += 1               # TESTMONAD-C2: the character itself, no spelling canonicalisation
            emitted.append(("demotic", dem, self.vocab[dem]["word"], out))
        w = pointer
        for _ in range(N):
            if written >= actual_max: break
            w = (w + step) % N
            if w == dem or w not in self.vocab or J[w] <= J_floor: continue
            if math.cos(zeros[w] * 0.5 + phi_rot) <= 0.0: continue
            word = self.vocab[w]["word"]
            if not self._han(word): continue                              # TESTMONAD-C1
            surf = word                                                  # TESTMONAD-C2
            jn = J[w] / J_max if J_max > 0.0 else 0.0
            sp = ""                                                    # TESTMONAD-C3: Chinese text has no inter-word spaces; J/J_max stays in the trace
            out += (sp if out else "") + surf; written += 1
            emitted.append(("walk", w, word, surf, float(J[w]), sp))
        self.age = [x + 1 for x in self.age]
        for i, _ in psi: self.age[i] = 0
        tr.update(dict(sum_V=sum_V, sum_T=sum_T, lag_ratio=lag, actual_max=actual_max, pointer=pointer, J_max=J_max, J_floor=J_floor,
                       golden_step=step, target_E=target_E, demotic=dem, emitted=emitted, phi_rot=phi_rot))
        return out

    def speak_wick(self, query, max_tokens=50, tr=None):
        saved = self.affect; self.affect = -1.0
        try: return self.speak(query, max_tokens, tr)
        finally: self.affect = saved


def show(s):
    return "".join(" | " if c in SEP else c for c in s)


def main(argv):
    exact = "--exact-zeros" in argv
    path = os.path.join(HERE, "test_chinese_v3.bin")
    if "--bin" in argv: path = argv[argv.index("--bin") + 1]
    prompts = [a for a in argv if not a.startswith("--") and a != path] or ['水 火', '人 大']
    for p in prompts:
        m = TestMonadChinese.from_bin(path)
        if exact: Z = exact_zeros(); m.zeros = [Z[k + 1] for k in range(m.N)]
        tr = {}; out = m.speak_wick(p, 50, tr)
        print(f"=== {p!r}\n  reply: {show(out)!r}")
        print(f"  heard: {[(t, i, 'known' if k else 'new') for i, E, k, t in m.hear_raw(p)]}")
        print(f"  lag {tr['lag_ratio']:.3f}  target_E {tr['target_E']:.5f}  J_max {tr['J_max']:.3g}  floor {tr['J_floor']:.3g}  demotic {tr['demotic']}  emitted {[(e[0], e[1], e[2]) for e in tr['emitted']]}\n  funnel {tr['funnel']}")


if __name__ == "__main__":
    main(sys.argv[1:])
