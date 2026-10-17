# The standard testing corpus of the semantic orbweaver

Chosen 2026-10-17. Every semantic-orbweaver function (the seven-slot decomposition, candidate seeding, the S score, the
epicycle monitor's feeds) is tested against **this** corpus and no other, so results from different dates stay comparable.
Never edit the texts or the prompt files to fit a result; a new corpus version gets a new directory.

## What is here

| path | what |
|---|---|
| `texts/` | 11 public-domain works, mirrored byte for byte (Project Gutenberg headers kept). Listed in `MANIFEST.md`; sha256 and sizes in `MANIFEST.json`. 8.7 MB. |
| `prompts_corpus.jsonl` | 134 sentences sampled from the 9 prose works (about 15 each), balanced by type: 36 question, 26 imperative, 36 copular, 36 statement. The type label is a punctuation and first-word heuristic, **not** an annotation. |
| `prompts_chat.jsonl` | 24 hand-written conversational prompts: the eight from the May 2026 run (`what is your name` and friends), the paper's prompts, and cases chosen to stress the roles (greetings, copulas, wh-gaps, embedded clauses, negation, fragments). |
| `answers_seed.jsonl` | **Reference answers**: the seven-slot decomposition of all 24 chat prompts and 16 corpus sentences, provided by the transformer (Claude Sonnet 5.5, 2026-10-17). **Model-provided and unreviewed; not human gold.** Engineer towards them, and correct them where Cody's reading differs. |
| `build_corpus.py` | Rebuilds `MANIFEST.*` and `prompts_corpus.jsonl` deterministically (seed 20261017) from `texts/`. |

## The answer format (`answers_seed.jsonl`)

One JSON object per prompt, using the seven deconstruction names (see `../../docs/semantic_orbweaver_notes.md`):

* `SHELL`: `act` (whQuestion, ynQuestion, statement, imperative, greet, thanks, other) and `polarity` (pos, neg).
* `ANCHOR`: the topic, the given, the anaphor; `(you)` marks an implicit addressee.
* `SPAN`: `relation` (an event verb lemma, `NAME` for a copula of identity or attribution, `LOCATE` for a locative copula, `EXIST`, or null), `claim` (the complement; `<gap:...>` is the thing a wh-question asks for), `frame` (the scope; a gap can sit here, as in "why"). A list when there are two clauses.
* `SCAFFOLD`: auxiliaries, modals, tense and voice carriers. `ELABORATE`: attributive modifiers. `HOOK`: names, numbers, specifics. `WRAP`: connectives and complementisers.
* `<clause: ...>` marks an embedded clause that is itself decomposed (not yet expanded in the seed set).

Conventions that are judgement calls and may be overruled: formulaic greetings are a bare `SHELL`; "about X" is a frame; a
predicate adjective is the `SPAN` claim while an attributive one is `ELABORATE`; a vocative name is a `HOOK`.

## What was left out on purpose

The large ebook collections under `~/Documents` (the `eBooks` zips, `books/eBooks/Fantasy`) and `~/Desktop/Desktop Archive` are
overwhelmingly modern, copyrighted novels, and personal files: none of that is mirrored or pushed. Only works that are in the
public domain worldwide were taken. `~/.ptolemy/.ptoltemp/75871-0.txt` (a Project Gutenberg text of unidentified title) was not used.

## The texts are mixed in encoding

Decoded with a fallback chain (utf-8-sig, cp1252, latin-1); the files themselves are untouched. The `Chesterton: Incredulity` text is
from Project Gutenberg of Australia (author died 1936); the rest are Project Gutenberg.
