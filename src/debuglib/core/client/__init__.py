# -*- coding=utf-8 -*-
r"""
Handshake Message:
- response of '1' means "connection accepted"
> DEBUGLIB\0{len:1}{version}\0
< 1

Normal Message:
- m: msgpack encoded body
- j: json encoded body
{m|j}{len:2}{body}
"""
import sys
import time
import socket
import typing as t
# import uuid
# noinspection PyPep8Naming
from ... import __version__ as DEBUGLIB_VERSION
from ..common import extract_server_info
from ...typing import ServerInfo, ServerInfoRaw, Message
try:
    # noinspection PyUnresolvedReferences
    from msgpack import dumps as dump_body
    body_format_identifier = b'm'
except ModuleNotFoundError:
    from json import dumps as dump_body
    body_format_identifier = b'j'
try:
    from better_exceptions import format_exception
    from better_exceptions.formatter import ExceptionFormatter

    def format_traceback(tb):
        formatter = ExceptionFormatter()
        return [formatter.format_traceback(tb)[0]]
except ModuleNotFoundError:
    from traceback import format_exception, format_tb as format_traceback


T_CB_ON_ERROR = t.Callable[[Exception], None]


class DebugClient:
    _server_info: ServerInfo
    _timeout: float
    _conn: t.Optional[socket.socket]
    _on_error: t.List[T_CB_ON_ERROR]
    _print_on_error: bool
    _last_attempt: float  # todo limit connection attempts

    def __init__(self, *, server_info: ServerInfoRaw = None, timeout: float = None):
        self._server_info = extract_server_info(server_info)
        self._timeout = timeout
        self._conn = self.create_connection()
        self._on_error = []
        self._print_on_error = False

    def __del__(self):
        self.close()

    def close(self):
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def on_error(self, callback: T_CB_ON_ERROR):
        self._on_error.append(callback)
        return callback

    def print_on_error(self, enable: bool = True):
        self._print_on_error = enable

    def _handle_error(self, error: Exception):
        if self._print_on_error:
            sys.stderr.write('\n'.join(format_exception(type(error), error, error.__traceback__)))

        for callback in self._on_error:
            try:
                callback(error)
            except Exception as cb_err:
                sys.stderr.write('\n'.join(format_exception(type(cb_err), cb_err, cb_err.__traceback__)))

    def send(self, message: str,
             *, body: t.Optional[str] = None, exception: t.Optional[BaseException] = None, timestamp: float = None):
        self._conn = conn = self._conn or self.create_connection()
        if conn is None:
            return
        message = self.build_message(message=message, body=body, exception=exception, timestamp=timestamp)
        body = self.format_message(message)
        try:
            conn.sendall(body)
        except socket.error:
            self._conn = None

    @staticmethod
    def build_message(
            message: str,
            body: t.Optional[str] = None,
            exception: t.Optional[BaseException] = None,
            timestamp: float = None,
    ) -> Message:
        return Message(
            message=message,
            body=body,
            exception_info=dict(
                type=type(exception).__name__,
                value=str(exception),
                traceback='\n'.join(format_traceback(exception.__traceback__)),
            ) if isinstance(exception, BaseException) else None,
            timestamp=time.time() if timestamp is None else timestamp,
        )

    @staticmethod
    def format_message(message: Message) -> bytes:
        body = dump_body(message)
        if isinstance(body, str):
            body = body.encode()
        return body_format_identifier + len(body).to_bytes(2, byteorder='big', signed=False) + body

    def create_connection(self) -> t.Optional[socket.socket]:
        r"""
        creates a connection and executes the handshake
        if the server cannot be found or rejects the connection this function returns None
        """
        try:
            sock = socket.create_connection(self._server_info, timeout=self._timeout)
            version = DEBUGLIB_VERSION.encode()
            version_bytes = len(version).to_bytes(1, byteorder='big', signed=False) + version
            handshake = b'DEBUGLIB\0' + version_bytes + b'\0'
            sock.sendall(handshake)
            if sock.recv(1) != b'1':
                self._handle_error(PermissionError("connection was refused"))
                sock.close()
                return None
            return sock
        except (socket.error, socket.timeout, TimeoutError) as error:
            self._handle_error(error)
            return None
