"""Source-preserving D1 single-module dependency closure, generated from SHA-pinned original 91 files.

NOT a full TAC strategy; consume only within a Binance AI Pro native D1-D6
assembly. No synthetic pivot logic. All original scientific function bodies
and numeric constants are unchanged; only module-relative imports removed.
"""
from __future__ import annotations
# --- ORIGINAL result_types.py ---
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from typing import Any

class Direction(str, Enum):
    UP = 'UP'
    DOWN = 'DOWN'
    UNKNOWN = 'UNKNOWN'

class IntegritySeverity(str, Enum):
    INFO = 'INFO'
    BLOCK = 'BLOCK'

@dataclass(frozen=True)
class IntegrityIssue:
    code: str
    severity: IntegritySeverity
    detail: str
    open_time: int | None = None
Number = Fraction

def number_to_exact_dict(value: Fraction) -> dict[str, int]:
    return {'numerator': value.numerator, 'denominator': value.denominator}

def freeze_payload(value: Any) -> Any:
    """Convert supported objects into deterministic JSON-safe primitives."""
    from dataclasses import asdict, is_dataclass
    if isinstance(value, Fraction):
        return {'__fraction__': [value.numerator, value.denominator]}
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {k: freeze_payload(v) for k, v in asdict(value).items()}
    if isinstance(value, dict):
        return {str(k): freeze_payload(v) for k, v in sorted(value.items(), key=lambda kv: str(kv[0]))}
    if isinstance(value, (list, tuple)):
        return [freeze_payload(v) for v in value]
    if value is None or isinstance(value, (str, int, bool)):
        return value
    raise TypeError(f'Unsupported deterministic payload type: {type(value)!r}')

# --- ORIGINAL ids.py ---
import hashlib
import json
from typing import Any

def canonical_json(value: Any) -> str:
    return json.dumps(freeze_payload(value), sort_keys=True, separators=(',', ':'), ensure_ascii=False)

def deterministic_id(namespace: str, *parts: Any, length: int=32) -> str:
    if not namespace or not isinstance(namespace, str):
        raise ValueError('namespace must be a non-empty string')
    payload = canonical_json({'namespace': namespace, 'parts': list(parts)})
    digest = hashlib.sha256(payload.encode('utf-8')).hexdigest()
    return f'{namespace}:{digest[:length]}'

# --- ORIGINAL runtime_guards/information_state.py ---
from dataclasses import dataclass
from enum import Enum
from typing import Generic, TypeVar
T = TypeVar('T')

class InfoKind(str, Enum):
    KNOWN = 'KNOWN'
    NONE = 'NONE'
    UNKNOWN = 'UNKNOWN'
    NA = 'N/A'
    ERROR = 'ERROR'

@dataclass(frozen=True)
class InfoValue(Generic[T]):
    kind: InfoKind
    value: T | None = None
    error_ref: str | None = None

    def __post_init__(self) -> None:
        if self.kind is InfoKind.KNOWN:
            if self.value is None or self.error_ref is not None:
                raise ValueError('KNOWN requires a value and no error_ref')
        elif self.kind is InfoKind.ERROR:
            if self.error_ref is None or self.value is not None:
                raise ValueError('ERROR requires error_ref and no value')
        elif self.value is not None or self.error_ref is not None:
            raise ValueError(f'{self.kind.value} cannot carry value/error_ref')

    @classmethod
    def known(cls, value: T) -> 'InfoValue[T]':
        return cls(InfoKind.KNOWN, value=value)

    @classmethod
    def none(cls) -> 'InfoValue[T]':
        return cls(InfoKind.NONE)

    @classmethod
    def unknown(cls) -> 'InfoValue[T]':
        return cls(InfoKind.UNKNOWN)

    @classmethod
    def na(cls) -> 'InfoValue[T]':
        return cls(InfoKind.NA)

    @classmethod
    def error(cls, error_ref: str) -> 'InfoValue[T]':
        return cls(InfoKind.ERROR, error_ref=error_ref)

    def require_known(self) -> T:
        if self.kind is not InfoKind.KNOWN:
            raise ValueError(f'Value is {self.kind.value}, not KNOWN')
        return self.value

# --- ORIGINAL runtime_guards/continuity_guard.py ---
class DataIntegrityBlock(RuntimeError):
    """System-level integrity block; never a market Strategy failure."""

class ContinuityReset(RuntimeError):
    """Marker exception for callers that choose exception-based segment handling."""

# --- ORIGINAL d1_data_math/ohlc_protocol.py ---
from fractions import Fraction
from typing import Protocol

class OHLCBar(Protocol):
    open_time: int
    close_time: int
    open: Fraction
    high: Fraction
    low: Fraction
    close: Fraction

# --- ORIGINAL d1_data_math/canonical.py ---
from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from typing import Iterable
TF_15M_MS = 15 * 60 * 1000

def parse_exact_number(value: str | int | Decimal | Fraction) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, bool):
        raise TypeError('bool is not a valid market number')
    if isinstance(value, int):
        return Fraction(value, 1)
    if isinstance(value, Decimal):
        return Fraction(value)
    if isinstance(value, str):
        return Fraction(Decimal(value))
    if isinstance(value, float):
        raise TypeError('float market inputs are forbidden; provide exact decimal string/int/Decimal/Fraction')
    raise TypeError(f'Unsupported market number type: {type(value)!r}')

@dataclass(frozen=True)
class CanonicalBar:
    symbol: str
    open_time: int
    close_time: int
    open: Fraction
    high: Fraction
    low: Fraction
    close: Fraction
    base_volume: Fraction | None = None
    quote_volume: Fraction | None = None
    is_closed: bool = True

    @classmethod
    def from_values(cls, *, symbol: str, open_time: int, close_time: int, open: str | int | Decimal | Fraction, high: str | int | Decimal | Fraction, low: str | int | Decimal | Fraction, close: str | int | Decimal | Fraction, base_volume: str | int | Decimal | Fraction | None=None, quote_volume: str | int | Decimal | Fraction | None=None, is_closed: bool=True) -> 'CanonicalBar':
        return cls(symbol=symbol, open_time=open_time, close_time=close_time, open=parse_exact_number(open), high=parse_exact_number(high), low=parse_exact_number(low), close=parse_exact_number(close), base_volume=None if base_volume is None else parse_exact_number(base_volume), quote_volume=None if quote_volume is None else parse_exact_number(quote_volume), is_closed=is_closed)

@dataclass(frozen=True)
class CanonicalRecord:
    bar: CanonicalBar
    canonical_segment_id: str

@dataclass(frozen=True)
class CanonicalizationResult:
    records: tuple[CanonicalRecord, ...]
    issues: tuple[IntegrityIssue, ...]
    identical_duplicates_deduplicated: int

    @property
    def information_cutoff(self) -> int | None:
        return self.records[-1].bar.close_time if self.records else None

def _validate_bar(bar: CanonicalBar) -> None:
    if not bar.symbol:
        raise DataIntegrityBlock('EMPTY_SYMBOL')
    if not bar.is_closed:
        raise DataIntegrityBlock(f'OPEN_BAR_FORBIDDEN open_time={bar.open_time}')
    if bar.open_time % TF_15M_MS != 0:
        raise DataIntegrityBlock(f'OPEN_TIME_NOT_15M_ALIGNED open_time={bar.open_time}')
    if bar.close_time <= bar.open_time:
        raise DataIntegrityBlock(f'IMPOSSIBLE_CLOSE_TIME open_time={bar.open_time} close_time={bar.close_time}')
    if bar.high < max(bar.open, bar.close, bar.low):
        raise DataIntegrityBlock(f'INVALID_HIGH open_time={bar.open_time}')
    if bar.low > min(bar.open, bar.close, bar.high):
        raise DataIntegrityBlock(f'INVALID_LOW open_time={bar.open_time}')
    if bar.base_volume is not None and bar.base_volume < 0:
        raise DataIntegrityBlock(f'NEGATIVE_BASE_VOLUME open_time={bar.open_time}')
    if bar.quote_volume is not None and bar.quote_volume < 0:
        raise DataIntegrityBlock(f'NEGATIVE_QUOTE_VOLUME open_time={bar.open_time}')

def canonicalize_15m(bars: Iterable[CanonicalBar]) -> CanonicalizationResult:
    ordered = sorted(bars, key=lambda b: (b.open_time, b.close_time))
    if not ordered:
        return CanonicalizationResult((), (), 0)
    by_open: dict[int, CanonicalBar] = {}
    dedup = 0
    for bar in ordered:
        _validate_bar(bar)
        prior = by_open.get(bar.open_time)
        if prior is None:
            by_open[bar.open_time] = bar
        elif prior == bar:
            dedup += 1
        else:
            raise DataIntegrityBlock(f'CONFLICTING_DUPLICATE open_time={bar.open_time}')
    unique = [by_open[k] for k in sorted(by_open)]
    symbols = {b.symbol for b in unique}
    if len(symbols) != 1:
        raise DataIntegrityBlock('MIXED_SYMBOL_INPUT')
    symbol = unique[0].symbol
    records: list[CanonicalRecord] = []
    issues: list[IntegrityIssue] = []
    segment_id: str | None = None
    prev_open: int | None = None
    for bar in unique:
        if prev_open is None or bar.open_time - prev_open != TF_15M_MS:
            if prev_open is not None:
                delta = bar.open_time - prev_open
                if delta <= 0:
                    raise DataIntegrityBlock('NON_MONOTONIC_OPEN_TIME')
                issues.append(IntegrityIssue(code='DATA_GAP_NEW_CANONICAL_SEGMENT', severity=IntegritySeverity.BLOCK, detail=f'gap_ms={delta - TF_15M_MS}; no forward fill; recursive state must reset', open_time=bar.open_time))
            segment_id = deterministic_id('canonical_segment', symbol, bar.open_time)
        records.append(CanonicalRecord(bar=bar, canonical_segment_id=segment_id))
        prev_open = bar.open_time
    return CanonicalizationResult(tuple(records), tuple(issues), dedup)

# --- ORIGINAL d1_data_math/ema.py ---
from fractions import Fraction

class EMARecurrence:

    def __init__(self, period: int) -> None:
        if period <= 0:
            raise ValueError('EMA period must be positive')
        self.period = period
        self._segment_id: str | None = None
        self._seed: list[Fraction] = []
        self._ema: Fraction | None = None
        self._alpha = Fraction(2, period + 1)

    def reset(self) -> None:
        self._seed.clear()
        self._ema = None

    def update(self, close: Fraction, *, segment_id: str) -> InfoValue[Fraction]:
        if self._segment_id != segment_id:
            self._segment_id = segment_id
            self.reset()
        if self._ema is None:
            self._seed.append(close)
            if len(self._seed) < self.period:
                return InfoValue.na()
            if len(self._seed) == self.period:
                self._ema = sum(self._seed, Fraction(0, 1)) / self.period
                return InfoValue.known(self._ema)
            raise AssertionError('EMA seed length invariant broken')
        self._ema = self._alpha * close + (1 - self._alpha) * self._ema
        return InfoValue.known(self._ema)

# --- ORIGINAL d1_data_math/atr.py ---
from fractions import Fraction

class ATR14Recurrence:
    period = 14

    def __init__(self) -> None:
        self._segment_id: str | None = None
        self._prev_close: Fraction | None = None
        self._trs: list[Fraction] = []
        self._atr: Fraction | None = None

    def reset(self) -> None:
        self._prev_close = None
        self._trs.clear()
        self._atr = None

    def update(self, bar: OHLCBar, *, segment_id: str) -> InfoValue[Fraction]:
        if self._segment_id != segment_id:
            self._segment_id = segment_id
            self.reset()
        if self._prev_close is None:
            tr = bar.high - bar.low
        else:
            tr = max(bar.high - bar.low, abs(bar.high - self._prev_close), abs(bar.low - self._prev_close))
        self._prev_close = bar.close
        if self._atr is None:
            self._trs.append(tr)
            if len(self._trs) < self.period:
                return InfoValue.na()
            if len(self._trs) == self.period:
                self._atr = sum(self._trs, Fraction(0, 1)) / self.period
                return InfoValue.known(self._atr)
            raise AssertionError('ATR seed length invariant broken')
        self._atr = (self._atr * (self.period - 1) + tr) / self.period
        return InfoValue.known(self._atr)

# --- ORIGINAL d1_data_math/supertrend.py ---
from dataclasses import dataclass
from fractions import Fraction
ST_MULTIPLIER = Fraction(3, 1)

@dataclass(frozen=True)
class SupertrendPoint:
    final_upper: InfoValue[Fraction]
    final_lower: InfoValue[Fraction]
    direction: Direction
    active_line: InfoValue[Fraction]

class SupertrendRecurrence:
    """RC1 + adopted post-RC1 exact final-band recurrence binding."""

    def __init__(self) -> None:
        self._segment_id: str | None = None
        self._prev_close: Fraction | None = None
        self._final_upper: Fraction | None = None
        self._final_lower: Fraction | None = None
        self._direction = Direction.UNKNOWN

    def reset(self) -> None:
        self._prev_close = None
        self._final_upper = None
        self._final_lower = None
        self._direction = Direction.UNKNOWN

    def update(self, bar: OHLCBar, atr14: InfoValue[Fraction], *, segment_id: str) -> SupertrendPoint:
        if self._segment_id != segment_id:
            self._segment_id = segment_id
            self.reset()
        if atr14.kind is not InfoKind.KNOWN:
            self._prev_close = bar.close
            return SupertrendPoint(final_upper=InfoValue.na(), final_lower=InfoValue.na(), direction=Direction.UNKNOWN, active_line=InfoValue.na())
        atr = atr14.require_known()
        hl2 = (bar.high + bar.low) / 2
        basic_upper = hl2 + ST_MULTIPLIER * atr
        basic_lower = hl2 - ST_MULTIPLIER * atr
        if self._final_upper is None or self._final_lower is None or self._prev_close is None:
            self._final_upper = basic_upper
            self._final_lower = basic_lower
            self._direction = Direction.UNKNOWN
            self._prev_close = bar.close
            return SupertrendPoint(final_upper=InfoValue.known(self._final_upper), final_lower=InfoValue.known(self._final_lower), direction=self._direction, active_line=InfoValue.na())
        prior_upper = self._final_upper
        prior_lower = self._final_lower
        prior_close = self._prev_close
        final_lower = basic_lower if basic_lower > prior_lower or prior_close < prior_lower else prior_lower
        final_upper = basic_upper if basic_upper < prior_upper or prior_close > prior_upper else prior_upper
        if bar.close > prior_upper:
            direction = Direction.UP
        elif bar.close < prior_lower:
            direction = Direction.DOWN
        else:
            direction = self._direction
        self._final_upper = final_upper
        self._final_lower = final_lower
        self._direction = direction
        self._prev_close = bar.close
        if direction is Direction.UP:
            active = InfoValue.known(final_lower)
        elif direction is Direction.DOWN:
            active = InfoValue.known(final_upper)
        else:
            active = InfoValue.na()
        return SupertrendPoint(final_upper=InfoValue.known(final_upper), final_lower=InfoValue.known(final_lower), direction=direction, active_line=active)

# --- ORIGINAL d1_data_math/htf_aggregation.py ---
from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable

@dataclass(frozen=True)
class HTFBar:
    symbol: str
    timeframe_ms: int
    open_time: int
    close_time: int
    open: Fraction
    high: Fraction
    low: Fraction
    close: Fraction
    base_volume: Fraction | None
    quote_volume: Fraction | None
    source_segment_id: str

def _sum_optional(values: list[Fraction | None]) -> Fraction | None:
    if any((v is None for v in values)):
        return None
    return sum((v for v in values if v is not None), Fraction(0, 1))

def aggregate_completed_htf(records: Iterable[CanonicalRecord], *, timeframe_ms: int, information_cutoff: int) -> tuple[HTFBar, ...]:
    if timeframe_ms not in (60 * 60 * 1000, 4 * 60 * 60 * 1000):
        raise ValueError('Only causal 1H and 4H aggregation is authorized in WP1')
    required = timeframe_ms // TF_15M_MS
    buckets: dict[tuple[str, int], list[CanonicalRecord]] = defaultdict(list)
    for rec in records:
        bucket_start = rec.bar.open_time // timeframe_ms * timeframe_ms
        buckets[rec.canonical_segment_id, bucket_start].append(rec)
    out: list[HTFBar] = []
    for (segment_id, bucket_start), members in sorted(buckets.items(), key=lambda kv: kv[0][1]):
        members.sort(key=lambda r: r.bar.open_time)
        expected_opens = [bucket_start + i * TF_15M_MS for i in range(required)]
        actual_opens = [r.bar.open_time for r in members]
        if actual_opens != expected_opens:
            continue
        if len({r.canonical_segment_id for r in members}) != 1:
            continue
        close_time = members[-1].bar.close_time
        if close_time > information_cutoff:
            continue
        first, last = (members[0].bar, members[-1].bar)
        out.append(HTFBar(symbol=first.symbol, timeframe_ms=timeframe_ms, open_time=bucket_start, close_time=close_time, open=first.open, high=max((r.bar.high for r in members)), low=min((r.bar.low for r in members)), close=last.close, base_volume=_sum_optional([r.bar.base_volume for r in members]), quote_volume=_sum_optional([r.bar.quote_volume for r in members]), source_segment_id=segment_id))
    return tuple(out)

# --- ORIGINAL parameter_snapshot.py ---
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Mapping

class ParameterState(str, Enum):
    FROZEN = 'FROZEN'
    OPEN = 'OPEN'
    LOCKED = 'LOCKED'

@dataclass(frozen=True)
class ParameterSlot:
    name: str
    state: ParameterState
    exact_value: str | None = None

    def __post_init__(self) -> None:
        if self.state is ParameterState.FROZEN and self.exact_value is None:
            raise ValueError(f'Frozen parameter {self.name} requires exact_value')
        if self.state is not ParameterState.FROZEN and self.exact_value is not None:
            raise ValueError(f'Unfrozen parameter {self.name} must not contain a value')

@dataclass(frozen=True)
class ParameterSnapshot:
    snapshot_id: str
    slots: Mapping[str, ParameterSlot]
    complete_strategy_parameter_snapshot: bool
    runtime_usable: bool
    source_status: str

    def __post_init__(self) -> None:
        object.__setattr__(self, 'slots', MappingProxyType(dict(self.slots)))

    def slot(self, name: str) -> ParameterSlot:
        try:
            return self.slots[name]
        except KeyError as exc:
            raise KeyError(f'Parameter slot not declared: {name}') from exc

    @property
    def frozen_count(self) -> int:
        return sum((s.state is ParameterState.FROZEN for s in self.slots.values()))
PARTIAL_PARAMETER_SNAPSHOT_ID = 'R1_PARTIAL_RESEARCH_SNAPSHOT_PROGRESS_RATE_B3_ACCEPT_OVER_995E24FBAA216C62'
PARTIAL_PARAMETER_SNAPSHOT_DETERMINISTIC_SHA256 = 'a869a3a7758c0a4ff34ddfb5ae1c4e012e0600bbea6492cf12efa19a148ef5bb'
_FROZEN = {'theta_accept': '2.1313767840459202205981702405574439224871803906649207193085500', 'theta_approach': '1.197268280893772873697806561124554291191704011769349520546870', 'theta_overextension': '2.7703041968078565478295719882475244376661292176373236367284700', 'theta_progress': '1.27112707163488491529631027277968495738450', 'theta_rate': '0.17560145225927980894381212168524856466229325734699705827303000', 'theta_separation': '2.24912097135367169114306428916723600671864369102654007565280', 'theta_test': '0.5913466407600057877252533034649404155944065891655909831651470'}

def current_partial_parameter_snapshot() -> ParameterSnapshot:
    """Bind the durable partial snapshot, overlaid by newer current governance.

    The source V5 snapshot recorded theta_stop as OPEN at that historical point.
    Current v12 governance supersedes only its current-state display and locks
    theta_stop. No numerical value is created for the locked slot.
    """
    slots: dict[str, ParameterSlot] = {name: ParameterSlot(name=name, state=ParameterState.FROZEN, exact_value=value) for name, value in _FROZEN.items()}
    slots.update({'theta_minor': ParameterSlot('theta_minor', ParameterState.OPEN), 'theta_intermediate': ParameterSlot('theta_intermediate', ParameterState.OPEN), 'theta_major': ParameterSlot('theta_major', ParameterState.OPEN), 'theta_stop': ParameterSlot('theta_stop', ParameterState.LOCKED)})
    return ParameterSnapshot(snapshot_id=PARTIAL_PARAMETER_SNAPSHOT_ID, slots=slots, complete_strategy_parameter_snapshot=False, runtime_usable=False, source_status='PARTIAL_RESEARCH_FREEZE_NOT_STRATEGY_USABLE_WITH_CURRENT_V12_THETA_STOP_LOCK_OVERLAY')

# --- ORIGINAL d2_market_state/parameters.py ---
from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction

class StructuralParameterResolutionBlock(RuntimeError):
    pass

def _exact_fraction(value: str) -> Fraction:
    return Fraction(Decimal(value))

@dataclass(frozen=True)
class StructuralScaleParameters:
    theta_minor: Fraction
    theta_intermediate: Fraction
    theta_major: Fraction

    def __post_init__(self) -> None:
        if not 0 < self.theta_minor < self.theta_intermediate < self.theta_major:
            raise ValueError('RC1 requires 0 < theta_minor < theta_intermediate < theta_major')

@dataclass(frozen=True)
class FrozenD2Parameters:
    theta_progress: Fraction
    theta_rate: Fraction
    theta_overextension: Fraction

    def __post_init__(self) -> None:
        if self.theta_progress < 0:
            raise ValueError('theta_progress must be >= 0')
        if self.theta_rate < 0:
            raise ValueError('theta_rate must be >= 0')
        if self.theta_overextension <= 1:
            raise ValueError('theta_overextension must be > 1')

def require_structural_scale_parameters(snapshot: ParameterSnapshot) -> StructuralScaleParameters:
    names = ('theta_minor', 'theta_intermediate', 'theta_major')
    slots = [snapshot.slot(name) for name in names]
    unresolved = [slot.name for slot in slots if slot.state is not ParameterState.FROZEN]
    if unresolved:
        raise StructuralParameterResolutionBlock('WP2_STRUCTURAL_SCALE_PARAMETERS_UNRESOLVED: ' + ','.join(unresolved))
    return StructuralScaleParameters(*(_exact_fraction(slot.exact_value or '') for slot in slots))

def frozen_d2_parameters(snapshot: ParameterSnapshot) -> FrozenD2Parameters:
    values: list[Fraction] = []
    for name in ('theta_progress', 'theta_rate', 'theta_overextension'):
        slot = snapshot.slot(name)
        if slot.state is not ParameterState.FROZEN or slot.exact_value is None:
            raise StructuralParameterResolutionBlock(f'D2_FROZEN_PARAMETER_MISSING: {name}')
        values.append(_exact_fraction(slot.exact_value))
    return FrozenD2Parameters(*values)

# --- ORIGINAL d2_market_state/types.py ---
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction
from typing import Mapping

class StructuralLayer(str, Enum):
    MINOR = 'MINOR'
    INTERMEDIATE = 'INTERMEDIATE'
    MAJOR = 'MAJOR'

class PivotType(str, Enum):
    HIGH = 'HIGH'
    LOW = 'LOW'

class SearchMode(str, Enum):
    UNKNOWN = 'UNKNOWN'
    NEUTRAL = 'NEUTRAL'
    SEEK_HIGH = 'SEEK_HIGH'
    SEEK_LOW = 'SEEK_LOW'

class ProgressRelation(str, Enum):
    MATERIAL_ADVANCE_UP = 'MATERIAL_ADVANCE_UP'
    MATERIAL_ADVANCE_DOWN = 'MATERIAL_ADVANCE_DOWN'
    STRUCTURALLY_EQUIVALENT = 'STRUCTURALLY_EQUIVALENT'

class TrendDirection(str, Enum):
    LONG = 'LONG'
    SHORT = 'SHORT'
    NONE = 'NONE'
    UNKNOWN = 'UNKNOWN'

class TrendIntegrity(str, Enum):
    HEALTHY = 'HEALTHY'
    PRESSURED = 'PRESSURED'
    DETERIORATING = 'DETERIORATING'
    FAILED = 'FAILED'

class TrendPhase(str, Enum):
    UNKNOWN = 'UNKNOWN'
    NO_TREND = 'NO_TREND'
    EXPANSION = 'EXPANSION'
    ACCELERATION = 'ACCELERATION'
    DECELERATION = 'DECELERATION'
    PLATFORM_CANDIDATE = 'PLATFORM_CANDIDATE'
    PLATFORM_CONFIRMED = 'PLATFORM_CONFIRMED'
    REVERSAL_CANDIDATE = 'REVERSAL_CANDIDATE'
    STRUCTURAL_FAILURE = 'STRUCTURAL_FAILURE'

class TrendPosition(str, Enum):
    BALANCED = 'BALANCED'
    PULLBACK = 'PULLBACK'
    EXTENDED = 'EXTENDED'
    OVEREXTENDED = 'OVEREXTENDED'
    UNKNOWN = 'UNKNOWN'
    NA = 'N/A'

class PlatformStatus(str, Enum):
    NONE = 'NONE'
    PLATFORM_CANDIDATE = 'PLATFORM_CANDIDATE'
    PLATFORM_CONFIRMED = 'PLATFORM_CONFIRMED'

@dataclass(frozen=True)
class StructuralPivot:
    pivot_id: str
    symbol: str
    timeframe_ms: int
    layer: StructuralLayer
    pivot_type: PivotType
    extreme_price: Fraction
    extreme_first_time: int
    extreme_last_time: int
    confirmed_at: int
    scale_at_extreme: Fraction
    canonical_segment_id: str
    source_pivot_ids: tuple[str, ...]
    provenance: Mapping[str, str]

    def __post_init__(self) -> None:
        if self.extreme_last_time < self.extreme_first_time:
            raise ValueError('extreme_last_time precedes extreme_first_time')
        if self.confirmed_at < self.extreme_last_time:
            raise ValueError('confirmed_at precedes extreme_last_time')
        if self.scale_at_extreme <= 0:
            raise ValueError('scale_at_extreme must be positive')
        if not self.canonical_segment_id:
            raise ValueError('canonical_segment_id is required')

@dataclass(frozen=True)
class LegMetrics:
    gross_displacement: Fraction
    normalized_displacement: Fraction
    directional_efficiency: InfoValue[Fraction]
    robust_normalized_slope: InfoValue[Fraction]

@dataclass(frozen=True)
class StructuralLeg:
    leg_id: str
    symbol: str
    timeframe_ms: int
    layer: StructuralLayer
    start_pivot_id: str
    end_pivot_id: str
    start_type: PivotType
    end_type: PivotType
    canonical_segment_id: str
    metrics: LegMetrics

@dataclass(frozen=True)
class EstablishmentEvidence:
    direction: TrendDirection
    newest_pivot_id: str
    sequence_pivot_ids: tuple[str, str, str, str]
    defended_opposite_pivot_id: str
    opposing_structural_cap_pivot_id: str

@dataclass(frozen=True)
class TrendEpisodeState:
    direction: TrendDirection
    episode_id: str | None
    episode_start_cutoff: int | None
    protected_pivot: StructuralPivot | None
    frontier_pivot: StructuralPivot | None
    phase: TrendPhase
    integrity: TrendIntegrity | None
    reversal_candidate_cap: StructuralPivot | None
    defended_pullback_after_pressure: bool
    prior_same_direction_edpr: InfoValue[Fraction]
    completed_trend_aligned_normalized_legs: tuple[Fraction, ...]
    terminal_episode_id: str | None = None

@dataclass(frozen=True)
class TrendPositionResult:
    position: TrendPosition
    x: InfoValue[Fraction]
    episode_excursion: InfoValue[Fraction]
    episode_median_leg_length: InfoValue[Fraction]
    overextension_ratio: InfoValue[Fraction]

@dataclass(frozen=True)
class StructuralCorridor:
    lower: Fraction
    upper: Fraction

@dataclass(frozen=True)
class FailedReexpansionEvent:
    event_id: str
    symbol: str
    timeframe_ms: int
    direction: TrendDirection
    confirmation_cutoff: int
    trend_side_minor_extreme_price: Fraction
    trend_side_minor_extreme_first_time: int
    trend_side_minor_extreme_last_time: int
    protected_structure_intact: bool
    independent_from_prior: bool
    rearmed_from_prior: bool

@dataclass(frozen=True)
class PlatformState:
    status: PlatformStatus
    contributing_event_ids: tuple[str, ...]
    trend_side_extremes: tuple[Fraction, ...]
    platform_cap_price: Fraction | None
    platform_scale: Fraction | None
    confirmed_at: int | None
    cap_first_time: int | None
    cap_last_time: int | None

# --- ORIGINAL d2_market_state/progress.py ---
from fractions import Fraction

def same_type_progress(p0: StructuralPivot, p1: StructuralPivot, theta_progress: Fraction) -> ProgressRelation:
    if p0.pivot_type is not p1.pivot_type:
        raise ValueError('same_type_progress requires same pivot type')
    if p0.layer is not p1.layer:
        raise ValueError('same_type_progress requires same structural layer')
    if p0.symbol != p1.symbol or p0.timeframe_ms != p1.timeframe_ms:
        raise ValueError('same_type_progress requires same symbol/timeframe')
    if p0.canonical_segment_id != p1.canonical_segment_id:
        raise ValueError('cross-gap progress comparison is forbidden')
    if p1.confirmed_at <= p0.confirmed_at:
        raise ValueError('p1 must be causally later than p0')
    if p0.scale_at_extreme <= 0:
        raise ValueError('p0 scale_at_extreme must be positive')
    delta_n = (p1.extreme_price - p0.extreme_price) / p0.scale_at_extreme
    if delta_n > theta_progress:
        return ProgressRelation.MATERIAL_ADVANCE_UP
    if delta_n < -theta_progress:
        return ProgressRelation.MATERIAL_ADVANCE_DOWN
    return ProgressRelation.STRUCTURALLY_EQUIVALENT

def normalized_delta(p0: StructuralPivot, p1: StructuralPivot) -> Fraction:
    if p0.scale_at_extreme <= 0:
        raise ValueError('p0 scale_at_extreme must be positive')
    return (p1.extreme_price - p0.extreme_price) / p0.scale_at_extreme

# --- ORIGINAL d2_market_state/establishment.py ---
from fractions import Fraction
from typing import Sequence

def latest_establishment_evidence(pivots: Sequence[StructuralPivot], *, theta_progress: Fraction) -> EstablishmentEvidence | None:
    """Evaluate only the latest complete alternating 4-pivot sequence ending at newest pivot."""
    if len(pivots) < 4:
        return None
    seq = tuple(pivots[-4:])
    if any((p.layer.value != 'INTERMEDIATE' for p in seq)):
        raise ValueError('Trend establishment consumes Intermediate pivots only')
    if len({p.canonical_segment_id for p in seq}) != 1:
        return None
    if not all((a.confirmed_at < b.confirmed_at for a, b in zip(seq, seq[1:]))):
        raise ValueError('Intermediate pivot stream must be causally ordered')
    types = tuple((p.pivot_type for p in seq))
    if types == (PivotType.LOW, PivotType.HIGH, PivotType.LOW, PivotType.HIGH):
        l0, h0, l1, h1 = seq
        high_progress = same_type_progress(h0, h1, theta_progress)
        low_progress = same_type_progress(l0, l1, theta_progress)
        if high_progress is ProgressRelation.MATERIAL_ADVANCE_UP and low_progress is not ProgressRelation.MATERIAL_ADVANCE_DOWN:
            return EstablishmentEvidence(direction=TrendDirection.LONG, newest_pivot_id=h1.pivot_id, sequence_pivot_ids=tuple((p.pivot_id for p in seq)), defended_opposite_pivot_id=l1.pivot_id, opposing_structural_cap_pivot_id=l1.pivot_id)
    if types == (PivotType.HIGH, PivotType.LOW, PivotType.HIGH, PivotType.LOW):
        h0, l0, h1, l1 = seq
        low_progress = same_type_progress(l0, l1, theta_progress)
        high_progress = same_type_progress(h0, h1, theta_progress)
        if low_progress is ProgressRelation.MATERIAL_ADVANCE_DOWN and high_progress is not ProgressRelation.MATERIAL_ADVANCE_UP:
            return EstablishmentEvidence(direction=TrendDirection.SHORT, newest_pivot_id=l1.pivot_id, sequence_pivot_ids=tuple((p.pivot_id for p in seq)), defended_opposite_pivot_id=h1.pivot_id, opposing_structural_cap_pivot_id=h1.pivot_id)
    return None

# --- ORIGINAL d2_market_state/pivots.py ---
from dataclasses import dataclass
from fractions import Fraction

@dataclass
class _MinorCandidate:
    pivot_type: PivotType
    price: Fraction
    first_time: int
    last_time: int
    scale: Fraction

class MinorDirectionalChangeEngine:
    """RC1 Minor directional-change state machine.

    Only canonical OHLC is consumed. A confirmation close may confirm a prior
    candidate, but the same confirmation bar's opposite wick is deliberately
    not reused as the next candidate because intrabar ordering is unknowable.
    """

    def __init__(self, *, symbol: str, timeframe_ms: int, theta_minor: Fraction) -> None:
        if theta_minor <= 0:
            raise ValueError('theta_minor must be positive')
        self.symbol = symbol
        self.timeframe_ms = timeframe_ms
        self.theta = theta_minor
        self.segment_id: str | None = None
        self.mode = SearchMode.UNKNOWN
        self.seed_close: Fraction | None = None
        self.seed_scale: Fraction | None = None
        self.candidate: _MinorCandidate | None = None
        self._sequence = 0

    def _reset(self, segment_id: str) -> None:
        self.segment_id = segment_id
        self.mode = SearchMode.UNKNOWN
        self.seed_close = None
        self.seed_scale = None
        self.candidate = None

    def _pivot(self, c: _MinorCandidate, *, confirmed_at: int, confirming_open_time: int) -> StructuralPivot:
        self._sequence += 1
        pid = deterministic_id('pivot', self.symbol, self.timeframe_ms, StructuralLayer.MINOR.value, c.pivot_type.value, c.price, c.first_time, c.last_time, confirmed_at, self.segment_id, self._sequence)
        return StructuralPivot(pivot_id=pid, symbol=self.symbol, timeframe_ms=self.timeframe_ms, layer=StructuralLayer.MINOR, pivot_type=c.pivot_type, extreme_price=c.price, extreme_first_time=c.first_time, extreme_last_time=c.last_time, confirmed_at=confirmed_at, scale_at_extreme=c.scale, canonical_segment_id=self.segment_id or '', source_pivot_ids=(), provenance={'rule': 'MS-003..MS-008', 'confirming_bar_open_time': str(confirming_open_time), 'ohlc_ordering': 'confirmation_close_may_confirm_prior_candidate; opposite_wick_not_reused_same_bar'})

    def update(self, bar: CanonicalBar, atr14: InfoValue[Fraction], *, canonical_segment_id: str) -> tuple[StructuralPivot, ...]:
        if bar.symbol != self.symbol:
            raise ValueError('symbol mismatch')
        if self.segment_id != canonical_segment_id:
            self._reset(canonical_segment_id)
        if atr14.kind is not InfoKind.KNOWN:
            return ()
        scale = atr14.require_known()
        if scale <= 0:
            return ()
        if self.mode is SearchMode.UNKNOWN:
            self.seed_close = bar.close
            self.seed_scale = scale
            self.mode = SearchMode.NEUTRAL
            return ()
        if self.mode is SearchMode.NEUTRAL:
            assert self.seed_close is not None and self.seed_scale is not None
            threshold = self.theta * self.seed_scale
            up = bar.close - self.seed_close
            down = self.seed_close - bar.close
            if up >= threshold:
                self.mode = SearchMode.SEEK_HIGH
                self.candidate = _MinorCandidate(PivotType.HIGH, bar.high, bar.open_time, bar.open_time, scale)
            elif down >= threshold:
                self.mode = SearchMode.SEEK_LOW
                self.candidate = _MinorCandidate(PivotType.LOW, bar.low, bar.open_time, bar.open_time, scale)
            return ()
        if self.candidate is None:
            if self.mode is SearchMode.SEEK_HIGH:
                self.candidate = _MinorCandidate(PivotType.HIGH, bar.high, bar.open_time, bar.open_time, scale)
                return ()
            if self.mode is SearchMode.SEEK_LOW:
                self.candidate = _MinorCandidate(PivotType.LOW, bar.low, bar.open_time, bar.open_time, scale)
                return ()
            raise AssertionError(f'unexpected mode {self.mode}')
        prior = self.candidate
        if self.mode is SearchMode.SEEK_HIGH:
            if bar.high > prior.price:
                self.candidate = _MinorCandidate(PivotType.HIGH, bar.high, bar.open_time, bar.open_time, scale)
                return ()
            if bar.high == prior.price:
                self.candidate = _MinorCandidate(PivotType.HIGH, prior.price, prior.first_time, bar.open_time, prior.scale)
                return ()
            if bar.open_time > prior.last_time and prior.price - bar.close >= self.theta * prior.scale:
                pivot = self._pivot(prior, confirmed_at=bar.close_time, confirming_open_time=bar.open_time)
                self.mode = SearchMode.SEEK_LOW
                self.candidate = None
                return (pivot,)
            return ()
        if self.mode is SearchMode.SEEK_LOW:
            if bar.low < prior.price:
                self.candidate = _MinorCandidate(PivotType.LOW, bar.low, bar.open_time, bar.open_time, scale)
                return ()
            if bar.low == prior.price:
                self.candidate = _MinorCandidate(PivotType.LOW, prior.price, prior.first_time, bar.open_time, prior.scale)
                return ()
            if bar.open_time > prior.last_time and bar.close - prior.price >= self.theta * prior.scale:
                pivot = self._pivot(prior, confirmed_at=bar.close_time, confirming_open_time=bar.open_time)
                self.mode = SearchMode.SEEK_HIGH
                self.candidate = None
                return (pivot,)
            return ()
        raise AssertionError(f'unexpected mode {self.mode}')

@dataclass
class _HierarchyCandidate:
    source: StructuralPivot

class PivotStreamDirectionalChangeEngine:
    """Generic higher-layer directional change over confirmed lower-layer pivots."""

    def __init__(self, *, output_layer: StructuralLayer, theta: Fraction) -> None:
        if output_layer is StructuralLayer.MINOR:
            raise ValueError('Use MinorDirectionalChangeEngine for MINOR')
        if theta <= 0:
            raise ValueError('theta must be positive')
        self.output_layer = output_layer
        self.theta = theta
        self.segment_id: str | None = None
        self.mode = SearchMode.UNKNOWN
        self.seed: StructuralPivot | None = None
        self.candidate: _HierarchyCandidate | None = None
        self._sequence = 0

    @staticmethod
    def _expected_input_layer(output_layer: StructuralLayer) -> StructuralLayer:
        return StructuralLayer.MINOR if output_layer is StructuralLayer.INTERMEDIATE else StructuralLayer.INTERMEDIATE

    def _reset(self, segment_id: str) -> None:
        self.segment_id = segment_id
        self.mode = SearchMode.UNKNOWN
        self.seed = None
        self.candidate = None

    def _emit(self, candidate: StructuralPivot, confirmer: StructuralPivot) -> StructuralPivot:
        self._sequence += 1
        pid = deterministic_id('pivot', candidate.symbol, candidate.timeframe_ms, self.output_layer.value, candidate.pivot_type.value, candidate.extreme_price, candidate.extreme_first_time, candidate.extreme_last_time, confirmer.confirmed_at, candidate.canonical_segment_id, self._sequence)
        return StructuralPivot(pivot_id=pid, symbol=candidate.symbol, timeframe_ms=candidate.timeframe_ms, layer=self.output_layer, pivot_type=candidate.pivot_type, extreme_price=candidate.extreme_price, extreme_first_time=candidate.extreme_first_time, extreme_last_time=candidate.extreme_last_time, confirmed_at=confirmer.confirmed_at, scale_at_extreme=candidate.scale_at_extreme, canonical_segment_id=candidate.canonical_segment_id, source_pivot_ids=(candidate.pivot_id, confirmer.pivot_id), provenance={'rule': 'MS-012', 'method': 'directional_change_over_confirmed_lower_pivot_stream'})

    def update(self, pivot: StructuralPivot) -> tuple[StructuralPivot, ...]:
        expected = self._expected_input_layer(self.output_layer)
        if pivot.layer is not expected:
            raise ValueError(f'{self.output_layer.value} requires {expected.value} input pivots')
        if self.segment_id != pivot.canonical_segment_id:
            self._reset(pivot.canonical_segment_id)
        if self.mode is SearchMode.UNKNOWN:
            self.seed = pivot
            self.mode = SearchMode.NEUTRAL
            return ()
        if self.mode is SearchMode.NEUTRAL:
            assert self.seed is not None
            if pivot.pivot_type is self.seed.pivot_type:
                if pivot.pivot_type is PivotType.HIGH and pivot.extreme_price >= self.seed.extreme_price:
                    self.seed = pivot
                elif pivot.pivot_type is PivotType.LOW and pivot.extreme_price <= self.seed.extreme_price:
                    self.seed = pivot
                return ()
            threshold = self.theta * self.seed.scale_at_extreme
            delta = pivot.extreme_price - self.seed.extreme_price
            if delta >= threshold:
                self.mode = SearchMode.SEEK_HIGH
                self.candidate = _HierarchyCandidate(pivot if pivot.pivot_type is PivotType.HIGH else self.seed)
            elif delta <= -threshold:
                self.mode = SearchMode.SEEK_LOW
                self.candidate = _HierarchyCandidate(pivot if pivot.pivot_type is PivotType.LOW else self.seed)
            return ()
        assert self.candidate is not None
        c = self.candidate.source
        if self.mode is SearchMode.SEEK_HIGH:
            if pivot.pivot_type is PivotType.LOW and c.extreme_price - pivot.extreme_price >= self.theta * c.scale_at_extreme:
                emitted = self._emit(c, pivot)
                self.mode = SearchMode.SEEK_LOW
                self.candidate = _HierarchyCandidate(pivot)
                return (emitted,)
            if pivot.pivot_type is PivotType.HIGH and pivot.extreme_price >= c.extreme_price:
                self.candidate = _HierarchyCandidate(pivot)
            return ()
        if self.mode is SearchMode.SEEK_LOW:
            if pivot.pivot_type is PivotType.HIGH and pivot.extreme_price - c.extreme_price >= self.theta * c.scale_at_extreme:
                emitted = self._emit(c, pivot)
                self.mode = SearchMode.SEEK_HIGH
                self.candidate = _HierarchyCandidate(pivot)
                return (emitted,)
            if pivot.pivot_type is PivotType.LOW and pivot.extreme_price <= c.extreme_price:
                self.candidate = _HierarchyCandidate(pivot)
            return ()
        raise AssertionError(f'unexpected mode {self.mode}')

# --- ORIGINAL d2_market_state/hierarchy.py ---
from dataclasses import dataclass
from fractions import Fraction

@dataclass(frozen=True)
class HierarchyUpdate:
    minor: tuple[StructuralPivot, ...]
    intermediate: tuple[StructuralPivot, ...]
    major: tuple[StructuralPivot, ...]

class StructuralHierarchyEngine:
    """One timeframe's Minor -> Intermediate -> Major RC1 hierarchy."""

    def __init__(self, *, symbol: str, timeframe_ms: int, params: StructuralScaleParameters) -> None:
        self.minor = MinorDirectionalChangeEngine(symbol=symbol, timeframe_ms=timeframe_ms, theta_minor=params.theta_minor)
        self.intermediate = PivotStreamDirectionalChangeEngine(output_layer=StructuralLayer.INTERMEDIATE, theta=params.theta_intermediate)
        self.major = PivotStreamDirectionalChangeEngine(output_layer=StructuralLayer.MAJOR, theta=params.theta_major)
        self._all_minor: list[StructuralPivot] = []
        self._all_intermediate: list[StructuralPivot] = []
        self._all_major: list[StructuralPivot] = []

    @property
    def all_minor(self) -> tuple[StructuralPivot, ...]:
        return tuple(self._all_minor)

    @property
    def all_intermediate(self) -> tuple[StructuralPivot, ...]:
        return tuple(self._all_intermediate)

    @property
    def all_major(self) -> tuple[StructuralPivot, ...]:
        return tuple(self._all_major)

    def update_bar(self, bar: CanonicalBar, atr14: InfoValue[Fraction], *, canonical_segment_id: str) -> HierarchyUpdate:
        minors = self.minor.update(bar, atr14, canonical_segment_id=canonical_segment_id)
        inters: list[StructuralPivot] = []
        majors: list[StructuralPivot] = []
        for p in minors:
            self._all_minor.append(p)
            new_i = self.intermediate.update(p)
            for ip in new_i:
                self._all_intermediate.append(ip)
                inters.append(ip)
                new_m = self.major.update(ip)
                for mp in new_m:
                    self._all_major.append(mp)
                    majors.append(mp)
        return HierarchyUpdate(minors, tuple(inters), tuple(majors))

# --- ORIGINAL d2_market_state/structural_legs.py ---
from dataclasses import dataclass
from fractions import Fraction
from statistics import median
from typing import Sequence

@dataclass(frozen=True)
class TimedClose:
    open_time: int
    close: Fraction

def _theil_sen_normalized_slope(closes: Sequence[TimedClose], *, timeframe_ms: int, scale_at_leg_start: Fraction) -> InfoValue[Fraction]:
    if len(closes) < 3:
        return InfoValue.na()
    if scale_at_leg_start <= 0:
        return InfoValue.error('NONPOSITIVE_LEG_START_SCALE')
    ordered = sorted(closes, key=lambda c: c.open_time)
    if len({c.open_time for c in ordered}) != len(ordered):
        return InfoValue.error('DUPLICATE_CLOSE_TIME_IN_LEG')
    slopes: list[Fraction] = []
    for i, left in enumerate(ordered[:-1]):
        for right in ordered[i + 1:]:
            delta_ms = right.open_time - left.open_time
            if delta_ms <= 0 or delta_ms % timeframe_ms != 0:
                return InfoValue.error('NONCANONICAL_ELAPSED_INTERVAL_IN_LEG')
            dx = Fraction(delta_ms, timeframe_ms)
            dy = (right.close - left.close) / scale_at_leg_start
            slopes.append(dy / dx)
    return InfoValue.known(median(slopes)) if slopes else InfoValue.na()

def build_structural_leg(start: StructuralPivot, end: StructuralPivot, *, close_path: Sequence[TimedClose]) -> StructuralLeg:
    if start.pivot_type is end.pivot_type:
        raise ValueError('Structural Leg requires adjacent opposite pivots')
    if start.layer is not end.layer:
        raise ValueError('Structural Leg requires same layer')
    if start.symbol != end.symbol or start.timeframe_ms != end.timeframe_ms:
        raise ValueError('Structural Leg requires same symbol/timeframe')
    if start.canonical_segment_id != end.canonical_segment_id:
        raise ValueError('Structural Leg cannot cross a canonical gap')
    if end.confirmed_at <= start.confirmed_at:
        raise ValueError('end pivot must be causally later')
    gross = abs(end.extreme_price - start.extreme_price)
    normalized = gross / start.scale_at_extreme
    if len(close_path) < 2:
        efficiency = InfoValue.na()
    else:
        ordered = sorted(close_path, key=lambda c: c.open_time)
        path = sum((abs(b.close - a.close) for a, b in zip(ordered, ordered[1:])))
        if path == 0:
            efficiency = InfoValue.na()
        else:
            efficiency = InfoValue.known(abs(ordered[-1].close - ordered[0].close) / path)
    slope = _theil_sen_normalized_slope(close_path, timeframe_ms=start.timeframe_ms, scale_at_leg_start=start.scale_at_extreme)
    metrics = LegMetrics(gross_displacement=gross, normalized_displacement=normalized, directional_efficiency=efficiency, robust_normalized_slope=slope)
    leg_id = deterministic_id('structural_leg', start.pivot_id, end.pivot_id, start.canonical_segment_id)
    return StructuralLeg(leg_id=leg_id, symbol=start.symbol, timeframe_ms=start.timeframe_ms, layer=start.layer, start_pivot_id=start.pivot_id, end_pivot_id=end.pivot_id, start_type=start.pivot_type, end_type=end.pivot_type, canonical_segment_id=start.canonical_segment_id, metrics=metrics)

def trend_aligned_edpr(leg: StructuralLeg, direction: TrendDirection) -> InfoValue[Fraction]:
    """B2 EDPR = TrendAlignedRobustSlope × DirectionalEfficiency."""
    slope = leg.metrics.robust_normalized_slope
    efficiency = leg.metrics.directional_efficiency
    if slope.kind.value != 'KNOWN' or efficiency.kind.value != 'KNOWN':
        return InfoValue.na()
    if direction is TrendDirection.LONG:
        aligned = slope.require_known()
    elif direction is TrendDirection.SHORT:
        aligned = -slope.require_known()
    else:
        return InfoValue.na()
    if aligned < 0:
        return InfoValue.error('LEG_NOT_TREND_ALIGNED')
    return InfoValue.known(aligned * efficiency.require_known())

# --- ORIGINAL d2_market_state/trend.py ---
from dataclasses import replace
from fractions import Fraction
from typing import Mapping, Sequence

def initial_trend_state() -> TrendEpisodeState:
    return TrendEpisodeState(direction=TrendDirection.UNKNOWN, episode_id=None, episode_start_cutoff=None, protected_pivot=None, frontier_pivot=None, phase=TrendPhase.UNKNOWN, integrity=None, reversal_candidate_cap=None, defended_pullback_after_pressure=False, prior_same_direction_edpr=InfoValue.na(), completed_trend_aligned_normalized_legs=())

def _by_id(pivots: Sequence[StructuralPivot]) -> dict[str, StructuralPivot]:
    return {p.pivot_id: p for p in pivots}

def _episode_from_establishment(evidence: EstablishmentEvidence, pivots: Sequence[StructuralPivot], *, leg_by_end_pivot: Mapping[str, StructuralLeg]) -> TrendEpisodeState:
    lookup = _by_id(pivots)
    newest = lookup[evidence.newest_pivot_id]
    protected = lookup[evidence.defended_opposite_pivot_id]
    episode_id = deterministic_id('trend_episode', newest.symbol, newest.timeframe_ms, evidence.direction.value, newest.confirmed_at, newest.pivot_id)
    leg = leg_by_end_pivot.get(newest.pivot_id)
    if leg is not None:
        lengths = (leg.metrics.normalized_displacement,)
        baseline = trend_aligned_edpr(leg, evidence.direction)
    else:
        lengths = ()
        baseline = InfoValue.na()
    return TrendEpisodeState(direction=evidence.direction, episode_id=episode_id, episode_start_cutoff=newest.confirmed_at, protected_pivot=protected, frontier_pivot=newest, phase=TrendPhase.EXPANSION, integrity=TrendIntegrity.HEALTHY, reversal_candidate_cap=None, defended_pullback_after_pressure=False, prior_same_direction_edpr=baseline, completed_trend_aligned_normalized_legs=lengths)

def _is_adverse(direction: TrendDirection, pivot: StructuralPivot) -> bool:
    return direction is TrendDirection.LONG and pivot.pivot_type is PivotType.LOW or (direction is TrendDirection.SHORT and pivot.pivot_type is PivotType.HIGH)

def _is_favorable(direction: TrendDirection, pivot: StructuralPivot) -> bool:
    return direction is TrendDirection.LONG and pivot.pivot_type is PivotType.HIGH or (direction is TrendDirection.SHORT and pivot.pivot_type is PivotType.LOW)

def _material_failure(direction: TrendDirection, protected: StructuralPivot, adverse: StructuralPivot, theta_progress: Fraction) -> bool:
    relation = same_type_progress(protected, adverse, theta_progress)
    return direction is TrendDirection.LONG and relation is ProgressRelation.MATERIAL_ADVANCE_DOWN or (direction is TrendDirection.SHORT and relation is ProgressRelation.MATERIAL_ADVANCE_UP)

def _inside_protected_zone(protected: StructuralPivot, adverse: StructuralPivot, theta_progress: Fraction) -> bool:
    return abs(normalized_delta(protected, adverse)) <= theta_progress

def _classify_edpr_phase(prior: InfoValue[Fraction], current: InfoValue[Fraction], theta_rate: Fraction) -> TrendPhase:
    if prior.kind is not InfoKind.KNOWN or current.kind is not InfoKind.KNOWN:
        return TrendPhase.EXPANSION
    delta = current.require_known() - prior.require_known()
    if delta > theta_rate:
        return TrendPhase.ACCELERATION
    if delta < -theta_rate:
        return TrendPhase.DECELERATION
    return TrendPhase.EXPANSION

def _opposite(direction: TrendDirection) -> TrendDirection:
    if direction is TrendDirection.LONG:
        return TrendDirection.SHORT
    if direction is TrendDirection.SHORT:
        return TrendDirection.LONG
    return TrendDirection.NONE

def _recovery_breaks_cap(direction: TrendDirection, cap: StructuralPivot, favorable: StructuralPivot, theta_progress: Fraction) -> bool:
    if cap.pivot_type is not favorable.pivot_type:
        return False
    rel = same_type_progress(cap, favorable, theta_progress)
    return direction is TrendDirection.LONG and rel is ProgressRelation.MATERIAL_ADVANCE_UP or (direction is TrendDirection.SHORT and rel is ProgressRelation.MATERIAL_ADVANCE_DOWN)

def on_new_intermediate_pivot(state: TrendEpisodeState, pivots: Sequence[StructuralPivot], *, theta_progress: Fraction, theta_rate: Fraction, leg_by_end_pivot: Mapping[str, StructuralLeg]) -> TrendEpisodeState:
    """UPDATE-006 event-driven D2 Trend transition on newest confirmed Intermediate pivot only."""
    if not pivots:
        return state
    newest = pivots[-1]
    if newest.layer.value != 'INTERMEDIATE':
        raise ValueError('Trend consumes Intermediate pivots only')
    if newest.confirmed_at != max((p.confirmed_at for p in pivots)):
        raise ValueError('newest pivot must be latest causal Intermediate event')
    evidence = latest_establishment_evidence(pivots, theta_progress=theta_progress)
    if state.direction not in (TrendDirection.LONG, TrendDirection.SHORT) or state.episode_id is None:
        if evidence is not None:
            return _episode_from_establishment(evidence, pivots, leg_by_end_pivot=leg_by_end_pivot)
        if len(pivots) >= 4:
            return replace(state, direction=TrendDirection.NONE, phase=TrendPhase.NO_TREND, integrity=None)
        return replace(state, direction=TrendDirection.UNKNOWN, phase=TrendPhase.UNKNOWN, integrity=None)
    direction = state.direction
    protected = state.protected_pivot
    if protected is None:
        raise ValueError('active Trend Episode requires Protected Intermediate Structure')
    if _is_adverse(direction, newest) and _material_failure(direction, protected, newest, theta_progress):
        terminal = state.episode_id
        if evidence is not None and evidence.direction is _opposite(direction):
            new_state = _episode_from_establishment(evidence, pivots, leg_by_end_pivot=leg_by_end_pivot)
            return replace(new_state, terminal_episode_id=terminal)
        return TrendEpisodeState(direction=TrendDirection.NONE, episode_id=None, episode_start_cutoff=None, protected_pivot=None, frontier_pivot=None, phase=TrendPhase.STRUCTURAL_FAILURE, integrity=TrendIntegrity.FAILED, reversal_candidate_cap=None, defended_pullback_after_pressure=False, prior_same_direction_edpr=InfoValue.na(), completed_trend_aligned_normalized_legs=(), terminal_episode_id=terminal)
    if evidence is not None and evidence.direction is _opposite(direction):
        lookup = _by_id(pivots)
        cap = lookup[evidence.defended_opposite_pivot_id]
        return replace(state, phase=TrendPhase.REVERSAL_CANDIDATE, integrity=TrendIntegrity.DETERIORATING, reversal_candidate_cap=cap, defended_pullback_after_pressure=False)
    if _is_adverse(direction, newest):
        pressured = _inside_protected_zone(protected, newest, theta_progress)
        if state.integrity is TrendIntegrity.PRESSURED:
            return replace(state, defended_pullback_after_pressure=True)
        if state.integrity is TrendIntegrity.DETERIORATING:
            return state
        if pressured:
            return replace(state, integrity=TrendIntegrity.PRESSURED, defended_pullback_after_pressure=False)
        return state
    if _is_favorable(direction, newest):
        prior_frontier = state.frontier_pivot
        state2 = replace(state, frontier_pivot=newest)
        if state.integrity is TrendIntegrity.DETERIORATING and state.reversal_candidate_cap is not None:
            if _recovery_breaks_cap(direction, state.reversal_candidate_cap, newest, theta_progress):
                leg = leg_by_end_pivot.get(newest.pivot_id)
                phase = _classify_edpr_phase(state.prior_same_direction_edpr, trend_aligned_edpr(leg, direction) if leg else InfoValue.na(), theta_rate)
                prior_edpr = trend_aligned_edpr(leg, direction) if leg is not None else state.prior_same_direction_edpr
                lengths = state.completed_trend_aligned_normalized_legs + ((leg.metrics.normalized_displacement,) if leg else ())
                return replace(state2, phase=phase, integrity=TrendIntegrity.PRESSURED, reversal_candidate_cap=None, defended_pullback_after_pressure=False, prior_same_direction_edpr=prior_edpr, completed_trend_aligned_normalized_legs=lengths)
            return state2
        material = False
        if prior_frontier is not None and prior_frontier.pivot_type is newest.pivot_type:
            rel = same_type_progress(prior_frontier, newest, theta_progress)
            material = direction is TrendDirection.LONG and rel is ProgressRelation.MATERIAL_ADVANCE_UP or (direction is TrendDirection.SHORT and rel is ProgressRelation.MATERIAL_ADVANCE_DOWN)
        if not material:
            return state2
        candidate = pivots[-2] if len(pivots) >= 2 and pivots[-2].pivot_type is not newest.pivot_type else None
        protected2 = protected
        if candidate is not None and candidate.pivot_type is protected.pivot_type:
            relp = same_type_progress(protected, candidate, theta_progress)
            if direction is TrendDirection.LONG and relp is ProgressRelation.MATERIAL_ADVANCE_UP:
                protected2 = candidate
            elif direction is TrendDirection.SHORT and relp is ProgressRelation.MATERIAL_ADVANCE_DOWN:
                protected2 = candidate
        leg = leg_by_end_pivot.get(newest.pivot_id)
        phase = _classify_edpr_phase(state.prior_same_direction_edpr, trend_aligned_edpr(leg, direction) if leg else InfoValue.na(), theta_rate)
        new_edpr = trend_aligned_edpr(leg, direction) if leg is not None else state.prior_same_direction_edpr
        lengths = state.completed_trend_aligned_normalized_legs + ((leg.metrics.normalized_displacement,) if leg else ())
        integrity = state.integrity
        defended = state.defended_pullback_after_pressure
        if integrity is TrendIntegrity.PRESSURED and defended:
            integrity = TrendIntegrity.HEALTHY
            defended = False
        return replace(state2, protected_pivot=protected2, phase=phase, integrity=integrity, defended_pullback_after_pressure=defended, prior_same_direction_edpr=new_edpr, completed_trend_aligned_normalized_legs=lengths)
    return state

# --- ORIGINAL d2_market_state/trend_position.py ---
from fractions import Fraction
from statistics import median

def protected_equivalence_zone(protected: StructuralPivot, theta_progress: Fraction) -> tuple[Fraction, Fraction]:
    half = theta_progress * protected.scale_at_extreme
    return (protected.extreme_price - half, protected.extreme_price + half)

def structural_corridor(*, direction: TrendDirection, protected: StructuralPivot | None, frontier: StructuralPivot | None, current_close: Fraction, theta_progress: Fraction) -> InfoValue[StructuralCorridor]:
    if direction not in (TrendDirection.LONG, TrendDirection.SHORT):
        return InfoValue.na()
    if protected is None or frontier is None:
        return InfoValue.unknown()
    low_zone, high_zone = protected_equivalence_zone(protected, theta_progress)
    if direction is TrendDirection.LONG:
        return InfoValue.known(StructuralCorridor(low_zone, max(current_close, frontier.extreme_price)))
    return InfoValue.known(StructuralCorridor(min(current_close, frontier.extreme_price), high_zone))

def classify_trend_position(*, direction: TrendDirection, current_close: Fraction, frontier: StructuralPivot | None, reset_pivot: StructuralPivot | None, theta_progress: Fraction, theta_overextension: Fraction, completed_trend_aligned_normalized_legs: tuple[Fraction, ...]) -> TrendPositionResult:
    if direction not in (TrendDirection.LONG, TrendDirection.SHORT):
        return TrendPositionResult(TrendPosition.NA, InfoValue.na(), InfoValue.na(), InfoValue.na(), InfoValue.na())
    if frontier is None or frontier.scale_at_extreme <= 0:
        return TrendPositionResult(TrendPosition.UNKNOWN, InfoValue.unknown(), InfoValue.unknown(), InfoValue.unknown(), InfoValue.unknown())
    sign = Fraction(1) if direction is TrendDirection.LONG else Fraction(-1)
    x = sign * (current_close - frontier.extreme_price) / frontier.scale_at_extreme
    if abs(x) <= theta_progress:
        base = TrendPosition.BALANCED
    elif x < -theta_progress:
        base = TrendPosition.PULLBACK
    else:
        base = TrendPosition.EXTENDED
    if reset_pivot is None or reset_pivot.scale_at_extreme <= 0:
        return TrendPositionResult(base, InfoValue.known(x), InfoValue.unknown(), InfoValue.unknown(), InfoValue.unknown())
    l_t = sign * (current_close - reset_pivot.extreme_price) / reset_pivot.scale_at_extreme
    positive_legs = tuple((v for v in completed_trend_aligned_normalized_legs if v > 0))
    if not positive_legs:
        return TrendPositionResult(base, InfoValue.known(x), InfoValue.known(l_t), InfoValue.na(), InfoValue.na())
    m_episode = median(positive_legs)
    if m_episode <= 0:
        return TrendPositionResult(base, InfoValue.known(x), InfoValue.known(l_t), InfoValue.error('NONPOSITIVE_EPISODE_MEDIAN'), InfoValue.error('NONPOSITIVE_EPISODE_MEDIAN'))
    ratio = l_t / m_episode
    pos = TrendPosition.OVEREXTENDED if base is TrendPosition.EXTENDED and ratio > theta_overextension else base
    return TrendPositionResult(pos, InfoValue.known(x), InfoValue.known(l_t), InfoValue.known(m_episode), InfoValue.known(ratio))

# --- ORIGINAL d2_reference.py ---
"""Non-trading WP2 D2 reference skeleton.

Only D2-owned UPDATE-005, UPDATE-006 and UPDATE-009 semantics are represented.
Construction from the current durable partial ParameterSnapshot is expected to
fail because theta_minor/intermediate/major remain OPEN.
"""
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Iterable

@dataclass
class _TimeframeState:
    symbol: str
    timeframe_ms: int
    structural_params: StructuralScaleParameters
    hierarchy: StructuralHierarchyEngine = field(init=False)
    segment_id: str | None = None
    intermediate: list[StructuralPivot] = field(default_factory=list)
    legs_by_end: dict[str, StructuralLeg] = field(default_factory=dict)
    closes: list[TimedClose] = field(default_factory=list)
    trend: TrendEpisodeState = field(default_factory=initial_trend_state)

    def __post_init__(self) -> None:
        self.hierarchy = StructuralHierarchyEngine(symbol=self.symbol, timeframe_ms=self.timeframe_ms, params=self.structural_params)

    def reset_for_segment(self, segment_id: str) -> None:
        self.segment_id = segment_id
        self.hierarchy = StructuralHierarchyEngine(symbol=self.symbol, timeframe_ms=self.timeframe_ms, params=self.structural_params)
        self.intermediate.clear()
        self.legs_by_end.clear()
        self.closes.clear()
        self.trend = initial_trend_state()

@dataclass(frozen=True)
class D2CutoffResult:
    information_cutoff: int
    update_005_minor: tuple[StructuralPivot, ...]
    update_005_intermediate: tuple[StructuralPivot, ...]
    update_005_major: tuple[StructuralPivot, ...]
    update_006_trend: TrendEpisodeState
    update_009_trend_position: object
    update_009_structural_corridor: object

class D2ReferenceSkeleton:

    def __init__(self, *, symbol: str, structural_params: StructuralScaleParameters, frozen_params: FrozenD2Parameters) -> None:
        self.symbol = symbol
        self.structural_params = structural_params
        self.frozen_params = frozen_params
        self._tf: dict[int, _TimeframeState] = {}

    @classmethod
    def from_parameter_snapshot(cls, *, symbol: str, snapshot: ParameterSnapshot) -> 'D2ReferenceSkeleton':
        structural = require_structural_scale_parameters(snapshot)
        frozen = frozen_d2_parameters(snapshot)
        return cls(symbol=symbol, structural_params=structural, frozen_params=frozen)

    def _state(self, timeframe_ms: int) -> _TimeframeState:
        state = self._tf.get(timeframe_ms)
        if state is None:
            state = _TimeframeState(self.symbol, timeframe_ms, self.structural_params)
            self._tf[timeframe_ms] = state
        return state

    @staticmethod
    def _reset_pivot(state: _TimeframeState) -> StructuralPivot | None:
        if state.trend.direction is TrendDirection.LONG:
            lows = [p for p in state.intermediate if p.pivot_type is PivotType.LOW]
            return lows[-1] if lows else state.trend.protected_pivot
        if state.trend.direction is TrendDirection.SHORT:
            highs = [p for p in state.intermediate if p.pivot_type is PivotType.HIGH]
            return highs[-1] if highs else state.trend.protected_pivot
        return None

    def advance_source_bar(self, bar: CanonicalBar, atr14: InfoValue[Fraction], *, canonical_segment_id: str) -> D2CutoffResult:
        """Execute only D2's UPDATE-005 -> UPDATE-006 -> UPDATE-009 slice."""
        state = self._state(self._infer_timeframe(bar))
        if state.segment_id != canonical_segment_id:
            state.reset_for_segment(canonical_segment_id)
        state.closes.append(TimedClose(bar.open_time, bar.close))
        update = state.hierarchy.update_bar(bar, atr14, canonical_segment_id=canonical_segment_id)
        for ip in update.intermediate:
            if state.intermediate:
                prior = state.intermediate[-1]
                if prior.pivot_type is not ip.pivot_type and prior.canonical_segment_id == ip.canonical_segment_id:
                    close_path = tuple((c for c in state.closes if prior.extreme_first_time <= c.open_time <= ip.extreme_last_time))
                    try:
                        state.legs_by_end[ip.pivot_id] = build_structural_leg(prior, ip, close_path=close_path)
                    except ValueError:
                        pass
            state.intermediate.append(ip)
            state.trend = on_new_intermediate_pivot(state.trend, state.intermediate, theta_progress=self.frozen_params.theta_progress, theta_rate=self.frozen_params.theta_rate, leg_by_end_pivot=state.legs_by_end)
        reset = self._reset_pivot(state)
        tpos = classify_trend_position(direction=state.trend.direction, current_close=bar.close, frontier=state.trend.frontier_pivot, reset_pivot=reset, theta_progress=self.frozen_params.theta_progress, theta_overextension=self.frozen_params.theta_overextension, completed_trend_aligned_normalized_legs=state.trend.completed_trend_aligned_normalized_legs)
        corridor = structural_corridor(direction=state.trend.direction, protected=state.trend.protected_pivot, frontier=state.trend.frontier_pivot, current_close=bar.close, theta_progress=self.frozen_params.theta_progress)
        return D2CutoffResult(information_cutoff=bar.close_time, update_005_minor=update.minor, update_005_intermediate=update.intermediate, update_005_major=update.major, update_006_trend=state.trend, update_009_trend_position=tpos, update_009_structural_corridor=corridor)

    @staticmethod
    def _infer_timeframe(bar: CanonicalBar) -> int:
        span = bar.close_time - bar.open_time
        candidates = (15 * 60 * 1000, 60 * 60 * 1000, 4 * 60 * 60 * 1000)
        for tf in candidates:
            if span in (tf, tf - 1):
                return tf
        raise ValueError(f'Unsupported D2 source timeframe span={span}')

# --- ORIGINAL d3_boundary_intelligence/types.py ---
from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction
from typing import Mapping

class CandidateFamily(str, Enum):
    EMA20 = 'EMA20'
    EMA50 = 'EMA50'
    ST_ACTIVE = 'ST_ACTIVE'

class CandidateAvailability(str, Enum):
    AVAILABLE = 'AVAILABLE'
    UNAVAILABLE = 'UNAVAILABLE'

class AnchorValidity(str, Enum):
    PROVISIONAL = 'PROVISIONAL'
    VALID = 'VALID'
    TERMINATED = 'TERMINATED'

class AnchorActivity(str, Enum):
    ACTIVE = 'ACTIVE'
    PRESSURED = 'PRESSURED'
    TERMINATED = 'TERMINATED'

class InteractionControl(str, Enum):
    UNARMED = 'UNARMED'
    ARMED = 'ARMED'
    INTERACTION_ACTIVE = 'INTERACTION_ACTIVE'
    RESOLVED = 'RESOLVED'

class InteractionResolution(str, Enum):
    RESOLVED_CORRECT_SIDE = 'RESOLVED_CORRECT_SIDE'
    RESOLVED_WRONG_SIDE = 'RESOLVED_WRONG_SIDE'
    UNRESOLVED = 'UNRESOLVED'
    ABORTED_APPROACH = 'ABORTED_APPROACH'
    UNKNOWN_CONTINUITY = 'UNKNOWN_CONTINUITY'

class BreakState(str, Enum):
    NONE = 'NONE'
    WRONG_SIDE_UNARMED = 'WRONG_SIDE_UNARMED'
    PROBE = 'PROBE'
    TEMPORARY_BREAK = 'TEMPORARY_BREAK'
    RECLAIMING = 'RECLAIMING'
    TRUE_BREAK = 'TRUE_BREAK'
    FALSE_BREAK = 'FALSE_BREAK'

class Role(str, Enum):
    PRIMARY = 'PRIMARY'
    SECONDARY = 'SECONDARY'
    STRUCTURAL = 'STRUCTURAL'

class RoleTransition(str, Enum):
    NONE = 'NONE'
    HANDOFF = 'HANDOFF'
    PROMOTION = 'PROMOTION'
    REPLACEMENT = 'REPLACEMENT'
    UNRESOLVED = 'UNRESOLVED'

class StructuralDepthRelation(str, Enum):
    SAME_LAYER = 'SAME_LAYER'
    DEEPER = 'DEEPER'
    SHALLOWER = 'SHALLOWER'
    UNRESOLVED = 'UNRESOLVED'

@dataclass(frozen=True)
class MathematicalBoundaryCandidate:
    candidate_id: str
    symbol: str
    source_timeframe_ms: int
    target_trend_episode_id: str
    target_direction: TrendDirection
    family: CandidateFamily
    boundary: InfoValue[Fraction]
    source_scale: InfoValue[Fraction]
    source_segment_id: str
    available_at: int
    availability: CandidateAvailability
    provenance: Mapping[str, str]

@dataclass(frozen=True)
class CausalBoundarySnapshot:
    snapshot_id: str
    candidate_id: str
    anchor_episode_id: str | None
    symbol: str
    source_timeframe_ms: int
    target_trend_episode_id: str
    target_direction: TrendDirection
    family: CandidateFamily
    boundary: Fraction
    source_scale: Fraction
    source_segment_id: str
    available_at: int
    provenance: Mapping[str, str]

@dataclass(frozen=True)
class B3Geometry:
    information_cutoff: int
    snapshot_id: str
    d_close: Fraction
    d_range_nearest: Fraction
    test: bool
    approach: bool
    separated: bool
    hysteresis_intermediate: bool
    wrong_side_range_penetration: bool
    wrong_side_close: bool
    material_wrong_side_separation: bool

@dataclass(frozen=True)
class PriceDrivenReturnEvidence:
    passed: bool
    adverse_raw_movement: Fraction
    minimum_required: Fraction
    provenance: Mapping[str, str]

@dataclass(frozen=True)
class StructuralAcceptanceEvidence:
    continuation_acceptance: bool = False
    failed_return_acceptance: bool = False
    confirmed_wrong_side_minor_extreme_id: str | None = None
    renewed_wrong_side_progress_pivot_id: str | None = None
    failed_return_progress_pivot_id: str | None = None

@dataclass(frozen=True)
class CorrectSideRecoveryEvidence:
    turning_structure_confirmed: bool = False
    material_correct_side_structural_recovery: bool = False
    turning_pivot_id: str | None = None
    recovery_pivot_id: str | None = None

@dataclass(frozen=True)
class InteractionEvent:
    event_id: str
    candidate_id: str
    anchor_episode_id: str | None
    target_trend_episode_id: str
    target_direction: TrendDirection
    control: InteractionControl
    resolution: InteractionResolution
    event_reference_boundary: Fraction | None
    event_reference_scale: Fraction | None
    started_at: int | None
    resolved_at: int | None
    armed_at: int | None
    approach_lineage_started_at: int | None
    attempted_wrong_side_acceptance: bool
    material_wrong_side_separation_observed: bool
    reclaim_observed: bool
    break_state: BreakState
    terminal: bool
    provenance: Mapping[str, str] = field(default_factory=dict)

@dataclass(frozen=True)
class BreakEvaluation:
    break_state: BreakState
    terminal: bool
    resolution: InteractionResolution
    attempted_wrong_side_acceptance: bool
    material_wrong_side_separation_observed: bool
    reclaim_observed: bool
    reason: str

@dataclass(frozen=True)
class TrendSideMinorProgressEvidence:
    pivot_id: str
    confirmed_at: int
    material_progress: bool
    timeframe_ms: int
    layer: str = 'MINOR'

@dataclass(frozen=True)
class QualifiedBoundaryUse:
    use_id: str
    anchor_episode_id: str
    negotiation_event_id: str
    correct_side_resolution_cutoff: int
    trend_side_minor_progress_pivot_id: str
    progress_confirmed_at: int

@dataclass(frozen=True)
class AnchorEvidenceDossier:
    boundary_side_integrity: InfoValue[str]
    structural_integrity: InfoValue[str]
    slope_alignment: InfoValue[str]
    independent_retest_evidence: InfoValue[str]
    retest_quality: InfoValue[str]
    current_relevance: InfoValue[str]
    true_break_evidence: InfoValue[str]
    data_confidence: InfoValue[str]

@dataclass(frozen=True)
class AnchorEpisode:
    anchor_episode_id: str
    candidate_id: str
    target_trend_episode_id: str
    target_direction: TrendDirection
    validity: AnchorValidity
    activity: AnchorActivity
    started_at: int
    ended_at: int | None
    interaction_event_ids: tuple[str, ...]
    qualified_uses: tuple[QualifiedBoundaryUse, ...]
    terminal_true_break: bool
    dossier: AnchorEvidenceDossier
    provenance: Mapping[str, str] = field(default_factory=dict)

@dataclass(frozen=True)
class BoundaryContactZone:
    zone_id: str
    anchor_episode_id: str
    lower: Fraction
    upper: Fraction
    information_cutoff: int
    provenance: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.upper < self.lower:
            raise ValueError('contact zone upper < lower')

    def intersects(self, lower: Fraction, upper: Fraction) -> bool:
        return self.lower <= upper and lower <= self.upper

@dataclass(frozen=True)
class EconomicBoundaryUnit:
    unit_id: str
    anchor_episode_ids: tuple[str, ...]
    contact_zones: tuple[BoundaryContactZone, ...]
    is_cluster: bool
    provenance: Mapping[str, str] = field(default_factory=dict)

@dataclass(frozen=True)
class BoundaryUnitRoleEvidence:
    unit: EconomicBoundaryUnit
    at_least_one_valid_member: bool
    current_relevant: bool
    latest_qualified_use_cutoff: int | None
    terminal_true_break: bool
    active_qualifying_interaction: bool
    unresolved_conflict: bool
    structural_depth_relation_to_primary: StructuralDepthRelation = StructuralDepthRelation.UNRESOLVED

@dataclass(frozen=True)
class EntryAnchorReference:
    """Interface-only reference: Entry Anchor need not equal Primary.

    WP3 does not create Opportunity or ENTRY_READY; a later D4 layer may consume
    a validated active Economic Boundary Unit through this reference.
    """
    unit_id: str
    validation_provenance: Mapping[str, str] = field(default_factory=dict)

@dataclass(frozen=True)
class RoleAssignment:
    primary_unit_id: str | None
    secondary_unit_id: str | None
    structural_unit_ids: tuple[str, ...]
    transition: RoleTransition
    unresolved_reason: str | None

@dataclass(frozen=True)
class PreBarBoundaryView:
    observer_open_time: int
    snapshots: tuple[CausalBoundarySnapshot, ...]

@dataclass(frozen=True)
class D3CutoffView:
    information_cutoff: int
    update_002_geometry: tuple[B3Geometry, ...]
    update_007_events: tuple[InteractionEvent, ...]
    update_008_anchor_episodes: tuple[AnchorEpisode, ...]
    update_008_units: tuple[EconomicBoundaryUnit, ...]
    update_008_roles: RoleAssignment | None

# --- ORIGINAL d3_boundary_intelligence/parameters.py ---
from dataclasses import dataclass
from fractions import Fraction

@dataclass(frozen=True)
class FrozenD3Parameters:
    theta_test: Fraction
    theta_approach: Fraction
    theta_separation: Fraction
    theta_accept: Fraction
    theta_progress: Fraction

def _frozen_fraction(snapshot: ParameterSnapshot, name: str) -> Fraction:
    slot = snapshot.slot(name)
    if slot.state is not ParameterState.FROZEN or slot.exact_value is None:
        raise ValueError(f'{name} must be FROZEN with an exact value for WP3')
    return Fraction(slot.exact_value)

def frozen_d3_parameters(snapshot: ParameterSnapshot) -> FrozenD3Parameters:
    p = FrozenD3Parameters(theta_test=_frozen_fraction(snapshot, 'theta_test'), theta_approach=_frozen_fraction(snapshot, 'theta_approach'), theta_separation=_frozen_fraction(snapshot, 'theta_separation'), theta_accept=_frozen_fraction(snapshot, 'theta_accept'), theta_progress=_frozen_fraction(snapshot, 'theta_progress'))
    if not Fraction(0) <= p.theta_test < p.theta_approach < p.theta_separation:
        raise ValueError('RC1 B3 geometry ordering violated')
    if p.theta_accept <= 0:
        raise ValueError('theta_accept must be > 0')
    return p

# --- ORIGINAL d3_boundary_intelligence/candidates.py ---
from fractions import Fraction
from typing import Mapping

def build_candidate(*, symbol: str, source_timeframe_ms: int, target_trend_episode_id: str, target_direction: TrendDirection, family: CandidateFamily, line: InfoValue[Fraction], source_scale: InfoValue[Fraction], source_segment_id: str, available_at: int, source_continuity_ok: bool, st_direction: Direction | None=None, provenance: Mapping[str, str] | None=None) -> MathematicalBoundaryCandidate:
    """Create a D1 mathematical boundary candidate without creating Trend truth.

    F1 availability is explicit. ST active line is UNAVAILABLE while ST direction
    is UNKNOWN. Source-TF Trend alignment is intentionally not required by F1.
    """
    available = source_continuity_ok and line.kind is InfoKind.KNOWN and (source_scale.kind is InfoKind.KNOWN)
    if family is CandidateFamily.ST_ACTIVE and (st_direction is None or st_direction is Direction.UNKNOWN):
        available = False
    candidate_id = deterministic_id('D3-CAND', symbol, str(source_timeframe_ms), target_trend_episode_id, target_direction.value, family.value, source_segment_id)
    return MathematicalBoundaryCandidate(candidate_id=candidate_id, symbol=symbol, source_timeframe_ms=source_timeframe_ms, target_trend_episode_id=target_trend_episode_id, target_direction=target_direction, family=family, boundary=line if available else InfoValue.na(), source_scale=source_scale if available else InfoValue.na(), source_segment_id=source_segment_id, available_at=available_at, availability=CandidateAvailability.AVAILABLE if available else CandidateAvailability.UNAVAILABLE, provenance=dict(provenance or {}))

# --- ORIGINAL d3_boundary_intelligence/snapshots.py ---
def snapshot_from_candidate(candidate: MathematicalBoundaryCandidate, *, anchor_episode_id: str | None) -> CausalBoundarySnapshot | None:
    if candidate.availability is CandidateAvailability.UNAVAILABLE:
        return None
    boundary = candidate.boundary.require_known()
    scale = candidate.source_scale.require_known()
    return CausalBoundarySnapshot(snapshot_id=deterministic_id('D3-SNAPSHOT', candidate.candidate_id, str(candidate.available_at), anchor_episode_id or 'WATCH'), candidate_id=candidate.candidate_id, anchor_episode_id=anchor_episode_id, symbol=candidate.symbol, source_timeframe_ms=candidate.source_timeframe_ms, target_trend_episode_id=candidate.target_trend_episode_id, target_direction=candidate.target_direction, family=candidate.family, boundary=boundary, source_scale=scale, source_segment_id=candidate.source_segment_id, available_at=candidate.available_at, provenance=dict(candidate.provenance))

def pre_bar_view(observer_open_time: int, snapshots: list[CausalBoundarySnapshot]) -> PreBarBoundaryView:
    """UPDATE-000/002 guard: only snapshots available before bar t began."""
    eligible = [s for s in snapshots if s.available_at < observer_open_time]
    latest: dict[str, CausalBoundarySnapshot] = {}
    for s in sorted(eligible, key=lambda x: (x.available_at, x.snapshot_id)):
        latest[s.candidate_id] = s
    return PreBarBoundaryView(observer_open_time=observer_open_time, snapshots=tuple(latest.values()))

# --- ORIGINAL d3_boundary_intelligence/geometry.py ---
from fractions import Fraction

def _sign(direction: TrendDirection) -> int:
    if direction is TrendDirection.LONG:
        return 1
    if direction is TrendDirection.SHORT:
        return -1
    raise ValueError('B3 geometry requires active LONG/SHORT target Trend')

def _classify_values(*, bar: OHLCBar, information_cutoff: int, reference_id: str, direction: TrendDirection, boundary: Fraction, scale: Fraction, params: FrozenD3Parameters) -> B3Geometry:
    s = _sign(direction)
    if scale <= 0:
        raise ValueError('source scale must be positive')
    d_close = Fraction(s) * (bar.close - boundary) / scale
    if direction is TrendDirection.LONG:
        d_range = (bar.low - boundary) / scale
    else:
        d_range = (boundary - bar.high) / scale
    test = d_range <= params.theta_test
    approach = params.theta_test < d_range <= params.theta_approach
    separated = d_close >= params.theta_separation
    hysteresis = d_range > params.theta_approach and d_close < params.theta_separation
    return B3Geometry(information_cutoff=information_cutoff, snapshot_id=reference_id, d_close=d_close, d_range_nearest=d_range, test=test, approach=approach, separated=separated, hysteresis_intermediate=hysteresis, wrong_side_range_penetration=d_range < 0, wrong_side_close=d_close < 0, material_wrong_side_separation=d_close <= -params.theta_accept)

def classify_geometry(*, bar: OHLCBar, information_cutoff: int, snapshot: CausalBoundarySnapshot, params: FrozenD3Parameters) -> B3Geometry:
    """Exact adopted post-RC1 B3 zone classifier.

    TEST/APPROACH are mutually exclusive range predicates. SEPARATED is an
    independent close predicate and may coexist with TEST.
    """
    return _classify_values(bar=bar, information_cutoff=information_cutoff, reference_id=snapshot.snapshot_id, direction=snapshot.target_direction, boundary=snapshot.boundary, scale=snapshot.source_scale, params=params)

def classify_event_reference_geometry(*, bar: OHLCBar, information_cutoff: int, event, params: FrozenD3Parameters) -> B3Geometry:
    """Classify active B3/B4 event against frozen reference, never Anchor drift."""
    if event.event_reference_boundary is None or event.event_reference_scale is None:
        raise ValueError('event has no frozen reference')
    return _classify_values(bar=bar, information_cutoff=information_cutoff, reference_id=f'EVENT_REFERENCE:{event.event_id}', direction=event.target_direction, boundary=event.event_reference_boundary, scale=event.event_reference_scale, params=params)

def qualify_price_driven_return(*, adverse_raw_movement: Fraction, source_scale: Fraction, params: FrozenD3Parameters, provenance: dict[str, str] | None=None) -> PriceDrivenReturnEvidence:
    """F3 return threshold only; caller must provide actual raw-price movement.

    RC1 freezes the required magnitude but not an extra theta_return. This helper
    does not invent a return-origin convention; raw movement + provenance must
    come from the caller's causal price path.
    """
    if adverse_raw_movement < 0 or source_scale <= 0:
        raise ValueError('invalid adverse movement/source scale')
    minimum = (params.theta_separation - params.theta_approach) * source_scale
    return PriceDrivenReturnEvidence(passed=adverse_raw_movement >= minimum, adverse_raw_movement=adverse_raw_movement, minimum_required=minimum, provenance=dict(provenance or {}))

# --- ORIGINAL d3_boundary_intelligence/interaction.py ---
from dataclasses import replace

def initial_watch(candidate_id: str, target_trend_episode_id: str, target_direction) -> InteractionEvent:
    return InteractionEvent(event_id=deterministic_id('D3-WATCH', candidate_id, target_trend_episode_id), candidate_id=candidate_id, anchor_episode_id=None, target_trend_episode_id=target_trend_episode_id, target_direction=target_direction, control=InteractionControl.UNARMED, resolution=InteractionResolution.UNRESOLVED, event_reference_boundary=None, event_reference_scale=None, started_at=None, resolved_at=None, armed_at=None, approach_lineage_started_at=None, attempted_wrong_side_acceptance=False, material_wrong_side_separation_observed=False, reclaim_observed=False, break_state=BreakState.NONE, terminal=False, provenance={})

def apply_geometry(event: InteractionEvent, *, geometry: B3Geometry, snapshot: CausalBoundarySnapshot, return_evidence: PriceDrivenReturnEvidence | None) -> InteractionEvent:
    """B3 event-control skeleton preserving no-same-cutoff re-open semantics."""
    if event.terminal or event.control is InteractionControl.RESOLVED:
        return event
    cutoff = geometry.information_cutoff
    if event.control is InteractionControl.UNARMED:
        if geometry.separated:
            return replace(event, control=InteractionControl.ARMED, armed_at=cutoff)
        return event
    if event.control is InteractionControl.ARMED:
        return_ok = return_evidence is not None and return_evidence.passed
        if return_ok and geometry.approach and (event.approach_lineage_started_at is None):
            return replace(event, approach_lineage_started_at=cutoff)
        if return_ok and geometry.test:
            return replace(event, event_id=deterministic_id('D3-INTERACTION', event.candidate_id, str(cutoff), snapshot.snapshot_id), control=InteractionControl.INTERACTION_ACTIVE, started_at=cutoff, approach_lineage_started_at=event.approach_lineage_started_at or cutoff, event_reference_boundary=snapshot.boundary, event_reference_scale=snapshot.source_scale, provenance={'snapshot_id': snapshot.snapshot_id})
        return event
    if geometry.separated and event.break_state not in (BreakState.TEMPORARY_BREAK, BreakState.RECLAIMING) and (not event.attempted_wrong_side_acceptance):
        return replace(event, control=InteractionControl.RESOLVED, resolution=InteractionResolution.RESOLVED_CORRECT_SIDE, resolved_at=cutoff)
    return event

def abort_approach(event: InteractionEvent, *, cutoff: int) -> InteractionEvent:
    if event.control is not InteractionControl.ARMED or event.approach_lineage_started_at is None:
        return event
    return replace(event, control=InteractionControl.RESOLVED, resolution=InteractionResolution.ABORTED_APPROACH, resolved_at=cutoff)

def break_continuity(event: InteractionEvent, *, cutoff: int) -> InteractionEvent:
    if event.control not in (InteractionControl.ARMED, InteractionControl.INTERACTION_ACTIVE):
        return event
    return replace(event, control=InteractionControl.RESOLVED, resolution=InteractionResolution.UNKNOWN_CONTINUITY, resolved_at=cutoff)

def rearm_after_resolution(event: InteractionEvent, *, geometry: B3Geometry) -> InteractionEvent:
    """Start a new independent armed cycle only after a later material re-separation."""
    if event.control is not InteractionControl.RESOLVED:
        return event
    if event.resolved_at is None or geometry.information_cutoff <= event.resolved_at:
        return event
    if not geometry.separated:
        return event
    return InteractionEvent(event_id=deterministic_id('D3-WATCH-REARM', event.candidate_id, event.event_id, str(geometry.information_cutoff)), candidate_id=event.candidate_id, anchor_episode_id=None, target_trend_episode_id=event.target_trend_episode_id, target_direction=event.target_direction, control=InteractionControl.ARMED, resolution=InteractionResolution.UNRESOLVED, event_reference_boundary=None, event_reference_scale=None, started_at=None, resolved_at=None, armed_at=geometry.information_cutoff, approach_lineage_started_at=None, attempted_wrong_side_acceptance=False, material_wrong_side_separation_observed=False, reclaim_observed=False, break_state=BreakState.NONE, terminal=False, provenance={'prior_event_id': event.event_id, 'rearm': 'MATERIAL_CORRECT_SIDE_SEPARATION'})

# --- ORIGINAL d3_boundary_intelligence/breaks.py ---
from dataclasses import replace

def evaluate_break(event: InteractionEvent, *, geometry: B3Geometry, structural_acceptance: StructuralAcceptanceEvidence | None=None, correct_side_recovery: CorrectSideRecoveryEvidence | None=None) -> BreakEvaluation:
    """B4 consumes frozen B3 event reference + D2 confirmed structure evidence."""
    if event.terminal:
        return BreakEvaluation(event.break_state, True, event.resolution, event.attempted_wrong_side_acceptance, event.material_wrong_side_separation_observed, event.reclaim_observed, 'event already terminal')
    if event.control is not InteractionControl.INTERACTION_ACTIVE or event.event_reference_boundary is None:
        if geometry.wrong_side_range_penetration or geometry.wrong_side_close:
            return BreakEvaluation(BreakState.WRONG_SIDE_UNARMED, False, InteractionResolution.UNRESOLVED, False, False, False, 'A5: wrong side without active armed lineage')
        return BreakEvaluation(BreakState.NONE, False, InteractionResolution.UNRESOLVED, False, False, False, 'no active interaction')
    attempted = event.attempted_wrong_side_acceptance or geometry.wrong_side_close
    material = event.material_wrong_side_separation_observed or geometry.material_wrong_side_separation
    reclaim = event.reclaim_observed
    if geometry.wrong_side_range_penetration and (not geometry.wrong_side_close):
        state = BreakState.PROBE
    elif geometry.wrong_side_close:
        state = BreakState.TEMPORARY_BREAK
    else:
        state = event.break_state if event.break_state in (BreakState.TEMPORARY_BREAK, BreakState.RECLAIMING, BreakState.PROBE) else BreakState.NONE
    sa = structural_acceptance or StructuralAcceptanceEvidence()
    if material and (sa.continuation_acceptance or sa.failed_return_acceptance):
        return BreakEvaluation(BreakState.TRUE_BREAK, True, InteractionResolution.RESOLVED_WRONG_SIDE, attempted, True, reclaim, 'material wrong-side separation + completed wrong-side structural acceptance')
    had_temp = event.break_state in (BreakState.TEMPORARY_BREAK, BreakState.RECLAIMING) or attempted
    if had_temp and (not geometry.wrong_side_close):
        reclaim = True
        state = BreakState.RECLAIMING
    cr = correct_side_recovery or CorrectSideRecoveryEvidence()
    if attempted and reclaim and cr.turning_structure_confirmed and cr.material_correct_side_structural_recovery:
        return BreakEvaluation(BreakState.FALSE_BREAK, True, InteractionResolution.RESOLVED_CORRECT_SIDE, True, material, True, 'attempted acceptance + reclaim + confirmed turning structure + material correct-side recovery')
    return BreakEvaluation(state, False, InteractionResolution.UNRESOLVED, attempted, material, reclaim, 'non-terminal B4 state')

def apply_break_evaluation(event: InteractionEvent, evaluation: BreakEvaluation, *, cutoff: int) -> InteractionEvent:
    updated = replace(event, attempted_wrong_side_acceptance=evaluation.attempted_wrong_side_acceptance, material_wrong_side_separation_observed=evaluation.material_wrong_side_separation_observed, reclaim_observed=evaluation.reclaim_observed, break_state=evaluation.break_state, terminal=evaluation.terminal)
    if evaluation.terminal:
        updated = replace(updated, control=InteractionControl.RESOLVED, resolution=evaluation.resolution, resolved_at=cutoff)
    return updated

# --- ORIGINAL d3_boundary_intelligence/anchors.py ---
from dataclasses import replace

def empty_dossier() -> AnchorEvidenceDossier:
    return AnchorEvidenceDossier(boundary_side_integrity=InfoValue.unknown(), structural_integrity=InfoValue.unknown(), slope_alignment=InfoValue.unknown(), independent_retest_evidence=InfoValue.none(), retest_quality=InfoValue.na(), current_relevance=InfoValue.unknown(), true_break_evidence=InfoValue.none(), data_confidence=InfoValue.unknown())

def maybe_start_anchor_episode(candidate: MathematicalBoundaryCandidate, event: InteractionEvent, *, target_trend_active: bool, candidate_terminally_invalidated: bool, cutoff: int) -> AnchorEpisode | None:
    """F1 starts PROVISIONAL only on qualifying armed Approach/Test lineage."""
    if candidate.availability is not CandidateAvailability.AVAILABLE or not target_trend_active or candidate_terminally_invalidated:
        return None
    lineage_started = event.approach_lineage_started_at is not None or event.control is InteractionControl.INTERACTION_ACTIVE
    if not lineage_started:
        return None
    aid = deterministic_id('D3-ANCHOR-EP', candidate.candidate_id, candidate.target_trend_episode_id, str(cutoff))
    return AnchorEpisode(anchor_episode_id=aid, candidate_id=candidate.candidate_id, target_trend_episode_id=candidate.target_trend_episode_id, target_direction=candidate.target_direction, validity=AnchorValidity.PROVISIONAL, activity=AnchorActivity.ACTIVE, started_at=cutoff, ended_at=None, interaction_event_ids=(event.event_id,), qualified_uses=(), terminal_true_break=False, dossier=empty_dossier(), provenance={'candidate_family': candidate.family.value})

def attach_interaction(episode: AnchorEpisode, event: InteractionEvent) -> AnchorEpisode:
    ids = episode.interaction_event_ids
    if event.event_id not in ids:
        ids = ids + (event.event_id,)
    activity = AnchorActivity.PRESSURED if event.control is InteractionControl.INTERACTION_ACTIVE else episode.activity
    return replace(episode, interaction_event_ids=ids, activity=activity)

def add_qualified_boundary_use(episode: AnchorEpisode, use: QualifiedBoundaryUse) -> AnchorEpisode:
    if use.anchor_episode_id != episode.anchor_episode_id:
        raise ValueError('QBU belongs to another Anchor Episode')
    if use.negotiation_event_id not in episode.interaction_event_ids:
        raise ValueError('QBU requires causal interaction lineage in this episode')
    return replace(episode, validity=AnchorValidity.VALID, activity=AnchorActivity.ACTIVE, qualified_uses=episode.qualified_uses + (use,), dossier=replace(episode.dossier, independent_retest_evidence=InfoValue.known('QUALIFIED_BOUNDARY_USE')))

def terminate_for_true_break(episode: AnchorEpisode, *, cutoff: int) -> AnchorEpisode:
    return replace(episode, validity=AnchorValidity.TERMINATED, activity=AnchorActivity.TERMINATED, ended_at=cutoff, terminal_true_break=True, dossier=replace(episode.dossier, true_break_evidence=InfoValue.known(BreakState.TRUE_BREAK.value)))

def recover_from_pressure(episode: AnchorEpisode, event: InteractionEvent) -> AnchorEpisode:
    if episode.validity is AnchorValidity.VALID and event.resolution is InteractionResolution.RESOLVED_CORRECT_SIDE:
        return replace(episode, activity=AnchorActivity.ACTIVE)
    return episode

def terminate_episode(episode: AnchorEpisode, *, cutoff: int, reason: str) -> AnchorEpisode:
    return replace(episode, validity=AnchorValidity.TERMINATED, activity=AnchorActivity.TERMINATED, ended_at=cutoff, provenance={**dict(episode.provenance), 'termination_reason': reason})

def bind_event_to_episode(event: InteractionEvent, episode: AnchorEpisode) -> InteractionEvent:
    if event.candidate_id != episode.candidate_id:
        raise ValueError('event/candidate mismatch')
    return replace(event, anchor_episode_id=episode.anchor_episode_id)

def make_qualified_boundary_use(episode: AnchorEpisode, event: InteractionEvent, progress: TrendSideMinorProgressEvidence) -> QualifiedBoundaryUse:
    if event.anchor_episode_id != episode.anchor_episode_id:
        raise ValueError('event is not attached to this Anchor Episode')
    if event.resolution is not InteractionResolution.RESOLVED_CORRECT_SIDE:
        raise ValueError('Qualified Boundary Use requires correct-side resolved negotiation')
    if event.break_state is BreakState.TRUE_BREAK:
        raise ValueError('True Break cannot qualify as correct-side boundary use')
    if not progress.material_progress or progress.timeframe_ms != 15 * 60 * 1000 or progress.layer != 'MINOR':
        raise ValueError('Qualified Boundary Use requires subsequent material trend-side 15M Minor progress')
    if progress.confirmed_at <= (event.resolved_at or -1):
        raise ValueError('trend-side progress must be subsequent to correct-side resolution')
    return QualifiedBoundaryUse(use_id=deterministic_id('D3-QBU', episode.anchor_episode_id, event.event_id, progress.pivot_id), anchor_episode_id=episode.anchor_episode_id, negotiation_event_id=event.event_id, correct_side_resolution_cutoff=event.resolved_at or 0, trend_side_minor_progress_pivot_id=progress.pivot_id, progress_confirmed_at=progress.confirmed_at)

# --- ORIGINAL d3_boundary_intelligence/clusters_roles.py ---
from fractions import Fraction

def cluster_units(zones: list[BoundaryContactZone]) -> tuple[EconomicBoundaryUnit, ...]:
    """Connected components over already-authoritative causal B3 contact zones.

    No new distance threshold or synthetic cluster center is created.
    """
    if not zones:
        return ()
    remaining = sorted(zones, key=lambda z: (z.lower, z.upper, z.anchor_episode_id))
    components: list[list[BoundaryContactZone]] = []
    current: list[BoundaryContactZone] = [remaining[0]]
    current_upper = remaining[0].upper
    for z in remaining[1:]:
        if z.lower <= current_upper:
            current.append(z)
            if z.upper > current_upper:
                current_upper = z.upper
        else:
            components.append(current)
            current = [z]
            current_upper = z.upper
    components.append(current)
    units: list[EconomicBoundaryUnit] = []
    for comp in components:
        members = tuple(sorted({z.anchor_episode_id for z in comp}))
        unit_id = deterministic_id('D3-EBU', *members, str(max((z.information_cutoff for z in comp))))
        units.append(EconomicBoundaryUnit(unit_id=unit_id, anchor_episode_ids=members, contact_zones=tuple(comp), is_cluster=len(members) > 1, provenance={'geometry': 'CONNECTED_CAUSAL_B3_CONTACT_ZONES_NO_SYNTHETIC_LINE'}))
    return tuple(units)

def unit_intersects_corridor(unit: EconomicBoundaryUnit, corridor: StructuralCorridor | None) -> bool:
    if corridor is None:
        return False
    return any((z.intersects(corridor.lower, corridor.upper) for z in unit.contact_zones))

def unit_intersects_protected_zone(unit: EconomicBoundaryUnit, *, protected_price: Fraction, protected_scale: Fraction, theta_progress: Fraction) -> bool:
    lower = protected_price - theta_progress * protected_scale
    upper = protected_price + theta_progress * protected_scale
    return any((z.intersects(lower, upper) for z in unit.contact_zones))

def current_relevance(unit: EconomicBoundaryUnit, *, corridor: StructuralCorridor | None, has_actual_market_use: bool, active_qualifying_interaction: bool) -> bool:
    return unit_intersects_corridor(unit, corridor) and (has_actual_market_use or active_qualifying_interaction)

def assign_roles(evidence: list[BoundaryUnitRoleEvidence], *, structural_suitable_unit_ids: set[str], prior_primary_unit_id: str | None=None, old_episode_ended: bool=False, takeover_depth_relation: StructuralDepthRelation=StructuralDepthRelation.UNRESOLVED, next_deeper_unit_id: str | None=None) -> RoleAssignment:
    """Event-driven role selection without score/family/distance tie-breaking.

    PRIMARY uses most-recent Qualified Boundary Use. Same-cutoff ambiguity is
    UNRESOLVED. SECONDARY requires an explicit DEEPER structural relation to the
    chosen primary; if several equally admissible units remain, it is UNRESOLVED.
    """
    eligible = [e for e in evidence if e.at_least_one_valid_member and e.current_relevant and (e.latest_qualified_use_cutoff is not None) and (not e.terminal_true_break) and (not e.unresolved_conflict)]
    if not eligible:
        return RoleAssignment(None, None, tuple(sorted(structural_suitable_unit_ids)), RoleTransition.NONE, None)
    latest = max((e.latest_qualified_use_cutoff for e in eligible if e.latest_qualified_use_cutoff is not None))
    primaries = [e for e in eligible if e.latest_qualified_use_cutoff == latest]
    if len(primaries) != 1:
        return RoleAssignment(None, None, tuple(sorted(structural_suitable_unit_ids)), RoleTransition.UNRESOLVED, 'multiple independent units satisfy Primary at same cutoff')
    primary = primaries[0]
    deeper = [e for e in eligible if e.unit.unit_id != primary.unit.unit_id and e.structural_depth_relation_to_primary is StructuralDepthRelation.DEEPER]
    secondary_id: str | None = None
    unresolved: str | None = None
    if deeper:
        if len(deeper) == 1:
            chosen = deeper[0]
        elif next_deeper_unit_id is not None:
            matches = [e for e in deeper if e.unit.unit_id == next_deeper_unit_id]
            chosen = matches[0] if len(matches) == 1 else None
        else:
            chosen = None
        if chosen is None:
            unresolved = 'next-deeper Secondary relation not uniquely established by supplied Price Structure context'
        elif set(chosen.unit.anchor_episode_ids).isdisjoint(primary.unit.anchor_episode_ids):
            secondary_id = chosen.unit.unit_id
    if unresolved is not None:
        transition = RoleTransition.UNRESOLVED
    elif prior_primary_unit_id is None or prior_primary_unit_id == primary.unit.unit_id:
        transition = RoleTransition.NONE
    elif old_episode_ended:
        transition = RoleTransition.REPLACEMENT
    elif takeover_depth_relation is StructuralDepthRelation.DEEPER:
        transition = RoleTransition.PROMOTION
    elif takeover_depth_relation is StructuralDepthRelation.SAME_LAYER:
        transition = RoleTransition.HANDOFF
    else:
        transition = RoleTransition.UNRESOLVED
        unresolved = 'takeover depth relation unresolved'
    return RoleAssignment(primary_unit_id=primary.unit.unit_id, secondary_unit_id=secondary_id, structural_unit_ids=tuple(sorted(structural_suitable_unit_ids)), transition=transition, unresolved_reason=unresolved)

def structural_role_eligible(evidence: BoundaryUnitRoleEvidence, *, protected_price: Fraction, protected_scale: Fraction, theta_progress: Fraction) -> bool:
    """A3/F1/B5 Structural-role gate; role multiplicity remains allowed."""
    return evidence.at_least_one_valid_member and evidence.current_relevant and (evidence.latest_qualified_use_cutoff is not None) and (not evidence.terminal_true_break) and (not evidence.unresolved_conflict) and unit_intersects_protected_zone(evidence.unit, protected_price=protected_price, protected_scale=protected_scale, theta_progress=theta_progress)

# --- ORIGINAL d3_boundary_intelligence/cutoff_contract.py ---
"""D3-owned slices of RC1 F9 global update order only."""
D3_UPDATE_ORDER = ('UPDATE-002_CAPTURE_BAR_T_BOUNDARY_GEOMETRY_FROM_PRE_BAR_SNAPSHOTS', 'UPDATE-007_RESOLVE_UPGRADE_INTERACTION_BREAK_USING_UPDATE002_PLUS_UPDATE005_STRUCTURE', 'UPDATE-008_UPDATE_ANCHOR_CANDIDATE_VALIDITY_CLUSTER_ROLES_FOR_FUTURE_BARS')
FORBIDDEN_D3_WRITES = ('MarketTrend', 'PriceStructure', 'ENTRY_READY', 'RiskFeasibility', 'RiskAnchor', 'Position', 'Exit', 'Execution')
CUTOFF_FIREWALL = {'bar_t_geometry_uses_only_pre_bar_snapshot': True, 'new_bar_t_ema_st_not_back_applied_to_bar_t_high_low': True, 'new_anchor_values_at_t_eligible_only_for_future_observer_bars': True, 'same_bar_resolve_rearm_cannot_open_next_event': True}

# --- ORIGINAL d3_reference.py ---
"""WP3 non-trading D3 reference skeleton.

This orchestrates only D3-owned RC1 slices. It never writes D2 Trend/Price
Structure, D4 Entry, D5 Risk, or D6 Position/Execution truth.
"""
from dataclasses import replace

class D3ReferenceSkeleton:

    def __init__(self, params: FrozenD3Parameters) -> None:
        self.params = params
        self._snapshots: list[CausalBoundarySnapshot] = []
        self._events: dict[str, InteractionEvent] = {}
        self._episodes: dict[str, AnchorEpisode] = {}

    @classmethod
    def from_parameter_snapshot(cls, snapshot: ParameterSnapshot) -> 'D3ReferenceSkeleton':
        return cls(frozen_d3_parameters(snapshot))

    def update_008_register_candidate(self, candidate: MathematicalBoundaryCandidate) -> CausalBoundarySnapshot | None:
        episode = self._episodes.get(candidate.candidate_id)
        snap = snapshot_from_candidate(candidate, anchor_episode_id=episode.anchor_episode_id if episode else None)
        if snap is not None:
            self._snapshots.append(snap)
        if candidate.candidate_id not in self._events:
            self._events[candidate.candidate_id] = initial_watch(candidate.candidate_id, candidate.target_trend_episode_id, candidate.target_direction)
        return snap

    def update_000_pre_bar_view(self, observer_open_time: int) -> PreBarBoundaryView:
        return pre_bar_view(observer_open_time, self._snapshots)

    def update_002_capture_geometry(self, *, bar: OHLCBar, information_cutoff: int, snapshot: CausalBoundarySnapshot) -> B3Geometry:
        event = self._events[snapshot.candidate_id]
        if event.control is InteractionControl.INTERACTION_ACTIVE and event.event_reference_boundary is not None:
            return classify_event_reference_geometry(bar=bar, information_cutoff=information_cutoff, event=event, params=self.params)
        return classify_geometry(bar=bar, information_cutoff=information_cutoff, snapshot=snapshot, params=self.params)

    def update_007_interaction_break(self, *, snapshot: CausalBoundarySnapshot, geometry: B3Geometry, return_evidence: PriceDrivenReturnEvidence | None, structural_acceptance: StructuralAcceptanceEvidence | None=None, correct_side_recovery: CorrectSideRecoveryEvidence | None=None) -> InteractionEvent:
        event = self._events[snapshot.candidate_id]
        if event.control is InteractionControl.RESOLVED:
            event = rearm_after_resolution(event, geometry=geometry)
            self._events[snapshot.candidate_id] = event
            if event.control is InteractionControl.ARMED:
                return event
        event = apply_geometry(event, geometry=geometry, snapshot=snapshot, return_evidence=return_evidence)
        evaluation = evaluate_break(event, geometry=geometry, structural_acceptance=structural_acceptance, correct_side_recovery=correct_side_recovery)
        event = apply_break_evaluation(event, evaluation, cutoff=geometry.information_cutoff)
        if not event.terminal:
            event = apply_geometry(event, geometry=geometry, snapshot=snapshot, return_evidence=return_evidence)
        self._events[snapshot.candidate_id] = event
        episode = self._episodes.get(snapshot.candidate_id)
        if episode is not None:
            episode = attach_interaction(episode, event)
            if event.break_state is BreakState.TRUE_BREAK and event.terminal:
                episode = terminate_for_true_break(episode, cutoff=geometry.information_cutoff)
            else:
                episode = recover_from_pressure(episode, event)
            self._episodes[snapshot.candidate_id] = episode
        return event

    def update_008_anchor_lifecycle(self, *, candidate: MathematicalBoundaryCandidate, target_trend_active: bool, candidate_terminally_invalidated: bool, cutoff: int) -> AnchorEpisode | None:
        existing = self._episodes.get(candidate.candidate_id)
        if existing is not None and existing.validity.value != 'TERMINATED':
            return existing
        event = self._events[candidate.candidate_id]
        episode = maybe_start_anchor_episode(candidate, event, target_trend_active=target_trend_active, candidate_terminally_invalidated=candidate_terminally_invalidated, cutoff=cutoff)
        if episode is not None:
            event = bind_event_to_episode(event, episode)
            self._events[candidate.candidate_id] = event
            self._episodes[candidate.candidate_id] = episode
        return episode

    def continuity_break(self, candidate_id: str, *, cutoff: int) -> InteractionEvent:
        event = break_continuity(self._events[candidate_id], cutoff=cutoff)
        self._events[candidate_id] = event
        episode = self._episodes.get(candidate_id)
        if episode is not None and episode.validity.value != 'TERMINATED':
            from .d3_boundary_intelligence.anchors import terminate_episode
            self._episodes[candidate_id] = terminate_episode(episode, cutoff=cutoff, reason='SOURCE_CONTINUITY_BREAK')
        return event

    def current_event(self, candidate_id: str) -> InteractionEvent:
        return self._events[candidate_id]

    def current_episode(self, candidate_id: str) -> AnchorEpisode | None:
        return self._episodes.get(candidate_id)

# --- ORIGINAL d4_opportunity/types.py ---
from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction
from typing import Mapping

class OpportunityLifecycle(str, Enum):
    """WP4-owned lifecycle subset only.

    ENTRY_READY / EXECUTED deliberately do not exist in this WP4 enum because
    B7-B and execution are outside the authorized stage.
    """
    CANDIDATE = 'CANDIDATE'
    SETUP_ACTIVE = 'SETUP_ACTIVE'
    WAIT_CONFIRMATION = 'WAIT_CONFIRMATION'
    INVALIDATED = 'INVALIDATED'
    EXPIRED = 'EXPIRED'

class OpportunityMechanism(str, Enum):
    NORMAL_RETEST_CONTINUATION = 'NORMAL_RETEST_CONTINUATION'
    FALSE_BREAK_RECLAIM = 'FALSE_BREAK_RECLAIM'
    PLATFORM_REEXPANSION = 'PLATFORM_REEXPANSION'
    DEEP_STRUCTURE_TAKEOVER = 'DEEP_STRUCTURE_TAKEOVER'
    TREND_ESTABLISHMENT_WATCH_ONLY = 'TREND_ESTABLISHMENT_WATCH_ONLY'

class GateName(str, Enum):
    MARKET_ELIGIBILITY = 'MARKET_ELIGIBILITY'
    LOCATION_ELIGIBILITY = 'LOCATION_ELIGIBILITY'
    BEHAVIOR_CONFIRMATION = 'BEHAVIOR_CONFIRMATION'

@dataclass(frozen=True)
class GateEvaluation:
    gate: GateName
    result: InfoValue[bool]
    reason: str

@dataclass(frozen=True)
class EntryBoundaryView:
    unit_id: str
    member_anchor_episode_ids: tuple[str, ...]
    valid_active: bool
    target_trend_episode_id: str
    target_direction: TrendDirection
    provenance: Mapping[str, str] = field(default_factory=dict)

@dataclass(frozen=True)
class LocalTrendControlRegainEvidence:
    """Causal D2 evidence interface consumed by D4.

    RC1 defines the semantic sequence but does not introduce another numeric
    threshold for the final material closed-price recovery. WP4 therefore does
    not invent one. The two semantic predicates below must be supplied from
    already-authoritative D2 price-structure evidence/provenance.
    """
    direction: TrendDirection
    adverse_reference_pivot_id: str
    adverse_reference_confirmed_at: int
    recovery_pivot_id: str
    recovery_pivot_confirmed_at: int
    countertrend_progression_failed: InfoValue[bool]
    material_original_direction_closed_price_recovery: InfoValue[bool]
    confirmation_cutoff: int
    provenance: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.direction not in (TrendDirection.LONG, TrendDirection.SHORT):
            raise ValueError('Local Trend-Control Regain requires LONG/SHORT')
        if not self.adverse_reference_pivot_id or not self.recovery_pivot_id:
            raise ValueError('Local Trend-Control Regain requires causal pivot references')
        if self.adverse_reference_confirmed_at > self.confirmation_cutoff:
            raise ValueError('future adverse reference cannot be consumed')
        if self.recovery_pivot_confirmed_at > self.confirmation_cutoff:
            raise ValueError('future recovery pivot cannot be consumed')
        if self.recovery_pivot_confirmed_at < self.adverse_reference_confirmed_at:
            raise ValueError('recovery pivot cannot predate adverse reference confirmation')

@dataclass(frozen=True)
class MechanismObservation:
    mechanism: OpportunityMechanism
    candidate: bool
    setup_active: bool
    wait_confirmation: bool
    behavior_confirmation: InfoValue[bool]
    location_qualified: InfoValue[bool]
    setup_lineage: tuple[str, ...]
    source_event_ids: tuple[str, ...]
    watch_only: bool = False
    provenance: Mapping[str, str] = field(default_factory=dict)

    @property
    def active(self) -> bool:
        return self.candidate or self.setup_active or self.wait_confirmation or (self.behavior_confirmation.value is True)

@dataclass(frozen=True)
class OpportunityState:
    opportunity_id: str
    trend_episode_id: str
    direction: TrendDirection
    market_event_id: str
    lifecycle: OpportunityLifecycle
    mechanism_history: tuple[OpportunityMechanism, ...]
    primary_mechanism: OpportunityMechanism
    entry_boundary_unit_id: str | None
    entry_boundary_member_anchor_episode_ids: tuple[str, ...]
    created_at: int
    updated_at: int
    setup_lineage: tuple[str, ...]
    detector_evidence_ids: tuple[str, ...]
    confirmation_candidate_ids: tuple[str, ...] = ()
    confirmation_mechanism_history: tuple[OpportunityMechanism, ...] = ()
    terminated_at: int | None = None
    termination_reason: str | None = None
    provenance: Mapping[str, str] = field(default_factory=dict)

    @property
    def terminal(self) -> bool:
        return self.lifecycle in (OpportunityLifecycle.INVALIDATED, OpportunityLifecycle.EXPIRED)

@dataclass(frozen=True)
class BehaviorConfirmationCandidate:
    """B7-A pre-risk confirmation candidate only; never ENTRY_READY."""
    candidate_id: str
    opportunity_id: str
    trend_episode_id: str
    direction: TrendDirection
    market_event_id: str
    mechanism: OpportunityMechanism
    setup_lineage: tuple[str, ...]
    entry_boundary_unit_id: str | None
    entry_boundary_member_anchor_episode_ids: tuple[str, ...]
    behavior_confirmation: InfoValue[bool]
    confirmation_cutoff: int
    source_event_ids: tuple[str, ...]
    same_cutoff_only: bool = True
    provenance: Mapping[str, str] = field(default_factory=dict)

@dataclass(frozen=True)
class OpportunityIndependenceEvidence:
    previous_opportunity_terminated: bool
    material_trend_side_reseparation_or_control: bool
    new_independent_countertrend_or_boundary_return_event: bool
    provenance: Mapping[str, str] = field(default_factory=dict)

@dataclass(frozen=True)
class OpportunityTerminationEvidence:
    trend_episode_ended: bool = False
    entry_boundary_terminal_true_break_without_false_break_recovery: bool = False
    mechanism_required_structure_materially_failed: bool = False
    critical_role_or_structure_replaced_destroying_thesis: bool = False
    irrecoverable_continuity_end: bool = False
    event_cycle_completed_and_new_independent_event_rearmed: bool = False
    downstream_actionable_entry_absent: InfoValue[bool] = field(default_factory=InfoValue.unknown)
    other_same_cutoff_non_thesis_gate_failed_after_confirmation: bool = False
    independent_open_mechanism_after_consumed_confirmation: bool = False
    provenance: Mapping[str, str] = field(default_factory=dict)

@dataclass(frozen=True)
class D4CutoffView:
    information_cutoff: int
    opportunity: OpportunityState | None
    primary_observation: MechanismObservation | None
    market_eligibility: GateEvaluation
    location_eligibility: GateEvaluation
    behavior_confirmation: GateEvaluation
    confirmation_candidate: BehaviorConfirmationCandidate | None
    update_step: str = 'UPDATE-011'

# --- ORIGINAL d4_opportunity/parameters.py ---
from dataclasses import dataclass
from fractions import Fraction

@dataclass(frozen=True)
class FrozenD4Parameters:
    theta_progress: Fraction

    def __post_init__(self) -> None:
        if self.theta_progress < 0:
            raise ValueError('theta_progress must be nonnegative')

def frozen_d4_parameters(snapshot: ParameterSnapshot) -> FrozenD4Parameters:
    slot = snapshot.slot('theta_progress')
    if slot.state is not ParameterState.FROZEN or slot.exact_value is None:
        raise ValueError('theta_progress must be FROZEN with exact value for WP4')
    return FrozenD4Parameters(theta_progress=Fraction(slot.exact_value))

# --- ORIGINAL d4_opportunity/control_regain.py ---
def evaluate_local_trend_control_regain(evidence: LocalTrendControlRegainEvidence) -> InfoValue[bool]:
    """Combine the two RC1 D2 structural predicates without inventing a new threshold."""
    left = evidence.countertrend_progression_failed
    right = evidence.material_original_direction_closed_price_recovery
    if left.kind is InfoKind.ERROR:
        return InfoValue.error(left.error_ref or 'LOCAL_CONTROL_COUNTERTREND_ERROR')
    if right.kind is InfoKind.ERROR:
        return InfoValue.error(right.error_ref or 'LOCAL_CONTROL_RECOVERY_ERROR')
    if left.kind is InfoKind.UNKNOWN or right.kind is InfoKind.UNKNOWN:
        return InfoValue.unknown()
    if left.kind is InfoKind.NA or right.kind is InfoKind.NA:
        return InfoValue.na()
    if left.kind is InfoKind.NONE or right.kind is InfoKind.NONE:
        return InfoValue.none()
    return InfoValue.known(bool(left.value and right.value))

# --- ORIGINAL d4_opportunity/eligibility.py ---
from collections.abc import Mapping

def _propagate_nonknown_bool(value: InfoValue[bool]) -> InfoValue[bool]:
    if value.kind is InfoKind.ERROR:
        return InfoValue.error(value.error_ref or 'D4_GATE_INPUT_ERROR')
    if value.kind is InfoKind.UNKNOWN:
        return InfoValue.unknown()
    if value.kind is InfoKind.NA:
        return InfoValue.na()
    if value.kind is InfoKind.NONE:
        return InfoValue.none()
    return value

def market_eligibility(trend: TrendEpisodeState, *, opportunity_direction: TrendDirection, critical_information_known: InfoValue[bool], watch_only: bool=False) -> GateEvaluation:
    if watch_only:
        return GateEvaluation(GateName.MARKET_ELIGIBILITY, InfoValue.na(), 'TREND_ESTABLISHMENT_WATCH_ONLY')
    info = _propagate_nonknown_bool(critical_information_known)
    if info.kind is not InfoKind.KNOWN:
        return GateEvaluation(GateName.MARKET_ELIGIBILITY, info, 'CRITICAL_INFORMATION_NOT_KNOWN')
    if info.value is not True:
        return GateEvaluation(GateName.MARKET_ELIGIBILITY, InfoValue.known(False), 'CRITICAL_INFORMATION_BLOCK')
    if trend.direction not in (TrendDirection.LONG, TrendDirection.SHORT) or trend.episode_id is None:
        return GateEvaluation(GateName.MARKET_ELIGIBILITY, InfoValue.known(False), 'NO_ACTIVE_TREND_EPISODE')
    if trend.direction is not opportunity_direction:
        return GateEvaluation(GateName.MARKET_ELIGIBILITY, InfoValue.known(False), 'TREND_DIRECTION_MISMATCH')
    if trend.integrity in (TrendIntegrity.DETERIORATING, TrendIntegrity.FAILED):
        return GateEvaluation(GateName.MARKET_ELIGIBILITY, InfoValue.known(False), f'TREND_INTEGRITY_{trend.integrity.value}')
    if trend.integrity in (TrendIntegrity.HEALTHY, TrendIntegrity.PRESSURED):
        return GateEvaluation(GateName.MARKET_ELIGIBILITY, InfoValue.known(True), 'ACTIVE_MATCHING_TREND_ELIGIBLE')
    return GateEvaluation(GateName.MARKET_ELIGIBILITY, InfoValue.unknown(), 'TREND_INTEGRITY_UNKNOWN')

def location_eligibility(trend_position: TrendPositionResult, *, mechanism_location_qualified: InfoValue[bool], watch_only: bool=False) -> GateEvaluation:
    if watch_only:
        return GateEvaluation(GateName.LOCATION_ELIGIBILITY, InfoValue.na(), 'TREND_ESTABLISHMENT_WATCH_ONLY')
    if trend_position.position is TrendPosition.OVEREXTENDED:
        return GateEvaluation(GateName.LOCATION_ELIGIBILITY, InfoValue.known(False), 'OVEREXTENDED')
    value = _propagate_nonknown_bool(mechanism_location_qualified)
    if value.kind is InfoKind.KNOWN:
        return GateEvaluation(GateName.LOCATION_ELIGIBILITY, value, 'MECHANISM_LOCATION_QUALIFIED' if value.value else 'MECHANISM_LOCATION_NOT_QUALIFIED')
    return GateEvaluation(GateName.LOCATION_ELIGIBILITY, value, 'MECHANISM_LOCATION_UNRESOLVED')

def entry_boundary_view(unit: EconomicBoundaryUnit | None, episodes: Mapping[str, AnchorEpisode], *, target_trend_episode_id: str, target_direction: TrendDirection, information_cutoff: int) -> EntryBoundaryView | None:
    if unit is None:
        return None
    members = tuple(unit.anchor_episode_ids)
    if any((z.information_cutoff > information_cutoff for z in unit.contact_zones)):
        raise ValueError('D4_CANNOT_CONSUME_FUTURE_BOUNDARY_UNIT_GEOMETRY')
    valid_members: list[AnchorEpisode] = []
    for aid in members:
        ep = episodes.get(aid)
        if ep is None:
            continue
        if ep.started_at > information_cutoff or (ep.ended_at is not None and ep.ended_at > information_cutoff):
            raise ValueError('D4_CANNOT_CONSUME_FUTURE_ANCHOR_EPISODE_STATE')
        if ep.target_trend_episode_id != target_trend_episode_id or ep.target_direction is not target_direction:
            continue
        if ep.validity is AnchorValidity.VALID and ep.activity in (AnchorActivity.ACTIVE, AnchorActivity.PRESSURED) and (not ep.terminal_true_break) and (ep.ended_at is None):
            valid_members.append(ep)
    return EntryBoundaryView(unit_id=unit.unit_id, member_anchor_episode_ids=members, valid_active=bool(valid_members), target_trend_episode_id=target_trend_episode_id, target_direction=target_direction, provenance={'unit_semantics': 'D3_ECONOMIC_BOUNDARY_UNIT', 'member_selection': 'NO_MEMBER_WINNER_INVENTED', 'valid_active_member_count': str(len(valid_members))})

# --- ORIGINAL d4_opportunity/mechanisms.py ---
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Mapping

@dataclass(frozen=True)
class NormalRetestEvidence:
    interaction: InteractionEvent
    qualifying_retest_or_probe: bool
    adverse_structural_reference_fixed: bool
    local_control_regain: LocalTrendControlRegainEvidence | None
    setup_lineage: tuple[str, ...]
    provenance: Mapping[str, str] = field(default_factory=dict)

@dataclass(frozen=True)
class FalseBreakReclaimEvidence:
    interaction: InteractionEvent
    setup_lineage: tuple[str, ...]
    provenance: Mapping[str, str] = field(default_factory=dict)

@dataclass(frozen=True)
class PlatformReexpansionEvidence:
    platform: PlatformState
    current_close: Fraction
    target_trend_episode_id: str
    direction: TrendDirection
    setup_lineage: tuple[str, ...]
    provenance: Mapping[str, str] = field(default_factory=dict)

@dataclass(frozen=True)
class DeepStructureTakeoverEvidence:
    shallow_operating_defense_no_longer_completes_setup: bool
    deeper_boundary_independent: bool
    deeper_interaction: InteractionEvent | None
    local_control_regain: LocalTrendControlRegainEvidence | None
    role_transition: RoleTransition
    promotion_confirmed_at: int | None
    setup_lineage: tuple[str, ...]
    provenance: Mapping[str, str] = field(default_factory=dict)

@dataclass(frozen=True)
class TrendEstablishmentWatchEvidence:
    observed: bool
    setup_lineage: tuple[str, ...]
    source_event_ids: tuple[str, ...]
    provenance: Mapping[str, str] = field(default_factory=dict)

def _market_pass(value: InfoValue[bool]) -> bool:
    return value.kind is InfoKind.KNOWN and value.value is True

def _validate_interaction_lineage(event: InteractionEvent, *, direction: TrendDirection, trend_episode_id: str, information_cutoff: int) -> None:
    if event.target_direction is not direction or event.target_trend_episode_id != trend_episode_id:
        raise ValueError('D4_INTERACTION_LINEAGE_MISMATCH')
    for value in (event.started_at, event.armed_at, event.approach_lineage_started_at, event.resolved_at):
        if value is not None and value > information_cutoff:
            raise ValueError('D4_CANNOT_CONSUME_FUTURE_INTERACTION_STATE')

def _current_or_historical_regain(evidence: LocalTrendControlRegainEvidence | None, *, direction: TrendDirection, information_cutoff: int, emit_only_if_current: bool) -> InfoValue[bool]:
    if evidence is None:
        return InfoValue.none()
    if evidence.direction is not direction:
        raise ValueError('D4_LOCAL_CONTROL_DIRECTION_MISMATCH')
    if evidence.confirmation_cutoff > information_cutoff:
        raise ValueError('D4_CANNOT_CONSUME_FUTURE_LOCAL_CONTROL_REGAIN')
    value = evaluate_local_trend_control_regain(evidence)
    if emit_only_if_current and evidence.confirmation_cutoff < information_cutoff and (value.kind is InfoKind.KNOWN) and (value.value is True):
        return InfoValue.none()
    return value

def normal_retest_observation(evidence: NormalRetestEvidence, *, direction: TrendDirection, trend_episode_id: str, information_cutoff: int, market_gate: InfoValue[bool], entry_boundary: EntryBoundaryView | None) -> MechanismObservation:
    valid_boundary = entry_boundary is not None and entry_boundary.valid_active
    event = evidence.interaction
    _validate_interaction_lineage(event, direction=direction, trend_episode_id=trend_episode_id, information_cutoff=information_cutoff)
    qualifying_lineage = event.control in (InteractionControl.ARMED, InteractionControl.INTERACTION_ACTIVE, InteractionControl.RESOLVED) and event.approach_lineage_started_at is not None and (event.break_state in (BreakState.NONE, BreakState.PROBE))
    candidate = _market_pass(market_gate) and valid_boundary and qualifying_lineage
    setup = candidate and evidence.qualifying_retest_or_probe
    regain = InfoValue.none()
    if setup and evidence.adverse_structural_reference_fixed:
        regain = _current_or_historical_regain(evidence.local_control_regain, direction=direction, information_cutoff=information_cutoff, emit_only_if_current=True)
    wait = setup and evidence.adverse_structural_reference_fixed and (not (regain.kind is InfoKind.KNOWN and regain.value is True))
    return MechanismObservation(mechanism=OpportunityMechanism.NORMAL_RETEST_CONTINUATION, candidate=candidate, setup_active=setup, wait_confirmation=wait, behavior_confirmation=regain, location_qualified=InfoValue.known(valid_boundary and setup), setup_lineage=evidence.setup_lineage, source_event_ids=(event.event_id,), provenance={**dict(evidence.provenance), 'semantic': 'RETEST_OR_PROBE_PLUS_LOCAL_CONTROL_REGAIN'})

def false_break_reclaim_observation(evidence: FalseBreakReclaimEvidence, *, direction: TrendDirection, trend_episode_id: str, information_cutoff: int, market_gate: InfoValue[bool], entry_boundary: EntryBoundaryView | None) -> MechanismObservation:
    valid_boundary = entry_boundary is not None and entry_boundary.valid_active
    _validate_interaction_lineage(evidence.interaction, direction=direction, trend_episode_id=trend_episode_id, information_cutoff=information_cutoff)
    state = evidence.interaction.break_state
    candidate_state = state in (BreakState.TEMPORARY_BREAK, BreakState.RECLAIMING, BreakState.FALSE_BREAK)
    candidate = _market_pass(market_gate) and valid_boundary and candidate_state
    setup = candidate and state in (BreakState.RECLAIMING, BreakState.FALSE_BREAK)
    confirmed = setup and state is BreakState.FALSE_BREAK and (evidence.interaction.resolved_at == information_cutoff)
    behavior = InfoValue.known(True) if confirmed else InfoValue.none()
    wait = setup and (not confirmed)
    return MechanismObservation(mechanism=OpportunityMechanism.FALSE_BREAK_RECLAIM, candidate=candidate, setup_active=setup, wait_confirmation=wait, behavior_confirmation=behavior, location_qualified=InfoValue.known(valid_boundary and setup), setup_lineage=evidence.setup_lineage, source_event_ids=(evidence.interaction.event_id,), provenance={**dict(evidence.provenance), 'semantic': 'B4_FALSE_BREAK_ONLY; PROBE_ALONE_NEVER_CONFIRMS'})

def platform_reexpansion_observation(evidence: PlatformReexpansionEvidence, *, direction: TrendDirection, trend_episode_id: str, information_cutoff: int, market_gate: InfoValue[bool], entry_boundary: EntryBoundaryView | None, theta_progress: Fraction) -> MechanismObservation:
    valid_boundary = entry_boundary is not None and entry_boundary.valid_active
    if evidence.direction is not direction or evidence.target_trend_episode_id != trend_episode_id:
        raise ValueError('D4_PLATFORM_LINEAGE_MISMATCH')
    state = evidence.platform
    if state.confirmed_at is not None and state.confirmed_at > information_cutoff:
        raise ValueError('D4_CANNOT_CONSUME_FUTURE_PLATFORM_STATE')
    candidate = _market_pass(market_gate) and state.status in (PlatformStatus.PLATFORM_CANDIDATE, PlatformStatus.PLATFORM_CONFIRMED)
    setup = candidate and state.status is PlatformStatus.PLATFORM_CONFIRMED and valid_boundary
    behavior: InfoValue[bool] = InfoValue.none()
    if setup:
        if state.platform_cap_price is None or state.platform_scale is None:
            behavior = InfoValue.error('PLATFORM_CONFIRMED_MISSING_FROZEN_CAP_OR_SCALE')
        elif direction is TrendDirection.LONG:
            behavior = InfoValue.known(evidence.current_close > state.platform_cap_price + theta_progress * state.platform_scale)
        elif direction is TrendDirection.SHORT:
            behavior = InfoValue.known(evidence.current_close < state.platform_cap_price - theta_progress * state.platform_scale)
        else:
            behavior = InfoValue.na()
    wait = setup and (not (behavior.kind is InfoKind.KNOWN and behavior.value is True))
    return MechanismObservation(mechanism=OpportunityMechanism.PLATFORM_REEXPANSION, candidate=candidate, setup_active=setup, wait_confirmation=wait, behavior_confirmation=behavior, location_qualified=InfoValue.known(valid_boundary and setup), setup_lineage=evidence.setup_lineage, source_event_ids=tuple(state.contributing_event_ids), provenance={**dict(evidence.provenance), 'semantic': 'FROZEN_PLATFORM_CAP_STRICT_ESCAPE'})

def deep_structure_takeover_observation(evidence: DeepStructureTakeoverEvidence, *, direction: TrendDirection, trend_episode_id: str, information_cutoff: int, market_gate: InfoValue[bool], entry_boundary: EntryBoundaryView | None) -> MechanismObservation:
    valid_boundary = entry_boundary is not None and entry_boundary.valid_active
    if evidence.deeper_interaction is not None:
        _validate_interaction_lineage(evidence.deeper_interaction, direction=direction, trend_episode_id=trend_episode_id, information_cutoff=information_cutoff)
    interaction_active = evidence.deeper_interaction is not None and evidence.deeper_interaction.control in (InteractionControl.ARMED, InteractionControl.INTERACTION_ACTIVE, InteractionControl.RESOLVED)
    candidate = _market_pass(market_gate) and valid_boundary and evidence.shallow_operating_defense_no_longer_completes_setup and evidence.deeper_boundary_independent
    setup = candidate and interaction_active
    regain: InfoValue[bool] = InfoValue.none()
    if setup:
        regain = _current_or_historical_regain(evidence.local_control_regain, direction=direction, information_cutoff=information_cutoff, emit_only_if_current=False)
    if evidence.promotion_confirmed_at is not None and evidence.promotion_confirmed_at > information_cutoff:
        raise ValueError('D4_CANNOT_CONSUME_FUTURE_PROMOTION')
    promotion = evidence.role_transition is RoleTransition.PROMOTION and evidence.promotion_confirmed_at is not None
    latest_required_cutoff = max(evidence.local_control_regain.confirmation_cutoff if evidence.local_control_regain is not None else -1, evidence.promotion_confirmed_at if evidence.promotion_confirmed_at is not None else -1)
    if regain.kind is InfoKind.ERROR:
        behavior = regain
    elif regain.kind is InfoKind.UNKNOWN:
        behavior = InfoValue.unknown()
    elif regain.kind is InfoKind.NA:
        behavior = InfoValue.na()
    elif regain.kind is InfoKind.NONE:
        behavior = InfoValue.none()
    else:
        passed = bool(regain.value and promotion)
        behavior = InfoValue.known(True) if passed and latest_required_cutoff == information_cutoff else InfoValue.none() if passed else InfoValue.known(False)
    wait = setup and (not (behavior.kind is InfoKind.KNOWN and behavior.value is True))
    event_ids = () if evidence.deeper_interaction is None else (evidence.deeper_interaction.event_id,)
    return MechanismObservation(mechanism=OpportunityMechanism.DEEP_STRUCTURE_TAKEOVER, candidate=candidate, setup_active=setup, wait_confirmation=wait, behavior_confirmation=behavior, location_qualified=InfoValue.known(valid_boundary and setup), setup_lineage=evidence.setup_lineage, source_event_ids=event_ids, provenance={**dict(evidence.provenance), 'semantic': 'LOCAL_CONTROL_REGAIN_AND_B5_PROMOTION'})

def trend_establishment_watch_observation(evidence: TrendEstablishmentWatchEvidence) -> MechanismObservation:
    return MechanismObservation(mechanism=OpportunityMechanism.TREND_ESTABLISHMENT_WATCH_ONLY, candidate=evidence.observed, setup_active=False, wait_confirmation=False, behavior_confirmation=InfoValue.na(), location_qualified=InfoValue.na(), setup_lineage=evidence.setup_lineage, source_event_ids=evidence.source_event_ids, watch_only=True, provenance={**dict(evidence.provenance), 'semantic': 'WATCH_ONLY_NEVER_EXECUTABLE'})
_EXECUTABLE_PRECEDENCE = (OpportunityMechanism.DEEP_STRUCTURE_TAKEOVER, OpportunityMechanism.PLATFORM_REEXPANSION, OpportunityMechanism.FALSE_BREAK_RECLAIM, OpportunityMechanism.NORMAL_RETEST_CONTINUATION)

def select_primary_observation(observations: tuple[MechanismObservation, ...]) -> MechanismObservation | None:
    active = [o for o in observations if o.active]
    if not active:
        return None
    by_mech = {o.mechanism: o for o in active}
    deep = by_mech.get(OpportunityMechanism.DEEP_STRUCTURE_TAKEOVER)
    if deep is not None and deep.setup_active:
        return deep
    if OpportunityMechanism.PLATFORM_REEXPANSION in by_mech and by_mech[OpportunityMechanism.PLATFORM_REEXPANSION].setup_active:
        return by_mech[OpportunityMechanism.PLATFORM_REEXPANSION]
    fbr = by_mech.get(OpportunityMechanism.FALSE_BREAK_RECLAIM)
    normal = by_mech.get(OpportunityMechanism.NORMAL_RETEST_CONTINUATION)
    if fbr is not None and fbr.behavior_confirmation.kind is InfoKind.KNOWN and (fbr.behavior_confirmation.value is True):
        return fbr
    if normal is not None:
        return normal
    if fbr is not None:
        return fbr
    platform = by_mech.get(OpportunityMechanism.PLATFORM_REEXPANSION)
    if platform is not None:
        return platform
    if deep is not None:
        return deep
    watch = by_mech.get(OpportunityMechanism.TREND_ESTABLISHMENT_WATCH_ONLY)
    return watch

def canonical_active_mechanisms(observations: tuple[MechanismObservation, ...]) -> tuple[OpportunityMechanism, ...]:
    active = {o.mechanism for o in observations if o.active}
    order = (OpportunityMechanism.NORMAL_RETEST_CONTINUATION, OpportunityMechanism.FALSE_BREAK_RECLAIM, OpportunityMechanism.PLATFORM_REEXPANSION, OpportunityMechanism.DEEP_STRUCTURE_TAKEOVER, OpportunityMechanism.TREND_ESTABLISHMENT_WATCH_ONLY)
    return tuple((m for m in order if m in active))

# --- ORIGINAL d4_opportunity/confirmation.py ---
from dataclasses import replace

class StaleConfirmationError(RuntimeError):
    pass

def make_behavior_confirmation_candidate(opportunity: OpportunityState, observation: MechanismObservation, *, information_cutoff: int) -> tuple[OpportunityState, BehaviorConfirmationCandidate | None]:
    if observation.watch_only or observation.mechanism is OpportunityMechanism.TREND_ESTABLISHMENT_WATCH_ONLY:
        return (opportunity, None)
    if observation.behavior_confirmation.kind is not InfoKind.KNOWN or observation.behavior_confirmation.value is not True:
        return (opportunity, None)
    if observation.mechanism in opportunity.confirmation_mechanism_history:
        return (opportunity, None)
    cid = deterministic_id('D4-B7A-CONFIRMATION', opportunity.opportunity_id, observation.mechanism.value, str(information_cutoff), *observation.source_event_ids)
    candidate = BehaviorConfirmationCandidate(candidate_id=cid, opportunity_id=opportunity.opportunity_id, trend_episode_id=opportunity.trend_episode_id, direction=opportunity.direction, market_event_id=opportunity.market_event_id, mechanism=observation.mechanism, setup_lineage=observation.setup_lineage, entry_boundary_unit_id=opportunity.entry_boundary_unit_id, entry_boundary_member_anchor_episode_ids=opportunity.entry_boundary_member_anchor_episode_ids, behavior_confirmation=InfoValue.known(True), confirmation_cutoff=information_cutoff, source_event_ids=observation.source_event_ids, provenance={'stage': 'B7-A_PRE_RISK_ONLY', 'no_risk_feasibility': 'true', 'no_entry_ready': 'true'})
    if cid in opportunity.confirmation_candidate_ids:
        return (opportunity, candidate)
    return (replace(opportunity, confirmation_candidate_ids=opportunity.confirmation_candidate_ids + (cid,), confirmation_mechanism_history=opportunity.confirmation_mechanism_history + (observation.mechanism,), updated_at=information_cutoff), candidate)

def require_same_cutoff(candidate: BehaviorConfirmationCandidate, information_cutoff: int) -> None:
    if information_cutoff != candidate.confirmation_cutoff:
        raise StaleConfirmationError(f'B7A_CONFIRMATION_STALE: candidate cutoff={candidate.confirmation_cutoff}, requested={information_cutoff}')

# --- ORIGINAL d4_opportunity/opportunity.py ---
from dataclasses import replace

class OpportunityIndependenceBlock(RuntimeError):
    pass

def _lifecycle_from_observation(obs: MechanismObservation) -> OpportunityLifecycle:
    if obs.wait_confirmation or obs.behavior_confirmation.value is True:
        return OpportunityLifecycle.WAIT_CONFIRMATION
    if obs.setup_active:
        return OpportunityLifecycle.SETUP_ACTIVE
    return OpportunityLifecycle.CANDIDATE

def _merge_history(prior: tuple[OpportunityMechanism, ...], observations: tuple[MechanismObservation, ...]) -> tuple[OpportunityMechanism, ...]:
    out = list(prior)
    for mech in canonical_active_mechanisms(observations):
        if mech not in out:
            out.append(mech)
    return tuple(out)

def open_or_update_opportunity(*, existing: OpportunityState | None, trend_episode_id: str, direction, market_event_id: str, information_cutoff: int, primary_observation: MechanismObservation, observations: tuple[MechanismObservation, ...], detector_evidence_ids: tuple[str, ...], entry_boundary: EntryBoundaryView | None, independence: OpportunityIndependenceEvidence | None) -> OpportunityState:
    """Identity follows market-event lineage; detector count never changes the ID."""
    if existing is not None and (not existing.terminal):
        if existing.trend_episode_id != trend_episode_id or existing.direction is not direction:
            raise OpportunityIndependenceBlock('ACTIVE_OPPORTUNITY_TREND_LINEAGE_MISMATCH')
        if existing.market_event_id != market_event_id:
            raise OpportunityIndependenceBlock('ACTIVE_OPPORTUNITY_MUST_TERMINATE_BEFORE_NEW_MARKET_EVENT')
        return replace(existing, lifecycle=_lifecycle_from_observation(primary_observation), mechanism_history=_merge_history(existing.mechanism_history, observations), primary_mechanism=primary_observation.mechanism, entry_boundary_unit_id=entry_boundary.unit_id if entry_boundary is not None else existing.entry_boundary_unit_id, entry_boundary_member_anchor_episode_ids=entry_boundary.member_anchor_episode_ids if entry_boundary is not None else existing.entry_boundary_member_anchor_episode_ids, updated_at=information_cutoff, setup_lineage=tuple(dict.fromkeys(existing.setup_lineage + primary_observation.setup_lineage)), detector_evidence_ids=tuple(sorted(set(existing.detector_evidence_ids + detector_evidence_ids))))
    if existing is not None and existing.terminal:
        if independence is None or not (independence.previous_opportunity_terminated and independence.material_trend_side_reseparation_or_control and independence.new_independent_countertrend_or_boundary_return_event):
            raise OpportunityIndependenceBlock('NEW_OPPORTUNITY_INDEPENDENCE_NOT_PROVEN')
    oid = deterministic_id('D4-OPPORTUNITY', trend_episode_id, direction.value, market_event_id)
    return OpportunityState(opportunity_id=oid, trend_episode_id=trend_episode_id, direction=direction, market_event_id=market_event_id, lifecycle=_lifecycle_from_observation(primary_observation), mechanism_history=_merge_history((), observations), primary_mechanism=primary_observation.mechanism, entry_boundary_unit_id=entry_boundary.unit_id if entry_boundary is not None else None, entry_boundary_member_anchor_episode_ids=entry_boundary.member_anchor_episode_ids if entry_boundary is not None else (), created_at=information_cutoff, updated_at=information_cutoff, setup_lineage=primary_observation.setup_lineage, detector_evidence_ids=tuple(sorted(set(detector_evidence_ids))), provenance={'identity': 'TREND_EPISODE_PLUS_INDEPENDENT_MARKET_EVENT_NOT_DETECTOR_COUNT'})

# --- ORIGINAL d4_opportunity/termination.py ---
from dataclasses import replace

def apply_wp4_termination(opportunity: OpportunityState, evidence: OpportunityTerminationEvidence, *, information_cutoff: int, behavior_confirmation_emitted: bool, location_failed_same_cutoff: bool) -> OpportunityState:
    """F7 subset safely decidable in WP4; downstream risk truth is not computed here."""
    if opportunity.terminal:
        return opportunity
    invalidation_reason: str | None = None
    if evidence.trend_episode_ended:
        invalidation_reason = 'SUPPORTING_TREND_EPISODE_ENDED'
    elif evidence.entry_boundary_terminal_true_break_without_false_break_recovery:
        invalidation_reason = 'ENTRY_BOUNDARY_TERMINAL_TRUE_BREAK'
    elif evidence.mechanism_required_structure_materially_failed:
        invalidation_reason = 'MECHANISM_REQUIRED_STRUCTURE_FAILED'
    elif evidence.critical_role_or_structure_replaced_destroying_thesis:
        invalidation_reason = 'CRITICAL_ROLE_OR_STRUCTURE_REPLACED'
    if invalidation_reason is not None:
        return replace(opportunity, lifecycle=OpportunityLifecycle.INVALIDATED, terminated_at=information_cutoff, updated_at=information_cutoff, termination_reason=invalidation_reason)
    if evidence.irrecoverable_continuity_end:
        return replace(opportunity, lifecycle=OpportunityLifecycle.EXPIRED, terminated_at=information_cutoff, updated_at=information_cutoff, termination_reason='IRRECOVERABLE_CANONICAL_CONTINUITY_END')
    consumed_nonactionable = behavior_confirmation_emitted and (location_failed_same_cutoff or evidence.other_same_cutoff_non_thesis_gate_failed_after_confirmation)
    if consumed_nonactionable and (not evidence.independent_open_mechanism_after_consumed_confirmation):
        return replace(opportunity, lifecycle=OpportunityLifecycle.EXPIRED, terminated_at=information_cutoff, updated_at=information_cutoff, termination_reason='CONFIRMATION_CONSUMED_NONACTIONABLE_SAME_CUTOFF')
    if evidence.event_cycle_completed_and_new_independent_event_rearmed:
        absent = evidence.downstream_actionable_entry_absent
        if absent.kind is InfoKind.KNOWN and absent.value is True:
            return replace(opportunity, lifecycle=OpportunityLifecycle.EXPIRED, terminated_at=information_cutoff, updated_at=information_cutoff, termination_reason='EVENT_CYCLE_COMPLETED_BEFORE_NEW_INDEPENDENT_EVENT')
    return opportunity

# --- ORIGINAL d4_opportunity/cutoff_contract.py ---
"""WP4 owns UPDATE-011 only.

It may consume immutable D2/D3 state but cannot write Price Structure, Trend,
Anchor, Interaction, Break, Roles, Risk, Position, Exit, or Execution truth.
"""
D4_OWNED_UPDATE_STEPS = ('UPDATE-011',)
D4_CONSUMES = ('D2_PRICE_STRUCTURE_TREND_POSITION_PLATFORM', 'D3_ANCHOR_INTERACTION_BREAK_ROLES')
D4_FORBIDDEN_WRITES = ('PRICE_STRUCTURE', 'MARKET_TREND', 'ANCHOR_INTERACTION_BREAK_ROLES', 'RISK_FEASIBILITY', 'ENTRY_READY', 'POSITION', 'EXIT', 'EXECUTION')

# --- ORIGINAL d4_opportunity/engine.py ---
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping

@dataclass(frozen=True)
class D4CutoffInput:
    information_cutoff: int
    trend: TrendEpisodeState
    trend_position: TrendPositionResult
    opportunity_direction: TrendDirection
    market_event_id: str
    detector_evidence_ids: tuple[str, ...]
    critical_information_known: InfoValue[bool]
    entry_boundary_unit: EconomicBoundaryUnit | None
    anchor_episodes: Mapping[str, AnchorEpisode]
    parameters: FrozenD4Parameters
    existing_opportunity: OpportunityState | None = None
    independence: OpportunityIndependenceEvidence | None = None
    termination: OpportunityTerminationEvidence = field(default_factory=OpportunityTerminationEvidence)
    normal_retest: NormalRetestEvidence | None = None
    false_break_reclaim: FalseBreakReclaimEvidence | None = None
    platform_reexpansion: PlatformReexpansionEvidence | None = None
    deep_takeover: DeepStructureTakeoverEvidence | None = None
    trend_establishment_watch: TrendEstablishmentWatchEvidence | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, 'anchor_episodes', MappingProxyType(dict(self.anchor_episodes)))
        if not self.market_event_id:
            raise ValueError('market_event_id required')

def _blocked_behavior_from_critical_info(info: InfoValue[bool]) -> GateEvaluation | None:
    if info.kind is InfoKind.ERROR:
        return GateEvaluation(GateName.BEHAVIOR_CONFIRMATION, InfoValue.error(info.error_ref or 'CRITICAL_INFO_ERROR'), 'SYSTEM_UNCERTAINTY')
    if info.kind is InfoKind.UNKNOWN:
        return GateEvaluation(GateName.BEHAVIOR_CONFIRMATION, InfoValue.unknown(), 'SYSTEM_UNCERTAINTY')
    if info.kind is InfoKind.KNOWN and info.value is not True:
        return GateEvaluation(GateName.BEHAVIOR_CONFIRMATION, InfoValue.unknown(), 'CRITICAL_INFORMATION_BLOCK')
    return None

def update_011(inp: D4CutoffInput) -> D4CutoffView:
    """Deterministic non-trading D4 reference update. No B8/B7-B work occurs."""
    watch_only_input = inp.trend_establishment_watch is not None and (not any((inp.normal_retest, inp.false_break_reclaim, inp.platform_reexpansion, inp.deep_takeover)))
    market_gate = market_eligibility(inp.trend, opportunity_direction=inp.opportunity_direction, critical_information_known=inp.critical_information_known, watch_only=watch_only_input)
    trend_episode_id = inp.trend.episode_id or (inp.existing_opportunity.trend_episode_id if inp.existing_opportunity is not None else 'WATCH_ONLY_NO_ACTIVE_EPISODE')
    entry_view = entry_boundary_view(inp.entry_boundary_unit, inp.anchor_episodes, target_trend_episode_id=trend_episode_id, target_direction=inp.opportunity_direction, information_cutoff=inp.information_cutoff)
    observations = []
    if inp.normal_retest is not None:
        observations.append(normal_retest_observation(inp.normal_retest, direction=inp.opportunity_direction, trend_episode_id=trend_episode_id, information_cutoff=inp.information_cutoff, market_gate=market_gate.result, entry_boundary=entry_view))
    if inp.false_break_reclaim is not None:
        observations.append(false_break_reclaim_observation(inp.false_break_reclaim, direction=inp.opportunity_direction, trend_episode_id=trend_episode_id, information_cutoff=inp.information_cutoff, market_gate=market_gate.result, entry_boundary=entry_view))
    if inp.platform_reexpansion is not None:
        pe = PlatformReexpansionEvidence(platform=inp.platform_reexpansion.platform, current_close=inp.platform_reexpansion.current_close, target_trend_episode_id=inp.platform_reexpansion.target_trend_episode_id, direction=inp.platform_reexpansion.direction, setup_lineage=inp.platform_reexpansion.setup_lineage, provenance=inp.platform_reexpansion.provenance)
        observations.append(platform_reexpansion_observation(pe, direction=inp.opportunity_direction, trend_episode_id=trend_episode_id, information_cutoff=inp.information_cutoff, market_gate=market_gate.result, entry_boundary=entry_view, theta_progress=inp.parameters.theta_progress))
    if inp.deep_takeover is not None:
        observations.append(deep_structure_takeover_observation(inp.deep_takeover, direction=inp.opportunity_direction, trend_episode_id=trend_episode_id, information_cutoff=inp.information_cutoff, market_gate=market_gate.result, entry_boundary=entry_view))
    if inp.trend_establishment_watch is not None:
        observations.append(trend_establishment_watch_observation(inp.trend_establishment_watch))
    observations_t = tuple(observations)
    primary = select_primary_observation(observations_t)
    if primary is None:
        system_block = _blocked_behavior_from_critical_info(inp.critical_information_known)
        behavior = system_block or GateEvaluation(GateName.BEHAVIOR_CONFIRMATION, InfoValue.none(), 'NO_ACTIVE_MECHANISM')
        return D4CutoffView(information_cutoff=inp.information_cutoff, opportunity=inp.existing_opportunity, primary_observation=None, market_eligibility=market_gate, location_eligibility=GateEvaluation(GateName.LOCATION_ELIGIBILITY, InfoValue.none(), 'NO_ACTIVE_MECHANISM'), behavior_confirmation=behavior, confirmation_candidate=None)
    watch_only = primary.mechanism is OpportunityMechanism.TREND_ESTABLISHMENT_WATCH_ONLY
    location_gate = location_eligibility(inp.trend_position, mechanism_location_qualified=primary.location_qualified, watch_only=watch_only)
    opportunity = open_or_update_opportunity(existing=inp.existing_opportunity, trend_episode_id=trend_episode_id, direction=inp.opportunity_direction, market_event_id=inp.market_event_id, information_cutoff=inp.information_cutoff, primary_observation=primary, observations=observations_t, detector_evidence_ids=inp.detector_evidence_ids, entry_boundary=entry_view, independence=inp.independence)
    system_block = _blocked_behavior_from_critical_info(inp.critical_information_known)
    if system_block is not None and (not watch_only):
        behavior_gate = system_block
        candidate = None
    else:
        behavior_gate = GateEvaluation(GateName.BEHAVIOR_CONFIRMATION, primary.behavior_confirmation, 'B7A_MECHANISM_BEHAVIOR_TRUTH')
        opportunity, candidate = make_behavior_confirmation_candidate(opportunity, primary, information_cutoff=inp.information_cutoff)
    location_failed = location_gate.result.kind is InfoKind.KNOWN and location_gate.result.value is False
    opportunity = apply_wp4_termination(opportunity, inp.termination, information_cutoff=inp.information_cutoff, behavior_confirmation_emitted=candidate is not None, location_failed_same_cutoff=location_failed)
    return D4CutoffView(information_cutoff=inp.information_cutoff, opportunity=opportunity, primary_observation=primary, market_eligibility=market_gate, location_eligibility=location_gate, behavior_confirmation=behavior_gate, confirmation_candidate=candidate)

# --- ORIGINAL d5_risk/types.py ---
from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction
from types import MappingProxyType
from typing import Mapping

class DecisionState(str, Enum):
    PASS = 'PASS'
    FAIL = 'FAIL'
    UNKNOWN = 'UNKNOWN'
    NA = 'N/A'
    ERROR = 'ERROR'
    BLOCKED = 'BLOCKED'

@dataclass(frozen=True)
class DecisionResult:
    state: DecisionState
    reason: str
    provenance: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, 'provenance', MappingProxyType(dict(self.provenance)))

@dataclass(frozen=True)
class RiskAnchorReference:
    risk_anchor_id: str
    opportunity_id: str
    confirmation_candidate_id: str
    mechanism: OpportunityMechanism
    direction: TrendDirection
    pivot_id: str
    pivot_type: PivotType
    layer: StructuralLayer
    price: Fraction
    confirmed_at: int
    canonical_segment_id: str
    source_scale_at_extreme: Fraction
    reason: str
    provenance: Mapping[str, str] = field(default_factory=dict)

@dataclass(frozen=True)
class AnchorSeparationView:
    entry_anchor_unit_id: str | None
    risk_anchor_id: str | None
    management_anchor_id: str | None
    management_anchor_state: DecisionResult

@dataclass(frozen=True)
class InitialHardStopCandidate:
    decision: DecisionResult
    direction: TrendDirection
    risk_anchor_id: str | None
    risk_anchor_price: Fraction | None
    symbolic_formula: str
    theta_stop_state: str
    theta_stop_exact_value: str | None
    atr_at_risk_reference: InfoValue[Fraction]
    numeric_stop_price: Fraction | None
    structural_stop_clearance: Fraction | None

    def __post_init__(self) -> None:
        if self.theta_stop_exact_value is not None:
            raise ValueError('WP5 forbids carrying a theta_stop numeric value')
        if self.numeric_stop_price is not None or self.structural_stop_clearance is not None:
            raise ValueError('WP5 forbids executable numeric Hard Stop completion')

class OperationalInputState(str, Enum):
    UNRESOLVED = 'UNRESOLVED'
    KNOWN = 'KNOWN'
    ERROR = 'ERROR'

@dataclass(frozen=True)
class OperationalInputSlot:
    name: str
    state: OperationalInputState
    exact_value: str | None = None
    error_ref: str | None = None

    def __post_init__(self) -> None:
        if self.state is OperationalInputState.KNOWN:
            if self.exact_value is None or self.error_ref is not None:
                raise ValueError('KNOWN operational input requires exact_value only')
        elif self.state is OperationalInputState.ERROR:
            if self.error_ref is None or self.exact_value is not None:
                raise ValueError('ERROR operational input requires error_ref only')
        elif self.exact_value is not None or self.error_ref is not None:
            raise ValueError('UNRESOLVED operational input cannot carry a value')

@dataclass(frozen=True)
class OperationalInputSet:
    slots: Mapping[str, OperationalInputSlot]

    def __post_init__(self) -> None:
        object.__setattr__(self, 'slots', MappingProxyType(dict(self.slots)))

    @property
    def unresolved_names(self) -> tuple[str, ...]:
        return tuple(sorted((k for k, v in self.slots.items() if v.state is OperationalInputState.UNRESOLVED)))

    @property
    def error_names(self) -> tuple[str, ...]:
        return tuple(sorted((k for k, v in self.slots.items() if v.state is OperationalInputState.ERROR)))

    @property
    def all_known(self) -> bool:
        return bool(self.slots) and all((v.state is OperationalInputState.KNOWN for v in self.slots.values()))

@dataclass(frozen=True)
class RiskAnchorSelectionResult:
    decision: DecisionResult
    anchor: RiskAnchorReference | None

@dataclass(frozen=True)
class RiskFeasibilityResult:
    decision: DecisionResult
    information_cutoff: int
    opportunity_id: str
    confirmation_candidate_id: str | None
    mechanism: OpportunityMechanism
    direction: TrendDirection
    risk_anchor: RiskAnchorReference | None
    hard_stop: InitialHardStopCandidate
    strategy_entry_reference_price: InfoValue[Fraction]
    per_unit_structural_risk: InfoValue[Fraction]
    canonical_continuity_intact: InfoValue[bool]
    risk_anchor_not_invalidated: InfoValue[bool]
    operational_inputs: OperationalInputSet
    update_step: str = 'UPDATE-012'

@dataclass(frozen=True)
class EntryReadyAssemblyResult:
    decision: DecisionResult
    information_cutoff: int
    opportunity_id: str | None
    confirmation_candidate_id: str | None
    risk_feasibility_state: DecisionState
    entry_ready_id: str | None
    semantic_entry_ready_emitted: bool
    executable: bool
    runtime_usable: bool
    update_step: str = 'UPDATE-013'

    def __post_init__(self) -> None:
        if self.executable or self.runtime_usable:
            raise ValueError('WP5 non-trading reference skeleton may not be executable/runtime usable')
        if self.semantic_entry_ready_emitted and self.entry_ready_id is None:
            raise ValueError('emitted semantic ENTRY_READY requires ID')

@dataclass(frozen=True)
class D5CutoffView:
    information_cutoff: int
    anchor_separation: AnchorSeparationView
    risk_feasibility: RiskFeasibilityResult
    entry_ready: EntryReadyAssemblyResult

# --- ORIGINAL d5_risk/parameters.py ---
from dataclasses import dataclass

@dataclass(frozen=True)
class D5ParameterView:
    snapshot_id: str
    theta_stop_state: ParameterState
    theta_stop_exact_value: str | None
    complete_strategy_parameter_snapshot: bool
    runtime_usable: bool

    def __post_init__(self) -> None:
        if self.theta_stop_state is not ParameterState.LOCKED:
            raise ValueError('WP5 current-governance contract requires theta_stop LOCKED')
        if self.theta_stop_exact_value is not None:
            raise ValueError('LOCKED theta_stop must carry no numeric value')
        if self.complete_strategy_parameter_snapshot or self.runtime_usable:
            raise ValueError('WP5 current snapshot must remain incomplete and runtime unusable')

def d5_parameter_view(snapshot: ParameterSnapshot) -> D5ParameterView:
    slot = snapshot.slot('theta_stop')
    return D5ParameterView(snapshot_id=snapshot.snapshot_id, theta_stop_state=slot.state, theta_stop_exact_value=slot.exact_value, complete_strategy_parameter_snapshot=snapshot.complete_strategy_parameter_snapshot, runtime_usable=snapshot.runtime_usable)

# --- ORIGINAL d5_risk/operational_inputs.py ---
REQUIRED_UNRESOLVED_OPERATIONAL_INPUTS = ('per_trade_account_risk', 'per_symbol_risk_cap', 'total_portfolio_risk_cap', 'same_direction_aggregate_cap', 'correlation_common_factor_budget', 'listing_liquidity_capacity_thresholds', 'spread_slippage_depth_feasibility_boundaries', 'execution_allowance', 'kill_switch_numeric_triggers', 'PORT_007_allocation_priority_policy')

def current_unresolved_operational_inputs() -> OperationalInputSet:
    return OperationalInputSet({name: OperationalInputSlot(name=name, state=OperationalInputState.UNRESOLVED) for name in REQUIRED_UNRESOLVED_OPERATIONAL_INPUTS})

def validate_required_slots(inputs: OperationalInputSet) -> tuple[str, ...]:
    return tuple((name for name in REQUIRED_UNRESOLVED_OPERATIONAL_INPUTS if name not in inputs.slots))

# --- ORIGINAL d5_risk/risk_anchor.py ---
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Mapping, Union

@dataclass(frozen=True)
class _CommonRiskEvidence:
    opportunity_id: str
    confirmation_candidate_id: str
    belongs_to_opportunity_lineage: bool
    thesis_defining: bool
    risk_anchor_not_invalidated: bool
    provenance: Mapping[str, str] = field(default_factory=dict)

@dataclass(frozen=True)
class NormalRetestRiskEvidence(_CommonRiskEvidence):
    participating_minor_pivots: tuple[StructuralPivot, ...] = ()

@dataclass(frozen=True)
class FalseBreakRiskEvidence(_CommonRiskEvidence):
    wrong_side_extreme: StructuralPivot | None = None
    false_break_event_id: str = ''

@dataclass(frozen=True)
class PlatformRiskEvidence(_CommonRiskEvidence):
    adverse_defense_extreme: StructuralPivot | None = None
    platform_episode_id: str = ''

@dataclass(frozen=True)
class DeepTakeoverRiskEvidence(_CommonRiskEvidence):
    adverse_defense_extreme: StructuralPivot | None = None
    deeper_takeover_lineage_id: str = ''

@dataclass(frozen=True)
class TrendEstablishmentRiskEvidence(_CommonRiskEvidence):
    pass
MechanismRiskEvidence = Union[NormalRetestRiskEvidence, FalseBreakRiskEvidence, PlatformRiskEvidence, DeepTakeoverRiskEvidence, TrendEstablishmentRiskEvidence]

def _validate_lineage(opportunity: OpportunityState, candidate: BehaviorConfirmationCandidate, evidence: _CommonRiskEvidence, *, information_cutoff: int) -> DecisionResult | None:
    if candidate.confirmation_cutoff != information_cutoff:
        return DecisionResult(DecisionState.ERROR, 'B7A_CONFIRMATION_NOT_SAME_CUTOFF')
    if candidate.opportunity_id != opportunity.opportunity_id or evidence.opportunity_id != opportunity.opportunity_id:
        return DecisionResult(DecisionState.ERROR, 'RISK_OPPORTUNITY_LINEAGE_MISMATCH')
    if evidence.confirmation_candidate_id != candidate.candidate_id:
        return DecisionResult(DecisionState.ERROR, 'RISK_CONFIRMATION_CANDIDATE_LINEAGE_MISMATCH')
    if candidate.trend_episode_id != opportunity.trend_episode_id or candidate.direction is not opportunity.direction:
        return DecisionResult(DecisionState.ERROR, 'RISK_TREND_LINEAGE_MISMATCH')
    if candidate.market_event_id != opportunity.market_event_id:
        return DecisionResult(DecisionState.ERROR, 'RISK_MARKET_EVENT_LINEAGE_MISMATCH')
    if opportunity.terminal:
        return DecisionResult(DecisionState.FAIL, 'OPPORTUNITY_ALREADY_TERMINATED')
    if not evidence.belongs_to_opportunity_lineage:
        return DecisionResult(DecisionState.FAIL, 'RISK_STRUCTURE_NOT_IN_OPPORTUNITY_LINEAGE')
    if not evidence.thesis_defining:
        return DecisionResult(DecisionState.FAIL, 'RISK_STRUCTURE_NOT_THESIS_DEFINING')
    return None

def _validate_pivot(pivot: StructuralPivot, *, direction: TrendDirection, information_cutoff: int, canonical_segment_id: str, require_minor: bool) -> DecisionResult | None:
    if pivot.confirmed_at > information_cutoff:
        return DecisionResult(DecisionState.ERROR, 'FUTURE_CONFIRMED_PIVOT_FORBIDDEN')
    if pivot.canonical_segment_id != canonical_segment_id:
        return DecisionResult(DecisionState.FAIL, 'RISK_ANCHOR_CANONICAL_SEGMENT_MISMATCH')
    if require_minor and pivot.layer is not StructuralLayer.MINOR:
        return DecisionResult(DecisionState.FAIL, 'NORMAL_RETEST_RISK_ANCHOR_MUST_BE_MINOR')
    expected_type = PivotType.LOW if direction is TrendDirection.LONG else PivotType.HIGH
    if pivot.pivot_type is not expected_type:
        return DecisionResult(DecisionState.FAIL, 'RISK_ANCHOR_NOT_ON_ADVERSE_STRUCTURAL_SIDE')
    return None

def _adverse_side_price_ok(direction: TrendDirection, pivot_price: Fraction, entry_price: Fraction) -> bool:
    return pivot_price < entry_price if direction is TrendDirection.LONG else pivot_price > entry_price

def _to_reference(opportunity: OpportunityState, candidate: BehaviorConfirmationCandidate, pivot: StructuralPivot, *, reason: str, evidence_provenance: Mapping[str, str]) -> RiskAnchorReference:
    rid = deterministic_id('D5-RISK-ANCHOR', opportunity.opportunity_id, candidate.candidate_id, pivot.pivot_id, reason)
    return RiskAnchorReference(risk_anchor_id=rid, opportunity_id=opportunity.opportunity_id, confirmation_candidate_id=candidate.candidate_id, mechanism=candidate.mechanism, direction=opportunity.direction, pivot_id=pivot.pivot_id, pivot_type=pivot.pivot_type, layer=pivot.layer, price=pivot.extreme_price, confirmed_at=pivot.confirmed_at, canonical_segment_id=pivot.canonical_segment_id, source_scale_at_extreme=pivot.scale_at_extreme, reason=reason, provenance={'writer': 'D5_RISK_REFERENCE_ONLY', 'source_truth': 'D2_CONFIRMED_PRICE_STRUCTURE', 'no_anchor_line_as_risk_anchor': 'true', 'not_selected_for_position_size': 'true', **dict(evidence_provenance)})

def select_mechanism_risk_anchor(opportunity: OpportunityState, candidate: BehaviorConfirmationCandidate, evidence: MechanismRiskEvidence, *, information_cutoff: int, canonical_segment_id: str, strategy_entry_reference_price: Fraction) -> RiskAnchorSelectionResult:
    lineage = _validate_lineage(opportunity, candidate, evidence, information_cutoff=information_cutoff)
    if lineage is not None:
        return RiskAnchorSelectionResult(lineage, None)
    if candidate.mechanism is OpportunityMechanism.TREND_ESTABLISHMENT_WATCH_ONLY:
        return RiskAnchorSelectionResult(DecisionResult(DecisionState.NA, 'TREND_ESTABLISHMENT_WATCH_ONLY_RISK_NA'), None)
    if candidate.mechanism is OpportunityMechanism.NORMAL_RETEST_CONTINUATION:
        if not isinstance(evidence, NormalRetestRiskEvidence):
            return RiskAnchorSelectionResult(DecisionResult(DecisionState.ERROR, 'MECHANISM_RISK_EVIDENCE_TYPE_MISMATCH'), None)
        pivots = []
        for pivot in evidence.participating_minor_pivots:
            check = _validate_pivot(pivot, direction=opportunity.direction, information_cutoff=information_cutoff, canonical_segment_id=canonical_segment_id, require_minor=True)
            if check is not None:
                return RiskAnchorSelectionResult(check, None)
            pivots.append(pivot)
        if not pivots:
            return RiskAnchorSelectionResult(DecisionResult(DecisionState.FAIL, 'NO_QUALIFIED_NORMAL_RETEST_MINOR_RISK_ANCHOR'), None)
        pivot = min(pivots, key=lambda p: p.extreme_price) if opportunity.direction is TrendDirection.LONG else max(pivots, key=lambda p: p.extreme_price)
        reason = 'ADVERSE_MOST_CONFIRMED_MINOR_IN_SETUP_THROUGH_LOCAL_CONTROL_REGAIN'
    elif candidate.mechanism is OpportunityMechanism.FALSE_BREAK_RECLAIM:
        if not isinstance(evidence, FalseBreakRiskEvidence) or evidence.wrong_side_extreme is None:
            return RiskAnchorSelectionResult(DecisionResult(DecisionState.ERROR, 'FALSE_BREAK_RISK_EVIDENCE_MISSING'), None)
        if not evidence.false_break_event_id:
            return RiskAnchorSelectionResult(DecisionResult(DecisionState.ERROR, 'FALSE_BREAK_EVENT_LINEAGE_MISSING'), None)
        pivot = evidence.wrong_side_extreme
        check = _validate_pivot(pivot, direction=opportunity.direction, information_cutoff=information_cutoff, canonical_segment_id=canonical_segment_id, require_minor=False)
        if check is not None:
            return RiskAnchorSelectionResult(check, None)
        reason = 'CONFIRMED_FALSE_BREAK_WRONG_SIDE_EXTREME'
    elif candidate.mechanism is OpportunityMechanism.PLATFORM_REEXPANSION:
        if not isinstance(evidence, PlatformRiskEvidence) or evidence.adverse_defense_extreme is None:
            return RiskAnchorSelectionResult(DecisionResult(DecisionState.ERROR, 'PLATFORM_RISK_EVIDENCE_MISSING'), None)
        if not evidence.platform_episode_id:
            return RiskAnchorSelectionResult(DecisionResult(DecisionState.ERROR, 'PLATFORM_EPISODE_LINEAGE_MISSING'), None)
        pivot = evidence.adverse_defense_extreme
        check = _validate_pivot(pivot, direction=opportunity.direction, information_cutoff=information_cutoff, canonical_segment_id=canonical_segment_id, require_minor=False)
        if check is not None:
            return RiskAnchorSelectionResult(check, None)
        reason = 'ADVERSE_DEFENSE_EXTREME_OF_CONFIRMED_PLATFORM_EPISODE'
    elif candidate.mechanism is OpportunityMechanism.DEEP_STRUCTURE_TAKEOVER:
        if not isinstance(evidence, DeepTakeoverRiskEvidence) or evidence.adverse_defense_extreme is None:
            return RiskAnchorSelectionResult(DecisionResult(DecisionState.ERROR, 'DEEP_TAKEOVER_RISK_EVIDENCE_MISSING'), None)
        if not evidence.deeper_takeover_lineage_id:
            return RiskAnchorSelectionResult(DecisionResult(DecisionState.ERROR, 'DEEP_TAKEOVER_LINEAGE_MISSING'), None)
        pivot = evidence.adverse_defense_extreme
        check = _validate_pivot(pivot, direction=opportunity.direction, information_cutoff=information_cutoff, canonical_segment_id=canonical_segment_id, require_minor=False)
        if check is not None:
            return RiskAnchorSelectionResult(check, None)
        reason = 'ADVERSE_DEFENSE_EXTREME_OF_DEEPER_TAKEOVER_CONFIRMATION_SEQUENCE'
    else:
        return RiskAnchorSelectionResult(DecisionResult(DecisionState.ERROR, 'UNSUPPORTED_MECHANISM'), None)
    if not _adverse_side_price_ok(opportunity.direction, pivot.extreme_price, strategy_entry_reference_price):
        return RiskAnchorSelectionResult(DecisionResult(DecisionState.FAIL, 'RISK_ANCHOR_NOT_ADVERSE_TO_STRATEGY_ENTRY_REFERENCE'), None)
    if not evidence.risk_anchor_not_invalidated:
        return RiskAnchorSelectionResult(DecisionResult(DecisionState.FAIL, 'RISK_ANCHOR_ALREADY_INVALIDATED'), None)
    return RiskAnchorSelectionResult(DecisionResult(DecisionState.PASS, 'QUALIFIED_MECHANISM_SPECIFIC_RISK_ANCHOR'), _to_reference(opportunity, candidate, pivot, reason=reason, evidence_provenance=evidence.provenance))

# --- ORIGINAL d5_risk/hard_stop.py ---
from fractions import Fraction

def symbolic_initial_hard_stop_candidate(risk_anchor: RiskAnchorReference | None, *, direction: TrendDirection, atr_at_risk_reference: InfoValue[Fraction], parameters: D5ParameterView) -> InitialHardStopCandidate:
    formula = 'HardStop = RiskAnchor - theta_stop * ATR_at_risk_reference' if direction is TrendDirection.LONG else 'HardStop = RiskAnchor + theta_stop * ATR_at_risk_reference'
    if risk_anchor is None:
        decision = DecisionResult(DecisionState.FAIL, 'NO_QUALIFIED_RISK_ANCHOR_FOR_HARD_STOP')
    elif atr_at_risk_reference.kind is InfoKind.ERROR:
        decision = DecisionResult(DecisionState.ERROR, 'ATR_AT_RISK_REFERENCE_ERROR')
    elif atr_at_risk_reference.kind is InfoKind.UNKNOWN:
        decision = DecisionResult(DecisionState.UNKNOWN, 'ATR_AT_RISK_REFERENCE_UNKNOWN')
    elif atr_at_risk_reference.kind in (InfoKind.NONE, InfoKind.NA):
        decision = DecisionResult(DecisionState.NA, 'ATR_AT_RISK_REFERENCE_NA')
    else:
        decision = DecisionResult(DecisionState.BLOCKED, 'THETA_STOP_LOCKED_NO_AUTHORIZED_NUMERIC_VALUE', {'formula_preserved': 'true', 'numeric_stop_forbidden_in_wp5': 'true'})
    return InitialHardStopCandidate(decision=decision, direction=direction, risk_anchor_id=risk_anchor.risk_anchor_id if risk_anchor is not None else None, risk_anchor_price=risk_anchor.price if risk_anchor is not None else None, symbolic_formula=formula, theta_stop_state=parameters.theta_stop_state.value, theta_stop_exact_value=parameters.theta_stop_exact_value, atr_at_risk_reference=atr_at_risk_reference, numeric_stop_price=None, structural_stop_clearance=None)

# --- ORIGINAL d5_risk/feasibility.py ---
from fractions import Fraction

def _nonknown_to_decision(value: InfoValue[object], label: str) -> DecisionResult | None:
    if value.kind is InfoKind.ERROR:
        return DecisionResult(DecisionState.ERROR, f'{label}_ERROR')
    if value.kind is InfoKind.UNKNOWN:
        return DecisionResult(DecisionState.UNKNOWN, f'{label}_UNKNOWN')
    if value.kind in (InfoKind.NONE, InfoKind.NA):
        return DecisionResult(DecisionState.NA, f'{label}_NA')
    return None

def evaluate_risk_feasibility(opportunity: OpportunityState, candidate: BehaviorConfirmationCandidate | None, anchor_selection: RiskAnchorSelectionResult, *, information_cutoff: int, strategy_entry_reference_price: InfoValue[Fraction], atr_at_risk_reference: InfoValue[Fraction], canonical_continuity_intact: InfoValue[bool], risk_anchor_not_invalidated: InfoValue[bool], operational_inputs: OperationalInputSet, parameters: D5ParameterView) -> RiskFeasibilityResult:
    mechanism = opportunity.primary_mechanism
    if mechanism is OpportunityMechanism.TREND_ESTABLISHMENT_WATCH_ONLY:
        hard = symbolic_initial_hard_stop_candidate(None, direction=opportunity.direction, atr_at_risk_reference=InfoValue.na(), parameters=parameters)
        return RiskFeasibilityResult(DecisionResult(DecisionState.NA, 'TREND_ESTABLISHMENT_WATCH_ONLY_RISK_FEASIBILITY_NA'), information_cutoff, opportunity.opportunity_id, None, mechanism, opportunity.direction, None, hard, strategy_entry_reference_price, InfoValue.na(), canonical_continuity_intact, risk_anchor_not_invalidated, operational_inputs)
    if candidate is None:
        hard = symbolic_initial_hard_stop_candidate(None, direction=opportunity.direction, atr_at_risk_reference=atr_at_risk_reference, parameters=parameters)
        return RiskFeasibilityResult(DecisionResult(DecisionState.NA, 'NO_SAME_CUTOFF_B7A_CONFIRMATION_CANDIDATE'), information_cutoff, opportunity.opportunity_id, None, mechanism, opportunity.direction, None, hard, strategy_entry_reference_price, InfoValue.na(), canonical_continuity_intact, risk_anchor_not_invalidated, operational_inputs)
    if candidate.confirmation_cutoff != information_cutoff:
        decision = DecisionResult(DecisionState.ERROR, 'STALE_B7A_CONFIRMATION_FOR_RISK')
    elif candidate.opportunity_id != opportunity.opportunity_id or candidate.trend_episode_id != opportunity.trend_episode_id:
        decision = DecisionResult(DecisionState.ERROR, 'B8_B7A_OPPORTUNITY_LINEAGE_MISMATCH')
    elif candidate.mechanism is not mechanism:
        decision = DecisionResult(DecisionState.ERROR, 'B8_PRIMARY_MECHANISM_MISMATCH')
    elif anchor_selection.decision.state is not DecisionState.PASS:
        decision = anchor_selection.decision
    else:
        entry_nonknown = _nonknown_to_decision(strategy_entry_reference_price, 'STRATEGY_ENTRY_REFERENCE')
        continuity_nonknown = _nonknown_to_decision(canonical_continuity_intact, 'CANONICAL_CONTINUITY')
        invalid_nonknown = _nonknown_to_decision(risk_anchor_not_invalidated, 'RISK_ANCHOR_VALIDITY')
        if entry_nonknown is not None:
            decision = entry_nonknown
        elif continuity_nonknown is not None:
            decision = continuity_nonknown
        elif invalid_nonknown is not None:
            decision = invalid_nonknown
        elif canonical_continuity_intact.value is not True:
            decision = DecisionResult(DecisionState.FAIL, 'CANONICAL_CONTINUITY_NOT_INTACT')
        elif risk_anchor_not_invalidated.value is not True:
            decision = DecisionResult(DecisionState.FAIL, 'RISK_ANCHOR_ALREADY_INVALIDATED')
        else:
            decision = DecisionResult(DecisionState.PASS, 'STRUCTURAL_PRECONDITIONS_AVAILABLE_PENDING_HARD_STOP_AND_OPERATIONAL_INPUTS')
    hard = symbolic_initial_hard_stop_candidate(anchor_selection.anchor if anchor_selection.decision.state is DecisionState.PASS else None, direction=opportunity.direction, atr_at_risk_reference=atr_at_risk_reference, parameters=parameters)
    missing = validate_required_slots(operational_inputs)
    if decision.state is DecisionState.PASS:
        if hard.decision.state is not DecisionState.PASS:
            decision = hard.decision
        elif missing:
            decision = DecisionResult(DecisionState.BLOCKED, 'REQUIRED_OPERATIONAL_INPUT_SLOTS_NOT_DECLARED')
        elif operational_inputs.error_names:
            decision = DecisionResult(DecisionState.ERROR, 'OPERATIONAL_INPUT_ERROR')
        elif operational_inputs.unresolved_names:
            decision = DecisionResult(DecisionState.BLOCKED, 'RISK_BUDGET_PORTFOLIO_LIQUIDITY_EXECUTION_INPUTS_UNRESOLVED', {'unresolved_count': str(len(operational_inputs.unresolved_names))})
        elif not operational_inputs.all_known:
            decision = DecisionResult(DecisionState.UNKNOWN, 'OPERATIONAL_INPUTS_NOT_ALL_KNOWN')
    per_unit = InfoValue.unknown() if decision.state in (DecisionState.BLOCKED, DecisionState.UNKNOWN) else InfoValue.na()
    return RiskFeasibilityResult(decision=decision, information_cutoff=information_cutoff, opportunity_id=opportunity.opportunity_id, confirmation_candidate_id=candidate.candidate_id, mechanism=mechanism, direction=opportunity.direction, risk_anchor=anchor_selection.anchor, hard_stop=hard, strategy_entry_reference_price=strategy_entry_reference_price, per_unit_structural_risk=per_unit, canonical_continuity_intact=canonical_continuity_intact, risk_anchor_not_invalidated=risk_anchor_not_invalidated, operational_inputs=operational_inputs)

# --- ORIGINAL d5_risk/engine.py ---
from dataclasses import dataclass
from fractions import Fraction

@dataclass(frozen=True)
class D5CutoffInput:
    information_cutoff: int
    d4_view: D4CutoffView
    risk_evidence: MechanismRiskEvidence
    canonical_segment_id: str
    strategy_entry_reference_price: InfoValue[Fraction]
    atr_at_risk_reference: InfoValue[Fraction]
    canonical_continuity_intact: InfoValue[bool]
    risk_anchor_not_invalidated: InfoValue[bool]
    operational_inputs: OperationalInputSet
    parameters: D5ParameterView

    def __post_init__(self) -> None:
        if self.d4_view.information_cutoff != self.information_cutoff:
            raise ValueError('D5_CANNOT_CONSUME_D4_VIEW_FROM_DIFFERENT_CUTOFF')
        if not self.canonical_segment_id:
            raise ValueError('canonical_segment_id required')

def update_012_013(inp: D5CutoffInput) -> D5CutoffView:
    opportunity = inp.d4_view.opportunity
    candidate = inp.d4_view.confirmation_candidate
    if opportunity is None:
        raise ValueError('D5_REQUIRES_D4_OPPORTUNITY_STATE')
    entry_value = inp.strategy_entry_reference_price.value if inp.strategy_entry_reference_price.kind is InfoKind.KNOWN else None
    if candidate is None:
        anchor_selection = RiskAnchorSelectionResult(DecisionResult(DecisionState.NA, 'RISK_ANCHOR_SELECTION_REQUIRES_CURRENT_B7A'), None)
    elif entry_value is None:
        if inp.strategy_entry_reference_price.kind is InfoKind.ERROR:
            state = DecisionState.ERROR
        elif inp.strategy_entry_reference_price.kind is InfoKind.UNKNOWN:
            state = DecisionState.UNKNOWN
        else:
            state = DecisionState.NA
        anchor_selection = RiskAnchorSelectionResult(DecisionResult(state, 'STRATEGY_ENTRY_REFERENCE_NOT_KNOWN_FOR_RISK_ANCHOR_ADVERSE_SIDE_CHECK'), None)
    else:
        anchor_selection = select_mechanism_risk_anchor(opportunity, candidate, inp.risk_evidence, information_cutoff=inp.information_cutoff, canonical_segment_id=inp.canonical_segment_id, strategy_entry_reference_price=entry_value)
    risk = evaluate_risk_feasibility(opportunity, candidate, anchor_selection, information_cutoff=inp.information_cutoff, strategy_entry_reference_price=inp.strategy_entry_reference_price, atr_at_risk_reference=inp.atr_at_risk_reference, canonical_continuity_intact=inp.canonical_continuity_intact, risk_anchor_not_invalidated=inp.risk_anchor_not_invalidated, operational_inputs=inp.operational_inputs, parameters=inp.parameters)
    entry_ready = assemble_b7b_entry_ready(inp.d4_view, risk, parameters=inp.parameters)
    separation = AnchorSeparationView(entry_anchor_unit_id=opportunity.entry_boundary_unit_id, risk_anchor_id=risk.risk_anchor.risk_anchor_id if risk.risk_anchor is not None else None, management_anchor_id=None, management_anchor_state=DecisionResult(DecisionState.NA, 'MANAGEMENT_ANCHOR_IS_POST_ENTRY_D6_SCOPE'))
    return D5CutoffView(information_cutoff=inp.information_cutoff, anchor_separation=separation, risk_feasibility=risk, entry_ready=entry_ready)

# --- ORIGINAL d5_risk/cutoff_contract.py ---
"""WP5 owns only UPDATE-012 and the B7-B assembly interface at UPDATE-013."""
D5_OWNED_UPDATE_STEPS = ('UPDATE-012', 'UPDATE-013')
UPDATE_012_CONTRACT = ('consume_same_cutoff_B7A_candidate', 'select_structural_RiskAnchor', 'preserve_symbolic_initial_HardStop', 'evaluate_RiskFeasibility_fail_closed')
UPDATE_013_CONTRACT = ('same_cutoff_market_location_behavior_risk_assembly', 'no_stale_cross_cutoff_gate_reuse', 'watch_only_never_entry_ready', 'incomplete_snapshot_blocks_runtime_entry_ready')

# --- ORIGINAL d4_b7b_entry_ready.py ---
def _gate_state(value: InfoValue[bool], label: str) -> DecisionResult:
    if value.kind is InfoKind.ERROR:
        return DecisionResult(DecisionState.ERROR, f'{label}_ERROR')
    if value.kind is InfoKind.UNKNOWN:
        return DecisionResult(DecisionState.UNKNOWN, f'{label}_UNKNOWN')
    if value.kind in (InfoKind.NONE, InfoKind.NA):
        return DecisionResult(DecisionState.NA, f'{label}_NA')
    return DecisionResult(DecisionState.PASS if value.value is True else DecisionState.FAIL, f"{label}_{('PASS' if value.value else 'FAIL')}")

def assemble_b7b_entry_ready(d4_view: D4CutoffView, risk: RiskFeasibilityResult, *, parameters: D5ParameterView) -> EntryReadyAssemblyResult:
    cutoff = d4_view.information_cutoff
    opportunity = d4_view.opportunity
    candidate = d4_view.confirmation_candidate
    oid = opportunity.opportunity_id if opportunity is not None else None
    cid = candidate.candidate_id if candidate is not None else None
    if risk.information_cutoff != cutoff:
        decision = DecisionResult(DecisionState.ERROR, 'B7B_RISK_CUTOFF_MISMATCH')
    elif opportunity is None:
        decision = DecisionResult(DecisionState.NA, 'NO_OPPORTUNITY')
    elif opportunity.primary_mechanism is OpportunityMechanism.TREND_ESTABLISHMENT_WATCH_ONLY:
        decision = DecisionResult(DecisionState.NA, 'TREND_ESTABLISHMENT_WATCH_ONLY_NEVER_ENTRY_READY')
    elif candidate is None:
        decision = DecisionResult(DecisionState.NA, 'NO_SAME_CUTOFF_B7A_CONFIRMATION')
    elif candidate.confirmation_cutoff != cutoff or not candidate.same_cutoff_only:
        decision = DecisionResult(DecisionState.ERROR, 'B7A_CONFIRMATION_NOT_SAME_CUTOFF')
    elif risk.confirmation_candidate_id != candidate.candidate_id or risk.opportunity_id != opportunity.opportunity_id:
        decision = DecisionResult(DecisionState.ERROR, 'B7B_LINEAGE_MISMATCH')
    else:
        gates = (_gate_state(d4_view.market_eligibility.result, 'MARKET_ELIGIBILITY'), _gate_state(d4_view.location_eligibility.result, 'LOCATION_ELIGIBILITY'), _gate_state(d4_view.behavior_confirmation.result, 'BEHAVIOR_CONFIRMATION'), risk.decision)
        error = next((g for g in gates if g.state is DecisionState.ERROR), None)
        blocked = next((g for g in gates if g.state is DecisionState.BLOCKED), None)
        failed = next((g for g in gates if g.state is DecisionState.FAIL), None)
        unknown = next((g for g in gates if g.state is DecisionState.UNKNOWN), None)
        na = next((g for g in gates if g.state is DecisionState.NA), None)
        if error is not None:
            decision = error
        elif blocked is not None:
            decision = blocked
        elif failed is not None:
            decision = failed
        elif unknown is not None:
            decision = unknown
        elif na is not None:
            decision = na
        elif not parameters.complete_strategy_parameter_snapshot or not parameters.runtime_usable:
            decision = DecisionResult(DecisionState.BLOCKED, 'INCOMPLETE_STRATEGY_PARAMETER_SNAPSHOT_RUNTIME_UNUSABLE')
        else:
            decision = DecisionResult(DecisionState.PASS, 'ALL_FOUR_SAME_CUTOFF_GATES_PASS')
    emitted = decision.state is DecisionState.PASS
    entry_ready_id = deterministic_id('D4-B7B-ENTRY-READY', oid, cid, str(cutoff)) if emitted else None
    return EntryReadyAssemblyResult(decision=decision, information_cutoff=cutoff, opportunity_id=oid, confirmation_candidate_id=cid, risk_feasibility_state=risk.decision.state, entry_ready_id=entry_ready_id, semantic_entry_ready_emitted=emitted, executable=False, runtime_usable=False)

# --- ORIGINAL d6_position_execution/types.py ---
from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction
from types import MappingProxyType
from typing import Mapping

class PositionProvenanceClass(str, Enum):
    AUTHORITATIVE_STRATEGY = 'AUTHORITATIVE_STRATEGY'
    NONAUTHORITATIVE_SYNTHETIC_FIXTURE_ONLY = 'NONAUTHORITATIVE_SYNTHETIC_FIXTURE_ONLY'

class PositionMode(str, Enum):
    ACTIVE = 'ACTIVE'
    DEGRADED_PROTECTIVE = 'DEGRADED_PROTECTIVE'
    CLOSED = 'CLOSED'

class PositionObserverLabel(str, Enum):
    INITIAL_RISK = 'INITIAL_RISK'
    STRUCTURE_CONFIRMED = 'STRUCTURE_CONFIRMED'
    TREND_RIDE = 'TREND_RIDE'
    PRESSURED = 'PRESSURED'
    EXIT_CANDIDATE = 'EXIT_CANDIDATE'

class StrategyExitReason(str, Enum):
    HARD_RISK_STOP = 'HARD_RISK_STOP'
    ENTRY_THESIS_FAILURE = 'ENTRY_THESIS_FAILURE'
    MANAGEMENT_STRUCTURE_FAILURE = 'MANAGEMENT_STRUCTURE_FAILURE'
    MARKET_STRUCTURAL_FAILURE = 'MARKET_STRUCTURAL_FAILURE'
    TREND_EPISODE_END = 'TREND_EPISODE_END'

class ExitSource(str, Enum):
    EXECUTION_HARD_PROTECTION = 'EXECUTION_HARD_PROTECTION'
    STRATEGY_CLOSED_BAR = 'STRATEGY_CLOSED_BAR'

class ExecutionStatus(str, Enum):
    EXECUTABLE = 'EXECUTABLE'
    BLOCKED = 'BLOCKED'
    MISSED = 'MISSED'
    FAILED = 'FAILED'
    CANCELLED_BY_STRATEGY = 'CANCELLED_BY_STRATEGY'
    EXPIRED = 'EXPIRED'

class TrendEpisodeEndCause(str, Enum):
    NONE = 'NONE'
    STRUCTURAL_FAILURE = 'STRUCTURAL_FAILURE'
    AUTHORIZED_NONSTRUCTURAL = 'AUTHORIZED_NONSTRUCTURAL'
    GAP = 'GAP'
    UNKNOWN = 'UNKNOWN'

@dataclass(frozen=True)
class FrozenEntryProvenance:
    provenance_class: PositionProvenanceClass
    entry_ready_id: str
    entry_ready_cutoff: int
    symbol: str
    direction: TrendDirection
    trend_episode_id: str
    opportunity_id: str
    market_event_id: str
    entry_boundary_unit_id: str | None
    risk_anchor_id: str
    risk_anchor_pivot_id: str
    risk_anchor_layer: StructuralLayer
    risk_anchor_price: Fraction
    risk_anchor_scale: Fraction
    risk_anchor_confirmed_at: int
    risk_anchor_timeframe_ms: int
    canonical_segment_id: str
    strategy_entry_reference_price: Fraction
    initial_hard_stop_state: DecisionState
    initial_hard_stop_numeric: Fraction | None
    provenance: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, 'provenance', MappingProxyType(dict(self.provenance)))
        if self.direction not in (TrendDirection.LONG, TrendDirection.SHORT):
            raise ValueError('Position entry provenance requires LONG/SHORT')
        if not self.entry_ready_id or not self.symbol or (not self.trend_episode_id) or (not self.opportunity_id):
            raise ValueError('frozen entry provenance requires immutable lineage IDs')
        if self.risk_anchor_scale <= 0:
            raise ValueError('risk_anchor_scale must be positive')
        if self.risk_anchor_confirmed_at > self.entry_ready_cutoff:
            raise ValueError('future Risk Anchor cannot be frozen into Entry provenance')
        if self.risk_anchor_timeframe_ms <= 0:
            raise ValueError('risk_anchor_timeframe_ms must be positive')
        if not self.canonical_segment_id:
            raise ValueError('canonical_segment_id required')
        if self.provenance_class is PositionProvenanceClass.AUTHORITATIVE_STRATEGY:
            if self.initial_hard_stop_numeric is not None and self.initial_hard_stop_state is not DecisionState.PASS:
                raise ValueError('authoritative numeric Hard Stop requires PASS state')

@dataclass(frozen=True)
class StrategyPositionSnapshot:
    position_id: str
    entry: FrozenEntryProvenance
    opened_from_execution_evidence_id: str | None
    opened_real_time: int | None
    mode: PositionMode
    latest_qualified_protective_pivot: StructuralPivot | None
    current_protective_stop: InfoValue[Fraction]
    observer_label: PositionObserverLabel | None = None
    closed_exit_id: str | None = None
    provenance: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, 'provenance', MappingProxyType(dict(self.provenance)))
        if self.mode is PositionMode.CLOSED and self.closed_exit_id is None:
            raise ValueError('CLOSED position requires closed_exit_id')
        if self.mode is not PositionMode.CLOSED and self.closed_exit_id is not None:
            raise ValueError('open position cannot carry closed_exit_id')
        if self.entry.provenance_class is PositionProvenanceClass.AUTHORITATIVE_STRATEGY:
            if not self.opened_from_execution_evidence_id or self.opened_real_time is None:
                raise ValueError('authoritative Strategy Position requires real execution activation evidence')

@dataclass(frozen=True)
class ProtectivePivotEvidence:
    adverse_minor_pivot: StructuralPivot | None
    material_favorable_post_entry_progress: InfoValue[bool]
    trade_thesis_intact: InfoValue[bool]
    trend_thesis_intact: InfoValue[bool]
    local_trend_control_regained: InfoValue[bool]
    provenance: Mapping[str, str] = field(default_factory=dict)

@dataclass(frozen=True)
class QualifiedProtectivePivotResult:
    decision: DecisionResult
    pivot: StructuralPivot | None
    symbolic_candidate_stop: str | None
    numeric_candidate_stop: Fraction | None
    theta_stop_state: str

    def __post_init__(self) -> None:
        if self.numeric_candidate_stop is not None:
            raise ValueError('WP6 current governance forbids generating a new numeric protective stop')

@dataclass(frozen=True)
class HardProtectionEvidence:
    triggered: InfoValue[bool]
    execution_event_id: str | None
    real_event_time: int | None
    evidence_source: str = 'EXTERNAL_EXECUTION_EVIDENCE_INTERFACE'

    def __post_init__(self) -> None:
        if self.triggered.value is True:
            if not self.execution_event_id or self.real_event_time is None:
                raise ValueError('known Hard Protection trigger requires execution event evidence/time')

@dataclass(frozen=True)
class TrendEpisodeEndEvidence:
    ended: InfoValue[bool]
    cause: TrendEpisodeEndCause
    provenance: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, 'provenance', MappingProxyType(dict(self.provenance)))
        if self.cause is TrendEpisodeEndCause.GAP and self.ended.value is True:
            raise ValueError('canonical gap may not be represented as TREND_EPISODE_END')

@dataclass(frozen=True)
class ExitCandidateEvidence:
    management_anchor_true_break: InfoValue[bool] = field(default_factory=InfoValue.unknown)
    entry_risk_anchor_wrong_side_close: InfoValue[bool] = field(default_factory=InfoValue.unknown)

@dataclass(frozen=True)
class TradeExitRecord:
    exit_id: str
    position_id: str
    primary_reason: StrategyExitReason
    source: ExitSource
    strategy_information_cutoff: int | None
    real_event_time: int | None
    concurrent_exit_conditions: tuple[StrategyExitReason, ...]
    supporting_trend_episode_ended: bool
    execution_evidence_id: str | None
    immutable: bool = True

    def __post_init__(self) -> None:
        if not self.immutable:
            raise ValueError('Trade Exit records are immutable')
        if self.source is ExitSource.STRATEGY_CLOSED_BAR and self.strategy_information_cutoff is None:
            raise ValueError('Strategy Exit requires causal closed-bar cutoff')
        if self.source is ExitSource.EXECUTION_HARD_PROTECTION:
            if self.real_event_time is None or not self.execution_evidence_id:
                raise ValueError('Hard Protection exit requires real execution evidence')

@dataclass(frozen=True)
class ExitEvaluation:
    decision: DecisionResult
    exit_record: TradeExitRecord | None
    entry_thesis_failure: DecisionResult
    management_structure_failure: DecisionResult
    market_structural_failure: DecisionResult
    trend_episode_end: DecisionResult
    exit_candidate: DecisionResult
    degraded_protective: bool

@dataclass(frozen=True)
class ExecutionIntentSnapshot:
    execution_intent_id: str
    entry_ready_id: str
    strategy_signal_cutoff: int
    status: ExecutionStatus
    status_event_id: str
    observed_at: int
    immutable_strategy_entry_ready: bool = True

    def __post_init__(self) -> None:
        if not self.immutable_strategy_entry_ready:
            raise ValueError('Execution cannot rewrite historical ENTRY_READY')

@dataclass(frozen=True)
class ReconciliationState:
    strategy_exit_id: str
    residual_real_exposure: InfoValue[bool]
    hard_protection_preserved: InfoValue[bool]
    execution_reconciliation_reference: str | None

@dataclass(frozen=True)
class D6CutoffView:
    information_cutoff: int
    position_id: str
    position_mode: PositionMode
    qualified_protective_pivot: QualifiedProtectivePivotResult
    exit_evaluation: ExitEvaluation
    new_risk_blocked: bool
    update_step: str = 'UPDATE-010'

# --- ORIGINAL d6_position_execution/parameters.py ---
from dataclasses import dataclass
from fractions import Fraction

@dataclass(frozen=True)
class D6ParameterView:
    theta_progress: Fraction
    theta_stop_state: ParameterState
    theta_stop_exact_value: str | None
    complete_strategy_parameter_snapshot: bool
    runtime_usable: bool

    def __post_init__(self) -> None:
        if self.theta_progress < 0:
            raise ValueError('theta_progress must be nonnegative')
        if self.theta_stop_state is not ParameterState.LOCKED:
            raise ValueError('current WP6 governance requires theta_stop LOCKED')
        if self.theta_stop_exact_value is not None:
            raise ValueError('LOCKED theta_stop must carry no numeric value')
        if self.complete_strategy_parameter_snapshot or self.runtime_usable:
            raise ValueError('current WP6 snapshot must remain incomplete/runtime unusable')

def d6_parameter_view(snapshot: ParameterSnapshot) -> D6ParameterView:
    progress = snapshot.slot('theta_progress')
    stop = snapshot.slot('theta_stop')
    if progress.state is not ParameterState.FROZEN or progress.exact_value is None:
        raise ValueError('theta_progress must be FROZEN with exact value')
    return D6ParameterView(theta_progress=Fraction(progress.exact_value), theta_stop_state=stop.state, theta_stop_exact_value=stop.exact_value, complete_strategy_parameter_snapshot=snapshot.complete_strategy_parameter_snapshot, runtime_usable=snapshot.runtime_usable)

# --- ORIGINAL d6_position_execution/position.py ---
from dataclasses import replace

class StrategyPositionRegistry:
    """In-memory reference firewall for Position baseline constraints.

    This is not persistence, execution, or order placement. It only rejects
    duplicate/opposite active Strategy Position histories and reuse of one
    Opportunity as more than one initial Strategy Entry.
    """

    def __init__(self) -> None:
        self._active_by_symbol: dict[str, StrategyPositionSnapshot] = {}
        self._used_opportunity_ids: set[str] = set()

    def register(self, position: StrategyPositionSnapshot) -> None:
        symbol = position.entry.symbol
        if symbol in self._active_by_symbol:
            raise ValueError('POSITION-001/002: at most one net Strategy Position per symbol')
        if position.entry.opportunity_id in self._used_opportunity_ids:
            raise ValueError('POSITION-003: one Opportunity may create at most one initial Strategy Entry')
        if position.mode is PositionMode.CLOSED:
            raise ValueError('cannot register already-closed position as active')
        self._active_by_symbol[symbol] = position
        self._used_opportunity_ids.add(position.entry.opportunity_id)

    def close(self, position_id: str, exit_id: str) -> StrategyPositionSnapshot:
        for symbol, position in tuple(self._active_by_symbol.items()):
            if position.position_id == position_id:
                closed = replace(position, mode=PositionMode.CLOSED, closed_exit_id=exit_id)
                del self._active_by_symbol[symbol]
                return closed
        raise KeyError(position_id)

    def active(self, symbol: str) -> StrategyPositionSnapshot | None:
        return self._active_by_symbol.get(symbol)

def position_id_from_entry_ready(entry_ready_id: str, opportunity_id: str, symbol: str) -> str:
    return deterministic_id('D6-STRATEGY-POSITION', entry_ready_id, opportunity_id, symbol)

def assert_current_wp5_cannot_create_real_position(entry_ready: EntryReadyAssemblyResult) -> None:
    """Current-state guard: WP5 did not emit ENTRY_READY, so WP6 cannot create a real Position."""
    if entry_ready.semantic_entry_ready_emitted:
        raise ValueError('unexpected current-state ENTRY_READY emission; authority/state review required')
    if entry_ready.entry_ready_id is not None:
        raise ValueError('non-emitted ENTRY_READY may not carry a usable ID')

def assert_synthetic_fixture(position: StrategyPositionSnapshot) -> None:
    if position.entry.provenance_class is not PositionProvenanceClass.NONAUTHORITATIVE_SYNTHETIC_FIXTURE_ONLY:
        raise ValueError('WP6 self-check Position must be NONAUTHORITATIVE_SYNTHETIC_FIXTURE_ONLY')

# --- ORIGINAL d6_position_execution/management.py ---
from fractions import Fraction

def _decision_from_required_bool(value, name: str) -> DecisionResult | None:
    if value.kind is InfoKind.ERROR:
        return DecisionResult(DecisionState.ERROR, f'{name}_ERROR')
    if value.kind is InfoKind.UNKNOWN:
        return DecisionResult(DecisionState.UNKNOWN, f'{name}_UNKNOWN')
    if value.kind in (InfoKind.NONE, InfoKind.NA):
        return DecisionResult(DecisionState.NA, f'{name}_NA')
    if value.value is not True:
        return DecisionResult(DecisionState.FAIL, f'{name}_NOT_SATISFIED')
    return None

def qualify_protective_pivot(position: StrategyPositionSnapshot, evidence: ProtectivePivotEvidence, *, information_cutoff: int, parameters: D6ParameterView) -> QualifiedProtectivePivotResult:
    pivot = evidence.adverse_minor_pivot
    if pivot is None:
        return QualifiedProtectivePivotResult(DecisionResult(DecisionState.NA, 'NO_ADVERSE_MINOR_PIVOT'), None, None, None, parameters.theta_stop_state.value)
    if pivot.confirmed_at > information_cutoff:
        return QualifiedProtectivePivotResult(DecisionResult(DecisionState.ERROR, 'FUTURE_CONFIRMED_PROTECTIVE_PIVOT_FORBIDDEN'), None, None, None, parameters.theta_stop_state.value)
    if pivot.symbol != position.entry.symbol or pivot.canonical_segment_id != position.entry.canonical_segment_id:
        return QualifiedProtectivePivotResult(DecisionResult(DecisionState.FAIL, 'PROTECTIVE_PIVOT_LINEAGE_OR_CONTINUITY_MISMATCH'), None, None, None, parameters.theta_stop_state.value)
    if pivot.layer is not StructuralLayer.MINOR:
        return QualifiedProtectivePivotResult(DecisionResult(DecisionState.FAIL, 'QUALIFIED_PROTECTIVE_PIVOT_MUST_BE_MINOR'), None, None, None, parameters.theta_stop_state.value)
    expected = PivotType.LOW if position.entry.direction is TrendDirection.LONG else PivotType.HIGH
    if pivot.pivot_type is not expected:
        return QualifiedProtectivePivotResult(DecisionResult(DecisionState.FAIL, 'PROTECTIVE_PIVOT_NOT_ADVERSE_MINOR_SIDE'), None, None, None, parameters.theta_stop_state.value)
    for value, name in ((evidence.material_favorable_post_entry_progress, 'MATERIAL_FAVORABLE_POST_ENTRY_PROGRESS'), (evidence.trade_thesis_intact, 'TRADE_THESIS_INTACT'), (evidence.trend_thesis_intact, 'TREND_THESIS_INTACT'), (evidence.local_trend_control_regained, 'LOCAL_TREND_CONTROL_REGAIN')):
        decision = _decision_from_required_bool(value, name)
        if decision is not None:
            return QualifiedProtectivePivotResult(decision, None, None, None, parameters.theta_stop_state.value)
    side = '-' if position.entry.direction is TrendDirection.LONG else '+'
    symbolic = f'{pivot.extreme_price} {side} theta_stop * ATR_at_protective_pivot_reference'
    return QualifiedProtectivePivotResult(DecisionResult(DecisionState.BLOCKED, 'QUALIFIED_PROTECTIVE_PIVOT_BUT_THETA_STOP_LOCKED_NO_NUMERIC_CANDIDATE'), pivot, symbolic, None, parameters.theta_stop_state.value)

def monotonic_stop_semantics(direction: TrendDirection, old_stop: Fraction, candidate_stop: Fraction) -> Fraction:
    """Pure RC1 ratchet relation; current WP6 engine never creates candidate_stop numerically."""
    if direction is TrendDirection.LONG:
        return max(old_stop, candidate_stop)
    if direction is TrendDirection.SHORT:
        return min(old_stop, candidate_stop)
    raise ValueError('monotonic stop semantics require LONG/SHORT')

# --- ORIGINAL d6_position_execution/exit.py ---
from fractions import Fraction
STRATEGY_EXIT_PRECEDENCE = (StrategyExitReason.MARKET_STRUCTURAL_FAILURE, StrategyExitReason.TREND_EPISODE_END, StrategyExitReason.ENTRY_THESIS_FAILURE, StrategyExitReason.MANAGEMENT_STRUCTURE_FAILURE)

def _bool_decision(value: InfoValue[bool], *, true_reason: str, false_reason: str) -> DecisionResult:
    if value.kind is InfoKind.ERROR:
        return DecisionResult(DecisionState.ERROR, f'{true_reason}_INPUT_ERROR')
    if value.kind is InfoKind.UNKNOWN:
        return DecisionResult(DecisionState.UNKNOWN, f'{true_reason}_INPUT_UNKNOWN')
    if value.kind in (InfoKind.NONE, InfoKind.NA):
        return DecisionResult(DecisionState.NA, f'{true_reason}_INPUT_NA')
    return DecisionResult(DecisionState.PASS if value.value else DecisionState.FAIL, true_reason if value.value else false_reason)

def _entry_thesis_failure(position: StrategyPositionSnapshot, new_adverse_pivot: StructuralPivot | None, *, information_cutoff: int, theta_progress: Fraction) -> DecisionResult:
    if new_adverse_pivot is None:
        return DecisionResult(DecisionState.NA, 'NO_NEW_ADVERSE_PIVOT_FOR_ENTRY_THESIS')
    p = new_adverse_pivot
    e = position.entry
    if p.confirmed_at > information_cutoff:
        return DecisionResult(DecisionState.ERROR, 'FUTURE_CONFIRMED_ENTRY_THESIS_PIVOT_FORBIDDEN')
    if p.symbol != e.symbol or p.timeframe_ms != e.risk_anchor_timeframe_ms or p.layer is not e.risk_anchor_layer:
        return DecisionResult(DecisionState.FAIL, 'ENTRY_THESIS_PIVOT_NOT_CORRESPONDING_STRUCTURE_LAYER')
    if p.canonical_segment_id != e.canonical_segment_id:
        return DecisionResult(DecisionState.UNKNOWN, 'ENTRY_THESIS_CONTINUITY_BROKEN')
    if p.confirmed_at <= e.risk_anchor_confirmed_at:
        return DecisionResult(DecisionState.FAIL, 'ENTRY_THESIS_PIVOT_NOT_CAUSALLY_LATER_THAN_RISK_ANCHOR')
    expected = PivotType.LOW if e.direction is TrendDirection.LONG else PivotType.HIGH
    if p.pivot_type is not expected:
        return DecisionResult(DecisionState.FAIL, 'ENTRY_THESIS_PIVOT_NOT_ADVERSE_TYPE')
    delta = (p.extreme_price - e.risk_anchor_price) / e.risk_anchor_scale
    failed = delta < -theta_progress if e.direction is TrendDirection.LONG else delta > theta_progress
    return DecisionResult(DecisionState.PASS if failed else DecisionState.FAIL, 'ENTRY_THESIS_MATERIAL_ADVERSE_PROGRESS_CONFIRMED' if failed else 'ENTRY_THESIS_MATERIAL_ADVERSE_PROGRESS_NOT_CONFIRMED', provenance={'normalized_delta': str(delta), 'theta_progress': str(theta_progress), 'source_truth': 'D2_CONFIRMED_PRICE_STRUCTURE'})

def _management_structure_failure(position: StrategyPositionSnapshot, new_adverse_pivot: StructuralPivot | None, *, theta_progress: Fraction) -> DecisionResult:
    reference = position.latest_qualified_protective_pivot
    if reference is None:
        return DecisionResult(DecisionState.NA, 'NO_QUALIFIED_PROTECTIVE_PIVOT_MANAGEMENT_FAILURE_NA')
    if new_adverse_pivot is None:
        return DecisionResult(DecisionState.NA, 'NO_NEW_ADVERSE_PIVOT_FOR_MANAGEMENT_FAILURE')
    try:
        relation = same_type_progress(reference, new_adverse_pivot, theta_progress)
    except ValueError as exc:
        if 'cross-gap' in str(exc):
            return DecisionResult(DecisionState.UNKNOWN, 'MANAGEMENT_STRUCTURE_CONTINUITY_BROKEN')
        return DecisionResult(DecisionState.FAIL, f'MANAGEMENT_STRUCTURE_PIVOT_NOT_COMPARABLE:{exc}')
    failed = relation is ProgressRelation.MATERIAL_ADVANCE_DOWN if position.entry.direction is TrendDirection.LONG else relation is ProgressRelation.MATERIAL_ADVANCE_UP
    return DecisionResult(DecisionState.PASS if failed else DecisionState.FAIL, 'MANAGEMENT_STRUCTURE_MATERIAL_ADVERSE_PROGRESS_CONFIRMED' if failed else 'MANAGEMENT_STRUCTURE_FAILURE_NOT_CONFIRMED', provenance={'progress_relation': relation.value, 'source_truth': 'D2_CONFIRMED_PRICE_STRUCTURE'})

def _trend_end_decision(evidence: TrendEpisodeEndEvidence) -> DecisionResult:
    if evidence.cause is TrendEpisodeEndCause.GAP:
        return DecisionResult(DecisionState.NA, 'CANONICAL_GAP_IS_NOT_TREND_EPISODE_END')
    if evidence.cause is TrendEpisodeEndCause.STRUCTURAL_FAILURE:
        return DecisionResult(DecisionState.NA, 'STRUCTURAL_FAILURE_USES_MARKET_STRUCTURAL_FAILURE_PRIMARY_REASON')
    if evidence.cause is TrendEpisodeEndCause.UNKNOWN:
        return DecisionResult(DecisionState.UNKNOWN, 'TREND_EPISODE_END_CAUSE_UNKNOWN')
    if evidence.cause is TrendEpisodeEndCause.NONE:
        return DecisionResult(DecisionState.FAIL, 'TREND_EPISODE_NOT_ENDED')
    return _bool_decision(evidence.ended, true_reason='AUTHORIZED_NONSTRUCTURAL_TREND_EPISODE_END_CONFIRMED', false_reason='AUTHORIZED_NONSTRUCTURAL_TREND_EPISODE_END_NOT_PRESENT')

def _exit_candidate(evidence: ExitCandidateEvidence) -> DecisionResult:
    values = (evidence.management_anchor_true_break, evidence.entry_risk_anchor_wrong_side_close)
    if any((v.kind is InfoKind.ERROR for v in values)):
        return DecisionResult(DecisionState.ERROR, 'EXIT_CANDIDATE_INPUT_ERROR')
    if any((v.value is True for v in values)):
        return DecisionResult(DecisionState.PASS, 'SERIOUS_NONTERMINAL_ADVERSE_EVIDENCE_ONLY')
    if any((v.kind is InfoKind.UNKNOWN for v in values)):
        return DecisionResult(DecisionState.UNKNOWN, 'EXIT_CANDIDATE_INPUT_UNKNOWN')
    return DecisionResult(DecisionState.FAIL, 'NO_EXIT_CANDIDATE_EVIDENCE')

def evaluate_exit(position: StrategyPositionSnapshot, *, information_cutoff: int, new_adverse_pivot: StructuralPivot | None, protected_intermediate_structure_failed: InfoValue[bool], trend_episode_end: TrendEpisodeEndEvidence, canonical_continuity_intact: InfoValue[bool], hard_protection: HardProtectionEvidence, exit_candidate_evidence: ExitCandidateEvidence, parameters: D6ParameterView) -> ExitEvaluation:
    if hard_protection.triggered.value is True:
        if hard_protection.real_event_time is not None and hard_protection.real_event_time > information_cutoff:
            err = DecisionResult(DecisionState.ERROR, 'FUTURE_HARD_PROTECTION_EXECUTION_EVIDENCE_FORBIDDEN')
            return ExitEvaluation(err, None, err, err, err, err, _exit_candidate(exit_candidate_evidence), False)
        exit_id = deterministic_id('D6-TRADE-EXIT-HARD-PROTECTION', position.position_id, hard_protection.execution_event_id)
        record = TradeExitRecord(exit_id=exit_id, position_id=position.position_id, primary_reason=StrategyExitReason.HARD_RISK_STOP, source=ExitSource.EXECUTION_HARD_PROTECTION, strategy_information_cutoff=None, real_event_time=hard_protection.real_event_time, concurrent_exit_conditions=(StrategyExitReason.HARD_RISK_STOP,), supporting_trend_episode_ended=False, execution_evidence_id=hard_protection.execution_event_id)
        na = DecisionResult(DecisionState.NA, 'TRADE_ALREADY_TERMINATED_BY_EARLIER_HARD_PROTECTION')
        return ExitEvaluation(DecisionResult(DecisionState.PASS, 'HARD_PROTECTION_ALREADY_TERMINATED_TRADE'), record, na, na, na, na, _exit_candidate(exit_candidate_evidence), degraded_protective=False)
    if canonical_continuity_intact.kind is InfoKind.KNOWN and canonical_continuity_intact.value is False:
        unknown = DecisionResult(DecisionState.UNKNOWN, 'CANONICAL_CONTINUITY_GAP_DEGRADED_PROTECTIVE_NO_MARKET_FAILURE')
        return ExitEvaluation(unknown, None, unknown, unknown, DecisionResult(DecisionState.NA, 'GAP_NOT_MARKET_STRUCTURAL_FAILURE'), DecisionResult(DecisionState.NA, 'GAP_NOT_TREND_EPISODE_END'), _exit_candidate(exit_candidate_evidence), degraded_protective=True)
    entry_failure = _entry_thesis_failure(position, new_adverse_pivot, information_cutoff=information_cutoff, theta_progress=parameters.theta_progress)
    management_failure = _management_structure_failure(position, new_adverse_pivot, theta_progress=parameters.theta_progress)
    market_failure = _bool_decision(protected_intermediate_structure_failed, true_reason='B2_PROTECTED_INTERMEDIATE_STRUCTURE_FAILURE_CONFIRMED', false_reason='B2_PROTECTED_INTERMEDIATE_STRUCTURE_INTACT')
    trend_end = _trend_end_decision(trend_episode_end)
    exit_candidate = _exit_candidate(exit_candidate_evidence)
    passed: list[StrategyExitReason] = []
    if market_failure.state is DecisionState.PASS:
        passed.append(StrategyExitReason.MARKET_STRUCTURAL_FAILURE)
    if trend_end.state is DecisionState.PASS:
        passed.append(StrategyExitReason.TREND_EPISODE_END)
    if entry_failure.state is DecisionState.PASS:
        passed.append(StrategyExitReason.ENTRY_THESIS_FAILURE)
    if management_failure.state is DecisionState.PASS:
        passed.append(StrategyExitReason.MANAGEMENT_STRUCTURE_FAILURE)
    if not passed:
        if any((x.state is DecisionState.ERROR for x in (entry_failure, management_failure, market_failure, trend_end))):
            overall = DecisionResult(DecisionState.ERROR, 'EXIT_EVALUATION_HAS_ERROR_INPUT')
        elif any((x.state is DecisionState.UNKNOWN for x in (entry_failure, management_failure, market_failure, trend_end))):
            overall = DecisionResult(DecisionState.UNKNOWN, 'EXIT_EVALUATION_HAS_UNKNOWN_INPUT')
        else:
            overall = DecisionResult(DecisionState.FAIL, 'NO_AUTHORITATIVE_EXIT_PREDICATE_CONFIRMED')
        return ExitEvaluation(overall, None, entry_failure, management_failure, market_failure, trend_end, exit_candidate, False)
    primary = next((reason for reason in STRATEGY_EXIT_PRECEDENCE if reason in passed))
    supporting_ended = trend_episode_end.ended.kind is InfoKind.KNOWN and trend_episode_end.ended.value is True or market_failure.state is DecisionState.PASS
    exit_id = deterministic_id('D6-STRATEGY-EXIT', position.position_id, str(information_cutoff), primary.value)
    record = TradeExitRecord(exit_id=exit_id, position_id=position.position_id, primary_reason=primary, source=ExitSource.STRATEGY_CLOSED_BAR, strategy_information_cutoff=information_cutoff, real_event_time=None, concurrent_exit_conditions=tuple((reason for reason in STRATEGY_EXIT_PRECEDENCE if reason in passed)), supporting_trend_episode_ended=supporting_ended, execution_evidence_id=None)
    return ExitEvaluation(DecisionResult(DecisionState.PASS, 'STRATEGY_EXIT_FROZEN_AT_CAUSAL_CUTOFF'), record, entry_failure, management_failure, market_failure, trend_end, exit_candidate, False)

# --- ORIGINAL d6_position_execution/execution_interface.py ---
from dataclasses import replace

def create_execution_intent_interface(*, entry_ready_id: str, strategy_signal_cutoff: int, status: ExecutionStatus, status_event_id: str, observed_at: int) -> ExecutionIntentSnapshot:
    """Create a non-ordering execution-state interface. No exchange side effect exists here."""
    return ExecutionIntentSnapshot(execution_intent_id=deterministic_id('D6-EXECUTION-INTENT', entry_ready_id), entry_ready_id=entry_ready_id, strategy_signal_cutoff=strategy_signal_cutoff, status=status, status_event_id=status_event_id, observed_at=observed_at)

def transition_execution_status(prior: ExecutionIntentSnapshot, *, status: ExecutionStatus, status_event_id: str, observed_at: int) -> ExecutionIntentSnapshot:
    if observed_at < prior.observed_at:
        raise ValueError('execution status cannot backdate before prior observation')
    return replace(prior, status=status, status_event_id=status_event_id, observed_at=observed_at)

def reconcile_after_strategy_exit(exit_record: TradeExitRecord, state: ReconciliationState) -> ReconciliationState:
    if state.strategy_exit_id != exit_record.exit_id:
        raise ValueError('reconciliation lineage must reference frozen Strategy/Trade exit')
    return state

# --- ORIGINAL d6_position_execution/engine.py ---
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class D6CutoffInput:
    information_cutoff: int
    position: StrategyPositionSnapshot
    protective_pivot_evidence: ProtectivePivotEvidence
    new_adverse_pivot: StructuralPivot | None
    protected_intermediate_structure_failed: InfoValue[bool]
    supporting_trend_episode_end: TrendEpisodeEndEvidence
    canonical_continuity_intact: InfoValue[bool]
    hard_protection: HardProtectionEvidence
    exit_candidate_evidence: ExitCandidateEvidence
    parameters: D6ParameterView

def update_010(inp: D6CutoffInput) -> D6CutoffView:
    if inp.position.mode is PositionMode.CLOSED:
        raise ValueError('UPDATE-010 cannot manage a closed Position')
    qpp = qualify_protective_pivot(inp.position, inp.protective_pivot_evidence, information_cutoff=inp.information_cutoff, parameters=inp.parameters)
    management_position = inp.position
    if qpp.pivot is not None:
        prior = inp.position.latest_qualified_protective_pivot
        if prior is None or qpp.pivot.confirmed_at > prior.confirmed_at:
            management_position = replace(inp.position, latest_qualified_protective_pivot=qpp.pivot)
    exit_eval = evaluate_exit(management_position, information_cutoff=inp.information_cutoff, new_adverse_pivot=inp.new_adverse_pivot, protected_intermediate_structure_failed=inp.protected_intermediate_structure_failed, trend_episode_end=inp.supporting_trend_episode_end, canonical_continuity_intact=inp.canonical_continuity_intact, hard_protection=inp.hard_protection, exit_candidate_evidence=inp.exit_candidate_evidence, parameters=inp.parameters)
    if exit_eval.exit_record is not None:
        mode = PositionMode.CLOSED
    elif exit_eval.degraded_protective:
        mode = PositionMode.DEGRADED_PROTECTIVE
    else:
        mode = PositionMode.ACTIVE
    return D6CutoffView(information_cutoff=inp.information_cutoff, position_id=inp.position.position_id, position_mode=mode, qualified_protective_pivot=qpp, exit_evaluation=exit_eval, new_risk_blocked=mode is PositionMode.DEGRADED_PROTECTIVE)

# --- ORIGINAL d6_position_execution/cutoff_contract.py ---
"""WP6 cutoff ownership contract.

Authorized scope:
- UPDATE-010 existing-position management / Strategy Exit
- non-ordering Strategy/execution boundary interfaces

Not implemented here:
- UPDATE-014 same-cutoff orchestration
- UPDATE-015 portfolio allocation
- full UPDATE-000..016 orchestrator
"""
D6_OWNED_UPDATE_STEPS = ('UPDATE-010',)
FORBIDDEN_ORCHESTRATION_STEPS = ('UPDATE-014', 'UPDATE-015')

# --- ORIGINAL ledger/events.py ---
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class EventEnvelope:
    event_id: str
    strategy_id: str
    spec_version: str
    parameter_snapshot_id: str
    symbol: str
    information_cutoff: int
    event_type: str
    source: str
    payload_json: str
    prior_state_ref: str | None = None
    canonical_segment_id: str | None = None
    event_channel: str = 'STRATEGY'
    transaction_id: str | None = None
    update_step: str | None = None

def make_event(*, strategy_id: str, parameter_snapshot_id: str, symbol: str, information_cutoff: int, event_type: str, source: str, payload: Any, prior_state_ref: str | None=None, canonical_segment_id: str | None=None, event_channel: str='STRATEGY', transaction_id: str | None=None, update_step: str | None=None) -> EventEnvelope:
    payload_json = canonical_json(payload)
    event_id = deterministic_id('event', strategy_id, SPEC_VERSION, parameter_snapshot_id, symbol, information_cutoff, event_type, source, payload_json, prior_state_ref, canonical_segment_id, event_channel, transaction_id, update_step)
    return EventEnvelope(event_id=event_id, strategy_id=strategy_id, spec_version=SPEC_VERSION, parameter_snapshot_id=parameter_snapshot_id, symbol=symbol, information_cutoff=information_cutoff, event_type=event_type, source=source, payload_json=payload_json, prior_state_ref=prior_state_ref, canonical_segment_id=canonical_segment_id, event_channel=event_channel, transaction_id=transaction_id, update_step=update_step)

# --- ORIGINAL ledger/append_only_store.py ---
class AppendOnlyViolation(RuntimeError):
    pass

class AppendOnlyLedger:

    def __init__(self) -> None:
        self._events: list[EventEnvelope] = []
        self._ids: set[str] = set()

    def append(self, event: EventEnvelope) -> None:
        if event.event_id in self._ids:
            raise AppendOnlyViolation(f'Event ID already appended: {event.event_id}')
        self._events.append(event)
        self._ids.add(event.event_id)

    def append_batch_atomic(self, events: tuple[EventEnvelope, ...]) -> None:
        incoming = [e.event_id for e in events]
        if len(incoming) != len(set(incoming)):
            raise AppendOnlyViolation('Duplicate Event ID inside atomic batch')
        collision = next((eid for eid in incoming if eid in self._ids), None)
        if collision is not None:
            raise AppendOnlyViolation(f'Event ID already appended: {collision}')
        self._events.extend(events)
        self._ids.update(incoming)

    def snapshot(self) -> tuple[EventEnvelope, ...]:
        return tuple(self._events)

# --- ORIGINAL runtime_guards/ambiguity.py ---
class AmbiguityStop(RuntimeError):
    marker = 'STOP_AND_REPORT_AMBIGUITY'

def stop_and_report_ambiguity(detail: str) -> None:
    raise AmbiguityStop(f'{AmbiguityStop.marker}: {detail}')

# --- ORIGINAL runtime_guards/namespace_guard.py ---
V2_NAMESPACE_PREFIX = 'tac_v2_rc1'
FORBIDDEN_LEGACY_MARKERS = ('version_c', 'tac_version_c')

class NamespaceViolation(RuntimeError):
    pass

def require_v2_namespace(namespace: str) -> None:
    lowered = namespace.lower()
    if any((marker in lowered for marker in FORBIDDEN_LEGACY_MARKERS)):
        raise NamespaceViolation('Legacy Version C namespace is forbidden as v2 runtime fallback')
    if not namespace.startswith(V2_NAMESPACE_PREFIX):
        raise NamespaceViolation(f'Namespace must start with {V2_NAMESPACE_PREFIX!r}')

# --- ORIGINAL runtime_guards/parameter_guard.py ---
class RuntimeEligibilityError(RuntimeError):
    pass

def unresolved_slots(snapshot: ParameterSnapshot) -> tuple[str, ...]:
    return tuple((name for name, slot in sorted(snapshot.slots.items()) if slot.state is not ParameterState.FROZEN))

def require_runtime_usable(snapshot: ParameterSnapshot) -> None:
    unresolved = unresolved_slots(snapshot)
    if unresolved or not snapshot.complete_strategy_parameter_snapshot or (not snapshot.runtime_usable):
        raise RuntimeEligibilityError('RUNTIME_NOT_USABLE: incomplete authorized parameter snapshot; unresolved=' + ','.join(unresolved))

# --- ORIGINAL cutoff_engine/types.py ---
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

class UpdateStep(str, Enum):
    UPDATE_000 = 'UPDATE-000'
    UPDATE_001 = 'UPDATE-001'
    UPDATE_002 = 'UPDATE-002'
    UPDATE_003 = 'UPDATE-003'
    UPDATE_004 = 'UPDATE-004'
    UPDATE_005 = 'UPDATE-005'
    UPDATE_006 = 'UPDATE-006'
    UPDATE_007 = 'UPDATE-007'
    UPDATE_008 = 'UPDATE-008'
    UPDATE_009 = 'UPDATE-009'
    UPDATE_010 = 'UPDATE-010'
    UPDATE_011 = 'UPDATE-011'
    UPDATE_012 = 'UPDATE-012'
    UPDATE_013 = 'UPDATE-013'
    UPDATE_014 = 'UPDATE-014'
    UPDATE_015 = 'UPDATE-015'
    UPDATE_016 = 'UPDATE-016'
UPDATE_ORDER: tuple[UpdateStep, ...] = tuple((UpdateStep(f'UPDATE-{i:03d}') for i in range(17)))

class DomainOwner(str, Enum):
    ORCHESTRATOR = 'ORCHESTRATOR'
    CANONICAL_DATA = 'CANONICAL_DATA'
    D1_DATA_MATH = 'D1_DATA_MATH'
    D2_MARKET_STATE = 'D2_MARKET_STATE'
    D3_BOUNDARY_INTELLIGENCE = 'D3_BOUNDARY_INTELLIGENCE'
    D4_OPPORTUNITY_DECISION = 'D4_OPPORTUNITY_DECISION'
    D5_RISK = 'D5_RISK'
    D6_STRATEGY = 'D6_STRATEGY'
    D6_EXECUTION = 'D6_EXECUTION'
    PORTFOLIO_BOUNDARY = 'PORTFOLIO_BOUNDARY'
    LEDGER = 'LEDGER'
EXPECTED_OWNER: Mapping[UpdateStep, DomainOwner] = MappingProxyType({UpdateStep.UPDATE_000: DomainOwner.ORCHESTRATOR, UpdateStep.UPDATE_001: DomainOwner.CANONICAL_DATA, UpdateStep.UPDATE_002: DomainOwner.D3_BOUNDARY_INTELLIGENCE, UpdateStep.UPDATE_003: DomainOwner.D1_DATA_MATH, UpdateStep.UPDATE_004: DomainOwner.D1_DATA_MATH, UpdateStep.UPDATE_005: DomainOwner.D2_MARKET_STATE, UpdateStep.UPDATE_006: DomainOwner.D2_MARKET_STATE, UpdateStep.UPDATE_007: DomainOwner.D3_BOUNDARY_INTELLIGENCE, UpdateStep.UPDATE_008: DomainOwner.D3_BOUNDARY_INTELLIGENCE, UpdateStep.UPDATE_009: DomainOwner.D2_MARKET_STATE, UpdateStep.UPDATE_010: DomainOwner.D6_STRATEGY, UpdateStep.UPDATE_011: DomainOwner.D4_OPPORTUNITY_DECISION, UpdateStep.UPDATE_012: DomainOwner.D5_RISK, UpdateStep.UPDATE_013: DomainOwner.D4_OPPORTUNITY_DECISION, UpdateStep.UPDATE_014: DomainOwner.ORCHESTRATOR, UpdateStep.UPDATE_015: DomainOwner.PORTFOLIO_BOUNDARY, UpdateStep.UPDATE_016: DomainOwner.LEDGER})
NEW_RISK_STEPS = frozenset({UpdateStep.UPDATE_011, UpdateStep.UPDATE_012, UpdateStep.UPDATE_013, UpdateStep.UPDATE_014, UpdateStep.UPDATE_015})

class StageState(str, Enum):
    PASS = 'PASS'
    BLOCKED = 'BLOCKED'
    SKIPPED = 'SKIPPED'
    NA = 'N/A'
    ERROR = 'ERROR'

class EventChannel(str, Enum):
    STRATEGY = 'STRATEGY'
    EXECUTION = 'EXECUTION'
    RECONCILIATION = 'RECONCILIATION'

@dataclass(frozen=True)
class ProposedEvent:
    event_type: str
    source: str
    payload_json: str
    channel: EventChannel = EventChannel.STRATEGY
    prior_state_ref: str | None = None
    canonical_segment_id: str | None = None
    admission_tag: str | None = None

    @classmethod
    def from_payload(cls, *, event_type: str, source: str, payload: Any, channel: EventChannel=EventChannel.STRATEGY, prior_state_ref: str | None=None, canonical_segment_id: str | None=None, admission_tag: str | None=None) -> 'ProposedEvent':
        return cls(event_type=event_type, source=source, payload_json=canonical_json(payload), channel=channel, prior_state_ref=prior_state_ref, canonical_segment_id=canonical_segment_id, admission_tag=admission_tag)

@dataclass(frozen=True)
class StageResult:
    owner: DomainOwner
    state: StageState
    reason: str
    payload_json: str
    proposed_events: tuple[ProposedEvent, ...] = ()
    blocks_new_risk: bool = False
    information_cutoff: int | None = None
    canonical_segment_id: str | None = None
    strategy_exit_created: bool = False
    entry_ready_created: bool = False
    entry_ready_ref: str | None = None
    runtime_usable_signal: bool = False
    next_boundary_snapshot_refs: tuple[str, ...] = ()
    next_interaction_control_refs: tuple[str, ...] = ()
    next_strategy_state_refs: tuple[str, ...] = ()

    @classmethod
    def make(cls, *, owner: DomainOwner, state: StageState=StageState.PASS, reason: str='OK', payload: Any=None, proposed_events: tuple[ProposedEvent, ...]=(), blocks_new_risk: bool=False, information_cutoff: int | None=None, canonical_segment_id: str | None=None, strategy_exit_created: bool=False, entry_ready_created: bool=False, entry_ready_ref: str | None=None, runtime_usable_signal: bool=False, next_boundary_snapshot_refs: tuple[str, ...]=(), next_interaction_control_refs: tuple[str, ...]=(), next_strategy_state_refs: tuple[str, ...]=()) -> 'StageResult':
        return cls(owner=owner, state=state, reason=reason, payload_json=canonical_json(payload), proposed_events=tuple(proposed_events), blocks_new_risk=blocks_new_risk, information_cutoff=information_cutoff, canonical_segment_id=canonical_segment_id, strategy_exit_created=strategy_exit_created, entry_ready_created=entry_ready_created, entry_ready_ref=entry_ready_ref, runtime_usable_signal=runtime_usable_signal, next_boundary_snapshot_refs=tuple(next_boundary_snapshot_refs), next_interaction_control_refs=tuple(next_interaction_control_refs), next_strategy_state_refs=tuple(next_strategy_state_refs))

@dataclass(frozen=True)
class StageEnvelope:
    step: UpdateStep
    owner: DomainOwner
    state: StageState
    reason: str
    input_digest: str
    output_digest: str
    payload_json: str

@dataclass(frozen=True)
class CausalObserverSnapshot:
    snapshot_id: str
    symbol: str
    source_information_cutoff: int
    eligible_from_open_time: int
    boundary_snapshot_refs: tuple[str, ...]
    interaction_control_refs: tuple[str, ...]
    strategy_state_refs: tuple[str, ...]

def make_causal_observer_snapshot(*, symbol: str, source_information_cutoff: int, eligible_from_open_time: int, boundary_snapshot_refs: tuple[str, ...]=(), interaction_control_refs: tuple[str, ...]=(), strategy_state_refs: tuple[str, ...]=()) -> CausalObserverSnapshot:
    boundary = tuple(sorted(set(boundary_snapshot_refs)))
    interaction = tuple(sorted(set(interaction_control_refs)))
    strategy = tuple(sorted(set(strategy_state_refs)))
    sid = deterministic_id('observer_snapshot', symbol, source_information_cutoff, eligible_from_open_time, boundary, interaction, strategy)
    return CausalObserverSnapshot(snapshot_id=sid, symbol=symbol, source_information_cutoff=source_information_cutoff, eligible_from_open_time=eligible_from_open_time, boundary_snapshot_refs=boundary, interaction_control_refs=interaction, strategy_state_refs=strategy)

@dataclass(frozen=True)
class SymbolCutoffInput:
    strategy_id: str
    parameter_snapshot_id: str
    observer_bar: CanonicalBar
    prebar_snapshot: CausalObserverSnapshot
    fixture_class: str | None = None

    @property
    def symbol(self) -> str:
        return self.observer_bar.symbol

@dataclass(frozen=True)
class StageContext:
    transaction_id: str
    step: UpdateStep
    symbol_input: SymbolCutoffInput
    information_cutoff: int | None
    canonical_segment_id: str | None
    new_risk_blocked: bool
    prior_envelopes: tuple[StageEnvelope, ...]
    prior_results: Mapping[UpdateStep, StageResult] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, 'prior_results', MappingProxyType(dict(self.prior_results)))

class TransactionTerminal(str, Enum):
    COMMITTED = 'COMMITTED'
    COMMITTED_WITH_BLOCKS = 'COMMITTED_WITH_BLOCKS'
    ABORTED_ERROR = 'ABORTED_ERROR'
    ABORTED_AMBIGUITY = 'ABORTED_AMBIGUITY'

@dataclass(frozen=True)
class PortfolioCandidate:
    symbol: str
    entry_ready_ref: str
    transaction_id: str

@dataclass(frozen=True)
class PortfolioBoundaryResult:
    state: StageState
    reason: str
    candidates: tuple[PortfolioCandidate, ...]
    allocation: None = None
    port_007_frozen: bool = False

    def __post_init__(self) -> None:
        if self.allocation is not None or self.port_007_frozen:
            raise ValueError('WP7 forbids portfolio allocation or PORT-007 freeze')

@dataclass(frozen=True)
class SymbolTransactionResult:
    transaction_id: str
    symbol: str
    information_cutoff: int | None
    canonical_segment_id: str | None
    terminal: TransactionTerminal
    new_risk_blocked: bool
    stages: tuple[StageEnvelope, ...]
    next_bar_snapshot: CausalObserverSnapshot | None
    appended_event_ids: tuple[str, ...]
    entry_ready_admitted_by_update014: bool
    error_reason: str | None = None

@dataclass(frozen=True)
class CutoffBatchResult:
    batch_id: str
    terminal: TransactionTerminal
    portfolio_boundary: PortfolioBoundaryResult | None
    symbol_results: tuple[SymbolTransactionResult, ...]
    ledger_event_ids: tuple[str, ...]

# --- ORIGINAL cutoff_engine/adapters.py ---
from dataclasses import dataclass
from typing import Callable, Mapping, Protocol

class StageAdapter(Protocol):

    def __call__(self, context: StageContext) -> StageResult:
        ...
REQUIRED_ADAPTER_STEPS: tuple[UpdateStep, ...] = tuple((UpdateStep(f'UPDATE-{i:03d}') for i in range(1, 14)))

@dataclass(frozen=True)
class AdapterRegistry:
    adapters: Mapping[UpdateStep, StageAdapter]

    def __post_init__(self) -> None:
        missing = [s.value for s in REQUIRED_ADAPTER_STEPS if s not in self.adapters]
        extra = [s.value for s in self.adapters if s not in REQUIRED_ADAPTER_STEPS]
        if missing or extra:
            stop_and_report_ambiguity(f'WP7 adapter registry must exactly cover UPDATE-001..013; missing={missing}; extra={extra}')

    def run(self, step: UpdateStep, context: StageContext) -> StageResult:
        adapter = self.adapters[step]
        result = adapter(context)
        expected = EXPECTED_OWNER[step]
        if result.owner is not expected:
            raise RuntimeError(f'WRITER_FIREWALL_VIOLATION step={step.value} expected={expected.value} got={result.owner.value}')
        return result

# --- ORIGINAL cutoff_engine/portfolio_boundary.py ---
PORT_007_STATE = 'OPEN_OPERATIONAL_OPEN_RESEARCH_UNFROZEN'

def evaluate_portfolio_boundary(candidates: tuple[PortfolioCandidate, ...]) -> PortfolioBoundaryResult:
    ordered = tuple(sorted(candidates, key=lambda c: (c.symbol, c.entry_ready_ref, c.transaction_id)))
    return PortfolioBoundaryResult(state=StageState.BLOCKED, reason='PORT007_UNRESOLVED_PRODUCTION_ALLOCATION_BLOCKED', candidates=ordered, allocation=None, port_007_frozen=False)

# --- ORIGINAL cutoff_engine/ledger_bridge.py ---
import json

def materialize_event(proposed: ProposedEvent, *, strategy_id: str, parameter_snapshot_id: str, symbol: str, information_cutoff: int, transaction_id: str, update_step: str) -> EventEnvelope:
    return make_event(strategy_id=strategy_id, parameter_snapshot_id=parameter_snapshot_id, symbol=symbol, information_cutoff=information_cutoff, event_type=proposed.event_type, source=proposed.source, payload=json.loads(proposed.payload_json), prior_state_ref=proposed.prior_state_ref, canonical_segment_id=proposed.canonical_segment_id, event_channel=proposed.channel.value, transaction_id=transaction_id, update_step=update_step)

def append_external_execution_outcome(ledger: AppendOnlyLedger, *, strategy_id: str, parameter_snapshot_id: str, symbol: str, information_cutoff: int, event_type: str, payload: object, strategy_signal_ref: str, channel: EventChannel=EventChannel.EXECUTION) -> EventEnvelope:
    if channel is EventChannel.STRATEGY:
        raise ValueError('External execution bridge may not append Strategy-channel truth')
    event = make_event(strategy_id=strategy_id, parameter_snapshot_id=parameter_snapshot_id, symbol=symbol, information_cutoff=information_cutoff, event_type=event_type, source='D6_EXECUTION_INTERFACE', payload={'strategy_signal_ref': strategy_signal_ref, 'outcome': payload}, event_channel=channel.value, prior_state_ref=strategy_signal_ref, update_step='EXECUTION_INTERFACE')
    ledger.append(event)
    return event

# --- ORIGINAL cutoff_engine/engine.py ---
import hashlib
from dataclasses import dataclass
from typing import Iterable

def _digest(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode('utf-8')).hexdigest()

def _stage_envelope(step: UpdateStep, result: StageResult, *, context_digest: str) -> StageEnvelope:
    return StageEnvelope(step=step, owner=result.owner, state=result.state, reason=result.reason, input_digest=context_digest, output_digest=_digest(result), payload_json=result.payload_json)

def _skip_result(step: UpdateStep, reason: str) -> StageResult:
    return StageResult.make(owner=EXPECTED_OWNER[step], state=StageState.SKIPPED, reason=reason, payload={'blocked': True, 'step': step.value})

@dataclass
class _ProvisionalSymbol:
    symbol_input: SymbolCutoffInput
    transaction_id: str
    information_cutoff: int | None
    canonical_segment_id: str | None
    new_risk_blocked: bool
    stages: list[StageEnvelope]
    results: dict[UpdateStep, StageResult]
    buffered_events: list[tuple[UpdateStep, ProposedEvent]]
    entry_ready_admitted: bool = False
    terminal: TransactionTerminal | None = None
    error_reason: str | None = None

class DeterministicCutoffEngine:
    """WP7 orchestration only; it never computes D1-D6 market semantics itself."""

    def __init__(self, *, adapters: AdapterRegistry, ledger: AppendOnlyLedger, runtime_usable: bool=False) -> None:
        if runtime_usable:
            raise ValueError('WP7 current incomplete parameter state forbids runtime_usable=True')
        self.adapters = adapters
        self.ledger = ledger
        self.runtime_usable = False

    def _validate_prebar(self, item: SymbolCutoffInput) -> None:
        snap = item.prebar_snapshot
        bar = item.observer_bar
        if snap.symbol != bar.symbol:
            stop_and_report_ambiguity('prebar snapshot symbol mismatch')
        if snap.eligible_from_open_time > bar.open_time:
            stop_and_report_ambiguity('prebar snapshot is not causally eligible for observer bar')
        if snap.source_information_cutoff >= bar.close_time:
            stop_and_report_ambiguity('same/future cutoff snapshot cannot be used for bar-t geometry')

    def _run_until_014(self, item: SymbolCutoffInput) -> _ProvisionalSymbol:
        self._validate_prebar(item)
        txid = deterministic_id('cutoff_tx', item.strategy_id, item.parameter_snapshot_id, item.symbol, item.observer_bar.open_time, item.observer_bar.close_time, item.prebar_snapshot.snapshot_id, item.fixture_class)
        p = _ProvisionalSymbol(item, txid, None, None, False, [], {}, [])
        r0 = StageResult.make(owner=DomainOwner.ORCHESTRATOR, payload={'prebar_snapshot_id': item.prebar_snapshot.snapshot_id, 'boundary_snapshot_refs': item.prebar_snapshot.boundary_snapshot_refs, 'interaction_control_refs': item.prebar_snapshot.interaction_control_refs, 'strategy_state_refs': item.prebar_snapshot.strategy_state_refs}, reason='PRE_BAR_STATE_FROZEN')
        c0 = _digest({'tx': txid, 'step': UpdateStep.UPDATE_000.value, 'input': item})
        p.results[UpdateStep.UPDATE_000] = r0
        p.stages.append(_stage_envelope(UpdateStep.UPDATE_000, r0, context_digest=c0))
        try:
            for step in tuple((UpdateStep(f'UPDATE-{i:03d}') for i in range(1, 14))):
                if p.new_risk_blocked and step in NEW_RISK_STEPS:
                    result = _skip_result(step, 'CRITICAL_BLOCK_STOPS_NEW_RISK_PROCESSING')
                else:
                    ctx = StageContext(transaction_id=txid, step=step, symbol_input=item, information_cutoff=p.information_cutoff, canonical_segment_id=p.canonical_segment_id, new_risk_blocked=p.new_risk_blocked, prior_envelopes=tuple(p.stages), prior_results=p.results)
                    result = self.adapters.run(step, ctx)
                if result.runtime_usable_signal:
                    raise RuntimeError('WP7_RUNTIME_USABLE_SIGNAL_FORBIDDEN')
                if step is UpdateStep.UPDATE_001:
                    if result.information_cutoff is None:
                        raise RuntimeError('UPDATE-001 must establish information_cutoff')
                    if result.information_cutoff != item.observer_bar.close_time:
                        raise RuntimeError('UPDATE-001 information_cutoff must equal committed observer bar close_time')
                    if result.canonical_segment_id is None:
                        raise RuntimeError('UPDATE-001 must expose canonical_segment_id')
                    p.information_cutoff = result.information_cutoff
                    p.canonical_segment_id = result.canonical_segment_id
                elif result.information_cutoff is not None and result.information_cutoff != p.information_cutoff:
                    raise RuntimeError(f'CROSS_CUTOFF_STAGE_OUTPUT step={step.value}')
                if result.blocks_new_risk:
                    p.new_risk_blocked = True
                if result.state is StageState.ERROR:
                    raise RuntimeError(f'STAGE_ERROR {step.value}: {result.reason}')
                context_digest = _digest({'tx': txid, 'step': step.value, 'cutoff': p.information_cutoff, 'segment': p.canonical_segment_id, 'prior_output_digests': tuple((e.output_digest for e in p.stages))})
                p.results[step] = result
                p.stages.append(_stage_envelope(step, result, context_digest=context_digest))
                p.buffered_events.extend(((step, event) for event in result.proposed_events))
            exit_created = p.results[UpdateStep.UPDATE_010].strategy_exit_created
            entry_result = p.results[UpdateStep.UPDATE_013]
            if exit_created and entry_result.entry_ready_created:
                p.entry_ready_admitted = False
                r14 = StageResult.make(owner=DomainOwner.ORCHESTRATOR, state=StageState.BLOCKED, reason='SAME_CUTOFF_EXIT_BLOCKS_ENTRY_READY', payload={'entry_ready_ref': entry_result.entry_ready_ref, 'exit_same_cutoff': True}, blocks_new_risk=True)
                p.new_risk_blocked = True
            elif entry_result.entry_ready_created:
                p.entry_ready_admitted = True
                r14 = StageResult.make(owner=DomainOwner.ORCHESTRATOR, state=StageState.PASS, reason='ENTRY_READY_ADMITTED_BY_SAME_CUTOFF_SAFETY', payload={'entry_ready_ref': entry_result.entry_ready_ref, 'exit_same_cutoff': False})
            else:
                r14 = StageResult.make(owner=DomainOwner.ORCHESTRATOR, state=StageState.NA, reason='NO_ENTRY_READY_CANDIDATE', payload=None)
            c14 = _digest({'tx': txid, 'step': UpdateStep.UPDATE_014.value, 'u010': p.results[UpdateStep.UPDATE_010], 'u013': entry_result})
            p.results[UpdateStep.UPDATE_014] = r14
            p.stages.append(_stage_envelope(UpdateStep.UPDATE_014, r14, context_digest=c14))
            p.terminal = TransactionTerminal.COMMITTED_WITH_BLOCKS if p.new_risk_blocked else TransactionTerminal.COMMITTED
            return p
        except AmbiguityStop as exc:
            p.terminal = TransactionTerminal.ABORTED_AMBIGUITY
            p.error_reason = str(exc)
            return p
        except Exception as exc:
            p.terminal = TransactionTerminal.ABORTED_ERROR
            p.error_reason = str(exc)
            return p

    def run_cutoff_batch(self, items: Iterable[SymbolCutoffInput]) -> CutoffBatchResult:
        ordered = tuple(sorted(items, key=lambda x: x.symbol))
        if not ordered:
            stop_and_report_ambiguity('cutoff batch cannot be empty')
        if len({x.symbol for x in ordered}) != len(ordered):
            stop_and_report_ambiguity('duplicate symbol in cutoff batch')
        expected_close = ordered[0].observer_bar.close_time
        if any((x.observer_bar.close_time != expected_close for x in ordered)):
            stop_and_report_ambiguity('all symbols in UPDATE-015 batch must share information cutoff')
        batch_id = deterministic_id('cutoff_batch', expected_close, tuple(((x.symbol, x.observer_bar.open_time, x.prebar_snapshot.snapshot_id) for x in ordered)))
        before_ledger = self.ledger.snapshot()
        provisionals = [self._run_until_014(x) for x in ordered]
        fatal = next((p for p in provisionals if p.terminal in (TransactionTerminal.ABORTED_ERROR, TransactionTerminal.ABORTED_AMBIGUITY)), None)
        if fatal is not None:
            if self.ledger.snapshot() != before_ledger:
                raise RuntimeError('PARTIAL_LEDGER_COMMIT_ON_ABORT')
            results = tuple((self._final_result_without_016(p) for p in provisionals))
            return CutoffBatchResult(batch_id=batch_id, terminal=fatal.terminal or TransactionTerminal.ABORTED_ERROR, portfolio_boundary=None, symbol_results=results, ledger_event_ids=tuple((e.event_id for e in self.ledger.snapshot())))
        candidates: list[PortfolioCandidate] = []
        for p in provisionals:
            er = p.results[UpdateStep.UPDATE_013]
            if p.entry_ready_admitted and er.entry_ready_created and er.entry_ready_ref:
                candidates.append(PortfolioCandidate(p.symbol_input.symbol, er.entry_ready_ref, p.transaction_id))
        portfolio = evaluate_portfolio_boundary(tuple(candidates))
        for p in provisionals:
            r15 = StageResult.make(owner=DomainOwner.PORTFOLIO_BOUNDARY, state=StageState.BLOCKED, reason=portfolio.reason, payload={'candidate_refs': tuple(((c.symbol, c.entry_ready_ref) for c in portfolio.candidates)), 'allocation': None, 'port_007_frozen': False}, blocks_new_risk=bool(portfolio.candidates))
            c15 = _digest({'batch': batch_id, 'step': UpdateStep.UPDATE_015.value, 'portfolio': portfolio})
            p.results[UpdateStep.UPDATE_015] = r15
            p.stages.append(_stage_envelope(UpdateStep.UPDATE_015, r15, context_digest=c15))
            if portfolio.candidates:
                p.new_risk_blocked = True
                p.terminal = TransactionTerminal.COMMITTED_WITH_BLOCKS
        all_events = []
        per_symbol_event_ids: dict[str, list[str]] = {p.symbol_input.symbol: [] for p in provisionals}
        next_snaps: dict[str, CausalObserverSnapshot] = {}
        for p in provisionals:
            assert p.information_cutoff is not None
            admitted_events: list[tuple[UpdateStep, ProposedEvent]] = []
            for step, proposed in p.buffered_events:
                if proposed.admission_tag == 'ENTRY_READY' and (not p.entry_ready_admitted):
                    continue
                admitted_events.append((step, proposed))
            for step, proposed in admitted_events:
                ev = materialize_event(proposed, strategy_id=p.symbol_input.strategy_id, parameter_snapshot_id=p.symbol_input.parameter_snapshot_id, symbol=p.symbol_input.symbol, information_cutoff=p.information_cutoff, transaction_id=p.transaction_id, update_step=step.value)
                all_events.append(ev)
                per_symbol_event_ids[p.symbol_input.symbol].append(ev.event_id)
            u7 = p.results[UpdateStep.UPDATE_007]
            u8 = p.results[UpdateStep.UPDATE_008]
            u10 = p.results[UpdateStep.UPDATE_010]
            next_open = p.symbol_input.observer_bar.open_time + 15 * 60 * 1000
            next_snaps[p.symbol_input.symbol] = make_causal_observer_snapshot(symbol=p.symbol_input.symbol, source_information_cutoff=p.information_cutoff, eligible_from_open_time=next_open, boundary_snapshot_refs=u8.next_boundary_snapshot_refs, interaction_control_refs=u7.next_interaction_control_refs, strategy_state_refs=u10.next_strategy_state_refs)
        self.ledger.append_batch_atomic(tuple(all_events))
        symbol_results: list[SymbolTransactionResult] = []
        for p in provisionals:
            snap = next_snaps[p.symbol_input.symbol]
            r16 = StageResult.make(owner=DomainOwner.LEDGER, state=StageState.PASS, reason='ATOMIC_EVENT_APPEND_AND_T_PLUS_1_SNAPSHOT_FROZEN', payload={'appended_event_ids': tuple(per_symbol_event_ids[p.symbol_input.symbol]), 'next_bar_snapshot_id': snap.snapshot_id, 'eligible_from_open_time': snap.eligible_from_open_time})
            c16 = _digest({'tx': p.transaction_id, 'step': UpdateStep.UPDATE_016.value, 'events': tuple(per_symbol_event_ids[p.symbol_input.symbol]), 'snapshot': snap})
            p.results[UpdateStep.UPDATE_016] = r16
            p.stages.append(_stage_envelope(UpdateStep.UPDATE_016, r16, context_digest=c16))
            if tuple((e.step for e in p.stages)) != UPDATE_ORDER:
                raise RuntimeError('FULL_UPDATE_ORDER_VIOLATION')
            symbol_results.append(SymbolTransactionResult(transaction_id=p.transaction_id, symbol=p.symbol_input.symbol, information_cutoff=p.information_cutoff, canonical_segment_id=p.canonical_segment_id, terminal=p.terminal or TransactionTerminal.COMMITTED, new_risk_blocked=p.new_risk_blocked, stages=tuple(p.stages), next_bar_snapshot=snap, appended_event_ids=tuple(per_symbol_event_ids[p.symbol_input.symbol]), entry_ready_admitted_by_update014=p.entry_ready_admitted, error_reason=None))
        batch_terminal = TransactionTerminal.COMMITTED_WITH_BLOCKS if any((r.new_risk_blocked for r in symbol_results)) else TransactionTerminal.COMMITTED
        return CutoffBatchResult(batch_id=batch_id, terminal=batch_terminal, portfolio_boundary=portfolio, symbol_results=tuple(symbol_results), ledger_event_ids=tuple((e.event_id for e in self.ledger.snapshot())))

    def _final_result_without_016(self, p: _ProvisionalSymbol) -> SymbolTransactionResult:
        return SymbolTransactionResult(transaction_id=p.transaction_id, symbol=p.symbol_input.symbol, information_cutoff=p.information_cutoff, canonical_segment_id=p.canonical_segment_id, terminal=p.terminal or TransactionTerminal.ABORTED_ERROR, new_risk_blocked=p.new_risk_blocked, stages=tuple(p.stages), next_bar_snapshot=None, appended_event_ids=(), entry_ready_admitted_by_update014=False, error_reason=p.error_reason)

# --- ORIGINAL spec_binding.py ---
"""Exact authority bindings for the WP0/WP1/WP2/WP3/WP4/WP5/WP6/WP7 non-trading reference skeleton.

This module binds metadata only. It does not create semantic authority.
"""
SPEC_ID = 'TAC_CLEANROOM_V2'
SPEC_VERSION = '1.0-RC1'
RC1_RAW_SHA256 = '0e910d20f12e18662779f2977b83413f86569b230e9b08e0c2ad7a6c2afc29bc'
SOURCE_GITHUB_HEAD = '9ad115b6e9eb7fe9f5a45f60fc6c11004346d625'
SOURCE_GITHUB_TREE = '5f639389ec12ba774ff4d0e74d3f20693f2b7396'
POST_RC1_BINDINGS = {'tac-v2-r1-post-rc1-semantic-authority-binding-v1.json': {'github_blob_sha': '99cba11b434a92c73712f997ca5ab70ca1b5dd76', 'deterministic_content_sha256': '3fe568ae8ea082bfe88b4106cb564882737884b84626dc81c4797666b232d3a1', 'scope': 'episode leg membership + B3 zone classifier'}, 'tac-v2-r1-post-rc1-st-final-band-recurrence-semantic-authority-binding-v1.json': {'github_blob_sha': '267d2002fe3290837a220e01ce0ada2e6754e672', 'deterministic_content_sha256': '5a22d76cf9b197cf3a5c6716fe7b176dccc33a02f8a17396d92dcd3664f42473', 'scope': 'Supertrend final-band recurrence'}}
CURRENT_STAGE = 'RC1_NONTRADING_REFERENCE_IMPLEMENTATION_WP7'
RUNTIME_AUTHORIZED = False
TRADING_AUTHORIZED = False
TEST_AUTHORIZED = False
WP8_STAGE = 'RC1_NONTRADING_REFERENCE_IMPLEMENTATION_WP8_V1'
WP8_SCOPE = 'SEMANTIC_TRACEABILITY_HARNESS_SYNTHETIC_FIXTURES_ONLY'


# === BEGIN AI PRO TEST_ONLY BINDING: ORIGINAL SOURCE ABOVE IS UNMODIFIED ===
import asyncio
from datetime import datetime, timezone
from binance.strategy.runtime import node, workflow, ctx
from binance.strategy.node.capabilities.data import kline_stream
TAC_LIVE_ENABLED = 0
TEST_ONLY_NONTRADING = True
# Set only after native code/spec validation of kline_stream signatures and quotas.
NATIVE_528_PROSPECTIVE_STREAM_AUTHORIZED = False
FROZEN_528_SYMBOLS = ["0GUSDT","1000000BOBUSDT","1000000MOGUSDT","1000BONKUSDT","1000CATUSDT","1000CHEEMSUSDT","1000FLOKIUSDT","1000LUNCUSDT","1000PEPEUSDT","1000RATSUSDT","1000SATSUSDT","1000SHIBUSDT","1000XECUSDT","1INCHUSDT","1MBABYDOGEUSDT","2ZUSDT","4USDT","AAVEUSDT","ACEUSDT","ACHUSDT","ACTUSDT","ACUUSDT","ADAUSDT","AEROUSDT","AEVOUSDT","AGLDUSDT","AGTUSDT","AIAUSDT","AIGENSYNUSDT","AINUSDT","AIOTUSDT","AIOUSDT","AIXBTUSDT","AKEUSDT","AKTUSDT","ALCHUSDT","ALGOUSDT","ALICEUSDT","ALLOUSDT","ALLUSDT","ALPINEUSDT","ALTUSDT","ANIMEUSDT","ANKRUSDT","APEUSDT","API3USDT","APRUSDT","APTUSDT","ARBUSDT","ARCUSDT","ARIAUSDT","ARKMUSDT","ARKUSDT","ARPAUSDT","ARUSDT","ARXUSDT","ASRUSDT","ASTERUSDT","ASTRUSDT","ATHUSDT","ATOMUSDT","ATUSDT","AUCTIONUSDT","AUSDT","AVAAIUSDT","AVAUSDT","AVAXUSDT","AVNTUSDT","AWEUSDT","AXLUSDT","AXSUSDT","AZTECUSDT","B2USDT","BABYUSDT","BANANAS31USDT","BANANAUSDT","BANDUSDT","BANKUSDT","BANUSDT","BARDUSDT","BASEDUSDT","BASUSDT","BATUSDT","BBUSDT","BCHUSDT","BEAMXUSDT","BEATUSDT","BELUSDT","BERAUSDT","BICOUSDT","BIGTIMEUSDT","BILLUSDT","BIOUSDT","BIRBUSDT","BLESSUSDT","BLUAIUSDT","BLURUSDT","BMTUSDT","BNBUSDT","BNTUSDT","BOMEUSDT","BRETTUSDT","BREVUSDT","BROCCOLI714USDT","BROCCOLIF3BUSDT","BRUSDT","BSBUSDT","BSVUSDT","BTCDOMUSDT","BTCUSDT","BTRUSDT","BTWUSDT","BULLAUSDT","BUSDT","C98USDT","CAKEUSDT","CAPUSDT","CARVUSDT","CATIUSDT","CCUSDT","CELOUSDT","CELRUSDT","CETUSUSDT","CFGUSDT","CFXUSDT","CGPTUSDT","CHILLGUYUSDT","CHIPUSDT","CHRUSDT","CHZUSDT","CKBUSDT","CLANKERUSDT","CLOUSDT","COAIUSDT","COLLECTUSDT","COMPUSDT","COOKIEUSDT","COTIUSDT","COWUSDT","CROSSUSDT","CRVUSDT","CTKUSDT","CTRUSDT","CTSIUSDT","CUSDT","CVCUSDT","CVXUSDT","CYBERUSDT","CYSUSDT","DASHUSDT","DATAIPUSDT","DEEPUSDT","DEXEUSDT","DIAUSDT","DODOXUSDT","DOGEUSDT","DOGSUSDT","DOLOUSDT","DOODUSDT","DOSUSDT","DOTUSDT","DRIFTUSDT","DUSKUSDT","DYDXUSDT","DYMUSDT","EDENUSDT","EDGEUSDT","EDUUSDT","EGLDUSDT","EIGENUSDT","ELSAUSDT","ENAUSDT","ENJUSDT","ENSOUSDT","ENSUSDT","EPICUSDT","ERAUSDT","ESPORTSUSDT","ESPUSDT","ETCUSDT","ETHFIUSDT","ETHUSDT","ETHWUSDT","EULUSDT","EVAAUSDT","FARTCOINUSDT","FETUSDT","FFUSDT","FHEUSDT","FIDAUSDT","FIGHTUSDT","FILUSDT","FLOCKUSDT","FLOWUSDT","FLUIDUSDT","FLUXUSDT","FOGOUSDT","FOLKSUSDT","FORMUSDT","FRAXUSDT","FUSDT","GALAUSDT","GASUSDT","GENIUSUSDT","GIGGLEUSDT","GLMUSDT","GMTUSDT","GMXUSDT","GOATUSDT","GPSUSDT","GRAMUSDT","GRASSUSDT","GRIFFAINUSDT","GRTUSDT","GRVTUSDT","GTCUSDT","GUAUSDT","GUNUSDT","GUSDT","GWEIUSDT","HAEDALUSDT","HANAUSDT","HBARUSDT","HEIUSDT","HEMIUSDT","HIVEUSDT","HMSTRUSDT","HOLOUSDT","HOMEUSDT","HOTUSDT","HUMAUSDT","HUSDT","HYPERUSDT","HYPEUSDT","ICNTUSDT","ICPUSDT","IDOLUSDT","IDUSDT","ILVUSDT","IMXUSDT","INITUSDT","INJUSDT","INUSDT","INXUSDT","IOSTUSDT","IOTAUSDT","IOTXUSDT","IOUSDT","IRYSUSDT","JASMYUSDT","JCTUSDT","JELLYJELLYUSDT","JOEUSDT","JSTUSDT","JTOUSDT","JUPUSDT","KAIAUSDT","KAITOUSDT","KASUSDT","KATUSDT","KAVAUSDT","KERNELUSDT","KGENUSDT","KITEUSDT","KMNOUSDT","KNCUSDT","KOMAUSDT","KSMUSDT","LABUSDT","LAUSDT","LAYERUSDT","LDOUSDT","LIGHTUSDT","LINEAUSDT","LINKUSDT","LISTAUSDT","LITUSDT","LPTUSDT","LQTYUSDT","LSKUSDT","LTCUSDT","LUMIAUSDT","LUNA2USDT","LYNUSDT","MAGICUSDT","MAGMAUSDT","MANAUSDT","MANTAUSDT","MANTRAUSDT","MARSCOINUSDT","MASKUSDT","MAVIAUSDT","MAVUSDT","MEGAUSDT","MELANIAUSDT","MEMEUSDT","MERLUSDT","METISUSDT","METUSDT","MEUSDT","MEWUSDT","MINAUSDT","MIRAUSDT","MITOUSDT","MMTUSDT","MOCAUSDT","MONUSDT","MOODENGUSDT","MORPHOUSDT","MOVEUSDT","MOVRUSDT","MTLUSDT","MUBARAKUSDT","MUSDT","MYXUSDT","NAORISUSDT","NEARUSDT","NEIROUSDT","NEOUSDT","NEWTUSDT","NIGHTUSDT","NILUSDT","NMRUSDT","NOMUSDT","NOTUSDT","NXPCUSDT","OGNUSDT","OGUSDT","ONDOUSDT","ONEUSDT","ONGUSDT","ONTUSDT","ONUSDT","OPENUSDT","OPGUSDT","OPNUSDT","OPUSDT","ORCAUSDT","ORDERUSDT","ORDIUSDT","OUSDT","PARTIUSDT","PAXGUSDT","PENDLEUSDT","PENGUUSDT","PEOPLEUSDT","PHAROSUSDT","PHAUSDT","PIEVERSEUSDT","PIPPINUSDT","PIXELUSDT","PLAYUSDT","PLUMEUSDT","PNUTUSDT","POLUSDT","POLYXUSDT","PONSUSDT","POPCATUSDT","PORTALUSDT","POWERUSDT","POWRUSDT","PRLUSDT","PROMPTUSDT","PROMUSDT","PROVEUSDT","PTBUSDT","PUMPBTCUSDT","PUMPUSDT","PUNDIXUSDT","PYTHUSDT","QNTUSDT","QTUMUSDT","QUSDT","RAREUSDT","RAVEUSDT","RAYSOLUSDT","RECALLUSDT","REDUSDT","RENDERUSDT","RESOLVUSDT","REUSDT","REZUSDT","RIFUSDT","RIVERUSDT","RLCUSDT","ROBOUSDT","RONINUSDT","ROSEUSDT","RPLUSDT","RSRUSDT","RUNEUSDT","RVNUSDT","SAFEUSDT","SAGAUSDT","SAHARAUSDT","SANDUSDT","SANTOSUSDT","SAPIENUSDT","SCRUSDT","SEIUSDT","SENTUSDT","SFPUSDT","SHELLUSDT","SIGNUSDT","SIRENUSDT","SKLUSDT","SKRUSDT","SKYAIUSDT","SKYUSDT","SLPUSDT","SLXUSDT","SNXUSDT","SOLUSDT","SOLVUSDT","SOMIUSDT","SONICUSDT","SOONUSDT","SOPHUSDT","SPACEUSDT","SPELLUSDT","SPKUSDT","SPORTFUNUSDT","SPXUSDT","SQDUSDT","SSVUSDT","STABLEUSDT","STARUSDT","STBLUSDT","STEEMUSDT","STGUSDT","STOUSDT","STRKUSDT","STXUSDT","SUIUSDT","SUNUSDT","SUPERUSDT","SUSDT","SUSHIUSDT","SWARMSUSDT","SXTUSDT","SYNUSDT","SYRUPUSDT","TACUSDT","TAGUSDT","TAIKOUSDT","TAKEUSDT","TAOUSDT","TAUSDT","THETAUSDT","THEUSDT","TIAUSDT","TLMUSDT","TNSRUSDT","TOSHIUSDT","TOWNSUSDT","TRADOORUSDT","TRBUSDT","TREEUSDT","TRIAUSDT","TRUMPUSDT","TRUSTUSDT","TRUTHUSDT","TRXUSDT","TSTUSDT","TURBOUSDT","TURTLEUSDT","TUSDT","TUTUSDT","TWTUSDT","UAIUSDT","UBUSDT","UMAUSDT","UNIUSDT","USDCUSDT","USELESSUSDT","USTCUSDT","USUALUSDT","USUSDT","VANAUSDT","VELODROMEUSDT","VELVETUSDT","VETUSDT","VIRTUALUSDT","VTHOUSDT","VVVUSDT","WALUSDT","WAXPUSDT","WCTUSDT","WETUSDT","WIFUSDT","WLDUSDT","WLFIUSDT","WOOUSDT","WUSDT","XAIUSDT","XANUSDT","XAUTUSDT","XLMUSDT","XMRUSDT","XNYUSDT","XPINUSDT","XPLUSDT","XRPUSDT","XTZUSDT","XVGUSDT","XVSUSDT","YBUSDT","YFIUSDT","YGGUSDT","ZAMAUSDT","ZBTUSDT","ZECUSDT","ZENUSDT","ZEREBROUSDT","ZESTUSDT","ZETAUSDT","ZILUSDT","ZKCUSDT","ZKPUSDT","ZKUSDT","ZORAUSDT","ZROUSDT","ZRXUSDT","哈基米USDT","币安人生USDT","我踏马来了USDT","牛来USDT","龙虾USDT"]
STRUCTURAL_THETA_TEST_ONLY = {
    'theta_minor':'0.655417496698647720797643159793938746032740795679425',
    'theta_intermediate':'1.7477799911963939221270484261171699894206421218118',
    'theta_major':'3.4955599823927878442540968522343399788412842436236'
}
FROZEN_528_ORDER_SHA256 = '4bb105592aaf8af4f7027f3806019d0dffdff1372842d2aec45e150b4c990bc1'
FORMAL_D5_10_SLOT_POLICY = 'D5_OPERATIONAL_RISK_PORTFOLIO_USER_FREEZE_V1'
LAST_ENTRY_AUTHORITY = 'UPDATE014_ONLY_NO_MANUAL_ENTRY'
MAX_EXACT_SOURCE_BARS = 1024

def _native_exact_closed_kline(event, symbol):
    if event is None:
        return None
    if not isinstance(event,dict) or event.get('dropped',0)!=0:
        raise ValueError('NATIVE_STREAM_OVERFLOW_OR_WRONG_SHAPE')
    k=event.get('k')
    if k is None and isinstance(event.get('data'),dict):
        k=event['data'].get('k')
    if not isinstance(k,dict):
        raise ValueError('NATIVE_STREAM_KLINE_K_REQUIRED')
    if k.get('x') is not True:
        return None
    if k.get('s',event.get('s'))!=symbol:
        raise ValueError('NATIVE_KLINE_SYMBOL_MISMATCH')
    t,T=k.get('t'),k.get('T')
    if type(t) is not int or type(T) is not int or t%900000 or T!=t+899999:
        raise ValueError('NATIVE_15M_CLOSED_TIMESTAMPS_INVALID')
    if not all(type(k.get(f)) is str for f in ('o','h','l','c','v','q')):
        raise ValueError('NATIVE_EXACT_DECIMAL_STRING_REQUIRED_FLOAT_FORBIDDEN')
    bar=CanonicalBar.from_values(symbol=symbol,open_time=t,close_time=T,
         open=k['o'],high=k['h'],low=k['l'],close=k['c'],
         base_volume=k['v'],quote_volume=k['q'])
    _validate_bar(bar)
    return {'symbol':symbol,'open_time':t,'close_time':T,'open':k['o'],
            'high':k['h'],'low':k['l'],'close':k['c'],
            'base_volume':k['v'],'quote_volume':k['q']}

def _replay_actual_original_d1d2(symbol, raw):
    if not raw:
        return {'symbol':symbol,'status':'BLOCKED_NO_CLOSED_DATA',
                'D1':'NOT_EXECUTED','D2':'NOT_EXECUTED'}
    bars=[]
    for row in raw:
        if not isinstance(row,dict) or row.get('symbol')!=symbol:
            raise ValueError('INVALID_SYMBOL_RAW_ROW')
        bars.append(CanonicalBar.from_values(symbol=symbol,
            open_time=row['open_time'],close_time=row['close_time'],
            open=row['open'],high=row['high'],low=row['low'],close=row['close'],
            base_volume=row['base_volume'],quote_volume=row['quote_volume']))
    if any(a.open_time>=b.open_time for a,b in zip(bars,bars[1:])):
        raise ValueError('NONMONOTONIC_RAW_SOURCE')
    d1=canonicalize_15m(bars)
    if d1.issues or len(d1.records)!=len(bars):
        raise ValueError('ORIGINAL_D1_INTEGRITY_OR_HISTORY_GAP')
    snapshot=current_partial_parameter_snapshot()
    if snapshot.runtime_usable or snapshot.complete_strategy_parameter_snapshot:
        raise ValueError('SCIENTIFIC_SNAPSHOT_STATUS_DRIFT')
    for n in ('theta_minor','theta_intermediate','theta_major'):
        slot=snapshot.slot(n)
        if slot.state is not ParameterState.OPEN or slot.exact_value is not None:
            raise ValueError('TEST_ONLY_STRUCTURAL_SOURCE_AUTHORITY_DRIFT')
    stop=snapshot.slot('theta_stop')
    if stop.state is not ParameterState.LOCKED or stop.exact_value is not None:
        raise ValueError('OFFICIAL_D5_D6_STOP_GOVERNANCE_DRIFT')
    p=StructuralScaleParameters(
        *(Fraction(Decimal(STRUCTURAL_THETA_TEST_ONLY[n]))
        for n in ('theta_minor','theta_intermediate','theta_major')))
    d2=D2ReferenceSkeleton(symbol=symbol,structural_params=p,
        frozen_params=frozen_d2_parameters(snapshot))
    atr=ATR14Recurrence()
    ema20=EMARecurrence(20)
    ema50=EMARecurrence(50)
    st=SupertrendRecurrence()
    last=None
    for rec in d1.records:
        b=rec.bar
        e20=ema20.update(b.close,segment_id=rec.canonical_segment_id)
        e50=ema50.update(b.close,segment_id=rec.canonical_segment_id)
        a=atr.update(b,segment_id=rec.canonical_segment_id)
        trend=st.update(b,a,segment_id=rec.canonical_segment_id)
        last=d2.advance_source_bar(b,a,canonical_segment_id=rec.canonical_segment_id)
    h1=aggregate_completed_htf(d1.records,timeframe_ms=3600000,
        information_cutoff=d1.information_cutoff)
    h4=aggregate_completed_htf(d1.records,timeframe_ms=14400000,
        information_cutoff=d1.information_cutoff)
    return {'symbol':symbol,'status':'PASS_ORIGINAL_D1D2_ONLY',
        'cutoff':d1.information_cutoff,'bars':len(d1.records),
        'ema20_kind':e20.kind.value,'ema50_kind':e50.kind.value,
        'atr14_kind':a.kind.value,'st_direction':trend.direction.value,
        'D2_trend':last.update_006_trend.direction.value,
        'D2_episode':last.update_006_trend.episode_id,
        'D2_minor_events':len(last.update_005_minor),
        'D2_intermediate_events':len(last.update_005_intermediate),
        'D2_major_events':len(last.update_005_major),
        'completed_1h':len(h1),'completed_4h':len(h4),
        'D3':'BLOCKED_NOT_YET_BOUND',
        'D4':'NOT_EXECUTED','F9':'NOT_EXECUTED','D5':'NOT_EXECUTED',
        'UPDATE014':'NOT_EXECUTED','D6':'NOT_EXECUTED',
        'entry_ready':False,'trade_authorized':False}

@node('std:fetch')
async def native_exact_15m_fetch(symbol):
    # This SDK signature is a native validation target, not a proven contract.
    return kline_stream(market_type='futures',symbol=symbol,timeframe='15m')

@node('custom:tac_original_core')
async def native_original_core_compute(exact_rows_by_symbol):
    if not isinstance(exact_rows_by_symbol,dict) or set(exact_rows_by_symbol)!=set(FROZEN_528_SYMBOLS):
        raise ValueError('EXACT_FROZEN_528_SYMBOL_SET_REQUIRED')
    out=[_replay_actual_original_d1d2(s,exact_rows_by_symbol[s])
         for s in FROZEN_528_SYMBOLS]
    good=[x for x in out if x['status']=='PASS_ORIGINAL_D1D2_ONLY']
    cutoffs={x['cutoff'] for x in good}
    return {'schema':'TAC_AI_PRO_ORIGINAL_D1_D2_NATIVE_TESTONLY_CANDIDATE_V1',
       'status':'PASS_ORIGINAL_D1D2_528_SINGLE_CUTOFF' if len(good)==528 and len(cutoffs)==1
                else 'BLOCKED_INCOMPLETE_EXACT_528_SOURCE',
       'frozen_universe_target':528,'d1d2_computed':len(good),
       'same_cutoff':len(cutoffs)==1,'per_symbol':out,
       'D3_D4_F9_D5_UPDATE014_D6':'NOT_BOUND_TO_NATIVE_EXECUTION',
       'TAC_LIVE_ENABLED':0,'orders':0,'fills':0,
       'execution_intents':0,'entry_ready':False,'trade_authorized':False}

@workflow
async def original_tac_testonly_workflow():
    if TAC_LIVE_ENABLED!=0 or NATIVE_528_PROSPECTIVE_STREAM_AUTHORIZED is not True:
        return {'status':'BLOCKED_NATIVE_STREAM_NOT_YET_VALIDATED',
                'target':528,'trade_authorized':False,'orders':0}
    previous=ctx.state.get('tac_original_exact_closed_15m_v1',{})
    if not isinstance(previous,dict):
        raise ValueError('STATE_TYPE_INVALID')
    next_rows={}
    for symbol in FROZEN_528_SYMBOLS:
        event=await native_exact_15m_fetch(symbol)
        parsed=_native_exact_closed_kline(event,symbol)
        series=list(previous.get(symbol,()))
        if parsed is not None:
            if series and parsed['open_time']<=series[-1]['open_time']:
                raise ValueError('STREAM_EVENT_DUPLICATE_OR_OUT_OF_ORDER:'+symbol)
            series.append(parsed)
        next_rows[symbol]=series[-MAX_EXACT_SOURCE_BARS:]
    # ctx.state has no vendor-guaranteed crash recovery; never create entry.
    ctx.state['tac_original_exact_closed_15m_v1']=next_rows
    return await native_original_core_compute(next_rows)

async def main():
    while True:
        now=datetime.now(timezone.utc)
        seconds=now.hour*3600+now.minute*60+now.second+now.microsecond/1000000
        await asyncio.sleep(900-(seconds%900)+5)
        try:
            await original_tac_testonly_workflow()
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            ctx.exception(exc,reason='ORIGINAL_TAC_TEST_ONLY_NATIVE_SOURCE_BLOCKED')
# === END AI PRO TEST_ONLY BINDING ===
