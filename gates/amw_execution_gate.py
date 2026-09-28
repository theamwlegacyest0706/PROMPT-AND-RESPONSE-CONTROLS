#!/usr/bin/env python3
"""
AMW Legacy fail-closed execution gate.

This gate does not decide creative/content correctness by itself. It blocks
PASS/HOLDS/COMPLETE/APPROVED/SAVED/CURRENT_CONTROLLED claims unless the task
packet records completion of the Founder-directed sequence and confirms that
the actual requested work—not just metadata—was reviewed for fidelity.

Exit codes:
  0 = ALLOW
  2 = BLOCK
  3 = invalid packet
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

FINAL_STATUS_CLAIMS = {
    "PASS", "HOLDS", "COMPLETE", "APPROVED", "SAVED", "CURRENT_CONTROLLED"
}
FOUNDER_ONLY_STATUS = {"APPROVED", "SAVED", "CURRENT_CONTROLLED"}

REQUIRED_TRUE = [
    "read_complete_prompt",
    "python_gate_complete",
    "github_gate_complete",
    "same_source_set_verified",
    "controls_cross_referenced",
    "prior_mirror_reviews_compared",
    "all_produced_work_reviewed",
    "cross_chat_legacy_db_review_complete",
    "corrections_applied",
    "post_correction_python_validated",
    "post_correction_github_validated",
    "final_mirror_review_complete",
    "actual_artifact_reviewed",
    "semantic_fidelity_reviewed",
    "output_matches_requested_type",
]

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def validate(packet: Dict[str, Any]) -> Dict[str, Any]:
    violations: List[str] = []

    for key in REQUIRED_TRUE:
        if packet.get(key) is not True:
            violations.append(f"{key}=true required")

    if packet.get("unresolved_changes", True):
        violations.append("unresolved_changes must be false")

    if packet.get("technical_validation_only", False):
        violations.append(
            "technical validation cannot substitute for semantic/artifact fidelity review"
        )

    if packet.get("failed_artifact_reused", False) and not packet.get(
        "founder_authorized_failed_artifact_reuse", False
    ):
        violations.append(
            "failed artifact reuse is blocked without explicit Founder authorization"
        )

    repeated = int(packet.get("repeated_failure_count", 0) or 0)
    if repeated >= 2:
        if packet.get("stabilization_mode") is not True:
            violations.append(
                "repeated failure trigger requires stabilization_mode=true"
            )
        if packet.get("scope_isolated_to_single_incident", False):
            violations.append(
                "repeated failure cannot be reframed as an isolated incident"
            )

    prompt_sha = packet.get("prompt_sha")
    python_sha = packet.get("python_source_sha")
    github_sha = packet.get("github_source_sha")
    if not prompt_sha:
        violations.append("prompt_sha is required")
    if prompt_sha != python_sha:
        violations.append("Python source hash must equal prompt/source hash")
    if prompt_sha != github_sha:
        violations.append("GitHub source hash must equal prompt/source hash")

    if packet.get("prompt_text") is not None and prompt_sha:
        calculated = sha256_text(str(packet["prompt_text"]))
        if calculated != prompt_sha:
            violations.append("prompt_text SHA-256 does not match prompt_sha")

    if packet.get("requested_output_type") and packet.get("actual_output_type"):
        if packet["requested_output_type"] != packet["actual_output_type"]:
            violations.append(
                "actual_output_type must match requested_output_type exactly"
            )

    claim = str(packet.get("status_claim", "")).upper()
    if claim in FOUNDER_ONLY_STATUS and not packet.get(
        "explicit_founder_status_directive", False
    ):
        violations.append(
            f"explicit Founder directive required for {claim} status"
        )

    if claim in FINAL_STATUS_CLAIMS and violations:
        violations.append(f"status_claim {claim} blocked while violations exist")

    return {
        "decision": "ALLOW" if not violations else "BLOCK",
        "violation_count": len(violations),
        "violations": violations,
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet", type=Path, help="JSON task packet")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    try:
        packet = json.loads(args.packet.read_text(encoding="utf-8"))
        if not isinstance(packet, dict):
            raise ValueError("packet must be a JSON object")
    except Exception as exc:
        print(json.dumps({"decision": "INVALID", "error": str(exc)}))
        return 3

    result = validate(packet)
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))
    return 0 if result["decision"] == "ALLOW" else 2

if __name__ == "__main__":
    sys.exit(main())
