# Automation & Meta-Skills Guide

This guide documents the **Meta-Skills** and **Automation Loops** integrated into the `learn-claude-code` suite. These tools are designed to make the AI assistant self-improving, self-healing, and self-navigating.

## 1. Philosophy: The Autonomous Loop

Traditional AI usage is linear: User -> Prompt -> Response.
Our goal is circular: **Action -> Log -> Audit -> Improvement**.

We introduce three core capabilities to achieve this:
1.  **Audit**: AI analyzes its own history to find gaps.
2.  **Recovery**: AI restores context after interruptions.
3.  **Discovery**: AI navigates its own toolset to find the right solution.

---

## 2. Skill Audit (`/audit-skills`)

**"Don't just use tools; build the tools you need."**

### Problem
As a project grows, users perform repetitive manual tasks that *could* be automated but aren't. Users often don't realize they need a new skill until they've done the task manually 10 times.

### Solution
The `/audit-skills` command allows Claude to analyze your recent conversation logs (or git history) to identify high-frequency manual operations.

### Usage
```bash
/audit-skills [optional: path/to/log]
```
If no path is provided, it automatically scans:
- `~/.claude/history.jsonl` (Global history)
- `.claude/tmp/session_summary.md` (Session summary)

### Output
A report listing "Missing Skills" with high ROI (Return on Investment), and a prompt to scaffold them immediately using `skill-creator`.

---

## 3. Session Recovery (`/recover`)

**"Never lose your flow state."**

### Problem
Context windows are finite. Terminals crash. Computers restart. Resuming a complex coding task often involves 15 minutes of "Where was I?" and "What was I doing?".

### Solution
We implemented a **Session Hook Loop**:
1.  **Save**: A `SessionEnd` hook triggers `.claude/hooks/session-summary.sh` whenever you exit Claude. It saves git status, recent commits, and modified files to `.claude/tmp/session_summary.md`.
2.  **Restore**: The `/recover` command invokes the `session-recovery` skill. It reads the summary + current git status to reconstruct your mental model.

### Optional: Exit Intercept for Knowledge Hygiene (neat-freak)

To prevent documentation + memory drift, we support an optional **Stop Hook intercept**:
- When you attempt to exit and **doc-related files** are dirty (`README.md`, `docs/`, `CLAUDE.md`, `AGENTS.md`, `HANDOFF.md`),
  the stop hook can **block exit** and present a TUI menu:
  - Run `neat-freak` now (recommended)
  - Skip and exit

This is best-effort:
- ✅ Covers normal `/exit` and many Ctrl+C stop paths
- ❌ Cannot guarantee coverage for hard kills (closing terminal, `kill -9`, shutdown)
- ✅ Provides a SessionStart fallback reminder if the doc changes still exist

### Usage
```bash
/recover
```
**Output**:
- **Last Activity**: "You were refactoring the login module."
- **Current State**: "3 files modified, tests failing."
- **Next Step**: "Run `pytest` to check failures."

---

## 4. Skill Discovery (`/find-skills`)

**"The best tool is the one you can find."**

### Problem
As the number of skills grows (30+), users forget what's available. "Is there a tool for video?" "Do we have a linter?"

### Solution
The `/find-skills` command uses a keyword-based search (upgradeable to semantic search) to find relevant skills. If no skill is found, it **proposes creating one**.

### Usage
```bash
/find-skills <query>
```
**Example**:
```bash
/find-skills "video cutting"
```
**Result**:
- ✅ Found: `video-semantic-cutter` (Score: 15)
- ❌ Or: "No skill found. Shall we create one?"

---

## 5. The "Meta" Workflow

Combine these tools for a self-evolving environment:

1.  **Start of Day**: Run `/recover` to load context.
2.  **During Work**: Forget a command? Run `/find-skills "how to deploy"`.
3.  **End of Week**: Run `/audit-skills` to see what new automations you should build.
