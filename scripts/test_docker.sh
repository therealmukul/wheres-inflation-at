#!/bin/bash
# Docker build and test script for uv compatibility

set -e

echo "Testing Docker build for uv compatibility..."

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed or not in PATH"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo "Docker daemon is not running. Please start Docker and try again."
    exit 1
fi

# Build the Docker image
echo "Building Docker image..."
docker build -t python-web-service-template:test .

# Test the image
echo "Testing Docker image..."
docker run --rm -d --name test-container -p 8001:8000 python-web-service-template:test

# Wait for container to start
sleep 5

# Test health endpoint
echo "Testing health endpoint..."
if curl -f http://localhost:8001/health; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
    docker logs test-container
    docker stop test-container
    exit 1
fi

# Test root endpoint
echo "Testing root endpoint..."
if curl -f http://localhost:8001/; then
    echo "✅ Root endpoint test passed"
else
    echo "❌ Root endpoint test failed"
    docker logs test-container
    docker stop test-container
    exit 1
fi

# Clean up
echo "Cleaning up..."
docker stop test-container
docker rmi python-web-service-template:test

echo "✅ All Docker tests passed!"