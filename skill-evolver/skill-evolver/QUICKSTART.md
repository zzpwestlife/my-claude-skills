# Quickstart

面向拿到 ZIP 压缩包后的使用者。

## 你拿到的是什么

这是一个用于本地 skill 自进化 / 评估 / 回滚的自包含 bundle。

它提供：

- 8 阶段循环
- 3 层评测
- 5 维 AND gate
- trace 驱动诊断
- keep / discard / rollback
- final report artifacts 约束

## 第一步：解压 ZIP

解压后，你应该看到：

```text
skill-evolver/
```

进入这个目录。

## 第二步：先做健康检查

先运行 package check：

```bash
python3 scripts/check_skill_package.py . --json
```

再运行 example dataset check：

```bash
python3 scripts/validate_dataset.py assets/example/dataset --json
```

如果这两步都通过，再开始真正使用。

## 第三步：决定你的使用方式

### 用法 A：只想验证数据集

如果你只是想检查自己的 dataset 是否符合格式：

```bash
python3 scripts/validate_dataset.py <dataset-dir> --json
```

适合：

- 准备数据集的人
- 只想先验格式的人

### 用法 B：只想验证 bundle 自身是否正常

```bash
python3 scripts/check_skill_package.py . --json
```

适合：

- 刚拿到 ZIP 的人
- 想先确认包是否干净的人

### 用法 C：想跑一次完整 evolution run

你需要准备三样东西：

1. `target skill` 目录
   - 目录内必须有 `SKILL.md`

2. `dataset` 目录
   - 至少包含：
     - `gt.jsonl`
     - `dev.jsonl`
   - 最好还包含：
     - `holdout.jsonl`
     - `regression.jsonl`

3. `output` 目录
   - 用来放 workspace、副本、trace、results、report

先运行 setup：

```bash
python3 scripts/setup_workspace.py \
  --skill-dir <target-skill-dir> \
  --dataset-dir <dataset-dir> \
  --output-dir <output-dir>
```

然后按 `SKILL.md` 的协议进入循环。

## 第四步：你应该先读什么

推荐顺序：

1. `SKILL.md`
2. `references/runbook.md`
3. `references/dataset-format.md`
4. `references/artifacts.md`
5. `references/distribution.md`

## 第五步：使用时最重要的规则

### 1. 不要跳过 trace

失败 case 没有 trace，就不要直接改。

### 2. 一轮只改一个原子 mutation

不要把 routing、body、helper 混在同一轮里改。

### 3. L1 失败就立刻停

L1 没过，不要继续跑 L2 / L3。

### 4. 五维 gate 是 AND，不是平均分

任何一项失败，都应该 discard / rollback。

### 5. dev 和 holdout / regression 的职责不同

- `dev` 用来优化
- `holdout` / `regression` 用来防止自我欺骗

## 第六步：example assets 有什么用

你可以直接看：

- `assets/example/target_skill/SKILL.md`
- `assets/example/dataset/*.jsonl`
- `assets/example/dataset/traces/*`

这些内容可以帮助你快速理解：

- 目标 skill 长什么样
- dataset 长什么样
- trace 大概长什么样

## 遇到问题时先检查什么

优先检查：

1. `SKILL.md` 是否存在于目标 skill 目录
2. dataset 是否至少包含 `gt.jsonl` 和 `dev.jsonl`
3. trace 路径是否真实存在
4. output 目录是否可写
5. 你是否在一次迭代里引入了多个 mutation

## 一句话上手路径

如果你只想最快上手：

```bash
python3 scripts/check_skill_package.py . --json
python3 scripts/validate_dataset.py assets/example/dataset --json
python3 scripts/setup_workspace.py \
  --skill-dir assets/example/target_skill \
  --dataset-dir assets/example/dataset \
  --output-dir /tmp/skill-evolver-smoke \
  --json
```

然后阅读 `SKILL.md` 和 `references/runbook.md`。
