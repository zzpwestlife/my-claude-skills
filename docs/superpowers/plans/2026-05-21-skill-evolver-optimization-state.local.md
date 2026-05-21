# skill-evolver Path A Optimization — State Tracker

## Baseline (captured 2026-05-21 before Task 0 commit)

- SKILL.md line count: **239**
- references line counts: artifacts=66, dataset-format=37, distribution=30, runbook=20
- check_skill_package errors (pre-existing, OS-junk only): `.DS_Store` × 2 → out-of-scope for Path A

## Invariant fingerprints (must remain ≥ 1 after every task)

| Token | Baseline count |
| --- | --- |
| `structure_and_safety` | 2 |
| `dev_quality` | 2 |
| `strict_quality` | 3 |
| `cost_budget` | 2 |
| `atomic_auditability` | 2 |
| `counterfactual` | 3 |
| 8-phase arrow line | 1 |
| `Layer 1` | 1 |
| `Layer 2` | 1 |
| `Layer 3` | 4 |

## Tasks

- [x] Task 0 baseline captured
- [ ] Task 1 references/safety-rules.md
- [ ] Task 2 references/mutation-layers.md
- [ ] Task 3 references/evaluation-layers.md
- [ ] Task 4 references/eval-noise.md
- [ ] Task 5 references/dataset-format.md (append GT-gen)
- [ ] Task 6 SKILL.md surgical edits (6a-6f)
- [ ] Task 7 README.md rationale line
- [ ] Task 8 check_skill_package.py REQUIRED_FILES update
- [ ] Task 9 final verification matrix

## Failures / Surprises

- **Env note 2026-05-21**: shell-aliased `grep` (Claude Code snapshot) routes to ugrep with incompatible flags; using `/usr/bin/grep` directly throughout. Plan example commands assume normal `grep` — substitute as needed.
