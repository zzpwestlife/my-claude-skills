---
description: Review specified code files or directories with a fresh perspective (Opus model). Ideally run in a new session.
argument-hint: [path_to_review | diff] [output_dir]
model: opus
allowed-tools: [AskUserQuestion, Read, Grep, Glob, RunCommand, Bash, Write]
---

# Code Review Command

**Best Practice**:
> **⚠️ Critical**: For an objective review, please run this command in a **NEW SESSION** (`/new`).
> This ensures the AI reviews the code as a fresh observer, without context bias from the development session.

**Mode Detection**:
- `diff` (or empty): Incremental Git Review (`git diff main...HEAD`).
- `path`: Full File Review.

**Process**:
1. **Static Analysis**: `go vet`, `flake8`, etc.
2. **Deep Review (Opus)**: Check Clarity, Simplicity, Style, Architecture.
3. **Report**: Save to `{output_dir}/CODE_REVIEW.md`.

**Handoff (MANDATORY TUI)**:
- **Options**:
  1. Generate Changelog (`/changelog-generator`)
  2. Fix Critical Issues (`/write-plan`)
  3. Manual Verification

> For detailed instructions, see `.claude/docs/references/commands/review_code_full.md`
