from __future__ import annotations

"""Pure-WATCH Trend-genesis UPDATE-008 completeness reconciliation V2.

This module does not change frozen UPDATE-008 scientific state.  It only
reconciles the D4-static engineering coverage cross-check for the exact
authoritative pure-WATCH genesis / no-Primary surface frozen by
D4_STATIC_PURE_WATCH_UPDATE008_COMPLETENESS_RECONCILIATION_V1.
"""

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

import nontrading_adapter_integration_v1 as frozen
import authoritative_d3_d4_evidence_packet_assembler_resumption_v2 as assembler
import authoritative_d3_b5_d4_base_runtime_producers_v1 as b5prod
import d4_market_event_lineage_production_binding_v2 as lineage_prod
import d4_static_detector_critical_production_binding_v1 as v1

from d2_to_b4_d4_causal_evidence_producers_v1 import EvidenceState
from strategy_rc1.d3_boundary_intelligence.types import RoleTransition
from strategy_rc1.runtime_guards.information_state import InfoValue


PRODUCER_ID = "D4_STATIC_PURE_WATCH_UPDATE008_COMPLETENESS_PRODUCTION_BINDING_V2"
SEMANTIC_ID = "D4_STATIC_PURE_WATCH_UPDATE008_COMPLETENESS_RECONCILIATION_V1"
SEMANTIC_CONTRACT_BLOB = "4061aefe7551dfaf3676ac843eff81030378f411"
SELECTION_PROTOCOL_BLOB = "40dbdaf808ebb30f28c1daefbb83e26c8f3ac5e7"
DECISION_BLOB = "b7a818916d03723b2141b9c8d7d13343eeab0198"
TRUTH_TABLE_BLOB = "d1b8fb36330b2e83c20a9ec7c27ce62aa8bb4f40"
V1_BINDING_BLOB = "9eac94f81d874f41f25f856aee16c60ee8deb312"
UPDATE008_PRODUCER_BLOB = "97a02f5584c1446ca5ae016bad383e3ed0e18bb5"
LINEAGE_V2_BLOB = "f334155bbb46ec2ff0ee748555cb15c1485d3036"

GENESIS_PROOF_KIND = "GENESIS_COVERAGE_FIRST_AUTHORITATIVE_ACTIVE_OBSERVATION"
NO_PRIMARY_REASON = "NO_AUTHORITATIVE_PRIMARY"


@dataclass(frozen=True)
class PureWatchGenesisReconciliationContext:
    """Typed context; no caller boolean can force the reconciliation."""

    lineage_request: lineage_prod.D4LineageProductionRequest
    provenance: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "provenance",
            MappingProxyType({str(k): str(v) for k, v in self.provenance.items()}),
        )


@dataclass(frozen=True)
class Update008CoverageReconciliation:
    effective_status: str
    applies: bool
    reason: str
    provenance: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.effective_status not in ("COMPLETE", "UNKNOWN", "CONFLICT"):
            raise ValueError("UNSUPPORTED_RECONCILIATION_STATUS")
        object.__setattr__(
            self,
            "provenance",
            MappingProxyType({str(k): str(v) for k, v in self.provenance.items()}),
        )


def _value(x: Any) -> str:
    return x.value if hasattr(x, "value") else str(x)


def _result(status: str, applies: bool, reason: str) -> Update008CoverageReconciliation:
    return Update008CoverageReconciliation(
        effective_status=status,
        applies=applies,
        reason=reason,
        provenance={
            "producer_id": PRODUCER_ID,
            "semantic_id": SEMANTIC_ID,
            "semantic_contract_blob": SEMANTIC_CONTRACT_BLOB,
            "scientific_update008_state_mutated": "false",
        },
    )


def _lineage_genesis_matches(
    req: v1.D4StaticAssociationRequest,
    ctx: PureWatchGenesisReconciliationContext | None,
) -> bool:
    if ctx is None:
        return False
    lr = ctx.lineage_request
    if not isinstance(lr, lineage_prod.D4LineageProductionRequest):
        return False
    if lr.information_cutoff != req.information_cutoff:
        return False
    if lr.trend_episode_id != req.trend_episode_id:
        return False
    if _value(lr.direction) != _value(req.direction):
        return False
    if lr.future_evidence_detected:
        return False
    if lr.canonical_continuity_known is not True or lr.canonical_continuity_intact is not True:
        return False
    if tuple(lr.active_mechanisms) != (lineage_prod.MECH_WATCH,):
        return False
    if lr.mechanisms != req.mechanisms:
        return False
    if lr.existing_opportunity is not None:
        return False
    record = lr.trend_establishment_record
    if not isinstance(record, b5prod.TrendEstablishmentRecord):
        return False
    if record.creation_cutoff != req.information_cutoff:
        return False
    if getattr(record.trend, "episode_start_cutoff", None) != req.information_cutoff:
        return False
    if getattr(record.trend, "episode_id", None) != req.trend_episode_id:
        return False
    if _value(getattr(record.trend, "direction", None)) != _value(req.direction):
        return False
    if record.trend != req.trend:
        return False
    if not record.newest_intermediate_pivot_id or not record.source_event_ids:
        return False

    p = req.lineage_projection
    if p.status != "KNOWN_START_FIRST_EVENT":
        return False
    if p.relation is not frozen.EventRelation.START_FIRST_EVENT:
        return False
    if tuple(p.proof_kinds) != (GENESIS_PROOF_KIND,):
        return False
    refs = tuple(p.lineage_evidence_refs)
    if not refs:
        return False
    required_prefixes = ("HistoryCoverage:", "TrendEpisode:", "StructuralPivot:", "D2Event:")
    if any(not any(x.startswith(prefix) for x in refs) for prefix in required_prefixes):
        return False
    if p.new_event_evidence is not None or p.independence is not None:
        return False
    return True


def classify_update008_coverage(
    req: v1.D4StaticAssociationRequest,
    *,
    reconciliation_context: PureWatchGenesisReconciliationContext | None = None,
) -> Update008CoverageReconciliation:
    """Classify only the UPDATE008_D3_B5_STATE *coverage* cross-check.

    Frozen Update008Output.state is never changed.
    """

    v1._validate_request(req)
    out = req.update008_output

    if out.conflict_lineage_refs or out.state is EvidenceState.CONFLICT:
        return _result("CONFLICT", False, "FROZEN_UPDATE008_CONFLICT")
    if out.unknown_lineage_refs:
        return _result("UNKNOWN", False, "FROZEN_UPDATE008_UNKNOWN_LINEAGE")
    if out.state is not EvidenceState.UNKNOWN:
        return _result("COMPLETE", False, "FROZEN_UPDATE008_NONUNKNOWN_UNCHANGED")

    if v1._mechanism_actual_status(req.mechanisms) != "COMPLETE":
        return _result("UNKNOWN", False, "MECHANISM_SURFACE_NOT_COMPLETE")
    if v1._lineage_actual_status(req.lineage_projection) != "COMPLETE":
        return _result("UNKNOWN", False, "LINEAGE_SURFACE_NOT_COMPLETE")
    if not v1._pure_watch_only(req.mechanisms):
        return _result("UNKNOWN", False, "NOT_PURE_WATCH")
    if not _lineage_genesis_matches(req, reconciliation_context):
        return _result("UNKNOWN", False, "AUTHORITATIVE_WATCH_GENESIS_NOT_PROVEN")

    if dict(out.provenance).get("runtime_contract_id") != b5prod.RUNTIME_CONTRACT_ID:
        return _result("UNKNOWN", False, "UPDATE008_RUNTIME_PROVENANCE_MISSING")
    if dict(out.provenance).get("f9_stage") != "UPDATE-008":
        return _result("UNKNOWN", False, "UPDATE008_F9_PROVENANCE_MISSING")
    if dict(out.provenance).get("no_update002_backflow") != "true":
        return _result("UNKNOWN", False, "UPDATE008_NO_BACKFLOW_PROVENANCE_MISSING")

    rr = out.role_runtime
    if not isinstance(rr, b5prod.RoleRuntimeOutput):
        return _result("UNKNOWN", False, "ROLE_RUNTIME_REQUIRED")
    if rr.state is not EvidenceState.UNKNOWN:
        return _result("UNKNOWN", False, "ROLE_RUNTIME_NOT_UNKNOWN")
    if rr.conflict_reasons:
        return _result("CONFLICT", False, "ROLE_RUNTIME_CONFLICT")
    if tuple(rr.unresolved_reasons) != (NO_PRIMARY_REASON,):
        return _result("UNKNOWN", False, "ROLE_RUNTIME_UNKNOWN_REASON_NOT_NO_PRIMARY")
    if out.roles is None or rr.assignment is None or out.roles != rr.assignment:
        return _result("CONFLICT", False, "ROLE_ASSIGNMENT_SURFACE_MISMATCH")
    assignment = rr.assignment
    if assignment.primary_unit_id is not None:
        return _result("UNKNOWN", False, "PRIMARY_ALREADY_EXISTS")
    if assignment.transition is not RoleTransition.NONE:
        return _result("UNKNOWN", False, "ROLE_TRANSITION_NOT_NONE")
    if assignment.unresolved_reason is not None:
        return _result("UNKNOWN", False, "ROLE_ASSIGNMENT_HAS_UNRESOLVED_REASON")
    if rr.primary_qbu_identities or out.produced_qbus:
        return _result("UNKNOWN", False, "QBU_ALREADY_PRESENT")
    if tuple(rr.units) != tuple(out.units) or tuple(rr.role_evidence) != tuple(out.role_evidence):
        return _result("CONFLICT", False, "ROLE_RUNTIME_OUTPUT_SURFACE_MISMATCH")
    if any(x.unresolved_conflict for x in rr.role_evidence):
        return _result("CONFLICT", False, "ROLE_EVIDENCE_CONFLICT")
    if any(x.latest_qualified_use_cutoff is not None for x in rr.role_evidence):
        return _result("UNKNOWN", False, "QUALIFIED_USE_EXISTS_WITHOUT_PRIMARY")
    if dict(rr.provenance).get("producer_semantic_contract_id") != "TAC_D3_B5_ROLE_STATE_PRODUCER_SEMANTIC_CONTRACT_V1":
        return _result("UNKNOWN", False, "ROLE_RUNTIME_PROVENANCE_MISSING")

    return _result(
        "COMPLETE",
        True,
        "PURE_WATCH_GENESIS_NO_AUTHORITATIVE_PRIMARY_ROLE_STATE_NOT_APPLICABLE_TO_COVERAGE",
    )


def _effective_coverage(
    req: v1.D4StaticAssociationRequest,
    reconciliation: Update008CoverageReconciliation,
) -> tuple[tuple[str, str], ...]:
    facts = dict(req.coverage.by_class())
    effective = {name: facts[name].status for name in v1.COVERAGE_CLASSES}
    effective["UPDATE008_D3_B5_STATE"] = v1._worse(
        effective["UPDATE008_D3_B5_STATE"],
        reconciliation.effective_status,
    )
    effective["D4_MECHANISM_SOURCE_COVERAGE"] = v1._worse(
        effective["D4_MECHANISM_SOURCE_COVERAGE"],
        v1._mechanism_actual_status(req.mechanisms),
    )
    effective["D4_MARKET_EVENT_LINEAGE"] = v1._worse(
        effective["D4_MARKET_EVENT_LINEAGE"],
        v1._lineage_actual_status(req.lineage_projection),
    )
    if req.coverage.future_evidence_detected:
        effective["RAW_AND_D2_STATE"] = v1._worse(
            effective["RAW_AND_D2_STATE"], "ERROR"
        )
    return tuple((name, effective[name]) for name in v1.COVERAGE_CLASSES)


def _projection_provenance(
    reconciliation: Update008CoverageReconciliation,
    *,
    detector_performed: bool,
) -> MappingProxyType:
    return MappingProxyType({
        "producer_id": PRODUCER_ID,
        "semantic_id": SEMANTIC_ID,
        "semantic_contract_blob": SEMANTIC_CONTRACT_BLOB,
        "v1_binding_blob": V1_BINDING_BLOB,
        "update008_producer_blob": UPDATE008_PRODUCER_BLOB,
        "d4_lineage_v2_blob": LINEAGE_V2_BLOB,
        "update008_reconciliation_applied": str(reconciliation.applies).lower(),
        "update008_reconciliation_reason": reconciliation.reason,
        "detector_projection_performed": str(detector_performed).lower(),
        "scientific_update008_state_mutated": "false",
        "scientific_state_mutated": "false",
        "real_market_data_read": "false",
        "test_read": "false",
        "pnl": "false",
        "trading": "FORBIDDEN",
    })


def project_d4_static_source_association(
    req: v1.D4StaticAssociationRequest,
    *,
    reconciliation_context: PureWatchGenesisReconciliationContext | None = None,
) -> v1.D4StaticAssociationProjection:
    """V1 projection with one preregistered pure-WATCH genesis cross-check repair."""

    v1._validate_request(req)
    reconciliation = classify_update008_coverage(
        req, reconciliation_context=reconciliation_context
    )
    statuses = _effective_coverage(req, reconciliation)
    refs = v1._coverage_source_refs(req)

    raw_values = tuple(v for _, v in statuses)
    if any(v in ("CONFLICT", "ERROR", "UNKNOWN", "MISSING") for v in raw_values):
        status, critical, blocked = v1._critical_from_coverage(
            statuses, pure_watch_only=False
        )
        return v1.D4StaticAssociationProjection(
            status=status,
            critical_information_known=critical,
            detector_evidence_ids=(),
            active_mechanisms=(),
            coverage_statuses=statuses,
            coverage_source_refs=refs,
            d4_static_authority=None,
            blocked_reason=blocked,
            provenance=_projection_provenance(reconciliation, detector_performed=False),
        )

    pure_watch = v1._pure_watch_only(req.mechanisms)
    status, critical, blocked = v1._critical_from_coverage(
        statuses, pure_watch_only=pure_watch
    )
    if status != "READY":
        raise v1.D4StaticAssociationConflict(
            "COMPLETE_COVERAGE_CRITICAL_MAPPING_NOT_READY"
        )

    try:
        observations = v1._preview_observations(req, critical=critical)
        detector_ids, active_mechanisms = v1._detector_ids_from_observations(
            observations
        )
    except assembler.PacketAssemblyBlock as exc:
        return v1.D4StaticAssociationProjection(
            status="BLOCKED_DETECTOR_PROVENANCE",
            critical_information_known=critical,
            detector_evidence_ids=(),
            active_mechanisms=(),
            coverage_statuses=statuses,
            coverage_source_refs=refs,
            d4_static_authority=None,
            blocked_reason="FROZEN_PREVIEW_BLOCK:" + str(exc),
            provenance=_projection_provenance(reconciliation, detector_performed=False),
        )
    except assembler.PacketAssemblyConflict as exc:
        return v1.D4StaticAssociationProjection(
            status="BLOCKED_DETECTOR_CONFLICT",
            critical_information_known=InfoValue.error(
                "D4_CRITICAL_INFORMATION_CONFLICT"
            ),
            detector_evidence_ids=(),
            active_mechanisms=(),
            coverage_statuses=statuses,
            coverage_source_refs=refs,
            d4_static_authority=None,
            blocked_reason="FROZEN_PREVIEW_CONFLICT:" + str(exc),
            provenance=_projection_provenance(reconciliation, detector_performed=False),
        )
    except v1.D4StaticAssociationBlock as exc:
        return v1.D4StaticAssociationProjection(
            status="BLOCKED_DETECTOR_PROVENANCE",
            critical_information_known=critical,
            detector_evidence_ids=(),
            active_mechanisms=(),
            coverage_statuses=statuses,
            coverage_source_refs=refs,
            d4_static_authority=None,
            blocked_reason=str(exc),
            provenance=_projection_provenance(reconciliation, detector_performed=False),
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
        bound = lineage_prod.bind_d4_static_authority(
            unbound, req.lineage_projection
        )
    except (
        lineage_prod.LineageProductionBlock,
        lineage_prod.LineageProductionConflict,
    ) as exc:
        return v1.D4StaticAssociationProjection(
            status="BLOCKED_LINEAGE_BINDING",
            critical_information_known=critical,
            detector_evidence_ids=detector_ids,
            active_mechanisms=active_mechanisms,
            coverage_statuses=statuses,
            coverage_source_refs=refs,
            d4_static_authority=None,
            blocked_reason=str(exc),
            provenance=_projection_provenance(reconciliation, detector_performed=True),
        )

    return v1.D4StaticAssociationProjection(
        status="READY",
        critical_information_known=critical,
        detector_evidence_ids=detector_ids,
        active_mechanisms=active_mechanisms,
        coverage_statuses=statuses,
        coverage_source_refs=refs,
        d4_static_authority=bound,
        blocked_reason=None,
        provenance=_projection_provenance(reconciliation, detector_performed=True),
    )


def bind_v3_static_base(
    projection: v1.D4StaticAssociationProjection,
    *,
    base_type: Any,
) -> Any:
    return v1.bind_v3_static_base(projection, base_type=base_type)
