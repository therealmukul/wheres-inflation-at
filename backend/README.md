# Backend API Service

This is the FastAPI backend service that provides health check endpoints and serves as the API layer for the application.

## Features

- FastAPI web framework with automatic API documentation
- Health check endpoints (`/health` and `/health/ready`)
- Comprehensive error handling and logging
- CORS support for frontend integration
- Environment-based configuration
- Docker support with multi-stage builds

## Quick Start

### Prerequisites

- Python 3.9+
- uv (recommended) or pip

### Installation

1. Install dependencies:
   ```bash
   # Using uv (recommended)
   uv sync
   
   # Or using pip
   pip install -r requirements.txt
   ```

2. Run the development server:
   ```bash
   # Using uv
   uv run python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   
   # Or using python directly
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. Access the API:
   - Health endpoint: http://localhost:8000/health
   - API documentation: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

## Configuration

The application uses environment variables for configuration. Create a `.env` file in the backend directory:

```env
# Server configuration
HOST=0.0.0.0
PORT=8000

# Application configuration
APP_NAME="Backend API Service"
VERSION=1.0.0
ENVIRONMENT=development
DEBUG=true

# Logging
LOG_LEVEL=INFO

# CORS origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## API Endpoints

### Health Endpoints

- `GET /health` - Basic health check
- `GET /health/ready` - Readiness check

### Root Endpoint

- `GET /` - Application information

## Development

### Running Tests

```bash
# Using uv
uv run pytest

# Or using pytest directly
pytest
```

### Code Quality

The project includes pre-commit hooks for code quality:

```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Docker

### Build and Run

```bash
# Build the image
docker build -t backend-api .

# Run the container
docker run -p 8000:8000 backend-api
```

### Using Docker Compose

From the root directory:

```bash
docker-compose up backend
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── models/              # Pydantic models
│   ├── routers/             # API route handlers
│   ├── services/            # Business logic
│   └── utils/               # Utility functions
├── tests/                   # Test files
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
├── pyproject.toml          # Project configuration
├── Dockerfile              # Docker configuration
└── README.md               # This file
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| HOST | 0.0.0.0 | Server host |
| PORT | 8000 | Server port |
| APP_NAME | Python Web Service Template | Application name |
| VERSION | 1.0.0 | Application version |
| ENVIRONMENT | development | Environment |
| DEBUG | false | Debug mode |
| LOG_LEVEL | INFO | Logging level |
| CORS_ORIGINS | http://localhost:3000,http://localhost:8080 | Allowed CORS origins |