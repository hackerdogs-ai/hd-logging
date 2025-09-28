# HD Logging

A comprehensive Python logging library with OpenTelemetry support, environment variable handling, and advanced log rotation capabilities.

## Features

- 🎨 **Colorized Console Output** - Beautiful, color-coded log messages
- 📊 **OpenTelemetry Integration** - JSON format logging with rich metadata
- 🔒 **Environment Variable Security** - Automatic sensitive data masking
- 📁 **Advanced Log Rotation** - Size and time-based rotation with compression
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

### Log Rotation

The library includes advanced log rotation with both size and time-based rotation:

```python
# Automatic rotation when:
# - File size exceeds 20MB (configurable)
# - Daily rotation at midnight
# - Automatic compression of rotated files
# - Retention of 7 days (configurable)
```

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
