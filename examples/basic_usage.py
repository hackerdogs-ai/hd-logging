#!/usr/bin/env python3
"""
Basic Usage Example for HD Logging

This example demonstrates the most common usage patterns for the setup_logger function.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from hd_logging import setup_logger

def main():
    """Demonstrate basic logging setup and usage."""
    
    # Example 1: Basic logger setup with default settings
    print("=== Example 1: Basic Logger Setup ===")
    logger = setup_logger("basic_example")
    
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.debug("This is a debug message (may not show depending on log level)")
    
    # Example 2: Logger with custom log file
    print("\n=== Example 2: Custom Log File ===")
    logger2 = setup_logger(
        "custom_file_example",
        log_file_path="examples/logs/custom_example.log"
    )
    
    logger2.info("This message will be written to a custom log file")
    logger2.error("Error messages are also written to the file")
    
    # Example 3: Different log levels for console and file
    print("\n=== Example 3: Different Log Levels ===")
    import logging
    
    logger3 = setup_logger(
        "level_example",
        log_level_console=logging.WARNING,  # Only warnings and errors to console
        log_level_files=logging.DEBUG,       # All messages to file
        log_file_path="examples/logs/level_example.log"
    )
    
    logger3.debug("Debug message (file only)")
    logger3.info("Info message (file only)")
    logger3.warning("Warning message (both console and file)")
    logger3.error("Error message (both console and file)")
    
    print("\n✅ Basic usage examples completed!")
    print("Check the 'examples/logs/' directory for generated log files.")

if __name__ == "__main__":
    main()

