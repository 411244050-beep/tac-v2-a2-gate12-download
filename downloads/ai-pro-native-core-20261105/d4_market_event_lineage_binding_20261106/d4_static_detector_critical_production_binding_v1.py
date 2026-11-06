from __future__ import annotations

"""D4 static detector-evidence + critical-information production binding V1.

This module is a pure production projection of the already-frozen
D4_STATIC_DETECTOR_CRITICAL_SOURCE_ASSOCIATION_V1 semantic.  It does not
produce D1/D2/D3/B3/B4/B5/D4 scientific evidence and does not change any
market-event identity, mechanism, Entry Boundary, or gate rule.

Inputs are:
- exact frozen producer outputs;
- exact frozen D4-lineage projection;
- a typed engineering coverage proof for the six frozen source-coverage
  classes.

Outputs are:
- critical_information_known;
- detector_evidence_ids;
- when fully admissible, an Assembler-V2 D4StaticAuthority already bound to
  the frozen lineage projection.

No market source, TEST/outcome, PnL, Forward Observation, or trading path is
present.
"""

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

import authoritative_d3_b5_d4_base_runtime_producers_v1 as b5prod
import authoritative_d3_d4_evidence_packet_assembler_resumption_v2 as assembler
import d4_market_event_lineage_production_binding_v2 as lineage_prod

from strategy_rc1.runtime_guards.information_state import InfoKind, InfoValue


PRODUCER_ID = "D4_STATIC_DETECTOR_CRITICAL_SOURCE_ASSOCIATION_PRODUCTION_BINDING_V1"
SEMANTIC_ID = "D4_STATIC_DETECTOR_CRITICAL_SOURCE_ASSOCIATION_V1"
SEMANTIC_CONTRACT_BLOB = "33bd7a452b6c2f3789a10fa5e8ca18653df5bc9e"
SEMANTIC_FREEZE_MANIFEST_BLOB = "28db016bbc13fba665676b16bb3b75dffebbf85b"
ASSEMBLER_BLOB = "a5f2b841cb44f9ff759232cc3ae72ff844cee02b"
D4_LINEAGE_PROJECTOR_BLOB = "abc5be6afa7cab1d6f958c4b26e368d4963ec80b"
D3_B5_D4_PRODUCER_BLOB = "97a02f5584c1446ca5ae016bad383e3ed0e18bb5"

COVERAGE_CLASSES = (
    "RAW_AND_D2_STATE",
    "D3_CANDIDATE_AND_RUNTIME_B3",
    "D2_B4_D4_CAUSAL_PROJECTIONS",
    "UPDATE008_D3_B5_STATE",
    "D4_MECHANISM_SOURCE_COVERAGE",
    "D4_MARKET_EVENT_LINEAGE",
)
COVERAGE_STATUSES = ("COMPLETE", "UNKNOWN", "MISSING", "CONFLICT", "ERROR")
_SEVERITY = {
    "COMPLETE": 0,
    "UNKNOWN": 1,
    "MISSING": 1,
    "CONFLICT": 2,
    "ERROR": 2,
}


class D4StaticAssociationBlock(RuntimeError):
    pass


class D4StaticAssociationConflict(D4StaticAssociationBlock):
    pass


@dataclass(frozen=True)
class SourceCoverageFact:
    """Engineering completeness proof for one frozen source-coverage class.

    This is not a strategy state and does not encode signal truth.  COMPLETE
    means the upstream production/orchestration layer has exhaustively
    accounted for that frozen class at this information cutoff.  UNKNOWN or
    MISSING preserves incompleteness; CONFLICT/ERROR preserves system
    uncertainty.  source_refs are provenance only.
    """

    status: str
    source_refs: tuple[str, ...] = ()
    error_ref: str | None = None
    provenance: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        status = str(self.status)
        if status not in COVERAGE_STATUSES:
            raise ValueError("UNSUPPORTED_COVERAGE_STATUS:" + status)
        refs = tuple(sorted(set(str(x) for x in self.source_refs if str(x))))
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "source_refs", refs)
        object.__setattr__(self, "provenance", MappingProxyType({str(k): str(v) for k, v in self.provenance.items()}))
        if status == "COMPLETE" and not refs:
            raise ValueError("COMPLETE_COVERAGE_REQUIRES_SOURCE_REFS")
        if status == "ERROR" and self.error_ref is None and not refs:
            raise ValueError("ERROR_COVERAGE_REQUIRES_ERROR_OR_SOURCE_REF")


@dataclass(frozen=True)
class D4CriticalCoverageProof:
    raw_and_d2_state: SourceCoverageFact
    d3_candidate_and_runtime_b3: SourceCoverageFact
    d2_b4_d4_causal_projections: SourceCoverageFact
    update008_d3_b5_state: SourceCoverageFact
    d4_mechanism_source_coverage: SourceCoverageFact
    d4_market_event_lineage: SourceCoverageFact
    future_evidence_detected: bool = False
    provenance: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "provenance", MappingProxyType({str(k): str(v) for k, v in self.provenance.items()}))

    def by_class(self) -> Mapping[str, SourceCoverageFact]:
        return MappingProxyType({
            "RAW_AND_D2_STATE": self.raw_and_d2_state,
            "D3_CANDIDATE_AND_RUNTIME_B3": self.d3_candidate_and_runtime_b3,
            "D2_B4_D4_CAUSAL_PROJECTIONS": self.d2_b4_d4_causal_projections,
            "UPDATE008_D3_B5_STATE": self.update008_d3_b5_state,
            "D4_MECHANISM_SOURCE_COVERAGE": self.d4_mechanism_source_coverage,
            "D4_MARKET_EVENT_LINEAGE": self.d4_market_event_lineage,
        })


@dataclass(frozen=True)
class D4StaticAssociationRequest:
    information_cutoff: int
    trend_episode_id: str
    direction: Any
    trend: Any
    trend_position: Any
    update008_output: b5prod.Update008Output
    mechanisms: assembler.MechanismProducerOutputs
    lineage_projection: lineage_prod.D4LineageProjection
    coverage: D4CriticalCoverageProof
    termination: Any | None = None
    provenance: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "provenance", MappingProxyType({str(k): str(v) for k, v in self.provenance.items()}))


@dataclass(frozen=True)
class D4StaticAssociationProjection:
    status: str
    critical_information_known: InfoValue[bool]
    detector_evidence_ids: tuple[str, ...]
    active_mechanisms: tuple[str, ...]
    coverage_statuses: tuple[tuple[str, str], ...]
    coverage_source_refs: tuple[str, ...]
    d4_static_authority: assembler.D4StaticAuthority | None
    blocked_reason: str | None = None
    provenance: Mapping[str, str] = field(default_factory=dict)


def _state_value(value: Any) -> str:
    return value.value if hasattr(value, "value") else str(value)


def _worse(a: str, b: str) -> str:
    if a not in _SEVERITY or b not in _SEVERITY:
        raise D4StaticAssociationConflict("UNSUPPORTED_EFFECTIVE_COVERAGE_STATUS")
    return b if _SEVERITY[b] > _SEVERITY[a] else a


def _update008_actual_status(output: b5prod.Update008Output) -> str:
    if not isinstance(output, b5prod.Update008Output):
        raise D4StaticAssociationConflict("UPDATE008_OUTPUT_SCHEMA")
    if output.conflict_lineage_refs:
        return "CONFLICT"
    state = _state_value(output.state)
    if state == "CONFLICT":
        return "CONFLICT"
    if output.unknown_lineage_refs:
        return "UNKNOWN"
    if state == "UNKNOWN":
        return "UNKNOWN"
    return "COMPLETE"


def _projection_surface_status(value: Any | None) -> str:
    if value is None:
        return "COMPLETE"
    state = getattr(value, "state", None)
    if state is None:
        return "COMPLETE"
    raw = _state_value(state)
    if raw == "CONFLICT":
        return "CONFLICT"
    if raw == "UNKNOWN":
        return "UNKNOWN"
    return "COMPLETE"


def _mechanism_actual_status(mechanisms: assembler.MechanismProducerOutputs) -> str:
    if not isinstance(mechanisms, assembler.MechanismProducerOutputs):
        raise D4StaticAssociationConflict("MECHANISM_OUTPUTS_SCHEMA")
    status = "COMPLETE"
    for value in (
        mechanisms.normal_retest,
        mechanisms.normal_entry_boundary,
        mechanisms.false_break_entry_boundary,
        mechanisms.platform_entry_boundary,
        mechanisms.deep_takeover,
        mechanisms.deep_entry_boundary,
        mechanisms.trend_establishment_watch,
    ):
        status = _worse(status, _projection_surface_status(value))
    return status


def _lineage_actual_status(projection: lineage_prod.D4LineageProjection) -> str:
    if not isinstance(projection, lineage_prod.D4LineageProjection):
        raise D4StaticAssociationConflict("D4_LINEAGE_PROJECTION_SCHEMA")
    relation = projection.relation
    if relation is None:
        return "UNKNOWN"
    rv = _state_value(relation)
    if rv == "CONFLICT":
        return "CONFLICT"
    if rv == "UNKNOWN":
        return "UNKNOWN"
    if not projection.lineage_evidence_refs:
        return "CONFLICT"
    return "COMPLETE"


def _validate_request(req: D4StaticAssociationRequest) -> None:
    if not isinstance(req, D4StaticAssociationRequest):
        raise D4StaticAssociationConflict("REQUEST_SCHEMA")
    if not isinstance(req.information_cutoff, int) or req.information_cutoff < 0:
        raise D4StaticAssociationBlock("INFORMATION_CUTOFF_INVALID")
    if not isinstance(req.trend_episode_id, str) or not req.trend_episode_id:
        raise D4StaticAssociationBlock("TREND_EPISODE_ID_REQUIRED")
    if getattr(req.trend, "episode_id", None) != req.trend_episode_id:
        raise D4StaticAssociationConflict("TREND_EPISODE_OBJECT_MISMATCH")
    if getattr(req.trend, "direction", None) is not req.direction:
        if _state_value(getattr(req.trend, "direction", None)) != _state_value(req.direction):
            raise D4StaticAssociationConflict("TREND_DIRECTION_MISMATCH")
    if not isinstance(req.coverage, D4CriticalCoverageProof):
        raise D4StaticAssociationConflict("COVERAGE_PROOF_SCHEMA")
    if not isinstance(req.mechanisms, assembler.MechanismProducerOutputs):
        raise D4StaticAssociationConflict("MECHANISM_OUTPUTS_SCHEMA")
    if not isinstance(req.update008_output, b5prod.Update008Output):
        raise D4StaticAssociationConflict("UPDATE008_OUTPUT_SCHEMA")
    if not isinstance(req.lineage_projection, lineage_prod.D4LineageProjection):
        raise D4StaticAssociationConflict("D4_LINEAGE_PROJECTION_SCHEMA")


def _effective_coverage(req: D4StaticAssociationRequest) -> tuple[tuple[str, str], ...]:
    facts = dict(req.coverage.by_class())
    effective = {name: facts[name].status for name in COVERAGE_CLASSES}
    effective["UPDATE008_D3_B5_STATE"] = _worse(
        effective["UPDATE008_D3_B5_STATE"],
        _update008_actual_status(req.update008_output),
    )
    effective["D4_MECHANISM_SOURCE_COVERAGE"] = _worse(
        effective["D4_MECHANISM_SOURCE_COVERAGE"],
        _mechanism_actual_status(req.mechanisms),
    )
    effective["D4_MARKET_EVENT_LINEAGE"] = _worse(
        effective["D4_MARKET_EVENT_LINEAGE"],
        _lineage_actual_status(req.lineage_projection),
    )
    if req.coverage.future_evidence_detected:
        # Future contamination has ERROR precedence but is recorded separately
        # rather than mutating any upstream scientific object.
        effective["RAW_AND_D2_STATE"] = _worse(effective["RAW_AND_D2_STATE"], "ERROR")
    return tuple((name, effective[name]) for name in COVERAGE_CLASSES)


def _coverage_source_refs(req: D4StaticAssociationRequest) -> tuple[str, ...]:
    out: set[str] = set()
    for fact in req.coverage.by_class().values():
        out.update(fact.source_refs)
    out.update(str(x) for x in req.update008_output.unknown_lineage_refs if str(x))
    out.update(str(x) for x in req.update008_output.conflict_lineage_refs if str(x))
    out.update(str(x) for x in req.lineage_projection.lineage_evidence_refs if str(x))
    return tuple(sorted(out))


def _critical_from_coverage(
    statuses: tuple[tuple[str, str], ...],
    *,
    pure_watch_only: bool,
) -> tuple[str, InfoValue[bool], str | None]:
    values = tuple(v for _, v in statuses)
    if any(v in ("CONFLICT", "ERROR") for v in values):
        return (
            "BLOCKED_CRITICAL_ERROR",
            InfoValue.error("D4_CRITICAL_INFORMATION_CONFLICT"),
            "CRITICAL_COVERAGE_CONFLICT_ERROR_OR_FUTURE",
        )
    if any(v in ("UNKNOWN", "MISSING") for v in values):
        return (
            "BLOCKED_CRITICAL_UNKNOWN",
            InfoValue.unknown(),
            "CRITICAL_COVERAGE_MISSING_OR_UNKNOWN",
        )
    if pure_watch_only:
        return "READY", InfoValue.na(), None
    return "READY", InfoValue.known(True), None


def _consume_mechanism_evidence(
    mechanisms: assembler.MechanismProducerOutputs,
) -> tuple[Any | None, Any | None, Any | None, Any | None, Any | None]:
    # Reuse the exact Assembler-V2 consumers.  They already preserve frozen
    # UNKNOWN/CONFLICT handling and do not invent evidence.
    return (
        assembler._normal_projection(mechanisms.normal_retest),
        mechanisms.false_break_reclaim,
        mechanisms.platform_reexpansion,
        assembler._deep_projection(mechanisms.deep_takeover),
        assembler._watch_projection(mechanisms.trend_establishment_watch),
    )


def _pure_watch_only(mechanisms: assembler.MechanismProducerOutputs) -> bool:
    normal, false_break, platform, deep, watch = _consume_mechanism_evidence(mechanisms)
    return (
        watch is not None
        and normal is None
        and false_break is None
        and platform is None
        and deep is None
    )


def _preview_observations(
    req: D4StaticAssociationRequest,
    *,
    critical: InfoValue[bool],
) -> tuple[Any, ...]:
    normal, false_break, platform, deep, watch = _consume_mechanism_evidence(req.mechanisms)
    normal_entry = assembler._entry_projection(
        req.mechanisms.normal_entry_boundary,
        mechanism="NORMAL_RETEST_CONTINUATION",
        required=normal is not None,
    )
    false_entry = assembler._entry_projection(
        req.mechanisms.false_break_entry_boundary,
        mechanism="FALSE_BREAK_RECLAIM",
        required=false_break is not None,
    )
    platform_entry = assembler._entry_projection(
        req.mechanisms.platform_entry_boundary,
        mechanism="PLATFORM_REEXPANSION",
        required=platform is not None,
    )
    deep_entry = assembler._entry_projection(
        req.mechanisms.deep_entry_boundary,
        mechanism="DEEP_STRUCTURE_TAKEOVER",
        required=deep is not None,
    )

    base = assembler.D4StaticAuthority(
        trend_episode_id=req.trend_episode_id,
        direction=req.direction,
        relation=req.lineage_projection.relation,
        trend=req.trend,
        trend_position=req.trend_position,
        detector_evidence_ids=(),
        critical_information_known=critical,
        termination=req.termination,
        independence=req.lineage_projection.independence,
        new_event_evidence=req.lineage_projection.new_event_evidence,
        lineage_evidence_refs=tuple(req.lineage_projection.lineage_evidence_refs),
    )
    post = assembler.PostUpdate008Authority(
        information_cutoff=req.information_cutoff,
        update008_output=req.update008_output,
        d4_static=base,
        mechanisms=req.mechanisms,
        provenance={"producer_id": PRODUCER_ID, "phase": "DETECTOR_PREVIEW"},
    )
    observations, _ = assembler._preview_observations(
        post,
        normal_evidence=normal,
        false_break_evidence=false_break,
        platform_evidence=platform,
        deep_evidence=deep,
        watch_evidence=watch,
        normal_entry=normal_entry,
        false_entry=false_entry,
        platform_entry=platform_entry,
        deep_entry=deep_entry,
    )
    return observations


def _detector_ids_from_observations(observations: tuple[Any, ...]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    ids: set[str] = set()
    active_names: set[str] = set()
    for obs in observations:
        if not getattr(obs, "active", False):
            continue
        refs = tuple(str(x) for x in getattr(obs, "source_event_ids", ()) if str(x))
        if not refs:
            raise D4StaticAssociationBlock("ACTIVE_MECHANISM_OBSERVATION_SOURCE_EVENT_IDS_EMPTY")
        ids.update(refs)
        mech = getattr(obs, "mechanism", None)
        active_names.add(_state_value(mech))
    return tuple(sorted(ids)), tuple(sorted(active_names))


def project_d4_static_source_association(
    req: D4StaticAssociationRequest,
) -> D4StaticAssociationProjection:
    """Project the two frozen D4 static source-association fields.

    This function is intentionally stateless. Transactionality remains owned by
    the surrounding live/raw orchestration layer; this projector performs no
    scientific state mutation.
    """

    _validate_request(req)
    statuses = _effective_coverage(req)
    refs = _coverage_source_refs(req)

    # Pure-WATCH classification is evaluated only after effective source
    # coverage is complete enough to safely consume the frozen mechanism
    # surfaces.  UNKNOWN/ERROR paths never infer WATCH from absence.
    raw_values = tuple(v for _, v in statuses)
    if any(v in ("CONFLICT", "ERROR", "UNKNOWN", "MISSING") for v in raw_values):
        status, critical, blocked = _critical_from_coverage(statuses, pure_watch_only=False)
        return D4StaticAssociationProjection(
            status=status,
            critical_information_known=critical,
            detector_evidence_ids=(),
            active_mechanisms=(),
            coverage_statuses=statuses,
            coverage_source_refs=refs,
            d4_static_authority=None,
            blocked_reason=blocked,
            provenance=MappingProxyType({
                "producer_id": PRODUCER_ID,
                "semantic_id": SEMANTIC_ID,
                "detector_projection_performed": "false",
                "scientific_state_mutated": "false",
            }),
        )

    pure_watch = _pure_watch_only(req.mechanisms)
    status, critical, blocked = _critical_from_coverage(statuses, pure_watch_only=pure_watch)
    if status != "READY":
        raise D4StaticAssociationConflict("COMPLETE_COVERAGE_CRITICAL_MAPPING_NOT_READY")

    try:
        observations = _preview_observations(req, critical=critical)
        detector_ids, active_mechanisms = _detector_ids_from_observations(observations)
    except assembler.PacketAssemblyBlock as exc:
        return D4StaticAssociationProjection(
            status="BLOCKED_DETECTOR_PROVENANCE",
            critical_information_known=critical,
            detector_evidence_ids=(),
            active_mechanisms=(),
            coverage_statuses=statuses,
            coverage_source_refs=refs,
            d4_static_authority=None,
            blocked_reason="FROZEN_PREVIEW_BLOCK:" + str(exc),
            provenance=MappingProxyType({
                "producer_id": PRODUCER_ID,
                "semantic_id": SEMANTIC_ID,
                "detector_projection_performed": "false",
                "scientific_state_mutated": "false",
            }),
        )
    except assembler.PacketAssemblyConflict as exc:
        return D4StaticAssociationProjection(
            status="BLOCKED_DETECTOR_CONFLICT",
            critical_information_known=InfoValue.error("D4_CRITICAL_INFORMATION_CONFLICT"),
            detector_evidence_ids=(),
            active_mechanisms=(),
            coverage_statuses=statuses,
            coverage_source_refs=refs,
            d4_static_authority=None,
            blocked_reason="FROZEN_PREVIEW_CONFLICT:" + str(exc),
            provenance=MappingProxyType({
                "producer_id": PRODUCER_ID,
                "semantic_id": SEMANTIC_ID,
                "detector_projection_performed": "false",
                "scientific_state_mutated": "false",
            }),
        )
    except D4StaticAssociationBlock as exc:
        return D4StaticAssociationProjection(
            status="BLOCKED_DETECTOR_PROVENANCE",
            critical_information_known=critical,
            detector_evidence_ids=(),
            active_mechanisms=(),
            coverage_statuses=statuses,
            coverage_source_refs=refs,
            d4_static_authority=None,
            blocked_reason=str(exc),
            provenance=MappingProxyType({
                "producer_id": PRODUCER_ID,
                "semantic_id": SEMANTIC_ID,
                "detector_projection_performed": "false",
                "scientific_state_mutated": "false",
            }),
        )

    unbound = assembler.D4StaticAuthority(
        trend_episode_id=req.trend_episode_id,
        direction=req.direction,
        relation=assembler.frozen.EventRelation.UNKNOWN,
        trend=req.trend,
        trend_position=req.trend_position,
        detector_evidence_ids=detector_ids,
        critical_information_known=critical,
        termination=req.termination,
    )
    try:
        bound = lineage_prod.bind_d4_static_authority(unbound, req.lineage_projection)
    except (lineage_prod.LineageProductionBlock, lineage_prod.LineageProductionConflict) as exc:
        return D4StaticAssociationProjection(
            status="BLOCKED_LINEAGE_BINDING",
            critical_information_known=critical,
            detector_evidence_ids=detector_ids,
            active_mechanisms=active_mechanisms,
            coverage_statuses=statuses,
            coverage_source_refs=refs,
            d4_static_authority=None,
            blocked_reason=str(exc),
            provenance=MappingProxyType({
                "producer_id": PRODUCER_ID,
                "semantic_id": SEMANTIC_ID,
                "detector_projection_performed": "true",
                "scientific_state_mutated": "false",
            }),
        )

    return D4StaticAssociationProjection(
        status="READY",
        critical_information_known=critical,
        detector_evidence_ids=detector_ids,
        active_mechanisms=active_mechanisms,
        coverage_statuses=statuses,
        coverage_source_refs=refs,
        d4_static_authority=bound,
        blocked_reason=None,
        provenance=MappingProxyType({
            "producer_id": PRODUCER_ID,
            "semantic_id": SEMANTIC_ID,
            "semantic_contract_blob": SEMANTIC_CONTRACT_BLOB,
            "semantic_freeze_manifest_blob": SEMANTIC_FREEZE_MANIFEST_BLOB,
            "assembler_blob": ASSEMBLER_BLOB,
            "d4_lineage_projector_blob": D4_LINEAGE_PROJECTOR_BLOB,
            "d3_b5_d4_producer_blob": D3_B5_D4_PRODUCER_BLOB,
            "detector_projection_performed": "true",
            "scientific_state_mutated": "false",
            "real_market_data_read": "false",
            "test_read": "false",
            "pnl": "false",
            "trading": "FORBIDDEN",
        }),
    )


def bind_v3_static_base(
    projection: D4StaticAssociationProjection,
    *,
    base_type: Any,
) -> Any:
    """Mechanical bridge helper for a later raw-orchestration stage.

    The current stage does not modify V3.  A later authorized integration may
    call this only when projection.status == READY.
    """
    if projection.status != "READY" or projection.d4_static_authority is None:
        raise D4StaticAssociationBlock("READY_PROJECTION_REQUIRED")
    st = projection.d4_static_authority
    return base_type(
        trend_episode_id=st.trend_episode_id,
        direction=st.direction,
        trend=st.trend,
        trend_position=st.trend_position,
        detector_evidence_ids=tuple(st.detector_evidence_ids),
        critical_information_known=st.critical_information_known,
        termination=st.termination,
    )
