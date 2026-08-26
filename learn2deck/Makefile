.PHONY: help install install-dev test lint format clean run build validate

PYTHON ?= python3
VENV ?= .venv

help:  ## 顯示這個 help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## 安裝套件（一般使用者）
	$(PYTHON) -m pip install -e .

install-dev:  ## 安裝含 dev 依賴
	$(PYTHON) -m pip install -e ".[dev]"

test:  ## 跑測試
	$(PYTHON) -m pytest

test-cov:  ## 跑測試 + 覆蓋率
	$(PYTHON) -m pytest --cov=learn2deck --cov-report=html

lint:  ## 跑 linter
	$(PYTHON) -m ruff check learn2deck tests

format:  ## 自動格式化
	$(PYTHON) -m ruff format learn2deck tests

clean:  ## 清除 build artifacts
	rm -rf build/ dist/ *.egg-info
	rm -rf .pytest_cache/ .ruff_cache/ htmlcov/ .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

run:  ## 跑 CLI（debug 用）
	$(PYTHON) -m learn2deck.cli

# 範例指令
build:  ## 範例：build 一份簡報
	$(PYTHON) -m learn2deck.cli build ../00-claude-code-plugins-series.md -o /tmp/test.pptx

validate:  ## 範例：validate 一份簡報
	$(PYTHON) -m learn2deck.cli validate /tmp/test.pptx
