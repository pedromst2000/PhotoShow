from app.controllers.contact_controller import ContactController
from app.presentation.views.helpers.data.pagination import PaginationManager
from app.presentation.views.profile.helpers.data.contacts_state import ContactsState
from app.utils.log_utils import log_exception

_CONTACTS_PER_PAGE = 8


def _get_page_slice(items: list, page_num: int, per_page: int) -> list:
    """
    Return the slice of *items* that belongs to *page_num*.

    Args:
        items: The full list of items to paginate.
        page_num: The 1-based page number to retrieve.
        per_page: The number of items per page.
    Returns:
        list: The slice of items for the requested page.
    """
    start = (page_num - 1) * per_page
    return items[start : start + per_page]


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

        PaginationManager.initialize_pagination(
            state,  # type: ignore[arg-type]
            items_per_page=_CONTACTS_PER_PAGE,
            data_provider=lambda p: _get_page_slice(contacts, p, _CONTACTS_PER_PAGE),
            total_items=len(contacts),
        )
        state.photos = PaginationManager.get_paginated_items(state)  # type: ignore[arg-type]
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

        PaginationManager.initialize_pagination(
            state,  # type: ignore[arg-type]
            items_per_page=_CONTACTS_PER_PAGE,
            data_provider=lambda p: _get_page_slice(contacts, p, _CONTACTS_PER_PAGE),
            total_items=len(contacts),
        )
        state.photos = PaginationManager.get_paginated_items(state)  # type: ignore[arg-type]

        widget = getattr(state, "listbox_widget", None)
        if widget is not None:
            selected_id = None
            if state.selected_contact is not None:
                selected_id = state.selected_contact.get("id")
            widget.refresh(state.photos, selected_item_id=selected_id)

        ctrl = getattr(state, "_pagination_ui_controller", None)
        if ctrl is not None:
            ctrl.refresh_ui()
    except Exception as e:
        log_exception("contacts.refresh_contacts_list", e)
