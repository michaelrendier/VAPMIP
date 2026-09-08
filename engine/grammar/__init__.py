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
"""
from . import conllu, frames, shadow, sails, sem_hash, generate   # noqa: F401
