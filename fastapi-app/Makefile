.PHONY: lock install run rename format lint typecheck skylos test pre-commit \
	check ci clean build build-all build-project build-packages help

# PEP 517 artifacts (wheels + sdists)
DIST ?= dist
# Paths checked by format, lint, typecheck, and Skylos
CHECK = project_name tests packages/example_lib

lock:  ## Refresh uv.lock for the workspace (root + packages/* members)
	uv lock

install: lock  ## Install project + dev tools (linters, tests, etc.)
	uv sync --extra dev
	@test -f .env || cp .env.example .env

rename:  ## Rename project_name to NAME=your_package (one-time setup)
	@test -n "$(NAME)" || (echo "Usage: make rename NAME=your_package" >&2; exit 1)
	@./scripts/rename_project.sh "$(NAME)"
	@$(MAKE) lock

run:  ## Run the application
	uv run main

format:  ## Ruff format + fixes
	uv run ruff format $(CHECK)
	uv run ruff check --fix $(CHECK)

lint:  ## Ruff
	uv run ruff check $(CHECK)

typecheck:  ## Type-check with basedpyright
	uv run basedpyright $(CHECK)

skylos:  ## Skylos (dead code, secrets, quality)
	uv run skylos --no-upload $(CHECK)

test:  ## Pytest (coverage and options from pyproject)
	uv run pytest tests

prek:  ## Fast local hooks (format + lint + types; run make ci before push)
	uv run prek auto-update
	uv run prek run --all-files

check: format lint typecheck skylos test  ## Local quality pipeline (format may autofix)

ci:  ## Read-only quality gate for CI (no autofix)
	uv run ruff format --check $(CHECK)
	uv run ruff check $(CHECK)
	$(MAKE) typecheck skylos test

build: lock  ## Wheels + sdists for every workspace member
	rm -rf "$(DIST)"
	mkdir -p "$(DIST)"
	uv build --all-packages -o $(DIST)

build-project: lock  ## Build only project (root project)
	rm -rf "$(DIST)"
	mkdir -p "$(DIST)"
	uv build --package project_name -o $(DIST)

build-packages: lock  ## Internal libs only
	@if [ ! -d packages ]; then \
		echo "No packages/ directory; create packages/<name>/ with a pyproject.toml." >&2; \
		exit 1; \
	fi
	@set -e; \
	rm -rf "$(DIST)"; \
	mkdir -p "$(DIST)"; \
	count=0; \
	for py in $$(find packages -maxdepth 2 -mindepth 2 -name pyproject.toml 2>/dev/null); do \
		if [ -f "$$py" ]; then \
			dir=$$(dirname "$$py"); \
			echo "uv build -> $(DIST) ($$dir)"; \
			uv build -o "$(DIST)" "$$dir"; \
			count=$$((count + 1)); \
		fi; \
	done; \
	if [ $$count -eq 0 ]; then \
		echo "No packages/*/pyproject.toml found under packages/." >&2; \
		exit 1; \
	fi

clean:  ## Remove caches, Skylos data, build artifacts (dist + $(DIST)), and test/coverage outputs
	find . -type d -name __pycache__ -not -path './.venv/*' -exec rm -rf {} +
	find . \( -path './.venv' -o -path './.git' \) -prune -o -type f \( -name '*.pyc' -o -name '*.pyo' \) -print | while IFS= read -r f; do rm -f "$$f"; done
	find . \( -path './.venv' -o -path './.git' \) -prune -o -type d -name '*.egg-info' -print | while IFS= read -r d; do rm -rf "$$d"; done
	rm -rf \
		.skylos \
		.pytest_cache \
		.ruff_cache \
		.pyright_cache \
		.pytest_results \
		.coverage \
		htmlcov \
		coverage.xml \
		junit.xml \
		build \
		"$(DIST)" \
		wheels \
		.eggs

help:  ## Show available make targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-14s %s\n", $$1, $$2}'
