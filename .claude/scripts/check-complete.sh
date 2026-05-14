#!/bin/bash
# Check if all tasks in the latest plan file are complete
# Supports both "Phase" (legacy) and "Task" (new) formats
# Tracks state in .claude/tmp/phase_state to detect transitions

PLAN_DIR="docs/plans"
STATUS_FILE=".claude/tmp/planning_status.md"
AUDIT_LOG=".claude/audit/planning.log"

# Ensure dirs exist
mkdir -p "$(dirname "$AUDIT_LOG")"
mkdir -p "$(dirname "$STATUS_FILE")"

# Find latest plan
PLAN_FILE=""
if [ -d "$PLAN_DIR" ]; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        PLAN_FILE=$(find "$PLAN_DIR" -name "*.md" -type f -exec stat -f "%m %N" {} + | sort -rn | head -n 1 | cut -d ' ' -f 2-)
    else
        PLAN_FILE=$(find "$PLAN_DIR" -name "*.md" -type f -exec stat -c "%Y %n" {} + | sort -rn | head -n 1 | cut -d ' ' -f 2-)
    fi
fi

if [ -z "$PLAN_FILE" ]; then
    # No plan found
    exit 0
fi

# Generate unique state file
PLAN_ABS_PATH=$(cd "$(dirname "$PLAN_FILE")" && pwd)/$(basename "$PLAN_FILE")
PLAN_HASH=$(echo "$PLAN_ABS_PATH" | md5sum 2>/dev/null | awk '{print $1}')
if [ -z "$PLAN_HASH" ]; then
    PLAN_HASH=$(echo "$PLAN_ABS_PATH" | md5 -q 2>/dev/null)
fi
if [ -z "$PLAN_HASH" ]; then
    PLAN_HASH="default"
fi
STATE_FILE=".claude/tmp/phase_state_${PLAN_HASH}"
mkdir -p "$(dirname "$STATE_FILE")"

# --- ANALYSIS ---

# Count total checkable items (- [ ])
TOTAL_ITEMS=$(grep -c "\- \[.\]" "$PLAN_FILE" || true)

# Count completed items (- [x])
COMPLETED_ITEMS=$(grep -c "\- \[x\]" "$PLAN_FILE" || true)

# Count incomplete items (- [ ])
INCOMPLETE_ITEMS=$(grep -c "\- \[ \]" "$PLAN_FILE" || true)

# --- STATUS FILE GENERATION ---
{
    echo "# Planning Status"
    echo "Time: $(date)"
    echo "Plan: $(basename "$PLAN_FILE")"
    echo "- Total Items: $TOTAL_ITEMS"
    echo "- Completed: $COMPLETED_ITEMS"
    echo "- Remaining: $INCOMPLETE_ITEMS"
    echo ""
    echo "## Recent Activity"
    tail -n 5 "$AUDIT_LOG" 2>/dev/null || echo "No recent activity."
} > "$STATUS_FILE"

# --- STATE TRACKING ---
PREV_COMPLETED=0
if [ -f "$STATE_FILE" ]; then
    PREV_COMPLETED=$(cat "$STATE_FILE")
    if ! [[ "$PREV_COMPLETED" =~ ^[0-9]+$ ]]; then
        PREV_COMPLETED=0
    fi
fi

# Update state
echo "$COMPLETED_ITEMS" > "$STATE_FILE"

# --- EVENT DETECTION ---
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# Detect Completion
if [ "$TOTAL_ITEMS" -gt 0 ] && [ "$INCOMPLETE_ITEMS" -eq 0 ]; then
    echo "ALL TASKS COMPLETE"
    if [ "$PREV_COMPLETED" -lt "$TOTAL_ITEMS" ]; then
        echo "$TIMESTAMP: All tasks completed ($COMPLETED_ITEMS/$TOTAL_ITEMS) in $(basename "$PLAN_FILE")" >> "$AUDIT_LOG"
    fi
elif [ "$COMPLETED_ITEMS" -gt "$PREV_COMPLETED" ]; then
    echo "TASK PROGRESS: $COMPLETED_ITEMS/$TOTAL_ITEMS"
    echo "$TIMESTAMP: Progress update ($COMPLETED_ITEMS/$TOTAL_ITEMS) in $(basename "$PLAN_FILE")" >> "$AUDIT_LOG"
fi
