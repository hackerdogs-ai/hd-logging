#!/usr/bin/env python3
"""
Standard Logging Format Example for HD Logging

This example demonstrates the standard (non-OTLP) logging format output.
Shows traditional log format with timestamps, levels, and structured information.
"""

import sys
import os
import time
import logging
from pathlib import Path

# Add the src directory to the Python path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from hd_logging import setup_logger

def main():
    """Demonstrate standard logging format (non-OTLP)."""
    
    print("=== Standard Logging Format Example ===")
    print("This example shows traditional log format (non-OTLP JSON)")
    print()
    
    # Example 1: Basic standard logging
    print("1. Basic Standard Logging")
    print("-" * 40)
    
    logger = setup_logger(
        "standard_example",
        log_file_path="examples/logs/standard_format.log",
        use_otlp_format=False,  # Explicitly disable OTLP format
        service_name="standard-service",
        environment="development",
        service_version="1.0.0"
    )
    
    logger.info("This is a standard format info message")
    logger.warning("This is a standard format warning message")
    logger.error("This is a standard format error message")
    logger.debug("This is a debug message in standard format")
    
    # Example 2: Logging with extra context
    print("\n2. Logging with Extra Context")
    print("-" * 40)
    
    logger.info("User login attempt", extra={
        "user_id": "12345",
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "login_method": "password"
    })
    
    logger.warning("Failed login attempt", extra={
        "user_id": "12345",
        "ip_address": "192.168.1.100",
        "attempt_count": 3,
        "reason": "invalid_password"
    })
    
    # Example 3: Exception logging
    print("\n3. Exception Logging")
    print("-" * 40)
    
    try:
        # Simulate an error
        result = 10 / 0
    except ZeroDivisionError as e:
        logger.error("Division by zero error occurred", exc_info=True, extra={
            "operation": "division",
            "dividend": 10,
            "divisor": 0,
            "error_type": "ZeroDivisionError"
        })
    
    # Example 4: Business logic logging
    print("\n4. Business Logic Logging")
    print("-" * 40)
    
    # Simulate order processing
    order_id = "ORD-12345"
    customer_id = "CUST-67890"
    amount = 99.99
    
    logger.info("Order processing started", extra={
        "order_id": order_id,
        "customer_id": customer_id,
        "amount": amount,
        "currency": "USD"
    })
    
    # Simulate processing steps
    time.sleep(0.1)  # Simulate work
    
    logger.info("Payment processed successfully", extra={
        "order_id": order_id,
        "payment_method": "credit_card",
        "transaction_id": "TXN-789",
        "processing_time_ms": 100
    })
    
    logger.info("Order completed", extra={
        "order_id": order_id,
        "status": "completed",
        "total_processing_time_ms": 150
    })
    
    # Example 5: Performance monitoring
    print("\n5. Performance Monitoring")
    print("-" * 40)
    
    start_time = time.time()
    
    # Simulate some work
    time.sleep(0.05)
    
    end_time = time.time()
    duration_ms = (end_time - start_time) * 1000
    
    logger.info("Operation completed", extra={
        "operation_name": "data_processing",
        "duration_ms": duration_ms,
        "memory_usage_mb": 45.2,
        "cpu_usage_percent": 12.5,
        "records_processed": 1000
    })
    
    # Example 6: Different log levels demonstration
    print("\n6. Different Log Levels")
    print("-" * 40)
    
    logger.debug("Debug message - detailed information for debugging")
    logger.info("Info message - general information about program execution")
    logger.warning("Warning message - something unexpected happened")
    logger.error("Error message - a serious problem occurred")
    logger.critical("Critical message - a very serious error occurred")
    
    print("\n✅ Standard logging examples completed!")
    print("Check the 'examples/logs/standard_format.log' file to see the standard format.")
    
    # Show a sample of the log file content
    log_file = Path("examples/logs/standard_format.log")
    if log_file.exists():
        print("\n--- Sample log file content (Standard Format) ---")
        with open(log_file, 'r') as f:
            lines = f.readlines()
            for line in lines[-5:]:  # Show last 5 lines
                print(line.strip())
        print("---")
        
        print(f"\nLog file size: {log_file.stat().st_size} bytes")
        print(f"Total log entries: {len(lines)}")

if __name__ == "__main__":
    main()
