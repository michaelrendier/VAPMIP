#!/usr/bin/env python3
"""boxkite_orbweaver_monad.py — the spider-web composition cycle, on top of
the rotary box-kite Monad.  UNTESTED — this file is the test bench.

Cody, 2026-09-03:

  One box-kite traversal = one SENTENCE = one RADIUS.  WordNet's job ends
  at the sentence (rings of box-kites = sentences).  ABOVE the sentence is
  a different organiser: the orb-weaver web-construction cycle.

    STRUCTURE   anchor -> bridge -> frame -> hub(= zero-divisor reframe)
                -> radii (one per section axis, one through-line each)
    SCAFFOLD    the centre->out spiral: the outline, `reach` loops deep,
                `reach` set by SCALE (paragraph / section / chapter)
    CAPTURE     the out->in spiral: the prose, one arc = one paragraph,
                each unit ending on the CONNECTIVE that names the next
                move on the web
    FRUSTRATION when context flow is turbulent (>= 3 near-equal relations)
                the spiral reverses along a strut — a `however` pivot + an
                aciniform recap, then jump radius; the return steps
                interdigitate the outbound steps

The heavy WordNet sentence layer (`rotary_rerun_boxkite_monad`) is loaded
lazily and only when `weave_via()` is used.  The default `weave()` path is
decoupled: it takes a light word list + a 19-slot relation vector (or
sniffs a crude one from the text) so the web cycle itself is fast to test.

Paragraph *construction* is meant to move into monad3_c.bin and paragraph
*usage* into the granular .bin files — that redesign happens AFTER this
test.  The connective lexicon and block frames live here for now, scoped
as a template layer, not a claimed NLG system.
"""
from __future__ import annotations

import math
import random
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from monad import cam_encode
from rotary_rerun_monad import (
    BoxKite, BoxKiteUnavailable, MindsEye, PapersHands,
    Ledger, Relation, Status, Fault,
)
from ptolemy_monad import infer_direction

# ── sentence templates — copied from rotary_rerun_boxkite_monad so this
#    file does not drag in its heavy import chain just to fill a frame. ───
_SENTENCE_TEMPLATES: Dict[str, str] = {
    "classify": "this is a kind of {0}.",
    "enumerate": "it includes {0}, {1}, and {2}.",
    "decompose": "it is made of {0} and {1}.",
    "situate": "it is part of {0}.",
    "characterize": "it is marked by {0}.",
    "explain": "it happens because of {0}.",
    "imply": "it leads to {0}.",
    "associate": "it relates to {0}.",
    "compare": "it resembles {0}.",
    "contextualize": "it belongs to the domain of {0}.",
    "localize": "it is found in {0}.",
    "register": "it is used in {0}.",
    "observe": "{0}.",
}


def assemble_sentence(direction: str, words_out: List[str]) -> str:
    if not words_out:
        return "(no candidates found)"
    tmpl = _SENTENCE_TEMPLATES.get(direction, "{0}.")
    fillers = list(words_out)
    while len(fillers) < tmpl.count("{"):
        fillers.append(fillers[-1])
    return tmpl.format(*fillers[:tmpl.count("{")])


# ── the connective lexicon — segue words, each a silk operator and a move
#    on the web.  ~closed class (Halliday & Hasan / PDTB); a starter slice.
_CONNECTIVES: Dict[str, List[str]] = {
    "throughline": ["because", "therefore", "thus", "hence", "so", "it follows that"],
    "elaborate":   ["specifically", "more precisely", "in detail", "that is",
                    "in other words"],
    "exemplify":   ["for example", "for instance", "consider", "namely"],
    "wrap":        ["in sum", "on the whole", "overall", "in short", "to summarise"],
    "lateral":     ["and", "also", "moreover", "next", "similarly", "likewise"],
    "reverse":     ["but", "however", "yet", "that said", "conversely",
                    "on the other hand"],
    "return":      ["as established", "recall that", "to return to", "as noted"],
    "scope":       ["with respect to", "as for", "turning to"],
    "signpost":    ["we return to this below", "more on this later",
                    "setting this aside for now"],
}
# radial move on the web per connective class:
#   +1 outward, -1 inward, 0 lateral (next spoke), "pivot" = frustrated reversal
_SPIRAL_MOVE: Dict[str, Any] = {
    "throughline": +1, "elaborate": +1, "exemplify": +1,
    "wrap": -1, "return": -1, "lateral": 0, "reverse": "pivot",
    "scope": 0, "signpost": 0,
}

# genre = a field configuration: which blocks, in what order, how deep.
_GENRE: Dict[str, Dict[str, Any]] = {
    "paper":    {"blocks": ["bridge", "frame", "body", "wrap"], "reach_cap": 4},
    "report":   {"blocks": ["bridge", "body", "wrap"],          "reach_cap": 3},
    "memo":     {"blocks": ["bridge", "body"],                  "reach_cap": 2},
    "tutorial": {"blocks": ["frame", "body"],                   "reach_cap": 4},
    "note":     {"blocks": ["body"],                            "reach_cap": 1},
}
_DEPTH_NAME = {1: "paragraph", 2: "section", 3: "chapter", 4: "part"}

# 19 WordNet relation slots -> a coarse direction, for the sniffed vector.
# (rotary_rerun_boxkite uses ptolemy_monad.infer_direction on the real
# 19-vector; the sniffer below only needs enough spread to rank axes.)
_STOP = set("a an the of to in on and or is are was were be been it its this "
            "that these those with for as at by from into over under".split())


# ── the room-shape calc — a standalone Cassini-oval fit to the content
#    projected from the prompt.  b/c is the continuous<->discrete knob and
#    IS the flashlight-to-wall distance: b/c > 1 one connected room
#    (continuous / Smith), b/c = 1 the lemniscate (NOW forms, sigma=1/2),
#    b/c < 1 two disconnected lobes (discrete / gasket, the room fractures).
#    No 0_RB in the running calc — cam_encode + a two-focus fit + word count.
def _cassini_r2(theta: float, a: float, b: float) -> Optional[float]:
    """Cassini oval, foci (+-a, 0), product b^2, polar:
    r^2 = a^2 cos2t +- sqrt(b^4 - a^4 sin^2 2t).  Returns the outer r^2 or
    None where the curve does not reach this angle (the b<a gap)."""
    s2 = math.sin(2 * theta)
    disc = b ** 4 - a ** 4 * s2 * s2
    if disc < 0:
        return None
    return a * a * math.cos(2 * theta) + math.sqrt(disc)


@dataclass
class RoomShape:
    foci_distance: float             # c — how far the shape moves when scaled up
    lobe_width: float               # b — the content's own extent, turbulence-widened
    ratio: float                    # b / c
    regime: str                     # continuous | lemniscate | discrete
    node: List[float]               # NOW — the midpoint of the two foci in cam space
    sample6: List[float]            # 6 Cassini radii sampled toward the node tip


@dataclass
class Radius:
    direction: str
    text: str
    struts: List[int] = field(default_factory=list)


@dataclass
class Block:
    kind: str                       # bridge | scope | paragraph | pivot | wrap
    depth: int
    radius: Optional[str]
    text: str
    connective_out: str = ""
    move: Any = 0
    tense: str = ""                 # past | now | future (light-cone band)


@dataclass
class Document:
    genre: str
    scale: Any
    reach: int
    turbulent: bool
    bridge: str
    frame: str
    radii: List[Radius]
    scaffold: List[str]
    blocks: List[Block]
    room: Optional[RoomShape] = None
    ledger_rows: List[Relation] = field(default_factory=list)

    def render(self) -> str:
        r = self.room
        room_line = (f"ROOM  : Cassini b/c={r.ratio:.3f}  {r.regime}  "
                     f"(c={r.foci_distance:.3f} b={r.lobe_width:.3f})  "
                     f"sample6={[round(x, 2) for x in r.sample6]}"
                     if r else "ROOM  : (not computed)")
        L = [f"[{self.genre}  scale={self.scale}  reach={self.reach}"
             f"  {'turbulent' if self.turbulent else 'laminar'}"
             f"  radii={len(self.radii)}  blocks={len(self.blocks)}]",
             room_line,
             f"BRIDGE: {self.bridge}",
             f"FRAME : {self.frame}", "SCAFFOLD (centre->out):"]
        L += [f"    {s}" for s in self.scaffold]
        L.append("CAPTURE (out->in, along the lemniscate):")
        for b in self.blocks:
            tag = b.kind + (f"/{b.radius}" if b.radius else "")
            L.append(f"    ·d{b.depth} [{b.tense or '—':^6}] {tag}: {b.text}"
                     + (f"   -> [{b.connective_out}]" if b.connective_out else ""))
        return "\n".join(L)


class OrbWeaverMonad:
    """The web-construction cycle.  Holds its own MindsEye / PapersHands /
    BoxKite (fast to build); the heavy WordNet Monad is optional."""

    def __init__(self) -> None:
        self._eye = MindsEye()
        self._hands = PapersHands()
        try:
            self.box_kite: Optional[BoxKite] = BoxKite.between(self._eye, self._hands)
            self._kite_error: Optional[str] = None
        except BoxKiteUnavailable as exc:
            self.box_kite = None
            self._kite_error = str(exc)

    # ── helpers ──────────────────────────────────────────────────────────
    def _struts(self, text: str) -> List[int]:
        if self.box_kite is None:
            return []
        try:
            return sorted(self._eye.lit_struts(cam_encode(text)))
        except Exception:                                          # noqa: BLE001
            return []

    @staticmethod
    def _sniff(text: str) -> Tuple[List[str], List[int]]:
        """A crude word list + 19-slot relation vector from the raw text —
        enough to rank section axes without loading WordNet."""
        toks = [w.lower() for w in re.findall(r"[A-Za-z][A-Za-z'-]+", text)]
        content = [w for w in toks if w not in _STOP and len(w) > 2]
        # dedupe, keep order
        seen: set = set()
        words = [w for w in content if not (w in seen or seen.add(w))]
        rv = [0] * 19
        # spread counts across slots by a stable hash of each content word
        for w in content:
            rv[hash(w) % 19] += 1
        if not any(rv):
            rv[12] = 1                                    # 'observe' fallback slot
        return (words or ["it"]), rv

    def _ranked_directions(self, rv: List[int], k: int) -> List[str]:
        v = list(rv)
        out: List[str] = []
        for _ in range(max(1, k)):
            if not any(v):
                break
            try:
                d = infer_direction(v)
            except Exception:                                     # noqa: BLE001
                d = "observe"
            if d not in out:
                out.append(d)
            v[max(range(len(v)), key=lambda i: v[i])] = 0
        return out or ["observe"]

    @staticmethod
    def _turbulence(rv: List[int]) -> Tuple[bool, int]:
        if not any(rv):
            return False, 0
        m = max(rv)
        peaks = sum(1 for c in rv if c >= 0.5 * m and c > 0)
        return peaks >= 3, peaks

    @staticmethod
    def _reach(scale: float, genre: str) -> int:
        cap = _GENRE.get(genre, _GENRE["paper"])["reach_cap"]
        try:
            from GenerationalLineage.engine import line_descend       # noqa: PLC0415
            g = line_descend("scale", float(max(scale, 1e-6)), chart=True)["charts"]
            rung = g["discrete"].get("generation")
            if isinstance(rung, int):
                return max(1, min(cap, rung + 1))
        except Exception:                                            # noqa: BLE001
            pass
        return max(1, min(cap, int(round(scale))))

    def _conn(self, cls: str, rng: random.Random) -> Tuple[str, Any]:
        return rng.choice(_CONNECTIVES.get(cls, ["and"])), _SPIRAL_MOVE.get(cls, 0)

    # ── the room-shape calc (standalone; no 0_RB) ────────────────────────
    def room_shape(self, text: str, words: List[str], peaks: int) -> RoomShape:
        f1 = cam_encode(text)
        bridge = assemble_sentence("contextualize", words)   # the scaled-up form
        f2 = cam_encode(bridge)
        c = math.sqrt(sum((x - y) ** 2 for x, y in zip(f1, f2))) or 1e-9
        norm1 = math.sqrt(sum(x * x for x in f1)) or 1e-9
        b = norm1 / (1.0 + 0.5 * peaks)          # narrower room when turbulent
        ratio = b / c
        regime = ("continuous" if ratio > 1.15
                  else "lemniscate" if ratio >= 0.9 else "discrete")
        node = [(x + y) / 2.0 for x, y in zip(f1, f2)]
        # sample the Cassini outline toward the node tip (theta -> pi/4)
        a = c / 2.0
        s6: List[float] = []
        for i in range(6):
            th = (math.pi / 4.0) * (i + 0.5) / 6.0
            r2 = _cassini_r2(th, a, b)
            s6.append(math.sqrt(r2) if r2 and r2 > 0 else 0.0)
        return RoomShape(foci_distance=c, lobe_width=b, ratio=ratio,
                         regime=regime, node=node, sample6=s6)

    @staticmethod
    def _reach_from_room(room: RoomShape, genre: str) -> int:
        cap = _GENRE.get(genre, _GENRE["paper"])["reach_cap"]
        # continuous = one connected room = shallow;
        # discrete = fractured lobes = deeper, more structure
        if room.regime == "continuous":
            r = 1
        elif room.regime == "lemniscate":
            r = 2
        else:                                    # discrete: deeper as b/c shrinks
            r = 3 + (1 if room.ratio < 0.6 else 0)
        return max(1, min(cap, r))

    @staticmethod
    def _tense(depth: int, reach: int) -> str:
        if reach <= 1:
            return "now"
        frac = (reach - depth) / (reach - 1)     # 0 deepest (past) .. 1 shallow (future)
        return "past" if frac < 0.34 else "future" if frac > 0.66 else "now"

    # ── the cycle ────────────────────────────────────────────────────────
    def weave(self, text: str, scale: Any = 2.0, genre: str = "paper",
              words: Optional[List[str]] = None,
              root_vector: Optional[List[int]] = None,
              seed: int = 20260903) -> Document:
        rng = random.Random(seed)
        if words is None or root_vector is None:
            words, root_vector = self._sniff(text)
        rv = list(root_vector)
        turbulent, peaks = self._turbulence(rv)
        room = self.room_shape(text, words, peaks)
        # scale="auto" -> reach from the content's own room shape;
        # a number -> the old hand path (kept for A/B).
        reach = (self._reach_from_room(room, genre) if scale == "auto"
                 else self._reach(scale, genre))
        gblocks = _GENRE.get(genre, _GENRE["paper"])["blocks"]

        # STRUCTURE ---------------------------------------------------------
        bridge = assemble_sentence("contextualize", words)
        frame_s = assemble_sentence("situate", words)
        n_axes = max(1, min(reach + 1, len(words)))
        dirs = self._ranked_directions(rv, n_axes)
        radii = [Radius(d, assemble_sentence(d, words),
                        self._struts(assemble_sentence(d, words))) for d in dirs]

        # SCAFFOLD SPIRAL (centre -> out) ---------------------------------
        scaffold: List[str] = []
        for depth in range(1, reach + 1):
            dn = _DEPTH_NAME.get(depth, f"d{depth}")
            for r in radii:
                scaffold.append(f"[{dn}] {r.direction}: {r.text}")

        # CAPTURE SPIRAL (out -> in, along the lemniscate: in through the
        # Past lobe, across the NOW node, out through the Future lobe) ----
        blocks: List[Block] = []
        if "bridge" in gblocks:
            blocks.append(Block("bridge", 0, None, bridge,
                                *self._conn("throughline", rng), tense="now"))
        if "frame" in gblocks:
            blocks.append(Block("scope", 0, None, frame_s,
                                *self._conn("scope", rng), tense="now"))

        for depth in range(reach, 0, -1):
            dn = _DEPTH_NAME.get(depth, f"level {depth}")
            tn = self._tense(depth, reach)
            for pos, r in enumerate(radii):
                cw, mv = self._conn("elaborate", rng)
                blocks.append(Block("paragraph", depth, r.direction,
                                    f"{cw.capitalize()}, {r.text[:-1]} at the "
                                    f"{dn} level.", cw, mv, tense=tn))
                if len(words) > pos + 1:
                    hw, hm = self._conn("exemplify", rng)
                    blocks.append(Block("paragraph", depth, r.direction,
                                        f"{hw.capitalize()}: {words[pos + 1]}.",
                                        hw, hm, tense=tn))
                # FRUSTRATION / EDDY: turbulent -> the point is contested at
                # the top red line; reverse along the strut, recap, jump
                # spoke.  The return step interdigitates the outbound step.
                if turbulent and depth == reach and pos < len(radii) - 1:
                    rw, rm = self._conn("reverse", rng)
                    blocks.append(Block("pivot", depth, r.direction,
                                        f"{rw.capitalize()}, the {r.direction} axis "
                                        f"only carries so far here.", rw, rm, tense=tn))
                    ww, wm = self._conn("wrap", rng)
                    blocks.append(Block("wrap", depth, r.direction,
                                        f"{ww.capitalize()}, {r.text[:-1]} — carried "
                                        f"back to the hub.", ww, wm, tense=tn))
        if "wrap" in gblocks:
            ww, wm = self._conn("wrap", rng)
            blocks.append(Block("wrap", 0, None, f"{ww.capitalize()}, {bridge[:-1]}.",
                                ww, wm, tense="now"))

        rows = self._measure(radii, blocks, room, turbulent, peaks, reach, rng)
        return Document(genre=genre, scale=scale, reach=reach, turbulent=turbulent,
                        bridge=bridge, frame=frame_s, radii=radii,
                        scaffold=scaffold, blocks=blocks, room=room, ledger_rows=rows)

    def weave_via(self, rbk_monad: Any, text: str, **kw) -> Document:
        """Heavy path: use a fully-built RotaryBoxKiteMonad for the real
        WordNet sentence layer, then weave.  Not exercised in __main__."""
        enc = rbk_monad.process_input(text)
        return self.weave(text, words=enc.words_out or None,
                          root_vector=list(enc.root_vector), **kw)

    # ── measurement (UNTESTED — new model, tiny n) ──────────────────────
    def _measure(self, radii: List[Radius], blocks: List[Block],
                 room: RoomShape, turbulent: bool, peaks: int, reach: int,
                 rng: random.Random) -> List[Relation]:
        rows: List[Relation] = []
        para = [b for b in blocks if b.kind == "paragraph" and b.radius]
        if self.box_kite is not None and para and len(radii) > 1:
            by_dir = {r.direction: set(r.struts) for r in radii}
            real = [len(set(self._struts(b.text)) & by_dir.get(b.radius, set()))
                    for b in para]
            ctrl = []
            for b in para:
                other = rng.choice([d for d in by_dir if d != b.radius]
                                   or list(by_dir))
                ctrl.append(len(set(self._struts(b.text)) & by_dir[other]))
            rmean = sum(real) / len(real)
            cmean = sum(ctrl) / len(ctrl)
            rows.append(Relation(
                name="orbweaver.paragraph_hangs_on_its_radius",
                claim="a capture-spiral paragraph shares more box-kite struts "
                      "with its own radius than with another radius",
                status=Status.UNTESTED,
                expected="real_mean > ctrl_mean",
                observed=f"{rmean:.3f} vs {cmean:.3f}  (n={len(para)})",
                detail="new model, tiny n — direction only",
                group="spider-web-composition"))
        else:
            rows.append(Relation(
                name="orbweaver.paragraph_hangs_on_its_radius",
                claim="capture-spiral paragraph <-> its radius strut overlap",
                status=Status.UNTESTED, fault=Fault.NONE,
                detail=f"BoxKite/para unavailable: {self._kite_error}",
                group="spider-web-composition"))
        rows.append(Relation(
            name="orbweaver.frustration_on_turbulence",
            claim="turbulent context flow (>=3 near-equal relations) triggers "
                  "spiral reversals (pivot + aciniform recap)",
            status=Status.UNTESTED,
            observed=f"turbulent={turbulent}  n_peaks={peaks}  "
                     f"pivots={sum(1 for b in blocks if b.kind == 'pivot')}",
            detail="mechanism wired; not validated against read-back",
            group="spider-web-composition"))

        # ── the room-shape / Cassini knob: does content shape's b/c set a
        # sensible reach, and does 'discrete' (b/c<1) really carry more
        # structure than 'continuous' (b/c>1)? ──────────────────────────
        rows.append(Relation(
            name="orbweaver.room_shape_sets_reach",
            claim="content-shape Cassini b/c (flashlight-to-wall) sets reach: "
                  "continuous(>1.15)->1  lemniscate(~1)->2  discrete(<1)->deeper",
            status=Status.UNTESTED,
            observed=f"b/c={room.ratio:.3f}  regime={room.regime}  "
                     f"reach={reach}  auto_reach={self._reach_from_room(room, 'paper')}",
            detail="the room is fitted from cam_encode(text) vs its scaled-up "
                   "form; no 0_RB in the fit",
            group="spider-web-composition"))

        # ── the lemniscate flow: does each block's connective point the way
        # its light-cone band (past/now/future) says it should? ─────────
        cflow = [b for b in blocks if b.connective_out and b.tense]
        if cflow:
            ok = 0
            for b in cflow:
                mv = b.move
                if b.tense == "now":
                    ok += 1
                elif b.tense == "past" and mv in (-1, 0):      # gathering -> inward
                    ok += 1
                elif b.tense == "future" and mv == 1:          # depositing -> outward
                    ok += 1
                elif mv == "pivot":                            # eddy — counted apart
                    ok += 1
            rows.append(Relation(
                name="orbweaver.connective_matches_lightcone_band",
                claim="a block's outbound connective move (+1/-1/0/pivot) matches "
                      "its past/now/future band (past->inward, future->outward)",
                status=Status.UNTESTED,
                observed=f"match {ok}/{len(cflow)} = {ok / len(cflow):.2f}",
                detail="connective classes are drawn at random within each silk "
                       "class here; a real weave would pick by band",
                group="spider-web-composition"))

        # ── eddies advance the storyline: after a pivot+wrap, is the next
        # paragraph shallower (progressed toward Future)? ───────────────
        pivots = [i for i, b in enumerate(blocks) if b.kind == "pivot"]
        if pivots:
            adv = 0
            for i in pivots:
                pd = blocks[i].depth
                nxt = next((blocks[j] for j in range(i + 1, len(blocks))
                            if blocks[j].kind == "paragraph"), None)
                if nxt is not None and nxt.depth <= pd:
                    adv += 1
            rows.append(Relation(
                name="orbweaver.eddy_advances_storyline",
                claim="after a contested-point eddy (pivot + wrap) the next "
                      "paragraph sits at an equal-or-shallower depth",
                status=Status.UNTESTED,
                observed=f"advanced {adv}/{len(pivots)}",
                detail="depth as a proxy for storyline progression",
                group="spider-web-composition"))
        return rows


if __name__ == "__main__":
    m = OrbWeaverMonad()
    ledger = Ledger()
    print(f"BoxKite {'sig ' + str(m.box_kite.signature) + '  ' + str(m.box_kite.n_struts) + ' struts' if m.box_kite else 'UNAVAILABLE: ' + str(m._kite_error)}")

    cases = [
        ("the engine contains sixteen distinct operators that fold into a "
         "single algebra", "auto", "paper"),
        ("she deposited her savings in the reserve account", "auto", "note"),
        ("the volcano formed a mountain of cinder ash lava rock and time "
         "under pressure and heat", "auto", "report"),
        # A/B: the same input on the hand-set scale path
        ("the engine contains sixteen distinct operators that fold into a "
         "single algebra", 2.0, "paper"),
    ]
    for text, scale, genre in cases:
        print(f"\n{'=' * 72}\ninput: {text!r}\n       scale={scale} genre={genre}")
        doc = m.weave(text, scale=scale, genre=genre)
        print(doc.render())
        for r in doc.ledger_rows:
            ledger.add(r)

    print(f"\n{'=' * 72}")
    for i in range(len(ledger)):
        print(ledger.at(i))
    print(f"\n{len(ledger)} relations   {ledger.count(Status.HOLDS)} hold   "
          f"{ledger.count(Status.VIOLATED)} FAULT   "
          f"{ledger.count(Status.UNTESTED)} untested")
    print("\nboxkite_orbweaver_monad.py: run complete.")
