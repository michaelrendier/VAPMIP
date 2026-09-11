"""
build monad_sentences.json — the generative grammar + context index.

Schema (v2):
  meta
  sails          pattern -> {slots:[{role,deprel,themrole,head}], order,
                             rhythm_affinity, frequency, example}
  speech_acts    act -> {sail, focus, ...}          (from sails.py)
  register_bands [name, lo, hi] over |gamma_radial| (context_hash_v2 scale)
  np_grammar     phrase-level sub-ring templates
  copular        linking verb -> its extra sails
  verbs          lemma -> {sails, maps:{sail:{themrole:slot}}, context_hash,
                           corpus_count}

context_hash per verb sense: {code_omega, log_code, gamma_radial, band}
from context_hash_v2 (WordNet loaded with an sklearn-import shim so nltk's
broken sklearn path does not abort it).
"""
from __future__ import annotations
import json
import os
import sys
from collections import Counter
from . import conllu
from .frames import (frame_of, verbnet_index, propbank_index, slot_maps,
                     selrestrs, COPULAR, PATTERNS)
from .shadow import reduce, check
from .sails import SAILS, RHYTHM_AFFINITY, SPEECH_ACTS, REGISTER_BANDS, band_of
from . import sem_hash

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "monad_sentences.json")

NP_GRAMMAR = {
    "plain":      ["det?", "N"],
    "modified":   ["det?", "amod*", "N", "pp*"],
    "possessive": ["nmod:poss", "N"],
    "appositive": ["N", ",", "appos", ","],
    "bare_plural": ["N"],
}


def _wordnet():
    for m in ("sklearn", "sklearn.feature_extraction", "sklearn.feature_extraction.text"):
        sys.modules.setdefault(m, None)
    from nltk.corpus import wordnet as wn
    return wn


def _context_hashes(lemmas):
    try:
        wn = _wordnet()
        import context_hash_v2 as ch
    except Exception as e:                                # noqa: BLE001
        print(f"  context hash unavailable ({e!r}); leaving null")
        return {}
    out = {}
    for lem in lemmas:
        ss = wn.synsets(lem.replace(" ", "_"), pos="v")
        if not ss:
            continue
        s = ss[0]
        try:
            gr = ch.gamma_radial(s)
            out[lem] = {
                "sense": s.name(),
                "code_omega": ch.code_omega(s),
                "log_code": round(ch.log_code(s), 4),
                "gamma_radial": round(gr, 4),
                "band": band_of(abs(gr)),
            }
        except Exception:                                 # noqa: BLE001
            continue
    return out


def run(with_hashes: bool = True):
    sail_freq = Counter(); sail_ex = {}
    verbs_seen = Counter(); verd = Counter(); n = 0
    filler_freq = Counter()          # lemma -> count, for NOUN/PROPN/ADJ
    for split in ("train", "dev", "test"):
        for corp in (conllu.EWT, conllu.GUM):
            p = corp[split]
            if not os.path.exists(p):
                continue
            for s in conllu.read(p):
                sh = reduce(s)
                if sh is None:
                    continue
                n += 1
                sail_freq[sh.pattern] += 1
                sail_ex.setdefault(sh.pattern, s.text[:120])
                verbs_seen[sh.verb_lemma] += 1
                for t in s.toks:
                    if t.upos in ("NOUN", "PROPN", "ADJ") and t.lemma.isalpha():
                        filler_freq[(t.lemma.lower(), "n" if t.upos != "ADJ" else "a")] += 1
                c = check(sh)
                verd[c["verdict"] if c["verb_known"] else "verb-unknown"] += 1

    vi, pi = verbnet_index(), propbank_index()
    lemmas = sorted(set(vi) | set(pi))
    hashes = _context_hashes(lemmas) if with_hashes else {}

    fillers = {}
    if with_hashes:
        try:
            wn = _wordnet(); import context_hash_v2 as _ch
            top = [lp for lp, _ in filler_freq.most_common(2500)]
            for (lem, pos) in top:
                ss = wn.synsets(lem, pos=pos)
                if not ss:
                    continue
                sc = sem_hash.sem_code(ss[0])
                try:
                    gr = _ch.gamma_radial(ss[0]); bd = band_of(abs(gr))
                except Exception:                        # noqa: BLE001
                    gr, bd = 0.0, "surface"
                fillers[lem] = {"pos": pos, "sense": ss[0].name(),
                                "sem_code": sc, "gamma_radial": round(gr, 4),
                                "band": bd, "count": filler_freq[(lem, pos)],
                                "source": "corpus"}

            # the sanitized monad_mathematics.bin pass (Cody, 2026-09-11):
            # "the complete vocabulary needs to be in monad3_c.bin, and upon
            # granularity, the mathematics.bin adds weight to the already
            # present vocabulary... it should become the primary 'lexicon'
            # in the case of granularity." These get the SAME sem_code/
            # gamma_radial/band treatment as the corpus fillers above, so
            # they are real, selectable candidates — not a side presence
            # check — tagged source="maths" so generate.py's _resonant_pick
            # can prefer them as the PRIMARY pool once a topic gates in
            # (sem_hash.is_maths_eligible), falling back to the full pool
            # only when the primary lexicon has nothing that fits.
            from . import maths_sanitize
            for lem, pos in maths_sanitize.sanitize().items():
                if lem in fillers:                        # corpus already won
                    continue
                ss = wn.synsets(lem, pos=pos)
                if not ss:
                    continue
                sc = sem_hash.sem_code(ss[0])
                try:
                    gr = _ch.gamma_radial(ss[0]); bd = band_of(abs(gr))
                except Exception:                          # noqa: BLE001
                    gr, bd = 0.0, "surface"
                fillers[lem] = {"pos": pos, "sense": ss[0].name(),
                                "sem_code": sc, "gamma_radial": round(gr, 4),
                                "band": bd, "count": 1, "source": "maths"}
        except Exception as e:                            # noqa: BLE001
            print(f"  fillers pass skipped ({e!r})")

    verbs = {}
    for lem in lemmas:
        fr = frame_of(lem)
        verbs[lem] = {
            "sails": fr["licensed_patterns"],
            "maps": slot_maps(lem),
            "selrestrs": selrestrs(lem),
            "context_hash": hashes.get(lem),
            "corpus_count": verbs_seen.get(lem, 0),
        }

    role_codes, selrestr_anchors = {}, {}
    if with_hashes:
        try:
            for tr in sem_hash.ROLE_ANCHORS:
                role_codes[tr] = sem_hash.role_code(tr)
            for typ in sem_hash.SELRESTR_ANCHORS:
                ac = sem_hash.anchor_code(typ)
                if ac:
                    selrestr_anchors[typ] = ac
        except Exception:                                # noqa: BLE001
            pass

    sails = {}
    for p in PATTERNS:
        sails[p] = {
            "slots": [{"role": ss.role, "deprel": ss.deprel,
                       "themrole": ss.themrole, "head": ss.head} for ss in SAILS[p]],
            "order": [ss.role for ss in SAILS[p]],
            "rhythm_affinity": RHYTHM_AFFINITY[p],
            "frequency": sail_freq[p],
            "example": sail_ex.get(p, ""),
        }

    index = {
        "meta": {
            "schema": 2, "sentences": n, "verbs": len(verbs),
            "verbs_with_hash": len(hashes), "fillers": len(fillers),
            "vn_lemmas": len(vi), "pb_lemmas": len(pi),
            "verdicts": dict(verd),
        },
        "sails": sails,
        "fillers": fillers,
        "role_codes": role_codes,
        "selrestr_anchors": selrestr_anchors,
        "ancestor_primes": sem_hash.dump_prime_table() if with_hashes else {},
        "speech_acts": SPEECH_ACTS,
        "register_bands": [list(b) for b in REGISTER_BANDS],
        "np_grammar": NP_GRAMMAR,
        "copular": COPULAR,
        "verbs": verbs,
    }
    with open(OUT, "w") as f:
        json.dump(index, f, indent=1, default=list)
    print(f"wrote {os.path.relpath(OUT)}  schema 2")
    print(f"  {n} sentences · {len(verbs)} verbs · {len(hashes)} verb hashes · {len(fillers)} fillers")
    print(f"  sail freq: {dict(sail_freq.most_common())}")
    print(f"  verdicts:  {dict(verd)}")
    for lem in ("give", "put", "be", "run", "converge"):
        v = verbs.get(lem, {})
        print(f"  {lem:10} sails={v.get('sails')}  hash_band="
              f"{(v.get('context_hash') or {}).get('band')}")
    return index


if __name__ == "__main__":
    run(with_hashes="--nohash" not in sys.argv)
