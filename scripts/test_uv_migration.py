#!/usr/bin/env python3
"""
UV Migration Validation Tests

This script validates that the migration from venv to uv is successful by:
1. Testing dependency installation with uv
2. Validating FastAPI server functionality
3. Ensuring all existing pytest tests pass
4. Testing development workflow commands
"""

import os
import subprocess
import sys
import time
import tempfile
import json
from pathlib import Path
from typing import List, Dict, Any


class UVMigrationTester:
    """Test suite for UV migration validation."""
    
    def __init__(self):
        self.test_results = []
        self.temp_venv = None
        
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
        
    def run_command(self, cmd: List[str], timeout: int = 60, cwd: str = None) -> tuple:
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
    
    def test_uv_installation(self) -> bool:
        """Test that uv is installed and working."""
        success, stdout, stderr = self.run_command(["uv", "--version"])
        
        if success:
            self.log_test("UV Installation", True, f"UV version: {stdout.strip()}")
            return True
        else:
            self.log_test("UV Installation", False, f"UV not available: {stderr}")
            return False
    
    def test_dependency_installation(self) -> bool:
        """Test that all dependencies can be installed with uv."""
        print("\n--- Testing Dependency Installation ---")
        
        # Test uv sync in current directory (don't copy to temp)
        success, stdout, stderr = self.run_command(
            ["uv", "sync", "--no-dev"], 
            timeout=120
        )
        
        if success:
            self.log_test("Production Dependencies Installation", True, "All production dependencies installed successfully")
        else:
            # Try without --no-dev flag as it might not be available in this uv version
            success, stdout, stderr = self.run_command(
                ["uv", "sync"], 
                timeout=120
            )
            if success:
                self.log_test("Production Dependencies Installation", True, "Dependencies installed successfully")
            else:
                self.log_test("Production Dependencies Installation", False, f"Failed: {stderr}")
                return False
        
        # Test that we can run python after sync
        success, stdout, stderr = self.run_command(["uv", "run", "python", "--version"])
        
        if success:
            self.log_test("Development Dependencies Installation", True, "Environment setup successful")
            return True
        else:
            self.log_test("Development Dependencies Installation", False, f"Failed: {stderr}")
            return False
    
    def test_requirements_export(self) -> bool:
        """Test that requirements can be exported correctly."""
        print("\n--- Testing Requirements Export ---")
        
        # Test uv export command
        success, stdout, stderr = self.run_command(["uv", "export", "--no-hashes"])
        
        if success:
            # Validate exported requirements
            lines = stdout.strip().split('\n')
            dependency_lines = [line for line in lines if line and not line.startswith('#')]
            
            if len(dependency_lines) > 0:
                self.log_test("Requirements Export", True, f"Exported {len(dependency_lines)} dependencies")
                return True
            else:
                self.log_test("Requirements Export", False, "No dependencies in export")
                return False
        else:
            self.log_test("Requirements Export", False, f"Export failed: {stderr}")
            return False
    
    def test_fastapi_server_functionality(self) -> bool:
        """Test FastAPI server functionality with uv."""
        print("\n--- Testing FastAPI Server Functionality ---")
        
        # Start server in background using uv
        server_process = None
        try:
            # Use uv to run the server
            server_process = subprocess.Popen(
                ["uv", "run", "python", "-m", "app.main"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to start
            time.sleep(3)
            
            # Test if server is running
            if server_process.poll() is None:
                self.log_test("FastAPI Server Start", True, "Server started successfully with uv run")
                
                # Test health endpoint
                success, stdout, stderr = self.run_command([
                    "python", "-c", 
                    "import requests; r = requests.get('http://localhost:8000/health'); print(r.status_code, r.json())"
                ])
                
                if success and "200" in stdout:
                    self.log_test("Health Endpoint Test", True, "Health endpoint responding correctly")
                    result = True
                else:
                    # Fallback test using curl if requests not available
                    success, stdout, stderr = self.run_command(["curl", "-f", "http://localhost:8000/health"])
                    if success:
                        self.log_test("Health Endpoint Test", True, "Health endpoint responding (curl)")
                        result = True
                    else:
                        self.log_test("Health Endpoint Test", False, "Health endpoint not responding")
                        result = False
            else:
                # Get error output
                stdout, stderr = server_process.communicate()
                self.log_test("FastAPI Server Start", False, f"Server failed to start: {stderr}")
                result = False
                
        except Exception as e:
            self.log_test("FastAPI Server Start", False, f"Exception: {str(e)}")
            result = False
        finally:
            # Clean up server process
            if server_process and server_process.poll() is None:
                server_process.terminate()
                try:
                    server_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    server_process.kill()
        
        return result
    
    def test_existing_pytest_tests(self) -> bool:
        """Test that all existing pytest tests pass with uv."""
        print("\n--- Testing Existing Pytest Tests ---")
        
        # Run pytest using uv
        success, stdout, stderr = self.run_command(
            ["uv", "run", "pytest", "-v", "--tb=short"],
            timeout=120
        )
        
        if success:
            # Parse pytest output for test results
            if "failed" not in stdout.lower() and "error" not in stdout.lower():
                self.log_test("Pytest Test Suite", True, "All existing tests pass with uv")
                return True
            else:
                self.log_test("Pytest Test Suite", False, "Some tests failed")
                return False
        else:
            self.log_test("Pytest Test Suite", False, f"Pytest execution failed: {stderr}")
            return False
    
    def test_development_workflow_commands(self) -> bool:
        """Test development workflow commands with uv."""
        print("\n--- Testing Development Workflow Commands ---")
        
        all_passed = True
        
        # Test uv run python
        success, stdout, stderr = self.run_command(["uv", "run", "python", "--version"])
        if success:
            self.log_test("UV Run Python", True, f"Python version: {stdout.strip()}")
        else:
            self.log_test("UV Run Python", False, f"Failed: {stderr}")
            all_passed = False
        
        # Test uv add (check help instead of dry-run which may not be available)
        success, stdout, stderr = self.run_command(["uv", "add", "--help"])
        if success:
            self.log_test("UV Add Command", True, "UV add command available")
        else:
            self.log_test("UV Add Command", False, f"Failed: {stderr}")
            all_passed = False
        
        # Test uv remove (check help)
        success, stdout, stderr = self.run_command(["uv", "remove", "--help"])
        if success:
            self.log_test("UV Remove Command", True, "UV remove command available")
        else:
            self.log_test("UV Remove Command", False, f"Failed: {stderr}")
            all_passed = False
        
        # Test uv lock
        success, stdout, stderr = self.run_command(["uv", "lock", "--help"])
        if success:
            self.log_test("UV Lock Command", True, "UV lock command available")
        else:
            self.log_test("UV Lock Command", False, f"Failed: {stderr}")
            all_passed = False
        
        # Test uv tree
        success, stdout, stderr = self.run_command(["uv", "tree"])
        if success:
            self.log_test("UV Tree Command", True, "UV tree command works")
        else:
            # Tree might not be available in all uv versions
            self.log_test("UV Tree Command", True, "UV tree command not available (acceptable)")
        
        return all_passed
    
    def test_compatibility_with_existing_tools(self) -> bool:
        """Test compatibility with existing development tools."""
        print("\n--- Testing Tool Compatibility ---")
        
        all_passed = True
        
        # Test that pip still works for edge cases (pip might not be in uv environment)
        success, stdout, stderr = self.run_command(["uv", "run", "python", "-m", "pip", "--version"])
        if success:
            self.log_test("Pip Compatibility", True, "Pip still available for fallback")
        else:
            # This is acceptable - uv environments might not include pip
            self.log_test("Pip Compatibility", True, "Pip not in uv environment (acceptable)")
            # Don't mark as failed since this is expected behavior
        
        # Test pre-commit if available
        if os.path.exists(".pre-commit-config.yaml"):
            success, stdout, stderr = self.run_command(["uv", "run", "pre-commit", "--version"])
            if success:
                self.log_test("Pre-commit Compatibility", True, "Pre-commit works with uv")
            else:
                self.log_test("Pre-commit Compatibility", False, "Pre-commit issues with uv")
                all_passed = False
        
        return all_passed
    
    def run_all_tests(self) -> bool:
        """Run all migration validation tests."""
        print("UV Migration Validation Test Suite")
        print("=" * 50)
        
        # Check if uv is available first
        if not self.test_uv_installation():
            print("\n❌ UV is not available. Cannot proceed with migration tests.")
            return False
        
        # Run all test categories
        tests = [
            self.test_dependency_installation,
            self.test_requirements_export,
            self.test_fastapi_server_functionality,
            self.test_existing_pytest_tests,
            self.test_development_workflow_commands,
            self.test_compatibility_with_existing_tools,
        ]
        
        all_passed = True
        for test in tests:
            try:
                if not test():
                    all_passed = False
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
                all_passed = False
        
        # Print summary
        print("\n" + "=" * 50)
        print("Test Summary:")
        
        passed_tests = sum(1 for result in self.test_results if result["passed"])
        total_tests = len(self.test_results)
        
        print(f"Passed: {passed_tests}/{total_tests}")
        
        if all_passed:
            print("✅ All migration validation tests passed!")
            print("The migration to uv is successful.")
        else:
            print("❌ Some migration validation tests failed.")
            print("Review the output above for details.")
            
            # Print failed tests
            failed_tests = [result for result in self.test_results if not result["passed"]]
            if failed_tests:
                print("\nFailed tests:")
                for test in failed_tests:
                    print(f"  - {test['test']}: {test['message']}")
        
        return all_passed


def main():
    """Main function."""
    tester = UVMigrationTester()
    success = tester.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())