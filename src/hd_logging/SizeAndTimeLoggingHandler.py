"""
Size and Time Rotating Logging Handler with Compression
Custom logging handler that rotates logs based on both size and time, with automatic compression.
Supports both plain text and OpenTelemetry JSON formats.
"""

from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import colorlog
import time
import os
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
            msg = "%s\n" % self.format(record)
            self.stream.seek(0, 2)  #due to non-posix-compliant Windows feature
            if self.stream.tell() + len(msg) >= self.maxBytes:
                return 1
        # Check rollover by time
        t = int(time.time())
        if t >= self.rolloverAt:
            return 1
        return 0

    def rotate(self, source, dest):
        """ Compress rotated log file """
        os.rename(source, dest)
        f_in = open(dest, 'rb')
        f_out = gzip.open("%s.gz" % dest, 'wb')
        f_out.writelines(f_in)
        f_out.close()
        f_in.close()
        os.remove(dest)
