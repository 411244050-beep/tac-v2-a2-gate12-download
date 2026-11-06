# TAC TEST_ONLY: D1ReferenceResult and formal transaction bridge
Date: 2026-11-06 | Pinned original source commit 1f2499ecb84bfefea063992d48f23949c65c5578

## Current real measured blocker

LONG genesis cutoff 74699999; original WATCH TRUE, lineage KNOWN_START_FIRST_EVENT and 7 refs; source classes 4 COMPLETE / 2 UNKNOWN; source association BLOCKED_CRITICAL_UNKNOWN; final D4/F9 UPDATE-011 NOT_REACHED; lineage commit 0, abort 1. Preserve this without re-running 78 cutoffs.

Verified original candidates.py SHA256 1dc00db7b7b61baee66129fad072e08e6db0ef3a7f7ce9c5f363c5a68f7fe0ec is present in the 91-file WP8 archive. The original relative-import rewriter loads it successfully only after removing a stale empty sys.modules shell; the loader must avoid duplicate types and maintain the same original module instance. This is solved.

Two remaining causes:
- CandidateProductionRequest.d1 got an adapter local CanonicalizationResult, but original candidate producer requires D1ReferenceResult with canonical_records and math_15m/math_1h/math_4h.
- No official formal_tx was visible from a post-UPDATE-008 local-scope probe; looking for tx/formal_tx in that scope returned nothing. This is an observation-point error, not absence of engine tx.

## Verified original source references

1. [Original V6 raw authority orchestration](https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/d2_genesis_authority_handoff_20261106/live_runtime_raw_authority_extraction_packet_orchestration_binding_v6.py) Git blob 2f12e518858be4758d81d0027c6045466ddf38f0. The _raw_shadow routine approximately lines 261-291 runs the original deterministic cutoff engine with the exact adapter snapshot, then gets sr = result.symbol_results[0], retrieves cache = adapter.tx_cache[sr.transaction_id], and *checks cache.d1 and cache.d2 non-None*.
2. In the same V6 _genesis, lines ~415-435, candidate producer request is built from d1=raw_cache.d1 (NOT a CanonicalizationResult local), target_trend=raw_cache.d2.update_006_trend and the causal pre-D3 interactions. Candidate transaction ID is raw_sr.transaction_id + ":CANDIDATE".
3. Original initial packet is produced from the exact candidate result; then post_sr = _post_d3_shadow(bar, initial). The source explicitly checks post_sr.transaction_id == raw_sr.transaction_id, and sets formal_tx = post_sr.transaction_id. Later complete Update008 is obtained through b5_rt.process_update008(formal_tx + ":U8", u8_req); same formal_tx is used in Update008:<formal_tx> original source reference and the subsequent staged F9 engine.
4. [Original D1D2D3 candidate production V1](https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/d2_genesis_watch_handoff_20261106/d1_d2_to_d3_candidate_production_v1.py) Git blob aa492e3ea176ab1bb81913e299fbee01b08bff5d. CandidateProductionRequest.d1 is typed D1ReferenceResult. The original code accesses d1.canonical_records and d1.math_*; it does NOT accept CanonicalizationResult.
5. [Original 91-file strategy_rc1 WP8 archive, checksum manifest, loader inputs](https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/wp8_strategy_rc1_full_original_20261106/README_RECOVERY_HANDOFF.md).
6. [Original pure WATCH and six-class source requirements](https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/d2_genesis_watch_handoff_20261106/README_WATCH_COVERAGE_FINISH.md).

## Next exact work — one bounded LONG genesis only

A. Use the **original WP8 relative-import rewriting loader** in a NEW isolated process or safe clean namespace, without hand-set package aliases, duplicate enums, or stale empty sys.modules objects. Do not switch back to the failed native import workaround. Verify single canonical frozen D1ReferenceResult class, TrendDirection, D3 types and B5 RoleRuntimeOutput; do not change scientific function AST.

B. Stop probing locals AFTER UPDATE-008. Instrument the exact frozen *upstream engine* boundary on the chosen LONG genesis bar (the same bar already in the offline 160-bar set). Capture at the real SymbolCutoffResult/StageContext boundary:
- raw_sr = raw_result.symbol_results[0] and raw_sr.transaction_id;
- raw_cache = raw_adapter.tx_cache[raw_sr.transaction_id];
- raw_cache.d1 and raw_cache.d2 exact type, source cutoff, original class identity and existing canonical_records/math_15m;
- original ctx.transaction_id at the initial stage if available.
Use original V6 _raw_shadow(bar) as the reference **in a copy of the isolated state**, not on a live or previously committed ledger.

C. Confirm that raw_cache.d1 is the **same original D1ReferenceResult instance/type** required by the frozen candidate producer; its canonical_records must come from real previous 160 offline closed bars, not fabricated from canonicalization metadata. If raw_cache.d1 is not the expected frozen type, trace the original D1 _u001/_u002 materialization and call the frozen D1 reference producer only via its documented original interface. Do not manufacture D1 math or rewrite expected candidate schema. Preserve no future bars. If cannot source it, return D1_REFERENCE_OUTPUT_OR_STAGE_BOUNDARY_BLOCKED with exact type and missing upstream source.

D. If D1 is genuine, invoke original frozen D1D2D3CandidateProductionRuntimeV1.project_candidate_updates with source D1, actual D2 trend and the existing original 3 D3 pre-events; candidate request ID is raw_sr.transaction_id + ":CANDIDATE". Capture its true output_digest and state/refs, with original prebar snapshot count 0. Then create exact initial packet through original initial_authority_from_frozen_producers.

E. Run original V6 _post_d3_shadow(bar,initial) in the SAME isolated source state. Get post_sr.transaction_id from post_result.symbol_results[0]; assert equality with raw_sr.transaction_id. Only then formal_tx = post_sr.transaction_id. If missing after actual engine stage, return FORMAL_TX_OR_STAGE_BOUNDARY_BLOCKED with exact last stage entry/return, rather than searching in post-UPDATE008 locals or generating deterministic fake strings.

F. Use original complete b5prod.Update008Output produced with formal_tx+":U8" in this actual source path. Strictly distinguish original science state UNKNOWN from engineering coverage: prove Update008:<formal_tx> and F9 stage provenance before tagging its source coverage COMPLETE. Do not forge provenance from a summary object. Preserve prior verified role-runtime 12-field normalization audit, but prefer canonical original producer class; if inconsistent enum/type or drift in field values, BLOCK.

G. With genuine CandidateBatch:<digest> and verifiable no prebar snapshot / no active B4 interaction, re-evaluate exact six D4 source classes (4 previous complete + remaining 2), original pure-WATCH reconciliation and static authority. If any source missing, UNKNOWN. If READY then original Assembler V2 final D4 packet before UPDATE-011, execute same formal_tx F9 stages, verify terminal/stage order/packet phase and only then commit lineage. Otherwise abort. If successful, inspect immediately next cutoff ONLY; never treat an aborted prepare as committed history.

H. Return: loader identity; original D1 type and canonical source cutoff; raw_sr tx and post_sr tx consistency (can redact ID text but state exact checked origin); candidate output_digest and producer counts; true full UPDATE008 provenance and unchanged UNKNOWN; six source class statuses/refs; static status; D4 final packet/F9 UPDATE-011 reached or NOT_REACHED; lineage commit/abort and exported ledger; tiny summary flush and explicit process exit. Do not re-run 78-cutoff or 156-call tests.

Safety: TEST_ONLY isolated memory, 528 frozen symbols, TAC_LIVE_ENABLED=0, subscriptions off, no market/account/order I/O, no saved deployment/Paper/Live/trades, no synthetic evidence promotion. Frozen strategy.py SHA256 792d2818d8495889319de5b3e6019ac0e856d27a59c6c959ac355ff239765a5f; spec.yaml SHA256 4fb02c4559fc2fe8ee4e95390b76fce132f5af34c4f7e23a0091f1c8f8108fd1. PORT007 allocation and D3/B3 joint durable persistence remain independent blockers.
