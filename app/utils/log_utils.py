import logging
import os
from datetime import datetime
from inspect import currentframe, getframeinfo
from typing import Optional

from colorama import Fore, Style, init

# Auto-reset colours after each print so callers never forget to reset.
init(autoreset=True)

# Create a logger for the application
logger = logging.getLogger("photoshow")

# Set logger level for debugging (console output only, no file logs)
logger.setLevel(logging.DEBUG)


def _get_caller_info() -> tuple[str, int, str]:
    """
    Get caller's filename, line number, and function name.

    Returns:
        tuple[str, int, str]: (filename, line number, function name)
    """
    frame = currentframe()
    try:
        # Skip: _get_caller_info -> log_* -> caller
        if frame is None or frame.f_back is None or frame.f_back.f_back is None:
            return "<unknown>", 0, "<unknown>"
        caller_frame = frame.f_back.f_back
        info = getframeinfo(caller_frame)
        filename = os.path.basename(info.filename)
        return filename, info.lineno, caller_frame.f_code.co_name
    finally:
        del frame


def _format_timestamp() -> str:
    """Return current time in HH:MM:SS format.

    Returns:
        str: Current time in HH:MM:SS format.
    """
    return datetime.now().strftime("%H:%M:%S")


# =====================================================================
#  Logging for Startup and General Issues
# =====================================================================


def log_check(msg: str) -> None:
    """Yellow — checking / in-progress step.

    Args:
        msg: Short, human-readable description of what is being checked.
    """
    ts = _format_timestamp()
    filename, lineno, funcname = _get_caller_info()
    location = f"{filename}:{lineno} in {funcname}"
    output = f"{ts} | [CHECK] {msg} ({location})"
    print(f"{Fore.YELLOW}{output}{Style.RESET_ALL}")
    logger.info(output)


def log_success(msg: str) -> None:
    """Green — step completed successfully.

    Args:
        msg: Short, human-readable description of what succeeded.
    """
    ts = _format_timestamp()
    filename, lineno, funcname = _get_caller_info()
    location = f"{filename}:{lineno} in {funcname}"
    output = f"{ts} | [SUCCESS] {msg} ({location})"
    print(f"{Fore.GREEN}{output}{Style.RESET_ALL}")
    logger.info(output)


def log_issue(
    msg: str, exc: Optional[Exception] = None, path: Optional[str] = None
) -> None:
    """
    Red — something went wrong.

    Args:
        msg: Short, human-readable description of what failed.
        exc: Optional exception — prints the type and message (no noisy traceback).
        path: Optional file/resource path — resolved to an absolute path so the
           developer can click straight to the file.

    """
    ts = _format_timestamp()
    filename, lineno, funcname = _get_caller_info()
    location = f"{filename}:{lineno} in {funcname}"

    parts = [msg]

    if path:
        abs_path = os.path.abspath(path)
        parts.append(f"Path → {abs_path}")

    if exc:
        parts.append(f"Exception → {type(exc).__name__}: {exc}")

    output = f"{ts} | [ISSUE] {' | '.join(parts)} ({location})"
    print(f"{Fore.RED}{output}{Style.RESET_ALL}")
    logger.error(output, exc_info=exc)


# =====================================================================
#  Logging for Backend Operations
# =====================================================================


def log_operation(
    operation: str, status: str, details: str = "", user_id: Optional[int] = None
) -> None:
    """
    Log a backend operation (service/controller/model action).
    Prints colored output to console with timestamp and source location.

    Args:
        operation: Name of the operation (e.g., "user.change_role", "category.add")
        status: Status of operation ('success', 'failed', 'validation_error')
        details: Optional additional context
        user_id: Optional user performing the action
    """
    ts = _format_timestamp()
    filename, lineno, funcname = _get_caller_info()
    location = f"{filename}:{lineno} in {funcname}"

    user_info = f" | user_id={user_id}" if user_id else ""
    full_msg = f"Operation: {operation} | Status: {status}{user_info}"
    if details:
        full_msg += f" | Details: {details}"

    # Determine color and log level based on status
    if status == "success":
        color = Fore.GREEN
        tag = "[SUCCESS]"
        log_fn = logger.info
    elif status == "validation_error":
        color = Fore.YELLOW
        tag = "[VALIDATION]"
        log_fn = logger.warning
    else:  # failed
        color = Fore.RED
        tag = "[FAILED]"
        log_fn = logger.error

    output = f"{ts} | {tag} {full_msg} ({location})"
    # Print colored output to console
    print(f"{color}{output}{Style.RESET_ALL}")
    # Log to logger
    log_fn(output)


def log_exception(
    operation: str,
    exc: Exception,
    user_id: Optional[int] = None,
    context: Optional[dict] = None,
) -> None:
    """
    Log an exception with context. Used internally, errors hidden from users.
    Prints colored output to console with timestamp, source location, and exception details.

    Args:
        operation: Name of the operation (e.g., "user.change_role")
        exc: The exception that occurred
        user_id: Optional user performing the action
        context: Optional dict with additional context
    """
    ts = _format_timestamp()
    filename, lineno, funcname = _get_caller_info()
    location = f"{filename}:{lineno} in {funcname}"

    user_info = f" | user_id={user_id}" if user_id else ""
    context_str = f" | context={context}" if context else ""
    exc_details = (
        f"Exception: {operation}{user_info}{context_str} | {type(exc).__name__}: {exc}"
    )

    output = f"{ts} | [EXCEPTION] {exc_details} ({location})"
    # Print colored error to console
    print(f"{Fore.RED}{output}{Style.RESET_ALL}")
    # Log with full traceback
    logger.error(output, exc_info=exc)
