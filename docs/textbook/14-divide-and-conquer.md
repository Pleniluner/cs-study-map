# 把问题分小再合起来：分治与递归归并

[返回教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [哈希表与图练习指引](../hash-graphs-practice.md)

[上一章：函数怎样调用自己：递归、返回与调用栈](13-recursion.md) · [下一章：先分区再递归：快速排序与三路划分](15-quick-sort.md)

[学习目标](#objectives) · [需要的基础](#prerequisites) · [例题](#examples) · [练习](#practice) · [自测](#self-check)

状态：**AI 初稿，可开始试学**。生成模型：Codex 当前会话（未记录具体模型型号）。

本章围绕资料中识别到的知识点重新编写；讲解、数值模型、例题与练习为 AI 原创组织，不是原课程题目或答案。主题出处只说明选题关联，不证明全部推导已经正确。

上一章的求和每次只去掉一项，容易形成很长的调用链。能否把问题分成两块，各自解决后再组合？这就是本章要建立的分治思路。我们先用区间求和看清拆分、子答案和合并，再把第 11 章的二分写成递归，最后把第 12 章的归并改为自顶向下组织。算法仍然要回答同样的问题：范围有没有漏项或重叠，基例是否完整，合并是否保留元素，以及总工作和同时存活空间各有多少。

<a id="objectives"></a>

## 学完要能做到

- 用半开区间明确两个子问题的覆盖范围及严格缩小。
- 区分两个子问题都求解与比较后只进入一边的工作量。
- 从叶子、内部结点和最长路径分别计算调用数、合并工作与栈深。
- 实现复用一个缓冲列表的递归归并，说明稳定性与副作用。
- 用分治处理计数、快速幂和逆序对，并说明组合步骤为什么正确。

<a id="prerequisites"></a>

## 需要的基础

- 掌握第 10–13 章的量级、半开区间、合并与递归调用。
- 区间统一要求 0≤lo≤hi≤len(values)，缓冲列表与输入等长且是不同对象。
- 二分只接受非降序整数列表；求和与排序接受任意整数列表，运算采用单位成本模型。

## 一、把完整范围分成互不遗漏的两半

分治把一个问题分成较小实例，递归求解，再把子答案组合成原问题的答案。对列表求和，split\_sum(values, lo, hi) 的承诺是返回半开区间 \[lo, hi) 内所有项之和。空区间直接返回 0，单元素直接返回该项，这两个基例分别解决没有数据与不必继续拆分的情况。

长度至少为 2 时，中点为 lo 加区间长度整除 2。两半分别是 \[lo, middle) 与 \[middle, hi)：前一段不包含 middle，后一段从它开始，既不重叠也不漏项。两边长度都小于原长度，即使长度为奇数也成立；不要求输入长度是 2 的幂，更不需要补零。

假定两次子调用都遵守求和承诺，把两个结果相加就得到全段之和。这个推理把正确性分为可直接核对的基例和组合步骤；终止性则另由区间严格缩短保证。只证明“分得更小”不能证明答案正确，子问题覆盖或组合方式仍可能写错。

下面对 \[4, -2, 7, 1, 3\] 求和，根区间分成长度 2 与 3 的两块，最终每一项恰好进入一个单元素基例。函数传递位置并共享只读列表，不创建子列表。两次子调用在代码中依次执行，分成两块也不意味着自动使用两颗处理器或并行执行。

**完整程序**

```python
def split_sum(values, lo, hi):
    if lo == hi:
        return 0
    if hi - lo == 1:
        return values[lo]
    middle = lo + (hi - lo) // 2
    left = split_sum(values, lo, middle)
    right = split_sum(values, middle, hi)
    return left + right

def balanced_sum(values):
    return split_sum(values, 0, len(values))

values = [4, -2, 7, 1, 3]
print(balanced_sum(values), values)
print(balanced_sum([]))
```

**预期输出**

```text
13 [4, -2, 7, 1, 3]
0
```


选题关联：来源主题 1（文末列出）。

## 二、树的结点数与高度回答不同问题

把每次调用画成一个结点，连向它创建的两个子调用，就得到分治调用树。这里每个非基例恰有两个孩子，单元素调用是叶子。对非空长度 n，每项形成一个叶子，共 n 个；每次合并两个子结果减少一个待组合结果，因此有 n-1 个内部结点，全部调用合计 2n-1 次。

沿最深的一条路径看，长度每次至多变成原长度的一半向上取整，直到 1。若把根本身计为第 1 层，最大同时存活的辅助调用是 log₂n 向上取整再加 1。n=5 时共有 9 个调用，最深只有 4 层；n=8 时有 15 个调用，最深也为 4 层。总调用数和峰值栈深不能互换。

下面 split\_report 只模拟区间拆分，分别返回 calls、depth、leaves。它不扫描实际列表，也不等于算法所有机器指令的计数。空区间也会直接进入一次基例，所以返回 1 次调用、1 层和 1 个终止结点；这个终止结点不代表一个数据元素，非空公式不能直接代入 n=0。

求和每个内部结点只作一次整数加法，因此总加法数为 n-1，整体时间 Θ(n)，栈空间 O(log n)，这里 n 至少为 2。它把上一章线性链的栈深降低了，却没有把全部求和工作降成对数。树有对数高度时，仍可能需要访问线性数量的结点。

**完整程序**

```python
def split_report(lo, hi):
    if hi - lo <= 1:
        return {"calls": 1, "depth": 1, "leaves": 1}
    middle = lo + (hi - lo) // 2
    left = split_report(lo, middle)
    right = split_report(middle, hi)
    deepest = left["depth"]
    if right["depth"] > deepest:
        deepest = right["depth"]
    return {"calls": 1 + left["calls"] + right["calls"], "depth": 1 + deepest, "leaves": left["leaves"] + right["leaves"]}

for size in [5, 8, 0]:
    print(size, split_report(0, size))
```

**预期输出**

```text
5 {'calls': 9, 'depth': 4, 'leaves': 5}
8 {'calls': 15, 'depth': 4, 'leaves': 8}
0 {'calls': 1, 'depth': 1, 'leaves': 1}
```


选题关联：来源主题 1（文末列出）。

## 三、只求一半：递归二分与两边求和的差别

第 11 章 lower\_bound 的循环也可以表达成递归。lower\_recursive 在候选元素区间 \[lo, hi) 里继续寻找左边界；区间为空时返回 lo。若中点值小于目标，下一次只处理 \[middle+1, hi)，否则只处理 \[lo, middle)。原有的有序前提和两侧不变式都要保留，不能因为改成函数调用就省略。

每一轮比较后只有一边仍可能包含答案，另一边不再求解。所以它与 split\_sum 的两边都调用不同：二分只沿一条路径走，单位比较模型下最坏工作 O(log n)；求和必须访问每个叶子，总工作仍为线性。广义的分治也包含这种排除一侧的形式，不必为凑“两半”去调用已经排除的部分。

递归分支直接返回子调用的边界，外层 recursive\_first 再检查位置合法且数值相等，才返回匹配下标。空表返回边界 0，但精确查找返回 -1；查询大于最大值的目标返回末尾边界，也必须在索引前拦住。重复值仍由左边界保证取第一个，不在相等时提前结束。

时间量级与原来的循环二分相同，空间却发生变化：递归版本保留沿途尚未返回的调用，最坏栈空间 O(log n)，循环版本只有固定数量端点。这里不建立切片，因此返回的是原列表的下标，分解时也没有隐藏线性复制成本。函数体短了，不代表空间自动更少。

**完整程序**

```python
def lower_recursive(values, target, lo, hi):
    if lo == hi:
        return lo
    middle = lo + (hi - lo) // 2
    if values[middle] < target:
        return lower_recursive(values, target, middle + 1, hi)
    return lower_recursive(values, target, lo, middle)

def recursive_first(values, target):
    position = lower_recursive(values, target, 0, len(values))
    if position < len(values) and values[position] == target:
        return position
    return -1

values = [-3, 1, 1, 5, 8]
print(recursive_first(values, 1), recursive_first(values, 4))
print(recursive_first([], 1), values)
```

**预期输出**

```text
1 -1
-1 [-3, 1, 1, 5, 8]
```


选题关联：来源主题 1（文末列出）。

## 四、递归归并：先排两半，再写回整段

第 12 章用宽度翻倍从小片段往上归并；这里从整段开始递归拆分。merge\_recursive\_range 只负责把 \[lo, hi) 排好，长度不超过 1 就直接返回。较长时先排左半，再排右半，最后调用 merge\_range。合并前两半必须各自已有序，不能只分出中点就立即假定前提成立。

merge\_range 用两个读取位置选择较小项，把结果先写到独立的 buffer，再把整个区间写回 values。若直接一边读取原列表一边覆盖尚未读取的项，可能丢失数据；独立缓冲使读取来源保持完整。buffer 必须等长且不与 values 是同一个列表，外层通过 copy 创建一次，后续所有调用复用它。

相等时先取左半，保持前面那条记录先出现；每一半内部的取出顺序也不变，所以稳定性从基例一直保持到根。左右剩余项各自全部写入，不去重。所有读写限制在当前区间，别的部分不受影响；例题会专门检查只排中间一段的情形。

这个公开接口修改原列表并返回 None，和第 12 章返回新列表的接口需要分别记住。它使用线性缓冲和对数调用栈，整体额外空间 O(n)，不能因结果写回原列表就按前章定义称为 O(1) 原地排序。空表也按同一接口正常返回，不读取任何元素。

**完整程序**

```python
def merge_range(values, buffer, lo, middle, hi):
    left = lo
    right = middle
    write = lo
    while left < middle and right < hi:
        if values[left] <= values[right]:
            buffer[write] = values[left]
            left = left + 1
        else:
            buffer[write] = values[right]
            right = right + 1
        write = write + 1
    while left < middle:
        buffer[write] = values[left]
        left = left + 1
        write = write + 1
    while right < hi:
        buffer[write] = values[right]
        right = right + 1
        write = write + 1
    for index in range(lo, hi):
        values[index] = buffer[index]

def merge_recursive_range(values, buffer, lo, hi):
    if hi - lo <= 1:
        return
    middle = lo + (hi - lo) // 2
    merge_recursive_range(values, buffer, lo, middle)
    merge_recursive_range(values, buffer, middle, hi)
    merge_range(values, buffer, lo, middle, hi)

def merge_sort_recursive(values):
    buffer = values.copy()
    merge_recursive_range(values, buffer, 0, len(values))

values = [6, 1, 4, 1, 9]
returned = merge_sort_recursive(values)
print(values, returned)
empty = []
print(merge_sort_recursive(empty), empty)
```

**预期输出**

```text
[1, 1, 4, 6, 9] None
None []
```


选题关联：来源主题 1（文末列出）。

## 五、递推式要把本层工作也算进去

递归归并的总时间等于两边递归时间加本次合并工作。长度 n 至少为 2 时，两半长度分别为向下取整的 n/2 与余下部分，本层合并写缓冲 n 次、写回 n 次，还有线性数量的比较和游标更新。所以本层工作为 Θ(n)，不是只有两次函数调用的固定开销。

把它写成递推式就是 T(n)=T(⌊n/2⌋)+T(⌈n/2⌉)+Θ(n)，其中 T(0)、T(1) 都是固定成本。向下与向上取整保证两半长度相加仍为 n；只有 n 为 2 的幂时，才能在每一层直接化成两个同样大的子问题。

为方便看层次，先取 n 为 2 的 k 次方。每个需要合并的深度层，其各区间互不重叠、总长为 n；这样的层有 k 层。因此只数写入缓冲的次数就是 n×k，加上基例等固定工作得到 Θ(n log n)。这是按各层实际规模求和，不能把总调用数 2n-1 乘根结点的 n 来当紧确计数。

下面 merge\_work 是这个计数模型：空或单元素不合并，其他情况返回两边计数加 n。n=8 得到 24，n=5 却是 12，而不是 5×3=15，因为最后一层有些分支已经停止，不会凑满 n 项。非 2 的幂仍有 Θ(n log n) 时间，但每层恰好 n 不能不加条件地照搬。

本实现不因输入已排序就跳过合并，所以最好与最坏都有同样量级的写入工作。缓冲始终只有一份长度 n 的列表，各次调用顺序使用；调用过程中累计写入 n log n 量级，不等于同时需要那么多存储。分析时间看累计工作，分析空间看峰值同时存活对象。

**完整程序**

```python
def merge_work(n):
    if n <= 1:
        return 0
    left_size = n // 2
    return merge_work(left_size) + merge_work(n - left_size) + n

for size in [0, 1, 5, 8, 9]:
    print(size, merge_work(size))
```

**预期输出**

```text
0 0
1 0
5 12
8 24
9 29
```


选题关联：来源主题 1（文末列出）。

<a id="examples"></a>

## 跟着做：原创例题

### 例题 1

对 \[5, -2, 4\] 的区间 \[0, 3) 做分治求和，记录拆分、基例和合并事件。说明为什么事件数与实际调用数不同。

1. 根区间中点是 1，先拆成 \[0, 1) 和 \[1, 3)，把拆分事件记下来。
2. 左边只有 5，直接返回；右边中点是 2，继续拆出 -2 和 4 两个基例。
3. 右边先合并得到 2，再与左边的 5 合并得到总和 7。
4. 调用树有三个叶子和两个内部结点，共五次调用；内部结点各有一次拆分和一次合并事件，所以一共七条记录。
5. 两侧依次执行，最长路径只有三个辅助调用；调试记录的额外存储要和普通求和分开计算。

**结果与核对**

最终和为 7。顺序是先记录根的拆分、完成左边，再深入右边，最后从右侧回到根合并；日志并不是按深度层逐层输出。

**完整程序**

```python
def sum_trace(values, lo, hi, events):
    if hi - lo <= 1:
        result = 0
        if lo < hi:
            result = values[lo]
        events.append(["base", lo, hi, result])
        return result
    middle = lo + (hi - lo) // 2
    events.append(["split", lo, hi, middle])
    left = sum_trace(values, lo, middle, events)
    right = sum_trace(values, middle, hi, events)
    result = left + right
    events.append(["join", lo, hi, result])
    return result

events = []
result = sum_trace([5, -2, 4], 0, 3, events)
for event in events:
    print(event)
print(result)
```

**预期输出**

```text
['split', 0, 3, 1]
['base', 0, 1, 5]
['split', 1, 3, 2]
['base', 1, 2, -2]
['base', 2, 3, 4]
['join', 1, 3, 2]
['join', 0, 3, 7]
7
```


### 例题 2

只把 \[99, 8, 2, 8, 1, -99\] 的区间 \[1, 5) 排成非降序。保留两端元素，再对 \[2, 2) 调用同一辅助函数，解释输入副作用的范围。

1. \[1, 5) 包含四项 8、2、8、1，不包括下标 0 的 99，也不包括下标 5 的 -99。
2. 中点 3 把范围分成 \[1, 3) 与 \[3, 5)，递归后分别变为 2、8 和 1、8。
3. 合并先取右边 1，再取左边 2，两个 8 相等时先取左边；写回的范围仍仅是 \[1, 5)。
4. 得到 \[99, 1, 2, 8, 8, -99\]，整个列表没有全部有序，这是只排序子区间的正确结果。
5. \[2, 2) 是空区间，命中基例，不读取或改写；缓冲与输入等长且为不同对象，能够继续复用。

**结果与核对**

两次打印都为 \[99, 1, 2, 8, 8, -99\]。检查时应同时核对中间区间的顺序与重数，以及两端哨兵值没有改变，不能只检查全表是否有序。

**完整程序**

```python
def merge_range(values, buffer, lo, middle, hi):
    left = lo
    right = middle
    write = lo
    while left < middle and right < hi:
        if values[left] <= values[right]:
            buffer[write] = values[left]
            left = left + 1
        else:
            buffer[write] = values[right]
            right = right + 1
        write = write + 1
    while left < middle:
        buffer[write] = values[left]
        left = left + 1
        write = write + 1
    while right < hi:
        buffer[write] = values[right]
        right = right + 1
        write = write + 1
    for index in range(lo, hi):
        values[index] = buffer[index]

def merge_recursive_range(values, buffer, lo, hi):
    if hi - lo <= 1:
        return
    middle = lo + (hi - lo) // 2
    merge_recursive_range(values, buffer, lo, middle)
    merge_recursive_range(values, buffer, middle, hi)
    merge_range(values, buffer, lo, middle, hi)

def merge_sort_recursive(values):
    buffer = values.copy()
    merge_recursive_range(values, buffer, 0, len(values))

values = [99, 8, 2, 8, 1, -99]
buffer = values.copy()
merge_recursive_range(values, buffer, 1, 5)
print(values)
merge_recursive_range(values, buffer, 2, 2)
print(values)
```

**预期输出**

```text
[99, 1, 2, 8, 8, -99]
[99, 1, 2, 8, 8, -99]
```


<a id="practice"></a>

## 自己做：先完成再看解答

### 练习 1

用分治写 positive\_range(values, lo, hi)，统计指定半开区间中正数的个数。检查 \[3, -1, 0, 4, -2\] 的 \[0, 5)、\[1, 4) 和 \[2, 2)，并解释为什么高度为对数不代表总时间为对数。

<details>
<summary>提示</summary>

空区间贡献 0，单元素按是否大于零贡献 1 或 0；两边答案直接相加。

</details>

<details>
<summary>解答与检查</summary>

结果为 2、1、0，零不算正数。长度 m 的非空范围产生 m 个叶子，每项仍必须判断一次；因此总时间 Θ(m)，栈空间 O(log m)（m 至少为 2）。空范围直接返回，不会把区间外的正数统计进来。

**完整程序**

```python
def positive_range(values, lo, hi):
    if lo == hi:
        return 0
    if hi - lo == 1:
        if values[lo] > 0:
            return 1
        return 0
    middle = lo + (hi - lo) // 2
    return positive_range(values, lo, middle) + positive_range(values, middle, hi)

values = [3, -1, 0, 4, -2]
print(positive_range(values, 0, 5), positive_range(values, 1, 4), positive_range(values, 2, 2))
```

**预期输出**

```text
2 1 0
```


</details>

### 练习 2

写 power\_fast(base, exponent)，base 为整数，exponent 为非负整数，指数为 0 时统一返回 1。每层只递归计算一次一半指数的结果，再处理奇偶，检查 3 的 5 次方、-2 的 6 次方和 0 的 0 次方。

<details>
<summary>提示</summary>

保存一次 half，先平方；奇数指数还剩一个 base 因子。不要把相同子调用写两遍。

</details>

<details>
<summary>解答与检查</summary>

结果为 243、64、1，最后一个按本题的空乘积约定处理。指数每次整除 2，乘法次数为对数量级；若重复调用两次相同的半指数问题，就失去了复用。这里计算的是乘法次数，实际整数随幂次增大，不能把大整数乘法都视为固定真实耗时。

**完整程序**

```python
def power_fast(base, exponent):
    if exponent == 0:
        return 1
    half = power_fast(base, exponent // 2)
    square = half * half
    if exponent % 2 == 1:
        return square * base
    return square

print(power_fast(3, 5), power_fast(-2, 6), power_fast(0, 0))
```

**预期输出**

```text
243 64 1
```


</details>

### 练习 3

逆序对是原下标 i 在 j 前面且 values\[i\] 严格大于 values\[j\] 的一对位置。扩展归并，返回有序副本与逆序对总数，不修改输入。检查 \[3, 1, 2, 1\] 及 \[2, 2\]。

<details>
<summary>提示</summary>

左右内部的逆序对递归统计。合并时若右项严格小于当前左项，它也小于所有剩余左项，一次增加 middle-left；相等时取左边，不计逆序。

</details>

<details>
<summary>解答与检查</summary>

第一组有四对，来自原下标 (0,1)、(0,2)、(0,3)、(2,3)，有序副本为 \[1, 1, 2, 3\]；第二组为零。左右内部与跨区间三类互不重叠，计数相加不漏不重。每次合并仍做线性工作，整体时间 Θ(n log n)、额外空间 O(n)（n 至少为 2），包括返回副本与缓冲。

**完整程序**

```python
def merge_count(values, buffer, lo, middle, hi):
    left = lo
    right = middle
    write = lo
    inversions = 0
    while left < middle and right < hi:
        if values[left] <= values[right]:
            buffer[write] = values[left]
            left = left + 1
        else:
            buffer[write] = values[right]
            right = right + 1
            inversions = inversions + middle - left
        write = write + 1
    while left < middle:
        buffer[write] = values[left]
        left = left + 1
        write = write + 1
    while right < hi:
        buffer[write] = values[right]
        right = right + 1
        write = write + 1
    for index in range(lo, hi):
        values[index] = buffer[index]
    return inversions

def inversion_range(values, buffer, lo, hi):
    if hi - lo <= 1:
        return 0
    middle = lo + (hi - lo) // 2
    left = inversion_range(values, buffer, lo, middle)
    right = inversion_range(values, buffer, middle, hi)
    across = merge_count(values, buffer, lo, middle, hi)
    return left + right + across

def inversion_report(values):
    result = values.copy()
    buffer = values.copy()
    count = inversion_range(result, buffer, 0, len(result))
    return {"sorted": result, "inversions": count}

values = [3, 1, 2, 1]
print(inversion_report(values))
print(inversion_report([2, 2]))
print(values)
```

**预期输出**

```text
{'sorted': [1, 1, 2, 3], 'inversions': 4}
{'sorted': [2, 2], 'inversions': 0}
[3, 1, 2, 1]
```


</details>

<a id="pitfalls"></a>

## 容易混淆的地方

- **两半都包含 middle，或两半都跳过 middle，导致重复或漏项。** 统一使用 \[lo, middle) 与 \[middle, hi)，并检查空区间和长度为 2、3 的情况。
- **看到高度是对数，就把两边都递归的总时间也写成对数。** 分别数本层工作、全部结点与最长路径；只查一边和两边都处理有不同递推。
- **只说归并修改原列表，就宣称额外空间为 O(1)。** 把共享缓冲和递归栈一起计入；只修改原容器并不消除缓冲存储。
- **快速幂重复求同一个 half，或逆序统计把相等项也算进去。** 保存子结果后复用；逆序是严格大于，相等时先取左项以保持定义与稳定性。

<a id="self-check"></a>

## 离开这一章前

- [ ] 画出长度 0、1、3、5 的拆分树，检查每个下标进入几个叶子。
- [ ] 比较 2n-1 个总调用与向上取整 log₂n 加 1 的最大深度，单独处理空范围。
- [ ] 用哨兵包住待排序区间，检查区域外完全不变。
- [ ] 核对 merge\_work(5) 与 merge\_work(8)，解释各层工作为什么不总是同一个数。
- [ ] 用直接枚举所有 i、j 的小程序核对逆序对，特别检查重复值。

## 本章边界

- 只分析顺序执行的分治，不把两次递归调用当作并行任务。
- 区间合法性和缓冲独立性是调用前提，辅助函数不负责修复非法范围或别名。
- 不使用主定理套公式，先按本章具体树和每层工作推导；一般递推留待后续。
- 快速幂采用非负整数指数与单位算术模型，不涉及负指数、模幂或位复杂度。

## 选题来源与覆盖

来源含学生报告时，仅将其作为选题线索；具体机制仍需结合后续实验或权威资料核对。

- [大一小学期/Week\_3-Python/docs/readme.md](https://github.com/PKUanonym/REKCARC-TSC-UHT/blob/37cd19f7a9fb80dc846a7016b3fd482ed5fe7cc0/%E5%A4%A7%E4%B8%80%E5%B0%8F%E5%AD%A6%E6%9C%9F/Week_3-Python/docs/readme.md)（已提取可读文本，固定版本 37cd19f7a9fb）
- 主题 1：Python 基础语法的外部学习入口；位置：第 41–80 行。
- 主题 2：从基础语法到工具与应用的建议阅读顺序；位置：第 121–160 行。

## 参考资料与规则核对

上游入口用于确定学习方向；下面的参考资料用于核对语言语义、数据结构或算法分析规则，例题和练习由本项目重新设计。

- [NIST DADS：分治](https://xlinux.nist.gov/dads/HTML/divideAndConquer.html)：核对分解、递归求解与组合的定义，以及二分只继续一侧的形式；题目和数据自拟。
- [Cornell CS2110：归并的递归与复杂度](https://www.cs.cornell.edu/courses/cs2110/2025fa/lectures/lec07/)：核对递归归并、按层计数与共享缓冲的空间分析；本章自行编写 Python 区间实现和逆序对练习。

**继续学习**：先独立完成自测，再记录仍需回读的步骤。

[上一章：函数怎样调用自己：递归、返回与调用栈](13-recursion.md) · [下一章：先分区再递归：快速排序与三路划分](15-quick-sort.md)

[教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [哈希表与图练习指引](../hash-graphs-practice.md) · [记录自己的学习](../learning-log-template.md)
