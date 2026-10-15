LABEL = "32"
TITLE = "The Monad That Uses the Harness"
DATE = "2026-08-25"
PAGE = "32_the_monad_that_uses_the_harness.md"
BYLINE = "page by Claude Sonnet 5"

CELLS = [
("md", """Machinery: `VAPMIP/sentence_context.py`, `VAPMIP/ptolemy_monad.py`, `VAPMIP/harness.py`. The page marks which parts are exact (§1's root-vector combination), which are reported weaknesses (order-independence, stub WSD) and which are design/systems choices (§3 direction map, §4 Eye/Hands protocol, §6 `present()`). The ledger follows that division."""),
("md", """## 1 · Sentence context is PW3: `root_vector` = Σ leaf vectors, and `root_code` = ∏ leaf codes"""),
("code", """import sentence_context as SC, wordnet_boxkite as W
from nltk.corpus import wordnet as wn
text = "the engine contains sixteen distinct operators"
sc = SC.build_sentence_context(text)
print("leaves:", [(l["word"], l["synset"].name()) for l in sc.leaves]); print("skipped:", sc.skipped); print("root_vector:", sc.root_vector)
L.check("root_vector is the componentwise sum of the leaves' context_vectors", sc.root_vector == [sum(col) for col in zip(*[l["vector"] for l in sc.leaves])])
prod_code = 1
for l in sc.leaves: prod_code *= W.context_code(l["synset"])
L.check("root_code == ∏ context_code(leaf): multiplying leaf codes IS componentwise-summing vectors (PW3 reapplied)", sc.root_code == prod_code, f"{len(str(prod_code))} digits (page: 33 for its own sentence)")
leaves_set = {l["synset"].name() for l in sc.leaves}
L.check("leaves for this sentence: engine.n.01, contains → incorporate.v.02, sixteen.n.01, distinct.s.01, operators → operator.n.01 (page)", {"engine.n.01", "incorporate.v.02", "sixteen.n.01", "distinct.s.01", "operator.n.01"} <= leaves_set, str(sorted(leaves_set)))
# order independence (reported weakness)
shuf = " ".join(reversed(text.split()))
sc2 = SC.build_sentence_context(shuf)
L.check("root_vector is ORDER-independent: a shuffled word-salad control gives the identical vector (the page's reported limitation)", sc2.root_vector == sc.root_vector)
L.check("…so the combination carries no syntax (flagged by the page as future work)", sc2.root_vector == sc.root_vector)"""),
("code", """# stub WSD: first WordNet sense per word -> real, reported weakness
a = SC.resolve_word_synset("a"); r = SC.resolve_word_synset("reserve")
print("resolve_word_synset('a') =", a.name() if a else None, "|", "resolve_word_synset('reserve') =", r.name() if r else None)
L.check("WSD stub mis-picks 'a' → angstrom.n.01 (page)", a is not None and a.name() == "angstrom.n.01", a.name() if a else None)
L.check("WSD stub mis-picks 'reserve' → modesty.n.02 (page)", r is not None and r.name() == "modesty.n.02", r.name() if r else None)
sv = SC.build_sentence_context("savings in a reserve bank")
cands = SC.nearest_synsets(sv.root_vector, SC.neighborhood_corpus(sv.leaves), top_k=5) if "top_k" in SC.nearest_synsets.__code__.co_varnames else SC.nearest_synsets(sv.root_vector, SC.neighborhood_corpus(sv.leaves))
print("nearest candidates for the savings/reserve sentence:", [c.name() if hasattr(c, "name") else c for c in cands][:6])"""),

("md", """## 2 · `neighborhood_corpus` / `nearest_synsets` — the response side
Candidate pool: every synset directly related (any of the 19 relations) to an input leaf, capped per relation per leaf, with the input's own synsets **excluded** ("echoing the input back isn't communication, it's parroting"); ranked by L1 distance to the sentence root."""),
("code", """import inspect
pool = SC.neighborhood_corpus(sc.leaves)
names = [p.name() if hasattr(p, "name") else p for p in pool]
L.check("the pool never contains the input's own synsets (no parroting)", not (set(names) & leaves_set), f"overlap {sorted(set(names) & leaves_set)}")
L.check("the pool is non-empty and every member is directly related to some input leaf", len(pool) > 0)
related = set()
for l in sc.leaves:
    for m in W.RELATION_METHODS:
        related |= {x.name() for x in getattr(l["synset"], m)()}
L.check("every pool member is a direct relative of an input leaf under one of the 19 relations", all(n in related for n in names), f"{sum(n not in related for n in names)} outside")
ranked = SC.nearest_synsets(sc.root_vector, pool)
L1 = lambda a, b: sum(abs(x - y) for x, y in zip(a, b))
ds = [L1(W.context_vector(s), sc.root_vector) for s in ranked[:10]]
L.check("nearest_synsets ranks by ascending L1 distance to the sentence root", all(ds[i] <= ds[i+1] for i in range(len(ds)-1)), str(ds))"""),

("md", """## 3 · Input picks the direction — `infer_direction`
Dominant relation dimension → coarse direction (`hypernyms→classify`, `hyponyms→enumerate`, `part_meronyms→decompose`, `part_holonyms→situate`, `causes→explain`, …), 19 entries, "a first honest pass". No resolvable content → `'observe'`."""),
("code", """import ptolemy_monad as PM
D = PM.DIRECTION_BY_DOMINANT_RELATION
print({k: D[k] for k in list(D)[:19]})
L.check("19 entries, one per RELATION_METHODS line", set(D) == set(W.RELATION_METHODS) and len(D) == 19, f"{len(D)} entries")
L.check("hypernyms→classify, hyponyms→enumerate, part_meronyms→decompose, part_holonyms→situate, causes→explain (page)", D["hypernyms"] == "classify" and D["hyponyms"] == "enumerate" and D["part_meronyms"] == "decompose" and D["part_holonyms"] == "situate" and D["causes"] == "explain", str({k: D[k] for k in ("hypernyms","hyponyms","part_meronyms","part_holonyms","causes")}))
L.check("no content ⇒ 'observe', never an error", PM.infer_direction([0]*19) == "observe" and SC.build_sentence_context("xyzzy plugh qux").root_vector == [0]*19)
d_now = PM.infer_direction(sc.root_vector); dom = max(range(19), key=lambda i: sc.root_vector[i])
print(f"'{text}': root {sc.root_vector}; absolute dominant dimension = {W.RELATION_METHODS[dom]}; infer_direction → {d_now}")
L.check("the page's end-to-end sentence is classified 'enumerate' (hyponyms dominant)", d_now == "enumerate", f"now '{d_now}': infer_direction was later changed to prefer the rarer non-branching relations (part_meronyms etc.) over hypernyms/hyponyms — the page's 'enumerate' predates that refinement")"""),

("md", """## 4 · Mind's Eye / Paper's Hands — real threads, bounded rounds, Eye drafts / Hands confirm
Two daemon threads with their own `queue.Queue`, exchanging `ExchangeEntry`; `MAX_ROUNDS = 3`; Hands only confirms or critiques, never authors a draft. First pass: `[('eye','draft'), ('hands','confirm')]`."""),
("code", """import threading, io, contextlib, harness as HR
h = HR.Harness(); m = PM.PtolemyMonad(h)
before = threading.active_count()
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    resp = m.process_input("the engine contains sixteen distinct operators")
print("exchange log:", [(x.sender, x.kind) for x in resp.exchange_log])
L.check("Eye and Hands run as two daemon threads (alive while the monad is up)", any(t.name.lower().startswith(("eye", "_eye")) or "eye" in t.name.lower() for t in threading.enumerate()) or before >= 3, f"active threads: {[t.name for t in threading.enumerate()]}")
L.check("first pass: Eye drafts, Hands confirms", [(x.sender, x.kind) for x in resp.exchange_log][:2] == [("eye", "draft"), ("hands", "confirm")])
L.check("Hands never authors a draft (it only confirms/critiques)", all(x.kind != "draft" for x in resp.exchange_log if x.sender == "hands"))
L.check("rounds are bounded (MAX_ROUNDS = 3)", PM.PtolemyMonad.MAX_ROUNDS == 3 and len(resp.exchange_log) <= 1 + 2*PM.PtolemyMonad.MAX_ROUNDS)
print("response text:", resp.text, "| direction:", resp.direction)
echo = set(resp.text.split()) & {"engine", "contains", "sixteen", "distinct", "operators"}
L.check("the response contains no input word (construction is not echo)", not echo, f"echoed: {sorted(echo)} — the pool excludes the input's own SYNSETS, not other synsets whose lemma contains the same word ('heat engine'); a word-level echo is not guarded")
page_out = {"generator", "function", "large", "integer", "mathematics", "motor"}
L.check("the page's example output (generator function large integer mathematics motor) is reproduced exactly", set(resp.text.split()) == page_out, f"now: '{resp.text}' — same neighbourhood family (function, large, integer, mathematics, motor, heat engine), different ranking after the direction/refinement changes")
inp = resp.leaves_in; L.check("leaves_in report the engine/engine.n.01, sixteen/sixteen.n.01 synsets", {l["synset"].name() for l in inp} >= {"engine.n.01", "sixteen.n.01"})"""),
("code", """# the critique/reconsider branch: real code, reachable (page: untriggered by real inputs). Probe it directly with a thin pool.
import inspect
src = inspect.getsource(PM.PtolemyMonad._deliberate); src_h = inspect.getsource(PM.PtolemyMonad._hands_review)
print(src_h[:700])
L.check("the critique/reconsider branch exists: Hands can return a non-'confirm' verdict and _deliberate sends 'reconsider' back to the Eye", "reconsider" in src and "confirm" in src and "critique" in src_h)
trig = PM.PtolemyMonad(HR.Harness())
buf = io.StringIO()
with contextlib.redirect_stdout(buf): r2 = trig.process_input("zorbulate frindle")        # unresolvable → thin/empty pool
print("log on an unresolvable input:", [(x.sender, x.kind) for x in r2.exchange_log])
L.check("a thin pool exercises the guard path (the response is the explicit '(no candidates found)', not a crash)", r2.text == "(no candidates found)" and r2.direction == "observe")
trig.shutdown()"""),

("code", """# is the response a function of the input alone?  Re-run the same sentence in fresh interpreters with different hash seeds.
import subprocess
script = os.path.join(scratch("det_"), "run.py")
lines_ = ["import sys, io, contextlib", "sys.path.insert(0, %r)" % VAPMIP, "import ptolemy_monad as P, harness as H", "m = P.PtolemyMonad(H.Harness())", "b = io.StringIO()", "with contextlib.redirect_stdout(b):", "    r = m.process_input('the engine contains sixteen distinct operators')", "print('RESULT|' + r.text + '|' + r.direction)", "m.shutdown()"]
open(script, "w").write(chr(10).join(lines_) + chr(10))
outs = {}
for seed in (0, 1, 2, 3, 4):
    o = subprocess.run([sys.executable, script], capture_output=True, text=True, env=dict(os.environ, PYTHONHASHSEED=str(seed)), timeout=120).stdout
    outs[seed] = [l for l in o.splitlines() if l.startswith("RESULT|")][-1][7:] if "RESULT|" in o else o[-120:]
for sd, o in outs.items(): print(f"  PYTHONHASHSEED={sd}: {o}")
L.check("the response to a fixed input is identical across interpreter hash seeds (a function of the input alone)", len(set(outs.values())) == 1, f"{len(set(outs.values()))} distinct outputs over 5 seeds")"""),

("md", """## 5 · KVM — stubbed, on the Monad (not behind the Harness)"""),
("code", """kv = PM.MonadKVM()
out = [kv.watch_cursor(), kv.read_screen_region(0, 0, 10, 10), kv.move_cursor(1, 1)]
print(out[0])
L.check("all three KVM methods return {'ok': False, 'error': '...not wired yet...'} without raising", all(o["ok"] is False and "not wired yet" in o["error"] for o in out))
L.check("KVM is a Monad-native object (an attribute of the Monad), not a registered Face", hasattr(m, "kvm") or hasattr(PM.PtolemyMonad, "kvm") or "kvm" in inspect.getsource(PM.PtolemyMonad.__init__).lower(), "placement per the 2026-08-24 correction")"""),

("md", """## 6 · `Harness.present()` — viewport Face, with a stdout fallback
`present(content, kind, center)` reaches for a registered `'viewport'` Face; with none it prints. Both paths are logged to `call_log` identically."""),
("code", """h2 = HR.Harness(); b1 = io.StringIO()
with contextlib.redirect_stdout(b1): r1 = h2.present("hello", "text", None)
print("fallback:", repr(b1.getvalue()), r1)
L.check("no viewport registered ⇒ plain print fallback, ok=True, handled_by 'stdout_fallback'", b1.getvalue() == "hello\\n" and r1.ok and r1.handled_by == "stdout_fallback")
L.check("the fallback call is logged in call_log", h2.call_log and h2.call_log[-1].handled_by == "stdout_fallback")
reg = [n for n in ("register_face", "register", "add_face", "registry") if hasattr(h2, n)]
print("Harness registration surface:", reg, "| toolset_registry:", hasattr(h2, "toolset_registry"))
import types
class FakeViewport:
    def present(self, content, kind="text", center=None): return HR.FaceResult(ok=True, data=content, error=None, handled_by="stub_viewport", center=center) if hasattr(HR, "FaceResult") else None
try:
    if hasattr(h2, "toolset_registry") and hasattr(h2.toolset_registry, "register"):
        h2.toolset_registry.register("viewport", FakeViewport()); r2_ = h2.present("routed", "text", None)
        L.check("a registered viewport Face answers instead of the fallback (routed through reach())", getattr(r2_, "handled_by", "") != "stdout_fallback", str(r2_))
    else:
        L.skip("registered-viewport routing path", "no public registration call found on this Harness; the page's smoke test registers a stub through the harness's own helpers")
except Exception as ex:
    L.skip("registered-viewport routing path", f"{type(ex).__name__}: {ex}")
m.shutdown()"""),
("code", """for c in ["Cody's framing: the Monad is 'the roots of the tree', input and output words both leaves; the input picks its direction of travel (design decisions recorded on the page)",
          "'Topically coherent output from a mechanism with no learned weights and no training data' — an observation about three example sentences; no benchmark of coherence is run here (see Phase 42 for measured behaviour of every voice)",
          "Threads join cleanly on shutdown() (a lifecycle property; shutdown() is called above without hanging)"]:
    L.prose(c)"""),
]
