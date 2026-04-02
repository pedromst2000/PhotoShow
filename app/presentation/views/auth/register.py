import tkinter as tk
import tkinter.messagebox as messagebox

from app.controllers.auth_controller import AuthController
from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold
from app.presentation.views.auth.helpers import auth_switch_label
from app.presentation.views.home.home import homeWindow
from app.presentation.widgets.helpers.button import on_enter as button_on_enter
from app.presentation.widgets.helpers.button import on_leave as button_on_leave
from app.presentation.widgets.helpers.icon_label import add_icon_canvas, add_label
from app.presentation.widgets.helpers.input import (
    on_click_outside,
    on_focus_in,
    on_focus_out,
)
from app.presentation.widgets.helpers.password_visibility import (
    attach_password_visibility,
)
from app.presentation.widgets.window import add_logo_canvas, create_toplevel


def registerWindow(event: object, Window: object):
    """
    This function is used to create the register window.

    Args:
        event (object): The event object from Tkinter.
        Window (object): The window of the application.
    """

    _registerWindow_: tk.Toplevel = create_toplevel(
        title="Sign Up",
        width=590,
        height=670,
        icon_path="app/assets/PhotoShowIcon.ico",
        bg_color=colors["primary-50"],
    )

    # add logo canvas
    add_logo_canvas(
        _registerWindow_,
        "app/assets/images/Logo_auth.png",
        x=120,
        y=20,
        width=334,
        height=120,
    )

    # ---------------------------

    # Icon Email
    add_icon_canvas(
        "email",
        _registerWindow_,
        "app/assets/images/UI_Icons/Email_Icon.png",
        icon_pos=(130, 170),
    )

    # Icon Password
    add_icon_canvas(
        "password",
        _registerWindow_,
        "app/assets/images/UI_Icons/Password_Icon.png",
        icon_pos=(130, 280),
    )

    # Icon Username
    add_icon_canvas(
        "username",
        _registerWindow_,
        "app/assets/images/UI_Icons/Username_Icon.png",
        icon_pos=(130, 390),
    )

    # Label Email
    add_label("email", _registerWindow_, "email", label_pos=(175, 190))

    # Label Password
    add_label("password", _registerWindow_, "password", label_pos=(175, 302))

    # Label Username
    add_label("username", _registerWindow_, "username", label_pos=(175, 412))

    # -- Inputs ---------------------------------------------------

    inputEmail = tk.Entry(
        _registerWindow_,
        width=30,
        borderwidth=0,
        font=quickSandBold(12),
        bg=colors["secondary-300"],
        fg=colors["secondary-500"],
        highlightthickness=0,
        cursor="xterm",
    )
    inputEmail.place(x=140, y=220)
    inputEmail.bind("<FocusIn>", lambda event: on_focus_in(event, inputEmail))
    inputEmail.bind("<FocusOut>", lambda event: on_focus_out(event, inputEmail))

    inputPassword = tk.Entry(
        _registerWindow_,
        width=30,
        borderwidth=0,
        font=quickSandBold(12),
        bg=colors["secondary-300"],
        fg=colors["secondary-500"],
        highlightthickness=0,
        cursor="xterm",
        show="*",
    )
    inputPassword.place(x=140, y=330)
    inputPassword.bind("<FocusIn>", lambda event: on_focus_in(event, inputPassword))
    inputPassword.bind("<FocusOut>", lambda event: on_focus_out(event, inputPassword))

    inputUsername = tk.Entry(
        _registerWindow_,
        width=30,
        borderwidth=0,
        font=quickSandBold(12),
        bg=colors["secondary-300"],
        fg=colors["secondary-500"],
        highlightthickness=0,
        cursor="xterm",
    )
    inputUsername.place(x=140, y=440)
    inputUsername.bind("<FocusIn>", lambda event: on_focus_in(event, inputUsername))
    inputUsername.bind("<FocusOut>", lambda event: on_focus_out(event, inputUsername))

    # password visibility canvas + bindings
    attach_password_visibility(_registerWindow_, inputPassword, 445, 325)

    # ---------------------------

    # Create the "Already have an account? Sign In!" label with click handler to open login window
    auth_switch_label(
        "Already have an account? Sign In!",
        _registerWindow_,
        164,
        500,
        openSignInLink,
        _registerWindow_,
        Window,
    )

    btnSignUp: tk.Button = tk.Button(
        _registerWindow_,
        width=24,
        height=2,
        text="Sign Up",
        borderwidth=10,
        font=quickSandBold(13),
        background=colors["accent-300"],
        bd=0,
        highlightthickness=0,
        activebackground=colors["accent-100"],
        cursor="hand2",
    )

    btnSignUp.place(x=164, y=570)
    # Hoover effect on the button
    btnSignUp.bind("<Enter>", lambda event: button_on_enter(event, btnSignUp))
    btnSignUp.bind("<Leave>", lambda event: button_on_leave(event, btnSignUp))

    _registerWindow_.bind(
        "<Button-1>",
        lambda event: on_click_outside(
            event, _registerWindow_, inputEmail, inputPassword, inputUsername
        ),
    )

    # bind - when the user clicks (onClick) on the button, will trigger checkRegister function
    btnSignUp.bind(
        "<Button-1>",
        lambda event: checkRegister(
            event,
            inputEmail.get(),
            inputPassword.get(),
            inputUsername.get(),
            _registerWindow_,
            Window,
        ),
    )

    _registerWindow_.grab_set()


def checkRegister(
    event: object,
    email: str,
    password: str,
    username: str,
    registerWindow: object,
    Window: object,
):
    """
    Handle register button click - delegates to AuthController.

    Args:
        event (object): The event object from the button click.
        email (str): The email entered by the user.
        password (str): The password entered by the user.
        username (str): The username entered by the user.
        registerWindow (object): The current register window to be closed if registration is successful.
        Window (object): The main application window to be passed to the home window if registration is successful.
    """
    success, message, _ = AuthController.register(username, email, password)

    if not success:
        messagebox.showerror("Error", message, parent=registerWindow)
        return

    # Show success message
    messagebox.showinfo("Success", message, parent=registerWindow)

    # Close windows and navigate
    registerWindow.destroy()
    Window.destroy()

    # Navigate to home
    homeWindow()


def openSignInLink(event: object, registerWindow: object, window: object):
    """
    Open the sign in window from the register window.

    Args:
        event (object): The event object from the button click.
        registerWindow (object): The current register window to be closed.
        window (object): The main application window to be passed to the login window.
    """
    # Local import to avoid circular dependency
    from app.presentation.views.auth.login import loginWindow

    registerWindow.destroy()
    loginWindow(event, window)
