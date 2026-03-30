import io
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

# Add repo root to path for direct script execution
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import isort
from colorama import Fore, Style, init

from app.utils.file_utils import ROOT, has_imports, iter_python_files

init(autoreset=True)

# Determine the repo root (one level above app/)
REPO_ROOT = ROOT.parent


def main():
    """
    Check that all Python files have properly sorted imports according to isort.
    """

    # When specific files are passed as CLI args (e.g. from CI changed-files),
    # lint only those. Otherwise fall back to scanning the whole project.
    if sys.argv[1:]:
        # Resolve to absolute paths so relative_to(REPO_ROOT) works regardless of cwd
        py_files = [Path(p).resolve() for p in sys.argv[1:] if p.endswith(".py")]
    else:
        py_files = list(iter_python_files(ROOT))
    if not py_files:
        print("No Python files found.")
        sys.exit(0)

    issues = []
    for filepath in py_files:
        if not has_imports(filepath):
            continue
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            ok = isort.check_file(str(filepath), show_diff=False)
        rel = filepath.relative_to(REPO_ROOT)
        if ok:
            print(f"{Fore.GREEN}{Style.BRIGHT}[ OK ]{Style.RESET_ALL} {rel}")
        else:
            print(f"{Fore.RED}{Style.BRIGHT}[FAIL]{Style.RESET_ALL} {rel}")
            issues.append(rel)

    print()
    if issues:
        print(
            f"{Fore.RED}{Style.BRIGHT}{len(issues)} file(s) have import order issues:{Style.RESET_ALL}"
        )
        for f in issues:
            print(f"  {Fore.YELLOW}→ {f}{Style.RESET_ALL}")
        print()
        print(
            f"{Fore.CYAN}Run {Style.BRIGHT}python scripts/format_imports.py"
            f"{Style.RESET_ALL}{Fore.CYAN} to auto-fix.{Style.RESET_ALL}"
        )
        sys.exit(1)
    else:
        print(
            f"{Fore.GREEN}{Style.BRIGHT}[OK] All imports are correctly sorted!{Style.RESET_ALL}"
        )


if __name__ == "__main__":
    main()  # This file is meant to be run as a script, not imported as a module.
