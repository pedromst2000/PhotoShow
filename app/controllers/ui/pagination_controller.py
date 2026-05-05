from app.controllers.ui.tree_view_controller import TreeViewController
from app.presentation.views.helpers.data.pagination import PaginationManager
from app.presentation.views.helpers.data.state import BasePhotoState
from app.utils.log_utils import log_issue


class PaginationUIController:
    """
    Controller for pagination UI logic. Handles page navigation and UI refresh.
    Pagination is initialized by load_catalog() with lazy-loading.
    """

    def __init__(self, state: BasePhotoState, on_page_changed=None):
        """
        Initialize controller.

        Args:
            state: BasePhotoState object with tree reference
            on_page_changed: Optional callback when page changes
        """
        self.state = state
        self.tree_controller = TreeViewController(state)
        self.on_page_changed = on_page_changed

    def go_to_next_page(self) -> None:
        """Navigate to next page."""
        if PaginationManager.go_to_next_page(self.state):
            self.refresh_ui()
            if self.on_page_changed:
                self.on_page_changed()

    def go_to_prev_page(self) -> None:
        """Navigate to previous page."""
        if PaginationManager.go_to_prev_page(self.state):
            self.refresh_ui()
            if self.on_page_changed:
                self.on_page_changed()

    def refresh_ui(self) -> None:
        """Refresh treeview and page label."""
        try:
            # Refresh tree with current page items
            self.tree_controller.refresh_treeview()

            # Update page label (looking for both possible names)
            label = getattr(self.state, "page_label", None) or getattr(
                self.state, "page_info_label", None
            )
            if label:
                page_info = PaginationManager.get_page_info(self.state)
                label.config(text=page_info)

            # Update button states based on page limits
            total_pages = PaginationManager.get_total_pages(self.state)
            self._update_button_states(total_pages)
        except Exception as e:
            log_issue("PaginationUIController.refresh_ui failed", exc=e)

    def _update_button_states(self, total_pages: int) -> None:
        """
        Enable/disable prev/next buttons based on current page.

        Args:
            total_pages: Total number of pages
        """
        # Look for buttons by both possible names
        prev_btn = getattr(self.state, "prev_page_btn", None) or getattr(
            self.state, "prev_button", None
        )
        next_btn = getattr(self.state, "next_page_btn", None) or getattr(
            self.state, "next_button", None
        )

        if not prev_btn or not next_btn:
            return

        # Disable prev button if on first page
        if self.state.current_page <= 1:
            prev_btn.config(state="disabled")
        else:
            prev_btn.config(state="normal")

        # Disable next button if on last page
        if self.state.current_page >= total_pages:
            next_btn.config(state="disabled")
        else:
            next_btn.config(state="normal")
