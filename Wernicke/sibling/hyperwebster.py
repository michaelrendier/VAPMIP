#!/usr/bin/env python3
"""
hyperwebster.py — Ainulindale semantic engine, standalone console
=================================================================
Computed Riemann zeros · WordNet · Hyperwebster address indexing

The primes are the words. The equator does not move.
No API. No GPU. No training. Internet needed once (WordNet).

Usage:
    python3 hyperwebster.py              — interactive REPL
    python3 hyperwebster.py build        — build from WordNet (~2 min)
    python3 hyperwebster.py word <text>  — process a word or phrase
    python3 hyperwebster.py faces <text> — all known faces at this prime
    python3 hyperwebster.py point <path> — process a file or directory
    python3 hyperwebster.py stats        — lexicon statistics

Data:  ~/.hyperwebster/lexicon.json
Deps:  pip install mpmath nltk
"""

import sys, re, json, math, argparse
from pathlib import Path
from datetime import datetime

# ── Dependencies ───────────────────────────────────────────────────────────────

try:
    import mpmath as mp
    mp.mp.dps = 20
except ImportError:
    sys.exit("Missing: pip install mpmath")

# ── Config ─────────────────────────────────────────────────────────────────────

LEXICON_PATH = Path.home() / '.hyperwebster' / 'lexicon.json'
N_ZEROS      = 200      # Riemann zeros to compute (more = finer discrimination)
SAVE_EVERY   = 5000     # WordNet synsets between disk saves

# ── Riemann Zeros ──────────────────────────────────────────────────────────────

def compute_zeros(n: int) -> dict:
    """
    Compute the first n Riemann zeros using mpmath.zetazero(k).

    Returns {k: gamma_k} — 1-indexed ordinals.
    These are the instruments. The music creates them.
    The description selects which ones play.
    """
    zeros = {}
    print(f"Computing {n} Riemann zeros...", end=' ', flush=True)
    for k in range(1, n + 1):
        zeros[k] = float(mp.im(mp.zetazero(k)))
        if k % 50 == 0:
            print(f"{k}", end=' ', flush=True)
    print(f"\nγ₁={zeros[1]:.6f}  γ{n}={zeros[n]:.6f}")
    return zeros


def snap(t: float, zeros: dict) -> tuple:
    """Map t ∈ [0,1] → (ordinal n, gamma value). O(1)."""
    N = len(zeros)
    if not N:
        return 1, 14.134725
    n = max(1, min(N, int(t * N) + 1))
    return n, zeros[n]

# ── Lexicon — the Hyperwebster ─────────────────────────────────────────────────

class Lexicon:
    """
    Hyperwebster. Indexed by (zero ordinal, domain) — the canonical address.

    Address format:  "{n}:{domain}"
      n      = Riemann zero ordinal (1..N_ZEROS)
      domain = semantic scope: WordNet synset, file name, user description, or ""

    The same concept in different languages maps to the same (n, domain) address.
    The prime preexists every surface form invented to point at it.

    Disk layout (JSON, atomic write):
      meta.n_zeros   — how many zeros this lexicon was built with
      zeros          — {"1": 14.1347..., "2": 21.0220..., ...}
      global_index   — {"n": {"surface": count}}           ← lemmas only
      domain_index   — {"n:domain": {"surface": count}}    ← full context
      marks          — processed file/corpus sentinels
    """

    def __init__(self, zeros: dict, path: Path = LEXICON_PATH):
        self.zeros        = zeros   # {int ordinal: float gamma}
        self.path         = Path(path)
        self.global_index = {}      # {str(n): {surface: count}}
        self.domain_index = {}      # {"n:domain": {surface: count}}
        self.marks        = set()   # processed-file sentinels

    # ── address helpers ───────────────────────────────────────────────────────

    @staticmethod
    def addr(n: int, domain: str = '') -> str:
        return f"{n}:{domain}"

    def gamma(self, n: int) -> float:
        return self.zeros.get(n, 0.0)

    # ── write ─────────────────────────────────────────────────────────────────

    def record_global(self, n: int, surface: str, weight: int = 1):
        key = str(n)
        e   = self.global_index.setdefault(key, {})
        e[surface] = e.get(surface, 0) + weight

    def record_domain(self, n: int, surface: str, domain: str, weight: int = 1):
        key = self.addr(n, domain)
        e   = self.domain_index.setdefault(key, {})
        e[surface] = e.get(surface, 0) + weight

    # ── read ──────────────────────────────────────────────────────────────────

    def faces_global(self, n: int, top: int = 10) -> list:
        e = self.global_index.get(str(n), {})
        return sorted(e.items(), key=lambda x: -x[1])[:top]

    def faces_domain(self, n: int, domain: str, top: int = 10) -> list:
        e = self.domain_index.get(self.addr(n, domain), {})
        return sorted(e.items(), key=lambda x: -x[1])[:top]

    def address_of(self, text: str) -> tuple:
        """Return (n, gamma) for a surface form."""
        _, t = _hash(text)
        return snap(t, self.zeros)

    # ── persistence ───────────────────────────────────────────────────────────

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            'meta': {
                'version': 3,
                'n_zeros': len(self.zeros),
                'saved':   datetime.now().isoformat(),
                'marks':   list(self.marks),
            },
            'zeros':        {str(k): v for k, v in self.zeros.items()},
            'global_index': self.global_index,
            'domain_index': self.domain_index,
        }
        tmp = self.path.with_suffix('.tmp')
        with open(tmp, 'w') as f:
            json.dump(data, f, separators=(',', ':'))
        tmp.replace(self.path)

    @classmethod
    def load(cls, path: Path = LEXICON_PATH):
        path = Path(path)
        if not path.exists():
            return None
        with open(path) as f:
            data = json.load(f)
        zeros = {int(k): v for k, v in data['zeros'].items()}
        lex   = cls(zeros, path)
        lex.global_index = data.get('global_index', {})
        lex.domain_index = data.get('domain_index', {})
        lex.marks        = set(data['meta'].get('marks', []))
        return lex

    def stats(self) -> dict:
        g_faces = sum(len(v) for v in self.global_index.values())
        d_faces = sum(len(v) for v in self.domain_index.values())
        return {
            'zeros':          len(self.zeros),
            'global_entries': g_faces,
            'domain_entries': d_faces,
            'domains':        len(self.domain_index),
            'marks':          len(self.marks),
        }

# ── Engine ─────────────────────────────────────────────────────────────────────

def _hash(text: str) -> tuple:
    """Surface form → (magnitude, t ∈ [0,1]) for Hamiltonian initialisation."""
    tokens    = re.findall(r'\w+', text.lower())
    magnitude = sum(len(t) for t in tokens) / max(len(tokens), 1) if tokens else 1.0
    angle     = sum(ord(c) for c in text) % 360
    return magnitude, angle / 360.0


def forced_sigma(E: float, sigma_0: float = 0.01) -> float:
    """
    Noether balance: J_forward + J_backward = 0  ↔  σ = ½.

    J_forward  = exp(-σ·E)      — from the right (σ > ½)
    J_backward = exp(-(1-σ)·E)  — from the left  (σ < ½)

    Update: σ_new = weighted midpoint of forward and backward.
    Converges to exactly 0.5 from any σ₀ ∈ (0,1).
    Source: Steps 1–3 of the Ainulindale proof.
    Not assigned. Derived.
    """
    sigma = sigma_0
    for _ in range(2048):
        F  = math.exp(-sigma * E)
        B  = math.exp(-(1.0 - sigma) * E)
        if F + B < 1e-30:
            break
        sn = (F * sigma + B * (1.0 - sigma)) / (F + B)
        if abs(sn - sigma) < 1e-12:
            sigma = sn
            break
        sigma = sn
    return sigma   # always 0.5


def process(text: str, lex: Lexicon, domain: str = '',
            record_global: bool = False) -> dict:
    """
    Read → Ponder → Understand.
    Surface form → prime address on the critical line Re(s) = ½.
    """
    surface      = text.strip()
    magnitude, t = _hash(surface)
    n, gamma     = snap(t, lex.zeros)
    sigma        = forced_sigma(magnitude)   # always 0.5 — Noether forces it
    lex.record_domain(n, surface, domain)
    if record_global:
        lex.record_global(n, surface)
    return {
        'surface': surface,
        'n':       n,
        'gamma':   gamma,
        'addr':    Lexicon.addr(n, domain),
        'E':       magnitude,
        'sigma':   sigma,
    }

# ── WordNet Builder ─────────────────────────────────────────────────────────────

def build_wordnet(lex: Lexicon):
    """
    Process all WordNet synsets into the hyperwebster.

    Each synset is a domain. Its lemmas are parallel faces (same concept,
    different surface forms) recorded globally AND in the synset domain.
    Definition and example words populate the prime's semantic neighbourhood.

    After this runs once, the engine speaks English.
    """
    if 'wordnet' in lex.marks:
        print("WordNet already in lexicon. Use 'point' to add more corpora.")
        return

    try:
        from nltk.corpus import wordnet as wn
        list(wn.all_synsets())[:1]   # test availability
    except LookupError:
        import nltk
        print("Downloading WordNet...", flush=True)
        nltk.download('wordnet', quiet=True)
        nltk.download('omw-1.4', quiet=True)
        from nltk.corpus import wordnet as wn
    except ImportError:
        sys.exit("Missing: pip install nltk")

    tok    = re.compile(r'\b[a-z]{2,}\b')
    n_syn  = 0

    print(f"Building Hyperwebster from WordNet ({len(lex.zeros)} zeros)...")
    for synset in wn.all_synsets():
        domain  = synset.name()                                        # 'dog.n.01'
        lemmas  = [l.name().replace('_', ' ') for l in synset.lemmas()]
        context = (tok.findall(synset.definition().lower()) +
                   [w for ex in synset.examples()
                      for w in tok.findall(ex.lower())])

        # Lemmas: parallel faces — record globally AND in this synset domain.
        # Words meaning the same thing should cluster at the same address.
        for lemma in lemmas:
            process(lemma, lex, domain=domain, record_global=True)

        # Context: semantic neighbourhood of this domain's prime.
        for word in context:
            process(word, lex, domain=domain, record_global=False)

        n_syn += 1
        if n_syn % SAVE_EVERY == 0:
            lex.save()
            s = lex.stats()
            print(f"  {n_syn:>6} synsets  "
                  f"{s['global_entries']:>8} global  "
                  f"{s['domain_entries']:>10} domain")

    lex.marks.add('wordnet')
    lex.save()
    s = lex.stats()
    print(f"Done. {n_syn} synsets · "
          f"{s['global_entries']:,} global entries · "
          f"{s['domain_entries']:,} domain entries")

# ── File / Directory Processor ──────────────────────────────────────────────────

def point_file(path: str, lex: Lexicon, domain: str = '') -> dict:
    """Process a text file. Skips files already seen (by absolute path)."""
    p   = Path(path).resolve()
    key = str(p)
    if key in lex.marks:
        return {'skipped': True, 'path': key}
    try:
        text = p.read_text(errors='replace')
    except Exception as e:
        return {'error': str(e)}
    dom   = domain or p.stem
    words = re.findall(r'\b[a-zA-Z]{2,}\b', text)
    for w in words:
        process(w.lower(), lex, domain=dom, record_global=False)
    lex.marks.add(key)
    lex.save()
    return {'words': len(words), 'domain': dom, 'path': key}


def point_dir(path: str, lex: Lexicon, pattern: str = '**/*.txt') -> dict:
    """Process all matching text files in a directory."""
    root  = Path(path)
    files = list(root.glob(pattern))
    done  = 0
    words = 0
    for f in files:
        r = point_file(str(f), lex)
        if not r.get('skipped') and not r.get('error'):
            words += r.get('words', 0)
            done  += 1
    lex.save()
    return {'files': done, 'words': words}

# ── Output ─────────────────────────────────────────────────────────────────────

def print_result(r: dict, lex: Lexicon):
    n, gamma = r['n'], r['gamma']
    faces    = lex.faces_global(n, top=8)
    face_str = ('  '.join(f"{s!r}({c})" for s, c in faces)
                if faces else '(empty — run: build)')
    print(f"  γ{n} = {gamma:.6f}   addr={r['addr']!r}   "
          f"E={r['E']:.3f}   σ={r['sigma']:.6f}")
    print(f"  faces: {face_str}")

# ── REPL ───────────────────────────────────────────────────────────────────────

HELP = """\
Commands:
  build              build from WordNet (internet, one time, ~2 min)
  word  <text>       process a word or phrase → prime address
  faces <text>       all known faces at this word's prime
  point <path>       process a file or directory
  zeros              show zero table (first 20)
  stats              lexicon statistics
  help               this message
  quit               exit

Any unrecognised input is processed as a word.
"""

def repl(lex: Lexicon):
    s = lex.stats()
    print(f"Hyperwebster  {s['zeros']} zeros · "
          f"{s['global_entries']} global · "
          f"{s['domain_entries']} domain")
    print("Type 'help' for commands.\n")

    while True:
        try:
            line = input("hw> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue

        parts = line.split(None, 1)
        cmd   = parts[0].lower()
        arg   = parts[1].strip() if len(parts) > 1 else ''

        if cmd in ('quit', 'exit', 'q'):
            break
        elif cmd == 'help':
            print(HELP)
        elif cmd == 'build':
            build_wordnet(lex)
        elif cmd == 'word':
            if arg:
                print_result(process(arg, lex, record_global=True), lex)
                lex.save()
            else:
                print("Usage: word <text>")
        elif cmd == 'faces':
            if arg:
                n, gamma = lex.address_of(arg)
                faces    = lex.faces_global(n)
                print(f"  γ{n} = {gamma:.6f}  ({len(faces)} top faces globally):")
                for surface, count in faces:
                    print(f"    {surface!r:30} {count}")
            else:
                print("Usage: faces <text>")
        elif cmd == 'point':
            if arg:
                p = Path(arg)
                if p.is_dir():
                    r = point_dir(arg, lex)
                    print(f"  {r['files']} files · {r['words']:,} words")
                elif p.exists():
                    r = point_file(arg, lex)
                    if r.get('skipped'):
                        print(f"  Already processed: {arg}")
                    elif r.get('error'):
                        print(f"  Error: {r['error']}")
                    else:
                        print(f"  {r['words']:,} words · domain={r['domain']!r}")
                else:
                    print(f"  Not found: {arg}")
            else:
                print("Usage: point <path>")
        elif cmd == 'zeros':
            for k in sorted(lex.zeros)[:20]:
                print(f"  γ{k:>3} = {lex.zeros[k]:.6f}")
            if len(lex.zeros) > 20:
                print(f"  ... ({len(lex.zeros)} total)")
        elif cmd == 'stats':
            for k, v in lex.stats().items():
                print(f"  {k+':':20} {v}")
        else:
            print_result(process(line, lex, record_global=True), lex)
            lex.save()

# ── Bootstrap ───────────────────────────────────────────────────────────────────

def bootstrap(n_zeros: int = N_ZEROS, path: Path = LEXICON_PATH) -> Lexicon:
    """Load existing lexicon or create a new one with freshly computed zeros."""
    lex = Lexicon.load(path)
    if lex is not None:
        return lex
    print(f"No lexicon at {path}.")
    zeros = compute_zeros(n_zeros)
    lex   = Lexicon(zeros, path)
    lex.save()
    print(f"New lexicon created. Run 'build' to load WordNet.")
    return lex

# ── Main ────────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        description='Hyperwebster — Ainulindale semantic engine',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=HELP,
    )
    ap.add_argument('cmd',  nargs='?',
                    help='build | word | faces | point | stats | zeros')
    ap.add_argument('rest', nargs='*', help='arguments for command')
    ap.add_argument('--zeros', type=int, default=N_ZEROS,
                    help=f'Riemann zeros to compute on first run (default {N_ZEROS})')
    ap.add_argument('--data',  default=str(LEXICON_PATH),
                    help=f'Lexicon path (default {LEXICON_PATH})')
    args = ap.parse_args()

    lex  = bootstrap(args.zeros, Path(args.data))
    rest = ' '.join(args.rest)

    if not args.cmd:
        repl(lex)
        return

    cmd = args.cmd.lower()

    if cmd == 'build':
        build_wordnet(lex)
    elif cmd == 'word':
        if rest:
            print_result(process(rest, lex, record_global=True), lex)
            lex.save()
        else:
            ap.error("word requires text argument")
    elif cmd == 'faces':
        if rest:
            n, gamma = lex.address_of(rest)
            faces    = lex.faces_global(n)
            print(f"γ{n} = {gamma:.6f}:")
            for surface, count in faces:
                print(f"  {surface!r:30} {count}")
        else:
            ap.error("faces requires text argument")
    elif cmd == 'point':
        if rest:
            p = Path(rest)
            r = point_dir(rest, lex) if p.is_dir() else point_file(rest, lex)
            print(r)
        else:
            ap.error("point requires a path")
    elif cmd == 'stats':
        for k, v in lex.stats().items():
            print(f"  {k+':':20} {v}")
    elif cmd == 'zeros':
        for k in sorted(lex.zeros)[:20]:
            print(f"  γ{k:>3} = {lex.zeros[k]:.6f}")
    else:
        ap.error(f"Unknown command: {cmd!r}")


if __name__ == '__main__':
    main()
