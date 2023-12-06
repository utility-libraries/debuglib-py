# -*- coding=utf-8 -*-
r"""

"""
import sys
import typing as t
from ..core.client import DebugClient


__all__ = ['hook']


original_hook: t.Optional[t.Callable[[t.Type[Exception], Exception, t.Any], None]] = None


def excepthook(exc, val, tb):
    client = DebugClient()
    client.send("sys.excepthook", exception=val)
    client.close()
    if original_hook is not None:
        original_hook(exc, val, tb)


def hook():
    global original_hook
    original_hook = sys.excepthook
    sys.excepthook = excepthook


def unhook(*, allow_unchanged: bool = False):
    global original_hook
    if original_hook is None:
        if allow_unchanged:
            return
        else:
            raise RuntimeError("unable to restore hook as it wasn't changed")
    sys.excepthook = original_hook
    original_hook = None
