#!/usr/bin/env python3
"""english_speaking_wordnet.py — the last layer before an English TestMonad speaks: WordNet context for any list of English words.

Input is a list of English words in ANY order (the order the Chinese walk or the English walk happened to choose them). The layer
  1. senses    chooses one WordNet synset per word, jointly: a sense scores by how closely it relates to the senses of every OTHER word
               (path similarity, derivational links; frequency-weighted votes, then iterated on the chosen senses), plus a small prior for sense-frequency order;
  2. edges     lists the WordNet relations between the chosen senses (same synset, hypernym/hyponym, sister, antonym, derivation, part/member, similar);
  3. arrange   returns the words in one of three orders:  given (as chosen) · english (adjectives, noun, verb, noun, adverbs: a plain S V O clause) · chain
               (greedy walk along the strongest WordNet relation from the best-connected word), and frames the result as a sentence.
It is the original WordNet method (NLTK + Princeton WordNet 3.0), not the boxkite. Unknown words (no synset) keep their place and are marked.
Limits, stated: no determiners, no tense; the only inflection is third-person -s on a verb that follows a noun; senses are chosen by relatedness only,
so a short list gives weak context (nltk-zork-wordnet skill §4).

    PtolemyDesktop/.venv/bin/python english_speaking_wordnet.py [--order given|english|chain|all] word word ...
The system python3 crashes on `import nltk` (pandas ABI mismatch); use the PtolemyDesktop venv.
"""
import sys, itertools
from nltk.corpus import wordnet as wn

POSN = {"n": "noun", "v": "verb", "a": "adj", "s": "adj", "r": "adv"}


def _lemmas(word):
    w = word.lower().replace(" ", "_")
    return w


class EnglishWordNetLayer:
    def __init__(self, prior=0.05):
        wn.ensure_loaded()
        self.prior = prior

    # -- 1 senses ---------------------------------------------------------------------------------------------------------
    def candidates(self, word):
        return wn.synsets(_lemmas(word)) or [s for p in "nvar" for m in [wn.morphy(_lemmas(word), p)] if m for s in wn.synsets(m, p)]

    @staticmethod
    def sim(a, b):
        """Relatedness of two synsets in [0, 1]: path similarity within a POS, 0.5 for a derivational link across POS."""
        if a == b: return 1.0
        p = a.path_similarity(b) if a.pos() in "nv" and a.pos() == b.pos() else None
        if p: return p
        la = {l.synset() for x in a.lemmas() for l in x.derivationally_related_forms()}
        return 0.5 if b in la else 0.0

    def senses(self, words, passes=3):
        """Pass 1: each candidate sense is voted for by the other words' candidates, each weighted by 1/(1+rank) (WordNet lists senses by frequency).
        Later passes: the vote comes from the other words' CURRENTLY chosen senses (a joint, iterated choice). Stops early when nothing changes."""
        cand = [self.candidates(w) for w in words]; n = len(words)
        chosen = [None] * n
        for p in range(passes):
            new = []
            for i, c in enumerate(cand):
                if not c: new.append(None); continue
                best, bs = None, -1.0
                for rank, sy in enumerate(c):
                    if p == 0:
                        ctx = sum(max((self.sim(sy, t) / (1 + r) for r, t in enumerate(cand[j])), default=0.0) for j in range(n) if j != i)
                    else:
                        ctx = sum(self.sim(sy, chosen[j]) for j in range(n) if j != i and chosen[j] is not None)
                    score = ctx + self.prior / (1 + rank)
                    if score > bs: best, bs = sy, score
                new.append(best)
            if new == chosen: break
            chosen = new
        return chosen

    # -- 2 edges -----------------------------------------------------------------------------------------------------------
    @staticmethod
    def relations(a, b):
        r = []
        if a == b: return [("same_synset", 1.0)]
        if b in a.hypernyms() + a.instance_hypernyms(): r.append(("hypernym", 0.9))
        if a in b.hypernyms() + b.instance_hypernyms(): r.append(("hyponym", 0.9))
        if set(a.hypernyms()) & set(b.hypernyms()): r.append(("sister", 0.7))
        if any(x.antonyms() and b in [y.synset() for y in x.antonyms()] for x in a.lemmas()): r.append(("antonym", 0.8))
        if b in {l.synset() for x in a.lemmas() for l in x.derivationally_related_forms()}: r.append(("derivation", 0.8))
        if b in a.part_meronyms() + a.member_meronyms() + a.substance_meronyms(): r.append(("has_part", 0.6))
        if b in a.part_holonyms() + a.member_holonyms() + a.substance_holonyms(): r.append(("part_of", 0.6))
        if b in a.similar_tos() + a.also_sees() + a.entailments() + a.causes(): r.append(("similar/also/entails/causes", 0.6))
        if not r:
            p = EnglishWordNetLayer.sim(a, b)
            if p >= 0.1: r.append((f"path {p:.2f}", p * 0.5))
        return r

    def edges(self, words, chosen):
        out = []
        for i, j in itertools.combinations(range(len(words)), 2):
            if chosen[i] is None or chosen[j] is None: continue
            for name, w in self.relations(chosen[i], chosen[j]):
                out.append((words[i], words[j], name, w))
        return out

    # -- 3 arrange ---------------------------------------------------------------------------------------------------------
    @staticmethod
    def role(s):
        return "unk" if s is None else {"n": "N", "v": "V", "a": "A", "s": "A", "r": "R"}[s.pos()]

    def _strength(self, words, chosen):
        st = [0.0] * len(words)
        for a, b, _, w in self.edges(words, chosen):
            for k, x in enumerate(words):
                if x == a or x == b: st[k] += w
        return st

    def arrange(self, words, chosen, order):
        idx = list(range(len(words)))
        if order == "given": return idx
        roles = [self.role(s) for s in chosen]
        if order == "chain":
            st = self._strength(words, chosen); cur = max(idx, key=lambda k: (st[k], -k)); seq = [cur]; left = [k for k in idx if k != cur]
            while left:
                nxt = max(left, key=lambda k: (sum(w for _, w in self.relations(chosen[cur], chosen[k])) if chosen[cur] and chosen[k] else 0.0, -k))
                seq.append(nxt); left.remove(nxt); cur = nxt
            return seq
        if order == "english":                                   # [A* N] [V] [A* N] [R] [unknown]
            nouns = [k for k in idx if roles[k] == "N"]; verbs = [k for k in idx if roles[k] == "V"]
            adjs = [k for k in idx if roles[k] == "A"]; advs = [k for k in idx if roles[k] == "R"]; unk = [k for k in idx if roles[k] == "unk"]
            subj, obj = nouns[:1], nouns[1:]
            def with_adj(ns, pool):                              # each adjective sits before the first noun that follows it in the given order, else the last noun
                seq = []
                for n in ns:
                    mine = [a for a in pool if a < n]; pool[:] = [a for a in pool if a not in mine]; seq += mine + [n]
                return seq
            pool = list(adjs); seq = with_adj(subj, pool) + verbs + with_adj(obj, pool) + pool + advs + unk
            return seq if len(seq) == len(words) else idx
        raise ValueError(order)

    @staticmethod
    def third_person(v):
        if v.endswith(("s", "x", "z", "ch", "sh", "o")): return v + "es"
        if v.endswith("y") and v[-2:-1] not in "aeiou": return v[:-1] + "ies"
        return v + "s"

    def sentence(self, words, order="given"):
        chosen = self.senses(words); seq = self.arrange(words, chosen, order)
        surf, prev_noun = [], False
        for k in seq:
            w = words[k]; r = self.role(chosen[k])
            surf.append(self.third_person(w) if (r == "V" and prev_noun and order == "english") else w)
            prev_noun = r == "N"
        text = " ".join(surf)
        return dict(order=order, sentence=(text[:1].upper() + text[1:] + ".") if text else "",
                    senses=[(w, s.name() if s else None, s.definition() if s else None) for w, s in zip(words, chosen)],
                    edges=self.edges(words, chosen), sequence=[words[k] for k in seq])


def main(argv):
    order = "all"
    if "--order" in argv: i = argv.index("--order"); order = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    words = [a for a in argv if not a.startswith("--")]
    L = EnglishWordNetLayer(); r0 = L.sentence(words, "given")
    for w, n, d in r0["senses"]: print(f"  {w:14s} {n or '(no synset)':26s} {d or ''}")
    for a, b, n, w in r0["edges"]: print(f"  edge {a} — {b}: {n} {w:.2f}")
    for o in (["given", "english", "chain"] if order == "all" else [order]):
        print(f"  [{o:7s}] {L.sentence(words, o)['sentence']}")


if __name__ == "__main__":
    main(sys.argv[1:])
