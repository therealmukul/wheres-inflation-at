# Python Web Service Template

A production-ready Python web service template built with FastAPI. This template provides a solid foundation for building REST APIs with essential features like health checks, CRUD operations, proper error handling, and comprehensive testing.

## Features

- **FastAPI Framework**: Modern, fast web framework for building APIs
- **Modern Dependency Management**: Uses uv for fast, reliable package management
- **Health Check Endpoints**: Built-in health monitoring for load balancers
- **Structured Logging**: Configurable logging with JSON output for production
- **Error Handling**: Comprehensive error handling with structured responses
- **Configuration Management**: Environment-based configuration with validation
- **API Documentation**: Automatic OpenAPI/Swagger documentation
- **Testing Suite**: Comprehensive test coverage with pytest
- **Development Tools**: Hot reload, debugging support, and development utilities

## Quick Start

### Prerequisites

- Python 3.9+
- uv (modern Python package manager)

### Installation

1. Install uv (if not already installed):
```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or using pip
pip install uv
```

2. Clone the repository:
```bash
git clone <repository-url>
cd python-web-service-template
```

3. Install dependencies and create virtual environment:
```bash
uv sync
```

4. Create environment configuration:
```bash
cp .env.example .env
# Edit .env with your configuration
```

The project uses `pyproject.toml` for dependency management and project configuration. Dependencies are automatically installed when you run `uv sync`.

### Running the Service

#### Development Mode
```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Production Mode
```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### Using the convenience script
```bash
./activate.sh
```

### API Documentation

Once the service is running, you can access:

- **Interactive API docs**: http://localhost:8000/docs
- **ReDoc documentation**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## API Endpoints

### Health Checks
- `GET /health` - Service health status
- `GET /health/ready` - Readiness check for load balancers

### Root
- `GET /` - Basic service information

## Project Structure

```
├── app/
│   ├── __init__.py
│   ├── main.py              # Application entry point
│   ├── config.py            # Configuration management
│   ├── models/
│   │   ├── __init__.py
│   │   └── health.py        # Pydantic models
│   ├── routers/
│   │   ├── __init__.py
│   │   └── health.py        # Health check endpoints
│   └── utils/
│       ├── __init__.py
│       ├── logging.py       # Logging configuration
│       └── exceptions.py    # Custom exceptions
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures
│   └── test_health.py       # Health endpoint tests
├── .env.example             # Environment variables template
├── pyproject.toml           # Project configuration and dependencies
├── uv.lock                  # Lock file for reproducible builds
├── requirements.txt         # Dependencies (exported for compatibility)
└── README.md               # This file
```

## Configuration

The service uses environment variables for configuration. Copy `.env.example` to `.env` and modify as needed:

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000

# Application Configuration
APP_NAME=Python Web Service Template
VERSION=1.0.0
ENVIRONMENT=development
DEBUG=false

# Logging Configuration
LOG_LEVEL=INFO

# CORS Configuration (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Testing

Run the test suite:

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app

# Run specific test file
uv run pytest tests/test_health.py

# Run with verbose output
uv run pytest -v
```

## Development

### Dependency Management

Add new dependencies:
```bash
# Add a production dependency
uv add fastapi

# Add a development dependency
uv add --dev pytest

# Remove a dependency
uv remove package-name

# Update all dependencies
uv sync --upgrade
```

### Requirements.txt Export

For compatibility with Docker builds and CI/CD systems that expect requirements.txt, this project includes automated export mechanisms:

```bash
# Export production dependencies only (for Docker)
make export-requirements

# Export all dependencies including dev dependencies
make export-dev-requirements

# Manual export using uv directly
uv export --no-dev --format requirements-txt > requirements.txt
uv export --format requirements-txt > requirements-dev.txt
```

The exported requirements.txt files are automatically updated when pyproject.toml changes through:
- **Pre-commit hooks**: Automatically sync requirements.txt when pyproject.toml is modified
- **GitHub Actions**: CI workflow that updates requirements.txt on pushes to main/develop branches
- **Manual export**: Use the Makefile commands or Python script

**Important**: Do not edit requirements.txt manually - it's auto-generated from pyproject.toml

### Adding New Endpoints

1. Create a new router in `app/routers/`
2. Define Pydantic models in `app/models/`
3. Add business logic in `app/services/` (if needed)
4. Register the router in `app/main.py`
5. Add tests in `tests/`

### Code Style

The project follows Python best practices:
- PEP 8 style guide
- Type hints for better code documentation
- Docstrings for functions and classes
- Structured error handling

### Troubleshooting

#### uv not found
If you get "command not found: uv", make sure uv is installed and in your PATH:
```bash
# Check if uv is installed
uv --version

# If not installed, install it
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Virtual environment issues
If you encounter virtual environment issues, you can recreate it:
```bash
# Remove existing environment
rm -rf .venv

# Recreate and sync
uv sync
```

## Deployment

### Docker (Recommended)

This project includes Docker support with both uv-optimized and traditional pip-compatible configurations.

#### Quick Start with Docker

```bash
# Build and run with Docker Compose (recommended)
docker-compose up

# Or build and run manually
docker build -t python-web-service-template .
docker run -p 8000:8000 python-web-service-template
```

#### Available Docker Configurations

1. **`Dockerfile`** (Default - Hybrid approach)
   - Automatically detects and uses uv if available
   - Falls back to pip for maximum compatibility
   - Uses exported requirements.txt for reliable builds
   - Multi-stage build for optimized production images

2. **`Dockerfile.uv`** (uv-optimized)
   - Native uv integration for fastest builds
   - Direct pyproject.toml support
   - Uses `uv run` for application execution

#### Docker Compose Services

```bash
# Standard Docker build
docker-compose up web

# uv-optimized build
docker-compose up web-uv

# Run both for comparison
docker-compose up
```

#### Testing Docker Setup

Validate your Docker configuration:

```bash
# Validate Dockerfile syntax and best practices
python3 scripts/validate_docker.py

# Run comprehensive Docker tests (without Docker daemon)
python3 scripts/test_docker_mock.py

# Full Docker build and runtime test (requires Docker)
./scripts/test_docker.sh
```

For detailed Docker documentation, see [docs/docker.md](docs/docker.md).

### Environment Variables for Production

Set these environment variables in your production environment:

- `ENVIRONMENT=production`
- `DEBUG=false`
- `LOG_LEVEL=INFO`
- `HOST=0.0.0.0`
- `PORT=8000`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions and support, please open an issue in the repository.