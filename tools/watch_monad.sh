#!/usr/bin/env bash
# tools/watch_monad.sh — live field evolution tracker for ptolemy-monad
#
# Samples the field every INTERVAL seconds and logs a time-series snapshot:
#   timestamp | vocab | BAO_mean | health | top_word | generated passage
#
# Run this in a second terminal alongside teach_english.sh to watch the
# field develop over time. The log file persists across sessions.
#
# Usage:
#   bash tools/watch_monad.sh
#   bash tools/watch_monad.sh --query "consciousness"  (watch one word)
#   bash tools/watch_monad.sh --seed "the nature of" --interval 60

PTOL_BIN="${PTOL_BIN:-ptolemy-monad}"
STATE="${STATE:-$HOME/.ptolemy/monad-english.ptol}"
EVOLVE_LOG="${EVOLVE_LOG:-$HOME/.ptolemy/field_evolution.log}"
INTERVAL="${INTERVAL:-45}"       # seconds between samples
GEN_WORDS="${GEN_WORDS:-20}"     # words per generated passage
SEED="${SEED:-the nature of language}"
QUERY_WORD=""

# Parse args
while [[ $# -gt 0 ]]; do
    case "$1" in
        --seed)      SEED="$2";     shift 2 ;;
        --query)     QUERY_WORD="$2"; shift 2 ;;
        --interval)  INTERVAL="$2"; shift 2 ;;
        --words)     GEN_WORDS="$2"; shift 2 ;;
        --state)     STATE="$2";    shift 2 ;;
        --log)       EVOLVE_LOG="$2"; shift 2 ;;
        *) echo "Unknown: $1"; shift ;;
    esac
done

mkdir -p "$(dirname "$EVOLVE_LOG")"

# ── Parse --report output into fields ─────────────────────────────────────────
parse_report() {
    local report="$1"
    VOCAB=$(echo     "$report" | grep -oP 'vocab=\K\d+')
    BAO=$(echo       "$report" | grep -oP 'BAO_mean=\K[0-9.]+')
    HEALTH=$(echo    "$report" | grep -oP 'field_health=\K[0-9.]+')
    DTC=$(echo       "$report" | grep -oP 'DTC P0087.*count: \K\d+')
    SEGS=$(echo      "$report" | grep -oP 'SEGFAULT count: \K\d+')
    TOP_WORD=$(echo  "$report" | grep -A2 'Top activated' | \
               grep -oP '^\s+\K\S+' | head -1)
    TOP_BETA=$(echo  "$report" | grep -A2 'Top activated' | \
               grep -oP 'β=\K[0-9.]+' | head -1)
}

# ── UNS bar chart (compact, 80-col) ──────────────────────────────────────────
print_uns() {
    local report="$1"
    local ops=("identity" "negate" "bind" "name" "apply" "abstract"
               "branch" "iterate" "recurse" "allocate" "query" "dereference"
               "compose" "parallelize" "interrupt" "emit")
    echo ""
    echo "  UNS coordinates:"
    for k in {0..15}; do
        local val
        val=$(echo "$report" | grep -P "e\s*${k}\s" | grep -oP '[0-9]+\.[0-9]+' | head -1)
        [[ -z "$val" ]] && val="0.0000"
        local pct
        pct=$(echo "$val" | awk '{printf "%d", $1 * 30}')
        local bar
        bar=$(printf '%0.s█' $(seq 1 $pct 2>/dev/null) 2>/dev/null || printf '')
        printf "  e%-2d %-13s %6.4f |%s\n" "$k" "${ops[$k]}" "$val" "$bar"
    done
}

# ── Single snapshot ───────────────────────────────────────────────────────────
take_snapshot() {
    local ts
    ts=$(date '+%Y-%m-%d %H:%M:%S')

    if [[ ! -f "$STATE" ]]; then
        echo "[$ts] State file not found: $STATE (teaching not started yet?)"
        return
    fi

    # Load report
    local report
    report=$("$PTOL_BIN" --load-bin "$STATE" --report 2>/dev/null)
    parse_report "$report"

    # Generate a passage
    local passage
    passage=$("$PTOL_BIN" --load-bin "$STATE" \
               --generate "$SEED" "$GEN_WORDS" 2>/dev/null)

    # Optional word query
    local word_info=""
    if [[ -n "$QUERY_WORD" ]]; then
        word_info=$("$PTOL_BIN" --load-bin "$STATE" \
                    --query "$QUERY_WORD" 2>/dev/null | head -4)
    fi

    # ── Display ──────────────────────────────────────────────────────────────

    clear
    echo "╔══════════════════════════════════════════════════════════╗"
    printf "║  PTOLEMY FIELD MONITOR   %-32s║\n" "$ts"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""
    printf "  vocab     : %s words\n"     "${VOCAB:--}"
    printf "  BAO mean  : %s  (target: 0.56714)\n" "${BAO:--}"
    printf "  health    : %s  (1.0 = operating temp)\n" "${HEALTH:--}"
    printf "  DTC P0087 : %s  (BAO fault count)\n"   "${DTC:--}"
    printf "  SEGFAULTs : %s  (zero-divisor corrections)\n" "${SEGS:--}"
    printf "  top word  : %s  β=%s\n"  "${TOP_WORD:--}" "${TOP_BETA:--}"
    echo ""

    print_uns "$report"

    echo ""
    echo "  ── Generated from: \"$SEED\" ──"
    echo "  $passage"

    if [[ -n "$QUERY_WORD" && -n "$word_info" ]]; then
        echo ""
        echo "  ── Word: \"$QUERY_WORD\" ──"
        while IFS= read -r line; do
            echo "  $line"
        done <<< "$word_info"
    fi

    echo ""
    echo "  ── Top activated words ──"
    echo "$report" | grep -A 12 'Top activated' | tail -11 | \
        while IFS= read -r line; do echo "  $line"; done

    echo ""
    echo "  Log: $EVOLVE_LOG"
    echo "  Next sample in ${INTERVAL}s  (Ctrl-C to stop)"

    # ── Log entry (one line, TSV) ─────────────────────────────────────────────
    local passage_short
    passage_short=$(echo "$passage" | tr '\n' ' ' | cut -c1-80)
    printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
        "$ts" \
        "${VOCAB:--}" \
        "${BAO:--}" \
        "${HEALTH:--}" \
        "${DTC:--}" \
        "${SEGS:--}" \
        "${TOP_WORD:--}" \
        "$passage_short" \
        >> "$EVOLVE_LOG"
}

# ── Print log history ─────────────────────────────────────────────────────────
print_history() {
    if [[ ! -f "$EVOLVE_LOG" ]]; then
        echo "(no log yet)"
        return
    fi
    echo ""
    echo "Field evolution log — $EVOLVE_LOG"
    echo "────────────────────────────────────────────────────────────"
    printf "%-20s  %-7s  %-7s  %-6s  %-6s  %-15s  %s\n" \
           "timestamp" "vocab" "BAO" "health" "DTC" "top_word" "passage..."
    echo "────────────────────────────────────────────────────────────"
    while IFS=$'\t' read -r ts vocab bao health dtc segs top passage; do
        printf "%-20s  %-7s  %-7s  %-6s  %-6s  %-15s  %s\n" \
               "$ts" "$vocab" "$bao" "$health" "$dtc" "$top" \
               "${passage:0:50}..."
    done < "$EVOLVE_LOG"
    echo ""
}

# ── Header ────────────────────────────────────────────────────────────────────

echo "Ptolemy Field Monitor"
echo "  State    : $STATE"
echo "  Log      : $EVOLVE_LOG"
echo "  Seed     : \"$SEED\""
[[ -n "$QUERY_WORD" ]] && echo "  Tracking : \"$QUERY_WORD\""
echo "  Interval : ${INTERVAL}s"
echo ""

# Print history from prior sessions
print_history

echo "Starting monitor... (Ctrl-C to stop)"
sleep 2

# ── Monitor loop ──────────────────────────────────────────────────────────────
while true; do
    take_snapshot
    sleep "$INTERVAL"
done
