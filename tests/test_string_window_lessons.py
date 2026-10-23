"""Run literal lessons against substring, multiset and exhaustive interval models."""

import unittest

from cs_study_map.textbook import validate_document
from test_data_structures_lessons import definitions, document, reviewed_tree, run_code

MATCHING = "31-string-matching"
TRIE = "32-trie"
WINDOWS = "33-prefix-window"

COMMON = r'''
import copy
import itertools
import sys
from collections import Counter

def words(alphabet, maximum):
    return [''.join(chars) for n in range(maximum + 1)
            for chars in itertools.product(alphabet, repeat=n)]

def matches(text, pattern):
    return [i for i in range(len(text) - len(pattern) + 1)
            if text[i:i + len(pattern)] == pattern]

def intervals(n, empty=False):
    return [(i, j) for i in range(n + 1)
            for j in range(i if empty else i + 1, n + 1)]

def longest_interval(candidates):
    return list(min(candidates, key=lambda pair: (pair[0] - pair[1], pair[0]),
                    default=(0, 0)))

def shortest_interval(candidates):
    result = min(candidates, key=lambda pair: (pair[1] - pair[0], pair[0]), default=None)
    return [] if result is None else list(result)

def inspect_trie(nodes, bag):
    # Reconstruct paths independently; compare each node with the word multiset.
    assert nodes and len({id(node) for node in nodes}) == len(nodes)
    assert len({id(node['next']) for node in nodes}) == len(nodes)
    seen = set()
    pending = [(0, '')]
    while pending:
        index, prefix = pending.pop()
        assert index not in seen
        seen.add(index)
        node = nodes[index]
        assert node['end'] == bag[prefix]
        assert node['count'] == sum(count for word, count in bag.items() if word.startswith(prefix))
        assert node['count'] == node['end'] + sum(nodes[child]['count'] for child in node['next'].values())
        assert node['end'] >= 0 and node['count'] >= 0
        for char, child in node['next'].items():
            assert len(char) == 1 and 0 <= child < len(nodes)
            pending.append((child, prefix + char))
    assert seen == set(range(len(nodes)))

def make_trie(bag):
    nodes = trie_new()
    for word, count in bag.items():
        for _ in range(count):
            trie_add(nodes, word)
    return nodes

def small_bags():
    terms = ['', 'a', 'ab', 'b', '计']
    for counts in itertools.product(range(3), repeat=len(terms)):
        yield Counter(dict(zip(terms, counts)))
'''


class StringWindowLessonTests(unittest.TestCase):
    def check(self, identifier, checks):
        run_code(definitions(identifier), COMMON + checks)

    def test_all_thirty_published_programs_match_exact_output(self):
        count = 0
        for identifier in (MATCHING, TRIE, WINDOWS):
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

    def test_membership_review_keeps_calls_and_attributes_restricted(self):
        reviewed_tree("data = {'a': 1}\nprint('a' in data, 'b' not in data)\n")
        for code in ("import os", "open('x')", "__import__('os')", "x.__class__", "eval('1')"):
            with self.subTest(code=code), self.assertRaises(AssertionError):
                reviewed_tree(code)

    def test_match_at_and_naive_against_literal_slices(self):
        self.check(MATCHING, r'''
for text in words('ab计', 4):
    for pattern in words('ab计', 3):
        assert naive_matches(text, pattern) == matches(text, pattern)
        for start in range(-1, len(text) + 2):
            expected = None if not 0 <= start <= len(text) else text[start:start + len(pattern)] == pattern
            assert match_at(text, pattern, start) is expected
''')

    def test_prefix_table_against_all_proper_prefixes(self):
        self.check(MATCHING, r'''
for text in words('ab', 8):
    expected = [max([0] + [size for size in range(1, stop)
                            if text[:size] == text[stop - size:stop]])
                for stop in range(1, len(text) + 1)]
    assert prefix_table(text) == expected
''')

    def test_kmp_overlaps_and_linear_index_access(self):
        self.check(MATCHING, r'''
for text in words('ab', 7):
    for pattern in words('ab', 4):
        assert kmp_matches(text, pattern) == matches(text, pattern)
class Indexed:
    def __init__(self, text):
        self.text = text
        self.reads = 0
    def __len__(self):
        return len(self.text)
    def __getitem__(self, index):
        self.reads += 1
        return self.text[index]
text = Indexed('a' * 12000 + 'b')
pattern = Indexed('a' * 3000 + 'c')
assert kmp_matches(text, pattern) == []
assert text.reads + pattern.reads < 12 * (len(text) + len(pattern))
''')

    def test_stream_all_partitions_and_empty_chunks(self):
        self.check(MATCHING, r'''
for text in words('ab', 6):
    for pattern in words('ab', 3)[1:]:
        expected = matches(text, pattern)
        for mask in range(1 << max(len(text) - 1, 0)):
            stops = [i for i in range(1, len(text)) if mask & (1 << (i - 1))] + [len(text)]
            state = matcher_new(pattern)
            table = state['table'].copy()
            actual = []
            start = 0
            for stop in stops:
                before = copy.deepcopy(state)
                assert matcher_feed(state, '') == [] and state == before
                actual.extend(matcher_feed(state, text[start:stop]))
                assert state['consumed'] == stop and 0 <= state['matched'] < len(pattern)
                start = stop
            assert actual == expected and state['table'] == table
''')

    def test_stream_instances_and_unicode_codepoint_contract(self):
        self.check(MATCHING, r'''
assert matcher_new('') is None
a, b = matcher_new('aba'), matcher_new('aba')
assert a is not b and a['table'] is not b['table']
assert matcher_feed(a, 'ab') == []
assert matcher_feed(b, 'aba') == [0]
assert matcher_feed(a, 'a') == [0]
assert kmp_matches('é é 😀😀 \x00', 'é') == [0]
assert kmp_matches('é é 😀😀 \x00', 'é') == [2]
assert kmp_matches('é é 😀😀 \x00', '😀') == [5, 6]
assert kmp_matches('é é 😀😀 \x00', '\x00') == [8]
''')

    def test_complete_period_against_direct_repetition(self):
        self.check(MATCHING, r'''
for text in words('ab', 9) + ['计数' * 5, 'ababa', 'abcab', '😀' * 7]:
    expected = next((p for p in range(1, len(text) + 1)
                     if len(text) % p == 0 and text[:p] * (len(text) // p) == text), 0)
    assert repeating_unit_length(text) == expected
''')

    def test_all_borders_against_prefix_suffix_equality(self):
        self.check(MATCHING, r'''
for text in words('ab', 9):
    expected = [p for p in range(len(text) - 1, 0, -1) if text[:p] == text[-p:]]
    assert border_lengths(text) == expected
''')

    def test_rotations_against_explicit_cuts(self):
        self.check(MATCHING, r'''
for source in words('ab', 6):
    for target in words('ab', 6):
        expected = next((i for i in range(max(len(source), 1))
                         if source[i:] + source[:i] == target), None)
        assert rotation_offset(source, target) == expected
''')

    def test_nonoverlap_selection_against_all_subsets(self):
        self.check(MATCHING, r'''
assert disjoint_matches('abc', '') is None
for text in words('ab', 7):
    for pattern in words('ab', 3)[1:]:
        starts = matches(text, pattern)
        options = []
        for mask in range(1 << len(starts)):
            chosen = [start for i, start in enumerate(starts) if mask & (1 << i)]
            if all(a + len(pattern) <= b for a, b in zip(chosen, chosen[1:])):
                options.append(chosen)
        expected = min(options, key=lambda selected: (-len(selected), selected))
        assert disjoint_matches(text, pattern) == expected
''')

    def test_trie_operation_histories_against_multiset(self):
        self.check(TRIE, r'''
terms = ['', 'a', 'ab', '计']
operations = list(itertools.product(('add', 'remove'), terms))
for history in itertools.product(operations, repeat=4):
    nodes, bag = trie_new(), Counter()
    for action, word in history:
        if action == 'add':
            trie_add(nodes, word)
            bag[word] += 1
        else:
            before = copy.deepcopy(nodes)
            expected = bag[word] > 0
            assert trie_remove(nodes, word) is expected
            if expected:
                bag[word] -= 1
            else:
                assert nodes == before
        inspect_trie(nodes, bag)
        for query in terms + ['b', 'a计']:
            assert trie_exact(nodes, query) == bag[query]
            assert trie_prefix_count(nodes, query) == sum(count for word, count in bag.items() if word.startswith(query))
''')

    def test_trie_queries_and_enumeration_against_bags(self):
        self.check(TRIE, r'''
for bag in small_bags():
    nodes = make_trie(bag)
    before = copy.deepcopy(nodes)
    for query in words('ab计', 3):
        assert trie_exact(nodes, query) == bag[query]
        expected = {word: count for word, count in bag.items() if count and word.startswith(query)}
        records = trie_words(nodes, query)
        assert len(records) == len(expected) and dict(records) == expected
        assert trie_prefix_count(nodes, query) == sum(expected.values())
        lengths = [len(word) for word, count in bag.items() if count and query.startswith(word)]
        assert trie_longest_prefix(nodes, query) == max(lengths, default=None)
    assert nodes == before
''')

    def test_trie_failed_deletion_and_historical_node_reuse(self):
        self.check(TRIE, r'''
nodes = trie_new()
trie_add(nodes, 'abc')
before = copy.deepcopy(nodes)
for absent in ('', 'a', 'ab', 'abcd', 'xyz'):
    assert trie_remove(nodes, absent) is False and nodes == before
assert trie_remove(nodes, 'abc') is True
assert len(nodes) == 4 and trie_words(nodes, '') == []
assert trie_locate(nodes, 'ab') is not None
assert trie_prefix_count(nodes, 'ab') == 0
assert trie_longest_prefix(nodes, 'abc') is None
trie_add(nodes, 'abc')
assert len(nodes) == 4 and nodes == before
''')

    def test_trie_enumeration_order_and_result_independence(self):
        self.check(TRIE, r'''
nodes = trie_new()
for word in ['bat', 'ab', 'ba', 'bat', '']:
    trie_add(nodes, word)
expected = [['', 1], ['ba', 1], ['bat', 2], ['ab', 1]]
assert trie_words(nodes, '') == expected
records = trie_words(nodes, '')
records[1][1] = 99
records.append(['fake', 1])
assert trie_words(nodes, '') == expected
assert trie_remove(nodes, 'ab')
trie_add(nodes, 'aa')
trie_add(nodes, 'ab')
assert trie_words(nodes, 'a') == [['ab', 1], ['aa', 1]]
''')

    def test_trie_wildcard_against_direct_character_comparison(self):
        self.check(TRIE, r'''
for bag in small_bags():
    nodes = make_trie(bag)
    for pattern in words('ab?', 3):
        expected = sum(count for word, count in bag.items()
                       if len(word) == len(pattern)
                       and all(p == '?' or p == c for p, c in zip(pattern, word)))
        assert trie_wildcard_count(nodes, pattern) == expected
nodes = trie_new()
for word in ['?', '*', '😀', 'é']:
    trie_add(nodes, word)
assert trie_wildcard_count(nodes, '?') == 3
assert trie_wildcard_count(nodes, '*') == 1
assert trie_wildcard_count(nodes, '??') == 1
''')

    def test_trie_common_prefix_against_all_words(self):
        self.check(TRIE, r'''
for bag in small_bags():
    nodes = make_trie(bag)
    active = [word for word, count in bag.items() if count]
    expected = None
    if active:
        expected = max(i for i in range(len(active[0]) + 1)
                       if all(word.startswith(active[0][:i]) for word in active))
    assert trie_common_prefix_length(nodes) == expected
nodes = trie_new()
for word in ['abc', 'abd', 'ax']:
    trie_add(nodes, word)
assert trie_remove(nodes, 'ax')
assert trie_common_prefix_length(nodes) == 2
assert trie_remove(nodes, 'abd')
assert trie_common_prefix_length(nodes) == 3
''')

    def test_trie_stable_unique_against_first_occurrence(self):
        self.check(TRIE, r'''
for length in range(6):
    for sequence in itertools.product(['', 'a', 'ab', '计'], repeat=length):
        original = list(sequence)
        expected = [word for i, word in enumerate(sequence) if word not in sequence[:i]]
        assert unique_words(original) == expected and original == list(sequence)
''')

    def test_trie_deep_nonrecursive_and_independent_instances(self):
        self.check(TRIE, r'''
sys.setrecursionlimit(100)
long_word = 'a' * 2000
nodes, other = trie_new(), trie_new()
trie_add(nodes, long_word)
assert other == [{'next': {}, 'end': 0, 'count': 0}]
assert trie_exact(nodes, long_word) == 1
assert trie_longest_prefix(nodes, long_word + 'b') == len(long_word)
assert trie_common_prefix_length(nodes) == len(long_word)
assert trie_words(nodes, '') == [[long_word, 1]]
assert trie_wildcard_count(nodes, '?' * len(long_word)) == 1
assert trie_remove(nodes, long_word)
assert trie_words(nodes, '') == []
''')

    def test_trie_unicode_empty_and_zero_count_boundaries(self):
        self.check(TRIE, r'''
bag = Counter(['', '', 'é', 'é', '😀', '\x00', 'e', 'é'])
nodes = make_trie(bag)
inspect_trie(nodes, bag)
assert trie_exact(nodes, 'é') == 2 and trie_exact(nodes, 'é') == 1
assert trie_prefix_count(nodes, 'e') == 2
assert trie_longest_prefix(nodes, 'z') == 0
assert trie_remove(nodes, '') and trie_remove(nodes, '')
assert not trie_remove(nodes, '') and trie_longest_prefix(nodes, 'z') is None
assert trie_remove(nodes, 'e')
assert trie_exact(nodes, 'e') == 0 and trie_prefix_count(nodes, 'e') == 1
''')

    def test_prefix_queries_against_direct_sums(self):
        self.check(WINDOWS, r'''
for n in range(7):
    for sequence in itertools.product((-2, 0, 3), repeat=n):
        values = list(sequence)
        prefix = prefix_sums(values)
        assert prefix == [sum(values[:i]) for i in range(n + 1)]
        for start, stop in intervals(n, empty=True):
            assert range_sum(prefix, start, stop) == sum(values[start:stop])
        assert values == list(sequence)
''')

    def test_difference_updates_against_elementwise_updates(self):
        self.check(WINDOWS, r'''
for n in range(5):
    options = [[start, stop, delta] for start, stop in intervals(n, empty=True) for delta in (-2, 0, 3)]
    for pair in itertools.product(options, repeat=2):
        requests = copy.deepcopy(list(pair))
        expected = [0] * n
        for start, stop, delta in requests:
            for i in range(start, stop):
                expected[i] += delta
        assert range_additions(n, requests) == expected
        assert requests == list(pair)
assert range_additions(3, []) == [0, 0, 0]
''')

    def test_invalid_ranges_and_atomic_requests(self):
        self.check(WINDOWS, r'''
prefix = prefix_sums([1, 2, 3])
for start, stop in [(-1, 2), (2, 1), (0, 4), (4, 4), (0, -1)]:
    assert range_sum(prefix, start, stop) is None
assert range_sum([], 0, 0) is None
assert range_additions(-1, []) is None
for bad in [[], [0, 1], [0, 1, 2, 3], [-1, 2, 0], [2, 1, 0], [0, 4, 1]]:
    requests = [[0, 2, 7], bad]
    before = copy.deepcopy(requests)
    assert range_additions(3, requests) is None and requests == before
''')

    def test_sorted_pairs_against_all_distinct_positions(self):
        self.check(WINDOWS, r'''
for n in range(8):
    for sequence in itertools.combinations_with_replacement(range(-2, 3), n):
        values = list(sequence)
        for target in range(-5, 6):
            options = [(i, j) for i in range(n) for j in range(i + 1, n) if values[i] + values[j] == target]
            actual = sorted_pair(values, target)
            assert tuple(actual) in options if options else actual == []
        assert values == list(sequence)
assert sorted_pair([3, 1, 2], 3) is None
assert sorted_pair([1, 2, 0], 3) is None
''')

    def test_shortest_nonnegative_window_against_all_intervals(self):
        self.check(WINDOWS, r'''
for n in range(7):
    for sequence in itertools.product(range(4), repeat=n):
        values = list(sequence)
        options = [(pair, sum(values[pair[0]:pair[1]])) for pair in intervals(n)]
        for target in range(1, 8):
            expected = shortest_interval([pair for pair, total in options if total >= target])
            assert shortest_window(values, target) == expected
        assert values == list(sequence)
''')

    def test_longest_unique_against_all_intervals(self):
        self.check(WINDOWS, r'''
for text in words('ab计', 7):
    expected = longest_interval([(i, j) for i, j in intervals(len(text))
                                 if len(set(text[i:j])) == j - i])
    assert longest_unique_window(text) == expected
assert longest_unique_window('abba') == [0, 2]
assert longest_unique_window('😀é😀') == [0, 3]
''')

    def test_longest_k_distinct_against_all_intervals(self):
        self.check(WINDOWS, r'''
for text in words('ab计', 6):
    for limit in range(5):
        expected = longest_interval([(i, j) for i, j in intervals(len(text))
                                     if len(set(text[i:j])) <= limit])
        assert longest_k_distinct(text, limit) == expected
assert longest_k_distinct('abc', -1) is None
''')

    def test_exact_distinct_counts_against_all_intervals(self):
        self.check(WINDOWS, r'''
for text in words('ab计', 6):
    sizes = [len(set(text[i:j])) for i, j in intervals(len(text))]
    for count in range(5):
        assert exactly_k_distinct_count(text, count) == sizes.count(count)
        assert at_most_distinct_count(text, count) == sum(size <= count for size in sizes)
assert exactly_k_distinct_count('abc', -1) is None
assert at_most_distinct_count('abc', -1) == 0
''')

    def test_signed_sum_counts_against_all_intervals(self):
        self.check(WINDOWS, r'''
for n in range(8):
    for sequence in itertools.product((-1, 0, 1), repeat=n):
        values = list(sequence)
        sums = Counter(sum(values[i:j]) for i, j in intervals(n))
        for target in range(-2, 3):
            assert subarray_sum_count(values, target) == sums[target]
        assert values == list(sequence)
''')

    def test_window_preconditions_big_integers_and_hash_collisions(self):
        self.check(WINDOWS, r'''
for values, target in [([1, -1, 5], 5), ([-1], 1), ([], 0), ([1], -1)]:
    before = values.copy()
    assert shortest_window(values, target) is None and values == before
big = 10 ** 100
values = [big, -big, big, 0, -big]
assert prefix_sums(values) == [0, big, 0, big, big, 0]
assert subarray_sum_count(values, 0) == sum(sum(values[i:j]) == 0 for i, j in intervals(len(values)))
assert shortest_window([0, big, 0, big], 2 * big) == [1, 4]
assert exactly_k_distinct_count('a' * 100000, 1) == 100000 * 100001 // 2
modulus = sys.hash_info.modulus
values = [modulus, modulus, -modulus, 0, -modulus]
assert len({hash(i * modulus) for i in range(5)}) == 1
for target in (-modulus, 0, modulus):
    assert subarray_sum_count(values, target) == sum(sum(values[i:j]) == target for i, j in intervals(len(values)))
''')


if __name__ == "__main__":
    unittest.main()
