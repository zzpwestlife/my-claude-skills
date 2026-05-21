# LLM Eval Noise Mitigation

LLM-judged assertions (`fact_coverage`, `llm_judge`) and overall pass-rate measurements drift across runs even when the skill state and GT are identical. Observed range can be ±0.10 on the same fixture.

## Default protocol

- **Repeat N**: every L2 / L3 evaluation that crosses a gate boundary is run **N = 3** times by default. Configurable in `evolve_plan.md` via `eval.repeat_n` (min 1, max 5).
- **Aggregation**: report median; record min, max, and per-run scores in `experiments.jsonl`.
- **Variance threshold**: if max − min > 0.05 on any aggregated metric, mark the result `noisy: true`.

## When to re-eval

Trigger an extra evaluation pass when **any** of:

- Iteration is provisionally a keep but margin to the kept checkpoint is < `eval.noise_margin` (default 0.02).
- `dev_pass_rate` is within 0.02 of the L3 trigger threshold (default 0.90).
- The proposer's `expected_fix` predicts a metric jump > 0.05 but observed jump is < 0.02 (the proposer's prediction failed; check whether the real signal is masked by noise).

## Cost trade-off

`N = 3` triples L2 token cost. The article reports this is the dominant cost driver. Reduce only when noise variance has been observed < 0.02 over 5 consecutive iterations on the current dataset.

## Out of scope

- Choosing a less stochastic judge model (decoupled from this skill).
- Fingerprinting the prompt for cache reuse (skill-creator's territory).
