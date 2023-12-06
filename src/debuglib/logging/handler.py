# -*- coding=utf-8 -*-
r"""
logging-handler to send messages to the debug-server
"""
import copy
import queue
import logging.handlers
from .._typing import ServerInfoRaw
from ..core import DebugClient


class BlockingDebugHandler(logging.Handler):
    r"""
    Logging-Handler that blocks as it waits till the message is sent to the server (if the server exists)
    """

    def __init__(self, server_info: ServerInfoRaw = None):
        super().__init__()
        self._client = DebugClient(server_info=server_info)

    def emit(self, record: logging.LogRecord):
        self._client.send(
            message=record.getMessage(),
            level=record.levelname,
            exception=record.exc_info[1] if record.exc_info else None,
            timestamp=record.created,
        )


class NonBlockingDebugHandler(logging.handlers.QueueHandler):
    r"""
    Logging-Handler for high-performance code that queues the logs and sends them in another thread to the server

    known to have problems with very short programs
    """

    def __init__(self, server_info: ServerInfoRaw = None):
        self._queue = queue.Queue()
        super().__init__(self._queue)
        self.__blocking_handler = BlockingDebugHandler(server_info=server_info)
        self._listener = logging.handlers.QueueListener(self._queue, self.__blocking_handler)
        self._listener.start()

    def __del__(self):
        self._listener.stop()

    # custom one as the original removes unpickleable elements but we don't pickle
    def prepare(self, record: logging.LogRecord) -> logging.LogRecord:
        return copy.copy(record)
