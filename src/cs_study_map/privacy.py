"""Reject contact addresses and machine paths in public source inventories."""

import json
import re
from urllib.parse import unquote

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
LOCAL_PATH = re.compile(r"(?i)(?<![A-Za-z0-9])(?:[a-z]:[\\/]|/Users/|/home/|file:///|\\\\[A-Za-z0-9_-]+\\)")


def private_reference(value, *, json_document=False):
    values = [value]
    if json_document:
        try:
            # Scan decoded strings, including keys and duplicate-key values.
            # A code line ending in n: followed by a JSON newline is not a drive.
            values = [json.loads(value, object_pairs_hook=list)]
        except ValueError:
            pass  # Malformed JSON still receives the ordinary text scan.
    while values:
        item = values.pop()
        if isinstance(item, (list, tuple)):
            values.extend(item)
        elif isinstance(item, str):
            decoded = unquote(item)
            if EMAIL.search(decoded) or LOCAL_PATH.search(decoded):
                return True
    return False
