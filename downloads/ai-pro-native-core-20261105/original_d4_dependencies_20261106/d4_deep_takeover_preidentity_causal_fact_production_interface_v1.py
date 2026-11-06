from __future__ import annotations

"""Mechanical preidentity deep-takeover causal-fact production interface V1.

This module exposes only the already-frozen deep causal facts needed by the
D4 market-event lineage projector. It does not consume or produce a downstream
market-event identity, does not construct DeepStructureTakeoverEvidence, and
does not add selectors, thresholds, timers, strategy state, or market I/O.
"""

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping

import authoritative_d3_b5_d4_base_runtime_producers_v1 as b5prod

from d2_to_b4_d4_causal_evidence_producers_v1 import EvidenceState
from strategy_rc1.d2_market_state.types import TrendDirection
from strategy_rc1.d3_boundary_intelligence.types import (
    BreakState,
    EconomicBoundaryUnit,
    InteractionEvent,
    InteractionResolution,
    StructuralDepthRelation,
)
from strategy_rc1.d4_opportunity.types import LocalTrendControlRegainEvidence


PRODUCER_ID = "D4_DEEP_TAKEOVER_PREIDENTITY_CAUSAL_FACT_PRODUCTION_INTERFACE_V1"
FROZEN_DEEP_PRODUCER_BLOB = "97a02f5584c1446ca5ae016bad383e3ed0e18bb5"
FROZEN_DEEP_SEMANTIC_CONTRACT_BLOB = "7889626f725e8dce2cf7c51fa277c72d82559623"


@dataclass(frozen=True)
class DeepTakeoverPreidentityRequest:
    information_cutoff: int
    trend_episode_id: str
    direction: TrendDirection
    shallow_unit: EconomicBoundaryUnit
    deeper_entry_boundary: b5prod.EntryBoundaryProjection
    deeper_interaction: InteractionEvent
    role_runtime: b5prod.RoleRuntimeOutput
    shallow_behavior_confirmation_cutoff: int | None
    local_control_regain: LocalTrendControlRegainEvidence | None
    setup_lineage: tuple[str, ...]
    provenance: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class DeepTakeoverPreidentityFacts:
    information_cutoff: int
    trend_episode_id: str
    direction: TrendDirection
    shallow_unit_id: str
    deeper_unit_id: str
    deeper_interaction: InteractionEvent
    setup_lineage: tuple[str, ...]
    shallow_behavior_confirmation_cutoff: int | None
    contact_cutoff: int
    structural_depth_relation: StructuralDepthRelation
    shallow_operating_defense_no_longer_completes_setup: bool
    deeper_boundary_independent: bool
    provenance: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class DeepTakeoverPreidentityProjection:
    state: EvidenceState
    facts: DeepTakeoverPreidentityFacts | None
    reason: str
    provenance: Mapping[str, str] = field(default_factory=dict)


def _prov() -> Mapping[str, str]:
    return MappingProxyType({
        "producer_id": PRODUCER_ID,
        "frozen_deep_producer_blob": FROZEN_DEEP_PRODUCER_BLOB,
        "frozen_deep_semantic_contract_blob": FROZEN_DEEP_SEMANTIC_CONTRACT_BLOB,
        "authority_phase": "PREIDENTITY_CAUSAL_FACTS_ONLY",
    })


def _projection(
    state: EvidenceState,
    facts: DeepTakeoverPreidentityFacts | None,
    reason: str,
) -> DeepTakeoverPreidentityProjection:
    return DeepTakeoverPreidentityProjection(
        state=state,
        facts=facts,
        reason=reason,
        provenance=_prov(),
    )


def produce_preidentity_deep_causal_facts(
    request: DeepTakeoverPreidentityRequest,
) -> DeepTakeoverPreidentityProjection:
    """Expose frozen deep causal facts without requiring downstream identity."""
    if not isinstance(request, DeepTakeoverPreidentityRequest):
        raise TypeError("DEEP_PREIDENTITY_REQUEST_SCHEMA")

    entry = request.deeper_entry_boundary
    if entry.state is EvidenceState.CONFLICT:
        return _projection(EvidenceState.CONFLICT, None, "DEEPER_ENTRY_BOUNDARY_CONFLICT")
    if entry.state is not EvidenceState.TRUE or entry.unit is None:
        return _projection(EvidenceState.UNKNOWN, None, "DEEPER_ENTRY_BOUNDARY_UNKNOWN")

    event = request.deeper_interaction
    if event.target_trend_episode_id != request.trend_episode_id or event.target_direction is not request.direction:
        return _projection(EvidenceState.CONFLICT, None, "DEEPER_INTERACTION_LINEAGE_CONFLICT")
    if event.anchor_episode_id not in entry.unit.anchor_episode_ids:
        return _projection(EvidenceState.CONFLICT, None, "DEEPER_INTERACTION_ENTRY_BOUNDARY_CONFLICT")
    if not b5prod._event_actual_contact(event, request.information_cutoff):
        return _projection(EvidenceState.FALSE, None, "DEEPER_APPROACH_ONLY_OR_NO_ACTUAL_CONTACT")
    if event.break_state is BreakState.TRUE_BREAK or (
        event.terminal and event.resolution is InteractionResolution.RESOLVED_WRONG_SIDE
    ):
        return _projection(EvidenceState.FALSE, None, "DEEPER_BOUNDARY_TERMINALLY_INVALIDATED")

    classes = dict(request.role_runtime.depth_class_by_unit_id)
    shallow_class = classes.get(request.shallow_unit.unit_id, b5prod.DEPTH_UNRESOLVED)
    deeper_unit = entry.unit
    deeper_class = classes.get(deeper_unit.unit_id, b5prod.DEPTH_UNRESOLVED)
    relation = b5prod.depth_relation(shallow_class, deeper_class)
    if relation is StructuralDepthRelation.UNRESOLVED:
        return _projection(EvidenceState.UNKNOWN, None, "DEEPER_STRUCTURAL_DEPTH_UNRESOLVED")

    independent = (
        deeper_unit.unit_id != request.shallow_unit.unit_id
        and set(request.shallow_unit.anchor_episode_ids).isdisjoint(deeper_unit.anchor_episode_ids)
        and relation is StructuralDepthRelation.DEEPER
    )
    if not independent:
        return _projection(EvidenceState.FALSE, None, "DEEPER_BOUNDARY_NOT_INDEPENDENT_DEEPER_EBU")

    contact_cutoff = event.started_at
    if contact_cutoff is None:
        return _projection(EvidenceState.UNKNOWN, None, "DEEPER_CONTACT_CUTOFF_UNKNOWN")
    shallow_already_completed = (
        request.shallow_behavior_confirmation_cutoff is not None
        and request.shallow_behavior_confirmation_cutoff <= contact_cutoff
    )
    if shallow_already_completed:
        return _projection(EvidenceState.FALSE, None, "SHALLOW_SETUP_COMPLETED_FIRST")

    facts = DeepTakeoverPreidentityFacts(
        information_cutoff=request.information_cutoff,
        trend_episode_id=request.trend_episode_id,
        direction=request.direction,
        shallow_unit_id=request.shallow_unit.unit_id,
        deeper_unit_id=deeper_unit.unit_id,
        deeper_interaction=event,
        setup_lineage=tuple(request.setup_lineage),
        shallow_behavior_confirmation_cutoff=request.shallow_behavior_confirmation_cutoff,
        contact_cutoff=contact_cutoff,
        structural_depth_relation=StructuralDepthRelation.DEEPER,
        shallow_operating_defense_no_longer_completes_setup=True,
        deeper_boundary_independent=True,
        provenance=_prov(),
    )
    return _projection(
        EvidenceState.TRUE,
        facts,
        "DEEP_TAKEOVER_PREIDENTITY_CAUSAL_FACTS_AUTHORITATIVE",
    )
