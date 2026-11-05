"""Non-mutating, deterministic original B5 UNKNOWN lineage inspector.

Call ONLY on actual output returned by frozen TAC_BASE_produce_update008.
It does NOT recompute or replace any QBU, boundary, role or D4 decision.
Useful when same-cutoff original identity and Minor projections pass but
the B5 stage stays UNKNOWN (e.g. 68/68 UNKNOWN in current synthetic loop).
No positive authority can be manufactured by this diagnostic function.
"""
def _tac_original_qbu_b5_unknown_diagnostic_v1(
        *,
        original_request,
        original_output,
        original_prior_role_memory=None,
        original_next_role_memory=None,
        source_mode="SYNTHETIC_TEST_ONLY"):
    if TAC_LIVE_ENABLED != 0:
        raise ValueError("DIAGNOSTIC_REQUIRES_NO_TRADING")
    if not isinstance(original_request,TAC_BASE_Update008Request):
        raise ValueError("ORIGINAL_B5_INPUT_SCHEMA_REQUIRED")
    if not isinstance(original_output,TAC_BASE_Update008Output):
        raise ValueError("ORIGINAL_B5_OUTPUT_SCHEMA_REQUIRED")
    if original_prior_role_memory is not None and not isinstance(
            original_prior_role_memory,TAC_BASE_RoleMemory):
        raise ValueError("PRIOR_ORIGINAL_ROLE_MEMORY_SCHEMA_REQUIRED")
    if original_next_role_memory is not None and not isinstance(
            original_next_role_memory,TAC_BASE_RoleMemory):
        raise ValueError("NEXT_ORIGINAL_ROLE_MEMORY_SCHEMA_REQUIRED")
    if original_output.state is EvidenceState.CONFLICT:
        status="BLOCKED_ORIGINAL_B5_CONFLICT"
    elif original_output.state is EvidenceState.UNKNOWN:
        status="BLOCKED_ORIGINAL_B5_UNKNOWN"
    elif original_output.state is EvidenceState.TRUE:
        status="OBSERVED_ORIGINAL_B5_TRUE_NO_EXECUTION_AUTHORITY"
    else:
        raise ValueError("UNRECOGNIZED_ORIGINAL_B5_EVIDENCE_STATE")
    rr=original_output.role_runtime
    if rr is not None and rr.assignment is not original_output.roles:
        # Enum, immutable role assignment and original result lineage must agree.
        if rr.assignment!=original_output.roles:
            raise ValueError("ORIGINAL_ROLE_OUTPUT_IDENTITY_MISMATCH")
    if original_prior_role_memory is not None:
        if original_prior_role_memory.trend_episode_id!=original_request.trend_episode_id:
            raise ValueError("ROLE_MEMORY_DIFFERENT_ORIGINAL_D2_TREND_EPISODE")
    if original_next_role_memory is not None:
        if original_next_role_memory.trend_episode_id!=original_request.trend_episode_id:
            raise ValueError("NEW_ROLE_MEMORY_DIFFERENT_ORIGINAL_D2_TREND_EPISODE")
    request=original_request
    output=original_output
    available_snapshots=sum(1 for s in request.snapshots
        if s.available_at<=request.information_cutoff)
    relinked_snapshots=sum(1 for s in request.snapshots
        if s.available_at<=request.information_cutoff
        and s.anchor_episode_id is not None)
    material_records=sum(1 for rec in request.progress_evidence
        if rec.progress.material_progress is True
        and rec.progress.confirmed_at<=request.information_cutoff)
    raw_progress_records=len(request.progress_evidence)
    role=output.roles
    return {
        "schema":"ORIGINAL_TAC_B5_UNKNOWN_NONMUTATING_DIAGNOSTIC_V1",
        "status":status,
        "symbol":next((c.symbol for c in request.candidates),None),
        "trend_episode_id":request.trend_episode_id,
        "cutoff":request.information_cutoff,
        "source_mode":source_mode,
        "original_b5_state":output.state.value,
        "original_b5_unknown_lineage_refs":tuple(output.unknown_lineage_refs),
        "original_b5_conflict_lineage_refs":tuple(output.conflict_lineage_refs),
        "original_role_unresolved_reasons":tuple(
            rr.unresolved_reasons if rr is not None else ()),
        "original_role_conflict_reasons":tuple(
            rr.conflict_reasons if rr is not None else ()),
        "input_anchors":len(request.episodes),
        "input_interaction_events":len(request.events),
        "input_candidates":len(request.candidates),
        "input_available_snapshots":available_snapshots,
        "input_anchor_relinked_snapshots":relinked_snapshots,
        "input_raw_minor_progress_records":raw_progress_records,
        "input_material_minor_progress_records":material_records,
        "input_known_negotiation_identities":len(
            request.negotiation_identity_by_event_id),
        "input_confirmed_continuity_candidates":sum(
            1 for v in request.continuity_by_candidate_id.values() if v is True),
        "original_b5_contact_zones":len(output.zones),
        "original_b5_economic_units":len(output.units),
        "original_b5_produced_qbus":len(output.produced_qbus),
        "original_b5_roles":(
            None if role is None else {
                "primary_present":role.primary_unit_id is not None,
                "secondary_present":role.secondary_unit_id is not None,
                "transition":role.transition.value}),
        "original_role_prior_primary_continuity_preserved":(
            None if rr is None else rr.prior_primary_continuity_preserved),
        "prior_role_memory_qbu_identities":(
            () if original_prior_role_memory is None else
            tuple(original_prior_role_memory.primary_qbu_identities)),
        "next_role_memory_qbu_identities":(
            () if original_next_role_memory is None else
            tuple(original_next_role_memory.primary_qbu_identities)),
        "is_mutating_original_science":False,
        "entry_ready":False,"trade_authorized":False,
        "TAC_LIVE_ENABLED":0,"orders":0}
