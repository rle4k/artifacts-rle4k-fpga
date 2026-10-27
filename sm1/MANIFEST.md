# SM-1 — Board-Level Raw Logs and Supporting Records
Supplementary Material for: "RLE4K: …" (target IEEE TIE), archive id RLE4K-FPGA-2026-08
Prepared: 2026-10-06. Authoritative index: `V08MAC/reports/2026-08-14-paper-data-consolidated.md` §10 (证据索引).
No manuscript numbers were recomputed here; this package only collects the raw records that index cites.

## Contents

| Directory | Files | Maps to | What it is |
|---|---|---|---|
| `rounds/pass2403/` | 152 | §10.1–§10.4 | All board rounds with `expected=2403 && blocks_completed=2403` (the regression sample of §10.4, exact count). Includes warmup-named logs that also meet the criterion (see note N3). |
| `rounds/crash-and-cal/` | 61 | §10.1–§10.3 | Crash rounds (e.g. `e6_smooth_k1_bg_p540_r241_run{1,2}`, `e5_burst_1024k_144_run{1,2}`, `e4_k1_t150_WEDGE_cold`) and calibration/probe rounds cited in §10. |
| `rounds/k4-baseline/` | 4 | §10.6 | K=4 baseline stdout: `e1_tag_run{1,2,3}` (used) + `e1_tag_run4` (present, not used — §8.1, shipped for completeness). |
| `rounds/pre-discipline-session/` | 9 | §10.2, §8.2 | `e2_k2_paced*` first-test session (91.81 G), unpaced wedge and gap-8 degenerate rounds — flagged in the consolidated volume as pre-discipline. |
| `gates/` | 6 | §3 discipline | `e2_k2_ping_gate.txt` (raw ping-gate stdout, ASCII) + the five 2026-08 session notes (`exp/*.md`) that record the "25 s settle → 10×`ping 5` = 50/50 gate → discard one warmup round → 5/5 post-round" gate results per round (see note N1). |
| `timing-utilization/` | 5 | §10.5, §10.6 | K=1/K=2 routed timing summary + utilization reports (`WNS −0.326 ns`, 5 RGMII TX endpoints identical), and K=4 `e1_59g_timing_summary_routed.rpt`. |
| `programming/` | 3 | §2 discipline, §10.6 | Programmer stdout: 2026-08-14 K=1 session log (carries the known-good signature `AFTER_ILA_COUNT 0` / `AFTER_VIO_COUNT 1`), `e2_k2_program.txt`, `e1_reprogram.txt` (K=4 session). |
| `build/` | 3 | §10.5 | `e3_build_k1.log` and `e2_build_k2.log` are synthesis logs proving lane-count binding (`P_NUM_LANES bound to`). `e1_impl_59g.log` is the implementation log of the 59g (K=2) branch build (timing/utilization context); it does not itself carry the binding line. |
| `rtl-kbranch-exp20260814/` | 4 | Fig. 4 lane naming only | RTL name ground truth for the parallel-bank branch (branch `exp/20260814-flowctl-fix` @993cb9b: `rle4k_parallel_bank_v8.v`, `rle4k_lane_pipe_v8.v`, `rle4k_lan_top_v8.v`, README). The Fig. 6 / Appendix A CORE sources are NOT in this folder; the complete source tree is available on request.
| `rounds/output-correctness/` | 17 | §3.4 output-correctness paragraph | Decode-correctness evidence: the fw 0x80104 golden-strip / per-file / single-strip rounds (2026-08-08/09 reports and summaries) plus, added 2026-10-26, `2026-10-26-fw80110-blockcrc/` — per-block CRC re-verification of the shipped K=1/K=2 bitstreams (6 block-level TSVs, 3 round logs, 1 report). Claim-to-file map in its `README.md`. |
| `CHECKSUMS.sha256` | 265 entries | — | sha256 of every other file in this package (LF newlines, `sha256sum -c` verifiable). |

Encoding: most round logs are UTF-8 with BOM (CRLF); `e1_*`, `e2_k2_program.txt`, `e1_reprogram.txt` are UTF-16 LE as produced by the capture tool. Files are byte-preserved except for the path redaction below.

## Sanitization applied (only these transformations)
1. Absolute paths pointing inside the authors' work tree (repo root under an external project directory) replaced with `<repo-root>` / `<path-redacted>`; EDA tool install paths replaced with `<path-redacted>`.
2. Machine hostname replaced with `<host>`.
No log content, timestamps, or measured values were altered. Raw round logs under `rounds/` contain no absolute paths and are byte-identical to the sources.

## Notes
- N1 — Per-round ping gate records: the paper's gate discipline (combined volume §3: burn-in → 25 s settle → 10×`ping 5` = 50/50 → discarded warmup round → post-round 5/5) is recorded per-session in the five `gates/20260814-*.md` session notes (e.g. smooth-feed-ceiling notes record 6× first-pass 50/50 and 4× 49/50-retest-50/50 events, each gate step-by-step), plus one raw ping-gate stdout (`e2_k2_ping_gate.txt`, 50/50 + 5/5 visible). Raw stdout for every individual round's ping was not retained as separate files in the source tree; the session notes are the primary records.
- N2 — Bitstreams (`.temp/bits/{k1,k2,k4}/*.bit`, ~6 MB each) are not duplicated here; a public reproduction repository including `bitstreams/` (fw `0x80110`) will be opened at the time of manuscript submission. This package's `build/` logs prove the lane-count binding and byte-identity with the images used on 2026-08-14.
- N3 — 24 of the 152 PASS logs have `warmup` in their filename. This is exactly the §10.4 authoritative sample (files with `expected=2403 && blocks_completed=2403`; the volume itself cites e.g. `e5_burst_4k_100_warmup1.txt` inside the §5 regression, line 353). Headline/crash-round files are unaffected.
- N4 — Excluded by design: everything from the retired simulation-era corpus (00.rules/04 in the writing repo: single-module simulation throughput, single-core LUT figures, dual-core aggregate, old compression-ratio table and its simulation file-table logs). Post-hoc token scan of the whole package for those retired figures: zero hits. Also excluded: 2026-08-08..10 debug-session logs (`pause*`, `k4_sustain_*`, `mlk_graft_*`, `.jou` journals) not cited by §10.

## Gate/discipline summary (for reviewers)
- PASS criterion in this dataset = `blocks_completed == 2403` + protocol reply / ping 5/5 — NOT content correctness (CRC gate off, combined volume §9.8; the manuscript states this).
- Both shipped bitstreams have unconverged timing (WNS −0.326 ns, 5 RGMII TX endpoints, identical for K=1/K=2; decode domain zero violations).

## N5 — Output-correctness evidence (added 2026-10-22)

`rounds/output-correctness/` — raw full-strip/per-file CRC logs and the three internal reports backing the
output-correctness paragraph in Sec. III (see its README for the claim-to-file map). Build relation is stated in the README.

### N6 — Shipped-bitstream re-verification (added 2026-10-26)

`rounds/output-correctness/2026-10-26-fw80110-blockcrc/` closes the earlier open item: the shipped K=1/K=2
bitstreams (fw `0x80110`) were re-verified block by block on 2026-10-26. Result: **2403/2403 blocks pass for
both configurations** (per block, FPGA word count equals the PC count and the post-XOR CRC32 equals the PC
reference; strip total 157,450,624 words), with `ping 5/5` after each configuration. Ten files: six
block-level TSVs (`crc_k{1,2}_part{1,2,3}.tsv`), three round logs, one report
(`2026-10-26-fw80110-blockcrc-reverify.md`). Two readout calibers of that build are on the record there: the
seven diagnostic checkpoint registers read back as zero (the CLI therefore reports a checkpoint mismatch and
the verdict rests on the word count and the final CRC), and the whole-strip single-stream word-count readback
reflects only the last block, which is why the evidence is given per block. Two further readout artifacts are on record (r020 P1-3/P2-7): in `crc_k1_part1.tsv` all 800 rows carry `verdict=FAIL, step3=NA` because the verifying script marks a row FAIL whenever the step line is missing from that early batch's log, while the row-level data are intact (`fpga_words==expected_words` and `fpga_crc32==pc_crc32` hold for 800/800 rows); and `2026-10-26-k1-blockcrc-verify.log` shows `OVERALL: FAIL (WORD_COUNT_MISMATCH, fpga_words=65535)` for the same whole-strip readback reason above. Neither is a decode failure; the per-block TSV columns are the verdict basis.

> 2026-10-24 清单收口（round2 P1）：`build/` 三件与 `programming/vivado_program_fpga.ps1.log` 现以 V08MAC/reports 当前副本在包（编程日志含 `AFTER_ILA_COUNT 0` 签名；e2/e3 含 `P_NUM_LANES bound to`）；SM-1 早期收录件系同批日志的旧拷贝，字节与现副本不同、已随工作区清理散失，包自洽以本清单+本校验单为准；`rounds/output-correctness/e7_fullstrip.log`、`e8_fullstrip.log`、`e8_perfile.log` 三件**已于 2026-10-26 自 095-submission 在包副本回收归位**（r020 P1-2；`cmp` 逐字节相等，CHECKSUMS 同步增补三条），原「散失、无法找回」表述作废，其逐块比对结论由该三件本体与同目录其余日志及本表 claims 支撑；CHECKSUMS 已按 LF 重算。
