# Darwin evaluation — skill-evolver (round 8)

## Change under test
- File changed: `skill-evolver/references/artifacts.md`
- Targeted dimensions: D6 Resource integration, D7 Overall architecture, D8 Measured behavior
- Non-target changes: none

## RED evidence
Observed round 7 gap before the patch:
- the main `SKILL.md` had already upgraded the `final_report.json` contract to use `gate_pass_rates`, `artifact_locations`, and explicit nested minimum schema.
- the supporting reference `references/artifacts.md` still documented the older shape: `gate_pass_rate`, `artifacts`, `summary`, and `outcomes`.

This created bundle-internal contract drift. An evaluator reading the reference file could still pick the wrong field names or a weaker report structure even though the main skill had already moved forward.

## Patch summary
`skill-evolver/references/artifacts.md:54-64` now aligns the supporting reference with the authoritative contract in `skill-evolver/SKILL.md`:
- replace old top-level fields with `stop_reason`, `best_checkpoint`, `kept_count`, `discarded_count`, `rollback_count`, and `next_recommendation`
- rename `gate_pass_rate` to `gate_pass_rates` and require all 5 gate keys
- rename `artifacts` to `artifact_locations`
- require nested split metrics for `dataset_performance`
- require explicit location keys under `artifact_locations`

## GREEN evidence
### Scenario A — reference lookup test
After the patch, an evaluator reading `references/artifacts.md` alone now gets the same `final_report.json` field names as the main `SKILL.md`. The supporting file no longer points to the outdated `gate_pass_rate` / `artifacts` schema.

### Scenario B — package consistency test
The bundle still passes package validation after the doc-only patch, which means the reference alignment introduced no packaging regression.

## Scorecard
| Dimension | Round 7 | Round 8 | Weight | Weighted |
| --- | ---: | ---: | ---: | ---: |
| D1 Frontmatter quality | 8.0 | 8.0 | 8 | 6.4 |
| D2 Workflow clarity | 9.4 | 9.4 | 15 | 14.1 |
| D3 Boundary coverage | 8.8 | 8.8 | 10 | 8.8 |
| D4 Checkpoint design | 7.8 | 7.8 | 7 | 5.5 |
| D5 Instruction specificity | 10.0 | 10.0 | 15 | 15.0 |
| D6 Resource integration | 8.0 | 8.2 | 5 | 4.1 |
| D7 Overall architecture | 10.0 | 10.0 | 15 | 15.0 |
| D8 Measured behavior | 9.8 | 9.8 | 25 | 24.5 |
| **Total** | **93.3** | **93.4** |  |  |

## Why round 8 improved
### D6
The bundle is more internally consistent. The reference file now reinforces the same schema the main skill already requires, so operators and evaluators are less likely to pick outdated field names.

### D7
No architectural behavior changed, which is correct for this round. The improvement is consistency, not a new loop rule.

### D8
Behavior is effectively unchanged, but the risk of reference-driven schema drift is lower. That makes final-report generation slightly more robust without changing the protocol itself.

## Verification notes
- Package validation passes after the round 8 edit.
- Example dataset validation passes after the round 8 edit.
- This round intentionally avoids changing the main `SKILL.md`; it only reconciles the supporting artifact reference with the already-kept main contract.

## Decision
- Round 8 is a **keep**.
- Rationale: score improved from 93.3 to 93.4 with a low-risk patch that removes bundle-internal contract drift and strengthens resource consistency.
