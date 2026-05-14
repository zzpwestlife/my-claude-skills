#!/bin/bash
# Claude Code Hook: Auto Format Go Code
# ======================================
# This hook runs as a PostToolUse hook for Edit, Write, and MultiEdit tools.
# It automatically formats .go files using gofmt, goimports and gofumpt.

# Read JSON input from stdin
INPUT_JSON=$(cat)

# Extract file path using grep/sed (to avoid jq dependency if possible, but jq is safer)
# Assuming tool_input.file_path structure.
# Using python for reliable JSON parsing since jq might not be available
FILE_PATH=$(echo "$INPUT_JSON" | python3 -c "import sys, json; print(json.load(sys.stdin).get('tool_input', {}).get('file_path', ''))")

# Check if file path is empty
if [ -z "$FILE_PATH" ]; then
    exit 0
fi

# Check if file extension is .go
if [[ "$FILE_PATH" != *.go ]]; then
    exit 0
fi

# Check if file exists
if [ ! -f "$FILE_PATH" ]; then
    exit 0
fi

# Apply formatting
# We use 'command -v' to check if tools exist before running them to avoid errors

# 1. gofmt (Standard)
if command -v gofmt >/dev/null 2>&1; then
    gofmt -w "$FILE_PATH"
fi

# 2. goimports (Imports management)
if command -v goimports >/dev/null 2>&1; then
    goimports -w "$FILE_PATH"
fi

# 3. gofumpt (Stricter formatting, as per go_annex.md)
if command -v gofumpt >/dev/null 2>&1; then
    gofumpt -w "$FILE_PATH"
fi

exit 0
