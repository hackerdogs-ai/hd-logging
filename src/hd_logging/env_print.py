#!/usr/bin/env python3
"""
Environment Variable Logger Module
Simple functions to return and log environment variables with sensitive data masking.
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, Any
from dotenv import dotenv_values, find_dotenv

# Add the project root to the Python path
try:
    project_root = Path(__file__).parent.parent
    sys.path.append(str(project_root))
except Exception as e:
    print(f"❌ Error setting up project path: {e}")

# Logger setup with fallback
try:
    from hd_logging.logger import setup_logger
    logger = setup_logger(__name__, log_file_path="logs/env_print.log")
except Exception as e:
    print(f"❌ Error setting up logger: {e}")
    # Fallback to basic logging
    import logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

def mask_sensitive_value(value: str, show_chars: int = 2) -> str:
    """Mask sensitive values by showing only the first few characters."""
    try:
        if not value or len(value) <= show_chars:
            return "*" * len(value) if value else ""
        return value[:show_chars] + "*" * (len(value) - show_chars)
    except Exception as e:
        logger.error(f"❌ Error masking value: {e}")
        return "***ERROR***"

def is_sensitive_variable(var_name: str) -> bool:
    """Check if an environment variable name contains sensitive keywords."""
    try:
        if not var_name:
            return True
        sensitive_patterns = ['_KEY', 'DATABASE_URL', 'PASSWORD', 'SECRET']
        var_name_upper = var_name.upper()
        return any(pattern in var_name_upper for pattern in sensitive_patterns)
    except Exception as e:
        logger.error(f"❌ Error checking variable sensitivity: {e}")
        return True

def get_env_vars_with_masking() -> Dict[str, Any]:
    """
    Function 1: Return all environment variables with sensitive values masked.
    
    Returns:
        Dictionary with all environment variables, sensitive ones masked
    """
    try:
        env_vars = {}
        all_env_vars = dict(os.environ)
        
        for var_name, var_value in all_env_vars.items():
            if is_sensitive_variable(var_name):
                env_vars[var_name] = mask_sensitive_value(var_value)
            else:
                env_vars[var_name] = var_value
        
        return env_vars
    except Exception as e:
        logger.error(f"❌ Error getting environment variables: {e}")
        return {}

def log_env_vars_with_masking():
    """
    Function 2: Log all environment variables with sensitive data masked.
    """
    try:
        logger.info("🔍 Logging all environment variables with sensitive data masked...")
        
        env_vars = get_env_vars_with_masking()
        sensitive_count = 0
        regular_count = 0
        
        for var_name, var_value in env_vars.items():
            if is_sensitive_variable(var_name):
                sensitive_count += 1
                logger.info(f"🔐 {var_name} = {var_value}")
            else:
                regular_count += 1
                logger.info(f"📋 {var_name} = {var_value}")
        
        logger.info(f"📊 Summary: {sensitive_count} sensitive, {regular_count} regular, {len(env_vars)} total")
        logger.info("✅ Environment variable logging completed")
        
    except Exception as e:
        logger.error(f"❌ Error logging environment variables: {e}")

def log_dotenv_vars_with_masking():
    """
    Function 3: Load, log, and mask variables from a .env file.
    """
    try:
        dotenv_path = find_dotenv()
        logger.info(f"🔍 Searching for .env file...")

        if not dotenv_path:
            logger.warning("⚠️  .env file not found in current directory or parent directories.")
            return

        logger.info(f"📄 Found and reading variables from: {dotenv_path}")
        dotenv_vars = dotenv_values(dotenv_path)
        
        if not dotenv_vars:
            logger.info("✅ .env file is empty or could not be parsed.")
            return

        logger.info(f"📄 Logging {len(dotenv_vars)} variables from .env file...")
        sensitive_count = 0
        regular_count = 0

        for var_name, var_value in dotenv_vars.items():
            if is_sensitive_variable(var_name):
                sensitive_count += 1
                logger.info(f"🔐 {var_name} = {mask_sensitive_value(var_value)}")
            else:
                regular_count += 1
                logger.info(f"📋 {var_name} = {var_value}")
        
        logger.info(f"📊 Summary: {sensitive_count} sensitive, {regular_count} regular, {len(dotenv_vars)} total from .env")
        logger.info("✅ .env file logging completed")

    except Exception as e:
        logger.error(f"❌ Error logging variables from .env file: {e}")

def get_dotenv_vars_with_masking() -> Dict[str, Any]:
    """
    Function 4: Return all variables from a .env file with sensitive values masked.

    Returns:
        Dictionary with all .env variables, sensitive ones masked
    """
    try:
        dotenv_path = find_dotenv()
        if not dotenv_path:
            logger.warning("⚠️  .env file not found by find_dotenv() for get_dotenv_vars_with_masking.")
            return {}

        dotenv_vars = dotenv_values(dotenv_path)
        if not dotenv_vars:
            return {}

        masked_vars = {}
        for var_name, var_value in dotenv_vars.items():
            if is_sensitive_variable(var_name):
                masked_vars[var_name] = mask_sensitive_value(var_value)
            else:
                masked_vars[var_name] = var_value
        
        return masked_vars

    except Exception as e:
        logger.error(f"❌ Error getting variables from .env file: {e}")
        return {}

# Convenience aliases
env_print = log_env_vars_with_masking

if __name__ == "__main__":
    # Example usage
    print("🔍 Environment Variable Logger - Simple Usage")
    print("=" * 50)
    
    # Function 1: Get all env vars with masking
    print("\n1. Getting all environment variables with masking:")
    env_vars = get_env_vars_with_masking()
    print(f"   Found {len(env_vars)} environment variables")
    
    # Function 2: Log all env vars with masking
    print("\n2. Logging all environment variables with masking:")
    log_env_vars_with_masking()
    
    # Function 3: Log all .env vars with masking
    print("\n3. Logging all variables from .env file with masking:")
    log_dotenv_vars_with_masking()

    # Function 4: Get all .env vars with masking
    print("\n4. Getting all variables from .env file with masking:")
    dotenv_vars_masked = get_dotenv_vars_with_masking()
    print(f"   Found {len(dotenv_vars_masked)} variables in .env file")

    print("\n✅ Example completed")