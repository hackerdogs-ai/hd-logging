"""
Size and Time Rotating Logging Handler with Compression
Custom logging handler that rotates logs based on both size and time, with automatic compression.
Supports both plain text and OpenTelemetry JSON formats.
"""

from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import colorlog
import time
import os
import sys
import gzip
from hd_logging.otlp_formatter import OpenTelemetryFormatter

# Reference: https://stackoverflow.com/questions/29602352/how-to-mix-logging-handlers-file-timed-and-compress-log-in-the-same-config-f
class SizeAndTimeLoggingHandler(TimedRotatingFileHandler):
    """ My rotating file hander to compress rotated file """
    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None,
                 delay=0, when='h', interval=1, utc=False, use_otlp_format=False, 
                 service_name=None, environment=None, service_version=None):
        if maxBytes > 0:
            mode = 'a'
        TimedRotatingFileHandler.__init__(
            self, filename, when, interval, backupCount, encoding, delay, utc)
        self.maxBytes = maxBytes
        self.backupCount = backupCount
        
        # OpenTelemetry format support
        self.use_otlp_format = use_otlp_format
        if use_otlp_format:
            from hd_logging.otlp_formatter import OpenTelemetryFormatter
            self.formatter = OpenTelemetryFormatter(
                service_name=service_name or "hd_logging",
                environment=environment or "development",
                service_version=service_version or "1.0.0"
            )

    def shouldRollover(self, record):
        """ Determine if rollover should occur. """
        # Check rollover by size
        if self.stream is None:                 # delay was set...
            self.stream = self._open()
        if self.maxBytes > 0:                   # are we rolling over?
            try:
                msg = "%s\n" % self.format(record)
                # Handle case where file was rotated/deleted by another process
                # (common in multiprocessing with fork())
                try:
                    self.stream.seek(0, 2)  #due to non-posix-compliant Windows feature
                    current_size = self.stream.tell()
                except (OSError, IOError, ValueError) as e:
                    # File was rotated/deleted by another process, reopen it
                    # This prevents FileNotFoundError in multiprocessing scenarios
                    try:
                        self.stream.close()
                    except Exception:
                        pass
                    self.stream = self._open()
                    self.stream.seek(0, 2)
                    current_size = self.stream.tell()
                
                if current_size + len(msg) >= self.maxBytes:
                    return 1
            except Exception as e:
                # If format() or stream operations fail, don't rollover
                # Log to stderr as fallback (can't use logger here - recursion risk)
                try:
                    print(f"WARNING: shouldRollover failed: {type(e).__name__}: {e}", file=sys.stderr)
                except Exception:
                    pass
                # Return 0 to prevent rollover on error
                return 0
        # Check rollover by time
        t = int(time.time())
        if t >= self.rolloverAt:
            return 1
        return 0

    def emit(self, record):
        """
        Emit a record with error handling to prevent logging failures from crashing the application.
        
        This wraps the parent emit() method to catch and handle exceptions that might occur
        during formatting, file writing, or rotation. If an error occurs, it falls back to
        stderr to ensure the error is visible without causing recursion.
        """
        try:
            super().emit(record)
        except Exception as e:
            # If logging fails, write to stderr as fallback to prevent recursion
            # This prevents the logging error handler from trying to log the error,
            # which could cause infinite recursion if the handler itself is broken
            try:
                print(f"Logging handler error: {type(e).__name__}: {e}", file=sys.stderr)
                print(f"Failed to log record: {record.getMessage()}", file=sys.stderr)
            except Exception:
                # Even stderr write failed - use absolute last resort
                pass
            # Don't re-raise - we've handled the error, don't let it propagate

    def rotate(self, source, dest):
        """ Compress rotated log file with error handling """
        try:
            os.rename(source, dest)
            with open(dest, 'rb') as f_in:
                with gzip.open("%s.gz" % dest, 'wb') as f_out:
                    f_out.writelines(f_in)
            os.remove(dest)
        except Exception as e:
            # If rotation fails, log to stderr and continue
            # Don't let rotation failures break logging
            try:
                print(f"Log rotation error: {type(e).__name__}: {e}", file=sys.stderr)
                print(f"Source: {source}, Dest: {dest}", file=sys.stderr)
            except Exception:
                pass
            # Re-raise to let the handler know rotation failed
            # The handler should handle this gracefully
            raise