# TAC V6 bounded bootstrap: 82 pre-genesis bars + 1 LONG genesis

2026-11-06. Original code pinned to private 411244050-beep/tac-v2-a2-external-runtime commit 1f2499ecb84bfefea063992d48f23949c65c5578. Only isolated TEST_ONLY, never deployed.

## Current verified facts, avoid repeat tests

Previous LONG genesis cutoff 74699999 has original WATCH TRUE and lineage prepare KNOWN_START_FIRST_EVENT with 7 causal refs, but lineage commit=0, abort=1. D4 static 4 COMPLETE / 2 UNKNOWN (candidate/D1 and UPDATE008/formal_tx); final D4 / F9 UPDATE-011 NOT_REACHED. Previous instrumented real engine call was located AFTER early exit, so its capture was None. Removing that early exit accidentally executed all 156 rows: this was an out-of-scope engineering incident and is not new source evidence. Never repeat that method or probe patch-local strings.

The original offline source reportedly has 160 closed 15m bars: 82 earlier bars and 78 F9-window bars. The genesis is first F9 bar, LONG cutoff 74699999 (open_time 73800000). Verify all actual source bytes and bar times, do not create fictitious bars or shift timestamp conventions to match a test.

## Published exact ORIGINAL dependencies

- V6 original raw authority orchestration Git Blob 2f12e518858be4758d81d0027c6045466ddf38f0: https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/d2_genesis_authority_handoff_20261106/live_runtime_raw_authority_extraction_packet_orchestration_binding_v6.py
- Original V6 test Git Blob 62afcda795b2b372b46158b1d32e4b6ab4f3e8e4: https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/v6_pregenesis_bootstrap_20261106/test_live_runtime_raw_authority_extraction_packet_orchestration_binding_v6.py
- Original minimal_runnable_v1_baseline source bundle Base64 Git Blob c5d9f08b79fa96d76e819eecbc1097551262d5ba: https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/v6_pregenesis_bootstrap_20261106/minimal_runnable_v1_baseline_code_bundle_v1.tar.xz.b64
- Original engine manifest Git Blob d38bd43c6e0cf8d270c3196b87f2d863d0fd45e3: https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/v6_pregenesis_bootstrap_20261106/minimal_runnable_v1_baseline_manifest_v1.json
- Original V3 staged authority binding Git Blob fa9842eab6851c2bb67f2f32ec09b20514271018: https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/v6_pregenesis_bootstrap_20261106/live_runtime_authority_extraction_packet_orchestration_binding_v3.py
- Original nontrading adapter bundle Git Blob add54fa0fb0749cf13ffae520fb6cd8181640302: https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/original_d4_dependencies_20261106/nontrading_adapter_integration_code_bundle_v1.tar.xz.b64
- Original verified 91-file WP8 strategy_rc1 and hash manifest: https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/wp8_strategy_rc1_full_original_20261106/README_RECOVERY_HANDOFF.md
- Original candidate producer Git Blob aa492e3ea176ab1bb81913e299fbee01b08bff5d: https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/d2_genesis_watch_handoff_20261106/d1_d2_to_d3_candidate_production_v1.py

The original engine transport manifest expects encoded Base64 SHA256 7dde0b5672f23e122d7af9914a27e8c1862017309c667f1ba9e2f9d65d86c91e, decoded XZ SHA256 1d1c02cfae34b28fc6e51de0622bd4784220410716082264939489c172b4d742, decoded tar SHA256 1330210481181e324c7be0aefd33b034c08b7ffd2441e3e400c859449ff0eedc, extracted minimal_runnable_v1_baseline.py SHA256 84b2f0e53f6ae6b4916d4b400568a1f382dee82b2e8990775a914aa3124f3a75. Decode into isolated folder and verify; do not run original V6 tests as source authority for the current 160 bars.

The original V6 constructor LiveRuntimeRawAuthorityOrchestrationV6() builds a fresh original frozen adapter, ledger, candidate, B5, platform and lineage state. Its run_cutoff(bar) calls original _raw_shadow, returns RAW_PRETREND for bars before first trend episode, and dispatches _genesis at the actual creation cutoff. Original test drive_to_genesis demonstrates chronological bootstrap from a new runtime on its own synthetic fixture. This confirms a state file is not intrinsically required by that code, NOT that this separate current dataset must succeed.

## Hard bounds and preflight, enforce before any science call

Only use the SAME authenticated offline LONG input bars. Check source identity, closed status, exact chronological time ordering, no duplicate or future bar, canonical continuity, frozen parameter snapshot and symbol. Require exactly 82 source bars before a real genesis_bar with close_time 74699999, and no conflict with already-proven D2 trend episode/pivot provenance. No on-demand market API download.

Construct a finite allowed input tuple of EXACTLY 83 elements: first 82 true pre-genesis closed bars + the one LONG genesis bar. Do not use a for-loop over all 160 bars, a 78-cutoff F9 window, or a dynamic loop until some future signal.

Guard counters AT the original outer run_cutoff boundary, not via a post-loop early return:
- original pre-genesis run_cutoff calls <=82;
- LONG genesis attempts <=1;
- any later LONG cutoff 0, all SHORT cutoff calls 0;
- total authorized original bar inputs <=83;
- hard fail on a 84th bar, any unexpected episode creation, any source mismatch or first failed prehistory stage.

No override of strategy.py or spec.yaml, no fake fields/objects/tx, no monkeypatch of scientific function bodies, no duplicate original dataclass/enum module instances. Use fresh isolated process and existing verified WP8 relative-import rewriter, removing stale empty sys.modules shells before load. Preserve original source/class identity.

## One exact V6 prehistory bootstrap

1. Create a fresh original LiveRuntimeRawAuthorityOrchestrationV6() with its empty initial state. Chronologically process ONLY the 82 source bars preceding cutoff 74699999 through original run_cutoff(bar). Each must return RAW_PRETREND. Its original _commit_raw records adapter state, prior D1/D2 history and intermediate pivots. If earlier genesis/terminal/divergence appears, stop PREHISTORY_RECONSTRUCTION_DIVERGENCE, with the first exact cutoff; do not force RAW_PRETREND.
2. Record exactly after these 82: original state_digest, last_cutoff, canonical source segment, actual minor/intermediate pivot IDs and source counts. Confirm all come from source bars, no D1 or D2 injected state. Compare with prior known LONG genesis expected typed provenance; if incompatible, report PREGENESIS_STATE_NOT_EQUIVALENT and stop.
3. Now perform ONLY ONE genesis-bar original V6 path. Preferred: one rt.run_cutoff(genesis_bar) with a read-only observer on actual original V6 method return boundaries _raw_shadow and _post_d3_shadow; capture original sr and tx_cache results and original candidate producer output without mutating them. Alternative: call original _raw_shadow(genesis_bar) once, then call original _genesis(bar=genesis_bar,raw_result=...,raw_sr=...,raw_cache=...) on the same untouched prestate. These are alternatives, DO NOT run both routes and DO NOT call run_cutoff again for the same bar.
4. Check original raw_cache.d1 is true frozen D1ReferenceResult with canonical_records, math_15m, math_1h, math_4h, not adapter CanonicalizationResult. Original candidate producer must receive this exact D1; capture genuine cand_result.output_digest and original candidate tx suffix :CANDIDATE. Check post_sr.transaction_id == raw_sr.transaction_id; then formal_tx is real post_sr.transaction_id. Do not infer identity from patch-local variables.
5. Verify genesis D2 trend episode ID trend_episode:4787bf50819e003d7d7642c87b78febc, frontier pivot pivot:bdd335165ad18f3492619e26189cce26, source pivot identities and direction LONG (from same class instance). These are expected comparisons from previous actual results, NOT fields to insert. A mismatch is GENESIS_SOURCE_ID_DRIFT and stops further admission.
6. Re-evaluate exact six original D4 source coverage classes, including genuinely produced CandidateBatch digest and Update008:<formal_tx> source. Original UPDATE008 scientific UNKNOWN remains unchanged. If any source not authentically present, keep UNKNOWN. If static READY, original V6 must assemble final D4 and run real single-cutoff F9 stages with original packet phase: initial through UPDATE-010, final from UPDATE-011; commit lineage ONLY after same-transaction downstream success. Abort on failure, no external persistence claim.
7. If original V6 cannot import or bootstrap, stop and report exact missing original dependency, first failing cutoff, original error. Do not return to previously failing patch-local engine hook and do not remove existing early returns. No unbounded fallback.

## Required report

Exact number of offline bars processed (<=83), per-direction count (LONG genesis <=1, SHORT 0), first failure cutoff, original class identities, raw D1 source and math counts, actual candidate digest, raw/post engine transaction IDs equality, original genesis pivot source match, six effective coverage statuses, D4 final and F9 UPDATE-011 reached or NOT_REACHED, lineage prepare/commit/abort, scalar summary flushed and normal process exit. Retain all independent blockers.

Immutable host boundary: strategy.py SHA256 792d2818d8495889319de5b3e6019ac0e856d27a59c6c959ac355ff239765a5f, spec.yaml SHA256 4fb02c4559fc2fe8ee4e95390b76fce132f5af34c4f7e23a0091f1c8f8108fd1. 528 symbols, TAC_LIVE_ENABLED=0, subscriptions OFF, TEST_ONLY. No account/market/order I/O, Paper/Live, trades, strategy save or deployment. PORT007_UNRESOLVED_PRODUCTION_ALLOCATION_BLOCKED and BLOCKED_D3_B3_JOINT_PERSISTENCE remain independent. Original synthetic V6 unit tests do not prove market-sourced evidence.
