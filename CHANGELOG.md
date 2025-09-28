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

## [Unreleased]

### Planned
- Async logging support
- Additional log formatters
- Enhanced error handling
- Performance optimizations
- Extended OpenTelemetry support
- Custom log rotation strategies
