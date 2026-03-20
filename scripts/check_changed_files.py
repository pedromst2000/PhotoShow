import subprocess
import sys
from pathlib import Path

from colorama import Fore, Style, init

init(autoreset=True)

ROOT = Path(__file__).parent.parent

"""
Run all code-quality checks on locally changed files (git diff vs HEAD).
If no changed files are detected, the script exits cleanly.
"""


def get_changed_files() -> list[Path]:
    """
    Return all files changed vs HEAD (staged + unstaged + untracked, added/copied/modified only).

    Returns:
        list[Path]: Absolute paths of changed files that exist on disk.
    """
    unstaged = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=ACM", "HEAD"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    staged = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=ACM", "--cached"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    # Also include new untracked files (not yet git-added) so newly created
    # files are checked even before their first commit.
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    names = (
        set(unstaged.stdout.splitlines())
        | set(staged.stdout.splitlines())
        | set(untracked.stdout.splitlines())
    )
    return [ROOT / f for f in sorted(names) if f and (ROOT / f).exists()]


def _header(title: str) -> None:
    print(
        f"\n{Fore.CYAN}{Style.BRIGHT}── {title} {'─' * (50 - len(title))}{Style.RESET_ALL}"
    )


def _run(label: str, cmd: list[str], check: bool = True) -> int:
    """Run a subprocess command, print its label, and return the exit code."""
    _header(label)
    result = subprocess.run(cmd, cwd=ROOT)
    return result.returncode


def main():
    fix = "--fix" in sys.argv

    files = get_changed_files()

    if not files:
        print(f"{Fore.YELLOW}No changed files detected (vs HEAD).{Style.RESET_ALL}")
        sys.exit(0)

    py_files = [str(f) for f in files if f.suffix == ".py"]
    csv_files = [str(f) for f in files if f.suffix == ".csv"]
    yaml_files = [str(f) for f in files if f.suffix in (".yml", ".yaml")]

    print(f"{Fore.CYAN}{Style.BRIGHT}Changed files:{Style.RESET_ALL}")
    for f in files:
        print(f"  {f.relative_to(ROOT)}")

    exit_code = 0

    # ── Python ───────────────────────────────────────────────────────────────
    if py_files:
        rc = _run("flake8 (lint)", ["python", "-m", "flake8"] + py_files)
        if rc != 0:
            exit_code = 1

        if fix:
            _run("black (format)", ["python", "-m", "black"] + py_files)
            _run("isort (format)", ["python", "scripts/format_imports.py"] + py_files)
        else:
            rc = _run("black (check)", ["python", "-m", "black", "--check"] + py_files)
            if rc != 0:
                exit_code = 1

            rc = _run(
                "isort (check)", ["python", "scripts/check_imports.py"] + py_files
            )
            if rc != 0:
                exit_code = 1

    # ── CSV ──────────────────────────────────────────────────────────────────
    if csv_files:
        if fix:
            _run("format_csv (format)", ["python", "scripts/format_csv.py"] + csv_files)
        else:
            rc = _run("lint_csv (check)", ["python", "scripts/lint_csv.py"] + csv_files)
            if rc != 0:
                exit_code = 1

    # ── YAML ─────────────────────────────────────────────────────────────────
    if yaml_files:
        rc = _run("yamllint (lint)", ["python", "-m", "yamllint"] + yaml_files)
        if rc != 0:
            exit_code = 1

    # ── Summary ──────────────────────────────────────────────────────────────
    print()
    if exit_code == 0:
        print(f"{Fore.GREEN}{Style.BRIGHT}✔ All checks passed!{Style.RESET_ALL}")
    else:
        print(
            f"{Fore.RED}{Style.BRIGHT}✘ Some checks failed. "
            f"Run with --fix to auto-format style issues (black/isort/format_csv), then review and commit. "
            f"Non-style problems must be fixed manually.{Style.RESET_ALL}"
        )

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
