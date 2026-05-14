# CORE RULES & PROTOCOLS (Unified V1.0)

## 1. Engineering Principles (Simplicity & Quality)
- **Simplicity First (YAGNI)**: Implement ONLY requested features; NO speculative abstractions. No abstractions for single-use code. No unrequested "flexibility" or "configurability." If 200 lines can become 50, rewrite.
- **Think Before Coding**: Explicitly state assumptions — unsure means ask, not guess. When ambiguous, present multiple interpretations. When a simpler solution exists, push back. When confused, STOP and call it out.
- **Atomic Execution**: Perform ONE task phase per turn. Stop and handoff after completion.
- **Evidence-Based**: Use logs, tests, and diffs for verification. NO "Happy Path" assumptions.
- **Zero-Friction**: Prefer TUI menus (`AskUserQuestion` with `options`) over open-ended text.
- **Root Cause Fixing**: Resolve the source of issues, not just symptoms. Zero hand-holding.
- **Plan-First**: Mandatory plan in `docs/plans/` for tasks >3 steps. STOP on deviation.
- **Goal-Driven Execution**: State goals, not instructions. "Write a test for invalid input, then make it pass" > "Add validation." For multi-step tasks: `[step] → verify: [check]`.
- **BDD & State Tracking**: For complex tasks, adopt the Red-Green Agent BDD loop. Maintain a `.local.md` state file tracking task dependencies and status. Read `.claude/docs/guides/agent_bdd_loop.md` for details.

## 2. Coding Standards
- **Surgical Changes**: Touch ONLY necessary files. Do NOT "improve" adjacent code, comments, or formatting. Match existing style even if you'd write it differently. Flag dead code — don't delete it. Only remove imports/vars/functions made obsolete by YOUR changes. Every changed line must trace back to the user's request.
- **Strict Typing**: NO `any` type or `eslint-disable`. Use explicit types.
- **Clean Code**: Delete unused code immediately; NO commented-out obsolete code.
- **File Limits**: Single file < 200 lines; functions < 20 lines. Hard wrap at 100 chars.
- **Metadata**: Source files MUST start with 3 header lines: INPUT, OUTPUT, POS.
- **Self-Documenting**: Naming explains "What"; comments explain "Why".

## 3. Workflow Protocol (Handoff & TUI)
- **Universal Handoff**: After EVERY phase (Plan, Exec, Review), display a TUI menu via `AskUserQuestion`.
- **Zero Friction Navigation**: Use `Bash` with pre-approved commands for standard next-steps.
- **Mandatory Pauses**: Respond to "🛑 STOP EXECUTION NOW 🛑" signals immediately.
- **Bilingual Options**: Provide bilingual (EN/CN) labels in `AskUserQuestion` options.
- **Mode Selection**: Diff Mode for incremental changes; Full Path for deep refactoring.

## 4. Operational & Git
- **Conventional Commits**: `type(scope): subject`.
- **Explicit Staging**: NO `git add .`; stage files explicitly after `git status`.
- **SubAgent Strategy**: Delegate exploration, research, and parallel tasks to subagents.
- **Concise Comms**: Redirect long logs to `.claude/tmp/logs.md`. No polite fillers.
- **Cross-Platform**: Support both macOS (BSD) and Linux (GNU) in all scripts.

## 5. Dynamic Context Hygiene (Token Optimization)
- **Silence is Golden**: Scripts MUST output nothing on success (or single line confirmation).
- **Filter First**: NEVER `cat` large files (>100 lines). Use `grep`, `head`, `tail` to extract relevant sections.
- **Search > Read**: Prefer `SearchCodebase` or `grep` over `Read` for exploration.
- **Iterative Retrieval**: Start with a summary/search; ONLY read full content if specific details are needed.
- **Truncation Awareness**: If output is truncated, explicitly state "Output truncated, use filter to see more."

## 6. Context Isolation (AI Flow State)
- **Project-Level Only**: DO NOT use user-level (`~/.claude/`) configuration for project-specific rules or tools.
- **Dependency Isolation**: All MCP servers and Skills MUST be defined within the repository (`.claude/`), ensuring reproducibility.
- **Minimal Global Context**: Keep the global context empty or restricted to OS-level utilities only.

## 7. Documentation & Copywriting (Chinese Guidelines)
- **Strict Adherence**: All Chinese documentation MUST follow `docs/zh-copywriting-guidelines.md`.
- **Spaces**: Always add spaces between Chinese and English/Numbers (e.g., "使用 GitHub 登录").
- **Punctuation**: Use full-width punctuation for Chinese sentences (e.g., "，" not ",").
- **No Repetition**: Do not repeat punctuation marks (e.g., "！！").

## 8. Agent Behavioral Constraints
- **Explicit Tool Execution**: If the user asks to use a specific tool or script (e.g., `./search.sh`), USE IT IMMEDIATELY. Do not explore the codebase on your own first.
- **Browser & Screenshot Tasks**: Use the Playwright MCP server or `screencapture` (macOS). NEVER restart Chrome or close existing tabs. If DevTools fails, suggest launching Chrome with `--remote-debugging-port=9222`.
- **Codebase Exploration Limits**: Set a strict limit (2-3 tool calls) when exploring. Summarize findings and ask for direction rather than exploring silently to avoid excessive delays.
- **Task Verification**: Before claiming a task is complete, verify ALL items have been addressed. Double-check lists and task counts. Never claim completion without explicit verification.
