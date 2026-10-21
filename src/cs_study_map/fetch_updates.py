"""Fetch only unseen/changed content into ignored local caches, with checksums."""

import hashlib
import os
import shutil
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path, PurePosixPath

from .storage import StudyError, git_blob_sha, read_json, read_jsonl, write_json


def file_blob_sha(path):
    size = path.stat().st_size
    h = hashlib.sha1(b"blob " + str(size).encode() + b"\0")
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def plan_updates(project, baseline):
    baseline = Path(baseline).resolve()
    if not baseline.is_dir():
        raise StudyError("Baseline directory does not exist")
    by_path = {}
    by_blob = {}
    for directory, dirs, names in os.walk(baseline, followlinks=False):
        dirs[:] = [d for d in dirs if d not in {".git", ".cache", ".venv"} and not (Path(directory) / d).is_symlink()]
        for name in names:
            path = Path(directory) / name
            if path.is_symlink():
                continue
            sha = file_blob_sha(path)
            relative = path.relative_to(baseline).as_posix()
            by_path[relative] = sha
            by_blob.setdefault(sha, relative)
    records = read_jsonl(project["root"] / "catalog/files.jsonl")
    state = read_json(project["root"] / "catalog/state.json")
    files = []
    unchanged = moved = 0
    for r in records:
        if by_path.get(r["path"]) == r["blob_sha"]:
            unchanged += 1
            continue
        if r["blob_sha"] in by_blob:
            moved += 1
            continue
        files.append({**r, "change": "modified" if r["path"] in by_path else "added", "download_status": "pending"})
    return {
        "source_repository": state["repository"], "commit": state["commit"],
        "baseline_kind": "local-snapshot-content-comparison", "baseline_directory": str(baseline),
        "unchanged": unchanged, "same_content_elsewhere": moved, "files": files,
    }


def fetch_updates(project, github, baseline, workers=4, plan_only=False):
    if not 1 <= workers <= 8:
        raise StudyError("Download workers must be between 1 and 8")
    root = project["root"]
    state = read_json(root / "catalog/state.json")
    folder = (root / ".cache/updates" / state["commit"]).resolve()
    if not folder.is_relative_to(root):
        raise StudyError("Update cache must remain inside the project")
    folder.mkdir(parents=True, exist_ok=True)
    manifest_path = folder / "manifest.json"
    old = read_json(manifest_path, {})
    baseline_path = str(Path(baseline).resolve())
    if old.get("baseline_kind") == "local-snapshot-content-comparison" and old.get("baseline_directory") == baseline_path and old.get("commit") == state["commit"]:
        manifest = old
    else:
        manifest = plan_updates(project, baseline)
    manifest["download_complete"] = False
    write_json(manifest_path, manifest)
    summary = {"changed_files": len(manifest["files"]), "changes": dict(Counter(r["change"] for r in manifest["files"])), "same_content_elsewhere": manifest["same_content_elsewhere"], "total_bytes": sum(r["size"] for r in manifest["files"]), "manifest": str(manifest_path)}
    print(__import__("json").dumps({"update_plan": summary}, ensure_ascii=False), flush=True)
    if plan_only:
        return summary
    by_blob = {}
    for r in manifest["files"]:
        by_blob.setdefault(r["blob_sha"], []).append(r)
    blob_dir = root / ".cache/blobs"
    blob_dir.mkdir(parents=True, exist_ok=True)
    files_dir = folder / "files"
    files_dir.mkdir(parents=True, exist_ok=True)

    def fetch_group(group):
        representative = group[0]
        blob = blob_dir / representative["blob_sha"]
        if not blob.exists() or file_blob_sha(blob) != representative["blob_sha"]:
            data = github.download(state["commit"], representative, 100 * 1024 * 1024)
            if git_blob_sha(data) != representative["blob_sha"]:
                raise StudyError("Update content checksum mismatch")
            temporary = blob.with_suffix(".part")
            temporary.write_bytes(data)
            os.replace(temporary, blob)
        results = []
        for r in group:
            suffix = PurePosixPath(r["path"]).suffix
            suffix = suffix if suffix.isascii() and len(suffix) <= 12 and all(c.isalnum() or c == "." for c in suffix) else ".bin"
            target = files_dir / (r["id"] + suffix)
            if target.exists() and file_blob_sha(target) != r["blob_sha"]:
                target.unlink()  # A verified blob below will replace only this cache file.
            if not target.exists():
                try:
                    os.link(blob, target)
                except OSError:
                    shutil.copyfile(blob, target)
            if file_blob_sha(target) != r["blob_sha"]:
                raise StudyError("Materialized update checksum mismatch")
            results.append((r, str(target)))
        return results

    completed = failed = 0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        tasks = {pool.submit(fetch_group, group): group for group in by_blob.values()}
        for future in as_completed(tasks):
            group = tasks[future]
            try:
                for record, path in future.result():
                    record.update(download_status="verified", local_path=path)
                    record.pop("download_error", None)
                    completed += 1
            except (StudyError, OSError) as exc:
                for record in group:
                    record.update(download_status="failed", download_error=str(exc) if isinstance(exc, StudyError) else "local-file-error")
                    failed += 1
            if (completed + failed) % 50 < len(group):
                write_json(manifest_path, manifest)
                print(__import__("json").dumps({"downloaded_verified": completed, "failed": failed, "total": len(manifest["files"])}, ensure_ascii=False), flush=True)
    manifest["download_complete"] = failed == 0
    manifest["verified_count"] = completed
    manifest["failed_count"] = failed
    write_json(manifest_path, manifest)
    return {**summary, "verified": completed, "failed": failed, "download_complete": failed == 0}
