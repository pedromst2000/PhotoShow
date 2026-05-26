import tkinter as tk
from typing import Any, Callable, Optional

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


def toggle_empty_content_state(state: Any, *, has_items: bool) -> None:
    """Show the content frame or the empty-state frame based on *has_items*.

    Shared by albums, favorites, contacts, and any future profile window that
    follows the same empty-frame / content-frame convention.  Both frames must
    be stored on *state* as ``_empty_frame`` and ``_content_frame``.

    Args:
        state: Any state object that carries ``_content_frame`` and
               ``_empty_frame`` attributes (set by the builder helpers).
        has_items: Pass ``True`` when there is at least one item to show
                   (content frame visible), ``False`` to reveal the empty state.
    """
    content_frame = getattr(state, "_content_frame", None)
    empty_frame = getattr(state, "_empty_frame", None)

    if content_frame is not None:
        if has_items:
            content_frame.pack(fill="both", expand=True)
        else:
            content_frame.pack_forget()

    if empty_frame is not None:
        if has_items:
            empty_frame.pack_forget()
        else:
            empty_frame.pack(fill="both", expand=True)
