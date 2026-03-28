import tkinter as tk

from styles.colors import colors

# Global variable
last_focused_input: tk.Entry = None


def on_focus_in(event: tk.Event, input: tk.Entry) -> None:
    """
    This function will change the background color and the foreground color of the input when the input is focused.

    Args:
        event (tk.Event): The event object.
        input (tk.Entry): The input widget.
    """

    input["background"] = colors["secondary-500"]
    input["fg"] = colors["primary-50"]
    input.config(insertbackground=colors["primary-50"])


def on_focus_out(event: tk.Event, input: tk.Entry) -> None:
    """
    This function will change the background color and the foreground color of the input when the input is not focused.

    Args:
        event (tk.Event): The event object.
        input (tk.Entry): The input widget.
    """

    input["background"] = colors["secondary-300"]
    input["fg"] = colors["secondary-500"]
    input.config(insertbackground=colors["secondary-500"])


def on_click_outside(event: tk.Event, window: tk.Tk, *input_fields: tk.Entry) -> None:
    """
    This function will change the background color and the foreground color of the input when the input is not focused.

    Args:
        event (tk.Event): The event object.
        window (tk.Tk): The window object.
        *input_fields (tk.Entry): The input fields to check if the click was outside of them.
    """

    global last_focused_input
    for input_field in input_fields:
        if input_field.winfo_containing(event.x_root, event.y_root) == input_field:
            last_focused_input = input_field
            return
    window.focus_set()
