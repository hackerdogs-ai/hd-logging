# HD Logging Examples

This directory contains comprehensive examples demonstrating how to use the HD Logging library in various scenarios.

## Examples Overview

### 1. Basic Usage (`basic_usage.py`)
Demonstrates the most common usage patterns for the `setup_logger` function:
- Basic logger setup with default settings
- Custom log file configuration
- Different log levels for console and file output
- Simple logging examples

**Run with:**
```bash
python examples/basic_usage.py
```

### 2. OpenTelemetry Usage (`opentelemetry_usage.py`)
Shows how to use the OpenTelemetry JSON format logging:
- OpenTelemetry format configuration
- Custom attributes and structured logging
- Exception logging with OTLP format
- Business event logging with rich metadata

**Run with:**
```bash
python examples/opentelemetry_usage.py
```

### 3. Environment Variable Usage (`environment_usage.py`)
Demonstrates environment variable handling features:
- Loading environment variables from .env files
- Sensitive data masking
- Environment-based logging configuration
- Security best practices

**Run with:**
```bash
python examples/environment_usage.py
```

### 4. Advanced Usage (`advanced_usage.py`)
Covers advanced logging features:
- Custom log rotation settings
- Multiple loggers for different components
- Error handling and exception logging
- Performance monitoring
- Business logic logging

**Run with:**
```bash
python examples/advanced_usage.py
```

### 5. Web Application Integration (`web_application_example.py`)
Shows how to integrate HD Logging into web applications:
- HTTP request/response logging
- Authentication event logging
- Business event tracking
- Database operation logging
- Error handling in web contexts

**Run with:**
```bash
python examples/web_application_example.py
```

### 6. Standard Logging Format (`standard_logging_example.py`)
Demonstrates traditional (non-OTLP) logging format:
- Standard text-based log format
- Traditional timestamp and level formatting
- Human-readable log entries
- Comparison with OTLP JSON format

**Run with:**
```bash
python examples/standard_logging_example.py
```

### 7. Environment Print Module (`env_print_example.py`)
Demonstrates direct usage of the `env_print.py` module functions:
- Environment variable logging with sensitive data masking
- Multiple logging approaches (get vs log functions)
- Sensitive data detection and protection
- .env file handling and processing
- Convenience alias usage

**Run with:**
```bash
python examples/env_print_example.py
```

## Running All Examples

To run all examples at once:

```bash
# Make sure you're in the project root directory
cd /path/to/hd-logging

# Run all examples
python examples/basic_usage.py
python examples/opentelemetry_usage.py
python examples/environment_usage.py
python examples/advanced_usage.py
python examples/web_application_example.py
python examples/standard_logging_example.py
python examples/env_print_example.py
```

## Generated Log Files

After running the examples, you'll find log files in the `examples/logs/` directory:

- `basic_example.log` - Basic logging output
- `custom_example.log` - Custom log file example
- `level_example.log` - Different log levels example
- `otlp_example.log` - OpenTelemetry JSON format
- `env_example.log` - Environment variable logging
- `rotation_example.log` - Log rotation example
- `api_service.log` - API service logging
- `database_service.log` - Database service logging
- `background_tasks.log` - Background task logging
- `error_handler.log` - Error handling example
- `performance.log` - Performance monitoring
- `business.log` - Business logic logging
- `demo_web_app.log` - Web application logging
- `standard_format.log` - Standard (non-OTLP) format logging
- `env_print.log` - Environment variable logging with masking

## Key Features Demonstrated

### Logging Configuration
- Console and file output with different log levels
- Colorized console output
- ISO 8601 timestamp formatting
- UTC timezone handling

### OpenTelemetry Integration
- JSON format logging
- Rich metadata and attributes
- Service identification
- Environment and version tracking

### Environment Variable Handling
- Automatic .env file loading
- Sensitive data masking
- Environment-based configuration
- Security best practices

### Log Rotation
- Size-based rotation (20MB default)
- Time-based rotation (daily)
- Automatic compression
- Configurable retention

### Error Handling
- Exception logging with stack traces
- Contextual error information
- Structured error reporting

### Performance Monitoring
- Timing information
- Resource usage tracking
- Business metrics logging

## Customization Examples

### Custom Log Levels
```python
import logging
from hd_logging import setup_logger

# Console shows only warnings and errors
# File captures all messages including debug
logger = setup_logger(
    "custom_levels",
    log_level_console=logging.WARNING,
    log_level_files=logging.DEBUG,
    log_file_path="custom.log"
)
```

### OpenTelemetry Configuration
```python
from hd_logging import setup_logger

logger = setup_logger(
    "otlp_service",
    use_otlp_format=True,
    service_name="my-service",
    environment="production",
    service_version="2.1.0",
    log_file_path="service.log"
)

# Log with custom attributes
logger.info("User action", extra={
    "user_id": "12345",
    "action": "login",
    "ip_address": "192.168.1.1"
})
```

### Environment Variable Integration
```python
import os
from hd_logging import setup_logger, load_env_file

# Load environment variables
load_env_file()

# Logger will use environment variables for configuration
logger = setup_logger("env_configured")
```

## Best Practices

1. **Use descriptive logger names** that identify the component or service
2. **Include contextual information** in log messages using the `extra` parameter
3. **Use appropriate log levels** (DEBUG, INFO, WARNING, ERROR, CRITICAL)
4. **Handle sensitive data** properly with masking
5. **Configure log rotation** based on your application's needs
6. **Use structured logging** for better analysis and monitoring
7. **Include performance metrics** for monitoring and optimization

## Troubleshooting

If you encounter issues running the examples:

1. **Import errors**: Make sure you're running from the project root directory
2. **Permission errors**: Ensure you have write permissions for the logs directory
3. **Missing dependencies**: Install required packages with `pip install -e .`
4. **Path issues**: Check that the `src` directory is in your Python path

For more information, see the main project README.md file.
