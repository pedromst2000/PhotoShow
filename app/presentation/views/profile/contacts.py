from app.presentation.styles.theme import LIST_BG
from app.presentation.views.profile.helpers.data.contacts_data import load_contacts
from app.presentation.views.profile.helpers.data.contacts_state import ContactsState
from app.presentation.views.profile.helpers.ui.contacts_builder import (
    _WIN_H,
    _WIN_W,
    build_contacts_body,
    build_contacts_header,
)
from app.presentation.widgets.window import create_toplevel


def contactsWindow() -> None:
    """Display the admin contacts window.

    This window is only accessible to admin users and shows all contact messages sent by users.
    """
    win = create_toplevel(
        title="\U0001f4ec Contacts",
        width=_WIN_W,
        height=_WIN_H,
        icon_path="app/assets/PhotoShowIcon.ico",
        bg_color=LIST_BG,
    )

    state = ContactsState()
    state.win = win

    load_contacts(state)
    build_contacts_header(win, state)
    build_contacts_body(win, state)

    win.grab_set()
