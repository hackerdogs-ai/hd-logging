# HD Logging

A comprehensive Python logging library with OpenTelemetry support, environment variable handling, and advanced log rotation capabilities.

## Features

- 🎨 **Colorized Console Output** - Beautiful, color-coded log messages
- 📊 **OpenTelemetry Integration** - JSON format logging with rich metadata
- 🔒 **Environment Variable Security** - Automatic sensitive data masking
- 📁 **Advanced Log Rotation** - Size and time-based rotation with compression
- 🐳 **Container-Ready** - Docker/Kubernetes support with stdout/stderr logging
- 🔄 **Multiprocess-Safe** - Handles concurrent log rotation in Celery workers and multiprocess environments
- 🛡️ **Crash-Proof** - Resilient error handling - never crashes your program, always returns a usable logger
- ⚙️ **Flexible Configuration** - Environment variables and programmatic setup
- 🚀 **High Performance** - Optimized for production workloads
- 🔧 **Easy Integration** - Simple setup with powerful features

## Installation

### Using pip
```bash
pip install hd-logging
```

### Using uv (recommended)
```bash
uv add hd-logging
```

### Development Installation
```bash
git clone https://github.com/tejaswiredkar/hd-logging.git
cd hd-logging
uv sync
uv pip install -e .
```

## Quick Start

### Basic Usage

```python
from hd_logging import setup_logger

# Create a logger with default settings
logger = setup_logger("my_app")

# Log messages
logger.info("Application started")
logger.warning("This is a warning")
logger.error("An error occurred")
```

### OpenTelemetry Format

```python
from hd_logging import setup_logger

# Create a logger with OpenTelemetry JSON format
logger = setup_logger(
    "my_service",
    use_otlp_format=True,
    service_name="my-service",
    environment="production",
    service_version="1.0.0",
    log_file_path="logs/service.log"
)

# Log with custom attributes
logger.info("User action performed", extra={
    "user_id": "12345",
    "action": "login",
    "ip_address": "192.168.1.1"
})
```

### Environment Variable Integration

```python
from hd_logging import setup_logger, load_env_file

# Load environment variables from .env file
load_env_file()

# Logger will automatically use environment variables
logger = setup_logger("env_configured")
```

## Configuration

### Environment Variables

The library supports configuration through environment variables:

```bash
# Log levels
LOG_LEVEL=INFO                    # Console and file log level
LOG_FILE_OTLP_FORMAT=true         # Enable OpenTelemetry format

# Service information
SERVICE_NAME=my-service           # Service name for OTLP logs
ENVIRONMENT=production            # Environment name
SERVICE_VERSION=1.0.0            # Service version

# Log file settings
LOG_FILE=logs/app.log             # Log file path

# Container/Docker settings
FORCE_LOGS_TO_STDOUT=true         # Force logs to stdout/stderr (no file handler)
                                  # INFO/DEBUG → stdout, WARNING/ERROR/CRITICAL → stderr

# Log rotation settings
DELETE_LOG_FILE_ON_COMPRESSION=true  # Delete rotated log files instead of compressing
                                     # Useful when log files are managed externally
```

### Programmatic Configuration

```python
from hd_logging import setup_logger
import logging

logger = setup_logger(
    logger_name="my_app",
    log_file_path="logs/app.log",
    log_level_console=logging.INFO,
    log_level_files=logging.DEBUG,
    use_otlp_format=True,
    service_name="my-service",
    environment="production",
    service_version="1.0.0"
)
```

## Advanced Features

### Docker and Container Logging

HD Logging is optimized for containerized environments (Docker, Kubernetes, etc.) where logs are typically collected from stdout/stderr:

```python
# In your Dockerfile or Kubernetes deployment, set:
# ENV FORCE_LOGS_TO_STDOUT=true

# Or in Python:
import os
os.environ["FORCE_LOGS_TO_STDOUT"] = "true"

from hd_logging import setup_logger

# When FORCE_LOGS_TO_STDOUT=true:
# - INFO and DEBUG logs go to stdout
# - WARNING, ERROR, and CRITICAL logs go to stderr
# - No file handler is created (log_file_path is ignored)
# - Perfect for container log aggregation (docker logs, kubectl logs, etc.)

logger = setup_logger("my_service")
logger.info("This goes to stdout")      # → stdout
logger.error("This goes to stderr")     # → stderr
```

**Benefits:**
- ✅ Logs automatically captured by Docker/Kubernetes
- ✅ Errors properly separated to stderr (standard practice)
- ✅ No log files to manage inside containers
- ✅ Works seamlessly with log aggregators (ELK, Splunk, etc.)

### Resilient Error Handling

HD Logging is designed to never crash your program. Even if file operations fail, the logger will always work:

```python
# Even with permission errors, invalid paths, or disk full:
# - Always returns a usable logger
# - Falls back to console handler if file handler fails
# - Warnings go to stdout, errors go to stderr
# - Never raises exceptions

logger = setup_logger("my_app", log_file_path="/root/cannot_write.log")
# Will work with console handler only, prints warning to stdout
logger.info("This will work!")  # ✅ Always works
```

**Features:**
- ✅ Never crashes - always returns a usable logger
- ✅ Graceful degradation - falls back to simpler configurations
- ✅ Warnings to stdout, errors to stderr (Unix conventions)
- ✅ Handles all failure scenarios: permissions, disk full, invalid paths
- ✅ Multiple fallback levels ensure logging always works

### Multiprocess-Safe Log Rotation

The library handles concurrent log rotation in multiprocess environments (e.g., Celery workers):

```python
# Safe for multiple processes sharing the same log file
# - Handles FileNotFoundError when another process rotates the file
# - Automatically reopens file handles if rotated by another process
# - Prevents crashes from race conditions during rotation

logger = setup_logger("celery_worker", log_file_path="logs/worker.log")
# Multiple Celery workers can safely use the same log file
```

**Features:**
- ✅ Race condition handling in `rotate()` method
- ✅ Automatic file handle recovery in `shouldRollover()`
- ✅ Error handling in `emit()` prevents logging failures from crashing the app
- ✅ No special configuration needed - works automatically

### Log Rotation

The library includes advanced log rotation with both size and time-based rotation:

```python
# Automatic rotation when:
# - File size exceeds 20MB (configurable)
# - Daily rotation at midnight
# - Automatic compression of rotated files (default)
# - Or deletion of rotated files (if DELETE_LOG_FILE_ON_COMPRESSION=true)
# - Retention of 7 days (configurable)
# - Multiprocess-safe (handles concurrent rotation)

# Delete instead of compress:
import os
os.environ["DELETE_LOG_FILE_ON_COMPRESSION"] = "true"
logger = setup_logger("my_app", log_file_path="logs/app.log")
# Rotated files will be deleted instead of compressed
```

**Configuration:**
- **Default**: Rotated files are compressed (`.gz` format)
- **DELETE_LOG_FILE_ON_COMPRESSION=true**: Rotated files are deleted instead
- Useful when log files are managed by external tools (log shippers, etc.)

### Sensitive Data Masking

Automatic masking of sensitive environment variables:

```python
from hd_logging import log_env_vars_with_masking

# Logs environment variables with sensitive data masked
log_env_vars_with_masking()
```

### Custom Attributes

Add rich metadata to your logs:

```python
logger.info("Order processed", extra={
    "order_id": "ORD-12345",
    "customer_id": "CUST-67890",
    "amount": 99.99,
    "currency": "USD",
    "payment_method": "credit_card"
})
```

## Examples

See the `examples/` directory for comprehensive usage examples:

- [Basic Usage](examples/basic_usage.py) - Simple logging setup
- [OpenTelemetry Usage](examples/opentelemetry_usage.py) - JSON format logging
- [Environment Variables](examples/environment_usage.py) - Environment handling
- [Advanced Features](examples/advanced_usage.py) - Advanced logging scenarios
- [Web Application](examples/web_application_example.py) - Web app integration

### Docker Example

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Enable stdout/stderr logging for container
ENV FORCE_LOGS_TO_STDOUT=true
ENV LOG_LEVEL=INFO

COPY . .
CMD ["python", "app.py"]
```

```python
# app.py
from hd_logging import setup_logger

# Automatically uses stdout/stderr when FORCE_LOGS_TO_STDOUT=true
logger = setup_logger("my_app")

logger.info("Application started")      # → stdout
logger.error("Something went wrong")    # → stderr
```

### Celery Worker Example

```python
# celery_config.py
from hd_logging import setup_logger

# Multiple workers can safely share the same log file
logger = setup_logger(
    "celery_worker",
    log_file_path="logs/celery.log",
    log_level_console=logging.INFO
)

@celery_app.task
def my_task():
    logger.info("Task started")  # Safe for concurrent access
```

Run examples:
```bash
python examples/basic_usage.py
python examples/opentelemetry_usage.py
# ... and more
```

## API Reference

### setup_logger()

```python
def setup_logger(
    logger_name: str,
    log_file_path: Optional[str] = None,
    log_level_console: Optional[int] = None,
    log_level_files: Optional[int] = None,
    use_otlp_format: bool = None,
    service_name: Optional[str] = None,
    environment: Optional[str] = None,
    service_version: Optional[str] = None
) -> logging.Logger
```

**Parameters:**
- `logger_name`: Name of the logger
- `log_file_path`: Path to log file (default: from LOG_FILE env var)
- `log_level_console`: Console log level (default: from LOG_LEVEL env var)
- `log_level_files`: File log level (default: from LOG_LEVEL env var)
- `use_otlp_format`: Enable OpenTelemetry format (default: from LOG_FILE_OTLP_FORMAT env var)
- `service_name`: Service name for OTLP logs (default: from SERVICE_NAME env var)
- `environment`: Environment name (default: from ENVIRONMENT env var)
- `service_version`: Service version (default: from SERVICE_VERSION env var)

### Environment Variable Functions

```python
from hd_logging import (
    load_env_file,           # Load .env file
    find_env_file,           # Find .env file path
    get_env_file_path,       # Get .env file path
    log_env_vars_with_masking,  # Log env vars with masking
    log_dotenv_vars_with_masking,  # Log .env vars with masking
    get_env_vars_with_masking,    # Get env vars with masking
    get_dotenv_vars_with_masking  # Get .env vars with masking
)
```

## Log Formats

### Standard Format
```
2024-01-15T10:30:45Z - my_app - INFO - Application started - [Component: main, Function: main, Line: 15]
```

### OpenTelemetry JSON Format
```json
{
  "timestamp": "2024-01-15T10:30:45.123456Z",
  "severityText": "INFO",
  "body": "Application started",
  "attributes": {
    "service.name": "my-service",
    "environment": "production",
    "logger.name": "my_app",
    "component": "main",
    "function": "main",
    "line": 15
  },
  "resource": {
    "host.name": "server-01",
    "os.type": "linux",
    "service.name": "my-service",
    "service.version": "1.0.0",
    "service.instance.id": "01HZ1234567890ABCDEF",
    "environment": "production"
  }
}
```

## Requirements

- Python 3.8+
- colorlog >= 6.9.0
- python-dotenv >= 1.0.0
- ulid-py >= 1.1.0

## Development

### Setup Development Environment

```bash
git clone https://github.com/tejaswiredkar/hd-logging.git
cd hd-logging
uv sync
```

### Run Tests

```bash
uv run pytest
```

### Code Formatting

```bash
uv run black src/
uv run flake8 src/
uv run mypy src/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.

## Support

- 📧 Email: support@hackerdogs.ai
- 🐛 Issues: [GitHub Issues](https://github.com/tejaswiredkar/hd-logging/issues)
- 📖 Documentation: [GitHub Wiki](https://github.com/tejaswiredkar/hd-logging/wiki)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a history of changes.

---

Made with ❤️ by [Hackerdogs.ai](https://hackerdogs.ai)
