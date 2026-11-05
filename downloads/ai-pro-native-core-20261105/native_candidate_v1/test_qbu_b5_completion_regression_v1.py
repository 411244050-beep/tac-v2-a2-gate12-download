"""Original TAC QBU/B5 acceptance gaps: LONG/SHORT/rearm/RoleMemory/terminal.

Both original standalone modules and exact namespaced single-file source
are executed on identical synthetic typed events, pivots and exact fractions.
No test data or positive signal is ever authorized as real market evidence.
"""
from __future__ import annotations
from dataclasses import replace
from fractions import Fraction
import unittest
from test_frozen_qbu_namespaced_parity_v1 import (
    load,evt,episode,pivot,semantic_identity,semantic_progress,req_base,HERE
)


def closed_source(m,direction,at=30,with_zones=True,prior_memory=None):
    short=direction is m.TrendDirection.SHORT
    event=replace(evt(m),
        target_direction=direction,
        event_reference_boundary=Fraction(-100 if short else 100))
    ep=replace(episode(m),target_direction=direction)
    ptype=m.PivotType.LOW if short else m.PivotType.HIGH
    prior=pivot(m,"P0",(-100 if short else 100),15)
    advance=pivot(m,"P1",(-120 if short else 120),at)
    boundary=Fraction(-100 if short else 100)
    candidate=m.MathematicalBoundaryCandidate(
        candidate_id="C1",symbol="SYNTH",source_timeframe_ms=900000,
        target_trend_episode_id="TE-1",target_direction=direction,
        family=m.CandidateFamily.EMA20,
        boundary=m.InfoValue.known(boundary),
        source_scale=m.InfoValue.known(Fraction(10)),
        source_segment_id="SEG",available_at=5,
        availability=m.CandidateAvailability.AVAILABLE,
        provenance={"fixture":"SYNTHETIC_ORIGINAL_ACCEPTANCE"})
    snapshot=m.CausalBoundarySnapshot(
        snapshot_id="SN-C1-5",candidate_id="C1",anchor_episode_id="A1",
        symbol="SYNTH",source_timeframe_ms=900000,
        target_trend_episode_id="TE-1",target_direction=direction,
        family=m.CandidateFamily.EMA20,
        boundary=boundary,source_scale=Fraction(10),
        source_segment_id="SEG",available_at=5,
        provenance={"fixture":"SYNTHETIC_ORIGINAL_ACCEPTANCE"})
    # No fabricated market inputs: these are deliberate synthetic complete
    # fixtures for code parity only, not authentic D1/D2 source observations.
    fact={
        "mode":"SYNTHETIC_TEST_ONLY_FULL_SOURCE",
        "history_complete":True,"provenance_complete":True,
        "same_cutoff_order_proven":True,"continuity_intact":True,
        "real_epoch_authorized":False,
        "synthetic_coverage_ref":"COMPLETE-SYNTHETIC-ONLY",
        "actual_rearm_predecessor_by_event_id":{}}
    return dict(
        symbol="SYNTH",information_cutoff=at,
        trend_episode_id="TE-1",direction=direction,
        source_receipt=fact,
        snapshots=(snapshot,) if with_zones else (),
        candidates=(candidate,) if with_zones else (),
        anchor_episodes=(ep,),interaction_events=(event,),
        all_original_d2_minor=(replace(prior,pivot_type=ptype),
            replace(advance,pivot_type=ptype)),
        canonical_segment_id_by_anchor_episode_id={"A1":"SEG"},
        continuity_by_candidate_id={"C1":True},
        corridor=m.StructuralCorridor(Fraction(-130 if short else 80),
                                      Fraction(-80 if short else 130)),
        protected_price=Fraction(-115 if short else 115),
        protected_scale=Fraction(2),trend_episode_start_cutoff=1,
        prior_role_memory=prior_memory)


class FrozenQBUCompletionDifferential(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m,cls.original_base,cls.original_id,cls.original_minor=load()
        code=(HERE/"QBU_B5_ORIGINAL_EVIDENCE_CUTOFF_BINDING_V1.py").read_text()
        exec(compile(code,"QBU_B5_ORIGINAL_EVIDENCE_CUTOFF_BINDING_V1.py","exec"),
             vars(cls.m))

    def test_long_positive_qbu_role_and_unchanged_evidence(self):
        m=self.m
        kwargs=closed_source(m,m.TrendDirection.LONG)
        result=m._tac_original_qbu_b5_synthetic_cutoff_v1(**kwargs)
        self.assertEqual(result["status"],"SYNTHETIC_ORIGINAL_QBU_B5_EVALUATED")
        self.assertEqual(result["minor_progress_status"],"TRUE")
        self.assertEqual(result["negotiation_identity_status"],"KNOWN")
        self.assertEqual(result["B5_state"],"TRUE")
        self.assertEqual(len(result["original_qbus"]),1)
        self.assertEqual(len(result["original_boundaries"]),1)
        self.assertIsNotNone(result["original_roles"])
        self.assertIsNotNone(result["original_roles"].primary_unit_id)
        self.assertIsNone(result["original_roles"].secondary_unit_id)
        self.assertIsNotNone(result["next_original_role_memory"])
        self.assertFalse(result["entry_ready"])
        self.assertFalse(result["trade_authorized"])
        self.assertEqual(result["orders"],0)

    def test_short_mirror_positive_real_original_roles(self):
        m=self.m
        result=m._tac_original_qbu_b5_synthetic_cutoff_v1(
            **closed_source(m,m.TrendDirection.SHORT))
        self.assertEqual(result["status"],"SYNTHETIC_ORIGINAL_QBU_B5_EVALUATED")
        self.assertEqual(result["B5_state"],"TRUE")
        self.assertEqual(result["minor_progress_status"],"TRUE")
        self.assertEqual(len(result["original_qbus"]),1)
        self.assertIsNotNone(result["original_roles"].primary_unit_id)
        self.assertIsNone(result["original_roles"].secondary_unit_id)
        self.assertEqual(result["orders"],0)

    def test_no_b5_role_when_source_snapshot_not_relinked(self):
        m=self.m
        result=m._tac_original_qbu_b5_synthetic_cutoff_v1(
            **closed_source(m,m.TrendDirection.LONG,with_zones=False))
        self.assertEqual(result["status"],"SYNTHETIC_ORIGINAL_QBU_B5_EVALUATED")
        self.assertEqual(result["negotiation_identity_status"],"KNOWN")
        self.assertEqual(result["minor_progress_status"],"TRUE")
        self.assertNotEqual(result["B5_state"],"TRUE")
        self.assertFalse(result["original_boundaries"])
        self.assertFalse(result["original_economic_units"])
        self.assertFalse(result["entry_ready"])

    def test_rearm_distinct_identity_and_overlap_conflict_original_parity(self):
        m=self.m
        first=evt(m,eid="E1",start=10,end=20)
        for start,want in ((21,"KNOWN"),(20,"CONFLICT")):
            second=evt(m,eid="E2",start=start,end=30)
            ep=replace(episode(m),interaction_event_ids=("E1","E2"))
            outputs=[]
            for impl in ("original","flattened"):
                cls=(self.original_id.NegotiationIdentityRequest
                     if impl=="original" else m.TAC_ID_NegotiationIdentityRequest)
                fn=(self.original_id.project_negotiation_identity
                    if impl=="original" else m.TAC_ID_project_negotiation_identity)
                req=cls(information_cutoff=40,trend_episode_id="TE-1",
                    direction=m.TrendDirection.LONG,
                    events=(first,second),episodes=(ep,),
                    continuity_by_candidate_id={"C1":True},
                    theta_test=m.frozen_d3_parameters(
                        m.current_partial_parameter_snapshot()).theta_test,
                    rearm_predecessor_by_event_id={"E2":"E1"},
                    history_complete=True,
                    provenance={"fixture":"SYNTHETIC_REARM_TEST"})
                out=fn(req)
                self.assertEqual(out.status,want)
                if want=="KNOWN":
                    self.assertNotEqual(out.negotiation_identity_by_event_id["E1"],
                                        out.negotiation_identity_by_event_id["E2"])
                outputs.append(semantic_identity(out))
            self.assertEqual(outputs[0],outputs[1])

    def test_b5_role_memory_next_cutoff_and_qbu_nonduplication(self):
        m=self.m
        params=closed_source(m,m.TrendDirection.LONG)
        first=m._tac_original_qbu_b5_synthetic_cutoff_v1(**params)
        mem=first["next_original_role_memory"]
        self.assertIsNotNone(mem)
        req=m.TAC_BASE_Update008Request(
            information_cutoff=30,trend_episode_id="TE-1",
            direction=m.TrendDirection.LONG,
            snapshots=params["snapshots"],candidates=params["candidates"],
            episodes=params["anchor_episodes"],events=params["interaction_events"],
            progress_evidence=(),negotiation_identity_by_event_id={},
            canonical_segment_id_by_anchor_episode_id={"A1":"SEG"},
            continuity_by_candidate_id={"C1":True},
            corridor=params["corridor"],protected_price=params["protected_price"],
            protected_scale=Fraction(2),
            theta_test=m.frozen_d3_parameters(
                m.current_partial_parameter_snapshot()).theta_test,
            theta_progress=m.frozen_d3_parameters(
                m.current_partial_parameter_snapshot()).theta_progress)
        orig_req=replace(req,
            negotiation_identity_by_event_id={"E1":next(iter(
                m.TAC_ID_project_negotiation_identity(
                    m.TAC_ID_NegotiationIdentityRequest(
                        information_cutoff=30,trend_episode_id="TE-1",
                        direction=m.TrendDirection.LONG,
                        events=params["interaction_events"],
                        episodes=params["anchor_episodes"],
                        continuity_by_candidate_id={"C1":True},
                        theta_test=req.theta_test,history_complete=True)
                ).negotiation_identity_by_event_id.values()))},
            progress_evidence=(
                m.TAC_BASE_ProgressLineageEvidence(
                    event_id="E1",
                    progress=m.TrendSideMinorProgressEvidence(
                        pivot_id="P1",confirmed_at=30,
                        material_progress=True,timeframe_ms=900000,layer="MINOR"),
                    target_trend_episode_id="TE-1",
                    direction=m.TrendDirection.LONG,
                    canonical_segment_id="SEG",continuity_intact=True),))
        first_out,_=m.TAC_BASE_produce_update008(orig_req)
        second_req=replace(orig_req,
            information_cutoff=31,episodes=first_out.episodes)
        second,mem2=m.TAC_BASE_produce_update008(second_req,prior_memory=mem)
        self.assertFalse(second.produced_qbus)
        self.assertIsNotNone(second.roles)
        # Geometric unit IDs include source cutoff and can legitimately churn.
        # RoleMemory tracks economic lineage by original anchor+QBU identity.
        self.assertTrue(second.role_runtime.prior_primary_continuity_preserved)
        self.assertEqual(second.roles.transition.value,"NONE")
        self.assertIsNotNone(mem2)
        self.assertEqual(mem2.primary_qbu_identities,mem.primary_qbu_identities)
        self.assertFalse(any(x for x in second.conflict_lineage_refs))

    def test_actual_D2_terminal_cutoff_limits_eligibility(self):
        m=self.m
        params=closed_source(m,m.TrendDirection.LONG)
        params["trend_episode_terminal_cutoff"]=25
        out=m._tac_original_qbu_b5_synthetic_cutoff_v1(**params)
        self.assertFalse(out["entry_ready"])
        self.assertEqual(out["orders"],0)
        # Original producer reports calculation TRUE even when *zero* eligible
        # progress records remain after applying the D2 terminal cutoff.
        # This is NOT a positive material progress record, and yields NO QBU.
        self.assertEqual(out["minor_progress_status"],"TRUE")
        self.assertFalse(out.get("original_qbus",()))
        self.assertTrue(out.get("original_roles") is None or
                        out["original_roles"].primary_unit_id is None)
        # Terminal cutoff must arise from actual D2 state; a passed integer
        # is not authenticated D2 episode-termination provenance.

    def test_unknown_epoch_and_missing_coverage_fail_closed(self):
        m=self.m
        params=closed_source(m,m.TrendDirection.LONG)
        params["source_receipt"]={"mode":"REAL_PROSPECTIVE","history_complete":True}
        unknown=m._tac_original_qbu_b5_synthetic_cutoff_v1(**params)
        self.assertFalse(unknown["producer_mutated"])
        self.assertFalse(unknown["b5_original_update008_bound"])
        self.assertEqual(unknown["status"],"BLOCKED_EPOCH_CONTINUITY_UNPROVEN")
        params["source_receipt"]=closed_source(m,m.TrendDirection.LONG)["source_receipt"].copy()
        params["source_receipt"]["synthetic_coverage_ref"]=""
        # This is source completeness failure, not a chance to infer progress.
        missing=m._tac_original_qbu_b5_synthetic_cutoff_v1(**params)
        self.assertNotEqual(missing.get("minor_progress_status"),"TRUE")
        self.assertFalse(missing["entry_ready"])

if __name__=="__main__":
    unittest.main()
