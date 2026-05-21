# skill-evolver: Degraded Mode & Trace Extraction — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add two independent entry modes to `skill-evolver/SKILL.md` — a no-dataset static evaluation mode (Degraded Mode) and a conversation-paste trace extraction helper — without touching any existing flow.

**Architecture:** Pure SKILL.md edits only. No new scripts, no new files, no external dependencies. The two new sections slot in after `## Self-Contained Bundle Checks` and before `## Iteration Loop`. Three smaller edits (frontmatter, intro paragraph, Inputs section) update routing so the new modes are reachable.

**Tech Stack:** Markdown only. Verification via `python3 scripts/check_skill_package.py . --json` (already in Makefile).

**Assumption Audit:** Assumes SKILL.md's `check_skill_package.py` validates section structure non-destructively and that adding new `##` sections does not break the package check. If `check_skill_package.py` enforces a fixed section list, Task 1 verification will fail and the script must be inspected before proceeding.

---

### Task 1: Update frontmatter description and intro routing

**Files:**
- Modify: `skill-evolver/SKILL.md` (lines 3, 12)

- [ ] **Step 1: Edit frontmatter `description` field (line 3)**

Replace:
```
description: Use when evolving or evaluating a local skill with GT/dev/holdout/regression data. Do not use when the user only wants dataset validation, package smoke checks, or a one-off review with no iteration loop. Example: improve a skill against dev and holdout splits; self-iterate a skill with trace-driven rollback.
```

With:
```
description: Use when evolving a skill with a dataset (full mode); evaluating a skill without a dataset (degraded mode, L1 + Rubric only); or extracting conversation traces into a dataset (trace extraction mode). Do not use when the user only wants dataset validation, package smoke checks, or a one-off review with no iteration loop.
```

- [ ] **Step 2: Edit intro routing paragraph (line 12) — append degraded-mode and trace-extraction routing**

The current line 12 ends with: `...but do not enter Modify/Commit/Verify.`

Append after that sentence (same paragraph or new sentence):
```
If the user provides a skill directory but no dataset, or explicitly requests evaluation without data, enter Degraded Mode (see below). If the user pastes a conversation excerpt and asks to extract a trace, enter Trace Extraction (see below).
```

- [ ] **Step 3: Verify package check still passes**

Run from `skill-evolver/`:
```bash
python3 scripts/check_skill_package.py . --json
```
Expected output:
```json
{"checked_files": 18, "errors": [], "ok": true}
```

- [ ] **Step 4: Commit**

```bash
git add skill-evolver/SKILL.md
git commit -m "feat(skill-evolver): update frontmatter + intro routing for degraded/trace modes"
```

---

### Task 2: Soften the `## Inputs` Required list

**Files:**
- Modify: `skill-evolver/SKILL.md` (lines 16–20)

- [ ] **Step 1: Edit the Required block**

Current content (lines 16–20):
```markdown
Required:

- Target skill directory containing `SKILL.md`.
- Dataset directory with GT/dev data and, when available, holdout/regression data.
- Output directory for workspace copies and audit artifacts.
```

Replace with:
```markdown
Required (full evolution mode):

- Target skill directory containing `SKILL.md`.
- Dataset directory with GT/dev data and, when available, holdout/regression data. If no dataset is provided, the skill enters Degraded Mode (see below) and performs static evaluation only.
- Output directory for workspace copies and audit artifacts.
```

- [ ] **Step 2: Verify package check**

```bash
python3 scripts/check_skill_package.py . --json
```
Expected: `"ok": true`

- [ ] **Step 3: Commit**

```bash
git add skill-evolver/SKILL.md
git commit -m "feat(skill-evolver): soften Inputs required — dataset optional in degraded mode"
```

---

### Task 3: Add `## Degraded Mode (No Dataset)` section

Insert after the last line of `## Self-Contained Bundle Checks` (currently line 76) and before `## Iteration Loop` (currently line 77).

**Files:**
- Modify: `skill-evolver/SKILL.md` (insert after line 76)

- [ ] **Step 1: Insert the Degraded Mode section**

Insert the following block between the last line of `## Self-Contained Bundle Checks` and the `## Iteration Loop` header:

```markdown

## Degraded Mode (No Dataset)

Enter this mode when Phase 0 finds a valid `SKILL.md` but no dataset directory, or when the user explicitly requests evaluation without data.

Do not enter the Iteration Loop from this mode. Output the score card, surface suggestions, and stop.

### L1 Static Check

Run these checks programmatically (no LLM call):

1. **Frontmatter structure** — `name` and `description` fields must be non-empty.
2. **Section presence** — at least one workflow or instruction section must exist after the frontmatter.
3. **Safety scan** — run all 11 rules from `references/safety-rules.md`. Critical (★) findings fail the check immediately; 9 warning-level findings are recorded and reported in the score card.

If either frontmatter or section check fails, stop and report the structural error before running Rubric.

### Built-in Rubric (4 dimensions)

After L1 passes, evaluate the skill with four LLM YES/NO questions. Read the full `SKILL.md` content, then answer each question independently.

| ID | Dimension | Question |
|----|-----------|----------|
| D1 | Trigger precision | "Can a reader determine in 5 seconds whether to invoke this skill for a given request, without confusing it with similar skills?" |
| D2 | Boundary clarity | "Does the skill explicitly state at least one scenario it does NOT handle?" |
| D3 | Workflow coverage | "Does the workflow or instructions section address all major input types mentioned in the description or trigger?" |
| D4 | Example quality | "If examples are present, do they include at least one positive (invoke) and one negative (do not invoke) case? If no examples are present, answer NO." |

Each dimension: YES = pass, NO = fail. Score = `passed_count / 4`.

### Score Card Output

Report in this format:

```
=== Degraded Mode Evaluation ===
Skill: <name from frontmatter>
Mode: No dataset — L1 + Rubric only

L1 Static Check
  structure:  PASS | FAIL — <reason>
  safety:     PASS | <n> warnings

Rubric
  D1 trigger precision:  YES | NO
  D2 boundary clarity:   YES | NO
  D3 workflow coverage:  YES | NO
  D4 example quality:    YES | NO

Score: <n>/4 rubric dimensions passed

Suggestions:
  <one line per NO dimension: what to add or fix>

Safety warnings:
  <list each warning-level finding with rule ID and description>
```

For each NO dimension, produce one concrete suggestion:
- D1 NO → "Tighten the description or add 1–2 specific trigger examples to distinguish this skill from similar ones."
- D2 NO → "Add a 'Do not use when...' line or sentence to the description or frontmatter."
- D3 NO → "Identify any input type mentioned in the trigger that has no corresponding handling in the workflow body, and add a handling rule or explicit exclusion."
- D4 NO → "Add at least one negative example showing a request that should NOT trigger this skill."

### Operator Checkpoint

After the score card is written, pause and present options:

1. Operator edits SKILL.md manually based on suggestions, then re-runs degraded mode to recheck.
2. Operator provides a dataset directory to unlock full evolution mode.
3. Operator exits.

Do not proceed to the Iteration Loop under any circumstance from this mode.

```

- [ ] **Step 2: Verify section is present and package check passes**

```bash
python3 -c "
content = open('SKILL.md').read()
assert '## Degraded Mode (No Dataset)' in content, 'Section missing'
assert '## Iteration Loop' in content, 'Iteration Loop section gone'
print('section headers OK')
"
python3 scripts/check_skill_package.py . --json
```
Expected: `section headers OK` and `"ok": true`

- [ ] **Step 3: Commit**

```bash
git add skill-evolver/SKILL.md
git commit -m "feat(skill-evolver): add Degraded Mode section (L1 + 4-dim Rubric, no loop)"
```

---

### Task 4: Add `## Trace Extraction` section

Insert immediately after the Degraded Mode section added in Task 3, still before `## Iteration Loop`.

**Files:**
- Modify: `skill-evolver/SKILL.md` (insert after new Degraded Mode section)

- [ ] **Step 1: Insert the Trace Extraction section**

```markdown

## Trace Extraction

Enter this mode when the user pastes a conversation excerpt and asks to extract a trace, or says they want to build a dataset from a conversation.

This mode does not require a dataset to already exist. It creates or appends to one.

### Steps

1. **Identify invocation boundary**

   Locate:
   - The user message that triggered the skill (this becomes `input`).
   - The assistant's final response after the skill completed (this becomes `expected_output`).

   If multiple skill invocations are present in the paste, process them one at a time in order.

   If the boundary is ambiguous (e.g. the skill was interrupted mid-execution), ask the user to mark the start and end before proceeding.

2. **Extract fields**

   | Field | Source |
   |-------|--------|
   | `id` | Auto-generate: `extracted-<YYYYMMDD>-<n>` where n is a zero-padded counter starting at 001 |
   | `input` | User message text that triggered the skill |
   | `expected_output` | Full assistant response, or user-highlighted portion if the user marked a subset |
   | `skill` | Skill name if identifiable from the conversation context; else ask the user |
   | `split` | Default `dev`; prompt the user to override to `gt`, `holdout`, or `regression` if appropriate |
   | `notes` | Empty string by default; user may add annotation |

3. **Show draft and confirm**

   Present the draft in this format before saving anything:

   ```
   === Extracted Trace Draft ===
   id:              extracted-<date>-001
   skill:           <skill name>
   split:           dev
   input:
     <extracted user message>
   expected_output:
     <extracted assistant response>
   notes:           (empty)

   Target dataset dir: <dataset-dir or ask if unknown>
   Will write:
     <dataset-dir>/traces/dev-extracted-001.json
     append to: <dataset-dir>/dev.jsonl

   Confirm? [y = save / n = discard / e = edit fields]
   ```

   Wait for operator response. If `e`, apply the user's edits and re-show the draft before saving.

4. **Save on confirmation**

   Write the trace file:

   ```json
   {
     "id": "extracted-<date>-001",
     "skill": "<skill name>",
     "split": "dev",
     "input": "...",
     "expected_output": "...",
     "notes": ""
   }
   ```

   Append one index line to `<dataset-dir>/dev.jsonl` (or the split-appropriate `.jsonl`):

   ```jsonl
   {"id": "extracted-<date>-001", "trace_path": "traces/dev-extracted-001.json", "split": "dev"}
   ```

   Confirm save with: `Saved: <trace_path>  Appended to: <jsonl_path>`

### Constraints

- Auto-extracted traces default to `dev` split. If the user wants a GT trace, they must explicitly confirm the output is the authoritative correct answer.
- If the target dataset directory does not exist yet, ask the user to confirm the path before creating it.
- Do not attempt to scan `~/.claude/` or any log file. Only process text the user explicitly pastes.

```

- [ ] **Step 2: Verify both new sections are present, order is correct, package check passes**

```bash
python3 -c "
content = open('SKILL.md').read()
dm_pos = content.index('## Degraded Mode (No Dataset)')
te_pos = content.index('## Trace Extraction')
il_pos = content.index('## Iteration Loop')
assert dm_pos < te_pos < il_pos, f'Wrong order: DM={dm_pos} TE={te_pos} IL={il_pos}'
print('section order OK')
"
python3 scripts/check_skill_package.py . --json
```
Expected: `section order OK` and `"ok": true`

- [ ] **Step 3: Commit**

```bash
git add skill-evolver/SKILL.md
git commit -m "feat(skill-evolver): add Trace Extraction section (paste-to-trace helper)"
```

---

### Task 5: Smoke test — invoke degraded mode against example skill

Verify the two new modes are correctly routable by reading the updated SKILL.md with a target skill that has no dataset.

**Files:** Read-only. No edits.

- [ ] **Step 1: Confirm `assets/example/target_skill/SKILL.md` exists and has no associated dataset**

```bash
ls skill-evolver/assets/example/target_skill/SKILL.md
```
Expected: file exists.

- [ ] **Step 2: Manually invoke skill-evolver against the example skill with no dataset path**

Compose a trigger message and confirm the routing instructions in the updated SKILL.md correctly direct to Degraded Mode. Read the updated SKILL.md trigger section and confirm:

```bash
python3 -c "
content = open('SKILL.md').read()
checks = [
    'Degraded Mode' in content,
    'Trace Extraction' in content,
    'No dataset is provided, the skill enters Degraded Mode' in content,
    'D1' in content and 'D2' in content and 'D3' in content and 'D4' in content,
    'extracted-<YYYYMMDD>' in content,
]
for i, ok in enumerate(checks, 1):
    print(f'Check {i}: {\"PASS\" if ok else \"FAIL\"}')
assert all(checks), 'One or more checks failed'
"
```
Expected: all 5 checks PASS.

- [ ] **Step 3: Run final package check**

```bash
python3 scripts/check_skill_package.py . --json
python3 scripts/validate_dataset.py assets/example/dataset --json
```
Expected: both `"ok": true`

- [ ] **Step 4: Tag completion**

```bash
git log --oneline -5
```
Confirm the 4 feature commits from Tasks 1–4 are present.

---

## Summary

| Task | Change | Verification |
|------|--------|-------------|
| 1 | Frontmatter + intro routing | `check_skill_package.py` |
| 2 | Soften Inputs Required | `check_skill_package.py` |
| 3 | Add Degraded Mode section | section header check + package check |
| 4 | Add Trace Extraction section | section order check + package check |
| 5 | Smoke test (read-only) | 5-point assertion script |
