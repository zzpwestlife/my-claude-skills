---
name: brainstorming
description: "You MUST use this before any creative work - creating features, building components, adding functionality, or modifying behavior. Explores user intent, requirements and design before implementation."
---

# Brainstorming Ideas Into Designs

## Overview

Help turn ideas into fully formed designs and specs through natural collaborative dialogue.

Start by understanding the current project context, then ask questions one at a time to refine the idea. Once you understand what you're building, present the design and get user approval.

<HARD-GATE>
Do NOT invoke any implementation skill, write any code, scaffold any project, or take any implementation action until you have presented a design and the user has approved it. This applies to EVERY project regardless of perceived simplicity.
</HARD-GATE>

## Anti-Pattern: "This Is Too Simple To Need A Design"

Every project goes through this process. A todo list, a single-function utility, a config change — all of them. "Simple" projects are where unexamined assumptions cause the most wasted work. The design can be short (a few sentences for truly simple projects), but you MUST present it and get approval.

## Checklist

You MUST create a task for each of these items and complete them in order:

1. **Explore project context** — check files, docs, recent commits
2. **Ask clarifying questions** — one at a time, understand purpose/constraints/success criteria
3. **Constitution Check** — Verify requirements against `constitution.md` (if exists)
4. **Propose 2-3 approaches** — with trade-offs and your recommendation
5. **Present design** — in sections scaled to their complexity, get user approval after each section
6. **Write design doc** — save to `docs/design/YYYY-MM-DD-<topic>.md` and commit
7. **Transition to implementation** — invoke writing-plans skill to create implementation plan

## Constitution Check (Zero-Friction)

**Before proposing approaches**, you MUST check if the project has a `constitution.md`. If so, verify the request against it:

- **Simplicity (Art. 1)**: Is this the simplest solution? Can we use stdlib?
- **Test-First (Art. 2)**: Does the design support TDD?
- **Security (Art. 11)**: Any input validation or data leakage risks?

If the request violates the Constitution, you MUST raise it immediately.

## Process Flow

```dot
digraph brainstorming {
    "Explore project context" [shape=box];
    "Ask clarifying questions" [shape=box];
    "Propose 2-3 approaches" [shape=box];
    "Present design sections" [shape=box];
    "User approves design? (AskUserQuestion)" [shape=diamond];
    "Write design doc" [shape=box];
    "Invoke writing-plans skill" [shape=doublecircle];

    "Explore project context" -> "Ask clarifying questions";
    "Ask clarifying questions" -> "Propose 2-3 approaches";
    "Propose 2-3 approaches" -> "Present design sections";
    "Present design sections" -> "User approves design? (AskUserQuestion)";
    "User approves design? (AskUserQuestion)" -> "Present design sections" [label="no, revise"];
    "User approves design? (AskUserQuestion)" -> "Write design doc" [label="yes"];
    "Write design doc" -> "Invoke writing-plans skill";
}
```

**The terminal state is invoking writing-plans.** Do NOT invoke frontend-design, mcp-builder, or any other implementation skill. The ONLY skill you invoke after brainstorming is writing-plans.

## The Process

**Understanding the idea (Grill-Me Protocol):**
- **Decision Tree Unpacking**: Do not treat the feature as a monolith. Break it down into a decision tree.
- **Relentless Questioning**: Walk down each branch of the design tree. Ask questions about edge cases, failure modes, data dependencies, and state management. Do not accept vague answers.
- **Autonomous Codebase Exploration**: Before asking the user "how is X implemented currently?", the AI **MUST** check out the current project state first to find the answer itself. Only ask the user when the codebase does not provide the answer or a product decision is needed.
- **Goal**: Reach a state of **Shared Understanding** where no branch is left unresolved.

**Exploring approaches:**
- Propose 2-3 different approaches with trade-offs
- Present options conversationally with your recommendation and reasoning
- Lead with your recommended option and explain why
- **MANDATORY TUI HANDOFF:**
  - You MUST use `AskUserQuestion` with `options` for the user to select the preferred approach.
  - NEVER ask "Do you agree?" or "Which one do you prefer?" in text.
  - NEVER wait for free-text input. Force a selection.

**Presenting the design:**
- Once you believe you understand what you're building, present the design
- Scale each section to its complexity: a few sentences if straightforward, up to 200-300 words if nuanced
- Ask after each section whether it looks right so far
- **MANDATORY TUI HANDOFF:**
  - You MUST use `AskUserQuestion` with `options` (e.g., "Approve Design", "Revise Design").
  - NEVER ask "Does this look good?" in text.

- Cover: architecture, components, data flow, error handling, testing
- Be ready to go back and clarify if something doesn't make sense

## After the Design

**Documentation:**
- Write the validated design to `docs/plans/YYYY-MM-DD-<topic>-design.md`
- Use elements-of-style:writing-clearly-and-concisely skill if available
- Commit the design document to git

**Implementation:**
- Invoke the writing-plans skill to create a detailed implementation plan
- Do NOT invoke any other skill. writing-plans is the next step.

## Key Principles

- **One question at a time** - Don't overwhelm with multiple questions
- **Multiple choice preferred** - Easier to answer than open-ended when possible
- **YAGNI ruthlessly** - Remove unnecessary features from all designs
- **Explore alternatives** - Always propose 2-3 approaches before settling
- **Incremental validation** - Present design, get approval before moving on
- **Be flexible** - Go back and clarify when something doesn't make sense
