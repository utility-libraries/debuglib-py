# -*- coding=utf-8 -*-
r"""

"""
import socket
from datetime import datetime
from ...core.server import DebugServer
from ...core.common import extract_server_info
from ..._typing import ServerInfoRaw, Message
from ..._packages import format_exception


class CLIListener:
    def __init__(self, server_info: ServerInfoRaw = None):
        self.server_info = server_info = extract_server_info(server_info)
        self._server = DebugServer(server_info=server_info)
        self._server.on_connection_open(self.on_connection_open)
        self._server.on_connection_closed(self.on_connection_closed)
        self._server.on_message(self.on_message)
        self._server.on_error(self.on_error)

    def run(self):
        print(f"Listening on {self.server_info[0]}:{self.server_info[1]}")
        try:
            self._server.serve_forever()
        except KeyboardInterrupt:
            self._server.shutdown()
        finally:
            self._server.close()

    @staticmethod
    def on_connection_open(client: str):
        print(f"New Connection from {client} ({socket.getfqdn(client.partition(':')[0])})")

    @staticmethod
    def on_connection_closed(client: str):
        print(f"Connection closed from {client} ({socket.getfqdn(client.partition(':')[0])})")

    @staticmethod
    def on_message(message: Message, client: str):
        ts = datetime.fromtimestamp(message['timestamp']).strftime("%H:%M:%S.%f")
        level = message['level'][:3].upper()
        print(f"{ts} | {client} | {message['program']} | {level:.3} | {message['message']}")
        exception_info = message['exception_info']
        if exception_info:
            print(exception_info['traceback'], flush=False)
            print(f"{exception_info['type']}: {exception_info['value']}", flush=False)
            print("--------------------------------------------------------------------------------")

    @staticmethod
    def on_error(error: Exception):
        print("----- <Server Error> -----------------------------------------------------------", flush=False)
        print('\n'.join(format_exception(type(error), error, error.__traceback__)), flush=False)  # file=sys.stderr?
        print("--------------------------------------------------------------------------------")
