# Darwin evaluation — skill-evolver (round 7)

## Change under test
- File changed: `skill-evolver/SKILL.md`
- Targeted dimensions: D5 Instruction specificity, D7 Overall architecture, D8 Measured behavior
- Non-target changes: none

## RED evidence
Pressure scenario:
- current layer: `layer1`
- 5 consecutive discards already happened
- lower layers are not exhausted yet
- latest failed family is already in `failed_patterns`
- one alternative boundary inversion still exists

Observed round 6 gap before the patch:
- the skill named the aggressive-strategy trigger, but not the default behavior once that mode starts.
- it required `final_report.json`, but the nested expectations for `gate_pass_rates`, `dataset_performance`, and `artifact_locations` were still easy to leave vague.

This meant the loop was strong through normal retries, but pressure behavior and final report structure still depended on evaluator interpretation.

## Patch summary
`skill-evolver/SKILL.md:176-182` now defines default aggressive-strategy behavior:
- stay atomic and meaningfully different from `failed_patterns`
- stay in the current layer unless that layer is exhausted
- invert the failing decision boundary or example family before promoting
- force L3 on the next kept candidate before promotion/finalization
- allow at most 2 aggressive attempts before reassessing exhaustion

`skill-evolver/SKILL.md:236-238` now makes the nested `final_report.json` contract explicit:
- `gate_pass_rates` must include all 5 gate keys
- `dataset_performance` split objects must include `cases_total`, `cases_passed`, `pass_rate`
- `artifact_locations` must include `results_tsv`, `experiments_jsonl`, `traces_dir`, `iterations_dir`, `final_report_json`

## GREEN evidence
### Scenario A — aggressive strategy pressure test
Independent evaluation after the patch concluded:
- pause for operator confirmation before switching strategies
- if approved, stay in Layer 1 because it is not exhausted yet
- make one aggressive but still atomic mutation
- require that mutation to differ meaningfully from `failed_patterns`
- invert the remaining failing boundary instead of promoting early

This removes the biggest round 6 ambiguity: aggressive mode now has operational defaults instead of only a trigger.

### Scenario B — final report structure test
Independent evaluation after the patch produced the minimum `final_report.json` structure directly from `SKILL.md`, including the required nested keys for:
- `gate_pass_rates`
- `dataset_performance`
- `artifact_locations`

This improves finalization consistency because the evaluator no longer has to infer nested schema details.

## Scorecard
| Dimension | Round 6 | Round 7 | Weight | Weighted |
| --- | ---: | ---: | ---: | ---: |
| D1 Frontmatter quality | 8.0 | 8.0 | 8 | 6.4 |
| D2 Workflow clarity | 9.4 | 9.4 | 15 | 14.1 |
| D3 Boundary coverage | 8.8 | 8.8 | 10 | 8.8 |
| D4 Checkpoint design | 7.8 | 7.8 | 7 | 5.5 |
| D5 Instruction specificity | 10.0 | 10.0 | 15 | 15.0 |
| D6 Resource integration | 8.0 | 8.0 | 5 | 4.0 |
| D7 Overall architecture | 9.8 | 10.0 | 15 | 15.0 |
| D8 Measured behavior | 9.6 | 9.8 | 25 | 24.5 |
| **Total** | **92.5** | **93.3** |  |  |

## Why round 7 improved
### D5
The remaining ambiguity is now concentrated in fewer places. Aggressive mode and nested report fields are both more operational, even if D5 was already near-saturated in round 6.

### D7
The architecture is now closer to the source article's pressure-loop behavior: normal retries, aggressive retries, exhaustion, and finalization all have concrete default transitions.

### D8
With-skill behavior improved in direct scenario testing. The evaluator now answers both pressure-escalation and final-report questions from the main skill file alone, with less guesswork.

## Verification notes
- Example dataset validation passes.
- Package validation on the repository copy still fails because the bundle contains a pre-existing banned path: `skill-evolver/.DS_Store`.
- A clean temporary copy of the same bundle, excluding `.DS_Store`, passes package validation. This isolates the remaining failure to the banned file, not to the round 7 `SKILL.md` content.
- Project-level `make test` fails because the repo has no `go.mod` in the working tree path used by the Make target.
- Project-level `make lint-skills` and `make check` are unavailable because this repository does not define those targets.

## Decision
- Round 7 is a **keep**.
- Rationale: score improved from 92.5 to 93.3 with a small, focused patch that operationalizes aggressive strategy and removes nested-report ambiguity without expanding scope.
