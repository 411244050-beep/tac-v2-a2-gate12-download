# --- EXACT SCIENCE NAMESPACE TAC_BASE_ ---
from dataclasses import dataclass, field, fields, is_dataclass, replace
from enum import Enum
from fractions import Fraction
from hashlib import sha256
import importlib
import json
from typing import Any, Mapping
TAC_BASE_SEMANTIC_FREEZE_TERMINAL_BLOB = 'fb03beb4c9559892f6d3d6f4b3602ef7f0e6da4b'
TAC_BASE_SEMANTIC_FREEZE_MANIFEST_BLOB = '09f1d5cc844f5943bacd2a06f8a319f30ab803dd'
TAC_BASE_RUNTIME_CONTRACT_ID = 'AUTHORITATIVE_D3_B5_D4_BASE_RUNTIME_PRODUCERS_V1'
TAC_BASE_OBSERVER_TIMEFRAME_MS = 15 * 60 * 1000
TAC_BASE_DEPTH_OPERATING_LOCAL = 'OPERATING_LOCAL'
TAC_BASE_DEPTH_PROTECTED_INTERMEDIATE = 'PROTECTED_INTERMEDIATE'
TAC_BASE_DEPTH_UNRESOLVED = 'UNRESOLVED'

class TAC_BASE_RuntimeProducerBlock(RuntimeError):
    pass

def TAC_BASE__encode(value: Any) -> Any:
    if isinstance(value, Fraction):
        return {'$fraction': [value.numerator, value.denominator]}
    if isinstance(value, Enum):
        return {'$enum': [value.__class__.__module__, value.__class__.__qualname__, value.value]}
    if isinstance(value, MappingProxyType):
        value = dict(value)
    if is_dataclass(value) and (not isinstance(value, type)):
        return {'$dataclass': [value.__class__.__module__, value.__class__.__qualname__], 'fields': {f.name: TAC_BASE__encode(getattr(value, f.name)) for f in fields(value)}}
    if isinstance(value, Mapping):
        return {'$map': [[str(k), TAC_BASE__encode(v)] for k, v in sorted(value.items(), key=lambda kv: str(kv[0]))]}
    if isinstance(value, tuple):
        return {'$tuple': [TAC_BASE__encode(x) for x in value]}
    if isinstance(value, list):
        return {'$list': [TAC_BASE__encode(x) for x in value]}
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    raise TypeError(f'UNSUPPORTED_SERIALIZATION_TYPE:{type(value)!r}')

def TAC_BASE__resolve(module: str, qualname: str) -> Any:
    obj: Any = importlib.import_module(module)
    for part in qualname.split('.'):
        obj = getattr(obj, part)
    return obj

def TAC_BASE__decode(value: Any) -> Any:
    if isinstance(value, list):
        return [TAC_BASE__decode(x) for x in value]
    if not isinstance(value, dict):
        return value
    if '$fraction' in value:
        return Fraction(*value['$fraction'])
    if '$enum' in value:
        module, qualname, raw = value['$enum']
        return TAC_BASE__resolve(module, qualname)(raw)
    if '$tuple' in value:
        return tuple((TAC_BASE__decode(x) for x in value['$tuple']))
    if '$list' in value:
        return [TAC_BASE__decode(x) for x in value['$list']]
    if '$map' in value:
        return {k: TAC_BASE__decode(v) for k, v in value['$map']}
    if '$dataclass' in value:
        module, qualname = value['$dataclass']
        cls = TAC_BASE__resolve(module, qualname)
        return cls(**{k: TAC_BASE__decode(v) for k, v in value['fields'].items()})
    return {k: TAC_BASE__decode(v) for k, v in value.items()}

def TAC_BASE_exact_json(value: Any) -> str:
    return json.dumps(TAC_BASE__encode(value), sort_keys=True, separators=(',', ':'), ensure_ascii=False)

def TAC_BASE_digest(value: Any) -> str:
    return sha256(TAC_BASE_exact_json(value).encode()).hexdigest()

@dataclass(frozen=True)
class TAC_BASE_ProgressLineageEvidence:
    event_id: str
    progress: TrendSideMinorProgressEvidence
    target_trend_episode_id: str
    direction: TrendDirection
    canonical_segment_id: str
    continuity_intact: bool
    provenance: Mapping[str, str] = field(default_factory=dict)

@dataclass(frozen=True)
class TAC_BASE_BoundaryZoneBatch:
    state: EvidenceState
    zones: tuple[BoundaryContactZone, ...]
    unavailable_anchor_ids: tuple[str, ...] = ()
    unknown_anchor_ids: tuple[str, ...] = ()
    conflict_anchor_ids: tuple[str, ...] = ()
    provenance: Mapping[str, str] = field(default_factory=dict)

@dataclass(frozen=True)
class TAC_BASE_QBUProjection:
    state: EvidenceState
    episodes: tuple[AnchorEpisode, ...]
    produced_uses: tuple[QualifiedBoundaryUse, ...]
    unknown_event_ids: tuple[str, ...] = ()
    conflict_event_ids: tuple[str, ...] = ()
    provenance: Mapping[str, str] = field(default_factory=dict)

@dataclass(frozen=True)
class TAC_BASE_RoleMemory:
    trend_episode_id: str
    primary_unit_id: str
    primary_anchor_episode_ids: tuple[str, ...]
    primary_depth_class: str
    primary_qbu_identities: tuple[str, ...]
    primary_qbu_cutoff: int

@dataclass(frozen=True)
class TAC_BASE_RoleRuntimeOutput:
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
class TAC_BASE_Update008Request:
    information_cutoff: int
    trend_episode_id: str
    direction: TrendDirection
    snapshots: tuple[CausalBoundarySnapshot, ...]
    candidates: tuple[MathematicalBoundaryCandidate, ...]
    episodes: tuple[AnchorEpisode, ...]
    events: tuple[InteractionEvent, ...]
    progress_evidence: tuple[TAC_BASE_ProgressLineageEvidence, ...]
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
class TAC_BASE_Update008Output:
    state: EvidenceState
    episodes: tuple[AnchorEpisode, ...]
    zones: tuple[BoundaryContactZone, ...]
    units: tuple[EconomicBoundaryUnit, ...]
    role_evidence: tuple[BoundaryUnitRoleEvidence, ...]
    roles: RoleAssignment | None
    role_runtime: TAC_BASE_RoleRuntimeOutput | None
    produced_qbus: tuple[QualifiedBoundaryUse, ...]
    unknown_lineage_refs: tuple[str, ...] = ()
    conflict_lineage_refs: tuple[str, ...] = ()
    provenance: Mapping[str, str] = field(default_factory=dict)

@dataclass(frozen=True)
class TAC_BASE_EntryBoundaryProjection:
    state: EvidenceState
    unit: EconomicBoundaryUnit | None
    view: EntryBoundaryView | None
    required_anchor_episode_ids: tuple[str, ...]
    reason: str
    provenance: Mapping[str, str] = field(default_factory=dict)

@dataclass(frozen=True)
class TAC_BASE_FixedAdverseReference:
    setup_key: str
    pivot_id: str
    confirmed_at: int
    canonical_segment_id: str
    direction: TrendDirection

@dataclass(frozen=True)
class TAC_BASE_NormalRetestProjection:
    state: EvidenceState
    evidence: NormalRetestEvidence | None
    adverse_reference: TAC_BASE_FixedAdverseReference | None
    reason: str
    provenance: Mapping[str, str] = field(default_factory=dict)

@dataclass(frozen=True)
class TAC_BASE_DeepTakeoverRequest:
    information_cutoff: int
    trend_episode_id: str
    direction: TrendDirection
    opportunity_id: str
    market_event_id: str
    shallow_unit: EconomicBoundaryUnit
    deeper_entry_boundary: TAC_BASE_EntryBoundaryProjection
    deeper_interaction: InteractionEvent
    role_runtime: TAC_BASE_RoleRuntimeOutput
    shallow_behavior_confirmation_cutoff: int | None
    same_market_event_identity_authoritative: bool
    local_control_regain: LocalTrendControlRegainEvidence | None
    setup_lineage: tuple[str, ...]
    provenance: Mapping[str, str] = field(default_factory=dict)

@dataclass(frozen=True)
class TAC_BASE_DeepTakeoverProjection:
    state: EvidenceState
    evidence: DeepStructureTakeoverEvidence | None
    reason: str
    provenance: Mapping[str, str] = field(default_factory=dict)

@dataclass(frozen=True)
class TAC_BASE_TrendEstablishmentRecord:
    trend: TrendEpisodeState
    creation_cutoff: int
    newest_intermediate_pivot_id: str
    source_event_ids: tuple[str, ...]
    provenance: Mapping[str, str] = field(default_factory=dict)

@dataclass(frozen=True)
class TAC_BASE_TrendWatchProjection:
    state: EvidenceState
    evidence: TrendEstablishmentWatchEvidence | None
    reason: str
    provenance: Mapping[str, str] = field(default_factory=dict)

def TAC_BASE__episode_map(episodes: tuple[AnchorEpisode, ...]) -> dict[str, AnchorEpisode]:
    return {ep.anchor_episode_id: ep for ep in episodes}

def TAC_BASE__event_map(events: tuple[InteractionEvent, ...]) -> dict[str, InteractionEvent]:
    return {ev.event_id: ev for ev in events}

def TAC_BASE__candidate_map(candidates: tuple[MathematicalBoundaryCandidate, ...]) -> dict[str, MathematicalBoundaryCandidate]:
    return {c.candidate_id: c for c in candidates}

def TAC_BASE__direction_ok(direction: TrendDirection) -> bool:
    return direction in (TrendDirection.LONG, TrendDirection.SHORT)

def TAC_BASE__event_actual_contact(event: InteractionEvent, cutoff: int) -> bool:
    if event.control not in (InteractionControl.INTERACTION_ACTIVE, InteractionControl.RESOLVED):
        return False
    if event.event_reference_boundary is None or event.event_reference_scale is None:
        return False
    if event.started_at is None or event.started_at > cutoff:
        return False
    return True

def TAC_BASE_produce_boundary_contact_zones(request: TAC_BASE_Update008Request) -> TAC_BASE_BoundaryZoneBatch:
    if not TAC_BASE__direction_ok(request.direction):
        return TAC_BASE_BoundaryZoneBatch(EvidenceState.CONFLICT, (), conflict_anchor_ids=('INVALID_DIRECTION',))
    candidates = TAC_BASE__candidate_map(request.candidates)
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
        snaps = [s for s in snapshots_by_anchor.get(episode.anchor_episode_id, ()) if s.candidate_id == candidate.candidate_id]
        if not snaps:
            unknown.append(episode.anchor_episode_id)
            continue
        latest_at = max((s.available_at for s in snaps))
        latest_by_id = {s.snapshot_id: s for s in snaps if s.available_at == latest_at}
        if len(latest_by_id) != 1:
            conflict.append(episode.anchor_episode_id)
            continue
        snap = next(iter(latest_by_id.values()))
        if snap.target_trend_episode_id != request.trend_episode_id or snap.target_direction is not request.direction or snap.anchor_episode_id != episode.anchor_episode_id or (snap.candidate_id != episode.candidate_id):
            conflict.append(episode.anchor_episode_id)
            continue
        if request.direction is TrendDirection.LONG:
            lower = snap.boundary
            upper = snap.boundary + request.theta_test * snap.source_scale
        else:
            lower = snap.boundary - request.theta_test * snap.source_scale
            upper = snap.boundary
        zones.append(BoundaryContactZone(zone_id=deterministic_id('D3-BCZ-V1', snap.snapshot_id, episode.anchor_episode_id, str(request.information_cutoff)), anchor_episode_id=episode.anchor_episode_id, lower=lower, upper=upper, information_cutoff=request.information_cutoff, provenance={'producer_semantic_contract_id': 'TAC_BOUNDARY_CONTACT_ZONE_QBU_RUNTIME_PROJECTION_SEMANTIC_CONTRACT_V1', 'snapshot_id': snap.snapshot_id, 'candidate_id': snap.candidate_id, 'target_trend_episode_id': snap.target_trend_episode_id, 'direction': snap.target_direction.value, 'source_timeframe_ms': str(snap.source_timeframe_ms), 'source_segment_id': snap.source_segment_id, 'boundary': str(snap.boundary), 'source_scale': str(snap.source_scale), 'theta_test': str(request.theta_test), 'information_cutoff': str(request.information_cutoff), 'geometry': 'DIRECTION_AWARE_B3_TEST_BAND'}))
    state = EvidenceState.CONFLICT if conflict else EvidenceState.TRUE if zones else EvidenceState.UNKNOWN
    return TAC_BASE_BoundaryZoneBatch(state=state, zones=tuple(sorted(zones, key=lambda z: (z.lower, z.upper, z.anchor_episode_id, z.zone_id))), unavailable_anchor_ids=tuple(sorted(set(unavailable))), unknown_anchor_ids=tuple(sorted(set(unknown))), conflict_anchor_ids=tuple(sorted(set(conflict))), provenance={'producer_semantic_contract_id': 'TAC_BOUNDARY_CONTACT_ZONE_QBU_RUNTIME_PROJECTION_SEMANTIC_CONTRACT_V1', 'f9_stage': 'UPDATE-008', 'historical_union': 'false'})

def TAC_BASE__progress_for_event(event: InteractionEvent, episode: AnchorEpisode, request: TAC_BASE_Update008Request) -> tuple[EvidenceState, TrendSideMinorProgressEvidence | None, str]:
    expected_segment = request.canonical_segment_id_by_anchor_episode_id.get(episode.anchor_episode_id)
    records = [p for p in request.progress_evidence if p.event_id == event.event_id]
    for rec in records:
        if rec.target_trend_episode_id != event.target_trend_episode_id or rec.direction is not event.target_direction or rec.continuity_intact is not True or (expected_segment is None) or (rec.canonical_segment_id != expected_segment):
            return (EvidenceState.CONFLICT, None, 'PROGRESS_LINEAGE_CONFLICT')
    eligible = [rec.progress for rec in records if event.resolved_at is not None and rec.progress.confirmed_at > event.resolved_at and (rec.progress.confirmed_at <= request.information_cutoff) and rec.progress.material_progress and (rec.progress.timeframe_ms == TAC_BASE_OBSERVER_TIMEFRAME_MS) and (rec.progress.layer == 'MINOR')]
    if not eligible:
        return (EvidenceState.UNKNOWN, None, 'NO_CAUSAL_POST_RESOLUTION_PROGRESS')
    first_cutoff = min((p.confirmed_at for p in eligible))
    first = {p.pivot_id: p for p in eligible if p.confirmed_at == first_cutoff}
    if len(first) != 1:
        return (EvidenceState.CONFLICT, None, 'MULTIPLE_FIRST_PROGRESS_PIVOTS')
    return (EvidenceState.TRUE, next(iter(first.values())), 'FIRST_CAUSAL_PROGRESS')

def TAC_BASE_produce_qbus(request: TAC_BASE_Update008Request) -> TAC_BASE_QBUProjection:
    episodes = TAC_BASE__episode_map(request.episodes)
    events = TAC_BASE__event_map(request.events)
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
            if event.anchor_episode_id != episode.anchor_episode_id or event.target_trend_episode_id != episode.target_trend_episode_id or event.target_direction is not episode.target_direction:
                conflict.append(event_id)
                continue
            if event.resolution is not InteractionResolution.RESOLVED_CORRECT_SIDE or event.break_state is BreakState.TRUE_BREAK:
                continue
            if event.resolved_at is None or event.resolved_at > request.information_cutoff:
                unknown.append(event_id)
                continue
            existing = [u for u in episode.qualified_uses if u.negotiation_event_id == event.event_id]
            state, progress, reason = TAC_BASE__progress_for_event(event, episode, request)
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
    return TAC_BASE_QBUProjection(state=state, episodes=tuple(sorted(episodes.values(), key=lambda ep: ep.anchor_episode_id)), produced_uses=tuple(sorted(produced, key=lambda u: (u.progress_confirmed_at, u.use_id))), unknown_event_ids=tuple(sorted(set(unknown))), conflict_event_ids=tuple(sorted(set(conflict))), provenance={'producer_semantic_contract_id': 'TAC_BOUNDARY_CONTACT_ZONE_QBU_RUNTIME_PROJECTION_SEMANTIC_CONTRACT_V1', 'selection': 'FIRST_CAUSAL_POST_RESOLUTION_MATERIAL_15M_MINOR_PROGRESS'})

def TAC_BASE__unit_qbu_summary(unit: EconomicBoundaryUnit, episodes: Mapping[str, AnchorEpisode], negotiation_identity_by_event_id: Mapping[str, str]) -> tuple[int | None, tuple[str, ...], bool, str | None]:
    by_identity: dict[str, set[int]] = {}
    for aid in unit.anchor_episode_ids:
        episode = episodes.get(aid)
        if episode is None:
            return (None, (), False, 'MISSING_MEMBER_EPISODE')
        for use in episode.qualified_uses:
            identity = negotiation_identity_by_event_id.get(use.negotiation_event_id)
            if not identity:
                return (None, (), False, f'MISSING_SAME_EVENT_IDENTITY:{use.negotiation_event_id}')
            by_identity.setdefault(identity, set()).add(use.progress_confirmed_at)
    for identity, cutoffs in by_identity.items():
        if len(cutoffs) != 1:
            return (None, (), False, f'SAME_EVENT_QBU_CUTOFF_CONFLICT:{identity}')
    if not by_identity:
        return (None, (), False, None)
    cutoff_by_identity = {identity: next(iter(cutoffs)) for identity, cutoffs in by_identity.items()}
    latest = max(cutoff_by_identity.values())
    all_ids = tuple(sorted(cutoff_by_identity))
    return (latest, all_ids, True, None)

def TAC_BASE__unit_has_active_qualifying_interaction(unit: EconomicBoundaryUnit, events: tuple[InteractionEvent, ...], cutoff: int, trend_episode_id: str, direction: TrendDirection) -> bool:
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

def TAC_BASE__depth_class(unit: EconomicBoundaryUnit, evidence: BoundaryUnitRoleEvidence, *, corridor: StructuralCorridor | None, protected_price: Fraction | None, protected_scale: Fraction | None, theta_progress: Fraction) -> str:
    if not evidence.current_relevant or corridor is None or protected_price is None or (protected_scale is None):
        return TAC_BASE_DEPTH_UNRESOLVED
    if not unit_intersects_corridor(unit, corridor):
        return TAC_BASE_DEPTH_UNRESOLVED
    if unit_intersects_protected_zone(unit, protected_price=protected_price, protected_scale=protected_scale, theta_progress=theta_progress):
        return TAC_BASE_DEPTH_PROTECTED_INTERMEDIATE
    return TAC_BASE_DEPTH_OPERATING_LOCAL

def TAC_BASE_depth_relation(primary_class: str, candidate_class: str) -> StructuralDepthRelation:
    if TAC_BASE_DEPTH_UNRESOLVED in (primary_class, candidate_class):
        return StructuralDepthRelation.UNRESOLVED
    if primary_class == candidate_class:
        return StructuralDepthRelation.SAME_LAYER
    if primary_class == TAC_BASE_DEPTH_OPERATING_LOCAL and candidate_class == TAC_BASE_DEPTH_PROTECTED_INTERMEDIATE:
        return StructuralDepthRelation.DEEPER
    if primary_class == TAC_BASE_DEPTH_PROTECTED_INTERMEDIATE and candidate_class == TAC_BASE_DEPTH_OPERATING_LOCAL:
        return StructuralDepthRelation.SHALLOWER
    return StructuralDepthRelation.UNRESOLVED

def TAC_BASE_produce_role_state(request: TAC_BASE_Update008Request, *, episodes: tuple[AnchorEpisode, ...], units: tuple[EconomicBoundaryUnit, ...], prior_memory: TAC_BASE_RoleMemory | None, conflict_anchor_ids: tuple[str, ...]=()) -> tuple[TAC_BASE_RoleRuntimeOutput, TAC_BASE_RoleMemory | None]:
    units = tuple(sorted(units, key=lambda u: u.unit_id))
    episode_map = TAC_BASE__episode_map(episodes)
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
        at_least_valid = any((ep.validity is AnchorValidity.VALID and ep.activity in (AnchorActivity.ACTIVE, AnchorActivity.PRESSURED) and (not ep.terminal_true_break) and (ep.ended_at is None) for ep in episodes_present))
        latest, qbu_ids, has_use, qbu_conflict = TAC_BASE__unit_qbu_summary(unit, episode_map, request.negotiation_identity_by_event_id)
        qbu_ids_by_unit[unit.unit_id] = qbu_ids
        if qbu_conflict:
            summary_conflicts.append(f'{unit.unit_id}:{qbu_conflict}')
        active_interaction = TAC_BASE__unit_has_active_qualifying_interaction(unit, request.events, request.information_cutoff, request.trend_episode_id, request.direction)
        relevant = current_relevance(unit, corridor=request.corridor, has_actual_market_use=has_use, active_qualifying_interaction=active_interaction)
        terminal_true_break = bool(episodes_present) and all((ep.terminal_true_break for ep in episodes_present))
        unresolved_conflict = bool(missing) or qbu_conflict is not None or any((aid in conflict_anchors for aid in unit.anchor_episode_ids)) or any((ep.target_trend_episode_id != request.trend_episode_id or ep.target_direction is not request.direction for ep in episodes_present))
        base.append(BoundaryUnitRoleEvidence(unit=unit, at_least_one_valid_member=at_least_valid, current_relevant=relevant, latest_qualified_use_cutoff=latest, terminal_true_break=terminal_true_break, active_qualifying_interaction=active_interaction, unresolved_conflict=unresolved_conflict, structural_depth_relation_to_primary=StructuralDepthRelation.UNRESOLVED))
    if summary_conflicts:
        return (TAC_BASE_RoleRuntimeOutput(state=EvidenceState.CONFLICT, units=units, role_evidence=tuple(base), assignment=None, depth_class_by_unit_id=(), qbu_identities_by_unit_id=tuple(sorted(qbu_ids_by_unit.items())), primary_qbu_identities=(), promotion_confirmed_at=None, prior_primary_continuity_preserved=False, conflict_reasons=tuple(sorted(summary_conflicts)), provenance={'producer_semantic_contract_id': 'TAC_D3_B5_ROLE_STATE_PRODUCER_SEMANTIC_CONTRACT_V1'}), prior_memory)
    preliminary = assign_roles(list(base), structural_suitable_unit_ids=set())
    if preliminary.primary_unit_id is None:
        state = EvidenceState.UNKNOWN if preliminary.transition is RoleTransition.UNRESOLVED or units else EvidenceState.UNKNOWN
        return (TAC_BASE_RoleRuntimeOutput(state=state, units=units, role_evidence=tuple(base), assignment=preliminary, depth_class_by_unit_id=tuple(((e.unit.unit_id, TAC_BASE_DEPTH_UNRESOLVED) for e in base)), qbu_identities_by_unit_id=tuple(sorted(qbu_ids_by_unit.items())), primary_qbu_identities=(), promotion_confirmed_at=None, prior_primary_continuity_preserved=False, unresolved_reasons=(preliminary.unresolved_reason,) if preliminary.unresolved_reason else ('NO_AUTHORITATIVE_PRIMARY',), provenance={'producer_semantic_contract_id': 'TAC_D3_B5_ROLE_STATE_PRODUCER_SEMANTIC_CONTRACT_V1'}), prior_memory)
    primary_id = preliminary.primary_unit_id
    primary_base = next((e for e in base if e.unit.unit_id == primary_id))
    base_class_by_id = {e.unit.unit_id: TAC_BASE__depth_class(e.unit, e, corridor=request.corridor, protected_price=request.protected_price, protected_scale=request.protected_scale, theta_progress=request.theta_progress) for e in base}
    primary_class = base_class_by_id[primary_id]
    final_evidence: list[BoundaryUnitRoleEvidence] = []
    for evidence in base:
        rel = TAC_BASE_depth_relation(primary_class, base_class_by_id[evidence.unit.unit_id])
        final_evidence.append(replace(evidence, structural_depth_relation_to_primary=rel))
    structural_ids: set[str] = set()
    if request.protected_price is not None and request.protected_scale is not None:
        for evidence in final_evidence:
            if structural_role_eligible(evidence, protected_price=request.protected_price, protected_scale=request.protected_scale, theta_progress=request.theta_progress):
                structural_ids.add(evidence.unit.unit_id)
    eligible_deeper = [e for e in final_evidence if e.unit.unit_id != primary_id and e.at_least_one_valid_member and e.current_relevant and (e.latest_qualified_use_cutoff is not None) and (not e.terminal_true_break) and (not e.unresolved_conflict) and (e.structural_depth_relation_to_primary is StructuralDepthRelation.DEEPER) and set(e.unit.anchor_episode_ids).isdisjoint(primary_base.unit.anchor_episode_ids)]
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
            old_episode_ended = bool(prior_eps) and all((ep is not None and ep.validity is AnchorValidity.TERMINATED and (ep.ended_at is not None) for ep in prior_eps))
            takeover_relation = TAC_BASE_depth_relation(prior_memory.primary_depth_class, primary_class)
    assignment = assign_roles(final_evidence, structural_suitable_unit_ids=structural_ids, prior_primary_unit_id=prior_primary_id_for_consumer, old_episode_ended=old_episode_ended, takeover_depth_relation=takeover_relation, next_deeper_unit_id=next_deeper_id)
    promotion_cutoff = current_latest if assignment.transition is RoleTransition.PROMOTION else None
    unresolved: list[str] = []
    if assignment.transition is RoleTransition.UNRESOLVED:
        unresolved.append(assignment.unresolved_reason or 'ROLE_TRANSITION_UNRESOLVED')
    state = EvidenceState.UNKNOWN if unresolved else EvidenceState.TRUE
    next_memory = prior_memory
    if assignment.primary_unit_id is not None and assignment.transition is not RoleTransition.UNRESOLVED:
        unit = next((u for u in units if u.unit_id == assignment.primary_unit_id))
        next_memory = TAC_BASE_RoleMemory(trend_episode_id=request.trend_episode_id, primary_unit_id=unit.unit_id, primary_anchor_episode_ids=tuple(sorted(unit.anchor_episode_ids)), primary_depth_class=base_class_by_id[unit.unit_id], primary_qbu_identities=qbu_ids_by_unit.get(unit.unit_id, ()), primary_qbu_cutoff=current_latest)
    return (TAC_BASE_RoleRuntimeOutput(state=state, units=units, role_evidence=tuple(final_evidence), assignment=assignment, depth_class_by_unit_id=tuple(sorted(base_class_by_id.items())), qbu_identities_by_unit_id=tuple(sorted(qbu_ids_by_unit.items())), primary_qbu_identities=current_primary_qbu_ids, promotion_confirmed_at=promotion_cutoff, prior_primary_continuity_preserved=continuity_preserved, unresolved_reasons=tuple(unresolved), provenance={'producer_semantic_contract_id': 'TAC_D3_B5_ROLE_STATE_PRODUCER_SEMANTIC_CONTRACT_V1', 'structural_depth_contract_id': 'TAC_ECONOMIC_BOUNDARY_UNIT_STRUCTURAL_DEPTH_SEMANTIC_CONTRACT_V1', 'f9_stage': 'UPDATE-008'}), next_memory)

def TAC_BASE_produce_update008(request: TAC_BASE_Update008Request, *, prior_memory: TAC_BASE_RoleMemory | None=None) -> tuple[TAC_BASE_Update008Output, TAC_BASE_RoleMemory | None]:
    zones = TAC_BASE_produce_boundary_contact_zones(request)
    if zones.state is EvidenceState.CONFLICT:
        return (TAC_BASE_Update008Output(state=EvidenceState.CONFLICT, episodes=request.episodes, zones=(), units=(), role_evidence=(), roles=None, role_runtime=None, produced_qbus=(), conflict_lineage_refs=zones.conflict_anchor_ids, provenance={'transaction': 'NO_PARTIAL_ROLE_STATE_COMMIT'}), prior_memory)
    qbus = TAC_BASE_produce_qbus(request)
    if qbus.state is EvidenceState.CONFLICT:
        return (TAC_BASE_Update008Output(state=EvidenceState.CONFLICT, episodes=request.episodes, zones=(), units=(), role_evidence=(), roles=None, role_runtime=None, produced_qbus=(), conflict_lineage_refs=qbus.conflict_event_ids, provenance={'transaction': 'NO_PARTIAL_QBU_OR_ROLE_STATE_COMMIT'}), prior_memory)
    units = cluster_units(list(zones.zones))
    roles, next_memory = TAC_BASE_produce_role_state(request, episodes=qbus.episodes, units=units, prior_memory=prior_memory, conflict_anchor_ids=zones.conflict_anchor_ids)
    if roles.state is EvidenceState.CONFLICT:
        return (TAC_BASE_Update008Output(state=EvidenceState.CONFLICT, episodes=request.episodes, zones=(), units=(), role_evidence=(), roles=None, role_runtime=roles, produced_qbus=(), conflict_lineage_refs=roles.conflict_reasons, provenance={'transaction': 'NO_PARTIAL_ROLE_STATE_COMMIT'}), prior_memory)
    return (TAC_BASE_Update008Output(state=roles.state, episodes=qbus.episodes, zones=zones.zones, units=units, role_evidence=roles.role_evidence, roles=roles.assignment, role_runtime=roles, produced_qbus=qbus.produced_uses, unknown_lineage_refs=tuple(sorted(set(zones.unknown_anchor_ids + qbus.unknown_event_ids))), provenance={'runtime_contract_id': TAC_BASE_RUNTIME_CONTRACT_ID, 'f9_stage': 'UPDATE-008', 'no_update002_backflow': 'true'}), next_memory)

def TAC_BASE_attribute_entry_boundary(*, required_anchor_episode_ids: tuple[str, ...], units: tuple[EconomicBoundaryUnit, ...], episodes: tuple[AnchorEpisode, ...], target_trend_episode_id: str, direction: TrendDirection, information_cutoff: int, mechanism: str) -> TAC_BASE_EntryBoundaryProjection:
    required = tuple(sorted(set(required_anchor_episode_ids)))
    if not required:
        return TAC_BASE_EntryBoundaryProjection(EvidenceState.UNKNOWN, None, None, required, 'NO_MECHANISM_DEFINING_ANCHOR_LINEAGE', {'producer_semantic_contract_id': 'TAC_ENTRY_BOUNDARY_ATTRIBUTION_SEMANTIC_CONTRACT_V1', 'mechanism': mechanism})
    episode_map = TAC_BASE__episode_map(episodes)
    wanted = set(required)
    matches: list[tuple[EconomicBoundaryUnit, EntryBoundaryView]] = []
    for unit in units:
        if not wanted.issubset(set(unit.anchor_episode_ids)):
            continue
        try:
            view = entry_boundary_view(unit, episode_map, target_trend_episode_id=target_trend_episode_id, target_direction=direction, information_cutoff=information_cutoff)
        except ValueError:
            return TAC_BASE_EntryBoundaryProjection(EvidenceState.CONFLICT, None, None, required, 'ENTRY_BOUNDARY_FUTURE_OR_LINEAGE_CONFLICT', {'producer_semantic_contract_id': 'TAC_ENTRY_BOUNDARY_ATTRIBUTION_SEMANTIC_CONTRACT_V1', 'mechanism': mechanism})
        if view is not None and view.valid_active:
            matches.append((unit, view))
    if len(matches) == 1:
        unit, view = matches[0]
        return TAC_BASE_EntryBoundaryProjection(EvidenceState.TRUE, unit, view, required, 'UNIQUE_CAUSAL_MECHANISM_BOUNDARY_LINEAGE', {'producer_semantic_contract_id': 'TAC_ENTRY_BOUNDARY_ATTRIBUTION_SEMANTIC_CONTRACT_V1', 'mechanism': mechanism, 'member_selection': 'WHOLE_ECONOMIC_BOUNDARY_UNIT_NO_MEMBER_WINNER'})
    if not matches:
        return TAC_BASE_EntryBoundaryProjection(EvidenceState.UNKNOWN, None, None, required, 'NO_VALID_ACTIVE_MATCHING_EBU', {'producer_semantic_contract_id': 'TAC_ENTRY_BOUNDARY_ATTRIBUTION_SEMANTIC_CONTRACT_V1', 'mechanism': mechanism})
    return TAC_BASE_EntryBoundaryProjection(EvidenceState.CONFLICT, None, None, required, 'MULTIPLE_VALID_ACTIVE_MATCHING_EBU', {'producer_semantic_contract_id': 'TAC_ENTRY_BOUNDARY_ATTRIBUTION_SEMANTIC_CONTRACT_V1', 'mechanism': mechanism})

def TAC_BASE__normal_retest_qualifies(event: InteractionEvent, cutoff: int) -> bool:
    return TAC_BASE__event_actual_contact(event, cutoff) and event.break_state in (BreakState.NONE, BreakState.PROBE)

def TAC_BASE__select_adverse_reference(*, setup_key: str, direction: TrendDirection, contact_cutoff: int, information_cutoff: int, canonical_segment_id: str, pivots: tuple[StructuralPivot, ...]) -> tuple[EvidenceState, TAC_BASE_FixedAdverseReference | None, str]:
    adverse_type = PivotType.LOW if direction is TrendDirection.LONG else PivotType.HIGH
    eligible = [p for p in pivots if p.timeframe_ms == TAC_BASE_OBSERVER_TIMEFRAME_MS and p.layer is StructuralLayer.MINOR and (p.pivot_type is adverse_type) and (p.confirmed_at > contact_cutoff) and (p.confirmed_at <= information_cutoff) and (p.canonical_segment_id == canonical_segment_id) and bool(p.provenance)]
    if not eligible:
        return (EvidenceState.UNKNOWN, None, 'NO_CAUSAL_ADVERSE_15M_MINOR_PIVOT_YET')
    first_cutoff = min((p.confirmed_at for p in eligible))
    first = {p.pivot_id: p for p in eligible if p.confirmed_at == first_cutoff}
    if len(first) != 1:
        return (EvidenceState.CONFLICT, None, 'MULTIPLE_FIRST_ADVERSE_PIVOTS')
    pivot = next(iter(first.values()))
    return (EvidenceState.TRUE, TAC_BASE_FixedAdverseReference(setup_key=setup_key, pivot_id=pivot.pivot_id, confirmed_at=pivot.confirmed_at, canonical_segment_id=pivot.canonical_segment_id, direction=direction), 'FIRST_CAUSAL_ADVERSE_15M_MINOR_FIXED')

def TAC_BASE_produce_normal_retest(*, setup_key: str, information_cutoff: int, trend_episode_id: str, direction: TrendDirection, interaction: InteractionEvent, entry_boundary: TAC_BASE_EntryBoundaryProjection, pivots: tuple[StructuralPivot, ...], canonical_segment_id: str, setup_lineage: tuple[str, ...], existing_fixed_reference: TAC_BASE_FixedAdverseReference | None=None, local_control_regain: LocalTrendControlRegainEvidence | None=None) -> TAC_BASE_NormalRetestProjection:
    provenance = {'producer_semantic_contract_id': 'TAC_NORMAL_RETEST_BASE_EVIDENCE_SEMANTIC_CONTRACT_V1', 'setup_key': setup_key}
    if entry_boundary.state is EvidenceState.CONFLICT:
        return TAC_BASE_NormalRetestProjection(EvidenceState.CONFLICT, None, existing_fixed_reference, 'ENTRY_BOUNDARY_CONFLICT', provenance)
    if entry_boundary.state is not EvidenceState.TRUE or entry_boundary.view is None:
        return TAC_BASE_NormalRetestProjection(EvidenceState.UNKNOWN, None, existing_fixed_reference, 'ENTRY_BOUNDARY_UNKNOWN', provenance)
    if interaction.anchor_episode_id not in entry_boundary.view.member_anchor_episode_ids or interaction.target_trend_episode_id != trend_episode_id or interaction.target_direction is not direction:
        return TAC_BASE_NormalRetestProjection(EvidenceState.CONFLICT, None, existing_fixed_reference, 'INTERACTION_ENTRY_BOUNDARY_LINEAGE_CONFLICT', provenance)
    for value in (interaction.started_at, interaction.armed_at, interaction.approach_lineage_started_at, interaction.resolved_at):
        if value is not None and value > information_cutoff:
            return TAC_BASE_NormalRetestProjection(EvidenceState.CONFLICT, None, existing_fixed_reference, 'FUTURE_INTERACTION_STATE', provenance)
    if not TAC_BASE__normal_retest_qualifies(interaction, information_cutoff):
        evidence = NormalRetestEvidence(interaction=interaction, qualifying_retest_or_probe=False, adverse_structural_reference_fixed=False, local_control_regain=None, setup_lineage=setup_lineage, provenance={**provenance, 'qualifying': 'FALSE_APPROACH_OR_NON_NORMAL_BREAK_STATE'})
        return TAC_BASE_NormalRetestProjection(EvidenceState.FALSE, evidence, existing_fixed_reference, 'NOT_QUALIFYING_RETEST_OR_PROBE', provenance)
    if interaction.started_at is None:
        return TAC_BASE_NormalRetestProjection(EvidenceState.UNKNOWN, None, existing_fixed_reference, 'CONTACT_CUTOFF_UNKNOWN', provenance)
    fixed = existing_fixed_reference
    if fixed is not None:
        if fixed.setup_key != setup_key or fixed.direction is not direction or fixed.canonical_segment_id != canonical_segment_id or (fixed.confirmed_at > information_cutoff):
            return TAC_BASE_NormalRetestProjection(EvidenceState.CONFLICT, None, fixed, 'FIXED_ADVERSE_REFERENCE_CONFLICT', provenance)
    else:
        state, fixed, reason = TAC_BASE__select_adverse_reference(setup_key=setup_key, direction=direction, contact_cutoff=interaction.started_at, information_cutoff=information_cutoff, canonical_segment_id=canonical_segment_id, pivots=pivots)
        if state is not EvidenceState.TRUE or fixed is None:
            return TAC_BASE_NormalRetestProjection(state, None, None, reason, provenance)
    evidence = NormalRetestEvidence(interaction=interaction, qualifying_retest_or_probe=True, adverse_structural_reference_fixed=True, local_control_regain=local_control_regain, setup_lineage=setup_lineage, provenance={**provenance, 'qualifying': 'ACTUAL_B3_TEST_CONTACT_BREAK_NONE_OR_PROBE', 'adverse_reference_pivot_id': fixed.pivot_id, 'adverse_reference_confirmed_at': str(fixed.confirmed_at), 'adverse_reference_nonrolling': 'true'})
    return TAC_BASE_NormalRetestProjection(EvidenceState.TRUE, evidence, fixed, 'NORMAL_RETEST_BASE_EVIDENCE_AUTHORITATIVE', provenance)

def TAC_BASE__depth_class_map(role_runtime: TAC_BASE_RoleRuntimeOutput) -> dict[str, str]:
    return dict(role_runtime.depth_class_by_unit_id)

def TAC_BASE_produce_deep_takeover(request: TAC_BASE_DeepTakeoverRequest) -> TAC_BASE_DeepTakeoverProjection:
    provenance = {'producer_semantic_contract_id': 'TAC_DEEP_STRUCTURE_TAKEOVER_BASE_EVIDENCE_SEMANTIC_CONTRACT_V1', 'opportunity_id': request.opportunity_id, 'market_event_id': request.market_event_id}
    if request.deeper_entry_boundary.state is EvidenceState.CONFLICT:
        return TAC_BASE_DeepTakeoverProjection(EvidenceState.CONFLICT, None, 'DEEPER_ENTRY_BOUNDARY_CONFLICT', provenance)
    if request.deeper_entry_boundary.state is not EvidenceState.TRUE or request.deeper_entry_boundary.unit is None:
        return TAC_BASE_DeepTakeoverProjection(EvidenceState.UNKNOWN, None, 'DEEPER_ENTRY_BOUNDARY_UNKNOWN', provenance)
    if request.same_market_event_identity_authoritative is not True:
        return TAC_BASE_DeepTakeoverProjection(EvidenceState.CONFLICT, None, 'MARKET_EVENT_IDENTITY_NOT_AUTHORITATIVE', provenance)
    event = request.deeper_interaction
    if event.target_trend_episode_id != request.trend_episode_id or event.target_direction is not request.direction:
        return TAC_BASE_DeepTakeoverProjection(EvidenceState.CONFLICT, None, 'DEEPER_INTERACTION_LINEAGE_CONFLICT', provenance)
    if event.anchor_episode_id not in request.deeper_entry_boundary.unit.anchor_episode_ids:
        return TAC_BASE_DeepTakeoverProjection(EvidenceState.CONFLICT, None, 'DEEPER_INTERACTION_ENTRY_BOUNDARY_CONFLICT', provenance)
    if not TAC_BASE__event_actual_contact(event, request.information_cutoff):
        return TAC_BASE_DeepTakeoverProjection(EvidenceState.FALSE, DeepStructureTakeoverEvidence(shallow_operating_defense_no_longer_completes_setup=False, deeper_boundary_independent=False, deeper_interaction=event, local_control_regain=None, role_transition=RoleTransition.NONE, promotion_confirmed_at=None, setup_lineage=request.setup_lineage, provenance={**provenance, 'qualifying_deeper_contact': 'false'}), 'DEEPER_APPROACH_ONLY_OR_NO_ACTUAL_CONTACT', provenance)
    if event.break_state is BreakState.TRUE_BREAK or (event.terminal and event.resolution is InteractionResolution.RESOLVED_WRONG_SIDE):
        return TAC_BASE_DeepTakeoverProjection(EvidenceState.FALSE, DeepStructureTakeoverEvidence(shallow_operating_defense_no_longer_completes_setup=False, deeper_boundary_independent=False, deeper_interaction=event, local_control_regain=None, role_transition=RoleTransition.NONE, promotion_confirmed_at=None, setup_lineage=request.setup_lineage, provenance={**provenance, 'deeper_boundary_valid': 'false_terminal_true_break'}), 'DEEPER_BOUNDARY_TERMINALLY_INVALIDATED', provenance)
    classes = TAC_BASE__depth_class_map(request.role_runtime)
    shallow_class = classes.get(request.shallow_unit.unit_id, TAC_BASE_DEPTH_UNRESOLVED)
    deeper_unit = request.deeper_entry_boundary.unit
    deeper_class = classes.get(deeper_unit.unit_id, TAC_BASE_DEPTH_UNRESOLVED)
    relation = TAC_BASE_depth_relation(shallow_class, deeper_class)
    if relation is StructuralDepthRelation.UNRESOLVED:
        return TAC_BASE_DeepTakeoverProjection(EvidenceState.UNKNOWN, None, 'DEEPER_STRUCTURAL_DEPTH_UNRESOLVED', provenance)
    disjoint = set(request.shallow_unit.anchor_episode_ids).isdisjoint(deeper_unit.anchor_episode_ids)
    independent = deeper_unit.unit_id != request.shallow_unit.unit_id and disjoint and (relation is StructuralDepthRelation.DEEPER)
    if not independent:
        evidence = DeepStructureTakeoverEvidence(shallow_operating_defense_no_longer_completes_setup=False, deeper_boundary_independent=False, deeper_interaction=event, local_control_regain=None, role_transition=request.role_runtime.assignment.transition if request.role_runtime.assignment else RoleTransition.UNRESOLVED, promotion_confirmed_at=None, setup_lineage=request.setup_lineage, provenance={**provenance, 'structural_depth_relation': relation.value, 'independent': 'false'})
        return TAC_BASE_DeepTakeoverProjection(EvidenceState.FALSE, evidence, 'DEEPER_BOUNDARY_NOT_INDEPENDENT_DEEPER_EBU', provenance)
    contact_cutoff = event.started_at
    assert contact_cutoff is not None
    shallow_already_completed = request.shallow_behavior_confirmation_cutoff is not None and request.shallow_behavior_confirmation_cutoff <= contact_cutoff
    shallow_no_longer = not shallow_already_completed
    assignment = request.role_runtime.assignment
    role_transition = assignment.transition if assignment is not None else RoleTransition.UNRESOLVED
    promotion_cutoff = request.role_runtime.promotion_confirmed_at if role_transition is RoleTransition.PROMOTION else None
    evidence = DeepStructureTakeoverEvidence(shallow_operating_defense_no_longer_completes_setup=shallow_no_longer, deeper_boundary_independent=True, deeper_interaction=event, local_control_regain=request.local_control_regain, role_transition=role_transition, promotion_confirmed_at=promotion_cutoff, setup_lineage=request.setup_lineage, provenance={**provenance, 'structural_depth_relation': StructuralDepthRelation.DEEPER.value, 'independent': 'true', 'shallow_completed_before_deeper_contact': str(shallow_already_completed).lower(), 'promotion_source': 'B5_ROLE_RUNTIME_ONLY'})
    return TAC_BASE_DeepTakeoverProjection(EvidenceState.TRUE if shallow_no_longer else EvidenceState.FALSE, evidence, 'DEEP_TAKEOVER_BASE_EVIDENCE_AUTHORITATIVE' if shallow_no_longer else 'SHALLOW_SETUP_COMPLETED_FIRST', provenance)

def TAC_BASE_produce_trend_establishment_watch(*, record: TAC_BASE_TrendEstablishmentRecord | None, information_cutoff: int) -> TAC_BASE_TrendWatchProjection:
    provenance = {'producer_semantic_contract_id': 'TAC_TREND_ESTABLISHMENT_WATCH_SEMANTIC_DISPOSITION_V1'}
    if record is None:
        evidence = TrendEstablishmentWatchEvidence(False, (), (), {**provenance, 'observed': 'false_no_episode_creation'})
        return TAC_BASE_TrendWatchProjection(EvidenceState.FALSE, evidence, 'NO_TREND_EPISODE_CREATION', provenance)
    trend = record.trend
    if trend.episode_id is None or trend.episode_start_cutoff is None:
        return TAC_BASE_TrendWatchProjection(EvidenceState.UNKNOWN, None, 'TREND_EPISODE_CREATION_PROVENANCE_MISSING', provenance)
    if record.creation_cutoff != trend.episode_start_cutoff:
        return TAC_BASE_TrendWatchProjection(EvidenceState.CONFLICT, None, 'TREND_CREATION_CUTOFF_CONFLICT', provenance)
    if not record.newest_intermediate_pivot_id or not record.source_event_ids:
        return TAC_BASE_TrendWatchProjection(EvidenceState.UNKNOWN, None, 'ESTABLISHMENT_SOURCE_PROVENANCE_MISSING', provenance)
    if record.creation_cutoff > information_cutoff:
        return TAC_BASE_TrendWatchProjection(EvidenceState.CONFLICT, None, 'FUTURE_TREND_CREATION', provenance)
    observed = information_cutoff == record.creation_cutoff
    evidence = TrendEstablishmentWatchEvidence(observed=observed, setup_lineage=(trend.episode_id,), source_event_ids=record.source_event_ids, provenance={**provenance, **dict(record.provenance), 'newest_intermediate_pivot_id': record.newest_intermediate_pivot_id, 'creation_cutoff': str(record.creation_cutoff), 'watch_only': 'true', 'entry_ready': 'false'})
    return TAC_BASE_TrendWatchProjection(EvidenceState.TRUE if observed else EvidenceState.FALSE, evidence, 'GENESIS_CUTOFF' if observed else 'LATER_ACTIVE_TREND_CUTOFF', provenance)

def TAC_BASE_wire_false_break_reclaim(interaction: InteractionEvent, *, setup_lineage: tuple[str, ...]) -> FalseBreakReclaimEvidence:
    return FalseBreakReclaimEvidence(interaction=interaction, setup_lineage=setup_lineage, provenance={'disposition': 'ALREADY_MECHANICALLY_CLOSED_NO_NEW_SEMANTIC_REQUIRED'})

def TAC_BASE_wire_platform_reexpansion(platform: PlatformState, *, current_close: Fraction, target_trend_episode_id: str, direction: TrendDirection, setup_lineage: tuple[str, ...]) -> PlatformReexpansionEvidence:
    return PlatformReexpansionEvidence(platform=platform, current_close=current_close, target_trend_episode_id=target_trend_episode_id, direction=direction, setup_lineage=setup_lineage, provenance={'disposition': 'ALREADY_MECHANICALLY_CLOSED_NO_NEW_SEMANTIC_REQUIRED'})

class TAC_BASE_AuthoritativeD3B5D4BaseRuntimeV1:
    """Small transactional producer runtime; no packet assembly and no market I/O."""

    def __init__(self) -> None:
        self._role_memory: dict[str, TAC_BASE_RoleMemory] = {}
        self._fixed_adverse: dict[str, TAC_BASE_FixedAdverseReference] = {}
        self._tx_input_digest: dict[str, str] = {}
        self._tx_result: dict[str, Any] = {}

    def _guard_tx(self, tx_id: str, payload: Any) -> tuple[bool, Any | None]:
        d = TAC_BASE_digest(payload)
        old = self._tx_input_digest.get(tx_id)
        if old is None:
            return (False, None)
        if old != d:
            raise TAC_BASE_RuntimeProducerBlock('SAME_TX_INPUT_MISMATCH')
        return (True, self._tx_result[tx_id])

    def _commit_tx(self, tx_id: str, payload: Any, result: Any) -> Any:
        self._tx_input_digest[tx_id] = TAC_BASE_digest(payload)
        self._tx_result[tx_id] = result
        return result

    def process_update008(self, tx_id: str, request: TAC_BASE_Update008Request) -> TAC_BASE_Update008Output:
        replay, result = self._guard_tx(tx_id, request)
        if replay:
            return result
        prior = self._role_memory.get(request.trend_episode_id)
        output, next_memory = TAC_BASE_produce_update008(request, prior_memory=prior)
        if output.state is not EvidenceState.CONFLICT and next_memory is not None:
            self._role_memory[request.trend_episode_id] = next_memory
        return self._commit_tx(tx_id, request, output)

    def process_normal_retest(self, tx_id: str, *, setup_key: str, information_cutoff: int, trend_episode_id: str, direction: TrendDirection, interaction: InteractionEvent, entry_boundary: TAC_BASE_EntryBoundaryProjection, pivots: tuple[StructuralPivot, ...], canonical_segment_id: str, setup_lineage: tuple[str, ...], local_control_regain: LocalTrendControlRegainEvidence | None=None) -> TAC_BASE_NormalRetestProjection:
        payload = (setup_key, information_cutoff, trend_episode_id, direction, interaction, entry_boundary, pivots, canonical_segment_id, setup_lineage, local_control_regain)
        replay, result = self._guard_tx(tx_id, payload)
        if replay:
            return result
        existing = self._fixed_adverse.get(setup_key)
        projection = TAC_BASE_produce_normal_retest(setup_key=setup_key, information_cutoff=information_cutoff, trend_episode_id=trend_episode_id, direction=direction, interaction=interaction, entry_boundary=entry_boundary, pivots=pivots, canonical_segment_id=canonical_segment_id, setup_lineage=setup_lineage, existing_fixed_reference=existing, local_control_regain=local_control_regain)
        if projection.state is EvidenceState.TRUE and projection.adverse_reference is not None and (existing is None):
            self._fixed_adverse[setup_key] = projection.adverse_reference
        return self._commit_tx(tx_id, payload, projection)

    def export_state(self) -> Mapping[str, Any]:
        return {'schema': 'AUTHORITATIVE_D3_B5_D4_BASE_RUNTIME_STATE_V1', 'role_memory': TAC_BASE__encode(self._role_memory), 'fixed_adverse': TAC_BASE__encode(self._fixed_adverse), 'tx_input_digest': dict(sorted(self._tx_input_digest.items())), 'tx_result': TAC_BASE__encode(self._tx_result)}

    @classmethod
    def restore_state(cls, state: Mapping[str, Any]) -> 'AuthoritativeD3B5D4BaseRuntimeV1':
        if state.get('schema') != 'AUTHORITATIVE_D3_B5_D4_BASE_RUNTIME_STATE_V1':
            raise TAC_BASE_RuntimeProducerBlock('RUNTIME_STATE_SCHEMA_MISMATCH')
        out = cls()
        role_memory = TAC_BASE__decode(state.get('role_memory', {'$map': []}))
        fixed = TAC_BASE__decode(state.get('fixed_adverse', {'$map': []}))
        tx_result = TAC_BASE__decode(state.get('tx_result', {'$map': []}))
        out._role_memory = dict(role_memory)
        out._fixed_adverse = dict(fixed)
        out._tx_input_digest = {str(k): str(v) for k, v in dict(state.get('tx_input_digest', {})).items()}
        out._tx_result = dict(tx_result)
        return out

# --- EXACT SCIENCE NAMESPACE TAC_ID_ ---
from dataclasses import dataclass, field, replace
from fractions import Fraction
from typing import Mapping
TAC_ID_PRODUCER_ID = 'QBU_SAME_EVENT_NEGOTIATION_IDENTITY_PRODUCTION_BINDING_V1'
TAC_ID_SEMANTIC_ID = 'QBU_SAME_EVENT_NEGOTIATION_IDENTITY_SOURCE_ASSOCIATION_V1'
TAC_ID_SEMANTIC_CONTRACT_BLOB = 'b6071576c708fc7b713e377ffdb9af4a0db9de8e'
TAC_ID_SEMANTIC_FREEZE_MANIFEST_BLOB = '210c2315ce618a17a83445a036e5aeb9cf49171b'
TAC_ID_RUNTIME_PRODUCER_BLOB = '97a02f5584c1446ca5ae016bad383e3ed0e18bb5'
TAC_ID_STATUS_KNOWN = 'KNOWN'
TAC_ID_STATUS_UNKNOWN = 'UNKNOWN'
TAC_ID_STATUS_CONFLICT = 'CONFLICT'

class TAC_ID_NegotiationIdentityBlock(RuntimeError):
    pass

class TAC_ID_NegotiationIdentityConflict(TAC_ID_NegotiationIdentityBlock):
    pass

@dataclass(frozen=True)
class TAC_ID_NegotiationIdentityRequest:
    information_cutoff: int
    trend_episode_id: str
    direction: TrendDirection
    events: tuple[InteractionEvent, ...]
    episodes: tuple[AnchorEpisode, ...]
    continuity_by_candidate_id: Mapping[str, bool | None]
    theta_test: Fraction
    rearm_predecessor_by_event_id: Mapping[str, str] = field(default_factory=dict)
    history_complete: bool = False
    provenance: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, 'continuity_by_candidate_id', MappingProxyType({str(k): v for k, v in self.continuity_by_candidate_id.items()}))
        object.__setattr__(self, 'rearm_predecessor_by_event_id', MappingProxyType({str(k): str(v) for k, v in self.rearm_predecessor_by_event_id.items()}))
        object.__setattr__(self, 'provenance', MappingProxyType({str(k): str(v) for k, v in self.provenance.items()}))

@dataclass(frozen=True)
class TAC_ID_NegotiationIdentityProjection:
    status: str
    negotiation_identity_by_event_id: Mapping[str, str]
    component_members: tuple[tuple[str, tuple[str, ...]], ...]
    unknown_refs: tuple[str, ...] = ()
    conflict_refs: tuple[str, ...] = ()
    reason: str | None = None
    provenance: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, 'negotiation_identity_by_event_id', MappingProxyType(dict(self.negotiation_identity_by_event_id)))
        object.__setattr__(self, 'provenance', MappingProxyType({str(k): str(v) for k, v in self.provenance.items()}))

def TAC_ID__direction_value(direction: TrendDirection) -> str:
    return direction.value if hasattr(direction, 'value') else str(direction)

def TAC_ID__event_zone(event: InteractionEvent, theta_test: Fraction) -> tuple[Fraction, Fraction]:
    boundary = event.event_reference_boundary
    scale = event.event_reference_scale
    if boundary is None or scale is None:
        raise TAC_ID_NegotiationIdentityBlock('EVENT_REFERENCE_GEOMETRY_UNKNOWN:' + event.event_id)
    if scale <= 0:
        raise TAC_ID_NegotiationIdentityConflict('EVENT_REFERENCE_SCALE_NONPOSITIVE:' + event.event_id)
    if event.target_direction is TrendDirection.LONG:
        return (boundary, boundary + theta_test * scale)
    if event.target_direction is TrendDirection.SHORT:
        return (boundary - theta_test * scale, boundary)
    raise TAC_ID_NegotiationIdentityConflict('INVALID_DIRECTION:' + event.event_id)

def TAC_ID__price_overlap(a: tuple[Fraction, Fraction], b: tuple[Fraction, Fraction]) -> bool:
    return max(a[0], b[0]) <= min(a[1], b[1])

def TAC_ID__time_overlap(a: InteractionEvent, b: InteractionEvent) -> bool:
    assert a.started_at is not None and a.resolved_at is not None
    assert b.started_at is not None and b.resolved_at is not None
    return max(a.started_at, b.started_at) <= min(a.resolved_at, b.resolved_at)

def TAC_ID__same_record(a: InteractionEvent, b: InteractionEvent) -> bool:
    return a == b

def TAC_ID__target_episode_map(req: TAC_ID_NegotiationIdentityRequest) -> dict[str, AnchorEpisode]:
    out: dict[str, AnchorEpisode] = {}
    for ep in req.episodes:
        if ep.target_trend_episode_id != req.trend_episode_id or ep.target_direction is not req.direction:
            continue
        if ep.anchor_episode_id in out and out[ep.anchor_episode_id] != ep:
            raise TAC_ID_NegotiationIdentityConflict('DIVERGENT_ANCHOR_EPISODE:' + ep.anchor_episode_id)
        out[ep.anchor_episode_id] = ep
    return out

def TAC_ID__event_map(req: TAC_ID_NegotiationIdentityRequest) -> tuple[dict[str, InteractionEvent], tuple[str, ...]]:
    by_id: dict[str, InteractionEvent] = {}
    conflicts: set[str] = set()
    for ev in req.events:
        old = by_id.get(ev.event_id)
        if old is not None and (not TAC_ID__same_record(old, ev)):
            conflicts.add(ev.event_id)
            continue
        by_id[ev.event_id] = ev
    return (by_id, tuple(sorted(conflicts)))

def TAC_ID__qbu_event_ids(episodes: Mapping[str, AnchorEpisode]) -> set[str]:
    out: set[str] = set()
    for ep in episodes.values():
        for use in ep.qualified_uses:
            out.add(use.negotiation_event_id)
    return out

def TAC_ID__candidate_target_event(ev: InteractionEvent, *, trend_episode_id: str, direction: TrendDirection) -> bool:
    return ev.target_trend_episode_id == trend_episode_id and ev.target_direction is direction

def TAC_ID__eligibility(req: TAC_ID_NegotiationIdentityRequest, ev: InteractionEvent, *, episode_map: Mapping[str, AnchorEpisode], qbu_event_ids: set[str]) -> tuple[str, bool, str | None]:
    """Return (status, eligible, ref).

    Non-QBU records that are authoritatively outside the frozen eligible domain
    are excluded rather than converted into conflicts.  Existing QBU-bearing
    records must satisfy every non-missing invariant or fail closed.
    """
    qbu_bearing = ev.event_id in qbu_event_ids
    if not TAC_ID__candidate_target_event(ev, trend_episode_id=req.trend_episode_id, direction=req.direction):
        if qbu_bearing:
            return (TAC_ID_STATUS_CONFLICT, False, 'QBU_TARGET_MISMATCH:' + ev.event_id)
        return (TAC_ID_STATUS_KNOWN, False, None)
    if ev.started_at is not None and ev.started_at > req.information_cutoff:
        return (TAC_ID_STATUS_CONFLICT, False, 'FUTURE_EVENT_START:' + ev.event_id)
    if ev.resolved_at is not None and ev.resolved_at > req.information_cutoff:
        return (TAC_ID_STATUS_CONFLICT, False, 'FUTURE_EVENT_RESOLUTION:' + ev.event_id)
    if ev.resolution is not InteractionResolution.RESOLVED_CORRECT_SIDE or ev.break_state is BreakState.TRUE_BREAK:
        if qbu_bearing:
            return (TAC_ID_STATUS_CONFLICT, False, 'INVALID_QBU_EVENT_STATE:' + ev.event_id)
        return (TAC_ID_STATUS_KNOWN, False, None)
    if ev.started_at is None or ev.resolved_at is None:
        return (TAC_ID_STATUS_UNKNOWN, False, 'EVENT_TIME_UNKNOWN:' + ev.event_id)
    if ev.resolved_at < ev.started_at:
        return (TAC_ID_STATUS_CONFLICT, False, 'EVENT_TIME_INVERTED:' + ev.event_id)
    if ev.event_reference_boundary is None or ev.event_reference_scale is None:
        return (TAC_ID_STATUS_UNKNOWN, False, 'EVENT_REFERENCE_UNKNOWN:' + ev.event_id)
    if ev.event_reference_scale <= 0:
        return (TAC_ID_STATUS_CONFLICT, False, 'EVENT_REFERENCE_SCALE_NONPOSITIVE:' + ev.event_id)
    if ev.anchor_episode_id is None:
        return (TAC_ID_STATUS_UNKNOWN, False, 'ANCHOR_EPISODE_UNKNOWN:' + ev.event_id)
    ep = episode_map.get(ev.anchor_episode_id)
    if ep is None:
        return (TAC_ID_STATUS_CONFLICT if qbu_bearing else TAC_ID_STATUS_UNKNOWN, False, 'ANCHOR_EPISODE_MISSING:' + ev.event_id)
    if ep.target_trend_episode_id != ev.target_trend_episode_id or ep.target_direction is not ev.target_direction or ep.candidate_id != ev.candidate_id or (ev.event_id not in set(ep.interaction_event_ids)):
        return (TAC_ID_STATUS_CONFLICT, False, 'EVENT_ANCHOR_LINEAGE_MISMATCH:' + ev.event_id)
    continuity = req.continuity_by_candidate_id.get(ev.candidate_id)
    if continuity is None:
        return (TAC_ID_STATUS_UNKNOWN, False, 'CONTINUITY_UNKNOWN:' + ev.event_id)
    if continuity is False:
        if qbu_bearing:
            return (TAC_ID_STATUS_CONFLICT, False, 'QBU_CONTINUITY_FALSE:' + ev.event_id)
        return (TAC_ID_STATUS_KNOWN, False, None)
    return (TAC_ID_STATUS_KNOWN, True, None)

def TAC_ID__same_negotiation_edge(req: TAC_ID_NegotiationIdentityRequest, a: InteractionEvent, b: InteractionEvent) -> bool:
    if a.target_trend_episode_id != b.target_trend_episode_id:
        return False
    if a.target_direction is not b.target_direction:
        return False
    if req.continuity_by_candidate_id.get(a.candidate_id) is not True:
        return False
    if req.continuity_by_candidate_id.get(b.candidate_id) is not True:
        return False
    return TAC_ID__price_overlap(TAC_ID__event_zone(a, req.theta_test), TAC_ID__event_zone(b, req.theta_test)) and TAC_ID__time_overlap(a, b)

def TAC_ID__canonical_identity(trend_episode_id: str, direction: TrendDirection, members: tuple[InteractionEvent, ...]) -> str:
    root_cutoff = min((ev.started_at for ev in members if ev.started_at is not None))
    root_event_ids = tuple(sorted((ev.event_id for ev in members if ev.started_at == root_cutoff)))
    return deterministic_id('QBU-NEGOTIATION-V1', trend_episode_id, TAC_ID__direction_value(direction), str(root_cutoff), '|'.join(root_event_ids))

def TAC_ID__ancestor_pairs(req: TAC_ID_NegotiationIdentityRequest) -> tuple[tuple[str, str], ...]:
    pred = dict(req.rearm_predecessor_by_event_id)
    pairs: set[tuple[str, str]] = set()
    for child in sorted(pred):
        seen: set[str] = set()
        cur = child
        while cur in pred:
            if cur in seen:
                raise TAC_ID_NegotiationIdentityConflict('REARM_PREDECESSOR_CYCLE:' + child)
            seen.add(cur)
            parent = pred[cur]
            if not parent:
                raise TAC_ID_NegotiationIdentityConflict('EMPTY_REARM_PREDECESSOR:' + child)
            pairs.add((child, parent))
            cur = parent
    return tuple(sorted(pairs))

def TAC_ID_project_negotiation_identity(req: TAC_ID_NegotiationIdentityRequest) -> TAC_ID_NegotiationIdentityProjection:
    if not isinstance(req, TAC_ID_NegotiationIdentityRequest):
        raise TAC_ID_NegotiationIdentityConflict('REQUEST_SCHEMA')
    if req.information_cutoff < 0:
        raise TAC_ID_NegotiationIdentityConflict('INVALID_INFORMATION_CUTOFF')
    if not req.trend_episode_id:
        raise TAC_ID_NegotiationIdentityConflict('TREND_EPISODE_ID_REQUIRED')
    if req.direction not in (TrendDirection.LONG, TrendDirection.SHORT):
        raise TAC_ID_NegotiationIdentityConflict('DIRECTION_REQUIRED')
    if req.theta_test <= 0:
        raise TAC_ID_NegotiationIdentityConflict('THETA_TEST_MUST_BE_POSITIVE_FROZEN_INPUT')
    if not req.history_complete:
        return TAC_ID_NegotiationIdentityProjection(status=TAC_ID_STATUS_UNKNOWN, negotiation_identity_by_event_id={}, component_members=(), unknown_refs=('INTERACTION_HISTORY_COVERAGE_INCOMPLETE',), reason='INTERACTION_HISTORY_COVERAGE_INCOMPLETE', provenance={'producer_id': TAC_ID_PRODUCER_ID, 'semantic_id': TAC_ID_SEMANTIC_ID, 'scientific_state_mutated': 'false'})
    try:
        episodes = TAC_ID__target_episode_map(req)
        events, duplicate_conflicts = TAC_ID__event_map(req)
    except TAC_ID_NegotiationIdentityConflict as exc:
        return TAC_ID_NegotiationIdentityProjection(status=TAC_ID_STATUS_CONFLICT, negotiation_identity_by_event_id={}, component_members=(), conflict_refs=(str(exc),), reason=str(exc), provenance={'producer_id': TAC_ID_PRODUCER_ID, 'semantic_id': TAC_ID_SEMANTIC_ID})
    if duplicate_conflicts:
        return TAC_ID_NegotiationIdentityProjection(status=TAC_ID_STATUS_CONFLICT, negotiation_identity_by_event_id={}, component_members=(), conflict_refs=tuple(('DIVERGENT_EVENT_RECORD:' + x for x in duplicate_conflicts)), reason='DIVERGENT_EVENT_RECORDS', provenance={'producer_id': TAC_ID_PRODUCER_ID, 'semantic_id': TAC_ID_SEMANTIC_ID})
    qbu_ids = TAC_ID__qbu_event_ids(episodes)
    missing_refs: set[str] = set()
    for ep in episodes.values():
        for event_id in ep.interaction_event_ids:
            if event_id not in events:
                missing_refs.add(event_id)
    missing_refs.update((event_id for event_id in qbu_ids if event_id not in events))
    if missing_refs:
        return TAC_ID_NegotiationIdentityProjection(status=TAC_ID_STATUS_UNKNOWN, negotiation_identity_by_event_id={}, component_members=(), unknown_refs=tuple(sorted(('MISSING_EVENT:' + x for x in missing_refs))), reason='REFERENCED_INTERACTION_EVENT_MISSING', provenance={'producer_id': TAC_ID_PRODUCER_ID, 'semantic_id': TAC_ID_SEMANTIC_ID})
    eligible: list[InteractionEvent] = []
    unknown: set[str] = set()
    conflict: set[str] = set()
    for ev in events.values():
        status, ok, ref = TAC_ID__eligibility(req, ev, episode_map=episodes, qbu_event_ids=qbu_ids)
        if status == TAC_ID_STATUS_UNKNOWN and ref:
            unknown.add(ref)
        elif status == TAC_ID_STATUS_CONFLICT and ref:
            conflict.add(ref)
        elif ok:
            eligible.append(ev)
    if conflict:
        return TAC_ID_NegotiationIdentityProjection(status=TAC_ID_STATUS_CONFLICT, negotiation_identity_by_event_id={}, component_members=(), conflict_refs=tuple(sorted(conflict)), reason='ELIGIBILITY_CONFLICT', provenance={'producer_id': TAC_ID_PRODUCER_ID, 'semantic_id': TAC_ID_SEMANTIC_ID})
    if unknown:
        return TAC_ID_NegotiationIdentityProjection(status=TAC_ID_STATUS_UNKNOWN, negotiation_identity_by_event_id={}, component_members=(), unknown_refs=tuple(sorted(unknown)), reason='ELIGIBILITY_UNKNOWN', provenance={'producer_id': TAC_ID_PRODUCER_ID, 'semantic_id': TAC_ID_SEMANTIC_ID})
    eligible_ids = {ev.event_id for ev in eligible}
    noneligible_qbu = sorted(qbu_ids - eligible_ids)
    if noneligible_qbu:
        return TAC_ID_NegotiationIdentityProjection(status=TAC_ID_STATUS_CONFLICT, negotiation_identity_by_event_id={}, component_members=(), conflict_refs=tuple(('QBU_EVENT_NOT_ELIGIBLE:' + x for x in noneligible_qbu)), reason='QBU_EVENT_NOT_ELIGIBLE', provenance={'producer_id': TAC_ID_PRODUCER_ID, 'semantic_id': TAC_ID_SEMANTIC_ID})
    parent = {ev.event_id: ev.event_id for ev in eligible}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: str, b: str) -> None:
        ra, rb = (find(a), find(b))
        if ra != rb:
            parent[rb] = ra
    eligible_sorted = tuple(sorted(eligible, key=lambda e: e.event_id))
    for i, a in enumerate(eligible_sorted):
        for b in eligible_sorted[i + 1:]:
            if TAC_ID__same_negotiation_edge(req, a, b):
                union(a.event_id, b.event_id)
    components_by_root: dict[str, list[InteractionEvent]] = {}
    for ev in eligible_sorted:
        components_by_root.setdefault(find(ev.event_id), []).append(ev)
    try:
        ancestor_pairs = TAC_ID__ancestor_pairs(req)
    except TAC_ID_NegotiationIdentityConflict as exc:
        return TAC_ID_NegotiationIdentityProjection(status=TAC_ID_STATUS_CONFLICT, negotiation_identity_by_event_id={}, component_members=(), conflict_refs=(str(exc),), reason='REARM_LINEAGE_CONFLICT', provenance={'producer_id': TAC_ID_PRODUCER_ID, 'semantic_id': TAC_ID_SEMANTIC_ID})
    for child, ancestor in ancestor_pairs:
        if child in parent and ancestor in parent and (find(child) == find(ancestor)):
            return TAC_ID_NegotiationIdentityProjection(status=TAC_ID_STATUS_CONFLICT, negotiation_identity_by_event_id={}, component_members=(), conflict_refs=('REARM_BOUNDARY_SAME_COMPONENT:' + child + ':' + ancestor,), reason='REARM_BOUNDARY_SAME_COMPONENT', provenance={'producer_id': TAC_ID_PRODUCER_ID, 'semantic_id': TAC_ID_SEMANTIC_ID})
    mapping: dict[str, str] = {}
    component_rows: list[tuple[str, tuple[str, ...]]] = []
    for members_list in components_by_root.values():
        members = tuple(sorted(members_list, key=lambda e: e.event_id))
        identity = TAC_ID__canonical_identity(req.trend_episode_id, req.direction, members)
        member_ids = tuple((ev.event_id for ev in members))
        component_rows.append((identity, member_ids))
        for event_id in member_ids:
            mapping[event_id] = identity
    if not qbu_ids.issubset(mapping):
        missing = tuple(sorted(qbu_ids - set(mapping)))
        return TAC_ID_NegotiationIdentityProjection(status=TAC_ID_STATUS_CONFLICT, negotiation_identity_by_event_id={}, component_members=(), conflict_refs=tuple(('QBU_IDENTITY_MISSING:' + x for x in missing)), reason='QBU_IDENTITY_MISSING', provenance={'producer_id': TAC_ID_PRODUCER_ID, 'semantic_id': TAC_ID_SEMANTIC_ID})
    return TAC_ID_NegotiationIdentityProjection(status=TAC_ID_STATUS_KNOWN, negotiation_identity_by_event_id=mapping, component_members=tuple(sorted(component_rows)), unknown_refs=(), conflict_refs=(), reason=None, provenance={'producer_id': TAC_ID_PRODUCER_ID, 'semantic_id': TAC_ID_SEMANTIC_ID, 'semantic_contract_blob': TAC_ID_SEMANTIC_CONTRACT_BLOB, 'semantic_freeze_manifest_blob': TAC_ID_SEMANTIC_FREEZE_MANIFEST_BLOB, 'runtime_producer_blob': TAC_ID_RUNTIME_PRODUCER_BLOB, 'f9_stage': 'POST_UPDATE007_PRE_UPDATE008', 'downstream_d4_identity_used': 'false', 'scientific_state_mutated': 'false', 'real_market_data_read': 'false', 'test_read': 'false', 'pnl': 'false', 'trading': 'FORBIDDEN'})

def TAC_ID_bind_update008_request(request: TAC_BASE_Update008Request, projection: TAC_ID_NegotiationIdentityProjection) -> TAC_BASE_Update008Request:
    """Bind frozen negotiation identity directly into the existing request.

    Caller prepopulation is forbidden so that production identity cannot be
    silently overridden or mixed with a guessed mapping.
    """
    if not isinstance(request, TAC_BASE_Update008Request):
        raise TAC_ID_NegotiationIdentityConflict('UPDATE008_REQUEST_SCHEMA')
    if request.negotiation_identity_by_event_id:
        raise TAC_ID_NegotiationIdentityConflict('CALLER_PREPOPULATED_NEGOTIATION_IDENTITY_FORBIDDEN')
    if projection.status != TAC_ID_STATUS_KNOWN:
        raise TAC_ID_NegotiationIdentityBlock('KNOWN_NEGOTIATION_IDENTITY_PROJECTION_REQUIRED')
    return replace(request, negotiation_identity_by_event_id=dict(projection.negotiation_identity_by_event_id), provenance={**dict(request.provenance), 'negotiation_identity_producer_id': TAC_ID_PRODUCER_ID, 'negotiation_identity_semantic_id': TAC_ID_SEMANTIC_ID})

# --- EXACT SCIENCE NAMESPACE TAC_PR_ ---
from dataclasses import dataclass, field, replace
from typing import Mapping
TAC_PR_PRODUCER_ID = 'QBU_MATERIAL_TREND_SIDE_MINOR_PROGRESS_PRODUCTION_BINDING_V1'
TAC_PR_SEMANTIC_ID = 'QBU_MATERIAL_TREND_SIDE_MINOR_PROGRESS_SOURCE_ASSOCIATION_V1'
TAC_PR_SEMANTIC_CONTRACT_BLOB = 'efa00c82a64a5d4d2a7db0e0679a105a8595924f'
TAC_PR_SEMANTIC_FREEZE_MANIFEST_BLOB = '2d0c6215de0c1653afe22a77be78859e2e8a1a4e'
TAC_PR_RUNTIME_CONSUMER_BLOB = '97a02f5584c1446ca5ae016bad383e3ed0e18bb5'
TAC_PR_OBSERVER_TIMEFRAME_MS = 15 * 60 * 1000

class TAC_PR_QBUProgressProductionBlock(RuntimeError):
    pass

class TAC_PR_QBUProgressProductionConflict(TAC_PR_QBUProgressProductionBlock):
    pass

@dataclass(frozen=True)
class TAC_PR_QBUProgressProductionRequest:
    update008_request: TAC_BASE_Update008Request
    all_minor: tuple[StructuralPivot, ...]
    trend_episode_start_cutoff: int
    trend_episode_terminal_cutoff: int | None
    history_complete: bool
    history_coverage_ref: str
    theta_progress_parameter_ref: str
    provenance: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, 'provenance', MappingProxyType({str(k): str(v) for k, v in self.provenance.items()}))

@dataclass(frozen=True)
class TAC_PR_QBUProgressProductionProjection:
    state: EvidenceState
    progress_evidence: tuple[TAC_BASE_ProgressLineageEvidence, ...]
    unknown_refs: tuple[str, ...] = ()
    conflict_refs: tuple[str, ...] = ()
    provenance: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, 'provenance', MappingProxyType({str(k): str(v) for k, v in self.provenance.items()}))

def TAC_PR__trend_side_type(direction: TrendDirection) -> PivotType:
    if direction is TrendDirection.LONG:
        return PivotType.HIGH
    if direction is TrendDirection.SHORT:
        return PivotType.LOW
    raise TAC_PR_QBUProgressProductionConflict('INVALID_DIRECTION')

def TAC_PR__material_relation(direction: TrendDirection) -> ProgressRelation:
    if direction is TrendDirection.LONG:
        return ProgressRelation.MATERIAL_ADVANCE_UP
    if direction is TrendDirection.SHORT:
        return ProgressRelation.MATERIAL_ADVANCE_DOWN
    raise TAC_PR_QBUProgressProductionConflict('INVALID_DIRECTION')

def TAC_PR__canonical_event_map(events: tuple[InteractionEvent, ...]) -> tuple[dict[str, InteractionEvent], tuple[str, ...]]:
    out: dict[str, InteractionEvent] = {}
    conflicts: set[str] = set()
    for ev in events:
        old = out.get(ev.event_id)
        if old is not None and old != ev:
            conflicts.add(ev.event_id)
        else:
            out[ev.event_id] = ev
    return (out, tuple(sorted(conflicts)))

def TAC_PR__canonical_pivot_map(pivots: tuple[StructuralPivot, ...]) -> tuple[dict[str, StructuralPivot], tuple[str, ...]]:
    out: dict[str, StructuralPivot] = {}
    conflicts: set[str] = set()
    for p in pivots:
        old = out.get(p.pivot_id)
        if old is not None and old != p:
            conflicts.add(p.pivot_id)
        else:
            out[p.pivot_id] = p
    return (out, tuple(sorted(conflicts)))

def TAC_PR__target_events(req: TAC_BASE_Update008Request) -> tuple[tuple[InteractionEvent, str], ...]:
    """Return consumer-relevant resolved events plus their canonical segment IDs."""
    event_map, event_conflicts = TAC_PR__canonical_event_map(req.events)
    if event_conflicts:
        raise TAC_PR_QBUProgressProductionConflict('DIVERGENT_EVENT_RECORD:' + ','.join(event_conflicts))
    rows: list[tuple[InteractionEvent, str]] = []
    seen: set[str] = set()
    for ep in sorted(req.episodes, key=lambda e: e.anchor_episode_id):
        if ep.target_trend_episode_id != req.trend_episode_id or ep.target_direction is not req.direction:
            continue
        if ep.validity is AnchorValidity.TERMINATED or ep.terminal_true_break:
            continue
        segment = req.canonical_segment_id_by_anchor_episode_id.get(ep.anchor_episode_id)
        if not segment:
            for eid in ep.interaction_event_ids:
                ev = event_map.get(eid)
                if ev is not None and ev.resolution is InteractionResolution.RESOLVED_CORRECT_SIDE:
                    raise TAC_PR_QBUProgressProductionBlock('CANONICAL_SEGMENT_UNKNOWN:' + ep.anchor_episode_id)
            continue
        continuity = req.continuity_by_candidate_id.get(ep.candidate_id)
        if continuity is None:
            for eid in ep.interaction_event_ids:
                ev = event_map.get(eid)
                if ev is not None and ev.resolution is InteractionResolution.RESOLVED_CORRECT_SIDE:
                    raise TAC_PR_QBUProgressProductionBlock('CONTINUITY_UNKNOWN:' + ep.candidate_id)
            continue
        if continuity is False:
            for eid in ep.interaction_event_ids:
                ev = event_map.get(eid)
                if ev is not None and ev.resolution is InteractionResolution.RESOLVED_CORRECT_SIDE:
                    raise TAC_PR_QBUProgressProductionConflict('CONTINUITY_FALSE:' + ep.candidate_id)
            continue
        for event_id in sorted(set(ep.interaction_event_ids)):
            ev = event_map.get(event_id)
            if ev is None:
                continue
            if ev.anchor_episode_id != ep.anchor_episode_id or ev.target_trend_episode_id != ep.target_trend_episode_id or ev.target_direction is not ep.target_direction or (ev.candidate_id != ep.candidate_id):
                raise TAC_PR_QBUProgressProductionConflict('EVENT_EPISODE_LINEAGE_MISMATCH:' + event_id)
            if ev.resolution is not InteractionResolution.RESOLVED_CORRECT_SIDE or ev.break_state is BreakState.TRUE_BREAK:
                continue
            if ev.resolved_at is None:
                raise TAC_PR_QBUProgressProductionBlock('EVENT_RESOLUTION_CUTOFF_UNKNOWN:' + event_id)
            if ev.resolved_at > req.information_cutoff:
                raise TAC_PR_QBUProgressProductionConflict('FUTURE_EVENT_RESOLUTION:' + event_id)
            if event_id in seen:
                raise TAC_PR_QBUProgressProductionConflict('EVENT_MULTI_EPISODE_MEMBERSHIP:' + event_id)
            seen.add(event_id)
            rows.append((ev, segment))
    return tuple(rows)

def TAC_PR__episode_segment_stream(request: TAC_PR_QBUProgressProductionRequest, *, segment: str) -> tuple[StructuralPivot, ...]:
    base = request.update008_request
    pivot_map, duplicate_conflicts = TAC_PR__canonical_pivot_map(request.all_minor)
    if duplicate_conflicts:
        raise TAC_PR_QBUProgressProductionConflict('DIVERGENT_PIVOT_RECORD:' + ','.join(duplicate_conflicts))
    selected: list[StructuralPivot] = []
    for p in pivot_map.values():
        if p.canonical_segment_id != segment:
            continue
        if p.confirmed_at < request.trend_episode_start_cutoff:
            continue
        if request.trend_episode_terminal_cutoff is not None and p.confirmed_at > request.trend_episode_terminal_cutoff:
            continue
        if p.confirmed_at > base.information_cutoff:
            raise TAC_PR_QBUProgressProductionConflict('FUTURE_PIVOT:' + p.pivot_id)
        if p.timeframe_ms != TAC_PR_OBSERVER_TIMEFRAME_MS:
            raise TAC_PR_QBUProgressProductionConflict('PIVOT_TIMEFRAME_MISMATCH:' + p.pivot_id)
        if p.layer is not StructuralLayer.MINOR:
            raise TAC_PR_QBUProgressProductionConflict('PIVOT_LAYER_MISMATCH:' + p.pivot_id)
        selected.append(p)
    return tuple(sorted(selected, key=lambda p: (p.confirmed_at, p.pivot_id)))

def TAC_PR__reference_p0(stream: tuple[StructuralPivot, ...], p1: StructuralPivot) -> tuple[EvidenceState, StructuralPivot | None, str | None]:
    same_type = [p for p in stream if p.pivot_id != p1.pivot_id and p.pivot_type is p1.pivot_type and (p.confirmed_at < p1.confirmed_at)]
    if not same_type:
        return (EvidenceState.UNKNOWN, None, 'NO_COMPARABLE_PREDECESSOR:' + p1.pivot_id)
    latest_cutoff = max((p.confirmed_at for p in same_type))
    roots = {p.pivot_id: p for p in same_type if p.confirmed_at == latest_cutoff}
    if len(roots) != 1:
        return (EvidenceState.CONFLICT, None, 'NONUNIQUE_IMMEDIATE_PREDECESSOR:' + p1.pivot_id)
    return (EvidenceState.TRUE, next(iter(roots.values())), None)

def TAC_PR_project_qbu_progress_evidence(request: TAC_PR_QBUProgressProductionRequest) -> TAC_PR_QBUProgressProductionProjection:
    if not isinstance(request, TAC_PR_QBUProgressProductionRequest):
        raise TAC_PR_QBUProgressProductionConflict('REQUEST_SCHEMA')
    base = request.update008_request
    if base.progress_evidence:
        return TAC_PR_QBUProgressProductionProjection(state=EvidenceState.CONFLICT, progress_evidence=(), conflict_refs=('CALLER_PREPOPULATED_PROGRESS_EVIDENCE_FORBIDDEN',), provenance={'producer_id': TAC_PR_PRODUCER_ID, 'semantic_id': TAC_PR_SEMANTIC_ID})
    if base.direction not in (TrendDirection.LONG, TrendDirection.SHORT):
        return TAC_PR_QBUProgressProductionProjection(state=EvidenceState.CONFLICT, progress_evidence=(), conflict_refs=('INVALID_DIRECTION',), provenance={'producer_id': TAC_PR_PRODUCER_ID, 'semantic_id': TAC_PR_SEMANTIC_ID})
    if request.trend_episode_start_cutoff < 0:
        return TAC_PR_QBUProgressProductionProjection(state=EvidenceState.CONFLICT, progress_evidence=(), conflict_refs=('INVALID_TREND_EPISODE_START_CUTOFF',), provenance={'producer_id': TAC_PR_PRODUCER_ID, 'semantic_id': TAC_PR_SEMANTIC_ID})
    if request.trend_episode_terminal_cutoff is not None and request.trend_episode_terminal_cutoff < request.trend_episode_start_cutoff:
        return TAC_PR_QBUProgressProductionProjection(state=EvidenceState.CONFLICT, progress_evidence=(), conflict_refs=('TREND_EPISODE_INTERVAL_INVERTED',), provenance={'producer_id': TAC_PR_PRODUCER_ID, 'semantic_id': TAC_PR_SEMANTIC_ID})
    if not request.history_complete or not request.history_coverage_ref:
        return TAC_PR_QBUProgressProductionProjection(state=EvidenceState.UNKNOWN, progress_evidence=(), unknown_refs=('MINOR_HISTORY_COVERAGE_INCOMPLETE',), provenance={'producer_id': TAC_PR_PRODUCER_ID, 'semantic_id': TAC_PR_SEMANTIC_ID})
    if not request.theta_progress_parameter_ref:
        return TAC_PR_QBUProgressProductionProjection(state=EvidenceState.UNKNOWN, progress_evidence=(), unknown_refs=('THETA_PROGRESS_PARAMETER_PROVENANCE_UNKNOWN',), provenance={'producer_id': TAC_PR_PRODUCER_ID, 'semantic_id': TAC_PR_SEMANTIC_ID})
    if base.theta_progress <= 0:
        return TAC_PR_QBUProgressProductionProjection(state=EvidenceState.CONFLICT, progress_evidence=(), conflict_refs=('THETA_PROGRESS_NONPOSITIVE',), provenance={'producer_id': TAC_PR_PRODUCER_ID, 'semantic_id': TAC_PR_SEMANTIC_ID})
    try:
        target_events = TAC_PR__target_events(base)
    except TAC_PR_QBUProgressProductionConflict as exc:
        return TAC_PR_QBUProgressProductionProjection(state=EvidenceState.CONFLICT, progress_evidence=(), conflict_refs=(str(exc),), provenance={'producer_id': TAC_PR_PRODUCER_ID, 'semantic_id': TAC_PR_SEMANTIC_ID})
    except TAC_PR_QBUProgressProductionBlock as exc:
        return TAC_PR_QBUProgressProductionProjection(state=EvidenceState.UNKNOWN, progress_evidence=(), unknown_refs=(str(exc),), provenance={'producer_id': TAC_PR_PRODUCER_ID, 'semantic_id': TAC_PR_SEMANTIC_ID})
    records: list[TAC_BASE_ProgressLineageEvidence] = []
    unknown: set[str] = set()
    conflict: set[str] = set()
    stream_cache: dict[str, tuple[StructuralPivot, ...]] = {}
    for event, segment in target_events:
        try:
            stream = stream_cache.setdefault(segment, TAC_PR__episode_segment_stream(request, segment=segment))
        except TAC_PR_QBUProgressProductionConflict as exc:
            conflict.add(str(exc))
            continue
        ptype = TAC_PR__trend_side_type(base.direction)
        candidates = [p for p in stream if p.pivot_type is ptype and p.confirmed_at > event.resolved_at and (p.confirmed_at <= base.information_cutoff)]
        for p1 in candidates:
            state, p0, reason = TAC_PR__reference_p0(stream, p1)
            if state is EvidenceState.UNKNOWN:
                assert reason is not None
                unknown.add(event.event_id + ':' + reason)
                continue
            if state is EvidenceState.CONFLICT or p0 is None:
                conflict.add(event.event_id + ':' + (reason or 'REFERENCE_CONFLICT'))
                continue
            if p0.symbol != p1.symbol or p0.timeframe_ms != p1.timeframe_ms or p0.layer is not p1.layer or (p0.pivot_type is not p1.pivot_type) or (p0.canonical_segment_id != p1.canonical_segment_id) or (p0.confirmed_at >= p1.confirmed_at):
                conflict.add(event.event_id + ':P0_P1_LINEAGE_CONFLICT:' + p1.pivot_id)
                continue
            try:
                relation = same_type_progress(p0, p1, base.theta_progress)
            except ValueError:
                conflict.add(event.event_id + ':SAME_TYPE_PROGRESS_INPUT_CONFLICT:' + p1.pivot_id)
                continue
            material = relation is TAC_PR__material_relation(base.direction)
            progress = TrendSideMinorProgressEvidence(pivot_id=p1.pivot_id, confirmed_at=p1.confirmed_at, material_progress=material, timeframe_ms=TAC_PR_OBSERVER_TIMEFRAME_MS, layer='MINOR')
            records.append(TAC_BASE_ProgressLineageEvidence(event_id=event.event_id, progress=progress, target_trend_episode_id=base.trend_episode_id, direction=base.direction, canonical_segment_id=segment, continuity_intact=True, provenance={'producer_id': TAC_PR_PRODUCER_ID, 'semantic_id': TAC_PR_SEMANTIC_ID, 'semantic_contract_blob': TAC_PR_SEMANTIC_CONTRACT_BLOB, 'semantic_freeze_manifest_blob': TAC_PR_SEMANTIC_FREEZE_MANIFEST_BLOB, 'history_coverage_ref': request.history_coverage_ref, 'p0_pivot_id': p0.pivot_id, 'p0_confirmed_at': str(p0.confirmed_at), 'p0_extreme_price': str(p0.extreme_price), 'p0_scale_at_extreme': str(p0.scale_at_extreme), 'p1_pivot_id': p1.pivot_id, 'p1_confirmed_at': str(p1.confirmed_at), 'p1_extreme_price': str(p1.extreme_price), 'same_type_progress_relation': relation.value, 'theta_progress_parameter_ref': request.theta_progress_parameter_ref, 'information_cutoff': str(base.information_cutoff)}))
    if conflict:
        return TAC_PR_QBUProgressProductionProjection(state=EvidenceState.CONFLICT, progress_evidence=(), conflict_refs=tuple(sorted(conflict)), provenance={'producer_id': TAC_PR_PRODUCER_ID, 'semantic_id': TAC_PR_SEMANTIC_ID})
    if unknown:
        return TAC_PR_QBUProgressProductionProjection(state=EvidenceState.UNKNOWN, progress_evidence=(), unknown_refs=tuple(sorted(unknown)), provenance={'producer_id': TAC_PR_PRODUCER_ID, 'semantic_id': TAC_PR_SEMANTIC_ID})
    canonical_records: dict[tuple[str, str], TAC_BASE_ProgressLineageEvidence] = {}
    for rec in records:
        key = (rec.event_id, rec.progress.pivot_id)
        old = canonical_records.get(key)
        if old is not None and old != rec:
            return TAC_PR_QBUProgressProductionProjection(state=EvidenceState.CONFLICT, progress_evidence=(), conflict_refs=('DIVERGENT_PROGRESS_RECORD:' + rec.event_id + ':' + rec.progress.pivot_id,), provenance={'producer_id': TAC_PR_PRODUCER_ID, 'semantic_id': TAC_PR_SEMANTIC_ID})
        canonical_records[key] = rec
    output = tuple((canonical_records[k] for k in sorted(canonical_records, key=lambda k: (k[0], canonical_records[k].progress.confirmed_at, canonical_records[k].progress.pivot_id))))
    return TAC_PR_QBUProgressProductionProjection(state=EvidenceState.TRUE, progress_evidence=output, unknown_refs=(), conflict_refs=(), provenance={'producer_id': TAC_PR_PRODUCER_ID, 'semantic_id': TAC_PR_SEMANTIC_ID, 'runtime_consumer_blob': TAC_PR_RUNTIME_CONSUMER_BLOB, 'history_coverage_ref': request.history_coverage_ref, 'theta_progress_parameter_ref': request.theta_progress_parameter_ref, 'f9_stage': 'POST_UPDATE007_PRE_UPDATE008', 'scientific_state_mutated': 'false', 'real_market_data_read': 'false', 'test_read': 'false', 'pnl': 'false', 'trading': 'FORBIDDEN'})

def TAC_PR_bind_update008_request(request: TAC_BASE_Update008Request, projection: TAC_PR_QBUProgressProductionProjection) -> TAC_BASE_Update008Request:
    if not isinstance(request, TAC_BASE_Update008Request):
        raise TAC_PR_QBUProgressProductionConflict('UPDATE008_REQUEST_SCHEMA')
    if request.progress_evidence:
        raise TAC_PR_QBUProgressProductionConflict('CALLER_PREPOPULATED_PROGRESS_EVIDENCE_FORBIDDEN')
    if projection.state is not EvidenceState.TRUE:
        raise TAC_PR_QBUProgressProductionBlock('TRUE_PROGRESS_PROJECTION_REQUIRED')
    return replace(request, progress_evidence=projection.progress_evidence, provenance={**dict(request.provenance), 'qbu_progress_producer_id': TAC_PR_PRODUCER_ID, 'qbu_progress_semantic_id': TAC_PR_SEMANTIC_ID})
