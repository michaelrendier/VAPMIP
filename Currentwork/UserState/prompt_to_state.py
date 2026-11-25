#!/usr/bin/env python3
"""prompt_to_state.py -- PROTOTYPE: Prompt > NLP > dose > user state (solution) > 15-layer strip > suggested move.   One user (Cody).

No transformer is loaded (memory; and the cheap pathway is the goal).  Meters used per prompt:
  usage   one sparse linear map (word+bigram tf-idf ridge, usage_model.joblib) -> 14 pole levels
  lexical VADER, arousal features, profanity, dialogue act (NLTK nps_chat Naive Bayes), stance cues  (user_state.score, models off)
The dose is the mean of the two (usage and lexical); their disagreement per pole is the UNCERTAINTY (spread) shown with the state.
The state is `Solution` (solution_tests.py): C1V1 + C2V2 = C3(V1+V2), Vmax caps memory; the cold prompt assigns.
Nuance is NOT modelled here: it is learned over time (Cody, 2026-11-24).  The spread is the hook it will use.

    python3 prompt_to_state.py            interactive: type prompts, blank line quits; 'reset' starts cold
    python3 prompt_to_state.py --demo     scripted conversation
    python3 prompt_to_state.py --json f   also append one JSON line per turn to f
"""
import json, os, re, sys, time
import numpy as np
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', '..')); sys.path.insert(0, H)
import joblib
from user_state import NT, RawMeters, score, net, scalar, arousal_features, empath_counts
from solution_tests import Solution, TABLE, B, vec14, mix_labels, cos, DSM_ROWS, LIGHT_OF
from recipes_v2 import LIB2, R as _R
RV2 = {k: v for k, v in _R(LIB2).items() if np.linalg.norm(v) > 0.05}

LAYERS = [(a, 0) for a in reversed(NT)] + [(a, 1) for a in NT]          # dark V I B G Y O R | light R O Y G B I V  (cursor between)
RGB = {'OPI': (220, 40, 40), 'GLU': (240, 130, 30), 'GABA': (230, 210, 40), 'DA': (50, 190, 70), '5HT': (50, 110, 230), 'NE': (90, 60, 200), 'OXT': (160, 70, 210)}
pname = lambda i: f"{NT[i // 2]}{'-' if i % 2 == 0 else '+'}"
THR_ON, THR_OFF, BAND = 2.5, 1.2, 1.5

class PromptToState:
    def __init__(self, vmax=8.0):
        self.rm = RawMeters(load_models=False)
        self.vec, self.mdl = joblib.load(os.path.join(H, 'usage_model.joblib'))
        self.sol = Solution(vmax=vmax); self.n = 0; self.on = False; self.prev_dose = None
        self.gain, self.base = self.calibration()

    def raw_dose(self, text):
        raw = {'text': text, 'vader': self.rm.vader.polarity_scores(text), 'act': self.rm.act(text),
               'feat': arousal_features(text), 'empath': empath_counts(text)}
        lex = score(raw, use=('vader', 'arousal', 'profanity', 'act', 'empath', 'stance'), irony=False)
        a = vec14(lex); b = np.clip(self.mdl.predict(self.vec.transform([text]))[0], 0, 1)
        return 9.0 * (a + b) / 2.0, 9.0 * np.abs(a - b) / 2.0

    def calibration(self):
        """The meters are quiet (a clear emotion reads ~0.3).  gain = 8 / p98 of each pole over 1,200 corpus prompts (goemotions, nps_chat, proj_chat; capped at 6);
        baseline = the median calibrated reading of those prompts (the typical prompt), not a hand-set recipe.  Cached in calib.json."""
        f = os.path.join(H, 'calib.json')
        if os.path.exists(f):
            j = json.load(open(f)); return np.array(j['gain']), np.array(j['base'])
        import random; random.seed(7); rows = [json.loads(l) for l in open(os.path.join(H, 'corpus.jsonl'))]; txt = []
        for src in ('goemotions', 'nps_chat', 'proj_chat'):
            t = [r['text'] for r in rows if r['source'] == src]; random.shuffle(t); txt += t[:400]
        D = np.array([self.raw_dose(t)[0] for t in txt])
        gain = np.minimum(6.0, 8.0 / np.maximum(np.percentile(D, 98, axis=0), 1e-6)); base = np.median(D * gain, axis=0)
        json.dump({'gain': gain.tolist(), 'base': base.tolist(), 'n': len(txt)}, open(f, 'w'))
        return gain, base

    CONT = [(re.compile(r"\bkee?ps?\s+(on\s+)?(?=\w+ing\b)|\bkept\s+(?=\w+ing\b)", re.I), 1.0), (re.compile(r"\bagain\b|\bstill\b|\banymore\b|\bevery\s+(single\s+)?(time|damn|day)\b|\bhow many times\b", re.I), 0.7),
            (re.compile(r"\b(\d+|two|three|four|five|ten|many|several|hundred|thousand)\s+times\b|\balways\b|\bnever\b|\bcontinu\w+\b", re.I), 0.7)]
    def continuation(self, text):
        """Aspect cues: something that keeps happening (keep + -ing, again, still, every time, N times, always/never).  A repeated problem is what frustration is made of
        (Cody, 2026-11-24): dark dose on 5HT-, GABA-, NE-; two hits at most."""
        hits = min(2.0, sum(w for rx, w in self.CONT if rx.search(text)))
        comp = self.rm.vader.polarity_scores(text)['compound']      # the aspect word takes its valence from the predicate: 'keep breaking' is a problem, 'keep going' is not
        hits *= 2.0 if comp <= -0.2 else (1.0 if comp < 0.2 else 0.0)
        d = np.zeros(14); d[2 * NT.index('5HT')] = 1.0 * hits; d[2 * NT.index('GABA')] = 0.8 * hits; d[2 * NT.index('NE')] = 0.5 * hits
        return d, hits

    def dose(self, text):
        """A long text is read sentence by sentence and averaged by length (one dose, not a saturated sum); short text is one reading.  Continuation cues add to it."""
        ss = [x for x in re.split(r'(?<=[.?!])\s+|\.\.\.+', text) if len(x.strip()) > 3]
        if len(ss) > 3:
            parts = [self.dose1(x) for x in ss]; wt = np.array([max(1, len(x.split())) for x in ss], float); wt /= wt.sum()
            d = sum(w * p[0] for w, p in zip(wt, parts)); sp = sum(w * p[1] for w, p in zip(wt, parts))
        else: d, sp = self.dose1(text)
        c, _ = self.continuation(text); return np.minimum(9.0, d + c), sp

    def mask_aspect(self, text):
        """The aspect words are scored once, by the continuation channel; the usage model never sees them (it reads 'keep going', 'always', 'still' as ordinary words)."""
        for rx, _ in self.CONT: text = rx.sub(' ', text)
        return text

    def dose1(self, text):
        """text -> (dose 14 in 0..9 after calibration, spread 14)."""
        d, sp = self.raw_dose(self.mask_aspect(text)); return np.minimum(9.0, d * self.gain), np.minimum(9.0, sp * self.gain)

    def turn(self, text):
        t0 = time.perf_counter()
        d, spread = self.dose(text)
        words = len(re.findall(r"[A-Za-z']+", text)); v = float(min(3.0, max(0.5, words / 25.0)))   # longer prompt = more volume
        incoming_jump = (self.sol.c is not None) and bool((d[0::2] - self.sol.c[0::2]).max() >= 4 and d[0::2].max() >= 5)
        c = self.sol.add(d, v); self.n += 1
        e = c - self.base
        ranked = sorted(((cos(np.maximum(e, 0), RV2[k]), k) for k in RV2), reverse=True)[:3]          # candidates, not a unique decomposition (R1: under-determined)
        syn = ranked[0] if np.linalg.norm(np.maximum(e, 0)) >= 2.5 and ranked[0][0] >= 0.6 else (0.0, 'none')
        self.ranked = [(k, round(c_, 2)) for c_, k in ranked]
        mx = float(np.max(np.abs(e))); self.on = (mx > THR_ON) or (self.on and mx > THR_OFF)
        move = self.move(c, e, incoming_jump)
        return dict(n=self.n, text=text, dose=d.round(1).tolist(), conc=c.round(2).tolist(), spread=spread.round(1).tolist(), volume=round(self.sol.V, 2),
                    e0=float(np.tanh(3 * net_of(c))), syndrome=(syn[1], round(syn[0], 2)), move=move, jump=incoming_jump, candidates=self.ranked, ms=round((time.perf_counter() - t0) * 1e3, 1))

    def move(self, c, e, jump):
        if jump and (c[0::2] - self.base[0::2]).max() > 1.5: return 'hold: abrupt rise; add baseline volume, no new solute (calm)'
        if not self.on: return 'none (inside the learning band)'
        elev = [p for p in np.where(e > BAND)[0] if p % 2 == 0]; depl = np.where(e < -BAND)[0]; m = []
        for p in elev:
            m.append(f'{pname(p)} high: ' + (f'neutralise with {NT[p // 2]}+' if p % 2 == 0 else 'dilute'))
        for p in depl:
            if p % 2 == 1: m.append(f'{pname(p)} low: ' + ('persuade' if NT[p // 2] in ('DA', 'GLU') else 'reassure'))
        return '; '.join(m) or 'none'

def net_of(c):
    return (c[1::2] - c[0::2]).sum() / (9.0 * 7)

def strip(c, spread=None):
    """15 layers: dark V I B G Y O R, cursor, light R O Y G B I V.  Block height = level 0..9, colour = the neurotransmitter, '?' marks spread >= 2."""
    bars = ' ▁▂▃▄▅▆▇█'; out = []
    def cell(i):
        a = NT[i // 2]; lv = int(round(min(9, max(0, c[i])))); r, g, b = RGB[a]
        k = 0.35 + 0.65 * lv / 9; ch = bars[min(8, lv)] if lv else '·'
        return f'\x1b[38;2;{int(r * k)};{int(g * k)};{int(b * k)}m{ch}\x1b[0m'
    dark = [2 * NT.index(a) for a in reversed(NT)]; light = [2 * NT.index(a) + 1 for a in NT]
    return ''.join(cell(i) for i in dark) + '│' + ''.join(cell(i) for i in light)

def show(r, color=True, BASE=None):
    s = strip(r['conc']); s = s if color else re.sub(r'\x1b\[[0-9;]*m', '', s)
    top = sorted(range(14), key=lambda i: -abs(r['conc'][i] - BASE[i]))[:3]
    dev = ', '.join(f"{pname(i)} {r['conc'][i]:.1f}({r['conc'][i] - BASE[i]:+.1f}±{r['spread'][i]:.1f})" for i in top)
    print(f"  {s}  e0 {r['e0']:+.2f}  vol {r['volume']}  {r['ms']} ms\n  largest from baseline: {dev}\n  candidates: {', '.join(f'{k} {c}' for k, c in r['candidates'])}\n  move: {r['move']}", flush=True)

DEMO = ["Hi, I'd like to learn how the Lambert W function connects to the Riemann zeros.",
        "That makes sense, thanks. Can you show the next step?",
        "Why does this keep breaking?! I already told you the file was there.",
        "This is fucking useless, I told you three times, nothing works.",
        "OK. I'm sorry. I'm tired. Let's just try again slowly.",
        "Oh that's interesting, so d* is the boundary. Show me.",
        "Great, that worked. I think I get it now."]

if __name__ == '__main__':
    P = PromptToState(); log = open(sys.argv[sys.argv.index('--json') + 1], 'a') if '--json' in sys.argv else None
    print('legend: dark V I B G Y O R │ light R O Y G B I V   (height = level 0-9; colour = neurotransmitter; baseline = white recipe)', flush=True)
    src = iter(DEMO) if '--demo' in sys.argv else None
    while True:
        try: t = next(src) if src else input('\n> ')
        except (StopIteration, EOFError): break
        if not t.strip(): break
        if t.strip() == 'reset': P = PromptToState(); print('  cold start'); continue
        if src: print(f'\n> {t}')
        r = P.turn(t); show(r, BASE=P.base)
        if log: log.write(json.dumps(r) + '\n'); log.flush()
