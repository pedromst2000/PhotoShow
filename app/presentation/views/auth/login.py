import tkinter as tk
import tkinter.messagebox as messagebox
from typing import Optional

from PIL import Image, ImageTk

from app.controllers.auth_controller import AuthController
from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold, quickSandRegular
from app.presentation.views.auth.register import registerWindow
from app.presentation.views.home.home import homeWindow
from app.presentation.views.home.home_banned import homeBannedWindow
from app.presentation.widgets.auth_icons import manageVisibility
from app.presentation.widgets.auth_icons import on_enter as label_on_enter
from app.presentation.widgets.auth_icons import on_leave as label_on_leave
from app.presentation.widgets.auth_icons import togglePasswordVisibility
from app.presentation.widgets.button import on_enter as button_on_enter
from app.presentation.widgets.button import on_leave as button_on_leave
from app.presentation.widgets.input import on_click_outside, on_focus_in, on_focus_out


def loginWindow(event: object, Window: tk.Tk):
    """
    Create and display the login window for user authentication.

    Args:
        event (object): The event object from Tkinter.
        Window (object): The main application window to pass to the login window.
    """

    # open the window
    _loginWindow_: tk.Toplevel = tk.Toplevel()

    # centering the window
    loginWindowWidth: int = 573  # width of the window
    loginWindowHeight: int = 580  # height of the window

    screenWidth: int = _loginWindow_.winfo_screenwidth()  # width of the screen

    screenHeight: int = _loginWindow_.winfo_screenheight()  # height of the screen

    x: int = int((screenWidth / 2) - (loginWindowWidth / 2))  # calculate x position

    y: int = int((screenHeight / 2) - (loginWindowHeight / 2))  # calculate y position

    # setting the window size and position
    # %d = integer
    # %dx%d = width x height
    # %d+%d = x position + y position
    _loginWindow_.geometry("%dx%d+%d+%d" % (loginWindowWidth, loginWindowHeight, x, y))
    _loginWindow_.title("Sign In")
    _loginWindow_.iconbitmap("app/assets/PhotoShowIcon.ico")
    _loginWindow_.resizable(False, False)
    _loginWindow_.config(bg=colors["primary-50"])

    canvasLogo: tk.Canvas = tk.Canvas(
        _loginWindow_, height=120, width=334, highlightthickness=0
    )
    canvasLogo.place(x=120, y=20)

    logo_image: Image.Image = Image.open("app/assets/images/Logo_auth.png")
    logo_image = logo_image.resize((334, 120))

    canvasLogo.image = ImageTk.PhotoImage(logo_image)

    canvasLogo.create_image(0, 0, anchor=tk.NW, image=canvasLogo.image)

    # ---------------------------

    # email icon label
    emailIcon: Image.Image = Image.open("app/assets/images/UI_Icons/Email_Icon.png")
    emailIcon = emailIcon.resize((48, 44))

    canvasEmailIcon: tk.Canvas = tk.Canvas(
        _loginWindow_, height=40, width=46, highlightthickness=0
    )
    canvasEmailIcon.place(x=130, y=170)

    canvasEmailIcon.image = ImageTk.PhotoImage(emailIcon)

    canvasEmailIcon.create_image(0, 0, anchor=tk.NW, image=canvasEmailIcon.image)

    # ---------------------------

    # password icon label
    passwordIcon: Image.Image = Image.open(
        "app/assets/images/UI_Icons/Password_Icon.png"
    )
    passwordIcon = passwordIcon.resize((48, 44))

    canvasPasswordIcon: tk.Canvas = tk.Canvas(
        _loginWindow_, height=40, width=46, highlightthickness=0
    )
    canvasPasswordIcon.place(x=130, y=280)

    canvasPasswordIcon.image = ImageTk.PhotoImage(passwordIcon)
    canvasPasswordIcon.create_image(0, 0, anchor=tk.NW, image=canvasPasswordIcon.image)

    # ---------------------------

    emailLabel: tk.Label = tk.Label(
        _loginWindow_,
        text="email",
        font=quickSandBold(14),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )
    emailLabel.place(x=175, y=190, anchor="w")

    # ---------------------------
    passwordLabel: tk.Label = tk.Label(
        _loginWindow_,
        text="password",
        font=quickSandBold(14),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )
    passwordLabel.place(x=175, y=302, anchor="w")

    # ---------------------------

    inputEmail: tk.Entry = tk.Entry(
        _loginWindow_,
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
    # ---------------------------

    inputPassword: tk.Entry = tk.Entry(
        _loginWindow_,
        width=30,
        borderwidth=0,
        font=quickSandBold(12),
        bg=colors["secondary-300"],
        fg=colors["secondary-500"],
        highlightthickness=0,
        show="*",
        cursor="xterm",
    )
    inputPassword.place(x=140, y=330)
    inputPassword.bind("<FocusIn>", lambda event: on_focus_in(event, inputPassword))
    inputPassword.bind("<FocusOut>", lambda event: on_focus_out(event, inputPassword))

    # ---------------------------
    #  manage password
    canvasManagePassword: tk.Canvas = tk.Canvas(
        _loginWindow_, height=36, width=50, highlightthickness=0, cursor="hand2"
    )

    canvasManagePassword.config(highlightthickness=0, bd=0, bg=colors["primary-50"])

    # bind - when the user releases the key (onKeyPress), the function will be called
    inputPassword.bind(
        "<KeyRelease>",
        lambda event: manageVisibility(
            event, ImageTk, Image, canvasManagePassword, tk.NW, inputPassword, 445, 325
        ),
    )

    # bind - when the user clicks (onClick) on the canvas, the function will be called
    canvasManagePassword.bind(
        "<Button-1>",
        lambda event: togglePasswordVisibility(
            event, ImageTk, Image, canvasManagePassword, tk.NW, inputPassword, 445, 325
        ),
    )

    # ---------------------------

    labelInfo: tk.Label = tk.Label(
        _loginWindow_,
        text="Don't have an account? Sign up!",
        font=quickSandRegular(12),
        bd=0,
        bg=colors["primary-50"],
        highlightthickness=0,
        fg=colors["secondary-500"],
        cursor="hand2",
    )
    labelInfo.place(x=162, y=409)
    labelInfo.bind("<Enter>", lambda event: label_on_enter(event, labelInfo))
    labelInfo.bind("<Leave>", lambda event: label_on_leave(event, labelInfo))
    labelInfo.bind(
        "<Button-1>",
        lambda event: openSignUpLink(event, _loginWindow_, Window),
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

    def trigger_check_login(event: Optional[tk.Event] = None):
        """
        Helper function to trigger the login check using the current input values.
        Can be called by button click or Enter key event.

        Args:
            event (tk.Event, optional): The event object from Tkinter. Defaults to None.
        """
        checkLogin(inputEmail.get(), inputPassword.get(), _loginWindow_, Window)

    # Bind button click
    btnSignIn.bind("<Button-1>", trigger_check_login)
    # Bind Enter key (Return) to window
    _loginWindow_.bind("<Return>", trigger_check_login)

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
    success, message, _ = AuthController.login(email, password)

    if not success:
        messagebox.showerror("Error", message, parent=loginWindow)
        return

    # Show success message
    messagebox.showinfo("Success", message, parent=loginWindow)

    # Close windows and navigate
    loginWindow.destroy()
    Window.destroy()

    # Navigate to appropriate home based on user state
    if AuthController.is_current_user_blocked():
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
    registerWindow(window)
