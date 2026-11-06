"""Original frozen B5 role arbitration: legitimate two-unit same-cutoff tie.

No changes to frozen assign_roles, scientific thresholds, B5 or live trading.
All test records are explicitly synthetic; not Binance native 473KB evidence.
"""
from __future__ import annotations

from dataclasses import replace
from fractions import Fraction
import unittest

from test_qbu_b5_completion_regression_v1 import (
    FrozenQBUCompletionDifferential, closed_source
)


def two_original_units(m, direction, second_p1_at=30):
    x = closed_source(m, direction, at=30)
    short = direction is m.TrendDirection.SHORT
    e1=x["interaction_events"][0]
    ep1=x["anchor_episodes"][0]
    s1=x["snapshots"][0]
    c1=x["candidates"][0]
    p0,p1=x["all_original_d2_minor"]
    b2=Fraction(-180 if short else 180)
    p1b_price=Fraction(-200 if short else 200)
    e2=replace(e1,
        event_id="E2", candidate_id="C2", anchor_episode_id="A2",
        event_reference_boundary=b2)
    ep2=replace(ep1,anchor_episode_id="A2",candidate_id="C2",
                interaction_event_ids=("E2",),qualified_uses=())
    s2=replace(s1,snapshot_id="SN-C2-5",candidate_id="C2",
                anchor_episode_id="A2",boundary=b2,
                source_segment_id="SEG2")
    c2=replace(c1,candidate_id="C2",boundary=m.InfoValue.known(b2),
                source_segment_id="SEG2")
    p0b=replace(p0,pivot_id="P0B",canonical_segment_id="SEG2",
                extreme_price=b2)
    p1b=replace(p1,pivot_id="P1B",canonical_segment_id="SEG2",
                extreme_price=p1b_price,confirmed_at=second_p1_at)
    x.update(
        snapshots=(s1,s2),candidates=(c1,c2),
        anchor_episodes=(ep1,ep2),interaction_events=(e1,e2),
        all_original_d2_minor=(p0,p1,p0b,p1b),
        canonical_segment_id_by_anchor_episode_id={"A1":"SEG","A2":"SEG2"},
        continuity_by_candidate_id={"C1":True,"C2":True},
        corridor=m.StructuralCorridor(
            Fraction(-220 if short else 70),
            Fraction(-70 if short else 220),
        ),
    )
    return x


class OriginalB5PrimaryAmbiguity(FrozenQBUCompletionDifferential):

    def test_both_real_original_qbus_at_same_latest_cutoff_no_primary(self):
        m=self.m
        for direction in (m.TrendDirection.LONG,m.TrendDirection.SHORT):
            params=two_original_units(m,direction)
            # This is the full original identity -> Minor -> B5 path,
            # no hand-supplied role evidence or manually inserted QBU.
            output=m._tac_original_qbu_b5_synthetic_cutoff_v1(**params)
            self.assertEqual(output["negotiation_identity_status"],"KNOWN")
            self.assertEqual(output["minor_progress_status"],"TRUE")
            self.assertEqual(output["original_minor_progress_record_count"],2)
            self.assertEqual(output["original_material_minor_progress_record_count"],2)
            self.assertEqual(len(output["original_qbus"]),2)
            self.assertEqual(len(output["original_economic_units"]),2)
            self.assertEqual(output["B5_state"],"UNKNOWN")
            self.assertEqual(output["original_roles"].transition,m.RoleTransition.UNRESOLVED)
            self.assertIsNone(output["original_roles"].primary_unit_id)
            self.assertIn("multiple independent units",
                          output["original_roles"].unresolved_reason)
            self.assertIsNone(output["next_original_role_memory"])
            self.assertFalse(output["entry_ready"])
            self.assertEqual(output["orders"],0)
            # Source-order permutation cannot legally select a winner.
            reverse={**params,
                     "snapshots":tuple(reversed(params["snapshots"])),
                     "candidates":tuple(reversed(params["candidates"])),
                     "anchor_episodes":tuple(reversed(params["anchor_episodes"])),
                     "interaction_events":tuple(reversed(params["interaction_events"]))}
            perm=m._tac_original_qbu_b5_synthetic_cutoff_v1(**reverse)
            self.assertEqual(perm["B5_state"],"UNKNOWN")
            self.assertIsNone(perm["original_roles"].primary_unit_id)
            self.assertEqual(
                {u.use_id for u in output["original_qbus"]},
                {u.use_id for u in perm["original_qbus"]}
            )

    def test_distinct_actual_confirmation_cutoff_originally_yields_unique_primary(self):
        m=self.m
        for direction in (m.TrendDirection.LONG,m.TrendDirection.SHORT):
            params=two_original_units(m,direction,second_p1_at=29)
            output=m._tac_original_qbu_b5_synthetic_cutoff_v1(**params)
            self.assertEqual(output["minor_progress_status"],"TRUE")
            self.assertEqual(len(output["original_qbus"]),2)
            self.assertEqual(len(output["original_economic_units"]),2)
            self.assertEqual(output["B5_state"],"TRUE")
            self.assertIsNotNone(output["original_roles"].primary_unit_id)
            self.assertIsNotNone(output["next_original_role_memory"])
            self.assertFalse(output["entry_ready"])
            self.assertEqual(output["orders"],0)


if __name__=="__main__":
    unittest.main()
