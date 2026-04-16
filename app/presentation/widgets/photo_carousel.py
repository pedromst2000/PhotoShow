import logging
import tkinter as tk
from collections import OrderedDict
from typing import Callable, Optional

from PIL import Image, ImageTk

from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold, quickSandRegular
from app.presentation.widgets.helpers.button import on_enter as button_on_enter
from app.presentation.widgets.helpers.button import on_leave as button_on_leave
from app.utils.file_utils import resolve_image_path

_ARROW_ICON = "app/assets/images/UI_Icons/arrow_right.png"


class PhotoCarouselWidget(tk.Frame):
    """
    Reusable photo-preview carousel widget with lazy image loading.

    Displays a photo on a canvas with circular Previous / Next navigation
    buttons (green circles with arrow icons).
    """

    def __init__(
        self,
        parent: tk.Widget,
        canvas_width: int = 600,
        canvas_height: int = 280,
        canvas_bg: Optional[str] = None,
        bg: Optional[str] = None,
        btn_bg: Optional[str] = None,
        btn_fg: Optional[str] = None,
        **kwargs,
    ):
        """
        Create and place the photo carousel widget.

        Args:
            parent (tk.Widget): The parent widget to attach the carousel to.
            canvas_width (int): The width of the image canvas. Default is 600 pixels.
            canvas_height (int): The height of the image canvas. Default is 280 pixels.
            canvas_bg (str, optional): Background color for the image canvas. If None, it will use a default color.
            bg (str, optional): Background color for the entire widget. If None, it will inherit from the parent or use a default color.
            btn_bg (str, optional): Background color for navigation buttons. If None, it will use a default color.
            btn_fg (str, optional): Foreground color for navigation buttons. If None, it will use a default color.
            **kwargs: Additional keyword arguments to pass to the Frame initializer.
        """

        frame_bg = bg or colors["secondary-300"]
        super().__init__(
            parent, bg=frame_bg, **kwargs
        )  # Initialize the Frame with the specified background color and any additional kwargs

        # Button color tokens (allow override)
        self._btn_bg = btn_bg or colors["accent-300"]
        self._btn_fg = btn_fg or colors["secondary-500"]

        self._canvas_width = canvas_width
        self._canvas_height = canvas_height
        self._canvas_bg = canvas_bg or colors["secondary-400"]
        self._image_ref: Optional[ImageTk.PhotoImage] = None
        self._image_cache: OrderedDict = (
            OrderedDict()
        )  # LRU cache: path → ImageTk.PhotoImage
        self._cache_max_size: int = (
            15  # Keep only last 15 images to prevent memory bloat on large lists
        )
        self._on_prev: Optional[Callable[[], None]] = None
        self._on_next: Optional[Callable[[], None]] = None

        # Keep icon references alive
        self._prev_icon_ref: Optional[ImageTk.PhotoImage] = None
        self._next_icon_ref: Optional[ImageTk.PhotoImage] = None

        # ── Image canvas ───────────────────────────────────────────────
        self._canvas = tk.Canvas(
            self,
            width=canvas_width,
            height=canvas_height,
            bg=self._canvas_bg,
            highlightthickness=0,
            bd=0,
        )
        self._canvas.pack(padx=10, pady=(8, 12))

        # ── Navigation bar (prev / next) ───────────────────────────────
        nav_frame = tk.Frame(self, bg=frame_bg)
        nav_frame.pack(fill="x", padx=10, pady=(0, 8))

        # Build prev arrow icon (flipped) — increase size for better visibility
        try:
            prev_img = Image.open(_ARROW_ICON).convert("RGBA")
            prev_img = prev_img.resize((24, 24), Image.LANCZOS)
            prev_img = prev_img.transpose(Image.FLIP_LEFT_RIGHT)
            self._prev_icon_ref = ImageTk.PhotoImage(prev_img)
        except Exception:
            self._prev_icon_ref = (
                None  # If loading fails, the button will just show text without an icon
            )

        # Build next arrow icon — increase size for better visibility
        try:
            next_img = Image.open(_ARROW_ICON).convert("RGBA")
            next_img = next_img.resize((24, 24), Image.LANCZOS)
            self._next_icon_ref = ImageTk.PhotoImage(next_img)
        except Exception:
            self._next_icon_ref = (
                None  # If loading fails, the button will just show text without an icon
            )

        # Flat buttons with text + icon – matching the search button style
        # Larger flat prev button with label + icon
        self._prev_btn = tk.Button(
            nav_frame,
            width=40,
            height=30,
            image=self._prev_icon_ref,
            compound=tk.LEFT,
            font=quickSandBold(12),
            bg=self._btn_bg,
            fg=self._btn_fg,
            activebackground=self._btn_bg,
            activeforeground=self._btn_fg,
            borderwidth=0,
            relief="flat",
            highlightthickness=0,
            cursor="hand2",
            padx=18,
            pady=9,
            command=self._on_prev_click,
        )
        self._prev_btn.pack(side=tk.LEFT)
        self._prev_btn.bind("<Enter>", lambda e: button_on_enter(e, self._prev_btn))
        self._prev_btn.bind("<Leave>", lambda e: button_on_leave(e, self._prev_btn))

        # Larger flat next button with label + icon
        self._next_btn = tk.Button(
            nav_frame,
            width=40,
            height=30,
            image=self._next_icon_ref,
            compound=tk.RIGHT,
            font=quickSandBold(12),
            bg=self._btn_bg,
            fg=self._btn_fg,
            activebackground=self._btn_bg,
            activeforeground=self._btn_fg,
            borderwidth=0,
            relief="flat",
            highlightthickness=0,
            cursor="hand2",
            padx=18,
            pady=9,
            command=self._on_next_click,
        )
        self._next_btn.pack(side=tk.RIGHT)
        self._next_btn.bind("<Enter>", lambda e: button_on_enter(e, self._next_btn))
        self._next_btn.bind("<Leave>", lambda e: button_on_leave(e, self._next_btn))

        self.set_nav_enabled(prev=False, next_=False)
        self.show_empty()

    def set_callbacks(
        self,
        on_prev: Callable[[], None],
        on_next: Callable[[], None],
    ):
        """
        Set the callback functions for the Previous and Next buttons.

        Args:
            on_prev (Callable[[], None]): The function to call when the Previous button is clicked.
            on_next (Callable[[], None]): The function to call when the Next button is clicked.
        """

        self._on_prev = on_prev
        self._on_next = on_next

    def display_photo(self, path: str):
        """
        Load and render an image from *path* onto the canvas.

        Args:
            path (str): The file path to the image to display.
        """
        self._canvas.delete("all")
        self._image_ref = None

        if not path or not path.strip():
            self.show_empty("No image path provided")
            return

        # Resolve the path: handle both absolute and relative (from project root)
        resolved_path = resolve_image_path(path)

        if not resolved_path:
            logging.debug(f"Image file not found at: {path}")
            self.show_empty("Image not found")
            return

        # Return cached PhotoImage if already loaded (avoids re-decoding on navigation)
        if resolved_path in self._image_cache:
            photo = self._image_cache[resolved_path]
            # Move to end (mark as recently used in LRU cache)
            self._image_cache.move_to_end(resolved_path)
            self._image_ref = photo
            cx = self._canvas_width // 2
            cy = self._canvas_height // 2
            self._canvas.create_image(cx, cy, image=photo, anchor="center")
            return

        try:
            logging.debug(f"Attempting to load image from: {resolved_path}")

            # Open and process the image
            pil_img = Image.open(resolved_path)

            # Convert to RGBA if needed, but handle different modes
            if pil_img.mode != "RGBA":
                pil_img = pil_img.convert("RGBA")

            # Resize image to exact canvas dimensions to ensure uniform size
            # This will fill the canvas regardless of original aspect ratio
            pil_img = pil_img.resize(
                (self._canvas_width, self._canvas_height), Image.LANCZOS
            )

            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(pil_img)

            # Store in LRU cache with eviction of oldest if cache exceeds max size
            self._image_cache[resolved_path] = photo
            if len(self._image_cache) > self._cache_max_size:
                # Remove oldest (first) item from cache to free memory
                oldest_path = next(iter(self._image_cache))
                del self._image_cache[oldest_path]
                logging.debug(
                    f"Evicted {oldest_path} from image cache (size={len(self._image_cache)})"
                )

            self._image_ref = photo

            # Display on canvas centered
            cx = self._canvas_width // 2
            cy = self._canvas_height // 2
            self._canvas.create_image(cx, cy, image=photo, anchor="center")

            logging.debug(f"Successfully loaded image: {resolved_path}")

        except FileNotFoundError as exc:
            logging.debug(f"File not found error for {resolved_path}: {exc}")
            self.show_empty("Image file not found")
        except Exception as exc:
            logging.debug(
                f"Failed to load image from {resolved_path}: {type(exc).__name__}: {exc}"
            )
            self.show_empty("Unable to load image")

    def show_empty(self, message: str = "No photo selected"):
        """
        Display a placeholder message on the canvas when no image is available.

        Args:
            message (str): The message to display. Default is "No photo selected".
        """
        self._canvas.delete("all")
        self._image_ref = None
        self._canvas.create_text(
            self._canvas_width // 2,
            self._canvas_height // 2,
            text=message,
            font=quickSandRegular(13),
            fill=colors["primary-50"],
            justify="center",
        )

    def set_nav_enabled(self, prev: bool = True, next_: bool = True):
        """
        Enable or disable the navigation buttons.

        Args:
            prev (bool): Whether the previous button should be enabled. Default is True.
            next_ (bool): Whether the next button should be enabled. Default is True.
        """
        self._prev_btn.config(state=tk.NORMAL if prev else tk.DISABLED)
        self._next_btn.config(state=tk.NORMAL if next_ else tk.DISABLED)

    def _on_prev_click(self):
        """Handle the Previous button click event by invoking the assigned callback."""
        if self._on_prev:
            self._on_prev()

    def _on_next_click(self):
        """Handle the Next button click event by invoking the assigned callback."""
        if self._on_next:
            self._on_next()
