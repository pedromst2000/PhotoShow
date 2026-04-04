import tkinter as tk
import tkinter.messagebox as messagebox

from app.controllers.auth_controller import AuthController
from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold
from app.presentation.views.auth.helpers import (
    attach_password_visibility,
    auth_switch_label,
    trigger_check_login,
)
from app.presentation.views.auth.register import registerWindow
from app.presentation.views.home.home import homeWindow
from app.presentation.views.home.home_banned import homeBannedWindow
from app.presentation.widgets.helpers.button import on_enter as button_on_enter
from app.presentation.widgets.helpers.button import on_leave as button_on_leave
from app.presentation.widgets.helpers.icon_label import add_icon_canvas, add_label
from app.presentation.widgets.helpers.input import (
    on_click_outside,
    on_focus_in,
    on_focus_out,
)
from app.presentation.widgets.helpers.window import load_image
from app.presentation.widgets.window import create_toplevel


def loginWindow(event: object, Window: tk.Tk):
    """
    Create and display the login window for user authentication.

    Args:
        event (object): The event object from Tkinter.
        Window (tk.Tk): The main application window to pass to the login window.
    """

    _loginWindow_: tk.Toplevel = create_toplevel(
        title="Sign In",
        width=573,
        height=580,
        icon_path="app/assets/PhotoShowIcon.ico",
        bg_color=colors["primary-50"],
    )

    # Logo — small canvas matching the window bg so the image renders without border
    _logo_canvas = tk.Canvas(
        _loginWindow_,
        width=334,
        height=120,
        highlightthickness=0,
        bd=0,
        bg=colors["primary-50"],
    )
    _logo_canvas.place(x=120, y=20)
    _logo_canvas.image = load_image(
        "app/assets/images/Logo_auth.png",
        size=(334, 120),
        canvas=_logo_canvas,
        x=0,
        y=0,
    )

    # ---------------------------
    # Icon Email
    add_icon_canvas(
        "email",
        _loginWindow_,
        "app/assets/images/UI_Icons/Email_Icon.png",
        icon_pos=(130, 170),
    )

    # Icon Password
    add_icon_canvas(
        "password",
        _loginWindow_,
        "app/assets/images/UI_Icons/Password_Icon.png",
        icon_pos=(130, 280),
    )

    # Label Email
    add_label("email", _loginWindow_, "email", label_pos=(175, 190))

    # Label Password
    add_label("password", _loginWindow_, "password", label_pos=(175, 302))

    # -- Inputs ---------------------------------------------------

    inputEmail = tk.Entry(
        _loginWindow_,
        width=30,
        borderwidth=0,
        font=quickSandBold(12),
        bg=colors["secondary-300"],
        fg=colors["secondary-500"],
        highlightthickness=0,
        cursor="xterm",
    )

    inputPassword = tk.Entry(
        _loginWindow_,
        width=30,
        borderwidth=0,
        font=quickSandBold(12),
        bg=colors["secondary-300"],
        fg=colors["secondary-500"],
        highlightthickness=0,
        cursor="xterm",
        show="*",
    )

    inputEmail.place(x=140, y=220)
    inputEmail.bind("<FocusIn>", lambda event: on_focus_in(event, inputEmail))
    inputEmail.bind("<FocusOut>", lambda event: on_focus_out(event, inputEmail))

    inputPassword.place(x=140, y=330)
    inputPassword.bind("<FocusIn>", lambda event: on_focus_in(event, inputPassword))
    inputPassword.bind("<FocusOut>", lambda event: on_focus_out(event, inputPassword))

    # password visibility canvas + bindings
    attach_password_visibility(_loginWindow_, inputPassword, 445, 325)

    # ---------------------------

    # Create the "Don't have an account? Sign up!" label with click handler to open register window
    auth_switch_label(
        "Don't have an account? Sign up!",
        _loginWindow_,
        162,
        409,
        openSignUpLink,
        _loginWindow_,
        Window,
    )

    # ---------------------------

    btnSignIn: tk.Button = tk.Button(
        _loginWindow_,
        width=24,
        height=2,
        text="Sign In",
        borderwidth=10,
        font=quickSandBold(13),
        background=colors["accent-300"],
        bd=0,
        highlightthickness=0,
        activebackground=colors["accent-100"],
        cursor="hand2",
    )

    btnSignIn.place(x=164, y=475)
    # Hoover effect on the button
    btnSignIn.bind("<Enter>", lambda event: button_on_enter(event, btnSignIn))
    btnSignIn.bind("<Leave>", lambda event: button_on_leave(event, btnSignIn))

    _loginWindow_.bind(
        "<Button-1>",
        lambda event: on_click_outside(event, _loginWindow_, inputEmail, inputPassword),
    )

    # Create and bind the login trigger handler using helper factory
    trigger_check_login_handler = trigger_check_login(
        checkLogin, inputEmail, inputPassword, _loginWindow_, Window
    )

    # Bind button click and Enter key to the handler
    btnSignIn.bind("<Button-1>", trigger_check_login_handler)
    _loginWindow_.bind("<Return>", trigger_check_login_handler)

    _loginWindow_.grab_set()


def checkLogin(
    email: str, password: str, loginWindow: tk.Toplevel, Window: tk.Tk
) -> None:
    """
    Handle login button click - delegates to AuthController.

    Args:
        email (str): The email entered by the user.
        password (str): The password entered by the user.
        loginWindow (object): The login window instance to be destroyed on successful login.
        Window (object): The main application window to pass to the home window.
    """

    # discarding user object returned by controller since we don't need it here, and it would be redundant to fetch it again in the home window after login. If login is successful, the session will already have the user data stored, so the home window can access it from there without needing it to be passed through this function. This keeps the code cleaner and avoids unnecessary data handling in this part of the flow.
    success, message, _ = AuthController.login(
        email, password
    )  # '_' intentionally unused (discarded user object)

    if not success:
        messagebox.showerror("Error", message, parent=loginWindow)
        return

    # Show success message
    messagebox.showinfo("Success", message, parent=loginWindow)

    # Close windows and navigate
    loginWindow.destroy()
    Window.destroy()

    # Navigate to appropriate home based on controller decision
    destination = AuthController.get_post_login_destination()
    if destination == "home_banned":
        homeBannedWindow()
    else:
        homeWindow()


def openSignUpLink(event: tk.Event, loginWindow: tk.Toplevel, window: tk.Tk):
    """
    Open the sign up (register) window from the login window.

    Args:
        event (tk.Event): The event object from Tkinter.
        loginWindow (object): The login window instance to be destroyed.
        window (object): The main application window to pass to the register window.

    """
    loginWindow.destroy()
    registerWindow(event, window)
