# Agent BDD Loop (Red-Green Agent Workflow)

This guide outlines the advanced workflow for AI agents handling complex or multi-step tasks within this project. It is inspired by the Superpowers + Ralph-Loop architecture, utilizing Behavior-Driven Development (BDD), strict state tracking, and specialized "Red" and "Green" agent roles.

## 1. The Core Philosophy
When dealing with complex implementations, a single AI session or "happy path" approach is prone to context loss and "lazy" assumptions. To enforce **ZERO laziness** and ensure **Simplicity & Elegance**, we adopt a continuous, state-driven, dual-agent verification loop.

- **BDD First**: Instead of jumping straight to code or unit tests, define the feature's behavior (Given-When-Then) first.
- **State-Driven**: Every complex task MUST be broken down into a `.local.md` state file. No task proceeds if its dependencies (`blocked by`) are not met.
- **Red-Green Agents**: Separation of concerns. The "Red Agent" writes the failing tests based on the BDD spec. The "Green Agent" writes the implementation to pass the tests.

## 2. Prerequisites & Setup

To execute this loop efficiently, the AI relies on the `superpowers` plugin with the `ralph-loop` feature.

### Installation
Run the following commands in your terminal to install the necessary tools:
```bash
# 1. Add the author's plugin marketplace
claude plugin marketplace add FradSer/dotclaude

# 2. Install the superpowers plugin
claude plugin install superpowers@frad-dotclaude
```
*Note: After installation, restart Claude Code or refresh your session. When executing a plan, the Superpower loop will automatically activate and generate `.local.md` tracking files.*

## 3. The Workflow Steps

### Step 1: BDD Specification & Planning
Before any code is written, the Agent must:
1. Research the codebase and requirements (as per `docs/research/`).
2. Draft a Plan in `docs/plans/` that includes **BDD Scenarios**.
3. Generate a State Tracking File.

### Step 2: The State Tracking File (`.local.md`)
For any multi-step task, create a tracking file (e.g., `docs/plans/task-name-state.local.md`). 
It must explicitly track:
- **Task ID & Description**
- **Status**: Pending / In Progress / Completed / Blocked
- **Dependencies**: Which task ID blocks the current one.

*Example:*
```markdown
# State: Implement Domain Models

- [x] #1 BDD Scenarios Designed
- [ ] #2 [Red] Write Failing Tests for Domain Models (Blocked by: None)
- [ ] #3 [Green] Implement Domain Models (Blocked by: #2)
- [ ] #4 [Red] Write Failing Tests for Repository (Blocked by: #3)
- [ ] #5 [Green] Implement Repository (Blocked by: #4)
```

### Step 3: Red Agent (Test Generation)
The Agent assumes the "Red" role. 
- It reads the BDD spec and the State Tracking File.
- It writes comprehensive, failing tests.
- It runs the tests to verify they **fail** (proving the tests are valid and not false-positives).
- It marks the Red task as `Completed` in the State Tracking File.

### Step 4: Green Agent (Implementation)
The Agent assumes the "Green" role.
- It reads the failing tests and implements the minimal required code to pass them.
- It runs the tests to verify they **pass**.
- It marks the Green task as `Completed`.

### Step 5: Refactor & Loop
- Once Green, refactor for clean code standards (File < 200 lines, 3-line metadata headers, etc.).
- Move to the next unblocked task in the State Tracking File.

## 4. Automation Loops & Superset Integration
For long-running tasks, this state file serves as the Single Source of Truth for external orchestration tools like **Superset** or **Conductor**. 
- Multiple agents can read the `.local.md` file in parallel across different git worktrees.
- If a background loop detects failing tests, it can automatically spawn a "Green Agent" task to fix it.

By adhering to this loop, the AI ensures test-driven, verified, and non-blocking progress on complex features.
