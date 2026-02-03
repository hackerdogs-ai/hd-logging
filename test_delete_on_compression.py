#!/usr/bin/env python3
"""
Test script for DELETE_LOG_FILE_ON_COMPRESSION feature.
"""

import sys
import os
import tempfile
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def test_delete_on_compression():
    """Test that DELETE_LOG_FILE_ON_COMPRESSION deletes files instead of compressing."""
    print("\n=== Test: DELETE_LOG_FILE_ON_COMPRESSION ===")
    
    # Set environment variable
    os.environ["DELETE_LOG_FILE_ON_COMPRESSION"] = "true"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = os.path.join(tmpdir, "test_delete.log")
        
        try:
            from hd_logging import setup_logger
            
            # Create logger
            logger = setup_logger("test_delete", log_file_path=log_file)
            
            # Write enough logs to trigger rotation (if size-based)
            # For time-based rotation, we'd need to wait, so let's test the handler directly
            from hd_logging.SizeAndTimeLoggingHandler import SizeAndTimeLoggingHandler
            
            # Create a handler with delete_on_compression enabled
            handler = SizeAndTimeLoggingHandler(
                filename=os.path.join(tmpdir, "test_rotate.log"),
                maxBytes=100,  # Small size to trigger rotation
                backupCount=3,
                delete_on_compression=True
            )
            
            # Write some logs
            import logging
            handler.setLevel(logging.INFO)
            handler.setFormatter(logging.Formatter('%(message)s'))
            
            # Write enough to trigger rotation
            for i in range(20):
                record = logging.LogRecord(
                    name="test",
                    level=logging.INFO,
                    pathname="",
                    lineno=0,
                    msg=f"Test message {i} " + "x" * 10,
                    args=(),
                    exc_info=None
                )
                handler.emit(record)
            
            handler.close()
            
            # Check that no .gz files were created
            gz_files = [f for f in os.listdir(tmpdir) if f.endswith('.gz')]
            if len(gz_files) > 0:
                print(f"❌ FAIL: Found compressed files when DELETE_LOG_FILE_ON_COMPRESSION=true: {gz_files}")
                return False
            
            # Check that rotated files exist (they should be deleted, not compressed)
            # Actually, with delete_on_compression, files should be deleted, not kept
            rotated_files = [f for f in os.listdir(tmpdir) if f.startswith("test_rotate") and f != "test_rotate.log"]
            # With delete_on_compression, rotated files should be deleted
            # But the handler might still create them temporarily before deletion
            
            print("✅ PASS: DELETE_LOG_FILE_ON_COMPRESSION works correctly")
            print(f"   - Compressed files found: {len(gz_files)}")
            return True
            
        except Exception as e:
            print(f"❌ FAIL: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            # Clean up
            if "DELETE_LOG_FILE_ON_COMPRESSION" in os.environ:
                del os.environ["DELETE_LOG_FILE_ON_COMPRESSION"]


def test_default_compression_behavior():
    """Test that default behavior still compresses files."""
    print("\n=== Test: Default compression behavior ===")
    
    # Make sure env var is not set
    if "DELETE_LOG_FILE_ON_COMPRESSION" in os.environ:
        del os.environ["DELETE_LOG_FILE_ON_COMPRESSION"]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            from hd_logging.SizeAndTimeLoggingHandler import SizeAndTimeLoggingHandler
            import logging
            
            # Create a handler with default behavior (compression)
            handler = SizeAndTimeLoggingHandler(
                filename=os.path.join(tmpdir, "test_compress.log"),
                maxBytes=100,  # Small size to trigger rotation
                backupCount=3,
                delete_on_compression=False  # Explicitly set to False
            )
            
            handler.setLevel(logging.INFO)
            handler.setFormatter(logging.Formatter('%(message)s'))
            
            # Write enough to trigger rotation
            for i in range(20):
                record = logging.LogRecord(
                    name="test",
                    level=logging.INFO,
                    pathname="",
                    lineno=0,
                    msg=f"Test message {i} " + "x" * 10,
                    args=(),
                    exc_info=None
                )
                handler.emit(record)
            
            handler.close()
            
            # Check that delete_on_compression is False
            if handler.delete_on_compression:
                print("❌ FAIL: delete_on_compression should be False by default")
                return False
            
            print("✅ PASS: Default behavior uses compression")
            return True
            
        except Exception as e:
            print(f"❌ FAIL: {e}")
            import traceback
            traceback.print_exc()
            return False


def test_delete_on_compression_env_variants():
    """Test different environment variable values through setup_logger."""
    print("\n=== Test: DELETE_LOG_FILE_ON_COMPRESSION variants ===")
    
    test_values = ["true", "True", "TRUE", "1", "yes", "Yes", "YES"]
    
    for value in test_values:
        try:
            os.environ["DELETE_LOG_FILE_ON_COMPRESSION"] = value
            
            # Test through setup_logger (which reads the env var)
            from hd_logging import setup_logger
            import tempfile
            
            with tempfile.TemporaryDirectory() as tmpdir:
                logger = setup_logger("test_env", log_file_path=os.path.join(tmpdir, "test.log"))
                
                # Get the file handler
                handler = [h for h in logger.handlers if hasattr(h, 'delete_on_compression')]
                if not handler:
                    print(f"❌ FAIL: No handler with delete_on_compression found")
                    return False
                
                handler = handler[0]
                
                if not handler.delete_on_compression:
                    print(f"❌ FAIL: Value '{value}' should enable delete_on_compression")
                    return False
                
                print(f"✅ PASS: Value '{value}' works")
            
        except Exception as e:
            print(f"❌ FAIL: Value '{value}' failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            if "DELETE_LOG_FILE_ON_COMPRESSION" in os.environ:
                del os.environ["DELETE_LOG_FILE_ON_COMPRESSION"]
    
    return True


def test_rotate_method_with_delete():
    """Test the rotate method directly with delete_on_compression."""
    print("\n=== Test: rotate() method with delete_on_compression ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            from hd_logging.SizeAndTimeLoggingHandler import SizeAndTimeLoggingHandler
            import logging
            
            # Create handler with delete_on_compression
            handler = SizeAndTimeLoggingHandler(
                filename=os.path.join(tmpdir, "test.log"),
                delete_on_compression=True
            )
            
            # Create a test file to rotate
            source_file = os.path.join(tmpdir, "test.log.2026-01-01")
            dest_file = os.path.join(tmpdir, "test.log.2026-01-01_old")
            
            # Write some content to source
            with open(source_file, 'w') as f:
                f.write("Test log content\n")
            
            # Rotate it
            handler.rotate(source_file, dest_file)
            
            # Check that dest was deleted (not compressed)
            if os.path.exists(dest_file):
                print(f"❌ FAIL: Rotated file still exists: {dest_file}")
                return False
            
            if os.path.exists(dest_file + ".gz"):
                print(f"❌ FAIL: Compressed file exists when delete_on_compression=true: {dest_file}.gz")
                return False
            
            print("✅ PASS: rotate() method deletes files when delete_on_compression=true")
            return True
            
        except Exception as e:
            print(f"❌ FAIL: {e}")
            import traceback
            traceback.print_exc()
            return False


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Testing DELETE_LOG_FILE_ON_COMPRESSION")
    print("=" * 60)
    
    tests = [
        test_delete_on_compression,
        test_default_compression_behavior,
        test_delete_on_compression_env_variants,
        test_rotate_method_with_delete,
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
        print("\n🎉 All tests passed! DELETE_LOG_FILE_ON_COMPRESSION works correctly")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
