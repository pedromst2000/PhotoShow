import tkinter as tk
import tkinter.messagebox as messagebox

from PIL import Image, ImageTk

from app.controllers.auth_controller import AuthController
from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold, quickSandRegular
from app.presentation.views.home.home import homeWindow
from app.presentation.widgets.auth_icons import manageVisibility
from app.presentation.widgets.auth_icons import on_enter as label_on_enter
from app.presentation.widgets.auth_icons import on_leave as label_on_leave
from app.presentation.widgets.auth_icons import togglePasswordVisibility
from app.presentation.widgets.button import on_enter as button_on_enter
from app.presentation.widgets.button import on_leave as button_on_leave
from app.presentation.widgets.input import on_click_outside, on_focus_in, on_focus_out


def registerWindow(Window: object):
    """
    This function is used to create the register window.

    Args:
        Window (object): The window of the application.
    """

    # open the window
    _registerWindow_: tk.Toplevel = tk.Toplevel()

    # centering the window
    registerWindowWidth: int = 590  # width of the window
    registerWindowHeight: int = 670  # height of the window

    screenWidth: int = _registerWindow_.winfo_screenwidth()  # width of the screen

    screenHeight: int = _registerWindow_.winfo_screenheight()  # height of the screen

    x: float = (screenWidth / 2) - (registerWindowWidth / 2)  # calculate x position

    y: float = (screenHeight / 2) - (registerWindowHeight / 2)  # calculate y position

    # setting the window size and position
    # %d = integer
    # %dx%d = width x height
    # %d+%d = x position + y position
    _registerWindow_.geometry(
        "%dx%d+%d+%d" % (registerWindowWidth, registerWindowHeight, x, y)
    )
    _registerWindow_.title("Sign Up")
    _registerWindow_.iconbitmap("app/assets/PhotoShowIcon.ico")
    _registerWindow_.resizable(0, 0)
    _registerWindow_.config(bg=colors["primary-50"])

    canvasLogo: tk.Canvas = tk.Canvas(
        _registerWindow_, height=120, width=334, highlightthickness=0
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
        _registerWindow_, height=40, width=46, highlightthickness=0
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
        _registerWindow_, height=40, width=46, highlightthickness=0
    )
    canvasPasswordIcon.place(x=130, y=280)

    canvasPasswordIcon.image = ImageTk.PhotoImage(passwordIcon)
    canvasPasswordIcon.create_image(0, 0, anchor=tk.NW, image=canvasPasswordIcon.image)

    # ---------------------------

    # username icon label
    usernameIcon: Image.Image = Image.open(
        "app/assets/images/UI_Icons/Username_Icon.png"
    )
    usernameIcon = usernameIcon.resize((48, 44))

    canvasUsernameIcon: tk.Canvas = tk.Canvas(
        _registerWindow_, height=40, width=46, highlightthickness=0
    )

    canvasUsernameIcon.place(x=130, y=390)

    canvasUsernameIcon.image = ImageTk.PhotoImage(usernameIcon)

    canvasUsernameIcon.create_image(0, 0, anchor=tk.NW, image=canvasUsernameIcon.image)

    # ---------------------------

    emailLabel: tk.Label = tk.Label(
        _registerWindow_,
        text="email",
        font=quickSandBold(14),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )
    emailLabel.place(x=175, y=190, anchor=tk.W)

    # ---------------------------
    passwordLabel: tk.Label = tk.Label(
        _registerWindow_,
        text="password",
        font=quickSandBold(14),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )
    passwordLabel.place(x=175, y=302, anchor=tk.W)

    # ---------------------------

    usernameLabel: tk.Label = tk.Label(
        _registerWindow_,
        text="username",
        font=quickSandBold(14),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )
    usernameLabel.place(x=175, y=412, anchor=tk.W)

    # ---------------------------

    inputEmail: tk.Entry = tk.Entry(
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
    # ---------------------------

    inputPassword: tk.Entry = tk.Entry(
        _registerWindow_,
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

    inputUsername: tk.Entry = tk.Entry(
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

    # ---------------------------

    #  manage password
    canvasManagePassword: tk.Canvas = tk.Canvas(
        _registerWindow_, height=36, width=50, highlightthickness=0, cursor="hand2"
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
        _registerWindow_,
        text="Already have an account? Sign In!",
        font=quickSandRegular(12),
        bd=0,
        bg=colors["primary-50"],
        highlightthickness=0,
        fg=colors["secondary-500"],
        cursor="hand2",
    )

    labelInfo.place(x=164, y=500)
    labelInfo.bind("<Enter>", lambda event: label_on_enter(event, labelInfo))
    labelInfo.bind("<Leave>", lambda event: label_on_leave(event, labelInfo))
    labelInfo.bind(
        "<Button-1>",
        lambda event: openSignInLink(event, _registerWindow_, Window),
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
    from views.auth.login import loginWindow

    registerWindow.destroy()
    loginWindow(event, window)
