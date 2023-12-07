# -*- coding=utf-8 -*-
r"""

"""
import time
import functools
from inspect import iscoroutinefunction
from ..core import DebugClient
from .._typing import DEFAULT_VALUE, ServerInfoRaw
from ._util import function_repr, format_delta_ns


class Decorator:
    def __init__(self, server_info: ServerInfoRaw = DEFAULT_VALUE,
                 *, timeout: float = DEFAULT_VALUE, connection_attempt_delta: float = DEFAULT_VALUE):
        self._client = DebugClient(
            server_info=server_info, timeout=timeout, connection_attempt_delta=connection_attempt_delta
        )

    def __del__(self):
        self._client.close()

    def reset_connection(self):
        self._client.close()

    def monitor(self, time_precision: int = 2):
        r"""
        monitor a sync/async function and sending the information (arguments, return-value, time) to the debug-server

        :param time_precision: 1=>1s | 2=>1s+1ms | 3=>1s+1ms+1μs | ...
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
                        time_repr = format_delta_ns(total_time_ns, precision=time_precision)
                        self._client.send(
                            message=f"{fn_repr} returned {value!r} after {time_repr}",
                        )
                        return value
                    except BaseException as error:
                        total_time_ns = time.perf_counter_ns() - start_time
                        time_repr = format_delta_ns(total_time_ns, precision=time_precision)
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
                        time_repr = format_delta_ns(total_time_ns, precision=time_precision)
                        self._client.send(
                            message=f"{fn_repr} returned {value!r} after {time_repr}",
                        )
                        return value
                    except BaseException as error:
                        total_time_ns = time.perf_counter_ns() - start_time
                        time_repr = format_delta_ns(total_time_ns, precision=time_precision)
                        self._client.send(
                            message=f"{fn_repr} failed with {type(error).__name__} after {time_repr}",
                            exception=error,
                        )
                        raise error
            return wrapper
        return decorator


def monitor(*, server_info: ServerInfoRaw = DEFAULT_VALUE,
            timeout: float = DEFAULT_VALUE, connection_attempt_delta: float = DEFAULT_VALUE,
            time_precision: int = 2):
    r"""
    monitor a sync/async function and sending the information (arguments, return-value, time) to the debug-server

    recommended to use the Decorator-class for better performance through one connection to the server

    :param server_info: server information
    :param timeout: socket timeout
    :param connection_attempt_delta: delta between connection attempts
    :param time_precision: time-precision
    :return: decorator
    """
    return Decorator(
        server_info=server_info, timeout=timeout, connection_attempt_delta=connection_attempt_delta,
    ).monitor(
        time_precision=time_precision
    )
