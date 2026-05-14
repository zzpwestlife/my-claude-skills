# Token Optimization & Context Management Whitepaper

**Version**: 1.3 (2026-03-08)
**Status**: Implemented
**Impact**: Active Token Reduction ~85.0% (Enhanced with RTK)

## 1. Executive Summary
This document outlines the systematic approach used to optimize the `.claude/` configuration directory. By implementing a "Hot/Cold Data Separation" strategy combined with **Dynamic CLI Proxying (RTK)**, we reduced the active context load from ~79k tokens to ~15.6k tokens while maintaining 100% functional integrity through explicit referencing.

## 2. Core Philosophy: JIT (Just-In-Time) Context
The central principle is **"Load what you need, when you need it."**
- **Active Context (Hot)**: Information the Agent MUST know to function safely (Rules, Workflow Steps, Checklists).
- **Reference Context (Cold)**: Information the Agent CAN look up if needed (Tutorials, Examples, Anti-patterns, Deep Dives).

## 3. Architecture Changes

### 3.1 Unified Core Rules
We consolidated fragmented rule files (`workflow-protocol.md`, `coding-standards.md`, `operational-standards.md`) into a single, high-density file:
- **File**: `.claude/rules/CORE_RULES.md`
- **Optimization**: Removed polite fillers, redundant explanations, and "why" narratives. Kept only actionable directives.

### 3.2 Constitution Refactoring
- **Active**: `.claude/constitution/constitution.md` (Condensed to ~80 lines). Contains only the 14 Articles and their sub-clauses.
- **Reference**: `.claude/constitution/constitution_full.md` (Full text). Backup for detailed interpretation.

### 3.3 Skill Refactoring (The "Trigger-Only" Pattern)
We applied a standardized template to high-cost skills (`tdd`, `debugging`, `subagent`, `git`, `review`, `dispatch`):

| Section | Location | Content |
| :--- | :--- | :--- |
| **Frontmatter** | `SKILL.md` | `name`, `description` (Trigger conditions ONLY) |
| **Body** | `SKILL.md` | Core Iron Laws, Checklists, Process Steps |
| **Deep Dive** | `docs/references/` | Tutorials, Examples, Diagrams, Anti-patterns |

**Example (TDD)**:
- `SKILL.md`: "NO PRODUCTION CODE WITHOUT FAILING TEST", Red-Green-Refactor steps.
- `tdd_full.md`: Detailed rationale, "Why order matters", "Common Rationalizations".

### 3.4 Phase 2 Optimizations (Secondary Skills)
We extended JIT optimization to secondary skills:
- `receiving-code-review`
- `dispatching-parallel-agents`
- `brainstorming`
- `using-git-worktrees`
- `review-code` (Command)

### 3.5 Phase 3 Optimizations (Source Isolation)
We isolated executable source code from the active context:
- **Action**: Moved `.py` and `.sh` scripts to `.claude/scripts/`.
- **Impact**: Agent knows *how* to call scripts (via arguments) but doesn't waste tokens reading their implementation details unless debugging them.
- **Affected**: `architect.py`, `changelog_agent.py`, `check-complete.sh`, `statusline.sh`.

### 3.6 Phase 4 Optimizations (Agent Definitions)
We refined the Agent definitions themselves:
- **Files**: `code-reviewer.md`, `changelog-generator.md`.
- **Optimization**: Reduced to "Role", "Goal", and "Workflow" bullets. Detailed instructions moved to `docs/references/agents/`.

### 3.7 Phase 5 Optimizations (System Tools - MCP)
In Claude Code v2.1.69+, we leverage the **Tool Search / Defer Loading** mechanism to solve the "System Context Explosion" problem.

- **Problem**: Loading 50+ MCP tools at startup consumes ~10% of context (30k+ tokens) and degrades tool selection accuracy.
- **Solution**: Use `defer_loading: true` for non-critical tools.
- **Strategy**:
    - **Core Tools (Hot)**: Keep 3-5 high-frequency tools loaded (e.g., `bash`, `edit`).
    - **Extended Tools (Cold)**: Set `defer_loading: true` for all other tools (Search, Jira, GitHub, etc.).
- **Impact**: Reduces System Context from ~30k tokens to <1k tokens. Tools are discovered on-demand via Regex or BM25 search.

## 4. Safety Mechanisms (Integrity Verification)

To ensure no functionality is lost, we implemented:

1.  **Explicit Linking**: Every condensed file contains a footer link to its full version.
    > `> For detailed tutorial, see .claude/docs/references/skills/tdd_full.md`
2.  **Context Efficiency Directive**: Added to `AGENTS.md` to instruct the Agent on the JIT strategy.
    > `Read-on-Demand: Do NOT read full skill/doc files unless executing that specific task.`
3.  **Automated Monitoring**: `token-analyzer.py` script distinguishes between Active and Reference tokens.
4.  **Hook Verification**: Verified that critical hooks (e.g., `PostToolUse` for plan checking) point to the correct new paths in `scripts/`.

## 5. Token Analysis Tool

A custom Python script (`.claude/scripts/token-analyzer.py`) is provided to monitor context usage.

**Usage**:
```bash
python3 .claude/scripts/token-analyzer.py
```

**Output**:
- **ACTIVE CONTEXT**: Files loaded by default or high-frequency skills.
- **REFERENCE CONTEXT**: Files available for on-demand lookup.
- **SAVINGS**: Percentage of tokens moved from Active to Reference.

## 6. Maintenance Guidelines

When modifying or adding new skills/rules:

1.  **Check Size**: If a file exceeds 100 lines, ask "Is this all active rule?"
2.  **Split**: Move explanations/examples to `docs/references/`.
3.  **Link**: Add a link in the main file.
4.  **Verify**: Run the analyzer to ensure Active Context remains lean.

## 7. Dynamic Context Optimization (Tool Output Hygiene)

While the strategies above optimize **Static Context** (files loaded *before* interaction), **Dynamic Context** (output generated *during* interaction) is equally critical. A single command outputting a 5MB log file can instantly deplete the context window.

### 7.1 The "Context Explosion" Problem
We conducted a controlled experiment simulating a tool outputting 5,000 lines of logs:
- **Raw Output**: ~418 KB (~130,000 tokens) -> **CATASTROPHIC** (Fills >60% of context)
- **Summarized Output** (Errors only): ~209 KB -> **POOR**
- **Compressed Output** (Head/Tail): < 1 KB (~250 tokens) -> **OPTIMAL**

### 7.2 Solution: RTK (Rust Token Killer)
We have integrated **RTK** as a global CLI proxy to automatically compress command outputs before they reach the Agent's context.

**Installation & Config**:
- **Tool**: `rtk` (Installed via brew)
- **Hook**: `PreToolUse` hook in `~/.claude/settings.json` rewrites commands (e.g., `git status` -> `rtk git status`).

**Impact (Measured)**:
| Command | Raw Tokens | RTK Tokens | Savings |
| :--- | :--- | :--- | :--- |
| `git status` | ~331 | ~44 | **86.7%** |
| `ls -R` | ~195,000 | ~49,000 | **74.9%** |

**Strategy**:
- **Smart Filtering**: Removes noise (whitespace, comments).
- **Grouping**: Aggregates similar items (files by directory).
- **Truncation**: Keeps relevant context, cuts redundancy.
- **Deduplication**: Collapses repeated log lines.

### 7.3 Best Practices for Tool Output (Legacy/Manual)
Even with RTK, follow these principles for custom scripts:
1.  **Silence is Golden**: Scripts should output nothing on success, or a single confirmation line.
2.  **Filter First**: Never run `cat huge_file.log`. Use `grep "ERROR" huge_file.log` or `tail -n 20 huge_file.log`.
3.  **Search > Read**: For large codebases, use search tools (`grep`, `ripgrep`) to locate relevant sections before reading files.

### 7.4 Safety Mechanisms: Does Optimization Mean Information Loss?

A common concern is: *"If I filter the logs, will I miss the root cause?"*
The answer is **No**, provided you follow the **Iterative Retrieval** pattern:

1.  **Survey (Broad)**: Check `tail -n 20` or `grep "ERROR"`. This is cheap (low tokens) and identifies *if* and *where* a problem exists.
2.  **Pinpoint (Targeted)**: Once you have a timestamp or error ID, use `grep -C 5 "ErrorID"` to see the specific context around that error.
3.  **Expand (Deep)**: Only if the context is insufficient, read the full surrounding block (e.g., 100 lines).

**Comparison**:
- **Traditional (Dump)**: Read 5000 lines -> Brain overload / Context full -> Misses the needle in the haystack.
- **Optimized (Iterative)**: Read 20 lines -> Find target -> Read 50 lines -> **Solves problem with <2% token cost and higher accuracy.**

## 8. Conclusion
Optimization is not deletion; it is organization. By structuring information hierarchically (Static JIT) and managing tool output discipline (Dynamic Hygiene with RTK), we enable the Agent to "think fast" (low latency/cost) while retaining the ability to "think deep" (access to full knowledge) when required.
