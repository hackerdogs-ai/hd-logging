#!/usr/bin/env python3
"""
Test that warnings go to stdout and errors go to stderr.
"""

import sys
import os
import tempfile
import io
import unittest.mock
from contextlib import redirect_stdout, redirect_stderr

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def test_warnings_to_stdout():
    """Test that warnings are printed to stdout."""
    print("\n=== Test: Warnings to stdout ===")
    
    try:
        from hd_logging import setup_logger
        
        # Capture stdout
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            # This should generate a warning (directory creation might fail)
            logger = setup_logger("test_warn_stdout", log_file_path="/invalid/path/test.log")
            logger.info("Test message")
        
        stdout_output = stdout_capture.getvalue()
        stderr_output = stderr_capture.getvalue()
        
        # Check that warnings are in stdout
        if "Warning:" in stdout_output:
            print("✅ PASS: Warnings are printed to stdout")
            print(f"   Sample: {stdout_output.strip()[:100]}")
            return True
        else:
            print(f"❌ FAIL: No warnings found in stdout")
            print(f"   stdout: {stdout_output}")
            print(f"   stderr: {stderr_output}")
            return False
            
    except Exception as e:
        print(f"❌ FAIL: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_errors_to_stderr():
    """Test that errors are printed to stderr."""
    print("\n=== Test: Errors to stderr ===")
    
    try:
        from hd_logging.SizeAndTimeLoggingHandler import SizeAndTimeLoggingHandler
        import logging
        import tempfile
        import io
        
        with tempfile.TemporaryDirectory() as tmpdir:
            handler = SizeAndTimeLoggingHandler(
                filename=os.path.join(tmpdir, "test.log")
            )
            
            handler.setLevel(logging.INFO)
            handler.setFormatter(logging.Formatter('%(message)s'))
            
            # Create a record
            record = logging.LogRecord(
                name="test",
                level=logging.INFO,
                pathname="",
                lineno=0,
                msg="Test message",
                args=(),
                exc_info=None
            )
            
            # Capture stderr
            stderr_capture = io.StringIO()
            stdout_capture = io.StringIO()
            
            # Mock super().emit() to raise an exception
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                with unittest.mock.patch.object(handler.__class__.__bases__[0], 'emit', side_effect=IOError("Write failed")):
                    handler.emit(record)
            
            stderr_output = stderr_capture.getvalue()
            stdout_output = stdout_capture.getvalue()
            
            # Check that errors are in stderr
            if "Error:" in stderr_output:
                print("✅ PASS: Errors are printed to stderr")
                print(f"   Sample: {stderr_output.strip()[:100]}")
                return True
            else:
                print(f"❌ FAIL: No errors found in stderr")
                print(f"   stdout: {stdout_output}")
                print(f"   stderr: {stderr_output}")
                return False
                
    except Exception as e:
        print(f"❌ FAIL: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_warning_vs_error_categorization():
    """Test that warnings and errors are correctly categorized."""
    print("\n=== Test: Warning vs Error categorization ===")
    
    try:
        from hd_logging import setup_logger
        import unittest.mock
        
        # Test 1: File handler creation failure (should be warning - we continue with console)
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            with unittest.mock.patch('hd_logging.SizeAndTimeLoggingHandler.SizeAndTimeLoggingHandler', side_effect=PermissionError("Permission denied")):
                logger = setup_logger("test_cat", log_file_path="/root/test.log")
                logger.info("Test")
        
        stdout_output = stdout_capture.getvalue()
        stderr_output = stderr_capture.getvalue()
        
        # File handler creation failure should be a warning (non-critical)
        if "Warning:" in stdout_output and "Could not create file handler" in stdout_output:
            print("✅ PASS: File handler creation failure is a warning (to stdout)")
        else:
            print(f"❌ FAIL: File handler creation failure not categorized as warning")
            print(f"   stdout: {stdout_output}")
            print(f"   stderr: {stderr_output}")
            return False
        
        # Test 2: Test actual error case - emit() error should go to stderr
        from hd_logging.SizeAndTimeLoggingHandler import SizeAndTimeLoggingHandler
        import logging
        import tempfile
        
        stdout_capture2 = io.StringIO()
        stderr_capture2 = io.StringIO()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            handler = SizeAndTimeLoggingHandler(
                filename=os.path.join(tmpdir, "test.log")
            )
            handler.setLevel(logging.INFO)
            handler.setFormatter(logging.Formatter('%(message)s'))
            
            record = logging.LogRecord(
                name="test",
                level=logging.INFO,
                pathname="",
                lineno=0,
                msg="Test message",
                args=(),
                exc_info=None
            )
            
            with redirect_stdout(stdout_capture2), redirect_stderr(stderr_capture2):
                # Mock super().emit() to raise an exception
                with unittest.mock.patch.object(handler.__class__.__bases__[0], 'emit', side_effect=IOError("Write failed")):
                    handler.emit(record)
        
        stderr_output2 = stderr_capture2.getvalue()
        
        # Errors from emit() should go to stderr
        if "Error:" in stderr_output2 and "Logging handler error" in stderr_output2:
            print("✅ PASS: Handler errors go to stderr")
        else:
            print(f"❌ FAIL: Handler errors not in stderr")
            print(f"   stderr: {stderr_output2}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Testing stdout/stderr Output")
    print("=" * 60)
    
    tests = [
        test_warnings_to_stdout,
        test_errors_to_stderr,
        test_warning_vs_error_categorization,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ FAIL: Test {test.__name__} crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    for i, (test, result) in enumerate(zip(tests, results), 1):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i}. {test.__name__}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Warnings go to stdout, errors go to stderr.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
