import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from colorama import Fore, Style, init

from utils.file_utils import FILES_DIR

init(autoreset=True)


# Settings for standard CSV formatting
def format_csv_file(filepath: Path) -> bool:
    """
    Reads a CSV file and writes it back with:
      - Consistent quoting (minimal)
      - No trailing spaces
      - No empty rows
      - Consistent delimiter (comma)

    Parameters:
        filepath: Path to the CSV file to format
    Returns:
        bool: True if the file was changed, False if it was already properly formatted
    """
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = list(csv.reader(f))
    if not reader:
        return False
    # Remove empty rows
    rows = [row for row in reader if any(cell.strip() for cell in row)]
    # Strip whitespace from each cell
    rows = [[cell.strip() for cell in row] for row in rows]
    # Only rewrite if changed
    with open(filepath, newline="", encoding="utf-8") as f:
        original = f.read()
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
        writer.writerows(rows)
    with open(filepath, newline="", encoding="utf-8") as f:
        new = f.read()
    return original != new


def main():
    # When specific files are passed as CLI args (e.g. from CI changed-files),
    # format only those. Otherwise fall back to scanning the whole files/ directory.
    if sys.argv[1:]:
        # Resolve to absolute paths so file operations work regardless of cwd
        csv_files = sorted(
            Path(p).resolve() for p in sys.argv[1:] if p.endswith(".csv")
        )
    else:
        csv_files = sorted(FILES_DIR.glob("*.csv"))
    changed = 0
    for filepath in csv_files:
        if format_csv_file(filepath):
            print(f"{Fore.GREEN}✔️  Formatted: {filepath.name}{Style.RESET_ALL}")
            changed += 1
        else:
            print(f"{Fore.YELLOW}⏭️  No change: {filepath.name}{Style.RESET_ALL}")
    if changed:
        print(
            f"\n{Fore.GREEN}{Style.BRIGHT}{changed} file(s) formatted.{Style.RESET_ALL}"
        )
    else:
        print(
            f"\n{Fore.YELLOW}{Style.BRIGHT}No files needed formatting.{Style.RESET_ALL}"
        )
    print(f"{Fore.CYAN}{Style.BRIGHT}All done!{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
