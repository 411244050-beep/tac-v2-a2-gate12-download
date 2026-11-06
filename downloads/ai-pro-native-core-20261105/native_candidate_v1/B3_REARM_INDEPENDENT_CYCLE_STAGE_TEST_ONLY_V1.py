"""Explicitly user-authorized isolated TEST_ONLY bridge for D3 new-cycle rearm.

ENGINEERING ADAPTER PROPOSAL V1 — NOT frozen science, not native Binance
source, not a strategy deployment, and NOT durable or joint atomic storage.
Runs on isolated copies only. Do not attach to a live/Paper workflow.

The *old* original D3 event stays RESOLVED until original D3 is invoked.
For a new independent cycle only, a staged frozen B3 observation uses its
existing UNARMED+separated first-arming entry branch, after checking exact
original rearm authority and absence of a B3 pending. This is the explicit
new-cycle representation approved for isolated TEST_ONLY experiments only.
"""


def _tac_b3_rearm_new_cycle_stage_test_only_v1(
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
    source_receipt,
    validate_staged_receipt=None,
):
    from copy import deepcopy

    if TAC_LIVE_ENABLED != 0:
        raise ValueError("B3_REARM_TEST_ONLY_NO_TRADING_REQUIRED")
    if not (
        type(source_receipt) is dict
        and source_receipt.get("mode") == "SYNTHETIC_TEST_ONLY_FULL_SOURCE"
        and source_receipt.get("history_complete") is True
        and source_receipt.get("provenance_complete") is True
        and source_receipt.get("same_cutoff_order_proven") is True
        and source_receipt.get("restart_coverage_proven") is True
    ):
        raise ValueError("B3_REARM_SYNTHETIC_FULL_SOURCE_RECEIPT_REQUIRED")
    if type(source_continuity_intact) is not bool or type(candidate_terminally_replaced) is not bool:
        raise ValueError("B3_REARM_EXPLICIT_SOURCE_TRUTH_REQUIRED")
    if not source_continuity_intact or candidate_terminally_replaced:
        raise ValueError("B3_REARM_SOURCE_CONTINUITY_OR_REPLACEMENT_BLOCK")
    if not isinstance(producer, RuntimeB3PriceDrivenReturnProducerV1):
        raise ValueError("B3_REARM_FROZEN_PRODUCER_REQUIRED")
    if not isinstance(d3, D3ReferenceSkeleton):
        raise ValueError("B3_REARM_ORIGINAL_D3_REQUIRED")
    if not isinstance(bar.close_time, int) or not isinstance(bar.open_time, int):
        raise ValueError("B3_REARM_BAR_TIMES_REQUIRED")
    if bar.open_time >= bar.close_time or geometry.information_cutoff != bar.close_time:
        raise ValueError("B3_REARM_CUTOFF_DRIFT")
    if geometry.snapshot_id != snapshot.snapshot_id:
        raise ValueError("B3_REARM_PREBAR_GEOMETRY_SNAPSHOT_ID_MISMATCH")
    if not geometry.separated:
        raise ValueError("B3_REARM_MATERIAL_SEPARATION_REQUIRED")
    if (
        bar.symbol != candidate.symbol
        or snapshot.symbol != candidate.symbol
        or candidate.candidate_id != snapshot.candidate_id
        or candidate.source_segment_id != snapshot.source_segment_id
        or candidate.source_timeframe_ms != snapshot.source_timeframe_ms
        or candidate.target_trend_episode_id != snapshot.target_trend_episode_id
        or candidate.target_direction is not snapshot.target_direction
    ):
        raise ValueError("B3_REARM_CANDIDATE_SNAPSHOT_LINEAGE_DRIFT")
    if (
        candidate.availability is not CandidateAvailability.AVAILABLE
        or snapshot.available_at > bar.open_time
    ):
        raise ValueError("B3_REARM_UNAVAILABLE_OR_NONCAUSAL_PREBAR")
    if (
        current_trend.episode_id != candidate.target_trend_episode_id
        or current_trend.direction is not candidate.target_direction
    ):
        raise ValueError("B3_REARM_D2_TREND_MISMATCH")

    # Unmodified prebar authority, never post-hoc relinking.
    prebar = d3.update_000_pre_bar_view(bar.open_time)
    matching = tuple(
        x for x in prebar.snapshots if x.candidate_id == candidate.candidate_id
    )
    if len(matching) != 1 or matching[0].snapshot_id != snapshot.snapshot_id:
        raise ValueError("B3_REARM_PREBAR_SNAPSHOT_LINEAGE_MISMATCH")

    original_geometry = d3.update_002_capture_geometry(bar=bar, information_cutoff=bar.close_time, snapshot=snapshot)
    if original_geometry != geometry:
        raise ValueError("B3_REARM_GEOMETRY_ORIGIN_MISMATCH")

    before = d3.current_event(candidate.candidate_id)
    if (
        before.control is not InteractionControl.RESOLVED
        or before.terminal
        or before.resolved_at is None
        or before.resolved_at >= bar.close_time
        or before.target_trend_episode_id != candidate.target_trend_episode_id
        or before.target_direction is not candidate.target_direction
    ):
        raise ValueError("B3_REARM_ORIGINAL_PRIOR_EVENT_NOT_ELIGIBLE")

    projected = rearm_after_resolution(before, geometry=geometry)
    if (
        projected.control is not InteractionControl.ARMED
        or projected.event_id == before.event_id
        or projected.armed_at != bar.close_time
        or projected.provenance.get("prior_event_id") != before.event_id
        or projected.provenance.get("rearm") != "MATERIAL_CORRECT_SIDE_SEPARATION"
    ):
        raise ValueError("B3_REARM_ORIGINAL_NEW_EVENT_PROJECTION_FAILED")
    if producer.pending_state(bar.symbol, candidate.candidate_id) is not None:
        raise ValueError("B3_REARM_OLD_PENDING_NOT_ABSENT")

    # The caller's original D3 and B3 objects are not mutated, even on success.
    staged_d3 = deepcopy(d3)
    staged_b3 = RuntimeB3PriceDrivenReturnProducerV1.restore_state(
        producer.export_state()
    )
    # Only the NEW-cycle pre-arming observation is mapped to this frozen
    # producer's existing entry branch. Original prior D3 is NEVER UNARMED.
    new_cycle_obs = RuntimeB3Observation(
        bar=bar,
        snapshot=snapshot,
        geometry=geometry,
        interaction_control=InteractionControl.UNARMED,
        params=staged_d3.params,
        symbol=bar.symbol,
        candidate_id=candidate.candidate_id,
        source_segment_id=candidate.source_segment_id,
        target_trend_episode_id=candidate.target_trend_episode_id,
        target_direction=candidate.target_direction,
        current_trend_episode_id=current_trend.episode_id,
        current_trend_direction=current_trend.direction,
        canonical_continuity_intact=source_continuity_intact,
        candidate_available=True,
        terminal_candidate_replacement=False,
        interaction_terminal=False,
    )

    # Identity-based transaction ID deliberately EXCLUDES mutable input digest.
    # Same stable transaction with differing input must be rejected by frozen
    # process_batch's separate input_digest field, not evade the conflict check.
    txn = deterministic_id(
        "TAC-B3-NEW-INDEPENDENT-CYCLE-TESTONLY-V1",
        candidate.candidate_id,
        candidate.target_trend_episode_id,
        candidate.source_segment_id,
        str(bar.close_time),
        projected.event_id,
    )
    one = staged_b3.process_batch(txn, (new_cycle_obs,))
    if len(one) != 1:
        raise ValueError("B3_REARM_RESULT_MULTIPLICITY")
    b3_output = one[0]
    pending = staged_b3.pending_state(bar.symbol, candidate.candidate_id)
    if (
        b3_output.reason != "ARMED_FROZEN_CURRENT_CUTOFF_NO_RETURN"
        or b3_output.return_evidence is not None
        or b3_output.latched_evidence is not None
        or pending is None
        or pending.arming_information_cutoff != bar.close_time
        or pending.arming_bar_close != bar.close
        or pending.arming_scale != snapshot.source_scale
        or pending.arming_snapshot_id != snapshot.snapshot_id
        or pending.arming_anchor_episode_id != snapshot.anchor_episode_id
        or pending.target_trend_episode_id != candidate.target_trend_episode_id
        or pending.source_segment_id != candidate.source_segment_id
        or pending.target_direction != candidate.target_direction.value
    ):
        raise ValueError("B3_REARM_FROZEN_PENDING_ORIGIN_MISMATCH")

    # D3 remains the single original authority. Call exactly once on the
    # prior RESOLVED state and compare to original pure rearm projection.
    actual_event = staged_d3.update_007_interaction_break(
        snapshot=snapshot,
        geometry=geometry,
        return_evidence=None,
        structural_acceptance=None,
        correct_side_recovery=None,
    )
    if actual_event != projected:
        raise ValueError("B3_REARM_ORIGINAL_D3_EVENT_DIFF")
    stage_episode = staged_d3.update_008_anchor_lifecycle(
        candidate=candidate,
        target_trend_active=True,
        candidate_terminally_invalidated=False,
        cutoff=bar.close_time,
    )
    # Full source digest is separately recorded. Does not alter transaction ID.
    observation_digest = _digest_record(_observation_record(new_cycle_obs))
    receipt = {
        "contract": "B3_REARM_INDEPENDENT_CYCLE_STAGE_TEST_ONLY_V1",
        "transaction_id": txn,
        "observation_digest": observation_digest,
        "candidate_id": candidate.candidate_id,
        "old_event_id": before.event_id,
        "new_event_id": actual_event.event_id,
        "information_cutoff": bar.close_time,
        "source_segment_id": candidate.source_segment_id,
        "D2_trend_episode_id": current_trend.episode_id,
        "arming_snapshot_id": snapshot.snapshot_id,
        "B3_state_digest": staged_b3.state_digest(),
        "D3_event_is_authoritative_original": True,
        "entry_ready": False,
        "TAC_LIVE_ENABLED": 0,
        "orders": 0,
        "stage_only": True,
        "durable_joint_checkpoint": False,
    }
    if validate_staged_receipt is not None:
        # Failures here leave both original objects unchanged.
        validate_staged_receipt(receipt)
    return {
        "status": "STAGED_TEST_ONLY_NO_DURABLE_COMMIT",
        "event": actual_event,
        "episode": stage_episode,
        "b3_output": b3_output,
        "staged_d3": staged_d3,
        "staged_b3": staged_b3,
        "receipt": receipt,
        "entry_ready": False,
        "orders": 0,
    }
