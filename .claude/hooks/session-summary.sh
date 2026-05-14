#!/bin/bash

# Session End Hook: Scan for Tweet Material
# Usage: This script runs automatically when the Claude Code session ends.

LOG_FILE=".claude/tmp/session_summary.md"
DATE=$(date +"%Y-%m-%d %H:%M:%S")

echo "# Session Summary - $DATE" > "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 1. Check Git Activity (Commits since session start - simplified to 'last 1 hour' or just recent)
echo "## Recent Git Activity" >> "$LOG_FILE"
if git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    git log --since="1 hour ago" --oneline --no-merges >> "$LOG_FILE"
else
    echo "No git repository found." >> "$LOG_FILE"
fi

echo "" >> "$LOG_FILE"

# 2. Check Modified Files
echo "## Modified Files" >> "$LOG_FILE"
git status --short >> "$LOG_FILE"

echo "" >> "$LOG_FILE"

# 3. Suggest Tweet (Simple Heuristic)
echo "## Tweet Suggestions" >> "$LOG_FILE"
COMMIT_COUNT=$(git log --since="1 hour ago" --oneline | wc -l)
if [ "$COMMIT_COUNT" -gt 0 ]; then
    echo "- 🚀 Just shipped $COMMIT_COUNT updates in #ClaudeCode!" >> "$LOG_FILE"
    echo "- 💡 Learned a lot about $(git log --since="1 hour ago" --oneline | head -n 1 | cut -d' ' -f2-) today." >> "$LOG_FILE"
else
    echo "- 🤔 Spent some time planning and exploring code." >> "$LOG_FILE"
fi

echo "Session summary saved to $LOG_FILE"
