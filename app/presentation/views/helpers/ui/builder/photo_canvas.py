import tkinter as tk

from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold
from app.presentation.views.helpers.data.state import BasePhotoState
from app.presentation.widgets.helpers.images import load_image
from app.utils.file_utils import resolve_image_path


def build_photo_canvas(
    parent: tk.Frame,
    state: BasePhotoState,
    img_refs: list,
    width: int = 568,
    height: int = 180,
    canvas_bg: str = colors["secondary-400"],
) -> tk.Canvas:
    """Render the selected photo image on a canvas packed into *parent*.

    Args:
        parent: The parent frame to attach the canvas to.
        state: BasePhotoState containing selected photo info.
        img_refs: List to hold image references for the window lifetime.
        width: Canvas pixel width. Defaults to 568.
        height: Canvas pixel height. Defaults to 180.
        canvas_bg: Canvas background colour when no image is available.

    Returns:
        The created tk.Canvas so callers can further configure it if needed.
    """
    photo = state.selected_photo

    photo_canvas = tk.Canvas(
        parent,
        width=width,
        height=height,
        bg=canvas_bg,
        highlightthickness=0,
        bd=0,
    )
    photo_canvas.pack(side=tk.TOP, fill=tk.X, pady=(0, 16))

    img_path = resolve_image_path(photo.get("image")) if photo else None
    img_ref = None
    if img_path:
        img_ref = load_image(
            img_path,
            size=(width, height),
            canvas=photo_canvas,
            x=0,
            y=0,
        )
        img_refs.append(img_ref)

    if img_ref is None:
        photo_canvas.create_text(
            width // 2,
            height // 2,
            text="No image available",
            font=quickSandBold(14),
            fill=colors["primary-50"],
        )

    return photo_canvas
