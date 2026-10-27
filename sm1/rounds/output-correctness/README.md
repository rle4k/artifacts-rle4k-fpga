# Output-Correctness Evidence (added 2026-10-22, review loop round-1 item R-P1-1)

Board-level bit-exactness evidence for decoded output, referenced from Sec. III of the manuscript
("Output correctness itself has positive board-level evidence..."):

| Manuscript claim | Evidence in this folder |
|---|---|
| golden-strip round, on-board decoded strip bit-exact vs host golden, post-XOR CRC32 0xf87c04d1, 6/6 | report-2026-08-08-s5-s7-golden-throughput.md (S5 section, CRC table) |
| every block independently CRC-verified against PC reference (per-file, tiers annotated) | e4 report per-file table: 2403/2403 in 368.7 s (138-Mbps target tier); e7_perfile-summary.txt: 2403/2403 in 366.6 s (580 us / 200-Mbps tier); e8_summary.txt (PERFILE line): 2403/2403, tool-measured wall_s=367.8 s (the e8 report states 369.8 s command wall-clock incl. overhead; 640 us / 250-Mbps tier) |
| single-strip full reconstruction, 157,450,624 words, CRC32 0xeb3f04cb, 7/7 checkpoints | e7_fullstrip.log, e8_fullstrip.log (crc32 lines), e8_summary.txt |
| ceiling-rate tier attainment (target 138, achieved 136.0 Mbps) | report-2026-08-09-e4-system-ceiling.md |

Provenance: copied verbatim from the V08MAC engineering-report tree (reports/e7, reports/e8,
reports/*.md; S5-S7 report from the wt-59g working tree). The verification builds above are the 2026-08-08/09 firmware builds (fw 0x80104).

Notes (added 2026-10-26, r020 P1-3/P2-7): (i) In `2026-10-26-fw80110-blockcrc/crc_k1_part1.tsv` the 800 `verdict=FAIL, step3=NA` rows are a readout artifact of the verifying script (missing step lines in that early batch), not decode failures: `fpga_crc32==pc_crc32` and `fpga_words==expected_words` hold for 800/800 rows, as in every other TSV of the set. (ii) `2026-10-26-k1-blockcrc-verify.log` reports `OVERALL: FAIL (WORD_COUNT_MISMATCH, fpga_words=65535)` because the whole-strip single-stream readback returns only the last block's word count; the per-block TSVs, not this log line, are the verdict basis. (iii) `e7_fullstrip.log`, `e8_fullstrip.log` and `e8_perfile.log` (recovered into this package from the 095-submission copy on 2026-10-26) back the single-strip reconstruction row of the claim map above. (iv) P1-3b closed 2026-10-26 by an independent K=2 rerun on the board (directory `2026-10-26-fw80110-k2-blockcrc-rerun/`: burn log, post-burn fw readback `0x80110`, ping gates, console log, three TSVs; 2403/2403 pass): the rerun TSVs are byte-identical to `crc_k2_part{1,2,3}.tsv` apart from the header BOM. Note that the seven TSV columns carry no lane-count information, so byte-identity between `crc_k1_part2/3.tsv` and `crc_k2_part2/3.tsv` is a mathematical consequence of deterministic correct decoding, not evidence of file reuse; run logs and burn records are what pin the configuration, and the rerun directory now supplies both for K=2. The two on-the-fly console outputs (post-burn `hardware --version` and pre-round `ping 10`) were not captured live; the directory instead carries post-hoc re-checks taken 2026-10-27 08:32 under an unchanged, un-reburned board (`post-hoc-fw-version-readback.log`: firmware `0x80110`; `post-hoc-ping10.log`: 10/10).

| Manuscript claim | Evidence in this folder |
|---|---|
| per-block CRC on the shipped bitstreams, K=1 and K=2 (fw 0x80110, added 2026-10-26) | `2026-10-26-fw80110-blockcrc/` — 6 block-level TSVs (2403 rows each, word count + both post-XOR CRC32) plus the round log, summarised in `2026-10-26-fw80110-blockcrc/2026-10-26-fw80110-blockcrc-reverify.md`: K=1 2403/2403, K=2 2403/2403, strip total 157,450,624 words, post-round `ping 5/5` |

Shipped K=1/K=2 bitstreams (fw 0x80110, 2026-08-14) incorporate the 2026-08-10 decode-core input front-end pipelining rework (prefetch registers, input-FIFO bypass removal, combinational code output, rewritten stream-end drain interlock) plus feed/protocol-side and RX-FIFO revisions, and were re-verified block by block on 2026-10-26 with the same caliber as the fw 0x80104 rows. Two readout calibers of that build are on the record: the seven diagnostic checkpoint registers read back as zero, so the CLI reports a checkpoint mismatch and the verdict rests on the word count and the final CRC, and the whole-strip single-stream word-count readback reflects only the last block, which is why this evidence is given per block.
