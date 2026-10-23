"""Execute literal lessons; compare with exhaustive intervals and direct arrays."""

import unittest

from cs_study_map.textbook import validate_document
from test_data_structures_lessons import definitions, document, reviewed_tree, run_code

MONOTONIC = "34-monotonic-structures"
FENWICK = "35-fenwick-tree"
SEGMENT = "36-segment-tree"

COMMON = r'''
import copy
import itertools
import random

def arrays(alphabet, maximum):
    for n in range(maximum + 1):
        for sequence in itertools.product(alphabet, repeat=n):
            yield list(sequence)

def intervals(n, empty=False):
    return [(i, j) for i in range(n + 1)
            for j in range(i if empty else i + 1, n + 1)]

def stats_of(values):
    return {'sum': sum(values), 'minimum': min(values, default=None), 'length': len(values)}

def inspect_bit(state, values):
    assert state['size'] == len(values)
    assert len(state['tree']) == len(values) + 1 and state['tree'][0] == 0
    for i in range(1, len(values) + 1):
        # Find the block width by divisibility, independently of lowbit code.
        width = 1
        while i % (2 * width) == 0:
            width *= 2
        assert state['tree'][i] == sum(values[i - width:i]), (i, values, state)

def inspect_segment(state, values):
    assert state['size'] == len(values)
    assert len({id(node) for node in state['nodes']}) == len(state['nodes'])
    def visit(node, low, high):
        assert state['nodes'][node] == stats_of(values[low:high])
        if high - low > 1:
            middle = (low + high) // 2
            visit(2 * node, low, middle)
            visit(2 * node + 1, middle, high)
    visit(1, 0, state['base'])

def inspect_lazy(state, values):
    assert state['size'] == len(values)
    def visit(node, low, high, inherited):
        assert state['sum'][node] + inherited * (high - low) == sum(values[low:high])
        if high - low > 1:
            assert state['sum'][node] == (state['sum'][2 * node]
                + state['sum'][2 * node + 1] + state['add'][node] * (high - low))
            middle = (low + high) // 2
            inherited += state['add'][node]
            visit(2 * node, low, middle, inherited)
            visit(2 * node + 1, middle, high, inherited)
    if values:
        visit(1, 0, len(values), 0)

def maxsum_of(values):
    return {'sum': sum(values),
            'prefix': max(sum(values[:i]) for i in range(len(values) + 1)),
            'suffix': max(sum(values[i:]) for i in range(len(values) + 1)),
            'best': max(sum(values[i:j]) for i, j in intervals(len(values), True))}
'''


class RangeStructuresLessonTests(unittest.TestCase):
    def check(self, chapter, checks):
        self.assertEqual(run_code(definitions(chapter), COMMON + checks), "")

    def test_all_thirty_published_programs_match_exact_output(self):
        count = 0
        for identifier in (MONOTONIC, FENWICK, SEGMENT):
            saved = document(identifier)
            validate_document(saved)
            for group, length in (("sections", 5), ("worked_examples", 2), ("exercises", 3)):
                self.assertEqual(len(saved["content"][group]), length)
                for index, item in enumerate(saved["content"][group]):
                    with self.subTest(chapter=identifier, group=group, item=index):
                        program = item["program"]
                        self.assertEqual(run_code(program["code"]), program["output"])
                        count += 1
        self.assertEqual(count, 30)

    def test_bitand_review_keeps_import_calls_and_attributes_restricted(self):
        reviewed_tree("i = 12\nprint(i & -i)\n")
        for code in ("import os", "open('x')", "__import__('os')", "x.__class__", "eval('1')"):
            with self.subTest(code=code), self.assertRaises(AssertionError):
                reviewed_tree(code)

    def test_next_greater_against_rightward_search(self):
        self.check(MONOTONIC, r'''
for values in arrays((-1, 0, 2), 7):
    original = values.copy()
    expected = [next((j for j in range(i + 1, len(values)) if values[j] > value), None)
                for i, value in enumerate(values)]
    assert next_greater(values) == expected and values == original
''')

    def test_previous_smaller_against_leftward_search(self):
        self.check(MONOTONIC, r'''
for values in arrays((-2, 0, 1), 7):
    expected = [next((j for j in range(i - 1, -1, -1) if values[j] < value), None)
                for i, value in enumerate(values)]
    assert previous_smaller(values) == expected
''')

    def test_histogram_against_all_interval_minima(self):
        self.check(MONOTONIC, r'''
for values in arrays((0, 1, 3), 7):
    original = values.copy()
    expected = max([0] + [(j - i) * min(values[i:j]) for i, j in intervals(len(values))])
    assert histogram_area(values) == expected and values == original
for values in [[-1], [0, -1, 5], [3, 2, -1]]:
    original = values.copy()
    assert histogram_area(values) is None and values == original
''')

    def test_window_maximum_latest_ties_and_ring_wrap(self):
        self.check(MONOTONIC, r'''
for values in arrays((-1, 0, 2), 6):
    for width in range(-1, len(values) + 2):
        expected = None
        if 1 <= width <= len(values):
            expected = [max(range(i, i + width), key=lambda j: (values[j], j))
                        for i in range(len(values) - width + 1)]
        assert window_max_indices(values, width) == expected
values = [8, 7, 6, 5, 4, 3, 2, 1] * 20
for width in [1, 2, 3, 7, 8, 9, 17]:
    assert window_max_indices(values, width) == [
        max(range(i, i + width), key=lambda j: (values[j], j))
        for i in range(len(values) - width + 1)]
''')

    def test_signed_shortest_against_all_nonempty_intervals(self):
        self.check(MONOTONIC, r'''
for values in arrays((-2, 0, 3), 6):
    candidates = [(i, j, sum(values[i:j])) for i, j in intervals(len(values))]
    original = values.copy()
    for target in range(-3, 8):
        best = min(((i, j) for i, j, total in candidates if total >= target),
                   key=lambda pair: (pair[1] - pair[0], pair[0]), default=None)
        assert shortest_signed_window(values, target) == ([] if best is None else list(best))
    assert values == original
''')

    def test_matrix_rectangles_against_all_four_boundaries(self):
        self.check(MONOTONIC, r'''
for height in range(4):
    for width in range(4):
        for flat in itertools.product((0, 1), repeat=height * width):
            rows = [list(flat[r * width:(r + 1) * width]) for r in range(height)]
            before = copy.deepcopy(rows)
            expected = max([0] + [(bottom - top) * (right - left)
                for top, bottom in intervals(height) for left, right in intervals(width)
                if all(rows[r][c] == 1 for r in range(top, bottom) for c in range(left, right))])
            assert ones_rectangle(rows) == expected and rows == before
for rows in [[[1], []], [[], [1]], [[1, 2]], [[-1]], [[0], [1, 0]]]:
    before = copy.deepcopy(rows)
    assert ones_rectangle(rows) is None and rows == before
''')

    def test_spans_against_direct_backward_scan(self):
        self.check(MONOTONIC, r'''
for values in arrays((-1, 0, 2), 7):
    expected = []
    for i, value in enumerate(values):
        start = i
        while start > 0 and values[start - 1] <= value:
            start -= 1
        expected.append(i - start + 1)
    assert upper_bounded_span(values) == expected
assert upper_bounded_span([3, 1, 2, 4]) == [1, 1, 2, 4]
''')

    def test_circular_next_against_one_complete_lap(self):
        self.check(MONOTONIC, r'''
for values in arrays((-1, 0, 2), 7):
    n = len(values)
    expected = [next(((i + distance) % n for distance in range(1, n)
                      if values[(i + distance) % n] > values[i]), None) for i in range(n)]
    assert circular_next_greater(values) == expected
''')

    def test_window_spreads_against_literal_extrema(self):
        self.check(MONOTONIC, r'''
for values in arrays((-3, 0, 2), 6):
    original = values.copy()
    for width in range(-1, len(values) + 2):
        expected = None if not 1 <= width <= len(values) else [
            max(values[i:i + width]) - min(values[i:i + width])
            for i in range(len(values) - width + 1)]
        assert window_spreads(values, width) == expected
    assert values == original
''')

    def test_bounded_maximum_against_sorted_interval_candidates(self):
        self.check(MONOTONIC, r'''
for values in arrays((-2, 0, 3), 6):
    original = values.copy()
    for limit in range(-1, len(values) + 3):
        options = [(sum(values[i:j]), i, j) for i, j in intervals(len(values)) if j - i <= limit]
        best = min(options, key=lambda row: (-row[0], row[1], row[2]), default=None)
        expected = None if best is None else dict(zip(('sum', 'start', 'stop'), best))
        assert bounded_max_sum(values, limit) == expected
    assert values == original
''')

    def test_monotonic_large_inputs_and_big_integers(self):
        self.check(MONOTONIC, r'''
class Indexed(list):
    def __init__(self, values):
        super().__init__(values)
        self.reads = 0
    def __getitem__(self, index):
        self.reads += 1
        return super().__getitem__(index)
n = 10000
for sequence in [list(range(n)), list(range(n, 0, -1)), [7] * n]:
    values = Indexed(sequence)
    next_greater(values)
    previous_smaller(values)
    histogram_area(values)
    window_max_indices(values, 137)
    circular_next_greater(values)
    upper_bounded_span(values)
    assert values.reads < 55 * n
big = 10 ** 120
assert histogram_area([big, big]) == 2 * big
assert shortest_signed_window([-big, big, big], 2 * big) == [1, 3]
assert bounded_max_sum([-big, big, big], 2) == {'sum': 2 * big, 'start': 1, 'stop': 3}
assert shortest_signed_window([0] * n, 1) == []
assert bounded_max_sum([0] * n, n) == {'sum': 0, 'start': 0, 'stop': 1}
''')

    def test_lowbit_blocks_partition_and_divisibility(self):
        self.check(FENWICK, r'''
assert prefix_blocks(-1) is None
for stop in range(1025):
    blocks = prefix_blocks(stop)
    assert [i for left, right in reversed(blocks) for i in range(left, right)] == list(range(stop))
    for left, right in blocks:
        width = right - left
        assert width > 0 and width & (width - 1) == 0
        assert right % width == 0 and right % (2 * width) != 0
assert prefix_blocks(2 ** 200) == [[0, 2 ** 200]]
''')

    def test_fenwick_build_each_block_against_direct_sums(self):
        self.check(FENWICK, r'''
for values in arrays((-2, 0, 3), 6):
    original = values.copy()
    state = fenwick_build(values)
    inspect_bit(state, values)
    for start, stop in intervals(len(values), True):
        assert fenwick_range(state, start, stop) == sum(values[start:stop])
    assert values == original
    if values:
        values[0] += 100
        inspect_bit(state, original)
''')

    def test_fenwick_interleaved_add_set_against_direct_array(self):
        self.check(FENWICK, r'''
rng = random.Random(3501)
for n in [1, 2, 3, 5, 8, 17, 33]:
    model = [0] * n
    state = fenwick_new(n)
    for step in range(120):
        index, value = rng.randrange(n), rng.randrange(-20, 21)
        if step % 2:
            assert fenwick_set(state, index, value)
            model[index] = value
        else:
            assert fenwick_add(state, index, value)
            model[index] += value
        inspect_bit(state, model)
        for stop in range(n + 1):
            assert fenwick_prefix(state, stop) == sum(model[:stop])
        start, stop = sorted([rng.randrange(n + 1), rng.randrange(n + 1)])
        assert fenwick_range(state, start, stop) == sum(model[start:stop])
big = 10 ** 150
state = fenwick_build([big, -big, 1])
assert fenwick_set(state, 1, big) and fenwick_range(state, 0, 3) == 2 * big + 1
''')

    def test_fenwick_invalid_requests_are_atomic(self):
        self.check(FENWICK, r'''
assert fenwick_new(-1) is None
for n in range(6):
    state = fenwick_build(list(range(n)))
    before = copy.deepcopy(state)
    for index in [-2, -1, n, n + 1]:
        assert fenwick_add(state, index, 99) is False
        assert fenwick_set(state, index, 99) is False
        assert state == before
    for stop in [-1, n + 1]:
        assert fenwick_prefix(state, stop) is None
    for start, stop in [(-1, n), (0, n + 1), (1, 0), (n + 1, n + 1)]:
        assert fenwick_range(state, start, stop) is None
    assert state == before and fenwick_range(state, n, n) == 0
''')

    def test_frequency_selection_against_expanded_small_multisets(self):
        self.check(FENWICK, r'''
assert frequency_new([0, -1, 2]) is None
for counts in arrays((0, 1, 2), 6):
    original = counts.copy()
    state = frequency_new(counts)
    expanded = [i for i, count in enumerate(counts) for _ in range(count)]
    for rank in range(-1, len(expanded) + 3):
        expected = expanded[rank - 1] if 1 <= rank <= len(expanded) else None
        assert frequency_select(state, rank) == expected
    assert counts == original
''')

    def test_frequency_updates_preserve_nonnegative_contract(self):
        self.check(FENWICK, r'''
rng = random.Random(3502)
for n in range(9):
    counts = [rng.randrange(4) for _ in range(n)]
    original = counts.copy()
    state = frequency_new(counts)
    model = counts.copy()
    for _ in range(100):
        index, delta = rng.randrange(-1, n + 1), rng.randrange(-5, 6)
        before = copy.deepcopy(state)
        allowed = 0 <= index < n and model[index] + delta >= 0
        assert frequency_change(state, index, delta) is allowed
        if allowed:
            model[index] += delta
        else:
            assert state == before
        assert state['counts'] == model and counts == original
        inspect_bit(state['bit'], model)
        for rank in [0, 1, sum(model), sum(model) + 1]:
            expected = next((i for i in range(n) if sum(model[:i + 1]) >= rank), None) if rank > 0 else None
            assert frequency_select(state, rank) == expected
    assert state['counts'] is not counts
''')

    def test_difference_ranges_against_elementwise_addition(self):
        self.check(FENWICK, r'''
rng = random.Random(3503)
for n in range(12):
    initial = [rng.randrange(-4, 5) for _ in range(n)]
    model = initial.copy()
    state = difference_new(initial)
    for _ in range(70):
        start, stop = sorted([rng.randrange(n + 1), rng.randrange(n + 1)])
        delta = rng.randrange(-5, 6)
        assert difference_add(state, start, stop, delta)
        for i in range(start, stop):
            model[i] += delta
        assert [difference_point(state, i) for i in range(n)] == model
        differences = [model[i] - (model[i - 1] if i else 0) for i in range(n)]
        differences.append(-model[-1] if n else 0)
        inspect_bit(state['bit'], differences)
    before = copy.deepcopy(state)
    for start, stop in [(-1, n), (0, n + 1), (1, 0)]:
        assert difference_add(state, start, stop, 3) is False and state == before
    assert difference_point(state, -1) is None and difference_point(state, n) is None
    assert state['bit']['tree'] is not initial
''')

    def test_inversions_against_all_ordered_position_pairs(self):
        self.check(FENWICK, r'''
coordinates = [-5, -2, 0, 3, 9]
for values in arrays((-2, 0, 3), 7):
    before = values.copy()
    expected = sum(values[i] > values[j] for i in range(len(values)) for j in range(i + 1, len(values)))
    assert inversion_count(values, coordinates) == expected and values == before
for coordinates in [[1, 1], [2, 1], [0, 2, 1]]:
    assert inversion_count([], coordinates) is None
assert inversion_count([2], [1, 3]) is None
assert inversion_count([2], []) is None
assert inversion_count([], []) == 0
''')

    def test_dual_ranges_against_all_direct_interval_sums(self):
        self.check(FENWICK, r'''
rng = random.Random(3504)
for n in range(11):
    initial = [rng.randrange(-5, 6) for _ in range(n)]
    model = initial.copy()
    state = dual_new(initial)
    for _ in range(45):
        start, stop = sorted([rng.randrange(n + 1), rng.randrange(n + 1)])
        delta = rng.randrange(-9, 10)
        assert dual_add(state, start, stop, delta)
        for i in range(start, stop):
            model[i] += delta
        for left, right in intervals(n, True):
            assert dual_range(state, left, right) == sum(model[left:right])
        assert dual_prefix(state, n) == sum(model)
        differences = [model[i] - (model[i - 1] if i else 0) for i in range(n)]
        differences.append(-model[-1] if n else 0)
        inspect_bit(state['plain'], differences)
        inspect_bit(state['weighted'], [i * value for i, value in enumerate(differences)])
    before = copy.deepcopy(state)
    for start, stop in [(-1, n), (0, n + 1), (1, 0)]:
        assert dual_add(state, start, stop, 3) is False
        assert dual_range(state, start, stop) is None and state == before
    assert dual_prefix(state, -1) is None and dual_prefix(state, n + 1) is None
''')

    def test_median_buckets_small_and_unexpanded_huge_counts(self):
        self.check(FENWICK, r'''
for counts in arrays((0, 1, 2), 6):
    expanded = [i for i, count in enumerate(counts) for _ in range(count)]
    expected = [] if not expanded else [expanded[(len(expanded) - 1) // 2], expanded[len(expanded) // 2]]
    assert median_buckets(frequency_new(counts)) == expected
big = 10 ** 200
state = frequency_new([0, big, 0, big])
assert median_buckets(state) == [1, 3]
assert frequency_change(state, 3, 1) and median_buckets(state) == [3, 3]
assert frequency_select(state, 2 * big + 1) == 3
''')

    def test_stats_identity_associativity_and_no_aliases(self):
        self.check(SEGMENT, r'''
summaries = [stats_of(values) for values in arrays((-2, 0, 3), 2)]
for a, b, c in itertools.product(summaries, repeat=3):
    assert stats_merge(stats_merge(a, b), c) == stats_merge(a, stats_merge(b, c))
for a in summaries:
    empty = stats_empty()
    before = copy.deepcopy(a)
    result = stats_merge(a, empty)
    assert result == a == stats_merge(empty, a)
    assert result is not a and result is not empty
    result['minimum'] = 999
    assert a == before
''')

    def test_segment_build_all_nodes_and_input_independence(self):
        self.check(SEGMENT, r'''
for values in arrays((-2, 0, 3), 5):
    original = values.copy()
    state = segment_build(values)
    inspect_segment(state, values)
    if values:
        values[0] += 100
        inspect_segment(state, original)
assert segment_build([5, 2, 7])['nodes'][1]['minimum'] == 2
''')

    def test_segment_set_path_against_array_and_atomic_failures(self):
        self.check(SEGMENT, r'''
rng = random.Random(3601)
for n in range(13):
    model = [rng.randrange(-9, 10) for _ in range(n)]
    original = model.copy()
    input_snapshot = original.copy()
    state = segment_build(original)
    for _ in range(90):
        index, value = rng.randrange(-1, n + 1), rng.randrange(-20, 21)
        before = copy.deepcopy(state)
        assert segment_set(state, index, value) is (0 <= index < n)
        if 0 <= index < n:
            model[index] = value
        else:
            assert state == before
        inspect_segment(state, model)
    assert original == input_snapshot
''')

    def test_segment_queries_all_ranges_and_return_independence(self):
        self.check(SEGMENT, r'''
for values in arrays((-2, 0, 3), 5):
    state = segment_build(values)
    before = copy.deepcopy(state)
    for start, stop in intervals(len(values), True):
        result = segment_query(state, start, stop)
        assert result == stats_of(values[start:stop])
        result['minimum'] = 999
        assert state == before
    for start, stop in [(-1, 0), (0, len(values) + 1), (1, 0)]:
        assert segment_query(state, start, stop) is None
''')

    def test_lazy_interleaved_updates_queries_and_internal_invariant(self):
        self.check(SEGMENT, r'''
rng = random.Random(3602)
for n in [0, 1, 2, 3, 5, 8, 11, 17]:
    model = [rng.randrange(-10, 11) for _ in range(n)]
    state = lazy_new(model)
    for step in range(100):
        start, stop = sorted([rng.randrange(n + 1), rng.randrange(n + 1)])
        if step % 3:
            delta = rng.randrange(-10, 11)
            assert lazy_add(state, start, stop, delta)
            for i in range(start, stop):
                model[i] += delta
        else:
            assert lazy_sum(state, start, stop) == sum(model[start:stop])
        inspect_lazy(state, model)
    for start, stop in intervals(n, True):
        assert lazy_sum(state, start, stop) == sum(model[start:stop])
    inspect_lazy(state, model)
''')

    def test_lazy_empty_invalid_and_independent_instances(self):
        self.check(SEGMENT, r'''
for n in range(6):
    values = list(range(n))
    state = lazy_new(values)
    other = lazy_new(values)
    before = copy.deepcopy(state)
    for start, stop in [(-1, n), (0, n + 1), (1, 0)]:
        assert lazy_add(state, start, stop, 3) is False
        assert lazy_sum(state, start, stop) is None and state == before
    for i in range(n + 1):
        assert lazy_add(state, i, i, 999) is True
        assert lazy_sum(state, i, i) == 0 and state == before
    lazy_add(state, 0, n, 4)
    assert other == before and values == list(range(n))
''')

    def test_lazy_push_changes_representation_without_losing_values(self):
        self.check(SEGMENT, r'''
state = lazy_new([2, -1, 4, 0])
assert lazy_add(state, 0, 4, 3)
assert [state['sum'][1], state['add'][1], state['sum'][2], state['sum'][3]] == [17, 3, 1, 4]
before = copy.deepcopy(state)
assert lazy_sum(state, 0, 1) == 5 and state != before
assert [state['sum'][1], state['add'][1], state['sum'][2], state['sum'][3]] == [17, 0, 7, 10]
inspect_lazy(state, [5, 2, 7, 3])
big = 10 ** 130
lazy_add(state, 0, 4, big)
lazy_add(state, 1, 3, -2 * big)
model = [5 + big, 2 - big, 7 - big, 3 + big]
for start, stop in intervals(4, True):
    assert lazy_sum(state, start, stop) == sum(model[start:stop])
inspect_lazy(state, model)
''')

    def test_first_threshold_position_against_scan_after_updates(self):
        self.check(SEGMENT, r'''
for values in arrays((-2, 0, 3), 5):
    state = segment_build(values)
    for start, stop in intervals(len(values), True):
        for threshold in [-3, -2, 0, 2, 3, 4]:
            expected = next((i for i in range(start, stop) if values[i] <= threshold), None)
            assert first_at_most(state, start, stop, threshold) == expected
    for start, stop in [(-1, 0), (0, len(values) + 1), (1, 0)]:
        assert first_at_most(state, start, stop, 3) is None
state = segment_build([8] * 1001)
assert segment_set(state, 999, -1)
assert first_at_most(state, 0, 1001, 0) == 999
assert first_at_most(state, 0, 999, 0) is None
''')

    def test_maxsum_summary_against_all_subarrays_and_splits(self):
        self.check(SEGMENT, r'''
for values in arrays((-2, 0, 3), 6):
    expected = maxsum_of(values)
    assert maxsum_summary(values) == expected
    for split in range(len(values) + 1):
        assert maxsum_merge(maxsum_of(values[:split]), maxsum_of(values[split:])) == expected
for a, b, c in itertools.product([[], [-2], [0], [3], [-2, 3]], repeat=3):
    left, middle, right = maxsum_of(a), maxsum_of(b), maxsum_of(c)
    assert maxsum_merge(maxsum_merge(left, middle), right) == maxsum_of(a + b + c)
    assert maxsum_merge(left, maxsum_merge(middle, right)) == maxsum_of(a + b + c)
''')

    def test_concat_noncommutative_queries_unicode_and_empty_tokens(self):
        self.check(SEGMENT, r'''
for tokens in arrays(('', 'a', '计数'), 5):
    original = tokens.copy()
    state = concat_build(tokens)
    before = copy.deepcopy(state)
    for start, stop in intervals(len(tokens), True):
        assert concat_query(state, start, stop) == ''.join(tokens[start:stop])
    assert state == before and tokens == original
    for start, stop in [(-1, 0), (0, len(tokens) + 1), (1, 0)]:
        assert concat_query(state, start, stop) is None
tokens = ['a', 'b', 'c', 'd', 'e', 'f']
assert concat_query(concat_build(tokens), 1, 5) == 'bcde'
assert concat_query(concat_build(['😀', 'é', 'é']), 0, 3) == '😀éé'
''')


if __name__ == "__main__":
    unittest.main()
