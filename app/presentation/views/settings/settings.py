import tkinter as tk

from app.presentation.styles.colors import colors

# Todo - Change the size of the window


def settingsWindow():
    """
    Display the settings window for user preferences and configuration.

    :return: None
    """
    # open the window
    _settingsWindow_: tk.Toplevel = tk.Toplevel()

    # centering the window
    settingsWindowWidth: int = 573  # width of the window
    settingsWindowHeight: int = 580  # height of the window

    screenWidth: int = _settingsWindow_.winfo_screenwidth()  # width of the screen

    screenHeight: int = _settingsWindow_.winfo_screenheight()  # height of the screen

    x: float = (screenWidth / 2) - (settingsWindowWidth / 2)  # calculate x position

    y: float = (screenHeight / 2) - (settingsWindowHeight / 2)  # calculate y position

    # setting the window size and position
    # %d = integer
    # %dx%d = width x height
    # %d+%d = x position + y position
    _settingsWindow_.geometry(
        "%dx%d+%d+%d" % (settingsWindowWidth, settingsWindowHeight, x, y)
    )
    _settingsWindow_.title("⚙️ Settings ⚙️")
    _settingsWindow_.iconbitmap("app/assets/PhotoShowIcon.ico")
    _settingsWindow_.resizable(0, 0)
    _settingsWindow_.config(bg=colors["primary-50"])

    _settingsWindow_.grab_set()
