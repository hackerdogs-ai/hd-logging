#!/usr/bin/env python3
"""
OpenTelemetry Usage Example for HD Logging

This example demonstrates how to use the OpenTelemetry JSON format logging.
"""

import sys
import os
import json
from pathlib import Path

# Add the src directory to the Python path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from hd_logging import setup_logger

def main():
    """Demonstrate OpenTelemetry logging setup and usage."""
    
    print("=== OpenTelemetry Logging Example ===")
    
    # Example 1: Basic OpenTelemetry logging
    logger = setup_logger(
        "otlp_example",
        log_file_path="examples/logs/otlp_example.log",
        use_otlp_format=True,
        service_name="example-service",
        environment="development",
        service_version="1.0.0"
    )
    
    logger.info("This is a regular info message in OTLP format")
    logger.warning("This is a warning message in OTLP format")
    logger.error("This is an error message in OTLP format")
    
    # Example 2: Logging with custom attributes
    logger.info("User action performed", extra={
        "user_id": "12345",
        "action": "login",
        "ip_address": "192.168.1.1",
        "user_agent": "Mozilla/5.0..."
    })
    
    # Example 3: Exception logging with OTLP format
    try:
        # Simulate an error
        result = 10 / 0
    except ZeroDivisionError as e:
        logger.error("Division by zero error occurred", exc_info=True, extra={
            "operation": "division",
            "dividend": 10,
            "divisor": 0
        })
    
    # Example 4: Structured logging for business events
    logger.info("Order processed successfully", extra={
        "order_id": "ORD-12345",
        "customer_id": "CUST-67890",
        "amount": 99.99,
        "currency": "USD",
        "payment_method": "credit_card",
        "shipping_address": {
            "street": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "zip": "12345"
        }
    })
    
    print("\n✅ OpenTelemetry logging examples completed!")
    print("Check the 'examples/logs/otlp_example.log' file to see the JSON format.")
    
    # Show a sample of the log file content
    log_file = Path("examples/logs/otlp_example.log")
    if log_file.exists():
        print("\n--- Sample log file content ---")
        with open(log_file, 'r') as f:
            lines = f.readlines()
            for line in lines[-3:]:  # Show last 3 lines
                try:
                    # Pretty print the JSON
                    log_entry = json.loads(line.strip())
                    print(json.dumps(log_entry, indent=2))
                    print("---")
                except json.JSONDecodeError:
                    print(line.strip())

if __name__ == "__main__":
    main()

