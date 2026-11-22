#!/usr/bin/env python3
"""build_bins.py — build NEW sanitised monad_mathematics.bin / monad_physics.bin from the PTorrent corpus URL lists.
fetch (PTorrent's own GenericCorpus._fetch_text: MediaWiki extracts API for Wikipedia, robots-checked HTML strip otherwise, Mozilla UA)
 -> cache raw text in PTorrent/corpus_text/<kind>/ (local, gitignored) -> Prose (pure @staticmethod rules: drop reference sections,
 sentence prose test, token sanitiser from sanitize_v0) -> runs of kept words -> Engine.crank.learn(run, weight) -> save_session.
Usage: build_bins.py maths|physics|both [--limit N] [--offline]"""
import json, os, re, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
PT = os.environ.get("PTORRENT", "/home/rendier/Projects/ThePlace/PTorrent")
PYDIR = f"{PT}/android/PtolemySeeder/app/src/main/python"
ASSETS = f"{PT}/android/PtolemySeeder/app/src/main/assets"
sys.path.insert(0, PYDIR)
import sanitize_v0 as S
import monad
from skills.corpus import GenericCorpus, parse_corpus_txt

KINDS = {
    "maths": dict(txt=f"{ASSETS}/mathematics_corpus.txt", bin=f"{PT}/bin_archive/clean/monad_mathematics.bin",
                  primary={"NUMBERTHEORY", "RIEMANN", "SPECTRAL", "MODULAR", "PRIMES", "CLAY", "HARMONIC"}),
    "physics": dict(txt=f"{ASSETS}/physics_corpus.txt", bin=f"{PT}/bin_archive/clean/monad_physics.bin",
                    primary={"FOUNDATIONS", "WAVES", "RESONANCE", "QM", "GR", "COSMOLOGY", "DARKMATTER", "YANGMILLS", "SPECTRAL"}),
}
HEADING = re.compile(r"^\s*(=+)\s*(.*?)\s*=+\s*$")
DROP_SECTIONS = {"references", "external links", "further reading", "bibliography", "notes", "see also", "sources", "citations",
                 "footnotes", "explanatory notes", "general references", "inline citations"}
KEEP = {"A", "B", "C", "F"}


class Prose:
    """Pure @staticmethod rules, no state."""

    @staticmethod
    def drop_sections(text):
        out, skipping, level = [], False, 0
        for line in text.splitlines():
            m = HEADING.match(line)
            if m:
                lv, title = len(m.group(1)), m.group(2).lower()
                if title in DROP_SECTIONS:
                    skipping, level = True, lv
                    continue
                if skipping and lv <= level:
                    skipping = False
                continue                                    # headings themselves are not sentences
            if not skipping:
                out.append(line)
        return "\n".join(out)

    @staticmethod
    def sentences(text):
        for para in text.splitlines():
            for s in re.split(r"(?<=[.!?])\s+(?=[A-Z\"“(])", para.strip()):
                if s:
                    yield s

    @staticmethod
    def verdicts(sentence):
        toks = [t.strip(".,;:()[]{}\"“”‘’?!*†‡") for t in sentence.split()]
        toks = [t for t in toks if t]
        return [(t,) + S.sanitize_token(t)[:2] for t in toks]

    @staticmethod
    def is_prose(vs):
        n = len(vs)
        if n < 5:
            return False
        kept = sum(1 for _, tier, _ in vs if tier in KEEP)
        func = sum(1 for _, tier, _ in vs if tier == "F")
        bad = sum(1 for _, tier, why in vs if tier == "Q" and why not in ("number", "time_expression"))
        return kept >= 5 and func / n >= 0.15 and bad / n <= 0.40

    @staticmethod
    def runs(vs):
        run = []
        for t, tier, _ in vs:
            if tier in KEEP:
                run.append(t.lower().replace("’", "'"))
            else:
                if len(run) >= 2:
                    yield " ".join(run)
                run = []
        if len(run) >= 2:
            yield " ".join(run)

    @staticmethod
    def clean(text):
        for s in Prose.sentences(Prose.drop_sections(text)):
            vs = Prose.verdicts(s)
            if Prose.is_prose(vs):
                yield from Prose.runs(vs)


def slug(url):
    return re.sub(r"[^A-Za-z0-9]+", "_", url.split("//", 1)[-1])[:80]


def build(kind, limit=None, offline=False):
    cfg = KINDS[kind]
    cache = f"{PT}/corpus_text/{kind}"
    os.makedirs(cache, exist_ok=True)
    corpus = parse_corpus_txt(cfg["txt"], cfg["primary"], 2.0, 1.0)[:limit]
    eng = monad.Engine()
    gc = GenericCorpus(monad.Engine(), cfg["txt"], "/nonexistent/x.bin", name=kind)
    log, words_total = [], 0
    for i, (tag, url, w) in enumerate(corpus):
        path = f"{cache}/{i:03d}_{tag}_{slug(url)}.txt"
        if os.path.exists(path):
            text = open(path, encoding="utf-8").read()
        elif offline:
            text = ""
        else:
            text = gc._fetch_text(url)
            time.sleep(1.0)
            if text:
                open(path, "w", encoding="utf-8").write(text)
        n_runs = n_words = 0
        for run in Prose.clean(text):
            n_words += eng.crank.learn(run, weight=w)
            n_runs += 1
        words_total += n_words
        log.append({"i": i, "tag": tag, "url": url, "weight": w, "chars": len(text), "runs": n_runs, "words": n_words})
        print(f"[{kind} {i+1}/{len(corpus)}] {tag:12} chars {len(text):7} runs {n_runs:5} words {n_words:6}  {url[:70]}", flush=True)
    res = eng.save_session(cfg["bin"])
    json.dump({"kind": kind, "bin": cfg["bin"], "saved": res, "pages": log, "words": words_total}, open(f"{HERE}/build_{kind}.json", "w"), indent=1)
    print("saved", res, "words learned", words_total, flush=True)


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    lim = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    if lim is not None:
        a = [x for x in a if x != str(lim)]
    for k in (["maths", "physics"] if (not a or a[0] == "both") else [a[0]]):
        build(k, lim, "--offline" in sys.argv)
