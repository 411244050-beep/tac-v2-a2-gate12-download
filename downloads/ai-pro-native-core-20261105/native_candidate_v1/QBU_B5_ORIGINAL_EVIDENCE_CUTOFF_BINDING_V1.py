"""Original-source QBU negotiation + 15m Minor progress -> B5 UPDATE008.

Source-only TEST_ONLY bridge. The THREE original frozen modules are the
TAC_BASE_, TAC_ID_ and TAC_PR_ namespaced source appended to strategy.py.
Only complete synthetic fixture coverage is presently authorized for positive
execution. Genuine native market epoch lacking restart/coverage proofs
FAILS CLOSED. No invented boundaries, event IDs, progress truth or positions.
"""
def _tac_original_qbu_b5_synthetic_cutoff_v1(
    *,
    symbol,
    information_cutoff,
    trend_episode_id,
    direction,
    source_receipt,
    snapshots,
    candidates,
    anchor_episodes,
    interaction_events,
    all_original_d2_minor,
    canonical_segment_id_by_anchor_episode_id,
    continuity_by_candidate_id,
    corridor,
    protected_price,
    protected_scale,
    trend_episode_start_cutoff,
    trend_episode_terminal_cutoff=None,
    prior_role_memory=None,
):
    if TAC_LIVE_ENABLED != 0:
        raise ValueError("TEST_ONLY_NONTRADING_REQUIRED")
    blocked={
        "status":"BLOCKED_EPOCH_CONTINUITY_UNPROVEN",
        "qbu_identity_bound":False,
        "qbu_minor_progress_bound":False,
        "b5_original_update008_bound":False,
        "producer_mutated":False,
        "entry_ready":False,
        "TAC_LIVE_ENABLED":0,"orders":0,
        "trade_authorized":False}
    if type(source_receipt) is not dict or source_receipt.get("mode") != "SYNTHETIC_TEST_ONLY_FULL_SOURCE":
        return blocked
    if (source_receipt.get("history_complete") is not True
        or source_receipt.get("provenance_complete") is not True
        or source_receipt.get("same_cutoff_order_proven") is not True
        or source_receipt.get("continuity_intact") is not True):
        return blocked
    if source_receipt.get("real_epoch_authorized") is not False:
        raise ValueError("SYNTHETIC_SOURCE_MUST_NEVER_DECLARE_REAL_EPOCH")
    if type(symbol) is not str or not symbol:
        raise ValueError("ORIGINAL_SYMBOL_REQUIRED")
    if type(information_cutoff) is not int or information_cutoff < 0:
        raise ValueError("ORIGINAL_CAUSAL_CUTOFF_REQUIRED")
    if type(trend_episode_id) is not str or not trend_episode_id:
        raise ValueError("ORIGINAL_D2_EPISODE_REQUIRED")
    if direction not in (TrendDirection.LONG,TrendDirection.SHORT):
        raise ValueError("ORIGINAL_TREND_DIRECTION_REQUIRED")
    for name,rows,typ in (
        ("D3_SNAPSHOTS",snapshots,CausalBoundarySnapshot),
        ("D3_CANDIDATES",candidates,MathematicalBoundaryCandidate),
        ("D3_EPISODES",anchor_episodes,AnchorEpisode),
        ("D3_EVENTS",interaction_events,InteractionEvent),
        ("D2_MINORS",all_original_d2_minor,StructuralPivot)):
        if type(rows) is not tuple or any(not isinstance(x,typ) for x in rows):
            raise ValueError("ORIGINAL_"+name+"_SOURCE_TYPE_MISMATCH")
    if any(p.layer is not StructuralLayer.MINOR or p.timeframe_ms!=900000
           for p in all_original_d2_minor):
        raise ValueError("ONLY_REAL_D2_15M_MINOR_PIVOTS_ALLOWED")
    if any(p.confirmed_at>information_cutoff for p in all_original_d2_minor):
        raise ValueError("FUTURE_MINOR_PIVOT_FORBIDDEN")
    if any(e.resolved_at is not None and e.resolved_at>information_cutoff
           for e in interaction_events):
        raise ValueError("FUTURE_D3_EVENT_FORBIDDEN")
    if (type(canonical_segment_id_by_anchor_episode_id) is not dict
        or type(continuity_by_candidate_id) is not dict):
        raise ValueError("ACTUAL_D3_SOURCE_LEDGER_DICT_REQUIRED")
    if type(trend_episode_start_cutoff) is not int:
        raise ValueError("D2_TREND_START_CUTOFF_REQUIRED")
    if (trend_episode_terminal_cutoff is not None and
        type(trend_episode_terminal_cutoff) is not int):
        raise ValueError("D2_TREND_TERMINAL_CUTOFF_INVALID")
    if prior_role_memory is not None and not isinstance(prior_role_memory,TAC_BASE_RoleMemory):
        raise ValueError("B5_ORIGINAL_ROLE_MEMORY_REQUIRED")
    # Source the *already scientifically FROZEN* QBU thresholds, not
    # the separate OPEN TEST_ONLY structural theta values used by D2.
    scientific=current_partial_parameter_snapshot()
    theta=frozen_d3_parameters(scientific)
    base=TAC_BASE_Update008Request(
        information_cutoff=information_cutoff,
        trend_episode_id=trend_episode_id,
        direction=direction,
        snapshots=snapshots,candidates=candidates,episodes=anchor_episodes,
        events=interaction_events,progress_evidence=(),
        negotiation_identity_by_event_id={},
        canonical_segment_id_by_anchor_episode_id=canonical_segment_id_by_anchor_episode_id,
        continuity_by_candidate_id=continuity_by_candidate_id,
        corridor=corridor,protected_price=protected_price,
        protected_scale=protected_scale,
        theta_test=theta.theta_test,theta_progress=theta.theta_progress,
        provenance={"source_mode":"SYNTHETIC_TEST_ONLY_FULL_SOURCE",
                    "original_symbol":symbol,
                    "original_D2_episode":trend_episode_id})
    identity_request=TAC_ID_NegotiationIdentityRequest(
        information_cutoff=information_cutoff,
        trend_episode_id=trend_episode_id,
        direction=direction,events=interaction_events,episodes=anchor_episodes,
        continuity_by_candidate_id=continuity_by_candidate_id,
        theta_test=theta.theta_test,
        rearm_predecessor_by_event_id=dict(source_receipt.get(
            "actual_rearm_predecessor_by_event_id",{})),
        history_complete=True,
        provenance={"source_mode":"SYNTHETIC_TEST_ONLY_FULL_SOURCE"})
    identity=TAC_ID_project_negotiation_identity(identity_request)
    if identity.status != TAC_ID_STATUS_KNOWN:
        return {
            **blocked,
            "status":"BLOCKED_QBU_IDENTITY_"+identity.status,
            "negotiation_identity_status":identity.status,
            "unknown_refs":tuple(identity.unknown_refs),
            "conflict_refs":tuple(identity.conflict_refs)}
    base=TAC_ID_bind_update008_request(base,identity)
    progress_request=TAC_PR_QBUProgressProductionRequest(
        update008_request=base,
        all_minor=all_original_d2_minor,
        trend_episode_start_cutoff=trend_episode_start_cutoff,
        trend_episode_terminal_cutoff=trend_episode_terminal_cutoff,
        history_complete=True,
        history_coverage_ref=source_receipt.get("synthetic_coverage_ref",""),
        theta_progress_parameter_ref=scientific.snapshot_id+":theta_progress",
        provenance={"source_mode":"SYNTHETIC_TEST_ONLY_FULL_SOURCE"})
    progress=TAC_PR_project_qbu_progress_evidence(progress_request)
    if progress.state is not EvidenceState.TRUE:
        return {
            **blocked,
            "status":"BLOCKED_QBU_MINOR_"+progress.state.value,
            "qbu_identity_bound":True,
            "negotiation_identity_by_event_id":dict(identity.negotiation_identity_by_event_id),
            "minor_progress_status":progress.state.value,
            "unknown_refs":tuple(progress.unknown_refs),
            "conflict_refs":tuple(progress.conflict_refs)}
    base=TAC_PR_bind_update008_request(base,progress)
    output,next_memory=TAC_BASE_produce_update008(
        base,prior_memory=prior_role_memory)
    if output.state is EvidenceState.CONFLICT:
        return {
            **blocked,
            "status":"BLOCKED_B5_ORIGINAL_CONFLICT",
            "qbu_identity_bound":True,"qbu_minor_progress_bound":True,
            "b5_original_update008_bound":True,
            "B5_conflicts":tuple(output.conflict_lineage_refs)}
    return {
        "status":"SYNTHETIC_ORIGINAL_QBU_B5_EVALUATED",
        "source_mode":"SYNTHETIC_TEST_ONLY_FULL_SOURCE",
        "qbu_identity_bound":True,
        "qbu_minor_progress_bound":True,
        "b5_original_update008_bound":True,
        "negotiation_identity_status":identity.status,
        "minor_progress_status":progress.state.value,
        "B5_state":output.state.value,
        "original_boundaries":output.zones,
        "original_economic_units":output.units,
        "original_role_evidence":output.role_evidence,
        "original_roles":output.roles,
        "original_qbus":output.produced_qbus,
        "next_original_role_memory":next_memory,
        "entry_ready":False,
        "TAC_LIVE_ENABLED":0,"trade_authorized":False,"orders":0,"fills":0,
        "D4_F9_D5_UPDATE014_D6":"NOT_CONNECTED"}
