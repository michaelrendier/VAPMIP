# monad_observe.py — the conversation-ingest hook

A copy, kept for provenance and documentation. **The live, running copy is
`~/.claude/hooks/monad_observe.py`, wired in `~/.claude/settings.json`** —
editing this repo copy does not change Claude Code's actual behavior. This
copy exists so the mechanism has a home in version control and next to the
`harness.py` machinery it depends on, instead of living only as an untracked
dotfile outside every repo.

## What it does

Every Claude Code turn produces two events this hook is wired to:

```
UserPromptSubmit -> monad_observe.py external   (the human's prompt)
Stop              -> monad_observe.py internal   (Claude's last text reply)
```

For `internal`, it reads the session transcript and keeps only the last
assistant turn's **text blocks** — thinking blocks, tool calls, and tool
results are dropped before anything is sent; the words for any maths are
expected to come from the calculator's own narration, not raw glyphs or
code output.

The text is prose-sanitised by `harness.strip_to_prose` (fenced code,
tables, box-drawing, links, and notation-dense lines removed), split into
sentences (`harness._sentences`), and written non-blocking to the Monad's
ingest FIFO — falling back to a local append-only spool file if the daemon
or its drive is unavailable. **It never blocks the prompt and never fails
the turn**: every failure path is caught and it always exits 0.

## The weight policy — `INGEST_POLICY` in `harness.py`

```python
INGEST_POLICY = {
    'external': {'w_sem': 1.5, 'w_ctx': 1.5, 'echo': 0},   # the human
    'internal': {'w_sem': 0.9, 'w_ctx': 0.6, 'echo': 1},   # Claude's own prose
}
```

The human's prompt is ingested at full, uncapped weight (`1.5`, echo 0 — it
is never an echo of anything). Claude's own reply is ingested at a lower,
asymmetric weight (`w_sem=0.9`, `w_ctx=0.6`) and flagged `echo=1` — it is
the coupled system's own language faculty responding to what it was just
given, not an independent external signal, and is weighted down accordingly
so the Monad's language field is shaped more by what it's told than by
what it just said back.

A prompt and the response it draws are linked by a random pair id, stashed
per-session in `~/.ptolemy/.pair-<session>` — minted on `external`, read
and consumed on `internal` — so the daemon can log the
prompt-bytes → response-bytes sample for a response-scaling engine.

## The rest of the pipeline (not this file, for context)

```
hook (this file)
  -> OBSERVE_FIFO / OBSERVE_SPOOL   (~/.ptolemy/, harness.py)
  -> ptolemy-monad.service          (systemd --user, socket-activated,
                                      resident field, niced + idle-IO)
  -> repack.py                      (../repack.py, folds drift into
                                      monad3_c.bin in place at the repack
                                      knee — MAP_SHARED + msync, no rebuild)
  -> PtolC/monad3_c.bin             (the packed store ptol.c actually reads)
```

See `../README.md` and `../SPEC.md` for the daemon/repack side; see
`../service/` for the systemd unit files.

## Dependency

Imports `harness.py` from `MONAD_HARNESS_DIR` (env override; defaults to
`~/Projects/ThePlace/VAPMIP`, i.e. this repo) — `strip_to_prose`,
`_sentences`, `OBSERVE_FIFO`, `OBSERVE_SPOOL`, `INGEST_POLICY`. If the
import fails for any reason, the hook silently no-ops.
