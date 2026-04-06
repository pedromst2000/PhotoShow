from typing import Dict

from PIL import ImageTk

from app.presentation.widgets.helpers.window import load_image


def load_menu_images(
    menu_images_paths: Dict[str, Dict[str, str]],
) -> Dict[str, Dict[str, ImageTk.PhotoImage]]:
    """
    Load menu button images for default and selected states.

    Args:
        menu_images_paths (Dict[str, Dict[str, str]]): A dictionary mapping button names to their image file paths for default and selected states.
    Returns:
        Dict[str, Dict[str, tk.PhotoImage]]: A dictionary mapping button names to their default and selected PhotoImage objects.
    """

    images: Dict[str, Dict[str, ImageTk.PhotoImage]] = {}
    for name, paths in menu_images_paths.items():
        default = load_image(paths.get("default"))
        selected = load_image(paths.get("selected"))
        images[name] = {"default": default, "selected": selected}
    return images
