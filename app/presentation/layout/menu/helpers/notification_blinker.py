"""Notification button blink animation with smooth ease-in image blending.

Uses Pillow to generate intermediate frames between the default and selected
notification button images, producing a smooth ease-in pulse effect.

The blinker mutates ``images_dict["default"]`` while active so that the
existing ``MenuButtonStateManager.on_button_leave`` naturally restores the
current blink frame (not the original static default) — no changes to the
state manager are needed.

Animation cycle (≈ 1.5 s total):
  ┌──────────────────────────────────────────────────┐
  │  Ease-in forward  FRAMES × FRAME_MS ≈  600 ms    │
  │  Hold at peak                    HOLD_MS ≈ 450 ms│
  │  Jump to base + hold             HOLD_MS ≈ 450 ms│
  └──────────────────────────────────────────────────┘
"""

import tkinter as tk
from typing import Dict, List, Optional

from PIL import Image, ImageTk


class NotificationBlinker:
    """Blinks the notifications menu button when unread notifications exist.

    Args:
        btn: The tk.Button widget for the notifications menu item.
        images_dict: Live ``menu_images["notifications"]`` dict with keys
                     ``"default"`` and ``"selected"``.  The blinker writes the
                     current blend frame back to ``images_dict["default"]`` each
                     tick so the MenuButtonStateManager stays consistent.
        default_path: File path to the default (dark) notification image.
        selected_path: File path to the selected (light) notification image.
    """

    FRAMES: int = 8  # blend steps in the forward pass
    FRAME_MS: int = 75  # ms per blend step → 600 ms forward pass
    HOLD_MS: int = 450  # ms to hold at peak / base → full cycle ≈ 1 500 ms

    def __init__(
        self,
        btn: tk.Button,
        images_dict: Dict[str, tk.PhotoImage],
        default_path: str,
        selected_path: str,
    ) -> None:
        self._btn = btn
        self._images_dict = images_dict
        self._original_default: tk.PhotoImage = images_dict["default"]
        self._frames: List[ImageTk.PhotoImage] = self._build_frames(
            default_path, selected_path
        )
        self._is_blinking: bool = False
        self._after_id: Optional[str] = None
        self._frame_idx: int = 0
        self._phase: str = "forward"  # "forward" | "hold_peak" | "hold_base"

    # ── Public API ────────────────────────────────────────────────────────────

    @property
    def is_blinking(self) -> bool:
        """True while the animation loop is running.

        Args:
            bool: True if the blinker is currently active and animating; False if not.
        """
        return self._is_blinking

    def start(self) -> None:
        """Start the blink animation; no-op if already running."""
        if self._is_blinking:
            return
        self._is_blinking = True
        self._frame_idx = 0
        self._phase = "forward"
        self._tick()

    def stop(self) -> None:
        """Stop animation and restore the original static default image."""
        self._is_blinking = False
        if self._after_id is not None:
            try:
                self._btn.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None
        self._images_dict["default"] = self._original_default
        try:
            if self._btn.winfo_exists():
                self._btn.config(image=self._original_default)
                self._btn.image = self._original_default  # GC guard
        except Exception:
            pass

    # ── Internal ──────────────────────────────────────────────────────────────

    @classmethod
    def _build_frames(
        cls, default_path: str, selected_path: str
    ) -> List[ImageTk.PhotoImage]:
        """Return FRAMES+1 ease-in blended frames (default → selected).

        Args:
            default_path (str): File path to the default (dark) notification image.
            selected_path (str): File path to the selected (light) notification image.

        Returns:
            List[ImageTk.PhotoImage]: A list of PhotoImage frames for the blink animation.
        """
        img_a = Image.open(default_path).convert("RGBA")
        img_b = Image.open(selected_path).convert("RGBA")
        if img_a.size != img_b.size:
            img_b = img_b.resize(img_a.size, Image.LANCZOS)
        frames: List[ImageTk.PhotoImage] = []
        n = cls.FRAMES
        for i in range(n + 1):
            t = i / n
            alpha = t * t  # ease-in quadratic
            blended = Image.blend(img_a, img_b, alpha)
            frames.append(ImageTk.PhotoImage(blended))
        return frames

    def _tick(self) -> None:
        """Advance one animation frame."""
        if not self._is_blinking:
            return
        try:
            if not self._btn.winfo_exists():
                self._is_blinking = False
                return
        except Exception:
            self._is_blinking = False
            return

        if self._phase == "forward":
            frame = self._frames[self._frame_idx]
            # Update the menu images dict so hover-leave restores this frame
            self._images_dict["default"] = frame
            self._btn.config(image=frame)
            self._btn.image = frame  # GC guard
            self._frame_idx += 1
            if self._frame_idx > self.FRAMES:
                self._phase = "hold_peak"
                self._after_id = self._btn.after(self.HOLD_MS, self._tick)
            else:
                self._after_id = self._btn.after(self.FRAME_MS, self._tick)

        elif self._phase == "hold_peak":
            # Snap back to the base frame instantly
            base = self._frames[0]
            self._images_dict["default"] = base
            self._btn.config(image=base)
            self._btn.image = base
            self._frame_idx = 0
            self._phase = "hold_base"
            self._after_id = self._btn.after(self.HOLD_MS, self._tick)

        elif self._phase == "hold_base":
            self._phase = "forward"
            self._tick()
