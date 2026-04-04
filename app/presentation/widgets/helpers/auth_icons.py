import tkinter as tk

from app.presentation.styles.fonts import quickSandRegular, quickSandRegularUnderline
from app.presentation.widgets.helpers.window import load_image

isPasswordVisible: bool = False


def hidePasswordIcon(canvasManagePassword: tk.Canvas, anchor: str, X: int, Y: int):
    """
    Display the 'hide password' icon on the password field.

    Args:
        ImageTk (ImageTk): The PIL ImageTk module.
        Image (Image): The PIL Image module.
        canvasManagePassword (tk.Canvas): The Canvas widget for the password visibility icon.
        NW (str): The anchor constant for positioning the icon.
        X (int): The X coordinate for placing the icon.
        Y (int): The Y coordinate for placing the icon.
    """
    photo = load_image(
        "app/assets/images/UI_Icons/Hide_Eye_Icon.png",
        size=(60, 40),
        canvas=canvasManagePassword,
        x=0,
        y=0,
        anchor=anchor,
    )
    canvasManagePassword.image = photo
    canvasManagePassword.place(x=X, y=Y)


def showPasswordIcon(canvasManagePassword: tk.Canvas, anchor: str, X: int, Y: int):
    """
    Display the 'show password' icon on the password field.

    Args:
        ImageTk (ImageTk): The PIL ImageTk module.
        Image (Image): The PIL Image module.
        canvasManagePassword (tk.Canvas): The Canvas widget for the password visibility icon.
        NW (str): The anchor constant for positioning the icon.
        X (int): The X coordinate for placing the icon.
        Y (int): The Y coordinate for placing the icon.
    """
    photo = load_image(
        "app/assets/images/UI_Icons/Eye_Icon.png",
        size=(60, 40),
        canvas=canvasManagePassword,
        x=0,
        y=0,
        anchor=anchor,
    )
    canvasManagePassword.image = photo
    canvasManagePassword.place(x=X, y=Y)


def togglePasswordVisibility(
    event: tk.Event,
    canvasManagePassword: tk.Canvas,
    anchor: str,
    inputPassword: tk.Entry,
    X: int,
    Y: int,
):
    """
    Toggle the visibility of the password field and update the icon.

    Args:
        event (tk.Event): The event object from the mouse click.
        ImageTk (ImageTk): The PIL ImageTk module.
        Image (Image): The PIL Image module.
        canvasManagePassword (tk.Canvas): The Canvas widget for the password visibility icon.
        NW (str): The anchor constant for positioning the icon.
        inputPassword (tk.Entry): The Entry widget for the password.
        X (int): X position.
        Y (int): Y position.
    """
    global isPasswordVisible

    if not isPasswordVisible:
        inputPassword.config(show="")
        isPasswordVisible = True
        showPasswordIcon(canvasManagePassword, anchor, X, Y)
    else:
        inputPassword.config(show="*")
        isPasswordVisible = False
        hidePasswordIcon(canvasManagePassword, anchor, X, Y)


def manageVisibility(
    event: tk.Event,
    canvasManagePassword: tk.Canvas,
    anchor: str,
    inputPassword: tk.Entry,
    X: int,
    Y: int,
):
    """
    Manage the visibility icon based on the password field content.

    Args:
        event (tk.Event): The event object from the key release.
        ImageTk (ImageTk): The PIL ImageTk module.
        Image (Image): The PIL Image module.
        canvasManagePassword (tk.Canvas): The Canvas widget for the password visibility icon.
        NW (str): The anchor constant for positioning the icon.
        inputPassword (tk.Entry): The Entry widget for the password.
        X (int): X position.
        Y (int): Y position.
    """
    if inputPassword.get() != "":
        if not isPasswordVisible:
            hidePasswordIcon(canvasManagePassword, anchor, X, Y)
        if isPasswordVisible:
            showPasswordIcon(canvasManagePassword, anchor, X, Y)
    else:
        canvasManagePassword.place_forget()


def on_enter(event: tk.Event, label: tk.Label):
    """
    Underline the label font on mouse enter.

    Args:
        event (tk.Event): The event object from the mouse entering the label.
        label (tk.Label): The label widget to underline.
    """
    label.config(font=quickSandRegularUnderline(12))


def on_leave(event: tk.Event, label: tk.Label):
    """
    Remove underline from the label font on mouse leave.

    Args:
        event (tk.Event): The event object from the mouse leaving the label.
        label (tk.Label): The label widget to remove underline from.
    """
    label.config(font=quickSandRegular(12))
