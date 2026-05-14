# Claude Code Configuration Entry Point

<!--
Purpose: This file serves as a compatibility layer for Claude Code.
Usage: It redirects the AI to the primary configuration file, `AGENTS.md`.
-->

**【强制要求】** 在回复用户任何消息之前，必须先使用 Read 工具读取项目配置目录下的 `.claude/AGENTS.md` 文件，并严格遵守其中的所有指令。未读取 `.claude/AGENTS.md` 之前，禁止回复用户。

- 如果需要写入 `CLAUDE.md`，请将内容写入 `.claude/AGENTS.md`。

# --- Configuration Import (Highest Priority) ---
@.claude/AGENTS.md Non-Negotiable

# --- Profile Specifics ---

# Go Profile Configuration

<!--
Purpose: Go-specific overrides for this project.
Note: Core configuration is loaded via CLAUDE.md → AGENTS.md
-->

# Go-Specific Guidelines

## Testing
- Use table-driven tests
- Test files should be in the same package with `_test.go` suffix

## Code Style
- Use `gofumpt` for formatting
- Use `goimports` for import management
- No `else` after return in early-return pattern
