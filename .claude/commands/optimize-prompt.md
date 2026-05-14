---
description: 交互式优化 Prompt，遵循 Anthropic Claude 4.5/4.6 最佳实践。使用XML结构、思维链(CoT)、示例驱动，输出高质量System Prompt。
argument-hint: <prompt_text|file_path> [output_dir]
model: sonnet
allowed-tools: [AskUserQuestion, Skill, Read, Write, Grep, Bash, Glob]
---

# Prompt Optimization Command

**Goal**: Transform raw requirements into production-grade System Prompts for Claude 4.5/4.6.

## Core Principles

| Principle | How |
|-----------|-----|
| **Structure (XML)** | Use `<task>`, `<rules>`, `<examples>` tags for clarity |
| **Clarity** | Explicit role, goal, constraints; no ambiguity |
| **Chain of Thought (CoT)** | Force reasoning via `<thinking>` tags for complex tasks |
| **Few-Shot** | 1-2 concrete input/output examples define boundaries better than 100 words |

## 4-Stage Workflow

### 1️⃣ Analysis
- Parse arguments; detect language (CN/EN)
- Identify missing: Role, Goal, Examples, Constraints, Input/Output Format
- Create/confirm `output_dir`

### 2️⃣ Socratic Interview
Ask targeted questions to fill gaps—especially **Examples** (most critical).
Use `AskUserQuestion` with preset options for fast TUI navigation.

### 3️⃣ Generation
Generate optimized prompt using principles above.
Output as Markdown code block; **save to** `{output_dir}/prompt.md`.

### 4️⃣ Handoff
Present TUI menu:
- **Proceed to Planning** → `/write-plan {output_dir}`
- **Revise & Iterate** → Collect feedback, loop to Stage 2

## Example: Before/After

**Before** (vague):
```
You are a helpful coding assistant. Help the user write code.
```

**After** (optimized):
```markdown
<task>
You are an expert Python code reviewer. Your job is to identify bugs, 
security issues, and performance bottlenecks in user-submitted code.
</task>

<rules>
- Always explain issues in plain English, then show the fix
- Flag security risks (SQL injection, XSS, etc.) with severity
- Suggest 1-2 optimization ideas per review
</rules>

<examples>
**Bad code**: `user_id = request.args.get('id')` (SQL injection risk)
**Your response**: "⚠️ SECURITY: Direct query parameter usage. Use parameterized queries..."
</examples>
```

---

**📖 Full interview strategies & edge cases**: `.claude/docs/references/commands/optimize_prompt_full.md`
