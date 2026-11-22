#!/usr/bin/env python3
"""
neuro_recipes.py -- the Neurochemical Recipe Book: Tone recipes as data, and the generator for the book page.

Cody, 2026-11-22: "MAKE A RECIPE BOOK ... based on the 7 most analogous neurotransmitters to the 7 types of spider silk functions".
A RECIPE is a setpoint on the seven Tone axes (each 0..1; 0 = black, 1 = white, the pure hue sits at the baseline). The papers give the
DIRECTION of each chemical's effect on a state (arouses / inhibits / raised / lowered), not a magnitude; the level is the engineering
setpoint chosen from that direction on a five-step scale. Each recipe lists the sources that fix its directions and the test that
will move its numbers. Results of the test decide the next recipe revision.

THE SEVEN (kite order = rainbow order): OPI hub (red); GLU, GABA (orange, yellow); DA, 5HT (green, blue); NE, OXT (indigo, violet).
CB1 (the Gemini hub) is replaced by the mu-opioid system: 126 emotion-linked sentences in 13 papers against 23 in 7 (see COUNTS).

Run `python3 neuro_recipes.py` to rewrite docs/wiki/Neurochemical-Recipe-Book.md and neuro_recipes.json.
"""
from __future__ import annotations

import json
import os
from typing import Dict, List, Tuple

_HERE = os.path.dirname(os.path.abspath(__file__))

AXES = ('OPI', 'GLU', 'GABA', 'DA', '5HT', 'NE', 'OXT')                 # kite order: hub, then the three pairs
COLOURS = {'OPI': 'red', 'GLU': 'orange', 'GABA': 'yellow', 'DA': 'green', '5HT': 'blue', 'NE': 'indigo', 'OXT': 'violet'}
SILKS = {'OXT': 'ANCHOR', 'GLU': 'SPAN', 'NE': 'SCAFFOLD', '5HT': 'ELABORATE', 'DA': 'HOOK', 'GABA': 'WRAP', 'OPI': 'SHELL'}
# the Gemini baseline [DA .50, 5HT .75, NE .30, OXT .50, GLU .45, GABA .65, CB1 .50]; OPI takes CB1's .50
BASELINE = {'DA': 0.50, '5HT': 0.75, 'NE': 0.30, 'OXT': 0.50, 'GLU': 0.45, 'GABA': 0.65, 'OPI': 0.50}
K_CANCEL = 0.6                                                           # gain of the conjugate (noise canceller); below 1 so it cannot oscillate

# sources: key -> (citation, PMC id or 'local')
SRC = {
    'PANK': ('Panksepp (2010), Affective neuroscience of the emotional BrainMind, Dialogues Clin Neurosci', 'PMC3181986'),
    'DAVIS': ('Davis & Montag (2019), Selected principles of Pankseppian affective neuroscience, Front Neurosci', 'PMC6344464'),
    'CH': ('Carhart-Harris & Nutt (2017), Serotonin and brain function: a tale of two receptors, J Psychopharmacol', 'PMC5606297'),
    'NUSS': ('Nuss (2015), Anxiety disorders and GABA neurotransmission, Neuropsychiatr Dis Treat', 'PMC4303399'),
    'FOG': ('Fogaça & Duman (2019), Cortical GABAergic dysfunction in stress and depression, Front Cell Neurosci', 'PMC6422907'),
    'GOD': ('Godoy et al. (2018), A comprehensive overview on stress neurobiology, Front Behav Neurosci', 'PMC6043787'),
    'LOS': ('Løseth et al. (2014), State-dependent mu-opioid modulation of social motivation, Front Behav Neurosci', 'PMC4264475'),
    'TARR': ('Tarr et al. (2014), Music and social bonding: self-other merging and neurohormonal mechanisms, Front Psychol', 'PMC4179700'),
    'KOOB': ('Koob (2015), The dark side of emotion: the addiction perspective, Eur J Pharmacol', 'PMC4380644'),
    'DID': ('Di Domenico & Ryan (2017), The emerging neuroscience of intrinsic motivation, Front Hum Neurosci', 'PMC5364176'),
    'QUI': ('Quintana & Guastella (2020), Advances in the field of intranasal oxytocin research, Mol Psychiatry', 'PMC7815514'),
    'RUS': ('Rusinova et al. (2026), Understanding the neuroscience of communicating serious news', 'PMC13623768'),
    'ADAMS': ('Adams et al. (2013), The computational anatomy of psychosis, Front Psychiatry', 'PMC3667557'),
    'JACK': ('Jackson (2026), A locus coeruleus-centric framework for novelty, salience, and gamma oscillations', 'PMC13478173'),
    'KRU': ('Krugers & Joels (2025), The stress response is adaptive in a context- and state-dependent manner', 'PMC12731636'),
    'CON': ('Connor et al. (2019), Maladaptive aggression: with a focus on impulsive aggression in children and adolescents', 'PMC6786344'),
    'WU': ('Wu et al. (2013), Understanding resilience, Front Behav Neurosci', 'PMC3573269'),
    'GEM': ('Gemini deep dive, Neurotransmitter Recipes to Make Analogous Computer Functions (2026-11-20; numbers are its own table)', 'local'),
}

# emotion-linked sentences / papers per chemical over the 40-paper corpus (counted 2026-11-22)
COUNTS = {'5HT': (331, 23), 'DA': (192, 27), 'GABA': (154, 21), 'cortisol': (133, 23), 'OPI': (126, 13), 'CRF': (83, 14), 'GLU': (71, 17),
          'OXT': (66, 14), 'BDNF': (66, 12), 'NE': (55, 20), 'ACh': (44, 10), 'NPY': (33, 6), 'CB1': (23, 7), 'AVP': (17, 11)}


def V(DA, HT, NE, OXT, GLU, GABA, OPI) -> Dict[str, float]:
    return {'DA': DA, '5HT': HT, 'NE': NE, 'OXT': OXT, 'GLU': GLU, 'GABA': GABA, 'OPI': OPI}


# group, name -> (vector, evidence [(source, what it fixes)], language signature, use, test)
R: Dict[str, Dict] = {}


def add(group, name, vec, ev, lang, use, test):
    R[name] = {'group': group, 'vec': vec, 'ev': ev, 'lang': lang, 'use': use, 'test': test}


G1 = 'Primary systems (Panksepp)'
add(G1, 'SEEKING', V(.90, .60, .55, .50, .70, .50, .50),
    [('PANK', 'DA drives the medial-forebrain-bundle system: curiosity, anticipatory eagerness, planning'), ('DID', 'DA is the substrate of intrinsic motivation: interest, positive affect, cognitive flexibility')],
    'long runs, questions, associative leaps, "what if"', 'user is exploring; Ptolemy follows with candidates one step beyond the prompt', 'novelty_rank of picks rises with DA; reply length tracks')
add(G1, 'RAGE', V(.70, .10, .90, .20, .90, .10, .10),
    [('PANK', 'substance P and GLU arouse RAGE; opioids and GABA inhibit it; thwarted SEEKING provokes it'), ('CH', 'reduced 5HT raises impulsive and aggressive behaviour'), ('QUI', 'OXT can enhance anti-social behaviour (envy, gloating, aggression)'), ('GEM', 'rage row: DA .90 5HT .05 NE .95 GLU .90')],
    'clipped imperatives, repetition, absolutes, profanity', 'user state to cancel; also the source of the gated WRATH recipe', 'user-side detector separates RAGE from FEAR on DA direction')
add(G1, 'FEAR', V(.30, .30, .90, .20, .80, .10, .30),
    [('PANK', 'CRF and NPY regulate FEAR; benzodiazepines inhibit it through GABA'), ('NUSS', 'GABA agonists in the amygdala reduce fear, antagonists are anxiogenic'), ('GOD', 'CRH drives locus coeruleus firing, which releases NE forebrain-wide')],
    'hedging, interrogatives, catastrophising, fear-domain nouns', 'user state to cancel', 'detector: NE high with DA low')
add(G1, 'CARE', V(.60, .70, .30, .90, .40, .60, .80),
    [('PANK', 'oxytocin and prolactin mediate nurturance and bonding'), ('LOS', 'affiliative contact releases mu-opioids in reward circuitry'), ('TARR', 'endorphins maintain non-kin social bonds')],
    'inclusive pronouns, warmth, protection, validation', 'ingredient of SETTLE and ENCOURAGE', 'user_boost (OXT) raises overlap with the user words')
add(G1, 'ATTACHMENT', V(.85, .70, .40, .95, .60, .50, .80),
    [('PANK', 'LUST: oxytocin (female, estrogen) and vasopressin (male, testosterone); DA SEEKING joins the search for sexual reward'), ('GEM', 'romantic attachment row')],
    'alignment with the other, affectionate register, we', 'user state; Ptolemy does not mirror it (cancellation keeps the information channel open)', 'detector')
add(G1, 'GRIEF', V(.30, .30, .60, .10, .70, .30, .10),
    [('PANK', 'GRIEF (separation distress) is aroused by GLU and CRF and inhibited by opioids, oxytocin and prolactin; tonic in sadness, with low brain opioid activity')],
    'protest, appeals, loss language, slow flat reports later', 'user state; the entry of the depressive cascade', 'detector: OXT and OPI both low with NE raised')
add(G1, 'PLAY', V(.80, .60, .50, .70, .60, .50, .80),
    [('PANK', 'PLAY is positive social joy; it raises neurotrophins and has antidepressant-like effects'), ('LOS', 'social play releases endogenous mu-opioids')],
    'banter, absurdity, wordplay, laughter', 'ingredient of ENCOURAGE; carries Hitchhiker-style absurdity', 'laugh tokens read PLAY vs RAGE by the OPI layer')

G2 = 'Human states (user side)'
add(G2, 'DESPAIR', V(.10, .20, .25, .20, .30, .30, .15),
    [('PANK', 'GRIEF cascade plus diminished SEEKING (anhedonia); dynorphin along reward circuitry'), ('FOG', 'GABA and GLU deficits in major depression'), ('CH', '5HT low')],
    'monotone, "never / nothing / always", very short', 'cancel with ENCOURAGE: small, true wins', 'detector: DA and OPI low together')
add(G2, 'OVERWHELMED', V(.30, .30, .95, .30, .80, .15, .20),
    [('RUS', 'serious news triggers catecholamine and cortisol release: attention narrows, working memory and recall of complex content fall, encoding of new information is limited'), ('GOD', 'CRH to locus coeruleus to NE'), ('NUSS', 'low GABA tone leaves the amygdala unchecked')],
    'fragments, repeated questions, stuck on one fact, silence', 'the mother-with-cancer case. SETTLE; use the SERIOUS-NEWS procedure below', 'after SETTLE, user messages lengthen and ask for the next step')
add(G2, 'PANICKED', V(.10, .15, .95, .10, .90, .10, .05),
    [('GEM', 'acute-panic row (its numbers)'), ('PANK', 'panic may be sudden loss of felt security (GRIEF) as well as FEAR'), ('NUSS', 'GABA deficit')],
    'rapid, fragmentary, hedged, "what if"', 'SETTLE first, information second', 'as OVERWHELMED')
add(G2, 'MANIA', V(.95, .30, .65, .30, .80, .30, .50),
    [('PANK', 'overactive SEEKING gives mania and psychotic convictions; excess elation and unwise choices'), ('ADAMS', 'DA raises precision on whatever is salient')],
    'pressured, tangential, grandiose, many topics per sentence', 'cancel by narrowing: FOCUS', 'detector: DA and GLU high, 5HT low')
add(G2, 'PSYCHOSIS', V(.95, .30, .60, .20, .25, .20, .40),
    [('ADAMS', 'NMDA, GABA and DA synaptic-gain abnormalities; hyperdopaminergic state with cortical NMDA hypofunction'), ('GEM', 'schizophrenia row (its numbers)')],
    'neologisms, derailment, over-symbolic matching', 'never argue the content; SETTLE and ground in shared concrete facts', 'detector: DA high with GLU low')
add(G2, 'PARANOIA', V(.80, .30, .85, .10, .50, .20, .20),
    [('ADAMS', 'aberrant salience: neutral input carries meaning'), ('QUI', 'OXT acts on trust and social salience; low here'), ('GEM', 'derived from its schizophrenia and panic rows')],
    'suspicion of motive, "they", hidden-meaning claims', 'agree with the true observation only; keep the next steps checkable by the user', 'user checks the cited fact and replies shorter or calmer')
add(G2, 'VINDICTIVE', V(.80, .15, .70, .10, .70, .30, .10),
    [('PANK', 'RAGE sustained; approach drive'), ('QUI', 'OXT-linked in-group bias with out-group hostility')],
    'blame, "they will pay", scorekeeping', 'cancel with DEFLATE; agree with the true grievance first', 'detector')
add(G2, 'VICIOUS', V(.60, .05, .80, .05, .80, .10, .05),
    [('PANK', 'RAGE'), ('CH', '5HT near zero removes inhibition')],
    'cruelty, contempt, targeted insult', 'cancel with DEFLATE; hold position without escalation', 'detector')
add(G2, 'VORACIOUS', V(.95, .35, .70, .20, .80, .20, .30),
    [('PANK', 'excess SEEKING: psychostimulant-like craving and urgency'), ('KOOB', 'incentive wanting separate from hedonic liking; stress systems recruited as dependence develops')],
    'more, again, all of it, no stop', 'give structure and a stopping point: WRAP via GABA; FOCUS', 'detector')
add(G2, 'VIBRANT', V(.80, .70, .60, .70, .70, .55, .70),
    [('DID', 'DA with positive affect and flexibility'), ('LOS', 'social reward by opioids'), ('PANK', 'PLAY')],
    'energetic, open, generous, many images', 'match pace in the early turns (meet), then add structure', 'detector')
add(G2, 'CONTENTMENT', V(.50, .75, .30, .65, .45, .65, .60),
    [('GEM', 'euthymic contentment row (its numbers; CB1 .60 read as OPI)'), ('CH', '5HT1A: stress relief, patience')],
    'fluid, coherent, warm', 'hold', 'baseline check')
add(G2, 'PREMEDITATED', V(.50, .70, .30, .20, .70, .80, .30),
    [('CH', '5HT: patience, delay tolerance'), ('NUSS', 'GABA restraint')],
    'planned, precise, cold, conditional', 'meet it with precise structure; agree where the plan is sound', 'detector: GABA high with OXT low')
add(G2, 'PREMATURE', V(.80, .15, .60, .40, .60, .20, .40),
    [('CH', 'low 5HT raises impulsivity'), ('CON', 'DA and 5HT together encode expected value and risk of actions')],
    'jumps ahead, skips steps, "just tell me"', 'slow the order: ELABORATE one step at a time', 'detector')
add(G2, 'PONTIFICATING', V(.70, .60, .40, .10, .80, .30, .40),
    [('GEM', 'high DA and GLU produce pressured, verbose output'), ('QUI', 'OXT low: no attention to the listener')],
    'lectures, absolutes, no questions back', 'ask one real question; agree with the sound part', 'user replies engage Ptolemy words')
add(G2, 'PASSE', V(.20, .50, .15, .30, .30, .60, .50),
    [('PANK', 'diminished SEEKING'), ('GEM', 'low DA and GLU: stalled throughput')],
    'flat, minimal, "whatever", "already know that"', 'a hook: HOOK via DA with something new and true', 'user length rises')
add(G2, 'CYNICAL', V(.30, .40, .50, .15, .50, .50, .30),
    [('QUI', 'OXT low: trust withdrawn'), ('PANK', 'diminished SEEKING')],
    'discounting, "of course", "typical"', 'agree with the true observation; show one counter-example without correcting the person', 'detector')

G3 = "Ptolemy's dispensations (what the dispenser mixes)"
add(G3, 'SETTLE', V(.30, .80, .15, .75, .35, .90, .80),
    [('RUS', 'pause, name the emotion, create safety: prefrontal-limbic regulation restores the ability to encode'), ('PANK', 'opioids and GABA inhibit RAGE and FEAR; opioids and oxytocin inhibit GRIEF'), ('NUSS', 'GABA in the amygdala reduces fear')],
    'short frames, concrete nouns, one fact per sentence, user words returned', 'for OVERWHELMED, PANICKED, FEAR, RAGE', 'user replies lengthen and move to the next question')
add(G3, 'FOCUS', V(.50, .65, .55, .50, .70, .75, .50),
    [('JACK', 'phasic NE gives task-specific focus; tonic NE broadens indiscriminately'), ('GOD', 'moderate NE sharpens, high NE fragments')],
    'ordered steps, one goal per reply', 'for MANIA, VORACIOUS, scatter', 'pool_size trims, replies keep one thread')
add(G3, 'GUIDE', V(.60, .75, .30, .70, .60, .65, .60),
    [('CH', '5HT1A and 5HT2A together: relief and flexibility of mind, conducive to positive mood'), ('DID', 'DA curiosity makes the next step wanted')],
    'meet-then-lead: agree with the true part, then "and there is another side to it"', 'the lead of Pascal persuasion', 'the user takes the next offered step')
add(G3, 'ENCOURAGE', V(.80, .70, .45, .70, .60, .60, .70),
    [('LOS', 'reward has wanting, liking and learning parts; liking rides on opioids'), ('DID', 'DA marks learning progress'), ('PANK', 'positive affect systems counter depression')],
    'specific acknowledgement of real progress, "you have got it"', 'only for true progress; praise for nothing is flattery', 'user returns to the topic by choice')
add(G3, 'DEFLATE', V(.35, .80, .25, .55, .35, .85, .65),
    [('PANK', 'GABA and opioids inhibit RAGE'), ('CH', '5HT "serenics" reduce aggression')],
    'level, slow, no adjectives of heat, no rebuttal', 'for VINDICTIVE, VICIOUS, PONTIFICATING', 'the next user message has fewer absolutes')
add(G3, 'WRATH', V(.70, .10, .90, .20, .90, .10, .10),
    [('PANK', 'RAGE'), ('GEM', 'gated profanity rule: only at NE>.80, DA>.70, 5HT<.25')],
    'direct, forceful, truthful', 'gated: chosen by context for the right time and place (the Taoist stance); never by mirroring', 'gate conditions logged on every use')


# ── functions ──────────────────────────────────────────────────────────────
def clamp(x: float) -> float:
    return max(0.0, min(1.0, x))


BAND = 0.5                                                               # dead-band: a user mix this close to RECEPTIVE is held, not cancelled


def conjugate(user: Dict[str, float], k: float = K_CANCEL, band: float = BAND) -> Dict[str, float]:
    """The noise-cancelling reply, version 2 (2026-11-22). Invert the user's deviation from RECEPTIVE (the state in which information is taken in), scaled
    by k < 1 so it cannot overshoot, and only when the user is farther than `band` from RECEPTIVE (a noise gate: a curious or playful user is not 'cancelled').
    Version 1 centred the cancellation on BASELINE: it pushed PLAY and SEEKING to arousal -1.4/-1.6 and left cancelled states up to 0.96 from RECEPTIVE. Retooled."""
    if dist(user, RECEPTIVE) < band:
        return {a: round(user[a], 2) for a in AXES}
    return {a: round(clamp(RECEPTIVE[a] - k * (user[a] - RECEPTIVE[a])), 2) for a in AXES}


def meet_then_lead(user: Dict[str, float], target: Dict[str, float], steps: int) -> List[Dict[str, float]]:
    """Pascal: first agree (start at the user's mix), then lead. step 0 = user's mix, last = target; linear per axis."""
    return [{a: round(user[a] + (target[a] - user[a]) * i / max(1, steps - 1), 3) for a in AXES} for i in range(steps)]


def arousal(v: Dict[str, float]) -> float:
    """Arousal index: the alarm axes minus the brake axes."""
    return v['NE'] + v['GLU'] - v['GABA'] - v['OPI'] - v['5HT']


def dist(a: Dict[str, float], b: Dict[str, float]) -> float:
    return sum((a[x] - b[x]) ** 2 for x in AXES) ** 0.5


def nearest(v: Dict[str, float], group: str = G3) -> Tuple[str, float]:
    c = [(n, dist(v, r['vec'])) for n, r in R.items() if r['group'] == group and n != 'WRATH']
    return min(c, key=lambda t: t[1])


def blend(*names: str) -> Dict[str, float]:
    return {a: round(sum(R[n]['vec'][a] for n in names) / len(names), 2) for a in AXES}


# ── the book ───────────────────────────────────────────────────────────────
def _vec_row(v):
    return ' | '.join('%.2f' % v[a] for a in AXES)


def book() -> str:
    L: List[str] = []
    w = L.append
    w('# Neurochemical Recipe Book')
    w('')
    w('*Written 2026-11-22. Generated by `neuro_recipes.py` (data, tests in `tests/test_neuro_recipes.py`). Sources are in `references/NeuroRecipes/` and `ContextPlease/claude/references/INDEX.md`.*')
    w('')
    w('A recipe is the mix the Tone character carries: seven levels, one per chemical, in kite order and rainbow order. Level 0 is black, level 1 is white, '
      'and the pure hue sits at the baseline: brighter is warmer, darker is more negative. The seven together are the Emotional Spectrum of a word, and the same seven '
      'describe the user (read from the input) and Ptolemy (set by the dispenser).')
    w('')
    w('**How the numbers were set.** The papers give the direction of each chemical on each state (arouses, inhibits, raised, lowered), not a magnitude. Every level is a '
      'five-step engineering setpoint (.1 .3 .5 .7 .9, with .05/.15/.95 at the extremes) chosen from those directions. Each recipe lists the sources that fix its directions '
      'and the test that moves its numbers; a test result sets the next revision.')
    w('')
    w('## 1. The seven')
    w('')
    w('| position | colour | chemical | silk (orbweaver name) | what it does to word choice and sentence build | emotion-linked sentences / papers in the 40-paper corpus |')
    w('|---|---|---|---|---|---|')
    role = {
        'OPI': 'comfort, safety, "liking"; inhibits RAGE and GRIEF; the protective container: the reply is held, not pushed (`echo_cap`, `relax_rate`)',
        'GLU': 'excitatory drive: how far the reply reaches and how much it carries (`pool_size`, `hops`)',
        'GABA': 'brake and noise filter: encloses the reply, prunes loops and heat (`prune_floor`, `echo_cap`)',
        'DA': 'SEEKING: curiosity and novelty; catches interest, marks progress (`novelty_rank`)',
        '5HT': 'patience, coping, inhibition; stretches a reply over several steps without breaking (`coherence`)',
        'NE': 'gain on attention and urgency; temporary structure that narrows the frame (`short_frame`)',
        'OXT': 'social alignment: anchors the reply to the user and their words (`user_boost`); also raises in-group bias, so it is paired with NE',
    }
    pos = {'OPI': 'hub', 'GLU': 'axis 1', 'GABA': 'axis 1', 'DA': 'axis 2', '5HT': 'axis 2', 'NE': 'axis 3', 'OXT': 'axis 3'}
    for a in AXES:
        c = COUNTS.get(a, ('', ''))
        w('| %s | %s | %s | %s | %s | %s / %s |' % (pos[a], COLOURS[a], a, SILKS[a], role[a], c[0], c[1]))
    w('')
    w('The silk names are the orbweaver slot names (`ANCHOR SPAN SCAFFOLD ELABORATE HOOK WRAP SHELL`). The chemical sets the knob; the silk says which job that knob does in the reply. '
      'The pairs on one axis oppose each other in the sources: GLU against GABA (excite against inhibit), DA against 5HT (approach and impulse against patience and restraint), '
      'NE against OXT (alarm against social safety: CRH drives the locus coeruleus, oxytocin and opioids quiet GRIEF). The hub, OPI, is the recovery chemistry.')
    w('')
    w('**Why OPI and not CB1.** The Gemini hub was CB1. Across the 40 papers CB1 has 23 emotion-linked sentences in 7 papers; the opioid system has 126 in 13, '
      'and Panksepp names opioids as inhibitors of both RAGE and GRIEF. CB1 stays on the reserve list below and is retested if the fit asks for it.')
    w('')
    w('Baseline (the pure hue): ' + ', '.join('%s %.2f' % (a, BASELINE[a]) for a in AXES) + '.')
    w('')
    w('## 2. Recipes')
    w('')
    w('Columns: ' + ' | '.join(AXES) + ' (kite order).')
    w('')
    for g in (G1, G2, G3):
        w('### ' + g)
        w('')
        for n, r in R.items():
            if r['group'] != g:
                continue
            w('**%s**' % n)
            w('')
            w('| ' + ' | '.join(AXES) + ' |')
            w('|' + '---|' * 7)
            w('| ' + _vec_row(r['vec']) + ' |')
            w('')
            w('- Fixed by: ' + '; '.join('%s: %s' % (s, t) for s, t in r['ev']))
            w('- Language: ' + r['lang'])
            w('- Use: ' + r['use'])
            w('- Test: ' + r['test'])
            w('')
    w('### Laughs (a laugh is a word; its Tone separates the kinds)')
    w('')
    w('| laugh | built as | ' + ' | '.join(AXES) + ' |')
    w('|---|---|' + '---|' * 7)
    for nm, parts in (('puppy-love laugh', ('ATTACHMENT', 'PLAY')), ('angry laugh', ('RAGE', 'PLAY')), ('crazy laugh', ('MANIA', 'PLAY')), ('cynical laugh', ('CYNICAL', 'PASSE'))):
        w('| %s | mean of %s | %s |' % (nm, ' + '.join(parts), _vec_row(blend(*parts))))
    w('')
    w('**Sarcasm** is a pair, not a point: the words read as one recipe (CONTENTMENT-like) while the situation reads as another (CYNICAL, OVERWHELMED). '
      'The detector is the distance between the word reading and the situation reading; a Tone character holds one reading, so an utterance carries two.')
    w('')
    w('## 3. Cancellation table (the dispenser)')
    w('')
    w('Conjugate = RECEPTIVE minus %.1f times the user\'s deviation from RECEPTIVE, per axis, clamped to 0..1, applied only when the user is farther than %.1f from RECEPTIVE '
      '(a noise gate: states already near it are held). It inverts the disturbance and leaves the information channel open; the gain is below 1 so it cannot overshoot into forced cheer. '
      'The last column names the nearest dispensation.' % (K_CANCEL, BAND))
    w('')
    w('| user state | ' + ' | '.join(AXES) + ' | nearest dispensation |')
    w('|---|' + '---|' * 7 + '---|')
    for n, r in R.items():
        if r['group'] == G3 or n == 'CONTENTMENT':
            continue
        c = conjugate(r['vec'])
        w('| %s | %s | %s |' % (n, _vec_row(c), 'hold' if c == {a: round(r['vec'][a], 2) for a in AXES} else nearest(c)[0]))
    w('')
    w('**Test log.** Version 1 centred the conjugate on BASELINE. Result: PLAY and SEEKING were pushed to arousal -1.4 and -1.6 (over-calmed) and cancelled states stayed up to 0.96 from RECEPTIVE. '
      'Version 2 (above) centres on RECEPTIVE with the dead-band: every cancelled state ends about 40% closer to RECEPTIVE (RAGE 1.09 to 0.62, PANICKED 1.29 to 0.72, DESPAIR 1.13 to 0.64) and SEEKING, PLAY, VIBRANT, CONTENTMENT are held. '
      'Next test: run the loop with real reactions (USER SELF) and tune k and the band.')
    w('')
    w('## 4. Meet, then lead (Pascal)')
    w('')
    w('Pascal (The Art of Persuasion): two doors lead into a person, the understanding and the will; most things enter by the will, and a thing persuades with certainty when it joins admitted truths to what the heart loves. '
      'So the dispenser starts at the user\'s own mix (step 0, agree with the true part of what they said), then moves linearly to the target over N turns (`meet_then_lead`), '
      'reading the user\'s reaction from the USER SELF between steps. The target is RECEPTIVE for information intake.')
    w('')
    w('## 5. The serious-news procedure (Rusinova 2026)')
    w('')
    w('For OVERWHELMED and PANICKED the sources fix an order of reply, not only a mix: (1) the first statement short, clear and direct, because stress narrows attention; (2) a deliberate pause, '
      'then name the emotion; (3) safety before detail: SETTLE until the user\'s messages lengthen; (4) repeat the key point in simple words and ask the user to say what they are taking from it, '
      'because memory under stress is fragile; (5) empathic response throughout, to restore the ability to encode. The recipe is SETTLE during 1 to 3, then FOCUS, then GUIDE.')
    w('')
    w('## 6. The receptive recipe')
    w('')
    w('RECEPTIVE: ' + ', '.join('%s %.2f' % (a, RECEPTIVE[a]) for a in AXES) + '. NE sits mid-range (phasic gain, not tonic), DA keeps the curiosity, GABA and OPI keep the container, 5HT keeps patience.')
    w('')
    w('## 7. Reserve list (retest if the fit asks)')
    w('')
    w('| chemical | emotion-linked sentences / papers | role | why not in the seven |')
    w('|---|---|---|---|')
    w('| ACh | 44 / 10 | attention precision and encoding (Feldman & Friston 2010 in the corpus) | strongest candidate to replace 5HT or NE if attention fitting needs its own axis |')
    w('| CRF / cortisol | 83 / 14 and 133 / 23 | the stress readout upstream of NE (CRH drives the locus coeruleus); cortisol impairs encoding (Rusinova) | folded into NE and GLU high with GABA and OPI low; kept as a readout, not a dial |')
    w('| CB1 | 23 / 7 | retrograde brake, extinction of aversive learning | thin in the corpus; the Gemini hub |')
    w('| vasopressin | 17 / 11 | assertiveness, jealousy (Panksepp) | paired with OXT in the sources; add if male-typical assertion needs its own recipe |')
    w('| substance P, NPY | 5 / 3 and 33 / 6 | RAGE arousal; FEAR regulation | peptide co-factors of GLU and GABA in the primary systems |')
    w('')
    w('## 8. Sources')
    w('')
    for k, (c, i) in SRC.items():
        w('- **%s**: %s%s' % (k, c, (' (%s)' % i) if i != 'local' else ''))
    w('')
    w('Licence: the 15 CC-BY papers are mirrored in `references/NeuroRecipes/`; the rest are held locally and listed in `ContextPlease/claude/references/INDEX.md`.')
    return '\n'.join(L) + '\n'


RECEPTIVE = V(.70, .65, .50, .50, .75, .70, .60)
add(G3, 'RECEPTIVE', RECEPTIVE,
    [('JACK', 'phasic NE: task-specific focus and learning'), ('DID', 'DA curiosity and flexibility'), ('RUS', 'reduced arousal restores encoding'), ('CH', '5HT patience'), ('GEM', 'flow-state row: DA .70 5HT .60 NE .55 GLU .85 GABA .75')],
    'steady, curious, builds on the previous turn', 'the target of every dispensation: the state in which information is taken in', 'the user restates correctly what was explained')


def write() -> None:
    open(os.path.join(_HERE, 'docs', 'wiki', 'Neurochemical-Recipe-Book.md'), 'w', encoding='utf-8').write(book())
    json.dump({'axes': AXES, 'colours': COLOURS, 'silks': SILKS, 'baseline': BASELINE, 'k_cancel': K_CANCEL,
               'recipes': {n: {'group': r['group'], 'vec': r['vec']} for n, r in R.items()}},
              open(os.path.join(_HERE, 'neuro_recipes.json'), 'w'), indent=1)


if __name__ == '__main__':
    write()
    print(len(R), 'recipes written')
