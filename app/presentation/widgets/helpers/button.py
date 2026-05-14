import tkinter as tk
from typing import Any, Optional

from app.presentation.styles.colors import colors


def on_enter(event: tk.Event, button: tk.Button):
    """
    This function will change the background color of the button when hovering over it.
    Only applies hover effect if the button is in NORMAL state (not disabled).

    Args:
        event (tk.Event): The event object from the mouse entering the button.
        button (tk.Button): The button widget to change the background color of.

    """
    # Only apply hover effect if button is enabled
    if button.cget("state") == tk.NORMAL:
        button["background"] = colors["accent-100"]


def on_leave(event: tk.Event, button: tk.Button):
    """
    This function will change the background color of the button when the mouse is not hovering over it.
    Only applies if the button is in NORMAL state (not disabled).

    Args:
        event (tk.Event): The event object from the mouse leaving the button.
        button (tk.Button): The button widget to change the background color of.

    """
    # Only reset if button is enabled
    if button.cget("state") == tk.NORMAL:
        button["background"] = colors["accent-300"]


def make_button(
    parent: tk.Widget,
    text: str,
    *,
    cmd: Optional[Any] = None,
    icon: Optional[Any] = None,
    **kwargs: Any,
) -> tk.Button:
    """Create a tk.Button with hover effects already bound.

    All extra keyword arguments are forwarded directly to tk.Button, so callers
    can pass any standard Button option (font, bg, fg, padx, state, …).

    Args:
        parent: The parent widget.
        text: The button label.
        cmd: Optional click command.
        icon: Optional PhotoImage icon; sets ``image=icon`` and defaults
              ``compound`` to ``tk.LEFT`` if not already provided.
        **kwargs: Any tk.Button keyword arguments.

    Returns:
        tk.Button: The created button widget with hover effects bound.
    """
    if icon is not None:
        kwargs.setdefault("compound", tk.LEFT)
        kwargs["image"] = icon
    if cmd is not None:
        kwargs["command"] = cmd
    btn = tk.Button(parent, text=text, **kwargs)
    btn.bind("<Enter>", lambda e: on_enter(e, btn))
    btn.bind("<Leave>", lambda e: on_leave(e, btn))
    return btn


def switch_button(btn: tk.Button, text: str, *, icon: Optional[Any] = None):
    """Update a toggle button's label and icon in-place.

    Use this instead of destroying and recreating buttons when switching
    between two states (e.g. Follow/Unfollow, Like/Unlike, Favorite/Unfavorite).

    Args:
        btn: The button widget to update.
        text: The new button label.
        icon: Optional new PhotoImage icon.  When provided the button's
              ``image`` attribute is also updated and a reference is kept on
              ``btn.image`` to prevent garbage-collection.
    """
    cfg: dict = {"text": text}
    if icon is not None:
        cfg["image"] = icon
        btn.image = icon  # GC guard
    btn.config(**cfg)
