import contextlib
import copy
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from cs_study_map.cli import main
from cs_study_map.pipeline import analyze
from cs_study_map.render import build
from cs_study_map.storage import StudyError, load_project, read_json, read_jsonl, write_json
from cs_study_map.study import PROGRESS_FILE, study
from cs_study_map.sync import synchronize
from cs_study_map.textbook import build_textbook, write_chapters
from cs_study_map.validate import validate
from test_pipeline import FakeGitHub, FakeModel, ROOT
from test_textbook_updates import BookModel


class StudyTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        for name in ("source.json", "taxonomy.json", "courses.json", "overrides.json"):
            write_json(self.root / "config" / name, read_json(ROOT / "config" / name))
        (self.root / "README.md").write_text("# Test\n", encoding="utf-8")
        (self.root / "docs").mkdir()
        (self.root / "docs/learning-log-template.md").write_text("# Notes\n", encoding="utf-8")
        self.project = load_project(self.root)
        self.github = FakeGitHub()
        synchronize(self.project, self.github)
        self.record = read_jsonl(self.root / "catalog/files.jsonl")[0]
        self.plan = {
            "title": "试学", "learner": "初学者", "planned": [],
            "chapters": [{"id": "01-start", "title": "第一章", "scope": "解释地址", "sources": [
                {"analysis_id": self.record["id"], "topic_indexes": [0]},
            ]}],
        }
        write_json(self.root / "config/curriculum.json", self.plan)
        with contextlib.redirect_stdout(io.StringIO()):
            analyze(self.project, self.github, FakeModel())
            write_chapters(self.project, BookModel())
        self.path = self.root / PROGRESS_FILE
        self.chapter_path = self.root / "catalog/chapters/01-start.json"

    def test_status_and_cli_are_read_only_and_do_not_create_network_clients(self):
        with patch("cs_study_map.cli.GitHub", side_effect=AssertionError("network client")), \
             patch("cs_study_map.cli.create_client", side_effect=AssertionError("AI client")), \
             contextlib.redirect_stdout(io.StringIO()) as output:
            result = main(["--root", str(self.root), "study"])
        self.assertEqual(result, 0)
        report = json.loads(output.getvalue())["study"]
        self.assertEqual((report["completed"], report["next_chapter"]), (0, "01-start"))
        self.assertEqual(report["chapters"][0]["status"], "not-started")
        self.assertFalse((self.root / ".local").exists())

    def test_notes_append_privately_and_resets_keep_notes(self):
        first_note = "只属于本机的学习卡点"
        study(self.project, "01-start", "reading", first_note)
        report = study(self.project, "01-start", note="第二个卡点")
        self.assertEqual(report["chapters"][0]["status"], "reading")
        self.assertEqual(report["chapters"][0]["note_count"], 2)
        self.assertNotIn(first_note, json.dumps(report, ensure_ascii=False))
        self.assertIn("self_checks", report["chapters"][0])
        saved = read_json(self.path)
        self.assertEqual(saved["chapters"]["01-start"]["notes"][0]["text"], first_note)
        study(self.project, "01-start", "completed")
        self.assertEqual(study(self.project)["completed"], 1)
        study(self.project, "01-start", "not-started")
        report = study(self.project)
        self.assertEqual(report["chapters"][0]["note_count"], 2)
        self.assertEqual(report["chapters"][0]["status"], "not-started")

    def test_changed_text_requires_review_and_notes_do_not_acknowledge_revision(self):
        study(self.project, "01-start", "completed")
        document = read_json(self.chapter_path)
        document["content"]["sections"][0]["body"] += "新版补充一次地址核对。"
        write_json(self.chapter_path, document)
        before = self.path.read_bytes()
        report = study(self.project)
        self.assertEqual(report["completed"], 0)
        self.assertEqual(report["chapters"][0]["status"], "review")
        self.assertTrue(report["chapters"][0]["chapter_changed"])
        self.assertEqual(self.path.read_bytes(), before)
        study(self.project, "01-start", note="稍后重做")
        self.assertEqual(study(self.project)["chapters"][0]["status"], "review")
        study(self.project, "01-start", "completed")
        self.assertEqual(study(self.project)["completed"], 1)

    def test_stale_source_blocks_completion_without_overwriting_old_record(self):
        study(self.project, "01-start", "completed", "保留的笔记")
        before = self.path.read_bytes()
        self.github.data[self.record["path"]] += b" changed"
        self.github.commit = "c" * 40
        synchronize(self.project, self.github)
        report = study(self.project)
        self.assertEqual(report["chapters"][0]["availability"], "needs-review")
        self.assertEqual(report["chapters"][0]["status"], "review")
        with self.assertRaisesRegex(StudyError, "awaits source"):
            study(self.project, "01-start", "completed")
        self.assertEqual(self.path.read_bytes(), before)

    def test_invalid_requests_leave_existing_progress_untouched(self):
        study(self.project, "01-start", "reading")
        before = self.path.read_bytes()
        for arguments in [
            {"status": "completed"}, {"note": "missing chapter"},
            {"chapter_id": "../outside", "status": "reading"},
            {"chapter_id": "01-start", "note": " "},
            {"chapter_id": "01-start", "note": "x" * 2001},
            {"chapter_id": "01-start", "status": "unknown"},
        ]:
            with self.subTest(arguments=arguments), self.assertRaises(StudyError):
                study(self.project, **arguments)
            self.assertEqual(self.path.read_bytes(), before)

    def test_corrupt_record_is_reported_without_overwriting_private_data(self):
        self.path.parent.mkdir()
        for contents in ['{"schema_version":', '{"schema_version":1,"chapters":{"01-start":{}}}']:
            self.path.write_text(contents, encoding="utf-8")
            with self.assertRaisesRegex(StudyError, "Local study progress is invalid"):
                study(self.project, "01-start", "reading", "new note")
            self.assertEqual(self.path.read_text(encoding="utf-8"), contents)

    def test_git_ignore_is_required_and_tracked_progress_is_rejected(self):
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True, capture_output=True)
        with self.assertRaisesRegex(StudyError, "Git must ignore"):
            study(self.project, "01-start", "reading")
        self.assertFalse(self.path.exists())
        (self.root / ".gitignore").write_text(".local/\n", encoding="utf-8")
        study(self.project, "01-start", "reading")
        subprocess.run(["git", "add", "-f", PROGRESS_FILE], cwd=self.root, check=True, capture_output=True)
        before = self.path.read_bytes()
        with self.assertRaisesRegex(StudyError, "Git must ignore"):
            study(self.project, "01-start", note="must not be saved")
        self.assertEqual(self.path.read_bytes(), before)

    def test_removed_chapters_keep_private_history_and_planned_chapters_are_explicit(self):
        study(self.project, "01-start", "completed", "retained")
        self.plan["chapters"][0]["id"] = "02-planned"
        write_json(self.root / "config/curriculum.json", self.plan)
        before = self.path.read_bytes()
        report = study(self.project)
        self.assertEqual(report["archived_records"], 1)
        self.assertEqual(report["next_chapter"], "02-planned")
        self.assertEqual(report["chapters"][0]["availability"], "planned")
        self.assertIsNone(report["chapters"][0]["page"])
        with self.assertRaisesRegex(StudyError, "not been written"):
            study(self.project, "02-planned", "reading")
        self.assertEqual(self.path.read_bytes(), before)

    def test_build_keeps_notes_private_and_navigation_is_deterministic(self):
        self.plan["chapters"] += [dict(copy.deepcopy(self.plan["chapters"][0]), id="02-next", title="第二章")]
        write_json(self.root / "config/curriculum.json", self.plan)
        with contextlib.redirect_stdout(io.StringIO()):
            write_chapters(self.project, BookModel())
        (self.root / "docs/study-guide.md").write_text("# Guide\n", encoding="utf-8")
        build(self.project)
        first = self.root / "docs/textbook/01-start.md"
        second = self.root / "docs/textbook/02-next.md"
        self.assertIn("[下一章：第二章](02-next.md)", first.read_text(encoding="utf-8"))
        self.assertIn("[上一章：第一章](01-start.md)", second.read_text(encoding="utf-8"))
        self.assertIn('[自测](#self-check)', first.read_text(encoding="utf-8"))
        self.assertIn('<a id="self-check"></a>', first.read_text(encoding="utf-8"))
        before = {p: p.read_bytes() for p in (self.root / "docs").rglob("*.md")}
        study(self.project, "01-start", "completed", "this note must stay private")
        build(self.project)
        self.assertEqual(before, {p: p.read_bytes() for p in (self.root / "docs").rglob("*.md")})
        self.assertEqual(validate(self.project)["chapters"], 2)
        self.assertEqual(study(self.project)["next_chapter"], "02-next")
        second_source = self.root / "catalog/chapters/02-next.json"
        second_source.unlink()
        build_textbook(self.project)
        self.assertFalse(second.exists())
        self.assertNotIn("](02-next.md)", first.read_text(encoding="utf-8"))
        self.assertIn("第二章（待编写）", first.read_text(encoding="utf-8"))
        self.assertEqual(validate(self.project)["chapters"], 1)
        write_json(second_source, {})
        build_textbook(self.project)
        self.assertNotIn("](02-next.md)", first.read_text(encoding="utf-8"))

    def test_broken_maintained_guide_links_are_checked(self):
        build(self.project)
        (self.root / "docs/study-guide.md").write_text("[missing](missing.md)\n", encoding="utf-8")
        with self.assertRaisesRegex(StudyError, "Broken local documentation link"):
            validate(self.project)


if __name__ == "__main__":
    unittest.main()
