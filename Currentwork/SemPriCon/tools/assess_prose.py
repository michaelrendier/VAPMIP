#!/usr/bin/env python3
"""assess_prose.py — grade a PTOL state file's vocabulary as 'prose words', in whatever language it turns out to hold.  Read-only.

The question: is every vocabulary entry a prose word of its own language, and nothing else?  The test is chosen AFTER the language is explored,
not before, and every threshold is read from that language's own dictionary (the Wiktionary extract corpora/derived/lex_<Language>.tsv), never assumed.

    1 EXPLORE   script census of the vocabulary; unit type (logographic = single Han code points; alphabetic = everything else);
                language = plurality of a per-word character-trigram attribution (models trained on each dictionary's own words; dictionary coverage is reported but is not the vote, because the dictionaries differ 40-fold in size);
                from that dictionary's own word entries: letter inventory, vowel-bearing share, longest consonant run, longest identical-letter run.
    2 CHOOSE    a shape test applies only if >= 99.5 % of that language's dictionary words pass it (so it is valid for the language).
    3 GRADE     per entry: PROSE:dict (a word entry), PROSE:name (proper noun only), UNLISTED (well-formed, absent from the dictionary),
                NONPROSE:<why> (fails an applicable shape test, or the dictionary lists it only as affix / symbol / punctuation / letter).

    python3 assess_prose.py <file.bin> <out.json> [out.md]
"""
import collections, json, os, sys, csv, unicodedata as ud

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, ".."))
DER = os.path.join(ROOT, "corpora", "derived")
sys.path.insert(0, HERE)
import ptol_bin
csv.field_size_limit(10 ** 9)
LANGS = ["English", "Chinese", "Finnish", "Indonesian"]
NONWORD = {"prefix", "suffix", "interfix", "infix", "circumfix", "symbol", "punct", "character", "soft-redirect", "root", "diacritic", "letter",
           "abbrev", "initialism", "acronym", "name", "num_sign"}
VOWEL_BASE = set("aeiouy")


def is_han(ch):
    c = ord(ch)
    return 0x3400 <= c <= 0x4DBF or 0x4E00 <= c <= 0x9FFF or 0x20000 <= c <= 0x323AF or 0xF900 <= c <= 0xFAFF or 0x2E80 <= c <= 0x2FDF


def base_letter(ch):
    d = ud.normalize("NFD", ch)
    return d[0] if d else ch


def load_lex(lang):
    """key -> (set of pos tokens, any is_form)"""
    out = {}
    with open(os.path.join(DER, f"lex_{lang}.tsv"), encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            k = ud.normalize("NFC", r["key"]).lower()
            p = set(r["pos"].split("/"))
            if k in out:
                out[k][0].update(p); out[k][1] = out[k][1] and r["is_form"] == "1"
            else:
                out[k] = [p, r["is_form"] == "1"]
    return out


def classify_pos(pos):
    if pos - NONWORD:
        return "word"
    if pos == {"name"}:
        return "name"
    if pos & {"character"} and pos <= {"character", "soft-redirect"}:
        return "character"
    return "nonword"


def run_len(s, pred):
    best = cur = 0
    for ch in s:
        cur = cur + 1 if pred(ch) else 0
        best = max(best, cur)
    return best


def same_run(s):
    best = cur = 1 if s else 0
    for a, b in zip(s, s[1:]):
        cur = cur + 1 if a == b else 1
        best = max(best, cur)
    return best


def trigram_model(keys, cap=27000):
    import random, math
    rnd = random.Random(7); keys = sorted(keys); rnd.shuffle(keys); keys = keys[:cap]
    cnt = collections.Counter(); ctx = collections.Counter()
    for k in keys:
        t = "^^" + k + "$"
        for i in range(len(t) - 2):
            cnt[t[i:i + 3]] += 1; ctx[t[i:i + 2]] += 1
    V = len({t[2] for t in cnt}) + 1
    return cnt, ctx, V


def trigram_score(model, w):
    import math
    cnt, ctx, V = model; t = "^^" + w + "$"; lp = 0.0
    for i in range(len(t) - 2):
        lp += math.log((cnt.get(t[i:i + 3], 0) + 0.05) / (ctx.get(t[i:i + 2], 0) + 0.05 * V))
    return lp / (len(t) - 2)


TEXT = {"English": "en", "Finnish": "fi", "Indonesian": "id", "Chinese": "zh"}
TOK = None


def case_census(lang, want):
    """For each wanted word: [lowercase occurrences, capitalised occurrences NOT at sentence start, capitalised at sentence start].
    Capitalisation in running text is how prose separates a proper noun from a common word when the dictionary is silent."""
    import re
    tok = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*"); sent = re.compile(r"(?<=[.!?])\s+")
    cnt = {w: [0, 0, 0] for w in want}
    path = os.path.join(ROOT, "corpora", "text", f"{TEXT[lang]}_v1.txt")
    with open(path, encoding="utf-8") as f:
        for line in f:
            for st in sent.split(line):
                for i, m in enumerate(tok.finditer(st)):
                    t = m.group(0); lo = ud.normalize("NFC", t).lower(); c = cnt.get(lo)
                    if c is None: continue
                    if t == t.lower(): c[0] += 1
                    elif t[0].isupper() and t[1:] == t[1:].lower(): c[2 if i == 0 else 1] += 1
    return cnt


def pct(sorted_vals, q):
    return sorted_vals[min(len(sorted_vals) - 1, int(q * len(sorted_vals)))]


def main(path, out_json, out_md=None):
    d = ptol_bin.load(path, with_edges=False) if "with_edges" in ptol_bin.load.__code__.co_varnames else ptol_bin.load(path)
    words = [ud.normalize("NFC", v[1]).lower() for v in d["vocab"]]
    n = len(words)

    # ── 1 EXPLORE ────────────────────────────────────────────────────────────
    script = collections.Counter()
    for w in words:
        sc = set()
        for ch in w:
            if is_han(ch): sc.add("HAN")
            elif ch.isascii(): sc.add("ASCII-letter" if ch.isalpha() else "ASCII-other")
            else:
                try: sc.add(ud.name(ch).split(" ")[0])
                except ValueError: sc.add("UNNAMED")
        script["+".join(sorted(sc))] += 1
    single_han = sum(1 for w in words if len(w) == 1 and is_han(w))
    unit = "logographic" if single_han / n >= 0.95 else "alphabetic"

    lex = {}; cover = {}
    for L_ in LANGS:
        lex[L_] = load_lex(L_)
        cover[L_] = round(100 * sum(1 for w in words if w in lex[L_]) / n, 2)
    def wordlike(k): return all(c.isalpha() or c in "'’-" for c in k) and any(c.isalpha() for c in k)
    attrib = {}; vote = collections.Counter(); models = {}
    if unit == "logographic":
        chosen = "Chinese"; margin = None
    else:
        for L_ in ("English", "Finnish", "Indonesian"):
            models[L_] = trigram_model([k for k, (p, f) in lex[L_].items() if classify_pos(p) == "word" and wordlike(k) and not any(is_han(c) for c in k)])
        for w in words:
            if wordlike(w):
                sc = {L_: trigram_score(m, w) for L_, m in models.items()}
                attrib[w] = max(sc, key=sc.get); vote[attrib[w]] += 1
        chosen = vote.most_common(1)[0][0]; tot = sum(vote.values())
        margin = round(100 * (vote.most_common(1)[0][1] - (vote.most_common(2)[1][1] if len(vote) > 1 else 0)) / tot, 2)
    ordered = [0, 0]
    L = lex[chosen]

    # dictionary profile from the chosen language's own word entries (alphabetic units only)
    prof = {}; applicable = {}
    if unit == "alphabetic":
        def wordlike(k): return all(c.isalpha() or c in "'’-" for c in k) and any(c.isalpha() for c in k)
        dw = [k for k, (p, f) in L.items() if classify_pos(p) == "word" and wordlike(k) and not any(is_han(c) for c in k)]
        letters = collections.Counter(c for k in dw for c in k if c.isalpha())
        tot = sum(letters.values()); inv = set(); acc = 0
        for c, m in letters.most_common():
            inv.add(c); acc += m
            if acc / tot >= 0.99995: break
        inv |= set("'’-")
        letter_set = set(letters)
        vowel = {c for c in letter_set if base_letter(c) in VOWEL_BASE}
        conlens = sorted(run_len(k, lambda ch: ch.isalpha() and ch not in vowel) for k in dw)
        replens = sorted(same_run(k) for k in dw)
        pass_inv = sum(all(c in inv for c in k) for k in dw) / len(dw)
        pass_vow = sum(any(c in vowel for c in k) for k in dw) / len(dw)
        con_lim = pct(conlens, 0.999); rep_lim = pct(replens, 0.999)
        pass_con = sum(c <= con_lim for c in conlens) / len(dw); pass_rep = sum(r <= rep_lim for r in replens) / len(dw)
        prof = dict(dictionary_word_entries=len(dw), letters_in_inventory=len(inv), vowels=sorted(vowel), consonant_run_limit=con_lim,
                    identical_run_limit=rep_lim, dictionary_pass=dict(inventory=round(pass_inv, 5), vowel=round(pass_vow, 5),
                    consonant_run=round(pass_con, 5), identical_run=round(pass_rep, 5)))
        applicable = {"inventory": pass_inv >= 0.995, "vowel": pass_vow >= 0.995, "consonant_run": pass_con >= 0.995, "identical_run": pass_rep >= 0.995}
        shape_fail = lambda w: ([] if not any(ch.isdigit() for ch in w) else ["digit"]) + \
            ([] if not applicable["inventory"] or all(c in inv for c in w) else ["inventory"]) + \
            ([] if not applicable["vowel"] or any(c in vowel for c in w) else ["no-vowel"]) + \
            ([] if not applicable["consonant_run"] or run_len(w, lambda ch: ch.isalpha() and ch not in vowel) <= con_lim else ["consonant-run"]) + \
            ([] if not applicable["identical_run"] or same_run(w) <= rep_lim else ["identical-run"])
    else:
        prof = dict(note="logographic: one Han code point per entry; shape tests that count letters do not apply")
        shape_fail = lambda w: ([] if len(w) == 1 and is_han(w) and ud.category(w) == "Lo" else ["not-single-Han-Lo"])

    # ── 3 GRADE ──────────────────────────────────────────────────────────────
    unl = [w for w in words if w not in L and not shape_fail(w)] if unit == "alphabetic" else []
    census = case_census(chosen, set(unl)) if unl else {}
    grade = collections.Counter(); samples = collections.defaultdict(list); forms = 0
    for w in words:
        bad = shape_fail(w)
        if bad:
            g = "NONPROSE:shape:" + "+".join(bad)
        elif w in L:
            c = classify_pos(L[w][0])
            if c == "word": g = "PROSE:dict"; forms += L[w][1]
            elif c == "character" and unit == "logographic": g = "PROSE:dict"
            elif c == "name": g = "PROSE:name"
            else: g = "NONPROSE:dict-" + "+".join(sorted(L[w][0]))[:40]
        else:
            other = [x for x in lex if x != chosen and w in lex[x] and classify_pos(lex[x][w][0]) == "word"] if unit == "alphabetic" else []
            a = attrib.get(w, chosen)
            if other and a != chosen: g = "NONPROSE:foreign-" + a
            else:
                lo, cap, init = census.get(w, [0, 0, 0])
                if cap >= 2 and cap >= 4 * lo: g = "UNLISTED:name-like(capitalised mid-sentence)"
                elif a != chosen: g = "UNLISTED:foreign-looking-" + a
                elif lo >= 3: g = "PROSE:attested(lowercase x3+ in corpus, dictionary silent)"
                else: g = "UNLISTED:native-looking, rare"
        grade[g] += 1
        if len(samples[g]) < 40: samples[g].append(w)
    prose = sum(m for g, m in grade.items() if g.startswith("PROSE")); non = sum(m for g, m in grade.items() if g.startswith("NONPROSE"))
    rep = dict(file=os.path.basename(path), vocab=n, unit=unit,
               explore=dict(script_census=dict(script.most_common()), dictionary_coverage_pct=cover, trigram_vote=dict(vote), chosen_dictionary=chosen,
                            choice_margin_pct=margin, profile=prof, tests_applied=applicable or "logographic rule"),
               summary=dict(prose_confirmed=prose, prose_dict_words=grade.get("PROSE:dict", 0), prose_names=grade.get("PROSE:name", 0),
                            dict_entries_that_are_inflected_forms=forms, unlisted_well_formed=sum(m for g, m in grade.items() if g.startswith('UNLISTED')), nonprose=non,
                            prose_confirmed_pct=round(100 * prose / n, 2), unlisted_pct=round(100 * sum(m for g, m in grade.items() if g.startswith('UNLISTED')) / n, 2),
                            nonprose_pct=round(100 * non / n, 2)),
               grades=dict(grade.most_common()), samples=samples)
    json.dump(rep, open(out_json, "w"), indent=1, ensure_ascii=False)
    s = rep["summary"]
    print(f"{rep['file']}: {unit}; language={chosen} (vote {dict(vote)}, cover {cover}); prose {s['prose_confirmed_pct']}%  unlisted {s['unlisted_pct']}%  nonprose {s['nonprose_pct']}%")
    if out_md:
        md = [f"# Prose-word assessment — `{rep['file']}`", "",
              f"- vocabulary {n:,}; unit type **{unit}**; language/dictionary chosen by trigram vote: **{chosen}** (coverage % by dictionary: {cover}; trigram vote {dict(vote)}; margin {margin} points)",
              f"- scripts: {dict(script.most_common(6))}", f"- dictionary profile: {json.dumps(prof, ensure_ascii=False)}",
              f"- shape tests applied (valid for ≥ 99.5 % of the dictionary's own words): {rep['explore']['tests_applied']}", "",
              "| grade | entries | % |", "|---|---:|---:|"]
        md += [f"| {g} | {m:,} | {100*m/n:.2f} |" for g, m in grade.most_common()]
        md += ["", "## Samples", ""] + [f"- **{g}**: {' '.join(v[:40])}" for g, v in samples.items()]
        open(out_md, "w", encoding="utf-8").write("\n".join(md) + "\n")


if __name__ == "__main__":
    main(*sys.argv[1:4])
