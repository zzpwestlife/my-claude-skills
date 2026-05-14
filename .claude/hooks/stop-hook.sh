#!/bin/bash

# Superpower Loop Stop Hook
# Prevents session exit when a superpower-loop is active
# Feeds Claude's output back as input to continue the loop

set -euo pipefail

# Returns 0 when "doc-related" files are dirty.
# We intentionally scope to "docs/memory hygiene" surface area to avoid over-triggering.
doc_dirty() {
  git rev-parse --is-inside-work-tree >/dev/null 2>&1 || return 1

  # Porcelain output examples:
  #  M README.md
  # ?? docs/new.md
  # R  docs/old.md -> docs/new.md
  local status
  status="$(git status --porcelain --untracked-files=normal 2>/dev/null || true)"
  [[ -n "$status" ]] || return 1

  echo "$status" | grep -Eq '(^|[[:space:]])(README\.md|CLAUDE\.md|AGENTS\.md|HANDOFF\.md|docs/)' && return 0
  return 1
}

# Read hook input from stdin (advanced stop hook API)
HOOK_INPUT=$(cat)

HOOK_SESSION=$(echo "$HOOK_INPUT" | jq -r '.session_id // ""')

# Find the state file owned by this session.
# Supports multiple concurrent loops (e.g. parallel tasks in executing-plans)
# by scanning all .claude/superpower-loop*.local.md files and matching session_id.
SUPERPOWER_STATE_FILE=""

for candidate in .claude/superpower-loop*.local.md; do
  [[ -f "$candidate" ]] || continue
  CANDIDATE_FRONTMATTER=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$candidate")
  CANDIDATE_SESSION=$(echo "$CANDIDATE_FRONTMATTER" | grep '^session_id:' | sed 's/session_id: *//' || true)
  # Match explicit session_id, or fall through for legacy files without one
  if [[ -z "$CANDIDATE_SESSION" ]] || [[ "$CANDIDATE_SESSION" == "$HOOK_SESSION" ]]; then
    SUPERPOWER_STATE_FILE="$candidate"
    break
  fi
done

if [[ -z "$SUPERPOWER_STATE_FILE" ]]; then
  # No active loop for this session.
  # If doc-related files are dirty, block exit and offer a TUI choice to run neat-freak.
  if doc_dirty; then
    jq -n \
      '{
        "decision": "block",
        "reason": "<system-reminder>⚠️ 检测到文档相关改动（README/docs/CLAUDE.md/AGENTS.md 等）。你 MUST 立刻调用 AskUserQuestion 工具弹出退出前菜单（不要输出其它文本）。\\n\\nquestion: \"退出前是否运行 neat-freak 进行收尾同步？\"\\noptions: 1) \"运行 neat-freak（推荐）\" 2) \"跳过并退出\"\\n\\n如果用户选择运行：调用 Skill(name=\"neat-freak\")，完成后告诉用户可再次 /exit 退出。\\n如果用户选择跳过：只输出一句“已跳过，本次不做同步。可再次 /exit 退出。”\\n\\n注意：此拦截无法覆盖强制杀进程/关机等情况；下次 SessionStart 会再次提醒（若仍存在文档改动）。</system-reminder>",
        "systemMessage": "neat-freak intercept: docs dirty, show TUI"
      }'
    exit 0
  fi

  # Otherwise allow exit.
  exit 0
fi

# Parse markdown frontmatter (YAML between ---) and extract values
FRONTMATTER=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$SUPERPOWER_STATE_FILE")
ITERATION=$(echo "$FRONTMATTER" | grep '^iteration:' | sed 's/iteration: *//')
MAX_ITERATIONS=$(echo "$FRONTMATTER" | grep '^max_iterations:' | sed 's/max_iterations: *//')
# Extract completion_promise and strip surrounding quotes if present
COMPLETION_PROMISE=$(echo "$FRONTMATTER" | grep '^completion_promise:' | sed 's/completion_promise: *//' | sed 's/^"\(.*\)"$/\1/')

# Validate numeric fields before arithmetic operations
if [[ ! "$ITERATION" =~ ^[0-9]+$ ]]; then
  echo "Warning: Superpower loop: State file corrupted" >&2
  echo "   File: $SUPERPOWER_STATE_FILE" >&2
  echo "   Problem: 'iteration' field is not a valid number (got: '$ITERATION')" >&2
  echo "" >&2
  echo "   This usually means the state file was manually edited or corrupted." >&2
  echo "   Superpower loop is stopping. Run /superpower-loop again to start fresh." >&2
  rm "$SUPERPOWER_STATE_FILE"
  exit 0
fi

if [[ ! "$MAX_ITERATIONS" =~ ^[0-9]+$ ]]; then
  echo "Warning: Superpower loop: State file corrupted" >&2
  echo "   File: $SUPERPOWER_STATE_FILE" >&2
  echo "   Problem: 'max_iterations' field is not a valid number (got: '$MAX_ITERATIONS')" >&2
  echo "" >&2
  echo "   This usually means the state file was manually edited or corrupted." >&2
  echo "   Superpower loop is stopping. Run /superpower-loop again to start fresh." >&2
  rm "$SUPERPOWER_STATE_FILE"
  exit 0
fi

# Check if max iterations reached
if [[ $MAX_ITERATIONS -gt 0 ]] && [[ $ITERATION -ge $MAX_ITERATIONS ]]; then
  echo "Superpower loop: Max iterations ($MAX_ITERATIONS) reached."
  rm "$SUPERPOWER_STATE_FILE"
  exit 0
fi

# Get transcript path from hook input
TRANSCRIPT_PATH=$(echo "$HOOK_INPUT" | jq -r '.transcript_path')

if [[ ! -f "$TRANSCRIPT_PATH" ]]; then
  # transcript_path may be a directory or missing in some Claude Code versions — not an error
  rm "$SUPERPOWER_STATE_FILE"
  exit 0
fi

# Read last assistant message from transcript (JSONL format - one JSON per line)
# First check if there are any assistant messages
if ! grep -q '"role":"assistant"' "$TRANSCRIPT_PATH"; then
  echo "Warning: Superpower loop: No assistant messages found in transcript" >&2
  echo "   Transcript: $TRANSCRIPT_PATH" >&2
  echo "   This is unusual and may indicate a transcript format issue" >&2
  echo "   Superpower loop is stopping." >&2
  rm "$SUPERPOWER_STATE_FILE"
  exit 0
fi

# Extract the most recent assistant text block.
#
# Claude Code writes each content block (text/tool_use/thinking) as its own
# JSONL line, all with role=assistant. So slurp the last N assistant lines,
# flatten to text blocks only, and take the last one.
#
# Capped at the last 100 assistant lines to keep jq's slurp input bounded
# for long-running sessions.
LAST_LINES=$(grep '"role":"assistant"' "$TRANSCRIPT_PATH" | tail -n 100)
if [[ -z "$LAST_LINES" ]]; then
  echo "Warning: Superpower loop: Failed to extract assistant messages" >&2
  echo "   Superpower loop is stopping." >&2
  rm "$SUPERPOWER_STATE_FILE"
  exit 0
fi

# Parse the recent lines and pull out the final text block.
# `last // ""` yields empty string when no text blocks exist (e.g. a turn
# that is all tool calls). That's fine: empty text means no <promise> tag,
# so the loop simply continues.
# (Briefly disable errexit so a jq failure can be caught by the $? check.)
set +e
LAST_OUTPUT=$(echo "$LAST_LINES" | jq -rs '
  map(.message.content[]? | select(.type == "text") | .text) | last // ""
' 2>&1)
JQ_EXIT=$?
set -e

# Check if jq succeeded
if [[ $JQ_EXIT -ne 0 ]]; then
  echo "Warning: Superpower loop: Failed to parse assistant message JSON" >&2
  echo "   Error: $LAST_OUTPUT" >&2
  echo "   This may indicate a transcript format issue." >&2
  echo "   Superpower loop is stopping." >&2
  rm "$SUPERPOWER_STATE_FILE"
  exit 0
fi

# Check for completion promise (only if set)
if [[ "$COMPLETION_PROMISE" != "null" ]] && [[ -n "$COMPLETION_PROMISE" ]]; then
  # Extract text from <promise> tags using Perl for multiline support
  # -0777 slurps entire input, s flag makes . match newlines
  # .*? is non-greedy (takes FIRST tag), whitespace normalized
  PROMISE_TEXT=$(echo "$LAST_OUTPUT" | perl -0777 -pe 's/.*?<promise>(.*?)<\/promise>.*/$1/s; s/^\s+|\s+$//g; s/\s+/ /g' 2>/dev/null || echo "")

  # Use = for literal string comparison (not pattern matching)
  # == in [[ ]] does glob pattern matching which breaks with *, ?, [ characters
  if [[ -n "$PROMISE_TEXT" ]] && [[ "$PROMISE_TEXT" = "$COMPLETION_PROMISE" ]]; then
    echo "Superpower loop: Detected <promise>$COMPLETION_PROMISE</promise>"
    rm "$SUPERPOWER_STATE_FILE"
    
    # FLOWSTATE INTERCEPT: Inject TUI command on completion
    # Instead of just allowing exit, we block one last time to inject the TUI options
    if [[ "$COMPLETION_PROMISE" == "BRAINSTORMING_COMPLETE" ]]; then
      jq -n \
        '{
          "decision": "block",
          "reason": "<system-reminder>⚡️ FLOWSTATE INTERCEPT: The Brainstorming and Design phase is complete. You MUST NOW physically invoke the `AskUserQuestion` tool to present the next steps. Do not say anything else. Set question to \"Brainstorming complete. What is the next step?\" and options to: 1. \"Proceed to Planning\" (Invoke writing-plans), 2. \"Review Design\", 3. \"Refine\".</system-reminder>",
          "systemMessage": "FlowState: Forcing TUI menu..."
        }'
      exit 0
    fi
    
    exit 0
  fi
fi

# Not complete - continue loop with SAME PROMPT
NEXT_ITERATION=$((ITERATION + 1))

# Extract prompt (everything after the closing ---)
# Skip first --- line, skip until second --- line, then print everything after
# Use i>=2 instead of i==2 to handle --- in prompt content
PROMPT_TEXT=$(awk '/^---$/{i++; next} i>=2' "$SUPERPOWER_STATE_FILE")

if [[ -z "$PROMPT_TEXT" ]]; then
  echo "Warning: Superpower loop: State file corrupted or incomplete" >&2
  echo "   File: $SUPERPOWER_STATE_FILE" >&2
  echo "   Problem: No prompt text found" >&2
  echo "" >&2
  echo "   This usually means:" >&2
  echo "     - State file was manually edited" >&2
  echo "     - File was corrupted during writing" >&2
  echo "" >&2
  echo "   Superpower loop is stopping. Run /superpower-loop again to start fresh." >&2
  rm "$SUPERPOWER_STATE_FILE"
  exit 0
fi

# Update iteration in frontmatter (portable across macOS and Linux)
# Create temp file, then atomically replace
TEMP_FILE="${SUPERPOWER_STATE_FILE}.tmp.$$"
sed "s/^iteration: .*/iteration: $NEXT_ITERATION/" "$SUPERPOWER_STATE_FILE" > "$TEMP_FILE"
mv "$TEMP_FILE" "$SUPERPOWER_STATE_FILE"

# Build system message with iteration count and completion promise info
if [[ "$COMPLETION_PROMISE" != "null" ]] && [[ -n "$COMPLETION_PROMISE" ]]; then
  SYSTEM_MSG="Superpower loop iteration $NEXT_ITERATION | To stop: output <promise>$COMPLETION_PROMISE</promise> (ONLY when statement is TRUE - do not lie to exit!)"
else
  SYSTEM_MSG="Superpower loop iteration $NEXT_ITERATION | No completion promise set - loop runs infinitely"
fi

# Append completion instruction to the re-injected prompt so Claude always
# has a positive directive — not just the negative "do not lie" constraint in
# the system message. This is critical: by the time later iterations run,
# the original skill context (SKILL.md) has been compressed out of the
# conversation window. Without this, Claude sees only a bare task prompt and
# never knows it must emit the promise tag when done.
if [[ "$COMPLETION_PROMISE" != "null" ]] && [[ -n "$COMPLETION_PROMISE" ]]; then
  INJECTED_PROMPT="${PROMPT_TEXT}

---
LOOP COMPLETION REQUIRED: When the above task is genuinely complete, output the following tag as the very last line of your response — nothing after it:
<promise>${COMPLETION_PROMISE}</promise>"
else
  INJECTED_PROMPT="$PROMPT_TEXT"
fi

# Output JSON to block the stop and feed prompt back
# The "reason" field contains the prompt that will be sent back to Claude
jq -n \
  --arg prompt "$INJECTED_PROMPT" \
  --arg msg "$SYSTEM_MSG" \
  '{
    "decision": "block",
    "reason": $prompt,
    "systemMessage": $msg
  }'

# Exit 0 for successful hook execution
exit 0
