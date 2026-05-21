# FAQ

## 1. 这是什么？

这是一个用于本地 skill 自进化的 bundle。

它不是单独一个 prompt，也不是一个只会做静态检查的脚本集合，而是一套完整协议：

- 先看 trace
- 再做单一原子 mutation
- 跑分层评测
- 过五维 AND gate
- 决定 keep / discard / rollback
- 记录 results、traces、iterations、final report

## 2. 我拿到 ZIP 后第一步做什么？

先进入解压后的 `skill-evolver/` 目录，运行：

```bash
python3 scripts/check_skill_package.py . --json
python3 scripts/validate_dataset.py assets/example/dataset --json
```

如果这两步没过，不要直接开始用。

## 3. 需要安装额外依赖吗？

当前 bundle 内置脚本只依赖 Python 标准库。

按分发契约，接收方应能在不安装额外项目依赖的前提下运行：

```bash
python3 scripts/check_skill_package.py . --json
```

## 4. 我只有一个目标 skill，没有 dataset，能用吗？

不能完整发挥它的价值。

这个 bundle 的核心前提是你至少有：

- `gt.jsonl`
- `dev.jsonl`

更理想的是再加上：

- `holdout.jsonl`
- `regression.jsonl`

没有 dataset，就只能做非常有限的人工评估。

## 5. trace 为什么这么重要？

因为 `skill-evolver` 不是鼓励“凭感觉改”。

如果失败 case 没有 trace，就很容易：

- 误判失败原因
- 一次改太多东西
- 在错误方向上持续优化

所以它要求 mutation proposal 必须能指向具体 trace 和具体失败现象。

## 6. 为什么一轮只能改一个 mutation？

因为要保证可归因。

如果一轮里同时改 routing、body、helper，就很难知道：

- 到底哪一处带来了提升
- 哪一处导致了回归
- rollback 应该回到哪里

## 7. 五维 gate 是怎么算的？

不是加权平均，而是 AND gate。

也就是说：

- 任意一维失败
- 这一轮就应 discard / rollback

五维包括：

- `structure_and_safety`
- `dev_quality`
- `strict_quality`
- `cost_budget`
- `atomic_auditability`

## 8. dev、holdout、regression 有什么区别？

- `dev`：用于日常优化
- `holdout`：用于更严格的泛化检查
- `regression`：用于防止旧问题回归

不要把它们混成同一类数据来使用。

## 9. 我只是想检查 ZIP 是否健康，不想跑完整 evolution，可以吗？

可以。

只运行：

```bash
python3 scripts/check_skill_package.py . --json
```

如果你只是想检查 dataset，则运行：

```bash
python3 scripts/validate_dataset.py <dataset-dir> --json
```

## 10. 最快的体验路径是什么？

直接运行：

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

- `SKILL.md`
- `QUICKSTART.md`
- `references/runbook.md`

## 11. 这个 bundle 现在成熟吗？

当前版本已经过多轮 Darwin ratchet 优化，并完成收口。

当前收口分数是：**93.4 / 100**。

对于“本地 skill evolution bundle”这个定位来说，它已经适合分发、演示和复用。

## 12. 如果我要发给别人，最容易踩的坑是什么？

最常见的是：

- ZIP 里混入 `.DS_Store`
- 解压后没有 `skill-evolver/` 这一层顶级目录
- 忘记附 `references/` 或 `assets/example/`
- 只发 `SKILL.md`，没发整个 bundle

发出去之前，先看：

- `PACKAGING.md`
- `references/distribution.md`
