# Migration Validation Testing

This document describes the test suite for validating the migration from venv to uv.

## Overview

The migration validation test suite ensures that:
1. All dependencies install correctly with uv
2. FastAPI server functionality works with uv
3. All existing pytest tests pass with uv
4. Development workflow commands work properly

## Test Scripts

### Main Test Runner
- `scripts/run_migration_tests.py` - Master test runner that orchestrates all tests

### Individual Test Scripts
- `scripts/test_uv_migration.py` - Comprehensive UV migration validation
- `scripts/test_fastapi_server.py` - FastAPI server functionality tests
- `scripts/test_pytest_compatibility.py` - Pytest compatibility validation
- `scripts/test_dev_workflow.py` - Development workflow command tests

## Running Tests

### Run All Tests
```bash
python scripts/run_migration_tests.py
```

### Run Quick Test
```bash
python scripts/run_migration_tests.py --quick
```

### Run Individual Tests
```bash
# Test UV migration
python scripts/test_uv_migration.py

# Test FastAPI server
python scripts/test_fastapi_server.py

# Test pytest compatibility
python scripts/test_pytest_compatibility.py

# Test development workflow
python scripts/test_dev_workflow.py
```

## Prerequisites

Before running the tests, ensure:
1. UV is installed (`uv --version` works)
2. `pyproject.toml` exists in the project root
3. `app/` directory exists with the FastAPI application
4. `tests/` directory exists with pytest tests

## Test Categories

### 1. Dependency Installation Tests
- Verifies uv can install production dependencies
- Verifies uv can install development dependencies
- Tests requirements export functionality
- Validates dependency resolution

### 2. FastAPI Server Tests
- Tests server startup with uv
- Validates health endpoints
- Tests API documentation endpoints
- Ensures server can be stopped gracefully

### 3. Pytest Compatibility Tests
- Runs existing test suite with uv
- Tests module imports
- Validates individual test files
- Checks for test failures or errors

### 4. Development Workflow Tests
- Tests basic uv commands
- Validates project management commands
- Tests dependency management
- Verifies Python execution with uv
- Tests development tool integration
- Validates environment isolation

## Expected Results

All tests should pass for a successful migration. If any tests fail:

1. Check the detailed error output
2. Ensure uv is properly installed and configured
3. Verify all dependencies are correctly specified in `pyproject.toml`
4. Check for any compatibility issues with existing code

## Troubleshooting

### UV Not Found
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
# or
pip install uv
```

### Dependency Issues
```bash
# Sync dependencies
uv sync

# Export requirements for debugging
uv export --no-hashes > requirements-debug.txt
```

### Server Issues
```bash
# Test server manually
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

# Check logs
uv run python -c "import app.main; print('Import OK')"
```

### Test Issues
```bash
# Run tests manually
uv run pytest -v

# Test specific file
uv run pytest tests/test_health.py -v
```

## Integration with CI/CD

These tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions step
- name: Run Migration Tests
  run: python scripts/run_migration_tests.py
```

## Maintenance

The test suite should be updated when:
- New dependencies are added
- New API endpoints are created
- New test files are added
- Development workflow changes