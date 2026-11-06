# TAC V6: unify MechanismProducerOutputs class identity, then at most one SYNTH genesis
2026-11-07 | Frozen original source commit: 1f2499ecb84bfefea063992d48f23949c65c5578 | TEST_ONLY

## Verified exact contract and latest observation

Latest synthetic random.Random(0) / SYNTH test completed one outer V6 genesis cutoff (open_time=73800000, close_time=74699999), with no prehistory calls, SHORT or future cutoffs. Previously reconstructed bar-82 checkpoint was restored from 13,683,812 real bytes; its full SHA256 matched V6.state_digest (prefix b342a5d01d3f...suffix 38a203fa); last_cutoff 73799999, 12 minor / 4 intermediate, next SYNTH snapshot exists. This private workspace checkpoint is NOT durable storage and is NOT in the public repository.

Original raw and post shadows both reached terminal COMMITTED, 17 stages each, and had matching transaction ID cutoff_tx:14f19d37474397a1311065faf55ce3de. Candidate producer returned 9 original updates with digest 3f207da1...6a5c. Availability diagnostics across two batches: 8 AVAILABLE snapshot-producing observations and 10 UNAVAILABLE observations returning None; require_known N/A exception absent. IMPORTANT: these 18 observations reflect 9 candidates across 2 internal batches, NOT 18 distinct candidate products.

Original V6 genesis passed its post/raw transaction equality check and assigned a local formal_tx to the same string; however the overall genesis has NOT successfully committed. It constructed a frozen Watch mechanisms payload and called lineage.prepare once, then threw LineageProductionConflict("MECHANISM_PRODUCER_OUTPUTS_SCHEMA"). No lineage pending projection was successfully prepared/committed and no abort call. V6 state digest remained checkpoint; no persistent strategy state, final D4 packet or F9 UPDATE-011 reached. PORT007 and D3/B3 joint persistence remain independent blockers.

This conflict is an EXACT Python isinstance contract at original lineage production source _validate_request, approximately lines 334-350:

if not isinstance(req.mechanisms, assembler.MechanismProducerOutputs):
    raise LineageProductionConflict("MECHANISM_PRODUCER_OUTPUTS_SCHEMA")

Original V6 _genesis around lines 590-609 constructs:

mechanisms = assembler.MechanismProducerOutputs(trend_establishment_watch=watch)
lineage_req = lineage_prod.D4LineageProductionRequest(... mechanisms=mechanisms, ...)

This validates only the class identity at that guard, NOT the presence/absence of a required mechanism field. A duplicated class object from loader/module identity drift is the leading hypothesis. Do not invent missing mechanism output fields or change the WATCH evidence science to work around it.

Pinned frozen sources and Git Blob IDs:
- V6, Git Blob 2f12e518858be4758d81d0027c6045466ddf38f0: https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/d2_genesis_authority_handoff_20261106/live_runtime_raw_authority_extraction_packet_orchestration_binding_v6.py
- Lineage v2, Git Blob f334155bbb46ec2ff0ee748555cb15c1485d3036: https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/d4_market_event_lineage_binding_20261106/d4_market_event_lineage_production_binding_v2.py
- D3/D4 assembler v2, Git Blob a5f2b841cb44f9ff759232cc3ae72ff844cee02b: https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/original_d4_dependencies_20261106/authoritative_d3_d4_evidence_packet_assembler_resumption_v2.py
- Frozen V6 bootstrap checkpoint protocol: https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/v6_pregenesis_bootstrap_20261106/README_POST_SHADOW_REQUIRE_KNOWN_CALLSITE.md

## One narrow and defensible next task

1. No K line calls yet. In a clean single-namespace WP8 original loader environment, check the ORIGINAL constructor class used by V6 _genesis, and the class expected by lineage _validate_request (both from the exact function __globals__ module aliases, not only module attributes):
   - v6asm = LiveRuntimeRawAuthorityOrchestrationV6._genesis.__globals__["assembler"]
   - linfunc = lineage_prod._validate_request
   - linasm = linfunc.__globals__["assembler"]
   - expected = linasm.MechanismProducerOutputs
   - constructed_type = v6asm.MechanismProducerOutputs
   - verify constructed_type is expected and v6asm is linasm, printing class id, __module__, source co_filename, dataclass fields, Git Blob/source provenance.
   - Verify the actual req.mechanisms class when the original request is constructed. If the first two checks already prove different classes before the run, there is no need to spend a bar to rediscover it.
2. Also inspect all other required original schema class identity boundaries in this same request (D4LineageProductionRequest, TrendEstablishmentRecord, InteractionEvent, WatchProjection, candidate data, original EvidenceState) as read-only preflight. Previous CandidateFamily, MathematicalBoundaryCandidate and TrendDirection each had two class copies; do not blindly patch them without a concrete original constructor-consumer mismatch. Record and preserve actual class provenance.
3. If and ONLY if exact original assembler class objects are demonstrably duplicated due to loader import graph, fix the loader/module aliases so the original V6, lineage producer, V3 and packet assembler use ONE canonical original MechanismProducerOutputs class object; also ensure the actual callable globals resolve to the same original module. No replacement dataclasses, no coercing instances, no monkeypatching isinstance, no scientific code edits, no field synthesis and no changing any WATCH/UNKNOWN/CONFLICT information values. If the discrepancy cannot be resolved with source-verifiable import identity only, return MECHANISM_SCHEMA_LOADER_BOUNDARY_BLOCKED without any bar call.
4. Verify WATCH is the original actual b5prod.produce_trend_establishment_watch(record,..), with true original TrendEstablishmentRecord provenance and no artificial effect. An instantiation of MechanismProducerOutputs(trend_establishment_watch=watch) with original frozen classes should satisfy lineage's exact isinstance guard in dry preflight WITHOUT calling lineage.prepare on an artificial request.
5. Verify the real saved private checkpoint exists and matches full previous SHA256 byte-for-byte (13,683,812 bytes). Restore only via original LiveRuntimeRawAuthorityOrchestrationV6.restore_state(raw); check exact full digest, last_cutoff=73799999, pivots 12/4 and SYNTH next snapshot. If file missing or byte/identity mismatch, report CHECKPOINT_UNAVAILABLE_OR_RESTORE_BLOCKED and do not reconstruct 82 pre-bars in this task.
6. Once constructor/consumer type identity is proven and checkpoint restored, authorize exactly one V6.run_cutoff on the SYNTH genesis bar open_time 73800000 close_time 74699999. Count outer calls <=1, prehistory 0, SHORT 0, future 0. The original frozen code may run raw, post and formal internal engine batches; count each separately. No 156-cutoff replay, no one-bar repeat, and no do-over after a new exception.
7. Observe the genuine 9 candidates and output_digest, raw/post terminals and transaction ids. Correctly distinguish the original LOCAL formal_tx value after original post equality guard from the later successful lineage prepare/commit and staged engine transaction. Do not call overall genesis committed merely because local formal_tx exists.
8. If lineage.prepare completes, capture authentic projection, relation, source coverage and the next real original V6 stage. Let the ORIGINAL same-cutoff flow continue into its frozen D4 static projection, packet assembler, and formal staged F9 UPDATE-011 only if original guards actually allow it. If staged formal engine aborts, preserve its frozen abort behavior; never force lineage commit. On the first new error, stop and record exact error type/field/traceback; do not fix and retry in this task.
9. If genesis ultimately returns GENESIS_FULL_TYPED_STAGED, verify immutable source visibility gates, initial-vs-final packet, lineage.prepare and commit, final state digest, original F9 stage order; report it as a SYNTHETIC ENGINEERING SUCCESS ONLY. Even a success does not resolve PORT007 or D3/B3 persistence and is not real-market/trading validation.
10. Report a concise scalar diagnostic: complete checkpoint SHA and restore check, all class ids and original module origins, actual constructor/consumer isinstance result, original Watch type/provenance, call counters, candidate count/digest, raw/post/local formal/staged tx outcomes, lineage prepare/commit/abort, D4 coverage/final packet/F9 actual stages vs NOT_REACHED, V6 state before/after, and exact next blocker.

Safety: all inputs are SYNTH random.Random(0) synthetic fixture, NOT market history. Immutable strategy.py SHA256 792d2818d8495889319de5b3e6019ac0e856d27a59c6c959ac355ff239765a5f, spec.yaml SHA256 4fb02c4559fc2fe8ee4e95390b76fce132f5af34c4f7e23a0091f1c8f8108fd1; 528 original symbols; TAC_LIVE_ENABLED=0 and subscriptions OFF. TEST_ONLY, no real market/account/order interfaces, Paper/Live, deploying/saving strategy, trades, outcomes or real market assertions. PORT007_UNRESOLVED_PRODUCTION_ALLOCATION_BLOCKED and BLOCKED_D3_B3_JOINT_PERSISTENCE remain independently blocked.
