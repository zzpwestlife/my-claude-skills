#!/bin/bash
# Get the absolute path to the project root (parent of .claude/hooks/)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

payload=$(cat)
skill=$(jq -r '.tool_input.name // .tool_input.skill // ""' <<< "$payload")
args=$(jq -r '.tool_input.args // ""' <<< "$payload")

echo "$(date -u +%s)  $USER   $skill  $args" >> "$PROJECT_ROOT/.claude/skill-usage.log"
