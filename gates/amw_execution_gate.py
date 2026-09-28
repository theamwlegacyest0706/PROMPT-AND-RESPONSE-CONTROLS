#!/usr/bin/env python3
"""
AMW Legacy fail-closed execution gate (v2).

Purpose:
- Enforce the Founder-directed execution order.
- Require evidence-backed requirement and artifact review.
- Block final status claims when any gate is missing, out of order, unsupported,
  or semantically unresolved.

This cannot alter the underlying model. It makes the AMW repository workflow
fail closed so narrative self-certification alone is not enough.

Exit codes:
  0 = ALLOW
  2 = BLOCK
  3 = INVALID
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

REQUIRED_EVENT_ORDER = [
    "read_complete_prompt",
    "python_gate_pre",
    "github_gate_pre",
    "cross_reference_all_controls_sources_work",
    "mirror_review_initial",
    "compare_prior_mirror_reviews",
    "apply_corrections",
    "review_actual_work",
    "python_gate_post",
    "github_gate_post",
    "cross_chat_prompt_legacy_database_review",
    "mirror_review_final",
]

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def _evidence_present(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return any(_evidence_present(v) for v in value)
    if isinstance(value, dict):
        return bool(value)
    return value is not None

def validate(packet: Dict[str, Any]) -> Dict[str, Any]:
    violations: List[str] = []

    prompt_text = packet.get("prompt_text")
    prompt_sha = packet.get("prompt_sha")
    python_sha = packet.get("python_source_sha")
    github_sha = packet.get("github_source_sha")
    if not isinstance(prompt_text, str) or not prompt_text.strip():
        violations.append("exact prompt_text is required")
    if not prompt_sha:
        violations.append("prompt_sha is required")
    elif isinstance(prompt_text, str) and sha256_text(prompt_text) != prompt_sha:
        violations.append("prompt_text SHA-256 does not match prompt_sha")
    if prompt_sha != python_sha:
        violations.append("Python source hash must equal prompt/source hash")
    if prompt_sha != github_sha:
        violations.append("GitHub source hash must equal prompt/source hash")

    events = packet.get("events")
    if not isinstance(events, list):
        violations.append("events list is required")
        events = []
    ids = [e.get("id") for e in events if isinstance(e, dict)]
    positions = []
    for required in REQUIRED_EVENT_ORDER:
        if required not in ids:
            violations.append(f"missing required event: {required}")
        else:
            positions.append(ids.index(required))
    if len(positions) == len(REQUIRED_EVENT_ORDER) and positions != sorted(positions):
        violations.append("required events are out of Founder-directed order")
    for event in events:
        if not isinstance(event, dict):
            violations.append("each event must be an object")
            continue
        if event.get("id") in REQUIRED_EVENT_ORDER:
            if event.get("status") != "PASS":
                violations.append(f"event {event.get('id')} must have status PASS")
            if not _evidence_present(event.get("evidence")):
                violations.append(f"event {event.get('id')} requires evidence")

    requirements = packet.get("requirements")
    if not isinstance(requirements, list) or not requirements:
        violations.append("nonempty requirements matrix is required")
        requirements = []
    for i, req in enumerate(requirements):
        if not isinstance(req, dict):
            violations.append(f"requirement[{i}] must be an object")
            continue
        if not str(req.get("text", "")).strip():
            violations.append(f"requirement[{i}] text is required")
        if req.get("status") != "PASS":
            violations.append(f"requirement[{i}] must have status PASS")
        if not _evidence_present(req.get("evidence")):
            violations.append(f"requirement[{i}] requires evidence")

    artifacts = packet.get("artifact_reviews")
    if not isinstance(artifacts, list) or not artifacts:
        violations.append("nonempty artifact_reviews is required")
        artifacts = []
    for i, art in enumerate(artifacts):
        if not isinstance(art, dict):
            violations.append(f"artifact_reviews[{i}] must be an object")
            continue
        if not str(art.get("artifact_ref", "")).strip():
            violations.append(f"artifact_reviews[{i}] artifact_ref is required")
        for key in ("semantic_fidelity", "output_type_match", "control_fidelity"):
            if art.get(key) != "PASS":
                violations.append(f"artifact_reviews[{i}].{key} must be PASS")
        if not _evidence_present(art.get("evidence")):
            violations.append(f"artifact_reviews[{i}] requires evidence")

    requested_type = packet.get("requested_output_type")
    actual_type = packet.get("actual_output_type")
    if not requested_type or not actual_type:
        violations.append("requested_output_type and actual_output_type are required")
    elif requested_type != actual_type:
        violations.append("actual_output_type must match requested_output_type exactly")

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
            violations.append("repeated failure trigger requires stabilization_mode=true")
        if packet.get("scope_isolated_to_single_incident", False):
            violations.append("repeated failure cannot be reframed as an isolated incident")

    if not _evidence_present(packet.get("prior_mirror_review_refs")):
        violations.append("prior_mirror_review_refs evidence is required")
    if not _evidence_present(packet.get("source_refs")):
        violations.append("source_refs evidence is required")

    if packet.get("unresolved_changes", True):
        violations.append("unresolved_changes must be false")

    claim = str(packet.get("status_claim", "")).upper()
    if claim in FOUNDER_ONLY_STATUS and not packet.get(
        "explicit_founder_status_directive", False
    ):
        violations.append(f"explicit Founder directive required for {claim} status")
    if claim in FINAL_STATUS_CLAIMS and violations:
        violations.append(f"status_claim {claim} blocked while violations exist")

    return {
        "decision": "ALLOW" if not violations else "BLOCK",
        "violation_count": len(violations),
        "violations": violations,
        "gate_version": 2,
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
        print(json.dumps({"decision": "INVALID", "error": str(exc), "gate_version": 2}))
        return 3

    result = validate(packet)
    print(json.dumps(result, indent=2 if args.pretty else None, sort_keys=True))
    return 0 if result["decision"] == "ALLOW" else 2

if __name__ == "__main__":
    sys.exit(main())
