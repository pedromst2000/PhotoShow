import os
import sys
import tkinter as tk

from app.controllers.user_controller import UserController
from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold
from app.presentation.views.helpers.auth.ui import attach_password_visibility
from app.presentation.widgets.helpers.button import make_button
from app.presentation.widgets.helpers.icon_label import add_icon_canvas, add_label
from app.presentation.widgets.helpers.images import load_image
from app.presentation.widgets.helpers.input import (
    on_click_outside,
    on_focus_in,
    on_focus_out,
)
from app.presentation.widgets.helpers.ui_dialogs import show_error, show_info
from app.presentation.widgets.window import create_toplevel


def changePasswordWindow():
    """
    Create and display the change password window.

    Layout follows the auth windows pattern with logo, icons, labels, inputs, and button.
    """
    # Create window
    _changePasswordWindow_: tk.Toplevel = create_toplevel(
        title="👤 Profile - Change Password 🔒🔑",
        width=573,
        height=650,
        icon_path="app/assets/PhotoShowIcon.ico",
        bg_color=colors["primary-50"],
    )

    # ==================== Logo ====================
    _logo_canvas = tk.Canvas(
        _changePasswordWindow_,
        width=290,
        height=75,
        highlightthickness=0,
        bd=0,
        bg=colors["primary-50"],
    )
    _logo_canvas.place(x=142, y=20)
    _logo_canvas.image = load_image(
        "app/assets/images/Logo.png",
        size=(290, 75),
        canvas=_logo_canvas,
        x=0,
        y=0,
    )

    # ==================== Icons ====================
    # Icon Current Password
    add_icon_canvas(
        "current_password",
        _changePasswordWindow_,
        "app/assets/images/UI_Icons/Password_Icon.png",
        icon_pos=(130, 120),
    )

    # Icon New Password
    add_icon_canvas(
        "new_password",
        _changePasswordWindow_,
        "app/assets/images/UI_Icons/Password_Icon.png",
        icon_pos=(130, 240),
    )

    # Icon Confirm Password
    add_icon_canvas(
        "confirm_password",
        _changePasswordWindow_,
        "app/assets/images/UI_Icons/Password_Icon.png",
        icon_pos=(130, 360),
    )

    # ==================== Labels ====================
    add_label(
        "current_password",
        _changePasswordWindow_,
        "current password",
        label_pos=(175, 140),
    )
    add_label(
        "new_password", _changePasswordWindow_, "new password", label_pos=(175, 260)
    )
    add_label(
        "confirm_password",
        _changePasswordWindow_,
        "confirm password",
        label_pos=(175, 380),
    )

    # ==================== Inputs ====================
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
    inputCurrentPassword.place(x=140, y=170)
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
    inputNewPassword.place(x=140, y=290)
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
    inputConfirmPassword.place(x=140, y=410)
    inputConfirmPassword.bind(
        "<FocusIn>", lambda e: on_focus_in(e, inputConfirmPassword)
    )
    inputConfirmPassword.bind(
        "<FocusOut>", lambda e: on_focus_out(e, inputConfirmPassword)
    )

    # ==================== Password Visibility ====================
    attach_password_visibility(_changePasswordWindow_, inputCurrentPassword, 445, 165)
    attach_password_visibility(_changePasswordWindow_, inputNewPassword, 445, 285)
    attach_password_visibility(_changePasswordWindow_, inputConfirmPassword, 445, 405)

    # ==================== Button ====================
    btnSave = make_button(
        _changePasswordWindow_,
        "Save Password",
        width=24,
        height=2,
        borderwidth=10,
        font=quickSandBold(13),
        background=colors["accent-300"],
        bd=0,
        highlightthickness=0,
        activebackground=colors["accent-100"],
        cursor="hand2",
    )
    btnSave.place(x=164, y=515)

    # ==================== Events ====================
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

    # Bind button click and Enter key - calls checkChangePassword handler
    btnSave.bind(
        "<Button-1>",
        lambda e: checkChangePassword(
            inputCurrentPassword.get(),
            inputNewPassword.get(),
            inputConfirmPassword.get(),
            _changePasswordWindow_,
        ),
    )
    _changePasswordWindow_.bind(
        "<Return>",
        lambda e: checkChangePassword(
            inputCurrentPassword.get(),
            inputNewPassword.get(),
            inputConfirmPassword.get(),
            _changePasswordWindow_,
        ),
    )

    _changePasswordWindow_.grab_set()


def checkChangePassword(
    current_password: str,
    new_password: str,
    confirm_password: str,
    window: tk.Toplevel,
) -> None:
    """
    Handle the change password logic when the user clicks the save button or presses Enter.

    Args:
        current_password: The user's current password.
        new_password: The desired new password.
        confirm_password: Confirmation of the new password.
        window: The change password Toplevel window.
    """
    # Controller handles all validation and business logic
    success, message = UserController.change_password(
        current_password, new_password, confirm_password
    )

    if not success:
        show_error(window, "Error", message)
        return

    # Success - show message and restart app for better UX
    show_info(
        window,
        "Success",
        "Password changed successfully!\n\nThe application will restart to apply changes.",
    )

    # Close the window
    window.destroy()

    python = sys.executable  # Get the path to the Python interpreter
    os.execl(
        python, python, *sys.argv
    )  # Restart the application to refresh session and apply new password immediately
