# TAC V6: observe six EFFECTIVE D4 coverage classes + pure-WATCH reconciliation on ONE SYNTH genesis
2026-11-07 | frozen original commit 1f2499ecb84bfefea063992d48f23949c65c5578 | TEST_ONLY only.

## Newest measured event

The exact original 13,683,812-byte private bar-82 checkpoint remains restorable (full saved SHA256 identical to V6.state_digest, abbreviated b342a5d01d3f...38a203fa; last_cutoff=73799999, 12 minor/4 intermediate pivots, next SYNTH snapshot). This is NOT durable storage; do not upload checkpoint contents to public GitHub.

A single outer V6.run_cutoff on SYNTH LONG genesis (open_time=73800000, close_time=74699999) completed raw and post engines with 17 stages each, terminal COMMITTED, same local transaction cutoff_tx:14f19d37474397a1311065faf55ce3de. Lineage.prepare called once and returned true KNOWN_START_FIRST_EVENT / EventRelation.START_FIRST_EVENT (canonical same enum member), 7 evidence refs, proof kind GENESIS_COVERAGE_FIRST_AUTHORITATIVE_ACTIVE_OBSERVATION, new_event_evidence absent. Lineage commit=0, abort=0. V6 state remained the bar-82 checkpoint; formal staged engine and final D4 packet are NOT_REACHED. Candidate digest and prebar count NOT_OBSERVED in the latest execution; do not re-label earlier synthetic digests as latest.

The NEW original exception is RawV6Block "D4_STATIC_NOT_READY:CRITICAL_COVERAGE_MISSING_OR_UNKNOWN" in V6 _genesis around lines 678-688. This confirms the **effective** coverage statuses include at least one UNKNOWN or MISSING, but exact affected class and reason are not yet observed. Do not assume which one.

## Freeze facts and decisive source distinction

- V6 source (Git Blob 2f12e518858be4758d81d0027c6045466ddf38f0):
https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/d2_genesis_authority_handoff_20261106/live_runtime_raw_authority_extraction_packet_orchestration_binding_v6.py
  - lines ~618-665 construct **six caller-provided SourceCoverageFact entries each labeled COMPLETE** with source refs.
  - lines ~666-684 call purewatch.project_d4_static_source_association(static_req, reconciliation_context=...). Caller labels alone do NOT prove authoritative effective coverage.
  - lines ~685-688 refuse to continue unless static_proj.status READY and d4_static_authority present.

- Frozen D4 static V1 (Git Blob 9eac94f81d874f41f25f856aee16c60ee8deb312):
https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/d4_market_event_lineage_binding_20261106/d4_static_detector_critical_production_binding_v1.py
  - COVERAGE_CLASSES are RAW_AND_D2_STATE, D3_CANDIDATE_AND_RUNTIME_B3, D2_B4_D4_CAUSAL_PROJECTIONS, UPDATE008_D3_B5_STATE, D4_MECHANISM_SOURCE_COVERAGE, D4_MARKET_EVENT_LINEAGE.
  - _update008_actual_status checks original state/conflict_lineage_refs/unknown_lineage_refs, _mechanism_actual_status checks mechanism output states, _lineage_actual_status checks relation and source refs.
  - _critical_from_coverage returns BLOCKED_CRITICAL_UNKNOWN if any effective UNKNOWN or MISSING; no inference of READY from WATCH alone.

- Frozen pure-WATCH reconciliation V2 (Git Blob 074a2b08a7aec6b2c51431a5ccadcc0aa75e0ebb):
https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/d2_genesis_watch_handoff_20261106/d4_static_pure_watch_update008_completeness_production_binding_v2.py
  - classify_update008_coverage returns Update008CoverageReconciliation {effective_status, applies, reason}; it DOES NOT change scientific frozen Update008Output.state.
  - Guard sequence is specific: conflict/unknown lineage refs; actual original Update008Output.state; complete WATCH mechanism and lineage; pure WATCH; exact genesis lineage relation/ref/provenance; exact original runtime/F9/backflow provenance; RoleRuntimeOutput type and UNKNOWN + NO_AUTHORITATIVE_PRIMARY; role assignment equality; no Primary/QBU; RoleTransition.NONE identity; no unresolved role evidence; role runtime provenance.
  - _effective_coverage begins from caller six COMPLETE statuses, recomputes UPDATE008_D3_B5_STATE via reconciliation.effective_status, D4_MECHANISM_SOURCE_COVERAGE via V1 mechanism actual status, D4_MARKET_EVENT_LINEAGE via V1 lineage actual status, and raw future flag. This is the actual authoritative six-class effective result.
  - project_d4_static_source_association returns a D4StaticAssociationProjection with coverage_statuses, blocked_reason, and provenance including update008_reconciliation_applied, update008_reconciliation_reason; capture it directly.

## ONE diagnosis, NO automatic repair

1. Before any bar, revalidate the complete private checkpoint bytes and full SHA, restore state through original V6.restore_state, verify 12/4 pivots, SYNTH snapshot, last_cutoff and exactly identical full state_digest. Missing bytes = CHECKPOINT_UNAVAILABLE_OR_RESTORE_BLOCKED; do not rebuild the 82 SYNTH prebars.
2. Preserve the previously proven D1, ParameterState, CandidateAvailability, MechanismProducerOutputs/assembler, EventRelation/frozen loader identity fixes. Check exact runtime class identities for b5prod.Update008Output, RoleRuntimeOutput, EvidenceState, d3 RoleTransition, lineage D4LineageProjection, purewatch reconciliation type, and static V1 request/projection; if duplicate identity is found record the concrete consumer/producer mismatch, but DO NOT patch it in this task.
3. Install read-only TEST_ONLY observation at the ACTUAL original purewatch.classify_update008_coverage RETURN boundary and original purewatch.project_d4_static_source_association RETURN boundary used by V6. When possible, use single-call wrappers that invoke each original function exactly once and return the identical output unmodified; alternatively narrow trace at function return. Do not invoke these functions a second time for logging. At V6 caller retain original exception behavior.
4. From actual static_req / return objects capture compact scalar fields:
   - the six caller SourceCoverageFact statuses and source-ref counts (avoid dumping 13 MB state);
   - the six static_proj.coverage_statuses EFFECTIVE statuses, exactly in original COVERAGE_CLASSES order;
   - static_proj.status, blocked_reason, critical_information_known.kind, d4_static_authority present/absent;
   - reconciliation.effective_status, applies, reason and project provenance update008_reconciliation_applied/reason;
   - actual frozen u8_out.state, update008 unknown/conflict ref counts, roles/role_runtime types, rr.state, unresolved_reasons, primary_unit_id, transition value AND identity, QBU counts, runtime provenance keys;
   - actual mechanism WATCH state, other mechanism non-null states, mechanism actual status; lineage status/relation/evidence ref count, lineage actual status;
   - explicit source/time/ref provenance for whichever category downgrades.
5. Run exactly ONE original outer V6.run_cutoff on existing SYNTH genesis bar (open_time=73800000, close_time=74699999); strict outer call cap<=1, earlier=0, SHORT=0, later=0. Original raw/post internal engine calls allowed. No 156-row replay.
6. If projector returns BLOCKED_CRITICAL_UNKNOWN again, do NOT modify SourceCoverageFact COMPLETE labels, underlying frozen Update008Output, unknown/conflict refs, RoleRuntimeOutput, no-Primary semantics, WATCH outputs, or original guards. Stop. Report exact downrated class and **first specific reconciliation reason** and whether from science evidence or a specific proven loader class-identity mismatch. Do not automatically fix-and-retry same genesis.
7. If unexpectedly static projector returns READY and original genesis progresses, observe only original same-cutoff D4 packet and F9 UPDATE-011 outcome; never force lineage commit. On any new genuine error, report exact original code and stop. Only the original end-to-end return GENESIS_FULL_TYPED_STAGED with actual staged engine success and lineage.commit can be called a synthetic-engineering genesis closure; does not resolve independent governance/persistence blockers.
8. Send concise scalar report with measured six caller-versus-effective statuses, exact reconciliation status/applies/reason, frozen Update008 vs reconciled coverage (do not conflate), function module/class provenance, batch tx/candidate digest if currently observed, outer call count, before/after state, lineage prepare/commit/abort, packet and F9 reached or NOT_REACHED, and first genuine next blocker. Preserve all outputs as SYNTH-only.

Hard safety: all 160 input records are random.Random(0) SYNTH synthetic fixture, not verified real market history. Frozen strategy.py SHA256 792d2818d8495889319de5b3e6019ac0e856d27a59c6c959ac355ff239765a5f; spec.yaml SHA256 4fb02c4559fc2fe8ee4e95390b76fce132f5af34c4f7e23a0091f1c8f8108fd1. 528 symbols; TAC_LIVE_ENABLED=0, subscriptions OFF. TEST_ONLY, no exchange market/account/order I/O, deployment, Paper/Live, trades, performance, real-market authority or persistence claims. PORT007_UNRESOLVED_PRODUCTION_ALLOCATION_BLOCKED and BLOCKED_D3_B3_JOINT_PERSISTENCE remain independent blocks.
