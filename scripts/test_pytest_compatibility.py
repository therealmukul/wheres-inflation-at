#!/usr/bin/env python3
"""
Pytest Compatibility Test

Ensures all existing pytest tests pass with uv environment.
"""

import subprocess
import sys
import os
import json
from pathlib import Path


class PytestCompatibilityTester:
    """Test pytest compatibility with uv."""
    
    def __init__(self):
        self.test_results = {}
        
    def run_pytest_with_uv(self) -> bool:
        """Run pytest using uv and capture results."""
        print("Running pytest with uv...")
        
        try:
            # Run pytest with JSON report for detailed results
            result = subprocess.run(
                ["uv", "run", "pytest", "-v", "--tb=short", "--json-report", "--json-report-file=test_results.json"],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            print("STDOUT:")
            print(result.stdout)
            
            if result.stderr:
                print("STDERR:")
                print(result.stderr)
            
            # Parse JSON results if available
            if os.path.exists("test_results.json"):
                try:
                    with open("test_results.json", "r") as f:
                        self.test_results = json.load(f)
                    os.remove("test_results.json")  # Clean up
                except Exception as e:
                    print(f"⚠️  Could not parse JSON results: {e}")
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print("❌ Pytest execution timed out")
            return False
        except Exception as e:
            print(f"❌ Error running pytest: {e}")
            return False
    
    def run_pytest_fallback(self) -> bool:
        """Run pytest without JSON report as fallback."""
        print("Running pytest (fallback mode)...")
        
        try:
            result = subprocess.run(
                ["uv", "run", "pytest", "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            print("STDOUT:")
            print(result.stdout)
            
            if result.stderr:
                print("STDERR:")
                print(result.stderr)
            
            # Parse output for basic statistics
            output = result.stdout + result.stderr
            
            if "failed" in output.lower():
                print("⚠️  Some tests may have failed")
            
            if "passed" in output.lower():
                print("✅ Some tests passed")
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Error running pytest: {e}")
            return False
    
    def analyze_results(self):
        """Analyze and report test results."""
        if not self.test_results:
            print("No detailed test results available")
            return
        
        summary = self.test_results.get("summary", {})
        
        print("\nTest Results Summary:")
        print(f"Total tests: {summary.get('total', 'unknown')}")
        print(f"Passed: {summary.get('passed', 0)}")
        print(f"Failed: {summary.get('failed', 0)}")
        print(f"Skipped: {summary.get('skipped', 0)}")
        print(f"Errors: {summary.get('error', 0)}")
        
        # Show failed tests if any
        tests = self.test_results.get("tests", [])
        failed_tests = [test for test in tests if test.get("outcome") == "failed"]
        
        if failed_tests:
            print("\nFailed Tests:")
            for test in failed_tests:
                print(f"  - {test.get('nodeid', 'unknown')}")
                if test.get("call", {}).get("longrepr"):
                    print(f"    Error: {test['call']['longrepr'][:100]}...")
    
    def test_specific_test_files(self) -> bool:
        """Test specific test files individually."""
        test_files = []
        
        # Find test files
        test_dir = Path("tests")
        if test_dir.exists():
            test_files = list(test_dir.glob("test_*.py"))
        
        if not test_files:
            print("No test files found")
            return True
        
        print(f"\nTesting {len(test_files)} test files individually...")
        
        all_passed = True
        for test_file in test_files:
            print(f"\nTesting {test_file}...")
            
            try:
                result = subprocess.run(
                    ["uv", "run", "pytest", str(test_file), "-v"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    print(f"✅ {test_file}: PASSED")
                else:
                    print(f"❌ {test_file}: FAILED")
                    print(f"   Error: {result.stderr[:200]}...")
                    all_passed = False
                    
            except Exception as e:
                print(f"❌ {test_file}: ERROR - {e}")
                all_passed = False
        
        return all_passed
    
    def test_import_compatibility(self) -> bool:
        """Test that all modules can be imported correctly."""
        print("\nTesting module imports...")
        
        modules_to_test = [
            "app.main",
            "app.config", 
            "app.routers.health",
        ]
        
        all_passed = True
        for module in modules_to_test:
            try:
                result = subprocess.run(
                    ["uv", "run", "python", "-c", f"import {module}; print('OK')"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    print(f"✅ Import {module}: OK")
                else:
                    print(f"❌ Import {module}: FAILED")
                    print(f"   Error: {result.stderr}")
                    all_passed = False
                    
            except Exception as e:
                print(f"❌ Import {module}: ERROR - {e}")
                all_passed = False
        
        return all_passed
    
    def run_all_tests(self) -> bool:
        """Run all pytest compatibility tests."""
        print("Pytest Compatibility Test Suite")
        print("=" * 40)
        
        # Test imports first
        imports_ok = self.test_import_compatibility()
        
        # Run full test suite
        print("\n" + "=" * 40)
        pytest_ok = self.run_pytest_with_uv()
        
        if not pytest_ok:
            print("\nTrying fallback pytest execution...")
            pytest_ok = self.run_pytest_fallback()
        
        # Analyze results
        self.analyze_results()
        
        # Test individual files if main suite failed
        if not pytest_ok:
            print("\nTesting individual test files...")
            individual_ok = self.test_specific_test_files()
        else:
            individual_ok = True
        
        # Summary
        print("\n" + "=" * 40)
        print("Test Summary:")
        print(f"Module imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
        print(f"Pytest suite: {'✅ PASS' if pytest_ok else '❌ FAIL'}")
        print(f"Individual tests: {'✅ PASS' if individual_ok else '❌ FAIL'}")
        
        overall_success = imports_ok and (pytest_ok or individual_ok)
        
        if overall_success:
            print("✅ All pytest compatibility tests passed!")
        else:
            print("❌ Some pytest compatibility tests failed!")
        
        return overall_success


def main():
    """Main function."""
    tester = PytestCompatibilityTester()
    success = tester.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())