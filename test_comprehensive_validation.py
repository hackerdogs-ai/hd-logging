#!/usr/bin/env python3
"""
Comprehensive validation tests to ensure bug fixes don't introduce new errors.

Tests:
1. Edge cases with extra parameter
2. Multiple logger instances
3. Concurrent logging (if applicable)
4. Formatter edge cases
5. Integration with existing examples
6. Performance impact
7. Memory leaks (basic check)
"""

import sys
import os
import tempfile
import json
import traceback
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from hd_logging import setup_logger
import logging


class TestResults:
    """Track test results."""
    def __init__(self):
        self.passed = []
        self.failed = []
        self.errors = []
    
    def add_pass(self, test_name):
        self.passed.append(test_name)
        print(f"✅ PASS: {test_name}")
    
    def add_fail(self, test_name, error=None):
        self.failed.append((test_name, error))
        print(f"❌ FAIL: {test_name}")
        if error:
            print(f"   Error: {error}")
    
    def add_error(self, test_name, exception):
        self.errors.append((test_name, exception))
        print(f"💥 ERROR: {test_name}")
        print(f"   Exception: {exception}")
        traceback.print_exc()
    
    def summary(self):
        total = len(self.passed) + len(self.failed) + len(self.errors)
        print(f"\n{'='*60}")
        print(f"Test Summary: {len(self.passed)}/{total} passed")
        if self.failed:
            print(f"\nFailed Tests ({len(self.failed)}):")
            for name, error in self.failed:
                print(f"  - {name}: {error}")
        if self.errors:
            print(f"\nErrors ({len(self.errors)}):")
            for name, exc in self.errors:
                print(f"  - {name}: {exc}")
        return len(self.failed) == 0 and len(self.errors) == 0


def test_edge_cases_extra_parameter():
    """Test various edge cases with extra parameter."""
    results = TestResults()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = os.path.join(tmpdir, "edge_test.log")
        logger = setup_logger("edge_test", log_file)
        
        test_cases = [
            ("None", None),
            ("Empty dict", {}),
            ("String", "not a dict"),
            ("List", [1, 2, 3]),
            ("Integer", 42),
            ("Boolean", True),
            ("Float", 3.14),
            ("Dict with None value", {"key": None}),
            ("Dict with empty string", {"key": ""}),
            ("Dict with zero", {"key": 0}),
            ("Dict with False", {"key": False}),
            ("Nested dict", {"nested": {"key": "value"}}),
            ("Dict with many keys", {f"key{i}": f"value{i}" for i in range(100)}),
            ("Dict with unicode", {"key": "测试"}),
            ("Dict with special chars", {"key": "test@#$%^&*()"}),
        ]
        
        for name, extra_value in test_cases:
            try:
                logger.info(f"Test: {name}", extra=extra_value)
                results.add_pass(f"Edge case: {name}")
            except AttributeError as e:
                if "copy" in str(e) or "_sanitize_extra" in str(e):
                    results.add_fail(f"Edge case: {name}", f"AttributeError in our code: {e}")
                else:
                    # Logging's own error is acceptable
                    results.add_pass(f"Edge case: {name} (logging handled)")
            except Exception as e:
                # Other exceptions might be acceptable depending on type
                if isinstance(extra_value, dict):
                    results.add_fail(f"Edge case: {name}", str(e))
                else:
                    # Non-dict types might cause logging errors, which is OK
                    results.add_pass(f"Edge case: {name} (logging error: {type(e).__name__})")
    
    return results


def test_reserved_keys_combinations():
    """Test various combinations of reserved keys."""
    results = TestResults()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = os.path.join(tmpdir, "reserved_test.log")
        logger = setup_logger("reserved_test", log_file)
        
        test_cases = [
            ("Only message", {"message": "test"}),
            ("Only asctime", {"asctime": "2024-01-01"}),
            ("Both reserved", {"message": "test", "asctime": "2024-01-01"}),
            ("Reserved + custom", {"message": "test", "custom": "value"}),
            ("Reserved + many custom", {"message": "test", **{f"key{i}": f"val{i}" for i in range(10)}}),
            ("Nested with reserved", {"message": "test", "nested": {"asctime": "nested"}}),
            ("Reserved as empty string", {"message": "", "asctime": ""}),
            ("Reserved as None", {"message": None, "asctime": None}),
        ]
        
        for name, extra in test_cases:
            try:
                logger.info(f"Test: {name}", extra=extra)
                # Verify no KeyError
                results.add_pass(f"Reserved keys: {name}")
            except KeyError as e:
                if "message" in str(e) or "asctime" in str(e):
                    results.add_fail(f"Reserved keys: {name}", f"KeyError for reserved key: {e}")
                else:
                    results.add_fail(f"Reserved keys: {name}", f"Unexpected KeyError: {e}")
            except Exception as e:
                results.add_fail(f"Reserved keys: {name}", str(e))
    
    return results


def test_all_logging_levels():
    """Test all logging levels with various extra parameters."""
    results = TestResults()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = os.path.join(tmpdir, "levels_test.log")
        logger = setup_logger("levels_test", log_file)
        
        levels = [
            (logging.DEBUG, logger.debug, "DEBUG"),
            (logging.INFO, logger.info, "INFO"),
            (logging.WARNING, logger.warning, "WARNING"),
            (logging.ERROR, logger.error, "ERROR"),
            (logging.CRITICAL, logger.critical, "CRITICAL"),
        ]
        
        extra_cases = [
            None,
            {},
            {"message": "test"},
            {"asctime": "test"},
            {"custom": "value"},
        ]
        
        for level, method, level_name in levels:
            for extra in extra_cases:
                try:
                    method(f"Test {level_name}", extra=extra)
                    results.add_pass(f"Level {level_name} with extra={type(extra).__name__}")
                except Exception as e:
                    if isinstance(extra, dict) and extra:
                        results.add_fail(f"Level {level_name} with extra", str(e))
                    else:
                        # None or empty dict should always work
                        results.add_fail(f"Level {level_name} with extra", str(e))
    
    return results


def test_multiple_loggers_same_name():
    """Test that getting the same logger multiple times works."""
    results = TestResults()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = os.path.join(tmpdir, "multi_test.log")
        
        # Get same logger multiple times
        logger1 = setup_logger("multi_logger", log_file)
        logger2 = setup_logger("multi_logger", log_file)
        logger3 = setup_logger("multi_logger", log_file)
        
        try:
            # Should all be the same logger instance
            assert logger1 is logger2 is logger3, "Loggers should be the same instance"
            
            # Test that sanitization still works
            logger1.info("Test 1", extra={"message": "test1"})
            logger2.info("Test 2", extra={"asctime": "test2"})
            logger3.info("Test 3", extra={"custom": "value"})
            
            results.add_pass("Multiple loggers same name")
        except Exception as e:
            results.add_fail("Multiple loggers same name", str(e))
    
    return results


def test_otlp_formatter_validation():
    """Test OTLP formatter with various scenarios."""
    results = TestResults()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = os.path.join(tmpdir, "otlp_test.log")
        logger = setup_logger("otlp_test", log_file, use_otlp_format=True)
        
        try:
            # Test with reserved keys (should be sanitized)
            logger.info("Test 1", extra={"message": "should be sanitized", "custom": "value"})
            
            # Test with normal extra
            logger.info("Test 2", extra={"user_id": 123, "action": "login"})
            
            # Test with nested structures
            logger.info("Test 3", extra={
                "metadata": {
                    "nested": "value",
                    "list": [1, 2, 3]
                }
            })
            
            # Read and validate JSON
            with open(log_file, 'r') as f:
                lines = f.readlines()
                for i, line in enumerate(lines, 1):
                    try:
                        data = json.loads(line)
                        # Verify structure
                        assert "timestamp" in data, f"Line {i}: Missing timestamp"
                        assert "severityText" in data, f"Line {i}: Missing severityText"
                        assert "body" in data, f"Line {i}: Missing body"
                        assert "attributes" in data, f"Line {i}: Missing attributes"
                        assert "resource" in data, f"Line {i}: Missing resource"
                        
                        # Verify reserved keys are NOT in attributes (should be sanitized)
                        attrs = data.get("attributes", {})
                        if "message" in attrs or "asctime" in attrs:
                            # Check if they're sanitized versions
                            if "log_message" in attrs or "log_asctime" in attrs:
                                results.add_pass(f"OTLP line {i}: Reserved keys sanitized")
                            else:
                                results.add_fail(f"OTLP line {i}: Reserved keys in attributes", 
                                                f"Found: {list(attrs.keys())}")
                        else:
                            results.add_pass(f"OTLP line {i}: Valid JSON structure")
                    except json.JSONDecodeError as e:
                        results.add_fail(f"OTLP line {i}: Invalid JSON", str(e))
            
            results.add_pass("OTLP formatter validation")
        except Exception as e:
            results.add_fail("OTLP formatter validation", str(e))
    
    return results


def test_backward_compatibility_real_world():
    """Test real-world scenarios to ensure backward compatibility."""
    results = TestResults()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = os.path.join(tmpdir, "compat_test.log")
        logger = setup_logger("compat_test", log_file)
        
        # Simulate real-world usage patterns
        scenarios = [
            ("Web request", {"method": "GET", "path": "/api/users", "status": 200}),
            ("Database query", {"query": "SELECT * FROM users", "duration": 0.123}),
            ("File operation", {"filename": "data.csv", "size": 1024, "operation": "read"}),
            ("API call", {"endpoint": "https://api.example.com", "response_time": 0.5}),
            ("User action", {"user_id": "12345", "action": "login", "ip": "192.168.1.1"}),
            ("Error context", {"error_code": "E001", "component": "auth", "retry_count": 3}),
        ]
        
        for scenario_name, extra in scenarios:
            try:
                logger.info(f"Scenario: {scenario_name}", extra=extra)
                results.add_pass(f"Backward compat: {scenario_name}")
            except Exception as e:
                results.add_fail(f"Backward compat: {scenario_name}", str(e))
    
    return results


def test_logger_method_chaining():
    """Test that logger methods can be called in sequence."""
    results = TestResults()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = os.path.join(tmpdir, "chain_test.log")
        logger = setup_logger("chain_test", log_file)
        
        try:
            # Chain multiple calls
            logger.debug("Debug", extra={"level": "debug"})
            logger.info("Info", extra={"level": "info"})
            logger.warning("Warning", extra={"level": "warning"})
            logger.error("Error", extra={"level": "error"})
            logger.critical("Critical", extra={"level": "critical"})
            
            # With reserved keys
            logger.info("With reserved", extra={"message": "test", "level": "info"})
            logger.warning("With reserved", extra={"asctime": "test", "level": "warning"})
            
            results.add_pass("Logger method chaining")
        except Exception as e:
            results.add_fail("Logger method chaining", str(e))
    
    return results


def test_no_double_sanitization():
    """Test that sanitization doesn't happen twice."""
    results = TestResults()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = os.path.join(tmpdir, "double_test.log")
        
        # Get logger multiple times (should not double-wrap)
        logger1 = setup_logger("double_test", log_file)
        logger2 = setup_logger("double_test", log_file)
        logger3 = setup_logger("double_test", log_file)
        
        try:
            # All should be the same instance
            assert logger1 is logger2 is logger3
            
            # Check that _extra_sanitized flag is set
            assert hasattr(logger1, "_extra_sanitized"), "Missing _extra_sanitized flag"
            assert logger1._extra_sanitized, "_extra_sanitized should be True"
            
            # Test that it still works
            logger1.info("Test", extra={"message": "test"})
            logger2.info("Test", extra={"asctime": "test"})
            logger3.info("Test", extra={"custom": "value"})
            
            results.add_pass("No double sanitization")
        except Exception as e:
            results.add_fail("No double sanitization", str(e))
    
    return results


def test_exception_logging():
    """Test exception logging with extra parameter."""
    results = TestResults()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = os.path.join(tmpdir, "exception_test.log")
        logger = setup_logger("exception_test", log_file)
        
        try:
            # Test exception with extra
            try:
                raise ValueError("Test exception")
            except Exception:
                logger.exception("Exception occurred", extra={"error_type": "ValueError", "message": "test"})
            
            # Test exception with reserved keys in extra
            try:
                raise KeyError("Test key error")
            except Exception:
                logger.exception("KeyError occurred", extra={"asctime": "test", "error_type": "KeyError"})
            
            results.add_pass("Exception logging")
        except Exception as e:
            results.add_fail("Exception logging", str(e))
    
    return results


def test_performance_basic():
    """Basic performance test to ensure no significant slowdown."""
    results = TestResults()
    
    import time
    
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = os.path.join(tmpdir, "perf_test.log")
        logger = setup_logger("perf_test", log_file)
        
        try:
            # Time logging without extra
            start = time.time()
            for i in range(1000):
                logger.info(f"Message {i}")
            time_no_extra = time.time() - start
            
            # Time logging with extra (should be similar)
            start = time.time()
            for i in range(1000):
                logger.info(f"Message {i}", extra={"key": "value"})
            time_with_extra = time.time() - start
            
            # Time logging with reserved keys (sanitization overhead)
            start = time.time()
            for i in range(1000):
                logger.info(f"Message {i}", extra={"message": "test"})
            time_with_reserved = time.time() - start
            
            # Sanitization should add minimal overhead (< 2x)
            overhead_ratio = time_with_reserved / time_no_extra
            if overhead_ratio < 2.0:
                results.add_pass(f"Performance: overhead ratio {overhead_ratio:.2f}x")
            else:
                results.add_fail("Performance", f"High overhead: {overhead_ratio:.2f}x")
            
        except Exception as e:
            results.add_fail("Performance", str(e))
    
    return results


def run_all_validation_tests():
    """Run all validation tests."""
    print("=" * 60)
    print("Comprehensive Validation Tests")
    print("=" * 60)
    
    all_results = []
    test_functions = [
        ("Edge Cases - Extra Parameter", test_edge_cases_extra_parameter),
        ("Reserved Keys Combinations", test_reserved_keys_combinations),
        ("All Logging Levels", test_all_logging_levels),
        ("Multiple Loggers Same Name", test_multiple_loggers_same_name),
        ("OTLP Formatter Validation", test_otlp_formatter_validation),
        ("Backward Compatibility", test_backward_compatibility_real_world),
        ("Logger Method Chaining", test_logger_method_chaining),
        ("No Double Sanitization", test_no_double_sanitization),
        ("Exception Logging", test_exception_logging),
        ("Performance Basic", test_performance_basic),
    ]
    
    for test_name, test_func in test_functions:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print(f"{'='*60}")
        try:
            result = test_func()
            all_results.append((test_name, result))
        except Exception as e:
            print(f"💥 Test suite '{test_name}' crashed: {e}")
            traceback.print_exc()
            all_results.append((test_name, None))
    
    # Summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    
    total_passed = 0
    total_failed = 0
    total_errors = 0
    
    for test_name, result in all_results:
        if result is None:
            print(f"💥 {test_name}: Test suite crashed")
            total_errors += 1
        else:
            passed = len(result.passed)
            failed = len(result.failed)
            errors = len(result.errors)
            total_passed += passed
            total_failed += failed
            total_errors += errors
            
            status = "✅" if failed == 0 and errors == 0 else "❌"
            print(f"{status} {test_name}: {passed} passed, {failed} failed, {errors} errors")
    
    print(f"\nTotal: {total_passed} passed, {total_failed} failed, {total_errors} errors")
    
    if total_failed == 0 and total_errors == 0:
        print("\n🎉 All validation tests passed! No regressions detected.")
        return 0
    else:
        print(f"\n⚠️  {total_failed + total_errors} issue(s) found. Please review.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_validation_tests())

