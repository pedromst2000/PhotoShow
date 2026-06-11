import io
import logging
import tkinter as tk
import urllib.request  # for loading images from URLs
from typing import Optional, Tuple

from PIL import Image, ImageTk


def create_loading_placeholder(
    size: Tuple[int, int] = (200, 200)
) -> ImageTk.PhotoImage:
    """
    Create a loading placeholder image (light gray with transparency).

    Displayed while remote Cloudinary images are being fetched over the network.
    Returns a semi-transparent gray box to indicate loading state.

    Args:
        size: Dimensions (width, height) in pixels.

    Returns:
        ImageTk.PhotoImage: A gray placeholder image.
    """
    try:
        placeholder = Image.new("RGBA", size, (200, 200, 200, 150))
        return ImageTk.PhotoImage(placeholder)
    except Exception:
        # Fallback: 1x1 transparent image.
        blank = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
        return ImageTk.PhotoImage(blank)


def load_pil_image_from_path_or_url(path_or_url: str) -> Image.Image:
    """
    Load a PIL Image from either a local file path or a remote URL.

    Handles both Cloudinary URLs and local file paths transparently.
    Remote URLs are downloaded into memory first, then converted to PIL Images.

    Args:
        path_or_url: Local file path or https:// URL to the image.

    Returns:
        Image.Image: A PIL Image in RGBA mode.

    Raises:
        FileNotFoundError: If local file does not exist.
        urllib.error.URLError: If remote URL is unreachable.
        IOError: If image data is corrupted or invalid format.
    """
    is_remote = path_or_url.startswith("http://") or path_or_url.startswith("https://")

    if is_remote:
        # Download remote image from URL (e.g., Cloudinary)
        logging.debug(f"Downloading remote image: {path_or_url}")
        with urllib.request.urlopen(path_or_url, timeout=10) as response:
            img_data = response.read()
        pil_img = Image.open(io.BytesIO(img_data))
    else:
        # Load local image file
        pil_img = Image.open(path_or_url)

    # Ensure RGBA mode for consistent processing
    if pil_img.mode != "RGBA":
        pil_img = pil_img.convert("RGBA")

    return pil_img


def show_loading_state(
    canvas: tk.Canvas,
    x: Optional[int] = None,
    y: Optional[int] = None,
    size: Tuple[int, int] = (200, 200),
    anchor: str = tk.NW,
    center: bool = False,
) -> int:
    """
    Display a loading placeholder on a canvas while an image is being fetched.

    Useful for showing visual feedback during async Cloudinary image downloads.

    Args:
        canvas: Tkinter canvas to draw on.
        x: X coordinate for placement (ignored if center=True).
        y: Y coordinate for placement (ignored if center=True).
        size: Placeholder dimensions (width, height).
        anchor: Anchor position (e.g., tk.NW, tk.CENTER).
        center: Whether to center on the canvas.

    Returns:
        int: Canvas item ID (for later deletion/update via canvas.itemconfig/delete).
    """
    placeholder = create_loading_placeholder(size)

    if center:
        try:
            cw = int(canvas.cget("width"))
            ch = int(canvas.cget("height"))
        except Exception:
            cw = canvas.winfo_width() or 0
            ch = canvas.winfo_height() or 0
        x = (cw - size[0]) // 2
        y = (ch - size[1]) // 2

    if x is None:
        x = 0
    if y is None:
        y = 0

    item_id = canvas.create_image(x, y, image=placeholder, anchor=anchor)

    # Attach placeholder to canvas for later reference.
    if not hasattr(canvas, "_loading_placeholders"):
        canvas._loading_placeholders = {}
    canvas._loading_placeholders[item_id] = placeholder

    return item_id


def load_image(
    path: str,
    size: Optional[Tuple[int, int]] = None,
    canvas: Optional[tk.Canvas] = None,
    x: Optional[int] = None,
    y: Optional[int] = None,
    anchor: str = tk.NW,
    center: bool = False,
    show_loading: bool = True,
) -> ImageTk.PhotoImage:
    """
    Load an image from a local file path or a remote URL (Cloudinary / https),
    optionally resizing it and placing it on a canvas.

    When loading from a remote URL, a loading placeholder is displayed first
    (if show_loading=True), then replaced with the actual image on success.

    Args:
        path (str): Local file path OR https:// URL to the image.
        size (Optional[Tuple[int, int]]): Desired (width, height) resize. If None, original size.
        canvas (Optional[tk.Canvas]): Canvas to place the image on.
        x (Optional[int]): X coordinate for placement. Ignored if `center` is True.
        y (Optional[int]): Y coordinate for placement. Ignored if `center` is True.
        anchor (str): Anchor position (e.g. tk.NW, tk.CENTER). Defaults to tk.NW.
        center (bool): Centre the image on the canvas. Defaults to False.
        show_loading (bool): Show loading placeholder while fetching remote images. Defaults to True.

    Returns:
        ImageTk.PhotoImage: The loaded (and possibly resized) image as a PhotoImage object.
    """
    is_remote = path and (path.startswith("http://") or path.startswith("https://"))
    loading_item_id = None

    try:
        # Show loading placeholder if fetching from remote URL.
        if is_remote and canvas and show_loading:
            placeholder_size = size if size else (200, 200)
            loading_item_id = show_loading_state(
                canvas, x=x, y=y, size=placeholder_size, anchor=anchor, center=center
            )

        # Fetch or load the image.
        if is_remote:
            with urllib.request.urlopen(path, timeout=10) as response:
                img_data = response.read()
            pil_img = Image.open(io.BytesIO(img_data)).convert("RGBA")
        else:
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
        # Remove loading placeholder if it was shown.
        if loading_item_id is not None:
            canvas.delete(loading_item_id)

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

        if x is None:
            x = 0
        if y is None:
            y = 0

        canvas.create_image(x, y, image=photo, anchor=anchor)

        if not hasattr(canvas, "_images"):
            canvas._images = []
        canvas._images.append(photo)

    return photo
