"""
Font Installation Script for PhotoShow

This script handles installing Quicksand fonts to the system fonts directory.
It runs at app startup and checks if fonts are already installed before installing.

Supports: Windows (system-wide or per-user), macOS, Linux
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

from app.utils.log_utils import log_check, log_issue, log_success


def get_fonts_directory():
    """Get the system fonts directory based on OS."""
    system = sys.platform

    if system == "win32":
        return Path(os.environ.get("WINDIR", "C:\\Windows")) / "Fonts"
    elif system == "darwin":  # macOS
        return Path.home() / "Library" / "Fonts"
    elif system == "linux":
        return Path.home() / ".local" / "share" / "fonts"
    else:
        raise OSError(f"Unsupported operating system: {system}")


def get_user_fonts_directory():
    """Get the user-local fonts directory (fallback for non-admin users)."""
    system = sys.platform

    if system == "win32":
        # User fonts directory (no admin needed)
        return (
            Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
            / "Microsoft"
            / "Windows"
            / "Fonts"
        )
    elif system == "darwin":  # macOS
        return Path.home() / "Library" / "Fonts"
    elif system == "linux":
        return Path.home() / ".local" / "share" / "fonts"
    else:
        raise OSError(f"Unsupported operating system: {system}")


def get_app_fonts_directory():
    """Get the app's fonts directory."""
    # Try to locate fonts relative to this script
    script_dir = Path(__file__).parent
    app_fonts = script_dir.parent / "app" / "assets" / "fonts"

    if app_fonts.exists():  # Common case when running from source
        return app_fonts

    # Fallback for PyInstaller bundle
    if getattr(sys, "frozen", False):
        # Running as PyInstaller bundle
        base_path = Path(sys._MEIPASS)
        app_fonts = base_path / "app" / "assets" / "fonts"
        if app_fonts.exists():
            return app_fonts

    raise FileNotFoundError("Could not locate app fonts directory")


def is_font_installed(font_name: str) -> bool:
    """
    Check if a font is already installed on the system or user fonts directory.

    Args:
        font_name: Font name without extension (e.g., "Quicksand-Regular")

    Returns:
        bool: True if font is installed, False otherwise
    """
    system = sys.platform
    system_fonts_dir = get_fonts_directory()
    user_fonts_dir = get_user_fonts_directory()

    # Check system fonts directory
    font_path = system_fonts_dir / f"{font_name}.ttf"
    if font_path.exists():
        return True

    # Check user fonts directory
    font_path = user_fonts_dir / f"{font_name}.ttf"
    if font_path.exists():
        return True

    # Additional check for Windows registry (system-wide)
    if system == "win32":
        try:
            import winreg

            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"Software\Microsoft\Windows NT\CurrentVersion\Fonts",
            ) as key:
                try:
                    value, _ = winreg.QueryValueEx(key, f"{font_name}.ttf")
                    return True
                except FileNotFoundError:
                    pass
        except Exception as e:
            log_issue(f"Could not check Windows registry: {e}")

    return False


def load_fonts_windows(font_paths: list) -> bool:
    """
    Load fonts into the current Windows session without requiring system installation.
    Uses Windows API AddFontResourceEx to load fonts for the current user session.

    Args:
        font_paths: List of absolute paths to TTF files

    Returns:
        bool: True if all fonts loaded successfully
    """
    try:
        import ctypes
        from ctypes import wintypes

        # Load Windows API
        gdi32 = ctypes.windll.gdi32

        # AddFontResourceEx signature
        AddFontResourceEx = gdi32.AddFontResourceExA
        AddFontResourceEx.argtypes = [wintypes.LPCSTR, wintypes.DWORD, wintypes.LPVOID]
        AddFontResourceEx.restype = wintypes.INT

        # FR_PRIVATE = 0x10 (makes font available only to this process)
        # FR_NOT_ENUM = 0x20 (font not enumerable)
        FR_PRIVATE = 0x10
        FR_NOT_ENUM = 0x20
        loaded_count = 0
        for font_path in font_paths:
            try:
                font_path_str = str(font_path).encode("utf-8")
                result = AddFontResourceEx(
                    font_path_str, FR_PRIVATE | FR_NOT_ENUM, None
                )
                if result > 0:
                    log_success(f"Loaded font to session: {font_path.name}")
                    loaded_count += 1
                else:
                    log_issue(f"Failed to load font to session: {font_path.name}")
            except Exception as e:
                log_issue(f"Error loading font {font_path.name} to session: {e}")

        return loaded_count == len(font_paths)

    except Exception as e:
        log_issue(f"Could not load fonts to Windows session: {e}")
        return False


def install_fonts() -> bool:
    """
    Install all Quicksand fonts.

    On Windows:
    - Try system-wide installation (C:\\Windows\\Fonts) first
    - If permission denied, fall back to user-local installation
    - Load fonts to current session via Windows API

    On macOS/Linux:
    - Install to system directory (may require sudo) or user directory

    Returns:
        bool: True if installation successful, False otherwise
    """
    try:
        app_fonts_dir = (
            get_app_fonts_directory()
        )  # Get path to app's bundled fonts (handles PyInstaller case)
        system = sys.platform  # Detect OS platform

        # List of fonts to install
        fonts_to_install = [
            "Quicksand-Regular.ttf",
            "Quicksand-Bold.ttf",
            "Quicksand-Light.ttf",
            "Quicksand-Medium.ttf",
            "Quicksand-SemiBold.ttf",
        ]

        # Check if all fonts are already installed
        all_installed = all(
            is_font_installed(font.replace(".ttf", "")) for font in fonts_to_install
        )

        if all_installed:
            log_success("All Quicksand fonts already installed")
            # On Windows, still load to session if needed
            if system == "win32":
                user_fonts_dir = (
                    get_user_fonts_directory()
                )  # Check user fonts directory for installed fonts
                user_font_paths = [
                    user_fonts_dir / f
                    for f in fonts_to_install
                    if (user_fonts_dir / f).exists()
                ]  # Load from user directory if found there
                if (
                    user_font_paths
                ):  # Only load if found in user directory (not system) to avoid duplicates
                    load_fonts_windows(user_font_paths)
            return True  # No installation needed, but fonts are ready to use

        # Determine target directory and fallback strategy
        system_fonts_dir = get_fonts_directory()
        user_fonts_dir = get_user_fonts_directory()

        fonts_installed = (
            []
        )  # Track successfully installed fonts for summary and session loading
        fonts_failed = []  # Track fonts that failed to install for summary
        use_user_dir = False  # Track if we fell back to user directory

        for font_file in fonts_to_install:  # Iterate over fonts to install
            src_path = (
                app_fonts_dir / font_file
            )  # Source path for font file in app assets

            if (
                not src_path.exists()
            ):  # Sanity check: ensure source font file exists before attempting installation
                log_issue(f"Font file not found: {src_path}")
                fonts_failed.append(font_file)
                continue

            # Try system directory first
            if not use_user_dir:
                try:  # Attempt to install to system fonts directory
                    dst_path = (
                        system_fonts_dir / font_file
                    )  # Destination path in system fonts directory
                    shutil.copy2(
                        src_path, dst_path
                    )  # Copy font file to system directory (may require admin permissions)
                    log_success(f"Installed font to system: {font_file}")
                    fonts_installed.append(
                        font_file
                    )  # Track successful installation for summary and session loading

                    # Windows: Register font in registry
                    if system == "win32":
                        try:
                            import winreg

                            font_name = font_file.replace(".ttf", "")
                            with winreg.OpenKey(
                                winreg.HKEY_LOCAL_MACHINE,  # Add font entry to Windows registry for system-wide installation
                                r"Software\Microsoft\Windows NT\CurrentVersion\Fonts",  # Registry path for installed fonts
                                access=winreg.KEY_WRITE,
                            ) as key:
                                winreg.SetValueEx(
                                    key, f"{font_name}", 0, winreg.REG_SZ, font_file
                                )
                        except PermissionError:
                            pass  # Registry write may fail; fall back to user dir
                        except Exception:
                            pass

                    # Linux: Update font cache
                    if system == "linux":
                        try:
                            subprocess.run(
                                ["fc-cache", "-f"], check=False
                            )  # Refresh font cache on Linux after installation
                        except Exception:
                            pass

                    continue

                except PermissionError:
                    # System install failed due to permissions; switch to user directory
                    log_check(
                        f"System fonts directory requires admin. Falling back to user directory: {user_fonts_dir}"
                    )
                    use_user_dir = True
                    # Continue to retry with user directory
                except Exception as e:
                    log_issue(f"Error installing font to system: {font_file}", exc=e)
                    fonts_failed.append(font_file)
                    continue

            # Install to user directory (after permission error or by default)
            if use_user_dir:
                try:
                    user_fonts_dir.mkdir(
                        parents=True, exist_ok=True
                    )  # Ensure user fonts directory exists
                    dst_path = (
                        user_fonts_dir / font_file
                    )  # Destination path in user fonts directory
                    shutil.copy2(src_path, dst_path)  # Copy font file to user directory
                    log_success(f"Installed font to user directory: {font_file}")
                    fonts_installed.append(
                        font_file
                    )  # Track successful installation for summary and session loading

                    # Linux: Update font cache
                    if system == "linux":
                        try:
                            subprocess.run(
                                ["fc-cache", "-f"], check=False
                            )  # Refresh font cache on Linux after installation
                        except Exception:
                            pass

                except Exception as e:
                    log_issue(
                        f"Error installing font to user directory: {font_file}", exc=e
                    )
                    fonts_failed.append(font_file)

        # On Windows, load fonts to current session if installed to user directory
        if system == "win32" and use_user_dir and fonts_installed:
            font_paths_to_load = [
                user_fonts_dir / f
                for f in fonts_installed
                if (user_fonts_dir / f).exists()
            ]
            if font_paths_to_load:
                load_fonts_windows(font_paths_to_load)

        # Summary
        if fonts_failed:
            log_issue(
                f"Font installation incomplete: {len(fonts_installed)} installed, {len(fonts_failed)} failed"
            )
            return False

        install_location = (
            "user directory (no admin required)"
            if use_user_dir
            else "system fonts directory"
        )
        log_success(
            f"All fonts installed to {install_location} ({len(fonts_installed)} fonts)"
        )
        return True

    except Exception as e:
        log_issue("Font installation error", exc=e)
        return False


def ensure_fonts_installed():
    """
    Main entry point: Check and install fonts if needed.
    Call this at application startup.
    """
    try:
        log_check("Checking Quicksand fonts...")
        success = install_fonts()

        if not success:
            log_issue(
                "Font installation encountered issues (continuing with app startup)"
            )
        else:
            log_success("Custom fonts ready")

        return success

    except Exception as e:
        log_issue("Error checking fonts", exc=e)
        return False


if __name__ == "__main__":
    # Direct script execution for testing
    ensure_fonts_installed()
