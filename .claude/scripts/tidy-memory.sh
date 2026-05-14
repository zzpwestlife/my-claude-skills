#!/bin/bash

# Tidy Memory Script
# Summarizes project lessons and cleans up redundant Core Memories.

LESSONS_FILE=".claude/lessons.md"
MEMORY_FILE="$HOME/.claude/memory/MEMORY.md"

echo "🧹 Tidying Memory..."

# 1. Summarize Lessons
if [ -f "$LESSONS_FILE" ]; then
    echo "  - Analyzing $LESSONS_FILE for patterns..."
    # (Placeholder: In a real agent workflow, this would call an LLM to summarize)
    # For now, we just deduplicate lines
    sort -u "$LESSONS_FILE" -o "$LESSONS_FILE.tmp" && mv "$LESSONS_FILE.tmp" "$LESSONS_FILE"
    echo "  - Deduplicated lessons."
else
    echo "  - No lessons file found to tidy."
fi

# 2. Report Core Memory Status
echo "  - Core Memory Status:"
# (Placeholder: This would invoke manage_core_memory tool if possible, but scripts can't call tools directly)
echo "    Please ask me: 'Review and consolidate my core memories'"

echo "✅ Memory Tidy Complete."
