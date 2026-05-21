# skill-evolver Path A Optimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align `skill-evolver/SKILL.md` with the article's described mechanisms (8-phase loop, 3-tier eval, 5-dim AND gate, trace diagnosis) by surgical edits — extract Mutation/Evaluation Layers detail to `references/`, add Dependencies/Eval-Noise/Safety-Rules sections, reconcile the Atomic gate, and bring `SKILL.md` back under the project's < 200-line rule — without altering any existing contract language.

**Architecture:** P1 surgical edits only — "add" and "move", never "delete contract" or "rewrite". 4 new reference files, 1 SKILL.md restructure split into 6 atomic edits, 1 README rationale line, 0 script logic changes (1 script REQUIRED_FILES list extension only). All verification via `wc/grep/python3 scripts/...` — no new toolchain.

**Tech Stack:** Markdown + Python 3 (stdlib only) + git. No tests beyond grep-as-assertion + existing `check_skill_package.py` exit code.

**Assumption Audit (假设审计):**
1. **SKILL.md is currently 239 lines** — verified via `wc -l`. If wrong, AC1 threshold needs recheck but plan structure unchanged.
2. **`Single file < 200 lines` from `.claude/AGENTS.md` applies to `SKILL.md`** — explicit project rule. If exempt, AC1 can relax to "no growth"; otherwise plan stands.
3. **Article's "11 safety rules" is meant as a target set, not a precise canonical list** — author drafts 11 reasonable rules in `safety-rules.md`; if user already has a canonical list, swap content in Task 2 only.
4. **`assets/example/` data exists and `check_skill_package.py` baseline error is only `.DS_Store` × 2** — verified at plan time. AC11 thus becomes "errors set is unchanged or shrunk by Path A; .DS_Store noise is pre-existing OS junk and out of scope".
5. **`scripts/check_skill_package.py` REQUIRED_FILES extension is the right place to enforce new references** — if user prefers a separate validator, swap Task 9 to a new helper.
6. **No GT-driven runtime verification this round** — Path B (running skill-evolver against itself) is explicitly out of scope per spec §1.

If any of (1)–(3) prove wrong, the plan can be adjusted in-task without restructuring. (4)–(6) are scope guardrails.

---

## File Structure

| File | Status | Responsibility |
| --- | --- | --- |
| `skill-evolver/SKILL.md` | modify | Contract spec only; details delegated to references; ≤ 200 lines |
| `skill-evolver/references/safety-rules.md` | **create** | 11 L1 safety rules (2 critical ★, 9 warning), each with detect/level/fix |
| `skill-evolver/references/mutation-layers.md` | **create** | Layer 1/2/3 full definitions, cross-layer rule, escalation/exhaustion |
| `skill-evolver/references/evaluation-layers.md` | **create** | L1 4-step, L2 8 assertion taxonomy, L3 trigger/holdout/regression/A-B |
| `skill-evolver/references/eval-noise.md` | **create** | Repeat-N protocol, variance threshold, re-eval triggers, cost trade-off |
| `skill-evolver/references/dataset-format.md` | modify | Append "GT generation via skill-creator" section |
| `skill-evolver/README.md` | modify | One-line meta-evolution rationale link |
| `skill-evolver/scripts/check_skill_package.py` | modify | Add 4 new references to `REQUIRED_FILES` |
| `docs/superpowers/plans/2026-05-21-skill-evolver-optimization-state.local.md` | **create** | BDD state tracker (this plan) |

**Out of scope:** `assets/example/*` (Path B), `scripts/setup_workspace.py`, `scripts/validate_dataset.py`, `FAQ.md`, `QUICKSTART.md`, `PACKAGING.md`, `RELEASE.md`, `agents/`, `test-prompts.json`.

---

## Task 0: Capture Baseline Invariants

**Why:** Surgical edits depend on knowing exactly what contract language must survive. We grep a fingerprint set before touching anything; later tasks must keep these greps non-empty.

**Files:**
- Read-only: `skill-evolver/SKILL.md`
- Create: `docs/superpowers/plans/2026-05-21-skill-evolver-optimization-state.local.md` (BDD state tracker)

- [ ] **Step 1: Run baseline metrics**

```bash
wc -l skill-evolver/SKILL.md skill-evolver/references/*.md
python3 skill-evolver/scripts/check_skill_package.py skill-evolver --json
```

Expected: SKILL.md = 239 lines; check_skill_package errors = 2 × `.DS_Store` only.

- [ ] **Step 2: Record invariant grep fingerprints**

```bash
cd skill-evolver && \
  grep -c "structure_and_safety" SKILL.md && \
  grep -c "dev_quality" SKILL.md && \
  grep -c "strict_quality" SKILL.md && \
  grep -c "cost_budget" SKILL.md && \
  grep -c "atomic_auditability" SKILL.md && \
  grep -c "Review -> Ideate -> Modify -> Commit -> Verify -> Gate -> Log -> Loop" SKILL.md && \
  grep -c "counterfactual" SKILL.md && \
  grep -c "Layer 1" SKILL.md && grep -c "Layer 2" SKILL.md && grep -c "Layer 3" SKILL.md
```

Expected: all counts ≥ 1. Save outputs into the state tracker file as the "must remain non-zero" baseline.

- [ ] **Step 3: Create state tracker file**

```markdown
# skill-evolver Path A Optimization — State Tracker

## Baseline Invariants (must remain non-zero after every task)
- structure_and_safety: 1
- dev_quality: 1
- strict_quality: 1
- cost_budget: 1
- atomic_auditability: 1
- 8-phase loop arrow line: 1
- counterfactual: 1
- Layer 1 / Layer 2 / Layer 3: ≥1 each

## Tasks
- [ ] Task 0 baseline captured
- [ ] Task 1 references/safety-rules.md
- [ ] Task 2 references/mutation-layers.md
- [ ] Task 3 references/evaluation-layers.md
- [ ] Task 4 references/eval-noise.md
- [ ] Task 5 references/dataset-format.md (append GT-gen)
- [ ] Task 6 SKILL.md surgical edits (split 6a-6f)
- [ ] Task 7 README.md rationale line
- [ ] Task 8 check_skill_package.py REQUIRED_FILES update
- [ ] Task 9 final verification matrix

## Failures / Surprises
(record here if any baseline grep returns 0 or wc -l differs)
```

Save to: `docs/superpowers/plans/2026-05-21-skill-evolver-optimization-state.local.md`

- [ ] **Step 4: Commit baseline tracker**

```bash
git add docs/superpowers/plans/2026-05-21-skill-evolver-optimization-state.local.md
git commit -m "chore(skill-evolver): capture Path A baseline invariants"
```

---

## Task 1: Create `references/safety-rules.md` (G2)

**Files:**
- Create: `skill-evolver/references/safety-rules.md`

- [ ] **Step 1: Write the file**

Content (copy verbatim):

```markdown
# L1 Safety Rules

This is the canonical rule set scanned by L1 quick guard. Critical findings (★) cause immediate L1 fail; warnings are recorded into the iteration's findings buffer for Ideate to consider.

## Critical (★) — Auto-block

| ID | Pattern | Detect | Fix Hint |
| --- | --- | --- | --- |
| ★ R1 | Dangerous removal — `rm -rf` (especially with `/`, `$HOME`, `~`, `..`, env vars) | regex over `SKILL.md` and any file under `scripts/` | Replace with scoped per-path delete; never templated paths |
| ★ R2 | Hardcoded credentials — API key / token / secret / private key marker | regex over all bundle files: `(api[_-]?key|secret|token|BEGIN .* PRIVATE KEY)` | Move to env var or docs-only placeholder |

## Warning — Recorded, not blocking

| ID | Pattern | Detect | Fix Hint |
| --- | --- | --- | --- |
| R3 | Hardcoded absolute path (`/Users/...`, `/home/...`, `C:\\...`) | regex | Use relative paths or `${HOME}` |
| R4 | Mutation of global git config (`git config --global`, `git config user.*` outside workspace) | regex | Scope changes to the isolated workspace copy |
| R5 | Unbounded network call (`curl`/`wget` without explicit allow-listed host) | regex | Pin host or require explicit allow-list |
| R6 | Dynamic shell — `eval`, `bash -c "$VAR"`, `exec` of constructed strings | regex | Inline the command literally |
| R7 | Cross-layer file pattern (e.g. Layer 1 mutation touching `scripts/`) | declared `target_layer` vs `target_files` | Split into another iteration on the right layer |
| R8 | SKILL.md frontmatter missing required field (`name`, `description`) | YAML parse | Repair frontmatter |
| R9 | `description` field overflow (> 1024 chars) — undermines Claude trigger weighting | character count | Tighten and move detail into the body |
| R10 | Mutation modifies an audit artifact outside `evolve_plan.md` / `baseline.json` (e.g. rewriting `experiments.jsonl` history) | path match against artifact list | Append-only writes; never edit prior rows |
| R11 | Mutation proposal lacks any `trace_path` reference | proposal field check in Ideate | Discard the iteration before Modify |

## Levels

- ★ critical: L1 returns `fail`. Iteration is discarded before L2.
- warning: L1 returns `pass` with `findings: [...]`. Findings are passed to Phase 1 Review of the next iteration.

## Out of Scope (Path B)

Wiring R1–R11 into `scripts/` as auto-detection is deferred. This document defines the contract; runtime enforcement may rely on agent inspection until a checker script is added.
```

- [ ] **Step 2: Verify file exists and is well-formed**

```bash
wc -l skill-evolver/references/safety-rules.md
grep -c "^| ★ R" skill-evolver/references/safety-rules.md
grep -c "^| R" skill-evolver/references/safety-rules.md
```

Expected: file exists; star-rule count = 2; warning-rule count = 9; total rules = 11.

- [ ] **Step 3: Commit**

```bash
git add skill-evolver/references/safety-rules.md
git commit -m "feat(skill-evolver): add references/safety-rules.md with 11 L1 rules (G2)"
```

---

## Task 2: Create `references/mutation-layers.md`

**Why:** Extracted from SKILL.md so the contract stays terse but the detail lives somewhere readable.

**Files:**
- Create: `skill-evolver/references/mutation-layers.md`

- [ ] **Step 1: Write the file**

```markdown
# Mutation Layers

Each iteration mutates exactly one layer. Cross-layer changes must be split into another iteration.

## Layer 1 — Trigger and routing (lowest cost)

**May edit:** trigger rules, invocation boundaries, routing hints, short examples, compact usage guards inside `SKILL.md`.

- Do: tighten the `description:` to better reflect when to invoke.
- Do: add a one-line guard like "do not use when X".
- Don't: rewrite multi-paragraph workflow logic — that is Layer 2.

## Layer 2 — Skill body (medium cost)

**May edit:** substantive workflow instructions, examples, refusal behavior, failure handling, decision policy inside `SKILL.md`.

- Do: rewrite a phase's procedure when trace evidence shows the current procedure mis-routes.
- Don't: edit `scripts/` or `references/` — that is Layer 3.

## Layer 3 — Support material (highest cost)

**May edit:** `scripts/*`, `references/*`, dataset adapters, bundled helper resources.

- Do: change `scripts/setup_workspace.py` only when trace evidence proves the failure lives in the helper.
- Don't: jump here just because Layer 1/2 felt slow — exhaust them first.

## Promotion rules

A layer is exhausted when **all three** are true:
1. ≥ 3 trace-backed atomic attempts in that layer
2. None produced a keep
3. Review cannot name a new counterfactual in that layer that is meaningfully different from prior failed patterns

When all lower layers are exhausted, the next higher layer becomes eligible. Do not skip directly to Layer 3 unless lower layers are exhausted **or** trace evidence already proves the failure lives in helper material.

## Atomic enforcement

Default: a single iteration touches at most **one file**. When `target_files` explicitly declares a pattern (e.g. "all warning rules in `references/safety-rules.md`"), up to **5 files** is permitted. Anything beyond 5 fails `atomic_auditability`.
```

- [ ] **Step 2: Verify**

```bash
wc -l skill-evolver/references/mutation-layers.md
grep -c "^## Layer" skill-evolver/references/mutation-layers.md
```

Expected: 3 `## Layer` headings.

- [ ] **Step 3: Commit**

```bash
git add skill-evolver/references/mutation-layers.md
git commit -m "feat(skill-evolver): add references/mutation-layers.md (extract detail from SKILL.md)"
```

---

## Task 3: Create `references/evaluation-layers.md`

**Files:**
- Create: `skill-evolver/references/evaluation-layers.md`

- [ ] **Step 1: Write the file**

```markdown
# Evaluation Layers

Three tiers, cost-ascending. Cheap tiers run every iteration; expensive tiers run on triggers.

## L1 — Quick guard (seconds, every iteration)

Runs four programmatic checks:

1. `SKILL.md` structure — frontmatter present, required sections in place.
2. `quick_validate` from skill-creator — format / metadata sanity.
3. Safety scan — see `references/safety-rules.md` (11 rules; 2 critical, 9 warning).
4. GT smoke sample — randomly sample 3 GT cases and confirm structural soundness.

A single critical (★) safety finding causes immediate L1 fail; the iteration is discarded before L2.

## L2 — Dev eval (minutes, every iteration after L1 passes)

Runs the full dev split case-by-case. Records per-case `id`, `input`, `actual_output`, `expected_output`, `assertion_results`, `pass/fail`, `score`, `trace_path`.

### Assertion taxonomy (default)

Programmatic (deterministic, runs in code):

- `contains` — substring match
- `not_contains` — substring absence
- `regex` — pattern match
- `path_hit` — agent-cited file path matches expected (still programmatic when comparison is exact)
- `json_field` — extract field, compare value
- `script_check` — run a script, assert exit code

Bounded LLM YES/NO (LLM emits a label; pass rate is counted programmatically):

- `fact_coverage` — does the output cover stated facts? (LLM evaluates per-fact)
- `llm_judge` — single rubric question with YES/NO output

## L3 — Strict eval (~10 min, conditional)

Triggers (defaults; `evolve_plan.md` may override):

- Every 3 iterations.
- Whenever dev pass-rate ≥ 0.90.
- Before any layer promotion.
- Before final validation / finalization.

Datasets covered:

- **holdout** — never seen by the optimizer; the over-fit guard.
- **regression** — case set that must keep passing; the no-backslide guard.
- **blind A/B** (optional) — only when explicitly requested by the user or `evolve_plan.md`.

## Why three tiers, not one

L1 catches obvious damage cheaply. L2 catches behavioral regressions on the dev set. L3 catches over-fitting and silent regressions. Running L3 every iteration is wasteful; running only L3 means cheap iterations get expensive feedback. The split keeps wasted-iteration cost to L1 — typically seconds.
```

- [ ] **Step 2: Verify**

```bash
wc -l skill-evolver/references/evaluation-layers.md
grep -c "^## L" skill-evolver/references/evaluation-layers.md
grep -c "fact_coverage\|llm_judge\|contains\|regex\|path_hit\|json_field\|script_check\|not_contains" skill-evolver/references/evaluation-layers.md
```

Expected: 3 `## L` headings; assertion-name count ≥ 8.

- [ ] **Step 3: Commit**

```bash
git add skill-evolver/references/evaluation-layers.md
git commit -m "feat(skill-evolver): add references/evaluation-layers.md (extract detail from SKILL.md)"
```

---

## Task 4: Create `references/eval-noise.md` (G1)

**Files:**
- Create: `skill-evolver/references/eval-noise.md`

- [ ] **Step 1: Write the file**

```markdown
# LLM Eval Noise Mitigation

LLM-judged assertions (`fact_coverage`, `llm_judge`) and overall pass-rate measurements drift across runs even when the skill state and GT are identical. Observed range can be ±0.10 on the same fixture.

## Default protocol

- **Repeat N**: every L2 / L3 evaluation that crosses a gate boundary is run **N = 3** times by default. Configurable in `evolve_plan.md` via `eval.repeat_n` (min 1, max 5).
- **Aggregation**: report median; record min, max, and per-run scores in `experiments.jsonl`.
- **Variance threshold**: if max − min > 0.05 on any aggregated metric, mark the result `noisy: true`.

## When to re-eval

Trigger an extra evaluation pass when **any** of:

- Iteration is provisionally a keep but margin to the kept checkpoint is < `eval.noise_margin` (default 0.02).
- `dev_pass_rate` is within 0.02 of the L3 trigger threshold (default 0.90).
- The proposer's `expected_fix` predicts a metric jump > 0.05 but observed jump is < 0.02 (the proposer's prediction failed; check whether the real signal is masked by noise).

## Cost trade-off

`N = 3` triples L2 token cost. The article reports this is the dominant cost driver. Reduce only when noise variance has been observed < 0.02 over 5 consecutive iterations on the current dataset.

## Out of scope

- Choosing a less stochastic judge model (decoupled from this skill).
- Fingerprinting the prompt for cache reuse (skill-creator's territory).
```

- [ ] **Step 2: Verify**

```bash
wc -l skill-evolver/references/eval-noise.md
grep -c "Repeat N" skill-evolver/references/eval-noise.md
```

Expected: file exists, "Repeat N" matched.

- [ ] **Step 3: Commit**

```bash
git add skill-evolver/references/eval-noise.md
git commit -m "feat(skill-evolver): add references/eval-noise.md (G1 noise mitigation)"
```

---

## Task 5: Append GT-generation section to `references/dataset-format.md` (G4)

**Files:**
- Modify: `skill-evolver/references/dataset-format.md`

- [ ] **Step 1: Read the current file**

```bash
cat skill-evolver/references/dataset-format.md
```

Capture the trailing line so the append is clean.

- [ ] **Step 2: Append a new section**

Append (do not replace) the following to the file end:

```markdown

## Generating GT when you don't have one

If your skill has no curated GT yet, do not block — bootstrap one:

1. Use **skill-creator's eval generator** to draft an initial GT set against your skill's intended inputs. Treat its output as a candidate, not as ground truth.
2. Manually review at least the first 10 cases. Discard or rewrite any case whose `expected` is ambiguous or whose `assertion` cannot be made deterministic.
3. Split the reviewed set into `gt.jsonl` (the contract) and `dev.jsonl` (the optimization target). Keep `holdout.jsonl` and `regression.jsonl` empty until you have a stable dev pass-rate; populate them when the loop reaches first L3 trigger.
4. After the first 3 keeps in the loop, audit any case that the optimizer "fixed" with a Layer 1 trigger edit — those edits sometimes reveal that the GT case itself was under-specified.

The aim is a small, hand-trusted seed (10–30 cases). The loop's failure traces will tell you which cases to add next.
```

- [ ] **Step 3: Verify**

```bash
wc -l skill-evolver/references/dataset-format.md
grep -c "skill-creator's eval generator" skill-evolver/references/dataset-format.md
```

Expected: file grew by ~12 lines; new section detected once.

- [ ] **Step 4: Commit**

```bash
git add skill-evolver/references/dataset-format.md
git commit -m "docs(skill-evolver): document GT generation via skill-creator (G4)"
```

---

## Task 6: SKILL.md surgical edits (split into 6 atomic edits)

**Files:**
- Modify: `skill-evolver/SKILL.md`

Each sub-step is a single Edit. Verify after each. Commit at the end of all 6 with a single message — but only if `wc -l SKILL.md ≤ 200` and all baseline greps from Task 0 still return ≥ 1.

### Task 6a: Add Dependencies section (G3)

- [ ] **Step 1: Edit**

After the line that ends the opening summary (right before `## Phase 0: Setup`), insert a new section. Locate the existing line in the file:

```text
The helper is optional. If it cannot run in the local environment, perform the same setup manually and write the artifacts.
```

Then locate `## Operator Checkpoints` (the next section heading after Phase 0). Use Edit to insert this BEFORE `## Phase 0: Setup`:

```markdown
## Dependencies

- **skill-creator** — hard dependency. Phase 0 baseline, L1 `quick_validate`, L2 `grader`, L3 `comparator`, and optional GT generation all rely on it. If skill-creator is unavailable, stop and surface the gap; do not attempt manual fallbacks for these capabilities.
- **git** — preferred for checkpointing and rollback. When unavailable, fall back to reversible file snapshots (Commit phase records the snapshot path as the checkpoint).

```

(The trailing blank line is intentional.)

- [ ] **Step 2: Verify**

```bash
grep -n "^## Dependencies" skill-evolver/SKILL.md
grep -c "skill-creator" skill-evolver/SKILL.md
```

Expected: `## Dependencies` heading present once; `skill-creator` count ≥ 2.

### Task 6b: Replace Mutation Layers detail with reference pointer

- [ ] **Step 1: Edit**

Find the existing `## Mutation Layers` block in `SKILL.md` (currently 9 lines starting at "Do not cross layers in a single iteration."). Replace the **entire block** including its heading with:

```markdown
## Mutation Layers

Each iteration mutates exactly one layer:

- **Layer 1** — `SKILL.md` trigger rules, invocation boundaries, routing hints, short examples, compact usage guards.
- **Layer 2** — `SKILL.md` substantive workflow instructions, examples, refusal behavior, failure handling, decision policy.
- **Layer 3** — `scripts/*`, `references/*`, dataset adapters, bundled helper resources.

Do not cross layers in a single iteration. For full layer definitions, escalation rules, exhaustion criteria, and atomic-file enforcement, read `references/mutation-layers.md`.
```

- [ ] **Step 2: Verify**

```bash
grep -c "^## Mutation Layers" skill-evolver/SKILL.md
grep -c "references/mutation-layers.md" skill-evolver/SKILL.md
grep -c "Layer 1" skill-evolver/SKILL.md
grep -c "Layer 2" skill-evolver/SKILL.md
grep -c "Layer 3" skill-evolver/SKILL.md
```

Expected: heading once; reference pointer once; each Layer N still present.

### Task 6c: Replace Evaluation Layers detail with reference pointer

- [ ] **Step 1: Edit**

Find the existing `## Evaluation Layers` block (about 16 lines, starts with "L1 quick guard is programmatic..."). Replace the **entire block** including its heading with:

```markdown
## Evaluation Layers

Three cost-ascending tiers gate every iteration:

- **L1 quick guard** — programmatic; always runs; immediate fail on any critical (★) safety finding.
- **L2 dev eval** — runs after L1 passes; full dev split case-by-case using the assertion taxonomy.
- **L3 strict eval** — conditional; covers `holdout` and `regression`; runs every 3 iterations, when dev pass-rate ≥ 0.90, before any layer promotion, and before final validation.

For the full L1 four-step procedure, the L2 assertion taxonomy (8 default assertions: 6 programmatic, 2 bounded LLM YES/NO), L3 trigger details, and the optional blind A/B comparator, read `references/evaluation-layers.md`.
```

- [ ] **Step 2: Verify**

```bash
grep -c "^## Evaluation Layers" skill-evolver/SKILL.md
grep -c "references/evaluation-layers.md" skill-evolver/SKILL.md
grep -c "L1\|L2\|L3" skill-evolver/SKILL.md
```

Expected: heading once; reference pointer once; L1/L2/L3 still well-represented.

### Task 6d: Add Eval Noise Mitigation section (G1)

- [ ] **Step 1: Edit**

Insert directly **after** the new compact `## Evaluation Layers` block and **before** `## Stop Rules`:

```markdown
## Eval Noise Mitigation

LLM-judged metrics drift across runs. To prevent flapping keep/discard decisions:

- Repeat L2 / L3 evaluation **N = 3** times for any iteration that crosses a gate boundary; configurable via `eval.repeat_n` in `evolve_plan.md`.
- Aggregate by **median**; record min, max, per-run scores, and a `noisy` flag (true when max − min > 0.05) in `experiments.jsonl`.
- Re-eval when the keep/discard margin is below the noise threshold or when the proposer's predicted jump diverges from the observed jump.

Full protocol, cost trade-offs, and re-eval triggers in `references/eval-noise.md`.
```

- [ ] **Step 2: Verify**

```bash
grep -c "^## Eval Noise Mitigation" skill-evolver/SKILL.md
grep -c "references/eval-noise.md" skill-evolver/SKILL.md
```

Expected: heading once; reference pointer once.

### Task 6e: Add Safety Rules section (G2)

- [ ] **Step 1: Edit**

Insert **immediately after** the `## Eval Noise Mitigation` block:

```markdown
## Safety Rules

L1 quick guard scans 11 safety rules — 2 critical (★) cause immediate L1 fail; 9 warnings are recorded into the iteration's findings buffer for the next Review. Full rule list with detect / level / fix is in `references/safety-rules.md`.

```

(Trailing blank line intentional.)

- [ ] **Step 2: Verify**

```bash
grep -c "^## Safety Rules" skill-evolver/SKILL.md
grep -c "references/safety-rules.md" skill-evolver/SKILL.md
```

Expected: heading once; reference pointer once.

### Task 6f: Reconcile Atomic judgment line (G7)

- [ ] **Step 1: Edit**

In the Gate section, find the line:

```text
- `atomic_auditability`: pass only when the mutation stays within one declared layer, touches no more than one file unless `target_files` explicitly allowed a pattern, and the iteration summary, traces, and checkpoint path are all present.
```

Replace with:

```text
- `atomic_auditability`: pass only when the mutation stays within one declared layer, touches no more than one file by default — up to 5 files when `target_files` explicitly declares a pattern (e.g. all warning rules in `references/safety-rules.md`) — and the iteration summary, traces, and checkpoint path are all present.
```

- [ ] **Step 2: Verify**

```bash
grep -c "up to 5 files" skill-evolver/SKILL.md
grep -c "atomic_auditability" skill-evolver/SKILL.md
```

Expected: "up to 5 files" appears once; `atomic_auditability` count unchanged from Task 0 baseline.

### Task 6 final verification + commit

- [ ] **Step 1: Re-run all baseline invariant greps**

```bash
cd skill-evolver && \
  echo "=== Line count ===" && wc -l SKILL.md && \
  echo "=== Invariants ===" && \
  for tok in structure_and_safety dev_quality strict_quality cost_budget atomic_auditability counterfactual; do \
    printf "%s: " "$tok"; grep -c "$tok" SKILL.md; \
  done && \
  echo "=== 8-phase loop arrow ===" && \
  grep -c "Review -> Ideate -> Modify -> Commit -> Verify -> Gate -> Log -> Loop" SKILL.md && \
  echo "=== Layer present ===" && \
  for L in "Layer 1" "Layer 2" "Layer 3"; do printf "%s: " "$L"; grep -c "$L" SKILL.md; done
```

Expected: line count ≤ 200; every count ≥ 1; arrow line still present.

If line count > 200: locate which inserted block is the largest contributor and trim by moving prose into the matching reference. Do **not** delete contract language to make the line budget — fail the task and surface the choice instead.

- [ ] **Step 2: Commit all 6 edits at once**

```bash
git add skill-evolver/SKILL.md
git commit -m "refactor(skill-evolver): trim SKILL.md to <200 lines, add deps/noise/safety pointers (G1/G2/G3/G6/G7)"
```

---

## Task 7: README rationale line (G8)

**Files:**
- Modify: `skill-evolver/README.md`

- [ ] **Step 1: Read the current README**

```bash
cat skill-evolver/README.md | head -40
```

Identify a natural insertion point near the top (after the one-line summary, before the install / usage block).

- [ ] **Step 2: Insert one rationale paragraph**

Use Edit to insert a short paragraph (~3 lines) introducing the meta-evolution self-test as the design rationale. Keep it factual — link to the article only if a path/URL exists in the bundle, otherwise say "self-evolution self-test (see project doc)."

Example content (adjust wording to match existing README tone):

```markdown
> Design rationale — skill-evolver was validated by running it against itself for 19 iterations with zero rollbacks; that meta-evolution exercise is the source of the 5-dimension AND gate, the 3-tier evaluation, and the trace-driven proposer protocol described in `SKILL.md` and the `references/`.
```

- [ ] **Step 3: Verify**

```bash
grep -c "meta-evolution\|meta evolution\|19 iterations" skill-evolver/README.md
```

Expected: ≥ 1.

- [ ] **Step 4: Commit**

```bash
git add skill-evolver/README.md
git commit -m "docs(skill-evolver): add meta-evolution self-test rationale (G8)"
```

---

## Task 8: Extend `check_skill_package.py` REQUIRED_FILES

**Files:**
- Modify: `skill-evolver/scripts/check_skill_package.py`

- [ ] **Step 1: Edit REQUIRED_FILES list**

Locate `REQUIRED_FILES = [...]` (lines 9–24). Append four entries inside the list, immediately after `"references/runbook.md",`:

```python
    "references/safety-rules.md",
    "references/mutation-layers.md",
    "references/evaluation-layers.md",
    "references/eval-noise.md",
```

- [ ] **Step 2: Run the script and confirm new files are tracked**

```bash
python3 skill-evolver/scripts/check_skill_package.py skill-evolver --json
```

Expected: still 2 errors (`.DS_Store` × 2 — pre-existing, out of scope); `checked_files` increases from 14 to 18; **no new errors of the form `Missing required file:`**.

If a `Missing required file: references/...` error appears, the corresponding Task 1–4 file is missing or mis-named. Fix and re-run.

- [ ] **Step 3: Commit**

```bash
git add skill-evolver/scripts/check_skill_package.py
git commit -m "chore(skill-evolver): track new references in check_skill_package"
```

---

## Task 9: Final verification matrix (Acceptance Criteria sweep)

**Files:**
- No edits. Read-only verification + state tracker update.

- [ ] **Step 1: Run all 11 ACs in sequence**

```bash
cd /Users/admin/openSource/my-claude-skills

echo "=== AC1: SKILL.md <= 200 lines ===" && \
  test "$(wc -l < skill-evolver/SKILL.md)" -le 200 && echo PASS || echo FAIL

echo "=== AC2: Dependencies section ===" && \
  grep -q "^## Dependencies" skill-evolver/SKILL.md && \
  grep -q "skill-creator" skill-evolver/SKILL.md && echo PASS || echo FAIL

echo "=== AC3: Eval Noise section ===" && \
  grep -q "^## Eval Noise Mitigation" skill-evolver/SKILL.md && echo PASS || echo FAIL

echo "=== AC4: safety-rules.md (11 rules, 2 critical) ===" && \
  test "$(grep -c '^| ★ R' skill-evolver/references/safety-rules.md)" = "2" && \
  test "$(grep -c '^| R' skill-evolver/references/safety-rules.md)" = "9" && echo PASS || echo FAIL

echo "=== AC5: mutation-layers.md exists; SKILL.md points to it ===" && \
  test -f skill-evolver/references/mutation-layers.md && \
  grep -q "references/mutation-layers.md" skill-evolver/SKILL.md && echo PASS || echo FAIL

echo "=== AC6: evaluation-layers.md exists; SKILL.md points to it ===" && \
  test -f skill-evolver/references/evaluation-layers.md && \
  grep -q "references/evaluation-layers.md" skill-evolver/SKILL.md && echo PASS || echo FAIL

echo "=== AC7: eval-noise.md exists ===" && \
  test -f skill-evolver/references/eval-noise.md && echo PASS || echo FAIL

echo "=== AC8: dataset-format.md has GT-gen section ===" && \
  grep -q "skill-creator's eval generator" skill-evolver/references/dataset-format.md && echo PASS || echo FAIL

echo "=== AC9: Atomic up-to-5 wording ===" && \
  grep -q "up to 5 files" skill-evolver/SKILL.md && echo PASS || echo FAIL

echo "=== AC10: invariants preserved ===" && \
  for tok in structure_and_safety dev_quality strict_quality cost_budget atomic_auditability counterfactual; do \
    grep -q "$tok" skill-evolver/SKILL.md || { echo "FAIL: $tok missing"; exit 1; }; \
  done && echo PASS

echo "=== AC11: check_skill_package no NEW Missing-file errors ===" && \
  python3 skill-evolver/scripts/check_skill_package.py skill-evolver --json | \
    python3 -c "import sys, json; r=json.load(sys.stdin); missing=[e for e in r['errors'] if e.startswith('Missing required file')]; \
    print('PASS' if not missing else f'FAIL: {missing}'); sys.exit(0 if not missing else 1)"
```

Expected: every echo prints PASS.

- [ ] **Step 2: Update state tracker**

In `docs/superpowers/plans/2026-05-21-skill-evolver-optimization-state.local.md`, mark all task checkboxes complete. If any AC failed, record the failure in the "Failures / Surprises" section and STOP — do not commit Task 9.

- [ ] **Step 3: Final commit**

```bash
git add docs/superpowers/plans/2026-05-21-skill-evolver-optimization-state.local.md
git commit -m "chore(skill-evolver): Path A optimization complete — 11/11 ACs pass"
```

- [ ] **Step 4: Report summary**

Output a 5-line summary to the user:
- Final SKILL.md line count
- Number of new reference files
- Number of commits in this session
- AC pass/fail tally
- Suggested next step (Path B decision)

---

## Self-Review

**Spec coverage:**
- AC1 (≤200 lines) → Task 6 final verification
- AC2 (Dependencies + skill-creator) → Task 6a
- AC3 (Eval Noise section) → Task 6d
- AC4 (safety-rules.md, 2 critical, 9 warning) → Task 1
- AC5 (mutation-layers.md + pointer) → Tasks 2 + 6b
- AC6 (evaluation-layers.md + pointer) → Tasks 3 + 6c
- AC7 (eval-noise.md) → Task 4
- AC8 (dataset-format.md GT-gen) → Task 5
- AC9 (Atomic ≤5 wording) → Task 6f
- AC10 (invariants preserved) → Task 0 baseline + Task 6 final + Task 9 sweep
- AC11 (check_skill_package no new Missing errors) → Task 8 + Task 9

All 11 ACs are covered. ✅

**Placeholder scan:** No `TBD`/`TODO`. Every code block is concrete content. The README rationale paragraph in Task 7 contains a model paragraph; tone-adjustment is the only judgement call but it is a single ~3-line addition with a verifiable grep target.

**Type / name consistency:**
- `references/safety-rules.md` referenced consistently in Tasks 1, 6e, 8, 9.
- `references/mutation-layers.md` consistent in 2, 6b, 8, 9.
- `references/evaluation-layers.md` consistent in 3, 6c, 8, 9.
- `references/eval-noise.md` consistent in 4, 6d, 8, 9.
- `eval.repeat_n` config key used consistently in `eval-noise.md` and SKILL.md noise section.
- `## Dependencies`, `## Eval Noise Mitigation`, `## Safety Rules` heading text consistent between content and grep checks.

No drift. ✅

---

## Risks & Rollback

- Any task that breaks an AC10 invariant is rolled back via `git revert HEAD`. Do not amend.
- If Task 6 final verification reports `wc -l > 200`, do **not** delete contract language — re-open the spec and ask the operator (per spec §8 risk register).
- If `check_skill_package.py` introduces new `Missing required file:` errors after Task 8, the corresponding reference is missing — Task 1–4 must be re-checked, not the script.
