import sys, glob, re, time
sys.path.insert(0, '.')
import english_stats as ES
files = sorted(glob.glob('Currentwork/Wernicke/corpus/texts/*.txt'))
toks_by = [re.findall(r"[a-z]+(?:'[a-z]+)?", open(f, encoding='utf-8', errors='ignore').read().lower()) for f in files]
held = []; train = []
for ts in toks_by:
    cut = int(len(ts) * .95); held.append(ts[cut:cut + 3000]); train.append(ts[:min(cut, 60000)])
heldtxt = ' '.join(' '.join(h) + ' .' for h in held)
ch = ES.ContextHash()
for label, kw in (('word+class+unigram (with context hash)', dict(chash=ch)), ('word pairs + unigram only (no hash)', dict())):
    s = ES.EnglishStats(**kw)
    print(label)
    for r in range(4):
        t = time.time()
        for ts in train:
            a = int(len(ts) * r / 4); b = int(len(ts) * (r + 1) / 4); s.observe(' '.join(ts[a:b]))
        bits = n = 0
        for h in held:
            bb, nn = s.bits(' '.join(h)); bits += bb; n += nn
        print('  round', r + 1, 'tokens %d vocab %d bits/word %.2f (%.0fs)' % (s.n_tokens, len(s.unigram), bits / n, time.time() - t), flush=True)
s = ES.EnglishStats(chash=ch)
for ts in train: s.observe(' '.join(ts))
for lv in ES.LEVELS:
    bits = n = 0
    for h in held:
        bb, nn = s.bits(' '.join(h), lv); bits += bb; n += nn
    print('level', lv, 'bits/word %.2f' % (bits / n))
print('poll:', {k: v for k, v in s.poll().items() if k != 'top_words'})
