# L1 Safety Rules

This is the canonical rule set scanned by L1 quick guard. Critical findings (★) cause immediate L1 fail; warnings are recorded into the iteration's findings buffer for Ideate to consider.

## Critical (★) — Auto-block

| ID | Pattern | Detect | Fix Hint |
| --- | --- | --- | --- |
| ★ R1 | Dangerous removal — `rm -rf` (especially with `/`, `$HOME`, `~`, `..`, env vars) | regex over `SKILL.md` and any file under `scripts/` | Replace with scoped per-path delete; never templated paths |
| ★ R2 | Hardcoded credentials — API key / token / secret / private key marker | regex over all bundle files: `(api[_-]?key|secret|token|BEGIN .* PRIVATE KEY)` | Move to env var or docs-only placeholder |

## Warning — Recorded, not blocking

| ID | Pattern | Detect | Fix Hint |
| --- | --- | --- | --- |
| R3 | Hardcoded absolute path (`/Users/...`, `/home/...`, `C:\\...`) | regex | Use relative paths or `${HOME}` |
| R4 | Mutation of global git config (`git config --global`, `git config user.*` outside workspace) | regex | Scope changes to the isolated workspace copy |
| R5 | Unbounded network call (`curl`/`wget` without explicit allow-listed host) | regex | Pin host or require explicit allow-list |
| R6 | Dynamic shell — `eval`, `bash -c "$VAR"`, `exec` of constructed strings | regex | Inline the command literally |
| R7 | Cross-layer file pattern (e.g. Layer 1 mutation touching `scripts/`) | declared `target_layer` vs `target_files` | Split into another iteration on the right layer |
| R8 | SKILL.md frontmatter missing required field (`name`, `description`) | YAML parse | Repair frontmatter |
| R9 | `description` field overflow (> 1024 chars) — undermines Claude trigger weighting | character count | Tighten and move detail into the body |
| R10 | Mutation modifies an audit artifact outside `evolve_plan.md` / `baseline.json` (e.g. rewriting `experiments.jsonl` history) | path match against artifact list | Append-only writes; never edit prior rows |
| R11 | Mutation proposal lacks any `trace_path` reference | proposal field check in Ideate | Discard the iteration before Modify |

## Levels

- ★ critical: L1 returns `fail`. Iteration is discarded before L2.
- warning: L1 returns `pass` with `findings: [...]`. Findings are passed to Phase 1 Review of the next iteration.

## Out of Scope (Path B)

Wiring R1–R11 into `scripts/` as auto-detection is deferred. This document defines the contract; runtime enforcement may rely on agent inspection until a checker script is added.
