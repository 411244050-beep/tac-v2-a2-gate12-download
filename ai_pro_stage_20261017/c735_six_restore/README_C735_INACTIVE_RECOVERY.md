# TAC-V2/A2 c735 host mismatch: isolated six-file original-source restoration

**This is not live deployment.** The private c735 reference has been re-read. All six problematic source files are byte-identical to their frozen pins in GitHub. This sealed payload carries only those six files, not a full checkout, runtime, account material, credentials or live activation.

- Reference source: `411244050-beep/tac-v2-a2-external-runtime@c73522e957a77c40096ebb880529ae5cd0fc81b0`
- Host report: 4 hash mismatches and 2 missing/symlinks out of 17 frozen source files.
- Crypto: ChaCha20-Poly1305 authenticated encryption; header `TAC-AIPRO-C735-SIX-CHACHA20-POLY1305-V1`.
- Recovery key must remain private; do NOT commit it to GitHub or include it in host receipts.
- Decryptor: `RECOVER_C735_SIX_TO_NEW_INACTIVE_ONLY.py`. Arguments `--encrypted-file`, `--verified-host-base-root`, `--new-inactive-dir`. Supply `TAC_C735_RESTORE_KEY_HEX` as environment variable.
- Destination must be a new child directory under the existing `tac-inactive-stage-*` directory. The script never overwrites host source. It first verifies all eleven unchanged host pin files, validates all six c735 source bytes, then copies seventeen exact source files into a new inactive folder.
- Strictly fail closed if any of the other eleven files don't match or the 6 source bytes are wrong. Existing active Forward, Measurement, cron, CURRENT, epoch, checkpoints and runtime pointers remain untouched.
- A seventeen-file recovered source snapshot is **NOT** a full runtime checkout; missing dependencies must be checked separately before any controlled nontrading cutover.
- After PASS, independently run the original `PRECHECK_C735_BASE_READONLY.py` against the NEW inactive source root and only then `GENERATE_RUNNER_IN_UPLOAD_FOLDER_ONLY.py` with the verified frozen runner path. Both remain stage-only. Report no claim of real continuity or readiness to trade.
- Keep `TAC_LIVE_ENABLED=0`. No orders, fills, intents or backfill. Gates remain OPEN and live activation NO-GO.
