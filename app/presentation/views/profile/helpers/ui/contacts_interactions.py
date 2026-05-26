import tkinter as tk

from app.controllers.contact_controller import ContactController
from app.presentation.views.helpers.ui.builder import toggle_empty_content_state
from app.presentation.views.profile.helpers.data.contacts_data import (
    refresh_contacts_list,
)
from app.presentation.views.profile.helpers.data.contacts_state import ContactsState
from app.presentation.widgets.helpers.ui_dialogs import (
    show_confirmation,
    show_error,
    show_info,
)

# ── Internal helpers ──────────────────────────────────────────────────────────


def _set_resolve_btn_state(state: ContactsState, *, enabled: bool) -> None:
    """Enable or disable the Resolve button.

    Args:
        state: Contacts state carrying the button reference.
        enabled: True to enable, False to disable.
    """
    btn = state.resolve_btn
    if btn is not None:
        btn.config(state=tk.NORMAL if enabled else tk.DISABLED)


def _reset_detail_panel(state: ContactsState) -> None:
    """Hide the detail frame and show the selection placeholder.

    Args:
        state: Contacts state carrying the panel widget references.
    """
    detail = state._detail_frame
    placeholder = state._placeholder_frame
    if detail is not None:
        detail.pack_forget()
    if placeholder is not None:
        placeholder.pack(fill="both", expand=True)


def _update_detail_panel(state: ContactsState) -> None:
    """Populate and reveal the detail panel for the selected contact.

    Args:
        state: Contacts state carrying the panel widget references and
               ``selected_contact`` dict.
    """
    contact = state.selected_contact
    if contact is None:
        return

    # Update label / text widget contents.
    author_lbl = state._author_label
    title_lbl = state._title_label
    msg_text = state._message_text

    if author_lbl is not None:
        author_lbl.config(text=contact.get("username", "Unknown"))
    if title_lbl is not None:
        title_lbl.config(text=contact.get("title", "—"))
    if msg_text is not None:
        msg_text.config(state=tk.NORMAL)
        msg_text.delete("1.0", tk.END)
        msg_text.insert("1.0", contact.get("message", ""))
        msg_text.config(state=tk.DISABLED)

    # Swap placeholder ↔ detail frame.
    placeholder = state._placeholder_frame
    detail = state._detail_frame
    if placeholder is not None:
        placeholder.pack_forget()
    if detail is not None:
        detail.pack(fill="both", expand=True)


# ── Contact selection ─────────────────────────────────────────────────────────


def on_contact_select(idx: int, state: ContactsState) -> None:
    """Handle selection of a contact in the left listbox.

    Updates the detail panel on the right to show the selected contact's
    author, title, and message.

    Args:
        idx: Local page index of the selected contact.
        state: Contacts view state.
    """
    contacts_on_page = state.photos
    if not (0 <= idx < len(contacts_on_page)):
        return

    state.selected_index = idx
    state.selected_contact = contacts_on_page[idx]

    _set_resolve_btn_state(state, enabled=True)
    _update_detail_panel(state)


# ── Resolve contact ───────────────────────────────────────────────────────────


def on_resolve_contact(state: ContactsState, body: tk.Widget) -> None:
    """Mark the selected contact message as resolved (delete it).

    Prompts the admin for confirmation before permanently removing the
    contact from the database and refreshing the listbox.

    Args:
        state: Contacts view state.
        body: Parent widget used for confirmation / info dialogs.
    """
    if state.selected_contact is None:
        show_info(body, "Mark as Resolved", "Please select a contact message first.")
        return

    title = state.selected_contact.get("title", "this message")
    contact_id = state.selected_contact.get("id")

    confirmed = show_confirmation(
        body,
        "Mark as Resolved",
        f'Mark "{title}" as resolved?\n\nThe message will be permanently removed.',
    )
    if not confirmed:
        return

    success, msg = ContactController.resolve(contact_id)
    if success:
        state.selected_contact = None
        state.selected_index = None
        _set_resolve_btn_state(state, enabled=False)
        _reset_detail_panel(state)
        refresh_contacts_list(state)
        toggle_empty_content_state(state, has_items=bool(state.all_contacts))
        show_info(body, "Mark as Resolved", "Contact message resolved successfully.")
    else:
        show_error(body, "Mark as Resolved", msg)
