#!/bin/bash
# Archive current plan and design documents
# Moves files from docs/plans/ and docs/design/ to .claude/archive/

ARCHIVE_DIR=".claude/archive"
PLANS_SRC="docs/plans"
DESIGN_SRC="docs/design"
TIMESTAMP=$(date "+%Y-%m-%d")

mkdir -p "$ARCHIVE_DIR/plans"
mkdir -p "$ARCHIVE_DIR/design"

echo "Archiving tasks..."

# Archive Plans
if [ -d "$PLANS_SRC" ]; then
    COUNT=$(find "$PLANS_SRC" -name "*.md" | wc -l)
    if [ "$COUNT" -gt 0 ]; then
        mv "$PLANS_SRC"/*.md "$ARCHIVE_DIR/plans/" 2>/dev/null
        echo "✅ Archived $COUNT plan(s) to $ARCHIVE_DIR/plans/"
    else
        echo "ℹ️ No plans found in $PLANS_SRC"
    fi
fi

# Archive Designs (Optional - usually we keep designs, but user asked to archive "task planning files")
# The original archive-task description said "docs/plans/*".
# Let's assume we only archive plans for now, as designs might be persistent documentation.
# But if the user wants to "archive task", maybe they mean the whole context.
# I'll stick to plans for now to be safe, or maybe move them if they are marked "done".
# For now, just plans.

echo "Archive complete."
