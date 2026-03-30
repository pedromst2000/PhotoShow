import tkinter.font as tkFont


def quickSandRegular(size: int) -> tkFont:
    """
    This function is used to set the font family to QuickSand Regular.

    Args:
        size (int): The size of the font.
    Returns:
        tkFont: The font object with QuickSand Regular style.

    """

    return tkFont.Font(family="QuickSand", size=size, weight="normal")


def quickSandBold(size: int) -> tkFont:
    """
    This function is used to set the font family to QuickSand Bold.

    Args:
        size (int): The size of the font.
    Returns:
        tkFont: The font object with QuickSand Bold style.
    """

    return tkFont.Font(family="QuickSand", size=size, weight="bold")


def quickSandRegularUnderline(size: int) -> tkFont:
    """
    This function is used to set the font family to QuickSand Regular Underline.

    Args:
        size (int): The size of the font.
    Returns:
        tkFont: The font object with QuickSand Regular Underline style.
    """

    return tkFont.Font(family="QuickSand", size=size, weight="normal", underline=1)


def quickSandBoldUnderline(size: int) -> tkFont:
    """
    This function is used to set the font family to QuickSand Bold Underline.

    Args:
        size (int): The size of the font.
    Returns:
        tkFont: The font object with QuickSand Bold Underline style.
    """

    return tkFont.Font(family="QuickSand", size=size, weight="bold", underline=1)
