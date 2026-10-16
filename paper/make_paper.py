#!/usr/bin/env python3
"""
make_paper.py: builds Forward_Propagation_of_Information.md from template.md, sec17.md and fresh runs of the engine (paper/evidence.py).

Every number that comes from code is taken from a run when this script runs. Numbers that depend on the machine's speed are wrapped in
the marker ⟦…⟧ or sit inside the <!-- TIMING --> block; `--check` ignores those and the date line, and compares everything else:

    ../../PtolemyDesktop/.venv/bin/python make_paper.py            write the paper
    ../../PtolemyDesktop/.venv/bin/python make_paper.py --check    regenerate in memory; exit 1 if the committed text no longer matches

It changes no engine file. (cs-paper-code-conventions §8: generated from the engines, with a --check mode.)
The notebooks under VAPMIP/notebooks/paper/ and VAPMIP/notebooks/c/ must have been built first (build_paper_notebooks.py).
"""
from __future__ import annotations

import datetime
import re
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import evidence as ev                                    # noqa: E402

PLACE = HERE.parent.parent
OUT = HERE / 'Forward_Propagation_of_Information.md'
TEMPLATE = HERE / 'template.md'
SEC17 = HERE / 'sec17.md'


def esc(s: str) -> str:
    return s.replace('|', '\\|').replace('\n', ' ⏎ ')


def md_table(head: list[str], rows: list[list[str]]) -> str:
    out = ['| ' + ' | '.join(head) + ' |', '|' + '---|' * len(head)]
    out += ['| ' + ' | '.join(r) + ' |' for r in rows]
    return '\n'.join(out)


def where_text(rel: str, name: str) -> str:
    loc = ev.where(rel, name)
    path, lines = loc.rsplit(':', 1)
    path = path[3:] if path.startswith('../') else 'VAPMIP/' + path
    return f"{path}:{lines.replace('-', '–')}"


# ── §19: every path named here must exist ────────────────────────────────────────────────────────────
CODE_BY_SECTION = [
    ('§3 The Null Operator', ['ValaQuenta/modules/box_kite/maths.py', 'VAPMIP/scaled_mind_eye_boxkite_kernel_monad.py']),
    ('§4 The store', ['VAPMIP/PtolC/monad3c.h', 'VAPMIP/PtolC/ptolemy.h', 'VAPMIP/PtolC/ptol.c', 'VAPMIP/PtolC/monad.c', 'VAPMIP/PtolC/monad.h', 'VAPMIP/PtolC/monad3_c.bin']),
    ('§5 The question', ['VAPMIP/PtolC/ptol.c']),
    ('§6 Words from ψ', ['VAPMIP/PtolC/ptol.c', 'VAPMIP/PtolC/ptol_layer.py', 'VAPMIP/wordnet_boxkite.py', 'VAPMIP/PtolC/dump_boxkite_bin.c']),
    ('§7 Learning and speaking in the C monad', ['VAPMIP/PtolC/monad.c', 'VAPMIP/PtolC/ptolemy.h']),
    ('§8 The sentence path', ['VAPMIP/PtolC/ptol.c', 'VAPMIP/engine/grammar/ptolc_bridge.py', 'VAPMIP/engine/grammar/generate.py']),
    ('§9 The parser and the harness', ['VAPMIP/PtolC/zork.c', 'VAPMIP/PtolC/zork.h', 'VAPMIP/zork_parser.py', 'VAPMIP/PtolC/monad_harness.c', 'VAPMIP/PtolC/monad_harness.h']),
    ('§10 The geometry', ['VAPMIP/rotary_rerun_monad.py', 'ValaQuenta/modules/box_kite/maths.py']),
    ('§11 The dial', ['VAPMIP/19D_boxkite_context_monad.py']),
    ('§12 The kernel', ['VAPMIP/scaled_mind_eye_boxkite_kernel_monad.py']),
    ('§13 The encounter', ['PtolemyDesktop/ptolemy_console.py', 'VAPMIP/19D_rotary_boxkite_monad.py', 'VAPMIP/ptolemy_monad.py']),
    ('§14 Fault handling and NULL behaviour', ['VAPMIP/rotary_rerun_monad.py']),
    ('§17 Tuning and the surface', ['VAPMIP/monad.py', 'VAPMIP/docs/wiki/Tuning-the-Engine/00_index.md', 'VAPMIP/docs/wiki/Tuning-the-Engine/02b_the_halocline_j_blue_j_red_h_hat_rb.md',
                                    'VAPMIP/docs/wiki/Tuning-the-Engine/06_definition_from_above_the_shadow_cascade.md', 'VAPMIP/docs/wiki/Tuning-the-Engine/09_the_void_named_itself.md',
                                    'VAPMIP/docs/wiki/Tuning-the-Engine/15_the_negative_space_response_equation.md']),
    ('§2 licences and third-party notices', ['VAPMIP/NOTICE', 'VAPMIP/WORDNET_LICENSE.txt', 'VAPMIP/LICENSE', 'VAPMIP/LICENSE-GPL-3.0.txt']),
]
NOTEBOOKS = [
    ('§3', 'VAPMIP/notebooks/paper/17_null_operator_and_hub.ipynb'), ('§4', 'VAPMIP/notebooks/c/08c_ptol_store.ipynb'),
    ('§5', 'VAPMIP/notebooks/c/07c_ptol_projection_and_balance.ipynb'), ('§6', 'VAPMIP/notebooks/c/08c_ptol_store.ipynb'),
    ('§7', 'VAPMIP/notebooks/c/09c_ptol_learning_step.ipynb'),
    ('§8', 'VAPMIP/notebooks/paper/18_ptol_sentence_bridge.ipynb'), ('§9', 'VAPMIP/notebooks/paper/19_parser_tables.ipynb'),
    ('§10', 'VAPMIP/notebooks/tuning_the_engine/phase_25.ipynb'), ('§10', 'VAPMIP/notebooks/tuning_the_engine/phase_39.ipynb'),
    ('§11', 'VAPMIP/notebooks/tuning_the_engine/phase_38.ipynb'), ('§12', 'VAPMIP/notebooks/paper/20_scaled_kernel_fibers.ipynb'),
    ('§13', 'VAPMIP/notebooks/paper/21_scaled_adapter_encounter.ipynb'), ('§14', 'VAPMIP/notebooks/paper/22_fault_ledger_and_null.ipynb'),
    ('§16', 'VAPMIP/notebooks/tuning_the_engine/phase_42.ipynb'),
    ('§17', 'VAPMIP/notebooks/tuning_the_engine/phase_06.ipynb'), ('§17', 'VAPMIP/notebooks/tuning_the_engine/phase_09.ipynb'),
    ('§17', 'VAPMIP/notebooks/tuning_the_engine/phase_15.ipynb'), ('§17', 'VAPMIP/notebooks/tuning_the_engine/phase_02b.ipynb'),
    ('§17', 'VAPMIP/notebooks/10_revised_navier_stokes.ipynb'), ('§17', 'VAPMIP/notebooks/11_language_as_navier_stokes.ipynb'),
]
EVIDENCE = [
    ('the generator, its template and its figure', ['VAPMIP/paper/evidence.py', 'VAPMIP/paper/make_paper.py', 'VAPMIP/paper/template.md', 'VAPMIP/paper/sec17.md', 'VAPMIP/paper/build_pdf.sh',
                                                     'VAPMIP/paper/figures/console_rotary_rerun_boxkite_2026-09-11.png']),
    ('the notebook builders', ['VAPMIP/notebooks/paper/pn.py', 'VAPMIP/notebooks/paper/build_paper_notebooks.py', 'VAPMIP/notebooks/paper/specs_paper.py', 'VAPMIP/notebooks/c/install_c_kernel.sh']),
    ('Tuning the Engine, and its findings roll-up', ['VAPMIP/notebooks/tuning_the_engine/FINDINGS.md', 'VAPMIP/docs/wiki/J_red-J_blue-0_RB-Record.md']),
    ('the name chronology of the Null Operator', ['Ainulindale/wiki/127_names_of_the_null_operator.md']),
    ('scratch evidence (persistent scratchpad)', ['ContextPlease/claude/scratchpad/2026-10-15_vapmip_paper', 'ContextPlease/claude/scratchpad/2026-10-15_null_operator_names']),
    ('the skill that decides how code is shown, and the introductions it was calibrated on', ['ContextPlease/claude/skills/cs-paper-code-conventions/SKILL.md',
                                                                                              'ContextPlease/claude/skills/cs-paper-code-conventions/references/WhitePaperIntroExemplars']),
    ('sources of the public energy figures (copies)', ['ContextPlease/claude/references/VAPMIPPaper', 'VAPMIP/paper/references']),
    ('the ledger of downloaded literature', ['ContextPlease/claude/references/INDEX.md']),
]


def sec19() -> tuple[str, str, str]:
    def chk(p: str) -> str:
        if not (PLACE / p).exists():
            raise SystemExit(f'§19 names a path that does not exist: {p}')
        return f'`{p}`'
    code = '\n'.join(f"- **{sec}:** " + ', '.join(chk(p) for p in paths) for sec, paths in CODE_BY_SECTION)
    nb = '\n'.join(f"- **{sec}:** {chk(p)}" for sec, p in NOTEBOOKS)
    evid = '\n'.join(f"- **{what}:** " + ', '.join(chk(p) for p in paths) for what, paths in EVIDENCE)
    return code, nb, evid


def build() -> str:
    st = ev.engine_state()
    qe = ev.question_and_eyes()
    ic = ev.identities_and_claims()
    nd = ev.near_d_star()
    us = ev.u_shape()
    sf = ev.surface()
    sd = ev.adapter_seeds()
    ad = sd['runs'][0]
    pz = ev.parser()
    sh = ev.store_header()
    nbl = {x['notebook'].split('/notebooks/')[-1]: x for x in ev.notebook_ledgers()}
    sn = ev.store_notebook()
    cc = ev.c_constants()
    kr = ev.kernel_rows()
    nc = ev.null_census()

    tok: dict[str, str] = {}
    tok['DATE'] = datetime.date.today().isoformat()
    tok['HEAD'] = st['git_head']
    tok['PTOLC_LINES'] = f"{st['ptol_c_lines']:,}"
    tok['STORE_BYTES'] = f"{sh['bytes']:,}"
    tok['N_WORDS'], tok['N_ENG'], tok['N_WN'], tok['N_PHON'], tok['NNZ'] = (f"{sh[k]:,}" for k in ('n_words', 'n_eng', 'n_wn', 'n_phon', 'nnz'))
    tok['RAW_WORST'] = f"{qe['raw_worst']:.1e}"
    tok['EYE_WORST'] = f"{qe['eye_worst']:.1e}"
    tok['C07_DIFF'] = f"max |extracted − real| = {ev.c07_diff()}"
    tok['SUM_DEV'] = f"{ic['sum_dev']:.1e}"
    tok['N_RANDOM'] = f"{ic['n_random']:,}"
    tok['PROD_MAX'] = f"{ic['prod_max']:.6f}"
    tok['PROD_MIN6'] = f"{ic['prod_min6']:.3f}"
    tok['PROD_MAX6'] = f"{ic['prod_max6']:.3f}"
    tok['SIG1_MED'], tok['SIG1_MAX'] = f"{ic['sigma1_median']:.3f}", f"{ic['sigma1_max']:.3f}"
    tok['SIG0_MED'], tok['SIG0_MIN'] = f"{ic['sigma0_median']:.3f}", f"{ic['sigma0_min']:.3f}"
    tok['CHANCE_RATE'] = f"{nd['rate']:.2%}"
    tok['U_N'] = str(us['n'])
    tok['U_UPPER'] = str(us['upper'])
    tok['U_ARGMIN'], tok['U_LO'], tok['U_HI'] = f"{us['argmin_med']:.2f}", f"{us['argmin_lo']:.2f}", f"{us['argmin_hi']:.2f}"
    tok['U_CTRL'] = f"{us['ctrl_med']:.2f}"
    tok['C_BETA_SAT'], tok['C_WINDOW_MAX'] = cc['beta_sat'], cc['window_max']

    # notebook ledgers
    def led(rel: str) -> str:
        x = nbl[rel]
        return f"{x['pass']} PASS, {x['fail']} FAIL" + (f", {x['errors']} cell errors" if x['errors'] else '')
    for key, rel in (('NB17', 'paper/17_null_operator_and_hub.ipynb'), ('NB18', 'paper/18_ptol_sentence_bridge.ipynb'), ('NB19', 'paper/19_parser_tables.ipynb'),
                     ('NB20', 'paper/20_scaled_kernel_fibers.ipynb'), ('NB21', 'paper/21_scaled_adapter_encounter.ipynb'), ('NB22', 'paper/22_fault_ledger_and_null.ipynb'),
                     ('NB07C', 'c/07c_ptol_projection_and_balance.ipynb'), ('NB08C', 'c/08c_ptol_store.ipynb')):
        tok[key] = led(rel)

    # tables
    tok['STATE_TABLE'] = md_table(['file', 'sha256 (12 hex)'], [[f'`{f}`', f'`{h}`'] for f, h in st['files'].items()])
    tok['LOOKUP_TABLE'] = md_table(['word', 'found', 'learned idx', 'WordNet idx', 'phonetic idx', 'co-occurrence degree', 'Gamma-Radial'],
                                   [[f'`{w}`', 'yes' if hit == '1' else 'no', eng, wn, ph, deg, g or '—'] for w, hit, eng, wn, ph, deg, g in sn['lookup']])
    tok['COORDS_TABLE'] = md_table(['word', 'slot (of 25,000)', 'E'], [[f'`{w}`', s, e] for w, s, e in sn['coords']])
    tree_c = next((g for w, hit, eng, wn, ph, deg, g in sn['lookup'] if w == 'tree' and g), 'n/a')
    tok['TREE_C'] = f"{float(tree_c):+.6f}" if tree_c != 'n/a' else 'n/a'
    tok['TREE_SENSES'] = '; '.join(f"`{n}` {g:+.6f}" for n, g in ev.tree_senses() if g is not None)
    tok['EYES_TABLE'] = md_table(['prompt', 'chars', 'R (σ=1)', 'C (¾)', 'H (½)', 'O (¼)', 'S (0)', 'Γ at H'],
                                 [[esc(r['prompt']), str(r['len'])] + [f"{r['eyes'][k]:.4f}" for k in 'RCHOS'] + [f"{r['gamma']:+.4f}"] for r in qe['rows']])
    gam = [r['gamma'] for r in qe['rows']]
    tok['GAMMA_MIN'], tok['GAMMA_MAX'] = f"{min(gam):+.2f}", f"{max(gam):+.2f}"
    merged: dict[int, list[int]] = {}
    for k, (ok, n) in ic['mono'].items():
        a = merged.setdefault(min(int(k), 90), [0, 0])
        a[0] += ok
        a[1] += n
    tok['MONO_TABLE'] = md_table(['input length (characters)', 'σ_self rises with the dial', 'fraction'],
                                 [[(f'{k}–{k + 9}' if k < 90 else '90 and over'), f'{ok} of {n}', f'{ok / n:.1%}'] for k, (ok, n) in sorted(merged.items())])
    tok['SURFACE_TABLE'] = md_table(['prompt', '`ptol` (plain)', '`ptol -say` (real HOME)', 'compiled REPL line', 'parser line'],
                                    [[esc(r['prompt']), '`' + esc(r['ptol']) + '`', '`' + esc(r['say']) + '`', '`' + esc(r['repl']) + '`', '`' + esc(r['repl_zork'].replace('[zork] ', '')) + '`'] for r in sf['rows']])
    tok['ADAPTER_TABLE'] = md_table(['prompt', 'kind', 'reply (warm, seed 0)'],
                                    [[esc(w['prompt']), esc(str(w['via'])), '`' + esc(w['reply']) + '`'] for w in ad['warm']])
    tok['ADAPTER_SAME'] = ('The second round returned exactly the replies of the first within the process.' if ad['same'] else 'The second round did NOT return the replies of the first.')
    var = [p for p in sd['per_prompt'] if p['distinct'] > 1]
    tok['SEED_VARIABLE'] = ['none', 'one', 'two', 'three', 'four', 'five', 'six'][len(var)]
    tok['N_RESOLVED'] = str(sum(1 for w in ad['warm'] if w['via'] == 'scaled_mind_eye'))
    tok['KERNEL_TABLE'] = md_table(['strut', 'assessor', 'fixed_point_weight', 'is_zero_divisor', 'windspeed', 'σ_self (kernel split)'],
                                   [[str(r['strut']), str(r['assessor']), f"{r['weight']:.6f}", str(r['zd']), f"{r['wind']:+.4f}", f"{r['sigma_self']:.4f}"] for r in kr])
    tok['HARNESS_COUNTS'] = ev.harness_counts()
    tok['NULL_CENSUS'] = '\n'.join(f"- **{'keeps NULL' if k == 'KEEPS NULL' else 'supplies a value'}:** `{what}` → {esc(ret)}" for k, what, ret in nc)
    cf = pz['conflicts']
    tok['PARSER_FACTS'] = '\n'.join([
        f"- Verbs in the compiled table: **{pz['c_verbs']}**; in the Python table: **{pz['py_verbs']}**. Operators covered: {pz['ops_c']} of 16 (compiled), {pz['ops_py']} of 16 (Python).",
        f"- In the Python table and not the compiled table: **{len(pz['only_py'])}** (" + ', '.join(f'`{v}`' for v in pz['only_py']) + f"); the other way: **{len(pz['only_c'])}**.",
        f"- Shared verbs that map to **different operators: {len(cf)}**: " + '; '.join(f"`{v}` (compiled {c}, Python {p})" for v, c, p, _ in cf) + '.',
        "- Cause: the Python table lists six verbs under two operators each and keeps the last; the compiled table lists each verb once. Five of the six then differ (`ask` agrees). The header of `zork.h` says the table \"mirrors zork_parser.py exactly\"."])
    tok['N_CONFLICTS'], tok['N_ONLY_PY'] = str(len(cf)), str(len(pz['only_py']))
    tok['PARSER_C_N'], tok['PARSER_PY_N'] = str(pz['c_verbs']), str(pz['py_verbs'])
    tok['PARSER_OPS'] = ', '.join(f"{pz['names'][k]} {n}" for k, n in pz['per_op'].items())

    # timing-dependent
    warm = [w['ms'] for w in ad['warm']]
    scaled_uwh = 9.255 * statistics.mean(warm) / 3.6
    say_s = statistics.mean(r['say_ms'] for r in sf['rows']) / 1000
    say_mwh = 9.255 * say_s / 3600 * 1000                     # W × s / 3600 = Wh; × 1000 = mWh
    tok['SCALED_UWH'] = f"⟦{scaled_uwh:.1f}⟧"
    tok['SAY_MWH'] = f"⟦{say_mwh:.0f}⟧"
    trows = [[esc(r['prompt']), f"{r['ptol_ms']:.0f}", f"{r['say_ms'] / 1000:.1f}", f"{r['repl_ms']:.0f}", f"{c['ms']:.1f}", f"{w['ms']:.2f}"]
             for r, c, w in zip(sf['rows'], ad['cold'], ad['warm'])]
    t = md_table(['prompt', '`ptol` ms', '`ptol -say` s', '`ptolemy -r -n` ms (whole process)', 'scaled adapter cold ms', 'scaled adapter warm ms'], trows)
    t += (f"\n\nAdapter: construction {ad['load_s']:.2f} s; the first call of a process also reads WordNet (cold column). `ptol -r` (the sixteen numbers alone) takes about 2 ms. "
          f"Compiled figures are the faster of two runs where two were taken (`-say` once, about 12 s) and include process start; the compiled REPL's per-line cost inside one session is the recorded 28.8 ms over 600 lines.")
    tok['TIMING'] = t

    tok['TTE_TOTALS'] = ev.tte_totals()
    for key, ph in (('P06', '06'), ('P09', '09'), ('P15', '15'), ('P02B', '02b')):
        tok[key] = ev.tte_counts(ph)
    tok['LINEAGE_TABLE'] = md_table(['strut', 'lineage'], [[str(s), l] for s, l in ev.lineage_table()])

    tok['SEC19_CODE'], tok['SEC19_NB'], tok['SEC19_EVID'] = sec19()

    text = TEMPLATE.read_text()
    text = text.replace('@@SEC17@@', SEC17.read_text().strip())
    for k, v in tok.items():
        text = text.replace(f'@@{k}@@', v)
    text = re.sub(r'\{\{w:([^:}]+):(\w+)\}\}', lambda m: where_text(m.group(1), m.group(2)), text)
    left = re.findall(r'@@[A-Z0-9_]+@@', text)
    if left:
        raise SystemExit(f'unfilled tokens: {sorted(set(left))}')
    if '[cite]' in text:
        raise SystemExit('a [cite] marker is still in the text')
    return text


def normalise(t: str) -> str:
    t = re.sub(r'^\*\*Date:\*\* [0-9-]+', '**Date:** DATE', t, flags=re.M)
    t = re.sub(r'<!-- TIMING -->.*?<!-- /TIMING -->', '<!-- TIMING -->', t, flags=re.S)
    t = re.sub(r'⟦[^⟧]*⟧', '⟦⟧', t)
    return t


if __name__ == '__main__':
    text = build()
    if '--check' in sys.argv:
        old = OUT.read_text() if OUT.exists() else ''
        a, b = normalise(old), normalise(text)
        if a == b:
            print('OK: the committed paper matches a fresh run of the engine.')
            sys.exit(0)
        import difflib
        d = list(difflib.unified_diff(a.splitlines(), b.splitlines(), 'committed', 'fresh', lineterm='', n=0))
        print('STALE: committed paper differs from a fresh run:\n' + '\n'.join(d[:40]))
        sys.exit(1)
    OUT.write_text(text)
    print(f'wrote {OUT} ({len(text):,} chars)')
