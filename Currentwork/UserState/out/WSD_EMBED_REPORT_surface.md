# Disambiguation, both ways (SemCor gold senses)

train (confirmed senses for the usage memory) 4000 sentences, validation 150, test 400. Embedding = all-MiniLM-L6-v2, context = the real sentence text, sense = "<lemma>: <WordNet gloss>".

| method | test accuracy | ambiguous tokens |
|---|---|---|
| rank prior only (first sense) | 0.515 | 4026 |
| embedding only | 0.203 | 4026 |
| usage memory only | 0.666 | 4026 |
| rank + embedding | 0.515 | 4026 |
| rank + usage | 0.554 | 4026 |
| all three, weights fitted on validation (0.5, 0, 2) | 0.670 | 4026 |
