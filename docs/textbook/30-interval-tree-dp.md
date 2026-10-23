# 按区间与子树组织依赖：区间和树形动态规划

[返回教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [哈希表与图练习指引](../hash-graphs-practice.md) · [拓扑排序与带权图练习指引](../weighted-graphs-practice.md)

[上一章：对齐两个前缀：序列动态规划与方案恢复](29-sequence-dp.md)

[学习目标](#objectives) · [需要的基础](#prerequisites) · [例题](#examples) · [练习](#practice) · [自测](#self-check)

状态：**AI 初稿，可开始试学**。生成模型：Codex 当前会话（未记录具体模型型号）。

本章围绕资料中识别到的知识点重新编写；讲解、数值模型、例题与练习为 AI 原创组织，不是原课程题目或答案。主题出处只说明选题关联，不证明全部推导已经正确。

前面的状态多按金额或前缀递增计算，但有些问题必须保留一整段区间，也有些问题由一棵树的孩子决定父结点。本章先从矩阵链的最后一次乘法找切分点，再研究只允许相邻合并的费用，最后把树上选择问题拆成选根和不选根两个状态。每个算法都明确依赖顺序、输入边界和方案含义，使用显式列表处理恢复和森林，避免把递归深度当作输入规模的隐含限制。

<a id="objectives"></a>

## 学完要能做到

- 用半开区间定义状态，推导按长度计算的切分转移。
- 恢复可实际按顺序执行的合并记录，并区分括号结构与执行顺序。
- 验证父表确实形成森林，以孩子先完成的顺序计算树形状态。
- 推导森林独立集、顶点覆盖与独立集计数，检查多根和空森林。

<a id="prerequisites"></a>

## 需要的基础

- 第 27–29 章的状态、最优子结构、平局和方案恢复。
- 第 14 章的半开区间，第 16 章的树、根、孩子与遍历。
- 第 21–22 章的队列游标与依赖顺序；第 26 章的任意两块最优合并。

## 区间状态：从最后一次矩阵乘法找切分点

先补一个成本模型。p 行 q 列矩阵乘 q 行 r 列矩阵，得到 p 行 r 列结果；通常逐格计算时，每格有 q 次标量乘法，共 pqr 次。本章只优化这个乘法次数，不计算矩阵元素，不计加法，不把次数等同运行秒数。改变括号不改变矩阵先后顺序，在精确算术模型中结果相同；浮点舍入影响另论。

用正整数列表 dimensions 表示维度，第 i 个矩阵形状为 dimensions\[i\] 行、dimensions\[i+1\] 列。n 个矩阵需要 n+1 个维度。定义 cost\[left\]\[right\] 为半开区间 \[left,right) 内矩阵按原顺序相乘的最少次数。单个矩阵已经是结果，费用为零。空链按教学约定费用为零，不把它解释为某个给定形状的单位矩阵。

长度至少为 2 时，最后一次乘法一定把区间切成 \[left,middle) 和 \[middle,right)，两边均非空。左结果形状为 dimensions\[left\] 乘 dimensions\[middle\]，右结果形状为 dimensions\[middle\] 乘 dimensions\[right\]，故新增次数为这三个数的乘积。枚举所有内部切分点，把两边最优费用与新增次数相加取最小；若某一侧不是最优，可替换而不影响结果形状，所以分类足够。

子区间都更短，按长度从 2 到 n 填表，每格的依赖已经完成。split 仅在严格改善时保存切分，平局保留最小 middle。示例维度 \[4,7,2,5\]，先乘前两矩阵花 56，再乘末矩阵花 40，共 96。完整表只读取对角线及其上方的有效区间，其他初始化槽不代表独立问题。空维度列表或非正维度返回 None；单元素维度表表示零个矩阵。时间 O((n+1)³)、空间 O((n+1)²)，按整数运算单位成本计。

**完整程序**

```python
def matrix_tables(dimensions):
    if len(dimensions) == 0:
        return None
    for dimension in dimensions:
        if dimension <= 0:
            return None
    n = len(dimensions) - 1
    cost = []
    split = []
    for i in range(n + 1):
        cost.append([0] * (n + 1))
        split.append([None] * (n + 1))
    for length in range(2, n + 1):
        for left in range(n - length + 1):
            right = left + length
            best = None
            for middle in range(left + 1, right):
                candidate = cost[left][middle] + cost[middle][right]
                candidate = candidate + dimensions[left] * dimensions[middle] * dimensions[right]
                if best is None or candidate < best:
                    best = candidate
                    split[left][right] = middle
            cost[left][right] = best
    return {"cost": cost, "split": split}

print(matrix_tables([4, 7, 2, 5])["cost"][0])
print(matrix_tables([4])["cost"])
print(matrix_tables([]))
```

**预期输出**

```text
[0, 0, 56, 96]
[[0]]
None
```


选题关联：来源主题 1（文末列出）。

## 恢复计算顺序：先完成左右两边，再合并

split 保存的是一棵括号树。若要给出可执行的乘法步骤，不能只从根向下打印：根的最后一次乘法依赖左右两边已经完成。这里返回三元列表 \[left,middle,right\]，表示把已经得到的 \[left,middle) 与 \[middle,right) 两个结果相乘。下标始终指向原矩阵区间，不随中间结果数量变化。

interval\_merges 使用栈帧 \[left,right,done\]。首次进入一个非平凡区间，先压入标记 done 为 True 的自身，再压右区间，最后压左区间。栈后进先出，实际先处理左边、再右边，最后再次弹出自身并记录合并。长度零或一不产生操作；每个真正的内部结点有两次访问，左右子区间长度严格减小。

这就是显式模拟后序恢复。给定 n 个矩阵，n 为正时恰有 n−1 次合并，空链为零次。恢复工作与输出都是 O(n+1)，最坏栈空间 O(n+1)，不使用 Python 递归。完整 matrix\_plan 仍先建立二次规模表并做三次量级计算，恢复没有降低整个算法的成本。

对 \[4,7,2,5\]，先得到记录 \[0,1,2\]，再得到 \[0,2,3\]。检查时先把每个单矩阵区间看作可用结果，每条操作必须找到恰好相邻的两段，用其结果替代；累计每步三个边界维度的乘积应为 96。这样同时检验依赖、原顺序和费用，而不只是看到一个正确数字。interval\_merges 是内部辅助函数，前提是 split 来自已经验证并填好的表；它不接受任意外部切分表，也不尝试修复非法结构。

**完整程序**

```python
def matrix_tables(dimensions):
    if len(dimensions) == 0:
        return None
    for dimension in dimensions:
        if dimension <= 0:
            return None
    n = len(dimensions) - 1
    cost = []
    split = []
    for i in range(n + 1):
        cost.append([0] * (n + 1))
        split.append([None] * (n + 1))
    for length in range(2, n + 1):
        for left in range(n - length + 1):
            right = left + length
            best = None
            for middle in range(left + 1, right):
                candidate = cost[left][middle] + cost[middle][right]
                candidate = candidate + dimensions[left] * dimensions[middle] * dimensions[right]
                if best is None or candidate < best:
                    best = candidate
                    split[left][right] = middle
            cost[left][right] = best
    return {"cost": cost, "split": split}

def interval_merges(split, n):
    operations = []
    stack = [[0, n, False]]
    while len(stack) > 0:
        frame = stack.pop()
        left = frame[0]
        right = frame[1]
        if right - left > 1:
            middle = split[left][right]
            if frame[2]:
                operations.append([left, middle, right])
            else:
                stack.append([left, right, True])
                stack.append([middle, right, False])
                stack.append([left, middle, False])
    return operations

def matrix_plan(dimensions):
    tables = matrix_tables(dimensions)
    if tables is None:
        return None
    n = len(dimensions) - 1
    return {"cost": tables["cost"][0][n],
            "merges": interval_merges(tables["split"], n)}

print(matrix_plan([4, 7, 2, 5]))
print(matrix_plan([4, 7]))
print(matrix_plan([4]))
```

**预期输出**

```text
{'cost': 96, 'merges': [[0, 1, 2], [0, 2, 3]]}
{'cost': 0, 'merges': []}
{'cost': 0, 'merges': []}
```


选题关联：来源主题 1（文末列出）。

## 只能合并相邻块：区间总和成为最后一步费用

有一排非负整数大小的块，每次只能合并当前相邻的两块，支付两块大小之和，直到剩一块。原顺序固定，因此每个中间块对应原列表的一段连续区间。第 26 章允许任意两块合并，本题增加了相邻限制，不能直接套用每次取全局最小两块的规则。

定义 cost\[left\]\[right\] 为把 \[left,right) 合成一块的最小累计费用。最后一次合并仍有一个内部切分点；两侧费用相加，再支付整个区间大小之和。这个新增费用与切分位置无关，但子区间费用不同，所以仍需枚举切分。空区间和单块费用为零；长度递增保证先算左右两侧，平局保留最小切分点。

为避免每个候选都重新扫描区间，先建立 prefix，prefix\[i\] 表示前 i 块的大小和，prefix\[0\] 为零。于是区间和是 prefix\[right\] 减 prefix\[left\]，用两个边界值即可得到。每次 append 加上当前块，新表长度最终为 n+1；这只是本题需要的前缀和用法，后续可另学更多区间查询技巧。

对 \[4,1,3,2\]，任意两块规则会先合并不相邻的 1 和 2，得到总费用 19，这一步在本题中不合法。区间算法得到费用 20，例如先合并 1 与 3 得 4，再与 2 合成 6，最后与最左 4 合并，支付 4、6、10。返回的记录可用上一节的区间执行检查核验。负大小拒绝，零大小允许，空输入费用零。前缀和 O(n+1)，填表时间 O((n+1)³)、表空间 O((n+1)²)，恢复 O(n+1)；没有使用未经讲解的优化降低切分枚举量。

**完整程序**

```python
def interval_merges(split, n):
    operations = []
    stack = [[0, n, False]]
    while len(stack) > 0:
        frame = stack.pop()
        left = frame[0]
        right = frame[1]
        if right - left > 1:
            middle = split[left][right]
            if frame[2]:
                operations.append([left, middle, right])
            else:
                stack.append([left, right, True])
                stack.append([middle, right, False])
                stack.append([left, middle, False])
    return operations

def adjacent_merge(weights):
    for weight in weights:
        if weight < 0:
            return None
    n = len(weights)
    prefix = [0]
    for weight in weights:
        prefix.append(prefix[-1] + weight)
    cost = []
    split = []
    for i in range(n + 1):
        cost.append([0] * (n + 1))
        split.append([None] * (n + 1))
    for length in range(2, n + 1):
        for left in range(n - length + 1):
            right = left + length
            best = None
            for middle in range(left + 1, right):
                candidate = cost[left][middle] + cost[middle][right]
                candidate = candidate + prefix[right] - prefix[left]
                if best is None or candidate < best:
                    best = candidate
                    split[left][right] = middle
            cost[left][right] = best
    return {"cost": cost[0][n], "merges": interval_merges(split, n)}

print(adjacent_merge([4, 1, 3, 2]))
print(adjacent_merge([]))
print(adjacent_merge([0, 0, 0]))
```

**预期输出**

```text
{'cost': 20, 'merges': [[1, 2, 3], [1, 3, 4], [0, 1, 4]]}
{'cost': 0, 'merges': []}
{'cost': 0, 'merges': [[1, 2, 3], [0, 1, 3]]}
```


选题关联：来源主题 1（文末列出）。

## 从父表建立森林：先验证，再安排依赖

树形问题输入用 parents 列表，结点编号为 0 到 n−1。parents\[v\] 为 −1 表示根，否则是唯一父结点编号；有多个根就是森林。类型约定为整数列表。父结点编号可以比孩子大，不能直接按编号倒序就声称孩子已完成。越界、其他负数、自身为父和循环关系都必须拒绝。

先为每个结点创建独立孩子表，再逐项登记父子边和根。随后把所有根放入 order，以游标从前向后读取，每访问一个结点便把其孩子追加到末尾。得到的顺序一定父先于子。它是从根扩展的顺序，不必等同某种深度优先后序；只要反转以后每个孩子都在父之前，就能用于下面的树形状态计算。

为什么这里不额外建立已访问集合？父表保证每个非根只有一个父亲，每个孩子也只被登记一次。从根出发不可能进入循环：环上的每个结点的唯一父亲都在环内，不会再有一条来自根路径的父边。因此每个可达结点只追加一次，循环所在分量反而不可从任何根到达。最后若 order 长度不是 n，就说明有未连到根的循环分量，返回 None。这个论证依赖父表契约，不能搬到任意邻接图上省掉访问标记。

示例 \[2,2,−1,0,−1\] 有根 2 和 4，order 为 \[2,4,0,1,3\]；逆序时 3 在 0 前，0、1 在 2 前。空父表是合法空森林。建表、扩展与验证时间和空间都是 O(n+1)，order 作为数组队列保留已经读过的前缀，空间仍计入。算法没有递归，长链也不依赖解释器递归层数。

**完整程序**

```python
def forest_structure(parents):
    n = len(parents)
    children = []
    roots = []
    for vertex in range(n):
        children.append([])
    for vertex in range(n):
        parent = parents[vertex]
        if parent == -1:
            roots.append(vertex)
        elif parent < 0 or parent >= n or parent == vertex:
            return None
        else:
            children[parent].append(vertex)
    order = roots.copy()
    front = 0
    while front < len(order):
        vertex = order[front]
        front = front + 1
        for child in children[vertex]:
            order.append(child)
    if len(order) != n:
        return None
    return {"children": children, "roots": roots, "order": order}

print(forest_structure([2, 2, -1, 0, -1]))
print(forest_structure([1, 0]))
print(forest_structure([]))
```

**预期输出**

```text
{'children': [[3], [], [0, 1], [], []], 'roots': [2, 4], 'order': [2, 4, 0, 1, 3]}
None
{'children': [], 'roots': [], 'order': []}
```


选题关联：来源主题 1（文末列出）。

## 选根与不选根：森林最大权独立集

给每个结点一个整数权重，要选出若干结点，使任何父子边都不同时选中两端，并让权重和最大。这叫独立集；“独立”在这里指图上不相邻，与概率独立无关。允许空选，权重可以为负。父表先通过上一节检查，权重列表长度必须相同。

对每个结点 v 定义 inside\[v\] 为在它的子树内强制选择 v 的最优值，outside\[v\] 为强制不选 v 的最优值。如果选 v，每个孩子都必须不选，故 inside 等于自身权重加各孩子 outside 之和；如果不选 v，孩子可选可不选，故 outside 为各孩子两个状态较大值之和。树中不同孩子的子树没有共享结点或跨边，在固定根的选择后才能独立组合。

叶子 inside 为其权重，outside 为 0。按 order 的逆序处理，孩子的两个值已经完成；把它们相加就完成父状态。若多个根，分量之间也无边，各自最优值可以相加。仅比较当前结点和直属孩子的权重不够，因为孩子状态还包含全部后代。示例根权重 6、两个叶子各为 4，不选根得到 8，比选根的 6 更好。

恢复改按父先于子的 order。父已选时强制不选当前结点；否则仅在 inside 严格大于 outside 时选择，平局不选。最后按编号扫描标记，输出升序原结点编号并重算权重。全负输入和空森林都返回空集、权重 0；若父表非法则返回 None。应同时检查边两端不能都在答案中，以及权重和等于穷举最优值。含验证、状态、恢复和结果的时间与空间均为 O(n+1)，按单位整数加法比较分析；一般有环图不能直接使用这两个树形转移。

**完整程序**

```python
def forest_structure(parents):
    n = len(parents)
    children = []
    roots = []
    for vertex in range(n):
        children.append([])
    for vertex in range(n):
        parent = parents[vertex]
        if parent == -1:
            roots.append(vertex)
        elif parent < 0 or parent >= n or parent == vertex:
            return None
        else:
            children[parent].append(vertex)
    order = roots.copy()
    front = 0
    while front < len(order):
        vertex = order[front]
        front = front + 1
        for child in children[vertex]:
            order.append(child)
    if len(order) != n:
        return None
    return {"children": children, "roots": roots, "order": order}

def forest_independent(weights, parents):
    if len(weights) != len(parents):
        return None
    forest = forest_structure(parents)
    if forest is None:
        return None
    inside = weights.copy()
    outside = [0] * len(weights)
    for vertex in forest["order"][::-1]:
        for child in forest["children"][vertex]:
            inside[vertex] = inside[vertex] + outside[child]
            best = outside[child]
            if inside[child] > best:
                best = inside[child]
            outside[vertex] = outside[vertex] + best
    chosen = [False] * len(weights)
    for vertex in forest["order"]:
        parent = parents[vertex]
        if parent == -1 or not chosen[parent]:
            chosen[vertex] = inside[vertex] > outside[vertex]
    total = 0
    vertices = []
    for vertex in range(len(weights)):
        if chosen[vertex]:
            total = total + weights[vertex]
            vertices.append(vertex)
    return {"weight": total, "vertices": vertices}

print(forest_independent([6, 4, 4], [-1, 0, 0]))
print(forest_independent([-2, -1], [-1, 0]))
print(forest_independent([], []))
```

**预期输出**

```text
{'weight': 8, 'vertices': [1, 2]}
{'weight': 0, 'vertices': []}
{'weight': 0, 'vertices': []}
```


选题关联：来源主题 1（文末列出）。

<a id="examples"></a>

## 跟着做：原创例题

### 例题 1

矩阵形状依次为 6×2、2×7、7×3，求最少标量乘法次数与执行记录；再检查三个 3×3 矩阵的平局。

1. 先算前两个矩阵花 6×2×7=84，结果形状 6×7，再乘末矩阵花 6×7×3=126，总计 210。
2. 先算后两个矩阵花 2×7×3=42，结果形状 2×3，再由首矩阵乘它花 6×2×3=36，总计 78。
3. 因此根切分在位置 1，先执行区间 \[1,3) 的合并，再执行整个 \[0,3) 的合并。
4. 三个 3×3 矩阵两种括号都是两次 27，总费用 54；最小切分点规则选择先算右侧。

**结果与核对**

第一组返回费用 78、记录 \[\[1,2,3\],\[0,1,3\]\]；第二组费用 54，记录相同。记录描述固定原顺序上的两侧结果，不是在矩阵之间换位。测试逐条消费已有区间，并枚举所有括号结构核对最优费用；只验证每条乘法尺寸相容仍不足以证明总费用最小。

**完整程序**

```python
def matrix_tables(dimensions):
    if len(dimensions) == 0:
        return None
    for dimension in dimensions:
        if dimension <= 0:
            return None
    n = len(dimensions) - 1
    cost = []
    split = []
    for i in range(n + 1):
        cost.append([0] * (n + 1))
        split.append([None] * (n + 1))
    for length in range(2, n + 1):
        for left in range(n - length + 1):
            right = left + length
            best = None
            for middle in range(left + 1, right):
                candidate = cost[left][middle] + cost[middle][right]
                candidate = candidate + dimensions[left] * dimensions[middle] * dimensions[right]
                if best is None or candidate < best:
                    best = candidate
                    split[left][right] = middle
            cost[left][right] = best
    return {"cost": cost, "split": split}

def interval_merges(split, n):
    operations = []
    stack = [[0, n, False]]
    while len(stack) > 0:
        frame = stack.pop()
        left = frame[0]
        right = frame[1]
        if right - left > 1:
            middle = split[left][right]
            if frame[2]:
                operations.append([left, middle, right])
            else:
                stack.append([left, right, True])
                stack.append([middle, right, False])
                stack.append([left, middle, False])
    return operations

def matrix_plan(dimensions):
    tables = matrix_tables(dimensions)
    if tables is None:
        return None
    n = len(dimensions) - 1
    return {"cost": tables["cost"][0][n],
            "merges": interval_merges(tables["split"], n)}

print(matrix_plan([6, 2, 7, 3]))
print(matrix_plan([3, 3, 3, 3]))
```

**预期输出**

```text
{'cost': 78, 'merges': [[1, 2, 3], [0, 1, 3]]}
{'cost': 54, 'merges': [[1, 2, 3], [0, 1, 3]]}
```


### 例题 2

权重 \[5,8,6,4,−2,3\]，父表 \[−1,0,0,1,1,−1\]。逐层求森林最大权独立集，并检查零权平局和循环父表。

1. 结点 3、4、2、5 是叶子，inside 分别为 4、−2、6、3，outside 都为 0。
2. 结点 1 的 inside 为 8，outside 为 4；负权叶子 4 可不选。
3. 结点 0 的 inside 为 5+4+0=9，outside 为 8+6=14，所以其分量选择结点 1 与 2。
4. 另一个根 5 独立贡献 3，合计 17；选择 1 后不能再选择它的孩子 3、4，恢复结果为 \[1,2,5\]。

**结果与核对**

答案权重 17，所有父子边都没有同时选择两端。零权二结点链在平局不选规则下返回空集，仍为最优；父表 \[1,0\] 没有根且形成循环，返回 None。没有为了处理循环而随意删边或把它当成两棵树。权重列表和父表均保持不变，测试以所有结点子集直接检查独立条件作为参考。

**完整程序**

```python
def forest_structure(parents):
    n = len(parents)
    children = []
    roots = []
    for vertex in range(n):
        children.append([])
    for vertex in range(n):
        parent = parents[vertex]
        if parent == -1:
            roots.append(vertex)
        elif parent < 0 or parent >= n or parent == vertex:
            return None
        else:
            children[parent].append(vertex)
    order = roots.copy()
    front = 0
    while front < len(order):
        vertex = order[front]
        front = front + 1
        for child in children[vertex]:
            order.append(child)
    if len(order) != n:
        return None
    return {"children": children, "roots": roots, "order": order}

def forest_independent(weights, parents):
    if len(weights) != len(parents):
        return None
    forest = forest_structure(parents)
    if forest is None:
        return None
    inside = weights.copy()
    outside = [0] * len(weights)
    for vertex in forest["order"][::-1]:
        for child in forest["children"][vertex]:
            inside[vertex] = inside[vertex] + outside[child]
            best = outside[child]
            if inside[child] > best:
                best = inside[child]
            outside[vertex] = outside[vertex] + best
    chosen = [False] * len(weights)
    for vertex in forest["order"]:
        parent = parents[vertex]
        if parent == -1 or not chosen[parent]:
            chosen[vertex] = inside[vertex] > outside[vertex]
    total = 0
    vertices = []
    for vertex in range(len(weights)):
        if chosen[vertex]:
            total = total + weights[vertex]
            vertices.append(vertex)
    return {"weight": total, "vertices": vertices}

print(forest_independent([5, 8, 6, 4, -2, 3], [-1, 0, 0, 1, 1, -1]))
print(forest_independent([0, 0], [-1, 0]))
print(forest_independent([1, 1], [1, 0]))
```

**预期输出**

```text
{'weight': 17, 'vertices': [1, 2, 5]}
{'weight': 0, 'vertices': []}
None
```


<a id="practice"></a>

## 自己做：先完成再看解答

### 练习 1

除最小费用外，统计矩阵链有多少种最优括号结构。对四个 2×2 矩阵、维度 \[6,2,7,3\] 和空链约定分别作答；不区分左右独立子树先计算哪一边。

<details>
<summary>提示</summary>

先求 cost，再枚举能达到该最优值的切分点。每个切分下，左侧最优结构数乘右侧最优结构数，再对不同切分相加。

</details>

<details>
<summary>解答与检查</summary>

四个 2×2 矩阵的费用均为三次 8，共 24，有 5 种括号结构；\[6,2,7,3\] 只有 1 种最优结构；空链按约定为费用 0、1 种空结构。空区间和单矩阵的 ways 为 1，不能初始化成零使乘法消失。不同根切分对应不同结构，所以可相加；同一结构的不同执行交错不另计。时间 O((n+1)³)、状态数 O((n+1)²)，计数很大时乘法和存储的位成本另计。

**完整程序**

```python
def matrix_tables(dimensions):
    if len(dimensions) == 0:
        return None
    for dimension in dimensions:
        if dimension <= 0:
            return None
    n = len(dimensions) - 1
    cost = []
    split = []
    for i in range(n + 1):
        cost.append([0] * (n + 1))
        split.append([None] * (n + 1))
    for length in range(2, n + 1):
        for left in range(n - length + 1):
            right = left + length
            best = None
            for middle in range(left + 1, right):
                candidate = cost[left][middle] + cost[middle][right]
                candidate = candidate + dimensions[left] * dimensions[middle] * dimensions[right]
                if best is None or candidate < best:
                    best = candidate
                    split[left][right] = middle
            cost[left][right] = best
    return {"cost": cost, "split": split}

def count_matrix_optima(dimensions):
    tables = matrix_tables(dimensions)
    if tables is None:
        return None
    n = len(dimensions) - 1
    ways = []
    for i in range(n + 1):
        ways.append([0] * (n + 1))
        ways[i][i] = 1
        if i < n:
            ways[i][i + 1] = 1
    for length in range(2, n + 1):
        for left in range(n - length + 1):
            right = left + length
            for middle in range(left + 1, right):
                candidate = tables["cost"][left][middle] + tables["cost"][middle][right]
                candidate = candidate + dimensions[left] * dimensions[middle] * dimensions[right]
                if candidate == tables["cost"][left][right]:
                    ways[left][right] = ways[left][right] + ways[left][middle] * ways[middle][right]
    return {"cost": tables["cost"][0][n], "count": ways[0][n]}

print(count_matrix_optima([2, 2, 2, 2, 2]))
print(count_matrix_optima([6, 2, 7, 3]))
print(count_matrix_optima([2]))
```

**预期输出**

```text
{'cost': 24, 'count': 5}
{'cost': 78, 'count': 1}
{'cost': 0, 'count': 1}
```


</details>

### 练习 2

森林每个结点有非负选择费用，要使每条父子边至少有一端被选，求最小费用及结点。这叫顶点覆盖。计算根费用 6、两个叶子各 4 的树，并检查零费用边。

<details>
<summary>提示</summary>

若不选父，所有孩子必须选；若选父，每个孩子可自由取两状态中较小值。恢复时父未选会强制当前结点选中。

</details>

<details>
<summary>解答与检查</summary>

inside 为自身费用加各孩子两状态最小值之和，outside 为所有孩子 inside 之和。示例选根费用 6，优于选两个叶子的 8。自由选择平局时不选，但父未选时必须选，故费用 \[0,0\] 的一条边返回孩子，不能返回空集。空森林费用零；负费用在本题接口中拒绝。含验证与恢复时间、空间 O(n+1)。独立集的补集恰是顶点覆盖，所以还可核对最小覆盖费用等于总费用减同权最大独立集；输出是否覆盖每条边仍需独立检查。

**完整程序**

```python
def forest_structure(parents):
    n = len(parents)
    children = []
    roots = []
    for vertex in range(n):
        children.append([])
    for vertex in range(n):
        parent = parents[vertex]
        if parent == -1:
            roots.append(vertex)
        elif parent < 0 or parent >= n or parent == vertex:
            return None
        else:
            children[parent].append(vertex)
    order = roots.copy()
    front = 0
    while front < len(order):
        vertex = order[front]
        front = front + 1
        for child in children[vertex]:
            order.append(child)
    if len(order) != n:
        return None
    return {"children": children, "roots": roots, "order": order}

def forest_vertex_cover(weights, parents):
    if len(weights) != len(parents):
        return None
    for weight in weights:
        if weight < 0:
            return None
    forest = forest_structure(parents)
    if forest is None:
        return None
    inside = weights.copy()
    outside = [0] * len(weights)
    for vertex in forest["order"][::-1]:
        for child in forest["children"][vertex]:
            best = outside[child]
            if inside[child] < best:
                best = inside[child]
            inside[vertex] = inside[vertex] + best
            outside[vertex] = outside[vertex] + inside[child]
    chosen = [False] * len(weights)
    for vertex in forest["order"]:
        parent = parents[vertex]
        if parent == -1 or chosen[parent]:
            chosen[vertex] = inside[vertex] < outside[vertex]
        else:
            chosen[vertex] = True
    total = 0
    vertices = []
    for vertex in range(len(weights)):
        if chosen[vertex]:
            total = total + weights[vertex]
            vertices.append(vertex)
    return {"cost": total, "vertices": vertices}

print(forest_vertex_cover([6, 4, 4], [-1, 0, 0]))
print(forest_vertex_cover([0, 0], [-1, 0]))
print(forest_vertex_cover([], []))
```

**预期输出**

```text
{'cost': 6, 'vertices': [0]}
{'cost': 0, 'vertices': [1]}
{'cost': 0, 'vertices': []}
```


</details>

### 练习 3

只给父表，统计全部独立结点子集数，包括空集。求一个根带两个叶子、两个孤立结点和空森林的结果；说明孩子之间为何相乘。

<details>
<summary>提示</summary>

inside 与 outside 改存条件方案数。选根时每个孩子只能不选；不选根时孩子的两类方案都允许。

</details>

<details>
<summary>解答与检查</summary>

叶子的两状态都为 1，分别对应选择它和不选它。inside 为各孩子 outside 的乘积，outside 为各孩子两状态之和的乘积；不同根分量的总数也相乘。星形三结点树有 5 个独立集，两个孤立点有 4 个，空森林有 1 个空集。这里统计全部合法方案，不能把最大权版本的 max 改成加号而保留其余所有运算。只有 O(n+1) 次状态组合及 O(n+1) 个整数槽位，但大整数可能各占多位；长链保留全部子树计数时不能据此声称只有线性位空间。

**完整程序**

```python
def forest_structure(parents):
    n = len(parents)
    children = []
    roots = []
    for vertex in range(n):
        children.append([])
    for vertex in range(n):
        parent = parents[vertex]
        if parent == -1:
            roots.append(vertex)
        elif parent < 0 or parent >= n or parent == vertex:
            return None
        else:
            children[parent].append(vertex)
    order = roots.copy()
    front = 0
    while front < len(order):
        vertex = order[front]
        front = front + 1
        for child in children[vertex]:
            order.append(child)
    if len(order) != n:
        return None
    return {"children": children, "roots": roots, "order": order}

def count_forest_independent(parents):
    forest = forest_structure(parents)
    if forest is None:
        return None
    inside = [1] * len(parents)
    outside = [1] * len(parents)
    for vertex in forest["order"][::-1]:
        for child in forest["children"][vertex]:
            inside[vertex] = inside[vertex] * outside[child]
            outside[vertex] = outside[vertex] * (inside[child] + outside[child])
    count = 1
    for root in forest["roots"]:
        count = count * (inside[root] + outside[root])
    return count

print(count_forest_independent([-1, 0, 0]))
print(count_forest_independent([-1, -1]))
print(count_forest_independent([]))
```

**预期输出**

```text
5
4
1
```


</details>

<a id="pitfalls"></a>

## 容易混淆的地方

- **把矩阵链的最后切分或树根的选择当作一次局部贪心。** 必须比较该选择下全部子问题的最优代价，不能只看眼前乘法次数或当前结点权重。
- **把编号倒序直接当作孩子先完成，或把循环父表当成森林。** 编号可能任意；先验证父表并建立父先于子的顺序，再反转计算。
- **恢复覆盖时遇到零费用就跳过，导致一条边两端都没选。** 平局规则只适用于自由状态；父未选时孩子必须选，不受本地费用是否为零影响。
- **把括号结构数、不同执行顺序数与最优值混为一谈。** 计数对象必须先固定；乘积组合独立子选择，相加组合互斥分类，最优值则使用最大或最小。

<a id="self-check"></a>

## 离开这一章前

- [ ] 用维度边界推导一条 \[left,middle,right\] 操作的两侧形状和乘法次数。
- [ ] 重放相邻合并记录，检查所有中间块仍对应连续原区间。
- [ ] 给父表重新编号，使父编号大于孩子，再验证结果不变。
- [ ] 分别列举三结点树的全部独立集和覆盖，核对空集、零权和平局。

## 本章边界

- 矩阵只优化传统标量乘法次数，不计算元素或讨论快速矩阵乘法；相邻合并限定线性排列与非负大小。
- 树形部分只接收经验证的单父森林，不能直接处理共享子结点的 DAG、一般图、环或动态修改。
- 未覆盖环形区间、区间优化、换根、树上背包及全部最优方案列举；计数与费用的大整数位成本另计。

## 选题来源与覆盖

来源含学生报告时，仅将其作为选题线索；具体机制仍需结合后续实验或权威资料核对。

- [大一小学期/Week\_3-Python/docs/readme.md](https://github.com/PKUanonym/REKCARC-TSC-UHT/blob/37cd19f7a9fb80dc846a7016b3fd482ed5fe7cc0/%E5%A4%A7%E4%B8%80%E5%B0%8F%E5%AD%A6%E6%9C%9F/Week_3-Python/docs/readme.md)（已提取可读文本，固定版本 37cd19f7a9fb）
- 主题 1：Python 基础语法的外部学习入口；位置：第 41–80 行。
- 主题 2：从基础语法到工具与应用的建议阅读顺序；位置：第 121–160 行。

## 参考资料与规则核对

上游入口用于确定学习方向；下面的参考资料用于核对语言语义、数据结构或算法分析规则，例题和练习由本项目重新设计。

- [MIT 6.006：矩阵链的区间状态](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/3484e876d81aba07911a1109f5b5e81e_MIT6_006F11_lec21.pdf)：仅核对最后切分与按区间长度的依赖；本章自行设计维度、零矩阵约定、显式操作记录和最优结构计数。
- [Illinois CS/ECE 374：树形动态规划](https://courses.grainger.illinois.edu/cs374al1/fa2026/lectures/tree-dynamic-programming.html)：核对区间拆分和固定根选择后组合孩子的思想；本章使用相邻合并模型和经验证的单父森林，例题、非递归实现及验收独立设计。
- [Stanford CS161：树上最大权独立集](https://web.stanford.edu/class/archive/cs/cs161/cs161.1172/CS161Lecture13.pdf)：核对选根与不选根的依赖关系；本章另定负权、空森林、父表拒绝和稳定恢复的接口。

**继续学习**：先独立完成自测，再记录仍需回读的步骤。

[上一章：对齐两个前缀：序列动态规划与方案恢复](29-sequence-dp.md)

[教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [哈希表与图练习指引](../hash-graphs-practice.md) · [拓扑排序与带权图练习指引](../weighted-graphs-practice.md) · [记录自己的学习](../learning-log-template.md)
