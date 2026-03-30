import tkinter as tk

from app.presentation.styles.colors import colors

# Todo - Change the size of the window


def notificationsWindow():
    """
    This function is used to display the notifications window.
    """

    # open the window
    _notificationsWindow_: tk.Toplevel = tk.Toplevel()

    # centering the window
    notificationsWindowWidth: int = 573  # width of the window
    notificationsWindowHeight: int = 580  # height of the window

    screenWidth: int = _notificationsWindow_.winfo_screenwidth()  # width of the screen

    screenHeight: int = (
        _notificationsWindow_.winfo_screenheight()
    )  # height of the screen

    x: float = (screenWidth / 2) - (
        notificationsWindowWidth / 2
    )  # calculate x position

    y: float = (screenHeight / 2) - (
        notificationsWindowHeight / 2
    )  # calculate y position

    # setting the window size and position
    # %d = integer
    # %dx%d = width x height
    # %d+%d = x position + y position
    _notificationsWindow_.geometry(
        "%dx%d+%d+%d" % (notificationsWindowWidth, notificationsWindowHeight, x, y)
    )
    _notificationsWindow_.title("🔔 Notifications 🔔")
    _notificationsWindow_.iconbitmap("app/assets/PhotoShowIcon.ico")
    _notificationsWindow_.resizable(0, 0)
    _notificationsWindow_.config(bg=colors["primary-50"])

    _notificationsWindow_.grab_set()
