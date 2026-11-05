# TAC 原版 D3 多周期原生增量补丁 — 仅限 TEST_ONLY

## 基线与发布结果

币安 AI Pro 最近一次自行报告的工作区基线（不要覆盖）：

- `strategy/strategy.py` SHA-256：`380d170d058580dd0da2b2fb8ab40e79236e3aec741918a7b90debc1d3dfda0c`
- `strategy/spec.yaml` SHA-256：`5065cae2e33e131fd0ae2155471a5891456cef9b2a6ead954d0bb8da4f284356`
- 3 个节点，2 条边，原生静态校验 PASS；**非已保存或运行**。

新文件：`D3_MULTITF_ORIGINAL_CAUSAL_PATCH_V1.py`，SHA-256：
`1fb81b14349e0dc081f10c9b4977c9b62abf000cb0026e2be32ebc981b6c7d7d`。

直接下载：https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/native_candidate_v1/D3_MULTITF_ORIGINAL_CAUSAL_PATCH_V1.py

GitHub Actions 源码身份与实际原版调用测试：https://github.com/411244050-beep/tac-v2-a2-gate12-download/actions/runs/42028927575

## 真实实现范围

`_tac_original_multitf_d3_testonly(symbol, raw_rows)` 接受明确带 `is_closed=True` 的原始精确闭合 15m 连续数据；不得缺省生成闭合标志。调用**原版** `CanonicalBar`、`canonicalize_15m`、`aggregate_completed_htf`、`EMARecurrence`、`ATR14Recurrence`、`SupertrendRecurrence`、`D2ReferenceSkeleton`、`D3ReferenceSkeleton`。1H/4H 只在 4/16 根完整 15m 同源段全部闭合时提供来源周期新候选；候选注册位于 source bar 结束之后，当前 15m 观察先 UPDATE000 前态，再 UPDATE002/007/008。

在 400 根合成上行 15m K 线中实际执行：

| 原版数学与状态函数 | 数量 |
|---|---:|
| 15m、1H、4H 完整来源 K 线 | 400 / 100 / 25 |
| 三周期可用候选快照 | 1055 / 208 / 10 |
| 三周期前态几何 UPDATE002 | 1052 / 820 / 128 |
| UPDATE007、UPDATE008 调用 | 各 2000 |
| 无机制 D4 `update_011` fail-closed 诊断调用 | 351 |
| B5 正式 Primary / D4 正式确认 / ENTRY_READY / 订单 | 0 |

9 个本地专项测试通过，发布文件通过公开 GitHub Actions 再次运行（记录 `TAC_ORIGINAL_D3_MULTI_TF_SOURCE_PASS`）。该结果**不是**平台原生运行或完整策略的证明。

## 币安 AI Pro 应执行的实际工作

1. 先获取并核对**当前真实工作区**两文件 SHA。如果与上述值不同，先确定并保留实际变动，不要强行覆盖回旧 SHA。
2. 将公开的 `.py` 文件作为**附加源码**放到当前 `strategy/strategy.py` 原版定义之后。不能替换已通过的 V2 `batch`、`interval` 参数、`from/to` 边、只读映射兼容或之前的 15m D3 路径。不要添加新的假交易信号。
3. 检查现有 3 节点 / 2 边的真实工作流和 Spec；在**当前 D3 custom node 内**新增对 `_tac_original_multitf_d3_testonly(symbol, exact_rows)` 的调用，输入必须来自已校验 `batch` 逐条闭合 K 线所累积的、严格有 `is_closed=True` 的相同 symbol 数据。原版 HTF 聚合不可由自造 HTF K 线替换。
4. 在不触及账户、订单、Paper/Live 的条件下，先做本地负向与原版输出对照，验证前态截止点、HTF 聚合时点、来源 tf、D3 status 和候选 ID。之后才调用币安 AI Pro **实际** `validate_code`、`validate_spec`。
5. `B5` 当前只有零输入、零角色时的原版 fail-closed 路径；原版 Qualified Boundary Use 需**真实已完成的回归、结构接受、后续 Minor 进展以及接触区**。没有这些，就不能构造 Primary、Secondary，也不能制造 D4 的 Normal/FalseBreak/Platform/Deep 机制证据。
6. `D4 update_011` 本文件仅对已有 D3 事件执行**无机制诊断分支**，并固定 `critical_information_known=UNKNOWN`，输出必须没有确认候选。它不代表原版 D4 四种机会机制已接线。后续要从真实 D3 与 D2 事件链获取有效证据再逐机制验收。
7. F9 / 正式 D5 十项 / UPDATE014 / D6 仍然 NOT_CONNECTED；若尚未接全，不调用正式交易或审核保存，不得报告运行成功。未证实的 1024 根历史重放、528 全订阅、故障重启／持久化问题始终标为未验证。

**TEST_ONLY 不得被升级为科研 FROZEN**。所有原版源码算法定义不得改动；任何改变都须记录 AST/输出对照。`TAC_LIVE_ENABLED=0`，行情订阅开关维持当前禁用状态，账户、订单及 Paper/Live 权限为零。

## 保留变更

这一文件是可编译的**增量实现**，不能将其原样当作完整 `strategy.py` 或单独策略运行。只有在当前币安临时工作区原样附加并绑入真实 D3 节点，经原生校验后，才算本步平台接线完成。返回真实最新 SHA、Spec 节点依赖、局部计算输出及剩余阻断，不要重复询问已经批准的 TEST_ONLY 参数。