import sys
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
    # When specific files are passed as CLI args (e.g. from CI changed-files),
    # format only those. Otherwise fall back to scanning the whole project.
    if sys.argv[1:]:
        # Resolve to absolute paths so relative_to(REPO_ROOT) works regardless of cwd
        py_files = [Path(p).resolve() for p in sys.argv[1:] if p.endswith(".py")]
    else:
        py_files = list(iter_python_files(ROOT))
    if not py_files:
        print("No Python files found.")
        sys.exit(0)

    changed = 0
    for filepath in py_files:
        if not has_imports(filepath):
            continue
        was_changed = isort.file(str(filepath))
        rel = filepath.relative_to(REPO_ROOT)
        if was_changed:
            print(f"{Fore.GREEN}[OK] Fixed:     {rel}{Style.RESET_ALL}")
            changed += 1
        else:
            print(f"{Fore.YELLOW}[SKIP] No change: {rel}{Style.RESET_ALL}")

    print()
    if changed:
        print(
            f"{Fore.GREEN}{Style.BRIGHT}{changed} file(s) had imports fixed.{Style.RESET_ALL}"
        )
    else:
        print(
            f"{Fore.YELLOW}{Style.BRIGHT}No files needed import sorting.{Style.RESET_ALL}"
        )
    print(f"{Fore.CYAN}{Style.BRIGHT}All done!{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
