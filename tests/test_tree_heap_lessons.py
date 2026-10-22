"""Execute reviewed tree programs and check structure, identities, and real work."""
import ast
import unittest
from pathlib import Path

from cs_study_map.storage import read_json
from cs_study_map.textbook import validate_document
from test_data_structures_lessons import reviewed_tree, run_code
from test_recursive_algorithm_lessons import PROFILE, GUARDED
from test_algorithm_lessons import INSTRUMENTS

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ["16-trees", "17-binary-search-trees", "18-heaps"]


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
                        raise AssertionError("Different copies of helper: " + node.name)
                    functions[node.name] = source
    return "\n\n".join(functions.values()) + "\n"


TREE_ORACLE = '''
from functools import lru_cache
from itertools import product, permutations
@lru_cache(None)
def shapes(size):
    if size == 0:
        return (None,)
    return tuple((left, right) for left_size in range(size)
                 for left in shapes(left_size) for right in shapes(size-1-left_size))

def materialize(shape, field="value", labels=None):
    values = iter(labels) if labels is not None else iter([-2, 0, 3, -2, 3, 0, 0, 9]*100)
    def make(part):
        if part is None:
            return None
        node = {field: next(values), "left": None, "right": None}
        node["left"] = make(part[0])
        node["right"] = make(part[1])
        return node
    return make(shape)

def inspect_tree(root, field="value"):
    records = []
    stack = [(root, ())]
    seen = set()
    while stack:
        node, path = stack.pop()
        if node is None:
            continue
        assert id(node) not in seen, "Cycle or shared child"
        seen.add(id(node))
        assert set(node) == {field, "left", "right"}
        records.append((node, path))
        stack.append((node["right"], path+(1,)))
        stack.append((node["left"], path+(0,)))
    return records

def snapshot(root, field="value"):
    return (id(root), {id(node): (node[field], id(node["left"]), id(node["right"]))
                      for node, path in inspect_tree(root, field)})

def ordered_values(records, order, field="value"):
    if order == "pre":
        key = lambda item: item[1]
    elif order == "in":
        key = lambda item: item[1]+(0.5,)
    elif order == "post":
        key = lambda item: item[1]+(2,)
    else:
        key = lambda item: (len(item[1]), item[1])
    return [node[field] for node, path in sorted(records, key=key)]

def assert_bst_state(root, expected):
    records = inspect_tree(root, "key")
    assert len(records) == len(expected)
    assert ordered_values(records, "in", "key") == sorted(expected)
    return records
'''


class TreeHeapLessonTests(unittest.TestCase):
    def test_all_thirty_literal_programs_match_exact_outputs(self):
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

    def test_tree_statistics_and_actual_calls_on_every_small_shape(self):
        checks = TREE_ORACLE + PROFILE + '''
cases = 0
for size in range(8):
    for shape in shapes(size):
        root = materialize(shape)
        before = snapshot(root)
        records = inspect_tree(root)
        height = max((len(path) for node, path in records), default=-1)
        leaves = sum(node["left"] is None and node["right"] is None for node, path in records)
        result, calls, depths = observe(tree_stats, (root,), {"tree_stats"})
        assert result == {"size": size, "height": height, "leaves": leaves}
        assert calls["tree_stats"] == 2*size+1 and depths["tree_stats"] == height+2
        assert snapshot(root) == before
        cases += 1
assert cases == 626
'''
        self.assertEqual(run_code(definitions(CHAPTERS[0]), checks), "")

    def test_all_traversals_and_levels_against_path_order(self):
        checks = TREE_ORACLE + '''
for size in range(8):
    for shape in shapes(size):
        root = materialize(shape)
        records = inspect_tree(root)
        before = snapshot(root)
        for order in ("pre", "in", "post"):
            first = traversal(root, order)
            second = traversal(root, order)
            assert first == second == ordered_values(records, order)
            assert first is not second
        assert inorder_iterative(root) == ordered_values(records, "in")
        height = max((len(path) for node, path in records), default=-1)
        levels = [[node["value"] for node, path in sorted(records, key=lambda item: item[1])
                   if len(path) == depth] for depth in range(height+1)]
        assert tree_levels(root) == levels
        assert snapshot(root) == before
'''
        self.assertEqual(run_code(definitions(CHAPTERS[0]), checks), "")

    def test_tree_entry_visit_exit_events_and_stack(self):
        checks = TREE_ORACLE + PROFILE + '''
for size in range(7):
    for shape in shapes(size):
        root = materialize(shape, labels=range(size))
        records = inspect_tree(root)
        events = []
        result, calls, depths = observe(inorder_events, (root, events), {"inorder_events"})
        assert result is None and len(events) == 3*size
        assert calls["inorder_events"] == 2*size+1
        assert depths["inorder_events"] == max((len(path) for node, path in records), default=-1)+2
        stack = []
        for action, value in events:
            if action == "enter":
                stack.append(value)
            elif action == "visit":
                assert stack[-1] == value
            else:
                assert action == "leave" and stack.pop() == value
        assert not stack
        for action, order in (("enter", "pre"), ("visit", "in"), ("leave", "post")):
            assert [value for event, value in events if event == action] == ordered_values(records, order)
'''
        self.assertEqual(run_code(definitions(CHAPTERS[0]), checks), "")

    def test_mirror_swaps_every_link_and_twice_restores_identity(self):
        checks = TREE_ORACLE + '''
for size in range(8):
    for shape in shapes(size):
        root = materialize(shape)
        before = snapshot(root)
        stats = tree_stats(root)
        old_inorder = inorder_iterative(root)
        assert mirror_tree(root) is root
        after = snapshot(root)
        assert after[0] == before[0] and set(after[1]) == set(before[1])
        for identity, (value, left, right) in before[1].items():
            assert after[1][identity] == (value, right, left)
        assert tree_stats(root) == stats and inorder_iterative(root) == old_inorder[::-1]
        assert mirror_tree(root) is root and snapshot(root) == before
'''
        self.assertEqual(run_code(definitions(CHAPTERS[0]), checks), "")

    def test_leaf_sums_depth_queries_and_complete_shape(self):
        checks = TREE_ORACLE + '''
for size in range(8):
    for shape in shapes(size):
        root = materialize(shape)
        before = snapshot(root)
        records = inspect_tree(root)
        assert leaf_sum(root) == sum(node["value"] for node, path in records
                                    if node["left"] is None and node["right"] is None)
        for depth in range(-2, size+2):
            expected = [node["value"] for node, path in sorted(records, key=lambda item: item[1])
                        if len(path) == depth]
            assert nodes_at_depth(root, depth) == expected
        indices = []
        for node, path in records:
            index = 0
            for direction in path:
                index = 2*index+1+direction
            indices.append(index)
        assert is_complete(root) is (sorted(indices) == list(range(size)))
        assert snapshot(root) == before
'''
        self.assertEqual(run_code(definitions(CHAPTERS[0]), checks), "")

    def test_long_tree_iterative_versions_without_raising_recursion_limit(self):
        checks = TREE_ORACLE + '''
import sys
sys.setrecursionlimit(100)
for side in ("left", "right"):
    root = None
    for value in range(500):
        node = tree_node(value)
        node[side] = root
        root = node
    before = snapshot(root)
    for function, arguments in ((tree_stats, (root,)), (traversal, (root, "in"))):
        try:
            function(*arguments)
        except RecursionError:
            pass
        else:
            raise AssertionError("Expected a deep recursive chain")
    expected = list(range(500)) if side == "left" else list(range(499, -1, -1))
    assert inorder_iterative(root) == expected
    assert tree_levels(root) == [[value] for value in range(499, -1, -1)]
    assert nodes_at_depth(root, 499) == [0]
    assert nodes_at_depth(root, 500) == []
    assert snapshot(root) == before
'''
        self.assertEqual(run_code(definitions(CHAPTERS[0]), checks), "")

    def test_bst_mixed_updates_against_set_and_object_snapshots(self):
        checks = TREE_ORACLE + '''
actions = [(kind, key) for kind in ("add", "remove") for key in (-1, 0, 2)]
cases = 0
for length in range(6):
    for sequence in product(actions, repeat=length):
        root = None
        expected = set()
        for kind, key in sequence:
            before = snapshot(root, "key")
            old_ids = set(before[1])
            existed = key in expected
            if kind == "add":
                root = bst_insert(root, key)
                expected.add(key)
            else:
                root = bst_delete(root, key)
                expected.discard(key)
            records = assert_bst_state(root, expected)
            after = snapshot(root, "key")
            new_ids = set(after[1])
            if (kind == "add" and existed) or (kind == "remove" and not existed):
                assert after == before
            elif kind == "add":
                assert old_ids < new_ids and len(new_ids-old_ids) == 1
            else:
                assert new_ids < old_ids and len(old_ids-new_ids) == 1
            assert bst_keys(root) == sorted(expected)
            for query in (-2, -1, 0, 1, 2, 3):
                assert bst_find(root, query) == (query if query in expected else None)
        cases += 1
assert cases == 9331
'''
        self.assertEqual(run_code(definitions(CHAPTERS[1]), checks), "")

    def test_bst_all_six_key_insertion_orders_and_each_deletion(self):
        checks = TREE_ORACLE + '''
keys = (-4, 0, 3, 7, 11, 20)
cases = 0
for order in permutations(keys):
    for removed in keys:
        root = bst_from_keys(list(order))
        before_ids = {id(node) for node, path in inspect_tree(root, "key")}
        root = bst_delete(root, removed)
        records = assert_bst_state(root, set(keys)-{removed})
        assert {id(node) for node, path in records} < before_ids
    root = bst_from_keys(list(order))
    remaining = set(keys)
    for removed in order:
        root = bst_delete(root, removed)
        remaining.remove(removed)
        assert_bst_state(root, remaining)
    assert root is None
    cases += 1
assert cases == 720
'''
        self.assertEqual(run_code(definitions(CHAPTERS[1]), checks), "")

    def test_bst_successor_with_right_child_and_root_identity_contract(self):
        checks = TREE_ORACLE + '''
for keys in ([12,5,18,2,9,15,21,16], [12,5,15,16], [12,5,18,15], [12,5,18]):
    root = bst_from_keys(keys)
    saved = root
    successor = root["right"]
    while successor["left"] is not None:
        successor = successor["left"]
    successor_key = successor["key"]
    successor_child = successor["right"]
    before_ids = {id(node) for node, path in inspect_tree(root, "key")}
    root = bst_delete(root, 12)
    records = assert_bst_state(root, set(keys)-{12})
    after_ids = {id(node) for node, path in records}
    assert root is saved and root["key"] == successor_key
    assert before_ids-after_ids == {id(successor)}
    if successor_child is not None:
        assert id(successor_child) in after_ids
for side, child_key in (("left", -2), ("right", 8)):
    root = bst_node(4)
    child = bst_node(child_key)
    root[side] = child
    assert bst_delete(root, 4) is child
assert bst_delete(bst_node(4), 4) is None
'''
        self.assertEqual(run_code(definitions(CHAPTERS[1]), checks), "")

    def test_bst_global_validation_against_strict_inorder(self):
        checks = TREE_ORACLE + '''
cases = 0
for size in range(5):
    for shape in shapes(size):
        for labels in product((-3, 0, 4), repeat=size):
            root = materialize(shape, "key", labels)
            before = snapshot(root, "key")
            values = ordered_values(inspect_tree(root, "key"), "in", "key")
            expected = all(a < b for a, b in zip(values, values[1:]))
            assert is_bst(root) is expected
            assert snapshot(root, "key") == before
            cases += 1
assert cases == 1291
root = bst_from_keys([0, -10**50, 10**50])
assert is_bst(root)
'''
        self.assertEqual(run_code(definitions(CHAPTERS[1]), checks), "")

    def test_bst_floor_and_range_queries_preserve_all_links(self):
        checks = TREE_ORACLE + '''
from bisect import bisect_right
for size in range(6):
    for order in permutations(range(size)):
        root = bst_from_keys(list(order))
        before = snapshot(root, "key")
        values = list(range(size))
        for query in range(-1, size+2):
            boundary = bisect_right(values, query)
            assert bst_floor(root, query) == (values[boundary-1] if boundary else None)
        for lower in range(-1, size+2):
            for upper in range(-1, size+2):
                assert bst_range(root, lower, upper) == [key for key in values if lower <= key <= upper]
        assert snapshot(root, "key") == before
'''
        self.assertEqual(run_code(definitions(CHAPTERS[1]), checks), "")

    def test_bst_report_paths_and_ordered_insertion_actual_work(self):
        checks = TREE_ORACLE + PROFILE + '''
for size in range(65):
    keys = list(range(size))
    root, calls, depths = observe(bst_from_keys, (keys,), {"bst_insert", "bst_node"})
    assert calls["bst_insert"] == size*(size+1)//2
    assert calls["bst_node"] == size
    assert depths["bst_insert"] == size
    for query in range(-1, size+1):
        report = bst_find_report(root, query)
        expected = list(range(min(size, max(1, query+1))))
        assert report == {"found": query in keys, "visited": expected}
    records = inspect_tree(root, "key")
    assert max((len(path) for node, path in records), default=-1) == size-1
assert bst_find_report(sample_bst(), 15) == {"found": True, "visited": [12,18,15]}
assert bst_find_report(sample_bst(), 6) == {"found": False, "visited": [12,5,9]}
'''
        self.assertEqual(run_code(definitions(CHAPTERS[1]), checks), "")

    def test_balanced_bst_actual_allocations_height_and_input_reads(self):
        checks = TREE_ORACLE + PROFILE + GUARDED + '''
class ReadCount(GuardedList):
    def __init__(self, values):
        super().__init__(values)
        self.reads = 0
    def __getitem__(self, index):
        self.reads += 1
        return super().__getitem__(index)
for size in range(257):
    values = ReadCount(range(-size, size, 2))
    root, calls, depths = observe(balanced_bst, (values,), {"bst_from_range", "bst_node"})
    records = assert_bst_state(root, set(range(-size, size, 2)))
    height = max((len(path) for node, path in records), default=-1)
    assert height == size.bit_length()-1
    assert calls["bst_from_range"] == 2*size+1 and calls["bst_node"] == size
    assert depths["bst_from_range"] == height+2
    assert values.reads == size and values.writes == 0
    assert list(values) == list(range(-size, size, 2))
'''
        self.assertEqual(run_code(definitions(CHAPTERS[1]), checks), "")

    def test_heap_validator_and_peek_do_not_change_input(self):
        checks = INSTRUMENTS + '''
from itertools import product
for size in range(8):
    for source in product((-2, 0, 3), repeat=size):
        heap = list(source)
        expected = all(heap[(index-1)//2] <= heap[index] for index in range(1, size))
        assert is_min_heap(heap) is expected
        assert heap_peek(heap) == (source[0] if size else None)
        assert heap == list(source)
        if expected and size:
            assert heap_peek(heap) == min(source)
for size in range(129):
    heap = [CountedInt(value) for value in range(size)]
    CountedInt.comparisons = 0
    assert is_min_heap(heap)
    assert CountedInt.comparisons == max(0, size-1)
    CountedInt.comparisons = 0
    heap_peek(heap)
    assert CountedInt.comparisons == 0
'''
        self.assertEqual(run_code(definitions(CHAPTERS[2]), checks), "")

    def test_heap_mixed_operations_against_sorted_multiset_and_heapq(self):
        checks = '''
from itertools import product
from collections import Counter
import heapq
actions = (None, -2, 0, 3)
cases = 0
for length in range(8):
    for sequence in product(actions, repeat=length):
        heap = []
        reference = []
        values = []
        for action in sequence:
            if action is None:
                expected = min(values) if values else None
                if values:
                    values.remove(expected)
                assert heap_pop(heap) == expected
                assert (heapq.heappop(reference) if reference else None) == expected
            else:
                assert heap_push(heap, action) is None
                heapq.heappush(reference, action)
                values.append(action)
            assert is_min_heap(heap)
            assert Counter(heap) == Counter(reference) == Counter(values)
            before = heap.copy()
            assert heap_peek(heap) == (min(values) if values else None)
            assert heap == before
        cases += 1
assert cases == 21845
'''
        self.assertEqual(run_code(definitions(CHAPTERS[2]), checks), "")

    def test_heapify_preserves_identity_and_has_linear_comparison_budget(self):
        checks = INSTRUMENTS + '''
from itertools import product
from collections import Counter
import heapq
cases = [list(values) for size in range(8) for values in product((-2, 0, 3), repeat=size)]
assert len(cases) == 3280
cases += [list(range(size, 0, -1)) for size in range(257)]
cases += [list(range(1024)), list(range(1023, -1, -1)), [3]*1025]
for source in cases:
    heap = [CountedInt(value) for value in source]
    identities = Counter(map(id, heap))
    CountedInt.comparisons = 0
    assert heapify(heap) is None
    comparisons = CountedInt.comparisons
    assert comparisons <= 2*(len(source)-len(source).bit_count())
    assert is_min_heap(heap) and Counter(map(id, heap)) == identities
    assert sorted(heap) == sorted(source)
    reference = source.copy()
    heapq.heapify(reference)
    extracted = [heap_pop(heap) for _ in source]
    assert extracted == [heapq.heappop(reference) for _ in source] == sorted(source)
    assert heap == [] and heap_pop(heap) is None
'''
        self.assertEqual(run_code(definitions(CHAPTERS[2]), checks), "")

    def test_heap_adjustment_actual_comparisons_follow_height_bounds(self):
        checks = INSTRUMENTS + '''
for size in range(129):
    for source in (list(range(size)), list(range(size, 0, -1)), [0]*size):
        heap = []
        for value in source:
            CountedInt.comparisons = 0
            heap_push(heap, CountedInt(value))
            assert CountedInt.comparisons <= len(heap).bit_length()-1
            assert is_min_heap(heap)
        previous = None
        while heap:
            CountedInt.comparisons = 0
            result = heap_pop(heap)
            comparisons = CountedInt.comparisons
            assert comparisons <= 2*max(0, len(heap).bit_length()-1)
            assert previous is None or previous <= result
            previous = result
            assert is_min_heap(heap)
'''
        self.assertEqual(run_code(definitions(CHAPTERS[2]), checks), "")

    def test_sift_down_respects_prefix_and_repairs_only_valid_child_heaps(self):
        checks = GUARDED + '''
from itertools import product
from collections import Counter
for size in range(7):
    for source in product((-2, 0, 3), repeat=size):
        for minimum, function in ((True, sift_down), (False, sift_down_max)):
            valid_children = all((source[(i-1)//2] <= source[i] if minimum else source[(i-1)//2] >= source[i])
                                 for i in range(3, size))
            if not valid_children:
                continue
            data = GuardedList(list(source)+[10**9, -10**9], 0, size)
            assert function(data, 0, size) is None
            output = list(data)
            assert output[size:] == [10**9, -10**9]
            assert Counter(output[:size]) == Counter(source)
            assert all((output[(i-1)//2] <= output[i] if minimum else output[(i-1)//2] >= output[i])
                       for i in range(1, size))
'''
        self.assertEqual(run_code(definitions(CHAPTERS[2]), checks), "")

    def test_heapify_snapshots_are_independent_and_preserve_other_subtrees(self):
        checks = INSTRUMENTS + '''
from itertools import product
from collections import Counter
for size in range(7):
    for source in product((-2, 0, 3), repeat=size):
        heap = list(source)
        steps = heapify_trace(heap)
        assert [step[0] for step in steps] == list(range(size//2-1, -1, -1))
        assert len({id(step[1]) for step in steps}) == len(steps)
        previous = list(source)
        for index, snapshot in steps:
            assert snapshot is not heap and Counter(snapshot) == Counter(source)
            descendants = set()
            pending = [index]
            while pending:
                position = pending.pop()
                if position < size:
                    descendants.add(position)
                    pending.extend((2*position+1, 2*position+2))
            for position in range(size):
                if position not in descendants:
                    assert snapshot[position] == previous[position]
                elif position != index:
                    assert snapshot[(position-1)//2] <= snapshot[position]
            previous = snapshot
        assert previous == heap and is_min_heap(heap)
heap = [CountedInt(value) for value in [9,4,7,1,3,6]]
CountedInt.comparisons = 0
heapify_trace(heap)
assert CountedInt.comparisons == 7
'''
        self.assertEqual(run_code(definitions(CHAPTERS[2]), checks), "")

    def test_heap_sorts_against_sorted_and_instability_identity_example(self):
        checks = INSTRUMENTS + '''
from itertools import product, permutations
from collections import Counter
cases = [list(values) for size in range(8) for values in product((-2, 0, 3), repeat=size)]
cases += [list(values) for values in permutations(range(6))]
cases += [list(range(1024)), list(range(1024, -1, -1)), [0]*1025, [10**50, -10**50, 0]]
for source in cases:
    values = [TaggedInt(value, index) for index, value in enumerate(source)]
    identities = Counter(map(id, values))
    assert heap_sort(values) is None
    assert values == sorted(source) and Counter(map(id, values)) == identities
    data = source.copy()
    output = heap_sort_copy(data)
    assert output == sorted(source) and output is not data and data == source
values = [TaggedInt(2, "A"), TaggedInt(2, "B")]
heap_sort(values)
assert [item.tag for item in values] == ["B", "A"]
'''
        self.assertEqual(run_code(definitions(CHAPTERS[2]), checks), "")

    def test_heap_sort_actual_loop_prefix_and_suffix_invariants(self):
        code = definitions(CHAPTERS[2])
        swap_line = code.splitlines().index("        heap_swap(values, 0, end)") + 1
        checks = f"\nsort_swap_line = {swap_line}\n" + '''
import sys
from itertools import product, permutations
from collections import Counter
events = []
def trace(frame, event, arg):
    if frame.f_code.co_name == "heap_sort" and event == "line" and frame.f_lineno == sort_swap_line:
        values, end = frame.f_locals["values"], frame.f_locals["end"]
        assert all(values[(i-1)//2] >= values[i] for i in range(1, end+1))
        assert values[end+1:] == sorted(values[end+1:])
        assert not values[end+1:] or max(values[:end+1]) <= values[end+1]
        assert Counter(values) == original
        events.append(end)
    return trace
cases = [list(values) for size in range(7) for values in product((-2, 0, 3), repeat=size)]
cases += [list(values) for values in permutations(range(6))]
for source in cases:
    values = source.copy()
    original = Counter(source)
    events = []
    sys.settrace(trace)
    try:
        heap_sort(values)
    finally:
        sys.settrace(None)
    assert events == list(range(len(source)-1, 0, -1))
    assert values == sorted(source)
'''
        self.assertEqual(run_code(code, checks), "")

    def test_largest_k_all_ranks_duplicates_and_input_preservation(self):
        checks = '''
from itertools import product
for size in range(8):
    for source in product((-2, 0, 3), repeat=size):
        values = list(source)
        for k in range(-1, size+3):
            expected = sorted(source)[-k:] if k > 0 else []
            assert largest_k(values, k) == expected
            assert values == list(source)
'''
        self.assertEqual(run_code(definitions(CHAPTERS[2]), checks), "")

    def test_largest_k_actual_prefix_selection_invariant(self):
        code = definitions(CHAPTERS[2])
        check_line = code.splitlines().index("        if len(heap) < k:") + 1
        checks = f"\nselection_line = {check_line}\n" + '''
import sys
from itertools import product
seen = 0
def trace(frame, event, arg):
    global seen
    if frame.f_code.co_name == "largest_k" and event == "line" and frame.f_lineno == selection_line:
        values, heap, k = (frame.f_locals[name] for name in ("values", "heap", "k"))
        assert len(heap) <= k and is_min_heap(heap)
        assert sorted(heap) == sorted(values[:seen])[-k:]
        seen += 1
    return trace
for size in range(6):
    for source in product((-2, 0, 3), repeat=size):
        for k in range(1, size+2):
            seen = 0
            sys.settrace(trace)
            try:
                result = largest_k(list(source), k)
            finally:
                sys.settrace(None)
            assert seen == size and result == sorted(source)[-k:]
'''
        self.assertEqual(run_code(code, checks), "")

    def test_multiway_merge_against_flat_sort_and_heapq_with_empty_groups(self):
        checks = '''
from itertools import combinations_with_replacement, product
import heapq
groups = [list(values) for size in range(4) for values in combinations_with_replacement((-2,0,3), size)]
assert len(groups) == 20
cases = 0
for combination in product(groups, repeat=3):
    data = [group.copy() for group in combination]
    before = [group.copy() for group in data]
    result = merge_sorted_groups(data)
    expected = sorted(value for group in data for value in group)
    assert result == expected == list(heapq.merge(*data))
    assert data == before and all(result is not group for group in data)
    cases += 1
assert cases == 8000
assert merge_sorted_groups([]) == []
assert merge_sorted_groups([[] for _ in range(1000)]) == []
assert merge_sorted_groups([[1], [1], [1]]) == [1,1,1]
'''
        self.assertEqual(run_code(definitions(CHAPTERS[2]), checks), "")


if __name__ == "__main__":
    unittest.main()
