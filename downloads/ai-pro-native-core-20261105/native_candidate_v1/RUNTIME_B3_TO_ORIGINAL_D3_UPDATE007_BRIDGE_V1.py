"""TEST_ONLY adapter from frozen Runtime-B3 return producer to exact D3 methods.

Append AFTER frozen Runtime-B3 source in the same original strategy.py.
This is a no-trading causal adapter, not a new return criterion. All required
truth flags must be established from actual upstream source, never defaults.
Call only AFTER this cutoff's original D2 UPDATE-005/006 output is available.
"""

def _tac_frozen_b3_update007_step(
    *,
    producer,
    d3,
    candidate,
    snapshot,
    geometry,
    bar,
    current_trend,
    source_continuity_intact,
    candidate_terminally_replaced,
    history_complete,
):
    if TAC_LIVE_ENABLED != 0:
        raise ValueError("TAC_F3_TEST_ONLY_REQUIRED")
    if not all(type(x) is bool for x in (
        source_continuity_intact,candidate_terminally_replaced,history_complete
    )):
        raise ValueError("TAC_F3_EXPLICIT_SOURCE_TRUTH_REQUIRED")
    if not history_complete:
        raise ValueError("TAC_F3_INCOMPLETE_REPLAY_OR_RESTART_UNKNOWN")
    if not isinstance(producer,RuntimeB3PriceDrivenReturnProducerV1):
        raise ValueError("TAC_F3_FROZEN_RUNTIME_B3_PRODUCER_REQUIRED")
    if not isinstance(d3,D3ReferenceSkeleton):
        raise ValueError("TAC_F3_ORIGINAL_D3_STATE_REQUIRED")
    if candidate.candidate_id != snapshot.candidate_id:
        raise ValueError("TAC_F3_ORIGINAL_CANDIDATE_ID_MISMATCH")
    if candidate.symbol != bar.symbol or snapshot.symbol != bar.symbol:
        raise ValueError("TAC_F3_SYMBOL_LINEAGE_MISMATCH")
    if (candidate.target_trend_episode_id!=snapshot.target_trend_episode_id
        or candidate.target_direction is not snapshot.target_direction):
        raise ValueError("TAC_F3_TREND_LINEAGE_MISMATCH")
    if candidate.source_segment_id != snapshot.source_segment_id:
        raise ValueError("TAC_F3_CANONICAL_SEGMENT_DRIFT")
    if (candidate.availability is not CandidateAvailability.AVAILABLE
        or snapshot.available_at > bar.open_time):
        raise ValueError("TAC_F3_PREBAR_SOURCE_NOT_AVAILABLE")
    if geometry.information_cutoff != bar.close_time:
        raise ValueError("TAC_F3_GEOMETRY_CUTOFF_DRIFT")
    before=d3.current_event(snapshot.candidate_id)
    if before.target_trend_episode_id != snapshot.target_trend_episode_id:
        raise ValueError("TAC_F3_EVENT_TREND_EPISODE_DRIFT")
    if before.target_direction is not snapshot.target_direction:
        raise ValueError("TAC_F3_EVENT_TREND_DIRECTION_DRIFT")
    obs=RuntimeB3Observation(
        bar=bar,snapshot=snapshot,geometry=geometry,
        interaction_control=before.control,params=d3.params,
        symbol=bar.symbol,candidate_id=candidate.candidate_id,
        source_segment_id=candidate.source_segment_id,
        target_trend_episode_id=candidate.target_trend_episode_id,
        target_direction=candidate.target_direction,
        current_trend_episode_id=current_trend.episode_id,
        current_trend_direction=current_trend.direction,
        canonical_continuity_intact=source_continuity_intact,
        candidate_available=True,
        terminal_candidate_replacement=candidate_terminally_replaced,
        interaction_terminal=before.terminal)
    # Unique original candidate and closed-cutoff transaction, no version
    # chosen by signal magnitude or price outcome.
    tx=deterministic_id("TAC-FROZEN-RUNTIME-B3",bar.symbol,
        candidate.candidate_id,str(bar.close_time),
        candidate.source_segment_id)
    one=producer.process_batch(tx,(obs,))
    if len(one)!=1:
        raise ValueError("TAC_F3_SINGLE_CANDIDATE_RESULT_MISMATCH")
    original=one[0]
    if original.continuity_resolution=="UNKNOWN_CONTINUITY":
        event=d3.continuity_break(candidate.candidate_id,cutoff=bar.close_time)
        return {"producer":original,"event":event,"episode":None,
                "continuity":"BLOCKED_UNKNOWN_CONTINUITY","entry_ready":False}
    if original.continuity_resolution is not None:
        raise ValueError("TAC_F3_UNHANDLED_CONTINUITY_RESOLUTION")
    event=d3.update_007_interaction_break(
        snapshot=snapshot,geometry=geometry,
        return_evidence=original.return_evidence,
        structural_acceptance=None,correct_side_recovery=None)
    active=(current_trend.episode_id==candidate.target_trend_episode_id
            and current_trend.direction is candidate.target_direction)
    episode=d3.update_008_anchor_lifecycle(
        candidate=candidate,target_trend_active=active,
        candidate_terminally_invalidated=(
            candidate_terminally_replaced or event.terminal
            and event.break_state is BreakState.TRUE_BREAK),
        cutoff=bar.close_time)
    return {"producer":original,"event":event,"episode":episode,
            "continuity":"KNOWN_EXACT_SOURCE_ONLY",
            "B4_structural_acceptance":"NOT_PRODUCED",
            "B5_qualified_boundary_use":"NOT_PRODUCED",
            "D4_F9_D5_UPDATE014_D6":"NOT_EXECUTED",
            "entry_ready":False,"trade_authorized":False,
            "orders":0,"TAC_LIVE_ENABLED":0}
