# TAC V6: canonical frozen.EventRelation identity before one SYNTH genesis retry
2026-11-07 | Original source pinned commit: 1f2499ecb84bfefea063992d48f23949c65c5578 | isolated TEST_ONLY.

## Proven latest status

- Original saved bar-82 V6 checkpoint is present at a private temporary workspace path: 13,683,812 bytes; full SHA256 matches V6.state_digest, abbreviated b342a5d01d3f...38a203fa; restored last_cutoff=73799999, 12 minor + 4 intermediate pivots, SYNTH observer snapshot exists. This copy is temporary only, NOT externally durable and must not be uploaded publicly.
- One and only one outer genesis cutoff was run on SYNTH random.Random(0) bar open_time=73800000, close_time=74699999; no prebars, SHORT, or later bars. Original raw/post batches both COMMITTED, 17 stages each, both transaction_id cutoff_tx:14f19d37474397a1311065faf55ce3de. Earlier candidate output 9 updates and digest prefix 3f207da1...suffix 6a5c, BUT not reobserved this latest run; do not falsely relabel it current-run evidence.
- MechanismProducerOutputs Python isinstance schema guard was resolved through actual canonical original assembler module identity; lineage.prepare(formal_tx,req) invoked once and RETURNED a projection. It did not commit or abort; no successful genesis result or persistence. Formal_tx was a local V6 transaction ID after passing raw/post identity check, not evidence of whole genesis commit.
- First new fail: RawV6Block GENESIS_LINEAGE_NOT_START_FIRST_EVENT, in original V6 _genesis line ~615-616: lin_proj.relation is not frozen.EventRelation.START_FIRST_EVENT.
- Measured real cause: two nontrading_adapter_integration_v1 module objects; lineage returns EventRelation.START_FIRST_EVENT from one copy, while V6 guard uses second. Members compare == true, identity is false. This is a Python loader class-instance drift, not an authoritative UNKNOWN/CONFLICT assessment. Original frozen scientific behavior must not be changed.
- CandidateFamily, MathematicalBoundaryCandidate, TrendDirection each still had two loaded classes; no proven current consumer mismatch, do not blindly patch. All 528 frozen symbols and unrelated governance blockers remain unchanged.
- D4 six-class recomputation, D4 final packet and F9 UPDATE-011 NOT_REACHED. V6 state remained at the bar-82 checkpoint; lineage prepare count=1, commit=0, abort=0.

## Exact original code authority

Original V6 file, Git Blob 2f12e518858be4758d81d0027c6045466ddf38f0:
https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/d2_genesis_authority_handoff_20261106/live_runtime_raw_authority_extraction_packet_orchestration_binding_v6.py
- line 22 imports nontrading_adapter_integration_v1 as frozen.
- line ~614 calls lineage_rt.prepare(formal_tx,lineage_req).
- line ~615 compares lin_proj.relation IS frozen.EventRelation.START_FIRST_EVENT and line ~616 raises on mismatch.
- line ~690 onward builds assembled D4 evidence, formal staged engine and only afterward commits lineage; do not bypass those guards.

Original frozen lineage v2, Git Blob f334155bbb46ec2ff0ee748555cb15c1485d3036:
https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/d4_market_event_lineage_binding_20261106/d4_market_event_lineage_production_binding_v2.py
- line 33 imports nontrading_adapter_integration_v1 as frozen.
- near line 1127 creates relation=frozen.EventRelation.START_FIRST_EVENT on first authoritative active genesis; line 1129 status KNOWN_START_FIRST_EVENT.
- relation may also be reconstructed by _projection_from_record via frozen.EventRelation, which must be the same canonical enum.
- Scientific UNKNOWN/CONFLICT values and relationship semantics must stay untouched.

Original nontrading adapter source transport, Git Blob add54fa0fb0749cf13ffae520fb6cd8181640302:
https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/original_d4_dependencies_20261106/nontrading_adapter_integration_code_bundle_v1.tar.xz.b64

## Next action: loader alias normalization then ONE genesis attempt

1. Before any cutoff, restore the proven correct and unchanged WP8 loader graph: original canonical evaluate_d1_reference binding, original ParameterState, original D3 CandidateAvailability producer-and-consumer, original MechanismProducerOutputs assembler identity. Do not remove working bindings or alter science functions, AST, thresholds, stage/status semantics.
2. Inspect REAL function global namespace, not just module attributes:
   - v6f = LiveRuntimeRawAuthorityOrchestrationV6._genesis.__globals__["frozen"]
   - linf = lineage_prod._compute_projection.__globals__["frozen"] (if actual executed function is another lineage projection creator, inspect its __globals__ too)
   - check whether v6f is linf; check v6f.EventRelation is linf.EventRelation; check v6f.EventRelation.START_FIRST_EVENT is linf.EventRelation.START_FIRST_EVENT.
   - check loaded exact canonical sys.modules["nontrading_adapter_integration_v1"] object and its original source provenance, frozen.EventRelation class __module__/identity, and if necessary other executed creator and consumer global bindings (including _projection_from_record).
3. Only if the two class/module objects are proven duplicate loader copies of the same frozen source, correct loader import aliases and actual function globals to one canonical ORIGINAL frozen module class. Both V6 and lineage must consume the same original EventRelation class before any science execution. Do NOT change "is" to "==", change EventRelation member values, reconstruct or coerce the returned projection/relation, edit WATCH science, modify original dataclass definitions, or change branch result.
4. Verify in STATIC preflight (without calling lineage.prepare on fabricated requests) that the original provider and V6 consumer point to identical EventRelation.START_FIRST_EVENT members. Confirm other direct same-cutoff enum guards on the next original V6 path use canonical source classes, without indiscriminate rewiring unrelated classes. If identity cannot be established from original code, report EVENTRELATION_LOADER_IDENTITY_BLOCKED with 0 bar calls.
5. Verify the actual private checkpoint bytes still exist, size exactly 13,683,812 and full SHA256 equals the previous recorded FULL state_digest. Rehydrate via original V6.restore_state(saved_bytes.decode("utf-8")), compare full V6.state_digest, last_cutoff=73799999, minor=12, intermediate=4, SYNTH next snapshot. If absent or mismatch, report CHECKPOINT_UNAVAILABLE_OR_RESTORE_BLOCKED. NO 82+1 fallback authorized.
6. After all preflights succeed, authorize at most ONE outer original V6.run_cutoff for the exact SYNTH genesis bar open_time=73800000 / close_time=74699999. Prehistory=0, SHORT=0, later cutoffs=0, 156-cutoff replay forbidden. Read-only scalar observer may count original raw/post/formal nested engine batches, terminal and error_reason without changing their behavior. Never run the outer cutoff twice.
7. After genuine lineage.prepare returns, compare lin_proj.status, lin_proj.relation and original EventRelation START_FIRST_EVENT by Python is; require original lineage source evidence, valid causal genesis relation and no future evidence. If relation truly different with unified class, preserve original fail-closed and report science difference, not a loader shortcut.
8. If original V6 passes the relation guard, allow it to execute original six D4 source coverage facts, static projector, authoritative packet assembler, and formal F9 staged engine through UPDATE-011 in the SAME existing cutoff ONLY. Keep original stage visibility constraints (D4 absent until UPDATE-011) and no invented missing coverage. Formal engine abort must remain original GENESIS_ABORTED, with its original lineage/platform abort operations. If any new exception, report first actual error, no same-task repair/retry.
9. Only if V6 itself reaches original lineage_rt.commit and returns GENESIS_FULL_TYPED_STAGED, report it as a successful SYNTHETIC ENGINEERING closure. Check final packet/ledger/scalar state and actual source coverage; do not assume all six classes COMPLETE unless original produced them. Even success does NOT resolve independent PORT007 or D3/B3 joint persistence and is NOT real-market or trading authority.
10. Report exact canonical frozen class/module identity across V6/lineage, original EventRelation member comparison after normalization, file checkpoint full SHA proof, outer run_cutoff calls<=1 and inner batch count, current-run candidate digest if actually captured (otherwise NOT_OBSERVED), raw/post/formal tx status, lineage prepare/commit/abort, six-class D4 source coverage, static projector/packet and F9 actual stages vs NOT_REACHED, V6 state before/after, and next real blocker. Keep concise scalar logs, no 13MB dump.

Safety boundary: all 160 records are SYNTH random.Random(0) fixture, NOT exchange market history. Immutable strategy.py SHA256 792d2818d8495889319de5b3e6019ac0e856d27a59c6c959ac355ff239765a5f and spec.yaml SHA256 4fb02c4559fc2fe8ee4e95390b76fce132f5af34c4f7e23a0091f1c8f8108fd1, frozen 528 symbols, TAC_LIVE_ENABLED=0, subscriptions OFF. TEST_ONLY. No market/account/order I/O, Paper/Live, trades, outcomes, strategy deployment or account access. PORT007_UNRESOLVED_PRODUCTION_ALLOCATION_BLOCKED and BLOCKED_D3_B3_JOINT_PERSISTENCE remain independent blockers.
