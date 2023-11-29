# -*- coding=utf-8 -*-
r"""
logging-handler to send messages to the debug-server
"""
import logging.handlers


class BlockingDebugHandler(logging.Handler):
    # creates connection to server
    pass


class NonBlockingDebugHandler(logging.Handler):
    # works with queue (logging.handlers.QueueListener)
    pass
