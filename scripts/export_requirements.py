#!/usr/bin/env python3
"""
Export requirements.txt from pyproject.toml for Docker builds and CI/CD compatibility.

This script reads the pyproject.toml file and generates a requirements.txt file
that includes both production and development dependencies in the format expected
by pip and Docker builds.
"""

import subprocess
import sys
from pathlib import Path


def export_requirements():
    """Export requirements.txt from pyproject.toml using uv."""
    project_root = Path(__file__).parent.parent
    requirements_file = project_root / "requirements.txt"
    
    try:
        # Export production dependencies only (no dev dependencies for Docker)
        print("Exporting production requirements from pyproject.toml...")
        result = subprocess.run(
            ["uv", "export", "--no-dev", "--format", "requirements-txt"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Write the exported requirements to requirements.txt
        with open(requirements_file, "w") as f:
            f.write("# This file is auto-generated from pyproject.toml\n")
            f.write("# Do not edit manually - run 'python scripts/export_requirements.py' to update\n")
            f.write("# Or use 'uv export --no-dev --format requirements-txt > requirements.txt'\n\n")
            f.write(result.stdout)
        
        print(f"✓ Successfully exported requirements to {requirements_file}")
        print(f"  Found {len(result.stdout.strip().split())} dependencies")
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Error exporting requirements: {e}")
        print(f"  stdout: {e.stdout}")
        print(f"  stderr: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print("✗ Error: 'uv' command not found. Please install uv first.")
        print("  Visit: https://docs.astral.sh/uv/getting-started/installation/")
        sys.exit(1)


def export_dev_requirements():
    """Export development requirements to requirements-dev.txt."""
    project_root = Path(__file__).parent.parent
    dev_requirements_file = project_root / "requirements-dev.txt"
    
    try:
        # Export all dependencies (including dev) for development environments
        print("Exporting development requirements from pyproject.toml...")
        result = subprocess.run(
            ["uv", "export", "--format", "requirements-txt"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Write the exported requirements to requirements-dev.txt
        with open(dev_requirements_file, "w") as f:
            f.write("# This file is auto-generated from pyproject.toml (includes dev dependencies)\n")
            f.write("# Do not edit manually - run 'python scripts/export_requirements.py' to update\n")
            f.write("# Or use 'uv export --format requirements-txt > requirements-dev.txt'\n\n")
            f.write(result.stdout)
        
        print(f"✓ Successfully exported dev requirements to {dev_requirements_file}")
        print(f"  Found {len(result.stdout.strip().split())} total dependencies")
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Error exporting dev requirements: {e}")
        print(f"  stdout: {e.stdout}")
        print(f"  stderr: {e.stderr}")
        sys.exit(1)


if __name__ == "__main__":
    export_requirements()
    export_dev_requirements()
    print("\n✓ Requirements export completed successfully!")
    print("  - requirements.txt: Production dependencies for Docker/CI")
    print("  - requirements-dev.txt: All dependencies for development")