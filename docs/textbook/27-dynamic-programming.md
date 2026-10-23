# 保存子问题的答案：动态规划入门

[返回教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [哈希表与图练习指引](../hash-graphs-practice.md) · [拓扑排序与带权图练习指引](../weighted-graphs-practice.md)

[上一章：证明眼前选择的正确性：贪心算法与交换论证](26-greedy-algorithms.md)

[学习目标](#objectives) · [需要的基础](#prerequisites) · [例题](#examples) · [练习](#practice) · [自测](#self-check)

状态：**AI 初稿，可开始试学**。生成模型：Codex 当前会话（未记录具体模型型号）。

本章围绕资料中识别到的知识点重新编写；讲解、数值模型、例题与练习为 AI 原创组织，不是原课程题目或答案。主题出处只说明选题关联，不证明全部推导已经正确。

同一个剩余问题可能沿不同选择路径反复出现。回溯会分别求解这些分支，动态规划则先定义清楚子问题，把已经求出的结果保存下来。本章从一步或两步的计数开始，依次建立记忆化、表格顺序、最少硬币和网格状态，再练习恢复方案与压缩空间。重点是状态究竟表示什么、依赖是否已经算好，以及改变循环顺序会不会悄悄改变题目。

<a id="objectives"></a>

## 学完要能做到

- 完整写出状态含义、转移、初始条件、计算顺序和最终答案。
- 把重复递归改成记忆化和自底向上计算，区分调用与实际展开。
- 正确表示不可达状态，恢复一个达到最优值的方案。
- 解释空间压缩后每个数组位置属于哪一轮，并识别数值大小带来的伪多项式成本。

<a id="prerequisites"></a>

## 需要的基础

- 第 13、25 章的递归、搜索与完整枚举。
- 第 6、10 章的列表、独立行和时间空间分析。
- 第 22、23、26 章的无环依赖、同步更新与贪心反例。

## 状态从问题含义出发：相同剩余量反复出现

从位置 0 到位置 n，每次前进 1 或 2，问不同步长序列有多少种。先把 n 限定为非负整数，顺序不同算不同方案。定义 w(r) 为恰好走完剩余 r 的序列数量；这里后面的合法选择只由剩余距离决定，与已经走过的顺序无关，因此 r 足够表示子问题。

当 r=0，不再走任何一步就是唯一的空序列，所以 w(0)=1；r=1 只能走一步，w(1)=1。r 至少为 2 时，按第一步长度分类，得到 w(r)=w(r−1)+w(r−2)。两类第一步不同，所以不重叠；每个合法序列都落入一类，所以没有遗漏。若把空序列计为 0，恰好走完的分支就会被错误抹掉。

ways\_naive 直接照此递归，并用单元素列表记录实际调用次数。n=5 的结果为 8，但需要 15 次调用；求 w(5) 时，w(3) 既出现在 w(4) 分支里，又作为另一个直接子问题出现。输入逐渐增大，这些重复会迅速累积。计数器包含基例调用，不等于不同子问题的数量。

这是计数问题，不必先有最大值或最小值才能使用动态规划。关键在于状态是否完整、依赖是否能终止，以及相同状态是否能复用同一个结果。如果题目规定不能连续走两次 2，单独记录 r 就不够，还要记前一步信息。朴素版本的安全时间上界为 O(2ⁿ)，递归工作空间 O(n+1)；即使只返回一个数，也可能做指数次工作。负 n 返回 None，测试只用能完成的小输入。

**完整程序**

```python
def ways_naive(n):
    if n < 0:
        return None
    calls = [0]
    def solve(remaining):
        calls[0] = calls[0] + 1
        if remaining <= 1:
            return 1
        return solve(remaining - 1) + solve(remaining - 2)
    answer = solve(n)
    return {"ways": answer, "calls": calls[0]}

print(ways_naive(5))
print(ways_naive(0))
```

**预期输出**

```text
{'ways': 8, 'calls': 15}
{'ways': 1, 'calls': 1}
```


选题关联：来源主题 1（文末列出）。

## 记忆化：先查表，真正需要时才展开

保持相同的 w(r) 定义，增加 memo 表。每次进入 solve 先检查相应槽位，已有值就直接返回；还没有值才递归求两个更小的状态，保存结果再返回。这叫自顶向下的记忆化。复用的是子问题答案，不是把不同完整方案认作同一条路径，所以计数仍然正确。

用 None 表示未计算，不要用 0 的真假来判断，因为其他动态规划问题的合法答案可能为零。本例先填好两个基例，只有状态 2 到 n 需要展开。n=5 时，solve 被调用 9 次，但展开只有 4 次；缓存命中仍然发生一次查表和返回，不能把它从调用统计中删除。

memo 在每次 ways\_memo 调用时重新建立，避免上一次输入或不同问题设置污染本次计算。所有依赖都从 r 指向更小的数，构成无环关系，所以递归一定先完成依赖再写入当前值。对含循环依赖的问题，仅加一个“结果缓存”并不会自动打断正在求解的循环；第 23 章通过增加边数维度处理过这种差别。

在按整数算术和列表下标访问为单位成本的模型下，有 O(n+1) 个状态，每个未缓存状态只做常数工作，时间 O(n+1)。表和递归栈都可达到 O(n+1)，因此记忆化并没有消除 Python 的递归深度限制。它减少重复工作，却不保证所有动态规划都是多项式：状态维度、每个状态的选择数量和数值编码长度仍需分别计算。下面的 expanded 特意不包含预先填好的基例。

**完整程序**

```python
def ways_memo(n):
    if n < 0:
        return None
    memo = [None] * (n + 1)
    memo[0] = 1
    if n > 0:
        memo[1] = 1
    calls = [0]
    expanded = [0]
    def solve(remaining):
        calls[0] = calls[0] + 1
        if memo[remaining] is not None:
            return memo[remaining]
        expanded[0] = expanded[0] + 1
        memo[remaining] = solve(remaining - 1) + solve(remaining - 2)
        return memo[remaining]
    answer = solve(n)
    return {"ways": answer, "calls": calls[0], "expanded": expanded[0]}

print(ways_memo(5))
print(ways_memo(0))
```

**预期输出**

```text
{'ways': 8, 'calls': 9, 'expanded': 4}
{'ways': 1, 'calls': 1, 'expanded': 0}
```


选题关联：来源主题 1（文末列出）。

## 自底向上：按依赖顺序填表

w(i) 只依赖 w(i−1) 和 w(i−2)，因此可以从小到大填表，不再让函数递归安排顺序。先建立长度 n+1 的表，把位置 0 设为 1；处理 i 时先取 i−1 的值，若 i 至少为 2 再加 i−2。这样 i=1 不会错误地访问负下标，在 Python 中负下标本来合法，更需要主动检查边界。

循环不变式是处理 i 之前，编号小于 i 的状态都已经等于其定义的正确答案。转移使用这些状态的值，按互不重叠的第一步分类得到 w(i)，因此不变式向前推进。最后 ways\[n\] 是目标答案，整个表还保存了每个中间问题的结果，方便手算核对。n=0 时没有循环，但初始化已经给出正确值。

自底向上顺序是子问题依赖图的一种拓扑序，不是机械地“把递归换成 for”。有些问题要按区间长度，有些要按物品数，有些要按网格方向；必须先画出依赖，再决定循环方向。本例全部状态都会用到，一般记忆化有时只访问目标需要的部分，而填完整表可能计算更多状态。

该实现返回完整表，时间和空间均为 O(n+1)，不使用递归栈。如果只要最终数量，可保留最近两个值，但那会改变返回接口，也失去直接查看全部中间值的能力。计数随 n 增长会变成大整数；这里的线性界按一次整数加法计一步，不表示任意大 n 的位运算时间和实际内存仍严格线性。先说明成本模型，再比较优化效果。

**完整程序**

```python
def ways_table(n):
    if n < 0:
        return None
    ways = [0] * (n + 1)
    ways[0] = 1
    for total in range(1, n + 1):
        ways[total] = ways[total - 1]
        if total >= 2:
            ways[total] = ways[total] + ways[total - 2]
    return ways

print(ways_table(5))
print(ways_table(0))
```

**预期输出**

```text
[1, 1, 2, 3, 5, 8]
[1]
```


选题关联：来源主题 1（文末列出）。

## 最少硬币：枚举最后一步并表示不可达

面额为正整数，每种可以无限使用，目标金额为非负整数。定义 best\[s\] 为恰好凑出金额 s 的最少枚数，best\[0\]=0，尚不可达的金额为 None。对每种不超过 s 的面额 c，若 best\[s−c\] 有限，就得到一个候选 best\[s−c\]+1；遍历所有候选取最小值，而不是只取最大面额。

正确性分两边看：每个候选在一个合法小金额方案后加一枚 c，确实能构成 s；反过来，任何非空最优方案都有最后一枚 c，去掉它后必须是 s−c 的最优方案，否则可以替换成更少枚数的子方案，改善原解。枚举所有最后一枚就不会漏掉最优方案。面额严格为正保证 s−c 更小，按金额递增计算依赖已完成。

last\[s\] 保存导致严格改善的面额。求完后从 amount 反复减去 last，便恢复一个最优方案；金额严格下降，所以一定到 0。相同枚数不覆盖旧选择，使平局由输入面额顺序决定，不保证字典序最小。重复面额不会改变最少枚数，只会多检查候选。零面额和负面额都拒绝，负金额也返回 None；在合法输入下返回 None 表示金额不可达。

设面额项数 k、目标 A，初始化表和恢复方案也计入后，时间为 O(k(A+1)+A+1)，空间 O(A+1)，按单位整数操作分析。这个界依赖金额的数值，而不是输入 A 所需的二进制位数，因此称为伪多项式；A 很大仍可能无法建表。金额 0 的答案是零枚和空列表，即使没有面额也成立。不能把 None 当作 0 加进候选。

**完整程序**

```python
def min_coins(coins, amount):
    if amount < 0:
        return None
    for coin in coins:
        if coin <= 0:
            return None
    best = [None] * (amount + 1)
    last = [None] * (amount + 1)
    best[0] = 0
    for total in range(1, amount + 1):
        for coin in coins:
            if coin <= total and best[total - coin] is not None:
                candidate = best[total - coin] + 1
                if best[total] is None or candidate < best[total]:
                    best[total] = candidate
                    last[total] = coin
    if best[amount] is None:
        return None
    selected = []
    remaining = amount
    while remaining > 0:
        coin = last[remaining]
        selected.append(coin)
        remaining = remaining - coin
    return {"count": best[amount], "coins": selected}

print(min_coins([4, 6], 8))
print(min_coins([4, 6], 7))
print(min_coins([], 0))
```

**预期输出**

```text
{'count': 2, 'coins': [4, 4]}
None
{'count': 0, 'coins': []}
```


选题关联：来源主题 1（文末列出）。

## 二维状态：只向右或向下的障碍网格

网格从左上角出发到右下角，每次只向右或向下。输入 blocked 是矩形布尔列表，True 表示障碍。定义 table\[r\]\[c\] 为到达格子 r、c 的合法路径数。障碍格为 0；无障碍的起点为 1；其他格按最后一步从上方还是左方进入分类，把存在的两项相加。

这两类路径互不重叠，而且包含所有到达当前格子的路径。循环从上到下、每行从左到右，处理当前格子时，上方整行和左方格子都已完成。首行没有上方贡献，首列没有左方贡献；被障碍切断的位置自然维持零。若起点就是障碍，所有后续值也保持零，不需要人为绕过起点。

每行必须独立创建。table.append(\[0\] \* columns) 在每次循环生成新行；若先造一行再复制它的引用，修改一个格子会影响其他行，破坏状态含义。grid\_shape 检查矩形形状；不规则行返回 None，空网格或零列网格没有起终点，路径数规定为 0。非空单格且无障碍时只有一条不移动的路径，返回 1。

对 R 行、C 列且 C 为正的网格，时间与表空间为 O(RC)，另有行结构开销；含零列情形可统一把时间写成 O(R(C+1)+1)。本例不返回具体路径，只返回数量。若允许向左或向上，就可能出现循环甚至无限游走，不能沿用这个两方向递推。将来若要压缩成一行，必须说明同一数组中哪些值属于上一行，哪些属于当前行，练习会逐格核对。

**完整程序**

```python
def grid_shape(grid):
    rows = len(grid)
    if rows == 0:
        return [0, 0]
    columns = len(grid[0])
    for row in grid:
        if len(row) != columns:
            return None
    return [rows, columns]

def grid_paths(blocked):
    shape = grid_shape(blocked)
    if shape is None:
        return None
    rows = shape[0]
    columns = shape[1]
    if rows == 0 or columns == 0:
        return 0
    table = []
    for row in range(rows):
        table.append([0] * columns)
    for row in range(rows):
        for column in range(columns):
            if not blocked[row][column]:
                if row == 0 and column == 0:
                    table[row][column] = 1
                else:
                    if row > 0:
                        table[row][column] = table[row - 1][column]
                    if column > 0:
                        table[row][column] = table[row][column] + table[row][column - 1]
    return table[rows - 1][columns - 1]

print(grid_paths([[False, False, False], [False, True, False], [False, False, False]]))
print(grid_paths([[False]]))
print(grid_paths([]))
```

**预期输出**

```text
2
1
0
```


选题关联：来源主题 1（文末列出）。

<a id="examples"></a>

## 跟着做：原创例题

### 例题 1

面额 \[1,4,6\]、目标 8，列出金额 0–8 的最少枚数，并恢复一种最优方案，与上一章的贪心结果比较。

1. 金额 0 的最少枚数是 0；金额 1、2、3 分别需要 1、2、3 枚。
2. 金额 4 可直接用一枚 4，金额 5 最少两枚，金额 6 可直接用一枚 6。
3. 金额 7 有 6+1，共两枚；金额 8 比较接 1、4、6 的候选，最优来自金额 4 再加一枚 4。
4. 回溯 last 从 8 到 4 再到 0，恢复 \[4,4\]；最大面额贪心的 \[6,1,1\] 多用一枚。

**结果与核对**

完整最少枚数表是 \[0,1,2,3,1,2,1,2,2\]。下面为了教学逐个调用函数打印每个金额的结果，这段展示程序会重复建表；它不是一次求解的线性扫描成本。目标到 A 的全部演示调用累计可达 O((k+1)(A+1)²)，而一次求解按正文给出的 O(k(A+1)+A+1) 分析。独立测试用按硬币枚数分层的搜索作为参照，另外核验恢复列表的总额与长度，避免只比较一个最优数值。

**完整程序**

```python
def min_coins(coins, amount):
    if amount < 0:
        return None
    for coin in coins:
        if coin <= 0:
            return None
    best = [None] * (amount + 1)
    last = [None] * (amount + 1)
    best[0] = 0
    for total in range(1, amount + 1):
        for coin in coins:
            if coin <= total and best[total - coin] is not None:
                candidate = best[total - coin] + 1
                if best[total] is None or candidate < best[total]:
                    best[total] = candidate
                    last[total] = coin
    if best[amount] is None:
        return None
    selected = []
    remaining = amount
    while remaining > 0:
        coin = last[remaining]
        selected.append(coin)
        remaining = remaining - coin
    return {"count": best[amount], "coins": selected}

counts = []
for amount in range(9):
    counts.append(min_coins([1, 4, 6], amount)["count"])
print(counts)
print(min_coins([1, 4, 6], 8))
```

**预期输出**

```text
[0, 1, 2, 3, 1, 2, 1, 2, 2]
{'count': 2, 'coins': [4, 4]}
```


### 例题 2

每进入一个格子支付该格费用，起点也计费，None 为障碍，只能向右或向下。求 \[\[2,5,1\],\[1,None,2\],\[3,1,1\]\] 的最小总费用，并返回路径坐标。

1. 第一行累计费用为 2、7、8，第一列累计费用为 2、3、6，中间障碍保持不可达。
2. 右中格只能从上方进入，费用为 10；下中格只能从左方进入，费用为 7。
3. 右下格比较从上方来的 10 和从左方来的 7，再加自身 1，得到 8。
4. 从终点沿 parent 倒推，反转坐标序列，得到先沿左列向下、再沿底行向右的路径。

**结果与核对**

返回费用 8 和 \[\[0,0\],\[1,0\],\[2,0\],\[2,1\],\[2,2\]\]。每次转移保存一个达到最小值的前驱；平局优先上方，只承诺一种最优路径。费用允许负整数，因为只右下移动的依赖图无环，不会出现负环。空网格、零列、不规则网格或终点不可达均返回 None，合法单格费用必须包含该格。时间 O(R(C+1)+1)，表、前驱和返回路径空间 O(R(C+1)+1)；若删去父指针以压缩空间，不能再声称原恢复接口仍然免费保留。

**完整程序**

```python
def grid_shape(grid):
    rows = len(grid)
    if rows == 0:
        return [0, 0]
    columns = len(grid[0])
    for row in grid:
        if len(row) != columns:
            return None
    return [rows, columns]

def min_grid_path(costs):
    shape = grid_shape(costs)
    if shape is None or shape[0] == 0 or shape[1] == 0:
        return None
    rows = shape[0]
    columns = shape[1]
    best = []
    parent = []
    for row in range(rows):
        best.append([None] * columns)
        parent.append([None] * columns)
    for row in range(rows):
        for column in range(columns):
            value = costs[row][column]
            if value is not None:
                if row == 0 and column == 0:
                    best[row][column] = value
                else:
                    if row > 0 and best[row - 1][column] is not None:
                        best[row][column] = best[row - 1][column] + value
                        parent[row][column] = [row - 1, column]
                    if column > 0 and best[row][column - 1] is not None:
                        candidate = best[row][column - 1] + value
                        if best[row][column] is None or candidate < best[row][column]:
                            best[row][column] = candidate
                            parent[row][column] = [row, column - 1]
    if best[rows - 1][columns - 1] is None:
        return None
    reverse_path = []
    current = [rows - 1, columns - 1]
    while current is not None:
        reverse_path.append(current)
        current = parent[current[0]][current[1]]
    path = []
    for index in range(len(reverse_path) - 1, -1, -1):
        path.append(reverse_path[index])
    return {"cost": best[rows - 1][columns - 1], "path": path}

print(min_grid_path([[2, 5, 1], [1, None, 2], [3, 1, 1]]))
print(min_grid_path([[None]]))
print(min_grid_path([[-3]]))
```

**预期输出**

```text
{'cost': 8, 'path': [[0, 0], [1, 0], [2, 0], [2, 1], [2, 2]]}
None
{'cost': -3, 'path': [[0, 0]]}
```


<a id="practice"></a>

## 自己做：先完成再看解答

### 练习 1

从整数列表中选取互不相邻的位置，使总和最大，允许一个也不选。对 \[4,7,3,6\] 返回最大和及原位置下标，并处理全负列表。

<details>
<summary>提示</summary>

令 best\[i\] 表示前 i 项的最优值，按是否选择第 i−1 项分类；选择时只能接到前 i−2 项。

</details>

<details>
<summary>解答与检查</summary>

不选当前项得到 best\[i−1\]，选当前项得到 values\[i−1\] 加 best\[i−2\]，只有一项时后者只取该值。初始化空前缀为 0，保证全负输入可选空集。take 保存严格改善的选择；恢复时选中就退两项，否则退一项，平局保留不选当前项的方案。本例得到总和 13、下标 \[1,3\]，全负列表得到 0 和 \[\]。每个状态常数工作，恢复最多 n 步，时间空间均为 O(n+1)。不能在状态里只记“上一项是否被选”却遗漏该状态的最优值。

**完整程序**

```python
def max_nonadjacent(values):
    n = len(values)
    best = [0] * (n + 1)
    take = [False] * (n + 1)
    for size in range(1, n + 1):
        candidate = values[size - 1]
        if size >= 2:
            candidate = candidate + best[size - 2]
        best[size] = best[size - 1]
        if candidate > best[size]:
            best[size] = candidate
            take[size] = True
    reverse_indices = []
    size = n
    while size > 0:
        if take[size]:
            reverse_indices.append(size - 1)
            size = size - 2
        else:
            size = size - 1
    indices = []
    for index in range(len(reverse_indices) - 1, -1, -1):
        indices.append(reverse_indices[index])
    return {"sum": best[n], "indices": indices}

print(max_nonadjacent([4, 7, 3, 6]))
print(max_nonadjacent([-2, -1]))
print(max_nonadjacent([]))
```

**预期输出**

```text
{'sum': 13, 'indices': [1, 3]}
{'sum': 0, 'indices': []}
{'sum': 0, 'indices': []}
```


</details>

### 练习 2

把障碍网格路径计数压缩为一个长度等于列数的列表，保持原输入不变。解释从左到右更新时每个操作数来自哪一行。

<details>
<summary>提示</summary>

更新 ways\[c\] 前，它是上一行同列的值；ways\[c−1\] 已经更新为当前行左邻值。遇到障碍必须把本槽清零。

</details>

<details>
<summary>解答与检查</summary>

初始化 ways\[0\]=1，其余为 0，将它看作进入起点的一份初始贡献；起点若是障碍，会立即清零。每个无障碍非首列格把旧的上方值与新的左方值相加，这次需要混用新旧状态，正好符合递推，而不是一律禁止本轮读取。时间与二维版本相同，工作空间降为 O(C+1)。单数组只保存计数，不保留完整表或父指针；不能顺带承诺恢复全部路径。矩形检查和空网格返回约定与正文一致。

**完整程序**

```python
def grid_shape(grid):
    rows = len(grid)
    if rows == 0:
        return [0, 0]
    columns = len(grid[0])
    for row in grid:
        if len(row) != columns:
            return None
    return [rows, columns]

def rolling_grid_paths(blocked):
    shape = grid_shape(blocked)
    if shape is None:
        return None
    rows = shape[0]
    columns = shape[1]
    if rows == 0 or columns == 0:
        return 0
    ways = [0] * columns
    ways[0] = 1
    for row in range(rows):
        for column in range(columns):
            if blocked[row][column]:
                ways[column] = 0
            elif column > 0:
                ways[column] = ways[column] + ways[column - 1]
    return ways[columns - 1]

print(rolling_grid_paths([[False, False, False], [False, True, False], [False, False, False]]))
print(rolling_grid_paths([[False, True, False]]))
print(rolling_grid_paths([[], []]))
```

**预期输出**

```text
2
0
0
```


</details>

### 练习 3

给定非负整数列表，每个位置最多使用一次，只判断能否恰好达到 target。实现单数组状态，解释为什么对 \[2\]、目标 4 必须返回 False。

<details>
<summary>提示</summary>

逐项处理物品。对当前值 value，从 target 向 value 递减更新，确保读取较小和时它还属于处理当前项之前。

</details>

<details>
<summary>解答与检查</summary>

reachable\[s\] 表示已处理位置能否组成 s，初始只有 reachable\[0\] 为 True。倒序时 s−value 尚未被当前正值修改，因此不会重复使用同一位置；若正序，处理一个 2 时可能先得到 2，再读这个新值得到 4，便变成允许重复使用。value=0 只把槽位与自身合并，不改变存在性，仍然正确；这不代表零对“方案数”没有影响。目标和数值为负时返回 None，空输入对零目标为 True。时间 O(n(T+1)+T+1)、空间 O(T+1)，属于依赖数值 T 的伪多项式算法；它只判断存在，不枚举第 25 章的全部位置子集。

**完整程序**

```python
def subset_reachable(values, target):
    if target < 0:
        return None
    for value in values:
        if value < 0:
            return None
    reachable = [False] * (target + 1)
    reachable[0] = True
    for value in values:
        for total in range(target, value - 1, -1):
            if reachable[total - value]:
                reachable[total] = True
    return reachable[target]

print(subset_reachable([2], 4))
print(subset_reachable([2, 3, 7], 5))
print(subset_reachable([0, 0], 0))
print(subset_reachable([], 1))
```

**预期输出**

```text
False
True
True
False
```


</details>

<a id="pitfalls"></a>

## 容易混淆的地方

- **先开一个数组，再猜一个转移就是动态规划。** 先用一句话定义每个状态包含哪些输入和目标，证明合法方案能按互斥或取优规则分类。
- **0、None 和 False 都可以表示没算过。** 零费用、零种方案和不可达具有不同含义；按状态语义选哨兵，不能只依靠真假判断。
- **任何单数组优化都应该正向更新。** 网格需要左边的新状态，每项一次的子集和需要较小和的旧状态；循环方向由依赖决定。
- **时间与金额成正比就一定是输入长度的多项式。** 一个大金额可以用很少二进制位写出，依赖数值的表长可能远大于输入位数。

<a id="self-check"></a>

## 离开这一章前

- [ ] 分别写出三种一步两步计数实现的状态与基例，解释调用数为何不同。
- [ ] 手算一个不可达金额，检查程序不会把 None 加成候选。
- [ ] 沿恢复路径核对每步合法、总费用和输出一致。
- [ ] 用一个物品构造正向更新会重复使用的最小例子。
- [ ] 解释二维表压缩后失去了哪些可直接查看的信息。

## 本章边界

- 只讲入门状态设计；背包优化、LCS、LIS、区间和树形动态规划仍待后续。
- 所有规模需适合内存和运行时间，记忆化仍受递归限制，计数的大整数位成本需另行分析。
- 代码验证不代替教学效果评估，教材继续保留 AI 草稿状态。

## 选题来源与覆盖

来源含学生报告时，仅将其作为选题线索；具体机制仍需结合后续实验或权威资料核对。

- [大一小学期/Week\_3-Python/docs/readme.md](https://github.com/PKUanonym/REKCARC-TSC-UHT/blob/37cd19f7a9fb80dc846a7016b3fd482ed5fe7cc0/%E5%A4%A7%E4%B8%80%E5%B0%8F%E5%AD%A6%E6%9C%9F/Week_3-Python/docs/readme.md)（已提取可读文本，固定版本 37cd19f7a9fb）
- 主题 1：Python 基础语法的外部学习入口；位置：第 41–80 行。
- 主题 2：从基础语法到工具与应用的建议阅读顺序；位置：第 121–160 行。

## 参考资料与规则核对

上游入口用于确定学习方向；下面的参考资料用于核对语言语义、数据结构或算法分析规则，例题和练习由本项目重新设计。

- [MIT 6.006：记忆化与自底向上计算](https://www.ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/b6d4083131dd16e7d97f56d04b6e858f_MIT6_006F11_lec19.pdf)：核对复用子问题、按依赖顺序计算与状态数乘每状态工作量的思路；本章问题、数字、返回接口及全部 Python 程序重新设计，不移植课程作业或参考解答。
- [NIST DADS：动态规划](https://xlinux.nist.gov/dads/HTML/dynamicprog.html)：核对缓存子问题答案的基本思想；本章还包含计数和存在性任务，并明确状态设计与伪多项式范围。

**继续学习**：先独立完成自测，再记录仍需回读的步骤。

[上一章：证明眼前选择的正确性：贪心算法与交换论证](26-greedy-algorithms.md)

[教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [哈希表与图练习指引](../hash-graphs-practice.md) · [拓扑排序与带权图练习指引](../weighted-graphs-practice.md) · [记录自己的学习](../learning-log-template.md)
