---
description: 智能生成符合 Conventional Commits 规范的 commit message，支持双语解析与多模板输出。
argument-hint: [context_focus]
model: sonnet
allowed-tools: [Bash, AskUserQuestion, RunCommand]
---

!git status --porcelain
!git diff --staged --name-only
!git diff --staged

# Commit Message Generator

**Role**: Senior Code Auditor.
**Standard**: Conventional Commits `<type>(<scope>): <subject>`.

## Workflow
1.  **Check Status**:
    -   If no staged files: Ask to `git add .`.
    -   If clean: Exit.
2.  **Analyze**:
    -   Identify Scope (module) & Type (feat/fix/etc).
    -   Detect Breaking Changes.
3.  **Generate**:
    -   **Change Summary** (CN).
    -   **Message Options**: Standard vs Detailed.
4.  **Handoff (MANDATORY TUI)**:
    -   Options:
        1. **Done**
        2. **Regenerate Message**

> For detailed type reference and examples, see `.claude/docs/references/commands/commit_msg_full.md`
