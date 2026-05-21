# Darwin evaluation — skill-evolver (round 4)

## Change under test
- File changed: `skill-evolver/SKILL.md`
- Targeted dimensions: D5 Instruction specificity, D7 Overall architecture, D8 Measured behavior
- Non-target changes: none

## RED evidence
Pressure scenario:
- 3 recent `routing hint` keeps
- 4 recent `body rewrite` discards
- `case-12` failed 5 times in a row
- `case-7` regressed in the last 2 strict evaluations
- no keep in the last 5 iterations

Observed baseline problem before the patch:
- the skill named the five Review signals, but did not require a structured Review output.
- it did not define default thresholds for when a pattern becomes reusable, avoidable, persistent, fragile, or stuck.
- evaluators could infer the right behavior, but the contract was still loose.

## Patch summary
`skill-evolver/SKILL.md:80-98` now defines a required `review signal pack` with exactly five keys:
- `successful_patterns`
- `failed_patterns`
- `persistent_failures`
- `regression_guards`
- `stuck_state`

It also adds default thresholds:
- 2 keeps to reuse a mutation family
- 2 discards to avoid a mutation family
- 3 failures to mark a case persistent
- 2 regressions to promote a case to guard
- stuck after either 5 consecutive discards or 5 iterations with no keep

And it now requires Review to state how each signal changes Ideate.

## GREEN evidence
### Scenario A — review pressure test
After the patch, the evaluator produced a structured signal pack instead of an informal narrative, and it mapped each signal to a concrete Ideate consequence: what to reuse, what to avoid, which case to target first, which guard to carry, and whether stuck-state escalation applies.

### Scenario B — alternate diagnosis test
On a second scenario, the evaluator correctly kept `stuck_state=false` when there was still one keep in the last 5 rounds, while still prioritizing the persistent failure and guarding the fragile case.

This is a meaningful improvement: Review is now an explicit operator artifact, not just a loose thought process.

## Scorecard
| Dimension | Round 3 | Round 4 | Weight | Weighted |
| --- | ---: | ---: | ---: | ---: |
| D1 Frontmatter quality | 8.0 | 8.0 | 8 | 6.4 |
| D2 Workflow clarity | 8.8 | 9.0 | 15 | 13.5 |
| D3 Boundary coverage | 8.0 | 8.3 | 10 | 8.3 |
| D4 Checkpoint design | 7.5 | 7.5 | 7 | 5.3 |
| D5 Instruction specificity | 9.5 | 9.8 | 15 | 14.7 |
| D6 Resource integration | 8.3 | 8.2 | 5 | 4.1 |
| D7 Overall architecture | 9.1 | 9.4 | 15 | 14.1 |
| D8 Measured behavior | 8.9 | 9.2 | 25 | 23.0 |
| **Total** | **87.4** | **89.4** |  |  |

## Why round 4 improved
### D5
The Review phase now specifies both output structure and default thresholds. This reduces room for vague summaries and makes the signal extraction repeatable.

### D7
The architecture is closer to the source article's Review intent: the loop now has a formal memory-reading artifact before Ideate, not just a list of things to look at.

### D8
With-skill behavior improved in a practical way. The evaluator now answers review-stage operator questions by emitting a signal pack and directly connecting it to Ideate choices.

## Verification notes
- Bundle validation still passes after the round 4 edit.
- The Review signal pack still leaves some advanced policy out of scope, such as how large the "recent" window should be by default across all repos, or how to merge conflicting signals.
- Those are now secondary gaps rather than missing basics.

## Decision
- Round 4 is a **keep**.
- Rationale: score improved from 87.4 to 89.4 with a single-section patch that makes the Review phase materially more operational.
