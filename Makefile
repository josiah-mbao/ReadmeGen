.PHONY: help install install-dev test test-cov test-unit test-integration lint format clean build docs serve-docs

# Default target
help: ## Show this help message
	@echo "ReadmeGen Development Commands"
	@echo "=============================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation
install: ## Install the package
	pip install .

install-dev: ## Install development dependencies
	pip install -e .[dev]

# Testing
test: ## Run all tests
	pytest tests/ -v

test-cov: ## Run tests with coverage
	pytest tests/ --cov=readme_generator --cov-report=term-missing --cov-report=html

test-unit: ## Run only unit tests
	pytest tests/ -v -m "not integration and not e2e"

test-integration: ## Run integration tests
	pytest tests/ -v -m integration

test-e2e: ## Run end-to-end tests
	pytest tests/ -v -m e2e

test-performance: ## Run performance tests
	pytest tests/ -v -m performance --durations=10

# Code Quality
lint: ## Run linting checks
	ruff check .
	ruff format --check .

format: ## Format code with ruff
	ruff check . --fix
	ruff format .

type-check: ## Run type checking
	pyright readme_generator/

# Building
build: ## Build the package
	python -m build

build-check: ## Build and check package
	python -m build
	twine check dist/*

# Development
clean: ## Clean build artifacts
	rm -rf dist/ build/ *.egg-info/ .coverage htmlcov/ .pytest_cache/ .ruff_cache/

docs: ## Generate documentation (placeholder)
	@echo "Documentation generation not yet implemented"

serve-docs: ## Serve documentation (placeholder)
	@echo "Documentation serving not yet implemented"

# Development workflow
dev-setup: clean install-dev ## Set up development environment
	@echo "Development environment ready!"

dev-test: lint test-cov ## Run full development test suite
	@echo "All tests passed! ✅"

# CI simulation
ci: lint test-cov build-check ## Run CI checks locally
	@echo "CI checks passed! 🚀"

# Release helpers
bump-patch: ## Bump patch version
	semantic-release version --patch

bump-minor: ## Bump minor version
	semantic-release version --minor

bump-major: ## Bump major version
	semantic-release version --major

release: build ## Build for release
	twine check dist/*

# Demo
demo: ## Run the 60-second demo
	./demo_60_second_experience.sh

# Utility
deps-update: ## Update dependencies
	pip install --upgrade pip
	pip install -e .[dev] --upgrade

shell: ## Start Python shell with package imported
	python -c "import readme_generator; print('ReadmeGen imported successfully!')"
