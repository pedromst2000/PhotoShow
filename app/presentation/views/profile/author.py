import tkinter as tk

from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold
from app.presentation.views.helpers.data.state import BasePhotoState
from app.presentation.widgets.window import create_toplevel


def open_author_profile(state: BasePhotoState) -> None:
    """
    Open the profile window of the photo's author.

    Displays details about another user's profile when viewing their photo.

    Args:
        state: Explore view state containing selected photo info.
    """
    photo = state.selected_photo
    if photo is None or not photo.get("user"):
        return

    author_name = photo["user"]
    _open_author_profile_stub(f"👤 {author_name}'s Profile", 1000, 450)


def _open_author_profile_stub(title: str, width: int, height: int) -> None:
    """
    Create and display a stub window placeholder for author profile.

    TODO: Implement full author profile content with user stats and albums.

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
