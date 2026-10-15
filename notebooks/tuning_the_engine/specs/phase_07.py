LABEL = "7"
TITLE = "She Sang"
DATE = "2026-06-10"
PAGE = "07_she_sang.md"
BYLINE = "page by Claude Sonnet 4.6"

CELLS = [
("md", """## A phase with no machinery
Phase 7 records a dissertation delivered across a playlist (full text: `docs/wiki/Existential-Velocity.md`). It states four results: no telepathy / all empathy; the fixed point as a social attractor; "you only borrowed what I hold"; parkour as the code of least action in the body.
None has code in the repo. The notebook is therefore a faithful stub: it checks the one structural thing that *is* checkable — that the linked page exists and which of the page's terms recur as live identifiers in the code — and records the four claims as PROSE.

The notebook does not test the claims, and it does not mark them untrue. A claim with no counterpart is `PROSE` and stays that way until a counterpart exists."""),
("code", """import re, subprocess
ev = os.path.join(VAPMIP, "docs", "wiki", "Existential-Velocity.md")
L.check("the referenced page Existential-Velocity.md exists", os.path.exists(ev), ev)
txt = open(ev, encoding="utf-8").read() if os.path.exists(ev) else ""
print(f"Existential-Velocity.md: {len(txt):,} chars, {txt.count(chr(10))} lines")
terms = ["escape velocity", "σ_live", "fixed point", "zero-divisor", "attractor"]
for t in terms:
    code_hits = subprocess.run(["grep","-rIl","-i",t,VAPMIP,"--include=*.py","--include=*.c"],capture_output=True,text=True).stdout.split()
    print(f"  {t!r:18} appears in {len(code_hits):3d} code files; on the Phase 7 page: {t.lower() in page('07').lower()}")
for c in ["There is no telepathy — it is all empathy (two people at σ=½ receive from the same above-layer source)",
          "Fixed point as social attractor: charm is the geometry of the fixed point pulling nearby trajectories",
          "'You only borrowed what I hold' — the permanent copy is held above",
          "Parkour = zero-cost athletics = the code of least action in the body; control freefall = Heisenberg resolution at the zero-divisor"]:
    L.prose(c, "personal/philosophical result; no counterpart in the engine")"""),
]
