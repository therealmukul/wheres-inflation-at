#!/usr/bin/env python3
"""
FastAPI Server Validation Test

Tests FastAPI server functionality after uv migration.
"""

import subprocess
import sys
import time
import signal
import os
from typing import Optional


class FastAPIServerTester:
    """Test FastAPI server functionality."""
    
    def __init__(self):
        self.server_process: Optional[subprocess.Popen] = None
        
    def start_server(self, use_uv: bool = True) -> bool:
        """Start the FastAPI server."""
        try:
            if use_uv:
                cmd = ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
            else:
                cmd = ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
            
            print(f"Starting server with command: {' '.join(cmd)}")
            
            self.server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=os.setsid if os.name != 'nt' else None
            )
            
            # Wait for server to start
            print("Waiting for server to start...")
            time.sleep(5)
            
            # Check if process is still running
            if self.server_process.poll() is None:
                print("✅ Server started successfully")
                return True
            else:
                stdout, stderr = self.server_process.communicate()
                print(f"❌ Server failed to start")
                print(f"STDOUT: {stdout}")
                print(f"STDERR: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return False
    
    def test_endpoints(self) -> bool:
        """Test server endpoints."""
        endpoints = [
            ("/", "Root endpoint"),
            ("/health", "Health check endpoint"),
            ("/health/ready", "Readiness check endpoint"),
        ]
        
        all_passed = True
        
        for endpoint, description in endpoints:
            try:
                # Use curl to test endpoints
                result = subprocess.run(
                    ["curl", "-f", "-s", f"http://localhost:8000{endpoint}"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    print(f"✅ {description}: OK")
                    print(f"   Response: {result.stdout[:100]}...")
                else:
                    print(f"❌ {description}: FAILED")
                    print(f"   Error: {result.stderr}")
                    all_passed = False
                    
            except subprocess.TimeoutExpired:
                print(f"❌ {description}: TIMEOUT")
                all_passed = False
            except Exception as e:
                print(f"❌ {description}: ERROR - {e}")
                all_passed = False
        
        return all_passed
    
    def test_openapi_docs(self) -> bool:
        """Test OpenAPI documentation endpoints."""
        docs_endpoints = [
            ("/docs", "Swagger UI"),
            ("/redoc", "ReDoc"),
            ("/openapi.json", "OpenAPI Schema"),
        ]
        
        all_passed = True
        
        for endpoint, description in docs_endpoints:
            try:
                result = subprocess.run(
                    ["curl", "-f", "-s", f"http://localhost:8000{endpoint}"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    print(f"✅ {description}: OK")
                else:
                    # Docs might be disabled in production mode
                    print(f"⚠️  {description}: Not available (may be disabled)")
                    
            except Exception as e:
                print(f"⚠️  {description}: {e}")
        
        return all_passed
    
    def stop_server(self):
        """Stop the FastAPI server."""
        if self.server_process:
            try:
                if os.name != 'nt':
                    # Send SIGTERM to the process group
                    os.killpg(os.getpgid(self.server_process.pid), signal.SIGTERM)
                else:
                    self.server_process.terminate()
                
                # Wait for graceful shutdown
                try:
                    self.server_process.wait(timeout=5)
                    print("✅ Server stopped gracefully")
                except subprocess.TimeoutExpired:
                    # Force kill if needed
                    if os.name != 'nt':
                        os.killpg(os.getpgid(self.server_process.pid), signal.SIGKILL)
                    else:
                        self.server_process.kill()
                    print("⚠️  Server force killed")
                    
            except Exception as e:
                print(f"⚠️  Error stopping server: {e}")
            finally:
                self.server_process = None
    
    def run_tests(self, use_uv: bool = True) -> bool:
        """Run all server tests."""
        print("FastAPI Server Validation Tests")
        print("=" * 40)
        
        try:
            # Start server
            if not self.start_server(use_uv):
                return False
            
            # Test endpoints
            print("\nTesting endpoints...")
            endpoints_ok = self.test_endpoints()
            
            # Test documentation
            print("\nTesting documentation endpoints...")
            docs_ok = self.test_openapi_docs()
            
            return endpoints_ok
            
        finally:
            # Always stop server
            self.stop_server()


def main():
    """Main function."""
    tester = FastAPIServerTester()
    
    # Test with uv
    print("Testing FastAPI server with uv...")
    uv_success = tester.run_tests(use_uv=True)
    
    print("\n" + "=" * 40)
    if uv_success:
        print("✅ FastAPI server validation passed!")
        return 0
    else:
        print("❌ FastAPI server validation failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())