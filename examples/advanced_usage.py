#!/usr/bin/env python3
"""
Advanced Usage Example for HD Logging

This example demonstrates advanced features like log rotation, custom formatters,
and integration with different logging scenarios.
"""

import sys
import os
import time
import logging
from pathlib import Path
from typing import Dict, Any

# Add the src directory to the Python path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from hd_logging import setup_logger, OpenTelemetryFormatter, SizeAndTimeLoggingHandler

def simulate_high_volume_logging(logger: logging.Logger, num_messages: int = 100):
    """Simulate high volume logging to test rotation."""
    for i in range(num_messages):
        logger.info(f"High volume log message {i+1}/{num_messages}")
        if i % 10 == 0:
            logger.warning(f"Warning message at iteration {i}")
        if i % 25 == 0:
            logger.error(f"Error message at iteration {i}")
        time.sleep(0.01)  # Small delay to simulate real usage

def main():
    """Demonstrate advanced logging features."""
    
    print("=== Advanced Logging Features Example ===")
    
    # Example 1: Custom log rotation settings
    print("\n1. Custom log rotation with size and time limits...")
    rotation_logger = setup_logger(
        "rotation_example",
        log_file_path="examples/logs/rotation_example.log",
        log_level_console=logging.INFO,
        log_level_files=logging.DEBUG
    )
    
    # Simulate some logging to test rotation
    for i in range(50):
        rotation_logger.info(f"Rotation test message {i+1}")
        if i % 10 == 0:
            rotation_logger.warning(f"Warning at message {i+1}")
    
    # Example 2: Multiple loggers for different components
    print("\n2. Multiple loggers for different components...")
    
    # API service logger
    api_logger = setup_logger(
        "api_service",
        log_file_path="examples/logs/api_service.log",
        service_name="api-service",
        environment="production",
        service_version="1.2.3"
    )
    
    # Database service logger
    db_logger = setup_logger(
        "database_service", 
        log_file_path="examples/logs/database_service.log",
        service_name="database-service",
        environment="production",
        service_version="2.1.0"
    )
    
    # Background task logger
    task_logger = setup_logger(
        "background_tasks",
        log_file_path="examples/logs/background_tasks.log",
        service_name="task-processor",
        environment="production", 
        service_version="1.0.5"
    )
    
    # Simulate different service activities
    api_logger.info("API request received", extra={
        "endpoint": "/api/users",
        "method": "GET",
        "user_id": "12345",
        "ip_address": "192.168.1.100"
    })
    
    db_logger.info("Database query executed", extra={
        "query_type": "SELECT",
        "table": "users",
        "execution_time_ms": 45,
        "rows_returned": 1
    })
    
    task_logger.info("Background task completed", extra={
        "task_id": "task_789",
        "task_type": "email_send",
        "duration_seconds": 2.5,
        "status": "success"
    })
    
    # Example 3: Error handling and exception logging
    print("\n3. Error handling and exception logging...")
    
    error_logger = setup_logger(
        "error_handler",
        log_file_path="examples/logs/error_handler.log"
    )
    
    # Simulate different types of errors
    try:
        # Simulate a file not found error
        with open("nonexistent_file.txt", "r") as f:
            content = f.read()
    except FileNotFoundError as e:
        error_logger.error("File not found error", exc_info=True, extra={
            "file_path": "nonexistent_file.txt",
            "operation": "file_read"
        })
    
    try:
        # Simulate a network error
        import requests
        response = requests.get("http://nonexistent-domain.com/api")
    except Exception as e:
        error_logger.error("Network request failed", exc_info=True, extra={
            "url": "http://nonexistent-domain.com/api",
            "error_type": type(e).__name__
        })
    
    # Example 4: Performance monitoring
    print("\n4. Performance monitoring with logging...")
    
    perf_logger = setup_logger(
        "performance_monitor",
        log_file_path="examples/logs/performance.log",
        use_otlp_format=True
    )
    
    # Simulate performance monitoring
    start_time = time.time()
    
    # Simulate some work
    time.sleep(0.1)
    
    end_time = time.time()
    duration = end_time - start_time
    
    perf_logger.info("Operation completed", extra={
        "operation_name": "data_processing",
        "duration_ms": duration * 1000,
        "memory_usage_mb": 45.2,
        "cpu_usage_percent": 12.5
    })
    
    # Example 5: Business logic logging
    print("\n5. Business logic logging...")
    
    business_logger = setup_logger(
        "business_logic",
        log_file_path="examples/logs/business.log",
        use_otlp_format=True
    )
    
    # Simulate business events
    business_logger.info("User registration completed", extra={
        "user_id": "user_12345",
        "email": "user@example.com",
        "registration_method": "email",
        "referral_code": "REF123",
        "marketing_source": "google_ads"
    })
    
    business_logger.info("Payment processed", extra={
        "transaction_id": "txn_67890",
        "amount": 99.99,
        "currency": "USD",
        "payment_method": "credit_card",
        "customer_id": "cust_12345"
    })
    
    business_logger.warning("Low inventory alert", extra={
        "product_id": "prod_456",
        "current_stock": 5,
        "minimum_threshold": 10,
        "warehouse": "warehouse_west"
    })
    
    print("\n✅ Advanced logging examples completed!")
    print("Check the 'examples/logs/' directory for all generated log files.")
    
    # Show log file sizes
    log_dir = Path("examples/logs")
    if log_dir.exists():
        print("\n--- Log file sizes ---")
        for log_file in log_dir.glob("*.log"):
            size_kb = log_file.stat().st_size / 1024
            print(f"{log_file.name}: {size_kb:.2f} KB")

if __name__ == "__main__":
    main()

