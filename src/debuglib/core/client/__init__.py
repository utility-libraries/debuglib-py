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
import socket
import time
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
except ModuleNotFoundError:
    from traceback import format_exception


class DebugClient:
    _conn: t.Optional[socket.socket]

    def __init__(self, *, server: ServerInfoRaw = None, timeout: float = None):
        self._server_info: ServerInfo = extract_server_info(server)
        self._timeout: float = timeout
        self._conn = None
        self._queue = None

    def __del__(self):
        self.close()

    def close(self):
        if self._conn is not None:
            self._conn.close()

    def send(self, message: str,
             *, body: t.Optional[str] = None, exception: t.Optional[BaseException] = None, timestamp: float = None):
        self._conn = conn = self._conn or self.create_connection()
        if conn is None:
            return
        message = self.build_message(message=message, body=body, exception=exception)
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
                traceback='\n'.join(format_exception(exception)),
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
                sock.close()
                return None
            return sock
        except (socket.error, socket.timeout, TimeoutError):
            return None
