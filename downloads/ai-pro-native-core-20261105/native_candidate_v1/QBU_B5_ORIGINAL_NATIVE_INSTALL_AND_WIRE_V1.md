# Binance AI Pro — TAC 原版 QBU 同事件身份 / Minor 进展 / B5 正式源码接线 V1

当前状态：Runtime-B3 和原版 B4 已在币安工作区多周期 D3 循环中真正接通并通过静态校验；**本交付尚未在币安原生工作区应用**。公开 GitHub Actions 不是币安已保存或真实行情执行。

## 1. 实际当前基线和源码（请先核对）

- `strategy/strategy.py` 最新用户报告 SHA-256：`b272cfaba80bc1535ba45a30602ad0e813d26de992128022be769634a1ff3b1f`
- `strategy/spec.yaml` 最新用户报告 SHA-256：`1777cac51bf3d8eb1d1d82dadde1d4d89e337a069ed7baff511f56d0ac7166e4`
- 只有当前实际文件 SHA 与给定基线一致时，才能自动安装；否则逐项对照真实工作区改动，禁止覆写。

**已生成可公开 HTTP 下载的具体文件：**

1. [冻结原版 QBU/B5 三模块静态命名空间单文件源码](https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/native_candidate_v1/QBU_B5_FROZEN_NAMESPACED_ORIGINAL_APPEND_V1.py)
2. [QBU 同事件 ID + 15m MINOR 进展 + B5 UPDATE008 的真实原版函数调用适配](https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/native_candidate_v1/QBU_B5_ORIGINAL_EVIDENCE_CUTOFF_BINDING_V1.py)
3. [当前策略指纹门控原位安装器](https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/native_candidate_v1/APPLY_FROZEN_QBU_B5_SOURCE_V1.py)
4. [原版模块 vs 同文件展开的差异测试](https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/native_candidate_v1/test_frozen_qbu_namespaced_parity_v1.py)
5. [原始冻结源码和完整来源 SHA 列表](https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/native_candidate_v1/QBU_B5_FROZEN_NAMESPACED_ORIGINAL_APPEND_V1.manifest.json)

原版三份冻结源码 SHA-256：
- B5/D4 基础 `authoritative_d3_b5_d4_base_runtime_producers_v1.py`: `6dd33000694a2f41713c9474070b6946ad23c622018bcf03fccd9d385e28cecd`
- QBU 同事件身份：`a8510ff4f17001afe97072c8829288d5a7ba1ca20f8a60c152b1425994c780f8`
- QBU Minor 进展：`b63a3c24fc7111d21e9e00bc55efcdd76c41a4b8d78b4290a1b314159059c4b5`

**生成的 88,056 字符单文件附加段 SHA-256：**

`9d1ae768305555a39958586d519d535098bc3e1c247a1cbe850d72c490dc10c1`

科学等价准备过程没有删减任何原有 76 个类／函数的判断分支。解决重复全局名称的静态前缀为 `TAC_BASE_`、`TAC_ID_`、`TAC_PR_`，例如不同模块同名 `bind_update008_request` 会成为两个互不覆盖的显式名字。原始模块仅作包导入展开、模块作用域名称引用重写，QBU 的冻结语义和参数未改。

**离线 CI：**
- [原版 QBU/B5 6 项差异测试](https://github.com/411244050-beep/tac-v2-a2-gate12-download/actions/runs/42063791978) **PASS**：同事件 KNOWN、重叠身份、未来事件 CONFLICT、历史 UNKNOWN、Minor material TRUE / nonmaterial / no-prior / 不完整历史、基础 B5 UPDATE008、合成 QBU→B5 真实函数调用；
- [SHA 门控原位安装脚本](https://github.com/411244050-beep/tac-v2-a2-gate12-download/actions/runs/42064034903) **PASS**：错误来源 SHA 拒写、原有 D1/B3/B4 AST 不改、合并文件普通 Python 可编译、零订单。

此证明是 **源码与合成输入的差异测试**，不是 Binance 原生 `validate_code`，更不是实时数据或交易证据。长期持久化 `TAC_BASE_AuthoritativeD3B5D4BaseRuntimeV1.export_state`／`restore_state` 的类身份和 importlib 解析仍未在平台证明。

## 2. 先实际安装：不准重复只分析依赖

在已经校验的原工作区中，把三个生成文件下载至 `tac_source/`，保留原来的 `strategy/strategy.py`、`strategy/spec.yaml`。

**校验、零写入：**

```bash
python tac_source/APPLY_FROZEN_QBU_B5_SOURCE_V1.py \
    --strategy strategy/strategy.py \
    --frozen-qbu tac_source/QBU_B5_FROZEN_NAMESPACED_ORIGINAL_APPEND_V1.py \
    --qbu-bridge tac_source/QBU_B5_ORIGINAL_EVIDENCE_CUTOFF_BINDING_V1.py
```

检查输出 `source_written=false`、原 AST 未改、原版 QBU SHA 与最新当前策略基线匹配后，运行同一命令加 `--commit`。它会写入 `strategy/strategy.py.pre_qbu_b5_original` 备份并且实际修改当前 `strategy.py`。若脚本报告不匹配，**禁止随意改基线指纹绕过**；应先核实真实差异。保留原版 B3、B4 多周期 cutoff 的唯一性，不要新建第二条相互竞争的 F9 路径。

安装后必须调用一次真实 Binance 原生 `validate_code` 及 `validate_spec`，报告准确错误和 SHA；特别核对平台是否支持展开后的顶层 `importlib` 与标准映射处理。不允许把 GitHub CI PASS 冒充平台验证。

## 3. 把 QBU/B5 真正接入当前 D3 截止点循环

安装仅证明**源码存在**，不是接线完成。本轮应实际修改当前 D3 custom node，使其在已有原版 B3、B4 之后运行：

1. 从已执行的原版 D2 获得**真实已确认的全部 15m MINOR Pivot**和趋势 Episode ID、起始截止点、可选终止截止点；从原版 D3 获得候选 `MathematicalBoundaryCandidate`、前态 `CausalBoundarySnapshot`、`AnchorEpisode`、完整 `InteractionEvent` 历史、按候选连续性表和 canonical segment ID。
2. 使用冻结 `frozen_d3_parameters(current_partial_parameter_snapshot())` 的 `theta_test`、`theta_progress`，不能借用未科学冻结的 D2 TEST_ONLY theta 改写 QBU 阈值。
3. 在**同截止点原版事件处理完成后**，先调用 `TAC_ID_project_negotiation_identity(TAC_ID_NegotiationIdentityRequest(...))`，把 KNOWN 事件身份使用 `TAC_ID_bind_update008_request` 绑定到 `TAC_BASE_Update008Request`，禁止预填身份映射。
4. 再调用 `TAC_PR_project_qbu_progress_evidence(TAC_PR_QBUProgressProductionRequest(...))`，使用 D2 原版 Minor Pivot 流、实际起始/终止时间与历史覆盖证据。TRUE 才允许 `TAC_PR_bind_update008_request`。UNKNOWN/CONFLICT 不可升级成 TRUE，必须阻断或返回原状态。
5. 只有上述输入具备**真实可认证的同一 prospective epoch 完整性及重启连续性**，才进入 `TAC_BASE_produce_update008`（用于 B5 Contact Zones、QBU、经济单元和 Primary/Secondary Role）。未认证历史时暂时 **BLOCKED**，不得伪造 `history_complete=True`。同一截止点 RoleMemory 按原版事务规则保存，禁止重复消费或未证明持久的跨重启恢复。
6. 先按现有 `_tac_original_qbu_b5_synthetic_cutoff_v1` 函数，用完整合成 TEST_ONLY fixture 跑正向、反向、事件重叠、重武装、Minor nonmaterial、重复／未来 Pivot、缺 epoch 负例。该 adapter 会在 real market mode 中直接阻断，不能直接作为 real market 生产路径。
7. 同一截止点 D3 不能为同一候选重复执行 UPDATE-007/008；QBU/B5 必须消费 **已经确定的** D3 事件和 Anchor，不得手造事件身份或趋势腿。当前 B4 合成样本全 UNKNOWN，不能据此伪造 B5 正向市场证据。

改动之后执行 **真实原生** `validate_code`、`validate_spec`，记录修改后两个 SHA、真实进入的 QBU/B5 函数调用次数及原版差异输出。接线完成再推进正式 D4 四机制、F9、当前 D5 十槽／PORT007、UPDATE014 和 D6。若阶段未接通，不标为完成。

## 4. 交易绝对边界

`TAC_LIVE_ENABLED=0`，528 冻结标的全部保留，原生行情订阅关闭。无账户访问、交易授权、订单、Paper/Live、审核保存或真实 dry-run。TEST_ONLY 用于工程测试，不代表原 D2 OPEN 参数已科研冻结。所有 QBU/Role/Entry 值仅来源于冻结原版条件和实际观察证据。

本轮你的目标：**不只下载或安装文件，必须实际修改 D3 cutoff 节点执行 QBU/B5 原版函数，完成合成差异测试与原生校验。**
