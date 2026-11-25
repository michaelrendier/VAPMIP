# Disambiguation, both ways (SemCor gold senses)

train (confirmed senses for the usage memory) 4000 sentences, validation 299, test 800. Embedding = all-MiniLM-L6-v2, context = the sentence's tagged content lemmas, sense = "<lemma>: <WordNet gloss>".

| method | test accuracy | ambiguous tokens |
|---|---|---|
| rank prior only (first sense) | 0.518 | 8119 |
| embedding only | 0.307 | 8119 |
| usage memory only | 0.667 | 8119 |
| rank + embedding | 0.518 | 8119 |
| rank + usage | 0.561 | 8119 |
| all three, weights fitted on validation (0.5, 2, 2) | 0.679 | 8119 |
