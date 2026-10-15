from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from full_live_live_readiness_artifact_verifier_v1 import (
    LiveReadinessArtifactBlock,
    verify_readiness_gate_artifact,
)

SCHEMA = "TAC_FULL_LIVE_CURRENT_ACTIVATION_READINESS_PROOF_V1"
STATUS = "PASS_ALL_CURRENT_ACTIVATION_GATES"
ACCOUNT_SOURCE = "BINANCE_CLI_USDM_PRIVATE_READ_ONLY_PREFLIGHT_V1"
REQUIRED_GATES = (
    "CURRENT_SOURCE_AND_STAGED_RUNTIME_IDENTITY",
    "FROZEN_RC1_INTEGRITY",
    "FROZEN_528_PROSPECTIVE_WHOLE_BATCH",
    "UPDATE014_FINAL_ADMISSION_UNCHANGED",
    "FROZEN_ALL_TEN_D5_POLICY_ENFORCED",
    "D6_GENUINE_END_TO_END_AND_RESTART_PROOF",
    "EXCHANGE_STOP_IDENTITY_AND_ORDER_OWNERSHIP",
    "GLOBAL_EXECUTION_UNCERTAINTY_LATCH_CLEAR",
    "CAPITAL_BASE_POLICY_FROZEN",
    "CANONICAL_AND_LIVE_AUTHORITY_BLOCKERS_CLOSED",
    "NO_BACKFILL_OR_HISTORICAL_OUTCOME",
    "INITIAL_ACTIVATION_ACCOUNT_CLEAN",
)


class LiveReadinessSemanticsBlock(RuntimeError):
    pass


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise LiveReadinessSemanticsBlock(code)


def _sha_ref(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 71
        and value.startswith("SHA256:")
        and all(c in "0123456789abcdef" for c in value[7:])
    )


def validate_current_live_readiness_proof(
    *,
    proof: Mapping[str, Any],
    source_head: str,
    activated_at_ms: int,
    d5_authority_digest: str,
    capital_authority_digest: str,
    canonical_audit_digest: str,
    live_authority_digest: str,
    evidence_root: Path,
) -> Mapping[str, Any]:
    """Validate a same-activation, source-bound live proof, not an old readiness note.

    This has no network I/O, writes, implicit authorization, or freshness window.
    It requires existing gate artifact bytes on disk and rejects arbitrary
    matching-format hashes without readable evidence.
    A producer must separately acquire genuine account evidence immediately
    before creating activation state. No producer is authorized by this module.
    The canonical audit and live authority must independently have zero blockers.
    """
    _require(isinstance(proof, Mapping), "READINESS_PROOF_MAPPING_REQUIRED")
    _require(proof.get("schema") == SCHEMA, "CURRENT_LIVE_READINESS_SCHEMA_REQUIRED")
    _require(proof.get("status") == STATUS, "CURRENT_LIVE_READINESS_PASS_REQUIRED")
    _require(proof.get("branch") == "tac-full-live-v1", "READINESS_BRANCH_DRIFT")
    _require(
        isinstance(source_head, str)
        and len(source_head) == 40
        and all(c in "0123456789abcdef" for c in source_head),
        "EXPECTED_SOURCE_HEAD_INVALID",
    )
    _require(proof.get("source_head") == source_head, "READINESS_SOURCE_HEAD_DRIFT")
    _require(
        isinstance(activated_at_ms, int) and not isinstance(activated_at_ms, bool)
        and activated_at_ms > 0
        and type(proof.get("activated_at_ms")) is int
        and proof.get("activated_at_ms") == activated_at_ms,
        "READINESS_ACTIVATION_EPOCH_DRIFT",
    )
    _require(
        isinstance(proof.get("runtime_epoch_id"), str)
        and bool(proof["runtime_epoch_id"].strip()),
        "READINESS_RUNTIME_EPOCH_REQUIRED",
    )
    for name, expected in (
        ("d5_authority_digest", d5_authority_digest),
        ("capital_authority_digest", capital_authority_digest),
        ("canonical_audit_digest", canonical_audit_digest),
        ("live_authority_digest", live_authority_digest),
    ):
        _require(_sha_ref(expected) and proof.get(name) == expected,
                 "READINESS_AUTHORITY_DIGEST_DRIFT:" + name)

    account = proof.get("account_preflight")
    _require(isinstance(account, Mapping), "READINESS_ACCOUNT_PREFLIGHT_REQUIRED")
    _require(account.get("mode") == "INITIAL_ACTIVATION",
             "READINESS_INITIAL_ACTIVATION_ACCOUNT_MODE_REQUIRED")
    _require(account.get("source") == ACCOUNT_SOURCE,
             "READINESS_ACCOUNT_EVIDENCE_SOURCE_DRIFT")
    _require(account.get("status") == "PASS_CLEAN_READ_ONLY",
             "READINESS_ACCOUNT_NOT_CLEAN")
    for name in (
        "futures_account_enabled", "api_key_reading_enabled",
        "api_key_futures_enabled", "dual_side_position",
        "clean_for_live_activation",
    ):
        _require(account.get(name) is True, "READINESS_ACCOUNT_GATE_FAILED:" + name)
    for name in (
        "nonzero_position_count", "standard_open_order_count",
        "algo_open_order_count",
    ):
        _require(type(account.get(name)) is int and account[name] == 0,
                 "READINESS_ACCOUNT_NOT_EMPTY:" + name)
    _require(
        type(account.get("server_time_ms")) is int
        and account["server_time_ms"] >= activated_at_ms,
        "READINESS_ACCOUNT_TIME_PRECEDES_ACTIVATION_REQUEST",
    )
    raw_digest = account.get("raw_reference_sha256")
    _require(
        isinstance(raw_digest, str)
        and len(raw_digest) == 64
        and all(c in "0123456789abcdef" for c in raw_digest),
        "READINESS_ACCOUNT_RAW_EVIDENCE_DIGEST_REQUIRED",
    )

    gates = proof.get("gates")
    _require(isinstance(gates, Mapping), "READINESS_TYPED_GATES_REQUIRED")
    _require(set(gates) == set(REQUIRED_GATES), "READINESS_GATE_SET_DRIFT")
    for gate in REQUIRED_GATES:
        evidence = gates[gate]
        _require(
            isinstance(evidence, Mapping)
            and evidence.get("status") == "PASS"
            and evidence.get("source_head") == source_head
            and _sha_ref(evidence.get("evidence_digest")),
            "READINESS_GATE_UNPROVEN:" + gate,
        )
        try:
            verify_readiness_gate_artifact(
                gate=gate,
                evidence=evidence,
                source_head=source_head,
                evidence_root=evidence_root,
            )
        except LiveReadinessArtifactBlock as exc:
            raise LiveReadinessSemanticsBlock(
                "READINESS_GATE_ARTIFACT_UNVERIFIED:" + gate + ":" + str(exc)
            ) from exc
    _require(proof.get("auto_activation") is False, "AUTO_ACTIVATION_FORBIDDEN")
    _require(proof.get("historical_backfill") is False, "BACKFILL_FORBIDDEN")
    _require(proof.get("trading_before_activation") is False,
             "PRE_ACTIVATION_TRADING_FORBIDDEN")
    return {
        "status": "PASS_READINESS_SEMANTIC_VALIDATION_ONLY",
        "source_head": source_head,
        "runtime_epoch_id": proof["runtime_epoch_id"],
        "account_evidence_server_time_ms": activated_at_ms,
        "gates_validated": len(REQUIRED_GATES),
        "gate_artifact_bytes_verified": len(REQUIRED_GATES),
        "authority_effect": "NONE_SEPARATE_LIVE_GATES_STILL_REQUIRED",
    }


__all__ = [
    "LiveReadinessSemanticsBlock",
    "REQUIRED_GATES",
    "validate_current_live_readiness_proof",
]
