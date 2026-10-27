# Dataset B — the RLE4K test strip actually fed to the board

2403 compressed `.rle4k` blocks (`raster_strip0_blockNNNN.rle4k`, 30,888,975 bytes
total) — the exact compressed code stream behind every board-level number in the
paper (all `sm1/` rounds used these blocks; `blocks_completed = 2403` is the pass
criterion).

Structure and identity (authoritative definition in `sm1/` round logs):

| Item | Value |
|---|---|
| blocks | 2403 |
| block_height / width=stride | 512 / 65,536 |
| strip height | 1,230,083 |
| on-wire per feed round | 24,334 frames, payload 30,794,948 B, 31,356,218 B incl. Ethernet framing |
| decoded output | 157,450,624 words of 64 B = 80.6147 Gbit |
| expansion ratio | 321.367:1 |
| strip geometry of origin | C = 1920, R = 512, N = 32 (DLP9500-class DMD) |

Provenance: regenerable end-to-end — rasterize the public PCB Gerber samples
(DOI 10.21227/t0cy-rb10) to 1-bpp DMD strips with the above geometry and encode
per block with the public reference codec [rle4k/encoder-rle4k-cpu](https://github.com/rle4k/encoder-rle4k-cpu)
(`redcli`). The copies here are byte-locked via `CHECKSUMS.sha256` (2403 entries,
`sha256sum -c` verifiable) so the regeneration claim is checkable against the fed
data, not just asserted.

`DATASET-META.json` carries the same numbers machine-readably.

License: MIT (repository-wide).
