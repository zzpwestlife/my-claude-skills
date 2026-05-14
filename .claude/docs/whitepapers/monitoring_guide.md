# Token Monitoring Guide

This guide explains how to use the `.claude/scripts/token-analyzer.py` tool to monitor token usage and verify optimization results.

## Prerequisites

- Python 3.x
- Standard library (os, glob)

## Usage

Run the analyzer from the project root:

```bash
python3 .claude/scripts/token-analyzer.py
```

## Output Interpretation

The script analyzes `.md`, `.py`, `.sh`, and `.json` files in the `.claude/` directory and categorizes them into two groups:

1.  **ACTIVE CONTEXT (Hot)**
    - Files that are likely to be loaded by the Agent during normal operation.
    - Examples: `AGENTS.md`, `CORE_RULES.md`, high-level `SKILL.md` files.
    - **Goal**: Keep this number LOW to minimize cost and latency.

2.  **REFERENCE CONTEXT (Cold)**
    - Files that are available for on-demand lookup but not loaded by default.
    - Examples: `docs/references/`, `archive/`, `tmp/`, full-text backups (`_full.md`).
    - **Goal**: This can grow as needed without impacting daily performance.

## Optimization Metric

The script calculates an **OPTIMIZATION SAVINGS** percentage:
`Savings = (Total Tokens - Active Tokens) / Total Tokens * 100`

- **Target**: > 30%
- **Current**: ~41.5%

## Troubleshooting

If Active Context spikes unexpectedly:
1.  Run the analyzer to identify the top offending files.
2.  Check if a large reference file was accidentally added to a non-reference path.
3.  Move the large file to `.claude/docs/references/` or `.claude/docs/archive/`.
4.  Add a link in the original location if necessary.
