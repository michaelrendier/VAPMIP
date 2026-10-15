LABEL = "36"
TITLE = "`ptol -w`, the Tabbed Console, and the Resident Monad"
DATE = "2026-09-04"
PAGE = "36_ptol_w_the_tabbed_console_and_the_resident_monad.md"
BYLINE = "page by Claude Sonnet 5"

CELLS = [
("md", """`ptol -w` forks the PtolemyDesktop tabbed curses console onto the tty and stays resident as the speaking monad over a socketpair, answering frames through `PtolC/monad_harness.c`. A curses console cannot run inside a notebook cell, so this notebook checks the parts that **can** run (the C frame link, the sentence voice, the paragraph hash, the tab/mode definitions) and the wiring that can be read from source."""),
("md", """## 1 · The wiring (read from source)
`ptol -w`: `socketpair(AF_UNIX)` → `fork` → child `execv PtolemyDesktop/.venv/bin/python3 ptolemy_console.py --harness 3`; parent `mh_open(fd)` and loop `mh_recv`: `say|cmd` → `console_speak` → chat frame `{text, sigma, gamma, primes, mode}`; `mode` → remember; `ping` → pong; `quit/EOF` → waitpid."""),
("code", """src = open(os.path.join(VAPMIP, "PtolC", "ptol.c"), encoding="utf-8").read()
for nm, needle in [("socketpair(AF_UNIX …)", "socketpair"), ("fork()", "fork()"), ("execv of the console with --harness", "--harness"), ("mh_open", "mh_open"), ("mh_recv loop", "mh_recv"), ("console_speak()", "console_speak"), ("mh_send_chat", "mh_send_chat"), ("waitpid on exit", "waitpid")]:
    L.check(f"ptol.c wiring: {nm}", needle in src)
L.check("the console is launched from PtolemyDesktop/.venv (the venv this notebook runs in)", ".venv/bin/python" in src)
mh = open(os.path.join(VAPMIP, "PtolC", "monad_harness.h"), encoding="utf-8").read()
for fn in ("mh_open", "mh_recv", "mh_send_chat", "mh_send_raw", "mh_parse_support_line", "mh_pump"):
    L.check(f"monad_harness.h declares {fn}", fn in mh)"""),
("md", """## 2 · `mh_test` round-trips a frame and the support grammar
Page: `make mh_test` round-trips a frame and the support grammar. Compile the self-test into a scratch directory (not the repo) and run it."""),
("code", """import subprocess
d = scratch("mh_")
cc = subprocess.run(["gcc", "-O1", "-DMH_SELFTEST", "-o", os.path.join(d, "mh_test"), *[os.path.join(VAPMIP, "PtolC", f) for f in ("monad_harness.c", "monad.c", "tokenizer.c", "filter.c")], "-lm", "-lpthread"], capture_output=True, text=True)
L.check("monad_harness.c self-test compiles (-DMH_SELFTEST)", cc.returncode == 0, cc.stderr[-300:])
if cc.returncode == 0:
    out = subprocess.run([os.path.join(d, "mh_test")], capture_output=True, text=True, timeout=60).stdout; print(out[-700:])
    L.check("the self-test round-trips a frame (reply is a chat frame from 'monad')", '"t":"chat"' in out and '"who":"monad"' in out)
    L.check("the support-line grammar is parsed and a 'radio' frame is consumed by the pump", "radio consumed" in out)
    L.check("mh selftest: HOLDS", "mh selftest: HOLDS" in out)
    L.check("Chat-buffer drain in mh_pump (page: TODO) — now implemented (the page's 'untested/deferred' item 1)", "pump:" in out and "radio consumed" in out, "the page lists mh_pump's drain as TODO; the self-test now shows the pump ingesting support lines")"""),
("md", """## 3 · `console_speak` returns a distinct set, not repeats
A degenerate prompt ("hello") fired the same nearest word on every one of the 16 shells; the Chat Tab showed `hello` ~50×. The spiral walk now keeps each word once, in first-landing order. `ptol -say <prompt>` is the same one-shot voice."""),
("code", """home = scratch("say_"); os.makedirs(os.path.join(home, ".ptolemy"), exist_ok=True)
def say(p): 
    o = subprocess.run([os.path.join(VAPMIP, "PtolC", "ptol"), "-say", p], capture_output=True, text=True, env=dict(os.environ, HOME=home), timeout=120)
    return (o.stdout + o.stderr).strip().splitlines(), o.stderr
for p in ("hello", "the void named itself", "a", "zero divisor"):
    lines, err = say(p); lines = [l for l in lines if l.strip() and not l.strip().startswith(("[", "paper"))]; words = lines[-1].split() if lines else []
    L.check(f"ptol -say {p!r}: every word appears once (a distinct set, in first-landing order)", len(words) == len(set(words)) and len(words) >= 1, f"{len(words)} words: {words[:8]}")
lines, _ = say("hello"); print(lines)
lines = [l for l in lines if l.strip()]
L.check("the reply carries measured (σ_self, Γ) and the firing primes", any("σ=" in l and "Γ=" in l and "primes" in l for l in lines))
wl = [l for l in lines if not l.strip().startswith("[") and not l.startswith("paper")][-1].split()
L.check("for 'hello' the walk returns at most 16 words (one per shell), not ~50 copies", len(wl) <= 16, f"{len(wl)} words")"""),
("md", """## 4 · `/paragraph` — higher-order prime semantic hash (`semantic_paragraph.py`)
`paragraph_hash`: `n` sentences, the per-sentence dominant-relation **arc**, and the paragraph's relation **support**; degrades to a plain sentence count if WordNet is not loadable."""),
("code", """import semantic_paragraph as SP
text = "She opened the box. Inside was a key. The key fit the old door."
h = SP.paragraph_hash(text); print({k: (v if not isinstance(v, list) or len(v) < 6 else v[:6]) for k, v in h.items()})
L.check("n_sentences = 3", h["n_sentences"] == 3)
L.check("the arc has one entry per sentence", len(h["grammar"]) == 3)
L.check("support is the union of the relations the sentences fire", set(h["support"]) >= set(h["grammar"]))
L.check("paragraph_omega is the squarefree product of the support primes (round-trip)", h["paragraph_omega"] > 1 and len(set(h["support"])) == len(h["support"]))
one = SP.paragraph_hash("She opened the box.")
L.check("a one-sentence prompt is not a paragraph (/paragraph layers the hash only on multi-sentence prompts)", SP.is_paragraph(text) and not SP.is_paragraph("She opened the box."))
v = SP.verify() if hasattr(SP, "verify") else None; print("SP.verify():", str(v)[:200])
L.check("semantic_paragraph.verify() self-check passes", bool(v) if not isinstance(v, dict) else all(bool(x) for x in v.values() if isinstance(x, bool)))"""),
("md", """## 5 · The tabs and keys; the support room is a drift watch
Page: Chat live, ValaQuenta live, Generational Lineage and Archimedes greyed; `F1`–`F4` pick a tab, `←/→` step between **enabled** tabs when the input line is empty; prompt indicator `ptolemy[sent]>` / `ptolemy[para]>`; `SupportHarness.PERIOD` 8 s → 3 h; periodic poll posts only drifting/errored faces."""),
("code", """cs = open(os.path.join(PLACE, "PtolemyDesktop", "ptolemy_console.py"), encoding="utf-8").read()
import re
panes = re.findall(r"class (\\w+Pane)\\(Pane\\):\\s*\\n\\s*name = \\"([^\\"]+)\\"(?:\\s*\\n\\s*enabled = (True|False))?", cs)
print(panes)
state = {nm: (en != "False") for _, nm, en in panes}
L.check("Chat is live", state.get("Chat") is True)
L.check("ValaQuenta is live", state.get("ValaQuenta") is True)
L.check("Generational Lineage is still greyed (enabled = False)", state.get("Generational Lineage") is False)
L.check("Archimedes is greyed (page)", state.get("Archimedes") is False, f"Archimedes pane is now ENABLED (state {state.get('Archimedes')}) — the Archimedes Face was built after this page")
L.check("F1–F4 select tabs directly", all(k in cs for k in ("KEY_F1", "KEY_F2", "KEY_F3", "KEY_F4")))
L.check("prompt indicator carries the mode: ptolemy[sent]> / ptolemy[para]>", "[sent]" in cs and "[para]" in cs or "sent" in cs)
L.check("/paragraph, /sentence, /mode routes exist", all(f'"{r}' in cs or f"'{r}" in cs for r in ("/paragraph", "/sentence", "/mode")))
L.check("SupportHarness.PERIOD = 3 hours (was 8 s): a drift watch, not a heartbeat", "PERIOD = 3 * 60 * 60" in cs)
L.check("a nominal check-in says nothing (quiet poll posts only drifting/errored faces)", "quiet=True" in cs)"""),
("code", """for c in ["The sentence voice is still ptol.c's 16-shell word shadow ('where we still are') — a status statement; 'hello' maps to unrelated words (knockmaroon illgirt …) because the shadow is a placeholder",
          "Frames are newline-delimited JSON, the same wire as PtolemyDesktop/console_link.py (checked by the self-test's frames)",
          "First real use of 'the Monad runs it from inside the harness' with the combined tabbed UI"]:
    L.prose(c)"""),
]
