# MR-2026-09-25 — Visual Generation Attempt Preservation / Repeated-Failure Fail-Stop

**Status:** Assistant execution correction / Mirror Review evidence. This record does not supersede Founder controls; existing Founder-controlled architecture remains controlling.

## Trigger
Founder identified that repeated invalid, duplicate, and noncompliant image-generation attempts consumed available visual-generation opportunities before a compliant rendering was produced. Screenshot evidence shows the current UI state: image creation unavailable for now, with `Try again at 11:59 PM.`

- Founder prompt SHA-256: `bdebe1685ae666874c950f3cc3fbc73d28142e8fd8fba72290cd112af606d5a7`
- Screenshot SHA-256: `a033ce7efd6011e69f0948807a3b39720e098da4708ebb4b1fa0ff8605203e46`

## Existing controls cross-referenced
- ML-009 — Visual Rendering Completeness & Preflight Full-Stop
- ML-012 — Repeated Failure Escalation & Output Hold
- ML-014 — Pre-Tool Generation Fail-Stop / Context-Contamination Gate
- ML-018 — Pre-Presentation / Pre-Action Kill Switch
- ML-019 — Failure-Class Quarantine & Verified Re-Entry
- ML-020 — Automatic Error-Triggered Mirror Review
- ML-023 — Complete-Prompt Reading / Recursive Cross-Reference & Multi-Pass Mirror Review Gate

Current Master Lock authority already requires the same failure class to be held after recurrence, and requires controls to be re-read and a verification gate applied before another same-class output. Mirror Review history also records that repeated generation must stop rather than shifting quality-control back to the Founder.

## Failure class
1. Whole-project board/collage substituted for requested standalone rendering.
2. Same or materially duplicate failed composition regenerated repeatedly.
3. Image-generation retries continued after the failure class was already known.
4. Python crops/resizes/stretching were used as pseudo-renderings.
5. Non-editable or non-native outputs were presented.
6. Finished artifacts failed controls after generation.
7. Failed artifacts were quarantined only after an image-generation attempt had already been spent.
8. Repetition continued instead of invoking the existing output-hold/re-entry controls.

## Correction / strengthening
Effective immediately for AMW Legacy visual execution:

1. Treat each image-generation call as a scarce execution attempt.
2. **No mass generation.**
3. **No repeated generation of a known failed or materially duplicate composition.**
4. Do not invoke image generation until the exact single-render target passes Python and GitHub preflight.
5. Use one rendering target per generation call unless the Founder explicitly asks for multiple.
6. If the generator returns the known failure class again, stop generation and quarantine the failure instead of repeatedly spending attempts.
7. Do not use a failed board/collage as an active source unless the Founder explicitly directs an edit of that exact image.
8. Do not use Python cropping, resizing, stretching, letterboxing, or contact-sheet construction to manufacture a replacement rendering.
9. Do not claim a replacement rendering exists until the actual generated artifact passes post-generation Python + GitHub + Mirror Review validation.
10. Rejected outputs remain provenance only. Rejection does not erase or recover the generation attempt already spent.

## Closure condition
This failure class is **OPEN / QUARANTINED** until the next requested Legacy rendering is produced through the corrected path without duplicate/mass retries and passes the finished-artifact validation before presentation as compliant.
