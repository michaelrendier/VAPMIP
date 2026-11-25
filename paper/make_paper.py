#!/usr/bin/env python3
"""make_paper.py: builds Forward_Propagation_of_Information.md from template.md and fresh runs of the current machinery (paper/evidence.py).   (2026-11-25 rewrite)

Numbers that depend on the machine's speed are wrapped in ⟦…⟧; `--check` ignores those and the date line and compares everything else:

    ../.venv/bin/python make_paper.py            write the paper
    ../.venv/bin/python make_paper.py --check    regenerate in memory; exit 1 if the committed text no longer matches

It changes no engine file.  (cs-paper-code-conventions §8: generated from the engines, with a --check mode; §10: the CS engineering white paper.)
"""
from __future__ import annotations

import datetime
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
import evidence as ev                                    # noqa: E402

OUT = HERE / 'Forward_Propagation_of_Information.md'
TEMPLATE = HERE / 'template.md'
SPECS = ['present', 'past', 'future', 'conditional', 'perfect', 'progressive', 'past perfect', 'past progressive', 'future perfect', 'future progressive',
         'present perfect progressive', 'past perfect progressive', 'imperative', 'base', 'future perfect progressive']
PROMPTS = ["Why does this keep breaking?! I already told you the file was there.", "That makes sense, thanks. Can you show the next step?", "I'm tired. Let's try again slowly.",
           "Hi, I'd like to learn how the Lambert W function connects to the Riemann zeros.", "ok", "WHAT?!", "Oh that's interesting, so d* is the boundary. Show me.", "Great, that worked. I think I get it now."]
CHAT = ["The king rules the kingdom and the dog chases the cat in the garden. I told him 3 times in 2024.", "/state", "/plan", "/audit", "Why does this keep breaking?! I already told you the file was there.",
        "/tense past perfect", "The painter mixes the colour and the sculptor carves the stone.", "/tense auto", "/trace", "/drift"]
PYTURNS = ["The king rules the kingdom and the dog chases the cat in the garden. I told him 3 times in 2024.", "Why does this keep breaking?! I already told you the file was there."]


def md_table(head, rows):
    return '\n'.join(['| ' + ' | '.join(head) + ' |', '|' + '---|' * len(head)] + ['| ' + ' | '.join(str(c).replace('|', '\\|') for c in r) + ' |' for r in rows])


class Numbering:
    n = 0


def lst(rel: str, quals: list[str], caption: str) -> str:
    Numbering.n += 1; parts, locs = [], []
    for q in quals:
        src, loc = ev.listing(rel, q); parts.append(src); locs.append(loc)
    where = ' ; '.join(f'`VAPMIP/{l}`' for l in locs)
    return f"**Listing {Numbering.n} — {caption}** ({where}; verbatim, docstring removed)\n\n```python\n" + '\n\n'.join(parts) + "\n```"


def tr(stmts, env=None):
    return '```\n' + ev.transcript(stmts, env) + '\n```'


def tenses_table() -> str:
    sys.path.insert(0, str(ev.ROOT)); import lyndon_conjugation as LC
    c = ev.c_probe(['V %s|see|0|3' % sp for sp in SPECS]); rows = []
    for sp, row in zip(SPECS, c):
        fr = LC.inflection_frame(sp, 'see'); py = ' '.join(fr['surface']); cs = row[1]
        rows.append([sp, ' · '.join(LC.factors(sp)), py, cs, f"{fr['tense']}/{fr['conj']}", '✓' if (py == cs and row[2] == fr['tense'] and row[3] == fr['conj']) else '✗'])
    return md_table(['tense', 'Lyndon factors', 'Python', 'C', 'marker tense/conj', 'same'], rows)


def senses_table() -> str:
    code = '''
import json, responder as R, sedenion_window as SW, weave_cycle as WC
from nltk.corpus import wordnet as wn
w = SW.SedenionWindow(R.default_bigram())
cases = {"bank": ["river", "water", "fish"], "run": ["program", "code", "computer"], "bat": ["ball", "game", "pitcher"], "light": ["weight", "heavy", "feather"], "plant": ["factory", "workers", "machinery"], "cell": ["prison", "jail", "guard"]}
rows = []
for k, ctx in cases.items():
    r = WC.word_web(w, k, ctx); rows.append([k, " ".join(ctx), r["sense"], wn.synsets(k)[0].name()])
print(json.dumps(rows))
'''
    out = ev.run([ev.PY, '-c', code]).stdout.strip().splitlines()[-1]
    rows = json.loads(out)
    return md_table(['word', 'context given', 'Python word web (sense)', 'first synset (what the C reads)', 'same'], [r + ['✓' if r[2] == r[3] else '✗'] for r in rows])


def meter_table() -> str:
    code = '''
import json, numpy as np, sys, os
sys.path.insert(0, os.path.join(os.getcwd(), "Currentwork", "UserState"))
from prompt_to_state import PromptToState
full = PromptToState(); use = PromptToState()
use.raw_dose = lambda t: (np.clip(use.mdl.predict(use.vec.transform([t]))[0], 0, 1) * 4.5, np.zeros(14)); use.continuation = lambda t: (np.zeros(14), 0.0); use.mask_aspect = lambda t: t
NT = full.__class__.__mro__ and ["OPI-","OPI+","GLU-","GLU+","GABA-","GABA+","DA-","DA+","5HT-","5HT+","NE-","NE+","OXT-","OXT+"]
rows = []
for t in json.loads(sys.stdin.read()):
    a = full.dose(t)[0]; b = use.dose(t)[0]; d = np.abs(a - b); k = int(d.argmax()); rows.append([t[:46] + ("…" if len(t) > 46 else ""), round(float(d.max()), 2), NT[k]])
print(json.dumps(rows))
'''
    out = ev.run([ev.PY, '-c', code], stdin=json.dumps(PROMPTS)).stdout.strip().splitlines()[-1]
    return md_table(['prompt', 'largest |full − usage-only| (dose units, 0..9)', 'at pole'], json.loads(out))


def blocks() -> dict:
    ev.build_c(); sz = ev.sizes(); s = ev.suite(); ms = ev.c_latency(40); b: dict[str, str] = {}
    b['SUITE_PASSED'] = str(s['passed']); b['PARITY'] = str(s['parity']); b['C_MS'] = f'{ms:.1f}'
    b['MONAD3_MB'], b['LEX_MB'], b['US_MB'] = str(sz['monad3_mb']), str(sz['voice_lex_mb']), str(sz['user_state_mb'])
    b['VOICE_LINES'], b['EARS_LINES'], b['PY_LINES'] = f"{sz['ptol_voice_lines']:,}", f"{sz['harness_ears_lines']:,}", f"{sum(sz['py_lines'].values()):,}"
    b['LOC_C_SPLIT'] = ev.cfunc('mh_split_numbers', 'monad_harness.c')
    src, loc = ev.listing('sedenion_window.py', 'SedenionWindow._pick'); b['PICK_LINES'] = str(src.count('\n') + 1); b['LOC_PICK'] = 'VAPMIP/' + loc
    b['L_split'] = lst('numeric.py', ['split'], 'numbers leave before any word is read (`numeric.split`)')
    b['L_pword'] = lst('Currentwork/UserState/vocab_store.py', ['UsageStore.p_word'], 'the speaker\'s usage as a probability (`UsageStore.p_word`)')
    b['L_drift'] = lst('bw_drift.py', ['BWDrift.update'], 'the Broca–Wernicke drift step (`BWDrift.update`)')
    b['L_observe'] = lst('state_repass.py', ['StateRepass.observe'], 'the speaker\'s state: read, heal, mix, cancel (`StateRepass.observe`)')
    b['L_webstep'] = lst('weave_cycle.py', ['web_step'], 'the one orbweaver step (`weave_cycle.web_step`)')
    b['L_conj'] = lst('lyndon_conjugation.py', ['verb_group', 'conjugates'], 'the verb group as a Lyndon factor list (`verb_group`, `conjugates`)')
    b['L_lemn'] = lst('tenseplan.py', ['lemniscate_tense'], 'tense from the lemniscate station (`tenseplan.lemniscate_tense`)')
    b['T_numeric'] = tr(['import numeric', 'numeric.split("I told you 3 times, 2.5% of $1,200, x2, version 3.10.3")', '[(n.text, n.kind, n.value) for n in numeric.split("the 4th, -7 and 1,000,000")[1]]'])
    b['T_usage'] = tr(['import tempfile, conversation_usage as CU', 'cu = CU.ConversationUsage(tempfile.mkdtemp())', 'cu.store.confidence()', "round(cu.bits_per_word('the king reads the book'), 3)",
                       "cu.hear('The king rules the kingdom and the queen reads the book. I told him 3 times.', 'external', 'p1') is None", 'cu.store.n_obs, round(cu.store.confidence(), 4), cu.numbers.n',
                       "round(cu.bits_per_word('the king reads the book'), 3)"])
    b['T_drift'] = tr(['import bw_drift', 'd = bw_drift.BWDrift()', "[(w, b, round(r['delta'], 3), r['active'], round(r['bw_correction'], 3)) for w, b in [(9.0, 9.5), (9.0, 14.0), (9.0, 11.0), (9.0, 9.4), (14.0, 9.0)] for r in [d.update(w, b)]]"])
    b['T_state'] = tr(['import neuro_recipes as NR, state_repass as SR', 'from prompt_to_state import PromptToState', 'st = SR.StateRepass(PromptToState())',
                       "st.observe('Why does this keep breaking?! I already told you the file was there.', fill=16)", 'st.heard_tone(), st.trajectory(4)',
                       "st.observe('Why does this keep breaking?! I already told you the file was there.', fill=9)['k_eff']"])
    b['T_webstep'] = tr(['import weave_cycle as WC', "WC.web_step('sentence', {'a': 9, 'b': 1, 'c': 1}, lambda: ('b', {'b': 1.0}))", "WC.web_step('sentence', {'a': 3, 'b': 3, 'c': 2}, lambda: ('c', {'c': 9, 'a': 1}))",
                         "WC.web_step('sentence', {'a': 3, 'b': 3, 'c': 2}, lambda: ('c', {'c': 3, 'a': 3, 'b': 3}))['reversed']"])
    b['T_conj'] = tr(['import lyndon_conjugation as LC', "[g['word'] for g in LC.conjugates('see', 'future perfect progressive')]", "LC.factors('past perfect progressive'), LC.verb_group('past perfect progressive')",
                      "LC.gcd('past perfect', 'past progressive') == LC.verb_group('past')", "LC.inflection_frame('past perfect', 'walk')['surface']"])
    b['T_orb'] = tr(['import sedenion_window as SW, responder as R, scaled_boxkite_orbweaver_monad as S', "t = 'The painter mixes the colour and the sculptor carves the stone while the musician plays the song in the temple.'",
                     'w = SW.SedenionWindow(R.default_bigram(), web=True); w.read(t)', 'm = S.ScaledOrbWeaverMonad(w); c = m.compose(t, scale=3.0, max_pieces=8)', 'c.text',
                     "c.plan['tenses'], c.plan['directions'], c.plan['turbulent']", 'all(m.audit(c).values())', "c2 = m.compose('I told him 3 times in 2024 and x2 that the king rules the kingdom.'); [n.text for n in c2.numbers], 'digit' if any(ch.isdigit() for ch in c2.text) else 'no digit in the reply'"])
    b['T_cchat'] = '```\n' + '\n'.join(f'> {q}\n{a}' for q, a in ev.c_chat(CHAT)) + '\n```'
    b['T_pyconv'] = '```\n' + ev.py_conversation(PYTURNS) + '\n```'
    b['TABLE_TENSES'] = tenses_table(); b['TABLE_SENSES'] = senses_table(); b['TABLE_METER'] = meter_table()
    b['TABLE_SUITE'] = md_table(['check', 'result'], [['tests in `VAPMIP/tests/`', f"{s['passed']} passed, {s['failed']} failed"], ['of which C ↔ Python parity (`tests/test_c_parity.py`)', str(s['parity'])], ['flow-chart names exist in the C (`tests/test_flowcharts.py`)', '2']])
    tte = sorted(int(m.group(1)) for p in (ev.ROOT / 'docs/wiki/Tuning-the-Engine').iterdir() if (m := re.match(r'(\d+)_', p.name))); b['TTE_LAST'] = str(tte[-1])
    return b


def build() -> str:
    text = TEMPLATE.read_text(encoding='utf-8'); b = blocks()
    b['DATE'] = datetime.date.today().isoformat(); b['HEAD'] = ev.git_head()
    for k, v in b.items(): text = text.replace('@@' + k + '@@', v)
    left = sorted(set(re.findall(r'@@[A-Za-z0-9_]+@@', text)))
    assert not left, left
    for n in ('monad_flow', 'harness_flow'): shutil.copyfile(ev.ROOT / 'docs' / 'flowcharts' / f'{n}.png', HERE / 'figures' / f'{n}.png')
    return text


def norm(t: str) -> str:
    t = re.sub(r'⟦[^⟧]*⟧', '⟦⟧', t); t = re.sub(r'\*\*Date:\*\* \S+', '**Date:** D', t); return re.sub(r'commit `[0-9a-f]+`', 'commit `H`', t)


if __name__ == '__main__':
    text = build()
    if '--check' in sys.argv:
        old = OUT.read_text(encoding='utf-8'); ok = norm(old) == norm(text)
        print('check:', 'OK' if ok else 'MISMATCH'); sys.exit(0 if ok else 1)
    OUT.write_text(text, encoding='utf-8'); print('wrote', OUT.name, len(text.splitlines()), 'lines')
