import tkinter as tk
from typing import Optional

from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold
from app.presentation.views.helpers.ui.builder.empty_state import (
    build_albums_empty_state,
)
from app.presentation.widgets.window import create_toplevel


def albunsProfileWindow(is_own: bool = True, username: Optional[str] = None) -> None:
    """
    Display the albums profile window.

    Args:
        is_own: True when the logged-in user is viewing their own albums.
        username: Username of the profile owner (used in visitor-facing messages).
    """
    win: tk.Toplevel = create_toplevel(
        title="Profile - Albums",
        width=900,
        height=540,
        icon_path="app/assets/PhotoShowIcon.ico",
        bg_color=colors["primary-50"],
    )

    tk.Label(
        win,
        text="Albums",
        font=quickSandBold(22),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    ).place(x=40, y=20)

    # TODO: Not yet implemented — the albums list is a placeholder.
    #       Replace this empty state with real album data fetched from the DB,
    #       showing the user's actual albums (or a dynamic empty state if they have none).
    build_albums_empty_state(win, is_own=is_own, username=username)

    win.grab_set()
