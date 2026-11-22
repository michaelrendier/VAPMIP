# Live vocabulary: the Monad improves its own words

*2026-11-21. Code: `live_vocabulary.py`; tests: `tests/test_live_vocabulary.py` (9). Symbols: `@RCCM_SYMBOLS`. Licence: proprietary, all rights reserved.*

**Requirement (the author).** The Monad must be able to add to and refine its own vocabulary and context set on the fly, with no hand-holding, and keep when a word was learned, how it was refined, and when it became a different word.

## Design
* A **sense** is the unit: `wn:<pos><offset>` (a WordNet sense; base counts read exactly from NLTK) or `live:<word>.<pos>.<nn>` (a sense the Monad learned).
* The 19-vector of a sense is **derived**: `compress_count(base count + edges added)` per relation, the definition in `wordnet_boxkite.context_vector`. Adding a relation edge is therefore the only way a vector changes, and the edge is kept.
* Reciprocals are written both ways (hypernym ↔ hyponym, instance, member/substance/part holonym ↔ meronym: exact on all of WordNet 3.0, `FourthAgePaper/ScalarContextPropagation/bench/dim19.txt`); `attributes`, `also_sees`, `verb_groups`, `similar_tos` are symmetric. `entailments`, `causes` and the three domain relations have no stored inverse.
* An append-only **journal** (JSONL) is the memory: `seen` (an unknown token met), `created`, `edge`, `support` (heard again), `split` (one sense became two). Replaying it rebuilds the same state (tested).
* `hear(text)` reads definitional sentences by pattern (Hearst 1992): "X is a kind of Y", "Y such as X, Z and W", "X is part of Y", "X is a member of Y", "X is made of Y", "X has a Y", "X causes Y" (verb–verb only), "X is similar to Y". Plurals are lemmatised (WordNet morphy, else a conservative strip).
* `propose_splits` / `split_sense`: a word whose hypernym targets are far apart in the WordNet taxonomy (path similarity < 0.15) is proposed for splitting; `split_sense` moves edges to a new sense and journals when.
* `dirty_frames()` gives the changed senses as **sedenion-shaped frames**: anchor e0 (most edges in its connected component), at most 15 others, a spanning tree of at most 15 relation edges; a larger context yields several frames sharing the anchor.
* `repack_monad3c(src, dst, rows)` writes the changed senses into a **copy** of `monad3_c.bin` (the source is never modified; refused if `dst == src`), adding new words to the word table and leaving the English field, the A-matrix and the phonetics byte for byte intact.

## Transcript (run 2026-11-21)
```
hear> A phasor is a kind of vector.        -> phasor --hypernyms--> vector   NEW
hear> Vectors such as spinors and twistors.-> spinor, twistor --hypernyms--> vector  NEW
hear> A glorp is a kind of institution.   -> glorp --hypernyms--> institution NEW
hear> A glorp is a kind of slope.          -> glorp --hypernyms--> slope      NEW   (vector now hypernyms=1, hyponyms=3 on the vector sense)
hear> A phasor is a kind of vector.        -> support (heard twice)
hear> A wheel is part of a car.            -> wheel --part_holonyms--> car    NEW
phasor : live:phasor.n.01  vec {hypernyms:1}  gamma_radial -0.9049
glorp  : live:glorp.n.01   vec {hypernyms:2}  gamma_radial -0.8184   propose_splits -> [[institution], [slope]]
$ ptol -M phasor      (the C binary, on the repacked copy)
  store: …/monad3_c.bin  (347125 words, 164283 eng, 146750 wn, 123455 phon, 2248064 edges)
  phasor: eng_idx=-1  wn_idx=98898  phon_idx=-1
  wn: pos=1  vec19=[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
  gamma_radial: -0.904887
```
Speed: 7 sentences in 2.65 s including the one-off WordNet load; repack of the 48 MB store 1.9 s.

## Measured limits (stated, not hidden)
* **Definitional text only.** On 1.64 MB of the standard testing corpus (narrative prose, 150 KB from each of 11 works) the reader found 3 edges, none sound (boilerplate and a list of authors). A child learns from running prose; this reader does not. Learning from everything the Monad hears needs the extractor and the orbweaver to supply relation evidence, or distributional evidence from the co-occurrence field; neither is built here.
* **Single-token noun heads**, English patterns, no compounds.
* **Sense choice** for an existing word is the first WordNet sense of the needed part of speech (recorded as `resolution`); context disambiguation is not done here.
* **One row per word in the bin.** The shipped store's own entry for "tree" is a verb sense (`vec19=[1,0,…]`, `ptol -M tree`), not the noun; a changed sense that is not the bin's own entry is written as the row `word#<pos>:<offset>`.
* **New words** have no phonetic row and no English co-occurrence row from this file.
* **No sedenion carrier for the 19.** No algebra has 19 dimensions, and the 117,659 WordNet 3.0 vectors have rank 19 (`bench/dim19.txt`), so no linear map into 16 reals is injective. What the sedenion window carries is a frame of 16 senses, not 19 numbers in 16.

## Use
```
v = LiveVocabulary(journal_path='vocab.jsonl', base_bin='PtolC/monad3_c.bin')
v.hear("A phasor is a kind of vector.")
v.lookup('phasor'); v.history('phasor'); v.dirty_frames()
repack_monad3c('PtolC/monad3_c.bin', 'PtolC/monad3_c.new.bin', v.bin_rows())
```
Run with `VAPMIP/.venv/bin/python` (needs NLTK and the WordNet corpus).
