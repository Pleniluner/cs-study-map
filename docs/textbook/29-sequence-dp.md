# 对齐两个前缀：序列动态规划与方案恢复

[返回教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [哈希表与图练习指引](../hash-graphs-practice.md) · [拓扑排序与带权图练习指引](../weighted-graphs-practice.md)

[上一章：限定容量与使用次数：背包问题和方案计数](28-knapsack.md) · [下一章：按区间与子树组织依赖：区间和树形动态规划](30-interval-tree-dp.md)

[学习目标](#objectives) · [需要的基础](#prerequisites) · [例题](#examples) · [练习](#practice) · [自测](#self-check)

状态：**AI 初稿，可开始试学**。生成模型：Codex 当前会话（未记录具体模型型号）。

本章围绕资料中识别到的知识点重新编写；讲解、数值模型、例题与练习为 AI 原创组织，不是原课程题目或答案。主题出处只说明选题关联，不证明全部推导已经正确。

两份文本有多少共同内容，修改一份需要几步，一串数里能保留多长的递增片段，都可以通过序列状态来回答。但连续子串、可以跳过元素的子序列、允许替换的编辑距离，约束并不相同。本章先补足字符串和字符位置的约定，再把两个前缀组成二维状态，最后处理一个序列的结束位置状态。每个最优值都配合位置或对齐结果核验，压缩空间时也说明哪些恢复信息已经丢失。

<a id="objectives"></a>

## 学完要能做到

- 准确区分子序列、连续子串以及字符串的码点位置。
- 推导最长公共子序列与单位编辑距离的边界和转移。
- 恢复原位置对、编辑对齐和严格递增的原下标序列。
- 解释一维 LCS 的旧对角值，识别只允许插删时的另一种距离。

<a id="prerequisites"></a>

## 需要的基础

- 第 27–28 章的二维状态、不可达与空方案、更新顺序和恢复思想。
- 列表切片、循环、布尔短路以及独立二维行。
- 第 11 章的原位置与排序后位置区别；本章不要求模式匹配知识。

## 先规定序列的单位：字符、位置与子序列

Python 的 str 是不可变的 Unicode 码点序列，len 和下标按码点计数，不按 UTF-8 字节计数，也不保证一个显示字形恰好占一个位置。本章文本接口只接收 str，区分大小写，不进行归一化。预组成的 é 长度为 1，e 后接组合重音符的长度为 2；即使显示相似，算法也按给定码点逐个比较。

子序列由严格递增的一组原位置选出，可以跳过中间字符；连续子串则要求位置相邻。例如 abc 的 ac 是子序列，ca 不是，因为顺序不能交换；ac 也不是它的连续子串。空串是任何字符串的子序列，匹配结果应为空下标表，而不是失败的 None。

先解决判定问题：给定 text 和 pattern，扫描 text，每次遇到 pattern 下一个待匹配字符就立即使用它。选择最早可用位置不会损失可行性，因为任何使用更晚位置的匹配，都可把这一位换成更早的相同字符，后面的匹配仍在其后。逐位替换就说明：若有解，最早匹配策略一定能找到；这是一段有明确交换理由的小型贪心。

程序先检查是否还有待匹配字符，才读取 pattern 的下标，避免空串或已经完成时越界。它返回原位置列表，失败返回 None，不修改字符串。示例中“计算计算”的“计计”位于 0 和 2。扫描时间 O(n+1)，输出至多 min(n,m) 个下标，其中 n、m 为两个串的码点长度；本实现完成匹配后仍扫描剩余 text，因此不要声称提前结束。这个判定器只问给定模式能否嵌入，下一节才在两串之间寻找最长的共同内容。

**完整程序**

```python
def subsequence_positions(text, pattern):
    positions = []
    next_match = 0
    for i in range(len(text)):
        if next_match < len(pattern) and text[i] == pattern[next_match]:
            positions.append(i)
            next_match = next_match + 1
    if next_match != len(pattern):
        return None
    return positions

print(subsequence_positions("计算计算", "计计"))
print(subsequence_positions("abc", "ca"))
print(subsequence_positions("abc", ""))
print(len("é"), len("e\u0301"))
```

**预期输出**

```text
[0, 2]
None
[]
1 2
```


选题关联：来源主题 1（文末列出）。

## 两个前缀组成状态：最长公共子序列

给定字符串 a 和 b，定义 table\[i\]\[j\] 为 a 的前 i 个码点与 b 的前 j 个码点的最长公共子序列长度，简称 LCS 长度。长度为零的前缀只能共有空串，故第零行和第零列全为 0。状态使用前缀长度，最后字符的位置分别是 i−1、j−1，不把长度直接当下标。

如果最后字符相同，可以把这一对接到两个更短前缀的共同子序列后，得到对角格加一。为什么不必另取上格或左格？任何最优匹配若使用其中一个末字符，都可把对应的同字符移到另一串末尾；移去最后这对后是两个更短前缀的匹配。若两端都没用，也不会超过对角格。因此存在配对这两个末字符的最优解。

如果最后字符不同，不可能把它们配成一对。一个保持顺序的共同子序列也不能同时使用这两个末位置分别去匹配对方更早的字符，否则两对会交叉。至少有一端被舍弃，所以取上格与左格的较大值。不是把两项相加，因为它们的方案可能重叠，目标也只是长度。

按行从上到下、列从左到右填表，当前格的上方、左方和左上方均已完成。每格依据上述分类得到正确长度，最后一格就是全串答案。示例 ab 与 ba 的最终长度为 1，两个前缀长度为 1 的状态却可能是 0。表的各行单独创建，输入不改变。含空串与初始化的时间、空间均为 O((n+1)(m+1))；这里 n、m 可以不同，不能把任意输入的成本简写为 O(n²)。表只记录长度，还没有告诉我们选了哪些位置。

**完整程序**

```python
def lcs_table(a, b):
    table = []
    for i in range(len(a) + 1):
        table.append([0] * (len(b) + 1))
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                table[i][j] = table[i - 1][j - 1] + 1
            else:
                table[i][j] = table[i - 1][j]
                if table[i][j - 1] > table[i][j]:
                    table[i][j] = table[i][j - 1]
    return table

for row in lcs_table("ab", "ba"):
    print(row)
```

**预期输出**

```text
[0, 0, 0]
[0, 0, 1]
[0, 1, 1]
```


选题关联：来源主题 1（文末列出）。

## 恢复共同位置：一条最优路径不代表全部答案

从完整表右下角开始，末字符相同就记录位置对 \[i−1,j−1\] 并沿对角线退一步；不同时，沿长度较大的上格或左格退。只要任一前缀为空，恢复就结束。每步至少减少一个前缀长度，因此过程有限，最多走 n+m 步。

本实现上格与左格相等时优先上格，即舍弃 a 的末字符。ab 与 ba 因而返回位置对 \[0,1\]，代表字符 a；选 b 也同样最优。平局规则只为了结果稳定，不保证字典序最小，也不枚举所有匹配。a 或 b 有重复字符时，相同文字甚至可能对应多组位置对，不能用文本相同推断位置相同。

恢复得到的位置对暂按从后往前排列，最后反转外层列表。每个位置对新建为独立列表，结果中的两列都应严格递增，而且对应码点相等。检查这三个条件能证明它确实是共同子序列；还要把位置对数量同最优长度核对，才能证明返回方案达到了要求。空串与另一串的结果是长度 0 和空 pairs。

返回位置而不直接反复拼接长字符串，可以保留来源身份，也避免把不可变字符串累加的复制开销藏在恢复里。若调用者需要显示内容，可再按这些位置读取字符。完整函数仍需 O((n+1)(m+1)) 时间与表空间，恢复和输出另外至多 O(n+m+1)。只保留两行或一行长度会省空间，但原路径不再全部可见；后面的压缩练习只返回长度，不声称能用相同信息恢复这一方案。

**完整程序**

```python
def lcs_table(a, b):
    table = []
    for i in range(len(a) + 1):
        table.append([0] * (len(b) + 1))
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                table[i][j] = table[i - 1][j - 1] + 1
            else:
                table[i][j] = table[i - 1][j]
                if table[i][j - 1] > table[i][j]:
                    table[i][j] = table[i][j - 1]
    return table

def lcs_match(a, b):
    table = lcs_table(a, b)
    pairs = []
    i = len(a)
    j = len(b)
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            pairs.append([i - 1, j - 1])
            i = i - 1
            j = j - 1
        elif table[i - 1][j] >= table[i][j - 1]:
            i = i - 1
        else:
            j = j - 1
    return {"length": table[len(a)][len(b)], "pairs": pairs[::-1]}

print(lcs_match("ab", "ba"))
print(lcs_match("", "ba"))
```

**预期输出**

```text
{'length': 1, 'pairs': [[0, 1]]}
{'length': 0, 'pairs': []}
```


选题关联：来源主题 1（文末列出）。

## 编辑距离：把保留、替换、删除和插入分开

现在允许把 a 变成 b。删除一个码点、插入一个码点、把一个码点替换成另一个，各花费 1；保留相同码点花费 0。这是单位 Levenshtein 距离。本章不允许把两个相邻字符交换当成一次操作，也不考虑不同字符的特殊代价。

定义 table\[i\]\[j\] 为把 a 的前 i 个字符改成 b 的前 j 个字符的最小代价。空源变成长度 j 的目标，需要 j 次插入，所以第零行为 0、1、2……；长度 i 的源变空，需要 i 次删除，所以第零列为 i。与 LCS 的全零边界不同，这是代价的必要部分。

观察最后一个对齐位置：若两边都有字符，可从左上格保留或替换；若只消耗源字符，从上格加一次删除；若只生成目标字符，从左格加一次插入。三类覆盖全部对齐的最后一步，取最小候选。已有更短前缀的最佳对齐接上最后一步一定可行，任何更差的前缀也可被最佳前缀替换，所以最优子结构成立。

示例 cat 到 cut 的中间字符替换一次即可，距离为 1；它们的 LCS 长度为 2，但这不意味着编辑距离必须是 2。只有禁止替换、仅允许插入删除时，才得到后面练习中的 n+m−2L 关系。完整表逐行计算，时间和空间均为 O((n+1)(m+1))。代码通过候选比较求最小值，不能把求最大长度时的比较方向照搬过来；返回表仍是代价证据，具体编辑对齐由例题恢复。

**完整程序**

```python
def edit_table(a, b):
    table = []
    for i in range(len(a) + 1):
        table.append([0] * (len(b) + 1))
        table[i][0] = i
    for j in range(len(b) + 1):
        table[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            extra = 0
            if a[i - 1] != b[j - 1]:
                extra = 1
            best = table[i - 1][j - 1] + extra
            if table[i - 1][j] + 1 < best:
                best = table[i - 1][j] + 1
            if table[i][j - 1] + 1 < best:
                best = table[i][j - 1] + 1
            table[i][j] = best
    return table

for row in edit_table("cat", "cut"):
    print(row)
```

**预期输出**

```text
[0, 1, 2, 3]
[1, 0, 1, 2]
[2, 1, 1, 2]
[3, 2, 2, 1]
```


选题关联：来源主题 1（文末列出）。

## 一个序列的状态：严格递增子序列以谁结尾

对整数列表 values，寻找原位置保持递增、所选数值也严格递增的最长子序列，简称严格 LIS。不能先排序再返回排序后的下标，因为排序破坏了原有先后关系。也不能把相等元素接起来，那会变成非降子序列问题。

定义 lengths\[i\] 为必须以位置 i 结尾的最长长度。单独选它就有长度 1；枚举所有更早的 j，若 values\[j\] 严格小于 values\[i\]，就可把 i 接在 j 的最佳序列后面，候选为 lengths\[j\]+1。任何以 i 结尾且长度大于 1 的合法序列，都有这样一个倒数第二位置，所以枚举完整。最后答案是所有结束位置中的最大值，不一定在列表末尾。

parent\[i\] 只在候选严格改善时记录 j；结束位置也只在严格改善时更新。于是同长度保留先遇到的前驱和结束点，提供确定的一种最优解。父下标每次严格减小，恢复一定终止。示例 \[3,1,2,2,5,4\] 返回原位置 \[1,2,4\]，值为 \[1,2,5\]；另一组原位置 \[1,2,5\] 对应值 \[1,2,4\]，也是最长，但这里没有采用字典序最小规则。

空输入没有结束位置，返回长度 0 和空下标表；全相等的非空列表返回第一项，长度 1。程序按原顺序扫描，不修改输入。内层枚举次数恰为 n(n−1)/2，时间 O(n²+1)，长度、前驱及结果空间 O(n+1)。存在更快的尾值与二分方法，但需要另外证明尾值状态以及恢复条件，本章不把那个时间界套到当前的平方实现。

**完整程序**

```python
def lis(values):
    lengths = [1] * len(values)
    parent = [None] * len(values)
    endpoint = None
    for i in range(len(values)):
        for j in range(i):
            if values[j] < values[i] and lengths[j] + 1 > lengths[i]:
                lengths[i] = lengths[j] + 1
                parent[i] = j
        if endpoint is None or lengths[i] > lengths[endpoint]:
            endpoint = i
    indices = []
    while endpoint is not None:
        indices.append(endpoint)
        endpoint = parent[endpoint]
    return {"length": len(indices), "indices": indices[::-1]}

print(lis([3, 1, 2, 2, 5, 4]))
print(lis([2, 2, 2]))
print(lis([]))
```

**预期输出**

```text
{'length': 3, 'indices': [1, 2, 4]}
{'length': 1, 'indices': [0]}
{'length': 0, 'indices': []}
```


选题关联：来源主题 1（文末列出）。

<a id="examples"></a>

## 跟着做：原创例题

### 例题 1

求 abac 与 baca 的最长公共子序列，返回两串中的位置对；说明 ab 与 ba 的平局结果为何不唯一。

1. 先按两个前缀填表，边界均为零，完整问题的 LCS 长度为 3。
2. 从末尾 c 与 a 不同开始，保留较大子问题；随后可依次配对 c、a、b。
3. 把倒序收集的对反转，得到 \[\[1,0\],\[2,1\],\[3,2\]\]，对应共同文字 bac。
4. 核对两列下标递增、三个码点分别相同；ab 与 ba 可选 a 或 b，程序依平局规则选 a。

**结果与核对**

第一组长度为 3，而两串长 4 且不相同，不可能有长度 4 的共同子序列，因此返回值达到上限。第二组有两个不同的最优文字，但程序只返回一个位置匹配。测试还用全部位置子集生成共同子序列集合，核对其他短串的最优长度，避免把恢复路径自身当作最优性证明。

**完整程序**

```python
def lcs_table(a, b):
    table = []
    for i in range(len(a) + 1):
        table.append([0] * (len(b) + 1))
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                table[i][j] = table[i - 1][j - 1] + 1
            else:
                table[i][j] = table[i - 1][j]
                if table[i][j - 1] > table[i][j]:
                    table[i][j] = table[i][j - 1]
    return table

def lcs_match(a, b):
    table = lcs_table(a, b)
    pairs = []
    i = len(a)
    j = len(b)
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            pairs.append([i - 1, j - 1])
            i = i - 1
            j = j - 1
        elif table[i - 1][j] >= table[i][j - 1]:
            i = i - 1
        else:
            j = j - 1
    return {"length": table[len(a)][len(b)], "pairs": pairs[::-1]}

print(lcs_match("abac", "baca"))
print(lcs_match("ab", "ba"))
```

**预期输出**

```text
{'length': 3, 'pairs': [[1, 0], [2, 1], [3, 2]]}
{'length': 1, 'pairs': [[0, 1]]}
```


### 例题 2

把 cab 变成 abc，恢复单位编辑距离的一种对齐。每一列 \[源字符,目标字符\] 中，None 表示该侧空位；解释空源与交换字母的结果。

1. 原串与目标长度相等，但三个位置都不同，一次替换不够；一次插入或删除又不能保持长度，故距离至少为 2。
2. 删除开头 c，保留 a、b，再在末尾插入 c，总代价为 2，达到下界。
3. 恢复时优先可达到最小值的对角候选，再尝试删除，最后插入；从后往前收集并反转列。
4. 去掉第一列中的 None 后重建源串，去掉第二列中的 None 后重建目标串，统计删除、插入、替换列共两次。

**结果与核对**

返回 \[\[c,None\],\[a,a\],\[b,b\],\[None,c\]\]，其中 c、a、b 表示对应单字符字符串。空源到“计”只需一列插入。ab 到 ba 的本模型距离为 2，程序选择两次替换；并没有把相邻交换计成一次。对齐列是稳定的消费源字符、生成目标字符的表示，不把列号误当作不断修改中的字符串下标。恢复 O(n+m+1)，完整表仍是二次规模；每列独立创建。

**完整程序**

```python
def edit_table(a, b):
    table = []
    for i in range(len(a) + 1):
        table.append([0] * (len(b) + 1))
        table[i][0] = i
    for j in range(len(b) + 1):
        table[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            extra = 0
            if a[i - 1] != b[j - 1]:
                extra = 1
            best = table[i - 1][j - 1] + extra
            if table[i - 1][j] + 1 < best:
                best = table[i - 1][j] + 1
            if table[i][j - 1] + 1 < best:
                best = table[i][j - 1] + 1
            table[i][j] = best
    return table

def edit_alignment(a, b):
    table = edit_table(a, b)
    columns = []
    i = len(a)
    j = len(b)
    while i > 0 or j > 0:
        extra = 0
        if i > 0 and j > 0 and a[i - 1] != b[j - 1]:
            extra = 1
        if i > 0 and j > 0 and table[i][j] == table[i - 1][j - 1] + extra:
            columns.append([a[i - 1], b[j - 1]])
            i = i - 1
            j = j - 1
        elif i > 0 and table[i][j] == table[i - 1][j] + 1:
            columns.append([a[i - 1], None])
            i = i - 1
        else:
            columns.append([None, b[j - 1]])
            j = j - 1
    return {"distance": table[len(a)][len(b)], "columns": columns[::-1]}

print(edit_alignment("cab", "abc"))
print(edit_alignment("", "计"))
print(edit_alignment("ab", "ba"))
```

**预期输出**

```text
{'distance': 2, 'columns': [['c', None], ['a', 'a'], ['b', 'b'], [None, 'c']]}
{'distance': 1, 'columns': [[None, '计']]}
{'distance': 2, 'columns': [['a', 'b'], ['b', 'a']]}
```


<a id="practice"></a>

## 自己做：先完成再看解答

### 练习 1

只求 abac 与 baca 的 LCS 长度，用一行数组实现；再检查 a 与 aa、空串与 aa，解释旧对角值如何保存。

<details>
<summary>提示</summary>

从左向右更新：row\[j\] 尚是上一行，row\[j−1\] 已是当前行；另用 diagonal 保存上一行的左邻。

</details>

<details>
<summary>解答与检查</summary>

先把旧 row\[j\] 保存到 old。相等时用 diagonal 加一，不等时比较旧上方和当前左方；结束本格后再让 diagonal=old。每一行开始的 diagonal 为零。结果依次为 3、1、0；若把刚更新的当前左邻当对角值，a 对 aa 可能错误地被用两次。时间 O((n+1)(m+1))、额外空间 O(m+1)，m 是第二个串长度；本实现没有交换两串来取较短维度，只返回长度。

**完整程序**

```python
def lcs_length_rolling(a, b):
    row = [0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        diagonal = 0
        for j in range(1, len(b) + 1):
            old = row[j]
            if a[i - 1] == b[j - 1]:
                row[j] = diagonal + 1
            elif row[j - 1] > row[j]:
                row[j] = row[j - 1]
            diagonal = old
    return row[len(b)]

print(lcs_length_rolling("abac", "baca"))
print(lcs_length_rolling("a", "aa"))
print(lcs_length_rolling("", "aa"))
```

**预期输出**

```text
3
1
0
```


</details>

### 练习 2

求 abxcd 与 abycd 的最长公共连续子串，返回长度及两串起点；若多个最长片段平局，优先 a 中起点小的，再优先 b 中起点小的。空结果规定起点均为 0。

<details>
<summary>提示</summary>

定义状态为恰好在两个当前位置结束的公共连续片段长度。相等接旧对角，不等必须归零，答案在整张表中取最大。

</details>

<details>
<summary>解答与检查</summary>

ab 和 cd 都长 2，按约定返回长度 2、起点 0 与 0。程序逐行逐列扫描，仅在严格变长时记录，因此最终最大长度平局时保留较早的结束位置，也就是较早起点。不相等处清零，不能沿上方或左方保留旧长度，否则又成了子序列。使用前后两行，时间 O((n+1)(m+1))、空间 O(m+1)；返回下标而不复制片段。空串或无共同字符时结果为长度 0、两起点 0。

**完整程序**

```python
def longest_common_substring(a, b):
    previous = [0] * (len(b) + 1)
    best = 0
    start_a = 0
    start_b = 0
    for i in range(1, len(a) + 1):
        current = [0] * (len(b) + 1)
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                current[j] = previous[j - 1] + 1
                if current[j] > best:
                    best = current[j]
                    start_a = i - best
                    start_b = j - best
        previous = current
    return {"length": best, "a_start": start_a, "b_start": start_b}

print(longest_common_substring("abxcd", "abycd"))
print(longest_common_substring("", "ab"))
```

**预期输出**

```text
{'length': 2, 'a_start': 0, 'b_start': 0}
{'length': 0, 'a_start': 0, 'b_start': 0}
```


</details>

### 练习 3

禁止替换，只允许每次插入或删除一个字符。用 LCS 长度求最小操作数，并比较 cat 到 cut 的答案与允许替换的编辑距离。

<details>
<summary>提示</summary>

任何未删除且保留下来的原字符，按顺序构成两串的共同子序列；先保留最长的一份，再删除和插入其余字符。

</details>

<details>
<summary>解答与检查</summary>

设 L 为 LCS 长度。保留它需要删除 n−L 个源字符、插入 m−L 个目标字符，给出 n+m−2L 次操作。反过来，任意操作序列中幸存的原字符至多 L 个，所以至少需要这两部分数量；界可以达到。cat 到 cut 的插删距离为 2，而允许替换时为 1；abac 到 baca 的插删距离也为 2。函数复用滚动 LCS，只返回数值，时间 O((n+1)(m+1))、空间 O(m+1)。不要将此公式用于允许一次相邻交换或任意编辑代价的其他模型。

**完整程序**

```python
def lcs_length_rolling(a, b):
    row = [0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        diagonal = 0
        for j in range(1, len(b) + 1):
            old = row[j]
            if a[i - 1] == b[j - 1]:
                row[j] = diagonal + 1
            elif row[j - 1] > row[j]:
                row[j] = row[j - 1]
            diagonal = old
    return row[len(b)]

def insertion_deletion_distance(a, b):
    common = lcs_length_rolling(a, b)
    return len(a) + len(b) - 2 * common

def edit_table(a, b):
    table = []
    for i in range(len(a) + 1):
        table.append([0] * (len(b) + 1))
        table[i][0] = i
    for j in range(len(b) + 1):
        table[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            extra = 0
            if a[i - 1] != b[j - 1]:
                extra = 1
            best = table[i - 1][j - 1] + extra
            if table[i - 1][j] + 1 < best:
                best = table[i - 1][j] + 1
            if table[i][j - 1] + 1 < best:
                best = table[i][j - 1] + 1
            table[i][j] = best
    return table

print(insertion_deletion_distance("cat", "cut"))
print(edit_table("cat", "cut")[3][3])
print(insertion_deletion_distance("abac", "baca"))
```

**预期输出**

```text
2
1
2
```


</details>

<a id="pitfalls"></a>

## 容易混淆的地方

- **把视觉上相同的字形直接当作相同长度、相同码点序列。** str 下标按 Unicode 码点；组合字符可能占多个位置，本章不做归一化或字形簇处理。
- **把最长公共连续子串的失配状态保留为邻格最大值。** 连续性要求失配时当前结束状态归零；子序列才允许跳过字符并沿邻格取最大。
- **把一条最优恢复路径当成全部最优方案，或者默认字典序最小。** 平局规则只选定一条路径；不同文字、位置对或编辑对齐都可能同样最优。
- **认为 LCS 长度直接决定所有定义下的编辑距离。** n+m−2L 适用于只允许单位插入删除；允许单位替换时必须使用相应的代价转移。

<a id="self-check"></a>

## 离开这一章前

- [ ] 手画 ab 与 ba 的 LCS 表，并恢复另一种最优位置匹配。
- [ ] 在 a 与 aa 的滚动计算中逐格标记旧上方、新左方与旧对角。
- [ ] 用恢复的编辑列分别重建源串与目标串，并重算操作代价。
- [ ] 为严格 LIS 找一个全重复输入，解释为什么答案不是整个列表。

## 本章边界

- 文本按 Unicode 码点直接比较，不覆盖编码转换、归一化、字形簇、模糊匹配或语言学相似度。
- 不枚举全部最优答案，也未实现二分尾值 LIS、线性空间 LCS 恢复及带权编辑距离。
- 本章的子序列和子串优化不代替 KMP 或 Trie 等模式匹配章节；复杂度按单位整数和码点比较分析。

## 选题来源与覆盖

来源含学生报告时，仅将其作为选题线索；具体机制仍需结合后续实验或权威资料核对。

- [大一小学期/Week\_3-Python/docs/readme.md](https://github.com/PKUanonym/REKCARC-TSC-UHT/blob/37cd19f7a9fb80dc846a7016b3fd482ed5fe7cc0/%E5%A4%A7%E4%B8%80%E5%B0%8F%E5%AD%A6%E6%9C%9F/Week_3-Python/docs/readme.md)（已提取可读文本，固定版本 37cd19f7a9fb）
- 主题 1：Python 基础语法的外部学习入口；位置：第 41–80 行。
- 主题 2：从基础语法到工具与应用的建议阅读顺序；位置：第 121–160 行。

## 参考资料与规则核对

上游入口用于确定学习方向；下面的参考资料用于核对语言语义、数据结构或算法分析规则，例题和练习由本项目重新设计。

- [Python 3.11：文本序列 str](https://docs.python.org/3.11/library/stdtypes.html#text-sequence-type-str)：核对不可变 Unicode 码点序列及下标；组合字符演示和算法接口自拟，不进行归一化。
- [MIT 6.006：最长公共子序列与父指针](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2008/1986024fc785732d48dc2e8d3780df1b_lec20.pdf)：仅核对子序列、前缀/后缀状态和恢复思想；本章使用前缀表、自己的平局规则、位置对及原创文字，不移植讲义程序。
- [NIST DADS：Levenshtein 距离](https://xlinux.nist.gov/dads/HTML/Levenshtein.html)：核对插入、删除、替换的最小次数定义；正文自行推导前缀转移与对齐，明确不包含一次相邻交换。
- [Algorithms for Competitive Programming：递增子序列](https://cp-algorithms.com/dynamic_programming/longest_increasing_subsequence.html)：核对严格递增与以当前位置结束的状态；本章独立编写平方实现和恢复，不采用该页更快算法的复杂度。

**继续学习**：先独立完成自测，再记录仍需回读的步骤。

[上一章：限定容量与使用次数：背包问题和方案计数](28-knapsack.md) · [下一章：按区间与子树组织依赖：区间和树形动态规划](30-interval-tree-dp.md)

[教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [哈希表与图练习指引](../hash-graphs-practice.md) · [拓扑排序与带权图练习指引](../weighted-graphs-practice.md) · [记录自己的学习](../learning-log-template.md)
