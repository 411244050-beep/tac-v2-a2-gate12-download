# TAC-V2/A2 — Gate 1 / Gate 2 read-only host handoff V1

**Scope:** source-bound inspection on a pre-staged OpenClaw/Binance AI Pro
host. **No deployment, no source download, no pointer switch, no trading,
no historical backfill and no evidence promotion.** GitHub CI is not a substitute
for actual host/private-account evidence.

## Preconditions

- Verify the *actual* staged checkout or deployment bundle SHA against the
  GitHub SHA being evaluated; use the 40-character SHA obtained from verified
  source transport. Do **not** invent a `.tac_source_identity_v1.json`
  record just to pass the checks.
- The staging root and durable state root must be their **actual** canonical
  on-host paths. Do **not** create empty substitutes or delete any ledger,
  checkpoint, execution-uncertainty latch, existing live activation state or D6
  manual-handoff marker to make the initial-activation gate appear clean.
- `TAC_LIVE_ENABLED=0`. No account key, CLI credential, private account
  response, hostname, order ID or position data may be put in GitHub, logs
  sent to chat, or a public CI artifact.

## A. Collect current-source offline blocker inventory

Set `STAGED_REPO`, `STATE_ROOT`, and `STAGED_HEAD` on the target host to
the **existing** verified paths/commit (never placeholders or a test head).

```sh
TAC_LIVE_ENABLED=0 \
PYTHONPATH="$STAGED_REPO/work/live" \
python "$STAGED_REPO/work/live/full_live_gate12_offhost_blocker_manifest_v1.py" \
  --repo-root "$STAGED_REPO" \
  --state-root "$STATE_ROOT" \
  --expected-head "$STAGED_HEAD"
```

This output is intentionally `BLOCKED_REAL_HOST_AND_POSITIVE_E2E_EVIDENCE_REQUIRED`.
It only inventories the 12 readiness artifact *filenames* and source-policy
blockers; `PRESENT_BYTES_UNVERIFIED_NOT_A_PASS` does not close any gate.
It does not contact Binance or change the host.

## B. One-shot signed read-only account and local durable-state observation

Only after authentic source staging, independently configured least-privilege
Binance CLI read-only credentials and a safe non-active target host, run:

```sh
TAC_LIVE_ENABLED=0 \
PYTHONPATH="$STAGED_REPO/work/live" \
python "$STAGED_REPO/work/live/full_live_nontrading_host_readonly_audit_v1.py" \
  --repo-root "$STAGED_REPO" \
  --state-root "$STATE_ROOT" \
  --expected-head "$STAGED_HEAD"
```

This uses private **read-only** account queries and separately checks
Multi-Asset Mode. It summarizes source identity, Hedge Mode, position count,
standard and Algo order counts, execution-uncertainty latch, D6 handoff,
ledger and activation state. Its output is redacted by design, but still
handle it as private operational evidence. A blocked exit code is expected
when any condition is not met; never force or edit the result to PASS.

Existing activations with positions or ledgers require the **recovery** path,
not first-activation cleanup. Do not cancel unknown orders or change account
mode using this handoff.

## C. Gate 2 and Gate 3 completion criteria

- **Gate 2:** all 12 `REQUIRED_GATES` must have independent verified
  current-source artifact bytes under
  `$STATE_ROOT/live_readiness_gate_evidence_v1/`, with genuine producer
  provenance. The strict `full_live_live_readiness_semantics_v1.py` validator
  must verify them at the correct runtime/activation epoch, and actual
  canonical/live blocker lists must be empty for sound reasons.
- **Gate 3:** frozen producers must **naturally** produce an accepted
  `UPDATE-014` on prospective completed 15-minute bars, with source-
  and transaction-identical D5 policy token, FakeExecutor hard-stop/entry
  boundary, durable execution ledger and D6 cold restart proof. Separate
  synthetic component successes, a `N/A` `UPDATE-014`, or a manually
  forged admission is not a positive end-to-end proof.
- **Gate 1:** a clean signed private account read belongs to the actual
  target host and activation attempt, not a fake, cached or old CI report.

All gates remain **OPEN**, all three are independently required, and
`TAC_LIVE_ENABLED` must remain **0**. Neither the inventory nor this
handoff can authorize a real order, create live activation state, or move a
runtime pointer.
