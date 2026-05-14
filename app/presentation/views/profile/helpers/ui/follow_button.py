import tkinter as tk

from app.controllers.user_controller import UserController
from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold
from app.presentation.widgets.helpers.button import make_button, switch_button
from app.presentation.widgets.helpers.images import load_image


def build_profile_follow_button(
    window: tk.Toplevel,
    *,
    profile_user_id: int,
    role_badge: tk.Label,
    banner_canvas: tk.Canvas,
    followers_text_id: int,
):
    """
    Render the Follow/Unfollow button on a profile page, allowing the logged-in user to follow or unfollow the profile owner.

    Args:
        window: The profile Toplevel window.
        profile_user_id: The ID of the user whose profile is being viewed.
        role_badge: The role-badge Label used to anchor the button position.
        banner_canvas: The banner Canvas used to refresh the follower count.
        followers_text_id: Canvas text-item ID that shows the follower count.
    """
    is_following = UserController.is_following(profile_user_id)

    follow_icon = load_image(
        "app/assets/images/UI_Icons/Follow_icon.png", size=(20, 20)
    )
    unfollow_icon = load_image(
        "app/assets/images/UI_Icons/Unfollow_Icon.png", size=(20, 20)
    )
    # Keep image references alive for the lifetime of the window.
    window._follow_icons = (follow_icon, unfollow_icon)  # type: ignore[attr-defined]

    _btn_style = dict(
        font=quickSandBold(11),
        bg=colors["accent-300"],
        fg=colors["secondary-500"],
        activebackground=colors["accent-100"],
        activeforeground=colors["secondary-500"],
        borderwidth=0,
        highlightthickness=0,
        cursor="hand2",
        padx=10,
        pady=4,
    )

    icon = unfollow_icon if is_following else follow_icon
    label = "  Unfollow" if is_following else "  Follow"
    btn = make_button(window, label, icon=icon, **_btn_style)
    state_ref = [is_following]

    def _place() -> None:
        role_badge.update_idletasks()
        bx = role_badge.winfo_x() + role_badge.winfo_width() + 12
        btn.place(x=bx, y=53)

    def _toggle() -> None:
        if state_ref[0]:
            UserController.unfollow_user(profile_user_id)
            state_ref[0] = False
        else:
            UserController.follow_user(profile_user_id)
            state_ref[0] = True

        new_stats = UserController.get_profile_stats(profile_user_id)
        banner_canvas.itemconfigure(
            followers_text_id,
            text=f"{new_stats['follower_count']} followers",
        )
        new_icon = unfollow_icon if state_ref[0] else follow_icon
        new_label = "  Unfollow" if state_ref[0] else "  Follow"
        switch_button(btn, new_label, icon=new_icon)

    btn.configure(command=_toggle)
    window.after(10, _place)
