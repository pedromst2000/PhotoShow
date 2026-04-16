import tkinter as tk

from app.controllers.photo_controller import PhotoController
from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold
from app.presentation.views.explore.helpers.data.state import ExploreState
from app.presentation.widgets.helpers.ui_dialogs import (
    show_confirmation,
    show_error,
    show_info,
)
from app.presentation.widgets.window import create_toplevel


def open_report_dialog(state: ExploreState):
    """
    Open photo report dialog.

    Displays a dialog for reporting the selected photo.

    Args:
        state: Explore view state containing selected photo info.
    """
    if state.selected_photo is None:
        return
    title = "⚠ Report Photo"
    win = create_toplevel(
        title=title,
        width=420,
        height=350,
        icon_path="app/assets/PhotoShowIcon.ico",
        bg_color=colors["primary-50"],
    )
    tk.Label(
        win,
        text=title,
        font=quickSandBold(16),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    ).pack(expand=True)


def handle_delete_photo(state: ExploreState):
    """
    Handle photo deletion with confirmation and feedback dialogs.

    For admin users or photo owners. Shows confirmation dialog before deletion,
    then deletes the photo and updates pagination.

    Args:
        state: Explore view state containing selected photo info.
    """
    if state.selected_photo is None:
        return

    photo_id = state.selected_photo.get("id")

    # Show confirmation dialog using the reusable confirmation function
    # Use state.win as parent so dialog appears within the explore window
    confirmed = show_confirmation(
        state.win,
        "Delete Photo",
        "Are you sure you want to delete this photo?\n\nThis action cannot be undone.",
    )

    if not confirmed:
        return  # User cancelled

    # Perform deletion
    try:

        # Use single delete method (handles both owner and admin deletion)
        success, message = PhotoController.delete_photo(photo_id)

        if success:
            show_info(state.win, "Success", message)

            # Clear the cache to force reload on next pagination
            from app.presentation.views.explore.helpers.data.catalog import (
                invalidate_catalog_cache,
            )

            invalidate_catalog_cache()

            # Reset the preview (clear selection) by resetting selected_index
            state.selected_index = None
            from app.presentation.views.explore.helpers.ui.preview import reset_preview

            reset_preview(state)

            # Reload catalog and refresh treeview
            from app.presentation.views.explore.helpers.data.catalog import load_catalog

            load_catalog(state)

            # Trigger treeview refresh if available
            pagination_controller = getattr(state, "_pagination_ui_controller", None)
            if pagination_controller and hasattr(
                pagination_controller, "tree_controller"
            ):
                pagination_controller.tree_controller.refresh_treeview()
        else:
            show_error(state.win, "Error", message)
    except Exception as e:
        # Log the real error for diagnostics; never expose internal details to the user.
        from app.utils.log_utils import log_issue

        log_issue("handle_delete_photo failed", exc=e)
        show_error(state.win, "Error", "Something went wrong. Please try again later.")
