# ══════════════════════════════════════════════════════════════════════════════
#  Font Specification Functions (work with both Tkinter and TTK)
# ══════════════════════════════════════════════════════════════════════════════
#
# These functions return font tuples ("FontName", size, "weight") that work with:
# - Regular Tkinter widgets: font=quickSandBold(12)
# - TTK styles: style.configure("Style", font=quickSandBold(12))
# - Font objects: tkFont.Font(family=quickSandBold(12)[0], size=quickSandBold(12)[1])
#
# Requires: Quicksand fonts installed on system (installed via font_installer.py at startup).


def quickSandRegular(size: int) -> tuple:
    """
    Get QuickSand Regular font specification.

    Args:
        size (int): The font size in points.
    Returns:
        tuple: Font specification ("Quicksand", size, "normal").
    """
    return ("Quicksand", size, "normal")


def quickSandBold(size: int) -> tuple:
    """
    Get QuickSand Bold font specification.

    Args:
        size (int): The font size in points.
    Returns:
        tuple: Font specification ("Quicksand", size, "bold").
    """
    return ("Quicksand", size, "bold")


def quickSandLight(size: int) -> tuple:
    """
    Get QuickSand Light font specification.

    Args:
        size (int): The font size in points.
    Returns:
        tuple: Font specification ("Quicksand", size, "normal").
    """
    return ("Quicksand", size, "normal")


def quickSandMedium(size: int) -> tuple:
    """
    Get QuickSand Medium font specification.

    Args:
        size (int): The font size in points.
    Returns:
        tuple: Font specification ("Quicksand", size, "normal").
    """
    return ("Quicksand", size, "normal")


def quickSandSemiBold(size: int) -> tuple:
    """
    Get QuickSand SemiBold font specification.

    Args:
        size (int): The font size in points.
    Returns:
        tuple: Font specification ("Quicksand", size, "bold").
    """
    return ("Quicksand", size, "bold")


def quickSandRegularUnderline(size: int) -> tuple:
    """
    Get QuickSand Regular font specification with underline.

    Args:
        size (int): The font size in points.
    Returns:
        tuple: Font specification ("Quicksand", size, "normal", "underline").
    """
    return ("Quicksand", size, "normal", "underline")


def quickSandBoldUnderline(size: int) -> tuple:
    """
    Get QuickSand Bold font specification with underline.

    Args:
        size (int): The font size in points.
    Returns:
        tuple: Font specification ("Quicksand", size, "bold", "underline").
    """
    return ("Quicksand", size, "bold", "underline")
