from __future__ import annotations

"""Production D1/D2 -> D3 mathematical candidate authority V1.

Engineering role only:
- extract already-authoritative D1/D2 state;
- call the frozen RC1 build_candidate() primitive;
- preserve all source-TF x family candidate slots;
- implement only the separately frozen candidate terminal-invalidation bookkeeping;
- emit repaired D3CandidateUpdateV1 rows.

No market source, performance data, TEST, PnL, order, Entry, D4, or execution logic
exists in this module.
"""

from copy import deepcopy
from dataclasses import dataclass, field, fields, is_dataclass, replace
from enum import Enum
from fractions import Fraction
from hashlib import sha256
import importlib
import json
from typing import Any, Callable, Mapping

import strategy_rc1.d3_boundary_intelligence.candidates as cand
import strategy_rc1.d3_boundary_intelligence.types as d3t
from strategy_rc1.d2_market_state.types import TrendDirection, TrendEpisodeState
from strategy_rc1.wp1_reference import D1MathPoint, D1ReferenceResult

import nontrading_adapter_d3_d4_schema_orchestration_rc1_conformance_repair_v1 as repaired
import authoritative_d3_b5_d4_base_runtime_producers_v1 as b5prod


PRODUCER_ID = "D1_D2_TO_D3_MATHEMATICAL_BOUNDARY_CANDIDATE_PRODUCTION_V1"
SEMANTIC_ID = "CANDIDATE_TERMINAL_INVALIDATION_AND_REVALIDATION_PRODUCTION_SEMANTIC_V1"
SOURCE_TIMEFRAMES_MS = (900_000, 3_600_000, 14_400_000)
CANDIDATE_FAMILIES = (
    d3t.CandidateFamily.EMA20,
    d3t.CandidateFamily.EMA50,
    d3t.CandidateFamily.ST_ACTIVE,
)
CAUSE_TRUE_BREAK = "TERMINAL_TRUE_BREAK"
CAUSE_B5_REPLACEMENT = "B5_REPLACEMENT"
REARM_PROVENANCE = "MATERIAL_CORRECT_SIDE_SEPARATION"


class CandidateProductionBlock(RuntimeError):
    pass


class CandidateProductionConflict(CandidateProductionBlock):
    pass


def _encode(value: Any) -> Any:
    if isinstance(value, Fraction):
        return {"$fraction":[value.numerator,value.denominator]}
    if isinstance(value, Enum):
        return {"$enum":[value.__class__.__module__,value.__class__.__qualname__,value.value]}
    if is_dataclass(value) and not isinstance(value, type):
        return {
            "$dataclass":[value.__class__.__module__,value.__class__.__qualname__],
            "fields":{f.name:_encode(getattr(value,f.name)) for f in fields(value)},
        }
    if isinstance(value, Mapping):
        return {"$map":[[str(k),_encode(v)] for k,v in sorted(value.items(),key=lambda kv:str(kv[0]))]}
    if isinstance(value, tuple):
        return {"$tuple":[_encode(x) for x in value]}
    if isinstance(value, list):
        return {"$list":[_encode(x) for x in value]}
    if isinstance(value,(str,int,bool)) or value is None:
        return value
    raise TypeError(f"UNSUPPORTED_SERIALIZATION_TYPE:{type(value)!r}")


def _resolve(module: str, qualname: str) -> Any:
    obj: Any = importlib.import_module(module)
    for part in qualname.split("."):
        obj = getattr(obj,part)
    return obj


def _decode(value: Any) -> Any:
    if isinstance(value,list):
        return [_decode(x) for x in value]
    if not isinstance(value,dict):
        return value
    if "$fraction" in value:
        return Fraction(*value["$fraction"])
    if "$enum" in value:
        module,qualname,raw=value["$enum"]
        return _resolve(module,qualname)(raw)
    if "$tuple" in value:
        return tuple(_decode(x) for x in value["$tuple"])
    if "$list" in value:
        return [_decode(x) for x in value["$list"]]
    if "$map" in value:
        return {k:_decode(v) for k,v in value["$map"]}
    if "$dataclass" in value:
        module,qualname=value["$dataclass"]
        cls=_resolve(module,qualname)
        return cls(**{k:_decode(v) for k,v in value["fields"].items()})
    return {k:_decode(v) for k,v in value.items()}


def exact_json(value: Any) -> str:
    return json.dumps(_encode(value),sort_keys=True,separators=(",",":"),ensure_ascii=False)


def digest(value: Any) -> str:
    return sha256(exact_json(value).encode()).hexdigest()


@dataclass(frozen=True)
class TerminalInvalidationCause:
    cause_id: str
    kind: str
    cutoff: int
    effective_same_cutoff: bool
    anchor_episode_ids: tuple[str,...] = ()
    interaction_event_ids: tuple[str,...] = ()
    evidence_refs: tuple[str,...] = ()


@dataclass(frozen=True)
class CandidateInvalidationRecord:
    candidate_id: str
    causes: tuple[TerminalInvalidationCause,...] = ()
    release_cutoff: int | None = None
    release_rearm_event_id: str | None = None

    @property
    def latest_invalidation_cutoff(self) -> int | None:
        return max((x.cutoff for x in self.causes),default=None)


@dataclass(frozen=True)
class CandidateProductionRequest:
    transaction_id: str
    symbol: str
    information_cutoff: int
    d1: D1ReferenceResult
    target_trend: TrendEpisodeState
    interaction_events: tuple[d3t.InteractionEvent,...] = ()


@dataclass(frozen=True)
class PostUpdate008RoleTransitionRequest:
    transaction_id: str
    information_cutoff: int
    role_assignment: Any
    prior_role_memory: b5prod.RoleMemory | None
    anchor_episodes: tuple[d3t.AnchorEpisode,...] = ()


@dataclass(frozen=True)
class CandidateProductionResult:
    transaction_id: str
    information_cutoff: int
    updates: tuple[repaired.D3CandidateUpdateV1,...]
    continuity_break_candidate_ids: tuple[str,...]
    target_trend_ended_candidate_ids: tuple[str,...]
    input_digest: str
    output_digest: str


@dataclass(frozen=True)
class PostUpdate008RoleTransitionResult:
    transaction_id: str
    information_cutoff: int
    affected_candidate_ids: tuple[str,...]
    input_digest: str


@dataclass(frozen=True)
class CandidateCompletedTransaction:
    input_digest: str
    result: CandidateProductionResult


@dataclass(frozen=True)
class RoleCompletedTransaction:
    input_digest: str
    result: PostUpdate008RoleTransitionResult


@dataclass
class CandidateProducerState:
    candidates: dict[str,d3t.MathematicalBoundaryCandidate] = field(default_factory=dict)
    active_slots: dict[str,str] = field(default_factory=dict)
    invalidations: dict[str,CandidateInvalidationRecord] = field(default_factory=dict)
    completed_candidate_transactions: dict[str,CandidateCompletedTransaction] = field(default_factory=dict)
    completed_role_transactions: dict[str,RoleCompletedTransaction] = field(default_factory=dict)
    last_candidate_cutoff_by_symbol: dict[str,int] = field(default_factory=dict)


PersistFn = Callable[[str],None]


def _slot_key(symbol: str, timeframe_ms: int, family: d3t.CandidateFamily) -> str:
    return f"{symbol}\x1f{timeframe_ms}\x1f{family.value}"


def _cause_id(kind: str, candidate_id: str, cutoff: int, refs: tuple[str,...]) -> str:
    raw="\x1f".join((kind,candidate_id,str(cutoff),*refs))
    return sha256(raw.encode()).hexdigest()


def _active_target(trend: TrendEpisodeState) -> tuple[bool,str | None,TrendDirection | None]:
    if trend.direction in (TrendDirection.LONG,TrendDirection.SHORT):
        if not trend.episode_id:
            raise CandidateProductionConflict("ACTIVE_TREND_WITHOUT_EPISODE_ID")
        if trend.terminal_episode_id == trend.episode_id:
            raise CandidateProductionConflict("ACTIVE_TREND_EPISODE_MARKED_TERMINAL")
        return True,trend.episode_id,trend.direction
    return False,None,None


def _current_canonical_segment(d1: D1ReferenceResult, symbol: str, cutoff: int) -> str | None:
    eligible=[]
    for rec in d1.canonical_records:
        bar=rec.bar
        if bar.symbol != symbol:
            raise CandidateProductionConflict("D1_MIXED_OR_WRONG_SYMBOL")
        if bar.close_time <= cutoff:
            eligible.append(rec)
    if not eligible:
        return None
    eligible.sort(key=lambda r:(r.bar.close_time,r.bar.open_time,r.canonical_segment_id))
    last=eligible[-1]
    same=[r for r in eligible if r.bar.close_time == last.bar.close_time]
    if len(same)>1 and any(r != last for r in same):
        raise CandidateProductionConflict("D1_CONFLICTING_CANONICAL_RECORD_AT_CUTOFF")
    return last.canonical_segment_id


def _stream_for(d1: D1ReferenceResult, timeframe_ms: int) -> tuple[D1MathPoint,...]:
    if timeframe_ms == 900_000:
        return d1.math_15m
    if timeframe_ms == 3_600_000:
        return d1.math_1h
    if timeframe_ms == 14_400_000:
        return d1.math_4h
    raise CandidateProductionConflict("UNAUTHORIZED_SOURCE_TIMEFRAME")


def _latest_point(d1: D1ReferenceResult, timeframe_ms: int, cutoff: int) -> D1MathPoint | None:
    eligible=[]
    for p in _stream_for(d1,timeframe_ms):
        if p.timeframe_ms != timeframe_ms:
            raise CandidateProductionConflict("D1_POINT_TIMEFRAME_MISMATCH")
        if p.source_close_time <= cutoff:
            eligible.append(p)
    if not eligible:
        return None
    eligible.sort(key=lambda p:(p.source_close_time,p.source_open_time,p.source_segment_id))
    last=eligible[-1]
    same=[p for p in eligible if p.source_close_time == last.source_close_time]
    if len(same)>1 and any(p != last for p in same):
        raise CandidateProductionConflict("D1_CONFLICTING_MATH_POINT_AT_SOURCE_CLOSE")
    return last


def _line(point: D1MathPoint, family: d3t.CandidateFamily) -> tuple[Any,Any | None]:
    if family is d3t.CandidateFamily.EMA20:
        return point.ema20,None
    if family is d3t.CandidateFamily.EMA50:
        return point.ema50,None
    if family is d3t.CandidateFamily.ST_ACTIVE:
        return point.supertrend.active_line,point.supertrend.direction
    raise CandidateProductionConflict("UNAUTHORIZED_CANDIDATE_FAMILY")


def _candidate_from_point(
    *,
    symbol: str,
    point: D1MathPoint,
    current_segment_id: str,
    trend_episode_id: str,
    direction: TrendDirection,
    family: d3t.CandidateFamily,
) -> d3t.MathematicalBoundaryCandidate:
    line,st_direction=_line(point,family)
    continuity_ok=point.source_segment_id == current_segment_id
    return cand.build_candidate(
        symbol=symbol,
        source_timeframe_ms=point.timeframe_ms,
        target_trend_episode_id=trend_episode_id,
        target_direction=direction,
        family=family,
        line=line,
        source_scale=point.atr14,
        source_segment_id=point.source_segment_id,
        available_at=point.source_close_time,
        source_continuity_ok=continuity_ok,
        st_direction=st_direction,
        provenance={
            "producer":PRODUCER_ID,
            "semantic":SEMANTIC_ID,
            "d1_source_close_time":str(point.source_close_time),
            "current_canonical_segment_id":current_segment_id,
        },
    )


def _unavailable_after_continuity_break(
    candidate: d3t.MathematicalBoundaryCandidate,
    *,
    cutoff: int,
) -> d3t.MathematicalBoundaryCandidate:
    return cand.build_candidate(
        symbol=candidate.symbol,
        source_timeframe_ms=candidate.source_timeframe_ms,
        target_trend_episode_id=candidate.target_trend_episode_id,
        target_direction=candidate.target_direction,
        family=candidate.family,
        line=cand.InfoValue.na(),
        source_scale=cand.InfoValue.na(),
        source_segment_id=candidate.source_segment_id,
        available_at=cutoff,
        source_continuity_ok=False,
        st_direction=cand.Direction.UNKNOWN if candidate.family is d3t.CandidateFamily.ST_ACTIVE else None,
        provenance={
            "producer":PRODUCER_ID,
            "semantic":SEMANTIC_ID,
            "reason":"SOURCE_CONTINUITY_BREAK",
        },
    )


def _record_active_at(record: CandidateInvalidationRecord | None, cutoff: int) -> bool:
    if record is None or not record.causes:
        return False
    if record.release_cutoff is not None:
        latest=record.latest_invalidation_cutoff
        if latest is None or record.release_cutoff > latest:
            return False
    return any(cutoff >= c.cutoff if c.effective_same_cutoff else cutoff > c.cutoff for c in record.causes)


def _add_cause(
    state: CandidateProducerState,
    *,
    candidate_id: str,
    kind: str,
    cutoff: int,
    effective_same_cutoff: bool,
    anchor_episode_ids: tuple[str,...]=(),
    interaction_event_ids: tuple[str,...]=(),
    evidence_refs: tuple[str,...]=(),
) -> None:
    refs=tuple(sorted(set((*anchor_episode_ids,*interaction_event_ids,*evidence_refs))))
    cid=_cause_id(kind,candidate_id,cutoff,refs)
    cause=TerminalInvalidationCause(
        cause_id=cid,
        kind=kind,
        cutoff=cutoff,
        effective_same_cutoff=effective_same_cutoff,
        anchor_episode_ids=tuple(sorted(set(anchor_episode_ids))),
        interaction_event_ids=tuple(sorted(set(interaction_event_ids))),
        evidence_refs=tuple(sorted(set(evidence_refs))),
    )
    prior=state.invalidations.get(candidate_id,CandidateInvalidationRecord(candidate_id))
    if any(x.cause_id == cid for x in prior.causes):
        return
    state.invalidations[candidate_id]=CandidateInvalidationRecord(
        candidate_id=candidate_id,
        causes=tuple(sorted((*prior.causes,cause),key=lambda x:(x.cutoff,x.kind,x.cause_id))),
        release_cutoff=None,
        release_rearm_event_id=None,
    )


def _apply_true_break_causes(state: CandidateProducerState, events: tuple[d3t.InteractionEvent,...], cutoff: int) -> None:
    seen: dict[str,d3t.InteractionEvent]={}
    for event in sorted(events,key=lambda x:(x.candidate_id,x.event_id)):
        prior=seen.get(event.candidate_id)
        if prior is not None and prior != event:
            raise CandidateProductionConflict("MULTIPLE_CURRENT_EVENTS_FOR_CANDIDATE")
        seen[event.candidate_id]=event
        if event.break_state is not d3t.BreakState.TRUE_BREAK or not event.terminal:
            continue
        cause_cutoff=event.resolved_at
        if cause_cutoff is None or cause_cutoff > cutoff:
            raise CandidateProductionConflict("TRUE_BREAK_WITH_INVALID_RESOLVED_AT")
        _add_cause(
            state,
            candidate_id=event.candidate_id,
            kind=CAUSE_TRUE_BREAK,
            cutoff=cause_cutoff,
            effective_same_cutoff=True,
            anchor_episode_ids=() if event.anchor_episode_id is None else (event.anchor_episode_id,),
            interaction_event_ids=(event.event_id,),
            evidence_refs=(event.event_id,),
        )


def _release_from_fresh_rearm(
    state: CandidateProducerState,
    *,
    events: tuple[d3t.InteractionEvent,...],
    trend: TrendEpisodeState,
    cutoff: int,
) -> None:
    active,episode_id,direction=_active_target(trend)
    if not active:
        return
    for event in sorted(events,key=lambda x:(x.candidate_id,x.event_id)):
        record=state.invalidations.get(event.candidate_id)
        if record is None or not _record_active_at(record,cutoff):
            continue
        latest=record.latest_invalidation_cutoff
        if latest is None:
            continue
        if event.target_trend_episode_id != episode_id or event.target_direction is not direction:
            continue
        if event.control is not d3t.InteractionControl.ARMED:
            continue
        if event.armed_at is None or event.armed_at <= latest:
            continue
        if event.provenance.get("rearm") != REARM_PROVENANCE:
            continue
        state.invalidations[event.candidate_id]=replace(
            record,
            release_cutoff=cutoff,
            release_rearm_event_id=event.event_id,
        )


def _merge_update(
    updates: dict[str,repaired.D3CandidateUpdateV1],
    item: repaired.D3CandidateUpdateV1,
) -> None:
    candidate_id=item.candidate.candidate_id
    prior=updates.get(candidate_id)
    if prior is not None and prior != item:
        raise CandidateProductionConflict("DUPLICATE_CANDIDATE_UPDATE_CONFLICT")
    updates[candidate_id]=item


def _update_for(
    state: CandidateProducerState,
    candidate: d3t.MathematicalBoundaryCandidate,
    *,
    target_trend_active: bool,
    cutoff: int,
) -> repaired.D3CandidateUpdateV1:
    return repaired.D3CandidateUpdateV1(
        candidate=candidate,
        target_trend_active=target_trend_active,
        candidate_terminally_invalidated=_record_active_at(state.invalidations.get(candidate.candidate_id),cutoff),
    )


class D1D2D3CandidateProductionRuntimeV1:
    def __init__(self, state: CandidateProducerState | None = None) -> None:
        self.state=CandidateProducerState() if state is None else state

    @classmethod
    def restore_state(cls,payload: str) -> "D1D2D3CandidateProductionRuntimeV1":
        state=_decode(json.loads(payload))
        if not isinstance(state,CandidateProducerState):
            raise CandidateProductionConflict("RESTORED_STATE_SCHEMA")
        return cls(state)

    def export_state(self) -> str:
        return exact_json(self.state)

    def state_digest(self) -> str:
        return digest(self.state)

    def candidate_terminally_invalidated(self,candidate_id: str,*,cutoff: int) -> bool:
        return _record_active_at(self.state.invalidations.get(candidate_id),cutoff)

    def _project(self, state: CandidateProducerState, request: CandidateProductionRequest) -> CandidateProductionResult:
        if not request.transaction_id or not request.symbol:
            raise CandidateProductionConflict("MISSING_TRANSACTION_OR_SYMBOL")
        if request.information_cutoff < 0:
            raise CandidateProductionConflict("NEGATIVE_INFORMATION_CUTOFF")

        last=state.last_candidate_cutoff_by_symbol.get(request.symbol)
        if last is not None and request.information_cutoff < last:
            raise CandidateProductionBlock("OUT_OF_ORDER_CANDIDATE_CUTOFF")
        if last is not None and request.information_cutoff == last:
            raise CandidateProductionBlock("NEW_TRANSACTION_SAME_CANDIDATE_CUTOFF")

        _apply_true_break_causes(state,request.interaction_events,request.information_cutoff)
        _release_from_fresh_rearm(
            state,
            events=request.interaction_events,
            trend=request.target_trend,
            cutoff=request.information_cutoff,
        )

        active,episode_id,direction=_active_target(request.target_trend)
        current_segment=_current_canonical_segment(request.d1,request.symbol,request.information_cutoff)
        if active and current_segment is None:
            raise CandidateProductionBlock("NO_CAUSAL_CANONICAL_SEGMENT_FOR_ACTIVE_TREND")

        prior_slots=dict(state.active_slots)
        updates: dict[str,repaired.D3CandidateUpdateV1]={}
        continuity_break_ids:set[str]=set()
        ended_ids:set[str]=set()

        if not active:
            for slot,candidate_id in sorted(prior_slots.items()):
                if not slot.startswith(request.symbol+"\x1f"):
                    continue
                previous=state.candidates.get(candidate_id)
                if previous is None:
                    raise CandidateProductionConflict("ACTIVE_SLOT_CANDIDATE_MISSING")
                _merge_update(
                    updates,
                    _update_for(state,previous,target_trend_active=False,cutoff=request.information_cutoff),
                )
                ended_ids.add(candidate_id)
                state.active_slots.pop(slot,None)
        else:
            assert episode_id is not None and direction is not None and current_segment is not None
            for timeframe_ms in SOURCE_TIMEFRAMES_MS:
                point=_latest_point(request.d1,timeframe_ms,request.information_cutoff)
                for family in CANDIDATE_FAMILIES:
                    slot=_slot_key(request.symbol,timeframe_ms,family)
                    prior_id=prior_slots.get(slot)
                    previous=state.candidates.get(prior_id) if prior_id is not None else None

                    if point is None:
                        if previous is None:
                            continue
                        same_target=(
                            previous.target_trend_episode_id == episode_id
                            and previous.target_direction is direction
                        )
                        if not same_target:
                            _merge_update(
                                updates,
                                _update_for(state,previous,target_trend_active=False,cutoff=request.information_cutoff),
                            )
                            ended_ids.add(previous.candidate_id)
                            state.active_slots.pop(slot,None)
                        elif previous.source_segment_id != current_segment:
                            unavailable=_unavailable_after_continuity_break(previous,cutoff=request.information_cutoff)
                            state.candidates[unavailable.candidate_id]=unavailable
                            _merge_update(
                                updates,
                                _update_for(state,unavailable,target_trend_active=True,cutoff=request.information_cutoff),
                            )
                            continuity_break_ids.add(unavailable.candidate_id)
                        else:
                            _merge_update(
                                updates,
                                _update_for(state,previous,target_trend_active=True,cutoff=request.information_cutoff),
                            )
                        continue

                    current=_candidate_from_point(
                        symbol=request.symbol,
                        point=point,
                        current_segment_id=current_segment,
                        trend_episode_id=episode_id,
                        direction=direction,
                        family=family,
                    )

                    if previous is not None and previous.candidate_id != current.candidate_id:
                        if (
                            previous.target_trend_episode_id != episode_id
                            or previous.target_direction is not direction
                        ):
                            _merge_update(
                                updates,
                                _update_for(state,previous,target_trend_active=False,cutoff=request.information_cutoff),
                            )
                            ended_ids.add(previous.candidate_id)
                        elif previous.source_segment_id != current.source_segment_id:
                            unavailable=_unavailable_after_continuity_break(previous,cutoff=request.information_cutoff)
                            state.candidates[unavailable.candidate_id]=unavailable
                            _merge_update(
                                updates,
                                _update_for(state,unavailable,target_trend_active=True,cutoff=request.information_cutoff),
                            )
                            continuity_break_ids.add(unavailable.candidate_id)

                    if (
                        previous is not None
                        and previous.candidate_id == current.candidate_id
                        and current.availability is d3t.CandidateAvailability.UNAVAILABLE
                        and previous.availability is d3t.CandidateAvailability.AVAILABLE
                        and point.source_segment_id != current_segment
                    ):
                        continuity_break_ids.add(current.candidate_id)

                    state.candidates[current.candidate_id]=current
                    state.active_slots[slot]=current.candidate_id
                    _merge_update(
                        updates,
                        _update_for(state,current,target_trend_active=True,cutoff=request.information_cutoff),
                    )

        rows=tuple(updates[k] for k in sorted(updates))
        base={
            "updates":rows,
            "continuity_break_candidate_ids":tuple(sorted(continuity_break_ids)),
            "target_trend_ended_candidate_ids":tuple(sorted(ended_ids)),
        }
        result=CandidateProductionResult(
            transaction_id=request.transaction_id,
            information_cutoff=request.information_cutoff,
            updates=rows,
            continuity_break_candidate_ids=base["continuity_break_candidate_ids"],
            target_trend_ended_candidate_ids=base["target_trend_ended_candidate_ids"],
            input_digest=digest(request),
            output_digest=digest(base),
        )
        state.last_candidate_cutoff_by_symbol[request.symbol]=request.information_cutoff
        return result

    def project_candidate_updates(
        self,
        request: CandidateProductionRequest,
        *,
        persist: PersistFn | None = None,
    ) -> CandidateProductionResult:
        input_digest=digest(request)
        prior=self.state.completed_candidate_transactions.get(request.transaction_id)
        if prior is not None:
            if prior.input_digest != input_digest:
                raise CandidateProductionConflict("DUPLICATE_TX_INPUT_MISMATCH")
            return prior.result

        working=deepcopy(self.state)
        result=self._project(working,request)
        if result.input_digest != input_digest:
            raise CandidateProductionConflict("INTERNAL_INPUT_DIGEST_MISMATCH")
        working.completed_candidate_transactions[request.transaction_id]=CandidateCompletedTransaction(
            input_digest=input_digest,
            result=result,
        )
        payload=exact_json(working)
        if persist is not None:
            persist(payload)
        self.state=working
        return result

    def record_post_update008_role_transition(
        self,
        request: PostUpdate008RoleTransitionRequest,
        *,
        persist: PersistFn | None = None,
    ) -> PostUpdate008RoleTransitionResult:
        input_digest=digest(request)
        prior=self.state.completed_role_transactions.get(request.transaction_id)
        if prior is not None:
            if prior.input_digest != input_digest:
                raise CandidateProductionConflict("DUPLICATE_ROLE_TX_INPUT_MISMATCH")
            return prior.result

        working=deepcopy(self.state)
        transition=request.role_assignment.transition
        affected:set[str]=set()

        if transition is b5prod.RoleTransition.UNRESOLVED:
            raise CandidateProductionBlock("ROLE_TRANSITION_UNRESOLVED")
        if transition is b5prod.RoleTransition.REPLACEMENT:
            if request.prior_role_memory is None:
                raise CandidateProductionConflict("REPLACEMENT_WITHOUT_PRIOR_ROLE_MEMORY")
            episode_map={x.anchor_episode_id:x for x in request.anchor_episodes}
            if len(episode_map) != len(request.anchor_episodes):
                raise CandidateProductionConflict("DUPLICATE_ANCHOR_EPISODE_ID")
            by_candidate: dict[str,list[str]]={}
            for anchor_id in request.prior_role_memory.primary_anchor_episode_ids:
                episode=episode_map.get(anchor_id)
                if episode is None:
                    raise CandidateProductionConflict("REPLACEMENT_PRIOR_ANCHOR_EPISODE_MISSING")
                if getattr(episode.validity,"value",None) != "TERMINATED":
                    raise CandidateProductionConflict("REPLACEMENT_PRIOR_ANCHOR_NOT_TERMINATED")
                if episode.candidate_id not in working.candidates:
                    raise CandidateProductionConflict("REPLACEMENT_CANDIDATE_NOT_IN_PRODUCTION_STATE")
                by_candidate.setdefault(episode.candidate_id,[]).append(anchor_id)
            for candidate_id,anchor_ids in sorted(by_candidate.items()):
                _add_cause(
                    working,
                    candidate_id=candidate_id,
                    kind=CAUSE_B5_REPLACEMENT,
                    cutoff=request.information_cutoff,
                    effective_same_cutoff=False,
                    anchor_episode_ids=tuple(sorted(anchor_ids)),
                    evidence_refs=("ROLE_TRANSITION_REPLACEMENT",),
                )
                affected.add(candidate_id)
        elif transition not in (
            b5prod.RoleTransition.NONE,
            b5prod.RoleTransition.HANDOFF,
            b5prod.RoleTransition.PROMOTION,
        ):
            raise CandidateProductionConflict("UNKNOWN_ROLE_TRANSITION")

        result=PostUpdate008RoleTransitionResult(
            transaction_id=request.transaction_id,
            information_cutoff=request.information_cutoff,
            affected_candidate_ids=tuple(sorted(affected)),
            input_digest=input_digest,
        )
        working.completed_role_transactions[request.transaction_id]=RoleCompletedTransaction(
            input_digest=input_digest,
            result=result,
        )
        payload=exact_json(working)
        if persist is not None:
            persist(payload)
        self.state=working
        return result
