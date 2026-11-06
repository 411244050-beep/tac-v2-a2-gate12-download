from __future__ import annotations

"""RC1-conformance repair for the nontrading D3/D4 evidence adapter surface.

This module is deliberately an adapter/orchestration repair, not a scientific producer.

D3:
- every concurrently newly available UPDATE-008 candidate is represented and consumed;
- no family, score, distance, lexical-family, rotation, winner, or drop rule exists;
- all causally available pre-bar boundary snapshot refs are consumed by UPDATE-002/007;
- per-snapshot supplied evidence can be carried without selecting one snapshot;
- singleton legacy behavior remains exact.

D4:
- the frozen UPDATE-011 implementation is inherited byte-for-code without override;
- no D4EvidencePacket constructor or D2->B4/D4 evidence producer is introduced.
"""

from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from typing import Any

import nontrading_adapter_integration_v1 as frozen


REPAIR_SCHEMA = "TAC_NONTRADING_ADAPTER_D3_D4_RC1_CONFORMANCE_REPAIR_V1"


@dataclass(frozen=True)
class D3CandidateUpdateV1:
    candidate: Any
    target_trend_active: bool = True
    candidate_terminally_invalidated: bool = False


@dataclass(frozen=True)
class D3SnapshotEvidenceV1:
    snapshot_ref: str
    return_evidence: Any | None = None
    structural_acceptance: Any | None = None
    correct_side_recovery: Any | None = None


@dataclass(frozen=True)
class D3EvidencePacketRC1V1:
    """Lossless repaired D3 surface.

    Mapping keys are identities, not priorities. Frozen canonical mapping serialization
    makes evidence identity independent of insertion order while orchestration consumes
    every represented item.

    The singular snapshot/evidence fields are retained only for exact legacy lifting.
    When more than one snapshot is causally active, unscoped legacy evidence is blocked
    rather than projected across candidates.
    """

    candidate_updates: Mapping[str, D3CandidateUpdateV1] = field(default_factory=dict)
    snapshot_evidence: Mapping[str, D3SnapshotEvidenceV1] = field(default_factory=dict)

    # Legacy singleton compatibility surface.
    snapshot_ref: str | None = None
    return_evidence: Any | None = None
    structural_acceptance: Any | None = None
    correct_side_recovery: Any | None = None


def _candidate_updates(packet: D3EvidencePacketRC1V1) -> tuple[D3CandidateUpdateV1, ...]:
    if not isinstance(packet, D3EvidencePacketRC1V1):
        raise frozen.IntegrationBlock("RC1_D3_PACKET_SCHEMA")
    if not isinstance(packet.candidate_updates, Mapping):
        raise frozen.IntegrationBlock("RC1_D3_CANDIDATE_UPDATES_NOT_MAPPING")

    rows: list[D3CandidateUpdateV1] = []
    for key, item in packet.candidate_updates.items():
        if not isinstance(key, str) or not key:
            raise frozen.IntegrationBlock("RC1_D3_CANDIDATE_KEY_INVALID")
        if not isinstance(item, D3CandidateUpdateV1):
            raise frozen.IntegrationBlock("RC1_D3_CANDIDATE_UPDATE_SCHEMA")
        candidate_id = getattr(item.candidate, "candidate_id", None)
        if not isinstance(candidate_id, str) or not candidate_id:
            raise frozen.IntegrationBlock("RC1_D3_CANDIDATE_ID_MISSING")
        if key != candidate_id:
            raise frozen.IntegrationBlock("RC1_D3_CANDIDATE_KEY_ID_MISMATCH")
        rows.append(item)
    return tuple(rows)


def _snapshot_evidence(packet: D3EvidencePacketRC1V1) -> dict[str, D3SnapshotEvidenceV1]:
    if not isinstance(packet.snapshot_evidence, Mapping):
        raise frozen.IntegrationBlock("RC1_D3_SNAPSHOT_EVIDENCE_NOT_MAPPING")

    out: dict[str, D3SnapshotEvidenceV1] = {}
    for key, item in packet.snapshot_evidence.items():
        if not isinstance(key, str) or not key:
            raise frozen.IntegrationBlock("RC1_D3_SNAPSHOT_KEY_INVALID")
        if not isinstance(item, D3SnapshotEvidenceV1):
            raise frozen.IntegrationBlock("RC1_D3_SNAPSHOT_EVIDENCE_SCHEMA")
        if item.snapshot_ref != key:
            raise frozen.IntegrationBlock("RC1_D3_SNAPSHOT_KEY_REF_MISMATCH")
        out[key] = item

    if packet.snapshot_ref is not None:
        if not isinstance(packet.snapshot_ref, str) or not packet.snapshot_ref:
            raise frozen.IntegrationBlock("RC1_D3_LEGACY_SNAPSHOT_REF_INVALID")
        if packet.snapshot_ref in out:
            raise frozen.IntegrationBlock("RC1_D3_DUPLICATE_SNAPSHOT_EVIDENCE_SCOPE")
    return out


def canonicalize_cutoff_packet(packet: frozen.CutoffEvidencePacket) -> frozen.CutoffEvidencePacket:
    """Validate/copy the repaired D3 mappings without creating any processing priority."""
    if not isinstance(packet, frozen.CutoffEvidencePacket):
        raise frozen.IntegrationBlock("RC1_CUTOFF_PACKET_SCHEMA")
    if packet.d3 is None:
        return packet
    if not isinstance(packet.d3, D3EvidencePacketRC1V1):
        raise frozen.IntegrationBlock("RC1_D3_PACKET_SCHEMA")

    _candidate_updates(packet.d3)
    _snapshot_evidence(packet.d3)
    d3 = replace(
        packet.d3,
        candidate_updates=dict(packet.d3.candidate_updates),
        snapshot_evidence=dict(packet.d3.snapshot_evidence),
    )
    return replace(packet, d3=d3)


def lift_legacy_d3_packet(packet: frozen.D3EvidencePacket) -> D3EvidencePacketRC1V1:
    """Exact singleton compatibility lift. No selector is introduced."""
    if not isinstance(packet, frozen.D3EvidencePacket):
        raise frozen.IntegrationBlock("RC1_LEGACY_D3_PACKET_SCHEMA")

    updates: dict[str, D3CandidateUpdateV1] = {}
    if packet.candidate is not None:
        candidate_id = getattr(packet.candidate, "candidate_id", None)
        if not isinstance(candidate_id, str) or not candidate_id:
            raise frozen.IntegrationBlock("RC1_D3_CANDIDATE_ID_MISSING")
        updates[candidate_id] = D3CandidateUpdateV1(
            candidate=packet.candidate,
            target_trend_active=packet.target_trend_active,
            candidate_terminally_invalidated=packet.candidate_terminally_invalidated,
        )

    return D3EvidencePacketRC1V1(
        candidate_updates=updates,
        snapshot_ref=packet.snapshot_ref,
        return_evidence=packet.return_evidence,
        structural_acceptance=packet.structural_acceptance,
        correct_side_recovery=packet.correct_side_recovery,
    )


def _legacy_projection(packet: frozen.CutoffEvidencePacket) -> frozen.CutoffEvidencePacket | None:
    """Return an exact old-schema projection only when the repaired packet is singleton-compatible."""
    p = packet.d3
    if not isinstance(p, D3EvidencePacketRC1V1):
        return None
    if len(p.candidate_updates) > 1 or p.snapshot_evidence:
        return None

    updates = _candidate_updates(p)
    item = updates[0] if updates else None
    legacy = frozen.D3EvidencePacket(
        candidate=None if item is None else item.candidate,
        target_trend_active=True if item is None else item.target_trend_active,
        candidate_terminally_invalidated=False
        if item is None
        else item.candidate_terminally_invalidated,
        snapshot_ref=p.snapshot_ref,
        return_evidence=p.return_evidence,
        structural_acceptance=p.structural_acceptance,
        correct_side_recovery=p.correct_side_recovery,
    )
    return replace(packet, d3=legacy)


class AdapterIntegrationRuntimeRC1ConformanceV1(frozen.AdapterIntegrationRuntime):
    """Frozen runtime with multiplicity repaired for D3 UPDATE-002/007/008 only."""

    def set_evidence(
        self, symbol: str, open_time: int, packet: frozen.CutoffEvidencePacket
    ) -> None:
        super().set_evidence(symbol, open_time, canonicalize_cutoff_packet(packet))

    @staticmethod
    def _evidence_digest(packet: frozen.CutoffEvidencePacket) -> str:
        legacy = _legacy_projection(packet)
        return frozen.digest(packet if legacy is None else legacy)

    def _make_adapter(self, step):
        # Exact frozen dispatch/idempotence logic, changing only evidence digest projection.
        def adapter(ctx):
            if ctx.step is not step:
                raise frozen.IntegrationBlock("ADAPTER_STEP_CONTEXT_MISMATCH")
            st = self._state(ctx.symbol_input.symbol)
            ev_digest = self._evidence_digest(self._packet(ctx))
            prior_digest = st.processed_tx_digests.get(ctx.transaction_id)
            if prior_digest is not None and prior_digest != ev_digest:
                raise frozen.IntegrationBlock("DUPLICATE_TX_EVIDENCE_MISMATCH")
            st.processed_tx_digests.setdefault(ctx.transaction_id, ev_digest)
            by_step = st.completed_stage_results.setdefault(ctx.transaction_id, {})
            if step.value in by_step:
                return by_step[step.value]
            self.owner_execution_ledger.append(
                (ctx.transaction_id, step.value, frozen.EXPECTED_OWNER[step].value)
            )
            result = getattr(self, f"_u{int(step.value[-3:]):03d}")(ctx)
            by_step[step.value] = result
            return result

        return adapter

    @classmethod
    def restore_state(cls, payload):
        base = frozen.AdapterIntegrationRuntime.restore_state(payload)
        out = cls()
        out.__dict__.update(base.__dict__)
        return out

    def _effective_snapshots(self, ctx, obj, packet: D3EvidencePacketRC1V1):
        annotations = _snapshot_evidence(packet)

        prebar = getattr(ctx.symbol_input, "prebar_snapshot", None)
        prebar_refs = () if prebar is None else tuple(prebar.boundary_snapshot_refs)
        if len(set(prebar_refs)) != len(prebar_refs):
            raise frozen.IntegrationBlock("RC1_D3_DUPLICATE_PREBAR_SNAPSHOT_REF")

        refs: list[str] = list(prebar_refs)
        if packet.snapshot_ref is not None and packet.snapshot_ref not in refs:
            refs.append(packet.snapshot_ref)
        for ref in annotations:
            if ref not in refs:
                refs.append(ref)

        if not refs:
            return ()

        view = obj.update_000_pre_bar_view(ctx.symbol_input.observer_bar.open_time)
        by_id = {snap.snapshot_id: snap for snap in view.snapshots}
        snapshots = []
        for ref in refs:
            snap = by_id.get(ref)
            if snap is None:
                raise frozen.RefBlock("D3_PREBAR_SNAPSHOT_REF_NOT_CAUSALLY_AVAILABLE")
            snapshots.append(snap)
        return tuple(snapshots)

    @staticmethod
    def _legacy_or_scoped_evidence(
        packet: D3EvidencePacketRC1V1,
        snapshots,
    ) -> dict[str, D3SnapshotEvidenceV1]:
        scoped = _snapshot_evidence(packet)

        legacy_has_evidence = any(
            x is not None
            for x in (
                packet.return_evidence,
                packet.structural_acceptance,
                packet.correct_side_recovery,
            )
        )
        if packet.snapshot_ref is not None:
            scoped[packet.snapshot_ref] = D3SnapshotEvidenceV1(
                snapshot_ref=packet.snapshot_ref,
                return_evidence=packet.return_evidence,
                structural_acceptance=packet.structural_acceptance,
                correct_side_recovery=packet.correct_side_recovery,
            )
        elif legacy_has_evidence:
            if len(snapshots) != 1:
                raise frozen.IntegrationBlock("RC1_D3_UNSCOPED_MULTI_SNAPSHOT_EVIDENCE")
            scoped[snapshots[0].snapshot_id] = D3SnapshotEvidenceV1(
                snapshot_ref=snapshots[0].snapshot_id,
                return_evidence=packet.return_evidence,
                structural_acceptance=packet.structural_acceptance,
                correct_side_recovery=packet.correct_side_recovery,
            )
        return scoped

    def _u002(self, ctx):
        p = self._packet(ctx).d3
        if p is None:
            return frozen.StageResult.make(
                owner=frozen.DomainOwner.D3_BOUNDARY_INTELLIGENCE,
                state=frozen.StageState.NA,
                reason="NO_D3_EVIDENCE_PACKET",
                payload=None,
                information_cutoff=ctx.information_cutoff,
            )
        if not isinstance(p, D3EvidencePacketRC1V1):
            raise frozen.IntegrationBlock("RC1_D3_PACKET_SCHEMA")

        obj = self._d3_rebuild(ctx.symbol_input.symbol)
        snapshots = self._effective_snapshots(ctx, obj, p)
        if not snapshots:
            return frozen.StageResult.make(
                owner=frozen.DomainOwner.D3_BOUNDARY_INTELLIGENCE,
                state=frozen.StageState.NA,
                reason="NO_CAUSAL_PREBAR_BOUNDARY_SNAPSHOT",
                payload=None,
                information_cutoff=ctx.information_cutoff,
            )

        bar = ctx.symbol_input.observer_bar
        geometries = []
        for snap in snapshots:
            geom = obj.update_002_capture_geometry(
                bar=bar,
                information_cutoff=ctx.information_cutoff or bar.close_time,
                snapshot=snap,
            )
            geometries.append((snap.snapshot_id, geom))

        cache = self._cache(ctx.transaction_id)
        if len(geometries) == 1:
            cache.d3_geometry = geometries[0][1]
            payload = geometries[0][1]
            reason = "D3_GEOMETRY_REFERENCE"
        else:
            cache.d3_geometry = tuple(geometries)
            payload = tuple(geometries)
            reason = "D3_GEOMETRY_REFERENCE_RC1_MULTIPLICITY"

        return frozen.StageResult.make(
            owner=frozen.DomainOwner.D3_BOUNDARY_INTELLIGENCE,
            reason=reason,
            payload=payload,
            information_cutoff=ctx.information_cutoff,
        )

    def _u007(self, ctx):
        p = self._packet(ctx).d3
        cache = self._cache(ctx.transaction_id)
        if p is None or cache.d3_geometry is None:
            return frozen.StageResult.make(
                owner=frozen.DomainOwner.D3_BOUNDARY_INTELLIGENCE,
                state=frozen.StageState.NA,
                reason="NO_D3_GEOMETRY_FOR_INTERACTION",
                payload=None,
                information_cutoff=ctx.information_cutoff,
            )
        if not isinstance(p, D3EvidencePacketRC1V1):
            raise frozen.IntegrationBlock("RC1_D3_PACKET_SCHEMA")

        obj = self._d3_rebuild(ctx.symbol_input.symbol)
        snapshots = self._effective_snapshots(ctx, obj, p)
        evidence = self._legacy_or_scoped_evidence(p, snapshots)

        if len(snapshots) == 1:
            geometry_by_ref = {snapshots[0].snapshot_id: cache.d3_geometry}
        else:
            if not isinstance(cache.d3_geometry, tuple):
                raise frozen.IntegrationBlock("RC1_D3_MULTI_GEOMETRY_CACHE_SCHEMA")
            geometry_by_ref = dict(cache.d3_geometry)
            if set(geometry_by_ref) != {x.snapshot_id for x in snapshots}:
                raise frozen.IntegrationBlock("RC1_D3_MULTI_GEOMETRY_SNAPSHOT_MISMATCH")

        events = []
        refs = []
        for snap in snapshots:
            scoped = evidence.get(snap.snapshot_id)
            kwargs = {
                "snapshot": snap,
                "geometry": geometry_by_ref[snap.snapshot_id],
                "return_evidence": None if scoped is None else scoped.return_evidence,
                "structural_acceptance": None
                if scoped is None
                else scoped.structural_acceptance,
                "correct_side_recovery": None
                if scoped is None
                else scoped.correct_side_recovery,
            }
            ev = obj.update_007_interaction_break(**kwargs)
            self._state(ctx.symbol_input.symbol).d3_replay.append(
                ("update_007_interaction_break", kwargs)
            )
            ref = self.refs.register(
                "InteractionEvent", ev, ctx.information_cutoff or 0
            )
            events.append((snap.snapshot_id, ev))
            refs.append(ref)

        if len(events) == 1:
            cache.d3_event = events[0][1]
            payload = events[0][1]
            reason = "D3_INTERACTION_BREAK_REFERENCE"
        else:
            cache.d3_event = tuple(events)
            payload = tuple(events)
            reason = "D3_INTERACTION_BREAK_REFERENCE_RC1_MULTIPLICITY"

        return frozen.StageResult.make(
            owner=frozen.DomainOwner.D3_BOUNDARY_INTELLIGENCE,
            reason=reason,
            payload=payload,
            information_cutoff=ctx.information_cutoff,
            next_interaction_control_refs=tuple(refs),
        )

    def _u008(self, ctx):
        p = self._packet(ctx).d3
        if p is None:
            return frozen.StageResult.make(
                owner=frozen.DomainOwner.D3_BOUNDARY_INTELLIGENCE,
                state=frozen.StageState.NA,
                reason="NO_D3_CANDIDATE_UPDATE",
                payload=None,
                information_cutoff=ctx.information_cutoff,
            )
        if not isinstance(p, D3EvidencePacketRC1V1):
            raise frozen.IntegrationBlock("RC1_D3_PACKET_SCHEMA")

        updates = _candidate_updates(p)
        if not updates:
            return frozen.StageResult.make(
                owner=frozen.DomainOwner.D3_BOUNDARY_INTELLIGENCE,
                state=frozen.StageState.NA,
                reason="NO_D3_CANDIDATE_UPDATE",
                payload=None,
                information_cutoff=ctx.information_cutoff,
            )

        obj = self._d3_rebuild(ctx.symbol_input.symbol)
        items = []
        refs = []
        cutoff = ctx.information_cutoff or 0

        for item in updates:
            candidate = item.candidate
            snap = obj.update_008_register_candidate(candidate)
            self._state(ctx.symbol_input.symbol).d3_replay.append(
                ("update_008_register_candidate", {"candidate": candidate})
            )

            ep = obj.update_008_anchor_lifecycle(
                candidate=candidate,
                target_trend_active=item.target_trend_active,
                candidate_terminally_invalidated=item.candidate_terminally_invalidated,
                cutoff=cutoff,
            )
            self._state(ctx.symbol_input.symbol).d3_replay.append(
                (
                    "update_008_anchor_lifecycle",
                    {
                        "candidate": candidate,
                        "target_trend_active": item.target_trend_active,
                        "candidate_terminally_invalidated": item.candidate_terminally_invalidated,
                        "cutoff": cutoff,
                    },
                )
            )

            if snap is not None:
                refs.append(snap.snapshot_id)
                self.refs.register("CausalBoundarySnapshot", snap, cutoff)
            if ep is not None:
                self.refs.register("AnchorEpisode", ep, cutoff)
            items.append((candidate.candidate_id, snap, ep))

        if len(items) == 1:
            self._cache(ctx.transaction_id).d3_episode = items[0][2]
            payload = {"snapshot": items[0][1], "episode": items[0][2]}
            reason = "D3_ANCHOR_LIFECYCLE_REFERENCE"
        else:
            self._cache(ctx.transaction_id).d3_episode = tuple(
                (candidate_id, ep) for candidate_id, _, ep in items
            )
            payload = tuple(items)
            reason = "D3_ANCHOR_LIFECYCLE_REFERENCE_RC1_MULTIPLICITY"

        return frozen.StageResult.make(
            owner=frozen.DomainOwner.D3_BOUNDARY_INTELLIGENCE,
            reason=reason,
            payload=payload,
            information_cutoff=ctx.information_cutoff,
            next_boundary_snapshot_refs=tuple(refs),
        )


def d4_passthrough_is_exact() -> bool:
    return "_u011" not in AdapterIntegrationRuntimeRC1ConformanceV1.__dict__
