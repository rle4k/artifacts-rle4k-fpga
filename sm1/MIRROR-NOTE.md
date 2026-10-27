# MIRROR-NOTE — public mirror vs submitted SM-1

This `sm1/` mirror reproduces the SM-1 supplementary package
(RLE4K-FPGA-2026-08, extended through the 2026-10-26/27 verification rounds).
The package copies already carry the declared anonymisation (work-tree root
replaced by `<repo-root>`, hostname by `<host>`); on top of that, five files
received additional sub-path truncation at mirroring time so that no path
below the work-tree root, username or host is recoverable:

- `build/e1_impl_59g.log`, `build/e2_build_k2.log`, `build/e3_build_k1.log`
- `programming/vivado_program_fpga.ps1.log`
- `timing-utilization/e1_59g_timing_summary_routed.rpt`

No measured value, timestamp or log line content is altered anywhere.
`CHECKSUMS.sha256` in this directory is recomputed for the mirror as a whole
(277 evidence files + this note); verify with `sha256sum -c CHECKSUMS.sha256`.
The mirror was rebuilt from the 2026-10-27 state of the package and supersedes
the 2026-10-24 staging snapshot (newer board-level re-verification rounds
included).
