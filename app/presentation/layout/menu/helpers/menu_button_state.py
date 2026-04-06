import tkinter as tk
from typing import Dict


class MenuButtonStateManager:
    """
    Manages visual state (default/selected/active) for menu buttons.

    This class replaces the former `MenuHoverHelper` name to better express
    its responsibility: managing the visual state of menu buttons.
    """

    def __init__(self) -> None:
        self.button_images: Dict[str, Dict[str, tk.PhotoImage]] = {}
        self.button_states: Dict[str, str] = {}
        self.active_button: str | None = None

    def register_button_images(
        self, button_name: str, images: Dict[str, tk.PhotoImage]
    ) -> None:
        """
        Register the default and selected images for a menu button.
        Args:
            button_name (str): The unique name of the button (e.g., "explore").
            images (Dict[str, tk.PhotoImage]): A dictionary with keys "default" and "selected"
                containing the corresponding PhotoImage objects.
        """

        self.button_images[button_name] = images
        self.button_states[button_name] = "default"

    def register_images(self, images: Dict[str, Dict[str, tk.PhotoImage]]) -> None:
        """
        Batch register images for multiple buttons.

        Args:
            images (Dict[str, Dict[str, tk.PhotoImage]]): A dictionary mapping button names to their default and selected PhotoImage objects.
        """

        for name, imgs in images.items():
            self.register_button_images(name, imgs)

    def on_button_enter(self, button: tk.Button, button_name: str) -> None:
        """
        Handle the event when the mouse enters a button.

        Args:
            button (tk.Button): The button widget.
            button_name (str): The unique name of the button.
        """

        if button_name in self.button_images:
            selected_image = self.button_images[button_name].get("selected")
            if selected_image:
                button.config(image=selected_image)
                # keep a reference to prevent ImageTk from being GC'd
                button.image = selected_image
                self.button_states[button_name] = "selected"

    def on_button_leave(self, button: tk.Button, button_name: str) -> None:
        """
        Handle the event when the mouse leaves a button.

        Args:
            button (tk.Button): The button widget.
            button_name (str): The unique name of the button.
        """

        if button_name != self.active_button:
            if button_name in self.button_images:
                default_image = self.button_images[button_name].get("default")
                if default_image:
                    button.config(image=default_image)
                    button.image = default_image
                    self.button_states[button_name] = "default"

    def set_active_button(self, button: tk.Button, button_name: str) -> None:
        """
        Set the specified button as active, changing its image to the selected state.

        Args:
            button (tk.Button): The button widget to set as active.
            button_name (str): The unique name of the button to set as active.
        """

        # mark the activated button so it keeps selected state on leave
        self.active_button = button_name
        if button_name in self.button_images:
            selected_image = self.button_images[button_name].get("selected")
            if selected_image:
                button.config(image=selected_image)
                button.image = selected_image
                self.button_states[button_name] = "selected"

    def reset_button_to_default(self, button: tk.Button, button_name: str) -> None:
        """
        Reset a single button to its default state and image.
        Responsibility: Manage visual state transition for button reset (SRP).

        Args:
            button (tk.Button): The button widget to reset.
            button_name (str): The unique name of the button.
        """
        if button_name in self.button_images:
            default_image = self.button_images[button_name].get("default")
            if default_image:
                button.config(image=default_image)
                button.image = default_image
                self.button_states[button_name] = "default"

    # Optional: A method to reset all buttons to default state (not currently used, but can be added if needed)
    # def reset(self) -> None:
    #     """
    #     Reset all buttons to their default state and clear the active button.
    #     """

    #     self.button_states = {name: "default" for name in self.button_images}
    #     self.active_button = None
