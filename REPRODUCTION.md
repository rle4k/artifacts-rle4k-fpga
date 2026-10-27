# Reproduction guide

What the paper claims as measured, and how to re-obtain it.

## Prerequisites

- Board: commercial off-the-shelf Kintex UltraScale XCKU040 data-processing card (MILIANKE KU040/060 series; or any board
  with the same TEMAC + RGMII front end; timings are board-specific — see the
  paper's retest caveat).
- Host: Windows with [Npcap](https://npcap.com/) installed (driver, not
  redistributed here); Visual Studio 2019/2022 + CMake for `rle4k_cli`.
- Toolchain: Vivado 2022.2 with Tri-Mode Ethernet MAC (TEMAC) IP licensed in the
  webtalk of the user's installation.

## Step 1 — encode the test strip (host)

Use `redcli` from [rle4k/encoder-rle4k-cpu](https://github.com/rle4k/encoder-rle4k-cpu):
rasterize a Gerber sample (DOI [10.21227/t0cy-rb10](https://dx.doi.org/10.21227/t0cy-rb10))
to 1-bpp DMD strips with the strip geometry of the paper ($C=1920$, $R=512$,
$N=32$), encode per block. The dataset-B strip (2403 blocks, expansion ratio
321.367:1) and its compressed code are regenerable end-to-end from the raw Gerber samples with the public codec above; an archive copy sits at the [IEEE DataPort RLE4K dataset page](https://ieee-dataport.org/documents/rle4k-pcb-raster-data-and-compression-code-real-time-maskless-lithography) (not cited by the paper); reproducing from the
raw Gerber is also possible end-to-end.

## Step 2 — build the bitstream (or program the shipped one)

`rle4k-decoder-fpga`: `scripts/create_project_2022_2.tcl` +
`scripts/quick_build.tcl`, or program `bitstreams/k1|rle4k_k1_fw0x80110.bit`
(K=1) / `bitstreams/k2/rle4k_k2_fw0x80110.bit` (K=2) directly.

## Step 3 — program and gate

```powershell
powershell scripts/program_fpga.ps1 -Bit <bit>
# programmer must report the known-good signature AFTER_ILA_COUNT 0 / AFTER_VIO_COUNT 1
# then wait 25 s settle; ping gate: 10 x (ping -n 5) must be 50/50
```

## Step 4 — feed and record

`scripts/BatchSendStrip.ps1` implements the three send shapes:
**block-gated** (per-block pacing), **per-block flush**, **constant-rate smooth**.
A round passes iff `blocks_completed = 2403` and post-round ping is 5/5.
A sustained point requires ≥3 consecutive passes and a reproducible crash above
(2 recurrences). Headline medians (dataset B): K=1 block-gated 56.38 Gbit/s;
K=2 per-block flush 93.53 Gbit/s; matched constant-rate pair 44.18 / 93.60
Gbit/s. Compare against `sm1/rounds/` logs — file names encode shape, lane
count and wire rate.

## Step 5 — verify this repository

```sh
sha256sum -c CHECKSUMS.sha256            # repo-wide
cd sm1 && sha256sum -c CHECKSUMS.sha256  # SM-1 mirror, 277 evidence files
```

## Known limitation

The DataPort landing page of the RLE4K dataset was under repair when this
repository was prepared; mirrors here (and, if enabled, a Zenodo archival) are
the fallback. The board-level numbers themselves are fully contained in `sm1/`.
