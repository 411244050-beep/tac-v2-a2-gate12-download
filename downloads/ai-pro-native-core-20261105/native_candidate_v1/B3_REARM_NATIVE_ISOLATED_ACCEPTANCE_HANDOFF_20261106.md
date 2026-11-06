# TAC / Binance AI Pro — isolated original B3 rearm acceptance handoff
Date: 2026-11-06
Scope: **TEST_ONLY IN MEMORY**. User explicitly authorized isolated new-cycle engineering mapping on 2026-11-06. No native baseline write, Paper/Live or trading authorization.

## Real results already established OUTSIDE Binance

- GitHub Actions source-only [run 42164754734](https://github.com/411244050-beep/tac-v2-a2-gate12-download/actions/runs/42164754734): **35/35 PASS**, including inherited prior LONG/SHORT regression tests. Independent bridge tests show *second* original D3 cycle: `RESOLVED -> new ARMED -> pending -> later qualified return -> later active interaction -> RESOLVED`. Old source was the public historical baseline, NOT the current 473KB native source.
- Public [approved isolated test-only adapter](https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/native_candidate_v1/B3_REARM_INDEPENDENT_CYCLE_STAGE_TEST_ONLY_V1.py).
- Public [direct stage test](https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/native_candidate_v1/test_b3_rearm_independent_cycle_stage_v1.py).
- Detailed [engineering mapping proposal](https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/native_candidate_v1/B3_REARM_INDEPENDENT_CYCLE_ADAPTER_BINDING_PROPOSAL_V1.md). It is **NOT a scientific authority change** and is not cleared for formal merge.
- Source-only stage receipt `durable_joint_checkpoint=False`, original caller D3/B3 never mutated by the proposed bridge.
- Important transaction clarification: the stable transaction identity is derived from candidate/episode/segment/cutoff/new-event identity and a fixed contract ID. It intentionally **excludes mutable observation digest**; the digest is recorded separately and the frozen producer rejects *same transaction ID with different input*. Including the digest in ID would evade that guard.

## Current exact native Binance baseline (read-only, preserved)

```
strategy/strategy.py: 473006 bytes SHA256 792d2818d8495889319de5b3e6019ac0e856d27a59c6c959ac355ff239765a5f
strategy/spec.yaml:     2865 bytes SHA256 4fb02c4559fc2fe8ee4e95390b76fce132f5af34c4f7e23a0091f1c8f8108fd1
```

Native latest report: 512 synthetic OHLC bars, 201 actual frozen B3 observations, D3 correctly `RESOLVED -> ARMED`, then `ARMED_WITHOUT_RUNTIME_B3_PENDING_STATE`. Existing QBU/B5 loop prior: identity state KNOWN but identity map empty 68/68; Minor state TRUE but actual material progress count zero 68/68; B5 UNKNOWN 68/68. Do NOT fabricate positive evidence.

## Next exact Binance execution (no further TEST_ONLY permission request needed)

1. Read public adapter and tests. Read **current native source** and assert full exact SHA before touching anything. Do NOT replace strategy.py with the public *older* strategy.py. Keep current source and spec file byte-for-byte unchanged.
2. Construct a completely **isolated in-memory module/copy** of the current native strategy.py, and add the new TEST_ONLY adapter **once** to that copy only. Preserve all current verified D3/B3/B4/V2 batch, namespaced QBU/B5 and ledger definitions. Resolve any real symbol collisions and report them, never silently shadow definitions.
3. In isolated copy, change only the D3/B3 adapter branch for **original prior D3 control RESOLVED** after an authoritative strictly later separation. It must first compare the *pure original* `rearm_after_resolution` projection and verify old B3 pending absent. Stage frozen B3 `UNARMED + separated` observation as **NEW_INDEPENDENT_CYCLE_PRE_ARM only**, not as a false representation of the prior D3 event. Use the actual prebar snapshot and arming 15m Close/scale, source digest, trend and segment. **No same-cutoff return.** Call original D3 `update_007_interaction_break` on the original RESOLVED event only once; require exact event parity. Other original branches unchanged.
4. Do NOT reset and rearm the same candidate in two B3 transactions at the same cutoff. One candidate/cutoff, one B3 process_batch transaction, deterministic stable ID independent of mutable source digest. Old pending present => BLOCKED. Mismatched source => BLOCKED. The stage adapter is not a write-back plan by itself.
5. Run original main cutoff loop (not only synthetic standalone producer) with LONG and SHORT sequences, correct-side legal rearm, same-cutoff illegal rearm, terminal and continuity change, candidate/snapshot identity conflict, and follow-on B3 return and TEST. At every cutoff verify D3 event, B3 pending, arming bar/snapshot/scale, source lineage and update007/008 original equivalence. Report exact invocation counts.
6. Stage joint checkpoint D3 event/Episode + B3 serialized pending and transaction completion + same original D2 episode RoleMemory + source cutoff and digest. Fault-inject failed atomic commit and cold-restart rehydration **only if the host actually offers a durable atomic store**. Do not claim that an in-memory object clone or B3 persist callback is a native host durable joint transaction. If unavailable, record `BLOCKED_D3_B3_JOINT_PERSISTENCE`.
7. If B3 branch passes, proceed with QBU/B5 actual original request/output via same main loop. Do not alter 68x UNKNOWN facts. A positive main-loop test is only positive if original QBU identity mapping, real Minor evidence records and materiality, original B5 TRUE, original Episode writeback and Primary/RoleMemory subsequent cutoff are actually observed. Independent positive fixtures alone are insufficient. D2 true terminal provenance cannot be imputed from integer cutoff.
8. Run `validate_code` and `validate_spec` on isolated copy **only if supported** and report exactly how they were called. If validators operate only on workspace files, do not overwrite baseline to invoke them. Report both original (unchanged) file SHA. Never claim native validator PASS without actual call.
9. If a test fails, return the exact original failing reason, observations and line numbers. No source guessing, blanket bypass, time estimates, extra tests outside changed path or requests for further TEST_ONLY authorization.

## Safety and downstream

Keep frozen 528-symbol order and count, `TAC_LIVE_ENABLED=0`, native subscriptions OFF. No account, market subscription, orders, cancels, position changes, Paper or Live. No current strategy save/overwrite/merge/deploy. Preserve every existing B3/B4/QBU/B5 implementation and frozen scientific parameters. GitHub source-only tests do not establish native production origin or durable epoch/restart integrity.

D4 four mechanisms, F9, D5/PORT007, UPDATE014 admission and D6 remain NOT ACCEPTED until the actual native main loop passes and durable lineage/recovery is resolved. No pretending that a valid single test positive is enough.

## Return format

- Original SHA, unchanged? exact bytes check
- In-memory updated adapter branch and actual called original function names
- LONG/SHORT rearm before-and-after state and B3 pending origin on same cutoff
- Original transaction IDs/input-digest conflict and restart handling
- Synthetic bars, B3 batch calls, D3 cutoff calls, positive QBU and Primary **inside actual native loop**, and failures
- Real joint durability/atomic restore status
- Native validate_code/validate_spec invoked? results or BLOCKED and reason
- Remaining genuine source evidence and minimal path to next stage
