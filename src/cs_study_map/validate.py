"""Validate public metadata and reject accidental upstream assets or secrets."""

import json
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote

from .pipeline import context_key
from .privacy import private_reference
from .render import effective_result
from .storage import StudyError, digest, git_blob_sha, read_json, read_jsonl, safe_relative


def validate(project, tracked=False):
    root = project["root"]
    records = read_jsonl(root / "catalog/files.jsonl")
    state = read_json(root / "catalog/state.json")
    subjects = project["taxonomy"]["subjects"]
    if not records or len(records) != state["files"]:
        raise StudyError("Inventory is missing or file count does not match state")
    if state["repository"] != project["source"]["repository"] or not re.fullmatch(r"[0-9a-f]{40}", state["commit"]):
        raise StudyError("Invalid source repository or commit")
    ids = set()
    paths = set()
    checks = 0
    for r in records:
        safe_relative(r["path"])
        if r["path"] in paths or r["id"] in ids or r["id"] != digest(r["path"])[:20]:
            raise StudyError("Duplicate or inconsistent inventory identity")
        paths.add(r["path"])
        ids.add(r["id"])
        if r["subject"] not in subjects or not re.fullmatch(r"[0-9a-f]{40}", r["blob_sha"]):
            raise StudyError("Invalid subject or content identity")
        path = root / "catalog/analyses" / (r["id"] + ".json")
        if not path.exists():
            continue
        a = read_json(path)
        expected = {"schema_version", "context_key", "source_repository", "source_commit", "path", "blob_sha", "model", "prompt_version", "extractor_version", "coverage", "review_status", "evidence", "result"}
        if set(a) != expected or a["path"] != r["path"] or a["source_repository"] != state["repository"]:
            raise StudyError("Invalid public analysis fields or source identity")
        if not re.fullmatch(r"[0-9a-f]{40}", a["source_commit"]):
            raise StudyError("Analysis source commit is invalid")
        if any(set(e) != {"id", "locator"} for e in a["evidence"]):
            raise StudyError("Evidence may contain only pointers, never source text")
        if a.get("context_key") != context_key(project, r):
            continue  # Stale results still undergo metadata checks, but are never rendered.
        if a["blob_sha"] != r["blob_sha"]:
            raise StudyError("Current analysis has mismatched source content")
        effective_result(project, r, a)
        checks += 1
    from .textbook import validate_document
    chapters = list((root / "catalog/chapters").glob("*.json"))
    for path in chapters:
        document = validate_document(read_json(path))
        if document["chapter_id"] != path.stem:
            raise StudyError("Chapter identifier does not match its filename")
    manifests = read_json(root / "docs/generated-manifest.json") + read_json(root / "docs/textbook-manifest.json", [])
    # Keep maintained reading guides under the same link checks as generated pages.
    manual_pages = ["docs/usage.md", "docs/learning-log-template.md", "docs/study-guide.md", "docs/unit-01-review.md"]
    manifests += [name for name in manual_pages if (root / name).is_file()]
    for relative in manifests:
        safe_relative(relative)
        if not relative.startswith("docs/"):
            raise StudyError("Generated page is outside docs")
        path = root / relative
        if not path.is_file():
            raise StudyError("Generated page is missing")
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^\s)]+)\)", text):
            if target.startswith(("https://", "#")):
                continue
            destination = (path.parent / unquote(target.split("#")[0])).resolve()
            if not destination.is_relative_to(root) or not destination.is_file():
                raise StudyError(f"Broken local documentation link in {relative}")
    if tracked:
        audit_tracked(root)
    return {"files": len(records), "current_analyses": checks, "chapters": len(chapters), "tracked_audit": tracked}


def audit_tracked(root):
    proc = subprocess.run(["git", "ls-files", "-z"], cwd=root, capture_output=True, check=True)
    files = [p.decode("utf-8") for p in proc.stdout.split(b"\0") if p]
    allowed_extensions = {".md", ".py", ".json", ".jsonl", ".toml", ".yml", ".yaml", ".txt"}
    allowed_names = {"LICENSE", ".gitignore", ".gitattributes", ".env.example"}
    secret_pattern = re.compile(r"(?:ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|sk-[A-Za-z0-9_-]{24,}|-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----)")
    upstream_blobs = {r["blob_sha"] for r in read_jsonl(root / "catalog/files.jsonl")}
    for relative in files:
        path = Path(relative)
        if path.parts[0] in {".cache", ".local", ".venv", "materials", "upstream"} or path.name == ".env":
            raise StudyError("Private or source-material directory is tracked")
        if path.suffix.lower() not in allowed_extensions and path.name not in allowed_names:
            raise StudyError("Unexpected tracked file type; publish audit stopped")
        data = (root / relative).read_bytes()
        if len(data) >= 64 and git_blob_sha(data) in upstream_blobs:
            raise StudyError("A tracked file duplicates upstream source content")
        text = data.decode("utf-8")
        if secret_pattern.search(text):
            raise StudyError("Potential credential found; publish audit stopped")
        if relative.startswith(("catalog/", "docs/", "config/")):
            if private_reference(text):
                raise StudyError("Contact address or local filesystem path found in public data")
            if re.search(r"(?i)(?:[A-Z]:[\\/](?:Users|CodeX|Finder|Academy_of_Sciences)|Bearer\s+[A-Za-z0-9_-]{20,})", text):
                raise StudyError("Machine-specific path or credential found in public data")
        if relative.startswith("catalog/analyses/"):
            value = json.loads(text)
            if any(key in value for key in ("text", "segments", "messages", "untrusted_segments", "raw")):
                raise StudyError("Extracted source content must not be published")
    return len(files)
