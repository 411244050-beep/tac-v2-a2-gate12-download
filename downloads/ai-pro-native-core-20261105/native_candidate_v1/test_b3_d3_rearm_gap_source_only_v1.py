"""Isolated original B3/D3 rearm mismatch reproduction (TEST_ONLY).

This is a source-correct gap probe and a proposed new-cycle binding *candidate*.
It is NOT an authorized production bridge or a replacement for current Binance code.
Actual Binance 473KB strategy.py is unavailable in this GitHub environment.
"""
from __future__ import annotations
from dataclasses import replace
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace
import unittest

from test_frozen_qbu_namespaced_parity_v1 import load, HERE


class FrozenB3D3RearmGap(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m, _, _, _ = load()
        # The public bridge is the older frozen implementation; actual Binance
        # adapter is at reported lines 5997-6082, NOT byte-identical here.
        bridge = (HERE / "RUNTIME_B3_TO_ORIGINAL_D3_UPDATE007_BRIDGE_V1.py").read_text()
        exec(compile(bridge, "RUNTIME_B3_TO_ORIGINAL_D3_UPDATE007_BRIDGE_V1.py", "exec"), vars(cls.m))
        assert cls.m.TAC_LIVE_ENABLED == 0

    def setUp(self):
        m = self.m
        self.t0 = 1800000000000
        self.d3 = m.D3ReferenceSkeleton.from_parameter_snapshot(
            m.current_partial_parameter_snapshot()
        )
        self.cand = m.build_candidate(
            symbol="BTCUSDT", source_timeframe_ms=900000,
            target_trend_episode_id="TE_REARM_PROBE",
            target_direction=m.TrendDirection.LONG,
            family=m.CandidateFamily.EMA20,
            line=m.InfoValue.known(Fraction(100)),
            source_scale=m.InfoValue.known(Fraction(2)),
            source_segment_id="SEG_CANONICAL", available_at=self.t0 - 1,
            source_continuity_ok=True,
        )
        self.snap = self.d3.update_008_register_candidate(self.cand)
        self.assertIsNotNone(self.snap)
        self.b3 = m.RuntimeB3PriceDrivenReturnProducerV1()

    def _step(self, idx, op, hi, lo, cl, producer=None, d3=None):
        m = self.m
        d3 = d3 or self.d3
        producer = producer or self.b3
        now = self.t0 + idx * 900000
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
                direction=m.TrendDirection.LONG,
            ), source_continuity_intact=True,
            candidate_terminally_replaced=False, history_complete=True,
        )
        return bar, snap, geo, result

    def _original_four(self):
        # Frozen positive sequence, unchanged from already-passed public CI.
        data = (
            ("110", "112", "108", "110"),
            ("105", "106", "99", "101"),
            ("102", "105", "98", "103"),
            ("103", "108", "101", "106"),
        )
        rows = [self._step(i, *p) for i, p in enumerate(data)]
        self.assertEqual(
            [x[3]["event"].control.value for x in rows],
            ["ARMED", "ARMED", "INTERACTION_ACTIVE", "RESOLVED"],
        )
        self.assertEqual(len(self.b3.state.lineages), 0)
        return rows

    def _fifth_raw(self):
        m = self.m
        idx = 4
        now = self.t0 + idx * 900000
        bar = m.CanonicalBar.from_values(
            symbol="BTCUSDT", open_time=now, close_time=now + 899999,
            open="110", high="112", low="108", close="110",
        )
        pre = self.d3.update_000_pre_bar_view(bar.open_time)
        self.assertEqual(len(pre.snapshots), 1)
        snap = pre.snapshots[0]
        geo = self.d3.update_002_capture_geometry(
            bar=bar, information_cutoff=bar.close_time, snapshot=snap
        )
        return bar, snap, geo

    def _observation(self, bar, snap, geo, control):
        m = self.m
        return m.RuntimeB3Observation(
            bar=bar, snapshot=snap, geometry=geo,
            interaction_control=control, params=self.d3.params,
            symbol=bar.symbol, candidate_id=self.cand.candidate_id,
            source_segment_id=self.cand.source_segment_id,
            target_trend_episode_id=self.cand.target_trend_episode_id,
            target_direction=self.cand.target_direction,
            current_trend_episode_id="TE_REARM_PROBE",
            current_trend_direction=m.TrendDirection.LONG,
            canonical_continuity_intact=True,
            candidate_available=True,
            terminal_candidate_replacement=False,
            interaction_terminal=False,
        )

    def test_current_old_control_adapter_rearm_has_no_b3_pending(self):
        self._original_four()
        before = self.d3.current_event(self.cand.candidate_id)
        self.assertEqual(before.control.value, "RESOLVED")
        bar, snap, geo, result = self._step(
            4, "110", "112", "108", "110"
        )
        self.assertTrue(geo.separated)
        self.assertEqual(result["event"].control.value, "ARMED")
        self.assertNotEqual(result["event"].event_id, before.event_id)
        self.assertEqual(result["event"].armed_at, bar.close_time)
        self.assertIsNone(
            self.b3.pending_state(bar.symbol, self.cand.candidate_id)
        )
        # Direct frozen B3 ARMED on next bar cannot inherit missing pending.
        now = self.t0 + 5 * 900000
        next_bar = self.m.CanonicalBar.from_values(
            symbol="BTCUSDT", open_time=now,
            close_time=now + 899999, open="105",
            high="106", low="99", close="101",
        )
        next_snap = self.d3.update_000_pre_bar_view(next_bar.open_time).snapshots[0]
        next_geo = self.d3.update_002_capture_geometry(
            bar=next_bar, information_cutoff=next_bar.close_time,
            snapshot=next_snap,
        )
        obs = self._observation(
            next_bar, next_snap, next_geo,
            self.m.InteractionControl.ARMED
        )
        with self.assertRaisesRegex(
            self.m.RuntimeB3Block, "ARMED_WITHOUT_RUNTIME_B3_PENDING_STATE"
        ):
            self.b3.process_batch("NEXT_AFTER_BAD_REARM", (obs,))

    def test_new_cycle_prearming_projection_is_only_a_contract_candidate(self):
        self._original_four()
        m = self.m
        prior = self.d3.current_event(self.cand.candidate_id)
        bar, snap, geo = self._fifth_raw()
        future = m.rearm_after_resolution(prior, geometry=geo)
        self.assertEqual(future.control.value, "ARMED")
        self.assertNotEqual(prior.event_id, future.event_id)
        self.assertEqual(future.armed_at, bar.close_time)
        self.assertIsNone(self.b3.pending_state(bar.symbol, self.cand.candidate_id))
        # EXPERIMENTAL mapping only. No production adapter can do this
        # without explicit binding authority for the new cycle pre-arming phase.
        state_before = self.b3.export_state()
        staged = m.RuntimeB3PriceDrivenReturnProducerV1.restore_state(state_before)
        obs = self._observation(bar, snap, geo, m.InteractionControl.UNARMED)
        out = staged.process_batch("PROPOSAL_NEW_CYCLE_ONLY", (obs,))
        self.assertEqual(out[0].reason, "ARMED_FROZEN_CURRENT_CUTOFF_NO_RETURN")
        pending = staged.pending_state(bar.symbol, self.cand.candidate_id)
        self.assertIsNotNone(pending)
        self.assertEqual(pending.arming_information_cutoff, future.armed_at)
        self.assertEqual(pending.arming_bar_close, bar.close)
        self.assertEqual(pending.arming_scale, snap.source_scale)
        self.assertEqual(pending.arming_snapshot_id, snap.snapshot_id)
        self.assertIsNone(out[0].return_evidence)
        # Live object remains unchanged; the above has not been adopted.
        self.assertEqual(self.b3.export_state(), state_before)

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
            raise OSError("INJECTED_WRITE_FAILURE")

        with self.assertRaisesRegex(OSError, "INJECTED_WRITE_FAILURE"):
            staged.process_batch("PROBE_PERSIST_FAIL", (obs,), persist=fail_persist)
        self.assertEqual(staged.export_state(), old)
        with self.assertRaisesRegex(
            m.RuntimeB3Conflict, "DUPLICATE_CANDIDATE_LINEAGE_IN_BATCH"
        ):
            staged.process_batch("PROBE_DUP_CANDIDATE", (obs, obs))
        one = staged.process_batch("PROBE_ONCE", (obs,))
        again = staged.process_batch("PROBE_ONCE", (obs,))
        self.assertEqual(one, again)
        changed = replace(obs, candidate_available=False)
        with self.assertRaisesRegex(
            m.RuntimeB3Conflict, "SAME_TRANSACTION_DIFFERENT_INPUT"
        ):
            staged.process_batch("PROBE_ONCE", (changed,))


if __name__ == "__main__":
    unittest.main()
