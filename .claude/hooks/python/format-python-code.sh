#!/bin/bash
# Claude Code Hook: Auto Format Python Code
# ==========================================
# PostToolUse hook for Edit, Write, and MultiEdit tools.
# Formats .py files using ruff (preferred) or black + isort.

INPUT_JSON=$(cat)

FILE_PATH=$(echo "$INPUT_JSON" | python3 -c "import sys, json; print(json.load(sys.stdin).get('tool_input', {}).get('file_path', ''))" 2>/dev/null)

if [ -z "$FILE_PATH" ] || [[ "$FILE_PATH" != *.py ]] || [ ! -f "$FILE_PATH" ]; then
    exit 0
fi

if command -v ruff >/dev/null 2>&1; then
    ruff format "$FILE_PATH"
    ruff check --fix --silent "$FILE_PATH"
elif command -v black >/dev/null 2>&1; then
    black --quiet "$FILE_PATH"
    if command -v isort >/dev/null 2>&1; then
        isort --quiet "$FILE_PATH"
    fi
fi

exit 0
