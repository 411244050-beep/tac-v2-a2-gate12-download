# TAC WP8 original strategy_rc1 complete source transport — isolated TEST_ONLY

Date 2026-11-06. The upstream exact-original transport was pinned to private user-owned repository `411244050-beep/tac-v2-a2-external-runtime`, commit `1f2499ecb84bfefea063992d48f23949c65c5578`.

The 6 original split base64 parts were copied from that exact commit, verifying original Git Blob IDs, concatenated in numeric order **without changing content**, and the joined ASCII base64 digest was independently calculated and confirmed to match the original manifest. The combined archive, full 91-file SHA256 list, and original transport manifest are delivered in public GitHub now. This does **not** claim full Binance native integration or persistence.

## Download

- [strategy_rc1_exact.tar.xz.b64](https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/wp8_strategy_rc1_full_original_20261106/strategy_rc1_exact.tar.xz.b64)
- [strategy_rc1_SHA256SUMS.txt](https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/wp8_strategy_rc1_full_original_20261106/strategy_rc1_SHA256SUMS.txt)
- [wp8_strategy_rc1_exact_transport_v1.json](https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/wp8_strategy_rc1_full_original_20261106/wp8_strategy_rc1_exact_transport_v1.json)

## Exact digest and known missing files

- Concatenated base64 file: **70812 bytes**, SHA-256 `cb966bf33f98b058c2bf7d70314b5ff18092395a0e0dd0757eb0a8cb778aeebe`
- Decoded XZ tar: **53108 bytes**, expected SHA-256 `36111563b5778513d5803a3ec7c2b86f967a71d915fbcfd9bee5cb4ebebf8174`
- 91 file SHA256 list: **9711 bytes**, expected SHA-256 `d997c67dd0e909c0a1b6eb849918e692cbe5739079605f3c78d96517d1f11b60`
- Original `strategy_rc1/d2_market_state/platform.py`: SHA-256 `2e1e56ef71d561cb23da02fc2dd44d939899353919df665fa7dd41905cfb72dc`
- Original `strategy_rc1/wp1_reference.py`: SHA-256 `31dcba1e5500a494f3ec48ae1a3c80b683ba75881bc2f64bccdcc425e41272f4`
- Original `strategy_rc1/d2_market_state/establishment.py`: SHA-256 `0ae801e864c99aafc751a1ae8af4d42f4b82f400809ce8619c92767b818f5c06`

## Recovery, validation, and execution boundaries

1. Download all three public files and verify base64 file + manifest hashes above BEFORE extracting anything.
2. Base64-decode the archive (content is a raw base64 string with no newline), verify XZ tar SHA-256, inspect tar members (must be under `strategy_rc1/`), extract ONLY into a fresh **isolated TEST_ONLY temporary directory**. Confirm all 91 listed SHA256 hashes match with `sha256sum -c strategy_rc1_SHA256SUMS.txt` from extraction root.
3. First restore `strategy_rc1.d2_market_state.platform.EMPTY_PLATFORM`, `update_platform`, and any exact frozen dependencies they import, and original `strategy_rc1.wp1_reference` if the full reference runner still needs it. Do not overwrite existing frozen Binance `strategy.py`, `spec.yaml` or silently substitute other module versions in the running package.
4. Original `authoritative_d3_b5_d4_base_runtime_producers_v1.TrendEstablishmentRecord` has `trend`, `creation_cutoff`, `newest_intermediate_pivot_id`, `source_event_ids`, `provenance`; its `produce_trend_establishment_watch` confirms creation at `trend.episode_start_cutoff`, requires pivot source provenance. Seek these facts in actual authoritative D2 **episode creation events** and causal source history. Never synthesize them from a current TrendState or a fresh empty lineage ledger. If the 78-cutoff replay begins AFTER genesis and lacks the earlier source, report `HISTORY_COVERAGE_NOT_ESTABLISHED`; do not claim first event.
5. Restore original platform producer and D4 market event lineage via previously published public handoff:
   [D4 market-event lineage handoff](https://raw.githubusercontent.com/411244050-beep/tac-v2-a2-gate12-download/main/downloads/ai-pro-native-core-20261105/d4_market_event_lineage_binding_20261106/README_NATIVE_HANDOFF.md).
6. Address prior **F9 new-adapter timeout** by instrumenting *actual adapter stage entry and completion*, with immediate flushed stage log `cutoff, stage, input source refs count, started, ended, elapsed, blocked_reason`. First attempt **a single direction, single preselected existing cutoff** with **bounded execution** before full replay. This is an adapter hang localization, NOT a repeat of B3/B5 positive scientific tests. If no complete results before deadline, return last completed stage and stack/log status; do not silently rerun long 78-cutoff jobs. Do not claim any science call occurred if only imports completed.
7. `D4MarketEventLineageProductionProjectorV2.prepare` is not `commit`; only commit after a downstream **same isolated transaction** succeeds, abort pending on downstream failure; no persistent host durability is claimed.
8. Continue F9 / D4 four-class, D5 / UPDATE-014 / D6 only where exact frozen source authority is available. Preserve `PORT007_UNRESOLVED_PRODUCTION_ALLOCATION_BLOCKED`, `BLOCKED_D3_B3_JOINT_PERSISTENCE`, other explicit UNKNOWN/CONFLICT conditions.

**Safety:** `strategy.py` SHA256 `792d2818d8495889319de5b3e6019ac0e856d27a59c6c959ac355ff239765a5f`; `spec.yaml` SHA256 `4fb02c4559fc2fe8ee4e95390b76fce132f5af34c4f7e23a0091f1c8f8108fd1`. 528 frozen symbols, `TAC_LIVE_ENABLED=0`, subscriptions off; no Binance account/order/market I/O, Paper/Live, save/deploy, persistence mutation or trades. Temporary artifacts may disappear.
