import tkinter as tk


def create_menu_button(canvas: tk.Canvas, img: tk.PhotoImage) -> tk.Button:
    """
    Create a styled Tkinter button for the menu.

    Args:
        canvas (tk.Canvas): The Canvas where the button will be placed.
        img (tk.PhotoImage): The image to display on the button.

    Returns:
        tk.Button: A Tkinter Button widget configured with the specified image and styling.
    """
    btn = tk.Button(
        canvas,
        image=img,
        width=113,
        height=120,
        cursor="hand2",
        borderwidth=0,
        highlightthickness=0,
    )
    # Keep a Python-side reference so ImageTk.PhotoImage is not garbage-collected
    btn.image = img
    return btn
