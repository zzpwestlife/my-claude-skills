# Artifact Contract

Keep artifacts local, inspectable, and append-friendly.

## `baseline.json`

Minimum fields:

- `skill_dir`
- `dataset_dir`
- `workspace_dir`
- `git_status`
- `baseline_eval`

## `evolve_plan.md`

Minimum sections:

- Paths
- Target metric
- Evaluation strategy
- Gate thresholds
- Starting mutation layer
- Stop conditions

## `results.tsv`

Minimum columns:

```text
iteration	status	checkpoint_id	failed_stage	failed_dimensions	rollback_performed
```

## `experiments.jsonl`

Append one object per iteration with:

- `iteration`
- `status`
- `checkpoint_id`
- `proposal`
- `verification`
- `gate`
- `rollback`

## `.skill_evolve/traces/`

Store raw or structured per-case traces. Each failed case referenced by a mutation proposal must have a trace path that exists or can be opened from this index.

## `.skill_evolve/iterations/`

Write one iteration summary per loop, such as `iteration-001.json`. Include phase order, proposal, changed files, verification result, gate decision, rollback result, and next loop decision.

## `.skill_evolve/final_report.json`

Minimum fields:

- `stop_reason`
- `best_checkpoint`
- `kept_count`
- `discarded_count`
- `rollback_count`
- `gate_pass_rates` with keys `structure_and_safety`, `dev_quality`, `strict_quality`, `cost_budget`, and `atomic_auditability`
- `dataset_performance` with split objects for `dev`, `holdout`, and `regression` when those datasets exist; each split should include at least `cases_total`, `cases_passed`, and `pass_rate`
- `artifact_locations` with at least `results_tsv`, `experiments_jsonl`, `traces_dir`, `iterations_dir`, and `final_report_json`
- `next_recommendation`
