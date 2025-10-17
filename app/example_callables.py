#!/usr/bin/env python3
"""
Example MDPS Callable for Testing
Demonstrates how to create a callable that works with the FastAPI wrapper.
"""

import time
import asyncio
from typing import Dict, Any


def simple_example(**kwargs) -> Dict[str, Any]:
    """
    Simple synchronous example callable.
    
    Args:
        **kwargs: Arbitrary keyword arguments
    
    Returns:
        Dictionary with results
    """
    print("Simple example starting...")
    print(f"Received parameters: {kwargs}")
    
    # Simulate some work
    time.sleep(2)
    
    result = {
        "status": "success",
        "message": "Simple example completed",
        "parameters": kwargs,
        "timestamp": time.time()
    }
    
    print(f"Simple example completed: {result}")
    return result


async def async_example(**kwargs) -> Dict[str, Any]:
    """
    Asynchronous example callable.
    
    Args:
        **kwargs: Arbitrary keyword arguments
    
    Returns:
        Dictionary with results
    """
    print("Async example starting...")
    print(f"Received parameters: {kwargs}")
    
    # Simulate async work
    await asyncio.sleep(2)
    
    result = {
        "status": "success",
        "message": "Async example completed",
        "parameters": kwargs,
        "timestamp": time.time()
    }
    
    print(f"Async example completed: {result}")
    return result


def failing_example(**kwargs) -> Dict[str, Any]:
    """
    Example callable that fails (for testing error handling).
    
    Args:
        **kwargs: Arbitrary keyword arguments
    
    Raises:
        ValueError: Always raises an error
    """
    print("Failing example starting...")
    print(f"Received parameters: {kwargs}")
    
    # Simulate some work before failing
    time.sleep(1)
    
    # Intentionally fail
    raise ValueError("This is an intentional test failure")


def long_running_example(**kwargs) -> Dict[str, Any]:
    """
    Long-running example callable.
    
    Args:
        **kwargs: Arbitrary keyword arguments
    
    Returns:
        Dictionary with results
    """
    duration = kwargs.get("duration", 30)
    print(f"Long-running example starting (duration: {duration}s)...")
    print(f"Received parameters: {kwargs}")
    
    # Simulate long-running work
    for i in range(int(duration)):
        print(f"Progress: {i+1}/{duration}")
        time.sleep(1)
    
    result = {
        "status": "success",
        "message": f"Long-running example completed after {duration}s",
        "parameters": kwargs,
        "timestamp": time.time()
    }
    
    print(f"Long-running example completed: {result}")
    return result


class CallableClass:
    """
    Example callable class.
    Demonstrates using a class with __call__ method.
    """
    
    def __init__(self):
        self.call_count = 0
    
    def __call__(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the callable.
        
        Args:
            **kwargs: Arbitrary keyword arguments
        
        Returns:
            Dictionary with results
        """
        self.call_count += 1
        
        print(f"CallableClass executing (call #{self.call_count})...")
        print(f"Received parameters: {kwargs}")
        
        # Simulate some work
        time.sleep(2)
        
        result = {
            "status": "success",
            "message": f"CallableClass completed (call #{self.call_count})",
            "parameters": kwargs,
            "call_count": self.call_count,
            "timestamp": time.time()
        }
        
        print(f"CallableClass completed: {result}")
        return result


# Create an instance for use as callable
callable_instance = CallableClass()


if __name__ == "__main__":
    # Test the examples
    print("=== Testing simple_example ===")
    result = simple_example(test_param="test_value")
    print(f"Result: {result}\n")
    
    print("=== Testing async_example ===")
    result = asyncio.run(async_example(test_param="test_value"))
    print(f"Result: {result}\n")
    
    print("=== Testing callable_instance ===")
    result = callable_instance(test_param="test_value")
    print(f"Result: {result}\n")
    
    print("=== Testing failing_example ===")
    try:
        result = failing_example(test_param="test_value")
    except ValueError as e:
        print(f"Expected error: {e}\n")
    
    print("All tests completed!")
