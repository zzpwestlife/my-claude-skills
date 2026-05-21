# Packaging Checklist

面向打包与分发操作人。

## 目标

生成一个可分发的 ZIP，解压后顶层目录为：

```text
skill-evolver/
```

## 打包前命令清单

以下命令都应在 `skill-evolver/` 目录内执行，除非特别说明。

### 1. 校验 package

```bash
python3 scripts/check_skill_package.py . --json
```

### 2. 校验 example dataset

```bash
python3 scripts/validate_dataset.py assets/example/dataset --json
```

### 3. 建议做一次 smoke setup

```bash
python3 scripts/setup_workspace.py \
  --skill-dir assets/example/target_skill \
  --dataset-dir assets/example/dataset \
  --output-dir /tmp/skill-evolver-smoke \
  --json
```

## 打包前人工检查

确认以下内容不在包里：

- `.DS_Store`
- `.git/`
- `__pycache__/`
- `.pytest_cache/`
- 临时输出目录
- 本仓库无关文档或构建产物

## 推荐打包方式

从 `skill-evolver/` 的父目录执行。

### macOS / Linux

```bash
zip -r skill-evolver.zip skill-evolver \
  -x "*.DS_Store" \
  -x "*/__pycache__/*" \
  -x "*/.pytest_cache/*" \
  -x "*/.git/*"
```

这样可以保证 ZIP 解压后保留顶层 `skill-evolver/` 目录。

## 打包后自检

建议把 ZIP 解压到一个临时目录，再重新验证一次。

### 1. 解压

```bash
mkdir -p /tmp/skill-evolver-release-check
unzip skill-evolver.zip -d /tmp/skill-evolver-release-check
```

### 2. 进入解压目录

```bash
cd /tmp/skill-evolver-release-check/skill-evolver
```

### 3. 重新执行校验

```bash
python3 scripts/check_skill_package.py . --json
python3 scripts/validate_dataset.py assets/example/dataset --json
```

## 分发前最后确认

在发出去之前，最后确认：

- ZIP 顶层目录是 `skill-evolver/`
- package check 通过
- example dataset check 通过
- `SKILL.md`、`references/`、`scripts/`、`assets/example/` 都在

## 推荐附带文案

发 ZIP 时建议附上：

> 解压后进入 `skill-evolver/`，先运行：
> `python3 scripts/check_skill_package.py . --json`
> `python3 scripts/validate_dataset.py assets/example/dataset --json`
> 如果要完整演练，再运行 `scripts/setup_workspace.py`。

## 相关文件

- 分发说明：`README.md`
- 使用者上手：`QUICKSTART.md`
- 分发契约：`references/distribution.md`
