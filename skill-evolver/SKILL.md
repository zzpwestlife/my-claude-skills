---
name: skill-evolver
description: Use when evolving or evaluating a local skill with GT/dev/holdout/regression data. Do not use when the user only wants dataset validation, package smoke checks, or a one-off review with no iteration loop. Example: improve a skill against dev and holdout splits; self-iterate a skill with trace-driven rollback.
---

# Skill Evolver

Use this skill to evolve a local skill against local evaluation data. This bundle is self-contained: use the workflow directly, and use the bundled `scripts/` helpers when deterministic setup or validation is useful. The core contract is the agent-run loop below: evidence first, one mutation at a time, verify before keeping, rollback on any failed gate.

Before modifying anything, inspect the target skill, dataset, output directory, and existing artifacts. If a target skill path, dataset path, or output directory is missing and cannot be inferred from the user request, ask for it.

If the user only wants dataset validation, run `python3 scripts/validate_dataset.py <dataset-dir> --json` and stop after reporting the result. If the user only wants a package or zip smoke check, run the bundle checks and stop after reporting the result. If the user only wants a one-off quality review with no iterative mutation loop, provide an evaluation summary and proposed next mutations, but do not enter Modify/Commit/Verify.

## Inputs

Required:

- Target skill directory containing `SKILL.md`.
- Dataset directory with GT/dev data and, when available, holdout/regression data.
- Output directory for workspace copies and audit artifacts.

Useful references:

- Dataset shape: read `references/dataset-format.md` when creating or validating evaluation data.
- Artifact shape: read `references/artifacts.md` when writing logs, traces, or reports.
- Distribution checks: read `references/distribution.md` when packaging or validating a zip bundle.
- Full local run sequence: read `references/runbook.md` when the user asks to run a complete evolution session.

## Phase 0: Setup

Run setup once per evolution run.

1. Confirm the target directory has `SKILL.md`.
2. Confirm the dataset directory exists and contains at least GT and dev data.
3. Create or confirm an isolated workspace copy before editing the target skill.
4. Detect git state: clean, dirty, not initialized, or git unavailable.
5. Create or confirm `baseline.json` with baseline evaluation status.
6. Create or confirm `evolve_plan.md` with evaluation strategy, gate thresholds, starting mutation layer, stop conditions, and artifact paths.

If deterministic setup is useful, use the bundled helper from the skill root:

```bash
python3 scripts/setup_workspace.py --skill-dir <target-skill> --dataset-dir <dataset> --output-dir <output>
```

The helper is optional. If it cannot run in the local environment, perform the same setup manually and write the artifacts.

## Operator Checkpoints

Pause and get operator confirmation at these checkpoints before continuing the loop:

1. After Phase 0 completes and `baseline.json` plus `evolve_plan.md` exist.
2. After the first baseline evaluation summary is written, before the first mutation.
3. Before promoting to Layer 3.
4. Before switching to aggressive strategy after five consecutive discards.
5. Before finalizing the best checkpoint and writing `final_report.json`.

If the user is unavailable, stop at the current checkpoint and report the recommended next action instead of guessing.

## Self-Contained Bundle Checks

When the skill is unpacked from a zip, first validate the bundle if the user asks for a smoke test or distribution check:

```bash
python3 scripts/check_skill_package.py . --json
python3 scripts/validate_dataset.py assets/example/dataset --json
python3 scripts/setup_workspace.py --skill-dir assets/example/target_skill --dataset-dir assets/example/dataset --output-dir /tmp/skill-evolver-smoke --json
```

These commands use only the Python standard library. They should not require any repository checkout, package install, or external dependency.

## Iteration Loop

Every iteration must run these phases in this exact order:

```text
Review -> Ideate -> Modify -> Commit -> Verify -> Gate -> Log -> Loop
```

### Review

Read the latest local evidence before proposing changes:

- Recent `git log` for checkpoints and repeated failed ideas.
- Recent `results.tsv` rows.
- Recent `experiments.jsonl` entries.
- Failed cases from the latest dev or strict evaluation.
- Trace index and trace files for those failed cases.

Extract a review signal pack before Ideate. The pack must name exactly these five signals:

- `successful_patterns`: mutations that recently kept and may be reused.
- `failed_patterns`: mutations that recently discarded and should be avoided.
- `persistent_failures`: case IDs that failed repeatedly and should be prioritized.
- `regression_guards`: fragile case IDs that recently regressed and must be protected.
- `stuck_state`: whether the loop is stuck, why, and which escalation rule is now relevant.

Use these defaults unless `evolve_plan.md` defines stricter review policy:

- Add a mutation family to `successful_patterns` only after at least 2 recent keeps.
- Add a mutation family to `failed_patterns` after at least 2 recent discards for the same family.
- Add a case to `persistent_failures` after at least 3 failed iterations for the same case.
- Add a case to `regression_guards` after at least 2 recent strict or dev regressions.
- Mark `stuck_state` true after either 5 consecutive discards or 5 iterations with no keep.

The Review output must say how each signal changes Ideate: what to reuse, what to avoid, which case to target first, which guards to carry forward, and whether to stay in layer, promote, or prepare aggressive strategy.

### Ideate

Produce exactly one mutation proposal. The proposal must include:

- `case_id`: the failed case being targeted.
- `trace_path`: the trace file used as evidence.
- `failure_reason`: what the trace proves went wrong.
- `expected_fix`: why the proposed mutation should change the outcome.
- `target_layer`: one of `layer1`, `layer2`, or `layer3`.
- `target_scope`: the allowed scope within that layer.
- `target_files`: the exact file or allowed file pattern to touch.
- `counterfactual`: one explicit sentence in this form: `Case <id> failed because <observed cause>; if we change <specific mutation>, we expect <observable result>.`

The `counterfactual` field is mandatory. It must name the observed failure, the single proposed change, and the expected observable difference in routing, output, assertion result, or pass/fail status. If that sentence cannot be written from trace evidence, discard the iteration before Modify.

Do not guess. If the proposal cannot cite trace evidence, discard the iteration before Modify and log the reason.

### Modify

Apply one atomic mutation only.

The one-sentence test: if describing the change requires "and", split it into another iteration. Keep the mutation within the selected layer. Do not mix trigger edits, body rewrites, and script/reference changes in the same iteration.

### Commit

Create a checkpoint after Modify and before Verify. Prefer git commits when the workspace is a git repository. If git is unavailable, create a reversible file snapshot in the output artifacts and record its path as the checkpoint.

### Verify

Run layered evaluation from cheapest to most expensive:

- L1 quick guard always runs.
- L2 dev eval runs only if L1 passes.
- L3 strict eval runs when triggered.

If L1 fails, stop immediately and mark the iteration discard. Do not run L2 or L3.

### Gate

Keep the mutation only if all five dimensions pass. Use these defaults unless `evolve_plan.md` defines stricter thresholds:

- `structure_and_safety`: pass only when L1 passes and reports zero critical safety findings.
- `dev_quality`: pass only when L2 pass rate is not lower than the current kept checkpoint and there are zero new dev regressions.
- `strict_quality`: when L3 runs, pass only when regression failures stay at zero and holdout pass rate is not lower than the current kept checkpoint. When L3 does not run for this iteration, treat `strict_quality` as pass for same-layer provisional keeps, but require a real L3 pass before layer promotion or finalization.
- `cost_budget`: pass only when total token cost is less than or equal to 110% of the current kept checkpoint unless `evolve_plan.md` sets a tighter budget.
- `atomic_auditability`: pass only when the mutation stays within one declared layer, touches no more than one file unless `target_files` explicitly allowed a pattern, and the iteration summary, traces, and checkpoint path are all present.

This is an AND gate, not a weighted score. Any false dimension means discard and rollback. Missing data is false, except the provisional `strict_quality` case above.

### Log

Write structured artifacts after every iteration, including discarded iterations:

- Append `results.tsv`.
- Append `experiments.jsonl`.
- Write iteration trace artifacts under `.skill_evolve/traces/`.
- Write iteration summaries under `.skill_evolve/iterations/`.

### Loop

After logging, decide one next action. Use these defaults unless `evolve_plan.md` defines stricter escalation rules:

- Continue in the same layer after a keep.
- Retry the same layer after a discard while layer budget remains.
- Move to the next layer after 3 iterations in the same layer with no keep.
- Switch to aggressive strategy after 5 consecutive discards, but pause at the operator checkpoint before doing so.
- Stop and write `final_report.json` after all layers are exhausted or the user-defined iteration budget is reached.

Aggressive strategy uses these defaults unless `evolve_plan.md` defines a stronger override:

- keep the mutation atomic, but require it to be meaningfully different from `failed_patterns`
- prefer the next eligible layer only if the current layer is exhausted; otherwise stay in the current layer and invert the failing decision boundary or example family
- do not skip directly to Layer 3 unless lower layers are exhausted or trace evidence already proves the failure lives in helper material
- force L3 on the next kept candidate before any further promotion or finalization
- allow at most 2 aggressive attempts before reassessing whether the current layer is exhausted

Treat a layer as exhausted when all three conditions are true:

- at least 3 trace-backed atomic attempts were made in that layer,
- none produced a keep,
- and Review cannot name a new counterfactual in that layer that is meaningfully different from prior failed patterns.

When all lower layers are exhausted, the next higher layer becomes eligible. Do not skip directly to Layer 3 unless lower layers are exhausted or trace evidence already proves the failure lives in helper material.

## Mutation Layers

Do not cross layers in a single iteration.

Layer 1 is low-cost trigger and routing work. It may edit only the target skill's trigger rules, invocation boundaries, routing hints, short examples, or compact usage guards inside `SKILL.md`.

Layer 2 is medium-cost skill body work. It may edit substantive workflow instructions, examples, refusal behavior, failure handling, or decision policy inside `SKILL.md`.

Layer 3 is high-cost support material work. It may edit only `scripts/*`, `references/*`, dataset adapters, or other bundled helper resources. Use Layer 3 only after lower layers are exhausted or trace evidence proves the failure lives in helper material.

## Evaluation Layers

L1 quick guard is programmatic and cheap. Check `SKILL.md` structure, required metadata, dangerous shell commands, hardcoded API keys, unsafe absolute paths, broad destructive operations, and a small GT smoke sample. Treat any critical safety finding as immediate fail.

L2 dev eval runs the dev split case by case. Record `id`, `input`, `actual output`, `expected output`, `assertion results`, `pass/fail`, `score`, and `trace path` for every case. Use this default assertion taxonomy unless the dataset defines a narrower set:

- Programmatic assertions: `contains`, `not_contains`, `regex`, `path_hit`, `json_field`, `script_check`
- Bounded LLM yes/no assertions: `fact_coverage`, `llm_judge`

L3 strict eval runs only on trigger conditions. Use these defaults unless `evolve_plan.md` defines stricter triggers:

- run every 3 iterations
- run when dev pass rate reaches 0.90 or higher
- run before any layer promotion
- run before final validation or finalization

L3 covers holdout and regression whenever those datasets exist. Add optional blind A/B comparison only when the user or `evolve_plan.md` explicitly requests it.

## Stop Rules

Stop the run when one of these is true:

- The user-defined iteration budget is reached.
- All layers are exhausted without improvement.
- There are no failed cases with usable trace evidence.
- The target metric has reached the planned threshold and strict evaluation passes.

Always write `final_report.json`. Use this minimum structure unless `evolve_plan.md` defines a richer schema:

- `stop_reason`
- `best_checkpoint`
- `kept_count`
- `discarded_count`
- `rollback_count`
- `gate_pass_rates` with keys `structure_and_safety`, `dev_quality`, `strict_quality`, `cost_budget`, and `atomic_auditability`
- `dataset_performance` with split objects for `dev`, `holdout`, and `regression` when those datasets exist; each split should include at least `cases_total`, `cases_passed`, and `pass_rate`
- `artifact_locations` with at least `results_tsv`, `experiments_jsonl`, `traces_dir`, `iterations_dir`, and `final_report_json`
- `next_recommendation`
