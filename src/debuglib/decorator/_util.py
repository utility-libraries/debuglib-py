# -*- coding=utf-8 -*-
r"""

"""
from itertools import chain
from inspect import iscoroutinefunction, getmodule


def function_repr(fn, args, kwargs):
    fn_name = f"{getmodule(fn).__name__}.{fn.__qualname__}"
    args_repr = map(repr, args)
    kwargs_repr = (f'{key}={repr(val)}' for key, val in kwargs.items())
    fn_msg = f"{fn_name}({', '.join(chain(args_repr, kwargs_repr))})"
    if iscoroutinefunction(fn):
        return f"async {fn_msg}"
    return fn_msg


TIME_UNITS = {
    0.000000001: "ns",  # nanoseconds
    0.000001: "μs",  # microseconds
    0.001: "ms",  # milliseconds
    1: "s",  # seconds
    60: "m",  # minutes
    3600: "h",  # hours
    86400: "d",  # days
    # 604800: "wk",  # weeks
    2628000: "mo",  # months
}
TIME_UNITS_FACTORS = sorted(TIME_UNITS, reverse=True)  # biggest first
TIME_UNITS_COUNT = len(TIME_UNITS)


def format_delta(delta: float, precision: int = 3) -> str:
    r"""
    format time-delta measured with time.perf_counter()
    """
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


TIME_UNITS_NS = {
    1: "ns",  # nanoseconds
    1000: "μs",  # microseconds
    1000000: "ms",  # milliseconds
    1000000000: "s",  # seconds
    60000000000: "m",  # minutes
    3600000000000: "h",  # hours
    86400000000000: "d",  # days
    # 604800000000000: "wk",  # weeks
    2628000000000000: "mo",  # months
}
TIME_UNITS_NS_FACTORS = sorted(TIME_UNITS_NS, reverse=True)  # biggest first
TIME_UNITS_NS_COUNT = len(TIME_UNITS_NS)


def format_delta_ns(delta: int, precision: int = 3) -> str:
    r"""
    format time-delta measured with time.perf_counter_ns()
    """
    start = next((index for index, factor in enumerate(TIME_UNITS_NS_FACTORS) if delta >= factor), None)
    if start is None:
        return f"{delta}s"  # in case of delta <= 0
    parts = []
    rest = delta
    for index in range(start, min(start + precision, TIME_UNITS_NS_COUNT)):
        factor = TIME_UNITS_NS_FACTORS[index]
        count, rest = divmod(rest, factor)
        if count:
            parts.append(f"{count}{TIME_UNITS_NS[factor]}")
        if not rest:
            break
    return '+'.join(parts)
