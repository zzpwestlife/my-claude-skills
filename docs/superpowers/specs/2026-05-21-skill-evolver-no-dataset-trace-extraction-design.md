# Design: skill-evolver — Degraded Mode & Trace Extraction

Date: 2026-05-21
Status: Approved

## Summary

Two independent additions to `skill-evolver/SKILL.md`:

1. **Degraded Mode** — when no dataset is provided, run L1 static check + 4-dim Rubric, output score card + suggestions, then stop. No iteration loop.
2. **Trace Extraction** — when user pastes a conversation excerpt, parse it into a `dev.jsonl`-compatible trace draft, show for review, then save on confirmation.

Neither feature affects the existing Phase 0 → iteration loop path.

---

## Feature 1: Degraded Mode (No Dataset)

### Trigger

Phase 0 setup finds a valid `SKILL.md` but no dataset directory, or the user explicitly requests evaluation without a dataset.

### Steps

1. **L1 static check** (existing rules, minus GT smoke sample which requires dataset)
   - Frontmatter present: `name`, `description` fields non-empty.
   - Required sections present (at minimum: one workflow or instruction section).
   - Safety scan: run all 11 rules. Critical (★) findings block; 9 warnings recorded.

2. **Built-in Rubric** (4 dimensions, each LLM YES/NO)

   | ID | Dimension | Question asked to LLM |
   |----|-----------|----------------------|
   | D1 | Trigger precision | "Can a reader determine in 5 seconds whether to invoke this skill for a given request, without confusing it with similar skills?" |
   | D2 | Boundary clarity | "Does the skill explicitly state at least one scenario it does NOT handle?" |
   | D3 | Workflow coverage | "Does the workflow/instructions section address all major input types mentioned in the description or trigger?" |
   | D4 | Example quality | "If examples are present, do they include at least one positive (invoke) and one negative (do not invoke) case? If no examples, answer NO." |

   Each dimension: YES = pass, NO = fail. Score = `passed / 4`.

3. **Output: Score Card**

   ```
   === Degraded Mode Evaluation ===
   Skill: <name>
   Mode: No dataset — L1 + Rubric only

   L1 Static Check
     structure:  PASS
     safety:     2 warnings (see below)

   Rubric (4/4)
     D1 trigger precision:  YES
     D2 boundary clarity:   NO  ← suggested fix below
     D3 workflow coverage:  YES
     D4 example quality:    NO  ← suggested fix below

   Score: 2/4 rubric dims passed

   Suggestions:
     D2: Add a "Do not use when..." line to the description frontmatter.
     D4: Add at least one negative example showing when NOT to invoke.

   Safety warnings:
     W3: description uses vague trigger ("use when helpful") — tighten to specific conditions
   ```

4. **STOP** — do not enter Modify/Commit/Verify loop. Surface suggestions and hand off to operator.

### Operator Checkpoint

One checkpoint after score card is written. Operator may:
- Accept suggestions and manually edit SKILL.md, then re-run degraded mode.
- Provide a dataset to unlock full evolution mode.
- Exit.

---

## Feature 2: Trace Extraction

### Trigger

User says they want to build a dataset from a conversation, or pastes conversation text and asks to extract a trace.

### Steps

1. **Identify invocation boundary**
   - Locate the user message that triggered the skill (input).
   - Locate the assistant's final response after skill execution (output).
   - If multiple skill invocations are present in the paste, process one at a time.

2. **Extract fields**

   | Field | Source |
   |-------|--------|
   | `id` | Auto-generated: `extracted-<timestamp>-<n>` |
   | `input` | User message text that triggered the skill |
   | `expected_output` | Full assistant response (or user-highlighted portion) |
   | `skill` | Skill name if identifiable from the conversation; else ask |
   | `split` | Default `dev`; user may override to `gt`, `holdout`, or `regression` |
   | `notes` | Optional: user annotation about why this is a good/bad example |

3. **Show draft**

   ```
   === Extracted Trace Draft ===
   id: extracted-20260521-001
   skill: skill-evolver
   split: dev
   input: |
     <extracted user message>
   expected_output: |
     <extracted assistant response>
   notes: (empty)

   Save to <dataset-dir>/traces/dev-extracted-001.json and append to dev.jsonl? [y/n/edit]
   ```

4. **Confirm → save** — write trace file and append index line to `dev.jsonl`.
   If user edits, apply edits then save. If user declines, discard.

### Output Format

Trace file (`traces/dev-extracted-<n>.json`):

```json
{
  "id": "extracted-20260521-001",
  "skill": "skill-evolver",
  "split": "dev",
  "input": "...",
  "expected_output": "...",
  "notes": ""
}
```

`dev.jsonl` index line:

```jsonl
{"id": "extracted-20260521-001", "trace_path": "traces/dev-extracted-001.json", "split": "dev"}
```

### Constraints

- Extraction is best-effort — operator must review the draft before saving.
- GT traces require manual confirmation that the extracted output is the "correct" answer; auto-extracted traces default to `dev` split, not `gt`.
- No automatic log scanning. Input must be pasted by the user.

---

## Changes to SKILL.md

Two new top-level sections added after "Self-Contained Bundle Checks" and before "Iteration Loop":

- `## Degraded Mode (No Dataset)` — the full flow above.
- `## Trace Extraction` — the full flow above.

The existing `## Inputs` section's "Required" list is softened:

> Dataset directory is required for full evolution mode. If no dataset is provided, the skill enters Degraded Mode (see below) and performs static evaluation only.

The `description` frontmatter trigger is updated to route both new entry points:

> Use when: evolving a skill with a dataset (full mode); evaluating a skill without a dataset (degraded mode); extracting conversation traces into a dataset (trace extraction mode).

---

## Out of Scope

- Automatic log scanning (no accessible log format with message content).
- Rubric-gated iteration loop in degraded mode (no GT = no verification of improvement).
- Integration with darwin-skill's Rubric (separate dependency, different dimensions).
