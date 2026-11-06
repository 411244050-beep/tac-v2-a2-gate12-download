from __future__ import annotations

"""Production D4 market-event lineage evidence projector V2.

This module is a mechanical projection of the frozen
D4_MARKET_EVENT_LINEAGE_EVIDENCE_SOURCE_ASSOCIATION_V1 semantic.

It does NOT:
- classify D4 mechanism science;
- select a candidate, snapshot, detector, mechanism, boundary, or price-distance winner;
- create market-event IDs;
- call MarketCycleState.decide() to infer an upstream relation;
- read market sources, TEST, outcomes, PnL, or execution state.

It consumes already-authoritative causal state and produces only:
- frozen EventRelation;
- frozen NewEventEvidence / OpportunityIndependenceEvidence;
- proof-minimal canonical lineage_evidence_refs;
- restartable causal coverage/provenance bookkeeping.

The bookkeeping is evidence/provenance state only.  It is not a parallel
strategy state machine.
"""

from dataclasses import dataclass, field, fields, is_dataclass, replace
from enum import Enum
from fractions import Fraction
from hashlib import sha256
import json
from types import MappingProxyType
from typing import Any, Iterable, Mapping

import nontrading_adapter_integration_v1 as frozen
import authoritative_d3_d4_evidence_packet_assembler_resumption_v2 as assembler
import authoritative_d3_b5_d4_base_runtime_producers_v1 as b5prod
import runtime_b3_price_driven_return_production_state_v1 as b3prod
import d4_deep_takeover_preidentity_causal_fact_production_interface_v1 as deeppre

from d2_to_b4_d4_causal_evidence_producers_v1 import EvidenceState, ProjectionResult
from strategy_rc1.d3_boundary_intelligence.types import InteractionControl, InteractionEvent
from strategy_rc1.d4_opportunity.types import OpportunityIndependenceEvidence, OpportunityState
from strategy_rc1.runtime_guards.information_state import InfoValue


PRODUCER_ID = "D4_MARKET_EVENT_LINEAGE_RELATION_AND_NEW_EVENT_EVIDENCE_PRODUCTION_BINDING_V2"
SEMANTIC_ID = "D4_MARKET_EVENT_LINEAGE_EVIDENCE_SOURCE_ASSOCIATION_V1"
SEMANTIC_CONTRACT_BLOB = "317ceadda177a64fb8ff751caa341bfddc1baaf6"
SEMANTIC_FREEZE_MANIFEST_BLOB = "350f3f9f8419eb8947a7c6df09419c915b76d1bc"
SEMANTIC_TERMINAL_BLOB = "e4ef567a8fab5a6e7a19e0ba6bc1cb70a661b86c"

REARM_PROVENANCE = "MATERIAL_CORRECT_SIDE_SEPARATION"
LOCAL_CONTROL_PRODUCER = "LOCAL_TREND_CONTROL_REGAIN_D2_PROJECTION_V1"

MECH_WATCH = "TREND_ESTABLISHMENT_WATCH_ONLY"
MECH_NORMAL = "NORMAL_RETEST_CONTINUATION"
MECH_FBR = "FALSE_BREAK_RECLAIM"
MECH_PLATFORM = "PLATFORM_REEXPANSION"
MECH_DEEP = "DEEP_STRUCTURE_TAKEOVER"
MECHANISMS = (MECH_WATCH, MECH_NORMAL, MECH_FBR, MECH_PLATFORM, MECH_DEEP)

REF_NAMESPACES = frozenset({
    "HistoryCoverage",
    "TrendEpisode",
    "D2Event",
    "StructuralPivot",
    "InteractionEvent",
    "AnchorEpisode",
    "Platform",
    "BoundarySnapshot",
    "OpportunityTerminal",
    "RearmSeparation",
    "LocalControlRegain",
    "PriceDrivenReturn",
    "SetupParent",
})


class LineageProductionBlock(RuntimeError):
    """Fail-closed production projection block."""


class LineageProductionConflict(LineageProductionBlock):
    """Conflicting authoritative causal lineage."""


@dataclass(frozen=True)
class D4LineageProductionRequest:
    symbol: str
    information_cutoff: int
    trend_episode_id: str
    direction: Any
    canonical_continuity_known: bool
    canonical_continuity_intact: bool
    active_mechanisms: tuple[str, ...] = ()
    trend_establishment_record: b5prod.TrendEstablishmentRecord | None = None
    existing_opportunity: OpportunityState | None = None
    interaction_events: tuple[InteractionEvent, ...] = ()
    runtime_b3_results: tuple[b3prod.RuntimeB3ProducerResult, ...] = ()
    local_control_regain_results: tuple[ProjectionResult, ...] = ()
    mechanisms: assembler.MechanismProducerOutputs = field(default_factory=assembler.MechanismProducerOutputs)
    deep_preidentity: deeppre.DeepTakeoverPreidentityProjection | None = None
    anchor_episode_ids: tuple[str, ...] = ()
    future_evidence_detected: bool = False
    provenance: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class D4LineageProjection:
    status: str
    relation: Any | None
    new_event_evidence: Any | None
    independence: OpportunityIndependenceEvidence | None
    lineage_evidence_refs: tuple[str, ...]
    proof_kinds: tuple[str, ...] = ()
    blocked_reason: str | None = None
    provenance: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class _ObservationAuthority:
    mechanism: str
    principal_refs: tuple[str, ...]
    primitive_refs: tuple[str, ...]
    interaction_refs: tuple[str, ...]
    anchor_refs: tuple[str, ...]
    setup_parent_targets: tuple[str, ...]
    setup_parent_markers: tuple[str, ...]
    platform_contributing_refs: tuple[str, ...]
    watch_genesis: bool = False


@dataclass(frozen=True)
class _CoverageLedger:
    symbol: str
    trend_episode_id: str
    direction_value: str
    genesis_cutoff: int
    coverage_ref: str
    genesis_refs: tuple[str, ...]
    last_evaluated_cutoff: int
    coverage_intact: bool = True
    admission_count: int = 0
    admission_tx_ids: tuple[str, ...] = ()
    active_event_open: bool = False
    current_origin_watch: bool = False
    current_closure_refs: tuple[str, ...] = ()
    previous_terminal_opportunity_id: str | None = None
    previous_terminal_cutoff: int | None = None
    previous_terminal_ref: str | None = None
    reseparation_or_control_cutoff: int | None = None
    reseparation_refs: tuple[str, ...] = ()
    coverage_chain_digest: str = ""


@dataclass(frozen=True)
class _Prepared:
    input_digest: str
    projection: D4LineageProjection
    proposed_ledger: _CoverageLedger | None


def _enum_value(value: Any) -> str:
    return value.value if hasattr(value, "value") else str(value)


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
    if isinstance(value, set):
        return {"$set": [_encode(x) for x in sorted(value, key=str)]}
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    raise TypeError(f"UNSUPPORTED_SERIALIZATION_TYPE:{type(value)!r}")


def exact_json(value: Any) -> str:
    return json.dumps(_encode(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return sha256(exact_json(value).encode("utf-8")).hexdigest()


def _request_input_digest(req: D4LineageProductionRequest) -> str:
    """Canonical transaction digest for scientifically unordered input collections."""
    canonical = replace(
        req,
        active_mechanisms=tuple(sorted(req.active_mechanisms)),
        interaction_events=tuple(
            sorted(req.interaction_events, key=lambda x: (x.event_id, exact_json(x)))
        ),
        runtime_b3_results=tuple(
            sorted(req.runtime_b3_results, key=lambda x: (x.candidate_id, exact_json(x)))
        ),
        local_control_regain_results=tuple(
            sorted(req.local_control_regain_results, key=exact_json)
        ),
        anchor_episode_ids=tuple(sorted(set(req.anchor_episode_ids))),
    )
    return digest(canonical)


def _canon(values: Iterable[str]) -> tuple[str, ...]:
    rows = tuple(sorted(set(str(x) for x in values if isinstance(x, str) and x)))
    for ref in rows:
        ns = ref.split(":", 1)[0]
        if ns not in REF_NAMESPACES:
            raise LineageProductionConflict(f"UNFROZEN_LINEAGE_REF_NAMESPACE:{ns}")
    return rows


def _ref(namespace: str, value: str) -> str:
    if namespace not in REF_NAMESPACES:
        raise LineageProductionConflict(f"UNFROZEN_LINEAGE_REF_NAMESPACE:{namespace}")
    if not isinstance(value, str) or not value:
        raise LineageProductionConflict(f"EMPTY_LINEAGE_REF_VALUE:{namespace}")
    return f"{namespace}:{value}"


def _trend_ref(trend_episode_id: str) -> str:
    return _ref("TrendEpisode", trend_episode_id)


def _event_ref(event_id: str) -> str:
    return _ref("InteractionEvent", event_id)


def _anchor_ref(anchor_episode_id: str) -> str:
    return _ref("AnchorEpisode", anchor_episode_id)


def _known_true(value: Any) -> bool:
    try:
        return value == InfoValue.known(True)
    except Exception:
        return False


def _direction_matches(a: Any, b: Any) -> bool:
    return _enum_value(a) == _enum_value(b)


def _state_value(value: Any) -> str:
    return _enum_value(value)


def _event_actual_contact(event: InteractionEvent, cutoff: int) -> bool:
    return (
        event.started_at is not None
        and event.started_at <= cutoff
        and _state_value(event.control) in ("INTERACTION_ACTIVE", "RESOLVED")
    )


def _coverage_key(req: D4LineageProductionRequest) -> str:
    return json.dumps(
        [req.symbol, req.trend_episode_id, _enum_value(req.direction)],
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _coverage_ref(req: D4LineageProductionRequest, creation_cutoff: int) -> str:
    return _ref(
        "HistoryCoverage",
        f"{req.symbol}:{req.trend_episode_id}:{_enum_value(req.direction)}:{creation_cutoff}",
    )


def _genesis_refs(req: D4LineageProductionRequest) -> tuple[str, ...]:
    record = req.trend_establishment_record
    if record is None:
        raise LineageProductionBlock("TREND_GENESIS_RECORD_REQUIRED")
    trend = record.trend
    episode_id = getattr(trend, "episode_id", None)
    episode_start = getattr(trend, "episode_start_cutoff", None)
    trend_direction = getattr(trend, "direction", None)
    if episode_id != req.trend_episode_id:
        raise LineageProductionConflict("TREND_GENESIS_EPISODE_MISMATCH")
    if trend_direction is not None and not _direction_matches(trend_direction, req.direction):
        raise LineageProductionConflict("TREND_GENESIS_DIRECTION_MISMATCH")
    if record.creation_cutoff != episode_start:
        raise LineageProductionConflict("TREND_GENESIS_CREATION_CUTOFF_MISMATCH")
    if record.creation_cutoff != req.information_cutoff:
        raise LineageProductionBlock("HISTORY_COVERAGE_MUST_BEGIN_AT_AUTHORITATIVE_GENESIS")
    if not record.newest_intermediate_pivot_id or not record.source_event_ids:
        raise LineageProductionBlock("TREND_GENESIS_PROVENANCE_INCOMPLETE")
    refs = [
        _coverage_ref(req, record.creation_cutoff),
        _trend_ref(req.trend_episode_id),
        _ref("StructuralPivot", record.newest_intermediate_pivot_id),
    ]
    refs.extend(_ref("D2Event", x) for x in record.source_event_ids)
    return _canon(refs)


def _start_ledger(req: D4LineageProductionRequest) -> _CoverageLedger:
    refs = _genesis_refs(req)
    coverage = _coverage_ref(req, req.trend_establishment_record.creation_cutoff)  # type: ignore[union-attr]
    seed = sha256(
        json.dumps(
            [PRODUCER_ID, req.symbol, req.trend_episode_id, _enum_value(req.direction), req.information_cutoff, refs],
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()
    return _CoverageLedger(
        symbol=req.symbol,
        trend_episode_id=req.trend_episode_id,
        direction_value=_enum_value(req.direction),
        genesis_cutoff=req.information_cutoff,
        coverage_ref=coverage,
        genesis_refs=refs,
        last_evaluated_cutoff=req.information_cutoff,
        coverage_chain_digest=seed,
    )


def _validate_request(req: D4LineageProductionRequest) -> None:
    if not req.symbol or not req.trend_episode_id:
        raise LineageProductionBlock("SYMBOL_AND_TREND_EPISODE_REQUIRED")
    if not isinstance(req.information_cutoff, int) or req.information_cutoff < 0:
        raise LineageProductionBlock("INFORMATION_CUTOFF_INVALID")
    if _enum_value(req.direction) not in ("LONG", "SHORT"):
        raise LineageProductionConflict("DIRECTION_NOT_LONG_SHORT")
    if not isinstance(req.canonical_continuity_known, bool) or not isinstance(req.canonical_continuity_intact, bool):
        raise LineageProductionBlock("CONTINUITY_FLAGS_REQUIRED")
    if req.future_evidence_detected:
        raise LineageProductionBlock("FUTURE_EVIDENCE_FIREWALL")
    if req.trend_establishment_record is not None and not isinstance(req.trend_establishment_record, b5prod.TrendEstablishmentRecord):
        raise LineageProductionConflict("TREND_ESTABLISHMENT_RECORD_SCHEMA")
    if req.existing_opportunity is not None and not isinstance(req.existing_opportunity, OpportunityState):
        raise LineageProductionConflict("OPPORTUNITY_STATE_SCHEMA")
    if not isinstance(req.mechanisms, assembler.MechanismProducerOutputs):
        raise LineageProductionConflict("MECHANISM_PRODUCER_OUTPUTS_SCHEMA")
    if req.deep_preidentity is not None and not isinstance(req.deep_preidentity, deeppre.DeepTakeoverPreidentityProjection):
        raise LineageProductionConflict("DEEP_PREIDENTITY_PROJECTION_SCHEMA")
    if any(not isinstance(x, InteractionEvent) for x in req.interaction_events):
        raise LineageProductionConflict("INTERACTION_EVENT_SCHEMA")
    if any(not isinstance(x, b3prod.RuntimeB3ProducerResult) for x in req.runtime_b3_results):
        raise LineageProductionConflict("RUNTIME_B3_RESULT_SCHEMA")
    if any(not isinstance(x, ProjectionResult) for x in req.local_control_regain_results):
        raise LineageProductionConflict("LOCAL_CONTROL_PROJECTION_SCHEMA")
    if len(set(req.active_mechanisms)) != len(req.active_mechanisms):
        raise LineageProductionConflict("DUPLICATE_ACTIVE_MECHANISM")
    unknown = sorted(set(req.active_mechanisms) - set(MECHANISMS))
    if unknown:
        raise LineageProductionConflict("UNKNOWN_ACTIVE_MECHANISM:" + ",".join(unknown))


def _collect_interactions(req: D4LineageProductionRequest) -> dict[str, InteractionEvent]:
    rows: dict[str, InteractionEvent] = {}
    def add(event: InteractionEvent | None) -> None:
        if event is None:
            return
        if not isinstance(event, InteractionEvent):
            raise LineageProductionConflict("INTERACTION_EVENT_SCHEMA")
        prior = rows.get(event.event_id)
        if prior is not None and prior != event:
            raise LineageProductionConflict("INTERACTION_EVENT_ID_CONFLICT")
        rows[event.event_id] = event

    for event in req.interaction_events:
        add(event)

    m = req.mechanisms
    if m.normal_retest is not None and m.normal_retest.evidence is not None:
        add(m.normal_retest.evidence.interaction)
    if m.false_break_reclaim is not None:
        add(m.false_break_reclaim.interaction)
    if m.deep_takeover is not None and m.deep_takeover.evidence is not None:
        add(m.deep_takeover.evidence.deeper_interaction)
    if req.deep_preidentity is not None and req.deep_preidentity.facts is not None:
        add(req.deep_preidentity.facts.deeper_interaction)
    return rows


def _resolve_setup_parents(
    setup_lineage: Iterable[str],
    interactions: Mapping[str, InteractionEvent],
    anchor_ids: set[str],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    targets: list[str] = []
    markers: list[str] = []
    for raw in setup_lineage:
        token = str(raw)
        if token in interactions:
            target = _event_ref(token)
            targets.append(target)
            markers.append(_ref("SetupParent", f"InteractionEvent:{token}"))
        elif token in anchor_ids:
            target = _anchor_ref(token)
            targets.append(target)
            markers.append(_ref("SetupParent", f"AnchorEpisode:{token}"))
    return _canon(targets), _canon(markers)


def _observation_authorities(req: D4LineageProductionRequest) -> tuple[_ObservationAuthority, ...]:
    if not req.active_mechanisms:
        return ()
    interactions = _collect_interactions(req)
    anchor_ids = set(req.anchor_episode_ids)
    for event in interactions.values():
        if event.anchor_episode_id:
            anchor_ids.add(event.anchor_episode_id)

    rows: list[_ObservationAuthority] = []
    for mech in sorted(req.active_mechanisms):
        principal: list[str] = []
        primitive: list[str] = [_trend_ref(req.trend_episode_id)]
        interaction_refs: list[str] = []
        anchor_refs: list[str] = []
        setup_targets: tuple[str, ...] = ()
        setup_markers: tuple[str, ...] = ()
        platform_contrib: tuple[str, ...] = ()
        watch_genesis = False

        if mech == MECH_WATCH:
            proj = req.mechanisms.trend_establishment_watch
            if proj is None or _state_value(proj.state) != "TRUE" or proj.evidence is None or proj.evidence.observed is not True:
                raise LineageProductionConflict("ACTIVE_WATCH_WITHOUT_AUTHORITATIVE_WATCH_EVIDENCE")
            ev = proj.evidence
            if not ev.source_event_ids:
                raise LineageProductionBlock("ACTIVE_WATCH_SOURCE_EVENT_IDS_MISSING")
            watch_genesis = True
            principal.extend(_ref("D2Event", x) for x in ev.source_event_ids)
            newest = ev.provenance.get("newest_intermediate_pivot_id")
            if newest:
                principal.append(_ref("StructuralPivot", newest))
            primitive.extend(principal)
            primitive.append(_trend_ref(req.trend_episode_id))

        elif mech == MECH_NORMAL:
            proj = req.mechanisms.normal_retest
            if proj is None or _state_value(proj.state) != "TRUE" or proj.evidence is None:
                raise LineageProductionConflict("ACTIVE_NORMAL_WITHOUT_AUTHORITATIVE_NORMAL_EVIDENCE")
            ev = proj.evidence
            event = ev.interaction
            if event.target_trend_episode_id != req.trend_episode_id or not _direction_matches(event.target_direction, req.direction):
                raise LineageProductionConflict("NORMAL_INTERACTION_TREND_LINEAGE_MISMATCH")
            iref = _event_ref(event.event_id)
            interaction_refs.append(iref)
            principal.append(iref)
            primitive.append(iref)
            if event.anchor_episode_id:
                aref = _anchor_ref(event.anchor_episode_id)
                anchor_refs.append(aref)
                primitive.append(aref)
            setup_targets, setup_markers = _resolve_setup_parents(ev.setup_lineage, interactions, anchor_ids)
            primitive.extend(setup_targets)
            primitive.extend(setup_markers)

        elif mech == MECH_FBR:
            ev = req.mechanisms.false_break_reclaim
            if ev is None:
                raise LineageProductionConflict("ACTIVE_FBR_WITHOUT_AUTHORITATIVE_FBR_EVIDENCE")
            event = ev.interaction
            if event.target_trend_episode_id != req.trend_episode_id or not _direction_matches(event.target_direction, req.direction):
                raise LineageProductionConflict("FBR_INTERACTION_TREND_LINEAGE_MISMATCH")
            iref = _event_ref(event.event_id)
            interaction_refs.append(iref)
            principal.append(iref)
            primitive.append(iref)
            if event.anchor_episode_id:
                aref = _anchor_ref(event.anchor_episode_id)
                anchor_refs.append(aref)
                primitive.append(aref)
            setup_targets, setup_markers = _resolve_setup_parents(ev.setup_lineage, interactions, anchor_ids)
            primitive.extend(setup_targets)
            primitive.extend(setup_markers)

        elif mech == MECH_PLATFORM:
            ev = req.mechanisms.platform_reexpansion
            if ev is None:
                raise LineageProductionConflict("ACTIVE_PLATFORM_WITHOUT_AUTHORITATIVE_PLATFORM_EVIDENCE")
            if ev.target_trend_episode_id != req.trend_episode_id or not _direction_matches(ev.direction, req.direction):
                raise LineageProductionConflict("PLATFORM_TREND_LINEAGE_MISMATCH")
            contributing = tuple(_event_ref(x) for x in ev.platform.contributing_event_ids)
            if not contributing:
                raise LineageProductionBlock("ACTIVE_PLATFORM_CONTRIBUTING_INTERACTION_REFS_MISSING")
            platform_contrib = _canon(contributing)
            principal.extend(platform_contrib)
            primitive.extend(platform_contrib)
            platform_key = sha256(
                json.dumps(
                    [list(ev.platform.contributing_event_ids), ev.platform.confirmed_at],
                    separators=(",", ":"),
                ).encode("utf-8")
            ).hexdigest()
            primitive.append(_ref("Platform", platform_key))
            setup_targets, setup_markers = _resolve_setup_parents(ev.setup_lineage, interactions, anchor_ids)
            primitive.extend(setup_targets)
            primitive.extend(setup_markers)

        elif mech == MECH_DEEP:
            proj = req.mechanisms.deep_takeover
            pre = req.deep_preidentity
            if proj is not None:
                if _state_value(proj.state) != "TRUE" or proj.evidence is None:
                    raise LineageProductionConflict("ACTIVE_DEEP_WITHOUT_AUTHORITATIVE_DEEP_EVIDENCE")
                ev = proj.evidence
                event = ev.deeper_interaction
                setup_lineage = tuple(ev.setup_lineage)
                shallow_no_longer = ev.shallow_operating_defense_no_longer_completes_setup
                deeper_independent = ev.deeper_boundary_independent
                if pre is not None:
                    if _state_value(pre.state) != "TRUE" or pre.facts is None:
                        raise LineageProductionConflict("ACTIVE_DEEP_PREIDENTITY_NOT_AUTHORITATIVE_TRUE")
                    facts = pre.facts
                    if (
                        facts.deeper_interaction != event
                        or tuple(facts.setup_lineage) != setup_lineage
                        or facts.shallow_operating_defense_no_longer_completes_setup is not True
                        or facts.deeper_boundary_independent is not True
                    ):
                        raise LineageProductionConflict("DEEP_PREIDENTITY_AND_AUTHORITATIVE_PROJECTION_MISMATCH")
            elif pre is not None:
                if _state_value(pre.state) != "TRUE" or pre.facts is None:
                    raise LineageProductionConflict("ACTIVE_DEEP_PREIDENTITY_NOT_AUTHORITATIVE_TRUE")
                facts = pre.facts
                event = facts.deeper_interaction
                setup_lineage = tuple(facts.setup_lineage)
                shallow_no_longer = facts.shallow_operating_defense_no_longer_completes_setup
                deeper_independent = facts.deeper_boundary_independent
            else:
                raise LineageProductionConflict("ACTIVE_DEEP_WITHOUT_AUTHORITATIVE_OR_PREIDENTITY_CAUSAL_FACTS")

            if event.target_trend_episode_id != req.trend_episode_id or not _direction_matches(event.target_direction, req.direction):
                raise LineageProductionConflict("DEEP_INTERACTION_TREND_LINEAGE_MISMATCH")
            if not shallow_no_longer or not deeper_independent:
                raise LineageProductionConflict("ACTIVE_DEEP_WITHOUT_FROZEN_CONTINUATION_FACTS")
            iref = _event_ref(event.event_id)
            interaction_refs.append(iref)
            principal.append(iref)
            primitive.append(iref)
            if event.anchor_episode_id:
                aref = _anchor_ref(event.anchor_episode_id)
                anchor_refs.append(aref)
                primitive.append(aref)
            setup_targets, setup_markers = _resolve_setup_parents(setup_lineage, interactions, anchor_ids)
            primitive.extend(setup_targets)
            primitive.extend(setup_markers)

        rows.append(
            _ObservationAuthority(
                mechanism=mech,
                principal_refs=_canon(principal),
                primitive_refs=_canon(primitive),
                interaction_refs=_canon(interaction_refs),
                anchor_refs=_canon(anchor_refs),
                setup_parent_targets=setup_targets,
                setup_parent_markers=setup_markers,
                platform_contributing_refs=platform_contrib,
                watch_genesis=watch_genesis,
            )
        )
    return tuple(rows)


def _connected_component_count(rows: tuple[_ObservationAuthority, ...]) -> int:
    if not rows:
        return 0
    sets = [set(r.primitive_refs) - {x for x in r.primitive_refs if x.startswith("TrendEpisode:")} for r in rows]
    seen: set[int] = set()
    components = 0
    for i in range(len(rows)):
        if i in seen:
            continue
        components += 1
        frontier = [i]
        seen.add(i)
        while frontier:
            cur = frontier.pop()
            for j in range(len(rows)):
                if j in seen:
                    continue
                if sets[cur] and sets[j] and sets[cur].intersection(sets[j]):
                    seen.add(j)
                    frontier.append(j)
    return components


def _principal_proof_refs(rows: tuple[_ObservationAuthority, ...]) -> tuple[str, ...]:
    refs: list[str] = []
    for row in rows:
        if not row.principal_refs:
            raise LineageProductionBlock(f"ACTIVE_MECHANISM_PRINCIPAL_CAUSAL_REF_MISSING:{row.mechanism}")
        refs.extend(row.principal_refs)
    return _canon(refs)


def _select_unique_minimal_proof(candidates: list[tuple[str, tuple[str, ...]]]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    if not candidates:
        raise LineageProductionBlock("NO_AUTHORITATIVE_SAME_EVENT_CAUSAL_EDGE")
    normalized: dict[tuple[str, ...], set[str]] = {}
    for kind, refs in candidates:
        normalized.setdefault(_canon(refs), set()).add(kind)
    min_len = min(len(x) for x in normalized)
    minimal = [refs for refs in normalized if len(refs) == min_len]
    # No lexical/mechanism priority is permitted.  Distinct equally-minimal
    # proof sets remain an ambiguity and block.
    if len(minimal) != 1:
        raise LineageProductionConflict("MULTIPLE_INCOMPARABLE_MINIMAL_SAME_EVENT_PROOFS")
    refs = minimal[0]
    kinds = tuple(sorted(normalized[refs]))
    return refs, kinds


def _same_event_proof(
    ledger: _CoverageLedger,
    rows: tuple[_ObservationAuthority, ...],
) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    closure = set(ledger.current_closure_refs)
    if not ledger.active_event_open:
        raise LineageProductionBlock("SAME_EVENT_REQUIRES_COMMITTED_ACTIVE_EVENT")
    all_proof_refs: list[str] = [ledger.coverage_ref, _trend_ref(ledger.trend_episode_id)]
    all_kinds: list[str] = []
    extension: list[str] = list(ledger.current_closure_refs)

    for row in rows:
        candidates: list[tuple[str, tuple[str, ...]]] = []

        for ref in row.interaction_refs:
            if ref in closure:
                candidates.append(("SAME_INTERACTION_EVENT", _canon([ledger.coverage_ref, ref])))

        for target, marker in zip(row.setup_parent_targets, row.setup_parent_markers):
            if target in closure:
                refs = [ledger.coverage_ref, target, marker]
                refs.extend(row.principal_refs)
                candidates.append(("EXPLICIT_SETUP_PARENT", _canon(refs)))

        if row.platform_contributing_refs:
            contrib = set(row.platform_contributing_refs)
            if contrib.issubset(closure):
                candidates.append(
                    ("PLATFORM_CONTRIBUTING_INTERACTION", _canon([ledger.coverage_ref, *row.platform_contributing_refs]))
                )
            elif contrib.intersection(closure):
                raise LineageProductionConflict("PLATFORM_CONTRIBUTING_LINEAGE_PARTIALLY_OUTSIDE_CURRENT_EVENT")

        if row.mechanism == MECH_DEEP and row.setup_parent_targets:
            parents = tuple(x for x in row.setup_parent_targets if x in closure)
            if parents:
                refs = [ledger.coverage_ref, *parents, *row.principal_refs]
                candidates.append(("DEEPER_CONTINUATION_FROM_ACTIVE_SHALLOW_SETUP", _canon(refs)))

        if ledger.current_origin_watch and row.mechanism != MECH_WATCH:
            fresh_refs = tuple(
                x for x in row.principal_refs
                if x.startswith("InteractionEvent:") or x.startswith("Platform:")
            )
            if not fresh_refs:
                fresh_refs = row.principal_refs
            if fresh_refs:
                candidates.append(
                    ("WATCH_GENESIS_CONTINUATION", _canon([ledger.coverage_ref, _trend_ref(ledger.trend_episode_id), *fresh_refs]))
                )

        proof_refs, kinds = _select_unique_minimal_proof(candidates)
        all_proof_refs.extend(proof_refs)
        all_kinds.extend(kinds)
        extension.extend(row.primitive_refs)

    return _canon(all_proof_refs), tuple(sorted(set(all_kinds))), _canon(extension)


def _local_control_branch(
    req: D4LineageProductionRequest,
    terminal_cutoff: int,
) -> list[tuple[int, tuple[str, ...]]]:
    rows: list[tuple[int, tuple[str, ...]]] = []
    for result in req.local_control_regain_results:
        if result.producer != LOCAL_CONTROL_PRODUCER:
            raise LineageProductionConflict("LOCAL_CONTROL_PRODUCER_ID_MISMATCH")
        if result.state is EvidenceState.CONFLICT:
            raise LineageProductionConflict("LOCAL_CONTROL_PROJECTION_CONFLICT")
        if result.state is EvidenceState.UNKNOWN:
            continue
        if result.state is not EvidenceState.TRUE:
            continue
        ev = result.consumer_evidence
        if ev is None:
            raise LineageProductionConflict("LOCAL_CONTROL_TRUE_WITHOUT_CONSUMER_EVIDENCE")
        if not _direction_matches(ev.direction, req.direction):
            raise LineageProductionConflict("LOCAL_CONTROL_DIRECTION_MISMATCH")
        target = result.provenance.get("target_trend_episode_id")
        if target and target != req.trend_episode_id:
            raise LineageProductionConflict("LOCAL_CONTROL_TREND_EPISODE_MISMATCH")
        if not (_known_true(ev.countertrend_progression_failed) and _known_true(ev.material_original_direction_closed_price_recovery)):
            raise LineageProductionConflict("LOCAL_CONTROL_TRUE_CONSTITUENTS_NOT_AUTHORITATIVE_TRUE")
        if not result.provenance or ev.confirmation_cutoff < terminal_cutoff:
            continue
        source_refs_raw = result.provenance.get("source_evidence_refs")
        if not source_refs_raw:
            raise LineageProductionBlock("LOCAL_CONTROL_SOURCE_EVIDENCE_REFS_MISSING")
        try:
            source_refs = tuple(str(x) for x in json.loads(source_refs_raw))
        except Exception as exc:
            raise LineageProductionConflict("LOCAL_CONTROL_SOURCE_EVIDENCE_REFS_INVALID") from exc
        if not source_refs:
            raise LineageProductionBlock("LOCAL_CONTROL_SOURCE_EVIDENCE_REFS_EMPTY")
        key = f"{ev.adverse_reference_pivot_id}:{ev.recovery_pivot_id}:{ev.confirmation_cutoff}"
        refs = [
            _ref("LocalControlRegain", key),
            _ref("StructuralPivot", ev.adverse_reference_pivot_id),
            _ref("StructuralPivot", ev.recovery_pivot_id),
            _trend_ref(req.trend_episode_id),
        ]
        # Existing producer refs may not use the D4 namespace grammar; retain
        # their causal identities only when they resolve to one of the already
        # frozen typed namespaces.  The structural refs above remain mandatory.
        for raw in source_refs:
            if ":" in raw and raw.split(":", 1)[0] in REF_NAMESPACES:
                refs.append(raw)
        rows.append((ev.confirmation_cutoff, _canon(refs)))
    return rows


def _rearm_branch(
    req: D4LineageProductionRequest,
    terminal_cutoff: int,
) -> list[tuple[int, tuple[str, ...]]]:
    rows: list[tuple[int, tuple[str, ...]]] = []
    for event in _collect_interactions(req).values():
        if event.target_trend_episode_id != req.trend_episode_id or not _direction_matches(event.target_direction, req.direction):
            continue
        if _state_value(event.control) != "ARMED":
            continue
        if event.armed_at is None or event.armed_at < terminal_cutoff:
            continue
        if event.provenance.get("rearm") != REARM_PROVENANCE:
            continue
        refs = [
            _ref("RearmSeparation", f"{event.event_id}:{event.armed_at}"),
            _event_ref(event.event_id),
            _trend_ref(req.trend_episode_id),
        ]
        if event.anchor_episode_id:
            refs.append(_anchor_ref(event.anchor_episode_id))
        rows.append((event.armed_at, _canon(refs)))
    return rows


def _first_reseparation_truth(
    req: D4LineageProductionRequest,
    ledger: _CoverageLedger,
) -> tuple[int | None, tuple[str, ...]]:
    if ledger.previous_terminal_cutoff is None:
        return None, ()
    if ledger.reseparation_or_control_cutoff is not None:
        return ledger.reseparation_or_control_cutoff, ledger.reseparation_refs

    candidates = _rearm_branch(req, ledger.previous_terminal_cutoff)
    candidates.extend(_local_control_branch(req, ledger.previous_terminal_cutoff))
    if not candidates:
        return None, ()
    cutoff = min(x[0] for x in candidates)
    # Complete coverage means a newly discovered first-truth fact cannot be
    # backfilled from an already-passed projector cutoff.
    if cutoff < req.information_cutoff:
        raise LineageProductionConflict("RESEPARATION_FIRST_TRUTH_RETROACTIVE_UNDER_COMPLETE_COVERAGE")
    refs: list[str] = []
    for candidate_cutoff, candidate_refs in candidates:
        if candidate_cutoff == cutoff:
            refs.extend(candidate_refs)
    return cutoff, _canon(refs)


def _qualifying_b3_lineages(
    req: D4LineageProductionRequest,
    event: InteractionEvent,
    reseparation_cutoff: int,
) -> tuple[b3prod.RuntimeB3PendingLineage, ...]:
    unique: dict[tuple[Any, ...], b3prod.RuntimeB3PendingLineage] = {}
    for result in req.runtime_b3_results:
        if result.candidate_id != event.candidate_id:
            continue
        lineage = result.pending_lineage
        if lineage is None:
            continue
        if lineage.target_trend_episode_id != req.trend_episode_id:
            continue
        if lineage.target_direction != _enum_value(req.direction):
            continue
        if event.armed_at is None or lineage.arming_information_cutoff != event.armed_at:
            continue
        if lineage.arming_information_cutoff < reseparation_cutoff:
            continue
        q = lineage.qualifying_return_information_cutoff
        evidence = lineage.evidence
        if q is None or evidence is None or evidence.passed is not True:
            continue
        if q <= lineage.arming_information_cutoff:
            raise LineageProductionConflict("B3_RETURN_QUALIFICATION_NOT_STRICTLY_AFTER_ARMING")
        if event.started_at is None or q >= event.started_at:
            continue
        key = (
            lineage.candidate_id,
            lineage.arming_snapshot_id,
            lineage.arming_information_cutoff,
            q,
            lineage.source_segment_id,
        )
        unique[key] = lineage
    return tuple(unique[k] for k in sorted(unique, key=lambda x: tuple(str(v) for v in x)))


def _new_return_candidates(
    req: D4LineageProductionRequest,
    reseparation_cutoff: int,
) -> tuple[tuple[InteractionEvent, b3prod.RuntimeB3PendingLineage, tuple[str, ...]], ...]:
    rows: list[tuple[InteractionEvent, b3prod.RuntimeB3PendingLineage, tuple[str, ...]]] = []
    for event in _collect_interactions(req).values():
        if event.target_trend_episode_id != req.trend_episode_id or not _direction_matches(event.target_direction, req.direction):
            continue
        if not _event_actual_contact(event, req.information_cutoff):
            continue
        if event.started_at is None or event.started_at <= reseparation_cutoff:
            continue
        if event.armed_at is None or event.armed_at < reseparation_cutoff:
            continue
        lineages = _qualifying_b3_lineages(req, event, reseparation_cutoff)
        if not lineages:
            continue
        if len(lineages) != 1:
            raise LineageProductionConflict("MULTIPLE_B3_PENDING_LINEAGES_MATCH_ONE_INTERACTION")
        lineage = lineages[0]
        q = lineage.qualifying_return_information_cutoff
        assert q is not None
        refs = [
            _trend_ref(req.trend_episode_id),
            _event_ref(event.event_id),
            _ref("BoundarySnapshot", lineage.arming_snapshot_id),
            _ref("PriceDrivenReturn", f"{lineage.candidate_id}:{lineage.arming_information_cutoff}:{q}"),
        ]
        if event.anchor_episode_id:
            refs.append(_anchor_ref(event.anchor_episode_id))
        rows.append((event, lineage, _canon(refs)))
    rows.sort(key=lambda x: (x[0].started_at if x[0].started_at is not None else -1, x[0].event_id))
    return tuple(rows)


def _new_event_fact(
    req: D4LineageProductionRequest,
    ledger: _CoverageLedger,
    active_rows: tuple[_ObservationAuthority, ...],
) -> tuple[int | None, tuple[str, ...], tuple[str, ...]]:
    resep = ledger.reseparation_or_control_cutoff
    if resep is None:
        return None, (), ()
    candidates = _new_return_candidates(req, resep)
    if not candidates:
        return None, (), ()
    first_cutoff = candidates[0][0].started_at
    assert first_cutoff is not None
    first = tuple(x for x in candidates if x[0].started_at == first_cutoff)
    if first_cutoff != req.information_cutoff:
        raise LineageProductionConflict("NEW_EVENT_FIRST_CAUSAL_CUTOFF_MISSED")
    if first_cutoff <= resep:
        raise LineageProductionBlock("NEW_EVENT_SAME_CUTOFF_OR_PRE_RESEPARATION_BLOCKED")

    candidate_refs = {_event_ref(x[0].event_id) for x in first}
    if len(candidate_refs) > 1:
        # Multiple earliest InteractionEvents may be admitted as one event only
        # if the already-authoritative active mechanism lineage itself connects
        # every candidate event into one causal group.  No winner is chosen.
        if not active_rows:
            raise LineageProductionConflict("MULTIPLE_EARLIEST_NEW_RETURN_EVENTS_WITHOUT_CAUSAL_GROUP")
        primitive_union = set()
        for row in active_rows:
            primitive_union.update(row.primitive_refs)
        if not candidate_refs.issubset(primitive_union) or _connected_component_count(active_rows) != 1:
            raise LineageProductionConflict("MULTIPLE_EARLIEST_DISCONNECTED_NEW_RETURN_EVENTS")

    refs: list[str] = []
    for _, _, proof in first:
        refs.extend(proof)
    # Every current active observation must attach to the selected new-event
    # interaction group; otherwise relation is ambiguous and no mechanism wins.
    if active_rows:
        seed = set(refs)
        for row in active_rows:
            if not seed.intersection(row.primitive_refs):
                raise LineageProductionConflict("ACTIVE_MECHANISM_NOT_CONNECTED_TO_NEW_EVENT_CAUSAL_GROUP")
            refs.extend(row.principal_refs)
    return first_cutoff, _canon(refs), tuple(sorted(candidate_refs))


def _record_terminal(
    req: D4LineageProductionRequest,
    ledger: _CoverageLedger,
) -> _CoverageLedger:
    opp = req.existing_opportunity
    if opp is None or not opp.terminal:
        return ledger
    if opp.trend_episode_id != req.trend_episode_id or not _direction_matches(opp.direction, req.direction):
        raise LineageProductionConflict("TERMINAL_OPPORTUNITY_TREND_LINEAGE_MISMATCH")
    if opp.terminated_at is None:
        raise LineageProductionBlock("TERMINAL_OPPORTUNITY_TERMINATED_AT_REQUIRED")
    if opp.terminated_at > req.information_cutoff:
        raise LineageProductionConflict("FUTURE_TERMINAL_OPPORTUNITY")
    if ledger.admission_count <= 0:
        raise LineageProductionConflict("TERMINAL_OPPORTUNITY_WITHOUT_RETAINED_D4_ADMISSION")
    ref = _ref("OpportunityTerminal", f"{opp.opportunity_id}:{opp.terminated_at}")
    if ledger.previous_terminal_cutoff is not None:
        if (
            ledger.previous_terminal_cutoff != opp.terminated_at
            or ledger.previous_terminal_opportunity_id != opp.opportunity_id
        ):
            raise LineageProductionConflict("TERMINAL_OPPORTUNITY_PROVENANCE_CHANGED")
        return ledger
    return replace(
        ledger,
        active_event_open=False,
        previous_terminal_opportunity_id=opp.opportunity_id,
        previous_terminal_cutoff=opp.terminated_at,
        previous_terminal_ref=ref,
        reseparation_or_control_cutoff=None,
        reseparation_refs=(),
    )


def _validate_active_opportunity_consistency(
    req: D4LineageProductionRequest,
    ledger: _CoverageLedger,
) -> None:
    opp = req.existing_opportunity
    if opp is None:
        return
    if opp.trend_episode_id != req.trend_episode_id or not _direction_matches(opp.direction, req.direction):
        raise LineageProductionConflict("OPPORTUNITY_TREND_LINEAGE_MISMATCH")
    if not opp.terminal:
        if ledger.admission_count == 0:
            raise LineageProductionConflict("ACTIVE_OPPORTUNITY_WITHOUT_RETAINED_D4_ADMISSION")
        if not ledger.active_event_open:
            raise LineageProductionConflict("ACTIVE_OPPORTUNITY_AFTER_RETAINED_TERMINAL_STATE")


def _advance_chain(ledger: _CoverageLedger, tx_id: str, input_digest: str, cutoff: int) -> _CoverageLedger:
    chain = sha256(
        json.dumps(
            [ledger.coverage_chain_digest, tx_id, input_digest, cutoff],
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    return replace(ledger, last_evaluated_cutoff=cutoff, coverage_chain_digest=chain)


def _result(
    *,
    status: str,
    relation: Any | None = None,
    new_event_evidence: Any | None = None,
    independence: OpportunityIndependenceEvidence | None = None,
    refs: Iterable[str] = (),
    proof_kinds: Iterable[str] = (),
    blocked_reason: str | None = None,
    ledger: _CoverageLedger | None = None,
) -> D4LineageProjection:
    prov = {
        "producer_id": PRODUCER_ID,
        "semantic_id": SEMANTIC_ID,
        "semantic_contract_blob": SEMANTIC_CONTRACT_BLOB,
        "semantic_freeze_manifest_blob": SEMANTIC_FREEZE_MANIFEST_BLOB,
    }
    if ledger is not None:
        prov.update(
            {
                "coverage_ref": ledger.coverage_ref,
                "coverage_chain_digest": ledger.coverage_chain_digest,
                "admission_count": str(ledger.admission_count),
            }
        )
    return D4LineageProjection(
        status=status,
        relation=relation,
        new_event_evidence=new_event_evidence,
        independence=independence,
        lineage_evidence_refs=_canon(refs),
        proof_kinds=tuple(sorted(set(proof_kinds))),
        blocked_reason=blocked_reason,
        provenance=MappingProxyType(dict(sorted(prov.items()))),
    )


def _compute_projection(
    req: D4LineageProductionRequest,
    ledger: _CoverageLedger | None,
    *,
    tx_id: str,
    input_digest: str,
) -> tuple[D4LineageProjection, _CoverageLedger | None]:
    _validate_request(req)

    if ledger is None:
        if req.trend_establishment_record is None:
            raise LineageProductionBlock("HISTORY_COVERAGE_NOT_ESTABLISHED")
        ledger = _start_ledger(req)
    else:
        if ledger.symbol != req.symbol or ledger.trend_episode_id != req.trend_episode_id:
            raise LineageProductionConflict("COVERAGE_LEDGER_SCOPE_MISMATCH")
        if ledger.direction_value != _enum_value(req.direction):
            raise LineageProductionConflict("COVERAGE_LEDGER_DIRECTION_MISMATCH")
        if req.information_cutoff <= ledger.last_evaluated_cutoff:
            raise LineageProductionConflict("NON_MONOTONIC_OR_DUPLICATE_CUTOFF_WITH_NEW_TRANSACTION")
        if req.trend_establishment_record is not None:
            record = req.trend_establishment_record
            if (
                getattr(record.trend, "episode_id", None) != ledger.trend_episode_id
                or record.creation_cutoff != ledger.genesis_cutoff
            ):
                raise LineageProductionConflict("TREND_GENESIS_RECORD_CHANGED_AFTER_COVERAGE_START")

    if not req.canonical_continuity_known or not req.canonical_continuity_intact:
        broken = replace(ledger, coverage_intact=False, active_event_open=False)
        broken = _advance_chain(broken, tx_id, input_digest, req.information_cutoff)
        return (
            _result(
                status="COVERAGE_BROKEN_BLOCKED",
                blocked_reason="CANONICAL_CONTINUITY_NOT_AUTHORITATIVE",
                ledger=broken,
            ),
            broken,
        )
    if not ledger.coverage_intact:
        raise LineageProductionBlock("HISTORY_COVERAGE_PREVIOUSLY_BROKEN")

    _validate_active_opportunity_consistency(req, ledger)
    ledger = _record_terminal(req, ledger)

    resep_cutoff, resep_refs = _first_reseparation_truth(req, ledger)
    if resep_cutoff is not None and ledger.reseparation_or_control_cutoff is None:
        ledger = replace(
            ledger,
            reseparation_or_control_cutoff=resep_cutoff,
            reseparation_refs=resep_refs,
        )

    active_rows = _observation_authorities(req)
    relation = None
    new_event_evidence = None
    independence = None
    lineage_refs: tuple[str, ...] = ()
    proof_kinds: tuple[str, ...] = ()
    status = "NO_ACTIVE_D4_OBSERVATION"

    if ledger.previous_terminal_cutoff is not None:
        new_cutoff, new_refs, _ = _new_event_fact(req, ledger, active_rows)
        if new_cutoff is None:
            status = "TERMINAL_PRIOR_AWAITING_COMPLETE_NEW_EVENT_EVIDENCE"
        else:
            if ledger.previous_terminal_ref is None or ledger.reseparation_or_control_cutoff is None:
                raise LineageProductionConflict("NEW_EVENT_INTERNAL_PROVENANCE_INCOMPLETE")
            evidence_refs = _canon(
                [
                    ledger.previous_terminal_ref,
                    *ledger.reseparation_refs,
                    *new_refs,
                    ledger.coverage_ref,
                    _trend_ref(req.trend_episode_id),
                ]
            )
            new_event_evidence = frozen.NewEventEvidence(
                previous_opportunity_terminated=True,
                material_trend_side_reseparation_or_control=True,
                new_independent_countertrend_or_boundary_return_event=True,
                previous_terminal_cutoff=ledger.previous_terminal_cutoff,
                reseparation_or_control_cutoff=ledger.reseparation_or_control_cutoff,
                new_event_cutoff=new_cutoff,
                evidence_refs=evidence_refs,
            )
            independence = OpportunityIndependenceEvidence(
                previous_opportunity_terminated=True,
                material_trend_side_reseparation_or_control=True,
                new_independent_countertrend_or_boundary_return_event=True,
                provenance={
                    "producer_id": PRODUCER_ID,
                    "semantic_id": SEMANTIC_ID,
                    "previous_terminal_cutoff": str(ledger.previous_terminal_cutoff),
                    "reseparation_or_control_cutoff": str(ledger.reseparation_or_control_cutoff),
                    "new_event_cutoff": str(new_cutoff),
                },
            )
            relation = frozen.EventRelation.NEW_INDEPENDENT_EVENT
            lineage_refs = evidence_refs
            proof_kinds = ("NEW_INDEPENDENT_EVENT_THREE_FACT_CAUSAL_CHAIN",)
            status = "KNOWN_NEW_INDEPENDENT_EVENT"
            closure = list(new_refs)
            for row in active_rows:
                closure.extend(row.primitive_refs)
            ledger = replace(
                ledger,
                admission_count=ledger.admission_count + 1,
                admission_tx_ids=ledger.admission_tx_ids + (tx_id,),
                active_event_open=True,
                current_origin_watch=False,
                current_closure_refs=_canon(closure),
                previous_terminal_opportunity_id=None,
                previous_terminal_cutoff=None,
                previous_terminal_ref=None,
                reseparation_or_control_cutoff=None,
                reseparation_refs=(),
            )

    elif ledger.admission_count == 0:
        if active_rows:
            if len(active_rows) > 1 and _connected_component_count(active_rows) != 1:
                raise LineageProductionConflict("MULTIPLE_DISCONNECTED_FIRST_EVENT_OBSERVATION_GROUPS")
            principal = _principal_proof_refs(active_rows)
            lineage_refs = _canon([*ledger.genesis_refs, *principal])
            relation = frozen.EventRelation.START_FIRST_EVENT
            proof_kinds = ("GENESIS_COVERAGE_FIRST_AUTHORITATIVE_ACTIVE_OBSERVATION",)
            status = "KNOWN_START_FIRST_EVENT"
            closure: list[str] = list(ledger.genesis_refs)
            for row in active_rows:
                closure.extend(row.primitive_refs)
            ledger = replace(
                ledger,
                admission_count=1,
                admission_tx_ids=ledger.admission_tx_ids + (tx_id,),
                active_event_open=True,
                current_origin_watch=any(x.watch_genesis for x in active_rows),
                current_closure_refs=_canon(closure),
            )

    else:
        if active_rows:
            refs, kinds, extension = _same_event_proof(ledger, active_rows)
            relation = frozen.EventRelation.SAME_EVENT
            lineage_refs = refs
            proof_kinds = kinds
            status = "KNOWN_SAME_EVENT"
            ledger = replace(ledger, current_closure_refs=extension)

    ledger = _advance_chain(ledger, tx_id, input_digest, req.information_cutoff)

    projection = _result(
        status=status,
        relation=relation,
        new_event_evidence=new_event_evidence,
        independence=independence,
        refs=lineage_refs,
        proof_kinds=proof_kinds,
        blocked_reason=None if relation is not None else status,
        ledger=ledger,
    )
    return projection, ledger


def bind_d4_static_authority(
    base: assembler.D4StaticAuthority,
    projection: D4LineageProjection,
) -> assembler.D4StaticAuthority:
    """Mechanically bind the projector output to Assembler V2 D4StaticAuthority."""
    if projection.relation is None:
        raise LineageProductionBlock("CANNOT_BIND_BLOCKED_OR_NO_RELATION_PROJECTION")
    if projection.relation in (frozen.EventRelation.UNKNOWN, frozen.EventRelation.CONFLICT):
        raise LineageProductionBlock("CANNOT_BIND_UNKNOWN_OR_CONFLICT_RELATION")
    if not projection.lineage_evidence_refs:
        raise LineageProductionBlock("KNOWN_RELATION_REQUIRES_LINEAGE_EVIDENCE_REFS")
    if projection.relation is frozen.EventRelation.NEW_INDEPENDENT_EVENT and projection.new_event_evidence is None:
        raise LineageProductionConflict("NEW_EVENT_RELATION_WITHOUT_NEW_EVENT_EVIDENCE")
    if projection.relation is not frozen.EventRelation.NEW_INDEPENDENT_EVENT and projection.new_event_evidence is not None:
        raise LineageProductionConflict("NON_NEW_EVENT_RELATION_CARRIES_NEW_EVENT_EVIDENCE")
    return replace(
        base,
        relation=projection.relation,
        new_event_evidence=projection.new_event_evidence,
        independence=projection.independence,
        lineage_evidence_refs=projection.lineage_evidence_refs,
    )


def _ledger_record(ledger: _CoverageLedger) -> Mapping[str, Any]:
    return {
        "symbol": ledger.symbol,
        "trend_episode_id": ledger.trend_episode_id,
        "direction_value": ledger.direction_value,
        "genesis_cutoff": ledger.genesis_cutoff,
        "coverage_ref": ledger.coverage_ref,
        "genesis_refs": list(ledger.genesis_refs),
        "last_evaluated_cutoff": ledger.last_evaluated_cutoff,
        "coverage_intact": ledger.coverage_intact,
        "admission_count": ledger.admission_count,
        "admission_tx_ids": list(ledger.admission_tx_ids),
        "active_event_open": ledger.active_event_open,
        "current_origin_watch": ledger.current_origin_watch,
        "current_closure_refs": list(ledger.current_closure_refs),
        "previous_terminal_opportunity_id": ledger.previous_terminal_opportunity_id,
        "previous_terminal_cutoff": ledger.previous_terminal_cutoff,
        "previous_terminal_ref": ledger.previous_terminal_ref,
        "reseparation_or_control_cutoff": ledger.reseparation_or_control_cutoff,
        "reseparation_refs": list(ledger.reseparation_refs),
        "coverage_chain_digest": ledger.coverage_chain_digest,
    }


def _ledger_from_record(row: Mapping[str, Any]) -> _CoverageLedger:
    return _CoverageLedger(
        symbol=str(row["symbol"]),
        trend_episode_id=str(row["trend_episode_id"]),
        direction_value=str(row["direction_value"]),
        genesis_cutoff=int(row["genesis_cutoff"]),
        coverage_ref=str(row["coverage_ref"]),
        genesis_refs=_canon(tuple(row["genesis_refs"])),
        last_evaluated_cutoff=int(row["last_evaluated_cutoff"]),
        coverage_intact=bool(row["coverage_intact"]),
        admission_count=int(row["admission_count"]),
        admission_tx_ids=tuple(str(x) for x in row["admission_tx_ids"]),
        active_event_open=bool(row["active_event_open"]),
        current_origin_watch=bool(row["current_origin_watch"]),
        current_closure_refs=_canon(tuple(row["current_closure_refs"])),
        previous_terminal_opportunity_id=row.get("previous_terminal_opportunity_id"),
        previous_terminal_cutoff=row.get("previous_terminal_cutoff"),
        previous_terminal_ref=row.get("previous_terminal_ref"),
        reseparation_or_control_cutoff=row.get("reseparation_or_control_cutoff"),
        reseparation_refs=_canon(tuple(row.get("reseparation_refs", ()))),
        coverage_chain_digest=str(row["coverage_chain_digest"]),
    )


def _projection_record(p: D4LineageProjection) -> Mapping[str, Any]:
    ev = p.new_event_evidence
    ind = p.independence
    return {
        "status": p.status,
        "relation": None if p.relation is None else _enum_value(p.relation),
        "new_event_evidence": None if ev is None else {
            "previous_opportunity_terminated": ev.previous_opportunity_terminated,
            "material_trend_side_reseparation_or_control": ev.material_trend_side_reseparation_or_control,
            "new_independent_countertrend_or_boundary_return_event": ev.new_independent_countertrend_or_boundary_return_event,
            "previous_terminal_cutoff": ev.previous_terminal_cutoff,
            "reseparation_or_control_cutoff": ev.reseparation_or_control_cutoff,
            "new_event_cutoff": ev.new_event_cutoff,
            "evidence_refs": list(ev.evidence_refs),
        },
        "independence": None if ind is None else {
            "previous_opportunity_terminated": ind.previous_opportunity_terminated,
            "material_trend_side_reseparation_or_control": ind.material_trend_side_reseparation_or_control,
            "new_independent_countertrend_or_boundary_return_event": ind.new_independent_countertrend_or_boundary_return_event,
            "provenance": dict(ind.provenance),
        },
        "lineage_evidence_refs": list(p.lineage_evidence_refs),
        "proof_kinds": list(p.proof_kinds),
        "blocked_reason": p.blocked_reason,
        "provenance": dict(p.provenance),
    }


def _projection_from_record(row: Mapping[str, Any]) -> D4LineageProjection:
    relation = None if row["relation"] is None else frozen.EventRelation(row["relation"])
    evr = row.get("new_event_evidence")
    ev = None
    if evr is not None:
        ev = frozen.NewEventEvidence(
            previous_opportunity_terminated=bool(evr["previous_opportunity_terminated"]),
            material_trend_side_reseparation_or_control=bool(evr["material_trend_side_reseparation_or_control"]),
            new_independent_countertrend_or_boundary_return_event=bool(evr["new_independent_countertrend_or_boundary_return_event"]),
            previous_terminal_cutoff=evr["previous_terminal_cutoff"],
            reseparation_or_control_cutoff=evr["reseparation_or_control_cutoff"],
            new_event_cutoff=evr["new_event_cutoff"],
            evidence_refs=_canon(tuple(evr["evidence_refs"])),
        )
    ir = row.get("independence")
    ind = None
    if ir is not None:
        ind = OpportunityIndependenceEvidence(
            previous_opportunity_terminated=bool(ir["previous_opportunity_terminated"]),
            material_trend_side_reseparation_or_control=bool(ir["material_trend_side_reseparation_or_control"]),
            new_independent_countertrend_or_boundary_return_event=bool(ir["new_independent_countertrend_or_boundary_return_event"]),
            provenance={str(k): str(v) for k, v in ir.get("provenance", {}).items()},
        )
    return D4LineageProjection(
        status=str(row["status"]),
        relation=relation,
        new_event_evidence=ev,
        independence=ind,
        lineage_evidence_refs=_canon(tuple(row.get("lineage_evidence_refs", ()))),
        proof_kinds=tuple(str(x) for x in row.get("proof_kinds", ())),
        blocked_reason=row.get("blocked_reason"),
        provenance=MappingProxyType({str(k): str(v) for k, v in row.get("provenance", {}).items()}),
    )


class D4MarketEventLineageProductionProjectorV2:
    """Two-phase transactional causal-evidence projector.

    prepare() computes a projection and proposed coverage ledger without making
    it authoritative. commit() applies that ledger only after the caller's
    downstream packet transaction succeeds. abort() leaves committed lineage
    state untouched.
    """

    def __init__(
        self,
        *,
        ledgers: Mapping[str, _CoverageLedger] | None = None,
        committed_transactions: Mapping[str, tuple[str, Mapping[str, Any]]] | None = None,
    ) -> None:
        self._ledgers = dict(ledgers or {})
        self._committed_transactions = {
            str(k): (str(v[0]), dict(v[1])) for k, v in (committed_transactions or {}).items()
        }
        self._pending: dict[str, _Prepared] = {}

    def prepare(self, transaction_id: str, request: D4LineageProductionRequest) -> D4LineageProjection:
        if not isinstance(transaction_id, str) or not transaction_id:
            raise LineageProductionBlock("TRANSACTION_ID_REQUIRED")
        if not isinstance(request, D4LineageProductionRequest):
            raise LineageProductionConflict("LINEAGE_PRODUCTION_REQUEST_SCHEMA")
        _validate_request(request)
        input_digest = _request_input_digest(request)

        committed = self._committed_transactions.get(transaction_id)
        if committed is not None:
            if committed[0] != input_digest:
                raise LineageProductionConflict("SAME_TRANSACTION_DIFFERENT_INPUT")
            return _projection_from_record(committed[1])

        pending = self._pending.get(transaction_id)
        if pending is not None:
            if pending.input_digest != input_digest:
                raise LineageProductionConflict("SAME_TRANSACTION_DIFFERENT_INPUT")
            return pending.projection

        key = _coverage_key(request)
        prior = self._ledgers.get(key)
        projection, proposed = _compute_projection(
            request,
            prior,
            tx_id=transaction_id,
            input_digest=input_digest,
        )
        self._pending[transaction_id] = _Prepared(input_digest, projection, proposed)
        return projection

    def commit(self, transaction_id: str) -> D4LineageProjection:
        committed = self._committed_transactions.get(transaction_id)
        if committed is not None:
            return _projection_from_record(committed[1])
        pending = self._pending.get(transaction_id)
        if pending is None:
            raise LineageProductionBlock("COMMIT_REQUIRES_PREPARED_TRANSACTION")
        projection = pending.projection
        if pending.proposed_ledger is not None:
            key = json.dumps(
                [
                    pending.proposed_ledger.symbol,
                    pending.proposed_ledger.trend_episode_id,
                    pending.proposed_ledger.direction_value,
                ],
                separators=(",", ":"),
                ensure_ascii=False,
            )
            self._ledgers[key] = pending.proposed_ledger
        record = _projection_record(projection)
        self._committed_transactions[transaction_id] = (pending.input_digest, record)
        del self._pending[transaction_id]
        return projection

    def abort(self, transaction_id: str) -> None:
        self._pending.pop(transaction_id, None)

    def ledger_for(self, symbol: str, trend_episode_id: str, direction: Any) -> Mapping[str, Any] | None:
        key = json.dumps([symbol, trend_episode_id, _enum_value(direction)], separators=(",", ":"), ensure_ascii=False)
        ledger = self._ledgers.get(key)
        return None if ledger is None else MappingProxyType(dict(_ledger_record(ledger)))

    def export_state(self) -> str:
        # Pending transactions are intentionally not persisted; after restart
        # they must be re-prepared from authoritative inputs before commit.
        payload = {
            "schema": "TAC_D4_LINEAGE_PRODUCTION_PROJECTOR_V2_STATE",
            "producer_id": PRODUCER_ID,
            "semantic_id": SEMANTIC_ID,
            "ledgers": [
                [key, _ledger_record(value)]
                for key, value in sorted(self._ledgers.items(), key=lambda kv: kv[0])
            ],
            "committed_transactions": [
                [tx, {"input_digest": row[0], "projection": row[1]}]
                for tx, row in sorted(self._committed_transactions.items(), key=lambda kv: kv[0])
            ],
        }
        return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    @classmethod
    def restore_state(cls, raw: str) -> "D4MarketEventLineageProductionProjectorV2":
        try:
            payload = json.loads(raw)
        except Exception as exc:
            raise LineageProductionConflict("STATE_JSON_INVALID") from exc
        if payload.get("schema") != "TAC_D4_LINEAGE_PRODUCTION_PROJECTOR_V2_STATE":
            raise LineageProductionConflict("STATE_SCHEMA_MISMATCH")
        if payload.get("producer_id") != PRODUCER_ID or payload.get("semantic_id") != SEMANTIC_ID:
            raise LineageProductionConflict("STATE_AUTHORITY_ID_MISMATCH")
        ledgers = {
            str(key): _ledger_from_record(value)
            for key, value in payload.get("ledgers", [])
        }
        committed = {
            str(tx): (str(value["input_digest"]), dict(value["projection"]))
            for tx, value in payload.get("committed_transactions", [])
        }
        out = cls(ledgers=ledgers, committed_transactions=committed)
        # Verify retained admission count exactly equals retained admission tx IDs.
        for ledger in out._ledgers.values():
            if ledger.admission_count != len(ledger.admission_tx_ids):
                raise LineageProductionConflict("RETAINED_ADMISSION_HISTORY_INCOMPLETE")
        return out

    def state_digest(self) -> str:
        return sha256(self.export_state().encode("utf-8")).hexdigest()
