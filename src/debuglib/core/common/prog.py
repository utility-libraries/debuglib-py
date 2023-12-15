# -*- coding=utf-8 -*-
r"""

"""
import functools


@functools.cache
def get_prog() -> str:
    import os, sys  # noqa: E401
    main = sys.modules.get('__main__')
    if not main:
        return "<unknown>"
    file = getattr(main, '__file__', '<unknown>')
    if file.startswith('<') and file.endswith('>'):  # <unknown> | <stdin>
        return file
    filename, _ = os.path.splitext(os.path.basename(file))
    if filename in {'__main__', '__init__'}:
        filename = os.path.basename(os.path.dirname(file))
    return filename
