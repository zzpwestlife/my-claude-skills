# Iter 2 — Atomic fix for dev-1

## Phases
- [x] Phase 1 Review     — Iter 1 discarded due to atomic violation; same target case dev-1 remains
- [x] Phase 2 Ideate     — single-file proposal; counterfactual states fix path
- [x] Phase 3 Modify     — appended one Routes bullet to target_skill/SKILL.md (single file, single layer)
- [x] Phase 4 Commit     — workspace git checkpoint e7149be
- [x] Phase 5 Verify     — L1 OK; L2 simulated re-route flips dev-1 fail -> pass; no regressions
- [x] Phase 6 Gate       — 5/5 dims PASS (atomic touched=1)
- [x] Phase 7 Log        — this file + results.tsv row + experiments.jsonl row
- [x] Phase 8 Loop       — keep; remain in Layer 1; next iter probe-only

## Verdict: KEEP
- All 5 cases now pass under simulated router (gt-1, dev-1, dev-2, holdout-1, reg-1)
- dev-1 0/2 -> 2/2 within dev split (was 1/2; now 2/2)
- Diff: target_skill/SKILL.md +1 line in Routes section

## Gate verdict per dimension
- structure_and_safety: PASS
- dev_quality:          PASS (dev-1 0/2 -> 2/2; others unchanged)
- strict_quality:       PROVISIONAL PASS (L3 not triggered)
- cost_budget:          PASS (N/A in B-Lite)
- atomic_auditability:  PASS (1 file, 1 layer)
