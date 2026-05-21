# Spec: skill-evolver Path B-Lite (mechanics dry-run)

- **Date**: 2026-05-21
- **Status**: pending spec review
- **Companion research**: `docs/research/2026-05-21-skill-evolver-pathb-lite.md`
- **Parent path**: depends on Path A (already merged on `main`)

## 1. Goal & Non-Goals

### Goal
在 toy `assets/example/` fixture 上手动走一次 skill-evolver 的 8 阶段 / 5 维 AND / 3 层评测，3 轮，**Iter 1 故意触发 reject + revert，Iter 2 修复 dev-1，Iter 3 复现/探索**。产出齐全的 audit artifacts（`baseline.json`、`evolve_plan.md`、`results.tsv`、`experiments.jsonl`、`iterations/`、`final_report.json`），并把 curated 摘要落到 `docs/superpowers/runs/2026-05-21-pathb-lite/`。

### Non-Goals
- 不跑 19 轮、不扩 GT、不补真 trace、不调用真 skill-creator
- 不衡量真实 token cost（本 session 无 metering）
- 不试图复现文章的 0-rollback 叙事
- 不修改 `assets/example/` 原始 fixture
- 不修改 `main` 上 Path A 已有内容（除 lessons.md 追加一条）

## 2. Acceptance Criteria

| # | 断言 | 验证方式 |
| --- | --- | --- |
| AC1 | workspace 在 `/tmp/skill-evolver-pathb-workspace/` 存在；含 target_skill/SKILL.md 副本 | `ls` |
| AC2 | `baseline.json` 写入；含 dev/holdout/regression pre-iter pass rate | `jq` 读取 |
| AC3 | `evolve_plan.md` 写入；声明 simulation 状态、trace 薄注释、3 轮预算 | grep |
| AC4 | Iter 1：5 维 AND 至少一维 fail；`git revert HEAD` 或 file snapshot rollback 被记录到 `iterations/iter-1.md` | iteration summary diff |
| AC5 | Iter 1 后 workspace SKILL.md 副本与 baseline 一致（rollback 生效） | `diff` |
| AC6 | Iter 2：dev-1 从 fail 变 pass；其他 4 case 不退步；5 维 AND 全 pass；mutation 被 keep | results.tsv 行 |
| AC7 | Iter 3：dev/holdout/regression 全 pass；要么稳定复现要么发现新问题，并写入 iter-3 summary | iteration summary |
| AC8 | `results.tsv` 至少 3 行（每轮一行，含 keep/discard 标记） | `wc -l` |
| AC9 | `experiments.jsonl` 至少 3 条 JSON 记录 | `wc -l` |
| AC10 | `iterations/iter-{1,2,3}.md` 各含 8 个 phase checklist，每项标记 ✅ 或 N/A | grep "Phase" 计数 |
| AC11 | `final_report.json` 含 `stop_reason`、`best_checkpoint`、`kept_count`=2、`discarded_count`=1（除非 Iter 3 也 discard）、`gate_pass_rates`、`dataset_performance`、`artifact_locations`、`next_recommendation` | `jq` 字段断言 |
| AC12 | `docs/superpowers/runs/2026-05-21-pathb-lite/SUMMARY.md` 在 repo 内提交，含 3 轮 verdict + 关键 artifact 节选 + 经验教训 | 文件存在 + commit |

## 3. 文件改动清单

| 路径 | 类型 | 责任 |
| --- | --- | --- |
| `/tmp/skill-evolver-pathb-workspace/target_skill/SKILL.md` | 工作副本（ephemeral） | 唯一被 mutate 的 SKILL.md |
| `/tmp/skill-evolver-pathb-workspace/dataset/*.jsonl` | 副本 | dev/holdout/regression 评测数据 |
| `/tmp/skill-evolver-pathb-workspace/baseline.json` | ephemeral | Phase 0 产物 |
| `/tmp/skill-evolver-pathb-workspace/evolve_plan.md` | ephemeral | Phase 0 产物 |
| `/tmp/skill-evolver-pathb-workspace/results.tsv` | ephemeral | 每轮一行 |
| `/tmp/skill-evolver-pathb-workspace/experiments.jsonl` | ephemeral | 每轮一条 |
| `/tmp/skill-evolver-pathb-workspace/iterations/iter-{1,2,3}.md` | ephemeral | 8-phase checklist + verdict |
| `/tmp/skill-evolver-pathb-workspace/.skill_evolve/traces/iter-{1,2,3}/...` | ephemeral | iteration trace |
| `/tmp/skill-evolver-pathb-workspace/final_report.json` | ephemeral | 终报 |
| `docs/superpowers/runs/2026-05-21-pathb-lite/SUMMARY.md` | **tracked**, new | 3 轮总结 + 节选 + lessons |
| `docs/superpowers/runs/2026-05-21-pathb-lite/baseline.json` | **tracked**, copy | 关键 artifact 留存 |
| `docs/superpowers/runs/2026-05-21-pathb-lite/final_report.json` | **tracked**, copy | 关键 artifact 留存 |
| `docs/superpowers/runs/2026-05-21-pathb-lite/iterations/iter-{1,2,3}.md` | **tracked**, copy | 留存 audit 用 |
| `.claude/lessons.md` | 追加一条 lesson | "不能在 stub trace 上断言 trace-driven 协议有效；需 B-Real 时补真 trace" |

## 4. 三轮剧本（执行细节）

### Iter 1 — Deliberately rejected mutation

**Goal**: 验证 5 维 AND 真的能拒绝坏 mutation。

**Mutation proposal**:
- `target_layer`: layer1 (trigger/SKILL.md)
- 但 mutation 同时改 SKILL.md **和** target_skill 同目录下另一 reference 文件 → 跨 layer，应触发 `atomic_auditability` fail
- counterfactual: "Case dev-1 失败因为路由表里没 permissions 提示；如果改 routes + 引用 manual，应该路由到 access.md。"

**Expected gate verdict**:
- `structure_and_safety`: pass (无 critical 安全发现)
- `dev_quality`: 即便 mock 评测显示 dev-1 通过，仍因 atomic 维度连带 discard
- `strict_quality`: pass (provisional)
- `cost_budget`: pass
- **`atomic_auditability`: FAIL**（跨 layer）→ 整体 discard

**Action**: rollback workspace SKILL.md 到 baseline；记录 `iter-1.md` verdict=DISCARD reason=atomic_violation。

### Iter 2 — Atomic fix for dev-1

**Mutation proposal**:
- `target_layer`: layer1
- 仅修改 workspace target_skill SKILL.md 的 Routes 段，加一行：
  > `- Permission, role change, and sign-in failure questions route to docs/access.md.`
- counterfactual: "Case dev-1 失败因 'cannot sign in after admin changed role' 没匹配到 access 路由；加 permissions/role/sign-in 提示行后，路由器应改判 access.md。"

**Expected gate verdict**:
- 5 维全 pass → keep；commit checkpoint。

**Verify**:
- dev-1 由 fail → pass
- dev-2、gt-1、holdout-1、reg-1 不退步

### Iter 3 — Reproducibility / probe

**Goal**: 验证 Iter 2 改动不是侥幸。

**Action**: 不再做 mutation；仅 re-run L2 dev eval 一次（simulation N=1，因为玩具确定性）；追加一行 "verification only" 到 results.tsv；写 `iter-3.md`，verdict=PROBE。

**Alternative**: 如果重跑发现新边界（如某个看起来合理的输入 routing 模糊），把它记入 lessons 而不立刻 mutate。

## 5. 协议简化清单（必要 simulations 的合规边界）

由于本 session 不能调用真 skill-creator binary，下列代理必须**显式标注**：

| 真协议要求 | B-Lite 代理 | 标注位置 |
| --- | --- | --- |
| `quick_validate` (skill-creator) | Claude 直接读 SKILL.md frontmatter + 按 `references/safety-rules.md` 11 条人工扫一遍 | `evolve_plan.md` simulations 节 |
| `grader` (skill-creator) | Claude 按 dataset assertion type 直接判 contains | `evolve_plan.md` |
| `comparator` (skill-creator) | 不跑（B-Lite 不做 blind A/B） | `evolve_plan.md` |
| `eval.repeat_n=3` | N=1（玩具确定性） | `evolve_plan.md` |
| `cost_budget` 真 token 计数 | 标 `N/A: session-mode metering unavailable` | `final_report.json` |
| `trace_path` 引用真 agent trace | 引用 stub trace + input/expected/actual 三元组 | 每个 iteration summary |

simulation 的代理不影响 mechanics 验证（gate 决策、rollback、artifact schema），但确实降低真实评测信度。final_report.json 必须显式记录这一点。

## 6. 验证（Verification Plan）

每轮写完 iteration summary 后立即验证：

1. iteration summary 含全部 8 个 phase 的 checklist
2. results.tsv 添了恰好一行
3. experiments.jsonl 添了恰好一条
4. 如果是 keep：workspace SKILL.md diff 与 mutation 描述吻合
5. 如果是 discard：workspace SKILL.md 与上一 keep checkpoint 一致

最终 sweep：
- AC1-AC12 逐条 grep / diff / jq
- 把 baseline.json、final_report.json、3 个 iteration summary copy 到 `docs/superpowers/runs/2026-05-21-pathb-lite/`
- 写 SUMMARY.md
- 在 lessons.md 追加经验

## 7. Risk Register

| 风险 | 概率 | 影响 | 缓解 |
| --- | --- | --- | --- |
| 故意制造的"跨 layer" mutation 在玩具上 gate 实际照过 | 中 | 中 | Plan 写明判定细则；如真照过，把 mutation 改成"动 2 个文件且无 target_files pattern 声明"以确保 atomic 维度 fail |
| dev-1 的修复行写错路由词，反而引入新失败 | 低 | 低 | Iter 2 verify 阶段对 5 个 case 都跑一遍 |
| `/tmp` 在某些环境（如 macOS sandboxed）不可写 | 低 | 中 | 退路：用 `~/.skill-evolver-pathb-workspace/` |
| 漂移：跳过 phase | 中 | 中 | 每个 iteration summary 强制 8 个 phase 行 |
| Claude 默认认为"可以省 trace 引用"再次违规 | 中 | 低 | 每 phase 显式写 trace_evidence 字段 |

## 8. Open Questions

- Q1: lessons.md 的追加位是放 "Mistake/Impact/Rule/Where" 还是写成纯观察？倾向：纯观察+Rule（保持 lessons 体例）。
- Q2: SUMMARY.md 是否要含 ASCII 流程图？倾向：不需要，文字够。
- Q3: `git revert` 在 ephemeral workspace 是用 `git init` + 真 commit/revert，还是用 file snapshot？倾向：workspace 内做真 git（Phase 0 step 4 的 git state detection 路径才被走过）。

## 9. Decision Log

| Decision | Options | Chosen | Why |
| --- | --- | --- | --- |
| 范围 | B-Lite / B-Build / B-Real / B-None | **B-Lite** | toy 已是真实 fixture；先验机制 |
| 轮数 | 1/2/3 | **3** | 用户指定 |
| Iter 1 性质 | happy / deliberately rejected | **rejected** | 取得 reject 路径证据 |
| Iter 1 触发哪一维 fail | `atomic_auditability` 跨 layer / `cost_budget` 故意超支 / `structure_and_safety` 故意写危险 cmd | **atomic_auditability 跨 layer** | 最自然、零安全风险、与 Path A G7 改动呼应 |
| Iter 3 是否再 mutate | yes / no probe-only | **no probe-only** | YAGNI；3 轮内重点是 reject+fix |
| Workspace 位置 | `/tmp` / `~/.skill-evolver-pathb-workspace` / repo 内 | **`/tmp`** | 默认；环境不允许时降级 |
| Workspace VCS | true git init / file snapshot | **true git init** | 让 SKILL.md Phase 0 git detection 走真路径 |
| simulation 标注 | inline 注释 / 集中 evolve_plan.md 节 / final_report 节 | **集中 evolve_plan + final_report 双标注** | audit 上下游都看得见 |
| 跟踪到 repo 的 artifacts | 无 / 仅 SUMMARY / 含 baseline+final+iterations | **含 baseline+final+iterations** | 留可复盘证据 |
