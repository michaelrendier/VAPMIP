# Scalar Boxkite context map (2026-11-21)

The exhaustive map of the context hash over WordNet 3.0 (NLTK, 117,659 synsets, 206,978 lemma-in-synset rows), computed from the data with `scalar_context_map.py` (run from `VAPMIP/` with `.venv/bin/python`). Definitions are those of `wordnet_boxkite.py`: `vec19`, `context_code` (Π p_i^vec19_i), `context_addr` (next prime), `gamma_radial`. This is the context half of the hash; the spelling half (`spelling_code`) is a separate number and is not in the table.

| file | what |
|---|---|
| `scalar_context_map.tsv.gz` | **the table**: one row per lemma in a synset: lemma, pos, synset, offset, class, density basin, attractor basin, gamma_radial, vec19, context_code, context_addr, delta (2.3 MB compressed) |
| `CLASS_MAP.md` | one row per exact context class (1,276): size, basins, gamma, vector, code, address, POS mix, examples |
| `BASIN_MAP.md` | the two basin readings below |
| `summary.json` | the counts |

## What the map shows
* **1,276 exact classes for 117,659 synsets.** Everything in a class shares one code, one address and one gamma. Class 1 (`hypernyms=1`, a leaf with one parent) holds 45,441 synsets (38.6%); the top 10 classes hold 77.5%.
* **Density basins** (valleys of the smoothed histogram of gamma): 15, ordered by branching (`hyponyms` = 0, 1, 2, … 6); gamma spans only −0.905 … −0.119.
* **Attractor basins** (classes joined when their vectors differ by 1 in one coordinate: 2,563 edges, 86 connected components; each class flows to its most populated neighbour): **171 basins, and one holds 970 of the 1,276 classes and 103,944 synsets (88%).** The second is the adjective satellites (`similar_tos=1`, 13,202 synsets). The rest are small and are hubs of one kind: named countries, professions, animal orders, arts.
* **So the context hash alone does not separate the neighbourhoods of most words**: 88% of the language is one basin. What separates words is the *identity* of their relation targets (the code's own comment: "target-identity sensitivity is real future work"), which is why the sedenion window takes its candidates from relation neighbours and uses the class and gamma only as labels.
* 7,925 synsets (6.7%) have no relation among the 19 (class 3; gamma undefined): mostly adjectives and adverbs, whose links are lemma-level (antonym, derivation, pertainym) and not in the 19.
