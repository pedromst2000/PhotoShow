import tkinter as tk
from typing import Optional

from app.core.state.session import session
from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold, quickSandRegular
from app.presentation.views.profile.helpers.avatar import (
    on_avatar_save,
    on_avatar_upload,
)
from app.presentation.widgets.helpers.button import make_button
from app.presentation.widgets.helpers.images import load_image
from app.presentation.widgets.window import create_toplevel


def changeAvatarWindow(profile_window: Optional[tk.Toplevel] = None) -> None:
    """
    Display the change avatar window.

    Provides UI for:
    - Viewing current avatar
    - Uploading new avatar image with preview
    - Saving avatar (copies to profile_avatars with {username}_avatar naming)
    - Persisting to database and syncing UI

    Args:
        profile_window: The parent profile window to close after a successful save.
    """
    user_id: int = session.user_id

    change_avatar_window: tk.Toplevel = create_toplevel(
        title="👤 Profile - Change Avatar 👤",
        width=500,
        height=595,
        icon_path="app/assets/PhotoShowIcon.ico",
        bg_color=colors["primary-50"],
    )

    # ----------------------  Labels -----------------------------------

    change_avatar_label: tk.Label = tk.Label(
        change_avatar_window,
        text="Change Avatar",
        font=quickSandBold(22),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )

    change_avatar_label.place(x=140, y=15)

    help_label: tk.Label = tk.Label(
        change_avatar_window,
        text="Select a new avatar for your profile",
        font=quickSandRegular(12),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )

    help_label.place(x=125, y=70)

    # ----------------------  Canvas for Preview Avatar -----------------------------------

    canvas_preview_avatar: tk.Canvas = tk.Canvas(
        change_avatar_window,
        width=200,
        height=200,
        bg=colors["primary-50"],
        highlightthickness=0,
    )

    canvas_preview_avatar.place(x=150, y=135)

    avatar_photo = load_image(
        session.avatar, size=(200, 200), canvas=canvas_preview_avatar, x=0, y=0
    )
    canvas_preview_avatar.image = avatar_photo

    # ----------------------  State Container -----------------------------------

    # Persistent state container across button clicks
    selected_avatar: dict[str, Optional[str]] = {"path": None}

    # ----------------------  Buttons -----------------------------------

    btn_save_avatar = make_button(
        change_avatar_window,
        "Save Avatar",
        width=16,
        height=2,
        state="disabled",
        borderwidth=10,
        font=quickSandBold(12),
        fg=colors["secondary-500"],
        background=colors["accent-300"],
        highlightthickness=0,
        activebackground=colors["accent-100"],
        cursor="arrow",
        compound="center",
        border=0,
        command=lambda: on_avatar_save(
            selected_avatar,
            user_id,
            change_avatar_window,
            profile_window,
        ),
    )

    btn_save_avatar.place(x=170, y=470)

    btn_change_avatar = make_button(
        change_avatar_window,
        "Upload Avatar",
        width=16,
        height=2,
        borderwidth=10,
        font=quickSandBold(12),
        fg=colors["secondary-500"],
        background=colors["accent-300"],
        highlightthickness=0,
        activebackground=colors["accent-100"],
        cursor="hand2",
        compound="center",
        border=0,
        command=lambda: on_avatar_upload(
            canvas_preview_avatar,
            btn_save_avatar,
            user_id,
            selected_avatar,
        ),
    )

    btn_change_avatar.place(x=170, y=380)

    change_avatar_window.grab_set()
