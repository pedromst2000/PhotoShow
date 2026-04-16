from app.presentation.views.explore.helpers.data.pagination import PaginationManager
from app.presentation.views.explore.helpers.data.state import ExploreState
from app.presentation.views.explore.helpers.ui.preview import update_preview


def navigate_prev(state: ExploreState):
    """
    Move to the previous photo, or go to previous page if at start.

    Args:
        state: ExploreState object containing current photos and selection index.
    """
    if not state.photos:
        return

    total = len(state.photos)

    if state.selected_index is None:
        # At start of page - go to previous page if available
        if PaginationManager.can_go_prev(state):
            PaginationManager.go_to_prev_page(state)
            if state._pagination_ui_controller:
                state._pagination_ui_controller.refresh_ui()
            state.selected_index = total - 1  # Go to last item of new page
        else:
            state.selected_index = total - 1  # Wrap to end of current page
    elif state.selected_index <= 0:
        # At start of page - go to previous page if available
        if PaginationManager.can_go_prev(state):
            PaginationManager.go_to_prev_page(state)
            if state._pagination_ui_controller:
                state._pagination_ui_controller.refresh_ui()
            state.selected_index = total - 1  # Go to last item of new page
        else:
            state.selected_index = total - 1  # Wrap to end of current page
    else:
        state.selected_index -= 1

    _sync_tree_selection(state, skip_scroll=True)
    update_preview(state)


def navigate_next(state: ExploreState):
    """
    Move to the next photo, or go to next page if at the end of current page.

    Args:
        state: ExploreState object containing current photos and selection index.
    """
    if not state.photos:
        return

    total = len(state.photos)

    if state.selected_index is None:
        state.selected_index = 0
    elif state.selected_index >= total - 1:
        # At end of page - go to next page if available
        if PaginationManager.can_go_next(state):
            PaginationManager.go_to_next_page(state)
            if state._pagination_ui_controller:
                state._pagination_ui_controller.refresh_ui()
            state.selected_index = 0  # Go to first item of new page
        else:
            state.selected_index = (
                0  # Wrap to start of current page (only if no next page)
            )
    else:
        state.selected_index += 1

    _sync_tree_selection(state, skip_scroll=True)
    update_preview(state)


def _sync_tree_selection(state: ExploreState, skip_scroll: bool = False):
    """
    Sync treeview selection with carousel position (local index only, current page).
    Uses PaginationManager for pagination awareness.

    Args:
        state: ExploreState object containing current photos and selection index.
        skip_scroll: If True, skip tree.see() for fast carousel navigation; if False, scroll to item.
    """
    tree = state.tree
    if tree is None or state.selected_index is None:
        return

    # state.selected_index is LOCAL index within current page (0-9)
    local_idx = state.selected_index
    iid = str(local_idx)

    try:
        tree.selection_set(iid)
        if not skip_scroll:
            tree.see(iid)
    except Exception:
        pass  # Item not found on current page, ignore
