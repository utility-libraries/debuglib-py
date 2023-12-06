# -*- coding=utf-8 -*-
r"""

"""
import time
import functools
from inspect import iscoroutinefunction
from ..core import DebugClient
from ..typing import ServerInfoRaw
from .util import function_repr, format_delta_ns


class Decorator:
    def __init__(self, server: ServerInfoRaw = None):
        self._client = DebugClient(server_info=server)

    def __del__(self):
        self._client.close()

    def reset_connection(self):
        self._client.close()

    def monitor(self, precision: int = 2):
        r"""
        monitor a sync/async function and sending the information (arguments, return-value, time) to the debug-server

        :param precision: time-precision
        :return: decorator
        """

        def decorator(fn):
            if iscoroutinefunction(fn):
                @functools.wraps(fn)
                async def wrapper(*args, **kwargs):
                    fn_repr = function_repr(fn, args, kwargs)
                    start_time = time.perf_counter_ns()
                    try:
                        value = await fn(*args, **kwargs)
                        total_time_ns = time.perf_counter_ns() - start_time
                        time_repr = format_delta_ns(total_time_ns, precision=precision)
                        self._client.send(
                            message=f"{fn_repr} returned {value!r} after {time_repr}",
                        )
                        return value
                    except BaseException as error:
                        total_time_ns = time.perf_counter_ns() - start_time
                        time_repr = format_delta_ns(total_time_ns, precision=precision)
                        self._client.send(
                            message=f"{fn_repr} failed with {type(error).__name__} after {time_repr}",
                            exception=error,
                        )
                        raise error
            else:
                @functools.wraps(fn)
                def wrapper(*args, **kwargs):
                    fn_repr = function_repr(fn, args, kwargs)
                    start_time = time.perf_counter_ns()
                    try:
                        value = fn(*args, **kwargs)
                        total_time_ns = time.perf_counter_ns() - start_time
                        time_repr = format_delta_ns(total_time_ns, precision=precision)
                        self._client.send(
                            message=f"{fn_repr} returned {value!r} after {time_repr}",
                        )
                        return value
                    except BaseException as error:
                        total_time_ns = time.perf_counter_ns() - start_time
                        time_repr = format_delta_ns(total_time_ns, precision=precision)
                        self._client.send(
                            message=f"{fn_repr} failed with {type(error).__name__} after {time_repr}",
                            exception=error,
                        )
                        raise error
            return wrapper
        return decorator


def monitor(*, server: ServerInfoRaw = None, precision: int = 2):
    r"""
    monitor a sync/async function and sending the information (arguments, return-value, time) to the debug-server

    recommended to use the Decorator-class for better performance through one connection to the server

    :param server: server information
    :param precision: time-precision
    :return: decorator
    """
    return Decorator(server=server).monitor(precision=precision)
