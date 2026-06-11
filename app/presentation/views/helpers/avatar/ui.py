import os
import tkinter as tk
import tkinter.filedialog as filedialog
from typing import Optional

from app.controllers.user_controller import UserController
from app.core.services.cloudinary_service import CloudinaryService
from app.core.services.user_service import UserService
from app.core.state.session import session
from app.presentation.widgets.helpers.images import load_image
from app.presentation.widgets.helpers.ui_dialogs import show_error


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
        photo_image = load_image(
            filename, size=(200, 200), canvas=canvas_avatar, x=0, y=0
        )
        canvas_avatar.image = photo_image  # type: ignore

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
    Handle avatar save: delete old avatar, upload new image to Cloudinary, update database.

    Ensures no duplicate avatars are left in the cloud by always deleting the old avatar
    before uploading the new one. Uses a deterministic Cloudinary public_id
    (<username>_avatar) for consistency.

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

        # Step 1: Get and delete the OLD avatar from PROD folder ONLY (if exists)
        # This prevents duplicate avatars from accumulating in the prod folder.
        # Dev folder avatars (hardcoded seed data) are never deleted.
        old_public_id = UserService.get_current_avatar_provider_id(user_id)
        if old_public_id and "photo-show/prod/" in old_public_id:
            # Only delete if it's from prod folder (user upload), not dev folder (seed data)
            CloudinaryService.delete_image(old_public_id)

        # Step 2: Upload the NEW avatar to Cloudinary
        # Uses deterministic public_id: photo-show/profile_avatars/<username>_avatar
        upload_result = CloudinaryService.upload_avatar(source_image_path, username)
        if upload_result is None:
            return False, "Failed to upload avatar to cloud storage"

        provider_id = upload_result["public_id"]
        provider_url_image = upload_result["url"]

        # Step 3: Update database via UserController
        success, message = UserController.update_avatar(provider_id, provider_url_image)

        if not success:
            return False, f"Failed to save avatar: {message}"

        # Refresh session data to reflect changes
        UserController.refresh_session_data()

        return True, "Avatar updated successfully"

    except Exception as e:
        return False, f"Something went wrong: {str(e)}"
