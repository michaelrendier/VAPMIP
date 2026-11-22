"""
math_isolate.py — separate mathematical ENGLISH from mathematical NOTATION
========================================================================

The granular .bin vocabularies ingested a maths corpus wholesale: LaTeX
fragments, DOIs, ISBNs, URLs, and raw mojibake all landed as "words".  The old
fix (_clean_word / _JUNK_RE in PtolC/ptol_layer.py) just DELETES anything that
looks non-English — lossy, and it cannot distinguish

    "the Möbius function"        <- WORD    (mathematical English — keep)
    "\\mu \\ast \\mathbf 1 = \\varepsilon"  <- FORMULA  (notation — isolate as ONE type)

This module classifies every token into a small closed set and, for ORDERED
text, merges adjacent notation tokens into a single FORMULA span so the English
layer only ever sees the type-token  ⟨formula⟩  (raw kept in a side table,
keyed by hash — retrievable, not vocabulary).

    WORD     clean English / a real loanword or proper noun      -> vocabulary
    FORMULA  a symbolic-maths fragment (LaTeX, operators, sub/sup) -> ⟨formula⟩
    NUMBER   a bare numeral / decimal                             -> ⟨number⟩
    GREEK    a Greek-script term (πρῶτος, ζ)                       -> ⟨greek⟩ (or keep)
    REF      DOI / ISBN / ISSN / arXiv id / URL / wiki oldid      -> ⟨ref⟩  (side table)
    GARBAGE  control chars, replacement chars, byte soup          -> dropped

Maths CODE is self-referential (x on both sides of =, f defined by f, reused
index names); a FORMULA span is exactly a maximal run with no English finite
verb and high operator/brace density.  `segment()` finds those runs.
"""
from __future__ import annotations
import hashlib
import re
import unicodedata
from typing import List, Tuple

# The equation .bin is not a resource the monad "scales in" — the marker below
# is a PERMANENT primitive of the lexicon (like punctuation, like 0 and 1).
MATHS_NOTATION = "[maths notation]"

# ── token-level patterns ────────────────────────────────────────────────────
_CTRL       = re.compile(r'[\x00-\x08\x0b-\x1f\x7f]')
_REPL       = '�'
_LATEX_CMD  = re.compile(r'\\[A-Za-z]+|\\[{}$&#_%^~]|\\\\')
_BRACE_SUP  = re.compile(r'[{}^_]|\$')
_OPERATORS  = {'=', '+', '<', '>', '±', '×', '÷', '·', '⋅', '≤', '≥', '≠',
               '≈', '≡', '⇒', '⇔', '→', '↦', '∑', '∏', '∫', '∂', '∇', '√',
               '∈', '∉', '⊂', '⊆', '∪', '∩', '∀', '∃', '∞', '⊕', '⊗', '∘', '≅'}
_MATH_PUNCT = set('=+*/^~|!<>-')            # notation when near a formula run
_EXPR       = re.compile(r'^[A-Za-z0-9()]+[/*^!|][A-Za-z0-9()/*^!|.-]*$|^-\d')
_VAR_SUB    = re.compile(r'^[A-Za-z][A-Za-z]?[_^]?\d|^\d[A-Za-z]|[A-Za-z]_\d|_\{|\}\^')
_DOI        = re.compile(r'^10\.\d{4,9}/')
_ISBN       = re.compile(r'^97[89][\d-]{10,}$|^\d{9}[\dxX]$')
_ISSN       = re.compile(r'^\d{4}-\d{3}[\dxX]$')
_ARXIV      = re.compile(r'^\d{4}\.\d{4,5}(v\d+)?$|^[a-z-]+/\d{7}$')
_URL        = re.compile(r'^(https?|ftp)://|^www\.|wikipedia\.org|oldid=')
_BIBCODE    = re.compile(r'^\d{4}[a-z]{2,}\.\.', re.I)
_DECADE_ORD = re.compile(r'^(mid-)?\d{1,4}(st|nd|rd|th|s)$', re.I)     # 1970s, 18th, mid-19th
_PURE_NUM   = re.compile(r'^-?\d{1,3}(,\d{3})*(\.\d+)?$|^-?\d+\.\d+$|^-?\d+$')
_WORDLIKE   = re.compile(r"^[A-Za-z][A-Za-z'’-]*[A-Za-z]$|^[A-Za-z]$")


def _greek(tok: str) -> bool:
    return any('GREEK' in unicodedata.name(c, '') for c in tok) and \
           all(unicodedata.category(c)[0] in 'LM' or c in "'’-" for c in tok)


def classify(tok: str) -> str:
    if not tok:
        return 'GARBAGE'
    if _CTRL.search(tok) or _REPL in tok:
        return 'GARBAGE'
    low = tok.lower()
    if _URL.search(low) or _DOI.match(low) or _ISBN.match(tok) or _ISSN.match(low) \
       or _ARXIV.match(low) or _BIBCODE.match(tok):
        return 'REF'
    if _DECADE_ORD.match(tok):
        return 'WORD'                                   # English time expression
    if _PURE_NUM.match(tok):
        return 'NUMBER'
    if _LATEX_CMD.search(tok) or _BRACE_SUP.search(tok):
        return 'FORMULA'
    if tok in _OPERATORS or (len(tok) <= 3 and any(c in _OPERATORS for c in tok)):
        return 'FORMULA'
    if _VAR_SUB.search(tok):
        return 'FORMULA'
    if _EXPR.match(tok) and any(c.isalnum() for c in tok):
        return 'FORMULA'
    # script / charset
    letters = [c for c in tok if c.isalpha()]
    if letters and _greek(tok):
        return 'GREEK'
    non_latin = sum(1 for c in letters if ord(c) > 0x250)
    if letters and non_latin / len(letters) > 0.5:
        return 'GARBAGE'                                # CJK / cyrillic soup / byte runs
    nonalnum = sum(1 for c in tok if not (c.isalnum() or c in "'’-"))
    if len(tok) and nonalnum / len(tok) > 0.34:
        return 'GARBAGE'
    if _WORDLIKE.match(tok) and sum(c.isalpha() for c in tok) >= 2:
        return 'WORD'
    if len(tok) == 1 and tok.isalpha():
        return 'WORD'
    return 'GARBAGE'


# ── span-level: merge adjacent notation into one FORMULA ────────────────────
_NOTATION = {'FORMULA', 'NUMBER'}
_FORMULA_TABLE: dict = {}


def _formula_id(raw: str) -> str:
    h = hashlib.blake2s(raw.encode('utf-8', 'replace'), digest_size=6).hexdigest()
    _FORMULA_TABLE[h] = raw
    return f'⟨formula:{h}⟩'


def segment(text: str) -> List[Tuple[str, str]]:
    """
    Ordered text -> list of (kind, piece).  Runs of notation (with the little
    connective words 'where/for/if/and' that live inside display maths) collapse
    to one ('FORMULA', '⟨formula:hash⟩'); prose stays word by word.
    """
    toks = text.split()
    out: List[Tuple[str, str]] = []
    buf: List[str] = []
    trail: List[str] = []

    GLUE = {'where', 'for', 'if', 'and', 'or', 'with', 'when'}

    def flush():
        # drop trailing English glue that no notation followed
        while buf and buf[-1].lower() in GLUE:
            trail.append(buf.pop())
        if not buf:
            pass
        elif sum(1 for t in buf if classify(t) == 'FORMULA') >= 1 and len(''.join(buf)) > 1:
            out.append(('FORMULA', _formula_id(' '.join(buf))))
        else:
            for t in buf:
                out.append((classify(t), t))
        buf.clear()
        while trail:
            w = trail.pop()
            out.append((classify(w), w))

    def in_run():
        return any(classify(b) == 'FORMULA' for b in buf)

    for t in toks:
        c = classify(t)
        single = len(t) == 1 and (t.isalpha() or t in _MATH_PUNCT)
        if c in _NOTATION:
            buf.append(t)
        elif buf and in_run() and (single or t in _MATH_PUNCT):
            buf.append(t)                               # variable/operator inside maths
        elif buf and in_run() and t.lower() in GLUE:
            buf.append(t)                               # display-maths connective
        else:
            flush()
            out.append((c, t))
    flush()
    return out


# ── resanitize an existing bag-of-words .bin ───────────────────────────────
def resanitize(words: List[str]) -> dict:
    from collections import Counter
    tag = Counter()
    kept, formulas, refs, numbers, greek = [], [], [], [], []
    for w in words:
        c = classify(w) if isinstance(w, str) else 'GARBAGE'
        tag[c] += 1
        if c == 'WORD':
            kept.append(w)
        elif c == 'FORMULA':
            formulas.append(w)
        elif c == 'REF':
            refs.append(w)
        elif c == 'NUMBER':
            numbers.append(w)
        elif c == 'GREEK':
            greek.append(w)
    return {
        'counts': dict(tag),
        'clean_vocab': kept,                 # the only tokens that stay as words
        'formula_table': formulas,           # -> collapse to one ⟨formula⟩ type
        'ref_table': refs,                   # -> one ⟨ref⟩ type / side file
        'number_table': numbers,             # -> one ⟨number⟩ type
        'greek_table': greek,
    }


# ── reading LaTeX: the equation bin's own granularity ──────────────────────
# A formula is NOT vocabulary — it is a structured stream.  latex_tokenize()
# lexes it into the small closed alphabet the equation .bin learns on:
#   control words  \frac \sum \mathbb \begin{aligned} ...
#   specials       { } ^ _ & 
#   operators      + - = < > / | ! ( ) [ ] \,  (and the unicode maths ops)
#   identifiers    one letter each (math mode: "xy" = x · y)
#   numbers        a digit run
_LX = re.compile(r"""
    \\begin\{[^}]*\} | \\end\{[^}]*\}          # environments
  | \\[A-Za-z]+ | \\.                          # control word / control symbol
  | \{ | \} | \^ | _ | & | \$                 # specials
  | \d+(?:\.\d+)?                              # number
  | [A-Za-z]                                   # one identifier letter
  | [-+=<>/|!()\[\].,;:*]                      # ascii operators / delimiters
  | [^\s\w\\{}^_&$]                            # any other single (unicode op)
""", re.X)


def latex_tokenize(s: str):
    """Formula string -> list of structural LaTeX tokens (the equation alphabet)."""
    if s.startswith('⟨formula:'):
        s = _FORMULA_TABLE.get(s[9:-1], s)
    return _LX.findall(s)


def read_equation(raw: str) -> dict:
    """The equation bin's feature read of one formula."""
    toks = latex_tokenize(raw)
    depth = mx = 0
    for t in toks:
        if t == '{':
            depth += 1; mx = max(mx, depth)
        elif t == '}':
            depth = max(0, depth - 1)
    cmds = [t for t in toks if t.startswith('\\')]
    envs = [t for t in toks if t.startswith('\\begin')]
    ids  = sorted({t for t in toks if len(t) == 1 and t.isalpha()})
    ops  = [t for t in toks if t in _OPERATORS or t in set('+-=<>/|!*')]
    return {
        'tokens': toks, 'n_tokens': len(toks),
        'commands': sorted(set(cmds)), 'environments': sorted(set(envs)),
        'brace_depth': mx, 'identifiers': ids, 'n_operators': len(ops),
        'has_sub': '_' in toks, 'has_sup': '^' in toks,
        'self_referent': len(ids) > 0 and toks.count('=') >= 1
                         and any(toks.count(i) >= 2 for i in ids),
    }


# ── split a maths corpus: English prose  +  [maths notation] blocks ────────
def split_corpus(text: str):
    """
    text -> (english, blocks)
      english : the prose with each formula replaced by the literal marker
                '[maths notation]'  (the words .bin never sees notation)
      blocks  : list of {raw, tokens}  for the equation .bin
    Works line by line; a run of NOTATION tokens (segment()) becomes one block.
    """
    eng_lines, blocks = [], []
    for line in text.splitlines():
        pieces = segment(line)
        out = []
        for kind, piece in pieces:
            if kind == 'FORMULA':
                out.append('[maths notation]')
                blocks.append({'raw': _FORMULA_TABLE.get(piece[9:-1], piece)
                               if piece.startswith('⟨formula:') else piece})
            elif kind in ('WORD', 'NUMBER'):
                out.append(piece)
            elif kind == 'GREEK':
                out.append(piece)
            # REF, GARBAGE dropped from prose
        if out:
            eng_lines.append(' '.join(out))
    for b in blocks:
        b['tokens'] = latex_tokenize(b['raw'])
    return '\n'.join(eng_lines), blocks


def build_equation_vocab(formula_blocks) -> dict:
    """LaTeX-token frequency over a set of formula strings/blocks — the
    equation .bin's alphabet.  Always part of the lexicon; no scale needed."""
    from collections import Counter
    cmd, spec, op, ident, num, env = Counter(), Counter(), Counter(), Counter(), Counter(), Counter()
    n_blocks = 0
    for b in formula_blocks:
        raw = b['raw'] if isinstance(b, dict) else b
        n_blocks += 1
        for t in latex_tokenize(raw):
            if t.startswith('\\begin') or t.startswith('\\end'):
                env[t] += 1
            elif t.startswith('\\'):
                cmd[t] += 1
            elif t in '{}^_&$':
                spec[t] += 1
            elif t in _OPERATORS or t in set('+-=<>/|!*()[].,;:'):
                op[t] += 1
            elif len(t) == 1 and t.isalpha():
                ident[t] += 1
            elif t[:1].isdigit():
                num[t] += 1
    return {
        'marker': MATHS_NOTATION, 'n_blocks': n_blocks,
        'commands': dict(cmd.most_common()), 'environments': dict(env.most_common()),
        'specials': dict(spec), 'operators': dict(op.most_common()),
        'identifiers': dict(ident.most_common()), 'numbers_seen': len(num),
        'alphabet_size': len(cmd) + len(spec) + len(op) + len(ident) + len(env),
    }


def resanitize_bin(in_path: str, out_dir: str | None = None) -> dict:
    """Split a polluted maths .bin into  <name>.words.bin  (clean English, the
    normal lexicon)  +  <name>.equation.bin  (the always-on LaTeX sublayer)  +
    <name>.refs.txt  (bibliography, out of the lexicon)."""
    import pickle, os
    import numpy as np
    d = pickle.load(open(in_path, 'rb'))
    words = list(d['words'])
    N = len(words)
    par = {k: d[k] for k in d if isinstance(d[k], list) and len(d[k]) == N}
    cls = [classify(w) if isinstance(w, str) else 'GARBAGE' for w in words]
    keep = [i for i, c in enumerate(cls) if c == 'WORD']
    types = {'FORMULA': '[maths notation]', 'NUMBER': '⟨number⟩',
             'REF': '⟨ref⟩', 'GREEK': '⟨greek⟩'}

    def slice_par(idxs):
        return {k: [v[i] for i in idxs] for k, v in par.items()}

    wb = {'version': d.get('version', '') + '+words', 'n': len(keep)}
    wb.update(slice_par(keep))
    # append the permanent type-tokens with a mean row where a matrix exists
    ekey = next((k for k in ('E', 'beta') if k in par), None)
    for c, name in types.items():
        rows = [i for i, cc in enumerate(cls) if cc == c]
        if not rows:
            continue
        wb['words'].append(name)
        for k, v in par.items():
            if rows and isinstance(v[rows[0]], list):
                wb[k].append(np.mean([v[i] for i in rows], axis=0).tolist())
            else:
                wb[k].append(0)
    wb['vocab'] = {w: i for i, w in enumerate(wb['words'])}
    wb['n'] = len(wb['words'])

    formula_frags = [words[i] for i, c in enumerate(cls) if c == 'FORMULA']
    eq = build_equation_vocab(formula_frags)
    eq['version'] = d.get('version', '') + '+equation'
    eq['always_in_lexicon'] = True

    out_dir = out_dir or os.path.dirname(in_path)
    stem = os.path.splitext(os.path.basename(in_path))[0]
    p_w = os.path.join(out_dir, stem + '.words.bin')
    p_e = os.path.join(out_dir, stem + '.equation.bin')
    p_r = os.path.join(out_dir, stem + '.refs.txt')
    pickle.dump(wb, open(p_w, 'wb'))
    pickle.dump(eq, open(p_e, 'wb'))
    open(p_r, 'w').write('\n'.join(words[i] for i, c in enumerate(cls) if c == 'REF'))
    from collections import Counter
    return {'in': in_path, 'counts': dict(Counter(cls)),
            'words_bin': p_w, 'words_kept': wb['n'],
            'equation_bin': p_e, 'equation_alphabet': eq['alphabet_size'],
            'refs': p_r}


if __name__ == '__main__':
    import pickle, sys, random
    path = sys.argv[1] if len(sys.argv) > 1 else \
        '/home/rendier/Projects/ThePlace/PtolemyDesktop/Archimedes/monad_mathematics.bin'
    if len(sys.argv) > 2 and sys.argv[1] == '--resanitize':
        import json
        print(json.dumps(resanitize_bin(sys.argv[2]), indent=1)); sys.exit()
    d = pickle.load(open(path, 'rb'))
    words = d['words'] if isinstance(d, dict) and 'words' in d else d
    r = resanitize(list(words))
    tot = sum(r['counts'].values())
    print(f"{path}\n{tot} tokens:")
    for k, v in sorted(r['counts'].items(), key=lambda x: -x[1]):
        print(f"  {k:8} {v:7,}  {100*v/tot:5.1f}%")
    random.seed(2)
    print("\nWORD sample   :", random.sample(r['clean_vocab'], 20))
    print("FORMULA sample:", random.sample(r['formula_table'], 12))
    print("REF sample    :", r['ref_table'][:6])
    print("\n── reading LaTeX (equation bin granularity) ──")
    for raw in (r"\frac{1}{2}\sum_{n=1}^{\infty}\frac{1}{n^{2}}=\frac{\pi^{2}}{6}",
                r"\begin{aligned}50&=2\times5^{2}\end{aligned}",
                r"z=we^{w}"):
        e = read_equation(raw)
        print(f"  {raw}")
        print(f"    tokens({e['n_tokens']}): {e['tokens']}")
        print(f"    commands={e['commands']}  depth={e['brace_depth']}  "
              f"ids={e['identifiers']}  self_referent={e['self_referent']}")

    para = (r"By the prime number theorem, \pi(x) \sim x/\log x. "
            r"We write n = p_{1}^{a_{1}} \cdots p_{k}^{a_{k}} for the factorisation, "
            r"and the number of divisors is \prod (a_{i}+1). This is elementary.")
    eng, blocks = split_corpus(para)
    print("\n── split_corpus ──\n  ENGLISH:", eng)
    for b in blocks:
        print("  BLOCK:", b["raw"], "->", b["tokens"])
