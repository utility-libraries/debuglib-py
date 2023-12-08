# -*- coding=utf-8 -*-
r"""

"""
try:  # try to use the faster orjson over the builtin one
    import orjson as json
except ModuleNotFoundError:
    import json

# maybe introduce that part later again
# try:
#     import msgpack
# except ModuleNotFoundError:
#     msgpack = None

try:
    from better_exceptions import format_exception, ExceptionFormatter as __ExceptionFormatter

    def format_traceback(tb):
        formatter = __ExceptionFormatter()
        return [formatter.format_traceback(tb)[0]]
except ModuleNotFoundError:
    from traceback import format_exception, format_tb as format_traceback

__all__ = [
    'json',
    # 'msgpack',
    'format_exception', 'format_traceback',
]
