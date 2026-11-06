from __future__ import annotations

"""Production binding for the frozen FailedReexpansionEvent source semantic V1.

This module implements only the already-frozen causal source association around
strategy_rc1.d2_market_state.platform.update_platform().  It adds no new
threshold, time window, strategy state, or mechanism selector.
"""

from dataclasses import dataclass, field
from fractions import Fraction
from types import MappingProxyType
from typing import Any, Mapping

import authoritative_d3_b5_d4_base_runtime_producers_v1 as b5prod

from d2_to_b4_d4_causal_evidence_producers_v1 import EvidenceState
from strategy_rc1.d2_market_state.platform import EMPTY_PLATFORM, update_platform
from strategy_rc1.d2_market_state.progress import same_type_progress
from strategy_rc1.d2_market_state.types import (
    FailedReexpansionEvent,
    PivotType,
    PlatformState,
    PlatformStatus,
    ProgressRelation,
    StructuralLayer,
    StructuralPivot,
    TrendDirection,
    TrendEpisodeState,
    TrendIntegrity,
)
from strategy_rc1.d3_boundary_intelligence.types import (
    AnchorEpisode,
    BreakState,
    InteractionControl,
    InteractionEvent,
    InteractionResolution,
)
from strategy_rc1.runtime_guards.information_state import InfoKind, InfoValue


PRODUCER_ID = "PLATFORM_FAILED_REEXPANSION_EVENT_AND_STATE_PRODUCTION_BINDING_V1"
SEMANTIC_ID = "PLATFORM_FAILED_REEXPANSION_SOURCE_ASSOCIATION_V1"
SEMANTIC_CONTRACT_BLOB = "a1a003665ea3acf48a62db85903e033c7fc78e5b"
SEMANTIC_FREEZE_MANIFEST_BLOB = "7a7a8bed6ccea6afc3320efe861708a3ebb4fdd9"
FROZEN_RUNTIME_CONSUMER_BLOB = "97a02f5584c1446ca5ae016bad383e3ed0e18bb5"
D4_LINEAGE_V2_BLOB = "f334155bbb46ec2ff0ee748555cb15c1485d3036"
OBSERVER_TIMEFRAME_MS = 15 * 60 * 1000
REARM_PROVENANCE = "MATERIAL_CORRECT_SIDE_SEPARATION"


class PlatformProductionBlock(RuntimeError):
    pass


class PlatformProductionConflict(PlatformProductionBlock):
    pass


@dataclass(frozen=True)
class PlatformProductionRequest:
    information_cutoff: int
    symbol: str
    trend_episode_id: str
    direction: TrendDirection
    trend_state: TrendEpisodeState
    all_minor: tuple[StructuralPivot, ...]
    events: tuple[InteractionEvent, ...]
    episodes: tuple[AnchorEpisode, ...]
    canonical_segment_id_by_anchor_episode_id: Mapping[str, str]
    continuity_by_candidate_id: Mapping[str, bool | None]
    rearm_predecessor_by_event_id: Mapping[str, str]
    rearm_cutoff_by_event_id: Mapping[str, int]
    canonical_continuity: bool | None
    atr14_at_confirmation: InfoValue[Fraction]
    theta_progress: Fraction
    theta_progress_parameter_ref: str
    history_complete: bool
    history_coverage_ref: str
    current_close: Fraction
    setup_lineage: tuple[str, ...] = ()
    provenance: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "canonical_segment_id_by_anchor_episode_id",
            "continuity_by_candidate_id",
            "rearm_predecessor_by_event_id",
            "rearm_cutoff_by_event_id",
            "provenance",
        ):
            value = getattr(self, name)
            object.__setattr__(self, name, MappingProxyType(dict(value)))


@dataclass(frozen=True)
class PlatformLineageMemory:
    trend_episode_id: str
    direction: TrendDirection
    canonical_segment_id: str | None
    platform: PlatformState
    candidate_source_event_id: str | None
    candidate_pivot_id: str | None
    source_pivot_by_event_id: tuple[tuple[str, str], ...]
    last_evaluated_cutoff: int


@dataclass(frozen=True)
class PlatformProductionProjection:
    state: EvidenceState
    platform: PlatformState
    failed_event: FailedReexpansionEvent | None
    platform_reexpansion_evidence: Any | None
    source_interaction_id: str | None
    source_pivot_id: str | None
    reset_reason: str | None
    unknown_refs: tuple[str, ...] = ()
    conflict_refs: tuple[str, ...] = ()
    provenance: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "provenance",
            MappingProxyType({str(k): str(v) for k, v in self.provenance.items()}),
        )


def _prov(req: PlatformProductionRequest, **extra: str) -> dict[str, str]:
    return {
        "producer_id": PRODUCER_ID,
        "semantic_id": SEMANTIC_ID,
        "semantic_contract_blob": SEMANTIC_CONTRACT_BLOB,
        "semantic_freeze_manifest_blob": SEMANTIC_FREEZE_MANIFEST_BLOB,
        "history_coverage_ref": req.history_coverage_ref,
        "theta_progress_parameter_ref": req.theta_progress_parameter_ref,
        "information_cutoff": str(req.information_cutoff),
        "scientific_state_machine_added": "false",
        "frozen_update_platform_modified": "false",
        **{str(k): str(v) for k, v in req.provenance.items()},
        **extra,
    }


def _projection(
    req: PlatformProductionRequest,
    *,
    state: EvidenceState,
    platform: PlatformState,
    failed_event: FailedReexpansionEvent | None = None,
    d4_evidence: Any | None = None,
    source_interaction_id: str | None = None,
    source_pivot_id: str | None = None,
    reset_reason: str | None = None,
    unknown_refs: tuple[str, ...] = (),
    conflict_refs: tuple[str, ...] = (),
    reason: str,
) -> PlatformProductionProjection:
    return PlatformProductionProjection(
        state=state,
        platform=platform,
        failed_event=failed_event,
        platform_reexpansion_evidence=d4_evidence,
        source_interaction_id=source_interaction_id,
        source_pivot_id=source_pivot_id,
        reset_reason=reset_reason,
        unknown_refs=tuple(sorted(set(unknown_refs))),
        conflict_refs=tuple(sorted(set(conflict_refs))),
        provenance=_prov(req, reason=reason),
    )


def _trend_side_type(direction: TrendDirection) -> PivotType:
    if direction is TrendDirection.LONG:
        return PivotType.HIGH
    if direction is TrendDirection.SHORT:
        return PivotType.LOW
    raise PlatformProductionConflict("INVALID_DIRECTION")


def _successful_relation(direction: TrendDirection) -> ProgressRelation:
    if direction is TrendDirection.LONG:
        return ProgressRelation.MATERIAL_ADVANCE_UP
    if direction is TrendDirection.SHORT:
        return ProgressRelation.MATERIAL_ADVANCE_DOWN
    raise PlatformProductionConflict("INVALID_DIRECTION")


def _canonical_events(events: tuple[InteractionEvent, ...]) -> dict[str, InteractionEvent]:
    out: dict[str, InteractionEvent] = {}
    for ev in events:
        old = out.get(ev.event_id)
        if old is not None and old != ev:
            raise PlatformProductionConflict("DIVERGENT_EVENT_RECORD:" + ev.event_id)
        out[ev.event_id] = ev
    return out


def _canonical_episodes(episodes: tuple[AnchorEpisode, ...]) -> dict[str, AnchorEpisode]:
    out: dict[str, AnchorEpisode] = {}
    for ep in episodes:
        old = out.get(ep.anchor_episode_id)
        if old is not None and old != ep:
            raise PlatformProductionConflict("DIVERGENT_ANCHOR_EPISODE:" + ep.anchor_episode_id)
        out[ep.anchor_episode_id] = ep
    return out


def _canonical_pivots(pivots: tuple[StructuralPivot, ...]) -> dict[str, StructuralPivot]:
    out: dict[str, StructuralPivot] = {}
    for p in pivots:
        old = out.get(p.pivot_id)
        if old is not None and old != p:
            raise PlatformProductionConflict("DIVERGENT_PIVOT_RECORD:" + p.pivot_id)
        out[p.pivot_id] = p
    return out


def _target_event(
    req: PlatformProductionRequest,
    ev: InteractionEvent,
    episode_map: Mapping[str, AnchorEpisode],
) -> tuple[str, str | None]:
    if ev.target_trend_episode_id != req.trend_episode_id or ev.target_direction is not req.direction:
        return "OUTSIDE", None
    if ev.resolved_at is not None and ev.resolved_at > req.information_cutoff:
        raise PlatformProductionConflict("FUTURE_EVENT_RESOLUTION:" + ev.event_id)
    if (
        ev.control is not InteractionControl.RESOLVED
        or ev.resolution is not InteractionResolution.RESOLVED_CORRECT_SIDE
        or ev.break_state is BreakState.TRUE_BREAK
    ):
        return "OUTSIDE", None
    if ev.resolved_at is None:
        return "UNKNOWN", "EVENT_RESOLUTION_UNKNOWN:" + ev.event_id
    if ev.anchor_episode_id is None:
        return "UNKNOWN", "ANCHOR_EPISODE_UNKNOWN:" + ev.event_id
    ep = episode_map.get(ev.anchor_episode_id)
    if ep is None:
        return "UNKNOWN", "ANCHOR_EPISODE_MISSING:" + ev.event_id
    if (
        ep.candidate_id != ev.candidate_id
        or ep.target_trend_episode_id != ev.target_trend_episode_id
        or ep.target_direction is not ev.target_direction
        or ev.event_id not in set(ep.interaction_event_ids)
    ):
        raise PlatformProductionConflict("EVENT_ANCHOR_LINEAGE_MISMATCH:" + ev.event_id)
    continuity = req.continuity_by_candidate_id.get(ev.candidate_id)
    if continuity is None:
        return "UNKNOWN", "CANDIDATE_CONTINUITY_UNKNOWN:" + ev.candidate_id
    if continuity is False:
        raise PlatformProductionConflict("CANDIDATE_CONTINUITY_FALSE:" + ev.candidate_id)
    segment = req.canonical_segment_id_by_anchor_episode_id.get(ev.anchor_episode_id)
    if not segment:
        return "UNKNOWN", "CANONICAL_SEGMENT_UNKNOWN:" + ev.anchor_episode_id
    return "KNOWN", segment


def _stream_for_segment(
    req: PlatformProductionRequest,
    pivot_map: Mapping[str, StructuralPivot],
    segment: str,
) -> tuple[StructuralPivot, ...]:
    start = req.trend_state.episode_start_cutoff
    if start is None:
        raise PlatformProductionBlock("TREND_EPISODE_START_UNKNOWN")
    ptype = _trend_side_type(req.direction)
    rows: list[StructuralPivot] = []
    for p in pivot_map.values():
        if p.symbol != req.symbol:
            continue
        if p.canonical_segment_id != segment:
            continue
        if p.confirmed_at < start:
            continue
        if p.confirmed_at > req.information_cutoff:
            raise PlatformProductionConflict("FUTURE_PIVOT:" + p.pivot_id)
        if p.timeframe_ms != OBSERVER_TIMEFRAME_MS:
            raise PlatformProductionConflict("PIVOT_TIMEFRAME_MISMATCH:" + p.pivot_id)
        if p.layer is not StructuralLayer.MINOR:
            raise PlatformProductionConflict("PIVOT_LAYER_MISMATCH:" + p.pivot_id)
        if p.pivot_type is ptype:
            rows.append(p)
    rows.sort(key=lambda x: (x.confirmed_at, x.extreme_first_time, x.extreme_last_time, x.pivot_id))
    # Equal confirmation cutoffs are not lexically selected.
    by_cutoff: dict[int, list[StructuralPivot]] = {}
    for p in rows:
        by_cutoff.setdefault(p.confirmed_at, []).append(p)
    for cutoff, same in by_cutoff.items():
        if len(same) > 1:
            raise PlatformProductionConflict("MULTIPLE_TREND_SIDE_PIVOTS_SAME_CUTOFF:" + str(cutoff))
    return tuple(rows)


def _first_post_resolution(
    stream: tuple[StructuralPivot, ...],
    ev: InteractionEvent,
) -> StructuralPivot | None:
    assert ev.resolved_at is not None
    eligible = tuple(
        p for p in stream
        if p.confirmed_at > ev.resolved_at and p.extreme_first_time >= ev.resolved_at
    )
    return eligible[0] if eligible else None


def _p0(stream: tuple[StructuralPivot, ...], p1: StructuralPivot) -> StructuralPivot | None:
    for i, p in enumerate(stream):
        if p.pivot_id == p1.pivot_id:
            return stream[i - 1] if i > 0 else None
    raise PlatformProductionConflict("P1_NOT_IN_CANONICAL_STREAM:" + p1.pivot_id)


def _structure_intact(req: PlatformProductionRequest) -> bool | None:
    state = req.trend_state
    if req.canonical_continuity is None:
        return None
    if req.canonical_continuity is False:
        return False
    if state.episode_id != req.trend_episode_id or state.direction is not req.direction:
        return False
    if state.integrity is TrendIntegrity.FAILED:
        return False
    if state.protected_pivot is None or state.integrity is None:
        return None
    return state.integrity in (
        TrendIntegrity.HEALTHY,
        TrendIntegrity.PRESSURED,
        TrendIntegrity.DETERIORATING,
    )


def _memory(
    req: PlatformProductionRequest,
    platform: PlatformState,
    *,
    segment: str | None,
    candidate_event: str | None,
    candidate_pivot: str | None,
    source_pairs: Mapping[str, str],
) -> PlatformLineageMemory:
    return PlatformLineageMemory(
        trend_episode_id=req.trend_episode_id,
        direction=req.direction,
        canonical_segment_id=segment,
        platform=platform,
        candidate_source_event_id=candidate_event,
        candidate_pivot_id=candidate_pivot,
        source_pivot_by_event_id=tuple(sorted((str(k), str(v)) for k, v in source_pairs.items())),
        last_evaluated_cutoff=req.information_cutoff,
    )


def _wire_if_confirmed(
    req: PlatformProductionRequest,
    platform: PlatformState,
) -> Any | None:
    if platform.status is not PlatformStatus.PLATFORM_CONFIRMED:
        return None
    return b5prod.wire_platform_reexpansion(
        platform,
        current_close=req.current_close,
        target_trend_episode_id=req.trend_episode_id,
        direction=req.direction,
        setup_lineage=tuple(req.setup_lineage),
    )


def project_platform_failed_reexpansion(
    req: PlatformProductionRequest,
    prior_memory: PlatformLineageMemory | None = None,
) -> tuple[PlatformProductionProjection, PlatformLineageMemory]:
    if req.theta_progress <= 0:
        raise PlatformProductionConflict("THETA_PROGRESS_NONPOSITIVE")
    if not req.history_complete:
        platform = prior_memory.platform if prior_memory is not None else EMPTY_PLATFORM
        memory = prior_memory or _memory(req, platform, segment=None, candidate_event=None, candidate_pivot=None, source_pairs={})
        return (
            _projection(
                req,state=EvidenceState.UNKNOWN,platform=platform,
                unknown_refs=(req.history_coverage_ref or "HISTORY_COVERAGE_MISSING",),
                reason="HISTORY_INCOMPLETE",
            ),
            memory,
        )
    if not req.history_coverage_ref:
        raise PlatformProductionBlock("HISTORY_COVERAGE_REF_REQUIRED")
    if not req.theta_progress_parameter_ref:
        raise PlatformProductionBlock("THETA_PROGRESS_PARAMETER_REF_REQUIRED")
    if req.direction not in (TrendDirection.LONG, TrendDirection.SHORT):
        raise PlatformProductionConflict("INVALID_DIRECTION")
    if req.trend_state.episode_id is not None and req.trend_state.episode_id != req.trend_episode_id:
        # Known replacement/terminal transition: candidate cannot carry.
        memory = _memory(req, EMPTY_PLATFORM, segment=None, candidate_event=None, candidate_pivot=None, source_pairs={})
        return (
            _projection(req,state=EvidenceState.FALSE,platform=EMPTY_PLATFORM,reset_reason="TREND_EPISODE_REPLACED",reason="TREND_EPISODE_REPLACED"),
            memory,
        )
    if prior_memory is not None:
        if prior_memory.trend_episode_id != req.trend_episode_id or prior_memory.direction is not req.direction:
            raise PlatformProductionConflict("MEMORY_TREND_LINEAGE_MISMATCH")
        if req.information_cutoff < prior_memory.last_evaluated_cutoff:
            raise PlatformProductionConflict("CUTOFF_REWIND")
        if req.information_cutoff == prior_memory.last_evaluated_cutoff:
            return (
                _projection(
                    req,state=EvidenceState.FALSE,platform=prior_memory.platform,
                    d4_evidence=_wire_if_confirmed(req, prior_memory.platform),
                    reset_reason=None,reason="CUTOFF_ALREADY_EVALUATED",
                ),
                prior_memory,
            )

    event_map = _canonical_events(req.events)
    episode_map = _canonical_episodes(req.episodes)
    pivot_map = _canonical_pivots(req.all_minor)
    platform = prior_memory.platform if prior_memory is not None else EMPTY_PLATFORM
    source_pairs = dict(prior_memory.source_pivot_by_event_id) if prior_memory is not None else {}
    candidate_event = prior_memory.candidate_source_event_id if prior_memory is not None else None
    candidate_pivot = prior_memory.candidate_pivot_id if prior_memory is not None else None
    candidate_segment = prior_memory.canonical_segment_id if prior_memory is not None else None

    intact = _structure_intact(req)
    if intact is None:
        memory = prior_memory or _memory(req, platform, segment=candidate_segment, candidate_event=candidate_event, candidate_pivot=candidate_pivot, source_pairs=source_pairs)
        return (
            _projection(req,state=EvidenceState.UNKNOWN,platform=platform,unknown_refs=("PROTECTED_STRUCTURE_UNKNOWN",),reason="PROTECTED_STRUCTURE_UNKNOWN"),
            memory,
        )
    if intact is False and platform.status is PlatformStatus.PLATFORM_CANDIDATE:
        platform = EMPTY_PLATFORM
        source_pairs = {}
        candidate_event = None
        candidate_pivot = None
        candidate_segment = None

    # Confirmed platform obeys frozen F6. Do not feed later events into a new state machine.
    if platform.status is PlatformStatus.PLATFORM_CONFIRMED:
        memory = _memory(req, platform, segment=candidate_segment, candidate_event=candidate_event, candidate_pivot=candidate_pivot, source_pairs=source_pairs)
        return (
            _projection(
                req,state=EvidenceState.FALSE,platform=platform,d4_evidence=_wire_if_confirmed(req,platform),
                reason="PLATFORM_ALREADY_CONFIRMED_F6",
            ),
            memory,
        )

    event_candidates: list[tuple[InteractionEvent, str, StructuralPivot, StructuralPivot, ProgressRelation]] = []
    unknown_refs: set[str] = set()

    for ev in event_map.values():
        status, info = _target_event(req, ev, episode_map)
        if status == "OUTSIDE":
            continue
        if status == "UNKNOWN":
            assert info is not None
            unknown_refs.add(info)
            continue
        assert info is not None
        segment = info
        stream = _stream_for_segment(req, pivot_map, segment)
        p1 = _first_post_resolution(stream, ev)
        if p1 is None or p1.confirmed_at != req.information_cutoff:
            continue
        p0 = _p0(stream, p1)
        if p0 is None:
            unknown_refs.add("NO_COMPARABLE_PREDECESSOR:" + p1.pivot_id)
            continue
        relation = same_type_progress(p0, p1, req.theta_progress)
        event_candidates.append((ev, segment, p0, p1, relation))

    if len(event_candidates) > 1:
        refs = tuple(sorted("InteractionEvent:" + x[0].event_id for x in event_candidates))
        memory = prior_memory or _memory(req, platform, segment=candidate_segment, candidate_event=candidate_event, candidate_pivot=candidate_pivot, source_pairs=source_pairs)
        return (
            _projection(
                req,state=EvidenceState.CONFLICT,platform=platform,
                conflict_refs=refs,reason="MULTIPLE_SOURCE_INTERACTIONS_OR_PLATFORM_BRANCHES_NO_WINNER",
            ),
            memory,
        )

    # Candidate reset is driven by any current same-segment materially successful
    # trend-side pivot, even when no InteractionEvent claims it.
    if platform.status is PlatformStatus.PLATFORM_CANDIDATE and candidate_segment is not None:
        stream = _stream_for_segment(req, pivot_map, candidate_segment)
        current = tuple(p for p in stream if p.confirmed_at == req.information_cutoff)
        if len(current) > 1:
            raise PlatformProductionConflict("MULTIPLE_CURRENT_TREND_SIDE_PIVOTS")
        if current:
            cp1 = current[0]
            cp0 = _p0(stream, cp1)
            if cp0 is None:
                unknown_refs.add("NO_COMPARABLE_PREDECESSOR:" + cp1.pivot_id)
            else:
                rel = same_type_progress(cp0, cp1, req.theta_progress)
                if rel is _successful_relation(req.direction):
                    memory = _memory(req, EMPTY_PLATFORM, segment=None, candidate_event=None, candidate_pivot=None, source_pairs={})
                    return (
                        _projection(
                            req,state=EvidenceState.FALSE,platform=EMPTY_PLATFORM,
                            source_pivot_id=cp1.pivot_id,
                            reset_reason="MATERIAL_SUCCESSFUL_REEXPANSION",
                            reason="PLATFORM_CANDIDATE_RESET_ON_SUCCESSFUL_REEXPANSION",
                        ),
                        memory,
                    )

    if not event_candidates:
        memory = _memory(req, platform, segment=candidate_segment, candidate_event=candidate_event, candidate_pivot=candidate_pivot, source_pairs=source_pairs)
        if unknown_refs:
            return (
                _projection(
                    req,state=EvidenceState.UNKNOWN,platform=platform,
                    unknown_refs=tuple(unknown_refs),reason="SOURCE_ASSOCIATION_INCOMPLETE",
                ),
                memory,
            )
        return (
            _projection(
                req,state=EvidenceState.FALSE,platform=platform,
                d4_evidence=_wire_if_confirmed(req,platform),
                reason="NO_FAILED_REEXPANSION_EVENT_AT_CUTOFF",
            ),
            memory,
        )

    ev, segment, p0, p1, relation = event_candidates[0]
    success = relation is _successful_relation(req.direction)
    if success:
        memory = _memory(req, EMPTY_PLATFORM if platform.status is PlatformStatus.PLATFORM_CANDIDATE else platform, segment=None if platform.status is PlatformStatus.PLATFORM_CANDIDATE else candidate_segment, candidate_event=None if platform.status is PlatformStatus.PLATFORM_CANDIDATE else candidate_event, candidate_pivot=None if platform.status is PlatformStatus.PLATFORM_CANDIDATE else candidate_pivot, source_pairs={} if platform.status is PlatformStatus.PLATFORM_CANDIDATE else source_pairs)
        return (
            _projection(
                req,state=EvidenceState.FALSE,platform=memory.platform,
                source_interaction_id=ev.event_id,source_pivot_id=p1.pivot_id,
                reset_reason="MATERIAL_SUCCESSFUL_REEXPANSION" if platform.status is PlatformStatus.PLATFORM_CANDIDATE else None,
                reason="SUCCESSFUL_REEXPANSION_NOT_FAILED_EVENT",
            ),
            memory,
        )

    independent = False
    rearmed = False
    if platform.status is PlatformStatus.PLATFORM_CANDIDATE:
        if candidate_event is None or candidate_pivot is None:
            raise PlatformProductionConflict("CANDIDATE_MEMORY_PROVENANCE_MISSING")
        if p0.pivot_id != candidate_pivot:
            memory = _memory(req, platform, segment=candidate_segment, candidate_event=candidate_event, candidate_pivot=candidate_pivot, source_pairs=source_pairs)
            return (
                _projection(
                    req,state=EvidenceState.UNKNOWN,platform=platform,
                    source_interaction_id=ev.event_id,source_pivot_id=p1.pivot_id,
                    unknown_refs=("SECOND_FAILED_EVENT_NOT_CONSECUTIVE_TO_CANDIDATE_PIVOT",),
                    reason="SECOND_FAILED_EVENT_PREDECESSOR_NOT_CANDIDATE_PIVOT",
                ),
                memory,
            )
        prior_id = req.rearm_predecessor_by_event_id.get(ev.event_id)
        rearm_cutoff = req.rearm_cutoff_by_event_id.get(ev.event_id)
        if prior_id is None or rearm_cutoff is None:
            memory = _memory(req, platform, segment=candidate_segment, candidate_event=candidate_event, candidate_pivot=candidate_pivot, source_pairs=source_pairs)
            return (
                _projection(
                    req,state=EvidenceState.UNKNOWN,platform=platform,
                    source_interaction_id=ev.event_id,source_pivot_id=p1.pivot_id,
                    unknown_refs=("REARM_LINEAGE_UNKNOWN:" + ev.event_id,),
                    reason="REARM_LINEAGE_REQUIRED_FOR_SECOND_FAILED_EVENT",
                ),
                memory,
            )
        if prior_id != candidate_event:
            raise PlatformProductionConflict("REARM_PRIOR_EVENT_MISMATCH:" + ev.event_id)
        prior_ev = event_map.get(candidate_event)
        if prior_ev is None or prior_ev.resolved_at is None:
            raise PlatformProductionBlock("PRIOR_SOURCE_INTERACTION_MISSING:" + candidate_event)
        if rearm_cutoff <= prior_ev.resolved_at:
            raise PlatformProductionConflict("REARM_CUTOFF_NOT_AFTER_PRIOR_RESOLUTION")
        if ev.started_at is None or ev.started_at <= rearm_cutoff:
            raise PlatformProductionConflict("CURRENT_INTERACTION_NOT_AFTER_REARM")
        if ev.event_id == candidate_event:
            raise PlatformProductionConflict("REARM_EVENT_ID_NOT_DISTINCT")
        if ev.target_trend_episode_id != prior_ev.target_trend_episode_id or ev.target_direction is not prior_ev.target_direction:
            raise PlatformProductionConflict("REARM_TREND_LINEAGE_MISMATCH")
        independent = True
        rearmed = True

    failed = FailedReexpansionEvent(
        event_id=ev.event_id,
        symbol=req.symbol,
        timeframe_ms=OBSERVER_TIMEFRAME_MS,
        direction=req.direction,
        confirmation_cutoff=p1.confirmed_at,
        trend_side_minor_extreme_price=p1.extreme_price,
        trend_side_minor_extreme_first_time=p1.extreme_first_time,
        trend_side_minor_extreme_last_time=p1.extreme_last_time,
        protected_structure_intact=bool(intact),
        independent_from_prior=independent,
        rearmed_from_prior=rearmed,
    )

    if intact:
        if req.atr14_at_confirmation.kind is not InfoKind.KNOWN:
            memory = _memory(req, platform, segment=candidate_segment, candidate_event=candidate_event, candidate_pivot=candidate_pivot, source_pairs=source_pairs)
            return (
                _projection(
                    req,state=EvidenceState.UNKNOWN,platform=platform,
                    source_interaction_id=ev.event_id,source_pivot_id=p1.pivot_id,
                    unknown_refs=("ATR14_CONFIRMATION_UNKNOWN",),
                    reason="ATR14_CONFIRMATION_UNKNOWN",
                ),
                memory,
            )
        atr = req.atr14_at_confirmation.require_known()
        if atr <= 0:
            raise PlatformProductionConflict("ATR14_CONFIRMATION_NONPOSITIVE")
    else:
        # update_platform returns EMPTY before consuming ATR when structure is not intact.
        atr = Fraction(1)

    next_platform = update_platform(platform, failed, atr14_at_confirmation=atr)
    source_pairs[ev.event_id] = p1.pivot_id

    if next_platform.status is PlatformStatus.PLATFORM_CANDIDATE:
        next_candidate_event = ev.event_id
        next_candidate_pivot = p1.pivot_id
        next_segment = segment
    elif next_platform.status is PlatformStatus.PLATFORM_CONFIRMED:
        next_candidate_event = candidate_event or ev.event_id
        next_candidate_pivot = candidate_pivot or p1.pivot_id
        next_segment = candidate_segment or segment
    else:
        next_candidate_event = None
        next_candidate_pivot = None
        next_segment = None
        source_pairs = {}

    memory = _memory(
        req,next_platform,segment=next_segment,
        candidate_event=next_candidate_event,candidate_pivot=next_candidate_pivot,
        source_pairs=source_pairs,
    )
    return (
        _projection(
            req,state=EvidenceState.TRUE,platform=next_platform,failed_event=failed,
            d4_evidence=_wire_if_confirmed(req,next_platform),
            source_interaction_id=ev.event_id,source_pivot_id=p1.pivot_id,
            reset_reason="PROTECTED_STRUCTURE_NOT_INTACT" if not intact else None,
            reason="FAILED_REEXPANSION_EVENT_PRODUCED",
        ),
        memory,
    )


def _frac(v: Fraction | None) -> Any:
    return None if v is None else [v.numerator, v.denominator]


def _unfrac(v: Any) -> Fraction | None:
    return None if v is None else Fraction(int(v[0]), int(v[1]))


def _encode_platform(p: PlatformState) -> Mapping[str, Any]:
    return {
        "status": p.status.value,
        "contributing_event_ids": list(p.contributing_event_ids),
        "trend_side_extremes": [_frac(x) for x in p.trend_side_extremes],
        "platform_cap_price": _frac(p.platform_cap_price),
        "platform_scale": _frac(p.platform_scale),
        "confirmed_at": p.confirmed_at,
        "cap_first_time": p.cap_first_time,
        "cap_last_time": p.cap_last_time,
    }


def _decode_platform(v: Mapping[str, Any]) -> PlatformState:
    return PlatformState(
        status=PlatformStatus(v["status"]),
        contributing_event_ids=tuple(str(x) for x in v.get("contributing_event_ids", ())),
        trend_side_extremes=tuple(_unfrac(x) for x in v.get("trend_side_extremes", ())),  # type: ignore[arg-type]
        platform_cap_price=_unfrac(v.get("platform_cap_price")),
        platform_scale=_unfrac(v.get("platform_scale")),
        confirmed_at=v.get("confirmed_at"),
        cap_first_time=v.get("cap_first_time"),
        cap_last_time=v.get("cap_last_time"),
    )


def _encode_memory(m: PlatformLineageMemory) -> Mapping[str, Any]:
    return {
        "trend_episode_id": m.trend_episode_id,
        "direction": m.direction.value,
        "canonical_segment_id": m.canonical_segment_id,
        "platform": _encode_platform(m.platform),
        "candidate_source_event_id": m.candidate_source_event_id,
        "candidate_pivot_id": m.candidate_pivot_id,
        "source_pivot_by_event_id": [list(x) for x in m.source_pivot_by_event_id],
        "last_evaluated_cutoff": m.last_evaluated_cutoff,
    }


def _decode_memory(v: Mapping[str, Any]) -> PlatformLineageMemory:
    return PlatformLineageMemory(
        trend_episode_id=str(v["trend_episode_id"]),
        direction=TrendDirection(v["direction"]),
        canonical_segment_id=v.get("canonical_segment_id"),
        platform=_decode_platform(v["platform"]),
        candidate_source_event_id=v.get("candidate_source_event_id"),
        candidate_pivot_id=v.get("candidate_pivot_id"),
        source_pivot_by_event_id=tuple((str(x[0]), str(x[1])) for x in v.get("source_pivot_by_event_id", ())),
        last_evaluated_cutoff=int(v["last_evaluated_cutoff"]),
    )


class PlatformFailedReexpansionProductionRuntimeV1:
    """Transactional wrapper. prepare() never mutates committed platform state."""

    def __init__(self) -> None:
        self._memory: dict[str, PlatformLineageMemory] = {}
        self._pending: dict[str, tuple[str, str, PlatformProductionProjection, PlatformLineageMemory]] = {}

    def prepare(self, tx_id: str, req: PlatformProductionRequest) -> PlatformProductionProjection:
        digest = b5prod.digest(req)
        pending = self._pending.get(tx_id)
        if pending is not None:
            old_digest, _, projection, _ = pending
            if old_digest != digest:
                raise PlatformProductionConflict("SAME_TX_INPUT_MISMATCH")
            return projection
        prior = self._memory.get(req.trend_episode_id)
        projection, next_memory = project_platform_failed_reexpansion(req, prior)
        self._pending[tx_id] = (digest, req.trend_episode_id, projection, next_memory)
        return projection

    def commit(self, tx_id: str) -> PlatformProductionProjection:
        pending = self._pending.pop(tx_id, None)
        if pending is None:
            raise PlatformProductionBlock("TX_NOT_PREPARED")
        _, episode_id, projection, next_memory = pending
        if projection.state is not EvidenceState.CONFLICT:
            self._memory[episode_id] = next_memory
        return projection

    def abort(self, tx_id: str) -> None:
        self._pending.pop(tx_id, None)

    def ledger_for(self, trend_episode_id: str) -> Mapping[str, Any] | None:
        m = self._memory.get(trend_episode_id)
        return None if m is None else _encode_memory(m)

    def export_state(self) -> Mapping[str, Any]:
        return {
            "schema": "PLATFORM_FAILED_REEXPANSION_PRODUCTION_RUNTIME_STATE_V1",
            "memory": {k: _encode_memory(self._memory[k]) for k in sorted(self._memory)},
        }

    @classmethod
    def restore_state(cls, state: Mapping[str, Any]) -> "PlatformFailedReexpansionProductionRuntimeV1":
        if state.get("schema") != "PLATFORM_FAILED_REEXPANSION_PRODUCTION_RUNTIME_STATE_V1":
            raise PlatformProductionBlock("RUNTIME_STATE_SCHEMA_MISMATCH")
        out = cls()
        raw = state.get("memory", {})
        if not isinstance(raw, Mapping):
            raise PlatformProductionBlock("RUNTIME_MEMORY_SCHEMA_MISMATCH")
        out._memory = {str(k): _decode_memory(v) for k, v in raw.items()}
        return out
