"""Inventory-only synchronization. No upstream content enters the public catalog."""

from pathlib import PurePosixPath

from .storage import StudyError, digest, read_json, read_jsonl, safe_relative, write_json, write_jsonl

TEXT_SUFFIXES = {".md", ".txt", ".rst", ".py", ".c", ".cpp", ".cc", ".h", ".hpp", ".java", ".v", ".vhd", ".sql", ".m", ".tex", ".html", ".htm"}
DOCUMENT_SUFFIXES = {".pdf", ".docx", ".pptx", ".ipynb"}
SKIP_PARTS = {".git", "node_modules", "__pycache__", "incremental_db", "db", "debug", "release", ".idea", ".vs"}
SKIP_SUFFIXES = {".class", ".exe", ".dll", ".o", ".obj", ".pyc", ".pdb", ".meta", ".aux", ".log", ".toc"}


def material_status(path, mode, size, limit):
    p = PurePosixPath(path)
    if mode == "120000":
        return "excluded", "symbolic-link"
    if any(part.lower() in SKIP_PARTS for part in p.parts) or p.suffix.lower() in SKIP_SUFFIXES:
        return "excluded", "build-or-generated-file"
    if size > limit:
        return "unsupported", "download-size-limit"
    if p.suffix.lower() in TEXT_SUFFIXES | DOCUMENT_SUFFIXES or p.name.lower() in {"readme", "makefile"}:
        return "pending", None
    return "unsupported", "format-not-supported"


def course_for(path, courses):
    matched = [c for c in courses if path == c["source_path"] or path.startswith(c["source_path"] + "/")]
    if matched:
        return max(matched, key=lambda c: len(c["source_path"]))
    parts = PurePosixPath(path).parts
    if len(parts) >= 3 and (parts[0].startswith("大") or parts[0] == "研究生"):
        prefix = "/".join(parts[:2])
        return {"id": "auto-" + digest(prefix)[:12], "title": parts[1], "source_path": prefix, "subject": "unclassified"}
    return {"id": "repository-notes", "title": "仓库说明与其他资料", "source_path": "", "subject": "unclassified"}


def make_records(entries, project):
    records = []
    seen = set()
    for item in entries:
        if item["type"] != "blob":
            continue
        path = safe_relative(item["path"])
        if path in seen:
            raise StudyError("Duplicate path in upstream inventory")
        seen.add(path)
        course = course_for(path, project["courses"])
        status, reason = material_status(path, item["mode"], item.get("size", 0), project["source"]["max_download_bytes"])
        records.append({
            "id": digest(path)[:20], "path": path, "blob_sha": item["sha"],
            "size": item.get("size", 0), "course_id": course["id"], "course_title": course["title"],
            "subject": course["subject"], "status": status, "reason": reason,
        })
    if not records:
        raise StudyError("Empty upstream inventory; refusing to replace existing index")
    return sorted(records, key=lambda r: r["path"])


def changes_between(previous, current):
    old = {r["path"]: r for r in previous}
    new = {r["path"]: r for r in current}
    added = sorted(new.keys() - old.keys())
    removed = sorted(old.keys() - new.keys())
    modified = sorted(p for p in old.keys() & new.keys() if old[p]["blob_sha"] != new[p]["blob_sha"])
    # Only label unambiguous identical-content moves; duplicate copies remain add/remove.
    moves = []
    for p in list(removed):
        candidates = [q for q in added if new[q]["blob_sha"] == old[p]["blob_sha"]]
        sources = [q for q in removed if old[q]["blob_sha"] == old[p]["blob_sha"]]
        if len(candidates) == len(sources) == 1:
            q = candidates[0]
            moves.append({"from": p, "to": q})
            added.remove(q)
            removed.remove(p)
    return {"added": added, "modified": modified, "removed": removed, "moved": moves}


def synchronize(project, github):
    root = project["root"]
    state = read_json(root / "catalog/state.json", {})
    previous = read_jsonl(root / "catalog/files.jsonl")
    commit, tree = github.head(project["source"]["branch"])
    config_key = digest({"courses": project["courses"], "source": project["source"], "taxonomy": project["taxonomy"], "sync_version": 1})
    if state.get("commit") == commit and state.get("config_key") == config_key and previous:
        return {"changed": False, "commit": commit, "files": len(previous)}
    records = make_records(github.tree(tree), project)
    changes = changes_between(previous, records)
    # The complete tree is fetched and validated before any public writes.
    write_jsonl(root / "catalog/files.jsonl", records)
    write_json(root / "catalog/changes.json", {"from_commit": state.get("commit"), "to_commit": commit, **changes})
    write_json(root / "catalog/state.json", {
        "schema_version": 1, "repository": project["source"]["repository"],
        "branch": project["source"]["branch"], "commit": commit, "tree": tree,
        "config_key": config_key, "files": len(records),
    })
    return {"changed": True, "commit": commit, "files": len(records), "changes": {k: len(v) for k, v in changes.items()}}
