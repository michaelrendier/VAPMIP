#!/usr/bin/env python3
"""en1_dict_pdf.py — slot dictionary of test_english_v1.0.bin as a PDF, plus its assessment.  Read-only on the bin and the corpus.

One table row per occupied slot: slot, E, β, the stored label, and every word that hashes there in order of first appearance in the corpus (word and count; the stored label in bold).
The word lists are rebuilt by a Python port of the engine's English path (ASCII-95 address, tokenizer, token_accept prose rules) and checked against the bin:
accepted tokens must equal the bin's word_count, the slot set must equal the bin's, and each stored label must be the highest-E member of its slot.

    .venv/bin/python tools/en1_dict_pdf.py <out.pdf>
"""
import collections, csv, json, os, random, re, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))
from dprint import dprint
import ptol_bin
import numpy as np
from xml.sax.saxutils import escape
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
from reportlab.platypus import SimpleDocTemplate, LongTable, Table, TableStyle, Paragraph, Spacer, PageBreak

M64 = (1 << 64) - 1; PHI = 0x9E3779B97F4A7C15; N = 25000; DSTAR = 0.24600; OMEGA = 0.56714
BIN = os.path.join(ROOT, "clean", "archive", "v1.0", "test_english_v1.0.bin")
ASSESS = os.path.join(ROOT, "clean", "archive", "v1.0", "assessment")
HEX = set("0123456789abcdefABCDEF")

def addr(w):
    v = 0
    for c in w: v = (v * 95 + (ord(c) - 31)) & M64
    if v > 0: v -= 1
    s = (v * PHI) & M64
    return (s * N) >> 64, DSTAR + (s >> 11) / 9007199254740992.0 * (OMEGA - DSTAR)

def reject_reason(t):
    """filter.c token_accept, prose rules, for tokens already >= 2 letters and not starting with an apostrophe"""
    n = len(t)
    if n > 24: return "longer than 24 characters"
    if n >= 3 and t[0] == "0" and t[1] in "xX": return "hex"
    if n >= 6 and all(c in HEX for c in t): return "hex-string gate (only a-f letters, 6 or more)"
    letters = sum(c != "'" for c in t); vc = sum(c in "aeiouy" for c in t if c != "'")
    if letters > 0:
        if vc == 0: return "no vowel"
        if n >= 6 and vc * 100 // n < 15: return "low vowel ratio (under 15 %, 6 or more)"
    if t[-1] == "'": return "trailing apostrophe"
    return None

# ── rebuild the corpus pass ──────────────────────────────────────────────────
txt = open(os.path.join(ROOT, "corpora", "text", "en_v1.txt"), encoding="utf-8").read()
order = collections.OrderedDict(); cnt = collections.Counter(); rej = collections.Counter(); rejn = collections.Counter(); rejtok = collections.defaultdict(collections.Counter)
lead = collections.Counter(); short = 0
for m in re.finditer(r"[A-Za-z']+", txt):
    t = m.group(0).lower()
    if len(t) < 2: short += 1; continue
    if t[0] == "'": lead[t] += 1; continue
    r = reject_reason(t)
    if r: rejn[r] += 1; rejtok[r][t] += 1; continue
    cnt[t] += 1
    if t not in order: order[t] = len(order)
dprint("accepted tokens", sum(cnt.values())); dprint("distinct accepted words", len(cnt))
slots = collections.defaultdict(list)
for t in order: slots[addr(t)[0]].append(t)
d = ptol_bin.load(BIN)
vocab = {i: (w, E) for i, w, E, *_ in d["vocab"]}
beta = d["beta"]
chk_wc = sum(cnt.values()) == d["word_count"]; chk_set = set(slots) == set(vocab)
chk_lab = sum(1 for s, ws in slots.items() if vocab[s][0] != max(ws, key=lambda w: addr(w)[1]))
dprint("check word_count", chk_wc); dprint("check slot set", chk_set); dprint("labels not highest-E", chk_lab)
assert chk_wc and chk_set and chk_lab == 0, "port does not reproduce the bin"
dom = {s: max(ws, key=lambda w: cnt[w]) for s, ws in slots.items()}
total = sum(cnt.values())

# ── PDF scaffolding ──────────────────────────────────────────────────────────
FD = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DV", FD + "DejaVuSans.ttf")); pdfmetrics.registerFont(TTFont("DV-B", FD + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DV-I", FD + "DejaVuSans-Oblique.ttf")); pdfmetrics.registerFont(TTFont("DV-BI", FD + "DejaVuSans-BoldOblique.ttf"))
pdfmetrics.registerFontFamily("DV", normal="DV", bold="DV-B", italic="DV-I", boldItalic="DV-BI")
ss = getSampleStyleSheet()
H1 = ParagraphStyle("h1", parent=ss["Heading1"], fontName="DV-B", fontSize=13, spaceAfter=4)
H2 = ParagraphStyle("h2", parent=ss["Heading2"], fontName="DV-B", fontSize=10, spaceBefore=8, spaceAfter=3)
BODY = ParagraphStyle("b", parent=ss["BodyText"], fontName="DV", fontSize=7, leading=9.2)
CELL = ParagraphStyle("c", fontName="DV", fontSize=5.2, leading=6.2)
CELLS = ParagraphStyle("cs", fontName="DV", fontSize=5.6, leading=6.8)
MONO = ParagraphStyle("m", fontName="Courier", fontSize=6.4, leading=7.6)
HDR = ParagraphStyle("hd", fontName="DV-B", fontSize=5.8, leading=7)
W = A4[0] - 2 * 30

def footer(c, doc):
    c.saveState(); c.setFont("DV", 6)
    c.drawString(30, 16, "SemPriCon_dict_english_v1.0 · test_english_v1.0.bin · slot dictionary")
    c.drawRightString(A4[0] - 30, 16, f"page {doc.page}"); c.restoreState()

def grid(rows, widths, head=True, size=6.2):
    data = [[Paragraph(escape(str(x)), HDR if (head and i == 0) else CELLS) for x in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1 if head else 0)
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.25, colors.grey), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("BACKGROUND", (0, 0), (-1, 0), colors.Color(.9, .9, .9) if head else colors.white),
                           ("LEFTPADDING", (0, 0), (-1, -1), 2), ("RIGHTPADDING", (0, 0), (-1, -1), 2), ("TOPPADDING", (0, 0), (-1, -1), 1), ("BOTTOMPADDING", (0, 0), (-1, -1), 1)]))
    return t

story = []
story.append(Paragraph("Slot dictionary — test_english_v1.0.bin", H1))
story.append(Paragraph(f"One row per occupied slot ({len(slots):,} of N = {N:,}). Words in order of first appearance in the corpus (first assigned … last assigned), each with its corpus count; "
                       "the word the bin shows as the slot label is in <b>bold</b>. E and β are read from the bin. The assessment follows the table.", BODY))
story.append(Spacer(1, 4))

# ── dictionary table ─────────────────────────────────────────────────────────
cw = [30, 33, 26, 70]; cw.append(W - sum(cw))
rows = [[Paragraph(x, HDR) for x in ("slot", "E", "β", "stored label", "words in order of first appearance (count)")]]
for s in sorted(slots):
    lab, E = vocab[s]
    ws = " ".join(("<b>%s</b>(%d)" if w == lab else "%s(%d)") % (escape(w), cnt[w]) for w in slots[s])
    rows.append([Paragraph(str(s), CELL), Paragraph("%.5f" % E, CELL), Paragraph("%.3f" % beta[s], CELL), Paragraph("<b>%s</b>" % escape(lab), CELL), Paragraph(ws, CELL)])
t = LongTable(rows, colWidths=cw, repeatRows=1)
t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.2, colors.grey), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("BACKGROUND", (0, 0), (-1, 0), colors.Color(.9, .9, .9)),
                       ("LEFTPADDING", (0, 0), (-1, -1), 2), ("RIGHTPADDING", (0, 0), (-1, -1), 2), ("TOPPADDING", (0, 0), (-1, -1), 0.6), ("BOTTOMPADDING", (0, 0), (-1, -1), 0.6)]))
story.append(t)
story.append(PageBreak())

# ── assessment ───────────────────────────────────────────────────────────────
A = json.load(open(os.path.join(ASSESS, "english_v1.0.json"), encoding="utf-8"))
story.append(Paragraph("Assessment of test_english_v1.0.bin", H1))
story.append(Paragraph("1 · The file and the port check", H2))
h = A["header"]
story.append(grid([["field", "value"], ["file", A["file"]], ["sha256", A["sha256"]], ["size", f'{A["size_bytes"]:,} bytes (all consumed)'],
                   ["state version / N", f'{h["version"]} / {h["N"]:,}'], ["vocab / A-edges", f'{h["vocab_size"]:,} / {h["A_size"]:,}'],
                   ["word_count (tokens the engine accepted)", f'{h["word_count"]:,}'],
                   ["port: accepted tokens", f"{total:,}  (equal to word_count: {chk_wc})"], ["port: distinct accepted words", f"{len(cnt):,}"],
                   ["port: slot set equals the bin's", f"{chk_set} ({len(slots):,} slots)"], ["port: stored labels that are not the highest-E member of their slot", chk_lab]],
                  [190, W - 190]))
story.append(Paragraph("Address: base-95 Horner over printable ASCII (rank = ord − 31, wrap mod 2⁶⁴, minus 1 when positive), × 0x9E3779B97F4A7C15 mod 2⁶⁴, slot = ⌊seed·N/2⁶⁴⌋, "
                       "E = d* + (seed ≫ 11)/2⁵³ · (Ω − d*), d* = 0.24600, Ω = 0.56714. The bin stores no σ per word.", BODY))

story.append(Paragraph("2 · What did not reach a slot (corpus tokens, counted by the port)", H2))
rr = [["rule", "tokens", "distinct", "most frequent examples"]]
rr.append(["a single letter (tokenizer, under 2 letters)", f"{short:,}", "—", "a, i, s, m …"])
rr.append(["starts with an apostrophe (tokenizer drops the whole token)", f"{sum(lead.values()):,}", f"{len(lead):,}", " ".join(f"{w}({c})" for w, c in lead.most_common(10))])
for r_, n_ in rejn.most_common():
    rr.append([r_, f"{n_:,}", f"{len(rejtok[r_]):,}", " ".join(f"{w}({c})" for w, c in rejtok[r_].most_common(10))])
story.append(grid(rr, [150, 40, 38, W - 228]))
story.append(Paragraph("The hex-string gate rejects ordinary words made only of the letters a–f (for example <i>facade, decade, defaced, effaced</i> when 6 letters or more). Listed above as counted.", BODY))

story.append(Paragraph("3 · Slot occupancy (distinct accepted words per slot)", H2))
occ = collections.Counter(len(ws) for ws in slots.values())
empty = [s for s in range(N) if s not in slots]
story.append(grid([["words in slot", "slots"]] + [[k, f"{occ[k]:,}"] for k in sorted(occ)], [70, 60]))
story.append(Paragraph(f"Slots with no word: {len(empty)} — {', '.join(map(str, empty))}. Largest slot: {max(len(w) for w in slots.values())} words. "
                       f"Mean words per occupied slot: {len(cnt) / len(slots):.2f}.", BODY))

story.append(Paragraph("4 · The stored label against the words that live in the slot", H2))
lab_dom = sum(1 for s in slots if vocab[s][0] == dom[s])
lab_mass = sum(cnt[vocab[s][0]] for s in slots); dom_mass = sum(cnt[dom[s]] for s in slots)
first_lab = sum(1 for s in slots if vocab[s][0] == slots[s][0])
story.append(grid([["measure", "value"],
                   ["slots whose label is the most frequent word of the slot", f"{lab_dom:,} of {len(slots):,} ({100 * lab_dom / len(slots):.1f} %)"],
                   ["slots whose label is the first word to appear", f"{first_lab:,} of {len(slots):,} ({100 * first_lab / len(slots):.1f} %)"],
                   ["share of all accepted tokens that belong to the label word", f"{100 * lab_mass / total:.1f} %"],
                   ["share of all accepted tokens that belong to the most frequent word of each slot", f"{100 * dom_mass / total:.1f} %"]], [330, W - 330]))
big = sorted(slots, key=lambda s: -sum(cnt[w] for w in slots[s]))[:10]
story.append(Paragraph("Ten heaviest slots by tokens: " + "; ".join(f"{s}: label {vocab[s][0]}, dominant {dom[s]}({cnt[dom[s]]:,}), {len(slots[s])} words" for s in big), BODY))
story.append(Paragraph("E range of occupied slots: %.5f – %.5f; E is determined by the slot (E = d* + (slot + fraction)·(Ω − d*)/N)." % (min(v[1] for v in vocab.values()), max(v[1] for v in vocab.values())), BODY))

story.append(Paragraph("5 · Existing assessments of this bin (archived, unchanged)", H2))
f = A["field"]
story.append(grid([["field measure", "value"], ["occupied zeros", f'{f["occupied_zeros"]:,}'], ["entropy / max", f'{f["entropy"]} / {f["entropy_max"]} ({f["entropy_pct"]} %)'],
                   ["gini of β", f["gini"]], ["β saturated", f'{f["beta_saturated"]} slots (β max {f["beta_max"]})'], ["eval_checkpoint polluted", f'{A["eval_checkpoint"]["polluted"]} ({A["eval_checkpoint"]["pollution_pct"]} %): {A["eval_checkpoint"]["by_category"]}'],
                   ["sanitiser tiers", A["sanitiser"]["tiers"]]], [110, W - 110]))
P = json.load(open(os.path.join(ASSESS, "english_v1.0_prose.json"), encoding="utf-8"))
pm = open(os.path.join(ASSESS, "english_v1.0_prose.md"), encoding="utf-8").read()
grade_rows = [["prose grade", "entries", "%"]]
for line in pm.splitlines():
    if line.startswith("| ") and not line.startswith("| grade") and not line.startswith("|---"):
        grade_rows.append([x.strip() for x in line.strip("|").split("|")])
story.append(grid(grade_rows, [260, 50, 40]))
story.append(Paragraph("Prose-word grader: dictionary = Wiktionary/kaikki English; language by trigram vote (English 18,244 words, Indonesian 4,574, Finnish 2,122 of 24,940 labels). "
                       "This grades the <b>stored labels</b>, which are not the dominant words (section 4). Top β: " + ", ".join(f'{x["word"]} (slot {x["idx"]}, β {x["beta"]})' for x in A["top_beta"][:8]) + ".", BODY))
story.append(Paragraph("Strongest edges (slot labels): " + "; ".join(f'{x["a"]}–{x["b"]} {x["w"]}' for x in A["top_edges"][:8]) + ".", BODY))

# ── semantic-neighbourhood tests ─────────────────────────────────────────────
story.append(Paragraph("6 · How close the address gets to a semantic neighbourhood in English", H2))
rows_c = list(csv.DictReader(open(os.path.join(ROOT, "calibration", "calibration_v1_en_zh.tsv"), encoding="utf-8"), delimiter="\t"))
by = collections.defaultdict(dict)
for r in rows_c: by[r["pair"]][r["half"]] = r["en_us"]
pairs = [(v["S"], v["L"]) for v in by.values() if "S" in v and "L" in v]
dsl = [abs(addr(a)[0] - addr(b)[0]) / N for a, b in pairs]
q = np.quantile(dsl, [.25, .5, .75]).round(4)
adj = collections.defaultdict(dict)
for i, j, w in d["edges"]: adj[int(i)][int(j)] = w
deg = collections.Counter()
for s_, m_ in adj.items():
    for j in m_: deg[j] += 1
def top(s, k=60):
    m_ = adj.get(s, {}); return set(j for j, _ in sorted(m_.items(), key=lambda x: -x[1] / (deg[x[0]] ** .5))[:k])
def jac(a, b):
    X, Y = top(addr(a)[0]), top(addr(b)[0]); return len(X & Y) / max(1, len(X | Y))
J = [jac(a, b) for a, b in pairs]
random.seed(1); words = [w for p in pairs for w in p]
R = [jac(random.choice(words), random.choice(words)) for _ in range(5000)]
thr = np.quantile(R, .95)
best = sorted(zip(J, pairs), reverse=True)[:12]
story.append(grid([["test", "result", "unrelated placement / chance"],
                   [f"{len(pairs)} same-synset English pairs (calibration S/L): |Δslot|/N quartiles", str([float(x) for x in q]), "[0.134, 0.293, 0.5]"],
                   ["pairs within 1 % of N apart", f"{sum(x < .01 for x in dsl)}", f"about {len(dsl) * 0.0199:.1f}"],
                   ["edge-neighbourhood Jaccard (top 60 edge targets weighted by 1/√degree): same-synset pairs, median", f"{np.median(J):.4f}", f"random pairs, median {np.median(R):.4f}"],
                   ["pairs above the random 95th percentile of that Jaccard", f"{sum(j > thr for j in J)} of {len(J)}", f"{len(J) * .05:.0f}"]], [250, 120, W - 370]))
story.append(Paragraph("Same-synset pairs with the highest edge-neighbourhood overlap: " + "; ".join(f"{a}/{b} {j:.2f}" for j, (a, b) in best) + ".", BODY))
vs, hs = addr("valence")[0], addr("hydrogen")[0]
shared = set(adj[vs]) & set(adj[hs])
story.append(Paragraph(f"<b>valence</b> slot {vs} (E {addr('valence')[1]:.4f}) and <b>hydrogen</b> slot {hs} (E {addr('hydrogen')[1]:.4f}) are {abs(vs - hs):,} slots apart. "
                       f"Their edge targets ({len(adj[vs])} and {len(adj[hs])}) share {len(shared)}. Of the shared targets, the heaviest by combined weight (dominant word of the slot): "
                       + ", ".join(dom.get(j, "?") for j, _ in sorted(((j, adj[vs][j] + adj[hs][j]) for j in shared), key=lambda x: -x[1])[:30]) + ".", BODY))
story.append(Paragraph("Edges join slots, not words, so a slot holding six words mixes six words' contexts; words above are read as the dominant word of each slot.", BODY))
srt = sorted((addr(t)[0], t) for t, c in cnt.most_common(3000) if len(t) >= 2)
random.seed(7)
story.append(Paragraph("Random ±3 slot neighbourhoods (dominant word of each slot): " + " | ".join(f"{s}: " + " ".join(dom.get(k, "·") for k in range(s - 3, s + 4)) for s in random.sample(sorted(slots), 8)), BODY))
story.append(Paragraph("Closest pairs in slot among the 3,000 most frequent words (same slot, Δ0): " + "; ".join(f"{a}/{b}" for (sa, a), (sb, b) in zip(srt, srt[1:]) if sb == sa)[:600] + " …", BODY))

story.append(Paragraph("7 · Faults logged from this bin (code against the goal; nothing repaired)", H2))
story.append(grid([["id", "fault", "evidence in this bin"],
                   ["F1", "one label per slot, higher E wins", f"label is the most frequent word in {100 * lab_dom / len(slots):.1f} % of slots"],
                   ["F2", "address is a hash of spelling", "same-synset pairs sit at the unrelated-placement quartiles"],
                   ["F7", f"load: {len(cnt):,} words on {N:,} slots", f"mean {len(cnt) / len(slots):.1f} words per slot; {len(empty)} slots empty"],
                   ["F8", "hex-string gate rejects ordinary a–f-letter words", f"{rejn['hex-string gate (only a-f letters, 6 or more)']} tokens"],
                   ["F9", "tokenizer drops whole tokens that begin with an apostrophe", f"{sum(lead.values()):,} tokens"],
                   ["F10", "trailing-apostrophe tokens rejected, not trimmed (possessive plurals)", f"{rejn['trailing apostrophe']:,} tokens"]], [26, 220, W - 246]))

out = sys.argv[1]
SimpleDocTemplate(out, pagesize=A4, leftMargin=30, rightMargin=30, topMargin=28, bottomMargin=28, title="SemPriCon slot dictionary, test_english_v1.0.bin").build(story, onFirstPage=footer, onLaterPages=footer)
dprint("wrote", out)
