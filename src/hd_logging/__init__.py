"""
HD Logging - A comprehensive logging library with OpenTelemetry support.

This package provides advanced logging capabilities including:
- Colorized console output
- OpenTelemetry JSON format support
- Environment variable handling with sensitive data masking
- Advanced log rotation with compression
- Size and time-based log rotation
"""

from .logger import setup_logger
from .env_loader import load_env_file, find_env_file, get_env_file_path
from .env_print import (
    get_env_vars_with_masking,
    log_env_vars_with_masking,
    log_dotenv_vars_with_masking,
    get_dotenv_vars_with_masking,
    env_print
)
from .otlp_formatter import OpenTelemetryFormatter
from .SizeAndTimeLoggingHandler import SizeAndTimeLoggingHandler

__version__ = "1.0.4"
__author__ = "Hackerdogs.ai"
__email__ = "support@hackerdogs.ai"

__all__ = [
    "setup_logger",
    "load_env_file",
    "find_env_file", 
    "get_env_file_path",
    "get_env_vars_with_masking",
    "log_env_vars_with_masking",
    "log_dotenv_vars_with_masking",
    "get_dotenv_vars_with_masking",
    "env_print",
    "OpenTelemetryFormatter",
    "SizeAndTimeLoggingHandler",
]
