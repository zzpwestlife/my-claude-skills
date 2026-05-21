# Darwin baseline evaluation — skill-evolver (round 0)

## Scope
- Target: `skill-evolver/SKILL.md`
- Goal: assess how closely the skill reproduces the article "让 Skill 自己训练自己：8 阶段 Loop、3 层评测、5 维 AND 门控，从此实现自进化".
- Prior Darwin artifacts found: none
- Test prompts created: `skill-evolver/test-prompts.json`
- Eval mode: `full_test` for D8 via independent baseline vs with-skill subagents

## Scorecard
| Dimension | Score (1-10) | Weight | Weighted |
| --- | ---: | ---: | ---: |
| D1 Frontmatter quality | 6.0 | 8 | 4.8 |
| D2 Workflow clarity | 8.5 | 15 | 12.8 |
| D3 Boundary coverage | 6.0 | 10 | 6.0 |
| D4 Checkpoint design | 3.0 | 7 | 2.1 |
| D5 Instruction specificity | 8.0 | 15 | 12.0 |
| D6 Resource integration | 8.5 | 5 | 4.3 |
| D7 Overall architecture | 7.5 | 15 | 11.3 |
| D8 Measured behavior | 7.0 | 25 | 17.5 |
| **Total** |  |  | **70.7 / 100** |

## Why these scores
### D1 Frontmatter quality — 6.0
Strengths:
- `name` is correct.
- `description` states what the skill does and when to use it.

Gaps:
- No explicit "do not use when" boundary.
- No frontmatter examples.
- Description is dense and compresses too many concepts into one sentence.

### D2 Workflow clarity — 8.5
Strengths:
- Clear Phase 0 and exact loop order at `skill-evolver/SKILL.md:58`.
- Inputs, mutation layers, evaluation layers, and stop rules are easy to locate.

Gap:
- The article frames the system as an 8-stage loop with named phases; the skill uses a compressed loop and loses some of that explicit mental model.

### D3 Boundary coverage — 6.0
Strengths:
- Missing paths are called out at `skill-evolver/SKILL.md:10`.
- Optional helper fallback exists at `skill-evolver/SKILL.md:44`.
- Stop rules exist at `skill-evolver/SKILL.md:167`.

Gaps:
- No explicit mis-trigger downgrade path.
- No explicit "this skill is not for X" section.
- Git-unavailable fallback is mentioned, but not the broader non-ideal cases described in the article.

### D4 Checkpoint design — 3.0
Strengths:
- Technical checkpoints exist via commit-before-verify and gate-before-keep.

Gaps:
- No human confirmation checkpoints.
- No pause after baseline / after each optimized round, unlike Darwin's own human-in-loop rule.
- No explicit decision UI / approval moments before expensive or aggressive strategy changes.

### D5 Instruction specificity — 8.0
Strengths:
- Mutation proposal fields are concrete at `skill-evolver/SKILL.md:86`.
- Gate dimensions are concrete at `skill-evolver/SKILL.md:120`.
- Layer boundaries are concrete at `skill-evolver/SKILL.md:151`.

Gap:
- Several critical parts remain under-specified versus the article: exact strict-eval triggers, exact exhaustion thresholds, and what counts as cost budget failure.

### D6 Resource integration — 8.5
Strengths:
- References are wired clearly at `skill-evolver/SKILL.md:20`.
- Helper scripts are discoverable and use standard library only.

Gap:
- The relationship between references and loop phases could be mapped more explicitly for first-time operators.

### D7 Overall architecture — 7.5
Strengths:
- The bundle has a coherent operator model: setup → iterate → gate → log.
- It captures the article's core ideas: trace-first diagnosis, layered eval, AND gate, rollback.

Gaps:
- The article's distinctive structure is only partially preserved:
  - article's explicit **8-phase loop** is compressed;
  - article's **3-layer evaluation** is present but not fully operationalized;
  - article's **5-dimensional AND gate** exists, but pass/fail criteria are still abstract;
  - article's **review memory signals** are weaker than the article's five-signal review step.

### D8 Measured behavior — 7.0
Method:
- Ran 3 prompts with independent subagents in two modes: baseline and with-skill.

Observed behavior:
1. **Setup / plan prompt**
   - With-skill answer was more structured and closer to the intended artifacts, explicitly naming `baseline.json`, `evolve_plan.md`, `.skill_evolve/traces/`, `.skill_evolve/iterations/`, and the L1/L2/L3 ordering.
   - Baseline answer was still decent, so the lift was real but not dramatic.
2. **Trace diagnosis prompt**
   - With-skill answer reliably produced a single atomic proposal with all required fields and kept the mutation at `layer1`.
   - Baseline also got close, but was less anchored to the skill's exact protocol.
3. **Gate / rollback prompt**
   - Both baseline and with-skill reached `discard`.
   - With-skill better matched the artifact logging and next-loop rules, but the practical lift over baseline was modest.

Conclusion:
- The skill improves structure and operator discipline.
- It does not yet create a dramatic enough behavioral delta over a strong baseline assistant.

## Gap vs target article
1. **8-phase loop is not explicit enough**
   - Article: Setup + Review / Ideate / Modify / Commit / Verify / Gate / Log / Loop.
   - Current skill: close, but misses the article's stronger naming and phase intent, especially the five review signals and explicit stuck-strategy switches.

2. **Three-layer evaluation lacks article-level detail**
   - Article: L1 security + smoke + quick_validate, L2 full dev with 8 assertion modes, L3 holdout/regression/A-B on triggers.
   - Current skill: has the 3 layers, but not the article's concrete assertion taxonomy or enough trigger detail.

3. **Five-dimensional AND gate is underspecified**
   - Current gate names the 5 dimensions, but does not define concrete pass/fail thresholds for each.
   - This weakens repeatability.

4. **Trace-driven diagnosis is good but not yet strict enough**
   - Current skill requires trace evidence.
   - The article also emphasizes counterfactual diagnosis and "no evidence, no mutation" discipline more forcefully.

5. **Human-in-loop checkpoints are weak**
   - The article's spirit is autonomous execution with human steering at meaningful checkpoints.
   - Current skill has rollback mechanics but almost no explicit operator confirmation points.

6. **Boundary / mis-trigger guidance is thin**
   - Missing explicit downgrade for requests that are only asking for evaluation, only packaging, or only dataset validation.

## Best next optimization targets
### Round 1 candidate
**Primary target: D4 Checkpoint design**
Why:
- Lowest score.
- High leverage with low blast radius.
- Can be fixed inside `SKILL.md` without changing the skill's purpose.

Proposed changes:
1. Add an explicit "Operator checkpoints" section.
2. Require a pause after baseline evaluation before optimization.
3. Require a pause before aggressive strategy / layer-3 escalation.
4. Add a downgrade path for eval-only / package-check-only / dataset-validate-only requests.

Expected score lift:
- D4: +3 to +5
- D3: +1 to +2
- D8: small positive lift from better operator discipline

## Evidence summary
- Target file read: `skill-evolver/SKILL.md:1`
- No prior Darwin report found under `docs/reports/`
- No prior `test-prompts.json` found; created `skill-evolver/test-prompts.json`
- Independent test runs completed for 3 prompts in baseline vs with-skill mode

## Recommended decision
Proceed to optimization round 1, targeting D4 first.
