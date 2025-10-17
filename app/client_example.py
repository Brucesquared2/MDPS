#!/usr/bin/env python3
"""
MDPS FastAPI Client Example

This script demonstrates how to interact with the MDPS FastAPI wrapper
from a Python client application.
"""

import requests
import time
import json
from typing import Dict, Any, Optional


class MDPSClient:
    """Client for interacting with MDPS FastAPI wrapper."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the MDPS client.
        
        Args:
            base_url: Base URL of the MDPS API server
        """
        self.base_url = base_url.rstrip('/')
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check API health status.
        
        Returns:
            Health status information
        """
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def create_job(
        self,
        parameters: Optional[Dict[str, Any]] = None,
        entrypoint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new job.
        
        Args:
            parameters: Job parameters to pass to the callable
            entrypoint: Optional entrypoint override (format: module:callable)
        
        Returns:
            Job information including job_id
        """
        data = {
            "parameters": parameters or {}
        }
        if entrypoint:
            data["entrypoint"] = entrypoint
        
        response = requests.post(
            f"{self.base_url}/jobs",
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get the status of a job.
        
        Args:
            job_id: Job identifier
        
        Returns:
            Job status information
        """
        response = requests.get(f"{self.base_url}/jobs/{job_id}")
        response.raise_for_status()
        return response.json()
    
    def list_jobs(
        self,
        status_filter: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        List all jobs.
        
        Args:
            status_filter: Optional status filter (pending, running, completed, failed)
            limit: Maximum number of jobs to return
        
        Returns:
            Jobs list and metadata
        """
        params = {"limit": limit}
        if status_filter:
            params["status_filter"] = status_filter
        
        response = requests.get(
            f"{self.base_url}/jobs",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def wait_for_job(
        self,
        job_id: str,
        timeout: int = 300,
        poll_interval: int = 2
    ) -> Dict[str, Any]:
        """
        Wait for a job to complete.
        
        Args:
            job_id: Job identifier
            timeout: Maximum time to wait in seconds
            poll_interval: Time between status checks in seconds
        
        Returns:
            Final job status
        
        Raises:
            TimeoutError: If job doesn't complete within timeout
        """
        start_time = time.time()
        
        while True:
            status = self.get_job_status(job_id)
            
            if status["status"] in ["completed", "failed"]:
                return status
            
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise TimeoutError(
                    f"Job {job_id} did not complete within {timeout} seconds"
                )
            
            time.sleep(poll_interval)
    
    def run_job_sync(
        self,
        parameters: Optional[Dict[str, Any]] = None,
        entrypoint: Optional[str] = None,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """
        Create a job and wait for it to complete.
        
        Args:
            parameters: Job parameters
            entrypoint: Optional entrypoint override
            timeout: Maximum time to wait for completion
        
        Returns:
            Job result
        
        Raises:
            TimeoutError: If job doesn't complete within timeout
            Exception: If job fails
        """
        # Create job
        job_info = self.create_job(parameters, entrypoint)
        job_id = job_info["job_id"]
        
        print(f"Job created: {job_id}")
        
        # Wait for completion
        final_status = self.wait_for_job(job_id, timeout)
        
        if final_status["status"] == "completed":
            print(f"Job completed successfully")
            return final_status
        else:
            error = final_status.get("error", "Unknown error")
            raise Exception(f"Job failed: {error}")


def example_basic_usage():
    """Example: Basic usage of the client."""
    print("=== Basic Usage Example ===\n")
    
    # Create client
    client = MDPSClient()
    
    # Check health
    health = client.health_check()
    print(f"API Status: {health['status']}")
    print(f"Active Jobs: {health['active_jobs']}\n")
    
    # Create a job
    job = client.create_job(
        parameters={"test": "value", "number": 42}
    )
    print(f"Job ID: {job['job_id']}")
    print(f"Status: {job['status']}\n")
    
    # Wait for completion
    print("Waiting for job to complete...")
    final_status = client.wait_for_job(job['job_id'])
    
    print(f"Final Status: {final_status['status']}")
    if final_status['result']:
        print(f"Result: {json.dumps(final_status['result'], indent=2)}\n")


def example_custom_entrypoint():
    """Example: Using a custom entrypoint."""
    print("=== Custom Entrypoint Example ===\n")
    
    client = MDPSClient()
    
    # Create job with custom entrypoint
    job = client.create_job(
        parameters={"test": "async"},
        entrypoint="app.example_callables:async_example"
    )
    print(f"Job ID: {job['job_id']}")
    
    # Wait for completion
    final_status = client.wait_for_job(job['job_id'])
    print(f"Status: {final_status['status']}")
    print(f"Result: {json.dumps(final_status['result'], indent=2)}\n")


def example_sync_execution():
    """Example: Synchronous job execution."""
    print("=== Synchronous Execution Example ===\n")
    
    client = MDPSClient()
    
    try:
        # Run job and wait for result
        result = client.run_job_sync(
            parameters={"symbol": "EURUSD", "timeframe": "H1"}
        )
        print(f"Result: {json.dumps(result['result'], indent=2)}\n")
    except Exception as e:
        print(f"Job failed: {e}\n")


def example_list_jobs():
    """Example: Listing jobs."""
    print("=== List Jobs Example ===\n")
    
    client = MDPSClient()
    
    # List all jobs
    all_jobs = client.list_jobs(limit=5)
    print(f"Total Jobs: {all_jobs['total']}")
    print(f"Showing: {all_jobs['count']}\n")
    
    for job in all_jobs['jobs']:
        print(f"Job {job['job_id'][:8]}... - Status: {job['status']}")
    
    print()
    
    # List only completed jobs
    completed = client.list_jobs(status_filter="completed", limit=5)
    print(f"Completed Jobs: {completed['count']}")
    for job in completed['jobs']:
        print(f"Job {job['job_id'][:8]}... - Completed at: {job['completed_at']}")
    
    print()


def example_error_handling():
    """Example: Handling errors."""
    print("=== Error Handling Example ===\n")
    
    client = MDPSClient()
    
    # Create a job that will fail
    job = client.create_job(
        entrypoint="app.example_callables:failing_example"
    )
    print(f"Created job that will fail: {job['job_id']}")
    
    # Wait and handle failure
    final_status = client.wait_for_job(job['job_id'])
    
    if final_status['status'] == 'failed':
        print(f"Job failed as expected")
        print(f"Error: {final_status['error']}\n")


def main():
    """Run all examples."""
    print("=" * 60)
    print("MDPS FastAPI Client Examples")
    print("=" * 60)
    print()
    
    try:
        # Run examples
        example_basic_usage()
        example_custom_entrypoint()
        example_sync_execution()
        example_list_jobs()
        example_error_handling()
        
        print("=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to MDPS API server.")
        print("Make sure the server is running:")
        print("  ./app/start.sh")
        print("or")
        print("  uvicorn app.main:app --host 0.0.0.0 --port 8000")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
