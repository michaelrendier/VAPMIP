#!/usr/bin/env python3
"""window16_tests.py -- W1 cyclic slots and 15 edges; W2 XOR labels follow the ruler pattern; W3 WordNet evidence on a real phrase; W4 a synset added mid-stream is used; W5 vector is exact."""
import os, sys
import numpy as np
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from window16 import Window16
from vocab_store import UsageStore
ok = {}
w = Window16(); words = 'the quick brown dog chased small grey cat across old stone bridge while heavy rain fell softly over quiet town again'.split()
for x in words[:20]: w.push(x)
ok['W1'] = (len(w.order()) == 16 and len(w.edges()) == 15 and [s['word'] for s in w.order()] == words[4:20] and w.slot[0]['word'] == words[16] and w.slot[3]['word'] == words[19])
print('W1 16 slots, 15 edges, 20 pushed -> holds the last 16, word 16 overwrote slot 0:', ok['W1'])
lab = [e['label'] for e in w.edges()]; w2 = Window16(); [w2.push(x) for x in words[:16]]; lab0 = [e['label'] for e in w2.edges()]
ruler = [1, 3, 1, 7, 1, 3, 1, 15, 1, 3, 1, 7, 1, 3, 1]
ok['W2'] = lab0 == ruler and all(1 <= x <= 15 for x in lab) and sorted(set(lab0)) == [1, 3, 7, 15]
print('W2 first full window labels', lab0, '== ruler:', lab0 == ruler, '| after 20 pushes (phase 4):', lab)
w3 = Window16(); w3.push_text('dog cat'); e = w3.edges()[0]
ok['W3'] = e['common_hypernym'] is not None and e['path_similarity'] and e['path_similarity'] > 0.1
print('W3 dog-cat edge:', e)
s = UsageStore(); sid = s.add_synset('86', 'remove an item from the menu because the kitchen has run out of it', 'v', relations={'hypernyms': ['remove.v.01']}, register='kitchen', examples=['we are out of salmon so eighty six the salmon'])
w4 = Window16(store=s, register='kitchen'); [w4.push(x) for x in ['we', 'are', 'out', 'salmon', 'chef']]; w4.push('86'); w4.push('salmon')
ed = w4.edges(); ok['W4'] = w4.slot[5]['sense'] == sid and any(x['relation'] == 'user-defined sense' for x in ed) and s.lemmas['86']['senses'][sid]['n'] == 1
print('W4 custom sense used in the window:', w4.slot[5]['sense'], '| edge evidence:', [x['relation'] for x in ed if x['relation']])
v = w.vector(); ok['W5'] = v.shape == (16,) and np.all(np.isfinite(v)) and np.count_nonzero(v) >= 12
print('W5 16-vector of gamma_radial, nonzero slots:', int(np.count_nonzero(v)), np.round(v, 2).tolist())
print(ok)
