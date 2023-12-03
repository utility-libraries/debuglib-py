# -*- coding=utf-8 -*-
r"""

"""
import socket
from datetime import datetime
from ...core.server import DebugServer
from ...core.common import extract_server_info
from ...typing import ServerInfoRaw, Message


class CLIListener:
    def __init__(self, server_info: ServerInfoRaw = None):
        self.server_info = server_info = extract_server_info(server_info)
        self._server = DebugServer(server_info=server_info)
        self._server.on_connection_open(self.on_connection_open)
        self._server.on_connection_closed(self.on_connection_closed)
        self._server.on_message(self.on_message)

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
        print(f"New Connection from {client} ({socket.getfqdn(client)})")

    @staticmethod
    def on_connection_closed(client: str):
        print(f"Connection closed from {client} ({socket.getfqdn(client)})")

    @staticmethod
    def on_message(message: Message, client: str):
        ts = datetime.fromtimestamp(message['timestamp']).strftime("%M:%S.%f")
        print(f"{ts} | {client} | {message['message']}")
        body = message['body']
        exception_info = message['exception_info']
        if body or exception_info:
            print(f"=" * 80)
        if body:
            print(body)
            print(f"=" * 80)
        if exception_info:
            print(exception_info['traceback'])
            print(f"{exception_info['type']}: {exception_info['value']}")
            print(f"=" * 80)
