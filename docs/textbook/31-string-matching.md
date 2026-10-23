# 复用已经相等的部分：字符串匹配与 KMP

[返回教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [哈希表与图练习指引](../hash-graphs-practice.md) · [拓扑排序与带权图练习指引](../weighted-graphs-practice.md)

[上一章：按区间与子树组织依赖：区间和树形动态规划](30-interval-tree-dp.md) · [下一章：把共同开头存成路径：Trie 与前缀检索](32-trie.md)

[学习目标](#objectives) · [需要的基础](#prerequisites) · [例题](#examples) · [练习](#practice) · [自测](#self-check)

状态：**AI 初稿，可开始试学**。生成模型：Codex 当前会话（未记录具体模型型号）。

本章围绕资料中识别到的知识点重新编写；讲解、数值模型、例题与练习为 AI 原创组织，不是原课程题目或答案。主题出处只说明选题关联，不证明全部推导已经正确。

第 29 章允许跳过字符寻找共同子序列，本章改为寻找连续、完全相等的一段文字。同一个模式可能出现多次，也可能与自己重叠；读入文本时，还可能恰好把一个匹配切在两块之间。我们先用逐个起点尝试的方法建立可信的基准，再研究怎样利用已经相等的部分避免重复比较，得到 KMP。最后把同一份前缀信息用于周期、旋转与不重叠选择，逐项说明适用条件和输出位置。

<a id="objectives"></a>

## 学完要能做到

- 规定码点位置、空模式、失配与非法起点的不同返回值。
- 从真前缀与后缀推导前缀表以及失配后的候选链。
- 实现保留重叠结果的 KMP，并保持跨块匹配状态。
- 用边界链解释完整重复单元，并验证旋转与不重叠匹配。

<a id="prerequisites"></a>

## 需要的基础

- 第 29 章关于 Unicode 码点、子串与子序列的区别。
- 第 6、10 章的列表下标、循环不变式与复杂度。
- 第 26 章的交换论证；不要求有限自动机课程知识。

## 先说明匹配单位：一个起点上的连续相等

本章所有文本参数都是 Python str，模式也称 pattern。位置从零开始，按 Unicode 码点计数；区分大小写，不去空格，也不做归一化。“计算”有两个位置，预组成的 é 与 e 后接组合重音符则是不同序列。用户感知的一个字形可以包含多个码点，文件中的一个码点也可以占多个字节，因此这里返回的下标不能直接当作文件字节偏移或显示光标位置。

定义 match\_at(text, pattern, start)：只检查从 start 开始的连续内容。start 是整数，允许从 0 到文本长度；超出这个范围返回 None。位置合法但剩余字符不足或有字符不同，返回 False。全部对应相等返回 True。此约定把错误位置与正常失配分开，尤其防止 Python 的负下标悄悄变成“从尾部数”。

空模式不消耗字符，所以在文本的每个边界都匹配，包括末尾；长度 n 的文本有 n+1 个边界。它与找不到非空模式时的空结果列表含义不同。程序先检查起点和剩余长度，再读取字符；比较了前 j 个位置仍未返回时，这 j 对必然相等，循环结束便证明整个模式相等。

示例中，从“计算计算”的位置 2 可读到“计算”，é 却不能直接与组合形式相等。实现不切出子串，只做下标比较，因此除返回值外额外空间 O(1)，最坏时间 O(m+1)，m 是模式长度。后续所有字符串算法保持这份码点契约；对任意输入类型的运行时检查不在这些教学函数的接口范围内。

**完整程序**

```python
def match_at(text, pattern, start):
    if start < 0 or start > len(text):
        return None
    if start + len(pattern) > len(text):
        return False
    j = 0
    while j < len(pattern):
        if text[start + j] != pattern[j]:
            return False
        j = j + 1
    return True

print(match_at('计算计算', '计算', 2))
print(match_at('é', 'é', 0))
print(match_at('计', '', 1))
print(match_at('计', '', -1))
```

**预期输出**

```text
True
False
True
None
```


选题关联：来源主题 1（文末列出）。

## 朴素扫描：每个合法起点都要考虑

当模式长度为 m、文本长度为 n，非空模式的起点只能从 0 到 n−m；更靠后的位置放不下整个模式。逐个调用上一节的判定器，把成功起点加入结果，就是朴素的全部匹配算法。枚举从小到大进行，结果天然有序，而且不同起点不会重复输出。

找到一次后仍只把起点增加 1，不增加 m。文本 aaaaa 中的 aaa 出现在 0、1、2，三个片段彼此重叠。如果业务只想要不重叠的片段，应另外规定如何选择；先让基础匹配器保留全部事实，章末再用明确的选择规则处理。

空模式时 m 为零，枚举恰好覆盖 n+1 个边界。模式比文本长时，range 的终点非正，循环不执行，返回空列表；空文本与空模式则返回 \[0\]。这些情况都来自同一组边界公式，没有把空串当作异常，也没有读取不存在的字符。

正确性分两部分：任何输出位置都通过逐字符检查，所以不会误报；任何真实匹配都有合法起点，而每个合法起点都已尝试，所以不会漏报。代价也容易核对：令 s 为 max(n−m+1,0)，最多做 s 次、每次 m 个字符比较，含循环与空模式的时间上界是 O(s(m+1)+1)，输出 z 个位置占 O(z+1) 空间。大量重复字符会使许多起点反复比较同样的内容，这正是下一节要解决的问题。这种直接实现仍适合短输入的独立核对，不应因它较慢就跳过契约和证明。

**完整程序**

```python
def match_at(text, pattern, start):
    if start < 0 or start > len(text):
        return None
    if start + len(pattern) > len(text):
        return False
    j = 0
    while j < len(pattern):
        if text[start + j] != pattern[j]:
            return False
        j = j + 1
    return True

def naive_matches(text, pattern):
    result = []
    for start in range(len(text) - len(pattern) + 1):
        if match_at(text, pattern, start):
            result.append(start)
    return result

print(naive_matches('aaaaa', 'aaa'))
print(naive_matches('计计', ''))
print(naive_matches('a', 'aa'))
```

**预期输出**

```text
[0, 1, 2]
[0, 1, 2]
[]
```


选题关联：来源主题 1（文末列出）。

## 前缀表：失配以后还剩多少已知相等

一个串的边界，是既为前缀又为后缀的真子串；“真”排除整个串自身。定义 table\[i\] 为模式前 i+1 个字符的最长边界长度，没有非空边界时为 0。例如 abacabab 的最后一个前缀就是全串，它的最长边界为 ab，长度 2；表值记录长度，不是该边界最后字符的位置。

计算位置 i 时，先令 matched 为 table\[i−1\]。如果新字符与 pattern\[matched\] 相同，原边界就能扩展一位。否则，能继续尝试的较短边界必须也是原边界的边界：把两端已知相等的部分对齐后，其余较短候选恰落在这个更小的前缀中。因此下一候选为 table\[matched−1\]，沿同样的链不断缩短，不必从所有长度重新开始。

候选为零时，仍要把新字符与第零个字符比较；相同则得到长度 1，不同则仍为 0。循环从 i=1 开始，所以读取 pattern\[matched\] 时 matched 总是合法位置，空串与单字符输入无需进入循环。每次失败使候选严格变短，候选链覆盖所有可能的边界，因此最后保留的是最长可扩展者。

虽然代码有嵌套循环，总成本并非平方。把 matched 看作高度：每处理一个新字符至多增加 1，所有回退消耗先前积累的高度，累计回退次数为 O(m)。初始化表同样需要线性时间，故总时间和空间都是 O(m+1)。这只是总量界，某一次字符比较仍可能连续回退很多步。读表时还要分清 table\[i\] 和 table\[matched−1\] 的含义，不能把“已经匹配的长度”直接当作最后位置使用。

**完整程序**

```python
def prefix_table(pattern):
    table = [0] * len(pattern)
    for i in range(1, len(pattern)):
        matched = table[i - 1]
        while matched > 0 and pattern[i] != pattern[matched]:
            matched = table[matched - 1]
        if pattern[i] == pattern[matched]:
            matched = matched + 1
        table[i] = matched
    return table

print(prefix_table('abacabab'))
print(prefix_table('aaaa'))
print(prefix_table(''))
```

**预期输出**

```text
[0, 0, 1, 0, 1, 2, 3, 2]
[0, 1, 2, 3]
[]
```


选题关联：来源主题 1（文末列出）。

## KMP：文本只向前走，模式沿边界回退

先为非空模式构造前缀表，再从左到右读取文本。处理下一个字符之前，matched 表示已经读过的文本末尾，与模式前缀相等的最长可继续匹配长度。遇到不同字符，沿前缀表尝试较短边界；相同时把 matched 增加 1。文本下标不回头，因为被舍弃的起点已由边界关系证明不能成功。

当 matched 达到 m，说明模式完整结束在当前文本位置 i，起点为 i+1−m。输出以后不能保留 m，否则下一次会读到模式范围外；也不能总归零，否则会丢掉重叠匹配。应回到 table\[m−1\]，留下这次完整匹配的最长真边界，供下一个字符继续使用。

示例 ababababa 中的 ababa 出现在 0、2、4。第一次完整匹配后保留 aba 的长度 3，再读两个字符就能得到下一次匹配。每个结束位置至多输出一次；所有可行的后续起点都沿边界链保留，而失配跳过的候选不可能成功，因此顺序扫描既不误报也不漏报。

空模式单独返回全部边界，避免对不存在的模式字符建状态。实现直接在文本和模式间比较，无需寻找一个“绝不会出现在输入中”的特殊分隔符，中文、组合符和其他码点都按同样规则处理。令 z 为结果个数，含建表与输出的总时间为 O(n+m+z+1)，额外空间为 O(m+z+1)。这里字符比较和位置整数运算按单位成本分析；KMP 保证的是整个扫描的线性总量，不保证每读一个字符都只比较一次。

**完整程序**

```python
def prefix_table(pattern):
    table = [0] * len(pattern)
    for i in range(1, len(pattern)):
        matched = table[i - 1]
        while matched > 0 and pattern[i] != pattern[matched]:
            matched = table[matched - 1]
        if pattern[i] == pattern[matched]:
            matched = matched + 1
        table[i] = matched
    return table

def kmp_matches(text, pattern):
    result = []
    if len(pattern) == 0:
        for i in range(len(text) + 1):
            result.append(i)
        return result
    table = prefix_table(pattern)
    matched = 0
    for i in range(len(text)):
        while matched > 0 and text[i] != pattern[matched]:
            matched = table[matched - 1]
        if text[i] == pattern[matched]:
            matched = matched + 1
        if matched == len(pattern):
            result.append(i + 1 - len(pattern))
            matched = table[matched - 1]
    return result

print(kmp_matches('ababababa', 'ababa'))
print(kmp_matches('计算计算', '计算'))
print(kmp_matches('', ''))
```

**预期输出**

```text
[0, 2, 4]
[0, 2]
[0]
```


选题关联：来源主题 1（文末列出）。

## 跨块匹配：保留状态，也保留全局位置

文本如果分块到达，逐块各自重新搜索会漏掉横跨边界的模式。搜索 aba 时先收到 ab，再收到 aba，拼接后的 ababa 有起点 0 和 2 两次匹配；第一块本身没有完整匹配，却必须留下 matched=2。

matcher\_new 为一个非空模式创建独立状态，保存模式、前缀表、matched 与已经消费的码点数 consumed。matcher\_feed 只接受由此创建且未被外部改坏的状态和一个 str 块，返回这次读入新发现的全局起点，并原地更新状态。新的起点可能落在上一块，因为发现时刻由匹配的结束字符决定。

一次调用内部沿用 KMP 转移，输出位置加上调用前的 consumed，结束后再增加块长度。空块不产生结果，也不改变状态；两个搜索任务必须使用两个独立状态，不能把同一个可变字典当作互不相干的副本。前缀表和模式在读块时保持不变。

本接口对空模式返回 None，调用者需先处理这个返回值。批量接口已经定义空模式为所有边界；流式接口若也接受它，还必须约定首次空块、连续空块及块交界处的边界由哪次调用报告。本章选择明确拒绝，避免暗中重复或遗漏。处理 b 块、总长 n 的文本，连同一次建表和 z 个输出，累计时间 O(m+n+b+z+1)；持久状态空间 O(m+1)，单次返回列表另按本次输出数计。它接收的是已解码字符串，不能直接将任意字节块当作完整码点。

**完整程序**

```python
def prefix_table(pattern):
    table = [0] * len(pattern)
    for i in range(1, len(pattern)):
        matched = table[i - 1]
        while matched > 0 and pattern[i] != pattern[matched]:
            matched = table[matched - 1]
        if pattern[i] == pattern[matched]:
            matched = matched + 1
        table[i] = matched
    return table

def matcher_new(pattern):
    if len(pattern) == 0:
        return None
    return {'pattern': pattern, 'table': prefix_table(pattern),
            'matched': 0, 'consumed': 0}

def matcher_feed(state, chunk):
    pattern = state['pattern']
    table = state['table']
    matched = state['matched']
    result = []
    for i in range(len(chunk)):
        while matched > 0 and chunk[i] != pattern[matched]:
            matched = table[matched - 1]
        if chunk[i] == pattern[matched]:
            matched = matched + 1
        if matched == len(pattern):
            result.append(state['consumed'] + i + 1 - len(pattern))
            matched = table[matched - 1]
    state['matched'] = matched
    state['consumed'] = state['consumed'] + len(chunk)
    return result

state = matcher_new('aba')
print(matcher_feed(state, 'ab'))
print(matcher_feed(state, ''))
print(matcher_feed(state, 'aba'))
print(state['consumed'], state['matched'])
print(matcher_new(''))
```

**预期输出**

```text
[]
[]
[0, 2]
5 1
None
```


选题关联：来源主题 1（文末列出）。

<a id="examples"></a>

## 跟着做：原创例题

### 例题 1

在 aabaaabaa 中寻找全部 aabaa。列出模式的前缀表，解释为什么第一次匹配结束后不能清空状态。

1. 模式各前缀的最长边界长度为 \[0,1,0,1,2\]，最后的 aa 是长度 2 的边界。
2. 读完文本前五个字符得到起点 0，随后保留 matched=2。
3. 下一个字符 a 与模式位置 2 的 b 不同，回退至长度 1；同一个 a 又能扩展到长度 2。
4. 后续 b、a、a 依次完成剩余匹配，结束在位置 8，得到起点 4。

**结果与核对**

结果 \[0,4\]，两段在位置 4 共享一个 a。若完整匹配后归零，会把这个可复用后缀丢掉。核对时可逐个检查九个码点上的全部合法起点，而不是只相信前缀表；测试也采用切片相等的独立模型。输出下标按原文本解释，没有先删除第一次匹配，因此不会因文本长度变化而偏移。

**完整程序**

```python
def prefix_table(pattern):
    table = [0] * len(pattern)
    for i in range(1, len(pattern)):
        matched = table[i - 1]
        while matched > 0 and pattern[i] != pattern[matched]:
            matched = table[matched - 1]
        if pattern[i] == pattern[matched]:
            matched = matched + 1
        table[i] = matched
    return table

def kmp_matches(text, pattern):
    result = []
    if len(pattern) == 0:
        for i in range(len(text) + 1):
            result.append(i)
        return result
    table = prefix_table(pattern)
    matched = 0
    for i in range(len(text)):
        while matched > 0 and text[i] != pattern[matched]:
            matched = table[matched - 1]
        if text[i] == pattern[matched]:
            matched = matched + 1
        if matched == len(pattern):
            result.append(i + 1 - len(pattern))
            matched = table[matched - 1]
    return result

print(prefix_table('aabaa'))
print(kmp_matches('aabaaabaa', 'aabaa'))
```

**预期输出**

```text
[0, 1, 0, 1, 2]
[0, 4]
```


### 例题 2

求一个字符串由同一非空片段完整重复构成时，最短片段的长度；对空串约定返回 0。比较“计数计数计数”和 ababa。

1. 若长度 n 的串由长度 p 的片段重复构成，p 必须整除 n，且长度 n−p 的前缀与后缀相同。
2. 沿全串的边界链从长到短枚举，候选 p=n−边界长度便从小到大出现。
3. 边界相等意味着相隔 p 的字符相同；再加 p 整除 n，就能按长度 p 分块，且每一块相等。
4. 返回第一个整除候选；若非空边界均不满足，整个串自身就是长度 n 的可行片段。

**结果与核对**

第一串返回 2，重复三次“计数”；ababa 虽有长度 3 的边界，但候选 2 不能整除 5，不能说它由 ab 完整重复而成，最终返回 5。所有较短可行片段必对应已经枚举的边界，故第一个满足者最短。链每次严格缩短，含建表的时间和空间 O(n+1)。这版显式检查整条边界链，不借用尚未证明的周期简化定理。

**完整程序**

```python
def prefix_table(pattern):
    table = [0] * len(pattern)
    for i in range(1, len(pattern)):
        matched = table[i - 1]
        while matched > 0 and pattern[i] != pattern[matched]:
            matched = table[matched - 1]
        if pattern[i] == pattern[matched]:
            matched = matched + 1
        table[i] = matched
    return table

def repeating_unit_length(text):
    n = len(text)
    if n == 0:
        return 0
    table = prefix_table(text)
    border = table[n - 1]
    while border > 0:
        size = n - border
        if n % size == 0:
            return size
        border = table[border - 1]
    return n

print(repeating_unit_length('计数计数计数'))
print(repeating_unit_length('ababa'))
print(repeating_unit_length(''))
```

**预期输出**

```text
2
5
0
```


<a id="practice"></a>

## 自己做：先完成再看解答

### 练习 1

返回 abacaba 的全部非空真边界长度，按从大到小排列；再检查 aaaa 和空串。

<details>
<summary>提示</summary>

从最后一个前缀表值出发，反复进入该边界自身的最长真边界，直到长度为零。

</details>

<details>
<summary>解答与检查</summary>

依次得到 \[3,1\]、\[3,2,1\]、\[\]。任何比最长边界更短的全串边界，也是最长边界的边界；反方向也成立，因此整条链既完整又没有重复。零长度和全串本身按题意排除。先建表再走链，含 z 个输出的时间 O(n+z+1)，空间 O(n+z+1)；不要把链上的长度当作子串起点。

**完整程序**

```python
def prefix_table(pattern):
    table = [0] * len(pattern)
    for i in range(1, len(pattern)):
        matched = table[i - 1]
        while matched > 0 and pattern[i] != pattern[matched]:
            matched = table[matched - 1]
        if pattern[i] == pattern[matched]:
            matched = matched + 1
        table[i] = matched
    return table

def border_lengths(text):
    result = []
    if len(text) == 0:
        return result
    table = prefix_table(text)
    border = table[len(text) - 1]
    while border > 0:
        result.append(border)
        border = table[border - 1]
    return result

print(border_lengths('abacaba'))
print(border_lengths('aaaa'))
print(border_lengths(''))
```

**预期输出**

```text
[3, 1]
[3, 2, 1]
[]
```


</details>

### 练习 2

判断 target 是否是 source 的循环左移结果，若是返回最小左移码点数，否则返回 None；两空串返回 0。测试“计算结构”与“结构计算”、abab 与 baba。

<details>
<summary>提示</summary>

两个非空串需等长。左移 k 位得到的串，正是 source+source 从 k 开始、长度为原串长的连续片段；限制 k 严格小于原串长。

</details>

<details>
<summary>解答与检查</summary>

答案分别为 2 和 1。先拒绝长度不同，再在两份源串拼接中找目标；KMP 的结果递增，取第一个合法起点即可。重复串可能有多个合法旋转，题目要求最小位移；位置 n 与位置 0 等价，要排除。构造双倍文本也会复制字符，故等长时总时间和额外空间均为 O(n+1)，不能只计算模式表而忽略拼接及全部匹配列表。

**完整程序**

```python
def prefix_table(pattern):
    table = [0] * len(pattern)
    for i in range(1, len(pattern)):
        matched = table[i - 1]
        while matched > 0 and pattern[i] != pattern[matched]:
            matched = table[matched - 1]
        if pattern[i] == pattern[matched]:
            matched = matched + 1
        table[i] = matched
    return table

def kmp_matches(text, pattern):
    result = []
    if len(pattern) == 0:
        for i in range(len(text) + 1):
            result.append(i)
        return result
    table = prefix_table(pattern)
    matched = 0
    for i in range(len(text)):
        while matched > 0 and text[i] != pattern[matched]:
            matched = table[matched - 1]
        if text[i] == pattern[matched]:
            matched = matched + 1
        if matched == len(pattern):
            result.append(i + 1 - len(pattern))
            matched = table[matched - 1]
    return result

def rotation_offset(source, target):
    if len(source) != len(target):
        return None
    if len(source) == 0:
        return 0
    matches = kmp_matches(source + source, target)
    for start in matches:
        if start < len(source):
            return start
    return None

print(rotation_offset('计算结构', '结构计算'))
print(rotation_offset('abab', 'baba'))
print(rotation_offset('ab', 'aa'))
print(rotation_offset('', ''))
```

**预期输出**

```text
2
1
None
0
```


</details>

### 练习 3

对非空模式，选择数量最多且互不重叠的一组匹配，按起点递增输出；平局时采用依次选择最早可行起点的规则。求 aaaaaaa 中的 aaa，以及 ababababa 中的 aba。

<details>
<summary>提示</summary>

先获得全部匹配。每次选择起点不早于上一片段结束位置的最早一个，然后更新允许的下一个起点。

</details>

<details>
<summary>解答与检查</summary>

分别返回 \[0,3\] 与 \[0,4\]。所有匹配长度相同，最早起点也就是最早结束；任意最优方案的第一段都可换成这一段而不挤占后续空间，递归应用交换理由便证明数量最大。空模式返回 None，避免把零长度片段的选择混入本题。当前实现先保存全部 z 个匹配再筛选，总时间 O(n+m+z+1)，额外空间 O(m+z+1)，并非只使用最终选择数的空间。

**完整程序**

```python
def prefix_table(pattern):
    table = [0] * len(pattern)
    for i in range(1, len(pattern)):
        matched = table[i - 1]
        while matched > 0 and pattern[i] != pattern[matched]:
            matched = table[matched - 1]
        if pattern[i] == pattern[matched]:
            matched = matched + 1
        table[i] = matched
    return table

def kmp_matches(text, pattern):
    result = []
    if len(pattern) == 0:
        for i in range(len(text) + 1):
            result.append(i)
        return result
    table = prefix_table(pattern)
    matched = 0
    for i in range(len(text)):
        while matched > 0 and text[i] != pattern[matched]:
            matched = table[matched - 1]
        if text[i] == pattern[matched]:
            matched = matched + 1
        if matched == len(pattern):
            result.append(i + 1 - len(pattern))
            matched = table[matched - 1]
    return result

def disjoint_matches(text, pattern):
    if len(pattern) == 0:
        return None
    result = []
    next_start = 0
    for start in kmp_matches(text, pattern):
        if start >= next_start:
            result.append(start)
            next_start = start + len(pattern)
    return result

print(disjoint_matches('aaaaaaa', 'aaa'))
print(disjoint_matches('ababababa', 'aba'))
print(disjoint_matches('abc', ''))
```

**预期输出**

```text
[0, 3]
[0, 4]
None
```


</details>

<a id="pitfalls"></a>

## 容易混淆的地方

- **把字符串下标当作字节位置，或认为视觉相同就必须匹配。** 本章比较码点序列；归一化、字形簇与编码转换需另设接口和位置映射。
- **失配后把文本下标也退回去，或匹配完成后总把状态清零。** 文本向前扫描，模式沿边界链回退；完整匹配后保留最长真边界以发现重叠结果。
- **只要存在短周期就认定能完整重复。** 完整分块还要求片段长度整除总长；ababa 是直接反例。
- **把批量空模式约定无声套进流式接口。** 本章流式初始化明确拒绝空模式；若扩展，先定义每个边界只报告一次的协议。

<a id="self-check"></a>

## 离开这一章前

- [ ] 手算 abacabab 的最后一次回退，解释为什么候选由 3 变成 1。
- [ ] 把 ababa 分成所有两块方式，核对流式结果始终是 \[0,2\]。
- [ ] 为模式长于文本、空模式和不存在匹配分别写出期望结果。
- [ ] 用全部子集验证一个短文本的不重叠匹配选择数。

## 本章边界

- 只覆盖单模式、码点级精确匹配；未实现归一化、字形簇切分、字节解码、正则表达式及多模式自动机。
- 流式状态只供顺序调用，未设计并发修改、序列化或不可信状态的校验。
- 复杂度采用码点比较与位置整数运算的单位成本，内存还需容纳输入及返回结果；代码用于学习，不声称快于 Python 内建查找。

## 选题来源与覆盖

来源含学生报告时，仅将其作为选题线索；具体机制仍需结合后续实验或权威资料核对。

- [大一小学期/Week\_3-Python/docs/readme.md](https://github.com/PKUanonym/REKCARC-TSC-UHT/blob/37cd19f7a9fb80dc846a7016b3fd482ed5fe7cc0/%E5%A4%A7%E4%B8%80%E5%B0%8F%E5%AD%A6%E6%9C%9F/Week_3-Python/docs/readme.md)（已提取可读文本，固定版本 37cd19f7a9fb）
- 主题 1：Python 基础语法的外部学习入口；位置：第 41–80 行。
- 主题 2：从基础语法到工具与应用的建议阅读顺序；位置：第 121–160 行。

## 参考资料与规则核对

上游入口用于确定学习方向；下面的参考资料用于核对语言语义、数据结构或算法分析规则，例题和练习由本项目重新设计。

- [Python 3.11：文本序列 str](https://docs.python.org/3.11/library/stdtypes.html#text-sequence-type-str)：核对码点序列、切片和不可变字符串语义；本章以原创字符串规定位置和空结果，不实现归一化或编码转换。
- [Unicode UAX 29：文本分段](https://www.unicode.org/reports/tr29/)：仅核对码点与用户感知字符、字形簇边界的区别；本章明确不实现该标准的分段算法。
- [Cornell CS312：字符串搜索](https://www.cs.cornell.edu/courses/cs312/2002fa/lectures/lec26.htm)：核对连续匹配和失配后利用前后缀的理由；本章自定全部匹配、空模式及跨块接口，未复制讲义伪代码或示例。
- [Algorithms for Competitive Programming：前缀函数](https://cp-algorithms.com/string/prefix-function.html)：核对边界链与前缀表的线性总量；原创 Python 实现直接扫描两串，周期例题显式枚举边界，不移植页面程序或练习。

**继续学习**：先独立完成自测，再记录仍需回读的步骤。

[上一章：按区间与子树组织依赖：区间和树形动态规划](30-interval-tree-dp.md) · [下一章：把共同开头存成路径：Trie 与前缀检索](32-trie.md)

[教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [哈希表与图练习指引](../hash-graphs-practice.md) · [拓扑排序与带权图练习指引](../weighted-graphs-practice.md) · [记录自己的学习](../learning-log-template.md)
