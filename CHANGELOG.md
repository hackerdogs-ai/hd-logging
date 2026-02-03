# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-15

### Added
- Initial release of HD Logging library
- `setup_logger()` function for easy logger configuration
- OpenTelemetry JSON format support with `OpenTelemetryFormatter`
- Environment variable handling with sensitive data masking
- Advanced log rotation with `SizeAndTimeLoggingHandler`
- Colorized console output with `colorlog` integration
- Support for custom attributes and structured logging
- Automatic log directory creation
- UTC timestamp formatting with ISO 8601 format
- Environment variable loading from `.env` files
- Sensitive data detection and masking for environment variables
- Log rotation based on both size (20MB) and time (daily)
- Automatic compression of rotated log files
- Configurable log levels for console and file output
- Service identification for OpenTelemetry logs
- Rich metadata support for business events
- Exception logging with stack traces
- Performance monitoring capabilities

### Features
- **Logging Configuration**: Flexible setup with environment variables and programmatic configuration
- **OpenTelemetry Integration**: Full OTLP JSON format support with rich metadata
- **Security**: Automatic masking of sensitive environment variables
- **Log Rotation**: Size and time-based rotation with compression
- **Performance**: Optimized for high-volume logging scenarios
- **Integration**: Easy integration with web applications and services

### Dependencies
- Python 3.8+
- colorlog >= 6.9.0
- python-dotenv >= 1.0.0
- ulid-py >= 1.1.0

### Examples
- Basic usage
- OpenTelemetry format logging
- Environment variable handling
- Advanced logging scenarios
- Web application integration

### Documentation
- Comprehensive README with installation and usage instructions
- API reference with parameter descriptions
- Multiple usage examples
- Best practices guide
- Troubleshooting section

## [1.0.2] - 2025-01-13

### Fixed
- **Critical**: Fixed indentation bug where `shouldRollover`, `emit`, and `rotate` methods were incorrectly nested inside `__init__` method, preventing them from being accessible as instance methods
- Fixed missing `sys` import that could cause `NameError` in `emit()` method when writing to stderr
- Improved file handle management in `rotate()` method by using context managers (`with` statements) to prevent file handle leaks
- Fixed incorrect `except` clause indentation in `rotate()` method that caused syntax errors

### Technical Details
- All class methods are now properly defined at the class level with correct indentation
- File operations in `rotate()` now use proper context managers for automatic cleanup
- Error handling in logging methods is now fully functional

## [1.0.4] - 2026-01-13

### Fixed
- **Critical**: Fixed type safety bug in `_sanitize_extra` function that could raise `AttributeError` when `extra` parameter was not a dict (e.g., `None`, string, list)
- **Critical**: Fixed `KeyError` when reserved LogRecord keys (`message`, `asctime`, `filename`) were passed in `extra` dict parameter
- Fixed reserved LogRecord keys (`message`, `asctime`) not being excluded in `OpenTelemetryFormatter._extract_attributes` method
- Added automatic sanitization of reserved keys in `extra` dict across all logger methods (`warning`, `error`, `info`, `debug`, `critical`, `log`)
- Reserved keys are now automatically renamed: `message` → `log_message`, `asctime` → `log_asctime`, `filename` → `log_filename`

### Technical Details
- `_sanitize_extra` now properly handles `None`, empty dicts, and non-dict types
- All logger methods now sanitize `extra` dict before passing to Python's logging system
- `standard_attrs` set in `OpenTelemetryFormatter` now includes `'message'` and `'asctime'` to prevent extraction
- Sanitization is applied transparently - no API changes required
- Prevents duplicate wrapping with `_extra_sanitized` flag
- Comprehensive validation testing performed (63 tests, 100% pass rate)

### Backward Compatibility
- ✅ Fully backward compatible - no API changes
- ✅ Transparent fix - existing code works without modification
- ✅ Defensive handling of edge cases (None, non-dict types, etc.)

## [1.0.3] - 2026-01-13

### Fixed
- **Critical**: Fixed type safety bug in `_sanitize_extra` function that could raise `AttributeError` when `extra` parameter was not a dict (e.g., `None`, string, list)
- **Critical**: Fixed `KeyError` when reserved LogRecord keys (`message`, `asctime`) were passed in `extra` dict parameter
- Fixed reserved LogRecord keys (`message`, `asctime`) not being excluded in `OpenTelemetryFormatter._extract_attributes` method
- Added automatic sanitization of reserved keys in `extra` dict across all logger methods (`warning`, `error`, `info`, `debug`, `critical`, `log`)
- Reserved keys are now automatically renamed: `message` → `log_message`, `asctime` → `log_asctime`

### Technical Details
- `_sanitize_extra` now properly handles `None`, empty dicts, and non-dict types
- All logger methods now sanitize `extra` dict before passing to Python's logging system
- `standard_attrs` set in `OpenTelemetryFormatter` now includes `'message'` and `'asctime'` to prevent extraction
- Sanitization is applied transparently - no API changes required
- Prevents duplicate wrapping with `_extra_sanitized` flag

### Backward Compatibility
- ✅ Fully backward compatible - no API changes
- ✅ Transparent fix - existing code works without modification
- ✅ Defensive handling of edge cases (None, non-dict types, etc.)

## [1.0.6] - 2026-01-13

### Added
- **Resilient Error Handling**: Comprehensive exception handling throughout `setup_logger()`
  - Never crashes the program - always returns a usable logger
  - Graceful degradation: falls back to simpler configurations on failures
  - Handles all failure scenarios: permission errors, disk full, invalid paths, etc.
  - Multiple fallback levels ensure logging always works
- **Standard Output Separation**: Warnings and errors now follow Unix conventions
  - Warnings (non-critical issues) → stdout
  - Errors (critical issues) → stderr
  - Better integration with Docker/Kubernetes log collection
  - Easier filtering and monitoring of warnings vs errors

### Improved
- **Error Handling in setup_logger()**: 
  - Environment variable access wrapped with fallbacks
  - Formatter creation has multiple fallback levels
  - Handler creation failures handled gracefully
  - File handler creation failures use console handler only
  - Always ensures at least one basic handler exists
- **Exception Message Routing**:
  - Directory creation failures → Warning to stdout
  - File handler creation failures → Warning to stdout (non-critical)
  - Logging handler errors → Error to stderr
  - Log rotation failures → Error to stderr
  - All exceptions properly categorized and routed

### Technical Details
- `setup_logger()` now has try/except blocks around all critical operations
- Formatter failures fall back to simple formatters, then default formatters
- Handler failures fall back to basic StreamHandler
- File handler failures continue with console handler only
- All error messages properly prefixed with "Warning:" or "Error:"
- No exceptions are ever raised from `setup_logger()` - always returns a logger

### Backward Compatibility
- ✅ Fully backward compatible - no API changes
- ✅ All existing code works without modification
- ✅ Enhanced resilience without breaking changes

## [1.0.5] - 2026-01-13

### Added
- **Container/Docker Support**: Added `FORCE_LOGS_TO_STDOUT` environment variable support
  - When enabled, logs go to stdout (INFO/DEBUG) and stderr (WARNING/ERROR/CRITICAL)
  - No file handler is created, perfect for containerized environments
  - Logs are automatically captured by Docker/Kubernetes log collectors
- **Multiprocess-Safe Log Rotation**: Enhanced log rotation to handle concurrent access
  - Handles `FileNotFoundError` when multiple processes rotate the same log file
  - Automatically reopens file handles if rotated by another process
  - Prevents crashes from race conditions in Celery workers and multiprocess setups
- **Delete Log Files on Rotation**: Added `DELETE_LOG_FILE_ON_COMPRESSION` environment variable
  - When enabled, rotated log files are deleted instead of compressed
  - Useful when log files are managed by external tools (log shippers, etc.)
  - Supports values: `true`, `1`, `yes` (case-insensitive)

### Fixed
- **Log Rotation Race Conditions**: Fixed `FileNotFoundError` in multiprocess scenarios
  - `rotate()` now checks if source file exists before attempting rename
  - Catches and handles `FileNotFoundError` gracefully (file already rotated by another process)
  - Prevents rotation errors from breaking logging in concurrent environments
- **Stream Error Handling**: Improved error handling in `shouldRollover()` and `emit()`
  - `shouldRollover()` handles OSError/IOError/ValueError from stream operations
  - Automatically reopens stream if file was rotated/deleted by another process
  - `emit()` wraps parent emit() to prevent logging failures from crashing the application

### Technical Details
- `FORCE_LOGS_TO_STDOUT` can be set to `true`, `1`, or `yes` (case-insensitive)
- When enabled, `log_file_path` parameter is ignored (no file handler created)
- Multiprocess-safe rotation works automatically - no configuration needed
- All error handling is defensive and prevents crashes

### Use Cases
- **Docker/Kubernetes**: Set `FORCE_LOGS_TO_STDOUT=true` in container environment
- **Celery Workers**: Multiple workers can safely share the same log file
- **Multiprocess Applications**: No special handling needed for concurrent log rotation

## [Unreleased]

### Planned
- Async logging support
- Additional log formatters
- Enhanced error handling
- Performance optimizations
- Extended OpenTelemetry support
- Custom log rotation strategies

