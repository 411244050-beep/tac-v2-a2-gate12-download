# TAC-V2/A2 — Gate 1/2 public offline inspection kit

This repository distributes **five selected, unmodified text files** from the private TAC-V2/A2 source reference commit, solely for offline Gate 1/2 diagnostic inspection in an isolated folder.

**Source reference:** `629c7ca50031a585cb7efe3c0795485314fb93be` on `tac-full-live-v1`. The copies' Git blob SHA-1 identifiers were checked against that source and are recorded in `FILE_INTEGRITY.json` together with SHA-256 hashes of their bytes.

## Download as ZIP

Use **Code → Download ZIP** or the public [main branch ZIP](https://github.com/411244050-beep/tac-v2-a2-gate12-download/archive/refs/heads/main.zip). GitHub generates the ZIP, so its outer ZIP SHA-256 **differs** from the original 13 KB chat attachment. Verify the extracted source files against `SHA256SUMS.txt` instead.

For a reproducible snapshot, select an exact public Git commit and download its ZIP archive rather than trusting a moving branch.

## Scope and safety

- This is **NOT** the complete TAC-V2/A2 repository, not a deployable runtime, not a live activation credential and **not** proof of current host source identity.
- The canonical audit JSON, live activation authority, D5 full policy, runtime collector, signed Binance account preflight and production host audit are **not included**.
- Unpack into a **NEW, inactive inspection directory**. Do not overwrite `tac-runtime`, Forward/Measurement active targets, or any state directory.
- The inventory script can perform a **partial** source-only check. A missing policy in this kit is expected; it does not prove policy absent on the host.
- Do not fabricate `.tac_source_identity_v1.json`, bypass Gate1/2/3, perform signed private-account requests, retrieve secrets, backfill, restart or alter pointers.
- `TAC_LIVE_ENABLED=0`. Gates 1/2/3 **OPEN**. Live Activation **NO-GO**. Archived CTAS is separate and untouched.

## Example (from ZIP extraction root)

```bash
export TAC_LIVE_ENABLED=0
export PYTHONDONTWRITEBYTECODE=1
PYTHONPATH="$PWD/work/live" python "$PWD/work/live/full_live_gate12_offhost_blocker_manifest_v1.py" \
  --repo-root "$PWD" \
  --expected-head 629c7ca50031a585cb7efe3c0795485314fb93be
```

The output is intentionally a diagnostic/blocker inventory, not a PASS. Do not point this public kit at the real state directory as if this kit represented the deployed source.

See `deploy/openclaw/GATE12_READONLY_HOST_HANDOFF_V1.md` for the rules applicable only after independently verified, complete host source and state binding. Never send Binance keys, raw account data or private host identity to this public repository.
