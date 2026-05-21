# Iter 3 — Probe only

## Phases
- [x] Phase 1 Review     — Iter 2 kept; all 5 cases pass; no remaining failures
- [x] Phase 2 Ideate     — no proposal (probe only)
- [N/A] Phase 3 Modify
- [N/A] Phase 4 Commit
- [x] Phase 5 Verify     — re-ran simulated eval; 5/5 stable
- [x] Phase 6 Gate       — N/A (no mutation to gate); recorded as PROBE
- [x] Phase 7 Log        — this file + results.tsv row + experiments.jsonl row
- [x] Phase 8 Loop       — budget exhausted (3/3); proceed to final report

## Verdict: PROBE (no mutation, no keep/discard)

## Boundary observation (out-of-scope for B-Lite)
The simulated router's keyword heuristic is ordered (access > billing > account). A hypothetical input "Why did my profile permissions change?" would match both 'profile' (account) and 'permission' (access), with access winning by ordering. Recommendation: when a richer GT exists (Path B-Build or B-Real), add disambiguation cases.

## Stability
- 5/5 = 1.00, identical to iter-2 result. Toy fixture is fully deterministic; eval noise N/A.
