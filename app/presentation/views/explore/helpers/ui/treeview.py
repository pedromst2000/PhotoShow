import tkinter as tk

from app.presentation.views.explore.helpers.data.state import ExploreState
from app.presentation.views.explore.helpers.ui.preview import (
    reset_preview,
    update_preview,
)


def on_treeview_select(event: tk.Event, state: ExploreState) -> None:
    """
    Handle treeview selection change. Navigate to correct page if needed, then update preview.

    Args:
        event: Tkinter event object from treeview selection
        state: ExploreState containing tree reference and pagination info
    """
    tree = state.tree
    if tree is None:
        return
    sel = tree.selection()
    if not sel or sel[0] == "empty":
        state.selected_index = None
        reset_preview(state)
        return
    try:
        local_idx = int(sel[0])
        # Convert local page index to global photo index using the mapping
        global_idx = state._tree_id_to_global_idx.get(str(local_idx), local_idx)

        # Determine which page this item is on
        page_size = state.items_per_page
        target_page = global_idx // page_size + 1

        # Navigate to that page if needed (and refresh everything)
        if target_page != state.current_page:
            state.current_page = target_page
            # Refresh entire UI (loads new page items, updates buttons, etc.)
            if state._pagination_ui_controller:
                state._pagination_ui_controller.refresh_ui()
            # Note: refresh_ui() already called refresh_treeview(), so tree is updated

        # Set LOCAL index for current page (always 0-9)
        state.selected_index = local_idx
    except (ValueError, KeyError, AttributeError):
        state.selected_index = None
        reset_preview(state)
        return
    update_preview(state)
