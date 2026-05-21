import os
import tkinter as tk
import tkinter.filedialog as filedialog
from pathlib import Path
from typing import Optional

from app.controllers.user_controller import UserController
from app.core.state.session import session
from app.presentation.widgets.helpers.images import load_image
from app.presentation.widgets.helpers.ui_dialogs import show_error
from app.utils.file_utils import replace_avatar_in_latest


def handle_upload_avatar(
    event: Optional[tk.Event],
    canvas_avatar: tk.Canvas,
    btn_save_avatar: tk.Button,
    user_id: int,
) -> Optional[str]:
    """
    Handle avatar upload: open file dialog, load and preview image.

    Implements file dialog for image selection with preview display on canvas.
    Updates the save button state and returns the selected file path.

    Args:
        event: Tkinter event (from button click).
        canvas_avatar: Canvas widget for image preview.
        btn_save_avatar: Save button to enable after selection.
        user_id: User ID (for reference).

    Returns:
        Optional[str]: Full path to selected image file, or None if cancelled.
    """
    # Open file dialog to select image
    filename: str = filedialog.askopenfilename(
        initialdir="/",
        title="Select an image",
        filetypes=(
            ("png files", "*.png"),
            ("jpg files", "*.jpg"),
            ("jpeg files", "*.jpeg"),
        ),
    )

    if not filename:
        return None

    try:
        # Load and display image preview
        photo_image = load_image(
            filename, size=(200, 200), canvas=canvas_avatar, x=0, y=0
        )
        canvas_avatar.image = photo_image  # type: ignore

        # Enable save button
        btn_save_avatar["state"] = "normal"
        btn_save_avatar["cursor"] = "hand2"

        return filename

    except Exception as e:
        show_error(canvas_avatar, "Error", f"Failed to load image: {str(e)}")
        return None


def handle_save_avatar(
    source_image_path: str,
    user_id: Optional[int] = None,
) -> tuple[bool, str]:
    """
    Handle avatar save: replace any existing avatar for the user in the latest
    tier (regardless of extension), update the database, and refresh the session.

    Args:
        source_image_path: Full path to source avatar image (from file dialog).
        user_id: User ID (optional, defaults to session.user_id).

    Returns:
        tuple[bool, str]: (success: bool, message: str)
    """
    if user_id is None:
        user_id = session.user_id

    if not user_id:
        return False, "Unable to identify user"

    if not source_image_path or not os.path.exists(source_image_path):
        return False, "Selected image file not found"

    try:
        username = session.user_data.get("username") if session.user_data else None
        if not username:
            return False, "Unable to identify username"

        # Copy to latest tier, removing any prior avatar (any extension) for this user.
        try:
            stored_path = replace_avatar_in_latest(username, source_image_path)
        except ValueError as e:
            return False, str(e)
        except OSError as e:
            return False, f"Failed to save avatar file: {str(e)}"

        # stored_path is "assets/images/local_cloud_media/latest/profile_avatars/{filename}"
        # UserController.update_avatar expects just the filename.
        avatar_filename = Path(stored_path).name

        # Update database via UserController
        success, message = UserController.update_avatar(avatar_filename)

        if not success:
            # Rollback: remove the file we just copied.
            from app.utils.file_utils import delete_from_latest

            delete_from_latest(stored_path)
            return False, f"Failed to save avatar to database: {message}"

        # Refresh session data to reflect changes
        UserController.refresh_session_data()

        return True, "Avatar updated successfully"

    except Exception as e:
        return False, f"Something went wrong: {str(e)}"
