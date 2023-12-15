# -*- coding=utf-8 -*-
r"""

"""
import threading
from io import StringIO
from datetime import datetime
from collections import defaultdict
from rich.markup import escape  # noqa
import textual.binding
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from ..._typing import ServerInfoRaw, Message
from ...core import DebugServer
from ..._packages import format_traceback


LEVEL2COLOR = {
    "DEB": "grey37",
    "INF": "green1",
    "WAR": "yellow3",
    "ERR": "red3",
    "CRI": "bright_red",
}


def new_random_color() -> str:
    import random
    r = random.randint(128, 255)
    g = random.randint(128, 255)
    b = random.randint(128, 255)
    return f"[rgb({r},{g},{b})]"


class CLIDebugger(App):
    BINDINGS = [
        textual.app.Binding("ctrl+c", "quit", "Quit"),  # default
        textual.app.Binding("ctrl+q", "quit", "Quit", show=False),  # unix-like
        textual.app.Binding("ctrl+x", "quit", "Quit", show=False),  # nano-like
        # textual.binding.Binding("ctrl+d", 'toggle_dark', "Toggle Dark-Mode"),
    ]

    CSS = r"""
    * {
        transition: background 500ms in_out_cubic, color 500ms in_out_cubic;
    }
    """

    _thread: 'threading.Thread' = None

    def __init__(self, server_info: ServerInfoRaw = None):
        super().__init__()
        self._server = DebugServer(server_info=server_info)
        self._server.on_connection_open(self.server_on_connection_open)
        self._server.on_connection_closed(self.server_on_connection_closed)
        self._server.on_message(self.server_on_message)
        self._server.on_error(self.server_on_error)
        self._client_color_map = defaultdict(new_random_color)
        self._program_color_map = defaultdict(new_random_color)

    def exit(self, *args, **kwargs) -> None:
        self._server.shutdown()
        super().exit(*args, **kwargs)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield textual.widgets.RichLog(max_lines=100_000, highlight=False, markup=True)
        yield Footer()

    @property
    def message_log(self) -> textual.widgets.RichLog:
        return self.query_one(textual.widgets.RichLog)

    def write(self, message: str):
        self.message_log.write(message)

    def highlight(self, text: str):
        from rich.text import Text  # noqa
        return self.message_log.highlighter(Text(escape(text))).markup

    def on_mount(self) -> None:
        self._thread = threading.Thread(target=self._server.serve_forever, name="debuglib server mainloop")
        self._thread.start()

        self.write(f"[turquoise2]Listening on {self._server.server_info[0]}:{self._server.server_info[1]}[/]")
        self.write(f"[turquoise2]{'Timestamp'.center(15)} | {'client'.center(15)} | {'program'.center(10)} "
                   f"| {'LVL'} | {'Message'}[/]")

    def server_on_connection_open(self, client: str) -> None:
        import socket
        domain_name = socket.getfqdn(client.partition(':')[0])
        self.notify(
            title="New Connection",
            message=f"{client} ({domain_name})",
            severity="information",
            timeout=5,
        )
        self.write(f"[turquoise2]New Connection from[/] "
                   f"{self._client_color_map[client]}{client}[/] "
                   f"[turquoise2]({escape(domain_name)})[/]")

    def server_on_connection_closed(self, client: str) -> None:
        import socket
        domain_name = socket.getfqdn(client.partition(':')[0])
        self.notify(
            title="Connection Closed",
            message=f"{client} ({domain_name})",
            severity="information",
            timeout=5,
        )
        self.write(f"[turquoise2]Connection closed from[/] "
                   f"{self._client_color_map[client]}{client}[/] "
                   f"[turquoise2]({escape(domain_name)})[/]")
        del self._client_color_map[client]  # cleanup

    def server_on_message(self, message: Message, client: str) -> None:
        text = StringIO()

        ts = datetime.fromtimestamp(message['timestamp']).strftime("%H:%M:%S.%f")
        level = message['level'][:3].upper()
        program = message['program']

        text.write(" | ".join([
            f"[turquoise2]{ts}[/]",
            f"{self._client_color_map[client]}{client}[/]",
            f"{self._program_color_map[program]}{program.ljust(10)}[/]",
            f"[{LEVEL2COLOR.get(level, '')}]{level:.3}[/]",
            f"{message['message']}"
        ]))

        exception_info = message['exception_info']
        if exception_info:
            text.write(f"\n"
                       f"{self.highlight(exception_info['traceback'])}\n"
                       f"[red]{exception_info['type']}:[/] {self.highlight(exception_info['value'])}")

        self.write(text.getvalue())

    def server_on_error(self, error: Exception) -> None:
        self.notify(
            title=type(error).__name__,
            message=str(error),
            severity="error",
            timeout=5,
        )
        exc_str = '\n'.join(format_traceback(error.__traceback__))
        self.write(f"----- <Server Error> -----------------------------------------------------------\n"
                   f"{self.highlight(exc_str)}\n"
                   f"[red]{type(error).__name__}:[/] {self.highlight(str(error))}\n"
                   f"--------------------------------------------------------------------------------")
