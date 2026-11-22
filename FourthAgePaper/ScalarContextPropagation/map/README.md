# Scalar Boxkite context map (2026-11-21)

The exhaustive map of the context hash over WordNet 3.0 (NLTK, 117,659 synsets, 206,978 lemma-in-synset rows), computed from the data with `scalar_context_map.py` (run from `VAPMIP/` with `.venv/bin/python`). Definitions are those of `wordnet_boxkite.py`: `vec19`, `context_code` (Π p_i^vec19_i), `context_addr` (next prime), `gamma_radial`. This is the context half of the hash; the spelling half (`spelling_code`) is a separate number and is not in the table.

| file | what |
|---|---|
| `scalar_context_map.tsv.gz` | **the table**: one row per lemma in a synset: lemma, pos, synset, offset, class, density basin, attractor basin, gamma_radial, vec19, context_code, context_addr, delta (2.3 MB compressed) |
| `CLASS_MAP.md` | one row per exact context class (1,276): size, basins, gamma, vector, code, address, POS mix, examples |
| `BASIN_MAP.md` | the two basin readings below |
| `summary.json` | the counts |

## Pictures
`landscape_2d.png` (x = Wernicke, 1 + γ; y = Broca, number of non-zero relations; size = log synsets; colour = attractor basin), `landscape_3d.png` (the spatial-simulation **3D overview function** on the 19-D class vectors: the three viewer axes are the directions of greatest spread; 70% of the variance is shown; loadings in the title), `landscape_words.png` (the senses of four words). The comb-like columns are the hyponym counts; the 3D axes are mostly hyponym count, then part-meronym versus instance-hyponym: the landscape is organised by branching and by part/instance structure.

## Words with several contexts (`polysemy.json`)
147,306 lemmas; 26,876 have two or more senses; **19,270 sit in two or more distinct context classes** and 4,022 in two or more attractor basins; one lemma reaches 26 classes. The widest gamma spreads (0.786) are lemmas such as `city`, `state`, `land`, `metropolis`: a hub sense and a leaf sense of the same word lie at opposite ends. So a lemma is not a point but a set of points; the sense a text means is the one that lies in the basin of the other words around it.

## Lorenz–Stirling (found 2026-11-21)
The author's code is `Currentwork/SemPriCon/orbweaver/LorenzStirling.py` (identical to `PtolemyDesktop/Archimedes/Maths/LorenzStirling.py`): the degree-9 Stirling polynomial S10 (UF `om.ufm` V=10) and a Lorenz trajectory. **As shipped it does not produce basins**: it iterates z → log|S10(1/z + p1)| and labels the final |z| (`int(|z|·7) % 8 + 1`); on its own default map every point is "extinct" (bail 4.0), and with a larger bailout everything is one basin. It never runs Newton's method, which is what the wiki (UF_NewtonBasins) and the primer (`PTOLEMY_DOCS/042`) describe.
`newton_stirling.py` implements the described object: Newton basins of S10. S10 has nine roots with a **double root at −1**, so **eight distinct basins** (roots −1.498, −1.454 ± 0.370i, −1, 0, 1.3059, 2.9802, 5.12). With Z = (1 + γ) + i·(non-zero relations), the context points fall almost wholly in one basin: **1,261 of 1,275 classes in the basin of root −1, 14 in the basin of root 0**, the rest of the eight basins empty; 211 of 140,117 lemmas have senses in both. The points occupy a strip (Wernicke 0.1–0.9, Broca 1–7) where the polynomial's basins are coarse; the intricate region is |z| of about 1.5 to 5. Where the points sit in that plane is the scale choice (the "lighting" of the mirror), and I did not tune it. Pictures: `newton_stirling_basins.png`, `newton_stirling_plane.png`.

## What the map shows
* **1,276 exact classes for 117,659 synsets.** Everything in a class shares one code, one address and one gamma. Class 1 (`hypernyms=1`, a leaf with one parent) holds 45,441 synsets (38.6%); the top 10 classes hold 77.5%.
* **Density basins** (valleys of the smoothed histogram of gamma): 15, ordered by branching (`hyponyms` = 0, 1, 2, … 6); gamma spans only −0.905 … −0.119.
* **Attractor basins** (classes joined when their vectors differ by 1 in one coordinate: 2,563 edges, 86 connected components; each class flows to its most populated neighbour): **171 basins, and one holds 970 of the 1,276 classes and 103,944 synsets (88%).** The second is the adjective satellites (`similar_tos=1`, 13,202 synsets). The rest are small and are hubs of one kind: named countries, professions, animal orders, arts.
* **So the context hash alone does not separate the neighbourhoods of most words**: 88% of the language is one basin. What separates words is the *identity* of their relation targets (the code's own comment: "target-identity sensitivity is real future work"), which is why the sedenion window takes its candidates from relation neighbours and uses the class and gamma only as labels.
* 7,925 synsets (6.7%) have no relation among the 19 (class 3; gamma undefined): mostly adjectives and adverbs, whose links are lemma-level (antonym, derivation, pertainym) and not in the 19.
