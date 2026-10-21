# 怎样缩小候选范围：顺序查找与二分查找

[返回教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md)

[上一章：数据变多会怎样：算法分析与增长量级](10-algorithm-analysis.md) · [下一章：怎样把数据排成顺序：选择、插入与归并排序](12-sorting.md)

[学习目标](#objectives) · [需要的基础](#prerequisites) · [例题](#examples) · [练习](#practice) · [自测](#self-check)

状态：**AI 初稿，可开始试学**。生成模型：Codex 当前会话（未记录具体模型型号）。

本章围绕资料中识别到的知识点重新编写；讲解、数值模型、例题与练习为 AI 原创组织，不是原课程题目或答案。主题出处只说明选题关联，不证明全部推导已经正确。

第 6 章曾按位置逐项查找，第 10 章又比较了首项命中与查找失败的工作量。本章把查找的契约写得更完整：返回值到底是元素、下标，还是可以插入的位置？输入已有顺序时，怎样安全地排除一半范围？我们先复习顺序查找，再从非降序前提和半开区间推导二分边界，最后处理重复值、区间计数和有序插入。每次运行都同时检查答案、输入是否变化和区间是否缩小，不把碰巧返回正确结果当作算法成立的证明。

<a id="objectives"></a>

## 学完要能做到

- 明确首个匹配下标与未找到标记，正确处理空输入和零下标。
- 解释二分查找为什么需要非降序列表，以及检查或建立顺序的成本。
- 用左右边界不变式推导 lower\_bound，并保证每轮严格缩小。
- 区分左边界、右边界、首个匹配与最后匹配，正确统计重复值。
- 分析多次查询和插入的完整流程，说明返回下标属于哪个列表。

<a id="prerequisites"></a>

## 需要的基础

- 掌握列表索引、切片、复制、insert，以及第 10 章计数与增长量级。
- 理解半开范围：包含左端而不包含右端；索引 n 不属于长度 n 的列表。
- 输入为整数列表；二分相关函数要求已非降序，只有明确说明的包装函数主动检查。

## 一、顺序查找：返回哪个答案

查找之前先确定接口。linear\_first 返回第一个等于 target 的非负下标，找不到返回 -1，不修改输入。这不是返回目标数值，也不是返回布尔值。列表可以无序；由于从下标 0 开始按顺序检查，第一次命中前的全部位置都已排除，因此返回的一定是最早位置。

下面 \[8, -2, 8, 5\] 中查找 8 返回 0，查找 5 返回 3，查找 7 返回 -1。0 是合法答案，不能用“结果为真”判断找到；-1 在 Python 中反而是真值，还能作为末项下标使用，所以直接把结果交给列表索引同样危险。先判断结果是否等于 -1，再决定是否读取。

空列表没有候选下标，循环执行零次，返回 -1。重复的两个 8 仍是两个位置；此接口遇到第一个就结束，若任务改为列出全部匹配位置，需要另一套返回约定。把这些差异写进函数说明，调用者才不会拿“任意一个匹配”误当作“第一个匹配”。

非空输入最好检查一次，最坏检查 n 次，额外只需固定数量的名字。顺序查找无需先检查有序性或改变排列，对一次临时查询常常已经合适。下一节的更快查询依赖额外前提，不能只比较函数内部的循环就断言完整任务总是更快。

**完整程序**

```python
def linear_first(values, target):
    for index in range(len(values)):
        if values[index] == target:
            return index
    return -1

values = [8, -2, 8, 5]
print(linear_first(values, 8), linear_first(values, 5), linear_first(values, 7))
print(linear_first([], 8), values)
```

**预期输出**

```text
0 3 -1
-1 [8, -2, 8, 5]
```


选题关联：来源主题 1（文末列出）。

## 二、非降序是排除范围的依据

本章二分查找要求列表非降序，即任何相邻前项都不大于后项。允许相等，所以 \[-2, 0, 0, 5\] 合格；不要求所有元素严格递增。空列表和单元素列表没有违反顺序的相邻对，约定也合格。is\_nondecreasing 通过检查相邻项来验证，发现一次下降就返回 False。

有序性使比较中间元素有用。若中间值小于目标，那么它以及更左边的值都小于目标，可以一起排除。若中间值已经不小于目标，那么第一处满足条件的位置不会在它的右边才首次出现。无序列表缺少这些推论，一次比较只能说明当前项，不能代表整半边。

只读的二分函数不会自动排序，也不在每次调用时扫描一遍验证顺序；调用者负责满足前提。对无序数据调用后碰巧得到某个下标，不能据此确认正确。若应用需要主动拒绝无序输入，可以先调用验证函数；但这次验证最坏检查 n 减 1 对，成本为 O(n)。

多次查询一份不再改变的有序列表，可以把验证放在查询组开始处。若先排序，排序本身也有成本，而且新下标属于新排列，未必是原记录的位置。对于只查一次的无序列表，先排序未必划算。把数据准备、查询和后续修改分别计入，才是在比较同一个完整任务。

**完整程序**

```python
def is_nondecreasing(values):
    for index in range(1, len(values)):
        if values[index - 1] > values[index]:
            return False
    return True

print(is_nondecreasing([-2, 0, 0, 5]))
print(is_nondecreasing([1, 8, 3, 6]))
print(is_nondecreasing([]), is_nondecreasing([7]))
```

**预期输出**

```text
True
False
True True
```


选题关联：来源主题 1（文末列出）。

## 三、二分左边界：寻找第一项不小于目标的位置

lower\_bound 返回第一个值不小于 target 的位置；若所有值都更小，返回 n。这是一个边界，允许等于列表长度，并不保证目标确实存在。我们用 left=0、right=n，把仍待判定的元素范围记作 \[left, right)，右端不包含在内；可能的答案边界则允许落在 right。

始终保持两条已知事实：left 之前的元素都小于目标，right 及之后的元素都不小于目标。初始两端外侧都没有元素，所以事实成立。中点取 left 加上区间长度整除 2；只要 left 小于 right，它就一定是合法候选下标，不会读取 values\[n\]。

中点值小于目标时，有序性允许把中点及其左边全部排除，令 left=middle+1。否则令 right=middle，保留中点作为可能的答案边界，并继续找更早的位置。每个分支都使 right 减 left 严格减少；不能写 left=middle，因为只剩一项时中点就是 left，可能永远不前进。

结束时两端相等，左侧全小于目标，右侧全不小于目标，这个分界就是答案。空输入立即返回 0；全部偏小时返回 n。下面对 \[-4, 1, 1, 6, 9\] 查询 1、4、10，边界分别为 1、3、5。第一种找到首个重复值，后两种只是定位到适合插入的地方。

**完整程序**

```python
def lower_bound(values, target):
    left = 0
    right = len(values)
    while left < right:
        middle = left + (right - left) // 2
        if values[middle] < target:
            left = middle + 1
        else:
            right = middle
    return left

values = [-4, 1, 1, 6, 9]
print(lower_bound(values, 1), lower_bound(values, 4), lower_bound(values, 10))
print(lower_bound([], 1))
```

**预期输出**

```text
1 3 5
0
```


选题关联：来源主题 1（文末列出）。

## 四、从边界得到首个精确匹配

取得左边界后，还要确认两件事：位置仍在列表内，该位置的值等于目标。binary\_first 先调用 lower\_bound，再用 and 连接这两个检查。Python 的 and 从左到右短路求值：位置已经等于 n 时，第二个索引表达式不会求值，避免越界。空列表也由同一个判断安全处理。

下面查找 1 得到边界 1，值也为 1，所以返回 1；查找 4 的边界为 3，但该项是 6，所以返回 -1。查找 -4 返回 0，空列表返回 -1。目标大于最大项时，边界等于 n，必须直接判未找到，不能先索引再补判断。

有重复值时，左边界之前已经保证全都小于目标，所以一旦边界值相等，它就是第一个匹配。这比“碰到相等立即返回”多了一层契约：后者可能返回重复区间里的任意位置。也不能见到相等后线性地向左扫描却仍声称最坏保持对数成本，重复值可能占满全表。

每轮候选元素数至多缩为原来的一半向下取整。非空长度 n 的最多轮数是 log₂n 向下取整再加 1，迭代版只保留左右端和中点，额外空间 O(1)；对增长的 n，查询最坏时间 O(log n)。这个结论不包含外部的有序性验证、排序或打印整个列表，也依赖列表下标访问的模型。

**完整程序**

```python
def lower_bound(values, target):
    left = 0
    right = len(values)
    while left < right:
        middle = left + (right - left) // 2
        if values[middle] < target:
            left = middle + 1
        else:
            right = middle
    return left

def binary_first(values, target):
    position = lower_bound(values, target)
    if position < len(values) and values[position] == target:
        return position
    return -1

values = [-4, 1, 1, 6, 9]
print(binary_first(values, 1), binary_first(values, 4), binary_first(values, -4))
print(binary_first([], 1), binary_first(values, 12))
```

**预期输出**

```text
1 -1 0
-1 -1
```


选题关联：来源主题 1（文末列出）。

## 五、右边界与重复值的数量

upper\_bound 返回第一个严格大于 target 的位置，所有值都不大于目标时返回 n。它与左边界的区别只在相等时走哪边：中点值等于目标仍归入左侧已排除部分，所以把 left 改到 middle+1；只有中点值严格更大，才把 right 移到中点。

因此结束后，左侧全都不大于目标，右侧全都大于目标。lower\_bound 与 upper\_bound 之间的半开区间恰好包含全部相等项：重复个数等于右边界减左边界。目标缺失时两个边界相同，差为零，无须额外遍历寻找重复项。

下面 \[-4, 1, 1, 1, 6, 9\] 对目标 1 的左边界为 1、右边界为 4，三个相等项占下标 1、2、3。对目标 5，两边界都为 4，虽然该位置实际存着 6，数量仍正确地为零。空列表两边界都是 0；全部值相等时，两端可以分别为 0 和 n。

两次二分的次数相加，仍为 O(log n) 的最坏查询成本，而不是相乘成平方。右边界本身通常不指向目标，最后匹配位置应从它减一后再检查。边界、元素下标和匹配数量是三个不同结果；调用之前先确认函数承诺的是哪一个。

**完整程序**

```python
def lower_bound(values, target):
    left = 0
    right = len(values)
    while left < right:
        middle = left + (right - left) // 2
        if values[middle] < target:
            left = middle + 1
        else:
            right = middle
    return left

def upper_bound(values, target):
    left = 0
    right = len(values)
    while left < right:
        middle = left + (right - left) // 2
        if values[middle] <= target:
            left = middle + 1
        else:
            right = middle
    return left

values = [-4, 1, 1, 1, 6, 9]
for target in [1, 5]:
    first = lower_bound(values, target)
    stop = upper_bound(values, target)
    print(first, stop, stop - first)
print(upper_bound([], 1) - lower_bound([], 1))
```

**预期输出**

```text
1 4 3
4 4 0
0
```


选题关联：来源主题 1（文末列出）。

<a id="examples"></a>

## 跟着做：原创例题

### 例题 1

对非降序列表 \[-3, 0, 4, 4, 4, 8, 12\]，求目标 4 的左边界，逐步记录比较前的 left、right、middle 和中点值；再查目标 13。解释两种终止位置，记录轨迹的版本不用于宣称常数辅助空间。

1. 目标 4：初始范围 \[0, 7)，中点 3 的值为 4，把 right 改为 3，继续寻找更早位置。
2. 范围 \[0, 3) 的中点为 1，值 0 小于目标，把 left 改为 2。
3. 范围 \[2, 3) 的中点为 2，值为 4，把 right 改为 2；两端重合，返回 2，共三次比较。
4. 目标 13：中点依次为 3、5、6，值都偏小，left 依次改为 4、6、7，最终返回 7。
5. 返回 7 是末尾边界，不可再索引该位置；需要精确匹配时应判未找到。保存三行轨迹额外占用空间，普通 lower\_bound 没有这份记录。

**结果与核对**

目标 4 返回 2；目标 13 返回 7。每轮区间长度从 7 变为 3、1、0，且端点更新不会跳过首个合法边界。

**完整程序**

```python
def lower_trace(values, target):
    left = 0
    right = len(values)
    trace = []
    while left < right:
        middle = left + (right - left) // 2
        trace.append([left, right, middle, values[middle]])
        if values[middle] < target:
            left = middle + 1
        else:
            right = middle
    return {"position": left, "trace": trace}

values = [-3, 0, 4, 4, 4, 8, 12]
for target in [4, 13]:
    report = lower_trace(values, target)
    print(report["position"], report["trace"])
```

**预期输出**

```text
2 [[0, 7, 3, 4], [0, 3, 1, 0], [2, 3, 2, 4]]
7 [[0, 7, 3, 4], [4, 7, 5, 8], [6, 7, 6, 12]]
```


### 例题 2

对 \[-2, 1, 1, 5, 8\] 批量查询 \[1, 7, -2, 1\] 的首个匹配下标。编写 checked\_queries，先验证非降序一次；无序时返回 None，否则按查询顺序返回列表，不改变任何输入。解释整体成本。

1. 相邻检查均未下降，可以开始查询；这一步只在整个查询组开头执行一次。
2. 目标 1 的左边界为 1，返回 1；目标 7 的边界为 4，但该处是 8，返回 -1。
3. 目标 -2 返回 0，重复查询 1 仍返回 1，查询本身不改变排列。
4. 遇到无序的 \[3, 1\] 时，验证阶段立即返回 None，表示输入前提不成立；它与合法列表中某目标缺失的 -1 不同。
5. q 次查询加一次验证：对 n 至少为 2，上界为 O(n+q log n)，另外返回 q 项结果；不能把整组工作只记成一次 O(log n)。

**结果与核对**

结果为 \[1, -1, 0, 1\]，原列表保持不变。合法空列表对每个目标返回 -1；空查询组仍执行一次约定的输入验证，然后返回空结果。

**完整程序**

```python
def is_nondecreasing(values):
    for index in range(1, len(values)):
        if values[index - 1] > values[index]:
            return False
    return True

def lower_bound(values, target):
    left = 0
    right = len(values)
    while left < right:
        middle = left + (right - left) // 2
        if values[middle] < target:
            left = middle + 1
        else:
            right = middle
    return left

def binary_first(values, target):
    position = lower_bound(values, target)
    if position < len(values) and values[position] == target:
        return position
    return -1

def checked_queries(values, targets):
    if not is_nondecreasing(values):
        return None
    result = []
    for target in targets:
        result.append(binary_first(values, target))
    return result

values = [-2, 1, 1, 5, 8]
print(checked_queries(values, [1, 7, -2, 1]))
print(values)
print(checked_queries([3, 1], [1]))
```

**预期输出**

```text
[1, -1, 0, 1]
[-2, 1, 1, 5, 8]
None
```


<a id="practice"></a>

## 自己做：先完成再看解答

### 练习 1

编写 binary\_last(values, target)，对非降序整数列表返回最后匹配下标，缺失返回 -1。检查 \[-4, 1, 1, 1, 6, 9\] 中的 1 和 7，以及空输入；不从某个匹配点逐项向右扫描。

<details>
<summary>提示</summary>

从严格大于目标的右边界减一；先确认得到的下标非负，再读值判断相等。

</details>

<details>
<summary>解答与检查</summary>

结果为 3、-1、-1。目标 1 的右边界为 4，减一得到最后一个 1；目标 7 的候选为下标 4，但该值为 6，所以缺失。空输入右边界 0 减一后为 -1，必须在索引之前排除。

**完整程序**

```python
def upper_bound(values, target):
    left = 0
    right = len(values)
    while left < right:
        middle = left + (right - left) // 2
        if values[middle] <= target:
            left = middle + 1
        else:
            right = middle
    return left

def binary_last(values, target):
    position = upper_bound(values, target) - 1
    if position >= 0 and values[position] == target:
        return position
    return -1

values = [-4, 1, 1, 1, 6, 9]
print(binary_last(values, 1), binary_last(values, 7), binary_last([], 1))
```

**预期输出**

```text
3 -1 -1
```


</details>

### 练习 2

编写 count\_closed\_range(values, low, high)，计算非降序整数列表中落在闭区间 low 到 high 的项数，两个端点都包含；low 大于 high 时返回 0。对 \[-3, 0, 0, 2, 6\] 检查区间 \[0, 2\]、\[3, 5\] 和 \[5, 3\]。

<details>
<summary>提示</summary>

左端排除所有小于 low 的项，右端排除所有大于 high 的项；用两个边界相减，不把重复值去重。

</details>

<details>
<summary>解答与检查</summary>

结果为 3、0、0。区间 \[0, 2\] 包含两个 0 和一个 2，左边界为 1，右边界为 4，差为 3。先处理反向区间，避免边界相减出现负数；空列表在任意合法区间都返回 0。

**完整程序**

```python
def lower_bound(values, target):
    left = 0
    right = len(values)
    while left < right:
        middle = left + (right - left) // 2
        if values[middle] < target:
            left = middle + 1
        else:
            right = middle
    return left

def upper_bound(values, target):
    left = 0
    right = len(values)
    while left < right:
        middle = left + (right - left) // 2
        if values[middle] <= target:
            left = middle + 1
        else:
            right = middle
    return left

def count_closed_range(values, low, high):
    if low > high:
        return 0
    return upper_bound(values, high) - lower_bound(values, low)

values = [-3, 0, 0, 2, 6]
print(count_closed_range(values, 0, 2), count_closed_range(values, 3, 5), count_closed_range(values, 5, 3))
```

**预期输出**

```text
3 0 0
```


</details>

### 练习 3

编写 inserted\_copy(values, value)，在非降序整数列表中相等项的后面插入一个新值，返回新列表，原列表不变。对 \[-2, 3, 3, 8\] 插入 3，再对空列表插入 0；分析为什么整个函数不是 O(log n)。

<details>
<summary>提示</summary>

用 upper\_bound 确定位置，再复制列表并 insert。定位和实际搬移分别计入成本。

</details>

<details>
<summary>解答与检查</summary>

插入位置为 3，新结果为 \[-2, 3, 3, 3, 8\]；空输入得到 \[0\]。二分定位是对数成本，但复制需线性工作，列表插入还可能搬移后缀，所以整体为 Θ(n+1) 时间与包含返回值的 Θ(n+1) 额外空间。

**完整程序**

```python
def upper_bound(values, target):
    left = 0
    right = len(values)
    while left < right:
        middle = left + (right - left) // 2
        if values[middle] <= target:
            left = middle + 1
        else:
            right = middle
    return left

def inserted_copy(values, value):
    position = upper_bound(values, value)
    result = values.copy()
    result.insert(position, value)
    return result

values = [-2, 3, 3, 8]
print(inserted_copy(values, 3), values)
print(inserted_copy([], 0))
```

**预期输出**

```text
[-2, 3, 3, 3, 8] [-2, 3, 3, 8]
[0]
```


</details>

<a id="pitfalls"></a>

## 容易混淆的地方

- **在无序列表上使用二分，或每次完整验证后仍宣称整次调用只有对数成本。** 有序性是排除半边的依据；显式验证最坏线性，数据准备必须计入完整流程。
- **把边界 n 当合法下标，或者把下标 0 当成查找失败。** 边界允许在末尾，读取前检查范围；精确查找以 -1 表示缺失，不能依赖真假值。
- **相等就立即返回，却声称保证第一个重复值；或用 left=middle 导致不前进。** 首匹配先求左边界；每个分支都检查区间长度严格减少，尤其验证只剩一项的情况。
- **把 upper\_bound 当作最后匹配位置，或把二分插入的总成本说成对数。** 右边界是第一项严格大于目标的位置，最后匹配需减一并核对；复制和插入搬移仍需计入。

<a id="self-check"></a>

## 离开这一章前

- [ ] 分别查空列表、单元素列表、首末值与缺失目标，说明每个返回值。
- [ ] 对全相等列表写出两个边界，并验证差值等于列表长度。
- [ ] 画出每轮半开区间，验证 left 前与 right 后的不变式。
- [ ] 区分目标缺失但处于两值之间、低于最小值、高于最大值三种边界。
- [ ] 比较一次无序查询和多次已有序查询，列出准备、查询、输出的不同成本。

## 本章边界

- 二分主体只接收已非降序整数列表，不主动修复无序输入；checked\_queries 是明确增加验证的包装。
- 不包含散列表、树索引、浮点 NaN 或自定义比较关系，不能直接推广其前提。
- 下标指向被查列表当前排列；排序之后不自动保留原位置。
- 追踪函数保存调试记录，其额外空间与只保留左右端的普通二分不同。

## 选题来源与覆盖

来源含学生报告时，仅将其作为选题线索；具体机制仍需结合后续实验或权威资料核对。

- [大一小学期/Week\_3-Python/docs/readme.md](https://github.com/PKUanonym/REKCARC-TSC-UHT/blob/37cd19f7a9fb80dc846a7016b3fd482ed5fe7cc0/%E5%A4%A7%E4%B8%80%E5%B0%8F%E5%AD%A6%E6%9C%9F/Week_3-Python/docs/readme.md)（已提取可读文本，固定版本 37cd19f7a9fb）
- 主题 1：Python 基础语法的外部学习入口；位置：第 41–80 行。
- 主题 2：从基础语法到工具与应用的建议阅读顺序；位置：第 121–160 行。

## 参考资料与规则核对

上游入口用于确定学习方向；下面的参考资料用于核对语言语义、数据结构或算法分析规则，例题和练习由本项目重新设计。

- [Python 3.11：bisect 的左右插入边界](https://docs.python.org/3.11/library/bisect.html)：核对有序前提、左右边界及插入搬移的线性成本；正文自己实现循环，数据与题目原创。
- [Python 3.11：布尔短路求值](https://docs.python.org/3.11/library/stdtypes.html#boolean-operations-and-or-not)：核对 and 从左到右短路，在确认下标有效之后才读取元素。

**继续学习**：先独立完成自测，再记录仍需回读的步骤。

[上一章：数据变多会怎样：算法分析与增长量级](10-algorithm-analysis.md) · [下一章：怎样把数据排成顺序：选择、插入与归并排序](12-sorting.md)

[教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [记录自己的学习](../learning-log-template.md)
