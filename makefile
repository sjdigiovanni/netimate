# Makefile for netimate Development

PYTHON=python
PKG=netimate
TESTDIR=tests

.DEFAULT_GOAL := help

help: ## Show this help.
	@awk 'BEGIN {FS = ":.*##"}; /^[a-zA-Z_-]+:.*##/ {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

format: ## Format code using black and organize imports with ruff
	black .
	ruff check $(PKG) --select I --fix

lint: ## Lint code with ruff
	ruff check $(PKG)

type-check: ## Run static type checking with mypy
	mypy $(PKG)

test: ## Run tests with coverage
	pytest $(TESTDIR) --cov=$(PKG) --cov-report=term-missing

complexity: ## Check code complexity with radon
	radon cc $(PKG) -s -a

maintainability: ## Check maintainability index with radon
	radon mi $(PKG) -s

import-lint: ## Run import linter
	lint-imports --config .importlinter.ini

ci: format lint type-check test import-lint complexity maintainability dead-code ## Run full local CI suite

.PHONY: help format lint type-check test complexity maintainability dead-code import-lint ci