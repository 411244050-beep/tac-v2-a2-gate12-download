"""QBU original D3 event-to-Anchor membership view, isolated TEST_ONLY.

ENGINEERING INPUT-PROJECTION EXPERIMENT ONLY. Read original D3 event and
AnchorEpisode records as they existed at this cutoff; do NOT fabricate a
missing event, alter frozen D3 scientific functions, or write to the D3 ledger.

This view binds an existing event's missing reciprocal Anchor ID ONLY if
original D3 already attached that same event ID to exactly one valid episode
and all original candidate/trend/direction invariants are exact. It does not
create new membership or make a WATCH/REARM into an eligible negotiation.

Caller must supply genuine as-of-cutoff original-source records with complete
coverage. This helper alone cannot certify historic coverage, atomic
persistence, or current Binance main-loop acceptance.
"""


def _tac_qbu_anchor_membership_view_test_only_v1(
    *,
    events,
    episodes,
    information_cutoff,
    history_complete,
):
    if TAC_LIVE_ENABLED != 0:
        raise ValueError("QBU_ANCHOR_BINDING_TEST_ONLY")
    if history_complete is not True:
        raise ValueError("QBU_ANCHOR_SOURCE_HISTORY_INCOMPLETE")
    if type(information_cutoff) is not int or information_cutoff < 0:
        raise ValueError("QBU_ANCHOR_INVALID_CUTOFF")
    if type(events) is not tuple or any(not isinstance(e, InteractionEvent) for e in events):
        raise ValueError("QBU_ANCHOR_ORIGINAL_EVENT_SCHEMA_REQUIRED")
    if type(episodes) is not tuple or any(not isinstance(ep, AnchorEpisode) for ep in episodes):
        raise ValueError("QBU_ANCHOR_ORIGINAL_EPISODE_SCHEMA_REQUIRED")
    event_map = {}
    for ev in events:
        previous = event_map.get(ev.event_id)
        if previous is not None and previous != ev:
            raise ValueError("QBU_ANCHOR_DIVERGENT_EVENT_ID:" + ev.event_id)
        if ev.started_at is not None and ev.started_at > information_cutoff:
            raise ValueError("QBU_ANCHOR_FUTURE_EVENT_START:" + ev.event_id)
        if ev.resolved_at is not None and ev.resolved_at > information_cutoff:
            raise ValueError("QBU_ANCHOR_FUTURE_EVENT_RESOLUTION:" + ev.event_id)
        event_map[ev.event_id] = ev
    episode_map = {}
    memberships = {}
    for ep in episodes:
        prior = episode_map.get(ep.anchor_episode_id)
        if prior is not None and prior != ep:
            raise ValueError("QBU_ANCHOR_DIVERGENT_EPISODE_ID:" + ep.anchor_episode_id)
        if ep.started_at > information_cutoff:
            raise ValueError("QBU_ANCHOR_FUTURE_EPISODE:" + ep.anchor_episode_id)
        if ep.ended_at is not None and ep.ended_at > information_cutoff:
            raise ValueError("QBU_ANCHOR_FUTURE_EPISODE_TERMINATION:" + ep.anchor_episode_id)
        episode_map[ep.anchor_episode_id] = ep
        if len(set(ep.interaction_event_ids)) != len(ep.interaction_event_ids):
            raise ValueError("QBU_ANCHOR_DUPLICATE_EPISODE_MEMBERSHIP:" + ep.anchor_episode_id)
        for member in ep.interaction_event_ids:
            memberships.setdefault(member, set()).add(ep.anchor_episode_id)

    out = []
    bound_ids = []
    excluded_ids = []
    for ev in events:
        # WATCH / WATCH-REARM without an original active TEST is never
        # turned into a QBU-eligible negotiated interaction.
        if ev.started_at is None:
            out.append(ev)
            excluded_ids.append(ev.event_id)
            continue
        holders = memberships.get(ev.event_id, set())
        if len(holders) > 1:
            raise ValueError("QBU_ANCHOR_MULTIPLE_EPISODES_FOR_EVENT:" + ev.event_id)
        if not holders:
            out.append(ev)
            excluded_ids.append(ev.event_id)
            continue
        ep_id = next(iter(holders))
        ep = episode_map[ep_id]
        if (
            ep.candidate_id != ev.candidate_id
            or ep.target_trend_episode_id != ev.target_trend_episode_id
            or ep.target_direction is not ev.target_direction
        ):
            raise ValueError("QBU_ANCHOR_EPISODE_EVENT_LINEAGE_MISMATCH:" + ev.event_id)
        if ep.validity is AnchorValidity.TERMINATED or ep.terminal_true_break:
            out.append(ev)
            excluded_ids.append(ev.event_id)
            continue
        if ev.anchor_episode_id is not None and ev.anchor_episode_id != ep_id:
            raise ValueError("QBU_ANCHOR_EXISTING_EVENT_EPISODE_CONFLICT:" + ev.event_id)
        if ev.anchor_episode_id is None:
            # The original, unmodified frozen callable is the sole creator
            # of the projected reciprocal link. No new QBU/Role is created.
            projected = bind_event_to_episode(ev, ep)
            if projected.event_id != ev.event_id or projected.candidate_id != ev.candidate_id:
                raise ValueError("QBU_ANCHOR_ORIGINAL_BIND_EVENT_IDENTITY_CHANGED")
            out.append(projected)
            bound_ids.append(ev.event_id)
        else:
            out.append(ev)
    return {
        "events": tuple(out),
        "bound_event_ids": tuple(sorted(set(bound_ids))),
        "not_projected_event_ids": tuple(sorted(set(excluded_ids))),
        "input_event_count": len(events),
        "distinct_event_ids": len(event_map),
        "episode_count": len(episode_map),
        "source_mode": "SYNTHETIC_TEST_ONLY_ORIGINAL_HISTORY",
        "entry_ready": False,
        "orders": 0,
    }
