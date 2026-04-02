import tkinter as tk
import tkinter.messagebox as messagebox
from typing import Optional

from app.controllers.profile_controller import ProfileController
from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold
from app.presentation.widgets.helpers.button import on_enter as button_on_enter
from app.presentation.widgets.helpers.button import on_leave as button_on_leave
from app.presentation.widgets.helpers.input import (
    on_click_outside,
    on_focus_in,
    on_focus_out,
)
from app.presentation.widgets.window import create_toplevel


def changePasswordWindow():
    """
    This function is used to display change password window.
    """
    # create the window using the reusable helper
    _changePasswordWindow_: tk.Toplevel = create_toplevel(
        title="👤 Profile - Change Password 🔒🔑",
        width=500,
        height=500,
        icon_path="app/assets/PhotoShowIcon.ico",
        bg_color=colors["primary-50"],
    )

    # ---------------------- Labels -----------------------------------

    titleLabel: tk.Label = tk.Label(
        _changePasswordWindow_,
        text="Change Password",
        font=quickSandBold(22),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )
    titleLabel.place(x=130, y=20)

    currentPasswordLabel: tk.Label = tk.Label(
        _changePasswordWindow_,
        text="Current Password",
        font=quickSandBold(13),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )
    currentPasswordLabel.place(x=50, y=90)

    newPasswordLabel: tk.Label = tk.Label(
        _changePasswordWindow_,
        text="New Password",
        font=quickSandBold(13),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )
    newPasswordLabel.place(x=50, y=210)

    confirmPasswordLabel: tk.Label = tk.Label(
        _changePasswordWindow_,
        text="Confirm New Password",
        font=quickSandBold(13),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )
    confirmPasswordLabel.place(x=50, y=320)

    # ---------------------- Inputs -----------------------------------

    inputCurrentPassword: tk.Entry = tk.Entry(
        _changePasswordWindow_,
        width=30,
        borderwidth=0,
        font=quickSandBold(12),
        bg=colors["secondary-300"],
        fg=colors["secondary-500"],
        highlightthickness=0,
        show="*",
        cursor="xterm",
    )
    inputCurrentPassword.place(x=50, y=130)
    inputCurrentPassword.bind(
        "<FocusIn>", lambda e: on_focus_in(e, inputCurrentPassword)
    )
    inputCurrentPassword.bind(
        "<FocusOut>", lambda e: on_focus_out(e, inputCurrentPassword)
    )

    inputNewPassword: tk.Entry = tk.Entry(
        _changePasswordWindow_,
        width=30,
        borderwidth=0,
        font=quickSandBold(12),
        bg=colors["secondary-300"],
        fg=colors["secondary-500"],
        highlightthickness=0,
        show="*",
        cursor="xterm",
    )
    inputNewPassword.place(x=50, y=250)
    inputNewPassword.bind("<FocusIn>", lambda e: on_focus_in(e, inputNewPassword))
    inputNewPassword.bind("<FocusOut>", lambda e: on_focus_out(e, inputNewPassword))

    inputConfirmPassword: tk.Entry = tk.Entry(
        _changePasswordWindow_,
        width=30,
        borderwidth=0,
        font=quickSandBold(12),
        bg=colors["secondary-300"],
        fg=colors["secondary-500"],
        highlightthickness=0,
        show="*",
        cursor="xterm",
    )
    inputConfirmPassword.place(x=50, y=360)
    inputConfirmPassword.bind(
        "<FocusIn>", lambda e: on_focus_in(e, inputConfirmPassword)
    )
    inputConfirmPassword.bind(
        "<FocusOut>", lambda e: on_focus_out(e, inputConfirmPassword)
    )

    # ---------------------- Button -----------------------------------

    btnSave: tk.Button = tk.Button(
        _changePasswordWindow_,
        width=20,
        height=2,
        text="Save Password",
        borderwidth=0,
        font=quickSandBold(13),
        background=colors["accent-300"],
        highlightthickness=0,
        activebackground=colors["accent-100"],
        fg=colors["secondary-500"],
        cursor="hand2",
    )
    btnSave.place(x=130, y=420)
    btnSave.bind("<Enter>", lambda e: button_on_enter(e, btnSave))
    btnSave.bind("<Leave>", lambda e: button_on_leave(e, btnSave))

    _changePasswordWindow_.bind(
        "<Button-1>",
        lambda e: on_click_outside(
            e,
            _changePasswordWindow_,
            inputCurrentPassword,
            inputNewPassword,
            inputConfirmPassword,
        ),
    )

    # ---------------------- Events -----------------------------------

    def _submit_(event: Optional[tk.Event] = None):
        success, message = ProfileController.change_password(
            inputCurrentPassword.get(),
            inputNewPassword.get(),
            inputConfirmPassword.get(),
        )
        if success:
            messagebox.showinfo("Success", message, parent=_changePasswordWindow_)
            _changePasswordWindow_.destroy()
        else:
            messagebox.showerror("Error", message, parent=_changePasswordWindow_)

    btnSave.bind("<Button-1>", _submit_)
    _changePasswordWindow_.bind("<Return>", _submit_)

    _changePasswordWindow_.grab_set()
