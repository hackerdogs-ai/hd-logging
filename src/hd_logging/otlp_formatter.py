"""
OpenTelemetry Log Formatter
Converts Python logging records to OpenTelemetry JSON format.
"""

import json
import os
import socket
import platform
from ulid import ULID
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional


class OpenTelemetryFormatter:
    """Formats log records to OpenTelemetry JSON format."""
    
    def __init__(self, service_name: str = "hd_logging", 
                 environment: str = "development", service_version: str = "1.0.0"):
        self.service_name = service_name
        self.environment = environment
        self.service_version = service_version
        self.resource_attributes = self._get_resource_attributes()
    
    def _get_resource_attributes(self) -> Dict[str, str]:
        """Get resource attributes for the service."""
        return {
            "host.name": self._get_hostname(),
            "os.type": self._get_os_type(),
            "service.name": self.service_name,
            "service.version": self.service_version,
            "service.instance.id": str(ULID()),
            "environment": self.environment
        }
    
    def _get_hostname(self) -> str:
        """Get the hostname of the system."""
        try:
            return socket.gethostname()
        except:
            return "unknown"
    
    def _get_os_type(self) -> str:
        """Get the operating system type."""
        return platform.system().lower()
    
    def _format_timestamp(self, timestamp: float) -> str:
        """Format timestamp to ISO 8601 format."""
        return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()
    
    def _extract_attributes(self, record) -> Dict[str, Any]:
        """Extract attributes from the log record."""
        # Standard logging attributes
        attributes = {
            "service.name": self.service_name,
            "environment": self.environment,
            "logger.name": record.name,
            "component": getattr(record, 'module', 'unknown'),
            "function": getattr(record, 'funcName', 'unknown'),
            "line": getattr(record, 'lineno', 0),
            "thread.name": getattr(record, 'threadName', 'unknown'),
            "process.name": getattr(record, 'processName', 'unknown'),
            "process.id": getattr(record, 'process', 0)
        }
        
        # Add any custom attributes from the record (otlp_attributes)
        if hasattr(record, 'otlp_attributes'):
            attributes.update(record.otlp_attributes)
        
        # Add ALL custom attributes from extra parameter
        # Get all attributes from the record and filter out standard logging ones
        # CRITICAL: 'message' and 'asctime' are reserved LogRecord properties that cannot
        # be overwritten. They must be excluded to prevent KeyError in makeRecord.
        standard_attrs = {
            'args', 'created', 'exc_info', 'exc_text', 'filename', 'funcName', 
            'levelname', 'levelno', 'lineno', 'module', 'msecs', 'msg', 'name', 
            'pathname', 'process', 'processName', 'relativeCreated', 'stack_info', 
            'taskName', 'thread', 'threadName', 'getMessage', 'otlp_attributes',
            'message',  # Reserved LogRecord property (computed from msg + args)
            'asctime'   # Reserved LogRecord property (formatted timestamp)
        }
        
        for attr_name in dir(record):
            if not attr_name.startswith('_') and attr_name not in standard_attrs:
                try:
                    attr_value = getattr(record, attr_name)
                    if not callable(attr_value) and attr_value is not None:
                        attributes[attr_name] = attr_value
                except (AttributeError, TypeError):
                    # Skip attributes that can't be accessed
                    pass
        
        # Add exception info if present
        if record.exc_info:
            attributes["exception.type"] = record.exc_info[0].__name__ if record.exc_info[0] else "Exception"
            attributes["exception.message"] = str(record.exc_info[1]) if record.exc_info[1] else ""
        
        return attributes
    
    def format(self, record) -> str:
        """Format the log record to OpenTelemetry JSON format."""
        try:
            otlp_record = {
                "timestamp": self._format_timestamp(record.created),
                "severityText": record.levelname,
                "body": record.getMessage(),
                "attributes": self._extract_attributes(record),
                "resource": self.resource_attributes
            }
            
            # Add tracing information if available
            if hasattr(record, 'traceId'):
                otlp_record["traceId"] = record.traceId
            if hasattr(record, 'spanId'):
                otlp_record["spanId"] = record.spanId
            
            return json.dumps(otlp_record, ensure_ascii=False)
            
        except Exception as e:
            # Fallback to simple JSON if formatting fails
            fallback_record = {
                "timestamp": self._format_timestamp(record.created),
                "severityText": record.levelname,
                "body": record.getMessage(),
                "error": f"Failed to format log record: {str(e)}"
            }
            return json.dumps(fallback_record, ensure_ascii=False)
    
    def formatTime(self, record, datefmt=None):
        """Format the timestamp (for compatibility with logging.Formatter)."""
        return self._format_timestamp(record.created)
