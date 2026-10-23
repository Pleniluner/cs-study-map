# 证明眼前选择的正确性：贪心算法与交换论证

[返回教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [哈希表与图练习指引](../hash-graphs-practice.md) · [拓扑排序与带权图练习指引](../weighted-graphs-practice.md)

[上一章：枚举选择并排除无解分支：回溯与搜索剪枝](25-backtracking.md) · [下一章：保存子问题的答案：动态规划入门](27-dynamic-programming.md)

[学习目标](#objectives) · [需要的基础](#prerequisites) · [例题](#examples) · [练习](#practice) · [自测](#self-check)

状态：**AI 初稿，可开始试学**。生成模型：Codex 当前会话（未记录具体模型型号）。

本章围绕资料中识别到的知识点重新编写；讲解、数值模型、例题与练习为 AI 原创组织，不是原课程题目或答案。主题出处只说明选题关联，不证明全部推导已经正确。

回溯保留多种可能，贪心则在每一步作出一个选择并继续向前。它吸引人的地方是过程简洁，但“眼前最好”并不自动推出整体最优。本章把目标函数、可行条件和正确性论证放在一起：先用找零反例说明边界，再证明最早结束的区间安排，随后理解最小合并与 Huffman。最后用删除区间、区间选点和截止时间练习迁移证明方法。

<a id="objectives"></a>

## 学完要能做到

- 明确贪心规则优化的是哪个目标，能用小反例否定不成立的规则。
- 用交换论证或保持领先说明某个最优解可以包含当前选择。
- 解释合并树的加权叶深与总合并费用的关系。
- 按实际排序和选择实现分析成本，不套用其他版本的复杂度。

<a id="prerequisites"></a>

## 需要的基础

- 第 10–12 章的复杂度、排序、稳定性与半开区间。
- 第 16–18、24 章的树、优先队列与 MST 交换思想。
- 第 25 章的枚举和小规模穷举验证。

## 先检查规则：最大的硬币不一定最好

一个优化问题至少要写出可行解和比较标准。找零例子允许每种正整数面额无限使用，要求总额恰好等于 amount，并最小化硬币枚数。贪心规则是每次取不超过剩余金额的最大面额，直到不能继续。程序返回已取面额列表和余款，余款非零只能说明这条贪心路线失败，不能证明原问题无解。

对面额 \[1,4,6\] 和金额 8，贪心先取 6，再取两个 1，共三枚；两个 4 只需两枚。若去掉面额 1，贪心取 6 后剩 2，仍然不能否定两个 4 的方案。这两个检查分别指出“能凑出但不最少”和“贪心失败但原问题有解”，不能把不同失败混在一起。

ordered 是第 12 章插入排序的副本形式，不改变输入；这里按升序排列，再从尾部取大面额。代码的目标是展示策略并保留可核查的选择过程。面额必须为正整数，零会导致重复取零而不能前进，负数会增大余款，因此显式拒绝；金额为负也返回 None。空面额对金额 0 成功，对正金额留下全部余款。重复面额不会改变这个策略的选择结果。

设面额项数为 k，实际取出 q 枚。插入排序最坏 O(k²)，随后遍历面额并输出硬币为 O(k+q)，总时间 O(k²+k+q+1)，空间 O(k+q+1)。某些面额系统能证明贪心最优，但必须另给依据。本章不会因为几组测试成功就推广到任意面额；下一章用动态规划解决一般正整数面额的最少枚数。

**完整程序**

```python
def ordered(values):
    result = values.copy()
    for index in range(1, len(result)):
        saved = result[index]
        position = index
        while position > 0 and result[position - 1] > saved:
            result[position] = result[position - 1]
            position = position - 1
        result[position] = saved
    return result

def greedy_change(coins, amount):
    if amount < 0:
        return None
    for coin in coins:
        if coin <= 0:
            return None
    values = ordered(coins)
    selected = []
    remaining = amount
    for index in range(len(values) - 1, -1, -1):
        coin = values[index]
        while remaining >= coin:
            remaining = remaining - coin
            selected.append(coin)
    return {"coins": selected, "remaining": remaining}

print(greedy_change([1, 4, 6], 8))
print(greedy_change([4, 6], 8))
print(greedy_change([], 0))
```

**预期输出**

```text
{'coins': [6, 1, 1], 'remaining': 0}
{'coins': [6], 'remaining': 2}
{'coins': [], 'remaining': 0}
```


选题关联：来源主题 1（文末列出）。

## 区间调度：先选结束最早的兼容任务

现在每个任务占据半开时间区间 \[start,finish)，规定 start 严格小于 finish，整数时间可以为负。只有一台资源，不能同时执行重叠任务，目标是选出数量最多的一组任务，每个任务价值相同。前一任务结束时后一任务可以立刻开始，所以兼容条件使用开始时间大于或等于上次结束时间。

为每个输入区间构造 \[结束时间,开始时间,原下标\] 记录，再用 ordered 排序。列表比较按从左到右的首个不同元素决定次序，因而先按结束时间，再按开始时间和下标打破平局。返回原下标保留任务身份；相同区间的两条输入仍是不同任务，但有正时长的相同区间不能同时选中。排序只移动新建记录，不修改原输入。

扫描时维护 last\_finish。它最初为 None，表示尚未选过任务，不能初始化为 0，否则会错过负时间区间。每遇到兼容任务就接受并更新结束时间，不兼容则跳过。这个规则让当前完成时刻尽早，为后面的任务保留最多可能空间。直觉还不是证明，下一节说明为什么可以把某个最优解的第一项换成它。

本章拒绝零长和倒置区间，避免把无占用任务的不同约定混入证明；空输入返回 \[\]。由于手写的是插入排序，总时间最坏 O(n²+n+1)，排序后扫描本身是 O(n+1)，空间 O(n+1)。使用更快排序可以降低排序部分，但不能把该版本直接写成 O(n log n)。若任务具有不同收益，最大数量不再等价于最大收益，本规则便没有这里的最优保证。

**完整程序**

```python
def ordered(values):
    result = values.copy()
    for index in range(1, len(result)):
        saved = result[index]
        position = index
        while position > 0 and result[position - 1] > saved:
            result[position] = result[position - 1]
            position = position - 1
        result[position] = saved
    return result

def interval_schedule(intervals):
    records = []
    for index in range(len(intervals)):
        start = intervals[index][0]
        finish = intervals[index][1]
        if start >= finish:
            return None
        records.append([finish, start, index])
    records = ordered(records)
    chosen = []
    last_finish = None
    for record in records:
        if last_finish is None or record[1] >= last_finish:
            chosen.append(record[2])
            last_finish = record[0]
    return chosen

print(interval_schedule([[0, 4], [1, 2], [2, 3], [3, 5]]))
print(interval_schedule([[-4, -2], [-2, 0]]))
print(interval_schedule([[1, 1]]))
```

**预期输出**

```text
[1, 2, 3]
[0, 1]
None
```


选题关联：来源主题 1（文末列出）。

## 交换与保持领先：证明不能只检查一个输出

设贪心选出的第一项是 g，某个最优排程按时间排列后的第一项是 o。由于 g 的结束时间不晚于 o，原来能放在 o 后面的所有任务，也能放在 g 后面。把 o 换成 g，任务数不减少、兼容性不破坏，因此存在一个同样最优且以 g 开始的方案。固定 g 后，余下问题就是在它结束之后安排最多任务，条件与原问题相同，可以反复应用这个论证。

另一种表述是保持领先：比较贪心与任意可行排程的第 i 个结束时刻。第一项贪心结束不晚；若前 i 项成立，另一排程的第 i+1 项在贪心第 i 项后也可安排，贪心会选一个结束不更晚的候选。因此只要另一方案还有第 i+1 项，贪心就不会提前无路可选，最终数量不会更少。

下面的 valid\_schedule 只核验给定下标序列是否互异、有效且按执行次序兼容。它可以证明输出可行，却无法单独证明数量最优。例子把 \[0,2\] 的第一项换成结束更早的 1，得到 \[1,2\]，两者都是两项可行排程。这个数值例子帮助观察交换，真正覆盖所有输入的是前面的论证。

证明依赖相同收益、单资源、非抢占及任务区间已固定。若目标改成总收益或有额外先后约束，替换任务可能损失价值或破坏关系，必须重新建模。测试时可枚举小输入的所有子集，筛出兼容组比较最大数量；证明与独立穷举互相补充，二者都不同于仅比较自己写的两个相似循环。

**完整程序**

```python
def valid_schedule(intervals, order):
    used = [False] * len(intervals)
    last_finish = None
    for index in order:
        if index < 0 or index >= len(intervals) or used[index]:
            return False
        start = intervals[index][0]
        finish = intervals[index][1]
        if start >= finish or (last_finish is not None and start < last_finish):
            return False
        used[index] = True
        last_finish = finish
    return True

intervals = [[0, 4], [1, 3], [4, 6]]
print(valid_schedule(intervals, [0, 2]))
print(valid_schedule(intervals, [1, 2]))
print(valid_schedule(intervals, [1, 1]))
print(valid_schedule(intervals, [2, 1]))
```

**预期输出**

```text
True
True
False
False
```


选题关联：来源主题 1（文末列出）。

## 最小合并成本：把最小两项先合起来

有若干非负整数大小的数据块，每次只能合并两块，费用规定为两块大小之和，合并后形成同样大小的新块。目标是让所有块最终合成一块时的累计费用最小；这里模拟大小和费用，不实际读写数据。反复取当前最小的两块，记录本次费用，再把和放回候选表，就是最小合并策略。

任意完整合并过程都能画成一棵满二叉树：原始块是叶子，每次合并产生一个父结点。每个叶子的大小会在从该叶到根的每次合并中被计费一次，所以总费用等于各叶子大小乘其深度再求和。较小权重放在更深处不会增加这个和，这是交换证明的入口。

一棵满二叉树的最深叶子有同深度的叶子兄弟。可以把两个最小权重移到这两个兄弟位置；与较浅处的较大权重交换时，加权深度不增加，因此存在这样布局的最优树。将这两个叶子收缩成一个权重为它们之和的叶子，原目标恰比收缩后多一个固定的合并费用。剩下仍是同类问题，归纳得到反复合并最小两项的正确性。

pop\_smallest 每次线性扫描并删除一个最小值，平局保留先遇到的项。整个过程共 n−1 次合并，选择和列表搬移最坏累计 O(n²+n+1) 时间，候选与轨迹为 O(n+1) 空间；这里未使用堆，不声称 O(n log n)。空输入和单块无需合并，费用为 0；零大小允许，负大小拒绝。若费用公式改变，或必须按原有相邻次序合并，这份证明不能直接使用。

**完整程序**

```python
def pop_smallest(values):
    best = 0
    for index in range(1, len(values)):
        if values[index] < values[best]:
            best = index
    return values.pop(best)

def optimal_merge(weights):
    for weight in weights:
        if weight < 0:
            return None
    queue = weights.copy()
    cost = 0
    merges = []
    while len(queue) > 1:
        first = pop_smallest(queue)
        second = pop_smallest(queue)
        total = first + second
        cost = cost + total
        merges.append([first, second, total])
        queue.append(total)
    return {"cost": cost, "merges": merges}

print(optimal_merge([3, 5, 8, 11]))
print(optimal_merge([9]))
print(optimal_merge([]))
```

**预期输出**

```text
{'cost': 51, 'merges': [[3, 5, 8], [8, 8, 16], [11, 16, 27]]}
{'cost': 0, 'merges': []}
{'cost': 0, 'merges': []}
```


选题关联：来源主题 1（文末列出）。

## Huffman：由合并树得到前缀码

若各符号出现次数已知，给频繁符号较短编码可能减少总位数，但编码还必须能区分。前缀码要求任何符号的码字都不是另一码字的前缀。把符号放在二叉树的叶子上，左边记 0、右边记 1，从根到叶的边序列就是码字；一个叶子不可能是另一个叶子的祖先，因此满足前缀条件。

权重是符号的正整数出现次数，目标为各权重乘码长之和。它与上一节的加权叶深完全相同，所以反复合并最轻的两棵树便得到最优的二进制符号前缀码。程序给每个符号保留原下标，候选森林中存完整树结点；合并后再深度优先遍历，用 path.copy() 把每个叶子的码字写回原位置。

同权重时可能有多棵最优树和多套码字。这里只要求前缀性质与最小加权长度，不能要求所有实现逐位一致。我们的线性扫描选择规则使结果可重复，先弹出的树放左边。输入为空返回 \[\]；零频或负频被拒绝，调用者可以先明确删除未出现的符号。仅有一个符号时按树模型返回空码字，其加权长度为 0；真实传输还必须另存符号数，否则无法知道重复次数。

树有 O(n+1) 个结点，码字总长度记为 L。线性取最小产生 O(n²+n+1) 时间，生成码字另需 O(L+1)，保存森林、树、递归路径和输出为 O(n+L+1) 空间。树可能很高，所以 L 可能达到平方量级，不能说保存所有码字总是线性。本节不计算码表、消息长度和文件头的开销，也不声称每个短文件经这种编码后都会缩小。

**完整程序**

```python
def pop_lightest(forest):
    best = 0
    for index in range(1, len(forest)):
        if forest[index]["weight"] < forest[best]["weight"]:
            best = index
    return forest.pop(best)

def huffman_codes(weights):
    forest = []
    for symbol in range(len(weights)):
        if weights[symbol] <= 0:
            return None
        forest.append({"weight": weights[symbol], "symbol": symbol,
                       "left": None, "right": None})
    if len(forest) == 0:
        return []
    while len(forest) > 1:
        left = pop_lightest(forest)
        right = pop_lightest(forest)
        forest.append({"weight": left["weight"] + right["weight"], "symbol": None,
                       "left": left, "right": right})
    codes = [None] * len(weights)
    path = []
    def visit(node):
        if node["symbol"] is not None:
            codes[node["symbol"]] = path.copy()
            return
        path.append(0)
        visit(node["left"])
        path.pop()
        path.append(1)
        visit(node["right"])
        path.pop()
    visit(forest[0])
    return codes

print(huffman_codes([2, 5, 9]))
print(huffman_codes([4]))
print(huffman_codes([]))
```

**预期输出**

```text
[[0, 0], [0, 1], [1]]
[[]]
[]
```


选题关联：来源主题 1（文末列出）。

<a id="examples"></a>

## 跟着做：原创例题

### 例题 1

检验两个看似合理的区间规则：最早开始优先，以及最短持续时间优先。分别对 \[\[0,10\],\[1,3\],\[3,5\],\[5,7\]\] 和 \[\[0,3\],\[3,6\],\[2,4\]\] 给出反例与正确最大数量。

1. 第一组最早开始会先取 \[0,10)，它与其余任务都重叠，只能选一项。
2. 按结束时间选择 \[1,3)、\[3,5)、\[5,7)，得到三项。
3. 第二组最短任务是 \[2,4)，选后另外两项都不能加入，只得一项。
4. 选择 \[0,3) 和 \[3,6) 得到两项，结束相接在半开区间约定下合法。

**结果与核对**

反例只需给出一个输入和更好的可行解，就足以否定某条普遍最优断言。最早结束规则有上一节的交换证明，因此不是从两个样例猜出来的。第一组目标值为 3，第二组为 2；程序返回原任务下标，便于核对区间身份。若改为带收益任务，则需要新的模型，本例中的任务数量结论不直接说明收益最优。

**完整程序**

```python
def ordered(values):
    result = values.copy()
    for index in range(1, len(result)):
        saved = result[index]
        position = index
        while position > 0 and result[position - 1] > saved:
            result[position] = result[position - 1]
            position = position - 1
        result[position] = saved
    return result

def interval_schedule(intervals):
    records = []
    for index in range(len(intervals)):
        start = intervals[index][0]
        finish = intervals[index][1]
        if start >= finish:
            return None
        records.append([finish, start, index])
    records = ordered(records)
    chosen = []
    last_finish = None
    for record in records:
        if last_finish is None or record[1] >= last_finish:
            chosen.append(record[2])
            last_finish = record[0]
    return chosen

print(interval_schedule([[0, 10], [1, 3], [3, 5], [5, 7]]))
print(interval_schedule([[0, 3], [3, 6], [2, 4]]))
```

**预期输出**

```text
[1, 2, 3]
[0, 1]
```


### 例题 2

四个符号的频数依次为 \[3,5,8,11\]。给出本实现的 Huffman 码字，核对加权码长等于三次合并费用之和。

1. 先合并频数 3 和 5，产生权重 8 的内部结点，费用为 8。
2. 原来的符号 8 与新结点 8 合并为 16，费用为 16。
3. 剩余符号 11 与结点 16 合并为 27，费用为 27，累计 51。
4. 按先弹出放左的规则，四个符号码字依次为 110、111、10、0，长度为 3、3、2、1。

**结果与核对**

加权码长为 3×3+5×3+8×2+11×1=51，与 8+16+27 相等。检查没有一个码字是另一个的前缀，才能确认可以逐个符号解码。交换左右子树可能改变具体比特，但不会改变码长或总代价。这里得到的是理想符号编码的最小数据位数；真实文件还需码表等元信息。程序同时计算两种形式的费用，独立穷举测试再比较所有小型合并次序的最低值。

**完整程序**

```python
def pop_lightest(forest):
    best = 0
    for index in range(1, len(forest)):
        if forest[index]["weight"] < forest[best]["weight"]:
            best = index
    return forest.pop(best)

def huffman_codes(weights):
    forest = []
    for symbol in range(len(weights)):
        if weights[symbol] <= 0:
            return None
        forest.append({"weight": weights[symbol], "symbol": symbol,
                       "left": None, "right": None})
    if len(forest) == 0:
        return []
    while len(forest) > 1:
        left = pop_lightest(forest)
        right = pop_lightest(forest)
        forest.append({"weight": left["weight"] + right["weight"], "symbol": None,
                       "left": left, "right": right})
    codes = [None] * len(weights)
    path = []
    def visit(node):
        if node["symbol"] is not None:
            codes[node["symbol"]] = path.copy()
            return
        path.append(0)
        visit(node["left"])
        path.pop()
        path.append(1)
        visit(node["right"])
        path.pop()
    visit(forest[0])
    return codes

def pop_smallest(values):
    best = 0
    for index in range(1, len(values)):
        if values[index] < values[best]:
            best = index
    return values.pop(best)

def optimal_merge(weights):
    for weight in weights:
        if weight < 0:
            return None
    queue = weights.copy()
    cost = 0
    merges = []
    while len(queue) > 1:
        first = pop_smallest(queue)
        second = pop_smallest(queue)
        total = first + second
        cost = cost + total
        merges.append([first, second, total])
        queue.append(total)
    return {"cost": cost, "merges": merges}

weights = [3, 5, 8, 11]
codes = huffman_codes(weights)
cost = 0
for index in range(len(weights)):
    cost = cost + weights[index] * len(codes[index])
print(codes)
print(cost)
print(optimal_merge(weights)["cost"])
```

**预期输出**

```text
[[1, 1, 0], [1, 1, 1], [1, 0], [0]]
51
51
```


<a id="practice"></a>

## 自己做：先完成再看解答

### 练习 1

删除尽量少的半开区间，使剩下区间互不重叠。对 \[\[0,2\],\[1,3\],\[2,4\],\[3,5\]\] 返回保留与删除的原下标；空输入也要处理。

<details>
<summary>提示</summary>

总数量固定，最少删除等价于最多保留；不需要重新发明一个“最重叠先删”规则。

</details>

<details>
<summary>解答与检查</summary>

调用 interval\_schedule 得到最大数量的兼容集合，删除补集。若保留 K 项，任何删除方案都至少删除 n−K 项，否则会产生超过 K 的可行集合，与最大性矛盾。保留下标按时间次序，删除下标按原编号次序；同样最优的不同集合都可以接受。本例保留 \[0,2\]、删除 \[1,3\]。额外补集处理线性，总时间仍由插入排序决定，为 O(n²+n+1)，空间 O(n+1)。

**完整程序**

```python
def ordered(values):
    result = values.copy()
    for index in range(1, len(result)):
        saved = result[index]
        position = index
        while position > 0 and result[position - 1] > saved:
            result[position] = result[position - 1]
            position = position - 1
        result[position] = saved
    return result

def interval_schedule(intervals):
    records = []
    for index in range(len(intervals)):
        start = intervals[index][0]
        finish = intervals[index][1]
        if start >= finish:
            return None
        records.append([finish, start, index])
    records = ordered(records)
    chosen = []
    last_finish = None
    for record in records:
        if last_finish is None or record[1] >= last_finish:
            chosen.append(record[2])
            last_finish = record[0]
    return chosen

def minimum_removals(intervals):
    kept = interval_schedule(intervals)
    if kept is None:
        return None
    selected = [False] * len(intervals)
    for index in kept:
        selected[index] = True
    removed = []
    for index in range(len(intervals)):
        if not selected[index]:
            removed.append(index)
    return {"kept": kept, "removed": removed}

print(minimum_removals([[0, 2], [1, 3], [2, 4], [3, 5]]))
print(minimum_removals([]))
```

**预期输出**

```text
{'kept': [0, 2], 'removed': [1, 3]}
{'kept': [], 'removed': []}
```


</details>

### 练习 2

给定闭区间 \[\[0,2\],\[2,5\],\[4,7\],\[7,7\]\]，选择最少的点，使每个区间至少包含一个所选点。允许单点区间，返回一种最优点集。

<details>
<summary>提示</summary>

先看右端点最小的未覆盖区间，把为它选择的点向右移到该右端点，检查其他已覆盖区间是否会丢失覆盖。

</details>

<details>
<summary>解答与检查</summary>

按右端点递增处理。任何覆盖当前最早右端点区间的点 p 都不大于该右端点 r；把 p 移到 r，原来包含 p 的后续区间右端点至少为 r、左端点不大于 p，因此仍包含 r。故存在以 r 为首个选择的最优解。重复即可得到 \[2,7\]，每次新点对应一个此前未覆盖的区间。这里是闭区间，端点算覆盖，start=finish 合法，与调度章节的契约不同。倒置区间返回 None。实现最坏时间 O(n²+n+1)、空间 O(n+1)。

**完整程序**

```python
def ordered(values):
    result = values.copy()
    for index in range(1, len(result)):
        saved = result[index]
        position = index
        while position > 0 and result[position - 1] > saved:
            result[position] = result[position - 1]
            position = position - 1
        result[position] = saved
    return result

def interval_stabbing(intervals):
    records = []
    for interval in intervals:
        if interval[0] > interval[1]:
            return None
        records.append([interval[1], interval[0]])
    records = ordered(records)
    points = []
    last = None
    for record in records:
        if last is None or last < record[1]:
            last = record[0]
            points.append(last)
    return points

print(interval_stabbing([[0, 2], [2, 5], [4, 7], [7, 7]]))
print(interval_stabbing([]))
```

**预期输出**

```text
[2, 7]
[]
```


</details>

### 练习 3

任务用 \[处理时长,截止时间\] 表示，均在时刻 0 就绪，单机连续执行、不能中断。最小化最大拖期，其中每项拖期为完成时间减截止时间与 0 的较大者。处理 \[\[4,5\],\[2,3\],\[3,6\]\]。

<details>
<summary>提示</summary>

按截止时间升序；比较两个相邻但截止时间倒置的任务，交换前后最晚的完成位置相同。

</details>

<details>
<summary>解答与检查</summary>

若 a 排在 b 前而 a 截止更晚，交换后 b 更早完成，其拖期不超过原来 b；a 占据原来 b 的完成时刻，又因截止不早于 b，拖期也不超过原来 b。其他任务完成时间不变，故交换不增加最大拖期，反复消除倒置得到截止时间顺序。本例顺序为 \[1,0,2\]，完成时间 \[2,6,9\] 按执行顺序对应，最大拖期为 3。时长允许零、拒绝负数，截止时间可为任意整数；空任务返回最大拖期 0。此结论不优化总拖期，也不适用于各任务不同就绪时间。插入排序使最坏时间为 O(n²+n+1)，空间 O(n+1)。

**完整程序**

```python
def ordered(values):
    result = values.copy()
    for index in range(1, len(result)):
        saved = result[index]
        position = index
        while position > 0 and result[position - 1] > saved:
            result[position] = result[position - 1]
            position = position - 1
        result[position] = saved
    return result

def minimum_max_tardiness(jobs):
    records = []
    for index in range(len(jobs)):
        duration = jobs[index][0]
        deadline = jobs[index][1]
        if duration < 0:
            return None
        records.append([deadline, index, duration])
    records = ordered(records)
    order = []
    finishes = []
    time = 0
    worst = 0
    for record in records:
        time = time + record[2]
        order.append(record[1])
        finishes.append(time)
        delay = time - record[0]
        if delay > worst:
            worst = delay
    return {"order": order, "finishes": finishes, "max_tardiness": worst}

print(minimum_max_tardiness([[4, 5], [2, 3], [3, 6]]))
print(minimum_max_tardiness([]))
```

**预期输出**

```text
{'order': [1, 0, 2], 'finishes': [2, 6, 9], 'max_tardiness': 3}
{'order': [], 'finishes': [], 'max_tardiness': 0}
```


</details>

<a id="pitfalls"></a>

## 容易混淆的地方

- **局部取最大的收益或最小的代价，总会得到全局最好。** 先列可行条件和完整目标，再给交换或保持领先证明；找零反例说明直觉会失败。
- **输出合法就已经证明最优。** 合法性和最优性是两项检查；小输入需要独立枚举全部可行解比较目标值。
- **同为区间问题，所有端点和零长度规则都相同。** 调度使用正时长半开区间，选点使用允许单点的闭区间，比较符号随模型而变。
- **Huffman 一定压缩每个文件，且最优码字唯一。** 加权码长最优只针对规定的前缀码目标；元信息需另计，等权和左右交换可产生不同最优码字。

<a id="self-check"></a>

## 离开这一章前

- [ ] 写出一个贪心找零剩余非零但原问题可解的输入。
- [ ] 不用程序，解释把最优排程第一项换成最早结束任务为何仍可行。
- [ ] 把合并过程画成二叉树，按叶深重新计算总代价。
- [ ] 给出改变条件后需要重新证明的两个例子。

## 本章边界

- 所有数值均为整数，按单位算术成本分析；不考虑任意大整数的位复杂度。
- 排序和最小值选择使用便于审读的平方时间实现；本章不提供文件压缩器或通用调度系统。
- 只证明上述指定问题，带权区间、复杂资源约束与更一般编码留待后续。

## 选题来源与覆盖

来源含学生报告时，仅将其作为选题线索；具体机制仍需结合后续实验或权威资料核对。

- [大一小学期/Week\_3-Python/docs/readme.md](https://github.com/PKUanonym/REKCARC-TSC-UHT/blob/37cd19f7a9fb80dc846a7016b3fd482ed5fe7cc0/%E5%A4%A7%E4%B8%80%E5%B0%8F%E5%AD%A6%E6%9C%9F/Week_3-Python/docs/readme.md)（已提取可读文本，固定版本 37cd19f7a9fb）
- 主题 1：Python 基础语法的外部学习入口；位置：第 41–80 行。
- 主题 2：从基础语法到工具与应用的建议阅读顺序；位置：第 121–160 行。

## 参考资料与规则核对

上游入口用于确定学习方向；下面的参考资料用于核对语言语义、数据结构或算法分析规则，例题和练习由本项目重新设计。

- [NIST DADS：贪心算法](https://xlinux.nist.gov/dads/HTML/greedyalgo.html)：核对局部选择并不对所有问题保证全局最优；本章各问题的交换论证、数据和代码自行组织。
- [David A. Cusack：区间调度](https://cusack.hope.edu/DAIADS/Content/Algorithms/Greedy/Interval%20Scheduling.html)：通过搜索索引核对最早结束策略和交换思路；直接读取不可用。本章使用自己的半开区间数据、原下标接口及插入排序，成本按实现另算。
- [NIST DADS：最优合并](https://xlinux.nist.gov/dads/HTML/optimalMerge.html)：核对两项合并且费用为和的模型；重新设计数值与轨迹，独立编写线性扫描选择实现。
- [NIST DADS：Huffman 编码](https://xlinux.nist.gov/dads/HTML/huffmanCoding.html)：核对最轻两树合并与二进制前缀码；只使用该模型，不采用页面关于其他编码法的附带比较。

**继续学习**：先独立完成自测，再记录仍需回读的步骤。

[上一章：枚举选择并排除无解分支：回溯与搜索剪枝](25-backtracking.md) · [下一章：保存子问题的答案：动态规划入门](27-dynamic-programming.md)

[教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [哈希表与图练习指引](../hash-graphs-practice.md) · [拓扑排序与带权图练习指引](../weighted-graphs-practice.md) · [记录自己的学习](../learning-log-template.md)
