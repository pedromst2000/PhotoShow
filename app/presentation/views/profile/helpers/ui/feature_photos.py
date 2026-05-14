import tkinter as tk
from typing import List, Optional

from app.presentation.styles.colors import colors
from app.presentation.views.helpers.ui.builder.empty_state import (
    build_profile_photos_empty_state,
)
from app.presentation.widgets.helpers.images import load_image


def build_feature_photos(
    window: tk.Toplevel,
    feature_photos: list,
    *,
    photos_y: int,
    photo_w: int,
    photo_h: int,
    is_unsigned: bool,
    is_logged_in: bool,
    own_profile: bool,
    win_h: int,
    photo_positions: Optional[List[int]] = None,
):
    """Render the feature photos grid, or an empty state when there are none.

    Args:
        window: The profile Toplevel window.
        feature_photos: Ordered list of photo dicts to display (max 3).
        photos_y: Top Y-coordinate for the photo canvases.
        photo_w: Width of each photo canvas in pixels.
        photo_h: Height of each photo canvas in pixels.
        is_unsigned: True if the current viewer is an unsigned user.
        is_logged_in: True if there is an authenticated session.
        own_profile: True when displaying the current user's own profile.
        win_h: Full pixel height of the window (used for rely calculations).
        photo_positions: X-positions for each photo slot.
                         Defaults to ``[40, 380, 720]``.
    """
    _positions = photo_positions or [40, 380, 720]

    if feature_photos:
        img_refs: list = []
        for i, photo in enumerate(feature_photos):
            px = _positions[i] if i < len(_positions) else _positions[-1]
            photo_canvas = tk.Canvas(
                window,
                width=photo_w,
                height=photo_h,
                bg=colors["secondary-400"],
                highlightthickness=1,
                highlightbackground=colors["secondary-400"],
            )
            photo_canvas.place(x=px, y=photos_y)

            img_path = photo.get("image")
            if img_path:
                ph_img = load_image(
                    img_path, size=(photo_w, photo_h), canvas=photo_canvas, x=0, y=0
                )
                img_refs.append(ph_img)
                photo_canvas.image = ph_img  # type: ignore[attr-defined]

        # Keep photo image references alive for the window lifetime.
        window._feature_photo_refs = img_refs  # type: ignore[attr-defined]
    else:
        build_profile_photos_empty_state(
            window,
            is_unsigned=is_unsigned,
            is_logged_in=is_logged_in,
            own_profile=own_profile,
            icon_rely=(photos_y + 30) / win_h,
            title_rely=(photos_y + 100) / win_h,
            subtitle_rely=(photos_y + 130) / win_h,
        )
