#!/usr/bin/env bash
# tools/teach_english.sh — overnight English corpus ingest for ptolemy-monad
#
# Online:  downloads canonical English literature from Project Gutenberg.
# Offline: falls back to filesystem exploration — scans the local machine
#          for prose text (docs, man pages, cached corpus, home directory).
#          Connectivity is re-checked every pass, so it will pick up internet
#          as soon as it becomes available.
#
# State is saved to ~/.ptolemy/monad-english.ptol after every source.
# Runs indefinitely.
#
# Usage:
#   bash tools/teach_english.sh
#
# Detached:
#   screen  -S ptolemy  bash tools/teach_english.sh
#   tmux new -s ptolemy bash tools/teach_english.sh
#   nohup bash tools/teach_english.sh > /tmp/ptol-teach.log 2>&1 &
#
# Override vars:
#   PTOL_BIN=ptolemy-monad   STATE=~/.ptolemy/monad-english.ptol
#   CORPUS_DIR=/tmp/ptol_corpus   REPORT_EVERY=10

PTOL_BIN="${PTOL_BIN:-ptolemy-monad}"
STATE="${STATE:-$HOME/.ptolemy/monad-english.ptol}"
CORPUS_DIR="${CORPUS_DIR:-/tmp/ptol_corpus}"
REPORT_EVERY="${REPORT_EVERY:-10}"
CURL_TIMEOUT="${CURL_TIMEOUT:-60}"
MIN_PROSE_BYTES="${MIN_PROSE_BYTES:-8192}"   # ignore files smaller than 8KB

# 22 canonical English texts — diverse register, public domain
BOOKS=(
    "https://www.gutenberg.org/files/10/10.txt"           # KJV Bible
    "https://www.gutenberg.org/files/100/100.txt"         # Complete Shakespeare
    "https://www.gutenberg.org/files/2701/2701-0.txt"     # Moby Dick
    "https://www.gutenberg.org/files/1342/1342-0.txt"     # Pride and Prejudice
    "https://www.gutenberg.org/files/1661/1661-0.txt"     # Adventures of Sherlock Holmes
    "https://www.gutenberg.org/files/98/98-0.txt"         # A Tale of Two Cities
    "https://www.gutenberg.org/files/84/84-0.txt"         # Frankenstein
    "https://www.gutenberg.org/files/1400/1400-0.txt"     # Great Expectations
    "https://www.gutenberg.org/files/11/11-0.txt"         # Alice in Wonderland
    "https://www.gutenberg.org/files/521/521-0.txt"       # Adventures of Tom Sawyer
    "https://www.gutenberg.org/files/76/76-0.txt"         # Huckleberry Finn
    "https://www.gutenberg.org/files/174/174-0.txt"       # The Picture of Dorian Gray
    "https://www.gutenberg.org/files/2554/2554-0.txt"     # Crime and Punishment
    "https://www.gutenberg.org/files/2600/2600-0.txt"     # War and Peace
    "https://www.gutenberg.org/files/4300/4300-0.txt"     # Ulysses
    "https://www.gutenberg.org/files/1497/1497-0.txt"     # Plato: The Republic
    "https://www.gutenberg.org/files/2413/2413-0.txt"     # Hume: Enquiry Concerning Human Understanding
    "https://www.gutenberg.org/files/1232/1232-0.txt"     # Machiavelli: The Prince
    "https://www.gutenberg.org/files/1080/1080-0.txt"     # Swift: A Modest Proposal
    "https://www.gutenberg.org/files/4085/4085-0.txt"     # Franklin: Autobiography
    "https://www.gutenberg.org/files/1952/1952-0.txt"     # The Yellow Wallpaper
    "https://www.gutenberg.org/files/5200/5200-0.txt"     # Metamorphosis (Kafka)
)

# Man pages worth learning from (dense English prose)
MAN_PAGES=(
    bash python3 git find grep sed awk perl
    make cmake gcc gdb
    ssh curl wget rsync
    vim emacs less more
    crontab systemd journalctl
    intro man ls cat
)

# ── Sanity checks ─────────────────────────────────────────────────────────────

if ! command -v "$PTOL_BIN" &>/dev/null; then
    echo "[ERROR] $PTOL_BIN not found."
    echo "        cd ~/Projects/Ptol/SMMIP && make && make install"
    exit 1
fi

mkdir -p "$CORPUS_DIR"
mkdir -p "$(dirname "$STATE")"

# ── Utility ───────────────────────────────────────────────────────────────────

# Returns 0 if internet is reachable
check_online() {
    if ! command -v curl &>/dev/null; then return 1; fi
    curl -s --max-time 6 --head "https://www.gutenberg.org/" &>/dev/null
}

# Feed one file to the monad. Args: path label
learn_one() {
    local path="$1"
    local label="${2:-$(basename "$1")}"
    local load_arg=""
    [[ -f "$STATE" ]] && load_arg="--load-bin $STATE"

    printf "[learn] %-44s " "${label:0:44}"

    local result
    result=$("$PTOL_BIN" $load_arg \
                          --learn-file "$path" \
                          --save-bin   "$STATE" 2>&1)

    local vocab learned
    vocab=$(echo  "$result" | grep -oP '(?<=saved )\d+(?= words)'  | tail -1)
    learned=$(echo "$result" | grep -oP '\d+(?= words from)'       | tail -1)
    printf "vocab=%-6s  +%s words\n" "${vocab:--}" "${learned:--}"
}

# Emit --report summary (brief)
brief_report() {
    [[ ! -f "$STATE" ]] && return
    "$PTOL_BIN" --load-bin "$STATE" --report 2>/dev/null | \
        grep -E '(vocab=|BAO_mean|field_health|DTC|SEGFAULT|Top act)' || true
}

# Full report every REPORT_EVERY items
maybe_report() {
    local n="$1"
    if (( n > 0 && n % REPORT_EVERY == 0 )); then
        echo ""
        "$PTOL_BIN" --load-bin "$STATE" --report 2>/dev/null || true
        echo ""
    fi
}

# ── Online pass ───────────────────────────────────────────────────────────────

run_online_pass() {
    local n=0
    echo "[online] Gutenberg corpus — ${#BOOKS[@]} titles"

    for url in "${BOOKS[@]}"; do
        local fname local_path
        fname="$(basename "$url")"
        local_path="$CORPUS_DIR/$fname"

        # Download if not cached or empty
        if [[ ! -s "$local_path" ]]; then
            printf "[dl]    %-44s " "${fname:0:44}"
            if curl -sL --max-time "$CURL_TIMEOUT" \
                    -A "Ptolemy/1.218" -o "$local_path" "$url" 2>/dev/null \
               && [[ -s "$local_path" ]]; then
                printf "%d KB\n" "$(( $(wc -c < "$local_path") / 1024 ))"
            else
                echo "FAILED"
                rm -f "$local_path"
                continue
            fi
        fi

        [[ ! -s "$local_path" ]] && continue
        n=$((n + 1))
        total_items=$((total_items + 1))
        learn_one "$local_path" "$fname"
        maybe_report "$total_items"
    done

    echo "[online] Pass complete — $n items"
}

# ── Offline pass ──────────────────────────────────────────────────────────────

# Collect local prose files into an array, randomised, deduped
collect_local_prose() {
    local -n _out=$1   # nameref to caller's array

    # 1. Already-cached Gutenberg corpus
    while IFS= read -r -d '' f; do
        _out+=("$f")
    done < <(find "$CORPUS_DIR" -type f -name "*.txt" -size +"${MIN_PROSE_BYTES}c" \
             -print0 2>/dev/null)

    # 2. Home directory: .txt, .md, .rst — skip hidden dirs and source trees
    while IFS= read -r -d '' f; do
        _out+=("$f")
    done < <(find "$HOME" \
             -not \( -path '*/.git/*' -o -path '*/node_modules/*' \
                  -o -path '*/__pycache__/*' -o -path '*/.cache/*' \
                  -o -path '*/.local/share/Trash/*' \) \
             -type f \
             \( -name "*.txt" -o -name "*.md" -o -name "*.rst" \) \
             -size +"${MIN_PROSE_BYTES}c" \
             -print0 2>/dev/null)

    # 3. System package documentation — READMEs, plain changelogs, licenses
    while IFS= read -r -d '' f; do
        _out+=("$f")
    done < <(find /usr/share/doc /usr/share/common-licenses \
             -maxdepth 4 -type f \
             \( -name "README" -o -name "README.txt" -o -name "README.md" \
                -o -name "changelog" -o -name "CHANGES" -o -name "NEWS" \
                -o -name "COPYING" -o -name "copyright" -o -name "AUTHORS" \) \
             -size +"${MIN_PROSE_BYTES}c" \
             -print0 2>/dev/null)

    # 4. Fortune cookie files (if installed) — dense, varied short prose
    if [[ -d /usr/share/games/fortunes ]]; then
        while IFS= read -r -d '' f; do
            # Fortune .dat files are binary indexes — skip them
            [[ "$f" == *.dat ]] && continue
            _out+=("$f")
        done < <(find /usr/share/games/fortunes -type f -size +"${MIN_PROSE_BYTES}c" \
                 -print0 2>/dev/null)
    fi
}

# Strip gzip doc in-place to a temp file, learn it, delete temp
learn_gzipped() {
    local gz="$1"
    local tmp
    tmp=$(mktemp /tmp/ptol_gz_XXXXXX.txt)
    if zcat "$gz" > "$tmp" 2>/dev/null && [[ -s "$tmp" ]]; then
        learn_one "$tmp" "$(basename "$gz" .gz)"
        total_items=$((total_items + 1))
        maybe_report "$total_items"
    fi
    rm -f "$tmp"
}

# Render a man page to plain text and learn it
learn_manpage() {
    local page="$1"
    local tmp
    tmp=$(mktemp /tmp/ptol_man_XXXXXX.txt)
    if man -P cat "$page" 2>/dev/null | col -b > "$tmp" \
       && [[ -s "$tmp" ]] \
       && (( $(wc -c < "$tmp") >= MIN_PROSE_BYTES )); then
        learn_one "$tmp" "man:$page"
        total_items=$((total_items + 1))
        maybe_report "$total_items"
    fi
    rm -f "$tmp"
}

run_offline_pass() {
    echo "[offline] No internet — scanning filesystem for prose..."

    # a) Collected prose files (random order each pass)
    local prose_files=()
    collect_local_prose prose_files

    # Deduplicate
    local seen=()
    local deduped=()
    for f in "${prose_files[@]}"; do
        local skip=0
        for s in "${seen[@]}"; do [[ "$s" == "$f" ]] && skip=1 && break; done
        if (( skip == 0 )); then
            seen+=("$f")
            deduped+=("$f")
        fi
    done

    # Shuffle (portable: sort -R, or python if available)
    local shuffled=()
    if command -v python3 &>/dev/null; then
        while IFS= read -r line; do
            shuffled+=("$line")
        done < <(printf '%s\n' "${deduped[@]}" | python3 -c \
                 'import sys,random; lines=sys.stdin.read().splitlines(); random.shuffle(lines); print("\n".join(lines))')
    else
        while IFS= read -r line; do
            shuffled+=("$line")
        done < <(printf '%s\n' "${deduped[@]}" | sort -R 2>/dev/null || printf '%s\n' "${deduped[@]}")
    fi

    echo "[offline] Found ${#shuffled[@]} local prose files"

    local n=0
    for path in "${shuffled[@]}"; do
        [[ ! -s "$path" ]] && continue

        # Gzipped docs: decompress to temp
        if [[ "$path" == *.gz ]]; then
            learn_gzipped "$path"
            n=$((n + 1))
            continue
        fi

        # Sanity: skip if mostly binary (>10% non-printable in first 512 bytes)
        local binary_ratio
        binary_ratio=$(head -c 512 "$path" 2>/dev/null | \
                       LC_ALL=C tr -cd '[:print:][:space:]' | wc -c)
        local raw_head
        raw_head=$(head -c 512 "$path" 2>/dev/null | wc -c)
        if (( raw_head > 0 && binary_ratio * 10 < raw_head * 9 )); then
            continue  # less than 90% printable — binary
        fi

        n=$((n + 1))
        total_items=$((total_items + 1))
        learn_one "$path" "$(basename "$path")"
        maybe_report "$total_items"
    done

    # b) Man pages — always available offline
    echo "[offline] Extracting man pages..."
    for page in "${MAN_PAGES[@]}"; do
        learn_manpage "$page"
    done

    # c) Gzipped changelogs in /usr/share/doc
    echo "[offline] Scanning gzipped system docs..."
    local gz_count=0
    while IFS= read -r -d '' gz; do
        learn_gzipped "$gz"
        gz_count=$((gz_count + 1))
        (( gz_count >= 200 )) && break   # cap at 200 per pass
    done < <(find /usr/share/doc -type f -name "*.gz" \
             -size +"${MIN_PROSE_BYTES}c" -print0 2>/dev/null | \
             sort -zR 2>/dev/null)

    echo "[offline] Pass complete — $n local files + ${#MAN_PAGES[@]} man pages + $gz_count gz docs"
}

# ── Header ────────────────────────────────────────────────────────────────────

echo "╔══════════════════════════════════════════════════════════╗"
echo "║          PTOLEMY MONAD — OVERNIGHT ENGLISH TEACH         ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo "  Binary  : $PTOL_BIN ($("$PTOL_BIN" --help 2>&1 | head -1))"
echo "  State   : $STATE"
echo "  Corpus  : $CORPUS_DIR"
echo "  Started : $(date)"
echo ""

# ── Main loop ─────────────────────────────────────────────────────────────────

total_items=0
pass=0

while true; do
    pass=$((pass + 1))
    echo ""
    echo "══ Pass $pass  $(date '+%Y-%m-%d %H:%M:%S') ══════════════════════════"

    if check_online; then
        echo "[net]   Online — using Gutenberg corpus"
        run_online_pass
    else
        echo "[net]   Offline — using local filesystem"
        run_offline_pass
    fi

    echo ""
    echo "── End of pass $pass.  Total items ingested: $total_items"
    brief_report
    echo ""
    echo "── Sleeping 30s before pass $((pass+1))  (Ctrl-C to stop)..."
    sleep 30
done
