---
name: writing-plans
description: |
  Invoke when there is an approved spec/requirements and we need a step-by-step implementation plan before touching code.
  Hard gate: no spec → STOP and route to brainstorming; execution request → route to executing-plans.
  Output: a plan file with minimal verification commands (test/lint/build) for each increment.
version: "1.0.0"
---

# Writing Plans

## Overview

Prefer **Detailed MVP plans** over “Comprehensive coverage”. Capture the shortest path to a verifiable increment, then iterate.

Assume they are a skilled developer, but know almost nothing about our toolset or problem domain. Assume they don't know good test design very well.

**Announce at start:** "I'm using the writing-plans skill to create the implementation plan."

**Context:** This should be run in a dedicated worktree (created by brainstorming skill).

## Reusable Interface (R) — Plan Contract

This skill must output a plan that other workflows can reuse (e.g. `executing-plans`, CI/Makefile flows).

### Required outputs
1) Plan file: `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md`
2) Verification gate: each task/increment must include at least one runnable verification command (test/lint/build).
   - If the repo/toolchain is unknown: explicitly state the limitation and ask for the exact command (do not invent one).

## Anti-Anchoring（反锚定，MANDATORY）

- 示例代码/命令是结构演示，不是模板；必须以仓库真实语言/真实测试框架为准。
- 禁止为“显得全面”而罗列大量边界：只写会改变计划结构/验证门的关键边界。
- spec 信息不足时：STOP 并 AskUserQuestion，而不是用假设填满计划。

## Structure & Creation
1. **Analyze & Create (AUTO-START)**:
   - Read the design document.
   - If there is no approved spec/design doc available: **STOP** and route to `brainstorming` (or ask the user to provide the spec path).
   - If the user is asking to execute an existing plan rather than write one: **STOP** and route to `executing-plans`.
   - **IMMEDIATELY** generate the plan file `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md`.
   - **AND** generate the State Tracking File `docs/superpowers/plans/YYYY-MM-DD-<feature-name>-state.local.md` (Refer to `.claude/docs/guides/agent_bdd_loop.md` for format).
   - **Do NOT wait** or ask for confirmation to write the plan (loading this skill IS confirmation).
   - Only use `AskUserQuestion` if the design is critically missing or unintelligible.

**Save plans to:** `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md`
- (User preferences for plan location override this default)

## Scope Check

If the spec covers multiple independent subsystems, it should have been broken into sub-project specs during brainstorming.

- If it wasn't: **STOP** and propose a decomposition (one plan per subsystem) and use `AskUserQuestion` to get user confirmation on the split **before** writing the plan.
- Each plan should produce working, testable software on its own.

## File Structure

Before defining tasks, map out which files will be created or modified and what each one is responsible for. This is where decomposition decisions get locked in.

- Design units with clear boundaries and well-defined interfaces. Each file should have one clear responsibility.
- You reason best about code you can hold in context at once, and your edits are more reliable when files are focused. Prefer smaller, focused files over large ones that do too much.
- Files that change together should live together. Split by responsibility, not by technical layer.
- In existing codebases, follow established patterns. If the codebase uses large files, don't unilaterally restructure - but if a file you're modifying has grown unwieldy, including a split in the plan is reasonable.

This structure informs the task decomposition. Each task should produce self-contained changes that make sense independently.

## Bite-Sized Task Granularity

**Each step is one action (2-5 minutes):**
- "Write the failing test" - step
- "Run it to make sure it fails" - step
- "Implement the minimal code to make the test pass" - step
- "Run the tests and make sure they pass" - step
- "Commit" - step

## Plan Document Header

**Every plan MUST start with this header:**

```markdown
# [Feature Name] Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

**Assumption Audit (假设审计):** [What assumptions did I make? If they are wrong, how does it change this plan?]

---
```

## Task Structure

````markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

- [ ] **Step 1: Write the failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

- [ ] **Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

## No Placeholders

Every step must contain the actual content an engineer needs. These are **plan failures** — never write them:
- "TBD", "TODO", "implement later", "fill in details"
- "Add appropriate error handling" / "add validation" / "handle edge cases"
- "Write tests for the above" (without actual test code)
- "Similar to Task N" (repeat the code — the engineer may be reading tasks out of order)
- Steps that describe what to do without showing how (code blocks required for code steps)
- References to types, functions, or methods not defined in any task
- **Do not invent toolchain commands** (`pytest` / `npm test` / `go test`) unless the repo/spec explicitly indicates them. If unknown, ask for the exact verification command.

## Remember
- Exact file paths always
- Complete code in every step — if a step changes code, show the code
- Exact commands with expected output
- DRY, YAGNI, TDD, frequent commits

## Self-Review

After writing the complete plan, look at the spec with fresh eyes and check the plan against it. This is a checklist you run yourself — not a subagent dispatch.

**1. Spec coverage:** Skim each section/requirement in the spec. Can you point to a task that implements it? List any gaps.

**2. Placeholder scan:** Search your plan for red flags — any of the patterns from the "No Placeholders" section above. Fix them.

**3. Type consistency:** Do the types, method signatures, and property names you used in later tasks match what you defined in earlier tasks? A function called `clearLayers()` in Task 3 but `clearFullLayers()` in Task 7 is a bug.

If you find issues, fix them inline. No need to re-review — just fix and move on. If you find a spec requirement with no task, add the task.

## Execution Handoff (MANDATORY TUI & GIT DIFF)

After saving the plan, you **MUST** do the following to ensure the zero-friction goal:
1. **Execute `git diff HEAD~1`** to show the generated plan to the user.
2. **Execute the `AskUserQuestion` tool** to offer the execution choice. You are **FORBIDDEN** from just printing text and waiting.

**Set the `question` parameter to:**
"Plan complete and saved to `docs/superpowers/plans/<filename>.md`. Which execution approach?"

**Set the `options` parameter to:**
1. `label`: "Subagent-Driven", `description`: "Fresh subagent per task, review between tasks, fast iteration (Use superpowers:subagent-driven-development)"
2. `label`: "Inline Execution", `description`: "Execute tasks in this session using executing-plans, batch execution with checkpoints (Use superpowers:executing-plans)"

**If Subagent-Driven chosen:**
- **REQUIRED SUB-SKILL:** Use superpowers:subagent-driven-development
- Fresh subagent per task + two-stage review

**If Inline Execution chosen:**
- **REQUIRED SUB-SKILL:** Use superpowers:executing-plans
- Batch execution with checkpoints for review

## Rules
- **TUI First**: NEVER start execution without explicit user approval via `AskUserQuestion`.
