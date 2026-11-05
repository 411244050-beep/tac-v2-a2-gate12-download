from __future__ import annotations

"""Pure QBU 15M MINOR material-progress production binding V1.

Implements only frozen semantic
QBU_MATERIAL_TREND_SIDE_MINOR_PROGRESS_SOURCE_ASSOCIATION_V1.

The constructor derives TrendSideMinorProgressEvidence / ProgressLineageEvidence
from an authoritative complete 15M MINOR pivot stream and binds the result into
the existing Update008Request.  It does not run UPDATE-008, D4 identity, market
I/O, outcome logic, PnL or trading.
"""

from dataclasses import dataclass, field, replace
from types import MappingProxyType
from typing import Mapping

import authoritative_d3_b5_d4_base_runtime_producers_v1 as runtime

from strategy_rc1.d2_market_state.progress import same_type_progress
from strategy_rc1.d2_market_state.types import (
    PivotType,
    ProgressRelation,
    StructuralLayer,
    StructuralPivot,
    TrendDirection,
)
from strategy_rc1.d3_boundary_intelligence.types import (
    AnchorValidity,
    BreakState,
    InteractionEvent,
    InteractionResolution,
    TrendSideMinorProgressEvidence,
)


PRODUCER_ID = "QBU_MATERIAL_TREND_SIDE_MINOR_PROGRESS_PRODUCTION_BINDING_V1"
SEMANTIC_ID = "QBU_MATERIAL_TREND_SIDE_MINOR_PROGRESS_SOURCE_ASSOCIATION_V1"
SEMANTIC_CONTRACT_BLOB = "efa00c82a64a5d4d2a7db0e0679a105a8595924f"
SEMANTIC_FREEZE_MANIFEST_BLOB = "2d0c6215de0c1653afe22a77be78859e2e8a1a4e"
RUNTIME_CONSUMER_BLOB = "97a02f5584c1446ca5ae016bad383e3ed0e18bb5"
OBSERVER_TIMEFRAME_MS = 15 * 60 * 1000


class QBUProgressProductionBlock(RuntimeError):
    pass


class QBUProgressProductionConflict(QBUProgressProductionBlock):
    pass


@dataclass(frozen=True)
class QBUProgressProductionRequest:
    update008_request: runtime.Update008Request
    all_minor: tuple[StructuralPivot, ...]
    trend_episode_start_cutoff: int
    trend_episode_terminal_cutoff: int | None
    history_complete: bool
    history_coverage_ref: str
    theta_progress_parameter_ref: str
    provenance: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "provenance",
            MappingProxyType({str(k): str(v) for k, v in self.provenance.items()}),
        )


@dataclass(frozen=True)
class QBUProgressProductionProjection:
    state: runtime.EvidenceState
    progress_evidence: tuple[runtime.ProgressLineageEvidence, ...]
    unknown_refs: tuple[str, ...] = ()
    conflict_refs: tuple[str, ...] = ()
    provenance: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "provenance",
            MappingProxyType({str(k): str(v) for k, v in self.provenance.items()}),
        )


def _trend_side_type(direction: TrendDirection) -> PivotType:
    if direction is TrendDirection.LONG:
        return PivotType.HIGH
    if direction is TrendDirection.SHORT:
        return PivotType.LOW
    raise QBUProgressProductionConflict("INVALID_DIRECTION")


def _material_relation(direction: TrendDirection) -> ProgressRelation:
    if direction is TrendDirection.LONG:
        return ProgressRelation.MATERIAL_ADVANCE_UP
    if direction is TrendDirection.SHORT:
        return ProgressRelation.MATERIAL_ADVANCE_DOWN
    raise QBUProgressProductionConflict("INVALID_DIRECTION")


def _canonical_event_map(events: tuple[InteractionEvent, ...]) -> tuple[dict[str, InteractionEvent], tuple[str, ...]]:
    out: dict[str, InteractionEvent] = {}
    conflicts: set[str] = set()
    for ev in events:
        old = out.get(ev.event_id)
        if old is not None and old != ev:
            conflicts.add(ev.event_id)
        else:
            out[ev.event_id] = ev
    return out, tuple(sorted(conflicts))


def _canonical_pivot_map(pivots: tuple[StructuralPivot, ...]) -> tuple[dict[str, StructuralPivot], tuple[str, ...]]:
    out: dict[str, StructuralPivot] = {}
    conflicts: set[str] = set()
    for p in pivots:
        old = out.get(p.pivot_id)
        if old is not None and old != p:
            conflicts.add(p.pivot_id)
        else:
            out[p.pivot_id] = p
    return out, tuple(sorted(conflicts))


def _target_events(req: runtime.Update008Request) -> tuple[tuple[InteractionEvent, str], ...]:
    """Return consumer-relevant resolved events plus their canonical segment IDs."""
    event_map, event_conflicts = _canonical_event_map(req.events)
    if event_conflicts:
        raise QBUProgressProductionConflict(
            "DIVERGENT_EVENT_RECORD:" + ",".join(event_conflicts)
        )

    rows: list[tuple[InteractionEvent, str]] = []
    seen: set[str] = set()
    for ep in sorted(req.episodes, key=lambda e: e.anchor_episode_id):
        if ep.target_trend_episode_id != req.trend_episode_id or ep.target_direction is not req.direction:
            continue
        if ep.validity is AnchorValidity.TERMINATED or ep.terminal_true_break:
            continue

        segment = req.canonical_segment_id_by_anchor_episode_id.get(ep.anchor_episode_id)
        if not segment:
            # Existing consumer will fail this event's lineage; constructor must
            # not invent a segment.
            for eid in ep.interaction_event_ids:
                ev = event_map.get(eid)
                if ev is not None and ev.resolution is InteractionResolution.RESOLVED_CORRECT_SIDE:
                    raise QBUProgressProductionBlock("CANONICAL_SEGMENT_UNKNOWN:" + ep.anchor_episode_id)
            continue

        continuity = req.continuity_by_candidate_id.get(ep.candidate_id)
        if continuity is None:
            for eid in ep.interaction_event_ids:
                ev = event_map.get(eid)
                if ev is not None and ev.resolution is InteractionResolution.RESOLVED_CORRECT_SIDE:
                    raise QBUProgressProductionBlock("CONTINUITY_UNKNOWN:" + ep.candidate_id)
            continue
        if continuity is False:
            for eid in ep.interaction_event_ids:
                ev = event_map.get(eid)
                if ev is not None and ev.resolution is InteractionResolution.RESOLVED_CORRECT_SIDE:
                    raise QBUProgressProductionConflict("CONTINUITY_FALSE:" + ep.candidate_id)
            continue

        for event_id in sorted(set(ep.interaction_event_ids)):
            ev = event_map.get(event_id)
            if ev is None:
                # Missing event remains owned by existing QBU consumer.
                continue
            if (
                ev.anchor_episode_id != ep.anchor_episode_id
                or ev.target_trend_episode_id != ep.target_trend_episode_id
                or ev.target_direction is not ep.target_direction
                or ev.candidate_id != ep.candidate_id
            ):
                raise QBUProgressProductionConflict("EVENT_EPISODE_LINEAGE_MISMATCH:" + event_id)
            if ev.resolution is not InteractionResolution.RESOLVED_CORRECT_SIDE or ev.break_state is BreakState.TRUE_BREAK:
                continue
            if ev.resolved_at is None:
                raise QBUProgressProductionBlock("EVENT_RESOLUTION_CUTOFF_UNKNOWN:" + event_id)
            if ev.resolved_at > req.information_cutoff:
                raise QBUProgressProductionConflict("FUTURE_EVENT_RESOLUTION:" + event_id)
            if event_id in seen:
                # One event may not belong to multiple target AnchorEpisodes.
                raise QBUProgressProductionConflict("EVENT_MULTI_EPISODE_MEMBERSHIP:" + event_id)
            seen.add(event_id)
            rows.append((ev, segment))
    return tuple(rows)


def _episode_segment_stream(
    request: QBUProgressProductionRequest,
    *,
    segment: str,
) -> tuple[StructuralPivot, ...]:
    base = request.update008_request
    pivot_map, duplicate_conflicts = _canonical_pivot_map(request.all_minor)
    if duplicate_conflicts:
        raise QBUProgressProductionConflict(
            "DIVERGENT_PIVOT_RECORD:" + ",".join(duplicate_conflicts)
        )

    selected: list[StructuralPivot] = []
    for p in pivot_map.values():
        if p.canonical_segment_id != segment:
            continue
        if p.confirmed_at < request.trend_episode_start_cutoff:
            continue
        if (
            request.trend_episode_terminal_cutoff is not None
            and p.confirmed_at > request.trend_episode_terminal_cutoff
        ):
            continue
        if p.confirmed_at > base.information_cutoff:
            raise QBUProgressProductionConflict("FUTURE_PIVOT:" + p.pivot_id)
        if p.timeframe_ms != OBSERVER_TIMEFRAME_MS:
            raise QBUProgressProductionConflict("PIVOT_TIMEFRAME_MISMATCH:" + p.pivot_id)
        if p.layer is not StructuralLayer.MINOR:
            raise QBUProgressProductionConflict("PIVOT_LAYER_MISMATCH:" + p.pivot_id)
        selected.append(p)

    return tuple(sorted(selected, key=lambda p: (p.confirmed_at, p.pivot_id)))


def _reference_p0(
    stream: tuple[StructuralPivot, ...],
    p1: StructuralPivot,
) -> tuple[runtime.EvidenceState, StructuralPivot | None, str | None]:
    same_type = [
        p for p in stream
        if p.pivot_id != p1.pivot_id
        and p.pivot_type is p1.pivot_type
        and p.confirmed_at < p1.confirmed_at
    ]
    if not same_type:
        return runtime.EvidenceState.UNKNOWN, None, "NO_COMPARABLE_PREDECESSOR:" + p1.pivot_id

    latest_cutoff = max(p.confirmed_at for p in same_type)
    roots = {p.pivot_id: p for p in same_type if p.confirmed_at == latest_cutoff}
    if len(roots) != 1:
        return runtime.EvidenceState.CONFLICT, None, "NONUNIQUE_IMMEDIATE_PREDECESSOR:" + p1.pivot_id
    return runtime.EvidenceState.TRUE, next(iter(roots.values())), None


def project_qbu_progress_evidence(
    request: QBUProgressProductionRequest,
) -> QBUProgressProductionProjection:
    if not isinstance(request, QBUProgressProductionRequest):
        raise QBUProgressProductionConflict("REQUEST_SCHEMA")

    base = request.update008_request
    if base.progress_evidence:
        return QBUProgressProductionProjection(
            state=runtime.EvidenceState.CONFLICT,
            progress_evidence=(),
            conflict_refs=("CALLER_PREPOPULATED_PROGRESS_EVIDENCE_FORBIDDEN",),
            provenance={"producer_id": PRODUCER_ID, "semantic_id": SEMANTIC_ID},
        )
    if base.direction not in (TrendDirection.LONG, TrendDirection.SHORT):
        return QBUProgressProductionProjection(
            state=runtime.EvidenceState.CONFLICT,
            progress_evidence=(),
            conflict_refs=("INVALID_DIRECTION",),
            provenance={"producer_id": PRODUCER_ID, "semantic_id": SEMANTIC_ID},
        )
    if request.trend_episode_start_cutoff < 0:
        return QBUProgressProductionProjection(
            state=runtime.EvidenceState.CONFLICT,
            progress_evidence=(),
            conflict_refs=("INVALID_TREND_EPISODE_START_CUTOFF",),
            provenance={"producer_id": PRODUCER_ID, "semantic_id": SEMANTIC_ID},
        )
    if (
        request.trend_episode_terminal_cutoff is not None
        and request.trend_episode_terminal_cutoff < request.trend_episode_start_cutoff
    ):
        return QBUProgressProductionProjection(
            state=runtime.EvidenceState.CONFLICT,
            progress_evidence=(),
            conflict_refs=("TREND_EPISODE_INTERVAL_INVERTED",),
            provenance={"producer_id": PRODUCER_ID, "semantic_id": SEMANTIC_ID},
        )
    if not request.history_complete or not request.history_coverage_ref:
        return QBUProgressProductionProjection(
            state=runtime.EvidenceState.UNKNOWN,
            progress_evidence=(),
            unknown_refs=("MINOR_HISTORY_COVERAGE_INCOMPLETE",),
            provenance={"producer_id": PRODUCER_ID, "semantic_id": SEMANTIC_ID},
        )
    if not request.theta_progress_parameter_ref:
        return QBUProgressProductionProjection(
            state=runtime.EvidenceState.UNKNOWN,
            progress_evidence=(),
            unknown_refs=("THETA_PROGRESS_PARAMETER_PROVENANCE_UNKNOWN",),
            provenance={"producer_id": PRODUCER_ID, "semantic_id": SEMANTIC_ID},
        )
    if base.theta_progress <= 0:
        return QBUProgressProductionProjection(
            state=runtime.EvidenceState.CONFLICT,
            progress_evidence=(),
            conflict_refs=("THETA_PROGRESS_NONPOSITIVE",),
            provenance={"producer_id": PRODUCER_ID, "semantic_id": SEMANTIC_ID},
        )

    try:
        target_events = _target_events(base)
    except QBUProgressProductionConflict as exc:
        return QBUProgressProductionProjection(
            state=runtime.EvidenceState.CONFLICT,
            progress_evidence=(),
            conflict_refs=(str(exc),),
            provenance={"producer_id": PRODUCER_ID, "semantic_id": SEMANTIC_ID},
        )
    except QBUProgressProductionBlock as exc:
        return QBUProgressProductionProjection(
            state=runtime.EvidenceState.UNKNOWN,
            progress_evidence=(),
            unknown_refs=(str(exc),),
            provenance={"producer_id": PRODUCER_ID, "semantic_id": SEMANTIC_ID},
        )

    records: list[runtime.ProgressLineageEvidence] = []
    unknown: set[str] = set()
    conflict: set[str] = set()
    stream_cache: dict[str, tuple[StructuralPivot, ...]] = {}

    for event, segment in target_events:
        try:
            stream = stream_cache.setdefault(
                segment,
                _episode_segment_stream(request, segment=segment),
            )
        except QBUProgressProductionConflict as exc:
            conflict.add(str(exc))
            continue

        ptype = _trend_side_type(base.direction)
        candidates = [
            p for p in stream
            if p.pivot_type is ptype
            and p.confirmed_at > event.resolved_at
            and p.confirmed_at <= base.information_cutoff
        ]

        for p1 in candidates:
            state, p0, reason = _reference_p0(stream, p1)
            if state is runtime.EvidenceState.UNKNOWN:
                assert reason is not None
                unknown.add(event.event_id + ":" + reason)
                continue
            if state is runtime.EvidenceState.CONFLICT or p0 is None:
                conflict.add(event.event_id + ":" + (reason or "REFERENCE_CONFLICT"))
                continue

            if (
                p0.symbol != p1.symbol
                or p0.timeframe_ms != p1.timeframe_ms
                or p0.layer is not p1.layer
                or p0.pivot_type is not p1.pivot_type
                or p0.canonical_segment_id != p1.canonical_segment_id
                or p0.confirmed_at >= p1.confirmed_at
            ):
                conflict.add(event.event_id + ":P0_P1_LINEAGE_CONFLICT:" + p1.pivot_id)
                continue

            try:
                relation = same_type_progress(p0, p1, base.theta_progress)
            except ValueError:
                conflict.add(event.event_id + ":SAME_TYPE_PROGRESS_INPUT_CONFLICT:" + p1.pivot_id)
                continue
            material = relation is _material_relation(base.direction)

            progress = TrendSideMinorProgressEvidence(
                pivot_id=p1.pivot_id,
                confirmed_at=p1.confirmed_at,
                material_progress=material,
                timeframe_ms=OBSERVER_TIMEFRAME_MS,
                layer="MINOR",
            )
            records.append(
                runtime.ProgressLineageEvidence(
                    event_id=event.event_id,
                    progress=progress,
                    target_trend_episode_id=base.trend_episode_id,
                    direction=base.direction,
                    canonical_segment_id=segment,
                    continuity_intact=True,
                    provenance={
                        "producer_id": PRODUCER_ID,
                        "semantic_id": SEMANTIC_ID,
                        "semantic_contract_blob": SEMANTIC_CONTRACT_BLOB,
                        "semantic_freeze_manifest_blob": SEMANTIC_FREEZE_MANIFEST_BLOB,
                        "history_coverage_ref": request.history_coverage_ref,
                        "p0_pivot_id": p0.pivot_id,
                        "p0_confirmed_at": str(p0.confirmed_at),
                        "p0_extreme_price": str(p0.extreme_price),
                        "p0_scale_at_extreme": str(p0.scale_at_extreme),
                        "p1_pivot_id": p1.pivot_id,
                        "p1_confirmed_at": str(p1.confirmed_at),
                        "p1_extreme_price": str(p1.extreme_price),
                        "same_type_progress_relation": relation.value,
                        "theta_progress_parameter_ref": request.theta_progress_parameter_ref,
                        "information_cutoff": str(base.information_cutoff),
                    },
                )
            )

    if conflict:
        return QBUProgressProductionProjection(
            state=runtime.EvidenceState.CONFLICT,
            progress_evidence=(),
            conflict_refs=tuple(sorted(conflict)),
            provenance={"producer_id": PRODUCER_ID, "semantic_id": SEMANTIC_ID},
        )
    if unknown:
        return QBUProgressProductionProjection(
            state=runtime.EvidenceState.UNKNOWN,
            progress_evidence=(),
            unknown_refs=tuple(sorted(unknown)),
            provenance={"producer_id": PRODUCER_ID, "semantic_id": SEMANTIC_ID},
        )

    canonical_records: dict[tuple[str, str], runtime.ProgressLineageEvidence] = {}
    for rec in records:
        key = (rec.event_id, rec.progress.pivot_id)
        old = canonical_records.get(key)
        if old is not None and old != rec:
            return QBUProgressProductionProjection(
                state=runtime.EvidenceState.CONFLICT,
                progress_evidence=(),
                conflict_refs=("DIVERGENT_PROGRESS_RECORD:" + rec.event_id + ":" + rec.progress.pivot_id,),
                provenance={"producer_id": PRODUCER_ID, "semantic_id": SEMANTIC_ID},
            )
        canonical_records[key] = rec

    output = tuple(
        canonical_records[k]
        for k in sorted(
            canonical_records,
            key=lambda k: (
                k[0],
                canonical_records[k].progress.confirmed_at,
                canonical_records[k].progress.pivot_id,
            ),
        )
    )
    return QBUProgressProductionProjection(
        state=runtime.EvidenceState.TRUE,
        progress_evidence=output,
        unknown_refs=(),
        conflict_refs=(),
        provenance={
            "producer_id": PRODUCER_ID,
            "semantic_id": SEMANTIC_ID,
            "runtime_consumer_blob": RUNTIME_CONSUMER_BLOB,
            "history_coverage_ref": request.history_coverage_ref,
            "theta_progress_parameter_ref": request.theta_progress_parameter_ref,
            "f9_stage": "POST_UPDATE007_PRE_UPDATE008",
            "scientific_state_mutated": "false",
            "real_market_data_read": "false",
            "test_read": "false",
            "pnl": "false",
            "trading": "FORBIDDEN",
        },
    )


def bind_update008_request(
    request: runtime.Update008Request,
    projection: QBUProgressProductionProjection,
) -> runtime.Update008Request:
    if not isinstance(request, runtime.Update008Request):
        raise QBUProgressProductionConflict("UPDATE008_REQUEST_SCHEMA")
    if request.progress_evidence:
        raise QBUProgressProductionConflict("CALLER_PREPOPULATED_PROGRESS_EVIDENCE_FORBIDDEN")
    if projection.state is not runtime.EvidenceState.TRUE:
        raise QBUProgressProductionBlock("TRUE_PROGRESS_PROJECTION_REQUIRED")
    return replace(
        request,
        progress_evidence=projection.progress_evidence,
        provenance={
            **dict(request.provenance),
            "qbu_progress_producer_id": PRODUCER_ID,
            "qbu_progress_semantic_id": SEMANTIC_ID,
        },
    )
