import tkinter as tk
from typing import Callable, Optional

from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold, quickSandRegular
from app.presentation.widgets.helpers.button import make_button


def build_empty_state(
    win: tk.Widget,
    *,
    icon: str,
    title: str,
    subtitle: str = "",
    btn_text: Optional[str] = None,
    btn_cmd: Optional[Callable] = None,
    bg: Optional[str] = None,
    icon_rely: float = 0.40,
    title_rely: float = 0.55,
    subtitle_rely: float = 0.64,
    btn_rely: float = 0.76,
) -> None:
    """
    Render a centred empty-state block inside *win*.

    Args:
        win: The parent window or frame.
        icon: Unicode emoji / character shown as a large glyph.
        title: Bold heading text.
        subtitle: Smaller description text shown below the title.
        btn_text: Label for an optional call-to-action button.
                  Pass ``None`` to omit the button.
        btn_cmd: Callback invoked when the button is clicked.
        bg: Background colour (defaults to ``colors["primary-50"]``).
        icon_rely: Relative Y position for the icon (0-1).
        title_rely: Relative Y position for the title (0-1).
        subtitle_rely: Relative Y position for the subtitle (0-1).
        btn_rely: Relative Y position for the button (0-1).
    """
    _bg = bg or colors["primary-50"]

    tk.Label(
        win,
        text=icon,
        font=quickSandBold(48),
        bg=_bg,
        fg=colors["secondary-400"],
    ).place(relx=0.5, rely=icon_rely, anchor=tk.CENTER)

    tk.Label(
        win,
        text=title,
        font=quickSandBold(18),
        bg=_bg,
        fg=colors["secondary-500"],
    ).place(relx=0.5, rely=title_rely, anchor=tk.CENTER)

    if subtitle:
        tk.Label(
            win,
            text=subtitle,
            font=quickSandRegular(12),
            bg=_bg,
            fg=colors["secondary-400"],
        ).place(relx=0.5, rely=subtitle_rely, anchor=tk.CENTER)

    if btn_text and btn_cmd:
        btn = make_button(
            win,
            btn_text,
            cmd=btn_cmd,
            font=quickSandBold(13),
            bg=colors["accent-300"],
            fg=colors["secondary-500"],
            activebackground=colors["accent-100"],
            activeforeground=colors["secondary-500"],
            borderwidth=0,
            highlightthickness=0,
            cursor="hand2",
            padx=20,
            pady=8,
            relief=tk.FLAT,
        )
        btn.place(relx=0.5, rely=btn_rely, anchor=tk.CENTER)


def build_albums_empty_state(
    win: tk.Widget,
    *,
    is_own: bool = True,
    username: Optional[str] = None,
) -> None:
    """
    Render the albums empty-state block, including the sub-header label.

    Args:
        win: The parent window or frame.
        is_own: Whether the profile belongs to the logged-in user.
        username: The profile owner's username, used when is_own is False.
    """
    if is_own:
        sub_header = "Create and manage your photo albums."
        empty_title = "You don't have any albums yet"
        empty_sub = "Create your first album to start sharing your photos!"
        btn_text: Optional[str] = "  Add Album"

        def _open_create() -> None:
            from app.presentation.views.album.create import openCreateAlbum

            openCreateAlbum()

        btn_cmd: Optional[Callable] = _open_create
    else:
        name = username or "This user"
        sub_header = f"Browse {name}'s photo albums."
        empty_title = f"{name} doesn't have any albums yet"
        empty_sub = "Check back later to see their albums."
        btn_text = None
        btn_cmd = None

    tk.Label(
        win,
        text=sub_header,
        font=quickSandRegular(12),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    ).place(x=40, y=60)

    build_empty_state(
        win,
        icon="\U0001f4f7",
        title=empty_title,
        subtitle=empty_sub,
        btn_text=btn_text,
        btn_cmd=btn_cmd,
    )


def build_favorites_empty_state(
    win: tk.Widget,
    *,
    is_own: bool = True,
    username: Optional[str] = None,
) -> None:
    """
    Render the favorites empty-state block, including the sub-header label.

    Args:
        win: The parent window or frame.
        is_own: Whether the profile belongs to the logged-in user.
        username: The profile owner's username, used when is_own is False.
    """
    if is_own:
        sub_header = "Albums you have marked as favorites will appear here."
        empty_title = "You haven't added any favorites yet"
        empty_sub = "Browse albums and add them to your favorites to see them here."
    else:
        name = username or "This user"
        sub_header = f"{name}'s favorite albums."
        empty_title = f"{name} hasn't added any favorites yet"
        empty_sub = "Check back later to see their favorite albums."

    tk.Label(
        win,
        text=sub_header,
        font=quickSandRegular(12),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    ).place(x=40, y=60)

    build_empty_state(
        win,
        icon="\u2728",
        title=empty_title,
        subtitle=empty_sub,
    )


def build_contacts_empty_state(win: tk.Widget) -> None:
    """
    Render the contacts empty-state block, including the sub-header label.

    Args:
        win: The parent window or frame.
    """
    tk.Label(
        win,
        text="Messages sent by users will appear here for review.",
        font=quickSandRegular(12),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    ).place(x=40, y=60)

    build_empty_state(
        win,
        icon="\U0001f465",
        title="No contact messages",
        subtitle="When users send contact messages they will appear here.",
    )


def build_reports_empty_state(win: tk.Widget) -> None:
    """
    Render the reports empty-state block, including the sub-header label.

    Args:
        win: The parent window or frame.
    """
    tk.Label(
        win,
        text="Review and manage reported content submitted by users.",
        font=quickSandRegular(12),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    ).place(x=40, y=60)

    build_empty_state(
        win,
        icon="\U0001f6a8",
        title="No reports to review",
        subtitle="When users submit reports about inappropriate content they will appear here.",
    )


def build_profile_photos_empty_state(
    win: tk.Widget,
    *,
    is_unsigned: bool = False,
    is_logged_in: bool = True,
    own_profile: bool = True,
    icon_rely: float = 0.40,
    title_rely: float = 0.55,
    subtitle_rely: float = 0.64,
) -> None:
    """
    Render the feature-photos empty-state for the profile window.

    Args:
        win: The parent window or frame.
        is_unsigned: Whether the user is unsigned.
        is_logged_in: Whether the user is logged in.
        own_profile: Whether the profile belongs to the logged-in user.
        icon_rely: The relative y-position of the icon.
        title_rely: The relative y-position of the title.
        subtitle_rely: The relative y-position of the subtitle.
    """
    if is_unsigned or not is_logged_in:
        # Unsigned users should see a message encouraging them to sign up.
        empty_title = "No feature photos"
        empty_sub = "You need approve of the admin " "to start having feature photos"
    elif own_profile:
        empty_title = "You don't have any photos yet"
        empty_sub = (
            "Upload your first photo to an album to start "
            "collecting likes, comments and ratings!"
        )
    else:
        empty_title = "No featured photos yet"
        empty_sub = "This user hasn't uploaded any photos yet."

    build_empty_state(
        win,
        icon="\U0001f4f7",
        title=empty_title,
        subtitle=empty_sub,
        icon_rely=icon_rely,
        title_rely=title_rely,
        subtitle_rely=subtitle_rely,
    )
