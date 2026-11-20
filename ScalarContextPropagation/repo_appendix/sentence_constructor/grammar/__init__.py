"""
VAPMIP.engine.grammar — the grammatical box-kite layer for monad_sentences.bin
============================================================================
Turn a sentence into its reduced SHADOW — a verb-rooted dependency ring (e0 =
the finite verb, the anchor that does no work; e1..e15 = the dependents; edges
= the ~37 UD relations) plus one of the 7 clause patterns (the sail of the
box-kite).  Then CHECK the shadow against the verb's licensed frames
(VerbNet + PropBank): agree = a well-formed sentence ("prime"); a residue =
a malformed / non-standard one ("composite").

Corpora: ../datasets/  (bash datasets/fetch.sh).  Design: docs/wiki/
Grammar-Resources-For-Monad-Sentences.md and Kings-Maille-Box-Kite-Rings-As-
Sentences.md.

── Run this under PtolemyDesktop/.venv, not the bare system python3 ────────
Every WordNet touch in this package (sem_hash.py, maths_sanitize.py,
slot_shells.py's _verb_lemma) goes through `from nltk.corpus import
wordnet`, and a bare `import nltk` pulls in nltk.chunk -> nltk.classify ->
sklearn -> pandas -- which crashes under the system python3's installed
package combination (confirmed live, 2026-09-11: `ValueError: numpy.dtype
size changed, may indicate binary incompatibility. Expected 96 from C
header, got 88 from PyObject`, from pandas._libs.interval).
PtolemyDesktop/.venv/bin/python3 (the interpreter ptolemy_console.py's
Chat tab actually runs under) has a pinned numpy/pandas/sklearn
combination that does NOT hit this — confirmed live, same import succeeds
clean there. Two independent mitigations exist in this package (both
needed; neither alone is a substitute for the other):
  1. Every function that touches WordNet stubs sklearn out of sys.modules
     BEFORE importing nltk (`sys.modules.setdefault("sklearn", None)` etc.
     for sklearn/sklearn.feature_extraction/sklearn.feature_extraction.text)
     -- this dodges the crash even under the bare system python3, but is
     easy to forget on a NEW function (slot_shells.py's _verb_lemma shipped
     without it once, and morphy silently returned the input unchanged
     instead of raising -- a silent wrong answer, not a loud failure).
  2. Prefer running/testing this package under
     `PtolemyDesktop/.venv/bin/python3` when there's a choice, since it
     needs no stub at all and has no chance of an un-stubbed new call site
     failing silently.
"""
from . import conllu, frames, shadow, sails, sem_hash, generate, rotary_bridge   # noqa: F401
