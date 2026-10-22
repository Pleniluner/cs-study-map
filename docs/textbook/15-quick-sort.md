# 先分区再递归：快速排序与三路划分

[返回教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md)

[上一章：把问题分小再合起来：分治与递归归并](14-divide-and-conquer.md) · [下一章：从链到层次：树、二叉树与遍历](16-trees.md)

[学习目标](#objectives) · [需要的基础](#prerequisites) · [例题](#examples) · [练习](#practice) · [自测](#self-check)

状态：**AI 初稿，可开始试学**。生成模型：Codex 当前会话（未记录具体模型型号）。

本章围绕资料中识别到的知识点重新编写；讲解、数值模型、例题与练习为 AI 原创组织，不是原课程题目或答案。主题出处只说明选题关联，不证明全部推导已经正确。

归并排序先把两边排好，再花线性工作合并；快速排序把主要工作放到前面：先按一个基准值分区，再分别处理需要继续排序的区域。本章不把“快”当作每个输入都快的保证，而是从分区契约推导递归范围，再用有序和全相等输入看清退化。随后把相等项集中成一段，并显式改变递归组织方式控制栈深。每个实现都会写明基准策略、区间边界、副作用和空间口径，避免把不同变体的结论混用。

<a id="objectives"></a>

## 学完要能做到

- 用循环不变式解释二路分区，并区分分区完成与整段有序。
- 正确排除已经定位的基准，保证两个递归区间严格缩小。
- 实测固定末项基准的比较次数与栈深，说明二次最坏情况。
- 维护三路分区的四个区域，正确处理从右侧换回的未知元素。
- 只递归短边、循环处理长边，区分栈空间保证与时间保证。

<a id="prerequisites"></a>

## 需要的基础

- 掌握第 10–14 章的比较计数、区间、交换、递归与分治。
- 主体处理整数列表，使用半开区间；分区函数要求非空合法区间，排序入口允许空表。
- 记录练习只按整数 key 比较，tag 用来观察身份；不涉及任意比较器或浮点特殊值。

## 一、二路分区先完成一项的定位

partition\_last 处理非空区间 \[lo, hi)，把末项的值保存为 pivot。它返回一个位置 p，使 p 之前的项都严格小于基准，p 处保存选中的基准项，p 之后都不小于基准。这里采用末项基准、严格小于归左边的二路方案；其他分区变体可能使用不同边界，不能直接交换它们的递归公式。

扫描前保持三段事实：\[lo, boundary) 已知小于基准，\[boundary, scan) 已知不小于基准，\[scan, hi-1) 尚未检查，末项暂时保存基准。当前项小于基准时，把它换到 boundary 并同时推进边界；否则只继续扫描。交换不会增加或删除元素，已分类区域仍满足约定。

全部扫描完后，把基准与 boundary 交换，得到最终位置 p。输入 \[6, 2, 5, 1, 4\] 的结果是 \[2, 1, 4, 6, 5\]，p=2；两边还没排好，但已确定不会有右边的元素需要跨到基准左侧。存在重复值时，基准占据一个合法排序位置，不表示所有相等项都已排成独立区域。

长度 m 的非空区间固定检查 m-1 个元素，分区时间 Θ(m)，只需固定数量辅助状态。分区不接受空区间，否则读取末项就失去意义；完整排序在调用前负责判断。所有交换都在原范围内，区间外的元素不应变化，后面的测试会单独验证这一点。

**完整程序**

```python
def swap(values, left, right):
    saved = values[left]
    values[left] = values[right]
    values[right] = saved

def partition_last(values, lo, hi):
    pivot = values[hi - 1]
    boundary = lo
    for scan in range(lo, hi - 1):
        if values[scan] < pivot:
            swap(values, boundary, scan)
            boundary = boundary + 1
    swap(values, boundary, hi - 1)
    return boundary

values = [6, 2, 5, 1, 4]
position = partition_last(values, 0, len(values))
print(position, values)
```

**预期输出**

```text
2 [2, 1, 4, 6, 5]
```


选题关联：来源主题 1（文末列出）。

## 二、递归范围必须排除已经定位的基准

一次分区只保证相对于基准的大小关系，不能直接返回并声称整表有序。quick\_range 先处理长度不超过 1 的基例，其他情况分区得到 p，再排序 \[lo, p) 与 \[p+1, hi)。基准本身已定位，不属于这两个子区间；重复包含它可能导致某次调用仍处理原长度，破坏终止。

正确性可以按区间长度说明：空与单项已排好；假定更短范围能正确排序，分区后两边都比原范围短，递归后两边各自有序，加上左小于基准、右不小于基准，整段就有序。交换与递归都保留元素，所以不会出现虽然有序却丢掉重复值的假答案。

即使基准是最小或最大，两边也只是空区间与长度少一的区间，数学上仍会结束。但是这会形成接近线性的调用链，在 Python 中可能先触及深度限制；本节普通递归版只用于小规模理解与计数。不能用数学上的严格减少来担保任意大列表都能运行。

quick\_sort 修改原列表并返回 None。分区自身用 O(1) 状态，完整递归排序还要算调用栈；两侧均衡时栈深为对数量级，极端不均衡时为线性。按前章“总辅助空间 O(1)”的原地定义，不能只看交换发生在原列表就给整个递归程序贴上常数空间结论。

**完整程序**

```python
def swap(values, left, right):
    saved = values[left]
    values[left] = values[right]
    values[right] = saved

def partition_last(values, lo, hi):
    pivot = values[hi - 1]
    boundary = lo
    for scan in range(lo, hi - 1):
        if values[scan] < pivot:
            swap(values, boundary, scan)
            boundary = boundary + 1
    swap(values, boundary, hi - 1)
    return boundary

def quick_range(values, lo, hi):
    if hi - lo <= 1:
        return
    pivot_index = partition_last(values, lo, hi)
    quick_range(values, lo, pivot_index)
    quick_range(values, pivot_index + 1, hi)

def quick_sort(values):
    quick_range(values, 0, len(values))

values = [6, 2, 5, 1, 4]
print(quick_sort(values), values)
empty = []
print(quick_sort(empty), empty)
```

**预期输出**

```text
None [1, 2, 4, 5, 6]
None []
```


选题关联：来源主题 1（文末列出）。

## 三、固定基准为什么会退化

在本章二路方案中，已递增列表的末项总是最大值，第一轮分成 n-1 项和空段。下一层仍如此，因此元素比较次数为 (n-1)+(n-2)+…+1，也就是 n(n-1)/2。全相等输入也会退化：没有任何项严格小于基准，每轮只定位一个相等项，剩余 n-1 项继续递归。

quick\_report 在副本上运行同一分区，按每段长度减一累计元素比较次数，并记录包含基例的最大辅助调用深度。它只数元素与 pivot 的大小比较，不把端点检查、交换、复制和打印混进该数字。长度 5 的递增与全相等输入都得到 10 次比较、5 层调用；不是所有“快速排序”变体对重复值都这样。

如果各层把剩余项分得比较均衡，每层总处理量为线性、层数为对数，才会得到 Θ(n log n) 的增长。本实现固定取末项，没有随机打乱，也没有随机选基准；不能把随机化算法在明确概率模型下的期望结论，当成这段确定性程序对所有输入的保证。最坏时间仍为 Θ(n²)。

报表为保留原输入先复制列表，空间应包含这份副本；深度字段只统计 quick\_count\_range 本身，不包括外层包装与分区的固定开销。接下来要分别处理两个问题：三路分区减少反复处理相等值的工作，而改变递归组织控制栈深。它们各有作用，不能相互替代。

**完整程序**

```python
def swap(values, left, right):
    saved = values[left]
    values[left] = values[right]
    values[right] = saved

def partition_last(values, lo, hi):
    pivot = values[hi - 1]
    boundary = lo
    for scan in range(lo, hi - 1):
        if values[scan] < pivot:
            swap(values, boundary, scan)
            boundary = boundary + 1
    swap(values, boundary, hi - 1)
    return boundary

def quick_count_range(values, lo, hi):
    if hi - lo <= 1:
        return {"comparisons": 0, "depth": 1}
    position = partition_last(values, lo, hi)
    left = quick_count_range(values, lo, position)
    right = quick_count_range(values, position + 1, hi)
    deepest = left["depth"]
    if right["depth"] > deepest:
        deepest = right["depth"]
    return {"comparisons": hi - lo - 1 + left["comparisons"] + right["comparisons"], "depth": 1 + deepest}

def quick_report(values):
    result = values.copy()
    report = quick_count_range(result, 0, len(result))
    report["sorted"] = result
    return report

for values in [[1, 2, 3, 4, 5], [7, 7, 7, 7, 7], [1, 2, 4, 5, 3]]:
    report = quick_report(values)
    print(report["comparisons"], report["depth"], report["sorted"])
```

**预期输出**

```text
10 5 [1, 2, 3, 4, 5]
10 5 [7, 7, 7, 7, 7]
6 3 [1, 2, 3, 4, 5]
```


选题关联：来源主题 1（文末列出）。

## 四、三路分区把全部相等项集中起来

三路分区把结果分成小于、等于、大于 pivot 的三段，返回相等区间 \[lt, gt)。本实现仍先保存末项的基准值，但扫描从 lo 开始，末项也参与分类。扫描中保持四区：\[lo, lt) 小于，\[lt, scan) 等于，\[scan, gt) 未知，\[gt, hi) 大于。gt 是半开右边界，不是最后一个相等元素的下标。

若当前值小于基准，与 lt 位置交换，lt 和 scan 同时加一；若相等，只推进 scan。若大于基准，先将 gt 减一，再把当前值换到 gt。特别要注意最后一种情况：从右边换回来的值还没检查，scan 必须停在原处，下一轮继续分类它，否则未知项可能被误当成相等项。

每轮未知长度 gt-scan 恰好减少一，所以长度 m 的输入恰有 m 轮，且不会因相等项多而卡住。程序先判断小于，必要时再判断大于，因此一轮可能有一次或两次元素比较；“m 轮”不能写成“恰好 m 次比较”。结束时未知区为空，原基准项保证相等区至少有一项。

下面 \[3, 1, 3, 5, 2, 3\] 得到相等区 \[2, 5)，中间三个 3 都不必继续排序。小于和大于区域仍需各自排序，不能因这次样例恰好有序就忽略它们。交换可能改变相同关键字记录的先后关系，三路只是按大小分类，不自动保证稳定性。

**完整程序**

```python
def swap(values, left, right):
    saved = values[left]
    values[left] = values[right]
    values[right] = saved

def partition_three(values, lo, hi):
    pivot = values[hi - 1]
    lt = lo
    scan = lo
    gt = hi
    while scan < gt:
        if values[scan] < pivot:
            swap(values, lt, scan)
            lt = lt + 1
            scan = scan + 1
        elif values[scan] > pivot:
            gt = gt - 1
            swap(values, scan, gt)
        else:
            scan = scan + 1
    return {"lt": lt, "gt": gt}

values = [3, 1, 3, 5, 2, 3]
print(partition_three(values, 0, len(values)))
print(values)
```

**预期输出**

```text
{'lt': 2, 'gt': 5}
[1, 2, 3, 3, 3, 5]
```


选题关联：来源主题 1（文末列出）。

## 五、短边递归，长边在当前调用里循环

三路分区后，只剩 \[lo, lt) 和 \[gt, hi) 两段需要继续排序。若照旧递归两边，遇到很差的基准仍可能形成长链。这里比较两边长度，只对更短且长度大于 1 的一边递归；较长一边通过修改当前 lo 或 hi，回到 while 继续处理，不再创建对应的新调用。

原段长度为 m，相等区至少一项，所以较短边长度至多为 (m-1)/2。每增加一个尚未返回的递归层，规模至少缩到接近一半，辅助调用栈因此有 O(log n) 的最坏上界；分区本身仍只用固定数量状态。只是调换两次递归的先后顺序不够，必须真正把长边那次调用改成循环。

两边长度相同可以任选一边递归，代码在这种情况下递归右边。空与单元素边不再调用；所有元素相等时，一次分区就把整段纳入相等区，随后结束，总时间 Θ(n)。这个程序不使用切片、不复制整表，也不保存所有中间状态，返回 None，结果仍在原列表。

控制栈深不等于消除二次时间。本实现依旧固定末项基准，对严格递增列表仍可能每轮只去掉一项，累计工作达到 Θ(n²)，只是长边现在由循环承接。为避免混淆，应分别写出时间最坏上界和栈空间最坏上界；实践中还可采用随机基准或回退策略，本章不把那些改进冒充已实现。

**完整程序**

```python
def swap(values, left, right):
    saved = values[left]
    values[left] = values[right]
    values[right] = saved

def partition_three(values, lo, hi):
    pivot = values[hi - 1]
    lt = lo
    scan = lo
    gt = hi
    while scan < gt:
        if values[scan] < pivot:
            swap(values, lt, scan)
            lt = lt + 1
            scan = scan + 1
        elif values[scan] > pivot:
            gt = gt - 1
            swap(values, scan, gt)
        else:
            scan = scan + 1
    return {"lt": lt, "gt": gt}

def quick_three_range(values, lo, hi):
    while hi - lo > 1:
        bounds = partition_three(values, lo, hi)
        lt = bounds["lt"]
        gt = bounds["gt"]
        if lt - lo < hi - gt:
            if lt - lo > 1:
                quick_three_range(values, lo, lt)
            lo = gt
        else:
            if hi - gt > 1:
                quick_three_range(values, gt, hi)
            hi = lt

def quick_three_sort(values):
    quick_three_range(values, 0, len(values))

values = [3, 1, 3, 5, 2, 3]
print(quick_three_sort(values), values)
same = [4, 4, 4]
print(quick_three_sort(same), same)
empty = []
print(quick_three_sort(empty), empty)
```

**预期输出**

```text
None [1, 2, 3, 3, 3, 5]
None [4, 4, 4]
None []
```


选题关联：来源主题 1（文末列出）。

<a id="examples"></a>

## 跟着做：原创例题

### 例题 1

用末项 4 为基准，对 \[6, 2, 5, 1, 4\] 做一次二路分区。每次扫描后记录 scan、boundary 和列表副本，再执行最后的基准交换，说明结果为何还需递归。

1. scan=0 的 6 不小于 4，boundary 保持 0；没有项被放入小于区。
2. scan=1 的 2 小于 4，与边界位置交换，得到 \[2, 6, 5, 1, 4\]，boundary=1。
3. scan=2 的 5 不小于 4；scan=3 的 1 与位置 1 交换，得到 \[2, 1, 5, 6, 4\]，boundary=2。
4. 最后把基准 4 换到位置 2，得到 \[2, 1, 4, 6, 5\]。两边符合大小关系，但各自仍无序。
5. 每轮保存 copy 才能保留当时状态；本例对整个长度 m 的列表分区，保存 m-1 份完整副本，额外空间为平方量级。若只分区较长列表中的一段，每份副本仍会复制整个列表。

**结果与核对**

四次元素比较后，基准位置为 2。后续递归范围是 \[0, 2) 和 \[3, 5)，不再包含位置 2；轨迹中保存的是扫描结束状态，最后一次基准交换另行打印。

**完整程序**

```python
def swap(values, left, right):
    saved = values[left]
    values[left] = values[right]
    values[right] = saved

def partition_trace(values, lo, hi):
    pivot = values[hi - 1]
    boundary = lo
    steps = []
    for scan in range(lo, hi - 1):
        if values[scan] < pivot:
            swap(values, boundary, scan)
            boundary = boundary + 1
        steps.append([scan, boundary, values.copy()])
    swap(values, boundary, hi - 1)
    return {"pivot": boundary, "steps": steps}

values = [6, 2, 5, 1, 4]
report = partition_trace(values, 0, len(values))
for step in report["steps"]:
    print(step)
print(report["pivot"], values)
```

**预期输出**

```text
[0, 0, [6, 2, 5, 1, 4]]
[1, 1, [2, 6, 5, 1, 4]]
[2, 1, [2, 6, 5, 1, 4]]
[3, 2, [2, 1, 5, 6, 4]]
2 [2, 1, 4, 6, 5]
```


### 例题 2

给短边递归、长边循环的三路快排加两个计数：分区次数与最大辅助调用深度。比较五项递增、五项全相等和 \[1, 2, 4, 5, 3\]，说明很浅的栈为何仍可能做很多工作。

1. 根辅助调用深度记为 1；只有真正递归短边时才给 depth 加一，当前 while 的下一轮不增加深度。
2. 五项递增每次仅定位末尾最大项，需要处理长度 5、4、3、2 四段，分区 4 次，但短边一直为空，最大深度为 1。
3. 五项全相等一次分区就完成，相等区覆盖全段，分区 1 次、深度 1。
4. \[1, 2, 4, 5, 3\] 首次分出长度 2 和 2 的两侧，递归其中一侧达到深度 2，总共分区 3 次。
5. 报表为保留原输入使用副本，包含输出的空间为线性；普通排序自身才使用对数栈加常数分区状态。

**结果与核对**

三组分区次数与深度分别为 (4,1)、(1,1)、(3,2)。分区次数还不等于比较次数，需要把各次实际范围中的比较次数分别相加；一层循环也可能累计二次工作。

**完整程序**

```python
def swap(values, left, right):
    saved = values[left]
    values[left] = values[right]
    values[right] = saved

def partition_three(values, lo, hi):
    pivot = values[hi - 1]
    lt = lo
    scan = lo
    gt = hi
    while scan < gt:
        if values[scan] < pivot:
            swap(values, lt, scan)
            lt = lt + 1
            scan = scan + 1
        elif values[scan] > pivot:
            gt = gt - 1
            swap(values, scan, gt)
        else:
            scan = scan + 1
    return {"lt": lt, "gt": gt}

def quick_three_depth_range(values, lo, hi, depth, stats):
    if depth > stats["depth"]:
        stats["depth"] = depth
    while hi - lo > 1:
        bounds = partition_three(values, lo, hi)
        stats["partitions"] = stats["partitions"] + 1
        lt = bounds["lt"]
        gt = bounds["gt"]
        if lt - lo < hi - gt:
            if lt - lo > 1:
                quick_three_depth_range(values, lo, lt, depth + 1, stats)
            lo = gt
        else:
            if hi - gt > 1:
                quick_three_depth_range(values, gt, hi, depth + 1, stats)
            hi = lt

def quick_three_report(values):
    result = values.copy()
    stats = {"partitions": 0, "depth": 0}
    quick_three_depth_range(result, 0, len(result), 1, stats)
    return {"sorted": result, "partitions": stats["partitions"], "depth": stats["depth"]}

for values in [[1, 2, 3, 4, 5], [7, 7, 7, 7, 7], [1, 2, 4, 5, 3]]:
    report = quick_three_report(values)
    print(report["partitions"], report["depth"], report["sorted"])
```

**预期输出**

```text
4 1 [1, 2, 3, 4, 5]
1 1 [7, 7, 7, 7, 7]
3 2 [1, 2, 3, 4, 5]
```


<a id="practice"></a>

## 自己做：先完成再看解答

### 练习 1

写 quick\_sort\_copy(values)，调用三路快排但返回新的外层列表，原输入不变。检查 \[5, -1, 5, 0\] 与空表，并说明接口改变后的空间口径。

<details>
<summary>提示</summary>

在入口复制一次，再把副本交给会修改输入的排序函数，不在每层建立新列表。

</details>

<details>
<summary>解答与检查</summary>

结果为 \[-1, 0, 5, 5\]，原列表仍为 \[5, -1, 5, 0\]；空表返回另一个空列表。包含返回副本的额外空间为 Θ(n+1)，不能把内部排序的 O(log n) 辅助栈结论直接当成整个包装函数的空间。

**完整程序**

```python
def swap(values, left, right):
    saved = values[left]
    values[left] = values[right]
    values[right] = saved

def partition_three(values, lo, hi):
    pivot = values[hi - 1]
    lt = lo
    scan = lo
    gt = hi
    while scan < gt:
        if values[scan] < pivot:
            swap(values, lt, scan)
            lt = lt + 1
            scan = scan + 1
        elif values[scan] > pivot:
            gt = gt - 1
            swap(values, scan, gt)
        else:
            scan = scan + 1
    return {"lt": lt, "gt": gt}

def quick_three_range(values, lo, hi):
    while hi - lo > 1:
        bounds = partition_three(values, lo, hi)
        lt = bounds["lt"]
        gt = bounds["gt"]
        if lt - lo < hi - gt:
            if lt - lo > 1:
                quick_three_range(values, lo, lt)
            lo = gt
        else:
            if hi - gt > 1:
                quick_three_range(values, gt, hi)
            hi = lt

def quick_three_sort(values):
    quick_three_range(values, 0, len(values))

def quick_sort_copy(values):
    result = values.copy()
    quick_three_sort(result)
    return result

values = [5, -1, 5, 0]
print(quick_sort_copy(values), values)
print(quick_sort_copy([]))
```

**预期输出**

```text
[-1, 0, 5, 5] [5, -1, 5, 0]
[]
```


</details>

### 练习 2

把普通二路快排改为只比较记录的 key，原记录依次为 2R、1S、2T。输出排序后的 tag 顺序，判断它是否稳定，并解释为什么只比较 key 仍不能保证稳定。

<details>
<summary>提示</summary>

保持末项基准和严格小于归左边的规则，交换整条记录引用；tag 只观察身份，不参与比较。

</details>

<details>
<summary>解答与检查</summary>

tag 顺序为 S、T、R。先把 1S 换到左侧，再把基准 2T 换到边界，原来在前的 2R 被移到后面。key 已有序，但两个 key=2 的记录顺序反转，因此该实现不稳定；比较条件是否含 tag 与交换能否跨过相等记录是不同问题。

**完整程序**

```python
def swap(values, left, right):
    saved = values[left]
    values[left] = values[right]
    values[right] = saved

def quick_key_range(records, lo, hi):
    if hi - lo <= 1:
        return
    pivot_key = records[hi - 1]["key"]
    boundary = lo
    for scan in range(lo, hi - 1):
        if records[scan]["key"] < pivot_key:
            swap(records, boundary, scan)
            boundary = boundary + 1
    swap(records, boundary, hi - 1)
    quick_key_range(records, lo, boundary)
    quick_key_range(records, boundary + 1, hi)

def quick_keys(records):
    quick_key_range(records, 0, len(records))

records = [{"key": 2, "tag": "R"}, {"key": 1, "tag": "S"}, {"key": 2, "tag": "T"}]
quick_keys(records)
tags = []
for record in records:
    tags.append(record["tag"])
print(tags)
```

**预期输出**

```text
['S', 'T', 'R']
```


</details>

### 练习 3

用三路分区写 kth\_smallest\_copy(values, k)，返回完整非降序排列中下标 k 的数值，重复值分别占位置；不必把整个列表排好，原输入不变。k 为整数，越界或空输入返回 None。检查 \[5, 1, 5, -2, 3\] 的 k=0、2、4 及非法下标。

<details>
<summary>提示</summary>

先复制列表。分区后 k 在相等区就直接返回；否则只缩到包含 k 的那一侧，k 始终使用同一副本的全局下标。

</details>

<details>
<summary>解答与检查</summary>

结果分别为 -2、3、5，k=-1 或 5 以及空表都返回 None。已排除区域在秩次上处于目标的一侧，不需要继续排序；两个 5 占据两个秩次。固定末项基准的最坏时间仍可能为二次，不能因只走一边就声称总是线性。副本占 Θ(n+1) 空间，循环本身只用固定状态。

**完整程序**

```python
def swap(values, left, right):
    saved = values[left]
    values[left] = values[right]
    values[right] = saved

def partition_three(values, lo, hi):
    pivot = values[hi - 1]
    lt = lo
    scan = lo
    gt = hi
    while scan < gt:
        if values[scan] < pivot:
            swap(values, lt, scan)
            lt = lt + 1
            scan = scan + 1
        elif values[scan] > pivot:
            gt = gt - 1
            swap(values, scan, gt)
        else:
            scan = scan + 1
    return {"lt": lt, "gt": gt}

def kth_smallest_copy(values, k):
    if k < 0 or k >= len(values):
        return None
    result = values.copy()
    lo = 0
    hi = len(result)
    while lo < hi:
        bounds = partition_three(result, lo, hi)
        if k < bounds["lt"]:
            hi = bounds["lt"]
        elif k >= bounds["gt"]:
            lo = bounds["gt"]
        else:
            return result[k]
    return None

values = [5, 1, 5, -2, 3]
print(kth_smallest_copy(values, 0), kth_smallest_copy(values, 2), kth_smallest_copy(values, 4))
print(kth_smallest_copy(values, -1), kth_smallest_copy(values, 5), kth_smallest_copy([], 0))
print(values)
```

**预期输出**

```text
-2 3 5
None None None
[5, 1, 5, -2, 3]
```


</details>

<a id="pitfalls"></a>

## 容易混淆的地方

- **把一次分区当成全部排序，或在递归区间里重新包含基准。** 分区只确定相对大小；二路递归使用 \[lo,p) 与 \[p+1,hi)，三路跳过整个相等区。
- **三路从右端换回未知元素后仍推进 scan。** 大于分支只缩 gt，当前项必须重新检查；每轮用未知区长度严格减少来验终止。
- **固定末项基准却无条件声称平均 n log n，或认为三路消除了所有最坏输入。** 概率结论需要概率模型；本章确定性基准仍有二次最坏情况，三路针对重复值改善。
- **只交换两个递归调用的顺序就宣称对数栈，或把交换排序当作稳定排序。** 长边要显式改成循环；稳定性另用带身份的重复关键字验证，不能只看数值有序。

<a id="self-check"></a>

## 离开这一章前

- [ ] 手算一次分区，检查每个区间的含义、基准位置与原元素重数。
- [ ] 分别运行空、单项、全相等、已排序、逆序、重复负数及两项输入。
- [ ] 用严格比较计数验证普通二路快排的 n(n−1)/2 最坏模型。
- [ ] 说明短边递归为何控制栈深，并举出栈浅而时间仍二次的输入。
- [ ] 检查记录身份、复制接口及秩次查询，确认下标和稳定性契约没有混用。

## 本章边界

- 普通二路递归版用于小规模讲解，最坏线性栈深可能触及 Python 递归限制。
- 本章未实现随机基准、内省排序或堆排序回退，不承诺最坏 n log n 时间。
- 分区辅助状态为常数，完整排序另计调用栈；复制包装和轨迹记录再计各自存储。
- 所有区间与整数参数按前提使用；排序不稳定，不能直接用于要求保持相等记录顺序的任务。

## 选题来源与覆盖

来源含学生报告时，仅将其作为选题线索；具体机制仍需结合后续实验或权威资料核对。

- [大一小学期/Week\_3-Python/docs/readme.md](https://github.com/PKUanonym/REKCARC-TSC-UHT/blob/37cd19f7a9fb80dc846a7016b3fd482ed5fe7cc0/%E5%A4%A7%E4%B8%80%E5%B0%8F%E5%AD%A6%E6%9C%9F/Week_3-Python/docs/readme.md)（已提取可读文本，固定版本 37cd19f7a9fb）
- 主题 1：Python 基础语法的外部学习入口；位置：第 41–80 行。
- 主题 2：从基础语法到工具与应用的建议阅读顺序；位置：第 121–160 行。

## 参考资料与规则核对

上游入口用于确定学习方向；下面的参考资料用于核对语言语义、数据结构或算法分析规则，例题和练习由本项目重新设计。

- [Algorithms 4/e：快速排序与三路分区](https://algs4.cs.princeton.edu/23quicksort/index.php)：核对分区、重复关键字及三路区域；本章采用自定半开边界与固定末项基准，计数按实际代码推导。
- [Cornell CS2110：快速排序的时间与空间](https://www.cs.cornell.edu/courses/cs2110/2025fa/lectures/lec07/)：核对不均衡分区、调用栈与稳定性；本章显式用循环处理长边，不假定 Python 自动消除尾调用。
- [Python 3.11：解释器递归深度](https://docs.python.org/3.11/library/sys.html#sys.getrecursionlimit)：区分数学上终止与解释器可用深度，普通递归版只用小规模示例。

**继续学习**：先独立完成自测，再记录仍需回读的步骤。

[上一章：把问题分小再合起来：分治与递归归并](14-divide-and-conquer.md) · [下一章：从链到层次：树、二叉树与遍历](16-trees.md)

[教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [记录自己的学习](../learning-log-template.md)
