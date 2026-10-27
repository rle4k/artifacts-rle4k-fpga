# CPU-side background data extracted from the LdViewer measurement database (redtt)

What this folder is, and is not.

**Is:** the exact database rows behind the CPU encode/decode background numbers the
paper *cites* (not measures): mean expansion ratio and mean encode/decode rates of
RLE4K over the 64 public PCB Gerber samples, as published in the JM^3 study and
cross-checked before citation.

**Is not:** part of the FPGA board experiments. No Gbit/s number on the board side
of the paper was derived from these rows, and the two quantities must never be
converted into each other (different estimators, different machines, different
pipeline scopes). The board numbers live entirely in `sm1/`.

## Provenance

- Source: LdViewer benchmark database, table `redtt_average_file_data` (file-level
  aggregates; one row per sample file per query condition). The companion table
  `redtt_repeat_strip_data` holds strip-level repeats and yields different means,
  it is NOT the cited table.
- Locked selection (the exact filter used for the citation cross-check, 2026-08-30):
  `n=32` (tilt factor), `pw=0.5` (pixel width um), `rt=4` (encode threads),
  `format_encoder=4` (RLE4K). This filter returns exactly 64 rows, one per sample.
- Export: `rle4k_cpu_background_64files_n32_pw0p5_rt4.csv`, full original columns
  plus three derived columns, see below. Internal primary-key column `id` removed.

## Derived columns and the JM^3-locked formulas

- `rho = TIS / CS` (uncompressed image bytes over compressed size).
- `E_gbps = (TIS/1e6)*8 / WED`, `D_gbps = (TIS/1e6)*8 / WDD` (JM^3-locked speed
  formulas, `TIS` in bytes, `WED`/`WDD` in ms; the estimator convention follows JM^3).

## Verified aggregates (reproduce with `python verify.py`)

`n_rows = 64`, mu(rho) = 203.4 +/- 93.7, mu(E) = 70.3 +/- 9.5, mu(D) = 78.3 +/- 10.2
(sample standard deviation). These match the values cited via the JM^3 study; the
cross-check record predates this export and is kept in the author's manuscript
repository (`0004.JM3 citation check`, 2026-08-30).

## Column glossary (LdViewer field labels)

| Column | Meaning |
|---|---|
| n | tilt factor N |
| pw | pixel width (um) |
| fileno | sample file number (1..64) |
| format_encoder | codec id, 4 = RLE4K |
| rrt / et / dt | raster / encode / decode thread counts |
| rt | encode threads used by the run (equals ET) |
| tis | target image accumulated bytes (uncompressed raster) |
| cs | compressed size (bytes) |
| acr | strip compression ratio (%) |
| tbc | strip total block count |
| wrd / srd | strip raster wall-clock / accumulated ms |
| wed / sed | strip encode wall-clock / accumulated ms |
| wdd / sdd | strip decode wall-clock / accumulated ms |
| spt / bat / scd | strip parallel span ms / per-block average ms / strip cache ms |
| gfs | source graphic file size (bytes) |
| sds | strip data volume (GB) |
| sdt | strip decode throughput MB/s (based on WDD) |
| grk / gek / gdk | GPU raster / encode / decode kernel ms (unused by CPU rows) |
| h2d / d2h / ptm | PCIe upload / download bytes / transfer ms |
| aggregated_date | aggregation timestamp |

## License

MIT (repository-wide). The 64 source samples are public under DOI
10.21227/t0cy-rb10 (see `../DATA-POINTERS.md`).
