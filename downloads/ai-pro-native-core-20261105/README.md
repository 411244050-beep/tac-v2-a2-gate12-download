# TAC original core → Binance AI Pro (native migration input, 2026-11-05)

[Direct public ZIP download](./TAC_AI_PRO_NATIVE_CORE_SOURCE_UPLOAD_V1.zip)

Raw ZIP (unauthenticated): https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/TAC_AI_PRO_NATIVE_CORE_SOURCE_UPLOAD_V1.zip

SHA-256: `25b969f1ed50c07798fe72f2eb4213011bde824677d5f2c0fdb25fe0f41efe7c`

This source-only package contains 106 verified files: the SHA-pinned original TAC D1–D6/F9 science reference, its frozen 91-file archive and module dependencies, the updated D5 ten-slot risk authority, UPDATE-014 final entry guard, the frozen ordered 528-symbol universe and validation manifests.

**It is input to build a Binance AI Pro native `strategy/strategy.py` and `strategy/spec.yaml`, NOT a saved/deployed/running strategy.** The main source is over 60k characters; Binance AI Pro must perform rule-preserving refactoring and actual native validation/audit. Do not invent missing parameters or replace the core logic with EMA/ATR/SuperTrend voting. Only user-approved signal-only, no-account, no-orders verification is in scope. `TAC_LIVE_ENABLED=0`.

This public download is intentionally available without GitHub login. No API keys or account contents are included.
