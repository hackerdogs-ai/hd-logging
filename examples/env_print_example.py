#!/usr/bin/env python3
"""
Environment Print Module Example

This example demonstrates how to use the env_print.py module functions
for logging environment variables with sensitive data masking.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from hd_logging import (
    get_env_vars_with_masking,
    log_env_vars_with_masking,
    log_dotenv_vars_with_masking,
    get_dotenv_vars_with_masking,
    env_print
)

def main():
    """Demonstrate env_print module functionality."""
    
    print("=== Environment Print Module Example ===")
    print("This example shows how to use env_print.py functions directly")
    print()
    
    # Set up some test environment variables
    print("1. Setting up test environment variables...")
    os.environ["TEST_API_KEY"] = "sk-1234567890abcdef"
    os.environ["DATABASE_PASSWORD"] = "super_secret_password_123"
    os.environ["SECRET_TOKEN"] = "very_secret_token_xyz"
    os.environ["NORMAL_CONFIG"] = "normal_value"
    os.environ["APP_NAME"] = "hd-logging-demo"
    os.environ["DEBUG_MODE"] = "true"
    
    print("✅ Test environment variables set")
    print()
    
    # Example 1: Get environment variables with masking (no logging)
    print("2. Getting environment variables with masking (no logging)...")
    print("-" * 60)
    
    env_vars = get_env_vars_with_masking()
    print(f"Found {len(env_vars)} environment variables")
    
    # Show a few examples
    print("\nSample masked variables:")
    for key, value in list(env_vars.items())[:5]:
        print(f"  {key} = {value}")
    
    print()
    
    # Example 2: Log environment variables with masking
    print("3. Logging environment variables with masking...")
    print("-" * 60)
    print("(This will create logs in 'logs/env_print.log')")
    print()
    
    log_env_vars_with_masking()
    
    print()
    
    # Example 3: Log .env file variables (if exists)
    print("4. Logging .env file variables with masking...")
    print("-" * 60)
    print("(This will check for .env file and log its contents)")
    print()
    
    log_dotenv_vars_with_masking()
    
    print()
    
    # Example 4: Get .env variables with masking (no logging)
    print("5. Getting .env variables with masking (no logging)...")
    print("-" * 60)
    
    dotenv_vars = get_dotenv_vars_with_masking()
    if dotenv_vars:
        print(f"Found {len(dotenv_vars)} variables in .env file")
        for key, value in list(dotenv_vars.items())[:3]:
            print(f"  {key} = {value}")
    else:
        print("No .env file found or empty")
    
    print()
    
    # Example 5: Using the convenience alias
    print("6. Using convenience alias 'env_print'...")
    print("-" * 60)
    print("(This is the same as log_env_vars_with_masking)")
    print()
    
    env_print()
    
    print()
    
    # Example 6: Demonstrate sensitive data detection
    print("7. Demonstrating sensitive data detection...")
    print("-" * 60)
    
    # Add more test variables with different patterns
    test_vars = {
        "API_SECRET_KEY": "secret_api_key_123",
        "DB_PASSWORD": "database_password_456",
        "JWT_SECRET": "jwt_secret_token_789",
        "NORMAL_VAR": "this_is_not_sensitive",
        "CONFIG_VALUE": "regular_config_value"
    }
    
    for key, value in test_vars.items():
        os.environ[key] = value
    
    print("Added test variables with different sensitivity patterns")
    print("Running final environment variable logging...")
    print()
    
    log_env_vars_with_masking()
    
    print()
    
    # Example 7: Show log file information
    print("8. Log file information...")
    print("-" * 60)
    
    log_file = Path("logs/env_print.log")
    if log_file.exists():
        file_size = log_file.stat().st_size
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        print(f"Log file: {log_file}")
        print(f"File size: {file_size} bytes")
        print(f"Total log entries: {len(lines)}")
        print()
        print("Last 3 log entries:")
        for line in lines[-3:]:
            print(f"  {line.strip()}")
    else:
        print("Log file not found: logs/env_print.log")
    
    print()
    print("✅ Environment print module examples completed!")
    print("Check the 'logs/env_print.log' file for detailed logs.")

if __name__ == "__main__":
    main()

