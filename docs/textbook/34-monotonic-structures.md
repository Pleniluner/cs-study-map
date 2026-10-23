# 淘汰不再有用的候选：单调栈与单调队列

[返回教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [哈希表与图练习指引](../hash-graphs-practice.md) · [拓扑排序与带权图练习指引](../weighted-graphs-practice.md)

[上一章：复用区间信息：前缀和、双指针与滑动窗口](33-prefix-window.md) · [下一章：动态维护前缀：树状数组与频次排名](35-fenwick-tree.md)

[学习目标](#objectives) · [需要的基础](#prerequisites) · [例题](#examples) · [练习](#practice) · [自测](#self-check)

状态：**AI 初稿，可开始试学**。生成模型：Codex 当前会话（未记录具体模型型号）。

本章围绕资料中识别到的知识点重新编写；讲解、数值模型、例题与练习为 AI 原创组织，不是原课程题目或答案。主题出处只说明选题关联，不证明全部推导已经正确。

第 33 章通过前缀和复用计算，通过双指针排除候选；本章继续追问：有些尚未处理的位置，能否因为新位置更有利而永远退出考虑？单调栈和单调队列保存的就是仍可能有用的候选。理解它们的关键不是背诵“大于时弹出”，而是分别证明已找到答案、被新候选替代、超过有效范围这三种删除理由，并确定相等值应当保留哪一个。

<a id="objectives"></a>

## 学完要能做到

- 根据严格大小关系推导栈的比较符，返回位置而非混用数值。
- 用柱状图说明出栈时能确定的矩形边界，并证明总操作次数。
- 用环形数组维护固定窗口候选，区分过期与被支配。
- 把前缀和与候选队列结合，解决含负数的最短达标区间和有长度上限的最大和。

<a id="prerequisites"></a>

## 需要的基础

- 第 8–10 章的栈、循环队列和摊还计数。
- 第 14 章的区间分解与不变式。
- 第 33 章的前缀边界、半开区间和窗口适用条件。

## 下一个严格更大值：为尚未得到答案的位置等待

对每个位置 i，寻找右边最近且数值严格更大的位置；不存在时记 None。答案是下标，不能把数值相同的两个位置当作同一个候选。依次扫描当前位置 j，栈中存放尚未得到答案的旧下标；它们的下标递增，数值从底到顶非增。

如果栈顶数值比当前值小，当前 j 就是它的答案。为什么一定最近？该位置从入栈至今一直未出栈，意味着此前扫描过的右侧值都没有首次解决它。又因为栈顶是当前未解决位置中数值较小的一端，可以连续解决若干个位置，再把 j 入栈。每次出栈都在交付答案，不是随意丢弃一个可能解。

输入 \[2,2,1,3,3\] 扫到下标 3 时，依次解决下标 2、1、0，答案都是 3。最后两个 3 没有严格更大值，保持 None。遇到相等数值不出栈，因此两个 2 能各自保留位置身份；若把比较改成允许相等，题目就变成“下一个大于或等于的值”。

空列表返回空列表，函数不修改整数输入。虽然 for 内含 while，每个下标只入栈一次、出栈至多一次，所以总时间 O(n+1)，栈和答案各占 O(n+1) 空间。一轮扫描可能连续弹出很多项，不能说每一轮最坏都是常数；线性结论来自整次扫描的总量。以下复杂度先按整数运算和比较为单位成本，Python 大整数的位数成本在章末另作说明。

**完整程序**

```python
def next_greater(values):
    answer = [None] * len(values)
    stack = []
    for i in range(len(values)):
        while len(stack) > 0 and values[stack[len(stack) - 1]] < values[i]:
            answer[stack.pop()] = i
        stack.append(i)
    return answer

print(next_greater([2, 2, 1, 3, 3]))
print(next_greater([]))
```

**预期输出**

```text
[3, 3, 3, None, None]
[]
```


选题关联：来源主题 1（文末列出）。

## 前一个严格更小值：新位置能够替代哪些旧位置

现在为当前位置 i 找左侧最近的严格更小值。扫描到 i 时，先弹掉栈顶所有大于或等于当前值的位置，再读取剩余栈顶；若栈空，答案是 None。最后把 i 压入。栈中下标递增，数值严格递增，因此剩余栈顶既满足大小要求，又是保留下标中最近的一个。

这次删除不是替旧位置找到答案，而是证明它不再有用。设旧位置 p 的值至少为当前值，未来某位置 q 若能把 p 当作严格更小的左邻候选，那么当前 i 的值也严格小于 q，且 i 更靠右。于是 p 永远不如 i。若 q 连 p 都不能选，删除 p 同样不会漏解。每次删除都有一个更近、数值不更大的替代者。

例如 \[3,2,2,4,1\] 中，第二个 2 会弹掉第一个 2。因为题目要求严格更小，它们不能互为答案；未来的 4 则应选择较新的 2，即下标 2。结果为 \[None,None,None,2,None\]。这里使用“大于或等于时弹出”，与上一节“严格小于时弹出”不同，不能只凭“单调栈”这个名字决定比较符。

更早被删除的候选要么本来不满足条件，要么有更近的替代者；沿着替代关系最终能在当前栈里找到不劣位置，所以读取栈顶不会漏掉真正最近的答案。空输入和全相等输入也遵守同一逻辑。每个下标至多入栈、出栈各一次，总时间 O(n+1)，额外空间 O(n+1)，包括返回列表。两节都只从列表尾部操作，没有把删除表头的线性移动藏进分析。

**完整程序**

```python
def previous_smaller(values):
    answer = []
    stack = []
    for i in range(len(values)):
        while len(stack) > 0 and values[stack[len(stack) - 1]] >= values[i]:
            stack.pop()
        if len(stack) == 0:
            answer.append(None)
        else:
            answer.append(stack[len(stack) - 1])
        stack.append(i)
    return answer

print(previous_smaller([3, 2, 2, 4, 1]))
print(previous_smaller([0, 0]))
```

**预期输出**

```text
[None, None, None, 2, None]
[None, None]
```


选题关联：来源主题 1（文末列出）。

## 柱状图面积：出栈时确定一个高度能延伸多远

把非负整数列表看作宽度均为 1 的柱子，求落在柱子以内、底边连续的最大矩形面积。固定一个高度后，矩形能延伸到哪里取决于两边第一次遇到更低柱子的位置。栈保存严格增高的柱子下标；扫描新柱时，只要栈顶高度至少为当前高度，就弹出并计算候选。

弹出高度 h 后，若栈非空，新的栈顶就是左侧更低的边界，矩形从该下标加 1 开始；栈为空则从 0 开始。右端暂取当前 i，宽度为 i−left，面积 h×宽度。当前柱更低时，它挡住了这个高度继续向右；当前柱等高时，先计算旧候选，再让较新的等高柱继承被腾出的左侧范围，未来仍能覆盖所有等高柱。

最后使用一个虚拟高度 0，使剩余正高度都完成计算。它只参与扫描，不追加到输入列表，也不压入栈。零高度被弹出只得到面积 0，不影响最大值。例如 \[2,2,1,3,3\] 的最后两根柱形成宽 2、高 3 的矩形，最大面积为 6；覆盖全宽的高度 1 只能得到 5。

任意最优矩形都可以把高度提高到区间内最低柱高，再左右延伸至无法继续。因此它对应某个最低高度被处理时的候选；等高合并保留了这种延伸能力。函数先完整检查非负性，负高度返回 None，空输入或全零返回 0，只交付面积，不恢复坐标。含验证、末尾清栈和扫描，总时间 O(n+1)，辅助栈 O(n+1)。乘法与面积比较若涉及巨大整数，还要计入实际位运算成本。

**完整程序**

```python
def histogram_area(heights):
    for height in heights:
        if height < 0:
            return None
    best = 0
    stack = []
    for i in range(len(heights) + 1):
        current = 0
        if i < len(heights):
            current = heights[i]
        while len(stack) > 0 and heights[stack[len(stack) - 1]] >= current:
            height = heights[stack.pop()]
            left = 0
            if len(stack) > 0:
                left = stack[len(stack) - 1] + 1
            area = height * (i - left)
            if area > best:
                best = area
        if i < len(heights):
            stack.append(i)
    return best

print(histogram_area([2, 2, 1, 3, 3]))
print(histogram_area([]), histogram_area([0, 0]))
print(histogram_area([2, -1]))
```

**预期输出**

```text
6
0 0
None
```


选题关联：来源主题 1（文末列出）。

## 固定窗口最大值：队头过期，队尾淘汰

对每个长度 width 的窗口返回最大值的下标；最大值重复时选最新位置。队列只保存可能成为窗口最大值的候选，下标从头到尾递增，数值严格递减。当前位置 i 的窗口左端为 i−width+1，队头若早于它便过期；随后从队尾删除数值不大于当前值的候选，最后加入 i。

队尾删除的理由是：新值不小于旧值，同时新位置更晚过期。在两者共同出现的任何未来窗口中，新位置都不差；等值时题目又要求较新下标，因此旧候选可以永久删除。队头删除则与大小无关，只因它已不在合法窗口。候选不必包含窗口所有元素，队头仍保存真正的最大值。

示例 \[4,4,2,5,5,1\]、宽度 3 的答案为 \[1,3,4,4\]。第一个窗口的两个 4 选下标 1，第三个窗口的两个 5 选下标 4。若要求最早最大值，下标保留规则就必须调整，不能只改答案说明。

程序用容量 width 的环形列表保存双端候选，以 head 和 count 表示有效部分，尾部位置通过取模计算。先移除过期项保证加入当前项之前至多有 width−1 个候选，容量不会溢出；弹尾只减 count，旧槽内容不属于有效队列。整数宽度必须在 1 到 n 之间，否则返回 None，空输入也没有合法窗口。每个下标进入一次并退出至多一次，初始化和扫描合计 O(n+1) 时间；工作队列 O(width)，另有 n−width+1 项输出。不能用列表 pop(0) 后仍声称每次出队常数。

**完整程序**

```python
def window_max_indices(values, width):
    if width <= 0 or width > len(values):
        return None
    queue = [0] * width
    head = 0
    count = 0
    answer = []
    for i in range(len(values)):
        while count > 0 and queue[head] <= i - width:
            head = (head + 1) % width
            count = count - 1
        while count > 0 and values[queue[(head + count - 1) % width]] <= values[i]:
            count = count - 1
        queue[(head + count) % width] = i
        count = count + 1
        if i + 1 >= width:
            answer.append(queue[head])
    return answer

print(window_max_indices([4, 4, 2, 5, 5, 1], 3))
print(window_max_indices([2, 2], 1))
print(window_max_indices([], 1))
```

**预期输出**

```text
[1, 3, 4, 4]
[0, 1]
None
```


选题关联：来源主题 1（文末列出）。

## 含负数的最短达标区间：在前缀边界上维护候选

列表允许负数，目标 target 可以是任意整数，求和至少为目标的最短非空区间。第 33 章的非负窗口证明已经不适用；现在写成前缀差 P\[stop\]−P\[start\]，并让队列保存严格更早的候选 start，使它们的前缀值严格递增。

每到一个终点 stop，先检查队头是否达标。如果达标，比较长度并弹出队头，继续尝试后面的起点。该起点已得到以当前终点结束的合法区间，以后终点更晚只会更长，所以可以退休。如果队头不达标，后面的前缀值更大，差值更小，也都不达标。

接着从队尾删除前缀值至少为 P\[stop\] 的旧起点，再把 stop 加入。新起点更晚且前缀值不更大，对未来终点能给出不小的区间和与更短长度，因而严格占优。这两类删除先后有别：先结算以 stop 结束的答案，最后才把 stop 变成未来的起点，保证不选空区间。目标为零或负数也不能省掉这项顺序。

\[1,−1,5\] 对目标 5 返回 \[2,3)，\[-2,0\] 对目标 0 返回 \[1,2)。无解或空输入返回 \[\]。长度相同只保留先发现者，由于终点递增，这也保留最早起点。代码以列表加 head 模拟队头移动，已经退出的表头槽不会马上回收，但总加入次数只有 n+1；加上完整前缀表，时间和空间均为 O(n+1)。它没有固定宽度的容量约束，不能把上一节 O(width) 的空间结论直接挪过来。

**完整程序**

```python
def shortest_signed_window(values, target):
    prefix = [0]
    for value in values:
        prefix.append(prefix[len(prefix) - 1] + value)
    queue = []
    head = 0
    best = []
    for stop in range(len(prefix)):
        while head < len(queue) and prefix[stop] - prefix[queue[head]] >= target:
            start = queue[head]
            if len(best) == 0 or stop - start < best[1] - best[0]:
                best = [start, stop]
            head = head + 1
        while head < len(queue) and prefix[queue[len(queue) - 1]] >= prefix[stop]:
            queue.pop()
        queue.append(stop)
    return best

print(shortest_signed_window([1, -1, 5], 5))
print(shortest_signed_window([-2, 0], 0))
print(shortest_signed_window([], -3))
```

**预期输出**

```text
[2, 3]
[1, 2]
[]
```


选题关联：来源主题 1（文末列出）。

<a id="examples"></a>

## 跟着做：原创例题

### 例题 1

在三行四列的二值矩阵 \[\[1,0,1,1\],\[1,1,1,1\],\[0,1,1,1\]\] 中寻找最大全 1 矩形面积。怎样利用柱状图程序，而不枚举全部四条边？

1. 固定矩形底边所在行，把各列向上连续的 1 的数量当作柱高。第一行得到 \[1,0,1,1\]。
2. 读第二行时，遇 1 加一，遇 0 归零，得到 \[2,1,2,2\]。
3. 第三行高度为 \[0,2,3,3\]，其中最后两列高 3、宽 2，面积 6；后三列高 2、宽 3，也为 6。
4. 每个全 1 矩形都有一条底边，所以逐行求柱状图最优值并取最大，覆盖全部可能答案。

**结果与核对**

最大面积为 6。函数先验证每行等宽且元素属于 0、1，非法返回 None；空矩阵、零列矩阵返回 0。设行数 R、列数 C，完整验证和逐行处理的时间 O(RC+R+1)，辅助高度与栈 O(C+1)，不复制或修改矩阵。即使 C 为零仍需检查 R 行，不能漏掉这个成本。独立核验会枚举矩形四条边并逐格检查。

**完整程序**

```python
def histogram_area(heights):
    for height in heights:
        if height < 0:
            return None
    best = 0
    stack = []
    for i in range(len(heights) + 1):
        current = 0
        if i < len(heights):
            current = heights[i]
        while len(stack) > 0 and heights[stack[len(stack) - 1]] >= current:
            height = heights[stack.pop()]
            left = 0
            if len(stack) > 0:
                left = stack[len(stack) - 1] + 1
            area = height * (i - left)
            if area > best:
                best = area
        if i < len(heights):
            stack.append(i)
    return best

def ones_rectangle(rows):
    if len(rows) == 0:
        return 0
    width = len(rows[0])
    for row in rows:
        if len(row) != width:
            return None
        for value in row:
            if value != 0 and value != 1:
                return None
    heights = [0] * width
    best = 0
    for row in rows:
        for i in range(width):
            if row[i] == 0:
                heights[i] = 0
            else:
                heights[i] = heights[i] + 1
        area = histogram_area(heights)
        if area > best:
            best = area
    return best

rows = [[1, 0, 1, 1], [1, 1, 1, 1], [0, 1, 1, 1]]
print(ones_rectangle(rows))
print(ones_rectangle([[], []]))
print(ones_rectangle([[1], [1, 0]]))
```

**预期输出**

```text
6
0
None
```


### 例题 2

测量值依次为 \[8,6,6,7,5,9\]。对每一天，求以当天结束、所有值都不大于当天值的最长连续天数，解释重复值的处理。

1. 当前天本身总能计入，因此非空输入的每个答案至少为 1。
2. 往左扩展时，第一个严格大于当天值的位置是阻挡；弹掉不大于当天值的候选，剩余栈顶正是这个阻挡。
3. 第三天数值 6 可以包含前一天的 6，但不能越过 8，跨度为 2；第四天的 7 可以包含两个 6，跨度为 3。
4. 最后的 9 大于此前全部值，没有阻挡，跨度为 6。

**结果与核对**

结果为 \[1,1,2,3,1,6\]。这些连续值只需各自不超过当天值，相邻两天不必单调，所以不要把题目读成“最长非降连续段”。有阻挡时长度是 i−阻挡下标，无阻挡以 −1 作边界，长度为 i+1。等值不构成阻挡，必须弹出。每个位置入栈、出栈至多一次，时间和含答案空间均为 O(n+1)；空输入返回 \[\]。

**完整程序**

```python
def upper_bounded_span(values):
    stack = []
    answer = []
    for i in range(len(values)):
        while len(stack) > 0 and values[stack[len(stack) - 1]] <= values[i]:
            stack.pop()
        previous = -1
        if len(stack) > 0:
            previous = stack[len(stack) - 1]
        answer.append(i - previous)
        stack.append(i)
    return answer

print(upper_bounded_span([8, 6, 6, 7, 5, 9]))
print(upper_bounded_span([]))
```

**预期输出**

```text
[1, 1, 2, 3, 1, 6]
[]
```


<a id="practice"></a>

## 自己做：先完成再看解答

### 练习 1

把列表看作一个环，每个位置向右最多查看其余 n−1 个位置，找第一个严格更大的值的原下标。求 \[3,1,2\]；没有答案用 None。

<details>
<summary>提示</summary>

把扫描延伸到两圈，用余数恢复原下标，但只在第一圈把待解决下标入栈。严格比较使位置不会以自身作为答案。

</details>

<details>
<summary>解答与检查</summary>

答案为 \[None,2,0\]。第一圈未解决的下标，在第二圈中只能被绕回来的更大值解决；若一整圈仍没有更大值，以后也不会出现新答案。每个位置只入栈一次，两圈共 2n 次扫描，时间和空间 O(n+1)。全相等时全部为 None；空列表的循环次数为零，不会执行对零取模。返回仍是原列表下标，不是展开后的下标。

**完整程序**

```python
def circular_next_greater(values):
    size = len(values)
    answer = [None] * size
    stack = []
    for step in range(2 * size):
        i = step % size
        while len(stack) > 0 and values[stack[len(stack) - 1]] < values[i]:
            answer[stack.pop()] = i
        if step < size:
            stack.append(i)
    return answer

print(circular_next_greater([3, 1, 2]))
print(circular_next_greater([2, 2]))
print(circular_next_greater([]))
```

**预期输出**

```text
[None, 2, 0]
[None, None]
[]
```


</details>

### 练习 2

求每个固定窗口的极差，即最大值减最小值。沿用窗口宽度检查，求 \[4,4,2,5,5,1\]、宽度 3。

<details>
<summary>提示</summary>

对原列表找最大值下标，再对逐项取负的新列表找最大值下标，它们对应原列表的最小值位置。

</details>

<details>
<summary>解答与检查</summary>

结果为 \[2,3,3,4\]，宽度 1 的极差全为 0。两次扫描各自满足单调队列证明，时间 O(n+1)。此实现保存取负副本、两份下标结果及极差结果，所以总额外空间 O(n+width)，不是只有 O(width)；若要压缩这些副本，需要把最大和最小队列放在同一次扫描里。非法宽度返回 None，原始值不变，负数也允许。

**完整程序**

```python
def window_max_indices(values, width):
    if width <= 0 or width > len(values):
        return None
    queue = [0] * width
    head = 0
    count = 0
    answer = []
    for i in range(len(values)):
        while count > 0 and queue[head] <= i - width:
            head = (head + 1) % width
            count = count - 1
        while count > 0 and values[queue[(head + count - 1) % width]] <= values[i]:
            count = count - 1
        queue[(head + count) % width] = i
        count = count + 1
        if i + 1 >= width:
            answer.append(queue[head])
    return answer

def window_spreads(values, width):
    if width <= 0 or width > len(values):
        return None
    negatives = []
    for value in values:
        negatives.append(-value)
    largest = window_max_indices(values, width)
    smallest = window_max_indices(negatives, width)
    result = []
    for i in range(len(largest)):
        result.append(values[largest[i]] - values[smallest[i]])
    return result

print(window_spreads([4, 4, 2, 5, 5, 1], 3))
print(window_spreads([-3, 2], 1))
print(window_spreads([1], 0))
```

**预期输出**

```text
[2, 3, 3, 4]
[0, 0]
None
```


</details>

### 练习 3

在整数列表中找长度不超过正整数 limit 的最大和非空区间。平局先选最小起点，再选最小终点。求 \[0,2,−1,2\]、limit=3，并处理全负数。

<details>
<summary>提示</summary>

固定终点 stop，合法起点位于 \[max(0,stop−limit),stop)。从这些前缀值里找最小者。相同前缀值保留更早起点，所以弹尾只删除严格更大的前缀。

</details>

<details>
<summary>解答与检查</summary>

答案为 sum=3、区间 \[1,4)。每步先移除过期起点，再加入 stop−1，队头就是最小前缀且同值最早的起点。只用真实非空候选初始化答案，全负数也会返回最大负数；空输入或非正上限返回 None，上限超过 n 允许。对于 \[0,0\] 保留 \[0,1)，而非空段或更晚零段。前缀表和保留旧表头槽的队列均占 O(n+1)，时间 O(n+1)。独立枚举所有合法区间，按“和降序、起点升序、终点升序”比较可核对平局。

**完整程序**

```python
def bounded_max_sum(values, limit):
    if limit <= 0 or len(values) == 0:
        return None
    prefix = [0]
    for value in values:
        prefix.append(prefix[len(prefix) - 1] + value)
    queue = []
    head = 0
    best = None
    for stop in range(1, len(prefix)):
        while head < len(queue) and queue[head] < stop - limit:
            head = head + 1
        candidate = stop - 1
        while head < len(queue) and prefix[queue[len(queue) - 1]] > prefix[candidate]:
            queue.pop()
        queue.append(candidate)
        start = queue[head]
        total = prefix[stop] - prefix[start]
        if best is None or total > best['sum'] or (total == best['sum'] and start < best['start']):
            best = {'sum': total, 'start': start, 'stop': stop}
    return best

print(bounded_max_sum([0, 2, -1, 2], 3))
print(bounded_max_sum([-4, -2, -2], 2))
print(bounded_max_sum([0, 0], 2))
print(bounded_max_sum([], 2))
```

**预期输出**

```text
{'sum': 3, 'start': 1, 'stop': 4}
{'sum': -2, 'start': 1, 'stop': 2}
{'sum': 0, 'start': 0, 'stop': 1}
None
```


</details>

<a id="pitfalls"></a>

## 容易混淆的地方

- **把所有单调结构的等值情况写成同一个比较符。** 先写严格大小要求与平局规则；最新最大值、最早起点和严格更小邻居各有不同的删除条件。
- **为删除队头反复调用 pop(0)，仍声称线性总时间。** 固定窗口用环形槽，前缀候选用 head 移动；同时把保留的旧槽计入空间。
- **含负数时继续用非负和窗口，或在目标非正时把当前前缀先加入。** 在前缀候选上分别证明达标退休与支配删除，查询在入队之前以排除空段。
- **最大和从零初始化，或者把跨度理解为相邻非降。** 非空最大和可能为负；连续跨度只要求所有元素不超过当天值。

<a id="self-check"></a>

## 离开这一章前

- [ ] 对 \[2,2,1,3,3\] 画出每次出栈，注明是交付答案还是永久淘汰。
- [ ] 解释柱状图中等高旧柱出栈后，其左侧延伸能力由谁保留。
- [ ] 手算宽度 1 的环形队列，确认先过期再插入不会越界。
- [ ] 用目标 −1、输入 \[−2\] 检查最短窗口是否错误返回空段。
- [ ] 比较两个零的最短达标与最大和问题，说明为何其等值处理不同。

## 本章边界

- 接口约定列表元素、目标、宽度为整数；检查语义与范围，不做任意对象类型转换。
- 这里只处理静态扫描和特定窗口，未实现可任意删除的通用双端队列接口或二维动态范围查询。
- 线性总量按单位整数成本分析；前缀和、面积、下标和巨大目标的算术、比较及存储还需计入位数。

## 选题来源与覆盖

来源含学生报告时，仅将其作为选题线索；具体机制仍需结合后续实验或权威资料核对。

- [大一小学期/Week\_3-Python/docs/readme.md](https://github.com/PKUanonym/REKCARC-TSC-UHT/blob/37cd19f7a9fb80dc846a7016b3fd482ed5fe7cc0/%E5%A4%A7%E4%B8%80%E5%B0%8F%E5%AD%A6%E6%9C%9F/Week_3-Python/docs/readme.md)（已提取可读文本，固定版本 37cd19f7a9fb）
- 主题 1：Python 基础语法的外部学习入口；位置：第 41–80 行。
- 主题 2：从基础语法到工具与应用的建议阅读顺序；位置：第 121–160 行。

## 参考资料与规则核对

上游入口用于确定学习方向；下面的参考资料用于核对语言语义、数据结构或算法分析规则，例题和练习由本项目重新设计。

- [USACO Guide：单调栈](https://usaco.guide/gold/stacks)：核对最近更小位置的候选替代理由和总入出栈次数；本章自定严格关系、下标输出及等值示例，未移植页面程序和题目。
- [USACO Guide：滑动窗口](https://usaco.guide/gold/sliding-window)：核对单调队列的过期和支配删除概念；本章使用自行编写的环形列表实现，另行证明最新最大值和含负数的前缀候选契约。
- [Algorithms for Competitive Programming：最小栈与最小队列](https://cp-algorithms.com/data_structures/stack_queue_modification.html)：仅参考候选不必保存全队列的抽象与摊还计数；矩阵、跨度和限长最大和例题及独立穷举均由本项目设计。

**继续学习**：先独立完成自测，再记录仍需回读的步骤。

[上一章：复用区间信息：前缀和、双指针与滑动窗口](33-prefix-window.md) · [下一章：动态维护前缀：树状数组与频次排名](35-fenwick-tree.md)

[教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [哈希表与图练习指引](../hash-graphs-practice.md) · [拓扑排序与带权图练习指引](../weighted-graphs-practice.md) · [记录自己的学习](../learning-log-template.md)
