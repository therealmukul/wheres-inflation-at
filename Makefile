# Python Web Service Template - Makefile
# Provides convenient commands for development workflow

.PHONY: help install dev test run export-requirements clean

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies using uv
	uv sync --no-dev

dev: ## Install all dependencies (including dev) using uv
	uv sync

test: ## Run tests using pytest
	uv run pytest

run: ## Run the FastAPI development server
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

export-requirements: ## Export requirements.txt from pyproject.toml for Docker/CI compatibility
	uv export --no-dev --format requirements-txt > requirements.txt
	@echo "# This file is auto-generated from pyproject.toml" > temp_req.txt
	@echo "# Do not edit manually - run 'make export-requirements' to update" >> temp_req.txt
	@echo "# Or use 'uv export --no-dev --format requirements-txt > requirements.txt'" >> temp_req.txt
	@echo "" >> temp_req.txt
	@cat requirements.txt >> temp_req.txt
	@mv temp_req.txt requirements.txt
	@echo "✓ Exported production requirements to requirements.txt"

export-dev-requirements: ## Export all requirements (including dev) to requirements-dev.txt
	uv export --format requirements-txt > requirements-dev.txt
	@echo "# This file is auto-generated from pyproject.toml (includes dev dependencies)" > temp_req.txt
	@echo "# Do not edit manually - run 'make export-dev-requirements' to update" >> temp_req.txt
	@echo "# Or use 'uv export --format requirements-txt > requirements-dev.txt'" >> temp_req.txt
	@echo "" >> temp_req.txt
	@cat requirements-dev.txt >> temp_req.txt
	@mv temp_req.txt requirements-dev.txt
	@echo "✓ Exported all requirements to requirements-dev.txt"

clean: ## Clean up temporary files and caches
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete