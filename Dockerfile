# Multi-stage Dockerfile supporting both uv and traditional pip installation
# Build stage
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy dependency files
COPY requirements.txt pyproject.toml ./
COPY app/ ./app/

# Install uv (optional - will be used if available)
RUN pip install uv 2>/dev/null || echo "uv not available, using pip"

# Install dependencies using uv if available, otherwise fall back to pip
# Handle editable install (-e .) by installing dependencies first, then the package
RUN if command -v uv >/dev/null 2>&1; then \
        echo "Installing dependencies with uv..." && \
        # Install dependencies excluding the editable package \
        grep -v "^-e" requirements.txt > /tmp/deps.txt && \
        uv pip install --system -r /tmp/deps.txt && \
        # Install the current package \
        uv pip install --system -e .; \
    else \
        echo "Installing dependencies with pip..." && \
        # Install dependencies excluding the editable package \
        grep -v "^-e" requirements.txt > /tmp/deps.txt && \
        pip install -r /tmp/deps.txt && \
        # Install the current package \
        pip install -e .; \
    fi

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r appuser && useradd -r -g appuser appuser

# Create app directory
WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy additional configuration files
COPY pyproject.toml ./

# Change ownership to non-root user
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]