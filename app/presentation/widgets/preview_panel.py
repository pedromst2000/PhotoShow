import tkinter as tk
from typing import Any, Optional, Tuple

from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold, quickSandBoldUnderline
from app.presentation.views.album.main import open_album
from app.presentation.views.comments.main import open_comments
from app.presentation.views.explore.helpers.ui.carousel import (
    navigate_next,
    navigate_prev,
)
from app.presentation.views.explore.helpers.ui.dialogs import (
    handle_delete_photo,
    open_report_dialog,
)
from app.presentation.views.explore.helpers.ui.interactions import (
    handle_like,
    handle_rate,
)
from app.presentation.views.explore.helpers.ui.preview import (
    reset_preview,
)
from app.presentation.views.photo.main import open_photo_details
from app.presentation.views.profile.author import open_author_profile
from app.presentation.widgets.helpers.button import on_enter as button_on_enter
from app.presentation.widgets.helpers.button import on_leave as button_on_leave
from app.presentation.widgets.helpers.icon_label import add_icon_canvas
from app.presentation.widgets.helpers.images import load_image
from app.presentation.widgets.photo_carousel import PhotoCarouselWidget
from app.presentation.widgets.star_rating import StarRatingWidget


class PreviewPanelWidget(tk.Frame):
    """
    Reusable preview panel widget with carousel and photo metadata.

    Contains:
    - Photo carousel with prev/next navigation
    - Metadata: avatar, username, rating stars
    - Stats: likes and comments count
    - Action buttons: like, details, comments, album, report
    """

    def __init__(
        self,
        parent: tk.Frame,
        state,
        x_pos: int = 545,
        width: int = 755,
        height: int = 674,
        panel_bg: Optional[str] = None,
        btn_bg: Optional[str] = None,
        btn_fg: Optional[str] = None,
        canvas_bg: Optional[str] = None,
    ):
        """
        Create and place preview panel.

        Args:
            parent: Parent Tkinter frame to attach the panel to.
            state: Shared state object for managing interactions and data.
            x_pos: X position of the panel (for balanced layout with left panel).
            width: Width of the preview panel.
            height: Height of the preview panel.
            panel_bg: Optional background color for the panel (overrides default).
            btn_bg: Optional background color for buttons (overrides default).
            btn_fg: Optional foreground color for buttons (overrides default).
            canvas_bg: Optional background color for the carousel canvas (overrides default).
        """
        self.parent = parent
        self.state = state
        self.x_pos = x_pos
        self.width = width
        self.height = height

        # Color scheme (allow override of panel background and buttons)
        self._panel_bg = panel_bg if panel_bg is not None else colors["secondary-300"]
        self._btn_bg = btn_bg if btn_bg is not None else colors["accent-300"]
        self._btn_fg = btn_fg if btn_fg is not None else colors["secondary-500"]
        self._canvas_bg = (
            canvas_bg if canvas_bg is not None else colors["secondary-400"]
        )
        self._icon_dir = "app/assets/images/UI_Icons/"

        self._build_preview_panel()

    def _build_preview_panel(self):
        """Build the right preview panel with carousel and metadata."""
        right = tk.Frame(self.parent, bg=self._panel_bg, bd=0)
        right.place(x=self.x_pos, y=0, width=self.width, height=self.height)

        # Header
        header_frame = tk.Frame(right, bg=self._panel_bg)
        header_frame.pack(fill="x", padx=15, pady=(10, 2))

        tk.Label(
            header_frame,
            text="Preview Photos",
            font=quickSandBold(14),
            bg=self._panel_bg,
            fg=colors["secondary-500"],
        ).pack(anchor="w")

        tk.Label(
            header_frame,
            text="View the album above  •  Click the username to view the author's profile  •  Hover over the stars to rate the photo",
            font=quickSandBold(12),
            bg=self._panel_bg,
            fg=colors["primary-50"],
            wraplength=700,
            justify="left",
        ).pack(anchor="w")

        # Preview column: carousel → metadata → buttons
        preview_col = tk.Frame(right, bg=self._panel_bg)
        preview_col.pack(fill="both", expand=False, padx=0, pady=0)

        # ── Carousel ────────────────────────────────────────────────────
        carousel = PhotoCarouselWidget(
            preview_col,
            canvas_width=450,
            canvas_height=220,
            canvas_bg=self._canvas_bg,
            bg=self._panel_bg,
            btn_bg=self._btn_bg,
            btn_fg=self._btn_fg,
        )
        carousel.pack(padx=10, pady=(4, 8))
        self.state.carousel = carousel
        carousel.set_callbacks(
            on_prev=lambda: navigate_prev(self.state),
            on_next=lambda: navigate_next(self.state),
        )

        # ── Metadata section (2 rows) ───────────────────────────────────
        metadata_container = tk.Frame(preview_col, bg=self._panel_bg)
        metadata_container.pack(fill="x", padx=10, pady=(12, 4))
        self.state.metadata_frame = metadata_container

        # Row 1: Avatar + Username + Stars
        meta_row1 = tk.Frame(metadata_container, bg=self._panel_bg)
        meta_row1.pack(fill="x", side=tk.TOP, pady=(0, 2))

        avatar_canvas = tk.Canvas(
            meta_row1,
            width=40,
            height=40,
            bg=self._panel_bg,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        avatar_canvas.pack(side=tk.LEFT, padx=(0, 8))
        self.state.avatar_canvas = avatar_canvas

        username_lbl = tk.Label(
            meta_row1,
            text="",
            font=quickSandBoldUnderline(12),
            bg=self._panel_bg,
            fg=colors["primary-50"],
            cursor="hand2",
        )
        username_lbl.pack(side=tk.LEFT, padx=(0, 20))
        self.state.username_label = username_lbl

        star_widget = StarRatingWidget(
            meta_row1,
            bg=self._panel_bg,
            interactive=True,
            size=24,
            on_rate=lambda v: handle_rate(self.state, v, right),
        )
        star_widget.pack(side=tk.RIGHT)
        self.state.star_widget = star_widget

        rating_count_lbl = tk.Label(
            meta_row1,
            text="",
            font=quickSandBold(10),
            bg=self._panel_bg,
            fg=colors["primary-50"],
        )
        rating_count_lbl.pack(side=tk.RIGHT, padx=(4, 0))
        self.state.rating_count_label = rating_count_lbl

        # Row 2: Likes + Comments (right-aligned)
        meta_row2 = tk.Frame(metadata_container, bg=self._panel_bg)
        meta_row2.pack(fill="x", side=tk.TOP, pady=(4, 0))

        meta_stats = tk.Frame(meta_row2, bg=self._panel_bg)
        meta_stats.pack(side=tk.RIGHT)

        # Like icon + count (load directly into packable canvas)
        like_canvas = tk.Canvas(
            meta_stats,
            width=20,
            height=20,
            bg=self._panel_bg,
            highlightthickness=0,
            bd=0,
        )
        like_canvas.pack(side=tk.LEFT, padx=(0, 6))
        like_photo = load_image(
            self._icon_dir + "Like_Icon.png",
            size=(20, 20),
            canvas=like_canvas,
            x=0,
            y=0,
        )
        like_canvas.image = like_photo
        self.state._like_icon_canvas = like_canvas

        likes_lbl = tk.Label(
            meta_stats,
            text="0",
            font=quickSandBold(14),
            bg=self._panel_bg,
            fg=colors["primary-50"],
        )
        likes_lbl.pack(side=tk.LEFT, padx=(0, 12))
        self.state.likes_label = likes_lbl

        # Comment icon + count (load directly into packable canvas)
        comment_canvas = tk.Canvas(
            meta_stats,
            width=20,
            height=20,
            bg=self._panel_bg,
            highlightthickness=0,
            bd=0,
        )
        comment_canvas.pack(side=tk.LEFT, padx=(0, 6))
        comment_photo = load_image(
            self._icon_dir + "Comment_Icon.png",
            size=(20, 20),
            canvas=comment_canvas,
            x=0,
            y=0,
        )
        comment_canvas.image = comment_photo
        self.state._comment_icon_canvas = comment_canvas

        comments_lbl = tk.Label(
            meta_stats,
            text="0",
            font=quickSandBold(14),
            bg=self._panel_bg,
            fg=colors["primary-50"],
        )
        comments_lbl.pack(side=tk.LEFT)
        self.state.comments_label = comments_lbl

        # ── Action buttons row (below metadata) ──────────────────────────
        btns_frame = tk.Frame(preview_col, bg=self._panel_bg)
        btns_frame.pack(fill="x", padx=10, pady=(12, 0))
        self.state.btns_frame = btns_frame

        # Load all button icons using add_icon_canvas (consistent pattern)
        like_icon, unlike_icon = self._load_button_icons()

        self.state.like_btn = self._make_icon_btn(
            btns_frame,
            label="  Add Like",
            command=lambda: handle_like(self.state, right),
            icon=like_icon,
            like_icon=like_icon,
            unlike_icon=unlike_icon,
        )
        self.state.details_btn = self._make_icon_btn(
            btns_frame,
            label="  See Details",
            command=lambda: open_photo_details(self.state),
            icon=self._get_icon_via_canvas(self._icon_dir + "Eye_Icon_V2.png"),
        )
        self.state.comments_btn = self._make_icon_btn(
            btns_frame,
            label="  See Comments",
            command=lambda: open_comments(self.state),
            icon=self._get_icon_via_canvas(self._icon_dir + "Comment_Icon_V2.png"),
        )
        self.state.album_btn = self._make_icon_btn(
            btns_frame,
            label="  See Album",
            command=lambda: open_album(self.state),
            icon=self._get_icon_via_canvas(self._icon_dir + "Eye_Icon_V2.png"),
        )

        # Create delete button - shown for admins and photo owners
        self.state.delete_btn = self._make_icon_btn(
            btns_frame,
            label="  Delete Photo",
            command=lambda: handle_delete_photo(self.state),
            icon=self._get_icon_via_canvas(self._icon_dir + "Remove_Icon.png"),
        )

        # Create report button - shown for users who don't own the photo
        self.state.report_btn = self._make_icon_btn(
            btns_frame,
            label="  Report Photo",
            command=lambda: open_report_dialog(self.state),
            icon=self._get_icon_via_canvas(self._icon_dir + "Report_Icon.png"),
        )

        # Configure grid layout for buttons (max 5 buttons per row)
        btns_frame.grid_columnconfigure([0, 1, 2, 3, 4], weight=0)

        buttons = [
            self.state.like_btn,
            self.state.details_btn,
            self.state.comments_btn,
            self.state.album_btn,
            self.state.delete_btn,
            self.state.report_btn,
        ]

        for idx, btn in enumerate(buttons):
            row = idx // 5
            col = idx % 5
            btn.grid(row=row, column=col, padx=4, pady=2, sticky="ew")

        # Bind click handlers
        username_lbl.bind("<Button-1>", lambda e: open_author_profile(self.state))
        avatar_canvas.bind("<Button-1>", lambda e: open_author_profile(self.state))

        reset_preview(self.state)

    def _make_icon_btn(
        self,
        parent: tk.Frame,
        label: str,
        command,
        icon=None,
        like_icon=None,
        unlike_icon=None,
    ) -> tk.Button:
        """
        Create a flat button with a pre-loaded icon (icons managed by caller like add_icon_canvas).

        Single Responsibility: Only handles button creation, configuration, and bindings.
        Icon loading and reference management is done by the caller.

        Args:
            parent: The parent frame to attach the button to.
            label: The text label to display on the button.
            command: The function to call when the button is clicked.
            icon: Pre-loaded PhotoImage object (for regular buttons).
            like_icon: Pre-loaded like icon (for like button dynamic switching).
            unlike_icon: Pre-loaded unlike icon (for like button dynamic switching).
        """
        btn = tk.Button(
            parent,
            text=label,
            image=icon,
            compound=tk.LEFT,
            font=quickSandBold(10),
            bg=self._btn_bg,
            fg=self._btn_fg,
            activebackground=self._btn_bg,
            activeforeground=self._btn_fg,
            borderwidth=0,
            highlightthickness=0,
            cursor="hand2",
            relief="flat",
            padx=8,
            pady=5,
            state=tk.DISABLED,
            command=command,
        )
        btn.image = icon

        # Store both icon states for dynamic like/unlike switching
        if like_icon and unlike_icon:
            btn._like_icon = like_icon
            btn._unlike_icon = unlike_icon

        btn.bind("<Enter>", lambda e: button_on_enter(e, btn))
        btn.bind("<Leave>", lambda e: button_on_leave(e, btn))

        return btn

    def _load_button_icons(self) -> Tuple[Any, Any]:
        """
        Load like/unlike button icons using add_icon_canvas pattern.

        Creates hidden canvases with add_icon_canvas to load and manage icon references,
        then extracts the PhotoImage objects with proper reference management.

        Returns:
            Tuple[PhotoImage, PhotoImage]: (like_icon, unlike_icon)
        """
        # Create an invisible holder frame for icon canvases
        icon_holder = tk.Frame(self.parent)  # Hidden, won't be packed

        like_canvas = add_icon_canvas(
            "btn_like",
            icon_holder,
            self._icon_dir + "Like_Icon_V2.png",
            icon_pos=(0, 0),
            icon_size=(16, 16),
            canvas_size=(16, 16),
            visible=False,  # Don't display the canvas
        )
        unlike_canvas = add_icon_canvas(
            "btn_unlike",
            icon_holder,
            self._icon_dir + "Unlike_Icon_V2.png",
            icon_pos=(0, 0),
            icon_size=(16, 16),
            canvas_size=(16, 16),
            visible=False,  # Don't display the canvas
        )

        # Extract PhotoImage objects from canvases (add_icon_canvas stores image as .image)
        like_icon = like_canvas.image
        unlike_icon = unlike_canvas.image

        # Store references in state to prevent garbage collection
        if not hasattr(self.state, "_btn_icon_refs"):
            self.state._btn_icon_refs = []
        self.state._btn_icon_refs.extend([like_icon, unlike_icon])

        return like_icon, unlike_icon

    def _get_icon_via_canvas(self, icon_path: str) -> Any:
        """
        Load a button icon using add_icon_canvas pattern.

        Creates a hidden canvas with add_icon_canvas, extracts the PhotoImage,
        and maintains the reference for garbage collection prevention.

        Args:
            icon_path: Path to the icon image file.

        Returns:
            PhotoImage: The loaded icon with reference managed by state.
        """
        # Create an invisible holder frame for the icon canvas
        icon_holder = tk.Frame(self.parent)  # Hidden, won't be packed

        icon_canvas = add_icon_canvas(
            f"btn_icon_{id(icon_path)}",
            icon_holder,
            icon_path,
            icon_pos=(0, 0),
            icon_size=(16, 16),
            canvas_size=(16, 16),
            visible=False,  # Don't display the canvas
        )

        # Extract PhotoImage and store reference
        icon = icon_canvas.image
        if not hasattr(self.state, "_btn_icon_refs"):
            self.state._btn_icon_refs = []
        self.state._btn_icon_refs.append(icon)

        return icon
