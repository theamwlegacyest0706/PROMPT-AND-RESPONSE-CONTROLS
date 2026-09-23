import json, pathlib, hashlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = json.load(open(ROOT / "review" / "validation_spec.json", encoding="utf-8"))
prompt = (ROOT / "controls" / "FOUNDER_CURRENT_CONTROL.txt").read_text(encoding="utf-8")

checks = {}
for concept in spec["required_prompt_concepts"]:
    checks["prompt:" + concept] = concept.lower() in prompt.lower()

required_paths = [
    "review/Mirror_Review_Archive_FULL.json",
    "review/Recovery_Crosswalk_FULL.json",
    "review/Open_Recovery_Queue_FULL.json",
    "review/Visual_Corpus_Audit_FULL.json",
    "review/Recovered_Work_Register_FULL.json",
    "review/Approved_Visual_Authority_9_19_FULL.json",
    "review/Authority_State_Dictionary_FULL.json",
    "review/Stabilization_Corpus_Summary_FULL.json",
    "review/previously_unrecoverable_recovery_queue.json",
    "review/HINDERING_BEHAVIOR_PATTERN_AUDIT_2026-09-23.json",
    "review/Mirror_Review_2026-09-23_SELF_HINDERING_PATTERN.json",
    "source-control/current/AMW_MASTER_LAUNCH_REGISTERS_CURRENT_STABILIZATION_ACTIVE_ALL_SHEETS.json",
    "source-control/historical/AMW_MASTER_LAUNCH_REGISTERS_2026-09-19_CURRENT_CONTROLLED_RECONCILED_ALL_SHEETS.json",
    "source-control/historical/AMW_MASTER_LAUNCH_REGISTERS_2026-09-15_CURRENT_CONTROLLED_UPDATED_ALL_SHEETS.json",
    "source-control/historical/AMW_MASTER_LAUNCH_REGISTERS_2026-09-13_CURRENT_CONTROLLED_STRENGTHENED_ALL_SHEETS.json",
    "source-control/library-inventory-complete/INVENTORY_SUMMARY.json",
]
for rel in required_paths:
    checks["exists:" + rel] = (ROOT / rel).exists()

exact_prompt = (ROOT / "controls" / "FOUNDER_PROMPT_EXACT_2026-09-23_CURRENT.txt").read_text(encoding="utf-8")
source_prompt = (ROOT / "source-control" / "FOUNDER_PROMPT_EXACT_2026-09-23.txt").read_text(encoding="utf-8")
checks["exact_prompt_synced"] = exact_prompt == source_prompt == prompt

audit = json.load(open(ROOT / "review" / "HINDERING_BEHAVIOR_PATTERN_AUDIT_2026-09-23.json", encoding="utf-8"))
self_review = json.load(open(ROOT / "review" / "Mirror_Review_2026-09-23_SELF_HINDERING_PATTERN.json", encoding="utf-8"))
checks["full_history_pattern_audit_present"] = audit.get("documented_failure_events_analyzed", 0) >= 30
checks["self_mirror_level5"] = str(self_review.get("result", "")).startswith("LEVEL 5")
checks["funding_never_freezes"] = any("Funding continuity remains urgent and never freezes" in x for x in audit.get("corrections_now_binding", []))
checks["changed_execution_standard"] = self_review.get("final_statement") == "The correction standard is changed execution, not another explanation."

result = {
    "pass": all(checks.values()),
    "checks": checks,
    "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
    "audit_sha256": hashlib.sha256((ROOT / "review" / "HINDERING_BEHAVIOR_PATTERN_AUDIT_2026-09-23.json").read_bytes()).hexdigest(),
    "self_review_sha256": hashlib.sha256((ROOT / "review" / "Mirror_Review_2026-09-23_SELF_HINDERING_PATTERN.json").read_bytes()).hexdigest(),
}
out = ROOT / "review" / "python_validation_result_current.json"
out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
sys.exit(0 if result["pass"] else 2)
