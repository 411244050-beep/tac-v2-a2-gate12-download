# TAC Binance AI Pro — QBU/B5 68× UNKNOWN：真实截止点定位与阶段验收补丁

## 当前 Binance 原生工作区

用户最新实测报告：`strategy/strategy.py` SHA-256 `d372f76f9140de24526a6e46bc3d9ac9913787e2457108c2653fabf4e023be4e`；`strategy/spec.yaml` SHA-256 `224a599d5a6b21346b37893d0cf70e1f1d8022a619d7faaf8e335ce6c609b18a`。

已经真实接通：D1/D2→多周期 D3→冻结 Runtime-B3→原版 B4→QBU identity→Minor progress→B5 UPDATE008。308 根合成 15m replay 中，identity 68× KNOWN、Minor projection 68× TRUE、B5 68× UNKNOWN。独立正向 fixture 原版 B5 TRUE / QBU 1 / Primary 非空；**不是当前主循环已经走通正向 QBU**。无原生行情执行、无保存、无订单。

**你不缺新的 TEST_ONLY 授权，也不应停在重新分析原版源码。**

## 本轮实际增加、公开测试通过的三份输入

1. [V2 QBU/B5 同截止点适配](https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/native_candidate_v1/QBU_B5_ORIGINAL_EVIDENCE_CUTOFF_BINDING_V2.py) — 保留 V1 全部原版生产函数调用，只扩展返回的正式 `AnchorEpisode` 更新集合、完整 `RoleRuntimeOutput`、UNKNOWN/CONFLICT references、有效 Minor record/material record 计数及下一期 `RoleMemory`。**不能把这个独立 synthetic adapter 直接当作已获 real market provenance 的原生生产路径。**
2. [B5 原始 UNKNOWN 逐截止点诊断器](https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/native_candidate_v1/DIAGNOSE_ORIGINAL_QBU_B5_UNKNOWN_V1.py) — 输入已经生成的 `TAC_BASE_Update008Request` + `TAC_BASE_Update008Output`，不再计算/覆盖任何原版 QBU/B5 状态；只报告原版未知原因、输入快照血缘、候选和 Minor 记录、role unresolved、RoleMemory 身份、经济单元/QBU/Role 状态。永远 `entry_ready=False`，零订单。
3. [14 项原版差异与接线回归](https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/native_candidate_v1/test_qbu_b5_completion_regression_v1.py) — 在已完成 6 项原版模块差异上增加 LONG、SHORT、合法/冲突重武装、D2 终止 cutoff 原语义、跨截止点 RoleMemory/Anchor Episode 回写、不重复生成 QBU、UNKNOWN 原始原因透传、真实未认证 epoch fail-close。

[GitHub Actions CI 14/14 实际 PASS](https://github.com/411244050-beep/tac-v2-a2-gate12-download/actions/runs/42070038666)，合成测试，不是币安 native `validate_code` 或行情执行。

### 测试中的两个关键事实，不得改原版来掩盖

- 原版 B5 经济单元 ID 带来源截止点，会自然变化。跨截止点应比较原版 `RoleRuntimeOutput.prior_primary_continuity_preserved`、`RoleMemory.primary_qbu_identities`、`RoleMemory.primary_anchor_episode_ids`、以及有血缘的 QBU，而不是要求 `primary_unit_id` 字符串保持恒定。
- 原版 QBU Minor 生产函数的投影 `EvidenceState.TRUE` 只表示**四态计算完成**，不能等同于本截止点有实质进展。D2 Episode 终止 cutoff 排除进展 Pivot 时，返回 TRUE 且 `progress_evidence=()` 是可能且原版合法的。若不检查 `len(progress.progress_evidence)` 和 `material_progress`，就会把 68 次 TRUE 错报为 68 次正向 QBU 机会。不能更改冻结生产器对此的原始语义。

## 币安当前真实工作区必须完成的代码修改

1. **核验基线 SHA**，保留所有原生静态校验通过的 `strategy.py` / `spec.yaml` 和 B3/B4/QBU 实际截止点接线。不要把公共目录的旧 `strategy/strategy.py` 重新下载覆盖这个工作区。将 V2 adapter 和 diagnostic 作为增量源码添加到同文件，或按等价、无重复定义方式接入已有代码；保留旧 D3 节点唯一的 UPDATE007/008 规则。
2. 在现有多周期 D3 **真实循环**中，已经取得 `TAC_BASE_Update008Request` 和 `TAC_BASE_produce_update008(...)` 输出后，调用诊断器。对 68 次合成 UNKNOWN，按真实调用结果记录最多 20 条代表性 `original_b5_unknown_lineage_refs`、`original_role_unresolved_reasons`、`input_anchor_relinked_snapshots`、`input_material_minor_progress_records`、`original_b5_contact_zones` 与 `original_b5_produced_qbus`。不要事先猜测 UNKNOWN 是否全因缺少快照链接、Anchor 更新或角色条件。
3. 使当前 D3 循环对**每一个截止点**将原版 `output.episodes` 写回该原版 D3 Episode ledger，并按 `produce_update008` 的正式事务语义保存 `next_memory` 到同一 D2 趋势 Episode 的 RoleMemory。相同 cutoff/候选不得重复调用。**不能把未经完整 provenance 的 real prospective 记录写成正式 Episode**。
4. 对 **SHORT** 原版真实方向、事件重新武装（合法与冲突）、D2 `TrendEpisodeState.episode_start_cutoff` 和 **真实终止血缘**、正向 QBU Episode 回写与 RoleMemory 下一 cutoff，使用现有原版阶段运行同一组**完整 synthetic TEST_ONLY** fixture。测试的关键不是单独调用冻结生产函数，而是当前 D3 custom node 循环真正执行到 B5 TRUE 与非空 Primary，且下一 cutoff 不重复生成 QBU。若主循环仍全部 UNKNOWN，报告真正缺失的原版 source record，不能手工填入事件、contact zone、Minor 进展或 Role。
5. D2 Episode 终止 cutoff 不能由任意整数冒充：需从已经验证的 D2 `TrendEpisodeState` 的真实 cutoff history / terminal transition 中推导并核对 `episode_id`、`terminal_episode_id` 与 canonical segment。当前没有这种完整来源时只许 UNKNOWN / BLOCKED，不能推断 QBU 为正。
6. 运行本地正向/负向和原版输出对照。随后对当前真实工作区调用 Binance `validate_code`、`validate_spec`，记录新 SHA、输出 state 原因和真实调用次数。平台静态 PASS 不能冒称已保存或有实时行情数据。
7. 只有 QBU/B5 同一 D3 主循环正向回写、SHORT、重武装、终止血缘及 memory 截止点通过，才转入冻结 D4 四机制；其后依次 F9、正式 D5 十槽与 PORT007、签名 UPDATE014、D6。阶段不得空接线、不得变更入场/科研授权。

**永远保持** `TAC_LIVE_ENABLED=0`、528 原始标的全部不变、原生订阅关闭、没有账户访问/订单/Paper/Live；真实连续性未知始终 BLOCKED。当前交付仅为原版 QBU/B5 进一步验收的工程资源。
