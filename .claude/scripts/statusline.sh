#!/bin/bash

# 读取 stdin 输入
input=$(cat)

# 定义颜色
RESET='\033[0m'
BOLD='\033[1m'
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
GRAY='\033[0;90m'

# 1. 模型信息
MODEL=$(echo "$input" | jq -r '.model.display_name // "Claude"')
MODEL_DISPLAY="${BOLD}${MAGENTA}🤖 ${MODEL}${RESET}"

# 2. 目录信息
DIR=$(echo "$input" | jq -r '.workspace.current_dir')
DIR_NAME="${DIR##*/}"
DIR_DISPLAY="📁 ${DIR_NAME}"

# 3. Git 分支
GIT_DISPLAY=""
if git rev-parse --git-dir > /dev/null 2>&1; then
    BRANCH=$(git branch --show-current 2>/dev/null)
    if [ -n "$BRANCH" ]; then
        GIT_DISPLAY=" ${CYAN} ${BRANCH}${RESET}"
    fi
fi

# 4. Token 使用率 (显示百分比和具体数值)
CONTEXT_SIZE=$(echo "$input" | jq -r '.context_window.context_window_size // 200000')
USAGE=$(echo "$input" | jq '.context_window.current_usage')
PERCENT_USED=0
TOKEN_DISPLAY=""

if [ "$USAGE" != "null" ] && [ "$USAGE" != "" ]; then
    # 计算总 Token
    CURRENT_TOKENS=$(echo "$USAGE" | jq '.input_tokens + (.cache_creation_input_tokens // 0) + (.cache_read_input_tokens // 0)')
    
    # 计算百分比
    if [ "$CONTEXT_SIZE" -gt 0 ]; then
        PERCENT_USED=$((CURRENT_TOKENS * 100 / CONTEXT_SIZE))
        if [ "$PERCENT_USED" -eq 0 ] && [ "$CURRENT_TOKENS" -gt 0 ]; then
            PERCENT_USED=1
        fi
    fi
    
    # 格式化 Token 数 (例如 22.5k)
    if [ "$CURRENT_TOKENS" -gt 1000 ]; then
        if command -v awk &> /dev/null; then
            TOKENS_FMT=$(echo "$CURRENT_TOKENS" | awk '{printf "%.1fk", $1/1000}')
        else
            TOKENS_FMT="$((CURRENT_TOKENS / 1000))k"
        fi
    else
        TOKENS_FMT="$CURRENT_TOKENS"
    fi
    
    # 颜色逻辑
    TOKEN_COLOR=$GREEN
    if [ "$PERCENT_USED" -ge 80 ]; then
        TOKEN_COLOR=$RED
    elif [ "$PERCENT_USED" -ge 50 ]; then
        TOKEN_COLOR=$YELLOW
    fi
    
    # 显示格式: 📊 11% (22.1k)
    TOKEN_DISPLAY="${TOKEN_COLOR}📊 ${PERCENT_USED}% (${TOKENS_FMT})${RESET}"
else
    TOKEN_DISPLAY="${GRAY}📊 0%${RESET}"
fi

# 5. 成本估算
COST_VAL=$(echo "$input" | jq -r '.cost.total_cost // 0')
COST_DISPLAY=""
if [ "$COST_VAL" != "null" ]; then
    if command -v awk &> /dev/null; then
        COST_FMT=$(echo "$COST_VAL" | awk '{printf "%.4f", $1}')
        COST_DISPLAY=" ${GRAY}|${RESET} 💰 \$${COST_FMT}"
    else
        COST_DISPLAY=" ${GRAY}|${RESET} 💰 \$${COST_VAL}"
    fi
fi

# 分隔符
SEP="${GRAY}|${RESET}"

# 组合输出
echo -e "${MODEL_DISPLAY} ${SEP} ${DIR_DISPLAY}${GIT_DISPLAY} ${SEP} ${TOKEN_DISPLAY}${COST_DISPLAY}"
