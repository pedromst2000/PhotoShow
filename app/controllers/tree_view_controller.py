from typing import Optional

from app.presentation.views.explore.helpers.data.pagination import PaginationManager
from app.presentation.views.explore.helpers.data.state import ExploreState


class TreeViewController:
    """
    Handles treeview rendering and updates.

    Responsibilities:
    - Refreshing treeview with paginated items
    - Clearing and repopulating treeview on filter/page changes
    - Mapping tree item IDs to global photo indices for selection
    Memory Efficiency:
    - Only current page items (10) are loaded into treeview at any time
    - Previous page items are cleared before new page is loaded
    - No accumulation of items across pages in UI or memory
    """

    def __init__(self, state: ExploreState):
        """
        Initialize controller.

        Args:
            state: ExploreState object containing tree reference
        """
        self.state = state

    def refresh_treeview(self) -> None:
        """
        Refresh treeview with paginated items.
        Called after pagination or filtering changes.
        """
        tree = self.state.tree
        if tree is None:
            return

        try:
            # Clear existing items from TreeView (delete previous page)
            self._clear_tree()

            # Get current page items (10 or fewer from filtered list)
            paginated = PaginationManager.get_paginated_items(self.state)

            if not paginated:
                self._show_empty_state()
                return

            # Build index mapping and insert items
            self._populate_tree(paginated)

            # Force Tkinter to render changes immediately
            self._force_update()
        except Exception as e:
            print(f"[ERROR] tree_view_controller.refresh_treeview: {e}")
            print(f"[ERROR] tree_view_controller.refresh_treeview: {e}")
            import traceback

            traceback.print_exc()

    def _clear_tree(self) -> None:
        """Clear all items from tree."""
        tree = self.state.tree
        if tree:
            for item in tree.get_children():
                tree.delete(item)

    def _show_empty_state(self) -> None:
        """Show empty state message."""
        tree = self.state.tree
        if tree:
            tree.insert("", "end", iid="empty", values=("No photos found", "", ""))

    def _populate_tree(self, paginated: list) -> None:
        """
        Insert paginated items with index mapping.

        Args:
            paginated: List of photo items for current page
        """
        tree = self.state.tree
        if not tree:
            return

        # Clear mapping and rebuild
        self.state._tree_id_to_global_idx = {}

        # Calculate global indices for this page
        page_start_idx = (self.state.current_page - 1) * self.state.items_per_page

        # Insert each item with local index as tree ID
        for local_idx, photo in enumerate(paginated):
            try:
                album = photo.get("album_name") or "—"
                author = photo.get("user") or "—"
                category = photo.get("category") or "—"

                # Map local ID to global index
                global_idx = page_start_idx + local_idx
                self.state._tree_id_to_global_idx[str(local_idx)] = global_idx

                # Use local index as tree ID (0-9 for 10 items per page)
                tree.insert(
                    "", "end", iid=str(local_idx), values=(album, author, category)
                )
            except Exception as e:
                print(f"[ERROR] _populate_tree item {local_idx}: {e}")

    def _force_update(self) -> None:
        """Force Tkinter to render tree changes immediately."""
        tree = self.state.tree
        if tree:
            tree.update()
            # Also update parent frames for complete refresh
            tree.focus()

    def update_selection(self, global_idx: Optional[int]) -> None:
        """
        Update tree selection based on global index.
        Only selects if item is on current page.

        Args:
            global_idx: Global photo index, or None to clear selection
        """
        if global_idx is None or self.state.tree is None:
            return

        # Check if item is on current page
        page_size = self.state.items_per_page
        item_page = global_idx // page_size + 1

        if item_page != self.state.current_page:
            # Item not on current page, don't select
            return

        # Convert global to local index
        local_idx = global_idx % page_size

        try:
            self.state.tree.selection_set(str(local_idx))
            self.state.tree.see(str(local_idx))
        except Exception:
            pass  # Item not found, silently ignore
