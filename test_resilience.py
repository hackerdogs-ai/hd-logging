#!/usr/bin/env python3
"""
Test resilience of setup_logger - should never crash the program.
"""

import sys
import os
import tempfile
import unittest.mock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def test_setup_logger_never_crashes():
    """Test that setup_logger never raises exceptions."""
    print("\n=== Test: setup_logger never crashes ===")
    
    test_cases = [
        ("Normal case", {}),
        ("Invalid log level", {"LOG_LEVEL": "INVALID_LEVEL"}),
        ("Permission denied directory", {"LOG_FILE": "/root/cannot_write.log"}),
        ("Very long file path", {"LOG_FILE": "/" + "a" * 1000 + "/test.log"}),
    ]
    
    for name, env_vars in test_cases:
        try:
            # Set environment variables
            original_env = {}
            for key, value in env_vars.items():
                original_env[key] = os.environ.get(key)
                os.environ[key] = value
            
            try:
                from hd_logging import setup_logger
                
                # This should never raise an exception
                logger = setup_logger("test_resilient")
                
                # Verify logger is usable
                logger.info("Test message")
                
                print(f"✅ PASS: {name}")
                
            except Exception as e:
                print(f"❌ FAIL: {name} - Exception raised: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                return False
            finally:
                # Restore environment
                for key, value in original_env.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value
                        
        except Exception as e:
            print(f"❌ FAIL: {name} - Setup failed: {e}")
            return False
    
    return True


def test_setup_logger_with_mocked_failures():
    """Test setup_logger with mocked failures."""
    print("\n=== Test: setup_logger with mocked failures ===")
    
    try:
        from hd_logging import setup_logger
        
        # Test 1: Mock os.makedirs to fail
        with unittest.mock.patch('os.makedirs', side_effect=PermissionError("Permission denied")):
            logger = setup_logger("test_mock1")
            logger.info("Should work despite makedirs failure")
            print("✅ PASS: Handles makedirs failure")
        
        # Test 2: Mock handler creation to fail
        with unittest.mock.patch('hd_logging.SizeAndTimeLoggingHandler.SizeAndTimeLoggingHandler', side_effect=OSError("Cannot create handler")):
            logger = setup_logger("test_mock2")
            logger.info("Should work despite handler creation failure")
            print("✅ PASS: Handles handler creation failure")
        
        # Test 3: Mock formatter creation to fail
        with unittest.mock.patch('colorlog.ColoredFormatter', side_effect=Exception("Formatter failed")):
            logger = setup_logger("test_mock3")
            logger.info("Should work despite formatter failure")
            print("✅ PASS: Handles formatter creation failure")
        
        # Test 4: Mock getattr to fail
        with unittest.mock.patch('builtins.getattr', side_effect=AttributeError("Attribute error")):
            logger = setup_logger("test_mock4")
            logger.info("Should work despite getattr failure")
            print("✅ PASS: Handles getattr failure")
        
        return True
        
    except Exception as e:
        print(f"❌ FAIL: Mock test failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_setup_logger_always_returns_logger():
    """Test that setup_logger always returns a usable logger."""
    print("\n=== Test: setup_logger always returns logger ===")
    
    try:
        from hd_logging import setup_logger
        
        # Even with all failures, should return a logger
        with unittest.mock.patch('os.makedirs', side_effect=Exception("Fail")), \
             unittest.mock.patch('hd_logging.SizeAndTimeLoggingHandler.SizeAndTimeLoggingHandler', side_effect=Exception("Fail")), \
             unittest.mock.patch('colorlog.ColoredFormatter', side_effect=Exception("Fail")):
            
            logger = setup_logger("test_always_works")
            
            # Should be a logger instance
            import logging
            assert isinstance(logger, logging.Logger), "Should return a Logger instance"
            
            # Should be able to log
            logger.info("Test message")
            
            print("✅ PASS: Always returns usable logger")
            return True
            
    except Exception as e:
        print(f"❌ FAIL: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all resilience tests."""
    print("=" * 60)
    print("Testing setup_logger Resilience")
    print("=" * 60)
    
    tests = [
        test_setup_logger_never_crashes,
        test_setup_logger_with_mocked_failures,
        test_setup_logger_always_returns_logger,
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
        print("\n🎉 All resilience tests passed! setup_logger is crash-proof.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
