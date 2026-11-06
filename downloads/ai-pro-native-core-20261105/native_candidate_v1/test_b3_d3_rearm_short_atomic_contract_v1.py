"""Frozen original SHORT rearm and atomic staging mechanics, TEST_ONLY.

NOT a production mapping authorization, not a Binance native source test.
All OHLC fixtures synthetic. No network, account, orders or Paper/Live.
"""
from __future__ import annotations

from dataclasses import replace
from fractions import Fraction
from types import SimpleNamespace
import unittest

import test_b3_d3_rearm_gap_source_only_v1 as original_probe


class ShortRearmGapAndStaging(original_probe.FrozenB3D3RearmGap):
    """Mirror the public LONG fixture into a valid frozen SHORT D3/B3 cycle."""

    def setUp(self):
        super().setUp()
        m = self.m
        self.d3 = m.D3ReferenceSkeleton.from_parameter_snapshot(
            m.current_partial_parameter_snapshot()
        )
        self.cand = m.build_candidate(
            symbol="BTCUSDT", source_timeframe_ms=900000,
            target_trend_episode_id="TE_REARM_PROBE",
            target_direction=m.TrendDirection.SHORT,
            family=m.CandidateFamily.EMA20,
            line=m.InfoValue.known(Fraction(-100)),
            source_scale=m.InfoValue.known(Fraction(2)),
            source_segment_id="SEG_CANONICAL",
            available_at=self.t0 - 1, source_continuity_ok=True,
        )
        self.snap = self.d3.update_008_register_candidate(self.cand)
        self.assertIsNotNone(self.snap)
        self.b3 = m.RuntimeB3PriceDrivenReturnProducerV1()

    @staticmethod
    def mirror(op, hi, lo, cl):
        def neg(x):
            return str(-Fraction(x))
        return neg(op), neg(lo), neg(hi), neg(cl)

    def _step(self, idx, op, hi, lo, cl, producer=None, d3=None):
        m = self.m
        d3 = d3 or self.d3
        producer = producer or self.b3
        now = self.t0 + idx * 900000
        op, hi, lo, cl = self.mirror(op, hi, lo, cl)
        bar = m.CanonicalBar.from_values(
            symbol="BTCUSDT", open_time=now, close_time=now + 899999,
            open=op, high=hi, low=lo, close=cl,
        )
        pre = d3.update_000_pre_bar_view(bar.open_time)
        self.assertEqual(len(pre.snapshots), 1)
        snap = pre.snapshots[0]
        geo = d3.update_002_capture_geometry(
            bar=bar, information_cutoff=bar.close_time, snapshot=snap
        )
        result = m._tac_frozen_b3_update007_step(
            producer=producer, d3=d3, candidate=self.cand,
            snapshot=snap, geometry=geo, bar=bar,
            current_trend=SimpleNamespace(
                episode_id="TE_REARM_PROBE",
                direction=m.TrendDirection.SHORT,
            ),
            source_continuity_intact=True,
            candidate_terminally_replaced=False,
            history_complete=True,
        )
        return bar, snap, geo, result

    def _observation(self, bar, snap, geo, control):
        return replace(super()._observation(bar, snap, geo, control),
                       current_trend_direction=self.m.TrendDirection.SHORT)

    def _original_four(self):
        data = (
            ("110", "112", "108", "110"),
            ("105", "106", "99", "101"),
            ("102", "105", "98", "103"),
            ("103", "108", "101", "106"),
        )
        rows = [self._step(i, *p) for i, p in enumerate(data)]
        trace = [
            (row[3]["producer"].reason, row[3]["event"].control.value,
             row[2].separated, row[2].test, row[2].approach,
             row[2].d_close, row[2].d_range_nearest)
            for row in rows
        ]
        self.assertEqual(
            [x[3]["event"].control.value for x in rows],
            ["ARMED", "ARMED", "INTERACTION_ACTIVE", "RESOLVED"],
            trace,
        )
        self.assertEqual(len(self.b3.state.lineages), 0)
        return rows

    def _fifth_raw(self):
        m = self.m
        now = self.t0 + 4 * 900000
        op, hi, lo, cl = self.mirror("110", "112", "108", "110")
        bar = m.CanonicalBar.from_values(
            symbol="BTCUSDT", open_time=now,
            close_time=now + 899999, open=op,
            high=hi, low=lo, close=cl
        )
        pre = self.d3.update_000_pre_bar_view(bar.open_time)
        self.assertEqual(len(pre.snapshots), 1)
        snap = pre.snapshots[0]
        geo = self.d3.update_002_capture_geometry(
            bar=bar, information_cutoff=bar.close_time, snapshot=snap
        )
        return bar, snap, geo

    def test_current_old_control_adapter_rearm_has_no_b3_pending(self):
        self._original_four()
        m = self.m
        before = self.d3.current_event(self.cand.candidate_id)
        self.assertEqual(before.control.value, "RESOLVED")
        bar, snap, geo, result = self._step(
            4, "110", "112", "108", "110"
        )
        self.assertTrue(geo.separated)
        self.assertEqual(result["event"].control.value, "ARMED")
        self.assertNotEqual(result["event"].event_id, before.event_id)
        self.assertEqual(result["event"].armed_at, bar.close_time)
        self.assertIsNone(self.b3.pending_state(bar.symbol, self.cand.candidate_id))
        now = self.t0 + 5 * 900000
        op, hi, lo, cl = self.mirror("105", "106", "99", "101")
        next_bar = m.CanonicalBar.from_values(
            symbol="BTCUSDT", open_time=now, close_time=now + 899999,
            open=op, high=hi, low=lo, close=cl
        )
        pre = self.d3.update_000_pre_bar_view(next_bar.open_time)
        next_snap = pre.snapshots[0]
        next_geo = self.d3.update_002_capture_geometry(
            bar=next_bar,
            information_cutoff=next_bar.close_time,
            snapshot=next_snap
        )
        obs = self._observation(
            next_bar, next_snap, next_geo,
            m.InteractionControl.ARMED
        )
        with self.assertRaisesRegex(
            m.RuntimeB3Block, "ARMED_WITHOUT_RUNTIME_B3_PENDING_STATE"
        ):
            self.b3.process_batch("SHORT_AFTER_BAD_REARM", (obs,))

    def test_new_cycle_prearming_projection_is_only_a_contract_candidate(self):
        self._original_four()
        m = self.m
        prior = self.d3.current_event(self.cand.candidate_id)
        bar, snap, geo = self._fifth_raw()
        future = m.rearm_after_resolution(prior, geometry=geo)
        self.assertEqual(future.control.value, "ARMED")
        self.assertNotEqual(prior.event_id, future.event_id)
        self.assertEqual(future.armed_at, bar.close_time)
        old = self.b3.export_state()
        staged = m.RuntimeB3PriceDrivenReturnProducerV1.restore_state(old)
        # This models a new independent watch's pre-arming phase. It is
        # not authorization to claim prior RESOLVED event was UNARMED.
        obs = self._observation(
            bar, snap, geo, m.InteractionControl.UNARMED
        )
        out = staged.process_batch("SHORT_PROPOSED_NEW_CYCLE", (obs,))
        pending = staged.pending_state(bar.symbol, self.cand.candidate_id)
        self.assertEqual(out[0].reason, "ARMED_FROZEN_CURRENT_CUTOFF_NO_RETURN")
        self.assertIsNotNone(pending)
        self.assertEqual(pending.arming_information_cutoff, future.armed_at)
        self.assertEqual(pending.arming_bar_close, bar.close)
        self.assertEqual(pending.arming_snapshot_id, snap.snapshot_id)
        self.assertEqual(pending.arming_scale, snap.source_scale)
        self.assertIsNone(out[0].return_evidence)
        self.assertEqual(self.b3.export_state(), old)

    def test_original_persist_failure_and_transaction_deny_paths(self):
        self._original_four()
        m = self.m
        bar, snap, geo = self._fifth_raw()
        obs = self._observation(bar, snap, geo, m.InteractionControl.UNARMED)
        staged = m.RuntimeB3PriceDrivenReturnProducerV1.restore_state(
            self.b3.export_state()
        )
        old = staged.export_state()

        def fail_persist(_state):
            raise OSError("WRITE_FAIL")

        with self.assertRaisesRegex(OSError, "WRITE_FAIL"):
            staged.process_batch("SHORT_FAIL", (obs,), persist=fail_persist)
        self.assertEqual(staged.export_state(), old)
        with self.assertRaisesRegex(
            m.RuntimeB3Conflict, "DUPLICATE_CANDIDATE_LINEAGE_IN_BATCH"
        ):
            staged.process_batch("SHORT_DUP", (obs, obs))
        got = staged.process_batch("SHORT_ONCE", (obs,))
        again = staged.process_batch("SHORT_ONCE", (obs,))
        self.assertEqual(got, again)
        with self.assertRaisesRegex(
            m.RuntimeB3Conflict, "SAME_TRANSACTION_DIFFERENT_INPUT"
        ):
            staged.process_batch(
                "SHORT_ONCE", (replace(obs, candidate_available=False),)
            )


if __name__ == "__main__":
    unittest.main()
