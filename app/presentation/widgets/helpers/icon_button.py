import tkinter as tk
from typing import Any, Optional

from app.presentation.styles.fonts import quickSandBold
from app.presentation.widgets.helpers.button import on_enter as button_on_enter
from app.presentation.widgets.helpers.button import on_leave as button_on_leave
from app.presentation.widgets.helpers.icon_label import add_icon_canvas

_ICON_DIR = "app/assets/images/UI_Icons/"


def load_btn_icon(parent: tk.Widget, state, icon_path: str) -> Any:
    """
    Load a button icon, keeping its reference alive via *state._btn_icon_refs*.

    Args:
        parent: Any widget — used only as the hidden holder's parent so the
                canvas is never garbage-collected before the window closes.
        state:  Any state object; must support a ``_btn_icon_refs`` list attr.
        icon_path: Full path to the icon image file.

    Returns:
        PhotoImage ready to be passed to ``tk.Button(image=…)``.
    """
    holder = tk.Frame(parent)  # Never packed — exists only to keep refs alive.
    canvas = add_icon_canvas(
        f"btn_icon_{id(icon_path)}",
        holder,
        icon_path,
        icon_pos=(0, 0),
        icon_size=(16, 16),
        canvas_size=(16, 16),
        visible=False,
    )
    icon = canvas.image
    if not hasattr(state, "_btn_icon_refs"):
        state._btn_icon_refs = []
    state._btn_icon_refs.append(icon)
    return icon


def make_icon_button(
    parent: tk.Frame,
    label: str,
    command,
    btn_bg: str,
    btn_fg: str,
    icon=None,
    like_icon: Optional[Any] = None,
    unlike_icon: Optional[Any] = None,
) -> tk.Button:
    """
    Create a flat icon button with hover effects.

    Args:
        parent:     Parent frame.
        label:      Button text.
        command:    Callable invoked on click.
        btn_bg:     Button background colour.
        btn_fg:     Button foreground colour.
        icon:       Pre-loaded PhotoImage for default icon.
        like_icon:  Pre-loaded like icon (toggleable buttons only).
        unlike_icon: Pre-loaded unlike icon (toggleable buttons only).

    Returns:
        Configured ``tk.Button`` (disabled by default; caller enables as needed).
    """
    btn = tk.Button(
        parent,
        text=label,
        image=icon,
        compound=tk.LEFT,
        font=quickSandBold(10),
        bg=btn_bg,
        fg=btn_fg,
        activebackground=btn_bg,
        activeforeground=btn_fg,
        borderwidth=0,
        highlightthickness=0,
        cursor="hand2",
        relief="flat",
        padx=8,
        pady=5,
        state=tk.DISABLED,
        command=command,
    )
    btn.image = icon

    if like_icon and unlike_icon:
        btn._like_icon = like_icon
        btn._unlike_icon = unlike_icon

    btn.bind("<Enter>", lambda e: button_on_enter(e, btn))
    btn.bind("<Leave>", lambda e: button_on_leave(e, btn))

    return btn
