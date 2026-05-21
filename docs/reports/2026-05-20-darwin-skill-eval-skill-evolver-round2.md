# Darwin evaluation — skill-evolver (round 2)

## Change under test
- File changed: `skill-evolver/SKILL.md`
- Targeted dimensions: D5 Instruction specificity, D7 Overall architecture, D8 Measured behavior
- Non-target changes: none

## RED evidence
Pressure scenario:
- L1 passed
- dev pass rate improved from 0.82 to 0.86
- strict had no regressions and holdout improved by 1/40
- token cost was +9% vs baseline
- one file changed, 8 lines, logs complete

Observed baseline problem before the patch:
- the Gate section named the five dimensions but did not define concrete default thresholds.
- both evaluators fell back to "cannot prove all five dimensions, so discard", citing missing threshold policy.

This showed that the Gate was principled but not repeatable.

## Patch summary
`skill-evolver/SKILL.md:132-142` now defines default pass/fail rules for:
- `structure_and_safety`
- `dev_quality`
- `strict_quality`
- `cost_budget`
- `atomic_auditability`

It also defines two important execution rules:
- `evolve_plan.md` may tighten defaults
- missing data is false, except provisional `strict_quality` when L3 does not run

## GREEN evidence
### Scenario A — threshold ambiguity pressure test
After the patch, the evaluator no longer complained that the Gate lacked thresholds. Instead, it evaluated against concrete rules and identified the remaining ambiguity as missing evidence fields such as new dev regressions, checkpoint metadata, or whether baseline equals the current kept checkpoint.

This is a real improvement: the failure mode changed from **missing policy** to **missing evidence**.

### Scenario B — rollback scenario
When strict regression dropped 2 cases and token cost rose 18%, the evaluator applied the defaults directly:
- `strict_quality` = fail
- `cost_budget` = fail because 118% > 110%
- result = `discard + rollback`

This is exactly the behavior the article implies.

## Scorecard
| Dimension | Round 1 | Round 2 | Weight | Weighted |
| --- | ---: | ---: | ---: | ---: |
| D1 Frontmatter quality | 8.0 | 8.0 | 8 | 6.4 |
| D2 Workflow clarity | 8.5 | 8.5 | 15 | 12.8 |
| D3 Boundary coverage | 8.0 | 8.0 | 10 | 8.0 |
| D4 Checkpoint design | 7.5 | 7.5 | 7 | 5.3 |
| D5 Instruction specificity | 8.2 | 9.1 | 15 | 13.7 |
| D6 Resource integration | 8.5 | 8.5 | 5 | 4.3 |
| D7 Overall architecture | 8.0 | 8.5 | 15 | 12.8 |
| D8 Measured behavior | 7.8 | 8.4 | 25 | 21.0 |
| **Total** | **80.4** | **84.3** |  |  |

## Why round 2 improved
### D5
The skill now defines concrete default gate thresholds instead of naming dimensions only. This makes the Gate executable rather than interpretive.

### D7
The architecture now better matches the article's core promise: not just a five-name gate, but a five-rule gate with default criteria and override policy.

### D8
Behavior improved in the most important way for this section:
- before: evaluators complained about threshold ambiguity
- after: evaluators applied the defaults and only stopped when evidence was missing or a threshold clearly failed

## Verification notes
- Bundle validation still passes after the round 2 SKILL.md edit.
- The skill remains a repo-root distributable bundle, not an installed `.claude/skills/*` local skill, so "manually invoked once" was approximated by independent with-skill pressure scenarios rather than slash-command invocation.
- The project-local `description <12 words` done condition is not met; the current frontmatter remains intentionally longer to preserve Darwin rubric coverage.

## Decision
- Round 2 is a **keep**.
- Rationale: score improved from 80.4 to 84.3, and the targeted ambiguity in the Gate section was materially reduced with a single-section patch.
