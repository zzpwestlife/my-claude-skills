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
- [x] Task 1 references/safety-rules.md (3cf5b0e, 33 lines)
- [x] Task 2 references/mutation-layers.md (16792a6, 39 lines)
- [x] Task 3 references/evaluation-layers.md (540336c, 53 lines)
- [x] Task 4 references/eval-noise.md (0d71fc8, 26 lines)
- [x] Task 5 references/dataset-format.md GT-gen append (9550881, +11 lines)
- [x] Task 6 SKILL.md surgical edits (dd4cd1e, 239→244)
- [x] Task 7 README.md rationale line (d1b85b4)
- [x] Task 8 check_skill_package.py REQUIRED_FILES update (a2cc5a8, 14→18 tracked)
- [x] Task 9 final verification matrix — 11/11 PASS

## Final state

- SKILL.md: 244 lines (baseline 239, +5 net for 3 new contract surfaces; AC1 ≤200 relaxed by user decision since hitting it would require deleting existing contract language)
- New references: 4 files, 151 lines total
- Dataset-format.md: 37 → 48 lines (+11 GT-gen section)
- README.md: +2 lines (meta-evolution rationale)
- check_skill_package: tracks 18 required files (was 14); pre-existing `.DS_Store` × 2 still flagged (out of Path A scope)

## Failures / Surprises

- **Env note 2026-05-21**: shell-aliased `grep` (Claude Code snapshot) routes to ugrep with incompatible flags; using `/usr/bin/grep` directly throughout. Plan example commands assume normal `grep` — substitute as needed.
- **Line-budget miss vs plan**: AC1 target ≤200 not achievable without removing contract language. User accepted relaxation to ≤244 (current). For a future Path A2, candidates to extract: Operator Checkpoints (~10 lines), final_report.json schema (~12 lines), Iteration Loop sub-section details (~50 lines, biggest but contract-heavy).
