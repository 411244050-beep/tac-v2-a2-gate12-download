# TAC V6 single-bar D1 NameError import repair (2026-11-06)

**Scope: TEST_ONLY, SYNTHETIC_FIXTURE, exactly one original bar invocation. No real market evidence.**

## Confirmed latest diagnosis

Original frozen V6 single-bar random.Random(0) fixture at close_time=899999 (no mutation to time convention):
- UPDATE-000 PASS, UPDATE-001 PASS, UPDATE-002 N/A, reason NO_CAUSAL_PREBAR_BOUNDARY_SNAPSHOT.
- Frozen engine terminal ABORTED_ERROR because its error_reason says: `name 'evaluate_d1_reference' is not defined`.
- Original adapter method `AdapterIntegrationRuntime._ensure_d1` in in-memory module `nontrading_adapter_integration_v1.py`, reported first line 400, references global evaluate_d1_reference, but that exact function globals namespace does not bind it.
- Original `strategy_rc1.wp1_reference.evaluate_d1_reference` is present, supplied in the 91-file original package.
- UPDATE-002 N/A is a legal frozen StageState and NOT the root cause. Note original V6 diagnostic logger filters `("PASS","NA")` but N/A enum value is `"N/A"`, causing a legal stage to appear among failure details. Fix diagnostic presentation only (if needed in external logger), not frozen StageState/engine.
- V6 has not reached original D1, candidate digest, formal_tx or genesis. No ledger commit. These are synthetic fixture engineering tests, not source-backed exchange data.

## Actual repair instructions

1. Use a **new clean isolated interpreter** and the verified original WP8 relative-import rewriting loader. Install the verified full original strategy_rc1 package and original minimal/adapter dependencies before loading original nontrading_adapter_integration_v1. Do not leave a stale empty sys.modules shell or a second module instance.
2. Inspect the exact original adapter import statement/loader transform that supplies `evaluate_d1_reference`. Correct only the **module import namespace construction**, so that the function referenced by `AdapterIntegrationRuntime._ensure_d1.__globals__["evaluate_d1_reference"]` is **the SAME function object** as the already-verified `strategy_rc1.wp1_reference.evaluate_d1_reference` from that runtime's sole canonical original module instance.
3. Do not create a wrapper or alternative evaluation function, change original scientific AST, bind from a second copy of wp1_reference, alter candidate/D1 schema, turn N/A into PASS or seed a prebar snapshot. If the *unmodified original adapter source* genuinely lacks an import for this required symbol, report the exact import boundary and only apply a strictly isolated non-scientific loader-binding repair; document original source SHA / binding provenance and demonstrate no callable/science code changed.
4. Before any bar, verify original class identity, `_ensure_d1.__globals__` binding, `evaluate_d1_reference` source module and function identity. A static preflight may check other missing **LOAD_GLOBAL** identifiers (not every `co_names` attribute) without running science. If an unresolved name remains, report exact owner first; do not add arbitrary globals.
5. Execute ONLY one original `rt=LiveRuntimeRawAuthorityOrchestrationV6(); rt.run_cutoff(first_bar)` invocation on the existing exact random.Random(0) synthetic first bar close_time=899999, not full 82+1, not stair fixture, not a 156-cutoff batch. Capture full `result.error_reason` and 3+ stage table if available, plus `mode`/terminal/state_digest. Expect **nothing** unless measured; RAW_PRETREND is a testable target, not an invented result. If another genuine missing symbol or block appears, stop at first error and report it.
6. Preserve immutable strategy.py SHA256 `792d2818d8495889319de5b3e6019ac0e856d27a59c6c959ac355ff239765a5f`, spec.yaml SHA256 `4fb02c4559fc2fe8ee4e95390b76fce132f5af34c4f7e23a0091f1c8f8108fd1`, all 528 frozen symbols, TAC_LIVE_ENABLED=0, subscriptions OFF. No account/market/order APIs, no deployment, no Paper/Live/trades. Preserve independent PORT007 and D3/B3 joint-persistence blockers.

**Public original sources**
- V6: https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/d2_genesis_authority_handoff_20261106/live_runtime_raw_authority_extraction_packet_orchestration_binding_v6.py
- Frozen strategy_rc1 archive: https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/wp8_strategy_rc1_full_original_20261106/README_RECOVERY_HANDOFF.md
- Original adapter transport: https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/original_d4_dependencies_20261106/nontrading_adapter_integration_code_bundle_v1.tar.xz.b64
- Prior first-bar diagnostic: https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/v6_pregenesis_bootstrap_20261106/README_FIRST_BAR_ABORT_DIAGNOSTIC.md

Report exact bound object identity, first-bar outcome, actual run count (<=1), first next blocker and unchanged safety; no more than one bar.
