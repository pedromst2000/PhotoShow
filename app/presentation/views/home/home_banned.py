import tkinter as tk
import tkinter.messagebox as messagebox
from typing import Optional

from app.controllers.profile_controller import ProfileController
from app.core.state.session import session
from app.presentation.styles.colors import colors
from app.presentation.styles.fonts import quickSandBold, quickSandRegular
from app.presentation.widgets.helpers.button import on_enter as button_on_enter
from app.presentation.widgets.helpers.button import on_leave as button_on_leave
from app.presentation.widgets.helpers.window import load_image
from app.presentation.widgets.window import create_main_window, create_toplevel

# fallback image
signoutBtnImage: str = ""


def homeBannedWindow():
    """
    Display the home window for a banned user.
    """

    global signoutBtnImage

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

    # sign out button
    signoutBtnImage = load_image(
        "app/assets/images/home/SignOutOptionBlocked.png", size=(82, 87)
    )

    signoutBtn: tk.Button = tk.Button(
        _homeBannedWindow_,
        image=signoutBtnImage,
        borderwidth=0,
        background=colors["primary-50"],
        highlightthickness=0,
        activebackground=colors["primary-50"],
        cursor="hand2",
    )
    signoutBtn.place(x=1130, y=510)

    # keep references to PhotoImage objects on the window to avoid garbage collection
    _homeBannedWindow_._images = (
        homeBannedImage,
        backgroundBanned,
        logoImage,
        signoutBtnImage,
    )

    contactAdminButton.bind(
        "<Enter>", lambda event: button_on_enter(event, contactAdminButton)
    )
    contactAdminButton.bind(
        "<Leave>", lambda event: button_on_leave(event, contactAdminButton)
    )

    def _contact_admin_(event: tk.Event):
        dialogWidth, dialogHeight = 420, 340
        dialog: tk.Toplevel = create_toplevel(
            title="Contact Admin",
            width=dialogWidth,
            height=dialogHeight,
            parent=_homeBannedWindow_,
            bg_color=colors["primary-50"],
        )

        tk.Label(
            dialog,
            text="Contact Admin",
            font=quickSandBold(18),
            bg=colors["primary-50"],
            fg=colors["secondary-500"],
        ).place(x=120, y=15)

        tk.Label(
            dialog,
            text="Title",
            font=quickSandBold(12),
            bg=colors["primary-50"],
            fg=colors["secondary-500"],
        ).place(x=30, y=65)
        titleEntry: tk.Entry = tk.Entry(
            dialog,
            width=40,
            borderwidth=0,
            font=quickSandBold(11),
            bg=colors["secondary-300"],
            fg=colors["secondary-500"],
            highlightthickness=0,
            cursor="xterm",
        )
        titleEntry.place(x=30, y=95)

        tk.Label(
            dialog,
            text="Message",
            font=quickSandBold(12),
            bg=colors["primary-50"],
            fg=colors["secondary-500"],
        ).place(x=30, y=130)
        messageText: tk.Text = tk.Text(
            dialog,
            width=40,
            height=6,
            font=quickSandRegular(11),
            bg=colors["secondary-300"],
            fg=colors["secondary-500"],
            highlightthickness=0,
            borderwidth=0,
            wrap="word",
        )
        messageText.place(x=30, y=158)

        def _submit_(e: Optional[tk.Event] = None):
            success, msg = ProfileController.contact_admin(
                titleEntry.get(),
                messageText.get("1.0", "end-1c"),
            )
            if success:
                messagebox.showinfo("Sent", msg, parent=dialog)
                dialog.destroy()
            else:
                messagebox.showerror("Error", msg, parent=dialog)

        sendBtn: tk.Button = tk.Button(
            dialog,
            width=18,
            height=2,
            text="Send Message",
            borderwidth=0,
            font=quickSandBold(12),
            background=colors["accent-300"],
            highlightthickness=0,
            activebackground=colors["accent-100"],
            fg=colors["secondary-500"],
            cursor="hand2",
        )
        sendBtn.place(x=130, y=290)
        sendBtn.bind("<Button-1>", _submit_)
        dialog.bind("<Return>", _submit_)
        dialog.grab_set()

    contactAdminButton.bind("<Button-1>", _contact_admin_)

    signoutBtn.bind(
        "<Button-1>", lambda event: (session.logout(), _homeBannedWindow_.destroy())
    )

    _homeBannedWindow_.mainloop()
