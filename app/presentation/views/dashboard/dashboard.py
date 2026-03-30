import tkinter as tk

from app.presentation.styles.colors import colors

# Todo - Change the size of the window


def dashboardWindow():
    """
    Display the main dashboard window of the application.
    """

    # open the window
    _dashboardWindow_: tk.Toplevel = tk.Toplevel()

    # centering the window
    dashboardWindowWidth: int = 573  # width of the window
    dashboardWindowHeight: int = 580  # height of the window

    screenWidth: int = _dashboardWindow_.winfo_screenwidth()  # width of the screen

    screenHeight: int = _dashboardWindow_.winfo_screenheight()  # height of the screen

    x: float = (screenWidth / 2) - (dashboardWindowWidth / 2)  # calculate x position

    y: float = (screenHeight / 2) - (dashboardWindowHeight / 2)  # calculate y position

    # setting the window size and position
    # %d = integer
    # %dx%d = width x height
    # %d+%d = x position + y position
    _dashboardWindow_.geometry(
        "%dx%d+%d+%d" % (dashboardWindowWidth, dashboardWindowHeight, x, y)
    )
    _dashboardWindow_.title("📈 Dashboard 📈")
    _dashboardWindow_.iconbitmap("app/assets/PhotoShowIcon.ico")
    _dashboardWindow_.resizable(0, 0)
    _dashboardWindow_.config(bg=colors["primary-50"])

    _dashboardWindow_.grab_set()
