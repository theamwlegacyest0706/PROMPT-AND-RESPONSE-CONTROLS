# AMW FAIL-SAFE OPTIONS REGISTER — 2026-09-27

Purpose: enumerate practical controls that reduce or prevent assistant prompt/control drift, especially controls that do not rely on assistant self-certification.

## Current exposure found
- The GitHub ChatGPT plugin currently has an app-specific permission of **Allow all actions**, which means ChatGPT can read and take GitHub actions without asking.
- The repository is **private**.
- No `.github` directory/workflow is currently present.
- GitHub repository rulesets are not available on the current private-repository plan state returned by the API; the API reports that GitHub Pro or a public repository is required for that feature.
- Branch-protection state could not be verified through this integration because that endpoint is not accessible to the integration.

## Fail-safe options

| ID | Option | What it blocks / exposes | Strength | Who must control it | Current status |
|---|---|---|---|---|---|
| FS-01 | Change GitHub ChatGPT permission from **Allow all actions** to **Always ask** | Prevents silent GitHub writes; every GitHub action requires user approval | Strong | Founder / ChatGPT permission setting | Available now; not enabled |
| FS-02 | Change GitHub ChatGPT permission to **Allow read actions; ask before making changes** | Allows verification reads but requires approval before writes | Strong | Founder / ChatGPT permission setting | Available now; not enabled |
| FS-03 | Disconnect/uninstall the GitHub plugin when authoritative controls are frozen | Removes ChatGPT's direct GitHub read/write path entirely | Very strong | Founder | Available now; disruptive to automated GitHub verification |
| FS-04 | Limit the GitHub App installation to selected repositories only | Keeps authoritative controls outside the connector's write scope | Very strong | Founder in GitHub App/install settings | Manual external configuration |
| FS-05 | Two-repository architecture: **AUTHORITY** repo inaccessible/read-only to ChatGPT + **WORKING** repo writable by ChatGPT | Prevents assistant from rewriting governing controls while still allowing work output | Very strong | Founder | Not yet implemented |
| FS-06 | User-owned read-only external master control source (GitHub repo, Drive file, local file) | Keeps governing prompt/control text outside assistant modification authority | Very strong | Founder | Not yet implemented |
| FS-07 | Offline/local immutable control package uploaded per task | Prevents silent changes to source-of-truth between tasks | Very strong | Founder | Available manually |
| FS-08 | Exact prompt/control SHA-256 manifest | Detects any source drift between Founder prompt, Python, GitHub, and output packet | Strong | Automated + Founder-verifiable | Partly implemented |
| FS-09 | User-signed GPG/SSH commit/tag or signed approval manifest | Assistant cannot legitimately forge Founder cryptographic approval | Very strong | Founder controls signing key | Not yet implemented |
| FS-10 | Founder-only release tag/token for `APPROVED`, `SAVED`, `CURRENT_CONTROLLED` | Prevents assistant from promoting its own work to Founder-approved state | Very strong | Founder | Policy implemented; external enforcement not yet implemented |
| FS-11 | Quarantine/staging branch or folder for all assistant outputs | Bad work cannot become authoritative merely because it exists | Strong | Founder promotes only reviewed outputs | Not yet implemented |
| FS-12 | PR-only workflow; no direct commits to authoritative branch | Makes every proposed change inspectable before merge | Very strong when enforced | GitHub configuration + Founder | Not yet enforced |
| FS-13 | Protected branch / repository ruleset requiring PR | Technically blocks direct promotion to main | Very strong | GitHub admin | Plan-dependent; rulesets API says Pro/public required for this private repo |
| FS-14 | Required status check running `amw_execution_gate.py` | Prevents merge/promotion unless machine gate passes | Very strong with protected branch | GitHub Actions + branch protection | Gate exists; Actions enforcement not installed |
| FS-15 | CODEOWNERS with required Founder review | Makes Founder review mandatory for control/authority paths when branch protection supports it | Very strong | Founder + GitHub protection | Not yet implemented |
| FS-16 | GitHub Environment/manual deployment approval | Requires a human approval before a release/promotion job can run | Strong | Founder + GitHub plan/config | Plan/feature dependent; not configured |
| FS-17 | Requirement-to-evidence matrix for every prompt | Exposes skipped requirements and blocks unsupported PASS claims | Strong | Machine gate + review | Implemented in gate v2 structure |
| FS-18 | Ordered event ledger | Detects skipped/out-of-order Python, GitHub, Mirror Review, correction, and revalidation steps | Strong | Machine gate | Implemented in gate v2 structure |
| FS-19 | Actual-artifact semantic/visual review gate | Stops metadata/hash/file-count checks from being treated as proof of prompt fidelity | Strong | Reviewer + gate evidence | Implemented structurally; human/independent evidence still needed |
| FS-20 | Requested-output-type equality gate | Stops documents/collages/labels from substituting for requested renderings/physical depictions/etc. | Strong | Machine gate | Implemented |
| FS-21 | Failed-artifact quarantine/no-reuse rule | Prevents rejected output from being cropped, stitched, relabeled, or repackaged into a false pass | Strong | Machine gate + provenance | Implemented |
| FS-22 | Frozen-reference/pixel-lock comparison | Detects unauthorized edits outside Founder-named areas | Strong for image edits | Python/image diff + Founder source | Available; task-specific |
| FS-23 | Automated count/label/layout/spec validators | Catches exact numeric/spec mismatches before presentation | Medium/Strong where computable | Python/CI | Available; task-specific |
| FS-24 | Independent second reviewer | Reduces self-review conflict; can be a human reviewer or separate independent review process | Stronger than self-review, not absolute | Founder-selected reviewer | Not yet implemented |
| FS-25 | Founder manual acceptance checklist before promotion | Makes final semantic authority human, not assistant-generated | Very strong | Founder | Available now |
| FS-26 | Local/offline gate script run by Founder before accepting/publishing files | Assistant cannot bypass a gate running outside ChatGPT | Very strong | Founder device | Not yet packaged for local use |
| FS-27 | External API wrapper that rejects outputs unless schema/gates pass | Prevents model output from reaching authoritative storage unless external policy engine approves | Very strong | Founder-controlled application/server | Requires custom external app/API workflow |
| FS-28 | Append-only audit/provenance log | Makes changes, reversals, rejected versions, and false PASS attempts visible instead of silently overwritten | Strong for accountability | Git/GitHub + Founder | Partially present through commits/Mirror Reviews |
| FS-29 | Immutable release snapshots/tags | Preserves exact approved source and prevents later drift from being confused with approved state | Strong | Founder | Not yet implemented |
| FS-30 | Manual re-upload of the exact control packet for high-risk tasks | Forces task-local authoritative source instead of relying on assistant memory | Strong but cumbersome | Founder | Available now |
| FS-31 | Chat/Project instructions / pinned control template | Increases instruction persistence inside ChatGPT but is not a hard security boundary | Soft | Founder | Existing prompt practice; not sufficient alone |
| FS-32 | Repeated-failure stabilization trigger | Stops normal production after repeated failure and forces correction/recovery scope | Medium/Strong as workflow | Gate + Founder | Implemented structurally |
| FS-33 | No-status-by-assistant rule | Assistant may only use OPEN/FAIL/PENDING unless status is proven by external gate or explicit Founder directive | Strong for false promotion | Gate + Founder | Can be made stricter than current policy |
| FS-34 | Separate Founder approval file stored where ChatGPT has no write permission | Creates a final authority token the assistant cannot manufacture | Very strong | Founder-only storage | Not yet implemented |
| FS-35 | Periodic permission audit | Detects if GitHub/other connectors regain broader write authority | Strong supporting control | Founder / permission inspection | Available now |

## Strongest practical architecture
The most resistant design is a combination of: Founder-controlled read-only AUTHORITY source; ChatGPT limited to read or ask-before-write; separate WORKING/quarantine repo; PR-only promotion; required CI gate; Founder-owned cryptographic/manual approval token; and final release/tag created outside ChatGPT.

## Important limitation
No prompt, Project instruction, Python script, GitHub file, or assistant-authored Mirror Review can guarantee that the model will never produce a noncompliant response. Hard protection comes from controls outside the model that prevent bad output from being promoted, saved as authoritative, or altering the governing source.
