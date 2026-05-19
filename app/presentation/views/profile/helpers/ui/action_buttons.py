import tkinter as tk

from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold
from app.presentation.views.profile.change_avatar import changeAvatarWindow
from app.presentation.views.profile.change_password import changePasswordWindow
from app.presentation.widgets.helpers.button import make_button


def build_profile_action_buttons(
    window: tk.Toplevel,
    *,
    win_w: int,
    win_h: int,
):
    """
    Render the action buttons (Change Avatar, Change Password) for the profile window.

    Args:
        window: The profile Toplevel window.
        win_w: Full pixel width of the window.
        win_h: Full pixel height of the window.
    """

    _btn_style = dict(
        font=quickSandBold(13),
        bg=colors["accent-300"],
        fg=colors["secondary-500"],
        activebackground=colors["accent-100"],
        activeforeground=colors["secondary-500"],
        borderwidth=0,
        highlightthickness=0,
        cursor="hand2",
        padx=16,
        pady=8,
        relief=tk.FLAT,
    )

    action_frame = tk.Frame(window, bg=colors["primary-50"])
    action_frame.place(x=win_w - 20, y=win_h - 55, anchor=tk.NE)

    change_av_btn = make_button(
        action_frame,
        "Change Avatar",
        cmd=lambda: changeAvatarWindow(profile_window=window),
        **_btn_style,
    )
    change_av_btn.pack(side=tk.RIGHT, padx=(6, 0))

    change_pw_btn = make_button(
        action_frame, "Change password", cmd=changePasswordWindow, **_btn_style
    )
    change_pw_btn.pack(side=tk.RIGHT, padx=(0, 6))
