# TAC 原版 B4 结构接受与恢复：实际源码安装与截止点绑定

## 当前币安工作区基线（最新用户报告）

```text
strategy/strategy.py SHA-256: db5b600c047b27c0be1ae821fd2d5b285a67aa50025ea6d57ba58ba1af2cbb69
strategy/spec.yaml SHA-256: c89ef014f408f39fa5e52ca11a29e763bbe0723594244c118dcba4ad734f8d85
```

这不是公开旧文件的指纹。币安已有实际的 Runtime-B3 内联＋四截止点回归调用链。严禁重新下载旧 `strategy.py` 覆盖当前 D1、D2、多周期 D3、B3 和 V2 batch 修改。当前无交易权限。

## 已验证并公开的四份具体文件

1. [原版 B4 科学定义内联源码](https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/native_candidate_v1/B4_FROZEN_ORIGINAL_PRODUCER_APPEND_V1.py)
2. [当前指纹门控自动安装脚本](https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/native_candidate_v1/APPLY_FROZEN_B4_SOURCE_V1.py)
3. [D2 Minor Pivot＋D3 Interaction → 原版 B4 证据的类型化绑定](https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/native_candidate_v1/B4_ORIGINAL_D2_PIVOT_EVENT_BINDING_V1.py)
4. [原版与内联版输出差异和绑定测试](https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/native_candidate_v1/test_frozen_b4_inline_parity_v1.py)

源码本体 SHA-256：`acdb9f7dcac5e4dee2cf012951c8c8eff51f59dcb9811304e833666bb0d8cdd3`。精确科学定义 AST 保留后的单文件追加段 SHA-256：`88b588848bad8661078ac8e928b50e49060dcb0389a0104709442e4b151984ba`。

真实公开 GitHub CI：
- [冻结 B4 原版 vs 同文件源码 5 项正负及四态对照](https://github.com/411244050-beep/tac-v2-a2-gate12-download/actions/runs/42057731647) **PASS**
- [SHA 门控防覆盖及原有 B3 科学 AST 保护](https://github.com/411244050-beep/tac-v2-a2-gate12-download/actions/runs/42057307797) **PASS**

B4 非科学兼容变换仅为移除已在原版单文件出现的包内类型 import、标准只读映射导入用等价内置 mappingproxy 类代替、去掉与冻结 B3 相同的 15m 时间常量定义；**B4 所有函数和类算法主体 AST 未改动**。无新技术指标、阈值、交易信号。

## 1. 首先实际安装 B4 到当前源码，而不是重复读取文件

请将安装脚本和 B4 append 源码分别下载到本地工作区 `tac_source/`，然后执行：

```bash
python tac_source/APPLY_FROZEN_B4_SOURCE_V1.py \
  --strategy strategy/strategy.py \
  --frozen-b4 tac_source/B4_FROZEN_ORIGINAL_PRODUCER_APPEND_V1.py
```

该命令**只校验** SHA/类型/定义冲突/AST，不修改文件。确认无异常后，加 `--commit`。脚本自动备份 `strategy/strategy.py.pre_b4_original` 后修改原文件。当前策略已不符合指纹时，**必须停止并对照最新变化**，不能硬改哈希门禁。

安装后请执行原生 `validate_code`、`validate_spec`，记录真实新 SHA，不把离线 CI 当作平台原生校验。

## 2. 本轮 B4 接线应该如何做

从每个 D3 候选实际的 `InteractionEvent`、D2 完整 MINOR Pivot 集合、冻结 B3 保存的分离／尝试时间来源及当前 exact closed CanonicalBar 构造原版 B4 requests，调用：

```text
produce_structural_acceptance(StructuralAcceptanceRequest(...))
produce_correct_side_recovery(CorrectSideRecoveryRequest(...))
```

必须保留以下四态：

- `TRUE`：源 Pivot 的因果顺序、进展和事件关系实际满足冻结规则；
- `FALSE`：原版明确计算出的否定，不可转成确认；
- `UNKNOWN`：无足够 Pivot、引用、延迟、连续性或者时间先后未证实；
- `CONFLICT`：同截止点角色歧义、来源/事件血缘冲突等。

`projection_to_info_value`、`safe_b4_consumer` 必须按原版转换：UNKNOWN/CONFLICT **不能**冒充 True，CONFLICT 必须暴露错误。B4 的正向输出仅是可供 UPDATE007 的输入证据，尚不能作为 D4 或最终交易权限。

上传的绑定文件只在**完整合成 TEST_ONLY 来源证明**下运行正向场景；当真实 prospective epoch 不完整时它提前返回 `BLOCKED_EPOCH_CONTINUITY_UNPROVEN`，不会假装执行真实 B4 或改写系统状态。后续真实绑定必须从原生采集／连续性的可信实际记录取得正向证据，不能把 TEST_ONLY 许可伪装为正式来源。

**严禁**人工将 `structural_acceptance=True`、`correct_side_recovery=True`、`history_complete=True` 硬编码进生产路径。B4 必须在原 D3 的正确截止点、正确候选身份，且只消费原版 D2 已确认的源 Pivot。

## 3. 明确验收

- 已在**当前** `strategy.py` 中安装冻结 B4 定义，旧版 Runtime-B3 四截止点回归测试仍过；
- 在真实 D3 节点的同截止点代码中完成 B4 生产函数调用，而不仅是“文件存在”；
- 使用完整合成样本验证 B4 TRUE、FALSE、UNKNOWN、CONFLICT 并与原版逐项对照；
- 缺失真实 epoch、来源失真、重复和错误 Pivot／时间戳时 fail-closed；
- 原生 `validate_code` / `validate_spec` 真实结果、修改后两个 SHA、可执行实际阶段和未接阶段写入交接记录；
- B4 完成后才继续冻结 QBU 同事件身份＋Minor 进展、有效 B5 role/qualified-use 和原版 D4 四机制，随后接 F9、正式 D5 十槽、UPDATE014、D6。

当前无运行、无审核保存：`TAC_LIVE_ENABLED=0`；528 标的、TEST_ONLY 参数、无账户、无订单、无 Paper/Live 全部保持。
