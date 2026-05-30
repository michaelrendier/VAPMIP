"""
skills/code.py — Code cognition: reading source files into the sedenion field.

:description:
    CodeReader maps Python source AST structure onto the lower-𝕆 operator
    dimensions (e₀..e₇) via the sedenion operator labels::

        e₂  bind       ← import / dependency (bind a name to a module)
        e₃  name       ← assignment / variable definition
        e₄  apply      ← function call
        e₅  abstract   ← function / class definition
        e₆  branch     ← conditional (if / match)
        e₇  iterate    ← loop (for / while / comprehension)
        e₁  negate     ← return / raise (scope exit / inversion)
        e₀  identity   ← module weight (overall complexity norm)

    The resulting 8-float vector encodes source structure density.
    It flows into MindEye.see() → hear() → study() the same way sensor
    data does, but the stimulus is code structure rather than physical signal.

    The strongest zero-divisor coupling channel is e₅(abstract)→e₁₂(compose).
    Source files rich in abstractions (function/class definitions) will push
    strongly through the compose dimension of the cognitive half — exactly the
    Curry-Howard isomorphism expressed algebraically.

    CodeReader does not execute code. It reads only.

    CodeWriter generates code text from the field using the current sedenion
    state as a prior — it does not write to disk.

:classes:
    CodeReader, CodeWriter

:constants:
    OP_TO_DIM, DIM_TO_OP
"""

import ast
import math
import os
from typing import Any, Dict, List, Optional, Tuple

# ── AST node → lower-𝕆 dimension mapping ─────────────────────────────────────

OP_TO_DIM: Dict[str, int] = {
    'identity':   0,
    'negate':     1,
    'bind':       2,
    'name':       3,
    'apply':      4,
    'abstract':   5,
    'branch':     6,
    'iterate':    7,
}

DIM_TO_OP: Dict[int, str] = {v: k for k, v in OP_TO_DIM.items()}

# Map Python AST node types to lower-𝕆 dims
_AST_MAP: Dict[type, int] = {
    ast.Import:          2,  # bind
    ast.ImportFrom:      2,  # bind
    ast.Assign:          3,  # name
    ast.AnnAssign:       3,  # name
    ast.AugAssign:       3,  # name
    ast.NamedExpr:       3,  # name (walrus :=)
    ast.Call:            4,  # apply
    ast.FunctionDef:     5,  # abstract
    ast.AsyncFunctionDef:5,  # abstract
    ast.ClassDef:        5,  # abstract
    ast.Lambda:          5,  # abstract
    ast.If:              6,  # branch
    ast.Match:           6,  # branch
    ast.For:             7,  # iterate
    ast.While:           7,  # iterate
    ast.ListComp:        7,  # iterate
    ast.SetComp:         7,  # iterate
    ast.DictComp:        7,  # iterate
    ast.GeneratorExp:    7,  # iterate
    ast.Return:          1,  # negate
    ast.Raise:           1,  # negate
    ast.Delete:          1,  # negate
    ast.Assert:          1,  # negate (asserts invert assumptions)
}


def _count_ast(source: str) -> Tuple[Dict[int, int], int]:
    """
    Parse Python source and count AST nodes per lower-𝕆 dimension.

    :param source: Python source code string.
    :returns: (counts dict dim→count, total_nodes)
    :rtype: tuple
    """
    counts = {i: 0 for i in range(8)}
    total  = 0
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return counts, 0
    for node in ast.walk(tree):
        dim = _AST_MAP.get(type(node))
        if dim is not None:
            counts[dim] += 1
            total += 1
    # e₀ (identity) = normalised total complexity
    counts[0] = total
    return counts, total


def _counts_to_vec(counts: Dict[int, int], total: int) -> List[float]:
    """
    Normalise AST counts to an 8-float unit vector for MindEye.

    :param counts: Raw dim → count dict from ``_count_ast``.
    :param total: Total node count (normalisation base).
    :returns: 8-float normalised vector.
    :rtype: list
    """
    if total == 0:
        return [0.0] * 8
    # e₀ = file complexity (clamped to 1.0)
    vec  = [min(total / 500.0, 1.0)] + [counts[i] / max(total, 1) for i in range(1, 8)]
    norm = math.sqrt(sum(v * v for v in vec))
    if norm > 0:
        vec = [v / norm for v in vec]
    return vec


# ── CodeReader ────────────────────────────────────────────────────────────────

class CodeReader:
    """
    Reads Python source files and encodes structure into the sedenion field.

    AST node counts map to lower-𝕆 dims → MindEye.see() → hear().
    e₅(abstract)→e₁₂(compose) is the dominant coupling channel; function-rich
    files drive the compose dimension of the cognitive half hardest.

    :param engine: Live ``Engine`` instance.

    :Example:

    .. code-block:: python

        cr = engine.get_code_reader()
        result = cr.read_file('/path/to/skills/study.py')
        print(result['dominant_op'], result['callosum'])

        snippet = cr.read_snippet('def f(x): return x * 2')
        print(snippet['counts'])
    """

    def __init__(self, engine):
        self._engine = engine

    # ── file reading ──────────────────────────────────────────────────────────

    def read_file(self, path: str) -> Dict[str, Any]:
        """
        Read a Python source file and encode its structure into the field.

        :param path: Absolute or relative file path.
        :returns: Dict with keys ``path``, ``counts``, ``dominant_op``,
            ``vec``, ``callosum``, ``heard``, ``error``.
        :rtype: dict
        """
        if not os.path.exists(path):
            return {'path': path, 'error': 'not found', 'counts': {},
                    'dominant_op': '', 'vec': [], 'callosum': 0.0, 'heard': ''}
        try:
            with open(path, 'r', errors='replace') as f:
                source = f.read()
        except Exception as e:
            return {'path': path, 'error': str(e), 'counts': {},
                    'dominant_op': '', 'vec': [], 'callosum': 0.0, 'heard': ''}
        return self._ingest(source, label=os.path.basename(path))

    def read_snippet(self, code: str, label: str = 'snippet') -> Dict[str, Any]:
        """
        Encode a Python code string into the field without touching any file.

        :param code: Python source code.
        :param label: Label for MindEye snapshot.
        :returns: Same structure as ``read_file``.
        :rtype: dict
        """
        return self._ingest(code, label=label)

    def _ingest(self, source: str, label: str) -> Dict[str, Any]:
        """
        Core ingest: count AST → normalise → MindEye → hear.

        :param source: Python source code.
        :param label: MindEye snapshot label.
        :returns: Result dict.
        :rtype: dict
        """
        counts, total = _count_ast(source)
        vec           = _counts_to_vec(counts, total)

        # dominant operator (excluding e₀ identity)
        dom_dim  = max(range(1, 8), key=lambda i: counts[i]) if total > 0 else 0
        dom_op   = DIM_TO_OP.get(dom_dim, 'identity')

        me   = self._engine.get_mind_eye()
        seen = me.see(vec, label=f'code:{label}')

        # hear using the first 256 chars of source (no execution, just text)
        heard = ''
        try:
            preview = source[:256].strip()
            heard   = self._engine.hear(preview)
        except Exception:
            pass

        count_named = {DIM_TO_OP[i]: counts[i] for i in range(8)}
        return {'label': label, 'counts': count_named, 'total': total,
                'dominant_op': dom_op, 'vec': vec,
                'callosum': seen.get('callosum', 0.0), 'heard': heard}

    def scan_repo(self, root: str,
                  extensions: Tuple[str, ...] = ('.py',),
                  max_files: int = 64) -> Dict[str, Any]:
        """
        Scan a directory tree and encode each source file.

        Accumulates per-dim counts across all files, then does a final
        combined MindEye.see() with the aggregate vector.

        :param root: Root directory to walk.
        :param extensions: File extensions to include.
        :param max_files: Maximum number of files to process.
        :returns: Dict with keys ``files``, ``aggregate``, ``dominant_op``,
            ``callosum``, ``heard``.
        :rtype: dict
        """
        agg    = {i: 0 for i in range(8)}
        files  = []
        n      = 0
        for dirpath, _, filenames in os.walk(root):
            for fname in sorted(filenames):
                if not any(fname.endswith(ext) for ext in extensions):
                    continue
                if n >= max_files:
                    break
                fpath  = os.path.join(dirpath, fname)
                result = self.read_file(fpath)
                if not result.get('error'):
                    files.append(result)
                    for i in range(8):
                        agg[i] += result['counts'].get(DIM_TO_OP[i], 0)
                    n += 1
            if n >= max_files:
                break

        total    = sum(agg[i] for i in range(1, 8))
        vec      = _counts_to_vec(agg, total)
        dom_dim  = max(range(1, 8), key=lambda i: agg[i]) if total > 0 else 0
        dom_op   = DIM_TO_OP.get(dom_dim, 'identity')
        me       = self._engine.get_mind_eye()
        seen     = me.see(vec, label=f'code:repo:{os.path.basename(root)}')
        heard    = ''
        try:
            heard = self._engine.hear(
                f'{n} files {dom_op} dominant {total} nodes')
        except Exception:
            pass
        agg_named = {DIM_TO_OP[i]: agg[i] for i in range(8)}
        return {'files': files, 'n_files': n, 'aggregate': agg_named,
                'dominant_op': dom_op, 'vec': vec,
                'callosum': seen.get('callosum', 0.0), 'heard': heard}


# ── CodeWriter ────────────────────────────────────────────────────────────────

class CodeWriter:
    """
    Generates code text from the current field state.

    Does not write to disk. Produces a code string by biasing generation
    toward the ``compose(e₁₂)`` cognitive dim — the strongest zero-divisor
    coupling channel from the lower-𝕆 codebase structure.

    :param engine: Live ``Engine`` instance.

    :Example:

    .. code-block:: python

        cw = engine.get_code_writer()
        # First ingest a file to prime the field
        engine.get_code_reader().read_file('skills/study.py')
        code = cw.generate('write a function that folds a list')
        print(code['text'])
    """

    def __init__(self, engine):
        self._engine = engine

    def generate(self, prompt: str, n_words: int = 64,
                 style: str = 'python') -> Dict[str, Any]:
        """
        Generate a code fragment from the current field state.

        Uses the engine's standard generate() path. The prompt is prefixed
        with a style directive that biases toward functional composition
        (the e₅→e₁₂ dominant coupling channel).

        :param prompt: Natural language description of desired code.
        :param n_words: Maximum token count.
        :param style: Target language hint (default ``'python'``).
        :returns: Dict with keys ``text``, ``prompt``, ``style``.
        :rtype: dict
        """
        full_prompt = f'{style} abstract compose {prompt}'
        result      = self._engine.generate(full_prompt, n_words=n_words)
        text        = result.get('text', '') if isinstance(result, dict) else str(result)
        return {'text': text, 'prompt': prompt, 'style': style}
