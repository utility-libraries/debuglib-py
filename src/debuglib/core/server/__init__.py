# -*- coding=utf-8 -*-
r"""

"""
import sys
import json
import socket
import select
import threading
import typing as t
# noinspection PyPep8Naming
from ... import __version__ as DEBUGLIB_VERSION
from ...typing import ServerInfoRaw, Message
from ..common import extract_server_info
try:
    import msgpack
except ModuleNotFoundError:
    msgpack = None
try:
    from better_exceptions import format_exception
except ModuleNotFoundError:
    from traceback import format_exception

# import socketserver
# socketserver.BaseServer.serve_forever


BODY_PARSER = {
    b'j': json.loads,
}
if msgpack:
    BODY_PARSER[b'm'] = msgpack.loads


T_CB_CONNECTION_OPEN = t.Callable[[str], None]
T_CB_CONNECTION_CLOSED = t.Callable[[str], None]
T_CB_MESSAGE = t.Callable[[Message, str], None]
T_CB_ERROR = t.Callable[[Exception], None]


class DebugServer:
    _server: socket.socket
    _connections: t.Dict[int, t.Tuple[socket.socket, str, t.BinaryIO]]
    _on_connection_open: t.List[T_CB_CONNECTION_OPEN]
    _on_connection_closed: t.List[T_CB_CONNECTION_CLOSED]
    _on_message: t.List[T_CB_MESSAGE]
    _on_error: t.List[T_CB_ERROR]
    _skip_version_check: bool
    _shutdown_requested: bool
    _is_shut_down: threading.Event

    def __init__(self, server_info: ServerInfoRaw = None, *, skip_version_check: bool = False):
        self._server = socket.create_server(address=extract_server_info(server_info))
        self._connections = {}
        self._on_message = []
        self._on_error = []
        self._on_connection_open = []
        self._on_connection_closed = []
        self._skip_version_check = skip_version_check
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
                readable, *_ = select.select([self._server, *self._connections], [], [], 0.5)
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

    def on_connection_open(self, callback: T_CB_CONNECTION_OPEN):
        self._on_connection_open.append(callback)
        return callback

    def on_connection_closed(self, callback: T_CB_CONNECTION_CLOSED):
        self._on_connection_closed.append(callback)
        return callback

    def on_message(self, callback: T_CB_MESSAGE):
        self._on_message.append(callback)
        return callback

    def on_error(self, callback: T_CB_ERROR):
        self._on_error.append(callback)
        return callback

    def _handle_error(self, error: Exception):
        if not self._on_error:  # no error handler registered
            sys.stderr.write('\n'.join(format_exception(type(error), error, error.__traceback__)))
        else:
            for callback in self._on_error:
                try:
                    callback(error)
                except Exception as cb_err:
                    sys.stderr.write('\n'.join(format_exception(type(cb_err), cb_err, cb_err.__traceback__)))

    def _call_no_error(self, fn: t.Callable, *args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as error:
            self._handle_error(error)

    def _handle_new_connection(self):
        connection, client_info = self._server.accept()
        client: str = f"{client_info[0]}:{client_info[1]}"  # ip:port
        rfile = connection.makefile('rb', -1)

        # @handshake
        # check for the debuglib protocol
        head = b'DEBUGLIB\0'
        if rfile.read(len(head)) != head:
            connection.close()
            self._handle_error(ConnectionError("bad connection attempt was made"))
            return
        # compare versions (could be improved to only check major.minor)
        version_length = int.from_bytes(rfile.read(1), byteorder='big', signed=False)
        version = rfile.read1(version_length).decode()
        if not self._skip_version_check and version != DEBUGLIB_VERSION:
            connection.close()
            self._handle_error(ConnectionError(f"version mismatch ({version} != {DEBUGLIB_VERSION})"))
            return
        # trailing head to ensure everything was read correctly
        if rfile.read(1) != b'\0':
            connection.close()
            self._handle_error(ConnectionError("trailing null-byte was not found"))
            return
        connection.sendall(b'1')  # accept the connection

        for callback in self._on_connection_open:
            self._call_no_error(callback, client)
        self._connections[connection.fileno()] = (connection, client, rfile)

    def _handle_one_message(self, fd: int):
        sock, client, rfile = self._connections[fd]
        body_format_identifier = rfile.read(1)
        if not body_format_identifier:  # b'' connection was closed
            self._close_connection(fd=fd)
            return

        length = int.from_bytes(rfile.read(2), byteorder='big', signed=False)
        body = rfile.read(length)
        body_parser = BODY_PARSER.get(body_format_identifier)
        if body_parser is None:  # unsupported
            self._handle_error(LookupError(f"unknown parser code received: {body_format_identifier.decode()!r}"))
            # todo: add error feedback for the client so he doesn't connect again
            # self._close_connection(fd=fd)  # assuming the format will stay the same
            return
        message: Message = body_parser(body)
        for callback in self._on_message:
            self._call_no_error(callback, message, client)

    def _close_connection(self, fd: int):
        sock, client, rfile = self._connections[fd]
        rfile.close()
        sock.close()
        del self._connections[fd]
        for callback in self._on_connection_closed:
            self._call_no_error(callback, client)
