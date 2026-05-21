# Darwin evaluation — skill-evolver (round 3)

## Change under test
- File changed: `skill-evolver/SKILL.md`
- Targeted dimensions: D5 Instruction specificity, D7 Overall architecture, D8 Measured behavior
- Non-target changes: none

## RED evidence
Pressure scenario:
- L1 passed
- dev pass rate reached 0.91
- this was iteration 4
- current layer was about to be promoted
- holdout and regression datasets existed

Observed baseline problem before the patch:
- the skill said L3 runs on trigger conditions, but did not define usable defaults for `every N iterations` or `dev pass rate above threshold`.
- the skill said L2 records per-case results, but did not require `id` or `input`.
- the skill did not inline the article-aligned assertion taxonomy, so evaluators had to infer or read references to know which checks are deterministic vs bounded LLM yes/no.

This meant the evaluation stack existed, but too much of its behavior lived outside the main contract.

## Patch summary
`skill-evolver/SKILL.md:173-185` now makes the evaluation layers more article-like:
- L1 now explicitly treats any critical safety finding as immediate fail.
- L2 now requires per-case fields: `id`, `input`, `actual output`, `expected output`, `assertion results`, `pass/fail`, `score`, `trace path`.
- L2 now inlines the default 8-assertion taxonomy.
- L3 now defines default triggers:
  - every 3 iterations
  - dev pass rate >= 0.90
  - before any layer promotion
  - before final validation/finalization
- L3 now states holdout + regression always run when those datasets exist, and blind A/B is optional by explicit request only.

## GREEN evidence
### Scenario A — evaluation-layer pressure test
After the patch, the evaluator answered the scenario directly from `SKILL.md`:
- it determined L3 must run because dev reached 0.91 and layer promotion was imminent.
- it listed the exact required L2 per-case fields.
- it split the 8 assertions into programmatic vs bounded-LLM groups.

This is a concrete improvement over the RED state, where important behavior was still implicit or delegated to references.

### Scenario B — setup/eval scenario
After the patch, the setup answer became more specific about how L1/L2/L3 trigger during a real run, including the new default L3 triggers and the operator checkpoint after Phase 0.

## Scorecard
| Dimension | Round 2 | Round 3 | Weight | Weighted |
| --- | ---: | ---: | ---: | ---: |
| D1 Frontmatter quality | 8.0 | 8.0 | 8 | 6.4 |
| D2 Workflow clarity | 8.5 | 8.8 | 15 | 13.2 |
| D3 Boundary coverage | 8.0 | 8.0 | 10 | 8.0 |
| D4 Checkpoint design | 7.5 | 7.5 | 7 | 5.3 |
| D5 Instruction specificity | 9.1 | 9.5 | 15 | 14.3 |
| D6 Resource integration | 8.5 | 8.3 | 5 | 4.2 |
| D7 Overall architecture | 8.5 | 9.1 | 15 | 13.7 |
| D8 Measured behavior | 8.4 | 8.9 | 25 | 22.3 |
| **Total** | **84.3** | **87.4** |  |  |

## Why round 3 improved
### D5
The skill no longer leaves crucial evaluation behavior under-specified. Triggers and assertion types are now executable guidance, not implied context.

### D7
The architecture is now materially closer to the article's "3-layer evaluation" idea: not just names of layers, but a defined L1/L2/L3 contract and a concrete 8-assertion split.

### D8
With-skill behavior improved in a testable way. The evaluator can now answer practical operator questions from the main skill file alone, without leaning on references for core semantics.

## Verification notes
- Bundle validation still passes after the round 3 edit.
- The skill still intentionally keeps some advanced details out of the main contract, including score aggregation, assertion-result schema shape, and LLM judge reproducibility policy.
- Those remaining gaps are smaller and now clearly secondary.

## Decision
- Round 3 is a **keep**.
- Rationale: score improved from 84.3 to 87.4 with a single-section patch that brings the evaluation stack closer to the source article.
