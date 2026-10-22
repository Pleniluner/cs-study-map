"""Run original lesson text and verify mappings, relations and traversal work."""
import ast
import unittest
from pathlib import Path

from cs_study_map.storage import read_json
from cs_study_map.textbook import validate_document
from test_data_structures_lessons import reviewed_tree, run_code
from test_recursive_algorithm_lessons import PROFILE

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ['19-hash-tables', '20-graphs', '21-graph-traversal']


def document(identifier):
    return read_json(ROOT / 'catalog/chapters' / (identifier + '.json'))


def definitions(identifier):
    functions = {}
    content = document(identifier)['content']
    for group in ('sections', 'worked_examples', 'exercises'):
        for item in content[group]:
            code = item['program']['code']
            for node in reviewed_tree(code).body:
                if isinstance(node, ast.FunctionDef):
                    source = ast.get_source_segment(code, node)
                    if node.name in functions and functions[node.name] != source:
                        raise AssertionError('Inconsistent helper: ' + node.name)
                    functions[node.name] = source
    return '\n\n'.join(functions.values()) + '\n'


HASH_ORACLE = '''
from itertools import product
def inspect_table(table, expected):
    buckets = table['buckets']
    assert len(buckets) > 0 and len({id(b) for b in buckets}) == len(buckets)
    records = [entry for bucket in buckets for entry in bucket]
    assert len({id(e) for e in records}) == len(records)
    assert len(records) == table['size'] == len(expected)
    assert len({e[0] for e in records}) == len(records)
    assert dict(records) == expected
    for number, bucket in enumerate(buckets):
        assert all(len(e) == 2 and e[0] % len(buckets) == number for e in bucket)
    for key in [-99, -4, 0, 4, 99] + list(expected):
        assert table_get(table, key) == [key in expected, expected.get(key)]
    return {e[0]: id(e) for e in records}

def table_snapshot(table):
    return (id(table['buckets']), table['size'],
            [(id(b), [(id(e), e[:]) for e in b]) for b in table['buckets']])

class CountKey(int):
    comparisons = 0
    remainders = 0
    def __eq__(self, other):
        CountKey.comparisons += 1
        return int(self) == int(other)
    def __mod__(self, other):
        CountKey.remainders += 1
        return int(self) % int(other)
    __hash__ = int.__hash__
'''

GRAPH_ORACLE = '''
from itertools import combinations, permutations, product
from copy import deepcopy
def small_graphs(maximum, directed=True):
    for n in range(maximum + 1):
        candidates = list(permutations(range(n), 2) if directed else combinations(range(n), 2))
        for mask in range(1 << len(candidates)):
            edges = {pair for i, pair in enumerate(candidates) if mask & (1 << i)}
            relation = edges if directed else edges | {(v, u) for u, v in edges}
            adjacency = [[v for v in range(n) if (u, v) in relation] for u in range(n)]
            yield adjacency, edges, relation

def relation_of(adjacency):
    return {(u, v) for u, row in enumerate(adjacency) for v in row}

def all_distances(adjacency):
    # Floyd-Warshall is independent of the lesson queue, stack, and discovery rule.
    n = len(adjacency)
    result = [[0 if u == v else n+1 for v in range(n)] for u in range(n)]
    for u, v in relation_of(adjacency):
        result[u][v] = 1
    for middle in range(n):
        for u in range(n):
            for v in range(n):
                result[u][v] = min(result[u][v], result[u][middle] + result[middle][v])
    return [[d if d <= n else -1 for d in row] for row in result]

def inspect_graph(adjacency, expected):
    n = len(adjacency)
    assert len({id(row) for row in adjacency}) == n
    assert relation_of(adjacency) == expected
    for u, row in enumerate(adjacency):
        assert len(row) == len(set(row)) and u not in row
        assert all(0 <= v < n for v in row)

def inspect_search(adjacency, start, result, distances):
    order, parent = result['order'], result['parent']
    reached = {v for v, d in enumerate(distances) if d >= 0}
    assert len(order) == len(set(order)) == len(reached)
    assert set(order) == reached and order[0] == start
    assert len(parent) == len(adjacency)
    discovered = set()
    for v in order:
        if v == start:
            assert parent[v] is None
        else:
            assert parent[v] in discovered and v in adjacency[parent[v]]
        discovered.add(v)
    assert all(parent[v] is None for v in range(len(adjacency)) if v not in reached)

class ScanRow(list):
    def __init__(self, values):
        super().__init__(values)
        self.reads = 0
    def __iter__(self):
        for value in super().__iter__():
            self.reads += 1
            yield value
    def __getitem__(self, index):
        assert isinstance(index, int) and 0 <= index < len(self)
        self.reads += 1
        return super().__getitem__(index)
'''


class HashGraphLessonTests(unittest.TestCase):
    def test_all_thirty_literal_programs_match_exact_outputs(self):
        count = 0
        for identifier in CHAPTERS:
            saved = document(identifier)
            validate_document(saved)
            for group, length in (('sections', 5), ('worked_examples', 2), ('exercises', 3)):
                self.assertEqual(len(saved['content'][group]), length)
                for index, item in enumerate(saved['content'][group]):
                    with self.subTest(chapter=identifier, group=group, item=index):
                        self.assertEqual(run_code(item['program']['code']), item['program']['output'])
                        count += 1
        self.assertEqual(count, 30)

    def test_hash_mixed_operations_against_mapping_and_identity_contracts(self):
        checks = HASH_ORACLE + '''
actions = [('set', -4, None), ('set', 0, 0), ('set', 4, 4), ('set', 0, 7),
           ('get', 0, None), ('delete', -4, None), ('delete', 0, None), ('delete', 4, None)]
cases = 0
for size in range(5):
    for sequence in product(actions, repeat=size):
        for capacity in (1, 3):
            for setter in (table_set, hash_put):
                table, expected = new_table(capacity), {}
                for kind, key, value in sequence:
                    before = table_snapshot(table)
                    if kind == 'set':
                        assert setter(table, key, value) == (key not in expected)
                        expected[key] = value
                    elif kind == 'delete':
                        existed = key in expected
                        assert table_delete(table, key) == existed
                        expected.pop(key, None)
                        if not existed:
                            assert table_snapshot(table) == before
                    else:
                        assert table_get(table, key) == [key in expected, expected.get(key)]
                        assert table_snapshot(table) == before
                    inspect_table(table, expected)
                    if setter is hash_put:
                        assert table['size'] <= len(table['buckets'])
                cases += 1
assert cases == 18724
'''
        self.assertEqual(run_code(definitions(CHAPTERS[0]), checks), '')

    def test_hash_resize_migration_preserves_keys_values_and_entry_identity(self):
        checks = HASH_ORACLE + '''
for initial in (1, 3, 8):
    table, expected = new_table(initial), {}
    for i in range(129):
        key = (-1 if i % 2 else 1) * (i * 4096 + 7)
        old = inspect_table(table, expected)
        value = None if i % 3 == 0 else -i
        assert hash_put(table, key, value)
        expected[key] = value
        now = inspect_table(table, expected)
        assert all(now[k] == old[k] for k in old)
        assert table['size'] <= len(table['buckets'])
        assert not hash_put(table, key, value)
    for capacity in (1, 7, 256):
        old = inspect_table(table, expected)
        old_buckets = table['buckets']
        rehash(table, capacity)
        assert inspect_table(table, expected) == old
        assert len(table['buckets']) == capacity
        assert not ({id(b) for b in old_buckets} & {id(b) for b in table['buckets']})
    retained = len(table['buckets'])
    for key in list(expected):
        assert table_delete(table, key)
        del expected[key]
        inspect_table(table, expected)
    assert len(table['buckets']) == retained
for key in [-10**100, -1, 0, 1, 10**100]:
    for capacity in (1, 2, 3, 17):
        assert 0 <= bucket_index(key, capacity) < capacity
'''
        self.assertEqual(run_code(definitions(CHAPTERS[0]), checks), '')

    def test_hash_actual_collision_comparisons_and_linear_rehash(self):
        checks = HASH_ORACLE + '''
for size in range(65):
    table = new_table(8)
    for i in range(size):
        table_set(table, CountKey(i * 128), i)
    for i in range(size):
        CountKey.comparisons = 0
        assert table_get(table, i * 128) == [True, i]
        assert CountKey.comparisons == i + 1
    CountKey.comparisons = 0
    assert hash_probe(table, -128) == [False, size]
    assert CountKey.comparisons == size
    CountKey.comparisons = CountKey.remainders = 0
    rehash(table, 16)
    assert CountKey.comparisons == 0 and CountKey.remainders == size
    assert len(table['buckets'][0]) == size
    assert table_profile(table)['maximum'] == size
    assert table_profile(table)['total'] == size
'''
        self.assertEqual(run_code(definitions(CHAPTERS[0]), checks), '')

    def test_hash_growth_work_is_measured_separately_from_bucket_search(self):
        checks = HASH_ORACLE + '''
import sys
migrations = []
def profile(frame, event, arg):
    if event == 'call' and frame.f_code is rehash.__code__:
        table = frame.f_locals['table']
        migrations.append((table['size'], len(table['buckets']), frame.f_locals['capacity']))
table = new_table(1)
sys.setprofile(profile)
try:
    for key in range(257):
        hash_put(table, key, key)
finally:
    sys.setprofile(None)
assert len(migrations) == 9
assert all(n == old + 1 and new == 2 * old for n, old, new in migrations)
assert sum(n for n, old, new in migrations) == 520 < 3 * 257
assert len(table['buckets']) == 512
'''
        self.assertEqual(run_code(definitions(CHAPTERS[0]), checks), '')

    def test_hash_frequencies_and_first_repeat_against_sequence_models(self):
        checks = HASH_ORACLE + '''
cases = 0
for n in range(8):
    for values in product((-2, 0, 3), repeat=n):
        values = list(values)
        before = values[:]
        order = list(dict.fromkeys(values))
        assert frequency_pairs(values) == [[v, values.count(v)] for v in order]
        repeat = next((v for i, v in enumerate(values) if v in values[:i]), None)
        assert first_repeat(values) == [repeat is not None, repeat]
        assert values == before
        cases += 1
assert cases == 3280
'''
        self.assertEqual(run_code(definitions(CHAPTERS[0]), checks), '')

    def test_hash_two_sum_against_ordered_position_pairs(self):
        checks = HASH_ORACLE + '''
cases = 0
for n in range(8):
    for values in product((-2, 0, 3), repeat=n):
        values = list(values)
        before = values[:]
        for target in range(-5, 8):
            expected = next(([j, i] for i in range(n) for j in range(i)
                             if values[j] + values[i] == target), None)
            assert two_sum_indices(values, target) == expected
            assert values == before
            cases += 1
assert cases == 42640
'''
        self.assertEqual(run_code(definitions(CHAPTERS[0]), checks), '')

    def test_graph_construction_deduplicates_and_preserves_isolated_vertices(self):
        checks = GRAPH_ORACLE + '''
cases = 0
for directed, maximum in ((True, 4), (False, 5)):
    for adjacency, edges, relation in small_graphs(maximum, directed):
        inputs = [list(pair) for pair in sorted(edges, reverse=True)]
        inputs += deepcopy(inputs)
        if not directed:
            inputs += [[v, u] for u, v in sorted(edges)]
        before = deepcopy(inputs)
        graph = build_graph(len(adjacency), inputs, directed)
        inspect_graph(graph, relation)
        assert len(graph) == len(adjacency) and inputs == before
        for u in range(len(graph)):
            for v in range(len(graph)):
                assert has_edge(graph, u, v) == ((u, v) in relation)
        cases += 1
assert cases == 5266
assert build_graph(-1, [], True) is None
for directed in (True, False):
    for edge in ([0, 0], [-1, 0], [0, -1], [0, 3], [3, 0]):
        inputs = [[0, 1], edge]
        before = deepcopy(inputs)
        assert build_graph(3, inputs, directed) is None and inputs == before
    assert build_graph(0, [[0, 1]], directed) is None
'''
        self.assertEqual(run_code(definitions(CHAPTERS[1]), checks), '')

    def test_graph_mixed_edge_mutations_against_relation_sets(self):
        checks = GRAPH_ORACLE + '''
actions = [(kind, u, v) for kind in ('add', 'remove') for u, v in ((0, 1), (1, 2), (2, 0))]
cases = 0
for length in range(6):
    for sequence in product(actions, repeat=length):
        for directed in (True, False):
            graph, relation = empty_graph(4), set()
            row_ids = list(map(id, graph))
            for kind, u, v in sequence:
                before = deepcopy(graph)
                existed = (u, v) in relation
                if kind == 'add':
                    assert add_edge(graph, u, v, directed) == (not existed)
                    relation.add((u, v))
                    if not directed:
                        relation.add((v, u))
                    if existed:
                        assert graph == before
                else:
                    assert remove_edge(graph, u, v, directed) == existed
                    relation.discard((u, v))
                    if not directed:
                        relation.discard((v, u))
                    expected = deepcopy(before)
                    if existed:
                        expected[u].remove(v)
                        if not directed:
                            expected[v].remove(u)
                    assert graph == expected
                inspect_graph(graph, relation)
                assert list(map(id, graph)) == row_ids
            cases += 1
assert cases == 18662
graph = [[1], [0], []]
for edge in ((-1, 0), (0, -1), (0, 3), (3, 0), (1, 1)):
    before = deepcopy(graph)
    assert not add_edge(graph, *edge, False)
    assert not remove_edge(graph, *edge, False)
    assert graph == before
'''
        self.assertEqual(run_code(definitions(CHAPTERS[1]), checks), '')

    def test_graph_degree_edge_counts_and_transpose_against_relations(self):
        checks = GRAPH_ORACLE + '''
for directed, maximum in ((True, 4), (False, 5)):
    for graph, edges, relation in small_graphs(maximum, directed):
        before = deepcopy(graph)
        report = degree_report(graph)
        n = len(graph)
        assert report == {'out': [sum(u == v for u, w in relation) for v in range(n)],
                          'in': [sum(w == v for u, w in relation) for v in range(n)],
                          'arcs': len(relation)}
        assert edge_count(graph, directed) == len(edges)
        reverse = reverse_edges(graph)
        inspect_graph(reverse, {(v, u) for u, v in relation})
        assert relation_of(reverse_edges(reverse)) == relation
        assert not ({id(row) for row in reverse} & {id(row) for row in graph})
        assert graph == before
graph = [[2, 1], [2], [], [1], []]
assert reverse_edges(reverse_edges(graph))[0] == [1, 2]
assert graph[0] == [2, 1]
'''
        self.assertEqual(run_code(definitions(CHAPTERS[1]), checks), '')

    def test_graph_matrix_conversion_roundtrips_relations_not_row_order(self):
        checks = GRAPH_ORACLE + '''
for directed, maximum in ((True, 4), (False, 5)):
    for graph, edges, relation in small_graphs(maximum, directed):
        before = deepcopy(graph)
        matrix = to_matrix(graph)
        n = len(graph)
        assert matrix == [[int((u, v) in relation) for v in range(n)] for u in range(n)]
        assert len({id(row) for row in matrix}) == n
        restored = matrix_to_lists(matrix)
        inspect_graph(restored, relation)
        assert all(row == sorted(row) for row in restored)
        assert to_matrix(restored) == matrix and graph == before
        if n:
            matrix[0][0] = 1
            assert graph == before and restored == before
graph = [[2, 1], [], []]
assert matrix_to_lists(to_matrix(graph)) == [[1, 2], [], []]
assert graph == [[2, 1], [], []]
'''
        self.assertEqual(run_code(definitions(CHAPTERS[1]), checks), '')

    def test_graph_walks_with_repeated_vertices_zero_edges_and_invalid_ids(self):
        checks = GRAPH_ORACLE + '''
for graph, edges, relation in small_graphs(3):
    n = len(graph)
    before = deepcopy(graph)
    for length in range(5):
        for route in product(range(n), repeat=length):
            route = list(route)
            expected = bool(route) and all(pair in relation for pair in zip(route, route[1:]))
            assert is_walk(graph, route) == expected
    for route in ([-1], [n], [0, -1], [-1, 0], [0, n], [n, 0]):
        assert not is_walk(graph, route)
    assert graph == before
assert is_walk([[1], [0]], [0, 1, 0, 1, 0])
'''
        self.assertEqual(run_code(definitions(CHAPTERS[1]), checks), '')

    def test_graph_duplicate_checks_have_actual_quadratic_star_build_work(self):
        checks = GRAPH_ORACLE + '''
for n in range(1, 65):
    graph = [ScanRow([]) for _ in range(n)]
    for v in range(1, n):
        assert add_edge(graph, 0, v, True)
    assert sum(row.reads for row in graph) == (n - 1) * (n - 2) // 2
    graph[0].reads = 0
    assert not has_edge(graph, 0, 0)
    assert graph[0].reads == n - 1
'''
        self.assertEqual(run_code(definitions(CHAPTERS[1]), checks), '')

    def test_bfs_all_small_directed_graphs_against_all_pairs_distance_oracle(self):
        checks = GRAPH_ORACLE + '''
cases = 0
for graph, edges, relation in small_graphs(4):
    oracle = all_distances(graph)
    before = deepcopy(graph)
    for start in range(len(graph)):
        result = breadth_first(graph, start)
        inspect_search(graph, start, result, oracle[start])
        assert result['distance'] == oracle[start]
        depths = [result['distance'][v] for v in result['order']]
        assert depths == sorted(depths)
        for v in result['order'][1:]:
            assert result['distance'][result['parent'][v]] + 1 == result['distance'][v]
        for target in range(len(graph)):
            path = shortest_path(graph, start, target)
            if oracle[start][target] == -1:
                assert path == []
            else:
                assert path[0] == start and path[-1] == target
                assert len(path) == len(set(path)) == oracle[start][target] + 1
                assert all(pair in relation for pair in zip(path, path[1:]))
        assert graph == before
    cases += 1
assert cases == 4166
'''
        self.assertEqual(run_code(definitions(CHAPTERS[2]), checks), '')

    def test_dfs_frames_match_recursive_tree_on_all_small_directed_graphs(self):
        checks = GRAPH_ORACLE + '''
for original, edges, relation in small_graphs(4):
    oracle = all_distances(original)
    for graph in (original, [list(reversed(row)) for row in original]):
        before = deepcopy(graph)
        for start in range(len(graph)):
            recursive = dfs_recursive(graph, start)
            iterative = dfs_stack(graph, start)
            assert iterative == recursive
            inspect_search(graph, start, iterative, oracle[start])
        assert graph == before
graph = [[1, 2], [2], []]
assert dfs_stack(graph, 0)['parent'] == [None, 0, 1]
assert breadth_first(graph, 0)['parent'] == [None, 0, 0]
graph = [[1, 3], [2], [3], []]
assert dfs_stack(graph, 0)['parent'] == [None, 0, 1, 2]
assert shortest_path(graph, 0, 3) == [0, 3]
'''
        self.assertEqual(run_code(definitions(CHAPTERS[2]), checks), '')

    def test_undirected_components_against_mutual_reachability(self):
        checks = GRAPH_ORACLE + '''
cases = 0
for graph, edges, relation in small_graphs(5, False):
    before = deepcopy(graph)
    oracle = all_distances(graph)
    result = components(graph)
    groups, label = result['groups'], result['label']
    flattened = [v for group in groups for v in group]
    assert sorted(flattened) == list(range(len(graph)))
    assert [group[0] for group in groups] == sorted(min(group) for group in groups)
    for i, group in enumerate(groups):
        assert group and all(label[v] == i for v in group)
    for u in range(len(graph)):
        for v in range(len(graph)):
            assert (label[u] == label[v]) == (oracle[u][v] >= 0)
    assert graph == before
    cases += 1
assert cases == 1100
'''
        self.assertEqual(run_code(definitions(CHAPTERS[2]), checks), '')

    def test_dfs_events_are_nested_and_each_vertex_finishes_after_neighbors(self):
        checks = GRAPH_ORACLE + '''
for graph, edges, relation in small_graphs(3):
    for start in range(len(graph)):
        events = dfs_events(graph, start)
        seen, finished, stack, order = set(), set(), [], []
        for kind, vertex in events:
            if kind == 'enter':
                assert vertex not in seen
                if stack:
                    assert vertex in graph[stack[-1]]
                seen.add(vertex)
                stack.append(vertex)
                order.append(vertex)
            else:
                assert kind == 'leave' and stack.pop() == vertex
                assert vertex not in finished and all(v in seen for v in graph[vertex])
                finished.add(vertex)
        assert not stack and seen == finished and len(events) == 2 * len(seen)
        assert order == dfs_recursive(graph, start)['order']
'''
        self.assertEqual(run_code(definitions(CHAPTERS[2]), checks), '')

    def test_bfs_snapshots_show_discovery_marking_and_do_not_alias(self):
        checks = GRAPH_ORACLE + '''
for graph, edges, relation in small_graphs(3):
    for start in range(len(graph)):
        trace = bfs_trace(graph, start)
        expected = breadth_first(graph, start)
        assert trace['distance'] == expected['distance']
        assert [step[0] for step in trace['steps']] == expected['order']
        processed, previous = set(), [-1] * len(graph)
        for vertex, waiting, distance in trace['steps']:
            processed.add(vertex)
            assert len(waiting) == len(set(waiting)) and not (set(waiting) & processed)
            assert {v for v, d in enumerate(distance) if d >= 0} == processed | set(waiting)
            assert all(previous[v] == -1 or previous[v] == distance[v] for v in range(len(graph)))
            assert all(distance[v] == -1 or distance[v] == expected['distance'][v] for v in range(len(graph)))
            previous = distance
        assert len({id(step[2]) for step in trace['steps']}) == len(trace['steps'])
        if trace['steps']:
            trace['steps'][0][2][start] = 999
            assert trace['distance'][start] == 0
            assert all(step[2][start] == 0 for step in trace['steps'][1:])
'''
        self.assertEqual(run_code(definitions(CHAPTERS[2]), checks), '')

    def test_distance_layers_and_reachability_matrix_against_distance_oracle(self):
        checks = GRAPH_ORACLE + '''
for graph, edges, relation in small_graphs(4):
    oracle = all_distances(graph)
    assert reachability_matrix(graph) == [[int(d >= 0) for d in row] for row in oracle]
    for start in range(len(graph)):
        for k in range(-1, len(graph) + 1):
            expected = [v for v, d in enumerate(oracle[start]) if d == k and k >= 0]
            assert vertices_at_distance(graph, start, k) == expected
'''
        self.assertEqual(run_code(definitions(CHAPTERS[2]), checks), '')

    def test_multi_source_distance_against_minimum_of_independent_single_sources(self):
        checks = GRAPH_ORACLE + '''
cases = 0
for graph, edges, relation in small_graphs(4):
    n = len(graph)
    oracle = all_distances(graph)
    before = deepcopy(graph)
    for mask in range(1 << n):
        sources = [v for v in range(n) if mask & (1 << v)]
        expected = [min((oracle[s][v] for s in sources if oracle[s][v] >= 0), default=-1)
                    for v in range(n)]
        assert multi_source_distances(graph, sources) == expected
        assert multi_source_distances(graph, list(reversed(sources)) + sources) == expected
        assert graph == before
        cases += 1
assert cases == 66067
'''
        self.assertEqual(run_code(definitions(CHAPTERS[2]), checks), '')

    def test_invalid_starts_targets_empty_graphs_and_invalid_sources(self):
        checks = GRAPH_ORACLE + '''
for graph in ([], [[]], [[1], [0], []]):
    n = len(graph)
    before = deepcopy(graph)
    for invalid in (-3, -1, n, n + 1):
        for dfs in (dfs_recursive, dfs_stack):
            assert dfs(graph, invalid) == {'order': [], 'parent': [None] * n}
        assert breadth_first(graph, invalid) == {'order': [], 'distance': [-1] * n, 'parent': [None] * n}
        assert shortest_path(graph, 0, invalid) == shortest_path(graph, invalid, 0) == []
        assert vertices_at_distance(graph, invalid, 0) == []
        assert dfs_events(graph, invalid) == []
        assert bfs_trace(graph, invalid) == {'distance': [-1] * n, 'steps': []}
        assert multi_source_distances(graph, [invalid]) is None
        if n:
            assert multi_source_distances(graph, [0, invalid]) is None
    assert multi_source_distances(graph, []) == [-1] * n
    assert graph == before
'''
        self.assertEqual(run_code(definitions(CHAPTERS[2]), checks), '')

    def test_traversals_scan_each_reachable_adjacency_item_once(self):
        checks = GRAPH_ORACLE + PROFILE + '''
original = [[1, 2], [3], [3, 0], [0], [5, 6], [4, 6], [4, 5], []]
oracle = all_distances(original)
for start in range(len(original)):
    reachable = {v for v, d in enumerate(oracle[start]) if d >= 0}
    expected = sum(len(original[v]) for v in reachable)
    for search in (dfs_recursive, dfs_stack, breadth_first, dfs_events, bfs_trace):
        graph = [ScanRow(row) for row in original]
        search(graph, start)
        assert sum(row.reads for row in graph) == expected
        assert all(graph[v].reads == len(original[v]) if v in reachable else graph[v].reads == 0
                   for v in range(len(graph)))
    result, calls, depths = observe(dfs_recursive, (original, start), {'dfs_visit'})
    assert calls['dfs_visit'] == len(reachable)
    assert 1 <= depths['dfs_visit'] <= len(reachable)
undirected = [[1, 2], [0, 3], [0, 3], [1, 2], [5], [4], []]
graph = [ScanRow(row) for row in undirected]
components(graph)
assert sum(row.reads for row in graph) == sum(map(len, undirected))
'''
        self.assertEqual(run_code(definitions(CHAPTERS[2]), checks), '')

    def test_iterative_searches_handle_long_paths_without_raising_recursion_limit(self):
        checks = GRAPH_ORACLE + '''
import sys
n = 1200
graph = [[i + 1] for i in range(n - 1)] + [[]]
before = deepcopy(graph)
old_limit = sys.getrecursionlimit()
sys.setrecursionlimit(100)
try:
    failed = False
    try:
        dfs_recursive(graph, 0)
    except RecursionError:
        failed = True
    assert failed
    assert dfs_stack(graph, 0)['order'] == list(range(n))
    assert breadth_first(graph, 0)['distance'] == list(range(n))
    assert shortest_path(graph, 0, n - 1) == list(range(n))
    assert multi_source_distances(graph, [0, 600]) == list(range(600)) * 2
    assert len(dfs_events(graph, 0)) == 2 * n
finally:
    sys.setrecursionlimit(old_limit)
assert graph == before
'''
        self.assertEqual(run_code(definitions(CHAPTERS[2]), checks), '')
