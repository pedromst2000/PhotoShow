import tkinter as tk

from app.presentation.styles.colors import colors

# Todo - Change the size of the window


def exploreWindow():
    """
    This function is used to create the Explore Window.
    """

    # open the window
    _exploreWindow_: tk.Toplevel = tk.Toplevel()

    # centering the window
    exploreWindowWidth: int = 573  # width of the window
    exploreWindowHeight: int = 580  # height of the window

    screenWidth: int = _exploreWindow_.winfo_screenwidth()  # width of the screen

    screenHeight: int = _exploreWindow_.winfo_screenheight()  # height of the screen

    x: float = (screenWidth / 2) - (exploreWindowWidth / 2)  # calculate x position

    y: float = (screenHeight / 2) - (exploreWindowHeight / 2)  # calculate y position

    # setting the window size and position
    # %d = integer
    # %dx%d = width x height
    # %d+%d = x position + y position
    _exploreWindow_.geometry(
        "%dx%d+%d+%d" % (exploreWindowWidth, exploreWindowHeight, x, y)
    )
    _exploreWindow_.title("🔍 Explore 🔍")
    _exploreWindow_.iconbitmap("app/assets/PhotoShowIcon.ico")
    _exploreWindow_.resizable(0, 0)
    _exploreWindow_.config(bg=colors["primary-50"])

    _exploreWindow_.grab_set()
