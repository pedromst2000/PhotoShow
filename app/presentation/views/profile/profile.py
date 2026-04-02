import tkinter as tk

from PIL import Image, ImageTk

from app.controllers.profile_controller import ProfileController
from app.core.state.session import session
from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold, quickSandRegular
from app.presentation.views.profile.albuns import albunsProfileWindow
from app.presentation.views.profile.change_avatar import changeAvatarWindow
from app.presentation.views.profile.change_password import changePasswordWindow
from app.presentation.views.profile.contacts import contactsWindow
from app.presentation.views.profile.favorites import favoritesProfileWindow
from app.presentation.widgets.helpers.button import on_enter as button_on_enter
from app.presentation.widgets.helpers.button import on_leave as button_on_leave
from app.presentation.widgets.window import create_toplevel
from app.utils.file_utils import resolve_avatar_path

# # fallback images
backgroundProfile: str = ""
followersImageIcon: str = ""
avatarImage: str = ""


def profileWindow():
    """
    This function is used to display the profile window.
    """

    global backgroundProfile, followersImageIcon, avatarImage

    # prepare data and create the window using the reusable helper
    userID: int = session.user_id
    userPayload: dict = session.user_data

    stats: dict = ProfileController.get_profile_stats(userID)
    follower_count: int = stats["follower_count"]
    photo_count: int = stats["photo_count"]

    profileWindowWidth: int = 1000  # width of the window
    profileWindowHeight: int = 450  # height of the window

    _profileWindow_: tk.Toplevel = create_toplevel(
        title="👤 Profile 👤",
        width=profileWindowWidth,
        height=profileWindowHeight,
        icon_path="app/assets/PhotoShowIcon.ico",
        bg_color=colors["primary-50"],
    )

    backgroundProfile = Image.open("app/assets/images/profile/backgroundProfile.png")
    backgroundProfile = backgroundProfile.resize((profileWindowWidth, 220))

    # Resolve avatar path robustly (stored values may be relative to project root)
    avatar_found = resolve_avatar_path(userPayload.get("avatar"))

    try:
        avatarImage = Image.open(avatar_found)
    except Exception:
        # fallback placeholder
        avatarImage = Image.new("RGB", (130, 130), color="#cccccc")

    avatarImage = avatarImage.resize((130, 130))

    followersImageIcon = Image.open("app/assets/images/UI_Icons/followersIcon.png")
    followersImageIcon = followersImageIcon.resize((20, 20))

    canvasBackgroundProfile: tk.Canvas = tk.Canvas(
        _profileWindow_,
        width=profileWindowWidth,
        height=220,
        highlightthickness=0,
        borderwidth=0,
    )

    canvasBackgroundProfile.place(x=0, y=0)

    canvasBackgroundProfile.image = ImageTk.PhotoImage(backgroundProfile)

    canvasBackgroundProfile.create_image(
        0, 0, image=canvasBackgroundProfile.image, anchor=tk.NW
    )

    avatarCanvas: tk.Canvas = tk.Canvas(
        _profileWindow_,
        width=130,
        height=130,
        highlightthickness=0,
        borderwidth=0,
    )
    avatarCanvas.place(x=40, y=40)

    avatarCanvas.image = ImageTk.PhotoImage(avatarImage)
    avatarCanvas.create_image(0, 0, image=avatarCanvas.image, anchor=tk.NW)

    canvasBackgroundProfile.create_text(
        200,
        50,
        text=f"{userPayload['username']}",
        font=quickSandBold(20),
        anchor=tk.NW,
        fill=colors["primary-50"],
    )

    roleLabel: tk.Label = tk.Label(
        _profileWindow_,
        text=f"{userPayload['role']}",
        font=(
            quickSandBold(12)
            if userPayload["role"] == "admin"
            else quickSandRegular(12)
        ),
        bg=(
            colors["primary-50"]
            if userPayload["role"] == "admin"
            else colors["secondary-400"]
        ),
        fg=(
            colors["secondary-500"]
            if userPayload["role"] == "admin"
            else colors["primary-50"]
        ),
    )

    roleLabel.place(x=200, y=100)

    canvasBackgroundProfile.create_text(
        850,
        175,
        text=f"{follower_count} followers",
        font=quickSandRegular(12),
        anchor=tk.NW,
        fill=colors["primary-50"],
    )

    followersImageIcon = ImageTk.PhotoImage(followersImageIcon)

    canvasBackgroundProfile.create_image(
        820, 177, image=followersImageIcon, anchor=tk.NW
    )

    # keep references to PhotoImage objects on the window to avoid GC
    _profileWindow_._images = (
        canvasBackgroundProfile.image,
        avatarCanvas.image,
        followersImageIcon,
    )

    canvasBackgroundProfile.create_text(
        710,
        175,
        text=f"{photo_count} photos",
        font=quickSandBold(12),
        anchor=tk.NW,
        fill=colors["primary-50"],
    )

    # ------------------------- Buttons ----------------------------------------------
    albunsBtn: tk.Button = tk.Button(
        _profileWindow_,
        width=18,
        height=2,
        text="Albuns",
        borderwidth=10,
        font=quickSandBold(13),
        background=colors["accent-300"],
        bd=0,
        highlightthickness=0,
        activebackground=colors["accent-100"],
        fg=colors["secondary-500"],
        cursor="hand2",
    )

    favoritesBtn: tk.Button = tk.Button(
        _profileWindow_,
        width=18,
        height=2,
        text="Favorites",
        borderwidth=10,
        font=quickSandBold(13),
        background=colors["accent-300"],
        bd=0,
        highlightthickness=0,
        activebackground=colors["accent-100"],
        fg=colors["secondary-500"],
        cursor="hand2",
    )

    changePasswordBtn: tk.Button = tk.Button(
        _profileWindow_,
        width=18,
        height=2,
        text="Change Password",
        borderwidth=10,
        font=quickSandBold(13),
        background=colors["accent-300"],
        bd=0,
        highlightthickness=0,
        activebackground=colors["accent-100"],
        fg=colors["secondary-500"],
        cursor="hand2",
    )

    changeAvatarBtn: tk.Button = tk.Button(
        _profileWindow_,
        width=18,
        height=2,
        text="Change Avatar",
        borderwidth=10,
        font=quickSandBold(13),
        background=colors["accent-300"],
        bd=0,
        highlightthickness=0,
        activebackground=colors["accent-100"],
        fg=colors["secondary-500"],
        cursor="hand2",
    )

    contactsBtn: tk.Button = tk.Button(
        _profileWindow_,
        width=18,
        height=2,
        text="Contacts",
        borderwidth=10,
        font=quickSandBold(13),
        background=colors["accent-300"],
        bd=0,
        highlightthickness=0,
        activebackground=colors["accent-100"],
        fg=colors["secondary-500"],
        cursor="hand2",
    )

    # TODO = If is a visitor, show only the albuns and favorites buttons

    (
        albunsBtn.place(x=40, y=270)
        if userPayload["role"] == "admin" or userPayload["role"] == "regular"
        else None
    )
    (
        favoritesBtn.place(x=240, y=270)
        if userPayload["role"] == "admin" or userPayload["role"] == "regular"
        else None
    )
    changePasswordBtn.place(x=440, y=270)
    changeAvatarBtn.place(x=640, y=270)
    contactsBtn.place(x=40, y=350) if userPayload["role"] == "admin" else None

    # ------------------------- Events ----------------------------------------------

    albunsBtn.bind("<Enter>", lambda event: button_on_enter(event, albunsBtn))
    albunsBtn.bind("<Leave>", lambda event: button_on_leave(event, albunsBtn))
    favoritesBtn.bind("<Enter>", lambda event: button_on_enter(event, favoritesBtn))
    favoritesBtn.bind("<Leave>", lambda event: button_on_leave(event, favoritesBtn))
    changePasswordBtn.bind(
        "<Enter>", lambda event: button_on_enter(event, changePasswordBtn)
    )
    changePasswordBtn.bind(
        "<Leave>", lambda event: button_on_leave(event, changePasswordBtn)
    )
    changeAvatarBtn.bind(
        "<Enter>", lambda event: button_on_enter(event, changeAvatarBtn)
    )
    changeAvatarBtn.bind(
        "<Leave>", lambda event: button_on_leave(event, changeAvatarBtn)
    )
    contactsBtn.bind("<Enter>", lambda event: button_on_enter(event, contactsBtn))
    contactsBtn.bind("<Leave>", lambda event: button_on_leave(event, contactsBtn))
    albunsBtn.bind("<Button-1>", lambda event: albunsProfileWindow())
    favoritesBtn.bind("<Button-1>", lambda event: favoritesProfileWindow())
    changePasswordBtn.bind("<Button-1>", lambda event: changePasswordWindow())
    contactsBtn.bind("<Button-1>", lambda event: contactsWindow())
    changeAvatarBtn.bind("<Button-1>", lambda event: changeAvatarWindow())

    _profileWindow_.grab_set()
