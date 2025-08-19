#!/usr/bin/env python3
"""
Development Workflow Test

Tests development workflow commands with uv to ensure smooth developer experience.
"""

import subprocess
import sys
import os
import tempfile
import shutil
from pathlib import Path


class DevWorkflowTester:
    """Test development workflow with uv."""
    
    def __init__(self):
        self.test_results = []
        
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result."""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"    {message}")
        
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "message": message
        })
    
    def run_command(self, cmd: list, timeout: int = 60, cwd: str = None) -> tuple:
        """Run a command and return (success, stdout, stderr)."""
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=timeout,
                cwd=cwd
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", f"Command timed out after {timeout}s"
        except Exception as e:
            return False, "", str(e)
    
    def test_uv_basic_commands(self) -> bool:
        """Test basic uv commands."""
        print("\n--- Testing Basic UV Commands ---")
        
        commands = [
            (["uv", "--version"], "UV Version"),
            (["uv", "--help"], "UV Help"),
            (["uv", "python", "list"], "UV Python List"),
        ]
        
        all_passed = True
        for cmd, name in commands:
            success, stdout, stderr = self.run_command(cmd)
            if success:
                self.log_test(name, True, stdout.split('\n')[0] if stdout else "OK")
            else:
                self.log_test(name, False, stderr)
                all_passed = False
        
        return all_passed
    
    def test_project_management(self) -> bool:
        """Test project management commands."""
        print("\n--- Testing Project Management ---")
        
        # Test uv sync (check help since dry-run may not be available)
        success, stdout, stderr = self.run_command(["uv", "sync", "--help"])
        if success:
            self.log_test("UV Sync Command", True, "Project sync command available")
        else:
            self.log_test("UV Sync Command", False, stderr)
            return False
        
        # Test uv lock
        success, stdout, stderr = self.run_command(["uv", "lock", "--help"])
        if success:
            self.log_test("UV Lock Command", True, "Lock file generation command available")
        else:
            self.log_test("UV Lock Command", False, stderr)
        
        # Test uv export
        success, stdout, stderr = self.run_command(["uv", "export"])
        if success:
            lines = stdout.strip().split('\n')
            deps = [line for line in lines if line and not line.startswith('#')]
            self.log_test("UV Export", True, f"Exported {len(deps)} dependencies")
        else:
            self.log_test("UV Export", False, stderr)
        
        return True
    
    def test_dependency_management(self) -> bool:
        """Test dependency management commands."""
        print("\n--- Testing Dependency Management ---")
        
        # Create temporary project for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Copy pyproject.toml
            shutil.copy("pyproject.toml", temp_dir)
            
            # Test uv add (check help since dry-run may not be available)
            success, stdout, stderr = self.run_command(
                ["uv", "add", "--help"], 
                cwd=temp_dir
            )
            if success:
                self.log_test("UV Add Command", True, "Package addition command available")
            else:
                self.log_test("UV Add Command", False, stderr)
            
            # Test uv remove (check help)
            success, stdout, stderr = self.run_command(
                ["uv", "remove", "--help"], 
                cwd=temp_dir
            )
            if success:
                self.log_test("UV Remove Command", True, "Package removal command available")
            else:
                self.log_test("UV Remove Command", False, stderr)
        
        return True
    
    def test_python_execution(self) -> bool:
        """Test Python execution with uv."""
        print("\n--- Testing Python Execution ---")
        
        # Test uv run python
        success, stdout, stderr = self.run_command(["uv", "run", "python", "--version"])
        if success:
            self.log_test("UV Run Python", True, stdout.strip())
        else:
            self.log_test("UV Run Python", False, stderr)
            return False
        
        # Test uv run with module
        success, stdout, stderr = self.run_command(["uv", "run", "python", "-c", "print('Hello from uv')"])
        if success and "Hello from uv" in stdout:
            self.log_test("UV Run Python Script", True, "Python execution works")
        else:
            self.log_test("UV Run Python Script", False, stderr)
            return False
        
        # Test uv run with app module
        success, stdout, stderr = self.run_command(["uv", "run", "python", "-c", "import app; print('App import OK')"])
        if success:
            self.log_test("UV Run App Import", True, "App module imports correctly")
        else:
            self.log_test("UV Run App Import", False, stderr)
        
        return True
    
    def test_development_tools(self) -> bool:
        """Test development tools integration."""
        print("\n--- Testing Development Tools ---")
        
        # Test pytest
        success, stdout, stderr = self.run_command(["uv", "run", "pytest", "--version"])
        if success:
            self.log_test("Pytest Integration", True, stdout.strip())
        else:
            self.log_test("Pytest Integration", False, stderr)
        
        # Test uvicorn
        success, stdout, stderr = self.run_command(["uv", "run", "uvicorn", "--version"])
        if success:
            self.log_test("Uvicorn Integration", True, stdout.strip())
        else:
            self.log_test("Uvicorn Integration", False, stderr)
        
        # Test pre-commit if available
        if os.path.exists(".pre-commit-config.yaml"):
            success, stdout, stderr = self.run_command(["uv", "run", "pre-commit", "--version"])
            if success:
                self.log_test("Pre-commit Integration", True, stdout.strip())
            else:
                self.log_test("Pre-commit Integration", False, stderr)
        
        return True
    
    def test_environment_isolation(self) -> bool:
        """Test environment isolation."""
        print("\n--- Testing Environment Isolation ---")
        
        # Test that uv creates isolated environment
        success, stdout, stderr = self.run_command(["uv", "run", "python", "-c", "import sys; print(sys.executable)"])
        if success:
            if ".venv" in stdout or "uv" in stdout:
                self.log_test("Environment Isolation", True, "Using isolated environment")
            else:
                self.log_test("Environment Isolation", False, "May be using system Python")
        else:
            self.log_test("Environment Isolation", False, stderr)
        
        # Test package availability
        success, stdout, stderr = self.run_command(["uv", "run", "python", "-c", "import fastapi; print(fastapi.__version__)"])
        if success:
            self.log_test("Package Availability", True, f"FastAPI version: {stdout.strip()}")
        else:
            self.log_test("Package Availability", False, "FastAPI not available")
        
        return True
    
    def test_common_workflows(self) -> bool:
        """Test common development workflows."""
        print("\n--- Testing Common Workflows ---")
        
        # Test: Install dependencies and run tests
        workflow_commands = [
            (["uv", "sync"], "Dependency Installation"),
            (["uv", "run", "python", "-m", "pytest", "--version"], "Test Runner Setup"),
        ]
        
        all_passed = True
        for cmd, name in workflow_commands:
            success, stdout, stderr = self.run_command(cmd, timeout=120)
            if success:
                self.log_test(name, True, "Workflow step completed")
            else:
                self.log_test(name, False, stderr)
                all_passed = False
        
        return all_passed
    
    def test_performance_comparison(self) -> bool:
        """Test performance of uv vs traditional pip."""
        print("\n--- Testing Performance ---")
        
        import time
        
        # Time uv sync
        start_time = time.time()
        success, stdout, stderr = self.run_command(["uv", "sync"], timeout=180)
        uv_time = time.time() - start_time
        
        if success:
            self.log_test("UV Sync Performance", True, f"Completed in {uv_time:.2f}s")
        else:
            self.log_test("UV Sync Performance", False, "Sync failed")
        
        return success
    
    def run_all_tests(self) -> bool:
        """Run all development workflow tests."""
        print("Development Workflow Test Suite")
        print("=" * 50)
        
        test_categories = [
            self.test_uv_basic_commands,
            self.test_project_management,
            self.test_dependency_management,
            self.test_python_execution,
            self.test_development_tools,
            self.test_environment_isolation,
            self.test_common_workflows,
            self.test_performance_comparison,
        ]
        
        all_passed = True
        for test_category in test_categories:
            try:
                if not test_category():
                    all_passed = False
            except Exception as e:
                print(f"❌ Test category failed with exception: {e}")
                all_passed = False
        
        # Print summary
        print("\n" + "=" * 50)
        print("Test Summary:")
        
        passed_tests = sum(1 for result in self.test_results if result["passed"])
        total_tests = len(self.test_results)
        
        print(f"Passed: {passed_tests}/{total_tests}")
        
        if all_passed:
            print("✅ All development workflow tests passed!")
            print("The development workflow with uv is working correctly.")
        else:
            print("❌ Some development workflow tests failed.")
            
            # Show failed tests
            failed_tests = [result for result in self.test_results if not result["passed"]]
            if failed_tests:
                print("\nFailed tests:")
                for test in failed_tests:
                    print(f"  - {test['test']}: {test['message']}")
        
        return all_passed


def main():
    """Main function."""
    tester = DevWorkflowTester()
    success = tester.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())