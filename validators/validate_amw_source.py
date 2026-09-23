import json, pathlib, hashlib, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=json.load(open(ROOT/"review"/"validation_spec.json"))
prompt=(ROOT/"controls"/"FOUNDER_CURRENT_CONTROL.txt").read_text()
checks={}
for concept in spec["required_prompt_concepts"]:
    checks["prompt:"+concept]=concept.lower() in prompt.lower()
manifest=json.load(open(ROOT/"source"/"manifest.json"))
for rel in ["review/Mirror_Review_Archive.json","review/Recovery_Crosswalk.json","review/Open_Recovery_Queue.json","review/Visual_Corpus_Audit.json","review/previously_unrecoverable_recovery_queue.json"]:
    checks["exists:"+rel]=(ROOT/rel).exists()
github_gate=(ROOT/"review"/"github_gate_pass.json")
checks["GITHUB_PASS_EVIDENCE"]=github_gate.exists() and json.load(open(github_gate)).get("pass") is True
result={"pass":all(checks.values()),"checks":checks}
json.dump(result,open(ROOT/"review"/"python_validation_result.json","w"),indent=2)
print(json.dumps(result,indent=2))
sys.exit(0 if result["pass"] else 2)
