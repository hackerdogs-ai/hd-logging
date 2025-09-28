#!/usr/bin/env python3
"""
Environment Variable Usage Example for HD Logging

This example demonstrates how to use the environment variable handling features.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from hd_logging import setup_logger, load_env_file, log_env_vars_with_masking, log_dotenv_vars_with_masking

def main():
    """Demonstrate environment variable handling with logging."""
    
    print("=== Environment Variable Logging Example ===")
    
    # Example 1: Load environment variables from .env file
    print("\n1. Loading environment variables from .env file...")
    env_loaded = load_env_file()
    if env_loaded:
        print("✅ Environment variables loaded from .env file")
    else:
        print("⚠️  No .env file found, using system environment variables")
    
    # Example 2: Setup logger with environment-based configuration
    logger = setup_logger(
        "env_example",
        log_file_path="examples/logs/env_example.log"
    )
    
    # Example 3: Log environment variables with sensitive data masking
    print("\n2. Logging environment variables with masking...")
    log_env_vars_with_masking()
    
    # Example 4: Log .env file variables with masking
    print("\n3. Logging .env file variables with masking...")
    log_dotenv_vars_with_masking()
    
    # Example 4.5: Use our custom logger for some messages
    print("\n3.5. Using custom logger for environment example...")
    logger.info("Environment example started")
    logger.info("This message should appear in env_example.log")
    logger.warning("Environment configuration warning")
    logger.error("Environment configuration error")
    
    # Example 5: Demonstrate environment-based logging configuration
    print("\n4. Environment-based logging configuration...")
    
    # Set some environment variables for demonstration
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["SERVICE_NAME"] = "env-demo-service"
    os.environ["ENVIRONMENT"] = "demo"
    os.environ["SERVICE_VERSION"] = "2.0.0"
    
    # Create a new logger that will use these environment variables
    env_logger = setup_logger("env_demo")
    
    env_logger.debug("This debug message should now be visible")
    env_logger.info("Service information")
    env_logger.warning("Service warning")
    env_logger.error("Service error")
    
    # Example 6: Demonstrate sensitive data handling
    print("\n5. Demonstrating sensitive data handling...")
    
    # Set some sensitive environment variables
    os.environ["DATABASE_PASSWORD"] = "super_secret_password_123"
    os.environ["API_KEY"] = "sk-1234567890abcdef"
    os.environ["SECRET_TOKEN"] = "very_secret_token_xyz"
    
    # These will be masked when logged
    os.environ["REGULAR_VAR"] = "this_will_not_be_masked"
    os.environ["NORMAL_CONFIG"] = "normal_value"
    
    # Log all environment variables again to show masking
    print("\nLogging environment variables with sensitive data masking:")
    log_env_vars_with_masking()
    
    # Final logging with our custom logger
    logger.info("Environment variable demonstration completed")
    logger.info("Sensitive data masking working correctly")
    logger.info("Environment-based configuration successful")
    
    print("\n✅ Environment variable logging examples completed!")
    print("Check the 'examples/logs/env_example.log' file for detailed logs.")

if __name__ == "__main__":
    main()
