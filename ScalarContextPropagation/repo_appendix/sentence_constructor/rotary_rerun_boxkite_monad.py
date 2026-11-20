#!/usr/bin/env python3
"""rotary_rerun_boxkite_monad.py — testing internal eyes / external eyes as
one Monad, against real content: the sedenion box-kite algebra AND the
WordNet-driven context composter, fused, not layered.

Cody, 2026-08-25 — the design this file tests, precisely:

  "the internal eyes are only necessary for the internal visual space...the
  external eyes are for the concrete structured reality...(in this
  methodology, the rendering and interacting with external data is paper's
  hands exactly)...the way in which the Mind's Eye interacts with the
  world...to be able to think about whatever session topic, project files,
  computer state etc...remember we don't need whole lots of separate
  layers...all doing work together if the monad does literally all the
  work."

So this file does NOT build a third Eye/Hands pair. `rotary_rerun_monad.py`
already has the real ones — `MindsEye` (reads, snapshot, all-at-once,
never emits, never renders, never touches anything external — the
INTERNAL visual space) and `PapersHands` (writes, ordered emission, ONE
relationship at a time — and per this session's clarification, rendering
and external interaction belong here too, not on some separate output
object). Those are reused directly. `RotaryBoxKiteMonad` below is the one
Monad that holds both and does the work; it does not reimplement them and
does not spin up a second Eye/Hands thread pair alongside them (that would
be exactly the "lots of separate layers" this was a caution against).

THE COMPOSTER, validated against existing code, not just intuition:
`sentence_context.py`'s `root_vector` (individual per-word context_vectors
componentwise-summed into one sentence root) is the SAME operation as
`rotary_rerun_monad.py`'s `Reading.summed_with()` — "product — componentwise
SUM. Vector addition of the magnitudes" — just run at 19 WordNet-relation
dimensions instead of 7 box-kite-strut dimensions. "Composter" is a good
conceptual name for what happens (individual leaf identity genuinely merges
— confirmed by the word-salad order-independence test in Phase 32 — the
same way composting loses individual-leaf identity into one substrate); the
codebase's own precise technical name for the operation is `summed`,
alongside `shared` (gcd/min — the same move `compare_context`'s `shared`
field already makes) and `combined` (lcm/max, not yet built here).

WHAT THIS FILE ACTUALLY TESTS, honestly, with a control:

Two independently-built systems exist in this project — the sedenion/
box-kite algebra (rotary_rerun_monad.py, real, tested, `7:7:7`) and the
WordNet relational-context composter (wordnet_boxkite.py / sentence_
context.py, real, tested, Phase 31/32). They have never been run against
the same input before. This file wires them together and asks a real,
falsifiable question: does a WordNet-context-generated response share MORE
box-kite struts (algebraic proximity, via cam_encode) with its own input
than an unrelated control text does? Measured below, not assumed.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

from rotary_rerun_monad import (
    BoxKite, BoxKiteUnavailable, MindsEye, PapersHands,
    Ledger, Relation, Status, Fault,
)
from monad import cam_encode
from sentence_context import build_sentence_context, neighborhood_corpus, nearest_synsets
from wordnet_boxkite import RELATION_METHODS, context_vector
from ptolemy_monad import infer_direction, MindsEyeRepass

# This session's pipeline, folded in additively (v5.1). Each import is
# guarded at call time; if the module or its data is absent the Monad
# falls back to the nearest_synsets path it always had.
try:
    from constructor import construct as _construct
except Exception:                                   # pragma: no cover
    _construct = None
try:
    import context_pruner as _pruner
except Exception:                                   # pragma: no cover
    _pruner = None
try:
    import monad_combine as _mc
    from monad_english_io import hear as _hear
except Exception:                                   # pragma: no cover
    _mc = None
    _hear = None
from nltk.corpus import wordnet as _wn


# ── sentence structure — a real, honestly-scoped template layer, not a
# claimed NLG system. `infer_direction` (ptolemy_monad.py) already reads
# which WordNet relation dominates the combined sentence context; each
# direction gets one grammatical frame, filled from the SAME nearest-
# context candidate words already generated. This is what turns a bag of
# words ('generator function large integer mathematics motor') into
# something with actual clause structure ('it relates to generator.') —
# genuinely simple, and named as exactly that, not oversold. ─────────────

_SENTENCE_TEMPLATES: Dict[str, str] = {
    'classify':      'this is a kind of {0}.',
    'enumerate':      'it includes {0}, {1}, and {2}.',
    'decompose':      'it is made of {0} and {1}.',
    'situate':        'it is part of {0}.',
    'characterize':   'it is marked by {0}.',
    'explain':        'it happens because of {0}.',
    'imply':          'it leads to {0}.',
    'associate':      'it relates to {0}.',
    'compare':        'it resembles {0}.',
    'contextualize':  'it belongs to the domain of {0}.',
    'localize':       'it is found in {0}.',
    'register':       'it is used in {0}.',
    'observe':        '{0}.',
}


def assemble_sentence(direction: str, words_out: List[str]) -> str:
    """Fill `direction`'s template from `words_out` (already ranked nearest
    to the sentence root — see sentence_context.nearest_synsets). Pads by
    repeating the last word rather than crashing when a template needs more
    slots than were found; never claims grammar it doesn't have."""
    if not words_out:
        return '(no candidates found)'
    template = _SENTENCE_TEMPLATES.get(direction, '{0}.')
    n_slots = template.count('{')
    fillers = list(words_out)
    while len(fillers) < n_slots:
        fillers.append(fillers[-1])
    return template.format(*fillers[:n_slots])


@dataclass
class Encounter:
    """One process_input() call's full record — internal read, external
    write, and the cross-check between the two independently-built systems.
    Nothing is dropped, same discipline as rotary_rerun_monad's Relation."""
    text: str
    response: str
    direction: str
    words_out: List[str]               # raw ranked candidates, before templating
    root_vector: List[int]
    snapshot: Dict[str, Any]           # MindsEye's internal-eyes read (input)
    snapshot_out: Dict[str, Any]       # same read, taken on the response
    pathways: List[str]                # PapersHands' external-eyes emission
    lit_struts_in: List[int]
    lit_struts_out: List[int]
    shared_struts: List[int]
    selector: str = 'nearest_synsets'  # 'constructor' | 'nearest_synsets' (fallback)
    pruned: Dict[str, Any] = field(default_factory=dict)   # context_pruner result
    repass: Dict[str, Any] = field(default_factory=dict)   # Mind's Eye recursive repass


class RotaryBoxKiteMonad:
    """One Monad. Two real faces already built elsewhere, reused, not
    reinvented. `MindsEye` is the internal visual space — it reads the
    Monad's own sentence-field snapshot and never touches anything outside
    it. `PapersHands` is where rendering AND external interaction live —
    ordered emission, and (per this session) `harness.present()`/KVM belong
    here too, not on a separate output object."""

    def __init__(self, harness: Optional[Any] = None) -> None:
        self.harness = harness
        try:
            self._eye_obj = MindsEye()
            self._hands_obj = PapersHands()
            self.box_kite: Optional[BoxKite] = BoxKite.between(
                self._eye_obj, self._hands_obj)
            self._kite_error: Optional[str] = None
        except BoxKiteUnavailable as exc:
            # Never silently degrade to a confident wrong answer — recorded,
            # not hidden, same rule this whole project uses for UNTESTED.
            self._eye_obj = MindsEye()
            self._hands_obj = PapersHands()
            self.box_kite = None
            self._kite_error = str(exc)

        # v5.1 pipeline state — tunables + the combined store (resident).
        self.topic: Optional[str] = None      # narrows the basin (monad_<topic>.bin)
        self.register: float = 0.0            # 0 = conjugate, 1 = matched
        self.store = None                     # monad_combine.CombinedMonad
        self._store_error: Optional[str] = None
        if _mc is not None:
            try:
                self.store = _mc.read()
            except Exception as exc:          # recorded, not hidden
                self._store_error = str(exc)

    def attach_harness(self, harness: Any) -> None:
        self.harness = harness

    # ── basic search / browse — bare-monad minimum, harness supersedes ────
    # Bare: the Monad does the ridiculously small number of ops it needs to
    # learn on its own — `search()` just opens the default browser, and
    # `browse_observe()` does a minimal fetch → strip → learn into its OWN
    # field, guarded by the RAM + ½·RAM-swap ceiling so it never overwhelms
    # the host. Inside the harness both delegate — the harness is the central
    # acquisition/distribution bus and dedups repeat operations.
    #
    # KVM tie-in (deferred, monad note): when bare and with no BrowserWindow,
    # poll the focused browser URL (Tesla/KVM.py) and feed it to
    # browse_observe() — the Monad's eyes without a window, a handful of ops
    # per page.

    def _governor(self):
        g = getattr(self, '_gov', None)
        if g is None:
            try:
                from monad_bus import ResourceGovernor
                g = ResourceGovernor()
            except Exception:            # noqa: BLE001 — warn-not-fault
                g = False
            self._gov = g
        return g or None

    def search(self, query: str, engine: str = 'ddg'):
        """Harnessed → the harness owns acquisition (dedup). Bare → open the
        default browser (xdg-open via webbrowser)."""
        if self.harness is not None and hasattr(self.harness, 'search'):
            return self.harness.search(query, engine=engine)
        try:
            import webbrowser
            from monad_browse import search_url
            u = search_url(query, engine)
            webbrowser.open(u)
            return {'ok': True, 'opened': u, 'via': 'default-browser'}
        except Exception as e:          # noqa: BLE001
            return {'ok': False, 'error': str(e)}

    def browse_observe(self, url: str):
        """Harnessed → delegate. Bare → minimal fetch, ceiling-checked, strip,
        learn into this Monad's own combined store. Never raises."""
        if self.harness is not None and hasattr(self.harness, 'browse'):
            return self.harness.browse(url)
        try:
            from monad_browse import fetch, strip_html, estimate_ram
        except Exception as e:          # noqa: BLE001
            return {'ok': False, 'error': f'monad_browse: {e}'}
        f = fetch(url)
        if f.status == 0 or f.status >= 400:
            return {'ok': False, 'status': f.status, 'error': f.error}
        gov = self._governor()
        is_html = 'html' in (f.content_type or '').lower() or not f.content_type
        if gov is not None and not gov.headroom_ok(estimate_ram(f.nbytes, is_html)):
            return {'ok': False, 'error': 'memory ceiling', 'nbytes': f.nbytes}
        prose = strip_html(f.body, f.content_type, f.url_final)
        n = 0
        if _hear is not None and self.store is not None and prose:
            try:
                _hear(self.store.english, prose, echo=0)
                n = len(prose.split())
            except Exception:          # noqa: BLE001
                pass
        return {'ok': True, 'url': f.url_final, 'nbytes': f.nbytes, 'words': n}

    def checkpoint(self, also_c: bool = False) -> Optional[str]:
        """Persist the combined store iff mutated. The sedenion WINDOW owns
        calling this — on its interval and on exit."""
        if self.store is None:
            return None
        return self.store.checkpoint(also_c=also_c)

    # ── Mind's Eye: internal visual space only — no render, no interact ────

    def look_inward(self, text: str) -> Tuple[List[float], Dict[str, Any]]:
        """A snapshot of the Monad's OWN field, produced from `text` via
        `cam_encode` (monad.py) — this is how the Eye 'thinks about' a
        session topic, a project file, computer state: encode it into the
        field and read the snapshot, never touching the outside world to
        do it."""
        psi = cam_encode(text)
        snap = self._eye_obj.snapshot(psi)
        return psi, snap

    # ── Paper's Hands: rendering AND external interaction, this face only ──

    def look_outward(self, psi: List[float], response_text: str) -> List[str]:
        """Ordered emission (the real work PapersHands does alone), plus
        the actual render — `harness.present()` — because rendering and
        interacting with external/concrete reality is this face's job,
        not a separate object's. KVM (Monad-level stub, still unwired)
        belongs here too on the same reasoning, once it's real."""
        pathways = (self._hands_obj.relate(self._eye_obj, psi)
                   if self.box_kite is not None else [])
        if self.harness is not None:
            self.harness.present(response_text, kind='monad_response', center='hands')
        return pathways

    # ── the one entry point — the composter feeds both eyes the same input ─

    def process_input(self, text: str, user_id: str = 'default') -> Encounter:
        ctx = build_sentence_context(text)   # the composter: leaves -> root
        direction = infer_direction(ctx.root_vector)

        psi_in, snapshot = self.look_inward(text)

        # ── word selection ── v5.1 constructor (radical distance +
        # gamma_radial fold + conjugate scale + co-occurrence basin), with
        # the nearest_synsets path kept as the guaranteed fallback (PACE).
        selector = 'nearest_synsets'
        out_synsets: List[Any] = []
        words_out: List[str] = []
        if _construct is not None:
            try:
                r = _construct(text, register=self.register, topic=self.topic)
                for w in r.get('top', []):
                    try:
                        out_synsets.append(_wn.synset(w['synset']))
                        words_out.append(w['word'].replace('_', ' '))
                    except Exception:
                        continue
                if words_out:
                    selector = 'constructor'
            except Exception:
                pass
        if not words_out:
            pool = neighborhood_corpus(ctx.leaves, basin_k=40,
                                       basin_topic=self.topic)
            out = nearest_synsets(ctx.root_vector, pool, top_k=5) if pool else []
            out_synsets = [s for _, s in out]
            words_out = [(s.lemma_names()[0] if s.lemma_names() else s.name())
                         .replace('_', ' ') for s in out_synsets]

        # ── schema prune ── collapse perspective-redundant foci, keep a
        # redundancy margin (never below 3 while we have them).
        pruned: Dict[str, Any] = {}
        if _pruner is not None and len(out_synsets) >= 3:
            try:
                vecs = [_pruner.embed16(context_vector(s)) for s in out_synsets]
                p = _pruner.prune(vecs)
                pruned = {'kept': p['kept'], 'dropped': p['dropped'],
                          'groups': [[words_out[i] for i in g] for g in p['groups']]}
                if p['kept'] >= 3:
                    keep = sorted(p['reps'])
                    out_synsets = [out_synsets[i] for i in keep]
                    words_out = [words_out[i] for i in keep]
            except Exception:
                pruned = {}

        # ── Mind's Eye recursive repass ── the redundancy layer, on the
        # chosen words (16-word frames, 15-edge tree, step +1/word).
        me = MindsEyeRepass(words_out)
        for _ in range(len(words_out) + 4):
            g = me.guidance()
            if g['action'] == 'stop':
                break
            me.record(g['slot'], g['operator'])
        repass = {'guidance_n': me.passes, 'coverage': me.coverage()}

        response_text = assemble_sentence(direction, words_out)

        psi_out = cam_encode(response_text) if words_out else psi_in
        pathways = self.look_outward(psi_out, response_text)
        snapshot_out = self._eye_obj.snapshot(psi_out)

        # ── ingest while it is in Hands ── the Monad hears its own output
        # (external-frame intake; echo 0 — the loop-level echo cap is a
        # driver concern, not this single pass).
        if _hear is not None and self.store is not None and words_out:
            try:
                _hear(self.store.english, response_text, echo=0)
            except Exception:
                pass

        if self.box_kite is not None:
            lit_in = self._eye_obj.lit_struts(psi_in)
            lit_out = self._eye_obj.lit_struts(psi_out)
        else:
            lit_in, lit_out = [], []
        shared = sorted(set(lit_in) & set(lit_out))

        return Encounter(text=text, response=response_text, direction=direction,
                         words_out=words_out, root_vector=ctx.root_vector,
                         snapshot=snapshot, snapshot_out=snapshot_out, pathways=pathways,
                         lit_struts_in=lit_in, lit_struts_out=lit_out,
                         shared_struts=shared,
                         selector=selector, pruned=pruned, repass=repass)


# ── the real test: does WordNet-context proximity track box-kite (algebraic)
# proximity, or are these two systems just coincidentally adjacent? ─────────

def _strut_overlap(text_a: str, text_b: str, monad: RotaryBoxKiteMonad) -> int:
    """|lit_struts(a) ∩ lit_struts(b)| — cheap, symmetric, no generation
    involved. Used both for the real (input, its own response) pairs and
    for the random-text control below."""
    psi_a = cam_encode(text_a)
    psi_b = cam_encode(text_b)
    if monad.box_kite is None:
        return -1   # DEGENERATE marker, never a confident wrong 0
    a = set(monad._eye_obj.lit_struts(psi_a))
    b = set(monad._eye_obj.lit_struts(psi_b))
    return len(a & b)


if __name__ == '__main__':
    from harness import Harness

    h = Harness()
    monad = RotaryBoxKiteMonad(harness=h)
    ledger = Ledger()

    if monad.box_kite is None:
        print(f'[BoxKite UNAVAILABLE] {monad._kite_error}')
        print('Continuing with WordNet-only (Eye/Hands snapshot/relate skipped).')
    else:
        print(f'BoxKite signature {monad.box_kite.signature}  '
             f'{monad.box_kite.n_struts} struts, {monad.box_kite.n_assessors} assessors')

    sentences = (
        'the volcano formed a mountain of cinder and ash',
        'she deposited her savings in the reserve account',
        'the engine contains sixteen distinct operators',
    )

    encounters: List[Encounter] = []
    for sentence in sentences:
        print(f'\n=== input: {sentence!r} ===')
        enc = monad.process_input(sentence, user_id='cody')
        encounters.append(enc)
        print(f'  response: {enc.response!r}')
        print(f'  root_vector (nonzero): '
             f'{ {RELATION_METHODS[i]: c for i, c in enumerate(enc.root_vector) if c} }')
        print(f'  Eye snapshot: sigma_self={enc.snapshot["sigma_self"]:.6f}  '
             f'trochoid_loss={enc.snapshot["trochoid_loss"]:.6f}')
        print(f'  lit_struts_in:  {enc.lit_struts_in}')
        print(f'  lit_struts_out: {enc.lit_struts_out}')
        print(f'  shared_struts:  {enc.shared_struts}')
        for p in enc.pathways[:3]:
            print(f'    {p}')

    # ── the honest measurement: real (input -> its own response) overlap
    # vs a shuffled control (input -> SOMEONE ELSE's response) ────────────
    print('\n=== measurement: does the composter\'s response share more struts '
         'with its own input than with an unrelated one? ===')

    real_overlaps = [len(e.shared_struts) for e in encounters]

    rng = random.Random(20260825)
    control_overlaps = []
    for i, e in enumerate(encounters):
        others = [j for j in range(len(encounters)) if j != i]
        j = rng.choice(others) if others else i
        control_overlaps.append(
            _strut_overlap(e.text, encounters[j].response, monad))

    print(f'  real   (input <-> its own response): {real_overlaps}  '
         f'mean={sum(real_overlaps)/len(real_overlaps):.2f}')
    print(f'  control(input <-> another response): {control_overlaps}  '
         f'mean={sum(control_overlaps)/len(control_overlaps):.2f}')

    if monad.box_kite is None:
        ledger.add(Relation(
            name='crossref.strut_overlap', claim='real overlap exceeds control',
            status=Status.UNTESTED, fault=Fault.NONE,
            detail=monad._kite_error, group='cross-system'))
    else:
        real_mean = sum(real_overlaps) / len(real_overlaps)
        ctrl_mean = sum(control_overlaps) / len(control_overlaps)
        # Small n (3) — report the number honestly, do not dress it as
        # significant. HOLDS here means "measured, real > control", nothing
        # stronger.
        ledger.add(Relation(
            name='crossref.strut_overlap',
            claim='real (input, own response) overlap >= control (input, other response)',
            status=Status.HOLDS if real_mean >= ctrl_mean else Status.VIOLATED,
            expected=f'real_mean >= ctrl_mean', observed=f'{real_mean:.3f} vs {ctrl_mean:.3f}',
            detail=f'n={len(encounters)} — too small to claim significance, '
                   f'reported as a direction, not a proof',
            group='cross-system'))

    # ── the coarser measurement Cody asked for: sigma_self/trochoid_loss
    # deltas (pressure-differential-style summaries) instead of binary
    # all-16-dims strut membership, which had zero discriminating power
    # above. Uses MindsEye.snapshot()'s own channel split as-is — noted,
    # not fixed: rotary_rerun_monad.py splits red/blue at k>=8, while
    # rotary_rerun.c splits at k in {4-7,12-15} — two different channel
    # partitions computing sigma_self two different ways across these two
    # files. Flagged here, left alone; this test runs on whichever split
    # MindsEye.snapshot() already uses. ──────────────────────────────────
    print('\n=== coarser measurement: sigma_self / trochoid_loss deltas '
         '(input vs response) — real vs control ===')

    def _delta(a: Dict[str, Any], b: Dict[str, Any]) -> Tuple[float, float]:
        return (abs(a['sigma_self'] - b['sigma_self']),
                abs(a['trochoid_loss'] - b['trochoid_loss']))

    real_deltas = [_delta(e.snapshot, e.snapshot_out) for e in encounters]
    control_deltas = []
    for i, e in enumerate(encounters):
        others = [j for j in range(len(encounters)) if j != i]
        j = rng.choice(others) if others else i
        control_deltas.append(_delta(e.snapshot, encounters[j].snapshot_out))

    real_sigma  = [d[0] for d in real_deltas]
    real_troch  = [d[1] for d in real_deltas]
    ctrl_sigma  = [d[0] for d in control_deltas]
    ctrl_troch  = [d[1] for d in control_deltas]

    print(f'  real    sigma_self delta: {[f"{v:.4f}" for v in real_sigma]}  '
         f'mean={sum(real_sigma)/len(real_sigma):.4f}')
    print(f'  control sigma_self delta: {[f"{v:.4f}" for v in ctrl_sigma]}  '
         f'mean={sum(ctrl_sigma)/len(ctrl_sigma):.4f}')
    print(f'  real    trochoid_loss delta: {[f"{v:.4f}" for v in real_troch]}  '
         f'mean={sum(real_troch)/len(real_troch):.4f}')
    print(f'  control trochoid_loss delta: {[f"{v:.4f}" for v in ctrl_troch]}  '
         f'mean={sum(ctrl_troch)/len(ctrl_troch):.4f}')

    sigma_real_mean, sigma_ctrl_mean = sum(real_sigma)/len(real_sigma), sum(ctrl_sigma)/len(ctrl_sigma)
    ledger.add(Relation(
        name='crossref.sigma_delta',
        claim='real (input, own response) sigma_self delta is SMALLER than control',
        status=Status.HOLDS if sigma_real_mean < sigma_ctrl_mean else Status.VIOLATED,
        expected='real_mean < ctrl_mean', observed=f'{sigma_real_mean:.4f} vs {sigma_ctrl_mean:.4f}',
        detail=f'n={len(encounters)} — direction only, not significance',
        group='cross-system'))

    print()
    for i in range(len(ledger)):
        print(ledger.at(i))
    print(f'\n{len(ledger)} relations   '
         f'{ledger.count(Status.HOLDS)} hold   '
         f'{ledger.count(Status.VIOLATED)} FAULT   '
         f'{ledger.count(Status.UNTESTED)} untested')

    print('\nrotary_rerun_boxkite_monad.py: run complete.')
