from typing import Any, Optional

from app.presentation.views.helpers.data.pagination import PaginationManager


def get_page_slice(items: list, page_num: int, per_page: int) -> list:
    """Return the slice of *items* that belongs to *page_num*.

    Args:
        items: The full list to paginate.
        page_num: 1-based page number.
        per_page: Number of items per page.

    Returns:
        list: The requested page slice.
    """
    start = (page_num - 1) * per_page
    return items[start : start + per_page]


def init_list_pagination(state: Any, items: list, per_page: int) -> None:
    """Initialise PaginationManager on *state* for a flat list of *items*.

    Calls ``PaginationManager.initialize_pagination`` then immediately sets
    ``state.photos`` to the first page.

    Args:
        state: View state that implements the PaginationManager interface.
        items: The full (flat) list of items to paginate.
        per_page: Number of items to show per page.
    """
    PaginationManager.initialize_pagination(
        state,  # type: ignore[arg-type]
        items_per_page=per_page,
        data_provider=lambda p: get_page_slice(items, p, per_page),
        total_items=len(items),
    )
    state.photos = PaginationManager.get_paginated_items(state)  # type: ignore[arg-type]


def refresh_listbox_ui(state: Any, *, selected_item_id: Optional[int] = None) -> None:
    """Refresh the listbox widget and pagination controller after items change.

    Safe to call when either widget is absent — uses ``getattr`` to locate
    both the listbox and the pagination UI controller.

    Args:
        state: View state with optional ``listbox_widget`` and
               ``_pagination_ui_controller`` attributes.
        selected_item_id: If provided, passed to ``listbox_widget.refresh``
                          so the listbox can preserve or restore the visual
                          selection by item ID.
    """
    widget = getattr(state, "listbox_widget", None)
    if widget is not None:
        widget.refresh(state.photos, selected_item_id=selected_item_id)

    ctrl = getattr(state, "_pagination_ui_controller", None)
    if ctrl is not None:
        ctrl.refresh_ui()
