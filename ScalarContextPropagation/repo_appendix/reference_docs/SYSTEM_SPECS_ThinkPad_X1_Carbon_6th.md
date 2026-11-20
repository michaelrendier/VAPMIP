# System Specs — Lenovo ThinkPad X1 Carbon (6th Gen)

Snapshot for benchmarking baseline reference.

**Snapshot date:** 2026-07-31
**Hostname:** rendier-HP-EliteBook-820-G3 (stale hostname string; hardware confirmed via DMI below is genuinely the X1 Carbon 6th, not an EliteBook)

## Machine Identity (DMI)
- **Manufacturer:** LENOVO
- **Product name:** 20KH002XUS
- **Version/Family:** ThinkPad X1 Carbon 6th
- **SKU:** LENOVO_MT_20KH_BU_Think_FM_ThinkPad X1 Carbon 6th

## CPU
- **Model:** Intel(R) Core(TM) i7-8550U @ 1.80GHz (Kaby Lake R)
- **Cores/Threads:** 4 cores / 8 threads
- **Max clock:** 4000 MHz | **Min clock:** 400 MHz
- **Cache:** L1d 128 KiB, L1i 128 KiB, L2 1 MiB, L3 8 MiB
- **Virtualization:** VT-x

## Memory
- **Total RAM:** 7.5 GiB
- **Swap:** 3.7 GiB

## Storage
- **NVMe (system):** Timetec MS10, 953.9 GB, MAXIO MAP1202 controller (DRAM-less), rev 01
  - `nvme0n1p1` 476M vfat `/boot/efi`
  - `nvme0n1p2` 93.1G ext4 `/` (49G used / 45G avail at snapshot time)
  - `nvme0n1p3` 3.7G swap
  - `nvme0n1p4` 856.5G ext4 `/home`
- **External SD/USB card:** SD/MMC CRW, 239.1G, exfat, mounted at `/media/rendier/0123-4567` (ThePlace working directory lives here) — 89G used / 151G avail at snapshot time

## GPU / Display
- **GPU:** Intel UHD Graphics 620 (rev 07), integrated
- **Panel:** eDP-1, 1920x1080 @ 60.05 Hz, 309mm x 174mm (~14" FHD)

## Networking
- **Ethernet:** Intel Ethernet Connection (4) I219-V (rev 21)
- **Wi-Fi:** Intel Wireless 8265/8275 (rev 78)

## Battery
- **State at snapshot:** discharging, 70%
- **Energy full (current):** 49.51 Wh
- **Energy full (design):** 57 Wh
- **Health:** ~86.9% of design capacity

## OS / Kernel
- **Distro:** Linux Mint 22.1 (Xia), Ubuntu Noble base
- **Kernel:** 6.8.0-117-lowlatency (SMP PREEMPT_DYNAMIC, built 2026-05-06)
- **Architecture:** x86_64

## Toolchain (snapshot)
- **GCC:** 13.3.0 (Ubuntu 13.3.0-6ubuntu2~24.04.1)
- **Python:** 3.12.3
- **Node:** v24.14.1

## Notes for future benchmarking
- This is the "home" NVMe machine (TimeTec MS10 is DRAM-less — expect softer sustained-write performance than a DRAM-cached NVMe under heavy I/O; useful to know when comparing benchmark runs across machines).
- RAM is the likely constraint (7.5 GiB) for anything memory-heavy (e.g. large sedenion/monad computations, corpus builds) — swap is present (3.7 GiB) but will skew timing benchmarks if triggered.
- SMART/NVMe wear stats and hdparm throughput were not captured this pass (require sudo password, not available non-interactively). Re-run with sudo for a fuller I/O baseline if needed:
  `sudo smartctl -a /dev/nvme0n1` and `sudo hdparm -t /dev/nvme0n1p2`
