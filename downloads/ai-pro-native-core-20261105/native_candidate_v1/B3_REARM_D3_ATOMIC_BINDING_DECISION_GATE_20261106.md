# TAC / Binance AI Pro — B3 rearm atomic binding decision gate (2026-11-06)

**STATUS: READ_ONLY CONTRACT ANALYSIS / NON-DEPLOYABLE / NO SCIENCE AUTHORITY GRANTED.** This is not a replacement strategy, native patch, backup, or evidence of passing tests.

## Current Binance baseline (read-only SHA attested by the user's latest Binance AI Pro report)

- `strategy/strategy.py`: 473006 UTF-8 bytes, SHA-256 `792d2818d8495889319de5b3e6019ac0e856d27a59c6c959ac355ff239765a5f`.
- `strategy/spec.yaml`: 2865 UTF-8 bytes, SHA-256 `4fb02c4559fc2fe8ee4e95390b76fce132f5af34c4f7e23a0091f1c8f8108fd1`.
- These bytes are **not available in this GitHub repository**; existing public strategy.py is an older, different baseline. **DO NOT OVERWRITE** the current Binance workspace with public source.
- External byte-identical backup: **BLOCKED**; no authorized transfer path established. Current live enable=0, 528 frozen symbols, native subscriptions off.

## Proven frozen source authorities (do not change)

1. Private reference `work/ai_pro_port_inactive/wp8_reference_91_v1/strategy_rc1/d3_boundary_intelligence/interaction.py`:
   - `rearm_after_resolution(event, geometry)` requires the old event `RESOLVED`, a *strictly later* geometry cutoff than `resolved_at`, and an authoritative separation; it returns a **new independent ARMED event** with deterministic new event ID and `armed_at=current cutoff`. It cannot admit return on that arming bar.
2. Private `provisional_shadow_v1/runtime_b3_price_driven_return_production_state_v1.py`, frozen producer:
   - `_reset_reasons`: `RESOLVED` / active terminal semantics clear old pending first;
   - `_process_one`: only an authoritative **UNARMED + separated** observation with absent old pending creates `RuntimeB3PendingLineage`. An **ARMED + no pending** observation MUST raise `ARMED_WITHOUT_RUNTIME_B3_PENDING_STATE`.
   - `process_batch`: deterministic candidate order; duplicate candidate in one batch rejects; transaction ID replay of differing input rejects; `persist(proposed_state)` precedes adoption on the producer object. It does **not** implement a D3+B3 joint store.
   - `restore_state(serialized)`, `export_state()`, `pending_state(symbol,candidate)` exist.
3. Private `provisional_shadow_v1/runtime_b3_price_driven_return_semantic_supplement_v1.json`:
   - reference is arming **closed 15m Close**, scale is arming **causal prebar snapshot.source_scale**, first return cutoff **strictly later**. No intrabar assumption, same-bar return, same-bar test activation, or new threshold.

## Reproduced *static* mismatch (latest Binance line numbers reported; not dynamically replayed here)

- 6032–6039: B3 consumes old `before.control=RESOLVED`; prior pending is cleared.
- 6053–6055: D3 subsequently re-arms via new event identity, `control=ARMED`.
- Next cutoff: frozen B3 sees `ARMED` without pending and blocks.
- 6070–6079: D3/B3 commit boundary needs joint atomicity; in the current Binance version no verified external durable store/restore transaction exists.

## Bridge design choice to resolve BEFORE code mutation

**Do not** create pending directly, quietly map an actual old `RESOLVED` event to `UNARMED`, duplicate the same candidate within one batch, or force the event to `UNARMED` at the next cutoff. All may change causal identity or freeze a wrong arming Close/scale.

One **candidate** adapter-only resolution, requiring a specifically approved/verified *new-cycle transition-phase mapping* and TEST_ONLY proof, is:

1. Stage the complete original D3 event/Episode ledger, frozen B3 exported state and completed transactions **off to the side**. Require authenticated closed bar, prebar snapshot and original D3 rearm predicates.
2. Compute `rearm_after_resolution` as a pure preprojection. Verify new event identity `E2 != E1`, same candidate/trend/segment/direction, `E2.armed_at == current cutoff`; reject inconsistent or terminal inputs. Verify frozen B3 prior pending state is absent (if present, fail closed; no manual clear).
3. Define an **explicit, contract-authorized new independent cycle pre-arming phase** distinct from changing the actual D3 event state. **Only if the binding contract formally permits this phase** may an authoritative B3 new-cycle arming observation be passed through the producer's existing `UNARMED + separated` entry branch, with the actual arming bar and prebar snapshot. This is NOT a claim that the old D3 event was UNARMED. Make this distinction visible in lineage/transaction ID.
4. Require one candidate/one B3 transaction per cutoff and frozen `ARMED_FROZEN_CURRENT_CUTOFF_NO_RETURN` result, with pending `arming_information_cutoff`, `arming_bar_close`, `arming_scale`, snapshot, trend, segment matching E2 and actual causal sources. Do not consume return evidence at that cutoff.
5. Publish a single **combined staged state** containing the D3 new event, B3 pending + completed tx digest, original D3 Episode ledger, RoleMemory and joint cutoff receipt. Adopt it only through a real atomic durable save/restore boundary. If the host only offers separate non-atomic mutable stores, report **BLOCKED_D3_B3_JOINT_PERSISTENCE**, do not assert restart equivalence.
6. Next cutoff, B3 sees genuine `ARMED` plus restored pending and applies frozen later-bar return rules; restore/duplicate/different-input replay must be checked.

This **is a proposal**, not existing frozen semantic authorization. A two-B3-transaction same-cutoff variant (old RESET then new ARM) is **not approved** here: the frozen producer permits unique transactions, but the cross-transaction same-candidate/same-cutoff and joint commit semantics have not been established.

If the authorized transition-phase mapping cannot be justified from the original frozen science, return `BLOCKED_REARM_B3_BINDING_AUTHORITY_MISSING`; no "repair" may assert parity.

## TEST_ONLY minimum regression (run against actual current D3 node, not merely standalone B3)

- LONG and SHORT: original `RESOLVED` E1 -> strictly later separated E2 -> frozen B3 pending created with same arming cutoff, bar Close, causal prebar scale/snapshot -> next-bar return only.
- Reject same cutoff, no separation, terminal/continuity break, D2 trend/segment/direction change, pending already exists, mismatched candidate/snapshot, and conflict lineage.
- Same transaction ID + identical source = exact replay; same ID + changed source = reject; duplicate candidate in batch = reject; no duplicate QBU/Role.
- Inject persistence failure: neither D3 E2 nor B3 pending becomes committed; restore original state intact. Restart after successful commit: same E2, pending, tx digest, RoleMemory, no duplicate arm/return.
- Preserve 68x UNKNOWN counts until actual original identity mapping and material Minor `progress_evidence` records exist; `EvidenceState.TRUE` without records never promotes B5.
- Original output equality, actual current-main-loop positive QBU and Primary, multiple cutoff RoleMemory, real D2 terminal provenance remain independent gates.
- Execute native `validate_code`, `validate_spec` only on the **current SHA-verified candidate**, after lawful backup and staged TEST_ONLY patch. Static PASS != save/market/live validation.

## Safety & next stage

Never enable subscription, paper/live, accounts, orders, cancel, position, or restart unsafe source without separate authority. Keep `TAC_LIVE_ENABLED=0`, 528 frozen symbols. D4 four frozen mechanisms, F9, D5/PORT007, UPDATE014 and D6 remain **NOT ACCEPTED** until the live main-loop source evidence meets the existing gate.

**Required human/environment dependency:** obtain a reliable external byte-identical backup of both current workspace files, or a formally proven platform rollback/export mechanism; until then do only public-reference source/test work, no current-workspace code writes.
