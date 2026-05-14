---
name: verification-before-completion
description: |
  Invoke when you are about to make ANY success/completion claim (tests pass, bug fixed, build succeeds),
  especially before committing/pushing/PR.

  Requirement: include an Evidence Block (Claim / Command / Exit code / Evidence).
  If you cannot run a real verification command in this environment: STOP and state the limitation.
version: "1.0.0"
---

# Verification Before Completion

## Overview

Claiming work is complete without verification is dishonesty, not efficiency.

**Core principle:** Evidence before claims, always.

**Violating the letter of this rule is violating the spirit of this rule.**

## Reusable Interface (R) — Output Contract

This skill is designed to be *callable* by other skills (e.g. `executing-plans`, `test-driven-development`, CI/Makefile flows).

**Artifacts that must exist for any completion claim:**
- Verification command (exact)
- Exit code (numeric)
- 1–3 lines of output that prove pass/fail
- (If code changed) brief change evidence: `git diff --stat` or equivalent summary

### Evidence Template (MANDATORY)

When making a success claim, include this minimal evidence block:

```
Claim: <what you are asserting>
Command: <exact command you ran>
Exit code: <numeric>
Evidence: <1-3 lines from output showing pass/fail counts or key success signal>
```

### Limitation Template (MANDATORY when you cannot run the command)

```
Limitation: I cannot run <command> here because <reason>.
Need from you: <repo access / exact command / CI log / install approval>.
Best available evidence now: <CI link/log excerpt OR repro steps/log excerpt OR diff-based hypothesis>.
```

## Anti-Anchoring (MANDATORY)

- **Do not** paraphrase or fabricate command output.
- Example outputs are formatting demos, not evidence.
- If the verification command cannot be executed, you **must not** claim success.

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

If you haven't run the verification command in this message, you cannot claim it passes.

## The Gate Function

```
BEFORE claiming any status or expressing satisfaction:

1. IDENTIFY: What command proves this claim?
2. RUN: Execute the FULL command (fresh, complete)
3. READ: Full output, check exit code, count failures
4. VERIFY: Does output confirm the claim?
   - If NO: State actual status with evidence
   - If YES: State claim WITH evidence
5. ONLY THEN: Make the claim

Skip any step = lying, not verifying
```

### No-Command / No-Environment Rule (MANDATORY)

If you cannot run the verification command (missing repo, missing dependencies, CI-only, no access):

1. **STOP** — do not claim success.
2. State the limitation explicitly ("I cannot run `<command>` here because ...").
3. Ask for what you need (repo access, command, CI link/log, dependency install approval).
4. Provide the *best available alternative evidence* (in descending order):
   - CI run link/log + exit status
   - Reproduction steps + screenshot/log excerpt
   - Minimal diff-based reasoning (only as a hypothesis, not a pass claim)

## Common Failures

| Claim | Requires | Not Sufficient |
|-------|----------|----------------|
| Tests pass | Test command output: 0 failures | Previous run, "should pass" |
| Linter clean | Linter output: 0 errors | Partial check, extrapolation |
| Build succeeds | Build command: exit 0 | Linter passing, logs look good |
| Bug fixed | Test original symptom: passes | Code changed, assumed fixed |
| Regression test works | Red-green cycle verified | Test passes once |
| Agent completed | VCS diff shows changes | Agent reports "success" |
| Requirements met | Line-by-line checklist | Tests passing |

## Red Flags - STOP

- Using "should", "probably", "seems to"
- Expressing satisfaction before verification ("Great!", "Perfect!", "Done!", etc.)
- About to commit/push/PR without verification
- Trusting agent success reports
- Relying on partial verification
- Thinking "just this once"
- Tired and wanting work over
- **ANY wording implying success without having run verification**

## Rationalization Prevention

| Excuse | Reality |
|--------|---------|
| "Should work now" | RUN the verification |
| "I'm confident" | Confidence ≠ evidence |
| "Just this once" | No exceptions |
| "Linter passed" | Linter ≠ compiler |
| "Agent said success" | Verify independently |
| "I'm tired" | Exhaustion ≠ excuse |
| "Partial check is enough" | Partial proves nothing |
| "Different words so rule doesn't apply" | Spirit over letter |

## Key Patterns

**Tests:**
```
✅ [Run test command] [See: 34/34 pass] "All tests pass"
❌ "Should pass now" / "Looks correct"
```

**Regression tests (TDD Red-Green):**
```
✅ Write → Run (pass) → Revert fix → Run (MUST FAIL) → Restore → Run (pass)
❌ "I've written a regression test" (without red-green verification)
```

**Build:**
```
✅ [Run build] [See: exit 0] "Build passes"
❌ "Linter passed" (linter doesn't check compilation)
```

**Requirements:**
```
✅ Re-read plan → Create checklist → Verify each → Report gaps or completion
❌ "Tests pass, phase complete"
```

**Agent delegation:**
```
✅ Agent reports success → Check VCS diff → Verify changes → Report actual state
❌ Trust agent report
```

## Why This Matters

From 24 failure memories:
- your human partner said "I don't believe you" - trust broken
- Undefined functions shipped - would crash
- Missing requirements shipped - incomplete features
- Time wasted on false completion → redirect → rework
- Violates: "Honesty is a core value. If you lie, you'll be replaced."

## When To Apply

**ALWAYS before:**
- ANY variation of success/completion claims
- ANY expression of satisfaction
- ANY positive statement about work state
- Committing, PR creation, task completion
- Moving to next task
- Delegating to agents

**Rule applies to:**
- Exact phrases
- Paraphrases and synonyms
- Implications of success
- ANY communication suggesting completion/correctness

## The Bottom Line

**No shortcuts for verification.**

Run the command. Read the output. THEN claim the result.

This is non-negotiable.
