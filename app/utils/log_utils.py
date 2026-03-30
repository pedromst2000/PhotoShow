import os

from colorama import Fore, Style, init

# Auto-reset colours after each print so callers never forget to reset.
init(autoreset=True)


def log_check(msg: str) -> None:
    """Yellow — checking / in-progress step.

    Args:
        msg: Short, human-readable description of what is being checked.
    """
    print(f"{Fore.YELLOW}[CHECK] {msg}{Style.RESET_ALL}")


def log_success(msg: str) -> None:
    """Green — step completed successfully.

    Args:
        msg: Short, human-readable description of what succeeded.
    """
    print(f"{Fore.GREEN}[SUCCESS] {msg}{Style.RESET_ALL}")


def log_issue(msg: str, exc: Exception = None, path: str = None) -> None:
    """
    Red — something went wrong.

    Args:
        msg: Short, human-readable description of what failed.
        exc: Optional exception — prints the type and message (no noisy traceback).
        path: Optional file/resource path — resolved to an absolute path so the
           developer can click straight to the file.

    """
    parts = [msg]

    if path:
        abs_path = os.path.abspath(path)
        parts.append(f"Path → {abs_path}")

    if exc:
        parts.append(f"Reason → {type(exc).__name__}: {exc}")

    print(f"{Fore.RED}[ISSUE] {' | '.join(parts)}{Style.RESET_ALL}")
