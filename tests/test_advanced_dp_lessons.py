"""Execute the literal DP lessons and compare with exhaustive independent models."""

import unittest

from cs_study_map.textbook import validate_document
from test_data_structures_lessons import definitions, document, run_code

KNAPSACK = "28-knapsack"
SEQUENCES = "29-sequence-dp"
STRUCTURES = "30-interval-tree-dp"

COMMON = '''
import copy
import itertools
import math
import sys
from collections import Counter, deque
from functools import lru_cache

def positions(n):
    return [tuple(i for i in range(n) if mask & (1 << i)) for mask in range(1 << n)]

def item_instances():
    kinds = ((0, -2), (0, 3), (1, 0), (2, 3), (3, -1), (3, 5))
    for n in range(5):
        for items in itertools.product(kinds, repeat=n):
            yield [item[0] for item in items], [item[1] for item in items]

def item_outcomes(weights, values):
    return [(sum(weights[i] for i in subset), sum(values[i] for i in subset), subset)
            for subset in positions(len(weights))]

def check_items(result, weights, values, capacity, repeated=False, exact=False):
    indices = result['indices']
    assert all(0 <= i < len(weights) for i in indices)
    if not repeated:
        assert indices == sorted(set(indices))
    weight = sum(weights[i] for i in indices)
    assert weight == capacity if exact else weight <= capacity
    assert sum(values[i] for i in indices) == result['value']
    if 'weight' in result:
        assert result['weight'] == weight

def words(alphabet, maximum):
    return [''.join(items) for n in range(maximum + 1)
            for items in itertools.product(alphabet, repeat=n)]

@lru_cache(None)
def subsequences(word):
    return {''.join(word[i] for i in selected) for selected in positions(len(word))}

def common_length(a, b):
    return max(map(len, subsequences(a) & subsequences(b)))

def check_pairs(result, a, b):
    pairs = result['pairs']
    assert result['length'] == len(pairs)
    assert len({id(pair) for pair in pairs}) == len(pairs)
    assert all(0 <= i < len(a) and 0 <= j < len(b) and a[i] == b[j] for i, j in pairs)
    assert all(x[0] < y[0] and x[1] < y[1] for x, y in zip(pairs, pairs[1:]))

def edit_distances(source, alphabet, maximum, replacement):
    # Search actual strings by number of edits, without a prefix-distance recurrence.
    distances = {source: 0}
    queue = deque([source])
    while queue:
        current = queue.popleft()
        neighbors = {current[:i] + current[i + 1:] for i in range(len(current))}
        if len(current) < maximum:
            neighbors.update(current[:i] + ch + current[i:]
                             for i in range(len(current) + 1) for ch in alphabet)
        if replacement:
            neighbors.update(current[:i] + ch + current[i + 1:]
                             for i in range(len(current)) for ch in alphabet)
        for neighbor in neighbors:
            if neighbor not in distances:
                distances[neighbor] = distances[current] + 1
                queue.append(neighbor)
    return distances

def check_alignment(result, a, b):
    columns = result['columns']
    assert len({id(column) for column in columns}) == len(columns)
    assert all(x is not None or y is not None for x, y in columns)
    assert ''.join(x for x, y in columns if x is not None) == a
    assert ''.join(y for x, y in columns if y is not None) == b
    assert sum(x != y for x, y in columns) == result['distance']

@lru_cache(None)
def bracket_trees(start, stop):
    # Enumerate complete binary structures, then evaluate each independently.
    if stop == start:
        return (None,)
    if stop == start + 1:
        return (start,)
    return tuple((left, right) for cut in range(start + 1, stop)
                 for left in bracket_trees(start, cut) for right in bracket_trees(cut, stop))

def evaluate_matrix_tree(tree, dimensions):
    if tree is None:
        return 0, None, None
    if isinstance(tree, int):
        return 0, dimensions[tree], dimensions[tree + 1]
    left, right = tree
    a, rows, middle = evaluate_matrix_tree(left, dimensions)
    b, shared, columns = evaluate_matrix_tree(right, dimensions)
    assert middle == shared
    return a + b + rows * middle * columns, rows, columns

def check_merges(result, n, step_cost):
    active = {(i, i + 1) for i in range(n)}
    total = 0
    assert len(result['merges']) == max(0, n - 1)
    assert len({id(row) for row in result['merges']}) == len(result['merges'])
    for left, middle, right in result['merges']:
        assert 0 <= left < middle < right <= n
        assert (left, middle) in active and (middle, right) in active
        active.remove((left, middle))
        active.remove((middle, right))
        active.add((left, right))
        total += step_cost(left, middle, right)
    assert active == ({(0, n)} if n else set())
    assert total == result['cost']

@lru_cache(None)
def adjacent_oracle(blocks):
    # Enumerate actual next adjacent merges of the current block list.
    if len(blocks) < 2:
        return 0
    return min(blocks[i] + blocks[i + 1] + adjacent_oracle(
        blocks[:i] + (blocks[i] + blocks[i + 1],) + blocks[i + 2:])
        for i in range(len(blocks) - 1))

def valid_parent_chains(parents):
    # Follow each vertex's parent chain, rather than expand roots as the lesson does.
    n = len(parents)
    for start in range(n):
        seen = set()
        vertex = start
        while vertex != -1:
            if not 0 <= vertex < n or vertex in seen:
                return False
            seen.add(vertex)
            vertex = parents[vertex]
    return True

def all_forests(maximum):
    for n in range(maximum + 1):
        for parents in itertools.product(range(-1, n), repeat=n):
            if valid_parent_chains(parents):
                yield list(parents)

def independent_subsets(parents):
    return [subset for subset in positions(len(parents))
            if all(parents[v] == -1 or parents[v] not in subset for v in subset)]

def cover_subsets(parents):
    return [subset for subset in positions(len(parents))
            if all(parent == -1 or v in subset or parent in subset
                   for v, parent in enumerate(parents))]
'''


class AdvancedDPLessonTests(unittest.TestCase):
    def check(self, chapter, checks):
        self.assertEqual(run_code(definitions(chapter), COMMON + checks), "")

    def test_all_thirty_literal_programs_match_output(self):
        count = 0
        for identifier in (KNAPSACK, SEQUENCES, STRUCTURES):
            saved = document(identifier)
            validate_document(saved)
            content = saved["content"]
            self.assertEqual([len(content[key]) for key in
                              ("sections", "worked_examples", "exercises")], [5, 2, 3])
            for group in ("sections", "worked_examples", "exercises"):
                for index, item in enumerate(content[group]):
                    with self.subTest(chapter=identifier, group=group, index=index):
                        self.assertEqual(run_code(item["program"]["code"]), item["program"]["output"])
                        count += 1
        self.assertEqual(count, 30)

    def test_knapsack_table_all_prefixes_against_position_subsets(self):
        self.check(KNAPSACK, '''
cases = 0
for weights, values in item_instances():
    before = copy.deepcopy((weights, values))
    table = knapsack_table(weights, values, 6)
    assert len(table) == len(weights) + 1
    assert len({id(row) for row in table}) == len(table)
    for i, row in enumerate(table):
        outcomes = item_outcomes(weights[:i], values[:i])
        assert row == [max(value for weight, value, chosen in outcomes if weight <= c)
                       for c in range(7)]
    assert (weights, values) == before
    cases += 1
assert cases == 1555
''')

    def test_knapsack_recovery_and_rolling_against_all_subsets(self):
        self.check(KNAPSACK, '''
cases = 0
for weights, values in item_instances():
    outcomes = item_outcomes(weights, values)
    before = copy.deepcopy((weights, values))
    for capacity in range(8):
        expected = max(value for weight, value, chosen in outcomes if weight <= capacity)
        answer = knapsack_solution(weights, values, capacity)
        assert answer['value'] == expected == knapsack_01_value(weights, values, capacity)
        check_items(answer, weights, values, capacity)
        assert (weights, values) == before
        cases += 1
assert cases == 12440
''')

    def test_exact_knapsack_negative_values_and_zero_weights(self):
        self.check(KNAPSACK, '''
cases = 0
for weights, values in item_instances():
    outcomes = item_outcomes(weights, values)
    for capacity in range(8):
        feasible = [value for weight, value, chosen in outcomes if weight == capacity]
        answer = knapsack_exact(weights, values, capacity)
        if not feasible:
            assert answer is None
        else:
            assert answer['value'] == max(feasible)
            check_items(answer, weights, values, capacity, exact=True)
        cases += 1
assert cases == 12440
assert knapsack_exact([0, 0, 2], [4, 3, -5], 2) == {'value': 2, 'indices': [0, 1, 2]}
''')

    def test_unbounded_knapsack_against_multiplicity_vectors(self):
        self.check(KNAPSACK, '''
kinds = tuple(itertools.product((1, 2, 3), (-2, 0, 3)))
cases = 0
for n in range(4):
    for items in itertools.product(kinds, repeat=n):
        weights = [item[0] for item in items]
        values = [item[1] for item in items]
        before = copy.deepcopy((weights, values))
        for capacity in range(8):
            expected = max(sum(k * v for k, v in zip(counts, values))
                           for counts in itertools.product(*(range(capacity // w + 1) for w in weights))
                           if sum(k * w for k, w in zip(counts, weights)) <= capacity)
            answer = knapsack_unbounded(weights, values, capacity)
            assert answer['value'] == expected
            check_items(answer, weights, values, capacity, repeated=True)
            assert (weights, values) == before
            cases += 1
assert cases == 6560
assert knapsack_unbounded([3], [4], 8) == {'value': 8, 'weight': 6, 'indices': [0, 0]}
''')

    def test_knapsack_invalid_inputs_ties_and_large_integers(self):
        self.check(KNAPSACK, '''
for solve in (knapsack_table, knapsack_solution, knapsack_01_value, knapsack_unbounded, knapsack_exact):
    for weights, values, capacity in (([1], [], 2), ([], [1], 2), ([-1], [2], 3), ([], [], -1)):
        before = copy.deepcopy((weights, values))
        assert solve(weights, values, capacity) is None
        assert (weights, values) == before
for value in (-1, 0, 4):
    assert knapsack_unbounded([0], [value], 0) is None
assert knapsack_solution([1, 1], [4, 4], 1)['indices'] == [0]
assert knapsack_exact([1, 1], [4, 4], 1)['indices'] == [0]
assert knapsack_solution([0, 0], [0, -1], 0)['indices'] == []
assert knapsack_01_value([0, 2], [10 ** 80, 10 ** 90], 2) == 10 ** 80 + 10 ** 90
assert knapsack_unbounded([2], [10 ** 80], 7)['value'] == 3 * 10 ** 80
''')

    def test_position_subset_counts_include_zero_choices(self):
        self.check(KNAPSACK, '''
cases = 0
for n in range(7):
    for weights in itertools.product((0, 1, 3), repeat=n):
        weights = list(weights)
        expected = Counter(sum(weights[i] for i in selected) for selected in positions(n))
        actual = [count_01_subsets(weights, target) for target in range(sum(weights) + 2)]
        assert actual == [expected[target] for target in range(sum(weights) + 2)]
        assert sum(actual) == 2 ** n
        cases += 1
assert cases == 1093
assert count_01_subsets([0] * 100, 0) == 2 ** 100
assert count_01_subsets([-1], 0) is None and count_01_subsets([], -1) is None
''')

    def test_coin_combinations_and_sequences_against_distinct_enumerations(self):
        self.check(KNAPSACK, '''
calls = 0
for selected in positions(5):
    coins = [i + 1 for i in selected]
    ordered = Counter()
    stack = [(0, ())]
    while stack:
        total, sequence = stack.pop()
        ordered[total] += 1
        for coin in coins:
            if total + coin <= 12:
                stack.append((total + coin, sequence + (coin,)))
    for target in range(13):
        combinations = sum(sum(k * coin for k, coin in zip(counts, coins)) == target
                           for counts in itertools.product(*(range(target // coin + 1) for coin in coins)))
        for order in (coins, coins[::-1]):
            before = order.copy()
            assert coin_combinations(order, target) == combinations
            assert coin_sequences(order, target) == ordered[target]
            assert order == before
            calls += 1
assert calls == 832
''')

    def test_coin_rejection_and_empty_solution_contracts(self):
        self.check(KNAPSACK, '''
for solve in (coin_combinations, coin_sequences):
    for coins in ([0], [-1], [1, 1], [2, 3, 2]):
        before = coins.copy()
        assert solve(coins, 0) is None and solve(coins, 5) is None
        assert coins == before
    assert solve([], -1) is None
    assert solve([], 0) == 1 and solve([], 5) == 0
assert coin_sequences([1, 3, 4], 6) == 9
assert coin_combinations([1, 3, 4], 6) == 4
''')

    def test_subsequence_positions_against_all_index_combinations(self):
        self.check(SEQUENCES, '''
samples = words('ab', 5)
cases = 0
for text in samples:
    for pattern in samples:
        candidates = [selected for selected in itertools.combinations(range(len(text)), len(pattern))
                      if ''.join(text[i] for i in selected) == pattern]
        expected = list(min(candidates)) if candidates else None
        assert subsequence_positions(text, pattern) == expected
        cases += 1
assert cases == 3969
''')

    def test_lcs_tables_and_recovery_against_subsequence_intersections(self):
        self.check(SEQUENCES, '''
samples = words('ab', 4)
cases = 0
for a in samples:
    for b in samples:
        table = lcs_table(a, b)
        assert len({id(row) for row in table}) == len(table)
        for i, row in enumerate(table):
            assert row == [common_length(a[:i], b[:j]) for j in range(len(b) + 1)]
        answer = lcs_match(a, b)
        assert answer['length'] == common_length(a, b)
        check_pairs(answer, a, b)
        cases += 1
assert cases == 961
''')

    def test_rolling_lcs_preserves_old_diagonal(self):
        self.check(SEQUENCES, '''
samples = words('abc', 4)
cases = 0
for a in samples:
    for b in samples:
        assert lcs_length_rolling(a, b) == common_length(a, b)
        cases += 1
assert cases == 14641
assert lcs_length_rolling('a', 'aaaa') == 1
assert lcs_length_rolling('aaaa', 'a') == 1
''')

    def test_unicode_codepoints_ties_and_independent_rows(self):
        self.check(SEQUENCES, r'''
samples = ('', '计算计算', '计计', 'é', 'e\u0301', '😀a😀', 'a😀', 'Aa', 'aa', 'a\x00b')
for a in samples:
    for b in samples:
        expected = common_length(a, b)
        answer = lcs_match(a, b)
        assert answer['length'] == expected == lcs_length_rolling(a, b)
        check_pairs(answer, a, b)
        check_alignment(edit_alignment(a, b), a, b)
assert len('é') == 1 and len('e\u0301') == 2
assert lcs_match('é', 'e\u0301')['length'] == 0
assert edit_table('é', 'e\u0301')[1][2] == 2
assert lcs_match('ab', 'ba')['pairs'] == [[0, 1]]
table = edit_table('ab', 'ba')
assert len({id(row) for row in table}) == len(table)
table[0][0] = 99
assert table[1][0] == 1
''')

    def test_edit_distance_and_alignment_against_string_bfs(self):
        self.check(SEQUENCES, '''
samples = words('ab', 3)
cases = 0
for a in samples:
    distances = edit_distances(a, 'ab', 6, True)
    for b in samples:
        answer = edit_alignment(a, b)
        assert answer['distance'] == distances[b] == edit_table(a, b)[len(a)][len(b)]
        check_alignment(answer, a, b)
        cases += 1
assert cases == 225
assert edit_alignment('ab', 'ba')['columns'] == [['a', 'b'], ['b', 'a']]
''')

    def test_strict_lis_against_all_position_subsets(self):
        self.check(SEQUENCES, '''
cases = 0
for n in range(8):
    choices = positions(n)
    for values in itertools.product((-1, 0, 2), repeat=n):
        values = list(values)
        before = values.copy()
        expected = max(len(selected) for selected in choices
                       if all(values[i] < values[j] for i, j in zip(selected, selected[1:])))
        answer = lis(values)
        indices = answer['indices']
        assert answer['length'] == len(indices) == expected
        assert indices == sorted(set(indices))
        assert all(0 <= i < n for i in indices)
        assert all(values[i] < values[j] for i, j in zip(indices, indices[1:]))
        assert values == before
        cases += 1
assert cases == 3280
assert lis([2, 2, 2])['indices'] == [0]
assert lis([3, 1, 2, 2, 5, 4])['indices'] == [1, 2, 4]
''')

    def test_common_substring_against_all_slices_and_ties(self):
        self.check(SEQUENCES, '''
samples = words('ab', 5)
cases = 0
for a in samples:
    for b in samples:
        candidates = [(0, 0, 0)]
        for length in range(1, min(len(a), len(b)) + 1):
            candidates.extend((length, i, j) for i in range(len(a) - length + 1)
                              for j in range(len(b) - length + 1) if a[i:i+length] == b[j:j+length])
        length, i, j = min(candidates, key=lambda row: (-row[0], row[1], row[2]))
        assert longest_common_substring(a, b) == {'length': length, 'a_start': i, 'b_start': j}
        cases += 1
assert cases == 3969
assert longest_common_substring('abxcd', 'abycd') == {'length': 2, 'a_start': 0, 'b_start': 0}
''')

    def test_insertion_deletion_distance_against_bfs_without_replacement(self):
        self.check(SEQUENCES, '''
samples = words('ab', 3)
cases = 0
for a in samples:
    distances = edit_distances(a, 'ab', 6, False)
    for b in samples:
        assert insertion_deletion_distance(a, b) == distances[b]
        cases += 1
assert cases == 225
assert insertion_deletion_distance('cat', 'cut') == 2
assert edit_table('cat', 'cut')[3][3] == 1
''')

    def test_matrix_cost_and_execution_against_all_bracket_trees(self):
        self.check(STRUCTURES, '''
cases = 0
for size in range(1, 7):
    for dimensions in itertools.product((1, 2, 4), repeat=size):
        dimensions = list(dimensions)
        before = dimensions.copy()
        n = len(dimensions) - 1
        expected = min(evaluate_matrix_tree(tree, dimensions)[0] for tree in bracket_trees(0, n))
        answer = matrix_plan(dimensions)
        assert answer['cost'] == expected
        check_merges(answer, n, lambda i, k, j: dimensions[i] * dimensions[k] * dimensions[j])
        tables = matrix_tables(dimensions)
        assert len({id(row) for row in tables['cost']}) == n + 1
        assert len({id(row) for row in tables['split']}) == n + 1
        assert dimensions == before
        cases += 1
assert cases == 1092
''')

    def test_optimal_matrix_structure_counts_against_tree_enumeration(self):
        self.check(STRUCTURES, '''
cases = 0
for size in range(1, 7):
    for dimensions in itertools.product((1, 2, 4), repeat=size):
        costs = [evaluate_matrix_tree(tree, dimensions)[0]
                 for tree in bracket_trees(0, len(dimensions) - 1)]
        assert count_matrix_optima(list(dimensions)) == {'cost': min(costs), 'count': costs.count(min(costs))}
        cases += 1
assert cases == 1092
for n in range(1, 16):
    expected = math.comb(2 * (n - 1), n - 1) // n
    assert count_matrix_optima([2] * (n + 1)) == {'cost': (n - 1) * 8, 'count': expected}
''')

    def test_matrix_invalid_inputs_empty_chain_ties_and_large_dimensions(self):
        self.check(STRUCTURES, '''
for solve in (matrix_tables, matrix_plan, count_matrix_optima):
    for dimensions in ([], [0], [-1], [2, 0, 3], [2, -1]):
        assert solve(dimensions) is None
assert matrix_plan([8]) == {'cost': 0, 'merges': []}
assert matrix_plan([8, 3]) == {'cost': 0, 'merges': []}
assert count_matrix_optima([8]) == {'cost': 0, 'count': 1}
assert matrix_plan([3, 3, 3, 3]) == {'cost': 54, 'merges': [[1, 2, 3], [0, 1, 3]]}
assert matrix_plan([10 ** 30] * 4)['cost'] == 2 * 10 ** 90
''')

    def test_adjacent_merge_against_all_current_block_merges(self):
        self.check(STRUCTURES, '''
cases = 0
for n in range(7):
    for weights in itertools.product((0, 1, 3), repeat=n):
        before = list(weights)
        answer = adjacent_merge(before)
        assert answer['cost'] == adjacent_oracle(weights)
        check_merges(answer, n, lambda i, k, j: sum(weights[i:j]))
        assert before == list(weights)
        cases += 1
assert cases == 1093
assert adjacent_merge([4, 1, 3, 2])['cost'] == 20
assert adjacent_merge([-1]) is None
assert adjacent_merge([10 ** 80, 10 ** 80])['cost'] == 2 * 10 ** 80
''')

    def test_forest_validation_against_parent_chain_cycle_detection(self):
        self.check(STRUCTURES, '''
cases = valid = 0
for n in range(6):
    for parents in itertools.product(range(-1, n), repeat=n):
        parents = list(parents)
        before = parents.copy()
        answer = forest_structure(parents)
        expected = valid_parent_chains(parents)
        assert (answer is not None) == expected
        if expected:
            valid += 1
            assert answer['roots'] == [v for v in range(n) if parents[v] == -1]
            assert sorted(answer['order']) == list(range(n))
            assert len({id(row) for row in answer['children']}) == n
            place = {v: i for i, v in enumerate(answer['order'])}
            for v in range(n):
                assert answer['children'][v] == [u for u in range(n) if parents[u] == v]
                if parents[v] != -1:
                    assert place[parents[v]] < place[v]
        assert parents == before
        cases += 1
assert cases == 8477 and valid == 1442
''')

    def test_forest_independent_weights_against_all_vertex_subsets(self):
        self.check(STRUCTURES, '''
cases = 0
for parents in all_forests(4):
    candidates = independent_subsets(parents)
    for weights in itertools.product((-2, 0, 3), repeat=len(parents)):
        weights = list(weights)
        before = copy.deepcopy((weights, parents))
        expected = max(sum(weights[v] for v in subset) for subset in candidates)
        answer = forest_independent(weights, parents)
        assert answer['weight'] == expected
        selected = answer['vertices']
        assert selected == sorted(set(selected)) and tuple(selected) in candidates
        assert sum(weights[v] for v in selected) == expected
        assert (weights, parents) == before
        cases += 1
assert cases == 10588
''')

    def test_forest_cover_against_all_covers_and_complement_identity(self):
        self.check(STRUCTURES, '''
cases = 0
for parents in all_forests(4):
    candidates = cover_subsets(parents)
    for weights in itertools.product((0, 1, 4), repeat=len(parents)):
        weights = list(weights)
        before = copy.deepcopy((weights, parents))
        expected = min(sum(weights[v] for v in subset) for subset in candidates)
        answer = forest_vertex_cover(weights, parents)
        assert answer['cost'] == expected
        selected = answer['vertices']
        assert selected == sorted(set(selected)) and tuple(selected) in candidates
        assert sum(weights[v] for v in selected) == expected
        assert expected == sum(weights) - forest_independent(weights, parents)['weight']
        assert (weights, parents) == before
        cases += 1
assert cases == 10588
assert forest_vertex_cover([0, 0], [-1, 0]) == {'cost': 0, 'vertices': [1]}
''')

    def test_forest_counts_against_all_independent_subsets(self):
        self.check(STRUCTURES, '''
cases = 0
for parents in all_forests(5):
    assert count_forest_independent(parents) == len(independent_subsets(parents))
    cases += 1
assert cases == 1442
assert count_forest_independent([-1] * 100) == 2 ** 100
assert count_forest_independent([-1] + [0] * 100) == 2 ** 100 + 1
assert count_forest_independent([]) == 1
''')

    def test_long_chains_and_interval_recovery_without_recursion(self):
        self.check(STRUCTURES, '''
sys.setrecursionlimit(80)
n = 5000
parents = [-1] + list(range(n - 1))
weights = [1] * n
assert forest_independent(weights, parents)['weight'] == (n + 1) // 2
assert forest_vertex_cover(weights, parents)['cost'] == n // 2
reverse_parents = list(range(1, n)) + [-1]
assert forest_independent(weights, reverse_parents)['weight'] == (n + 1) // 2
path_size = 1200
expected = sum(math.comb(path_size - k + 1, k) for k in range((path_size + 1) // 2 + 1))
assert count_forest_independent([-1] + list(range(path_size - 1))) == expected
answer = matrix_plan([2] * 121)
assert answer['cost'] == 119 * 8
check_merges(answer, 120, lambda i, k, j: 8)
''')

    def test_forest_invalid_ranges_cycles_and_weight_contracts(self):
        self.check(STRUCTURES, '''
for parents in ([0], [1, 0], [-1, 2, 1], [-2], [1], [-1, 3], [2, 0, 1]):
    before = parents.copy()
    assert forest_structure(parents) is None
    assert count_forest_independent(parents) is None
    assert forest_independent([1] * len(parents), parents) is None
    assert forest_vertex_cover([1] * len(parents), parents) is None
    assert parents == before
assert forest_independent([], [-1]) is None
assert forest_vertex_cover([1], []) is None
assert forest_vertex_cover([-1], [-1]) is None
assert forest_independent([-1], [-1]) == {'weight': 0, 'vertices': []}
assert forest_independent([10 ** 80, 10 ** 90], [-1, 0])['weight'] == 10 ** 90
assert forest_vertex_cover([10 ** 80, 10 ** 90], [-1, 0])['cost'] == 10 ** 80
''')

    def test_returned_lists_are_fresh_and_do_not_share_input_state(self):
        self.check(KNAPSACK, '''
weights = [0, 1, 2]
values = [2, 3, 4]
for solve in (knapsack_solution, knapsack_exact):
    first = solve(weights, values, 3)
    second = solve(weights, values, 3)
    first['indices'].append(99)
    assert second['indices'] == [0, 1, 2]
assert weights == [0, 1, 2] and values == [2, 3, 4]
''')
        self.check(SEQUENCES, '''
first = lcs_match('aaa', 'aaa')
second = lcs_match('aaa', 'aaa')
first['pairs'][0][0] = 99
assert first['pairs'][1] == [1, 1] and second['pairs'][0] == [0, 0]
first = edit_alignment('aaa', 'aaa')
second = edit_alignment('aaa', 'aaa')
first['columns'][0][0] = 'x'
assert first['columns'][1] == ['a', 'a'] and second['columns'][0] == ['a', 'a']
''')
        self.check(STRUCTURES, '''
parents = [-1, 0, 0]
forest = forest_structure(parents)
forest['children'][1].append(99)
assert forest['children'][2] == [] and parents == [-1, 0, 0]
plan = matrix_plan([4, 7, 2, 5])
plan['merges'][0][0] = 99
assert plan['merges'][1] == [0, 2, 3]
assert matrix_plan([4, 7, 2, 5])['merges'][0] == [0, 1, 2]
''')


if __name__ == "__main__":
    unittest.main()
