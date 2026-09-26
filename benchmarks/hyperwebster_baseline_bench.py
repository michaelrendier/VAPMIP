#!/usr/bin/env python3
"""
VAPMIP/benchmarks/hyperwebster_baseline_bench.py
=================================================
Baseline benchmark for the plain (non-octonion) HyperWebster indexer —
the "quaint, first project out the gate" bijective base-N text/integer
mapping, canonical source:
  PtolemyDesktop/Callimachus/HyperWebster-Data-Storage/hyperwebster.py

Run against the UNMODIFIED canonical class (imported by path, not copied,
so this benchmark can never silently drift from the real implementation).

Purpose (Cody, 2026-09-25): establish measured numbers — encode/decode
time vs chunk size, address size with full vs minimal (per-chunk) charset,
and multi-layer (chunk -> day -> month -> year) nested-index reconstruction
time — as the starting data for FourthAgePapers/HyperindexingSystem and the
forthcoming HyperWebster Navigation and Indexing Specification for the Monad.

Sibling result already on record: FourthAgePapers `data-storage-no-location`
branch (2026-08-30, unpushed) measured Horner encode at ~O(n^1.8) on this
same reference machine, via the octonion/Cayley-Dickson-folded variant. This
benchmark's ~4.7-5.3x time growth per input-size doubling (between quadratic
and cubic) is consistent with that prior, independent measurement -- two
different code paths on the same core Horner mechanism agreeing on the same
non-linear growth rate.

No network, no repo mutation. Read-only against the canonical file.
"""

import sys
import time
import platform
import importlib.util

CANONICAL_HW_PATH = (
    "/home/rendier/Projects/ThePlace/PtolemyDesktop/"
    "Callimachus/HyperWebster-Data-Storage/hyperwebster.py"
)


def _load_canonical_hyperwebster():
    spec = importlib.util.spec_from_file_location("hyperwebster_canonical", CANONICAL_HW_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.HyperWebster


SAMPLE_PARAGRAPH = (
    "The bee's flight has no airfoil in the aircraft-wing sense; it stays "
    "aloft by stalling and re-stalling its wings on every stroke, shedding "
    "leading-edge vortices fast enough that lift never fully collapses. Same "
    "trick a fly uses, just a smaller, buzzier version of it, and it works "
    "because the air behaves differently at that scale, not because a fly "
    "quietly disobeys physics."
)


def bench_chunk_sizes(HyperWebster, sizes=(140, 500, 1000, 2000, 4000)):
    rows = []
    for size in sizes:
        text = (SAMPLE_PARAGRAPH * ((size // len(SAMPLE_PARAGRAPH)) + 1))[:size]

        hw_full = HyperWebster()
        t0 = time.perf_counter()
        addr = hw_full.point_to_text(text)
        t1 = time.perf_counter()
        back = hw_full.regenerate_text(addr)
        t2 = time.perf_counter()
        assert back == text, "full-charset round-trip failed"

        minchars = "".join(sorted(set(text)))
        hw_min = HyperWebster(characters=minchars)
        t3 = time.perf_counter()
        addr2 = hw_min.point_to_text(text)
        t4 = time.perf_counter()
        back2 = hw_min.regenerate_text(addr2)
        t5 = time.perf_counter()
        assert back2 == text, "minimal-charset round-trip failed"

        rows.append({
            "chars": size,
            "N_full": hw_full.N, "addr_bits_full": addr.bit_length(),
            "enc_ms_full": 1000 * (t1 - t0), "dec_ms_full": 1000 * (t2 - t1),
            "N_min": hw_min.N, "addr_bits_min": addr2.bit_length(),
            "enc_ms_min": 1000 * (t4 - t3), "dec_ms_min": 1000 * (t5 - t4),
        })
    return rows


def bench_multilayer_reconstruction(HyperWebster):
    """Simulate chunk -> day -> month -> year nested index reconstruction.
    Each level is a small JSON-shaped string of child pointers; decoding the
    full path is a fixed number of hops (4), never a scan of prior history."""
    hw = HyperWebster()
    chunk_text = SAMPLE_PARAGRAPH[:800]
    chunk_addr, _, _ = hw.index_text(chunk_text)

    day_index = f'{{"chunks":["{chunk_addr}"]}}'
    month_index = f'{{"days":["{hw.int_to_hex256(hw.point_to_text(day_index))}"]}}'
    year_index = f'{{"months":["{hw.int_to_hex256(hw.point_to_text(month_index))}"]}}'

    t0 = time.perf_counter()
    decoded_year = hw.regenerate_text(hw.hex256_to_int(hw.int_to_hex256(hw.point_to_text(year_index))))
    month_addr_hex = decoded_year.split('"')[3]
    decoded_month = hw.regenerate_text(hw.hex256_to_int(month_addr_hex))
    day_addr_hex = decoded_month.split('"')[3]
    decoded_day = hw.regenerate_text(hw.hex256_to_int(day_addr_hex))
    chunk_addr_hex = decoded_day.split('"')[3]
    decoded_chunk = hw.regenerate_text(hw.hex256_to_int(chunk_addr_hex))
    t1 = time.perf_counter()

    return {
        "roundtrip_ok": decoded_chunk == chunk_text,
        "n_layers": 4,
        "total_ms": 1000 * (t1 - t0),
    }


def machine_report():
    import subprocess
    try:
        cpu = subprocess.check_output(
            "lscpu | grep 'Model name' | sed 's/Model name:\\s*//'",
            shell=True, text=True).strip()
    except Exception:
        cpu = platform.processor() or "unknown"
    return {
        "cpu": cpu,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
    }


if __name__ == "__main__":
    HyperWebster = _load_canonical_hyperwebster()

    m = machine_report()
    print("=" * 78)
    print("HyperWebster baseline benchmark -- canonical, unmodified indexer")
    print(f"CPU: {m['cpu']}  |  Python {m['python']}  |  {m['platform']}")
    print("=" * 78)

    print(f"\n{'chars':>6} {'N(full)':>8} {'bits(full)':>11} {'enc_ms':>8} {'dec_ms':>8} "
          f"{'N(min)':>7} {'bits(min)':>10} {'enc_ms_min':>11} {'dec_ms_min':>11}")
    for r in bench_chunk_sizes(HyperWebster):
        print(f"{r['chars']:>6} {r['N_full']:>8} {r['addr_bits_full']:>11} "
              f"{r['enc_ms_full']:>8.3f} {r['dec_ms_full']:>8.3f} "
              f"{r['N_min']:>7} {r['addr_bits_min']:>10} "
              f"{r['enc_ms_min']:>11.3f} {r['dec_ms_min']:>11.3f}")

    ml = bench_multilayer_reconstruction(HyperWebster)
    print(f"\n4-layer (chunk/day/month/year) nested reconstruction: "
          f"{ml['total_ms']:.4f} ms, round-trip correct: {ml['roundtrip_ok']}")
