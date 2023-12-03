# -*- coding=utf-8 -*-
r"""
logging-handler to send messages to the debug-server
"""
import logging
from ..typing import ServerInfoRaw
from ..core import DebugClient


class BlockingDebugHandler(logging.Handler):
    # creates connection to server
    def __init__(self, server_info: ServerInfoRaw = None):
        super().__init__()
        self._client = DebugClient(server_info=server_info)

    def emit(self, record: logging.LogRecord):
        self._client.send(
            message=f"{record.levelname} | {record.getMessage()}",
            # body=...,
            exception=record.exc_info[1] if record.exc_info else None,
            timestamp=record.created,
        )


class NonBlockingDebugHandler(logging.Handler):
    # works with queue (logging.handlers.QueueListener)
    pass
