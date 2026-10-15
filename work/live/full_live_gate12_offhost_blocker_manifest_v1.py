"""Read-only, secret-free Gate 1/2/3 gap inventory for the current source.

A GitHub Actions checkout cannot prove a signed Binance account, active
host state, prospective exchange data or a natural positive UPDATE-014 E2E.
This module NEVER emits a readiness PASS or an activation artifact. It only
identifies which evidence must be collected under the existing strict
readiness verifier, without changing scientific or execution authority.

Host use: python work/live/full_live_gate12_offhost_blocker_manifest_v1.py
          --expected-head <40hex> [--state-root <existing-state-dir>]
No Binance CLI, network, subprocess, state writes, or API keys are required.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from full_live_live_readiness_semantics_v1 import REQUIRED_GATES

SCHEMA = "TAC_FULL_LIVE_GATE12_OFFHOST_BLOCKER_MANIFEST_V1"
ROOT = Path(__file__).resolve().parents[2]

SOURCE_FILE = ".tac_source_identity_v1.json"
AUDIT = "work/live/full_live_predeployment_strategy_runtime_audit_v1.json"
LIVE = "work/live/full_live_live_activation_authority_v1.json"
D5 = "work/live/full_live_d5_operational_risk_policy_authority_v1.json"
CAPITAL = "work/live/full_live_capital_base_snapshot_policy_authority_v1.json"

def _safe_json(repo: Path, relative: str) -> Mapping[str, Any] | None:
    base = repo / relative
    if base.is_symlink() or not base.is_file():
        return None
    try:
        payload = json.loads(base.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError):
        return None
    return payload if isinstance(payload, dict) else None


def _short_blocker_ids(raw: Any) -> list[str]:
    if not isinstance(raw, list):
        return ["UNKNOWN_OR_MISSING_BLOCKER_ARRAY"]
    ids = []
    for item in raw:
        name = item.get("id") if isinstance(item, dict) else item
        if not isinstance(name, str) or not name:
            name = "INVALID_BLOCKER_RECORD"
        # Never echo source detail/free text from confidential host files.
        ids.append(name[:100])
    return ids


def collect_manifest(
    *,
    repo_root: Path,
    expected_head: str,
    state_root: Path | None = None,
) -> dict[str, Any]:
    repo = Path(repo_root)
    expected_valid = (
        type(expected_head) is str
        and len(expected_head) == 40
        and all(c in "0123456789abcdef" for c in expected_head)
    )
    live_off = os.environ.get("TAC_LIVE_ENABLED", "0") == "0"
    safe_repo = repo.is_dir() and not repo.is_symlink()
    digest_ok = expected_valid and safe_repo and live_off

    policies: dict[str, Any] = {}
    for name, rel in (("d5", D5), ("capital", CAPITAL)):
        packet = _safe_json(repo, rel) if digest_ok else None
        policies[name] = {
            "status": packet.get("status") if packet else "NOT_READABLE",
            "frozen_at_source": bool(packet and packet.get("status") == "FROZEN"),
        }

    audit = _safe_json(repo, AUDIT) if digest_ok else None
    live = _safe_json(repo, LIVE) if digest_ok else None
    audit_blockers = _short_blocker_ids(
        audit.get("unresolved_rule_blockers") if audit else None
    )
    live_blockers = _short_blocker_ids(
        live.get("final_activation_blockers") if live else None
    )
    source = _safe_json(repo, SOURCE_FILE) if digest_ok else None
    staged_source_match = bool(
        source
        and source.get("schema") == "TAC_SOURCE_IDENTITY_V1"
        and source.get("branch") == "tac-full-live-v1"
        and source.get("head") == expected_head
    )

    state_readable = bool(
        state_root is not None
        and Path(state_root).is_dir()
        and not Path(state_root).is_symlink()
    )
    state_dir = Path(state_root) if state_readable else None
    evidence_root = (
        state_dir / "live_readiness_gate_evidence_v1"
        if state_dir is not None else None
    )
    root_safe = bool(
        evidence_root is not None
        and evidence_root.is_dir()
        and not evidence_root.is_symlink()
    )
    artifact_presence = {}
    for gate in REQUIRED_GATES:
        artifact = (evidence_root / (gate.lower() + ".json")) if root_safe else None
        exists = bool(artifact and artifact.is_file() and not artifact.is_symlink())
        artifact_presence[gate] = (
            "PRESENT_BYTES_UNVERIFIED_NOT_A_PASS"
            if exists else "MISSING_OR_UNTRUSTED_NOT_A_PASS"
        )

    readiness_file = (
        state_dir / "live_activation_readiness_proof_v1.json"
        if state_dir is not None else None
    )
    proof_exists = bool(
        readiness_file is not None
        and readiness_file.is_file()
        and not readiness_file.is_symlink()
    )

    # No synthetic or stub gate data can close Gate 1/2/3. Actual account
    # evidence must be acquired by the separate one-shot host audit, and
    # readiness evidence must be checked by the existing byte verifier.
    return {
        "schema": SCHEMA,
        "status": "BLOCKED_REAL_HOST_AND_POSITIVE_E2E_EVIDENCE_REQUIRED",
        "expected_source_head": expected_head if expected_valid else "INVALID",
        "branch": "tac-full-live-v1",
        "live_flag_off": live_off,
        "repository_readable": safe_repo,
        "staged_identity_matches": staged_source_match,
        "staged_identity_status": (
            "MATCHED_IDENTITY_FILE_NOT_SIGNED_BINARY_ATTESTATION"
            if staged_source_match else "MISSING_OR_MISMATCHED"
        ),
        "frozen_policy_status": policies,
        "canonical_audit_blocker_ids": audit_blockers,
        "live_authority_blocker_ids": live_blockers,
        "readiness_required_gate_count": len(REQUIRED_GATES),
        "readiness_gate_artifact_presence_only": artifact_presence,
        "readiness_proof_file_present_unverified": proof_exists,
        "readiness_artifact_verification_performed": False,
        "signed_private_account_observation_performed": False,
        "host_cloud_runtime_observed": False,
        "real_prospective_528_positive_update014_e2e_observed": False,
        "gate1": "OPEN_SIGNED_HOST_ACCOUNT_REQUIRED",
        "gate2": "OPEN_INDEPENDENT_12_ARTIFACT_VERIFICATION_REQUIRED",
        "gate3": "OPEN_NATURAL_POSITIVE_SAME_SOURCE_E2E_REQUIRED",
        "live_activation": "NO_GO",
        "auto_activation": False,
        "trading": False,
        "exchange_calls": 0,
        "host_writes": 0,
        "orders": 0,
        "fills": 0,
        "execution_intents": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--state-root", type=Path)
    args = parser.parse_args()
    output = collect_manifest(
        repo_root=args.repo_root,
        expected_head=args.expected_head,
        state_root=args.state_root,
    )
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
