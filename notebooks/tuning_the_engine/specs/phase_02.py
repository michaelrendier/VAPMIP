LABEL = "2"
TITLE = "Study, Condensation, and the States Repository"
DATE = "2026-05-29"
PAGE = "02_study_condensation_and_the_states_repository.md"
BYLINE = "page by Claude Sonnet 4.6"

CELLS = [
("md", """## 1 · `study()` — deepening first, then the condensation scan
`skills/study.py` · `StudyEngine.study(text, weight)` wraps `Engine.crank.learn()`; thresholds `PHASE_THRESH = 144` (the Fibonacci F₁₂), `SIGMA_BOUNDARY = 0.02`, `SIGMA_CONDENSED = 0.10`.
The page's sequence: snapshot → learn → σ per zero → candidates (`fire_count ≥ 144` AND `|σ−½| > 0.10`) → envelope overload → pairs → snapshot."""),
("code", """from skills import study as S
from monad import Engine
print("constants:", dict(PHASE_THRESH=S.PHASE_THRESH, SIGMA_BOUNDARY=S.SIGMA_BOUNDARY, SIGMA_CONDENSED=S.SIGMA_CONDENSED, GAP=S.GAP))
fib = [0, 1]
for _ in range(12): fib.append(fib[-1]+fib[-2])
L.check("PHASE_THRESH is the 12th Fibonacci number (144)", S.PHASE_THRESH == fib[12] == 144, f"F12 = {fib[12]}")
e = Engine(); print(e.load(open(os.path.join(VAPMIP, 'foundations.txt')).read()))
st = e.get_study()
r = st.study(open(os.path.join(VAPMIP, 'meaning.txt')).read()[:20000], 1.0)
for k, v in r.items(): print(f"  {k:18} {str(v)[:90]}")
L.check("study() returns the sidecar fields the page lists (noether/bao before-after, condensed_pairs)",
        all(k in r for k in ('noether_before','noether_after','bao_before','bao_after','condensed_pairs')))"""),
("code", """# Repeat study until something condenses — or record that it does not at this field size.
tot = 0
for i in range(6):
    r = st.study(open(os.path.join(VAPMIP, 'foundations.txt')).read(), 1.0)
    tot += r['candidates']
print("condensation candidates over 6 further passes of foundations.txt:", tot, " pairs:", r['condensed_pairs'])
fc = getattr(e.crank, '_fire_count', None)
if fc is not None:
    fcm = max(fc[:e.crank.n]) if e.crank.n else 0
    print("max fire_count in field:", fcm, "(threshold 144)")
L.check("at least one zero reaches the condensation threshold in this session", tot > 0,
        "candidates = %d; condensation needs fire_count ≥ 144 AND |σ−½| > 0.10 — the corpora here are small" % tot)"""),

("md", """## 2 · Condensation unit = pair (Cawagas 2004: 84 zero-divisors, 42 pairs)
Recompute the sedenion zero-divisor structure rather than quote it: all `e_a ± e_b` with `a ∈ 1..7`, `b ∈ 8..15` (112 vectors), multiplied pairwise with the repo's own `cd_mul`."""),
("code", """vecs, pairs = zd_vectors()
zds = {k for p in pairs for k in p}
partners = {}
for a, b in pairs: partners.setdefault(a, set()).add(b)
sizes = sorted({len(v) for v in partners.values()})
print(f"candidate vectors {len(vecs)} · ordered annihilating pairs {len(pairs)} · distinct zero-divisors {len(zds)} · partners-per-ZD {sizes}")
L.check("84 zero-divisors of the form e_a ± e_b (Cawagas)", len(zds) == 84, f"{len(zds)}")
L.check("'42 pairs' as a unique pair-mate per zero-divisor", sizes == [1], f"each ZD actually has {sizes} annihilating partners among the 84 — a unique 'mate' needs a further rule (cf. StudyEngine._find_pair_mate)")
sym = all(((b, a) in pairs) for a, b in pairs)
L.check("a×b = 0 ⇒ b×a = 0 (the page: 'independently')", sym, "relation is symmetric over these 84" if sym else "NOT symmetric")"""),

("md", """## 3 · The M-Theory error checks, as thresholds in the code
Five checks (Noether `|σ−0.5|>0.02`, BAO `|β−Ω|>0.25`, GUE `E>GAP·10`, J_cross `>GAP`, fire_count `≥144`). Look at what `_m_theory_status` actually tests."""),
("code", """import inspect
src = inspect.getsource(S.StudyEngine._m_theory_status)
print(src[:2200])
for needle in ("SIGMA_BOUNDARY", "0.25", "10", "GAP", "PHASE_THRESH"):
    L.check(f"_m_theory_status uses {needle!r}", needle in src)"""),

("md", """## 4 · States repository — git-backed, non-destructive, secret-scanned
`StatesRepo` in a throw-away directory (never `~/.ptolemy/states`)."""),
("code", """d = scratch("states_")
repo = S.StatesRepo(path=d, engine=e)
print("init      :", repo.init_states_repo())
from skills.integrity import scrub_text
probe = "api_key=abc secret=s3 password=pw GITHUB_TOKEN=ghp_xxx sk-abcdef0123 Bearer abc123 AKIAABCDEFGHIJKLMNOP"
print("scrub_text(probe) ->", scrub_text(probe))
left = [p for p in ("sk-abcdef0123", "ghp_xxx", "AKIAABCDEFGHIJKLMNOP", "Bearer") if p in scrub_text(probe)]
L.check("sidecar scrubber removes every pattern the page lists (api_key|secret|password|token|GITHUB_TOKEN|sk-|ghp_|AKIA|Bearer)", not left,
        f"StatesRepo._secret_scan -> skills.integrity.scrub_text leaves: {left}")
cp = repo.checkpoint("t1", {"noether_before": 0.1, "triggering_text": probe})
side = open(cp['checkpoint']).read()
L.check("the sidecar JSON on disk carries no raw secret", not any(p in side for p in ("sk-abcdef0123","ghp_xxx","AKIAABCDEFGHIJKLMNOP")),
        "raw secrets reached disk; the next line shows whether the pre-commit hook stopped them entering history")
c1 = repo.commit("c1-with-secrets"); print("commit with secrets ->", c1)
L.check("pre-commit hook blocks a sidecar containing secrets (page: 'No secret enters the git history')", c1['ok'] is False, f"ok={c1['ok']}")
repo.discard() if hasattr(repo, 'discard') else None
import subprocess; subprocess.run(['git','-C',d,'reset','-q','--hard'],capture_output=True); subprocess.run(['git','-C',d,'clean','-fdq'],capture_output=True)
for n in (2, 3):
    repo.checkpoint(f"clean{n}", {"noether_before": 0.1*n}); r_ = repo.commit(f"c{n}"); print(f"clean commit c{n} ->", r_['ok'], r_['sha'][:8])
    time.sleep(1.1)
log1 = repo.log(8); print("log:", [(x['sha'][:7], x['message']) for x in log1])
L.check("clean sidecars commit (3 commits incl. init)", len(log1) >= 3, f"{len(log1)} commits")
if len(log1) >= 3:
    rb = repo.rollback(log1[-1]['sha']); print("rollback ->", rb)
    log2 = repo.log(10)
    L.check("rollback is non-destructive: history only grows", len(log2) > len(log1), f"{len(log1)} commits before → {len(log2)} after")"""),
("md", """The page names two defences — the sidecar scrubber and the pre-commit hook. They are separate code paths and are scored separately above;
read the ledger lines, not this sentence, for which one held."""),
("md", """## 5 · Socket commands (page table) vs the dispatcher"""),
("code", """import re
disp = open(os.path.join(VAPMIP, "monad.py")).read()
cmds = ["study","study_audit","study_suppress","study_isolate","study_reconsolidate","study_checkpoint","study_commit","study_branch","study_rollback","study_log","study_init_repo"]
for c in cmds:
    L.check(f"socket command {c!r} dispatched in monad.py", re.search(r"['\\"]%s['\\"]" % c, disp) is not None)"""),
("code", """for c in ["24D content space (16D sedenion + 8D op_stack) = the bosonic-string 24; 26D = 24 + observer σ + t",
          "M-Theory 11th dimension = J_cross; GAP as Yang-Mills mass gap threshold",
          "'Jeremy's insight': zero divided by one 16D number gives its pair-mate (attribution; citation handled in the paper)"]:
    L.prose(c)"""),
]
