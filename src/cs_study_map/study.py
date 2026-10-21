"""Offline, private learning progress tied to the chapter actually studied."""

from datetime import datetime, timezone
import re
import subprocess

from .storage import StudyError, digest, read_json, write_json
from .textbook import chapter_status, curriculum, validate_document

PROGRESS_FILE = ".local/study-progress.json"
STATUSES = ("not-started", "reading", "review", "completed")
STATUS_LABELS = dict(zip(STATUSES, ("未开始", "学习中", "待复习", "已完成自测")))


def progress_path(project):
    root = project["root"]
    path = root / PROGRESS_FILE
    if path.resolve() != path:
        raise StudyError("Learning progress must stay inside the project's private .local directory")
    return path


def load_progress(path):
    try:
        value = read_json(path, {"schema_version": 1, "chapters": {}})
        if not isinstance(value, dict) or set(value) != {"schema_version", "chapters"}:
            raise ValueError
        if value["schema_version"] != 1 or not isinstance(value["chapters"], dict):
            raise ValueError
        for chapter_id, record in value["chapters"].items():
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", chapter_id):
                raise ValueError
            if not isinstance(record, dict) or set(record) != {"status", "document_digest", "updated_at", "notes"}:
                raise ValueError
            if record["status"] not in STATUSES or not isinstance(record["updated_at"], str):
                raise ValueError
            fingerprint = record["document_digest"]
            if fingerprint is not None and (not isinstance(fingerprint, str) or not re.fullmatch(r"[0-9a-f]{64}", fingerprint)):
                raise ValueError
            if record["status"] != "not-started" and fingerprint is None:
                raise ValueError
            if not isinstance(record["notes"], list):
                raise ValueError
            for note in record["notes"]:
                if not isinstance(note, dict) or set(note) != {"at", "text"}:
                    raise ValueError
                if not isinstance(note["at"], str) or not isinstance(note["text"], str) or not 1 <= len(note["text"].strip()) <= 2000:
                    raise ValueError
        return value
    except (ValueError, TypeError, UnicodeError):
        raise StudyError("Local study progress is invalid; repair or back up .local/study-progress.json before updating it") from None


def study(project, chapter_id=None, status=None, note=None):
    """Report progress, or save a learner's explicit status/note without any AI call."""
    if status is not None and status not in STATUSES:
        raise StudyError("Unknown learning status")
    if (status is not None or note is not None) and not chapter_id:
        raise StudyError("Choose --chapter before recording a status or note")
    if note is not None and (not isinstance(note, str) or not 1 <= len(note.strip()) <= 2000):
        raise StudyError("A learning note must contain 1 to 2000 characters")
    plan = curriculum(project)
    if chapter_id and chapter_id not in {c["id"] for c in plan["chapters"]}:
        raise StudyError("Requested chapter does not exist in the curriculum")
    path = progress_path(project)
    progress = load_progress(path)
    documents = {}
    availability = {}
    for chapter in plan["chapters"]:
        identifier = chapter["id"]
        document = read_json(project["root"] / "catalog/chapters" / (identifier + ".json"), {})
        if document:
            validate_document(document)
            if document["chapter_id"] != identifier:
                raise StudyError("Chapter identifier does not match its filename")
        documents[identifier] = document
        availability[identifier] = chapter_status(project, plan, chapter, document)

    if status is not None or note is not None:
        document = documents[chapter_id]
        if not document:
            raise StudyError("This chapter has not been written yet; learning progress was not changed")
        if status == "completed" and availability[chapter_id] != "current":
            raise StudyError("This chapter awaits source or curriculum review; it cannot be marked completed")
        # Git also refuses tracked files here, even if an ignore rule was later added.
        if (project["root"] / ".git").exists():
            result = subprocess.run(["git", "check-ignore", "-q", "--", PROGRESS_FILE], cwd=project["root"], capture_output=True)
            if result.returncode != 0:
                raise StudyError("Git must ignore .local/study-progress.json before saving personal progress")
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        record = progress["chapters"].setdefault(chapter_id, {
            "status": "not-started", "document_digest": None, "updated_at": now, "notes": [],
        })
        if status is not None:
            record["status"] = status
            record["document_digest"] = None if status == "not-started" else digest(document)
        if note is not None:
            record["notes"].append({"at": now, "text": note.strip()})
        record["updated_at"] = now
        write_json(path, progress)

    rows = []
    for chapter in plan["chapters"]:
        identifier = chapter["id"]
        document = documents[identifier]
        record = progress["chapters"].get(identifier, {})
        recorded = record.get("status", "not-started")
        changed = bool(record.get("document_digest") and record["document_digest"] != digest(document))
        effective = "review" if recorded == "completed" and (changed or availability[identifier] != "current") else recorded
        row = {
            "id": identifier, "title": chapter["title"],
            "page": f"docs/textbook/{identifier}.md" if document else None,
            "availability": availability[identifier], "status": effective,
            "status_label": STATUS_LABELS[effective], "recorded_status": recorded,
            "chapter_changed": changed, "note_count": len(record.get("notes", [])),
        }
        if chapter_id == identifier and document:
            row["self_checks"] = document["content"]["self_checks"]
        rows.append(row)
    next_chapter = next((row["id"] for row in rows if row["status"] != "completed"), None)
    return {
        "storage": PROGRESS_FILE, "completed": sum(row["status"] == "completed" for row in rows),
        "total": len(rows), "next_chapter": next_chapter,
        "chapters": [row for row in rows if not chapter_id or row["id"] == chapter_id],
        "archived_records": len(set(progress["chapters"]) - {c["id"] for c in plan["chapters"]}),
    }
