from app.presentation.views.helpers.data.pagination import PaginationManager
from app.presentation.views.helpers.data.state import BasePhotoState
from app.presentation.views.helpers.ui.preview import update_preview


def navigate_prev(state: BasePhotoState):
    """
    Move to the previous photo, or go to previous page if at start.

    Args:
        state: BasePhotoState object containing current photos and selection index.
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


def navigate_next(state: BasePhotoState):
    """
    Move to the next photo, or go to next page if at the end of current page.

    Args:
        state: BasePhotoState object containing current photos and selection index.
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


def _sync_tree_selection(state: BasePhotoState, skip_scroll: bool = False):
    """
    Sync treeview selection with carousel position (local index only, current page).
    Uses PaginationManager for pagination awareness.

    Args:
        state: BasePhotoState object containing current photos and selection index.
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


def _sync_listbox_selection(state: BasePhotoState) -> None:
    """
    Sync the PhotoListboxWidget selection to match state.selected_index.

    Used by listbox-based views (album details, profile) to keep the
    left-panel listbox in sync with carousel navigation.

    Args:
        state: BasePhotoState subclass that exposes a ``listbox_widget`` attribute.
    """
    widget = getattr(state, "listbox_widget", None)
    if widget is None or state.selected_index is None:
        return
    lb = getattr(widget, "_listbox", None)
    if lb is None:
        return
    lb.selection_clear(0, "end")
    lb.selection_set(state.selected_index)
    lb.see(state.selected_index)


def listbox_navigate_prev(state: BasePhotoState) -> None:
    """
    Move to the previous photo and sync the listbox widget selection.

    Suitable for listbox-based views (album details, profile) where
    navigation arrows should keep the side-panel listbox in sync.

    Args:
        state: BasePhotoState subclass with a ``listbox_widget`` attribute.
    """
    navigate_prev(state)
    _sync_listbox_selection(state)


def listbox_navigate_next(state: BasePhotoState) -> None:
    """
    Move to the next photo and sync the listbox widget selection.

    Suitable for listbox-based views (album details, profile) where
    navigation arrows should keep the side-panel listbox in sync.

    Args:
        state: BasePhotoState subclass with a ``listbox_widget`` attribute.
    """
    navigate_next(state)
    _sync_listbox_selection(state)
