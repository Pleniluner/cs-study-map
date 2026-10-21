"""Reject contact addresses and machine paths in public source inventories."""

import re
from urllib.parse import unquote

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
LOCAL_PATH = re.compile(r"(?i)(?<![A-Za-z0-9])(?:[a-z]:[\\/]|/Users/|/home/|file:///|\\\\[A-Za-z0-9_-]+\\)")


def private_reference(value):
    decoded = unquote(value)
    return bool(EMAIL.search(decoded) or LOCAL_PATH.search(decoded))
