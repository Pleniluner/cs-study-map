import copy
import io
import json
import os
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from cs_study_map.ai import ModelClient, validate_result
from cs_study_map.extract import extract
from cs_study_map.github import GitHub
from cs_study_map.pipeline import analyze, current_analysis
from cs_study_map.render import build, md
from cs_study_map.storage import StudyError, git_blob_sha, load_project, read_json, read_jsonl, write_json
from cs_study_map.sync import changes_between, synchronize
from cs_study_map.validate import validate

ROOT = Path(__file__).resolve().parents[1]


def model_result(identifier="L1-L3"):
    return {
        "subjects": ["systems"], "resource_type": "lab", "summary": "介绍页表映射与内存分配实验的观察方法。",
        "topics": [{"name": "虚拟内存与页表", "evidence_ids": [identifier]}],
        "suggested_prerequisites": ["了解地址转换"], "suggested_exercises": ["对照两组映射结果解释地址转换过程。"], "uncertain": False,
    }


class FakeGitHub:
    def __init__(self):
        self.commit = "a" * 40
        self.data = {"大三下/操作系统/lab.md": "# 页表实验\n观察物理页分配和虚拟地址到物理地址的转换。\n记录页表变化，比较不同映射后的结果。".encode()}
        self.tree_calls = 0
        self.downloads = 0

    def head(self, branch):
        return self.commit, "b" * 40

    def tree(self, sha):
        self.tree_calls += 1
        return [{"path": p, "type": "blob", "mode": "100644", "sha": git_blob_sha(d), "size": len(d)} for p, d in self.data.items()]

    def download(self, commit, record, limit):
        self.downloads += 1
        return self.data[record["path"]]


class FakeModel:
    configured = True
    model = "test-fixture-not-a-real-model"

    def __init__(self):
        self.calls = 0

    def analyze(self, context):
        self.calls += 1
        return model_result(context["untrusted_segments"][0]["id"])


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ["source.json", "taxonomy.json", "courses.json", "overrides.json"]:
            write_json(self.root / "config" / name, read_json(ROOT / "config" / name))
        (self.root / "README.md").write_text("# test\n", encoding="utf-8")
        self.project = load_project(self.root)
        self.github = FakeGitHub()
        self.model = FakeModel()

    def initialize(self):
        synchronize(self.project, self.github)
        return read_jsonl(self.root / "catalog/files.jsonl")[0]

    def test_end_to_end_public_content_and_idempotence(self):
        record = self.initialize()
        report = analyze(self.project, self.github, self.model)
        self.assertEqual(report["completed"], 1)
        build(self.project)
        self.assertEqual(validate(self.project)["current_analyses"], 1)
        before = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob("*") if p.is_file() and ".cache" not in p.parts}
        self.assertFalse(synchronize(self.project, self.github)["changed"])
        analyze(self.project, self.github, self.model)
        build(self.project)
        after = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob("*") if p.is_file() and ".cache" not in p.parts}
        self.assertEqual(before, after)
        self.assertEqual(self.model.calls, 1)
        self.assertEqual(self.github.tree_calls, 1)
        public = current_analysis(self.project, record)
        self.assertNotIn("segments", public)
        self.assertNotIn("text", public["evidence"][0])
        self.assertNotIn(self.github.data[record["path"]].decode(), json.dumps(public, ensure_ascii=False))

    def test_changed_content_expires_old_analysis_and_retries(self):
        record = self.initialize()
        analyze(self.project, self.github, self.model)
        self.github.data[record["path"]] += "\n新增缺页处理实验和比较步骤。".encode()
        self.github.commit = "c" * 40
        synchronize(self.project, self.github)
        changed = read_jsonl(self.root / "catalog/files.jsonl")[0]
        self.assertIsNone(current_analysis(self.project, changed))
        build(self.project)
        self.assertEqual(read_json(self.root / "catalog/coverage.json")["analyzed"], 0)
        analyze(self.project, self.github, self.model)
        self.assertEqual(self.model.calls, 2)

    def test_removal_prunes_current_guides_and_pages(self):
        record = self.initialize()
        analyze(self.project, self.github, self.model)
        build(self.project)
        self.github.data = {"new-course/readme.md": b"Another sufficiently long resource about algorithms and data."}
        self.github.commit = "d" * 40
        synchronize(self.project, self.github)
        build(self.project)
        self.assertFalse((self.root / "catalog/analyses" / (record["id"] + ".json")).exists())
        self.assertFalse((self.root / "docs/courses" / (record["course_id"] + ".md")).exists())

    def test_manual_correction_survives_regeneration(self):
        record = self.initialize()
        analyze(self.project, self.github, self.model)
        self.project["overrides"]["files"][record["path"]] = {"subjects": ["algorithms"], "summary": "人工修正的学习说明。"}
        build(self.project)
        page = self.root / "docs/courses" / (record["course_id"] + ".md")
        self.assertIn("人工修正的学习说明", page.read_text(encoding="utf-8"))
        analyze(self.project, self.github, self.model)
        build(self.project)
        self.assertIn("人工修正的学习说明", page.read_text(encoding="utf-8"))

    def test_no_configuration_is_not_successful_analysis(self):
        self.initialize()
        with patch.dict(os.environ, {}, clear=True):
            result = analyze(self.project, self.github, ModelClient())
            self.assertEqual(result["status"], "not-configured")
            with self.assertRaises(StudyError):
                analyze(self.project, self.github, ModelClient(), require_ai=True)

    def test_failure_keeps_successful_analysis_and_can_resume(self):
        record = self.initialize()
        self.model.analyze = lambda context: (_ for _ in ()).throw(StudyError("AI provider returned HTTP 503"))
        result = analyze(self.project, self.github, self.model)
        self.assertEqual(result["failed"], 1)
        self.assertIsNone(current_analysis(self.project, record))
        good = FakeModel()
        analyze(self.project, self.github, good)
        self.assertEqual(read_json(self.root / "catalog/analysis-failures.json"), {})

    def test_partial_tree_failure_preserves_old_index(self):
        self.initialize()
        old = (self.root / "catalog/files.jsonl").read_bytes()
        self.github.commit = "e" * 40
        self.github.tree = lambda sha: (_ for _ in ()).throw(StudyError("Incomplete tree"))
        with self.assertRaises(StudyError):
            synchronize(self.project, self.github)
        self.assertEqual(old, (self.root / "catalog/files.jsonl").read_bytes())

    def test_empty_tree_does_not_erase_index(self):
        self.initialize()
        self.github.commit = "e" * 40
        self.github.data = {}
        with self.assertRaises(StudyError):
            synchronize(self.project, self.github)
        self.assertEqual(len(read_jsonl(self.root / "catalog/files.jsonl")), 1)

    def test_invalid_ai_evidence_is_rejected(self):
        extraction = extract("file.md", next(iter(self.github.data.values())))
        with self.assertRaises(StudyError):
            validate_result(model_result("invented-page"), extraction, self.project["taxonomy"])

    def test_raw_fields_and_long_copy_are_rejected(self):
        result = model_result()
        result["source_text"] = "raw document"
        with self.assertRaises(StudyError):
            validate_result(result, {"segments": []}, self.project["taxonomy"])
        long_text = "这是一段不能原样公开复制的测试原始材料。" * 8
        result = model_result()
        result["summary"] = long_text
        with self.assertRaises(StudyError):
            validate_result(result, {"segments": [{"id": "L1-L3", "text": long_text}]}, self.project["taxonomy"])

    def test_source_path_escape_rejected(self):
        self.github.data = {"../../escape.md": b"not allowed"}
        with self.assertRaises(StudyError):
            synchronize(self.project, self.github)

    def test_tracked_audit_rejects_source_document(self):
        self.initialize()
        build(self.project)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        (self.root / "original.pdf").write_bytes(b"%PDF upstream source")
        subprocess.run(["git", "add", "original.pdf"], cwd=self.root, check=True)
        with self.assertRaises(StudyError):
            validate(self.project, tracked=True)


class IndependentTests(unittest.TestCase):
    def test_tree_truncation_fetches_subtrees(self):
        client = GitHub("owner/repo")
        responses = {
            "git/trees/root?recursive=1": {"truncated": True, "tree": [{"path": "partial"}]},
            "git/trees/root": {"truncated": False, "tree": [{"path": "folder", "type": "tree", "sha": "child"}]},
            "git/trees/child": {"truncated": False, "tree": [{"path": "a.md", "type": "blob", "sha": "blob"}]},
        }
        client.api = responses.__getitem__
        self.assertEqual(client.tree("root")[0]["path"], "folder/a.md")

    def test_download_checks_hash(self):
        client = GitHub("owner/repo")
        client._get = lambda url, limit: b"tampered"
        with self.assertRaises(StudyError):
            client.download("a" * 40, {"path": "a.md", "blob_sha": git_blob_sha(b"original"), "size": 8}, 100)

    def test_rename_and_modification(self):
        old = [{"path": "old", "blob_sha": "1"}, {"path": "modify", "blob_sha": "2"}]
        new = [{"path": "new", "blob_sha": "1"}, {"path": "modify", "blob_sha": "3"}]
        result = changes_between(old, new)
        self.assertEqual(result["moved"], [{"from": "old", "to": "new"}])
        self.assertEqual(result["modified"], ["modify"])

    def test_partial_and_redacted_text(self):
        data = ("Contact student@example.com 2018011438\n" + "算法与数据结构学习资料\n" * 50).encode()
        result = extract("note.txt", data, max_chars=120)
        self.assertEqual(result["coverage"], "partial")
        text = result["segments"][0]["text"]
        self.assertNotIn("student@example.com", text)
        self.assertNotIn("2018011438", text)

    def test_notebook_ignores_outputs(self):
        data = json.dumps({"cells": [{"cell_type": "code", "source": ["# Understand the memory allocator and compare page table mappings"], "outputs": [{"text": "PRIVATE OUTPUT"}]}]}).encode()
        result = extract("test.ipynb", data)
        self.assertNotIn("PRIVATE OUTPUT", json.dumps(result))

    def test_docx_without_execution(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as z:
            z.writestr("word/document.xml", '<w:document xmlns:w="urn:word"><w:t>学习内存管理中的页表、映射与地址转换，记录实验现象并说明原因。</w:t></w:document>')
        self.assertEqual(extract("test.docx", buffer.getvalue())["segments"][0]["locator"], "Word 正文")

    def test_markdown_escape(self):
        result = md('<script>alert(1)</script> [evil](x) | *')
        self.assertNotIn("<script>", result)
        self.assertIn("\\[", result)

    def test_unsupported_model_result_shape(self):
        with self.assertRaises(StudyError):
            validate_result([], {"segments": []}, {"subjects": {}, "resource_types": []})


if __name__ == "__main__":
    unittest.main()
