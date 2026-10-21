"""Check Git snapshots and metadata without echoing rejected private values."""

import json
import re
import shlex
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote


EMAIL = re.compile(r"[\w.%+\[\]-]+@[\w.-]+\.[A-Za-z]{2,}")
NOREPLY = re.compile(r"[\w+\[\]-]+@users\.noreply\.github\.com\Z")
LOCAL = re.compile(r"(?i)(?<![\w])(?:[a-z]:[\\/]|file:/" r"//[\w%]|/Users/[\w.-]+/|/home/[\w.-]+/|\\\\[\w.-]+\\[\w.-]+)")
# Reserved documentation domains cannot be personal contact addresses.
EXAMPLE_DOMAINS = {'example.com', 'example.org', 'example.net', 'example.test'}


def git(*args):
    return subprocess.check_output(['git', *args], stderr=subprocess.DEVNULL)


def check(data, *, json_document=False):
    values = [data.decode('utf-8')]
    if json_document:
        try:
            # Keep every key/value pair, even when a JSON key occurs twice.
            values = [json.loads(values[0], object_pairs_hook=list)]
        except ValueError:
            pass
    while values:
        item = values.pop()
        if isinstance(item, (list, tuple)):
            values.extend(item)
        elif isinstance(item, str):
            text = unquote(item)
            if LOCAL.search(text) or any(not NOREPLY.fullmatch(m.group()) and
                                         m.group().split('@')[1].lower() not in EXAMPLE_DOMAINS
                                         for m in EMAIL.finditer(text)):
                raise ValueError('Personal email or absolute local path detected; private value omitted.')


def identity(value):
    match = re.search(rb'<([^<>]+)>', value)
    if not match or not NOREPLY.fullmatch(match[1].decode('utf-8')):
        raise ValueError('Author and committer must use a GitHub noreply address.')
    check(value)


def snapshot(tree=None, seen=None):
    entries = git('ls-tree', '-rz', tree) if tree else git('ls-files', '--stage', '-z')
    if seen is None:
        seen = set()
    for entry in entries.split(b'\0'):
        if not entry:
            continue
        metadata, name = entry.split(b'\t', 1)
        fields = metadata.split()
        mode, oid = (fields[0], fields[2]) if tree else fields[:2]
        check(name)
        if mode == b'160000':
            raise ValueError('Submodule content cannot be privacy-audited.')
        json_document = name.lower().endswith(b'.json')
        scan_key = (oid, json_document)
        if scan_key not in seen:
            check(git('cat-file', 'blob', oid.decode()), json_document=json_document)
            seen.add(scan_key)


def history(revision):
    seen = set()
    for commit in git('rev-list', revision).decode().splitlines():
        author, committer, message = git('show', '-s', '--format=%an <%ae>%x00%cn <%ce>%x00%B', commit).split(b'\0', 2)
        identity(author)
        identity(committer)
        check(message)
        snapshot(commit, seen)


def install():
    # Executable paths stay in ignored, machine-local hooks, never in Git.
    root = Path(git('rev-parse', '--show-toplevel').decode().strip())
    hooks = root / '.local' / 'git-hooks'
    hooks.mkdir(parents=True, exist_ok=True)
    for hook, mode in [('pre-commit', 'index'), ('commit-msg', 'message'), ('pre-push', 'push')]:
        path = hooks / hook
        path.write_text('#!/bin/sh\nexec ' + shlex.quote(Path(sys.executable).as_posix()) +
                        ' scripts/privacy_guard.py ' + mode + ' "$@"\n', encoding='utf-8', newline='\n')
        path.chmod(0o755)
    subprocess.run(['git', 'config', '--local', 'core.hooksPath', '.local/git-hooks'], check=True)
    subprocess.run(['git', 'config', '--local', 'user.useConfigOnly', 'true'], check=True)
    print('Privacy hooks installed for this checkout.')


def main():
    mode = sys.argv[1]
    if mode == 'install':
        install()
    elif mode == 'index':
        identity(git('var', 'GIT_AUTHOR_IDENT'))
        identity(git('var', 'GIT_COMMITTER_IDENT'))
        snapshot()
    elif mode == 'message':
        check(Path(sys.argv[2]).read_bytes())
    elif mode == 'history':
        history(sys.argv[2] if len(sys.argv) > 2 else 'HEAD')
    elif mode == 'push':
        for line in sys.stdin:
            _, local_oid, _, _ = line.split()
            if set(local_oid) != {'0'}:
                history(local_oid)
    else:
        raise ValueError('Unknown privacy check mode.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, UnicodeError, subprocess.CalledProcessError):
        print('Privacy check blocked this operation. Check identity, message, filenames and text for personal emails or local paths. Details omitted to avoid disclosure.', file=sys.stderr)
        sys.exit(1)
