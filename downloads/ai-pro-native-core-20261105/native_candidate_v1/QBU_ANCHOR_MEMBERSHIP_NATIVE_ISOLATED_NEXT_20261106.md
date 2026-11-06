# TAC Binance AI Pro — next isolated QBU anchor-membership projection
Date: 2026-11-06
Status: **ACTIONABLE ISOLATED TEST_ONLY HANDOFF; NATIVE ACCEPTANCE NOT YET PROVED**

Do not rebuild strategy. Do not edit, overwrite, save, deploy or export the current Binance baseline. No subscription, account, order, Paper/Live, or trading action. Keep 528 ordered symbols, `TAC_LIVE_ENABLED=0`, original B3/B4/D3/QBU frozen science unchanged.

## Native state from latest actual Binance report

Source baseline, read-only:
- `strategy/strategy.py` 473006 bytes SHA256 `792d2818d8495889319de5b3e6019ac0e856d27a59c6c959ac355ff239765a5f`
- `strategy/spec.yaml` 2865 bytes SHA256 `4fb02c4559fc2fe8ee4e95390b76fce132f5af34c4f7e23a0091f1c8f8108fd1`

Already established, per LONG/SHORT direction:
- Main synthetic source 160 OHLC bars, 335/335 B3+D3 bridges, three rearm cycles, original B5 parity for 15 old reachable cutoffs, A/B rearm-to-later-return-consumption tested, C unfinished (no qualification).
- After delivering 12 actual original historical event IDs, identity UNKNOWN 63 -> 8; KNOWN 15 -> 70; missing referenced events 63 -> 0; KNOWN mapping nonempty 44, empty 26; 0 conflict. 8 remaining UNKNOWN are `ELIGIBILITY_UNKNOWN` for four actual new `D3-INTERACTION` event IDs with missing `anchor_episode_id`.
- 15 old reachable B5 requests remain UNKNOWN with zero QBU / qualified Anchor use / Primary / new RoleMemory; identity mapping empty and no material Minor progress records. Minor has actual raw inputs, but no consumer-related eligible correctly resolved interactions. Do not infer missing pivots/threshold failure.

## Verified frozen D3 code source causal diagnosis

In frozen original `work/ai_pro_port_inactive/wp8_reference_91_v1/strategy_rc1/d3_reference.py` and flattened older public `strategy/strategy.py`:
- Original `D3ReferenceSkeleton.update_007_interaction_break` attaches a new `D3-INTERACTION` member ID to an existing `AnchorEpisode.interaction_event_ids` using original `attach_interaction`.
- Original `update_008_anchor_lifecycle` returns existing non-terminated episode early; `bind_event_to_episode(event,episode)` only runs when an episode starts or restarts. Therefore an existing Episode may hold later interaction E2 membership, while the *new E2 event record* still has `anchor_episode_id=None`.
- This is reciprocal source-binding/engineering-projection incompleteness, not permission to manufacture an Anchor Episode. No original scientific callable may be changed.

New source-only isolated exact test:
- [QBU_ANCHOR_MEMBERSHIP_VIEW_TEST_ONLY_V1.py](https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/native_candidate_v1/QBU_ANCHOR_MEMBERSHIP_VIEW_TEST_ONLY_V1.py)
- [test_qbu_anchor_membership_view_test_only_v1.py](https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/native_candidate_v1/test_qbu_anchor_membership_view_test_only_v1.py)
- [GitHub Actions source-only original LONG/SHORT 34/34 PASS](https://github.com/411244050-beep/tac-v2-a2-gate12-download/actions/runs/42172050379). Count includes inherited previous tests. Original D3 remains unchanged, full original E1/WATCH-REARM/E2 history reaches identity, original `bind_event_to_episode` on copied E2 plus genuine Episode membership yields original identity `UNKNOWN -> KNOWN` and *distinct identity per cycle*. No native Binance claim.

## NEXT native isolated execution, in this order

1. Read original Binance in-memory history and confirm current SHA baseline still unchanged. Locate exact `update_007`, `update_008`, event observation ledger, episode membership ledger, and QBU identity request builder. Preserve as-of-cutoff original event *versions*: no projecting a later resolved record into an earlier cutoff.
2. For **each of the four exact new interaction IDs** (two per direction) with `ELIGIBILITY_UNKNOWN`, show the real original event `candidate_id, trend_episode_id, direction, started_at, resolved_at, event_reference_boundary/scale`, the *one original episode* bearing this exact event ID, `AnchorEpisode.interaction_event_ids`, `validity`, `terminal_true_break`, and original UPDATE007/008 observed cutoffs. Never link by candidate identity alone. If multiple, absent, invalid, future or terminated episodes: fail closed for that event.
3. Create a cutoff-scoped **non-mutating event view** only. For a genuine original E2 with `started_at` set, `anchor_episode_id=None`, exact one source Episode member, same candidate/trend/direction, an active or provisional/valid Episode and complete cutoff history, call **original frozen** `bind_event_to_episode(E2,EP)` on a copy, not a made-up association and not a mutation of D3. WATCH or WATCH-REARM with no started_at never gets a fabricated Anchor ID. Preserve E1/WATCH-REARM/E2 history together, else `REFERENCED_INTERACTION_EVENT_MISSING` masks the eligibility result.
4. Compare source view and original D3 objects before/after to prove no mutation. Assert the projected E2 differs only by `anchor_episode_id` and leaves event ID, time, resolution, reference geometry, B3/B4, Episode members and transaction receipt untouched. Read the listed test-only view and adapt only for the current native definitions; do not overwrite native 473KB source with the older public code.
5. Re-run the **same 78 identity cutoff inputs per direction** with the repaired event-view and genuine replay-derived `rearm_predecessor_by_event_id` (E2 -> E1; never watch -> E1). Compare exact results to original frozen identity source per request. Return before/after `UNKNOWN/KNOWN/CONFLICT`, missing Anchor eligible refs, mappings nonempty/empty, and whether the prior 8 unknowns are resolved or now expose a different legitimate blocker. Never assert all 8 become KNOWN unless actual original Episode membership proves it.
6. **Then recompute the real main-loop downstream reachability from the repaired identity projection**, rather than freezing the earlier 15 B5 cutoffs. Use existing authentic call gate/ordering, not "invoke B5 at all KNOWN cutoffs". Record which of the 78 identity cutoffs now correctly call Minor/B5, exact old vs new counts, actual eligible resolved interaction consumer count, original minor material record counts, B5 state/outputs and original parity. Newly reachable cutoffs must be valid and derived from the original flow; no fake QBU.
7. Where identity mapping exists but Minor remains TRUE with zero actual material records, trace original frozen Minor source predicates using real original D2 MINOR pivots, episode start/terminal, correct-side resolution and strictly later confirmed trend-side progress. If B5 produces original QBU, only then trace actual Episode QBU writeback and next-cutoff RoleMemory; no claims from KNOWN/TRUE statuses alone.
8. Specific negative tests in the current native isolated copy: E2 missing from actual Episode.members -> UNKNOWN or fail closed; wrong candidate/trend/direction, conflicting existing Anchor ID, future resolution, duplicate divergent same event ID, terminated Episode, TRUE_BREAK, WATCH incorrectly bound, incomplete event history and rearm ancestry cycle -> appropriate original CONFLICT/UNKNOWN. Use original source outputs; never override frozen producer errors to PASS.
9. Joint durable D3+B3+RoleMemory atomic commit remains separately `BLOCKED_D3_B3_JOINT_PERSISTENCE`. A copied event view or in-memory restore does not solve native host persistence. Do not call native validate_code/spec if validators cannot accept isolated source paths; do not overwrite source for validation.

## Return required

Return actual per-direction counts from native isolated main loop:
- Four named E2 -> source Episode membership proof; any refused binding and reason;
- original identity before/after 78 cutoffs, source parity and QBU consumer counts;
- correctly newly reachable Minor/B5 calls, actual material progress, QBU/Primary/RoleMemory original output;
- negative guards, original source/AST identity;
- source SHA unchanged and any true native platform atomicity/validator capabilities.

**Do not redo already completed 160-bar B3 long/short standalone tests. Preserve original source and avoid needless model-point consumption.**
