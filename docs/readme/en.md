# cs-study-map · Personal computer science textbooks

| [简体中文](../../README.md) | [繁體中文](zh-TW.md) | [English](en.md) | [日本語](ja.md) | [Русский](ru.md) | [Français](fr.md) | [Deutsch](de.md) | [Italiano](it.md) | [Português](pt.md) | [Español](es.md) | [العربية](ar.md) | [한국어](ko.md) |

This project is mainly for the maintainer’s own study. It selects useful topics from [REKCARC-TSC-UHT](https://github.com/PKUanonym/REKCARC-TSC-UHT), reorganizes them into a Chinese-language textbook according to prerequisites, and adds explanations, original examples, solved exercises, and self-checks. Synchronization, AI classification, and source guides support selection and updates.

**[Textbook](../textbook/index.md)** · [Study map](../index.md) · [Coverage](../status.md) · [Usage](../usage.md) · [Sources and licensing](../../ATTRIBUTION.md)

This is Pleniluner’s personal learning project, with no official affiliation with Tsinghua University or upstream maintainers. The public repository contains original tools, textbook drafts, source indexes, and AI guides. Original course materials, slides, assignments, student source code, and extracted full text are not published.

## Thirty-six chapters to study in order

| # | Topic | Activity |
| --- | --- | --- |
| 1 | [Binary, bytes, and little-endian order](../textbook/01-data-and-bytes.md) | Split a number into bytes, then reconstruct it from memory |
| 2 | [Registers, memory, and the stack](../textbook/02-execution-and-stack.md) | Trace a toy machine state step by step |
| 3 | [First fit, splitting, and coalescing](../textbook/03-first-fit.md) | Simulate allocation and release; explain external fragmentation |
| 4 | [Sequence, branches, and loops](../textbook/04-control-flow.md) | Trace variables, write repeated calculations, and check boundaries and termination |
| 5 | [Parameters, return values, and functions](../textbook/05-functions.md) | Compose functions and distinguish printing, returning, and local names |
| 6 | [Arrays and sequential lists](../textbook/06-arrays.md) | Track indices, capacity, shared lists, and element shifts |
| 7 | [Singly linked lists](../textbook/07-linked-lists.md) | Trace node references, insert, delete, and reverse links |
| 8 | [Stacks](../textbook/08-stacks.md) | Apply LIFO order to undo history and bracket matching |
| 9 | [Queues and circular arrays](../textbook/09-queues.md) | Track FIFO order, wraparound, and empty or full states |
| 10 | [Algorithm analysis](../textbook/10-algorithm-analysis.md) | Count operations, compare growth, and account for extra space |
| 11 | [Sequential and binary search](../textbook/11-searching.md) | Trace boundaries, duplicates, and missing targets |
| 12 | [Selection, insertion, and merge sort](../textbook/12-sorting.md) | Check ordering, multiplicities, stability, and search after sorting |
| 13 | [Recursion, returns, and the call stack](../textbook/13-recursion.md) | Trace base cases, progress, total calls, and peak stack depth |
| 14 | [Divide and conquer and recursive merge sort](../textbook/14-divide-and-conquer.md) | Split ranges, combine answers, and count inversions |
| 15 | [Quicksort and three-way partitioning](../textbook/15-quick-sort.md) | Check partitions, duplicates, worst cases, and bounded stack depth |
| 16 | [Trees, binary trees, and traversals](../textbook/16-trees.md) | Track height, traversal order, mirroring, and completeness |
| 17 | [Binary search trees](../textbook/17-binary-search-trees.md) | Maintain global key order, deletion links, range queries, and height bounds |
| 18 | [Binary heaps and priority queues](../textbook/18-heaps.md) | Repair heap order, build heaps, sort, select top k, and merge streams |
| 19 | [Hash tables, collisions, and resizing](../textbook/19-hash-tables.md) | Maintain key-value buckets and distinguish expected, worst-case, and amortized costs |
| 20 | [Graphs and storage representations](../textbook/20-graphs.md) | Model direction and check adjacency lists, matrices, degrees, and reversed edges |
| 21 | [DFS, BFS, and unweighted shortest paths](../textbook/21-graph-traversal.md) | Track discovery, recover paths, and handle components and multiple sources |
| 22 | [Topological sorting and DAG applications](../textbook/22-topological-sort.md) | Track remaining prerequisites, recover cycles, and schedule tasks |
| 23 | [Weighted shortest paths and relaxation](../textbook/23-weighted-shortest-paths.md) | Compare Dijkstra, Bellman–Ford, DAG order, and bounded walks |
| 24 | [Minimum spanning trees and disjoint sets](../textbook/24-minimum-spanning-trees.md) | Explain Prim and Kruskal, verify forests, and improve a tree with a new edge |
| 25 | [Backtracking and pruning](../textbook/25-backtracking.md) | Restore search state and prove that pruning preserves all answers |
| 26 | [Greedy algorithms and exchange arguments](../textbook/26-greedy-algorithms.md) | Build counterexamples and verify scheduling, merging, and prefix codes |
| 27 | [Introduction to dynamic programming](../textbook/27-dynamic-programming.md) | Define states, recover solutions, and check update order |
| 28 | [Knapsack problems and counting](../textbook/28-knapsack.md) | Distinguish capacity, exact weight, reuse, combinations, and sequences |
| 29 | [Sequence dynamic programming](../textbook/29-sequence-dp.md) | Recover LCS matches, edit alignments, and increasing subsequences |
| 30 | [Interval and tree dynamic programming](../textbook/30-interval-tree-dp.md) | Plan adjacent merges and solve independent sets, covers, and counts |
| 31 | [String matching and KMP](../textbook/31-string-matching.md) | Track prefix fallback, overlaps, chunk boundaries, and rotations |
| 32 | [Tries and prefix queries](../textbook/32-trie.md) | Maintain duplicate words, deletion, enumeration, and prefix counts |
| 33 | [Prefix sums, two pointers, and sliding windows](../textbook/33-prefix-window.md) | Prove interval boundaries, monotonicity, and counting rules |
| 34 | [Monotonic stacks and queues](../textbook/34-monotonic-structures.md) | Prove candidate removal and verify intervals with negative values |
| 35 | [Fenwick trees and frequency ranks](../textbook/35-fenwick-tree.md) | Maintain prefix blocks, differences, and nonnegative ranks |
| 36 | [Segment trees and lazy propagation](../textbook/36-segment-tree.md) | Merge summaries and trace query order and pending updates |

Chapters 4–36 use Python 3.11 or later and include 330 standalone programs with expected outputs. See the [programming practice guide](../programming-practice.md), [data structures guide](../data-structures-practice.md), and [algorithm practice guide](../algorithms-practice.md), all in Chinese. [Recursion and divide-and-conquer exercises (in Chinese)](../recursion-practice.md). [Tree and heap exercises (in Chinese)](../trees-practice.md). [Hash table and graph exercises (in Chinese)](../hash-graphs-practice.md). [Topological sorting and weighted graph exercises (in Chinese)](../weighted-graphs-practice.md). [Backtracking, greedy, and dynamic programming exercises (in Chinese)](../strategy-practice.md). [Advanced dynamic programming exercises (in Chinese)](../advanced-dp-practice.md). [String, trie, and interval exercises (in Chinese)](../string-window-practice.md). [Monotonic structures and dynamic range query exercises (in Chinese)](../range-structures-practice.md).

Each chapter has detailed explanations, 2 original examples, 3 exercises with expandable solutions, a self-check, and topic sources. This is an AI first draft, not reviewed by subject experts or trial learners; it does not mean every course has a textbook.

## What you can do

Study by chapter and keep private notes in Git-ignored `.local/`; create original chapters from identified topics while recording source versions; find materials by field, course, or AI-identified topic and open a fixed upstream revision; inspect topics, prerequisites, suggestions, and evidence locations; check upstream changes and reuse unchanged analyses; override automatic classification with human decisions.

AI guides state extraction coverage, model, and unreviewed status. Catalog completeness and AI-guide coverage are tracked separately; partial extraction, unsupported formats, and failures are reported honestly.

## Quick start

Requires Python 3.11+. This fetches metadata and builds navigation; no model key is needed and source contents are not downloaded.

```bash
git clone https://github.com/Pleniluner/cs-study-map.git
cd cs-study-map
python -m venv .venv
# Linux / macOS:
source .venv/bin/activate
# Windows PowerShell:
# .\.venv\Scripts\Activate.ps1
python -m pip install -e .
cs-study-map run --limit 0
```

## AI workflow

Both providers use the same validation and guide-generation pipeline. For a model API set `CS_STUDY_API_BASE`, `CS_STUDY_MODEL`, and `CS_STUDY_API_KEY`. For local Codex CLI set `CS_STUDY_PROVIDER=codex` and `CS_STUDY_MODEL`; optionally set `CS_STUDY_CODEX_BIN`. API adapters support Chat Completions and Responses; `chat` is the default and `CS_STUDY_API_STYLE=responses` selects Responses. Use a model supported by the service. Codex requires a current CLI supporting the chosen model and manages its credentials.

```bash
cs-study-map analyze --course 程序设计基础 --limit 2 --require-ai
cs-study-map write --limit 1 --require-ai
cs-study-map build
cs-study-map validate
```

See [usage and setup](../usage.md) for configuration, PowerShell examples, and GitHub settings.

## Scheduled synchronization

GitHub Actions checks upstream daily and can be started manually as **Sync study map**. When a model is configured, it generates guides and textbook chapters within configured budgets, validates, and commits updates. Defaults are at most 6 materials analyzed and 1 chapter written per day; scope is in `config/curriculum.json`.

Without a model, the workflow still syncs the catalog and reports `not-configured`; existing guides remain available and changed sources await analysis. Filename rules and simulated output are never labeled completed AI work. Anyone can browse the published map without a model account. Forks need their own model API configuration; local Codex login is not uploaded to GitHub. GitHub may disable schedules after prolonged inactivity; re-enable them in Actions.

## Project layout

```text
config/                  routes, sources, taxonomy, course map and overrides
catalog/                 metadata, analyses, textbook drafts and coverage
docs/textbook/           GitHub-readable textbook (currently Chinese)
docs/                    course and field navigation, study log template, usage
src/cs_study_map/        synchronization, extraction, AI classification and writing
tests/                   synchronization, recovery, provenance and publishing checks
.github/workflows/       scheduled synchronization and CI
.cache/                  local source files and extraction cache; never commit
.local/                  private study notes; never commit
```

README translations do not mean the textbook chapters themselves are translated; the current textbook text is Chinese.

Initial field mappings came from the maintainer’s personal organization of course directories. They are revisable and are not official upstream categories or a university curriculum. New courses are marked pending classification. Supported inputs include text, common source code, text-extractable PDF, DOCX, PPTX, and Notebook. OCR for scans, legacy DOC/PPT, and archive analysis are not implemented. PDF extraction defaults to at most 8 pages and 10,000 characters, so a long lecture may only be partially read.

## Validation and contributions

Run `python -m unittest discover -s tests -v` and `cs-study-map validate --tracked`. Report errors through Issues. Pull requests may improve code, mappings, or manual correction rules; see the [contribution guide](../../CONTRIBUTING.md).

Original programs, textbook text, and maintenance documents use the MIT License. This does not change source-material rights; see [attribution and licensing](../../ATTRIBUTION.md).

Early work: [knowledge overview and 60 course guides](../early-work/index.md), including the original category overview and textbook README. These pre-existing documents were imported into Git with learning content preserved and local absolute paths removed.
