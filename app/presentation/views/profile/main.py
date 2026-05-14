import tkinter as tk
from typing import Optional

from app.controllers.user_controller import UserController
from app.core.state.session import session
from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold, quickSandRegular
from app.presentation.views.profile.helpers.data.feature_photos import (
    load_feature_photos,
)
from app.presentation.views.profile.helpers.ui.action_buttons import (
    build_profile_action_buttons,
)
from app.presentation.views.profile.helpers.ui.feature_photos import (
    build_feature_photos,
)
from app.presentation.views.profile.helpers.ui.follow_button import (
    build_profile_follow_button,
)
from app.presentation.views.profile.helpers.ui.nav import build_profile_nav
from app.presentation.widgets.helpers.images import load_image
from app.presentation.widgets.helpers.ui_dialogs import show_limited_access
from app.presentation.widgets.window import create_toplevel
from app.utils.file_utils import resolve_avatar_path

# ── Layout constants ───────────────────────────────────────────────────────────
_WIN_W = 1000
_WIN_H = 530
_BANNER_H = 155
_NAV_H = 50
_PHOTO_W = 240
_PHOTO_H = 160


def profileWindow(user_id: Optional[int] = None) -> None:
    """
    Display the profile window.

    Args:
        user_id: Optional user ID to view. If None, shows the logged-in user's profile.
    """
    # ── Resolve context ────────────────────────────────────────────────
    # When called without arguments, show the logged-in user's own profile.
    effective_user_id: Optional[int] = (
        user_id if user_id is not None else session.user_id
    )
    own_profile: bool = (
        effective_user_id is not None and effective_user_id == session.user_id
    )
    is_logged_in: bool = session.user_id is not None

    if own_profile:
        userID: int = session.user_id
        userPayload: dict = session.user_data
    else:
        userID = effective_user_id
        userPayload = UserController.get_profile(effective_user_id) or {}
        if not userPayload:
            # Profile not found — show a minimal error window instead of a blank screen.
            win = create_toplevel(
                title="👤 Profile",
                width=_WIN_W,
                height=_WIN_H,
                icon_path="app/assets/PhotoShowIcon.ico",
                bg_color=colors["primary-50"],
            )
            tk.Label(
                win,
                text="Profile not available",
                font=quickSandBold(16),
                bg=colors["primary-50"],
                fg=colors["secondary-500"],
            ).pack(expand=True)
            win.grab_set()
            return

    stats: dict = UserController.get_profile_stats(userID)
    follower_count: int = stats["follower_count"]
    photo_count: int = stats["photo_count"]
    role: str = userPayload.get("role", "")

    # Viewer role reflects the logged-in user, not the profile being visited.
    _viewer_role: str = (
        (session.user_data or {}).get("role", "") if is_logged_in else ""
    )
    is_unsigned: bool = _viewer_role == "unsigned"

    # ── Window ────────────────────────────────────────────────────────
    _profileWindow_: tk.Toplevel = create_toplevel(
        title="👤 Profile 👤",
        width=_WIN_W,
        height=_WIN_H,
        icon_path="app/assets/PhotoShowIcon.ico",
        bg_color=colors["primary-50"],
    )

    # ── Banner canvas ─────────────────────────────────────────────────
    banner_canvas = tk.Canvas(
        _profileWindow_,
        width=_WIN_W,
        height=_BANNER_H,
        highlightthickness=0,
        borderwidth=0,
    )
    banner_canvas.place(x=0, y=0)

    banner_img = load_image(
        "app/assets/images/profile/bannerProfile.png",
        size=(_WIN_W, _BANNER_H),
        canvas=banner_canvas,
        x=0,
        y=0,
    )
    banner_canvas.image = banner_img  # type: ignore[attr-defined]

    # ── Avatar ────────────────────────────────────────────────────────
    avatar_path = resolve_avatar_path(userPayload.get("avatar"))
    avatar_canvas = tk.Canvas(
        _profileWindow_,
        width=130,
        height=130,
        highlightthickness=0,
        borderwidth=0,
        bg=colors["secondary-500"],
    )
    avatar_canvas.place(x=40, y=12)
    avatar_img = load_image(
        avatar_path, size=(130, 130), canvas=avatar_canvas, x=0, y=0
    )
    avatar_canvas.image = avatar_img  # type: ignore[attr-defined]

    # ── Username ──────────────────────────────────────────────────────
    banner_canvas.create_text(
        190,
        22,
        text=userPayload.get("username", ""),
        font=quickSandBold(20),
        anchor=tk.NW,
        fill=colors["primary-50"],
    )

    # ── Role badge ────────────────────────────────────────────────────
    role_badge = tk.Label(
        _profileWindow_,
        text=role,
        font=quickSandBold(11) if role == "admin" else quickSandRegular(11),
        bg=colors["primary-50"] if role == "admin" else colors["secondary-400"],
        fg=colors["secondary-500"] if role == "admin" else colors["primary-50"],
        padx=8,
        pady=2,
    )
    role_badge.place(x=190, y=57)

    # ── Stats: photos + followers ─────────────────────────────────────
    # Stats are rendered before the follow button so followers_text_id is
    # available to pass to build_profile_follow_button.
    banner_canvas.create_text(
        695,
        128,
        text=f"{photo_count} photos",
        font=quickSandBold(12),
        anchor=tk.NW,
        fill=colors["primary-50"],
    )
    followers_icon = load_image(
        "app/assets/images/UI_Icons/followersIcon.png",
        size=(20, 20),
        canvas=banner_canvas,
        x=820,
        y=126,
    )
    _followers_text_id = banner_canvas.create_text(
        845,
        128,
        text=f"{follower_count} followers",
        font=quickSandRegular(12),
        anchor=tk.NW,
        fill=colors["primary-50"],
    )

    # Store references to banner elements that may need to be updated by the follow/unfollow button logic.
    _profileWindow_._banner_refs = (banner_img, avatar_img, followers_icon)  # type: ignore[attr-defined]

    # ── Follow / Unfollow button ──────────────────────────────────────
    if not own_profile and is_logged_in and not is_unsigned:
        build_profile_follow_button(
            _profileWindow_,
            profile_user_id=userID,
            role_badge=role_badge,
            banner_canvas=banner_canvas,
            followers_text_id=_followers_text_id,
        )

    # ── Navigation bar ────────────────────────────────────────────────
    # Unsigned users cannot access albums, favorites, contacts, or reports.
    show_albuns = own_profile and not is_unsigned
    show_favorites = own_profile and not is_unsigned
    show_contacts = own_profile and role == "admin"
    show_reports = own_profile and role == "admin"

    if show_albuns or show_favorites or show_contacts or show_reports:
        build_profile_nav(
            _profileWindow_,
            banner_height=_BANNER_H,
            nav_height=_NAV_H,
            win_width=_WIN_W,
            show_albuns=show_albuns,
            show_favorites=show_favorites,
            show_contacts=show_contacts,
            show_reports=show_reports,
            own_profile=own_profile,
            username=userPayload.get("username", ""),
        )

    # ── Unsigned-user / unsigned-visitor notice ───────────────────────
    if is_unsigned or not is_logged_in:
        show_limited_access(
            _profileWindow_,
            "You can view feature photos but cannot follow users, "
            "manage albums or favorites",
        )

    # ── Feature Photos ────────────────────────────────────────────────
    has_nav = show_albuns or show_favorites or show_contacts or show_reports
    content_y = _BANNER_H + _NAV_H if has_nav else _BANNER_H

    tk.Label(
        _profileWindow_,
        text="Feature Photos",
        font=quickSandBold(16),
        bg=colors["primary-50"],
        fg=colors["secondary-500"],
    ).place(x=40, y=content_y + 15)

    feature_photos = load_feature_photos(userPayload.get("username", ""))
    photos_y = content_y + 50

    build_feature_photos(
        _profileWindow_,
        feature_photos,
        photos_y=photos_y,
        photo_w=_PHOTO_W,
        photo_h=_PHOTO_H,
        is_unsigned=is_unsigned,
        is_logged_in=is_logged_in,
        own_profile=own_profile,
        win_h=_WIN_H,
    )

    # ── Bottom action buttons (own profile, non-unsigned only) ────────
    if own_profile and not is_unsigned:
        build_profile_action_buttons(_profileWindow_, win_w=_WIN_W, win_h=_WIN_H)

    _profileWindow_.grab_set()
