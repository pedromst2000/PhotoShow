import tkinter as tk
import tkinter.messagebox as messagebox

from app.core.state.session import session
from app.presentation.layout.menu.Menu import Menu
from app.presentation.styles.colors import colors
from app.presentation.widgets.helpers.window import load_image
from app.presentation.widgets.window import create_main_window


def homeWindow() -> None:
    """Create and show the home window."""
    home_window: tk.Tk = create_main_window(
        title="PhotoShow - Home",
        width=1350,
        height=700,
        icon_path="app/assets/PhotoShowIcon.ico",
        bg_color=colors["primary-50"],
    )

    home_canvas: tk.Canvas = tk.Canvas(home_window, width=1350, height=700)
    home_canvas.place(x=0, y=0)

    # main background (fills the canvas)
    bg_photo = load_image(
        "app/assets/images/main_background.png",
        size=(1350, 700),
        canvas=home_canvas,
        x=0,
        y=0,
    )

    # menu background centered on the canvas
    menu_photo = load_image(
        "app/assets/images/home/menu/backgroundMenu.png",
        size=(1145, 396),
        canvas=home_canvas,
        center=True,
    )

    # logo
    logo_photo = load_image(
        "app/assets/images/Logo.png", size=(306, 65), canvas=home_canvas, x=522, y=180
    )

    # keep references to PhotoImage objects to prevent garbage collection
    home_window._images = (bg_photo, menu_photo, logo_photo)

    # MENU - Render based on user role
    menu_instance: Menu = Menu(homeCanvas=home_canvas, homeWindow=home_window)

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

    menu_instance.render()

    home_window.mainloop()
