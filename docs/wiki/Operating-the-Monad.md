# Operating the Monad

*Ptolemy Monad Engine — `ptolemy-monad` C binary, v1.218+*

---

The monad is the engine core. One binary. No dependencies beyond libc, libm, and pthreads. No transformers, no autoregression, no external model weights. It learns English by reading text and fires words by Noether current propagation through a sedenion β-field.

This page covers everything you need to operate it: install, all CLI flags, teaching, generation, diagnostics, and how to set it loose overnight.

For the mathematical architecture behind why it works, read [Tuning-the-Engine.md](Tuning-the-Engine.md).

---

## The Three Constants

These three numbers govern everything. You will see them in every report.

| Constant | Value | Meaning |
|----------|-------|---------|
| `OMEGA_ZS` | 0.56714 | Lambert W(1). BAO spectral gap. The engine's idle RPM. |
| `GAP` | 0.000707 | Yang-Mills mass gap. Semantic vacuum floor. No word's β ever falls below this. |
| `D_STAR` | 0.246 | Fermat proximity threshold. Zero-divisor danger zone in sedenion space. |

---

## Installation

### Prerequisites

```bash
# Build tools only
sudo apt install gcc make
```

No other dependencies. The binary is fully self-contained.

### Build

```bash
cd ~/Projects/Ptol/SMMIP
make
```

### Install system-wide (graphical sudo)

```bash
make install
# Polkit dialog will appear — authenticate to install to /usr/local/bin/ptolemy-monad
```

Or manually with an absolute path (pkexec drops the working directory):

```bash
pkexec install -m 755 /full/path/to/ptolemy-monad /usr/local/bin/ptolemy-monad
```

### Verify

```bash
ptolemy-monad --help
```

---

## CLI Reference

All flags are processed **left to right**. Order matters: `--load-bin` before `--learn-file` before `--save-bin`. You can chain multiple operations in one invocation.

### State Management

```bash
# Save the current field to a .ptol binary
ptolemy-monad --save-bin ~/.ptolemy/monad.ptol

# Load a previously saved field
ptolemy-monad --load-bin ~/.ptolemy/monad.ptol

# Load, learn a file, and immediately save — the typical loop step
ptolemy-monad --load-bin ~/.ptolemy/monad.ptol \
              --learn-file book.txt \
              --save-bin   ~/.ptolemy/monad.ptol
```

The `.ptol` format is v3 binary. It is **not** compatible with the Python pickle `.bin` files used by `monad.py`. They are separate engines with separate state files.

### Teaching

```bash
# Learn from a local text file
ptolemy-monad --learn-file /path/to/book.txt

# Fetch a plain HTTP URL and learn it (HTTP only — no TLS)
ptolemy-monad --url http://some.mirror/text.txt

# Interactive teaching from stdin (Ctrl-D to finish)
ptolemy-monad --teach

# Pipe text in
cat moby-dick.txt | ptolemy-monad --teach
```

### Generation

```bash
# Generate 32 words from a seed phrase (default)
ptolemy-monad --generate "the sea at midnight"

# Generate a specific count
ptolemy-monad --generate "consciousness" 64

# Generate with a loaded field (much better output)
ptolemy-monad --load-bin ~/.ptolemy/monad.ptol \
              --generate "the structure of language" 50
```

Generation uses the full engine: cam_encode → J_pos/J_neg → A-matrix propagation → σ-candidates → Three-Face Wankel → no-repeat buffer. It is not autoregression. Each word is independently scored against the sedenion field.

### Word Query

```bash
# Print the sedenion coordinates and field state for a specific word
ptolemy-monad --load-bin ~/.ptolemy/monad.ptol --query "language"
```

Output shows: sedenion vector (16 components), β (charge amplitude), E (Riemann energy), age, sedenion dimension assignment, and all A-matrix neighbours with edge weights.

### Hamiltonian Report

```bash
ptolemy-monad --load-bin ~/.ptolemy/monad.ptol --report
```

This is the engine's "My Location" function. Output includes:

- **Vocabulary count** — total words in the field
- **BAO mean vs OMEGA_ZS** — how close the field is to operating temperature
- **Field health** — 1.0 = perfect BAO convergence, 0.0 = DTC P0087 fault
- **DTC P0087 count** — number of times BAO diverged beyond ±0.25 from OMEGA_ZS
- **SEGFAULT count** — zero-divisor encounters corrected by Fermat rotation
- **UNS coordinates** — Universal Native Space: which sedenion dimensions dominate
- **Top activated words** — highest β×E² words in the field

### TCP Teaching Daemon

```bash
# Start daemon on default port 7297, teaching from any TCP connection
ptolemy-monad --load-bin ~/.ptolemy/monad.ptol --daemon 7297

# Different port
ptolemy-monad --daemon 9000

# Send text to the daemon from another terminal
echo "the sky is full of stars" | nc localhost 7297
# Response: +N (N = words learned from that chunk)
```

The daemon keeps the entire field in memory. There is no auto-save — if you kill the daemon the unsaved state is lost. Use the daemon when you want to feed text from multiple sources simultaneously. Combine with a cron job or signal handler to save periodically.

---

## Understanding the Report

### UNS Coordinates

The 16 sedenion dimensions each correspond to a semantic operator:

| Dim | Operator | What it means when high |
|-----|----------|------------------------|
| e0 | identity | Self-reference, identity statements |
| e1 | negate | Negation, opposition, NOT operations |
| e2 | bind | Variable binding, assignment, reference |
| e3 | name | Nouns, labels, named things |
| e4 | apply | Verbs, function application, actions |
| e5 | abstract | Adjectives, descriptors, abstraction |
| e6 | branch | Conditionals, decision points, IF/THEN |
| e7 | iterate | Repetition, loops, temporal sequence |
| e8 | recurse | Self-referential structure, recursion |
| e9 | allocate | Fetching, loading, resource acquisition |
| e10 | query | Searching, questioning, introspection |
| e11 | dereference | Pronoun resolution, pointer following |
| e12 | compose | Function composition, piping, chaining |
| e13 | parallelize | Threading, concurrency, simultaneity |
| e14 | interrupt | Exceptions, signals, breaking flow |
| e15 | emit | Output, speaking, writing, printing |

A healthy English field will show moderate activation across e3 (nouns), e4 (verbs), e5 (descriptors), e9 (fetch/get), and e15 (emit/say). Extreme concentration in any single dimension indicates a narrow corpus.

### BAO and Field Health

The **BAO mean** is the mean of `β × E²` across the vocabulary. It should converge to `OMEGA_ZS = 0.56714`. This is the Lambert W fixed point — the semantic equivalent of the Baryon Acoustic Oscillation scale, the lowest non-zero eigenvalue of the field's Laplacian.

- **BAO near OMEGA_ZS, health near 1.0** → engine is at operating temperature
- **BAO below OMEGA_ZS, DTC P0087 incrementing** → field is too sparse, needs more ingest
- **BAO above OMEGA_ZS** → field is oversaturated, redundant corpus

### DTC Codes

| Code | Name | Meaning |
|------|------|---------|
| P0087 | BAO Fault | β×E² mean diverged >±0.25 from OMEGA_ZS |
| SEGFAULT | Zero-Divisor Encounter | Fermat scan detected proximity to sedenion zero-divisor; rotation applied |

These are not errors — they are diagnostic flags. A few P0087 faults during initial corpus ingest is normal. Persistent high counts mean the corpus needs more variety.

---

## Teaching English Overnight

The `tools/teach_english.sh` script runs an indefinite ingest loop against classic English literature from Project Gutenberg. It downloads and caches each book locally, feeds it to the monad, saves state after every book, and loops continuously.

### Quick start

```bash
# Make sure you have curl
which curl

# Run the overnight session (leave this terminal open, or use screen/tmux)
cd ~/Projects/Ptol/SMMIP
bash tools/teach_english.sh
```

State is saved to `~/.ptolemy/monad-english.ptol` after every book.

### In a detached session

```bash
# Using screen
screen -S ptolemy-teach
bash tools/teach_english.sh
# Ctrl-A D to detach. Re-attach tomorrow: screen -r ptolemy-teach

# Using tmux
tmux new -s ptolemy-teach
bash tools/teach_english.sh
# Ctrl-B D to detach. Re-attach: tmux attach -t ptolemy-teach

# Using nohup (no terminal reattach)
nohup bash tools/teach_english.sh > /tmp/ptol-teach.log 2>&1 &
echo "PID: $!"
# Check progress: tail -f /tmp/ptol-teach.log
```

### What it ingests

22 canonical English texts on first pass, cycling indefinitely:

- KJV Bible (vocabulary breadth, poetic register)
- Complete Shakespeare (all registers, archaic and modern)
- Moby Dick, Pride and Prejudice, Crime and Punishment, War and Peace (novel register)
- Sherlock Holmes (deductive reasoning structure)
- Huck Finn (vernacular, dialogue-heavy)
- Plato's Republic, Hume's Enquiry, Machiavelli's Prince (philosophical register)
- Alice in Wonderland, Dorian Gray, Frankenstein (literary range)
- Franklin's Autobiography, Tom Sawyer, Ulysses (American/modernist)

The corpus is deliberately diverse. Overtraining on a single register produces a field that only speaks in that voice.

### Checking progress overnight

```bash
# Quick health check from another terminal
ptolemy-monad --load-bin ~/.ptolemy/monad-english.ptol --report

# Watch it grow (if using nohup log)
tail -50 /tmp/ptol-teach.log

# Live query
ptolemy-monad --load-bin ~/.ptolemy/monad-english.ptol --query "the"
```

### Expected trajectory

| Books ingested | Expected vocab | Field health |
|----------------|---------------|--------------|
| 5 | ~15,000 | 0.6–0.8 |
| 20 | ~35,000 | 0.75–0.9 |
| 50 | ~55,000 | 0.85–0.95 |
| 100+ (2nd pass) | ~65,000 | 0.90–0.98 |

The field saturates around 65,000–80,000 words — most English running text. On the second pass (books already cached), the engine reinforces β values on known words rather than allocating new vocabulary. BAO mean converges toward OMEGA_ZS as the field deepens.

### Loading the trained state into generation

```bash
# Next morning — generate from the trained field
ptolemy-monad --load-bin ~/.ptolemy/monad-english.ptol \
              --generate "the nature of consciousness" 80
```

---

## Chaining Operations

Multiple flags in one invocation are processed left to right. This is the intended workflow:

```bash
# Full pipeline: load → ingest three files → generate → save
ptolemy-monad \
    --load-bin  ~/.ptolemy/monad.ptol \
    --learn-file corpus/shakespeare.txt \
    --learn-file corpus/bible.txt \
    --learn-file corpus/hume.txt \
    --generate  "the nature of understanding" 40 \
    --report \
    --save-bin  ~/.ptolemy/monad.ptol
```

---

## Differences from PtolC and monad.py

There are three implementations. They share the same mathematical core but are separate binaries with separate state files.

| | `ptolemy-monad` | `PtolC/ptolemy` | `monad.py` |
|--|-----------------|-----------------|------------|
| Language | C (self-contained) | C (cmake build) | Python |
| State format | `.ptol` v3 | `.bin` (PtolC format) | `.pkl` (pickle) |
| Word hash | FNV-1a | SHA-256 equivalent | SHA-256 |
| Config file | none (CLI only) | `~/.ptolemy/ptolemy.cfg` | `.ptolrc` |
| Filesystem ingest | `--learn-file` | `-I <path>` (recursive) | via `monad.py` |
| Daemon | TCP port 7297 | Unix socket | — |
| SedenionAddressBook | — | — | yes (apisniff.py) |
| SkillBook DNS | — | — | yes (apisniff.py) |

`ptolemy-monad` is the learning engine. `PtolC/ptolemy` is the full operational kernel with config, filesystem walker, and daemon protocol. `monad.py` is the Python reference implementation with the SkillBook and SedenionAddressBook.

All three implement the same physics: cam_encode → J_pos/J_neg → A-matrix → σ-candidates → emit. The numbers diverge slightly due to the hash function difference (FNV-1a vs SHA-256), but the field topology is identical.

---

## Compilation Notes

```bash
# Standard build (recommended)
gcc -O2 -Wall -std=c99 -o ptolemy-monad monad.c -lm -lpthread

# Debug build (no optimization, assertions active)
gcc -O0 -g -Wall -std=c99 -o ptolemy-monad monad.c -lm -lpthread

# Strict (treat warnings as errors — all current warnings are benign stubs)
gcc -O2 -Wall -Werror -std=c99 -o ptolemy-monad monad.c -lm -lpthread
```

The `DIM_ROLE` array and `sed_dot`/`sed_add` functions are stubs for the Three-Face Wankel renderer (v2.2). They compile cleanly but produce `-Wunused` warnings under `-Wextra`. This is expected.

---

## Quick Reference Card

```
ptolemy-monad --load-bin FILE          Load .ptol state
              --save-bin FILE          Save .ptol state
              --learn-file PATH        Ingest text file
              --url http://...         Fetch HTTP and ingest
              --teach                  Learn from stdin (Ctrl-D to stop)
              --generate "seed" [N]    Generate N words (default 32)
              --query WORD             Print sedenion + field state
              --report                 Hamiltonian report (UNS, BAO, top words)
              --daemon [PORT]          TCP teaching server (default 7297)
              --help                   This help text

State:  ~/.ptolemy/monad-english.ptol  (overnight English corpus)
Log:    /tmp/ptol-teach.log           (if using nohup)
Daemon: nc localhost 7297              (send text, receive +N word count)

OMEGA_ZS = 0.56714  GAP = 0.000707  D_STAR = 0.246
```
