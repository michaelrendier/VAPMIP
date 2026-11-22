#!/usr/bin/env python3
"""verify_learn_against_c.py — learn the same text with the C binary and with monad_py from the same ground state; compare the saved files."""
import os, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import monad_py as mp, ptol_bin
ROOT = os.path.abspath(os.path.join(HERE, ".."))
BIN = os.path.join(ROOT, "build", "PtolC_eb28ce8", "ptolemy")
SC = os.path.join(ROOT, "scratch_home", ".ptolemy")

def c_learn(text, ft="-l"):
    p = os.path.join(SC, "learn_t.bin"); ptol_bin.write_ground(p)
    env = dict(os.environ, PTOLEMY_HOME=SC, HOME=os.path.join(ROOT, "scratch_home"))
    subprocess.run([BIN, "-c", p, ft, text], capture_output=True, text=True, env=env)
    return ptol_bin.load(p)

def compare(text, ft="-l"):
    c = c_learn(text, ft); m = mp.Monad()
    m.learn_ex(text, mp.NS_FT_WORDNET if ft == "-L" else mp.NS_FT_PROSE)
    cv = {i: (w, E, ps) for i, w, E, hs, gs, ps in c["vocab"]}
    pv = {i: (v["word"], v["E"], v["ps"]) for i, v in m.vocab.items()}
    ce = {(int(a), int(b)): float(w) for a, b, w in zip(c["edges"]["i"], c["edges"]["j"], c["edges"]["w"])}
    pe = m._A_dict()
    dmax = max([abs(ce[k] - pe.get(k, 0.0)) / max(ce[k], 1e-300) for k in ce] + [0.0])
    db = float(np.max(np.abs(np.array(m.beta) - c["beta"])))
    return dict(vocab_equal=cv == pv, n_vocab=(len(cv), len(pv)), edges=(len(ce), len(pe)), edge_keys_equal=set(ce) == set(pe),
                max_rel_edge_err=dmax, max_abs_beta_err=db, word_count=(c["word_count"], m.word_count))

if __name__ == "__main__":
    for t in ["The tree is a plant. Water is a liquid that the tree drinks. Arbre means tree in French.",
              "I am Ptolemy. I am named after Ptolemy the Second, Philadelphos, who commissioned the Septuagint.",
              "Holcus is a genus of grasses; velvet grass, Yorkshire fog. Qgt xz bcdfg aeiou 12345 http://x.y/z tree tree tree."]:
        print(compare(t))
