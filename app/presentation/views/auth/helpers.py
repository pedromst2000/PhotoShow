import tkinter as tk
from typing import Callable, Optional


def trigger_check_login(
    check_fn: Callable[[str, str, tk.Toplevel, tk.Tk], None],
    input_email: tk.Entry,
    input_password: tk.Entry,
    login_win: tk.Toplevel,
    main_window: tk.Tk,
) -> Callable[[Optional[tk.Event]], None]:
    """
    Return an event handler that calls `check_fn` with current input values.

    This is kept free of imports from the view module so it can be imported
    without creating circular dependencies. Callers should pass the view's
    `checkLogin` function as `check_fn`.

    Args:
        check_fn: The function to call with the email, password, login window, and main window.
        input_email: The Entry widget for the email input.
        input_password: The Entry widget for the password input.
        login_win: The Toplevel window for the login view.
        main_window: The main application window.

    Returns:
        A function that can be used as an event handler for login actions.

    """

    def handler(event: Optional[tk.Event] = None) -> None:
        check_fn(input_email.get(), input_password.get(), login_win, main_window)

    return handler


def auth_switch_label(
    text: str,
    parent: tk.Misc,
    x: int,
    y: int,
    click_handler: Callable[..., None],
    *click_args,
) -> tk.Label:
    """
    Create a clickable auth-switch label (e.g. "Don't have an account? Sign up!").

    Binds hover enter/leave effects and the provided click handler. The
    click_handler is called as `click_handler(event, *click_args)` when the
    label is clicked.

    Args:
        text: The text to display on the label.
        parent: The parent widget to place the label on.
        x: The x-coordinate for placing the label.
        y: The y-coordinate for placing the label.
        click_handler: The function to call when the label is clicked. It should accept an event as its first argument, followed by any additional arguments provided in `click_args`.
        *click_args: Additional arguments to pass to the click handler when the label is clicked.

    Returns:
        The created `tk.Label` widget.
    """

    # Defer heavy imports to avoid module-level side-effects / circular refs
    from app.presentation.styles.colors import colors
    from app.presentation.styles.fonts import quickSandRegular
    from app.presentation.widgets.helpers.auth_icons import on_enter as label_on_enter
    from app.presentation.widgets.helpers.auth_icons import on_leave as label_on_leave

    label = tk.Label(
        parent,
        text=text,
        font=quickSandRegular(12),
        bd=0,
        bg=colors["primary-50"],
        highlightthickness=0,
        fg=colors["secondary-500"],
        cursor="hand2",
    )
    label.place(x=x, y=y)
    label.bind("<Enter>", lambda event: label_on_enter(event, label))
    label.bind("<Leave>", lambda event: label_on_leave(event, label))
    label.bind("<Button-1>", lambda event: click_handler(event, *click_args))
    return label
