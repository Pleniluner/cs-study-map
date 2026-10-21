"""Incremental analysis with resumable per-file results and explicit coverage."""

import json
from collections import defaultdict, deque
from pathlib import Path, PurePosixPath

from .ai import PROMPT_VERSION, SYSTEM_PROMPT, validate_result
from .extract import EXTRACTOR_VERSION, extract
from .storage import StudyError, digest, git_blob_sha, read_json, read_jsonl, write_json


def context_key(project, record):
    return digest({
        "blob": record["blob_sha"], "path": record["path"], "course": record["course_id"],
        "subject": record["subject"], "taxonomy": project["taxonomy"],
        "prompt": SYSTEM_PROMPT, "prompt_version": PROMPT_VERSION, "extractor_version": EXTRACTOR_VERSION,
        "max_chars": project["source"]["max_extract_chars"], "max_pages": project["source"]["max_pdf_pages"],
    })


def current_analysis(project, record):
    result = read_json(project["root"] / "catalog/analyses" / (record["id"] + ".json"), {})
    if result.get("context_key") == context_key(project, record):
        return result
    return None


def load_extraction(project, record, state, github, source_dir=None):
    root = project["root"]
    key = digest({"blob": record["blob_sha"], "extension": PurePosixPath(record["path"]).suffix.lower(), "version": EXTRACTOR_VERSION, "chars": project["source"]["max_extract_chars"], "pages": project["source"]["max_pdf_pages"]})
    extracted = root / ".cache/extracted" / (key + ".json")
    if extracted.exists():
        return read_json(extracted)
    blob = root / ".cache/blobs" / record["blob_sha"]
    data = None
    if blob.exists():
        data = blob.read_bytes()
        if git_blob_sha(data) != record["blob_sha"]:
            raise StudyError("Cached blob checksum mismatch")
    if data is None and source_dir:
        base = Path(source_dir).resolve()
        local = (base / record["path"]).resolve()
        if local.is_relative_to(base) and local.is_file() and local.stat().st_size <= project["source"]["max_download_bytes"]:
            candidate = local.read_bytes()
            if git_blob_sha(candidate) == record["blob_sha"]:
                data = candidate
    if data is None:
        data = github.download(state["commit"], record, project["source"]["max_download_bytes"])
    blob.parent.mkdir(parents=True, exist_ok=True)
    if not blob.exists():
        blob.write_bytes(data)
    result = extract(record["path"], data, project["source"]["max_extract_chars"], project["source"]["max_pdf_pages"])
    write_json(extracted, result)
    return result


def rank(record):
    path = PurePosixPath(record["path"])
    name = path.name.lower()
    if name.startswith("readme"):
        weight = 0
    elif any(word in name for word in ("实验", "lab", "作业", "要求", "说明", "syllabus", "大纲")):
        weight = 1
    elif path.suffix.lower() in {".pdf", ".docx", ".pptx"}:
        weight = 2
    elif path.suffix.lower() in {".md", ".txt"}:
        weight = 3
    else:
        weight = 4
    return weight, len(path.parts), record["path"]


def candidate_queue(project, records, courses=None, paths=None):
    groups = defaultdict(list)
    for r in records:
        if r["status"] != "pending" or current_analysis(project, r):
            continue
        if courses and not any(c == r["course_id"] or c in r["course_title"] for c in courses):
            continue
        if paths and r["path"] not in paths:
            continue
        groups[r["course_id"]].append(r)
    queues = [deque(sorted(groups[c], key=rank)) for c in sorted(groups)]
    while queues:
        for q in list(queues):
            yield q.popleft()
            if not q:
                queues.remove(q)


def analyze(project, github, client, limit=6, courses=None, paths=None, source_dir=None, require_ai=False):
    if not 0 <= limit <= 100:
        raise StudyError("Analysis limit must be between 0 and 100")
    if not client.configured:
        if require_ai:
            raise StudyError("AI configuration is missing; configure endpoint/model and a provider key")
        return {"status": "not-configured", "attempted": 0, "completed": 0, "failed": 0}
    root = project["root"]
    state = read_json(root / "catalog/state.json")
    records = read_jsonl(root / "catalog/files.jsonl")
    failures = read_json(root / "catalog/analysis-failures.json", {})
    live_ids = {r["id"] for r in records}
    failures = {k: v for k, v in failures.items() if k in live_ids}
    attempted = completed = failed = 0
    for record in candidate_queue(project, records, courses, paths):
        if attempted >= limit:
            break
        attempted += 1
        try:
            extraction = load_extraction(project, record, state, github, source_dir)
            context = {
                "path": record["path"], "course_hint": record["course_title"],
                "allowed_subjects": project["taxonomy"]["subjects"],
                "allowed_resource_types": project["taxonomy"]["resource_types"],
                "coverage": extraction["coverage"], "untrusted_segments": extraction["segments"],
            }
            result = validate_result(client.analyze(context), extraction, project["taxonomy"])
            evidence_ids = {identifier for topic in result["topics"] for identifier in topic["evidence_ids"]}
            # Only pointers are public; text sent to the model is never serialized here.
            public = {
                "schema_version": 1, "context_key": context_key(project, record),
                "source_repository": state["repository"], "source_commit": state["commit"],
                "path": record["path"], "blob_sha": record["blob_sha"],
                "model": client.model, "prompt_version": PROMPT_VERSION,
                "extractor_version": EXTRACTOR_VERSION, "coverage": extraction["coverage"],
                "review_status": "ai-unreviewed",
                "evidence": [{"id": s["id"], "locator": s["locator"]} for s in extraction["segments"] if s["id"] in evidence_ids],
                "result": result,
            }
            write_json(root / "catalog/analyses" / (record["id"] + ".json"), public)
            failures.pop(record["id"], None)
            completed += 1
            print(json.dumps({"analysis": "completed", "path": record["path"], "coverage": extraction["coverage"]}, ensure_ascii=False), flush=True)
        except StudyError as exc:
            # Messages come from controlled local errors; provider response bodies are suppressed.
            failures[record["id"]] = {"context_key": context_key(project, record), "reason": str(exc)}
            failed += 1
            print(json.dumps({"analysis": "failed", "path": record["path"], "reason": str(exc)}, ensure_ascii=False), flush=True)
            if str(exc).startswith(("AI provider", "AI endpoint")):
                break
    write_json(root / "catalog/analysis-failures.json", failures)
    return {"status": "completed" if not failed else "partial", "attempted": attempted, "completed": completed, "failed": failed}
