from __future__ import annotations

"""Production reconciliation for the exact mature no-active D4 coverage surface.

Scientific objects remain untouched:
- frozen Update008Output.state stays UNKNOWN;
- frozen lineage projection stays NO_ACTIVE_D4_OBSERVATION / relation=None;
- no D4StaticAuthority, EventRelation, MechanismObservation, or D4 packet is created.

This module only reconciles the two engineering coverage cross-checks frozen by
MATURE_NO_ACTIVE_D4_OBSERVATION_UPDATE008_LINEAGE_COMPLETENESS_RECONCILIATION_V1.
"""

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

import authoritative_d3_b5_d4_base_runtime_producers_v1 as b5prod
import authoritative_d3_d4_evidence_packet_assembler_resumption_v2 as assembler
import d4_market_event_lineage_production_binding_v2 as lineage_prod
import d4_static_detector_critical_production_binding_v1 as v1

from d2_to_b4_d4_causal_evidence_producers_v1 import EvidenceState
from strategy_rc1.d3_boundary_intelligence.types import RoleTransition
from strategy_rc1.runtime_guards.information_state import InfoValue


PRODUCER_ID = "MATURE_NO_ACTIVE_D4_OBSERVATION_UPDATE008_LINEAGE_COMPLETENESS_PRODUCTION_BINDING_V1"
SEMANTIC_ID = "MATURE_NO_ACTIVE_D4_OBSERVATION_UPDATE008_LINEAGE_COMPLETENESS_RECONCILIATION_V1"
SEMANTIC_CONTRACT_BLOB = "8b04c2bc4fc22540b62d3697f8e456f43b1b1264"
SEMANTIC_FREEZE_MANIFEST_BLOB = "d97524cc7c00ff6728fb7deb7b0193abfc5adfd1"
SELECTION_PROTOCOL_BLOB = "259ae399f317a774cb61d18ee509c5ff7efb5de1"
DECISION_BLOB = "51cfefca19417a75bfd32b91b52199d61d623209"
TRUTH_TABLE_BLOB = "bd5bd4fafb8447cbd9094800f8f4d3e209ad2ac1"
D4_STATIC_V1_BLOB = "9eac94f81d874f41f25f856aee16c60ee8deb312"
UPDATE008_PRODUCER_BLOB = "97a02f5584c1446ca5ae016bad383e3ed0e18bb5"
LINEAGE_V2_BLOB = "f334155bbb46ec2ff0ee748555cb15c1485d3036"
NO_PRIMARY_REASON = "NO_AUTHORITATIVE_PRIMARY"


class MatureNoActiveCoverageBlock(RuntimeError):
    pass


class MatureNoActiveCoverageConflict(MatureNoActiveCoverageBlock):
    pass


@dataclass(frozen=True)
class MatureNoActiveReconciliationContext:
    lineage_request: lineage_prod.D4LineageProductionRequest
    prior_lineage_ledger: Mapping[str, Any]
    causal_prebar_snapshot_ids: tuple[str, ...] = ()
    provenance: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "prior_lineage_ledger",
            MappingProxyType({str(k): v for k, v in self.prior_lineage_ledger.items()}),
        )
        object.__setattr__(
            self,
            "causal_prebar_snapshot_ids",
            tuple(sorted(set(str(x) for x in self.causal_prebar_snapshot_ids if str(x)))),
        )
        object.__setattr__(
            self,
            "provenance",
            MappingProxyType({str(k): str(v) for k, v in self.provenance.items()}),
        )


@dataclass(frozen=True)
class MatureNoActiveCoverageProjection:
    status: str
    applies: bool
    critical_information_known: InfoValue[bool]
    detector_evidence_ids: tuple[str, ...]
    active_mechanisms: tuple[str, ...]
    coverage_statuses: tuple[tuple[str, str], ...]
    coverage_source_refs: tuple[str, ...]
    d4_static_authority: None = None
    blocked_reason: str | None = None
    provenance: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "provenance",
            MappingProxyType({str(k): str(v) for k, v in self.provenance.items()}),
        )


def _value(x: Any) -> str:
    return x.value if hasattr(x, "value") else str(x)


def _blocked(req: v1.D4StaticAssociationRequest, reason: str) -> MatureNoActiveCoverageProjection:
    statuses = tuple((name, dict(req.coverage.by_class())[name].status) for name in v1.COVERAGE_CLASSES)
    return MatureNoActiveCoverageProjection(
        status="BLOCKED_NOT_EXACT_MATURE_NO_ACTIVE",
        applies=False,
        critical_information_known=InfoValue.unknown(),
        detector_evidence_ids=(),
        active_mechanisms=(),
        coverage_statuses=statuses,
        coverage_source_refs=v1._coverage_source_refs(req),
        blocked_reason=reason,
        provenance={
            "producer_id": PRODUCER_ID,
            "semantic_id": SEMANTIC_ID,
            "semantic_contract_blob": SEMANTIC_CONTRACT_BLOB,
            "scientific_update008_state_mutated": "false",
            "scientific_lineage_relation_mutated": "false",
            "synthetic_d4_packet_created": "false",
        },
    )


def _update008_exact(req: v1.D4StaticAssociationRequest) -> str | None:
    out = req.update008_output
    if out.conflict_lineage_refs or out.state is EvidenceState.CONFLICT:
        return "FROZEN_UPDATE008_CONFLICT"
    if out.unknown_lineage_refs:
        return "FROZEN_UPDATE008_UNKNOWN_LINEAGE"
    if out.state is not EvidenceState.UNKNOWN:
        return "UPDATE008_NOT_UNKNOWN"
    prov = dict(out.provenance)
    if prov.get("runtime_contract_id") != b5prod.RUNTIME_CONTRACT_ID:
        return "UPDATE008_RUNTIME_PROVENANCE_MISSING"
    if prov.get("f9_stage") != "UPDATE-008":
        return "UPDATE008_F9_PROVENANCE_MISSING"
    if prov.get("no_update002_backflow") != "true":
        return "UPDATE008_NO_BACKFLOW_PROVENANCE_MISSING"

    rr = out.role_runtime
    if not isinstance(rr, b5prod.RoleRuntimeOutput):
        return "ROLE_RUNTIME_REQUIRED"
    if rr.state is not EvidenceState.UNKNOWN:
        return "ROLE_RUNTIME_NOT_UNKNOWN"
    if rr.conflict_reasons:
        return "ROLE_RUNTIME_CONFLICT"
    if tuple(rr.unresolved_reasons) != (NO_PRIMARY_REASON,):
        return "ROLE_RUNTIME_UNKNOWN_REASON_NOT_NO_PRIMARY"
    if out.roles is None or rr.assignment is None or out.roles != rr.assignment:
        return "ROLE_ASSIGNMENT_SURFACE_MISMATCH"
    a = rr.assignment
    if a.primary_unit_id is not None:
        return "PRIMARY_ALREADY_EXISTS"
    if a.transition is not RoleTransition.NONE:
        return "ROLE_TRANSITION_NOT_NONE"
    if a.unresolved_reason is not None:
        return "ROLE_ASSIGNMENT_HAS_UNRESOLVED_REASON"
    if rr.primary_qbu_identities or out.produced_qbus:
        return "QBU_ALREADY_PRESENT"
    if tuple(rr.units) != tuple(out.units) or tuple(rr.role_evidence) != tuple(out.role_evidence):
        return "ROLE_RUNTIME_OUTPUT_SURFACE_MISMATCH"
    if any(x.unresolved_conflict for x in rr.role_evidence):
        return "ROLE_EVIDENCE_CONFLICT"
    if any(x.latest_qualified_use_cutoff is not None for x in rr.role_evidence):
        return "QUALIFIED_USE_EXISTS_WITHOUT_PRIMARY"
    if dict(rr.provenance).get("producer_semantic_contract_id") != "TAC_D3_B5_ROLE_STATE_PRODUCER_SEMANTIC_CONTRACT_V1":
        return "ROLE_RUNTIME_PROVENANCE_MISSING"
    return None


def _lineage_exact(
    req: v1.D4StaticAssociationRequest,
    ctx: MatureNoActiveReconciliationContext,
) -> str | None:
    lr = ctx.lineage_request
    if not isinstance(lr, lineage_prod.D4LineageProductionRequest):
        return "LINEAGE_REQUEST_SCHEMA"
    if lr.information_cutoff != req.information_cutoff:
        return "LINEAGE_CUTOFF_MISMATCH"
    if lr.trend_episode_id != req.trend_episode_id:
        return "LINEAGE_TREND_EPISODE_MISMATCH"
    if _value(lr.direction) != _value(req.direction):
        return "LINEAGE_DIRECTION_MISMATCH"
    if lr.future_evidence_detected:
        return "FUTURE_EVIDENCE"
    if lr.canonical_continuity_known is not True or lr.canonical_continuity_intact is not True:
        return "CANONICAL_CONTINUITY_NOT_AUTHORITATIVE"
    if tuple(lr.active_mechanisms):
        return "ACTIVE_MECHANISM_PRESENT"
    if lr.mechanisms != req.mechanisms:
        return "MECHANISM_SURFACE_MISMATCH"
    if lr.deep_preidentity is not None:
        return "DEEP_PREIDENTITY_PRESENT"
    if tuple(lr.runtime_b3_results) or tuple(lr.local_control_regain_results):
        return "B3_B4_RESULTS_PRESENT_ON_NO_PREBAR_SURFACE"
    if ctx.causal_prebar_snapshot_ids:
        return "CAUSAL_PREBAR_SNAPSHOT_PRESENT"

    opp = lr.existing_opportunity
    if opp is None:
        return "EXISTING_OPPORTUNITY_REQUIRED"
    if bool(getattr(opp, "terminal", True)):
        return "EXISTING_OPPORTUNITY_TERMINAL"
    if getattr(opp, "trend_episode_id", None) != req.trend_episode_id:
        return "OPPORTUNITY_TREND_EPISODE_MISMATCH"
    if _value(getattr(opp, "direction", None)) != _value(req.direction):
        return "OPPORTUNITY_DIRECTION_MISMATCH"

    prior = dict(ctx.prior_lineage_ledger)
    if prior.get("symbol") != lr.symbol:
        return "LEDGER_SYMBOL_MISMATCH"
    if prior.get("trend_episode_id") != lr.trend_episode_id:
        return "LEDGER_TREND_EPISODE_MISMATCH"
    if str(prior.get("direction_value")) != _value(lr.direction):
        return "LEDGER_DIRECTION_MISMATCH"
    if prior.get("coverage_intact") is not True:
        return "LEDGER_COVERAGE_NOT_INTACT"
    if int(prior.get("admission_count", 0)) < 1:
        return "WATCH_ORIGIN_ADMISSION_MISSING"
    if prior.get("active_event_open") is not True:
        return "LEDGER_ACTIVE_EVENT_NOT_OPEN"
    if prior.get("current_origin_watch") is not True:
        return "LEDGER_CURRENT_ORIGIN_NOT_WATCH"
    if prior.get("previous_terminal_cutoff") is not None:
        return "LEDGER_PRIOR_TERMINAL_PRESENT"
    if int(prior.get("genesis_cutoff", req.information_cutoff)) >= req.information_cutoff:
        return "NOT_STRICTLY_MATURE_AFTER_GENESIS"
    if int(prior.get("last_evaluated_cutoff", req.information_cutoff)) >= req.information_cutoff:
        return "LEDGER_NOT_BEFORE_CURRENT_CUTOFF"
    if not prior.get("coverage_ref") or not prior.get("coverage_chain_digest"):
        return "LEDGER_PROVENANCE_INCOMPLETE"

    p = req.lineage_projection
    if p.status != "NO_ACTIVE_D4_OBSERVATION":
        return "LINEAGE_STATUS_NOT_NO_ACTIVE"
    if p.relation is not None:
        return "LINEAGE_RELATION_SYNTHESIZED"
    if p.new_event_evidence is not None or p.independence is not None:
        return "NO_ACTIVE_LINEAGE_CARRIES_EVENT_EVIDENCE"
    if tuple(p.lineage_evidence_refs) or tuple(p.proof_kinds):
        return "NO_ACTIVE_LINEAGE_CARRIES_RELATION_PROOF"
    if p.blocked_reason != "NO_ACTIVE_D4_OBSERVATION":
        return "LINEAGE_BLOCKED_REASON_MISMATCH"
    pp = dict(p.provenance)
    if pp.get("coverage_ref") != prior.get("coverage_ref"):
        return "LINEAGE_COVERAGE_REF_MISMATCH"
    if pp.get("admission_count") != str(prior.get("admission_count")):
        return "LINEAGE_ADMISSION_COUNT_DRIFT"
    if not pp.get("coverage_chain_digest"):
        return "LINEAGE_PROPOSED_CHAIN_DIGEST_MISSING"
    if pp.get("coverage_chain_digest") == prior.get("coverage_chain_digest"):
        return "LINEAGE_LEDGER_NOT_PROPOSED_TO_ADVANCE"
    return None


def project_mature_no_active_coverage(
    req: v1.D4StaticAssociationRequest,
    *,
    reconciliation_context: MatureNoActiveReconciliationContext,
) -> MatureNoActiveCoverageProjection:
    v1._validate_request(req)

    facts = dict(req.coverage.by_class())
    if any(facts[name].status != "COMPLETE" for name in v1.COVERAGE_CLASSES):
        return _blocked(req, "CALLER_COVERAGE_NOT_COMPLETE")
    if req.coverage.future_evidence_detected:
        return _blocked(req, "FUTURE_EVIDENCE")
    if v1._mechanism_actual_status(req.mechanisms) != "COMPLETE":
        return _blocked(req, "MECHANISM_SURFACE_NOT_COMPLETE")
    if req.mechanisms != assembler.MechanismProducerOutputs():
        return _blocked(req, "CURRENT_MECHANISM_OUTPUTS_NOT_EMPTY")

    reason = _update008_exact(req)
    if reason is not None:
        return _blocked(req, reason)
    reason = _lineage_exact(req, reconciliation_context)
    if reason is not None:
        return _blocked(req, reason)

    statuses = tuple((name, "COMPLETE") for name in v1.COVERAGE_CLASSES)
    status, critical, blocked = v1._critical_from_coverage(
        statuses, pure_watch_only=False
    )
    if status != "READY" or critical != InfoValue.known(True) or blocked is not None:
        raise MatureNoActiveCoverageConflict("COMPLETE_NO_ACTIVE_CRITICAL_MAPPING_NOT_KNOWN_TRUE")

    return MatureNoActiveCoverageProjection(
        status="READY_NO_D4_OBSERVATION",
        applies=True,
        critical_information_known=critical,
        detector_evidence_ids=(),
        active_mechanisms=(),
        coverage_statuses=statuses,
        coverage_source_refs=v1._coverage_source_refs(req),
        d4_static_authority=None,
        blocked_reason=None,
        provenance={
            "producer_id": PRODUCER_ID,
            "semantic_id": SEMANTIC_ID,
            "semantic_contract_blob": SEMANTIC_CONTRACT_BLOB,
            "semantic_freeze_manifest_blob": SEMANTIC_FREEZE_MANIFEST_BLOB,
            "selection_protocol_blob": SELECTION_PROTOCOL_BLOB,
            "decision_blob": DECISION_BLOB,
            "truth_table_blob": TRUTH_TABLE_BLOB,
            "d4_static_v1_blob": D4_STATIC_V1_BLOB,
            "update008_producer_blob": UPDATE008_PRODUCER_BLOB,
            "lineage_v2_blob": LINEAGE_V2_BLOB,
            "update008_reconciliation": "COMPLETE_NOT_APPLICABLE_ROLE_STATE",
            "lineage_reconciliation": "COMPLETE_NO_ACTIVE_D4_OBSERVATION_NO_RELATION_REQUIRED",
            "scientific_update008_state_mutated": "false",
            "scientific_lineage_relation_mutated": "false",
            "synthetic_d4_packet_created": "false",
            "detector_projection_performed": "false_no_active_observation",
            "critical_information_known": "KNOWN_TRUE",
            "lineage_commit_required_after_full_staged_success": "true",
            "real_market_data_read": "false",
            "test_read": "false",
            "pnl": "false",
            "trading": "FORBIDDEN",
        },
    )
