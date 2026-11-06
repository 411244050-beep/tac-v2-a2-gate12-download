from __future__ import annotations

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
PROVISIONAL_DIR = REPO_ROOT / "provisional_shadow_v1"
if str(PROVISIONAL_DIR) not in sys.path:
    sys.path.insert(0, str(PROVISIONAL_DIR))

"""Pure active-D4 mechanism composition over already-frozen producers.

This module intentionally owns no durable state, no runtime dispatch and no
strategy science.  It consumes one same-cutoff typed authority bundle and
returns MechanismProducerOutputs plus the typed source sidecars later needed
by full-live D5.
"""

from dataclasses import dataclass, field
from fractions import Fraction
from types import MappingProxyType
from typing import Any, Mapping

from strategy_rc1.d2_market_state.types import TrendDirection
from strategy_rc1.d4_opportunity.types import OpportunityMechanism

import authoritative_d3_d4_evidence_packet_assembler_resumption_v2 as assembler
import authoritative_d3_b5_d4_base_runtime_producers_v1 as b5prod
import d2_to_b4_d4_causal_evidence_producers_v1 as b4proj
import d4_deep_takeover_preidentity_causal_fact_production_interface_v1 as deep_preid

from d2_to_b4_d4_causal_evidence_producers_v1 import EvidenceState


class FullLiveActiveD4MechanismBlock(RuntimeError):
    pass


class FullLiveActiveD4MechanismConflict(FullLiveActiveD4MechanismBlock):
    pass


@dataclass(frozen=True)
class ActiveD4CompositionInputV1:
    information_cutoff: int
    symbol: str
    trend_episode_id: str
    direction: TrendDirection
    canonical_segment_id: str
    current_close: Fraction
    theta_progress: Fraction
    opportunity: Any
    market_event_id: str
    setup_lineage: tuple[str, ...]
    events: tuple[Any, ...]
    episodes: tuple[Any, ...]
    units: tuple[Any, ...]
    role_runtime: Any
    minor_history: tuple[Any, ...]
    canonical_records: tuple[Any, ...]
    structural_by_candidate: Mapping[str, Any]
    recovery_by_candidate: Mapping[str, Any]
    platform_projection: Any
    existing_fixed_adverse_by_setup: Mapping[str, Any] = field(
        default_factory=dict
    )
    shallow_behavior_confirmation_cutoff: int | None = None
    shallow_behavior_confirmation_authority_complete: bool = False

    def __post_init__(self) -> None:
        if self.information_cutoff < 0:
            raise ValueError("ACTIVE_D4_CUTOFF_NEGATIVE")
        if not self.symbol or not self.trend_episode_id:
            raise ValueError("ACTIVE_D4_IDENTITY_REQUIRED")
        if not self.canonical_segment_id:
            raise ValueError("ACTIVE_D4_CANONICAL_SEGMENT_REQUIRED")
        if self.direction not in (TrendDirection.LONG, TrendDirection.SHORT):
            raise ValueError("ACTIVE_D4_DIRECTION_REQUIRED")
        object.__setattr__(
            self,
            "structural_by_candidate",
            MappingProxyType(dict(self.structural_by_candidate)),
        )
        object.__setattr__(
            self,
            "recovery_by_candidate",
            MappingProxyType(dict(self.recovery_by_candidate)),
        )
        object.__setattr__(
            self,
            "existing_fixed_adverse_by_setup",
            MappingProxyType(dict(self.existing_fixed_adverse_by_setup)),
        )


@dataclass(frozen=True)
class ActiveD4CompositionResultV1:
    mechanisms: assembler.MechanismProducerOutputs
    active_mechanisms: tuple[str, ...]
    local_control_regain_results: tuple[Any, ...]
    d5_sidecars: Mapping[str, Any]
    deep_preidentity: Any | None = None
    unbound_deep_request: Any | None = None
    fixed_adverse_updates: Mapping[str, Any] = field(default_factory=dict)
    provenance: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "d5_sidecars",
            MappingProxyType(dict(self.d5_sidecars)),
        )
        object.__setattr__(
            self,
            "fixed_adverse_updates",
            MappingProxyType(dict(self.fixed_adverse_updates)),
        )
        object.__setattr__(
            self,
            "provenance",
            MappingProxyType(dict(self.provenance)),
        )


def _enum(value: Any) -> str:
    return str(getattr(value, "value", value))


def _candidate_event_map(events: tuple[Any, ...]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for event in events:
        cid = str(getattr(event, "candidate_id", ""))
        eid = str(getattr(event, "event_id", ""))
        if not cid or not eid:
            raise FullLiveActiveD4MechanismConflict(
                "INTERACTION_IDENTITY_MISSING"
            )
        old = out.get(cid)
        if old is not None and old != event:
            raise FullLiveActiveD4MechanismConflict(
                "MULTIPLE_INTERACTIONS_FOR_CANDIDATE:" + cid
            )
        out[cid] = event
    return out


def _episodes_by_candidate(episodes: tuple[Any, ...]) -> dict[str, tuple[str, ...]]:
    out: dict[str, list[str]] = {}
    for ep in episodes:
        cid = str(getattr(ep, "candidate_id", ""))
        aid = str(getattr(ep, "anchor_episode_id", ""))
        if not cid or not aid:
            raise FullLiveActiveD4MechanismConflict(
                "ANCHOR_EPISODE_IDENTITY_MISSING"
            )
        out.setdefault(cid, []).append(aid)
    return {
        cid: tuple(sorted(set(aids)))
        for cid, aids in out.items()
    }


def _closed_prices(inp: ActiveD4CompositionInputV1) -> tuple[Any, ...]:
    rows: list[Any] = []
    seen: dict[int, Fraction] = {}
    for rec in inp.canonical_records:
        bar = getattr(rec, "bar", None)
        segment = getattr(rec, "canonical_segment_id", None)
        if bar is None:
            raise FullLiveActiveD4MechanismBlock(
                "D1_CANONICAL_RECORD_BAR_MISSING"
            )
        close_time = getattr(bar, "close_time", None)
        close = getattr(bar, "close", None)
        if close_time is None or close is None:
            raise FullLiveActiveD4MechanismBlock(
                "D1_CANONICAL_RECORD_CLOSE_MISSING"
            )
        cutoff = int(close_time)
        if cutoff > inp.information_cutoff:
            raise FullLiveActiveD4MechanismConflict(
                "D1_FUTURE_CANONICAL_RECORD"
            )
        if str(segment) != inp.canonical_segment_id:
            continue
        value = Fraction(close)
        old = seen.get(cutoff)
        if old is not None and old != value:
            raise FullLiveActiveD4MechanismConflict(
                "DIVERGENT_CLOSE_AT_CUTOFF:" + str(cutoff)
            )
        seen[cutoff] = value
    for cutoff, close in sorted(seen.items()):
        rows.append(
            b4proj.ClosedPriceObservation(
                information_cutoff=cutoff,
                close=close,
                provenance={
                    "source": "D1_CANONICAL_RECORD",
                    "canonical_segment_id": inp.canonical_segment_id,
                },
            )
        )
    if not rows or rows[-1].information_cutoff != inp.information_cutoff:
        raise FullLiveActiveD4MechanismBlock(
            "D1_CANONICAL_CLOSE_HISTORY_NOT_COMPLETE_THROUGH_CUTOFF"
        )
    return tuple(rows)


def _lineage_context(
    inp: ActiveD4CompositionInputV1,
    *,
    event: Any,
) -> b4proj.LineageContext:
    return b4proj.LineageContext(
        symbol=inp.symbol,
        target_trend_episode_id=inp.trend_episode_id,
        direction=inp.direction,
        information_cutoff=inp.information_cutoff,
        canonical_segment_id=inp.canonical_segment_id,
        interaction_event_id=str(event.event_id),
        market_event_id=inp.market_event_id,
        source_evidence_refs=(
            "InteractionEvent:" + str(event.event_id),
            "Opportunity:" + str(inp.opportunity.opportunity_id),
        ),
        continuity_known=True,
        continuity_intact=True,
        same_cutoff_order_proven=True,
    )


def _event_setup_key(inp: ActiveD4CompositionInputV1, event: Any) -> str:
    return (
        str(inp.opportunity.opportunity_id)
        + "|"
        + str(event.event_id)
    )


def _entry_boundary_for_event(
    inp: ActiveD4CompositionInputV1,
    event: Any,
    mechanism: OpportunityMechanism,
) -> Any:
    required = (str(event.anchor_episode_id),)
    return b5prod.attribute_entry_boundary(
        required_anchor_episode_ids=required,
        units=inp.units,
        episodes=inp.episodes,
        target_trend_episode_id=inp.trend_episode_id,
        direction=inp.direction,
        information_cutoff=inp.information_cutoff,
        mechanism=mechanism.value,
    )


def _local_regain(
    inp: ActiveD4CompositionInputV1,
    *,
    event: Any,
    adverse_reference_pivot_id: str,
    closed_prices: tuple[Any, ...],
) -> Any:
    result = b4proj.produce_local_trend_control_regain(
        b4proj.LocalTrendControlRegainRequest(
            context=_lineage_context(inp, event=event),
            pivots=inp.minor_history,
            adverse_reference_pivot_id=adverse_reference_pivot_id,
            theta_progress=inp.theta_progress,
            closed_prices=closed_prices,
        )
    )
    if result.state is EvidenceState.CONFLICT:
        raise FullLiveActiveD4MechanismConflict(
            "LOCAL_CONTROL_REGAIN_CONFLICT:"
            + str(event.event_id)
            + ":"
            + result.reason
        )
    return result


def _normal_projection(
    inp: ActiveD4CompositionInputV1,
    *,
    event: Any,
    closed_prices: tuple[Any, ...],
) -> tuple[Any, Any, Any]:
    entry = _entry_boundary_for_event(
        inp,
        event,
        OpportunityMechanism.NORMAL_RETEST_CONTINUATION,
    )
    setup_key = _event_setup_key(inp, event)
    existing = inp.existing_fixed_adverse_by_setup.get(setup_key)

    base = b5prod.produce_normal_retest(
        setup_key=setup_key,
        information_cutoff=inp.information_cutoff,
        trend_episode_id=inp.trend_episode_id,
        direction=inp.direction,
        interaction=event,
        entry_boundary=entry,
        pivots=inp.minor_history,
        canonical_segment_id=inp.canonical_segment_id,
        setup_lineage=inp.setup_lineage,
        existing_fixed_reference=existing,
        local_control_regain=None,
    )
    if base.state is EvidenceState.CONFLICT:
        raise FullLiveActiveD4MechanismConflict(
            "NORMAL_BASE_CONFLICT:" + base.reason
        )
    if base.adverse_reference is None:
        return base, entry, None

    regain = _local_regain(
        inp,
        event=event,
        adverse_reference_pivot_id=base.adverse_reference.pivot_id,
        closed_prices=closed_prices,
    )
    consumer = b4proj.safe_b4_consumer(regain)
    final = b5prod.produce_normal_retest(
        setup_key=setup_key,
        information_cutoff=inp.information_cutoff,
        trend_episode_id=inp.trend_episode_id,
        direction=inp.direction,
        interaction=event,
        entry_boundary=entry,
        pivots=inp.minor_history,
        canonical_segment_id=inp.canonical_segment_id,
        setup_lineage=inp.setup_lineage,
        existing_fixed_reference=base.adverse_reference,
        local_control_regain=consumer,
    )
    if final.state is EvidenceState.CONFLICT:
        raise FullLiveActiveD4MechanismConflict(
            "NORMAL_FINAL_CONFLICT:" + final.reason
        )
    return final, entry, regain


def compose_active_d4_mechanisms(
    inp: ActiveD4CompositionInputV1,
) -> ActiveD4CompositionResultV1:
    if inp.opportunity is None or getattr(inp.opportunity, "terminal", False):
        raise FullLiveActiveD4MechanismBlock(
            "ACTIVE_NONTERMINAL_OPPORTUNITY_REQUIRED"
        )
    if (
        getattr(inp.opportunity, "trend_episode_id", None)
        != inp.trend_episode_id
        or getattr(inp.opportunity, "direction", None) is not inp.direction
    ):
        raise FullLiveActiveD4MechanismConflict(
            "OPPORTUNITY_TREND_LINEAGE_MISMATCH"
        )
    if str(getattr(inp.opportunity, "market_event_id", "")) != inp.market_event_id:
        raise FullLiveActiveD4MechanismConflict(
            "OPPORTUNITY_MARKET_EVENT_ID_MISMATCH"
        )

    closed_prices = _closed_prices(inp)
    event_by_candidate = _candidate_event_map(inp.events)
    anchor_by_candidate = _episodes_by_candidate(inp.episodes)

    normal_rows: list[tuple[Any, Any, Any, Any]] = []
    fbr_rows: list[tuple[Any, Any, Any]] = []
    regain_results: list[Any] = []
    fixed_updates: dict[str, Any] = {}

    for cid in sorted(event_by_candidate):
        event = event_by_candidate[cid]
        if (
            event.target_trend_episode_id != inp.trend_episode_id
            or event.target_direction is not inp.direction
        ):
            continue
        if event.anchor_episode_id not in anchor_by_candidate.get(cid, ()):
            raise FullLiveActiveD4MechanismConflict(
                "INTERACTION_ANCHOR_EPISODE_LINEAGE_MISMATCH:"
                + str(event.event_id)
            )

        normal, normal_entry, regain = _normal_projection(
            inp,
            event=event,
            closed_prices=closed_prices,
        )
        if regain is not None:
            regain_results.append(regain)
        normal_rows.append((event, normal, normal_entry, regain))
        if (
            normal.adverse_reference is not None
            and _event_setup_key(inp, event)
            not in inp.existing_fixed_adverse_by_setup
        ):
            fixed_updates[_event_setup_key(inp, event)] = (
                normal.adverse_reference
            )

        recovery = inp.recovery_by_candidate.get(cid)
        if (
            _enum(event.break_state) == "FALSE_BREAK"
            and recovery is not None
            and getattr(recovery, "state", None) is EvidenceState.TRUE
            and getattr(recovery, "consumer_evidence", None) is not None
        ):
            fbr = b5prod.wire_false_break_reclaim(
                event,
                setup_lineage=inp.setup_lineage,
            )
            fbr_entry = _entry_boundary_for_event(
                inp,
                event,
                OpportunityMechanism.FALSE_BREAK_RECLAIM,
            )
            fbr_rows.append((event, fbr, fbr_entry))

    # Mechanism overlap is intentionally not resolved here.  Frozen D4
    # assembler precedence owns the classification.  We may only carry at most
    # one evidence object per mechanism into MechanismProducerOutputs.  Multiple
    # disconnected instances of the same mechanism in one Opportunity are a
    # lineage conflict, not a ranking problem.
    normal_active = [
        row for row in normal_rows
        if row[1].state is EvidenceState.TRUE
        and row[1].evidence is not None
    ]
    if len(normal_active) > 1:
        raise FullLiveActiveD4MechanismConflict(
            "MULTIPLE_ACTIVE_NORMAL_RETEST_INSTANCES"
        )
    if len(fbr_rows) > 1:
        raise FullLiveActiveD4MechanismConflict(
            "MULTIPLE_ACTIVE_FALSE_BREAK_INSTANCES"
        )

    normal_projection = normal_active[0][1] if normal_active else None
    normal_entry = normal_active[0][2] if normal_active else None
    fbr = fbr_rows[0][1] if fbr_rows else None
    fbr_entry = fbr_rows[0][2] if fbr_rows else None

    platform_evidence = getattr(
        inp.platform_projection,
        "platform_reexpansion_evidence",
        None,
    )
    platform_entry = None
    if platform_evidence is not None:
        contributing = tuple(
            getattr(inp.platform_projection.platform, "contributing_event_ids", ())
        )
        required_anchor_ids: list[str] = []
        event_by_id = {
            str(e.event_id): e for e in inp.events
            if getattr(e, "event_id", None)
        }
        for event_id in contributing:
            event = event_by_id.get(str(event_id))
            if event is None:
                raise FullLiveActiveD4MechanismBlock(
                    "PLATFORM_CONTRIBUTING_EVENT_MISSING:" + str(event_id)
                )
            required_anchor_ids.append(str(event.anchor_episode_id))
        platform_entry = b5prod.attribute_entry_boundary(
            required_anchor_episode_ids=tuple(required_anchor_ids),
            units=inp.units,
            episodes=inp.episodes,
            target_trend_episode_id=inp.trend_episode_id,
            direction=inp.direction,
            information_cutoff=inp.information_cutoff,
            mechanism=OpportunityMechanism.PLATFORM_REEXPANSION.value,
        )

    # Deep follows the frozen causal identity order:
    # preidentity facts -> D4 SAME_EVENT proof -> frozen Deep producer.
    # This pure composer may prepare preidentity facts and an unbound request,
    # but it must never self-authorize market-event identity.
    deep_projection = None
    deep_preidentity = None
    unbound_deep_request = None
    deep_entry = None
    role_runtime = inp.role_runtime
    assignment = getattr(role_runtime, "assignment", None)
    by_unit = {str(u.unit_id): u for u in inp.units}
    shallow_id = None if assignment is None else assignment.primary_unit_id
    if shallow_id:
        shallow = by_unit.get(str(shallow_id))
        if shallow is None:
            raise FullLiveActiveD4MechanismConflict(
                "PRIMARY_SHALLOW_UNIT_MISSING"
            )
        deeper_role_rows = [
            row for row in tuple(getattr(role_runtime, "role_evidence", ()))
            if getattr(row, "structural_depth_relation_to_primary", None)
            is b5prod.StructuralDepthRelation.DEEPER
            and getattr(row, "active_qualifying_interaction", False)
            and getattr(getattr(row, "unit", None), "unit_id", None)
            != shallow_id
        ]
        if len(deeper_role_rows) > 1:
            raise FullLiveActiveD4MechanismConflict(
                "MULTIPLE_B5_DEEPER_ACTIVE_ROLE_ROWS"
            )
        if len(deeper_role_rows) == 1:
            if not inp.shallow_behavior_confirmation_authority_complete:
                raise FullLiveActiveD4MechanismBlock(
                    "DEEP_SHALLOW_CONFIRMATION_CUTOFF_AUTHORITY_INCOMPLETE"
                )
            deeper_unit = deeper_role_rows[0].unit
            required = tuple(deeper_unit.anchor_episode_ids)
            deep_entry = b5prod.attribute_entry_boundary(
                required_anchor_episode_ids=required,
                units=inp.units,
                episodes=inp.episodes,
                target_trend_episode_id=inp.trend_episode_id,
                direction=inp.direction,
                information_cutoff=inp.information_cutoff,
                mechanism=OpportunityMechanism.DEEP_STRUCTURE_TAKEOVER.value,
            )
            event_candidates = [
                e for e in inp.events
                if e.target_trend_episode_id == inp.trend_episode_id
                and e.target_direction is inp.direction
                and e.anchor_episode_id in set(required)
                and _enum(e.control) in ("INTERACTION_ACTIVE", "RESOLVED")
                and e.started_at is not None
                and e.started_at <= inp.information_cutoff
            ]
            if len(event_candidates) > 1:
                raise FullLiveActiveD4MechanismConflict(
                    "MULTIPLE_DEEP_INTERACTIONS_FOR_B5_DEEPER_ROLE"
                )
            if len(event_candidates) == 1:
                deep_event = event_candidates[0]
                setup_key = _event_setup_key(inp, deep_event)
                fixed = inp.existing_fixed_adverse_by_setup.get(setup_key)
                if fixed is not None:
                    if (
                        fixed.setup_key != setup_key
                        or fixed.direction is not inp.direction
                        or fixed.canonical_segment_id
                        != inp.canonical_segment_id
                        or fixed.confirmed_at > inp.information_cutoff
                    ):
                        raise FullLiveActiveD4MechanismConflict(
                            "DEEP_FIXED_ADVERSE_REFERENCE_CONFLICT"
                        )
                else:
                    state, fixed, reason = b5prod._select_adverse_reference(
                        setup_key=setup_key,
                        direction=inp.direction,
                        contact_cutoff=deep_event.started_at,
                        information_cutoff=inp.information_cutoff,
                        canonical_segment_id=inp.canonical_segment_id,
                        pivots=inp.minor_history,
                    )
                    if state is EvidenceState.CONFLICT:
                        raise FullLiveActiveD4MechanismConflict(
                            "DEEP_ADVERSE_REFERENCE_CONFLICT:" + reason
                        )
                    if state is EvidenceState.TRUE and fixed is not None:
                        fixed_updates[setup_key] = fixed

                deep_regain = None
                local_regain = None
                if fixed is not None:
                    deep_regain = _local_regain(
                        inp,
                        event=deep_event,
                        adverse_reference_pivot_id=fixed.pivot_id,
                        closed_prices=closed_prices,
                    )
                    regain_results.append(deep_regain)
                    local_regain = b4proj.safe_b4_consumer(deep_regain)

                deep_preidentity = (
                    deep_preid.produce_preidentity_deep_causal_facts(
                        deep_preid.DeepTakeoverPreidentityRequest(
                            information_cutoff=inp.information_cutoff,
                            trend_episode_id=inp.trend_episode_id,
                            direction=inp.direction,
                            shallow_unit=shallow,
                            deeper_entry_boundary=deep_entry,
                            deeper_interaction=deep_event,
                            role_runtime=role_runtime,
                            shallow_behavior_confirmation_cutoff=(
                                inp.shallow_behavior_confirmation_cutoff
                            ),
                            local_control_regain=local_regain,
                            setup_lineage=inp.setup_lineage,
                            provenance={
                                "producer_id": (
                                    "FULL_LIVE_ACTIVE_D4_MECHANISM_COMPOSER_V1"
                                )
                            },
                        )
                    )
                )
                if deep_preidentity.state is EvidenceState.CONFLICT:
                    raise FullLiveActiveD4MechanismConflict(
                        "DEEP_PREIDENTITY_CONFLICT:"
                        + deep_preidentity.reason
                    )
                if (
                    deep_preidentity.state is EvidenceState.TRUE
                    and deep_preidentity.facts is not None
                ):
                    unbound_deep_request = b5prod.DeepTakeoverRequest(
                        information_cutoff=inp.information_cutoff,
                        trend_episode_id=inp.trend_episode_id,
                        direction=inp.direction,
                        opportunity_id=str(inp.opportunity.opportunity_id),
                        market_event_id=inp.market_event_id,
                        shallow_unit=shallow,
                        deeper_entry_boundary=deep_entry,
                        deeper_interaction=deep_event,
                        role_runtime=role_runtime,
                        shallow_behavior_confirmation_cutoff=(
                            inp.shallow_behavior_confirmation_cutoff
                        ),
                        same_market_event_identity_authoritative=False,
                        local_control_regain=local_regain,
                        setup_lineage=inp.setup_lineage,
                        provenance={
                            "producer_id": (
                                "FULL_LIVE_ACTIVE_D4_MECHANISM_COMPOSER_V1"
                            ),
                            "identity_binding": (
                                "PREIDENTITY_THEN_D4_SAME_EVENT_REQUIRED"
                            ),
                        },
                    )

    mechanisms = assembler.MechanismProducerOutputs(
        normal_retest=normal_projection,
        normal_entry_boundary=normal_entry,
        false_break_reclaim=fbr,
        false_break_entry_boundary=fbr_entry,
        platform_reexpansion=platform_evidence,
        platform_entry_boundary=platform_entry,
        deep_takeover=deep_projection,
        deep_entry_boundary=deep_entry,
    )

    active: list[str] = []
    if normal_projection is not None:
        active.append(OpportunityMechanism.NORMAL_RETEST_CONTINUATION.value)
    if fbr is not None:
        active.append(OpportunityMechanism.FALSE_BREAK_RECLAIM.value)
    if platform_evidence is not None:
        active.append(OpportunityMechanism.PLATFORM_REEXPANSION.value)
    if (
        deep_preidentity is not None
        and deep_preidentity.state is EvidenceState.TRUE
        and deep_preidentity.facts is not None
        and unbound_deep_request is not None
    ):
        active.append(OpportunityMechanism.DEEP_STRUCTURE_TAKEOVER.value)

    d5_sidecars: dict[str, Any] = {}
    if fbr_rows:
        event = fbr_rows[0][0]
        d5_sidecars["false_break_reclaim"] = {
            "event": event,
            "correct_side_recovery": inp.recovery_by_candidate[
                event.candidate_id
            ],
        }
    if normal_active:
        d5_sidecars["normal_retest"] = normal_active[0][1].evidence

    return ActiveD4CompositionResultV1(
        mechanisms=mechanisms,
        active_mechanisms=tuple(active),
        local_control_regain_results=tuple(regain_results),
        d5_sidecars=d5_sidecars,
        deep_preidentity=deep_preidentity,
        unbound_deep_request=unbound_deep_request,
        fixed_adverse_updates=fixed_updates,
        provenance={
            "composer": "FULL_LIVE_ACTIVE_D4_MECHANISM_COMPOSER_V1",
            "primary_mechanism_selected_here": "false",
            "d4_frozen_precedence_retained": "true",
            "new_numeric_threshold": "false",
            "new_fixed_window": "false",
        },
    )


def invariants() -> Mapping[str, Any]:
    return {
        "primary_mechanism_selected_here": False,
        "d4_frozen_precedence_retained": True,
        "normal_fixed_adverse_rule_reused": True,
        "local_control_regain_rule_reused": True,
        "false_break_requires_typed_correct_side_recovery": True,
        "deep_role_authority_required": True,
        "deep_shallow_confirmation_cutoff_authority_required": True,
        "deep_preidentity_then_d4_same_event_required": True,
        "deep_self_authorized_market_event_identity": False,
        "new_numeric_threshold": False,
        "new_fixed_window": False,
        "quality_ranking_added": False,
        "trading_activated": False,
    }
