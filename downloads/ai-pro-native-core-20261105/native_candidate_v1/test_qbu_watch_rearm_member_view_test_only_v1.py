"""Guarded frozen original WATCH-REARM member-view isolated regression.

Uses previous original-source LONG/SHORT cycles, not current Binance 473KB.
No mutation, no guessed Episode membership, no invented contact/QBU.
"""
from __future__ import annotations

from dataclasses import replace
import unittest

from test_b3_d3_rearm_gap_source_only_v1 import FrozenB3D3RearmGap
from test_b3_d3_rearm_short_atomic_contract_v1 import ShortRearmGapAndStaging
from test_qbu_minor_watch_rearm_reciprocal_diagnostic_v1 import _OriginalConsumerWatchProbe
from test_frozen_qbu_namespaced_parity_v1 import HERE


class _GuardedWatchCase(_OriginalConsumerWatchProbe):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        source = (HERE/"QBU_WATCH_REARM_MEMBER_VIEW_TEST_ONLY_V1.py").read_text()
        exec(compile(source,"QBU_WATCH_REARM_MEMBER_VIEW_TEST_ONLY_V1.py","exec"),vars(cls.m))

    def _view(self, events, episodes, cutoff, complete=True):
        return self.m._tac_qbu_watch_rearm_member_view_test_only_v1(
            events=events, episodes=episodes,
            information_cutoff=cutoff,history_complete=complete,
        )

    def test_exact_original_watch_membership_only_leaves_contact_and_qbu_absent(self):
        prior,watch,latest,ep,cutoff,d3 = self._case()
        before_d3=d3.current_event(self.cand.candidate_id)
        e2=self.m.bind_event_to_episode(latest,ep)
        baseline=self._progress((prior,watch,e2),ep,cutoff)
        self.assertEqual(baseline.state,self.m.EvidenceState.CONFLICT)
        view=self._view((prior,watch,e2),(ep,),cutoff)
        self.assertEqual(view["projected_watch_rearm_event_ids"],(watch.event_id,))
        self.assertEqual(view["unprojected"],())
        self.assertEqual(view["events"][1],self.m.bind_event_to_episode(watch,ep))
        self.assertIsNone(view["events"][1].started_at)
        self.assertIsNone(view["events"][1].resolved_at)
        self.assertIsNone(view["events"][1].event_reference_boundary)
        self.assertIsNone(view["events"][1].event_reference_scale)
        self.assertEqual(view["events"][1].control,self.m.InteractionControl.ARMED)
        self.assertFalse(view["entry_ready"])
        self.assertEqual(view["orders"],0)
        result=self._progress(view["events"],ep,cutoff)
        self.assertEqual(result.state,self.m.EvidenceState.TRUE)
        self.assertEqual(result.progress_evidence,())
        self.assertEqual(d3.current_event(self.cand.candidate_id),before_d3)
        self.assertIsNone(watch.anchor_episode_id)

    def test_missing_actual_membership_is_not_built(self):
        prior,watch,latest,ep,cutoff,_=self._case()
        ep2=replace(ep,interaction_event_ids=tuple(
            x for x in ep.interaction_event_ids if x != watch.event_id
        ))
        result=self._view((prior,watch,latest),(ep2,),cutoff)
        self.assertEqual(result["projected_watch_rearm_event_ids"],())
        self.assertEqual(result["events"][1],watch)
        self.assertEqual(result["unprojected"],(
            (watch.event_id,"NOT_ORIGINAL_EPISODE_MEMBER"),)
        )

    def test_terminal_episode_is_not_backfilled(self):
        prior,watch,latest,ep,cutoff,_=self._case()
        ep2=replace(ep,validity=self.m.AnchorValidity.TERMINATED)
        result=self._view((prior,watch,latest),(ep2,),cutoff)
        self.assertEqual(result["projected_watch_rearm_event_ids"],())
        self.assertEqual(result["events"][1],watch)
        self.assertEqual(result["unprojected"],(
            (watch.event_id,"TERMINATED_OR_TRUE_BREAK_EPISODE"),)
        )

    def test_fake_original_predecessor_and_contact_are_rejected(self):
        prior,watch,latest,ep,cutoff,_=self._case()
        provenance={**dict(watch.provenance),"prior_event_id":"FAKE"}
        with self.assertRaisesRegex(ValueError,"INVALID_PREDECESSOR"):
            self._view((prior,replace(watch,provenance=provenance),latest),(ep,),cutoff)
        with self.assertRaisesRegex(ValueError,"INVALID_ORIGINAL_NONCONTACT_STATE"):
            self._view((prior,replace(watch,started_at=watch.armed_at),latest),(ep,),cutoff)
        with self.assertRaisesRegex(ValueError,"HISTORY_COVERAGE_INCOMPLETE"):
            self._view((prior,watch,latest),(ep,),cutoff,complete=False)

    def test_divergent_event_and_ambiguous_episode_rejected(self):
        prior,watch,latest,ep,cutoff,_=self._case()
        with self.assertRaisesRegex(ValueError,"DIVERGENT_EVENT"):
            self._view((prior,watch,replace(watch,armed_at=watch.armed_at-1),latest),(ep,),cutoff)
        ep2=replace(ep,anchor_episode_id=ep.anchor_episode_id+"-OTHER")
        with self.assertRaisesRegex(ValueError,"AMBIGUOUS_MEMBER"):
            self._view((prior,watch,latest),(ep,ep2),cutoff)


class TestLongGuardedWatch(_GuardedWatchCase,FrozenB3D3RearmGap):
    pass


class TestShortGuardedWatch(_GuardedWatchCase,ShortRearmGapAndStaging):
    pass


if __name__=="__main__":
    unittest.main()
