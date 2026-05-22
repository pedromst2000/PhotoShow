import tkinter as tk
from pathlib import Path
from tkinter import filedialog
from typing import Callable, Optional

from app.controllers.category_controller import CategoryController
from app.controllers.photo_controller import PhotoController
from app.presentation.widgets.helpers.images import load_image
from app.presentation.widgets.helpers.scrollable_text import ScrollableText
from app.presentation.widgets.helpers.ui_dialogs import show_error, show_info

_MAX_DESCRIPTION = 255
_MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB in bytes
_ALLOWED_FORMATS = (".png", ".jpg", ".jpeg")


def validate_photo_file(
    win: tk.Toplevel,
    filename: str,
) -> bool:
    """
    Validate photo file format and size.

    Args:
        win: Parent window for error dialogs.
        filename: Path to the file to validate.

    Returns:
        bool: True if file is valid, False otherwise.
    """
    if not filename:
        return False

    try:
        file_ext = Path(filename).suffix.lower()
        if file_ext not in _ALLOWED_FORMATS:
            show_error(
                win,
                "Invalid Format",
                f"Only {', '.join(_ALLOWED_FORMATS)} formats are supported.",
            )
            return False

        file_size = Path(filename).stat().st_size
        if file_size > _MAX_FILE_SIZE:
            max_mb = _MAX_FILE_SIZE / (1024 * 1024)
            show_error(
                win,
                "File Too Large",
                f"Maximum file size is {max_mb:.1f} MB. Your file is {file_size / (1024 * 1024):.2f} MB.",
            )
            return False

        return True

    except Exception as e:
        show_error(win, "Error", f"Failed to validate file: {str(e)}")
        return False


def handle_photo_upload(
    win: tk.Toplevel,
    state: dict,
    canvas: tk.Canvas,
    submit_btn: tk.Button,
) -> None:
    """
    Handle photo selection, validation, and preview rendering.

    Updates the state container and enables the submit button on success.

    Args:
        win: The add photo window.
        state: Photo state container to store file path.
        canvas: Canvas widget for preview rendering.
        submit_btn: Submit button to enable after upload.
    """
    filename = filedialog.askopenfilename(
        initialdir="/",
        title="Select a photo",
        filetypes=(
            ("Image files", "*.png *.jpg *.jpeg"),
            ("PNG files", "*.png"),
            ("JPG files", "*.jpg *.jpeg"),
        ),
    )

    if not filename:
        return

    if not validate_photo_file(win, filename):
        return

    try:
        # Load and display preview
        photo_image = load_image(filename, size=(350, 350), canvas=canvas, x=0, y=0)
        canvas.image = photo_image  # type: ignore

        # Store path in state
        state["path"] = filename

        # Enable submit button
        submit_btn["state"] = "normal"
        submit_btn["cursor"] = "hand2"

    except Exception as e:
        show_error(win, "Error", f"Failed to load image: {str(e)}")


def handle_photo_submission(
    win: tk.Toplevel,
    album_id: Optional[int],
    state: dict,
    scrollable_desc: ScrollableText,
    cat_var: tk.StringVar,
    on_created: Optional[Callable[[], None]],
) -> None:
    """
    Validate form, upload photo, and trigger callback.

    Args:
        win: The add photo window.
        album_id: ID of the album for the photo.
        state: Photo state container.
        scrollable_desc: Description textarea.
        cat_var: Category dropdown variable.
        on_created: Optional callback after successful creation.
    """
    # Validate photo uploaded
    if not state.get("path"):
        show_error(win, "Error", "Please upload a photo.")
        return

    # Validate album ID
    if not album_id:
        show_error(win, "Error", "Album ID is missing.")
        return

    # Validate description
    description = scrollable_desc.text.get("1.0", "end-1c").strip()
    if not description:
        show_error(win, "Error", "Please enter a description for the photo.")
        return
    if len(description) > _MAX_DESCRIPTION:
        show_error(
            win, "Error", f"Description must be at most {_MAX_DESCRIPTION} characters."
        )
        return

    # Validate category selection
    category_name = cat_var.get()
    if not category_name or category_name == "Select an option":
        show_error(win, "Error", "Please select a category.")
        return

    try:
        # Get category ID from name using controller
        categories = CategoryController.get_all_categories()
        category_id = None
        for cat in categories:
            if cat.get("category") == category_name:
                category_id = cat.get("id")
                break

        if not category_id:
            show_error(win, "Error", "Selected category not found.")
            return

        # Upload photo via controller
        success, message = PhotoController.upload_photo(
            image_path=state["path"],
            album_id=album_id,
            category_id=category_id,
            description=description,
        )

        if not success:
            show_error(win, "Error", message)
            return

        # Destroy the modal first so the grab is released and the parent
        # window can render the listbox update immediately after.
        show_info(win, "Success", message)
        win.destroy()

        if on_created and callable(on_created):
            on_created()

    except Exception as e:
        show_error(win, "Error", f"Failed to create photo: {str(e)}")
