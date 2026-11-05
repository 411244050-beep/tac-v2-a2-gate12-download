"""Frozen original QBU identity + Minor progress vs AST-only static namespace.

Original modules load unchanged using strategy_rc1 import shims bound to the
same 91 original frozen class definitions that power the native candidate.
The namespaced result uses only same-file source; no Binance SDK interaction.
Differences in module/class names are excluded from semantic comparison.
"""
from __future__ import annotations

import ast
from dataclasses import replace
from fractions import Fraction
import importlib.util
from pathlib import Path
import sys
import types
import unittest

from build_frozen_qbu_namespace_v1 import HERE,SOURCE,OUT,build


def stub_sdk():
    for name in ("binance","binance.strategy","binance.strategy.runtime",
                 "binance.strategy.node","binance.strategy.node.capabilities",
                 "binance.strategy.node.capabilities.data"):
        m=types.ModuleType(name)
        m.__path__=[]
        sys.modules[name]=m
    r=sys.modules["binance.strategy.runtime"]
    r.node=lambda name:lambda fn:fn
    r.workflow=lambda fn:fn
    r.ctx=types.SimpleNamespace(state={},exception=lambda *a,**k:None)
    sys.modules["binance.strategy.node.capabilities.data"].kline_stream=lambda **k:None


def add_import_shims(source_ns):
    # Only original source names, never custom science stubs.
    froms=[]
    for filename in ("authoritative_d3_b5_d4_base_runtime_producers_v1.py",
                     "qbu_same_event_negotiation_identity_production_binding_v1.py",
                     "qbu_material_trend_side_minor_progress_production_binding_v1.py"):
        tree=ast.parse((SOURCE/filename).read_text())
        for node in tree.body:
            if isinstance(node,ast.ImportFrom) and (
                    (node.module or "").startswith("strategy_rc1")
                    or node.module=="d2_to_b4_d4_causal_evidence_producers_v1"):
                froms.append(node)
    for node in froms:
        module=node.module
        prefix=""
        for part in module.split("."):
            prefix=part if not prefix else prefix+"."+part
            if prefix not in sys.modules:
                shim=types.ModuleType(prefix)
                shim.__path__=[]
                sys.modules[prefix]=shim
        obj=sys.modules[module]
        for alias in node.names:
            if not hasattr(source_ns,alias.name):
                raise ValueError("MISSING_ORIGINAL_SOURCE_SHIM:"+module+":"+alias.name)
            setattr(obj,alias.name,getattr(source_ns,alias.name))


def fetch_original_module(name):
    path=SOURCE/(name+".py")
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod
    spec.loader.exec_module(mod)
    return mod


def load():
    stub_sdk()
    src=(HERE/"strategy/strategy.py").read_text()+"\n"+(
         HERE/"RUNTIME_B3_FROZEN_ORIGINAL_PRODUCER_APPEND_V1.py").read_text()+"\n"+(
         HERE/"B4_FROZEN_ORIGINAL_PRODUCER_APPEND_V1.py").read_text()+"\n"+OUT.read_text()
    flat=types.ModuleType("tac_frozen_QBU_static_source_ci")
    sys.modules[flat.__name__]=flat
    exec(compile(src,"tac_frozen_QBU_static_source_ci.py","exec"),vars(flat))
    add_import_shims(flat)
    base=fetch_original_module("authoritative_d3_b5_d4_base_runtime_producers_v1")
    ident=fetch_original_module("qbu_same_event_negotiation_identity_production_binding_v1")
    prog=fetch_original_module("qbu_material_trend_side_minor_progress_production_binding_v1")
    return flat,base,ident,prog


def evt(m,eid="E1",cid="C1",aid="A1",start=10,end=20):
    return m.InteractionEvent(
        event_id=eid,candidate_id=cid,anchor_episode_id=aid,
        target_trend_episode_id="TE-1",
        target_direction=m.TrendDirection.LONG,
        control=m.InteractionControl.RESOLVED,
        resolution=m.InteractionResolution.RESOLVED_CORRECT_SIDE,
        event_reference_boundary=Fraction(100),
        event_reference_scale=Fraction(10),
        started_at=start,resolved_at=end,
        armed_at=start-2,approach_lineage_started_at=start-1,
        attempted_wrong_side_acceptance=False,
        material_wrong_side_separation_observed=False,
        reclaim_observed=False,break_state=m.BreakState.NONE,
        terminal=False,provenance={"fixture":"SYNTHETIC_ORIGINAL_QBU"})


def episode(m,eid="E1",cid="C1",aid="A1"):
    return m.AnchorEpisode(
        anchor_episode_id=aid,candidate_id=cid,
        target_trend_episode_id="TE-1",
        target_direction=m.TrendDirection.LONG,
        validity=m.AnchorValidity.VALID,
        activity=m.AnchorActivity.ACTIVE,
        started_at=1,ended_at=None,
        interaction_event_ids=(eid,),qualified_uses=(),
        terminal_true_break=False,dossier=m.empty_dossier(),
        provenance={"fixture":"SYNTHETIC_ORIGINAL_QBU"})


def pivot(m,pid,price,at):
    return m.StructuralPivot(
        pivot_id=pid,symbol="SYNTH",timeframe_ms=900000,
        layer=m.StructuralLayer.MINOR,pivot_type=m.PivotType.HIGH,
        extreme_price=Fraction(price),extreme_first_time=at-2,
        extreme_last_time=at-1,confirmed_at=at,
        scale_at_extreme=Fraction(10),
        canonical_segment_id="SEG",source_pivot_ids=(),
        provenance={"fixture":"SYNTHETIC_ORIGINAL_MINOR"})


def req_base(m,cls,*,events=None,episodes=None,continuity=True,cutoff=30):
    return cls(
        information_cutoff=cutoff,trend_episode_id="TE-1",
        direction=m.TrendDirection.LONG,
        snapshots=(),candidates=(),
        episodes=(episode(m),) if episodes is None else episodes,
        events=(evt(m),) if events is None else events,
        progress_evidence=(),
        negotiation_identity_by_event_id={},
        canonical_segment_id_by_anchor_episode_id={"A1":"SEG"},
        continuity_by_candidate_id={"C1":continuity},
        corridor=None,protected_price=None,protected_scale=None,
        theta_test=Fraction(1,10),
        theta_progress=Fraction(1,2),
        provenance={"fixture":"SYNTHETIC_ORIGINAL_QBU"})


def semantic_identity(out):
    return (out.status,dict(out.negotiation_identity_by_event_id),
            tuple(out.component_members),tuple(out.unknown_refs),
            tuple(out.conflict_refs),out.reason,dict(out.provenance))


def semantic_progress(out):
    lines=[]
    for rec in out.progress_evidence:
        lines.append((
            rec.event_id,rec.progress.pivot_id,rec.progress.confirmed_at,
            rec.progress.material_progress,rec.target_trend_episode_id,
            rec.direction.value,rec.canonical_segment_id,
            rec.continuity_intact,dict(rec.provenance)))
    return (out.state.value,tuple(lines),tuple(out.unknown_refs),
            tuple(out.conflict_refs),dict(out.provenance))


class OriginalFrozenQBUParity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.flat,cls.base,cls.identity,cls.progress=load()

    def test_original_science_AST_three_modules(self):
        code,records=build()
        self.assertEqual(code,OUT.read_text())
        self.assertEqual(len(records),3)
        self.assertEqual(sum(r["scientific_definitions_preserved"] for r in records),
                         76)
        self.assertTrue(hasattr(self.flat,"TAC_BASE_produce_update008"))
        self.assertTrue(hasattr(self.flat,"TAC_ID_bind_update008_request"))
        self.assertTrue(hasattr(self.flat,"TAC_PR_bind_update008_request"))

    def test_identity_known_and_shared_component(self):
        got=[]
        for x in ("original","flat"):
            m=self.flat
            id_mod=self.identity if x=="original" else m
            cls=self.identity.NegotiationIdentityRequest if x=="original" else m.TAC_ID_NegotiationIdentityRequest
            call=self.identity.project_negotiation_identity if x=="original" else m.TAC_ID_project_negotiation_identity
            events=(evt(m,"E1","C1","A1",10,20),
                    evt(m,"E2","C2","A2",15,25))
            episodes=(episode(m,"E1","C1","A1"),
                      episode(m,"E2","C2","A2"))
            req=cls(information_cutoff=40,trend_episode_id="TE-1",
                direction=m.TrendDirection.LONG,events=events,
                episodes=episodes,
                continuity_by_candidate_id={"C1":True,"C2":True},
                theta_test=Fraction(1,10),
                history_complete=True,
                provenance={"fixture":"SYNTHETIC_ORIGINAL_QBU"})
            out=call(req)
            self.assertEqual(out.status,"KNOWN")
            self.assertEqual(out.negotiation_identity_by_event_id["E1"],
                             out.negotiation_identity_by_event_id["E2"])
            got.append(semantic_identity(out))
        self.assertEqual(got[0],got[1])

    def test_identity_unknown_future_conflict(self):
        for mode in ("unknown","future","divergent"):
            got=[]
            for src in ("original","flat"):
                m=self.flat
                cls=self.identity.NegotiationIdentityRequest if src=="original" else m.TAC_ID_NegotiationIdentityRequest
                call=self.identity.project_negotiation_identity if src=="original" else m.TAC_ID_project_negotiation_identity
                events=(evt(m),)
                complete=True
                if mode=="unknown":complete=False
                if mode=="future":events=(evt(m,end=50),)
                if mode=="divergent":events=(evt(m),evt(m,end=21))
                req=cls(information_cutoff=40,trend_episode_id="TE-1",
                    direction=m.TrendDirection.LONG,
                    events=events,episodes=(episode(m),),
                    continuity_by_candidate_id={"C1":True},
                    theta_test=Fraction(1,10),
                    history_complete=complete)
                out=call(req)
                self.assertEqual(out.status,"UNKNOWN" if mode=="unknown" else "CONFLICT")
                got.append(semantic_identity(out))
            self.assertEqual(got[0],got[1],mode)

    def test_minor_material_progress_positive_and_unknown(self):
        for mode in ("material","not_material","no_prior","incomplete","bad_continuity"):
            got=[]
            for source in ("original","flat"):
                m=self.flat
                req_cls=self.base.Update008Request if source=="original" else m.TAC_BASE_Update008Request
                progress_cls=self.progress.QBUProgressProductionRequest if source=="original" else m.TAC_PR_QBUProgressProductionRequest
                calculate=self.progress.project_qbu_progress_evidence if source=="original" else m.TAC_PR_project_qbu_progress_evidence
                continuity=None if mode=="bad_continuity" else True
                base=req_base(m,req_cls,continuity=continuity)
                pivots=(pivot(m,"H0",100,15),pivot(m,"H1",120,30))
                if mode=="not_material":pivots=(pivots[0],pivot(m,"H1",102,30))
                if mode=="no_prior":pivots=pivots[1:]
                req=progress_cls(
                    update008_request=base,all_minor=pivots,
                    trend_episode_start_cutoff=1,
                    trend_episode_terminal_cutoff=None,
                    history_complete=mode!="incomplete",
                    history_coverage_ref="HIST:FULL_SYNTHETIC",
                    theta_progress_parameter_ref="THETA:SOURCE_FROZEN",
                    provenance={"fixture":"SYNTHETIC_ORIGINAL_QBU"})
                out=calculate(req)
                if mode=="material":
                    self.assertEqual(out.state.value,"TRUE")
                    self.assertEqual(len(out.progress_evidence),1)
                    self.assertTrue(out.progress_evidence[0].progress.material_progress)
                if mode in ("no_prior","incomplete","bad_continuity"):
                    self.assertNotEqual(out.state.value,"TRUE")
                got.append(semantic_progress(out))
            self.assertEqual(got[0],got[1],mode)

    def test_original_base_B5_produce_update008_no_trade(self):
        got=[]
        for src in ("original","flat"):
            m=self.flat
            cls=self.base.Update008Request if src=="original" else m.TAC_BASE_Update008Request
            call=self.base.produce_update008 if src=="original" else m.TAC_BASE_produce_update008
            request=req_base(m,cls,continuity=None)
            output,memory=call(request)
            self.assertNotEqual(output.state.value,"TRUE")
            self.assertFalse(output.produced_qbus)
            got.append((output.state.value,tuple(output.unknown_lineage_refs),
                         tuple(output.conflict_lineage_refs),
                         output.roles is None,memory is None))
        self.assertEqual(got[0],got[1])

if __name__=="__main__":
    unittest.main()
