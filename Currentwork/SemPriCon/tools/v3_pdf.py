#!/usr/bin/env python3
"""v3_pdf.py — the v3.0 word list and where each word lands, English and Chinese side by side (UNS mechanisms M3 and M4), as a PDF.

Reads data/v3_map.tsv and data/v3_build_summary.json (written by tools/v3_build.py); nothing is recomputed or typed by hand.
    .venv/bin/python tools/v3_pdf.py /home/rendier/Desktop/SpaceClaude/SemPriCon/SemPriCon_v3.0_word_list_map.pdf
"""
import csv, json, os, sys
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, LongTable, Table, TableStyle, Paragraph, Spacer, PageBreak
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DJ = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DJ", DJ + "DejaVuSans.ttf")); pdfmetrics.registerFont(TTFont("DJB", DJ + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("CJK", "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"))
body = ParagraphStyle("b", fontName="DJ", fontSize=8.6, leading=11.4, spaceAfter=4)
h1 = ParagraphStyle("h1", fontName="DJB", fontSize=15, leading=19, spaceAfter=6)
h2 = ParagraphStyle("h2", fontName="DJB", fontSize=10.5, leading=14, spaceBefore=8, spaceAfter=3)
cell = ParagraphStyle("c", fontName="DJ", fontSize=7.4, leading=9.2)
small = ParagraphStyle("s", fontName="DJ", fontSize=7.2, leading=9, textColor=colors.HexColor("#444444"))
P = lambda t, s=body: Paragraph(t, s)
zh = lambda t: f'<font name="CJK">{escape(t)}</font>'


def main(out):
    rows = list(csv.DictReader(open(os.path.join(ROOT, "data", "v3_map.tsv"), encoding="utf-8"), delimiter="\t"))
    S = json.load(open(os.path.join(ROOT, "data", "v3_build_summary.json"), encoding="utf-8"))
    E, Z, d, sl = S["english"], S["chinese"], S["english_vs_chinese_same_row_turn_distance"], S["SL_partner_turn_distance"]
    doc = SimpleDocTemplate(out, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=40, title="SemPriCon v3.0 word list and its UNS map", author="Cody Michael Allison (Michael Rendier)")
    st = [P("SemPriCon v3.0 — the 1 024-word list and where each word lands", h1),
          P(f"English (M3, Universal Native Space) and Chinese (M4, Universal Native Space), side by side. Word list <b>calibration_v3_en_zh.tsv</b>, sha256 {S['list_sha256'][:32]}…. "
            "Bins: <b>test_english_v3.bin</b> and <b>test_chinese_v3.bin</b> (state v6, read-only, Fresh Start 2026-10-21). Each row: the word pair as the row header; for each language the <b>slot</b> (0 … 24 999) and "
            "the <b>critical-line number γ</b> of that slot's exact zero ρ = ½ + iγ of ζ. Flat mechanisms (M1, M2) are not used."),
          P("Why Chinese is the baseline (Cody's stated rationale)", h2),
          P("Chinese is the baseline for measuring English because: <b>A)</b> it is ideographic, so a character is an idea and not a spelling; <b>B)</b> it is alive and spoken well today (not dead, not recently dead, not dying like Navajo and Comanche); "
            "<b>C)</b> it has been in existence for over five millennia; <b>D)</b> it is believed to be one of the most efficient partitionings of idea space in language form. It is taken as the bare minimum of ideas space. "
            "An ideographic writing system also separates ideas that English spelling lumps together (<i>couch</i> and <i>chair</i> are not two versions of one idea). Egyptian hieroglyphs would have been chosen if the language were not dead; "
            "Demotic put one character at the start of a word to carry its tone, and that became the tone / tense / conjugation marks that are invisible on screen and that the orbweaver will carry. "
            "<i>A, B and C are stated as fact by Cody; D is his assumption, to be tested, not measured here.</i>"),
          P("How the list was made (the established calibration protocol)", h2),
          P("1 024 rows = 512 concepts × two. <b>S</b> (first of a pair) is a simple word for a contextually simple concept; <b>L</b> is a different word of the same meaning with a deeper contextual interpretation. Each concept has an English word and a "
            "<b>single</b> Han character (the Chinese mechanism maps single characters only). Concepts are WordNet synsets with ≥ 2 single-word English lemmas; English S is the most frequent lemma in English Wikipedia text (80 M characters), L a rarer lemma "
            "with the most senses; Chinese S is a character CC-CEDICT lists the English S word as a whole gloss of (one of its first four definitions), L any other single character glossed by a lemma of the synset; "
            "every surface word is used once; at most 15 % of concepts from one lexicographer class. Traditional characters, in the engine's Han alphabet. <b>Known noise:</b> WordNet and CC-CEDICT senses are not perfect, "
            "and many Han characters are polysemous, so some pairs are a near match rather than a direct one (kept: this is the list as the protocol builds it; corrections go to a new version)."),
          P("The two UNS mechanisms, side by side (both on trial)", h2)]
    mech = [["", "English — M3", "Chinese — M4"],
            ["input", "the spelling of a word", "one character: its place in the dictionary"],
            ["winding / order", "base-95 Horner count of the letters, then v golden-angle turns: turn = frac(v/φ)", "dictionary order (radical, residual strokes, key component, code point): turn = (i + ½)/97 518"],
            ["θ (polar)", "π/2 — the equator, σ = ½", "π/2 — the equator, σ = ½"],
            ["φ (azimuth)", "2π · turn", "2π · turn"],
            ["slot", "⌊25 000 · turn⌋", "⌊25 000 · turn⌋"],
            ["r (radial)", "E / d*_taut with E = d* + turn·(Ω − d*): the radius is the azimuth (one spiral, one coordinate)", "E / d*_taut with E from the golden hash of the KEY component: radius is independent of azimuth (two coordinates)"],
            ["what neighbours mean", "nothing (a hash of spelling)", "shared radical / structure"],
            ["precision", "float seed of eb28ce8 (53 bits; carried on purpose)", "exact 64-bit integers"],
            ["collisions", "all words of a slot share it; one label per slot (highest E)", "same, but the library is a 97 518-character table"],
            ["zero used here", "exact zero of the slot (UNS)", "exact zero of the slot"]]
    t = Table([[P(c, cell) for c in r] for r in mech], colWidths=[84, 238, 238])
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), .3, colors.grey), ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8e8f0")), ("VALIGN", (0, 0), (-1, -1), "TOP")])); st.append(t)
    st += [P("What the first survey shows (computed from the two bins; no tuning)", h2)]
    res = [["", "English bin", "Chinese bin"],
           ["words / characters addressed", "1 024", "1 024"],
           ["occupied slots", str(E["occupied_slots"]), str(Z["occupied_slots"])],
           ["largest number sharing one slot", str(E["max_words_in_a_slot"]), str(Z["max_words_in_a_slot"])],
           ["words outranked by a higher E in their slot (invisible to the label)", str(E["outranked_words"]), str(Z["outranked_words"])],
           ["at slot 0", f"{E['slot_0_words']} (of which {E['words_of_8_or_more_letters']} words have 8 or more letters: the float seed runs out)", str(Z["slot_0_words"])],
           ["S and L of one concept: median distance round the ring (turns)", f"{sl['english_median']:.3f} (unrelated pairs: {sl['english_shuffled_median']:.3f})", f"{sl['chinese_median']:.3f} (unrelated pairs: {sl['chinese_shuffled_median']:.3f})"],
           ["S and L within 0.01 turn (of 512 concepts)", f"{sl['english_within_0_01']} (unrelated pairs: {sl['english_shuffled_within_0_01']})", f"{sl['chinese_within_0_01']} (unrelated pairs: {sl['chinese_shuffled_within_0_01']})"],
           ["engine filter would have rejected", f"{E['filter_would_reject']} words (not applied here)", "—"]]
    t = Table([[P(c, cell) for c in r] for r in res], colWidths=[220, 170, 170])
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), .3, colors.grey), ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8e8f0")), ("VALIGN", (0, 0), (-1, -1), "TOP")])); st.append(t)
    st += [Spacer(1, 4), P(f"<b>English against Chinese, same row:</b> the same concept lands in the same slot in <b>{S['same_slot']}</b> of 1 024 rows. The median distance round the ring between the two placements of one row is {d['median']:.3f} turn "
                          f"(rows paired with unrelated rows: {d['shuffled_median']:.3f}; uniform expectation of the mean: 0.250). Within 0.01 turn: {d['within_0_01']} rows (unrelated: {d['shuffled_within_0_01']}). "
                          "The two mechanisms place a concept independently of each other, as expected. Nothing has been assigned or aligned yet: the next step is a discussion of the assignment, not of the mapping.", body),
           P("Reading the table: <b>slot</b> is the integer 0–24 999; <b>γ</b> is the imaginary part of the zero ρ = ½ + iγ at that slot (the number on the critical line); a dagger (†) marks a word outranked in its slot (another word of the same bin has the higher E and carries the label). "
             "Per-row detail (E, turn, radius, state, whether the engine filter rejects the word) is in <b>SemPriCon/data/v3_map.tsv</b>.", small), PageBreak()]
    hdr = [P("<b>row</b>", cell), P("<b>English · </b>" + zh("中文"), cell), P("<b>English slot</b>", cell), P("<b>English γ</b>", cell), P(zh("中文") + "<b> slot</b>", cell), P(zh("中文") + "<b> γ</b>", cell)]
    data = [hdr]
    for r in rows:
        head = f'<b>{escape(r["en"])}</b> · {zh(r["zh"])}'
        data.append([P(f'{r["id"]}{r["half"]}', cell), P(head, cell), P(r["en_slot"] + (" †" if r["en_state"] == "O" else ""), cell), P(f'{float(r["en_gamma"]):.6f}', cell),
                     P(r["zh_slot"] + (" †" if r["zh_state"] == "O" else ""), cell), P(f'{float(r["zh_gamma"]):.6f}', cell)])
    lt = LongTable(data, colWidths=[44, 170, 70, 92, 70, 92], repeatRows=1)
    lt.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), .25, colors.HexColor("#bbbbbb")), ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8e8f0")), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f6f6fa")]), ("TOPPADDING", (0, 0), (-1, -1), 1.2), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.2)]))
    st.append(lt)

    def foot(c, dc):
        c.saveState(); c.setFont("DJ", 7); c.setFillColor(colors.grey); c.drawString(36, 22, "SemPriCon v3.0 · word list and UNS map · test_english_v3.bin / test_chinese_v3.bin"); c.drawRightString(A4[0] - 36, 22, f"page {dc.page}"); c.restoreState()
    doc.build(st, onFirstPage=foot, onLaterPages=foot)
    print("wrote", out)


if __name__ == "__main__":
    main(sys.argv[1])
