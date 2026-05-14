#!/bin/bash
# Cleanup runtime artifacts script

echo "Cleaning up runtime artifacts..."

# Remove directories if they exist
[ -d ".claude/audit" ] && rm -rf .claude/audit && echo "Removed .claude/audit"
[ -d ".claude/logs" ] && rm -rf .claude/logs && echo "Removed .claude/logs"
[ -d ".claude/tmp" ] && rm -rf .claude/tmp && echo "Removed .claude/tmp"

echo "Cleanup complete."
