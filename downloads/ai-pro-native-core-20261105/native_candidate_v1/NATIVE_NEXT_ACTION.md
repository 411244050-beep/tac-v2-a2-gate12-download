# TAC 原版 Binance AI Pro 原生构建交接（有真实源码文件）

## 立即使用的两个工作区文件

- [strategy/strategy.py](./strategy/strategy.py)
- [strategy/spec.yaml](./strategy/spec.yaml)

AI Pro 可直接 HTTP GET 的公开源文件：

```text
https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/native_candidate_v1/strategy/strategy.py
https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/native_candidate_v1/strategy/spec.yaml
```

原版完整 106 文件输入包仍可获取：

```text
https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/TAC_AI_PRO_NATIVE_CORE_SOURCE_UPLOAD_V1.zip
```

## 本次比上轮新增的真实工作成果

1. **生成了物理文件** `strategy.py` 和 `spec.yaml`，不是空工作区，不是让 AI Pro 从头重读再写的计划。
2. `strategy.py` 前 243,903 字符保留原始展开版 D1–D6/F9 源码原样（SHA-256 `a3c8af708d29c82afe7bd89f04f9434838bb1bfdea95936791d5bf33b28aa708`）；后面附加明确隔离的 Binance 原生候选绑定层。最新正式 D5 十项政策和 UPDATE-014 实现继续以完整 ZIP 中的正式源码为准；历史 PORT-007 unresolved 不能充当现在的组合分配实施。
3. 全 528 冻结身份在代码中显式列出，未降范围。
4. 有实际 `@node('std:fetch')`、`@node('custom:tac_original_core')`、`@workflow`、`main()` 候选定义；`kline_stream` 的形参名字须以币安原生平台工具实际契约验证，不得把代码通过普通 Python 编译报告成平台 SDK 已验证。
5. 在 GitHub Actions 完成实际 `strategy.py` Python 编译、与原始源码前缀字节一致校验，以及 300 根闭合 15m 数据的原版 D1+D2 算法运行；并验证拒绝 float 输入、原始参数 OPEN/LOCKED、不给出任何入场许可。日志：https://github.com/411244050-beep/tac-v2-a2-gate12-download/actions/runs/42020156227
6. 当前文件**尚不完整**：只绑定 D1+D2 真实计算；D3→D4→F9→D5→UPDATE014→D6 仍须接通，且完整 528 订阅、实际原生审核及运行均未验证。候选文件总长约 258,165 字符，是否受大小限制，必须由平台真实 validate 结果判断。

## 币安 AI Pro 现在执行的事项（无需重新询问 TEST_ONLY 授权）

1. 把上面两个真实 HTTP 源码写入工作区对应位置 `strategy/strategy.py`、`strategy/spec.yaml`，读取后报告 SHA/字节数。若实际平台无法以 HTTP 获取，返回**准确错误**；不要再称仓库中没有源码，也不要默默用简化替代策略。
2. 以此已存在的原版源码为基础，先运行 `validate_code` 和 `validate_spec`，报告大小上限、SDK 导入、装饰器、流 API 参数和 Spec 节点依赖的具体错误。此阶段不要以修兼容为名删除 D3–D6 原版规则。
3. 仅在平台确认导入/源码长度后，做**规则等价重构**：D3 原始 UPDATE000/002/007/008、D4 的 UPDATE011 四机制、F9 真阶段适配器、正式 10 槽 D5 与新版 PORT007、签名 UPDATE014 最终许可及 D6 保护。不得把“函数存在”当成“阶段已接通”。每接一段对照原版原始输出并保持 528 顺序。
4. TEST_ONLY 值仅注入原版 D2 的 `StructuralScaleParameters` 与构造器，不改变 `current_partial_parameter_snapshot()` 的 OPEN 或 LOCKED 状态；`theta_stop=1.0` 仅为不可执行的工程假设值。正式交易权限始终关闭。
5. 只有获得平台真实支持、完整核心实现与一致性证据，才调用 `audit_code`；`validate_spec` 不是保存。保存成功必须有策略 ID/版本，随后才能根据无交易权限做原生 dry-run。
6. 所有输出必须指明：真实执行到的 stage、未绑定的 stage、有没有原生 SDK 验证、是否保存、是否运行、有无市场数据。严禁把 GitHub Actions 通过冒称 Binance 原生运行。

交易绝对边界：`TAC_LIVE_ENABLED=0`，不授权账户调用、订单、Paper/Live 或实盘资金使用。未完成正式 D5/D6/UPDATE014 风控与持续状态证据前不得打开任何交易权限。

## 与旧方案的界线

不要再回到 `pragmatic_core_v1` 的简化三指标观察器；它不是原始 TAC。这个候选也是**尚未完成的忠实迁移工作区文件**，不是可直接部署的生产策略。其功能扩大必须依据原版和正式冻结规则，不得自创交易逻辑。
