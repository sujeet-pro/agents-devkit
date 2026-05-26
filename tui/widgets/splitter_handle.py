"""SplitterHandle — draggable bar between the queue and the detail tabs.

The handle is 1 row tall and spans the full width. It captures the mouse on
``MouseDown``, emits :class:`SplitterHandle.Dragged` on every ``MouseMove``
while the button is held, and emits :class:`SplitterHandle.Released` on
``MouseUp``.

The parent app translates the vertical deltas into a new ``split_percent``
and re-applies layout; persistence to the prefs sidecar happens only on
``Released`` to avoid hammering the disk during a drag.
"""
from __future__ import annotations

from textual import events
from textual.message import Message
from textual.widgets import Static


class SplitterHandle(Static):
    """A thin draggable bar that re-sizes the split between two siblings."""

    DEFAULT_CSS = """
    SplitterHandle {
        background: $primary-background;
        color: $accent;
        content-align: center middle;
    }
    SplitterHandle:hover {
        background: $accent;
        color: $text;
    }
    SplitterHandle.-dragging {
        background: $accent;
        color: $text;
    }
    """

    class Dragged(Message):
        """Emitted while the user drags the handle. ``delta_x`` / ``delta_y``
        are screen-coordinate deltas relative to the previous event."""

        def __init__(self, delta_x: int, delta_y: int) -> None:
            super().__init__()
            self.delta_x = delta_x
            self.delta_y = delta_y

    class Released(Message):
        """Emitted once the user releases the mouse button.

        Signals that the parent should persist the current split."""

        def __init__(self) -> None:
            super().__init__()

    def __init__(self, *, ascii_only: bool = False) -> None:
        glyph = "-- drag --" if ascii_only else "··· drag ···"
        super().__init__(glyph, markup=False)
        self._ascii_only = ascii_only
        self._dragging = False
        self._last_screen_x = 0
        self._last_screen_y = 0

    # --- mouse handling ---

    def on_mouse_down(self, event: events.MouseDown) -> None:
        self.capture_mouse()
        self._dragging = True
        self._last_screen_x = event.screen_x
        self._last_screen_y = event.screen_y
        self.add_class("-dragging")
        event.stop()

    def on_mouse_move(self, event: events.MouseMove) -> None:
        if not self._dragging:
            return
        dx = event.screen_x - self._last_screen_x
        dy = event.screen_y - self._last_screen_y
        if dx == 0 and dy == 0:
            return
        self._last_screen_x = event.screen_x
        self._last_screen_y = event.screen_y
        self.post_message(self.Dragged(dx, dy))

    def on_mouse_up(self, event: events.MouseUp) -> None:  # noqa: ARG002
        if not self._dragging:
            return
        self._dragging = False
        self.remove_class("-dragging")
        try:
            self.release_mouse()
        except Exception:
            pass
        self.post_message(self.Released())
