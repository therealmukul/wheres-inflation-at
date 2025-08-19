# Backend-Frontend Reorganized Project - Makefile
# Provides convenient commands for development workflow

.PHONY: help install dev test run backend-run export-requirements clean

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies for backend using uv
	cd backend && uv sync --no-dev

dev: ## Install all dependencies (including dev) for backend using uv
	cd backend && uv sync

test: ## Run backend tests using pytest
	cd backend && uv run pytest

run: backend-run ## Run the FastAPI development server (alias for backend-run)

backend-run: ## Run the FastAPI backend development server
	cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

export-requirements: ## Export requirements.txt from backend pyproject.toml for Docker/CI compatibility
	cd backend && uv export --no-dev --format requirements-txt > requirements.txt
	@echo "# This file is auto-generated from pyproject.toml" > backend/temp_req.txt
	@echo "# Do not edit manually - run 'make export-requirements' to update" >> backend/temp_req.txt
	@echo "# Or use 'uv export --no-dev --format requirements-txt > requirements.txt'" >> backend/temp_req.txt
	@echo "" >> backend/temp_req.txt
	@cat backend/requirements.txt >> backend/temp_req.txt
	@mv backend/temp_req.txt backend/requirements.txt
	@echo "✓ Exported production requirements to backend/requirements.txt"

export-dev-requirements: ## Export all requirements (including dev) to backend requirements-dev.txt
	cd backend && uv export --format requirements-txt > requirements-dev.txt
	@echo "# This file is auto-generated from pyproject.toml (includes dev dependencies)" > backend/temp_req.txt
	@echo "# Do not edit manually - run 'make export-dev-requirements' to update" >> backend/temp_req.txt
	@echo "# Or use 'uv export --format requirements-txt > requirements-dev.txt'" >> backend/temp_req.txt
	@echo "" >> backend/temp_req.txt
	@cat backend/requirements-dev.txt >> backend/temp_req.txt
	@mv backend/temp_req.txt backend/requirements-dev.txt
	@echo "✓ Exported all requirements to backend/requirements-dev.txt"

clean: ## Clean up temporary files and caches
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete