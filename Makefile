.PHONY: help install dev proto test smoke schema clean build publish publish-dry publish-remaining sync-version serve-mcp serve-rest cli-list cli-validate

PYTHON ?= python3
ROOT   := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
VERSION := $(shell tr -d '[:space:]' < VERSION)
DIST   := dist

PACKAGES := skillm \
	packages/nlp2skillm \
	packages/dsl2skillm \
	packages/uri2skillm \
	packages/cli2skillm \
	packages/mcp2skillm \
	packages/rest2skillm

TEST_PATHS := skillm/tests packages/
MANIFEST   ?= app.skillm.yaml
REST_PORT  ?= 8216
REST_HOST  ?= 127.0.0.1

help: ## Pokaż dostępne cele
	@grep -E '^[a-zA-Z0-9_.-]+:.*##' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install dev: ## Editable install wszystkich paczek + protobuf
	@bash install-dev.sh

proto: ## Wygeneruj protobuf (dsl2skillm)
	@$(PYTHON) -m pip install -q grpcio-tools
	@bash packages/dsl2skillm/scripts/generate-proto.sh
	@touch packages/dsl2skillm/src/dsl2skillm/v1/__init__.py

test: ## Uruchom pytest (skillm + packages)
	@$(PYTHON) -m pytest $(TEST_PATHS) -q

test-verbose: ## Uruchom pytest z verbose
	@$(PYTHON) -m pytest $(TEST_PATHS) -v

smoke: ## Testy dymne E2E (CLI, MCP, REST)
	@bash scripts/smoke-test.sh

schema: ## Waliduj registry JSON Schema
	@dsl2skillm validate-schema

sync-version: ## Synchronizuj VERSION → pyproject.toml
	@bash scripts/sync-version.sh

clean: ## Usuń artefakty build/test
	@rm -rf $(DIST) .pytest_cache app.skillm.events.jsonl
	@find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.pytest_cache' -exec rm -rf {} + 2>/dev/null || true

build: sync-version install test ## Zbuduj wheel/sdist do dist/
	@rm -rf $(DIST) && mkdir -p $(DIST)
	@$(PYTHON) -m pip install -q build
	@cd skillm && $(PYTHON) -m build --outdir $(ROOT)$(DIST)
	@for pkg in nlp2skillm dsl2skillm uri2skillm cli2skillm mcp2skillm rest2skillm; do \
		echo "==> build $$pkg"; \
		cd packages/$$pkg && $(PYTHON) -m build --outdir $(ROOT)$(DIST); \
	done
	@ls -la $(DIST)

publish-dry: ## Build + test bez uploadu na PyPI
	@bash scripts/publish.sh --dry-run

publish: ## Build + test + upload wszystkich paczek na PyPI
	@bash scripts/publish.sh

publish-remaining: ## Dokończ upload paczek po limicie PyPI
	@bash scripts/publish-remaining.sh

serve-mcp: ## Uruchom serwer MCP (stdio)
	@mcp2skillm serve

serve-rest: ## Uruchom REST API (port $(REST_PORT))
	@rest2skillm serve --host $(REST_HOST) --port $(REST_PORT)

shell: ## Interaktywny REPL DSL
	@cli2skillm shell --file $(MANIFEST)

cli-list: ## LIST skilli z manifestu
	@cli2skillm exec 'LIST FILE $(MANIFEST)'

cli-validate: ## VALIDATE manifestu
	@cli2skillm exec 'VALIDATE $(MANIFEST)'

cli-invoke: ## INVOKE echo-python (make cli-invoke ARGS='["world"]')
	@cli2skillm exec 'INVOKE skillm://skill/echo-python FILE $(MANIFEST) ARGS $(or $(ARGS),["world"])'

check: install test smoke schema ## Pełna weryfikacja przed release

.DEFAULT_GOAL := help
