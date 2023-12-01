# -*- coding=utf-8 -*-
r"""

"""
import time
import logging
import functools
from itertools import chain
from inspect import iscoroutinefunction


class Decorator:
    def __init__(self):
        pass

    def monitor(self):
        def decorator(fn):
            if iscoroutinefunction(fn):
                @functools.wraps(fn)
                async def wrapper(*args, **kwargs):
                    args_repr = map(repr, args)
                    kwargs_repr = (f'{key}={repr(val)}' for key, val in kwargs.items())
                    fn_msg = f"async {fn.__name__}({', '.join(chain(args_repr, kwargs_repr))})"
                    start_time = time.perf_counter()
                    try:
                        value = await fn(*args, **kwargs)
                        total_time = time.perf_counter() - start_time
                        logging.debug(f"{fn_msg} returned {value!r} after {total_time}s")
                        return value
                    except BaseException as error:
                        total_time = time.perf_counter() - start_time
                        logging.error(f"{fn_msg} failed with {type(error).__name__} after {total_time}s",
                                      exc_info=error)
                        raise error
            else:
                @functools.wraps(fn)
                def wrapper(*args, **kwargs):
                    args_repr = map(repr, args)
                    kwargs_repr = (f'{key}={repr(val)}' for key, val in kwargs.items())
                    fn_msg = f"{fn.__name__}({', '.join(chain(args_repr, kwargs_repr))})"
                    start_time = time.perf_counter()
                    try:
                        value = fn(*args, **kwargs)
                        total_time = time.perf_counter() - start_time
                        logging.debug(f"{fn_msg} returned {value!r} after {total_time}s")
                        return value
                    except BaseException as error:
                        total_time = time.perf_counter() - start_time
                        logging.error(f"{fn_msg} failed with {type(error).__name__} after {total_time}s",
                                      exc_info=error)
                        raise error
            return wrapper
        return decorator


def monitor(*args, **kwargs):
    return Decorator(*args, **kwargs).monitor
