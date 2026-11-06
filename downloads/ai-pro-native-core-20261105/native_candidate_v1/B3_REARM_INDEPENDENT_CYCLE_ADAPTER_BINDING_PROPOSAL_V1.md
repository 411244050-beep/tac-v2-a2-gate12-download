# TAC / Binance AI Pro — B3 independent-cycle rearm adapter binding PROPOSAL V1
Date: 2026-11-06

**STATUS: USER-APPROVED FOR ISOLATED TEST_ONLY ENGINEERING EXPERIMENTS (2026-11-06) — NOT ORIGINAL FROZEN AUTHORITY; NOT APPROVED FOR NATIVE MERGE, DURABLE PRODUCTION OR LIVE USE.**

This decision packet resolves the **technical definition** of the missing B3 mapping but does **not** assert that the original frozen D3/B3 contracts already authorized it. The user authorized **isolated TEST_ONLY experimentation** on 2026-11-06. Production adoption and joint durable state are still separately unproven; outside isolated experiments, keep `BLOCKED_REARM_B3_BINDING_AUTHORITY_MISSING` or `BLOCKED_D3_B3_JOINT_PERSISTENCE` as appropriate.

## Sources and evidence

- Frozen D3: `work/ai_pro_port_inactive/wp8_reference_91_v1/strategy_rc1/d3_boundary_intelligence/interaction.py` on private `411244050-beep/tac-v2-a2-external-runtime/tac-full-live-v1`, `rearm_after_resolution`.
- Frozen B3: `provisional_shadow_v1/runtime_b3_price_driven_return_production_state_v1.py` on same branch: `_reset_reasons`, `_process_one`, `restore_state`, `process_batch`.
- Frozen B3 semantic supplement: `provisional_shadow_v1/runtime_b3_price_driven_return_semantic_supplement_v1.json`.
- Public old-source direct tests: `test_b3_d3_rearm_gap_source_only_v1.py`, `test_b3_d3_rearm_short_atomic_contract_v1.py`.
- Actual source-only CI: [run 42164006565](https://github.com/411244050-beep/tac-v2-a2-gate12-download/actions/runs/42164006565), **9/9 PASS**, LONG+SHORT. This is NOT the 473KB native strategy and NOT a durable Binance-host transaction proof.
- Binance user-reported latest native source: `strategy.py` 473006 bytes SHA256 `792d2818d8495889319de5b3e6019ac0e856d27a59c6c959ac355ff239765a5f`; `spec.yaml` 2865 bytes SHA256 `4fb02c4559fc2fe8ee4e95390b76fce132f5af34c4f7e23a0091f1c8f8108fd1`.
- Actual current Binance synthetic main loop: 512 OHLC source bars, 201 B3 batch observations, rearm `RESOLVED -> ARMED` then `ARMED_WITHOUT_RUNTIME_B3_PENDING_STATE` BLOCKED. No current source was changed.

## Scope and derivation

Original D3 returns a **new independent armed event** `E2` on a strictly later separated cutoff after `E1=RESOLVED`. Frozen B3 creates its pending only from `UNARMED+separated`, and its pending is keyed by `(symbol,candidate_id)`, not by D3 event ID. Reusing `E1` or inheriting its adverse price extrema would violate the fresh-cycle and no-same-bar rules.

The required engineering bridge is to distinguish **the existing prior D3 control state (RESOLVED)** from **the beginning of a *new independent* B3 observation cycle**. The latter has not been formally mapped in the frozen original B3 contract. It is **incorrect** to claim prior D3 was UNARMED. The adapter may introduce a separate, provenance-labeled `NEW_CYCLE_PRE_ARM` phase *only if this proposal is approved*. That phase projects to B3's existing `UNARMED+separated` producer input, without overwriting, aliasing, or reclassifying the real original D3 event.

## Proposed binding requirements (must ALL hold)

R1. Read current **original** D3 `before`, D2 trend episode/direction, canonical source segment, closed bar, causal prebar snapshot and corresponding geometry. Only complete, authenticated source may proceed; real epoch continuity UNKNOWN still blocks.

R2. If `before.control != RESOLVED`, do not use this mapping. Follow existing frozen B3 path unchanged.

R3. If `before.control == RESOLVED`, compute `projected = rearm_after_resolution(before, geometry)` **without mutating authoritative D3**. Only `projected.control==ARMED`, `projected.armed_at==current cutoff`, `projected.event_id != before.event_id`, `projected.provenance.prior_event_id==before.event_id`, `before.terminal==False`, valid trend and candidate, complete continuity, no source/segment/direction drift, and `geometry.separated==True` can enter the new-cycle phase. Same-cutoff, unresolved, or conflict cases fail closed.

R4. Verify frozen B3 `pending_state(symbol,candidate_id) is None` from restored state **before staging**. If old pending still exists, report conflict; do not manually delete. No two B3 observations for this candidate/cutoff. No reset+arm double-tx workaround.

R5. **Only after formal acceptance of this engineering mapping**, construct one B3 observation for `NEW_CYCLE_PRE_ARM` using the actual current authenticated bar, snapshot, geometry, D2 direction and candidate, with B3 producer's `interaction_control=UNARMED`. This is an observation of the *new independent cycle's pre-state*, not an assertion about the old D3 event. Do not mutate actual `before.control`.

R6. Execute one frozen B3 `process_batch` in a **restored, isolated staged producer**, with a single deterministic transaction ID bound to candidate, cutoff, canonical segment, new event ID and contract ID; **exclude mutable source digest from the transaction ID**, but record it separately in the original frozen B3 input digest and joint receipt so same identity/different input rejects. Require reason `ARMED_FROZEN_CURRENT_CUTOFF_NO_RETURN`, no return evidence, pending at the exact cutoff, bar Close, arming snapshot/source_scale, trend ID, direction, segment. Failure => no adoption.

R7. Invoke the **original D3** `update_007_interaction_break` exactly once on the **original prior event state**, with no eligible return from the current arming bar, and check D3's actual result exactly equals the unmutated preprojection `projected` (event ID, control, cutoff, provenance). No synthetic D3 event construction or custom scientific transition.

R8. The **combined** persistent checkpoint must include exact original D3 event+Episode ledger, frozen B3 exported state+completed transactions, D2 source identity, canonical receipt/digest, RoleMemory, source cutoff, a single-writer revision and joint transaction ID. Use a **real atomic durable commit** and restore from that same single revision; the B3 `persist` callback alone does NOT establish joint D3/B3 durability. No real host atomicity => `BLOCKED_D3_B3_JOINT_PERSISTENCE`.

R9. On exact duplicate cutoff/transaction, read joint committed receipt and return cached original result; different source digest for the same identity rejects. Cold-restart must verify `D3 E2.armed_at == B3 pending.arming_information_cutoff` and exact source/candidate/segment identity. Partial/mixed or missing revision fails closed, never guesses.

R10. New-cycle arming cutoff may NOT consume a B3 return, start a TEST, generate a QBU, Primary, entry authority, or trade. First eligible adverse return observer cutoff **strictly later**; qualification and test activation remain separated by at least one later cutoff per frozen causal semantics.

## NON-AUTHORITATIVE pseudo-code sketch for future native isolated implementation

```python
# NOT DROP-IN CODE. Do not copy over frozen producer or current native strategy.
assert TAC_LIVE_ENABLED == 0 and source.is_complete
stage = restore_complete_joint_checkpoint(base)  # requires REAL durable store
before = stage.d3.current_event(candidate_id)
if before.control is RESOLVED:
    proposed = frozen_rearm_after_resolution(before, geometry)
    if original_rearm_guards_pass(before, proposed, source) and stage.b3.pending_state(symbol, candidate_id) is None:
        # ONLY WHEN THIS BINDING IS EXPLICITLY ADOPTED
        new_cycle_obs = frozen_b3_observation(
            source=source, interaction_control=UNARMED,
            phase="NEW_CYCLE_PRE_ARM", lineage_link=proposed.event_id,
        )
        b3_result = stage.b3.process_batch(UNIQUE_JOINT_TX, (new_cycle_obs,))
        assert_exact_new_pending_and_no_return(b3_result, proposed, source)
        d3_result = stage.d3.update_007_interaction_break(
            snapshot=snapshot, geometry=geometry, return_evidence=None,
            structural_acceptance=None, correct_side_recovery=None
        )
        assert_semantic_identity(d3_result, proposed)
        atomic_commit_complete_joint_checkpoint(stage)
    else:
        fail_closed()
```

## Acceptance and blockers

T1. Existing old and new source-only LONG/SHORT fixture results: [35/35 PASS including inherited regressions](https://github.com/411244050-beep/tac-v2-a2-gate12-download/actions/runs/42164754734) as independent source-bound proof only; also includes staged second-cycle return and interaction tests. This is not native Binance acceptance.
T2. Current 473KB Binance main cutoff node under an **isolated code copy**, with full TEST_ONLY LONG/SHORT and legal/conflicting rearm + B3 pending + return later cutoff: **NOT RUN**.
T3. Combined state commit crash injection and cold restart on actual Binance storage: **NOT RUN**.
T4. Original output differential, QBU Episode/RoleMemory/Primary actual main-loop positive, D2 terminal provenance: **NOT RUN / BLOCKED**.
T5. Native `validate_code`, `validate_spec` after hypothetical patch: **NOT RUN**.

Before authorizing any native code merge, preserve the verified 473KB baseline or provide provable rollback. Never present this engineering mapping as original frozen science. Preserve original B3/B4/QBU functions and 528 universe, `TAC_LIVE_ENABLED=0`, subscriptions off; no account, orders, Paper/Live, or execution.

## TEST_ONLY implementation and native acceptance handoff (2026-11-06)

- [Staged adapter source](https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/native_candidate_v1/B3_REARM_INDEPENDENT_CYCLE_STAGE_TEST_ONLY_V1.py)
- [Staged LONG/SHORT tests](https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/native_candidate_v1/test_b3_rearm_independent_cycle_stage_v1.py)
- [Exact Binance isolated acceptance handoff](https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/native_candidate_v1/B3_REARM_NATIVE_ISOLATED_ACCEPTANCE_HANDOFF_20261106.md)
