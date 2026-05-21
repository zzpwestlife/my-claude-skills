# Research: skill-evolver 与原文对齐分析

- **Date**: 2026-05-21
- **Topic**: 把 `skill-evolver/SKILL.md` 与《让 Skill 自己训练自己：8 阶段 Loop、3 层评测、5 维 AND 门控》一文对照，识别 gap 与改进项
- **Author**: Claude (Opus 4.7) under Principal Engineer protocol
- **Decision scope**: 本轮只做 Path A（静态对齐 + SKILL.md 优化），Path B（补 GT 样例 + 跑 meta-evolution）等 A 完成后再定

## 1. 现状（Inventory）

| 路径 | 行数 | 用途 |
| --- | --- | --- |
| `skill-evolver/SKILL.md` | 239 | 主契约（违反项目 < 200 行硬规） |
| `skill-evolver/references/artifacts.md` | 66 | artifacts 落盘格式 |
| `skill-evolver/references/dataset-format.md` | 37 | GT/dev 数据格式说明 |
| `skill-evolver/references/distribution.md` | 30 | 打包/分发说明 |
| `skill-evolver/references/runbook.md` | 20 | 完整流程参考 |
| `skill-evolver/scripts/check_skill_package.py` | 89 | 包结构 smoke check |
| `skill-evolver/scripts/setup_workspace.py` | 131 | Phase 0 deterministic helper |
| `skill-evolver/scripts/validate_dataset.py` | 87 | 数据集校验 |
| `skill-evolver/assets/` | — | **空目录**：QUICKSTART 提到的 example 不存在 |
| `skill-evolver/test-prompts.json` | — | 3 条用于人工抽查的 prompt（非 GT 格式） |

## 2. 文章核心机制清单（用作 alignment 基准）

1. **Phase 0 Setup**：检测 SKILL.md/git/GT，自动产出 `evolve_plan.md` + `baseline.json`
2. **8 阶段每轮 Loop**：Review → Ideate → Modify → Commit → Verify → Gate → Log → Loop
3. **Review 提取 5 信号**：successful/failed patterns、persistent failures、regression guards、stuck state
4. **Ideate 强制 counterfactual**：必须引用 trace 证据写出"Case X 失败因 Y，改 Z 期望 W"
5. **Modify 原子化**：一句话测试，不允许"和"字
6. **3 层评测 L1/L2/L3**：硬规 → 全量 dev → holdout/regression
7. **L1 内含 11 条安全规则**（文章说，2 条 critical 直接阻断）
8. **L2 8 种 assertion**：6 程序判 + 2 LLM YES/NO（contains, not_contains, regex, path_hit, json_field, script_check, fact_coverage, llm_judge）
9. **L3 触发条件**：每 N 轮、dev pass_rate 过阈值、层晋升前
10. **5 维 AND 门控**：structure_safety, dev_quality, strict_quality, cost_budget, atomic_auditability
11. **3 层 Mutation**：Layer 1 trigger / Layer 2 body / Layer 3 scripts/refs，不准跨层
12. **Aggressive 策略**：5 次 discard 后切换，强制 L3 验证
13. **Trace 驱动诊断**：proposer 拿到的是 trace path，不是 prompt 塞 trace
14. **LLM 评测噪声**：同状态同 GT 跑 4 次会在 0.79~0.92 漂移，需要重复采样
15. **GT 生成路径**：可借用 skill-creator 的 eval 功能自动生成
16. **skill-creator 是硬依赖**：quick_validate + grader + comparator + GT 生成 全套使用

## 3. Gap 分析（按"是否可写成可测断言"过滤）

| ID | Gap | 影响 | 是否可断言 | 处理 |
| --- | --- | --- | --- | --- |
| G1 | LLM 评测噪声完全没提 | 高 | ✅（"重复采样 N≥3，记录方差，方差> X 触发 re-eval"） | SKILL.md 加 "Eval Noise Mitigation" 小节 |
| G2 | L1 safety 只列 4 项示例 | 中-高 | ✅（11 条具体规则可写脚本） | 抽到 `references/safety-rules.md` |
| G3 | skill-creator 硬依赖未声明 | 中-高 | ✅（缺工具时 Phase 0 报错） | SKILL.md 头部加 Dependencies |
| G4 | GT 生成路径未提 | 中 | ✅（Phase 0 检查 GT 缺失时给指引） | references/dataset-format.md 补一节 |
| G5 | `assets/example/` 空目录 | 中 | — | **Path B 范畴，本轮不做** |
| G6 | SKILL.md 239 行超 200 行硬规 | 中 | ✅（行数检查） | 提取 Mutation/Evaluation Layers 详规到 references |
| G7 | Atomic 判定与文章不一致（≤1 vs ≤5） | 低-中 | ✅（gate 中条件已可表达） | 改写为"默认 1，target_files 显式 pattern 时 ≤5" |
| G8 | Meta-evolution 自证未引用 | 低 | — | README/SKILL.md 一句 design rationale |

## 4. 候选方案（已与用户讨论）

### Approach P1: 外科手术（**已选**）
- 仅"加"和"挪"，不"删"或"改写"既有 invariant
- 提取 Mutation Layers / Evaluation Layers 详细规则到 `references/mutation-layers.md` 和 `references/evaluation-layers.md`
- SKILL.md 内只保留契约式概念引用（≤200 行）
- 新增 `references/safety-rules.md`（11 条规则）
- 新增 `references/eval-noise.md`（噪声缓解策略）
- 在 SKILL.md 顶部加 Dependencies 节
- 影响约 5-6 个文件，±300 行
- 风险：低（不破坏 5 维 AND/8 阶段/3 层 mutation 等核心契约）

### Approach P2: 全面重构（未选）
- 重写 SKILL.md 为契约骨架，所有详规移走，重做 README/QUICKSTART/FAQ
- 风险：高（可能打破 operator checkpoints、 aggressive 策略等子契约）

### Approach P3: 只动 SKILL.md 内联（未选）
- SKILL.md 进一步膨胀，违反 < 200 行硬规

## 5. Constitution Check
- **Simplicity First**：P1 通过提取详规到 references 来缩小 SKILL.md，本质是把"被多次引用的细节"和"契约本身"分开，不是制造抽象层
- **Surgical Changes**：P1 严格"加+挪"，不修改任何已有契约语句
- **YAGNI**：G5（assets/example）、G8 重写 README 等推迟到 Path B 评估后再说

## 6. Pre-mortem
- **死法 1**：补成"对照清单"反而让 SKILL.md 失焦 → 缓解：高影响 gap 优先，低影响只做 design rationale 记录
- **死法 2**：照抄文章营销话术 → 缓解：每条新增内容必须可写成断言或可指向具体行为
- **死法 3**：references 数量爆炸（>10 个）反而增加阅读成本 → 缓解：每个 reference 都对应"按需读取"，SKILL.md 主流程内只在条件触发时才指向

## 7. Decision Log

| Decision | Options | Chosen | Why |
| --- | --- | --- | --- |
| Scope | A only / B (GT+meta-evo) / A→B / report-only | **A→B（按用户选 C）** | 先锁定确定收益，B 是高成本动作（$100/19 轮），等 A 成果再判定 |
| 执行风格 | P1 外科 / P2 重构 / P3 仅 SKILL.md | **P1 外科** | 平衡"对齐文章" vs "保住 invariant" vs "<200 行硬规" |
| Gap 过滤准则 | 全部对齐 / 仅可断言 / 仅营销 | **仅可断言** | 避免引入空洞规则，保证规则有执行通路 |
| GT example 是否补 | 本轮补 / 留 Path B | **留 Path B** | 与"先锁 A"决策一致 |

## 8. Out of Scope（本轮明确不做）
- 创建 `assets/example/` 下的 GT 样例数据（Path B）
- 跑 meta-evolution 自证（Path B，需 API 预算）
- README/QUICKSTART/FAQ 的全面重写（仅必要处微调）
- 修改 `scripts/*.py`（除非 G2 safety 规则需要落地为脚本字段）
