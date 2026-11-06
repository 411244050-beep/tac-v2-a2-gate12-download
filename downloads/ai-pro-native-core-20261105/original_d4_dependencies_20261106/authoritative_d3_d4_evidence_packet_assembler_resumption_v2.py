from __future__ import annotations

"""Authoritative D3/D4 evidence packet assembler resumption V2.

This module is orchestration / projection / transport only.

It consumes already-authoritative producer outputs from:
- repaired D3 multiplicity surface;
- frozen D2->B4/D4 projection producers;
- frozen D3/B5 role-state and D4 base-mechanism producers.

It does not create BoundaryContactZone/QBU/role/EntryBoundary/mechanism truth,
does not access any market source, and does not activate Forward Observation.
"""

from dataclasses import dataclass, field, fields, is_dataclass
from enum import Enum
from fractions import Fraction
from hashlib import sha256
import importlib
import json
from types import MappingProxyType
from typing import Any, Mapping

import nontrading_adapter_integration_v1 as frozen
import nontrading_adapter_d3_d4_schema_orchestration_rc1_conformance_repair_v1 as repaired
import authoritative_d3_b5_d4_base_runtime_producers_v1 as b5prod

from d2_to_b4_d4_causal_evidence_producers_v1 import EvidenceState, ProjectionResult
from strategy_rc1.d3_boundary_intelligence.types import EconomicBoundaryUnit
from strategy_rc1.d4_opportunity.eligibility import entry_boundary_view, market_eligibility
from strategy_rc1.d4_opportunity.mechanisms import (
    deep_structure_takeover_observation,
    false_break_reclaim_observation,
    normal_retest_observation,
    platform_reexpansion_observation,
    select_primary_observation,
    trend_establishment_watch_observation,
)


ASSEMBLER_ID = "AUTHORITATIVE_D3_D4_EVIDENCE_PACKET_ASSEMBLER_RESUMPTION_V2"
UPSTREAM_RUNTIME_PRODUCER_TERMINAL_BLOB = "32eee15c6dfc5c4b015ac84db20edce05de66360"
UPSTREAM_RUNTIME_PRODUCER_VERIFICATION_BLOB = "524ff36b668db9b96d410a00bbb136472bc71915"
PRIOR_ASSEMBLER_BLOCKER_BLOB = "ad336f068b1cd5ffa863773e2a15a2707a6c1c73"
PRIOR_ASSEMBLER_TERMINAL_BLOB = "d52750e67af9651e831b35600b40b5e2855824cc"


class PacketAssemblyBlock(RuntimeError):
    pass


class PacketAssemblyConflict(PacketAssemblyBlock):
    pass


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
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    raise TypeError(f"UNSUPPORTED_SERIALIZATION_TYPE:{type(value)!r}")


def _resolve(module: str, qualname: str) -> Any:
    obj: Any = importlib.import_module(module)
    for part in qualname.split("."):
        obj = getattr(obj, part)
    return obj


def _decode(value: Any) -> Any:
    if isinstance(value, list):
        return [_decode(x) for x in value]
    if not isinstance(value, dict):
        return value
    if "$fraction" in value:
        return Fraction(*value["$fraction"])
    if "$enum" in value:
        module, qualname, raw = value["$enum"]
        return _resolve(module, qualname)(raw)
    if "$tuple" in value:
        return tuple(_decode(x) for x in value["$tuple"])
    if "$list" in value:
        return [_decode(x) for x in value["$list"]]
    if "$map" in value:
        return {k: _decode(v) for k, v in value["$map"]}
    if "$dataclass" in value:
        module, qualname = value["$dataclass"]
        cls = _resolve(module, qualname)
        return cls(**{k: _decode(v) for k, v in value["fields"].items()})
    return {k: _decode(v) for k, v in value.items()}


def exact_json(value: Any) -> str:
    return json.dumps(_encode(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return sha256(exact_json(value).encode()).hexdigest()


@dataclass(frozen=True)
class D3SnapshotProjectionAuthority:
    snapshot_ref: str
    return_evidence: Any | None = None
    structural_acceptance: ProjectionResult | None = None
    correct_side_recovery: ProjectionResult | None = None
    source_evidence_refs: tuple[str, ...] = ()
    provenance: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class InitialPacketAuthority:
    candidate_updates: tuple[repaired.D3CandidateUpdateV1, ...] = ()
    snapshot_projections: tuple[D3SnapshotProjectionAuthority, ...] = ()


@dataclass(frozen=True)
class D4StaticAuthority:
    trend_episode_id: str
    direction: Any
    relation: Any
    trend: Any
    trend_position: Any
    detector_evidence_ids: tuple[str, ...]
    critical_information_known: Any
    termination: Any | None = None
    independence: Any | None = None
    new_event_evidence: Any | None = None
    lineage_evidence_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class MechanismProducerOutputs:
    normal_retest: b5prod.NormalRetestProjection | None = None
    normal_entry_boundary: b5prod.EntryBoundaryProjection | None = None
    false_break_reclaim: Any | None = None
    false_break_entry_boundary: b5prod.EntryBoundaryProjection | None = None
    platform_reexpansion: Any | None = None
    platform_entry_boundary: b5prod.EntryBoundaryProjection | None = None
    deep_takeover: b5prod.DeepTakeoverProjection | None = None
    deep_entry_boundary: b5prod.EntryBoundaryProjection | None = None
    trend_establishment_watch: b5prod.TrendWatchProjection | None = None


@dataclass(frozen=True)
class PostUpdate008Authority:
    information_cutoff: int
    update008_output: b5prod.Update008Output
    d4_static: D4StaticAuthority
    mechanisms: MechanismProducerOutputs
    existing_opportunity: Any | None = None
    provenance: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class PacketAssemblyResult:
    initial_packet: Any
    final_packet: Any
    selected_primary_mechanism: str | None
    selected_entry_boundary_unit_id: str | None
    update008_state: EvidenceState
    packet_digest: str
    provenance: Mapping[str, str]


def _projection_consumer(
    result: ProjectionResult | None,
    *,
    expected_producer: str,
    field_name: str,
) -> Any | None:
    if result is None:
        return None
    if result.producer != expected_producer:
        raise PacketAssemblyConflict(f"{field_name}:PRODUCER_ID_MISMATCH")
    if result.state is EvidenceState.UNKNOWN:
        raise PacketAssemblyBlock(f"{field_name}:UNKNOWN:{result.reason}")
    if result.state is EvidenceState.CONFLICT:
        raise PacketAssemblyConflict(f"{field_name}:CONFLICT:{result.reason}")
    if result.consumer_evidence is None:
        raise PacketAssemblyConflict(f"{field_name}:KNOWN_STATE_WITHOUT_CONSUMER_EVIDENCE")
    return result.consumer_evidence


def assemble_d3_packet(authority: InitialPacketAuthority) -> repaired.D3EvidencePacketRC1V1:
    candidate_rows: dict[str, repaired.D3CandidateUpdateV1] = {}
    for item in authority.candidate_updates:
        if not isinstance(item, repaired.D3CandidateUpdateV1):
            raise PacketAssemblyConflict("D3_CANDIDATE_UPDATE_SCHEMA")
        candidate_id = getattr(item.candidate, "candidate_id", None)
        if not isinstance(candidate_id, str) or not candidate_id:
            raise PacketAssemblyConflict("D3_CANDIDATE_ID_MISSING")
        if candidate_id in candidate_rows and candidate_rows[candidate_id] != item:
            raise PacketAssemblyConflict("D3_DUPLICATE_CANDIDATE_ID_CONFLICT")
        candidate_rows[candidate_id] = item

    snapshot_rows: dict[str, repaired.D3SnapshotEvidenceV1] = {}
    for row in authority.snapshot_projections:
        if not row.snapshot_ref:
            raise PacketAssemblyConflict("D3_SNAPSHOT_REF_MISSING")
        if row.snapshot_ref in snapshot_rows:
            raise PacketAssemblyConflict("D3_DUPLICATE_SNAPSHOT_REF")
        structural = _projection_consumer(
            row.structural_acceptance,
            expected_producer="B4_STRUCTURAL_ACCEPTANCE_D2_PROJECTION_V1",
            field_name=f"{row.snapshot_ref}:STRUCTURAL_ACCEPTANCE",
        )
        recovery = _projection_consumer(
            row.correct_side_recovery,
            expected_producer="B4_CORRECT_SIDE_RECOVERY_D2_PROJECTION_V1",
            field_name=f"{row.snapshot_ref}:CORRECT_SIDE_RECOVERY",
        )
        snapshot_rows[row.snapshot_ref] = repaired.D3SnapshotEvidenceV1(
            snapshot_ref=row.snapshot_ref,
            return_evidence=row.return_evidence,
            structural_acceptance=structural,
            correct_side_recovery=recovery,
        )

    return repaired.D3EvidencePacketRC1V1(
        candidate_updates={k: candidate_rows[k] for k in sorted(candidate_rows)},
        snapshot_evidence={k: snapshot_rows[k] for k in sorted(snapshot_rows)},
    )


def assemble_initial_cutoff_packet(authority: InitialPacketAuthority) -> Any:
    return frozen.CutoffEvidencePacket(d3=assemble_d3_packet(authority), d4=None)


def _entry_projection(
    projection: b5prod.EntryBoundaryProjection | None,
    *,
    mechanism: str,
    required: bool,
) -> b5prod.EntryBoundaryProjection | None:
    if projection is None:
        if required:
            raise PacketAssemblyBlock(f"{mechanism}:ENTRY_BOUNDARY_MISSING")
        return None
    if projection.state is EvidenceState.CONFLICT:
        raise PacketAssemblyConflict(f"{mechanism}:ENTRY_BOUNDARY_CONFLICT:{projection.reason}")
    if projection.state is EvidenceState.UNKNOWN:
        raise PacketAssemblyBlock(f"{mechanism}:ENTRY_BOUNDARY_UNKNOWN:{projection.reason}")
    if projection.state is not EvidenceState.TRUE or projection.unit is None or projection.view is None:
        raise PacketAssemblyBlock(f"{mechanism}:ENTRY_BOUNDARY_NOT_AUTHORITATIVE")
    return projection


def _normal_projection(
    projection: b5prod.NormalRetestProjection | None,
) -> Any | None:
    if projection is None:
        return None
    if projection.state is EvidenceState.CONFLICT:
        raise PacketAssemblyConflict(f"NORMAL_RETEST:CONFLICT:{projection.reason}")
    if projection.state is EvidenceState.UNKNOWN:
        raise PacketAssemblyBlock(f"NORMAL_RETEST:UNKNOWN:{projection.reason}")
    if projection.evidence is None:
        raise PacketAssemblyConflict("NORMAL_RETEST:KNOWN_STATE_WITHOUT_EVIDENCE")
    return projection.evidence


def _deep_projection(
    projection: b5prod.DeepTakeoverProjection | None,
) -> Any | None:
    if projection is None:
        return None
    if projection.state is EvidenceState.CONFLICT:
        raise PacketAssemblyConflict(f"DEEP_TAKEOVER:CONFLICT:{projection.reason}")
    if projection.state is EvidenceState.UNKNOWN:
        raise PacketAssemblyBlock(f"DEEP_TAKEOVER:UNKNOWN:{projection.reason}")
    if projection.evidence is None:
        raise PacketAssemblyConflict("DEEP_TAKEOVER:KNOWN_STATE_WITHOUT_EVIDENCE")
    return projection.evidence


def _watch_projection(
    projection: b5prod.TrendWatchProjection | None,
) -> Any | None:
    if projection is None:
        return None
    if projection.state is EvidenceState.CONFLICT:
        raise PacketAssemblyConflict(f"TREND_WATCH:CONFLICT:{projection.reason}")
    if projection.state is EvidenceState.UNKNOWN:
        raise PacketAssemblyBlock(f"TREND_WATCH:UNKNOWN:{projection.reason}")
    if projection.evidence is None:
        raise PacketAssemblyConflict("TREND_WATCH:KNOWN_STATE_WITHOUT_EVIDENCE")
    return projection.evidence


def _market_gate(static: D4StaticAuthority, *, watch_only: bool) -> Any:
    return market_eligibility(
        static.trend,
        opportunity_direction=static.direction,
        critical_information_known=static.critical_information_known,
        watch_only=watch_only,
    ).result


def _preview_observations(
    post: PostUpdate008Authority,
    *,
    normal_evidence: Any | None,
    false_break_evidence: Any | None,
    platform_evidence: Any | None,
    deep_evidence: Any | None,
    watch_evidence: Any | None,
    normal_entry: b5prod.EntryBoundaryProjection | None,
    false_entry: b5prod.EntryBoundaryProjection | None,
    platform_entry: b5prod.EntryBoundaryProjection | None,
    deep_entry: b5prod.EntryBoundaryProjection | None,
) -> tuple[tuple[Any, ...], dict[Any, b5prod.EntryBoundaryProjection | None]]:
    static = post.d4_static
    observations: list[Any] = []
    boundary_by_mechanism: dict[Any, b5prod.EntryBoundaryProjection | None] = {}

    if normal_evidence is not None:
        assert normal_entry is not None
        obs = normal_retest_observation(
            normal_evidence,
            direction=static.direction,
            trend_episode_id=static.trend_episode_id,
            information_cutoff=post.information_cutoff,
            market_gate=_market_gate(static, watch_only=False),
            entry_boundary=normal_entry.view,
        )
        observations.append(obs)
        boundary_by_mechanism[obs.mechanism] = normal_entry

    if false_break_evidence is not None:
        assert false_entry is not None
        obs = false_break_reclaim_observation(
            false_break_evidence,
            direction=static.direction,
            trend_episode_id=static.trend_episode_id,
            information_cutoff=post.information_cutoff,
            market_gate=_market_gate(static, watch_only=False),
            entry_boundary=false_entry.view,
        )
        observations.append(obs)
        boundary_by_mechanism[obs.mechanism] = false_entry

    if platform_evidence is not None:
        assert platform_entry is not None
        theta_progress = getattr(getattr(platform_evidence, "provenance", {}), "theta_progress", None)
        # Frozen consumer owns theta_progress.  The exact authoritative value comes
        # from the current parameter snapshot used by the RC1 adapter, not provenance.
        params = frozen.frozen_d4_parameters(frozen.current_partial_parameter_snapshot())
        obs = platform_reexpansion_observation(
            platform_evidence,
            direction=static.direction,
            trend_episode_id=static.trend_episode_id,
            information_cutoff=post.information_cutoff,
            market_gate=_market_gate(static, watch_only=False),
            entry_boundary=platform_entry.view,
            theta_progress=params.theta_progress,
        )
        observations.append(obs)
        boundary_by_mechanism[obs.mechanism] = platform_entry

    if deep_evidence is not None:
        assert deep_entry is not None
        obs = deep_structure_takeover_observation(
            deep_evidence,
            direction=static.direction,
            trend_episode_id=static.trend_episode_id,
            information_cutoff=post.information_cutoff,
            market_gate=_market_gate(static, watch_only=False),
            entry_boundary=deep_entry.view,
        )
        observations.append(obs)
        boundary_by_mechanism[obs.mechanism] = deep_entry

    if watch_evidence is not None:
        obs = trend_establishment_watch_observation(watch_evidence)
        observations.append(obs)
        boundary_by_mechanism[obs.mechanism] = None

    return tuple(observations), boundary_by_mechanism


def _preserved_existing_boundary(
    post: PostUpdate008Authority,
    episodes: Mapping[str, Any],
) -> EconomicBoundaryUnit | None:
    existing = post.existing_opportunity
    if existing is None:
        return None
    unit_id = getattr(existing, "entry_boundary_unit_id", None)
    if not unit_id:
        return None
    matches = [u for u in post.update008_output.units if u.unit_id == unit_id]
    if len(matches) > 1:
        raise PacketAssemblyConflict("EXISTING_ENTRY_BOUNDARY_UNIT_ID_NONUNIQUE")
    if not matches:
        return None
    unit = matches[0]
    view = entry_boundary_view(
        unit,
        episodes,
        target_trend_episode_id=post.d4_static.trend_episode_id,
        target_direction=post.d4_static.direction,
        information_cutoff=post.information_cutoff,
    )
    return unit if view is not None and view.valid_active else None


def _actual_primary_with_selected_boundary(
    post: PostUpdate008Authority,
    selected_unit: EconomicBoundaryUnit | None,
    *,
    normal_evidence: Any | None,
    false_break_evidence: Any | None,
    platform_evidence: Any | None,
    deep_evidence: Any | None,
    watch_evidence: Any | None,
) -> Any | None:
    static = post.d4_static
    episodes = {ep.anchor_episode_id: ep for ep in post.update008_output.episodes}
    selected_view = entry_boundary_view(
        selected_unit,
        episodes,
        target_trend_episode_id=static.trend_episode_id,
        target_direction=static.direction,
        information_cutoff=post.information_cutoff,
    )
    observations: list[Any] = []
    market_gate = _market_gate(static, watch_only=False)
    if normal_evidence is not None:
        observations.append(normal_retest_observation(
            normal_evidence, direction=static.direction, trend_episode_id=static.trend_episode_id,
            information_cutoff=post.information_cutoff, market_gate=market_gate, entry_boundary=selected_view,
        ))
    if false_break_evidence is not None:
        observations.append(false_break_reclaim_observation(
            false_break_evidence, direction=static.direction, trend_episode_id=static.trend_episode_id,
            information_cutoff=post.information_cutoff, market_gate=market_gate, entry_boundary=selected_view,
        ))
    if platform_evidence is not None:
        params = frozen.frozen_d4_parameters(frozen.current_partial_parameter_snapshot())
        observations.append(platform_reexpansion_observation(
            platform_evidence, direction=static.direction, trend_episode_id=static.trend_episode_id,
            information_cutoff=post.information_cutoff, market_gate=market_gate,
            entry_boundary=selected_view, theta_progress=params.theta_progress,
        ))
    if deep_evidence is not None:
        observations.append(deep_structure_takeover_observation(
            deep_evidence, direction=static.direction, trend_episode_id=static.trend_episode_id,
            information_cutoff=post.information_cutoff, market_gate=market_gate, entry_boundary=selected_view,
        ))
    if watch_evidence is not None:
        observations.append(trend_establishment_watch_observation(watch_evidence))
    return select_primary_observation(tuple(observations))


def assemble_d4_packet(post: PostUpdate008Authority) -> tuple[Any, str | None, str | None]:
    output = post.update008_output
    static = post.d4_static

    if output.state is EvidenceState.CONFLICT:
        raise PacketAssemblyConflict("UPDATE008_OUTPUT_CONFLICT")
    if static.trend_episode_id != getattr(static.trend, "episode_id", None):
        raise PacketAssemblyConflict("D4_STATIC_TREND_EPISODE_MISMATCH")
    if not static.lineage_evidence_refs:
        raise PacketAssemblyBlock("D4_LINEAGE_EVIDENCE_REFS_REQUIRED")
    relation_value = getattr(static.relation, "value", str(static.relation))
    if relation_value in ("UNKNOWN", "CONFLICT"):
        raise PacketAssemblyBlock("D4_MARKET_EVENT_RELATION_BLOCKED")

    m = post.mechanisms
    normal_evidence = _normal_projection(m.normal_retest)
    deep_evidence = _deep_projection(m.deep_takeover)
    watch_evidence = _watch_projection(m.trend_establishment_watch)
    false_break_evidence = m.false_break_reclaim
    platform_evidence = m.platform_reexpansion

    normal_entry = _entry_projection(m.normal_entry_boundary, mechanism="NORMAL_RETEST_CONTINUATION", required=normal_evidence is not None)
    false_entry = _entry_projection(m.false_break_entry_boundary, mechanism="FALSE_BREAK_RECLAIM", required=false_break_evidence is not None)
    platform_entry = _entry_projection(m.platform_entry_boundary, mechanism="PLATFORM_REEXPANSION", required=platform_evidence is not None)
    deep_entry = _entry_projection(m.deep_entry_boundary, mechanism="DEEP_STRUCTURE_TAKEOVER", required=deep_evidence is not None)

    preview, boundary_by_mechanism = _preview_observations(
        post,
        normal_evidence=normal_evidence,
        false_break_evidence=false_break_evidence,
        platform_evidence=platform_evidence,
        deep_evidence=deep_evidence,
        watch_evidence=watch_evidence,
        normal_entry=normal_entry,
        false_entry=false_entry,
        platform_entry=platform_entry,
        deep_entry=deep_entry,
    )
    primary = select_primary_observation(preview)
    episodes = {ep.anchor_episode_id: ep for ep in output.episodes}

    if primary is None:
        selected_unit = _preserved_existing_boundary(post, episodes)
        selected_mechanism = None
    else:
        selected_mechanism = primary.mechanism.value
        selected_projection = boundary_by_mechanism.get(primary.mechanism)
        selected_unit = None if selected_projection is None else selected_projection.unit

    actual_primary = _actual_primary_with_selected_boundary(
        post,
        selected_unit,
        normal_evidence=normal_evidence,
        false_break_evidence=false_break_evidence,
        platform_evidence=platform_evidence,
        deep_evidence=deep_evidence,
        watch_evidence=watch_evidence,
    )
    actual_name = None if actual_primary is None else actual_primary.mechanism.value
    if actual_name != selected_mechanism:
        raise PacketAssemblyConflict(
            f"ENTRY_BOUNDARY_PRIMARY_ROUND_TRIP_MISMATCH:{selected_mechanism}:{actual_name}"
        )

    termination = static.termination if static.termination is not None else frozen.OpportunityTerminationEvidence()
    packet = frozen.D4EvidencePacket(
        trend_episode_id=static.trend_episode_id,
        direction=static.direction,
        relation=static.relation,
        trend=static.trend,
        trend_position=static.trend_position,
        detector_evidence_ids=tuple(static.detector_evidence_ids),
        critical_information_known=static.critical_information_known,
        entry_boundary_unit=selected_unit,
        anchor_episodes=episodes,
        termination=termination,
        independence=static.independence,
        new_event_evidence=static.new_event_evidence,
        lineage_evidence_refs=tuple(static.lineage_evidence_refs),
        normal_retest=normal_evidence,
        false_break_reclaim=false_break_evidence,
        platform_reexpansion=platform_evidence,
        deep_takeover=deep_evidence,
        trend_establishment_watch=watch_evidence,
    )
    return packet, selected_mechanism, None if selected_unit is None else selected_unit.unit_id


class AuthoritativeD3D4PacketAssemblerV2:
    """Atomic staged assembler.

    begin() is pure and emits only the repaired D3 packet.
    complete() consumes post-UPDATE-008 authoritative outputs and atomically records a
    final packet digest.  Failed completion mutates no assembler transaction state.
    """

    STATE_SCHEMA = "AUTHORITATIVE_D3_D4_PACKET_ASSEMBLER_V2_STATE"

    def __init__(self) -> None:
        self._records: dict[str, tuple[str, str]] = {}

    def begin(self, authority: InitialPacketAuthority) -> Any:
        return assemble_initial_cutoff_packet(authority)

    def complete(
        self,
        tx_id: str,
        initial: InitialPacketAuthority,
        post: PostUpdate008Authority,
    ) -> PacketAssemblyResult:
        if not tx_id:
            raise PacketAssemblyBlock("TX_ID_REQUIRED")
        input_digest = digest((initial, post))
        prior = self._records.get(tx_id)
        if prior is not None and prior[0] != input_digest:
            raise PacketAssemblyConflict("SAME_TX_DIFFERENT_INPUT")

        initial_packet = assemble_initial_cutoff_packet(initial)
        d4, selected_mechanism, selected_unit_id = assemble_d4_packet(post)
        final_packet = frozen.CutoffEvidencePacket(d3=initial_packet.d3, d4=d4)
        result = PacketAssemblyResult(
            initial_packet=initial_packet,
            final_packet=final_packet,
            selected_primary_mechanism=selected_mechanism,
            selected_entry_boundary_unit_id=selected_unit_id,
            update008_state=post.update008_output.state,
            packet_digest=digest(final_packet),
            provenance={
                "assembler_id": ASSEMBLER_ID,
                "f9_initial_packet_visible_through": "UPDATE-008",
                "f9_final_packet_visible_from": "UPDATE-011",
                "update008_to_update002_backflow": "false",
                "schema_modified": "false",
            },
        )
        result_digest = digest(result)
        if prior is not None:
            if prior[1] != result_digest:
                raise PacketAssemblyConflict("RESTART_OR_REPLAY_RESULT_MISMATCH")
            return result

        self._records[tx_id] = (input_digest, result_digest)
        return result

    def export_state(self) -> Mapping[str, Any]:
        return MappingProxyType({
            "schema": self.STATE_SCHEMA,
            "records": {k: [v[0], v[1]] for k, v in sorted(self._records.items())},
            "governance": {
                "forward_observation": "NOT_ACTIVE",
                "test": "NOT_AUTHORIZED",
                "trading": "FORBIDDEN",
                "packet_schema_modified": False,
            },
        })

    @classmethod
    def restore_state(cls, state: Mapping[str, Any]) -> "AuthoritativeD3D4PacketAssemblerV2":
        if state.get("schema") != cls.STATE_SCHEMA:
            raise PacketAssemblyConflict("ASSEMBLER_STATE_SCHEMA_MISMATCH")
        gov = state.get("governance") or {}
        if (
            gov.get("forward_observation") != "NOT_ACTIVE"
            or gov.get("test") != "NOT_AUTHORIZED"
            or gov.get("trading") != "FORBIDDEN"
            or gov.get("packet_schema_modified") is not False
        ):
            raise PacketAssemblyConflict("ASSEMBLER_STATE_GOVERNANCE_MISMATCH")
        out = cls()
        raw = state.get("records") or {}
        out._records = {str(k): (str(v[0]), str(v[1])) for k, v in raw.items()}
        return out


def direct_d4_consumer_input_from_packet(packet: Any, *, information_cutoff: int, existing_opportunity: Any | None = None) -> Any:
    """Mechanical mirror of frozen adapter _u011 D4CutoffInput construction."""
    if not isinstance(packet, frozen.D4EvidencePacket):
        raise PacketAssemblyConflict("D4_PACKET_SCHEMA")
    market_event_id = "SYNTHETIC_DIRECT_CONSUMER_EVENT"
    return frozen.D4CutoffInput(
        information_cutoff=information_cutoff,
        trend=packet.trend,
        trend_position=packet.trend_position,
        opportunity_direction=packet.direction,
        market_event_id=market_event_id,
        detector_evidence_ids=packet.detector_evidence_ids,
        critical_information_known=packet.critical_information_known,
        entry_boundary_unit=packet.entry_boundary_unit,
        anchor_episodes=packet.anchor_episodes,
        parameters=frozen.frozen_d4_parameters(frozen.current_partial_parameter_snapshot()),
        existing_opportunity=existing_opportunity,
        independence=packet.independence,
        termination=packet.termination,
        normal_retest=packet.normal_retest,
        false_break_reclaim=packet.false_break_reclaim,
        platform_reexpansion=packet.platform_reexpansion,
        deep_takeover=packet.deep_takeover,
        trend_establishment_watch=packet.trend_establishment_watch,
    )
