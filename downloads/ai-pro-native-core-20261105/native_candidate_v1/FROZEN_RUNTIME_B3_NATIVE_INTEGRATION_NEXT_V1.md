# TAC 原版 Runtime-B3 回归证据生产：币安 AI Pro 增量接线

**基于最新币安 AI Pro 原生静态校验通过的当前工作区；不得用旧文件替换。**

- Binance 当前 `strategy/strategy.py` SHA-256：`377a25ef6831764b7e9f1ef1703898552b531d537b0c2f5d2e55ded4bcf410fc`
- Binance 当前 `strategy/spec.yaml` SHA-256：`24f1ac99ac7619feb3481f2e64965ef51ca12e0e80554ddc34d6485a66c49eb9`
- Binance 上轮真实校验：3 节点、2 边、`validate_code` 错误列表全空、`validate_spec valid=true`。尚未保存/部署、无真实行情。
- 全部 528 标的、TEST_ONLY 和 `TAC_LIVE_ENABLED=0` 均保持不变。

## 两个已经发布并实际测试的源码

1. 冻结的 Runtime-B3 F3 价格回归生产算法（直接追加到 **同一** `strategy.py` 的原版源码之后）：

   https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/native_candidate_v1/RUNTIME_B3_FROZEN_ORIGINAL_PRODUCER_APPEND_V1.py

2. 把 F3 生产结果接入原版 D3 `UPDATE-007/008` 的无交易调用适配器（位于第一段新增函数之后）：

   https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/native_candidate_v1/RUNTIME_B3_TO_ORIGINAL_D3_UPDATE007_BRIDGE_V1.py

**原始生产科学文件**：`provisional_shadow_v1/runtime_b3_price_driven_return_production_state_v1.py`，源 SHA-256：

`d2ea2d356862f0685adac35f8e3e1c44cec4cf904c623231e6e4c948fcbe4526`

经 AST 等价清除原包相对导入后，附加源码 AST-SHA256：

`d8dec00ab2d5d9c5723dd041b21ad95a1d83dcb244ee83a1558bd631607399cc`

**实测源码及输出差异测试**（4 项全部通过）：
https://github.com/411244050-beep/tac-v2-a2-external-runtime/actions/runs/42034750899

**实际 B3→D3 四截止点正向证明**（公开 CI PASS）：
https://github.com/411244050-beep/tac-v2-a2-gate12-download/actions/runs/42035411711

对照输出：
- 截止点 1：`ARMED_FROZEN_CURRENT_CUTOFF_NO_RETURN` → D3 `ARMED`，无 Anchor
- 截止点 2：`RETURN_QUALIFIED_LATCHED_NOT_CONSUMABLE_SAME_CUTOFF` → D3 仍 `ARMED`，**当期不使用回归**
- 截止点 3：`LATCHED_RETURN_CONSUMABLE` → D3 `INTERACTION_ACTIVE`，原版生成 Anchor Episode
- 截止点 4：`RESET:INTERACTION_NO_LONGER_PENDING` → D3 `RESOLVED`，保留 Episode

所有测试数据为显式合成 fixture，`D4=NOT_AUTHORIZED`，`ENTRY_READY=False`，无账户、订单、Paper/Live。

## 当前工作区实施步骤（必须原位补丁，绝不覆盖）

1. **先验证上面的基线 SHA**；若与当前实际工作区不同，逐项保留最近变动。
2. 在现有 `strategy/strategy.py` 中源码定义区**追加**两个文件的内容，保留其原始算法主体。不要重建 `strategy/spec.yaml`，除非节点输入/边需要具体修正。
3. 当前多周期 D3 逐 bar 的控制时序必须是：
   `UPDATE-000` 只看该观察 bar 开盘前候选 → `UPDATE-002` 捕获当前已闭合 15m 价格几何 → 运行原版 D2 该截止点的 `UPDATE-005/006` 并获取**真实当前趋势** → 运行本补丁冻结 Runtime-B3 生产器 → `_tac_frozen_b3_update007_step(...)` 完成原版 `UPDATE-007/008` → 当前 bar 收盘后才注册新的 D3 来源周期候选。
4. **每个 symbol/连续数据段的回放**只能建立一次 `RuntimeB3PriceDrivenReturnProducerV1()`；不得每根 bar 初始化，否则 F3 武装状态丢失。也不能让多个同标的 F3 消费者拆分事件。原版 F3 Producer 的 `process_batch` 保持原样，真正的 `RuntimeB3Observation` 来自原版 prebar snapshot、原版 UPDATE-002 geometry、已确认的 D2 episode、当期原始 `CanonicalBar`。
5. `history_complete=True` **不是因为这次的局部连续 300/400 根合成样本就自动成立**。只能由完整的 TEST_ONLY prospective epoch、逐根闭合、无 dropped、无中断的可信状态证明；缺少证明必须保持阻断。重启后无持久检查点、历史丢失，不能误当连续策略状态。
6. 对相同 `snapshot.candidate_id` **只执行一次 UPDATE-007/008**。本适配器已经执行这两步，现有多周期 D3 循环不能再额外重复调用旧分支；否则事件、Anchor、QBU 状态可能重复写入。
7. **不要提前将 `structural_acceptance`、`correct_side_recovery` 填 True**：本补丁保持为 `None`，仅解决具有正式来源规则的 F3 PriceDrivenReturnEvidence。下一阶段的原版 D2→B4 结构接受生产器在现有 GitHub 源文件 `provisional_shadow_v1/d2_to_b4_d4_causal_evidence_producers_v1.py` 中；QBU 同一事件/Minor 进展冻结源分别为 `qbu_same_event_negotiation_identity_production_binding_v1.py` 和 `qbu_material_trend_side_minor_progress_production_binding_v1.py`。不得重新设计这三条科学契约。
8. 将 TEST_ONLY 4 截止点正向用例、缺少武装状态、跨 cutoff、重复事务、缺少历史来源、Float OHLC、结构信息未确认、重启状态丢失等负例与原版对照，然后运行币安真实 `validate_code` / `validate_spec`。
9. 继续将已冻结的 B4 结构接受、QBU、B5 角色接至 D4 四机制；然后接 F9 最新 PORT007、正式 D5 十项、UPDATE014 和 D6。不得用 GitHub Actions 测试当作 Binance native runtime；**也不得把 F3 返回成功当作 ENTRY_READY**。

## 科学与交易权限

这次不会改变任何 `FROZEN` 科研参数，也不会把 3 个 OPEN theta 改成 FROZEN。原版 `theta_stop=LOCKED`、正式 D5、UPDATE014 最终授权不变。**原生订阅依旧关闭；只有在用户另外授权实际订阅并且平台能力已验证时才可能启用。** `TAC_LIVE_ENABLED=0`，不访问账户，不下单，不启用 Paper/Live。当前只允许源码准备、静态原生校验及离线用例。

尚未取得保存策略 ID、版本或实际原生行情证据，继续据实报告。
