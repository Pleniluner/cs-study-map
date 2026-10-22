"""Execute published programs; compare graph algorithms with independent small-graph oracles."""

import unittest

from cs_study_map.textbook import validate_document
from test_data_structures_lessons import definitions, document, run_code

TOPO = "22-topological-sort"
SHORTEST = "23-weighted-shortest-paths"
MST = "24-minimum-spanning-trees"

TOPO_ORACLE = '''
import itertools
import copy

def digraphs(maximum):
    for n in range(maximum + 1):
        pairs = [(u, v) for u in range(n) for v in range(n) if u != v]
        for bits in itertools.product((0, 1), repeat=len(pairs)):
            graph = [[] for _ in range(n)]
            for (u, v), present in zip(pairs, bits):
                if present:
                    graph[u].append(v)
            yield graph

def orders_of(graph):
    return [list(order) for order in itertools.permutations(range(len(graph)))
            if all(order.index(u) < order.index(v)
                   for u, row in enumerate(graph) for v in row)]

def reachability(graph):
    n = len(graph)
    reach = [[v in graph[u] for v in range(n)] for u in range(n)]
    for k in range(n):
        for u in range(n):
            for v in range(n):
                reach[u][v] = reach[u][v] or (reach[u][k] and reach[k][v])
    return reach

def paths_from(graph, start):
    paths = []
    pending = [[start]]
    while pending:
        path = pending.pop()
        paths.append(path)
        for target in graph[path[-1]]:
            assert target not in path
            pending.append(path + [target])
    return paths
'''

WEIGHT_ORACLE = '''
import itertools
import copy

def weighted_graphs(n, weights, directed=True):
    pairs = [(u, v) for u in range(n) for v in range(n)
             if (u != v if directed else u < v)]
    for values in itertools.product([None] + list(weights), repeat=len(pairs)):
        graph = [[] for _ in range(n)]
        edges = []
        for (u, v), w in zip(pairs, values):
            if w is not None:
                graph[u].append([v, w])
                edges.append([u, v, w])
                if not directed:
                    graph[v].append([u, w])
        yield graph, edges

def floyd(graph):
    n = len(graph)
    distance = [[float('inf')] * n for _ in range(n)]
    for u in range(n):
        distance[u][u] = 0
        for v, w in graph[u]:
            distance[u][v] = min(distance[u][v], w)
    for k in range(n):
        for u in range(n):
            for v in range(n):
                distance[u][v] = min(distance[u][v], distance[u][k] + distance[k][v])
    return distance

def inspect_shortest(graph, start, result, expected):
    actual = result['distance']
    parent = result['parent']
    assert len(actual) == len(parent) == len(graph)
    assert actual == [None if d == float('inf') else d for d in expected]
    for target, value in enumerate(actual):
        if value is None:
            assert parent[target] is None
        else:
            vertex = target
            seen = set()
            cost = 0
            while parent[vertex] is not None:
                assert vertex not in seen
                seen.add(vertex)
                source = parent[vertex]
                matches = [w for v, w in graph[source] if v == vertex]
                assert len(matches) == 1
                cost += matches[0]
                vertex = source
            assert vertex == start and cost == value

def bounded_walks(graph, start, k):
    best = [None] * len(graph)
    pending = [(start, 0, 0)]
    while pending:
        vertex, cost, length = pending.pop()
        if best[vertex] is None or cost < best[vertex]:
            best[vertex] = cost
        if length < k:
            pending.extend((v, cost + w, length + 1) for v, w in graph[vertex])
    return best
'''

FOREST_ORACLE = '''
def partition(n, edges):
    graph = [set() for _ in range(n)]
    for u, v, w in edges:
        graph[u].add(v)
        graph[v].add(u)
    unseen = set(range(n))
    groups = set()
    while unseen:
        pending = [min(unseen)]
        group = set()
        while pending:
            vertex = pending.pop()
            if vertex not in group:
                group.add(vertex)
                pending.extend(graph[vertex] - group)
        unseen -= group
        groups.add(frozenset(group))
    return groups

def forest_optima(n, edges):
    best = {}
    for mask in range(1 << len(edges)):
        chosen = [edge for i, edge in enumerate(edges) if mask & (1 << i)]
        groups = partition(n, chosen)
        if len(chosen) == n - len(groups):
            k = len(groups)
            weight = sum(edge[2] for edge in chosen)
            best[k] = min(best.get(k, float('inf')), weight)
    return best

def inspect_forest(n, original, result, k, weight):
    allowed = {tuple(edge) for edge in original}
    chosen = result['edges']
    normalized = [(min(u, v), max(u, v), w) for u, v, w in chosen]
    assert len(set(normalized)) == len(chosen)
    assert set(normalized) <= allowed
    assert len(chosen) == n - k
    assert len(partition(n, chosen)) == k
    assert result['components'] == k
    assert result['weight'] == weight == sum(edge[2] for edge in chosen)
'''


class WeightedGraphLessonTests(unittest.TestCase):
    def test_all_thirty_literal_programs_match_expected_output(self):
        count = 0
        for identifier in (TOPO, SHORTEST, MST):
            saved = document(identifier)
            validate_document(saved)
            content = saved["content"]
            self.assertEqual([len(content[group]) for group in
                              ("sections", "worked_examples", "exercises")], [5, 2, 3])
            for group in ("sections", "worked_examples", "exercises"):
                for index, item in enumerate(content[group]):
                    with self.subTest(chapter=identifier, group=group, index=index):
                        self.assertEqual(run_code(item["program"]["code"]), item["program"]["output"])
                        count += 1
        self.assertEqual(count, 30)

    def test_topological_orders_and_cycles_against_all_permutations(self):
        run_code(definitions(TOPO), TOPO_ORACLE + '''
count = 0
for graph in digraphs(4):
    before = copy.deepcopy(graph)
    valid = orders_of(graph)
    k = kahn(graph)
    d = dfs_topology(graph)
    if valid:
        assert k['order'] in valid and d['order'] in valid
        assert k['blocked'] == d['cycle'] == []
        assert topological_order_valid(graph, k['order'])
    else:
        assert k['blocked'] and d['order'] == []
        cycle = d['cycle']
        assert len(cycle) >= 2 and cycle[0] == cycle[-1]
        assert len(set(cycle[:-1])) == len(cycle) - 1
        assert all(v in graph[u] for u, v in zip(cycle, cycle[1:]))
    assert graph == before
    count += 1
assert count == 4166
''')

    def test_blocked_means_cycle_and_downstream_not_just_cycle_members(self):
        run_code(definitions(TOPO), TOPO_ORACLE + '''
for graph in digraphs(4):
    reach = reachability(graph)
    expected = [v for v in range(len(graph))
                if any(reach[u][u] and reach[u][v] for u in range(len(graph)))]
    result = kahn(graph)
    assert result['blocked'] == expected
    removed = set()
    for v in result['order']:
        assert all(u in removed for u, row in enumerate(graph) if v in row)
        removed.add(v)
    assert removed.isdisjoint(expected)
    assert removed | set(expected) == set(range(len(graph)))
''')

    def test_unique_and_smallest_orders_against_permutation_oracle(self):
        run_code(definitions(TOPO), TOPO_ORACLE + '''
for graph in digraphs(4):
    valid = orders_of(graph)
    result = topological_unique(graph)
    smallest = topological_smallest(graph)
    if not valid:
        assert result is None and smallest is None
    else:
        assert result['unique'] == (len(valid) == 1)
        assert result['order'] in valid
        assert smallest == min(valid)
assert kahn([[1], [], []])['order'] == [0, 2, 1]
assert topological_smallest([[1], [], []]) == [0, 1, 2]
''')

    def test_topological_self_loops_invalid_orders_and_long_chain(self):
        run_code(definitions(TOPO), '''
assert dfs_topology([[0]]) == {'order': [], 'cycle': [0, 0]}
assert kahn([[0], []]) == {'order': [1], 'blocked': [0]}
assert topological_unique([[0]]) is None
assert topological_smallest([[0]]) is None
for order in ([0], [0, 0], [0, -1], [0, 2], [1, 0]):
    assert not topological_order_valid([[1], []], order)
assert topological_order_valid([], [])
n = 5000
chain = [[v + 1] for v in range(n - 1)] + [[]]
assert dfs_topology(chain)['order'] == list(range(n))
assert kahn(chain)['order'] == list(range(n))
# A black cross edge is not a back edge; an unreachable cycle still is a failure.
assert dfs_topology([[1, 2], [3], [3], []])['cycle'] == []
assert dfs_topology([[], [2], [1]])['cycle'] == [1, 2, 1]
''')

    def test_layers_path_counts_and_finish_times_against_path_enumeration(self):
        run_code(definitions(TOPO), TOPO_ORACLE + '''
for graph in digraphs(4):
    n = len(graph)
    valid = orders_of(graph)
    durations = [(v * 3 + 2) % 5 for v in range(n)]
    layer_result = topological_layers(graph)
    result = earliest_finish(graph, durations)
    if not valid:
        assert result is None and layer_result['blocked']
        for start in range(n):
            assert count_dag_paths(graph, start) is None
    else:
        all_paths = [p for start in range(n) for p in paths_from(graph, start)]
        expected_finish = [max(sum(durations[x] for x in p) for p in all_paths if p[-1] == v)
                           for v in range(n)]
        assert result['finish'] == expected_finish
        assert result['start'] == [expected_finish[v] - durations[v] for v in range(n)]
        assert result['total'] == max(expected_finish, default=0)
        levels = {v: i for i, row in enumerate(layer_result['layers']) for v in row}
        assert len(levels) == n and layer_result['blocked'] == []
        for v in range(n):
            assert levels[v] == max(len(p) - 1 for p in all_paths if p[-1] == v)
        for start in range(n):
            paths = paths_from(graph, start)
            assert count_dag_paths(graph, start) == [sum(p[-1] == v for p in paths) for v in range(n)]
    assert count_dag_paths(graph, -1) is None
    assert count_dag_paths(graph, n) is None
assert earliest_finish([[1], []], [0, 0])['total'] == 0
''')

    def test_kahn_trace_snapshots_match_remaining_dependencies(self):
        run_code(definitions(TOPO), TOPO_ORACLE + '''
for graph in digraphs(3):
    result = kahn_trace(graph)
    removed = set()
    for source, ready, degree in result['trace']:
        assert all(u in removed for u, row in enumerate(graph) if source in row)
        removed.add(source)
        expected = [sum(v in row for u, row in enumerate(graph) if u not in removed)
                    for v in range(len(graph))]
        assert degree == expected
        assert set(ready) == {v for v in range(len(graph)) if v not in removed and degree[v] == 0}
    assert result['order'] == kahn(graph)['order']
    assert result['blocked'] == kahn(graph)['blocked']
    states = [event[2] for event in result['trace']]
    assert len({id(row) for row in states}) == len(states)
''')

    def test_graph_construction_and_path_weight_contract(self):
        run_code(definitions(SHORTEST), '''
import copy
edges = [[0, 1, 0], [1, 2, -1]]
before = copy.deepcopy(edges)
directed = weighted_adjacency(4, edges, True)
undirected = weighted_adjacency(4, edges, False)
assert edges == before
assert len({id(row) for row in directed}) == 4
assert directed == [[[1, 0]], [[2, -1]], [], []]
assert undirected == [[[1, 0]], [[0, 0], [2, -1]], [[1, -1]], []]
assert path_weight(directed, [0, 1, 2]) == -1
assert path_weight(directed, [2, 1]) is None
assert path_weight(directed, []) is None
assert path_weight(directed, [-1]) is None
assert path_weight(directed, [4]) is None
assert path_weight(directed, [3]) == 0
directed[0][0][1] = 99
assert edges == before and undirected[0][0][1] == 0
''')

    def test_nonnegative_shortest_paths_against_floyd(self):
        run_code(definitions(SHORTEST), WEIGHT_ORACLE + '''
count = 0
for graph, edges in weighted_graphs(3, (0, 2, 5)):
    before = copy.deepcopy(graph)
    expected = floyd(graph)
    for start in range(3):
        for algorithm in (dijkstra_scan, dijkstra_heap, bellman_ford):
            result = algorithm(graph, start)
            assert not result.get('negative_cycle', False)
            inspect_shortest(graph, start, result, expected[start])
    assert graph == before
    count += 1
assert count == 4096
''')

    def test_signed_bellman_ford_and_reachable_negative_cycles_against_floyd(self):
        run_code(definitions(SHORTEST), WEIGHT_ORACLE + '''
for graph, edges in weighted_graphs(3, (-2, 0, 3)):
    before = copy.deepcopy(graph)
    expected = floyd(graph)
    for start in range(3):
        bad = any(expected[start][v] != float('inf') and expected[v][v] < 0 for v in range(3))
        result = bellman_ford(graph, start)
        assert result['negative_cycle'] == bad
        if bad:
            assert result['distance'] == result['parent'] == []
        else:
            inspect_shortest(graph, start, result, expected[start])
    assert graph == before
for weight in (-1, 0, 2):
    result = bellman_ford([[[0, weight]]], 0)
    assert result['negative_cycle'] == (weight < 0)
''')

    def test_dag_signed_distances_and_global_cycle_rejection(self):
        run_code(definitions(SHORTEST), WEIGHT_ORACLE + '''
for graph, edges in weighted_graphs(3, (-2, 0, 3)):
    valid = any(all(order.index(u) < order.index(v) for u, v, w in edges)
                for order in itertools.permutations(range(3)))
    expected = floyd(graph)
    for start in range(3):
        result = dag_shortest_paths(graph, start)
        if valid:
            inspect_shortest(graph, start, result, expected[start])
        else:
            assert result is None
assert dag_shortest_paths([[], [[2, 0]], [[1, 0]]], 0) is None
''')

    def test_shortest_path_boundaries_zero_cycles_and_large_integers(self):
        run_code(definitions(SHORTEST), WEIGHT_ORACLE + '''
for algorithm in (dijkstra_scan, dijkstra_heap, bellman_ford, dag_shortest_paths):
    assert algorithm([], 0) is None
    assert algorithm([[]], -1) is None
    assert algorithm([[]], 1) is None
    assert algorithm([[]], 0)['distance'] == [0]
negative_unreachable = [[], [[2, -3]], [[1, 1]]]
for algorithm in (dijkstra_scan, dijkstra_heap):
    assert algorithm(negative_unreachable, 0) is None
assert bellman_ford(negative_unreachable, 0)['distance'] == [0, None, None]
assert bellman_ford(negative_unreachable, 1)['negative_cycle']
huge = 10 ** 100
graphs = [
    [[[1, 0], [2, 0]], [[2, 0]], [[0, 0], [1, 0]]],
    [[[1, huge], [2, huge + 5]], [[2, 2]], []],
    [[[0, 0], [1, 0]], [[1, 0]]],
]
for graph in graphs:
    expected = floyd(graph)
    for algorithm in (dijkstra_scan, dijkstra_heap, bellman_ford):
        result = algorithm(graph, 0)
        inspect_shortest(graph, 0, result, expected[0])
        for target in range(len(graph)):
            path = recover_path(result['distance'], result['parent'], target)
            assert path_weight(graph, path) == result['distance'][target]
assert recover_path([0, None], [None, None], 1) == []
assert recover_path([0], [None], -1) == []
assert recover_path([0], [None], 1) == []
''')

    def test_relaxation_is_strict_and_does_not_create_reachability(self):
        run_code(definitions(SHORTEST), '''
distance = [0, None, None]
parent = [None, None, None]
assert not relax(distance, parent, 1, 2, -100)
assert distance == [0, None, None]
assert relax(distance, parent, 0, 1, -1)
assert not relax(distance, parent, 0, 1, -1)
assert parent == [None, 0, None]
assert relax(distance, parent, 1, 2, 0)
assert not relax(distance, parent, 2, 1, 0)
assert parent == [None, 0, 1]
''')

    def test_bounded_walks_against_explicit_walk_enumeration(self):
        run_code(definitions(SHORTEST), WEIGHT_ORACLE + '''
for graph, edges in weighted_graphs(3, (-2, 1)):
    before = copy.deepcopy(graph)
    for start in range(3):
        for k in range(5):
            assert at_most_k_edges(graph, start, k) == bounded_walks(graph, start, k)
    assert graph == before
graph = [[[1, 4], [2, 9]], [[2, -2]], []]
assert at_most_k_edges(graph, 0, 1) == [0, 4, 9]
assert at_most_k_edges(graph, 0, 2) == [0, 4, 2]
assert at_most_k_edges(graph, 0, -1) is None
assert at_most_k_edges(graph, -1, 1) is None
assert at_most_k_edges(graph, 3, 1) is None
assert at_most_k_edges([], 0, 0) is None
''')

    def test_lazy_heap_stale_records_scan_each_reachable_row_once(self):
        run_code(definitions(SHORTEST), '''
class Row(list):
    def __init__(self, values):
        super().__init__(values)
        self.scans = 0
    def __iter__(self):
        self.scans += 1
        return super().__iter__()

graph = [Row(row) for row in [
    [[1, 7], [2, 2]], [[3, 2]], [[1, 1], [3, 8], [4, 12]], [[4, 1]], [], []]]
result = dijkstra_heap_trace(graph, 0)
settled = [event[1] for event in result['events'] if event[0] == 'settle']
skipped = [event[1] for event in result['events'] if event[0] == 'skip']
assert settled == [0, 2, 1, 3, 4] and skipped == [1, 3, 4]
# One scan for the nonnegative contract, then one per reachable vertex.
assert [row.scans for row in graph] == [2, 2, 2, 2, 2, 1]
assert len(result['events']) <= sum(len(row) for row in graph) + 1
''')

    def test_lazy_heap_can_hold_more_than_one_record_per_vertex(self):
        run_code(definitions(SHORTEST), '''
real_push = heap_push
peak = [0]
def counted_push(heap, value):
    real_push(heap, value)
    peak[0] = max(peak[0], len(heap))
heap_push = counted_push
n = 18
graph = [[] for _ in range(n)]
for u in range(n):
    for v in range(u + 1, n):
        graph[u].append([v, 1 if v == u + 1 else 1000 - 20 * u + v])
result = dijkstra_heap(graph, 0)
assert result['distance'] == list(range(n))
assert peak[0] > n
''')

    def test_bellman_ford_reverse_chain_needs_multiple_rounds_but_flattens_once(self):
        run_code(definitions(SHORTEST), '''
class Row(list):
    def __init__(self, values):
        super().__init__(values)
        self.scans = 0
    def __iter__(self):
        self.scans += 1
        return super().__iter__()
n = 9
graph = [Row([])] + [Row([[v - 1, -1]]) for v in range(1, n)]
calls = [0]
original = relax
def counted(*args):
    calls[0] += 1
    return original(*args)
relax = counted
result = bellman_ford(graph, n - 1)
assert result['distance'] == list(range(-(n - 1), 1))
assert calls[0] == (n - 1) * (n - 1)
assert all(row.scans == 1 for row in graph)
calls[0] = 0
bellman_ford([[[1, 1]], []], 0)
assert calls[0] == 1
''')

    def test_prim_and_kruskal_against_exhaustive_forest_subsets(self):
        run_code(definitions(MST), WEIGHT_ORACLE + FOREST_ORACLE + '''
count = 0
for graph, edges in weighted_graphs(4, (-2, 0, 3), directed=False):
    before_graph, before_edges = copy.deepcopy(graph), copy.deepcopy(edges)
    original_groups = partition(4, edges)
    k = len(original_groups)
    best = forest_optima(4, edges)
    for result in (prim_forest(graph), kruskal_forest(4, edges)):
        inspect_forest(4, edges, result, k, best[k])
        assert partition(4, result['edges']) == original_groups
    assert graph == before_graph and edges == before_edges
    count += 1
assert count == 4096
''')

    def test_exact_k_forest_against_exhaustive_subsets(self):
        run_code(definitions(MST), WEIGHT_ORACLE + FOREST_ORACLE + '''
for graph, edges in weighted_graphs(4, (-2, 0, 3), directed=False):
    best = forest_optima(4, edges)
    for k in range(1, 5):
        result = minimum_k_forest(4, edges, k)
        if k not in best:
            assert result is None
        else:
            inspect_forest(4, edges, result, k, best[k])
assert minimum_k_forest(0, [], 0) == {'edges': [], 'weight': 0, 'components': 0}
for n in range(5):
    assert minimum_k_forest(n, [], -1) is None
    assert minimum_k_forest(n, [], n + 1) is None
    if n:
        assert minimum_k_forest(n, [], 0) is None
assert minimum_k_forest(2, [[0, 1, -100]], 2)['weight'] == 0
''')

    def test_minimum_tree_empty_singleton_and_disconnected_contract(self):
        run_code(definitions(MST), '''
empty = {'edges': [], 'weight': 0, 'components': 0}
single = {'edges': [], 'weight': 0, 'components': 1}
assert prim_forest([]) == kruskal_forest(0, []) == empty
assert prim_forest([[]]) == kruskal_forest(1, []) == minimum_tree(1, []) == single
assert minimum_tree(0, []) is None
assert minimum_tree(2, []) is None
assert minimum_tree(2, [[0, 1, 0]])['weight'] == 0
assert minimum_tree(2, [[0, 1, -10 ** 100]])['weight'] == -10 ** 100
''')

    def test_dsu_mixed_operations_against_explicit_sets(self):
        run_code(definitions(MST), '''
import random
rng = random.Random(73024)
for n in range(1, 35):
    dsu = new_dsu(n)
    groups = [{v} for v in range(n)]
    for step in range(100):
        a, b = rng.randrange(n), rng.randrange(n)
        left = next(group for group in groups if a in group)
        right = next(group for group in groups if b in group)
        different = left is not right
        assert join(dsu, a, b) == different
        if different:
            groups.remove(left)
            groups.remove(right)
            groups.append(left | right)
        assert dsu['components'] == len(groups)
        for group in groups:
            roots = {find_root(dsu, v) for v in group}
            assert len(roots) == 1
            root = roots.pop()
            assert dsu['size'][root] == len(group)
            assert dsu['parent'][root] == root
assert new_dsu(0) == {'parent': [], 'size': [], 'components': 0}
''')

    def test_union_by_size_height_and_full_path_compression(self):
        run_code(definitions(MST), '''
n = 64
dsu = new_dsu(n)
width = 1
while width < n:
    for start in range(0, n, 2 * width):
        assert join(dsu, start, start + width)
    width *= 2
path = []
v = n - 1
while dsu['parent'][v] != v:
    path.append(v)
    v = dsu['parent'][v]
assert len(path) == 6
assert find_root(dsu, n - 1) == v
assert all(dsu['parent'][x] == v for x in path)
assert not join(dsu, 0, n - 1)
assert dsu['components'] == 1 and dsu['size'][v] == n
''')

    def test_kruskal_trace_rejections_and_equal_weight_alternatives(self):
        run_code(definitions(MST), FOREST_ORACLE + '''
edges = [[0, 1, 1], [1, 2, 2], [0, 2, 3], [2, 3, 10], [1, 3, 11]]
result = kruskal_trace(4, edges)
accepted = []
for action, edge, remaining in result['events']:
    before = partition(4, accepted)
    after = partition(4, accepted + [edge])
    assert (action == 'take') == (len(after) == len(before) - 1)
    if action == 'take':
        accepted.append(edge)
    assert remaining == len(partition(4, accepted))
assert result['weight'] == 13
equal = [[0, 1, 1], [0, 2, 1], [1, 2, 1]]
for arrangement in (equal, list(reversed(equal))):
    assert kruskal_forest(3, arrangement)['weight'] == 2
assert total_weight([[0, 1, 1], [1, 2, 1]]) == total_weight([[0, 1, 1], [0, 2, 1]])
''')

    def test_adding_new_edge_against_exhaustive_spanning_tree_oracle(self):
        run_code(definitions(MST), WEIGHT_ORACLE + FOREST_ORACLE + '''
checked = 0
for graph, edges in weighted_graphs(4, (-3, 2), directed=False):
    if len(partition(4, edges)) != 1:
        continue
    tree = kruskal_forest(4, edges)['edges']
    old_pairs = {(u, v) for u, v, w in edges}
    before = copy.deepcopy(tree)
    for u in range(4):
        for v in range(u + 1, 4):
            if (u, v) not in old_pairs:
                for w in (-5, 0, 6):
                    edge = [u, v, w]
                    expected = forest_optima(4, edges + [edge])[1]
                    assert improved_tree_weight(4, tree, edge) == expected
                    checked += 1
    assert tree == before
assert checked > 500
''')

    def test_tree_path_maximum_handles_all_negative_edges_and_missing_paths(self):
        run_code(definitions(MST), '''
graph = weighted_adjacency(5, [[0, 1, -5], [1, 2, -2], [2, 3, -8]], False)
assert forest_path_max(graph, 0, 3) == -2
assert forest_path_max(graph, 2, 3) == -8
assert forest_path_max(graph, 3, 0) == -2
assert forest_path_max(graph, 0, 0) is None
assert forest_path_max(graph, 0, 4) is None
assert forest_path_max(graph, -1, 2) is None
assert forest_path_max(graph, 0, 5) is None
assert forest_path_max([], 0, 0) is None
''')


if __name__ == "__main__":
    unittest.main()
