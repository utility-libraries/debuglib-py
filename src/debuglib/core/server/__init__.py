# -*- coding=utf-8 -*-
r"""

"""
import socket
import select
import threading
import typing as t
import json
# noinspection PyPep8Naming
from ... import __version__ as DEBUGLIB_VERSION
from ...typing import ServerInfoRaw, Message
from ..common import extract_server_info
try:
    import msgpack
except ModuleNotFoundError:
    msgpack = None

# import socketserver
# socketserver.BaseServer.serve_forever


BODY_PARSER = {
    b'j': json.loads,
}
if msgpack:
    BODY_PARSER[b'm'] = msgpack.loads


class DebugServer:
    _server: socket.socket
    _connections: t.Dict[socket.socket, t.Tuple[str, t.BinaryIO]]
    _on_message: t.List[t.Callable[[Message, str], None]]
    _on_connection: t.List[t.Callable[[str], None]]
    _shutdown_requested: bool
    _is_shut_down: threading.Event

    def __init__(self, server_info: ServerInfoRaw = None):
        self._server = socket.create_server(address=extract_server_info(server_info))
        self._connections = {}
        self._on_message = []
        self._on_connection = []
        self._shutdown_requested = False
        self._is_shut_down = threading.Event()

    def serve_forever(self):
        self._shutdown_requested = False
        self._is_shut_down.clear()
        try:
            while not self._shutdown_requested:
                ready, *_ = select.select([self._server, *self._connections.keys()], [], [], 0.1)
                # bpo-35017: shutdown() called during select(), exit immediately.
                if self._shutdown_requested:
                    break
                if ready:
                    for sock in ready:
                        if sock is self._server:
                            self._handle_new_connection()
                        else:
                            self._handle_one_message(sock)
        finally:
            self._shutdown_requested = False
            self._is_shut_down.set()

    def shutdown(self):
        self._shutdown_requested = True
        self._is_shut_down.wait()

    def on_connection(self, callback: t.Callable[[str], None]):
        self._on_connection.append(callback)

    def on_message(self, callback: t.Callable[[Message], None]):
        self._on_message.append(callback)

    def _handle_new_connection(self):
        connection, client_address = self._server.accept()
        rfile = connection.makefile('rb', -1)

        # @handshake
        # check for the debuglib protocol
        head = b'DEBUGLIB\0'
        if rfile.read(len(head)) != head:
            connection.close()
        # compare versions (could be improved to only check major.minor)
        version_length = int.from_bytes(rfile.read(1), byteorder='big', signed=False)
        if rfile.read1(version_length) != DEBUGLIB_VERSION.encode():
            connection.close()
        # trailing head to ensure everything was read correctly
        if rfile.read(1) != '\0':
            connection.close()
        connection.sendall(b'1')  # accept the connection

        for callback in self._on_connection:
            callback(client_address)
        self._connections[connection] = (client_address, rfile)

    def _handle_one_message(self, sock: socket.socket):
        client_address, rfile = self._connections[sock]
        body_format_identifier = rfile.read(1)
        length = int.from_bytes(rfile.read(2), byteorder='big', signed=False)
        body = rfile.read(length)
        body_parser = BODY_PARSER.get(body_format_identifier)
        if body_parser is None:  # unsupported
            # todo: error message
            return
        message: Message = body_parser(body)
        for callback in self._on_message:
            callback(message, client_address)
