import tkinter as tk
from tkinter import messagebox

from app.controllers.explore_controller import ExploreController
from app.presentation.views.explore.helpers.data.state import ExploreState
from app.presentation.views.explore.helpers.ui.preview import update_preview


def handle_like(state: ExploreState, parent: tk.Widget):
    """
    Toggle like on selected photo.

    Args:
        state (ExploreState): The current state of the explore view.
        parent (tk.Widget): The parent widget for displaying error messages.
    """
    photo = state.selected_photo
    if photo is None:
        return

    success, msg, is_liked_now = ExploreController.toggle_like(photo["id"])
    if not success:
        messagebox.showerror("Error", msg, parent=parent)
        return

    photo["has_liked"] = is_liked_now
    photo["likes"] = max(0, photo.get("likes", 0) + (1 if is_liked_now else -1))
    update_preview(state)  # Update the preview to reflect the new like status and count


def handle_rate(state: ExploreState, rating_value: int, parent: tk.Widget):
    """
    Rate selected photo and update preview with the new average rating.

    Args:
        state (ExploreState): The current state of the explore view.
        rating_value (int): The rating value to be applied (1-5).
        parent (tk.Widget): The parent widget for displaying error messages.
    """
    photo = state.selected_photo
    if photo is None:
        return

    success, msg = ExploreController.rate_photo(photo["id"], rating_value)
    if not success:
        messagebox.showerror("Error", msg, parent=parent)
        return

    # Update user's rating
    photo["user_rating"] = rating_value

    # Fetch the updated photo to get new ratings from backend
    updated_photo = ExploreController.get_photo_by_id(photo["id"])
    if updated_photo:
        # Update both simple and weighted averages from backend (backend calculates these)
        photo["avg_rating"] = updated_photo.get(
            "avg_rating", photo.get("avg_rating", 1.0)
        )
        photo["weighted_rating"] = updated_photo.get(
            "weighted_rating", photo.get("weighted_rating", 1.0)
        )
        photo["rating_count"] = updated_photo.get(
            "rating_count", photo.get("rating_count", 0)
        )

    update_preview(state)  # Update the preview to reflect the new rating status
