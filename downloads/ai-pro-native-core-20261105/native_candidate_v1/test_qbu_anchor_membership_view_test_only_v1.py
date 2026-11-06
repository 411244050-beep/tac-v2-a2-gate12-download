"""Exact original D3 second-cycle event/Anchor membership view tests.

Synthetic LONG/SHORT full source, original immutable scientific methods only.
No Binance native baseline writes, orders, market, Paper/Live or deployment.
"""
from __future__ import annotations

from dataclasses import replace
from fractions import Fraction
import unittest

from test_b3_d3_rearm_gap_source_only_v1 import FrozenB3D3RearmGap
from test_b3_d3_rearm_short_atomic_contract_v1 import ShortRearmGapAndStaging
from test_b3_rearm_independent_cycle_stage_v1 import _StagedRearmCase
from test_frozen_qbu_namespaced_parity_v1 import HERE


class _AnchorMembershipCase(_StagedRearmCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        source = (HERE / "QBU_ANCHOR_MEMBERSHIP_VIEW_TEST_ONLY_V1.py").read_text()
        exec(compile(source, "QBU_ANCHOR_MEMBERSHIP_VIEW_TEST_ONLY_V1.py", "exec"),
             vars(cls.m))

    def _original_two_cycles(self):
        self._original_four()
        prior = self.d3.current_event(self.cand.candidate_id)
        bar, snapshot, geometry, staged = self._stage()
        self._rearm_event = staged["event"]
        stage_d3 = staged["staged_d3"]
        stage_b3 = staged["staged_b3"]
        rows = []
        for i, ohlc in enumerate((
            ("105", "106", "99", "101"),
            ("102", "105", "98", "103"),
            ("103", "108", "101", "106"),
        ), start=5):
            rows.append(self._step(i, *ohlc, producer=stage_b3, d3=stage_d3))
        latest = stage_d3.current_event(self.cand.candidate_id)
        episode = stage_d3.current_episode(self.cand.candidate_id)
        self.assertIsNotNone(episode)
        self.assertIn(prior.event_id, episode.interaction_event_ids)
        self.assertIn(latest.event_id, episode.interaction_event_ids)
        self.assertEqual(latest.control.value, "RESOLVED")
        self.assertEqual(latest.resolution.value, "RESOLVED_CORRECT_SIDE")
        self.assertIsNone(latest.anchor_episode_id)
        return prior, latest, episode, rows[-1][0].close_time, stage_d3

    def test_original_member_without_reciprocal_anchor_link_then_exact_view(self):
        prior, latest, episode, cutoff, original_d3 = self._original_two_cycles()
        before_event = original_d3.current_event(self.cand.candidate_id)
        view = self.m._tac_qbu_anchor_membership_view_test_only_v1(
            events=(prior, self._rearm_event, latest), episodes=(episode,),
            information_cutoff=cutoff, history_complete=True,
        )
        self.assertEqual(view["bound_event_ids"], (latest.event_id,))
        self.assertEqual(view["input_event_count"], 3)
        self.assertEqual(view["distinct_event_ids"], 3)
        self.assertEqual(view["orders"], 0)
        self.assertEqual(view["events"][0], prior)
        self.assertEqual(
            view["events"][2],
            self.m.bind_event_to_episode(latest, episode)
        )
        self.assertEqual(view["events"][2].anchor_episode_id, episode.anchor_episode_id)
        self.assertEqual(original_d3.current_event(self.cand.candidate_id), before_event)
        self.assertIsNone(before_event.anchor_episode_id)

        def project(events):
            req = self.m.TAC_ID_NegotiationIdentityRequest(
                information_cutoff=cutoff,
                trend_episode_id=self.cand.target_trend_episode_id,
                direction=self.cand.target_direction,
                events=events,
                episodes=(episode,),
                continuity_by_candidate_id={self.cand.candidate_id: True},
                theta_test=Fraction(1, 10),
                history_complete=True,
                rearm_predecessor_by_event_id={latest.event_id:prior.event_id},
            )
            return self.m.TAC_ID_project_negotiation_identity(req)

        before = project((prior,self._rearm_event,latest))
        self.assertEqual(before.status, "UNKNOWN")
        self.assertIn("ANCHOR_EPISODE_UNKNOWN:"+latest.event_id, before.unknown_refs)
        after = project(view["events"])
        self.assertEqual(after.status, "KNOWN")
        self.assertEqual(set(after.negotiation_identity_by_event_id),
                         {prior.event_id, latest.event_id})
        self.assertNotEqual(
            after.negotiation_identity_by_event_id[prior.event_id],
            after.negotiation_identity_by_event_id[latest.event_id]
        )

    def test_missing_member_cannot_be_projected(self):
        prior, latest, episode, cutoff, _ = self._original_two_cycles()
        altered = replace(episode,interaction_event_ids=(prior.event_id,))
        view = self.m._tac_qbu_anchor_membership_view_test_only_v1(
            events=(prior, self._rearm_event, latest),episodes=(altered,),
            information_cutoff=cutoff,history_complete=True
        )
        self.assertEqual(view["bound_event_ids"], ())
        self.assertIsNone(view["events"][2].anchor_episode_id)

    def test_event_episode_target_conflict_rejected(self):
        prior, latest, episode, cutoff, _ = self._original_two_cycles()
        conflicting = replace(latest, candidate_id="OTHER_CANDIDATE")
        with self.assertRaisesRegex(ValueError,"EPISODE_EVENT_LINEAGE_MISMATCH"):
            self.m._tac_qbu_anchor_membership_view_test_only_v1(
                events=(prior,self._rearm_event,conflicting), episodes=(episode,),
                information_cutoff=cutoff, history_complete=True
            )

    def test_future_and_conflicting_same_event_record_rejected(self):
        prior, latest, episode, cutoff, _ = self._original_two_cycles()
        call = self.m._tac_qbu_anchor_membership_view_test_only_v1
        with self.assertRaisesRegex(ValueError,"FUTURE_EVENT_RESOLUTION"):
            call(events=(prior,self._rearm_event,replace(latest,resolved_at=cutoff+1)),
                 episodes=(episode,), information_cutoff=cutoff,
                 history_complete=True)
        with self.assertRaisesRegex(ValueError,"DIVERGENT_EVENT_ID"):
            call(events=(prior, self._rearm_event, latest, replace(latest,resolved_at=cutoff-1)),
                 episodes=(episode,), information_cutoff=cutoff,
                 history_complete=True)
        with self.assertRaisesRegex(ValueError,"SOURCE_HISTORY_INCOMPLETE"):
            call(events=(prior,self._rearm_event,latest),episodes=(episode,),
                 information_cutoff=cutoff,history_complete=False)


class TestOriginalLongAnchorMembership(_AnchorMembershipCase, FrozenB3D3RearmGap):
    pass


class TestOriginalShortAnchorMembership(_AnchorMembershipCase, ShortRearmGapAndStaging):
    pass


if __name__ == "__main__":
    unittest.main()
