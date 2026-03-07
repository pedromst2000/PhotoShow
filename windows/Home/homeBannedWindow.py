from tkinter import Canvas, Button, NW, CENTER, Tk
from PIL import ImageTk, Image
from styles.colors import colors
from styles.fonts import quickSandBold, quickSandRegular
from utils.widgets.button import (
    on_enter as button_on_enter,
    on_leave as button_on_leave,
)

# fallback image
signoutBtnImage = ""


def homeBannedWindow(email: str):
    """
    Display the home window for a banned user.

    :param email: The email address of the banned user.
    :return: None
    """
    """
    This function is used to display the home window for banned users.

    :param email: str
    """
    global signoutBtnImage

    # open the window
    _homeBannedWindow_ = Tk()
    # centering the window
    homeBannedWindowWidth = 1350  # width of the window
    homeBannedWindowHeight = 700  # height of the window

    screenWidth = _homeBannedWindow_.winfo_screenwidth()  # width of the screen

    screenHeight = _homeBannedWindow_.winfo_screenheight()  # height of the screen

    x = (screenWidth / 2) - (homeBannedWindowWidth / 2)  # calculate x position

    y = (screenHeight / 2) - (homeBannedWindowHeight / 2)  # calculate y position

    # setting the window size and position
    # %d = integer
    # %dx%d = width x height
    # %d+%d = x position + y position
    _homeBannedWindow_.geometry(
        "%dx%d+%d+%d" % (homeBannedWindowWidth, homeBannedWindowHeight, x, y)
    )
    _homeBannedWindow_.title("PhotoShow - Banned Notice")
    _homeBannedWindow_.iconbitmap("assets/PhotoShowIcon.ico")
    _homeBannedWindow_.resizable(0, 0)
    _homeBannedWindow_.config(bg=colors["primary-50"])

    homeBannedCanvas = Canvas(_homeBannedWindow_, width=1350, height=700)
    homeBannedCanvas.place(x=0, y=0)

    homeBannedImage = Image.open("assets/images/home/mainBlockedBackground.png")
    homeBannedImage = homeBannedImage.resize((1350, 700))

    homeBannedImage = ImageTk.PhotoImage(homeBannedImage)

    homeBannedCanvas.create_image(0, 0, image=homeBannedImage, anchor=NW)

    backgroundBanned = Image.open("assets/images/home/blockedBackground.png")
    backgroundBanned = backgroundBanned.resize((1146, 530))

    backgroundBanned = ImageTk.PhotoImage(backgroundBanned)

    homeBannedCanvas.create_image(102, 102, image=backgroundBanned, anchor=NW)

    logoImage = Image.open("assets/images/Logo.png")
    logoImage = logoImage.resize((306, 65))

    logoImage = ImageTk.PhotoImage(logoImage)
    homeBannedCanvas.create_image(522, 70, image=logoImage, anchor=NW)

    # title
    homeBannedCanvas.create_text(
        675,
        200,
        text="ACCOUNT SUPSENSION NOTICE",
        font=quickSandBold(18),
        fill=colors["primary-50"],
        anchor=CENTER,
    )

    # first paragraph
    homeBannedCanvas.create_text(
        675,
        270,
        text="We regret to inform you that your account has been suspended due to a violation of our community guidelines.",
        font=quickSandRegular(14),
        fill=colors["accent-100"],
        anchor=CENTER,
    )

    # second paragraph
    homeBannedCanvas.create_text(
        658,
        320,
        text="After careful review from our admin, it has been determined  that your actions have breached our policies, resulting in the necessity to suspend your account.",
        font=quickSandRegular(14),
        fill=colors["accent-100"],
        anchor=CENTER,
        width=950,
    )

    # third paragraph
    homeBannedCanvas.create_text(
        638,
        385,
        text="Please be aware we are commited to maintaining a safe and respectful environment for all users. Any activities that undermine this commitment, such as explicit content are taken seriously.",
        font=quickSandRegular(14),
        fill=colors["accent-100"],
        anchor=CENTER,
        width=950,
    )

    # fourth paragraph
    homeBannedCanvas.create_text(
        628,
        435,
        text="If you believe this suspension is in error would like to appeal the decision, please contact our admin.",
        font=quickSandRegular(14),
        fill=colors["accent-100"],
        anchor=CENTER,
    )

    # contact Admin button
    contactAdminButton = Button(
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

    # sign out button
    signoutBtnImage = Image.open("assets/images/home/SignOutOptionBlocked.png")
    signoutBtnImage = signoutBtnImage.resize((82, 87))

    signoutBtnImage = ImageTk.PhotoImage(signoutBtnImage)

    signoutBtn = Button(
        _homeBannedWindow_,
        image=signoutBtnImage,
        borderwidth=0,
        background=colors["primary-50"],
        highlightthickness=0,
        activebackground=colors["primary-50"],
        cursor="hand2",
    )
    signoutBtn.place(x=1130, y=510)

    contactAdminButton.bind("<Enter>", lambda e: button_on_enter(e, contactAdminButton))
    contactAdminButton.bind("<Leave>", lambda e: button_on_leave(e, contactAdminButton))

    signoutBtn.bind("<Button-1>", lambda e: _homeBannedWindow_.destroy())

    _homeBannedWindow_.mainloop()
