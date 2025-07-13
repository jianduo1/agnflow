.PHONY: help install install-dev test format lint clean build

help: ## 显示帮助信息
	@echo "可用的命令:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## 安装生产依赖
	uv pip install -e .

install-dev: ## 安装开发依赖
	uv pip install -e ".[dev]"

test: ## 运行测试
	uv run pytest

format: ## 格式化代码
	uv run black .
	uv run isort .

format-check: ## 检查代码格式
	uv run black --check .
	uv run isort --check-only .

lint: ## 代码检查
	uv run flake8 .

clean: ## 清理构建文件
	rm -rf dist/ build/ *.egg-info/ .pytest_cache/ .coverage htmlcov/

build: ## 构建包
	uv run python -m build

upload-test: ## 上传到 TestPyPI
	uv run twine upload --repository testpypi dist/*

upload: ## 上传到 PyPI
	uv run twine upload dist/*

lock: ## 更新依赖锁文件
	uv lock

sync: ## 同步依赖
	uv sync

dev: install-dev ## 开发环境设置
	@echo "开发环境已设置完成！" 