import tkinter as tk
import tkinter.messagebox as messagebox
from typing import Optional

from app.presentation.views.helpers.avatar.ui import (
    handle_save_avatar,
    handle_upload_avatar,
)


def on_avatar_upload(
    canvas: tk.Canvas,
    save_button: tk.Button,
    user_id: int,
    state_container: dict[str, Optional[str]],
) -> None:
    """
    Handle the Upload Avatar button click.

    Opens a file dialog, renders the preview on *canvas*, enables *save_button*,
    and stores the chosen path in *state_container["path"]*.

    Args:
        canvas: Canvas widget used to preview the selected image.
        save_button: Save button to enable once an image is selected.
        user_id: ID of the current user (passed through to the upload helper).
        state_container: Shared dict with a ``"path"`` key that persists the
            selected file path across button clicks.
    """
    path = handle_upload_avatar(None, canvas, save_button, user_id)
    if path:
        state_container["path"] = path


def on_avatar_save(
    state_container: dict[str, Optional[str]],
    user_id: int,
    window: tk.Toplevel,
    profile_window: Optional[tk.Toplevel],
) -> None:
    """
    Handle the Save Avatar button click.

    Validates that an image has been selected, delegates the file-copy and
    database update to the save helper, shows feedback, and closes both the
    change-avatar window and the parent profile window on success.

    Args:
        state_container: Shared dict with a ``"path"`` key holding the selected
            file path (or ``None`` if nothing was uploaded yet).
        user_id: ID of the current user.
        window: The change-avatar ``Toplevel`` to destroy after a successful save.
        profile_window: The parent profile ``Toplevel`` to also destroy after a
            successful save.  May be ``None`` if called outside the profile flow.
    """
    selected_path = state_container["path"]

    if not selected_path:
        messagebox.showwarning("No Avatar Selected", "Please upload an avatar first")
        return

    success, message = handle_save_avatar(selected_path, user_id=user_id)

    if success:
        messagebox.showinfo("Success", message)
        window.destroy()
        if profile_window and profile_window.winfo_exists():
            profile_window.destroy()
    else:
        messagebox.showerror("Error", message)
