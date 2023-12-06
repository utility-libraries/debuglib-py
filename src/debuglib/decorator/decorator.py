# -*- coding=utf-8 -*-
r"""

"""
import time
import functools
from itertools import chain
from inspect import iscoroutinefunction, getmodule
from ..core import DebugClient
from ..typing import ServerInfoRaw


# https://www.calculatorsoup.com/calculators/conversions/time.php
TIME_UNITS = {
    0.000000001: "ns",  # nanoseconds
    0.000001: "μs",  # microseconds
    0.001: "ms",  # milliseconds
    1: "s",  # seconds
    3600: "h",  # hours
    86400: "d",  # days
    604800: "wk",  # weeks
    2628000: "mo",  # months
}
TIME_UNITS_FACTORS = sorted(TIME_UNITS, reverse=True)  # biggest first
TIME_UNITS_COUNT = len(TIME_UNITS)


class Decorator:
    def __init__(self, server: ServerInfoRaw = None):
        self._client = DebugClient(server_info=server)

    def __del__(self):
        self._client.close()

    def reset_connection(self):
        self._client.close()

    @staticmethod
    def _function_repr(fn, args, kwargs):
        fn_name = f"{getmodule(fn).__name__}.{fn.__qualname__}"
        args_repr = map(repr, args)
        kwargs_repr = (f'{key}={repr(val)}' for key, val in kwargs.items())
        fn_msg = f"{fn_name}({', '.join(chain(args_repr, kwargs_repr))})"
        if iscoroutinefunction(fn):
            return f"async {fn_msg}"
        return fn_msg

    @staticmethod
    def _format_time(delta: float, precision: int = 3) -> str:
        start = next((index for index, factor in enumerate(TIME_UNITS_FACTORS) if delta >= factor), None)
        if start is None:
            return f"{delta}s"  # in case of delta <= 0
        parts = []
        rest = delta
        for index in range(start, min(start + precision, TIME_UNITS_COUNT)):
            factor = TIME_UNITS_FACTORS[index]
            count, rest = divmod(rest, factor)
            if count:
                parts.append(f"{int(count)}{TIME_UNITS[factor]}")
            if not rest:
                break
        return '+'.join(parts)

    def monitor(self):
        def decorator(fn):
            if iscoroutinefunction(fn):
                @functools.wraps(fn)
                async def wrapper(*args, **kwargs):
                    fn_repr = self._function_repr(fn, args, kwargs)
                    start_time = time.perf_counter()
                    try:
                        value = await fn(*args, **kwargs)
                        total_time = time.perf_counter() - start_time
                        time_repr = self._format_time(total_time)
                        self._client.send(
                            message=f"{fn_repr} returned {value!r} after {time_repr}",
                        )
                        return value
                    except BaseException as error:
                        total_time = time.perf_counter() - start_time
                        time_repr = self._format_time(total_time)
                        self._client.send(
                            message=f"{fn_repr} failed with {type(error).__name__} after {time_repr}",
                            exception=error,
                        )
                        raise error
            else:
                @functools.wraps(fn)
                def wrapper(*args, **kwargs):
                    fn_repr = self._function_repr(fn, args, kwargs)
                    start_time = time.perf_counter()
                    try:
                        value = fn(*args, **kwargs)
                        total_time = time.perf_counter() - start_time
                        time_repr = self._format_time(total_time)
                        self._client.send(
                            message=f"{fn_repr} returned {value!r} after {time_repr}",
                        )
                        return value
                    except BaseException as error:
                        total_time = time.perf_counter() - start_time
                        time_repr = self._format_time(total_time)
                        self._client.send(
                            message=f"{fn_repr} failed with {type(error).__name__} after {time_repr}",
                            exception=error,
                        )
                        raise error
            return wrapper
        return decorator


def monitor(*, server: ServerInfoRaw = None):
    return Decorator(server=server).monitor()
