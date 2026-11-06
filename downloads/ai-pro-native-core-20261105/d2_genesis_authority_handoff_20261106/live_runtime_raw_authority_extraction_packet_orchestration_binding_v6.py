from __future__ import annotations

"""V6 raw completed-15M -> typed authority -> D4 -> staged-engine orchestration.

Current implementation closes the exact first-authoritative-Trend / pure-WATCH
genesis path from durable raw state.  It intentionally fails closed on later
active-Trend continuation until the mature prebar B3/B4 mechanism path has been
mechanically bound in this same V6 authorization.

No market I/O, TEST/outcome/PnL surface, trading, new strategy state, numeric
threshold, fixed window, or mechanism priority is introduced.
"""

from dataclasses import dataclass, field, replace
from fractions import Fraction
from hashlib import sha256
import json
from types import MappingProxyType
from typing import Any, Mapping

import minimal_runnable_v1_baseline as minimal
import nontrading_adapter_integration_v1 as frozen
import nontrading_adapter_d3_d4_schema_orchestration_rc1_conformance_repair_v1 as repaired
import authoritative_d3_d4_evidence_packet_assembler_resumption_v2 as assembler
import authoritative_d3_b5_d4_base_runtime_producers_v1 as b5prod
import d1_d2_to_d3_candidate_production_v1 as candidate_prod
import runtime_b3_price_driven_return_production_state_v1 as b3prod
import qbu_same_event_negotiation_identity_production_binding_v1 as qid
import qbu_material_trend_side_minor_progress_production_binding_v1 as qprog
import d4_market_event_lineage_production_binding_v2 as lineage_prod
import d4_static_detector_critical_production_binding_v1 as d4static
import d4_static_pure_watch_update008_completeness_production_binding_v2 as purewatch
import mature_no_active_d4_observation_update008_lineage_completeness_production_binding_v1 as maturenoactive
import platform_failed_reexpansion_event_and_state_production_binding_v1 as platform_prod
import live_runtime_authority_extraction_packet_orchestration_binding_v3 as live

from d2_to_b4_d4_causal_evidence_producers_v1 import EvidenceState
from strategy_rc1.d2_market_state.establishment import latest_establishment_evidence
from strategy_rc1.d2_market_state.types import StructuralPivot, TrendDirection
from strategy_rc1.runtime_guards.information_state import InfoKind, InfoValue


BINDING_ID = "LIVE_RUNTIME_RAW_AUTHORITY_EXTRACTION_PACKET_ORCHESTRATION_BINDING_V6"
PLATFORM_BINDING_BLOB = "0f114278eebb683c9090a476f6ece62fe12ed105"
PURE_WATCH_BINDING_BLOB = "074a2b08a7aec6b2c51431a5ccadcc0aa75e0ebb"
D4_STATIC_BINDING_BLOB = "9eac94f81d874f41f25f856aee16c60ee8deb312"
D4_LINEAGE_BINDING_BLOB = "f334155bbb46ec2ff0ee748555cb15c1485d3036"
ASSEMBLER_BLOB = "a5f2b841cb44f9ff759232cc3ae72ff844cee02b"
V3_BINDING_BLOB = "fa9842eab6851c2bb67f2f32ec09b20514271018"
MATURE_NO_ACTIVE_BINDING_BLOB = "e4d0ff83d3e8168ddac63c4aad63942e3cac2b99"
OBSERVER_TIMEFRAME_MS = 15 * 60 * 1000


class RawV6Block(RuntimeError):
    pass


class RawV6Conflict(RawV6Block):
    pass


@dataclass(frozen=True)
class RawV6CutoffResult:
    mode: str
    engine_result: Any
    trend_episode_id: str | None
    relation: Any | None
    coverage_statuses: tuple[tuple[str, str], ...] = ()
    candidate_update_count: int = 0
    prebar_snapshot_count: int = 0
    final_packet_digest: str | None = None
    persistent_state_committed: bool = True
    blocker: str | None = None
    provenance: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "provenance",
            MappingProxyType({str(k): str(v) for k, v in self.provenance.items()}),
        )


@dataclass
class RawV6State:
    adapter_state: str
    ledger_events: tuple[Any, ...] = ()
    next_snapshots: dict[str, Any] = field(default_factory=dict)
    assembler_state: Mapping[str, Any] = field(default_factory=dict)
    lineage_state: str = ""
    candidate_state: str = ""
    b3_state: str = ""
    b5_state: Mapping[str, Any] = field(default_factory=dict)
    platform_state: Mapping[str, Any] = field(default_factory=dict)
    minor_history: tuple[StructuralPivot, ...] = ()
    intermediate_history: tuple[StructuralPivot, ...] = ()
    completed: dict[str, tuple[str, RawV6CutoffResult]] = field(default_factory=dict)
    last_cutoff: int | None = None


def _append_pivots(
    prior: tuple[StructuralPivot, ...],
    new: tuple[StructuralPivot, ...],
) -> tuple[StructuralPivot, ...]:
    rows = {p.pivot_id: p for p in prior}
    for p in new:
        old = rows.get(p.pivot_id)
        if old is not None and old != p:
            raise RawV6Conflict("DIVERGENT_PIVOT_RECORD:" + p.pivot_id)
        rows[p.pivot_id] = p
    return tuple(sorted(rows.values(), key=lambda x: (x.confirmed_at, x.pivot_id)))


def _collection(obj: Any, name: str) -> tuple[Any, ...]:
    value = getattr(obj, name, None)
    if value is None:
        return ()
    if isinstance(value, Mapping):
        rows = tuple(value.values())
    elif isinstance(value, (list, tuple)):
        rows = tuple(value)
    else:
        raise RawV6Conflict("D3_COLLECTION_SCHEMA:" + name)
    return rows


def _event_rows(d3: Any) -> tuple[Any, ...]:
    by_id: dict[str, Any] = {}
    for ev in _collection(d3, "_events"):
        old = by_id.get(ev.event_id)
        if old is not None and old != ev:
            raise RawV6Conflict("DIVERGENT_INTERACTION_EVENT:" + ev.event_id)
        by_id[ev.event_id] = ev
    return tuple(by_id[k] for k in sorted(by_id))


def _episode_rows(d3: Any) -> tuple[Any, ...]:
    by_id: dict[str, Any] = {}
    for ep in _collection(d3, "_episodes"):
        old = by_id.get(ep.anchor_episode_id)
        if old is not None and old != ep:
            raise RawV6Conflict("DIVERGENT_ANCHOR_EPISODE:" + ep.anchor_episode_id)
        by_id[ep.anchor_episode_id] = ep
    return tuple(by_id[k] for k in sorted(by_id))


def _snapshot_rows(d3: Any) -> tuple[Any, ...]:
    by_id: dict[str, Any] = {}
    for snap in _collection(d3, "_snapshots"):
        old = by_id.get(snap.snapshot_id)
        if old is not None and old != snap:
            raise RawV6Conflict("DIVERGENT_SNAPSHOT:" + snap.snapshot_id)
        by_id[snap.snapshot_id] = snap
    return tuple(by_id[k] for k in sorted(by_id))


class _PreassembledPacketSession:
    def __init__(self, adapter: Any, initial_packet: Any, final_packet: Any) -> None:
        self.adapter = adapter
        self.initial_packet = initial_packet
        self.final_packet = final_packet
        self.initial_steps: list[str] = []
        self.final_steps: list[str] = []

    def adapter_for(self, step: Any):
        def run(ctx: Any) -> Any:
            if ctx.step is not step:
                raise RawV6Conflict("STAGE_CONTEXT_MISMATCH")
            if step.value in live.INITIAL_VISIBLE_STEPS:
                packet = self.initial_packet
                self.initial_steps.append(step.value)
            else:
                packet = self.final_packet
                self.final_steps.append(step.value)
            self.adapter.set_evidence(
                ctx.symbol_input.symbol,
                ctx.symbol_input.observer_bar.open_time,
                packet,
            )
            self.adapter.owner_execution_ledger.append(
                (ctx.transaction_id, step.value, frozen.EXPECTED_OWNER[step].value)
            )
            return getattr(self.adapter, f"_u{int(step.value[-3:]):03d}")(ctx)
        return run

    def registry(self) -> Any:
        return live.engine_mod.AdapterRegistry({
            step: self.adapter_for(step)
            for step in tuple(live.engine_mod.UpdateStep(f"UPDATE-{i:03d}") for i in range(1, 14))
        })


class LiveRuntimeRawAuthorityOrchestrationV6:
    STATE_SCHEMA = "TAC_LIVE_RUNTIME_RAW_AUTHORITY_PACKET_ORCHESTRATION_V6_STATE"

    def __init__(self, state: RawV6State | None = None) -> None:
        if state is None:
            adapter = repaired.AdapterIntegrationRuntimeRC1ConformanceV1()
            asm = assembler.AuthoritativeD3D4PacketAssemblerV2()
            lin = lineage_prod.D4MarketEventLineageProductionProjectorV2()
            cand = candidate_prod.D1D2D3CandidateProductionRuntimeV1()
            b3 = b3prod.RuntimeB3PriceDrivenReturnProducerV1()
            b5 = b5prod.AuthoritativeD3B5D4BaseRuntimeV1()
            plat = platform_prod.PlatformFailedReexpansionProductionRuntimeV1()
            state = RawV6State(
                adapter_state=adapter.export_state(),
                assembler_state=dict(asm.export_state()),
                lineage_state=lin.export_state(),
                candidate_state=cand.export_state(),
                b3_state=b3.export_state(),
                b5_state=dict(b5.export_state()),
                platform_state=dict(plat.export_state()),
            )
        self.state = state

    def _adapter(self) -> Any:
        out = repaired.AdapterIntegrationRuntimeRC1ConformanceV1.restore_state(self.state.adapter_state)
        if not isinstance(out, repaired.AdapterIntegrationRuntimeRC1ConformanceV1):
            raise RawV6Conflict("RESTORED_ADAPTER_SCHEMA")
        return out

    def _ledger(self) -> Any:
        out = minimal.AppendOnlyLedger()
        for ev in self.state.ledger_events:
            out.append(ev)
        return out

    def _input(self, bar: Any) -> Any:
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
            raise RawV6Block("PREBAR_NOT_YET_ELIGIBLE")

        # UPDATE-008 next refs are prospective handoff refs, not an assertion
        # that every produced snapshot is already visible at the next observer
        # open. Rebuild the frozen D3 state and use its exact pre-bar view.
        # available_at is never rewritten and no ref is admitted early.
        durable = self._adapter()._d3_rebuild(bar.symbol)
        eligible = tuple(sorted(
            snap.snapshot_id
            for snap in durable.update_000_pre_bar_view(bar.open_time).snapshots
        ))
        if tuple(pre.boundary_snapshot_refs) != eligible:
            pre = replace(pre, boundary_snapshot_refs=eligible)
        return minimal.SymbolCutoffInput(
            strategy_id=minimal.STRATEGY_ID,
            parameter_snapshot_id=minimal.current_partial_parameter_snapshot().snapshot_id,
            observer_bar=bar,
            prebar_snapshot=pre,
            fixture_class=minimal.FIXTURE_CLASS,
        )

    def _raw_shadow(self, bar: Any) -> tuple[Any, Any, Any, Any, Any]:
        adapter = self._adapter()
        ledger = self._ledger()
        inp = self._input(bar)
        packet = frozen.CutoffEvidencePacket(
            d3=repaired.D3EvidencePacketRC1V1(),
            d4=None,
        )
        adapter.set_evidence(bar.symbol, bar.open_time, packet)
        engine = minimal.DeterministicCutoffEngine(adapters=adapter.registry(), ledger=ledger)
        result = engine.run_cutoff_batch((inp,))
        sr = result.symbol_results[0]
        if result.terminal in (
            minimal.TransactionTerminal.ABORTED_ERROR,
            minimal.TransactionTerminal.ABORTED_AMBIGUITY,
        ):
            details=[]
            for row in result.symbol_results:
                for stage in row.stages:
                    state=getattr(stage.state,"value",str(stage.state))
                    reason=getattr(stage,"reason",None)
                    if state not in ("PASS","NA"):
                        details.append(f"{stage.step.value}:{state}:{reason}")
            raise RawV6Block(
                "RAW_SHADOW_ABORTED:" + result.terminal.value + ":" + "|".join(details)
                + ":RESULT=" + repr(result)[:8000]
            )
        cache = adapter.tx_cache[sr.transaction_id]
        if cache.d1 is None or cache.d2 is None:
            raise RawV6Block("RAW_D1_D2_NOT_MATERIALIZED")
        return adapter, ledger, result, sr, cache

    def _post_d3_shadow(
        self,
        bar: Any,
        initial: assembler.InitialPacketAuthority,
    ) -> tuple[Any, Any, Any, Any, Any]:
        adapter = self._adapter()
        ledger = self._ledger()
        inp = self._input(bar)
        packet = assembler.assemble_initial_cutoff_packet(initial)
        adapter.set_evidence(bar.symbol, bar.open_time, packet)
        engine = minimal.DeterministicCutoffEngine(adapters=adapter.registry(), ledger=ledger)
        result = engine.run_cutoff_batch((inp,))
        sr = result.symbol_results[0]
        if result.terminal in (
            minimal.TransactionTerminal.ABORTED_ERROR,
            minimal.TransactionTerminal.ABORTED_AMBIGUITY,
        ):
            raise RawV6Block("POST_D3_SHADOW_ABORTED:" + result.terminal.value)
        cache = adapter.tx_cache[sr.transaction_id]
        return adapter, ledger, result, sr, cache

    def _commit_raw(
        self,
        *,
        bar: Any,
        adapter: Any,
        ledger: Any,
        engine_result: Any,
        cache: Any,
        result: RawV6CutoffResult,
    ) -> RawV6CutoffResult:
        sr = engine_result.symbol_results[0]
        snaps = dict(self.state.next_snapshots)
        if sr.next_bar_snapshot is not None:
            snaps[sr.symbol] = sr.next_bar_snapshot
        minor = _append_pivots(self.state.minor_history, tuple(cache.d2.update_005_minor))
        intermediate = _append_pivots(
            self.state.intermediate_history,
            tuple(cache.d2.update_005_intermediate),
        )
        completed = dict(self.state.completed)
        completed[f"{bar.symbol}:{bar.close_time}"] = (live.digest(bar), result)
        self.state = RawV6State(
            adapter_state=adapter.export_state(),
            ledger_events=ledger.snapshot(),
            next_snapshots=snaps,
            assembler_state=self.state.assembler_state,
            lineage_state=self.state.lineage_state,
            candidate_state=self.state.candidate_state,
            b3_state=self.state.b3_state,
            b5_state=self.state.b5_state,
            platform_state=self.state.platform_state,
            minor_history=minor,
            intermediate_history=intermediate,
            completed=completed,
            last_cutoff=bar.close_time,
        )
        return result

    def _continuity_map(self, candidates: tuple[Any, ...], segment: str) -> dict[str, bool]:
        out: dict[str, bool] = {}
        for c in candidates:
            ok = c.source_segment_id == segment
            prior = out.get(c.candidate_id)
            if prior is not None and prior != ok:
                raise RawV6Conflict("CANDIDATE_CONTINUITY_CONFLICT:" + c.candidate_id)
            out[c.candidate_id] = ok
        return out

    def _genesis(
        self,
        *,
        bar: Any,
        raw_result: Any,
        raw_sr: Any,
        raw_cache: Any,
    ) -> RawV6CutoffResult:
        trend = raw_cache.d2.update_006_trend
        if trend.episode_id is None or trend.episode_start_cutoff != bar.close_time:
            raise RawV6Conflict("GENESIS_PRECONDITION_MISMATCH")
        direction = trend.direction
        if direction not in (TrendDirection.LONG, TrendDirection.SHORT):
            raise RawV6Conflict("GENESIS_DIRECTION_INVALID")

        params = frozen.frozen_d3_parameters(minimal.current_partial_parameter_snapshot())
        minor_history = _append_pivots(
            self.state.minor_history, tuple(raw_cache.d2.update_005_minor)
        )
        intermediate_history = _append_pivots(
            self.state.intermediate_history, tuple(raw_cache.d2.update_005_intermediate)
        )
        establishment = latest_establishment_evidence(
            intermediate_history,
            theta_progress=params.theta_progress,
        )
        if establishment is None:
            raise RawV6Block("GENESIS_ESTABLISHMENT_EVIDENCE_MISSING")
        if (
            establishment.newest_pivot_id != trend.frontier_pivot.pivot_id
            or establishment.direction is not direction
        ):
            raise RawV6Conflict("GENESIS_ESTABLISHMENT_TREND_MISMATCH")
        record = b5prod.TrendEstablishmentRecord(
            trend=trend,
            creation_cutoff=trend.episode_start_cutoff,
            newest_intermediate_pivot_id=establishment.newest_pivot_id,
            source_event_ids=tuple(establishment.sequence_pivot_ids),
            provenance={
                "producer_id": BINDING_ID,
                "source": "FROZEN_LATEST_ESTABLISHMENT_EVIDENCE",
            },
        )

        pre_d3 = self._adapter()._d3_rebuild(bar.symbol)
        pre_events = _event_rows(pre_d3)
        pre_snaps = tuple(
            x for x in _snapshot_rows(pre_d3)
            if x.available_at <= bar.open_time
        )
        if pre_snaps:
            raise RawV6Block("MATURE_PREBAR_RUNTIME_B3_B4_PATH_REQUIRED")

        cand_rt = candidate_prod.D1D2D3CandidateProductionRuntimeV1.restore_state(
            self.state.candidate_state
        )
        cand_req = candidate_prod.CandidateProductionRequest(
            transaction_id=raw_sr.transaction_id + ":CANDIDATE",
            symbol=bar.symbol,
            information_cutoff=bar.close_time,
            d1=raw_cache.d1,
            target_trend=trend,
            interaction_events=pre_events,
        )
        cand_result = cand_rt.project_candidate_updates(cand_req)
        initial = live.initial_authority_from_frozen_producers(
            candidate_result=cand_result,
            snapshot_projections=(),
        )

        post_adapter, _, post_result, post_sr, _ = self._post_d3_shadow(bar, initial)
        if post_sr.transaction_id != raw_sr.transaction_id:
            raise RawV6Conflict("SHADOW_TRANSACTION_ID_DRIFT")
        formal_tx = post_sr.transaction_id
        post_d3 = post_adapter._d3_rebuild(bar.symbol)
        snapshots = _snapshot_rows(post_d3)
        episodes = _episode_rows(post_d3)
        events = _event_rows(post_d3)
        candidates_by_id: dict[str, Any] = {}
        for row in cand_result.updates:
            c = row.candidate
            old = candidates_by_id.get(c.candidate_id)
            if old is not None and old != c:
                raise RawV6Conflict("DIVERGENT_CANDIDATE:" + c.candidate_id)
            candidates_by_id[c.candidate_id] = c
        candidates = tuple(candidates_by_id[k] for k in sorted(candidates_by_id))

        segment = raw_result.symbol_results[0].canonical_segment_id
        if not segment:
            segment = post_adapter._state(bar.symbol).last_canonical_segment_id
        if not segment:
            raise RawV6Block("CURRENT_CANONICAL_SEGMENT_REQUIRED")
        continuity = self._continuity_map(candidates, segment)

        segment_by_anchor: dict[str, str] = {}
        for ep in episodes:
            matching = [
                c.source_segment_id for c in candidates
                if c.candidate_id == ep.candidate_id
            ]
            if len(set(matching)) > 1:
                raise RawV6Conflict("ANCHOR_CANDIDATE_SEGMENT_CONFLICT:" + ep.anchor_episode_id)
            if matching:
                segment_by_anchor[ep.anchor_episode_id] = matching[0]

        corridor_info = raw_cache.d2.update_009_structural_corridor
        corridor = (
            corridor_info.require_known()
            if corridor_info.kind is InfoKind.KNOWN
            else None
        )
        protected = trend.protected_pivot
        base_u8 = b5prod.Update008Request(
            information_cutoff=bar.close_time,
            trend_episode_id=trend.episode_id,
            direction=direction,
            snapshots=snapshots,
            candidates=candidates,
            episodes=episodes,
            events=events,
            progress_evidence=(),
            negotiation_identity_by_event_id={},
            canonical_segment_id_by_anchor_episode_id=segment_by_anchor,
            continuity_by_candidate_id=continuity,
            corridor=corridor,
            protected_price=None if protected is None else protected.extreme_price,
            protected_scale=None if protected is None else protected.scale_at_extreme,
            theta_test=params.theta_test,
            theta_progress=params.theta_progress,
            provenance={
                "producer_id": BINDING_ID,
                "f9_stage": "UPDATE-008",
                "no_update002_backflow": "true",
                "runtime_contract_id": b5prod.RUNTIME_CONTRACT_ID,
            },
        )
        qid_proj = qid.project_negotiation_identity(
            qid.NegotiationIdentityRequest(
                information_cutoff=bar.close_time,
                trend_episode_id=trend.episode_id,
                direction=direction,
                events=events,
                episodes=episodes,
                continuity_by_candidate_id=continuity,
                theta_test=params.theta_test,
                rearm_predecessor_by_event_id={},
                history_complete=True,
                provenance={"producer_id": BINDING_ID},
            )
        )
        if qid_proj.status != qid.STATUS_KNOWN:
            raise RawV6Block("GENESIS_NEGOTIATION_IDENTITY_NOT_KNOWN:" + str(qid_proj.reason))
        u8_qid = qid.bind_update008_request(base_u8, qid_proj)
        qprog_proj = qprog.project_qbu_progress_evidence(
            qprog.QBUProgressProductionRequest(
                update008_request=u8_qid,
                all_minor=minor_history,
                trend_episode_start_cutoff=trend.episode_start_cutoff,
                trend_episode_terminal_cutoff=None,
                history_complete=True,
                history_coverage_ref="V6:MINOR_HISTORY:" + trend.episode_id,
                theta_progress_parameter_ref="PARAM:theta_progress",
                provenance={"producer_id": BINDING_ID},
            )
        )
        if qprog_proj.state is not EvidenceState.TRUE:
            raise RawV6Block("GENESIS_QBU_PROGRESS_NOT_TRUE")
        u8_req = qprog.bind_update008_request(u8_qid, qprog_proj)

        b5_rt = b5prod.AuthoritativeD3B5D4BaseRuntimeV1.restore_state(
            dict(self.state.b5_state)
        )
        prior_role_memory = b5_rt._role_memory.get(trend.episode_id)
        u8_out = b5_rt.process_update008(formal_tx + ":U8", u8_req)
        if u8_out.roles is None:
            raise RawV6Block("UPDATE008_ROLE_ASSIGNMENT_MISSING")
        cand_rt.record_post_update008_role_transition(
            candidate_prod.PostUpdate008RoleTransitionRequest(
                transaction_id=formal_tx + ":ROLE",
                information_cutoff=bar.close_time,
                role_assignment=u8_out.roles,
                prior_role_memory=prior_role_memory,
                anchor_episodes=tuple(u8_out.episodes),
            )
        )

        watch = b5prod.produce_trend_establishment_watch(
            record=record,
            information_cutoff=bar.close_time,
        )
        if watch.state is not EvidenceState.TRUE or watch.evidence is None:
            raise RawV6Block("AUTHORITATIVE_WATCH_GENESIS_NOT_TRUE")

        platform_rt = platform_prod.PlatformFailedReexpansionProductionRuntimeV1.restore_state(
            dict(self.state.platform_state)
        )
        current_d1 = raw_cache.d1.math_15m[-1]
        platform_projection = platform_rt.prepare(
            formal_tx,
            platform_prod.PlatformProductionRequest(
                information_cutoff=bar.close_time,
                symbol=bar.symbol,
                trend_episode_id=trend.episode_id,
                direction=direction,
                trend_state=trend,
                all_minor=minor_history,
                events=events,
                episodes=episodes,
                canonical_segment_id_by_anchor_episode_id=segment_by_anchor,
                continuity_by_candidate_id=continuity,
                rearm_predecessor_by_event_id={},
                rearm_cutoff_by_event_id={},
                canonical_continuity=True,
                atr14_at_confirmation=InfoValue.known(current_d1.atr14),
                theta_progress=params.theta_progress,
                theta_progress_parameter_ref="PARAM:theta_progress",
                history_complete=True,
                history_coverage_ref="V6:RAW_D2_HISTORY:" + trend.episode_id,
                current_close=bar.close,
                setup_lineage=(),
                provenance={"producer_id": BINDING_ID},
            ),
        )
        if platform_projection.state in (EvidenceState.UNKNOWN, EvidenceState.CONFLICT):
            raise RawV6Block("GENESIS_PLATFORM_SURFACE_NOT_COMPLETE")
        if platform_projection.platform_reexpansion_evidence is not None:
            raise RawV6Conflict("GENESIS_PLATFORM_UNEXPECTEDLY_ACTIVE")

        mechanisms = assembler.MechanismProducerOutputs(
            trend_establishment_watch=watch,
        )
        lineage_rt = lineage_prod.D4MarketEventLineageProductionProjectorV2.restore_state(
            self.state.lineage_state
        )
        lineage_req = lineage_prod.D4LineageProductionRequest(
            symbol=bar.symbol,
            information_cutoff=bar.close_time,
            trend_episode_id=trend.episode_id,
            direction=direction,
            canonical_continuity_known=True,
            canonical_continuity_intact=True,
            active_mechanisms=(lineage_prod.MECH_WATCH,),
            trend_establishment_record=record,
            existing_opportunity=None,
            interaction_events=events,
            runtime_b3_results=(),
            local_control_regain_results=(),
            mechanisms=mechanisms,
            anchor_episode_ids=tuple(ep.anchor_episode_id for ep in episodes),
            future_evidence_detected=False,
            provenance={"producer_id": BINDING_ID},
        )
        lin_proj = lineage_rt.prepare(formal_tx, lineage_req)
        if lin_proj.relation is not frozen.EventRelation.START_FIRST_EVENT:
            raise RawV6Block("GENESIS_LINEAGE_NOT_START_FIRST_EVENT")

        coverage = d4static.D4CriticalCoverageProof(
            raw_and_d2_state=d4static.SourceCoverageFact(
                "COMPLETE",
                (
                    "CanonicalBar:" + str(bar.open_time),
                    "D1Math15M:" + str(bar.close_time),
                    "TrendEpisode:" + trend.episode_id,
                    "D2Intermediate:" + establishment.newest_pivot_id,
                ),
                provenance={"producer_id": BINDING_ID},
            ),
            d3_candidate_and_runtime_b3=d4static.SourceCoverageFact(
                "COMPLETE",
                (
                    "CandidateBatch:" + cand_result.output_digest,
                    "RuntimeB3:NOT_APPLICABLE_NO_CAUSAL_PREBAR_SNAPSHOT",
                ),
                provenance={"prebar_snapshot_count": str(len(pre_snaps))},
            ),
            d2_b4_d4_causal_projections=d4static.SourceCoverageFact(
                "COMPLETE",
                ("B4:NOT_APPLICABLE_NO_ACTIVE_PREBAR_INTERACTION",),
                provenance={"producer_id": BINDING_ID},
            ),
            update008_d3_b5_state=d4static.SourceCoverageFact(
                "COMPLETE",
                ("Update008:" + formal_tx,),
                provenance={"producer_id": BINDING_ID},
            ),
            d4_mechanism_source_coverage=d4static.SourceCoverageFact(
                "COMPLETE",
                (
                    "Mechanism:WATCH:TRUE",
                    "Mechanism:NORMAL:NOT_APPLICABLE_NO_ACTIVE_INTERACTION",
                    "Mechanism:FBR:NOT_APPLICABLE_NO_ACTIVE_INTERACTION",
                    "Mechanism:PLATFORM:EVALUATED_FALSE",
                    "Mechanism:DEEP:NOT_APPLICABLE_NO_ACTIVE_INTERACTION",
                ),
                provenance={"producer_id": BINDING_ID},
            ),
            d4_market_event_lineage=d4static.SourceCoverageFact(
                "COMPLETE",
                tuple(lin_proj.lineage_evidence_refs),
                provenance={"producer_id": BINDING_ID},
            ),
            future_evidence_detected=False,
            provenance={"producer_id": BINDING_ID},
        )
        static_req = d4static.D4StaticAssociationRequest(
            information_cutoff=bar.close_time,
            trend_episode_id=trend.episode_id,
            direction=direction,
            trend=trend,
            trend_position=raw_cache.d2.update_009_trend_position,
            update008_output=u8_out,
            mechanisms=mechanisms,
            lineage_projection=lin_proj,
            coverage=coverage,
            provenance={"producer_id": BINDING_ID},
        )
        static_proj = purewatch.project_d4_static_source_association(
            static_req,
            reconciliation_context=purewatch.PureWatchGenesisReconciliationContext(
                lineage_request=lineage_req,
                provenance={"producer_id": BINDING_ID},
            ),
        )
        if static_proj.status != "READY" or static_proj.d4_static_authority is None:
            raise RawV6Block(
                "D4_STATIC_NOT_READY:" + str(static_proj.blocked_reason or static_proj.status)
            )

        asm_rt = assembler.AuthoritativeD3D4PacketAssemblerV2.restore_state(
            dict(self.state.assembler_state)
        )
        initial_packet = asm_rt.begin(initial)
        assembled = asm_rt.complete(
            formal_tx,
            initial,
            assembler.PostUpdate008Authority(
                information_cutoff=bar.close_time,
                update008_output=u8_out,
                d4_static=static_proj.d4_static_authority,
                mechanisms=mechanisms,
                existing_opportunity=None,
                provenance={"producer_id": BINDING_ID},
            ),
        )
        final_packet = assembled.final_packet

        formal_adapter = self._adapter()
        formal_ledger = self._ledger()
        session = _PreassembledPacketSession(
            formal_adapter, initial_packet, final_packet
        )
        engine = minimal.DeterministicCutoffEngine(
            adapters=session.registry(),
            ledger=formal_ledger,
        )
        formal_result = engine.run_cutoff_batch((self._input(bar),))
        formal_sr = formal_result.symbol_results[0]
        if formal_sr.transaction_id != formal_tx:
            raise RawV6Conflict("FORMAL_TRANSACTION_ID_DRIFT")
        if formal_result.terminal in (
            minimal.TransactionTerminal.ABORTED_ERROR,
            minimal.TransactionTerminal.ABORTED_AMBIGUITY,
        ):
            lineage_rt.abort(formal_tx)
            platform_rt.abort(formal_tx)
            return RawV6CutoffResult(
                mode="GENESIS_ABORTED",
                engine_result=formal_result,
                trend_episode_id=trend.episode_id,
                relation=lin_proj.relation,
                coverage_statuses=static_proj.coverage_statuses,
                candidate_update_count=len(cand_result.updates),
                prebar_snapshot_count=len(pre_snaps),
                final_packet_digest=assembled.packet_digest,
                persistent_state_committed=False,
                blocker="FORMAL_STAGED_ENGINE_ABORT",
                provenance={"binding_id": BINDING_ID, "abort_is_atomic": "true"},
            )
        if tuple(session.initial_steps) != live.INITIAL_VISIBLE_STEPS:
            raise RawV6Conflict("INITIAL_PACKET_STAGE_VISIBILITY_VIOLATION")
        if tuple(session.final_steps) != live.FINAL_VISIBLE_STEPS:
            raise RawV6Conflict("FINAL_PACKET_STAGE_VISIBILITY_VIOLATION")
        if getattr(initial_packet, "d4", None) is not None:
            raise RawV6Conflict("D4_VISIBLE_BEFORE_UPDATE011")
        if getattr(final_packet, "d4", None) is None:
            raise RawV6Conflict("FINAL_D4_PACKET_MISSING")

        lineage_rt.commit(formal_tx)
        platform_rt.commit(formal_tx)
        snaps = dict(self.state.next_snapshots)
        if formal_sr.next_bar_snapshot is not None:
            snaps[formal_sr.symbol] = formal_sr.next_bar_snapshot
        result = RawV6CutoffResult(
            mode="GENESIS_FULL_TYPED_STAGED",
            engine_result=formal_result,
            trend_episode_id=trend.episode_id,
            relation=lin_proj.relation,
            coverage_statuses=static_proj.coverage_statuses,
            candidate_update_count=len(cand_result.updates),
            prebar_snapshot_count=len(pre_snaps),
            final_packet_digest=assembled.packet_digest,
            persistent_state_committed=True,
            provenance={
                "binding_id": BINDING_ID,
                "platform_binding_blob": PLATFORM_BINDING_BLOB,
                "pure_watch_binding_blob": PURE_WATCH_BINDING_BLOB,
                "d4_static_binding_blob": D4_STATIC_BINDING_BLOB,
                "d4_lineage_binding_blob": D4_LINEAGE_BINDING_BLOB,
                "assembler_blob": ASSEMBLER_BLOB,
                "v3_binding_blob": V3_BINDING_BLOB,
                "initial_packet_visible_through": "UPDATE-010",
                "final_packet_visible_from": "UPDATE-011",
                "update008_to_update002_backflow": "false",
            },
        )
        completed = dict(self.state.completed)
        completed[f"{bar.symbol}:{bar.close_time}"] = (live.digest(bar), result)
        self.state = RawV6State(
            adapter_state=formal_adapter.export_state(),
            ledger_events=formal_ledger.snapshot(),
            next_snapshots=snaps,
            assembler_state=dict(asm_rt.export_state()),
            lineage_state=lineage_rt.export_state(),
            candidate_state=cand_rt.export_state(),
            b3_state=self.state.b3_state,
            b5_state=dict(b5_rt.export_state()),
            platform_state=dict(platform_rt.export_state()),
            minor_history=minor_history,
            intermediate_history=intermediate_history,
            completed=completed,
            last_cutoff=bar.close_time,
        )
        return result


    def _mature_no_active(
        self,
        *,
        bar: Any,
        raw_result: Any,
        raw_sr: Any,
        raw_cache: Any,
    ) -> RawV6CutoffResult:
        trend = raw_cache.d2.update_006_trend
        if trend.episode_id is None or trend.episode_start_cutoff is None:
            raise RawV6Conflict("MATURE_TREND_REQUIRED")
        if trend.episode_start_cutoff >= bar.close_time:
            raise RawV6Conflict("MATURE_CUTOFF_NOT_AFTER_GENESIS")
        direction = trend.direction
        if direction not in (TrendDirection.LONG, TrendDirection.SHORT):
            raise RawV6Conflict("MATURE_DIRECTION_INVALID")

        params = frozen.frozen_d3_parameters(minimal.current_partial_parameter_snapshot())
        minor_history = _append_pivots(
            self.state.minor_history, tuple(raw_cache.d2.update_005_minor)
        )
        intermediate_history = _append_pivots(
            self.state.intermediate_history, tuple(raw_cache.d2.update_005_intermediate)
        )

        durable_d3 = self._adapter()._d3_rebuild(bar.symbol)
        pre_view = durable_d3.update_000_pre_bar_view(bar.open_time)
        pre_snaps = tuple(pre_view.snapshots)
        if pre_snaps:
            raise RawV6Block(
                "MATURE_NO_ACTIVE_RECONCILIATION_REQUIRES_ZERO_CAUSAL_PREBAR_SNAPSHOT"
            )
        pre_events = _event_rows(durable_d3)

        cand_rt = candidate_prod.D1D2D3CandidateProductionRuntimeV1.restore_state(
            self.state.candidate_state
        )
        cand_req = candidate_prod.CandidateProductionRequest(
            transaction_id=raw_sr.transaction_id + ":CANDIDATE",
            symbol=bar.symbol,
            information_cutoff=bar.close_time,
            d1=raw_cache.d1,
            target_trend=trend,
            interaction_events=pre_events,
        )
        cand_result = cand_rt.project_candidate_updates(cand_req)
        initial = live.initial_authority_from_frozen_producers(
            candidate_result=cand_result,
            snapshot_projections=(),
        )

        post_adapter, _, _, post_sr, _ = self._post_d3_shadow(bar, initial)
        if post_sr.transaction_id != raw_sr.transaction_id:
            raise RawV6Conflict("MATURE_SHADOW_TRANSACTION_ID_DRIFT")
        formal_tx = post_sr.transaction_id
        post_d3 = post_adapter._d3_rebuild(bar.symbol)
        snapshots = _snapshot_rows(post_d3)
        episodes = _episode_rows(post_d3)
        events = _event_rows(post_d3)

        candidates_by_id: dict[str, Any] = {}
        for row in cand_result.updates:
            c = row.candidate
            old = candidates_by_id.get(c.candidate_id)
            if old is not None and old != c:
                raise RawV6Conflict("DIVERGENT_CANDIDATE:" + c.candidate_id)
            candidates_by_id[c.candidate_id] = c
        candidates = tuple(candidates_by_id[k] for k in sorted(candidates_by_id))

        segment = raw_result.symbol_results[0].canonical_segment_id
        if not segment:
            segment = post_adapter._state(bar.symbol).last_canonical_segment_id
        if not segment:
            raise RawV6Block("CURRENT_CANONICAL_SEGMENT_REQUIRED")
        continuity = self._continuity_map(candidates, segment)

        segment_by_anchor: dict[str, str] = {}
        for ep in episodes:
            matching = [
                c.source_segment_id for c in candidates
                if c.candidate_id == ep.candidate_id
            ]
            if len(set(matching)) > 1:
                raise RawV6Conflict(
                    "ANCHOR_CANDIDATE_SEGMENT_CONFLICT:" + ep.anchor_episode_id
                )
            if matching:
                segment_by_anchor[ep.anchor_episode_id] = matching[0]

        corridor_info = raw_cache.d2.update_009_structural_corridor
        corridor = (
            corridor_info.require_known()
            if corridor_info.kind is InfoKind.KNOWN
            else None
        )
        protected = trend.protected_pivot
        base_u8 = b5prod.Update008Request(
            information_cutoff=bar.close_time,
            trend_episode_id=trend.episode_id,
            direction=direction,
            snapshots=snapshots,
            candidates=candidates,
            episodes=episodes,
            events=events,
            progress_evidence=(),
            negotiation_identity_by_event_id={},
            canonical_segment_id_by_anchor_episode_id=segment_by_anchor,
            continuity_by_candidate_id=continuity,
            corridor=corridor,
            protected_price=None if protected is None else protected.extreme_price,
            protected_scale=None if protected is None else protected.scale_at_extreme,
            theta_test=params.theta_test,
            theta_progress=params.theta_progress,
            provenance={
                "producer_id": BINDING_ID,
                "f9_stage": "UPDATE-008",
                "no_update002_backflow": "true",
                "runtime_contract_id": b5prod.RUNTIME_CONTRACT_ID,
            },
        )
        qid_proj = qid.project_negotiation_identity(
            qid.NegotiationIdentityRequest(
                information_cutoff=bar.close_time,
                trend_episode_id=trend.episode_id,
                direction=direction,
                events=events,
                episodes=episodes,
                continuity_by_candidate_id=continuity,
                theta_test=params.theta_test,
                rearm_predecessor_by_event_id={},
                history_complete=True,
                provenance={"producer_id": BINDING_ID},
            )
        )
        if qid_proj.status != qid.STATUS_KNOWN:
            raise RawV6Block(
                "MATURE_NEGOTIATION_IDENTITY_NOT_KNOWN:" + str(qid_proj.reason)
            )
        u8_qid = qid.bind_update008_request(base_u8, qid_proj)
        qprog_proj = qprog.project_qbu_progress_evidence(
            qprog.QBUProgressProductionRequest(
                update008_request=u8_qid,
                all_minor=minor_history,
                trend_episode_start_cutoff=trend.episode_start_cutoff,
                trend_episode_terminal_cutoff=None,
                history_complete=True,
                history_coverage_ref="V6:MINOR_HISTORY:" + trend.episode_id,
                theta_progress_parameter_ref="PARAM:theta_progress",
                provenance={"producer_id": BINDING_ID},
            )
        )
        if qprog_proj.state is not EvidenceState.TRUE:
            raise RawV6Block("MATURE_QBU_PROGRESS_NOT_TRUE")
        u8_req = qprog.bind_update008_request(u8_qid, qprog_proj)

        b5_rt = b5prod.AuthoritativeD3B5D4BaseRuntimeV1.restore_state(
            dict(self.state.b5_state)
        )
        prior_role_memory = b5_rt._role_memory.get(trend.episode_id)
        u8_out = b5_rt.process_update008(formal_tx + ":U8", u8_req)
        if u8_out.roles is None:
            raise RawV6Block("MATURE_UPDATE008_ROLE_ASSIGNMENT_MISSING")
        cand_rt.record_post_update008_role_transition(
            candidate_prod.PostUpdate008RoleTransitionRequest(
                transaction_id=formal_tx + ":ROLE",
                information_cutoff=bar.close_time,
                role_assignment=u8_out.roles,
                prior_role_memory=prior_role_memory,
                anchor_episodes=tuple(u8_out.episodes),
            )
        )

        platform_rt = platform_prod.PlatformFailedReexpansionProductionRuntimeV1.restore_state(
            dict(self.state.platform_state)
        )
        current_d1 = raw_cache.d1.math_15m[-1]
        platform_projection = platform_rt.prepare(
            formal_tx,
            platform_prod.PlatformProductionRequest(
                information_cutoff=bar.close_time,
                symbol=bar.symbol,
                trend_episode_id=trend.episode_id,
                direction=direction,
                trend_state=trend,
                all_minor=minor_history,
                events=events,
                episodes=episodes,
                canonical_segment_id_by_anchor_episode_id=segment_by_anchor,
                continuity_by_candidate_id=continuity,
                rearm_predecessor_by_event_id={},
                rearm_cutoff_by_event_id={},
                canonical_continuity=True,
                atr14_at_confirmation=InfoValue.known(current_d1.atr14),
                theta_progress=params.theta_progress,
                theta_progress_parameter_ref="PARAM:theta_progress",
                history_complete=True,
                history_coverage_ref="V6:RAW_D2_HISTORY:" + trend.episode_id,
                current_close=bar.close,
                setup_lineage=(),
                provenance={"producer_id": BINDING_ID},
            ),
        )
        if platform_projection.state in (EvidenceState.UNKNOWN, EvidenceState.CONFLICT):
            raise RawV6Block("MATURE_PLATFORM_SURFACE_NOT_COMPLETE")
        if platform_projection.platform_reexpansion_evidence is not None:
            raise RawV6Block(
                "MATURE_NO_ACTIVE_RECONCILIATION_NOT_APPLICABLE_PLATFORM_ACTIVE"
            )

        mechanisms = assembler.MechanismProducerOutputs()
        lineage_rt = lineage_prod.D4MarketEventLineageProductionProjectorV2.restore_state(
            self.state.lineage_state
        )
        existing_opportunity = self._adapter()._state(bar.symbol).current_opportunity
        if existing_opportunity is None or existing_opportunity.terminal:
            raise RawV6Block("MATURE_ACTIVE_WATCH_ORIGIN_OPPORTUNITY_REQUIRED")
        prior_lineage_ledger = lineage_rt.ledger_for(
            bar.symbol, trend.episode_id, direction
        )
        if prior_lineage_ledger is None:
            raise RawV6Block("MATURE_PRIOR_LINEAGE_LEDGER_REQUIRED")

        lineage_req = lineage_prod.D4LineageProductionRequest(
            symbol=bar.symbol,
            information_cutoff=bar.close_time,
            trend_episode_id=trend.episode_id,
            direction=direction,
            canonical_continuity_known=True,
            canonical_continuity_intact=True,
            active_mechanisms=(),
            trend_establishment_record=None,
            existing_opportunity=existing_opportunity,
            interaction_events=events,
            runtime_b3_results=(),
            local_control_regain_results=(),
            mechanisms=mechanisms,
            anchor_episode_ids=tuple(ep.anchor_episode_id for ep in episodes),
            future_evidence_detected=False,
            provenance={"producer_id": BINDING_ID},
        )
        lin_proj = lineage_rt.prepare(formal_tx, lineage_req)
        if lin_proj.status != "NO_ACTIVE_D4_OBSERVATION" or lin_proj.relation is not None:
            lineage_rt.abort(formal_tx)
            platform_rt.abort(formal_tx)
            raise RawV6Block("MATURE_LINEAGE_NOT_EXACT_NO_ACTIVE")

        coverage_ref = str(prior_lineage_ledger["coverage_ref"])
        coverage = d4static.D4CriticalCoverageProof(
            raw_and_d2_state=d4static.SourceCoverageFact(
                "COMPLETE",
                (
                    "CanonicalBar:" + str(bar.open_time),
                    "D1Math15M:" + str(bar.close_time),
                    "TrendEpisode:" + trend.episode_id,
                ),
                provenance={"producer_id": BINDING_ID},
            ),
            d3_candidate_and_runtime_b3=d4static.SourceCoverageFact(
                "COMPLETE",
                (
                    "CandidateBatch:" + cand_result.output_digest,
                    "RuntimeB3:NOT_APPLICABLE_NO_CAUSAL_PREBAR_SNAPSHOT",
                ),
                provenance={"prebar_snapshot_count": "0"},
            ),
            d2_b4_d4_causal_projections=d4static.SourceCoverageFact(
                "COMPLETE",
                ("B4:NOT_APPLICABLE_NO_ACTIVE_PREBAR_INTERACTION",),
                provenance={"producer_id": BINDING_ID},
            ),
            update008_d3_b5_state=d4static.SourceCoverageFact(
                "COMPLETE",
                ("Update008:" + formal_tx,),
                provenance={"producer_id": BINDING_ID},
            ),
            d4_mechanism_source_coverage=d4static.SourceCoverageFact(
                "COMPLETE",
                (
                    "Mechanism:WATCH:NOT_APPLICABLE_MATURE_NON_GENESIS",
                    "Mechanism:NORMAL:NOT_APPLICABLE_NO_CAUSAL_PREBAR_SNAPSHOT",
                    "Mechanism:FBR:NOT_APPLICABLE_NO_ACTIVE_PREBAR_INTERACTION",
                    "Mechanism:PLATFORM:EVALUATED_FALSE",
                    "Mechanism:DEEP:NOT_APPLICABLE_NO_CAUSAL_PREBAR_SNAPSHOT",
                ),
                provenance={"producer_id": BINDING_ID},
            ),
            d4_market_event_lineage=d4static.SourceCoverageFact(
                "COMPLETE",
                (
                    coverage_ref,
                    "LineageStatus:NO_ACTIVE_D4_OBSERVATION",
                ),
                provenance={"producer_id": BINDING_ID},
            ),
            future_evidence_detected=False,
            provenance={"producer_id": BINDING_ID},
        )
        static_req = d4static.D4StaticAssociationRequest(
            information_cutoff=bar.close_time,
            trend_episode_id=trend.episode_id,
            direction=direction,
            trend=trend,
            trend_position=raw_cache.d2.update_009_trend_position,
            update008_output=u8_out,
            mechanisms=mechanisms,
            lineage_projection=lin_proj,
            coverage=coverage,
            provenance={"producer_id": BINDING_ID},
        )
        static_proj = maturenoactive.project_mature_no_active_coverage(
            static_req,
            reconciliation_context=maturenoactive.MatureNoActiveReconciliationContext(
                lineage_request=lineage_req,
                prior_lineage_ledger=prior_lineage_ledger,
                causal_prebar_snapshot_ids=tuple(s.snapshot_id for s in pre_snaps),
                provenance={"producer_id": BINDING_ID},
            ),
        )
        if (
            static_proj.status != "READY_NO_D4_OBSERVATION"
            or not static_proj.applies
            or static_proj.critical_information_known != InfoValue.known(True)
            or static_proj.detector_evidence_ids
            or static_proj.d4_static_authority is not None
        ):
            lineage_rt.abort(formal_tx)
            platform_rt.abort(formal_tx)
            raise RawV6Block(
                "MATURE_NO_ACTIVE_COVERAGE_NOT_READY:"
                + str(static_proj.blocked_reason or static_proj.status)
            )

        asm_rt = assembler.AuthoritativeD3D4PacketAssemblerV2.restore_state(
            dict(self.state.assembler_state)
        )
        initial_packet = asm_rt.begin(initial)
        if getattr(initial_packet, "d4", None) is not None:
            raise RawV6Conflict("MATURE_INITIAL_PACKET_D4_MUST_BE_NONE")

        formal_adapter = self._adapter()
        formal_ledger = self._ledger()
        session = _PreassembledPacketSession(
            formal_adapter, initial_packet, initial_packet
        )
        engine = minimal.DeterministicCutoffEngine(
            adapters=session.registry(),
            ledger=formal_ledger,
        )
        formal_result = engine.run_cutoff_batch((self._input(bar),))
        formal_sr = formal_result.symbol_results[0]
        if formal_sr.transaction_id != formal_tx:
            raise RawV6Conflict("MATURE_FORMAL_TRANSACTION_ID_DRIFT")

        if formal_result.terminal in (
            minimal.TransactionTerminal.ABORTED_ERROR,
            minimal.TransactionTerminal.ABORTED_AMBIGUITY,
        ):
            lineage_rt.abort(formal_tx)
            platform_rt.abort(formal_tx)
            return RawV6CutoffResult(
                mode="MATURE_NO_ACTIVE_ABORTED",
                engine_result=formal_result,
                trend_episode_id=trend.episode_id,
                relation=None,
                coverage_statuses=static_proj.coverage_statuses,
                candidate_update_count=len(cand_result.updates),
                prebar_snapshot_count=0,
                final_packet_digest=assembler.digest(initial_packet),
                persistent_state_committed=False,
                blocker="FORMAL_STAGED_ENGINE_ABORT",
                provenance={
                    "binding_id": BINDING_ID,
                    "mature_no_active_binding_blob": MATURE_NO_ACTIVE_BINDING_BLOB,
                    "abort_is_atomic": "true",
                    "scientific_update008_state": getattr(u8_out.state, "value", str(u8_out.state)),
                    "scientific_lineage_relation": "NONE",
                    "synthetic_d4_packet_created": "false",
                },
            )

        if tuple(session.initial_steps) != live.INITIAL_VISIBLE_STEPS:
            raise RawV6Conflict("MATURE_INITIAL_PACKET_STAGE_VISIBILITY_VIOLATION")
        if tuple(session.final_steps) != live.FINAL_VISIBLE_STEPS:
            raise RawV6Conflict("MATURE_FINAL_PACKET_STAGE_VISIBILITY_VIOLATION")
        if getattr(initial_packet, "d4", None) is not None:
            raise RawV6Conflict("MATURE_SYNTHETIC_D4_PACKET")
        u11 = next(x for x in formal_sr.stages if x.step.value == "UPDATE-011")
        if u11.state is not frozen.StageState.NA or u11.reason != "NO_D4_EVIDENCE_PACKET":
            raise RawV6Conflict("MATURE_UPDATE011_NOT_NA_WITHOUT_D4_PACKET")
        after_opportunity = formal_adapter._state(bar.symbol).current_opportunity
        if after_opportunity != existing_opportunity:
            raise RawV6Conflict("MATURE_NO_ACTIVE_MUTATED_EXISTING_OPPORTUNITY")

        lineage_rt.commit(formal_tx)
        platform_rt.commit(formal_tx)
        committed_ledger = lineage_rt.ledger_for(
            bar.symbol, trend.episode_id, direction
        )
        if committed_ledger is None:
            raise RawV6Conflict("MATURE_LINEAGE_LEDGER_COMMIT_MISSING")
        if committed_ledger["last_evaluated_cutoff"] != bar.close_time:
            raise RawV6Conflict("MATURE_LINEAGE_LEDGER_CUTOFF_NOT_ADVANCED")
        if committed_ledger["admission_count"] != prior_lineage_ledger["admission_count"]:
            raise RawV6Conflict("MATURE_NO_ACTIVE_CHANGED_ADMISSION_COUNT")

        snaps = dict(self.state.next_snapshots)
        if formal_sr.next_bar_snapshot is not None:
            snaps[formal_sr.symbol] = formal_sr.next_bar_snapshot
        result = RawV6CutoffResult(
            mode="MATURE_NO_ACTIVE_FULL_TYPED_STAGED",
            engine_result=formal_result,
            trend_episode_id=trend.episode_id,
            relation=None,
            coverage_statuses=static_proj.coverage_statuses,
            candidate_update_count=len(cand_result.updates),
            prebar_snapshot_count=0,
            final_packet_digest=assembler.digest(initial_packet),
            persistent_state_committed=True,
            provenance={
                "binding_id": BINDING_ID,
                "mature_no_active_binding_blob": MATURE_NO_ACTIVE_BINDING_BLOB,
                "update008_engineering_coverage": "COMPLETE_NOT_APPLICABLE_ROLE_STATE",
                "lineage_engineering_coverage": "COMPLETE_NO_ACTIVE_D4_OBSERVATION_NO_RELATION_REQUIRED",
                "critical_information_known": "KNOWN_TRUE",
                "scientific_update008_state": getattr(u8_out.state, "value", str(u8_out.state)),
                "scientific_lineage_relation": "NONE",
                "detector_evidence_ids": "EMPTY",
                "synthetic_d4_packet_created": "false",
                "initial_packet_visible_through": "UPDATE-010",
                "no_d4_packet_visible_from_update011": "true",
                "lineage_commit_after_full_staged_success": "true",
            },
        )
        completed = dict(self.state.completed)
        completed[f"{bar.symbol}:{bar.close_time}"] = (live.digest(bar), result)
        self.state = RawV6State(
            adapter_state=formal_adapter.export_state(),
            ledger_events=formal_ledger.snapshot(),
            next_snapshots=snaps,
            assembler_state=dict(asm_rt.export_state()),
            lineage_state=lineage_rt.export_state(),
            candidate_state=cand_rt.export_state(),
            b3_state=self.state.b3_state,
            b5_state=dict(b5_rt.export_state()),
            platform_state=dict(platform_rt.export_state()),
            minor_history=minor_history,
            intermediate_history=intermediate_history,
            completed=completed,
            last_cutoff=bar.close_time,
        )
        return result

    def run_cutoff(self, bar: Any) -> RawV6CutoffResult:
        if self.state.last_cutoff is not None and bar.close_time <= self.state.last_cutoff:
            prior = self.state.completed.get(f"{bar.symbol}:{bar.close_time}")
            if prior is not None and prior[0] == live.digest(bar):
                return prior[1]
            raise RawV6Block("NON_MONOTONIC_OR_DUPLICATE_CUTOFF")

        raw_adapter, raw_ledger, raw_result, raw_sr, raw_cache = self._raw_shadow(bar)
        trend = raw_cache.d2.update_006_trend

        if trend.episode_id is None:
            result = RawV6CutoffResult(
                mode="RAW_PRETREND",
                engine_result=raw_result,
                trend_episode_id=None,
                relation=None,
                provenance={
                    "binding_id": BINDING_ID,
                    "typed_d4_not_applicable": "true",
                },
            )
            return self._commit_raw(
                bar=bar,adapter=raw_adapter,ledger=raw_ledger,
                engine_result=raw_result,cache=raw_cache,result=result,
            )

        if trend.episode_start_cutoff == bar.close_time:
            return self._genesis(
                bar=bar,raw_result=raw_result,raw_sr=raw_sr,raw_cache=raw_cache
            )

        return self._mature_no_active(
            bar=bar,
            raw_result=raw_result,
            raw_sr=raw_sr,
            raw_cache=raw_cache,
        )

    def export_state(self) -> str:
        payload = {
            "schema": self.STATE_SCHEMA,
            "adapter_state": self.state.adapter_state,
            "ledger_events": live._encode(self.state.ledger_events),
            "next_snapshots": live._encode(self.state.next_snapshots),
            "assembler_state": live._encode(dict(self.state.assembler_state)),
            "lineage_state": self.state.lineage_state,
            "candidate_state": self.state.candidate_state,
            "b3_state": self.state.b3_state,
            "b5_state": live._encode(dict(self.state.b5_state)),
            "platform_state": live._encode(dict(self.state.platform_state)),
            "minor_history": live._encode(self.state.minor_history),
            "intermediate_history": live._encode(self.state.intermediate_history),
            "completed": live._encode(self.state.completed),
            "last_cutoff": self.state.last_cutoff,
            "governance": {
                "real_market_data_read": False,
                "test": "NOT_AUTHORIZED",
                "outcome_read": False,
                "pnl": False,
                "forward_observation": "NOT_ACTIVE",
                "trading": "FORBIDDEN",
                "production_runtime_usable_claim": False,
            },
        }
        return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    @classmethod
    def restore_state(cls, raw: str) -> "LiveRuntimeRawAuthorityOrchestrationV6":
        try:
            p = json.loads(raw)
        except Exception as exc:
            raise RawV6Conflict("STATE_JSON_INVALID") from exc
        if p.get("schema") != cls.STATE_SCHEMA:
            raise RawV6Conflict("STATE_SCHEMA_MISMATCH")
        gov = p.get("governance") or {}
        if (
            gov.get("real_market_data_read") is not False
            or gov.get("test") != "NOT_AUTHORIZED"
            or gov.get("outcome_read") is not False
            or gov.get("pnl") is not False
            or gov.get("forward_observation") != "NOT_ACTIVE"
            or gov.get("trading") != "FORBIDDEN"
            or gov.get("production_runtime_usable_claim") is not False
        ):
            raise RawV6Conflict("STATE_GOVERNANCE_MISMATCH")
        state = RawV6State(
            adapter_state=str(p["adapter_state"]),
            ledger_events=tuple(live._decode(p["ledger_events"])),
            next_snapshots=dict(live._decode(p["next_snapshots"])),
            assembler_state=dict(live._decode(p["assembler_state"])),
            lineage_state=str(p["lineage_state"]),
            candidate_state=str(p["candidate_state"]),
            b3_state=str(p["b3_state"]),
            b5_state=dict(live._decode(p["b5_state"])),
            platform_state=dict(live._decode(p["platform_state"])),
            minor_history=tuple(live._decode(p["minor_history"])),
            intermediate_history=tuple(live._decode(p["intermediate_history"])),
            completed=dict(live._decode(p["completed"])),
            last_cutoff=p.get("last_cutoff"),
        )
        out = cls(state)
        out._adapter()
        assembler.AuthoritativeD3D4PacketAssemblerV2.restore_state(dict(state.assembler_state))
        lineage_prod.D4MarketEventLineageProductionProjectorV2.restore_state(state.lineage_state)
        candidate_prod.D1D2D3CandidateProductionRuntimeV1.restore_state(state.candidate_state)
        b3prod.RuntimeB3PriceDrivenReturnProducerV1.restore_state(state.b3_state)
        b5prod.AuthoritativeD3B5D4BaseRuntimeV1.restore_state(dict(state.b5_state))
        platform_prod.PlatformFailedReexpansionProductionRuntimeV1.restore_state(dict(state.platform_state))
        return out

    def state_digest(self) -> str:
        return sha256(self.export_state().encode("utf-8")).hexdigest()
