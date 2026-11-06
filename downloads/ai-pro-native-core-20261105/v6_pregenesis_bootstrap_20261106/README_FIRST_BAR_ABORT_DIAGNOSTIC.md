# TAC V6 first-bar abort: source-classification and causal prebar diagnosis (2026-11-06)

## Corrected evidence labels

The previously tested 160-bar "SYNTH" 15m input is **random.Random(0) synthetic fixture**, not historical exchange data. Prior WATCH TRUE, START_FIRST_EVENT, 7 lineage refs, 4/6 source-coverage COMPLETE are **engineering/synthetic fixture observations only**. They do not validate real-market event identity, market history coverage, trade readiness, or performance. Never promote them to real market authority.

V6 complete import chain is now verified; previous two original QBU modules were already located in frozen_evidence_producers_v1. Latest strict 82+1 test attempted only **one bar**, cutoff **899999**; V6 _raw_shadow failed closed with frozen stage UPDATE-002 state N/A reason NO_CAUSAL_PREBAR_BOUNDARY_SNAPSHOT, overall batch terminal ABORTED_ERROR. V6 state stayed unchanged; LONG genesis not reached, no candidate/formal_tx/ledger commit. No new D4 science established. A past 156-row unintended replay remains an out-of-scope engineering incident.

## Key distinction before any implementation

The frozen V6 test *does* demonstrate original code starting with an empty LiveRuntimeRawAuthorityOrchestrationV6() and processing SYNTH stair bars via run_cutoff until RAW_PRETREND then genesis. Therefore "V6 structurally cannot cold start" is **not established** merely because this different random fixture's first cutoff aborts.

Check the *entire* original engine SymbolResult and terminal error path. Stage UPDATE-002 returning N/A does not by itself prove UPDATE-002 is the cause of ABORTED_ERROR. Inspect every stage's state and reason and the first ERROR, exception, or wrong terminal handling. Frozen V6 _raw_shadow explicitly computes details for stage state outside PASS/NA, then raises RAW_SHADOW_ABORTED with repr(result). Report this complete error chain; do not infer root cause from one N/A label.

Source references:
- Original V6 orchestration (source Git blob 2f12e518858be4758d81d0027c6045466ddf38f0):
https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/d2_genesis_authority_handoff_20261106/live_runtime_raw_authority_extraction_packet_orchestration_binding_v6.py
- Original V6 test with cold-start and explicit SYNTH stair fixture (Git blob 62afcda795b2b372b46158b1d32e4b6ab4f3e8e4):
https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/v6_pregenesis_bootstrap_20261106/test_live_runtime_raw_authority_extraction_packet_orchestration_binding_v6.py
- Minimal original engine bundle (Git blob c5d9f08b79fa96d76e819eecbc1097551262d5ba):
https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/v6_pregenesis_bootstrap_20261106/minimal_runnable_v1_baseline_code_bundle_v1.tar.xz.b64
- Previous strict bounded 82+1 handoff:
https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/v6_pregenesis_bootstrap_20261106/README_STRICT_V6_BOOTSTRAP_82_PLUS_ONE.md

## One bounded next diagnostic — no wide replay

1. Confirm the currently loaded V6/minimal/repaired adapter class identity, 91-file WP8 SHA256, and exact generator/parameter snapshot for random.Random(0). Explicitly label all data SYNTHETIC_FIXTURE.
2. For the **single first failing bar** close_time=899999, capture scalar stage table: step, StageState, reason, exception, next-bar snapshot existence/reference eligibility, and batch terminal reason. Capture exact V6 RawV6Block message including any RAW_SHADOW_ABORTED details and no-output-state digest. Instrument returned engine objects in original V6 _raw_shadow, not the post-UPDATE008 patch-string scope. Run only this one bar, not 82+1 until blocker is understood.
3. Compare with the ORIGINAL V6 test's **first SYNTH stair bar** under identical frozen modules, but explicitly keep its input generator separate. Original test fixture close_time=(i+1)*900000; current random fixture reports close_time=i*900000+899999. This 1 ms difference is a discrepancy to investigate, **not** authorization to silently rewrite bar close_time. Check all source origin/canonical parameter assumptions and whether original test has different prebar eligibility.
4. Source-level trace the frozen UPDATE-002 handler and DeterministicCutoffEngine state-machine to distinguish legitimate N/A (no eligible prebar) from true batch ABORTED_ERROR, including whether later stage unexpectedly needs prebar. Do not alter PASS/NA/ERROR semantics or change strategy science.
5. If a legal original prebar snapshot is truly required, identify its **existing original-producing previous cutoff** and source/history, and show exact eligibility/ledger constraints. Do not fabricate or seed a D3 snapshot, empty state or an opportunity. If no legal existing snapshot can be built for the particular fixture, leave fail-closed and report COLD_START_PREBAR_AUTHORITY_NOT_AVAILABLE.
6. After the first-bar issue has been demonstrated resolved on a legitimate original fixture, the **next** test remains strictly bounded by <=82 original prehistory bars plus <=1 LONG genesis bar, SHORT=0, later=0. Abort immediately on any early genesis, identity drift, or unexpected error. Do not remove early return, repeat the past 156-row overrun, or perform any live-market download.
7. Only if original D1ReferenceResult and original engine transaction IDs become reachable may original candidate production and six-class D4 source coverage proceed, still as **synthetic fixture engineering tests**. No real-market validation or trading claims.

Report: (a) exact first non-PASS/NA error or proven terminal policy, (b) whether UPDATE-002 N/A is allowed by frozen contract, (c) original stair first-bar comparison, (d) legitimate prebar eligibility provenance or exact absence, (e) number of bar calls (must be <=2 in this diagnostic: one random fixture, one original stair fixture), and (f) genuine next blocker. No full-window F9 rerun.

Hard safety: unchanged frozen strategy.py SHA256 792d2818d8495889319de5b3e6019ac0e856d27a59c6c959ac355ff239765a5f, spec.yaml SHA256 4fb02c4559fc2fe8ee4e95390b76fce132f5af34c4f7e23a0091f1c8f8108fd1; 528 symbols; TAC_LIVE_ENABLED=0, subscriptions OFF; TEST_ONLY isolated state, no account/market/order APIs, deployment, Paper/Live or trading. PORT007 and D3/B3 durable joint-persistence remain independent. Real market data sourcing/forward verification is a separate later design requiring explicit source, availability and governance review; never substitute this synthetic fixture.
