import logging
import tkinter as tk
from typing import Optional, Tuple

from PIL import Image, ImageTk


def load_image(
    path: str,
    size: Optional[Tuple[int, int]] = None,
    canvas: Optional[tk.Canvas] = None,
    x: Optional[int] = None,
    y: Optional[int] = None,
    anchor: str = tk.NW,
    center: bool = False,
) -> ImageTk.PhotoImage:
    """
    Load an image and optionally render it on a Tk `canvas`.

    If `canvas` is provided, the image will be created on the canvas at
    coordinates `(x, y)` (or centered if `center=True`). The function
    always returns the `ImageTk.PhotoImage` instance so callers can keep a
    reference.

    Args:
        path (str): The file path to the image.
        size (Optional[Tuple[int, int]]): Optional (width, height) to resize the image to.
        canvas (Optional[tk.Canvas]): Optional Tkinter Canvas to render the image on.
        x (Optional[int]): The x-coordinate for the image on the canvas (ignored if `center=True`).
        y (Optional[int]): The y-coordinate for the image on the canvas (ignored if `center=True`).
        anchor (str): The anchor position for the image on the canvas (default: tk.NW).
        center (bool): Whether to center the image on the canvas (overrides x and y if True).
    Returns:
        ImageTk.PhotoImage: The loaded (and possibly resized) image.
    """
    try:
        pil_img = Image.open(path).convert("RGBA")
        if size:
            pil_img = pil_img.resize(size)
        photo = ImageTk.PhotoImage(pil_img)
    except Exception as exc:
        logging.debug("load_image failed for %s: %s", path, exc)
        fallback_size = size if size else (1, 1)
        fallback = Image.new("RGBA", fallback_size, (0, 0, 0, 0))
        photo = ImageTk.PhotoImage(fallback)

    if canvas is not None:
        # compute center coordinates if requested
        if center:
            try:
                cw = int(canvas.cget("width"))
                ch = int(canvas.cget("height"))
            except Exception:
                cw = canvas.winfo_width() or 0
                ch = canvas.winfo_height() or 0

            if size:
                img_w, img_h = size
            else:
                try:
                    img_w, img_h = photo.width(), photo.height()
                except Exception:
                    img_w, img_h = 0, 0

            x = (cw - img_w) // 2
            y = (ch - img_h) // 2

        # default coordinates
        if x is None:
            x = 0
        if y is None:
            y = 0

        canvas.create_image(x, y, image=photo, anchor=anchor)

        # store reference on the canvas to prevent garbage collection
        if not hasattr(canvas, "_images"):
            canvas._images = []
        canvas._images.append(photo)

    return photo
