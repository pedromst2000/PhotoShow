import tkinter as tk
import tkinter.font as tkFont
from typing import Any, Dict, Optional, Tuple

from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold
from app.presentation.widgets.helpers.images import load_image


def add_icon_canvas(
    type: str,
    parent: tk.Widget,
    icon_path: str,
    icon_pos: Tuple[int, int],
    icon_size: Tuple[int, int] = (48, 44),
    canvas_size: Tuple[int, int] = (46, 40),
    visible: bool = True,
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
        visible (bool, optional): Whether to display the canvas (True) or keep it hidden (False). Defaults to True.

    Returns the created `tk.Canvas` (with `.image` kept alive).
    """
    canvas_icon: tk.Canvas = tk.Canvas(
        parent, height=canvas_size[1], width=canvas_size[0], highlightthickness=0
    )
    if visible:
        canvas_icon.place(x=icon_pos[0], y=icon_pos[1])
    photo = load_image(icon_path, size=icon_size, canvas=canvas_icon, x=0, y=0)
    # keep attribute for compatibility
    canvas_icon.image = photo
    return canvas_icon


def add_label(
    type: str,
    parent: tk.Widget,
    text: str,
    label_pos: Optional[Tuple[int, int]] = None,
    font: tkFont.Font = None,
    grid: Optional[Tuple[int, int]] = None,
    grid_kwargs: Optional[Dict[str, Any]] = None,
) -> tk.Label:
    """
    Create and place a label on `parent`.

    Args:
        type (str): The type of label (e.g., "email", "password").
        parent (tk.Widget): The parent widget to place the label on.
        text (str): The text to display on the label.
        label_pos (Tuple[int, int]): The (x, y) position to place the label.
        font (tkFont.Font, optional): The font to use for the label. If provided,
            it already contains the font size, so do not pass a separate size.
        grid (Optional[Tuple[int,int]]): If provided, place the label using
            `grid(row, column)` on the parent instead of `place`.
        grid_kwargs (Optional[Dict]): Extra keyword args forwarded to `.grid()`
            (for example `pady`, `sticky`).

    Returns:
        tk.Label: The created label.
    """

    label: tk.Label = tk.Label(
        parent,
        text=text,
        font=font if font else quickSandBold(14),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )

    # Prefer grid placement when requested (keeps existing grid-based layouts).
    if grid is not None:
        row, col = grid
        kwargs = dict(grid_kwargs) if grid_kwargs else {}
        label.grid(row=row, column=col, **kwargs)
    elif label_pos is not None:
        label.place(x=label_pos[0], y=label_pos[1], anchor="w")
    else:
        # Fallback to pack when no placement information provided.
        label.pack()

    return label
