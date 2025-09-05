
PYTHON ?= python
PKG = trading-ideas
TEST_FLAGS ?= -q

.PHONY: help install install-dev uninstall dev test test-verbose ci lint format clean coverage build tidy tidy-dryrun
DEMO_SCRIPTS := scripts/demo_backtest.py scripts/demo_statarb.py scripts/demo_momentum.py scripts/demo_etf_momentum.py scripts/demo_factor_model.py

.PHONY: demo demo-open demo-all
demo: ## Run a single demo: make demo SCRIPT=scripts/demo_factor_model.py ARGS="--tickers AAPL MSFT" (example)
	@echo "Usage: make demo SCRIPT=scripts/demo_factor_model.py ARGS='--tickers AAPL MSFT --start 2023-01-01 --end 2024-01-01'"
	@if [ -z "$(SCRIPT)" ]; then echo "Please set SCRIPT variable"; exit 1; fi
	bash -c "$(SCRIPT) $(ARGS)"

demo-all: ## Run all demos (requires network and yfinance); may take time
	@echo "Running all demos..."
	python3 scripts/demo_backtest.py --ticker SPY --start 2023-01-01 --end 2024-01-01 || true
	python3 scripts/demo_statarb.py --x SPY --y QQQ --start 2023-01-01 --end 2024-01-01 || true
	python3 scripts/demo_momentum.py --tickers AAPL MSFT NVDA AMZN --start 2023-01-01 --end 2024-01-01 || true
	python3 scripts/demo_etf_momentum.py --tickers SPY QQQ IWM AGG --start 2023-01-01 --end 2024-01-01 || true
	python3 scripts/demo_factor_model.py --tickers AAPL MSFT AMZN NVDA --start 2023-01-01 --end 2024-01-01 || true

demo-open: ## Open the scripts/ folder with the generated artifacts (uses xdg-open on Linux)
	@if command -v xdg-open >/dev/null 2>&1; then xdg-open scripts || echo "xdg-open not available"; else echo "Please open the scripts/ folder to view artifacts"; fi


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
	# remove demo artifacts produced by scripts/
	rm -rf scripts/demo_*.png scripts/demo_*.csv
	# remove notebook checkpoints and outputs
	rm -rf .ipynb_checkpoints
	find . -name '__pycache__' -type d -exec rm -rf {} +
	@echo "Cleaned build, test, demo artifacts, and caches."

tidy-dryrun: ## Show which tracked files would be removed because they match .gitignore
	git rm -r --cached --dry-run .

tidy: ## Untrack files now ignored by .gitignore (keeps files locally)
	git rm -r --cached .
	git add .
	git commit -m "chore: remove files ignored by .gitignore from repository (keep locally)" || echo "No changes to commit"

# End
