# TAC D2 genesis authority recovery + post-F9 reporting repair (2026-11-06)

## Existing evidence (from Binance AI Pro report, not a new test)

- Original 91-file `strategy_rc1` reference archive loaded; 91/91 file SHA256 passed. Original `d2_market_state/platform.py`, `wp1_reference.py`, `d2_market_state/establishment.py` now available. No missing imported module names.
- 78 cutoffs **per direction** LONG and SHORT, total 156 calls of original `D4MarketEventLineageProductionProjectorV2.prepare`: all `HISTORY_COVERAGE_NOT_ESTABLISHED` (no real TrendGenesis record); 156 D4 static/source calls: `BLOCKED_CRITICAL_UNKNOWN`; lineage `commit=0`; F9 stages completed 78 per direction, no admission or order.
- 313 flushed stage log lines reach final SHORT cutoff `143999999`. No science function hang detected. Post-science summary output stalls in adapter; two bounded runs never wrote summary row.
- `COMMITTED` at F9 engine is in-memory, not durable host persistence. Science module import alone is not science output.

## Pinned original source locating D2 genesis — now publicly available

Original private repository `411244050-beep/tac-v2-a2-external-runtime`, pinned `1f2499ecb84bfefea063992d48f23949c65c5578`.

- [Original V6 raw authority extraction implementation](https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/d2_genesis_authority_handoff_20261106/live_runtime_raw_authority_extraction_packet_orchestration_binding_v6.py)
- Original Git blob SHA-1: **`2f12e518858be4758d81d0027c6045466ddf38f0`**.
- Implementation location: method **`_genesis`**, lines approximately 362-404, in the original source. This is a *historical reference implementation*, not proof that its full runner will work in the current AI Pro environment.
- It reads **actual** `raw_cache.d2.update_006_trend` when `trend.episode_start_cutoff == bar.close_time`; accumulates authoritative `raw_cache.d2.update_005_intermediate`; calls frozen `strategy_rc1.d2_market_state.establishment.latest_establishment_evidence(intermediate_history,theta_progress=params.theta_progress)`; checks `newest_pivot_id == trend.frontier_pivot.pivot_id` and direction equality; then creates the exact original `b5prod.TrendEstablishmentRecord(trend, creation_cutoff, newest_intermediate_pivot_id, source_event_ids=tuple(establishment.sequence_pivot_ids), provenance=...)`.
- **Original 91-file reference transport and SHA256 manifest**: [WP8 reference archive handoff](https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/wp8_strategy_rc1_full_original_20261106/README_RECOVERY_HANDOFF.md). The archived `strategy_rc1/d2_market_state/establishment.py` has original SHA-256 **`0ae801e864c99aafc751a1ae8af4d42f4b82f400809ce8619c92767b818f5c06`**.
- **Original D4 market-event binding handoff**: [D4 native handoff](https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/d4_market_event_lineage_binding_20261106/README_NATIVE_HANDOFF.md).

## One scoped TEST_ONLY follow-on task

1. **Post-science output first, no new full replay**: flush existing 313-line log and any state/report already in memory or temporary files; isolate summary writing from science in a separate minimal function/process with a small summary of **counts**. Instrument `SUMMARY_STARTED`, `SUMMARY_SERIALIZED`, `SUMMARY_WRITTEN`, `SUMMARY_FLUSHED`. If it blocks again, capture last marker, stack/IO destination, size of would-be serialized object and timeout; avoid serializing large D3 candidate/snapshot or entire F9 object graph recursively. Do not invent a completed summary, don't repeat 156 scientific calls to diagnose the reporter. A one-cutoff adapter-only probe is permissible if existing results are missing.
2. **Discover actual D2 trend genesis boundaries**: inspect the frozen `TrendEpisodeState.episode_start_cutoff`, available prior closed-bar history, and typed D2 `UPDATE-005` pivot event lineage. First determine whether source history genuinely covers the episode birth. If the current 78-cutoff window starts after the episode birth, this window **cannot** by itself establish `HISTORY_COVERAGE`.
3. **If and only if valid earlier existing data are available**: extend the isolated historical replay backward to before the first needed episode birth and forward chronologically, using the same frozen D1/D2/D3 reference logic. At the actual `UPDATE-006` episode creation cutoff, apply original V6 genesis path `latest_establishment_evidence`; verify the precise pivot IDs, direction, provenance, exact episode creation cutoff and canonical continuity. Do not use current Trend as a fabricated source event. Retain coverage/ledger across all relevant subsequent cutoffs in the same isolated transaction chain.
4. **If historical source data are unavailable**: explicitly return `HISTORY_COVERAGE_NOT_ESTABLISHED` and report minimum missing cutoff span / source type required. Do not manufacture a `START_FIRST_EVENT`, `SAME_EVENT`, `NEW_INDEPENDENT_EVENT`, source ref, or first WATCH.
5. Continue independent **platform source producer** `project_platform_failed_reexpansion` if its **real** `history_complete`, coverage refs, ATR-at-confirmation and frozen D2 pivot/event sources are available; else retain UNKNOWN, count it as attempted or unavailable, not confirmed. Keep separate from lineage-genesis gating.
6. Only after authoritative genesis coverage is actually created, call original `D4MarketEventLineageProductionProjectorV2.prepare` with typed original request; if produced relation and proof refs are authoritative, bind to D4 Assembler V2 and then run original F9 / four-mechanism stages as appropriate. Do not issue lineage `commit` without corresponding downstream isolated commit; `abort` when downstream fails.
7. Report per-direction original D2 episode birth count and earliest available cutoff, `TrendEstablishmentRecord` TRUE/UNKNOWN/CONFLICT counts, known market event relation status, new actual `D4` packet and composer counts, independent platform producer calls/status, and adapter-summary outcome. The snapshot counts 262 candidates and 10143 snapshots from previous replay are **not** substitute lineage.
8. Stop after true blocker. No repeat B3/B5 QBU positive fixtures or 78-window complete replay merely to get a different summary.

## Safety

Pinned `strategy.py` SHA256 `792d2818d8495889319de5b3e6019ac0e856d27a59c6c959ac355ff239765a5f`; `spec.yaml` SHA256 `4fb02c4559fc2fe8ee4e95390b76fce132f5af34c4f7e23a0091f1c8f8108fd1`; 528 symbols unchanged, `TAC_LIVE_ENABLED=0`, subscriptions off, isolated TEST_ONLY only, no strategy save/deploy, no account/order/market interfaces, no Paper/Live trades. `PORT007_UNRESOLVED_PRODUCTION_ALLOCATION_BLOCKED` and `BLOCKED_D3_B3_JOINT_PERSISTENCE` remain independent. Temporary memory logs do **not** prove durable state.

No synthetic scientific observations may be promoted to source authority.
