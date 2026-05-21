# Lessons (Project Memory)

本文件用于沉淀在本仓库中反复出现的错误与对应的永久规则。

## How to Write a Lesson

使用固定格式追加一条记录：

- **Mistake**: 发生了什么
- **Impact**: 造成了什么代价
- **Rule**: 永久规则（可执行、可验证）
- **Where**: 应该加到哪里（例如 `.claude/rules/CORE_RULES.md`，或保持只在本文件）

## Lessons

- **Mistake**: 在 stub trace 上跑 skill-evolver dry-run 时，trace-driven proposer 协议会自然退化成 input/expected/actual 三元组诊断。
- **Impact**: 形式上协议被遵守，但 trace 真信息缺位，proposer 的诊断质量上限被 GT 文本质量直接决定。
- **Rule**: 任何 B-Lite/B-Build 类的 dry-run 都要在 `evolve_plan.md` 的 `Simulations` 节显式记录"trace 信息薄"；下游报告必须重申一次（见 `final_report.json` 的 `simulations.agent_traces`）。结论性主张（"机制 work"）只覆盖 mechanics，不覆盖 trace-driven 诊断质量。
- **Where**: 项目内本文件即可；不进 `skill-evolver/SKILL.md`（这是运行模式约束，不是 skill 契约）。
