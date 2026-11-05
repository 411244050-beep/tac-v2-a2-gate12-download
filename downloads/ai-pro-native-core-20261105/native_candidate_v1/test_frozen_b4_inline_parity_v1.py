"""Frozen original B4 vs mechanically inlined B4, same original scientific types."""
from __future__ import annotations
import ast
from dataclasses import fields,is_dataclass,replace
from fractions import Fraction
import importlib.util
from pathlib import Path
import sys
import types
import unittest

from build_frozen_b4_append_v1 import HERE,ORIGINAL,OUT,flatten_source

def stub_binance_sdk():
    for name in ("binance","binance.strategy","binance.strategy.runtime",
        "binance.strategy.node","binance.strategy.node.capabilities",
        "binance.strategy.node.capabilities.data"):
        module=types.ModuleType(name)
        module.__path__=[]
        sys.modules[name]=module
    r=sys.modules["binance.strategy.runtime"]
    r.node=lambda name:lambda fn:fn
    r.workflow=lambda fn:fn
    r.ctx=types.SimpleNamespace(state={},exception=lambda *args,**kw:None)
    sys.modules["binance.strategy.node.capabilities.data"].kline_stream=lambda **kw:None

def load():
    stub_binance_sdk()
    from build_frozen_b4_append_v1 import BASIS,B3
    src=BASIS.read_text()+"\n"+B3.read_text()+"\n"+OUT.read_text()
    ns=types.ModuleType("tac_frozen_b4_original_inline")
    sys.modules[ns.__name__]=ns
    exec(compile(src,"native_original_b4.py","exec"),vars(ns))
    # Import original frozen module unchanged, binding its strategy_rc1 imports
    # to matching core objects from the 91-module flattened source.
    original=ast.parse(ORIGINAL.read_text())
    for node in original.body:
        if not isinstance(node,ast.ImportFrom) or not (node.module or "").startswith("strategy_rc1"):
            continue
        prefix=""
        for part in node.module.split("."):
            prefix=part if not prefix else prefix+"."+part
            if prefix not in sys.modules:
                q=types.ModuleType(prefix)
                q.__path__=[]
                sys.modules[prefix]=q
        q=sys.modules[node.module]
        for alias in node.names:
            setattr(q,alias.name,getattr(ns,alias.name))
    spec=importlib.util.spec_from_file_location(
        "tac_actual_original_frozen_B4_module",ORIGINAL)
    mod=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=mod
    spec.loader.exec_module(mod)
    return ns,mod

def fixture(m,b):
    Trend=m.TrendDirection
    p0=m.StructuralPivot(
        pivot_id="P0",symbol="SYNTH",timeframe_ms=900000,
        layer=m.StructuralLayer.MINOR,pivot_type=m.PivotType.LOW,
        extreme_price=Fraction(90),extreme_first_time=15,
        extreme_last_time=15,confirmed_at=20,scale_at_extreme=Fraction(10),
        canonical_segment_id="SEG",source_pivot_ids=(),
        provenance={"fixture":"SOURCE_ONLY_TEST"})
    opp=replace(p0,pivot_id="OPP",pivot_type=m.PivotType.HIGH,
        extreme_price=Fraction(96),extreme_first_time=25,
        extreme_last_time=25,confirmed_at=30)
    p1=replace(p0,pivot_id="P1",extreme_price=Fraction(80),
        extreme_first_time=35,extreme_last_time=35,confirmed_at=40)
    ctx=b.LineageContext(symbol="SYNTH",target_trend_episode_id="TEP",
        direction=Trend.LONG,information_cutoff=50,
        canonical_segment_id="SEG",interaction_event_id="EV",
        market_event_id="MKT",source_evidence_refs=("SRC",),
        continuity_known=True,continuity_intact=True,
        same_cutoff_order_proven=True)
    event=m.InteractionEvent(
        event_id="EV",candidate_id="CAND",anchor_episode_id="ANCH",
        target_trend_episode_id="TEP",target_direction=Trend.LONG,
        control=m.InteractionControl.INTERACTION_ACTIVE,
        resolution=m.InteractionResolution.UNRESOLVED,
        event_reference_boundary=Fraction(100),
        event_reference_scale=Fraction(10),
        started_at=5,resolved_at=None,armed_at=5,
        approach_lineage_started_at=4,attempted_wrong_side_acceptance=True,
        material_wrong_side_separation_observed=True,reclaim_observed=False,
        break_state=m.BreakState.TEMPORARY_BREAK,
        terminal=False,provenance={"fixture":"TEST_ONLY_SOURCE"})
    req=b.StructuralAcceptanceRequest(context=ctx,interaction=event,
        pivots=(p0,opp,p1),separation_origin_open_time=10,
        separation_cutoff=10,theta_progress=Fraction(1,2),
        prior_reclaim_cutoffs=())
    rec=b.CorrectSideRecoveryRequest(context=ctx,interaction=event,
        pivots=(p0,opp),attempt_origin_open_time=10,
        attempt_cutoff=10,evaluating_close=Fraction(101))
    return req,rec

def normalized(result):
    ev=result.consumer_evidence
    fields_out=(None if ev is None else
        tuple((f.name,getattr(ev,f.name)) for f in fields(ev)))
    return result.state.value,result.reason,fields_out,dict(result.provenance)

class B4OriginalSourceDifferential(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.flat,cls.orig=load()

    def test_science_ast_and_no_collision(self):
        code,raw,removed=flatten_source()
        self.assertEqual(code,OUT.read_text())
        self.assertIn("duplicate frozen OBSERVER_TIMEFRAME_MS=900000",removed)
        self.assertGreater(len(raw),30000)

    def test_original_structural_acceptance_positive_and_negative(self):
        results=[]
        for b in (self.orig,self.flat):
            req,rec=fixture(self.flat,b)
            pos=b.produce_structural_acceptance(req)
            self.assertEqual(pos.state.value,"TRUE")
            self.assertTrue(pos.consumer_evidence.continuation_acceptance)
            missing=b.produce_structural_acceptance(
                replace(req,context=replace(req.context,continuity_known=False)))
            self.assertEqual(missing.state.value,"UNKNOWN")
            notyet=b.produce_structural_acceptance(
                replace(req,pivots=(req.pivots[0],req.pivots[1])))
            self.assertEqual(notyet.state.value,"UNKNOWN")
            failed=b.produce_structural_acceptance(
                replace(req,prior_reclaim_cutoffs=(35,)))
            self.assertEqual(failed.state.value,"TRUE")
            self.assertTrue(failed.consumer_evidence.failed_return_acceptance)
            conflict=b.produce_structural_acceptance(
                replace(req,context=replace(req.context,interaction_event_id="OTHER")))
            self.assertEqual(conflict.state.value,"CONFLICT")
            results.append(tuple(map(normalized,(pos,missing,notyet,failed,conflict))))
        self.assertEqual(results[0],results[1])

    def test_original_correct_side_recovery_true_false_unknown(self):
        results=[]
        for b in (self.orig,self.flat):
            req,rec=fixture(self.flat,b)
            yes=b.produce_correct_side_recovery(rec)
            self.assertEqual(yes.state.value,"TRUE")
            equal=b.produce_correct_side_recovery(replace(rec,evaluating_close=Fraction(96)))
            self.assertEqual(equal.state.value,"FALSE")
            missing=b.produce_correct_side_recovery(replace(rec,pivots=(rec.pivots[0],)))
            self.assertEqual(missing.state.value,"UNKNOWN")
            noreturn=b.produce_correct_side_recovery(
                replace(rec,interaction=replace(rec.interaction,attempted_wrong_side_acceptance=False)))
            self.assertEqual(noreturn.state.value,"UNKNOWN")
            results.append(tuple(map(normalized,(yes,equal,missing,noreturn))))
        self.assertEqual(results[0],results[1])

    def test_original_four_state_consumer_projection(self):
        for b in (self.orig,self.flat):
            req,rec=fixture(self.flat,b)
            for outcome in (
                b.produce_structural_acceptance(req),
                b.produce_structural_acceptance(replace(
                    req,context=replace(req.context,continuity_known=False))),
                b.produce_structural_acceptance(replace(
                    req,context=replace(req.context,interaction_event_id="OTHER"))),
            ):
                cv=b.projection_to_info_value(outcome)
                if outcome.state.value=="TRUE": self.assertTrue(cv.value)
                else: self.assertIsNone(b.safe_b4_consumer(outcome))


    def test_original_D2_D3_cutoff_binding_without_real_epoch_spoofing(self):
        source=(HERE/"B4_ORIGINAL_D2_PIVOT_EVENT_BINDING_V1.py").read_text()
        exec(compile(source,"B4_ORIGINAL_D2_PIVOT_EVENT_BINDING_V1.py","exec"),
             vars(self.flat))
        c=self.flat
        req,rec=fixture(c,c)
        bar=c.CanonicalBar.from_values(symbol="SYNTH",open_time=1800000000000,
            close_time=1800000899999,open="100",high="102",low="94",
            close="101")
        receipt={
            "mode":"SYNTHETIC_TEST_ONLY_FULL_SOURCE",
            "complete":True,"same_cutoff_order_proven":True,
            "canonical_continuity_intact":True,
            "source_evidence_refs":("SRC",),
            "canonical_segment_id":"SEG","market_event_id":"MKT",
            "actual_prior_reclaim_cutoffs":()}
        call=lambda b4_receipt:c._tac_original_b4_from_D2_D3_source_v1(
            bar=bar,original_d3_event=req.interaction,
            original_d2_minor_pivots=req.pivots,
            source_receipt=b4_receipt,theta_progress=Fraction(1,2),
            separation_origin_open_time=10,separation_cutoff=10,
            attempt_origin_open_time=10,attempt_cutoff=10)
        out=call(receipt)
        self.assertTrue(out["original_B4_bound"])
        self.assertEqual(out["structural_acceptance_state"],"TRUE")
        self.assertEqual(out["correct_side_recovery_state"],"TRUE")
        self.assertFalse(out["entry_ready"])
        self.assertFalse(out["trade_authorized"])
        self.assertEqual(out["orders"],0)
        blocked=call({"mode":"REAL_PROSPECTIVE","complete":False})
        self.assertEqual(blocked["status"],"BLOCKED_EPOCH_CONTINUITY_UNPROVEN")
        self.assertFalse(blocked["original_B4_bound"])
        self.assertIsNone(blocked["structural_acceptance"])
        self.assertIsNone(blocked["correct_side_recovery"])
        unknown=call({**receipt,"canonical_continuity_intact":False})
        self.assertFalse(unknown["original_B4_bound"])
        self.assertEqual(unknown["orders"],0)
        bogus=call({**receipt,"source_evidence_refs":()})
        self.assertFalse(bogus["original_B4_bound"])
        self.assertEqual(bogus["orders"],0)

if __name__=="__main__":
    unittest.main()
