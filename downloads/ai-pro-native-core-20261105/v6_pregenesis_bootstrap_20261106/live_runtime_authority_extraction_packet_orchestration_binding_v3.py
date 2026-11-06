from __future__ import annotations

"""Live runtime authority extraction + staged packet orchestration binding V3.

This is orchestration/transport only. It does not reproduce D1/D2/D3/B3/D4
scientific producers. Those producers supply typed authority objects. This
binding:
- converts frozen producer outputs into Assembler V2 authority surfaces;
- invokes the frozen D4 lineage projector immediately before UPDATE-011;
- injects the immutable initial packet through UPDATE-010 and the completed
  final packet from UPDATE-011;
- runs the unchanged deterministic cutoff engine and repaired adapter;
- commits adapter/ledger/assembler/lineage state only after a non-aborted batch.

No market source, TEST/outcome, PnL, Forward Observation, or trading path exists
in this module.
"""

from copy import deepcopy
from dataclasses import dataclass, field, fields, is_dataclass, replace
from enum import Enum
from fractions import Fraction
from hashlib import sha256
import importlib
import json
from types import MappingProxyType
from typing import Any, Iterable, Mapping

import minimal_runnable_v1_baseline as minimal
import nontrading_adapter_d3_d4_schema_orchestration_rc1_conformance_repair_v1 as repaired
import authoritative_d3_d4_evidence_packet_assembler_resumption_v2 as assembler
import authoritative_d3_b5_d4_base_runtime_producers_v1 as b5prod
import runtime_b3_price_driven_return_production_state_v1 as b3prod
import d1_d2_to_d3_candidate_production_v1 as candidate_prod
import d4_market_event_lineage_production_binding_v2 as lineage_prod


frozen = repaired.frozen
engine_mod = importlib.import_module(minimal.DeterministicCutoffEngine.__module__)

BINDING_ID = "LIVE_RUNTIME_AUTHORITY_EXTRACTION_PACKET_ORCHESTRATION_BINDING_V3"
D4_LINEAGE_BINDING_BLOB = "abc5be6afa7cab1d6f958c4b26e368d4963ec80b"
ASSEMBLER_BLOB = "a5f2b841cb44f9ff759232cc3ae72ff844cee02b"
REPAIRED_ADAPTER_BLOB = "ac6bf1385268fa96f2df572772ccee7e4268fd71"

INITIAL_VISIBLE_STEPS = tuple(f"UPDATE-{i:03d}" for i in range(1, 11))
FINAL_VISIBLE_STEPS = tuple(f"UPDATE-{i:03d}" for i in range(11, 14))


class LiveRuntimeBindingBlock(RuntimeError):
    pass


class LiveRuntimeBindingConflict(LiveRuntimeBindingBlock):
    pass


@dataclass(frozen=True)
class D4StaticBaseAuthority:
    """Already-authoritative non-lineage D4 static inputs.

    relation/new-event evidence/lineage refs are intentionally absent. They are
    produced only by the frozen D4 lineage projector inside this binding.
    """

    trend_episode_id: str
    direction: Any
    trend: Any
    trend_position: Any
    detector_evidence_ids: tuple[str, ...]
    critical_information_known: Any
    termination: Any | None = None


@dataclass(frozen=True)
class LiveRuntimeCutoffAuthority:
    """Typed authority bundle for one symbol/cutoff.

    Candidate/B3/D2/D3-B5 mechanism science is not recomputed here. The fields
    are outputs of those already-frozen producers.
    """

    initial: assembler.InitialPacketAuthority
    update008_output: b5prod.Update008Output
    mechanisms: assembler.MechanismProducerOutputs
    d4_static_base: D4StaticBaseAuthority
    lineage_request: lineage_prod.D4LineageProductionRequest
    d5: Any | None = None
    d6: Any | None = None
    provenance: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class PacketVisibilityTrace:
    symbol: str
    transaction_id: str
    initial_packet_digest: str
    final_packet_digest: str | None
    initial_steps: tuple[str, ...]
    final_steps: tuple[str, ...]
    d4_visible_before_update011: bool
    final_visible_from_update011: bool


@dataclass(frozen=True)
class LiveRuntimeBindingResult:
    engine_result: Any
    assembly_results: tuple[tuple[str, assembler.PacketAssemblyResult | None], ...]
    visibility: tuple[PacketVisibilityTrace, ...]
    input_digest: str
    provenance: Mapping[str, str] = field(default_factory=dict)


@dataclass
class LiveRuntimeBindingState:
    adapter_state: str
    ledger_events: tuple[Any, ...] = ()
    next_snapshots: dict[str, Any] = field(default_factory=dict)
    assembler_state: Mapping[str, Any] = field(default_factory=dict)
    lineage_state: str = ""
    completed_batches: dict[str, tuple[str, LiveRuntimeBindingResult]] = field(default_factory=dict)
    last_cutoff: int | None = None


def _resolve(module: str, qualname: str) -> Any:
    obj: Any = importlib.import_module(module)
    for part in qualname.split("."):
        obj = getattr(obj, part)
    return obj


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
    if "$set" in value:
        return set(_decode(x) for x in value["$set"])
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
    return sha256(exact_json(value).encode("utf-8")).hexdigest()


def snapshot_projection_from_authoritative_producers(
    *,
    snapshot_ref: str,
    runtime_b3_result: b3prod.RuntimeB3ProducerResult | None = None,
    structural_acceptance: Any | None = None,
    correct_side_recovery: Any | None = None,
    source_evidence_refs: tuple[str, ...] = (),
    provenance: Mapping[str, str] | None = None,
) -> assembler.D3SnapshotProjectionAuthority:
    """Mechanical mapping into Assembler V2 D3 snapshot authority.

    Runtime-B3's return_evidence is used exactly. latched_evidence is not
    consumed on the qualification cutoff, preserving the frozen same-cutoff
    qualification/contact prohibition.
    """
    if not snapshot_ref:
        raise LiveRuntimeBindingBlock("SNAPSHOT_REF_REQUIRED")
    return_evidence = None
    if runtime_b3_result is not None:
        if not isinstance(runtime_b3_result, b3prod.RuntimeB3ProducerResult):
            raise LiveRuntimeBindingConflict("RUNTIME_B3_RESULT_SCHEMA")
        if runtime_b3_result.snapshot_ref not in (None, snapshot_ref):
            raise LiveRuntimeBindingConflict("RUNTIME_B3_SNAPSHOT_REF_MISMATCH")
        return_evidence = runtime_b3_result.return_evidence
    return assembler.D3SnapshotProjectionAuthority(
        snapshot_ref=snapshot_ref,
        return_evidence=return_evidence,
        structural_acceptance=structural_acceptance,
        correct_side_recovery=correct_side_recovery,
        source_evidence_refs=tuple(sorted(set(source_evidence_refs))),
        provenance=dict(provenance or {}),
    )


def initial_authority_from_frozen_producers(
    *,
    candidate_result: candidate_prod.CandidateProductionResult | None,
    snapshot_projections: Iterable[assembler.D3SnapshotProjectionAuthority] = (),
) -> assembler.InitialPacketAuthority:
    """Lossless candidate multiplicity + snapshot authority mapping."""
    if candidate_result is not None and not isinstance(candidate_result, candidate_prod.CandidateProductionResult):
        raise LiveRuntimeBindingConflict("CANDIDATE_PRODUCTION_RESULT_SCHEMA")
    rows = tuple(snapshot_projections)
    if any(not isinstance(x, assembler.D3SnapshotProjectionAuthority) for x in rows):
        raise LiveRuntimeBindingConflict("D3_SNAPSHOT_PROJECTION_AUTHORITY_SCHEMA")
    refs = [x.snapshot_ref for x in rows]
    if len(refs) != len(set(refs)):
        raise LiveRuntimeBindingConflict("DUPLICATE_D3_SNAPSHOT_AUTHORITY")
    return assembler.InitialPacketAuthority(
        candidate_updates=() if candidate_result is None else tuple(candidate_result.updates),
        snapshot_projections=tuple(sorted(rows, key=lambda x: x.snapshot_ref)),
    )


def _packet_with_external(
    packet: Any,
    *,
    d5: Any | None,
    d6: Any | None,
) -> Any:
    if not isinstance(packet, frozen.CutoffEvidencePacket):
        raise LiveRuntimeBindingConflict("ASSEMBLER_PACKET_SCHEMA")
    return frozen.CutoffEvidencePacket(d3=packet.d3, d4=packet.d4, d5=d5, d6=d6)


def _validate_authority_bundle(bundle: LiveRuntimeCutoffAuthority) -> None:
    if not isinstance(bundle, LiveRuntimeCutoffAuthority):
        raise LiveRuntimeBindingConflict("LIVE_RUNTIME_AUTHORITY_BUNDLE_SCHEMA")
    if not isinstance(bundle.initial, assembler.InitialPacketAuthority):
        raise LiveRuntimeBindingConflict("INITIAL_PACKET_AUTHORITY_SCHEMA")
    if not isinstance(bundle.update008_output, b5prod.Update008Output):
        raise LiveRuntimeBindingConflict("UPDATE008_OUTPUT_SCHEMA")
    if not isinstance(bundle.mechanisms, assembler.MechanismProducerOutputs):
        raise LiveRuntimeBindingConflict("MECHANISM_OUTPUTS_SCHEMA")
    if not isinstance(bundle.d4_static_base, D4StaticBaseAuthority):
        raise LiveRuntimeBindingConflict("D4_STATIC_BASE_SCHEMA")
    if not isinstance(bundle.lineage_request, lineage_prod.D4LineageProductionRequest):
        raise LiveRuntimeBindingConflict("D4_LINEAGE_REQUEST_SCHEMA")
    base = bundle.d4_static_base
    req = bundle.lineage_request
    if not base.trend_episode_id or base.trend_episode_id != req.trend_episode_id:
        raise LiveRuntimeBindingConflict("D4_STATIC_LINEAGE_TREND_EPISODE_MISMATCH")
    if getattr(base.direction, "value", base.direction) != getattr(req.direction, "value", req.direction):
        raise LiveRuntimeBindingConflict("D4_STATIC_LINEAGE_DIRECTION_MISMATCH")
    if getattr(base.trend, "episode_id", None) != base.trend_episode_id:
        raise LiveRuntimeBindingConflict("D4_STATIC_TREND_OBJECT_EPISODE_MISMATCH")


def _batch_key(bars: tuple[Any, ...]) -> str:
    if not bars:
        raise LiveRuntimeBindingBlock("EMPTY_BATCH")
    closes = {x.close_time for x in bars}
    if len(closes) != 1:
        raise LiveRuntimeBindingBlock("MIXED_CUTOFF_BATCH")
    return f"{next(iter(closes))}:" + ",".join(sorted(x.symbol for x in bars))


def _input_digest(
    bars: tuple[Any, ...],
    authorities: Mapping[tuple[str, int], LiveRuntimeCutoffAuthority],
) -> str:
    payload = {
        "bars": tuple(sorted(bars, key=lambda x: x.symbol)),
        "authorities": tuple(
            sorted(
                ((symbol, open_time, authorities[(symbol, open_time)]) for symbol, open_time in authorities),
                key=lambda x: (x[0], x[1]),
            )
        ),
    }
    return digest(payload)


class _StageBindingSession:
    def __init__(
        self,
        *,
        adapter: repaired.AdapterIntegrationRuntimeRC1ConformanceV1,
        assembler_runtime: assembler.AuthoritativeD3D4PacketAssemblerV2,
        lineage_runtime: lineage_prod.D4MarketEventLineageProductionProjectorV2,
        authorities: Mapping[tuple[str, int], LiveRuntimeCutoffAuthority],
    ) -> None:
        self.adapter = adapter
        self.assembler_runtime = assembler_runtime
        self.lineage_runtime = lineage_runtime
        self.authorities = authorities
        self.initial_packets: dict[str, Any] = {}
        self.final_packets: dict[str, Any] = {}
        self.assembly_results: dict[str, assembler.PacketAssemblyResult] = {}
        self.initial_steps: dict[str, list[str]] = {}
        self.final_steps: dict[str, list[str]] = {}
        self.prepared_lineage_tx: set[str] = set()

    def _bundle(self, ctx: Any) -> LiveRuntimeCutoffAuthority:
        key = (ctx.symbol_input.symbol, ctx.symbol_input.observer_bar.open_time)
        if key not in self.authorities:
            raise LiveRuntimeBindingBlock("LIVE_RUNTIME_AUTHORITY_BUNDLE_MISSING")
        bundle = self.authorities[key]
        _validate_authority_bundle(bundle)
        if bundle.lineage_request.symbol != ctx.symbol_input.symbol:
            raise LiveRuntimeBindingConflict("LINEAGE_REQUEST_SYMBOL_MISMATCH")
        cutoff = ctx.information_cutoff or ctx.symbol_input.observer_bar.close_time
        if bundle.lineage_request.information_cutoff != cutoff:
            raise LiveRuntimeBindingConflict("LINEAGE_REQUEST_CUTOFF_MISMATCH")
        return bundle

    def _initial_packet(self, ctx: Any) -> Any:
        tx = ctx.transaction_id
        if tx not in self.initial_packets:
            bundle = self._bundle(ctx)
            initial = self.assembler_runtime.begin(bundle.initial)
            self.initial_packets[tx] = _packet_with_external(initial, d5=bundle.d5, d6=bundle.d6)
        return self.initial_packets[tx]

    def _post_d3_state(self, ctx: Any) -> tuple[tuple[Any, ...], tuple[str, ...]]:
        obj = self.adapter._d3_rebuild(ctx.symbol_input.symbol)
        events = tuple(sorted(obj._events.values(), key=lambda x: x.event_id))
        anchor_ids = tuple(sorted(ep.anchor_episode_id for ep in obj._episodes.values()))
        return events, anchor_ids

    def _final_packet(self, ctx: Any) -> Any:
        tx = ctx.transaction_id
        if tx in self.final_packets:
            return self.final_packets[tx]
        bundle = self._bundle(ctx)
        existing = self.adapter._state(ctx.symbol_input.symbol).current_opportunity
        events, anchor_ids = self._post_d3_state(ctx)

        req = replace(
            bundle.lineage_request,
            existing_opportunity=existing,
            interaction_events=events,
            anchor_episode_ids=anchor_ids,
            mechanisms=bundle.mechanisms,
        )
        projection = self.lineage_runtime.prepare(tx, req)
        self.prepared_lineage_tx.add(tx)
        if projection.relation is None:
            raise LiveRuntimeBindingBlock(
                "D4_LINEAGE_PROJECTION_BLOCKED:" + str(projection.blocked_reason or projection.status)
            )

        base = bundle.d4_static_base
        static = assembler.D4StaticAuthority(
            trend_episode_id=base.trend_episode_id,
            direction=base.direction,
            relation=frozen.EventRelation.UNKNOWN,
            trend=base.trend,
            trend_position=base.trend_position,
            detector_evidence_ids=tuple(base.detector_evidence_ids),
            critical_information_known=base.critical_information_known,
            termination=base.termination,
        )
        static = lineage_prod.bind_d4_static_authority(static, projection)
        post = assembler.PostUpdate008Authority(
            information_cutoff=ctx.information_cutoff or ctx.symbol_input.observer_bar.close_time,
            update008_output=bundle.update008_output,
            d4_static=static,
            mechanisms=bundle.mechanisms,
            existing_opportunity=existing,
            provenance={
                "binding_id": BINDING_ID,
                "symbol": ctx.symbol_input.symbol,
                "transaction_id": tx,
            },
        )
        assembled = self.assembler_runtime.complete(tx, bundle.initial, post)
        final = _packet_with_external(assembled.final_packet, d5=bundle.d5, d6=bundle.d6)
        self.assembly_results[tx] = assembled
        self.final_packets[tx] = final
        return final

    def _call_frozen_stage(self, ctx: Any, packet: Any) -> Any:
        step = ctx.step
        self.adapter.set_evidence(ctx.symbol_input.symbol, ctx.symbol_input.observer_bar.open_time, packet)
        self.adapter.owner_execution_ledger.append(
            (ctx.transaction_id, step.value, frozen.EXPECTED_OWNER[step].value)
        )
        return getattr(self.adapter, f"_u{int(step.value[-3:]):03d}")(ctx)

    def adapter_for(self, step: Any):
        def run(ctx: Any) -> Any:
            if ctx.step is not step:
                raise LiveRuntimeBindingConflict("STAGE_CONTEXT_MISMATCH")
            if step.value in INITIAL_VISIBLE_STEPS:
                packet = self._initial_packet(ctx)
                self.initial_steps.setdefault(ctx.transaction_id, []).append(step.value)
            else:
                packet = self._final_packet(ctx)
                self.final_steps.setdefault(ctx.transaction_id, []).append(step.value)
            return self._call_frozen_stage(ctx, packet)
        return run

    def registry(self) -> Any:
        return engine_mod.AdapterRegistry({
            step: self.adapter_for(step)
            for step in tuple(engine_mod.UpdateStep(f"UPDATE-{i:03d}") for i in range(1, 14))
        })

    def visibility(self, result: Any) -> tuple[PacketVisibilityTrace, ...]:
        rows: list[PacketVisibilityTrace] = []
        for sr in result.symbol_results:
            tx = sr.transaction_id
            initial = self.initial_packets.get(tx)
            final = self.final_packets.get(tx)
            i_steps = tuple(self.initial_steps.get(tx, ()))
            f_steps = tuple(self.final_steps.get(tx, ()))
            rows.append(
                PacketVisibilityTrace(
                    symbol=sr.symbol,
                    transaction_id=tx,
                    initial_packet_digest="" if initial is None else assembler.digest(initial),
                    final_packet_digest=None if final is None else assembler.digest(final),
                    initial_steps=i_steps,
                    final_steps=f_steps,
                    d4_visible_before_update011=bool(
                        initial is not None and getattr(initial, "d4", None) is not None
                    ),
                    final_visible_from_update011=(
                        final is not None
                        and getattr(final, "d4", None) is not None
                        and (not f_steps or f_steps[0] == "UPDATE-011")
                    ),
                )
            )
        return tuple(rows)


class LiveRuntimeAuthorityPacketOrchestrationV3:
    """Transactional staged runtime around the frozen deterministic engine."""

    STATE_SCHEMA = "TAC_LIVE_RUNTIME_AUTHORITY_PACKET_ORCHESTRATION_V3_STATE"

    def __init__(self, state: LiveRuntimeBindingState | None = None) -> None:
        if state is None:
            adapter = repaired.AdapterIntegrationRuntimeRC1ConformanceV1()
            asm = assembler.AuthoritativeD3D4PacketAssemblerV2()
            lin = lineage_prod.D4MarketEventLineageProductionProjectorV2()
            state = LiveRuntimeBindingState(
                adapter_state=adapter.export_state(),
                assembler_state=dict(asm.export_state()),
                lineage_state=lin.export_state(),
            )
        self.state = state

    def _restore_adapter(self) -> repaired.AdapterIntegrationRuntimeRC1ConformanceV1:
        obj = repaired.AdapterIntegrationRuntimeRC1ConformanceV1.restore_state(self.state.adapter_state)
        if not isinstance(obj, repaired.AdapterIntegrationRuntimeRC1ConformanceV1):
            raise LiveRuntimeBindingConflict("RESTORED_ADAPTER_NOT_REPAIRED_SCHEMA")
        return obj

    def _restore_ledger(self) -> Any:
        led = minimal.AppendOnlyLedger()
        for event in self.state.ledger_events:
            led.append(event)
        return led

    def _restore_assembler(self) -> assembler.AuthoritativeD3D4PacketAssemblerV2:
        return assembler.AuthoritativeD3D4PacketAssemblerV2.restore_state(dict(self.state.assembler_state))

    def _restore_lineage(self) -> lineage_prod.D4MarketEventLineageProductionProjectorV2:
        return lineage_prod.D4MarketEventLineageProductionProjectorV2.restore_state(self.state.lineage_state)

    def _input_for(self, bar: Any) -> Any:
        pre = self.state.next_snapshots.get(bar.symbol)
        if pre is None:
            pre = minimal.make_causal_observer_snapshot(
                symbol=bar.symbol,
                source_information_cutoff=bar.open_time - 1,
                eligible_from_open_time=bar.open_time,
                boundary_snapshot_refs=(),
                interaction_control_refs=(),
                strategy_state_refs=(),
            )
        if pre.eligible_from_open_time > bar.open_time:
            raise LiveRuntimeBindingBlock("PREBAR_NOT_YET_ELIGIBLE")
        return minimal.SymbolCutoffInput(
            strategy_id=minimal.STRATEGY_ID,
            parameter_snapshot_id=minimal.current_partial_parameter_snapshot().snapshot_id,
            observer_bar=bar,
            prebar_snapshot=pre,
            fixture_class=minimal.FIXTURE_CLASS,
        )

    def run_cutoff(
        self,
        bars: Iterable[Any],
        authorities: Mapping[tuple[str, int], LiveRuntimeCutoffAuthority],
    ) -> LiveRuntimeBindingResult:
        bars_t = tuple(sorted(tuple(bars), key=lambda x: x.symbol))
        if not bars_t:
            raise LiveRuntimeBindingBlock("EMPTY_BATCH")
        cutoff = bars_t[0].close_time
        if any(x.close_time != cutoff for x in bars_t):
            raise LiveRuntimeBindingBlock("MIXED_CUTOFF_BATCH")
        if len({x.symbol for x in bars_t}) != len(bars_t):
            raise LiveRuntimeBindingBlock("DUPLICATE_SYMBOL_IN_BATCH")
        if self.state.last_cutoff is not None and cutoff < self.state.last_cutoff:
            raise LiveRuntimeBindingBlock("NON_MONOTONIC_CUTOFF")

        expected_keys = {(x.symbol, x.open_time) for x in bars_t}
        if set(authorities) != expected_keys:
            raise LiveRuntimeBindingConflict("AUTHORITY_KEYSET_MUST_EXACTLY_MATCH_BATCH")
        for bundle in authorities.values():
            _validate_authority_bundle(bundle)

        key = _batch_key(bars_t)
        input_digest = _input_digest(bars_t, authorities)
        prior = self.state.completed_batches.get(key)
        if prior is not None:
            if prior[0] != input_digest:
                raise LiveRuntimeBindingConflict("DUPLICATE_BATCH_AUTHORITY_MISMATCH")
            return prior[1]

        candidate_adapter = self._restore_adapter()
        candidate_ledger = self._restore_ledger()
        candidate_assembler = self._restore_assembler()
        candidate_lineage = self._restore_lineage()

        session = _StageBindingSession(
            adapter=candidate_adapter,
            assembler_runtime=candidate_assembler,
            lineage_runtime=candidate_lineage,
            authorities=authorities,
        )
        engine = minimal.DeterministicCutoffEngine(
            adapters=session.registry(),
            ledger=candidate_ledger,
        )
        engine_result = engine.run_cutoff_batch(tuple(self._input_for(x) for x in bars_t))

        if engine_result.terminal in (
            minimal.TransactionTerminal.ABORTED_ERROR,
            minimal.TransactionTerminal.ABORTED_AMBIGUITY,
        ):
            return LiveRuntimeBindingResult(
                engine_result=engine_result,
                assembly_results=tuple(
                    (sr.symbol, session.assembly_results.get(sr.transaction_id))
                    for sr in engine_result.symbol_results
                ),
                visibility=session.visibility(engine_result),
                input_digest=input_digest,
                provenance=MappingProxyType({
                    "binding_id": BINDING_ID,
                    "persistent_state_committed": "false",
                    "abort_is_atomic": "true",
                }),
            )

        # The lineage projector is prepared during UPDATE-011 but becomes
        # authoritative only after the entire cutoff batch has survived.
        for sr in engine_result.symbol_results:
            if sr.transaction_id in session.prepared_lineage_tx:
                candidate_lineage.commit(sr.transaction_id)

        visibility = session.visibility(engine_result)
        for row in visibility:
            if row.d4_visible_before_update011:
                raise LiveRuntimeBindingConflict("D4_VISIBLE_BEFORE_UPDATE011")
            if row.final_packet_digest is not None:
                if row.initial_steps != INITIAL_VISIBLE_STEPS:
                    raise LiveRuntimeBindingConflict("INITIAL_PACKET_STAGE_VISIBILITY_VIOLATION")
                if row.final_steps != FINAL_VISIBLE_STEPS:
                    raise LiveRuntimeBindingConflict("FINAL_PACKET_STAGE_VISIBILITY_VIOLATION")
                if not row.final_visible_from_update011:
                    raise LiveRuntimeBindingConflict("FINAL_PACKET_NOT_VISIBLE_FROM_UPDATE011")

        result = LiveRuntimeBindingResult(
            engine_result=engine_result,
            assembly_results=tuple(
                (sr.symbol, session.assembly_results.get(sr.transaction_id))
                for sr in engine_result.symbol_results
            ),
            visibility=visibility,
            input_digest=input_digest,
            provenance=MappingProxyType({
                "binding_id": BINDING_ID,
                "d4_lineage_binding_blob": D4_LINEAGE_BINDING_BLOB,
                "assembler_blob": ASSEMBLER_BLOB,
                "repaired_adapter_blob": REPAIRED_ADAPTER_BLOB,
                "persistent_state_committed": "true",
                "initial_packet_visible_through": "UPDATE-010",
                "final_packet_visible_from": "UPDATE-011",
                "update008_to_update002_backflow": "false",
            }),
        )

        new_snaps = dict(self.state.next_snapshots)
        for sr in engine_result.symbol_results:
            if sr.next_bar_snapshot is not None:
                new_snaps[sr.symbol] = sr.next_bar_snapshot
        completed = dict(self.state.completed_batches)
        completed[key] = (input_digest, result)

        self.state = LiveRuntimeBindingState(
            adapter_state=candidate_adapter.export_state(),
            ledger_events=candidate_ledger.snapshot(),
            next_snapshots=new_snaps,
            assembler_state=dict(candidate_assembler.export_state()),
            lineage_state=candidate_lineage.export_state(),
            completed_batches=completed,
            last_cutoff=cutoff,
        )
        return result

    def export_state(self) -> str:
        payload = {
            "schema": self.STATE_SCHEMA,
            "adapter_state": self.state.adapter_state,
            "ledger_events": _encode(self.state.ledger_events),
            "next_snapshots": _encode(self.state.next_snapshots),
            "assembler_state": _encode(dict(self.state.assembler_state)),
            "lineage_state": self.state.lineage_state,
            "completed_batches": _encode(self.state.completed_batches),
            "last_cutoff": self.state.last_cutoff,
            "governance": {
                "real_market_data_read": False,
                "test": "NOT_AUTHORIZED",
                "forward_observation": "NOT_ACTIVE",
                "trading": "FORBIDDEN",
                "production_runtime_usable_claim": False,
            },
        }
        return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    @classmethod
    def restore_state(cls, raw: str) -> "LiveRuntimeAuthorityPacketOrchestrationV3":
        try:
            payload = json.loads(raw)
        except Exception as exc:
            raise LiveRuntimeBindingConflict("STATE_JSON_INVALID") from exc
        if payload.get("schema") != cls.STATE_SCHEMA:
            raise LiveRuntimeBindingConflict("STATE_SCHEMA_MISMATCH")
        gov = payload.get("governance") or {}
        if (
            gov.get("real_market_data_read") is not False
            or gov.get("test") != "NOT_AUTHORIZED"
            or gov.get("forward_observation") != "NOT_ACTIVE"
            or gov.get("trading") != "FORBIDDEN"
            or gov.get("production_runtime_usable_claim") is not False
        ):
            raise LiveRuntimeBindingConflict("STATE_GOVERNANCE_MISMATCH")
        state = LiveRuntimeBindingState(
            adapter_state=str(payload["adapter_state"]),
            ledger_events=tuple(_decode(payload["ledger_events"])),
            next_snapshots=dict(_decode(payload["next_snapshots"])),
            assembler_state=dict(_decode(payload["assembler_state"])),
            lineage_state=str(payload["lineage_state"]),
            completed_batches=dict(_decode(payload["completed_batches"])),
            last_cutoff=payload.get("last_cutoff"),
        )
        out = cls(state)
        # Eagerly validate all frozen state schemas.
        out._restore_adapter()
        out._restore_assembler()
        out._restore_lineage()
        return out

    def state_digest(self) -> str:
        return sha256(self.export_state().encode("utf-8")).hexdigest()
