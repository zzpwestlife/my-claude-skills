# Spec: skill-evolver Path A Optimization

- **Date**: 2026-05-21
- **Status**: Approved scope (Path A=do, Path B=defer), pending spec review
- **Approach**: P1 外科手术式（surgical edits）
- **Companion research**: `docs/research/2026-05-21-skill-evolver-alignment.md`

## 1. Goal & Non-Goals

### Goal
让 `skill-evolver/SKILL.md` 与原文《让 Skill 自己训练自己》描述的核心机制达成"可断言级别"对齐，同时把 SKILL.md 行数压回项目硬规 < 200 行以下，且不破坏当前任何契约语句（5 维 AND、8 阶段 Loop、3 层 Mutation、3 层 Evaluation、Stop Rules、Aggressive 策略）。

### Non-Goals（推迟到 Path B 或永久不做）
- 创建 `assets/example/` GT 样例数据
- 跑 meta-evolution 自证 19 轮
- 重写 README/QUICKSTART/FAQ 全文
- 改 `scripts/*.py` 既有逻辑（除非 safety 规则要求新字段）

## 2. Acceptance Criteria（如何判断"做完了"）

| # | 断言 | 验证方式 |
| --- | --- | --- |
| AC1 | `SKILL.md` ≤ 200 行 | `wc -l skill-evolver/SKILL.md` |
| AC2 | `SKILL.md` 顶部存在 Dependencies 节，明确列出 skill-creator 与 git | grep |
| AC3 | `SKILL.md` 存在 "Eval Noise" 小节，说明重复采样策略 | grep "Eval Noise" |
| AC4 | `references/safety-rules.md` 存在，列 11 条规则，区分 critical/warning | 文件存在 + 行数检查 |
| AC5 | `references/mutation-layers.md` 存在；SKILL.md 中 Mutation Layers 节缩成单段引用 | 文件 diff |
| AC6 | `references/evaluation-layers.md` 存在；SKILL.md 中 Evaluation Layers 节缩成单段引用 | 文件 diff |
| AC7 | `references/eval-noise.md` 存在 | 文件存在 |
| AC8 | `references/dataset-format.md` 增加 "GT 生成"段，引导用 skill-creator | grep |
| AC9 | Atomic 判定从"≤1 文件"改为"默认 1，pattern 显式声明可放宽到 ≤5" | grep + diff |
| AC10 | 所有原 invariant 语句仍然在文档中存在（5 维 AND 关键词、8 阶段名、3 层 mutation 名） | grep 检查 |
| AC11 | `python3 scripts/check_skill_package.py . --json` 通过 | 脚本退出码 0 |

## 3. 文件改动清单（File-Level Plan）

| 文件 | 改动 | 估算变化 |
| --- | --- | --- |
| `skill-evolver/SKILL.md` | 提取 Mutation Layers / Evaluation Layers 详规到 references；新增 Dependencies、Eval Noise、Safety Rules 引用段；调整 Atomic 判定描述；行数压到 ≤ 200 | -80 ~ -100 行 |
| `skill-evolver/references/mutation-layers.md` | **新建** | +50 行左右 |
| `skill-evolver/references/evaluation-layers.md` | **新建** | +80 行左右 |
| `skill-evolver/references/safety-rules.md` | **新建**：11 条规则，2 条 critical 标 ★，9 条 warning | +50 行左右 |
| `skill-evolver/references/eval-noise.md` | **新建**：N≥3 重复采样、方差阈值、何时 re-eval | +30 行左右 |
| `skill-evolver/references/dataset-format.md` | 补 "GT 生成（用 skill-creator）" 一节 | +15 行 |
| `skill-evolver/README.md` | 补一行 design rationale 引用 meta-evolution 自证 | +2~3 行 |
| `skill-evolver/scripts/check_skill_package.py` | 校验新增 reference 文件存在 | +5~10 行（仅必要时） |

> 不在改动范围：`scripts/setup_workspace.py`、`scripts/validate_dataset.py`、`FAQ.md`、`QUICKSTART.md`、`PACKAGING.md`、`RELEASE.md`、`agents/`、`assets/`、`test-prompts.json`。

## 4. SKILL.md 结构（修改后）

```
---
name: skill-evolver
description: ...（保留原文）
---

# Skill Evolver

简介段（保留）。

## Dependencies              ← 新
- skill-creator (hard): quick_validate / grader / comparator / GT generation
- git (preferred for checkpointing; falls back to file snapshot if unavailable)

## Inputs                    （保留）

## Phase 0: Setup            （保留，可微调一句话）

## Operator Checkpoints      （保留）

## Self-Contained Bundle Checks  （保留）

## Iteration Loop            （保留：Review→Ideate→Modify→Commit→Verify→Gate→Log→Loop）
- Review                     （保留含 5 信号）
- Ideate                     （保留 counterfactual 强制；Atomic 判定改写见 §5）
- Modify
- Commit
- Verify
- Gate                       （保留 5 维 AND，含原阈值）
- Log
- Loop                       （保留 Aggressive 策略与 layer exhausted 三条件）

## Mutation Layers           （瘦身：保留契约性一段，详细规则指向 references/mutation-layers.md）

## Evaluation Layers         （瘦身：保留契约性一段，详细规则指向 references/evaluation-layers.md）

## Eval Noise Mitigation     ← 新（短，约 6-10 行）
- Repeat L2/L3 evaluation N≥3 times for any iteration that crosses a gate boundary
- Record per-run scores and variance in `experiments.jsonl`
- If variance exceeds plan-defined threshold, mark "noisy" and prefer median over mean
- Refer to `references/eval-noise.md` for detailed protocol

## Safety Rules              ← 新（短，约 4-6 行）
- L1 quick guard checks 11 safety rules (2 critical, 9 warning)
- Critical findings cause immediate L1 fail; warnings are recorded for Ideate
- Full list in `references/safety-rules.md`

## Stop Rules                （保留）

最终 final_report.json schema   （保留）
```

## 5. 关键文本变更（Atomic 判定调和）

**当前**（SKILL.md `Gate` 段）：
> `atomic_auditability`: pass only when the mutation stays within one declared layer, **touches no more than one file** unless `target_files` explicitly allowed a pattern, and ...

**改为**：
> `atomic_auditability`: pass only when the mutation stays within one declared layer, **touches no more than one file by default; up to 5 files when `target_files` explicitly declares a pattern (e.g. all references in a folder)**, and the iteration summary, traces, and checkpoint path are all present.

唯一语义改动是把"上限"显式化（默认 1，pattern 时 ≤5），与文章"git diff --stat 超过 5 文件大概率不是原子的"对齐，同时不破坏现有 gate 逻辑。

## 6. 新增 references 文件大纲

### `references/safety-rules.md`
- 章节：Critical (★)、Warning
- 11 条规则草案（落地用，可被 L1 脚本扫描）：
  - ★ R1: rm -rf / 危险删除指令出现在脚本或 SKILL.md
  - ★ R2: 硬编码 API key / token / secret pattern
  - R3: 硬编码绝对路径（/Users/、/home/ 等）
  - R4: 直接修改 git config / 全局 git 状态
  - R5: 网络请求未限定域（curl/wget 任意 URL）
  - R6: shell 中 `eval` / 动态构造命令字符串
  - R7: 跨 layer 的 file pattern（layer1 改 scripts/）
  - R8: SKILL.md 缺 frontmatter 必需字段
  - R9: description 字段超长（影响 Claude trigger）
  - R10: 改写 baseline.json / evolve_plan.md 之外的 audit artifact
  - R11: 无 trace 引用却产出 mutation proposal
- 每条给出：检测方式（grep/AST）、failure level、修复指引

### `references/mutation-layers.md`
- 三层完整定义、跨层禁止规则、何时升级、何时回退
- 每层 1 个 do/don't 例子

### `references/evaluation-layers.md`
- L1 4 件事详细列表
- L2 8 种 assertion 详细语义
- L3 触发条件 + holdout/regression 集职责 + 可选 blind A/B

### `references/eval-noise.md`
- 噪声来源（temperature/sampling/instruction drift）
- 重复采样 N 默认 3，可在 evolve_plan.md 调整
- 方差阈值默认 0.05，可调
- 何时触发 re-eval：跨 gate 边界（dev_quality 接近门槛、strict_quality 触发 L3 前）
- 与成本预算的取舍：N=3 把 L2 成本三倍，但避免误判 keep/discard

## 7. 验证（Verification Plan）

执行顺序（每步都要有证据）：
1. 改动完成后跑 `wc -l skill-evolver/SKILL.md` → 必须 ≤ 200
2. 跑 `python3 skill-evolver/scripts/check_skill_package.py skill-evolver --json` → 必须退出码 0
3. 跑 `python3 skill-evolver/scripts/validate_dataset.py skill-evolver/assets/example/dataset --json` → 已知会失败（assets 空，Path B 范畴），记录但不阻塞
4. 对所有 AC1~AC11 用 `grep` / `wc` 逐条验证，附输出
5. `git diff --stat` 总改动文件数应在 6~8 之间，单个新文件 ≤ 100 行

## 8. Risk Register

| 风险 | 概率 | 影响 | 缓解 |
| --- | --- | --- | --- |
| 提取过程意外改变契约语义 | 中 | 高 | 用 grep 对比"提取前/后"关键短语，变更前先记 baseline grep 列表 |
| 新增 references 太多增加阅读负担 | 低 | 中 | SKILL.md 中明确"按需读取"指引，不放进每轮必读 |
| safety-rules 11 条无脚本兜底变成空文 | 中 | 低 | 本轮先列规则，落地脚本作为后续工作记录到 lessons.md |
| `scripts/check_skill_package.py` 改动引入回归 | 低 | 中 | 改动前先跑一次记录输出，改动后对比 |
| 文章营销描述被机械搬入（违反 YAGNI） | 中 | 中 | 每个新增条目必须出现在 AC 列表，否则不写 |

## 9. Open Questions（写实现 plan 时再敲定）

- Q1: SKILL.md 中"Mutation Layers"瘦身后是否保留每层一句话定义？倾向：保留（契约必要）
- Q2: `safety-rules.md` 中规则 ID 是否在 `experiments.jsonl` 里 reference？倾向：作为 finding 字段记录，不强制 ID
- Q3: Eval Noise 的 N=3 是写死 default 还是只在 evolve_plan.md 默认？倾向：SKILL.md 写 "≥3 default; configurable in evolve_plan.md"

## 10. Decision Log

| Decision | Options | Chosen | Why |
| --- | --- | --- | --- |
| 范围 | A only / B / A→B / report-only | **A→B** | 用户选 C，先锁 A 收益 |
| 执行风格 | P1/P2/P3 | **P1 surgical** | 保住 invariant + 满足 <200 行 + 控 churn |
| 提取目标 | 全 SKILL.md 重写 / 仅 Mutation+Eval Layers 提取 / 不提取 | **仅提取 2 个详规节** | 这两节是行数最大且最适合按需读取的部分 |
| Atomic 判定 | 保留 ≤1 / 改 ≤5 / 改 "默认 1，pattern 时 ≤5" | **第三选项** | 与原契约 + 文章 + 实际 references 改动场景同时兼容 |
| 11 条 safety 规则 | 全写脚本 / 只写文档 / 文档+脚本桩 | **本轮只写文档** | 落地脚本属下一阶段，避免本轮范围爆炸；脚本桩作 lessons 记录 |
| GT 生成路径 | SKILL.md 内联 / 仅 references / 不提 | **仅 references** | 避免 SKILL.md 膨胀，保留按需读取语义 |
| Meta-evolution 自证引用位置 | SKILL.md / README / 不引 | **README 一行** | 它是 design rationale 不是契约，避免 SKILL.md 含市场叙事 |
