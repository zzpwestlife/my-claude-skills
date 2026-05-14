---
name: brainstorming
description: |
  Invoke when the user wants to create/modify behavior and the requirements/approach are not yet decided.
  Hard gate: if it’s pure explanation or a small localized edit, STOP and downgrade (no full design loop).
  Output: research note + decision log + spec, with AskUserQuestion gates before implementation.
version: "1.0.0"
---

# Brainstorming Ideas Into Designs

Help turn ideas into fully formed designs and specs through natural collaborative dialogue.

Start by understanding the current project context, then ask questions one at a time to refine the idea. Once you understand what you're building, present the design and get user approval.

<HARD-GATE>
Do NOT invoke any implementation skill, write any code, scaffold any project, or take any implementation action until you have presented a design and the user has approved it. This applies to EVERY project regardless of perceived simplicity.
Exception: If the Triage step determines brainstorming is not the right tool for this request, STOP and handle the request directly or route to the appropriate skill.
</HARD-GATE>

## Anti-Pattern: "This Is Too Simple To Need A Design"

Every project goes through this process. A todo list, a single-function utility, a config change — all of them. "Simple" projects are where unexamined assumptions cause the most wasted work. The design can be short (a few sentences for truly simple projects), but you MUST present it and get approval.

## Reusable Interface (R) — Brainstorming Deliverables Contract

This skill must produce *reusable artifacts* that downstream workflows can consume (e.g. `writing-plans`).

**Minimum deliverables:**
1) `docs/research/YYYY-MM-DD-<topic>.md` — current state / constraints / risks / 2-3 approaches
2) `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md` — the approved spec
3) **Decision Log** (in the spec or a small section in the research doc):
   - Decision
   - Options considered (2-3)
   - Why chosen

## Anti-Anchoring（反锚定，MANDATORY）

- Do not “over-question” to look thorough: focus on the 2–3 decisions that change scope/architecture/verification.
- Do not design the whole universe: converge to an MVP spec first, then iterate.
- Diagrams/templates are structure demos, not rituals. The goal is decisions + artifacts.

## Process & Checklist

You MUST create a task for each of these items and complete them in order:

0. **Triage (mis-trigger downgrade path)** — First, confirm this request actually needs brainstorming.
   - If the user is asking for factual info / explanation only: **STOP** and answer directly (do not run the design loop).
   - If the user only needs a small, localized edit (typo/formatting/minor config): **STOP** and propose the minimal change without a full design cycle.
   - If the user wants implementation but the requirements are already clear and approved: consider skipping to `writing-plans` instead.
   - If you cannot tell which bucket this is: ask **ONE** clarifying question, then decide whether to proceed or downgrade.

1. **Explore project context & Research** — Check files, docs, context. **MANDATORY**: Create `docs/research/YYYY-MM-DD-<topic>.md` analyzing existing patterns, dependencies, and constraints. Ensure you understand the "intricacies" before designing.
2. **Offer visual companion** (if topic will involve visual questions) — this is its own message, not combined with a clarifying question. See the Visual Companion section below.
3. **The "Grill-Me" Interview (Stress-Test & Deep Dive)**:
   - Break the user's plan/idea into a **decision tree**. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one.
   - **Relentless Questioning**: Interview the user relentlessly about every aspect of this plan until reaching a shared understanding. Do NOT accept vague answers.
   - **Autonomous Exploration**: If a question can be answered by exploring the codebase, **explore the codebase instead** (use `SearchCodebase`/`Grep`) rather than asking the user.
   - Focus on: **Edge Cases**, **Dependencies**, **Failure Modes**, and **Success Criteria**.
   - **Devil's Advocate (魔鬼代言人)**: Explicitly challenge the user's core idea. Find every wrong assumption, every ignored risk, and every reason it might fail. Do NOT hold back.
   - **LOOP**: Do NOT proceed until you are confident every branch has been resolved without guessing.
4. **Constitution Check**: Verify against `constitution.md` (Simplicity, Security).
5. **Pre-mortem (前期验尸)**: Before proposing approaches, run a pre-mortem: "Assume this feature fails completely in 6 months. Here are the 3 most likely specific reasons why." Ensure the design mitigates these.
6. **Propose 2-3 approaches** — with trade-offs and your recommendation. **MANDATORY TUI**: Use `AskUserQuestion` to select approach.
7. **Present design** — in sections scaled to their complexity, get user approval after each section. **MANDATORY TUI**: Use `AskUserQuestion` to approve/revise.
8. **Write design doc** — save to `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md` and commit.
9. **Spec self-review** — quick inline check for placeholders, contradictions, ambiguity, scope (see below).
10. **User reviews written spec** — execute `git diff HEAD~1` to show changes, then use `AskUserQuestion` to ask user to review the spec file before proceeding.
11. **Transition to implementation** — invoke writing-plans skill to create implementation plan.

## Examples (Anchors)

**Should downgrade (no full design loop):**
- "Fix a typo / formatting / minor config tweak"
- "Explain how X works" (informational)

**Should use brainstorming (design loop):**
- "Add a new feature that changes app behavior"
- "Introduce a new CI/build workflow where trade-offs and verification gates matter"

## Process Flow

```dot
digraph brainstorming {
    "Explore project context" [shape=box];
    "Visual questions ahead?" [shape=diamond];
    "Offer Visual Companion\n(own message, no other content)" [shape=box];
    "Grill-Me Interview" [shape=box];
    "Constitution Check" [shape=box];
    "Pre-mortem" [shape=box];
    "Propose 2-3 approaches" [shape=box];
    "Present design sections" [shape=box];
    "User approves design?" [shape=diamond];
    "Write design doc" [shape=box];
    "Spec self-review\n(fix inline)" [shape=box];
    "User reviews spec?" [shape=diamond];
    "Invoke writing-plans skill" [shape=doublecircle];

    "Explore project context" -> "Visual questions ahead?";
    "Visual questions ahead?" -> "Offer Visual Companion\n(own message, no other content)" [label="yes"];
    "Visual questions ahead?" -> "Grill-Me Interview" [label="no"];
    "Offer Visual Companion\n(own message, no other content)" -> "Grill-Me Interview";
    "Grill-Me Interview" -> "Constitution Check";
    "Constitution Check" -> "Pre-mortem";
    "Pre-mortem" -> "Propose 2-3 approaches";
    "Propose 2-3 approaches" -> "Present design sections";
    "Present design sections" -> "User approves design?";
    "User approves design?" -> "Present design sections" [label="no, revise"];
    "User approves design?" -> "Write design doc" [label="yes"];
    "Write design doc" -> "Spec self-review\n(fix inline)";
    "Spec self-review\n(fix inline)" -> "User reviews spec?";
    "User reviews spec?" -> "Write design doc" [label="changes requested"];
    "User reviews spec?" -> "Invoke writing-plans skill" [label="approved"];
}
```

**The terminal state is invoking writing-plans.** Do NOT invoke frontend-design, mcp-builder, or any other implementation skill. The ONLY skill you invoke after brainstorming is writing-plans.

## The Process Details

**Understanding the idea:**

- Check out the current project state first (files, docs, recent commits)
- Before asking detailed questions, assess scope: if the request describes multiple independent subsystems (e.g., "build a platform with chat, file storage, billing, and analytics"), flag this immediately. Don't spend questions refining details of a project that needs to be decomposed first.
- If the project is too large for a single spec, help the user decompose into sub-projects: what are the independent pieces, how do they relate, what order should they be built? Then brainstorm the first sub-project through the normal design flow. Each sub-project gets its own spec → plan → implementation cycle.
- For appropriately-scoped projects, ask questions one at a time to refine the idea
- Prefer multiple choice questions when possible, but open-ended is fine too
- Only one question per message - if a topic needs more exploration, break it into multiple questions
- Focus on understanding: purpose, constraints, success criteria

**Exploring approaches:**

- Propose 2-3 different approaches with trade-offs
- Present options conversationally with your recommendation and reasoning
- Lead with your recommended option and explain why

**Presenting the design:**

- Once you believe you understand what you're building, present the design
- Scale each section to its complexity: a few sentences if straightforward, up to 200-300 words if nuanced
- Ask after each section whether it looks right so far
- Cover: architecture, components, data flow, error handling, testing
- Be ready to go back and clarify if something doesn't make sense

**Design for isolation and clarity:**

- Break the system into smaller units that each have one clear purpose, communicate through well-defined interfaces, and can be understood and tested independently
- For each unit, you should be able to answer: what does it do, how do you use it, and what does it depend on?
- Can someone understand what a unit does without reading its internals? Can you change the internals without breaking consumers? If not, the boundaries need work.
- Smaller, well-bounded units are also easier for you to work with - you reason better about code you can hold in context at once, and your edits are more reliable when files are focused. When a file grows large, that's often a signal that it's doing too much.

**Working in existing codebases:**

- Explore the current structure before proposing changes. Follow existing patterns.
- Where existing code has problems that affect the work (e.g., a file that's grown too large, unclear boundaries, tangled responsibilities), include targeted improvements as part of the design - the way a good developer improves code they're working in.
- Don't propose unrelated refactoring. Stay focused on what serves the current goal.

## After the Design

**Documentation:**

- Write the validated design (spec) to `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`
  - (User preferences for spec location override this default)
- Use elements-of-style:writing-clearly-and-concisely skill if available
- Commit the design document to git

**Spec Self-Review:**
After writing the spec document, look at it with fresh eyes:

1. **Placeholder scan:** Any "TBD", "TODO", incomplete sections, or vague requirements? Fix them.
2. **Internal consistency:** Do any sections contradict each other? Does the architecture match the feature descriptions?
3. **Scope check:** Is this focused enough for a single implementation plan, or does it need decomposition?
4. **Ambiguity check:** Could any requirement be interpreted two different ways? If so, pick one and make it explicit.

Fix any issues inline. No need to re-review — just fix and move on.

**User Review Gate:**
After the spec review loop passes, you **MUST** execute `git diff HEAD~1` to show the spec changes. Then, use the `AskUserQuestion` tool to ask the user to review the written spec before proceeding:

> "Spec written and committed to `<path>`. Please review it and let me know if you want to make any changes before we start writing out the implementation plan."

Wait for the user's response via the tool. If they request changes, make them and re-run the spec review loop. Only proceed once the user approves.

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

## Visual Companion

A browser-based companion for showing mockups, diagrams, and visual options during brainstorming. Available as a tool — not a mode. Accepting the companion means it's available for questions that benefit from visual treatment; it does NOT mean every question goes through the browser.

**Offering the companion:** When you anticipate that upcoming questions will involve visual content (mockups, layouts, diagrams), offer it once for consent:
> "Some of what we're working on might be easier to explain if I can show it to you in a web browser. I can put together mockups, diagrams, comparisons, and other visuals as we go. This feature is still new and can be token-intensive. Want to try it? (Requires opening a local URL)"

**This offer MUST be its own message.** Do not combine it with clarifying questions, context summaries, or any other content. The message should contain ONLY the offer above and nothing else. Wait for the user's response before continuing. If they decline, proceed with text-only brainstorming.

**Per-question decision:** Even after the user accepts, decide FOR EACH QUESTION whether to use the browser or the terminal. The test: **would the user understand this better by seeing it than reading it?**

- **Use the browser** for content that IS visual — mockups, wireframes, layout comparisons, architecture diagrams, side-by-side visual designs
- **Use the terminal** for content that is text — requirements questions, conceptual choices, tradeoff lists, A/B/C/D text options, scope decisions

A question about a UI topic is not automatically a visual question. "What does personality mean in this context?" is a conceptual question — use the terminal. "Which wizard layout works better?" is a visual question — use the browser.

If they agree to the companion, read the detailed guide before proceeding:
`skills/brainstorming/visual-companion.md`
