# Bug Fixes Applied to hd-logging

## Issues Fixed

### 1. Type Safety Bug in `_sanitize_extra` (CRITICAL)

**Location**: `src/hd_logging/logger.py`, line 52-66

**Problem**: 
- Original code assumed `extra` was always a dict
- If `extra` was a non-dict type (e.g., string, list), `extra.copy()` would raise `AttributeError`
- The check `if not extra:` would incorrectly handle falsy values like `0` or `False`

**Fix**:
- Added explicit `isinstance(extra, dict)` check
- Handle `None` explicitly
- Return non-dict types as-is (let logging handle the error)
- Only process dict types

**Before**:
```python
def _sanitize_extra(extra):
    if not extra:
        return extra
    # Would fail if extra is not a dict
    sanitized = extra.copy()
```

**After**:
```python
def _sanitize_extra(extra):
    if extra is None:
        return None
    if not isinstance(extra, dict):
        return extra  # Let logging handle non-dict types
    if not extra:  # Empty dict
        return extra
    # Safe to call .copy() now
```

### 2. Reserved LogRecord Keys Not Excluded in Formatter

**Location**: `src/hd_logging/otlp_formatter.py`, line 73-82

**Problem**:
- `_extract_attributes` iterates through `dir(record)` to extract all attributes
- `record.message` is a LogRecord property that appears in `dir(record)`
- `record.asctime` is also a reserved property
- These were not in `standard_attrs`, so they could be extracted incorrectly

**Fix**:
- Added `'message'` and `'asctime'` to `standard_attrs` set
- Prevents these reserved properties from being extracted as attributes

**Before**:
```python
standard_attrs = {
    'args', 'created', 'exc_info', ..., 'getMessage', 'otlp_attributes'
    # Missing 'message' and 'asctime'
}
```

**After**:
```python
standard_attrs = {
    'args', 'created', 'exc_info', ..., 'getMessage', 'otlp_attributes',
    'message',  # Reserved LogRecord property
    'asctime'   # Reserved LogRecord property
}
```

### 3. Extra Dict Sanitization Not Applied

**Location**: `src/hd_logging/logger.py`, line 50-103

**Problem**:
- No sanitization of `extra` dict before it reaches `makeRecord`
- If code accidentally passes `"message"` or `"asctime"` in `extra`, Python's logging raises `KeyError`

**Fix**:
- Added `_sanitize_extra` function to rename reserved keys
- Wrapped all logger methods (`warning`, `error`, `info`, `debug`, `critical`, `log`) to sanitize `extra`
- Applied early in `setup_logger` (before handler setup) to ensure all loggers are protected
- Prevents duplicate wrapping with `_extra_sanitized` flag

**Implementation**:
- `"message"` → `"log_message"`
- `"asctime"` → `"log_asctime"`
- `"filename"` → `"log_filename"` (added during validation testing)
- Applied transparently - no API changes required

## Testing Recommendations

1. **Test with reserved keys**:
   ```python
   from hd_logging import setup_logger
   logger = setup_logger('test', 'logs/test.log')
   
   # Should NOT raise KeyError
   logger.warning('test', extra={'message': 'should be sanitized'})
   logger.error('test', extra={'asctime': '2024-01-01'})
   ```

2. **Test with None and empty dict**:
   ```python
   logger.info('test', extra=None)  # Should work
   logger.info('test', extra={})    # Should work
   ```

3. **Test with non-dict types** (should pass through, logging will handle error):
   ```python
   logger.info('test', extra='not a dict')  # Should not crash our code
   ```

4. **Test backward compatibility**:
   ```python
   # Normal usage should work exactly as before
   logger.warning('test', extra={'bucket_name': 'test', 'blob_name': 'test'})
   ```

## Files Modified

1. `src/hd_logging/logger.py` - Added sanitization wrapper
2. `src/hd_logging/otlp_formatter.py` - Added reserved keys to exclusion list

## Backward Compatibility

✅ **Fully backward compatible** - No API changes
✅ **Transparent fix** - Existing code works without modification
✅ **Defensive** - Handles edge cases (None, non-dict types, etc.)

