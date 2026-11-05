from __future__ import annotations

"""Pure pre-UPDATE-008 QBU SAME_EVENT negotiation-identity production mapper V1.

Implements only the frozen semantic:
QBU_SAME_EVENT_NEGOTIATION_IDENTITY_SOURCE_ASSOCIATION_V1 /
N6_EVENT_TIME_PRICE_AND_INTERACTION_TIME_CONNECTED_COMPONENT.

No D4 market-event/Opportunity identity, outcome, PnL, market I/O or trading
surface is imported or consumed.
"""

from dataclasses import dataclass, field, replace
from fractions import Fraction
from types import MappingProxyType
from typing import Mapping

import authoritative_d3_b5_d4_base_runtime_producers_v1 as runtime

from strategy_rc1.d2_market_state.types import TrendDirection
from strategy_rc1.d3_boundary_intelligence.types import (
    AnchorEpisode,
    BreakState,
    InteractionEvent,
    InteractionResolution,
)
from strategy_rc1.ids import deterministic_id


PRODUCER_ID = "QBU_SAME_EVENT_NEGOTIATION_IDENTITY_PRODUCTION_BINDING_V1"
SEMANTIC_ID = "QBU_SAME_EVENT_NEGOTIATION_IDENTITY_SOURCE_ASSOCIATION_V1"
SEMANTIC_CONTRACT_BLOB = "b6071576c708fc7b713e377ffdb9af4a0db9de8e"
SEMANTIC_FREEZE_MANIFEST_BLOB = "210c2315ce618a17a83445a036e5aeb9cf49171b"
RUNTIME_PRODUCER_BLOB = "97a02f5584c1446ca5ae016bad383e3ed0e18bb5"

STATUS_KNOWN = "KNOWN"
STATUS_UNKNOWN = "UNKNOWN"
STATUS_CONFLICT = "CONFLICT"


class NegotiationIdentityBlock(RuntimeError):
    pass


class NegotiationIdentityConflict(NegotiationIdentityBlock):
    pass


@dataclass(frozen=True)
class NegotiationIdentityRequest:
    information_cutoff: int
    trend_episode_id: str
    direction: TrendDirection
    events: tuple[InteractionEvent, ...]
    episodes: tuple[AnchorEpisode, ...]
    continuity_by_candidate_id: Mapping[str, bool | None]
    theta_test: Fraction

    # Produced by replay/orchestration from the explicit frozen rearm transition.
    # Key = later member InteractionEvent.event_id after the rearmed cycle reaches
    # actual TEST/contact; value = prior resolved InteractionEvent.event_id.
    rearm_predecessor_by_event_id: Mapping[str, str] = field(default_factory=dict)

    # Completeness covers the canonical one-record-per-event InteractionEvent
    # ledger, AnchorEpisode membership and replay-derived rearm transition ledger
    # through information_cutoff.  It is engineering coverage, not strategy state.
    history_complete: bool = False
    provenance: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "continuity_by_candidate_id",
            MappingProxyType({str(k): v for k, v in self.continuity_by_candidate_id.items()}),
        )
        object.__setattr__(
            self,
            "rearm_predecessor_by_event_id",
            MappingProxyType({str(k): str(v) for k, v in self.rearm_predecessor_by_event_id.items()}),
        )
        object.__setattr__(
            self,
            "provenance",
            MappingProxyType({str(k): str(v) for k, v in self.provenance.items()}),
        )


@dataclass(frozen=True)
class NegotiationIdentityProjection:
    status: str
    negotiation_identity_by_event_id: Mapping[str, str]
    component_members: tuple[tuple[str, tuple[str, ...]], ...]
    unknown_refs: tuple[str, ...] = ()
    conflict_refs: tuple[str, ...] = ()
    reason: str | None = None
    provenance: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "negotiation_identity_by_event_id",
            MappingProxyType(dict(self.negotiation_identity_by_event_id)),
        )
        object.__setattr__(
            self,
            "provenance",
            MappingProxyType({str(k): str(v) for k, v in self.provenance.items()}),
        )


def _direction_value(direction: TrendDirection) -> str:
    return direction.value if hasattr(direction, "value") else str(direction)


def _event_zone(event: InteractionEvent, theta_test: Fraction) -> tuple[Fraction, Fraction]:
    boundary = event.event_reference_boundary
    scale = event.event_reference_scale
    if boundary is None or scale is None:
        raise NegotiationIdentityBlock("EVENT_REFERENCE_GEOMETRY_UNKNOWN:" + event.event_id)
    if scale <= 0:
        raise NegotiationIdentityConflict("EVENT_REFERENCE_SCALE_NONPOSITIVE:" + event.event_id)
    if event.target_direction is TrendDirection.LONG:
        return boundary, boundary + theta_test * scale
    if event.target_direction is TrendDirection.SHORT:
        return boundary - theta_test * scale, boundary
    raise NegotiationIdentityConflict("INVALID_DIRECTION:" + event.event_id)


def _price_overlap(a: tuple[Fraction, Fraction], b: tuple[Fraction, Fraction]) -> bool:
    return max(a[0], b[0]) <= min(a[1], b[1])


def _time_overlap(a: InteractionEvent, b: InteractionEvent) -> bool:
    assert a.started_at is not None and a.resolved_at is not None
    assert b.started_at is not None and b.resolved_at is not None
    return max(a.started_at, b.started_at) <= min(a.resolved_at, b.resolved_at)


def _same_record(a: InteractionEvent, b: InteractionEvent) -> bool:
    return a == b


def _target_episode_map(req: NegotiationIdentityRequest) -> dict[str, AnchorEpisode]:
    out: dict[str, AnchorEpisode] = {}
    for ep in req.episodes:
        if ep.target_trend_episode_id != req.trend_episode_id or ep.target_direction is not req.direction:
            continue
        if ep.anchor_episode_id in out and out[ep.anchor_episode_id] != ep:
            raise NegotiationIdentityConflict("DIVERGENT_ANCHOR_EPISODE:" + ep.anchor_episode_id)
        out[ep.anchor_episode_id] = ep
    return out


def _event_map(req: NegotiationIdentityRequest) -> tuple[dict[str, InteractionEvent], tuple[str, ...]]:
    by_id: dict[str, InteractionEvent] = {}
    conflicts: set[str] = set()
    for ev in req.events:
        old = by_id.get(ev.event_id)
        if old is not None and not _same_record(old, ev):
            conflicts.add(ev.event_id)
            continue
        by_id[ev.event_id] = ev
    return by_id, tuple(sorted(conflicts))


def _qbu_event_ids(episodes: Mapping[str, AnchorEpisode]) -> set[str]:
    out: set[str] = set()
    for ep in episodes.values():
        for use in ep.qualified_uses:
            out.add(use.negotiation_event_id)
    return out


def _candidate_target_event(
    ev: InteractionEvent,
    *,
    trend_episode_id: str,
    direction: TrendDirection,
) -> bool:
    return ev.target_trend_episode_id == trend_episode_id and ev.target_direction is direction


def _eligibility(
    req: NegotiationIdentityRequest,
    ev: InteractionEvent,
    *,
    episode_map: Mapping[str, AnchorEpisode],
    qbu_event_ids: set[str],
) -> tuple[str, bool, str | None]:
    """Return (status, eligible, ref).

    Non-QBU records that are authoritatively outside the frozen eligible domain
    are excluded rather than converted into conflicts.  Existing QBU-bearing
    records must satisfy every non-missing invariant or fail closed.
    """
    qbu_bearing = ev.event_id in qbu_event_ids

    if not _candidate_target_event(ev, trend_episode_id=req.trend_episode_id, direction=req.direction):
        if qbu_bearing:
            return STATUS_CONFLICT, False, "QBU_TARGET_MISMATCH:" + ev.event_id
        return STATUS_KNOWN, False, None

    if ev.started_at is not None and ev.started_at > req.information_cutoff:
        return STATUS_CONFLICT, False, "FUTURE_EVENT_START:" + ev.event_id
    if ev.resolved_at is not None and ev.resolved_at > req.information_cutoff:
        return STATUS_CONFLICT, False, "FUTURE_EVENT_RESOLUTION:" + ev.event_id

    if ev.resolution is not InteractionResolution.RESOLVED_CORRECT_SIDE or ev.break_state is BreakState.TRUE_BREAK:
        if qbu_bearing:
            return STATUS_CONFLICT, False, "INVALID_QBU_EVENT_STATE:" + ev.event_id
        return STATUS_KNOWN, False, None

    if ev.started_at is None or ev.resolved_at is None:
        return STATUS_UNKNOWN, False, "EVENT_TIME_UNKNOWN:" + ev.event_id
    if ev.resolved_at < ev.started_at:
        return STATUS_CONFLICT, False, "EVENT_TIME_INVERTED:" + ev.event_id
    if ev.event_reference_boundary is None or ev.event_reference_scale is None:
        return STATUS_UNKNOWN, False, "EVENT_REFERENCE_UNKNOWN:" + ev.event_id
    if ev.event_reference_scale <= 0:
        return STATUS_CONFLICT, False, "EVENT_REFERENCE_SCALE_NONPOSITIVE:" + ev.event_id

    if ev.anchor_episode_id is None:
        return STATUS_UNKNOWN, False, "ANCHOR_EPISODE_UNKNOWN:" + ev.event_id
    ep = episode_map.get(ev.anchor_episode_id)
    if ep is None:
        return STATUS_CONFLICT if qbu_bearing else STATUS_UNKNOWN, False, "ANCHOR_EPISODE_MISSING:" + ev.event_id
    if (
        ep.target_trend_episode_id != ev.target_trend_episode_id
        or ep.target_direction is not ev.target_direction
        or ep.candidate_id != ev.candidate_id
        or ev.event_id not in set(ep.interaction_event_ids)
    ):
        return STATUS_CONFLICT, False, "EVENT_ANCHOR_LINEAGE_MISMATCH:" + ev.event_id

    continuity = req.continuity_by_candidate_id.get(ev.candidate_id)
    if continuity is None:
        return STATUS_UNKNOWN, False, "CONTINUITY_UNKNOWN:" + ev.event_id
    if continuity is False:
        if qbu_bearing:
            return STATUS_CONFLICT, False, "QBU_CONTINUITY_FALSE:" + ev.event_id
        return STATUS_KNOWN, False, None

    return STATUS_KNOWN, True, None


def _same_negotiation_edge(
    req: NegotiationIdentityRequest,
    a: InteractionEvent,
    b: InteractionEvent,
) -> bool:
    if a.target_trend_episode_id != b.target_trend_episode_id:
        return False
    if a.target_direction is not b.target_direction:
        return False
    if req.continuity_by_candidate_id.get(a.candidate_id) is not True:
        return False
    if req.continuity_by_candidate_id.get(b.candidate_id) is not True:
        return False
    return _price_overlap(_event_zone(a, req.theta_test), _event_zone(b, req.theta_test)) and _time_overlap(a, b)


def _canonical_identity(
    trend_episode_id: str,
    direction: TrendDirection,
    members: tuple[InteractionEvent, ...],
) -> str:
    root_cutoff = min(ev.started_at for ev in members if ev.started_at is not None)
    root_event_ids = tuple(sorted(ev.event_id for ev in members if ev.started_at == root_cutoff))
    return deterministic_id(
        "QBU-NEGOTIATION-V1",
        trend_episode_id,
        _direction_value(direction),
        str(root_cutoff),
        "|".join(root_event_ids),
    )


def _ancestor_pairs(req: NegotiationIdentityRequest) -> tuple[tuple[str, str], ...]:
    pred = dict(req.rearm_predecessor_by_event_id)
    pairs: set[tuple[str, str]] = set()
    for child in sorted(pred):
        seen: set[str] = set()
        cur = child
        while cur in pred:
            if cur in seen:
                raise NegotiationIdentityConflict("REARM_PREDECESSOR_CYCLE:" + child)
            seen.add(cur)
            parent = pred[cur]
            if not parent:
                raise NegotiationIdentityConflict("EMPTY_REARM_PREDECESSOR:" + child)
            pairs.add((child, parent))
            cur = parent
    return tuple(sorted(pairs))


def project_negotiation_identity(
    req: NegotiationIdentityRequest,
) -> NegotiationIdentityProjection:
    if not isinstance(req, NegotiationIdentityRequest):
        raise NegotiationIdentityConflict("REQUEST_SCHEMA")
    if req.information_cutoff < 0:
        raise NegotiationIdentityConflict("INVALID_INFORMATION_CUTOFF")
    if not req.trend_episode_id:
        raise NegotiationIdentityConflict("TREND_EPISODE_ID_REQUIRED")
    if req.direction not in (TrendDirection.LONG, TrendDirection.SHORT):
        raise NegotiationIdentityConflict("DIRECTION_REQUIRED")
    if req.theta_test <= 0:
        raise NegotiationIdentityConflict("THETA_TEST_MUST_BE_POSITIVE_FROZEN_INPUT")

    if not req.history_complete:
        return NegotiationIdentityProjection(
            status=STATUS_UNKNOWN,
            negotiation_identity_by_event_id={},
            component_members=(),
            unknown_refs=("INTERACTION_HISTORY_COVERAGE_INCOMPLETE",),
            reason="INTERACTION_HISTORY_COVERAGE_INCOMPLETE",
            provenance={
                "producer_id": PRODUCER_ID,
                "semantic_id": SEMANTIC_ID,
                "scientific_state_mutated": "false",
            },
        )

    try:
        episodes = _target_episode_map(req)
        events, duplicate_conflicts = _event_map(req)
    except NegotiationIdentityConflict as exc:
        return NegotiationIdentityProjection(
            status=STATUS_CONFLICT,
            negotiation_identity_by_event_id={},
            component_members=(),
            conflict_refs=(str(exc),),
            reason=str(exc),
            provenance={"producer_id": PRODUCER_ID, "semantic_id": SEMANTIC_ID},
        )

    if duplicate_conflicts:
        return NegotiationIdentityProjection(
            status=STATUS_CONFLICT,
            negotiation_identity_by_event_id={},
            component_members=(),
            conflict_refs=tuple("DIVERGENT_EVENT_RECORD:" + x for x in duplicate_conflicts),
            reason="DIVERGENT_EVENT_RECORDS",
            provenance={"producer_id": PRODUCER_ID, "semantic_id": SEMANTIC_ID},
        )

    qbu_ids = _qbu_event_ids(episodes)

    # Target AnchorEpisode history is an authoritative ledger. Missing member
    # InteractionEvent records mean connected-component history may be incomplete.
    missing_refs: set[str] = set()
    for ep in episodes.values():
        for event_id in ep.interaction_event_ids:
            if event_id not in events:
                missing_refs.add(event_id)
    missing_refs.update(event_id for event_id in qbu_ids if event_id not in events)
    if missing_refs:
        return NegotiationIdentityProjection(
            status=STATUS_UNKNOWN,
            negotiation_identity_by_event_id={},
            component_members=(),
            unknown_refs=tuple(sorted("MISSING_EVENT:" + x for x in missing_refs)),
            reason="REFERENCED_INTERACTION_EVENT_MISSING",
            provenance={"producer_id": PRODUCER_ID, "semantic_id": SEMANTIC_ID},
        )

    eligible: list[InteractionEvent] = []
    unknown: set[str] = set()
    conflict: set[str] = set()

    for ev in events.values():
        status, ok, ref = _eligibility(req, ev, episode_map=episodes, qbu_event_ids=qbu_ids)
        if status == STATUS_UNKNOWN and ref:
            unknown.add(ref)
        elif status == STATUS_CONFLICT and ref:
            conflict.add(ref)
        elif ok:
            eligible.append(ev)

    if conflict:
        return NegotiationIdentityProjection(
            status=STATUS_CONFLICT,
            negotiation_identity_by_event_id={},
            component_members=(),
            conflict_refs=tuple(sorted(conflict)),
            reason="ELIGIBILITY_CONFLICT",
            provenance={"producer_id": PRODUCER_ID, "semantic_id": SEMANTIC_ID},
        )
    if unknown:
        return NegotiationIdentityProjection(
            status=STATUS_UNKNOWN,
            negotiation_identity_by_event_id={},
            component_members=(),
            unknown_refs=tuple(sorted(unknown)),
            reason="ELIGIBILITY_UNKNOWN",
            provenance={"producer_id": PRODUCER_ID, "semantic_id": SEMANTIC_ID},
        )

    # If an existing QBU refers to no eligible node, fail closed rather than
    # inventing/falling back to member event identity.
    eligible_ids = {ev.event_id for ev in eligible}
    noneligible_qbu = sorted(qbu_ids - eligible_ids)
    if noneligible_qbu:
        return NegotiationIdentityProjection(
            status=STATUS_CONFLICT,
            negotiation_identity_by_event_id={},
            component_members=(),
            conflict_refs=tuple("QBU_EVENT_NOT_ELIGIBLE:" + x for x in noneligible_qbu),
            reason="QBU_EVENT_NOT_ELIGIBLE",
            provenance={"producer_id": PRODUCER_ID, "semantic_id": SEMANTIC_ID},
        )

    parent = {ev.event_id: ev.event_id for ev in eligible}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    eligible_sorted = tuple(sorted(eligible, key=lambda e: e.event_id))
    for i, a in enumerate(eligible_sorted):
        for b in eligible_sorted[i + 1 :]:
            if _same_negotiation_edge(req, a, b):
                union(a.event_id, b.event_id)

    components_by_root: dict[str, list[InteractionEvent]] = {}
    for ev in eligible_sorted:
        components_by_root.setdefault(find(ev.event_id), []).append(ev)

    # Explicit rearm ancestry is a distinct-cycle boundary. Any connected
    # component that crosses such a boundary contradicts the frozen semantic.
    try:
        ancestor_pairs = _ancestor_pairs(req)
    except NegotiationIdentityConflict as exc:
        return NegotiationIdentityProjection(
            status=STATUS_CONFLICT,
            negotiation_identity_by_event_id={},
            component_members=(),
            conflict_refs=(str(exc),),
            reason="REARM_LINEAGE_CONFLICT",
            provenance={"producer_id": PRODUCER_ID, "semantic_id": SEMANTIC_ID},
        )

    for child, ancestor in ancestor_pairs:
        if child in parent and ancestor in parent and find(child) == find(ancestor):
            return NegotiationIdentityProjection(
                status=STATUS_CONFLICT,
                negotiation_identity_by_event_id={},
                component_members=(),
                conflict_refs=("REARM_BOUNDARY_SAME_COMPONENT:" + child + ":" + ancestor,),
                reason="REARM_BOUNDARY_SAME_COMPONENT",
                provenance={"producer_id": PRODUCER_ID, "semantic_id": SEMANTIC_ID},
            )

    mapping: dict[str, str] = {}
    component_rows: list[tuple[str, tuple[str, ...]]] = []
    for members_list in components_by_root.values():
        members = tuple(sorted(members_list, key=lambda e: e.event_id))
        identity = _canonical_identity(req.trend_episode_id, req.direction, members)
        member_ids = tuple(ev.event_id for ev in members)
        component_rows.append((identity, member_ids))
        for event_id in member_ids:
            mapping[event_id] = identity

    # Existing QBU-bearing events must always receive identity on KNOWN path.
    if not qbu_ids.issubset(mapping):
        missing = tuple(sorted(qbu_ids - set(mapping)))
        return NegotiationIdentityProjection(
            status=STATUS_CONFLICT,
            negotiation_identity_by_event_id={},
            component_members=(),
            conflict_refs=tuple("QBU_IDENTITY_MISSING:" + x for x in missing),
            reason="QBU_IDENTITY_MISSING",
            provenance={"producer_id": PRODUCER_ID, "semantic_id": SEMANTIC_ID},
        )

    return NegotiationIdentityProjection(
        status=STATUS_KNOWN,
        negotiation_identity_by_event_id=mapping,
        component_members=tuple(sorted(component_rows)),
        unknown_refs=(),
        conflict_refs=(),
        reason=None,
        provenance={
            "producer_id": PRODUCER_ID,
            "semantic_id": SEMANTIC_ID,
            "semantic_contract_blob": SEMANTIC_CONTRACT_BLOB,
            "semantic_freeze_manifest_blob": SEMANTIC_FREEZE_MANIFEST_BLOB,
            "runtime_producer_blob": RUNTIME_PRODUCER_BLOB,
            "f9_stage": "POST_UPDATE007_PRE_UPDATE008",
            "downstream_d4_identity_used": "false",
            "scientific_state_mutated": "false",
            "real_market_data_read": "false",
            "test_read": "false",
            "pnl": "false",
            "trading": "FORBIDDEN",
        },
    )


def bind_update008_request(
    request: runtime.Update008Request,
    projection: NegotiationIdentityProjection,
) -> runtime.Update008Request:
    """Bind frozen negotiation identity directly into the existing request.

    Caller prepopulation is forbidden so that production identity cannot be
    silently overridden or mixed with a guessed mapping.
    """
    if not isinstance(request, runtime.Update008Request):
        raise NegotiationIdentityConflict("UPDATE008_REQUEST_SCHEMA")
    if request.negotiation_identity_by_event_id:
        raise NegotiationIdentityConflict("CALLER_PREPOPULATED_NEGOTIATION_IDENTITY_FORBIDDEN")
    if projection.status != STATUS_KNOWN:
        raise NegotiationIdentityBlock("KNOWN_NEGOTIATION_IDENTITY_PROJECTION_REQUIRED")
    return replace(
        request,
        negotiation_identity_by_event_id=dict(projection.negotiation_identity_by_event_id),
        provenance={
            **dict(request.provenance),
            "negotiation_identity_producer_id": PRODUCER_ID,
            "negotiation_identity_semantic_id": SEMANTIC_ID,
        },
    )
