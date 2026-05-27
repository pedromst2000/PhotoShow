from app.controllers.contact_controller import ContactController
from app.presentation.views.helpers.data.pagination_helpers import (
    init_list_pagination,
    refresh_listbox_ui,
)
from app.presentation.views.profile.helpers.data.contacts_state import ContactsState
from app.utils.log_utils import log_exception

_CONTACTS_PER_PAGE = 8


def load_contacts(state: ContactsState) -> bool:
    """
    Load all enriched contact messages into *state* and initialise pagination.

    Populates ``all_contacts`` with the full list and sets up the pagination
    state so the listbox can display the first page.

    Args:
        state: The ``ContactsState`` instance to populate.

    Returns:
        bool: True on success, False on unexpected error.
    """
    try:
        contacts = ContactController.get_all_enriched()
        state.all_contacts = contacts
        init_list_pagination(state, contacts, _CONTACTS_PER_PAGE)
        return True
    except Exception as e:
        log_exception("contacts.load_contacts", e)
        return False


def refresh_contacts_list(state: ContactsState) -> None:
    """
    Reload all contacts from the controller and reinitialise pagination.

    Used after resolving a contact so the left listbox reflects the current
    DB state without reopening the window.

    Args:
        state: The ``ContactsState`` instance.
    """
    try:
        contacts = ContactController.get_all_enriched()
        state.all_contacts = contacts
        init_list_pagination(state, contacts, _CONTACTS_PER_PAGE)
        refresh_listbox_ui(state)
    except Exception as e:
        log_exception("contacts.refresh_contacts_list", e)
