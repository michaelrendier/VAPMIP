# POISON NOTE: monad_wordnet_v4_20260519

* file: `monad_wordnet_v4_20260519.bin`; byte-identical copies: `~/.ptolemy/dirty/monad_wordnet.bin` (mtime 2026-05-17 15:08), `~/.ptolemy/clean/monad_wordnet_v4_20260519.bin`, `VAPMIP/checkpoints/clean/monad_wordnet_v4_20260519.bin`
* sha256: `66f70c70dcd8d860fa4af01833cf5c6e4c376194c510b5be156fe0c6064faf31`; size 110,040,527 bytes; PTOL v4 (read in full: every byte accounted for); N 25,000; vocabulary 24,485 slots; A-edges 6,825,748; word_count 121,914,388
* measured by `VAPMIP/SemPriCon/tools/assess_bin.py` (the `eval_checkpoint.py` classifier and metrics + the 2026-10-17 token sanitiser `Wernicke/sanitize/sanitize_v0.py`), 2026-10-18
* what it is: the store the C monad (`PtolC/` at commit `eb28ce8`, v1.215) loaded when it answered "what is your name" with `holcus same stuff seemy` (screenshots dated 2026-05-19; header numbers identical to the screenshot's `vocab=24485  A=6825748  wc=121914388`). Reproduced from source on 2026-10-18.

**Label: DIRTY, verdict PASS.** Under the project's own rule (`eval_checkpoint.py`): pollution 5.04 % (< 20 %: PASS; not < 1 %: not CONVERGED); entropy 88.68 % of maximum (natural band 85–92); Gini 0.7564 (natural band 0.60–0.80). The same bytes sit in `clean/` (labelled "WordNet 3.1 + Gutenberg … most thoroughly trained", `checkpoints/clean/PRIMER_from_dot_ptolemy.md`) and in `dirty/` (`~/.ptolemy/dirty/monad_wordnet.bin`, with a 2026-05-17 assessment of 5.04 %); this note settles the placement: dirty.

| tier:reason (sanitiser) | tokens | examples |
|---|---|---|
| B:candidate_evidence_pending (no WordNet synset) | 18,409 | 'seemy', 'carre', 'azv', 'xxa', 'diem', 'gaii', 'uxp', 'arcos' |
| A:in_wordnet | 4,563 | 'fluid', 'papaw', 'pommy', 'quiets', 'farm', 'atrip' |
| Q:no_vowel | 990 | |
| C:proper_noun | 450 | |
| F:function_word | 55 | |
| Q:chrome | 14 | |
| Q:single_letter | 3 | |
| Q:non_latin_or_symbol | 1 | |

| class (eval_checkpoint) | tokens |
|---|---|
| consonant-only | 993 |
| consonant-cluster-3 | 654 |
| no-vowel | 344 |
| hex-string | 268 |
| total polluted | 1,233 of 24,485 (5.04 %) |

**What it does NOT contain.** No multilingual content: all 24,485 displayed words are ASCII (0 non-ASCII). The C tokenizer of this build (`tokenizer.c`: `isalpha()` in the C locale) discards every non-ASCII byte, so a Greek, Chinese, Arabic or accented word could not have entered through any ingest path of this build.

**Structure that makes the vocabulary unrepresentative (not corpus pollution).**
* A slot displays the highest-`E` word that ever addressed it (`monad_learn_ex`); `E` is a function of spelling. Of 76,719 WordNet single-token ASCII lemmas, 5.1 % (3,919) are their slot's displayed word; `tree`, `water`, `name`, `is` display other words (`typhon`, `defrg`, `emite`, `nanti`).
* Every word of 8+ letters addresses to slot 0 (`seemy`), E = d\*: 49,018 of 76,719 lemmas (`monad_word_coords`: the float seed loses its fractional bits). Slot 0 is the best-connected slot (22,987 neighbours).
* `prose_seen` is per slot: 8,968 slots flagged "WordNet + prose" display a word with no WordNet synset.

**Cause of the pollution classes:** corpus text with OCR/abbreviation/hex fragments (the 2026-05-16 `~/Documents` runs documented in `checkpoints/README.md` are the same classes; this store is the later, post-vowel-fix English run, so the classes are smaller: 5.04 % against 10.7 % and 35.58 % there). Top A-edge: `qgt`–`each`, w = 3,840 (a consonant-only token on slot 8017, the slot of `of`).

**Identity text:** the store carries `PTOLEMY_IDENTITY` (`monad.c`, learned by `-i`): all 646 edges that text creates are present, each at least as heavy as the identity's own contribution (chance at this store's edge density: ≈ 14).

**Discrepancy recorded, not resolved:** the 2026-05-17 assessment of the v2-format serialisation of this data (`monad_wordnet_v4_20260519.assessment.2026-05-17-v2format.json`) reports word_count 44,782,621; the v4 header reports 121,914,388. Vocabulary, A-edge count and pollution counts are identical in both.

Status: archived beside the SemPriCon white paper as the baseline store, read-only (`chmod a-w`). Not a starting point for new training. Not a working bin: `monad3_c.bin` and everything `ptol.c` uses were not touched. Bins are gitignored (too large for GitHub): this note, `monad_wordnet_v4_20260519.ASSESSMENT.md` and `monad_wordnet_v4_20260519.assessment.json` are what is committed.
