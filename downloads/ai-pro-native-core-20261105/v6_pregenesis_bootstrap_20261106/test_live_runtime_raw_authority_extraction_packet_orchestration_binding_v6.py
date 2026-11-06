from __future__ import annotations

from fractions import Fraction
import json
from unittest.mock import patch

import minimal_runnable_v1_baseline as minimal
import live_runtime_raw_authority_extraction_packet_orchestration_binding_v6 as v6


TF=15*60*1000


def bar(i,x):
    q=Fraction(x)
    return minimal.CanonicalBar(
        symbol="SYNTH",open_time=i*TF,close_time=(i+1)*TF,
        open=q,high=q+3,low=q-3,close=q,
        base_volume=10,quote_volume=1000,is_closed=True,
    )


def stair(n=40):
    out=[]; x=100
    for i in range(n):
        if i%6 in (0,1,2): x+=8
        else: x-=4
        out.append(x)
    return out


def drive_to_genesis(rt):
    xs=stair()
    for i,x in enumerate(xs):
        out=rt.run_cutoff(bar(i,x))
        if out.mode=="GENESIS_FULL_TYPED_STAGED":
            return xs,i,out
        assert out.mode=="RAW_PRETREND"
    raise AssertionError("GENESIS_NOT_REACHED")


def test_raw_to_full_typed_watch_genesis_and_restart():
    rt=v6.LiveRuntimeRawAuthorityOrchestrationV6()
    xs,gi,genesis=drive_to_genesis(rt)
    assert genesis.trend_episode_id is not None
    assert getattr(genesis.relation,"value",None)=="START_FIRST_EVENT"
    assert genesis.candidate_update_count==9
    assert genesis.prebar_snapshot_count==0
    assert genesis.final_packet_digest
    assert genesis.persistent_state_committed
    assert dict(genesis.coverage_statuses)=={
        "RAW_AND_D2_STATE":"COMPLETE",
        "D3_CANDIDATE_AND_RUNTIME_B3":"COMPLETE",
        "D2_B4_D4_CAUSAL_PROJECTIONS":"COMPLETE",
        "UPDATE008_D3_B5_STATE":"COMPLETE",
        "D4_MECHANISM_SOURCE_COVERAGE":"COMPLETE",
        "D4_MARKET_EVENT_LINEAGE":"COMPLETE",
    }
    state=rt.export_state()
    restored=v6.LiveRuntimeRawAuthorityOrchestrationV6.restore_state(state)
    assert restored.export_state()==state
    assert restored.state_digest()==rt.state_digest()
    replay=restored.run_cutoff(bar(gi,xs[gi]))
    assert replay==genesis
    assert restored.export_state()==state


def test_first_post_genesis_mature_no_active_full_typed_staged():
    rt=v6.LiveRuntimeRawAuthorityOrchestrationV6()
    xs,gi,_=drive_to_genesis(rt)
    before_ledger_rt=v6.lineage_prod.D4MarketEventLineageProductionProjectorV2.restore_state(rt.state.lineage_state)
    durable=rt._adapter()
    opp_before=durable._state("SYNTH").current_opportunity
    assert opp_before is not None and not opp_before.terminal
    ledger_before=before_ledger_rt.ledger_for("SYNTH",opp_before.trend_episode_id,opp_before.direction)
    assert ledger_before is not None and ledger_before["current_origin_watch"] is True

    out=rt.run_cutoff(bar(gi+1,xs[gi+1]))
    assert out.mode=="MATURE_NO_ACTIVE_FULL_TYPED_STAGED"
    assert out.relation is None
    assert out.prebar_snapshot_count==0
    assert out.persistent_state_committed
    assert dict(out.coverage_statuses)=={
        "RAW_AND_D2_STATE":"COMPLETE",
        "D3_CANDIDATE_AND_RUNTIME_B3":"COMPLETE",
        "D2_B4_D4_CAUSAL_PROJECTIONS":"COMPLETE",
        "UPDATE008_D3_B5_STATE":"COMPLETE",
        "D4_MECHANISM_SOURCE_COVERAGE":"COMPLETE",
        "D4_MARKET_EVENT_LINEAGE":"COMPLETE",
    }
    assert out.provenance["scientific_update008_state"]=="UNKNOWN"
    assert out.provenance["scientific_lineage_relation"]=="NONE"
    assert out.provenance["synthetic_d4_packet_created"]=="false"
    assert out.provenance["critical_information_known"]=="KNOWN_TRUE"

    u11=next(x for x in out.engine_result.symbol_results[0].stages if x.step.value=="UPDATE-011")
    assert u11.state is v6.frozen.StageState.NA
    assert u11.reason=="NO_D4_EVIDENCE_PACKET"

    durable_after=rt._adapter()
    assert durable_after._state("SYNTH").current_opportunity==opp_before
    lineage_after=v6.lineage_prod.D4MarketEventLineageProductionProjectorV2.restore_state(rt.state.lineage_state)
    ledger_after=lineage_after.ledger_for("SYNTH",opp_before.trend_episode_id,opp_before.direction)
    assert ledger_after is not None
    assert ledger_after["last_evaluated_cutoff"]==bar(gi+1,xs[gi+1]).close_time
    assert ledger_after["admission_count"]==ledger_before["admission_count"]
    assert ledger_after["coverage_chain_digest"]!=ledger_before["coverage_chain_digest"]

    state=rt.export_state()
    restored=v6.LiveRuntimeRawAuthorityOrchestrationV6.restore_state(state)
    replay=restored.run_cutoff(bar(gi+1,xs[gi+1]))
    assert replay==out
    assert restored.export_state()==state


def test_mature_no_active_abort_is_zero_commit():
    rt=v6.LiveRuntimeRawAuthorityOrchestrationV6()
    xs,gi,_=drive_to_genesis(rt)
    before=rt.export_state()
    before_digest=rt.state_digest()
    original=v6._PreassembledPacketSession.adapter_for

    def sabotaged(self, step):
        base=original(self,step)
        def run(ctx):
            out=base(ctx)
            if step.value=="UPDATE-012":
                raise RuntimeError("SYNTHETIC_POST_LINEAGE_PREPARE_ABORT")
            return out
        return run

    with patch.object(v6._PreassembledPacketSession,"adapter_for",sabotaged):
        out=rt.run_cutoff(bar(gi+1,xs[gi+1]))
    assert out.mode=="MATURE_NO_ACTIVE_ABORTED"
    assert out.relation is None
    assert out.persistent_state_committed is False
    assert out.blocker=="FORMAL_STAGED_ENGINE_ABORT"
    assert rt.export_state()==before
    assert rt.state_digest()==before_digest


def test_static_firewall():
    import inspect
    src=inspect.getsource(v6).lower()
    for bad in (
        "requests","httpx","websocket","ccxt","binance",
        "theta_minor =","theta_intermediate =","theta_major =","theta_stop =",
        "fixed_cooldown=","fixed_time_window=",
    ):
        assert bad not in src
    assert "latest_establishment_evidence(" in src
    assert "project_negotiation_identity(" in src
    assert "project_qbu_progress_evidence(" in src
    assert "platformfailedreexpansionproductionruntimev1" in src
    assert "project_mature_no_active_coverage(" in src
    assert "mature_no_active_full_typed_staged" in src
    wrapper=inspect.getsource(v6.maturenoactive).lower()
    assert "d4staticauthority(" not in wrapper
    assert "eventrelation." not in wrapper
    assert "bind_d4_static_authority(" not in wrapper
    assert "synthetic_d4_packet_created" in wrapper


def run():
    tests=[
        test_raw_to_full_typed_watch_genesis_and_restart,
        test_first_post_genesis_mature_no_active_full_typed_staged,
        test_mature_no_active_abort_is_zero_commit,
        test_static_firewall,
    ]
    for fn in tests: fn()
    report={
        "schema":"TAC_LIVE_RUNTIME_RAW_AUTHORITY_PACKET_ORCHESTRATION_V6_MATURE_NO_ACTIVE_VERIFICATION",
        "status":"PASS",
        "tests":len(tests),
        "watch_genesis_regression":True,
        "mature_no_active_full_typed_staged":True,
        "mature_update008_scientific_state_unknown_preserved":True,
        "mature_lineage_relation_none_preserved":True,
        "mature_zero_synthetic_d4_packet":True,
        "mature_update011_na":True,
        "mature_existing_opportunity_preserved":True,
        "mature_lineage_ledger_advances_on_success":True,
        "mature_lineage_admission_count_unchanged":True,
        "mature_abort_zero_commit":True,
        "restart_replay":True,
        "six_class_coverage_complete":True,
        "critical_information_known_true":True,
        "causal_prebar_runtime_b3_b4_closed":False,
        "new_strategy_states":0,
        "new_numeric_thresholds":0,
        "new_fixed_time_windows":0,
        "real_market_data_read":False,
        "test_read":False,
        "test_availability_checked":False,
        "outcome_read":False,
        "pnl":False,
        "forward_observation":"NOT_ACTIVE",
        "trading":"FORBIDDEN",
        "orders":0,"fills":0,"execution_intents":0,
    }
    print("RAW_V6_MATURE_NO_ACTIVE_VERIFY="+json.dumps(report,sort_keys=True,separators=(",",":")))
    return report

if __name__=="__main__":
    run()
