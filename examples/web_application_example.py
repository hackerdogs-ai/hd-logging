#!/usr/bin/env python3
"""
Web Application Integration Example for HD Logging

This example demonstrates how to integrate HD Logging into a web application
using Flask as an example framework.
"""

import sys
import os
import time
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Add the src directory to the Python path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from hd_logging import setup_logger

# Simulate Flask-like request handling
class MockRequest:
    def __init__(self, method: str, path: str, remote_addr: str, user_agent: str):
        self.method = method
        self.path = path
        self.remote_addr = remote_addr
        self.user_agent = user_agent
        self.headers = {"User-Agent": user_agent}

class MockResponse:
    def __init__(self, status_code: int, data: Any = None):
        self.status_code = status_code
        self.data = data

class WebApplicationLogger:
    """A web application logger that demonstrates best practices."""
    
    def __init__(self, app_name: str = "web_app"):
        self.app_name = app_name
        self.logger = setup_logger(
            app_name,
            log_file_path=f"examples/logs/{app_name}.log",
            use_otlp_format=True,
            service_name=app_name,
            environment="production",
            service_version="1.0.0"
        )
    
    def log_request(self, request: MockRequest, response: MockResponse, 
                   duration_ms: float, user_id: Optional[str] = None):
        """Log HTTP request/response with timing and user context."""
        
        # Extract request information
        request_data = {
            "method": request.method,
            "path": request.path,
            "remote_addr": request.remote_addr,
            "user_agent": request.user_agent,
            "status_code": response.status_code,
            "duration_ms": duration_ms
        }
        
        # Add user context if available
        if user_id:
            request_data["user_id"] = user_id
        
        # Log based on status code
        if response.status_code >= 500:
            self.logger.error("Server error", extra=request_data)
        elif response.status_code >= 400:
            self.logger.warning("Client error", extra=request_data)
        else:
            self.logger.info("Request completed", extra=request_data)
    
    def log_authentication(self, user_id: str, action: str, success: bool, 
                          ip_address: str, user_agent: str):
        """Log authentication events."""
        
        auth_data = {
            "user_id": user_id,
            "action": action,
            "success": success,
            "ip_address": ip_address,
            "user_agent": user_agent
        }
        
        if success:
            self.logger.info("Authentication successful", extra=auth_data)
        else:
            self.logger.warning("Authentication failed", extra=auth_data)
    
    def log_business_event(self, event_type: str, user_id: str, 
                          event_data: Dict[str, Any]):
        """Log business events."""
        
        business_data = {
            "event_type": event_type,
            "user_id": user_id,
            **event_data
        }
        
        self.logger.info(f"Business event: {event_type}", extra=business_data)
    
    def log_database_operation(self, operation: str, table: str, 
                              duration_ms: float, rows_affected: int = None):
        """Log database operations."""
        
        db_data = {
            "operation": operation,
            "table": table,
            "duration_ms": duration_ms,
            "rows_affected": rows_affected
        }
        
        self.logger.info("Database operation", extra=db_data)
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """Log errors with context."""
        
        error_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            **(context or {})
        }
        
        self.logger.error("Application error", exc_info=True, extra=error_data)

def simulate_web_application():
    """Simulate a web application with various logging scenarios."""
    
    print("=== Web Application Logging Example ===")
    
    # Initialize the web application logger
    app_logger = WebApplicationLogger("demo_web_app")
    
    # Simulate various web application scenarios
    
    # 1. User authentication
    print("\n1. Simulating user authentication...")
    app_logger.log_authentication(
        user_id="user_12345",
        action="login",
        success=True,
        ip_address="192.168.1.100",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    
    # 2. HTTP requests
    print("\n2. Simulating HTTP requests...")
    
    # Successful API request
    request1 = MockRequest("GET", "/api/users/12345", "192.168.1.100", 
                          "Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    response1 = MockResponse(200, {"user_id": "12345", "name": "John Doe"})
    app_logger.log_request(request1, response1, 45.2, user_id="user_12345")
    
    # Failed API request
    request2 = MockRequest("POST", "/api/users", "192.168.1.101", 
                          "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)")
    response2 = MockResponse(400, {"error": "Invalid email format"})
    app_logger.log_request(request2, response2, 12.8)
    
    # Server error
    request3 = MockRequest("GET", "/api/orders", "192.168.1.102", 
                          "Mozilla/5.0 (X11; Linux x86_64)")
    response3 = MockResponse(500, {"error": "Internal server error"})
    app_logger.log_request(request3, response3, 1200.5, user_id="user_67890")
    
    # 3. Business events
    print("\n3. Simulating business events...")
    
    app_logger.log_business_event(
        "order_created",
        "user_12345",
        {
            "order_id": "ORD-12345",
            "amount": 99.99,
            "currency": "USD",
            "items": 3,
            "payment_method": "credit_card"
        }
    )
    
    app_logger.log_business_event(
        "user_profile_updated",
        "user_12345",
        {
            "profile_fields": ["email", "phone"],
            "update_source": "user_dashboard"
        }
    )
    
    # 4. Database operations
    print("\n4. Simulating database operations...")
    
    app_logger.log_database_operation(
        "SELECT",
        "users",
        25.5,
        rows_affected=1
    )
    
    app_logger.log_database_operation(
        "INSERT",
        "orders",
        45.2,
        rows_affected=1
    )
    
    app_logger.log_database_operation(
        "UPDATE",
        "user_profiles",
        67.8,
        rows_affected=1
    )
    
    # 5. Error handling
    print("\n5. Simulating error scenarios...")
    
    try:
        # Simulate a database connection error
        raise ConnectionError("Database connection timeout")
    except Exception as e:
        app_logger.log_error(e, {
            "operation": "database_connection",
            "database": "postgresql",
            "host": "db.example.com",
            "port": 5432
        })
    
    try:
        # Simulate a validation error
        raise ValueError("Invalid email format: missing @ symbol")
    except Exception as e:
        app_logger.log_error(e, {
            "operation": "user_validation",
            "field": "email",
            "value": "invalid-email"
        })
    
    # 6. Performance monitoring
    print("\n6. Simulating performance monitoring...")
    
    # Simulate a slow operation
    start_time = time.time()
    time.sleep(0.1)  # Simulate work
    end_time = time.time()
    
    app_logger.logger.info("Performance metric", extra={
        "metric_name": "api_response_time",
        "value": (end_time - start_time) * 1000,
        "unit": "milliseconds",
        "endpoint": "/api/users",
        "method": "GET"
    })
    
    print("\n✅ Web application logging examples completed!")
    print("Check the 'examples/logs/demo_web_app.log' file for detailed logs.")

def main():
    """Main function to run the web application example."""
    simulate_web_application()

if __name__ == "__main__":
    main()

