.PHONY: help install install-dev clean clean-build clean-pyc clean-test clean-coverage clean-docker
.PHONY: lint lint-isort lint-ruff lint-mypy lint-ci format format-check
.PHONY: test test-unit test-integration test-coverage test-coverage-html test-coverage-xml test-ci
.PHONY: pipeline-lint pipeline-test pipeline-coverage pipeline-full
.PHONY: docker-build docker-run docker-test serve serve-dev
.PHONY: build release tag update-deps docs
.DEFAULT_GOAL := help

# Colors for terminal output
RED := \033[31m
GREEN := \033[32m
YELLOW := \033[33m
BLUE := \033[34m
RESET := \033[0m

# Python version detection
PYTHON_VERSION := $(shell python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")

define PRINT_HELP_PYSCRIPT
import re, sys

print("$(BLUE)Phoney API Development Commands$(RESET)")
print("$(BLUE)================================$(RESET)")
print()

categories = {
    "Setup & Installation": [],
    "Code Quality & Linting": [],
    "Testing": [],
    "CI/CD Pipeline Simulation": [],
    "Development Server": [],
    "Docker": [],
    "Build & Release": [],
    "Maintenance": []
}

for line in sys.stdin:
    match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
    if match:
        target, help_text = match.groups()
        
        if any(x in target for x in ['install', 'deps']):
            categories["Setup & Installation"].append((target, help_text))
        elif any(x in target for x in ['lint', 'format', 'mypy', 'ruff', 'isort']):
            categories["Code Quality & Linting"].append((target, help_text))
        elif any(x in target for x in ['test', 'coverage']):
            categories["Testing"].append((target, help_text))
        elif 'pipeline' in target:
            categories["CI/CD Pipeline Simulation"].append((target, help_text))
        elif any(x in target for x in ['serve', 'dev']):
            categories["Development Server"].append((target, help_text))
        elif 'docker' in target:
            categories["Docker"].append((target, help_text))
        elif any(x in target for x in ['build', 'release', 'tag']):
            categories["Build & Release"].append((target, help_text))
        else:
            categories["Maintenance"].append((target, help_text))

for category, targets in categories.items():
    if targets:
        print(f"$(YELLOW){category}:$(RESET)")
        for target, help_text in targets:
            print(f"  $(GREEN)%-20s$(RESET) %s" % (target, help_text))
        print()

print("$(BLUE)Environment Info:$(RESET)")
print(f"  Python Version: $(GREEN)$(PYTHON_VERSION)$(RESET)")
print(f"  Poetry Status:  $(GREEN)$(shell poetry --version 2>/dev/null || echo 'Not installed')$(RESET)")
print()
endef
export PRINT_HELP_PYSCRIPT

help: ## Show this help message
	@python3 -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

# ============================================================================
# Setup & Installation
# ============================================================================

install: ## Install production dependencies
	@echo "$(BLUE)Installing production dependencies...$(RESET)"
	poetry install --no-dev --no-interaction

install-dev: ## Install all dependencies including development tools
	@echo "$(BLUE)Installing all dependencies...$(RESET)"
	poetry install --no-interaction

update-deps: ## Update all dependencies
	@echo "$(BLUE)Updating dependencies...$(RESET)"
	poetry update

# ============================================================================
# Code Quality & Linting (CI/CD Pipeline Mirror)
# ============================================================================

lint-isort: ## Check import sorting (mirrors CI isort check)
	@echo "$(BLUE)Checking import sorting...$(RESET)"
	poetry run isort --check .

lint-ruff: ## Run ruff linting (mirrors CI ruff check)
	@echo "$(BLUE)Running ruff linting...$(RESET)"
	poetry run ruff check .

lint-mypy: ## Run mypy type checking (mirrors CI mypy check)
	@echo "$(BLUE)Running mypy type checking...$(RESET)"
	poetry run mypy phoney/ tests/ --ignore-missing-imports

lint-ci: lint-ruff ## Run all linting checks (mirrors CI lint job)
	@echo "$(GREEN)✓ All linting checks passed$(RESET)"

lint: lint-ci ## Alias for lint-ci

format: ## Auto-format code with black and isort
	@echo "$(BLUE)Formatting code...$(RESET)"
	poetry run black .
	poetry run isort .
	@echo "$(GREEN)✓ Code formatted$(RESET)"

format-check: ## Check if code needs formatting without making changes
	@echo "$(BLUE)Checking code formatting...$(RESET)"
	poetry run black --check .
	poetry run isort --check .

# ============================================================================
# Testing (CI/CD Pipeline Mirror)
# ============================================================================

test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(RESET)"
	poetry run pytest tests/ -v

test-integration: ## Run integration tests
	@echo "$(BLUE)Running integration tests...$(RESET)"
	poetry run pytest tests/test_integration.py -v

test-coverage: ## Run tests with coverage reporting (mirrors CI coverage)
	@echo "$(BLUE)Running tests with coverage...$(RESET)"
	poetry run pytest --cov=phoney --cov-report=term --cov-fail-under=75

test-coverage-html: ## Generate HTML coverage report (mirrors CI artifacts)
	@echo "$(BLUE)Generating HTML coverage report...$(RESET)"
	poetry run pytest --cov=phoney --cov-report=html --cov-report=term --cov-fail-under=75
	@echo "$(GREEN)✓ HTML coverage report generated in htmlcov/$(RESET)"

test-coverage-xml: ## Generate XML coverage report (mirrors CI artifacts)
	@echo "$(BLUE)Generating XML coverage report...$(RESET)"
	poetry run pytest --cov=phoney --cov-report=xml --cov-report=term --cov-fail-under=75

test-ci: ## Run full test suite with coverage (mirrors CI test job)
	@echo "$(BLUE)Running CI test suite...$(RESET)"
	poetry run pytest --cov=phoney --cov-report=xml --cov-report=html --cov-report=term --cov-fail-under=75 --junit-xml=test-results.xml -v
	@echo "$(GREEN)✓ All tests passed with coverage$(RESET)"

test: test-ci ## Alias for test-ci

# ============================================================================
# CI/CD Pipeline Simulation
# ============================================================================

pipeline-lint: ## Simulate CI lint pipeline stage
	@echo "$(YELLOW)========================================$(RESET)"
	@echo "$(YELLOW)🚀 Simulating CI Lint Pipeline Stage$(RESET)"
	@echo "$(YELLOW)========================================$(RESET)"
	@echo "$(BLUE)Setting up Python $(PYTHON_VERSION)...$(RESET)"
	@echo "$(BLUE)Installing dependencies...$(RESET)"
	@poetry install --no-interaction
	@echo "$(BLUE)Creating .env file for testing...$(RESET)"
	@echo "ENV_STATE=test" > .env
	@echo "HOST=localhost" >> .env
	@echo "PORT=8000" >> .env
	@echo "API_USERNAME=test_user" >> .env
	@echo "API_PASSWORD_HASH=\$$2b\$$12\$$tufn64/0gSIHZMPLEHASH" >> .env
	@echo "SECRET_KEY=$$(openssl rand -hex 32)" >> .env
	@$(MAKE) lint-ci
	@echo "$(GREEN)✅ Lint pipeline stage completed successfully$(RESET)"

pipeline-test: ## Simulate CI test pipeline stage for current Python version
	@echo "$(YELLOW)========================================$(RESET)"
	@echo "$(YELLOW)🚀 Simulating CI Test Pipeline Stage$(RESET)"
	@echo "$(YELLOW)Python $(PYTHON_VERSION)$(RESET)"
	@echo "$(YELLOW)========================================$(RESET)"
	@echo "$(BLUE)Setting up Python $(PYTHON_VERSION)...$(RESET)"
	@echo "$(BLUE)Installing dependencies...$(RESET)"
	@poetry install --no-interaction
	@echo "$(BLUE)Creating .env file for testing...$(RESET)"
	@echo "ENV_STATE=test" > .env
	@echo "HOST=localhost" >> .env
	@echo "PORT=8000" >> .env
	@echo "API_USERNAME=test_user" >> .env
	@echo "API_PASSWORD_HASH=\$$2b\$$12\$$tufn64/0gSIHZMPLEHASH" >> .env
	@echo "SECRET_KEY=$$(openssl rand -hex 32)" >> .env
	@$(MAKE) test-ci
	@echo "$(GREEN)✅ Test pipeline stage completed successfully$(RESET)"

pipeline-coverage: ## Simulate CI coverage verification stage
	@echo "$(YELLOW)========================================$(RESET)"
	@echo "$(YELLOW)🚀 Simulating CI Coverage Pipeline Stage$(RESET)"
	@echo "$(YELLOW)========================================$(RESET)"
	@echo "$(BLUE)Setting up Python $(PYTHON_VERSION)...$(RESET)"
	@echo "$(BLUE)Installing dependencies...$(RESET)"
	@poetry install --no-interaction
	@echo "$(BLUE)Creating .env file for testing...$(RESET)"
	@echo "ENV_STATE=test" > .env
	@echo "HOST=localhost" >> .env
	@echo "PORT=8000" >> .env
	@echo "API_USERNAME=test_user" >> .env
	@echo "API_PASSWORD_HASH=\$$2b\$$12\$$tufn64/0gSIHZMPLEHASH" >> .env
	@echo "SECRET_KEY=$$(openssl rand -hex 32)" >> .env
	@poetry run pytest --cov=phoney --cov-report=xml --cov-report=html --cov-report=term --cov-fail-under=75
	@echo "$(BLUE)Current test coverage meets minimum requirement of 75%$(RESET)"
	@poetry run coverage report --fail-under=90 || echo "$(YELLOW)⚠️  Test coverage is below target of 90%$(RESET)"
	@echo "$(GREEN)✅ Coverage pipeline stage completed successfully$(RESET)"

pipeline-aws-test: ## Simulate AWS deployment pipeline test stage
	@echo "$(YELLOW)========================================$(RESET)"
	@echo "$(YELLOW)🚀 Simulating AWS Deployment Test Stage$(RESET)"
	@echo "$(YELLOW)========================================$(RESET)"
	@echo "$(BLUE)Running linting...$(RESET)"
	@poetry run ruff check phoney/ tests/
	@echo "$(BLUE)Running type checking...$(RESET)"
	@poetry run mypy phoney/ --ignore-missing-imports
	@echo "$(BLUE)Running tests with coverage and XML output...$(RESET)"
	@poetry run pytest tests/ --cov=phoney --cov-report=xml --cov-report=html --junit-xml=test-results.xml -v
	@echo "$(GREEN)✅ AWS deployment test stage completed successfully$(RESET)"

pipeline-full: pipeline-lint pipeline-test pipeline-coverage ## Run complete CI/CD pipeline simulation
	@echo "$(GREEN)========================================$(RESET)"
	@echo "$(GREEN)🎉 Complete CI/CD Pipeline Successful!$(RESET)"
	@echo "$(GREEN)========================================$(RESET)"
	@echo "$(GREEN)✅ Lint Stage: Passed$(RESET)"
	@echo "$(GREEN)✅ Test Stage: Passed$(RESET)"
	@echo "$(GREEN)✅ Coverage Stage: Passed$(RESET)"
	@echo "$(BLUE)Ready for deployment! 🚀$(RESET)"

# ============================================================================
# Development Server
# ============================================================================

serve: ## Start the development server with .env file
	@echo "$(BLUE)Starting development server...$(RESET)"
	@echo "$(YELLOW)Server will be available at: http://localhost:8000$(RESET)"
	@echo "$(YELLOW)API documentation: http://localhost:8000/docs$(RESET)"
	poetry run uvicorn phoney.app.main:app --env-file .env --reload

serve-prod: ## Start the production server
	@echo "$(BLUE)Starting production server...$(RESET)"
	poetry run uvicorn phoney.app.main:app --host 0.0.0.0 --port 8000

serve-dev: ## Start development server with debug logging
	@echo "$(BLUE)Starting development server with debug logging...$(RESET)"
	@echo "ENV_STATE=dev" > .env.dev
	@echo "HOST=localhost" >> .env.dev
	@echo "PORT=8000" >> .env.dev
	@echo "LOG_LEVEL=DEBUG" >> .env.dev
	@echo "API_USERNAME=dev_user" >> .env.dev
	@echo "API_PASSWORD_HASH=\$$2b\$$12\$$tufn64/0gSIHZMPLEHASH" >> .env.dev
	@echo "SECRET_KEY=$$(openssl rand -hex 32)" >> .env.dev
	poetry run uvicorn phoney.app.main:app --env-file .env.dev --reload --log-level debug

# ============================================================================
# Docker
# ============================================================================

docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(RESET)"
	docker build -t phoney:latest .

docker-run: docker-build ## Build and run Docker container
	@echo "$(BLUE)Running Docker container...$(RESET)"
	@echo "$(YELLOW)Server will be available at: http://localhost:8000$(RESET)"
	docker run -p 8000:8000 --env-file .env phoney:latest

docker-test: docker-build ## Build Docker image and run tests inside container
	@echo "$(BLUE)Running tests in Docker container...$(RESET)"
	docker run --rm phoney:latest poetry run pytest

# ============================================================================
# Build & Release
# ============================================================================

build: clean test ## Build the package after cleaning and testing
	@echo "$(BLUE)Building package...$(RESET)"
	poetry build
	@echo "$(GREEN)✓ Package built successfully$(RESET)"

release: pipeline-full build ## Run full pipeline and build for release
	@echo "$(BLUE)Preparing for release...$(RESET)"
	@echo "$(GREEN)✓ All checks passed, ready to release$(RESET)"

tag: ## Create and push a git tag based on version
	@export VERSION_TAG=`poetry version -s` \
	&& echo "$(BLUE)Creating tag v$$VERSION_TAG...$(RESET)" \
	&& git tag v$$VERSION_TAG \
	&& git push origin v$$VERSION_TAG \
	&& echo "$(GREEN)✓ Tag v$$VERSION_TAG created and pushed$(RESET)"

# ============================================================================
# Maintenance & Cleanup
# ============================================================================

clean: clean-build clean-pyc clean-test clean-coverage ## Clean all build, test, and cache files
	@echo "$(GREEN)✓ Cleanup completed$(RESET)"

clean-build: ## Clean build artifacts
	@echo "$(BLUE)Cleaning build artifacts...$(RESET)"
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## Clean Python cache files
	@echo "$(BLUE)Cleaning Python cache files...$(RESET)"
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## Clean test artifacts
	@echo "$(BLUE)Cleaning test artifacts...$(RESET)"
	rm -fr .pytest_cache
	rm -f test-results.xml
	rm -f .env .env.dev

clean-coverage: ## Clean coverage reports
	@echo "$(BLUE)Cleaning coverage reports...$(RESET)"
	rm -f .coverage
	rm -fr htmlcov/
	rm -f coverage.xml

clean-docker: ## Clean Docker images and containers
	@echo "$(BLUE)Cleaning Docker images...$(RESET)"
	docker image prune -af

docs: ## Generate documentation
	@echo "$(BLUE)Generating documentation...$(RESET)"
	@echo "$(YELLOW)Documentation available at: http://localhost:8000/docs$(RESET)"
	@echo "$(YELLOW)Run 'make serve' to view API documentation$(RESET)"

# ============================================================================
# Quick Development Workflow
# ============================================================================

check: lint-ci test-coverage ## Quick check: run linting and tests with coverage
	@echo "$(GREEN)✅ Quick check completed successfully$(RESET)"

fix: format lint-ci test-ci ## Fix formatting issues and run full checks
	@echo "$(GREEN)✅ Code fixed and validated$(RESET)"

ci: pipeline-full ## Alias for complete CI/CD pipeline simulation
	@echo "$(GREEN)✅ Complete CI simulation finished$(RESET)"