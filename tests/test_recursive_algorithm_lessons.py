"""Run reviewed recursion lessons and check values, partitions, and actual call depth."""
import ast
import unittest
from pathlib import Path

from cs_study_map.storage import read_json
from cs_study_map.textbook import validate_document
from test_algorithm_lessons import reviewed_tree, run_code, INSTRUMENTS

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ["13-recursion", "14-divide-and-conquer", "15-quick-sort"]


def document(identifier):
    return read_json(ROOT / "catalog/chapters" / (identifier + ".json"))


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


PROFILE = '''
import sys
def observe(function, arguments, names):
    counts = {name: 0 for name in names}
    active = {name: 0 for name in names}
    peaks = {name: 0 for name in names}
    def profile(frame, event, arg):
        name = frame.f_code.co_name
        if name in counts:
            if event == "call":
                counts[name] += 1
                active[name] += 1
                peaks[name] = max(peaks[name], active[name])
            elif event == "return":
                active[name] -= 1
    sys.setprofile(profile)
    try:
        result = function(*arguments)
    finally:
        sys.setprofile(None)
    assert all(value == 0 for value in active.values())
    return result, counts, peaks
'''

GUARDED = '''
class GuardedList(list):
    def __init__(self, values, lo=0, hi=None):
        super().__init__(values)
        self.lo = lo
        self.hi = len(self) if hi is None else hi
        self.writes = 0
    def __getitem__(self, index):
        assert isinstance(index, int) and self.lo <= index < self.hi, "Read outside interval"
        return super().__getitem__(index)
    def __setitem__(self, index, value):
        assert isinstance(index, int) and self.lo <= index < self.hi, "Write outside interval"
        self.writes += 1
        super().__setitem__(index, value)
'''


class RecursiveAlgorithmLessonTests(unittest.TestCase):
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

    def test_factorial_values_and_actual_call_stack(self):
        checks = PROFILE + '''
import math
for n in range(41):
    result, calls, depths = observe(factorial, (n,), {"factorial"})
    assert result == math.factorial(n)
    assert calls["factorial"] == depths["factorial"] == n + 1
'''
        self.assertEqual(run_code(definitions(CHAPTERS[0]), checks), "")

    def test_recursive_list_operations_against_independent_results(self):
        checks = '''
from itertools import product
cases = 0
for size in range(8):
    for source in product((-2, 0, 3), repeat=size):
        data = list(source)
        assert recursive_sum(data) == iterative_sum(data) == sum(source)
        assert recursive_max(data) == (max(source) if source else None)
        assert is_palindrome(data) is (source == source[::-1])
        for target in (-2, 0, 3, 7):
            assert count_equal(data, target) == source.count(target)
        for start in range(size + 1):
            assert sum_from(data, start) == sum(source[start:])
        assert data == list(source)
        cases += 1
assert cases == 3280
'''
        self.assertEqual(run_code(definitions(CHAPTERS[0]), checks), "")

    def test_digit_sum_against_decimal_representation(self):
        checks = '''
cases = list(range(10000))
cases += [10**power + 507 for power in range(4, 41)]
for n in cases:
    assert digit_sum(n) == sum(int(character) for character in str(n))
'''
        self.assertEqual(run_code(definitions(CHAPTERS[0]), checks), "")

    def test_entry_and_return_events_have_matching_local_state(self):
        checks = PROFILE + '''
import math
for n in range(13):
    events = []
    assert factorial_trace(n, events) == math.factorial(n)
    assert events[:n+1] == [["enter", k] for k in range(n, -1, -1)]
    assert events[n+1:] == [["leave", k, math.factorial(k)] for k in range(n+1)]
    stack = []
    for event in events:
        if event[0] == "enter":
            stack.append(event[1])
        else:
            assert stack.pop() == event[1]
    assert not stack
for size in range(65):
    data = [1] * size
    result, calls, depths = observe(recursive_sum, (data,), {"sum_from"})
    assert result == size and calls["sum_from"] == depths["sum_from"] == size + 1
'''
        self.assertEqual(run_code(definitions(CHAPTERS[0]), checks), "")

    def test_fibonacci_total_calls_differ_from_peak_depth(self):
        checks = PROFILE + '''
sequence = [0, 1]
for index in range(17):
    sequence.append(sequence[-1] + sequence[-2])
for n in range(16):
    report, calls, depths = observe(fib_report, (n,), {"fib_report"})
    assert report == {"value": sequence[n], "calls": 2*sequence[n+1]-1}
    assert calls["fib_report"] == report["calls"]
    assert depths["fib_report"] == max(1, n)
'''
        self.assertEqual(run_code(definitions(CHAPTERS[0]), checks), "")

    def test_divide_range_sum_and_positive_count(self):
        checks = GUARDED + '''
from itertools import product
for size in range(6):
    for source in product((-2, 0, 3), repeat=size):
        for lo in range(size + 1):
            for hi in range(lo, size + 1):
                data = GuardedList(source, lo, hi)
                assert split_sum(data, lo, hi) == sum(source[lo:hi])
                assert positive_range(data, lo, hi) == sum(value > 0 for value in source[lo:hi])
                assert data.writes == 0 and list(data) == list(source)
        assert balanced_sum(list(source)) == sum(source)
'''
        self.assertEqual(run_code(definitions(CHAPTERS[1]), checks), "")

    def test_divide_tree_counts_depth_and_actual_merge_writes(self):
        checks = PROFILE + GUARDED + '''
for size in range(257):
    calls_expected = 2*size - 1 if size else 1
    depth_expected = (size - 1).bit_length() + 1 if size else 1
    expected = {"calls": calls_expected, "depth": depth_expected, "leaves": size or 1}
    report, counts, depths = observe(split_report, (0, size), {"split_report"})
    assert report == expected
    assert counts["split_report"] == calls_expected and depths["split_report"] == depth_expected
    source = [(index*37) % 19 - 9 for index in range(size)]
    data = GuardedList(source)
    buffer = GuardedList([0]*size)
    returned, counts, depths = observe(merge_recursive_range, (data, buffer, 0, size), {"merge_recursive_range"})
    assert returned is None and list(data) == sorted(source)
    assert counts["merge_recursive_range"] == calls_expected
    assert depths["merge_recursive_range"] == depth_expected
    height = (size - 1).bit_length() if size else 0
    exact_writes = size*(height+1) - 2**height if size else 0
    assert buffer.writes == data.writes == merge_work(size) == exact_writes
'''
        self.assertEqual(run_code(definitions(CHAPTERS[1]), checks), "")

    def test_recursive_binary_search_matches_bisect_and_stays_in_bounds(self):
        checks = PROFILE + INSTRUMENTS + GUARDED + '''
from itertools import combinations_with_replacement
from bisect import bisect_left
cases = 0
for size in range(11):
    for source in combinations_with_replacement((-2, 0, 3), size):
        for target in (-3, -2, -1, 0, 1, 3, 4):
            data = GuardedList(CountedInt(value) for value in source)
            CountedInt.comparisons = 0
            result, calls, depths = observe(lower_recursive, (data, target, 0, size), {"lower_recursive"})
            comparisons = CountedInt.comparisons
            assert result == bisect_left(source, target)
            assert comparisons <= size.bit_length()
            assert calls["lower_recursive"] == depths["lower_recursive"] == comparisons + 1
            expected = source.index(target) if target in source else -1
            assert recursive_first(GuardedList(source), target) == expected
            assert list(data) == list(source) and data.writes == 0
            cases += 1
assert cases == 2002
'''
        self.assertEqual(run_code(definitions(CHAPTERS[1]), checks), "")

    def test_recursive_merge_and_inversions_against_sorted_and_pairs(self):
        checks = '''
from itertools import product
from collections import Counter
for size in range(8):
    for source in product((-2, 0, 3), repeat=size):
        data = list(source)
        assert merge_sort_recursive(data) is None
        assert data == sorted(source) and Counter(data) == Counter(source)
        original = list(source)
        report = inversion_report(original)
        expected = sum(source[i] > source[j] for i in range(size) for j in range(i+1, size))
        assert report == {"sorted": sorted(source), "inversions": expected}
        assert report["sorted"] is not original and original == list(source)
'''
        self.assertEqual(run_code(definitions(CHAPTERS[1]), checks), "")

    def test_merge_subranges_buffers_and_cross_inversions(self):
        checks = GUARDED + '''
from itertools import product, combinations_with_replacement
for size in range(6):
    for source in product((-2, 0, 3), repeat=size):
        for lo in range(size+1):
            for hi in range(lo, size+1):
                data = GuardedList(source, lo, hi)
                buffer = GuardedList([0]*size, lo, hi)
                merge_recursive_range(data, buffer, lo, hi)
                assert list(data) == list(source[:lo]) + sorted(source[lo:hi]) + list(source[hi:])
parts = [list(values) for size in range(5) for values in combinations_with_replacement((-2, 0, 3), size)]
assert len(parts) == 35
for left in parts:
    for right in parts:
        source = [99] + left + right + [-99]
        lo, middle, hi = 1, 1+len(left), len(source)-1
        data = GuardedList(source, lo, hi)
        buffer = GuardedList([0]*len(source), lo, hi)
        actual = merge_count(data, buffer, lo, middle, hi)
        assert actual == sum(a > b for a in left for b in right)
        assert list(data) == [99] + sorted(left+right) + [-99]
        assert buffer.writes == data.writes == len(left)+len(right)
'''
        self.assertEqual(run_code(definitions(CHAPTERS[1]), checks), "")

    def test_recursive_merge_preserves_equal_item_identity_order(self):
        checks = INSTRUMENTS + '''
from itertools import product
for size in range(7):
    for keys in product((-1, 0, 2), repeat=size):
        records = [TaggedInt(key, index) for index, key in enumerate(keys)]
        expected = sorted(records)
        data = records.copy()
        merge_sort_recursive(data)
        report = inversion_report(records)
        assert len(data) == len(expected) == len(report["sorted"])
        assert all(a is b for a, b in zip(data, expected))
        assert all(a is b for a, b in zip(report["sorted"], expected))
        assert [item.tag for item in records] == list(range(size))
'''
        self.assertEqual(run_code(definitions(CHAPTERS[1]), checks), "")

    def test_fast_power_reuses_exactly_one_half_call(self):
        checks = PROFILE + '''
for base in range(-5, 6):
    for exponent in range(65):
        result, calls, depths = observe(power_fast, (base, exponent), {"power_fast"})
        assert result == pow(base, exponent)
        assert calls["power_fast"] == depths["power_fast"] == exponent.bit_length() + 1
'''
        self.assertEqual(run_code(definitions(CHAPTERS[1]), checks), "")

    def test_sum_trace_has_valid_nested_ranges_and_results(self):
        checks = '''
for size in range(33):
    source = [(index*7)%11 - 5 for index in range(size)]
    events = []
    assert sum_trace(source, 0, size, events) == sum(source)
    stack = []
    leaves = []
    for kind, lo, hi, value in events:
        assert 0 <= lo <= hi <= size
        if kind == "split":
            assert lo < value < hi
            stack.append((lo, hi))
        else:
            assert value == sum(source[lo:hi])
            if kind == "join":
                assert stack.pop() == (lo, hi)
            else:
                assert hi-lo <= 1
                leaves.extend(range(lo, hi))
    assert not stack and leaves == list(range(size))
    assert len(events) == (3*size-2 if size else 1)
'''
        self.assertEqual(run_code(definitions(CHAPTERS[1]), checks), "")

    def test_two_way_partition_contract_identity_and_exact_comparisons(self):
        checks = INSTRUMENTS + GUARDED + '''
from itertools import product
from collections import Counter
for size in range(1, 8):
    for source in product((-2, 0, 3), repeat=size):
        items = [CountedInt(value) for value in source]
        data = GuardedList([99] + items + [-99], 1, size+1)
        pivot = items[-1]
        CountedInt.comparisons = 0
        position = partition_last(data, 1, size+1)
        assert CountedInt.comparisons == size-1
        output = list(data)
        assert 1 <= position < size+1 and output[position] is pivot
        assert all(value < pivot for value in output[1:position])
        assert all(value >= pivot for value in output[position+1:-1])
        assert Counter(map(id, output[1:-1])) == Counter(map(id, items))
        assert output[0] == 99 and output[-1] == -99
'''
        self.assertEqual(run_code(definitions(CHAPTERS[2]), checks), "")

    def test_three_way_partition_invariants_at_every_actual_loop(self):
        code = definitions(CHAPTERS[2])
        loop_line = code.splitlines().index("    while scan < gt:") + 1
        checks = INSTRUMENTS + GUARDED + f"\npartition_loop_line = {loop_line}\n" + '''
import sys
from itertools import product
from collections import Counter
states = []
def trace(frame, event, arg):
    if frame.f_code.co_name == "partition_three" and event == "line" and frame.f_lineno == partition_loop_line:
        local = frame.f_locals
        lo, lt, scan, gt, hi = (local[name] for name in ("lo", "lt", "scan", "gt", "hi"))
        values, pivot = list(local["values"]), local["pivot"]
        assert lo <= lt <= scan <= gt <= hi
        assert all(value < pivot for value in values[lo:lt])
        assert all(value == pivot for value in values[lt:scan])
        assert all(value > pivot for value in values[gt:hi])
        states.append(gt-scan)
    return trace
for size in range(1, 7):
    for source in product((-2, 0, 3), repeat=size):
        items = [TaggedInt(value, index) for index, value in enumerate(source)]
        data = GuardedList([99] + items + [-99], 1, size+1)
        states = []
        sys.settrace(trace)
        try:
            bounds = partition_three(data, 1, size+1)
        finally:
            sys.settrace(None)
        output = list(data)
        lt, gt = bounds["lt"], bounds["gt"]
        assert 1 <= lt < gt <= size+1
        assert states == list(range(size, -1, -1))
        assert all(value < source[-1] for value in output[1:lt])
        assert all(value == source[-1] for value in output[lt:gt])
        assert all(value > source[-1] for value in output[gt:-1])
        assert Counter(map(id, output[1:-1])) == Counter(map(id, items))
        assert output[0] == 99 and output[-1] == -99
'''
        self.assertEqual(run_code(code, checks), "")

    def test_quicksorts_and_copy_interfaces_against_sorted(self):
        checks = '''
from itertools import product, permutations
from collections import Counter
cases = [list(values) for size in range(8) for values in product((-2, 0, 3), repeat=size)]
assert len(cases) == 3280
cases += [list(values) for values in permutations(range(6))]
cases += [list(range(65)), list(range(65, -1, -1)), [4]*67, [10**30, -10**30, 0, 10**30]]
for source in cases:
    for function in (quick_sort, quick_three_sort):
        data = source.copy()
        assert function(data) is None
        assert data == sorted(source) and Counter(data) == Counter(source)
    data = source.copy()
    result = quick_sort_copy(data)
    assert result == sorted(source) and result is not data and data == source
'''
        self.assertEqual(run_code(definitions(CHAPTERS[2]), checks), "")

    def test_quick_reports_match_actual_comparisons_and_stack(self):
        checks = PROFILE + INSTRUMENTS + '''
from itertools import product
cases = [list(values) for size in range(6) for values in product((-2, 0, 3), repeat=size)]
cases += [list(range(size)) for size in range(65)]
cases += [[7]*size for size in range(65)]
for source in cases:
    data = [CountedInt(value) for value in source]
    CountedInt.comparisons = 0
    _, calls, depths = observe(quick_sort, (data,), {"quick_range"})
    comparisons = CountedInt.comparisons
    report = quick_report(source)
    assert report == {"comparisons": comparisons, "depth": depths["quick_range"], "sorted": sorted(source)}
    data = source.copy()
    _, calls, depths = observe(quick_three_sort, (data,), {"quick_three_range", "partition_three"})
    report = quick_three_report(source)
    assert report == {"sorted": sorted(source), "partitions": calls["partition_three"], "depth": depths["quick_three_range"]}
    assert depths["quick_three_range"] <= max(1, len(source).bit_length())
for size in range(129):
    for source in (list(range(size)), list(range(size-1, -1, -1)), [7]*size):
        report = quick_report(source)
        assert report["comparisons"] == size*(size-1)//2
        assert report["depth"] == max(1, size)
    for source in (list(range(size)), [7]*size):
        data = [CountedInt(value) for value in source]
        CountedInt.comparisons = 0
        quick_three_sort(data)
        comparisons = CountedInt.comparisons
        expected = (size*(size+3)//2 - 2) if size >= 2 else 0
        if source == [7]*size:
            expected = 2*size if size >= 2 else 0
        assert comparisons == expected
'''
        self.assertEqual(run_code(definitions(CHAPTERS[2]), checks), "")

    def test_quick_partial_ranges_and_partition_trace_snapshots(self):
        checks = GUARDED + '''
from itertools import product
for size in range(6):
    for source in product((-2, 0, 3), repeat=size):
        for lo in range(size+1):
            for hi in range(lo, size+1):
                expected = list(source[:lo]) + sorted(source[lo:hi]) + list(source[hi:])
                for function in (quick_range, quick_three_range):
                    data = GuardedList(source, lo, hi)
                    function(data, lo, hi)
                    assert list(data) == expected
        if size:
            data = list(source)
            other = list(source)
            report = partition_trace(data, 0, size)
            assert report["pivot"] == partition_last(other, 0, size) and data == other
            assert len(report["steps"]) == size-1
            snapshots = [step[2] for step in report["steps"]]
            assert len({id(snapshot) for snapshot in snapshots}) == size-1
            for scan, boundary, snapshot in report["steps"]:
                assert snapshot is not data and sorted(snapshot) == sorted(source)
                assert all(value < source[-1] for value in snapshot[:boundary])
                assert all(value >= source[-1] for value in snapshot[boundary:scan+1])
                assert snapshot[scan+1:] == list(source[scan+1:])
'''
        self.assertEqual(run_code(definitions(CHAPTERS[2]), checks), "")

    def test_reduced_limit_exposes_long_chains_but_short_side_sort_completes(self):
        checks = '''
import sys
sys.setrecursionlimit(100)
for function, arguments in ((factorial, (200,)), (recursive_sum, ([1]*200,)), (quick_sort, (list(range(200)),))):
    try:
        function(*arguments)
    except RecursionError:
        pass
    else:
        raise AssertionError("Expected a finite but too-deep call chain")
assert iterative_sum([1]*200) == balanced_sum([1]*200) == 200
for source in (list(range(1200)), list(range(1200, -1, -1)), [3]*5000):
    data = source.copy()
    quick_three_sort(data)
    assert data == sorted(source)
'''
        code = "\n".join(definitions(identifier) for identifier in CHAPTERS)
        self.assertEqual(run_code(code, checks), "")

    def test_record_sort_identity_and_instability_counterexample(self):
        checks = '''
from itertools import product
for size in range(7):
    for keys in product((-1, 0, 2), repeat=size):
        records = [{"key": key, "tag": index} for index, key in enumerate(keys)]
        before = [item.copy() for item in records]
        identities = sorted(map(id, records))
        assert quick_keys(records) is None
        assert [item["key"] for item in records] == sorted(keys)
        assert sorted(map(id, records)) == identities
        assert sorted(records, key=lambda item: item["tag"]) == before
records = [{"key": 2, "tag": "R"}, {"key": 1, "tag": "S"}, {"key": 2, "tag": "T"}]
quick_keys(records)
assert [item["tag"] for item in records] == ["S", "T", "R"]
'''
        self.assertEqual(run_code(definitions(CHAPTERS[2]), checks), "")

    def test_selection_ranks_duplicates_invalid_indices_and_input_preservation(self):
        checks = '''
from itertools import product
for size in range(8):
    for source in product((-2, 0, 3), repeat=size):
        data = list(source)
        expected = sorted(source)
        for rank in range(-1, size+1):
            result = kth_smallest_copy(data, rank)
            assert result == (expected[rank] if 0 <= rank < size else None)
            assert data == list(source)
'''
        self.assertEqual(run_code(definitions(CHAPTERS[2]), checks), "")


if __name__ == "__main__":
    unittest.main()
