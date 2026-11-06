# TAC / Binance AI Pro — frozen B5 Primary ambiguity, isolated native next task
Date: 2026-11-06
**TEST_ONLY, source-only frozen contract diagnosis. No new scientific policy or tie-break. No current Binance source mutation, save or deployment.**

## Current precise native evidence, furnished by the last Binance AI Pro isolated report

Per LONG **and** SHORT, each using the actual current 473KB native-source isolated main loop:
- 78 identity and 78 Minor and 78 B5 original request invocations;
- Identity UNKNOWN/KNOWN/CONFLICT = 0/78/0; Minor TRUE/UNKNOWN/CONFLICT = 78/0/0;
- Original B5 output parity 78/78; B5 overall state UNKNOWN 78/78;
- At synthetic OHLC information cutoff `123299999`, **two** original QualifiedBoundaryUses were produced from genuine D2 15m MINOR inputs confirmed at cutoff `123299999`, strictly later than associated correct-side InteractionEvent resolution cutoff `118799999`;
- Both QualifiedBoundaryUses applied to two original AnchorEpisodes via the original `TAC_BASE_produce_update008` result; neither is a WATCH-REARM QBU;
- At the role stage: **no authoritative Primary, multiple independent units qualifying at the same latest cutoff**. Primary/next RoleMemory both absent. Do not call this QBU failure.
- Original D3/B3 frozen 528 symbols, `TAC_LIVE_ENABLED=0`, subscriptions OFF, no account access or orders, no Paper/Live, source AST unchanged.
- Current native original SHA256 `strategy.py` 473006B `792d2818d8495889319de5b3e6019ac0e856d27a59c6c959ac355ff239765a5f`, `spec.yaml` 2865B `4fb02c4559fc2fe8ee4e95390b76fce132f5af34c4f7e23a0091f1c8f8108fd1`.
- Real one-version D3+B3+Episode+RoleMemory durable checkpoint/restart `BLOCKED_D3_B3_JOINT_PERSISTENCE`. Validators only accept current baseline, not isolated source, thus not called.

## Exact original frozen role contract — verified source

Frozen original `work/ai_pro_port_inactive/wp8_reference_91_v1/strategy_rc1/d3_boundary_intelligence/clusters_roles.py` and flattened original `strategy/strategy.py` `assign_roles`: eligibility requires VALID Anchor member, current relevance, known latest QBU cutoff, no terminal TRUE_BREAK and no unresolved member conflict. Primary uses the **unique latest QBU cutoff**. When 2+ independently eligible units tie at this latest cutoff, `RoleTransition.UNRESOLVED`, `primary_unit_id=None`, reason `multiple independent units satisfy Primary at same cutoff`. **No family/price/distance/ID tie-break** is authorized.

Original frozen `authoritative_d3_b5_d4_base_runtime_producers_v1.py` `produce_role_state` computes: `at_least_one_valid_member`, `current_relevant`, `latest_qualified_use_cutoff`, terminal/conflict, and `qbu_identities_by_unit_id`; it calls frozen `assign_roles`. On unresolved Primary it returns `EvidenceState.UNKNOWN` and **does not fabricate next RoleMemory**. `produce_update008` may still return real original QBU and updated Episodes when B5 role state is UNKNOWN — this is not a contradictory state and does not confer a trade signal.

**Independent full original source chain proof**:
- [Public test](https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/native_candidate_v1/test_original_b5_primary_same_cutoff_ambiguity_v1.py)
- [GitHub Actions run 42175459500, 18/18 PASS incl. inherited regressions](https://github.com/411244050-beep/tac-v2-a2-gate12-download/actions/runs/42175459500).
- The test calls frozen actual identity -> Minor -> B5 from full synthetic inputs, proves 2 QBU and two distinct economic units at the **same** confirmed cutoff correctly leave B5 UNKNOWN/Primary None/Memory None, independent of source row ordering. When original D2-confirmed progress times are **actually different within a separate synthetic fixture**, original role consumer selects the unique latest Primary and creates RoleMemory. These are **not** Binance current 160-bar acceptance results, and do not authorize injecting a fabricated different cutoff.

## Next actual native isolated operation: role SOURCE AUDIT, no rebuilding B3

1. Reuse same already-replayed LONG/SHORT native cutoff results and ledger; do not repeat B3, 63 missing references, E2 Anchor, WATCH-REARM Minor or 78 entire source-loop tests unless absolutely necessary. At the first B5 cutoff producing QBU, extract the **actual original** `Update008Request`, `Update008Output`, `RoleRuntimeOutput`, `prior RoleMemory`, and `next RoleMemory`. Do not copy fake fixture result into native ledger.
2. Print a row **per actual EconomicBoundaryUnit** with: `unit_id`, exact `anchor_episode_ids`, `contact_zones` and exact price intervals, actual source snapshot IDs, canonical D2 segment, source Episode validity/activity/termination, `at_least_one_valid_member`, `current_relevant`, `latest_qualified_use_cutoff`, sorted distinct QBU negotiation IDs + actual progress P1 cutoff, `terminal_true_break`, `unresolved_conflict`, `active_qualifying_interaction`. Include exact original `role_runtime.unresolved_reasons` and `conflict_reasons`, `roles.unresolved_reason`, plus `prior_primary_continuity_preserved`.
3. Verify canonical `produce_boundary_contact_zones` produced two legitimate **non-overlapping** contact-zone components. If they truly overlap, frozen `cluster_units` should have merged into one; trace snapshot availability and cutoff order and report source mismatch. Do not manually merge or split units. Verify two QBU identities are actually independent under frozen negotiation/rearm graph. No duplicates, no future cutoff, no missing segment/source; same latest QBU `123299999` genuinely applies to both.
4. Reproduce the original `assign_roles` result exactly from the original `role_evidence`, compare standalone frozen method and namespaced same-file original. Require no array-order influence. If exactly two latest eligible units tie, classify `EXPECTED_FROZEN_PRIMARY_AMBIGUITY` and preserve B5 UNKNOWN, no Primary, no new RoleMemory. Never pick an arbitrary winner or change a threshold.
5. Distinguish role-source **error** vs legitimate ambiguity. If unit snapshot/segment/QBU/role eligibility inputs are actually wrong or not cutoff-causal, fix only that original provenance in an isolated input view and differential-test; do not change original science or suppress a genuine tie.
6. If tie is legitimate, use separate *closed-source* LONG and SHORT main-loop synthetic coverage, **not editing the input B5 request**: select or derive a distinct complete original D1/D2 OHLC/Minor source sequence where the original science naturally confirms a **strictly later** material QBU for one of two units. Re-run original D1→D2→D3→B3/B4→B5 actual main-loop from causal inputs, no hand-injected `ProgressLineageEvidence` or altered `progress_confirmed_at` in the native request. Only if a legitimate unique later QBU results, demonstrate same-cutoff original Primary and **next** cutoff RoleMemory continuity and QBU deduplication. If a full authentic chain cannot be produced in the session, mark `BLOCKED_NO_AUTHENTIC_UNIQUE_PRIMARY_SEQUENCE` instead of passing a manually edited synthetic QBU.
7. Preserve a separate same-cutoff symmetric negative fixture: 2 valid units same latest QBU remains UNRESOLVED and Primary None, even when prior RoleMemory is absent. Source row permutation cannot be a tie-break.
8. In reporting, separate original B5 `UNKNOWN` role arbitration from `QBUProjection.TRUE` and `Minor TRUE` source facts. Name which B5 cutoffs produced two QBU and show later cutoff visibility and episode writeback; do not inflate unique QBU counts by repeated per-cutoff reports.
9. Return source/AST hashes unchanged and the genuine latest blocker. `BLOCKED_D3_B3_JOINT_PERSISTENCE` remains independently BLOCKED until a REAL host atomic durable checkpoint + cold restore for D3/B3/Episodes/RoleMemory exists. Native `validate_code` and `validate_spec` cannot verify isolated copy as previously reported, so no overwriting current files for validation.

## Stage acceptance gate

Only native actual main-loop causal evidence of unique latest QBU -> original Primary -> original newly written RoleMemory -> next cutoff verified continuity can close the *positive role* gate. Original ambiguity can be a correct expected unresolved output, not itself a defect in B5 scientific logic. Full production merge/Live remains blocked by no durable atomic host persistence and no exact external rollback.

Keep all original 528 ordered symbols and TEST_ONLY controls; no account, subscriptions, paper or live, no trade/position/order side effects.
