"""Frozen-source WATCH-REARM reciprocal *membership* view (TEST_ONLY).

Explicitly READ-ONLY diagnostic; not a change to original D3, B3/B4, QBU
science, Episode membership, a contact event or trading authority.
The original D3 Episode ALREADY owns the watch ID. Original bind_event_to_episode
can reflect this reciprocal membership in an immutable consumer input VIEW
without adding started_at, resolved_at, reference geometry, return or QBU.

This is NOT cleared for a Binance strategy write or official native merge.
If any original source/transition identity is absent, fails closed.
"""


def _tac_qbu_watch_rearm_member_view_test_only_v1(
    *,
    events,
    episodes,
    information_cutoff,
    history_complete,
):
    if TAC_LIVE_ENABLED != 0:
        raise ValueError("QBU_WATCH_REARM_TEST_ONLY_NO_TRADING")
    if history_complete is not True:
        raise ValueError("QBU_WATCH_REARM_HISTORY_COVERAGE_INCOMPLETE")
    if type(information_cutoff) is not int or information_cutoff < 0:
        raise ValueError("QBU_WATCH_REARM_INVALID_CUTOFF")
    if type(events) is not tuple or any(not isinstance(ev, InteractionEvent) for ev in events):
        raise ValueError("QBU_WATCH_REARM_ORIGINAL_EVENTS_REQUIRED")
    if type(episodes) is not tuple or any(not isinstance(ep, AnchorEpisode) for ep in episodes):
        raise ValueError("QBU_WATCH_REARM_ORIGINAL_EPISODES_REQUIRED")

    by_event = {}
    for ev in events:
        old = by_event.get(ev.event_id)
        if old is not None and old != ev:
            raise ValueError("QBU_WATCH_REARM_DIVERGENT_EVENT:" + ev.event_id)
        if (
            (ev.started_at is not None and ev.started_at > information_cutoff)
            or (ev.resolved_at is not None and ev.resolved_at > information_cutoff)
            or (ev.armed_at is not None and ev.armed_at > information_cutoff)
        ):
            raise ValueError("QBU_WATCH_REARM_FUTURE_EVENT:" + ev.event_id)
        by_event[ev.event_id] = ev
    by_episode = {}
    by_member = {}
    for ep in episodes:
        prior = by_episode.get(ep.anchor_episode_id)
        if prior is not None and prior != ep:
            raise ValueError("QBU_WATCH_REARM_DIVERGENT_EPISODE:" + ep.anchor_episode_id)
        if ep.started_at > information_cutoff:
            raise ValueError("QBU_WATCH_REARM_FUTURE_EPISODE:" + ep.anchor_episode_id)
        if ep.ended_at is not None and ep.ended_at > information_cutoff:
            raise ValueError("QBU_WATCH_REARM_FUTURE_EPISODE_END:" + ep.anchor_episode_id)
        by_episode[ep.anchor_episode_id] = ep
        if len(ep.interaction_event_ids) != len(set(ep.interaction_event_ids)):
            raise ValueError("QBU_WATCH_REARM_DUPLICATE_EPISODE_MEMBER:" + ep.anchor_episode_id)
        for event_id in ep.interaction_event_ids:
            by_member.setdefault(event_id, set()).add(ep.anchor_episode_id)

    projected = []
    projected_watch_ids = []
    rejected = []
    for ev in events:
        if not ev.event_id.startswith("D3-WATCH-REARM:"):
            projected.append(ev)
            continue
        if ev.anchor_episode_id is not None:
            projected.append(ev)
            continue
        holders = by_member.get(ev.event_id, set())
        if not holders:
            projected.append(ev)
            rejected.append((ev.event_id, "NOT_ORIGINAL_EPISODE_MEMBER"))
            continue
        if len(holders) != 1:
            raise ValueError("QBU_WATCH_REARM_AMBIGUOUS_MEMBER:" + ev.event_id)
        ep_id = next(iter(holders))
        ep = by_episode[ep_id]
        if ep.validity is AnchorValidity.TERMINATED or ep.terminal_true_break:
            projected.append(ev)
            rejected.append((ev.event_id, "TERMINATED_OR_TRUE_BREAK_EPISODE"))
            continue
        if (
            ep.candidate_id != ev.candidate_id
            or ep.target_trend_episode_id != ev.target_trend_episode_id
            or ep.target_direction is not ev.target_direction
            or ep.started_at > (ev.armed_at if ev.armed_at is not None else -1)
        ):
            raise ValueError("QBU_WATCH_REARM_EPISODE_LINEAGE_MISMATCH:" + ev.event_id)
        if not (
            ev.control is InteractionControl.ARMED
            and ev.resolution is InteractionResolution.UNRESOLVED
            and ev.started_at is None
            and ev.resolved_at is None
            and ev.armed_at is not None
            and ev.armed_at <= information_cutoff
            and ev.event_reference_boundary is None
            and ev.event_reference_scale is None
            and ev.terminal is False
            and ev.provenance.get("rearm") == "MATERIAL_CORRECT_SIDE_SEPARATION"
        ):
            raise ValueError("QBU_WATCH_REARM_INVALID_ORIGINAL_NONCONTACT_STATE:" + ev.event_id)
        parent_id = ev.provenance.get("prior_event_id")
        parent = by_event.get(parent_id)
        if (
            parent is None
            or parent.control is not InteractionControl.RESOLVED
            or parent.resolved_at is None
            or parent.resolved_at >= ev.armed_at
            or parent.target_trend_episode_id != ev.target_trend_episode_id
            or parent.target_direction is not ev.target_direction
            or parent.candidate_id != ev.candidate_id
            or parent_id not in ep.interaction_event_ids
        ):
            raise ValueError("QBU_WATCH_REARM_INVALID_PREDECESSOR:" + ev.event_id)
        exact_id = deterministic_id(
            "D3-WATCH-REARM", ev.candidate_id, parent_id, str(ev.armed_at)
        )
        if exact_id != ev.event_id:
            raise ValueError("QBU_WATCH_REARM_NONORIGINAL_EVENT_ID:" + ev.event_id)
        bound = bind_event_to_episode(ev, ep)
        # Verify source-only reciprocal field, no simulated interaction.
        if bound != replace(ev, anchor_episode_id=ep_id):
            raise ValueError("QBU_WATCH_REARM_NONRECIPROCAL_MUTATION:" + ev.event_id)
        projected.append(bound)
        projected_watch_ids.append(ev.event_id)
    return {
        "events": tuple(projected),
        "projected_watch_rearm_event_ids": tuple(sorted(set(projected_watch_ids))),
        "unprojected": tuple(rejected),
        "source_mode": "SYNTHETIC_ORIGINAL_EPISODE_MEMBERSHIP_ONLY",
        "input_event_count": len(events),
        "stage_only": True,
        "entry_ready": False,
        "orders": 0,
    }
