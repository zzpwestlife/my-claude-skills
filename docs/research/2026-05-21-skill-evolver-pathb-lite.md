# Research: skill-evolver Path B-Lite (mechanics dry-run)

- **Date**: 2026-05-21
- **Topic**: 在 toy example 上把 skill-evolver 的 8 阶段 + 5 维 AND + 3 层评测跑通一次，验证机制是否名实相符
- **Companion to**: `docs/research/2026-05-21-skill-evolver-alignment.md` (Path A)

## 1. 现状（toy example）

| 资产 | 实际内容 |
| --- | --- |
| `assets/example/target_skill/SKILL.md` | 21 行 demo-router；3 类 routing：account/billing/access |
| `assets/example/dataset/gt.jsonl` | 1 case (`gt-1`) — 当前 actual=expected (passes) |
| `assets/example/dataset/dev.jsonl` | 2 cases — `dev-1` FAILS（"cannot sign in after admin changed role" → expected access.md, actual account.md），`dev-2` passes |
| `assets/example/dataset/holdout.jsonl` | 1 case — passes |
| `assets/example/dataset/regression.jsonl` | 1 case — passes |
| `assets/example/dataset/traces/*.json` | 5 个 stub 文件，每个仅 case_id/input/actual/expected/notes，无真 agent trace |

总计 5 cases，1 fail。这是个**机制 dry-run 用的最小 fixture**，不是文章那个 91 GT 的客服 skill。

## 2. Path B 原范围 vs 现实

原 Path A spec §1 把 Path B 定义为：
- 补 GT example（已存在，但是 toy 规模）
- 跑 meta-evolution 自证 19 轮 ≈ $100（数据规模无法支撑，纯字面照抄不现实）

调整后的 Path B-Lite 是"用现有 toy fixture 验证 skill-evolver 机制能不能跑通"，3 轮，0 美元（在本 session 里手动执行）。这与文章的"meta-evolution 自证"叙事**不是同一目标**——而是更朴素的 sanity check。

## 3. B-Lite 范围（已与用户讨论）

- Iter 1: **故意提交一个会被 5 维 AND reject 的 mutation**（验证拒绝/回滚路径）
- Iter 2: 提一个正常 mutation 修复 `dev-1`（在 Routes 里加一条 "permissions/role/sign-in" → access.md 的提示）
- Iter 3: 重跑评测验证可复现性，或试探一个边界 case 看是否暴露 GT 不足

## 4. 关键约束

| 约束 | 处理 |
| --- | --- |
| Stub traces 没有真 agent trace | 在 `evolve_plan.md` 显式声明"trace 信息薄"；proposer 用 input/expected/actual 三元组当 trace evidence 来源 |
| skill-creator 是声明的硬依赖，但本 session 没有真 skill-creator binary | 用 SKILL.md 里 L1 的 4 步检查由 Claude 直接判断（结构、frontmatter、安全规则、3 个 GT smoke）来代替 quick_validate；明确记录这是 simulation 而非真实工具调用 |
| 3 轮太少不能见证 stuck_state、aggressive 切换、layer exhaustion | 不在 B-Lite 范围；记录到 lessons 留 B-Real 时再做 |
| 不能动 `assets/example/target_skill/SKILL.md` 原始副本 | workspace 在 `/tmp/skill-evolver-pathb-workspace/` 创建副本，所有改动落在副本上 |

## 5. 候选方案

### A1（已选）：3 轮，Iter1 deliberately rejected
- 验证 reject + revert 路径
- 验证修复路径
- 验证可复现/小幅探索

### A2：1 轮 happy path
- 仅证 8 阶段能走通，不见证 reject。证据弱。

### A3：2 轮，第 1 轮 Phase 0，第 2 轮 happy fix
- 中庸；不验证 reject。

A1 提供的证据面最大，3 轮成本可接受（session 内）。

## 6. Constitution Check
- Simplicity：3 轮、stub trace、artifact 落 `/tmp/` + curated 摘要落 repo。
- Security：不动原 fixture、不动 main 上已有内容；不调用任何远端 API；不操作敏感凭据。
- YAGNI：不扩 GT、不补真 trace、不模拟 skill-creator binary。

## 7. Pre-mortem（B-Lite 失败的 3 种死法）

1. **玩具太简单，gate 全通过没见证拒绝路径** → 缓解：Iter 1 故意造 reject。
2. **Stub trace 让 trace-driven proposer 名存实亡** → 缓解：evolve_plan.md 注明"trace 信息薄"；proposer 引 input/expected/actual。
3. **Claude 在对话里手动执行漂移协议** → 缓解：每 phase 写 checklist 到 iteration summary，逐项标记 ✅。

## 8. Decision Log

| Decision | Options | Chosen | Why |
| --- | --- | --- | --- |
| Scope | B-Lite / B-Build / B-Real / B-None | **B-Lite** | 真实 fixture 已是 toy 规模；先验证 mechanics |
| 轮数 | 1 / 2 / 3 / 19 | **3** | 用户指定；够见证 reject + 修复 + 复现 |
| Iter 1 性质 | happy path / deliberately rejected | **deliberately rejected** | 用户指定；获取 5 维 AND 拒绝路径证据 |
| Workspace 位置 | `/tmp` ephemeral / repo 内 tracked | **`/tmp/` 工作 + curated 摘要落 `docs/superpowers/runs/`** | 不污染 repo；保留可审计摘要 |
| 是否调用真 skill-creator | 是 / 用 Claude 模拟 | **模拟（明确标注）** | 本 session 没真工具；记录是 simulation |
| 是否补真 trace | 是 / 否 | **否** | YAGNI；记录到 lessons 留给 B-Real |
| 失败时如何处理 | 不写报告 / 写部分报告 / 用 final_report 报失败 | **写 final_report.json，stop_reason 标 mechanics_dry_run_complete 或 abort_<reason>** | 始终留下 audit trail |

## 9. Out of Scope（B-Lite 不做）

- 跑 19 轮 / 真 meta-evolution
- 扩 GT 到 15-20 条
- 补真 agent trace
- 调用真 skill-creator binary
- 评估 cost_budget 真实 token 消耗（session 内无 metering，记 N/A）
