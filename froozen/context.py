# -*- coding=utf-8 -*-
r"""

"""
import sys
import types
import traceback
import typing as t


class ContextInfo(t.NamedTuple):
    filename: str
    modulename: str
    lines: t.List[t.Tuple[int, str]]


def get_context(*, lines_around: int = 2) -> ContextInfo:
    frame, code, filename, modulename, lineno = _outside_of_package("debuglib")
    return ContextInfo(
        filename=filename,
        modulename=modulename,
        lines=_format_frame_lines(frame=frame, lineno=lineno, around=lines_around)
    )


def _format_frame_lines(frame: types.FrameType, lineno: int, around: int) -> t.List[t.Tuple[int, str]]:
    import linecache
    code = frame.f_code
    return [(no, linecache.getline(code.co_filename, no)) for no in range(lineno - around, lineno + around + 1)]


class _OutsideInfo(t.NamedTuple):
    frame: types.FrameType
    code: types.CodeType
    filename: str
    modulename: str
    lineno: int


def _outside_of_package(package: str) -> _OutsideInfo:
    frame = sys._getframe()  # noqa
    for frame, lineno in traceback.walk_stack(frame):
        code = frame.f_code
        module = _file2module(code.co_filename)
        if not module.__name__.startswith(package):
            return _OutsideInfo(
                frame=frame, code=code, filename=code.co_filename, modulename=module.__name__, lineno=lineno
            )
    raise LookupError("can't find outside code")


def _file2module(file: str) -> types.ModuleType:
    for module in sys.modules.values():
        if not hasattr(module, '__file__'):
            continue
        if module.__file__ == file:
            return module
    raise LookupError(f"can't find module for file {file!r}")
