# TAC V6: canonical CandidateAvailability BEFORE candidate construction — one genesis retry
Date 2026-11-07 | pinned original source commit 1f2499ecb84bfefea063992d48f23949c65c5578 | SYNTH-only TEST_ONLY

## Latest proven source-backed blocker

- Original V6 checkpoint at bar 82 remains 13,683,812 bytes, original full SHA256 b342a5d01d3f...38a203fa, last_cutoff 73799999, 12 MINOR/4 INTERMEDIATE pivots, next SYNTH observer snapshot; can be restored byte-exactly from user's existing private temporary path. No external durable persistence.
- One outer V6 genesis at open_time 73800000, close_time 74699999: raw shadow COMMITTED 17 stages, post-shadow ABORTED_ERROR 8 stages; source error Value is N/A, not KNOWN; after legal UPDATE-007 N/A the UPDATE-008 StageResult was not appended. The raw and post batch tx IDs are textually identical cutoff_tx:14f19d37474397a1311065faf55ce3de, but original formal_tx is NOT established while post aborts.
- Original D1ReferenceResult and 9 candidate updates were genuinely produced, earlier output_digest prefix 3f207da1...suffix 6a5c. Current run no later D4/lineage steps, V6 state unchanged after the aborted genesis.
- Measured Python class identities were SPLIT:
  * canonical strategy_rc1.d3_boundary_intelligence.types.CandidateAvailability id 94458223327360
  * frozen original strategy_rc1.d3_boundary_intelligence.snapshots uses this canonical type
  * executed flat current_qbu_singlefile snapshot_from_candidate (near line 1721) uses a second CandidateAvailability id 94458221372368
  * candidate production output's availability uses a third class (id 139843312102704, no module source), from loader-resolved candidate construction.
  * InfoValue and InfoKind class objects were each unique as observed.
- The original standalone WP8 snapshots.snapshot_from_candidate did NOT execute (observed calls zero). Thus normalize the **actual executed flat helper**, not just the dormant canonical snapshots module.
- NOTE: boundary.kind N/A alone does not establish candidate.availability. Validate the actual enum member class AND member value. The measured identity split is very strong evidence, but the complete root cause is still conditional on the actual candidate.availability identity and original callsite.
- The original candidate-production file does NOT define an independent CandidateAvailability class. It imports strategy_rc1.d3_boundary_intelligence.types as d3t, and calls cand.build_candidate; therefore its apparent third class is loader/module-instance drift in the imported graph, NOT a license to invent a new source class.

## Frozen original code anchors

Original candidate source:
https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/d2_genesis_watch_handoff_20261106/d1_d2_to_d3_candidate_production_v1.py
Git Blob aa492e3ea176ab1bb81913e299fbee01b08bff5d. It imports strategy_rc1.d3_boundary_intelligence.candidates as cand and .types as d3t. Candidate result is produced by original project_candidate_updates on raw D1ReferenceResult.

Original frozen strategy_rc1 (91 files):
https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/wp8_strategy_rc1_full_original_20261106/README_RECOVERY_HANDOFF.md
Original strategy_rc1/d3_boundary_intelligence/candidates.py sets availability to CandidateAvailability.UNAVAILABLE and both boundary/source_scale to InfoValue.na when source is unavailable (code lines approximately 33-56). Original strategy_rc1/d3_boundary_intelligence/snapshots.py snapshot_from_candidate returns None if candidate.availability is CandidateAvailability.UNAVAILABLE before reading boundary.require_known and source_scale.require_known (code lines approximately 7-11). The flat current_qbu_singlefile copy must implement the same original frozen condition and reference the same canonical enum class.

Original repaired D3 adapter:
https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/original_d4_dependencies_20261106/nontrading_adapter_d3_d4_schema_orchestration_rc1_conformance_repair_v1.py
Git Blob ac6bf1385268fa96f2df572772ccee7e4268fd71. _u008 uses original D3.update_008_register_candidate and update_008_anchor_lifecycle; original consumed frozen class identity must be preserved.

Original V6:
https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/d2_genesis_authority_handoff_20261106/live_runtime_raw_authority_extraction_packet_orchestration_binding_v6.py
Git Blob 2f12e518858be4758d81d0027c6045466ddf38f0.

## Exact next task: repair loader symbols and preflight, then one original genesis only

1. Do not immediately mutate the currently running module with already-created candidate instances. In a fresh isolated interpreter, load canonical frozen WP8 strategy_rc1 classes through the existing original relative-import rewriting loader exactly once; avoid stale sys.modules shells, duplicate flat copies, or deleted import statements. Reapply the verified original evaluate_d1_reference and ParameterState loader-symbol identity fixes, with no science source/AST change.
2. BEFORE creating any candidate, identify and verify these exact identities using Python 'is':
   - canonical = strategy_rc1.d3_boundary_intelligence.types.CandidateAvailability
   - candidate_producer.d3t.CandidateAvailability is canonical
   - candidate_producer.cand.build_candidate.__globals__["CandidateAvailability"] is canonical
   - the actual executed current_qbu_singlefile.snapshot_from_candidate.__globals__["CandidateAvailability"] is canonical (function __globals__, not merely module attribute).
   - if any other loaded D3 candidate/snapshot consumer has a separate CandidateAvailability class, normalize its importer/global symbol to canonical too. Confirm CandidateFamily, MathematicalBoundaryCandidate, TrendDirection and InfoKind/InfoValue class origins; do not force arbitrary fields to canonical if their original provenance genuinely differs.
3. Resolve this by restoring the original import/module symbol graph in the loader. If it is impossible to guarantee all source producers and executed consumers share one canonical class **before candidate creation**, report CANDIDATEAVAILABILITY_LOADER_IDENTITY_BLOCKED and stop, with no bar call. Do not alter 'is' guards, compare .value instead, manually replace candidate.availability on produced dataclasses, or synthesize boundary values.
4. Check canonical class enum members AVAILABLE/UNAVAILABLE identity and that original unavailability means InfoValue.na() in both source boundary and scale. A recorded N/A field does not alone prove candidate availability. Retain original module path, class and constant source provenance. Validate that a restored pre-genesis state has no stale candidate enum values requiring unsafe object reconstruction.
5. Validate existence and full SHA256 of the original private checkpoint bytes (13,683,812); call only original V6.restore_state on those bytes in the now unified module graph, and require full state_digest equality, last_cutoff 73799999, 12/4 pivots and SYNTH next snapshot. If checkpoint lost or restore identity/digest differs: CHECKPOINT_UNAVAILABLE_OR_RESTORE_BLOCKED, **no 82+1 fallback authorized in this run**.
6. Bound one original V6.run_cutoff(SYNTH genesis_bar), open 73800000, close 74699999; outer genesis calls exactly 1 max, prehistory calls=0, SHORT=0, later=0, never 156-window replay. Keep original nested raw/post engine batches and original invocation order, no monkeypatch of scientific functions, stage statuses, exceptions or return values. Read-only observer may record class ids, candidate fields, actual raw/post error_reason and all stage state/reason.
7. During candidate creation, for all 9 actual candidates record compact: candidate_id, candidate.availability and its class identity, boundary.kind, source_scale.kind, target timeframes and canonical class consistency. For unavailable candidates require same canonical UNAVAILABLE member and kind NA for boundary/scale as specified by frozen source. For available candidates require canonical AVAILABLE and known fields. Do not call require_known to check; inspect only. If candidate source produces invalid AVAILABLE+NA, this is a scientific-source/loader consistency BLOCK rather than a pass.
8. Inspect whether the actual flat snapshot_from_candidate guard correctly returns None on unavailable candidates and no longer calls require_known on NA boundary. If post-shadow passes, V6 itself checks post_sr.transaction_id == raw_sr.transaction_id; only after this successful return and equality guard can formal_tx be reported. An abort, even with equal text, still means formal_tx NOT_ESTABLISHED. Do not force success if any genuinely required known evidence is absent.
9. If the genesis advances into original UPDATE008, six D4 engineering source classes, static detector, final D4 packet or F9 UPDATE-011, report each exact reached stage and original result; ledger commit only on original same-tx downstream success, abort otherwise. If the next genuine blocker arises, stop, return precise first error, no same-task fix and retry, no next cutoff.
10. Verify whether original candidate output_digest exactly matches the previously recorded 3f207da1...6a5c. WARNING: original producer encodes Enum class module/qualname in digest; fixing class identity/provenance can change binary digest even if visible candidate fields and scientific meaning match. Any drift requires output-by-output original source/digest provenance comparison and clear report, NEVER blindly claim unchanged digest, hardcode expected digest, or conceal identity differences. Retain exact original output if legitimate and no science drift established.
11. Report scalar summary and explicit flush: checkpoint proof; full source original module/blob identity; canonical availability class objects across producer, build_candidate and actual flat snapshot helper; all 9 candidate identities/availability and fields; raw/post actual terminal, stage table, first error_reason; raw/post tx comparison and formal_tx status; D4/F9/lineage reached/NOT_REACHED; original state before/after and measured outer call count.

Safety: all input records are random.Random(0) SYNTH fixture, not real market data. strategy.py SHA256 792d2818d8495889319de5b3e6019ac0e856d27a59c6c959ac355ff239765a5f; spec.yaml SHA256 4fb02c4559fc2fe8ee4e95390b76fce132f5af34c4f7e23a0091f1c8f8108fd1. 528 frozen symbols, TAC_LIVE_ENABLED=0, subscriptions OFF, TEST_ONLY. No exchange market/account/order I/O, no Paper/Live, trading, saving/deploying strategy, or real-market signal claim. PORT007_UNRESOLVED_PRODUCTION_ALLOCATION_BLOCKED and BLOCKED_D3_B3_JOINT_PERSISTENCE independently remain blocked.
