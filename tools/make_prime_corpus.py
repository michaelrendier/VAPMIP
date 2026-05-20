#!/usr/bin/env python3
"""
tools/make_prime_corpus.py — Build a prime-addressed Ptolemy corpus.

Maps each word in a corpus to a prime from the sequence [0, 1, 2, 3, 5, 7, ...].
Index 0 → 0   the vacuum prime.   Pre-prime ground, unmarked state (Spencer-Brown).
Index 1 → 1   the mark.           First distinction, multiplicative identity.
Index 2 → 2   first standard prime; all subsequent are primes proper.

The spectral energy of each word uses the prime as the golden-ratio seed:

    seed = fmod(prime * φ, 1.0)     (prime > 0)
    seed = 0.0                       (prime = 0, vacuum)
    E    = D_STAR + seed * (Ω − D_STAR)

The zero index in the field is sequential: word[n] → zero_idx=n.
The prime is the word's irreducible address label.  Composite-index zeros
are left empty — they are the harmonic positions, not concept seats.

The resulting .bin is a valid PTOL v4 state file, loadable by ptolemy directly.

Corpus loaded (in merge order):
  1. WordNet lemmas (NLTK) — ~147k alpha words
  2. NLTK words corpus     — ~237k English words
  3. aspell en dump        — ~91k entries
  4. /usr/share/dict/*     — american-english, british-english, + large variants
  5. /usr/share/hunspell/en_*.dic — en_US, en_GB, en_AU, en_CA
  6. CJK Unified Ideographs (Unicode) — ~27k characters (Basic + Ext-A + Compat)

English union target: ~300k unique alpha words.
CJK target: ~27k characters.
Total: ~328k entries → default N = 350_000.

Usage
-----
    python3 tools/make_prime_corpus.py                        # all sources → ~/.ptolemy/monad_prime.bin
    python3 tools/make_prime_corpus.py -o /path/to/out.bin   # custom output path
    python3 tools/make_prime_corpus.py -f corpus.txt         # plaintext corpus only
    python3 tools/make_prime_corpus.py -n 400000             # custom N
    python3 tools/make_prime_corpus.py --report              # print prime→word table, no write
    python3 tools/make_prime_corpus.py --no-cjk              # skip CJK characters
    python3 tools/make_prime_corpus.py --no-english          # skip English (CJK only)

Author: Cody Michael Allison · Collaborator: Claude Sonnet 4.6
Date:   2026-05-17
"""

import struct
import sys
import os
import argparse
import math
import subprocess

# ── Constants — mirror ptolemy.h exactly ─────────────────────────────────────

PTOL_MAGIC    = b"PTOL"
STATE_VER     = 4
N_DEFAULT     = 350_000
D_STAR        = 0.24600
OMEGA_ZS      = 0.56714329040978387
PHI           = 1.6180339887498948482
L_GROUND_ABS  = 1.888          # |L_GROUND|
EMIT_THRESH   = 3.776          # |L_GROUND| × 2  (emission threshold)
NS_R          = 0              # σ₀  ℝ — vacuum/real stratum
NS_C          = 1              # σ₁  ℂ — language/critical-line stratum
PROSE_WORDNET = 2              # prose_seen flag: WordNet/NLTK origin
PROSE_CJK     = 3              # prose_seen flag: CJK Unicode character

# ── Prime generation ──────────────────────────────────────────────────────────

def _sieve(limit):
    """Eratosthenes sieve; returns list of primes ≤ limit."""
    if limit < 2:
        return []
    is_p = bytearray([1]) * (limit + 1)
    is_p[0] = is_p[1] = 0
    for i in range(2, int(limit ** 0.5) + 1):
        if is_p[i]:
            is_p[i * i :: i] = bytearray(len(is_p[i * i :: i]))
    return [i for i, v in enumerate(is_p) if v]


def prime_list_starting_zero(count):
    """Return the sequence [0, 1, 2, 3, 5, 7, ...] with ``count`` elements.

    Index 0 → 0: void, the unmarked state (Spencer-Brown).
    Index 1 → 1: the mark, first distinction, the unit (multiplicative identity).
    Index 2 → 2: first standard prime; all subsequent elements are primes.

    Both 0 and 1 precede the primes proper.  They are not primes — they are
    the pre-prime ground: the void and the first distinction.

    :param count: Total length of the sequence to return.
    :returns: List ``[0, 1, 2, 3, 5, 7, 11, ...]`` of length ``count``.
    """
    if count <= 0:
        return []
    if count == 1:
        return [0]
    if count == 2:
        return [0, 1]
    n_std = count - 2          # standard primes needed (indices 2..count-1)
    if n_std == 0:
        return [0, 1]
    # Rosser's bound: p_n < n*(ln n + ln ln n + 1.5) for n ≥ 6
    if n_std < 6:
        limit = 20
    else:
        ll = math.log(n_std)
        limit = int(n_std * (ll + math.log(ll) + 2.0)) + 64
    std_primes = []
    while len(std_primes) < n_std:
        std_primes = _sieve(limit)
        limit *= 2
    return [0, 1] + std_primes[:n_std]

# ── Spectral energy from prime ─────────────────────────────────────────────────

def prime_E(prime):
    """Spectral energy coordinate E ∈ [D_STAR, OMEGA_ZS] for an address.

    - ``prime=0``: vacuum  → E = D_STAR           (floor, σ₀ ground)
    - ``prime=1``: mark    → E = D_STAR + (φ−1)·(Ω−D_STAR)  (golden section)
    - ``prime≥2``: concept → E = D_STAR + fmod(prime·φ,1)·(Ω−D_STAR)

    The first distinction (prime=1) lands at the golden section of the
    spectral range — the max-entropy split between vacuum and the Omega ceiling.

    :param prime: Integer prime address (0 = vacuum, 1 = mark, ≥2 = concept).
    :returns: Energy coordinate E as float.
    """
    if prime == 0:
        return D_STAR
    seed = (prime * PHI) % 1.0          # fmod(prime·φ, 1.0) — equidistributed
    return D_STAR + seed * (OMEGA_ZS - D_STAR)

# ── Riemann zero generation — mirrors monad.c:generate_zeros() ───────────────

_EXACT_ZEROS_20 = [
    14.134725, 21.022040, 25.010858, 30.424876, 32.935062,
    37.586178, 40.918719, 43.327073, 48.005151, 49.773832,
    52.970321, 56.446248, 59.347044, 60.831779, 65.112544,
    67.079811, 69.546402, 72.067158, 75.704691, 77.144840,
]


def _generate_zeros(N):
    """Return a list of N Riemann zero imaginary parts (γ_k), k=1..N.

    :param N: Number of Riemann zeros to generate.
    :returns: List of float γ values.
    """
    z = list(_EXACT_ZEROS_20[:min(N, 20)])
    if N <= 20:
        return z
    two_pi = 2.0 * math.pi
    for n in range(21, N + 1):
        t = z[-1] + (z[-1] - z[-2])
        for _ in range(30):
            if t < 2.0:
                t = float(n) * 3.0
            nt  = (t / two_pi) * (math.log(t / two_pi) - 1.0) + 0.875
            dnt = math.log(t / two_pi) / two_pi
            if abs(dnt) < 1e-15:
                break
            dt = (nt - n) / dnt
            t -= dt
            if abs(dt) < 1e-4:
                break
        z.append(t)
    return z

# ── Corpus loading ─────────────────────────────────────────────────────────────

def _load_wordnet():
    """Load unique lowercase alpha lemma names from NLTK WordNet.

    :returns: Set of lowercase alpha strings.
    """
    try:
        from nltk.corpus import wordnet as wn
    except ImportError:
        print("[prime-corpus] NLTK not installed — skipping WordNet")
        return set()
    try:
        wn.synsets("test")
    except Exception:
        import nltk
        nltk.download("wordnet", quiet=True)
        nltk.download("omw-1.4", quiet=True)
    words = set()
    for syn in wn.all_synsets():
        for lemma in syn.lemma_names():
            w = lemma.lower().replace("_", " ")
            # Only keep single-word alpha entries for tokeniser compatibility
            if w.isalpha():
                words.add(w)
    return words


def _load_nltk_words():
    """Load NLTK words corpus (236k English words).

    :returns: Set of lowercase alpha strings.
    """
    try:
        import nltk
        nltk.download("words", quiet=True)
        from nltk.corpus import words as nltk_words
        return set(w.lower() for w in nltk_words.words() if w.isalpha())
    except Exception as e:
        print(f"[prime-corpus] NLTK words corpus unavailable: {e}")
        return set()


def _load_aspell():
    """Load English words from aspell dump.

    :returns: Set of lowercase alpha strings.
    """
    words = set()
    try:
        result = subprocess.run(
            ["aspell", "-d", "en", "dump", "master"],
            capture_output=True, text=True, timeout=30
        )
        for line in result.stdout.splitlines():
            w = line.strip().split("/")[0].lower()
            if w.isalpha():
                words.add(w)
    except Exception:
        pass
    return words


def _load_dict_file(path):
    """Load words from a /usr/share/dict style file (one word per line).

    :param path: Absolute path to the dict file.
    :returns: Set of lowercase alpha strings.
    """
    words = set()
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                w = line.strip().lower()
                if w.isalpha():
                    words.add(w)
    except OSError:
        pass
    return words


def _load_hunspell(path):
    """Load words from a hunspell .dic file (``word/flags`` format).

    :param path: Absolute path to the .dic file.
    :returns: Set of lowercase alpha strings.
    """
    words = set()
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                w = line.strip().split("/")[0].lower()
                if w.isalpha():
                    words.add(w)
    except OSError:
        pass
    return words


def _load_all_english(verbose=True):
    """Load the union of all available English word sources on this system.

    Sources (in load order; all merged into a single de-duplicated set):

    1. WordNet lemmas (NLTK)
    2. NLTK words corpus
    3. aspell ``en`` dump
    4. ``/usr/share/dict/american-english`` and ``british-english``
    5. ``/usr/share/hunspell/en_{US,GB,AU,CA}.dic``

    :param verbose: Print running totals per source when True.
    :returns: Sorted list of unique lowercase alpha English words.
    """
    words = set()

    def _report(tag):
        if verbose:
            print(f"[prime-corpus]   {tag}: {len(words)}")

    if verbose:
        print("[prime-corpus] loading English sources...")

    wn = _load_wordnet()
    words |= wn
    _report(f"WordNet ({len(wn)} alpha lemmas)")

    nw = _load_nltk_words()
    words |= nw
    _report(f"NLTK words ({len(nw)} words)")

    asp = _load_aspell()
    words |= asp
    _report(f"aspell ({len(asp)} entries)")

    for dname in ["american-english", "british-english",
                  "american-english-large", "british-english-large"]:
        path = f"/usr/share/dict/{dname}"
        if os.path.exists(path):
            d = _load_dict_file(path)
            words |= d
            _report(f"/usr/share/dict/{dname} ({len(d)} entries)")

    for code in ["en_US", "en_GB", "en_AU", "en_CA"]:
        path = f"/usr/share/hunspell/{code}.dic"
        if os.path.exists(path):
            h = _load_hunspell(path)
            words |= h
            _report(f"hunspell/{code} ({len(h)} entries)")

    if verbose:
        print(f"[prime-corpus] English union: {len(words)} unique words")

    return sorted(words)


def _load_cjk(verbose=True):
    """Load CJK characters from Unicode standard ranges.

    Ranges included:
    - CJK Unified Ideographs       U+4E00–U+9FFF  (20,902 chars)
    - CJK Unified Ideographs Ext-A U+3400–U+4DBF  ( 6,592 chars)
    - CJK Compatibility Ideographs U+F900–U+FAFF  (  512 chars)

    Each Unicode codepoint is returned as a single-character string.
    This gives ~27k Chinese characters addressable as individual monad entries.

    :param verbose: Print count when True.
    :returns: Sorted list of single-character CJK strings by codepoint.
    """
    chars = []
    ranges = [
        (0x4E00, 0x9FFF),   # CJK Unified Ideographs (Basic)
        (0x3400, 0x4DBF),   # CJK Extension A
        (0xF900, 0xFAFF),   # CJK Compatibility Ideographs
    ]
    seen = set()
    for lo, hi in ranges:
        for cp in range(lo, hi + 1):
            if cp not in seen:
                seen.add(cp)
                chars.append(chr(cp))

    if verbose:
        print(f"[prime-corpus] CJK characters (Unicode ranges): {len(chars)}")

    return chars


def _load_file(path):
    """Load unique lowercase words from a plaintext file.

    :param path: Path to a UTF-8 text file.
    :returns: Sorted list of unique lowercase alpha strings.
    """
    words = set()
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            for tok in line.strip().split():
                w = tok.lower().strip(".,!?;:'\"()[]{}—-")
                if w and w.isalpha():
                    words.add(w)
    return sorted(words)

# ── Binary writer ─────────────────────────────────────────────────────────────

def write_prime_bin(path, entries, N):
    """Write a PTOL v4 state file with prime-addressed vocabulary.

    Binary layout (all little-endian)::

        magic[4]  version[4]  N[4]  vocab_count[4]  A_count[4]  word_count[4]
        emission_threshold[8]  affect[4]
        beta[N × 8]
        age[N × 4]
        vocab_entries × (idx[4] wlen[2] E[8] home[1] gen[1] prose[1] word[wlen])

    :param path:    Output .bin path.
    :param entries: list of ``(word: str, prime: int, zero_idx: int, prose_flag: int)``.
    :param N:       Total number of Riemann zeros in the field.
    """
    ground_beta  = L_GROUND_ABS / N
    vocab_count  = len(entries)
    a_count      = 0
    word_count   = vocab_count

    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

    with open(path, "wb") as f:
        # ── Header ──────────────────────────────────────────────────────────
        f.write(PTOL_MAGIC)
        f.write(struct.pack("<I", STATE_VER))
        f.write(struct.pack("<I", N))
        f.write(struct.pack("<I", vocab_count))
        f.write(struct.pack("<I", a_count))
        f.write(struct.pack("<I", word_count))
        f.write(struct.pack("<d", EMIT_THRESH))
        f.write(struct.pack("<f", 0.0))           # affect = neutral

        # ── Beta — all zeros at ground-state floor ───────────────────────
        for _ in range(N):
            f.write(struct.pack("<d", ground_beta))

        # ── Age — all counters at zero ────────────────────────────────────
        for _ in range(N):
            f.write(struct.pack("<i", 0))

        # ── Vocab entries ─────────────────────────────────────────────────
        for (word, prime, zero_idx, prose_flag) in entries:
            E   = prime_E(prime)
            hs  = NS_R if prime == 0 else NS_C
            gs  = NS_C
            ps  = prose_flag
            raw = word.encode("utf-8")[:255]
            wlen = len(raw)
            f.write(struct.pack("<I", zero_idx))
            f.write(struct.pack("<H", wlen))
            f.write(struct.pack("<d", E))
            f.write(struct.pack("<B", hs))
            f.write(struct.pack("<B", gs))
            f.write(struct.pack("<B", ps))
            f.write(raw)

    size_mb = os.path.getsize(path) / 1024 / 1024
    print(f"[prime-corpus] wrote    {path}")
    print(f"               N        {N}")
    print(f"               words    {vocab_count}")
    print(f"               size     {size_mb:.1f} MB")
    print(f"               prime[0] 0  (__vacuum__  E={D_STAR:.5f})")
    if len(entries) > 1:
        w1, p1, _, _ = entries[1]
        print(f"               prime[1] {p1}  ('{w1}'  E={prime_E(p1):.5f})")
    if len(entries) > 2:
        wl, pl, _, _ = entries[-1]
        print(f"               prime[-1] {pl}  ('{wl}'  E={prime_E(pl):.5f})")

# ── Report ────────────────────────────────────────────────────────────────────

def print_report(entries, zeros):
    """Print a human-readable prime → word mapping table.

    :param entries: List of ``(word, prime, zero_idx, prose_flag)`` tuples.
    :param zeros:   List of Riemann zero imaginary parts.
    """
    print()
    print("┌─────────────────────────────────────────────────────────────────────┐")
    print("│  Prime-addressed corpus — sample mapping                            │")
    print("├──────────┬──────────┬───────────┬────────────┬─────────────────────┤")
    print("│  prime   │  zero_idx│  γ[idx]   │  E         │  word               │")
    print("├──────────┼──────────┼───────────┼────────────┼─────────────────────┤")

    sample_indices = [0, 1, 2, 3, 4, 5, 10, 50, 100, 500, 1000,
                      5000, 10000, 50000, 100000, 200000, 299000]
    for si in sample_indices:
        if si >= len(entries):
            break
        word, prime, zero_idx, _ = entries[si]
        gamma = zeros[zero_idx] if zero_idx < len(zeros) else 0.0
        E     = prime_E(prime)
        tag   = " ← vacuum" if prime == 0 else (" ← mark" if prime == 1 else "")
        print(f"│ {prime:<8d} │ {zero_idx:<8d} │ {gamma:<9.4f} │ {E:<10.5f} │ {word[:19]:<19}{tag}")

    print("└──────────┴──────────┴───────────┴────────────┴─────────────────────┘")
    print()
    print("E-distribution across primes (golden-ratio seed equidistribution):")
    if len(entries) > 1:
        Es = [prime_E(p) for _, p, _, _ in entries[1:min(1001, len(entries))]]
        print(f"  min E = {min(Es):.5f}   max E = {max(Es):.5f}   mean E = {sum(Es)/len(Es):.5f}")
    print()

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    """Entry point: parse arguments, build corpus, write PTOL binary."""
    ap = argparse.ArgumentParser(
        description="Build a prime-addressed Ptolemy corpus (.bin)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("Author")[0].strip()
    )
    ap.add_argument("-o", "--output",
                    default=os.path.expanduser("~/.ptolemy/monad_prime.bin"),
                    help="output .bin path (default ~/.ptolemy/monad_prime.bin)")
    ap.add_argument("-f", "--file", default=None,
                    help="plaintext corpus file — overrides default source loading")
    ap.add_argument("-n", "--zeros", type=int, default=N_DEFAULT,
                    help=f"number of Riemann zeros (default {N_DEFAULT})")
    ap.add_argument("--report", action="store_true",
                    help="print prime→word table and exit without writing")
    ap.add_argument("--no-cjk", action="store_true",
                    help="skip CJK character loading")
    ap.add_argument("--no-english", action="store_true",
                    help="skip English word loading (CJK only)")
    args = ap.parse_args()

    N = args.zeros

    # ── Load corpus ──────────────────────────────────────────────────────────
    if args.file:
        print(f"[prime-corpus] loading corpus from {args.file}...")
        corpus_en  = _load_file(args.file)
        corpus_cjk = []
    else:
        corpus_en  = [] if args.no_english else _load_all_english(verbose=True)
        corpus_cjk = [] if args.no_cjk     else _load_cjk(verbose=True)

    # Build unified word list — English first, then CJK
    all_words = corpus_en + corpus_cjk
    print(f"[prime-corpus] combined corpus: {len(all_words)} unique entries "
          f"({len(corpus_en)} English + {len(corpus_cjk)} CJK)")

    # Prepend vacuum and mark before any corpus words
    words = ["__vacuum__", "__mark__"] + all_words

    # Auto-size N if corpus is larger than default
    if len(words) > N:
        N = len(words) + max(1000, len(words) // 10)
        print(f"[prime-corpus] auto-sizing N to {N} to fit {len(words)} entries")

    # Clamp to args.zeros if user specified explicitly
    if args.zeros != N_DEFAULT and len(words) > args.zeros:
        print(f"[prime-corpus] corpus ({len(words)}) > N ({args.zeros}); truncating")
        words = words[:args.zeros]
        N = args.zeros
    elif len(words) > N_DEFAULT and args.zeros == N_DEFAULT:
        pass  # already auto-sized above

    # ── Generate prime list [0, 1, 2, 3, 5, 7, ...] ──────────────────────
    print(f"[prime-corpus] generating {len(words)} primes...")
    primes = prime_list_starting_zero(len(words))

    # Build (word, prime, zero_idx, prose_flag) tuples
    entries = []
    for i, (w, p) in enumerate(zip(words, primes)):
        if i == 0:
            pf = PROSE_WORDNET  # __vacuum__
        elif i == 1:
            pf = PROSE_WORDNET  # __mark__
        elif i - 2 < len(corpus_en):
            pf = PROSE_WORDNET
        else:
            pf = PROSE_CJK
        entries.append((w, p, i, pf))

    # ── Report ────────────────────────────────────────────────────────────
    if args.report:
        zeros = _generate_zeros(min(N, max(e[2] for e in entries) + 1))
        print_report(entries, zeros)
        return

    # ── Write ─────────────────────────────────────────────────────────────
    print(f"[prime-corpus] writing {args.output}...")
    write_prime_bin(args.output, entries, N)

    # Brief sample
    print()
    print("First five mappings:")
    zeros_sample = _generate_zeros(min(N, 6))
    for i in range(min(5, len(entries))):
        word, prime, zero_idx, _ = entries[i]
        gamma = zeros_sample[zero_idx] if zero_idx < len(zeros_sample) else 0.0
        E     = prime_E(prime)
        tag   = "  ← vacuum (σ₀)" if prime == 0 else (
                "  ← mark (σ₁)"   if prime == 1 else "")
        print(f"  prime={prime:<7d}  zero[{zero_idx}] γ={gamma:.4f}  E={E:.5f}  '{word}'{tag}")

    print()
    print(f"Load with:  ptolemy -c {args.output} -h 'your query'")
    print(f"Inspect:    ptolemy -c {args.output} -w '__vacuum__'")
    print(f"            ptolemy -c {args.output} -w '水'")


if __name__ == "__main__":
    main()
