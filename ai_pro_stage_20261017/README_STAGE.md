# TAC-V2/A2 — Binance Ai Pro isolated NONTRADING Forward stage transport

The published `.enc` file is **encrypted**; no private strategy repository, plaintext runner, order/account data, secrets or trading keys are published. The one-time 256-bit ChaCha20-Poly1305 decryption key is delivered in the owner's separate private ChatGPT exchange. **Do not publish that key here.**

- Private source branch: `tac-full-live-v1`; source stage tested at `127ba7b31a8e4b30fb18c9bd6c05d236feadf419`. Latest source HEAD confirmed as `ca26c05d09887b974ab42697f004b720b1a3305d` with no stage code change.
- `TAC_AIPro_528_Forward_EOF_STAGE_ONLY.zip.enc` SHA256: `22730a5d22bbce455808a0e5bb193d14ff5b27bd4676dacfc647d6c4d1435eed`.
- Authenticated cipher: ChaCha20-Poly1305 RFC 8439; AAD and header pinned in `DECRYPT_STAGE_STDLIB_ONLY.py`.
- Decrypted ORIGINAL ZIP: exactly 10,163 bytes; SHA256: `a583976874d613ec859b10c33947ccb937ba5c5c438e49530205d8b5f2af210f`.
- No pip, PAT, GitHub private-repo access, OpenSSL or third-party crypto package required on host; decryptor uses Python 3 standard library.
- Source ZIP contains only transport, generator, 17-file read-only prechecker, verifier, README, manifest. The frozen original runner is deliberately NOT included and must exist on the Ai Pro host as a byte-verified offline c735 source.

## Host stage operation only (NOT CUTOVER)

1. Download `DECRYPT_STAGE_STDLIB_ONLY.py` and `.enc` from the **exact immutable Git commit** URL supplied by ChatGPT; inspect/verify expected SHA256.
2. In a brand-new HOME-local staging directory, run the Python decryptor with `TAC_LIVE_ENABLED=0` and `TAC_STAGE_DECRYPT_KEY_HEX` provided privately. Do not persist the key in source files. Do not output/report the key.
3. Run extracted `VERIFY_PACKAGE_READONLY.py`; read-only `PRECHECK_C735_BASE_READONLY.py --base-root <verified c735 full source root>`; then generate new runner inside decrypted inactive folder only.
4. Verify generated runner Git blob `8174d073558ec118b53d5ee0daa04a037b9fd230`, transport Git blob `ead664d9a6805b151feaf52fb729f5066b9e5349`.
5. Read-only report actual Forward/Measurement PID, CWD, cron, active runtime pointers, CURRENT/epoch, latest two prospective cutoffs. Output `AI_PRO_SOURCE_STAGE_READY_NONTRADING_NO_CUTOVER` or `HOLD_*` and STOP.

NEVER start a second Forward, rotate epoch, touch active runtime, checkpoint, Measurement, recovery cron, CURRENT, live money, orders, cancel, leverage, Hedge Mode or backfill. `TAC_LIVE_ENABLED=0`, Gate1/2/3 OPEN, LiveActivation NO_GO. No production host operation is authorized by publication of these transport bytes.
