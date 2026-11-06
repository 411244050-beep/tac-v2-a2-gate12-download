# TAC V6: bar-84 causal pre-bar snapshot audit — ZERO bar calls; private archive remains NOT DURABLE
Date 2026-11-07 | pinned frozen original commit 1f2499ecb84bfefea063992d48f23949c65c5578 | TEST_ONLY.

## Actual verified, not inferred

- Portable private archive remains inside AI Pro temporary workspace ONLY:
  tac_source/.private_checkpoints/ARCHIVE_v6_genesis_bar82_bar83_20261107.tar.gz
  length 2,316,545 bytes; SHA256 4bfd9da7ad6a4e72e26baa4ce0026e462365c5d72d14ab40f165b6e46d6f308f. 7 SHA256SUMS members verified, no unsafe tar members. There is NO presently verified user-downloadable private attachment/export channel. DURABLE_BACKUP=NO, and the assistant does not have this archive's bytes.
- Original bar-83 committed state inside that archive was independently restored with zero science cutoff calls. Exact bytes 13,937,694, SHA256 a074d852158c99e5eccedde1643f19ef6453ef4064cce6fc481cfb762b023617, last_cutoff=74699999; completed["SYNTH:74699999"] GENESIS_FULL_TYPED_STAGED with full D4, final packet digest 5b5dbc5f56a34c4b608d3e33744cbe1928bd1e95adc344cd692056d0b8624f6c, F9 UPDATE-011 PASS, F9 UPDATE-015 BLOCKED (PORT007), lineage committed_transactions=1 and ledgers=1. Original bar-82 prior checkpoint length 13,683,812, SHA256 previously verified in local manifest; preserve actual full hash from verified archive manifest and do not guess its truncated visible form.
- 528 symbols frozen, TAC_LIVE_ENABLED=0, subscriptions off. No real market data, account, orders, Paper/Live, deployment or trading. Separate blocked PORT007_UNRESOLVED_PRODUCTION_ALLOCATION_BLOCKED and BLOCKED_D3_B3_JOINT_PERSISTENCE.
- The next candidate bar, if later authorized, opens at 74700000 and closes at 75599999, SYNTH 15m. **This task does NOT authorize running it.**

## Exact frozen guard source

Original V6 source Git Blob 2f12e518858be4758d81d0027c6045466ddf38f0:
https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/d2_genesis_authority_handoff_20261106/live_runtime_raw_authority_extraction_packet_orchestration_binding_v6.py

Within _mature_no_active approx lines 822-828:
- durable_d3 = self._adapter()._d3_rebuild(bar.symbol)
- pre_view = durable_d3.update_000_pre_bar_view(bar.open_time)
- pre_snaps = tuple(pre_view.snapshots)
- if pre_snaps: raise RawV6Block("MATURE_NO_ACTIVE_RECONCILIATION_REQUIRES_ZERO_CAUSAL_PREBAR_SNAPSHOT")

Original frozen WP8 strategy_rc1/d3_boundary_intelligence/snapshots.py (within the 91-file original archive) pre_bar_view filters CausalBoundarySnapshot using snapshot.available_at < observer_open_time. The next observer's actual open_time is 74700000. Source snapshots from bar-83 genesis are NOT the same as the genesis bar's own prebar count=0; remeasure causal eligibility at the new observer open.

## Proposed zero-cutoff READ-ONLY diagnostic

1. Verify BOTH saved state files and original private archive bytes/full SHA256. Preserve originals and archive intact. If source unavailable, stop ARCHIVE_BYTES_UNAVAILABLE — no regeneration or bar replay. Check the exact known SHA of bar-83 export and its runtime governance. Never call V6.run_cutoff or minimal engine.run_cutoff_batch.
2. Using the exact seven original canonical loader identity fixes, restore the VERIFIED original bar-83 V6 state into a NEW isolated in-memory object. Assert last_cutoff=74699999, completed genesis, full state_digest same as saved bytes, next SYNTH observer snapshot and lineage ledger. Record original state_digest BEFORE any read-only inspection.
3. Read original relevant code or use a fresh isolated D3 reconstruction to calculate ONLY the next observer's causal pre-bar snapshot view at open_time=74700000:
   - the original symbol is SYNTH, no market or order I/O.
   - inspect the original reconstructed D3 snapshot collection, then call the ORIGINAL update_000_pre_bar_view(74700000) if verified non-mutating and available; if the method's purity is uncertain, refrain from calling it and instead report that the prebar count is NOT_PROVEN. Do not synthesize snapshots or invoke _mature_no_active.
   - capture number of snapshots, snapshot_id/candidate_id, available_at, source_timeframe_ms, whether strictly available before the next observer open, and original D3 data provenance. No huge data graphs. Compare against the exact snapshot filter from frozen original snapshots.py (eligible where available_at < 74700000).
   - Distinguish existing next_bar_snapshot in engine state from D3 causal boundary snapshots. Neither source should be silently substituted for the other.
4. Without running the next D1/D2 bar, read-only inspect genesis state trend_episode_id, episode_start_cutoff and continuity preconditions, but do not assert that the next raw D2 trend/canonical segment will remain eligible. _mature_no_active branch is only reached after raw D1/D2 for that bar; this is NOT executed here.
5. Check the rebuilt D3 reconstruction did not mutate the original restored V6 state: state_digest AFTER inspection must equal digest before; no changes in original checkpoint bytes. If any mutation is detected or state digest cannot be compared safely, report READ_ONLY_INVARIANT_FAILED.
6. Return one of:
   - NEXT_MATURE_PREBAR_GUARD_WOULD_BLOCK: actual causal prebar snapshots count >0 for SYNTH open_time 74700000, with actual original source refs; given _mature_no_active is later selected, its snapshot guard rejects (but do not assume the branch itself will be selected).
   - NEXT_MATURE_PREBAR_ZERO_ONLY: actual count=0, meaning only this ONE necessary guard is met, NOT sufficient authorization or overall next bar eligibility.
   - NEXT_BAR_ELIGIBILITY_NOT_PROVEN: cannot reproduce the exact original read-only pre-bar view safely and causally.
7. Do not run bar-84, any historical replay, raw/post/formal engine, a fake D3 update, or scientific computations that produce new state. Do not claim future readiness, forward test results, profit, risk or trade authority. Outer V6.run_cutoff=0; engine batch count=0.
8. Separately report PRIVATE EXPORT still blocked. The AI Pro platform has NOT yielded a private user-download attachment. Preserve the present verified tar.gz for eventual manual secure export. Do not upload state to public GitHub, paste state into chat, publish encoded chunks, or send to an unapproved remote endpoint. If an operator/user later identifies an explicit supported private export or user-controlled destination, require their authorization and separate verified remote readback before DURABLE_BACKUP=YES. Do not guess network paths, passwords or keys.
9. Final report: archive size/SHA, bar-83 restored SHA, zero run/engine calls, D3 original snapshot availability at open_time 74700000 (count and concise IDs), whether strict original guard is met, before/after V6 digest, no claims of next bar full readiness, private export status, independent PORT007/D3-B3 blocks. Use only scalar excerpts, do not dump either large state or full archive.

## Frozen original governance
strategy.py SHA256 792d2818d8495889319de5b3e6019ac0e856d27a59c6c959ac355ff239765a5f
spec.yaml SHA256 4fb02c4559fc2fe8ee4e95390b76fce132f5af34c4f7e23a0091f1c8f8108fd1
TEST_ONLY / SYNTH fixture random.Random(0); no real market evidence, production runtime, brokerage account, deployment, trade or order. Keep original scientific code, AST, statuses and frozen thresholds unchanged.
