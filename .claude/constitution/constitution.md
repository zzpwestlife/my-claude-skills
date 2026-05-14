# Project Constitution (Condensed)

## 1. Simplicity (Core)
- **1.1 YAGNI**: Only implement requested features.
- **1.2 Minimal Deps**: Standard lib > external deps.
- **1.3 No Over-Engineering**: Simple > Abstract.
- **1.4 Root Causes**: No temp fixes; solve the constraint.
- **1.5 First Principles**: Break down to truth, not analogy.

## 2. Testing (Non-Negotiable)
- **2.1 Strategy**: Complex logic = Test-First.
- **2.2 Coverage**: Happy path + Error paths + Edge cases.
- **2.3 Design**: Dependency Injection for testability.

## 3. Clarity
- **3.1 Errors**: Handle explicitly; NO silent failures.
- **3.2 Deps**: Explicitly passed; NO global state.
- **3.3 Naming**: Self-documenting; comments explain "Why".

## 4. Architecture (SOLID)
- **4.1 Isolation**: Core logic decoupled from I/O (Library First).
- **4.2 SRP**: One module/function = One responsibility.
- **4.3 ISP**: Small, focused interfaces.
- **4.4 DIP**: Depend on abstractions.

## 5. Structure
- **5.1 Minimal Changes**: Touch only necessary files.
- **5.2 File Size**: < 200 lines.
- **5.3 Func Size**: < 20 lines.
- **5.4 Line Width**: < 100 chars.
- **5.5 Evolution**: Delete old code; NO commented-out blocks.
- **5.6 Metadata**: Header lines: INPUT, OUTPUT, POS.

## 6. Typography
- **6.1 Spacing**: Space between CJK and ASCII/Numbers.
- **6.2 Punctuation**: Full-width (CN) vs Half-width (EN).
- **6.3 Case**: Correct proper nouns (GitHub, iPhone).

## 7. Improvement
- **7.1 Loop**: Mistake -> Rule -> `.claude/lessons.md`.
- **7.2 Pre-load**: Read lessons at session start.
- **7.3 Iteration**: Iterate until mistake rate drops.

## 8. Planning (Non-Negotiable)
- **8.1 Mandatory**: Tasks > 3 steps MUST have plan in `docs/plans/`.
- **8.2 Deviation**: STOP on plan deviation; re-plan.
- **8.3 Check**: Verify plan against Constitution.

## 9. Evidence
- **9.1 Logs**: Debug via logs/errors, not guesses.
- **9.2 Reproduction**: Reproduce before fixing.
- **9.3 Verification**: Tests/scripts required for fix.

## 10. Zero-Friction (TUI)
- **10.1 Preference**: Use Arrow Keys + Enter (TUI).
- **10.2 Defaults**: Provide sensible defaults.
- **10.3 Options**: Use `AskUserQuestion(options=[...])`.

## 11. Delivery
- **11.1 Complete**: Production-ready; NO TODOs.
- **11.2 Hygiene**: Clean temp files.
- **11.3 Security**: No PII/Secrets in logs/tests.
- **11.4 Validation**: "Would a staff engineer approve?"

## 12. Security
- **12.1 Least Privilege**: Min permissions.
- **12.2 Input**: Validate/Sanitize all boundaries.
- **12.3 Privacy**: Protect PII.
- **12.4 Deps**: Audit vulnerabilities.

## 13. Workflow Control
- **13.1 Atomic**: One step per turn.
- **13.2 Handoff**: STOP and ask user after each phase.
- **13.3 Navigation**: Bilingual TUI menus.

## 14. Cognitive
- **14.1 Occam's Razor**: Minimize entities.
- **14.2 Feynman**: Explain simply.
- **14.3 Socratic**: Question assumptions.

## 15. Karpathy Coding Discipline
- **15.1 Think Before Coding**: Explicitly state assumptions. If unsure, ask — never guess. When ambiguous, present multiple interpretations. When a simpler solution exists, push back. When confused, STOP and call it out.
- **15.2 Simplicity First (Karpathy)**: No abstractions for single-use code. No unrequested "flexibility" or "configurability." No error handling for impossible scenarios. If 200 lines can become 50, rewrite. **Test**: Would a senior engineer call this over-engineered? If yes, simplify.
- **15.3 Surgical Changes (Karpathy)**: Do NOT "improve" adjacent code, comments, or formatting. Do NOT refactor what isn't broken. Match existing style even if you'd write it differently. Flag dead code — don't delete it. Only remove imports/vars/functions made obsolete by YOUR changes. **Test**: Every changed line must trace back to the user's request.
- **15.4 Goal-Driven Execution**: State goals, not instructions. "Write a test for invalid input, then make it pass" > "Add validation." For multi-step tasks, state a brief plan with verification per step: `[step] → verify: [check]`.
