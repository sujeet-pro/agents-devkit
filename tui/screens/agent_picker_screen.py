from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import OptionList, Static
from textual.widgets.option_list import Option

from tui.agent_registry import list_agents


class AgentPickerScreen(ModalScreen[str | None]):
    """Modal picker for the runner registry. Dismiss with the picked name
    on enter; dismiss with None on escape."""

    BINDINGS = [Binding("escape", "cancel", show=False)]

    DEFAULT_CSS = """
    AgentPickerScreen {
        align: center middle;
    }
    AgentPickerScreen > Container {
        width: 64;
        height: auto;
        padding: 1 2;
        border: round $accent;
        background: $surface;
    }
    AgentPickerScreen Static {
        width: 100%;
        padding-bottom: 1;
    }
    AgentPickerScreen OptionList {
        width: 100%;
        height: auto;
    }
    """

    def __init__(self, *, current: str = "claude") -> None:
        super().__init__()
        self._current = current

    def compose(self) -> ComposeResult:
        with Container():
            yield Static(
                f"Pick runner (current: {self._current})",
                markup=False,
            )
            opts = [
                Option(f"{spec.name:10s}  {spec.description}", id=spec.name)
                for spec in list_agents()
            ]
            yield OptionList(*opts)

    def on_mount(self) -> None:
        opt_list = self.query_one(OptionList)
        for i, spec in enumerate(list_agents()):
            if spec.name == self._current:
                opt_list.highlighted = i
                break

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self.dismiss(event.option.id)

    def action_cancel(self) -> None:
        self.dismiss(None)
