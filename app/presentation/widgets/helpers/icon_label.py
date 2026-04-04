import tkinter as tk
from typing import Tuple

from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold
from app.presentation.widgets.helpers.window import load_image


def add_icon_canvas(
    type: str,
    parent: tk.Widget,
    icon_path: str,
    icon_pos: Tuple[int, int],
    icon_size: Tuple[int, int] = (48, 44),
    canvas_size: Tuple[int, int] = (46, 40),
) -> tk.Canvas:
    """
    Create and place an icon canvas on `parent`.

    Args:
        type (str): The type of icon (e.g., "email", "password").
        parent (tk.Widget): The parent widget to place the canvas on.
        icon_path (str): The file path to the icon image.
        icon_pos (Tuple[int, int]): The (x, y) position to place the canvas.
        icon_size (Tuple[int, int], optional): The size to resize the icon to. Defaults to (48, 44).
        canvas_size (Tuple[int, int], optional): The size of the canvas. Defaults to (46, 40).

    Returns the created `tk.Canvas` (with `.image` kept alive).
    """
    canvas_icon: tk.Canvas = tk.Canvas(
        parent, height=canvas_size[1], width=canvas_size[0], highlightthickness=0
    )
    canvas_icon.place(x=icon_pos[0], y=icon_pos[1])
    photo = load_image(icon_path, size=icon_size, canvas=canvas_icon, x=0, y=0)
    # keep attribute for compatibility
    canvas_icon.image = photo
    return canvas_icon


def add_label(
    type: str,
    parent: tk.Widget,
    text: str,
    label_pos: Tuple[int, int],
    font_size: int = 14,
) -> tk.Label:
    """
    Create and place a label on `parent`.

    Args:
        type (str): The type of label (e.g., "email", "password").
        parent (tk.Widget): The parent widget to place the label on.
        text (str): The text to display on the label.
        label_pos (Tuple[int, int]): The (x, y) position to place the label.
        font_size (int, optional): The font size of the label text. Defaults to 14.

    Returns:
        tk.Label: The created label.
    """

    label: tk.Label = tk.Label(
        parent,
        text=text,
        font=quickSandBold(font_size),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )
    label.place(x=label_pos[0], y=label_pos[1], anchor="w")
    return label
