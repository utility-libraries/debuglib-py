# -*- coding=utf-8 -*-
r"""

"""
import threading
from io import StringIO
from datetime import datetime
import textual.binding
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from ..._typing import ServerInfoRaw, Message
from ...core import DebugServer


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

    def exit(self, *args, **kwargs) -> None:
        self._server.shutdown()
        super().exit(*args, **kwargs)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield textual.widgets.Log()
        yield Footer()

    @property
    def message_log(self) -> textual.widgets.Log:
        return self.query_one(textual.widgets.Log)

    def on_mount(self) -> None:
        self._thread = threading.Thread(target=self._server.serve_forever, name="debuglib server mainloop")
        self._thread.start()

        self.message_log.write(f"Listening on {self._server.server_info[0]}:{self._server.server_info[1]}\n")

    def server_on_connection_open(self, client: str) -> None:
        import socket
        domain_name = socket.getfqdn(client.partition(':')[0])
        self.notify(
            title="New Connection",
            message=f"{client} ({domain_name})",
            severity="information",
            timeout=5,
        )

    def server_on_connection_closed(self, client: str) -> None:
        import socket
        domain_name = socket.getfqdn(client.partition(':')[0])
        self.notify(
            title="Connection Closed",
            message=f"{client} ({domain_name})",
            severity="information",
            timeout=5,
        )

    def server_on_message(self, message: Message, client: str) -> None:
        text = StringIO()

        ts = datetime.fromtimestamp(message['timestamp']).strftime("%H:%M:%S.%f")
        level = message['level'][:3].upper()

        text.write(f"{ts} | {client} | {level:.3} | {message['message']}\n")

        exception_info = message['exception_info']
        if exception_info:
            text.write(exception_info['traceback'])
            text.write(f"{exception_info['type']}: {exception_info['value']}\n")

        self.message_log.write(text.getvalue())

    def server_on_error(self, error: Exception) -> None:
        self.notify(
            title=type(error).__name__,
            message=str(error),
            severity="error",
            timeout=5,
        )
