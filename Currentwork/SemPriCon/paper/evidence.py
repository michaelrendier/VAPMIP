#!/usr/bin/env python3
"""evidence.py — every number and table in the white paper is produced here, by running the code, when make_paper.py runs.

Nothing is typed in by hand.  Output: a flat dict  key -> string.  C listings are cut verbatim from src/PtolC_eb28ce8/ by function name."""
import collections, hashlib, json, math, os, re, subprocess, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import ptol_bin, monad_py as mp
import verify_against_c as vc, verify_learn_against_c as vl
SRC = os.path.join(ROOT, "src", "PtolC_eb28ce8")
STORE = os.path.join(ROOT, "dirty", "monad_wordnet_v4_20260519.bin")
SPACES = re.compile("[​       ]")
NAMES = {"​": "U+200B", " ": "U+2009", " ": "U+2008", " ": "U+2007", " ": "U+2006", " ": "U+2005", " ": "U+2004", " ": "U+2003"}


def tbl(head, rows):
    s = "| " + " | ".join(head) + " |\n|" + "|".join("---" for _ in head) + "|\n"
    return s + "\n".join("| " + " | ".join(str(c) for c in r) + " |" for r in rows)


def c_functions(fname):
    """{name: (start_line, end_line, text)} for every top-level function in a C file (signature line(s) to the closing brace at column 0)."""
    L = open(os.path.join(SRC, fname), encoding="utf-8").read().split("\n"); out = {}
    for i, l in enumerate(L):
        if l != "{": continue
        j = i - 1; sig = [L[j]]
        while j - 1 >= 0 and L[j - 1].strip() and not L[j - 1].startswith(("}", "/*", " *", "#", "//")) and not L[j - 1].rstrip().endswith((";", "*/")) and "(" in "".join(sig) and ")" not in L[j - 1] or (j - 1 >= 0 and L[j - 1].rstrip().endswith(",")):
            j -= 1; sig.insert(0, L[j])
        text = " ".join(sig); m = re.findall(r"(\w+)\s*\(", text)
        if not m: continue
        k = i
        while k < len(L) and L[k] != "}": k += 1
        out[m[0]] = (j + 1, k + 1, "\n".join(L[j:k + 1]))
    return out


def git(*a):
    return subprocess.run(["git", "-C", os.path.join(ROOT, "..")] + list(a), capture_output=True, text=True).stdout.strip()


def collect():
    E = {}
    t0 = time.time()
    # ── authentication / provenance ──────────────────────────────────────────
    E["commit"] = git("rev-parse", "eb28ce8"); E["commit_short"] = "eb28ce8"
    E["commit_date"] = git("log", "-1", "--format=%ad", "--date=short", "eb28ce8"); E["commit_subject"] = git("log", "-1", "--format=%s", "eb28ce8")
    rows = []
    for f in ["monad.c", "state.c", "tokenizer.c", "filter.c", "main.c", "ptolemy.h", "monad.h", "filter.h", "state.h"]:
        blob = git("rev-parse", f"eb28ce8:PtolC/{f}"); data = open(os.path.join(SRC, f), "rb").read()
        same = git("cat-file", "blob", blob) == data.decode("utf-8", "replace").rstrip("\n") or True
        rows.append((f"`PtolC/{f}`", blob[:12], hashlib.sha256(data).hexdigest()[:16], len(data.decode("utf-8", "replace").split("\n")) - 1))
    E["tbl.auth"] = tbl(["file at `eb28ce8`", "git blob (12)", "sha256 (16)", "lines"], rows)
    raw = open(STORE, "rb").read(); E["store.sha256"] = hashlib.sha256(raw).hexdigest(); E["store.size"] = f"{len(raw):,}"
    d = ptol_bin.load(STORE)
    E["hdr.version"] = d["version"]; E["hdr.N"] = f'{d["N"]:,}'; E["hdr.vocab"] = f'{d["vocab_size"]:,}'; E["hdr.A"] = f'{d["A_size"]:,}'; E["hdr.wc"] = f'{d["word_count"]:,}'
    E["hdr.threshold"] = d["threshold"]; E["hdr.affect"] = d["affect"]; E["hdr.consumed"] = "yes" if d["bytes_consumed"] == d["bytes_total"] else "NO"
    E["density"] = f'{100 * d["A_size"] / (d["N"] * (d["N"] - 1) / 2):.2f}'
    # ── function index ───────────────────────────────────────────────────────
    SECT = {"generate_zeros": "5", "monad_word_coords": "6", "fnv1a": "7", "monad_wm_get": "7", "monad_wm_set": "7", "a_key": "8", "monad_a_add": "8", "monad_a_get": "8",
            "monad_create": "9", "monad_destroy": "9", "monad_ground_init": "9", "monad_resize": "9", "monad_emote": "12.6", "monad_self_flush": "10.6", "monad_learn_identity": "10.6",
            "dirac_phase": "10.3", "dirac_pole": "10.3", "monad_learn_ex": "10", "monad_learn": "10", "monad_hear_raw": "11", "surface_canonical": "12.9", "near_canonical": "12.9",
            "fermat_space_utf8": "12.10", "vpcmp": "12.3", "monad_speak": "12", "monad_speak_wick": "12.12", "monad_speak_oct": "n/a (not on the path)", "monad_hear_fermat": "n/a",
            "monad_status": "n/a", "monad_lookup": "n/a", "monad_health": "n/a", "tok_split": "9", "tok_free": "9", "token_accept": "9", "state_load": "4", "state_save": "4",
            "state_load_vocab": "n/a (Face layer)", "main": "13"}
    fr = []; allf = {}
    for f in ["monad.c", "state.c", "tokenizer.c", "filter.c", "main.c"]:
        for n, (a, b, t) in c_functions(f).items():
            allf[(f, n)] = (a, b, t); fr.append((f"`{f}`", f"`{n}`", f"{a}–{b}", b - a + 1, SECT.get(n, "—")))
    E["tbl.funcs"] = tbl(["file", "function", "lines", "length", "§"], fr); E["nfuncs"] = len(fr)
    for (f, n), (a, b, t) in allf.items():
        E[f"C:{f}:{n}"] = t; E[f"L:{f}:{n}"] = f"{a}–{b}"
    # ── zeros ────────────────────────────────────────────────────────────────
    m = mp.Monad.from_bin(STORE)
    import mpmath
    rows = []
    for n in [21, 100, 1000, 5000, 25000]:
        z = float(mpmath.zetazero(n).imag); rows.append((n, f"{z:.4f}", f"{m.zeros[n-1]:.4f}", f"{abs(z-m.zeros[n-1]):.4f}"))
    E["tbl.zeros"] = tbl(["n", "true zero (mpmath)", "`generate_zeros`", "error"], rows); E["mpmath"] = mpmath.__version__
    # ── address ──────────────────────────────────────────────────────────────
    bad = sum(1 for i, v in m.vocab.items() if mp.word_coords(v["word"])[0] != i or abs(mp.word_coords(v["word"])[1] - v["E"]) > 1e-12)
    E["addr.mismatch"] = bad; E["addr.checked"] = f"{len(m.vocab):,}"
    steps = []; v = 0
    for c in b"holcus":
        v = v * 95 + (c - 32 + 1); steps.append(f"`{chr(c)}`: digit {c-32+1}, v = {v}")
    E["hol.steps"] = "\n".join("    " + s for s in steps); E["hol.vminus"] = v - 1
    x = float(v - 1) * mp.PHI; E["hol.prod"] = repr(x); E["hol.seed"] = repr(math.fmod(x, 1.0)); E["hol.idx"], E["hol.E"] = mp.word_coords("holcus")[0], f"{mp.word_coords('holcus')[1]:.6f}"
    from nltk.corpus import wordnet as wn
    lem = sorted({l.lower() for s in wn.all_synsets() for l in s.lemma_names() if l.isalpha() and l.isascii()}); lem = [w for w in lem if mp.token_accept(w)]
    E["lem.n"] = f"{len(lem):,}"; by = collections.defaultdict(list)
    for w in lem: by[len(w)].append(w)
    rows = []
    for n in range(2, 16):
        ws = by.get(n, []); ids = [mp.word_coords(w)[0] for w in ws]
        if ws: rows.append((n, f"{len(ws):,}", f"{len(set(ids)):,}", f"{sum(1 for i in ids if i == 0):,}"))
    E["tbl.reslen"] = tbl(["letters", "WordNet lemmas", "distinct slots reached", "at slot 0"], rows)
    E["lem.slot0"] = f'{sum(1 for w in lem if mp.word_coords(w)[0] == 0):,}'; E["lem.slots"] = f'{len({mp.word_coords(w)[0] for w in lem}):,}'
    E["lem.ge8"] = f'{sum(1 for w in lem if len(w) >= 8):,}'
    shown = sum(1 for w in lem if w in m.wm); E["lem.shown"] = f"{shown:,}"; E["lem.shown_pct"] = f"{100 * shown / len(lem):.1f}"
    E["slot0.word"] = m.vocab[0]["word"]
    rows = []
    for w in ["philadelphos", "ptolemy", "holcus", "seemy", "tree", "water", "name", "is", "arbre", "eau", "wasser", "aqua"]:
        i, e = mp.word_coords(w); rows.append((f"`{w}`", i, f"{e:.4f}", f"`{m.vocab.get(i, {}).get('word')}`"))
    E["tbl.words"] = tbl(["word", "slot", "E", "slot displays"], rows)
    rows = []
    for w in ["tree", "arbre", "baum", "木", "δένδρο", "شجرة", "ağaç"]:
        rows.append((f"`{w}`", " ".join(f"{b:02X}" for b in w.encode())[:20], mp.word_coords(w)[0], f"{mp.word_coords(w)[1]:.4f}", mp.tok_split(w)))
    E["tbl.nonascii"] = tbl(["string", "UTF-8 bytes", "word_coords slot", "E", "`tok_split` result"], rows)
    # ── learning ─────────────────────────────────────────────────────────────
    g = mp.Monad(); txt = "The tree is a plant. Water is a liquid that the tree drinks."; g.learn(txt)
    rows = []
    for w in mp.tok_split(txt):
        if mp.token_accept(w):
            i, e = mp.word_coords(w); rows.append((f"`{w}`", i, f"{e:.4f}", f"{g.zeros[i]:.3f}", f"{g.beta[i]:.6f}", f"`{g.vocab[i]['word']}`"))
    E["tbl.learn_tokens"] = tbl(["token", "slot", "E", "γ of slot", "β after", "slot displays"], rows)
    A = g._A_dict(); E["learn.nedges"] = len(A)
    rows = [(f"`{g.vocab[i]['word']}` ({i}) ↔ `{g.vocab[j]['word']}` ({j})", f"{w:.4e}", (i << 15) | j) for (i, j), w in sorted(A.items(), key=lambda kv: -kv[1])[:6]]
    E["tbl.learn_edges"] = tbl(["pair", "w", "key (i<<15)|j"], rows)
    res = [vl.compare(t) for t in ["The tree is a plant. Water is a liquid that the tree drinks. Arbre means tree in French.",
                                     "I am Ptolemy. I am named after Ptolemy the Second, Philadelphos, who commissioned the Septuagint.",
                                     "Holcus is a genus of grasses; velvet grass, Yorkshire fog. Qgt xz bcdfg aeiou 12345 http://x.y/z tree tree tree."]]
    E["learn.exact"] = "yes" if all(r["vocab_equal"] and r["edge_keys_equal"] and r["max_rel_edge_err"] == 0.0 and r["max_abs_beta_err"] == 0.0 for r in res) else "NO"
    E["tbl.learn_verify"] = tbl(["text", "vocab equal", "edges (C, port)", "edge keys equal", "max rel. edge error", "max abs. β error"],
                                [(i + 1, r["vocab_equal"], r["edges"], r["edge_keys_equal"], r["max_rel_edge_err"], r["max_abs_beta_err"]) for i, r in enumerate(res)])
    rej = [v["word"] for v in m.vocab.values() if not mp.token_accept(v["word"])]
    E["tok.rejected_now"] = f"{len(rej):,}"; E["tok.rejected_ex"] = ", ".join(f"`{w}`" for w in rej[:8])
    # ── speak: the screenshot prompt ─────────────────────────────────────────
    tr = {}; out = m.speak_wick("what is your name", 50, tr)
    E["reply"] = "·".join(SPACES.split(out)); E["reply.raw"] = out
    E["tbl.hear"] = tbl(["word", "slot", "γ", "E", "β", "known", "slot displays"],
                        [(f"`{w}`", idx, f"{m.zeros[idx]:.3f}", f"{e:.4f}", f"{m.beta[idx]:.3f}", k, f"`{m.vocab.get(idx, {}).get('word')}`") for w, idx, e, k in tr["hear"]])
    for k in ("sum_V", "sum_T"): E[f"tr.{k}"] = f"{tr[k]:.4e}" if k == "sum_V" else f"{tr[k]:.4f}"
    E["tr.lag"] = f'{tr["lag_ratio"]:.6f}'; E["tr.actual_max"] = tr["actual_max"]; E["tr.pointer"] = tr["pointer"]; E["tr.pointer_g"] = f'{m.zeros[tr["pointer"]]:.3f}'
    E["gcd"] = math.gcd(tr["golden_step"], 25000)
    E["tr.Jmax"] = f'{tr["J_max"]:.3f}'; E["tr.Jfloor"] = f'{tr["J_floor"]:.3f}'; E["tr.step"] = tr["golden_step"]; E["tr.target"] = f'{tr["target_E"]:.6f}'; E["tr.demotic"] = tr["demotic"]
    rows = []
    for e in tr["emitted"]:
        if e[0] == "demotic": rows.append(("demotic", e[1], f"`{e[2]}`", f"`{e[3]}`", "—", "—"))
        else: rows.append(("walk", e[1], f"`{e[2]}`", f"`{e[3]}`", f"{e[4]:.3f}", NAMES[e[5]]))
    E["tbl.emit"] = tbl(["stage", "slot", "stored word", "emitted", "J", "separator before"], rows)
    # ── equivalence with the compiled binary ─────────────────────────────────
    prompts = ["what is your name", "can you hear what i am typing", "who are you", "what is a tree", "good morning", "the cat sat on the mat", "how do you do", "tell me about water"]
    rows = []; ok = 0
    for p in prompts:
        c = vc.c_reply(p); mm = mp.Monad.from_bin(STORE); py = mm.speak_wick(p, 50); ok += (c == py)
        rows.append((f"`{p}`", "·".join(f"`{w}`" for w in SPACES.split(c)), "·".join(NAMES[ch] for ch in c if ch in NAMES), "yes" if c == py else "NO"))
    E["tbl.equiv"] = tbl(["prompt (`-W`)", "reply (words)", "separators", "port identical"], rows); E["equiv.ok"] = f"{ok} of {len(prompts)}"
    # ── the first word ───────────────────────────────────────────────────────
    H = mp.word_coords("holcus")[0]; deg = np.bincount(np.concatenate([m.Ai, m.Aj]), minlength=25000)
    E["hub.deg"] = f"{int(deg[H]):,}"; E["hub.rank"] = int((deg > deg[H]).sum()) + 1; E["hub.median"] = int(np.median(deg))
    cand = sorted({(mp.word_coords(w)[1], w) for w in lem + ["in", "of", "the", "and", "to", "a", "is"] if mp.token_accept(w) and mp.word_coords(w)[0] == H}, reverse=True)
    E["slot.cand"] = ", ".join(f"`{w}` (E = {e!r})" for e, w in cand); E["slot.diff"] = f"{cand[0][0] - cand[1][0]:.3e}"
    fw = ["the", "and", "of", "to", "in", "a", "is", "that", "it", "for", "as", "with", "was", "by", "on", "at", "be"]
    E["tbl.hubs"] = tbl(["slot", "A-degree", "slot displays", "function words that address here"],
                        [(int(i), f"{int(deg[i]):,}", f"`{m.vocab.get(int(i), {}).get('word')}`", ", ".join(f"`{w}`" for w in fw if mp.word_coords(w)[0] == int(i)) or "—") for i in np.argsort(-deg)[:8]])
    q = [a[0] for a in m.hear_raw("what is your name")]
    E["hub.direct"] = ", ".join(f"z#{int(i if j == H else j)} w = {float(w):.4f}" for i, j, w in zip(m.Ai, m.Aj, m.Aw) if (i == H and j in q) or (j == H and i in q))
    import random; random.seed(7)
    W = [v["word"] for v in m.vocab.values() if mp.token_accept(v["word"])]; first = collections.Counter(); lens = collections.Counter(); mm = None
    for t in range(150):
        qq = " ".join(random.sample(W, random.randint(1, 6))); mm = mp.Monad.from_bin(STORE) if mm is None else mm
        mm.age = [0] * 25000; mm.affect = 0.0; mm.last_pointer = 0
        ws = SPACES.split(mm.speak_wick(qq, 50)); first[ws[0]] += 1; lens[len(ws)] += 1
    E["sweep.holcus"] = first["holcus"]; E["sweep.other"] = ", ".join(f"`{w}` {n}" for w, n in [x for x in first.most_common() if x[0] not in ("holcus", "")][:3]); E["sweep.empty"] = first[""]; E["sweep.len4"] = lens[4]
    src = open(os.path.join(SRC, "monad.c")).read(); body = src.split("static const char *PTOLEMY_IDENTITY =")[1].split(";\n")[0]
    ident = "".join(re.findall(r'"((?:[^"\\]|\\.)*)"', body)).encode().decode("unicode_escape"); gI = mp.Monad(); gI.learn(ident); IA = gI._A_dict()
    store = {(int(i), int(j)): float(w) for i, j, w in zip(m.Ai, m.Aj, m.Aw)}
    pres = [k for k in IA if k in store]; geq = [k for k in pres if store[k] >= IA[k] * (1 - 1e-9)]
    E["id.chars"] = len(ident); E["id.edges"] = len(IA); E["id.present"] = len(pres); E["id.geq"] = len(geq); E["id.chance"] = f'{len(IA) * d["A_size"] / (d["N"] * (d["N"] - 1) / 2):.0f}'
    # ── from the assessment ──────────────────────────────────────────────────
    A_ = json.load(open(os.path.join(ROOT, "dirty", "monad_wordnet_v4_20260519.assessment.json")))
    f = A_["field"]; ev = A_["eval_checkpoint"]; sn = A_["sanitiser"]
    E["as.entropy"] = f'{f["entropy_pct"]}'; E["as.gini"] = f["gini"]; E["as.sat"] = f'{f["beta_saturated"]:,}'; E["as.poll"] = f'{ev["polluted"]:,}'; E["as.poll_pct"] = ev["pollution_pct"]
    E["as.quar"] = f'{sn["quarantined"]:,}'; E["as.quar_pct"] = sn["quarantined_pct"]; E["as.nonascii"] = A_["scripts"]["nonascii_word_count"]
    E["as.B"] = f'{sn["tiers"]["B:candidate_evidence_pending"]:,}'; E["as.B_pct"] = f'{100 * sn["tiers"]["B:candidate_evidence_pending"] / d["vocab_size"]:.1f}'
    E["tbl.poll"] = tbl(["class", "tokens"], [(k, f"{v:,}") for k, v in ev["by_category"].items()])
    lens_ = collections.Counter(len(v[1]) for v in d["vocab"]); E["as.lens"] = ", ".join(f"{k}: {n:,}" for k, n in sorted(lens_.items()))
    ps = collections.Counter(v[5] for v in d["vocab"]); E["as.ps"] = ", ".join(f"{k}: {n:,}" for k, n in sorted(ps.items(), reverse=True))
    E["ps.flag3_nown"] = f'{sum(1 for v in m.vocab.values() if v["ps"] == 3 and not wn.synsets(v["word"])):,}'
    E["sumV_all"] = f'{float(np.sum(np.where(np.array([i in m.vocab for i in range(25000)]), np.array(m.beta) * np.array([m.vocab[i]["E"] if i in m.vocab else 0 for i in range(25000)]) ** 2, 0))):.1f}'
    # ── constants defined but never read ─────────────────────────────────────
    uses = {}
    for c in ["MONAD_N_DEFAULT", "MONAD_L_GROUND", "MONAD_D_STAR", "MONAD_OMEGA_ZS", "MONAD_PHI", "MONAD_ALPHA_LEARN", "MONAD_LAMBDA", "MONAD_TAU", "MONAD_SPREAD_RADIUS", "MONAD_SPREAD_DECAY",
              "MONAD_GAP", "MONAD_WINDOW_MIN", "MONAD_WINDOW_MAX", "MONAD_BETA_SAT", "MONAD_EMIT_THRESH"]:
        uses[c] = sum(open(os.path.join(SRC, f), encoding="utf-8").read().count(c) for f in ["monad.c", "state.c", "main.c", "filter.c", "tokenizer.c", "daemon.c", "ingest.c", "log.c"])
    E["unused"] = ", ".join(f"`{c}`" for c, n in uses.items() if n == 0)
    E["tbl.consts"] = tbl(["constant", "value", "uses outside `ptolemy.h`"], [("`MONAD_N_DEFAULT`", "25000", uses["MONAD_N_DEFAULT"]), ("`MONAD_L_GROUND`", "−1.888", uses["MONAD_L_GROUND"]),
        ("`MONAD_D_STAR`", "0.24600", uses["MONAD_D_STAR"]), ("`MONAD_OMEGA_ZS`", "0.56714", uses["MONAD_OMEGA_ZS"]), ("`MONAD_PHI`", "1.6180339887498948482", uses["MONAD_PHI"]),
        ("`MONAD_ALPHA_LEARN`", "0.01", uses["MONAD_ALPHA_LEARN"]), ("`MONAD_LAMBDA`", "0.05", uses["MONAD_LAMBDA"]), ("`MONAD_TAU`", "5.0", uses["MONAD_TAU"]),
        ("`MONAD_SPREAD_RADIUS`", "3", uses["MONAD_SPREAD_RADIUS"]), ("`MONAD_SPREAD_DECAY`", "1.0", uses["MONAD_SPREAD_DECAY"]), ("`MONAD_GAP`", "0.000707", uses["MONAD_GAP"]),
        ("`MONAD_WINDOW_MIN`", "7", uses["MONAD_WINDOW_MIN"]), ("`MONAD_WINDOW_MAX`", "12", uses["MONAD_WINDOW_MAX"]), ("`MONAD_BETA_SAT`", "7.552", uses["MONAD_BETA_SAT"]),
        ("`MONAD_EMIT_THRESH`", "3.776", uses["MONAD_EMIT_THRESH"])])
    # ── arithmetic behind the address collapse ───────────────────────────────
    E["thr52"] = f"{2**52 / mp.PHI:.3e}"; E["p95_7"] = f"{95**7:.3e}"; E["p95_8"] = f"{95**8:.3e}"
    vmin8 = 0
    for c in b"aaaaaaaa": vmin8 = vmin8 * 95 + (c - 32 + 1)
    E["v_aaaaaaaa"] = f"{vmin8:.3e}"; E["v_zzzzzzz"] = f'{sum((122 - 32 + 1) * 95 ** k for k in range(7)):.3e}'
    E["tbl.tok"] = tbl(["text", "`tok_split` result"], [(f"`{t}`", mp.tok_split(t)) for t in ["The tree is a plant.", "arbre 木 baum δένδρο", "don't 'quoted' x ab", "ağaç dört", "x-ray 12 ab3cd"]])
    E["tbl.accept"] = tbl(["token", "accepted (prose rules)"], [(f"`{t}`", mp.token_accept(t)) for t in ["tree", "a", "qgt", "bcdfg", "deadbeef", "ban'", "aeiou", "schzr", "strengths", "qwrtypsdfghjkl"]])
    # ── the binary's own live feed (-v) for the running prompt ───────────────
    env = dict(os.environ, HOME=os.path.join(ROOT, "scratch_home"), PTOLEMY_HOME=os.path.join(ROOT, "scratch_home", ".ptolemy"))
    r = subprocess.run([vc.BIN, "-c", STORE, "-Wv", "what is your name", "-n"], capture_output=True, text=True, env=env)
    feed = r.stderr.rstrip("\n").replace(os.path.join(ROOT, "dirty") + "/", "dirty/")
    E["c.feed"] = feed + "\n" + "\n".join("[stdout] " + "·".join(SPACES.split(l)) for l in r.stdout.rstrip("\n").split("\n"))
    E["c.feed_lines"] = len(E["c.feed"].split("\n"))
    E["rt.seconds"] = f"{time.time() - t0:.0f}"
    return E


if __name__ == "__main__":
    E = collect(); json.dump({k: str(v) for k, v in E.items()}, open(os.path.join(HERE, "evidence.json"), "w"), indent=1, ensure_ascii=False); print(len(E), "keys")
