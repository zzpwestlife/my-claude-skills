---
name: executing-plans
description: |
  Invoke when there is an approved plan document and we must execute it step-by-step.
  Required outputs: task tracking + chunk diffs + Evidence Blocks for success claims.
  If no plan exists (or plan lacks verification commands): STOP and route to writing-plans / verification-before-completion.
version: "2.0.0"
---

# Executing Plans

Load plan, execute tasks, review, finish branch. Supports sequential or subagent-parallel modes.

## Reusable Interface (R) — Execution Transcript Contract

This skill must produce artifacts that other skills (and humans) can audit and reuse.

### Mandatory outputs

1) **Task tracking**
- Maintain a task list (TodoWrite) with `pending / in_progress / completed`.

2) **Step evidence** (delegated to `verification-before-completion`)
- Every completion/success claim MUST include an Evidence Block:
  - Claim / Command / Exit code / Evidence

3) **Chunk boundaries**
- After each chunk of work: show a concise change summary (`git diff --stat` or equivalent).

4) **Finish options**
- Present the 4 finish options (merge / PR / keep / discard).
- Discard requires typed confirmation.

## Anti-Anchoring (MANDATORY)

- A plan is a constraint, not a template to blindly copy.
- Any example commands/outputs are formatting demos only; reality (repo state, CI, toolchain) always wins.
- If the plan lacks verification commands, STOP and route to `verification-before-completion` to define the verification gate before executing.

## Mode Selection

| Condition | Mode |
|-----------|------|
| Tasks independent + subagents available | **Subagent mode** (fresh agent per task) |
| Tasks tightly coupled OR no subagents | **Sequential mode** (execute in current session) |

## The Process

### Step 1: Load and Review Plan

0. Triage (mis-trigger downgrade path):
   - If there is no plan document to follow: STOP and route to `writing-plans` (or ask the user to provide the plan path).
   - If the user only wants a review of code changes (no execution): STOP and route to `code-review`.
   - If this is not a git repository but the plan requires `git diff` / branching operations: STOP and ask the user to run inside a git repo or provide an explicit patch/diff to work from.
   - If the plan is missing verification steps/commands (tests, lint, build) required for completion claims: STOP and ask to amend the plan (or route to `verification-before-completion` to define the verification gate).

1. Read plan file.
2. Review critically — raise concerns before starting.
3. Create task list and proceed.

### Step 2: Execute Tasks

#### Sequential Mode

For each task:
1. Mark as `in_progress`.
2. Follow each step exactly.
3. Run verifications as specified.
4. Mark as `completed`.
5. After each chunk: run `git diff`, present TUI options (Continue / Review / Pause).

#### Subagent Mode

For each task:
1. Dispatch implementer subagent with full task text + context (see `assets/prompts/implementer-prompt.md`).
2. If implementer asks questions — answer before proceeding.
3. Dispatch spec reviewer (`assets/prompts/spec-reviewer-prompt.md`) — must pass before quality review.
4. Dispatch code quality reviewer (`assets/prompts/code-quality-reviewer-prompt.md`).
5. If issues found: implementer fixes → re-review until approved.
6. Mark task complete.

**Implementer statuses:** DONE (proceed), DONE_WITH_CONCERNS (assess), NEEDS_CONTEXT (provide & re-dispatch), BLOCKED (escalate).

**Model selection:** Cheap model for 1-2 file mechanical tasks, standard for integration, capable for architecture/review.

### Step 3: Finish Branch

After all tasks complete:

1. **Verify tests pass** (`npm test` / `go test ./...` / `pytest`). Stop if failing.
2. **Determine base branch** (`git merge-base HEAD main`).
3. **Present 4 options:**
   - Merge back to base branch locally
   - Push and create a Pull Request
   - Keep the branch as-is
   - Discard this work (requires typed "discard" confirmation)
4. **Clean up worktree** for merge/discard options; keep for PR/as-is.

## When to Stop

- Hit a blocker (missing dependency, test fails, instruction unclear).
- Plan has critical gaps.
- Verification fails repeatedly.

**Ask for clarification rather than guessing.**

## Red Flags

**Never:**
- Start on main/master without explicit consent.
- Skip reviews (spec compliance OR code quality).
- Dispatch parallel implementation subagents (conflicts).
- Proceed with unfixed issues.
- Force-push without explicit request.

**Always:**
- Follow plan steps exactly.
- Verify tests before offering finish options.
- Get typed confirmation for discard.
