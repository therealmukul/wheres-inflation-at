# Requirements.txt Export Mechanism

This document explains how the project maintains compatibility with Docker builds and CI/CD systems that expect `requirements.txt` files while using `pyproject.toml` as the primary dependency management source.

## Overview

The project uses `uv` and `pyproject.toml` for modern Python dependency management, but exports `requirements.txt` files for backward compatibility with:

- Docker builds that expect `pip install -r requirements.txt`
- CI/CD systems that haven't migrated to uv yet
- Legacy deployment scripts
- Third-party tools that require requirements.txt

## Export Methods

### 1. Makefile Commands (Recommended)

```bash
# Export production dependencies only
make export-requirements

# Export all dependencies (including dev)
make export-dev-requirements
```

### 2. Python Script

```bash
# Run the export script directly
python scripts/export_requirements.py
```

### 3. Manual uv Commands

```bash
# Production dependencies only
uv export --no-dev --format requirements-txt > requirements.txt

# All dependencies (including dev)
uv export --format requirements-txt > requirements-dev.txt
```

## Automated Synchronization

### Pre-commit Hooks

The project includes a pre-commit hook that automatically updates `requirements.txt` when `pyproject.toml` is modified:

```yaml
# .pre-commit-config.yaml
- id: sync-requirements
  name: Sync requirements.txt from pyproject.toml
  entry: bash -c 'if [ -f pyproject.toml ]; then make export-requirements; fi'
  language: system
  files: pyproject.toml
```

To enable pre-commit hooks:

```bash
# Install pre-commit (if not already installed)
uv add --dev pre-commit

# Install the hooks
uv run pre-commit install
```

### GitHub Actions

The CI workflow automatically updates `requirements.txt` when `pyproject.toml` changes:

- Triggers on pushes to main/develop branches
- Triggers on pull requests that modify pyproject.toml
- Automatically commits updated requirements.txt back to the repository

### Manual Sync

If automated sync fails or you need to manually update:

```bash
# Quick sync using Makefile
make export-requirements

# Or use the Python script
python scripts/export_requirements.py
```

## File Structure

```
├── requirements.txt          # Production dependencies (auto-generated)
├── requirements-dev.txt      # All dependencies including dev (auto-generated)
├── pyproject.toml           # Source of truth for dependencies
├── scripts/
│   └── export_requirements.py  # Export script
├── Makefile                 # Convenient export commands
└── .github/workflows/
    └── sync-requirements.yml   # CI automation
```

## Docker Integration

### Option 1: Use uv in Docker (Recommended)

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy project files
COPY pyproject.toml uv.lock ./
COPY app/ ./app/

# Install dependencies
RUN uv sync --frozen --no-cache

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Option 2: Use exported requirements.txt

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Use exported requirements.txt for compatibility
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## CI/CD Integration

### GitHub Actions Example

```yaml
- name: Install dependencies
  run: |
    # Option 1: Use uv (recommended)
    uv sync
    
    # Option 2: Use exported requirements.txt
    pip install -r requirements.txt
```

### Jenkins/GitLab CI Example

```bash
# Use exported requirements.txt for compatibility
pip install -r requirements.txt
```

## Troubleshooting

### Requirements.txt Out of Sync

If `requirements.txt` is out of sync with `pyproject.toml`:

```bash
# Re-export requirements
make export-requirements

# Commit the changes
git add requirements.txt requirements-dev.txt
git commit -m "Update requirements.txt from pyproject.toml"
```

### Pre-commit Hook Issues

If the pre-commit hook fails:

```bash
# Check pre-commit installation
uv run pre-commit --version

# Reinstall hooks
uv run pre-commit uninstall
uv run pre-commit install

# Test the hook
uv run pre-commit run sync-requirements
```

### CI Workflow Issues

If the GitHub Actions workflow fails:

1. Check that uv is properly installed in the workflow
2. Verify the workflow has write permissions to commit changes
3. Ensure the workflow is triggered on the correct file changes

## Best Practices

1. **Never edit requirements.txt manually** - it will be overwritten
2. **Always modify dependencies in pyproject.toml**
3. **Run export after dependency changes** during development
4. **Commit both pyproject.toml and requirements.txt** together
5. **Test Docker builds** after dependency changes
6. **Keep requirements-dev.txt** for development environment setup

## Migration Notes

When migrating from requirements.txt to this system:

1. Import existing requirements: `uv add $(cat requirements.txt)`
2. Separate dev dependencies in pyproject.toml
3. Export new requirements.txt: `make export-requirements`
4. Update Docker/CI configurations as needed
5. Set up automated sync mechanisms