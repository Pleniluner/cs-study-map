"""Execute reviewed algorithm lessons and compare with independent oracles."""
import ast
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from cs_study_map.storage import read_json
from cs_study_map.textbook import validate_document
from test_data_structures_lessons import NODES

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ["10-algorithm-analysis", "11-searching", "12-sorting"]
METHODS = {"append", "copy", "insert", "sort"}


def document(identifier):
    return read_json(ROOT / "catalog/chapters" / (identifier + ".json"))


def reviewed_tree(code):
    tree = ast.parse(code)
    functions = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
    for node in ast.walk(tree):
        if type(node) not in NODES:
            raise AssertionError("Unreviewed lesson construct: " + type(node).__name__)
        if isinstance(node, ast.Attribute) and node.attr not in METHODS:
            raise AssertionError("Unreviewed lesson attribute")
        if isinstance(node, ast.Call):
            name_ok = isinstance(node.func, ast.Name) and node.func.id in functions | {"print", "range", "len", "sorted"}
            method_ok = isinstance(node.func, ast.Attribute) and node.func.attr in METHODS
            if not (name_ok or method_ok):
                raise AssertionError("Unreviewed lesson call")
    return tree


def run_code(code, checks=""):
    reviewed_tree(code)
    with tempfile.TemporaryDirectory() as directory:
        result = subprocess.run(
            [sys.executable, "-I", "-S", "-X", "utf8", "-c", code + "\n" + checks],
            cwd=directory, capture_output=True, text=True, encoding="utf-8", timeout=15,
        )
    if result.returncode:
        raise AssertionError(result.stderr)
    return result.stdout


def definitions(identifier):
    functions = {}
    content = document(identifier)["content"]
    for group in ("sections", "worked_examples", "exercises"):
        for item in content[group]:
            code = item["program"]["code"]
            for node in reviewed_tree(code).body:
                if isinstance(node, ast.FunctionDef):
                    source = ast.get_source_segment(code, node)
                    if node.name in functions and functions[node.name] != source:
                        raise AssertionError("Inconsistent copies of helper: " + node.name)
                    functions[node.name] = source
    return "\n\n".join(functions.values()) + "\n"


INSTRUMENTS = '''
class CountedInt(int):
    comparisons = 0
    def __lt__(self, other):
        CountedInt.comparisons += 1
        return int(self) < int(other)
    def __le__(self, other):
        CountedInt.comparisons += 1
        return int(self) <= int(other)
    def __gt__(self, other):
        CountedInt.comparisons += 1
        return int(self) > int(other)

class TaggedInt(int):
    def __new__(cls, key, tag):
        item = int.__new__(cls, key)
        item.tag = tag
        return item

class CheckedIndices(list):
    def __getitem__(self, index):
        assert isinstance(index, int) and 0 <= index < len(self), "Invalid search index"
        return super().__getitem__(index)
'''


class AlgorithmLessonTests(unittest.TestCase):
    def test_all_thirty_literal_programs_match_exact_output(self):
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
        self.assertEqual(count, 30)

    def test_exact_loop_counts_against_closed_formulas(self):
        checks = '''
for n in range(129):
    report = loop_counts(n)
    assert report == {"sequential": 2*n, "square": n*n, "triangle": n*(n-1)//2}
    assert scan_then_pairs(n) == {"scan": n, "pairs": n*(n-1)//2, "total": n*(n+1)//2}
    assert fixed_width(n) == 3*n
    assert linear_model(n) == 3*n + 7 and quadratic_model(n) == n*n
    if n >= 1:
        assert 3*n <= linear_model(n) <= 10*n
'''
        self.assertEqual(run_code(definitions(CHAPTERS[0]), checks), "")

    def test_halving_and_doubling_near_powers_of_two(self):
        checks = '''
cases = set(range(257))
for exponent in range(1, 12):
    cases.update((2**exponent - 1, 2**exponent, 2**exponent + 1))
for n in sorted(cases):
    assert half_steps(n) == max(0, n.bit_length() - 1)
    rounds = (n - 1).bit_length() if n >= 1 else 0
    assert full_pass_work(n) == {"rounds": rounds, "visits": n*rounds}
'''
        self.assertEqual(run_code(definitions(CHAPTERS[0]), checks), "")

    def test_list_counts_prefix_sums_and_shared_cursor_batches(self):
        checks = '''
from itertools import product, accumulate
for size in range(6):
    for values in product((-2, 0, 3), repeat=size):
        data = list(values)
        assert positive_report(data) == {"positive": sum(v > 0 for v in values), "checks": size}
        result = prefix_totals(data)
        assert result == list(accumulate(values)) and result is not data
        for target in (-2, 0, 3, 7):
            expected = values.index(target) if target in values else -1
            assert first_report(data, target) == {"index": expected, "checks": expected + 1 if expected >= 0 else size}
        assert data == list(values)
for n in range(129):
    for batch_size in range(1, 33):
        assert consume_batches(n, batch_size) == {"batches": (n + batch_size - 1)//batch_size, "visits": n}
'''
        self.assertEqual(run_code(definitions(CHAPTERS[0]), checks), "")

    def test_binary_bounds_first_and_last_against_bisect(self):
        checks = '''
from itertools import combinations_with_replacement
from bisect import bisect_left, bisect_right
cases = 0
for size in range(9):
    for values in combinations_with_replacement((-3, 0, 2), size):
        data = list(values)
        for target in (-4, -3, -1, 0, 1, 2, 3):
            left = bisect_left(values, target)
            right = bisect_right(values, target)
            assert lower_bound(data, target) == left
            assert upper_bound(data, target) == right
            matches = [i for i, value in enumerate(values) if value == target]
            assert binary_first(data, target) == (matches[0] if matches else -1)
            assert binary_last(data, target) == (matches[-1] if matches else -1)
            assert right - left == len(matches)
            assert data == list(values)
            cases += 1
assert cases == 1155
'''
        self.assertEqual(run_code(definitions(CHAPTERS[1]), checks), "")

    def test_binary_actual_comparisons_and_no_invalid_index(self):
        checks = INSTRUMENTS + '''
from bisect import bisect_left, bisect_right
for size in range(129):
    plain = [2*i - size for i in range(size)]
    maximum = 0
    for target in range(-size - 1, size + 2):
        for function, oracle in ((lower_bound, bisect_left), (upper_bound, bisect_right)):
            data = CheckedIndices(CountedInt(v) for v in plain)
            CountedInt.comparisons = 0
            result = function(data, target)
            actual = CountedInt.comparisons
            assert result == oracle(plain, target)
            assert actual <= size.bit_length()
            maximum = max(maximum, actual)
        guarded = CheckedIndices(plain)
        matching = [i for i, value in enumerate(plain) if value == target]
        assert binary_first(guarded, target) == (matching[0] if matching else -1)
        assert binary_last(guarded, target) == (matching[-1] if matching else -1)
    assert maximum == size.bit_length()
'''
        self.assertEqual(run_code(definitions(CHAPTERS[1]), checks), "")

    def test_trace_invariants_and_strict_shrinkage(self):
        checks = '''
from bisect import bisect_left
for size in range(65):
    values = [i//3 - 5 for i in range(size)]
    for target in range(-6, 19):
        report = lower_trace(values, target)
        assert report["position"] == bisect_left(values, target)
        assert len(report["trace"]) <= size.bit_length()
        previous_length = size + 1
        for left, right, middle, value in report["trace"]:
            assert 0 <= left <= middle < right <= size
            assert right - left < previous_length
            assert value == values[middle]
            assert all(v < target for v in values[:left])
            assert all(v >= target for v in values[right:])
            previous_length = right - left
'''
        self.assertEqual(run_code(definitions(CHAPTERS[1]), checks), "")

    def test_search_preconditions_queries_ranges_and_inserted_copy(self):
        checks = '''
from itertools import product, combinations_with_replacement
for size in range(6):
    for values in product((-1, 0, 2), repeat=size):
        data = list(values)
        ordered = data == sorted(data)
        assert is_nondecreasing(data) is ordered
        targets = [-1, 3, 0, -1]
        expected = [values.index(t) if t in values else -1 for t in targets]
        assert checked_queries(data, targets) == (expected if ordered else None)
        for target in targets:
            assert linear_first(data, target) == (values.index(target) if target in values else -1)
        assert checked_queries(data, []) == ([] if ordered else None)
        assert data == list(values)
for size in range(7):
    for values in combinations_with_replacement((-3, 0, 2), size):
        data = list(values)
        for low in range(-4, 4):
            for high in range(-4, 4):
                assert count_closed_range(data, low, high) == sum(low <= v <= high for v in values)
            result = inserted_copy(data, low)
            assert result == sorted(list(values) + [low]) and result is not data
        assert data == list(values)
'''
        self.assertEqual(run_code(definitions(CHAPTERS[1]), checks), "")

    def test_all_sorters_against_sorted_and_multisets(self):
        checks = '''
from itertools import product
from collections import Counter
cases = [list(values) for size in range(8) for values in product((-2, 0, 3), repeat=size)]
assert len(cases) == 3280
cases += [list(range(65)), list(range(65, -1, -1)), [4]*67, [10**30, -10**30, 0, 10**30]]
for source in cases:
    expected = sorted(source)
    for function in (selection_sort, insertion_sort, bubble_sort):
        data = source.copy()
        alias = data
        returned = function(data)
        assert data == expected and Counter(data) == Counter(source) and data is alias
        if function is not bubble_sort:
            assert returned is None
        else:
            assert 0 <= returned <= len(source)*(len(source)-1)//2
    data = source.copy()
    result = merge_sort(data)
    assert result == expected and Counter(result) == Counter(source)
    assert result is not data and data == source
'''
        self.assertEqual(run_code(definitions(CHAPTERS[2]), checks), "")

    def test_actual_sort_comparison_counts(self):
        checks = INSTRUMENTS + '''
for size in range(65):
    for plain in (list(range(size)), list(range(size - 1, -1, -1)), [4]*size):
        values = [CountedInt(v) for v in plain]
        CountedInt.comparisons = 0
        selection_sort(values)
        assert CountedInt.comparisons == size*(size-1)//2
        values = [CountedInt(v) for v in plain]
        CountedInt.comparisons = 0
        insertion_sort(values)
        expected = max(0, size - 1) if plain == sorted(plain) else size*(size-1)//2
        assert CountedInt.comparisons == expected
        values = [CountedInt(v) for v in plain]
        CountedInt.comparisons = 0
        reported = bubble_sort(values)
        assert reported == CountedInt.comparisons == expected
        values = [CountedInt(v) for v in plain]
        CountedInt.comparisons = 0
        result = merge_sort(values)
        rounds = (size - 1).bit_length() if size else 0
        assert CountedInt.comparisons <= size*rounds
        assert result == sorted(plain)
'''
        self.assertEqual(run_code(definitions(CHAPTERS[2]), checks), "")

    def test_insertion_moves_equal_inversions_and_snapshots_are_distinct(self):
        checks = '''
from itertools import product
for size in range(7):
    for source in product((-2, 0, 3), repeat=size):
        data = list(source)
        report = insertion_report(data)
        inversions = sum(source[i] > source[j] for i in range(size) for j in range(i + 1, size))
        assert report["moves"] == inversions and data == sorted(source)
        states = report["states"]
        assert len(states) == max(0, size - 1)
        assert len({id(state) for state in states}) == len(states)
        for count, state in enumerate(states, 2):
            assert state == sorted(source[:count]) + list(source[count:])
            assert state is not data
'''
        self.assertEqual(run_code(definitions(CHAPTERS[2]), checks), "")

    def test_merge_unequal_and_empty_inputs_with_comparison_bound(self):
        checks = INSTRUMENTS + '''
from itertools import combinations_with_replacement
cases = [list(values) for size in range(6) for values in combinations_with_replacement((-2, 0, 3), size)]
assert len(cases) == 56
for left in cases:
    for right in cases:
        a = [CountedInt(v) for v in left]
        b = [CountedInt(v) for v in right]
        CountedInt.comparisons = 0
        result = merge_sorted(a, b)
        actual = CountedInt.comparisons
        assert actual <= len(a)+len(b)-1 if a and b else actual == 0
        assert result == sorted(left + right)
        assert result is not a and result is not b
        assert a == left and b == right
'''
        self.assertEqual(run_code(definitions(CHAPTERS[2]), checks), "")

    def test_stability_of_actual_sorters_and_selection_counterexample(self):
        checks = INSTRUMENTS + '''
from itertools import product
for size in range(7):
    for keys in product((-1, 0, 2), repeat=size):
        records = [TaggedInt(key, index) for index, key in enumerate(keys)]
        expected = sorted(records)
        for function in (insertion_sort, bubble_sort, merge_sort):
            data = records.copy()
            returned = function(data)
            ordered = returned if function is merge_sort else data
            assert all(a is b for a, b in zip(ordered, expected))
            assert len(ordered) == len(expected)
        records_as_dicts = [{"key": key, "tag": index} for index, key in enumerate(keys)]
        before = [record.copy() for record in records_as_dicts]
        ordered = stable_by_key(records_as_dicts)
        expected_dicts = sorted(records_as_dicts, key=lambda record: record["key"])
        assert all(a is b for a, b in zip(ordered, expected_dicts))
        assert ordered is not records_as_dicts and records_as_dicts == before
        assert record_tags(ordered) == [record["tag"] for record in expected_dicts]
records = [TaggedInt(2, "R"), TaggedInt(2, "T"), TaggedInt(1, "S")]
selection_sort(records)
assert [item.tag for item in records] == ["S", "T", "R"]
left = [TaggedInt(1, "L1"), TaggedInt(2, "L2")]
right = [TaggedInt(1, "R1"), TaggedInt(2, "R2")]
assert [item.tag for item in merge_sorted(left, right)] == ["L1", "R1", "L2", "R2"]
shared = {"key": 2, "tag": "X"}
assert all(item is shared for item in stable_by_key([shared, shared]))
'''
        self.assertEqual(run_code(definitions(CHAPTERS[2]), checks), "")

    def test_merge_passes_at_irregular_lengths_and_powers(self):
        checks = '''
sizes = set(range(18))
for exponent in range(1, 10):
    sizes.update((2**exponent - 1, 2**exponent, 2**exponent + 1))
for size in sorted(sizes):
    source = [(i*37) % 23 - 11 for i in range(size)]
    current = source.copy()
    width = 1
    rounds = 0
    while width < size:
        before = current.copy()
        following = merge_pass(current, width)
        expected = []
        for start in range(0, size, 2*width):
            expected.extend(sorted(before[start:start + 2*width]))
        assert following == expected and len(following) == size
        assert current == before and following is not current
        current = following
        width *= 2
        rounds += 1
    assert rounds == ((size - 1).bit_length() if size else 0)
    assert current == merge_sort(source) == sorted(source)
'''
        self.assertEqual(run_code(definitions(CHAPTERS[2]), checks), "")

    def test_sorted_lookup_uses_sorted_positions_and_keeps_input(self):
        checks = '''
from itertools import product
for size in range(6):
    for source in product((-2, 0, 3), repeat=size):
        ordered = sorted(source)
        data = list(source)
        for target in (-3, -2, 0, 1, 3, 4):
            expected = ordered.index(target) if target in ordered else -1
            result = sorted_lookup(data, target)
            assert result == {"sorted": ordered, "index": expected}
            assert result["sorted"] is not data
            assert data == list(source)
'''
        self.assertEqual(run_code(definitions(CHAPTERS[2]), checks), "")


if __name__ == "__main__":
    unittest.main()
