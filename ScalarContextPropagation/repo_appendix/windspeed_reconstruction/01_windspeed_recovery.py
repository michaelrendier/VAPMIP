import sys, os, math
sys.path.insert(0, os.path.expanduser("~/Projects/ThePlace/ValaQuenta/modules/box_kite"))
sys.path.insert(0, os.path.expanduser("~/Projects/ThePlace/VAPMIP"))
import maths as bk
import monad_english_io as meio
from wordnet_boxkite import spelling_code, context_code, next_prime, LETTER_PRIMES, CONTEXT_PRIMES
import nltk
from nltk.corpus import wordnet as wn

# ---------- WINDSPEED B: recovered context gamma_radial (WordNet-calibrated) ----------
def windspeed_B(word):
    syns = wn.synsets(word)
    if not syns:
        return None
    s = syns[0]
    ccode = context_code(s)
    scode = spelling_code(word)
    full_code = scode * ccode
    full_addr = next_prime(full_code)
    delta = full_addr - full_code
    # RECOVERY (as specified): full_addr, delta, word -> spelling -> divide out -> context_code
    recovered_full = full_addr - delta
    recovered_spelling = spelling_code(word)          # from text alone
    recovered_context = recovered_full // recovered_spelling
    assert recovered_full % recovered_spelling == 0, "spelling does not divide cleanly"
    assert recovered_context == ccode, "recovery mismatch"
    log_code = sum(v * math.log(p) for v, p in zip(
        [1]*0, [1]*0))  # placeholder, real fold below
    # gamma_radial fold, matching notebook 05's LOG_ANCHOR convention
    from wordnet_boxkite import RELATION_METHODS
    _HYP = RELATION_METHODS.index("hyponyms")
    LNP = [math.log(p) for p in CONTEXT_PRIMES[:len(RELATION_METHODS)]]
    LOG_ANCHOR = sum(LNP[i] for i in range(len(RELATION_METHODS)) if i != _HYP)
    # factor recovered_context back over CONTEXT_PRIMES to get the 19-vector
    v = [0]*len(RELATION_METHODS)
    rc = recovered_context
    for i, p in enumerate(CONTEXT_PRIMES[:len(RELATION_METHODS)]):
        while rc % p == 0:
            rc //= p
            v[i] += 1
    lc = sum(v[i]*LNP[i] for i in range(len(RELATION_METHODS)))
    if lc <= 0:
        return 0.0, ccode, full_addr, delta
    gr = math.tanh(0.5*math.log(lc/LOG_ANCHOR))
    return gr, ccode, full_addr, delta

# ---------- WINDSPEED A: A-matrix basin drift (operational stand-in, flagged) ----------
def windspeed_A(word, me):
    b = me.basin([word], k=1, idf=True)
    if not b:
        return 0.0
    top = max(b.values())
    return math.tanh(top / 10.0)   # normalized into (-1,1) for comparability, documented choice

me = meio.read()
WORD = "tree"
wA = windspeed_A(WORD, me)
wB, ccode, full_addr, delta = windspeed_B(WORD)
print(f"word={WORD!r}")
print(f"  windspeed_A (basin drift, tanh(top_pull/10)) = {wA:.6f}")
print(f"  windspeed_B (recovered context gamma_radial)  = {wB:.6f}")
print(f"  context_code={ccode}  full_addr={full_addr}  delta={delta}")
