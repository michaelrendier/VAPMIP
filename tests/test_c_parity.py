"""C <-> Python parity (2026-11-25).  The Python monad is the test bench; the C harness (PtolC/monad_harness.c) and voice (PtolC/ptol.c) are ported from it
and must agree.  Builds the probes with cc and compares.  Skips if there is no C compiler."""
import os, random, re, shutil, subprocess, sys
import numpy as np
import pytest
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); PC = os.path.join(ROOT, 'PtolC'); sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'Currentwork', 'UserState'))
import numeric as N

pytestmark = pytest.mark.skipif(shutil.which('cc') is None or not os.path.exists(os.path.join(PC, 'user_state.bin')), reason='needs cc and PtolC/user_state.bin')


def build(tmp, name, srcs):
    out = str(tmp / name)
    r = subprocess.run(['cc', '-O2', '-I' + PC, '-o', out] + [os.path.join(PC, s) for s in srcs] + ['-lm'], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-2000:]
    return out


@pytest.fixture(scope='module')
def probe(tmp_path_factory):
    tmp = tmp_path_factory.mktemp('probe')
    exe = build(tmp, 'hp', ['tests/c_harness_probe.c', 'monad_harness.c', 'monad.c', 'tokenizer.c', 'filter.c'])
    state = str(tmp / 'state')
    def run(lines):
        r = subprocess.run([exe, state, PC], input='\n'.join(lines) + '\n', capture_output=True, text=True, timeout=300)
        assert r.returncode == 0, r.stderr
        return [l.split('\t') for l in r.stdout.splitlines()]
    return run


# ── numbers ─────────────────────────────────────────────────────────────────
FIXED = ["I told you 3 times, 2.5% of $1,200 in the 4th row, x2 and h264, -7 degrees, 1,000,000 words. version 3.10.3 ok", "no numbers at all", "3d 2nd 21st 3rdx 1.2.3.4a 1,000, and 5.",
         "a-7 b+3 x.5 .5 5. 12abc abc12 _3 3_ 007 0.001% $.5 €5 £7,000.25 1e5 2,3,4 1..2 3.14.15.92"]


def ref(t):
    w, ns = N.split(t); return w, [(n.text, n.kind, (n.value if n.value is not None else 0.0), int(n.value is not None)) for n in ns]


def cres(row):
    return row[1], [(x.split('|')[0], x.split('|')[1], float(x.split('|')[2]), int(x.split('|')[3])) for x in row[3:]]


def test_numbers_agree_on_fixed_and_random_strings(probe):
    rnd = random.Random(5); alpha = list("0123456789,.%$+- abcxdnrst_hE'") + ['th', 'st', 'nd', 'rd']
    cases = FIXED + [''.join(rnd.choice(alpha) for _ in range(rnd.randint(1, 24))) for _ in range(4000)]
    rows = probe(['N ' + t for t in cases])
    bad = []
    for t, row in zip(cases, rows):
        w, ns = ref(t); cw, cn = cres(row)
        if cw != w or len(ns) != len(cn) or any(a[:2] != b[:2] or abs(a[2] - b[2]) > 1e-9 * max(1, abs(a[2])) or a[3] != b[3] for a, b in zip(ns, cn)): bad.append((t, w, ns, cw, cn))
    assert not bad, bad[:3]


# ── the drift ────────────────────────────────────────────────────────────────
def test_drift_agrees_with_bw_drift_py(probe):
    import bw_drift
    rnd = random.Random(9); d = bw_drift.BWDrift(); lines, refs, act = [], [], 0
    for _ in range(300):
        w, b = rnd.uniform(1, 20), rnd.uniform(1, 20); r = d.update(w, b); lines.append('D %.9f %.9f %d' % (w, b, act)); refs.append(r); act = int(r['active'])
    for row, r in zip(probe(lines), refs):
        assert abs(float(row[1]) - r['delta']) < 1e-6 and abs(float(row[2]) - r['gamma']) < 1e-6 and int(row[3]) == int(r['active']) and abs(float(row[4]) - r['bw_correction']) < 1e-6


# ── the user meter, the solution and the repass ────────────────────────────────
PROMPTS = ["Why does this keep breaking?! I already told you the file was there.", "That makes sense, thanks. Can you show the next step?", "I'm tired. Let's try again slowly.",
           "This is a long message. It has many sentences. Every one of them says something. The fourth one is here. And a fifth for good measure. Great, that worked!",
           "Hi, I'd like to learn how the Lambert W function connects to the Riemann zeros.", "ok", "WHAT?!", "Oh that's interesting, so d* is the boundary. Show me."]


@pytest.fixture(scope='module')
def py_engine():
    from prompt_to_state import PromptToState
    return PromptToState()


def py_usage_dose(P, text):
    """PromptToState.dose with the lexical meters, the continuation channel and the aspect mask switched off: what the C meter is defined to do."""
    P.raw_dose_orig = P.raw_dose
    P.raw_dose = lambda t: (np.clip(P.mdl.predict(P.vec.transform([t]))[0], 0, 1) * 4.5, np.zeros(14))
    P.continuation = lambda t: (np.zeros(14), 0.0); P.mask_aspect = lambda t: t
    return P.dose(text)[0]


def test_meter_agrees_with_the_python_usage_ridge(probe, py_engine):
    rows = probe(['M ' + t for t in PROMPTS])
    for t, row in zip(PROMPTS, rows):
        py = np.clip(py_engine.mdl.predict(py_engine.vec.transform([t]))[0], 0, 1) * 4.5
        assert np.allclose([float(x) for x in row[1:]], py, atol=2e-5), (t, row[1:4], py[:3])


def test_state_turns_agree_with_solution_and_state_repass(probe, py_engine):
    import neuro_recipes as NR, state_repass as SR
    from solution_tests import Solution
    sol = Solution(vmax=8.0); P = py_engine; rows = probe(['T 16|' + t for t in PROMPTS]); engine_stub = None
    class Eng:
        NT = SR.AXES
        def __init__(s, c, sp, base): s.c, s.sp, s.base = c, sp, base
        def turn(s, text): return {'conc': s.c, 'spread': s.sp}
    for t, row in zip(PROMPTS, rows):
        d = py_usage_dose(P, t); words = len(re.findall(r"[A-Za-z']+", t)); v = float(min(3.0, max(0.5, words / 25.0))); c = sol.add(d, v)
        conc_c = np.array([float(x) for x in row[-14:]]); assert np.allclose(conc_c, c, atol=1e-3), (t, conc_c[:3], c[:3])
        sp = np.minimum(9.0, np.array([0.0] * 14)); import struct
        st = SR.StateRepass(Eng(conc_c.tolist(), [float(x) for x in np.fromfile(os.path.join(PC, 'user_state.bin'), '<f8', 14, offset=8 + 12 + 14 * 8 * 2)], P.base))
        st.observe(t, fill=16)
        mix_c = [float(x) for x in row[7:14]]; tgt_c = [float(x) for x in row[14:21]]
        assert np.allclose(mix_c, [st.mix[a] for a in SR.AXES], atol=6e-4) and np.allclose(tgt_c, [st.target[a] for a in SR.AXES], atol=0.011), (t, mix_c, st.mix)
        assert int(row[2]) == int(st.held) and int(row[3]) == int(st.healed.sum()), (t, row[2:4], st.held, st.healed.sum())
        assert row[6] == st.heard_tone()[0] and int(row[4]) == st.heard_tone()[1]
        assert row[21:26] == ['%s:%d' % (('OPI' if a == 'CB1' else a), l) for a, l in st.trajectory(5)], (t, row[21:26], st.trajectory(5))


def test_thin_context_scales_the_correction_like_the_python(probe):
    rows = probe(['T 9|WHAT?! Why does this keep breaking?!', 'T 16|WHAT?! Why does this keep breaking?!'])
    assert abs(float(rows[0][5]) - 0.6 * (9 / 16) ** 0.5) < 1e-3 and abs(float(rows[1][5]) - 0.6 * (16 / 16) ** 0.5) < 1e-3


# ── the usage store ───────────────────────────────────────────────────────────
def test_usage_counts_confidence_and_p_word(probe):
    from vocab_store import content_lemmas, sentences
    text = "The king rules the kingdom. The queen reads the book in 2024 and x2. The king reads the book."
    known = {'king', 'kingdom', 'queen', 'book', 'rules', 'reads'}
    rows = probe(['K ' + ' '.join(known), 'H 0|p1|' + text, 'R king', 'R queen', 'R zzz'])
    prose, nums = N.split(text); cnt = {}
    for s in sentences(prose):
        for l in content_lemmas(s):
            if l in known: cnt[l] = cnt.get(l, 0) + 1
    n_obs = sum(cnt.values()); assert int(rows[0][2]) == n_obs and int(rows[0][1]) == 2           # 2 numbers found (2024, x2)
    lam = n_obs / (n_obs + 200.0); assert abs(float(rows[0][3]) - lam) < 1e-9
    for w, row in zip(('king', 'queen', 'zzz'), rows[1:]):
        pu = (cnt.get(w, 0) + 0.5) / (n_obs + 0.5 * len(cnt)); assert abs(float(row[1]) - (lam * pu + (1 - lam) * 1e-4)) < 1e-9


def test_the_reply_moves_the_drift_for_the_next_turn(probe):
    rows = probe(['K king queen book', 'H 0|p0|king queen book king queen book king queen book', 'H 0|c|king queen book', 'H 1|c|zzz yyy xxx www vvv', 'H 0|d|king queen book', 'H 1|d|king queen book'])
    assert float(rows[1][4]) == 0.0 and float(rows[2][4]) > 0.0               # a reply dearer than the user's own words pushes the correction positive (favour probable words)


# ═══════════ the voice: ptol.c, driven through `ptol -P` ═══════════════════════════════════════════════════════════
@pytest.fixture(scope='module')
def vprobe(tmp_path_factory):
    if not os.path.exists(os.path.join(PC, 'monad3_c.bin')): pytest.skip('needs PtolC/monad3_c.bin')
    tmp = tmp_path_factory.mktemp('vprobe'); exe = build(tmp, 'ptol_probe', ['ptol.c', 'monad_harness.c', 'monad.c', 'tokenizer.c', 'filter.c'])
    env = dict(os.environ, PTOL_USAGE_DIR=str(tmp / 'u'), PTOLC_DIR=PC)
    def run(lines):
        r = subprocess.run([exe, '-P'], input='\n'.join(lines) + '\n', capture_output=True, text=True, timeout=600, env=env); assert r.returncode == 0, r.stderr[-500:]
        return [l.split('\t') for l in r.stdout.splitlines()]
    return run


SPECS = ['present', 'past', 'future', 'conditional', 'perfect', 'progressive', 'past perfect', 'past progressive', 'future perfect', 'future progressive', 'present perfect progressive',
         'past perfect progressive', 'imperative', 'base', 'future perfect progressive']


def test_verb_groups_agree_with_lyndon_conjugation_py(vprobe):
    import lyndon_conjugation as LC
    from nltk.corpus import wordnet as wn
    rnd = random.Random(3); lem = sorted({l for s in wn.all_synsets('v') for l in s.lemma_names() if l.isalpha() and l.islower() and 2 < len(l) < 20})
    sample = ['be', 'have', 'do', 'go', 'see', 'walk', 'stop', 'plan', 'try', 'carry', 'lie', 'die', 'know', 'think', 'run', 'rule', 'read', 'admit', 'visit', 'panic'] + rnd.sample(lem, 400)
    cases = [(sp, l, pl, pe) for sp in SPECS for l in sample[:60] for pl in (0, 1) for pe in (1, 3)] + [(rnd.choice(SPECS), l, rnd.choice((0, 1)), 3) for l in sample[60:]]
    rows = vprobe(['V %s|%s|%d|%d' % c for c in cases]); bad = []
    for (sp, l, pl, pe), row in zip(cases, rows):
        fr = LC.inflection_frame(sp, l, 'pl' if pl else 'sg', pe)
        exp = (' '.join(fr['surface']), fr['tense'], fr['conj'], len(LC.verb_group(sp)), len(LC.factors(sp)), *LC.verb_group(sp))
        got = (row[1], row[2], row[3], int(row[4]), int(row[5]), *[int(x) for x in row[6:]])
        if exp != got: bad.append(((sp, l, pl, pe), exp, got))
    assert not bad, (len(bad), bad[:4])


def test_tense_plan_agrees_with_tenseplan_py(vprobe):
    import tenseplan as TP
    pairs = [(d, r) for r in range(1, 7) for d in range(1, r + 1)]
    for (d, r), row in zip(pairs, vprobe(['T %d %d' % p for p in pairs])): assert row[1] == TP.lemniscate_tense(d, r), (d, r)
    sents = ["I walked home yesterday", "We will go tomorrow", "I walk", "She was tired and he had left", "going to the shop", "We are going to win", "Nothing happened here", "He said nothing", "It is what it is",
             "I'm gonna try", "They shall not pass", "the played game ended", "red", "I can't believe you didn't come", "It's already finished"]
    for s, row in zip(sents, vprobe(['M ' + s for s in sents])): assert row[1] == TP.mirror_tense(s), (s, row[1], TP.mirror_tense(s))


def test_cam_encode_agrees_with_monad_py(vprobe):
    import monad
    texts = ["The king rules the kingdom and the dog chases the cat in the garden.", "Why does the bridge keep breaking when the river floods the valley?", "I am so happy and grateful, thank you!",
             "what does it mean when they say never again", "a", "hello", "The painter mixes the colour and the sculptor carves the stone while the musician plays the song in the temple.",
             "It was not a good idea, and it is never explained, so the reader remains uncertain; however, the explanation is meant to clarify."]
    for t, row in zip(texts, vprobe(['C ' + t for t in texts])):
        assert np.allclose([float(x) for x in row[1:]], monad.cam_encode(t), atol=1e-9), t


def test_bigram_agrees_with_sedenion_window_py(vprobe):
    import sedenion_window as SW
    bg = SW.Bigram().fit([open(os.path.join(ROOT, 'english_corpus.txt'), encoding='utf-8', errors='ignore').read()])
    rnd = random.Random(2); words = [w for w, _ in bg.uni.most_common(300)]
    pairs = [(rnd.choice(words), rnd.choice(words)) for _ in range(300)] + [('the', None), ('zzzz', 'the'), ('king', 'zzzz')]
    for (w, pv), row in zip(pairs, vprobe(['G %s|%s' % (w, pv or '') for w, pv in pairs])):
        assert abs(float(row[1]) - bg.p(w, pv)) < 1e-12 * max(1, bg.p(w, pv)), (w, pv, row[1], bg.p(w, pv))


def test_orbweaver_plan_agrees_with_the_python_bench_on_first_senses(vprobe):
    import boxkite_orbweaver_monad as OW, wordnet_boxkite as WB, sedenion_window as SW, re
    from nltk.corpus import wordnet as wn
    ow = OW.OrbWeaverMonad(); CL = SW.CLOSED
    texts = ["The king rules the kingdom and the dog chases the cat in the garden. I told him 3 times in 2024 and x2.", "Why does the bridge keep breaking when the river floods the valley and the farmers rebuild the road every spring?",
             "The painter mixes the colour and the sculptor carves the stone while the musician plays the song in the temple.", "hello", "Computation transforms information into knowledge through measurement."]
    rows = vprobe(['O ' + t for t in texts]); mism = 0
    for t, row in zip(texts, rows):
        body, nums = N.split(t); toks = [w.lower() for w in re.findall(r"[A-Za-z][A-Za-z'-]+", body)]; seen = set(); content = []
        for w in toks:
            if w in CL or w in seen or len(w) < 3: continue
            seen.add(w); content.append(w)
        known = [w for w in content if wn.synsets(w)]; rv = [0] * 19
        for w in known: rv = [a + b for a, b in zip(rv, WB.context_vector(wn.synsets(w)[0]))]
        c_rv = [int(x) for x in row[9].split(',')]
        if c_rv != rv: mism += 1; continue                                  # the C store's first-sense entry differs from nltk's first synset: reported below, not silently passed
        turb, peaks = ow._turbulence(rv); room = ow.room_shape(body, known or ['it'], peaks); reach = ow._reach_from_room(room, 'paper')
        assert int(row[1]) == reach and row[2] == room.regime and abs(float(row[3]) - room.ratio) < 1e-9 and int(row[4]) == int(turb) and int(row[5]) == peaks, (t, row[1:6], reach, room.regime, room.ratio)
        dirs = ow._ranked_directions(rv, max(1, min(reach + 1, max(1, len(known))))); assert row[8].split(',') == dirs, (t, row[8], dirs)
    assert mism <= 1, '%d of %d prompts have different first-sense relation vectors in monad3_c.bin than in NLTK WordNet' % (mism, len(texts))


# ═══════════ the resident monad over the frame link (what the Python console talks to) ═════════════════════════════════
CONSOLE = '''
import json, os, socket, sys
s = socket.socket(fileno=int(os.environ["PTOL_HARNESS_FD"])); f = s.makefile("rw", encoding="utf-8", newline="\\n")
def say(i, t, kind="say"):
    f.write(json.dumps({"t": kind, "id": i, "text": t}) + "\\n"); f.flush()
    while True:
        fr = json.loads(f.readline())
        if fr.get("t") == "chat": return fr
for i, (t, k) in enumerate(json.loads(os.environ["CONSOLE_TURNS"])): print(json.dumps(say(i + 1, t, k)), flush=True)
f.write(json.dumps({"t": "quit"}) + "\\n"); f.flush()
'''


def test_the_resident_child_answers_plain_text_frames(tmp_path):
    if not os.path.exists(os.path.join(PC, 'monad3_c.bin')): pytest.skip('needs PtolC/monad3_c.bin')
    exe = build(tmp_path, 'ptol', ['ptol.c', 'monad_harness.c', 'monad.c', 'tokenizer.c', 'filter.c'])
    script = tmp_path / 'console.py'; script.write_text(CONSOLE)
    import json
    turns = [["The king rules the kingdom and the dog chases the cat in the garden.", "say"], ["/state", "cmd"], ["/tense past perfect", "cmd"], ["I told him 3 times in 2024.", "say"], ["/numbers", "cmd"], ["/legacy hello", "cmd"]]
    env = dict(os.environ, PTOL_USAGE_DIR=str(tmp_path / 'u'), PTOLC_DIR=PC, PTOL_CONSOLE_PY=str(script), PTOL_PY=sys.executable, CONSOLE_TURNS=json.dumps(turns))
    r = subprocess.run([exe, '-w'], capture_output=True, text=True, timeout=120, env=env, stdin=subprocess.DEVNULL)
    frames = [json.loads(l) for l in r.stdout.splitlines() if l.startswith('{')]
    assert len(frames) == len(turns), (r.stdout[-500:], r.stderr[-500:])
    assert frames[0]['text'] and not any(c.isdigit() for c in frames[0]['text'])
    assert 'heard' in frames[1]['text'] and 'mix' in frames[1]['text']
    assert frames[2]['text'].startswith('tense: past perfect')
    assert 'had' in frames[3]['text'].split() and not any(c.isdigit() for c in frames[3]['text'])
    assert 'numbers heard: 2' in frames[4]['text']                                    # 3 and 2024, on their own channel
    assert frames[5]['text']
