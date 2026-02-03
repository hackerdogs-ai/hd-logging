# hd_logging: requested fixes and changes (for hd_logging developer)

This document lists all fixes and changes requested for the **hd_logging** package so it works reliably in containers (e.g. Celery workers under Docker) and supports forcing logs to stdout. Pass this to the hd_logging developer.

---

## 1. Log rotation: avoid `FileNotFoundError` when multiple processes share the same log file

**Problem:** When multiple Celery workers (or any multiprocess setup) use the same log file path, one process can rotate the file (rename it) while another is about to rotate. The second process then tries to rename a file that no longer exists → **FileNotFoundError** and log rotation errors in stderr.

**Required change:** In the rotating file handler (e.g. `SizeAndTimeLoggingHandler` or whatever does the actual rename/rotation):

1. **In `rotate()` (or the method that renames `source` → `dest`):**
   - **Before** calling `os.rename(source, dest)`, check `if not os.path.exists(source): return`. If the source file is already gone (another process rotated it), exit without error.
   - Wrap the rename/compress logic in **`try/except FileNotFoundError`**: if `FileNotFoundError` is raised (e.g. race between existence check and rename), **catch it and return/skip** (do not re-raise). Optionally catch other exceptions, log a short message to stderr, and either skip or re-raise per your policy.

2. **In `shouldRollover()` (if you use stream-based size checks):**
   - If `self.stream.seek()` / `self.stream.tell()` raise **OSError, IOError, or ValueError** (e.g. file was rotated/deleted by another process), **close the stream**, call **`self.stream = self._open()`** to reopen, then retry the size check. Do not let that exception propagate.
   - On any other exception in `shouldRollover()`, **return 0** (do not rollover) and optionally print a short message to stderr, so a bad state does not cause repeated crashes.

3. **In `emit()`:**
   - Wrap the call to the parent **`emit()`** (or the code that writes the record) in **try/except Exception**. On exception, **print a short message to stderr** (e.g. handler name and exception type/message) and **do not re-raise**, so a single logging failure does not crash the process.

**Reference (same behavior, different codebase):** In this repo, `shared/SizeAndTimeLoggingHandler.py` implements the above pattern (see `rotate()`, `shouldRollover()`, and `emit()` there). You can mirror that logic in hd_logging’s handler.

---

## 2. New behavior: force all logs to stdout when `FORCE_LOGS_TO_STDOUT=true`

**Goal:** In containers, logs are usually collected from **stdout/stderr** (e.g. `docker logs`, Kubernetes). We want an option to send logs to **stdout** (INFO/DEBUG) and **stderr** (WARNING/ERROR/CRITICAL), with **no file handler**, so there are no log files and no rotation inside the container, and errors go to stderr as expected.

**Required change:** In **`setup_logger()`** (or wherever the root/logger handlers are configured):

1. At the **start** of the function, read the environment variable:
   - `force_stdout = os.environ.get("FORCE_LOGS_TO_STDOUT", "").strip().lower() in ("true", "1", "yes")`

2. **If `force_stdout` is True:**
   - Configure the logger with **only** stream handlers (no file handler; do not use `log_file_path` for writing):
     - **stdout:** attach a **`logging.StreamHandler(sys.stdout)`** for **INFO and DEBUG** (and any lower level). Use your usual formatter and level.
     - **stderr:** attach a **`logging.StreamHandler(sys.stderr)`** for **WARNING, ERROR, and CRITICAL**, so errors go to stderr (conventional and expected by Docker/Kubernetes and log aggregators).
   - So when `FORCE_LOGS_TO_STDOUT=true`, the `log_file_path` argument is effectively ignored for output; normal logs go to stdout and errors to stderr.

3. **If `force_stdout` is False (or unset):**
   - Keep **current behavior** (e.g. file handler with `log_file_path`, rotation, etc.).

**Usage:** In Docker/Kubernetes, set `FORCE_LOGS_TO_STDOUT=true` in the container environment so logs go to stdout/stderr and are captured by the platform (errors on stderr).

---

## Summary checklist for hd_logging

| # | Item | Where |
|---|------|--------|
| 1 | In rotate(): check `os.path.exists(source)` before rename; on missing source, return. | Rotating file handler (e.g. SizeAndTimeLoggingHandler) |
| 2 | In rotate(): catch `FileNotFoundError` and skip (no raise). | Same |
| 3 | In shouldRollover(): on OSError/IOError/ValueError from stream, reopen stream and retry; on other exceptions return 0. | Same |
| 4 | In emit(): wrap parent emit() in try/except; on exception, print to stderr and do not re-raise. | Same |
| 5 | In setup_logger(): if env `FORCE_LOGS_TO_STDOUT` is true/1/yes, use only stream handlers: stdout for INFO/DEBUG, stderr for WARNING/ERROR/CRITICAL; no file handler. | setup_logger() |

---

## Version and consumption

- After implementing these changes, **bump the package version** (e.g. to **1.0.5**).
- This repo will update requirements (e.g. `hd-logging==1.0.5`) in the relevant `*requirements*.txt` files and set `FORCE_LOGS_TO_STDOUT=true` in containers where we want stdout-only logging.

No API changes are required: existing callers keep using `setup_logger(name, log_file_path="...")`; only the env var and the internal behavior of the handler and setup_logger change.
