import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from colorama import Fore, Style, init

from utils.file_utils import FILES_DIR

init(autoreset=True)


def lint_csv(filepath: Path) -> list[str]:
    """
    Lint a CSV file for common issues:
    - Empty file (no header row)
    - Empty header row
    - Inconsistent number of columns across rows
    Args:
        filepath: Path to the CSV file to lint
    Returns:
        list[str]: List of error messages found in the file, empty if no issues
    """

    errors = []
    try:
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            try:
                header = next(reader)
            except StopIteration:
                errors.append("File is empty (no header row)")
                return errors

            if not header:
                errors.append("Header row is empty")
                return errors

            expected_cols = len(header)

            for line_num, row in enumerate(reader, start=2):
                if all(cell.strip() == "" for cell in row):
                    errors.append(f"Line {line_num}: empty row")
                    continue
                if len(row) != expected_cols:
                    errors.append(
                        f"Line {line_num}: expected {expected_cols} columns, "
                        f"got {len(row)} — {row}"
                    )
    except csv.Error as e:
        errors.append(f"CSV parse error: {e}")
    except UnicodeDecodeError as e:
        errors.append(f"Encoding error: {e}")

    return errors


def main():
    # When specific files are passed as CLI args (e.g. from CI changed-files),
    # lint only those. Otherwise fall back to scanning the whole files/ directory.
    if sys.argv[1:]:
        # Resolve to absolute paths so file operations work regardless of cwd
        csv_files = sorted(
            Path(p).resolve() for p in sys.argv[1:] if p.endswith(".csv")
        )
    else:
        csv_files = sorted(FILES_DIR.glob("*.csv"))

    if not csv_files:
        print(f"No CSV files found in {FILES_DIR}")
        sys.exit(0)

    total_errors = 0
    for filepath in csv_files:
        errors = lint_csv(filepath)
        if errors:
            print(f"{Fore.RED}{Style.BRIGHT}[FAIL]{Style.RESET_ALL} {filepath.name}")
            for err in errors:
                print(f"       {Fore.YELLOW}{err}{Style.RESET_ALL}")
            total_errors += len(errors)
        else:
            print(f"{Fore.GREEN}{Style.BRIGHT}[ OK ]{Style.RESET_ALL} {filepath.name}")

    print()
    if total_errors:
        print(
            f"{Fore.RED}{Style.BRIGHT}{total_errors} error(s) found across {len(csv_files)} file(s).{Style.RESET_ALL}"
        )
        sys.exit(1)
    else:
        print(
            f"{Fore.GREEN}{Style.BRIGHT}All {len(csv_files)} CSV file(s) passed.{Style.RESET_ALL}"
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
