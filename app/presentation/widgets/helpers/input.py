import tkinter as tk
from typing import Optional

from app.presentation.styles.colors import colors

# Module-scoped state used by the input helpers
last_focused_input: Optional[tk.Entry] = None


def on_focus_in(event: tk.Event, input: tk.Entry) -> None:
    """
    Change styling when an input receives focus.

    Args:
        event (tk.Event): The focus event.
        input (tk.Entry): The Entry widget.
    """

    input["background"] = colors["secondary-500"]
    input["fg"] = colors["primary-50"]
    input.config(insertbackground=colors["primary-50"])


def on_focus_out(event: tk.Event, input: tk.Entry) -> None:
    """
    Restore styling when an input loses focus.

    Args:
        event (tk.Event): The focus event.
        input (tk.Entry): The Entry widget.
    """

    input["background"] = colors["secondary-300"]
    input["fg"] = colors["secondary-500"]
    input.config(insertbackground=colors["secondary-500"])


def on_click_outside(event: tk.Event, window: tk.Tk, *input_fields: tk.Entry) -> None:
    """
    If a click occurs outside the provided input fields, move focus to the
    given window (clearing focus from the inputs). Tracks the last focused
    input in `last_focused_input`.

    Args:
        event (tk.Event): The click event.
        window (tk.Tk): The window to focus if click outside inputs.
        *input_fields (tk.Entry): Entry widgets to consider as "inside" clicks.
    """

    global last_focused_input
    for input_field in input_fields:
        if input_field.winfo_containing(event.x_root, event.y_root) == input_field:
            last_focused_input = input_field
            return
    window.focus_set()
