import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox
from typing import Any, Callable

from app.controllers.profile_controller import ProfileController
from app.core.state.session import session
from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold, quickSandRegular
from app.presentation.widgets.helpers.button import on_enter as button_on_enter
from app.presentation.widgets.helpers.button import on_leave as button_on_leave
from app.presentation.widgets.helpers.window import load_image
from app.presentation.widgets.window import create_toplevel

image: Any = ""
photo_image: Any = ""
statusBtn = "disabled"
cursorBtn = "arrow"


def uploadAvatar(
    event: Callable[..., Any],
    canvasAvatar: tk.Canvas,
    btnSaveAvatar: tk.Button,
    userID: int,
):
    """
    This function is used to upload the avatar.

    Args:
        event (callable): The event object from the button click.
        canvasAvatar (tk.Canvas): The Canvas widget to display the avatar preview.
        btnSaveAvatar (tk.Button): The Button widget to save the avatar.
        userID (int): The ID of the user whose avatar is being changed.
    """

    global image, photo_image, statusBtn, cursorBtn

    # open the file dialog
    filename: str = filedialog.askopenfilename(
        initialdir="/",
        title="Select an image",
        filetypes=(
            ("png files", "*.png"),
            ("jpg files", "*.jpg"),
            ("jpeg files", "*.jpeg"),
        ),
    )

    if filename == "":
        return

    if filename != "":
        image_path = filename

        photo_image = load_image(
            image_path, size=(200, 200), canvas=canvasAvatar, x=0, y=0
        )
        image = image_path  # assigning the global variable image to the image_path
        canvasAvatar.image = photo_image  # type: ignore
        statusBtn = "normal"
        cursorBtn = "hand2"
        btnSaveAvatar["state"] = statusBtn
        btnSaveAvatar["cursor"] = cursorBtn
        btnSaveAvatar.bind("<Enter>", lambda e: button_on_enter(e, btnSaveAvatar))
        btnSaveAvatar.bind("<Leave>", lambda e: button_on_leave(e, btnSaveAvatar))
        btnSaveAvatar.bind("<Button-1>", lambda event: _saveAvatar_(event, image_path))


def _saveAvatar_(event: Callable[..., Any], avatar: str):
    """
    This function is used to save the avatar.

    Args:
        event (callable): The event object from the button click.
        avatar (str): The file path of the new avatar image.

    """

    # slicing the path to get only the image name
    avatar_filename: str = avatar.split("/")[-1]

    success, message = ProfileController.update_avatar(avatar_filename)

    if success:
        ProfileController.refresh_session_data()
        messagebox.showinfo("Success", message)
    else:
        messagebox.showerror("Error", message)


def changeAvatarWindow():
    """
    This function is used to display change avatar window.
    """

    # create the window using the reusable helper
    userID: int = session.user_id

    _changeAvatarWindow_: tk.Toplevel = create_toplevel(
        title="👤 Profile - Change Avatar 👤",
        width=500,
        height=595,
        icon_path="app/assets/PhotoShowIcon.ico",
        bg_color=colors["primary-50"],
    )

    # ----------------------  Labels -----------------------------------

    changeAvatarLabel: tk.Label = tk.Label(
        _changeAvatarWindow_,
        text="Change Avatar",
        font=quickSandBold(22),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )

    changeAvatarLabel.place(x=140, y=15)

    helpLabel: tk.Label = tk.Label(
        _changeAvatarWindow_,
        text="Select a new avatar for your profile",
        font=quickSandRegular(12),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    )

    helpLabel.place(x=125, y=70)

    # ----------------------  Buttons -----------------------------------

    btnChangeAvatar: tk.Button = tk.Button(
        _changeAvatarWindow_,
        width=16,
        height=2,
        text="Upload Avatar",
        borderwidth=10,
        font=quickSandBold(12),
        fg=colors["secondary-500"],
        background=colors["accent-300"],
        highlightthickness=0,
        activebackground=colors["accent-100"],
        cursor="hand2",
        compound="center",
        border=0,
    )

    btnChangeAvatar.place(x=170, y=380)

    btnSaveAvatar: tk.Button = tk.Button(
        _changeAvatarWindow_,
        width=16,
        height=2,
        state=statusBtn,
        text="Save Avatar",
        borderwidth=10,
        font=quickSandBold(12),
        fg=colors["secondary-500"],
        background=colors["accent-300"],
        highlightthickness=0,
        activebackground=colors["accent-100"],
        cursor=cursorBtn,
        compound="center",
        border=0,
    )

    btnSaveAvatar.place(x=170, y=470)

    # ----------------------  Preeview Avatar -----------------------------------

    canvasPreeviewAvatar: tk.Canvas = tk.Canvas(
        _changeAvatarWindow_,
        width=200,
        height=200,
        bg=colors["primary-50"],
        highlightthickness=0,
    )

    canvasPreeviewAvatar.place(x=150, y=135)

    avatar_photo = load_image(
        session.avatar, size=(200, 200), canvas=canvasPreeviewAvatar, x=0, y=0
    )
    canvasPreeviewAvatar.image = avatar_photo

    # ----------------------  Events -----------------------------------
    btnChangeAvatar.bind(
        "<Enter>", lambda event: button_on_enter(event, btnChangeAvatar)
    )
    btnChangeAvatar.bind(
        "<Leave>", lambda event: button_on_leave(event, btnChangeAvatar)
    )
    btnChangeAvatar.bind(
        "<Button-1>",
        lambda event: uploadAvatar(event, canvasPreeviewAvatar, btnSaveAvatar, userID),
    )

    _changeAvatarWindow_.grab_set()
