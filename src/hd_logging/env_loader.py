"""
Environment File Loader
Simple utility to find and load .env files from common locations.
"""

import os
import glob
from pathlib import Path
from typing import Optional


def find_env_file(start_path: Optional[str] = None) -> Optional[Path]:
    """
    Find .env file in common locations using glob patterns.
    
    Searches in:
    1. Current directory
    2. One level up
    3. Two levels up
    
    Args:
        start_path: Starting directory path (defaults to current working directory)
        
    Returns:
        Path to .env file if found, None otherwise
    """
    if start_path is None:
        start_path = os.getcwd()
    
    # Convert to Path object for easier manipulation
    start = Path(start_path).resolve()
    
    # Search patterns: current dir, 1 level up, 2 levels up
    search_paths = [
        start,                    # Current directory
        start.parent,            # One level up
        start.parent.parent,     # Two levels up
    ]
    
    # Use glob to search for .env files in each directory
    for search_path in search_paths:
        if search_path.exists():
            # Use glob to find .env files in this directory
            env_files = glob.glob(str(search_path / ".env"))
            if env_files:
                return Path(env_files[0])  # Return the first .env file found
    
    return None


def load_env_file(start_path: Optional[str] = None, override: bool = True) -> bool:
    """
    Find and load .env file from common locations.
    
    Args:
        start_path: Starting directory path (defaults to current working directory)
        override: Whether to override existing environment variables
        
    Returns:
        True if .env file was found and loaded, False otherwise
    """
    try:
        from dotenv import load_dotenv
        
        env_file = find_env_file(start_path)
        
        if env_file:
            load_dotenv(env_file, override=override)
            return True
        else:
            # Fallback to default behavior
            load_dotenv(override=override)
            return False
            
    except ImportError:
        print("Warning: python-dotenv not installed. Using system environment variables only.")
        print("Install with: pip install python-dotenv")
        return False


def get_env_file_path(start_path: Optional[str] = None) -> Optional[str]:
    """
    Get the path to the .env file that would be loaded.
    
    Args:
        start_path: Starting directory path (defaults to current working directory)
        
    Returns:
        String path to .env file if found, None otherwise
    """
    env_file = find_env_file(start_path)
    return str(env_file) if env_file else None
