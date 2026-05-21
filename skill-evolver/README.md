# skill-evolver

A self-contained bundle for local skill evolution.

`skill-evolver` 用于在本地对目标 `SKILL.md` 做可追溯、可回滚、可验证的迭代优化。它把 skill 优化流程收敛为一套明确协议：先看 trace，再做单一原子 mutation，用分层评测和五维 AND gate 决定 keep / discard / rollback。

> **设计依据**：skill-evolver 的 5 维 AND 门控、3 层评测和 trace 驱动 proposer 协议来自一次 meta-evolution 自证 —— 让该 skill 自己优化自己跑 19 轮、零 rollback，过程中暴露的真问题反过来塑造了 `SKILL.md` 与 `references/` 的当前形态。

## 核心能力

- **8 阶段循环**
  - `Review -> Ideate -> Modify -> Commit -> Verify -> Gate -> Log -> Loop`
- **3 层评测**
  - `L1` quick guard
  - `L2` dev eval
  - `L3` strict eval
- **5 维 AND gate**
  - `structure_and_safety`
  - `dev_quality`
  - `strict_quality`
  - `cost_budget`
  - `atomic_auditability`
- **trace 驱动诊断**
- **keep / discard / rollback**
- **final report artifacts 约束**

## 适合谁

- 想把一个现有 skill 做成本地可迭代优化流程的人
- 想用 `GT / dev / holdout / regression` 拆分来评估 skill 的人
- 想把“凭感觉改 prompt”升级为“有证据、有回滚、有产物”的人

## 不适合谁

- 只想做一次普通文案润色的人
- 没有本地数据集、也不需要评测闭环的人
- 只想跑一次静态检查，不想进入迭代循环的人

## 最短上手路径

解压 ZIP 后进入 `skill-evolver/`，先运行：

```bash
python3 scripts/check_skill_package.py . --json
python3 scripts/validate_dataset.py assets/example/dataset --json
python3 scripts/setup_workspace.py \
  --skill-dir assets/example/target_skill \
  --dataset-dir assets/example/dataset \
  --output-dir /tmp/skill-evolver-smoke \
  --json
```

然后阅读：

1. `SKILL.md`
2. `QUICKSTART.md`
3. `references/runbook.md`

## 目录说明

```text
skill-evolver/
  SKILL.md
  QUICKSTART.md
  PACKAGING.md
  RELEASE.md
  FAQ.md
  references/
  scripts/
  assets/example/
```

## 文档入口

- **最终使用者**：`QUICKSTART.md`
- **打包 / 分发操作人**：`PACKAGING.md`
- **GitHub release 文案**：`RELEASE.md`
- **常见问题**：`FAQ.md`
- **分发契约**：`references/distribution.md`
- **本地运行顺序**：`references/runbook.md`
- **数据集格式**：`references/dataset-format.md`
- **产物契约**：`references/artifacts.md`

## 当前状态

当前 bundle 已通过：

- package check
- example dataset check
- Darwin 连续优化与 ratchet 记录

当前收口分数：**93.4 / 100**。

## 发布建议

如果你是分发人，建议随 ZIP 一起附带下面这段说明：

> 这是 `skill-evolver` bundle。
> 解压后进入 `skill-evolver/`，先运行：
> `python3 scripts/check_skill_package.py . --json`
> `python3 scripts/validate_dataset.py assets/example/dataset --json`
> 如果要完整演练，再运行 `scripts/setup_workspace.py`。
> 主入口是 `SKILL.md`，快速上手见 `QUICKSTART.md`。
