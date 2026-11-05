"""Frozen original B4 producer binding: D2 MINOR pivots + original D3 event.

This is not new market science. Never infer truth from a missing source field.
The original return/structural values remain four-state and fail-closed.
A complete SYNTHETIC_TEST_ONLY fixture exercises source-level positive cases;
a real prospective epoch still needs an authenticated upstream receipt.
"""
def _tac_original_b4_from_D2_D3_source_v1(
    *,
    bar,
    original_d3_event,
    original_d2_minor_pivots,
    source_receipt,
    theta_progress,
    separation_origin_open_time,
    separation_cutoff,
    attempt_origin_open_time,
    attempt_cutoff,
):
    if TAC_LIVE_ENABLED != 0:
        raise ValueError("ORIGINAL_B4_NONTRADING_ONLY")
    blocked={
        "status":"BLOCKED_EPOCH_CONTINUITY_UNPROVEN",
        "original_B4_bound":False,
        "structural_acceptance":None,
        "correct_side_recovery":None,
        "B5_QBU_D4_F9_D5_UPDATE014_D6":"NOT_CONNECTED",
        "entry_ready":False,"trade_authorized":False,
        "TAC_LIVE_ENABLED":0,"orders":0}
    # No real prospective epoch assertion is possible from this adapter alone.
    # The synthetic source is a test scope, never native market proof.
    if type(source_receipt) is not dict or source_receipt.get("mode")!="SYNTHETIC_TEST_ONLY_FULL_SOURCE":
        return blocked
    if source_receipt.get("complete") is not True or source_receipt.get("same_cutoff_order_proven") is not True:
        return blocked
    if source_receipt.get("canonical_continuity_intact") is not True:
        return blocked
    refs=source_receipt.get("source_evidence_refs")
    if type(refs) is not tuple or not refs or not all(type(x) is str and x for x in refs):
        return blocked
    if type(original_d2_minor_pivots) is not tuple:
        raise ValueError("B4_ACTUAL_D2_MINOR_TUPLE_REQUIRED")
    if not all(isinstance(p,StructuralPivot) for p in original_d2_minor_pivots):
        raise ValueError("B4_ORIGINAL_STRUCTURAL_PIVOTS_REQUIRED")
    if not isinstance(original_d3_event,InteractionEvent):
        raise ValueError("B4_ORIGINAL_D3_INTERACTION_REQUIRED")
    if type(theta_progress) is not Fraction or theta_progress<=0:
        raise ValueError("B4_FROZEN_THETA_PROGRESS_EXACT_FRACTION_REQUIRED")
    cutoff=bar.close_time
    if type(cutoff) is not int:
        raise ValueError("B4_EXACT_BAR_CUTOFF_REQUIRED")
    if not original_d3_event.event_id or not original_d3_event.target_trend_episode_id:
        raise ValueError("B4_D3_EVENT_IDENTITY_MISSING")
    if original_d3_event.target_direction not in (
        TrendDirection.LONG,TrendDirection.SHORT):
        raise ValueError("B4_D3_LONG_OR_SHORT_REQUIRED")
    if type(separation_origin_open_time) is not int or type(separation_cutoff) is not int:
        raise ValueError("B4_ACTUAL_SEPARATION_TIMING_REQUIRED")
    if type(attempt_origin_open_time) is not int or type(attempt_cutoff) is not int:
        raise ValueError("B4_ACTUAL_ATTEMPT_TIMING_REQUIRED")
    if any(t>cutoff for t in (separation_origin_open_time,
        separation_cutoff,attempt_origin_open_time,attempt_cutoff)):
        raise ValueError("B4_FUTURE_INFORMATION_FORBIDDEN")
    if any(p.confirmed_at>cutoff for p in original_d2_minor_pivots):
        raise ValueError("B4_FUTURE_PIVOTS_FORBIDDEN")
    ctx=LineageContext(
        symbol=bar.symbol,
        target_trend_episode_id=original_d3_event.target_trend_episode_id,
        direction=original_d3_event.target_direction,
        information_cutoff=cutoff,
        canonical_segment_id=source_receipt.get("canonical_segment_id",""),
        interaction_event_id=original_d3_event.event_id,
        market_event_id=source_receipt.get("market_event_id"),
        source_evidence_refs=refs,
        continuity_known=True,continuity_intact=True,
        same_cutoff_order_proven=True)
    sa=produce_structural_acceptance(StructuralAcceptanceRequest(
        context=ctx,interaction=original_d3_event,
        pivots=original_d2_minor_pivots,
        separation_origin_open_time=separation_origin_open_time,
        separation_cutoff=separation_cutoff,
        theta_progress=theta_progress,
        prior_reclaim_cutoffs=tuple(source_receipt.get("actual_prior_reclaim_cutoffs",()))))
    cr=produce_correct_side_recovery(CorrectSideRecoveryRequest(
        context=ctx,interaction=original_d3_event,
        pivots=original_d2_minor_pivots,
        attempt_origin_open_time=attempt_origin_open_time,
        attempt_cutoff=attempt_cutoff,
        evaluating_close=bar.close))
    # B4 is allowed to make four-state evidence, not "force" confirmed entry.
    # No positive result can become trade permission without full B5->D4->D5.
    return {
        "status":"SYNTHETIC_TEST_ONLY_ORIGINAL_B4_EVALUATED",
        "original_B4_bound":True,
        "structural_acceptance_state":sa.state.value,
        "structural_acceptance_reason":sa.reason,
        "structural_acceptance":safe_b4_consumer(sa),
        "correct_side_recovery_state":cr.state.value,
        "correct_side_recovery_reason":cr.reason,
        "correct_side_recovery":safe_b4_consumer(cr),
        "consumer_conflict_silently_promoted":False,
        "B5_QBU_D4_F9_D5_UPDATE014_D6":"NOT_CONNECTED",
        "entry_ready":False,"trade_authorized":False,
        "TAC_LIVE_ENABLED":0,"orders":0}
