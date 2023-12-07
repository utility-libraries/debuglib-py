# -*- coding=utf-8 -*-
r"""

"""
from ..._typing import DEFAULT_VALUE, ServerInfo, ServerInfoRaw
from ...defaults import DEFAULT_SERVER_HOST, DEFAULT_SERVER_PORT


def extract_server_info(info: ServerInfoRaw) -> ServerInfo:
    r"""
    allowed formats
    - None|DEFAULT_VALUE
    - host
    - port
    - (host|None, port|None)
    """
    if info is None or info is DEFAULT_VALUE:  # take default
        return DEFAULT_SERVER_HOST, DEFAULT_SERVER_PORT
    elif isinstance(info, str):  # host specified
        return info, DEFAULT_SERVER_PORT
    elif isinstance(info, int):  # port specified
        return DEFAULT_SERVER_HOST, info
    elif isinstance(info, tuple) and len(info) == 2:
        host, port = info
        return host or DEFAULT_SERVER_HOST, port or DEFAULT_SERVER_PORT
    else:
        raise ValueError(f"unknown server specification: {info!r}")
