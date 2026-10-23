"""Run literal lessons and compare search, greedy and DP with independent oracles."""

import unittest

from cs_study_map.textbook import validate_document
from test_data_structures_lessons import definitions, document, run_code

BACKTRACK = "25-backtracking"
GREEDY = "26-greedy-algorithms"
DP = "27-dynamic-programming"

COMMON = '''
import copy
import itertools
import math
from collections import Counter, deque
from functools import lru_cache

def inspect_lists(actual, expected):
    encoded = [tuple(row) for row in actual]
    assert len(encoded) == len(set(encoded))
    assert set(encoded) == set(expected)
    assert len({id(row) for row in actual}) == len(actual)

def position_subsets(n):
    return [tuple(i for i in range(n) if mask & (1 << i)) for mask in range(1 << n)]

def interval_optimum(intervals):
    return max((len(chosen) for chosen in position_subsets(len(intervals))
                if all(intervals[a][1] <= intervals[b][0] or intervals[b][1] <= intervals[a][0]
                       for a, b in itertools.combinations(chosen, 2))), default=0)

@lru_cache(None)
def merge_oracle(weights):
    if len(weights) <= 1:
        return 0
    return min(weights[i] + weights[j] + merge_oracle(tuple(sorted(
                   [v for k, v in enumerate(weights) if k not in (i, j)] + [weights[i] + weights[j]])))
               for i in range(len(weights)) for j in range(i + 1, len(weights)))

def monotone_paths(rows, columns):
    if not rows or not columns:
        return []
    paths = []
    for down_positions in itertools.combinations(range(rows + columns - 2), rows - 1):
        row = column = 0
        path = [(0, 0)]
        for step in range(rows + columns - 2):
            if step in down_positions:
                row += 1
            else:
                column += 1
            path.append((row, column))
        paths.append(path)
    return paths
'''


class StrategyLessonTests(unittest.TestCase):
    def test_all_thirty_literal_programs_match_output(self):
        count = 0
        for identifier in (BACKTRACK, GREEDY, DP):
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

    def test_binary_and_subsets_against_products_and_bit_masks(self):
        run_code(definitions(BACKTRACK), COMMON + '''
for n in range(9):
    strings = binary_strings(n)
    inspect_lists(strings, itertools.product((0, 1), repeat=n))
    assert strings == sorted(strings)
    actual = subsets(n)
    inspect_lists(actual, position_subsets(n))
    assert all(row == sorted(row) for row in actual)
    assert len(actual) == 2 ** n
assert binary_strings(-1) is None and subsets(-1) is None
''')

    def test_position_permutations_against_library_enumeration(self):
        run_code(definitions(BACKTRACK), COMMON + '''
for n in range(8):
    actual = permutations(n)
    inspect_lists(actual, itertools.permutations(range(n)))
    assert len(actual) == math.factorial(n)
    assert actual == sorted(actual)
assert permutations(-1) is None
''')

    def test_combinations_include_empty_and_impossible_sizes(self):
        run_code(definitions(BACKTRACK), COMMON + '''
for n in range(10):
    for k in range(n + 3):
        actual = combinations(n, k)
        inspect_lists(actual, itertools.combinations(range(n), k))
        assert actual == sorted(actual)
assert combinations(3, -1) is None and combinations(-1, 0) is None
''')

    def test_subset_sum_all_small_inputs_and_pruning_equivalence(self):
        run_code(definitions(BACKTRACK), COMMON + '''
cases = 0
for n in range(6):
    for values in itertools.product((0, 1, 3), repeat=n):
        values = list(values)
        before = values.copy()
        candidates = position_subsets(n)
        for target in range(sum(values) + 3):
            expected = [indices for indices in candidates if sum(values[i] for i in indices) == target]
            plain = subset_sum(values, target, False)
            cut = subset_sum(values, target, True)
            inspect_lists(plain['solutions'], expected)
            inspect_lists(cut['solutions'], expected)
            assert plain['solutions'] == cut['solutions']
            assert cut['calls'] <= plain['calls'] == 2 ** (n + 1) - 1
            assert values == before
            cases += 1
assert cases > 3000
assert subset_sum([-1, 2], 1, False) is None
assert subset_sum([0], -1, True) is None
''')

    def test_pruning_statistics_distinguish_no_gain_and_root_rejection(self):
        run_code(definitions(BACKTRACK), COMMON + '''
for enabled in (False, True):
    result = subset_sum([0, 2, 3, 5], 5, enabled)
    assert result['calls'] == 31 and len(result['solutions']) == 4
assert subset_sum([2, 3, 5], 11, True) == {'solutions': [], 'calls': 1}
for n in range(9):
    result = subset_sum([0] * n, 0, True)
    assert len(result['solutions']) == 2 ** n
    assert result['calls'] == 2 ** (n + 1) - 1
''')

    def test_queens_against_all_column_permutations(self):
        run_code(definitions(BACKTRACK), COMMON + '''
known_counts = [1, 1, 0, 0, 2, 10, 4, 40, 92]
for n in range(9):
    expected = [p for p in itertools.permutations(range(n))
                if all(abs(p[a] - p[b]) != b - a for a in range(n) for b in range(a + 1, n))]
    actual = queens(n)
    inspect_lists(actual, expected)
    assert len(actual) == known_counts[n]
assert queens(-1) is None
''')

    def test_value_permutation_deduplication_and_input_identity(self):
        run_code(definitions(BACKTRACK), COMMON + '''
for n in range(6):
    for values in itertools.product((-1, 0, 2), repeat=n):
        values = list(values)
        before = values.copy()
        actual = unique_permutations(values)
        inspect_lists(actual, set(itertools.permutations(values)))
        assert values == before
        assert all(Counter(row) == Counter(values) for row in actual)
        if actual:
            actual[0].append(99)
            assert values == before
assert unique_permutations([2, 1, 2]) == [[2, 1, 2], [2, 2, 1], [1, 2, 2]]
''')

    def test_balanced_brackets_against_all_binary_strings(self):
        run_code(definitions(BACKTRACK), COMMON + '''
for n in range(7):
    expected = set()
    for candidate in itertools.product('()', repeat=2 * n):
        balance = 0
        valid = True
        for char in candidate:
            balance += 1 if char == '(' else -1
            valid = valid and balance >= 0
        if valid and balance == 0:
            expected.add(''.join(candidate))
    actual = balanced(n)
    assert set(actual) == expected and len(actual) == len(expected)
    assert actual == sorted(actual)
assert balanced(-1) is None
''')

    def test_simple_paths_all_small_digraphs_against_vertex_permutations(self):
        run_code(definitions(BACKTRACK), COMMON + '''
graphs = 0
for n in range(1, 5):
    edges = [(u, v) for u in range(n) for v in range(n) if u != v]
    for mask in range(1 << len(edges)):
        graph = [[] for _ in range(n)]
        for index, (u, v) in enumerate(edges):
            if mask & (1 << index):
                graph[u].append(v)
        before = copy.deepcopy(graph)
        for start in range(n):
            for target in range(n):
                expected = []
                if start == target:
                    expected = [(start,)]
                else:
                    middle = [v for v in range(n) if v not in (start, target)]
                    for size in range(len(middle) + 1):
                        for inner in itertools.permutations(middle, size):
                            path = (start,) + inner + (target,)
                            if all(v in graph[u] for u, v in zip(path, path[1:])):
                                expected.append(path)
                inspect_lists(simple_paths(graph, start, target), expected)
        assert graph == before
        graphs += 1
assert graphs == 4165
assert simple_paths([], 0, 0) is None
assert simple_paths([[0, 1], [1]], 0, 1) == [[0, 1]]
assert simple_paths([[]], -1, 0) is None
''')

    def test_greedy_change_conservation_and_counterexamples(self):
        run_code(definitions(GREEDY), COMMON + '''
for mask in range(64):
    coins = [c for c in range(1, 7) if mask & (1 << (c - 1))]
    before = coins.copy()
    for amount in range(25):
        actual = greedy_change(coins, amount)
        assert sum(actual['coins']) + actual['remaining'] == amount
        assert all(c in coins for c in actual['coins'])
        assert actual['coins'] == sorted(actual['coins'], reverse=True)
        assert not coins or actual['remaining'] < min(coins)
        assert coins == before
assert greedy_change([1, 4, 6], 8)['coins'] == [6, 1, 1]
assert greedy_change([4, 6], 8)['remaining'] == 2
assert 4 + 4 == 8
assert greedy_change([1, 0], 0) is None
assert greedy_change([-1, 2], 3) is None
assert greedy_change([1], -1) is None
''')

    def test_interval_schedule_and_removals_against_all_subsets(self):
        run_code(definitions(GREEDY), COMMON + '''
candidates = [(a, b) for a in range(-2, 3) for b in range(a + 1, 3)]
cases = 0
for n in range(5):
    for records in itertools.combinations_with_replacement(candidates, n):
        for source in (records, records[::-1]):
            intervals = [list(record) for record in source]
            before = copy.deepcopy(intervals)
            optimum = interval_optimum(intervals)
            chosen = interval_schedule(intervals)
            assert valid_schedule(intervals, chosen) and len(chosen) == optimum
            result = minimum_removals(intervals)
            assert valid_schedule(intervals, result['kept'])
            assert len(result['removed']) == n - optimum
            assert set(result['kept']).isdisjoint(result['removed'])
            assert set(result['kept']) | set(result['removed']) == set(range(n))
            assert intervals == before
            cases += 1
assert cases == 2002
''')

    def test_interval_contracts_and_invalid_schedules(self):
        run_code(definitions(GREEDY), COMMON + '''
for invalid in ([[1, 1]], [[4, 1]], [[0, 2], [3, 3]]):
    assert interval_schedule(invalid) is None
    assert minimum_removals(invalid) is None
intervals = [[-4, -2], [-2, 0]]
assert valid_schedule(intervals, [0, 1])
for order in ([0, 0], [1, 0], [-1], [2]):
    assert not valid_schedule(intervals, order)
assert interval_schedule([[0, 2], [0, 2], [2, 3]]) == [0, 2]
assert interval_schedule([[0, 10], [1, 3], [3, 5], [5, 7]]) == [1, 2, 3]
assert interval_schedule([[0, 3], [3, 6], [2, 4]]) == [0, 1]
''')

    def test_merge_against_all_pair_choices_and_trace_multisets(self):
        run_code(definitions(GREEDY), COMMON + '''
cases = 0
for n in range(7):
    for weights in itertools.combinations_with_replacement(range(4), n):
        original = list(reversed(weights))
        before = original.copy()
        result = optimal_merge(original)
        assert result['cost'] == merge_oracle(weights)
        remaining = list(original)
        cost = 0
        for first, second, total in result['merges']:
            assert first in remaining
            remaining.remove(first)
            assert second in remaining
            remaining.remove(second)
            assert total == first + second
            remaining.append(total)
            cost += total
        assert len(result['merges']) == max(0, n - 1)
        assert cost == result['cost'] and original == before
        assert remaining == ([sum(weights)] if weights else [])
        cases += 1
assert cases == 210
assert optimal_merge([1, -1]) is None
''')

    def test_huffman_prefix_codes_optimum_and_independent_decoding(self):
        run_code(definitions(GREEDY), COMMON + '''
for n in range(6):
    for weights in itertools.product((1, 2, 4), repeat=n):
        values = list(weights)
        codes = huffman_codes(values)
        assert values == list(weights) and len(codes) == n
        assert len({id(code) for code in codes}) == n
        assert all(bit in (0, 1) for code in codes for bit in code)
        assert sum(w * len(code) for w, code in zip(weights, codes)) == merge_oracle(tuple(sorted(weights)))
        if n > 1:
            for i in range(n):
                for j in range(n):
                    if i != j:
                        assert codes[j][:len(codes[i])] != codes[i]
            symbols = list(range(n)) + list(reversed(range(n)))
            bits = [bit for symbol in symbols for bit in codes[symbol]]
            lookup = {tuple(code): i for i, code in enumerate(codes)}
            decoded, prefix = [], []
            for bit in bits:
                prefix.append(bit)
                if tuple(prefix) in lookup:
                    decoded.append(lookup[tuple(prefix)])
                    prefix = []
            assert decoded == symbols and not prefix
        elif n == 1:
            assert codes == [[]]
assert huffman_codes([0, 2]) is None and huffman_codes([-1]) is None
assert max(map(len, huffman_codes([2 ** i for i in range(9)]))) == 8
''')

    def test_interval_stabbing_against_all_point_subsets(self):
        run_code(definitions(GREEDY), COMMON + '''
coordinates = list(range(-1, 3))
candidates = [(a, b) for a in coordinates for b in coordinates if a <= b]
point_sets = [tuple(coordinates[i] for i in indices) for indices in position_subsets(len(coordinates))]
cases = 0
for n in range(5):
    for intervals in itertools.combinations_with_replacement(candidates, n):
        source = [list(interval) for interval in reversed(intervals)]
        before = copy.deepcopy(source)
        best = min(len(points) for points in point_sets
                   if all(any(a <= p <= b for p in points) for a, b in intervals))
        actual = interval_stabbing(source)
        assert len(actual) == best
        assert all(any(a <= p <= b for p in actual) for a, b in intervals)
        assert source == before
        cases += 1
assert cases == 1001
assert interval_stabbing([[3, 2]]) is None
assert interval_stabbing([[2, 2], [2, 2]]) == [2]
''')

    def test_deadlines_against_all_job_orders(self):
        run_code(definitions(GREEDY), COMMON + '''
def score(jobs, order):
    time = 0
    delays = [0]
    for index in order:
        time += jobs[index][0]
        delays.append(time - jobs[index][1])
    return max(delays)
candidates = list(itertools.product((0, 1, 3), (-1, 2, 5)))
cases = 0
for n in range(5):
    for jobs in itertools.product(candidates, repeat=n):
        source = [list(job) for job in jobs]
        before = copy.deepcopy(source)
        result = minimum_max_tardiness(source)
        optimum = min(score(jobs, order) for order in itertools.permutations(range(n)))
        assert result['max_tardiness'] == score(jobs, result['order']) == optimum
        assert sorted(result['order']) == list(range(n))
        assert result['finishes'] == [sum(jobs[j][0] for j in result['order'][:i + 1]) for i in range(n)]
        assert source == before
        cases += 1
assert cases == 7381
assert minimum_max_tardiness([[-1, 3]]) is None
''')

    def test_counting_states_against_combinatorial_formula(self):
        run_code(definitions(DP), COMMON + '''
for n in range(46):
    # With k twos there are n-k steps; choose the k positions occupied by twos.
    expected = sum(math.comb(n - k, k) for k in range(n // 2 + 1))
    memo = ways_memo(n)
    table = ways_table(n)
    assert memo['ways'] == table[-1] == expected
    assert len(table) == n + 1
    assert memo['expanded'] == max(0, n - 1)
    assert memo['calls'] == (2 * n - 1 if n >= 2 else 1)
    assert ways_memo(n) == memo
    if n <= 12:
        naive = ways_naive(n)
        assert naive['ways'] == expected
        assert naive['calls'] == 2 * expected - 1
for function in (ways_naive, ways_memo, ways_table):
    assert function(-1) is None
''')

    def test_memoization_keeps_stack_limit_but_iteration_completes(self):
        run_code(definitions(DP), COMMON + '''
import sys
sys.setrecursionlimit(100)
try:
    ways_memo(1200)
except RecursionError:
    pass
else:
    raise AssertionError('Memoization unexpectedly bypassed recursion limit')
table = ways_table(1200)
assert len(table) == 1201
assert table[-1] == sum(math.comb(1200 - k, k) for k in range(601))
''')

    def test_minimum_coins_against_breadth_first_amount_search(self):
        run_code(definitions(DP), COMMON + '''
for mask in range(64):
    coins = [c for c in range(1, 7) if mask & (1 << (c - 1))]
    distance = {0: 0}
    queue = deque([0])
    while queue:
        amount = queue.popleft()
        for coin in coins:
            following = amount + coin
            if following <= 24 and following not in distance:
                distance[following] = distance[amount] + 1
                queue.append(following)
    for amount in range(25):
        for order in (coins, coins[::-1], coins + coins):
            before = order.copy()
            result = min_coins(order, amount)
            if amount not in distance:
                assert result is None
            else:
                assert result['count'] == len(result['coins']) == distance[amount]
                assert sum(result['coins']) == amount
                assert all(coin in coins for coin in result['coins'])
            assert order == before
''')

    def test_minimum_coin_zero_unreachable_invalid_and_tie_contracts(self):
        run_code(definitions(DP), COMMON + '''
assert min_coins([], 0) == {'count': 0, 'coins': []}
assert min_coins([], 1) is None
assert min_coins([4, 6], 7) is None
assert min_coins([4, 6], 8) == {'count': 2, 'coins': [4, 4]}
assert min_coins([2, 3, 4], 6) == {'count': 2, 'coins': [2, 4]}
assert min_coins([3, 2, 4], 6) == {'count': 2, 'coins': [3, 3]}
for coins in ([0], [-1], [1, 0]):
    assert min_coins(coins, 0) is None
assert min_coins([1], -1) is None
''')

    def test_grid_counts_against_all_monotone_paths_and_obstacles(self):
        run_code(definitions(DP), COMMON + '''
cases = 0
for rows in range(1, 4):
    for columns in range(1, 4):
        paths = monotone_paths(rows, columns)
        for flags in itertools.product((False, True), repeat=rows * columns):
            grid = [list(flags[r * columns:(r + 1) * columns]) for r in range(rows)]
            before = copy.deepcopy(grid)
            expected = sum(all(not grid[r][c] for r, c in path) for path in paths)
            assert grid_paths(grid) == rolling_grid_paths(grid) == expected
            assert grid == before
            cases += 1
assert cases == 682
''')

    def test_grid_empty_ragged_and_shared_input_rows(self):
        run_code(definitions(DP), COMMON + '''
for grid in ([], [[]], [[], []]):
    assert grid_paths(grid) == rolling_grid_paths(grid) == 0
    assert min_grid_path(grid) is None
for grid in ([[], [False]], [[False], [False, True]]):
    assert grid_paths(grid) is None and rolling_grid_paths(grid) is None
for grid in ([[], [0]], [[0], [0, 1]]):
    assert min_grid_path(grid) is None
row = [False, False, False]
shared = [row, row, row]
assert grid_paths(shared) == rolling_grid_paths(shared) == 6
assert shared[0] is shared[1] is shared[2] and row == [False] * 3
assert min_grid_path([[0, 0], [0, 0]])['path'] == [[0, 0], [0, 1], [1, 1]]
''')

    def test_minimum_grid_paths_against_enumerated_signed_costs(self):
        run_code(definitions(DP), COMMON + '''
cases = 0
for rows, columns in ((1, 1), (1, 3), (3, 1), (2, 2), (2, 3), (3, 2)):
    paths = monotone_paths(rows, columns)
    for values in itertools.product((None, -2, 0, 3), repeat=rows * columns):
        grid = [list(values[r * columns:(r + 1) * columns]) for r in range(rows)]
        before = copy.deepcopy(grid)
        feasible = [path for path in paths if all(grid[r][c] is not None for r, c in path)]
        result = min_grid_path(grid)
        if not feasible:
            assert result is None
        else:
            path = [tuple(cell) for cell in result['path']]
            assert path in feasible
            optimum = min(sum(grid[r][c] for r, c in candidate) for candidate in feasible)
            assert result['cost'] == optimum == sum(grid[r][c] for r, c in path)
            assert len({id(cell) for cell in result['path']}) == len(path)
        assert grid == before
        cases += 1
assert cases == 8580
''')

    def test_nonadjacent_maximum_against_all_position_subsets(self):
        run_code(definitions(DP), COMMON + '''
cases = 0
for n in range(7):
    allowed = [indices for indices in position_subsets(n)
               if all(b - a > 1 for a, b in zip(indices, indices[1:]))]
    for values in itertools.product((-2, 0, 1, 4), repeat=n):
        source = list(values)
        result = max_nonadjacent(source)
        chosen = tuple(result['indices'])
        optimum = max(sum(values[i] for i in indices) for indices in allowed)
        assert chosen in allowed
        assert result['sum'] == optimum == sum(values[i] for i in chosen)
        assert source == list(values)
        cases += 1
assert cases == 5461
assert max_nonadjacent([2, 2]) == {'sum': 2, 'indices': [0]}
assert max_nonadjacent([0, 0, 0]) == {'sum': 0, 'indices': []}
assert max_nonadjacent([10 ** 100, -1, 10 ** 100])['sum'] == 2 * 10 ** 100
''')

    def test_single_use_subset_reachability_against_all_sums(self):
        run_code(definitions(DP), COMMON + '''
cases = 0
for n in range(7):
    subsets = position_subsets(n)
    for values in itertools.product((0, 1, 3), repeat=n):
        expected = {sum(values[i] for i in indices) for indices in subsets}
        source = list(values)
        for target in range(sum(values) + 3):
            assert subset_reachable(source, target) == (target in expected)
            assert source == list(values)
            cases += 1
assert cases == 11299
assert subset_reachable([2], 4) is False
assert subset_reachable([0, 0], 0) is True
assert subset_reachable([-1, 2], 1) is None
assert subset_reachable([1], -1) is None
''')
