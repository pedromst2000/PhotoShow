import logging
from typing import Optional, Tuple

from PIL import Image, ImageTk


def load_image(path: str, size: Optional[Tuple[int, int]] = None) -> ImageTk.PhotoImage:
    """Load and resize an image, returning an ImageTk.PhotoImage.

    If loading fails, returns a tiny transparent fallback image so callers
    can continue without crashing the UI.

    Args:
        path: File path to the image.
        size: Optional (width, height) to resize the image to.

    Returns:
        ImageTk.PhotoImage: Ready-to-use PhotoImage instance.
    """
    try:
        img = Image.open(path).convert("RGBA")
        if size:
            img = img.resize(size)
        return ImageTk.PhotoImage(img)
    except Exception as exc:
        logging.debug("load_image failed for %s: %s", path, exc)
        fallback_size = size if size else (1, 1)
        fallback = Image.new("RGBA", fallback_size, (0, 0, 0, 0))
        return ImageTk.PhotoImage(fallback)
