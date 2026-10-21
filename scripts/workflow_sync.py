"""Emit an honest Actions summary without credentials or source text."""

import os
from pathlib import Path

from cs_study_map.ai import create_client
from cs_study_map.github import GitHub
from cs_study_map.pipeline import analyze
from cs_study_map.render import build
from cs_study_map.storage import StudyError, load_project
from cs_study_map.sync import synchronize
from cs_study_map.textbook import write_chapters
from cs_study_map.validate import validate


def main():
    project = load_project(Path.cwd())
    raw_limit = os.getenv("RUN_LIMIT", "6")
    try:
        limit = int(raw_limit)
    except ValueError:
        raise StudyError("RUN_LIMIT must be an integer") from None
    if not 0 <= limit <= 100:
        raise StudyError("RUN_LIMIT must be between 0 and 100")
    require_ai = os.getenv("REQUIRE_AI", "false").lower() == "true"
    github = GitHub(project["source"]["repository"], os.getenv("GITHUB_TOKEN"))
    synced = synchronize(project, github)
    client = create_client(project["root"])
    results = analyze(project, github, client, limit=limit, require_ai=require_ai)
    book_limit = int(os.getenv("RUN_BOOK_LIMIT", "1"))
    chapters = write_chapters(project, client, limit=book_limit, require_ai=require_ai)
    pages = build(project)
    validate(project)
    lines = ["## Study map synchronization", "",
             f"- Upstream commit: `{synced['commit']}`", f"- Indexed files: {synced['files']}",
             f"- AI state: `{results['status']}`", f"- Newly analyzed: {results['completed']}",
             f"- Failed attempts: {results['failed']}", f"- Current valid guides: {pages['analyzed']}",
             f"- Still pending: {pages['pending']}", ""]
    lines += [f"- Newly written chapters: {chapters['completed']}", f"- Chapter failures: {chapters['failed']}", ""]
    if not client.configured:
        lines += ["AI is not configured. Metadata synchronization is active; automatic cloud AI analysis is not active.",
                  "Configure CS_STUDY_API_BASE and CS_STUDY_MODEL as repository variables and CS_STUDY_API_KEY as a secret.", ""]
        print("::warning::AI is not configured; only metadata synchronization and existing guide generation ran.")
    if results["failed"]:
        print("::warning::Some materials remain pending after analysis failures; see coverage state.")
    summary = "\n".join(lines)
    print(summary)
    if os.getenv("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as handle:
            handle.write(summary)
    return 2 if require_ai and (results["failed"] or chapters["failed"]) else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except StudyError as exc:
        print(f"::error::{exc}")
        raise SystemExit(1)
