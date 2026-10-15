from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

SCHEMA = "TAC_FULL_LIVE_READINESS_GATE_ARTIFACT_V1"


class LiveReadinessArtifactBlock(RuntimeError):
    pass


def verify_readiness_gate_artifact(
    *,
    gate: str,
    evidence: Mapping[str, Any],
    source_head: str,
    evidence_root: Path,
) -> None:
    """Validate genuine on-disk bytes, NOT merely a supplied digest string.

    NOTE: Matching artifacts are NOT an independent CI attestation or
    exchange verification. The upstream producer of PASS_VERIFIED evidence
    and the genuine D6 E2E test remain separate blocking requirements.
    """
    path_root = Path(evidence_root)
    if path_root.is_symlink() or not path_root.is_dir():
        raise LiveReadinessArtifactBlock("READINESS_ARTIFACT_ROOT_NOT_TRUSTED")
    if path_root.resolve() != path_root.absolute():
        raise LiveReadinessArtifactBlock("READINESS_ARTIFACT_ROOT_ALIAS_FORBIDDEN")
    expected_name = gate.lower() + ".json"
    if evidence.get("artifact_file") != expected_name:
        raise LiveReadinessArtifactBlock("READINESS_ARTIFACT_FILENAME_DRIFT:" + gate)
    artifact_path = path_root / expected_name
    if artifact_path.is_symlink() or not artifact_path.is_file():
        raise LiveReadinessArtifactBlock("READINESS_ARTIFACT_FILE_REQUIRED:" + gate)
    try:
        raw = artifact_path.read_bytes()
        artifact = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise LiveReadinessArtifactBlock("READINESS_ARTIFACT_UNREADABLE:" + gate) from exc
    digest = "SHA256:" + hashlib.sha256(raw).hexdigest()
    if evidence.get("evidence_digest") != digest:
        raise LiveReadinessArtifactBlock("READINESS_ARTIFACT_DIGEST_MISMATCH:" + gate)
    if not isinstance(artifact, dict) or set(artifact) != {
        "schema", "gate_id", "source_head", "status",
        "authority_effect", "provenance",
    }:
        raise LiveReadinessArtifactBlock("READINESS_ARTIFACT_SCHEMA_DRIFT:" + gate)
    if artifact["schema"] != SCHEMA or artifact["gate_id"] != gate:
        raise LiveReadinessArtifactBlock("READINESS_ARTIFACT_GATE_DRIFT:" + gate)
    if artifact["source_head"] != source_head:
        raise LiveReadinessArtifactBlock("READINESS_ARTIFACT_SOURCE_DRIFT:" + gate)
    if artifact["status"] != "PASS_VERIFIED":
        raise LiveReadinessArtifactBlock("READINESS_ARTIFACT_NOT_VERIFIED:" + gate)
    if artifact["authority_effect"] != "NONE":
        raise LiveReadinessArtifactBlock("READINESS_ARTIFACT_IMPLICIT_AUTHORITY_FORBIDDEN:" + gate)
    provenance = artifact["provenance"]
    if not isinstance(provenance, dict) or not isinstance(
        provenance.get("verification_surface"), str
    ) or not provenance["verification_surface"].strip():
        raise LiveReadinessArtifactBlock("READINESS_ARTIFACT_PROVENANCE_REQUIRED:" + gate)


__all__ = [
    "LiveReadinessArtifactBlock",
    "SCHEMA",
    "verify_readiness_gate_artifact",
]
