# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
#
"""
Ports related utility functions.
"""
import contextlib
import logging
from typing import Set

import pytest

from pytestskipmarkers.utils import socket

log = logging.getLogger(__name__)


def get_unused_localhost_port(use_cache: bool = False) -> int:
    """
    Return a random unused port on localhost.

    :keyword bool use_cache:
        If ``use_cache`` is ``True``, consecutive calls to this function will never return the cached port.
    """
    if not isinstance(use_cache, bool):
        raise pytest.UsageError(
            f"The value of 'use_cache' needs to be an boolean, not {type(use_cache)}"
        )

    with contextlib.closing(socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)) as usock:
        usock.bind(("127.0.0.1", 0))
        port: int = usock.getsockname()[1]

    if use_cache:
        try:
            cached_ports = get_unused_localhost_port.__cached_ports__  # type: ignore[attr-defined]
        except AttributeError:
            cached_ports = get_unused_localhost_port.__cached_ports__ = set()  # type: ignore[attr-defined]
        if port in cached_ports:
            return get_unused_localhost_port(use_cache=use_cache)
        cached_ports.add(port)

    return port


def get_connectable_ports(ports: Set[int]) -> Set[int]:
    """
    Returns a set of the ports where connection was successful.

    :param ~collections.abc.Iterable ports: An iterable of ports to try and connect to
    :rtype: set
    :return: Returns a set of the ports where connection was successful
    """
    connectable_ports = set()
    ports = set(ports)

    for port in set(ports):
        with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            conn = sock.connect_ex(("localhost", port))
            try:
                if conn == 0:
                    log.debug("Port %s is connectable!", port)
                    connectable_ports.add(port)
                    sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                continue
    return connectable_ports
