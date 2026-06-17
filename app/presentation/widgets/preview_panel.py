import tkinter as tk
from typing import Callable, Optional

from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold, quickSandBoldUnderline
from app.presentation.widgets.helpers.icon_button import load_btn_icon, make_icon_button
from app.presentation.widgets.helpers.images import load_image
from app.presentation.widgets.photo_carousel import PhotoCarouselWidget
from app.presentation.widgets.star_rating import StarRatingWidget


class PreviewPanelWidget(tk.Frame):
    """
    Generic preview panel widget with photo carousel and optional metadata.

    All behaviour (navigation, rating, username click, action buttons) is
    provided via callbacks, making this widget reusable across different
    views (Explore, Album, Admin, etc.) without modifications.

    Button config dict schema::

        {
            "name":        str,       # attribute name stored on state (e.g. "like_btn")
            "label":       str,       # button text
            "icon":        str,       # icon filename (under UI_Icons/)
            "command":     Callable,  # action executed on click
            "unlike_icon": str,       # (optional) alternate icon filename for toggle state
        }
    """

    def __init__(
        self,
        parent: tk.Frame,
        state,
        title: str = "Preview",
        subtitle: Optional[str] = None,
        show_metadata: bool = True,
        on_prev: Optional[Callable] = None,
        on_next: Optional[Callable] = None,
        on_username_click: Optional[Callable] = None,
        on_rate: Optional[Callable] = None,
        buttons: Optional[list[dict]] = None,
        x_pos: int = 545,
        width: int = 755,
        height: int = 674,
        panel_bg: Optional[str] = None,
        btn_bg: Optional[str] = None,
        btn_fg: Optional[str] = None,
        canvas_bg: Optional[str] = None,
    ):
        """
        Create and place a preview panel.

        Args:
            parent: Parent Tkinter frame.
            state: Shared state object; carousel, metadata widget refs, and button
                refs will be stored here as attributes.
            title: Main heading text.
            subtitle: Optional secondary heading text (shown only when not None).
            show_metadata: Whether to show avatar / username / stars / counts row.
            on_prev: No-arg callable for carousel "previous" navigation.
            on_next: No-arg callable for carousel "next" navigation.
            on_username_click: No-arg callable when username/avatar is clicked.
            on_rate: Callable receiving the chosen star value (int) on rating.
            buttons: List of button config dicts (see class docstring).
                Buttons are stored on *state* by their "name" key.
            x_pos: X position of the panel in parent.
            width: Panel pixel width.
            height: Panel pixel height.
            panel_bg: Panel background colour override.
            btn_bg: Button background colour override.
            btn_fg: Button foreground colour override.
            canvas_bg: Carousel canvas background colour override.
        """
        self.parent = parent
        self.state = state
        self.title = title
        self.subtitle = subtitle
        self.show_metadata = show_metadata
        self._on_prev = on_prev
        self._on_next = on_next
        self._on_username_click = on_username_click
        self._on_rate = on_rate
        self.buttons = buttons or []
        self.x_pos = x_pos
        self.width = width
        self.height = height

        self._panel_bg = panel_bg if panel_bg is not None else colors["secondary-300"]
        self._btn_bg = btn_bg if btn_bg is not None else colors["accent-300"]
        self._btn_fg = btn_fg if btn_fg is not None else colors["secondary-500"]
        self._canvas_bg = (
            canvas_bg if canvas_bg is not None else colors["secondary-400"]
        )
        self._icon_dir = "app/assets/images/UI_Icons/"

        self._build_preview_panel()

    def _build_preview_panel(self):
        """Build the preview panel with carousel, optional metadata, and action buttons."""
        right = tk.Frame(self.parent, bg=self._panel_bg, bd=0)
        right.place(x=self.x_pos, y=0, width=self.width, height=self.height)

        # ── Header ──────────────────────────────────────────────────────
        header_frame = tk.Frame(right, bg=self._panel_bg)
        header_frame.pack(fill="x", padx=15, pady=(10, 2))

        tk.Label(
            header_frame,
            text=self.title,
            font=quickSandBold(14),
            bg=self._panel_bg,
            fg=colors["secondary-500"],
        ).pack(anchor="w")

        if self.subtitle is not None:
            tk.Label(
                header_frame,
                text=self.subtitle,
                font=quickSandBold(12),
                bg=self._panel_bg,
                fg=colors["primary-50"],
                wraplength=700,
                justify="left",
            ).pack(anchor="w")

        # ── Preview column: carousel → metadata → buttons ────────────────
        preview_col = tk.Frame(right, bg=self._panel_bg)
        preview_col.pack(fill="both", expand=False, padx=0, pady=0)

        # ── Carousel ─────────────────────────────────────────────────────
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
            on_prev=self._on_prev,
            on_next=self._on_next,
        )

        # ── Metadata section ─────────────────────────────────────────────
        if self.show_metadata:
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
                on_rate=self._on_rate,
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

            # Bind username / avatar click
            if self._on_username_click is not None:
                _on_click = self._on_username_click  # capture for mypy type narrowing
                username_lbl.bind("<Button-1>", lambda e: _on_click())
                avatar_canvas.bind("<Button-1>", lambda e: _on_click())

        # ── Action buttons ───────────────────────────────────────────────
        if self.buttons:
            btns_frame = tk.Frame(preview_col, bg=self._panel_bg)
            btns_frame.pack(fill="x", padx=10, pady=(12, 0))
            self.state.btns_frame = btns_frame

            btn_widgets = []
            for btn_cfg in self.buttons:
                name = btn_cfg["name"]
                label = btn_cfg["label"]
                icon_file = btn_cfg["icon"]
                command = btn_cfg["command"]
                unlike_file = btn_cfg.get("unlike_icon")

                icon = load_btn_icon(
                    self.parent, self.state, self._icon_dir + icon_file
                )
                unlike_icon = (
                    load_btn_icon(self.parent, self.state, self._icon_dir + unlike_file)
                    if unlike_file
                    else None
                )

                btn = make_icon_button(
                    btns_frame,
                    label=label,
                    command=command,
                    btn_bg=self._btn_bg,
                    btn_fg=self._btn_fg,
                    icon=icon,
                    like_icon=icon if unlike_icon else None,
                    unlike_icon=unlike_icon,
                )
                setattr(self.state, name, btn)
                btn_widgets.append(btn)

            btns_frame.grid_columnconfigure(list(range(5)), weight=0)
            for idx, btn in enumerate(btn_widgets):
                row = idx // 5
                col = idx % 5
                btn.grid(row=row, column=col, padx=4, pady=2, sticky="ew")

        # ── Initial empty state ──────────────────────────────────────────
        self.state.carousel.show_empty("No photo selected")
        self.state.carousel.set_nav_enabled(prev=False, next_=False)

        if (
            self.show_metadata
            and hasattr(self.state, "metadata_frame")
            and self.state.metadata_frame
        ):
            self.state.metadata_frame.pack_forget()

        for btn_cfg in self.buttons:
            name = btn_cfg.get("name")
            if name:
                btn = getattr(self.state, name, None)
                if btn:
                    btn.grid_remove()
                    btn.config(state=tk.DISABLED)
