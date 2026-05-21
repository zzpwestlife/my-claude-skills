# Release Copy

以下内容可直接用于 GitHub Release、飞书文档发布说明，或附在 ZIP 下载页。

---

## Title

`skill-evolver` v1 — Local skill evolution bundle

## Short description

`skill-evolver` 是一个用于本地 skill 自进化的自包含 bundle。

它把 skill 优化流程收敛为：

- 8 阶段循环
- 3 层评测
- 5 维 AND gate
- trace 驱动诊断
- keep / discard / rollback
- final report artifacts 约束

适合希望把 skill 优化从“凭感觉改”升级为“有证据、有回滚、有产物”的团队或个人。

## What's included

ZIP 解压后顶层目录为：

```text
skill-evolver/
```

主要内容包括：

- `SKILL.md`：主协议入口
- `references/`：运行顺序、数据集格式、产物契约、分发契约
- `scripts/`：本地校验与 workspace setup
- `assets/example/`：可直接演练的最小样例
- `QUICKSTART.md`：使用者快速上手
- `PACKAGING.md`：打包与分发检查清单
- `FAQ.md`：常见问题

## Quick start

解压后进入 `skill-evolver/`，先运行：

```bash
python3 scripts/check_skill_package.py . --json
python3 scripts/validate_dataset.py assets/example/dataset --json
```

如果要完整演练，再运行：

```bash
python3 scripts/setup_workspace.py \
  --skill-dir assets/example/target_skill \
  --dataset-dir assets/example/dataset \
  --output-dir /tmp/skill-evolver-smoke \
  --json
```

## Who this is for

适合：

- 想在本地迭代优化现有 `SKILL.md` 的人
- 想使用 `GT / dev / holdout / regression` 评测闭环的人
- 想保留 trace、results、report 等产物的人

不适合：

- 只想做一次普通 prompt 润色的人
- 没有数据集也不需要评测闭环的人
- 不打算执行 keep / rollback 协议的人

## Validation status

当前版本已通过：

- package check
- example dataset validation
- Darwin 多轮 ratchet 优化

当前收口分数：**93.4 / 100**。

## Recommended files to read

1. `README.md`
2. `QUICKSTART.md`
3. `SKILL.md`
4. `references/runbook.md`

## One-paragraph share text

`skill-evolver` 是一个可直接分发的本地 skill evolution bundle。它提供 8 阶段循环、3 层评测、5 维 AND gate、trace 驱动诊断，以及 keep / discard / rollback 机制，适合把 skill 优化过程做成可验证、可追溯、可回滚的本地闭环。ZIP 解压后可直接运行 package check 和 example dataset check，无需额外安装项目依赖。
