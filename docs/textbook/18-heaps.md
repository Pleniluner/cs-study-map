# 让最值留在根部：二叉堆与优先队列

[返回教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [哈希表与图练习指引](../hash-graphs-practice.md)

[上一章：用大小约束引导查找：二叉搜索树](17-binary-search-trees.md) · [下一章：按键定位记录：哈希表、冲突与扩容](19-hash-tables.md)

[学习目标](#objectives) · [需要的基础](#prerequisites) · [例题](#examples) · [练习](#practice) · [自测](#self-check)

状态：**AI 初稿，可开始试学**。生成模型：Codex 当前会话（未记录具体模型型号）。

本章围绕资料中识别到的知识点重新编写；讲解、数值模型、例题与练习为 AI 原创组织，不是原课程题目或答案。主题出处只说明选题关联，不证明全部推导已经正确。

普通队列按到达顺序服务，二叉搜索树适合按键查找；若每次只需要取出当前最小任务，优先队列提供更直接的接口。本章用列表表示完全二叉树，实现最小堆的查看、插入和删除，再说明怎样从整批数据线性建堆。最后把同样的修复思想用于最大堆排序、保留最大的若干项和合并多路有序数据。每一步都核对形状、父子约束和元素重数，并区分堆调整本身的成本、Python 列表扩容和保存输出的成本。

<a id="objectives"></a>

## 学完要能做到

- 用零基下标定位父子，说明完全形状与堆序是两个条件。
- 实现上浮、选择较小孩子的下沉，以及空堆、单元素的取出约定。
- 按子树高度累加工作，解释自底向上建堆为何是线性时间。
- 维护堆排序的有效前缀与有序后缀，分析最坏时间和稳定性。
- 用堆处理最大的 k 项与多路归并，核对重复值、输入保持和输出成本。

<a id="prerequisites"></a>

## 需要的基础

- 掌握列表、交换、半开区间、排序和第 16 章完全二叉树；示例使用 Python 3.11+。
- 普通堆只存整数，None 表示空堆无结果；多路归并练习另说明整数列表的比较规则。
- 入堆、取出和取最小值要求输入已为最小堆；建堆与堆排序接受任意整数列表，修改输入并返回 None。
- 把比较与引用操作看作单位成本，动态列表扩缩容按摊还成本另外说明。

## 一、列表中的完全二叉树只保证父子有序

二叉堆把完全二叉树按层排进连续列表，不为缺失位置留中间洞。根下标为 0，下标 i 的左、右孩子分别为 2i+1、2i+2，只有小于列表长度的下标才存在。非根结点的父下标为 (i-1)//2；根没有父亲，不能把 i=0 代入后用负下标访问列表末尾。

最小堆要求每个父值不大于已有孩子。沿任意根到后代的路径逐次使用这个关系，就知道根不大于任何元素。它不要求左右兄弟有序，也不要求左侧所有值小于右侧。例子 \[1,4,2,9,7,3\] 是最小堆：4 可以出现在 2 前面，末项 3 也不是最大值。堆顶之外的任意查找没有搜索树那样的整侧排除规则。

heap\_peek 只读取堆顶，空堆返回 None；检查函数则逐个比较非根结点与父结点。前者为 O(1)，后者最坏 Θ(n+1)，二者不要混为每次操作都扫描整堆。实际插入和取出依赖调用前的堆序，只修复可能损坏的一条路径。重复整数允许保留多份，因此比较规则包含相等。

本章的“堆”是优先队列的数据结构，与前面讨论内存分配时的堆存储区不是同一概念。最小优先队列按数值选出最小项，不按插入先后决定全部顺序；若记录有相同优先级且要求先来先服务，还需要明确的平局规则。我们先用整数避免把记录的比较方式与结构维护混在一起。

**完整程序**

```python
def is_min_heap(heap):
    for index in range(1, len(heap)):
        parent = (index - 1) // 2
        if heap[parent] > heap[index]:
            return False
    return True

def heap_peek(heap):
    if len(heap) == 0:
        return None
    return heap[0]

heap = [1, 4, 2, 9, 7, 3]
print(is_min_heap(heap), heap_peek(heap))
print(heap)
print(is_min_heap([2, 1]), is_min_heap([]), heap_peek([]))
```

**预期输出**

```text
True 1
[1, 4, 2, 9, 7, 3]
False True None
```


选题关联：来源主题 1（文末列出）。

## 二、末尾插入，只沿祖先路径上浮

插入先在列表末尾追加新值，这恰好占据完全树下一个合法位置，形状无需额外修复。原来所有父子关系都还成立，唯一可能出现的问题是新值比父值小。于是比较当前位置与父位置：父不大于当前值就结束，否则交换两处，再把当前下标移到父亲，继续向上检查。

为什么交换后只需继续向上？原父值本来不大于它原来的后代，把它放到较低位置后，沿这条路径之外的关系仍然成立；较小的新值上升，也不会破坏它与另一侧孩子的关系。每次下标严格移向根，根无父亲时结束。因此不是从任意位置反复扫描，而是维护一个明确的局部缺口。

从空堆依次加入 7、2、6、1，列表分别成为 \[7\]、\[2,7\]、\[2,7,6\]、\[1,2,6,7\]。最后的 1 从下标 3 上浮到 1，再到 0；6 无需跨到左侧才能保持堆序。heap\_push 修改原列表，正常返回 None；相等时不继续交换，仍保留重复项的数量。

完全树的高度为对数，上浮的值比较与交换最坏 O(log(n+1)+1)，循环额外状态为 O(1)。Python 列表 append 偶尔扩容会移动线性数量引用，所以不能把包含分配的每一次真实调用都说成严格对数时间；在操作序列中计入摊还扩容成本，插入仍为摊还 O(log(n+1)+1)。堆存储的 n 项本身也不属于常数空间。

**完整程序**

```python
def heap_swap(heap, left, right):
    saved = heap[left]
    heap[left] = heap[right]
    heap[right] = saved

def sift_up(heap, index):
    while index > 0:
        parent = (index - 1) // 2
        if heap[parent] <= heap[index]:
            return
        heap_swap(heap, parent, index)
        index = parent

def heap_push(heap, value):
    heap.append(value)
    sift_up(heap, len(heap) - 1)

heap = []
for value in [7, 2, 6, 1]:
    heap_push(heap, value)
    print(heap)
print(heap_push(heap, 2), heap)
```

**预期输出**

```text
[7]
[2, 7]
[2, 7, 6]
[1, 2, 6, 7]
None [1, 2, 6, 7, 2]
```


选题关联：来源主题 1（文末列出）。

## 三、用末项补根，再向较小的孩子下沉

取最小值先保存根，再删除列表末项。若此时列表为空，原堆只有一项，直接返回保存的最小值；否则把取出的末项放到根。这样完全形状仍成立，根的两棵子树各自也仍是堆，唯一可能损坏的是新根与孩子之间的关系。不能从表头直接 pop 后把其他元素整体前移，那会改变大量父子关系。

下沉先找较小的孩子，再与当前值比较。若当前值已不大于较小孩子，它也不大于另一个孩子，可以结束；否则与较小孩子交换，再在该孩子的位置继续。同样小的两个孩子选择左边即可。若随意与较大的孩子换，较小孩子可能仍小于新父，局部约束就没有修好。

sift\_down 的 size 表示有效前缀 \[0,size)，不是整个底层列表一定都参加调整。仅有左孩子时也必须处理；只有下标合法后才能读右孩子。每轮要么立即返回，要么向下移动一层，额外状态为常数。最坏调整层数为对数，每层最多进行一次孩子间比较和一次父子比较，比较数不能直接等同于层数。

对 \[1,2,6,7,2\]，弹出 1 后用末尾 2 补根，得到 \[2,2,6,7\]，父子关系已经满足。连续取出得到 1、2、2、6、7，空堆再取返回 None 且仍为空。教材的空堆约定与标准库 heapq 的抛出 IndexError 不同。列表末尾 pop 的扩缩容也按摊还成本计，不改变调整路径的对数比较上界。

**完整程序**

```python
def heap_swap(heap, left, right):
    saved = heap[left]
    heap[left] = heap[right]
    heap[right] = saved

def sift_down(heap, index, size):
    while 2 * index + 1 < size:
        child = 2 * index + 1
        right = child + 1
        if right < size and heap[right] < heap[child]:
            child = right
        if heap[index] <= heap[child]:
            return
        heap_swap(heap, index, child)
        index = child

def heap_pop(heap):
    if len(heap) == 0:
        return None
    smallest = heap[0]
    last = heap.pop()
    if len(heap) > 0:
        heap[0] = last
        sift_down(heap, 0, len(heap))
    return smallest

heap = [1, 2, 6, 7, 2]
while len(heap) > 0:
    print(heap_pop(heap), heap)
print(heap_pop(heap), heap)
```

**预期输出**

```text
1 [2, 2, 6, 7]
2 [2, 7, 6]
2 [6, 7]
6 [7]
7 []
None []
```


选题关联：来源主题 1（文末列出）。

## 四、自底向上建堆，要把不同高度的工作相加

给定任意列表，可以反复插入建堆，最坏花 O(n log n)；也可以直接在原列表自底向上修复。下标从 n//2 开始的结点都是叶子，单个叶子天然是堆。于是从最后一个内部结点 n//2-1 开始，倒着走到根，对每个位置调用下沉。处理一个位置时，它两侧更大下标的子树已经是堆，正好满足下沉前提。

不能把每个结点都按整树高度收费。叶子不下沉，接近底层的内部结点最多走一两层，只有很少的上层结点能走很多层。换一种记账方式：能支付第一层下降的结点有 floor(n/2) 个，能支付第二层的有 floor(n/4) 个，依次累加，小于 n。每层至多两次值比较，所以所有下沉工作的总上界为线性。

外层本身遍历约一半结点，完整建堆的时间为 Θ(n+1)，循环辅助空间 O(1)，没有递归和新建整份副本。空表或单项的 range 自然为空，保持原样并返回 None。例题会逐步记录 \[9,4,7,1,3,6\] 的三个内部位置，区分“下面已经修好”与“整个列表已经有序”。

自底向上法得到的堆数组不一定与逐个插入或标准库的内部数组完全一样，多个合法布局可以表示相同的元素集合。验证应检查每条父子约束、元素重数及连续取出的顺序；只有追踪特定实现时才逐字比较数组。若为了观察每一步额外复制整个列表，轨迹存储和复制时间都要另算，不能继续套用普通建堆的常数辅助空间。

**完整程序**

```python
def heap_swap(heap, left, right):
    saved = heap[left]
    heap[left] = heap[right]
    heap[right] = saved

def sift_down(heap, index, size):
    while 2 * index + 1 < size:
        child = 2 * index + 1
        right = child + 1
        if right < size and heap[right] < heap[child]:
            child = right
        if heap[index] <= heap[child]:
            return
        heap_swap(heap, index, child)
        index = child

def heapify(heap):
    for index in range(len(heap) // 2 - 1, -1, -1):
        sift_down(heap, index, len(heap))

values = [9, 4, 7, 1, 3, 6]
print(heapify(values), values)
empty = []
print(heapify(empty), empty)
single = [0]
print(heapify(single), single)
```

**预期输出**

```text
None [1, 3, 6, 4, 9, 7]
None []
None [0]
```


选题关联：来源主题 1（文末列出）。

## 五、最大堆排序维护有效前缀与有序后缀

若要在原列表内升序排序，可以把比较方向反过来建立最大堆：父值不小于孩子，根就是当前最大值。将根与有效范围末项交换，最大值便到达最终位置；随后把有效长度减一，只在剩余前缀下沉新的根。末尾已完成的位置不再参与堆调整，否则会把已经排好的后缀重新破坏。

循环开始时，前缀 \[0,end+1) 是最大堆，后缀 \[end+1,n) 已按非降序排好，且不小于前缀所有值。交换后，当前最大值落在 end；对 \[0,end) 修复堆序，就把这个不变式推进到下一轮。最大堆下沉要选择较大的孩子，停止条件也反向，不能只把最小堆代码的一处比较改掉。

建堆线性，随后至多 n-1 次下沉各花对数成本，最坏时间 Θ(n log n)，循环辅助空间 O(1)，整个排序修改输入并返回 None。此实现遇到相等值会提前结束下沉，全相等数据可以是线性时间；“最坏”不意味着每个输入都执行同样多工作。与固定基准快排相比，这里有最坏时间上界，但不保证每个实际任务耗时更少。

交换根与末项可能颠倒相等记录。设两个比较键都是 2，身份依次 A、B，建堆无需交换，排序的根末交换却会变为 B、A，因此本实现不稳定。对整数看不见身份变化，测试必须额外带标签观察。例题与练习还会用最小堆返回新列表；那种接口要计入副本和输出，不能沿用本节原地版本的空间结论。

**完整程序**

```python
def heap_swap(heap, left, right):
    saved = heap[left]
    heap[left] = heap[right]
    heap[right] = saved

def sift_down_max(values, index, size):
    while 2 * index + 1 < size:
        child = 2 * index + 1
        right = child + 1
        if right < size and values[right] > values[child]:
            child = right
        if values[index] >= values[child]:
            return
        heap_swap(values, index, child)
        index = child

def heap_sort(values):
    for index in range(len(values) // 2 - 1, -1, -1):
        sift_down_max(values, index, len(values))
    for end in range(len(values) - 1, 0, -1):
        heap_swap(values, 0, end)
        sift_down_max(values, 0, end)

values = [4, -2, 4, 0, 9, 1]
print(heap_sort(values), values)
empty = []
print(heap_sort(empty), empty)
```

**预期输出**

```text
None [-2, 0, 1, 4, 4, 9]
None []
```


选题关联：来源主题 1（文末列出）。

<a id="examples"></a>

## 跟着做：原创例题

### 例题 1

对 \[9,4,7,1,3,6\] 执行自底向上最小堆构造，按处理下标记录完整快照。手算各次下沉的值比较数，并说明保存快照后时间和空间为何改变。

1. 最后一个内部位置是 2，只有下标 5 的孩子 6；一次父子比较后交换，得到 \[9,4,6,1,3,7\]。
2. 处理下标 1，比较孩子 1 与 3，再比较父 4 与较小者 1，两次比较后得到 \[9,1,6,4,3,7\]。
3. 处理根 9，先与孩子 1 交换，再在下标 1 与较小孩子 3 交换，两层共四次比较。
4. 三次下沉共做 7 次值比较，最终 \[1,3,6,4,9,7\] 满足堆序但不是全局有序列表。
5. 快照复制三次完整列表；一般 n 项有 floor(n/2) 份长度 n 的副本，轨迹版本需二次复制时间与存储。

**结果与核对**

处理顺序为 2、1、0，比较数为 1、2、4，总计 7。普通建堆仍是线性时间和常数辅助状态；本例用于追踪的完整快照另收费，且每份都必须是独立副本。

**完整程序**

```python
def heap_swap(heap, left, right):
    saved = heap[left]
    heap[left] = heap[right]
    heap[right] = saved

def sift_down(heap, index, size):
    while 2 * index + 1 < size:
        child = 2 * index + 1
        right = child + 1
        if right < size and heap[right] < heap[child]:
            child = right
        if heap[index] <= heap[child]:
            return
        heap_swap(heap, index, child)
        index = child

def heapify_trace(heap):
    steps = []
    for index in range(len(heap) // 2 - 1, -1, -1):
        sift_down(heap, index, len(heap))
        steps.append([index, heap.copy()])
    return steps

heap = [9, 4, 7, 1, 3, 6]
for step in heapify_trace(heap):
    print(step)
```

**预期输出**

```text
[2, [9, 4, 6, 1, 3, 7]]
[1, [9, 1, 6, 4, 3, 7]]
[0, [1, 3, 6, 4, 9, 7]]
```


### 例题 2

从空堆开始加入 5、-1、5，取出一次，再加入 0，最后取空。说明优先顺序、重复值重数和调用后列表状态；空堆再取如何处理？

1. 前三次加入后堆为 \[-1,5,5\]，两个 5 都保留。
2. 第一次返回 -1，堆中剩下两个 5；它比先到的 5 更早被取出，符合最小优先规则。
3. 加入 0 后堆为 \[0,5,5\]，新加入的 0 又成为下一个最小项。
4. 继续返回 0、5、5，两个相同整数分别占一次取出；每次只减少一个元素。
5. 空堆返回 None，不产生新的元素，也不改变空列表。

**结果与核对**

完整取出顺序为 -1、0、5、5，过程中不能把重复值去重成集合。整数堆不提供相等记录的先来先服务保证；若任务需要这种语义，应显式增加次序字段。

**完整程序**

```python
def heap_swap(heap, left, right):
    saved = heap[left]
    heap[left] = heap[right]
    heap[right] = saved

def sift_up(heap, index):
    while index > 0:
        parent = (index - 1) // 2
        if heap[parent] <= heap[index]:
            return
        heap_swap(heap, parent, index)
        index = parent

def heap_push(heap, value):
    heap.append(value)
    sift_up(heap, len(heap) - 1)

def sift_down(heap, index, size):
    while 2 * index + 1 < size:
        child = 2 * index + 1
        right = child + 1
        if right < size and heap[right] < heap[child]:
            child = right
        if heap[index] <= heap[child]:
            return
        heap_swap(heap, index, child)
        index = child

def heap_pop(heap):
    if len(heap) == 0:
        return None
    smallest = heap[0]
    last = heap.pop()
    if len(heap) > 0:
        heap[0] = last
        sift_down(heap, 0, len(heap))
    return smallest

heap = []
for value in [5, -1, 5]:
    heap_push(heap, value)
print(heap)
print(heap_pop(heap), heap)
heap_push(heap, 0)
print(heap)
while len(heap) > 0:
    print(heap_pop(heap))
print(heap_pop(heap), heap)
```

**预期输出**

```text
[-1, 5, 5]
-1 [5, 5]
[0, 5, 5]
0
5
5
None []
```


<a id="practice"></a>

## 自己做：先完成再看解答

### 练习 1

写 heap\_sort\_copy(values)，返回新的非降序列表且不修改输入。复制一次、线性建最小堆，再反复取出；检查 \[3,-1,3,0\] 和空表，说明与本章原地堆排序的空间区别。

<details>
<summary>提示</summary>

在副本上维护堆，另用结果列表接收每次最小值；取出次数由堆是否为空决定。

</details>

<details>
<summary>解答与检查</summary>

返回 \[-1,0,3,3\]，输入仍为 \[3,-1,3,0\]；空输入返回另一个空列表。最坏时间 O(n log(n+1)+1)，副本和输出合计 Θ(n+1) 空间。重复项保留，不把最小堆的内部数组直接当成排序结果。

**完整程序**

```python
def heap_swap(heap, left, right):
    saved = heap[left]
    heap[left] = heap[right]
    heap[right] = saved

def sift_down(heap, index, size):
    while 2 * index + 1 < size:
        child = 2 * index + 1
        right = child + 1
        if right < size and heap[right] < heap[child]:
            child = right
        if heap[index] <= heap[child]:
            return
        heap_swap(heap, index, child)
        index = child

def heap_pop(heap):
    if len(heap) == 0:
        return None
    smallest = heap[0]
    last = heap.pop()
    if len(heap) > 0:
        heap[0] = last
        sift_down(heap, 0, len(heap))
    return smallest

def heapify(heap):
    for index in range(len(heap) // 2 - 1, -1, -1):
        sift_down(heap, index, len(heap))

def heap_sort_copy(values):
    heap = values.copy()
    heapify(heap)
    result = []
    while len(heap) > 0:
        result.append(heap_pop(heap))
    return result

values = [3, -1, 3, 0]
print(heap_sort_copy(values), values)
print(heap_sort_copy([]))
```

**预期输出**

```text
[-1, 0, 3, 3] [3, -1, 3, 0]
[]
```


</details>

### 练习 2

写 largest\_k(values, k)，返回最大的 k 个整数并按非降序排列，重复值各占一个名额。k 为整数，k 不大于零返回空表，k 超过长度就返回所有值；只维护至多 k 项的最小堆，输入不变。

<details>
<summary>提示</summary>

堆未满就加入；满时堆顶是保留项中最小者，新值只有严格更大才替换堆顶并下沉。最后取空得到升序结果。

</details>

<details>
<summary>解答与检查</summary>

对 \[4,1,4,-2,9\]，k=3 得 \[4,4,9\]，k=0 得 \[\]，k=9 得 \[-2,1,4,4,9\]。保持的堆始终是已读前缀最大的至多 k 项，相等新值可直接舍弃一个等值副本而不改变所需重数。令 m=min(k,n)，k 为正时最坏时间 O(n log(m+1)+1)，存储 O(m+1)，其中包含最终输出。

**完整程序**

```python
def heap_swap(heap, left, right):
    saved = heap[left]
    heap[left] = heap[right]
    heap[right] = saved

def sift_up(heap, index):
    while index > 0:
        parent = (index - 1) // 2
        if heap[parent] <= heap[index]:
            return
        heap_swap(heap, parent, index)
        index = parent

def heap_push(heap, value):
    heap.append(value)
    sift_up(heap, len(heap) - 1)

def sift_down(heap, index, size):
    while 2 * index + 1 < size:
        child = 2 * index + 1
        right = child + 1
        if right < size and heap[right] < heap[child]:
            child = right
        if heap[index] <= heap[child]:
            return
        heap_swap(heap, index, child)
        index = child

def heap_pop(heap):
    if len(heap) == 0:
        return None
    smallest = heap[0]
    last = heap.pop()
    if len(heap) > 0:
        heap[0] = last
        sift_down(heap, 0, len(heap))
    return smallest

def largest_k(values, k):
    if k <= 0:
        return []
    heap = []
    for value in values:
        if len(heap) < k:
            heap_push(heap, value)
        elif value > heap[0]:
            heap[0] = value
            sift_down(heap, 0, len(heap))
    result = []
    while len(heap) > 0:
        result.append(heap_pop(heap))
    return result

values = [4, 1, 4, -2, 9]
print(largest_k(values, 3))
print(largest_k(values, 0), largest_k(values, 9))
print(values)
```

**预期输出**

```text
[4, 4, 9]
[] [-2, 1, 4, 4, 9]
[4, 1, 4, -2, 9]
```


</details>

### 练习 3

把多份已经非降序的整数列表合并成一份新列表，保留重复项且不改任何输入。堆只保存每份尚未输出的首项，记录格式为 \[值,组号,位置\]；检查 \[\[1,4,4\],\[\],\[-2,4\],\[0,7\]\] 以及全部为空的情况。

<details>
<summary>提示</summary>

Python 列表按从左到右第一个不同元素比较，三字段全是整数。取出某组首项后，只把该组的下一项入堆；组号用于相等值的确定次序。

</details>

<details>
<summary>解答与检查</summary>

输出 \[-2,0,1,4,4,4,7\]，空组不入堆，全部为空得到 \[\]。各组剩余项都不小于自己的首项，因此最小首项就是全体下一项。设 g 为总组数、r 为非空组数、n 为总项数，时间 O(g+n log(r+1)+1)，堆工作区 O(r+1)，返回列表另占 O(n+1)；即使全是空组，也要计算扫描 g 组的成本。

**完整程序**

```python
def heap_swap(heap, left, right):
    saved = heap[left]
    heap[left] = heap[right]
    heap[right] = saved

def sift_up(heap, index):
    while index > 0:
        parent = (index - 1) // 2
        if heap[parent] <= heap[index]:
            return
        heap_swap(heap, parent, index)
        index = parent

def heap_push(heap, value):
    heap.append(value)
    sift_up(heap, len(heap) - 1)

def sift_down(heap, index, size):
    while 2 * index + 1 < size:
        child = 2 * index + 1
        right = child + 1
        if right < size and heap[right] < heap[child]:
            child = right
        if heap[index] <= heap[child]:
            return
        heap_swap(heap, index, child)
        index = child

def heap_pop(heap):
    if len(heap) == 0:
        return None
    smallest = heap[0]
    last = heap.pop()
    if len(heap) > 0:
        heap[0] = last
        sift_down(heap, 0, len(heap))
    return smallest

def merge_sorted_groups(groups):
    heap = []
    for group in range(len(groups)):
        if len(groups[group]) > 0:
            heap_push(heap, [groups[group][0], group, 0])
    result = []
    while len(heap) > 0:
        item = heap_pop(heap)
        result.append(item[0])
        group = item[1]
        position = item[2] + 1
        if position < len(groups[group]):
            heap_push(heap, [groups[group][position], group, position])
    return result

groups = [[1, 4, 4], [], [-2, 4], [0, 7]]
print(merge_sorted_groups(groups))
print(groups)
print(merge_sorted_groups([[], []]))
```

**预期输出**

```text
[-2, 0, 1, 4, 4, 4, 7]
[[1, 4, 4], [], [-2, 4], [0, 7]]
[]
```


</details>

<a id="pitfalls"></a>

## 容易混淆的地方

- **把堆数组当成有序列表，或按搜索树规则在堆中查任意键。** 堆只保证父子关系与根最值，兄弟和子树之间没有全局分隔。
- **下沉时忽略仅左孩子、随意选孩子，或者把已排好后缀也纳入范围。** 先检查下标，再按最小或最大版本选正确孩子，始终使用显式有效长度。
- **把每个结点都按整树高度收费，断言向下建堆也是 n log n。** 按能下降的层数累加，底部大多数结点很浅，总预算小于 n 层。
- **宣称动态列表每次扩容都常数，或把堆排序当成稳定排序。** 区分调整路径与摊还分配；用相等键的对象身份检查交换后的顺序。

<a id="self-check"></a>

## 离开这一章前

- [ ] 手算零基父子下标，检查根、末项和只有左孩子的位置。
- [ ] 每次入堆与取出后检查所有父子关系、元素重数及返回值。
- [ ] 独立推导六项建堆的三份快照与七次比较。
- [ ] 对堆排序逐轮检查最大堆前缀、已排好后缀与区间外不变。
- [ ] 用空组、重复值、k 越界与输入副本验证两种应用的完整契约。

## 本章边界

- 只实现二叉堆基础接口，未实现任意位置删除、优先级修改、索引堆或并发任务队列。
- 空堆取出约定为 None，与 heapq 异常接口不同；普通最值接口限定整数。
- 堆排序不稳定；多路归并的平局规则由整数记录明确给出，不直接比较任意任务对象。
- 动态列表操作采用摊还分析，原地调整与复制、输出、完整轨迹的空间分别计算。

## 选题来源与覆盖

来源含学生报告时，仅将其作为选题线索；具体机制仍需结合后续实验或权威资料核对。

- [大一小学期/Week\_3-Python/docs/readme.md](https://github.com/PKUanonym/REKCARC-TSC-UHT/blob/37cd19f7a9fb80dc846a7016b3fd482ed5fe7cc0/%E5%A4%A7%E4%B8%80%E5%B0%8F%E5%AD%A6%E6%9C%9F/Week_3-Python/docs/readme.md)（已提取可读文本，固定版本 37cd19f7a9fb）
- 主题 1：Python 基础语法的外部学习入口；位置：第 41–80 行。
- 主题 2：从基础语法到工具与应用的建议阅读顺序；位置：第 121–160 行。

## 参考资料与规则核对

上游入口用于确定学习方向；下面的参考资料用于核对语言语义、数据结构或算法分析规则，例题和练习由本项目重新设计。

- [Python 3.11：heapq](https://docs.python.org/3.11/library/heapq.html)：核对零基最小堆不变式和线性 heapify；本章原创实现不导入库，空堆返回 None 而非抛异常。
- [Open Data Structures：二叉堆](https://opendatastructures.org/newhtml/ods/latex/heaps.html)：核对完全形状、父子索引与把扩缩容成本分开摊还的分析；不涉及可合并堆实现。
- [Algorithms 4/e：优先队列与堆排序](https://algs4.cs.princeton.edu/24pq/)：核对向下建堆总预算、堆排序最坏上界与稳定性；计数和测试按本章实际代码完成。
- [Python 3.11：序列比较](https://docs.python.org/3.11/tutorial/datastructures.html#comparing-sequences-and-other-types)：核对多路归并中三整数列表的字典序比较，以及 list 的末尾取出与浅复制语义。

**继续学习**：先独立完成自测，再记录仍需回读的步骤。

[上一章：用大小约束引导查找：二叉搜索树](17-binary-search-trees.md) · [下一章：按键定位记录：哈希表、冲突与扩容](19-hash-tables.md)

[教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [哈希表与图练习指引](../hash-graphs-practice.md) · [记录自己的学习](../learning-log-template.md)
