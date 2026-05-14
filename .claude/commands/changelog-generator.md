---
description: 自动生成或更新项目的 CHANGELOG.md 文件。支持指定输出目录。
argument-hint: [output_dir]
allowed-tools:
  - Bash
  - Read
  - Write
  - AskUserQuestion
  - RunCommand
---

!python3 .claude/scripts/changelog_agent.py

You are a **Changelog Specialist**.

# Task
1.  **Analyze Arguments**: Check if an argument is provided. If it looks like a directory path, treat it as `output_dir`.
2.  **Visual Progress**: Start output with `[✔ Optimize] → [✔ Plan] → [✔ Execute] → [✔ Review] → [➤ Changelog] → [Commit]`
3.  **Analyze Diff**: Read the output from the script above (which shows the git diff).
4.  **Update Changelog**:
    -   Determine target file:
        -   If `output_dir` is provided: `output_dir/CHANGELOG.md`
        -   Otherwise: `CHANGELOG.md` (in current root)
    -   Read the target file (if it exists).
    -   Append or Insert the new changes under a strict "Unreleased" or current date section.
    -   Follow "Keep a Changelog" format.
    -   If file does not exist, create it.

# Workflow Handoff
**After the Changelog is successfully generated/updated:**

1.  **Reflective Handoff (Interactive Menu)**:
    -   **Mandatory**: You **MUST** use `AskUserQuestion` to present options (support bilingual).
    -   **Question**: `Changelog 已更新至 {target_file}。下一步？`
    -   **Options**:
        1.  **Generate Commit Message**
            -   **Label**: `Generate Commit Message (生成提交信息)`
            -   **Action**: Call `RunCommand(command="/commit-message-generator {output_dir}", requires_approval=False)`
        2.  **Review Changelog**
            -   **Label**: `Review Changelog (查看/编辑日志)`
            -   **Action**: Wait for user input.

2.  **Action (Interactive Navigation)**:
    -   **IMMEDIATELY** after the user selects an option, you **MUST** use `RunCommand` to execute the corresponding command.
    -   **Zero Friction**: You **MUST** set `requires_approval=False` for these follow-up commands to allow one-click execution.
    -   Example: If user selects "Generate Commit Message", you call `RunCommand(command="/commit-message-generator {output_dir}", requires_approval=False)`.

