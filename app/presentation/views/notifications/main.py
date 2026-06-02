import tkinter as tk

from app.presentation.styles.colors import colors
from app.presentation.styles.theme import PAGE_BG
from app.presentation.views.notifications.helpers.data.notification_data import (
    load_notifications,
)
from app.presentation.views.notifications.helpers.data.state import NotificationState
from app.presentation.views.notifications.helpers.ui.builder import (
    build_notification_body,
    build_notification_header,
)
from app.presentation.views.notifications.helpers.ui.interactions import (
    on_mark_all_read,
    on_mark_read,
)
from app.presentation.widgets.window import create_toplevel


def notificationsWindow() -> None:
    """Open the Notifications window (modal Toplevel).

    Loads unread notifications, renders the list + detail panel,
    and wires the 'Mark as Read' / 'Mark All Read' buttons.
    """
    state = NotificationState()
    load_notifications(state)

    win: tk.Toplevel = create_toplevel(
        title="🔔 Notifications",
        width=900,
        height=620,
        icon_path="app/assets/PhotoShowIcon.ico",
        bg_color=colors[PAGE_BG] if PAGE_BG in colors else colors["primary-50"],
    )
    state.win = win

    build_notification_header(win, state)
    build_notification_body(win, state)

    # Wire action buttons now that state has all widget refs
    if state.mark_read_btn:
        state.mark_read_btn.config(command=lambda: on_mark_read(state))
    if state.mark_all_btn:
        state.mark_all_btn.config(command=lambda: on_mark_all_read(state))

    win.grab_set()
