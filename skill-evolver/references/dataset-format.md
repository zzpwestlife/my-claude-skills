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
