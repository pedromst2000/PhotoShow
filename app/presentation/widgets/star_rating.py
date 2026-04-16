import tkinter as tk
from typing import Callable, Optional

from PIL import Image, ImageTk

from app.presentation.styles.colors import colors
from app.presentation.widgets.helpers.icon_label import add_icon_canvas

_STAR_DEFAULT_PATH = "app/assets/images/UI_Icons/Star_Icon_Default.png"
_STAR_SELECTED_PATH = "app/assets/images/UI_Icons/Star_Icon_Selected.png"


class StarRatingWidget(tk.Frame):
    """
    Reusable star rating widget displaying 1-5 stars using PNG icons.

    Supports two modes:
    - Display mode (interactive=False): renders a static average rating.
    - Interactive mode (interactive=True): allows hovering and clicking to rate.
    """

    def __init__(
        self,
        parent: tk.Widget,
        bg: Optional[str] = None,
        interactive: bool = False,
        on_rate: Optional[Callable[[int], None]] = None,
        size: int = 20,
        **kwargs,
    ):
        """
        Initialize the StarRatingWidget.

        Args:
            parent: The parent widget to attach this star rating widget to.
            bg: Optional background color for the widget. If None, inherits from parent or uses theme token.
            interactive: If True, enables hover and click interactions for rating. Defaults to False (display mode).
            on_rate: Optional callback function that receives the new rating value (1-5) when a star is clicked in interactive mode.
            size: The width and height of each star icon in pixels. Defaults to 20.
        """

        # Determine background: explicit bg -> parent's bg -> color token fallback
        bg_value = bg
        if bg_value is None:
            try:
                bg_value = parent.cget("bg")
            except Exception:
                bg_value = None
        if not bg_value:
            bg_value = colors["primary-50"]

        super().__init__(parent, bg=bg_value, **kwargs)

        self._bg = bg_value
        self._interactive = interactive
        self._on_rate = on_rate
        self._current_value: float = 0.0
        self._star_labels: list[tk.Label] = []

        # Load PNG icons using add_icon_canvas pattern and keep references alive
        self._img_default = self._load_star(_STAR_DEFAULT_PATH, size)
        self._img_selected = self._load_star(_STAR_SELECTED_PATH, size)

        for i in range(1, 6):
            lbl = tk.Label(
                self,
                image=self._img_default,
                bg=self._bg,
                cursor="hand2" if interactive else "arrow",
                bd=0,
                highlightthickness=0,
            )
            lbl.pack(side=tk.LEFT, padx=1)
            self._star_labels.append(lbl)

            def _make_enter(_val: int):
                """
                Create an event handler for mouse enter that captures the current star value.

                Args:
                    _val: The star value (1-5) associated with this label.
                """

                def _enter(event: tk.Event, _v: int = _val):
                    """
                    Create an event handler for mouse enter that updates the display to show the hovered star value.

                    Args:
                        event: The Tkinter event object from the mouse enter event.
                        _v: The star value (1-5) associated with the hovered label.
                    """

                    self._on_hover(_v)

                return _enter

            def _make_leave():
                """Create an event handler for mouse leave that resets to the current rating."""

                def _leave(event: tk.Event):
                    """
                    Create an event handler for mouse leave that resets to the current rating.

                    Args:
                        event: The Tkinter event object from the mouse leave event.
                    """
                    self._on_leave()

                return _leave

            def _make_click(_val: int):
                """
                Create an event handler for mouse click that captures the current star value.

                Args:
                    _val: The star value (1-5) associated with the clicked label.
                """

                def _click(event: tk.Event, _v: int = _val):
                    """
                    Create an event handler for mouse click that sets the rating to the clicked star value.

                    Args:
                        event: The Tkinter event object from the mouse click event.
                        _v: The star value (1-5) associated with the clicked label.
                    """
                    self._on_click(_v)

                return _click

            lbl.bind("<Enter>", _make_enter(i))
            lbl.bind("<Leave>", _make_leave())
            lbl.bind("<Button-1>", _make_click(i))

        self.set_value(0.0)

    def set_value(self, value: float):
        """Set and render a numeric rating value (0.0 – 5.0).

        Args:
            value: The numeric rating value to set (0.0 – 5.0).
        """
        self._current_value = value
        self._render(value)

    def get_value(self) -> float:
        """
        Return the currently displayed rating value.

        Returns:
            float: The current rating value (0.0 – 5.0) being displayed by the widget.
        """
        return self._current_value

    def set_interactive(self, enabled: bool):
        """Enable or disable interactive hover/click behaviour at runtime.

        Args:
            enabled: A boolean indicating whether to enable or disable interactivity.
        """
        cursor = "hand2" if enabled else "arrow"
        for lbl in self._star_labels:
            lbl.config(cursor=cursor)
        self._interactive = enabled

    def _load_star(self, path: str, size: int) -> ImageTk.PhotoImage:
        """
        Load a star icon using add_icon_canvas pattern.

        Creates a hidden canvas with add_icon_canvas to load and manage the star icon,
        then extracts and returns the PhotoImage with reference management.

        Args:
            path: The file path to the star icon image.
            size: The width and height to resize the star icon to (in pixels).

        Returns:
            ImageTk.PhotoImage: The loaded and resized star icon as a PhotoImage object.
        """
        # Create an invisible holder frame for the icon canvas (like add_icon_canvas pattern)
        icon_holder = tk.Frame(self)  # Hidden, won't be packed

        try:
            # Load star icon using add_icon_canvas pattern with hidden canvas
            star_canvas = add_icon_canvas(
                f"star_{id(path)}",
                icon_holder,
                path,
                icon_pos=(0, 0),
                icon_size=(size, size),
                canvas_size=(size, size),
                visible=False,  # Don't display the canvas
            )

            # Extract PhotoImage from canvas
            return star_canvas.image
        except Exception:
            # Fallback: create an empty PhotoImage if loading fails
            fallback = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            return ImageTk.PhotoImage(fallback)

    def _render(self, value: float):
        """
        Render the star icons based on the given rating value.

        Args:
            value: The numeric rating value to render (0.0 – 5.0). Stars will be filled up to the rounded integer value.
        """

        filled = round(value)
        for i, lbl in enumerate(self._star_labels):
            lbl.config(image=self._img_selected if i < filled else self._img_default)

    def _on_hover(self, val: int):
        """
        Handle the hover event over a star icon.

        Args:
            val: The star value (1-5) that is currently being hovered over.
        """

        if not self._interactive:
            return
        for i, lbl in enumerate(self._star_labels):
            lbl.config(image=self._img_selected if i < val else self._img_default)

    def _on_leave(self):
        """
        Handle the leave event when the mouse cursor leaves a star icon.
        """
        if not self._interactive:
            return
        self._render(self._current_value)

    def _on_click(self, val: int):
        """
        Handle the click event on a star icon.

        Args:
            val: The star value (1-5) that was clicked.
        """
        if not self._interactive:
            return
        self._current_value = float(val)
        self._render(self._current_value)
        if self._on_rate:
            self._on_rate(val)
