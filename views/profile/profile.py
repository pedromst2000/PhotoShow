import tkinter as tk

from PIL import Image, ImageTk

from services.photo_service import PhotoService
from services.user_service import UserService
from state.session import session
from styles.colors import colors
from styles.fonts import quickSandBold, quickSandRegular
from views.profile.albuns import albunsProfileWindow
from views.profile.change_avatar import changeAvatarWindow
from views.profile.change_password import changePasswordWindow
from views.profile.contacts import contactsWindow
from views.profile.favorites import favoritesProfileWindow
from widgets.button import on_enter as button_on_enter
from widgets.button import on_leave as button_on_leave

# # fallback images
backgroundProfile: str = ""
followersImageIcon: str = ""
avatarImage: str = ""


def profileWindow():
    """
    This function is used to display the profile window.
    """

    global backgroundProfile, followersImageIcon, avatarImage

    # open the window
    _profileWindow_: tk.Toplevel = tk.Toplevel()

    userID: int = session.user_id
    userPayload: dict = session.user_data

    follower_count: int = UserService.count_followers(userID)
    photo_count: int = PhotoService.count_photos_by_user(userID)

    # centering the window
    profileWindowWidth: int = 1000  # width of the window
    profileWindowHeight: int = 450  # height of the window

    screenWidth: int = _profileWindow_.winfo_screenwidth()  # width of the screen

    screenHeight: int = _profileWindow_.winfo_screenheight()  # height of the screen

    x: float = (screenWidth / 2) - (profileWindowWidth / 2)  # calculate x position

    y: float = (screenHeight / 2) - (profileWindowHeight / 2)  # calculate y position

    # setting the window size and position
    # %d = integer
    # %dx%d = width x height
    # %d+%d = x position + y position
    _profileWindow_.geometry(
        "%dx%d+%d+%d" % (profileWindowWidth, profileWindowHeight, x, y)
    )
    _profileWindow_.title("👤 Profile 👤")
    _profileWindow_.iconbitmap("assets/PhotoShowIcon.ico")
    _profileWindow_.resizable(0, 0)
    _profileWindow_.config(bg=colors["primary-50"])

    backgroundProfile = Image.open("assets/images/profile/backgroundProfile.png")
    backgroundProfile = backgroundProfile.resize((profileWindowWidth, 220))

    avatarImage = Image.open(userPayload["avatar"])
    avatarImage = avatarImage.resize((130, 130))

    followersImageIcon = Image.open("assets/images/UI_Icons/followersIcon.png")
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
