import tkinter as tk

from app.core.state.session import session
from app.presentation.layout.menu.helpers.menu_button_state import (
    MenuButtonStateManager,
)
from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold, quickSandRegular
from app.presentation.views.home.contact_admin.dialog import open_contact_admin
from app.presentation.widgets.helpers.button import on_enter as button_on_enter
from app.presentation.widgets.helpers.button import on_leave as button_on_leave
from app.presentation.widgets.helpers.window import load_image
from app.presentation.widgets.window import create_main_window


def homeBannedWindow():
    """
    Display the home window for a banned user.
    """

    # open the window using the reusable helper (centering, sizing, icon, bg)
    homeBannedWindowWidth: int = 1350  # width of the window
    homeBannedWindowHeight: int = 700  # height of the window

    _homeBannedWindow_: tk.Tk = create_main_window(
        title="PhotoShow - Banned Notice",
        width=homeBannedWindowWidth,
        height=homeBannedWindowHeight,
        icon_path="app/assets/PhotoShowIcon.ico",
        bg_color=colors["primary-50"],
    )

    homeBannedCanvas: tk.Canvas = tk.Canvas(_homeBannedWindow_, width=1350, height=700)
    homeBannedCanvas.place(x=0, y=0)

    homeBannedImage = load_image(
        "app/assets/images/home/mainBlockedBackground.png",
        size=(1350, 700),
        canvas=homeBannedCanvas,
        x=0,
        y=0,
    )

    backgroundBanned = load_image(
        "app/assets/images/home/blockedBackground.png",
        size=(1146, 530),
        canvas=homeBannedCanvas,
        x=102,
        y=102,
    )

    logoImage = load_image(
        "app/assets/images/Logo.png",
        size=(306, 65),
        canvas=homeBannedCanvas,
        x=522,
        y=70,
    )

    # title
    homeBannedCanvas.create_text(
        675,
        200,
        text="ACCOUNT SUPSENSION NOTICE",
        font=quickSandBold(18),
        fill=colors["primary-50"],
        anchor=tk.CENTER,
    )

    # first paragraph
    homeBannedCanvas.create_text(
        675,
        270,
        text="We regret to inform you that your account has been suspended due to a violation of our community guidelines.",
        font=quickSandRegular(14),
        fill=colors["accent-100"],
        anchor=tk.CENTER,
    )

    # second paragraph
    homeBannedCanvas.create_text(
        658,
        320,
        text="After careful review from our admin, it has been determined  that your actions have breached our policies, resulting in the necessity to suspend your account.",
        font=quickSandRegular(14),
        fill=colors["accent-100"],
        anchor=tk.CENTER,
        width=950,
    )

    # third paragraph
    homeBannedCanvas.create_text(
        638,
        385,
        text="Please be aware we are commited to maintaining a safe and respectful environment for all users. Any activities that undermine this commitment, such as explicit content are taken seriously.",
        font=quickSandRegular(14),
        fill=colors["accent-100"],
        anchor=tk.CENTER,
        width=950,
    )

    # fourth paragraph
    homeBannedCanvas.create_text(
        628,
        435,
        text="If you believe this suspension is in error would like to appeal the decision, please contact our admin.",
        font=quickSandRegular(14),
        fill=colors["accent-100"],
        anchor=tk.CENTER,
    )

    # contact Admin button
    contactAdminButton: tk.Button = tk.Button(
        _homeBannedWindow_,
        width=24,
        height=2,
        text="Contact Admin",
        borderwidth=10,
        font=quickSandBold(13),
        background=colors["accent-300"],
        bd=0,
        highlightthickness=0,
        activebackground=colors["accent-100"],
        cursor="hand2",
    )

    contactAdminButton.place(x=560, y=500)

    # sign out button with hover behavior (reusing Menu helpers)
    signout_state_manager = MenuButtonStateManager()
    signout_default = load_image(
        "app/assets/images/home/signOutDefault.png", size=(113, 113)
    )
    signout_selected = load_image(
        "app/assets/images/home/signOutSelect.png", size=(113, 113)
    )
    signout_state_manager.register_button_images(
        "signOut", {"default": signout_default, "selected": signout_selected}
    )

    signoutBtn: tk.Button = tk.Button(
        _homeBannedWindow_,
        image=signout_default,
        borderwidth=0,
        background=colors["primary-50"],
        highlightthickness=0,
        activebackground=colors["primary-50"],
        cursor="hand2",
    )
    signoutBtn.image = signout_default
    signoutBtn.place(x=1130, y=510)

    # keep references to PhotoImage objects on the window to avoid garbage collection
    _homeBannedWindow_._images = (
        homeBannedImage,
        backgroundBanned,
        logoImage,
        signout_default,
        signout_selected,
    )

    contactAdminButton.bind(
        "<Enter>", lambda event: button_on_enter(event, contactAdminButton)
    )
    contactAdminButton.bind(
        "<Leave>", lambda event: button_on_leave(event, contactAdminButton)
    )

    # Bind hover behavior for signOut button using state manager
    signoutBtn.bind(
        "<Enter>",
        lambda event: signout_state_manager.on_button_enter(signoutBtn, "signOut"),
    )
    signoutBtn.bind(
        "<Leave>",
        lambda event: signout_state_manager.on_button_leave(signoutBtn, "signOut"),
    )

    contactAdminButton.bind(
        "<Button-1>", lambda event: open_contact_admin(_homeBannedWindow_, event)
    )

    signoutBtn.bind(
        "<Button-1>", lambda event: (session.logout(), _homeBannedWindow_.destroy())
    )

    _homeBannedWindow_.mainloop()
