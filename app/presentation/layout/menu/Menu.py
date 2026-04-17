import tkinter as tk
from typing import Callable, Optional

from app.core.state.session import session
from app.presentation.views.dashboard.main import dashboardWindow
from app.presentation.views.explore.main import exploreWindow
from app.presentation.views.manage.main import manageWindow
from app.presentation.views.notifications.main import notificationsWindow
from app.presentation.views.profile.main import profileWindow
from app.presentation.views.settings.main import settingsWindow
from app.presentation.widgets.menu_button import create_menu_button

from .helpers.menu_button_state import MenuButtonStateManager
from .helpers.menu_config import MENU_IMAGES_PATHS, MENU_LAYOUT, MENU_OPTIONS
from .helpers.menu_resources import load_menu_images


class Menu:
    """
    Creates and manages the navigation menu for the application,
    supporting both regular and admin users.
    """

    def __init__(
        self,
        homeCanvas: Optional[tk.Canvas] = None,
        homeWindow: Optional[tk.Tk] = None,
    ) -> None:
        self.homeCanvas: tk.Canvas = homeCanvas
        self.homeWindow: tk.Tk = homeWindow

        self.gap = MENU_LAYOUT["gap"]
        self.posAdminMenuX = MENU_LAYOUT["admin_start_x"]
        self.posRegularMenuX = MENU_LAYOUT["regular_start_x"]
        self.posMenuY = MENU_LAYOUT["menu_y"]

        self.hover_helper = MenuButtonStateManager()

        self.menu_images = load_menu_images(MENU_IMAGES_PATHS)
        # Batch-register images with the state manager
        self.hover_helper.register_images(self.menu_images)

        self.buttons_by_name: dict[str, tk.Button] = self._create_menu_buttons()

        # Actions accept an optional tkinter event parameter (use a permissive callable type)
        self.actions: dict[str, Callable[..., None]] = {
            "explore": self._wrap_action(exploreWindow),
            "profile": self._wrap_action(profileWindow),
            "notifications": self._wrap_action(notificationsWindow),
            "settings": self._wrap_action(settingsWindow),
            "manage": self._wrap_action(manageWindow),
            "dashboard": self._wrap_action(dashboardWindow),
            "signOut": self._sign_out_handler,
        }

    def _create_menu_buttons(self) -> dict[str, tk.Button]:
        """
        Create Tkinter buttons for each menu option using the loaded images.

        Returns:
            dict[str, tk.Button]: A dictionary mapping button names to their corresponding Tkinter Button widgets.
        """

        buttons = {}
        for option in MENU_OPTIONS:
            name: str = option["name"]
            default_img = self.menu_images[name]["default"]
            btn = create_menu_button(self.homeCanvas, default_img)
            # Keep an explicit Python reference on the widget to prevent GC of ImageTk.PhotoImage
            btn.image = default_img
            buttons[name] = btn
        return buttons

    def _wrap_action(self, fn: Callable[[], None]) -> Callable[..., None]:
        """
        Wrap a menu action function to ensure it can be called with an optional event parameter from button bindings.

        Args:
            fn: The menu action function to wrap (e.g., opening a new window).
        Returns:
            Callable: A wrapped function that accepts an optional event parameter and calls the original function.
        """

        return fn

    def _on_enter(self, e: Optional[tk.Event] = None) -> None:
        """
        Generic enter handler: read button attributes from the event widget and delegate to hover helper.

        Args:
            e: Optional event parameter for binding.
        """

        btn_widget = getattr(e, "widget", None)
        if not btn_widget:
            return
        btn_name = getattr(btn_widget, "_menu_name", None)
        self.hover_helper.on_button_enter(btn_widget, btn_name)

    def _on_leave(self, e: Optional[tk.Event] = None) -> None:
        """
        Generic leave handler: read button attributes from the event widget and delegate to hover helper.

        Args:
            e: Optional event parameter for binding.
        """
        btn_widget = getattr(e, "widget", None)
        if not btn_widget:
            return
        btn_name = getattr(btn_widget, "_menu_name", None)
        self.hover_helper.on_button_leave(btn_widget, btn_name)

    def _on_click(self, e: Optional[tk.Event] = None) -> None:
        """
        Generic click handler: read button attributes from the event widget and delegate to click processor.

        Args:
            e: Optional event parameter for binding.
        """
        btn_widget = getattr(e, "widget", None)
        if not btn_widget:
            return
        btn_name = getattr(btn_widget, "_menu_name", None)
        self.handle_menu_click(btn_name, btn_widget, e)

    def render(self) -> None:
        """Render the menu buttons on the canvas based on the user's role (admin or regular)."""
        if session.is_admin:
            self.render_menu("admin", self.posAdminMenuX)
        elif session.is_authenticated:
            self.render_menu("regular", self.posRegularMenuX)

    def handle_menu_click(
        self,
        btn_name: str,
        btn_widget: tk.Button,
        e: Optional[tk.Event] = None,
    ) -> None:
        """
        Handle the click event for a menu button:
        - Update the visual state of the clicked button to "selected".
        - Reset the previously active button to "default" state.
        - Execute the associated action for the button.
        Args:
            btn_name (str): The unique name of the clicked button.
            btn_widget (tk.Button): The button widget that was clicked.
            e: Optional[tk.Event] = None, the event object from the click binding.
        """
        # Reset previously active button (if any) to default state
        prev = self.hover_helper.active_button
        if prev and prev != btn_name:
            prev_btn = self.buttons_by_name.get(prev)
            if prev_btn:
                self.hover_helper.reset_button_to_default(prev_btn, prev)

        # Set the clicked button to selected state and update active button reference
        self.hover_helper.set_active_button(btn_widget, btn_name)

        # Update the active button reference in the state manager
        try:
            if self.homeWindow:
                self.homeWindow.update_idletasks()
        except Exception:
            pass

        # Execute the button's action. Actions are stored in `self.actions`.
        action = self.actions.get(btn_name)
        if not action:
            return
        # Prefer calling without event (most actions don't expect it).
        try:
            action()
        except TypeError:
            try:
                action(e)
            except Exception:
                pass

    def render_menu(self, role: str, start_x: int) -> None:
        """
        Render menu buttons for the specified user role at the given starting X position.

        Args:
            role (str): The user role ("admin" or "regular") to determine which buttons to render.
            start_x (int): The starting X coordinate for placing the first button.
        """
        position = 0
        for option in MENU_OPTIONS:
            if role not in option["roles"]:
                continue

            name: str = option["name"]
            btn = self.buttons_by_name[name]
            btn.place(
                x=start_x + (position * (btn.winfo_reqwidth() + self.gap)),
                y=self.posMenuY,
            )

            handler = self.actions.get(name)
            if handler:
                # Store metadata on the widget so generic handlers can access it.
                setattr(btn, "_menu_name", name)
                setattr(btn, "_menu_action", handler)
                btn.bind("<Button-1>", self._on_click)

            btn.bind("<Enter>", self._on_enter)
            btn.bind("<Leave>", self._on_leave)

            position += 1

    def _sign_out_handler(self, e: Optional[tk.Event] = None) -> None:
        """
        Handle the sign-out action by logging out the user and closing the home window.

        Args:
            e: Optional event parameter for binding.
        """

        try:
            session.logout()
        finally:
            if self.homeWindow:
                try:
                    self.homeWindow.destroy()
                except Exception:
                    pass
