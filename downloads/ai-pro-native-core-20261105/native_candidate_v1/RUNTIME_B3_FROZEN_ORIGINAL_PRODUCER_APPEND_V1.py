from copy import deepcopy
from dataclasses import dataclass, field, replace
from fractions import Fraction
from hashlib import sha256
import json
from typing import Any, Callable, Iterable, Mapping
PRODUCER_ID = 'RUNTIME_B3_PRICE_DRIVEN_RETURN_PRODUCTION_STATE_PRODUCER_V1'
SEMANTIC_ID = 'RUNTIME_B3_PRICE_DRIVEN_RETURN_CAUSAL_ORIGIN_ORDER_V1'
OBSERVER_TIMEFRAME_MS = 900000
STAGE3B_BINDING_DETERMINISTIC_SHA256 = '580be20518ad4a63909021d04284ffd96959e822dfd21c03092bc9729769c667'

class RuntimeB3Block(RuntimeError):
    pass

class RuntimeB3Conflict(RuntimeB3Block):
    pass

def _exact(value: Fraction) -> str:
    if not isinstance(value, Fraction):
        raise RuntimeB3Conflict('NON_EXACT_FRACTION_INPUT')
    return f'{value.numerator}/{value.denominator}'

def _parse_exact(value: str) -> Fraction:
    if not isinstance(value, str) or '/' not in value:
        raise RuntimeB3Conflict('INVALID_EXACT_FRACTION_ENCODING')
    a, b = value.split('/', 1)
    out = Fraction(int(a), int(b))
    if _exact(out) != value:
        raise RuntimeB3Conflict('NON_CANONICAL_EXACT_FRACTION_ENCODING')
    return out

def _enum_value(value: Any) -> str:
    raw = getattr(value, 'value', None)
    if not isinstance(raw, str) or not raw:
        raise RuntimeB3Conflict('ENUM_VALUE_REQUIRED')
    return raw

def _lineage_key(symbol: str, candidate_id: str) -> str:
    if not symbol or not candidate_id:
        raise RuntimeB3Conflict('LINEAGE_IDENTITY_REQUIRED')
    return symbol + '\x1f' + candidate_id

def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)

def _digest_record(value: Any) -> str:
    return sha256(_canonical_json(value).encode('utf-8')).hexdigest()

def _evidence_record(evidence: PriceDrivenReturnEvidence | None) -> Any:
    if evidence is None:
        return None
    return {'passed': bool(evidence.passed), 'adverse_raw_movement': _exact(evidence.adverse_raw_movement), 'minimum_required': _exact(evidence.minimum_required), 'provenance': [[str(k), str(v)] for k, v in evidence.provenance.items()]}

def _evidence_from_record(record: Any) -> PriceDrivenReturnEvidence | None:
    if record is None:
        return None
    return PriceDrivenReturnEvidence(passed=bool(record['passed']), adverse_raw_movement=_parse_exact(record['adverse_raw_movement']), minimum_required=_parse_exact(record['minimum_required']), provenance={str(k): str(v) for k, v in record['provenance']})

@dataclass(frozen=True)
class RuntimeB3Observation:
    bar: Any
    snapshot: CausalBoundarySnapshot | None
    geometry: B3Geometry | None
    interaction_control: InteractionControl
    params: Any
    symbol: str
    candidate_id: str
    source_segment_id: str
    target_trend_episode_id: str
    target_direction: Any
    current_trend_episode_id: str | None
    current_trend_direction: Any | None
    canonical_continuity_intact: bool
    candidate_available: bool
    terminal_candidate_replacement: bool = False
    interaction_terminal: bool = False

@dataclass(frozen=True)
class RuntimeB3PendingLineage:
    symbol: str
    candidate_id: str
    arming_snapshot_id: str
    arming_anchor_episode_id: str | None
    source_timeframe_ms: int
    source_segment_id: str
    target_trend_episode_id: str
    target_direction: str
    arming_information_cutoff: int
    arming_bar_close: Fraction
    arming_scale: Fraction
    first_eligible_return_information_cutoff: int | None = None
    adverse_extreme: Fraction | None = None
    qualifying_return_information_cutoff: int | None = None
    evidence: PriceDrivenReturnEvidence | None = None
    last_observed_information_cutoff: int | None = None

@dataclass(frozen=True)
class RuntimeB3ProducerResult:
    symbol: str
    candidate_id: str
    snapshot_ref: str | None
    reason: str
    return_evidence: PriceDrivenReturnEvidence | None
    latched_evidence: PriceDrivenReturnEvidence | None
    continuity_resolution: str | None
    pending_lineage: RuntimeB3PendingLineage | None

@dataclass(frozen=True)
class RuntimeB3CompletedTransaction:
    input_digest: str
    results: tuple[RuntimeB3ProducerResult, ...]

@dataclass
class RuntimeB3ProducerState:
    lineages: dict[str, RuntimeB3PendingLineage] = field(default_factory=dict)
    completed_transactions: dict[str, RuntimeB3CompletedTransaction] = field(default_factory=dict)

def _lineage_record(lineage: RuntimeB3PendingLineage | None) -> Any:
    if lineage is None:
        return None
    return {'symbol': lineage.symbol, 'candidate_id': lineage.candidate_id, 'arming_snapshot_id': lineage.arming_snapshot_id, 'arming_anchor_episode_id': lineage.arming_anchor_episode_id, 'source_timeframe_ms': lineage.source_timeframe_ms, 'source_segment_id': lineage.source_segment_id, 'target_trend_episode_id': lineage.target_trend_episode_id, 'target_direction': lineage.target_direction, 'arming_information_cutoff': lineage.arming_information_cutoff, 'arming_bar_close': _exact(lineage.arming_bar_close), 'arming_scale': _exact(lineage.arming_scale), 'first_eligible_return_information_cutoff': lineage.first_eligible_return_information_cutoff, 'adverse_extreme': None if lineage.adverse_extreme is None else _exact(lineage.adverse_extreme), 'qualifying_return_information_cutoff': lineage.qualifying_return_information_cutoff, 'evidence': _evidence_record(lineage.evidence), 'last_observed_information_cutoff': lineage.last_observed_information_cutoff}

def _lineage_from_record(record: Any) -> RuntimeB3PendingLineage | None:
    if record is None:
        return None
    return RuntimeB3PendingLineage(symbol=record['symbol'], candidate_id=record['candidate_id'], arming_snapshot_id=record['arming_snapshot_id'], arming_anchor_episode_id=record['arming_anchor_episode_id'], source_timeframe_ms=int(record['source_timeframe_ms']), source_segment_id=record['source_segment_id'], target_trend_episode_id=record['target_trend_episode_id'], target_direction=record['target_direction'], arming_information_cutoff=int(record['arming_information_cutoff']), arming_bar_close=_parse_exact(record['arming_bar_close']), arming_scale=_parse_exact(record['arming_scale']), first_eligible_return_information_cutoff=record['first_eligible_return_information_cutoff'], adverse_extreme=None if record['adverse_extreme'] is None else _parse_exact(record['adverse_extreme']), qualifying_return_information_cutoff=record['qualifying_return_information_cutoff'], evidence=_evidence_from_record(record['evidence']), last_observed_information_cutoff=record['last_observed_information_cutoff'])

def _result_record(result: RuntimeB3ProducerResult) -> Any:
    return {'symbol': result.symbol, 'candidate_id': result.candidate_id, 'snapshot_ref': result.snapshot_ref, 'reason': result.reason, 'return_evidence': _evidence_record(result.return_evidence), 'latched_evidence': _evidence_record(result.latched_evidence), 'continuity_resolution': result.continuity_resolution, 'pending_lineage': _lineage_record(result.pending_lineage)}

def _result_from_record(record: Any) -> RuntimeB3ProducerResult:
    return RuntimeB3ProducerResult(symbol=record['symbol'], candidate_id=record['candidate_id'], snapshot_ref=record['snapshot_ref'], reason=record['reason'], return_evidence=_evidence_from_record(record['return_evidence']), latched_evidence=_evidence_from_record(record['latched_evidence']), continuity_resolution=record['continuity_resolution'], pending_lineage=_lineage_from_record(record['pending_lineage']))

def _state_record(state: RuntimeB3ProducerState) -> Any:
    return {'producer_id': PRODUCER_ID, 'semantic_id': SEMANTIC_ID, 'lineages': [[key, _lineage_record(value)] for key, value in sorted(state.lineages.items(), key=lambda kv: kv[0])], 'completed_transactions': [[tx, {'input_digest': completed.input_digest, 'results': [_result_record(x) for x in completed.results]}] for tx, completed in sorted(state.completed_transactions.items(), key=lambda kv: kv[0])]}

def _state_from_record(record: Any) -> RuntimeB3ProducerState:
    if record.get('producer_id') != PRODUCER_ID or record.get('semantic_id') != SEMANTIC_ID:
        raise RuntimeB3Conflict('STATE_AUTHORITY_ID_MISMATCH')
    lineages = {str(key): _lineage_from_record(value) for key, value in record.get('lineages', [])}
    if any((value is None for value in lineages.values())):
        raise RuntimeB3Conflict('NULL_PENDING_LINEAGE_IN_STATE')
    completed: dict[str, RuntimeB3CompletedTransaction] = {}
    for tx, value in record.get('completed_transactions', []):
        completed[str(tx)] = RuntimeB3CompletedTransaction(input_digest=value['input_digest'], results=tuple((_result_from_record(x) for x in value['results'])))
    return RuntimeB3ProducerState(lineages={k: v for k, v in lineages.items() if v is not None}, completed_transactions=completed)

def _snapshot_record(snapshot: CausalBoundarySnapshot | None) -> Any:
    if snapshot is None:
        return None
    return {'snapshot_id': snapshot.snapshot_id, 'candidate_id': snapshot.candidate_id, 'anchor_episode_id': snapshot.anchor_episode_id, 'symbol': snapshot.symbol, 'source_timeframe_ms': snapshot.source_timeframe_ms, 'target_trend_episode_id': snapshot.target_trend_episode_id, 'target_direction': _enum_value(snapshot.target_direction), 'family': _enum_value(snapshot.family), 'boundary': _exact(snapshot.boundary), 'source_scale': _exact(snapshot.source_scale), 'source_segment_id': snapshot.source_segment_id, 'available_at': snapshot.available_at, 'provenance': [[str(k), str(v)] for k, v in sorted(snapshot.provenance.items())]}

def _geometry_record(geometry: B3Geometry | None) -> Any:
    if geometry is None:
        return None
    return {'information_cutoff': geometry.information_cutoff, 'snapshot_id': geometry.snapshot_id, 'd_close': _exact(geometry.d_close), 'd_range_nearest': _exact(geometry.d_range_nearest), 'test': bool(geometry.test), 'approach': bool(geometry.approach), 'separated': bool(geometry.separated), 'hysteresis_intermediate': bool(geometry.hysteresis_intermediate), 'wrong_side_range_penetration': bool(geometry.wrong_side_range_penetration), 'wrong_side_close': bool(geometry.wrong_side_close), 'material_wrong_side_separation': bool(geometry.material_wrong_side_separation)}

def _observation_record(obs: RuntimeB3Observation) -> Any:
    bar = obs.bar
    return {'symbol': obs.symbol, 'candidate_id': obs.candidate_id, 'source_segment_id': obs.source_segment_id, 'target_trend_episode_id': obs.target_trend_episode_id, 'target_direction': _enum_value(obs.target_direction), 'current_trend_episode_id': obs.current_trend_episode_id, 'current_trend_direction': None if obs.current_trend_direction is None else _enum_value(obs.current_trend_direction), 'canonical_continuity_intact': bool(obs.canonical_continuity_intact), 'candidate_available': bool(obs.candidate_available), 'terminal_candidate_replacement': bool(obs.terminal_candidate_replacement), 'interaction_terminal': bool(obs.interaction_terminal), 'interaction_control': _enum_value(obs.interaction_control), 'bar': {'symbol': getattr(bar, 'symbol', None), 'open_time': getattr(bar, 'open_time', None), 'close_time': getattr(bar, 'close_time', None), 'high': _exact(getattr(bar, 'high')), 'low': _exact(getattr(bar, 'low')), 'close': _exact(getattr(bar, 'close'))}, 'snapshot': _snapshot_record(obs.snapshot), 'geometry': _geometry_record(obs.geometry), 'params': {'theta_separation': _exact(getattr(obs.params, 'theta_separation')), 'theta_approach': _exact(getattr(obs.params, 'theta_approach'))}}

class RuntimeB3PriceDrivenReturnProducerV1:

    def __init__(self, state: RuntimeB3ProducerState | None=None) -> None:
        self.state = state or RuntimeB3ProducerState()

    @classmethod
    def restore_state(cls, serialized: str) -> 'RuntimeB3PriceDrivenReturnProducerV1':
        try:
            record = json.loads(serialized)
        except Exception as exc:
            raise RuntimeB3Conflict('STATE_JSON_INVALID') from exc
        return cls(_state_from_record(record))

    def export_state(self) -> str:
        return _canonical_json(_state_record(self.state))

    def state_digest(self) -> str:
        return sha256(self.export_state().encode('utf-8')).hexdigest()

    def pending_state(self, symbol: str, candidate_id: str) -> RuntimeB3PendingLineage | None:
        return self.state.lineages.get(_lineage_key(symbol, candidate_id))

    def process_batch(self, transaction_id: str, observations: Iterable[RuntimeB3Observation], *, persist: Callable[[str], None] | None=None) -> tuple[RuntimeB3ProducerResult, ...]:
        if not isinstance(transaction_id, str) or not transaction_id:
            raise RuntimeB3Conflict('TRANSACTION_ID_REQUIRED')
        ordered = tuple(sorted(tuple(observations), key=lambda x: (x.symbol, x.candidate_id)))
        if not ordered:
            raise RuntimeB3Conflict('EMPTY_RUNTIME_B3_BATCH')
        keys = [_lineage_key(x.symbol, x.candidate_id) for x in ordered]
        if len(set(keys)) != len(keys):
            raise RuntimeB3Conflict('DUPLICATE_CANDIDATE_LINEAGE_IN_BATCH')
        input_record = [_observation_record(x) for x in ordered]
        input_digest = _digest_record(input_record)
        prior = self.state.completed_transactions.get(transaction_id)
        if prior is not None:
            if prior.input_digest != input_digest:
                raise RuntimeB3Conflict('SAME_TRANSACTION_DIFFERENT_INPUT')
            return prior.results
        candidate_state = deepcopy(self.state)
        results: list[RuntimeB3ProducerResult] = []
        for obs in ordered:
            results.append(self._process_one(candidate_state, obs))
        completed = RuntimeB3CompletedTransaction(input_digest=input_digest, results=tuple(results))
        candidate_state.completed_transactions[transaction_id] = completed
        proposed_serialized = _canonical_json(_state_record(candidate_state))
        if persist is not None:
            persist(proposed_serialized)
        self.state = candidate_state
        return completed.results

    def _reset_reasons(self, obs: RuntimeB3Observation) -> tuple[str, ...]:
        reasons: list[str] = []
        if not obs.canonical_continuity_intact:
            reasons.append('CANONICAL_CONTINUITY_BREAK')
        target_direction = _enum_value(obs.target_direction)
        current_direction = None if obs.current_trend_direction is None else _enum_value(obs.current_trend_direction)
        if obs.current_trend_episode_id is None or obs.current_trend_episode_id != obs.target_trend_episode_id or current_direction != target_direction:
            reasons.append('TARGET_TREND_EPISODE_END_OR_CHANGE')
        if not obs.candidate_available:
            reasons.append('CANDIDATE_UNAVAILABLE')
        if obs.terminal_candidate_replacement:
            reasons.append('TERMINAL_CANDIDATE_REPLACEMENT')
        if obs.interaction_terminal or obs.interaction_control in (InteractionControl.INTERACTION_ACTIVE, InteractionControl.RESOLVED):
            reasons.append('INTERACTION_NO_LONGER_PENDING')
        return tuple(reasons)

    def _validate_common(self, obs: RuntimeB3Observation) -> None:
        if not obs.symbol or not obs.candidate_id or (not obs.source_segment_id) or (not obs.target_trend_episode_id):
            raise RuntimeB3Conflict('OBSERVATION_LINEAGE_IDENTITY_REQUIRED')
        if getattr(obs.bar, 'symbol', None) != obs.symbol:
            raise RuntimeB3Conflict('BAR_SYMBOL_MISMATCH')
        if not isinstance(getattr(obs.bar, 'open_time', None), int) or not isinstance(getattr(obs.bar, 'close_time', None), int):
            raise RuntimeB3Conflict('BAR_TIME_REQUIRED')
        for name in ('high', 'low', 'close'):
            if not isinstance(getattr(obs.bar, name, None), Fraction):
                raise RuntimeB3Conflict(f'BAR_{name.upper()}_MUST_BE_EXACT_FRACTION')
        if _enum_value(obs.target_direction) not in ('LONG', 'SHORT'):
            raise RuntimeB3Conflict('TARGET_DIRECTION_LONG_OR_SHORT_REQUIRED')
        if not isinstance(obs.canonical_continuity_intact, bool):
            raise RuntimeB3Conflict('CONTINUITY_FLAG_REQUIRED')
        if not isinstance(obs.candidate_available, bool) or not isinstance(obs.terminal_candidate_replacement, bool):
            raise RuntimeB3Conflict('CANDIDATE_RESET_FLAGS_REQUIRED')
        if not isinstance(getattr(obs.params, 'theta_separation', None), Fraction):
            raise RuntimeB3Conflict('THETA_SEPARATION_EXACT_REQUIRED')
        if not isinstance(getattr(obs.params, 'theta_approach', None), Fraction):
            raise RuntimeB3Conflict('THETA_APPROACH_EXACT_REQUIRED')

    def _validate_active_surface(self, obs: RuntimeB3Observation) -> None:
        if obs.snapshot is None or obs.geometry is None:
            raise RuntimeB3Conflict('ACTIVE_CANDIDATE_REQUIRES_SNAPSHOT_AND_GEOMETRY')
        snapshot = obs.snapshot
        geometry = obs.geometry
        if snapshot.candidate_id != obs.candidate_id or snapshot.symbol != obs.symbol:
            raise RuntimeB3Conflict('SNAPSHOT_CANDIDATE_OR_SYMBOL_MISMATCH')
        if snapshot.source_segment_id != obs.source_segment_id:
            raise RuntimeB3Conflict('SNAPSHOT_SEGMENT_MISMATCH')
        if snapshot.target_trend_episode_id != obs.target_trend_episode_id:
            raise RuntimeB3Conflict('SNAPSHOT_TREND_EPISODE_MISMATCH')
        if _enum_value(snapshot.target_direction) != _enum_value(obs.target_direction):
            raise RuntimeB3Conflict('SNAPSHOT_DIRECTION_MISMATCH')
        if geometry.snapshot_id != snapshot.snapshot_id:
            raise RuntimeB3Conflict('GEOMETRY_SNAPSHOT_MISMATCH')
        if geometry.information_cutoff != obs.bar.close_time:
            raise RuntimeB3Conflict('GEOMETRY_CUTOFF_MISMATCH')
        if snapshot.available_at > obs.bar.open_time:
            raise RuntimeB3Conflict('SNAPSHOT_NOT_CAUSALLY_PREBAR_AVAILABLE')
        if not isinstance(snapshot.source_scale, Fraction) or snapshot.source_scale <= 0:
            raise RuntimeB3Conflict('ARMING_SOURCE_SCALE_MUST_BE_POSITIVE_EXACT')

    def _validate_pending_lineage(self, lineage: RuntimeB3PendingLineage, obs: RuntimeB3Observation) -> None:
        if lineage.symbol != obs.symbol or lineage.candidate_id != obs.candidate_id or lineage.source_segment_id != obs.source_segment_id or (lineage.target_trend_episode_id != obs.target_trend_episode_id) or (lineage.target_direction != _enum_value(obs.target_direction)):
            raise RuntimeB3Conflict('PENDING_LINEAGE_IDENTITY_MISMATCH')

    def _result(self, obs: RuntimeB3Observation, *, reason: str, return_evidence: PriceDrivenReturnEvidence | None, latched_evidence: PriceDrivenReturnEvidence | None, continuity_resolution: str | None, pending: RuntimeB3PendingLineage | None) -> RuntimeB3ProducerResult:
        return RuntimeB3ProducerResult(symbol=obs.symbol, candidate_id=obs.candidate_id, snapshot_ref=None if obs.snapshot is None else obs.snapshot.snapshot_id, reason=reason, return_evidence=return_evidence, latched_evidence=latched_evidence, continuity_resolution=continuity_resolution, pending_lineage=pending)

    def _process_one(self, state: RuntimeB3ProducerState, obs: RuntimeB3Observation) -> RuntimeB3ProducerResult:
        self._validate_common(obs)
        key = _lineage_key(obs.symbol, obs.candidate_id)
        reset_reasons = self._reset_reasons(obs)
        if reset_reasons:
            state.lineages.pop(key, None)
            return self._result(obs, reason='RESET:' + '|'.join(reset_reasons), return_evidence=None, latched_evidence=None, continuity_resolution='UNKNOWN_CONTINUITY' if 'CANONICAL_CONTINUITY_BREAK' in reset_reasons else None, pending=None)
        self._validate_active_surface(obs)
        assert obs.snapshot is not None
        assert obs.geometry is not None
        cutoff = obs.geometry.information_cutoff
        existing = state.lineages.get(key)
        if obs.interaction_control is InteractionControl.UNARMED:
            if existing is not None:
                raise RuntimeB3Conflict('UNARMED_WITH_EXISTING_PENDING_RUNTIME_B3_STATE')
            if not obs.geometry.separated:
                return self._result(obs, reason='UNARMED_NO_SEPARATION', return_evidence=None, latched_evidence=None, continuity_resolution=None, pending=None)
            lineage = RuntimeB3PendingLineage(symbol=obs.symbol, candidate_id=obs.candidate_id, arming_snapshot_id=obs.snapshot.snapshot_id, arming_anchor_episode_id=obs.snapshot.anchor_episode_id, source_timeframe_ms=obs.snapshot.source_timeframe_ms, source_segment_id=obs.snapshot.source_segment_id, target_trend_episode_id=obs.snapshot.target_trend_episode_id, target_direction=_enum_value(obs.snapshot.target_direction), arming_information_cutoff=cutoff, arming_bar_close=obs.bar.close, arming_scale=obs.snapshot.source_scale, last_observed_information_cutoff=cutoff)
            state.lineages[key] = lineage
            return self._result(obs, reason='ARMED_FROZEN_CURRENT_CUTOFF_NO_RETURN', return_evidence=None, latched_evidence=None, continuity_resolution=None, pending=lineage)
        if obs.interaction_control is not InteractionControl.ARMED:
            raise RuntimeB3Conflict('UNSUPPORTED_PENDING_INTERACTION_CONTROL')
        if existing is None:
            raise RuntimeB3Block('ARMED_WITHOUT_RUNTIME_B3_PENDING_STATE')
        self._validate_pending_lineage(existing, obs)
        if cutoff < existing.arming_information_cutoff:
            raise RuntimeB3Conflict('CUTOFF_BEFORE_ARMING')
        if existing.last_observed_information_cutoff is not None and cutoff < existing.last_observed_information_cutoff:
            raise RuntimeB3Conflict('NON_MONOTONIC_RUNTIME_B3_CUTOFF')
        if existing.last_observed_information_cutoff == cutoff:
            if cutoff == existing.arming_information_cutoff:
                return self._result(obs, reason='INELIGIBLE_SAME_OR_EARLIER_BAR', return_evidence=None, latched_evidence=existing.evidence, continuity_resolution=None, pending=existing)
            raise RuntimeB3Conflict('REPEATED_CUTOFF_REQUIRES_SAME_TRANSACTION_REPLAY')
        if existing.evidence is not None:
            if existing.qualifying_return_information_cutoff is None:
                raise RuntimeB3Conflict('LATCHED_EVIDENCE_WITHOUT_QUALIFICATION_CUTOFF')
            updated = replace(existing, last_observed_information_cutoff=cutoff)
            state.lineages[key] = updated
            return self._result(obs, reason='LATCHED_RETURN_CONSUMABLE', return_evidence=existing.evidence if cutoff > existing.qualifying_return_information_cutoff else None, latched_evidence=existing.evidence, continuity_resolution=None, pending=updated)
        first_eligible = cutoff if existing.first_eligible_return_information_cutoff is None else existing.first_eligible_return_information_cutoff
        current_extreme = obs.bar.low if existing.target_direction == 'LONG' else obs.bar.high
        if existing.adverse_extreme is None:
            extreme = current_extreme
        elif existing.target_direction == 'LONG':
            extreme = min(existing.adverse_extreme, current_extreme)
        else:
            extreme = max(existing.adverse_extreme, current_extreme)
        adverse = existing.arming_bar_close - extreme if existing.target_direction == 'LONG' else extreme - existing.arming_bar_close
        updated = replace(existing, first_eligible_return_information_cutoff=first_eligible, adverse_extreme=extreme, last_observed_information_cutoff=cutoff)
        if adverse < 0:
            state.lineages[key] = updated
            return self._result(obs, reason='NEGATIVE_SIGNED_NOT_ADVERSE_YET', return_evidence=None, latched_evidence=None, continuity_resolution=None, pending=updated)
        minimum = (obs.params.theta_separation - obs.params.theta_approach) * existing.arming_scale
        provenance = {'semantic_id': SEMANTIC_ID, 'candidate_id': existing.candidate_id, 'arming_snapshot_id': existing.arming_snapshot_id, 'symbol': existing.symbol, 'source_timeframe_ms': str(existing.source_timeframe_ms), 'observer_timeframe_ms': str(OBSERVER_TIMEFRAME_MS), 'source_segment_id': existing.source_segment_id, 'target_trend_episode_id': existing.target_trend_episode_id, 'target_direction': existing.target_direction, 'arming_information_cutoff': str(existing.arming_information_cutoff), 'arming_bar_close_exact': _exact(existing.arming_bar_close), 'arming_scale_exact': _exact(existing.arming_scale), 'first_eligible_return_information_cutoff': str(first_eligible), 'qualifying_return_information_cutoff': str(cutoff), 'adverse_extreme_field': 'LOW' if existing.target_direction == 'LONG' else 'HIGH', 'adverse_extreme_exact': _exact(extreme), 'adverse_raw_movement_exact': _exact(adverse), 'minimum_required_exact': _exact(minimum), 'stage3b_research_binding_deterministic_sha256': STAGE3B_BINDING_DETERMINISTIC_SHA256}
        evidence = qualify_price_driven_return(adverse_raw_movement=adverse, source_scale=existing.arming_scale, params=obs.params, provenance=provenance)
        if evidence.minimum_required != minimum:
            raise RuntimeB3Conflict('WP3_MINIMUM_REQUIRED_DIVERGENCE')
        if dict(evidence.provenance) != provenance:
            raise RuntimeB3Conflict('WP3_PROVENANCE_DIVERGENCE')
        if evidence.passed:
            latched = replace(updated, qualifying_return_information_cutoff=cutoff, evidence=evidence)
            state.lineages[key] = latched
            return self._result(obs, reason='RETURN_QUALIFIED_LATCHED_NOT_CONSUMABLE_SAME_CUTOFF', return_evidence=None, latched_evidence=evidence, continuity_resolution=None, pending=latched)
        state.lineages[key] = updated
        return self._result(obs, reason='RETURN_NOT_YET_QUALIFIED', return_evidence=None, latched_evidence=None, continuity_resolution=None, pending=updated)
