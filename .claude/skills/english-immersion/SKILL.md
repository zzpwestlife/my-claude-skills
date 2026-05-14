---
name: english-immersion
description: |
  Passive English immersion + IELTS prep built into daily sessions (English Mode ON/OFF).
  Hard gate: never interrupt the user for grammar; log silently and batch-review at session end.
  Output contract: obey the file contract below; if evidence (logs) is missing/unreadable, STOP and use fallback behavior.
version: "1.0.0"
---

# English Immersion Skill

Daily-driver English immersion + IELTS prep, built into the conversation loop.

## Reusable Interface (R) — File Contract

This skill is designed to be composable with `ielts` (active feeder) and other workflows.

### Authoritative state
- `state.md` — stores `mode: on|off`

### Append-only logs
- `inputs_log.md`
- `errors_tagged.md` (with `<!-- reviewed: ... -->` marker)
- `words_learned.md`

### Weekly output
- `weekly_reports/YYYY-WNN.md`

### IELTS hook inputs (written by ielts, read by this skill)
- `methodology.md`
- `ielts_vocab.md`

**Fallback rule (MANDATORY):** if the primary data directory is unavailable (iCloud/permissions), fall back to `.claude/english-immersion/tmp/` for this session and warn once.

## Anti-Anchoring（反锚定，MANDATORY）

- Do not “over-correct” inline: grammar corrections are logged, not injected into the reply unless explicitly requested.
- Do not fabricate log content. Missing/unreadable files must be stated explicitly, then follow fallback behavior.
- IELTS examples/collocations are guidance; prefer the user’s *real inputs* and the *actual logs* as the source of truth.

---

## Mode: ON / OFF

### Switching ON (any trigger)
- "english mode on" / "english on" / "switch to english"
- "学英语" / "练英语"
- Any `/ielts-*` sub-command (auto-ON for the session)

### Switching OFF (any trigger)
- "english mode off" / "english off" / "中文" / "切中文"
- Any skill that produces native-language content (don’t interfere)

## ON-mode behavior (core loop)

1) **Reply in English** by default (technical terms/identifiers unchanged).
2) **Log user inputs** (English or mixed) to `inputs_log.md`.
3) **Log errors silently** to `errors_tagged.md` (never nag inline unless user asks).
4) **Unknown word teaching**: use `reference/wittgenstein-style.md`; then append a short “word card” to `words_learned.md`.

## Session-end batch review (pull-only / no nagging)

### Triggers
- Explicit: "/done" / "english review" / "复盘英语"
- Farewell with no follow-up task

### Boundary conditions
- If English turns < 3 → skip review
- If no errors logged → skip review
- Never show more than 7 errors; group by pattern

### Output format (in chat)
```
English Review — {{timestamp}} — {{N}} errors across {{M}} patterns
1. "{{original}}" → "{{corrected}}"
   Pattern: {{pattern-label}}
   {{short explanation}}
```

## References

- `reference/wittgenstein-style.md`
- `reference/error-pattern-taxonomy.md`
- `reference/ielts-rubrics.md`
- `sub-skills/` (active IELTS practice commands)
