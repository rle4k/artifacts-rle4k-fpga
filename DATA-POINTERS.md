# Data pointers

Canonical locations of every dataset and binary referenced by the paper.

| Artifact | Canonical | Mirrors |
|---|---|---|
| 64 PCB Gerber samples (`DIF01.zip`…`DIF64.zip`, ~705 MB) | DOI [10.21227/t0cy-rb10](https://dx.doi.org/10.21227/t0cy-rb10) | GitHub [disking-cn/gerber-sample-files](https://github.com/disking-cn/gerber-sample-files) · Gitee `disking-cn/gerber_sample_files` |
| RLE4K test dataset: dataset-B strip (2403 compressed blocks) | this repo `data/rle4k_1/` (byte-locked, `CHECKSUMS.sha256`) + bitstreams at [rle4k/rle4k-decoder-fpga](https://github.com/rle4k/rle4k-decoder-fpga) — regenerable end-to-end from the 64 public samples with the public codec | archive copy: [IEEE DataPort RLE4K dataset page](https://ieee-dataport.org/documents/rle4k-pcb-raster-data-and-compression-code-real-time-maskless-lithography) (not cited by the paper, author decision 2026-10-25) |
| Board-level raw logs / timing / gates | this repo `sm1/` | submitted SM-1 in the journal package (id RLE4K-FPGA-2026-08) |
| CPU background extract (cited JM^3 numbers) | this repo `cpu-background-redtt/` | — |
| Host reference codec `redcli` | [rle4k/encoder-rle4k-cpu](https://github.com/rle4k/encoder-rle4k-cpu) | Gitee `rle4k/encoder-rle4k-cpu` |

**Repair note (2026-10):** at preparation time the DataPort landing page for
the RLE4K dataset was redirecting incorrectly (repair in progress). Until it
is fixed, the mirrors in the table above are the working access path; the DataPort page
is retained as an archive only and is no longer cited by the paper (author decision 2026-10-25).

**Bitstreams:** the shipped K=1/K=2 bitstreams (fw `0x80110`) are mirrored at
`rle4k-decoder-fpga/bitstreams/` with this repo's `sm1/build/` logs proving the
lane-count binding; they are byte-identical to the images used on 2026-08-14.
