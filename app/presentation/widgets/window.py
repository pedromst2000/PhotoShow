import tkinter as tk
from typing import Optional

# Module-level storage for the current main window (for use as parent when creating Toplevels)
_current_main_window: Optional[tk.Tk] = None


def set_main_window(window: tk.Tk) -> None:
    """
    Store the main window globally so Toplevels can use it as parent.

    Args:
        window: The main Tk window to store.
    """
    global _current_main_window
    _current_main_window = window


def _get_parent_window() -> Optional[tk.Tk]:
    """
    Get the current main window to use as parent for Toplevels.

    Returns:
        Optional[tk.Tk]: The current main window if it exists and is valid, otherwise None.
    """
    global _current_main_window
    if _current_main_window:
        try:
            if _current_main_window.winfo_exists():
                return _current_main_window
        except Exception:
            # Window was destroyed or other error; clear reference
            _current_main_window = None
    # Fallback: try the Tk default root
    try:
        root = tk.Tk._default_root
        if root and root.winfo_exists():
            return root
    except Exception:
        pass
    return None


def create_toplevel(
    title: str,
    width: int,
    height: int,
    icon_path: Optional[str] = None,
    bg_color: Optional[str] = None,
    parent: Optional[tk.Tk] = None,
) -> tk.Toplevel:
    """Create and return a centered Toplevel window with common configuration.

    Args:
        title: Window title.
        width: Window width in pixels.
        height: Window height in pixels.
        icon_path: Optional path to an .ico file.
        bg_color: Optional background color for the window.
        parent: Optional parent Tk window.

    Returns:
        :tk.Toplevel: Configured `tk.Toplevel` instance.
    """
    # If no parent provided, use the stored main window; otherwise create without parent
    effective_parent = parent if parent else _get_parent_window()
    win = tk.Toplevel(effective_parent) if effective_parent else tk.Toplevel()

    # Make window transient to parent (stays on top) and modal
    if effective_parent:
        win.transient(effective_parent)
        win.grab_set()  # Make window modal - user must close it before accessing parent

    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))
    win.geometry("%dx%d+%d+%d" % (width, height, x, y))
    win.title(title)
    if icon_path:
        try:
            win.iconbitmap(icon_path)
        except Exception:
            # icon may not be available on all platforms or path could be wrong
            pass
    win.resizable(False, False)
    if bg_color is not None:
        win.config(bg=bg_color)
    return win


def create_main_window(
    title: str,
    width: int,
    height: int,
    icon_path: Optional[str] = None,
    bg_color: Optional[str] = None,
) -> tk.Tk:
    """Create and return a centered Tk root window with common configuration.

    This parallels `create_toplevel` but returns a `tk.Tk` instance suitable
    for main application windows that need to own the mainloop.

    Args:
        title: Window title.
        width: Window width in pixels.
        height: Window height in pixels.
        icon_path: Optional path to an .ico file.
        bg_color: Optional background color for the window.
    Returns:
        :tk.Tk: Configured `tk.Tk` instance.

    """
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))
    root.geometry("%dx%d+%d+%d" % (width, height, x, y))
    root.title(title)
    if icon_path:
        try:
            root.iconbitmap(icon_path)
        except Exception:
            # icon may not be available on all platforms or path could be wrong
            pass
    root.resizable(False, False)
    if bg_color is not None:
        root.config(bg=bg_color)
    set_main_window(root)  # Store as parent for future Toplevels
    return root
