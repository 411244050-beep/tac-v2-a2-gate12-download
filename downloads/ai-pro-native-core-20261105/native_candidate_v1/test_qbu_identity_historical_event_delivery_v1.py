"""Isolated original QBU identity event-history completeness tests (TEST_ONLY).

Tests pure frozen identity mapper against same original-source flattened mapping.
Does not alter frozen identity or generate real event records. Synthetic fixture
IDs and events model the exact missing-reference failure reported by Binance.
"""
from __future__ import annotations

from dataclasses import replace
from fractions import Fraction
import unittest

from test_frozen_qbu_namespaced_parity_v1 import (
    load, evt, episode, semantic_identity,
)


class OriginalHistoricalEventDelivery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m, _, cls.original, _ = load()
        assert cls.m.TAC_LIVE_ENABLED == 0

    def _fixture(self, mode="complete"):
        m = self.m
        real = evt(
            m, eid="D3-INTERACTION:AUTH-E1", cid="C1", aid="A1",
            start=10, end=20
        )
        watch = replace(
            real,
            event_id="D3-WATCH:AUTH-W",
            control=m.InteractionControl.UNARMED,
            resolution=m.InteractionResolution.UNRESOLVED,
            break_state=m.BreakState.NONE,
            anchor_episode_id=None,
            started_at=None,
            resolved_at=None,
            armed_at=None,
            event_reference_boundary=None,
            event_reference_scale=None,
            provenance={"original_cycle": "INITIAL_WATCH"},
        )
        rearm = replace(
            watch,
            event_id="D3-WATCH-REARM:AUTH-R",
            control=m.InteractionControl.ARMED,
            armed_at=6,
            provenance={
                "prior_event_id": "D3-INTERACTION:AUTH-PRIOR",
                "rearm": "MATERIAL_CORRECT_SIDE_SEPARATION"
            },
        )
        ep = replace(
            episode(m, eid=real.event_id, cid="C1", aid="A1"),
            interaction_event_ids=(
                watch.event_id, rearm.event_id, real.event_id
            ),
        )
        events = (real, watch, rearm)
        if mode == "missing":
            events = (real,)
        return real, watch, rearm, ep, events

    def _project(self, mode, *, include_history=True, extra_events=(),
                 predecessor=None, episode_override=None):
        m = self.m
        real, watch, rearm, ep, events = self._fixture(mode)
        if episode_override is not None:
            ep = episode_override(ep)
        out = []
        for cls, func in (
            (self.original.NegotiationIdentityRequest,
             self.original.project_negotiation_identity),
            (m.TAC_ID_NegotiationIdentityRequest,
             m.TAC_ID_project_negotiation_identity),
        ):
            request = cls(
                information_cutoff=30,
                trend_episode_id="TE-1",
                direction=m.TrendDirection.LONG,
                events=events + tuple(extra_events),
                episodes=(ep,),
                continuity_by_candidate_id={"C1": True},
                theta_test=Fraction(1, 10),
                history_complete=include_history,
                rearm_predecessor_by_event_id=predecessor or {},
                provenance={"source": "SYNTHETIC_HISTORY_DELIVERY_TEST_ONLY"},
            )
            out.append(func(request))
        self.assertEqual(semantic_identity(out[0]),
                         semantic_identity(out[1]))
        return out[0], real, watch, rearm

    def test_missing_watch_and_rearm_are_real_blockers(self):
        out, real, watch, rearm = self._project("missing")
        self.assertEqual(out.status, "UNKNOWN")
        self.assertEqual(out.reason, "REFERENCED_INTERACTION_EVENT_MISSING")
        self.assertEqual(
            set(out.unknown_refs),
            {"MISSING_EVENT:" + watch.event_id,
             "MISSING_EVENT:" + rearm.event_id},
        )
        self.assertEqual(dict(out.negotiation_identity_by_event_id), {})

    def test_deliver_exact_history_resolves_missing_refs_not_eligible_watch(self):
        out, real, watch, rearm = self._project("complete")
        self.assertEqual(out.status, "KNOWN")
        mapping = dict(out.negotiation_identity_by_event_id)
        self.assertEqual(set(mapping), {real.event_id})
        self.assertNotIn(watch.event_id, mapping)
        self.assertNotIn(rearm.event_id, mapping)
        self.assertTrue(mapping[real.event_id].startswith("QBU-NEGOTIATION-V1:"))
        self.assertEqual(out.unknown_refs, ())

    def test_history_complete_false_still_unknown_even_with_all_records(self):
        out, _, _, _ = self._project("complete", include_history=False)
        self.assertEqual(out.status, "UNKNOWN")
        self.assertEqual(out.reason, "INTERACTION_HISTORY_COVERAGE_INCOMPLETE")

    def test_divergent_duplicate_historical_event_fails_closed(self):
        _, real, watch, rearm, _ = self._fixture("complete")
        changed = replace(watch, armed_at=7)
        out, _, _, _ = self._project(
            "complete", extra_events=(changed,)
        )
        self.assertEqual(out.status, "CONFLICT")
        self.assertEqual(out.reason, "DIVERGENT_EVENT_RECORDS")
        self.assertIn(
            "DIVERGENT_EVENT_RECORD:" + watch.event_id,
            out.conflict_refs
        )

    def test_conflicting_rearm_predecessor_same_component_rejected(self):
        # The referenced previous negotiation must be a distinct cycle.
        m = self.m
        prior = evt(
            m, eid="D3-INTERACTION:AUTH-PRIOR", cid="C2", aid="A2",
            start=12, end=18
        )
        real, watch, rearm, ep, events = self._fixture("complete")
        ep2 = episode(m, eid=prior.event_id, cid="C2", aid="A2")
        out = []
        for cls, func in (
            (self.original.NegotiationIdentityRequest,
             self.original.project_negotiation_identity),
            (m.TAC_ID_NegotiationIdentityRequest,
             m.TAC_ID_project_negotiation_identity),
        ):
            req = cls(
                information_cutoff=30,
                trend_episode_id="TE-1",
                direction=m.TrendDirection.LONG,
                events=events+(prior,),
                episodes=(ep,ep2),
                continuity_by_candidate_id={"C1":True,"C2":True},
                theta_test=Fraction(1,10),
                history_complete=True,
                rearm_predecessor_by_event_id={real.event_id:prior.event_id},
            )
            out.append(func(req))
        self.assertEqual(semantic_identity(out[0]),semantic_identity(out[1]))
        self.assertEqual(out[0].status, "CONFLICT")
        self.assertEqual(out[0].reason, "REARM_BOUNDARY_SAME_COMPONENT")


if __name__ == "__main__":
    unittest.main()
