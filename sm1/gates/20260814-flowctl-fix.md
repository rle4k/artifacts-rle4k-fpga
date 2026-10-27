---
exp: 20260814-flowctl-fix
branch: exp/20260814-flowctl-fix
head: 993cb9b
base: exp/20260814-k1-nodram @ eb22fc1（NUM_LANES=1，实测 56.41 G / 176.69 Mbps）
worktree: .temp/wt-59g（复用已生成 IP 的沙箱；K=1 与 K=2 的 bit 均已存档）
status: done
created: 2026-08-14
verdict: H-NOFIX — 崩溃阈值未动（181.5 vs 基线 179.79 ± 3.10，落在同一区间），`end_sync_ms` 仍死平，PAUSE 最小保持时间不是根因；按 §5 停手，不叠第二个补丁
---

# EXP 20260814-flowctl-fix — 修每块接收缓冲排空缺陷，测真实 lane 容量

## 1. 目的

三轮测量已经确定：**板卡的吞吐天花板不是解码算力，是一个接收侧缓冲/流控缺陷。**
证据有三条，彼此独立：

1. K=1 的崩溃阈值随主机发包形状摆动 **58.6%**（113.34 / 140.87 / 179.79 Mbps），
   算力上限不可能随主机发包形状变化。
2. `end_sync_ms` 从未增长。K=2 在 99 → 293 Mbps 这 3 倍跨度上死平在 6.2–7.7 ms，
   K=1 最坏 9.2 ms 且非单调。**解码全程没落后过**，最坏滞后只占整轮的 0.65%。
3. 起作用的机制不是「平滑」：sendqueue 放大 4 倍到 4096 KiB 阈值纹丝不动，
   而在**块与块之间插入空档**换来 +26%。⇒ 瓶颈在**每块**的接收缓冲排空，
   不在总带宽，也不在队列深度。

失效方式是整轮 wedge（`blocks_completed=0`、失联），不是优雅降级——没有背压，
只有溢出。修好它有两个产出：论文能拿到真正的 capacity 数；产品侧不再有猝死模式。

## 2. 假设与预测

**H-FIX**：修复后板卡在超过原阈值时**背压而非猝死**，喂料继续上抬时
`end_sync_ms` 开始单调增长，最终吞吐停在某个平台。该平台 = 真实 lane 算力。
预测 K=1 平台 > 56.41 G；早先供需模型给的参考值是 62 G（196 Mbps），仅作参考，**不去迁就**。

**H-NOFIX**：修复后阈值不变或仍猝死 ⇒ 根因判断错误，回到 §1 重新取证，不叠补丁。

## 3. 基线（对照的唯一参照）

| 项 | 值 | 出处 |
|---|---|---|
| K=1 可持续 | **176.69 Mbps / 56.41 G / 17.67%** | 附录 B |
| K=1 崩溃阈值 | 179.79 ± 3.10 Mbps（2/2 复现） | 附录 B |
| `end_sync_ms` | 6.3 → 9.2 ms，非单调，最坏占 0.65% | 附录 B |
| K=2 可持续 | 295.52 Mbps / 94.34 G / 29.55% | 附录 B |
| K=2 崩溃阈值 | 295.87 ± 0.35 Mbps（2/2 复现） | 附录 B |

基线**具备分辨力**：K=1 在 176.7 通过、182.9 崩溃，区间 3.5%，任何改善立刻可辨。

分支从 `exp/20260814-k1-nodram` @ eb22fc1 开出，所以与 56.41 G 那次测量之间
**只差这个修复**，是干净的单变量对照。

## 4. 唯一变更

`src/rle4k_pause_ctrl.v`：**给 XOFF 加一个最小保持时间，防止它被自己的 XON 提前撤销。**
只动流控逻辑；未碰解码器、`src/vendor/**`、`npcap-sdk/**`；`NUM_LANES` 仍为 1
（综合日志两处 `Parameter P_NUM_LANES bound to: 1`）。commit `993cb9b`，父提交即基线 `eb22fc1`。

```diff
@@ -18,7 +18,12 @@ module rle4k_pause_ctrl #(
     parameter [15:0]  P_PAUSE_QUANTA   = 16'hFFFF,
     // Retrigger period while congested, in tx_clk cycles.
     // Default ~800 µs @ 125 MHz — well under max-quanta hold (~33.5 ms).
-    parameter integer P_RETRIG_CYCLES  = 100_000
+    parameter integer P_RETRIG_CYCLES  = 100_000,
+    // Minimum XOFF hold after the last congestion assertion, in tx_clk cycles.
+    // 25_000 @ 125 MHz = 200 us: long enough for the PAUSE frame to reach the
+    // peer and take effect, and long enough for rx_async_fifo0 (2048 x 8 B) to
+    // drain on its 15.625 MHz read side (~125 MB/s => ~25 KB in 200 us).
+    parameter integer P_MIN_HOLD_CYCLES = 25_000
 ) (
@@ -42,6 +47,27 @@ end
 assign congested_sync = c1;

+reg [31:0] hold_cnt;
+always @(posedge tx_clk) begin
+    if (tx_reset)
+        hold_cnt <= 32'd0;
+    else if (congested_sync)
+        hold_cnt <= P_MIN_HOLD_CYCLES[31:0];
+    else if (hold_cnt != 32'd0)
+        hold_cnt <= hold_cnt - 32'd1;
+end
+
+wire congested_hold = congested_sync | (hold_cnt != 32'd0);
+
 reg        congested_d;
 reg [31:0] retrig_cnt;
@@ -52,20 +78,20 @@ always @(posedge tx_clk) begin
-        congested_d <= congested_sync;
+        congested_d <= congested_hold;
-        if (congested_sync && !congested_d) begin
+        if (congested_hold && !congested_d) begin
-        end else if (!congested_sync && congested_d) begin
+        end else if (!congested_hold && congested_d) begin
-        end else if (congested_sync) begin
+        end else if (congested_hold) begin
```

同 commit 另含**门禁**改动（不进比特流，不影响对照）：
`tb/tb_rle4k_pause_ctrl.v` 增加 `latency1` 模式与可变 sink 容量、
`scripts/run_sim_pause_ctrl.tcl` 增加 `PAUSE_PEER_LAT` 开关。见 §6.3。

## 5. 判据（跑之前定死）

- **H-FIX 成立**：同时满足两条 ——
  (a) 在原崩溃阈值（179.79 Mbps）以上仍能完成整轮，`blocks_completed=2403`；
  (b) 继续上抬喂料，`end_sync_ms` ≥ 14 ms 且连续 ≥2 档单调上升。
  此时最后一个 3/3 通过点的 Gbit/s **可作为单 lane 算力写入论文**。
- **部分成立**：阈值上移但仍猝死、`end_sync` 仍平 ⇒ 只更新可持续吞吐数值，
  措辞仍为「特定发送配置下的可持续吞吐」，**不得**改称容量。
- **H-NOFIX**：阈值未动 ⇒ 根因错误，停下重新取证，**不叠第二个补丁**。

前置门禁（改 RTL 的硬约束，缺一不可）：

- **先 TB 后上板**。修改后必须先过既有仿真门禁（`scripts/run_sim_*.tcl`），
  且新写的用例要能在**未修复**的 RTL 上先红（`14-v08mac-testbench-validity.mdc`）。
- 综合后核对 `Parameter P_NUM_LANES bound to: 1`，确认未误改 lane 数。
- 烧写后核对 `AFTER_ILA_COUNT 0 / AFTER_VIO_COUNT 1`。
- 上板前 10 × `ping 5` 门禁须 100%；每次运行后 `ping 5` 须 5/5。
- 测量口径与附录 B 完全一致（块门控喂料 + `--sendqueue-chunk-kib 1024`），
  否则与 56.41 G 不可比。

## 6. 执行记录

| 时间 | 事件 |
|---|---|
| 15:0x | graphify 定位 RX 链路与 PAUSE 触发源；读 `tb_rle4k_rxchain.v` 头注释 |
| 15:2x | 定位根因（§6.2）：`rle4k_pause_ctrl` 在复合拥塞信号的下降沿立刻发 XON |
| 15:3x | 实现 §4 最小改动；`git diff` 仅 31+/5-，首 3 字节 `2F 2F 20`（无 BOM） |
| 15:4x | 门禁红/绿对照（§6.3）：**红了，但没有全绿**——4.4× 改善，非通过 |
| 15:36 | commit `993cb9b`；Vivado 2022.2 分离进程起构建 |

### 6.1 先排除的候选

| 候选 | 结论 | 依据 |
|---|---|---|
| `rle4k_cdc_fifo_36` 占用/almost-full 阈值 | **不是**触发点 | `cdc_almost_full = stg_almost_full \| cdc_almost_full_raw`，且 staging FIFO（`rle4k_sync_fifo_36`，`P_ADDR_BITS=12`）的 `pause_level = DEPTH − 2048`，即**半满**就报拥塞。这一路本来就是「早警告」，不是「已溢出」 |
| `STREAM_BLOCK_START` 处理 / 每块暂存路径 | **不是**丢帧点 | `rle4k_stream_adapter_v8` 的 `rx_ready` 在 `S_RX_IDLE`/`S_RX_RECV` 之外拉低，是**真背压**，会一路顶到 `app_rx_ready → pause_congested`，不会静默丢弃 |
| K=4 调度器块派发 / `rle4k_ring_window` | **与本轮无关** | `accept_ready = ~accept_conflict` 常高；且 `NUM_LANES=1` 时 `lane_busy` 把块串行化，32 槽窗口远未用满 |
| PAUSE 是否端到端接通 | **是接通的**（推翻「`pause_seen=0` ⇒ 没接」的直觉） | 本分支 `master_wrapper_v8.v:466-467` 把 `rle4k_pause_ctrl` 的 `pause_req/pause_val` 接到 TEMAC；`:553` 用 `32'h6000_0000` 强制置 0x40C 的 TX/RX 流控使能位。**不是没接，是接了不起作用** |
| `axis_dwidth_converter_1` 的 `s_axis_tready` 悬空 | **本分支已修** | `:390` 已接 `rx_dwc_s_axis_tready` 并在 `:563` 并入 `pause_congested`。`tb_rle4k_rxchain.v` 头注释里「line 377 悬空」是**过期描述**，基线 eb22fc1 已含该修复 |

### 6.2 根因：PAUSE 用「已满」当触发源，并且立刻用 XON 撤销自己

`master_wrapper_v8.v:561-566` 的拥塞信号是这样拼出来的：

```verilog
wire pause_congested =
    app_rx_congested |            // staging 半满（真·水位）
    (~rx_dwc_s_axis_tready) |     // DWC 拒收 —— 瞬时「已满」
    (~m_axis_tready3) |           // rx_async_fifo0 满 —— 瞬时「已满」
    (~m_axis_tready4) |           // rx_packet_fifo0 满 —— 瞬时「已满」
    ((~app_rx_ready) & (proto_rx_valid | m_axis_tvalid4));
```

后四项都是**瞬时满标志**：只要下游排掉**一个字**，`tready` 就回高，拥塞随即消失。
async FIFO 读侧在 15.625 MHz，一个字 64 ns；`tx_clk` 是 125 MHz。
也就是说这个信号会以**几个时钟周期**的粒度反复起落。

而 `rle4k_pause_ctrl`（修复前）的行为是：

- 上升沿 → 发 XOFF（`pause_val = 0xFFFF`）
- **下降沿 → 立刻发 XON（`pause_val = 0`）**

一个 64 字节 PAUSE 帧本身要 512 ns 上线，还要对端 NIC 解析生效，往返在**微秒到数十微秒**量级。
于是 XON 紧跟在 XOFF 后面几个周期发出，对端**几乎同时**收到一对 XOFF/XON，净效果 ≈ **零背压**。
**PAUSE 机器接通了、也确实在发帧，但在线上不产生任何减速。**

这一条同时解释了主报告里那三条互相独立的证据：

1. **阈值随发包形状摆动 58.6%** —— 背压既然无效，能不能扛住就只取决于主机突发的瞬时速率
   与 RX 缓冲（`rx_async_fifo0` = 2048 × 8 B = 16 KB）之比，而不取决于平均速率。
2. **`end_sync_ms` 死平** —— 失效模式是**丢帧**，不是**滞后**。丢一帧 `STREAM_DATA`
   之后该块永远数不满 `cfg_block_height` 行，`block_done` 不来、`lane_busy` 不清，
   adapter 停在 `S_BLOCK_ASSIGN` 且 `rx_ready=0` ⇒ 整轮 wedge、`ping 0/5`。
   解码器从头到尾没落后过，所以 `end_sync_ms` 没有任何理由增长。
3. **sendqueue 加大 4 倍无效、块间空档 +26%** —— 队列深度改变的是主机侧排队，
   不改变上线后的瞬时速率；块间空档直接给 RX 缓冲留出排空时间。**唯一有效的是排空时间**，
   与「背压不工作」完全一致。

仿真里可以直接看到「自己撤销自己」：未修复 RTL 在 8 次 XOFF 之间夹了 **5 次 XON**（§6.3）。

### 6.3 门禁：红了，但修复后**没有全绿**（如实记录）

既有 `run_sim_pause_ctrl.tcl` / `tb_rle4k_pause_ctrl.v` 在缺陷 RTL 上是**绿的**，
原因正是 `14-v08mac-testbench-validity.mdc` 说的那类构造：它建模的对端是**零延时**的
——`pause_req` 一拉，主机同一拍就停。零延时下「XOFF 后立刻 XON」当然无害，
于是这个门禁在结构上无法暴露本缺陷。

新增 `latency1` 模式：对端延迟 `PEER_LAT = 24` 个 `tx_clk` 周期才响应（真实 NIC 至少要
64 周期把 PAUSE 帧串行化，24 是刻意取的保守低估）。结果：

| RTL | sink 容量 | 结果 | offered | dropped | XOFF | XON |
|---|---|---|---|---|---|---|
| **未修复**（`HEAD:src/rle4k_pause_ctrl.v`） | 8（余量 4 < 延时窗 24） | **FAIL（红）** | 141 | **84** | 8 | **5** |
| 已修复 | 8 | FAIL | 30 | **19** | 7 | **0** |
| 未修复 | 64（余量 32 > 延时窗 24） | PASS | 542 | 0 | 66 | 16 |
| 已修复 | 64 | PASS | 62 | 0 | 61 | **0** |

如实结论，不粉饰：

- **红是真红**：未修复 RTL 在余量小于「延时 × 带宽」时丢 84/141 拍（59.6%），
  且日志里能数出 5 次自我撤销的 XON。修复后 XON 归零，丢帧降到 19 拍（**4.4× 改善**）。
- **但没到零**，所以**这不是一条通过的门禁**，只是一个被量化的改善。剩下的 19 拍是
  「缓冲余量小于延时带宽积」的固有损失，任何 PAUSE 控制器都救不回来。
- **余量充足时（64）两版都是零丢**：未修复版靠 XOFF/XON 高频振荡把水位钉在水线上
  （66 次 XOFF/16 次 XON），也能不丢。所以本修复的收益**依赖于板上实际余量与
  PAUSE 往返之比**，而这个比值仿真里给不出可信数值 —— 必须上板测。
- 既有零延时模式（`honor0`/`honor1`）在修复后仍全绿，无回归。
- 另外提醒后来者：`tb_rle4k_rxchain.v` 在线速下的 64% 丢帧（120 帧丢 77）**不能**用来门禁
  本修复 —— 那个 TB 里根本没有 PAUSE 回路（没有 TX 通路回到激励源），
  它测的是「sink 能否吃住线速」，与背压是否生效无关。

### 6.4 板级复测（口径与附录 B 完全一致）

构建：Vivado 2022.2 分离进程，25 min 06 s，`write_bitstream completed successfully`；
综合日志两处 `Parameter P_NUM_LANES bound to: 1`；**无** `[filemgmt 20-742]`；
布线后 `WNS = -0.326 / WHS = +0.022`（与基线同量级的既有 setup 违例，非本轮引入）。
产物存 `.temp/bits/flowctl-fix/`（bit + routed timing + utilization + ltx）。
烧写核对 `AFTER_ILA_COUNT 0 / AFTER_VIO_COUNT 1`；`fw=0x80110`。
上板前 10 × `ping 5` = **50/50**。喂料一律 block-gated + `--sendqueue-chunk-kib 1024`，
`R = round(130480 / P)`（与附录 B 的 `R = 1.25 × 104384 bit / P` 同式），全程未用 unpaced。
每轮 stdout 存 `reports/e7_flowctl_P<P>_r<n>.txt`（含全部崩溃轮）。

预热轮（**已丢弃**，仅列作记录）：`P=560 R=233` wire 176.540 / dc 1431.6 / es 10.6 / blk 2403 / PASS。

| P (µs) | R | 实测 wire_Mbps | dc_ms | **es_ms** | blocks | 后置 ping | 判定 |
|---|---|---|---|---|---|---|---|
| 560 | 233 | 176.115 | 1433.2 | **8.8** | 2403 | 5/5 | PASS |
| 560 | 233 | 176.509 | 1431.8 | **10.6** | 2403 | 5/5 | PASS |
| 560 | 233 | 176.441 | 1429.9 | **8.2** | 2403 | 5/5 | PASS |
| 545 | 239 | 181.544 | 9452.1 | 8070.3 | **0** | **0/5** | **WEDGE** |
| 545 | 239 | 181.331 | 9428.2 | 8044.8 | **0** | **0/5** | **WEDGE** |
| 545 | 239 | 180.943 | 9446.6 | 8060.3 | **0** | **0/5** | **WEDGE** |

（崩溃轮的 `es ≈ 8050 ms` 是等待超时常量，不是真实滞后，不入 `end_sync` 序列。）

**与基线逐项对照：**

| 项 | 基线 eb22fc1（附录 B） | 本轮 993cb9b | 变化 |
|---|---|---|---|
| 最高 3/3 通过线速 | 176.690 Mbps | **176.441**（中位；3/3） | −0.14%，**未动** |
| 对应解码吞吐 | 56.41 Gbit/s | **56.30 Gbit/s** | 未动 |
| 复现崩溃阈值 | **179.79 ± 3.10** Mbps | **178.69 ± 2.25**（176.44 通过 / 180.94 崩溃，3/3 复现） | **落在基线区间内，未动** |
| 通过点 `end_sync_ms` | 9.2 ms | **8.8 ms**（8.2 / 8.8 / 10.6） | 未动，**仍死平** |
| 崩溃签名 | `blocks_completed=0`、`ping 0/5`、需重烧 | **完全同构** | 未变 |

崩溃后板卡失联，`ping 0/5`，重烧 `.temp/bits/k1/` 基线 bit 后恢复 **25/25**。

## 7. 结论

**判定：H-NOFIX。** 按 §5「阈值未动 ⇒ 根因错误，停下重新取证，不叠第二个补丁」，本轮就此收手。

三条判据逐条对账：

1. **(a) 不成立** —— 在原崩溃阈值（179.79 Mbps）以上没能完成整轮：`P=545`（180.9–181.5 Mbps）
   三次全部 `blocks_completed=0`，且崩溃签名与基线逐项同构。
2. **(b) 不成立** —— 通过点 `end_sync_ms` 中位 8.8 ms（基线 9.2 ms），既没到 14 ms，
   也谈不上单调上升；只有 3 个通过样本且区间与基线重叠。
3. 阈值中位从 179.79 变到 178.69，**在两侧不确定度内属同一个值**，不构成「部分成立」的上移。

**所以：PAUSE 的 XOFF 被自己的 XON 提前撤销，虽然确实是一个真实缺陷（仿真里 §6.3 有
4.4× 的量化改善、XON 自我撤销从 5 次降到 0 次），但它不是这个吞吐天花板的限制项。**
修掉它对板级阈值没有可测量的影响。

### 7.1 这轮排除掉了什么（对下一个人有用的部分）

- **不是** PAUSE 未接通（`master_wrapper_v8.v:466/553` 确实接了并强制使能 0x40C）。
- **不是** PAUSE 保持时间太短（本轮把它从「几个周期」拉到 200 µs，阈值不动）。
- **不是** `axis_dwidth_converter_1` 的 `s_axis_tready` 悬空（基线 eb22fc1 已修）。
- **不是** `rle4k_cdc_fifo_36` / staging 的 almost-full 水位设得太晚（staging 半满即报）。
- **不是** ring window / K=4 派发（`NUM_LANES=1` 下 32 槽窗口远未用满）。

⚠ 同时要指出：**`pause_seen=0` 这条线索本身不可靠。** 该字段在本轮所用的
block-gated / batch 通路里并不被真正采样，所以它的 0 既不能证明 PAUSE 没发，
也不能证明 PAUSE 没生效。任何后续实验不要再把它当证据。

### 7.2 下一步应该往哪查（不在本轮范围，未实施）

阈值对**主机突发形状**敏感（58.6%）、对**平均带宽**不敏感、`end_sync_ms` 全程死平，
而背压路径已被本轮基本排除。剩下最可疑的是**丢一帧就整轮猝死的那个不可恢复性**本身，
而不是「为什么会丢」：

- `rle4k_stream_adapter_v8` 的 `S_BLOCK_ASSIGN` 在 `lane_busy` 永不清零时会永久停住
  （`rx_ready=0` ⇒ 板卡彻底失联）。给它加超时强制释放 lane，可把整轮 wedge 变成
  「短一点的 `blocks_completed`」，即先拿到**优雅降级**，再谈提阈值。
  本轮曾实现该改动，为守住「一实验一变量」而**回退未测**，见 §6 时间线。
- 若要继续追丢帧本身，应先在 `rx_async_fifo0` 写侧取真实占用（IP 需开
  `axis_wr_data_count`，代价是重生成该 IP），把「已满」换成「水位」再测一轮。
