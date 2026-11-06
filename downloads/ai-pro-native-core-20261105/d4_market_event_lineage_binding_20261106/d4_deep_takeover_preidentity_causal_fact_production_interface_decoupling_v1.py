from __future__ import annotations

"""Acyclic binding from preidentity deep facts through D4 SAME_EVENT to frozen deep production."""

from dataclasses import dataclass, field, replace
from types import MappingProxyType
from typing import Mapping

import authoritative_d3_b5_d4_base_runtime_producers_v1 as b5prod
import d4_deep_takeover_preidentity_causal_fact_production_interface_v1 as preid
import d4_market_event_lineage_production_binding_v2 as d4lineage
import nontrading_adapter_integration_v1 as frozen

from d2_to_b4_d4_causal_evidence_producers_v1 import EvidenceState


INTERFACE_ID = "D4_DEEP_TAKEOVER_PREIDENTITY_CAUSAL_FACT_PRODUCTION_INTERFACE_DECOUPLING_V1"
REQUIRED_D4_PROOF_KIND = "DEEPER_CONTINUATION_FROM_ACTIVE_SHALLOW_SETUP"


class DeepPreidentityBindingBlock(RuntimeError):
    pass


class DeepPreidentityBindingConflict(DeepPreidentityBindingBlock):
    pass


@dataclass(frozen=True)
class DeepPreidentityDecoupledTransactionResult:
    transaction_id: str
    lineage_projection: d4lineage.D4LineageProjection
    bound_deep_request: b5prod.DeepTakeoverRequest
    deep_projection: b5prod.DeepTakeoverProjection
    provenance: Mapping[str, str] = field(default_factory=dict)


def _assert_request_binding(
    *,
    preidentity: preid.DeepTakeoverPreidentityProjection,
    lineage_request: d4lineage.D4LineageProductionRequest,
    deep_request: b5prod.DeepTakeoverRequest,
) -> preid.DeepTakeoverPreidentityFacts:
    if preidentity.state is not EvidenceState.TRUE or preidentity.facts is None:
        raise DeepPreidentityBindingBlock("PREIDENTITY_DEEP_FACTS_NOT_AUTHORITATIVE_TRUE")
    if deep_request.same_market_event_identity_authoritative is True:
        raise DeepPreidentityBindingConflict("CALLER_PREAUTHORIZED_MARKET_EVENT_IDENTITY_FORBIDDEN")
    if d4lineage.MECH_DEEP not in lineage_request.active_mechanisms:
        raise DeepPreidentityBindingConflict("D4_DEEP_MECHANISM_NOT_ACTIVE")
    if lineage_request.mechanisms.deep_takeover is not None:
        raise DeepPreidentityBindingConflict("FIRST_IDENTITY_BINDING_MUST_NOT_CONSUME_DEEP_PROJECTION")
    if lineage_request.deep_preidentity != preidentity:
        raise DeepPreidentityBindingConflict("D4_REQUEST_PREIDENTITY_OBJECT_MISMATCH")

    active_opportunity = lineage_request.existing_opportunity
    if active_opportunity is None or active_opportunity.terminal:
        raise DeepPreidentityBindingConflict("ACTIVE_SHALLOW_OPPORTUNITY_REQUIRED_FOR_IDENTITY_BINDING")
    if (
        active_opportunity.opportunity_id != deep_request.opportunity_id
        or active_opportunity.market_event_id != deep_request.market_event_id
        or active_opportunity.trend_episode_id != deep_request.trend_episode_id
        or active_opportunity.direction != deep_request.direction
    ):
        raise DeepPreidentityBindingConflict("ACTIVE_SHALLOW_OPPORTUNITY_IDENTITY_MISMATCH")

    facts = preidentity.facts
    entry_unit = deep_request.deeper_entry_boundary.unit
    if entry_unit is None:
        raise DeepPreidentityBindingConflict("DEEP_REQUEST_ENTRY_UNIT_MISSING")
    checks = (
        lineage_request.information_cutoff == deep_request.information_cutoff == facts.information_cutoff,
        lineage_request.trend_episode_id == deep_request.trend_episode_id == facts.trend_episode_id,
        lineage_request.direction == deep_request.direction == facts.direction,
        deep_request.shallow_unit.unit_id == facts.shallow_unit_id,
        entry_unit.unit_id == facts.deeper_unit_id,
        deep_request.deeper_interaction == facts.deeper_interaction,
        tuple(deep_request.setup_lineage) == tuple(facts.setup_lineage),
        deep_request.shallow_behavior_confirmation_cutoff == facts.shallow_behavior_confirmation_cutoff,
        facts.shallow_operating_defense_no_longer_completes_setup is True,
        facts.deeper_boundary_independent is True,
    )
    if not all(checks):
        raise DeepPreidentityBindingConflict("PREIDENTITY_TO_DEEP_REQUEST_CAUSAL_BINDING_MISMATCH")
    return facts


def prepare_d4_same_event_then_produce_deep(
    *,
    projector: d4lineage.D4MarketEventLineageProductionProjectorV2,
    transaction_id: str,
    preidentity: preid.DeepTakeoverPreidentityProjection,
    lineage_request: d4lineage.D4LineageProductionRequest,
    deep_request: b5prod.DeepTakeoverRequest,
) -> DeepPreidentityDecoupledTransactionResult:
    """Enforce transaction order: preidentity -> D4 prepare -> identity bind -> frozen deep producer.

    D4 commit remains the caller's downstream atomic-commit responsibility.
    """
    if not isinstance(projector, d4lineage.D4MarketEventLineageProductionProjectorV2):
        raise DeepPreidentityBindingConflict("D4_PROJECTOR_SCHEMA")
    if not isinstance(transaction_id, str) or not transaction_id:
        raise DeepPreidentityBindingBlock("TRANSACTION_ID_REQUIRED")

    facts = _assert_request_binding(
        preidentity=preidentity,
        lineage_request=lineage_request,
        deep_request=deep_request,
    )

    lineage = projector.prepare(transaction_id, lineage_request)
    if lineage.relation is not frozen.EventRelation.SAME_EVENT:
        raise DeepPreidentityBindingBlock("D4_SAME_EVENT_NOT_AUTHORITATIVE")
    if REQUIRED_D4_PROOF_KIND not in lineage.proof_kinds:
        raise DeepPreidentityBindingBlock("D4_DEEPER_CONTINUATION_PROOF_KIND_MISSING")
    expected_event_ref = "InteractionEvent:" + facts.deeper_interaction.event_id
    if expected_event_ref not in lineage.lineage_evidence_refs:
        raise DeepPreidentityBindingConflict("D4_DEEP_INTERACTION_REF_MISSING")

    bound = replace(deep_request, same_market_event_identity_authoritative=True)
    deep = b5prod.produce_deep_takeover(bound)
    if deep.state is not EvidenceState.TRUE or deep.evidence is None:
        raise DeepPreidentityBindingConflict("FROZEN_DEEP_PRODUCER_DID_NOT_CONFIRM_PREIDENTITY_FACTS")
    if (
        deep.evidence.deeper_interaction != facts.deeper_interaction
        or tuple(deep.evidence.setup_lineage) != tuple(facts.setup_lineage)
        or deep.evidence.shallow_operating_defense_no_longer_completes_setup is not True
        or deep.evidence.deeper_boundary_independent is not True
    ):
        raise DeepPreidentityBindingConflict("FROZEN_DEEP_PROJECTION_CAUSAL_FACT_MISMATCH")

    provenance = MappingProxyType({
        "interface_id": INTERFACE_ID,
        "d4_producer_id": d4lineage.PRODUCER_ID,
        "d4_semantic_id": d4lineage.SEMANTIC_ID,
        "required_d4_proof_kind": REQUIRED_D4_PROOF_KIND,
        "identity_binding_order": "PREIDENTITY_THEN_D4_SAME_EVENT_THEN_DEEP_PRODUCER",
        "identity_source": "ACTIVE_SHALLOW_OPPORTUNITY_PLUS_D4_SAME_EVENT_CAUSAL_PROOF",
        "self_proof": "false",
    })
    return DeepPreidentityDecoupledTransactionResult(
        transaction_id=transaction_id,
        lineage_projection=lineage,
        bound_deep_request=bound,
        deep_projection=deep,
        provenance=provenance,
    )
