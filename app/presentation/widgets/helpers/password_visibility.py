import tkinter as tk

from PIL import Image, ImageTk

from app.presentation.styles.colors import colors
from app.presentation.widgets.helpers.auth_icons import (
    manageVisibility,
    togglePasswordVisibility,
)


def attach_password_visibility(
    parent: tk.Widget,
    input_password: tk.Entry,
    x: int,
    y: int,
    bg_color: str | None = None,
) -> tk.Canvas:
    """
    Create a small canvas used to toggle password visibility and attach
    the necessary bindings to the provided password `Entry`.

    The canvas is not placed immediately; the visibility helpers will
    place it when appropriate.

    Args:
        parent: Parent widget (typically the Toplevel / root window).
        input_password: The password `tk.Entry` to control.
        x: X coordinate where the visibility icon should be placed.
        y: Y coordinate where the visibility icon should be placed.
        bg_color: Optional background color for the canvas. Defaults to
            `colors['primary-50']`.

    Returns:
        The created `tk.Canvas` widget (not guaranteed placed).
    """
    if bg_color is None:
        bg_color = colors["primary-50"]

    canvas_manage = tk.Canvas(
        parent, height=36, width=50, highlightthickness=0, cursor="hand2"
    )
    canvas_manage.config(highlightthickness=0, bd=0, bg=bg_color)

    # Bind key release on the entry to show/hide the icon when text exists
    input_password.bind(
        "<KeyRelease>",
        lambda event: manageVisibility(
            event, ImageTk, Image, canvas_manage, tk.NW, input_password, x, y
        ),
    )

    # Bind click on the canvas to toggle password visibility
    canvas_manage.bind(
        "<Button-1>",
        lambda event: togglePasswordVisibility(
            event, ImageTk, Image, canvas_manage, tk.NW, input_password, x, y
        ),
    )

    return canvas_manage
