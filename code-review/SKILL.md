---
name: code-review
description: Review existing code and provide actionable feedback on correctness, readability, security, performance, and maintainability
---

# Code Review Skill

## Trigger
Use this skill when the user provides existing code and asks for review, quality check, bug risk analysis, or improvement suggestions.

Do not trigger for pure code generation, architecture brainstorming without concrete code, or documentation-only edits.

## Review Flow
1. Identify language, scope, and user constraints.
2. Scan for correctness and edge-case risks.
3. Evaluate readability, naming, structure, and error handling.
4. Check security and performance hotspots.
5. Prioritize findings by impact.

## Output Requirements
Return structured markdown with these sections:
- Summary: 2-3 sentences on overall quality and top risks.
- Strengths: 2-4 concrete positives.
- Improvements: each item must include Issue, Location, Problem, Suggestion.
- Priority: mark each item as Critical, Important, or Minor.
- Educational Note: one practical best-practice tip tied to the dominant issue pattern.

## Quality Bar
- Keep feedback specific and evidence-based.
- Prefer minimal, safe changes over broad rewrites.
- Respect explicit constraints from the user.
- Avoid vague statements without actionable guidance.
- Keep typical response length around 300-600 words unless the code scope is very small or very large.
