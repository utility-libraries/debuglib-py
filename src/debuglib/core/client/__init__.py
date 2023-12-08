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
# noinspection PyPep8Naming
from ... import __version__ as DEBUGLIB_VERSION
from ..._packages import json, format_traceback, format_exception
from ..._typing import DEFAULT_VALUE, ServerInfo, ServerInfoRaw, Message
from ..common import extract_server_info


T_CB_ON_ERROR = t.Callable[[Exception], None]


class DebugClient:
    _server_info: ServerInfo
    _timeout: float
    _conn: t.Optional[socket.socket]
    _on_error: t.List[T_CB_ON_ERROR]
    _print_on_error: bool
    _connection_attempt_delta: float
    _next_connection_attempt: float

    def __init__(self, *, server_info: ServerInfoRaw = DEFAULT_VALUE, timeout: float = DEFAULT_VALUE,
                 connection_attempt_delta: float = DEFAULT_VALUE):
        r"""

        :param server_info: information about the server (host|port|(host, port))
        :param timeout: socket timeout
        :param connection_attempt_delta: delta between connection attempts
        """
        self._server_info = extract_server_info(server_info)
        self._timeout = None if timeout is DEFAULT_VALUE else timeout
        self._connection_attempt_delta = 0.1 if connection_attempt_delta is DEFAULT_VALUE else connection_attempt_delta
        self._next_connection_attempt = 0.0
        self._print_on_error = False
        self._on_error = []
        self._conn = self.create_connection()

    def __del__(self):
        self.close()

    def close(self):
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    @property
    def server_info(self) -> ServerInfo:
        return self._server_info

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
             *, level: t.Optional[str] = None, exception: t.Optional[BaseException] = None,
             timestamp: float = None):
        self._conn = conn = self._conn or self.create_connection()
        if conn is None:
            return
        message = self.build_message(message=message, level=level, exception=exception, timestamp=timestamp)
        body = self.format_message(message)
        try:
            conn.sendall(body)
        except socket.error:
            self._conn = None

    @staticmethod
    def build_message(
            message: str,
            level: t.Optional[str] = None,
            exception: t.Optional[BaseException] = None,
            timestamp: float = None,
    ) -> Message:
        level = (level or ("INFO" if exception is None else "ERROR"))[:3].upper()  # DEB|INF|WAR|ERR|CRI
        return Message(
            message=message,
            level=level,
            exception_info=dict(
                type=type(exception).__name__,
                value=str(exception),
                traceback='\n'.join(format_traceback(exception.__traceback__)),
            ) if isinstance(exception, BaseException) else None,
            timestamp=time.time() if timestamp is None else timestamp,
        )

    @staticmethod
    def format_message(message: Message) -> bytes:
        body = json.dumps(message)
        if isinstance(body, str):
            body = body.encode()
        return b'j' + len(body).to_bytes(2, byteorder='big', signed=False) + body

    def create_connection(self) -> t.Optional[socket.socket]:
        r"""
        creates a connection and executes the handshake
        if the server cannot be found or rejects the connection this function returns None
        """
        now = time.time()
        if now < self._next_connection_attempt:
            return None
        try:
            self._next_connection_attempt = now + self._connection_attempt_delta
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
