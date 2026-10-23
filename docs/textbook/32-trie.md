# 把共同开头存成路径：Trie 与前缀检索

[返回教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [哈希表与图练习指引](../hash-graphs-practice.md) · [拓扑排序与带权图练习指引](../weighted-graphs-practice.md)

[上一章：复用已经相等的部分：字符串匹配与 KMP](31-string-matching.md) · [下一章：复用区间信息：前缀和、双指针与滑动窗口](33-prefix-window.md)

[学习目标](#objectives) · [需要的基础](#prerequisites) · [例题](#examples) · [练习](#practice) · [自测](#self-check)

状态：**AI 初稿，可开始试学**。生成模型：Codex 当前会话（未记录具体模型型号）。

本章围绕资料中识别到的知识点重新编写；讲解、数值模型、例题与练习为 AI 原创组织，不是原课程题目或答案。主题出处只说明选题关联，不证明全部推导已经正确。

搜索一个固定模式时，KMP 复用模式自身的前缀信息；若要保存许多词并不断查询共同前缀，可以把相同开头直接共享在一棵树中。这就是 Trie，也叫前缀树。本章从可重复的词库出发，区分路径存在、完整词结束和前缀下有多少词，逐步加入删除、枚举与最长前缀查询。我们既检查每次操作的答案，也检查整棵树的计数关系，让结构维护有可以反复核对的依据。

<a id="objectives"></a>

## 学完要能做到

- 用字符边与结束计数表达空词、重复词和共享前缀。
- 维护子树词数不变式，实现精确查询、前缀计数与删除一次。
- 说明枚举次序、结果复制以及保留旧结点的空间代价。
- 实现最长已存前缀、单字符通配、共同前缀与稳定去重。

<a id="prerequisites"></a>

## 需要的基础

- 第 16、19 章的树结构与哈希映射基础。
- 第 8、20 章的栈和显式深度优先遍历。
- 第 31 章的码点字符串契约；本章不需要 KMP 的前缀表。

## 共享路径：结束计数与子树词数各管什么

从根出发，每条边标一个码点，一条路径拼起来就是某个前缀。根代表空前缀。保存“计”和“计算”只需共用第一条“计”边，再为后者加“算”边；是否存过完整的“计”，不能仅靠这条路径存在判断，还需记录它是否在这里结束。

程序把结点放在 nodes 列表中，以整数下标连接。每个结点有 next 字典、end 结束次数和 count 子树词数。字典的键是单字符 str，值是孩子下标；char in mapping 检查键是否存在，char not in mapping 表示不存在。字符直接作为键，无需把中文强行换成 26 个字母槽位；每个结点的字典必须独立创建。

插入一次词，就把根及沿途所有结点的 count 加一，最后把 end 加一。重复词复用整条路径，但计数继续增加；空词不走任何边，在根增加两个计数。于是每个结点始终满足：count 等于自身 end 加所有孩子 count 的总和。根的 count 是含重复次数的词库大小，不是结点数，也不是不同词数。

示例插入“计”“计算”“计”和空词后仅有三个结点，根总数为 4，“计”结点的子树数为 3、结束数为 2。接口只接收未被外部破坏的本章结构和 str，插入会原地修改词库。按字典操作期望 O(1)、列表扩容摊还 O(1) 分析，插入长度 L 的词需期望 O(L+1) 时间，至多新增 L 个结点。以下哈希相关时间都采用这个假设，不把它写成无条件最坏保证；巨大计数还要另计整数位运算和存储成本。

**完整程序**

```python
def trie_new():
    return [{'next': {}, 'end': 0, 'count': 0}]

def trie_add(nodes, word):
    current = 0
    nodes[current]['count'] = nodes[current]['count'] + 1
    for char in word:
        if char not in nodes[current]['next']:
            nodes[current]['next'][char] = len(nodes)
            nodes.append({'next': {}, 'end': 0, 'count': 0})
        current = nodes[current]['next'][char]
        nodes[current]['count'] = nodes[current]['count'] + 1
    nodes[current]['end'] = nodes[current]['end'] + 1

nodes = trie_new()
trie_add(nodes, '计')
trie_add(nodes, '计算')
trie_add(nodes, '计')
trie_add(nodes, '')
print(len(nodes))
print(nodes[0]['count'], nodes[0]['end'])
child = nodes[0]['next']['计']
print(nodes[child]['count'], nodes[child]['end'])
```

**预期输出**

```text
3
4 1
3 2
```


选题关联：来源主题 1（文末列出）。

## 两种查询：完整词次数与前缀覆盖次数

trie\_locate 沿给定前缀逐字符走边，缺边时返回 None，否则返回到达的结点下标。空前缀直接返回根下标 0；判断失败应使用 is None，不能把下标 0 当成假值而误判。这个定位操作只说明路径存在，真正的词库语义由结点上的计数决定。

精确查询读取终点的 end，前缀查询读取终点的 count；缺路径都返回 0。词库有两次“计算”、一次“计时”和一次空词时，精确查“计”是 0，前缀查“计”却是 3。查空前缀得到全库四次词，精确查空词只得到一次。这些差异不是特殊补丁，而是根及各结点含义的直接结果。

两种查询都以走过的路径表示已经确认相等的开头。每走一条边，新确认一个字符；路径缺失时，任何以该开头存入的词都应要求这条边，因此不可能存在。到达后，结束计数与子树计数的不变式分别给出两种答案。程序不扫描所有完整词，也不将共享前缀重复保存。

长度 P 的查询需期望 O(P+1) 时间、O(1) 额外空间，不修改树。即使有百万次相同词，查询也不逐次枚举它们；但若要求列出所有匹配，输出成本不可消失，后面另行分析。所有比较保持大小写和码点形式，é 与组合形式仍是两个键序列；业务若希望合并它们，应在插入与查询两端采用一致的预处理，而不能只修改查询端。

**完整程序**

```python
def trie_new():
    return [{'next': {}, 'end': 0, 'count': 0}]

def trie_add(nodes, word):
    current = 0
    nodes[current]['count'] = nodes[current]['count'] + 1
    for char in word:
        if char not in nodes[current]['next']:
            nodes[current]['next'][char] = len(nodes)
            nodes.append({'next': {}, 'end': 0, 'count': 0})
        current = nodes[current]['next'][char]
        nodes[current]['count'] = nodes[current]['count'] + 1
    nodes[current]['end'] = nodes[current]['end'] + 1

def trie_locate(nodes, prefix):
    current = 0
    for char in prefix:
        if char not in nodes[current]['next']:
            return None
        current = nodes[current]['next'][char]
    return current

def trie_exact(nodes, word):
    current = trie_locate(nodes, word)
    if current is None:
        return 0
    return nodes[current]['end']

def trie_prefix_count(nodes, prefix):
    current = trie_locate(nodes, prefix)
    if current is None:
        return 0
    return nodes[current]['count']

nodes = trie_new()
for word in ['计算', '计算', '计时', '']:
    trie_add(nodes, word)
print(trie_exact(nodes, '计'), trie_prefix_count(nodes, '计'))
print(trie_exact(nodes, '计算'), trie_prefix_count(nodes, ''))
print(trie_exact(nodes, ''), trie_prefix_count(nodes, '算'))
```

**预期输出**

```text
0 3
2 4
1 0
```


选题关联：来源主题 1（文末列出）。

## 删除一次：先确认存在，再一起减少计数

删除 word 的一次出现，成功返回 True，词不存在返回 False。先走完整条路径，把经过的结点下标放进 path；缺边或终点 end 为零时立即返回失败，此时一个计数也不能改。否则先把终点 end 减一，再把 path 上各结点 count 减一。

为什么必须连根一起减少？被删除的这次词原先属于路径上每个前缀的子树，因此它们都应少一次。对终点，end 与 count 同减；对祖先，自己的 count 与一个孩子 count 同减，等式继续成立。对路径外结点没有影响。空词的路径只有根，算法自然只减少根的 end 与 count。

如果“算”保存两次、“算法”保存一次，前两次删除“算”都成功，但第二次以后“算”结点仍需保留，才能通向“算法”；第三次删除“算”失败，不能把后者一起抹掉。即使整个分支的 count 已为零，本实现仍保留结点和边，以简化下标管理并支持以后复用。

这种保留方式意味着路径存在不再等价于当前有词使用它，查询与枚举必须看计数。空间按历史上建立过的不同前缀计算，删除不会收缩 nodes。不能宣称空间只与当前词数有关，更不能直接从列表中间删结点而忘记修改其他下标。长度 L 的删除需期望 O(L+1) 时间及 O(L+1) 路径空间；失败也最多走这条路径。调用者应把 nodes 当作内部结构，直接改 count 或共享字典会破坏这里的推理前提。

**完整程序**

```python
def trie_new():
    return [{'next': {}, 'end': 0, 'count': 0}]

def trie_add(nodes, word):
    current = 0
    nodes[current]['count'] = nodes[current]['count'] + 1
    for char in word:
        if char not in nodes[current]['next']:
            nodes[current]['next'][char] = len(nodes)
            nodes.append({'next': {}, 'end': 0, 'count': 0})
        current = nodes[current]['next'][char]
        nodes[current]['count'] = nodes[current]['count'] + 1
    nodes[current]['end'] = nodes[current]['end'] + 1

def trie_locate(nodes, prefix):
    current = 0
    for char in prefix:
        if char not in nodes[current]['next']:
            return None
        current = nodes[current]['next'][char]
    return current

def trie_exact(nodes, word):
    current = trie_locate(nodes, word)
    if current is None:
        return 0
    return nodes[current]['end']

def trie_prefix_count(nodes, prefix):
    current = trie_locate(nodes, prefix)
    if current is None:
        return 0
    return nodes[current]['count']

def trie_remove(nodes, word):
    current = 0
    path = [0]
    for char in word:
        if char not in nodes[current]['next']:
            return False
        current = nodes[current]['next'][char]
        path.append(current)
    if nodes[current]['end'] == 0:
        return False
    nodes[current]['end'] = nodes[current]['end'] - 1
    for index in path:
        nodes[index]['count'] = nodes[index]['count'] - 1
    return True

nodes = trie_new()
for word in ['算', '算法', '算', '']:
    trie_add(nodes, word)
print(trie_remove(nodes, '算'), trie_exact(nodes, '算'))
print(trie_remove(nodes, '算'), trie_prefix_count(nodes, '算'))
print(trie_remove(nodes, '算'), trie_exact(nodes, '算法'))
print(trie_remove(nodes, ''), trie_prefix_count(nodes, ''))
```

**预期输出**

```text
True 1
True 1
False 1
True 1
```


选题关联：来源主题 1（文末列出）。

## 枚举前缀下的词：顺序与输出都有成本

trie\_words 返回前缀下所有仍存在的不同词，每项为 \[词,次数\]；重复词用次数合并，缺路径或终点 count 为零时返回空列表。先定位前缀，再用显式栈遍历其子树，结点 end 为正时报告该词，只进入 count 为正的孩子。

这里规定先报告当前结点，再按孩子边首次创建的顺序向下遍历。Python 字典保留键的插入顺序；为让后进先出的栈按这个顺序弹出，程序先收集孩子，再反向压栈。它没有对字符排序，也不按完整词的全局插入先后输出。例如先插 bat、再插 ab、再插 ba，枚举仍先报告 ba 再报告 bat，然后才到 ab；空词若存在，作为根的结束词最先报告。

每个结点只有一个父亲，前缀路径唯一，所以遍历不需通用图的 visited，也不会重复报告同一个词。删除后保留的零计数分支不产生结果，重新插入复用旧边时，边的历史创建顺序也保留。返回的外层表和次数记录都是新列表，修改这些列表不会改动词库；字符串不可变，可安全共享。

不能把枚举成本直接写成 O(词数)。程序沿边使用 text+char 构造新字符串，每次会复制当前前缀；长单链上的总复制量也可能是平方。设历史结点数 N、最大词长 H、查询前缀长 P，含扫描旧边与构造结果的保守期望时间上界为 O(P+N(H+1)+1)，额外空间也可用这个量作上界。更精细的计量是实际扫描边数加所有新建路径字符串的长度之和。压缩路径或共享字符缓冲区属于另一个实现，不能替当前代码省掉成本。

**完整程序**

```python
def trie_new():
    return [{'next': {}, 'end': 0, 'count': 0}]

def trie_add(nodes, word):
    current = 0
    nodes[current]['count'] = nodes[current]['count'] + 1
    for char in word:
        if char not in nodes[current]['next']:
            nodes[current]['next'][char] = len(nodes)
            nodes.append({'next': {}, 'end': 0, 'count': 0})
        current = nodes[current]['next'][char]
        nodes[current]['count'] = nodes[current]['count'] + 1
    nodes[current]['end'] = nodes[current]['end'] + 1

def trie_locate(nodes, prefix):
    current = 0
    for char in prefix:
        if char not in nodes[current]['next']:
            return None
        current = nodes[current]['next'][char]
    return current

def trie_exact(nodes, word):
    current = trie_locate(nodes, word)
    if current is None:
        return 0
    return nodes[current]['end']

def trie_prefix_count(nodes, prefix):
    current = trie_locate(nodes, prefix)
    if current is None:
        return 0
    return nodes[current]['count']

def trie_words(nodes, prefix):
    current = trie_locate(nodes, prefix)
    if current is None or nodes[current]['count'] == 0:
        return []
    result = []
    stack = [[current, prefix]]
    while len(stack) > 0:
        frame = stack.pop()
        index = frame[0]
        text = frame[1]
        if nodes[index]['end'] > 0:
            result.append([text, nodes[index]['end']])
        pending = []
        for char in nodes[index]['next']:
            child = nodes[index]['next'][char]
            if nodes[child]['count'] > 0:
                pending.append([child, text + char])
        i = len(pending) - 1
        while i >= 0:
            stack.append(pending[i])
            i = i - 1
    return result

nodes = trie_new()
for word in ['bat', 'ab', 'ba', 'bat', '']:
    trie_add(nodes, word)
print(trie_words(nodes, ''))
print(trie_words(nodes, 'ba'))
print(trie_words(nodes, 'z'))
```

**预期输出**

```text
[['', 1], ['ba', 1], ['bat', 2], ['ab', 1]]
[['ba', 1], ['bat', 2]]
[]
```


选题关联：来源主题 1（文末列出）。

## 最长已存前缀：走得最深不等于词已结束

给定查询 query，找出词库中作为 query 前缀的最长完整词，返回其码点长度；没有这样的词返回 None。接口只返回长度，调用者需要文字时再取 query 的对应切片。若词库确实含空词，长度 0 是合法结果，必须与 None 分开。

从根沿 query 行走，每遇到一个 end 为正的结点就更新 best。边缺失、孩子 count 为零或查询结束时，返回最近一次记录的 best。路径越深，前缀越长，故后一次有效结束自然优于前一次；路径上未标结束的结点只是中间前缀，不能覆盖答案。

示例存有空词、“算”“算法”“算法论”，查询“算法题”应返回 2，对应“算法”；读到“题”时没有边，但此前完整词仍有效。查询“树”返回 0，因为空词存在；全新空词库查询“树”返回 None。若只有“算法论”，查询“算法”应返回 None，虽然整条查询路径都存在，却没有任何非空完整词在途中结束。

所有可能答案都必须是 query 的一个前缀，因而只能位于这条路径上；记录所有可达结束位置中的最深者已经覆盖全部候选，无需搜索旁支。长度 Q 的查询期望时间 O(Q+1)，额外空间 O(1)。这与“查询串跟某个词最多共享多长开头”不同，也与“找所有以查询为开头的词”不同；后者是上一节的子树枚举。实际应用先写清这三种问题，再决定返回长度、次数还是词列表。

**完整程序**

```python
def trie_new():
    return [{'next': {}, 'end': 0, 'count': 0}]

def trie_add(nodes, word):
    current = 0
    nodes[current]['count'] = nodes[current]['count'] + 1
    for char in word:
        if char not in nodes[current]['next']:
            nodes[current]['next'][char] = len(nodes)
            nodes.append({'next': {}, 'end': 0, 'count': 0})
        current = nodes[current]['next'][char]
        nodes[current]['count'] = nodes[current]['count'] + 1
    nodes[current]['end'] = nodes[current]['end'] + 1

def trie_longest_prefix(nodes, query):
    best = None
    if nodes[0]['end'] > 0:
        best = 0
    current = 0
    for i in range(len(query)):
        if query[i] not in nodes[current]['next']:
            return best
        current = nodes[current]['next'][query[i]]
        if nodes[current]['count'] == 0:
            return best
        if nodes[current]['end'] > 0:
            best = i + 1
    return best

nodes = trie_new()
for word in ['', '算', '算法', '算法论']:
    trie_add(nodes, word)
print(trie_longest_prefix(nodes, '算法题'))
print(trie_longest_prefix(nodes, '树'))
print(trie_longest_prefix(trie_new(), '树'))
```

**预期输出**

```text
2
0
None
```


选题关联：来源主题 1（文末列出）。

<a id="examples"></a>

## 跟着做：原创例题

### 例题 1

词库依次加入“数据”“数据结构”“数据”“数据库”和空词，然后删除一次“数据”。分别求“数据”的精确次数、前缀总次数及枚举结果。

1. 五次插入后根 count 为 5；“数据”结点 end 为 2，count 为 4。
2. 成功删除一次后，根总数变 4，“数据”结点 end 变 1、count 变 3。
3. 精确查询只看 end，前缀查询还包含“数据结构”和“数据库”。
4. 按结点先于孩子、边创建顺序的规则，报告“数据”一次、“数据结构”一次、“数据库”一次。

**结果与核对**

精确次数为 1，前缀次数为 3，三个不同词各保存一次。空词仍在根，但不以非空的“数据”为前缀，因此不在这一枚举结果中。独立核验可直接维护词列表，删除其中一次相等元素，再按字符串开头筛选；没有必要用另一棵 Trie 重复同一套逻辑。

**完整程序**

```python
def trie_new():
    return [{'next': {}, 'end': 0, 'count': 0}]

def trie_add(nodes, word):
    current = 0
    nodes[current]['count'] = nodes[current]['count'] + 1
    for char in word:
        if char not in nodes[current]['next']:
            nodes[current]['next'][char] = len(nodes)
            nodes.append({'next': {}, 'end': 0, 'count': 0})
        current = nodes[current]['next'][char]
        nodes[current]['count'] = nodes[current]['count'] + 1
    nodes[current]['end'] = nodes[current]['end'] + 1

def trie_remove(nodes, word):
    current = 0
    path = [0]
    for char in word:
        if char not in nodes[current]['next']:
            return False
        current = nodes[current]['next'][char]
        path.append(current)
    if nodes[current]['end'] == 0:
        return False
    nodes[current]['end'] = nodes[current]['end'] - 1
    for index in path:
        nodes[index]['count'] = nodes[index]['count'] - 1
    return True

def trie_locate(nodes, prefix):
    current = 0
    for char in prefix:
        if char not in nodes[current]['next']:
            return None
        current = nodes[current]['next'][char]
    return current

def trie_exact(nodes, word):
    current = trie_locate(nodes, word)
    if current is None:
        return 0
    return nodes[current]['end']

def trie_prefix_count(nodes, prefix):
    current = trie_locate(nodes, prefix)
    if current is None:
        return 0
    return nodes[current]['count']

def trie_words(nodes, prefix):
    current = trie_locate(nodes, prefix)
    if current is None or nodes[current]['count'] == 0:
        return []
    result = []
    stack = [[current, prefix]]
    while len(stack) > 0:
        frame = stack.pop()
        index = frame[0]
        text = frame[1]
        if nodes[index]['end'] > 0:
            result.append([text, nodes[index]['end']])
        pending = []
        for char in nodes[index]['next']:
            child = nodes[index]['next'][char]
            if nodes[child]['count'] > 0:
                pending.append([child, text + char])
        i = len(pending) - 1
        while i >= 0:
            stack.append(pending[i])
            i = i - 1
    return result

nodes = trie_new()
for word in ['数据', '数据结构', '数据', '数据库', '']:
    trie_add(nodes, word)
print(trie_remove(nodes, '数据'))
print(trie_exact(nodes, '数据'), trie_prefix_count(nodes, '数据'))
print(trie_words(nodes, '数据'))
```

**预期输出**

```text
True
1 3
[['数据', 1], ['数据结构', 1], ['数据库', 1]]
```


### 例题 2

只插入一次“旧词”后将它删除，再查询“旧”并重新插入“旧词”。结点数、前缀次数和枚举结果如何变化？

1. 插入时建立根、“旧”、“旧词”共三个结点，沿途 count 均为 1。
2. 删除成功后全部 count 与终点 end 变为零，三结点及两条边保留。
3. 定位“旧”仍能到达结点，但前缀次数为零，枚举返回空列表。
4. 重新插入沿已有路径增加计数，无需新建结点，精确次数回到 1。

**结果与核对**

输出结点数始终为 3；删除后的前缀次数为 0，重新插入后精确次数为 1。这说明“历史路径存在”与“当前词存在”需要分别检查。若不断插入不同词再删除，历史空间仍会增长；要回收应设计完整的空分支解绑与结点管理，不能仅依据当前返回结果为空就声称结构已经释放。

**完整程序**

```python
def trie_new():
    return [{'next': {}, 'end': 0, 'count': 0}]

def trie_add(nodes, word):
    current = 0
    nodes[current]['count'] = nodes[current]['count'] + 1
    for char in word:
        if char not in nodes[current]['next']:
            nodes[current]['next'][char] = len(nodes)
            nodes.append({'next': {}, 'end': 0, 'count': 0})
        current = nodes[current]['next'][char]
        nodes[current]['count'] = nodes[current]['count'] + 1
    nodes[current]['end'] = nodes[current]['end'] + 1

def trie_remove(nodes, word):
    current = 0
    path = [0]
    for char in word:
        if char not in nodes[current]['next']:
            return False
        current = nodes[current]['next'][char]
        path.append(current)
    if nodes[current]['end'] == 0:
        return False
    nodes[current]['end'] = nodes[current]['end'] - 1
    for index in path:
        nodes[index]['count'] = nodes[index]['count'] - 1
    return True

def trie_locate(nodes, prefix):
    current = 0
    for char in prefix:
        if char not in nodes[current]['next']:
            return None
        current = nodes[current]['next'][char]
    return current

def trie_exact(nodes, word):
    current = trie_locate(nodes, word)
    if current is None:
        return 0
    return nodes[current]['end']

def trie_prefix_count(nodes, prefix):
    current = trie_locate(nodes, prefix)
    if current is None:
        return 0
    return nodes[current]['count']

def trie_words(nodes, prefix):
    current = trie_locate(nodes, prefix)
    if current is None or nodes[current]['count'] == 0:
        return []
    result = []
    stack = [[current, prefix]]
    while len(stack) > 0:
        frame = stack.pop()
        index = frame[0]
        text = frame[1]
        if nodes[index]['end'] > 0:
            result.append([text, nodes[index]['end']])
        pending = []
        for char in nodes[index]['next']:
            child = nodes[index]['next'][char]
            if nodes[child]['count'] > 0:
                pending.append([child, text + char])
        i = len(pending) - 1
        while i >= 0:
            stack.append(pending[i])
            i = i - 1
    return result

nodes = trie_new()
trie_add(nodes, '旧词')
print(trie_remove(nodes, '旧词'))
print(len(nodes), trie_prefix_count(nodes, '旧'))
print(trie_words(nodes, '旧'))
trie_add(nodes, '旧词')
print(len(nodes), trie_exact(nodes, '旧词'))
```

**预期输出**

```text
True
3 0
[]
3 1
```


<a id="practice"></a>

## 自己做：先完成再看解答

### 练习 1

增加匹配计数：模式中的 ? 恰好代表一个任意码点，其他字符按字面比较，要求整个词等长匹配并计入重复次数。词库为“猫咪”“猫粮”“猫咪”“狗粮”“猫”和空词，求“猫?”、“?粮”和空模式的结果。

<details>
<summary>提示</summary>

每读一个模式字符维护所有仍可能到达的结点；? 沿全部活跃孩子走一步，普通字符只走同名边，最后相加 end。

</details>

<details>
<summary>解答与检查</summary>

答案为 3、2、1。长度不足或过长的词不会在最终层贡献 end；空模式只看根的 end。树中每个结点有唯一父亲，同一层候选不会从不同路径重复到达。设模式长 M、历史结点数 N，扫描层次和边的保守期望时间 O(M+N+1)，候选表空间 O(N+1)，不会一般地降为 O(M)。本练习无转义语法，? 无法作为字面查询，星号没有特殊含义，也不支持任意长度通配。

**完整程序**

```python
def trie_new():
    return [{'next': {}, 'end': 0, 'count': 0}]

def trie_add(nodes, word):
    current = 0
    nodes[current]['count'] = nodes[current]['count'] + 1
    for char in word:
        if char not in nodes[current]['next']:
            nodes[current]['next'][char] = len(nodes)
            nodes.append({'next': {}, 'end': 0, 'count': 0})
        current = nodes[current]['next'][char]
        nodes[current]['count'] = nodes[current]['count'] + 1
    nodes[current]['end'] = nodes[current]['end'] + 1

def trie_wildcard_count(nodes, pattern):
    frontier = [0]
    for char in pattern:
        following = []
        for index in frontier:
            if char == '?':
                for edge in nodes[index]['next']:
                    child = nodes[index]['next'][edge]
                    if nodes[child]['count'] > 0:
                        following.append(child)
            else:
                if char in nodes[index]['next']:
                    child = nodes[index]['next'][char]
                    if nodes[child]['count'] > 0:
                        following.append(child)
        frontier = following
    result = 0
    for index in frontier:
        result = result + nodes[index]['end']
    return result

nodes = trie_new()
for word in ['猫咪', '猫粮', '猫咪', '狗粮', '猫', '']:
    trie_add(nodes, word)
print(trie_wildcard_count(nodes, '猫?'))
print(trie_wildcard_count(nodes, '?粮'))
print(trie_wildcard_count(nodes, ''))
```

**预期输出**

```text
3
2
1
```


</details>

### 练习 2

求当前所有词共同前缀的长度，重复次数不改变答案；无词返回 None，存在空词则返回 0。测试“算法”“算法题”“算法”，然后加入空词。

<details>
<summary>提示</summary>

记根的 count 为 total。只要当前结点没有结束词，且有某个孩子 count 等于 total，所有词就仍沿这个孩子同行。

</details>

<details>
<summary>解答与检查</summary>

首先返回 2，加入空词后返回 0，空词库返回 None。正计数孩子之和不超过 total，所以 count 等于 total 的孩子最多一个；走到结束词或分叉时必须停止。代码扫描当前结点的所有历史孩子，故不能仅凭返回长度声称 O(共同前缀长度)：许多零计数旧边也会被访问。保守期望时间 O(N+1)，额外空间 O(1)，N 为历史结点数。

**完整程序**

```python
def trie_new():
    return [{'next': {}, 'end': 0, 'count': 0}]

def trie_add(nodes, word):
    current = 0
    nodes[current]['count'] = nodes[current]['count'] + 1
    for char in word:
        if char not in nodes[current]['next']:
            nodes[current]['next'][char] = len(nodes)
            nodes.append({'next': {}, 'end': 0, 'count': 0})
        current = nodes[current]['next'][char]
        nodes[current]['count'] = nodes[current]['count'] + 1
    nodes[current]['end'] = nodes[current]['end'] + 1

def trie_common_prefix_length(nodes):
    total = nodes[0]['count']
    if total == 0:
        return None
    current = 0
    length = 0
    while nodes[current]['end'] == 0:
        chosen = None
        for char in nodes[current]['next']:
            child = nodes[current]['next'][char]
            if nodes[child]['count'] == total:
                chosen = child
        if chosen is None:
            return length
        current = chosen
        length = length + 1
    return length

nodes = trie_new()
for word in ['算法', '算法题', '算法']:
    trie_add(nodes, word)
print(trie_common_prefix_length(nodes))
trie_add(nodes, '')
print(trie_common_prefix_length(nodes))
print(trie_common_prefix_length(trie_new()))
```

**预期输出**

```text
2
0
None
```


</details>

### 练习 3

按首次出现的完整词顺序去重，保留空词并区分不同码点形式。处理 \[图,空词,图论,图,空词,树\]；说明为什么不能直接枚举 Trie 得到要求的顺序。

<details>
<summary>提示</summary>

依次读取原列表，只有精确次数为零时才插入并立即追加到结果；共享前缀不算完整词重复。

</details>

<details>
<summary>解答与检查</summary>

返回 \[图,空词,图论,树\]，每项仍是字符串。枚举 Trie 的次序由边创建和深度优先决定，不能代替原列表首次出现次序。逐项查询确保已经报告的词都被跳过，未报告的词立即输出，因此完整且稳定。设输入词数 K、总码点数 S，期望时间 O(S+K+1)，新树和结果额外空间 O(S+K+1)，字符串本身可共享；两种 é 形式作为不同词各保留一次。

**完整程序**

```python
def trie_new():
    return [{'next': {}, 'end': 0, 'count': 0}]

def trie_add(nodes, word):
    current = 0
    nodes[current]['count'] = nodes[current]['count'] + 1
    for char in word:
        if char not in nodes[current]['next']:
            nodes[current]['next'][char] = len(nodes)
            nodes.append({'next': {}, 'end': 0, 'count': 0})
        current = nodes[current]['next'][char]
        nodes[current]['count'] = nodes[current]['count'] + 1
    nodes[current]['end'] = nodes[current]['end'] + 1

def trie_locate(nodes, prefix):
    current = 0
    for char in prefix:
        if char not in nodes[current]['next']:
            return None
        current = nodes[current]['next'][char]
    return current

def trie_exact(nodes, word):
    current = trie_locate(nodes, word)
    if current is None:
        return 0
    return nodes[current]['end']

def trie_prefix_count(nodes, prefix):
    current = trie_locate(nodes, prefix)
    if current is None:
        return 0
    return nodes[current]['count']

def unique_words(words):
    nodes = trie_new()
    result = []
    for word in words:
        if trie_exact(nodes, word) == 0:
            trie_add(nodes, word)
            result.append(word)
    return result

print(unique_words(['图', '', '图论', '图', '', '树']))
print(unique_words(['é', 'é', 'é']))
```

**预期输出**

```text
['图', '', '图论', '树']
['é', 'é']
```


</details>

<a id="pitfalls"></a>

## 容易混淆的地方

- **有路径就认定完整词存在，或把根下标 0 当作查找失败。** 精确存在看 end，前缀次数看 count；定位失败明确用 None。
- **删除时只减少终点，或者把仍有后代的前缀整段删掉。** 先确认 end 为正，再让根和整条路径同时减一次，保留不变式。
- **默认枚举是字符排序或完整词的插入顺序。** 本实现采用结点先于孩子、边首次创建顺序的深度优先次序；稳定去重另按输入流输出。
- **把字典边的期望时间写成无条件最坏时间，并忽略路径字符串复制。** 哈希操作、计数整数、旧结点与输出构造分别计成本，返回列表的枚举不等于一次精确查询。

<a id="self-check"></a>

## 离开这一章前

- [ ] 每次插入删除后核对所有结点的 count=end+孩子 count 之和。
- [ ] 构造只存长词而不存短前缀的输入，比较三种查询的答案。
- [ ] 删除最后一次词后再插入，检查结点数与边顺序。
- [ ] 找一个 Trie 枚举顺序与完整词首次出现顺序不同的例子。

## 本章边界

- 使用 Python 字典边、可变结点列表和保留旧结点的删除方式，未实现路径压缩、结点回收、持久化或并发更新。
- 只按原始码点保存词，不做大小写折叠、归一化、字形簇处理和语言排序。
- 单字符通配仅为入门练习，不等同于正则表达式；多模式自动机、后缀结构及词频排名仍待后续章节。

## 选题来源与覆盖

来源含学生报告时，仅将其作为选题线索；具体机制仍需结合后续实验或权威资料核对。

- [大一小学期/Week\_3-Python/docs/readme.md](https://github.com/PKUanonym/REKCARC-TSC-UHT/blob/37cd19f7a9fb80dc846a7016b3fd482ed5fe7cc0/%E5%A4%A7%E4%B8%80%E5%B0%8F%E5%AD%A6%E6%9C%9F/Week_3-Python/docs/readme.md)（已提取可读文本，固定版本 37cd19f7a9fb）
- 主题 1：Python 基础语法的外部学习入口；位置：第 41–80 行。
- 主题 2：从基础语法到工具与应用的建议阅读顺序；位置：第 121–160 行。

## 参考资料与规则核对

上游入口用于确定学习方向；下面的参考资料用于核对语言语义、数据结构或算法分析规则，例题和练习由本项目重新设计。

- [Princeton Algorithms：Tries](https://algs4.cs.princeton.edu/52trie/)：核对共享前缀、最长键前缀、通配与延迟删除的概念。页面直读受限，本轮通过可读取的同网址索引全文核对；没有移植 Java 程序、题目或数据。计数不变式和下标结构由本项目自定。
- [Python 3.11：dict 映射](https://docs.python.org/3.11/library/stdtypes.html#mapping-types-dict)：核对键成员查询、插入顺序及独立字典语义；本章明确区分边创建顺序、字符排序与完整词首次出现顺序。

**继续学习**：先独立完成自测，再记录仍需回读的步骤。

[上一章：复用已经相等的部分：字符串匹配与 KMP](31-string-matching.md) · [下一章：复用区间信息：前缀和、双指针与滑动窗口](33-prefix-window.md)

[教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [哈希表与图练习指引](../hash-graphs-practice.md) · [拓扑排序与带权图练习指引](../weighted-graphs-practice.md) · [记录自己的学习](../learning-log-template.md)
