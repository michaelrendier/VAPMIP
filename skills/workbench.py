"""
skills/workbench.py — Sandboxed experiment layer for the β-field.

:description:
    The Workbench is a delta-on-write sandbox. The base Engine field is
    **read-only** during a workbench session. All experimental writes land
    in a sparse ``WorkbenchDelta`` overlay. The permanent field is never
    touched until the user explicitly calls ``merge()`` — and even then,
    only clean tokens pass the integrity filter.

    Three modes control write permissions:

    * **analysis** — read-only probe. No writes at all. Safe for spectral
      scans, bifurcation parameter sweeps, FieldHealth reports.
    * **draft** — writes go to the delta layer only. Delta is visible to
      generation (shadow β-field) but isolated from the base field.
    * **ingest** — strict intake: ``integrity.scrub()`` strips all
      contaminated tokens before the delta is updated. Use for controlled
      corpus experiments before promoting to the permanent field.

    Source tags track where every word in the delta came from.

:classes:
    WorkbenchDelta, Workbench

:constants:
    SRC_CORPUS, SRC_COMMIT, SRC_WORKBENCH, SRC_SELF, SRC_DATA, SRC_REPLAY
"""

import threading
import time
from typing import Dict, List, Any, Optional

from skills.integrity import scrub_text, FieldHealth, classify_token, TAG_CLEAN

# ── Source provenance tags ─────────────────────────────────────────────────────
SRC_CORPUS    = 'corpus'     # auto-ingested seed / Gutenberg
SRC_COMMIT    = 'commit'     # explicit MonadInterface.commit() call
SRC_WORKBENCH = 'workbench'  # written during a workbench session
SRC_SELF      = 'self'       # Ptolemy's own generated output
SRC_DATA      = 'data'       # numeric / structured data import
SRC_REPLAY    = 'replay'     # memory_log.replay() on reload

# ── Workbench modes ────────────────────────────────────────────────────────────
MODE_ANALYSIS = 'analysis'   # read-only
MODE_DRAFT    = 'draft'      # write to delta, no scrub
MODE_INGEST   = 'ingest'     # write to delta, integrity scrub enforced

_VALID_MODES = {MODE_ANALYSIS, MODE_DRAFT, MODE_INGEST}

# Spectral gap from monad.py (imported lazily to avoid circular import)
_OMEGA_ZS = 0.5671432904097838


class WorkbenchDelta:
    """
    Sparse diff layer over the β-field.

    Stores only the words and edges that the workbench session touched.
    The base Engine field is never modified. ``to_dict()`` serialises
    the delta for logging or later replay.

    :param session_id: Human-readable session identifier.
    :param mode: One of MODE_ANALYSIS / MODE_DRAFT / MODE_INGEST.
    :param source: Default source tag for this session (SRC_* constant).
    """

    def __init__(self, session_id: str, mode: str, source: str = SRC_WORKBENCH):
        self.session_id  = session_id
        self.mode        = mode
        self.source      = source
        self.created_at  = time.time()

        # Sparse overlays: index → delta value
        self._beta_delta: Dict[int, float]        = {}
        # A-matrix edge overlays: (src, dst) → delta weight
        self._a_delta:    Dict[tuple, float]       = {}
        # Retraction masks applied inside the session
        self._mask_delta: Dict[int, Dict[int, float]] = {}
        # New words added during this session (word → assigned index)
        self._new_words:  Dict[str, int]           = {}
        # Source tag per new word
        self._source_tags: Dict[str, str]          = {}
        # Tokens that were scrubbed out (audit trail)
        self._scrub_log:  List[Dict[str, str]]     = []

    def _learn_delta(self, words: List[str],
                     vocab: Dict[str, int],
                     n_base: int,
                     beta_base: List[float],
                     source: str):
        """
        Apply word list to delta overlay. New words get index n_base + offset.
        Does not touch Engine._beta or Engine._vocab.

        :param words: Clean token list.
        :param vocab: Base vocabulary dict (read-only reference).
        :param n_base: Current base vocab size (next available index).
        :param beta_base: Base β list (read-only reference).
        :param source: Source tag for new words.
        """
        beta_mult = 1.08
        edge_fwd  = 0.05
        edge_back = 0.02
        prev_idx  = None

        for w in words:
            if w in vocab:
                idx = vocab[w]
                base_b = beta_base[idx] if idx < len(beta_base) else _OMEGA_ZS
                cur = self._beta_delta.get(idx, base_b)
                self._beta_delta[idx] = min(cur * beta_mult, 1.0)
            else:
                # New word — assign a session-local index
                if w not in self._new_words:
                    self._new_words[w] = n_base + len(self._new_words)
                    self._source_tags[w] = source
                    self._beta_delta[self._new_words[w]] = _OMEGA_ZS

                idx = self._new_words[w]
                cur = self._beta_delta.get(idx, _OMEGA_ZS)
                self._beta_delta[idx] = min(cur * beta_mult, 1.0)

            if prev_idx is not None and prev_idx != idx:
                key_fwd  = (prev_idx, idx)
                key_back = (idx, prev_idx)
                self._a_delta[key_fwd]  = min(
                    self._a_delta.get(key_fwd,  0.0) + edge_fwd,  1.0)
                self._a_delta[key_back] = min(
                    self._a_delta.get(key_back, 0.0) + edge_back, 1.0)
            prev_idx = idx

    def record_scrub(self, original: str, tag: str):
        """
        Add an entry to the scrub audit log.

        :param original: Token that was stripped.
        :param tag: Classification tag that caused the strip.
        """
        self._scrub_log.append({'token': original, 'tag': tag, 'ts': str(time.time())})

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialise the delta for logging or file export.

        :returns: JSON-serialisable dict.
        :rtype: dict
        """
        return {
            'session_id':  self.session_id,
            'mode':        self.mode,
            'source':      self.source,
            'created_at':  self.created_at,
            'new_words':   self._new_words,
            'source_tags': self._source_tags,
            'scrub_log':   self._scrub_log,
            'beta_count':  len(self._beta_delta),
            'edge_count':  len(self._a_delta),
        }

    def stats(self) -> Dict[str, Any]:
        """
        :returns: Quick summary stats for the delta.
        :rtype: dict
        """
        return {
            'session_id':    self.session_id,
            'mode':          self.mode,
            'new_words':     len(self._new_words),
            'beta_updates':  len(self._beta_delta),
            'edge_updates':  len(self._a_delta),
            'scrubbed':      len(self._scrub_log),
        }


class Workbench:
    """
    Sandboxed experiment session over a live Engine.

    The base Engine field is never written. All experiments land in
    ``WorkbenchDelta``. Call ``merge()`` to promote clean delta words
    into the permanent field, or ``discard()`` to throw the session away.

    :param engine: Live ``Engine`` instance (read-only base).
    :param monad: ``MonadInterface`` instance (used for merge writes).
    :param mode: ``MODE_ANALYSIS``, ``MODE_DRAFT``, or ``MODE_INGEST``.
    :param session_id: Optional session name (auto-generated if omitted).

    :Example:

    .. code-block:: python

        wb = monad.workbench(mode='ingest', session_id='exp_001')
        wb.learn('experimental corpus text with numeric junk 0x123 here')
        print(wb.stats())          # shows scrubbed count
        wb.merge()                 # pushes clean words to permanent field
    """

    def __init__(self, engine, monad, mode: str = MODE_DRAFT,
                 session_id: Optional[str] = None):
        if mode not in _VALID_MODES:
            raise ValueError(f'mode must be one of {_VALID_MODES}')
        self._engine    = engine
        self._monad     = monad
        self._mode      = mode
        self._lock      = threading.Lock()
        sid = session_id or f'wb_{int(time.time())}'
        self._delta     = WorkbenchDelta(sid, mode)
        self._merged    = False
        self._discarded = False

    # ── Core experiment API ────────────────────────────────────────────────────

    def learn(self, text: str, source: str = SRC_WORKBENCH) -> Dict[str, Any]:
        """
        Write text into the delta layer (not the permanent field).

        In ``MODE_ANALYSIS`` this is a no-op — returns a read stats dict.
        In ``MODE_INGEST`` the text is scrubbed before learning.

        :param text: Input text.
        :param source: Source tag for new vocabulary added.
        :returns: Stats dict with words_processed and scrubbed_count.
        :rtype: dict
        """
        self._check_active()
        if self._mode == MODE_ANALYSIS:
            return {'mode': MODE_ANALYSIS, 'words_processed': 0, 'scrubbed': 0}

        tokens   = text.split()
        scrubbed = 0

        if self._mode == MODE_INGEST:
            clean_tokens = []
            for t in tokens:
                tag = classify_token(t)
                if tag == TAG_CLEAN:
                    clean_tokens.append(t)
                else:
                    self._delta.record_scrub(t, tag)
                    scrubbed += 1
            tokens = clean_tokens

        with self._lock:
            crank  = self._engine.crank
            self._delta._learn_delta(
                tokens,
                vocab     = crank._vocab,
                n_base    = crank.n,
                beta_base = crank._beta,
                source    = source,
            )

        return {
            'mode':            self._mode,
            'words_processed': len(tokens),
            'scrubbed':        scrubbed,
        }

    def health(self) -> Dict[str, Any]:
        """
        Run a FieldHealth scan on the **base** engine vocabulary.
        Always available regardless of mode.

        :returns: FieldHealth report dict (DTC fault codes + ratios).
        :rtype: dict
        """
        return FieldHealth(self._engine.crank).report()

    def probe(self, word: str) -> Dict[str, Any]:
        """
        Read the effective β score for *word*, checking delta overlay first.

        :param word: Word to probe.
        :returns: Dict with ``base_beta``, ``delta_beta``, ``effective_beta``,
            ``source`` (where it came from).
        :rtype: dict
        """
        w = word.lower().strip()
        crank    = self._engine.crank
        base_idx = crank._vocab.get(w, -1)
        base_b   = crank._beta[base_idx] if base_idx >= 0 else 0.0

        with self._lock:
            if base_idx >= 0:
                delta_b = self._delta._beta_delta.get(base_idx, base_b)
                src     = SRC_CORPUS
            elif w in self._delta._new_words:
                delta_idx = self._delta._new_words[w]
                delta_b   = self._delta._beta_delta.get(delta_idx, 0.0)
                src       = self._delta._source_tags.get(w, SRC_WORKBENCH)
            else:
                delta_b = 0.0
                src     = 'unknown'

        return {
            'word':         w,
            'base_beta':    round(base_b, 6),
            'delta_beta':   round(delta_b, 6),
            'effective':    round(delta_b if delta_b else base_b, 6),
            'source':       src,
            'in_base':      base_idx >= 0,
            'in_delta':     w in self._delta._new_words or base_idx in self._delta._beta_delta,
        }

    def delta_stats(self) -> Dict[str, Any]:
        """
        :returns: Current delta statistics.
        :rtype: dict
        """
        with self._lock:
            return self._delta.stats()

    def merge(self) -> Dict[str, Any]:
        """
        Promote new words from the delta into the permanent β-field via
        ``MonadInterface.commit()``. Only ``TAG_CLEAN`` new words are promoted.
        Base-field β updates are discarded (they were already there).

        :returns: Dict with ``promoted``, ``skipped``, ``session_id``.
        :rtype: dict
        :raises RuntimeError: If already merged or discarded, or in analysis mode.
        """
        self._check_active()
        if self._mode == MODE_ANALYSIS:
            raise RuntimeError('analysis workbench cannot merge — read-only mode')

        with self._lock:
            new_words = list(self._delta._new_words.keys())

        promoted = 0
        skipped  = 0
        if new_words:
            # Build a single commit text from clean new words only
            clean = [w for w in new_words if classify_token(w) == TAG_CLEAN]
            skipped = len(new_words) - len(clean)
            if clean:
                commit_text = ' '.join(clean)
                self._monad.commit(
                    commit_text,
                    weight=1.2,
                    reason=f'workbench merge: {self._delta.session_id}',
                )
                promoted = len(clean)

        self._merged = True
        return {
            'session_id': self._delta.session_id,
            'promoted':   promoted,
            'skipped':    skipped,
        }

    def discard(self) -> Dict[str, Any]:
        """
        Throw away this workbench session. Nothing is written to the field.

        :returns: Session stats at the point of discard.
        :rtype: dict
        """
        self._check_active()
        stats = self._delta.stats()
        self._discarded = True
        return {'discarded': True, **stats}

    def export_log(self) -> Dict[str, Any]:
        """
        Export full delta log (session metadata + scrub audit trail).

        :returns: Delta serialisation dict.
        :rtype: dict
        """
        with self._lock:
            return self._delta.to_dict()

    # ── Private helpers ────────────────────────────────────────────────────────

    def _check_active(self):
        if self._merged:
            raise RuntimeError('workbench already merged')
        if self._discarded:
            raise RuntimeError('workbench already discarded')

    @property
    def mode(self) -> str:
        """Current mode string."""
        return self._mode

    @property
    def session_id(self) -> str:
        """Session identifier."""
        return self._delta.session_id
