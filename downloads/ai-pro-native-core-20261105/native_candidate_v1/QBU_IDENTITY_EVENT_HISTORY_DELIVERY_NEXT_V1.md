# TAC / Binance AI Pro: QBU identity historical event delivery — next isolated TEST_ONLY task
Date: 2026-11-06

**SCOPE:** only the existing Binance AI Pro strategy's *in-memory isolated copy*, no baseline write, no strategy save, no subscription, no orders, no Paper/Live. User has previously authorized continued TEST_ONLY engineering. This document is NOT native test acceptance, scientific changes, or a new original-source authorization.

## Native evidence provided by the latest Binance report (do not rerun unchanged B3 tests)

- Both LONG and SHORT, each 160 synthetic OHLC source bars, B3 and original D3 bridge each 335/335, UPDATE007/008 each 335/335, 3 independent rearms each.
- Original identity / Minor progress / B5 request calls each direction 78/15/15; original B5 per request 15/15 exact parity but all remain UNKNOWN.
- 63 identity UNKNOWN per direction: `REFERENCED_INTERACTION_EVENT_MISSING`. Across those identity requests, 123 missing occurrences: `D3-WATCH` 63 and `D3-WATCH-REARM` 60. Every referenced original event can be located in the actual isolated loop's **observation ledger**, yet was omitted from the identity request `events`.
- 15 identity projections KNOWN but empty identity mapping, 15 Minor evidence states TRUE with zero actual progress records; positive QBU/Primary/valid Anchor uses still zero. Missing WATCH event histories and empty material Minor progress are **distinct** gates.
- LONG/SHORT A/B: post-rearm return qualified and consumed in the actual bridge; C remains pending/unfinished, not an asserted failure. These were synthetic-clock cutoffs, not real-market timestamps.
- Frozen original B4 FALSE_BREAK correctly resolves a terminal event `RESOLVED_CORRECT_SIDE`; only the exact B4-produced, original-state-applied, source-verified correct-side terminal subset is permitted by isolated adapter, not TRUE_BREAK, terminated Anchor or other terminal states. Source-only public adapter might lag Binance's in-memory provenance checks; do NOT overwrite native code with it.
- Native SHA `strategy.py` 473006 bytes: `792d2818d8495889319de5b3e6019ac0e856d27a59c6c959ac355ff239765a5f`; `spec.yaml` 2865 bytes `4fb02c4559fc2fe8ee4e95390b76fce132f5af34c4f7e23a0091f1c8f8108fd1`; both unchanged.
- Native durable D3+B3+RoleMemory one-version atomic checkpoint and restart remain **BLOCKED_D3_B3_JOINT_PERSISTENCE**; native `validate_code`/`validate_spec` do not accept an isolated source path, so neither was called. No deployment readiness.

## Original frozen source has already been verified

`downloads/ai-pro-native-core-20261105/frozen_evidence_producers_v1/qbu_same_event_negotiation_identity_production_binding_v1.py` is the exact frozen identity producer. The key source behaviors:

1. `NegotiationIdentityRequest.events` must contain a **canonical one-record-per-event InteractionEvent history** for every `AnchorEpisode.interaction_event_ids` ref and every QBU-bearing ref. `history_complete` attests the true original D3 event / Episode / replay-derived rearm predecessor coverage, not merely successful local lookup.
2. `_event_map` rejects divergent repeated `event_id` records as `DIVERGENT_EVENT_RECORDS`.
3. Missing member records produce `UNKNOWN / REFERENCED_INTERACTION_EVENT_MISSING` even if those watch/rearm events would not subsequently be eligible.
4. `_eligibility` excludes non-correct-side-resolved WATCH/REARM records. An eligible negotiated interaction needs real started/resolved timestamps, original reference boundary/scale, Anchor Episode link, continuity and matching target trend.
5. `rearm_predecessor_by_event_id` is keyed by a **later actual TEST/contact InteractionEvent ID** after the rearmed cycle. It links to the prior resolved InteractionEvent ID — not the WATCH-REARM ID. It must be replay-derived; a component crossing a distinct rearm boundary is a CONFLICT.
6. `KNOWN` with an empty mapping means all supplied records were excluded or there are no eligible records. It is NOT a positive QBU. `EvidenceState.TRUE` with zero `progress_evidence` means no material Minor records. Both require separate source diagnosis; never fill based on positivity.
7. Original B5 requests and outputs must still be compared for exact parity; no fabricated eligible events, QBU or Primary.

Public, independent original-source parity regression:
- [test_qbu_identity_historical_event_delivery_v1.py](https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/native_candidate_v1/test_qbu_identity_historical_event_delivery_v1.py)
- [GitHub Actions run 42168847816](https://github.com/411244050-beep/tac-v2-a2-gate12-download/actions/runs/42168847816) — 5/5 PASS; **not** native 473KB verification.

## Next isolated native execution — minimal, no full strategy rebuild

A. Read the existing in-memory main-loop event observation ledger, original D3 `update_007` / Anchor `update_008` event transition records and existing QBU identity request assembler. Do not re-run 68 old UNKNOWN diagnostics.

B. Identify the exact line/function that truncates `identity_request.events` to current-only / active-only events. Construct a **non-mutating cutoff-scoped canonical historical view** from *actual originally emitted* D3 events. Include each member event ID exactly once, with its authoritative as-of-cutoff record. For a record with same ID that evolves across successive cutoffs, use the latest authorized original post-D3 state observed at or before the requested cutoff, with deterministic version/cutoff provenance. Do not blindly select a last duplicate in the same cutoff, and do not project a future post-cutoff state backwards. Ensure final D3 `update_008` event/episode binding is respected.

C. For each target Anchor Episode, require every `interaction_event_ids` member and QBU negotiation ID to resolve to an exact original event record at that cutoff; verify candidate, episode, trend, direction, segment and source cutoff. Preserve original historical WATCH / WATCH-REARM event IDs but do NOT give them fabricated `started_at`, `resolved_at`, event-reference fields or Anchor association. Each remains noneligible if the frozen original science says so.

D. Build `rearm_predecessor_by_event_id` from the *actual original* `RESOLVED E1 -> WATCH-REARM W2 -> later D3-INTERACTION E2` transition and contact ledger. Map `E2 -> E1` only when that new actual interaction is observed; never map `W2 -> E1` as if W2 were a completed interaction. Validate graph acyclic, exact refs, no rearm boundary same-component conflict.

E. Assert `history_complete=True` **only** where original event/episode/canonical/rearm ledgers and source coverage are actually complete through cutoff. Otherwise preserve UNKNOWN. Missing original source, duplicate divergent event, future state, cross-episode changes => explicit fail-closed.

F. Recompute original identity projection from the same requests with **ONLY** repaired historical `events` and truly derived rearm predecessor map. Show a before/after table, by direction:
   - identity calls 78, before missing-event UNKNOWN 63;
   - after missing-event UNKNOWN count, new UNKNOWN/conflict reasons and number of actually eligible resolved negotiations;
   - KNOWN with zero mapping vs KNOWN with nonempty mapping, no borrowed event identities;
   - count of real original history records included, versus duplicate/conflicting IDs.
   Compare original frozen module and namespaced implementation one-to-one. Do not claim all 63 become positive.

G. Only then re-run the **15 real B5-request cutoffs per direction** that the current main loop actually reaches. Report identity map counts, Minor material evidence record counts, actual B5 output states, produced QBU, original Episode writeback, Primary and next-cutoff RoleMemory. `KNOWN` or `TRUE` without records does not constitute progress.

H. If the 15 still have zero real material 15m Minor pivots, report which exact frozen Minor-progress prerequisites fail (start/terminal Trend Episode cutoffs; pivot confirmation after resolved cutoff; trend-side movement vs frozen theta; canonical continuity/segment; required prior structural pivot). Do not add artificial pivots or synthetic progress to existing main loop merely to pass.

I. Keep full Binance source unchanged and don't call native validators that only read the baseline. Audit whether this is compatible with the old current source's QBU and RoleMemory ledger. If any test or source coverage is impossible, report exact blocked condition rather than write new scientific rules.

J. Joint persistence/rollback remains an **independent** blocker. No D4 onward merge, subscriptions, Paper/Live, account or trading. Failure to find an atomic host state restore interface must not stop isolated event-history diagnostics, but it DOES stop claims of official native merge readiness.

## Independent test gates

- Referenced WATCH/REARM real historical records inserted exactly once -> original missing refs disappear only where true coverage exists; WATCH/REARM not eligible and do not create negotiation IDs.
- Divergent same event ID same cutoff -> CONFLICT; incomplete source coverage -> UNKNOWN.
- Episode membership or candidate/segment mismatch -> not silently repaired.
- Actual TEST/contact predecessor from rearm source ledger maps to prior resolved E1, not W2; cycle boundaries remain distinct.
- Future event records are never included.
- Both LONG/SHORT main-loop B5 original parity stays exact; no new QBU unless original real material evidence exists.

**Return the actual native counts, functions and cutoff trace, before/after output parity and unchanged source SHAs. Do not rerun unrelated B3 validation.**
