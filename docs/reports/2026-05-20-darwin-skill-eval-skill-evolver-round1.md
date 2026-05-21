# Darwin evaluation — skill-evolver (round 1)

## Change under test
- File changed: `skill-evolver/SKILL.md`
- Targeted dimensions: D4 Checkpoint design, D3 Boundary coverage, D1 Frontmatter quality
- Non-target changes: none

## Scorecard
| Dimension | Round 0 | Round 1 | Weight | Weighted |
| --- | ---: | ---: | ---: | ---: |
| D1 Frontmatter quality | 6.0 | 8.0 | 8 | 6.4 |
| D2 Workflow clarity | 8.5 | 8.5 | 15 | 12.8 |
| D3 Boundary coverage | 6.0 | 8.0 | 10 | 8.0 |
| D4 Checkpoint design | 3.0 | 7.5 | 7 | 5.3 |
| D5 Instruction specificity | 8.0 | 8.2 | 15 | 12.3 |
| D6 Resource integration | 8.5 | 8.5 | 5 | 4.3 |
| D7 Overall architecture | 7.5 | 8.0 | 15 | 12.0 |
| D8 Measured behavior | 7.0 | 7.8 | 25 | 19.5 |
| **Total** | **70.7** | **80.4** |  |  |

## Why round 1 improved
### D1
- Frontmatter now states when not to use the skill and includes concrete examples.
- This directly addresses the rubric gap from round 0.

### D3
- `skill-evolver/SKILL.md:12` now adds explicit downgrade routes for dataset-only, package-only, and eval-only requests.
- This makes mis-trigger handling concrete instead of implied.

### D4
- `skill-evolver/SKILL.md:48` adds a dedicated `Operator Checkpoints` section.
- It forces pause points after setup, after baseline, before Layer 3, before aggressive strategy, and before finalization.
- Score does not go to 10 because the pauses are explicit but not yet coupled to a concrete UI contract.

### D8
- In the setup-plan prompt, with-skill responses now surface the operator checkpoint after Phase 0 and before the first mutation.
- In the gate/rollback prompt, with-skill responses now mention operator confirmation before switching to aggressive strategy.
- The lift is real but moderate, because the baseline assistant already answered the core logic fairly well.

## Verification notes
- Dataset validation passed on the bundled example dataset.
- Package validation still fails, but the failure is due to pre-existing banned `.DS_Store` files in the bundle, not the SKILL.md text change from this round.

## Decision
- Round 1 is a **keep**.
- Rationale: score improved from 70.7 to 80.4 with a single-file, single-purpose change.
