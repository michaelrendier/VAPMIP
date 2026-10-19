#!/usr/bin/env python3
"""verify_unicode_against_c.py — the Unicode build's binary against its port: learned state (multilingual texts) and replies (-W) from a learned store."""
import os, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ptol_bin, monad_pyu as mu
ROOT = os.path.abspath(os.path.join(HERE, ".."))
BIN = os.path.join(ROOT, "build", "PtolC_unicode", "ptolemy")
SC = os.path.join(ROOT, "scratch_home", ".ptolemy")
ENV = dict(os.environ, PTOLEMY_HOME=SC, HOME=os.path.join(ROOT, "scratch_home"))
TEXTS = {
 "finnish":    "Puu on kasvi. Epäjärjestelmällisyys on pitkä sana. Vesi on neste, jota puu juo. Ääni kuuluu kauas.",
 "mandarin":   "树是一种植物。水是一种液体。树喝水。我们喝水。你叫什么名字？我是一个人！",
 "swahili":    "Mti ni mmea. Maji ni kimiminika ambacho mti hunywa. Jina lako nani? Ninaitwa Juma.",
 "indonesian": "Pohon adalah tumbuhan. Air adalah cairan yang diminum pohon. Siapa namamu? Namaku Budi.",
 "quechua":    "Sach'a hatun yurakmi. Yaku ukhu yakum. Imam sutiyki? Sutiyqa Pidru.",
 "english-us": "The color of the tree is green. I realize the center of the program is gray.",
 "english-uk": "The colour of the tree is green. I realise the centre of the programme is grey.",
 "mixed":      "Tree puu 树 mti pohon sach'a. Don’t stop — it’s ‘fine’… really‽ Café naïve ÉCOLE İstanbul Ünlü.",
}
def c_state(text):
    p = os.path.join(SC, "ul.bin"); ptol_bin.write_ground(p, version=5)
    subprocess.run([BIN, "-c", p, "-l", text], capture_output=True, text=True, env=ENV)
    return p, ptol_bin.load(p)
def compare(text):
    p, c = c_state(text); m = mu.Monad(); m.learn_ex(text)
    cv = {i: (w, E, ps) for i, w, E, hs, gs, ps in c["vocab"]}; pv = {i: (v["word"], v["E"], v["ps"]) for i, v in m.vocab.items()}
    ce = {(int(a), int(b)): float(w) for a, b, w in zip(c["edges"]["i"], c["edges"]["j"], c["edges"]["w"])}; pe = m._A_dict()
    return dict(vocab_equal=cv == pv, n=(len(cv), len(pv)), edges=(len(ce), len(pe)), keys_equal=set(ce) == set(pe),
                max_rel_edge_err=max([abs(ce[k] - pe.get(k, 0.0)) / max(ce[k], 1e-300) for k in ce] + [0.0]),
                max_beta_err=float(np.max(np.abs(np.array(m.beta) - c["beta"]))), wc=(c["word_count"], m.word_count))
def reply(path, prompt):
    r = subprocess.run([BIN, "-c", path, "-W", prompt, "-n"], capture_output=True, text=True, env=ENV); return r.stdout.rstrip("\n")
if __name__ == "__main__":
    ok = True
    for k, t in TEXTS.items():
        r = compare(t); good = r["vocab_equal"] and r["keys_equal"] and r["max_rel_edge_err"] == 0.0 and r["max_beta_err"] == 0.0 and r["wc"][0] == r["wc"][1]
        ok &= good; print("OK  " if good else "DIFF", k, r)
    allt = " ".join(TEXTS.values()); p, c = c_state(allt)
    for prompt in ["puu on kasvi", "树是什么", "mti ni nini", "pohon dan air", "sach'a", "the colour of the tree", "what is your name"]:
        m = mu.Monad.from_bin(p); a = reply(p, prompt); b = m.speak_wick(prompt, 50)
        ok &= (a == b); print("OK  " if a == b else "DIFF", repr(prompt), repr(a), "" if a == b else repr(b))
    print("ALL OK" if ok else "FAILURES")
