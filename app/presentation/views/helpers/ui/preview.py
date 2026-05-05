import tkinter as tk
from typing import (  # For type hinting tk.Button without importing the entire module
    Optional,
    cast,
)

from app.core.state.session import session
from app.presentation.views.helpers.data.state import BasePhotoState
from app.presentation.widgets.helpers.images import load_image
from app.utils.file_utils import resolve_image_path


def _display_carousel_image(state: BasePhotoState, img_path: Optional[str]) -> None:
    """
    Display image on carousel or show empty state.

    Single Responsibility: Only handles carousel image display.

    Args:
        state: Explore view state.
        img_path: Path to image (relative or absolute).
    """
    if not state.carousel:
        return

    resolved_path = resolve_image_path(img_path) if img_path else None

    if resolved_path:
        state.carousel.display_photo(resolved_path)
    else:
        state.carousel.show_empty(
            f"Image not found: {img_path if img_path else 'unknown'}"
        )

    # Enable nav if more than one photo
    total = len(state.photos)
    state.carousel.set_nav_enabled(prev=total > 1, next_=total > 1)


def reset_preview(state: BasePhotoState, carousel_message: str = "No photo selected"):
    """
    Reset preview panel to empty/default state.

    Args:
        state (BasePhotoState): The current state of the explore view.
        carousel_message (str): Message to display in the carousel. Defaults to "No photo selected".
    """
    if state.carousel:
        state.carousel.show_empty(carousel_message)
        state.carousel.set_nav_enabled(prev=False, next_=False)

    _hide_metadata(state)

    # Hide action buttons when no photo is selected
    for btn in (
        getattr(state, "like_btn", None),
        getattr(state, "details_btn", None),
        getattr(state, "comments_btn", None),
        getattr(state, "album_btn", None),
        getattr(state, "delete_btn", None),
        getattr(state, "report_btn", None),
    ):
        if btn:
            btn.grid_remove()

    _set_action_buttons_state(state, enabled=False)


def update_preview(state: BasePhotoState):
    """
    Update preview panel to display selected photo.

    Args:
        state (BasePhotoState): The current state of the explore view.
    """
    photo = state.selected_photo
    if photo is None:
        reset_preview(state)
        return

    # ── Carousel image ────────────────────────────────────────────────
    _display_carousel_image(state, photo.get("image"))

    # ── Avatar + Username ─────────────────────────────────────────────
    is_own = photo.get("owner_id") == session.user_id
    if state.avatar_canvas and state.username_label:
        current_owner_id = photo.get("owner_id")
        # Only reload avatar if owner changed (avoid redundant PIL operations on navigation)
        if (
            not is_own
            and photo.get("user")
            and current_owner_id != state._cached_avatar_owner_id
        ):
            # Load avatar image (only when owner changes)
            avatar_path = (
                photo.get("owner_avatar")
                or "app/assets/images/profile_avatars/default_avatar.jpg"
            )
            from app.utils.file_utils import resolve_avatar_path

            avatar_path = resolve_avatar_path(avatar_path)
            state.avatar_canvas.delete("all")
            img = load_image(
                avatar_path, size=(40, 40), canvas=state.avatar_canvas, x=0, y=0
            )
            state._avatar_img_ref = img
            state._cached_avatar_owner_id = current_owner_id
            state.avatar_canvas.pack(side=tk.LEFT, padx=(0, 8))

            state.username_label.config(text=photo["user"])
            state.username_label.pack(side=tk.LEFT, padx=(0, 20))
        elif is_own or not photo.get("user"):
            state.avatar_canvas.pack_forget()
            state.username_label.pack_forget()
            state._cached_avatar_owner_id = None

    # ── Star rating ───────────────────────────────────────────────────
    if state.star_widget:
        # Use weighted rating for display (more professional, accounts for vote reliability)
        weighted_rating = photo.get("weighted_rating", photo.get("avg_rating", 1.0))
        rating_count = photo.get("rating_count", 0)

        # Display the weighted average rating
        state.star_widget.set_value(weighted_rating)
        can_rate = not state.is_unsigned
        state.star_widget.set_interactive(can_rate)

    # ── Rating count label ────────────────────────────────────────────
    if state.rating_count_label:
        rating_count = photo.get("rating_count", 0)
        state.rating_count_label.config(text=f"({rating_count})")

    # ── Likes & comments ──────────────────────────────────────────────
    if state.likes_label:
        state.likes_label.config(text=str(photo.get("likes", 0)))
    if state.comments_label:
        state.comments_label.config(text=str(photo.get("comments", 0)))

    _show_metadata(state)

    # ── Like button label + icon ──────────────────────────────────
    if state.like_btn:
        has_liked = photo.get("has_liked")
        label = "  Unlike" if has_liked else "  Add Like"
        icon = (
            getattr(state.like_btn, "_unlike_icon", None)
            if has_liked
            else getattr(state.like_btn, "_like_icon", None)
        )
        if icon:
            state.like_btn.config(text=label, image=icon)
        else:
            state.like_btn.config(text=label)

    # ── Show and update action buttons ────────────────────────────────
    # Show the always-visible buttons
    for btn in (
        state.like_btn,
        state.details_btn,
        state.comments_btn,
        state.album_btn,
    ):
        if btn:
            btn.grid()

    # Update delete/report button based on ownership
    _update_delete_report_button(state)
    _set_action_buttons_state(state, enabled=not state.is_unsigned)


def _update_delete_report_button(state: BasePhotoState):
    """
    Update delete/report button visibility based on user ownership and admin status.

    Button visibility logic:
    - Admin: Show delete button only (no report)
    - Owner (regular user): Show delete button only (can't report own photos)
    - Other users: Show report button only, unless photo owner is admin
    - Never show report button for admin-owned photos or own photos

    Args:
        state (BasePhotoState): The current state of the explore view.
    """
    if state.selected_photo is None:
        return

    photo_owner_id = state.selected_photo.get("owner_id")
    is_owner = photo_owner_id == session.user_id
    is_admin = session.is_admin
    owner_is_admin = state.selected_photo.get("owner_is_admin", False)

    # Get button references
    delete_btn = getattr(state, "delete_btn", None)
    report_btn = getattr(state, "report_btn", None)

    if is_admin:
        # Admin: show delete only, hide report
        if delete_btn:
            delete_btn.grid()
        if report_btn:
            report_btn.grid_remove()
    elif is_owner:
        # Owner: show delete only (can't report own photos)
        if delete_btn:
            delete_btn.grid()
        if report_btn:
            report_btn.grid_remove()
    else:
        # Other users: show report only if photo owner is NOT admin
        if delete_btn:
            delete_btn.grid_remove()
        if report_btn:
            if owner_is_admin:
                report_btn.grid_remove()  # Can't report admin photos
            else:
                report_btn.grid()


def _show_metadata(state: BasePhotoState):
    """
    Show metadata frame above action buttons.

    Args:
        state (BasePhotoState): The current state of the explore view.
    """
    if state.metadata_frame:
        # Ensure metadata is packed before the action buttons frame so
        # it remains visually above the buttons after being hidden/shown.
        try:
            if getattr(state, "btns_frame", None):
                state.metadata_frame.pack(
                    before=state.btns_frame, fill="x", padx=10, pady=5
                )
            else:
                state.metadata_frame.pack(fill="x", padx=10, pady=5)
        except Exception:
            # Fallback to normal pack if 'before' isn't supported in this context
            state.metadata_frame.pack(fill="x", padx=10, pady=5)


def _hide_metadata(state: BasePhotoState):
    """
    Hide metadata frame and reset values.

    Args:
        state (BasePhotoState): The current state of the explore view.
    """
    if state.metadata_frame:
        state.metadata_frame.pack_forget()
    if state.avatar_canvas:
        state.avatar_canvas.pack_forget()
    if state.username_label:
        state.username_label.pack_forget()
    if state.likes_label:
        state.likes_label.config(text="0")
    if state.comments_label:
        state.comments_label.config(text="0")
    if state.rating_count_label:
        state.rating_count_label.config(text="")
    if state.star_widget:
        state.star_widget.set_value(0.0)


def _set_action_buttons_state(state: BasePhotoState, enabled: bool):
    """
    Enable or disable all action buttons.

    Special handling:
    - delete_btn: Always enabled for admins, otherwise follows enabled parameter
    - All other buttons: Follow the enabled parameter

    Args:
        state (BasePhotoState): The current state of the explore view.
        enabled (bool): Whether to enable or disable the buttons.
    """
    s = tk.NORMAL if enabled else tk.DISABLED

    # Special case: delete button always enabled for admins
    delete_btn = getattr(state, "delete_btn", None)
    if delete_btn:
        delete_state = tk.NORMAL if session.is_admin else s
        cast(tk.Button, delete_btn).config(state=delete_state)  # type: ignore[call-overload]

    # All other buttons follow the enabled parameter
    for btn in (
        state.like_btn,
        state.details_btn,
        state.comments_btn,
        state.album_btn,
        state.report_btn,
    ):
        if btn:
            cast(tk.Button, btn).config(state=s)  # type: ignore[call-overload]
