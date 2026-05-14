import tkinter as tk
from typing import Optional

from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold
from app.presentation.views.helpers.ui.builder.empty_state import (
    build_favorites_empty_state,
)
from app.presentation.widgets.window import create_toplevel


def favoritesProfileWindow(is_own: bool = True, username: Optional[str] = None) -> None:
    """
    Display the favorite albums profile window.

    Args:
        is_own: True when the logged-in user is viewing their own favorites.
        username: Username of the profile owner (used in visitor-facing messages).
    """
    win: tk.Toplevel = create_toplevel(
        title="\U0001f464 Profile - Favorites \u2728",
        width=900,
        height=540,
        icon_path="app/assets/PhotoShowIcon.ico",
        bg_color=colors["primary-50"],
    )

    tk.Label(
        win,
        text="Favorite Albums",
        font=quickSandBold(22),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    ).place(x=40, y=20)

    # TODO: Not yet implemented — the favorites list is a placeholder.
    #       Replace this empty state with real favorites data fetched from the DB,
    #       showing albums the user has marked as favorites (or a dynamic empty state if none).
    build_favorites_empty_state(win, is_own=is_own, username=username)

    win.grab_set()
