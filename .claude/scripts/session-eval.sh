#!/bin/bash
# session-eval.sh - Claude Code Session Evaluator
# Usage:
#   .claude/scripts/session-eval.sh [session_id|"latest"] [out_dir]
#   .claude/scripts/session-eval.sh --global [session_id|"latest"] [out_dir]
#
#   --global   Scan all projects in ~/.claude/projects (no project dependency)
#   list       Show available session files
#
# Output: 8 files (4 x jsonl + 4 x csv):
#   user_prompts.*   User inputs
#   api_requests.*   API usage & metadata
#   tool_decisions.* Tool call decisions
#   tool_results.*   Tool execution results

set -euo pipefail

GLOBAL_MODE=false
SESSION_ID="latest"
OUT_DIR=""
POSITIONAL_ARGS=()

for arg in "$@"; do
  case "$arg" in
    --global) GLOBAL_MODE=true; shift ;;
    --help|-h)
      echo "Usage: $0 [--global] [session_id|'latest'] [out_dir]"
      echo "  --global   Scan all projects in ~/.claude/projects"
      echo "  list       Show available sessions"
      exit 0
      ;;
    *) POSITIONAL_ARGS+=("$1"); shift ;;
  esac
done

case ${#POSITIONAL_ARGS[@]} in
  0) ;;
  1) SESSION_ID="${POSITIONAL_ARGS[0]}" ;;
  2) SESSION_ID="${POSITIONAL_ARGS[0]}"; OUT_DIR="${POSITIONAL_ARGS[1]}" ;;
  *) echo "Too many arguments" >&2; exit 1 ;;
esac

PROJECTS_DIR="$HOME/.claude/projects"

if [[ "$GLOBAL_MODE" == "true" ]]; then
  if [[ "$SESSION_ID" == "list" ]]; then
    echo "Available sessions (newest first):"
    ls -t "$PROJECTS_DIR"/*/*.jsonl 2>/dev/null | head -20 | sed 's|^|  |'
    exit 0
  fi

  if [[ "$SESSION_ID" == "latest" ]]; then
    SESSION_FILE="$(ls -t "$PROJECTS_DIR"/*/*.jsonl 2>/dev/null | head -1)"
  else
    SESSION_FILE="$(find "$PROJECTS_DIR" -name "${SESSION_ID}*.jsonl" 2>/dev/null | head -1)"
  fi

  if [[ -z "$SESSION_FILE" ]] || [[ ! -f "$SESSION_FILE" ]]; then
    echo "Session not found: $SESSION_ID" >&2
    echo "Run '$0 --global list' to see available sessions." >&2
    exit 1
  fi

  OUT_DIR="${OUT_DIR:-$HOME/.claude/eval_exports/$(date -u +%Y%m%dT%H%M%SZ)}"
else
  SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  PROJECT_ROOT="$(cd "$SELF_DIR/../.." && pwd)"
  PROJECT_KEY="$(echo "$PROJECT_ROOT" | sed 's#/#-#g')"
  SESSION_DIR="$PROJECTS_DIR/$PROJECT_KEY"

  if [[ ! -d "$SESSION_DIR" ]]; then
    echo "No session directory for this project: $SESSION_DIR" >&2
    exit 1
  fi

  if [[ "$SESSION_ID" == "latest" ]]; then
    SESSION_FILE="$(ls -t "$SESSION_DIR"/*.jsonl 2>/dev/null | head -1)"
  else
    if [[ -f "$SESSION_ID" ]]; then
      SESSION_FILE="$SESSION_ID"
    else
      SESSION_FILE="$SESSION_DIR/${SESSION_ID}.jsonl"
    fi
  fi

  if [[ -z "$SESSION_FILE" ]] || [[ ! -f "$SESSION_FILE" ]]; then
    echo "Session file not found: $SESSION_ID" >&2
    echo "Run '$0 list' to see available sessions." >&2
    exit 1
  fi

  OUT_DIR="${OUT_DIR:-$PROJECT_ROOT/.claude/eval_exports/$(date -u +%Y%m%dT%H%M%SZ)}"
fi

mkdir -p "$OUT_DIR"

echo "session_file=$SESSION_FILE"
echo "out_dir=$OUT_DIR"

jq -rc '
  select(.type=="user" and .message.role=="user" and (.message.content|type=="string"))
  | {timestamp, session_id, prompt:.message.content}
' "$SESSION_FILE" > "$OUT_DIR/user_prompts.jsonl"

jq -rc '
  select(.type=="assistant" and .message.usage!=null)
  | {
      timestamp,
      session_id,
      model:.message.model,
      message_id:.message.id,
      stop_reason:(.message.stop_reason // ""),
      input_tokens:(.message.usage.input_tokens // 0),
      output_tokens:(.message.usage.output_tokens // 0),
      cache_read_input_tokens:(.message.usage.cache_read_input_tokens // 0),
      cache_creation_input_tokens:(.message.usage.cache_creation_input_tokens // 0)
    }
' "$SESSION_FILE" > "$OUT_DIR/api_requests.jsonl"

jq -rc '
  select(.type=="assistant")
  | . as $root
  | .message.content[]?
  | select(.type=="tool_use")
  | {
      timestamp: $root.timestamp,
      session_id: $root.session_id,
      tool_use_id:.id,
      tool_name:.name,
      tool_input_json:(.input | tojson)
    }
' "$SESSION_FILE" > "$OUT_DIR/tool_decisions.jsonl"

jq -rc '
  select(.type=="user")
  | . as $root
  | .message.content[]?
  | select(.type=="tool_result")
  | {
      timestamp: $root.timestamp,
      session_id: $root.session_id,
      tool_use_id:.tool_use_id,
      tool_result_preview:((.content | tostring)[0:200])
    }
' "$SESSION_FILE" > "$OUT_DIR/tool_results.jsonl"

jq -sr '
  ["timestamp","session_id","prompt"],
  (.[] | [.timestamp, .session_id, .prompt])
  | @csv
' "$OUT_DIR/user_prompts.jsonl" > "$OUT_DIR/user_prompts.csv"

jq -sr '
  ["timestamp","session_id","model","message_id","stop_reason","input_tokens","output_tokens","cache_read_input_tokens","cache_creation_input_tokens"],
  (.[] | [.timestamp, .session_id, .model, .message_id, .stop_reason, (.input_tokens|tostring), (.output_tokens|tostring), (.cache_read_input_tokens|tostring), (.cache_creation_input_tokens|tostring)])
  | @csv
' "$OUT_DIR/api_requests.jsonl" > "$OUT_DIR/api_requests.csv"

jq -sr '
  ["timestamp","session_id","tool_use_id","tool_name","tool_input_json"],
  (.[] | [.timestamp, .session_id, .tool_use_id, .tool_name, .tool_input_json])
  | @csv
' "$OUT_DIR/tool_decisions.jsonl" > "$OUT_DIR/tool_decisions.csv"

jq -sr '
  ["timestamp","session_id","tool_use_id","tool_result_preview"],
  (.[] | [.timestamp, .session_id, .tool_use_id, .tool_result_preview])
  | @csv
' "$OUT_DIR/tool_results.jsonl" > "$OUT_DIR/tool_results.csv"

echo ""
echo "generated_files="
ls "$OUT_DIR"