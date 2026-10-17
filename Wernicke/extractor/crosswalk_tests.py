#!/usr/bin/env python3
"""crosswalk_tests.py — test the seven-role rule base (silk_map.py) against annotation that already exists.

    A  UD English-EWT (gold dependencies): does every token get a role? what is left over?
    B  PropBank (gold semantic roles) on the Penn Treebank sample, parsed by Stanza: do ARG labels land on the predicted role?
    C  WordNet's 35 verb frames and VerbNet's frame patterns: do they decompose into ANCHOR + SPAN(relation, claim, frame)?
    D  NLTK dialogue acts (nps_chat): does the SHELL act inventory cover them?
Run one:  python3 crosswalk_tests.py A|B|C|D      Output: a text report on stdout (CROSSWALK_REPORT.md collects them).
No orbweaver web, no A-edges: only the seven roles.
"""
import collections
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import silk_map as SM  # noqa: E402

NLP = os.path.expanduser("~/nlp_data")


def pct(a, b):
    return f"{100.0 * a / b:.1f}%" if b else "n/a"


def test_A(files=("en_ewt-ud-dev.conllu", "en_ewt-ud-test.conllu")):
    import conllu
    tok_n = covered = multi = 0
    unc = collections.Counter()
    roles = collections.Counter()
    sents = lacking_span = lacking_anchor = lacking_both = 0
    occupancy = collections.Counter()
    for fn in files:
        path = glob.glob(f"{NLP}/ud-english-ewt/**/{fn}", recursive=True)[0]
        with open(path) as f:
            for sent in conllu.parse_incr(f):
                sents += 1
                have = set()
                for tok in sent:
                    if not isinstance(tok["id"], int):
                        continue
                    rs = SM.roles_ud(tok, sent)
                    if ("PUNCT", None) in rs:
                        continue
                    tok_n += 1
                    bad = {r for r in rs if r[0] == "UNCOVERED"}
                    good = rs - bad
                    if good:
                        covered += 1
                    if len({r[0] for r in good}) > 1:
                        multi += 1
                    for r in bad:
                        unc[(r[1], tok["upos"])] += 1
                    for r in good:
                        roles[r[0] + ("." + r[1] if r[1] else "")] += 1
                        have.add(r[0])
                has_a, has_s = "ANCHOR" in have, "SPAN" in have
                lacking_anchor += not has_a
                lacking_span += not has_s
                lacking_both += (not has_a and not has_s)
                occupancy[len(have)] += 1
    print(f"A. UD English-EWT dev + test: {sents} sentences, {tok_n} non-punctuation tokens")
    print(f"   tokens given at least one role: {covered} ({pct(covered, tok_n)}); given more than one role: {multi} ({pct(multi, tok_n)})")
    print("   role.field counts: " + ", ".join(f"{k} {v}" for k, v in sorted(roles.items(), key=lambda kv: -kv[1])))
    print("   left over (deprel, upos) not covered by the seven: " + (", ".join(f"{k} x{v}" for k, v in unc.most_common(12)) or "none"))
    print(f"   sentences with no ANCHOR: {pct(lacking_anchor, sents)}; no SPAN: {pct(lacking_span, sents)}; neither: {pct(lacking_both, sents)}")
    print("   roles occupied per sentence: " + ", ".join(f"{k}: {pct(v, sents)}" for k, v in sorted(occupancy.items())))
    return {"sentences": sents, "tokens": tok_n, "covered": covered}


def _feats(fs):
    if not fs or fs == "_":
        return {}
    return dict(kv.split("=", 1) for kv in fs.split("|") if "=" in kv)


def test_B(max_sents=700):
    """PropBank on the Penn Treebank sample, parsed by Stanza from the gold tokens: do ARG labels land on the predicted roles?"""
    import random
    import stanza
    from nltk.corpus import propbank as pb, treebank as tb
    have = set(tb.fileids())
    by_sent = collections.defaultdict(list)
    for inst in pb.instances():
        if inst.fileid in have:
            by_sent[(inst.fileid, inst.sentnum)].append(inst)
    keys = sorted(by_sent)
    random.Random(20261017).shuffle(keys)
    keys = keys[:max_sents]
    nlp = stanza.Pipeline("en", processors="tokenize,pos,lemma,depparse", tokenize_pretokenized=True, use_gpu=False, verbose=False)
    cross = collections.defaultdict(collections.Counter)
    pred_roles = collections.Counter()
    agree = collections.Counter()
    skipped = 0
    for fileid, sn in keys:
        tree = tb.parsed_sents(fileid)[sn]
        leaves = tree.leaves()
        tags = [p for _, p in tree.pos()]
        idx = [i for i, t in enumerate(tags) if t != "-NONE-"]
        pos_of = {leaf: k for k, leaf in enumerate(idx)}
        words = [leaves[i] for i in idx]
        if not words:
            continue
        doc = nlp([words])
        sent = [{"id": w.id, "form": w.text, "lemma": w.lemma, "upos": w.upos, "head": w.head, "deprel": w.deprel, "feats": _feats(w.feats)} for w in doc.sentences[0].words]
        if len(sent) != len(words):
            skipped += 1
            continue
        leafpos = [tree.leaf_treeposition(i) for i in range(len(leaves))]

        def covered(ptr):
            pieces = getattr(ptr, "pieces", None)
            if pieces:
                out = set()
                for pc in pieces:
                    out |= covered(pc)
                return out
            tp = ptr.treepos(tree)
            return {i for i, lp in enumerate(leafpos) if lp[:len(tp)] == tp}

        for inst in by_sent[(fileid, sn)]:
            pw = inst.wordnum
            if pw in pos_of:
                rs = SM.roles_ud(sent[pos_of[pw]], sent)
                for r in rs:
                    pred_roles[r[0] + ("." + r[1] if r[1] else "")] += 1
            for ptr, label in inst.arguments:
                try:
                    cov = {pos_of[i] for i in covered(ptr) if i in pos_of}
                except Exception:                                    # noqa: BLE001
                    continue
                if not cov:
                    continue
                heads = [k for k in sorted(cov) if (sent[k]["head"] - 1) not in cov or sent[k]["head"] == 0]
                h = sent[heads[0] if heads else min(cov)]
                rs = {r[0] + ("." + r[1] if r[1] else "") for r in SM.roles_ud(h, sent) if r[0] not in ("PUNCT",)}
                lab = label.split("-")[0] if label.startswith("ARGM") and False else label
                for r in rs:
                    cross[lab][r] += 1
                exp = SM.PROPBANK_EXPECT.get(lab)
                if exp:
                    agree[(lab, exp in rs or exp.split(".")[0] in {x.split(".")[0] for x in rs} and "." not in exp)] += 1
    print(f"B. PropBank on the Penn Treebank sample, Stanza-parsed from gold tokens: {len(keys)} sentences sampled, {skipped} skipped (token mismatch)")
    print("   predicate (the verb) gets: " + ", ".join(f"{k} {v}" for k, v in pred_roles.most_common(5)))
    print("   argument label -> role of the argument's head token (top three), and whether the predicted role was among them:")
    for lab in sorted(cross, key=lambda k: -sum(cross[k].values())):
        tot = sum(cross[lab].values())
        if tot < 25:
            continue
        top = ", ".join(f"{k} {100 * v // tot}%" for k, v in cross[lab].most_common(3))
        exp = SM.PROPBANK_EXPECT.get(lab, "-")
        ok, no = agree[(lab, True)], agree[(lab, False)]
        print(f"     {lab:9s} n={tot:5d}  {top:62s} expected {exp:12s} hit {pct(ok, ok + no)}")


def test_F(files=("en_ewt-ud-train.conllu", "en_ewt-ud-dev.conllu", "en_ewt-ud-test.conllu")):
    """Closed classes: how many distinct lemmas fill SCAFFOLD, WRAP, the SPAN.frame marker (case) and SHELL, and how much of the text do the top N cover?"""
    import conllu
    classes = {"SCAFFOLD (aux, cop, expl)": ("aux", "cop", "expl"), "WRAP (mark, cc)": ("mark", "cc"), "SPAN.frame marker (case)": ("case",),
               "ELABORATE (amod, advmod)": ("amod", "advmod"), "ANCHOR givenness (det, nmod:poss)": ("det", "nmod:poss")}
    cnt = {k: collections.Counter() for k in classes}
    for fn in files:
        path = glob.glob(f"{NLP}/ud-english-ewt/**/{fn}", recursive=True)[0]
        with open(path) as f:
            for sent in conllu.parse_incr(f):
                for t in sent:
                    if not isinstance(t["id"], int):
                        continue
                    base = t["deprel"].split(":")[0] if t["deprel"] != "nmod:poss" else "nmod:poss"
                    for k, rels in classes.items():
                        if t["deprel"] in rels or base in rels:
                            cnt[k][(t["lemma"] or t["form"]).lower()] += 1
    print("F. closed-class test on UD English-EWT (train, dev, test): distinct lemmas per role-class and the share of its tokens the top N lemmas cover")
    for k, c in cnt.items():
        tot = sum(c.values())
        cum = lambda n: pct(sum(v for _, v in c.most_common(n)), tot)
        print(f"   {k:34s} tokens {tot:6d}, distinct lemmas {len(c):5d}; top 10 cover {cum(10)}, top 25 {cum(25)}, top 50 {cum(50)}, top 100 {cum(100)}; most common: {', '.join(w for w, _ in c.most_common(8))}")


def test_A2(files=("en_ewt-ud-train.conllu",)):
    """Is SPAN's frame independent of its claim in real text?  Per verb: has a claim (obj, iobj, ccomp, xcomp) / a frame (obl, advcl)?"""
    import math
    import conllu
    joint = collections.Counter()
    cop_clauses = verb_clauses = 0
    for fn in files:
        path = glob.glob(f"{NLP}/ud-english-ewt/**/{fn}", recursive=True)[0]
        with open(path) as f:
            for sent in conllu.parse_incr(f):
                kids = collections.defaultdict(list)
                for t in sent:
                    if isinstance(t["id"], int):
                        kids[t["head"]].append(t["deprel"])
                for t in sent:
                    if not isinstance(t["id"], int):
                        continue
                    ks = kids.get(t["id"], [])
                    if t["upos"] == "VERB" and not any(k.startswith("cop") for k in ks):
                        claim = any(SM.ud_base(k) in ("obj", "iobj", "ccomp", "xcomp") for k in ks)
                        frame = any(SM.ud_base(k) in ("obl", "advcl") for k in ks)
                        joint[(claim, frame)] += 1
                        verb_clauses += 1
                    elif any(k == "cop" for k in ks):
                        cop_clauses += 1
    n11, n10, n01, n00 = joint[(True, True)], joint[(True, False)], joint[(False, True)], joint[(False, False)]
    tot = n11 + n10 + n01 + n00
    phi = (n11 * n00 - n10 * n01) / math.sqrt((n11 + n10) * (n01 + n00) * (n11 + n01) * (n10 + n00))
    print(f"A2. UD English-EWT train, real text: {verb_clauses} event-verb clauses and {cop_clauses} copular clauses ({pct(cop_clauses, cop_clauses + verb_clauses)} copular)")
    print(f"   SPAN fields claim x frame per event verb: both {n11}, claim only {n10}, frame only {n01}, neither {n00}; phi = {phi:+.3f} (0 = independent)")
    print(f"   P(claim) = {pct(n11 + n10, tot)}, P(frame) = {pct(n11 + n01, tot)}, P(both) = {pct(n11, tot)} vs the product {100.0 * (n11 + n10) / tot * (n11 + n01) / tot:.1f}%")


def test_C():
    import re
    fr = {}
    for line in open(f"{NLP}/wordnet-3.1/dict/verb.Framestext", encoding="latin-1"):
        n, txt = line.strip().split(None, 1)
        fr[int(n)] = txt
    pat = collections.Counter()
    for n, t in fr.items():
        subject = "ANCHOR" if re.match(r"^(Somebody|Something|It|Somebody's)", t) else "?"
        parts = []
        t2 = re.sub(r"^(Somebody's \(body part\)|Somebody|Something|It( is)?)\s+(----s|----ing)", "V", t)
        t2 = t2.replace("----s", "V").replace("----ing", "V")
        for w in t2.split():
            if w == "V":
                parts.append("relation")
            elif w in ("somebody", "something", "Adjective/Noun", "Adjective", "that", "CLAUSE", "INFINITIVE", "to", "VERB-ing", "V-ing", "whether", "into", "on", "from", "with", "of"):
                parts.append("claim" if w in ("somebody", "something", "Adjective/Noun", "Adjective", "CLAUSE", "INFINITIVE", "VERB-ing", "V-ing") else "(marker)")
            elif w == "PP":
                parts.append("frame")
        pat[subject + " + " + ", ".join(dict.fromkeys(parts))] += 1
    unmapped = [t for n, t in fr.items() if not re.match(r"^(Somebody|Something|It|Somebody's)", t)]
    print(f"C. WordNet 3.1 verb frames: {len(fr)} generic frames; all open with a subject (ANCHOR): {len(fr) - len(unmapped)}; others: {unmapped}")
    print("   slot patterns (ANCHOR + SPAN fields) and how many frames have each:")
    for k, v in pat.most_common():
        print(f"     {v:2d}  {k}")
    import math
    from nltk.corpus import verbnet as vn
    elems = collections.Counter()
    roles_pre = collections.Counter()
    shape = collections.Counter()
    nclaim = collections.Counter()
    nframe = collections.Counter()
    joint = collections.Counter()
    nf = 0
    for cid in vn.classids():
        for fm in vn.frames(cid):
            nf += 1
            syn = fm["syntax"]
            for e in syn:
                elems[e["pos_tag"]] += 1
            vi = next((i for i, e in enumerate(syn) if e["pos_tag"] == "VERB"), None)
            if vi is None:
                continue
            pre = [e for e in syn[:vi] if e["pos_tag"] == "NP"]
            for e in pre[:1]:
                roles_pre[(e.get("modifiers") or {}).get("value", "?")] += 1
            post = syn[vi + 1:]
            claims = frames = 0
            i = 0
            while i < len(post):
                e = post[i]
                if e["pos_tag"] == "PREP":
                    frames += 1
                    if i + 1 < len(post) and post[i + 1]["pos_tag"] == "NP":
                        i += 1                       # the NP belongs to the PP
                elif e["pos_tag"] in ("NP", "ADJ"):
                    claims += 1
                elif e["pos_tag"] == "ADV":
                    frames += 1
                i += 1
            shape[("pre-verbal NP" if pre else "no pre-verbal NP")] += 1
            nclaim[min(claims, 3)] += 1
            nframe[min(frames, 3)] += 1
            joint[(claims > 0, frames > 0)] += 1
    n11, n10, n01, n00 = joint[(True, True)], joint[(True, False)], joint[(False, True)], joint[(False, False)]
    tot = n11 + n10 + n01 + n00
    phi = (n11 * n00 - n10 * n01) / math.sqrt((n11 + n10) * (n01 + n00) * (n11 + n01) * (n10 + n00)) if tot else 0.0
    print(f"   VerbNet {len(vn.classids())} classes, {nf} frames. Syntax elements in all frames: " + ", ".join(f"{k} {v}" for k, v in elems.most_common()))
    print("   every element is one the roles can hold: NP (ANCHOR or claim), VERB (relation), PREP+NP (frame), ADJ (claim), ADV (frame), LEX (fixed words)")
    print("   frames with a pre-verbal NP (ANCHOR): " + pct(shape['pre-verbal NP'], nf) + "; thematic roles of that NP: " + ", ".join(f"{k} {v}" for k, v in roles_pre.most_common(8)))
    print("   post-verbal claims per frame (0,1,2,3+): " + ", ".join(f"{k}: {v}" for k, v in sorted(nclaim.items())) + "; frames (PP or ADV) per frame: " + ", ".join(f"{k}: {v}" for k, v in sorted(nframe.items())))
    print(f"   SPAN fields claim x frame across VerbNet frames: both {n11}, claim only {n10}, frame only {n01}, neither {n00}; phi = {phi:+.3f} (0 = independent)")


def test_D():
    from nltk.corpus import nps_chat
    cnt = collections.Counter(p.attrib["class"] for p in nps_chat.xml_posts())
    miss = [c for c in cnt if c not in SM.NPS_TO_SHELL]
    print(f"D. nps_chat: {sum(cnt.values())} posts in {len(cnt)} dialogue acts; acts with no SHELL.act mapping: {miss or 'none'}")
    print("   act counts: " + ", ".join(f"{k} {v}" for k, v in cnt.most_common()))
    mine = {"whQuestion", "ynQuestion", "statement", "imperative", "greet", "thanks", "other"}
    need = set(SM.NPS_TO_SHELL.values())
    print(f"   SHELL.act values the corpus needs: {sorted(need)}")
    print(f"   values in my hand-made answers but absent from nps_chat: {sorted(mine - need)}; in nps_chat but absent from my answers: {sorted(need - mine)}")


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "A"
    {"A": test_A, "A2": test_A2, "B": test_B, "F": test_F, "C": test_C, "D": test_D}[which]()
