# Darwin evaluation — skill-evolver (round 6)

## Change under test
- File changed: `skill-evolver/SKILL.md`
- Targeted dimensions: D5 Instruction specificity, D7 Overall architecture, D8 Measured behavior
- Non-target changes: none

## RED evidence
Pressure scenario:
- layer1
- 5 consecutive discards
- 3 recent iterations with no keep
- remaining iteration budget = 4
- holdout and regression exist
- no layer explicitly exhausted yet

Observed baseline problem before the patch:
- the skill clearly named the loop directions, but did not define a default threshold for `repeated no-keep iterations`.
- `layer exhausted` was implied but not operationalized.
- `final_report.json` content was described narratively, not as a minimum schema.

This meant the loop looked right, but escalation and stop/finalization still depended on operator interpretation.

## Patch summary
`skill-evolver/SKILL.md:166-175` now defines default loop / escalation rules:
- move to next layer after 3 iterations in the same layer with no keep
- switch to aggressive strategy after 5 consecutive discards, but only after the operator checkpoint
- stop after all layers are exhausted or budget is reached
- higher layers become eligible only after lower layers are exhausted, unless trace evidence already proves the failure lives in helper material

`skill-evolver/SKILL.md:181-194` now defines:
- a concrete `layer exhausted` test with 3 required conditions
- a minimum `final_report.json` structure with required fields

## GREEN evidence
### Scenario A — loop / escalation pressure test
After the patch, the evaluator no longer had to infer the rules. It concluded:
- do not stop yet
- prepare aggressive strategy because 5 consecutive discards are explicit
- do not skip directly to a higher layer unless exhaustion conditions are met
- use the new 3-part exhausted test for layer decisions

### Scenario B — finalization scenario
When iteration budget was exhausted and datasets had all been evaluated, the evaluator correctly treated stop as mandatory and produced the minimum `final_report.json` field structure directly from `SKILL.md`.

This is a meaningful improvement: the loop now has concrete default escalation and termination behavior.

## Scorecard
| Dimension | Round 5 | Round 6 | Weight | Weighted |
| --- | ---: | ---: | ---: | ---: |
| D1 Frontmatter quality | 8.0 | 8.0 | 8 | 6.4 |
| D2 Workflow clarity | 9.1 | 9.4 | 15 | 14.1 |
| D3 Boundary coverage | 8.4 | 8.8 | 10 | 8.8 |
| D4 Checkpoint design | 7.5 | 7.8 | 7 | 5.5 |
| D5 Instruction specificity | 10.0 | 10.0 | 15 | 15.0 |
| D6 Resource integration | 8.1 | 8.0 | 5 | 4.0 |
| D7 Overall architecture | 9.6 | 9.8 | 15 | 14.7 |
| D8 Measured behavior | 9.4 | 9.6 | 25 | 24.0 |
| **Total** | **90.8** | **92.5** |  |  |

## Why round 6 improved
### D5
The loop and stop logic now have concrete defaults instead of narrative intent. This closes one of the last major ambiguity pockets.

### D7
The architecture is now much closer to the source article's outer loop: review, proposal, gate, escalation, and stop/finalization all have default operational behavior.

### D8
With-skill behavior improved in direct testing. The evaluator now answers escalation and finalization questions from the main skill file alone, with less guesswork and more consistent decisions.

## Verification notes
- Bundle validation still passes after the round 6 edit.
- The remaining gaps are now relatively minor: exact aggressive-strategy content, internal schemas for nested report fields, and optional visualization/report polish.

## Decision
- Round 6 is a **keep**.
- Rationale: score improved from 90.8 to 92.5 with a focused patch that operationalizes loop escalation and final reporting.
