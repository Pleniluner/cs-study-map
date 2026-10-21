"""Execute only the two reviewed, original programming lessons, never upstream files."""

import ast
import copy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from cs_study_map.storage import StudyError, load_project, read_json
from cs_study_map.textbook import (
    BOOK_PROMPT, BOOK_PROMPT_VERSION, PYTHON_BOOK_PROMPT_VERSION,
    chapter_status, curriculum, program_lines, validate_document,
    validate_program, validate_references, writing_prompt,
)

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ["04-control-flow", "05-functions"]
# These lessons deliberately use only names, arithmetic and structured control flow.
# Expanding this list requires reviewing the newly introduced teaching constructs.
ALLOWED_NODES = {
    ast.Module, ast.Assign, ast.Name, ast.Load, ast.Store, ast.Constant,
    ast.BinOp, ast.Add, ast.Sub, ast.Mult, ast.FloorDiv, ast.Mod,
    ast.UnaryOp, ast.USub, ast.UAdd, ast.Not, ast.BoolOp, ast.And, ast.Or,
    ast.Compare, ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
    ast.If, ast.While, ast.For, ast.Expr, ast.Call, ast.FunctionDef,
    ast.arguments, ast.arg, ast.Return,
}


def lesson(chapter):
    return read_json(ROOT / "catalog/chapters" / (chapter + ".json"))["content"]


def checked_tree(code):
    tree = ast.parse(code)
    functions = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    for node in ast.walk(tree):
        if type(node) not in ALLOWED_NODES:
            raise AssertionError("Unreviewed construct in lesson program: " + type(node).__name__)
        if isinstance(node, ast.Call) and (not isinstance(node.func, ast.Name) or node.func.id not in {"print", "range"} | functions):
            raise AssertionError("Unreviewed call in lesson program")
    return tree


def run_program(program, overrides=None, checks=""):
    tree = checked_tree(program["code"])
    changed = set()
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name in (overrides or {}):
                node.value = ast.Constant(overrides[name])
                changed.add(name)
    if changed != set(overrides or {}):
        raise AssertionError("Boundary test did not replace the intended input")
    code = ast.unparse(ast.fix_missing_locations(tree)) + "\n" + checks
    with tempfile.TemporaryDirectory() as directory:
        result = subprocess.run(
            [sys.executable, "-I", "-S", "-X", "utf8", "-c", code],
            cwd=directory, capture_output=True, text=True, encoding="utf-8", timeout=4,
        )
    if result.returncode:
        raise AssertionError(result.stderr)
    return result.stdout


class ProgrammingLessonTests(unittest.TestCase):
    def test_all_twenty_original_programs_match_their_printed_outputs(self):
        count = 0
        for identifier in CHAPTERS:
            document = read_json(ROOT / "catalog/chapters" / (identifier + ".json"))
            validate_document(document)
            for group in ("sections", "worked_examples", "exercises"):
                for index, item in enumerate(document["content"][group]):
                    with self.subTest(chapter=identifier, group=group, item=index):
                        self.assertEqual(run_program(item["program"]), item["program"]["output"])
                        count += 1
        self.assertEqual(count, 20)

    def test_control_flow_boundary_inputs(self):
        content = lesson("04-control-flow")
        cases = [
            (content["sections"][1], "temperature", [(14, "cool\n"), (15, "mild\n"), (29, "mild\n"), (30, "hot\n")]),
            (content["sections"][2], "remaining", [(0, "0 0\n"), (2, "0 2\n"), (3, "1 0\n"), (6, "2 0\n")]),
            (content["sections"][4], "n", [(0, "1 0\n"), (1, "2 1\n")]),
            (content["worked_examples"][0], "participants", [(0, "empty\n"), (1, "small\n"), (8, "small\n"), (9, "large\n")]),
            (content["worked_examples"][1], "target", [(0, "0 0\n"), (1, "1 1\n"), (15, "5 15\n"), (16, "6 21\n"), (21, "6 21\n")]),
            (content["exercises"][0], "number", [(-2, "negative\n"), (0, "zero\n"), (5, "positive\n")]),
            (content["exercises"][1], "upper", [(0, "0 0\n"), (3, "1 3\n"), (15, "4 30\n"), (20, "5 48\n")]),
            (content["exercises"][2], "remaining", [(0, "0 0\n"), (1, "1 0\n"), (5, "1 0\n"), (6, "2 0\n"), (23, "5 0\n")]),
        ]
        for item, name, values in cases:
            for value, output in values:
                with self.subTest(input=name, value=value, expected=output):
                    self.assertEqual(run_program(item["program"], {name: value}), output)

    def test_unit_function_capacity_and_minimality_over_many_inputs(self):
        item = lesson("05-functions")["worked_examples"][0]
        checks = """
for byte_count in range(101):
    for unit_size in range(1, 11):
        needed = required_units(byte_count, unit_size)
        assert isinstance(needed, int)
        assert needed * unit_size >= byte_count
        assert (needed == 0 and byte_count == 0) or (needed - 1) * unit_size < byte_count
"""
        self.assertEqual(run_program(item["program"], checks=checks), item["program"]["output"])

    def test_composed_functions_and_local_names(self):
        item = lesson("05-functions")["worked_examples"][1]
        checks = """
for n in range(41):
    m = n // 2
    assert sum_even_squares(n) == 4 * m * (m + 1) * (2 * m + 1) // 6
assert total == 100
assert sum_even_squares(6) == 56
assert sum_even_squares(0) == 0
assert sum_even_squares(6) == 56
"""
        self.assertEqual(run_program(item["program"], checks=checks), item["program"]["output"])

    def test_function_exercises_include_empty_negative_and_threshold_cases(self):
        exercises = lesson("05-functions")["exercises"]
        checks = [
            "\nfor n in range(-12, 13):\n    assert clamp_to_zero(n) == max(n, 0)\n",
            "\nfor a in range(-5, 6):\n    for b in range(a, 7):\n        assert sum_between(a, b) == (b - a) * (a + b - 1) // 2\n",
            """
for n in range(51):
    assert sum_to(n) == n * (n + 1) // 2
for target in range(251):
    days = days_to_reach(target)
    assert days * (days + 1) // 2 >= target
    assert (days == 0 and target == 0) or (days - 1) * days // 2 < target
""",
        ]
        for item, additional_checks in zip(exercises, checks):
            self.assertEqual(run_program(item["program"], checks=additional_checks), item["program"]["output"])

    def test_program_validation_checks_syntax_without_running_it(self):
        validate_program({"code": "raise RuntimeError('must not execute')", "output": ""})
        invalid = [
            {"code": "while True print(1)", "output": ""},
            {"code": "return 1", "output": ""},
            {"code": " ", "output": ""},
            {"code": "print(1)", "output": "```"},
            {"code": "print(1)", "output": 1},
            {"code": "print(1)", "output": "1\n", "raw": "unexpected"},
        ]
        for value in invalid:
            with self.subTest(value=value), self.assertRaises(StudyError):
                validate_program(value)

    def test_python_chapters_require_executable_exercise_solutions(self):
        document = read_json(ROOT / "catalog/chapters/05-functions.json")
        self.assertEqual(document["prompt_version"], PYTHON_BOOK_PROMPT_VERSION)
        del document["content"]["exercises"][0]["program"]
        with self.assertRaisesRegex(StudyError, "require programs"):
            validate_document(document)

    def test_reference_snapshots_and_prose_prompt_remain_compatible(self):
        project = load_project(ROOT)
        plan = curriculum(project)
        for chapter in plan["chapters"]:
            document = read_json(ROOT / "catalog/chapters" / (chapter["id"] + ".json"))
            self.assertEqual(chapter_status(project, plan, chapter, document), "current")
            if chapter.get("format") == "python":
                self.assertEqual(document["references"], chapter["references"])
            else:
                self.assertEqual(writing_prompt(chapter), (BOOK_PROMPT, BOOK_PROMPT_VERSION))
        reference = copy.deepcopy(plan["chapters"][-1]["references"][0])
        for url in ["http://docs.python.org/3.11/", "https://docs.python.org/3.11/?key=example"]:
            reference["url"] = url
            with self.assertRaises(StudyError):
                validate_references([reference])

    def test_code_renderer_preserves_comparisons_and_indentation(self):
        item = lesson("04-control-flow")["exercises"][2]
        text = "\n".join(program_lines(item))
        self.assertIn("while remaining > 0:", text)
        self.assertIn("    if remaining >= capacity:", text)
        self.assertIn("```text\n5 0\n```", text)
        self.assertNotIn("&gt;", text)


if __name__ == "__main__":
    unittest.main()
