#!/usr/bin/env python3
"""
Migration Validation Test Runner

Master script that runs all migration validation tests in the correct order.
"""

import subprocess
import sys
import os
from pathlib import Path


class MigrationTestRunner:
    """Orchestrates all migration validation tests."""
    
    def __init__(self):
        self.test_scripts = [
            ("scripts/test_uv_migration.py", "UV Migration Validation"),
            ("scripts/test_fastapi_server.py", "FastAPI Server Validation"),
            ("scripts/test_pytest_compatibility.py", "Pytest Compatibility"),
            ("scripts/test_dev_workflow.py", "Development Workflow"),
        ]
        self.results = {}
    
    def run_test_script(self, script_path: str, test_name: str) -> bool:
        """Run a single test script."""
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print(f"Script: {script_path}")
        print(f"{'='*60}")
        
        if not os.path.exists(script_path):
            print(f"❌ Test script not found: {script_path}")
            return False
        
        try:
            # Make script executable
            os.chmod(script_path, 0o755)
            
            # Run the test script
            result = subprocess.run(
                [sys.executable, script_path],
                timeout=600  # 10 minutes timeout
            )
            
            success = result.returncode == 0
            self.results[test_name] = success
            
            if success:
                print(f"\n✅ {test_name} completed successfully")
            else:
                print(f"\n❌ {test_name} failed")
            
            return success
            
        except subprocess.TimeoutExpired:
            print(f"\n❌ {test_name} timed out")
            self.results[test_name] = False
            return False
        except Exception as e:
            print(f"\n❌ {test_name} failed with exception: {e}")
            self.results[test_name] = False
            return False
    
    def check_prerequisites(self) -> bool:
        """Check that all prerequisites are met."""
        print("Checking prerequisites...")
        
        # Check if uv is installed
        try:
            result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ UV is installed: {result.stdout.strip()}")
            else:
                print("❌ UV is not working properly")
                return False
        except FileNotFoundError:
            print("❌ UV is not installed")
            print("Please install uv first: https://docs.astral.sh/uv/getting-started/installation/")
            return False
        
        # Check if pyproject.toml exists
        if not os.path.exists("pyproject.toml"):
            print("❌ pyproject.toml not found")
            return False
        else:
            print("✅ pyproject.toml found")
        
        # Check if app directory exists
        if not os.path.exists("app"):
            print("❌ app directory not found")
            return False
        else:
            print("✅ app directory found")
        
        # Check if tests directory exists
        if not os.path.exists("tests"):
            print("❌ tests directory not found")
            return False
        else:
            print("✅ tests directory found")
        
        return True
    
    def run_all_tests(self) -> bool:
        """Run all migration validation tests."""
        print("Migration Validation Test Suite")
        print("=" * 60)
        print("This suite validates that the migration from venv to uv is successful.")
        print("It tests dependency installation, server functionality, test compatibility,")
        print("and development workflow commands.")
        print("=" * 60)
        
        # Check prerequisites
        if not self.check_prerequisites():
            print("\n❌ Prerequisites not met. Cannot run tests.")
            return False
        
        # Run all test scripts
        all_passed = True
        for script_path, test_name in self.test_scripts:
            success = self.run_test_script(script_path, test_name)
            if not success:
                all_passed = False
        
        # Print final summary
        print(f"\n{'='*60}")
        print("FINAL TEST SUMMARY")
        print(f"{'='*60}")
        
        for test_name, passed in self.results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status}: {test_name}")
        
        passed_count = sum(1 for passed in self.results.values() if passed)
        total_count = len(self.results)
        
        print(f"\nOverall: {passed_count}/{total_count} test suites passed")
        
        if all_passed:
            print("\n🎉 ALL MIGRATION VALIDATION TESTS PASSED!")
            print("The migration from venv to uv is successful.")
            print("You can now use uv for all development workflows.")
        else:
            print("\n❌ SOME MIGRATION VALIDATION TESTS FAILED!")
            print("Please review the test output above and fix any issues.")
            print("The migration may not be complete or there may be compatibility issues.")
        
        return all_passed
    
    def run_quick_test(self) -> bool:
        """Run a quick validation test."""
        print("Quick Migration Validation")
        print("=" * 40)
        
        # Just run the main migration test
        return self.run_test_script("scripts/test_uv_migration.py", "Quick UV Migration Test")


def main():
    """Main function."""
    runner = MigrationTestRunner()
    
    # Check for quick test flag
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        success = runner.run_quick_test()
    else:
        success = runner.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())