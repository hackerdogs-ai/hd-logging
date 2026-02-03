#!/usr/bin/env python3
"""
Verify all requirements are implemented correctly.
"""

import sys
import os
import tempfile
import unittest.mock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def test_requirement_1_file_open_failure():
    """Requirement 1: setup_logger() on file open failure, use only stream handlers."""
    print("\n=== Requirement 1: File open failure handling ===")
    
    try:
        from hd_logging import setup_logger
        import logging
        
        # Clear any existing handlers first
        test_logger = logging.getLogger("test_req1")
        test_logger.handlers.clear()
        
        # Mock file handler creation to raise PermissionError
        with unittest.mock.patch('hd_logging.SizeAndTimeLoggingHandler.SizeAndTimeLoggingHandler', side_effect=PermissionError("Permission denied")):
            logger = setup_logger("test_req1", log_file_path="/root/cannot_write.log")
            
            # Should have stream handlers but no file handlers
            file_handlers = [h for h in logger.handlers if hasattr(h, 'baseFilename')]
            stream_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)]
            
            if len(file_handlers) > 0:
                print(f"❌ FAIL: File handlers found when file open should fail: {len(file_handlers)}")
                print(f"   Handlers: {[type(h).__name__ for h in logger.handlers]}")
                return False
            
            if len(stream_handlers) == 0:
                print(f"❌ FAIL: No stream handlers found")
                return False
            
            # Should be able to log
            logger.info("Test message")
            
            # Should not raise exception
            print("✅ PASS: File open failure handled - uses stream handlers only")
            return True
            
    except PermissionError:
        print("❌ FAIL: PermissionError was not caught - should not raise")
        return False
    except Exception as e:
        print(f"❌ FAIL: Exception raised: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_requirement_2_rotate_check_exists():
    """Requirement 2: rotate() checks os.path.exists(source) before rename."""
    print("\n=== Requirement 2: rotate() checks source exists ===")
    
    try:
        from hd_logging.SizeAndTimeLoggingHandler import SizeAndTimeLoggingHandler
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            handler = SizeAndTimeLoggingHandler(
                filename=os.path.join(tmpdir, "test.log"),
                delete_on_compression=False
            )
            
            # Test with non-existent source
            source = os.path.join(tmpdir, "nonexistent.log")
            dest = os.path.join(tmpdir, "rotated.log")
            
            # Should return without error
            handler.rotate(source, dest)
            
            # Should not create dest file
            if os.path.exists(dest):
                print(f"❌ FAIL: Dest file created when source doesn't exist")
                return False
            
            print("✅ PASS: rotate() checks source exists before rename")
            return True
            
    except Exception as e:
        print(f"❌ FAIL: Exception raised: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_requirement_3_rotate_catch_filenotfound():
    """Requirement 3: rotate() catches FileNotFoundError and skips."""
    print("\n=== Requirement 3: rotate() catches FileNotFoundError ===")
    
    try:
        from hd_logging.SizeAndTimeLoggingHandler import SizeAndTimeLoggingHandler
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            handler = SizeAndTimeLoggingHandler(
                filename=os.path.join(tmpdir, "test.log"),
                delete_on_compression=False
            )
            
            source = os.path.join(tmpdir, "source.log")
            dest = os.path.join(tmpdir, "dest.log")
            
            # Create source file
            with open(source, 'w') as f:
                f.write("test")
            
            # Mock os.rename to raise FileNotFoundError
            with unittest.mock.patch('os.rename', side_effect=FileNotFoundError("File not found")):
                # Should not raise, should return gracefully
                handler.rotate(source, dest)
            
            print("✅ PASS: rotate() catches FileNotFoundError and skips")
            return True
            
    except FileNotFoundError:
        print("❌ FAIL: FileNotFoundError was not caught")
        return False
    except Exception as e:
        print(f"❌ FAIL: Unexpected exception: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_requirement_4_shouldrollover_stream_errors():
    """Requirement 4: shouldRollover() on stream errors, reopen and retry."""
    print("\n=== Requirement 4: shouldRollover() handles stream errors ===")
    
    try:
        from hd_logging.SizeAndTimeLoggingHandler import SizeAndTimeLoggingHandler
        import logging
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            handler = SizeAndTimeLoggingHandler(
                filename=os.path.join(tmpdir, "test.log"),
                maxBytes=100
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
            
            # Mock stream.seek to raise OSError first time, then work
            call_count = [0]
            original_seek = handler.stream.seek
            
            def mock_seek(*args, **kwargs):
                call_count[0] += 1
                if call_count[0] == 1:
                    raise OSError("Stream error")
                return original_seek(*args, **kwargs)
            
            handler.stream.seek = mock_seek
            
            # Should handle the error and retry
            result = handler.shouldRollover(record)
            
            # Should return 0 or 1 (not raise)
            if result not in (0, 1):
                print(f"❌ FAIL: shouldRollover returned unexpected value: {result}")
                return False
            
            print("✅ PASS: shouldRollover() handles stream errors and retries")
            return True
            
    except Exception as e:
        print(f"❌ FAIL: Exception raised: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_requirement_5_emit_error_handling():
    """Requirement 5: emit() wraps write in try/except, prints to stderr, doesn't re-raise."""
    print("\n=== Requirement 5: emit() error handling ===")
    
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
            
            # Mock super().emit() to raise an exception
            original_emit = handler.__class__.__bases__[0].emit
            
            with unittest.mock.patch.object(handler.__class__.__bases__[0], 'emit', side_effect=IOError("Write failed")):
                # Capture stderr
                stderr_capture = io.StringIO()
                
                import sys
                old_stderr = sys.stderr
                sys.stderr = stderr_capture
                
                try:
                    # Should not raise
                    handler.emit(record)
                    
                    # Should have printed to stderr
                    stderr_output = stderr_capture.getvalue()
                    if "Logging handler error" not in stderr_output:
                        print(f"❌ FAIL: Error not printed to stderr")
                        return False
                    
                    print("✅ PASS: emit() handles errors, prints to stderr, doesn't re-raise")
                    return True
                finally:
                    sys.stderr = old_stderr
                    
    except Exception as e:
        print(f"❌ FAIL: Exception raised: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_requirement_6_force_stdout():
    """Requirement 6: setup_logger() if FORCE_LOGS_TO_STDOUT=true, use only stdout/stderr handlers."""
    print("\n=== Requirement 6: FORCE_LOGS_TO_STDOUT ===")
    
    try:
        from hd_logging import setup_logger
        import logging
        
        os.environ["FORCE_LOGS_TO_STDOUT"] = "true"
        
        try:
            logger = setup_logger("test_req6", log_file_path="logs/test.log")
            
            # Should have no file handlers
            file_handlers = [h for h in logger.handlers if hasattr(h, 'baseFilename')]
            if len(file_handlers) > 0:
                print(f"❌ FAIL: File handlers found when FORCE_LOGS_TO_STDOUT=true: {len(file_handlers)}")
                return False
            
            # Should have stream handlers
            stream_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)]
            if len(stream_handlers) == 0:
                print(f"❌ FAIL: No stream handlers found")
                return False
            
            # Should be able to log
            logger.info("Test message")
            
            print("✅ PASS: FORCE_LOGS_TO_STDOUT uses only stdout/stderr handlers")
            return True
        finally:
            if "FORCE_LOGS_TO_STDOUT" in os.environ:
                del os.environ["FORCE_LOGS_TO_STDOUT"]
            
    except Exception as e:
        print(f"❌ FAIL: Exception raised: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all requirement verification tests."""
    print("=" * 60)
    print("Verifying All Requirements")
    print("=" * 60)
    
    tests = [
        ("1. File open failure handling", test_requirement_1_file_open_failure),
        ("2. rotate() checks source exists", test_requirement_2_rotate_check_exists),
        ("3. rotate() catches FileNotFoundError", test_requirement_3_rotate_catch_filenotfound),
        ("4. shouldRollover() stream error handling", test_requirement_4_shouldrollover_stream_errors),
        ("5. emit() error handling", test_requirement_5_emit_error_handling),
        ("6. FORCE_LOGS_TO_STDOUT", test_requirement_6_force_stdout),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ FAIL: Test {name} crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Requirement Verification Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} requirements verified")
    
    if passed == total:
        print("\n🎉 All requirements are correctly implemented!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} requirement(s) need attention.")
        return 1


if __name__ == "__main__":
    import logging
    sys.exit(run_all_tests())
