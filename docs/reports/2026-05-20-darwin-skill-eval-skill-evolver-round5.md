# Darwin evaluation — skill-evolver (round 5)

## Change under test
- File changed: `skill-evolver/SKILL.md`
- Targeted dimensions: D5 Instruction specificity, D7 Overall architecture, D8 Measured behavior
- Non-target changes: none

## RED evidence
Pressure scenario:
- `case-41` trace proved the request was wrongly routed to email classification
- GT pointed to `通讯录/删除或禁用成员`
- Review said routing hints recently kept and body rewrites recently discarded
- a regression guard existed

Observed baseline problem before the patch:
- the skill already required `failure_reason` and `expected_fix`, but it did not force a single explicit counterfactual sentence.
- evaluators could still comply in spirit while varying format and level of causal precision.

This meant Ideate was good, but not yet as hard-edged as the article's "counterfactual diagnosis before mutation" standard.

## Patch summary
`skill-evolver/SKILL.md:108-120` now adds a mandatory `counterfactual` field to the mutation proposal:
- exact form: `Case <id> failed because <observed cause>; if we change <specific mutation>, we expect <observable result>.`
- it must name the observed failure, the single proposed change, and the expected observable difference.
- if that sentence cannot be written from trace evidence, the iteration must be discarded before Modify.

## GREEN evidence
### Scenario A — ideate pressure test
After the patch, the evaluator emitted a proposal that included a concrete `counterfactual` sentence tying the routing error to a Layer 1 routing-hint change and an observable route change.

### Scenario B — alternate diagnosis test
On a second case about `如何进入内部群`, the evaluator again produced a complete proposal with a valid `counterfactual`, and explicitly justified why body rewrite was the wrong first move.

This is a material improvement: the skill now requires a visible causal hypothesis, not just adjacent fields.

## Scorecard
| Dimension | Round 4 | Round 5 | Weight | Weighted |
| --- | ---: | ---: | ---: | ---: |
| D1 Frontmatter quality | 8.0 | 8.0 | 8 | 6.4 |
| D2 Workflow clarity | 9.0 | 9.1 | 15 | 13.7 |
| D3 Boundary coverage | 8.3 | 8.4 | 10 | 8.4 |
| D4 Checkpoint design | 7.5 | 7.5 | 7 | 5.3 |
| D5 Instruction specificity | 9.8 | 10.0 | 15 | 15.0 |
| D6 Resource integration | 8.2 | 8.1 | 5 | 4.1 |
| D7 Overall architecture | 9.4 | 9.6 | 15 | 14.4 |
| D8 Measured behavior | 9.2 | 9.4 | 25 | 23.5 |
| **Total** | **89.4** | **90.8** |  |  |

## Why round 5 improved
### D5
The mutation protocol is now stricter and more testable. It requires one explicit causal sentence rather than relying on the evaluator to synthesize one from neighboring fields.

### D7
The architecture is closer to the article's trace-driven diagnosis standard: Review produces signals, Ideate must now translate trace evidence into a falsifiable hypothesis.

### D8
With-skill behavior improved in direct testing. The evaluator now produces visibly better mutation proposals by default, especially on routing errors where the first-hop change should be explicit.

## Verification notes
- Bundle validation still passes after the round 5 edit.
- The main remaining gaps are not in Ideate anymore; they are mostly in Loop / escalation defaults and final reporting structure.

## Decision
- Round 5 is a **keep**.
- Rationale: score improved from 89.4 to 90.8 with a small but meaningful patch that hardens Ideate into an explicit counterfactual protocol.
