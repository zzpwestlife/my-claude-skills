# lark-doc-copywriting Skill 设计文档

**日期**：2026-05-11  
**状态**：待实现  
**位置**：`~/.claude/skills/lark-doc-copywriting/SKILL.md`

---

## 概览

将"改造版中文文案排版指北"落地为可执行的飞书文档整理 skill。一条指令完成：全角标点 → 半角、空格规范化、未包裹代码块 → fenced code block。

**不是**通用中文排版 skill；规则是"改造版"——保留必要空格、标点尽量半角，不是严格的 W3C 规范。

---

## 触发条件

**触发**（用户显式请求）：
- "帮我整理排版" / "标点半角化" / "中文排版修复"
- "整理这篇文档的标点" / "代码块整理"

**不触发**：
- 用户仅读取、搜索、查看文档内容
- 用户提供 URL 但未提排版相关需求

---

## 执行流程

```
用户提供文档 URL
       ↓
Step 1: 解析 URL 类型
  - /wiki/TOKEN → lark-cli wiki spaces get_node 获取真实 obj_token
  - /docx/TOKEN 或 /doc/TOKEN → 直接使用 TOKEN
       ↓
Step 2: docs +fetch 获取 markdown → /tmp/doc_original.md
       ↓
Step 3: 写出并运行 Python 脚本 /tmp/lark_copywriting.py
  - 阶段1: 标点半角化 + 空格修复（fix_line 逐行处理）
  - 阶段2: 代码块候选检测（detect_code_candidates）
  - 输出:
      /tmp/doc_fixed.md          — 修复后内容
      /tmp/doc_diff.txt          — unified diff
      /tmp/code_candidates.json  — 代码块候选列表
       ↓
Step 4: Claude 读取输出
  - 读 diff，统计变更行数，提取 3 个典型示例
  - 读 candidates，确认每个候选的语言 tag（可调整）
       ↓
Step 5: 展示摘要 + AskUserQuestion 确认
  示例："将修改 42 处标点，检测到 2 处未包裹代码块（sql, bash）。
        示例变更：'结束。下一步' → '结束. 下一步'
        [确认写入] [取消]"
       ↓
Step 6: 用户确认后
  - 以 image token 为分隔符将文档切成段
  - 每段调用 replace_range 写回（使用 subprocess 传参，不走 shell）
  - 报告完成：成功段数 / 失败段数
```

---

## Python 脚本设计

### PUNCT_MAP（顺序敏感）

```python
PUNCT_MAP = [
    ('\uff0c', ','),   # 全角逗号
    ('\u3002', '.'),   # 句号
    ('\u3001', ','),   # 顿号 → 逗号
    ('\uff1a', ':'),   # 全角冒号
    ('\uff08', '('),   # 全角左括号
    ('\uff09', ')'),   # 全角右括号
    ('\u201c', '"'),   # 左弯引号
    ('\u201d', '"'),   # 右弯引号
    ('\uff1f', '?'),   # 全角问号
    ('\uff1b', ';'),   # 全角分号
    ('\uff01', '!'),   # 全角感叹号
    ('\u2014\u2014', '--'),  # 双破折号
    ('\u2014', '-'),   # 单破折号
]
```

### fix_line 函数（操作顺序关键）

```python
def fix_line(line):
    stripped = line.strip()
    # 跳过不处理的行
    if stripped.startswith('<image ') or stripped.startswith('```'):
        return line
    # 1. 替换全角标点
    for src, dst in PUNCT_MAP:
        line = line.replace(src, dst)
    # 2. 先去除标点前多余空格（顺序关键：必须在补空格之前）
    line = re.sub(r'\s+([,.:;!?])(?![-/])', r'\1', line)
    # 3. 补标点后空格
    line = re.sub(r'(?<![0-9/\s]),(?=[^\s\n,])', ', ', line)
    line = re.sub(r'(?<![0-9/\s\.])\.(?=[\u4e00-\u9fffA-Z])', '. ', line)
    line = re.sub(r'[?!](?=[\u4e00-\u9fff\u0041-\u005A])',
                  lambda m: m.group(0) + ' ', line)
    line = re.sub(r':(?!//|[0-9])(?=[^\s\n])', ': ', line)
    line = re.sub(r'(?<=[^\s\-])--(?=[^\s\-])', ' -- ', line)
    # 4. 压缩多余空格
    line = re.sub(r'(?<!\n)  +', ' ', line)
    return line
```

**关键约束**：步骤 2（去标点前空格）必须在步骤 3（补标点后空格）之前。原因：`做 。下一步` 经全角替换后变为 `做 .下一步`，若先补空格则 `.` 前有空格触发不了补空格的正则，导致 `做 .下一步` 无法变为 `做. 下一步`。

### detect_code_candidates 函数

```python
CODE_PATTERNS = {
    'sql':  r'^(CREATE|SELECT|INSERT|UPDATE|DELETE|ALTER|DROP|--\s)',
    'json': r'^\s*[{\[]',
    'bash': r'^(curl|npm|pip|git|docker|make|cd|ls|cat)\b',
}

def detect_code_candidates(lines):
    """
    扫描连续3行以上匹配同一模式的段落。
    返回: [{"start": int, "end": int, "lang": str, "preview": str}]
    跳过已在 ``` 块内的行。
    """
```

### segment_to_markdown（段落分隔）

```python
def segment_to_markdown(seg_text):
    lines = seg_text.split('\n')
    result_lines = []
    in_code = False
    for line in lines:
        if line.strip().startswith('```'):
            in_code = not in_code
            result_lines.append(line)
        elif in_code:
            result_lines.append(line)
        elif line.strip():
            result_lines.append(fix_line(line.rstrip('\n')))
    return '\n\n'.join(result_lines)  # \n\n 而非 \n，防止段落合并
```

---

## SKILL.md 结构

```
--- frontmatter (name/version/description/metadata) ---

# lark-doc-copywriting

> 前置：先读 lark-shared/SKILL.md

## 触发场景

## 执行步骤（Step 1-6 详细命令）

## Python 脚本（完整 heredoc）

## 关键约束
- \n\n 段落分隔（不用 \n）
- image token 行原样保留
- 已有 ``` 行跳过
- subprocess 传参，不经 shell

## 错误处理
- wiki token 解析失败 → 提示用户检查 URL
- diff 为空 → 告知"文档无需修改"
- replace_range 失败 → 报告具体段落，其余继续执行
```

---

## 约束与教训（来自实际验证）

| 约束 | 原因 |
|------|------|
| `\n\n` 分隔段落 | 单 `\n` 在 lark-doc 中是软换行，不创建新块 |
| `<image token>` 行不处理 | image block 无法通过文本替换重建 |
| Unicode escape 写 PUNCT_MAP | shell heredoc 中直接写 `"` `"` 可能编码丢失 |
| subprocess 传参不走 shell | `@file` 只接受相对路径；复杂内容 shell 引号转义易出错 |
| 先去空格再补空格 | 顺序错误会导致 `做 .下一步` 无法正确处理 |

---

## 成功标准

- [ ] `~/.claude/skills/lark-doc-copywriting/SKILL.md` 存在且 frontmatter 合法
- [ ] 给定飞书文档 URL（wiki/docx 两种），skill 能正确获取内容
- [ ] diff 摘要展示后，用户确认，文档成功写回
- [ ] image block 行在写回后保持不变
- [ ] 已有 ``` 块内的内容不被二次处理
