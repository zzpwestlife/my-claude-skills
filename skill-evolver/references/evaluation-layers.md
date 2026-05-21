# Evaluation Layers

Three tiers, cost-ascending. Cheap tiers run every iteration; expensive tiers run on triggers.

## L1 — Quick guard (seconds, every iteration)

Runs four programmatic checks:

1. `SKILL.md` structure — frontmatter present, required sections in place.
2. `quick_validate` from skill-creator — format / metadata sanity.
3. Safety scan — see `references/safety-rules.md` (11 rules; 2 critical, 9 warning).
4. GT smoke sample — randomly sample 3 GT cases and confirm structural soundness.

A single critical (★) safety finding causes immediate L1 fail; the iteration is discarded before L2.

## L2 — Dev eval (minutes, every iteration after L1 passes)

Runs the full dev split case-by-case. Records per-case `id`, `input`, `actual_output`, `expected_output`, `assertion_results`, `pass/fail`, `score`, `trace_path`.

### Assertion taxonomy (default)

Programmatic (deterministic, runs in code):

- `contains` — substring match
- `not_contains` — substring absence
- `regex` — pattern match
- `path_hit` — agent-cited file path matches expected (still programmatic when comparison is exact)
- `json_field` — extract field, compare value
- `script_check` — run a script, assert exit code

Bounded LLM YES/NO (LLM emits a label; pass rate is counted programmatically):

- `fact_coverage` — does the output cover stated facts? (LLM evaluates per-fact)
- `llm_judge` — single rubric question with YES/NO output

## L3 — Strict eval (~10 min, conditional)

Triggers (defaults; `evolve_plan.md` may override):

- Every 3 iterations.
- Whenever dev pass-rate ≥ 0.90.
- Before any layer promotion.
- Before final validation / finalization.

Datasets covered:

- **holdout** — never seen by the optimizer; the over-fit guard.
- **regression** — case set that must keep passing; the no-backslide guard.
- **blind A/B** (optional) — only when explicitly requested by the user or `evolve_plan.md`.

## Why three tiers, not one

L1 catches obvious damage cheaply. L2 catches behavioral regressions on the dev set. L3 catches over-fitting and silent regressions. Running L3 every iteration is wasteful; running only L3 means cheap iterations get expensive feedback. The split keeps wasted-iteration cost to L1 — typically seconds.
