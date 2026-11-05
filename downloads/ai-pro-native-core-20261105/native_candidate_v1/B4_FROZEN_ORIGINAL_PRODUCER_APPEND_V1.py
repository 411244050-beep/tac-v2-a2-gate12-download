from dataclasses import dataclass, field, fields, is_dataclass
from enum import Enum
from fractions import Fraction
import hashlib
import json
MappingProxyType = type(type.__dict__)
from typing import Any, Callable, Mapping
SEMANTIC_VERSION = 'D2_TO_B4_D4_CAUSAL_EVIDENCE_PRODUCER_V1'
CONTRACT_ID = 'TAC_D2_TO_B4_D4_CAUSAL_EVIDENCE_SCIENTIFIC_CONVENTION_CONTRACT_V1'

class EvidenceState(str, Enum):
    TRUE = 'TRUE'
    FALSE = 'FALSE'
    UNKNOWN = 'UNKNOWN'
    CONFLICT = 'CONFLICT'

class ProducerRuntimeBlock(RuntimeError):
    pass

@dataclass(frozen=True)
class ClosedPriceObservation:
    information_cutoff: int
    close: Fraction
    provenance: Mapping[str, str] = field(default_factory=dict)

@dataclass(frozen=True)
class LineageContext:
    symbol: str
    target_trend_episode_id: str
    direction: TrendDirection
    information_cutoff: int
    canonical_segment_id: str
    interaction_event_id: str | None = None
    market_event_id: str | None = None
    source_evidence_refs: tuple[str, ...] = ()
    continuity_known: bool = True
    continuity_intact: bool = True
    same_cutoff_order_proven: bool = True

@dataclass(frozen=True)
class ProjectionResult:
    producer: str
    state: EvidenceState
    reason: str
    consumer_evidence: Any | None
    provenance: Mapping[str, str]

    @property
    def executable_positive(self) -> bool:
        return self.state is EvidenceState.TRUE and self.consumer_evidence is not None

@dataclass(frozen=True)
class StructuralAcceptanceRequest:
    context: LineageContext
    interaction: InteractionEvent
    pivots: tuple[StructuralPivot, ...]
    separation_origin_open_time: int
    separation_cutoff: int
    theta_progress: Fraction
    prior_reclaim_cutoffs: tuple[int, ...]

@dataclass(frozen=True)
class CorrectSideRecoveryRequest:
    context: LineageContext
    interaction: InteractionEvent
    pivots: tuple[StructuralPivot, ...]
    attempt_origin_open_time: int
    attempt_cutoff: int
    evaluating_close: Fraction

@dataclass(frozen=True)
class LocalTrendControlRegainRequest:
    context: LineageContext
    pivots: tuple[StructuralPivot, ...]
    adverse_reference_pivot_id: str
    theta_progress: Fraction
    closed_prices: tuple[ClosedPriceObservation, ...]

def _encode(value: Any) -> Any:
    if isinstance(value, Fraction):
        return {'$fraction': [value.numerator, value.denominator]}
    if isinstance(value, Enum):
        return {'$enum': [value.__class__.__module__, value.__class__.__qualname__, value.value]}
    if isinstance(value, MappingProxyType):
        value = dict(value)
    if is_dataclass(value):
        return {'$dataclass': [value.__class__.__module__, value.__class__.__qualname__], 'fields': {f.name: _encode(getattr(value, f.name)) for f in fields(value)}}
    if isinstance(value, Mapping):
        return {str(k): _encode(value[k]) for k in sorted(value, key=lambda x: str(x))}
    if isinstance(value, tuple):
        return [_encode(x) for x in value]
    if isinstance(value, list):
        return [_encode(x) for x in value]
    if isinstance(value, set):
        return sorted((_encode(x) for x in value), key=lambda x: json.dumps(x, sort_keys=True))
    return value

def exact_json(value: Any) -> str:
    return json.dumps(_encode(value), sort_keys=True, separators=(',', ':'), ensure_ascii=False)

def digest(value: Any) -> str:
    return hashlib.sha256(exact_json(value).encode()).hexdigest()

def _adverse_type(direction: TrendDirection) -> PivotType:
    if direction is TrendDirection.LONG:
        return PivotType.LOW
    if direction is TrendDirection.SHORT:
        return PivotType.HIGH
    raise ProducerRuntimeBlock('LONG_OR_SHORT_REQUIRED')

def _favorable_type(direction: TrendDirection) -> PivotType:
    return PivotType.HIGH if direction is TrendDirection.LONG else PivotType.LOW

def _pivot_shape_ok(p: StructuralPivot, ctx: LineageContext) -> bool:
    return p.symbol == ctx.symbol and p.timeframe_ms == OBSERVER_TIMEFRAME_MS and (p.layer is StructuralLayer.MINOR) and (p.canonical_segment_id == ctx.canonical_segment_id)

def _pivot_provenance_ok(p: StructuralPivot) -> bool:
    return bool(p.pivot_id and p.canonical_segment_id and p.provenance)

def _pivot_available(p: StructuralPivot, ctx: LineageContext) -> bool:
    if p.confirmed_at > ctx.information_cutoff:
        return False
    if p.confirmed_at == ctx.information_cutoff and (not ctx.same_cutoff_order_proven):
        return False
    return True

def _base_context_state(ctx: LineageContext) -> tuple[EvidenceState | None, str]:
    if ctx.direction not in (TrendDirection.LONG, TrendDirection.SHORT):
        return (EvidenceState.CONFLICT, 'DIRECTION_NOT_LONG_SHORT')
    if not ctx.symbol or not ctx.target_trend_episode_id or (not ctx.canonical_segment_id):
        return (EvidenceState.UNKNOWN, 'MANDATORY_LINEAGE_MISSING')
    if not ctx.source_evidence_refs:
        return (EvidenceState.UNKNOWN, 'SOURCE_EVIDENCE_REFS_MISSING')
    if not ctx.continuity_known or not ctx.continuity_intact:
        return (EvidenceState.UNKNOWN, 'CANONICAL_CONTINUITY_NOT_AUTHORITATIVE')
    return (None, 'OK')

def _interaction_state(ctx: LineageContext, event: InteractionEvent) -> tuple[EvidenceState | None, str]:
    base, reason = _base_context_state(ctx)
    if base is not None:
        return (base, reason)
    if ctx.interaction_event_id is None:
        return (EvidenceState.UNKNOWN, 'INTERACTION_EVENT_ID_MISSING')
    if event.event_id != ctx.interaction_event_id:
        return (EvidenceState.CONFLICT, 'INTERACTION_EVENT_ID_MISMATCH')
    if event.target_trend_episode_id != ctx.target_trend_episode_id:
        return (EvidenceState.CONFLICT, 'TARGET_TREND_EPISODE_MISMATCH')
    if event.target_direction is not ctx.direction:
        return (EvidenceState.CONFLICT, 'DIRECTION_LINEAGE_MISMATCH')
    for cutoff in (event.started_at, event.armed_at, event.approach_lineage_started_at, event.resolved_at):
        if cutoff is not None and cutoff > ctx.information_cutoff:
            return (EvidenceState.CONFLICT, 'FUTURE_INTERACTION_STATE')
    return (None, 'OK')

def _eligible_local_stream(pivots: tuple[StructuralPivot, ...], ctx: LineageContext, *, after_cutoff: int | None=None, extreme_not_before: int | None=None) -> tuple[EvidenceState, tuple[StructuralPivot, ...], str]:
    rows = []
    for p in pivots:
        if not _pivot_shape_ok(p, ctx):
            continue
        if after_cutoff is not None and p.confirmed_at <= after_cutoff:
            continue
        if extreme_not_before is not None and p.extreme_last_time < extreme_not_before:
            continue
        if not _pivot_available(p, ctx):
            continue
        if not _pivot_provenance_ok(p):
            return (EvidenceState.UNKNOWN, (), 'PIVOT_PROVENANCE_MISSING')
        rows.append(p)
    by_id: dict[str, list[StructuralPivot]] = {}
    by_cutoff: dict[int, list[StructuralPivot]] = {}
    for p in rows:
        by_id.setdefault(p.pivot_id, []).append(p)
        by_cutoff.setdefault(p.confirmed_at, []).append(p)
    if any((len(v) != 1 for v in by_id.values())):
        return (EvidenceState.CONFLICT, (), 'DUPLICATE_PIVOT_ID')
    if any((len(v) > 1 for v in by_cutoff.values())):
        return (EvidenceState.CONFLICT, (), 'SAME_CUTOFF_EXCLUSIVE_ROLE_AMBIGUITY')
    ordered = tuple(sorted(rows, key=lambda p: p.confirmed_at))
    for left, right in zip(ordered, ordered[1:]):
        if left.pivot_type is right.pivot_type:
            return (EvidenceState.CONFLICT, (), 'NONALTERNATING_LOCAL_PIVOT_STREAM')
    return (EvidenceState.TRUE, ordered, 'OK')

def _provenance(ctx: LineageContext, *, producer: str, pivots: tuple[StructuralPivot, ...]=(), turning_pivot: StructuralPivot | None=None, adverse_reference: StructuralPivot | None=None, recovery_pivot: StructuralPivot | None=None, evaluating_close: Fraction | None=None, information_cutoff: int | None=None) -> Mapping[str, str]:
    cutoff = ctx.information_cutoff if information_cutoff is None else information_cutoff
    pivot_rows = tuple(dict.fromkeys((p.pivot_id for p in pivots)))
    confirmations = {p.pivot_id: p.confirmed_at for p in pivots}
    values = {'semantic_version': SEMANTIC_VERSION, 'producer_semantic_contract_id': CONTRACT_ID, 'producer': producer, 'symbol': ctx.symbol, 'source_timeframe_ms': str(OBSERVER_TIMEFRAME_MS), 'structural_layer': 'MINOR', 'information_cutoff': str(cutoff), 'target_trend_episode_id': ctx.target_trend_episode_id, 'direction': ctx.direction.value, 'interaction_event_id': ctx.interaction_event_id or '', 'market_event_id': ctx.market_event_id or '', 'canonical_segment_id': ctx.canonical_segment_id, 'source_d2_structure_ids': json.dumps([f'StructuralPivot:{x}' for x in pivot_rows], separators=(',', ':')), 'source_pivot_ids': json.dumps(list(pivot_rows), separators=(',', ':')), 'pivot_confirmation_cutoffs': json.dumps(confirmations, sort_keys=True, separators=(',', ':')), 'adverse_reference_pivot_id': '' if adverse_reference is None else adverse_reference.pivot_id, 'turning_pivot_id': '' if turning_pivot is None else turning_pivot.pivot_id, 'recovery_pivot_id': '' if recovery_pivot is None else recovery_pivot.pivot_id, 'recovery_pivot_role': '' if recovery_pivot is None else 'FIRST_CAUSAL_FAVORABLE_MINOR_AFTER_ROLE_SCOPED_ADVERSE_OR_TURN', 'exact_recovery_reference_price': '' if recovery_pivot is None else str(recovery_pivot.extreme_price), 'exact_evaluating_close': '' if evaluating_close is None else str(evaluating_close), 'source_evidence_refs': json.dumps(list(ctx.source_evidence_refs), separators=(',', ':')), 'continuity_provenance': 'KNOWN_INTACT' if ctx.continuity_known and ctx.continuity_intact else 'NOT_AUTHORITATIVE'}
    return MappingProxyType(dict(sorted(values.items())))

def _result(producer: str, state: EvidenceState, reason: str, ctx: LineageContext, *, consumer: Any | None=None, pivots: tuple[StructuralPivot, ...]=(), turning_pivot: StructuralPivot | None=None, adverse_reference: StructuralPivot | None=None, recovery_pivot: StructuralPivot | None=None, evaluating_close: Fraction | None=None, information_cutoff: int | None=None) -> ProjectionResult:
    return ProjectionResult(producer=producer, state=state, reason=reason, consumer_evidence=consumer, provenance=_provenance(ctx, producer=producer, pivots=pivots, turning_pivot=turning_pivot, adverse_reference=adverse_reference, recovery_pivot=recovery_pivot, evaluating_close=evaluating_close, information_cutoff=information_cutoff))

def material_original_direction_closed_price_recovery(*, ctx: LineageContext, recovery_pivot: StructuralPivot | None, evaluating_close: Fraction) -> ProjectionResult:
    producer = 'MATERIAL_ORIGINAL_DIRECTION_CLOSED_PRICE_RECOVERY_V1'
    base, reason = _base_context_state(ctx)
    if base is not None:
        return _result(producer, base, reason, ctx, recovery_pivot=recovery_pivot, evaluating_close=evaluating_close)
    if recovery_pivot is None:
        return _result(producer, EvidenceState.UNKNOWN, 'RECOVERY_PIVOT_NOT_AVAILABLE', ctx, evaluating_close=evaluating_close)
    if not _pivot_shape_ok(recovery_pivot, ctx):
        return _result(producer, EvidenceState.CONFLICT, 'RECOVERY_PIVOT_LINEAGE_OR_SEGMENT_MISMATCH', ctx, recovery_pivot=recovery_pivot, evaluating_close=evaluating_close)
    if recovery_pivot.pivot_type is not _favorable_type(ctx.direction):
        return _result(producer, EvidenceState.CONFLICT, 'RECOVERY_PIVOT_ROLE_MISMATCH', ctx, recovery_pivot=recovery_pivot, evaluating_close=evaluating_close)
    if not _pivot_provenance_ok(recovery_pivot):
        return _result(producer, EvidenceState.UNKNOWN, 'RECOVERY_PIVOT_PROVENANCE_MISSING', ctx, recovery_pivot=recovery_pivot, evaluating_close=evaluating_close)
    if not _pivot_available(recovery_pivot, ctx):
        return _result(producer, EvidenceState.UNKNOWN, 'RECOVERY_PIVOT_NOT_CAUSALLY_AVAILABLE', ctx, recovery_pivot=recovery_pivot, evaluating_close=evaluating_close)
    passed = evaluating_close > recovery_pivot.extreme_price if ctx.direction is TrendDirection.LONG else evaluating_close < recovery_pivot.extreme_price
    state = EvidenceState.TRUE if passed else EvidenceState.FALSE
    return _result(producer, state, 'STRICT_RECOVERY_CROSS_TRUE' if passed else 'STRICT_RECOVERY_CROSS_FALSE', ctx, pivots=(recovery_pivot,), recovery_pivot=recovery_pivot, evaluating_close=evaluating_close)

def produce_structural_acceptance(req: StructuralAcceptanceRequest) -> ProjectionResult:
    producer = 'B4_STRUCTURAL_ACCEPTANCE_D2_PROJECTION_V1'
    state, reason = _interaction_state(req.context, req.interaction)
    if state is not None:
        return _result(producer, state, reason, req.context)
    if req.interaction.terminal and req.interaction.resolution is InteractionResolution.RESOLVED_CORRECT_SIDE:
        consumer = StructuralAcceptanceEvidence()
        return _result(producer, EvidenceState.FALSE, 'INTERACTION_ALREADY_RESOLVED_CORRECT_SIDE', req.context, consumer=consumer)
    if req.separation_cutoff >= req.context.information_cutoff:
        return _result(producer, EvidenceState.UNKNOWN, 'POST_SEPARATION_STRUCTURE_NOT_YET_CAUSAL', req.context)
    if any((x > req.context.information_cutoff for x in req.prior_reclaim_cutoffs)):
        return _result(producer, EvidenceState.CONFLICT, 'FUTURE_RECLAIM_HISTORY', req.context)
    stream_state, stream, stream_reason = _eligible_local_stream(req.pivots, req.context, after_cutoff=req.separation_cutoff, extreme_not_before=req.separation_origin_open_time)
    if stream_state is not EvidenceState.TRUE:
        return _result(producer, stream_state, stream_reason, req.context)
    adverse = _adverse_type(req.context.direction)
    p0 = next((p for p in stream if p.pivot_type is adverse), None)
    if p0 is None:
        return _result(producer, EvidenceState.UNKNOWN, 'P0_NOT_YET_AVAILABLE', req.context)
    p1 = None
    for p in stream:
        if p.confirmed_at <= p0.confirmed_at or p.pivot_type is not adverse:
            continue
        relation = same_type_progress(p0, p, req.theta_progress)
        material = relation is ProgressRelation.MATERIAL_ADVANCE_DOWN if req.context.direction is TrendDirection.LONG else relation is ProgressRelation.MATERIAL_ADVANCE_UP
        if material:
            p1 = p
            break
    if p1 is None:
        return _result(producer, EvidenceState.UNKNOWN, 'P1_MATERIAL_WRONG_SIDE_PROGRESS_NOT_YET_AVAILABLE', req.context, pivots=(p0,))
    had_prior_reclaim = any((x < p1.confirmed_at for x in req.prior_reclaim_cutoffs))
    consumer = StructuralAcceptanceEvidence(continuation_acceptance=not had_prior_reclaim, failed_return_acceptance=had_prior_reclaim, confirmed_wrong_side_minor_extreme_id=p0.pivot_id, renewed_wrong_side_progress_pivot_id=p1.pivot_id if not had_prior_reclaim else None, failed_return_progress_pivot_id=p1.pivot_id if had_prior_reclaim else None)
    return _result(producer, EvidenceState.TRUE, 'FAILED_RETURN_ACCEPTANCE' if had_prior_reclaim else 'CONTINUATION_ACCEPTANCE', req.context, consumer=consumer, pivots=(p0, p1))

def produce_correct_side_recovery(req: CorrectSideRecoveryRequest) -> ProjectionResult:
    producer = 'B4_CORRECT_SIDE_RECOVERY_D2_PROJECTION_V1'
    state, reason = _interaction_state(req.context, req.interaction)
    if state is not None:
        return _result(producer, state, reason, req.context, evaluating_close=req.evaluating_close)
    if not req.interaction.attempted_wrong_side_acceptance:
        return _result(producer, EvidenceState.UNKNOWN, 'ATTEMPTED_WRONG_SIDE_ACCEPTANCE_NOT_ESTABLISHED', req.context, evaluating_close=req.evaluating_close)
    if req.interaction.terminal and req.interaction.resolution is InteractionResolution.RESOLVED_WRONG_SIDE:
        consumer = CorrectSideRecoveryEvidence()
        return _result(producer, EvidenceState.FALSE, 'INTERACTION_ALREADY_RESOLVED_WRONG_SIDE', req.context, consumer=consumer, evaluating_close=req.evaluating_close)
    stream_state, stream, stream_reason = _eligible_local_stream(req.pivots, req.context, after_cutoff=req.attempt_cutoff, extreme_not_before=req.attempt_origin_open_time)
    if stream_state is not EvidenceState.TRUE:
        return _result(producer, stream_state, stream_reason, req.context, evaluating_close=req.evaluating_close)
    adverse = _adverse_type(req.context.direction)
    favorable = _favorable_type(req.context.direction)
    turning = next((p for p in stream if p.pivot_type is adverse), None)
    if turning is None:
        return _result(producer, EvidenceState.UNKNOWN, 'TURNING_PIVOT_NOT_YET_AVAILABLE', req.context, evaluating_close=req.evaluating_close)
    recovery = next((p for p in stream if p.confirmed_at > turning.confirmed_at and p.pivot_type is favorable), None)
    if recovery is None:
        return _result(producer, EvidenceState.UNKNOWN, 'RECOVERY_PIVOT_NOT_YET_AVAILABLE', req.context, pivots=(turning,), turning_pivot=turning, evaluating_close=req.evaluating_close)
    primitive = material_original_direction_closed_price_recovery(ctx=req.context, recovery_pivot=recovery, evaluating_close=req.evaluating_close)
    if primitive.state in (EvidenceState.UNKNOWN, EvidenceState.CONFLICT):
        return _result(producer, primitive.state, f'RECOVERY_PRIMITIVE_{primitive.reason}', req.context, pivots=(turning, recovery), turning_pivot=turning, recovery_pivot=recovery, evaluating_close=req.evaluating_close)
    passed = primitive.state is EvidenceState.TRUE
    consumer = CorrectSideRecoveryEvidence(turning_structure_confirmed=True, material_correct_side_structural_recovery=passed, turning_pivot_id=turning.pivot_id, recovery_pivot_id=recovery.pivot_id)
    return _result(producer, EvidenceState.TRUE if passed else EvidenceState.FALSE, 'TURNING_AND_MATERIAL_RECOVERY_TRUE' if passed else 'TURNING_TRUE_RECOVERY_FALSE', req.context, consumer=consumer, pivots=(turning, recovery), turning_pivot=turning, recovery_pivot=recovery, evaluating_close=req.evaluating_close)

def _closed_price_rows(observations: tuple[ClosedPriceObservation, ...], ctx: LineageContext) -> tuple[EvidenceState, tuple[ClosedPriceObservation, ...], str]:
    rows = [x for x in observations if x.information_cutoff <= ctx.information_cutoff]
    by_cutoff: dict[int, list[ClosedPriceObservation]] = {}
    for x in rows:
        if not x.provenance:
            return (EvidenceState.UNKNOWN, (), 'CLOSE_PROVENANCE_MISSING')
        by_cutoff.setdefault(x.information_cutoff, []).append(x)
    if any((len(v) > 1 for v in by_cutoff.values())):
        return (EvidenceState.CONFLICT, (), 'DUPLICATE_CLOSE_CUTOFF')
    return (EvidenceState.TRUE, tuple(sorted(rows, key=lambda x: x.information_cutoff)), 'OK')

def produce_local_trend_control_regain(req: LocalTrendControlRegainRequest) -> ProjectionResult:
    producer = 'LOCAL_TREND_CONTROL_REGAIN_D2_PROJECTION_V1'
    base, reason = _base_context_state(req.context)
    if base is not None:
        return _result(producer, base, reason, req.context)
    matches = [p for p in req.pivots if p.pivot_id == req.adverse_reference_pivot_id]
    if not matches:
        return _result(producer, EvidenceState.UNKNOWN, 'FIXED_ADVERSE_REFERENCE_MISSING', req.context)
    if len(matches) != 1:
        return _result(producer, EvidenceState.CONFLICT, 'FIXED_ADVERSE_REFERENCE_NONUNIQUE', req.context)
    adverse = matches[0]
    if not _pivot_shape_ok(adverse, req.context):
        return _result(producer, EvidenceState.CONFLICT, 'FIXED_ADVERSE_REFERENCE_LINEAGE_MISMATCH', req.context, adverse_reference=adverse)
    if adverse.pivot_type is not _adverse_type(req.context.direction):
        return _result(producer, EvidenceState.CONFLICT, 'FIXED_ADVERSE_REFERENCE_ROLE_MISMATCH', req.context, adverse_reference=adverse)
    if not _pivot_provenance_ok(adverse):
        return _result(producer, EvidenceState.UNKNOWN, 'FIXED_ADVERSE_REFERENCE_PROVENANCE_MISSING', req.context, adverse_reference=adverse)
    if not _pivot_available(adverse, req.context):
        return _result(producer, EvidenceState.UNKNOWN, 'FIXED_ADVERSE_REFERENCE_NOT_CAUSAL', req.context, adverse_reference=adverse)
    same_cutoff_competitors = [p for p in req.pivots if p.pivot_id != adverse.pivot_id and _pivot_shape_ok(p, req.context) and (p.confirmed_at == adverse.confirmed_at)]
    if same_cutoff_competitors:
        return _result(producer, EvidenceState.CONFLICT, 'FIXED_ADVERSE_REFERENCE_SAME_CUTOFF_ROLE_AMBIGUITY', req.context, adverse_reference=adverse)
    stream_state, stream, stream_reason = _eligible_local_stream(req.pivots, req.context, after_cutoff=adverse.confirmed_at)
    if stream_state is not EvidenceState.TRUE:
        return _result(producer, stream_state, stream_reason, req.context, adverse_reference=adverse)
    favorable = _favorable_type(req.context.direction)
    adverse_type = _adverse_type(req.context.direction)
    if not stream:
        return _result(producer, EvidenceState.UNKNOWN, 'RECOVERY_PIVOT_NOT_YET_AVAILABLE', req.context, pivots=(adverse,), adverse_reference=adverse)
    if stream[0].pivot_type is not favorable:
        return _result(producer, EvidenceState.CONFLICT, 'FIRST_POST_REFERENCE_PIVOT_NOT_FAVORABLE', req.context, pivots=(adverse, stream[0]), adverse_reference=adverse)
    recovery = stream[0]
    if len(stream) < 2:
        return _result(producer, EvidenceState.UNKNOWN, 'POST_RECOVERY_ADVERSE_PIVOT_NOT_YET_AVAILABLE', req.context, pivots=(adverse, recovery), adverse_reference=adverse, recovery_pivot=recovery)
    if stream[1].pivot_type is not adverse_type:
        return _result(producer, EvidenceState.CONFLICT, 'FIRST_POST_RECOVERY_PIVOT_NOT_ADVERSE', req.context, pivots=(adverse, recovery, stream[1]), adverse_reference=adverse, recovery_pivot=recovery)
    later_adverse = stream[1]
    relation = same_type_progress(adverse, later_adverse, req.theta_progress)
    countertrend_failed = not (relation is ProgressRelation.MATERIAL_ADVANCE_DOWN if req.context.direction is TrendDirection.LONG else relation is ProgressRelation.MATERIAL_ADVANCE_UP)
    close_state, closes, close_reason = _closed_price_rows(req.closed_prices, req.context)
    if close_state is not EvidenceState.TRUE:
        return _result(producer, close_state, close_reason, req.context, pivots=(adverse, recovery, later_adverse), adverse_reference=adverse, recovery_pivot=recovery)
    role_ready_cutoff = max(recovery.confirmed_at, later_adverse.confirmed_at)
    eligible_closes = tuple((x for x in closes if x.information_cutoff >= role_ready_cutoff))
    if not eligible_closes:
        return _result(producer, EvidenceState.UNKNOWN, 'NO_CAUSAL_CLOSE_AFTER_ROLE_COMPLETION', req.context, pivots=(adverse, recovery, later_adverse), adverse_reference=adverse, recovery_pivot=recovery)
    if not countertrend_failed:
        latest = eligible_closes[-1]
        consumer = LocalTrendControlRegainEvidence(direction=req.context.direction, adverse_reference_pivot_id=adverse.pivot_id, adverse_reference_confirmed_at=adverse.confirmed_at, recovery_pivot_id=recovery.pivot_id, recovery_pivot_confirmed_at=recovery.confirmed_at, countertrend_progression_failed=InfoValue.known(False), material_original_direction_closed_price_recovery=InfoValue.known(latest.close > recovery.extreme_price if req.context.direction is TrendDirection.LONG else latest.close < recovery.extreme_price), confirmation_cutoff=later_adverse.confirmed_at, provenance={})
        prov = _provenance(req.context, producer=producer, pivots=(adverse, recovery, later_adverse), adverse_reference=adverse, recovery_pivot=recovery, evaluating_close=latest.close, information_cutoff=later_adverse.confirmed_at)
        consumer = LocalTrendControlRegainEvidence(direction=consumer.direction, adverse_reference_pivot_id=consumer.adverse_reference_pivot_id, adverse_reference_confirmed_at=consumer.adverse_reference_confirmed_at, recovery_pivot_id=consumer.recovery_pivot_id, recovery_pivot_confirmed_at=consumer.recovery_pivot_confirmed_at, countertrend_progression_failed=consumer.countertrend_progression_failed, material_original_direction_closed_price_recovery=consumer.material_original_direction_closed_price_recovery, confirmation_cutoff=consumer.confirmation_cutoff, provenance=prov)
        return ProjectionResult(producer, EvidenceState.FALSE, 'COUNTERTREND_MATERIAL_ADVANCE_CONTINUES', consumer, prov)
    first_true: ClosedPriceObservation | None = None
    for x in eligible_closes:
        if x.information_cutoff == role_ready_cutoff and (not req.context.same_cutoff_order_proven):
            continue
        passed = x.close > recovery.extreme_price if req.context.direction is TrendDirection.LONG else x.close < recovery.extreme_price
        if passed:
            first_true = x
            break
    latest = eligible_closes[-1]
    if first_true is None:
        prov = _provenance(req.context, producer=producer, pivots=(adverse, recovery, later_adverse), adverse_reference=adverse, recovery_pivot=recovery, evaluating_close=latest.close)
        consumer = LocalTrendControlRegainEvidence(direction=req.context.direction, adverse_reference_pivot_id=adverse.pivot_id, adverse_reference_confirmed_at=adverse.confirmed_at, recovery_pivot_id=recovery.pivot_id, recovery_pivot_confirmed_at=recovery.confirmed_at, countertrend_progression_failed=InfoValue.known(True), material_original_direction_closed_price_recovery=InfoValue.known(False), confirmation_cutoff=req.context.information_cutoff, provenance=prov)
        return ProjectionResult(producer, EvidenceState.FALSE, 'RECOVERY_CLOSE_NOT_YET_STRICTLY_CROSSED', consumer, prov)
    prov = _provenance(req.context, producer=producer, pivots=(adverse, recovery, later_adverse), adverse_reference=adverse, recovery_pivot=recovery, evaluating_close=first_true.close, information_cutoff=first_true.information_cutoff)
    consumer = LocalTrendControlRegainEvidence(direction=req.context.direction, adverse_reference_pivot_id=adverse.pivot_id, adverse_reference_confirmed_at=adverse.confirmed_at, recovery_pivot_id=recovery.pivot_id, recovery_pivot_confirmed_at=recovery.confirmed_at, countertrend_progression_failed=InfoValue.known(True), material_original_direction_closed_price_recovery=InfoValue.known(True), confirmation_cutoff=first_true.information_cutoff, provenance=prov)
    return ProjectionResult(producer, EvidenceState.TRUE, 'LOCAL_TREND_CONTROL_REGAIN_TRUE', consumer, prov)

def safe_b4_consumer(result: ProjectionResult) -> Any | None:
    if result.state in (EvidenceState.UNKNOWN, EvidenceState.CONFLICT):
        return None
    return result.consumer_evidence

def projection_to_info_value(result: ProjectionResult) -> InfoValue[bool]:
    if result.state is EvidenceState.TRUE:
        return InfoValue.known(True)
    if result.state is EvidenceState.FALSE:
        return InfoValue.known(False)
    if result.state is EvidenceState.UNKNOWN:
        return InfoValue.unknown()
    return InfoValue.error(f'PROJECTION_CONFLICT:{result.reason}')

class ProducerTransactionRuntimeV1:
    """Digest-only persistence wrapper around pure projections.

    Results are recomputed on replay and checked against the committed result digest.
    A failed projection never mutates transaction state.
    """

    def __init__(self, records: Mapping[str, tuple[str, str]] | None=None):
        self._records = dict(records or {})

    def process(self, tx_id: str, request: Any, producer: Callable[[Any], ProjectionResult]) -> ProjectionResult:
        if not tx_id:
            raise ProducerRuntimeBlock('TX_ID_REQUIRED')
        input_digest = digest(request)
        prior = self._records.get(tx_id)
        if prior is not None and prior[0] != input_digest:
            raise ProducerRuntimeBlock('SAME_TX_INPUT_MISMATCH')
        result = producer(request)
        result_digest = digest(result)
        if prior is not None:
            if prior[1] != result_digest:
                raise ProducerRuntimeBlock('RESTART_OR_REPLAY_RESULT_MISMATCH')
            return result
        self._records[tx_id] = (input_digest, result_digest)
        return result

    def export_state(self) -> Mapping[str, tuple[str, str]]:
        return MappingProxyType(dict(sorted(self._records.items())))

    @classmethod
    def restore_state(cls, state: Mapping[str, tuple[str, str]]) -> 'ProducerTransactionRuntimeV1':
        return cls(records=state)
