# rle4k-fpga-artifacts

Raw experimental records backing the paper *"RLE4K FPGA Board-Level Decoding
for High-Throughput Maskless-Lithography Data Paths"* (target: IEEE Trans.
Industrial Electronics). This repository answers one question: **every number
in the paper — where does its raw record live?**

- RTL, bitstreams, build scripts: [rle4k/rle4k-decoder-fpga](https://github.com/rle4k/rle4k-decoder-fpga)
- Host-side reference codec (`redcli`): [rle4k/encoder-rle4k-cpu](https://github.com/rle4k/encoder-rle4k-cpu)

## Layout

| Path | What it is |
|---|---|
| `sm1/` | Full supplementary-material package (as submitted, extended through the 2026-10-27 verification rounds; see sm1/MIRROR-NOTE.md): all PASS rounds (152), crash/calibration rounds (61), K=4 baseline rounds (4), pre-discipline session logs (9), ping-gate records, routed timing & utilization reports, programmer logs, synthesis logs proving `P_NUM_LANES` binding. See `sm1/MANIFEST.md` for the paper-section map and `sm1/CHECKSUMS.sha256` (255 entries, `sha256sum -c` verifiable). |
| `sm1/rounds/output-correctness/` | Golden-strip and full-dataset CRC rounds backing the output-correctness claims, with a claim-to-file map. |
| `REPRODUCTION.md` | End-to-end reproduction procedure (host encode → feed shapes → programming → pass gate). |
| `DATA-POINTERS.md` | Canonical locations of the datasets and bitstreams. |
| `data/rle4k_1/` | Dataset B: the 2403 compressed `.rle4k` blocks actually fed to the board, byte-locked by its own `CHECKSUMS.sha256`; regenerable from the public Gerber samples with the public codec. |
| `cpu-background-redtt/` | Extracted database rows behind the cited CPU-side background numbers (64 public samples; JM^3 measurement campaign), with the locked query, verified aggregates and a glossary. Not part of the board experiments. |
| `CHECKSUMS.sha256` | Repository-wide checksum list (LF, `sha256sum -c` verifiable). |

## Sanitization

Only two transformations were applied to raw records, identical to the submitted
SM-1 package: absolute author work-tree paths → `<repo-root>` / `<path-redacted>`;
machine hostname → `<host>`. No measured value, timestamp or log line was altered.
Round logs under `sm1/rounds/` are byte-identical to the sources.

## Measurement discipline in one paragraph

A round PASSES iff `blocks_completed = 2403` and the ping gate holds (50/50
before, 5/5 after); the CRC content gate was OFF during throughput sweeps, so
these logs support *sustained-throughput* claims, not per-bit correctness —
the separate CRC round family covers correctness. A sustained point requires
≥3 consecutive passes with a reproducible crash above it. Both shipped builds
disclose routed WNS = −0.326 ns on five RGMII TX endpoints, decode domain clean.

## License

MIT (see `LICENSE`).
