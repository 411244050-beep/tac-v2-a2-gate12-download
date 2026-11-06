# TAC: move observation from patch-string scope to actual engine / original V6 raw-shadow

Pinned original: 411244050-beep/tac-v2-a2-external-runtime commit 1f2499ecb84bfefea063992d48f23949c65c5578.
Date: 2026-11-06. Only isolated TEST_ONLY. No frozen strategy changes.

## What is proven and what is blocked

LONG genesis 74699999: original WATCH TRUE, lineage KNOWN_START_FIRST_EVENT with 7 refs; original D4 engineering proof is 4 COMPLETE + 2 UNKNOWN. Static BLOCKED_CRITICAL_UNKNOWN; lineage prepare 1, abort 1, commit 0. D4 final packet/F9 UPDATE-011 NOT_REACHED. Do not re-run prior 78-cutoff/156-call science tests.

Original candidate module and original WP8 relative-import loader now resolve; candidate producer failed only because adapter-local d1 is CanonicalizationResult, whereas the original candidate producer expects D1ReferenceResult. Formal tx identity was absent because local instrumentation currently executes in a post-UPDATE008 **patch-source string/composer namespace**. Local adapter/_adapter were strings, and the 'c' object exposed only two narrow step functions: NOT a DeteministicCutoffEngine instance, NOT a tx_cache.

Do NOT inspect those same locals or the same call stack again; the scope can never expose raw_sr / raw_adapter solely by searching names. Missing evidence is the **actual upstream invocation**, not proof no D1/tx exists.

## Original verified source and exact executable observation surface

- [Original V6 60045-byte Python](https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/d2_genesis_authority_handoff_20261106/live_runtime_raw_authority_extraction_packet_orchestration_binding_v6.py), Git Blob SHA-1 2f12e518858be4758d81d0027c6045466ddf38f0.
- Its `LiveRuntimeRawAuthorityOrchestrationV6._raw_shadow(bar)` (about lines 261-291) creates ORIGINAL `repaired.AdapterIntegrationRuntimeRC1ConformanceV1`, `minimal.DeterministicCutoffEngine`, runs `run_cutoff_batch((inp,))`, reads `sr = result.symbol_results[0]`, obtains `cache = adapter.tx_cache[sr.transaction_id]`, checks `cache.d1` AND `cache.d2` non-null, and returns `(adapter, ledger, result, sr, cache)`.
- Its `_post_d3_shadow(bar, initial)` (about lines 293-312) re-runs a second original staged shadow with initial D3 packet; returns its SymbolResult and tx_cache.
- Its `_genesis` (about lines 415-435): candidate request `d1=raw_cache.d1`, tx `raw_sr.transaction_id + ":CANDIDATE"`, then exact post-D3 initial packet, check `post_sr.transaction_id == raw_sr.transaction_id`, assign `formal_tx=post_sr.transaction_id`. Original full `b5prod.Update008Output` later produced with tx `formal_tx + ":U8"`.
- Its `run_cutoff(bar)` (about lines 1249-1285) calls `_raw_shadow`, detects genuine D2 trend genesis and dispatches. Its `export_state()/restore_state()` (about 1287-1357) contains raw adapter state, candidate and lineage state, chronological minor/intermediate pivots and prior cutoff; never restore stale or fabricated source history.
- [Original WP8 strategy_rc1 transport and 91-file hashes](https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/wp8_strategy_rc1_full_original_20261106/README_RECOVERY_HANDOFF.md).
- [Original candidate producer](https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/d2_genesis_watch_handoff_20261106/d1_d2_to_d3_candidate_production_v1.py) Git Blob aa492e3ea176ab1bb81913e299fbee01b08bff5d.

## Next immediate task (choose ONE actual entrypoint; stop re-probing patch-local strings)

**Preferred: independent exact-original V6 raw-shadow on copied authorized state.**
1. In NEW TEST_ONLY interpreter with already SHA-verified WP8 relative-import rewriter, load original V6 and its frozen imports once. Do not patch frozen class/function AST or create alias copies of enum classes.
2. Take an authentic, already-saved **pre-genesis state** from the same offline bar series, including D1/D2 accumulated history and canonical segment continuity. Create a state copy via exact original V6 state codec, or reconstruct from original offline closed bars chronologically if no such saved state exists. A bare current trend object or an uninitialized V6 state is NOT an authentic pre-genesis state. Do not inject current cutoff D1 into a false earlier state.
3. Execute ONLY `_raw_shadow(genesis_bar)` on that cloned valid pre-genesis state. Capture the returned `sr.transaction_id` and `cache.d1` type (`D1ReferenceResult`), `cache.d1.canonical_records` count and last allowed cutoff, original math_15m/1h/4h counts, `cache.d2.update_006_trend.episode_start_cutoff`, same symbol and source segment; record whether `cache.d1` is original class identity required by candidate producer. Stop if D1 is not the expected frozen result.
4. Only after raw-shadow succeeds, pass `raw_cache.d1` to original candidate producer once. Obtain genuine `cand_result.output_digest`, produce exact initial packet, invoke `_post_d3_shadow(genesis_bar,initial)` on equivalent untouched original cloned pre-genesis state and confirm `post_sr.transaction_id == raw_sr.transaction_id`. Produce genuine `formal_tx`; no manual string generation.
5. If the necessary V6 inputs or valid pre-genesis state are missing, return `V6_ENTRYPOINT_OR_PRESTATE_BLOCKED`, exact missing original modules and earliest available historical state. Do not silently substitute a new synthetic fixture.

**Alternative if independent V6 entrypoint is not callable:** make a bounded, **test-only wrapper** at the actual isolated `frozen_downstream_causal_order` *engine-construction and run* invocation (the user reports `engine=c.DeterministicCutoffEngine(adapters=registry, ledger=...)`). Capture references to the REAL engine object, adapter registry and result of `engine.run_cutoff_batch` from that actual runtime call, NOT from a text variable named `adapter`. The true symbol result contains transaction identity; find frozen adapter's owned `tx_cache` in the actual registry/owner instance if present. If the active code has no accessible reference, instrument only the isolated caller/engine adapter boundary, not frozen strategy.py, and do not rewrite engine scientific code. If `adapter.tx_cache` is not part of this implementation, stop with `F9_RUNTIME_OWNERSHIP_BOUNDARY_BLOCKED` rather than inventing it. Any 'patch' must remain isolated and instrument only access/metrics, not semantics.

Never run BOTH entrypoints to repeatedly produce the same science fixtures. One bounded LONG cutoff / minimal prehistory to prepare a valid V6 state is authorized within TEST_ONLY scope; avoid full new 78 F9 staged replay. Preserve separate original event ID / typed output identity.

## Following two concrete results

- `D1_CANDIDATE_SOURCE`: exact D1ReferenceResult object origin/type, authentic canonical history, actual original candidate call count and output_digest. Only then D3_CANDIDATE_AND_RUNTIME_B3 coverage may become COMPLETE, and only with verified no prebar snapshot (already observed zero on LONG genesis). No `CandidateBatch` string from guessed digest.
- `FORMAL_TX_SOURCE`: exact original `raw_sr.transaction_id`, `post_sr.transaction_id` equality and actual stage ownership. Only then UPDATE008 source ref `Update008:<formal_tx>` may become COMPLETE, using full same-transaction original Update008Output and existing pure-WATCH reconciliation. Do not change scientific UNKNOWN or ignore role-runtime class-schema checks.

If and ONLY if the six exact original coverage classes are independently COMPLETE and D4 static READY, complete original assembler final packet; drive same-tx F9 staged stages with D4 visible at UPDATE-011, then commit original lineage only on downstream success. Otherwise abort; prior WATCH/START_FIRST_EVENT prepare alone is not ledger commit. Distinguish not-reached from measured call zero.

Required report: actual entrypoint used; original loaded module/one-instance type; prestate/source history validity; D1 object schema; raw/post transaction identity; candidate digest; source-backed two remaining coverage classes; F9 D4 final/UPDATE-011 and lineage commit/abort status; next *new* blocker. Send scalar flushed summary, do not serialize entire state graph.

Safety: 528 symbols frozen, TAC_LIVE_ENABLED=0, subscriptions OFF, strategy.py SHA256 792d2818d8495889319de5b3e6019ac0e856d27a59c6c959ac355ff239765a5f, spec.yaml SHA256 4fb02c4559fc2fe8ee4e95390b76fce132f5af34c4f7e23a0091f1c8f8108fd1. No strategy save/deploy, account/market/order APIs, Paper/Live or trading. PORT007 production allocation and D3/B3 joint durable persistence remain separate blockers. No synthetic evidence promoted to true market authority.
