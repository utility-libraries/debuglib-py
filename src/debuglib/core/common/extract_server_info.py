# -*- coding=utf-8 -*-
r"""

"""
from ...typing import ServerInfo, ServerInfoRaw
from ...defaults import DEFAULT_SERVER_HOST, DEFAULT_SERVER_PORT


def extract_server_info(info: ServerInfoRaw) -> ServerInfo:
    if info is None:  # take default
        return DEFAULT_SERVER_HOST, DEFAULT_SERVER_PORT
    elif isinstance(info, str):  # host specified
        return info, DEFAULT_SERVER_PORT
    elif isinstance(info, int):  # port specified
        return DEFAULT_SERVER_HOST, info
    elif (isinstance(info, tuple) and len(info) == 2
          and isinstance(info[0], str) and isinstance(info[1], int)):  # properly specified
        return info
    else:
        raise ValueError(f"unknown server specification: {info!r}")
