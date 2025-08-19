#!/bin/bash
# Activation script for the Python Web Service Template (uv-powered)

echo "🚀 Setting up Python Web Service Template with uv..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install uv first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "   or visit: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

# Sync dependencies if needed
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment and installing dependencies..."
    uv sync
else
    echo "📦 Virtual environment exists, syncing dependencies..."
    uv sync
fi

echo "✅ uv environment ready!"
echo "📦 Python version: $(uv run python --version)"
echo "📍 uv version: $(uv --version)"
echo ""
echo "🔧 Available uv commands:"
echo "  uv run python -m app.main             # Run the FastAPI server"
echo "  uv run uvicorn app.main:app --reload  # Run with auto-reload"
echo "  uv run pytest                         # Run tests"
echo "  uv add <package>                      # Add a new dependency"
echo "  uv remove <package>                   # Remove a dependency"
echo "  uv sync                               # Sync dependencies"
echo "  uv shell                              # Activate shell (optional)"
echo ""
echo "💡 Pro tip: Use 'uv run' prefix for any Python command to automatically use the project environment"
echo ""
echo "🌐 Server will be available at: http://localhost:8000"
echo "📚 API docs will be at: http://localhost:8000/docs"