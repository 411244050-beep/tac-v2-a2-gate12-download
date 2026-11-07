# TAC V6 PRIVATE REPO CREATED — external AI Pro NONSTATE canary, zero K-line

2026-11-07. TEST_ONLY, SYNTH-only. The user has **explicitly approved** a dedicated private GitHub repository for future TAC V6 engineering checkpoints, but has **NOT authorized upload of any serialized state or execution of 83-bar recovery**.

## VERIFIED BY CHATGPT'S OWN CONNECTED GITHUB INSTANCE (not AI Pro)

- Exact repository `411244050-beep/tac-v6-private-checkpoints`, GitHub metadata reports `visibility=private`, `default_branch=main`, `archived=false`. Connected ChatGPT GitHub identity has Admin/Pull/Push. Never infer same access inside separate Binance AI Pro execution.
- A tiny public-safe NONSTATE text file was written and read back using the connected GitHub app: `canary/chatgpt-connector-private-access-20261107.txt`; Git blob `900e2d3b29ce5044564f84f21a940570d51512f6`, readback exact 305 ASCII characters. It contains only safe test labels. It was written to this **Private** repo, NOT the public download repo. This confirms connected GitHub integration can write to this private repository ONLY, and does not validate AI Pro network/secrets.
- This task file itself is a NONSECRET instruction in a separate public handoff repository. Do not upload any private state to the public handoff repo. Do not assume repo visibility stays Private forever: verify immediately before every future write.

## ACTUAL LOSS & EXACT GATES

The prior AI Pro temporary runtime was reclaimed. No V6 checkpoint bytes remain. `BACKUP_LOST=YES`, `RESTORABLE_BAR82=NO`, `RESTORABLE_BAR83=NO`, `DURABLE_BACKUP=NO`.
- Historical bar82 full V6 SHA256 `b342a5d01d3fb094ef350ef47ac23c51bcad408b14459590795b7d0a38a203fa` (13,683,812 bytes).
- Historical bar83 full V6 SHA256 `a074d852158c99e5eccedde1643f19ef6453ef4064cce6fc481cfb762b023617` (13,937,694 bytes).
- Current reconstructed input generator is NOT original source: `fixture_gen_reconstructed_83_20261107.py` SHA256 `ba961b8c043596babf8e8ef7dcee71914ffa1d8b7adbacde729b7069adbb781f`, and exact 83-input fingerprint `102186c82d3f08e944e848e95d35e27e67907b4c779c9f79e067778529e6c027` agrees with historical input manifest. Matching input fingerprint is not a new restore of V6 state.
- Original frozen source and 528-symbol rules unchanged. Independent `PORT007_UNRESOLVED_PRODUCTION_ALLOCATION_BLOCKED` (F9 UPDATE-015) and `BLOCKED_D3_B3_JOINT_PERSISTENCE` remain.

## NEXT AUTHORIZED BOUNDARY: nonstate AI Pro connectivity test ONLY

1. First check inside the **actual separate Binance AI Pro sandbox**, not ChatGPT: is a supported GitHub integration/connector available with permissions to the exact new private repo? If YES, prefer explicit platform-provided authenticated GitHub action and do not ask user to paste credentials. If NO, check whether platform offers a protected secrets/environment-injection mechanism. If neither method available, return `AI_PRO_PRIVATE_GITHUB_AUTH_UNAVAILABLE` and STOP; do not paste tokens in ordinary chat.
2. If user opts for a GitHub fine-grained token, the USER must create and scope it to ONLY `411244050-beep/tac-v6-private-checkpoints`, minimal Contents Read/Write permission, short expiration. Token must be supplied only through a secure secrets configuration accessible to AI Pro; do not expose in text output, logs, URL query strings, Git remote URL or public manifests. No tokens in any public repo. Never request GitHub account password.
3. With credentials safely configured, try HTTPS TLS-verified API access from AI Pro. Fetch private repository metadata in the authenticated context and REQUIRE `full_name=411244050-beep/tac-v6-private-checkpoints` and `private=true` (or verified `visibility=private`). If not verified, STOP `PRIVATE_REPO_VISIBILITY_OR_ACCESS_BLOCKED`. Never silently fallback to existing PUBLIC `411244050-beep/tac-v2-a2-gate12-download`.
4. Create a NEW small NONSTATE canary in **private repo only**, e.g. `canary/ai-pro-runtime-access-20261107.txt` with random test-only nonce and source label (no state bytes, no keys, no PII). Read it back in the same AI Pro sandbox using authenticated method; compare exact returned byte length and a fresh local SHA256 of the actual payload, not the Git Blob SHA. Record `HTTP/API response class`, remote URL path (nonsecret), `private=true`, bytes, SHA, and write+read status, never log Authorization header. If any step fails STOP `AI_PRO_PRIVATE_SINK_NOT_VERIFIED`. Optional cleanup only once proof recorded.
5. A passing CANARY proves AI Pro can write and read this private GitHub location. It does **not** yet prove a durable state backup exists, does not verify end-to-end encryption/decryption, and does not authorize 83-bar reconstruction. Report `AI_PRO_PRIVATE_CANARY=PASS`, `CURRENT_DURABLE_CHECKPOINT=NO`.
6. Prepare a later encrypted-file transfer design with user-controlled decryption key outside AI Pro/GitHub. No state upload until explicit subsequent user approval, successful encryption-key setup and matching full historical state digests. Check target repository privacy again before any future transfer. Prefer keeping a second independent copy (NAS/offline disk). Private repo is access-controlled, not a substitute for client-side encryption.
7. **ZERO** outer `V6.run_cutoff`, engine batches, RuntimeB3 batches, synthetic-history replay or new state generation. No next-bar `75599999` execution. Do not edit frozen code or lift production blocks.

## Return

`CHATGPT_GITHUB_PRIVATE_REPO_VERIFIED=YES`;
`CHATGPT_CONNECTOR_NONSTATE_CANARY=PASS`;
`AI_PRO_GITHUB_AUTH_METHOD=...`;
`AI_PRO_PRIVATE_REPO_METADATA=PASS/FAIL/NOT_REACHED`;
`AI_PRO_NONSTATE_CANARY_WRITE_READBACK_SHA=PASS/FAIL/NOT_REACHED`;
`PRIVATE_SINK_READY=YES` only if private repo and AI Pro's actual canary pass;
`CHECKPOINT_BYTES_AVAILABLE=NO`, `DURABLE_BACKUP=NO`, `BACKUP_LOST=YES`;
`ALLOWED_REPLAY=NO`, `BAR84_NOT_AUTHORIZED`, external bars/engine batches=0; a concrete blocker if any.

Safety: 528 symbols, original frozen strategy.py SHA256 `792d2818d8495889319de5b3e6019ac0e856d27a59c6c959ac355ff239765a5f` and spec.yaml `4fb02c4559fc2fe8ee4e95390b76fce132f5af34c4f7e23a0091f1c8f8108fd1`; `TAC_LIVE_ENABLED=0`, subscriptions disabled, no real market, orders, accounts, trades, strategy deployment or production admission.
