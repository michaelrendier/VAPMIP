#!/usr/bin/env python3
"""zh_half_line.py — M2: one Chinese character → a zero on the critical line σ = ½, and an energy E.  SINGLE CHARACTERS ONLY.

A character is an ideogram: its structure is its meaning.  This mechanism reads structure, not spelling.
  1. dictionary order   the characters are put in the dictionary's own order: Kangxi radical, residual strokes, key component, code point   (Unihan kRSUnicode, cjkvi-ids)
  2. slot               the i-th of M characters takes slot ⌊(i + ½)·N / M⌋, N = 25 000: radical neighbours are slot neighbours, every slot holds about M/N characters, and the characters
                        that share a slot accumulate there (none outranks another)
  3. zero               slot k lands on the exact zero ρ_{k+1} = ½ + iγ_{k+1} of ζ (SpecTools/zeros/zeros_exact_25000.tsv, found by SpecTools/zeros/zeros_exact.py), not on an approximation
  4. energy             E = d* + (Ω − d*)·frac(key/φ): the golden-ratio (Fibonacci) hash of the KEY COMPONENT, in exact 64-bit integers (0x9E3779B97F4A7C15 = ⌊2⁶⁴/φ⌋).
                        The key is the component of the character other than its radical (the phonetic part of a pictophonetic character); a simple character is its own key.
                        Equal E therefore means "same other component"; the character 月 and every character that carries 月 as its non-radical part share E.
Constants used: N, φ, d* = Ω/ln 10 (d*_taut), Ω = W(1), ln 10, and the zeros.  Nothing else.

    from zh_half_line import Table; T = Table(); T.address("河")
    .venv/bin/python tools/zh_half_line.py --selftest
"""
import collections, hashlib, json, math, os, random, re, sys, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from dprint import dprint
from zh_structure import load
ROOT = os.path.abspath(os.path.join(HERE, ".."))
M64 = (1 << 64) - 1
N = 25000                                         # MONAD_N_DEFAULT
GOLD64 = 0x9E3779B97F4A7C15                       # ⌊2⁶⁴/φ⌋
OMEGA = 0.5671432904097838                        # Ω_ZS = W(1)
LN10 = math.log(10.0)
DSTAR = OMEGA / LN10                              # d*_taut, the radial unit
IDC = set("⿰⿱⿲⿳⿴⿵⿶⿷⿸⿹⿺⿻")
dprint("N", N); dprint("OMEGA", OMEGA); dprint("DSTAR (d*_taut)", DSTAR)

def zeros(path=None):
    path = path or os.path.join(ROOT, "SpecTools", "zeros", "zeros_exact_25000.tsv")
    g = {}
    for line in open(path):
        if line[0] == "k": continue
        k, v = line.split("\t"); g[int(k)] = float(v)
    return g

def key_of(C, c):
    """the component of c other than its radical; c itself when c is simple or has no decomposition on file"""
    r = C[c]; ids = r.get("ids")
    if not ids or ids == c: return c
    L = [l for l in ids if l not in IDC and l != "？"]
    if len(L) < 2: return c
    sem = [l for l in L if l in C and C[l]["rad"] == r["rad"]]
    other = [l for l in L if l not in sem[:1]]
    return other[0] if other else c

def energy(cp):
    """E from the golden-ratio hash of a code point, exact integers (the engine's own construction)"""
    s = (cp * GOLD64) & M64
    return DSTAR + (s >> 11) / 9007199254740992.0 * (OMEGA - DSTAR)

class Table:
    def __init__(self):
        D = load(); self.C = D["chars"]; C = self.C; self.M = len(C)
        self.key = {c: key_of(C, c) for c in C}
        order = sorted(C, key=lambda c: (C[c]["rad"], C[c]["res"], ord(self.key[c]), ord(c)))
        self.order = order; self.index = {c: i for i, c in enumerate(order)}
        self.slot = {c: ((2 * i + 1) * N) // (2 * self.M) for c, i in self.index.items()}
        self._z = None
    def gamma(self, k):
        if self._z is None: self._z = zeros()
        return self._z[k]
    def address(self, c):
        if len(c) != 1: raise ValueError("M2 maps a single character; a word of two characters is two addresses and a relation (pair())")
        if c not in self.slot: raise KeyError(f"{c!r} is not in the Han alphabet on file")
        s = self.slot[c]; k = s + 1; kc = self.key[c]
        return {"char": c, "slot": s, "zero_index": k, "gamma": self.gamma(k), "sigma": 0.5, "E": energy(ord(kc)), "key": kc}
    def pair(self, a, b):
        x, y = self.address(a), self.address(b)
        return {"a": x, "b": y, "d_slot": y["slot"] - x["slot"], "d_E": y["E"] - x["E"], "same_radical": self.C[a]["rad"] == self.C[b]["rad"]}
    def digest(self):
        h = hashlib.sha256()
        for c in self.order: h.update(f"{ord(c)}\t{self.slot[c]}\t{ord(self.key[c])}\n".encode())
        return h.hexdigest()

def circ(a, b): d = abs(a - b); return min(d, N - d)

def selftest(T, out):
    C = T.C; res = {}
    res["characters"] = len(C); res["table_sha256"] = T.digest(); res["table_sha256_again"] = Table().digest()
    res["deterministic"] = res["table_sha256"] == res["table_sha256_again"]
    es = [energy(ord(T.key[c])) for c in C]
    res["E_min"] = min(es); res["E_max"] = max(es); res["E_in_range"] = DSTAR <= min(es) and max(es) < OMEGA
    res["slot_min"] = min(T.slot.values()); res["slot_max"] = max(T.slot.values())
    occ = collections.Counter(T.slot.values()); L = [occ.get(s, 0) for s in range(N)]
    res["occupancy"] = {"max": max(L), "min": min(L), "empty_slots": sum(1 for x in L if x == 0), "mean": sum(L) / N,
                        "hist": dict(sorted(collections.Counter(L).items()))}
    rad_mixed = sum(1 for s in occ if len({C[c]["rad"] for c in C if False}) ) if False else None
    bys = collections.defaultdict(set)
    for c, s in T.slot.items(): bys[s].add(C[c]["rad"])
    res["slots_with_more_than_one_radical"] = sum(1 for v in bys.values() if len(v) > 1)
    res["monotone_in_dictionary_order"] = all(T.slot[T.order[i]] <= T.slot[T.order[i + 1]] for i in range(len(T.order) - 1))
    pe = collections.Counter((T.slot[c], energy(ord(T.key[c]))) for c in C)
    res["distinct_slot_E_pairs"] = len(pe); res["characters_sharing_slot_E_with_another"] = sum(v for v in pe.values() if v > 1)
    ex = [(s, e) for (s, e), v in pe.items() if v > 1][:6]
    res["shared_slot_E_examples"] = [["".join(c for c in C if T.slot[c] == s and energy(ord(T.key[c])) == e)] for s, e in ex]
    # exact zeros, spot checks against ζ itself
    z = zeros(); res["zeros_loaded"] = len(z)
    import mpmath as mp
    mp.mp.dps = 25; random.seed(11); worst = 0.0
    for k in random.sample(sorted(z), 60):
        worst = max(worst, float(abs(mp.zeta(mp.mpf("0.5") + 1j * mp.mpf(z[k])))))
    res["zeta_abs_at_60_random_zeros_max"] = worst
    # every character addressed, single-character guard
    bad = 0
    for c in C:
        a = T.address(c); bad += not (a["sigma"] == 0.5 and 1 <= a["zero_index"] <= N and DSTAR <= a["E"] < OMEGA)
    res["addresses_out_of_range"] = bad
    try: T.address("河流"); res["two_char_guard"] = False
    except ValueError: res["two_char_guard"] = True
    # held-out probes (none of these data are used by the mechanism)
    two = load()["two"]; pairs = [(a, b) for a, b in two if a in C and b in C and a != b]
    random.seed(3); sh = [b for a, b in pairs]; random.shuffle(sh); rnd = [(a, b2) for (a, b), b2 in zip(pairs, sh) if a != b2]
    pr = {}
    for eps in (0.002, 0.02):
        cm = sum(circ(T.slot[a], T.slot[b]) < eps * N for a, b in pairs) / len(pairs); rr = sum(circ(T.slot[a], T.slot[b]) < eps * N for a, b in rnd) / len(rnd)
        pr[f"compounds_within_{eps}"] = {"observed": cm, "shuffled_baseline": rr, "enrichment": cm / rr}
    for k in (0, 1, 3, 10):
        cm = sum(circ(T.slot[a], T.slot[b]) <= k for a, b in pairs) / len(pairs); rr = sum(circ(T.slot[a], T.slot[b]) <= k for a, b in rnd) / len(rnd)
        pr[f"compounds_within_{k}_slots_basin"] = {"observed": cm, "shuffled_baseline": rr, "enrichment": cm / rr if rr else None}
    pr["compounds_share_radical"] = {"observed": sum(C[a]["rad"] == C[b]["rad"] for a, b in pairs) / len(pairs), "shuffled_baseline": sum(C[a]["rad"] == C[b]["rad"] for a, b in rnd) / len(rnd)}
    STOP = set("a an the of to or and in on for with by be is as at it from that this one any used also".split())
    G = {c: {w for w in re.findall(r"[a-z]+", C[c]["defn"].lower()) if w not in STOP and len(w) > 2} for c in C if C[c].get("defn")}
    gc = list(G); random.seed(5); gp = [tuple(random.sample(gc, 2)) for _ in range(300000)]
    for eps in (0.002, 0.02):
        near = [bool(G[a] & G[b]) for a, b in gp if circ(T.slot[a], T.slot[b]) < eps * N]; far = [bool(G[a] & G[b]) for a, b in gp if circ(T.slot[a], T.slot[b]) >= eps * N]
        pr[f"gloss_overlap_within_{eps}"] = {"near": sum(near) / len(near), "far": sum(far) / len(far), "enrichment": (sum(near) / len(near)) / (sum(far) / len(far)), "near_pairs": len(near)}
    for k in (0, 1, 3):
        near = [bool(G[a] & G[b]) for a, b in gp if circ(T.slot[a], T.slot[b]) <= k]; far = [bool(G[a] & G[b]) for a, b in gp if circ(T.slot[a], T.slot[b]) > k]
        pr[f"gloss_overlap_within_{k}_slots_basin"] = {"near_pairs": len(near), "near": (sum(near) / len(near)) if near else None, "far": sum(far) / len(far)}
    var = list({tuple(sorted((c, chr(int(t, 16))))) for c in C for k in ("sem", "trad", "simp") if C[c].get(k) for t in re.findall(r"U\+([0-9A-F]+)", C[c][k]) if chr(int(t, 16)) in C and chr(int(t, 16)) != c})
    random.seed(7); rv = [tuple(random.sample(list(C), 2)) for _ in range(len(var))]
    pr["variant_pairs_within_0.02"] = {"observed": sum(circ(T.slot[a], T.slot[b]) < 0.02 * N for a, b in var) / len(var), "random_pairs": sum(circ(T.slot[a], T.slot[b]) < 0.02 * N for a, b in rv) / len(rv), "pairs": len(var)}
    def tl(p): return unicodedata.normalize("NFD", p).encode("ascii", "ignore").decode()
    bykey = collections.defaultdict(list)
    for c in C:
        if T.key[c] != c and "mand" in C[c]: bykey[T.key[c]].append(c)
    same = tot = 0
    for k, cs in bykey.items():
        for i in range(len(cs)):
            for j in range(i + 1, len(cs)): tot += 1; same += tl(C[cs[i]]["mand"]) == tl(C[cs[j]]["mand"])
    pool = [c for c in C if "mand" in C[c] and T.key[c] != c]; random.seed(1); hit = sum(tl(C[a]["mand"]) == tl(C[b]["mand"]) for a, b in (random.sample(pool, 2) for _ in range(200000)))
    pr["same_key_share_toneless_pinyin"] = {"same_key_pairs": tot, "observed": same / tot, "random_pairs": hit / 200000}
    res["held_out_probes"] = pr
    json.dump(res, open(out, "w"), ensure_ascii=False, indent=1)
    return res

if __name__ == "__main__":
    T = Table()
    if "--selftest" in sys.argv:
        out = os.path.join(ROOT, "data", "zh_half_line_selftest.json"); r = selftest(T, out)
        print(json.dumps(r, ensure_ascii=False, indent=1)[:6000])
        with open(os.path.join(ROOT, "data", "zh_half_line_addresses.tsv"), "w") as f:
            f.write("char\tcodepoint\tradical\tresidual\tkey\tslot\tzero_index\tgamma\tE\n")
            for c in T.order:
                a = T.address(c); f.write(f"{c}\tU+{ord(c):04X}\t{T.C[c]['rad']}\t{T.C[c]['res']}\t{a['key']}\t{a['slot']}\t{a['zero_index']}\t{a['gamma']:.12f}\t{a['E']:.10f}\n")
    else:
        for c in sys.argv[1:]: print(T.address(c))
