"""Original-source LONG/SHORT TEST_ONLY staged rearm bridge coverage.

Not a native Binance validation. User-approved isolated adaptation, never
trades and never changes frozen B3/D3 source or current Binance workspace.
"""
from dataclasses import replace
from types import SimpleNamespace
from fractions import Fraction
import unittest

from test_b3_d3_rearm_gap_source_only_v1 import FrozenB3D3RearmGap
from test_b3_d3_rearm_short_atomic_contract_v1 import ShortRearmGapAndStaging
from test_frozen_qbu_namespaced_parity_v1 import HERE


class _StagedRearmCase:
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        source = (HERE / "B3_REARM_INDEPENDENT_CYCLE_STAGE_TEST_ONLY_V1.py").read_text()
        exec(compile(source, "B3_REARM_INDEPENDENT_CYCLE_STAGE_TEST_ONLY_V1.py", "exec"),
             vars(cls.m))

    def _source_receipt(self):
        return {
            "mode": "SYNTHETIC_TEST_ONLY_FULL_SOURCE",
            "history_complete": True,
            "provenance_complete": True,
            "same_cutoff_order_proven": True,
            "restart_coverage_proven": True,
        }

    def _stage(self, callback=None):
        bar, snapshot, geometry = self._fifth_raw()
        proposed = self.m._tac_b3_rearm_new_cycle_stage_test_only_v1(
            producer=self.b3,
            d3=self.d3,
            candidate=self.cand,
            snapshot=snapshot,
            geometry=geometry,
            bar=bar,
            current_trend=SimpleNamespace(
                episode_id="TE_REARM_PROBE",
                direction=self.cand.target_direction,
            ),
            source_continuity_intact=True,
            candidate_terminally_replaced=False,
            source_receipt=self._source_receipt(),
            validate_staged_receipt=callback,
        )
        return bar, snapshot, geometry, proposed

    def test_second_original_cycle_arming_later_return_and_event(self):
        self._original_four()
        before_d3_event = self.d3.current_event(self.cand.candidate_id)
        before_b3 = self.b3.export_state()
        bar, snapshot, geometry, staged = self._stage()
        self.assertEqual(staged["status"], "STAGED_TEST_ONLY_NO_DURABLE_COMMIT")
        self.assertFalse(staged["receipt"]["durable_joint_checkpoint"])
        self.assertFalse(staged["entry_ready"])
        self.assertEqual(staged["orders"], 0)
        self.assertEqual(staged["event"].control.value, "ARMED")
        self.assertEqual(staged["event"].armed_at, bar.close_time)
        self.assertNotEqual(before_d3_event.event_id, staged["event"].event_id)
        self.assertEqual(staged["receipt"]["old_event_id"], before_d3_event.event_id)
        self.assertEqual(staged["receipt"]["new_event_id"], staged["event"].event_id)
        self.assertEqual(self.d3.current_event(self.cand.candidate_id), before_d3_event)
        self.assertEqual(self.b3.export_state(), before_b3)
        self.assertIsNone(staged["b3_output"].return_evidence)
        pending = staged["staged_b3"].pending_state(bar.symbol, self.cand.candidate_id)
        self.assertIsNotNone(pending)
        self.assertEqual(pending.arming_snapshot_id, snapshot.snapshot_id)
        self.assertEqual(pending.arming_information_cutoff, bar.close_time)
        self.assertEqual(pending.arming_bar_close, bar.close)
        self.assertEqual(pending.arming_scale, snapshot.source_scale)
        self.assertEqual(pending.target_direction, self.cand.target_direction.value)

        # Later cutoffs resume the EXISTING frozen B3+original D3 bridge.
        stage_d3 = staged["staged_d3"]
        stage_b3 = staged["staged_b3"]
        result1 = self._step(
            5, "105", "106", "99", "101",
            producer=stage_b3, d3=stage_d3
        )[3]
        self.assertEqual(result1["producer"].reason,
                         "RETURN_QUALIFIED_LATCHED_NOT_CONSUMABLE_SAME_CUTOFF")
        self.assertIsNone(result1["producer"].return_evidence)
        result2 = self._step(
            6, "102", "105", "98", "103",
            producer=stage_b3, d3=stage_d3
        )[3]
        self.assertEqual(result2["producer"].reason, "LATCHED_RETURN_CONSUMABLE")
        self.assertEqual(result2["event"].control.value, "INTERACTION_ACTIVE")
        result3 = self._step(
            7, "103", "108", "101", "106",
            producer=stage_b3, d3=stage_d3
        )[3]
        self.assertEqual(result3["event"].control.value, "RESOLVED")
        self.assertIsNone(stage_b3.pending_state(bar.symbol, self.cand.candidate_id))

    def test_callback_failure_does_not_mutate_originals(self):
        self._original_four()
        original_event = self.d3.current_event(self.cand.candidate_id)
        original_state = self.b3.export_state()
        def fail_receipt(receipt):
            self.assertTrue(receipt["stage_only"])
            raise RuntimeError("INJECTED_RECEIPT_REJECT")
        with self.assertRaisesRegex(RuntimeError, "INJECTED_RECEIPT_REJECT"):
            self._stage(callback=fail_receipt)
        self.assertEqual(self.d3.current_event(self.cand.candidate_id), original_event)
        self.assertEqual(self.b3.export_state(), original_state)

    def test_forged_geometry_and_missing_source_truth_rejected(self):
        self._original_four()
        bar, snapshot, geometry = self._fifth_raw()
        common = dict(
            producer=self.b3, d3=self.d3, candidate=self.cand,
            snapshot=snapshot, geometry=geometry, bar=bar,
            current_trend=SimpleNamespace(
                episode_id="TE_REARM_PROBE",
                direction=self.cand.target_direction
            ),
            source_continuity_intact=True,
            candidate_terminally_replaced=False,
            source_receipt=self._source_receipt(),
        )
        call = self.m._tac_b3_rearm_new_cycle_stage_test_only_v1
        with self.assertRaisesRegex(ValueError, "GEOMETRY_ORIGIN_MISMATCH"):
            call(**dict(common, geometry=replace(geometry, d_close=geometry.d_close + Fraction(1))))
        with self.assertRaisesRegex(ValueError, "FULL_SOURCE_RECEIPT"):
            call(**dict(common, source_receipt={"mode": "SYNTHETIC_TEST_ONLY_FULL_SOURCE"}))
        with self.assertRaisesRegex(ValueError, "D2_TREND_MISMATCH"):
            opposite = (self.m.TrendDirection.LONG
                        if self.cand.target_direction is self.m.TrendDirection.SHORT
                        else self.m.TrendDirection.SHORT)
            call(**dict(common, current_trend=SimpleNamespace(
                episode_id="TE_REARM_PROBE", direction=opposite
            )))
        self.assertIsNone(self.b3.pending_state(bar.symbol, self.cand.candidate_id))

    def test_replay_and_conflicting_source_digest_deny(self):
        self._original_four()
        bar, snap, geo, staged = self._stage()
        txn = staged["receipt"]["transaction_id"]
        out = staged["b3_output"]
        # Use the exact frozen B3 serialized state after stage: must restore.
        restore = self.m.RuntimeB3PriceDrivenReturnProducerV1.restore_state(
            staged["staged_b3"].export_state()
        )
        obs = self._observation(bar, snap, geo, self.m.InteractionControl.UNARMED)
        self.assertEqual(restore.process_batch(txn, (obs,))[0], out)
        changed = replace(obs, candidate_available=False)
        with self.assertRaisesRegex(
            self.m.RuntimeB3Conflict, "SAME_TRANSACTION_DIFFERENT_INPUT"
        ):
            restore.process_batch(txn, (changed,))
        # Committed D3 is already ARMED, so another rearm for this cutoff fails.
        with self.assertRaisesRegex(ValueError, "ORIGINAL_PRIOR_EVENT_NOT_ELIGIBLE"):
            self.m._tac_b3_rearm_new_cycle_stage_test_only_v1(
                producer=staged["staged_b3"],
                d3=staged["staged_d3"],
                candidate=self.cand,
                snapshot=snap,
                geometry=geo,
                bar=bar,
                current_trend=SimpleNamespace(
                    episode_id="TE_REARM_PROBE", direction=self.cand.target_direction
                ),
                source_continuity_intact=True,
                candidate_terminally_replaced=False,
                source_receipt=self._source_receipt(),
            )


class TestStageLong(_StagedRearmCase, FrozenB3D3RearmGap):
    pass


class TestStageShort(_StagedRearmCase, ShortRearmGapAndStaging):
    pass


if __name__ == "__main__":
    unittest.main()
