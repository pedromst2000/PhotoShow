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
    Load an image from the specified path, optionally resizing it and placing it on a canvas.

    Args:
        path (str): The file path to the image.
        size (Optional[Tuple[int, int]]): The desired size (width, height) to resize the image to. If None, original size is used.
        canvas (Optional[tk.Canvas]): A Tkinter Canvas to place the image on. If None, the image is not placed on a canvas.
        x (Optional[int]): The X coordinate for placing the image on the canvas. Ignored if `center` is True.
        y (Optional[int]): The Y coordinate for placing the image on the canvas. Ignored if `center` is True.
        anchor (str): The anchor position for placing the image on the canvas (e.g., tk.NW, tk.CENTER). Defaults to tk.NW.
        center (bool): If True, the image will be centered on the canvas regardless of x and y values. Defaults to False.
    Returns:
        ImageTk.PhotoImage: The loaded (and possibly resized) image as a PhotoImage object.
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
