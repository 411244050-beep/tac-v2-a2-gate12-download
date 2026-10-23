# TAC AI Pro 原版 D1 公共下载区

这个目录仅发布**原版源码文件**，不是可直接运行的策略，也不包含账户密钥或实盘授权。

- **完整 ZIP**：`TAC_original_91_sources_verified_for_AIPro_20261023.zip`，内含 91 个原始 `strategy_rc1` 源码及校验信息。
- **单文件 Python**：`TAC_D1_CanonicalBar_original_verified.py`，就是 `strategy_rc1/d1_data_math/canonical.py` 的字节一致副本。
- **单文件纯文本**：`TAC_D1_CanonicalBar_original_verified.txt`，用于不能上传 `.py` 的应用。
- **下载 SHA-256**：`SHA256SUMS_DOWNLOADS.txt`。

校验标准：压缩原件 `36111563b5778513d5803a3ec7c2b86f967a71d915fbcfd9bee5cb4ebebf8174`；原始 `canonical.py` SHA-256 `a647c3f66448dbf1cb322fd7561fdc74d3584ce2c5ef1c7450dd63837ef75b62`。

本目录通过 `build_downloads.py` 在 GitHub Actions 中从已固定的 91 文件 tar.xz 和原始哈希清单生成 ZIP、PY 和 TXT。生成前按文件名及 SHA-256 逐个验证 91 个原始文件。

**仅供 Binance AI Pro 新建独立 D1 验证策略。** 不覆盖运行中的 BTC 信号策略或原 528 探针 r1。原版数学依赖 `decimal.Decimal` 与 `fractions.Fraction`，AI Pro 环境能否导入仍待独立检查；不得擅自用 float 代替。

`TAC_LIVE_ENABLED=0`。未授权实盘或下单。

## 原版 D1 精确运算对照（合成数据）

- [3 组正常样本和 5 组异常阻断样本（JSON）](TAC_D1_original_exact_parity_vectors_synthetic_v1.json)
- [直接调用冻结的 91 文件 ZIP 进行本地对照检查（Python）](verify_original_d1_parity_v1.py)
- [公开回归 CI](https://github.com/411244050-beep/tac-v2-a2-gate12-download/actions/workflows/verify-tac-d1-original-parity-v1.yml)

运行检查（纯本地、无交易、无账号）：

```bash
python3 verify_original_d1_parity_v1.py
```

对照数据属于明确标记的合成 K 线，不是交易所历史行情；原版 `CanonicalBar` 对 `close_time` 的直接要求是大于 `open_time`，流入口必须另行验证 `k.T == k.t + 899999` 且 `k.x=True`，直接传入来源的 `k.t/k.T`，不得自行取整或使用 float。通过这项回归不能推断币安 AI Pro 运行时已通过，也不授权真实或模拟下单。
