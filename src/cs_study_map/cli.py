"""Console interface for local use and scheduled GitHub Actions."""

import argparse
import json
import os
from pathlib import Path

from .ai import create_client
from .github import GitHub
from .fetch_updates import fetch_updates
from .pipeline import analyze
from .render import build
from .storage import StudyError, load_project
from .study import STATUSES, study
from .sync import synchronize
from .textbook import write_chapters
from .validate import validate


def main(argv=None):
    parser = argparse.ArgumentParser(description="同步资料，识别知识点，编写供个人自学的原创教材。")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Project root containing config/")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("sync", help="Synchronize upstream file metadata only")
    commands.add_parser("build", help="Generate GitHub Markdown navigation")
    learning = commands.add_parser("study", help="查看或记录本机学习进度，不调用模型或网络")
    learning.add_argument("--chapter", help="Chapter id from config/curriculum.json")
    learning.add_argument("--status", choices=STATUSES, help="个人自测状态：未开始、学习中、待复习、已完成")
    learning.add_argument("--note", help="追加一条本机学习笔记（最多 2000 字）")
    fetch = commands.add_parser("fetch-updates", help="Download new/modified content to ignored cache after comparing a local snapshot")
    fetch.add_argument("--baseline-dir", type=Path, required=True)
    fetch.add_argument("--workers", type=int, default=4)
    fetch.add_argument("--plan-only", action="store_true")
    check = commands.add_parser("validate", help="Validate index, guides and local links")
    check.add_argument("--tracked", action="store_true", help="Also audit Git-tracked files for assets/secrets")
    book = commands.add_parser("write", help="Write original textbook chapters from analyzed topic briefs")
    book.add_argument("--limit", type=int, default=1)
    book.add_argument("--chapter", action="append", help="Chapter id from config/curriculum.json; repeatable")
    book.add_argument("--require-ai", action="store_true")
    for name in ("analyze", "run"):
        p = commands.add_parser(name, help="Analyze pending materials" if name == "analyze" else "Sync, analyze, build and validate")
        p.add_argument("--limit", type=int, default=None)
        p.add_argument("--course", action="append", help="Course id or title substring; repeatable")
        p.add_argument("--path", action="append", help="Exact upstream path; repeatable")
        p.add_argument("--source-dir", type=Path, help="Optional local upstream copy; contents are checked by Git blob SHA")
        p.add_argument("--require-ai", action="store_true", help="Fail if AI is unconfigured or any selected analysis fails")
    args = parser.parse_args(argv)
    try:
        project = load_project(args.root)
        github = GitHub(project["source"]["repository"], os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")) if args.command in {"fetch-updates", "sync", "run", "analyze"} else None
        results = {}
        if args.command == "study":
            results["study"] = study(project, args.chapter, args.status, args.note)
        if args.command == "fetch-updates":
            results["updates"] = fetch_updates(project, github, args.baseline_dir, args.workers, args.plan_only)
        if args.command in {"sync", "run"}:
            results["sync"] = synchronize(project, github)
        if args.command in {"analyze", "run"}:
            results["analysis"] = analyze(project, github, create_client(project["root"]), limit=args.limit if args.limit is not None else project["source"]["daily_analysis_limit"], courses=args.course, paths=args.path, source_dir=args.source_dir, require_ai=args.require_ai)
        if args.command == "write":
            results["textbook"] = write_chapters(project, create_client(project["root"]), limit=args.limit, selected=args.chapter, require_ai=args.require_ai)
        if args.command in {"build", "run", "write"}:
            results["build"] = build(project)
        if args.command in {"validate", "run", "write"}:
            results["validation"] = validate(project, tracked=getattr(args, "tracked", False))
        print(json.dumps(results, ensure_ascii=False, indent=2))
        if results.get("updates", {}).get("failed"):
            return 2
        if getattr(args, "require_ai", False) and results.get("analysis", {}).get("failed"):
            return 2
        if results.get("textbook", {}).get("failed"):
            return 2
        return 0
    except (StudyError, FileNotFoundError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
