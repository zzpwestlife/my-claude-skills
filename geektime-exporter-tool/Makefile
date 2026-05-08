PYTHON ?= python3
CLI ?= $(PYTHON) -m geektime_exporter

CONFIG ?=
OUTPUT ?= ./output
IMAGES ?= ./output/images
NAMING ?= slug
RETRIES ?= 3
LOG_FILE ?= ./output/export.log

ARTICLE ?=
BATCH ?=
CONFIG_ARG := $(if $(strip $(CONFIG)),--config "$(CONFIG)",)

.PHONY: help install install-browser start-cdp-chrome run test lint fmt export-log-reset export-one export-one-clean export-batch export-batch-clean clean

help:
	@echo "Targets:"
	@echo "  make install      - 安装开发依赖并可编辑安装"
	@echo "  make install-browser - 安装浏览器登录依赖（playwright + chromium）"
	@echo "  make start-cdp-chrome - 以CDP端口9222启动Chrome"
	@echo "  make run          - 对话式导出（推荐）"
	@echo "  make test         - 运行测试"
	@echo "  make lint         - 运行代码检查（ruff check）"
	@echo "  make fmt          - 格式化代码（ruff format）"
	@echo "  make export-log-reset - 清空导出日志（减少历史噪音）"
	@echo "  make export-one   - 导出单篇文章（需 ARTICLE=...）"
	@echo "  make export-one-clean - 先清空日志再导出单篇"
	@echo "  make export-batch - 批量导出专栏（需 BATCH=...）"
	@echo "  make export-batch-clean - 先清空日志再批量导出"
	@echo "  参数: CONFIG=./config.json（可选）"
	@echo "  make clean        - 清理输出目录"

install:
	$(PYTHON) -m pip install -e .
	$(PYTHON) -m pip install pytest ruff playwright

install-browser:
	$(PYTHON) -m pip install playwright
	$(PYTHON) -m playwright install chromium

start-cdp-chrome:
	open -na "Google Chrome" --args --remote-debugging-port=9222

run:
	$(CLI) run $(CONFIG_ARG)

test:
	$(PYTHON) -m pytest -q

lint:
	$(PYTHON) -m ruff check .

fmt:
	$(PYTHON) -m ruff format .

export-log-reset:
	@mkdir -p "$$(dirname "$(LOG_FILE)")"
	@> "$(LOG_FILE)"
	@echo "Log reset: $(LOG_FILE)"

export-one:
	@if [ -z "$(ARTICLE)" ]; then echo "ERROR: ARTICLE is required"; exit 1; fi
	$(CLI) export \
		--article "$(ARTICLE)" \
		--output "$(OUTPUT)" \
		--images-dir "$(IMAGES)" \
		--naming "$(NAMING)" \
		--retries "$(RETRIES)" \
		$(CONFIG_ARG)

export-one-clean:
	@$(MAKE) export-log-reset LOG_FILE="$(LOG_FILE)"
	@$(MAKE) export-one ARTICLE="$(ARTICLE)" OUTPUT="$(OUTPUT)" IMAGES="$(IMAGES)" NAMING="$(NAMING)" RETRIES="$(RETRIES)" CONFIG="$(CONFIG)"

export-batch:
	@if [ -z "$(BATCH)" ]; then echo "ERROR: BATCH is required"; exit 1; fi
	$(CLI) export \
		--batch "$(BATCH)" \
		--output "$(OUTPUT)" \
		--images-dir "$(IMAGES)" \
		--naming "$(NAMING)" \
		--retries "$(RETRIES)" \
		$(CONFIG_ARG)

export-batch-clean:
	@$(MAKE) export-log-reset LOG_FILE="$(LOG_FILE)"
	@$(MAKE) export-batch BATCH="$(BATCH)" OUTPUT="$(OUTPUT)" IMAGES="$(IMAGES)" NAMING="$(NAMING)" RETRIES="$(RETRIES)" CONFIG="$(CONFIG)"

clean:
	rm -rf "$(OUTPUT)"
