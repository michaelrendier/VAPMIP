# 05 — The Baseline, and the fitting rules

**Job.** Define the Chinese reference everything is placed against, say what is frozen, and state what "fitting" means in this construction.

## What The Baseline is
Written Mandarin in Traditional script. **No Cantonese, Hokkien or Min sources.** It is the foundation of the construction: the Fresh Start Protocol returns to it, the way `fresh_start.sh` once returned to `monad_English.bin`.

Contents (v1 scope is Cody's call; the options are A: characters + MOE-learned store, B: A + the Shuowen grounding kernel, C: B + the Vital-article topic labels):

| source | what it gives | measured |
|---|---|---|
| MOE 重編國語辭典修訂本 (`zh/moedict`) | 161 194 headwords with Chinese definitions and examples | 12 515 distinct Han characters; 227 cover 50 %, 1 640 cover 90 %, 4 720 cover 99 %; 53.7 % of headwords have two characters |
| Unihan (`zh/structure`) | 102 999 characters, radical-stroke, variants, readings | 9 810 in the international core set |
| makemeahanzi, cjkvi-ids | component structure | 72.8 % of 9 574 characters pictophonetic; 88 937 decompositions |
| 說文解字 (`zh/classical`, CC0, Simplified-mixed) | each character defined by other characters | 9 453 heads; one cyclic core of 2 153 characters; 6 922 acyclic |
| Vital Articles, Level 3 → zh.wikipedia, zh-tw (`zh/vital`) | topic-labelled Traditional prose | 1 000 articles in 11 categories |

Spot checks of purity: no Cantonese content in the MOE dictionary (the flagged characters are classical Mandarin uses); a handful of Taiwan-Mandarin loans from Hokkien (囝仔, 歌仔戲); Simplified-only characters ≈ 0.002 % of the text.

## Frozen
The Baseline is a **read-only store + manifest** (source hashes, `MANIFEST.tsv`) with a push-first assessment, archived under the Fresh Start Protocol. Nothing writes to it. Fits are **overlays** that can be deleted; Fresh Start deletes the overlays and restores the Baseline byte for byte. *(Status: not built yet.)*

## Fitting (the scoped exception)
English (US, UK) and the other languages are fitted **to** The Baseline, never the reverse. A fit is permitted because it:
1. is computed from Baseline data by a stated procedure, with no hand-picked constant;
2. is listed in a **ledger** (value, procedure, data used);
3. **keeps its residual**: what does not map is recorded, never dropped (couch is a composition, not an atom: that is a result);
4. is an overlay on The Baseline and never changes it;
5. is tested on mappings it was not built from.

A value put in by hand with none of these is a guess, and is not allowed. Mathematics work stays no-fit.

## Topic Space
"My Topic Space" is the geometry of The Baseline's slots and links, not WordNet's. Which topic labels define it (the 11 Vital-article categories, the 19 chapters of the 爾雅, radical classes) is open.


## Test bins
The first frozen pair, `test_chinese_v1.0.bin` and `test_english_v1.0.bin`, is described in [09](09_the_test_bins.md). It is not yet The Baseline: nothing has been fitted.
