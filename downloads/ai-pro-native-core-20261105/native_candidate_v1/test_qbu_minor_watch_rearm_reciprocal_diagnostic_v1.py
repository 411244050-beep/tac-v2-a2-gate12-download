"""Source-only diagnostic: frozen Minor consumer vs actual WATCH-REARM membership.

TEST_ONLY diagnostic only; no change to original science, no native Binance writes.
A WATCH-REARM is never assigned a fabricated contact timestamp, resolution,
reference geometry or Qualified Boundary Use. Its original AnchorEpisode
membership is checked separately from eligibility for a QBU negotiation.

This probe tests a read-only reciprocal link returned by the ORIGINAL
bind_event_to_episode; it does NOT approve platform source/ledger mutations.
"""
from __future__ import annotations

from dataclasses import replace
from fractions import Fraction
import sys
import unittest

from test_b3_d3_rearm_gap_source_only_v1 import FrozenB3D3RearmGap
from test_b3_d3_rearm_short_atomic_contract_v1 import ShortRearmGapAndStaging
from test_qbu_anchor_membership_view_test_only_v1 import _AnchorMembershipCase


class _OriginalConsumerWatchProbe(_AnchorMembershipCase):

    def _case(self):
        prior, latest, ep, cutoff, current_d3 = self._original_two_cycles()
        watch = self._rearm_event
        m = self.m
        self.assertIn(watch.event_id, ep.interaction_event_ids)
        self.assertIsNone(watch.anchor_episode_id)
        self.assertIsNone(watch.started_at)
        self.assertIsNone(watch.resolved_at)
        self.assertIsNone(watch.event_reference_boundary)
        self.assertIsNone(watch.event_reference_scale)
        self.assertEqual(watch.control, m.InteractionControl.ARMED)
        self.assertEqual(watch.resolution, m.InteractionResolution.UNRESOLVED)
        self.assertEqual(watch.provenance["prior_event_id"], prior.event_id)
        self.assertEqual(
            watch.event_id,
            m.deterministic_id(
                "D3-WATCH-REARM", watch.candidate_id,
                prior.event_id, str(watch.armed_at)
            ),
        )
        self.assertIsNotNone(prior.resolved_at)
        self.assertLess(prior.resolved_at, watch.armed_at)
        self.assertEqual(watch.candidate_id, ep.candidate_id)
        self.assertEqual(watch.target_trend_episode_id, ep.target_trend_episode_id)
        self.assertEqual(watch.target_direction, ep.target_direction)
        return prior, watch, latest, ep, cutoff, current_d3

    def _progress(self, events, ep, cutoff):
        m=self.m
        original = sys.modules[
            "qbu_material_trend_side_minor_progress_production_binding_v1"
        ]
        original_base = sys.modules[
            "authoritative_d3_b5_d4_base_runtime_producers_v1"
        ]
        d3params = m.frozen_d3_parameters(m.current_partial_parameter_snapshot())
        actual=[]
        for base_cls, request_cls, call in (
            (original_base.Update008Request,
             original.QBUProgressProductionRequest,
             original.project_qbu_progress_evidence),
            (m.TAC_BASE_Update008Request,
             m.TAC_PR_QBUProgressProductionRequest,
             m.TAC_PR_project_qbu_progress_evidence),
        ):
            base = base_cls(
                information_cutoff=cutoff,
                trend_episode_id=self.cand.target_trend_episode_id,
                direction=self.cand.target_direction,
                snapshots=(), candidates=(self.cand,),
                episodes=(ep,), events=events,
                progress_evidence=(),
                negotiation_identity_by_event_id={},
                canonical_segment_id_by_anchor_episode_id={
                    ep.anchor_episode_id:self.cand.source_segment_id
                },
                continuity_by_candidate_id={self.cand.candidate_id: True},
                corridor=None,protected_price=None,protected_scale=None,
                theta_test=d3params.theta_test,
                theta_progress=d3params.theta_progress,
            )
            req = request_cls(
                update008_request=base,
                all_minor=(),
                trend_episode_start_cutoff=0,
                trend_episode_terminal_cutoff=None,
                history_complete=True,
                history_coverage_ref="COMPLETE_SYNTHETIC_NO_POST_RESOLVE_PIVOTS",
                theta_progress_parameter_ref="FROZEN_PARAM_TEST",
            )
            actual.append(call(req))
        x,y=actual
        self.assertEqual(
            (x.state, x.progress_evidence, x.unknown_refs, x.conflict_refs),
            (y.state, y.progress_evidence, y.unknown_refs, y.conflict_refs),
        )
        return y

    def test_original_minor_conflict_is_from_unbound_watched_member(self):
        prior, watch, latest, ep, cutoff, _ = self._case()
        # Latest actual interaction has already been reciprocal-projected via
        # the previous isolated original-source view. WATCH remains unbound.
        associated = self.m.bind_event_to_episode(latest, ep)
        result = self._progress((prior,watch,associated),ep,cutoff)
        self.assertEqual(result.state,self.m.EvidenceState.CONFLICT)
        self.assertEqual(result.conflict_refs,
                         ("EVENT_EPISODE_LINEAGE_MISMATCH:"+watch.event_id,))

    def test_original_reciprocal_membership_does_not_invent_contact_or_qbu(self):
        prior, watch, latest, ep, cutoff, current_d3 = self._case()
        before = current_d3.current_event(self.cand.candidate_id)
        original_watch = watch
        self.assertIsNone(original_watch.anchor_episode_id)
        projected = self.m.bind_event_to_episode(watch, ep)
        self.assertEqual(projected, replace(watch,anchor_episode_id=ep.anchor_episode_id))
        self.assertIsNone(projected.started_at)
        self.assertIsNone(projected.resolved_at)
        self.assertIsNone(projected.event_reference_boundary)
        self.assertIsNone(projected.event_reference_scale)
        self.assertEqual(projected.resolution,self.m.InteractionResolution.UNRESOLVED)
        self.assertEqual(projected.control,self.m.InteractionControl.ARMED)
        association = self.m.bind_event_to_episode(latest, ep)
        result = self._progress((prior,projected,association),ep,cutoff)
        self.assertEqual(result.state,self.m.EvidenceState.TRUE)
        self.assertEqual(len(result.progress_evidence),0)
        self.assertEqual(current_d3.current_event(self.cand.candidate_id),before)
        self.assertIsNone(original_watch.anchor_episode_id)

        identity_req = self.m.TAC_ID_NegotiationIdentityRequest(
            information_cutoff=cutoff,
            trend_episode_id=self.cand.target_trend_episode_id,
            direction=self.cand.target_direction,
            events=(prior,projected,association),
            episodes=(ep,),
            continuity_by_candidate_id={self.cand.candidate_id:True},
            theta_test=Fraction(1,10),
            history_complete=True,
            rearm_predecessor_by_event_id={latest.event_id:prior.event_id},
        )
        output=self.m.TAC_ID_project_negotiation_identity(identity_req)
        self.assertEqual(output.status,"KNOWN")
        self.assertEqual(set(output.negotiation_identity_by_event_id),
                         {prior.event_id, latest.event_id})
        self.assertNotIn(projected.event_id,output.negotiation_identity_by_event_id)

    def test_invalid_member_or_predecessor_must_not_be_reciprocally_projected(self):
        prior, watch, latest, ep, cutoff, _=self._case()
        with self.assertRaisesRegex(ValueError,"event/candidate mismatch"):
            self.m.bind_event_to_episode(
                replace(watch,candidate_id="OTHER_CANDIDATE"),ep)
        altered=replace(ep,interaction_event_ids=(
            x for x in ep.interaction_event_ids if x != watch.event_id
        ))
        # The literal tuple is required; a generator is invalid provenance.
        self.assertNotIn(watch.event_id,tuple(altered.interaction_event_ids))
        self.assertEqual(watch.provenance["prior_event_id"],prior.event_id)


class TestLongWatch(_OriginalConsumerWatchProbe,FrozenB3D3RearmGap):
    pass


class TestShortWatch(_OriginalConsumerWatchProbe,ShortRearmGapAndStaging):
    pass


if __name__=="__main__":
    unittest.main()
