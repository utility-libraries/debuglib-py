# -*- coding=utf-8 -*-
r"""

"""
import typing as t


ServerInfo = t.Tuple[str, int]
ServerInfoRaw = t.Union[None, str, int, ServerInfo]


class ExceptionInfo(t.TypedDict):
    type: str  # type(exception)
    value: str  # str(exception)
    traceback: str  # format_traceback(exception)


class Message(t.TypedDict):
    message: str  # "short" message
    body: t.Optional[str]  # longer more detailed message
    exception_info: t.Optional[ExceptionInfo]
    timestamp: float
