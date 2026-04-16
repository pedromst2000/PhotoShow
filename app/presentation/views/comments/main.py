import tkinter as tk

from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold
from app.presentation.views.explore.helpers.data.state import ExploreState
from app.presentation.widgets.window import create_toplevel


def open_comments(state: ExploreState) -> None:
    """
    Open the photo comments window.

    Displays all comments on the selected photo.

    Args:
        state: Explore view state containing selected photo info.
    """
    if state.selected_photo is None:
        return
    _open_comments_stub("💬 Photo Comments", 600, 500)


def _open_comments_stub(title: str, width: int, height: int) -> None:
    """
    Create and display a stub window placeholder for comments.

    TODO: Implement full comments view with comment list, add comment form, and moderation options.

    Args:
        title: Window title to display.
        width: Window width in pixels.
        height: Window height in pixels.
    """
    win = create_toplevel(
        title=title,
        width=width,
        height=height,
        icon_path="app/assets/PhotoShowIcon.ico",
        bg_color=colors["primary-50"],
    )
    tk.Label(
        win,
        text=title,
        font=quickSandBold(16),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    ).pack(expand=True)
