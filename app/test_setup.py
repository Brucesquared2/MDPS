#!/usr/bin/env python3
"""
Test script to validate the FastAPI wrapper setup.
Run this to ensure everything is working correctly.
"""

import os
import sys
import time
import requests
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_success(msg):
    print(f"{GREEN}✓{RESET} {msg}")

def print_error(msg):
    print(f"{RED}✗{RESET} {msg}")

def print_info(msg):
    print(f"{YELLOW}ℹ{RESET} {msg}")

def test_imports():
    """Test that required packages can be imported."""
    print("\n=== Testing Imports ===")
    
    try:
        import fastapi
        print_success("fastapi imported")
    except ImportError as e:
        print_error(f"fastapi import failed: {e}")
        return False
    
    try:
        import uvicorn
        print_success("uvicorn imported")
    except ImportError as e:
        print_error(f"uvicorn import failed: {e}")
        return False
    
    try:
        import pydantic
        print_success("pydantic imported")
    except ImportError as e:
        print_error(f"pydantic import failed: {e}")
        return False
    
    return True

def test_app_import():
    """Test that the app can be imported."""
    print("\n=== Testing App Import ===")
    
    try:
        from app.main import app
        print_success("app.main.app imported successfully")
        return True
    except Exception as e:
        print_error(f"Failed to import app: {e}")
        return False

def test_example_callables():
    """Test that example callables work."""
    print("\n=== Testing Example Callables ===")
    
    try:
        from app.example_callables import simple_example
        result = simple_example(test="value")
        if result.get("status") == "success":
            print_success("simple_example works")
        else:
            print_error("simple_example returned unexpected result")
            return False
    except Exception as e:
        print_error(f"simple_example failed: {e}")
        return False
    
    try:
        import asyncio
        from app.example_callables import async_example
        result = asyncio.run(async_example(test="value"))
        if result.get("status") == "success":
            print_success("async_example works")
        else:
            print_error("async_example returned unexpected result")
            return False
    except Exception as e:
        print_error(f"async_example failed: {e}")
        return False
    
    return True

def test_directory_structure():
    """Test that required directories exist."""
    print("\n=== Testing Directory Structure ===")
    
    required_dirs = [
        "app",
        ".quant_runs"
    ]
    
    required_files = [
        "app/main.py",
        "app/__init__.py",
        "app/README.md",
        "app/example_callables.py",
        "app/start.sh",
        ".devcontainer/devcontainer.json",
        "requirements.txt"
    ]
    
    all_ok = True
    
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print_success(f"Directory exists: {dir_path}")
        else:
            print_error(f"Directory missing: {dir_path}")
            all_ok = False
    
    for file_path in required_files:
        if Path(file_path).exists():
            print_success(f"File exists: {file_path}")
        else:
            print_error(f"File missing: {file_path}")
            all_ok = False
    
    return all_ok

def test_server_startup():
    """Test that the server can start and respond to requests."""
    print("\n=== Testing Server Startup ===")
    
    # Set environment variable
    os.environ["MDPS_ENTRYPOINT"] = "app.example_callables:simple_example"
    
    # Start server in background
    print_info("Starting server...")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8001"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        # Test health endpoint
        response = requests.get("http://127.0.0.1:8001/health", timeout=5)
        if response.status_code == 200:
            print_success("Server started and health check passed")
            
            # Test creating a job
            response = requests.post(
                "http://127.0.0.1:8001/jobs",
                json={"parameters": {"test": "value"}},
                timeout=5
            )
            
            if response.status_code == 201:
                job_id = response.json()["job_id"]
                print_success(f"Job created: {job_id}")
                
                # Wait for job to complete
                time.sleep(3)
                
                # Check job status
                response = requests.get(f"http://127.0.0.1:8001/jobs/{job_id}", timeout=5)
                if response.status_code == 200:
                    status = response.json()["status"]
                    print_success(f"Job status retrieved: {status}")
                    
                    if status == "completed":
                        print_success("Job completed successfully")
                        return True
                    else:
                        print_error(f"Job did not complete (status: {status})")
                        return False
                else:
                    print_error(f"Failed to get job status: {response.status_code}")
                    return False
            else:
                print_error(f"Failed to create job: {response.status_code}")
                return False
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"Server request failed: {e}")
        return False
    finally:
        # Stop server
        proc.terminate()
        proc.wait(timeout=5)
        print_info("Server stopped")

def main():
    """Run all tests."""
    print("=" * 60)
    print("MDPS FastAPI Wrapper - Setup Validation")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("App Import", test_app_import),
        ("Example Callables", test_example_callables),
        ("Directory Structure", test_directory_structure),
        ("Server Startup", test_server_startup)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"{name} test failed with exception: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"{name:.<50} {status}")
    
    print("=" * 60)
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print_success("\nAll tests passed! Setup is complete and working.")
        return 0
    else:
        print_error(f"\n{total - passed} test(s) failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
