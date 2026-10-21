"""Deterministic public files and private, ignored cache storage."""

import hashlib
import json
import os
import tempfile
from pathlib import Path, PurePosixPath


class StudyError(Exception):
    """An actionable error whose message is safe to show in public logs."""


def read_json(path, default=None):
    path = Path(path)
    if not path.exists() and default is not None:
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_write(path, text):
    path = Path(path)
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".write-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return True


def write_json(path, value):
    return atomic_write(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def read_jsonl(path):
    if not Path(path).exists():
        return []
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line]


def write_jsonl(path, values):
    return atomic_write(path, "".join(json.dumps(v, ensure_ascii=False, sort_keys=True) + "\n" for v in values))


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def git_blob_sha(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def safe_relative(value):
    p = PurePosixPath(value)
    if not value or p.is_absolute() or ".." in p.parts or "\\" in value or ":" in value or "\x00" in value:
        raise StudyError("Invalid repository-relative path")
    return value


def load_project(root):
    root = Path(root).resolve()
    return {
        "root": root,
        "source": read_json(root / "config/source.json"),
        "taxonomy": read_json(root / "config/taxonomy.json"),
        "courses": read_json(root / "config/courses.json"),
        "overrides": read_json(root / "config/overrides.json", {"files": {}}),
    }
