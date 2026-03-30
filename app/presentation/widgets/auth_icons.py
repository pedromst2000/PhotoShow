import tkinter as tk

from PIL import Image, ImageTk

from app.presentation.styles.fonts import quickSandRegular, quickSandRegularUnderline

isPasswordVisible: bool = False


def hidePasswordIcon(
    ImageTk: ImageTk,
    Image: Image,
    canvasManagePassword: tk.Canvas,
    NW: str,
    X: int,
    Y: int,
):
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
    eye: Image.Image = Image.open("app/assets/images/UI_Icons/Hide_Eye_Icon.png")
    eye = eye.resize((60, 40))
    canvasManagePassword.image = ImageTk.PhotoImage(eye)
    canvasManagePassword.create_image(0, 0, anchor=NW, image=canvasManagePassword.image)
    canvasManagePassword.place(x=X, y=Y)


def showPasswordIcon(
    ImageTk: ImageTk,
    Image: Image,
    canvasManagePassword: tk.Canvas,
    NW: str,
    X: int,
    Y: int,
):
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
    eye: Image.Image = Image.open("app/assets/images/UI_Icons/Eye_Icon.png")
    eye = eye.resize((60, 40))
    canvasManagePassword.image = ImageTk.PhotoImage(eye)
    canvasManagePassword.create_image(0, 0, anchor=NW, image=canvasManagePassword.image)
    canvasManagePassword.place(x=X, y=Y)


def togglePasswordVisibility(
    event: tk.Event,
    ImageTk: ImageTk,
    Image: Image,
    canvasManagePassword: tk.Canvas,
    NW: str,
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
        showPasswordIcon(ImageTk, Image, canvasManagePassword, NW, X, Y)
    else:
        inputPassword.config(show="*")
        isPasswordVisible = False
        hidePasswordIcon(ImageTk, Image, canvasManagePassword, NW, X, Y)


def manageVisibility(
    event: tk.Event,
    ImageTk: ImageTk,
    Image: Image,
    canvasManagePassword: tk.Canvas,
    NW: str,
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
            hidePasswordIcon(ImageTk, Image, canvasManagePassword, NW, X, Y)
        if isPasswordVisible:
            showPasswordIcon(ImageTk, Image, canvasManagePassword, NW, X, Y)
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
