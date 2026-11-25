#!/usr/bin/env python3
"""export_c_monad_data.py -- data the C monad (ptol.c + monad_harness.c) needs from the Python monad.   (2026-11-25)

Run with VAPMIP/.venv:   .venv/bin/python PtolC/tools/export_c_monad_data.py
Writes next to this script's parent (PtolC/):
    user_state.bin       the usage ridge of Currentwork/UserState/prompt_to_state.py: TF-IDF (1-2 grams, sublinear, l2) -> 14 poles; + calibration gain/base;
                         + spread[14] = the median per-pole disagreement of the two Python meters over the calibration corpus (the C meter has only one meter)
    harness_data.txt     C source for monad_harness.c (the stop-word list of the usage store)
    ptol_voice_data.txt  C source for the tables ptol.c needs (irregular verb forms, cam_encode word sets); spliced into ptol.c between
                         /* BEGIN GENERATED ptol_voice_data */ and /* END GENERATED ptol_voice_data */ by tools/splice_voice_data.py
Nothing here runs downloaded code; the model is a joblib file made by this project.
"""
import json, os, random, re, struct, sys
import numpy as np
H = os.path.dirname(os.path.abspath(__file__)); PC = os.path.dirname(H); ROOT = os.path.dirname(PC)
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'Currentwork', 'UserState'))

def user_state_bin():
    import joblib
    from prompt_to_state import PromptToState
    US = os.path.join(ROOT, 'Currentwork', 'UserState')
    vec, mdl = joblib.load(os.path.join(US, 'usage_model.joblib'))
    P = PromptToState(); gain, base = P.gain, P.base
    random.seed(7); rows = [json.loads(l) for l in open(os.path.join(US, 'corpus.jsonl'))]; txt = []
    for src in ('goemotions', 'nps_chat', 'proj_chat'):
        t = [r['text'] for r in rows if r['source'] == src]; random.shuffle(t); txt += t[:400]
    sp = np.array([np.minimum(9.0, P.raw_dose(P.mask_aspect(t))[1] * gain) for t in txt]); spread = np.median(sp, axis=0)
    terms = sorted(vec.vocabulary_.items(), key=lambda kv: kv[0]); n = len(terms)
    idf = np.array([vec.idf_[i] for _, i in terms], np.float32)
    coefT = np.array([mdl.coef_[:, i] for _, i in terms], np.float32)                 # feature-major: n x 14
    blob = b''.join(t.encode('utf-8') + b'\0' for t, _ in terms)
    with open(os.path.join(PC, 'user_state.bin'), 'wb') as f:
        f.write(b'USTATE1\0'); f.write(struct.pack('<III', n, 14, len(blob)))
        for arr in (gain, base, spread, mdl.intercept_): f.write(np.asarray(arr, '<f8').tobytes())
        f.write(blob); f.write(((8 - (len(blob) % 8)) % 8) * b'\0'); f.write(idf.tobytes()); f.write(coefT.tobytes())
    print('user_state.bin', n, 'features; spread', np.round(spread, 2).tolist())

# ---- the regular-verb rules, the SAME as ptol.c's (kept in step by tests/test_c_parity.py) -----------------------------------
V = set('aeiou')
def _cvc(w):
    return len(w) >= 3 and w[-1] not in V and w[-1] not in 'wxy' and w[-2] in V and w[-3] not in V and sum(1 for i, c in enumerate(w) if c in V and (i == 0 or w[i-1] not in V)) == 1
def reg(w, tag):
    if tag == 'VBZ':
        if re.search(r'(s|x|z|ch|sh)$', w): return w + 'es'
        if len(w) > 1 and w[-1] == 'y' and w[-2] not in V: return w[:-1] + 'ies'
        return w + 's'
    if tag in ('VBD', 'VBN'):
        if w.endswith('e'): return w + 'd'
        if len(w) > 1 and w[-1] == 'y' and w[-2] not in V: return w[:-1] + 'ied'
        if _cvc(w): return w + w[-1] + 'ed'
        return w + 'ed'
    if tag == 'VBG':
        if w.endswith('ie'): return w[:-2] + 'ying'
        if w.endswith('e') and not w.endswith(('ee', 'ye', 'oe')): return w[:-1] + 'ing'
        if _cvc(w): return w + w[-1] + 'ing'
        return w + 'ing'

def voice_data():
    from nltk.corpus import wordnet as wn
    from lemminflect import getInflection
    import monad as M
    lemmas = sorted({l for s in wn.all_synsets('v') for l in s.lemma_names() if l.isalpha() and l.islower() and 2 < len(l) < 20} | {'be', 'have', 'do', 'go'})
    tab = []
    for l in lemmas:
        f = {t: (getInflection(l, tag=t) or [l])[0] for t in ('VBD', 'VBN', 'VBG', 'VBZ')}
        if l in ('be', 'have') or any(f[t] != reg(l, t) for t in f): tab.append((l, f['VBD'], f['VBN'], f['VBG'], f['VBZ']))
    out = ['/* irregular or rule-breaking verb forms: lemma, VBD, VBN, VBG, VBZ (from lemminflect; every lemma the regular rules get right is left out) */',
           'static const char *const VERB_FORMS[][5] = {']
    out += ['    {"%s","%s","%s","%s","%s"},' % t for t in tab]; out += ['};', 'static const int N_VERB_FORMS = %d;' % len(tab), '']
    def arr(name, s): return 'static const char *const %s[] = {%s};\nstatic const int N_%s = %d;' % (name, ','.join('"%s"' % w.replace('"', '\\"') for w in sorted(s)), name, len(s))
    for nm in ('_PRONOUNS', '_AUXILIARIES', '_CONJUNCTS', '_TIME', '_QUESTION', '_NEGATION', '_DETERMINERS', '_META', '_AFF_POS', '_AFF_NEG'):
        out.append(arr('CAM' + nm, getattr(M, nm)))
    out.append('static const char *const CAM_NOUN_SUFF[] = {%s};' % ','.join('"%s"' % s for s in M._NOUN_SUFF)); out.append('static const int N_CAM_NOUN_SUFF = %d;' % len(M._NOUN_SUFF))
    out.append('static const char *const CAM_ADJ_SUFF[] = {%s};' % ','.join('"%s"' % s for s in M._ADJ_SUFF)); out.append('static const int N_CAM_ADJ_SUFF = %d;' % len(M._ADJ_SUFF))
    import sedenion_window as SW
    from vocab_store import STOP
    for nm, st in (('SW_DET', SW.DET), ('SW_PREP', SW.PREP), ('SW_CONJ', SW.CONJ_W), ('SW_AUX', SW.AUX), ('SW_PRON', SW.PRON)):
        out.append(arr(nm, st))
    open(os.path.join(PC, 'harness_data.txt'), 'w').write(arr('VS_STOP', STOP) + '\n')
    out.append('static const double CAM_GAP = %.17g;' % M.GAP)
    open(os.path.join(PC, 'ptol_voice_data.txt'), 'w').write('\n'.join(out) + '\n'); print('verb forms:', len(tab), 'of', len(lemmas), 'lemmas')

def voice_lex_bin():
    """voice_lex.bin: every single-word lowercase WordNet lemma -> mask of the parts of speech it has (n=1 v=2 a=4 r=8), the part of speech of its FIRST synset
    (nltk's wn.synsets(w)[0], 1 n 2 v 3 a 4 r), and that synset's 19 relation counts (wordnet_boxkite.context_vector).  monad3_c.bin keeps one lossy entry per word
    ('dog' is a verb there; 'rules' is absent); the C voice needs the nouns/verbs/adjectives a word really is."""
    from nltk.corpus import wordnet as wn
    import wordnet_boxkite as WB
    names = sorted({l for l in wn.all_lemma_names() if l.isalpha() and l.islower() and l.isascii() and 1 < len(l) < 40})
    rows = []
    for l in names:
        ss = [s for s in wn.synsets(l) if l in [x.lower() for x in s.lemma_names()]]        # DIRECT senses only: wn.synsets() also returns the senses of l's lemma ('roots' -> root.v.01), which would make 'roots' a verb lemma
        if not ss: continue
        mask = 0
        for s in ss: mask |= {'n': 1, 'v': 2, 'a': 4, 's': 4, 'r': 8}[s.pos()]
        s0 = ss[0]; pos1 = {'n': 1, 'v': 2, 'a': 3, 's': 3, 'r': 4}[s0.pos()]
        rows.append((l, mask, pos1, [max(-127, min(127, int(x))) for x in WB.context_vector(s0)]))
    blob = b''.join(r[0].encode() + b'\0' for r in rows); offs = np.cumsum([0] + [len(r[0]) + 1 for r in rows[:-1]]).astype('<u4')
    with open(os.path.join(PC, 'voice_lex.bin'), 'wb') as f:
        f.write(b'VLEX1\0\0\0'); f.write(struct.pack('<II', len(rows), len(blob))); f.write(blob); f.write(((8 - (len(blob) % 8)) % 8) * b'\0')
        f.write(offs.tobytes()); f.write(bytes(r[1] for r in rows)); f.write(bytes(r[2] for r in rows)); f.write(np.array([r[3] for r in rows], '<i1').tobytes())
    print('voice_lex.bin', len(rows), 'words')


if __name__ == '__main__':
    voice_data()
    if '--lex' in sys.argv: voice_lex_bin()
    if '--no-model' not in sys.argv and '--lex' not in sys.argv: user_state_bin()
