import copy
import io
import json
import subprocess
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

from cs_study_map.ai import ModelClient
from cs_study_map.fetch_updates import fetch_updates, plan_updates
from cs_study_map.net import open_without_redirects
from cs_study_map.pipeline import analyze
from cs_study_map.render import build
from cs_study_map.storage import StudyError, git_blob_sha, load_project, read_json, read_jsonl, write_json
from cs_study_map.sync import synchronize
from cs_study_map.textbook import build_textbook, resolve_sources, validate_chapter, write_chapters
from cs_study_map.validate import audit_tracked, validate
from test_pipeline import FakeGitHub, FakeModel, ROOT


def chapter_fixture(key):
    body = "先规定每个编号表示一个固定大小的存储单元。处理问题时先记录初始状态，再按规则修改一项，并核对其他项没有变化。" * 6
    return {
        "introduction": "这一章通过一个小模型解释地址和数据的关系。" * 8,
        "objectives": ["解释一个地址对应的含义", "画出初始状态并逐步追踪", "用独立计算检查所得结果"],
        "prerequisites": ["只需理解自然数和四则运算"],
        "sections": [{"title": f"概念 {i}", "body": body, "source_topic_keys": [key]} for i in range(3)],
        "worked_examples": [{"question": "假设有十个存储单元，分出两个后还剩多少？", "steps": ["先确定全部空间共有十个单元。", "再从这十个单元中划出两个。", "用剩余空间与已分出空间相加检查总量。"], "answer": "还剩八个；八加二等于十，数量保持一致。"} for _ in range(2)],
        "exercises": [{"question": "假设初始有十个单元，取出三个，还剩多少？", "hint": "可以先画十个方格，再划去其中三个。", "answer": "十减三等于七；七加三等于十，可验证结果。"} for _ in range(3)],
        "pitfalls": [{"mistake": "把地址编号当作里面保存的数据。", "correction": "地址用来定位，数据是对应位置保存的值。"} for _ in range(2)],
        "self_checks": ["独立画出初始状态", "自己完成一次计算", "用逆向运算检查答案"],
        "limitations": ["这里使用的是简化教学模型，尚未模拟硬件。"],
    }


class BookModel:
    configured = True
    model = "test-fixture-not-a-real-model"

    def __init__(self):
        self.calls = 0
        self.context = None

    def generate(self, context, prompt, max_tokens):
        self.calls += 1
        self.context = context
        return chapter_fixture(context["source_topics"][0]["key"])


class BookAndUpdateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ["source.json", "taxonomy.json", "courses.json", "overrides.json"]:
            write_json(self.root / "config" / name, read_json(ROOT / "config" / name))
        (self.root / "README.md").write_text("# Fixture\n", encoding="utf-8")
        (self.root / "docs").mkdir()
        (self.root / "docs/learning-log-template.md").write_text("# 本地记录\n", encoding="utf-8")
        self.project = load_project(self.root)
        self.github = FakeGitHub()
        synchronize(self.project, self.github)
        self.record = read_jsonl(self.root / "catalog/files.jsonl")[0]
        self.plan = {"title": "测试教材", "learner": "零基础", "chapters": [{"id": "01-start", "title": "认识存储", "scope": "解释地址", "sources": [{"analysis_id": self.record["id"], "topic_indexes": [0]}]}], "planned": []}
        write_json(self.root / "config/curriculum.json", self.plan)
        self.model = BookModel()

    def prepare(self):
        analyze(self.project, self.github, FakeModel())

    def test_book_is_original_brief_only_idempotent_and_has_answers(self):
        self.prepare()
        result = write_chapters(self.project, self.model)
        self.assertEqual(result["completed"], 1)
        self.assertEqual(set(self.model.context), {"learner", "title", "scope", "source_topics"})
        self.assertNotIn("segments", json.dumps(self.model.context))
        build(self.project)
        self.assertEqual(validate(self.project)["chapters"], 1)
        page = (self.root / "docs/textbook/01-start.md").read_text(encoding="utf-8")
        self.assertIn("解答与检查", page)
        self.assertIn("固定版本", page)
        before = (self.root / "catalog/chapters/01-start.json").read_bytes()
        self.assertEqual(write_chapters(self.project, self.model)["attempted"], 0)
        self.assertEqual(self.model.calls, 1)
        self.assertEqual(before, (self.root / "catalog/chapters/01-start.json").read_bytes())

    def test_upstream_change_marks_book_stale_and_missing_evidence_stops_writing(self):
        self.prepare()
        write_chapters(self.project, self.model)
        self.github.data[self.record["path"]] += b" changed"
        self.github.commit = "c" * 40
        synchronize(self.project, self.github)
        self.assertEqual(build_textbook(self.project)["needs_review"], 1)
        self.assertEqual(write_chapters(self.project, self.model)["failed"], 1)
        self.assertEqual(self.model.calls, 1)

    def test_manual_analysis_correction_invalidates_book(self):
        self.prepare()
        write_chapters(self.project, self.model)
        self.project["overrides"]["files"][self.record["path"]] = {"summary": "人工修改的具体解释。"}
        self.assertEqual(build_textbook(self.project)["needs_review"], 1)

    def test_book_rejects_invented_evidence_and_thin_outline(self):
        self.prepare()
        sources = resolve_sources(self.project, self.plan["chapters"][0])
        content = chapter_fixture(sources[0]["topics"][0]["key"])
        content["sections"][0]["source_topic_keys"] = ["invented:0"]
        with self.assertRaises(StudyError):
            validate_chapter(content, sources)
        content["sections"][0]["source_topic_keys"] = [sources[0]["topics"][0]["key"]]
        content["sections"][0]["body"] = "只有一个提纲"
        with self.assertRaises(StudyError):
            validate_chapter(content, sources)

    def test_book_rejects_uncertain_source_and_ignores_removed_chapter(self):
        self.prepare()
        path = self.root / "catalog/analyses" / (self.record["id"] + ".json")
        analysis = read_json(path)
        analysis["result"]["uncertain"] = True
        write_json(path, analysis)
        self.assertEqual(write_chapters(self.project, self.model)["failed"], 1)
        self.assertEqual(self.model.calls, 0)
        with self.assertRaises(StudyError):
            write_chapters(self.project, self.model, selected=["missing"])

    def test_diff_plan_uses_content_and_does_not_redownload_moved_files(self):
        baseline = self.root / ".local/baseline"
        baseline.mkdir(parents=True)
        (baseline / "moved.md").write_bytes(self.github.data[self.record["path"]])
        result = plan_updates(self.project, baseline)
        self.assertEqual(result["files"], [])
        self.assertEqual(result["same_content_elsewhere"], 1)

    def test_fetch_resumes_and_repairs_corrupt_private_cache(self):
        baseline = self.root / ".local/baseline"
        baseline.mkdir(parents=True)
        result = fetch_updates(self.project, self.github, baseline, workers=2)
        self.assertTrue(result["download_complete"])
        self.assertEqual(result["verified"], 1)
        count = self.github.downloads
        manifest = read_json(result["manifest"])
        local = Path(manifest["files"][0]["local_path"])
        self.assertTrue(local.resolve().is_relative_to((self.root / ".cache").resolve()))
        fetch_updates(self.project, self.github, baseline)
        self.assertEqual(self.github.downloads, count)
        local.write_bytes(b"corrupt")
        self.assertTrue(fetch_updates(self.project, self.github, baseline)["download_complete"])
        self.assertEqual(git_blob_sha(local.read_bytes()), self.record["blob_sha"])

    def test_failed_fetch_is_not_complete_and_can_retry(self):
        baseline = self.root / ".local/baseline"
        baseline.mkdir(parents=True)
        with patch.object(self.github, "download", side_effect=StudyError("GitHub network request failed")):
            result = fetch_updates(self.project, self.github, baseline)
        self.assertFalse(result["download_complete"])
        self.assertEqual(result["failed"], 1)
        self.assertTrue(fetch_updates(self.project, self.github, baseline)["download_complete"])

    def test_publish_audit_blocks_upstream_markdown_even_if_renamed(self):
        (self.root / "copied.md").write_bytes(self.github.data[self.record["path"]])
        proc = subprocess.CompletedProcess([], 0, stdout=b"copied.md\0")
        with patch("cs_study_map.validate.subprocess.run", return_value=proc):
            with self.assertRaisesRegex(StudyError, "duplicates upstream"):
                audit_tracked(self.root)


class TransportTests(unittest.TestCase):
    def test_api_both_protocols_parse_complete_json(self):
        for style in ["chat", "responses"]:
            with self.subTest(style=style):
                content = '{"ok":true}'
                body = {"choices": [{"finish_reason": "stop", "message": {"content": content}}]} if style == "chat" else {"status": "completed", "output": [{"content": [{"type": "output_text", "text": content}]}]}
                response = io.BytesIO(json.dumps(body).encode())
                with patch("cs_study_map.ai.open_without_redirects", return_value=response) as opened:
                    client = ModelClient(base="https://example.invalid/v1", key="test-only", model="test", style=style)
                    self.assertEqual(client.generate({"topic": "test"}, "test prompt", 12000), {"ok": True})
                    payload = json.loads(opened.call_args.args[0].data)
                    self.assertEqual(payload["model"], "test")
                    self.assertFalse(payload["stream"])

    def test_api_error_body_is_withheld_and_request_not_replayed(self):
        failure = urllib.error.HTTPError("https://example.invalid", 503, "busy", {}, io.BytesIO(b"private-provider-output"))
        with patch("cs_study_map.ai.open_without_redirects", side_effect=failure) as opened:
            with self.assertRaisesRegex(StudyError, "HTTP 503") as error:
                ModelClient(base="https://example.invalid", key="private", model="test").analyze({})
            self.assertNotIn("private-provider-output", str(error.exception))
            self.assertEqual(opened.call_count, 1)

    def test_redirect_does_not_replay_authorization(self):
        seen = []

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                seen.append(self.path)
                self.send_response(302)
                self.send_header("Location", "/would-receive-credential")
                self.end_headers()

            def log_message(self, *args):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            request = urllib.request.Request(f"http://127.0.0.1:{server.server_port}/initial", headers={"Authorization": "Bearer test-only"})
            with self.assertRaises(urllib.error.HTTPError):
                open_without_redirects(request, 5)
            self.assertEqual(seen, ["/initial"])
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == "__main__":
    unittest.main()
