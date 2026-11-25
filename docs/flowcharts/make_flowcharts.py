#!/usr/bin/env python3
"""make_flowcharts.py -- the code flow charts of the Monad (ptol.c, THE CHILD'S VOICE) and of the Harness (monad_harness.c, THE HARNESS HEARS).   (2026-11-25)
Writes monad_flow.svg and harness_flow.svg here and converts each to PNG (rsvg-convert).  Every title is a name that exists in the C files (tests/test_flowcharts.py checks that).
    VAPMIP/.venv/bin/python docs/flowcharts/make_flowcharts.py
"""
import os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from flowlib import Chart
HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = {}                                                  # name -> list of identifiers the chart claims (checked against the C source)


def monad() -> Chart:
    c = Chart('The Monad: one turn through ptol.c  (THE CHILD\'S VOICE)', 'Python twins: responder.py · sedenion_window.py · scaled_boxkite_orbweaver_monad.py · weave_cycle.py · tenseplan.py · lyndon_conjugation.py · tone_chord.py   |   the Harness is the other chart',
              [('cv_read', 'the speaker\'s turn'), ('cv_turn', 'the resident turn · run_console'), ('cv_compose', 'the scaled orbweaver: plan the web'), ('cv_write', 'one sentence, slot by slot'), ('one word', 'cv_pick · cv_revisit · cv_inflect'), ('stored data', 'read, never written, by the voice')],
              lane_w=300, row_h=76, top=104)
    n = c.node; e = c.edge
    # --- lane 1: cv_turn
    n('t0', 1, 0, 'term', 'say / cmd frame', 'plain text from the console'); n('t1', 1, 1, 'io', 'mh_pump → mh_frame', 'monad_harness.c: frame link, radio folded in')
    n('t2', 1, 2, 'dec', "text starts with '/'?"); n('cmd', 2, 2, 'proc', 'cv_command', '/state /plan /trace /audit\n/drift /tense  → chat frame')
    n('t3', 1, 3, 'pre', 'mh_ear_hear(EXTERNAL)', 'harness chart: numbers out, count, price')
    n('t4', 1, 4, 'pre', 'cv_read(prompt)', 'state · tone · words into the ring')
    n('t5', 1, 6, 'pre', 'cv_compose(prompt, 3)', 'plan the web; every sentence by cv_write')
    n('t6', 1, 17, 'proc', 'cv_audit', 'seven checks on the reply')
    n('t7', 1, 18, 'pre', 'mh_ear_hear(INTERNAL)', 'harness chart: price the reply, move the drift')
    n('t8', 1, 19, 'io', 'mh_send_chat', 'reply, σ (measure_sigma), Γ (measure_gamma), primes'); n('t9', 1, 20, 'term', 'the console shows it')
    for a, b, l in (('t0', 't1', ''), ('t1', 't2', ''), ('t2', 't3', 'no'), ('t3', 't4', '')): e(a, b, l)
    e('t2', 'cmd', 'yes', 'side'); e('t4', 'r0', '', 'side'); e('t5', 'c0', '', 'side'); e('t6', 't7'); e('t7', 't8'); e('t8', 't9')
    c.note(1, 5, 'or  /tense <name> : one sentence\nin that tense, straight to cv_write', dy=-6)
    # --- lane 0: cv_read
    n('r0', 0, 4, 'proc', 'mh_split_numbers', 'numbers are not words: they leave here'); n('r1', 0, 5, 'pre', 'mh_ear_user_turn', 'harness chart: 14 poles → mix → target')
    n('r2', 0, 6, 'dec', 'meter loaded?'); n('r3', 0, 7, 'proc', 'mh_state_heard', 'axis farthest from RECEPTIVE, level 0..6'); n('r4', 0, 8, 'proc', 'cv_detect_tone', 'lexicon fallback (NE OPI DA OXT GABA)')
    n('r5', 0, 9, 'proc', 'words → ring · user words', 'cv_place: e0 anchor, newest into slot 1')
    e('r0', 'r1'); e('r1', 'r2'); e('r2', 'r3', 'yes'); e('r2', 'r4', 'no', 'loopl'); e('r3', 'r5', '', 'loopr'); e('r4', 'r5')
    # --- lane 2: cv_compose
    n('c0', 2, 6, 'proc', 'mh_split_numbers', 'content words: not closed class, ≥ 3 letters'); n('c1', 2, 7, 'proc', 'cv_entry per word', 'voice_lex.bin: first synset → 19 relation counts')
    n('c2', 2, 8, 'proc', 'rv = Σ vectors', 'cv_turbulent: ≥ 3 radii within half of the strongest?'); n('c3', 2, 9, 'proc', 'cv_room', 'cv_cam_encode ×2 (SHA-256) → b/c → regime → reach')
    n('c4', 2, 10, 'proc', 'cv_infer_direction', 'ranked radii; hyper/hyponyms only as the fallback'); n('c5', 2, 11, 'proc', 'words → radii', 'each word to its own strongest spoke')
    n('c6', 2, 12, 'dec', 'depth × radius left?'); n('c7', 2, 13, 'pre', 'cv_emit(paragraph)', 'tense = cv_lemniscate_tense(depth, reach)', tag='1'); n('c8', 2, 14, 'dec', 'turbulent ∧ deepest\n∧ not the last radius?')
    n('c9', 2, 15, 'pre', 'cv_emit(pivot) · cv_emit(wrap)', 'strut-partner tone: GLU|GABA DA|5HT NE|OXT', tag='1'); n('c10', 2, 16, 'proc', 'join the pieces', 'connective + sentence; fixed rotation')
    for a, b, l in (('c0', 'c1', ''), ('c1', 'c2', ''), ('c2', 'c3', ''), ('c3', 'c4', ''), ('c4', 'c5', ''), ('c5', 'c6', ''), ('c6', 'c7', 'yes'), ('c7', 'c8', ''), ('c8', 'c9', 'yes')): e(a, b, l)
    e('c9', 'c6', '', 'loopr', 12); e('c8', 'c6', 'no', 'loopl'); e('c6', 'c10', 'no', 'loopr', 40); e('c10', 't6', '', 'elbow')
    # --- lane 3: cv_write
    n('w0', 3, 13, 'proc', 'cv_resolve_tense', 'name · auto (lemniscate) · mirror (yours)', tag='1', tagside='l'); n('w1', 3, 14, 'proc', 'topic', 'cv_morphy_pos lemmas · cv_neighbours (co-occurrence) · imitation')
    n('w2', 3, 15, 'proc', 'frame · cv_trajectory', 'NE>0.3 sva · ≥2 nouns svo · else sv_prep; meet, then lead'); n('w3', 3, 16, 'dec', 'slot left?')
    n('w4', 3, 17, 'proc', 'Tone7 ← trajectory[k]', 'cv_tone_from_axis → cv_knobs_of'); n('w5', 3, 18, 'pre', 'cv_pick', 'one word for the open slot', tag='2')
    n('w6', 3, 19, 'dec', 'web ∧ content slot?'); n('w7', 3, 20, 'pre', 'cv_revisit', 'thin margin → re-pick on the strut', tag='3'); n('w8', 3, 21, 'dec', 'V slot, or AUX\nwhen tense ≠ present?')
    n('w9', 3, 22, 'pre', 'cv_inflect', 'the Lyndon verb group', tag='4'); n('w10', 3, 23, 'proc', 'cv_marker · cv_place', 'invisible tone|tense|conj tag; ring; taken'); n('w11', 3, 24, 'proc', 'assemble the sentence', 'capital, full stop; Piece.marked')
    for a, b, l in (('w0', 'w1', ''), ('w1', 'w2', ''), ('w2', 'w3', ''), ('w3', 'w4', 'yes'), ('w4', 'w5', ''), ('w5', 'w6', ''), ('w6', 'w7', 'yes'), ('w7', 'w8', ''), ('w8', 'w9', 'yes'), ('w9', 'w10', ''), ('w10', 'w11', '')): e(a, b, l)
    e('c7', 'w0', '', 'side')
    e('w6', 'w8', 'no', 'loopl'); e('w8', 'w10', 'no', 'loopl', 14); e('w10', 'w3', '', 'loopr'); e('w3', 'w11', 'no', 'loopl', 28)
    # --- lane 4: one word (the call targets)
    n('p0', 4, 17, 'term', '(2) cv_pick', 'ring slot: DET PREP CONJ AUX', tagside='l', tag='2'); n('p1', 4, 18, 'proc', 'candidates', 'content: topic − taken, else corpus-frequent by POS')
    n('p2', 4, 19, 'proc', 'w = P(w|prev)^(coherence·(1+g)) · x', 'g = bw_correction; user_boost + imitation'); n('p3', 4, 20, 'proc', 'heard words ≥ 1.1 × max', 'the child repeats what it heard')
    n('p4', 4, 21, 'proc', 'prune · pool · novelty', 'GABA floor · GLU/NE pool · DA rank → word, P, n')
    n('q0', 4, 22, 'term', '(3) cv_revisit', '', tagside='l', tag='3'); n('q1', 4, 23, 'dec', 'cv_turbulent(weights)?'); n('q2', 4, 24, 'proc', 're-pick under cv_strut_partner(axis)', 'keep it only if P₂ > P and the word differs')
    n('v0', 4, 25, 'term', '(4) cv_inflect', '', tagside='l', tag='4'); n('v1', 4, 26, 'proc', 'cv_parse_tense → cv_verb_group', 'ranks TENSE 4 > MODAL 3 > PERF 2 > PROG 1 > V 0; cv_duval'); n('v2', 4, 27, 'proc', 'cv_conjugates', 'affix hopping: modal → bare stem; have → -en; be → -ing')
    n('v3', 4, 28, 'proc', 'cv_form', 'be/have table · VERB_FORMS (irregular) · cv_regular rules'); n('v4', 4, 29, 'proc', 'surface · tense code · conj code', 'will have seen · future · pastpart')
    for a, b in (('p0', 'p1'), ('p1', 'p2'), ('p2', 'p3'), ('p3', 'p4'), ('q0', 'q1'), ('v0', 'v1'), ('v1', 'v2'), ('v2', 'v3'), ('v3', 'v4')): e(a, b)
    e('q1', 'q2', 'yes')
    # stored data
    n('d0', 5, 7, 'data', 'voice_lex.bin · monad3_c.bin', 'words, parts of speech, 19 counts; co-occurrence CSR'); n('d1', 5, 13, 'data', 'english_corpus.txt', 'the bigram P(w|prev), lam 0.7 (cv_bg_fit)')
    n('d2', 5, 19, 'data', 'PTOL_USAGE_DIR', 'usage_c.txt · numbers_c.txt (kept by the harness)')
    return c


def harness() -> Chart:
    c = Chart('The Harness: hearing a turn  (monad_harness.c, THE HARNESS HEARS)', 'Python twins: numeric.py · conversation_usage.py · bw_drift.py · vocab_store.py · state_repass.py · neuro_recipes.py · prompt_to_state.py (usage meter) · three_hearers.py   |   the Monad is the other chart',
              [('the frame link', 'mh_open · mh_pump · mh_send_chat'), ('MH_EXTERNAL', 'the user: counted and priced'), ('MH_INTERNAL', 'the reply: priced, moves the drift'), ('mh_split_numbers', 'numbers are not words'), ('mh_ear_user_turn', 'the user\'s state'), ('stored data', '')],
              lane_w=292, row_h=76, top=104)
    n = c.node; e = c.edge
    # lane 0: frame link
    n('f0', 0, 0, 'term', 'console (Python, curses)', 'ptolemy_console.py'); n('f1', 0, 1, 'io', 'socketpair frames', 'newline-delimited JSON: say cmd mode ping attach quit radio')
    n('f2', 0, 2, 'pre', 'mh_open · mh_recv', 'poll; EOF or hard error ends the session'); n('f3', 0, 3, 'dec', 'radio frame?')
    n('f4', 0, 4, 'proc', 'mh_parse_support_line', '« face » post · « Ptolemy » judgement'); n('f5', 0, 5, 'proc', 'mh_ingest_support', 'HARDEN THROTTLE ESCALATE raise emote; DEFER HOLD change nothing')
    n('f6', 0, 6, 'proc', 'say · cmd · mode · … → ptol.c', 'the monad answers (cv_turn / cv_command)'); n('f7', 0, 7, 'io', 'mh_send_chat', 'text, σ, Γ, primes, mode'); n('f8', 0, 8, 'term', 'console shows the reply')
    for a, b, l in (('f0', 'f1', ''), ('f1', 'f2', ''), ('f2', 'f3', ''), ('f3', 'f4', 'yes'), ('f4', 'f5', ''), ('f6', 'f7', ''), ('f7', 'f8', '')): e(a, b, l)
    e('f3', 'f6', 'no', 'loopl'); e('f5', 'f2', '', 'loopl', 24)
    c.note(0, 9, 'the Monad calls mh_ear_hear and\nmh_ear_user_turn (ptol.c, cv_turn / cv_read)', dy=-6)
    # lane 1: external
    n('x0', 1, 1, 'term', 'mh_ear_hear(text, cls, pair)', 'called by cv_turn before the user is answered'); n('x1', 1, 2, 'pre', 'mh_split_numbers', 'prose, nums', tag='A'); n('x2', 1, 3, 'proc', 'n_numbers += nums', 'not for MH_DOCUMENT')
    n('x3', 1, 4, 'dec', 'cls?'); n('x4', 1, 5, 'proc', 'mh_ear_bits_per_word(prose)', 'priced BEFORE it is counted: mean −log₂ mh_ear_p_word; p_word = λ·usage + (1−λ)·general, λ = N/(N+200)'); n('x5', 1, 6, 'proc', 'u_observe', 'tokens, stop-words, length ≥ 3, no digits, known by the monad')
    n('x6', 1, 7, 'proc', 'pending[pair] = bits', '16 slots; the oldest is dropped')
    for a, b, l in (('x0', 'x1', ''), ('x1', 'x2', ''), ('x2', 'x3', ''), ('x3', 'x4', 'EXTERNAL'), ('x4', 'x5', ''), ('x5', 'x6', '')): e(a, b, l)
    c.note(1, 9, 'MH_DOCUMENT: nothing is counted', dy=-14)
    # lane 2: internal
    n('i0', 2, 4, 'proc', 'bits = mh_ear_bits_per_word(reply)', 'the monad\'s own words, same prices'); n('i1', 2, 5, 'dec', 'pending[pair] found?')
    n('i2', 2, 6, 'proc', 'w = pending bits, b = reply bits', 'only if b > 0 ∧ w > 0'); n('i3', 2, 7, 'pre', 'mh_bw_correction(w, b)', 'bw_drift.py'); n('i4', 2, 8, 'proc', 'δ = ln(b/w) ;  Γ = tanh(ln(Z/Z₀)/2)', 'Z = w + ib, Z₀ = √(wb)(1+i)')
    n('i5', 2, 9, 'dec', '|δ| > 0.35  ∨  (active ∧ |δ| > 0.15)?'); n('i6', 2, 10, 'proc', 'bw_corr = sign(δ)·(|δ|−0.15)/0.85, clipped to ±1', '> 0 favour probable words; < 0 flatten'); n('i7', 2, 11, 'proc', 'mh_ear_bw_correction()', 'read by cv_pick: exponent coherence·(1+g)')
    for a, b, l in (('i0', 'i1', ''), ('i1', 'i2', 'yes'), ('i2', 'i3', ''), ('i3', 'i4', ''), ('i4', 'i5', ''), ('i5', 'i6', 'yes'), ('i6', 'i7', '')): e(a, b, l)
    e('x3', 'i0', 'INTERNAL', 'side'); e('i5', 'i7', 'no (0)', 'loopr')
    # lane 3: numbers
    n('n0', 3, 1, 'term', '(A) mh_split_numbers', '', tagside='l', tag='A'); n('n1', 3, 2, 'dec', 'version?', '1.2.3  (digits, 2+ dots)'); n('n2', 3, 3, 'dec', 'number?', 'sign $ int .dec % st nd rd th')
    n('n3', 3, 4, 'dec', 'code?', 'x2 · h264 · 3d'); n('n4', 3, 5, 'proc', 'one space; record mh_number', 'integer decimal percent ordinal currency signed code')
    n('n5', 3, 6, 'proc', 'copy the byte', 'no match here'); n('n6', 3, 7, 'proc', 'prose out', 'tested on 4,000 random strings against numeric.py')
    for a, b, l in (('n0', 'n1', ''), ('n1', 'n2', 'no'), ('n2', 'n3', 'no'), ('n3', 'n5', 'no'), ('n4', 'n6', ''), ('n5', 'n6', '')): e(a, b, l)
    e('n1', 'n4', 'yes', 'loopr'); e('n2', 'n4', 'yes', 'loopr', 20); e('n3', 'n4', 'yes', 'loopl')
    # lane 4: user turn
    n('u0', 4, 1, 'term', 'mh_ear_user_turn(text, fill)', 'called by cv_read'); n('u1', 4, 2, 'proc', 'ms_dose', 'more than 3 sentences: read each, average by length'); n('u2', 4, 3, 'proc', 'mh_meter_raw', 'tokens (1–2-grams) → TF-IDF (sublinear, l2) → ridge → clip 0..1 → 4.5×')
    n('u3', 4, 4, 'proc', '× gain, capped at 9', 'calibration gain per pole'); n('u4', 4, 5, 'proc', 'solution: C = (V·C + v·d)/(V + v)', 'v = clip(words/25, 0.5, 3); V ≤ 8'); n('u5', 4, 6, 'proc', 'heal: |conc − base| ≤ spread → 0', 'a reading inside the noise is not acted on')
    n('u6', 4, 7, 'proc', 'mix[a] = BASELINE + (light − dark)/9', 'OPI GLU GABA DA 5HT NE OXT; clamp 0..1'); n('u7', 4, 8, 'proc', 'k_eff = 0.6·√(fill/16)', 'fewer words in the 16-slot ring, smaller correction')
    n('u8', 4, 9, 'dec', 'dist(mix, RECEPTIVE) < 0.5?'); n('u9', 4, 10, 'proc', 'target = mix  (held)', ''); n('u10', 4, 11, 'proc', 'target = RECEPTIVE − k_eff(mix − RECEPTIVE)', 'conjugate: the noise-cancelling reply')
    n('u11', 4, 12, 'proc', 'mh_state_heard · mh_state_trajectory', 'meet the mix, lead to the target, per word')
    for a, b in (('u0', 'u1'), ('u1', 'u2'), ('u2', 'u3'), ('u3', 'u4'), ('u4', 'u5'), ('u5', 'u6'), ('u6', 'u7'), ('u7', 'u8')): e(a, b)
    e('u8', 'u9', 'yes', 'loopl'); e('u8', 'u10', 'no'); e('u9', 'u11', '', 'loopl'); e('u10', 'u11')
    # lane 5: stored data
    n('s0', 5, 2, 'data', 'user_state.bin', 'ridge: 45,448 features × 14 poles, gain, base, spread'); n('s1', 5, 5, 'data', 'usage_c.txt', 'n_obs and one count per lemma'); n('s2', 5, 7, 'data', 'numbers_c.txt', 'how many numbers were heard')
    n('s3', 5, 9, 'data', 'mh_ear_close', 'saves usage_c.txt and numbers_c.txt on exit')
    return c


def main():
    for name, fn in (('monad_flow', monad), ('harness_flow', harness)):
        ch = fn(); p = os.path.join(HERE, name + '.svg'); open(p, 'w').write(ch.svg())
        subprocess.run(['rsvg-convert', '-w', '2000', '-o', os.path.join(HERE, name + '.png'), p], check=True); print(name, 'ok')


if __name__ == '__main__': main()
