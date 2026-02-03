import logging
import os
import sys
from typing import Optional
import colorlog
from hd_logging.SizeAndTimeLoggingHandler import SizeAndTimeLoggingHandler as STLH
import time

def setup_logger(
    logger_name: str,
    log_file_path: Optional[str] = None,
    log_level_console: Optional[int] = None,
    log_level_files: Optional[int] = None,
    use_otlp_format: bool = None,
    service_name: Optional[str] = None,
    environment: Optional[str] = None,
    service_version: Optional[str] = None
) -> logging.Logger:
    """
    Set up a standardized logger with colorized console output and size+time rotating file handler.
    - Prevents duplicate handlers.
    - Uses ISO 8601 timestamps.
    - Log levels and file path can be set via environment variables or function arguments.
    - Supports container environments with FORCE_LOGS_TO_STDOUT environment variable.
    - Resilient error handling - never crashes the program, always returns a usable logger.

    Args:
        logger_name (str): Name of the logger (use 'api_service' for main app).
        log_file_path (str, optional): Path to the log file. Defaults to 'hd_shared.log' if not specified.
            Ignored when FORCE_LOGS_TO_STDOUT=true (logs go to stdout/stderr instead).
        log_level_console (int, optional): Console log level. Defaults to LOG_LEVEL env or logging.INFO.
        log_level_files (int, optional): File log level. Defaults to LOG_LEVEL env or logging.INFO.

    Returns:
        logging.Logger: Configured logger instance. Always returns a logger, even if setup partially fails.
    """
    # Get logger first - this is always safe
    logger = logging.getLogger(logger_name)
    
    # Try to get basic configuration with safe defaults
    try:
        # Check if we should force logs to stdout/stderr (for container environments)
        force_stdout = os.environ.get("FORCE_LOGS_TO_STDOUT", "").strip().lower() in ("true", "1", "yes")
    except Exception:
        # If env var access fails, default to False
        force_stdout = False
    
    # Environment/config defaults with error handling
    try:
        log_file_path = log_file_path or os.getenv("LOG_FILE", "logs/hd_logging.log")
    except Exception:
        log_file_path = "logs/hd_logging.log"
    
    try:
        env_log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        log_level_console = log_level_console or getattr(logging, env_log_level, logging.INFO)
        log_level_files = log_level_files or getattr(logging, env_log_level, logging.INFO)
    except Exception:
        # Fallback to INFO if anything fails
        log_level_console = log_level_console or logging.INFO
        log_level_files = log_level_files or logging.INFO
    
    # OpenTelemetry format configuration
    try:
        if use_otlp_format is None:
            use_otlp_format = os.getenv("LOG_FILE_OTLP_FORMAT", "true").lower() == "true"
    except Exception:
        use_otlp_format = True  # Default to True
    
    try:
        service_name = service_name or os.getenv("SERVICE_NAME", "hd_logging")
        environment = environment or os.getenv("ENVIRONMENT", "development")
        service_version = service_version or os.getenv("SERVICE_VERSION", "1.0.0")
    except Exception:
        # Fallback values
        service_name = service_name or "hd_logging"
        environment = environment or "development"
        service_version = service_version or "1.0.0"

    # Set logger level with error handling
    try:
        logger.setLevel(min(log_level_console, log_level_files))  # Set to lowest for capturing all
    except Exception:
        # If level setting fails, use INFO as fallback
        try:
            logger.setLevel(logging.INFO)
        except Exception:
            pass  # If even this fails, continue with default level

    # CRITICAL FIX: Sanitize extra dict to prevent "Attempt to overwrite 'message' in LogRecord" errors
    # This must be applied even if handlers are already set, to ensure all loggers are protected
    def _sanitize_extra(extra):
        """Sanitize extra dict to remove reserved LogRecord keys.
        
        Args:
            extra: The extra dict passed to logging methods, or None
            
        Returns:
            The sanitized extra dict with reserved keys renamed, or None/unchanged if no sanitization needed
        """
        # Handle None and non-dict types
        if extra is None:
            return None
        if not isinstance(extra, dict):
            # If extra is not a dict, return as-is (logging will handle the error)
            return extra
        if not extra:  # Empty dict
            return extra
        
        # Check if any reserved keys are present
        # These are LogRecord attributes that cannot be overwritten
        reserved_keys = {'message', 'asctime', 'filename'}
        if any(key in extra for key in reserved_keys):
            # Create a copy to avoid modifying the original
            sanitized = extra.copy()
            if 'message' in sanitized:
                sanitized['log_message'] = sanitized.pop('message')
            if 'asctime' in sanitized:
                sanitized['log_asctime'] = sanitized.pop('asctime')
            if 'filename' in sanitized:
                sanitized['log_filename'] = sanitized.pop('filename')
            return sanitized
        return extra

    # Only wrap logger methods if not already wrapped (prevent duplicate wrapping)
    # Wrap in try/except to ensure we always have a usable logger
    try:
        if not getattr(logger, "_extra_sanitized", False):
            # Wrap logger methods to sanitize extra dict
            try:
                original_warning = logger.warning
                original_error = logger.error
                original_info = logger.info
                original_debug = logger.debug
                original_critical = logger.critical
                original_log = logger.log
            except Exception:
                # If we can't get original methods, skip patching
                pass
            else:
                # Use **kwargs for maximum compatibility across Python versions
                # Python's logging methods accept and ignore unknown kwargs in modern versions
                def patched_warning(msg, *args, extra=None, **kwargs):
                    try:
                        return original_warning(msg, *args, extra=_sanitize_extra(extra), **kwargs)
                    except Exception:
                        # Fallback to original if sanitization fails
                        return original_warning(msg, *args, extra=extra, **kwargs)
                
                def patched_error(msg, *args, extra=None, **kwargs):
                    try:
                        return original_error(msg, *args, extra=_sanitize_extra(extra), **kwargs)
                    except Exception:
                        return original_error(msg, *args, extra=extra, **kwargs)
                
                def patched_info(msg, *args, extra=None, **kwargs):
                    try:
                        return original_info(msg, *args, extra=_sanitize_extra(extra), **kwargs)
                    except Exception:
                        return original_info(msg, *args, extra=extra, **kwargs)
                
                def patched_debug(msg, *args, extra=None, **kwargs):
                    try:
                        return original_debug(msg, *args, extra=_sanitize_extra(extra), **kwargs)
                    except Exception:
                        return original_debug(msg, *args, extra=extra, **kwargs)
                
                def patched_critical(msg, *args, extra=None, **kwargs):
                    try:
                        return original_critical(msg, *args, extra=_sanitize_extra(extra), **kwargs)
                    except Exception:
                        return original_critical(msg, *args, extra=extra, **kwargs)
                
                def patched_log(level, msg, *args, extra=None, **kwargs):
                    try:
                        return original_log(level, msg, *args, extra=_sanitize_extra(extra), **kwargs)
                    except Exception:
                        return original_log(level, msg, *args, extra=extra, **kwargs)

                # Apply patches with error handling
                try:
                    logger.warning = patched_warning
                    logger.error = patched_error
                    logger.info = patched_info
                    logger.debug = patched_debug
                    logger.critical = patched_critical
                    logger.log = patched_log
                    logger._extra_sanitized = True  # Mark as sanitized
                except Exception:
                    # If patching fails, continue without patches
                    pass
    except Exception:
        # If entire wrapping process fails, continue with default logger
        pass

    # Prevent duplicate handlers
    try:
        if getattr(logger, "_custom_handlers_set", False):
            return logger
    except Exception:
        # If check fails, continue with setup
        pass

    # Create formatters with error handling
    iso_time_format = "%Y-%m-%dT%H:%M:%S%z"
    file_formatter = None
    console_formatter = None
    
    try:
        # Set the converter for all Formatters to use UTC
        logging.Formatter.converter = time.gmtime
    except Exception:
        # If time conversion fails, continue with default
        pass
    
    try:
        # File formatter
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s - [Component: %(module)s, Function: %(funcName)s, Line: %(lineno)d]',
            datefmt=iso_time_format
        )
    except Exception:
        # Fallback to simple formatter if custom formatter fails
        try:
            file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        except Exception:
            file_formatter = None  # Will use default formatter if this also fails

    try:
        # Colorized console formatter
        console_formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s - [Component: %(module)s, Function: %(funcName)s, Line: %(lineno)d]",
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            },
            datefmt=iso_time_format
        )
    except Exception:
        # Fallback to simple formatter if colorlog fails
        try:
            console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        except Exception:
            console_formatter = None  # Will use default formatter if this also fails

    # If FORCE_LOGS_TO_STDOUT is enabled, use only stream handlers (no file handler)
    # This is useful for container environments where logs are collected from stdout/stderr
    # NOTE: When force_stdout is True, log_file_path is completely ignored - no file handler is created
    try:
        if force_stdout:
            # stdout handler for INFO and DEBUG
            try:
                stdout_handler = logging.StreamHandler(sys.stdout)
                stdout_handler.setLevel(logging.DEBUG)  # Capture DEBUG and INFO
                stdout_handler.addFilter(lambda record: record.levelno <= logging.INFO)
                if console_formatter:
                    stdout_handler.setFormatter(console_formatter)
                logger.addHandler(stdout_handler)
            except Exception as e:
                # If stdout handler fails, try basic handler
                try:
                    stdout_handler = logging.StreamHandler()
                    stdout_handler.setLevel(logging.DEBUG)
                    logger.addHandler(stdout_handler)
                except Exception:
                    # If even basic handler fails, continue without it
                    pass
            
            # stderr handler for WARNING, ERROR, and CRITICAL
            try:
                stderr_handler = logging.StreamHandler(sys.stderr)
                stderr_handler.setLevel(logging.WARNING)  # Capture WARNING, ERROR, CRITICAL
                if console_formatter:
                    stderr_handler.setFormatter(console_formatter)
                logger.addHandler(stderr_handler)
            except Exception as e:
                # If stderr handler fails, try basic handler
                try:
                    stderr_handler = logging.StreamHandler()
                    stderr_handler.setLevel(logging.WARNING)
                    logger.addHandler(stderr_handler)
                except Exception:
                    # If even basic handler fails, continue without it
                    pass
        else:
            # Normal behavior: console handler + file handler
            # Console handler
            try:
                console_handler = logging.StreamHandler()
                console_handler.setLevel(log_level_console)
                if console_formatter:
                    console_handler.setFormatter(console_formatter)
                logger.addHandler(console_handler)
            except Exception:
                # If console handler fails, try basic handler
                try:
                    console_handler = logging.StreamHandler()
                    console_handler.setLevel(log_level_console)
                    logger.addHandler(console_handler)
                except Exception:
                    # If even basic handler fails, continue without it
                    pass

            # File handler setup with comprehensive error handling
            try:
                # Ensure log directory exists if log_file_path is set
                if log_file_path:
                    try:
                        log_dir = os.path.dirname(log_file_path)
                        if log_dir and not os.path.exists(log_dir):
                            os.makedirs(log_dir, exist_ok=True)
                    except (OSError, PermissionError, IOError) as e:
                        # If directory creation fails, log warning to stdout and continue
                        # We'll try to create the file anyway (parent dir might exist)
                        try:
                            print(f"Warning: Could not create log directory {log_dir}: {e}", file=sys.stdout)
                        except Exception:
                            pass
                
                # Check if we should delete log files instead of compressing
                try:
                    delete_on_compression = os.environ.get("DELETE_LOG_FILE_ON_COMPRESSION", "").strip().lower() in ("true", "1", "yes")
                except Exception:
                    delete_on_compression = False
                
                # Size and time rotating file handler
                # On file open failure (PermissionError/OSError/IOError), use only stream handlers
                stime_handler = None
                try:
                    stime_handler = STLH(
                        filename=log_file_path,
                        when="midnight",
                        interval=1,
                        backupCount=7,
                        maxBytes=20_000_000,
                        use_otlp_format=use_otlp_format,
                        service_name=service_name,
                        environment=environment,
                        service_version=service_version,
                        delete_on_compression=delete_on_compression
                    )
                    stime_handler.setLevel(log_level_files)
                    
                    # Set formatter based on OTLP format preference
                    if not use_otlp_format and file_formatter:
                        try:
                            stime_handler.setFormatter(file_formatter)
                        except Exception:
                            # If formatter setting fails, continue without it
                            pass
                    
                    # Only add handler if creation and setup succeeded
                    logger.addHandler(stime_handler)
                    stime_handler = None  # Mark as successfully added
                except (OSError, PermissionError, IOError) as e:
                    # If file handler creation fails (permissions, disk full, etc.),
                    # log warning to stdout and continue with console handler only
                    # Never raise - always return logger with stream handlers only
                    try:
                        print(f"Warning: Could not create file handler for {log_file_path}: {e}", file=sys.stdout)
                        print("Continuing with console handler only.", file=sys.stdout)
                    except Exception:
                        pass
                    # Ensure handler is not added if it was partially created
                    if stime_handler is not None:
                        try:
                            stime_handler.close()
                        except Exception:
                            pass
                except Exception as e:
                    # Catch any other unexpected errors
                    # Never raise - always return logger with stream handlers only
                    try:
                        print(f"Error: Unexpected error creating file handler: {type(e).__name__}: {e}", file=sys.stderr)
                    except Exception:
                        pass
                    # Ensure handler is not added if it was partially created
                    if stime_handler is not None:
                        try:
                            stime_handler.close()
                        except Exception:
                            pass
            except Exception as e:
                # If entire file handler setup fails, continue without it
                try:
                    print(f"Error: File handler setup failed: {type(e).__name__}: {e}", file=sys.stderr)
                except Exception:
                    pass
    except Exception as e:
        # If handler setup completely fails, ensure we at least have a basic handler
        try:
            if not logger.handlers:
                basic_handler = logging.StreamHandler()
                basic_handler.setLevel(logging.INFO)
                logger.addHandler(basic_handler)
        except Exception:
            # If even basic handler fails, return logger as-is (Python's default handler will be used)
            pass

    # Mark as configured to prevent duplicate handlers
    try:
        logger._custom_handlers_set = True
    except Exception:
        # If setting flag fails, continue anyway
        pass

    # Always return the logger, even if setup partially failed
    return logger 
