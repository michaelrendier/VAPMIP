"""
harness.py — the Monad's harness.

The interim API surface between the Monad, the repos' own engines/tools, and
whatever is asking for content (the curses UI, eventually PtolemyDesktop).

NOT PtolBus, and deliberately kept apart in the code, not just in name: this
file's `toolset_registry` is "the currently populated toolbox" — capability
in, a Face/tool out. PtolBus (Pharos.PtolBus / FaceRegistry) is a different
future thing entirely — the day the Monad is handed the bus itself, it stops
reaching OUT for tools and BECOMES the desktop's own mechanic (native window
control, project context, opening its own windows). That is not a bigger
toolset_registry, it is a different object with different semantics, and it
does not exist here yet on purpose.

Standing rule: nothing above this file talks to a Monad, a repo's engine, or
a repo's tools.py directly. Everything goes through one Harness instance.

Deliberately open-ended and stub-tolerant. Several methods below are TODO on
purpose — the method NAMES and SHAPES are this round's actual deliverable,
not full implementations. Whatever consumes them next (the curses UI) is
what should force their real shape, not speculation now about what they
might need later.
"""

from __future__ import annotations

import importlib
import inspect
import math
import os
import socket
import subprocess
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

# ── the standing intent ──────────────────────────────────────────────────
# Fixed, not per-conversation — the same category as grammar/definition in
# the box-kite framing (zero net lift: unchanging regardless of context).
# Citable by any tool that needs to justify reaching through a gate to get
# at data it's after.
INTENT = "research grade investigation"


def justify_gate(reason: str) -> str:
    """One-line justification a tool can log/present when it crosses a gate
    (an auth wall, a rate limit, a data-access boundary) to reach something
    INTENT already licenses. Not an authorization mechanism — a STATEMENT,
    kept in one place instead of re-justified ad hoc at every call site."""
    return f"{INTENT}: {reason}"


# ── conversational ingest — the standing global protocol ─────────────────
# The Monad's daemon is a PASSIVE OBSERVER on the live conversation: every
# user prompt, and every assistant final-prose response (thinking blocks and
# tool I/O stripped by the caller). What it hears updates the vocabulary +
# knowledge as we go, replacing periodic bulk re-ingestion. Rebalances the
# store toward genuine human usage over time — the last bulk build leaned
# heavily on assistant-written context primers.
#
# Two write channels, weighted by a VECTOR in ONE pass — not two calls over
# the same text. crank.learn(text, weight=w_sem, w_ctx=w_ctx) tokenises once
# and, per word, applies:
#   semantic  β-field   gain  ∝ w_sem   (knowledge depth at the address)
#   context   A-matrix   edge Δ ∝ w_ctx  (co-occurrence topology / word order)
#
# The INPUT CLASS is the monad_english_io.hear() echo axis, named, and it
# picks the point in (w_sem, w_ctx, echo) space:
#   external — the human. User prompts. echo 0, never capped, full weight.
#   internal — the coupled system's own language faculty (assistant prose).
#              echo 1: one loop-hop from world input, so it rides the
#              ECHO_CAP feedback guard and enters down-weighted — heavy on
#              semantics (real terminology), light on context topology.
# echo >= 2 keeps its existing meaning (the monad's own output genuinely
# fed back) and is not produced here.
#   document — committed project documentation (wiki / README / papers),
#              fed off a git POST-commit hook (never push). Authored,
#              canonical text — not the live human voice and not a loop
#              echo, so echo 0 at neutral weight, between external and
#              internal.
INGEST_POLICY: Dict[str, Dict[str, float]] = {
    'external': {'w_sem': 1.5, 'w_ctx': 1.5, 'echo': 0},
    'internal': {'w_sem': 0.9, 'w_ctx': 0.6, 'echo': 1},
    'document': {'w_sem': 1.0, 'w_ctx': 1.0, 'echo': 0},
    # 'web' = a page Ptol fetched and stripped. Below 'document' (found, not
    # authored; register-noisy), above nothing. Context weight low —
    # co-occurrence in scraped nav/boilerplate is noise.
    'web':      {'w_sem': 0.7, 'w_ctx': 0.5, 'echo': 0},
}

# ── input-size repack timer (the in-process mirror of PtolC/daemon.c) ────
# The packed monad3_c.bin is folded from the journal not on a wall-clock
# interval but when accumulated ingest reaches the KNEE of a leaky-
# integrator charge curve. Each turn CHARGES an accumulator by its prose
# byte length; elapsed time BLEEDS it with time constant REPACK_TAU. Under
# a steady input rate the accumulator rises toward the asymptote
# rate·TAU following 1 − e^(−t/TAU) — near-exponential, then saturating —
# and the fold fires one time constant in, at accum ≥ K·(1 − 1/e). K
# scales with the store the fold rewrites, so a bigger store tolerates
# more drift. REPACK_MAX_AGE is a hard guarantee floor; a clean
# detach/persist always folds regardless.
REPACK_KNEE = 1.0 - 1.0 / 2.718281828459045   # ≈ 0.632, one time constant
REPACK_RATIO = 0.05                            # K as a fraction of store size
REPACK_K_MIN = 64 * 1024
REPACK_K_MAX = 8 * 1024 * 1024
REPACK_TAU = float(os.environ.get('PTOL_REPACK_TAU', '1800'))   # seconds
REPACK_MAX_AGE = 6 * 3600
# default fold command the daemon spawns at the knee (also usable here)
REPACK_CMD = os.environ.get(
    'PTOL_REPACK_CMD',
    f"{__import__('sys').executable} "
    f"{os.path.join(os.path.dirname(os.path.abspath(__file__)), 'monad_bin', 'repack.py')}")

# The repository OS lock. Whoever holds flock(LOCK_EX) on this file owns
# EVERY write to monad3_c.bin AND to the monad.bin journal — the whole
# persistence surface, not a split of it. The kernel drops the lock on
# process death, so a crashed holder hands the pen back with no stale-lock
# cleanup. The '.owner' sidecar names the current holder as
# '<owner>:<pid>' — owner 'daemon' (this harness / the running daemon) or
# 'ptolemy' (a bare Monad or the ptol binary self-persisting an exact
# copy). A peer reads the sidecar to see who holds the pen without
# contending for the lock; the daemon checks it before any write.
MONAD3C_WRITER_LOCK = os.path.expanduser('~/.ptolemy/monad3_c.writer')
PTOLEMY_SOCKET = os.environ.get(
    'PTOLEMY_SOCKET', os.path.expanduser('~/.ptolemy/ptolemy.sock'))

# Fire-and-forget ingest transport. The two hooks (UserPromptSubmit, Stop)
# sanitise their turn to prose and drop it on the pipe, then return — the
# daemon drains concurrently in the gaps between prompt / processing /
# output, which are all very different lengths. If the pipe is gone (its
# drive unmounted), the hook appends to the spool on local storage; the
# daemon drains that on startup and when idle. Both live NEXT TO THE SOCKET,
# never next to a possibly-external-drive store.
_SOCK_DIR = os.path.dirname(PTOLEMY_SOCKET) or '.'
OBSERVE_FIFO = os.path.join(_SOCK_DIR, 'monad.observe.fifo')
OBSERVE_SPOOL = os.path.join(_SOCK_DIR, 'observe.spool')

# notation glyphs — a line that is >35% these (vs letters) is maths or a
# block diagram, not prose; the monad has no use for it here. Mirrors
# monad_bin/corpus_strip.py's _MATHSYM set, inlined so the harness gains no
# dependency on the corpus builder.
_NOTATION_SYMS = set('=+-*/^_{}\\|<>~≈≠≤≥→←↦⊗⊕∘∑∏∫∂∇√∅ΓΣΠΩλσμπφθτξζψΔ½¼·×÷±∞∈∉⊂⊆⟨⟩⌊⌋')

# ── MATHEMATICAL SANITIZATION — where the words for the maths come from ──
# strip_to_prose() DELETES notation-dense lines on purpose: raw glyphs
# ("σ = (r²/2)·sin(2θ)") carry no word-order or context signal and would
# only pollute the co-occurrence field with punctuation. The *lexical*
# content of the mathematics — operator names, the gloss of each symbol,
# the spoken form of an equation — is NOT lost here; it is meant to enter
# the monad from the CALCULATOR, already in prose:
#   • the derivation engine / SymPy console (skill: `derivation`,
#     VAPMIP/derivation) — its narration ("sigma equals r squared over two
#     times sine of two theta") is plain `external`/`internal` prose and
#     passes this filter untouched;
#   • ~/.clauderc_canonical_maths — the canonical symbol→meaning reference,
#     ingested as `document`;
#   • the `unit-management` skill — dimension and quantity vocabulary.
# So: strip the notation, keep the calculator's words. A turn that only
# quotes an equation contributes nothing; a turn that *explains* it
# contributes fully. Anyone extending this filter must preserve that split.
_MATH_WORD_SOURCE = ('derivation-engine', 'clauderc_canonical_maths',
                     'unit-management')   # documented, not enforced here


def strip_to_prose(text: str) -> str:
    """Reduce a conversation turn to the English prose the monad should
    hear — the part carrying word choice, order and context. Drops fenced
    code, tables, box-drawing, markdown scaffolding, links, and
    notation-dense lines. Same filter as monad_bin/corpus_strip.py, inlined
    and compact.

    Maths note: notation lines are deleted; the WORDS for the maths come
    from the calculator (the derivation engine's narration, the canonical
    maths reference, the unit-management vocabulary) — see
    _MATH_WORD_SOURCE above."""
    import re
    out: List[str] = []
    in_fence = False
    for ln in str(text).splitlines():
        s = ln.strip()
        if s.startswith('```') or s.startswith('~~~'):
            in_fence = not in_fence
            continue
        if in_fence or not s:
            continue
        if s[:1] in '|>#':
            s = s.lstrip('|># ').strip()
        s = re.sub(r'^([-*+]|\d+[.)]|[a-zA-Z][.)])\s+', '', s)   # list markers
        s = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', s)           # md links
        s = re.sub(r'`([^`]*)`', r'\1', s)                        # inline code
        s = re.sub(r'(\*\*|\*|__|_)(.+?)\1', r'\2', s)            # emphasis
        s = re.sub(r'https?://\S+', ' ', s).strip()
        if len(s) < 3:
            continue
        letters = sum(c.isalpha() for c in s)
        syms = sum(c in _NOTATION_SYMS for c in s)
        if letters == 0 or (syms and syms / max(letters, 1) > 0.35):
            continue
        out.append(s)
    return '\n'.join(out)


def _sentences(text: str, cap: int = 3500):
    """Yield <=cap-char pieces, breaking on sentence enders where possible —
    keeps a long turn under the daemon's 4 KB line buffer."""
    import re
    buf = ''
    for piece in re.split(r'(?<=[.!?])\s+', str(text)):
        if buf and len(buf) + len(piece) + 1 > cap:
            yield buf
            buf = ''
        buf = f'{buf} {piece}'.strip()
    if buf:
        yield buf


# ── module discovery — corrected APISniff: getattr chains, never exec ────
# APISniff.py (PtolemyDesktop/Phaleron/APISniff/) proved this pattern works:
# doc / contents / code, off dir() and inspect, no hand-written documentation
# anywhere. What it got wrong was building each lookup as a formatted code
# STRING and exec()-ing it to walk a breadcrumb path. A getattr chain gets
# the identical result without ever executing a string.

@dataclass
class MemberInfo:
    """One introspected member of a scope — a module, class, function,
    whatever dir() turns up. The same three sections APISniff already
    proved useful: doc, contents, code. `error` is set instead of raising
    when introspection fails partway, so a caller always gets an object
    back, never an exception to handle."""
    name: str
    kind: str                                   # module|class|function|method|builtin|callable|data|unknown
    doc: Optional[str] = None
    contents: List[str] = field(default_factory=list)   # dir() of this member, if it has one
    source: Optional[str] = None                # inspect.getsourcelines, if available
    error: Optional[str] = None


def _classify(obj: Any) -> str:
    if inspect.ismodule(obj):   return 'module'
    if inspect.isclass(obj):    return 'class'
    if inspect.isfunction(obj): return 'function'
    if inspect.ismethod(obj):   return 'method'
    if inspect.isbuiltin(obj):  return 'builtin'
    if callable(obj):           return 'callable'
    return 'data'


def _walk(root: Any, path: Sequence[str]) -> Any:
    """getattr-chain walk: root.a.b.c given ['a','b','c']. Raises
    AttributeError on a miss — callers decide whether that's fatal."""
    obj = root
    for p in path:
        obj = getattr(obj, p)
    return obj


def inspect_member(root: Any, path: Sequence[str] = ()) -> MemberInfo:
    """The corrected APISniff core. No exec() of formatted strings anywhere
    in this function or anything it calls."""
    try:
        obj = _walk(root, path)
    except AttributeError as e:
        return MemberInfo(name='.'.join(path) or repr(root), kind='unknown', error=str(e))

    name = path[-1] if path else getattr(root, '__name__', repr(root))
    info = MemberInfo(name=name, kind=_classify(obj), doc=inspect.getdoc(obj))

    try:
        info.contents = sorted(a for a in dir(obj) if not a.startswith('__'))
    except Exception:
        pass

    try:
        info.source = ''.join(inspect.getsourcelines(obj)[0])
    except (TypeError, OSError):
        pass  # builtins, C extensions, etc. — no source available, not an error

    return info


# ── static discovery — "see what's available", never execute anything ──────
# inspect_member() above needs an already-imported live object. That's fine
# for known-safe things (stdlib, an attached Monad). It is NOT safe as the
# default way to ask "what does this Face have" — checked by hand this
# session, Tesla alone has: a file that binds a UDP port and blocks forever
# in recvfrom() at import time (Sockets.py), a file with a dangling `import`
# statement that is a flat SyntaxError (HolePunchServer.py), and a file using
# @dataclass without importing it (Zork_Sentence_Parser.py, NameError on
# import). "Diagnostic mode, doesn't need to use any tools, just sees what's
# available" means static AST parsing — the source is read, never run.

@dataclass
class FileInfo:
    """What one .py file defines, read from its own source — never
    imported, so an import-time crash or a blocking call in that file
    cannot affect the caller."""
    path: str
    doc: Optional[str] = None
    classes: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    parse_error: Optional[str] = None


def discover_directory(path: str, pattern: str = '*.py') -> List[FileInfo]:
    """AST-only discovery of every file matching `pattern` in `path` — top-
    level class names, top-level function names, module docstring. Never
    imports, never executes. A file that fails to even parse (real example:
    HolePunchServer.py) comes back with parse_error set, not raised —
    discovery keeps going over the rest of the directory regardless."""
    import ast
    import glob as _glob
    import os as _os
    out: List[FileInfo] = []
    for fp in sorted(_glob.glob(_os.path.join(path, pattern))):
        info = FileInfo(path=fp)
        try:
            with open(fp, encoding='utf-8', errors='replace') as f:
                src = f.read()
            tree = ast.parse(src, filename=fp)
            info.doc = ast.get_docstring(tree)
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    info.classes.append(node.name)
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    info.functions.append(node.name)
        except SyntaxError as e:
            info.parse_error = f'SyntaxError: {e}'
        except Exception as e:
            info.parse_error = str(e)
        out.append(info)
    return out


# ── the harness itself ────────────────────────────────────────────────────

@dataclass
class FaceResult:
    """The one result shape every level of the toolset_registry returns —
    the harness calling a Face, or a Face (Tesla) calling one of its own
    tools underneath it, look identical to whoever made the call."""
    ok: bool
    data: Any = None
    error: Optional[str] = None
    handled_by: Optional[str] = None   # name of the handler that answered
    center: Optional[str] = None       # 'eye' | 'hands' | None — which of
                                        # the Monad's two centers made this
                                        # call, so Ptolemy (external — the
                                        # process clock already scheduling
                                        # every Face's thread, per
                                        # Ptolemy3.py's own threading
                                        # contract) can compare their tool
                                        # usage. Not evaluated here — the
                                        # harness only tags and keeps the
                                        # record; Ptolemy is the judge.


class ToolsetRegistry:
    """
    "The currently populated toolbox." Capability string in, a registered
    handler out. Used TWICE in this design, same class both times: once by
    the Harness (registering Faces), and once inside Tesla itself
    (registering its own tools — HolePunch, KVM, SensorStream, Sockets).
    That reuse is the point — a third level costs nothing new to add.

    NOT the future bus registry (see module docstring) — this only ever
    looks capabilities up and calls a handler; it never owns a desktop.
    """

    def __init__(self) -> None:
        self._handlers: Dict[str, tuple] = {}          # name -> (capabilities, handler)
        self._by_capability: Dict[str, List[str]] = {}  # capability -> [names]

    def register(self, name: str, capabilities: Sequence[str], handler) -> None:
        """handler: callable(capability: str, action: str, **params) ->
        FaceResult. Both are passed through, not just action — a handler
        that delegates to its OWN nested ToolsetRegistry (Tesla does this)
        needs the original capability to look itself up by, with action
        distinguishing which operation within it was requested."""
        self._handlers[name] = (tuple(capabilities), handler)
        for cap in capabilities:
            self._by_capability.setdefault(cap, [])
            if name not in self._by_capability[cap]:
                self._by_capability[cap].append(name)

    def unregister(self, name: str) -> None:
        caps, _ = self._handlers.pop(name, ((), None))
        for cap in caps:
            names = self._by_capability.get(cap, [])
            if name in names:
                names.remove(name)

    def candidates(self, capability: str) -> List[str]:
        return list(self._by_capability.get(capability, []))

    def names(self) -> List[str]:
        return sorted(self._handlers)

    def capabilities(self) -> List[str]:
        return sorted(self._by_capability)

    def reach(self, capability: str, name: Optional[str] = None,
              action: Optional[str] = None, chooser=None, **params) -> FaceResult:
        """
        Resolve `capability` to a registered handler and call it.

        name:    bypass candidate selection, call this handler directly —
                 the escape hatch for a caller that already knows who it wants.
        action:  passed through to the handler (defaults to `capability`
                 itself, since for a single-purpose handler they're the same).
        chooser: optional callable(candidate_names) -> name, for when more
                 than one handler offers the same capability. Defaults to
                 "first registered" — TODO: the lineage-engine-informed
                 tier/primitivity chooser described this session isn't
                 wired in yet; this is where it plugs in.

        handled_by reports the DEEPEST handler that actually answered, not
        just the top-level name reach() was called with — if a handler's
        own callable delegates to a nested ToolsetRegistry (Tesla does this
        for its own tools), that inner reach()'s handled_by passes through
        unchanged. Convention: name nested handlers 'facename.tool' (e.g.
        'tesla.kvm') so the result stays self-documenting at both levels.
        """
        if name is None:
            cands = self.candidates(capability)
            if not cands:
                return FaceResult(ok=False, error=f"no handler registered for {capability!r}")
            name = chooser(cands) if chooser else cands[0]
        entry = self._handlers.get(name)
        if entry is None:
            return FaceResult(ok=False, error=f"no handler named {name!r}")
        _, handler = entry
        try:
            result = handler(capability, action or capability, **params)
            if isinstance(result, FaceResult):
                if result.handled_by is None:
                    result.handled_by = name
                return result
            return FaceResult(ok=True, data=result, handled_by=name)
        except Exception as e:
            return FaceResult(ok=False, error=str(e), handled_by=name)


class Harness:
    """
    Everything a presentation layer needs from the Monad or from a repo's
    engines/tools comes from one Harness instance. Open-ended by design —
    grows as real needs surface, not pre-shaped for a fixed feature set.
    """

    CALL_LOG_MAX = 500   # bounded — this is a recent-activity window for
                          # Ptolemy to compare against, not an audit log

    def __init__(self) -> None:
        from three_hearers import ThreeHearers          # Tao 41: laughter is expected, not correction
        self.hearers = ThreeHearers()
        self.last_reaction: Optional[Dict[str, Any]] = None
        self._monad: Any = None
        self._roots: Dict[str, Any] = {}   # name -> browsable root (module/package/live scope)
        self.toolset_registry = ToolsetRegistry()
        self._lineage_module: Any = None
        self.call_log: List[FaceResult] = []
        self._pen: Any = None              # flock fd on MONAD3C_WRITER_LOCK while held
        self._repack_accum = 0.0           # leaky-integrator charge (see REPACK_*)
        self._repack_accum_ts = time.time()
        self._repack_last = time.time()
        self._repack_had_input = False
        # ── acquisition bus: language-blind backend + threading/memory governor
        self._backend: Any = None          # monad_bus.MonadBackend once loaded
        self._governor: Any = None         # monad_bus.ResourceGovernor (lazy)
        self._seen: Dict[str, float] = {}  # url -> last-fetch ts (dedup; stands
                                           # in for ptol_blockchain's Long Path)

    # ── the toolset registry — one capability-based call to any Face ───────

    def reach(self, capability: str, center: Optional[str] = None,
              **kwargs) -> FaceResult:
        """The single function the Monad calls for anything outside itself:
        `harness.reach('research', query=..., center='hands')`. Resolution
        and dispatch are entirely toolset_registry's job — see
        ToolsetRegistry.reach(). `center` ('eye'/'hands'/None) is stamped
        onto the result and appended to call_log — the harness does not
        compare the two centers' usage itself, that's Ptolemy's job as the
        already-scheduling process clock (Ptolemy3.py's threading contract),
        external to this file. This is only the record it reads from."""
        result = self.toolset_registry.reach(capability, **kwargs)
        result.center = center
        self.call_log.append(result)
        if len(self.call_log) > self.CALL_LOG_MAX:
            del self.call_log[:len(self.call_log) - self.CALL_LOG_MAX]
        return result

    def calls_by_center(self, center: str) -> List[FaceResult]:
        """Recent reach() results tagged with this center — what Ptolemy
        would pull to compare Eye's tool usage against Hands'."""
        return [r for r in self.call_log if r.center == center]

    # ── presenting output — the harness's one call to "show something" ─────
    # Surfaced building the first Monad that actually calls the harness
    # (Cody, 2026-08-25): the Monad needs somewhere to send a constructed
    # response that isn't "print it and hope" — a chat window, a curses
    # "lecture viewport" box, or PtolemyDesktop's own interface/window-
    # decoration code, once any of those exist. Kept exactly as open-ended
    # as the rest of this file: a Face registers under capability
    # 'viewport' (curses now, PGui/compositor later — same registration
    # shape as Tesla's 'network'), and present() reaches for it. With
    # nothing registered yet, the fallback is a plain print so output is
    # never lost while no real viewport exists — same call_log accounting
    # either way, so callers don't need to know which path answered.

    def present(self, content: Any, kind: str = 'text',
               center: Optional[str] = None) -> FaceResult:
        """The Monad's one call to show something to whatever's listening.
        Prefers a registered 'viewport' Face; falls back to stdout."""
        if self.toolset_registry.candidates('viewport'):
            return self.reach('viewport', center=center, action='present',
                              content=content, kind=kind)
        print(content)
        result = FaceResult(ok=True, data=content, handled_by='stdout_fallback',
                            center=center)
        self.call_log.append(result)
        if len(self.call_log) > self.CALL_LOG_MAX:
            del self.call_log[:len(self.call_log) - self.CALL_LOG_MAX]
        return result

    # ── the generational lineage engine — direct, not just for display ─────

    @property
    def lineage(self) -> Any:
        """Live reference to GenerationalLineage/engine/lineage.py —
        decompose(), TIERS, GenerationalLineageEngine, run(), all of it. This is
        what a tier-informed `chooser` in ToolsetRegistry.reach() would
        consult; format_derivation() below is a display formatter over the
        SAME module, not a separate thing.

        (Repo was SedenionFactoralRelativity -> FactoralDecomposition ->
        GenerationalLineage; the older dir names are tried as a fallback.)"""
        if self._lineage_module is None:
            import os
            import sys
            _theplace = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            _cands = [os.path.join(_theplace, d) for d in
                      ('GenerationalLineage', 'FactoralDecomposition',
                       'SedenionFactoralRelativity')]
            _repo = next((d for d in _cands if os.path.isdir(d)), _cands[0])
            if _repo not in sys.path:
                sys.path.insert(0, _repo)
            try:
                from engine import lineage as _lineage_mod
            except ImportError as e:
                raise RuntimeError(
                    f"generational lineage engine not reachable at {_repo}: {e}")
            self._lineage_module = _lineage_mod
        return self._lineage_module

    # ── monad lifecycle ───────────────────────────────────────────────────

    def attach_monad(self, monad: Any) -> None:
        """Attach a live Monad (VAPMIP.monad.Engine or compatible).
        Deliberately duck-typed — the harness doesn't own what counts as a
        Monad, it just holds whatever it's handed.

        Attaching also TAKES THE WRITER PEN (_take_pen): while a Monad is in
        the harness, the harness owns every write to monad3_c.bin and the
        monad.bin journal, and the bare-monad self-persist path stands down.
        detach_monad() hands the pen back. Failing to take the pen is a
        WARNING, not a fault — ingest still works, persistence just isn't
        ours to do until the current holder releases it."""
        self._monad = monad
        self._take_pen(owner='daemon')

    def detach_monad(self) -> None:
        """Fold any un-repacked ingest, release the writer pen, drop the
        Monad. The final fold is unconditional (not knee-gated) — a clean
        detach always lands what the charge curve was still holding. A bare
        Monad (or the ptol binary) can then reclaim the pen and resume
        self-persisting monad3_c.bin as its own exact copy."""
        if self._repack_had_input and self.holds_pen() and self.monad_attached:
            self.persist(also_c=True)
        self._release_pen()
        self._monad = None

    @property
    def monad_attached(self) -> bool:
        return self._monad is not None

    @property
    def monad(self) -> Any:
        """Raises if nothing is attached. Callers that need manual-mode
        fallback should check monad_attached first, not catch this."""
        if self._monad is None:
            raise RuntimeError("no Monad attached — check monad_attached first")
        return self._monad

    # ── acquisition bus: language-blind monad + threading/memory governor ──
    # The harness is BLIND to whether the Monad is the C binary (the ptolemy
    # daemon) or the python object. load_monad() picks one — or a
    # NullMonadBackend — and REPORTS. Every path here is warn-not-fault.

    def load_monad(self, prefer: str = 'auto') -> Dict[str, Any]:
        """Load a Monad backend at `prefer` ∈ {'auto','c','python'} and
        return the report. 'auto' = the C daemon if reachable, else the
        python RotaryBoxKiteMonad, else Null. Never raises."""
        try:
            from monad_bus import load_monad as _load
        except Exception as e:   # noqa: BLE001
            self.present(f"harness: monad_bus unavailable ({e}) — "
                         "backend stays unset", center=None)
            return {'chosen': None, 'why': f'import failed: {e}', 'alive': False}
        be, rpt = _load(prefer, fifo=OBSERVE_FIFO, sock=PTOLEMY_SOCKET,
                        spool=OBSERVE_SPOOL,
                        log=lambda m: self.present(m, center=None))
        self._backend = be
        self.present(f"harness: monad backend = {rpt['chosen']} "
                     f"({rpt['why']}); alive={rpt['alive']}", center=None)
        return rpt

    @property
    def backend(self) -> Any:
        return self._backend

    @property
    def governor(self) -> Any:
        """The threading/memory admission governor (lazy). Memory management
        falls out of threading: a job is admitted only if a slot is free AND
        committed RAM + its estimate stays under
        MemTotal + min(SwapTotal, MemTotal//2)."""
        if self._governor is None:
            try:
                from monad_bus import ResourceGovernor
                self._governor = ResourceGovernor()
            except Exception as e:   # noqa: BLE001
                self.present(f"harness: ResourceGovernor unavailable ({e})",
                             center=None)
        return self._governor

    def search(self, query: str, engine: str = 'ddg') -> FaceResult:
        """Harnessed search: the harness owns acquisition, so this routes
        through browse() (fetch → strip → ingest → render stub), which
        dedups repeat URLs. The BARE monad's search() opens the default
        browser instead — that path is on RotaryBoxKiteMonad, not here."""
        try:
            from monad_browse import search_url
        except Exception as e:   # noqa: BLE001
            return FaceResult(ok=False, error=f'monad_browse: {e}',
                              handled_by='harness.search')
        return self.browse(search_url(query, engine))

    def browse(self, url: str, ttl: float = 900.0, cls: str = 'web') -> FaceResult:
        """Fetch `url`, strip to prose, feed the vocabulary monad, hand a
        render summary to Paper's Hands. Governor-guarded (RAM + bandwidth
        admission) and deduped against a recent-URL cache within `ttl`
        seconds — 'locked behind the harness to keep repeat operations from
        happening'. Never raises."""
        now = time.time()
        last = self._seen.get(url)
        if last is not None and (now - last) < ttl:
            return FaceResult(ok=True, data='deduped', handled_by='harness.browse')
        try:
            from monad_browse import fetch, strip_html, estimate_ram
        except Exception as e:   # noqa: BLE001
            return FaceResult(ok=False, error=f'monad_browse: {e}',
                              handled_by='harness.browse')

        gov = self.governor
        # coarse pre-fetch estimate; refined once nbytes is known
        job = None
        cm = None
        if gov is not None:
            try:
                from monad_bus import Job
                job = Job(name=f"browse:{url[:56]}", tier=1,
                          ram_peak=8 * 1024 * 1024, bw_cost=1.0 * 1024 * 1024)
                cm = gov.guard(job)
                cm.__enter__()
            except Exception as e:   # noqa: BLE001
                self.present(f"harness: governor guard skipped ({e})", center=None)
                cm = None
        try:
            f = fetch(url)
            if f.status == 0 or f.status >= 400:
                return FaceResult(ok=False,
                                  error=f'fetch {f.status} {f.error}'.strip(),
                                  handled_by='harness.browse')
            is_html = 'html' in (f.content_type or '').lower() or not f.content_type
            if gov is not None and not gov.headroom_ok(
                    estimate_ram(f.nbytes, is_html)):
                self.present(f"harness: browse {url} — {f.nbytes} B exceeds the "
                             "memory ceiling, page not parsed", center=None)
                return FaceResult(ok=False, error='memory ceiling',
                                  handled_by='harness.browse')
            prose = strip_html(f.body, f.content_type, f.url_final)
        finally:
            if cm is not None:
                try:
                    cm.__exit__(None, None, None)
                except Exception:   # noqa: BLE001
                    pass

        self._seen[url] = now
        if len(self._seen) > 4096:
            cut = now - ttl
            self._seen = {k: v for k, v in self._seen.items() if v > cut}

        r = self.observe(prose, cls=cls)
        # render stitch — Paper's Hands / the BrowserWindow Face owns this later
        self.present(f"[browse] {f.url_final} — {f.nbytes} B, "
                     f"{len(prose.split())} words → {r.handled_by}",
                     kind='browse', center='hands')
        return FaceResult(ok=r.ok, data={'url': f.url_final, 'bytes': f.nbytes,
                                         'words': len(prose.split()),
                                         'ingest': r.handled_by, 'ingest_ok': r.ok},
                          handled_by='harness.browse')

    # ── the writer pen — repository OS lock on monad3_c.bin ───────────────
    # Copied up from the monad side, where "nothing else writes the combined
    # store" (CombinedMonad.checkpoint / monad_combine.write / .write_c) was
    # convention. Here it is enforced with flock, and made conditional on
    # harness attachment: harnessed → the harness holds the pen; bare → the
    # monad does. One writer, whole persistence surface, either way.

    def _take_pen(self, owner: str = 'daemon') -> bool:
        """flock(LOCK_EX | LOCK_NB) on MONAD3C_WRITER_LOCK; keep the fd on
        self._pen so the lock outlives this call. Write '<owner>:<pid>' to
        the '.owner' sidecar for the daemon's pre-write check. Returns True
        if taken, False (with a present() warning) if held elsewhere or the
        path is unwritable. Never raises, never blocks."""
        import fcntl
        if self._pen is not None:
            return True
        try:
            os.makedirs(os.path.dirname(MONAD3C_WRITER_LOCK), exist_ok=True)
            fd = open(MONAD3C_WRITER_LOCK, 'a+')
        except OSError as e:
            self.present(f"harness: cannot open writer pen ({e}) — "
                         "persistence disabled", center=None)
            return False
        try:
            fcntl.flock(fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            fd.close()
            self.present(
                f"harness: writer pen held by {self.pen_owner() or 'another process'} "
                "— ingest continues, persistence deferred", center=None)
            return False
        self._pen = fd
        try:
            with open(MONAD3C_WRITER_LOCK + '.owner', 'w') as o:
                o.write(f"{owner}:{os.getpid()}")
        except OSError:
            pass
        return True

    def _release_pen(self) -> None:
        import fcntl
        fd = self._pen
        if fd is None:
            return
        try:
            fcntl.flock(fd.fileno(), fcntl.LOCK_UN)
        finally:
            fd.close()
            self._pen = None
        try:
            os.unlink(MONAD3C_WRITER_LOCK + '.owner')
        except OSError:
            pass

    def holds_pen(self) -> bool:
        return self._pen is not None

    def pen_owner(self) -> Optional[str]:
        """'<owner>:<pid>' from the sidecar, or None. owner is 'daemon'
        (this harness / the running daemon) or 'ptolemy' (a bare Monad or
        the ptol binary self-persisting). The daemon reads this before it
        writes: a live 'ptolemy:<pid>' → the daemon stands down; stale,
        absent, or 'daemon:*' → the daemon proceeds."""
        try:
            with open(MONAD3C_WRITER_LOCK + '.owner') as f:
                return f.read().strip() or None
        except OSError:
            return None

    # ── conversational ingest — fire-and-forget ─────────────────────────

    def connection_ok(self) -> bool:
        """The check each hook makes before it writes. True if the ingest
        pipe is present and openable (the daemon is up and its drive is
        mounted). False → the hook should spool locally instead. Cheap:
        a non-blocking open, no handshake."""
        try:
            fd = os.open(OBSERVE_FIFO, os.O_WRONLY | os.O_NONBLOCK)
        except OSError:
            return False
        os.close(fd)
        return True

    def observe(self, text: str, cls: str = 'external',
                pair_id: Optional[str] = None) -> FaceResult:
        """Hear one conversation turn — fire-and-forget. `cls` ∈
        INGEST_POLICY: 'external' = a user prompt, 'internal' = the
        assistant's final prose (thinking / tool I/O stripped by the
        caller), 'document' = committed project docs off a post-commit hook.

        `pair_id` links an external prompt to the internal response it
        drew, so the daemon can log the (prompt_bytes → response_bytes)
        sample — raw material for a response-scaling engine. Ignored for
        'document'.

        Prose-strips, then drops the framed message on OBSERVE_FIFO and
        returns immediately — the daemon drains it concurrently. If the
        pipe is unreachable: append to OBSERVE_SPOOL (local storage,
        drained by the daemon later); if THAT fails too, fall back to
        in-process ingest through an attached Monad; with none of those,
        warn. Never blocks on the daemon, never raises."""
        pol = INGEST_POLICY.get(cls)
        if pol is None:
            return FaceResult(ok=False, error=f"unknown ingest class {cls!r}")
        prose = strip_to_prose(text)
        if cls == 'external':
            self.last_reaction = self.hearers.note(pair_id or 'conversation', prose)    # laughter never raises the monad's emote
        if not prose:
            return FaceResult(ok=True, data='(nothing to hear)',
                              handled_by='observe')

        self._usage_hear(prose, cls, pair_id)           # usage, senses and Broca-Wernicke drift (conversation_usage.py); never raises

        hdr = cls if (not pair_id or cls == 'document') else f"{cls} {pair_id}"
        msg = f"{hdr}\n" + "\n".join(_sentences(prose)) + "\n.\n"

        if self._fifo_write(msg):
            return FaceResult(ok=True, data=f"{len(prose.split())} words",
                              handled_by='daemon.fifo')
        # A LOCAL (python) backend learns in-process now — spooling into a
        # void only helps when a daemon will drain it later.
        be = self._backend
        local_backend = be is not None and getattr(be, 'name', '').startswith('python')
        if local_backend:
            self._observe_in_process(prose, pol)
            return FaceResult(ok=True, data=f"{len(prose.split())} words",
                              handled_by='harness.observe')
        if self._spool_write(msg):
            return FaceResult(ok=True, data='spooled', handled_by='observe.spool')
        if self.monad_attached or be is not None:
            self._observe_in_process(prose, pol)
            return FaceResult(ok=True, data=f"{len(prose.split())} words",
                              handled_by='harness.observe')

        self.present("harness: no pipe, no spool, no Monad — "
                     f"conversational ingest dropped a {cls} turn", center=None)
        return FaceResult(ok=False, error='nowhere to ingest',
                          handled_by='observe')

    def _usage_hear(self, prose: str, cls: str, pair_id: Optional[str]) -> None:
        """The daemon's usage channel (2026-11-25): in-process, lazy, off with PTOL_USAGE=0, a failure is a warning, not an error."""
        if os.environ.get('PTOL_USAGE', '1') == '0':
            return
        try:
            if getattr(self, '_cu', None) is None:
                import conversation_usage
                self._cu = conversation_usage.ConversationUsage()
            self._cu.hear(prose, cls, pair_id)
        except Exception as e:   # noqa: BLE001
            self._cu = False if getattr(self, '_cu', None) is None else self._cu
            self.present(f"harness: usage channel failed ({e})", center=None)

    @property
    def usage(self):
        """The ConversationUsage in force (its `.store`, `.vocab`, `.drift`, `.channels['bw_correction']`), or None."""
        return getattr(self, '_cu', None) or None

    def hear_turn(self, prompt: Optional[str] = None,
                  response: Optional[str] = None,
                  pair_id: Optional[str] = None) -> List[FaceResult]:
        """Convenience for a hook / bus: feed a prompt as 'external' and a
        response as 'internal' in one call, linked by `pair_id` (a random
        token if not given, when both halves are present) so the daemon
        can record the prompt→response scale sample. Either half may be
        None."""
        if pair_id is None and prompt and response:
            pair_id = os.urandom(6).hex()
        out: List[FaceResult] = []
        if prompt:
            out.append(self.observe(prompt, 'external', pair_id))
        if response:
            out.append(self.observe(response, 'internal', pair_id))
        return out

    def hear_documents(self, paths: Sequence[str]) -> List[FaceResult]:
        """Feed committed project docs (wiki / README / papers) as the
        'document' class. Each file is read, prose-stripped by observe(),
        and sent. Missing / unreadable files are skipped, not raised — a
        post-commit hook must never fail the commit."""
        out: List[FaceResult] = []
        for p in paths:
            try:
                with open(p, encoding='utf-8', errors='replace') as f:
                    body = f.read()
            except OSError:
                continue
            out.append(self.observe(body, 'document'))
        return out

    def _fifo_write(self, msg: str) -> bool:
        """One non-blocking write to the ingest pipe. False if the pipe is
        absent, has no reader (daemon down), or would block (reader wedged)
        — the caller then spools. Never raises."""
        try:
            fd = os.open(OBSERVE_FIFO, os.O_WRONLY | os.O_NONBLOCK)
        except OSError:
            return False
        try:
            data = msg.encode('utf-8', 'replace')
            return os.write(fd, data) == len(data)
        except OSError:
            return False
        finally:
            os.close(fd)

    def _spool_write(self, msg: str) -> bool:
        """Append the framed message to the local spool for the daemon to
        drain later. False only if the spool itself is unwritable."""
        try:
            os.makedirs(os.path.dirname(OBSERVE_SPOOL), exist_ok=True)
            with open(OBSERVE_SPOOL, 'a', encoding='utf-8') as f:
                f.write(msg)
            return True
        except OSError:
            return False

    def _observe_in_process(self, prose: str, pol: Dict[str, float]) -> None:
        """Last-resort direct ingest — used when the daemon FIFO and the
        spool are both unreachable. Routes through the language-blind
        backend if one is loaded (monad_bus.MonadBackend), else falls back
        to the duck-typed `.crank.learn` on an attached Monad. A missing
        target is a silent no-op. Charges the repack timer and folds at the
        knee."""
        did = False
        if self._backend is not None:
            try:
                self._backend.learn(prose, pol['w_sem'],
                                    pol.get('w_ctx', pol['w_sem']))
                did = True
            except Exception as e:   # noqa: BLE001
                self.present(f"harness: backend ingest failed ({e})", center=None)
        if not did:
            crank = getattr(self._monad, 'crank', None)
            if crank is None or not hasattr(crank, 'learn'):
                return
            try:
                crank.learn(prose, weight=pol['w_sem'], w_ctx=pol['w_ctx'])
            except TypeError:
                crank.learn(prose, weight=pol['w_sem'])   # pre-vector monad
            except Exception as e:   # noqa: BLE001
                self.present(f"harness: in-process ingest failed ({e})", center=None)
                return
        self._repack_charge(len(prose.encode('utf-8')))
        if self.repack_due():
            self.persist(also_c=True)

    # ── input-size repack timer — leaky integrator, fires at the knee ────

    def _repack_store_bytes(self) -> int:
        """Proxy for the size of the store a fold rewrites: the journal
        pickle if present, else 0 (→ K floors at REPACK_K_MIN)."""
        j = os.path.expanduser('~/.ptolemy/monad.bin')
        try:
            return os.path.getsize(j)
        except OSError:
            return 0

    def _repack_K(self) -> float:
        k = REPACK_RATIO * self._repack_store_bytes()
        return min(max(k, REPACK_K_MIN), REPACK_K_MAX)

    def _repack_charge(self, nbytes: int) -> None:
        now = time.time()
        if now > self._repack_accum_ts:
            self._repack_accum *= math.exp(
                -(now - self._repack_accum_ts) / REPACK_TAU)
        self._repack_accum += float(nbytes)
        self._repack_accum_ts = now
        self._repack_had_input = True

    def repack_urgency(self) -> float:
        """Where we are on the charge curve, in [0, 1). Bleeds with elapsed
        time — call it any time for a live reading."""
        now = time.time()
        a = self._repack_accum
        if now > self._repack_accum_ts:
            a *= math.exp(-(now - self._repack_accum_ts) / REPACK_TAU)
        k = self._repack_K()
        return 1.0 - math.exp(-a / k) if k else 0.0

    def repack_due(self) -> bool:
        """True when the accumulator has reached the knee (accum ≥ K·(1−1/e),
        i.e. urgency ≥ REPACK_KNEE) or the max-age floor is hit with
        un-folded input pending."""
        if not self._repack_had_input:
            return False
        if self.repack_urgency() >= REPACK_KNEE:
            return True
        return (time.time() - self._repack_last) >= REPACK_MAX_AGE

    def _repack_reset(self) -> None:
        self._repack_accum = 0.0
        self._repack_accum_ts = time.time()
        self._repack_last = time.time()
        self._repack_had_input = False

    # ── persistence — the exact-copy write path, pen-gated ───────────────

    def persist(self, also_c: bool = True) -> FaceResult:
        """Serialise the attached Monad's state: the journal pickle and,
        with also_c, the packed monad3_c.bin. Runs only while this harness
        holds the writer pen; otherwise a warning (the pen's holder does
        it). The pack is delegated to monad_combine.write / write_c — ONE
        serializer, so a harness-written and a bare-monad-written bin are
        byte-identical (the pack invariant)."""
        if not self.monad_attached:
            return FaceResult(ok=False, error='no Monad attached')
        if not self.holds_pen() and not self._take_pen(owner='daemon'):
            return FaceResult(ok=False, error='writer pen held elsewhere',
                              handled_by='persist')
        try:
            _here = os.path.dirname(os.path.abspath(__file__))
            import sys as _sys
            if _here not in _sys.path:
                _sys.path.insert(0, _here)
            import monad_combine as _mc
        except ImportError as e:
            return FaceResult(ok=False, error=f"monad_combine unavailable: {e}")
        cm = getattr(self._monad, 'combined', None) or self._monad
        paths: Dict[str, str] = {}
        try:
            paths['journal'] = _mc.write(cm)
            if also_c:
                paths['packed'] = _mc.write_c(cm)
        except Exception as e:
            return FaceResult(ok=False, error=str(e), handled_by='persist')
        self._repack_reset()   # the charge curve starts over from a clean fold
        return FaceResult(ok=True, data=paths, handled_by='persist')

    # ── the daemon — the harness runs it; absence is a warning ───────────

    @property
    def daemon_up(self) -> bool:
        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.settimeout(0.5)
            s.connect(PTOLEMY_SOCKET)
            s.close()
            return True
        except OSError:
            return False

    def run_daemon(self, argv: Optional[Sequence[str]] = None,
                   wait: float = 3.0) -> bool:
        """Ensure the ptol daemon is up. The harness runs the daemon; a
        daemon that will not start is a WARNING, not a fault — the harness
        falls back to in-process ingest through the attached Monad. Returns
        True if the daemon is up afterwards."""
        if self.daemon_up:
            return True
        cmd = list(argv) if argv else ['ptol', '--daemon']
        try:
            self._daemon_proc = subprocess.Popen(
                cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except (OSError, ValueError) as e:
            self.present(f"harness: could not start daemon ({e}) — "
                         "falling back to in-process ingest", center=None)
            return False
        deadline = time.time() + wait
        while time.time() < deadline:
            if self.daemon_up:
                return True
            time.sleep(0.1)
        self.present("harness: daemon did not come up in time — "
                     "falling back to in-process ingest", center=None)
        return False

    def _daemon_send(self, line: str, payload: Optional[str] = None
                     ) -> Optional[str]:
        """Send one command and read to the lone-'.' sentinel. Returns the
        response text, or None if the daemon is unreachable (a present()
        warning, never a raise). `payload`, if given, is sent
        sentence-per-line after `line` so a long turn stays under the
        daemon's 4 KB line buffer, then a lone '.'."""
        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.settimeout(2.0)
            s.connect(PTOLEMY_SOCKET)
        except OSError:
            return None
        try:
            f = s.makefile('rwb', buffering=0)
            f.write((line + '\n').encode('utf-8', 'replace'))
            if payload is not None:
                for chunk in _sentences(payload):
                    f.write((chunk + '\n').encode('utf-8', 'replace'))
                f.write(b'.\n')
            f.flush()
            out: List[str] = []
            while True:
                raw = f.readline()
                if not raw or raw.rstrip(b'\r\n') == b'.':
                    break
                out.append(raw.decode('utf-8', 'replace'))
            return ''.join(out).strip()
        except OSError as e:
            self.present(f"harness: daemon send failed ({e})", center=None)
            return None
        finally:
            s.close()

    # ── module discovery ──────────────────────────────────────────────────

    def register_root(self, name: str, root: Any) -> None:
        """Add a browsable root — an already-imported module/package, or
        the harness's own live scope for a 'Current' root (APISniff's own
        special case: pass sys.modules[__name__] or similar)."""
        self._roots[name] = root

    def import_root(self, name: str, module_path: str) -> None:
        """Import module_path and register it under name, so a caller can
        add a browsable root by dotted path (e.g. 'ValaQuenta.engine')
        without the harness needing to know about it in advance."""
        self._roots[name] = importlib.import_module(module_path)

    def roots(self) -> List[str]:
        return sorted(self._roots)

    def inspect(self, root_name: str, path: Sequence[str] = ()) -> MemberInfo:
        """The corrected-APISniff lookup: doc/contents/code for
        roots[root_name].<path>. Real, not a stub — cheap, mechanical, and
        every registered root gets it for free with zero per-module
        wiring."""
        if root_name not in self._roots:
            return MemberInfo(name=root_name, kind='unknown',
                              error=f"no root registered as {root_name!r}")
        return inspect_member(self._roots[root_name], path)

    # ── tools-over-engines routing ────────────────────────────────────────

    def get_module_view(self, root_name: str, path: Sequence[str] = ()) -> MemberInfo:
        """Prefer a module's tools.py / viewer_data() surface when the
        target has one; fall back to raw inspect() otherwise.

        TODO: the tools.py-detection heuristic. For now this always falls
        back to inspect() — no curses box exists yet to demand the richer
        shape, so there's nothing yet to route toward. Real detection logic
        (matching SedenionFactoralRelativity's and ValaQuenta's existing
        maths.py/tools.py split) goes here once one does.
        """
        return self.inspect(root_name, path)

    def discover_face(self, name: str, directory: str,
                      pattern: str = '*.py') -> Dict[str, FileInfo]:
        """Safe ('diagnostic mode') discovery of what a Face's directory
        offers — static AST parsing, never imports. This is the pattern
        for visiting each Face: Tesla first, same call for every other one
        later. Cached per (name, directory) — call again after the Face's
        code changes if you need a fresh read."""
        if not hasattr(self, '_face_discoveries'):
            self._face_discoveries: Dict[str, Dict[str, FileInfo]] = {}
        key = f'{name}:{directory}'
        if key not in self._face_discoveries:
            files = discover_directory(directory, pattern)
            self._face_discoveries[key] = {f.path: f for f in files}
        return self._face_discoveries[key]

    # ── the box-data contract ─────────────────────────────────────────────

    def get_box_data(self, box_spec: Dict[str, Any]) -> Dict[str, Any]:
        """TODO: the single call every curses box will make to refresh
        itself. Shape deliberately undecided until the curses UI is built
        against it — stubbed here so the method exists and box code can be
        written against it without waiting on this file again."""
        raise NotImplementedError("get_box_data: shape TBD when the curses UI needs it")

    # ── proof / derivation formatting ─────────────────────────────────────

    def format_derivation(self, obj: Any) -> str:
        """Render a Relation (SedenionFactoralRelativity) or an Equation
        (ValaQuenta) as a proof-flavoured paragraph — generated from
        whichever fields the object actually has, never hand-written.
        Duck-typed on purpose: a future module's own result object works
        here too, as long as it carries a matching handful of field names.
        """
        # SedenionFactoralRelativity.Relation: name, claim, tier, descends, status, detail
        if hasattr(obj, 'claim') and hasattr(obj, 'descends'):
            status = getattr(obj, 'status', None)
            status_word = getattr(status, 'value', status)
            return (
                f"{obj.name} (tier {obj.tier}). {obj.claim}\n"
                f"Descends from: {obj.descends}\n"
                f"Status: {status_word}\n"
                f"{getattr(obj, 'detail', '')}"
            )
        # ValaQuenta.Equation: name, display, confidence, code_verified, params
        if hasattr(obj, 'display') and hasattr(obj, 'confidence'):
            verified = 'code-verified' if getattr(obj, 'code_verified', False) else 'not yet code-verified'
            params = ', '.join(getattr(obj, 'params', None) or []) or 'none'
            return (
                f"{obj.display} [{obj.confidence}, {verified}]\n"
                f"Variables: {params}"
            )
        # TODO: anything that isn't one of the two known shapes yet.
        return f"(no known derivation format for {type(obj).__name__})"

    # ── standing intent ───────────────────────────────────────────────────

    intent = INTENT

    def justify_gate(self, reason: str) -> str:
        return justify_gate(reason)

    # ── per-user context buffers (Philadelphos.cyclic_context_buffer) ──────
    # One CyclicContextBuffer PER USER — a live, per-conversation version of
    # a .clauderc-style context file, generated purely from that user's own
    # interactions, partitioned and selected as needed rather than pouring
    # everything into one ever-growing window. Ptolemy3.py currently holds
    # ONE kernel-level instance (self.ccb) — that's a real gap against this
    # per-user design, not yet reconciled, noted rather than papered over.
    # STUB: real CyclicContextBuffer (Philadelphos/cyclic_context_buffer.py)
    # is a FIFO sliding window of EntryObjects (prompt+response), confirmed
    # eviction (compress -> hyperindex -> commit to a BranchBlockchain) —
    # the harness just needs to hold one per user_id and hand it back; it
    # does not reimplement any of that.

    def __init_context_buffers(self) -> None:
        if not hasattr(self, '_context_buffers'):
            self._context_buffers: Dict[str, Any] = {}

    def attach_context_buffer(self, user_id: str, buffer: Any) -> None:
        """Register a user's live CyclicContextBuffer (or compatible)."""
        self.__init_context_buffers()
        self._context_buffers[user_id] = buffer

    def detach_context_buffer(self, user_id: str) -> None:
        self.__init_context_buffers()
        self._context_buffers.pop(user_id, None)

    def context_buffer(self, user_id: str) -> Any:
        """Returns None if this user has no live buffer yet — callers
        should treat that as 'nothing partitioned in yet', not an error."""
        self.__init_context_buffers()
        return self._context_buffers.get(user_id)

    def context_users(self) -> List[str]:
        self.__init_context_buffers()
        return sorted(self._context_buffers)

    # ── compositor (Pharos.PGui / PWindow) ──────────────────────────────────
    # PGui: the self-contained shim replicating Qt window decoration via a
    # minimal SVG low-overhead replacement -- this IS where "PtolemyDesktop
    # must remain a compositor" lives, and it's what gives Ptolemy real KVM
    # access through Tesla. Explicitly underdeveloped per Cody (toolset
    # creation has been the priority) -- stub only, no real integration yet.

    def attach_compositor(self, compositor: Any) -> None:
        self._compositor = compositor

    def detach_compositor(self) -> None:
        self._compositor = None

    @property
    def compositor_attached(self) -> bool:
        return getattr(self, '_compositor', None) is not None

    @property
    def compositor(self) -> Any:
        if not self.compositor_attached:
            raise RuntimeError(
                "no compositor attached -- PGui is underdeveloped, check "
                "compositor_attached before use, not a real integration yet")
        return self._compositor


# ── smoke test — functional, not a self-checked relation; this is systems
# glue, not a mathematical claim, and gets tested that way ───────────────
if __name__ == '__main__':
    import math as _math

    h = Harness()
    assert not h.monad_attached

    h.attach_monad(object())
    assert h.monad_attached
    h.detach_monad()
    assert not h.monad_attached

    h.register_root('math', _math)
    info = h.inspect('math', ['sqrt'])
    assert info.kind == 'builtin', info
    assert info.error is None, info

    missing = h.inspect('math', ['not_a_real_function'])
    assert missing.error is not None

    assert h.context_buffer('cody') is None
    h.attach_context_buffer('cody', object())
    assert h.context_users() == ['cody']
    h.detach_context_buffer('cody')
    assert h.context_users() == []

    assert not h.compositor_attached
    h.attach_compositor(object())
    assert h.compositor_attached
    h.detach_compositor()
    assert not h.compositor_attached

    # a stub Tesla, registered exactly the way a real one would be — a
    # nested ToolsetRegistry underneath, same class as the harness's own.
    # Naming convention: a nested handler is named 'facename.tool' so
    # handled_by (which reports the DEEPEST handler that actually answered,
    # not just the top-level Face) stays self-documenting either way.
    #
    # NOT kvm here, deliberately (Cody, 2026-08-24): KVM is a basic INPUT
    # function the Monad/Ptolemy needs directly to interact with anything
    # at all — it lives with Ptolemy, not behind a reach()-for-it capability
    # a moment might or might not grant. What DOES belong on Tesla's own
    # registry is the reach-for-it stuff — hole-punch rendezvous, sensor
    # streams, device discovery — genuinely optional tools, not a basic
    # sense/actuator every turn needs. 'network' (HolePunch) stands in here.
    tesla_tools = ToolsetRegistry()
    tesla_tools.register('tesla.holepunch', ['network'],
                         lambda capability, action, **p: FaceResult(ok=False,
                             error='Tesla.HolePunch not wired yet — stub'))

    def _tesla_handle(capability, action, **params):
        return tesla_tools.reach(capability, action=action, **params)

    h.toolset_registry.register('tesla', ['network', 'sensor',
                                          'device_interface'], _tesla_handle)

    r = h.reach('network', center='hands', action='punch', peer_id='ptolemy_local')
    assert r.handled_by == 'tesla.holepunch', r
    assert not r.ok and 'not wired yet' in r.error, r
    assert r.center == 'hands', r

    r2 = h.reach('research', center='eye', query='does not exist yet')
    assert not r2.ok and 'no handler registered' in r2.error, r2
    assert r2.center == 'eye', r2

    assert len(h.calls_by_center('hands')) == 1
    assert len(h.calls_by_center('eye')) == 1
    assert h.calls_by_center('eye')[0] is r2

    # present() — no viewport registered yet, falls back to stdout, still logged
    pr = h.present('smoke-test viewport fallback line', center='eye')
    assert pr.ok and pr.handled_by == 'stdout_fallback' and pr.center == 'eye', pr
    assert h.calls_by_center('eye')[-1] is pr

    # present() — a real viewport Face registered, present() reaches it instead
    h.toolset_registry.register('curses_viewport', ['viewport'],
                                lambda capability, action, **p: FaceResult(
                                    ok=True, data=f"[viewport] {p.get('content')}"))
    pr2 = h.present('routed through a registered viewport', center='hands')
    assert pr2.ok and pr2.handled_by == 'curses_viewport', pr2
    assert pr2.data == '[viewport] routed through a registered viewport', pr2

    try:
        h.lineage
        lineage_ok = True
    except RuntimeError as e:
        lineage_ok = False
        print(f'[lineage] not reachable (fine if SFR repo path differs): {e}')
    if lineage_ok:
        assert hasattr(h.lineage, 'TIERS') and hasattr(h.lineage, 'decompose')
        print(f"lineage engine reachable: {len(h.lineage.TIERS)} tiered operations known")

    class _FakeRelation:
        name, tier, claim = 'demo.smoke_test', 1, 'a fake relation for the smoke test'
        descends = 'ADD, SCALE'
        status = type('S', (), {'value': 'HOLDS'})()
        detail = '[fake] nothing measured, this is a formatting test'

    print(h.format_derivation(_FakeRelation()))
    print()
    print(h.justify_gate('reading a public FITS archive'))

    # ── conversational ingest + writer pen ───────────────────────────────
    prose = strip_to_prose(
        "Here is **real** prose.\n"
        "```\nx = f(y)   # dropped: fenced\n```\n"
        "σ = (r²/2)·sin(2θ) ⊗ ∅_RB   <- dropped: notation-dense\n"
        "| a | b |   <- dropped: table\n"
        "- and this list item survives as a sentence.")
    assert 'real prose' in prose, prose
    assert 'f(y)' not in prose and 'sin(2' not in prose and '| a |' not in prose, prose
    assert 'this list item survives' in prose, prose

    import tempfile as _tf
    _spooldir = _tf.mkdtemp(prefix='harness_smoke_')
    globals()['OBSERVE_FIFO'] = os.path.join(_spooldir, 'monad.observe.fifo')
    globals()['OBSERVE_SPOOL'] = os.path.join(_spooldir, 'observe.spool')

    h2 = Harness()
    # no daemon (no pipe) → the turn spools locally, never blocks, never raises
    assert not h2.connection_ok()
    r = h2.observe('a user prompt with nowhere to go', 'external')
    assert r.ok and r.handled_by == 'observe.spool', r
    with open(OBSERVE_SPOOL) as _sf:
        _spooled = _sf.read()
    assert _spooled.startswith('external\n') and _spooled.rstrip().endswith('.'), _spooled
    assert 'nowhere to go' in _spooled
    # bad class
    assert not h2.observe('x', 'sideways').ok
    # attach takes the pen; a second harness cannot
    assert not h2.holds_pen()
    h2.attach_monad(object())
    if h2.holds_pen():                       # skips if ~/.ptolemy is unwritable
        owner = h2.pen_owner()
        assert owner and owner.startswith('daemon:'), owner
        h3 = Harness()
        h3.attach_monad(object())
        assert not h3.holds_pen(), "two harnesses must not both hold the pen"
        h2.detach_monad()
        assert not h2.holds_pen()
        assert h3._take_pen(), "pen should free up once h2 detaches"
        h3.detach_monad()
    # in-process fallback: vector weight, one call, tolerates a pre-vector monad
    class _Crank:
        def __init__(self): self.calls = []
        def learn(self, text, weight=1.0, w_ctx=None):
            self.calls.append((weight, w_ctx))
            return len(text.split())
    class _M:
        def __init__(self): self.crank = _Crank()
    globals()['OBSERVE_SPOOL'] = os.path.join(_spooldir, 'nope', 'x')  # unwritable dir
    os.chmod(_spooldir, 0o500)
    try:
        h4 = Harness(); h4.attach_monad(_M())
        ing = h4.observe('assistant prose to the field', 'internal')
        assert ing.ok and ing.handled_by == 'harness.observe', ing
        assert h4._monad.crank.calls == [(0.9, 0.6)], h4._monad.crank.calls
        # one small turn does NOT reach the knee
        assert h4._repack_had_input and not h4.repack_due(), h4.repack_urgency()
        assert 0.0 < h4.repack_urgency() < REPACK_KNEE
    finally:
        os.chmod(_spooldir, 0o700)
    assert isinstance(h2.daemon_up, bool)

    # ── repack timer: charge to the knee, then it fires ──────────────────
    h5 = Harness()
    K = h5._repack_K()
    assert REPACK_K_MIN <= K <= REPACK_K_MAX
    # charge past the knee in one go
    h5._repack_charge(int(K * 3))
    assert h5.repack_due(), h5.repack_urgency()
    # bleed: after ~5·TAU of (simulated) silence, urgency collapses
    h5._repack_accum_ts = time.time() - 5 * REPACK_TAU
    assert h5.repack_urgency() < 0.05, h5.repack_urgency()
    assert not h5.repack_due()
    # max-age floor still fires with pending input
    h5._repack_charge(10)
    h5._repack_last = time.time() - REPACK_MAX_AGE - 1
    assert h5.repack_due()
    h5._repack_reset()
    assert not h5._repack_had_input and h5.repack_urgency() == 0.0

    import shutil as _sh
    _sh.rmtree(_spooldir, ignore_errors=True)
    print("\nharness.py: smoke test passed.")
