# 合并区间摘要：线段树与延迟更新

[返回教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [哈希表与图练习指引](../hash-graphs-practice.md) · [拓扑排序与带权图练习指引](../weighted-graphs-practice.md)

[上一章：动态维护前缀：树状数组与频次排名](35-fenwick-tree.md)

[学习目标](#objectives) · [需要的基础](#prerequisites) · [例题](#examples) · [练习](#practice) · [自测](#self-check)

状态：**AI 初稿，可开始试学**。生成模型：Codex 当前会话（未记录具体模型型号）。

本章围绕资料中识别到的知识点重新编写；讲解、数值模型、例题与练习为 AI 原创组织，不是原课程题目或答案。主题出处只说明选题关联，不证明全部推导已经正确。

树状数组适合用加法拆解前缀；如果想同时维护区间和、最小值、长度，或者让一整段统一增加，便需要更明确地组织区间。线段树把连续范围分成左右两半，每个结点只保存一份可合并摘要。本章从摘要含义出发实现建树、点赋值与半开查询，再为范围加法引入延迟标记，说明什么时候可以整段处理、什么时候必须把更新交给孩子。

<a id="objectives"></a>

## 学完要能做到

- 为区间摘要定义结合运算和空区间单位元，区分结合性与交换性。
- 用补齐叶子的数组建树，完成点赋值和保持顺序的范围查询。
- 推导区间增加对总和的影响，维护延迟标记与下推不变量。
- 用摘要剪枝、最大子段和及字符串拼接检验结构的能力与成本边界。

<a id="prerequisites"></a>

## 需要的基础

- 第 13–16 章的递归、分治与树形结构。
- 第 29、33 章的连续子段、前缀和与半开边界。
- 第 35 章的动态查询接口、输入独立性和复杂度分析。

## 可合并摘要：结合性和单位元分别解决什么问题

把一段整数概括为三个字段：sum 是总和，minimum 是最小值，length 是实际元素数。两个相邻区间合并时，总和相加、长度相加、最小值取两者较小值。摘要保存的是区间的性质，不必保留每个元素；只要左右摘要充分，父区间就能用常数次操作恢复这些性质。

空区间用 sum=0、minimum=None、length=0 表示。None 的含义是“没有最小值”，不能当作数参与比较；合并时跳过没有值的一侧。若把空最小值写成 0，那么全是正数的区间会被错误压到零。单位元要求空摘要与任何摘要合并后，内容保持原摘要，这也让补齐叶子和空查询有统一处理。

合并满足结合律：三个相邻区间无论先合并哪两段，总和、最小值、元素数都等于同一个拼接区间的性质。线段树因此可以改变括号位置。结合性不意味着可以交换左右；本例的和与最小值碰巧允许交换，但字符串拼接、矩阵相乘等摘要不允许，后面的查询仍会保持原始顺序。

函数每次返回新字典，包括某侧为空时也不直接返回原字典，避免调用者修改结果后连带改变树内结点。合并不修改输入摘要。按单位整数成本，一个摘要与合并都为 O(1)；若字段本身是长字符串或大对象，必须重新分析，不能只数树层数。本章先用固定三个字段建立可核对的结构，最后再用拼接练习揭示这项成本前提。

**完整程序**

```python
def stats_empty():
    return {'sum': 0, 'minimum': None, 'length': 0}

def stats_leaf(value):
    return {'sum': value, 'minimum': value, 'length': 1}

def stats_merge(left, right):
    smallest = left['minimum']
    if smallest is None or (right['minimum'] is not None and right['minimum'] < smallest):
        smallest = right['minimum']
    return {'sum': left['sum'] + right['sum'], 'minimum': smallest, 'length': left['length'] + right['length']}

left = stats_leaf(5)
print(stats_merge(left, stats_leaf(-2)))
print(stats_merge(stats_empty(), left))
print(stats_merge(stats_empty(), stats_empty()))
```

**预期输出**

```text
{'sum': 3, 'minimum': -2, 'length': 2}
{'sum': 5, 'minimum': 5, 'length': 1}
{'sum': 0, 'minimum': None, 'length': 0}
```


选题关联：来源主题 1（文末列出）。

## 补齐叶子：从连续元素向上构建摘要树

令 base 为不小于 n 的最小二次幂，空输入也取 base=1。树根放在数组下标 1，结点 i 的左右孩子放在 2i 与 2i+1；叶子从 base 开始，外部位置 j 对应 base+j。真实元素之后的补齐叶子保存空摘要，不参与长度或最小值计算。

先为各叶子写入单元素摘要，再从 base−1 逆序到 1 合并左右孩子。因为孩子编号比父亲大，倒序时它们已经准备好。每个内部结点的含义是其叶子覆盖范围内的摘要；对补齐区间而言，真实元素数可以小于该范围的槽数，这正是 length 与树形区间宽度需要区分的地方。

输入 \[5,2,7\] 需要 base=4，叶子槽 4、5、6 放三个值，槽 7 放空摘要，根得到 sum=14、minimum=2、length=3。第四个叶子不是值为零的真实元素。空输入的根则直接是空摘要，后续 \[0,0) 查询仍有定义，但不存在可修改的位置。

创建结点时逐次调用 stats\_empty，不能用一个可变字典乘以列表长度，否则很多位置会指向同一对象。叶子也只复制整数值，原列表后来被修改不会暗中改变树。对 n 至少为 1，base 小于 2n，整棵数组不到 4n 个槽；连同空输入情况，建树和空间均为 O(n+1)。本实现每个结点只合并一次，比为每个位置从根单独插入更直接，也便于逐结点对照真实区间检查。

**完整程序**

```python
def stats_empty():
    return {'sum': 0, 'minimum': None, 'length': 0}

def stats_leaf(value):
    return {'sum': value, 'minimum': value, 'length': 1}

def stats_merge(left, right):
    smallest = left['minimum']
    if smallest is None or (right['minimum'] is not None and right['minimum'] < smallest):
        smallest = right['minimum']
    return {'sum': left['sum'] + right['sum'], 'minimum': smallest, 'length': left['length'] + right['length']}

def segment_build(values):
    base = 1
    while base < len(values):
        base = base * 2
    nodes = []
    for i in range(2 * base):
        nodes.append(stats_empty())
    for i in range(len(values)):
        nodes[base + i] = stats_leaf(values[i])
    for i in range(base - 1, 0, -1):
        nodes[i] = stats_merge(nodes[2 * i], nodes[2 * i + 1])
    return {'size': len(values), 'base': base, 'nodes': nodes}

state = segment_build([5, 2, 7])
print(state['base'], state['nodes'][1])
print(state['nodes'][7])
print(segment_build([])['nodes'][1])
```

**预期输出**

```text
4 {'sum': 14, 'minimum': 2, 'length': 3}
{'sum': 0, 'minimum': None, 'length': 0}
{'sum': 0, 'minimum': None, 'length': 0}
```


选题关联：来源主题 1（文末列出）。

## 点赋值：只重算从叶子到根的一条路径

要把位置 index 改为 value，先找到叶子 base+index，替换成新的单元素摘要。随后不断把编号整除 2，重新合并当前父结点的两个孩子，直到根处理完毕。没有使用旧值计算差量，因此即使维护最小值，也不需要“减去旧最小值”这种没有依据的逆操作。

为什么其他结点无需更新？不包含该叶子的区间没有元素变化，摘要保持有效；包含它的结点恰好是它的全部祖先。沿路径从下到上处理时，发生变化的孩子已经更新，另一个孩子仍正确，所以重新合并得到正确父摘要。由此逐层恢复整棵树的不变量。

示例 \[5,2,7\] 把位置 1 设为 9，根变为总和 21、最小值 5、长度 3。原来最小值是被修改的 2，必须从两个孩子重新选择；若只对根的最小值加 7，就会得到错误结果。重复赋成同一值则保持同样内容，赋值的语义与范围加法不同。

index 必须在 0 到 n−1 之间，非法返回 False 且不改变任何槽；成功返回 True。补齐叶子不开放修改，空结构没有合法点。状态应来自 segment\_build，并通过本章接口操作，不接受调用者任意篡改树的编号和摘要。路径长 O(log(n+1)+1)，每层合并常数字段，所以赋值同阶时间；迭代过程只保留一个编号，辅助空间 O(1)。保存整棵树仍需 O(n+1)，不能把操作工作空间当作整个结构的存储成本。

**完整程序**

```python
def stats_empty():
    return {'sum': 0, 'minimum': None, 'length': 0}

def stats_leaf(value):
    return {'sum': value, 'minimum': value, 'length': 1}

def stats_merge(left, right):
    smallest = left['minimum']
    if smallest is None or (right['minimum'] is not None and right['minimum'] < smallest):
        smallest = right['minimum']
    return {'sum': left['sum'] + right['sum'], 'minimum': smallest, 'length': left['length'] + right['length']}

def segment_build(values):
    base = 1
    while base < len(values):
        base = base * 2
    nodes = []
    for i in range(2 * base):
        nodes.append(stats_empty())
    for i in range(len(values)):
        nodes[base + i] = stats_leaf(values[i])
    for i in range(base - 1, 0, -1):
        nodes[i] = stats_merge(nodes[2 * i], nodes[2 * i + 1])
    return {'size': len(values), 'base': base, 'nodes': nodes}

def segment_set(state, index, value):
    if index < 0 or index >= state['size']:
        return False
    i = state['base'] + index
    state['nodes'][i] = stats_leaf(value)
    i = i // 2
    while i > 0:
        state['nodes'][i] = stats_merge(state['nodes'][2 * i], state['nodes'][2 * i + 1])
        i = i // 2
    return True

state = segment_build([5, 2, 7])
print(segment_set(state, 1, 9), state['nodes'][1])
print(segment_set(state, 3, -8), state['nodes'][1])
```

**预期输出**

```text
True {'sum': 21, 'minimum': 5, 'length': 3}
False {'sum': 21, 'minimum': 5, 'length': 3}
```


选题关联：来源主题 1（文末列出）。

## 半开区间查询：两端累积并保留拼接顺序

查询 \[start,stop) 时，先把两端移到叶子层。left 若为奇数，说明它是某父结点的右孩子，其左兄弟不在待查范围，必须单独取走 left，再让它加一。right 若为奇数，说明排除边界落在一个右孩子处，应先减一，取走紧邻左边的那块。剩余部分的两端都对齐，可以一起整除 2 上移。

程序维护 before 与 after 两份摘要。左边取出的块越来越靠右，应接在 before 后面；右边取出的块却越来越靠左，应接在 after 前面。最后合并 before、after，得到原区间顺序。每次已经取走的块与尚待处理的中间范围互不重叠，它们按顺序拼接始终是原始查询区间。

每层最多取两块，上移后范围约缩半，因此访问 O(log(n+1)+1) 个结点。对于 \[5,2,7,−1,4\] 的 \[1,4)，摘要为总和 8、最小值 −1、长度 3。空范围返回全新空摘要；非法负边界、倒置或超过 size 返回 None。终点允许等于 n，不允许用 base 把补齐槽冒充合法数据。

当前三字段摘要具有交换性，即使把右侧顺序写反，少量求和测试也可能通过。练习中的字符串拼接专门检验这一点。segment\_query 不修改树，而且返回字典与内部槽独立，修改结果不会污染下一次查询。单位字段成本下时间 O(log(n+1)+1)，迭代工作空间 O(1)，输出也是常数大小；如果摘要本身可变长，就必须把复制和合并成本一起乘进去。

**完整程序**

```python
def stats_empty():
    return {'sum': 0, 'minimum': None, 'length': 0}

def stats_leaf(value):
    return {'sum': value, 'minimum': value, 'length': 1}

def stats_merge(left, right):
    smallest = left['minimum']
    if smallest is None or (right['minimum'] is not None and right['minimum'] < smallest):
        smallest = right['minimum']
    return {'sum': left['sum'] + right['sum'], 'minimum': smallest, 'length': left['length'] + right['length']}

def segment_build(values):
    base = 1
    while base < len(values):
        base = base * 2
    nodes = []
    for i in range(2 * base):
        nodes.append(stats_empty())
    for i in range(len(values)):
        nodes[base + i] = stats_leaf(values[i])
    for i in range(base - 1, 0, -1):
        nodes[i] = stats_merge(nodes[2 * i], nodes[2 * i + 1])
    return {'size': len(values), 'base': base, 'nodes': nodes}

def segment_query(state, start, stop):
    if start < 0 or stop < start or stop > state['size']:
        return None
    left = start + state['base']
    right = stop + state['base']
    before = stats_empty()
    after = stats_empty()
    while left < right:
        if left % 2 == 1:
            before = stats_merge(before, state['nodes'][left])
            left = left + 1
        if right % 2 == 1:
            right = right - 1
            after = stats_merge(state['nodes'][right], after)
        left = left // 2
        right = right // 2
    return stats_merge(before, after)

state = segment_build([5, 2, 7, -1, 4])
print(segment_query(state, 1, 4))
print(segment_query(state, 3, 3))
print(segment_query(state, 4, 6))
```

**预期输出**

```text
{'sum': 8, 'minimum': -1, 'length': 3}
{'sum': 0, 'minimum': None, 'length': 0}
None
```


选题关联：来源主题 1（文末列出）。

## 范围增加与范围和：把尚未交给孩子的工作记下来

本节另建递归线段树，只维护区间和及加法标记，不与前面的三字段结构混用。结点代表真实区间 \[low,high)。整段增加 delta 时，总和增加 (high−low)×delta；同时把 delta 累加到 add\[node\]，表示这次增加已计入本结点，却尚未交给孩子。整段命中时可以立即停止下降。

若更新或查询只覆盖一部分，就先下推：把父标记分别应用到两个孩子，再清父标记。孩子的总和按各自长度增加，孩子已有标记也要叠加。对于内部结点，在未下推时，父总和等于两个孩子总和再加父标记乘区间长度；下推后父标记为零，父总和恰等于孩子总和之和。它并不要求所有叶子随时保存最新显式值。

更新完成部分递归后，要把两个孩子的新和相加写回父结点。查询无交集返回零，完整覆盖直接读总和，部分覆盖先下推再查询两侧。因此查询可能改变内部标记的分布，却不改变逻辑数组的值；不能以“查询函数”之名断言结构字节完全不变。叶子没有孩子，标记可留在叶子上。

公开接口先检查零起点半开范围，非法更新返回 False，非法查询返回 None；合法空更新返回 True 且不递归，空查询返回 0。空输入也由这条规则处理。建树时间和空间 O(n+1)，每次范围操作 O(log(n+1)+1)：每层只有至多两条边界路径继续部分下降，完全覆盖的兄弟立即停止。递归栈 O(log(n+1)+1)。本标签只表达加法，若加入整段赋值，覆盖次序和标签组合必须重新定义，不能直接沿用累加。

**完整程序**

```python
def lazy_build_node(state, node, low, high, values):
    if high - low == 1:
        state['sum'][node] = values[low]
    else:
        middle = (low + high) // 2
        lazy_build_node(state, 2 * node, low, middle, values)
        lazy_build_node(state, 2 * node + 1, middle, high, values)
        state['sum'][node] = state['sum'][2 * node] + state['sum'][2 * node + 1]

def lazy_new(values):
    size = len(values)
    state = {'size': size, 'sum': [0] * (4 * size + 4), 'add': [0] * (4 * size + 4)}
    if size > 0:
        lazy_build_node(state, 1, 0, size, values)
    return state

def lazy_apply(state, node, low, high, delta):
    state['sum'][node] = state['sum'][node] + (high - low) * delta
    state['add'][node] = state['add'][node] + delta

def lazy_push(state, node, low, high):
    delta = state['add'][node]
    if high - low > 1 and delta != 0:
        middle = (low + high) // 2
        lazy_apply(state, 2 * node, low, middle, delta)
        lazy_apply(state, 2 * node + 1, middle, high, delta)
        state['add'][node] = 0

def lazy_add_node(state, node, low, high, start, stop, delta):
    if stop <= low or high <= start:
        return
    if start <= low and high <= stop:
        lazy_apply(state, node, low, high, delta)
    else:
        lazy_push(state, node, low, high)
        middle = (low + high) // 2
        lazy_add_node(state, 2 * node, low, middle, start, stop, delta)
        lazy_add_node(state, 2 * node + 1, middle, high, start, stop, delta)
        state['sum'][node] = state['sum'][2 * node] + state['sum'][2 * node + 1]

def lazy_add(state, start, stop, delta):
    if start < 0 or stop < start or stop > state['size']:
        return False
    if start < stop:
        lazy_add_node(state, 1, 0, state['size'], start, stop, delta)
    return True

def lazy_sum_node(state, node, low, high, start, stop):
    if stop <= low or high <= start:
        return 0
    if start <= low and high <= stop:
        return state['sum'][node]
    lazy_push(state, node, low, high)
    middle = (low + high) // 2
    return lazy_sum_node(state, 2 * node, low, middle, start, stop) + lazy_sum_node(state, 2 * node + 1, middle, high, start, stop)

def lazy_sum(state, start, stop):
    if start < 0 or stop < start or stop > state['size']:
        return None
    if start == stop:
        return 0
    return lazy_sum_node(state, 1, 0, state['size'], start, stop)

state = lazy_new([2, -1, 4, 0])
lazy_add(state, 0, 4, 3)
lazy_add(state, 1, 3, -2)
print(lazy_sum(state, 0, 4), lazy_sum(state, 1, 3))
print(lazy_add(state, 2, 2, 8), lazy_sum(state, 2, 2))
print(lazy_add(state, -1, 2, 9), lazy_sum(state, 0, 5))
```

**预期输出**

```text
13 5
True 0
False None
```


选题关联：来源主题 1（文末列出）。

<a id="examples"></a>

## 跟着做：原创例题

### 例题 1

为 \[5,2,7\] 建立三字段线段树，查询整段；把位置 1 设为 9 后，查询单点 \[1,2) 和空段 \[3,3)。解释补齐单位元的重要性。

1. 三个元素补齐到四个叶子，第四个存 minimum=None、length=0，不是一个额外的零。
2. 整段摘要为 sum=14、minimum=2、length=3，补齐部分没有改变真实最小值。
3. 修改后单点摘要为 sum=9、minimum=9、length=1，父路径已同步重算。
4. 空段返回 sum=0、minimum=None、length=0；输入列表仍保留初始值。

**结果与核对**

示例依次检验正数最小值、单点赋值、空单位元与输入独立性。如果补齐最小值误设零，最初查询就会暴露错误。建树 O(n+1)，常数次更新查询合计 O(log(n+1)+1)，整段工作以建树的 O(n+1) 为主。返回字典也应与树内槽分离，测试会主动修改返回结果后再查询，核对没有别名污染。

**完整程序**

```python
def stats_empty():
    return {'sum': 0, 'minimum': None, 'length': 0}

def stats_leaf(value):
    return {'sum': value, 'minimum': value, 'length': 1}

def stats_merge(left, right):
    smallest = left['minimum']
    if smallest is None or (right['minimum'] is not None and right['minimum'] < smallest):
        smallest = right['minimum']
    return {'sum': left['sum'] + right['sum'], 'minimum': smallest, 'length': left['length'] + right['length']}

def segment_build(values):
    base = 1
    while base < len(values):
        base = base * 2
    nodes = []
    for i in range(2 * base):
        nodes.append(stats_empty())
    for i in range(len(values)):
        nodes[base + i] = stats_leaf(values[i])
    for i in range(base - 1, 0, -1):
        nodes[i] = stats_merge(nodes[2 * i], nodes[2 * i + 1])
    return {'size': len(values), 'base': base, 'nodes': nodes}

def segment_set(state, index, value):
    if index < 0 or index >= state['size']:
        return False
    i = state['base'] + index
    state['nodes'][i] = stats_leaf(value)
    i = i // 2
    while i > 0:
        state['nodes'][i] = stats_merge(state['nodes'][2 * i], state['nodes'][2 * i + 1])
        i = i // 2
    return True

def segment_query(state, start, stop):
    if start < 0 or stop < start or stop > state['size']:
        return None
    left = start + state['base']
    right = stop + state['base']
    before = stats_empty()
    after = stats_empty()
    while left < right:
        if left % 2 == 1:
            before = stats_merge(before, state['nodes'][left])
            left = left + 1
        if right % 2 == 1:
            right = right - 1
            after = stats_merge(state['nodes'][right], after)
        left = left // 2
        right = right // 2
    return stats_merge(before, after)

values = [5, 2, 7]
state = segment_build(values)
print(segment_query(state, 0, 3))
segment_set(state, 1, 9)
print(segment_query(state, 1, 2))
print(segment_query(state, 3, 3))
print(values)
```

**预期输出**

```text
{'sum': 14, 'minimum': 2, 'length': 3}
{'sum': 9, 'minimum': 9, 'length': 1}
{'sum': 0, 'minimum': None, 'length': 0}
[5, 2, 7]
```


### 例题 2

对 \[2,−1,4,0\] 整段加 3，再查询 \[0,1)。跟踪根及两个孩子的总和，说明查询为何可以下推而不改变答案。

1. 初始根和为 5，左右孩子区间 \[0,2)、\[2,4) 的和分别为 1、4。
2. 整段增加后根和为 17、标记为 3，孩子和暂仍是 1、4；逻辑列表已是 \[5,2,7,3\]。
3. 查询单点必须下降，根标记传给两个长度为 2 的孩子，各增加 6，得到 7、10，根标记归零。
4. 继续下推左孩子后读到第一项 5。根和仍为 17，与两个孩子和之和一致。

**结果与核对**

程序先打印 17、3、1、4，查询结果为 5，再打印 17、0、7、10。前后内部表示不同，逻辑数组始终相同。若只把标记传给查询命中的左孩子却清掉父标记，右侧更新就会永久丢失；下推必须同时处理两个孩子。反复查询、整段更新后再做局部负增量、查询后再次更新，都是独立数组模型需要覆盖的顺序。

**完整程序**

```python
def lazy_build_node(state, node, low, high, values):
    if high - low == 1:
        state['sum'][node] = values[low]
    else:
        middle = (low + high) // 2
        lazy_build_node(state, 2 * node, low, middle, values)
        lazy_build_node(state, 2 * node + 1, middle, high, values)
        state['sum'][node] = state['sum'][2 * node] + state['sum'][2 * node + 1]

def lazy_new(values):
    size = len(values)
    state = {'size': size, 'sum': [0] * (4 * size + 4), 'add': [0] * (4 * size + 4)}
    if size > 0:
        lazy_build_node(state, 1, 0, size, values)
    return state

def lazy_apply(state, node, low, high, delta):
    state['sum'][node] = state['sum'][node] + (high - low) * delta
    state['add'][node] = state['add'][node] + delta

def lazy_push(state, node, low, high):
    delta = state['add'][node]
    if high - low > 1 and delta != 0:
        middle = (low + high) // 2
        lazy_apply(state, 2 * node, low, middle, delta)
        lazy_apply(state, 2 * node + 1, middle, high, delta)
        state['add'][node] = 0

def lazy_add_node(state, node, low, high, start, stop, delta):
    if stop <= low or high <= start:
        return
    if start <= low and high <= stop:
        lazy_apply(state, node, low, high, delta)
    else:
        lazy_push(state, node, low, high)
        middle = (low + high) // 2
        lazy_add_node(state, 2 * node, low, middle, start, stop, delta)
        lazy_add_node(state, 2 * node + 1, middle, high, start, stop, delta)
        state['sum'][node] = state['sum'][2 * node] + state['sum'][2 * node + 1]

def lazy_add(state, start, stop, delta):
    if start < 0 or stop < start or stop > state['size']:
        return False
    if start < stop:
        lazy_add_node(state, 1, 0, state['size'], start, stop, delta)
    return True

def lazy_sum_node(state, node, low, high, start, stop):
    if stop <= low or high <= start:
        return 0
    if start <= low and high <= stop:
        return state['sum'][node]
    lazy_push(state, node, low, high)
    middle = (low + high) // 2
    return lazy_sum_node(state, 2 * node, low, middle, start, stop) + lazy_sum_node(state, 2 * node + 1, middle, high, start, stop)

def lazy_sum(state, start, stop):
    if start < 0 or stop < start or stop > state['size']:
        return None
    if start == stop:
        return 0
    return lazy_sum_node(state, 1, 0, state['size'], start, stop)

state = lazy_new([2, -1, 4, 0])
lazy_add(state, 0, 4, 3)
print(state['sum'][1], state['add'][1], state['sum'][2], state['sum'][3])
print(lazy_sum(state, 0, 1))
print(state['sum'][1], state['add'][1], state['sum'][2], state['sum'][3])
```

**预期输出**

```text
17 3 1 4
5
17 0 7 10
```


<a id="practice"></a>

## 自己做：先完成再看解答

### 练习 1

利用三字段树，在给定半开范围内寻找第一个值不大于 threshold 的位置。求 \[7,4,6,2,4\] 在 \[1,5) 和 \[2,5) 中第一个不超过 4 的位置。

<details>
<summary>提示</summary>

无交集、空摘要或结点最小值大于阈值，都可以直接排除。未被排除时先查左孩子，左边无答案再查右边。

</details>

<details>
<summary>解答与检查</summary>

答案分别为 1 和 3。完整区间最小值过大就证明整块无解；先左后右保证最小下标。空范围、非法范围和正常无解均返回 None，本接口不进一步区分。只有至多两条查询边界路径和首个可行块内的一条下降路径需要展开，其余完整失败块立即剪掉，所以时间 O(log(n+1)+1)，递归辅助空间同阶；调用前的建树另需 O(n+1)。不能先把每个叶子取出来再声称对数查询。

**完整程序**

```python
def stats_empty():
    return {'sum': 0, 'minimum': None, 'length': 0}

def stats_leaf(value):
    return {'sum': value, 'minimum': value, 'length': 1}

def stats_merge(left, right):
    smallest = left['minimum']
    if smallest is None or (right['minimum'] is not None and right['minimum'] < smallest):
        smallest = right['minimum']
    return {'sum': left['sum'] + right['sum'], 'minimum': smallest, 'length': left['length'] + right['length']}

def segment_build(values):
    base = 1
    while base < len(values):
        base = base * 2
    nodes = []
    for i in range(2 * base):
        nodes.append(stats_empty())
    for i in range(len(values)):
        nodes[base + i] = stats_leaf(values[i])
    for i in range(base - 1, 0, -1):
        nodes[i] = stats_merge(nodes[2 * i], nodes[2 * i + 1])
    return {'size': len(values), 'base': base, 'nodes': nodes}

def first_at_most_node(state, node, low, high, start, stop, threshold):
    smallest = state['nodes'][node]['minimum']
    if high <= start or stop <= low or smallest is None or smallest > threshold:
        return None
    if high - low == 1:
        return low
    middle = (low + high) // 2
    answer = first_at_most_node(state, 2 * node, low, middle, start, stop, threshold)
    if answer is None:
        answer = first_at_most_node(state, 2 * node + 1, middle, high, start, stop, threshold)
    return answer

def first_at_most(state, start, stop, threshold):
    if start < 0 or stop < start or stop > state['size'] or start == stop:
        return None
    return first_at_most_node(state, 1, 0, state['base'], start, stop, threshold)

state = segment_build([7, 4, 6, 2, 4])
print(first_at_most(state, 1, 5, 4))
print(first_at_most(state, 2, 5, 4))
print(first_at_most(state, 0, 3, 1))
```

**预期输出**

```text
1
3
None
```


</details>

### 练习 2

为最大连续子段和设计摘要，允许选空段，因此全负数答案为零。保存 sum、最大前缀和 prefix、最大后缀和 suffix、最大子段和 best，求 \[2,−3,4,−1,2\]。

<details>
<summary>提示</summary>

跨越分界的子段一定由左段的后缀和右段的前缀组成。最大前缀要么留在左段，要么包含整个左段并接右前缀；后缀对称。

</details>

<details>
<summary>解答与检查</summary>

根摘要为 sum=4、prefix=4、suffix=5、best=5。best 取左侧最优、右侧最优、左后缀加右前缀三者最大；这三种位置关系覆盖全部子段。空摘要四项为零，单元素负数的总和仍为负，其他三项为零，不能把 sum 也截为零。各字段表达同一区间的确定性质，所以任意相邻合并括号得到相同结果。程序只实现全区间摘要构建与合并，O(n+1) 时间空间，未额外提供这个摘要的动态修改接口；穷举所有连续区间独立核对。

**完整程序**

```python
def maxsum_empty():
    return {'sum': 0, 'prefix': 0, 'suffix': 0, 'best': 0}

def maxsum_merge(left, right):
    prefix = left['prefix']
    if left['sum'] + right['prefix'] > prefix:
        prefix = left['sum'] + right['prefix']
    suffix = right['suffix']
    if right['sum'] + left['suffix'] > suffix:
        suffix = right['sum'] + left['suffix']
    best = left['best']
    if right['best'] > best:
        best = right['best']
    if left['suffix'] + right['prefix'] > best:
        best = left['suffix'] + right['prefix']
    return {'sum': left['sum'] + right['sum'], 'prefix': prefix, 'suffix': suffix, 'best': best}

def maxsum_summary(values):
    base = 1
    while base < len(values):
        base = base * 2
    nodes = []
    for i in range(2 * base):
        nodes.append(maxsum_empty())
    for i in range(len(values)):
        best = 0
        if values[i] > best:
            best = values[i]
        nodes[base + i] = {'sum': values[i], 'prefix': best, 'suffix': best, 'best': best}
    for i in range(base - 1, 0, -1):
        nodes[i] = maxsum_merge(nodes[2 * i], nodes[2 * i + 1])
    return nodes[1].copy()

print(maxsum_summary([2, -3, 4, -1, 2]))
print(maxsum_summary([-4, -1]))
print(maxsum_summary([]))
```

**预期输出**

```text
{'sum': 4, 'prefix': 4, 'suffix': 5, 'best': 5}
{'sum': -5, 'prefix': 0, 'suffix': 0, 'best': 0}
{'sum': 0, 'prefix': 0, 'suffix': 0, 'best': 0}
```


</details>

### 练习 3

把每个叶子改成字符串片段，合并为按顺序拼接。求 \[a,b,c,d,e,f\] 的 \[1,5)，并说明为什么不能照抄常数摘要的时间结论。

<details>
<summary>提示</summary>

左侧块接到 before 后，右侧块接到 after 前；空字符串是单位元。字符串连接满足结合性，却不满足交换性。

</details>

<details>
<summary>解答与检查</summary>

结果是 bcde，不能颠倒右侧块的顺序；含空片段和 Unicode 的例子仍按列表位置查询，空范围返回空串，非法返回 None。设 n 个片段、总码点数 B，构建及存储的保守上界 O(n+B log(n+1)+1)，因为每层可能复制这些字符；一次结果长 L 的查询至多合并对数次，保守时间 O((L+1)log(n+1)+1)，工作空间 O(L+1)，已有树另计。即使访问结点很少，复制长文本也不是常数工作。

**完整程序**

```python
def concat_build(tokens):
    base = 1
    while base < len(tokens):
        base = base * 2
    nodes = [''] * (2 * base)
    for i in range(len(tokens)):
        nodes[base + i] = tokens[i]
    for i in range(base - 1, 0, -1):
        nodes[i] = nodes[2 * i] + nodes[2 * i + 1]
    return {'size': len(tokens), 'base': base, 'nodes': nodes}

def concat_query(state, start, stop):
    if start < 0 or stop < start or stop > state['size']:
        return None
    left = state['base'] + start
    right = state['base'] + stop
    before = ''
    after = ''
    while left < right:
        if left % 2 == 1:
            before = before + state['nodes'][left]
            left = left + 1
        if right % 2 == 1:
            right = right - 1
            after = state['nodes'][right] + after
        left = left // 2
        right = right // 2
    return before + after

state = concat_build(['a', 'b', 'c', 'd', 'e', 'f'])
print(concat_query(state, 1, 5))
print(concat_query(concat_build(['计', '', '算', '法']), 1, 4))
print(concat_query(state, 6, 6) == '')
print(concat_query(state, -1, 2))
```

**预期输出**

```text
bcde
算法
True
None
```


</details>

<a id="pitfalls"></a>

## 容易混淆的地方

- **把空区间的最小值设成零，或用重复引用初始化所有摘要。** 空最小值用 None 单独处理，每个可变摘要独立创建；零可以是真实数据。
- **把右边取出的块也追加到末尾，因为求和示例看不出区别。** 右侧块按从右向左发现，应前插到右累计摘要；用拼接核对非交换运算。
- **整段加只改标记不改当前和，或下推后忘记清父标记。** 本结点总和立即包含增加，标记只表示尚未传给孩子的部分；下推后父标记清零。
- **声称延迟树查询不修改内部表示，或把加法标签套到赋值。** 查询部分覆盖时也可能下推；新增更新类型必须重新证明标签组合和先后顺序。

<a id="self-check"></a>

## 离开这一章前

- [ ] 为三个正数画出四叶子树，标出补齐叶子的 length 与 minimum。
- [ ] 手算 \[1,5) 的左右取块次序，说明 right 为什么要先减一。
- [ ] 用根标记不为零的状态核对“孩子和加待传增量”等式。
- [ ] 比较查询前后树内数组，区分逻辑数据不变与物理表示不变。
- [ ] 说明最大子段和允许空段时，单个负数的四个摘要字段是什么。

## 本章边界

- 接口约定整数值、整数边界及未被外部破坏的状态；字符串练习另约定每个输入项为 str。
- 尚未实现混合赋值和增加标签、二维结构、持久化、动态开点或线程安全接口。
- 常数大小整数摘要按单位运算分析，大整数和可变长摘要需另计运算、复制及存储成本；所有章节仍保留 AI 草稿审读状态。

## 选题来源与覆盖

来源含学生报告时，仅将其作为选题线索；具体机制仍需结合后续实验或权威资料核对。

- [大一小学期/Week\_3-Python/docs/readme.md](https://github.com/PKUanonym/REKCARC-TSC-UHT/blob/37cd19f7a9fb80dc846a7016b3fd482ed5fe7cc0/%E5%A4%A7%E4%B8%80%E5%B0%8F%E5%AD%A6%E6%9C%9F/Week_3-Python/docs/readme.md)（已提取可读文本，固定版本 37cd19f7a9fb）
- 主题 1：Python 基础语法的外部学习入口；位置：第 41–80 行。
- 主题 2：从基础语法到工具与应用的建议阅读顺序；位置：第 121–160 行。

## 参考资料与规则核对

上游入口用于确定学习方向；下面的参考资料用于核对语言语义、数据结构或算法分析规则，例题和练习由本项目重新设计。

- [AtCoder Library：Segtree](https://atcoder.github.io/ac-library/production/document_en/segtree.html)：核对结合性、单位元与常数合并成本的前提；本章原创三字段摘要及半开接口，不移植库代码、竞赛题或示例。
- [AtCoder Library：Lazy Segtree](https://atcoder.github.io/ac-library/production/document_en/lazysegtree.html)：核对更新映射可组合并与摘要相容的条件；本章只推导整数范围加法，不宣称实现通用映射库。
- [Algorithms for Competitive Programming：Segment Tree](https://cp-algorithms.com/data_structures/segment_tree.html)：核对完整覆盖停止、部分覆盖下推的概念；本章自定递归半开结构、空范围与非法操作契约，并用直接数组模型核验。

**继续学习**：先独立完成自测，再记录仍需回读的步骤。

[上一章：动态维护前缀：树状数组与频次排名](35-fenwick-tree.md)

[教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [哈希表与图练习指引](../hash-graphs-practice.md) · [拓扑排序与带权图练习指引](../weighted-graphs-practice.md) · [记录自己的学习](../learning-log-template.md)
