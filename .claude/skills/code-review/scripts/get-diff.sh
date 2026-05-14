#!/usr/bin/env bash
set -euo pipefail

if git diff --cached --quiet; then
  git diff HEAD
else
  git diff --cached
fi
