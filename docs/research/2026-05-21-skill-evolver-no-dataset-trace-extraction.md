# Research: skill-evolver — No-Dataset Mode & Trace Extraction

Date: 2026-05-21

## Current State

skill-evolver Phase 0 hard-requires a dataset directory with at least GT and dev splits.
Without it, the skill cannot enter the iteration loop and will stop at setup.

Evaluation layers:
- L1: programmatic (structure + safety scan). No dataset needed, but GT smoke sample requires dataset.
- L2: full dev split eval. Dataset required.
- L3: holdout + regression. Dataset required.

Claude Code log locations investigated:
- `~/.claude/debug/*.txt` — request metadata only (message count, token count). No content.
- `~/.claude/history.jsonl` — command input history. No assistant responses.
- `~/.claude/sessions/*.json` — session metadata (pid, cwd). No messages.
- No accessible conversation JSONL found.

## Constraints

1. L2/L3 evaluation cannot run without a dataset — no workaround.
2. No automatic log source for trace extraction — user must supply conversation text manually.
3. darwin-skill has an 8-dimension Rubric but is an external dependency.

## Risks

- Rubric scoring (LLM YES/NO) can be inconsistent if dimensions are loosely defined.
- Trace extraction is manual — adoption risk if friction is too high.
- Degraded mode score may diverge from actual skill quality if Rubric dimensions don't map to real failure modes.

## Decision Log

| Decision | Options Considered | Chosen | Why |
|----------|-------------------|--------|-----|
| Rubric source | darwin-skill reuse / internal 4-5 dim / inline LLM parse | Internal 4-5 dim | Avoid external dep; self-contained bundle |
| Degraded mode behavior | Evaluate only / full iteration loop with Rubric gate | Evaluate + suggestions, no loop | No GT = no way to verify mutations improve things |
| Integration style | Two independent modes / embed in Phase 0 | Two independent modes | Cleaner separation, no risk to existing flow |
| Log source for extraction | debug files / verbose mode / user paste | User paste | debug files contain no message content |
