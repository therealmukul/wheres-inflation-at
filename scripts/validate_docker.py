#!/usr/bin/env python3
"""
Dockerfile validation script for uv compatibility.
Validates Dockerfile syntax and checks for common issues.
"""

import os
import re
import sys
from pathlib import Path


def validate_dockerfile(dockerfile_path):
    """Validate Dockerfile syntax and best practices."""
    print(f"Validating {dockerfile_path}...")
    
    if not os.path.exists(dockerfile_path):
        print(f"❌ {dockerfile_path} not found")
        return False
    
    with open(dockerfile_path, 'r') as f:
        content = f.read()
    
    issues = []
    warnings = []
    
    # Check for required instructions
    required_instructions = ['FROM', 'WORKDIR', 'COPY', 'EXPOSE', 'CMD']
    for instruction in required_instructions:
        if not re.search(rf'^{instruction}\s+', content, re.MULTILINE | re.IGNORECASE):
            issues.append(f"Missing required instruction: {instruction}")
    
    # Check for security best practices
    if not re.search(r'USER\s+\w+', content, re.MULTILINE):
        warnings.append("Consider adding USER instruction for security")
    
    # Check for health check
    if not re.search(r'HEALTHCHECK', content, re.MULTILINE):
        warnings.append("Consider adding HEALTHCHECK instruction")
    
    # Check for proper COPY usage
    if re.search(r'COPY\s+\.\s+', content, re.MULTILINE):
        warnings.append("Consider using specific COPY paths instead of copying everything")
    
    # Check for uv-specific patterns
    if 'uv' in content:
        print("✅ uv support detected")
        if not re.search(r'pip.*uv|uv.*pip', content):
            warnings.append("Consider adding pip fallback for uv installation")
    
    # Check for requirements.txt handling
    if 'requirements.txt' in content:
        print("✅ requirements.txt support detected")
        if '-e .' in open('requirements.txt').read():
            if not re.search(r'grep.*-e.*requirements', content):
                warnings.append("requirements.txt contains -e . but Dockerfile doesn't handle it properly")
    
    # Print results
    if issues:
        print("❌ Issues found:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    
    if warnings:
        print("⚠️  Warnings:")
        for warning in warnings:
            print(f"  - {warning}")
    
    print("✅ Dockerfile validation passed")
    return True


def validate_dockerignore():
    """Validate .dockerignore file."""
    print("Validating .dockerignore...")
    
    if not os.path.exists('.dockerignore'):
        print("⚠️  .dockerignore not found - consider creating one for better build performance")
        return True
    
    with open('.dockerignore', 'r') as f:
        content = f.read()
    
    recommended_patterns = [
        '.git', '__pycache__', '*.pyc', '.pytest_cache', 
        '.venv', 'venv/', '.env', 'tests/', '*.md'
    ]
    
    missing_patterns = []
    for pattern in recommended_patterns:
        if pattern not in content:
            missing_patterns.append(pattern)
    
    if missing_patterns:
        print("⚠️  Consider adding these patterns to .dockerignore:")
        for pattern in missing_patterns:
            print(f"  - {pattern}")
    
    print("✅ .dockerignore validation completed")
    return True


def validate_requirements():
    """Validate requirements.txt compatibility with Docker."""
    print("Validating requirements.txt...")
    
    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt not found")
        return False
    
    with open('requirements.txt', 'r') as f:
        content = f.read()
    
    # Check for editable installs
    if '-e .' in content:
        print("✅ Editable install detected - ensure Dockerfile handles this properly")
    
    # Check for hash verification
    if '--hash=' in content:
        print("✅ Hash verification detected for security")
    
    # Check for platform-specific dependencies
    if 'sys_platform' in content or 'platform_system' in content:
        print("✅ Platform-specific dependencies detected")
    
    print("✅ requirements.txt validation completed")
    return True


def main():
    """Main validation function."""
    print("Docker Configuration Validation")
    print("=" * 40)
    
    all_valid = True
    
    # Validate Dockerfiles
    dockerfiles = ['Dockerfile', 'Dockerfile.uv']
    for dockerfile in dockerfiles:
        if os.path.exists(dockerfile):
            if not validate_dockerfile(dockerfile):
                all_valid = False
        else:
            print(f"⚠️  {dockerfile} not found")
    
    print()
    
    # Validate .dockerignore
    validate_dockerignore()
    print()
    
    # Validate requirements.txt
    if not validate_requirements():
        all_valid = False
    
    print()
    print("=" * 40)
    if all_valid:
        print("✅ All validations passed!")
        return 0
    else:
        print("❌ Some validations failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())