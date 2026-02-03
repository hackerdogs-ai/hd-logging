#!/usr/bin/env python3
"""
Test that FORCE_LOGS_TO_STDOUT=true prevents file logging even when file path is specified.
"""

import sys
import os
import tempfile

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def test_force_stdout_ignores_file_path():
    """Test that file path is ignored when FORCE_LOGS_TO_STDOUT=true."""
    print("\n=== Test: FORCE_LOGS_TO_STDOUT ignores file path ===")
    
    # Set environment variable
    os.environ["FORCE_LOGS_TO_STDOUT"] = "true"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = os.path.join(tmpdir, "should_not_exist.log")
        
        try:
            from hd_logging import setup_logger
            
            # Create logger with explicit file path
            logger = setup_logger("test_no_file", log_file_path=log_file)
            
            # Log some messages
            logger.info("Test message 1")
            logger.error("Test message 2")
            
            # Verify NO file was created
            if os.path.exists(log_file):
                print(f"❌ FAIL: File was created at {log_file} even though FORCE_LOGS_TO_STDOUT=true")
                return False
            
            # Verify no file handlers exist
            file_handlers = [h for h in logger.handlers if hasattr(h, 'baseFilename')]
            if len(file_handlers) > 0:
                print(f"❌ FAIL: File handlers found: {file_handlers}")
                return False
            
            # Verify only stream handlers exist
            stream_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)]
            if len(stream_handlers) != 2:
                print(f"❌ FAIL: Expected 2 stream handlers, found {len(stream_handlers)}")
                return False
            
            # Verify handlers are stdout and stderr
            stdout_handlers = [h for h in stream_handlers if h.stream == sys.stdout]
            stderr_handlers = [h for h in stream_handlers if h.stream == sys.stderr]
            
            if len(stdout_handlers) != 1:
                print(f"❌ FAIL: Expected 1 stdout handler, found {len(stdout_handlers)}")
                return False
            
            if len(stderr_handlers) != 1:
                print(f"❌ FAIL: Expected 1 stderr handler, found {len(stderr_handlers)}")
                return False
            
            print("✅ PASS: File path is ignored when FORCE_LOGS_TO_STDOUT=true")
            print(f"   - No file created at: {log_file}")
            print(f"   - File handlers: {len(file_handlers)}")
            print(f"   - Stream handlers: {len(stream_handlers)} (stdout: {len(stdout_handlers)}, stderr: {len(stderr_handlers)})")
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


def test_force_stdout_with_explicit_file_path():
    """Test with explicit file path parameter."""
    print("\n=== Test: FORCE_LOGS_TO_STDOUT with explicit file path ===")
    
    os.environ["FORCE_LOGS_TO_STDOUT"] = "true"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        explicit_file = os.path.join(tmpdir, "explicit.log")
        
        try:
            from hd_logging import setup_logger
            import logging
            
            # Create logger with explicit file path
            logger = setup_logger(
                "test_explicit",
                log_file_path=explicit_file,
                log_level_console=logging.INFO,
                log_level_files=logging.DEBUG
            )
            
            # Log messages
            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")
            logger.error("Error message")
            
            # Verify file was NOT created
            if os.path.exists(explicit_file):
                print(f"❌ FAIL: File was created at {explicit_file}")
                return False
            
            # Verify no file handlers
            file_handlers = [h for h in logger.handlers if hasattr(h, 'baseFilename')]
            if len(file_handlers) > 0:
                print(f"❌ FAIL: File handlers found: {[h.baseFilename for h in file_handlers]}")
                return False
            
            print("✅ PASS: Explicit file path is ignored when FORCE_LOGS_TO_STDOUT=true")
            return True
            
        except Exception as e:
            print(f"❌ FAIL: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            if "FORCE_LOGS_TO_STDOUT" in os.environ:
                del os.environ["FORCE_LOGS_TO_STDOUT"]


def test_normal_behavior_without_force_stdout():
    """Test that normal behavior still works when FORCE_LOGS_TO_STDOUT is not set."""
    print("\n=== Test: Normal behavior without FORCE_LOGS_TO_STDOUT ===")
    
    # Make sure env var is not set
    if "FORCE_LOGS_TO_STDOUT" in os.environ:
        del os.environ["FORCE_LOGS_TO_STDOUT"]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = os.path.join(tmpdir, "should_exist.log")
        
        try:
            from hd_logging import setup_logger
            
            # Create logger with file path
            logger = setup_logger("test_normal", log_file_path=log_file)
            
            # Log some messages
            logger.info("Test message")
            
            # Verify file handler exists
            file_handlers = [h for h in logger.handlers if hasattr(h, 'baseFilename')]
            if len(file_handlers) == 0:
                print("❌ FAIL: No file handler found when FORCE_LOGS_TO_STDOUT is not set")
                return False
            
            # Verify file was created (or at least handler is configured)
            handler_file = file_handlers[0].baseFilename
            if handler_file != log_file:
                print(f"❌ FAIL: Handler file path mismatch. Expected: {log_file}, Got: {handler_file}")
                return False
            
            print("✅ PASS: Normal behavior works - file handler is created")
            return True
            
        except Exception as e:
            print(f"❌ FAIL: {e}")
            import traceback
            traceback.print_exc()
            return False


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Testing FORCE_LOGS_TO_STDOUT file path behavior")
    print("=" * 60)
    
    tests = [
        test_force_stdout_ignores_file_path,
        test_force_stdout_with_explicit_file_path,
        test_normal_behavior_without_force_stdout,
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
        print("\n🎉 All tests passed! File path is correctly ignored when FORCE_LOGS_TO_STDOUT=true")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")
        return 1


if __name__ == "__main__":
    import logging
    sys.exit(run_all_tests())
