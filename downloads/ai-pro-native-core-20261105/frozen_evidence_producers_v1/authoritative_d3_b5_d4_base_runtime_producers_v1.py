from __future__ import annotations

"""Authoritative D3/B5 + D4 base-evidence runtime producers V1.

Production implementation only.  Scientific semantics are not defined here; every
projection mechanically implements the frozen post-RC1 semantic contracts referenced
by SEMANTIC_FREEZE_TERMINAL_BLOB / SEMANTIC_FREEZE_MANIFEST_BLOB.

This module does not assemble CutoffEvidencePacket, access a market source, evaluate
TEST/outcomes/PnL, create orders, or activate Forward Observation.
"""

from dataclasses import dataclass, field, fields, is_dataclass, replace
from enum import Enum
from fractions import Fraction
from hashlib import sha256
import importlib
import json
from types import MappingProxyType
from typing import Any, Mapping

from strategy_rc1.ids import deterministic_id
from strategy_rc1.d2_market_state.types import (
    PivotType,
    StructuralCorridor,
    StructuralLayer,
    StructuralPivot,
    TrendDirection,
    TrendEpisodeState,
    PlatformState,
)
from strategy_rc1.d3_boundary_intelligence.anchors import (
    add_qualified_boundary_use,
    make_qualified_boundary_use,
)
from strategy_rc1.d3_boundary_intelligence.clusters_roles import (
    assign_roles,
    cluster_units,
    current_relevance,
    structural_role_eligible,
    unit_intersects_corridor,
    unit_intersects_protected_zone,
)
from strategy_rc1.d3_boundary_intelligence.types import (
    AnchorActivity,
    AnchorEpisode,
    AnchorValidity,
    BoundaryContactZone,
    BoundaryUnitRoleEvidence,
    BreakState,
    CandidateAvailability,
    CausalBoundarySnapshot,
    EconomicBoundaryUnit,
    InteractionControl,
    InteractionEvent,
    InteractionResolution,
    MathematicalBoundaryCandidate,
    QualifiedBoundaryUse,
    RoleAssignment,
    RoleTransition,
    StructuralDepthRelation,
    TrendSideMinorProgressEvidence,
)
from strategy_rc1.d4_opportunity.eligibility import entry_boundary_view
from strategy_rc1.d4_opportunity.mechanisms import (
    DeepStructureTakeoverEvidence,
    FalseBreakReclaimEvidence,
    NormalRetestEvidence,
    PlatformReexpansionEvidence,
    TrendEstablishmentWatchEvidence,
)
from strategy_rc1.d4_opportunity.types import EntryBoundaryView, LocalTrendControlRegainEvidence

from d2_to_b4_d4_causal_evidence_producers_v1 import EvidenceState


SEMANTIC_FREEZE_TERMINAL_BLOB = "fb03beb4c9559892f6d3d6f4b3602ef7f0e6da4b"
SEMANTIC_FREEZE_MANIFEST_BLOB = "09f1d5cc844f5943bacd2a06f8a319f30ab803dd"
RUNTIME_CONTRACT_ID = "AUTHORITATIVE_D3_B5_D4_BASE_RUNTIME_PRODUCERS_V1"
OBSERVER_TIMEFRAME_MS = 15 * 60 * 1000

DEPTH_OPERATING_LOCAL = "OPERATING_LOCAL"
DEPTH_PROTECTED_INTERMEDIATE = "PROTECTED_INTERMEDIATE"
DEPTH_UNRESOLVED = "UNRESOLVED"


class RuntimeProducerBlock(RuntimeError):
    pass


def _encode(value: Any) -> Any:
    if isinstance(value, Fraction):
        return {"$fraction": [value.numerator, value.denominator]}
    if isinstance(value, Enum):
        return {"$enum": [value.__class__.__module__, value.__class__.__qualname__, value.value]}
    if isinstance(value, MappingProxyType):
        value = dict(value)
    if is_dataclass(value) and not isinstance(value, type):
        return {
            "$dataclass": [value.__class__.__module__, value.__class__.__qualname__],
            "fields": {f.name: _encode(getattr(value, f.name)) for f in fields(value)},
        }
    if isinstance(value, Mapping):
        return {"$map": [[str(k), _encode(v)] for k, v in sorted(value.items(), key=lambda kv: str(kv[0]))]}
    if isinstance(value, tuple):
        return {"$tuple": [_encode(x) for x in value]}
    if isinstance(value, list):
        return {"$list": [_encode(x) for x in value]}
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    raise TypeError(f"UNSUPPORTED_SERIALIZATION_TYPE:{type(value)!r}")


def _resolve(module: str, qualname: str) -> Any:
    obj: Any = importlib.import_module(module)
    for part in qualname.split("."):
        obj = getattr(obj, part)
    return obj


def _decode(value: Any) -> Any:
    if isinstance(value, list):
        return [_decode(x) for x in value]
    if not isinstance(value, dict):
        return value
    if "$fraction" in value:
        return Fraction(*value["$fraction"])
    if "$enum" in value:
        module, qualname, raw = value["$enum"]
        return _resolve(module, qualname)(raw)
    if "$tuple" in value:
        return tuple(_decode(x) for x in value["$tuple"])
    if "$list" in value:
        return [_decode(x) for x in value["$list"]]
    if "$map" in value:
        return {k: _decode(v) for k, v in value["$map"]}
    if "$dataclass" in value:
        module, qualname = value["$dataclass"]
        cls = _resolve(module, qualname)
        return cls(**{k: _decode(v) for k, v in value["fields"].items()})
    return {k: _decode(v) for k, v in value.items()}


def exact_json(value: Any) -> str:
    return json.dumps(_encode(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return sha256(exact_json(value).encode()).hexdigest()


@dataclass(frozen=True)
class ProgressLineageEvidence:
    event_id: str
    progress: TrendSideMinorProgressEvidence
    target_trend_episode_id: str
    direction: TrendDirection
    canonical_segment_id: str
    continuity_intact: bool
    provenance: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class BoundaryZoneBatch:
    state: EvidenceState
    zones: tuple[BoundaryContactZone, ...]
    unavailable_anchor_ids: tuple[str, ...] = ()
    unknown_anchor_ids: tuple[str, ...] = ()
    conflict_anchor_ids: tuple[str, ...] = ()
    provenance: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class QBUProjection:
    state: EvidenceState
    episodes: tuple[AnchorEpisode, ...]
    produced_uses: tuple[QualifiedBoundaryUse, ...]
    unknown_event_ids: tuple[str, ...] = ()
    conflict_event_ids: tuple[str, ...] = ()
    provenance: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class RoleMemory:
    trend_episode_id: str
    primary_unit_id: str
    primary_anchor_episode_ids: tuple[str, ...]
    primary_depth_class: str
    primary_qbu_identities: tuple[str, ...]
    primary_qbu_cutoff: int


@dataclass(frozen=True)
class RoleRuntimeOutput:
    state: EvidenceState
    units: tuple[EconomicBoundaryUnit, ...]
    role_evidence: tuple[BoundaryUnitRoleEvidence, ...]
    assignment: RoleAssignment | None
    depth_class_by_unit_id: tuple[tuple[str, str], ...]
    qbu_identities_by_unit_id: tuple[tuple[str, tuple[str, ...]], ...]
    primary_qbu_identities: tuple[str, ...]
    promotion_confirmed_at: int | None
    prior_primary_continuity_preserved: bool
    unresolved_reasons: tuple[str, ...] = ()
    conflict_reasons: tuple[str, ...] = ()
    provenance: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Update008Request:
    information_cutoff: int
    trend_episode_id: str
    direction: TrendDirection
    snapshots: tuple[CausalBoundarySnapshot, ...]
    candidates: tuple[MathematicalBoundaryCandidate, ...]
    episodes: tuple[AnchorEpisode, ...]
    events: tuple[InteractionEvent, ...]
    progress_evidence: tuple[ProgressLineageEvidence, ...]
    negotiation_identity_by_event_id: Mapping[str, str]
    canonical_segment_id_by_anchor_episode_id: Mapping[str, str]
    continuity_by_candidate_id: Mapping[str, bool | None]
    corridor: StructuralCorridor | None
    protected_price: Fraction | None
    protected_scale: Fraction | None
    theta_test: Fraction
    theta_progress: Fraction
    provenance: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Update008Output:
    state: EvidenceState
    episodes: tuple[AnchorEpisode, ...]
    zones: tuple[BoundaryContactZone, ...]
    units: tuple[EconomicBoundaryUnit, ...]
    role_evidence: tuple[BoundaryUnitRoleEvidence, ...]
    roles: RoleAssignment | None
    role_runtime: RoleRuntimeOutput | None
    produced_qbus: tuple[QualifiedBoundaryUse, ...]
    unknown_lineage_refs: tuple[str, ...] = ()
    conflict_lineage_refs: tuple[str, ...] = ()
    provenance: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class EntryBoundaryProjection:
    state: EvidenceState
    unit: EconomicBoundaryUnit | None
    view: EntryBoundaryView | None
    required_anchor_episode_ids: tuple[str, ...]
    reason: str
    provenance: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class FixedAdverseReference:
    setup_key: str
    pivot_id: str
    confirmed_at: int
    canonical_segment_id: str
    direction: TrendDirection


@dataclass(frozen=True)
class NormalRetestProjection:
    state: EvidenceState
    evidence: NormalRetestEvidence | None
    adverse_reference: FixedAdverseReference | None
    reason: str
    provenance: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class DeepTakeoverRequest:
    information_cutoff: int
    trend_episode_id: str
    direction: TrendDirection
    opportunity_id: str
    market_event_id: str
    shallow_unit: EconomicBoundaryUnit
    deeper_entry_boundary: EntryBoundaryProjection
    deeper_interaction: InteractionEvent
    role_runtime: RoleRuntimeOutput
    shallow_behavior_confirmation_cutoff: int | None
    same_market_event_identity_authoritative: bool
    local_control_regain: LocalTrendControlRegainEvidence | None
    setup_lineage: tuple[str, ...]
    provenance: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class DeepTakeoverProjection:
    state: EvidenceState
    evidence: DeepStructureTakeoverEvidence | None
    reason: str
    provenance: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class TrendEstablishmentRecord:
    trend: TrendEpisodeState
    creation_cutoff: int
    newest_intermediate_pivot_id: str
    source_event_ids: tuple[str, ...]
    provenance: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class TrendWatchProjection:
    state: EvidenceState
    evidence: TrendEstablishmentWatchEvidence | None
    reason: str
    provenance: Mapping[str, str] = field(default_factory=dict)


def _episode_map(episodes: tuple[AnchorEpisode, ...]) -> dict[str, AnchorEpisode]:
    return {ep.anchor_episode_id: ep for ep in episodes}


def _event_map(events: tuple[InteractionEvent, ...]) -> dict[str, InteractionEvent]:
    return {ev.event_id: ev for ev in events}


def _candidate_map(candidates: tuple[MathematicalBoundaryCandidate, ...]) -> dict[str, MathematicalBoundaryCandidate]:
    return {c.candidate_id: c for c in candidates}


def _direction_ok(direction: TrendDirection) -> bool:
    return direction in (TrendDirection.LONG, TrendDirection.SHORT)


def _event_actual_contact(event: InteractionEvent, cutoff: int) -> bool:
    if event.control not in (InteractionControl.INTERACTION_ACTIVE, InteractionControl.RESOLVED):
        return False
    if event.event_reference_boundary is None or event.event_reference_scale is None:
        return False
    if event.started_at is None or event.started_at > cutoff:
        return False
    return True


def produce_boundary_contact_zones(request: Update008Request) -> BoundaryZoneBatch:
    if not _direction_ok(request.direction):
        return BoundaryZoneBatch(EvidenceState.CONFLICT, (), conflict_anchor_ids=("INVALID_DIRECTION",))
    candidates = _candidate_map(request.candidates)
    snapshots_by_anchor: dict[str, list[CausalBoundarySnapshot]] = {}
    for snap in request.snapshots:
        if snap.available_at > request.information_cutoff:
            continue
        if snap.anchor_episode_id is not None:
            snapshots_by_anchor.setdefault(snap.anchor_episode_id, []).append(snap)

    zones: list[BoundaryContactZone] = []
    unavailable: list[str] = []
    unknown: list[str] = []
    conflict: list[str] = []

    for episode in sorted(request.episodes, key=lambda e: e.anchor_episode_id):
        if episode.target_trend_episode_id != request.trend_episode_id or episode.target_direction is not request.direction:
            continue
        if episode.validity is AnchorValidity.TERMINATED or episode.activity is AnchorActivity.TERMINATED or episode.terminal_true_break:
            continue

        candidate = candidates.get(episode.candidate_id)
        if candidate is None:
            unknown.append(episode.anchor_episode_id)
            continue
        if candidate.target_trend_episode_id != request.trend_episode_id or candidate.target_direction is not request.direction:
            conflict.append(episode.anchor_episode_id)
            continue
        if candidate.availability is not CandidateAvailability.AVAILABLE:
            unavailable.append(episode.anchor_episode_id)
            continue

        continuity = request.continuity_by_candidate_id.get(candidate.candidate_id)
        if continuity is not True:
            unknown.append(episode.anchor_episode_id)
            continue

        snaps = [
            s for s in snapshots_by_anchor.get(episode.anchor_episode_id, ())
            if s.candidate_id == candidate.candidate_id
        ]
        if not snaps:
            unknown.append(episode.anchor_episode_id)
            continue
        latest_at = max(s.available_at for s in snaps)
        latest_by_id = {s.snapshot_id: s for s in snaps if s.available_at == latest_at}
        if len(latest_by_id) != 1:
            conflict.append(episode.anchor_episode_id)
            continue
        snap = next(iter(latest_by_id.values()))
        if (
            snap.target_trend_episode_id != request.trend_episode_id
            or snap.target_direction is not request.direction
            or snap.anchor_episode_id != episode.anchor_episode_id
            or snap.candidate_id != episode.candidate_id
        ):
            conflict.append(episode.anchor_episode_id)
            continue

        if request.direction is TrendDirection.LONG:
            lower = snap.boundary
            upper = snap.boundary + request.theta_test * snap.source_scale
        else:
            lower = snap.boundary - request.theta_test * snap.source_scale
            upper = snap.boundary
        zones.append(
            BoundaryContactZone(
                zone_id=deterministic_id(
                    "D3-BCZ-V1",
                    snap.snapshot_id,
                    episode.anchor_episode_id,
                    str(request.information_cutoff),
                ),
                anchor_episode_id=episode.anchor_episode_id,
                lower=lower,
                upper=upper,
                information_cutoff=request.information_cutoff,
                provenance={
                    "producer_semantic_contract_id": "TAC_BOUNDARY_CONTACT_ZONE_QBU_RUNTIME_PROJECTION_SEMANTIC_CONTRACT_V1",
                    "snapshot_id": snap.snapshot_id,
                    "candidate_id": snap.candidate_id,
                    "target_trend_episode_id": snap.target_trend_episode_id,
                    "direction": snap.target_direction.value,
                    "source_timeframe_ms": str(snap.source_timeframe_ms),
                    "source_segment_id": snap.source_segment_id,
                    "boundary": str(snap.boundary),
                    "source_scale": str(snap.source_scale),
                    "theta_test": str(request.theta_test),
                    "information_cutoff": str(request.information_cutoff),
                    "geometry": "DIRECTION_AWARE_B3_TEST_BAND",
                },
            )
        )

    state = EvidenceState.CONFLICT if conflict else (EvidenceState.TRUE if zones else EvidenceState.UNKNOWN)
    return BoundaryZoneBatch(
        state=state,
        zones=tuple(sorted(zones, key=lambda z: (z.lower, z.upper, z.anchor_episode_id, z.zone_id))),
        unavailable_anchor_ids=tuple(sorted(set(unavailable))),
        unknown_anchor_ids=tuple(sorted(set(unknown))),
        conflict_anchor_ids=tuple(sorted(set(conflict))),
        provenance={
            "producer_semantic_contract_id": "TAC_BOUNDARY_CONTACT_ZONE_QBU_RUNTIME_PROJECTION_SEMANTIC_CONTRACT_V1",
            "f9_stage": "UPDATE-008",
            "historical_union": "false",
        },
    )


def _progress_for_event(
    event: InteractionEvent,
    episode: AnchorEpisode,
    request: Update008Request,
) -> tuple[EvidenceState, TrendSideMinorProgressEvidence | None, str]:
    expected_segment = request.canonical_segment_id_by_anchor_episode_id.get(episode.anchor_episode_id)
    records = [p for p in request.progress_evidence if p.event_id == event.event_id]
    for rec in records:
        if (
            rec.target_trend_episode_id != event.target_trend_episode_id
            or rec.direction is not event.target_direction
            or rec.continuity_intact is not True
            or expected_segment is None
            or rec.canonical_segment_id != expected_segment
        ):
            return EvidenceState.CONFLICT, None, "PROGRESS_LINEAGE_CONFLICT"

    eligible = [
        rec.progress for rec in records
        if event.resolved_at is not None
        and rec.progress.confirmed_at > event.resolved_at
        and rec.progress.confirmed_at <= request.information_cutoff
        and rec.progress.material_progress
        and rec.progress.timeframe_ms == OBSERVER_TIMEFRAME_MS
        and rec.progress.layer == "MINOR"
    ]
    if not eligible:
        return EvidenceState.UNKNOWN, None, "NO_CAUSAL_POST_RESOLUTION_PROGRESS"
    first_cutoff = min(p.confirmed_at for p in eligible)
    first = {p.pivot_id: p for p in eligible if p.confirmed_at == first_cutoff}
    if len(first) != 1:
        return EvidenceState.CONFLICT, None, "MULTIPLE_FIRST_PROGRESS_PIVOTS"
    return EvidenceState.TRUE, next(iter(first.values())), "FIRST_CAUSAL_PROGRESS"


def produce_qbus(request: Update008Request) -> QBUProjection:
    episodes = _episode_map(request.episodes)
    events = _event_map(request.events)
    produced: list[QualifiedBoundaryUse] = []
    unknown: list[str] = []
    conflict: list[str] = []

    for episode_id in sorted(episodes):
        episode = episodes[episode_id]
        if episode.target_trend_episode_id != request.trend_episode_id or episode.target_direction is not request.direction:
            continue
        if episode.validity is AnchorValidity.TERMINATED or episode.terminal_true_break:
            continue
        for event_id in sorted(set(episode.interaction_event_ids)):
            event = events.get(event_id)
            if event is None:
                unknown.append(event_id)
                continue
            if (
                event.anchor_episode_id != episode.anchor_episode_id
                or event.target_trend_episode_id != episode.target_trend_episode_id
                or event.target_direction is not episode.target_direction
            ):
                conflict.append(event_id)
                continue
            if event.resolution is not InteractionResolution.RESOLVED_CORRECT_SIDE or event.break_state is BreakState.TRUE_BREAK:
                continue
            if event.resolved_at is None or event.resolved_at > request.information_cutoff:
                unknown.append(event_id)
                continue

            existing = [u for u in episode.qualified_uses if u.negotiation_event_id == event.event_id]
            state, progress, reason = _progress_for_event(event, episode, request)
            if existing:
                if len(existing) != 1:
                    conflict.append(event_id)
                    continue
                if state is EvidenceState.TRUE and progress is not None:
                    old = existing[0]
                    if old.trend_side_minor_progress_pivot_id != progress.pivot_id or old.progress_confirmed_at != progress.confirmed_at:
                        conflict.append(event_id)
                continue
            if state is EvidenceState.UNKNOWN:
                unknown.append(event_id)
                continue
            if state is EvidenceState.CONFLICT or progress is None:
                conflict.append(event_id)
                continue

            try:
                use = make_qualified_boundary_use(episode, event, progress)
            except ValueError:
                conflict.append(event_id)
                continue
            episode = add_qualified_boundary_use(episode, use)
            episodes[episode.anchor_episode_id] = episode
            produced.append(use)

    state = EvidenceState.CONFLICT if conflict else EvidenceState.TRUE
    return QBUProjection(
        state=state,
        episodes=tuple(sorted(episodes.values(), key=lambda ep: ep.anchor_episode_id)),
        produced_uses=tuple(sorted(produced, key=lambda u: (u.progress_confirmed_at, u.use_id))),
        unknown_event_ids=tuple(sorted(set(unknown))),
        conflict_event_ids=tuple(sorted(set(conflict))),
        provenance={
            "producer_semantic_contract_id": "TAC_BOUNDARY_CONTACT_ZONE_QBU_RUNTIME_PROJECTION_SEMANTIC_CONTRACT_V1",
            "selection": "FIRST_CAUSAL_POST_RESOLUTION_MATERIAL_15M_MINOR_PROGRESS",
        },
    )


def _unit_qbu_summary(
    unit: EconomicBoundaryUnit,
    episodes: Mapping[str, AnchorEpisode],
    negotiation_identity_by_event_id: Mapping[str, str],
) -> tuple[int | None, tuple[str, ...], bool, str | None]:
    by_identity: dict[str, set[int]] = {}
    for aid in unit.anchor_episode_ids:
        episode = episodes.get(aid)
        if episode is None:
            return None, (), False, "MISSING_MEMBER_EPISODE"
        for use in episode.qualified_uses:
            identity = negotiation_identity_by_event_id.get(use.negotiation_event_id)
            if not identity:
                return None, (), False, f"MISSING_SAME_EVENT_IDENTITY:{use.negotiation_event_id}"
            by_identity.setdefault(identity, set()).add(use.progress_confirmed_at)
    for identity, cutoffs in by_identity.items():
        if len(cutoffs) != 1:
            return None, (), False, f"SAME_EVENT_QBU_CUTOFF_CONFLICT:{identity}"
    if not by_identity:
        return None, (), False, None
    cutoff_by_identity = {identity: next(iter(cutoffs)) for identity, cutoffs in by_identity.items()}
    latest = max(cutoff_by_identity.values())
    all_ids = tuple(sorted(cutoff_by_identity))
    return latest, all_ids, True, None


def _unit_has_active_qualifying_interaction(
    unit: EconomicBoundaryUnit,
    events: tuple[InteractionEvent, ...],
    cutoff: int,
    trend_episode_id: str,
    direction: TrendDirection,
) -> bool:
    members = set(unit.anchor_episode_ids)
    for event in events:
        if event.anchor_episode_id not in members:
            continue
        if event.target_trend_episode_id != trend_episode_id or event.target_direction is not direction:
            continue
        if event.control is not InteractionControl.INTERACTION_ACTIVE:
            continue
        if event.event_reference_boundary is None or event.event_reference_scale is None:
            continue
        if event.started_at is not None and event.started_at <= cutoff:
            return True
    return False


def _depth_class(
    unit: EconomicBoundaryUnit,
    evidence: BoundaryUnitRoleEvidence,
    *,
    corridor: StructuralCorridor | None,
    protected_price: Fraction | None,
    protected_scale: Fraction | None,
    theta_progress: Fraction,
) -> str:
    if (
        not evidence.current_relevant
        or corridor is None
        or protected_price is None
        or protected_scale is None
    ):
        return DEPTH_UNRESOLVED
    if not unit_intersects_corridor(unit, corridor):
        return DEPTH_UNRESOLVED
    if unit_intersects_protected_zone(
        unit,
        protected_price=protected_price,
        protected_scale=protected_scale,
        theta_progress=theta_progress,
    ):
        return DEPTH_PROTECTED_INTERMEDIATE
    return DEPTH_OPERATING_LOCAL


def depth_relation(primary_class: str, candidate_class: str) -> StructuralDepthRelation:
    if DEPTH_UNRESOLVED in (primary_class, candidate_class):
        return StructuralDepthRelation.UNRESOLVED
    if primary_class == candidate_class:
        return StructuralDepthRelation.SAME_LAYER
    if primary_class == DEPTH_OPERATING_LOCAL and candidate_class == DEPTH_PROTECTED_INTERMEDIATE:
        return StructuralDepthRelation.DEEPER
    if primary_class == DEPTH_PROTECTED_INTERMEDIATE and candidate_class == DEPTH_OPERATING_LOCAL:
        return StructuralDepthRelation.SHALLOWER
    return StructuralDepthRelation.UNRESOLVED


def produce_role_state(
    request: Update008Request,
    *,
    episodes: tuple[AnchorEpisode, ...],
    units: tuple[EconomicBoundaryUnit, ...],
    prior_memory: RoleMemory | None,
    conflict_anchor_ids: tuple[str, ...] = (),
) -> tuple[RoleRuntimeOutput, RoleMemory | None]:
    # Engineering-only canonicalization: scientific membership is a set keyed by
    # deterministic unit identity; caller iteration order must not affect output.
    units = tuple(sorted(units, key=lambda u: u.unit_id))
    episode_map = _episode_map(episodes)
    conflict_anchors = set(conflict_anchor_ids)
    base: list[BoundaryUnitRoleEvidence] = []
    qbu_ids_by_unit: dict[str, tuple[str, ...]] = {}
    summary_conflicts: list[str] = []

    for unit in units:
        member_eps = [episode_map.get(aid) for aid in unit.anchor_episode_ids]
        missing = [aid for aid, ep in zip(unit.anchor_episode_ids, member_eps) if ep is None]
        if missing:
            summary_conflicts.append(f"MISSING_EPISODES:{unit.unit_id}:{','.join(missing)}")
        episodes_present = [ep for ep in member_eps if ep is not None]
        at_least_valid = any(
            ep.validity is AnchorValidity.VALID
            and ep.activity in (AnchorActivity.ACTIVE, AnchorActivity.PRESSURED)
            and not ep.terminal_true_break
            and ep.ended_at is None
            for ep in episodes_present
        )
        latest, qbu_ids, has_use, qbu_conflict = _unit_qbu_summary(
            unit, episode_map, request.negotiation_identity_by_event_id
        )
        qbu_ids_by_unit[unit.unit_id] = qbu_ids
        if qbu_conflict:
            summary_conflicts.append(f"{unit.unit_id}:{qbu_conflict}")
        active_interaction = _unit_has_active_qualifying_interaction(
            unit,
            request.events,
            request.information_cutoff,
            request.trend_episode_id,
            request.direction,
        )
        relevant = current_relevance(
            unit,
            corridor=request.corridor,
            has_actual_market_use=has_use,
            active_qualifying_interaction=active_interaction,
        )
        terminal_true_break = bool(episodes_present) and all(ep.terminal_true_break for ep in episodes_present)
        unresolved_conflict = (
            bool(missing)
            or qbu_conflict is not None
            or any(aid in conflict_anchors for aid in unit.anchor_episode_ids)
            or any(
                ep.target_trend_episode_id != request.trend_episode_id
                or ep.target_direction is not request.direction
                for ep in episodes_present
            )
        )
        base.append(
            BoundaryUnitRoleEvidence(
                unit=unit,
                at_least_one_valid_member=at_least_valid,
                current_relevant=relevant,
                latest_qualified_use_cutoff=latest,
                terminal_true_break=terminal_true_break,
                active_qualifying_interaction=active_interaction,
                unresolved_conflict=unresolved_conflict,
                structural_depth_relation_to_primary=StructuralDepthRelation.UNRESOLVED,
            )
        )

    if summary_conflicts:
        return (
            RoleRuntimeOutput(
                state=EvidenceState.CONFLICT,
                units=units,
                role_evidence=tuple(base),
                assignment=None,
                depth_class_by_unit_id=(),
                qbu_identities_by_unit_id=tuple(sorted(qbu_ids_by_unit.items())),
                primary_qbu_identities=(),
                promotion_confirmed_at=None,
                prior_primary_continuity_preserved=False,
                conflict_reasons=tuple(sorted(summary_conflicts)),
                provenance={"producer_semantic_contract_id": "TAC_D3_B5_ROLE_STATE_PRODUCER_SEMANTIC_CONTRACT_V1"},
            ),
            prior_memory,
        )

    preliminary = assign_roles(list(base), structural_suitable_unit_ids=set())
    if preliminary.primary_unit_id is None:
        state = EvidenceState.UNKNOWN if preliminary.transition is RoleTransition.UNRESOLVED or units else EvidenceState.UNKNOWN
        return (
            RoleRuntimeOutput(
                state=state,
                units=units,
                role_evidence=tuple(base),
                assignment=preliminary,
                depth_class_by_unit_id=tuple((e.unit.unit_id, DEPTH_UNRESOLVED) for e in base),
                qbu_identities_by_unit_id=tuple(sorted(qbu_ids_by_unit.items())),
                primary_qbu_identities=(),
                promotion_confirmed_at=None,
                prior_primary_continuity_preserved=False,
                unresolved_reasons=(preliminary.unresolved_reason,) if preliminary.unresolved_reason else ("NO_AUTHORITATIVE_PRIMARY",),
                provenance={"producer_semantic_contract_id": "TAC_D3_B5_ROLE_STATE_PRODUCER_SEMANTIC_CONTRACT_V1"},
            ),
            prior_memory,
        )

    primary_id = preliminary.primary_unit_id
    primary_base = next(e for e in base if e.unit.unit_id == primary_id)
    base_class_by_id = {
        e.unit.unit_id: _depth_class(
            e.unit,
            e,
            corridor=request.corridor,
            protected_price=request.protected_price,
            protected_scale=request.protected_scale,
            theta_progress=request.theta_progress,
        )
        for e in base
    }
    primary_class = base_class_by_id[primary_id]
    final_evidence: list[BoundaryUnitRoleEvidence] = []
    for evidence in base:
        rel = depth_relation(primary_class, base_class_by_id[evidence.unit.unit_id])
        final_evidence.append(replace(evidence, structural_depth_relation_to_primary=rel))

    structural_ids: set[str] = set()
    if request.protected_price is not None and request.protected_scale is not None:
        for evidence in final_evidence:
            if structural_role_eligible(
                evidence,
                protected_price=request.protected_price,
                protected_scale=request.protected_scale,
                theta_progress=request.theta_progress,
            ):
                structural_ids.add(evidence.unit.unit_id)

    eligible_deeper = [
        e for e in final_evidence
        if e.unit.unit_id != primary_id
        and e.at_least_one_valid_member
        and e.current_relevant
        and e.latest_qualified_use_cutoff is not None
        and not e.terminal_true_break
        and not e.unresolved_conflict
        and e.structural_depth_relation_to_primary is StructuralDepthRelation.DEEPER
        and set(e.unit.anchor_episode_ids).isdisjoint(primary_base.unit.anchor_episode_ids)
    ]
    next_deeper_id = eligible_deeper[0].unit.unit_id if len(eligible_deeper) == 1 else None

    current_primary_qbu_ids = qbu_ids_by_unit.get(primary_id, ())
    current_latest = primary_base.latest_qualified_use_cutoff
    assert current_latest is not None

    continuity_preserved = False
    old_episode_ended = False
    takeover_relation = StructuralDepthRelation.UNRESOLVED
    prior_primary_id_for_consumer: str | None = None

    if prior_memory is not None:
        prior_identity_set = set(prior_memory.primary_qbu_identities)
        current_identity_set = set(current_primary_qbu_ids)
        continuity_preserved = bool(prior_identity_set) and prior_identity_set.issubset(current_identity_set)
        if continuity_preserved:
            prior_primary_id_for_consumer = primary_id
        else:
            prior_primary_id_for_consumer = prior_memory.primary_unit_id
            prior_eps = [episode_map.get(aid) for aid in prior_memory.primary_anchor_episode_ids]
            old_episode_ended = bool(prior_eps) and all(
                ep is not None
                and ep.validity is AnchorValidity.TERMINATED
                and ep.ended_at is not None
                for ep in prior_eps
            )
            takeover_relation = depth_relation(prior_memory.primary_depth_class, primary_class)

    assignment = assign_roles(
        final_evidence,
        structural_suitable_unit_ids=structural_ids,
        prior_primary_unit_id=prior_primary_id_for_consumer,
        old_episode_ended=old_episode_ended,
        takeover_depth_relation=takeover_relation,
        next_deeper_unit_id=next_deeper_id,
    )

    promotion_cutoff = (
        current_latest
        if assignment.transition is RoleTransition.PROMOTION
        else None
    )
    unresolved: list[str] = []
    if assignment.transition is RoleTransition.UNRESOLVED:
        unresolved.append(assignment.unresolved_reason or "ROLE_TRANSITION_UNRESOLVED")

    state = EvidenceState.UNKNOWN if unresolved else EvidenceState.TRUE
    next_memory = prior_memory
    if assignment.primary_unit_id is not None and assignment.transition is not RoleTransition.UNRESOLVED:
        unit = next(u for u in units if u.unit_id == assignment.primary_unit_id)
        next_memory = RoleMemory(
            trend_episode_id=request.trend_episode_id,
            primary_unit_id=unit.unit_id,
            primary_anchor_episode_ids=tuple(sorted(unit.anchor_episode_ids)),
            primary_depth_class=base_class_by_id[unit.unit_id],
            primary_qbu_identities=qbu_ids_by_unit.get(unit.unit_id, ()),
            primary_qbu_cutoff=current_latest,
        )

    return (
        RoleRuntimeOutput(
            state=state,
            units=units,
            role_evidence=tuple(final_evidence),
            assignment=assignment,
            depth_class_by_unit_id=tuple(sorted(base_class_by_id.items())),
            qbu_identities_by_unit_id=tuple(sorted(qbu_ids_by_unit.items())),
            primary_qbu_identities=current_primary_qbu_ids,
            promotion_confirmed_at=promotion_cutoff,
            prior_primary_continuity_preserved=continuity_preserved,
            unresolved_reasons=tuple(unresolved),
            provenance={
                "producer_semantic_contract_id": "TAC_D3_B5_ROLE_STATE_PRODUCER_SEMANTIC_CONTRACT_V1",
                "structural_depth_contract_id": "TAC_ECONOMIC_BOUNDARY_UNIT_STRUCTURAL_DEPTH_SEMANTIC_CONTRACT_V1",
                "f9_stage": "UPDATE-008",
            },
        ),
        next_memory,
    )


def produce_update008(
    request: Update008Request,
    *,
    prior_memory: RoleMemory | None = None,
) -> tuple[Update008Output, RoleMemory | None]:
    zones = produce_boundary_contact_zones(request)
    if zones.state is EvidenceState.CONFLICT:
        return (
            Update008Output(
                state=EvidenceState.CONFLICT,
                episodes=request.episodes,
                zones=(),
                units=(),
                role_evidence=(),
                roles=None,
                role_runtime=None,
                produced_qbus=(),
                conflict_lineage_refs=zones.conflict_anchor_ids,
                provenance={"transaction": "NO_PARTIAL_ROLE_STATE_COMMIT"},
            ),
            prior_memory,
        )

    qbus = produce_qbus(request)
    if qbus.state is EvidenceState.CONFLICT:
        return (
            Update008Output(
                state=EvidenceState.CONFLICT,
                episodes=request.episodes,
                zones=(),
                units=(),
                role_evidence=(),
                roles=None,
                role_runtime=None,
                produced_qbus=(),
                conflict_lineage_refs=qbus.conflict_event_ids,
                provenance={"transaction": "NO_PARTIAL_QBU_OR_ROLE_STATE_COMMIT"},
            ),
            prior_memory,
        )

    units = cluster_units(list(zones.zones))
    roles, next_memory = produce_role_state(
        request,
        episodes=qbus.episodes,
        units=units,
        prior_memory=prior_memory,
        conflict_anchor_ids=zones.conflict_anchor_ids,
    )
    if roles.state is EvidenceState.CONFLICT:
        return (
            Update008Output(
                state=EvidenceState.CONFLICT,
                episodes=request.episodes,
                zones=(),
                units=(),
                role_evidence=(),
                roles=None,
                role_runtime=roles,
                produced_qbus=(),
                conflict_lineage_refs=roles.conflict_reasons,
                provenance={"transaction": "NO_PARTIAL_ROLE_STATE_COMMIT"},
            ),
            prior_memory,
        )

    return (
        Update008Output(
            state=roles.state,
            episodes=qbus.episodes,
            zones=zones.zones,
            units=units,
            role_evidence=roles.role_evidence,
            roles=roles.assignment,
            role_runtime=roles,
            produced_qbus=qbus.produced_uses,
            unknown_lineage_refs=tuple(sorted(set(zones.unknown_anchor_ids + qbus.unknown_event_ids))),
            provenance={
                "runtime_contract_id": RUNTIME_CONTRACT_ID,
                "f9_stage": "UPDATE-008",
                "no_update002_backflow": "true",
            },
        ),
        next_memory,
    )


def attribute_entry_boundary(
    *,
    required_anchor_episode_ids: tuple[str, ...],
    units: tuple[EconomicBoundaryUnit, ...],
    episodes: tuple[AnchorEpisode, ...],
    target_trend_episode_id: str,
    direction: TrendDirection,
    information_cutoff: int,
    mechanism: str,
) -> EntryBoundaryProjection:
    required = tuple(sorted(set(required_anchor_episode_ids)))
    if not required:
        return EntryBoundaryProjection(
            EvidenceState.UNKNOWN, None, None, required, "NO_MECHANISM_DEFINING_ANCHOR_LINEAGE",
            {"producer_semantic_contract_id": "TAC_ENTRY_BOUNDARY_ATTRIBUTION_SEMANTIC_CONTRACT_V1", "mechanism": mechanism},
        )
    episode_map = _episode_map(episodes)
    wanted = set(required)
    matches: list[tuple[EconomicBoundaryUnit, EntryBoundaryView]] = []
    for unit in units:
        if not wanted.issubset(set(unit.anchor_episode_ids)):
            continue
        try:
            view = entry_boundary_view(
                unit,
                episode_map,
                target_trend_episode_id=target_trend_episode_id,
                target_direction=direction,
                information_cutoff=information_cutoff,
            )
        except ValueError:
            return EntryBoundaryProjection(
                EvidenceState.CONFLICT, None, None, required, "ENTRY_BOUNDARY_FUTURE_OR_LINEAGE_CONFLICT",
                {"producer_semantic_contract_id": "TAC_ENTRY_BOUNDARY_ATTRIBUTION_SEMANTIC_CONTRACT_V1", "mechanism": mechanism},
            )
        if view is not None and view.valid_active:
            matches.append((unit, view))
    if len(matches) == 1:
        unit, view = matches[0]
        return EntryBoundaryProjection(
            EvidenceState.TRUE,
            unit,
            view,
            required,
            "UNIQUE_CAUSAL_MECHANISM_BOUNDARY_LINEAGE",
            {
                "producer_semantic_contract_id": "TAC_ENTRY_BOUNDARY_ATTRIBUTION_SEMANTIC_CONTRACT_V1",
                "mechanism": mechanism,
                "member_selection": "WHOLE_ECONOMIC_BOUNDARY_UNIT_NO_MEMBER_WINNER",
            },
        )
    if not matches:
        return EntryBoundaryProjection(
            EvidenceState.UNKNOWN, None, None, required, "NO_VALID_ACTIVE_MATCHING_EBU",
            {"producer_semantic_contract_id": "TAC_ENTRY_BOUNDARY_ATTRIBUTION_SEMANTIC_CONTRACT_V1", "mechanism": mechanism},
        )
    return EntryBoundaryProjection(
        EvidenceState.CONFLICT, None, None, required, "MULTIPLE_VALID_ACTIVE_MATCHING_EBU",
        {"producer_semantic_contract_id": "TAC_ENTRY_BOUNDARY_ATTRIBUTION_SEMANTIC_CONTRACT_V1", "mechanism": mechanism},
    )


def _normal_retest_qualifies(event: InteractionEvent, cutoff: int) -> bool:
    return (
        _event_actual_contact(event, cutoff)
        and event.break_state in (BreakState.NONE, BreakState.PROBE)
    )


def _select_adverse_reference(
    *,
    setup_key: str,
    direction: TrendDirection,
    contact_cutoff: int,
    information_cutoff: int,
    canonical_segment_id: str,
    pivots: tuple[StructuralPivot, ...],
) -> tuple[EvidenceState, FixedAdverseReference | None, str]:
    adverse_type = PivotType.LOW if direction is TrendDirection.LONG else PivotType.HIGH
    eligible = [
        p for p in pivots
        if p.timeframe_ms == OBSERVER_TIMEFRAME_MS
        and p.layer is StructuralLayer.MINOR
        and p.pivot_type is adverse_type
        and p.confirmed_at > contact_cutoff
        and p.confirmed_at <= information_cutoff
        and p.canonical_segment_id == canonical_segment_id
        and bool(p.provenance)
    ]
    if not eligible:
        return EvidenceState.UNKNOWN, None, "NO_CAUSAL_ADVERSE_15M_MINOR_PIVOT_YET"
    first_cutoff = min(p.confirmed_at for p in eligible)
    first = {p.pivot_id: p for p in eligible if p.confirmed_at == first_cutoff}
    if len(first) != 1:
        return EvidenceState.CONFLICT, None, "MULTIPLE_FIRST_ADVERSE_PIVOTS"
    pivot = next(iter(first.values()))
    return (
        EvidenceState.TRUE,
        FixedAdverseReference(
            setup_key=setup_key,
            pivot_id=pivot.pivot_id,
            confirmed_at=pivot.confirmed_at,
            canonical_segment_id=pivot.canonical_segment_id,
            direction=direction,
        ),
        "FIRST_CAUSAL_ADVERSE_15M_MINOR_FIXED",
    )


def produce_normal_retest(
    *,
    setup_key: str,
    information_cutoff: int,
    trend_episode_id: str,
    direction: TrendDirection,
    interaction: InteractionEvent,
    entry_boundary: EntryBoundaryProjection,
    pivots: tuple[StructuralPivot, ...],
    canonical_segment_id: str,
    setup_lineage: tuple[str, ...],
    existing_fixed_reference: FixedAdverseReference | None = None,
    local_control_regain: LocalTrendControlRegainEvidence | None = None,
) -> NormalRetestProjection:
    provenance = {
        "producer_semantic_contract_id": "TAC_NORMAL_RETEST_BASE_EVIDENCE_SEMANTIC_CONTRACT_V1",
        "setup_key": setup_key,
    }
    if entry_boundary.state is EvidenceState.CONFLICT:
        return NormalRetestProjection(EvidenceState.CONFLICT, None, existing_fixed_reference, "ENTRY_BOUNDARY_CONFLICT", provenance)
    if entry_boundary.state is not EvidenceState.TRUE or entry_boundary.view is None:
        return NormalRetestProjection(EvidenceState.UNKNOWN, None, existing_fixed_reference, "ENTRY_BOUNDARY_UNKNOWN", provenance)
    if (
        interaction.anchor_episode_id not in entry_boundary.view.member_anchor_episode_ids
        or interaction.target_trend_episode_id != trend_episode_id
        or interaction.target_direction is not direction
    ):
        return NormalRetestProjection(EvidenceState.CONFLICT, None, existing_fixed_reference, "INTERACTION_ENTRY_BOUNDARY_LINEAGE_CONFLICT", provenance)
    for value in (interaction.started_at, interaction.armed_at, interaction.approach_lineage_started_at, interaction.resolved_at):
        if value is not None and value > information_cutoff:
            return NormalRetestProjection(EvidenceState.CONFLICT, None, existing_fixed_reference, "FUTURE_INTERACTION_STATE", provenance)

    if not _normal_retest_qualifies(interaction, information_cutoff):
        evidence = NormalRetestEvidence(
            interaction=interaction,
            qualifying_retest_or_probe=False,
            adverse_structural_reference_fixed=False,
            local_control_regain=None,
            setup_lineage=setup_lineage,
            provenance={**provenance, "qualifying": "FALSE_APPROACH_OR_NON_NORMAL_BREAK_STATE"},
        )
        return NormalRetestProjection(EvidenceState.FALSE, evidence, existing_fixed_reference, "NOT_QUALIFYING_RETEST_OR_PROBE", provenance)

    if interaction.started_at is None:
        return NormalRetestProjection(EvidenceState.UNKNOWN, None, existing_fixed_reference, "CONTACT_CUTOFF_UNKNOWN", provenance)

    fixed = existing_fixed_reference
    if fixed is not None:
        if (
            fixed.setup_key != setup_key
            or fixed.direction is not direction
            or fixed.canonical_segment_id != canonical_segment_id
            or fixed.confirmed_at > information_cutoff
        ):
            return NormalRetestProjection(EvidenceState.CONFLICT, None, fixed, "FIXED_ADVERSE_REFERENCE_CONFLICT", provenance)
    else:
        state, fixed, reason = _select_adverse_reference(
            setup_key=setup_key,
            direction=direction,
            contact_cutoff=interaction.started_at,
            information_cutoff=information_cutoff,
            canonical_segment_id=canonical_segment_id,
            pivots=pivots,
        )
        if state is not EvidenceState.TRUE or fixed is None:
            return NormalRetestProjection(state, None, None, reason, provenance)

    evidence = NormalRetestEvidence(
        interaction=interaction,
        qualifying_retest_or_probe=True,
        adverse_structural_reference_fixed=True,
        local_control_regain=local_control_regain,
        setup_lineage=setup_lineage,
        provenance={
            **provenance,
            "qualifying": "ACTUAL_B3_TEST_CONTACT_BREAK_NONE_OR_PROBE",
            "adverse_reference_pivot_id": fixed.pivot_id,
            "adverse_reference_confirmed_at": str(fixed.confirmed_at),
            "adverse_reference_nonrolling": "true",
        },
    )
    return NormalRetestProjection(EvidenceState.TRUE, evidence, fixed, "NORMAL_RETEST_BASE_EVIDENCE_AUTHORITATIVE", provenance)


def _depth_class_map(role_runtime: RoleRuntimeOutput) -> dict[str, str]:
    return dict(role_runtime.depth_class_by_unit_id)


def produce_deep_takeover(request: DeepTakeoverRequest) -> DeepTakeoverProjection:
    provenance = {
        "producer_semantic_contract_id": "TAC_DEEP_STRUCTURE_TAKEOVER_BASE_EVIDENCE_SEMANTIC_CONTRACT_V1",
        "opportunity_id": request.opportunity_id,
        "market_event_id": request.market_event_id,
    }
    if request.deeper_entry_boundary.state is EvidenceState.CONFLICT:
        return DeepTakeoverProjection(EvidenceState.CONFLICT, None, "DEEPER_ENTRY_BOUNDARY_CONFLICT", provenance)
    if request.deeper_entry_boundary.state is not EvidenceState.TRUE or request.deeper_entry_boundary.unit is None:
        return DeepTakeoverProjection(EvidenceState.UNKNOWN, None, "DEEPER_ENTRY_BOUNDARY_UNKNOWN", provenance)
    if request.same_market_event_identity_authoritative is not True:
        return DeepTakeoverProjection(EvidenceState.CONFLICT, None, "MARKET_EVENT_IDENTITY_NOT_AUTHORITATIVE", provenance)

    event = request.deeper_interaction
    if event.target_trend_episode_id != request.trend_episode_id or event.target_direction is not request.direction:
        return DeepTakeoverProjection(EvidenceState.CONFLICT, None, "DEEPER_INTERACTION_LINEAGE_CONFLICT", provenance)
    if event.anchor_episode_id not in request.deeper_entry_boundary.unit.anchor_episode_ids:
        return DeepTakeoverProjection(EvidenceState.CONFLICT, None, "DEEPER_INTERACTION_ENTRY_BOUNDARY_CONFLICT", provenance)
    if not _event_actual_contact(event, request.information_cutoff):
        return DeepTakeoverProjection(EvidenceState.FALSE, DeepStructureTakeoverEvidence(
            shallow_operating_defense_no_longer_completes_setup=False,
            deeper_boundary_independent=False,
            deeper_interaction=event,
            local_control_regain=None,
            role_transition=RoleTransition.NONE,
            promotion_confirmed_at=None,
            setup_lineage=request.setup_lineage,
            provenance={**provenance, "qualifying_deeper_contact": "false"},
        ), "DEEPER_APPROACH_ONLY_OR_NO_ACTUAL_CONTACT", provenance)
    if event.break_state is BreakState.TRUE_BREAK or event.terminal and event.resolution is InteractionResolution.RESOLVED_WRONG_SIDE:
        return DeepTakeoverProjection(EvidenceState.FALSE, DeepStructureTakeoverEvidence(
            shallow_operating_defense_no_longer_completes_setup=False,
            deeper_boundary_independent=False,
            deeper_interaction=event,
            local_control_regain=None,
            role_transition=RoleTransition.NONE,
            promotion_confirmed_at=None,
            setup_lineage=request.setup_lineage,
            provenance={**provenance, "deeper_boundary_valid": "false_terminal_true_break"},
        ), "DEEPER_BOUNDARY_TERMINALLY_INVALIDATED", provenance)

    classes = _depth_class_map(request.role_runtime)
    shallow_class = classes.get(request.shallow_unit.unit_id, DEPTH_UNRESOLVED)
    deeper_unit = request.deeper_entry_boundary.unit
    deeper_class = classes.get(deeper_unit.unit_id, DEPTH_UNRESOLVED)
    relation = depth_relation(shallow_class, deeper_class)
    if relation is StructuralDepthRelation.UNRESOLVED:
        return DeepTakeoverProjection(EvidenceState.UNKNOWN, None, "DEEPER_STRUCTURAL_DEPTH_UNRESOLVED", provenance)

    disjoint = set(request.shallow_unit.anchor_episode_ids).isdisjoint(deeper_unit.anchor_episode_ids)
    independent = (
        deeper_unit.unit_id != request.shallow_unit.unit_id
        and disjoint
        and relation is StructuralDepthRelation.DEEPER
    )
    if not independent:
        evidence = DeepStructureTakeoverEvidence(
            shallow_operating_defense_no_longer_completes_setup=False,
            deeper_boundary_independent=False,
            deeper_interaction=event,
            local_control_regain=None,
            role_transition=request.role_runtime.assignment.transition if request.role_runtime.assignment else RoleTransition.UNRESOLVED,
            promotion_confirmed_at=None,
            setup_lineage=request.setup_lineage,
            provenance={**provenance, "structural_depth_relation": relation.value, "independent": "false"},
        )
        return DeepTakeoverProjection(EvidenceState.FALSE, evidence, "DEEPER_BOUNDARY_NOT_INDEPENDENT_DEEPER_EBU", provenance)

    contact_cutoff = event.started_at
    assert contact_cutoff is not None
    shallow_already_completed = (
        request.shallow_behavior_confirmation_cutoff is not None
        and request.shallow_behavior_confirmation_cutoff <= contact_cutoff
    )
    shallow_no_longer = not shallow_already_completed

    assignment = request.role_runtime.assignment
    role_transition = assignment.transition if assignment is not None else RoleTransition.UNRESOLVED
    promotion_cutoff = request.role_runtime.promotion_confirmed_at if role_transition is RoleTransition.PROMOTION else None
    evidence = DeepStructureTakeoverEvidence(
        shallow_operating_defense_no_longer_completes_setup=shallow_no_longer,
        deeper_boundary_independent=True,
        deeper_interaction=event,
        local_control_regain=request.local_control_regain,
        role_transition=role_transition,
        promotion_confirmed_at=promotion_cutoff,
        setup_lineage=request.setup_lineage,
        provenance={
            **provenance,
            "structural_depth_relation": StructuralDepthRelation.DEEPER.value,
            "independent": "true",
            "shallow_completed_before_deeper_contact": str(shallow_already_completed).lower(),
            "promotion_source": "B5_ROLE_RUNTIME_ONLY",
        },
    )
    return DeepTakeoverProjection(
        EvidenceState.TRUE if shallow_no_longer else EvidenceState.FALSE,
        evidence,
        "DEEP_TAKEOVER_BASE_EVIDENCE_AUTHORITATIVE" if shallow_no_longer else "SHALLOW_SETUP_COMPLETED_FIRST",
        provenance,
    )


def produce_trend_establishment_watch(
    *,
    record: TrendEstablishmentRecord | None,
    information_cutoff: int,
) -> TrendWatchProjection:
    provenance = {"producer_semantic_contract_id": "TAC_TREND_ESTABLISHMENT_WATCH_SEMANTIC_DISPOSITION_V1"}
    if record is None:
        evidence = TrendEstablishmentWatchEvidence(False, (), (), {**provenance, "observed": "false_no_episode_creation"})
        return TrendWatchProjection(EvidenceState.FALSE, evidence, "NO_TREND_EPISODE_CREATION", provenance)
    trend = record.trend
    if trend.episode_id is None or trend.episode_start_cutoff is None:
        return TrendWatchProjection(EvidenceState.UNKNOWN, None, "TREND_EPISODE_CREATION_PROVENANCE_MISSING", provenance)
    if record.creation_cutoff != trend.episode_start_cutoff:
        return TrendWatchProjection(EvidenceState.CONFLICT, None, "TREND_CREATION_CUTOFF_CONFLICT", provenance)
    if not record.newest_intermediate_pivot_id or not record.source_event_ids:
        return TrendWatchProjection(EvidenceState.UNKNOWN, None, "ESTABLISHMENT_SOURCE_PROVENANCE_MISSING", provenance)
    if record.creation_cutoff > information_cutoff:
        return TrendWatchProjection(EvidenceState.CONFLICT, None, "FUTURE_TREND_CREATION", provenance)
    observed = information_cutoff == record.creation_cutoff
    evidence = TrendEstablishmentWatchEvidence(
        observed=observed,
        setup_lineage=(trend.episode_id,),
        source_event_ids=record.source_event_ids,
        provenance={
            **provenance,
            **dict(record.provenance),
            "newest_intermediate_pivot_id": record.newest_intermediate_pivot_id,
            "creation_cutoff": str(record.creation_cutoff),
            "watch_only": "true",
            "entry_ready": "false",
        },
    )
    return TrendWatchProjection(EvidenceState.TRUE if observed else EvidenceState.FALSE, evidence, "GENESIS_CUTOFF" if observed else "LATER_ACTIVE_TREND_CUTOFF", provenance)


def wire_false_break_reclaim(
    interaction: InteractionEvent,
    *,
    setup_lineage: tuple[str, ...],
) -> FalseBreakReclaimEvidence:
    return FalseBreakReclaimEvidence(
        interaction=interaction,
        setup_lineage=setup_lineage,
        provenance={"disposition": "ALREADY_MECHANICALLY_CLOSED_NO_NEW_SEMANTIC_REQUIRED"},
    )


def wire_platform_reexpansion(
    platform: PlatformState,
    *,
    current_close: Fraction,
    target_trend_episode_id: str,
    direction: TrendDirection,
    setup_lineage: tuple[str, ...],
) -> PlatformReexpansionEvidence:
    return PlatformReexpansionEvidence(
        platform=platform,
        current_close=current_close,
        target_trend_episode_id=target_trend_episode_id,
        direction=direction,
        setup_lineage=setup_lineage,
        provenance={"disposition": "ALREADY_MECHANICALLY_CLOSED_NO_NEW_SEMANTIC_REQUIRED"},
    )


class AuthoritativeD3B5D4BaseRuntimeV1:
    """Small transactional producer runtime; no packet assembly and no market I/O."""

    def __init__(self) -> None:
        self._role_memory: dict[str, RoleMemory] = {}
        self._fixed_adverse: dict[str, FixedAdverseReference] = {}
        self._tx_input_digest: dict[str, str] = {}
        self._tx_result: dict[str, Any] = {}

    def _guard_tx(self, tx_id: str, payload: Any) -> tuple[bool, Any | None]:
        d = digest(payload)
        old = self._tx_input_digest.get(tx_id)
        if old is None:
            return False, None
        if old != d:
            raise RuntimeProducerBlock("SAME_TX_INPUT_MISMATCH")
        return True, self._tx_result[tx_id]

    def _commit_tx(self, tx_id: str, payload: Any, result: Any) -> Any:
        self._tx_input_digest[tx_id] = digest(payload)
        self._tx_result[tx_id] = result
        return result

    def process_update008(self, tx_id: str, request: Update008Request) -> Update008Output:
        replay, result = self._guard_tx(tx_id, request)
        if replay:
            return result
        prior = self._role_memory.get(request.trend_episode_id)
        output, next_memory = produce_update008(request, prior_memory=prior)
        if output.state is not EvidenceState.CONFLICT and next_memory is not None:
            self._role_memory[request.trend_episode_id] = next_memory
        return self._commit_tx(tx_id, request, output)

    def process_normal_retest(
        self,
        tx_id: str,
        *,
        setup_key: str,
        information_cutoff: int,
        trend_episode_id: str,
        direction: TrendDirection,
        interaction: InteractionEvent,
        entry_boundary: EntryBoundaryProjection,
        pivots: tuple[StructuralPivot, ...],
        canonical_segment_id: str,
        setup_lineage: tuple[str, ...],
        local_control_regain: LocalTrendControlRegainEvidence | None = None,
    ) -> NormalRetestProjection:
        payload = (
            setup_key, information_cutoff, trend_episode_id, direction, interaction,
            entry_boundary, pivots, canonical_segment_id, setup_lineage, local_control_regain,
        )
        replay, result = self._guard_tx(tx_id, payload)
        if replay:
            return result
        existing = self._fixed_adverse.get(setup_key)
        projection = produce_normal_retest(
            setup_key=setup_key,
            information_cutoff=information_cutoff,
            trend_episode_id=trend_episode_id,
            direction=direction,
            interaction=interaction,
            entry_boundary=entry_boundary,
            pivots=pivots,
            canonical_segment_id=canonical_segment_id,
            setup_lineage=setup_lineage,
            existing_fixed_reference=existing,
            local_control_regain=local_control_regain,
        )
        if projection.state is EvidenceState.TRUE and projection.adverse_reference is not None and existing is None:
            self._fixed_adverse[setup_key] = projection.adverse_reference
        return self._commit_tx(tx_id, payload, projection)

    def export_state(self) -> Mapping[str, Any]:
        return {
            "schema": "AUTHORITATIVE_D3_B5_D4_BASE_RUNTIME_STATE_V1",
            "role_memory": _encode(self._role_memory),
            "fixed_adverse": _encode(self._fixed_adverse),
            "tx_input_digest": dict(sorted(self._tx_input_digest.items())),
            "tx_result": _encode(self._tx_result),
        }

    @classmethod
    def restore_state(cls, state: Mapping[str, Any]) -> "AuthoritativeD3B5D4BaseRuntimeV1":
        if state.get("schema") != "AUTHORITATIVE_D3_B5_D4_BASE_RUNTIME_STATE_V1":
            raise RuntimeProducerBlock("RUNTIME_STATE_SCHEMA_MISMATCH")
        out = cls()
        role_memory = _decode(state.get("role_memory", {"$map": []}))
        fixed = _decode(state.get("fixed_adverse", {"$map": []}))
        tx_result = _decode(state.get("tx_result", {"$map": []}))
        out._role_memory = dict(role_memory)
        out._fixed_adverse = dict(fixed)
        out._tx_input_digest = {str(k): str(v) for k, v in dict(state.get("tx_input_digest", {})).items()}
        out._tx_result = dict(tx_result)
        return out
