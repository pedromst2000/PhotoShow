import tkinter as tk
from typing import Optional


class LoadingStateManager:
    """
    Manages loading indicators and states.
    Responsibility: loading state tracking only.
    """

    LOADING_STATES = {
        "idle": "Ready",
        "loading": "Loading...",
        "loaded": "Done",
        "error": "Error loading images",
    }

    def __init__(self, status_label: Optional[tk.Label] = None):
        """
        Initialize loading state manager.

        Args:
            status_label: Optional label to update with loading status
        """
        self.status_label = status_label
        self.current_state = "idle"

    def set_loading(self) -> None:
        """Set loading state."""
        self.current_state = "loading"
        self._update_label()

    def set_loaded(self) -> None:
        """Set loaded state."""
        self.current_state = "loaded"
        self._update_label()

    def set_error(self, message: str = None) -> None:
        """
        Set error state.

        Args:
            message: Optional error message
        """
        self.current_state = "error"
        self._update_label(message or "Error loading images")

    def set_idle(self) -> None:
        """Set idle state."""
        self.current_state = "idle"
        self._update_label()

    def _update_label(self, message: str = None) -> None:
        """
        Update status label if available.

        Args:
            message: Optional custom message to display instead of default state text
        """
        if not self.status_label:
            return

        text = message or self.LOADING_STATES.get(self.current_state, "")
        self.status_label.config(text=text)
        self.status_label.update()

    def is_loading(self) -> bool:
        """
        Check if currently loading.

        Returns:
            bool: True if loading, False otherwise
        """
        return self.current_state == "loading"

    def get_state(self) -> str:
        """Get current loading state."""
        return self.current_state


class LoadingIndicator:
    """
    Visual loading indicator for treeview.
    Responsibility: Display loading state only.
    """

    def __init__(self, tree):
        """
        Initialize loading indicator.

        Args:
            tree: ttk.Treeview widget
        """
        self.tree = tree
        self.is_visible = False

    def show(self) -> None:
        """Show loading indicator in treeview."""
        if not self.tree:
            return

        # Clear tree and show loading message
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.tree.insert(
            "", "end", iid="loading", values=("Loading next page...", "", "")
        )
        self.is_visible = True
        self.tree.update()

    def hide(self) -> None:
        """Hide loading indicator."""
        if self.tree and self.is_visible:
            try:
                self.tree.delete("loading")
            except Exception:
                pass
            self.is_visible = False
