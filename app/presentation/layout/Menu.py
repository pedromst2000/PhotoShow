import tkinter as tk

from PIL import Image, ImageTk

from app.core.state.session import session
from app.presentation.views.dashboard.dashboard import dashboardWindow
from app.presentation.views.explore.explore import exploreWindow
from app.presentation.views.manage.manage import manageWindow
from app.presentation.views.notifications.notifications import notificationsWindow
from app.presentation.views.profile.profile import profileWindow
from app.presentation.views.settings.settings import settingsWindow


class menu:
    """
    The menu class creates and manages the navigation menu for the application, supporting both regular and admin users.
    """

    def __init__(
        self,
        homeCanvas: tk.Canvas = None,
        homeWindow: tk.Tk = None,
    ) -> None:
        """
        Initialize the menu with images, button widgets, and layout configuration.

        Args:
            homeCanvas (tk.Canvas): The Canvas widget where the menu will be displayed.
            homeWindow (tk.Tk): The main application window.

        """
        self.homeCanvas: tk.Canvas = homeCanvas
        self.homeWindow: tk.Tk = homeWindow
        self.gap: int = 50
        self.posAdminMenuX: int = 130
        self.posRegularMenuX: int = 300
        self.posMenuY: int = 310
        self.isAdminOpt: bool = False

        self.exploreImg: ImageTk.PhotoImage = ImageTk.PhotoImage(
            Image.open("app/assets/images/home/menu/explore.png")
        )
        self.profileImg: ImageTk.PhotoImage = ImageTk.PhotoImage(
            Image.open("app/assets/images/home/menu/profile.png")
        )
        self.notificationsImg: ImageTk.PhotoImage = ImageTk.PhotoImage(
            Image.open("app/assets/images/home/menu/notifications.png")
        )
        self.settingsImg: ImageTk.PhotoImage = ImageTk.PhotoImage(
            Image.open("app/assets/images/home/menu/settings.png")
        )
        self.manageImg: ImageTk.PhotoImage = ImageTk.PhotoImage(
            Image.open("app/assets/images/home/menu/manage.png")
        )
        self.dashboardImg: ImageTk.PhotoImage = ImageTk.PhotoImage(
            Image.open("app/assets/images/home/menu/dashboard.png")
        )
        self.signOutImg: ImageTk.PhotoImage = ImageTk.PhotoImage(
            Image.open("app/assets/images/home/menu/signOut.png")
        )

        def _btn(img: ImageTk.PhotoImage) -> tk.Button:
            """
            Create a styled Tkinter button for the menu.

            Args:
                img (ImageTk.PhotoImage): The image to display on the button.

            Returns:
                tk.Button: A Tkinter Button widget configured with the specified image and styling.
            """
            return tk.Button(
                self.homeCanvas,
                image=img,
                width=113,
                height=120,
                cursor="hand2",
                borderwidth=0,
                highlightthickness=0,
            )

        exploreOptButton: tk.Button = _btn(self.exploreImg)
        profileOptButton: tk.Button = _btn(self.profileImg)
        notificationsOptButton: tk.Button = _btn(self.notificationsImg)
        settingsOptButton: tk.Button = _btn(self.settingsImg)
        manageOptButton: tk.Button = _btn(self.manageImg)
        dashboardOptButton: tk.Button = _btn(self.dashboardImg)
        signOutOptButton: tk.Button = _btn(self.signOutImg)

        self.menuOpts: dict[str, list[tk.Button]] = {
            "regular": [
                exploreOptButton,
                profileOptButton,
                notificationsOptButton,
                dashboardOptButton,
                signOutOptButton,
            ],
            "admin": [
                exploreOptButton,
                profileOptButton,
                notificationsOptButton,
                settingsOptButton,
                manageOptButton,
                dashboardOptButton,
                signOutOptButton,
            ],
        }

    def regularMenu(self) -> None:
        """
        Display the regular user menu and bind each button to its corresponding action.

        """
        for i, opt in enumerate(self.menuOpts["regular"]):
            opt.place(
                x=self.posRegularMenuX + (i * (opt.winfo_reqwidth() + self.gap)),
                y=self.posMenuY,
            )
            if i == 0:
                opt.bind("<Button-1>", lambda e: exploreWindow())
            elif i == 1:
                opt.bind("<Button-1>", lambda e: profileWindow())
            elif i == 2:
                opt.bind("<Button-1>", lambda e: notificationsWindow())
            elif i == 3:
                opt.bind("<Button-1>", lambda e: dashboardWindow())
            elif i == 4:
                opt.bind(
                    "<Button-1>",
                    lambda e: (session.logout(), self.homeWindow.destroy()),
                )

    def adminMenu(self) -> None:
        """
        Display the admin user menu and bind each button to its corresponding action.

        """
        for i, opt in enumerate(self.menuOpts["admin"]):
            opt.place(
                x=self.posAdminMenuX + (i * (opt.winfo_reqwidth() + self.gap)),
                y=self.posMenuY,
            )
            if i == 0:
                opt.bind("<Button-1>", lambda e: exploreWindow())
            elif i == 1:
                opt.bind("<Button-1>", lambda e: profileWindow())
            elif i == 2:
                opt.bind("<Button-1>", lambda e: notificationsWindow())
            elif i == 3:
                opt.bind("<Button-1>", lambda e: settingsWindow())
            elif i == 4:
                opt.bind("<Button-1>", lambda e: manageWindow())
            elif i == 5:
                opt.bind("<Button-1>", lambda e: dashboardWindow())
            elif i == 6:
                opt.bind(
                    "<Button-1>",
                    lambda e: (session.logout(), self.homeWindow.destroy()),
                )
