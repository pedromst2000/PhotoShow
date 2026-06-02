import tkinter as tk
from typing import Optional

from PIL import ImageTk

from app.presentation.widgets.helpers.images import load_image
from app.utils.file_utils import resolve_avatar_path


def build_avatar_canvas(
    parent: tk.Widget,
    *,
    size: int = 64,
    bg: str,
) -> tk.Canvas:
    """Create a square Canvas widget for displaying a user avatar image.

    Args:
        parent: Parent widget that will contain the canvas.
        size: Width and height of the canvas in pixels (default ``64``).
        bg: Background colour matching the surrounding panel.

    Returns:
        tk.Canvas: An empty canvas ready to receive an avatar image via
        :func:`load_avatar_image`.
    """
    return tk.Canvas(
        parent,
        width=size,
        height=size,
        bg=bg,
        highlightthickness=0,
        bd=0,
    )


def load_avatar_image(
    canvas: tk.Canvas,
    avatar_path: Optional[str],
    *,
    size: int = 64,
) -> ImageTk.PhotoImage:
    """Resolve and load an avatar image into *canvas*.

    Clears any previous content on the canvas before drawing.

    The caller **must** keep the returned :class:`~PIL.ImageTk.PhotoImage`
    reference alive (e.g. on the state object) to prevent garbage collection.

    Args:
        canvas: Target canvas widget to draw the avatar on.
        avatar_path: Raw avatar path from the data store (may be ``None`` or a
            legacy-prefixed path); resolved by :func:`~app.utils.file_utils.resolve_avatar_path`.
        size: Width and height of the rendered image in pixels (default ``64``).

    Returns:
        ImageTk.PhotoImage: The loaded image reference that must be retained by
        the caller.
    """
    canvas.delete("all")
    resolved = resolve_avatar_path(avatar_path)
    return load_image(resolved, size=(size, size), canvas=canvas, x=0, y=0)
