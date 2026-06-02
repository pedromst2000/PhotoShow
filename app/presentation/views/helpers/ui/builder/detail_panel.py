import tkinter as tk
from typing import List

from app.core.state.session import session
from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import (
    quickSandBold,
    quickSandBoldUnderline,
    quickSandRegular,
)
from app.presentation.styles.theme import BTN_BG, BTN_FG, PANEL_BG, TEXT_FG
from app.presentation.views.helpers.data.state import BasePhotoState
from app.presentation.views.helpers.ui.builder.photo_canvas import build_photo_canvas
from app.presentation.views.helpers.ui.interactions import handle_like, handle_rate
from app.presentation.widgets.helpers.icon_button import load_btn_icon, make_icon_button
from app.presentation.widgets.helpers.images import load_image
from app.presentation.widgets.star_rating import StarRatingWidget
from app.utils.file_utils import resolve_avatar_path

_ICON_DIR = "app/assets/images/UI_Icons/"


def build_detail_panel(
    parent: tk.Frame,
    state: BasePhotoState,
    *,  # * means all following args must be passed as kwargs, not positionally
    win: tk.Toplevel,
    img_refs: List,
    on_delete_callback=None,
):
    """
    Build the photo-detail panel and pack it into *parent*.

    Args:
        parent: Frame to pack everything into.
        state:  Any ``BasePhotoState`` subclass; ``selected_photo`` must be set.
        win:    The owning ``tk.Toplevel`` (used as ``parent`` for modals).
        img_refs: List for keeping ``PhotoImage`` references alive.
    """
    # Lazy cross-view imports to avoid circular dependencies at module load time.
    from app.presentation.views.album.main import open_album
    from app.presentation.views.comments.main import open_comments
    from app.presentation.views.helpers.ui.modals import open_report_dialog
    from app.presentation.views.profile.author import open_author_profile
    from app.presentation.widgets.helpers.ui_dialogs import handle_delete_photo

    photo = state.selected_photo or {}

    # ── Photo canvas ──────────────────────────────────────────────────────────
    build_photo_canvas(parent, state, img_refs)

    # ── Metadata container ────────────────────────────────────────────────────
    meta_frame = tk.Frame(parent, bg=PANEL_BG, pady=6, padx=10)
    meta_frame.pack(fill=tk.X, pady=(0, 0))

    # Hint label inside metadata (right-aligned above stars)
    hint_frame = tk.Frame(meta_frame, bg=PANEL_BG)
    hint_frame.pack(fill=tk.X)
    tk.Label(
        hint_frame,
        text="Hover over the stars to rate the photo",
        font=quickSandRegular(9),
        bg=PANEL_BG,
        fg=colors["primary-50"],
    ).pack(side=tk.RIGHT)

    # Row 1 — left: avatar + username | right: star rating
    row1 = tk.Frame(meta_frame, bg=PANEL_BG)
    row1.pack(fill=tk.X)

    # Avatar
    avatar_path = resolve_avatar_path(photo.get("owner_avatar"))
    avatar_canvas = tk.Canvas(
        row1, width=32, height=32, bg=PANEL_BG, highlightthickness=0, bd=0
    )
    avatar_canvas.pack(side=tk.LEFT, padx=(0, 6))
    av_img = load_image(avatar_path, size=(32, 32), canvas=avatar_canvas, x=0, y=0)
    img_refs.append(av_img)

    # Username link
    username = photo.get("user", "Unknown")
    username_lbl = tk.Label(
        row1,
        text=username,
        font=quickSandBoldUnderline(11),
        bg=PANEL_BG,
        fg=colors["primary-50"],
        cursor="hand2",
    )
    username_lbl.pack(side=tk.LEFT)
    username_lbl.bind("<Button-1>", lambda _e: open_author_profile(state))

    # Star rating (right side, interactive)
    star_frame = tk.Frame(row1, bg=PANEL_BG)
    star_frame.pack(side=tk.RIGHT)
    star_widget = StarRatingWidget(
        star_frame,
        bg=PANEL_BG,
        interactive=True,
        on_rate=lambda v: handle_rate(state, v, win),
        size=20,
    )
    star_widget.pack()
    star_widget.set_value(photo.get("user_rating") or photo.get("avg_rating") or 0)

    # Rating count label (next to stars, right-aligned)
    rating_count_lbl = tk.Label(
        row1,
        text=f"({photo.get('rating_count') or 0})",
        font=quickSandBold(10),
        bg=PANEL_BG,
        fg=colors["primary-50"],
    )
    rating_count_lbl.pack(side=tk.RIGHT, padx=(4, 0))

    # Row 2 — left: category badge | right: likes + comments counts
    row2 = tk.Frame(meta_frame, bg=PANEL_BG)
    row2.pack(fill=tk.X, pady=(6, 2))

    category = photo.get("category", "")
    if category:
        tk.Label(
            row2,
            text=f"  {category}  ",
            font=quickSandBold(9),
            bg=colors["secondary-500"],
            fg=colors["primary-50"],
            padx=4,
            pady=2,
        ).pack(side=tk.LEFT)

    counts_frame = tk.Frame(row2, bg=PANEL_BG)
    counts_frame.pack(side=tk.RIGHT)

    like_canvas = tk.Canvas(
        counts_frame, width=20, height=20, bg=PANEL_BG, highlightthickness=0, bd=0
    )
    like_canvas.pack(side=tk.LEFT, padx=(0, 4))
    like_stat_img = load_image(
        _ICON_DIR + "Like_Icon.png", size=(20, 20), canvas=like_canvas, x=0, y=0
    )
    like_canvas.image = like_stat_img

    likes_lbl = tk.Label(
        counts_frame,
        text=str(photo.get("likes", 0)),
        font=quickSandBold(10),
        bg=PANEL_BG,
        fg=colors["primary-50"],
    )
    likes_lbl.pack(side=tk.LEFT, padx=(0, 12))

    comment_canvas = tk.Canvas(
        counts_frame, width=20, height=20, bg=PANEL_BG, highlightthickness=0, bd=0
    )
    comment_canvas.pack(side=tk.LEFT, padx=(0, 4))
    comment_stat_img = load_image(
        _ICON_DIR + "Comment_Icon.png", size=(20, 20), canvas=comment_canvas, x=0, y=0
    )
    comment_canvas.image = comment_stat_img

    comments_lbl = tk.Label(
        counts_frame,
        text=str(photo.get("comments", 0)),
        font=quickSandBold(10),
        bg=PANEL_BG,
        fg=colors["primary-50"],
    )
    comments_lbl.pack(side=tk.LEFT)

    # ── Description ───────────────────────────────────────────────────────────
    description = photo.get("description", "")
    if description:
        description_frame = tk.Frame(parent, bg=colors["primary-50"])
        description_frame.pack(fill=tk.X, pady=(4, 0))
        tk.Label(
            description_frame,
            text=description,
            font=quickSandRegular(12),
            bg=colors["primary-50"],
            fg=TEXT_FG,
            wraplength=520,
            justify=tk.LEFT,
        ).pack(anchor=tk.W, padx=4, pady=(8, 4))

    # ── Action buttons ────────────────────────────────────────────────────────
    album_icon = load_btn_icon(parent, state, _ICON_DIR + "Eye_Icon_V2.png")
    comments_icon = load_btn_icon(parent, state, _ICON_DIR + "Comment_Icon_V2.png")

    row_btns = tk.Frame(parent, bg=colors["primary-50"])
    row_btns.pack(fill=tk.X, pady=(8, 4))

    # See Album (always available)
    album_btn = make_icon_button(
        row_btns,
        label="  See Album",
        command=lambda: open_album(state),
        btn_bg=BTN_BG,
        btn_fg=BTN_FG,
        icon=album_icon,
    )
    album_btn.pack(side=tk.LEFT, padx=(0, 6))
    album_btn.config(state=tk.NORMAL)

    # See Comments (always available)
    comments_btn = make_icon_button(
        row_btns,
        label="  See Comments",
        command=lambda: open_comments(state),
        btn_bg=BTN_BG,
        btn_fg=BTN_FG,
        icon=comments_icon,
    )
    comments_btn.pack(side=tk.LEFT, padx=(0, 6))
    comments_btn.config(state=tk.NORMAL)

    if not state.is_unsigned:
        # Add Like / Unlike (toggle on click)
        like_icon = load_btn_icon(parent, state, _ICON_DIR + "Like_Icon_V2.png")
        unlike_icon = load_btn_icon(parent, state, _ICON_DIR + "Unlike_Icon_V2.png")
        initial_liked = bool(photo.get("has_liked"))

        def _on_like_click():
            handle_like(state, win)
            updated = state.selected_photo or {}
            liked = bool(updated.get("has_liked"))
            like_btn.config(
                text="  Unlike" if liked else "  Add Like",
                image=unlike_icon if liked else like_icon,
            )
            likes_lbl.config(text=str(updated.get("likes", 0)))

        like_btn = make_icon_button(
            row_btns,
            label="  Unlike" if initial_liked else "  Add Like",
            command=_on_like_click,
            btn_bg=BTN_BG,
            btn_fg=BTN_FG,
            icon=unlike_icon if initial_liked else like_icon,
        )
        like_btn.pack(side=tk.LEFT, padx=(0, 6))
        like_btn.config(state=tk.NORMAL)

        # Delete Photo (admin or owner) / Report Photo (others)
        can_delete = session.role == "admin" or (
            session.user_id is not None and photo.get("owner_id") == session.user_id
        )
        if can_delete:
            delete_icon = load_btn_icon(parent, state, _ICON_DIR + "Remove_Icon.png")

            if on_delete_callback is not None:
                # Notifications path: delete DB notifications first, then photo.
                _pid = photo.get("id")

                def _on_delete():
                    from app.controllers.notification_controller import (
                        NotificationController,
                    )
                    from app.presentation.widgets.helpers.ui_dialogs import (
                        show_confirmation,
                        show_error,
                        show_info,
                    )

                    confirmed = show_confirmation(
                        win,
                        "Delete Photo",
                        "Are you sure you want to delete this photo?\n\nThis action cannot be undone.",
                    )
                    if not confirmed:
                        return

                    # Remove DB notifications BEFORE photo deletion (FK still set).
                    NotificationController.delete_by_photo(_pid)

                    from app.controllers.photo_controller import PhotoController

                    success, message = PhotoController.delete_photo(_pid)
                    if success:
                        show_info(win, "Success", message)
                        on_delete_callback(_pid)
                        win.destroy()
                    else:
                        show_error(win, "Error", message)

            else:
                # Explore / album path: standard catalog-aware deletion.
                def _on_delete():
                    count_before = len(state.photos)
                    handle_delete_photo(state)
                    if len(state.photos) < count_before:
                        win.destroy()

            action_btn = make_icon_button(
                row_btns,
                label="  Delete Photo",
                command=_on_delete,
                btn_bg=BTN_BG,
                btn_fg=BTN_FG,
                icon=delete_icon,
            )
        else:
            report_icon = load_btn_icon(parent, state, _ICON_DIR + "Report_Icon.png")
            action_btn = make_icon_button(
                row_btns,
                label="  Report Photo",
                command=lambda: open_report_dialog(win, photo_id=photo.get("id")),
                btn_bg=BTN_BG,
                btn_fg=BTN_FG,
                icon=report_icon,
            )
        action_btn.pack(side=tk.LEFT, padx=(0, 6))
        action_btn.config(state=tk.NORMAL)
