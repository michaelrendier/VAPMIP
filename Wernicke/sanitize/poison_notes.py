#!/usr/bin/env python3
"""poison_notes.py — measure a granular .bin with the sanitiser and write one POISON note per distinct bin (markdown).
Usage: poison_notes.py OUT_DIR BIN [BIN ...]     (BINs with identical sha256 share one note, copies listed)
The note states measurements only; where the cause is not established it says so."""
import collections, hashlib, os, pickle, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sanitize_v0 as S

CAUSE = {
    "mathematics": "Built from Wikipedia/MathWorld/DLMF pages by an HTML-strip path (corpus list code-corpora/mathematics_corpus.txt). Evidence: Wikipedia page chrome and the interlanguage list sit at the top of the fire counts; LaTeX source fragments and ISBN/DOI/bibcode strings are in the vocabulary. The old cleaner only deleted what looked non-English.",
    "physics": "Built from Wikipedia/HyperPhysics/Feynman Lectures pages by an HTML-strip path (corpus list code-corpora/physics_corpus.txt). Evidence: Wikipedia page chrome and the interlanguage list sit at the top of the fire counts; LaTeX fragments and ISBN/DOI/bibcode strings are in the vocabulary.",
    "war": "Fermat/Caesar war corpus (monad_war). Evidence: the top fire-count words are 'alexander', 'great', 'world', 'history', 'encyclopedia' followed by JSON-LD page metadata fragments (@context, streetaddress, publisher) from a World History Encyclopedia page, so a page's embedded structured data was ingested as prose. Small vocabulary, so the percentage is dominated by those fragments.",
    "sedenion": "Sedenion/Ainulindale corpus bin. Evidence: thousands of random-looking strings (azv, hosh, cricy, ekluo, zje), URL fragments (ftp://, https://www.jstor.org/...) and empty tokens. The e0..e15 basis names classify as FORMULA here and are legitimate vocabulary, not poison. Cause of the random strings not established.",
}


def measure(path):
    d = pickle.load(open(path, "rb"))
    words = [w for w in d["words"] if isinstance(w, str)]
    fc = d.get("fire_count") or []
    if len(fc) != len(d["words"]):
        fc = [-i for i in range(len(d["words"]))]        # no usable fire counts: first words in insertion order
    reasons, sample = collections.Counter(), collections.defaultdict(list)
    for w in words:
        t, why, _ = S.sanitize_token(w)
        reasons[(t, why)] += 1
        if len(sample[(t, why)]) < 8:
            sample[(t, why)].append(w)
    top = [d["words"][i] for i in sorted(range(len(d["words"])), key=lambda i: -fc[i])[:30]]
    return d, words, reasons, sample, top


def note(path, copies, sha, d, words, reasons, sample, top, name):
    n = len(words)
    q = sum(v for (t, _), v in reasons.items() if t == "Q")
    tiers = collections.Counter()
    for (t, _), v in reasons.items():
        tiers[t] += v
    kind = next((k for k in CAUSE if k in name), None)
    L = [f"# POISON NOTE: {name}", "",
         f"* file: `{os.path.basename(path)}`; identical copies: {', '.join('`'+c+'`' for c in copies) or 'none'}",
         f"* sha256: `{sha}`; size {os.path.getsize(path):,} bytes; pickle v{d.get('version')}; vocabulary {n:,}; word_count {d.get('word_count')}",
         f"* measured by `VAPMIP/Wernicke/sanitize/sanitize_v0.py` (deterministic ruleset), 2026-10-17",
         f"* quarantined by the sanitiser: **{q:,} of {n:,} ({100*q/n:.1f}%)**; admitted tiers A {tiers['A']:,} (in WordNet), B {tiers['B']:,} (candidates), C {tiers['C']:,} (proper nouns), F {tiers['F']:,} (function words)", "",
         "| tier:reason | tokens | examples |", "|---|---|---|"]
    for (t, why), v in sorted(reasons.items(), key=lambda x: -x[1]):
        ex = ", ".join(repr(x)[:24] for x in sample[(t, why)][:6]).replace("|", "/")
        L.append(f"| {t}:{why} | {v:,} | {ex} |")
    L += ["", "Top 30 words by fire count: " + ", ".join(repr(x)[:18] for x in top), ""]
    L.append("Cause: " + (CAUSE[kind] if kind else "not established; measured only. A code or specialist corpus can read as 'quarantined' here because its vocabulary is identifiers and symbols, which is a different thing from page-chrome poisoning."))
    L.append("")
    L.append("Status: moved to `PTorrent/bin_archive/dirty/` on 2026-10-17 (Cody's instruction); kept as a historical record, not a starting point. Bins are gitignored (too large for GitHub): this note is what is committed.")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    groups = collections.OrderedDict()
    for p in sys.argv[2:]:
        h = hashlib.sha256(open(p, "rb").read()).hexdigest()
        groups.setdefault(h, []).append(p)
    for h, ps in groups.items():
        ps.sort(key=lambda p: (os.path.basename(p).startswith(("holcus_", "phone_")), os.path.basename(p)))
        main = ps[0]
        name = os.path.basename(main)[:-4]
        d, words, reasons, sample, top = measure(main)
        txt = note(main, [os.path.basename(c) for c in ps[1:]], h, d, words, reasons, sample, top, name)
        open(os.path.join(out, name + ".POISON.md"), "w").write(txt)
        print(name, len(words), "->", name + ".POISON.md", [os.path.basename(c) for c in ps[1:]])
