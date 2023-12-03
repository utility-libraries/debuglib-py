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


TC_CONNECTION_OPEN = t.Callable[[str], None]
TC_CONNECTION_CLOSED = t.Callable[[str], None]
TC_MESSAGE = t.Callable[[Message, str], None]


class DebugServer:
    _server: socket.socket
    _connections: t.Dict[int, t.Tuple[socket.socket, str, t.BinaryIO]]
    _on_connection_open: t.List[TC_CONNECTION_OPEN]
    _on_connection_closed: t.List[TC_CONNECTION_CLOSED]
    _on_message: t.List[TC_MESSAGE]
    _shutdown_requested: bool
    _is_shut_down: threading.Event

    def __init__(self, server_info: ServerInfoRaw = None):
        self._server = socket.create_server(address=extract_server_info(server_info))
        self._connections = {}
        self._on_message = []
        self._on_connection_open = []
        self._on_connection_closed = []
        self._shutdown_requested = False
        self._is_shut_down = threading.Event()

    def __del__(self):
        self.close()

    def close(self):
        self._server.close()

    def serve_forever(self):
        self._shutdown_requested = False
        self._is_shut_down.clear()
        try:
            while not self._shutdown_requested:
                readable, *_ = select.select([self._server, *self._connections], [], [], 0.1)
                # bpo-35017: shutdown() called during select(), exit immediately.
                if self._shutdown_requested:
                    break
                for fd in readable:
                    if fd is self._server:
                        self._handle_new_connection()
                    else:
                        self._handle_one_message(fd)
        finally:
            self._shutdown_requested = False
            self._is_shut_down.set()

    def shutdown(self):
        self._shutdown_requested = True
        self._is_shut_down.wait()

    def on_connection_open(self, callback: TC_CONNECTION_OPEN):
        self._on_connection_open.append(callback)

    def on_connection_closed(self, callback: TC_CONNECTION_CLOSED):
        self._on_connection_closed.append(callback)

    def on_message(self, callback: TC_MESSAGE):
        self._on_message.append(callback)

    def _handle_new_connection(self):
        connection, client_info = self._server.accept()
        client_address: str = client_info[0]
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

        for callback in self._on_connection_open:
            callback(client_address)
        self._connections[connection.fileno()] = (connection, client_address, rfile)

    def _handle_one_message(self, fd: int):
        sock, client_address, rfile = self._connections[fd]
        body_format_identifier = rfile.read(1)
        if not body_format_identifier:  # b''
            self._close_connection(fd=fd)
            return

        length = int.from_bytes(rfile.read(2), byteorder='big', signed=False)
        body = rfile.read(length)
        body_parser = BODY_PARSER.get(body_format_identifier)
        if body_parser is None:  # unsupported
            # todo: error message
            return
        message: Message = body_parser(body)
        for callback in self._on_message:
            callback(message, client_address)

    def _close_connection(self, fd: int):
        sock, client_address, rfile = self._connections[fd]
        rfile.close()
        sock.close()
        del self._connections[fd]
        for callback in self._on_connection_closed:
            callback(client_address)
