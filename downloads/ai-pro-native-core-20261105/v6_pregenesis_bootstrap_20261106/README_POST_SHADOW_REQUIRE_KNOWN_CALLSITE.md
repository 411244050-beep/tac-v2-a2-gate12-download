# TAC V6: one-bar read-only diagnosis of post-shadow N/A require_known exception

Date: 2026-11-07. Pinned original commit 1f2499ecb84bfefea063992d48f23949c65c5578. TEST_ONLY / SYNTHETIC_FIXTURE. Do not deploy, trade or use real exchange data.

## Confirmed actual result, not to be repeated or promoted

Saved original V6 pre-genesis checkpoint exists only in the user's temporary private workspace: 13,683,812 bytes, SHA256 full original state_digest with prefix b342a5d01d3f and suffix 38a203fa, last_cutoff 73799999, 12 minor + 4 intermediate pivots, next SYNTH observer snapshot. A second temporary path is NOT durable backup. Check exact full hash from the saved previous report; never reconstruct from truncated digest.

One original outer V6 run_cutoff on SYNTH LONG bar open_time 73800000, close_time 74699999 led to TWO nested engine batches:
- raw: terminal COMMITTED, 17 stages, transaction cutoff_tx:14f19d37474397a1311065faf55ce3de, original D1ReferenceResult.
- post: terminal ABORTED_ERROR, 8 stages, textual tx identical to raw, symbol.error_reason "Value is N/A, not KNOWN". Last appended post stage was UPDATE-007 N/A with NO_D3_GEOMETRY_FOR_INTERACTION. This N/A itself is legal; it does not show where Python raised. No UPDATE-008 StageResult appended, possibly because exception occurred DURING _u008 before StageResult construction.
- Frozen original candidate producer output is 9 updates with output_digest prefix 3f207da1 suffix 6a5c. Post abort prevents the original V6 _genesis equality guard and formal_tx assignment. Do NOT claim formal_tx because raw and post batch IDs happen to match.
- No lineage operations yet, original V6 state still at pre-genesis checkpoint. D4 six-class coverage, final D4 packet, F9 UPDATE-011 NOT_REACHED this run. Retain PORT007 and D3/B3 joint persistence as independent blocks.

## Frozen original source search results

Original repaired adapter:
https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/original_d4_dependencies_20261106/nontrading_adapter_d3_d4_schema_orchestration_rc1_conformance_repair_v1.py
Git Blob ac6bf1385268fa96f2df572772ccee7e4268fd71:
- _u007 approx lines 333-343 returns legal N/A when d3_geometry absent.
- _u008 approx lines 402-479 reads original candidate_updates and calls original D3 update_008_register_candidate and update_008_anchor_lifecycle for each candidate, prior to appending final StageResult.

Actual original WP8 helper strategy_rc1/d3_boundary_intelligence/snapshots.py (inside verified frozen 91-file source):
- snapshot_from_candidate(candidate, anchor_episode_id) returns None IF candidate.availability is CandidateAvailability.UNAVAILABLE, otherwise calls candidate.boundary.require_known() and candidate.source_scale.require_known(). Original candidates.py sets both InfoValue.na and CandidateAvailability.UNAVAILABLE when a candidate is not available.
- Therefore a **duplicated CandidateAvailability enum** in the D3 snapshot helper versus the candidate instance is a plausible cause of the N/A read, as is an InfoKind/InfoValue class split or invalid candidate contract. This is ONLY a hypothesis until actual callsite and field are observed.
- Do not rewrite any guard to compare enum .value or reinterpret N/A as KNOWN. Inspect original module identity and which field invoked require_known first.

Original V6:
https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/d2_genesis_authority_handoff_20261106/live_runtime_raw_authority_extraction_packet_orchestration_binding_v6.py
Git Blob 2f12e518858be4758d81d0027c6045466ddf38f0. _post_d3_shadow approx lines 293-312 runs the second batch and throws shorthand POST_D3_SHADOW_ABORTED without underlying error_reason.
Full frozen original WP8 code and hashes:
https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/wp8_strategy_rc1_full_original_20261106/README_RECOVERY_HANDOFF.md

## Next task: exactly one original genesis bar, read-only trace

1. Before science calls, verify the actual private file bytes exist, length exactly 13683812, complete SHA256, and original V6.restore_state yields identical state_digest, last_cutoff, 12/4 pivot counts and SYNTH next snapshot. Confirm canonical loader identity and previous two import-binding fixes. If missing, return CHECKPOINT_UNAVAILABLE_OR_RESTORE_BLOCKED; **do not rebuild the earlier 82 bars**.
2. Without running any bars, inspect actual class identities and module origins for strategy_rc1.d3_boundary_intelligence.types.CandidateAvailability, original snapshots.snapshot_from_candidate.__globals__.CandidateAvailability, original frozen candidate producers, InfoValue, InfoKind and original runtime_guards.information_state. Compare via Python object identity, not matching string names or enum values.
3. Put a non-mutating observer on the actual original POST engine execution, preferably a narrowly scoped sys.settrace EXCEPTION event callback on InformationState InfoValue.require_known call and its caller, or the existing read-only run_cutoff_batch observer enriched with exception traceback. Preserve the original callable and return/throw semantics; NEVER call the original method twice. Capture actual caller co_filename/firstlineno/current lineno, traceback frames, the original field (candidate.boundary or candidate.source_scale if applicable), candidate_id/family and avail/kind identities only if visible, original exception type/message. Limit log to concise scalar fields.
4. One outer original V6 run_cutoff for SYNTH LONG genesis at open_time 73800000, close_time 74699999; cap 1 outer call, no pre-bars, SHORT, later cutoffs, or full 82+1 rerun. Nested RAW and POST engine batches are permitted inside that one call; measure actual count.
5. Observe the original _u008 candidate processing if reached. For each original candidate, record compact read-only candidate_id, family, availability enum type and whether it is the SAME canonical CandidateAvailability.UNAVAILABLE object, boundary.kind/source_scale.kind, their InfoKind class identities and whether data are genuinely KNOWN. Check for inconsistent AVAILABLE + NA or unavailable plus identity-split guard. The source line snapshot_from_candidate is an investigative hypothesis, not an established cause.
6. Stop at first real post-shadow require_known exception and give its exact original caller/field and identities; **do not auto-fix and re-run** in this diagnostic. Do not seed snapshots, fabricate known values, rewrite frozen science AST, change enum guards, alter theta, change 9-candidate digest, or promote N/A.
7. If the post-shadow unexpectedly succeeds, record post transaction and whether the original V6 equality guard actually executed before calling it formal_tx. Do not process subsequent bars or infer science beyond that same original genesis attempt.
8. Produce a brief flushed, scalar report: checkpoint restoration and full hash verified, loader/class identity, outer call count <=1, RAW/POST engine results/stages/errors, exception traceback filename/current line, candidate field/identity, candidate output digest and number, raw-vs-post IDs but formal_tx NOT ESTABLISHED if aborted, before/after V6 state_digest, lineage calls, next precise blocker. No 13MB state dump, no public checkpoint upload.

Safety: source random.Random(0) SYNTH synthetic data, not exchange market evidence. Frozen strategy.py SHA256 792d2818d8495889319de5b3e6019ac0e856d27a59c6c959ac355ff239765a5f, spec.yaml SHA256 4fb02c4559fc2fe8ee4e95390b76fce132f5af34c4f7e23a0091f1c8f8108fd1, 528 symbols unchanged, TAC_LIVE_ENABLED=0, subscriptions OFF, TEST_ONLY. No account/market/order I/O, Paper/Live, trading, deployment, performance or market authority claims. PORT007_UNRESOLVED_PRODUCTION_ALLOCATION_BLOCKED and BLOCKED_D3_B3_JOINT_PERSISTENCE remain independently blocked.
