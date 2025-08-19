# Docker Setup Guide

This project supports multiple Docker configurations to accommodate both traditional pip and modern uv package management workflows.

## Available Dockerfiles

### 1. `Dockerfile` (Default - Hybrid Approach)
- **Purpose**: Production-ready image with automatic uv/pip detection
- **Features**:
  - Attempts to use uv for faster dependency installation
  - Falls back to pip if uv is not available
  - Uses exported `requirements.txt` for maximum compatibility
  - Multi-stage build for optimized image size
  - Non-root user for security
  - Health checks included

### 2. `Dockerfile.uv` (uv-Optimized)
- **Purpose**: Optimized for uv-based development workflows
- **Features**:
  - Native uv integration
  - Can install from `pyproject.toml` directly
  - Uses `uv run` for application execution
  - Faster dependency resolution and installation

## Building Images

### Standard Build (Recommended)
```bash
# Build with default Dockerfile
docker build -t python-web-service-template .

# Build with uv-optimized Dockerfile
docker build -f Dockerfile.uv -t python-web-service-template:uv .
```

### Using Docker Compose
```bash
# Start with standard Dockerfile
docker-compose up web

# Start with uv-optimized Dockerfile
docker-compose up web-uv

# Start both for comparison
docker-compose up
```

## Running Containers

### Standard Run
```bash
# Run standard image
docker run -p 8000:8000 python-web-service-template

# Run uv-optimized image
docker run -p 8000:8000 python-web-service-template:uv
```

### Development Mode
```bash
# With environment variables
docker run -p 8000:8000 \
  -e ENVIRONMENT=development \
  -e DEBUG=true \
  -e LOG_LEVEL=DEBUG \
  python-web-service-template
```

### With Volume Mounting (Development)
```bash
# Mount source code for live reloading
docker run -p 8000:8000 \
  -v $(pwd)/app:/app/app:ro \
  -e ENVIRONMENT=development \
  -e DEBUG=true \
  python-web-service-template
```

## Testing Docker Builds

Use the provided test script to validate Docker functionality:

```bash
# Make script executable
chmod +x scripts/test_docker.sh

# Run tests
./scripts/test_docker.sh
```

The test script will:
1. Build the Docker image
2. Start a container
3. Test health and root endpoints
4. Clean up resources

## Environment Variables

The following environment variables can be configured:

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `production` | Application environment |
| `DEBUG` | `false` | Enable debug mode |
| `LOG_LEVEL` | `INFO` | Logging level |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |

## Health Checks

Both Dockerfiles include health checks that:
- Check the `/health` endpoint every 30 seconds
- Allow 30 seconds for response
- Wait 5 seconds before first check
- Retry 3 times before marking as unhealthy

## Security Features

- **Non-root user**: Containers run as `appuser` for security
- **Minimal base image**: Uses `python:3.11-slim` for reduced attack surface
- **No cache directories**: Removes package manager caches to reduce image size
- **Read-only volumes**: Development mounts are read-only by default

## Troubleshooting

### Build Issues
1. **Docker daemon not running**: Start Docker Desktop or Docker service
2. **Permission denied**: Ensure Docker has proper permissions
3. **Network issues**: Check internet connection for package downloads

### Runtime Issues
1. **Port conflicts**: Change port mapping if 8000 is in use
2. **Health check failures**: Check application logs with `docker logs <container>`
3. **Environment issues**: Verify environment variables are set correctly

### Performance Optimization
1. **Use .dockerignore**: Ensure `.dockerignore` excludes unnecessary files
2. **Layer caching**: Order Dockerfile commands to maximize cache hits
3. **Multi-stage builds**: Use builder pattern for smaller production images

## CI/CD Integration

### GitHub Actions Example
```yaml
- name: Build Docker image
  run: docker build -t ${{ github.repository }}:${{ github.sha }} .

- name: Test Docker image
  run: |
    docker run -d --name test-container -p 8000:8000 ${{ github.repository }}:${{ github.sha }}
    sleep 10
    curl -f http://localhost:8000/health
    docker stop test-container
```

### Production Deployment
```bash
# Build for production
docker build --target production -t python-web-service-template:prod .

# Run in production mode
docker run -d \
  --name web-service \
  --restart unless-stopped \
  -p 80:8000 \
  -e ENVIRONMENT=production \
  python-web-service-template:prod
```