# TAC Binance AI Pro — next concrete action, 2026-11-05

**No new parameter approval needed.** The most recent user-reported native workspace has:

```text
strategy/strategy.py sha256:
ccd0a505729d0060d987f523ffa967d0c738586a4bf88019064177c8da012249
strategy/spec.yaml sha256:
2d25002b0a022f266bb8d45c085fa40dad81e3fc11e87b4688de7fbbf1df26c2
```

Prior update only wrote a `runtime_b3` BLOCKED status, not scientific B3 integration.

## Actual source installer (published and offline tested)

https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/native_candidate_v1/APPLY_RUNTIME_B3_SCIENCE_SAFE_V1.py

Original frozen source files **already in your workspace**:

```text
tac_source/runtime_b3_native_inputs/RUNTIME_B3_FROZEN_ORIGINAL_PRODUCER_APPEND_V1.py
tac_source/runtime_b3_native_inputs/RUNTIME_B3_TO_ORIGINAL_D3_UPDATE007_BRIDGE_V1.py
```

Place installer in `tac_source/APPLY_RUNTIME_B3_SCIENCE_SAFE_V1.py`. In an isolated Python/scratch tool, run *inspection first*:

```bash
python tac_source/APPLY_RUNTIME_B3_SCIENCE_SAFE_V1.py \
 --strategy strategy/strategy.py \
 --producer tac_source/runtime_b3_native_inputs/RUNTIME_B3_FROZEN_ORIGINAL_PRODUCER_APPEND_V1.py \
 --bridge tac_source/runtime_b3_native_inputs/RUNTIME_B3_TO_ORIGINAL_D3_UPDATE007_BRIDGE_V1.py
```

Inspection only prints a proposed new SHA and original-AST assurance, and writes nothing. Once the exact known baseline and frozen original B3 AST both match, execute the same command with `--commit`, saving a `strategy/strategy.py.pre_b3_original` backup. If source changed, the script refuses modification; inspect the differences and update the intended baseline **only after actually reconciling changes**, never bypass the SHA check.

CI for source-preserving installer:
https://github.com/411244050-beep/tac-v2-a2-gate12-download/actions/runs/42052521421

## Important: Append is not yet native D3 binding

After installation, the actual D3 custom node's **existing** per-15m-cutoff logic must call the newly imported `_tac_frozen_b3_update007_step` INSTEAD OF the old D3 `update_007_interaction_break` / `update_008_anchor_lifecycle` pair. Do not run both. Bind its arguments from actual original current-cutoff D2 trend, prebar snapshot, geometry, original candidate, exact closed bar, and persistent frozen Runtime-B3 producer state. The original producer's pending arming state MUST survive between successive cutoffs of the same independently authenticated epoch. Never initialize a new producer on each bar.

For **fully specified synthetic test fixtures ONLY**, prove the 4-cutoff positive case:
`ARMED_FROZEN_CURRENT_CUTOFF_NO_RETURN` →
`RETURN_QUALIFIED_LATCHED_NOT_CONSUMABLE_SAME_CUTOFF` →
`LATCHED_RETURN_CONSUMABLE` + original D3 INTERACTION_ACTIVE →
original D3 RESOLVED. Exact runnable source and CI test:
https://github.com/411244050-beep/tac-v2-a2-gate12-download/actions/runs/42035411711

For **real prospective market data** no stable epoch/restart proof currently exists, so `history_complete=False` and `BLOCKED_EPOCH_CONTINUITY_UNPROVEN` must remain and producer must not mutate. Do not confuse this real-data guard with the synthetic test mode. Do not infer full provenance from a bounded in-memory 300/400-bar array.

Return current full `strategy.py` SHA, changed function names, native `validate_code` and `validate_spec` actual results, and whether D3's live cutoff function **really calls the frozen producer**. A standalone synthetic test is meaningful only for the producer science; it is not real native market execution.

Keep all 528 target symbols, D1/D2 and D3 multiTF sources, TEST_ONLY provenance, `TAC_LIVE_ENABLED=0`, no account, no orders, no Paper/Live. Do not invoke audit/save until the original full-stage chain is actually connected. Continue next with original B4 and QBU freeze sources already in `tac_source/frozen_evidence_producers_v1/`.

**The first action in this turn must be running the installer and updating actual strategy.py, not writing another BLOCKED field or a summary.**
