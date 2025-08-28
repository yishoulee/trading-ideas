
PYTHON ?= python
PKG = trading-ideas
TEST_FLAGS ?= -q

.PHONY: help install install-dev uninstall dev test test-verbose ci lint format clean coverage build tidy tidy-dryrun

help: ## Show available targets
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?##' Makefile | sed 's/:.*##/\t- /'

install: ## Install package (editable) with extras
	$(PYTHON) -m pip install -e .[web,dev]

install-dev: install ## Alias for install
	@echo "Dev environment installed."

uninstall: ## Uninstall package
	-$(PYTHON) -m pip uninstall -y $(PKG)

dev: install ## Set up dev environment (alias)
	@echo "Dev environment ready."

test: ## Run tests (quiet)
	pytest $(TEST_FLAGS)

test-verbose: ## Run tests with verbose output
	pytest -v

ci: ## Run tests and produce junit xml report in reports/
	mkdir -p reports
	pytest -q --maxfail=1 --junitxml=reports/junit.xml

lint: ## Run linter (prefer ruff, fall back to flake8)
	@if command -v ruff >/dev/null 2>&1; then ruff check .; \
	elif command -v flake8 >/dev/null 2>&1; then flake8 .; \
	else echo "No supported linter (ruff/flake8) installed"; fi

format: ## Format code (black + isort) if available
	@if command -v black >/dev/null 2>&1; then black .; else echo "black not installed"; fi
	@if command -v isort >/dev/null 2>&1; then isort .; else echo "isort not installed"; fi

coverage: ## Run tests with coverage and show report
	coverage run -m pytest && coverage report -m

build: ## Build wheel and sdist
	$(PYTHON) -m build

clean: ## Remove build/test artifacts
	rm -rf build dist *.egg-info .pytest_cache .mypy_cache .coverage reports
	find . -name '__pycache__' -type d -exec rm -rf {} +

tidy-dryrun: ## Show which tracked files would be removed because they match .gitignore
	git rm -r --cached --dry-run .

tidy: ## Untrack files now ignored by .gitignore (keeps files locally)
	git rm -r --cached .
	git add .
	git commit -m "chore: remove files ignored by .gitignore from repository (keep locally)" || echo "No changes to commit"

# End
