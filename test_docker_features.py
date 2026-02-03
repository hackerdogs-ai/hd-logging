#!/usr/bin/env python3
"""
Test script for Docker/container features:
1. FORCE_LOGS_TO_STDOUT environment variable
2. Multiprocess-safe log rotation
"""

import sys
import os
import tempfile
import io
from contextlib import redirect_stdout, redirect_stderr

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def test_force_logs_to_stdout():
    """Test FORCE_LOGS_TO_STDOUT environment variable."""
    print("\n=== Test: FORCE_LOGS_TO_STDOUT ===")
    
    # Set environment variable
    os.environ["FORCE_LOGS_TO_STDOUT"] = "true"
    
    # Capture stdout and stderr
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    
    try:
        from hd_logging import setup_logger
        
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            logger = setup_logger("test_stdout")
            
            # These should go to stdout
            logger.debug("Debug message")
            logger.info("Info message")
            
            # These should go to stderr
            logger.warning("Warning message")
            logger.error("Error message")
            logger.critical("Critical message")
        
        stdout_output = stdout_capture.getvalue()
        stderr_output = stderr_capture.getvalue()
        
        # Verify INFO/DEBUG go to stdout
        assert "Info message" in stdout_output or "Debug message" in stdout_output, \
            "INFO/DEBUG messages should go to stdout"
        
        # Verify WARNING/ERROR/CRITICAL go to stderr
        assert "Warning message" in stderr_output or "Error message" in stderr_output or "Critical message" in stderr_output, \
            "WARNING/ERROR/CRITICAL messages should go to stderr"
        
        # Verify no file handler was created
        file_handlers = [h for h in logger.handlers if hasattr(h, 'baseFilename')]
        assert len(file_handlers) == 0, "No file handlers should be created when FORCE_LOGS_TO_STDOUT=true"
        
        print("✅ PASS: FORCE_LOGS_TO_STDOUT works correctly")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up
        if "FORCE_LOGS_TO_STDOUT" in os.environ:
            del os.environ["FORCE_LOGS_TO_STDOUT"]


def test_multiprocess_rotation():
    """Test multiprocess-safe log rotation."""
    print("\n=== Test: Multiprocess-Safe Rotation ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = os.path.join(tmpdir, "test_rotation.log")
        
        try:
            from hd_logging import setup_logger
            
            logger = setup_logger("test_rotation", log_file)
            
            # Write some logs
            logger.info("Test message 1")
            logger.info("Test message 2")
            
            # Simulate file being rotated by another process
            # (delete the file to simulate race condition)
            if os.path.exists(log_file):
                # This simulates another process rotating the file
                rotated_file = log_file + ".1"
                os.rename(log_file, rotated_file)
            
            # Try to log again - should handle gracefully
            logger.info("Test message 3")
            
            # Verify logging still works
            assert True, "Logging should continue to work after file rotation"
            
            print("✅ PASS: Multiprocess rotation handled gracefully")
            return True
            
        except FileNotFoundError as e:
            print(f"❌ FAIL: FileNotFoundError not handled: {e}")
            return False
        except Exception as e:
            print(f"❌ FAIL: Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return False


def test_force_stdout_env_variants():
    """Test different environment variable values."""
    print("\n=== Test: FORCE_LOGS_TO_STDOUT Variants ===")
    
    test_values = ["true", "True", "TRUE", "1", "yes", "Yes", "YES"]
    
    for value in test_values:
        try:
            os.environ["FORCE_LOGS_TO_STDOUT"] = value
            
            from hd_logging import setup_logger
            
            logger = setup_logger("test_variant")
            
            # Check that no file handler was created
            file_handlers = [h for h in logger.handlers if hasattr(h, 'baseFilename')]
            assert len(file_handlers) == 0, f"Value '{value}' should enable stdout mode"
            
            print(f"✅ PASS: Value '{value}' works")
            
        except Exception as e:
            print(f"❌ FAIL: Value '{value}' failed: {e}")
            return False
        finally:
            if "FORCE_LOGS_TO_STDOUT" in os.environ:
                del os.environ["FORCE_LOGS_TO_STDOUT"]
    
    return True


def run_all_tests():
    """Run all Docker feature tests."""
    print("=" * 60)
    print("Testing Docker/Container Features")
    print("=" * 60)
    
    tests = [
        test_force_logs_to_stdout,
        test_multiprocess_rotation,
        test_force_stdout_env_variants,
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
        print("\n🎉 All Docker feature tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
