import tkinter as tk
import tkinter.messagebox as messagebox

from PIL import Image, ImageTk

from app.core.state.session import session
from app.presentation.layout.Menu import menu
from app.presentation.styles.colors import colors
from app.presentation.widgets.window import create_main_window


def homeWindow() -> None:
    """
    This function is used to create the home window.
    """
    # create the main application window using the reusable helper
    _homeWindow_: tk.Tk = create_main_window(
        title="PhotoShow - Home",
        width=1350,
        height=700,
        icon_path="app/assets/PhotoShowIcon.ico",
        bg_color=colors["primary-50"],
    )

    homeCanvas: tk.Canvas = tk.Canvas(_homeWindow_, width=1350, height=700)
    homeCanvas.place(x=0, y=0)

    homeImage: Image.Image = Image.open("app/assets/images/main_background.png")
    homeImage = homeImage.resize((1350, 700))

    homeImageTk: ImageTk.PhotoImage = ImageTk.PhotoImage(homeImage)

    homeCanvas.create_image(0, 0, image=homeImageTk, anchor=tk.NW)

    backgroundMenu: Image.Image = Image.open(
        "app/assets/images/home/menu/backgroundMenu.png"
    )
    backgroundMenu = backgroundMenu.resize((1145, 396))

    backgroundMenuTk: ImageTk.PhotoImage = ImageTk.PhotoImage(backgroundMenu)

    # centering the image on the canvas
    x: int = (1350 - 1145) // 2
    y: int = (700 - 396) // 2

    homeCanvas.create_image(x, y, image=backgroundMenuTk, anchor=tk.NW)

    logoImage: Image.Image = Image.open("app/assets/images/Logo.png")
    logoImage = logoImage.resize((306, 65))

    logoImageTk: ImageTk.PhotoImage = ImageTk.PhotoImage(logoImage)
    homeCanvas.create_image(522, 180, image=logoImageTk, anchor=tk.NW)

    # keep references to PhotoImage objects to prevent garbage collection
    _homeWindow_._images = (homeImageTk, backgroundMenuTk, logoImageTk)

    _menu_: menu = menu(homeCanvas=homeCanvas, homeWindow=_homeWindow_)

    if session.is_new_user:
        messagebox.showinfo(
            "Welcome to PhotoShow!",
            "Where every pixel tells a tale, you can now enjoy your time with us.\n\n"
            "Let's take a look at our features:\n\n"
            "  - \U0001f310 Explore: Explore the world of photos with other users\n\n"
            "  - \U0001f464 Profile: Edit your profile and view your photos and albums\n\n"
            "  - \U0001f514 Notifications: Stay updated with news through notifications\n\n"
            "  - \U0001f4c8 Dashboard: Check your dashboard for statistics",
        )

    if session.is_admin:
        _menu_.adminMenu()
    elif session.is_authenticated:
        _menu_.regularMenu()

    _homeWindow_.mainloop()
