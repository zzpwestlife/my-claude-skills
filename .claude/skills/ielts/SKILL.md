---
name: ielts
description: |
  Active IELTS feeder: ingest transcripts/manual rules/vocab and write the shared knowledge base for english-immersion to use.
  Hard gate: pull-only (runs once per `/ielts ...`), never does passive correction or proactive reminders.
  Output contract: updates `data/state.md` (anchor) or appends to `data/methodology.md` / `data/ielts_vocab.md`.
version: "1.0.0"
---

# IELTS Skill — Active Feeder

This skill only handles **active feeding** (user-initiated). Passive absorption and daily correction are handled by `english-immersion`.

## Reusable Interface (R) — Feeder Contract

When invoked, it must produce concrete, reusable artifacts:

- Update **exactly one** of:
  - `data/state.md` (`sliding_anchor` section)
  - `data/methodology.md` (append rules)
  - `data/ielts_vocab.md` (append collocations)
- Print a short confirmation:
  - File written
  - What was added/updated (count)

## Anti-Anchoring（反锚定，MANDATORY）

- Prefer a small set of **atomic, detectable, executable** rules (L1) over comprehensive vague advice.
- Examples are format demos, not content to blindly copy.
- If required files are missing: STOP and ask for the correct working directory / file paths.

## Sub-commands (entry points)

- `/ielts anchor` — set sliding anchor (exam date / current / target)
- `/ielts feed <transcript>` — extract rules from a transcript, show for user approval, then append to `methodology.md`
- `/ielts rule <rule text>` — manually add one rule to `methodology.md`
- `/ielts vocab <word list>` — append collocations to `ielts_vocab.md` (dedupe)
- `/ielts status` — one-screen progress summary (user-initiated only)

## Shared Data Contract (with english-immersion)

| File | Owner (writes) | Reader |
|---|---|---|
| `data/state.md` (`sliding_anchor`) | ielts | english-immersion |
| `data/methodology.md` | ielts | english-immersion |
| `data/ielts_vocab.md` | ielts + user | english-immersion |
| `data/absorption_log.md` | english-immersion | weekly report |

