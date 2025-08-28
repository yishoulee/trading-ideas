PYTHON ?= python
PKG = trading-ideas
TEST_FLAGS ?= -q

.PHONY: help install dev test lint format clean coverage docs build

help:
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?##' Makefile | sed 's/:.*##/\t- /'

install: ## Install package (editable)
	$(PYTHON) -m pip install -e .[web,dev]

dev: install ## Set up dev environment
	@echo "Dev environment ready."

test: ## Run test suite
	pytest $(TEST_FLAGS)

lint: ## Run basic lint (flake8 if available, else pyflakes)
	@if command -v flake8 >/dev/null 2>&1; then flake8 src tests; \
	elif command -v pyflakes >/dev/null 2>&1; then pyflakes src tests; \
	else echo "No linter installed"; fi

format: ## Format with black & isort if installed
	@if command -v black >/dev/null 2>&1; then black src tests; else echo "black not installed"; fi
	@if command -v isort >/dev/null 2>&1; then isort src tests; else echo "isort not installed"; fi

coverage: ## Run tests with coverage
	coverage run -m pytest && coverage report -m

build: ## Build distribution artifacts
	$(PYTHON) -m build

clean: ## Remove build/test artifacts
	rm -rf build dist *.egg-info .pytest_cache .mypy_cache .coverage
	find . -name '__pycache__' -type d -exec rm -rf {} +

# End
