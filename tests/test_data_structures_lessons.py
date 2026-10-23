"""Run reviewed, original data-structure programs and independent reference models."""

import ast
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from cs_study_map.storage import read_json
from cs_study_map.textbook import validate_document
from test_programming_lessons import ALLOWED_NODES

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ["06-arrays", "07-linked-lists", "08-stacks", "09-queues"]
NODES = ALLOWED_NODES | {
    ast.List, ast.Dict, ast.Subscript, ast.Slice, ast.Attribute,
    ast.Is, ast.IsNot, ast.In, ast.NotIn, ast.BitAnd,
}
METHODS = {"append", "pop", "insert", "copy"}


def document(identifier):
    return read_json(ROOT / "catalog/chapters" / (identifier + ".json"))


def reviewed_tree(code):
    tree = ast.parse(code)
    names = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
    for node in ast.walk(tree):
        if type(node) not in NODES:
            raise AssertionError("Unreviewed lesson construct: " + type(node).__name__)
        if isinstance(node, ast.Attribute) and node.attr not in METHODS:
            raise AssertionError("Unreviewed attribute in lesson")
        if isinstance(node, ast.Call):
            allowed_name = isinstance(node.func, ast.Name) and node.func.id in names | {"print", "range", "len"}
            allowed_method = isinstance(node.func, ast.Attribute) and node.func.attr in METHODS
            if not (allowed_name or allowed_method):
                raise AssertionError("Unreviewed call in lesson")
    return tree


def run_code(code, checks=""):
    reviewed_tree(code)
    with tempfile.TemporaryDirectory() as directory:
        # Execute the literal published code, including its indentation and main program.
        result = subprocess.run(
            [sys.executable, "-I", "-S", "-X", "utf8", "-c", code + "\n" + checks],
            cwd=directory, capture_output=True, text=True, encoding="utf-8", timeout=12,
        )
    if result.returncode:
        raise AssertionError(result.stderr)
    return result.stdout


def definitions(identifier):
    functions = {}
    content = document(identifier)["content"]
    for group in ("sections", "worked_examples", "exercises"):
        for item in content[group]:
            for node in reviewed_tree(item["program"]["code"]).body:
                if isinstance(node, ast.FunctionDef):
                    source = ast.unparse(node)
                    if node.name in functions and functions[node.name] != source:
                        raise AssertionError("Different copies of a lesson helper: " + node.name)
                    functions[node.name] = source
    return "\n\n".join(functions.values()) + "\n"


CHAIN_ORACLE = '''
def inspect_chain(head):
    nodes = []
    seen = set()
    while head is not None:
        assert id(head) not in seen, "Cycle in result"
        seen.add(id(head))
        assert set(head) == {"value", "next"}
        nodes.append(head)
        head = head["next"]
    return nodes

def same_nodes(actual, expected):
    assert len(actual) == len(expected)
    assert all(left is right for left, right in zip(actual, expected))
'''


class DataStructuresLessonTests(unittest.TestCase):
    def test_all_forty_published_programs_match_exact_output(self):
        count = 0
        for identifier in CHAPTERS:
            saved = document(identifier)
            validate_document(saved)
            for group, length in (("sections", 5), ("worked_examples", 2), ("exercises", 3)):
                self.assertEqual(len(saved["content"][group]), length)
                for index, item in enumerate(saved["content"][group]):
                    with self.subTest(chapter=identifier, group=group, item=index):
                        self.assertEqual(run_code(item["program"]["code"]), item["program"]["output"])
                        count += 1
        self.assertEqual(count, 40)

    def test_array_insert_erase_against_sequence_model(self):
        checks = '''
from itertools import product
for capacity in range(6):
    for size in range(capacity + 1):
        for values in product((-1, 0, 2), repeat=size):
            for index in range(-1, size + 2):
                for value in (-2, 0, 4):
                    data = list(values) + [0] * (capacity - size)
                    before = data.copy()
                    expected = list(values)
                    allowed = 0 <= index <= size and size < capacity
                    if allowed:
                        expected.insert(index, value)
                    actual_size = insert_at(data, size, index, value)
                    assert actual_size == len(expected)
                    assert data == expected + [0] * (capacity - len(expected))
                    if not allowed:
                        assert data == before
                data = list(values) + [0] * (capacity - size)
                expected = list(values)
                if 0 <= index < size:
                    del expected[index]
                actual_size = erase_at(data, size, index)
                assert actual_size == len(expected)
                assert data == expected + [0] * (capacity - len(expected))
'''
        self.assertEqual(run_code(definitions("06-arrays"), checks), "")

    def test_array_search_filter_maximum_and_reverse(self):
        checks = '''
from itertools import product
for size in range(6):
    for values in product((-3, 0, 2), repeat=size):
        data = list(values)
        for target in (-3, 0, 2, 7):
            expected = next((i for i, value in enumerate(values) if value == target), -1)
            assert first_index(data, target) == expected
        assert largest(data) == (max(values) if values else None)
        kept = nonnegative_copy(data)
        assert kept == [value for value in values if value >= 0]
        assert kept is not data and data == list(values)
        alias = data
        assert reverse_in_place(data) is None
        assert data == list(values)[::-1] and data is alias
        reverse_in_place(data)
        assert data == list(values)
        assert add_to_first(data, 5) is None
        assert data == ([values[0] + 5] + list(values[1:]) if values else [])
'''
        self.assertEqual(run_code(definitions("06-arrays"), checks), "")

    def test_linked_construction_prepend_and_shared_suffix(self):
        checks = CHAIN_ORACLE + '''
from itertools import product
for size in range(6):
    for values in product((-1, 0, 2), repeat=size):
        source = list(values)
        head = make_chain(source)
        nodes = inspect_chain(head)
        assert [node["value"] for node in nodes] == source
        assert chain_values(head) == source
        assert chain_length(head) == size
        same_nodes(inspect_chain(head), nodes)
        new_head = prepend(head, 7)
        assert new_head["next"] is head
        assert chain_values(new_head) == [7] + source
        same_nodes(inspect_chain(new_head)[1:], nodes)
        if head is not None:
            head["value"] = 9
            assert new_head["next"]["value"] == 9
        assert source == list(values)
'''
        self.assertEqual(run_code(definitions("07-linked-lists"), checks), "")

    def test_linked_insert_and_append_keep_existing_nodes(self):
        checks = CHAIN_ORACLE + '''
from itertools import product
assert insert_after(None, 5) is False
for size in range(5):
    for values in product((-1, 0, 2), repeat=size):
        for index in range(size):
            head = make_chain(list(values))
            nodes = inspect_chain(head)
            assert insert_after(nodes[index], 7) is True
            after = inspect_chain(head)
            same_nodes(after[:index + 1], nodes[:index + 1])
            same_nodes(after[index + 2:], nodes[index + 1:])
            assert after[index + 1]["value"] == 7
            assert all(after[index + 1] is not node for node in nodes)
            assert chain_values(head) == list(values[:index + 1]) + [7] + list(values[index + 1:])
        head = make_chain(list(values))
        nodes = inspect_chain(head)
        result = append_value(head, 4)
        after = inspect_chain(result)
        same_nodes(after[:-1], nodes)
        assert chain_values(result) == list(values) + [4]
        assert after[-1]["next"] is None
        if nodes:
            assert result is head
'''
        self.assertEqual(run_code(definitions("07-linked-lists"), checks), "")

    def test_linked_delete_removes_only_first_matching_node(self):
        checks = CHAIN_ORACLE + '''
from itertools import product
for size in range(6):
    for values in product((-1, 0, 2), repeat=size):
        for target in (-1, 0, 2, 7):
            head = make_chain(list(values))
            nodes = inspect_chain(head)
            expected_nodes = nodes.copy()
            expected_values = list(values)
            if target in values:
                index = values.index(target)
                del expected_nodes[index]
                del expected_values[index]
            result = delete_first(head, target)
            same_nodes(inspect_chain(result), expected_nodes)
            assert chain_values(result) == expected_values
            assert [node["value"] for node in nodes] == list(values)
            if target not in values:
                assert result is head
'''
        self.assertEqual(run_code(definitions("07-linked-lists"), checks), "")

    def test_linked_reverse_preserves_identity_and_restores_links(self):
        checks = CHAIN_ORACLE + '''
from itertools import product
for size in range(6):
    for values in product((-1, 0, 2), repeat=size):
        head = make_chain(list(values))
        nodes = inspect_chain(head)
        reversed_head = reverse_chain(head)
        same_nodes(inspect_chain(reversed_head), nodes[::-1])
        assert chain_values(reversed_head) == list(values)[::-1]
        if head is not None:
            assert head["next"] is None
        restored = reverse_chain(reversed_head)
        same_nodes(inspect_chain(restored), nodes)
        assert restored is head
'''
        self.assertEqual(run_code(definitions("07-linked-lists"), checks), "")

    def test_bounded_stack_operation_sequences_and_peek(self):
        checks = '''
from itertools import product
for capacity in range(1, 5):
    for length in range(7):
        for actions in product(("push-zero", "push-negative", "pop"), repeat=length):
            stack = []
            model = ()
            for action in actions:
                before = stack.copy()
                if action == "pop":
                    expected = model[-1] if model else None
                    assert pop_safe(stack) == expected
                    model = model[:-1]
                    if expected is None:
                        assert stack == before
                else:
                    value = 0 if action == "push-zero" else -2
                    allowed = len(model) < capacity
                    assert push_bounded(stack, value, capacity) is allowed
                    if allowed:
                        model = model + (value,)
                    else:
                        assert stack == before
                before_peek = stack.copy()
                assert peek(stack) == (model[-1] if model else None)
                assert stack == before_peek == list(model)
'''
        self.assertEqual(run_code(definitions("08-stacks"), checks), "")

    def test_stack_reverse_and_limited_removal(self):
        checks = '''
from itertools import product
for size in range(6):
    for values in product((-1, 0, 2), repeat=size):
        original = list(values)
        result = reversed_copy(original)
        assert result == original[::-1] and result is not original
        assert original == list(values)
        for limit in range(size + 3):
            stack = list(values)
            count = min(limit, size)
            expected = list(values)[size - count:][::-1]
            assert take_from_stack(stack, limit) == expected
            assert stack == list(values)[:size - count]
'''
        self.assertEqual(run_code(definitions("08-stacks"), checks), "")

    def test_brackets_against_prefix_counts_and_pair_cancellation(self):
        checks = '''
from itertools import product
for length in range(11):
    for marks in product("()", repeat=length):
        text = "".join(marks)
        depth = 0
        minimum = 0
        for mark in marks:
            depth += 1 if mark == "(" else -1
            minimum = min(minimum, depth)
        assert balanced(text) is (depth == 0 and minimum == 0)
for length in range(7):
    for marks in product("()[]", repeat=length):
        text = "".join(marks)
        reduced = text
        while True:
            following = reduced.replace("()", "").replace("[]", "")
            if following == reduced:
                break
            reduced = following
        assert balanced_pairs(text) is (reduced == "")
for text in ("x", "(x)", " ", "[]x"):
    assert balanced(text) is False
    assert balanced_pairs(text) is False
'''
        self.assertEqual(run_code(definitions("08-stacks"), checks), "")

    def test_circular_queue_sequences_against_deque(self):
        checks = '''
from itertools import product
from collections import deque
from copy import deepcopy
assert new_queue(0) is None and new_queue(-1) is None
assert new_queue(2)["data"] is not new_queue(2)["data"]
for capacity in range(1, 5):
    for length in range(8):
        for actions in product(("enqueue-zero", "enqueue-negative", "dequeue"), repeat=length):
            queue = new_queue(capacity)
            model = deque()
            for action in actions:
                before = deepcopy(queue)
                if action == "dequeue":
                    expected = model.popleft() if model else None
                    assert dequeue(queue) == expected
                    if expected is None:
                        assert queue == before
                else:
                    value = 0 if action == "enqueue-zero" else -2
                    allowed = len(model) < capacity
                    assert enqueue(queue, value) is allowed
                    if allowed:
                        model.append(value)
                    else:
                        assert queue == before
                assert len(queue["data"]) == capacity
                assert 0 <= queue["head"] < capacity
                assert queue["size"] == len(model)
                assert queue_values(queue) == list(model)
                occupied = {(queue["head"] + i) % capacity for i in range(queue["size"])}
                assert all(value is None for i, value in enumerate(queue["data"]) if i not in occupied)
                before_peek = deepcopy(queue)
                assert peek_queue(queue) == (model[0] if model else None)
                assert queue == before_peek
'''
        self.assertEqual(run_code(definitions("09-queues"), checks), "")

    def test_queue_batches_after_wrap_and_round_robin_work(self):
        checks = '''
from itertools import product
from collections import deque
for size in range(5):
    for values in product((-1, 0, 2), repeat=size):
        for limit in range(size + 3):
            queue = new_queue(size + 1)
            enqueue(queue, 99)
            assert dequeue(queue) == 99
            for value in values:
                assert enqueue(queue, value) is True
            assert take_from_queue(queue, limit) == list(values[:limit])
            assert queue_values(queue) == list(values[limit:])
for size in range(5):
    for jobs in product((1, 2, 3), repeat=size):
        expected_served = []
        expected_finished = []
        reference = deque(jobs)
        while reference:
            current = reference.popleft()
            expected_served.append(current)
            if current == 1:
                expected_finished.append(len(expected_served))
            else:
                reference.append(current - 1)
        data = list(jobs)
        actual = service_trace(data)
        assert actual == {"served": expected_served, "finished": expected_finished}
        assert len(actual["served"]) == sum(jobs)
        assert len(actual["finished"]) == len(jobs)
        assert data == list(jobs)
'''
        self.assertEqual(run_code(definitions("09-queues"), checks), "")


if __name__ == "__main__":
    unittest.main()
