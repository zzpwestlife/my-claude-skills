# Dataset Format

Use JSONL files so cases can be appended and inspected with standard shell tools.

Required files:

- `gt.jsonl`: small smoke set for Phase 0 and L1.
- `dev.jsonl`: optimization split visible to the loop.
- `holdout.jsonl`: hidden strict split used only by L3.
- `regression.jsonl`: old or fragile cases that must not break.

Recommended case fields:

- `id`: stable case identifier.
- `input`: user request or task prompt.
- `expected`: expected answer, route, file path, behavior, or structured result.
- `actual`: latest observed answer or structured result, if already run.
- `trace`: path or URI for the raw execution trace.
- `assertions`: list of checks to run for the case.
- `notes`: optional human context.

Recommended assertion types:

- `contains`: output must include a literal string.
- `not_contains`: output must not include a literal string.
- `regex`: output must match a regular expression.
- `path_hit`: output must cite or select the expected path.
- `json_field`: structured output field must equal an expected value.
- `script_check`: run a local deterministic checker.
- `fact_coverage`: semantic yes/no coverage check.
- `llm_judge`: bounded yes/no semantic classification.

Trace rules:

- Every failed dev or strict case should point to a raw trace file.
- Mutation proposals must cite the trace path and the specific failure observed.
- Do not summarize away trace evidence before diagnosis; read the relevant raw trace first.

## Generating GT when you don't have one

If your skill has no curated GT yet, do not block — bootstrap one:

1. Use **skill-creator's eval generator** to draft an initial GT set against your skill's intended inputs. Treat its output as a candidate, not as ground truth.
2. Manually review at least the first 10 cases. Discard or rewrite any case whose `expected` is ambiguous or whose `assertion` cannot be made deterministic.
3. Split the reviewed set into `gt.jsonl` (the contract) and `dev.jsonl` (the optimization target). Keep `holdout.jsonl` and `regression.jsonl` empty until you have a stable dev pass-rate; populate them when the loop reaches first L3 trigger.
4. After the first 3 keeps in the loop, audit any case that the optimizer "fixed" with a Layer 1 trigger edit — those edits sometimes reveal that the GT case itself was under-specified.

The aim is a small, hand-trusted seed (10–30 cases). The loop's failure traces will tell you which cases to add next.
