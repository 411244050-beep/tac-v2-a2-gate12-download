# TAC V6: ParameterState class-identity repair, then exact genesis bar 83 retry
2026-11-07 | Original pinned commit 1f2499ecb84bfefea063992d48f23949c65c5578
Synthetic-only TEST_ONLY science; no live market claim, deployment, or trading permission.

## Latest actual baseline; keep earned work

- The original WP8 loader/adapter D1 import binding was repaired without editing the frozen science. Exactly 82 SYNTH random.Random(0) pre-genesis bars returned RAW_PRETREND, all normal committed engine transactions, SHORT=0, no future cutoffs.
- Verified pre-genesis checkpoint after bar 82: last_cutoff=73799999, state_digest prefix b342a5d01d3f and suffix 38a203fa, minor pivots 12, intermediate pivots 4, next observer snapshot exists for SYNTH. Original export_state was 13683812 bytes and its SHA256 equals state_digest. This is an isolated memory-state checkpoint, **not durable persistence** unless the exact bytes are actually retained in the new process.
- The single original bar 83: open_time=73800000, close_time=74699999. Raw shadow reached, raw D1 is original D1ReferenceResult, raw transaction_id cutoff_tx:14f19d37474397a1311065faf55ce3de.
- Failure next occurred in frozen parameter view while entering original V6 _genesis: ValueError "theta_test must be FROZEN with an exact value for WP3". The reported slot is FROZEN and has exact_value; the original identity guard failed because the slot's ParameterState and the class global used by frozen_d3_parameters were different Python Enum class objects. Existing imported frozen.frozen_d3_parameters was traced into current_qbu_singlefile at code first line ~1696. It is not a numeric parameter omission and is NOT permission to change the guard.
- Candidate output_digest, post-shadow transaction, formal_tx, six updated D4 classes, static/packet/F9 UPDATE-011 and lineage prepare/commit/abort were NOT_REACHED this round. The pre-genesis V6 state remained at checkpoint after the thrown genesis exception.
- Two distinct blocked governance gates remain: PORT007_UNRESOLVED_PRODUCTION_ALLOCATION_BLOCKED and BLOCKED_D3_B3_JOINT_PERSISTENCE. Earlier WATCH TRUE and START_FIRST_EVENT came only from synthetic fixture engineering tests, not real-market evidence.

## Frozen reference authority

- [Original V6 Python](https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/d2_genesis_authority_handoff_20261106/live_runtime_raw_authority_extraction_packet_orchestration_binding_v6.py), Git Blob 2f12e518858be4758d81d0027c6045466ddf38f0; genesis calls frozen.frozen_d3_parameters(minimal.current_partial_parameter_snapshot()) at approx line 377.
- [Original strategy_rc1 91-file package/manifest](https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/wp8_strategy_rc1_full_original_20261106/README_RECOVERY_HANDOFF.md).
- [Exact original archive SHA256SUMS](https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/wp8_strategy_rc1_full_original_20261106/strategy_rc1_SHA256SUMS.txt). Relevant members:
  - strategy_rc1/parameter_snapshot.py SHA256 e02a74f60bbee0ccf67ea793d7e30174f91524d97af1aabf0ffb000052ca37f5
  - strategy_rc1/d3_boundary_intelligence/parameters.py SHA256 ef2efcb5ebb277b496596b099261fe852363852ef629ef2968661a9d70dd9881
- [Earlier strict bounded V6 82+1 handoff](https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/v6_pregenesis_bootstrap_20261106/README_AFTER_D1_IMPORT_SINGLE_BAR_PASS_82_PLUS_ONE.md).

Frozen WP3 parameter extraction has the identity condition: slot.state is ParameterState.FROZEN, and slot.exact_value is not None. The original class should come from the single original strategy_rc1.parameter_snapshot import. The loaded current_qbu_singlefile flat copy is suspected to have a separate class global. Do not treat equal enum .value, class name, or source string as Python class identity.

## One permitted next attempt

**Preflight is mandatory before calling any K line or science:**

1. In the existing isolated process or a new identically verified import environment, locate the precise frozen function that V6 uses: frozen.frozen_d3_parameters and its __globals__. Locate its helper _frozen_fraction and its global ParameterState. Locate minimal.current_partial_parameter_snapshot(), each slot.state and its class, the original strategy_rc1.parameter_snapshot.ParameterState, and strategy_rc1.d3_boundary_intelligence.parameters loaded module. Print only names, IDs/class identity and source provenance (no full object graph).
2. Verify reference identities, e.g.:
   - type(snapshot.slot("theta_test").state) is canonical ParameterState
   - snapshot.slot("theta_test").state is canonical ParameterState.FROZEN
   - extracted frozen parameter helper __globals__["ParameterState"] is canonical ParameterState
   - snapshot original ParameterSnapshot/ParameterSlot class identity and all five original theta slots have exact values and FROZEN identity.
   Also verify any other frozen runtime copy of ParameterState. Preserve original Fraction values and ordering. Do not infer correctness from str(slot.state) or .value.
3. Repair only the **loader's original module symbol resolution** using one canonical module instance, matching the successful evaluate_d1_reference fix. Prefer loading the exact original strategy_rc1.parameter_snapshot and reusing its classes for both snapshot factory and parameter extraction; re-export/alias only that same canonical class where the loader previously omitted/rebound an import. If the current_qbu_singlefile frozen function was re-executed as a separate flat copy, document its source and make its referenced class binding canonical without changing its AST, guard, class definitions or numerical constants. If class identity cannot be unified with source provenance and no behavior changes, report PARAMETERSTATE_IDENTITY_LOAD_BOUNDARY_BLOCKED.
4. After repair, require original frozen_d3_parameters(snapshot) to succeed in **static preflight** with exactly the unmodified original parameter values. If it fails, report exact original exception and do not call run_cutoff; no fake FROZEN field, no reconstructing snapshot with arbitrary values, no relaxing "is" to "==" or ".value".

**State acquisition and run limit:**

5. **Preferred:** Continue in the SAME isolated V6 runtime that currently has the 82-bar state, or restore an actual saved original 13683812-byte export_state using exact V6.restore_state() with the SAME canonical module graph. Verify last_cutoff 73799999, full state_digest against saved SHA256, minor_count 12, intermediate_count 4 and SYNTH next snapshot. A state hash alone cannot reconstruct bytes; if actual checkpoint bytes do not exist, do not claim restore.
6. Then invoke exactly **one** original V6 run_cutoff(genesis_bar) at 74699999 in a single bounded trial. Stop on first unexpected exception, report its exact original code path. Observer may capture small scalar return metadata from original _raw_shadow, _post_d3_shadow, candidate result; it must never alter execution order.
7. **Fallback only if the valid prestate is missing:** Reconstruct from the SAME original random.Random(0) synthetic fixture in a clean validated isolated process, with an immutable allowed tuple of 82 prebars plus the one genesis bar, hard outer run_cutoff boundary cap <=83 inputs, pregenesis <=82, genesis <=1, SHORT=0, subsequent cutoff=0. Require 82 RAW_PRETREND returns and exact previously recorded checkpoint digest. Any drift: stop before genesis; no forced alignment, no parallel/unbounded 156-row code. Do not run fallback if a valid original checkpoint is available.
8. At genesis check raw D1 type remains D1ReferenceResult and actual raw transaction ID/source unchanged; if subsequent code reaches candidate production, log genuine output_digest and actual original post_sr.transaction_id equality raw_sr.transaction_id to yield formal_tx. Do not invent refs. Compare new D2 pivot/source event IDs and WATCH/genesis identities against previous synthetic observations; no injection or hard-coded science results.
9. If six original D4 source classes can genuinely be proven and original static READY, let original V6 execute staged F9 packet through UPDATE-011 and same-transaction commit. Otherwise abort and retain no committed genesis ledger. No further bars after genesis even if success. No market signals are inferred from WATCH.

**Required output:** ParameterState object identity before/after (including original module origin); five actual frozen theta identities/values preserved; checkpoint reused versus 82 recomputed; exact run counts and first failure; original raw D1 + candidate digest, raw/post tx and formal_tx if reached; source comparison; six D4 coverage classes; final packet/F9/lineage commit actual or NOT_REACHED; explicit scalar summary flushed and process exit; continued synthetic-only classification. Do not label previous 4+2 source proof as real-market coverage.

Immutable boundary: strategy.py SHA256 792d2818d8495889319de5b3e6019ac0e856d27a59c6c959ac355ff239765a5f; spec.yaml SHA256 4fb02c4559fc2fe8ee4e95390b76fce132f5af34c4f7e23a0091f1c8f8108fd1; 528 frozen symbols, TAC_LIVE_ENABLED=0, subscriptions off, TEST_ONLY. No orders, market/account I/O, Paper/Live, trades, deployment or persistent strategy save. Keep PORT007 and D3/B3 durable joint-persistence explicitly independent.
