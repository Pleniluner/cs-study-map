# 限定容量与使用次数：背包问题和方案计数

[返回教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [哈希表与图练习指引](../hash-graphs-practice.md) · [拓扑排序与带权图练习指引](../weighted-graphs-practice.md)

[上一章：保存子问题的答案：动态规划入门](27-dynamic-programming.md) · [下一章：对齐两个前缀：序列动态规划与方案恢复](29-sequence-dp.md)

[学习目标](#objectives) · [需要的基础](#prerequisites) · [例题](#examples) · [练习](#practice) · [自测](#self-check)

状态：**AI 初稿，可开始试学**。生成模型：Codex 当前会话（未记录具体模型型号）。

本章围绕资料中识别到的知识点重新编写；讲解、数值模型、例题与练习为 AI 原创组织，不是原课程题目或答案。主题出处只说明选题关联，不证明全部推导已经正确。

上一章已经能判断一组数能否凑出目标，也能求最少硬币。本章再加入价值、容量和物品使用次数：同样写一个数组，究竟表示容量上限还是恰好重量，会改变初值；同样使用一个物品，究竟只能一次还是可以重复，会改变依赖。先手算小表，再恢复原位置，最后研究计数。每个程序都独立可运行，返回值、空方案和无解分别说明。学习重点是从问题模型推导循环，而不是记住几个方向口令。

<a id="objectives"></a>

## 学完要能做到

- 用物品前缀和容量定义 0/1 背包状态，并证明选与不选的分类完整。
- 恢复满足容量和次数限制的一种最优方案，解释零重量物品的停止条件。
- 区分一次使用、无限使用、恰好装满及不同计数对象的初值与依赖。
- 说明容量数值、整数位数、完整表和压缩数组各自对成本的影响。

<a id="prerequisites"></a>

## 需要的基础

- 第 27 章的状态、不可达哨兵、更新顺序与方案恢复。
- 列表下标、独立二维行、函数、循环和 None 判断。
- 第 25 章的位置子集与第 26 章的贪心反例。

## 容量上限与物品前缀：0/1 背包的二维状态

有 n 件物品，第 i 件重量为 weights\[i\]、价值为 values\[i\]，背包容量为 C。要选择总重量不超过 C 的位置子集，使价值和最大，每个位置最多选一次；重复的重量和价值仍可以属于不同物品。允许空选。本章输入为整数和整数列表，容量、重量非负，价值可以为负；不进行类型转换。valid\_items 只检查长度及数值范围，类型契约由调用者满足。

定义 table\[i\]\[c\] 为只允许前 i 件、容量上限为 c 时的最大价值。第 0 行全为 0，因为没有物品时任何容量都可留空。对第 i−1 件，不选得到上一行同列；能放下时，选它得到上一行 c−weight 列加 value。两种情况覆盖所有方案，且选它后的剩余方案不能再含它。若剩余部分不是对应子问题的最优解，替换后会改进总方案，故可以取两项中的较大者。

物品行从小到大，每次只读上一行，所以本节容量列正向计算也安全。循环之前上一行已正确，分类转移得到当前行，最终 table\[n\]\[C\] 即所求。每一行单独创建，避免共享行。重量为零时仍读上一行同列：一个正价值零重量物品可加入一次，不会无限获利；负价值物品可以不选。容量为零的列也必须参与计算，不能一概固定为零。

示例三件物品的重量为 2、3、4，价值为 5、6、7，容量 6。处理前两件后，容量 5 和 6 都能取得 11；加入第三件后，容量 6 可由第一件与第三件取得 12。表的每格是容量上限答案，不保证恰好使用该重量。按整数运算单位成本计算，含初始化的时间与空间均为 O((n+1)(C+1))，即使没有物品也要创建一行。若 C 用二进制输入，表长取决于数值而非位数，这是伪多项式界。

**完整程序**

```python
def valid_items(weights, values, capacity, positive):
    if capacity < 0 or len(weights) != len(values):
        return False
    for weight in weights:
        if weight < 0 or (positive and weight == 0):
            return False
    return True

def knapsack_table(weights, values, capacity):
    if not valid_items(weights, values, capacity, False):
        return None
    table = []
    for i in range(len(weights) + 1):
        table.append([0] * (capacity + 1))
    for i in range(1, len(weights) + 1):
        weight = weights[i - 1]
        value = values[i - 1]
        for limit in range(capacity + 1):
            table[i][limit] = table[i - 1][limit]
            if weight <= limit:
                candidate = table[i - 1][limit - weight] + value
                if candidate > table[i][limit]:
                    table[i][limit] = candidate
    return table

for row in knapsack_table([2, 3, 4], [5, 6, 7], 6):
    print(row)
```

**预期输出**

```text
[0, 0, 0, 0, 0, 0, 0]
[0, 0, 5, 5, 5, 5, 5]
[0, 0, 5, 6, 6, 11, 11]
[0, 0, 5, 6, 7, 11, 12]
```


选题关联：来源主题 1（文末列出）。

## 恢复原位置：价值相同也要规定选择

最大价值只是一个数，实际使用时还要知道选了哪些物品。保留完整表以后，从状态 n、C 向前走。若当前值严格大于上一行同列，不选当前物品就达不到这个值，因此记录位置 i−1，并把剩余容量减去其重量；否则沿上一行同列走。每一步都把 i 减一，直到没有物品可检查。

相等时采用不选当前物品的规则。这给出确定的一种最优答案，不意味着最少件数、最轻总重量或字典序最小；这些是额外目标，需要另加比较规则。选中位置是倒序收集的，最后用切片反转成升序。返回的 indices 是原列表位置，不把重量当身份，因此能准确区分两个相同物品。weight 用原容量减去恢复后的剩余容量得到，可能小于容量上限。

示例加入零重量、价值 4 的物品。容量 3 时选位置 0 和 2，重量 3、价值 10；容量 0 时仍能选位置 0，价值 4。恢复循环不能写成“剩余容量为正才继续”，否则容量归零后尚未检查的零重量物品会被漏掉。这里严格下降的是物品前缀长度，不一定是容量。

检查结果要做三件事：下标合法且不重复，重量和满足上限，价值和等于最优值。仅验证最后一个数不能发现重复使用物品或位置错误。每次函数调用新建表和结果列表，原输入保持不变。空输入给出价值 0、重量 0 和空下标表；检测到长度不符、负容量或负重量则返回 None。恢复本身只需 O(n+1) 时间和 O(n+1) 输出空间，完整函数仍由二维表主导，不能因为恢复短就把总空间说成线性。

**完整程序**

```python
def valid_items(weights, values, capacity, positive):
    if capacity < 0 or len(weights) != len(values):
        return False
    for weight in weights:
        if weight < 0 or (positive and weight == 0):
            return False
    return True

def knapsack_table(weights, values, capacity):
    if not valid_items(weights, values, capacity, False):
        return None
    table = []
    for i in range(len(weights) + 1):
        table.append([0] * (capacity + 1))
    for i in range(1, len(weights) + 1):
        weight = weights[i - 1]
        value = values[i - 1]
        for limit in range(capacity + 1):
            table[i][limit] = table[i - 1][limit]
            if weight <= limit:
                candidate = table[i - 1][limit - weight] + value
                if candidate > table[i][limit]:
                    table[i][limit] = candidate
    return table

def knapsack_solution(weights, values, capacity):
    table = knapsack_table(weights, values, capacity)
    if table is None:
        return None
    selected = []
    limit = capacity
    i = len(weights)
    while i > 0:
        if table[i][limit] > table[i - 1][limit]:
            selected.append(i - 1)
            limit = limit - weights[i - 1]
        i = i - 1
    return {"value": table[len(weights)][capacity],
            "weight": capacity - limit, "indices": selected[::-1]}

print(knapsack_solution([0, 2, 3], [4, 5, 6], 3))
print(knapsack_solution([0, 2, 3], [4, 5, 6], 0))
```

**预期输出**

```text
{'value': 10, 'weight': 3, 'indices': [0, 2]}
{'value': 4, 'weight': 0, 'indices': [0]}
```


选题关联：来源主题 1（文末列出）。

## 压缩到一行：倒序保护上一轮的答案

如果只需要最大价值，可以把二维表压成 best\[c\]。处理当前物品之前，数组代表上一批物品的答案；希望更新之后，它代表增加当前物品的答案。对于正重量，容量从大到小走，读取的较小位置 c−weight 还没有被本轮更新，所以候选只含旧物品，再加入当前物品一次。这就是倒序的依据。

若正向处理一个重量 2、价值 5 的唯一物品，先把容量 2 的值改为 5，再在容量 4 读到这个新值，就会得到 10，相当于使用了两次。正确的一次使用答案仍为 5。方向不是由“背包”这个名称决定，而是由状态中允许使用的物品集合决定。

零重量需要单独理解。此时读写的是同一槽位，不存在更小容量；右侧表达式先读取该槽的旧值，再写入候选，每个槽在本轮只访问一次，因此一个正价值零重量物品仍恰好加一次。while 中的 limit 无论是否改善都会减一，所以重量为零也会终止。负价值候选不会压低当前值。

压缩以后，只保留最优数值，没有保存每个物品层的决定。不能在这个可覆盖数组里随便存一个容量前驱，就承诺还能恢复 0/1 方案：较小容量之后可能被改成包含同一物品的新状态。需要方案时，本章使用上一节的完整表。当前函数的表空间为 O(C+1)，时间可统一写为 O((n+1)(C+1))；输入检查也要扫描 n 件物品。例子第二次调用有重量 0 和 2、价值 3 和 5，容量 4，答案为 8，两个物品都只使用一次。

**完整程序**

```python
def valid_items(weights, values, capacity, positive):
    if capacity < 0 or len(weights) != len(values):
        return False
    for weight in weights:
        if weight < 0 or (positive and weight == 0):
            return False
    return True

def knapsack_01_value(weights, values, capacity):
    if not valid_items(weights, values, capacity, False):
        return None
    best = [0] * (capacity + 1)
    for i in range(len(weights)):
        limit = capacity
        while limit >= weights[i]:
            candidate = best[limit - weights[i]] + values[i]
            if candidate > best[limit]:
                best[limit] = candidate
            limit = limit - 1
    return best[capacity]

print(knapsack_01_value([2], [5], 4))
print(knapsack_01_value([0, 2], [3, 5], 4))
```

**预期输出**

```text
5
8
```


选题关联：来源主题 1（文末列出）。

## 完全背包：较小容量允许包含同类物品

现在把每个位置看成一种物品类型，每种有无限件。仍允许留空和不装满，但重量必须是正整数，价值仍可为任意整数。若存在零重量正价值类型，价值可以无限增长，有限最优值不存在；本实现为保持统一接口，拒绝所有零重量类型，也不尝试处理零重量非正价值的特殊分支。

定义 best\[c\] 为所有类型可重复使用、容量上限为 c 的最大价值。从任意非空方案中拿掉一件类型 i，余下部分的重量不超过 c−weights\[i\]，所以候选为 best\[c−weights\[i\]\] 加 values\[i\]；空方案价值 0 也是候选。遍历容量 1 到 C，内部枚举所有放得下的类型。正重量保证依赖容量严格更小，已经算完，而且允许其中再次出现类型 i。

这段程序没有物品层。容量正序是为保证所有较小容量已完成，不要把它与上一节每种物品单独更新一轮混为一谈。也可用物品外层、容量正序表达完全背包，但必须重新说明行的含义。本例容量 7、重量 2 和 3、价值 5 和 6，最优可取 2、2、3，价值 16。

last\[c\] 记录最后加入的类型，仅在严格改善时覆盖。恢复时重复读取并减去正重量，直到 last 为 None；没有后继表示剩余容量选择空方案，不要求容量恰好归零。相同价值保留先遇到的类型；全负价值时返回价值 0 和空方案。类型下标允许重复，这正是与 0/1 接口的区别。含输入检查、初始化和恢复的时间为 O((n+1)(C+1))，表与返回结果空间 O(C+1)。大容量仍可能无法建表，压缩并没有消除伪多项式限制。

**完整程序**

```python
def valid_items(weights, values, capacity, positive):
    if capacity < 0 or len(weights) != len(values):
        return False
    for weight in weights:
        if weight < 0 or (positive and weight == 0):
            return False
    return True

def knapsack_unbounded(weights, values, capacity):
    if not valid_items(weights, values, capacity, True):
        return None
    best = [0] * (capacity + 1)
    last = [None] * (capacity + 1)
    for limit in range(1, capacity + 1):
        for i in range(len(weights)):
            if weights[i] <= limit:
                candidate = best[limit - weights[i]] + values[i]
                if candidate > best[limit]:
                    best[limit] = candidate
                    last[limit] = i
    selected = []
    limit = capacity
    while last[limit] is not None:
        i = last[limit]
        selected.append(i)
        limit = limit - weights[i]
    return {"value": best[capacity], "weight": capacity - limit,
            "indices": selected}

print(knapsack_unbounded([2, 3], [5, 6], 7))
print(knapsack_unbounded([0], [5], 0))
print(knapsack_unbounded([2], [-1], 5))
```

**预期输出**

```text
{'value': 16, 'weight': 7, 'indices': [0, 0, 1]}
None
{'value': 0, 'weight': 0, 'indices': []}
```


选题关联：来源主题 1（文末列出）。

## 恰好装满：不可达不能冒充零价值

回到每个位置最多一次，但要求重量和恰好为 C。定义 table\[i\]\[s\] 为前 i 件恰好达到重量 s 的最大价值。没有物品时只有重量 0 可达，因此只把 table\[0\]\[0\] 设为 0，其余为 None。如果把所有格都初始化成 0，就会给未凑出的重量虚构一个零价值方案。

不选的候选仍来自上一行同列；选的候选只有在上一行 s−weight 可达时才存在。当前不可达，或者候选严格更大，才写入新值并把 take 标记为 True。合法答案可以是负数，不能用正负或真假判断是否存在。例如重量 2 和 3、价值 −4 和 5，目标 2 的唯一方案价值为 −4；目标 4 无法恰好凑出，返回 None。

每一行只读前一行，所以零重量正价值可选一次，零重量负价值可不选，零重量零价值在最优值平局时不选。take 把当前层的决定保留下来，恢复仍每次减少物品数，即使容量不变也能终止。恰好目标 0 的空输入返回价值 0 和空列表，这是一个可行空方案，不是没有方案。

对合法输入，None 专门说明无法恰好装满；函数也沿用对范围或长度错误返回 None 的教学接口，调用方需先确认输入契约才能区分两种原因。完整函数时间、表和标记空间均为 O((n+1)(C+1))。本节与容量上限版看似只改初值，实际上状态集合也改变了：前者允许总重量小于目标，后者只能保留完全相等的方案。后面的计数练习还会再次改变“一个格子存什么”，不能把最大值转移直接当作方案数相加。

**完整程序**

```python
def valid_items(weights, values, capacity, positive):
    if capacity < 0 or len(weights) != len(values):
        return False
    for weight in weights:
        if weight < 0 or (positive and weight == 0):
            return False
    return True

def knapsack_exact(weights, values, capacity):
    if not valid_items(weights, values, capacity, False):
        return None
    table = []
    take = []
    for i in range(len(weights) + 1):
        table.append([None] * (capacity + 1))
        take.append([False] * (capacity + 1))
    table[0][0] = 0
    for i in range(1, len(weights) + 1):
        weight = weights[i - 1]
        for total in range(capacity + 1):
            table[i][total] = table[i - 1][total]
            if weight <= total and table[i - 1][total - weight] is not None:
                candidate = table[i - 1][total - weight] + values[i - 1]
                if table[i][total] is None or candidate > table[i][total]:
                    table[i][total] = candidate
                    take[i][total] = True
    if table[len(weights)][capacity] is None:
        return None
    selected = []
    total = capacity
    i = len(weights)
    while i > 0:
        if take[i][total]:
            selected.append(i - 1)
            total = total - weights[i - 1]
        i = i - 1
    return {"value": table[len(weights)][capacity], "indices": selected[::-1]}

print(knapsack_exact([2, 3], [-4, 5], 2))
print(knapsack_exact([2, 3], [-4, 5], 4))
print(knapsack_exact([], [], 0))
```

**预期输出**

```text
{'value': -4, 'indices': [0]}
None
{'value': 0, 'indices': []}
```


选题关联：来源主题 1（文末列出）。

<a id="examples"></a>

## 跟着做：原创例题

### 例题 1

三件物品重量 \[2,3,4\]、价值 \[5,6,7\]，容量 6。比较按价值重量比贪心、0/1 最优和允许重复时的最优，并给出可核对的方案。

1. 比值依次为 2.5、2、1.75；按此顺序装入前两件，重量为 5、价值为 11，剩余容量放不下第三件。
2. 0/1 情形枚举单件和可放下的两件：位置 0 与 2 的重量为 6、价值为 12，优于位置 0 与 1。
3. 允许重复后，三件重量 2 的同类物品恰好占满，价值为 15；返回下标 0 重复三次。
4. 逐一把返回下标映射回重量与价值，检查 0/1 方案无重复，而完全背包允许重复。

**结果与核对**

两个最优值分别为 12 和 15。比值贪心的 11 是可行但次优的 0/1 答案；它的失败不否定其他问题中已经证明的贪心规则。完整程序调用各自模型的求解函数；返回一种方案不代表已经枚举所有最优方案。测试用位置子集和各类型件数的独立枚举检查最优值。

**完整程序**

```python
def valid_items(weights, values, capacity, positive):
    if capacity < 0 or len(weights) != len(values):
        return False
    for weight in weights:
        if weight < 0 or (positive and weight == 0):
            return False
    return True

def knapsack_table(weights, values, capacity):
    if not valid_items(weights, values, capacity, False):
        return None
    table = []
    for i in range(len(weights) + 1):
        table.append([0] * (capacity + 1))
    for i in range(1, len(weights) + 1):
        weight = weights[i - 1]
        value = values[i - 1]
        for limit in range(capacity + 1):
            table[i][limit] = table[i - 1][limit]
            if weight <= limit:
                candidate = table[i - 1][limit - weight] + value
                if candidate > table[i][limit]:
                    table[i][limit] = candidate
    return table

def knapsack_solution(weights, values, capacity):
    table = knapsack_table(weights, values, capacity)
    if table is None:
        return None
    selected = []
    limit = capacity
    i = len(weights)
    while i > 0:
        if table[i][limit] > table[i - 1][limit]:
            selected.append(i - 1)
            limit = limit - weights[i - 1]
        i = i - 1
    return {"value": table[len(weights)][capacity],
            "weight": capacity - limit, "indices": selected[::-1]}

def knapsack_unbounded(weights, values, capacity):
    if not valid_items(weights, values, capacity, True):
        return None
    best = [0] * (capacity + 1)
    last = [None] * (capacity + 1)
    for limit in range(1, capacity + 1):
        for i in range(len(weights)):
            if weights[i] <= limit:
                candidate = best[limit - weights[i]] + values[i]
                if candidate > best[limit]:
                    best[limit] = candidate
                    last[limit] = i
    selected = []
    limit = capacity
    while last[limit] is not None:
        i = last[limit]
        selected.append(i)
        limit = limit - weights[i]
    return {"value": best[capacity], "weight": capacity - limit,
            "indices": selected}

print(knapsack_solution([2, 3, 4], [5, 6, 7], 6))
print(knapsack_unbounded([2, 3, 4], [5, 6, 7], 6))
```

**预期输出**

```text
{'value': 12, 'weight': 6, 'indices': [0, 2]}
{'value': 15, 'weight': 6, 'indices': [0, 0, 0]}
```


### 例题 2

物品重量 \[0,2,3\]、价值 \[4,−3,2\]，每件最多一次。分别求恰好重量 5、容量上限 5 和恰好重量 1 的结果，并说明负价值和零重量的作用。

1. 恰好达到 5 必须选重量 2 与 3 的物品，它们价值和为 −1，不能因其中一件价值负就直接删掉。
2. 加入零重量、价值 4 的物品后，重量仍为 5，最优价值升到 3，选中全部三个位置。
3. 若只要求不超过 5，可不选负价值物品，只选位置 0 与 2，重量 3、价值 6。
4. 所有位置子集的重量只有 0、2、3、5，不存在重量 1，第三个问题返回 None。

**结果与核对**

恰好装满的约束可能迫使答案使用负价值物品，容量上限版则可以留出空间。恢复必须继续检查零重量位置，不能在剩余容量变零时直接结束。程序不修改输入，三次调用的结果彼此独立；应对重量条件和价值分别核对，不能只比较两个最优数值的大小。

**完整程序**

```python
def valid_items(weights, values, capacity, positive):
    if capacity < 0 or len(weights) != len(values):
        return False
    for weight in weights:
        if weight < 0 or (positive and weight == 0):
            return False
    return True

def knapsack_table(weights, values, capacity):
    if not valid_items(weights, values, capacity, False):
        return None
    table = []
    for i in range(len(weights) + 1):
        table.append([0] * (capacity + 1))
    for i in range(1, len(weights) + 1):
        weight = weights[i - 1]
        value = values[i - 1]
        for limit in range(capacity + 1):
            table[i][limit] = table[i - 1][limit]
            if weight <= limit:
                candidate = table[i - 1][limit - weight] + value
                if candidate > table[i][limit]:
                    table[i][limit] = candidate
    return table

def knapsack_solution(weights, values, capacity):
    table = knapsack_table(weights, values, capacity)
    if table is None:
        return None
    selected = []
    limit = capacity
    i = len(weights)
    while i > 0:
        if table[i][limit] > table[i - 1][limit]:
            selected.append(i - 1)
            limit = limit - weights[i - 1]
        i = i - 1
    return {"value": table[len(weights)][capacity],
            "weight": capacity - limit, "indices": selected[::-1]}

def knapsack_exact(weights, values, capacity):
    if not valid_items(weights, values, capacity, False):
        return None
    table = []
    take = []
    for i in range(len(weights) + 1):
        table.append([None] * (capacity + 1))
        take.append([False] * (capacity + 1))
    table[0][0] = 0
    for i in range(1, len(weights) + 1):
        weight = weights[i - 1]
        for total in range(capacity + 1):
            table[i][total] = table[i - 1][total]
            if weight <= total and table[i - 1][total - weight] is not None:
                candidate = table[i - 1][total - weight] + values[i - 1]
                if table[i][total] is None or candidate > table[i][total]:
                    table[i][total] = candidate
                    take[i][total] = True
    if table[len(weights)][capacity] is None:
        return None
    selected = []
    total = capacity
    i = len(weights)
    while i > 0:
        if take[i][total]:
            selected.append(i - 1)
            total = total - weights[i - 1]
        i = i - 1
    return {"value": table[len(weights)][capacity], "indices": selected[::-1]}

print(knapsack_exact([0, 2, 3], [4, -3, 2], 5))
print(knapsack_solution([0, 2, 3], [4, -3, 2], 5))
print(knapsack_exact([0, 2, 3], [4, -3, 2], 1))
```

**预期输出**

```text
{'value': 3, 'indices': [0, 1, 2]}
{'value': 6, 'weight': 3, 'indices': [0, 2]}
None
```


<a id="practice"></a>

## 自己做：先完成再看解答

### 练习 1

统计重量 \[0,2,2,3\] 中恰好和为 4 的位置子集数，每个位置最多使用一次；再求 \[0,0\]、目标 0 和空列表、目标 0 的结果。

<details>
<summary>提示</summary>

ways\[s\] 存数量，初始只有空子集使和为零。按位置处理并倒序更新，当前位置的选与不选是两类不同方案。

</details>

<details>
<summary>解答与检查</summary>

目标 4 必须选两个重量 2 的位置，零重量位置可选可不选，因此有 2 个子集；两个零的目标 0 有 4 个，空输入有 1 个空子集。零重量使每格原值加自身，正好为每个已有子集提供选与不选两种扩展。重复重量仍按位置区分，不先去重。负重量或目标拒绝。时间 O((n+1)(T+1))、表空间 O(T+1)，按单位整数运算分析；方案数可能指数大，其存储和加法位成本还需另算。

**完整程序**

```python
def count_01_subsets(weights, target):
    if target < 0:
        return None
    for weight in weights:
        if weight < 0:
            return None
    ways = [0] * (target + 1)
    ways[0] = 1
    for weight in weights:
        total = target
        while total >= weight:
            ways[total] = ways[total] + ways[total - weight]
            total = total - 1
    return ways[target]

print(count_01_subsets([0, 2, 2, 3], 4))
print(count_01_subsets([0, 0], 0))
print(count_01_subsets([], 0))
```

**预期输出**

```text
2
4
1
```


</details>

### 练习 2

面额 \[1,3,4\] 每种可用无限枚，凑出 6，按各面额使用件数统计组合，不区分摆放顺序。返回组合数，并处理空面额、零目标以及重复面额输入。

<details>
<summary>提示</summary>

外层逐种面额，内层金额正序；处理某面额后，数组只包含已处理面额的件数组合。

</details>

<details>
<summary>解答与检查</summary>

四种组合是六枚 1、三枚 1 加一枚 3、两枚 3、两枚 1 加一枚 4。ways\[0\] 为 1，每种组合由当前类型的件数唯一描述，金额正序允许再次使用当前类型。本接口要求面额正且互不重复；重复输入返回 None，避免把同面额误当不同颜色的硬币。空面额与零目标返回 1。逐对查重耗时 O(k²)，加上填表总时间 O(k²+(k+1)(T+1))，空间 O(T+1)；不能漏算验证成本。

**完整程序**

```python
def valid_coins(coins, target):
    if target < 0:
        return False
    for i in range(len(coins)):
        if coins[i] <= 0:
            return False
        for j in range(i):
            if coins[j] == coins[i]:
                return False
    return True

def coin_combinations(coins, target):
    if not valid_coins(coins, target):
        return None
    ways = [0] * (target + 1)
    ways[0] = 1
    for coin in coins:
        for total in range(coin, target + 1):
            ways[total] = ways[total] + ways[total - coin]
    return ways[target]

print(coin_combinations([1, 3, 4], 6))
print(coin_combinations([], 0))
print(coin_combinations([1, 1], 2))
```

**预期输出**

```text
4
1
None
```


</details>

### 练习 3

沿用 \[1,3,4\] 凑出 6，但把 \[1,1,4\] 与 \[4,1,1\] 看作不同有序序列。求数量，解释为何交换循环后不再回答上一题，并检查空序列。

<details>
<summary>提示</summary>

按最后一枚硬币分类。固定金额后，枚举最后的面额，把较小金额的全部序列各追加这一枚。

</details>

<details>
<summary>解答与检查</summary>

结果为 9：全 1 有 1 种，一枚 3 与三枚 1 有 4 种，两枚 3 有 1 种，一枚 4 与两枚 1 有 3 种。以最后一枚分类互不重叠且完整，所以金额外层、面额内层把顺序纳入方案身份。上一题组合数仍为 4。零目标有一种空序列；正面额保证长度有限，不允许零面额无限插入。验证、时间与空间界和上一题相同，但计数可更大。本题代码同时打印两种答案，要求先解释计数对象再看输出。

**完整程序**

```python
def valid_coins(coins, target):
    if target < 0:
        return False
    for i in range(len(coins)):
        if coins[i] <= 0:
            return False
        for j in range(i):
            if coins[j] == coins[i]:
                return False
    return True

def coin_combinations(coins, target):
    if not valid_coins(coins, target):
        return None
    ways = [0] * (target + 1)
    ways[0] = 1
    for coin in coins:
        for total in range(coin, target + 1):
            ways[total] = ways[total] + ways[total - coin]
    return ways[target]

def coin_sequences(coins, target):
    if not valid_coins(coins, target):
        return None
    ways = [0] * (target + 1)
    ways[0] = 1
    for total in range(1, target + 1):
        for coin in coins:
            if coin <= total:
                ways[total] = ways[total] + ways[total - coin]
    return ways[target]

print(coin_combinations([1, 3, 4], 6))
print(coin_sequences([1, 3, 4], 6))
print(coin_sequences([], 0))
```

**预期输出**

```text
4
9
1
```


</details>

<a id="pitfalls"></a>

## 容易混淆的地方

- **把所有背包的第零列都固定为零，忽略零重量物品。** 0/1 模型中零重量正价值物品可选一次，容量零列也要更新；完全背包统一拒绝零重量。
- **容量上限与恰好重量都用全零数组初始化。** 恰好模型中除重量零外的初始状态不可达，用 None 区分；合法最优价值可以为负数。
- **交换循环只是改写代码，组合数和序列数一定相同。** 外层含义决定最后按什么分类：按面额件数或按最后一枚，得到的方案身份不同。

<a id="self-check"></a>

## 离开这一章前

- [ ] 用一个重量 2、价值 5 的物品手算正序误用两次的过程。
- [ ] 为容量零和两个零重量物品分别写出最优值与位置子集数。
- [ ] 重新计算例题的返回下标对应的重量、价值及使用次数。
- [ ] 说明容量大而物品少时，为什么压缩数组仍可能不可行。

## 本章边界

- 仅讨论整数容量；类型作为前提，不提供任意输入的解析或异常处理。容量上限允许空选，完全背包要求正重量。
- 未覆盖有件数上限的多重背包、分组背包、多资源背包、近似算法及全部最优方案枚举。
- 复杂度按整数操作单位成本给出；大整数位成本、输出打印和资源限制需另计。来源入口仅关联选题，程序和例题为原创。

## 选题来源与覆盖

来源含学生报告时，仅将其作为选题线索；具体机制仍需结合后续实验或权威资料核对。

- [大一小学期/Week\_3-Python/docs/readme.md](https://github.com/PKUanonym/REKCARC-TSC-UHT/blob/37cd19f7a9fb80dc846a7016b3fd482ed5fe7cc0/%E5%A4%A7%E4%B8%80%E5%B0%8F%E5%AD%A6%E6%9C%9F/Week_3-Python/docs/readme.md)（已提取可读文本，固定版本 37cd19f7a9fb）
- 主题 1：Python 基础语法的外部学习入口；位置：第 41–80 行。
- 主题 2：从基础语法到工具与应用的建议阅读顺序；位置：第 121–160 行。

## 参考资料与规则核对

上游入口用于确定学习方向；下面的参考资料用于核对语言语义、数据结构或算法分析规则，例题和练习由本项目重新设计。

- [Stanford CS161：背包的两种使用次数模型](https://web.stanford.edu/class/archive/cs/cs161/cs161.1172/CS161Lecture13.pdf)：仅核对一次使用、无限使用与容量状态的模型；本章另行设计零重量、负价值、平局和恢复接口，题目、代码与数值原创。
- [Algorithms for Competitive Programming：背包的更新顺序](https://cp-algorithms.com/dynamic_programming/knapsack.html)：核对压缩状态与使用次数的关系；未移植页面例题、练习或 C++ 代码，本章完全背包采用容量外层并保存最后类型。
- [MIT 6.006：背包与伪多项式时间](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/3484e876d81aba07911a1109f5b5e81e_MIT6_006F11_lec21.pdf)：仅引用背包与数值编码长度部分，核对伪多项式概念；第 29 章的单位编辑距离模型另按 NIST 定义核对。

**继续学习**：先独立完成自测，再记录仍需回读的步骤。

[上一章：保存子问题的答案：动态规划入门](27-dynamic-programming.md) · [下一章：对齐两个前缀：序列动态规划与方案恢复](29-sequence-dp.md)

[教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [哈希表与图练习指引](../hash-graphs-practice.md) · [拓扑排序与带权图练习指引](../weighted-graphs-practice.md) · [记录自己的学习](../learning-log-template.md)
