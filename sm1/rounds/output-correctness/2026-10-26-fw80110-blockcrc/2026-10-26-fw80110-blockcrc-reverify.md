---
IOF: RYIOF_DWS20261026010
title: fw 0x80110 主比特流逐块 CRC 复验（P0-1 闭合）
class: 实验报告
version: v1.0.0
status: done
date: 2026-10-26
memo: K=1/K=2 各 2403/2403 逐块与 PC 参考 CRC 一致；闭合「吞吐数在新流、正确性证据在旧流」的断层
---

# fw 0x80110 主比特流逐块 CRC 复验（2026-10-26）

## 1. 目的与判据

闭合 `094-reviews/cards/P0-2-fw0x80110-blockCRC板测复验.md` 的断层：吞吐数字来自 fw 0x80110，
而此前的板级正确性证据全部产自 fw 0x80104。

判据（沿用该卡）：**2403/2403 块逐块与 PC 参考 CRC 一致 + ping 门禁**；日志入 SM-1。

## 2. 条件

| 项 | 值 |
|---|---|
| 器件 | XCKU040-FFVA1156-2-I（工业级 −2） |
| 位流 | `.temp/bits/k1/rle4k_lan_top.bit`（K=1，08-14 09:43）、`.temp/bits/k2/rle4k_lan_top.bit`（K=2，08-14 09:12） |
| 固件 | `hw.firmware=0x80110`（两配置同一固件号，burn_time=0x20260810） |
| 烧写 | `scripts/program_fpga.ps1`，Vivado 2022.2；烧后探针 `AFTER_ILA_COUNT 0 / AFTER_VIO_COUNT 1`（known-good 签名） |
| CLI | `.temp/wt-59g/rle4k_cli/build/Release/rle4k_v8.exe`（与固件同 tag 构建；主树 CLI 与本 bit 不兼容，见 §5b） |
| 主机 | Windows 工作站，Npcap 二层裸帧，EtherType 0x4B52，iface `\Device\NPF_{0F60CD7D-...1170}`，PC MAC `EE:EE:EE:EE:B6:4A`，FPGA MAC `00:0A:35:00:01:02` |
| 数据 | `D:\outputs\rle4k_1`（2403 块，height 1 230 083，block_height 512，stride 65 536，压缩 30 792 855 B） |
| 方法 | **逐文件** `verify file <block>`：每块独立成流，主机侧 PC 参考解码算 post-XOR CRC32 后与板上 CRC 比对 |

## 3. 结果

| 配置 | 块数 | 通过 | 失败 | 每块字数 | 全条带字数和 | 轮后门禁 |
|---|---|---|---|---|---|---|
| K=1 | 2403 | **2403** | 0 | fpga = expected（满块 65 536，末块 33 152） | 157 450 624 | `ping 5/5`，fw 0x80110 |
| K=2 | 2403 | **2403** | 0 | 同上 | 157 450 624 | `ping 5/5`，fw 0x80110 |

- 每块判据：`FPGA word_count == PC word_count` 且 `FPGA crc32 == PC crc32`（post-XOR）。
- 全条带字数和 157 450 624 与数据集几何 1 230 083 × 65 536 / 512 一致。
- 耗时：约 62 s / 800 块，全量约 186 s / 配置（逐块握手挂钟，非吞吐口径）。
- 原始台账：`reports/2026-10-26-fw80110-blockcrc/crc_k{1,2}_part{1,2,3}.tsv`（逐块 7 列，含两侧 CRC）。

## 4. 与该 fw 读数口径相关的两个已知现象

**(a) 诊断检查点读回为零。** 该构建的 7 个 `diag_crc` 检查点寄存器读回全 0，CLI 因此将
「Step 2 CRC Checkpoints」判为 0/7，整体结论报 `DIAG_CHECKPOINT_MISMATCH`（即
AGENTS 记的 CLI 伪 FAIL）。本次判定因此以 Step 1（字长）与 Step 3（最终 CRC）为准，
不采信 Step 2。**不是解码错误，是诊断寄存器在该构建上未接。**

**(b) 整条带单流的字数读回只反映最后一块。** `send folder ... --parallel` 后 `crc` 查询得到
`lines=259 words=33 152`，即末块（259 行 × 128 字/行 = 33 152 字）；早前 fw 0x80104 上
同一测法得到 `words=157 450 624 / crc32=0xeb3f04cb`（e4 报告）。故 **0x80104 的整条带单流逐位
口径在 0x80110 上不可复现**，0x80110 的正确性证据只能以逐块口径给出。

**(c) 非 parallel 的多块单流会在首块后停。** `verify folder`（不带 `--parallel`）在同一 bit 上
只解到 512–771 行即 `done=1`，加 `--parallel` 才完整走完（`blocks_completed=2403`）；
`--parallel` 走的是 send-only 路径、不做 CRC 轮询。历史 K=1/K=2 吞吐轮均带 `--parallel`，
与此一致。

## 5. 复现命令

```powershell
$env:PATH = "C:\Windows\System32\npcap;$env:PATH"
$cli = ".temp\wt-59g\rle4k_cli\build\Release\rle4k_v8.exe"
$a = @("--iface","\Device\NPF_{0F60CD7D-397C-4595-813D-2A381F9E1170}",
       "--local-mac","EE:EE:EE:EE:B6:4A","--target-mac","00:0A:35:00:01:02","--timeout","30000")

.\scripts\program_fpga.ps1 -BitFile ".temp\bits\k1\rle4k_lan_top.bit"   # 核对 AFTER_ILA=0 / AFTER_VIO=1
& $cli @a hardware --version      # fw = 0x80110
& $cli @a ping 10                 # 10/10

# 逐块 CRC（每块独立流；分 3 批跑，规避单次会话过长）
.\.temp\verify_perfile.ps1 -Skip 0    -Count 800 -OutTsv .temp\crc_k1_part1.tsv
.\.temp\verify_perfile.ps1 -Skip 800  -Count 800 -OutTsv .temp\crc_k1_part2.tsv
.\.temp\verify_perfile.ps1 -Skip 1600 -Count 803 -OutTsv .temp\crc_k1_part3.tsv
```

## 6. 结论与后续

- **P0-2 卡判据达成**：fw 0x80110 上 K=1/K=2 各 2403/2403 逐块 CRC 与字数全部一致，轮后链路可恢复。
- 稿件 §3.4 已按此改写（v0.4.23I）：删除「主比特流补跑 CRC 是投稿前行动项」，
  改为已复核，并披露 (a)(b) 两条读数口径。
- SM-1 需追加本目录日志并重算 CHECKSUMS/MANIFEST（本次未动 CHECKSUMS，待按包纪律执行）。
