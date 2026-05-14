#!/bin/bash
# Smart Skill Architect Activator
# Automatically detects task completion context and prompts for skill evolution.
#
# Context-Aware Logic:
# 1. Checks if CHANGELOG.md was modified recently (indicating task completion).
# 2. Checks if the latest plan in docs/plans/ is completed and modified recently.
# 3. Checks if review_report.md was generated recently.
# 4. Logs decisions to .claude/logs/activator.log.

LOG_FILE=".claude/logs/activator.log"
mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Threshold in seconds (5 minutes)
THRESHOLD=300
SHOULD_RUN=false
REASON=""

# Function to get file modification time age in seconds
get_file_age() {
    local file="$1"
    local age
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        local mod_time=$(stat -f %m "$file")
        local now=$(date +%s)
        age=$((now - mod_time))
    else
        # Linux
        local mod_time=$(stat -c %Y "$file")
        local now=$(date +%s)
        age=$((now - mod_time))
    fi
    echo "$age"
}

# Check CHANGELOG.md
if [ -f "CHANGELOG.md" ]; then
    AGE=$(get_file_age "CHANGELOG.md")
    if [ "$AGE" -lt "$THRESHOLD" ]; then
        SHOULD_RUN=true
        REASON="CHANGELOG.md modified ${AGE}s ago"
    fi
fi

# Check latest plan in docs/plans/ (only if not already running)
if [ "$SHOULD_RUN" = "false" ] && [ -d "docs/plans" ]; then
    # Find the most recently modified .md file in docs/plans/
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS: stat -f "%m %N" | sort -rn | head -1
        LATEST_PLAN=$(find docs/plans -name "*.md" -type f -exec stat -f "%m %N" {} + | sort -rn | head -n 1 | cut -d ' ' -f 2-)
    else
        # Linux: stat -c "%Y %n" | sort -rn | head -1
        LATEST_PLAN=$(find docs/plans -name "*.md" -type f -exec stat -c "%Y %n" {} + | sort -rn | head -n 1 | cut -d ' ' -f 2-)
    fi

    if [ -n "$LATEST_PLAN" ]; then
        # Check if all tasks are checked (no empty [ ])
        if ! grep -q "\- \[ \]" "$LATEST_PLAN"; then
            AGE=$(get_file_age "$LATEST_PLAN")
            if [ "$AGE" -lt "$THRESHOLD" ]; then
                SHOULD_RUN=true
                REASON="Plan $(basename "$LATEST_PLAN") completed & modified ${AGE}s ago"
            fi
        fi
    fi
fi

# Check CODE_REVIEW.md (or legacy review_report.md)
if [ "$SHOULD_RUN" = "false" ]; then
    if [ -f "CODE_REVIEW.md" ]; then
        AGE=$(get_file_age "CODE_REVIEW.md")
        if [ "$AGE" -lt "$THRESHOLD" ]; then
            SHOULD_RUN=true
            REASON="CODE_REVIEW.md generated ${AGE}s ago"
        fi
    elif [ -f "review_report.md" ]; then
         AGE=$(get_file_age "review_report.md")
         if [ "$AGE" -lt "$THRESHOLD" ]; then
             SHOULD_RUN=true
             REASON="review_report.md generated ${AGE}s ago"
         fi
    fi
fi

if [ "$SHOULD_RUN" = "true" ]; then
    log "ACTIVATED: $REASON"
    cat << 'EOF'
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 SKILL ARCHITECT: EVOLUTION CHECK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Context detected: Task likely completed.
Evaluate if you have gained new knowledge:

1. NEW CAPABILITY?
   → Use `skill-architect` (Tool: Forge) to create a new skill.

2. NEW WISDOM? (Bug fix, better prompt, preference)
   → Use `skill-architect` (Tool: Refine) to save it to an existing skill.

This ensures your toolkit gets smarter over time.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF
fi

# Always exit successfully to prevent hook errors
exit 0
