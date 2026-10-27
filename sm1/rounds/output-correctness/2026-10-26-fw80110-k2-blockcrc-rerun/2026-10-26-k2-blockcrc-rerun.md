---
IOF: RYIOF_DWS20261026013
title: fw 0x80110 K=2 逐块 CRC 独立复跑（r020 P1-3b 闭合）
class: 实验报告
version: v1.0.0
status: done
date: 2026-10-26
memo: 应 r020 P1-3b（10-26 K=2 台账无 run log），板卡在线重烧 K=2 比特流复跑 2403 块，run log 全程留档
---

# fw 0x80110 K=2 逐块 CRC 独立复跑（2026-10-26 23:02–23:06）

## 1. 目的

r020 审项 P1-3b：`2026-10-26-fw80110-blockcrc/` 的 `crc_k2_part{1,2,3}.tsv` 无对应 run log 与烧写日志，且 part2/part3 与 K=1 同名件 sha 全等，档案上无法区分独立复跑与复用。本次在板卡上重烧 K=2 比特流完整复跑，run log、烧写日志、轮后门禁全部留档。

## 2. 条件（与 10-26 复验同口径）

| 项 | 值 |
|---|---|
| 器件/位流 | XCKU040-FFVA1156-2-I；`.temp/bits/k2/rle4k_lan_top.bit`（08-14 09:12 件，复跑前重烧） |
| 烧写 | `scripts/program_fpga.ps1`，Vivado 2022.2；`AFTER_ILA_COUNT 0 / AFTER_VIO_COUNT 1`（known-good），日志 `2026-10-26-k2-program.log`（脱敏后） |
| 固件确认 | 烧后 `hardware --version` 读回 `0x80110`，`burn_time=0x20260810`（现场 stdout 未单独留存；板卡未断电未重烧条件下，2026-10-27 08:32 事后补读 `post-hoc-fw-version-readback.log` 读回同值 `0x80110`，与烧写日志同场） |
| 轮前门禁 | `ping 10` → 10/10（现场 stdout 未单独留存；同条件事后补验 `post-hoc-ping10.log` 2026-10-27 08:32 → 10/10；当场门禁结果见 `run-console.log` 各批 0 失败与轮后 `post-round-ping.log` 5/5） |
| CLI/数据 | `.temp/wt-59g/.../rle4k_v8.exe`；`D:\outputs\rle4k_1` 2403 块（同 10-26 件） |
| 方法 | `verify_perfile.ps1` 逐文件独立成流，分 3 批（Skip 0/800/1600，Count 800/800/803），批次参数与汇总行见 `run-console.log` |

## 3. 结果

| 批 | 块数 | 通过 | 失败 | 耗时 |
|---|---|---|---|---|
| part1 | 800 | 800 | 0 | 59.6 s |
| part2 | 800 | 800 | 0 | 59.7 s |
| part3 | 803 | 803 | 0 | 58.9 s |
| 合计 | **2403** | **2403** | **0** | ≈178 s |

轮后门禁：`ping 5` → 5/5（`post-round-ping.log`）。每块判据同 10-26：`fpga_words==expected_words` 且 `fpga_crc32==pc_crc32`（post-XOR）。

## 4. 与 10-26 台账的关系（P1-3a 澄清）

- 本次三份 TSV 与 10-26 的 `crc_k2_part{1,2,3}.tsv` **数据区逐字节一致**（唯一差异为表头 BOM），即 10-26 K=2 台账数字获得独立复跑背书。
- **TSV 同构原理**：台账 7 列（block/两侧 words/两侧 crc32/step3/verdict）不含 lane 数信息，K=1 与 K=2 解码同为正确时输出确定且相同，故 `crc_k1_part2/3.tsv` 与 `crc_k2_part2/3.tsv` 同 sha 是**确定性解码下的数学必然，不构成复用证据**；能区分配置的只有烧写记录与 run log，本目录即为 K=2 配置下带完整 run log 的独立证据。
- 10-26 的 `crc_k1_part1.tsv` verdict 列为 FAIL 系该构建诊断检查点未接引发的 step3 伪判定（10-26 报告 §4a），其两侧 CRC 与字长列全对，不影响正确性结论。

## 5. 结论

**P1-3b 闭合**：fw 0x80110 的 K=2 逐块正确性具备独立 run log、烧写日志、烧后 fw 读回与轮前后门禁的完整证据链；SM-1 `CHECKSUMS.sha256` 已含本目录全部文件。
