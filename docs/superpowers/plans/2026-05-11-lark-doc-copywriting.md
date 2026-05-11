# lark-doc-copywriting Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create `~/.claude/skills/lark-doc-copywriting/SKILL.md` — a self-contained skill that converts full-width Chinese punctuation to half-width, fixes spacing, and wraps bare code blocks in fenced code fences for Feishu documents.

**Architecture:** Single `SKILL.md` file with embedded Python script (heredoc). Claude writes the script to `/tmp/`, runs it to produce a diff + code candidates, shows a summary, gets user confirmation, then calls `lark-cli docs +update --mode replace_range` per document segment via Python subprocess (not shell) to avoid escaping issues.

**Tech Stack:** Python 3, lark-cli, regex, difflib, json, subprocess

---

## File Structure

| File | Action | Responsibility |
|------|--------|----------------|
| `~/.claude/skills/lark-doc-copywriting/SKILL.md` | Create | Entire skill: frontmatter, steps, embedded Python, constraints |

---

### Task 1: Write and Validate the Python Transform Script

**Goal:** Confirm the core Python logic works correctly before embedding it in the skill.

**Files:**
- Create: `/tmp/lark_copywriting.py` (temporary validation only — final version lives inside SKILL.md)

- [ ] **Step 1: Write the script to `/tmp/lark_copywriting.py`**

```python
#!/usr/bin/env python3
# INPUT: /tmp/doc_original.md (fetched lark doc markdown)
# OUTPUT: /tmp/doc_fixed.md, /tmp/doc_diff.txt, /tmp/code_candidates.json

import re, sys, json, difflib

PUNCT_MAP = [
    ('\uff0c', ','), ('\u3002', '.'), ('\u3001', ','), ('\uff1a', ':'),
    ('\uff08', '('), ('\uff09', ')'),
    ('\u201c', '"'), ('\u201d', '"'),
    ('\uff1f', '?'), ('\uff1b', ';'), ('\uff01', '!'),
    ('\u2014\u2014', '--'), ('\u2014', '-'),
]

CODE_PATTERNS = {
    'sql':  re.compile(r'^(CREATE|SELECT|INSERT|UPDATE|DELETE|ALTER|DROP|--\s)', re.I),
    'json': re.compile(r'^\s*[{\[]'),
    'bash': re.compile(r'^(curl|npm|pip|git|docker|make|cd|ls|cat)\b'),
}

def fix_line(line):
    stripped = line.strip()
    if stripped.startswith('<image ') or stripped.startswith('```'):
        return line
    for src, dst in PUNCT_MAP:
        line = line.replace(src, dst)
    line = re.sub(r'\s+([,.:;!?])(?![-/])', r'\1', line)
    line = re.sub(r'(?<![0-9/\s]),(?=[^\s\n,])', ', ', line)
    line = re.sub(r'(?<![0-9/\s\.])\.(?=[\u4e00-\u9fffA-Z])', '. ', line)
    line = re.sub(r'[?!](?=[\u4e00-\u9fff\u0041-\u005A])', lambda m: m.group(0)+' ', line)
    line = re.sub(r':(?!//|[0-9])(?=[^\s\n])', ': ', line)
    line = re.sub(r'(?<=[^\s\-])--(?=[^\s\-])', ' -- ', line)
    line = re.sub(r'(?<!\n)  +', ' ', line)
    return line

def detect_code_candidates(lines):
    # Only first line needs to match a CODE_PATTERN; expand block until blank line.
    # SQL/bash continuation lines don't match patterns — old per-line approach missed them.
    candidates = []
    in_code = False
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped.startswith('```'):
            in_code = not in_code
            i += 1
            continue
        if in_code:
            i += 1
            continue
        matched_lang = None
        for lang, pat in CODE_PATTERNS.items():
            if pat.match(stripped):
                matched_lang = lang
                break
        if matched_lang:
            block_start = i
            j = i + 1
            while j < len(lines):
                next_stripped = lines[j].strip()
                if not next_stripped or next_stripped.startswith('<image '):
                    break
                j += 1
            block_end = j - 1
            if block_end - block_start + 1 >= 3:
                candidates.append({
                    'start': block_start, 'end': block_end,
                    'lang': matched_lang, 'preview': lines[block_start][:80].strip()
                })
            i = j
        else:
            i += 1
    return candidates

def process(src_path, dst_path, diff_path, candidates_path):
    with open(src_path, encoding='utf-8') as f:
        original_lines = f.readlines()
    fixed_lines = []
    in_code = False
    for line in original_lines:
        stripped = line.strip()
        if stripped.startswith('```'):
            in_code = not in_code
            fixed_lines.append(line)
        elif in_code or stripped.startswith('<image '):
            fixed_lines.append(line)
        else:
            fixed_lines.append(fix_line(line.rstrip('\n')) + '\n')
    with open(dst_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    diff = list(difflib.unified_diff(
        original_lines, fixed_lines,
        fromfile='original', tofile='fixed', lineterm=''
    ))
    with open(diff_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(diff))
    candidates = detect_code_candidates([l.rstrip('\n') for l in original_lines])
    with open(candidates_path, 'w', encoding='utf-8') as f:
        json.dump(candidates, f, ensure_ascii=False, indent=2)
    changed = sum(1 for d in diff if d.startswith('-') and not d.startswith('---'))
    print(f"Changed lines: {changed}")
    print(f"Code candidates: {len(candidates)}")
    for c in candidates:
        print(f"  [{c['lang']}] lines {c['start']}-{c['end']}: {c['preview']}")

if __name__ == '__main__':
    src = sys.argv[1] if len(sys.argv) > 1 else '/tmp/doc_original.md'
    process(src, '/tmp/doc_fixed.md', '/tmp/doc_diff.txt', '/tmp/code_candidates.json')
```

- [ ] **Step 2: Create a minimal test input**

```bash
cat > /tmp/test_punct.md << 'EOF'
这是一句话，后面跟着另一句话。
我是 Robert.从这一讲开始，正式进入核心功能开发。
上来就让 Claude Code 写代码是最常见的错误 ,你连这个模块要考虑哪些东西都没想清楚
这个分类是关键洞察,  "OpenAI 兼容" 是一个巨大的阵营。
CREATE TABLE provider (
id BIGINT AUTO_INCREMENT PRIMARY KEY,
name VARCHAR ( 100 ) NOT NULL COMMENT '供应商名称',
enabled TINYINT DEFAULT 1
) COMMENT '模型提供商';
<image token="abc123" width="800" height="600"/>
已有代码块不应被处理:
```json
{"key": "value"}
```
EOF
```

- [ ] **Step 3: Run script against test input**

```bash
python3 /tmp/lark_copywriting.py /tmp/test_punct.md
```

Expected output:
```
Changed lines: 4
Code candidates: 1
  [sql] lines 4-8: CREATE TABLE provider (
```

- [ ] **Step 4: Verify diff output**

```bash
cat /tmp/doc_diff.txt | grep '^[-+]' | grep -v '^---\|^+++'
```

Expected to see lines like:
```
-这是一句话，后面跟着另一句话。
+这是一句话, 后面跟着另一句话.
-我是 Robert.从这一讲开始，正式进入核心功能开发。
+我是 Robert. 从这一讲开始, 正式进入核心功能开发.
```

- [ ] **Step 5: Verify image lines are untouched**

```bash
python3 -c "
lines = open('/tmp/doc_fixed.md').readlines()
for l in lines:
    if '<image' in l:
        print('IMAGE LINE:', repr(l))
"
```

Expected: `IMAGE LINE: '<image token="abc123" width="800" height="600"/>\n'` — unchanged.

- [ ] **Step 6: Verify existing code blocks are untouched**

```bash
python3 -c "
import json
c = json.load(open('/tmp/code_candidates.json'))
# Should find SQL (lines 4-8), should NOT find the existing json block
for x in c: print(x)
assert all(x['lang'] != 'json' for x in c), 'FAIL: existing json block detected as candidate'
print('PASS: existing code blocks not in candidates')
"
```

- [ ] **Step 7: Commit validation note**

```bash
# Script validated. No files to commit — script will live inside SKILL.md.
echo "Task 1 complete"
```

---

### Task 2: Write `~/.claude/skills/lark-doc-copywriting/SKILL.md`

**Goal:** Create the full self-contained skill file.

**Files:**
- Create: `~/.claude/skills/lark-doc-copywriting/SKILL.md`

- [ ] **Step 1: Create the skill directory**

```bash
mkdir -p ~/.claude/skills/lark-doc-copywriting
```

- [ ] **Step 2: Write the complete SKILL.md**

Write the file at `~/.claude/skills/lark-doc-copywriting/SKILL.md` with this exact content:

````markdown
---
name: lark-doc-copywriting
version: 1.0.0
description: "改造版中文文案排版：将飞书文档中的全角标点转为半角、修复空格规范、整理未包裹代码块。当用户说'帮我整理排版'/'标点半角化'/'中文排版修复'/'整理这篇文档的标点'/'代码块整理'时触发。"
metadata:
  requires:
    bins: ["lark-cli", "python3"]
---

# lark-doc-copywriting

> **前置条件：** 先阅读 [`../lark-shared/SKILL.md`](../lark-shared/SKILL.md) 了解认证和安全规则。

改造版中文文案排版整理，针对飞书文档执行：
1. 全角标点 → 半角（PUNCT_MAP 映射）
2. 标点前后空格规范化
3. 未包裹代码段 → fenced code block

**不是**通用排版规范，不处理段落间距、列表格式等。

---

## 触发场景

**触发**：用户显式提出排版/标点/代码块整理需求：
- "帮我整理排版" / "整理这篇文档" / "标点半角化"
- "中文排版修复" / "代码块整理"

**不触发**：用户仅读取、查看、搜索文档时不调用本 skill。

---

## 执行步骤

### Step 1: 解析文档 URL，获取 doc_id

```bash
# wiki URL: https://xxx.feishu.cn/wiki/TOKEN
lark-cli wiki spaces get_node --params '{"token":"WIKI_TOKEN"}'
# 从返回的 node.obj_token 获取真实 doc_id

# docx/doc URL: https://xxx.feishu.cn/docx/DOC_ID
# 直接从 URL 路径提取 DOC_ID
```

### Step 2: 获取文档内容

```bash
lark-cli docs +fetch --doc "<doc_id>" 2>&1 | python3 -c "
import json,sys
d=json.load(sys.stdin)
open('/tmp/doc_original.md','w').write(d['data']['markdown'])
print('Fetched', len(d['data']['markdown']), 'chars')
"
```

### Step 3: 写出并运行 Python 脚本

将以下脚本写到 `/tmp/lark_copywriting.py`（使用 heredoc 或 Write 工具），然后运行：

```bash
python3 /tmp/lark_copywriting.py /tmp/doc_original.md
```

**脚本内容（完整）**：

```python
#!/usr/bin/env python3
import re, sys, json, difflib

PUNCT_MAP = [
    ('\uff0c', ','), ('\u3002', '.'), ('\u3001', ','), ('\uff1a', ':'),
    ('\uff08', '('), ('\uff09', ')'),
    ('\u201c', '"'), ('\u201d', '"'),
    ('\uff1f', '?'), ('\uff1b', ';'), ('\uff01', '!'),
    ('\u2014\u2014', '--'), ('\u2014', '-'),
]

CODE_PATTERNS = {
    'sql':  re.compile(r'^(CREATE|SELECT|INSERT|UPDATE|DELETE|ALTER|DROP|--\s)', re.I),
    'json': re.compile(r'^\s*[{\[]'),
    'bash': re.compile(r'^(curl|npm|pip|git|docker|make|cd|ls|cat)\b'),
}

def fix_line(line):
    stripped = line.strip()
    if stripped.startswith('<image ') or stripped.startswith('```'):
        return line
    for src, dst in PUNCT_MAP:
        line = line.replace(src, dst)
    # 顺序关键: 先去标点前空格，再补标点后空格
    line = re.sub(r'\s+([,.:;!?])(?![-/])', r'\1', line)
    line = re.sub(r'(?<![0-9/\s]),(?=[^\s\n,])', ', ', line)
    line = re.sub(r'(?<![0-9/\s\.])\.(?=[\u4e00-\u9fffA-Z])', '. ', line)
    line = re.sub(r'[?!](?=[\u4e00-\u9fff\u0041-\u005A])', lambda m: m.group(0)+' ', line)
    line = re.sub(r':(?!//|[0-9])(?=[^\s\n])', ': ', line)
    line = re.sub(r'(?<=[^\s\-])--(?=[^\s\-])', ' -- ', line)
    line = re.sub(r'(?<!\n)  +', ' ', line)
    return line

def detect_code_candidates(lines):
    candidates = []
    in_code = False
    run_start = None
    run_lang = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('```'):
            in_code = not in_code
            if run_start is not None:
                if i - run_start >= 3:
                    candidates.append({'start': run_start, 'end': i-1,
                                       'lang': run_lang, 'preview': lines[run_start][:80].strip()})
                run_start = None
            continue
        if in_code:
            continue
        matched_lang = None
        for lang, pat in CODE_PATTERNS.items():
            if pat.match(stripped):
                matched_lang = lang
                break
        if matched_lang:
            if run_start is None:
                run_start, run_lang = i, matched_lang
            elif matched_lang != run_lang:
                if i - run_start >= 3:
                    candidates.append({'start': run_start, 'end': i-1,
                                       'lang': run_lang, 'preview': lines[run_start][:80].strip()})
                run_start, run_lang = i, matched_lang
        else:
            if run_start is not None:
                if i - run_start >= 3:
                    candidates.append({'start': run_start, 'end': i-1,
                                       'lang': run_lang, 'preview': lines[run_start][:80].strip()})
                run_start = None
    return candidates

def process(src_path):
    with open(src_path, encoding='utf-8') as f:
        original_lines = f.readlines()
    fixed_lines = []
    in_code = False
    for line in original_lines:
        stripped = line.strip()
        if stripped.startswith('```'):
            in_code = not in_code
            fixed_lines.append(line)
        elif in_code or stripped.startswith('<image '):
            fixed_lines.append(line)
        else:
            fixed_lines.append(fix_line(line.rstrip('\n')) + '\n')
    with open('/tmp/doc_fixed.md', 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    diff = list(difflib.unified_diff(
        original_lines, fixed_lines, fromfile='original', tofile='fixed', lineterm=''))
    with open('/tmp/doc_diff.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(diff))
    candidates = detect_code_candidates([l.rstrip('\n') for l in original_lines])
    with open('/tmp/code_candidates.json', 'w', encoding='utf-8') as f:
        json.dump(candidates, f, ensure_ascii=False, indent=2)
    changed = sum(1 for d in diff if d.startswith('-') and not d.startswith('---'))
    print(f"Changed: {changed} lines | Code candidates: {len(candidates)}")
    for c in candidates:
        print(f"  [{c['lang']}] lines {c['start']}-{c['end']}: {c['preview']}")

if __name__ == '__main__':
    src = sys.argv[1] if len(sys.argv) > 1 else '/tmp/doc_original.md'
    process(src)
```

### Step 4: 读取结果，展示摘要

```bash
# 读取 diff 统计
python3 -c "
lines = open('/tmp/doc_diff.txt').readlines()
changed = [l for l in lines if l.startswith('-') and not l.startswith('---')]
examples = []
for i,l in enumerate(lines):
    if l.startswith('-') and not l.startswith('---') and i+1 < len(lines) and lines[i+1].startswith('+'):
        examples.append((l.strip()[1:], lines[i+1].strip()[1:]))
    if len(examples) >= 3: break
print(f'变更行数: {len(changed)}')
for old,new in examples:
    print(f'  \"{old}\" → \"{new}\"')
"

# 读取代码候选
cat /tmp/code_candidates.json
```

向用户展示摘要，例如：
> 将修改 42 处标点，检测到 2 处未包裹代码块（sql: lines 54-91, bash: lines 130-139）。
> 示例变更：`做完。下一步` → `做完. 下一步`
> 
> 确认写入吗？

使用 `AskUserQuestion` 询问用户。**如果 diff 为空且无候选**，告知"文档无需修改"，退出。

### Step 5: 用户确认后 — 逐段写回

**分段策略**：以 `<image token=` 行为天然分隔符，将文档切成若干段。每段独立调用 `replace_range`。

```python
import subprocess, json, re

def split_by_image(text):
    """按 <image token= 行分割，每段首行作为选区起点，image 行随前段。"""
    lines = text.split('\n')
    segments = []
    current = []
    for line in lines:
        if line.strip().startswith('<image ') and current:
            current.append(line)
            segments.append('\n'.join(current))
            current = []
        else:
            current.append(line)
    if current:
        segments.append('\n'.join(current))
    return segments

original = open('/tmp/doc_original.md', encoding='utf-8').read()
fixed    = open('/tmp/doc_fixed.md',    encoding='utf-8').read()

orig_segs  = split_by_image(original)
fixed_segs = split_by_image(fixed)

doc_id = '<DOC_ID>'  # 替换为实际 doc_id
success, fail = 0, 0

for i, (orig_seg, fixed_seg) in enumerate(zip(orig_segs, fixed_segs)):
    if orig_seg == fixed_seg:
        continue  # 无变更，跳过

    # 构建 selection：取原始段的首尾各15字符
    orig_lines = [l for l in orig_seg.strip().split('\n') if l.strip() and not l.strip().startswith('<image ')]
    if not orig_lines:
        continue
    first_line = orig_lines[0][:50].strip()
    last_line  = orig_lines[-1][-50:].strip() if len(orig_lines) > 1 else ''

    if last_line and first_line != last_line:
        selection = f"{first_line}...{last_line}"
    else:
        selection = first_line

    # segment_to_markdown: 段内用 \n\n 分隔段落
    para_lines = [l for l in fixed_seg.split('\n') if l.strip()]
    markdown = '\n\n'.join(para_lines)

    result = subprocess.run(
        ['lark-cli', 'docs', '+update',
         '--doc', doc_id,
         '--mode', 'replace_range',
         '--selection-with-ellipsis', selection,
         '--markdown', markdown],
        capture_output=True, text=True
    )
    resp = json.loads(result.stdout) if result.stdout.strip().startswith('{') else {}
    if resp.get('data', {}).get('success'):
        success += 1
    else:
        fail += 1
        print(f"Segment {i} FAILED: {result.stdout[:200]}")

print(f"\n完成: {success} 段成功, {fail} 段失败")
```

---

## 关键约束

| 约束 | 原因 |
|------|------|
| `\n\n` 分隔替换内容段落 | 单 `\n` 在 lark-doc 中是软换行，会合并段落 |
| `<image token>` 行原样保留 | image block 无法通过文本替换重建 |
| 已有 ` ``` ` 行跳过 | 已有代码块不重复包裹 |
| subprocess 传参，不走 shell | `@file` 只接受相对路径；复杂内容经 shell 引号易出错 |
| PUNCT_MAP 用 Unicode escape | shell heredoc 中直接写弯引号可能编码丢失 |
| 先去标点前空格，再补标点后空格 | 顺序错误导致 `做 .下一步` 无法正确处理为 `做. 下一步` |

---

## 错误处理

- **wiki token 解析失败**：提示用户"请检查 URL 格式，wiki 链接需要 `/wiki/TOKEN` 格式"
- **diff 为空 + 无候选**：告知"文档无需修改"，退出
- **replace_range 失败**：报告具体段落索引和错误信息，其余段落继续执行
- **doc_id 解析失败**：要求用户提供文档 token 或重新粘贴 URL
````

- [ ] **Step 3: Verify frontmatter is valid**

```bash
python3 -c "
import re
content = open(r'$HOME/.claude/skills/lark-doc-copywriting/SKILL.md').read()
m = re.match(r'^---\n(.+?)\n---', content, re.DOTALL)
assert m, 'No frontmatter found'
fm = m.group(1)
assert 'name: lark-doc-copywriting' in fm
assert 'description:' in fm
print('Frontmatter OK')
print('File size:', len(content), 'chars')
"
```

Expected: `Frontmatter OK` + file size > 3000 chars.

- [ ] **Step 4: Commit**

```bash
cd ~/.claude && git add skills/lark-doc-copywriting/SKILL.md && git status
# If no git repo at ~/.claude, skip commit — the file exists and is ready
echo "Skill file written"
```

---

### Task 3: End-to-End Smoke Test

**Goal:** Verify the skill works on a real Feishu document (read-only test: fetch + run script + show diff, without writing back).

**Files:**
- No new files; uses the skill created in Task 2

- [ ] **Step 1: Fetch a real document**

Use any available Feishu doc URL. If you have `G184dMQ84oMObjxGDUUcDrX3nBe` from the session:

```bash
lark-cli docs +fetch --doc "G184dMQ84oMObjxGDUUcDrX3nBe" 2>&1 | python3 -c "
import json,sys
d=json.load(sys.stdin)
open('/tmp/doc_original.md','w').write(d['data']['markdown'])
print('Fetched', len(d['data']['markdown']), 'chars')
"
```

- [ ] **Step 2: Run the transform script**

```bash
python3 /tmp/lark_copywriting.py /tmp/doc_original.md
```

- [ ] **Step 3: Verify image lines are preserved in output**

```bash
python3 -c "
orig = open('/tmp/doc_original.md').readlines()
fixed = open('/tmp/doc_fixed.md').readlines()
for i,(o,f) in enumerate(zip(orig,fixed)):
    if '<image' in o:
        assert o == f, f'Line {i} image changed: {repr(o)} -> {repr(f)}'
print('PASS: all image lines preserved')
"
```

- [ ] **Step 4: Verify existing code blocks not in candidates**

```bash
python3 -c "
import json
candidates = json.load(open('/tmp/code_candidates.json'))
orig_lines = open('/tmp/doc_original.md').readlines()
for c in candidates:
    # lines before candidate should not have ``` 
    context_start = max(0, c['start'] - 2)
    pre = orig_lines[context_start:c['start']]
    in_fence = any(l.strip().startswith('\`\`\`') for l in pre)
    assert not in_fence, f'Candidate at {c[\"start\"]} is inside a code fence'
print(f'PASS: {len(candidates)} candidates found, none inside existing fences')
"
```

- [ ] **Step 5: Check diff has meaningful changes**

```bash
python3 -c "
diff = open('/tmp/doc_diff.txt').read()
changed = [l for l in diff.split('\n') if l.startswith('-') and not l.startswith('---')]
print(f'Changed lines: {len(changed)}')
# Show 3 examples
examples = []
lines = diff.split('\n')
for i,l in enumerate(lines):
    if l.startswith('-') and not l.startswith('---') and i+1<len(lines) and lines[i+1].startswith('+'):
        examples.append((l[1:50], lines[i+1][1:50]))
    if len(examples)>=3: break
for old,new in examples:
    print(f'  BEFORE: {old}')
    print(f'  AFTER:  {new}')
"
```

---

## Self-Review Notes

- **Spec coverage**: All 5 success criteria from spec are covered:
  - ✓ SKILL.md exists with valid frontmatter (Task 2 Step 3)
  - ✓ Wiki/docx URL handling (Step 1 of SKILL.md)
  - ✓ Diff shown before write, user confirms (Steps 4-5 of SKILL.md)
  - ✓ Image lines preserved (Task 3 Step 3)
  - ✓ Existing code blocks not double-processed (Task 3 Step 4)
- **No placeholders**: All code blocks are complete
- **Type consistency**: `fix_line`, `detect_code_candidates`, `process`, `split_by_image` — names consistent across tasks
