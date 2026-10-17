#!/usr/bin/env python3
"""verify_nlp_environment.py — does THIS interpreter have the content-extraction stack, and does each piece LOAD?

Run it with every interpreter that matters:
    python3 tools/verify_nlp_environment.py                         # system python
    VAPMIP/.venv/bin/python tools/verify_nlp_environment.py         # VAPMIP's own venv
    ValaQuenta/.venv/bin/python tools/verify_nlp_environment.py     # ValaQuenta (gets every repository's tools)
Each line is PASS (it loaded and answered), MISS (not installed or data absent) or FAIL (present but raised).
Exit code 0 only when nothing FAILed; MISS is reported, not hidden.  See docs/NLP_ENVIRONMENT.md.
"""
import importlib
import sys
import warnings

warnings.filterwarnings("ignore")
rows = []


def check(name, fn):
    try:
        out = fn()
        rows.append(("PASS", name, str(out)[:70]))
    except (ImportError, LookupError, OSError) as e:
        rows.append(("MISS", name, type(e).__name__ + ": " + str(e).split("\n")[0][:60]))
    except Exception as e:                                  # noqa: BLE001
        rows.append(("FAIL", name, type(e).__name__ + ": " + str(e).split("\n")[0][:60]))


def imp(mod):
    return lambda: getattr(importlib.import_module(mod), "__version__", "ok")


for m in ("numpy", "scipy", "pandas", "sklearn", "networkx", "nltk", "spacy", "lemminflect", "inflect", "conllu", "wn", "rapidfuzz"):
    check("import " + m, imp(m))
for m in ("stanza", "gensim", "textblob", "pywsd"):             # system-python extras (not in the repo venvs)
    check("import " + m + " (optional)", imp(m))


def nltk_calls():
    import nltk
    from nltk.corpus import wordnet as wn, verbnet as vn
    return {
        "nltk wordnet 3.0 synsets('play')": lambda: len(wn.synsets("play")),
        "nltk verbnet classids('play')": lambda: vn.classids("play")[:3],
        "nltk wordnet_ic (information content)": lambda: __import__("nltk.corpus", fromlist=["wordnet_ic"]).wordnet_ic.ic("ic-brown.dat") and "ic-brown.dat",
        "nltk propbank roleset": lambda: __import__("nltk.corpus", fromlist=["propbank"]).propbank.roleset("play.01").attrib["name"],
        "nltk framenet frames": lambda: len(__import__("nltk.corpus", fromlist=["framenet"]).framenet.frames()),
        "nltk semcor sentences": lambda: len(__import__("nltk.corpus", fromlist=["semcor"]).semcor.sents()[:5]),
        "nltk sentiwordnet": lambda: str(__import__("nltk.corpus", fromlist=["sentiwordnet"]).sentiwordnet.senti_synset("happy.a.01"))[:40],
        "nltk cmudict": lambda: __import__("nltk.corpus", fromlist=["cmudict"]).cmudict.dict()["piano"][0],
        "nltk punkt_tab sent_tokenize": lambda: len(nltk.sent_tokenize("It is yellow. Is it? Yes.")),
        "nltk POS tagger": lambda: nltk.pos_tag(nltk.word_tokenize("can you play the piano"))[2],
        "nltk NE chunker": lambda: str(nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize("Hawkeye went to Fort William Henry")))).replace("\n", " ")[:50],
        "nltk conll2000 chunk corpus": lambda: len(__import__("nltk.corpus", fromlist=["conll2000"]).conll2000.chunked_sents()[:3]),
        "nltk nps_chat dialogue acts": lambda: __import__("nltk.corpus", fromlist=["nps_chat"]).nps_chat.xml_posts()[0].attrib["class"],
        "nltk treebank": lambda: len(__import__("nltk.corpus", fromlist=["treebank"]).treebank.tagged_sents()[:3]),
        "nltk universal_tagset map": lambda: nltk.map_tag("en-ptb", "universal", "NNS"),
        "nltk lemmatizer (wordnet)": lambda: nltk.stem.WordNetLemmatizer().lemmatize("played", "v"),
        "nltk stopwords": lambda: len(__import__("nltk.corpus", fromlist=["stopwords"]).stopwords.words("english")),
        "nltk brown / gutenberg": lambda: len(__import__("nltk.corpus", fromlist=["brown"]).brown.words()[:10]),
    }


try:
    for k, f in nltk_calls().items():
        check(k, f)
except Exception as e:                                       # noqa: BLE001
    rows.append(("MISS", "nltk data", type(e).__name__))


def spacy_model(name):
    def f():
        import spacy
        d = spacy.load(name)("The sun is yellow.")
        return [(t.text, t.dep_) for t in d][:4]
    return f


for mdl in ("en_core_web_sm", "en_core_web_md", "en_core_web_lg"):
    check("spacy model " + mdl, spacy_model(mdl))
check("lemminflect conjugate play (VBD, VBG)", lambda: (__import__("lemminflect").getInflection("play", "VBD")[0], __import__("lemminflect").getInflection("play", "VBG")[0]))
check("inflect plural of 'tree'", lambda: __import__("inflect").engine().plural("tree"))


def wn_modern():
    import wn
    return [(lx.id, lx.version) for lx in wn.lexicons()]


check("wn (modern API) lexicons", wn_modern)
check("wn oewn:2025 synsets('tree')", lambda: len(__import__("wn").Wordnet("oewn:2025").synsets("tree")))

width = max(len(r[1]) for r in rows)
for status, name, note in rows:
    print(f"{status:4s} {name:<{width}s}  {note}")
n = {s: sum(r[0] == s for r in rows) for s in ("PASS", "MISS", "FAIL")}
print(f"\n{sys.executable}\n{n['PASS']} PASS, {n['MISS']} MISS, {n['FAIL']} FAIL")
sys.exit(1 if n["FAIL"] else 0)
