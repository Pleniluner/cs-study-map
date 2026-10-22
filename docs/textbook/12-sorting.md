# 怎样把数据排成顺序：选择、插入与归并排序

[返回教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [哈希表与图练习指引](../hash-graphs-practice.md)

[上一章：怎样缩小候选范围：顺序查找与二分查找](11-searching.md) · [下一章：函数怎样调用自己：递归、返回与调用栈](13-recursion.md)

[学习目标](#objectives) · [需要的基础](#prerequisites) · [例题](#examples) · [练习](#practice) · [自测](#self-check)

状态：**AI 初稿，可开始试学**。生成模型：Codex 当前会话（未记录具体模型型号）。

本章围绕资料中识别到的知识点重新编写；讲解、数值模型、例题与练习为 AI 原创组织，不是原课程题目或答案。主题出处只说明选题关联，不证明全部推导已经正确。

二分查找需要有序数据，本章学习怎样把数据排成顺序，并验证排列没有丢项或凭空增加元素。我们从原地选择和插入开始，再把两个有序片段合并，最终用逐轮翻倍的方式完成归并排序。这样只用已有的循环、函数和列表知识，就能理解平方量级与 n log n 量级的差别。除了最终输出，还要检查输入是否被修改、相等关键字是否保持原先次序，以及辅助列表实际占用多少空间。例题给出中间过程，练习则要求独立实现和解释边界。

<a id="objectives"></a>

## 学完要能做到

- 同时检查非降序与元素重数保持，区分原地修改、返回新列表和稳定性。
- 用已完成前缀解释选择排序，用有序前缀和保存待插项解释插入排序。
- 正确合并两个非降序列表，处理相等、空片段和剩余后缀。
- 用宽度翻倍构造自底向上归并，并分析每轮工作与峰值额外空间。
- 实现提前停止的冒泡和稳定记录排序，解释排序后查找的下标与总成本。

<a id="prerequisites"></a>

## 需要的基础

- 掌握第 6 章的列表复制、元素搬移，以及第 10、11 章的计数与查找。
- 会使用字典固定字段；最后的记录排序以整数 key 决定顺序、tag 区分记录身份。
- 使用 Python 3.11+；主体输入为整数列表，默认按非降序排列，不要求递归知识。

## 一、排序正确，不只是看起来有序

本章排序要求结果非降序，并且包含原来的全部元素及各自出现次数。例如 \[4, -1, 4, 2\] 应变为 \[-1, 2, 4, 4\]；少掉一个 4 虽然仍有序，却不是正确结果。验证时要同时检查顺序、长度和每个值的数量，不能只比较最小值与最大值，也不能去重后比较集合。

还应说明是否修改输入。Python 的 sorted(values) 返回新的外层列表，原列表保留；values.sort() 原地改变排列并返回 None。下面先展示两者作为实际使用的工具，之后手写算法时逐步说明内部变化。不要把 sort 的返回值重新赋给原变量后，误以为那里还保存着排好的列表。

稳定性是另一条性质：若两条记录的排序关键字相等，排序后仍保留它们原有的先后关系。假设只按 key 排列记录，tag 只是辨认身份；相同 key 的 R 原来在 T 之前，稳定排序后仍如此。仅看两个相等整数无法观察身份次序，后面的记录练习会专门检查。

原地与稳定没有互相包含关系：一个算法可以原地但不稳定，也可以用额外列表且稳定。本文称原地时，表示在原列表内完成重排、只用 O(1) 单位辅助状态；保存完整轨迹的调试版需要另算。空列表和单元素已经满足排序目标，仍应符合各函数的返回约定。

**完整程序**

```python
values = [4, -1, 4, 2]
result = sorted(values)
print(result, values)
returned = values.sort()
print(returned, values)
```

**预期输出**

```text
[-1, 2, 4, 4] [4, -1, 4, 2]
None [-1, 2, 4, 4]
```


选题关联：来源主题 1（文末列出）。

## 二、选择排序：每轮固定一个位置

选择排序把列表分成已完成前缀和待处理后缀。第 start 轮在后缀中寻找最小项的位置 smallest，再把它与 start 交换。循环结束时，start 位置已经放好剩余项中的最小值；此前放好的前缀不再修改，因此下一轮可以从 start 加 1 开始。

下面 \[6, 2, 5, 2\] 的第一轮找到下标 1，把 2 与 6 交换，得到 \[2, 6, 5, 2\]。第二轮选择剩余最小的 2，得到 \[2, 2, 5, 6\]；第三轮最小项已在当前位置，无需交换。交换先用 saved 保存旧值，确保不会覆盖后丢失原元素。

元素比较次数依次为 n 减 1、n 减 2，一直到 1，合计 n(n−1)/2；即使输入已经有序，也照样扫描后缀。因此其最好和最坏时间都为 Θ(n²)，n 至少为 1 时实际交换至多 n 减 1 次。空与单元素不进入外层，函数原地修改并自然返回 None，只用固定数量的辅助名字。

本实现的远距离交换不保证稳定。若只看关键字，记录依次为 2R、2T、1S，第一轮把 1S 换到开头，会得到 1S、2T、2R，相同关键字的原顺序反转。即使寻找最小值时只在严格更小时更新，也不能避免这一反例；稳定性取决于整个移动过程。

**完整程序**

```python
def selection_sort(values):
    for start in range(len(values) - 1):
        smallest = start
        for probe in range(start + 1, len(values)):
            if values[probe] < values[smallest]:
                smallest = probe
        if smallest != start:
            saved = values[start]
            values[start] = values[smallest]
            values[smallest] = saved

values = [6, 2, 5, 2]
returned = selection_sort(values)
print(values, returned)
```

**预期输出**

```text
[2, 2, 5, 6] None
```


选题关联：来源主题 1（文末列出）。

## 三、插入排序：为当前项找到空位

插入排序开始时把第一项看成已排好的前缀，每轮把下一项插入其中。先用 pending 保存当前值，再从它左边向前检查：只要前项严格大于 pending，就把前项右移一格。找到不大于 pending 的项或到达开头后，把 pending 写进空位，前缀就增加一项。

保存 pending 很关键。右移会暂时让列表里出现重复的旧值，但待插值还在局部名字里，没有丢失；整轮完成后，元素重数恢复。while 先检查 cursor 大于 0，才读取 cursor 减 1；否则 Python 的负下标可能把末项当作前项，破坏正确的边界判断。

下面 \[5, 2, 4, 2\] 先把 5 右移，得到 \[2, 5, 4, 2\]；再插入 4，得到 \[2, 4, 5, 2\]；最后把 5 和 4 右移，让后来的 2 放在原有 2 后面。相等项不右移，后来项不会越过较早的相等项，因此这种插入方法稳定。

非空列表已非降序时，每轮只比较一次就停止，总共 n 减 1 次元素比较，没有右移，时间为 Θ(n)。严格逆序时，第 i 轮右移 i 项，总共 n(n−1)/2 次，最坏为 Θ(n²)。同一函数对不同排列有不同成本；普通版本额外空间 O(1)，返回 None，最终结果留在原列表。

**完整程序**

```python
def insertion_sort(values):
    for index in range(1, len(values)):
        pending = values[index]
        cursor = index
        while cursor > 0 and values[cursor - 1] > pending:
            values[cursor] = values[cursor - 1]
            cursor = cursor - 1
        values[cursor] = pending

values = [5, 2, 4, 2]
returned = insertion_sort(values)
print(values, returned)
```

**预期输出**

```text
[2, 2, 4, 5] None
```


选题关联：来源主题 1（文末列出）。

## 四、合并：同时维护两个有序入口

若 left 和 right 各自已经非降序，合并不必把两者接起来后重新扫描找最小。用 i、j 分别指向两边尚未取走的首项，较小者就是所有剩余项的最小候选。把它加入新结果，只推进对应的一边；结果前缀因而始终有序，未取走的项仍保持各自原顺序。

当两边当前值相等时，本实现先取左边。若两个片段来自原列表中相邻的前后两段，这能保住跨片段相等项的先后关系；同时，每个片段内部也按原顺序取出。稳定合并需要这个相等处理，不能随意改成优先右边后仍宣称整体稳定。

一边耗尽后，另一边剩余项已经有序，直接按顺序追加即可。下面合并 \[-2, 3, 3\] 与 \[0, 3, 7\]，结果是 \[-2, 0, 3, 3, 3, 7\]。共有三个 3，不能在相等时只写一次却同时推进两边，否则会丢项。任一输入为空时，结果是另一边的外层复制。

两边长度为 m、n，每轮至少消耗一项，结果恰有 m+n 项。两边都非空时，跨边元素比较至多 m+n−1 次；两边总计非空时，时间为 Θ(m+n)，输出占同样量级空间，除此之外只有固定数量游标。函数不修改输入；有序前提仍由调用者保证。

**完整程序**

```python
def merge_sorted(left, right):
    result = []
    i = 0
    j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i = i + 1
        else:
            result.append(right[j])
            j = j + 1
    while i < len(left):
        result.append(left[i])
        i = i + 1
    while j < len(right):
        result.append(right[j])
        j = j + 1
    return result

left = [-2, 3, 3]
right = [0, 3, 7]
print(merge_sorted(left, right))
print(left, right)
print(merge_sorted([], [4]))
```

**预期输出**

```text
[-2, 0, 3, 3, 3, 7]
[-2, 3, 3] [0, 3, 7]
[4]
```


选题关联：来源主题 1（文末列出）。

## 五、自底向上归并：让有序片段逐轮变长

一个元素本身就是有序片段。第一轮把相邻的长度 1 片段两两合并，下一轮合并长度 2 片段，然后长度 4、8，直到片段宽度足以覆盖整个列表。这种自底向上的做法不需要递归；每轮开始时，按 width 分出的各个片段已分别有序，是本轮能正确合并的前提。

merge\_pass 的 width 必须为正整数。range 的三个参数表示起点、停止值、步长，因此 start 从 0 开始，每次前进 2×width，找到下一对片段。values\[start:stop\] 取半开切片，停止值越过列表末尾时只取已有项；最后一个片段不足 width 或缺少右半边，都可由合并函数处理。

merge\_sort 先复制输入，再把每轮新结果作为下一轮输入，width 每轮翻倍。空与单元素直接返回外层副本；一般列表不断减少片段数量，最终整段有序。相等时左边先出，各轮都保留相对次序，所以稳定性从单元素片段一直保持到最终结果。

每轮切片、合并和追加合计处理与 n 成正比的元素，n 至少为 2 时共有向上取整的 log₂n 轮，所以本实现时间为 Θ(n log n)。同时存在的是当前列表、本轮结果和少数片段副本，峰值额外空间为 O(n)，不是 O(1)。累计复制量可达 n log n 量级，但旧轮结果不全部留存，累计分配量不能直接当成峰值空间。

**完整程序**

```python
def merge_sorted(left, right):
    result = []
    i = 0
    j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i = i + 1
        else:
            result.append(right[j])
            j = j + 1
    while i < len(left):
        result.append(left[i])
        i = i + 1
    while j < len(right):
        result.append(right[j])
        j = j + 1
    return result

def merge_pass(values, width):
    result = []
    for start in range(0, len(values), 2 * width):
        left = values[start:start + width]
        right = values[start + width:start + 2 * width]
        merged = merge_sorted(left, right)
        for value in merged:
            result.append(value)
    return result

def merge_sort(values):
    result = values.copy()
    width = 1
    while width < len(result):
        result = merge_pass(result, width)
        width = width * 2
    return result

values = [9, 1, 5, 1, 3]
print(merge_sort(values), values)
print(merge_sort([]))
```

**预期输出**

```text
[1, 1, 3, 5, 9] [9, 1, 5, 1, 3]
[]
```


选题关联：来源主题 1（文末列出）。

<a id="examples"></a>

## 跟着做：原创例题

### 例题 1

对 \[5, 2, 4, 2\] 执行插入排序，记录每轮完成后的列表，并仅统计较大元素右移的次数，不统计 pending 的最终写回。给出总数，解释两个相等的 2 为什么不互相越过。

1. 待插 2 时右移 5 一次，结果为 \[2, 5, 4, 2\]，累计 1 次。
2. 待插 4 时右移 5 一次，遇到前面的 2 停止，结果为 \[2, 4, 5, 2\]，累计 2 次。
3. 最后待插 2 时右移 5、4，共两次；遇到原有 2 时相等，不再移动。
4. 最终为 \[2, 2, 4, 5\]，累计右移 4 次。把当前项写回空位的三次写入没有算入 moves。
5. 轨迹保存使用 copy，否则几行可能都指向同一最终列表；这个调试版本保存多份状态，不能沿用普通插入排序的 O(1) 额外空间结论。

**结果与核对**

每轮状态依次是 \[2, 5, 4, 2\]、\[2, 4, 5, 2\]、\[2, 2, 4, 5\]，右移总数为 4。结果有序且仍有两个 2，较早的 2 保持在较晚的 2 前面。

**完整程序**

```python
def insertion_report(values):
    moves = 0
    states = []
    for index in range(1, len(values)):
        pending = values[index]
        cursor = index
        while cursor > 0 and values[cursor - 1] > pending:
            values[cursor] = values[cursor - 1]
            cursor = cursor - 1
            moves = moves + 1
        values[cursor] = pending
        states.append(values.copy())
    return {"moves": moves, "states": states}

values = [5, 2, 4, 2]
report = insertion_report(values)
print(report["states"])
print(report["moves"], values)
```

**预期输出**

```text
[[2, 5, 4, 2], [2, 4, 5, 2], [2, 2, 4, 5]]
4 [2, 2, 4, 5]
```


### 例题 2

对 \[7, 2, 6, 1, 5\] 逐轮归并，分别给出 width 为 1、2、4 时的结果，并解释长度不是 2 的幂时最后的片段如何处理。保留原列表。

1. width=1：合并 \[7\] 与 \[2\]、\[6\] 与 \[1\]，最后 \[5\] 与空片段合并，得到 \[2, 7, 1, 6, 5\]。
2. width=2：合并 \[2, 7\] 与 \[1, 6\]，最后的 \[5\] 继续保留，得到 \[1, 2, 6, 7, 5\]。
3. width=4：合并 \[1, 2, 6, 7\] 与 \[5\]，得到 \[1, 2, 5, 6, 7\]。
4. 接着 width=8 已不小于长度 5，停止；总共三轮，每轮输出都保留五项。
5. 切片只读取已有项，剩余单段交给合并函数，不补零、不丢掉尾部，也不要求长度正好为 2 的幂。

**结果与核对**

三轮结果按 1、2、4 的宽度输出，最终为 \[1, 2, 5, 6, 7\]，原列表仍为 \[7, 2, 6, 1, 5\]。每轮产生新的外层列表，原输入未参与写入。

**完整程序**

```python
def merge_sorted(left, right):
    result = []
    i = 0
    j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i = i + 1
        else:
            result.append(right[j])
            j = j + 1
    while i < len(left):
        result.append(left[i])
        i = i + 1
    while j < len(right):
        result.append(right[j])
        j = j + 1
    return result

def merge_pass(values, width):
    result = []
    for start in range(0, len(values), 2 * width):
        left = values[start:start + width]
        right = values[start + width:start + 2 * width]
        merged = merge_sorted(left, right)
        for value in merged:
            result.append(value)
    return result

values = [7, 2, 6, 1, 5]
current = values.copy()
width = 1
while width < len(current):
    current = merge_pass(current, width)
    print(width, current)
    width = width * 2
print(values)
```

**预期输出**

```text
1 [2, 7, 1, 6, 5]
2 [1, 2, 6, 7, 5]
4 [1, 2, 5, 6, 7]
[7, 2, 6, 1, 5]
```


<a id="practice"></a>

## 自己做：先完成再看解答

### 练习 1

实现原地冒泡排序 bubble\_sort：每趟从左到右比较相邻项，只在前项更大时交换；一趟没有交换就提前停止。返回实际相邻元素比较次数。检查 \[4, 1, 3, 1\]、已经有序的 \[1, 1, 3, 4\] 与空列表。

<details>
<summary>提示</summary>

每趟把当前最大项推到未完成范围末端，下一趟缩短末端。用 changed 记录本趟是否交换，相等时保持顺序。

</details>

<details>
<summary>解答与检查</summary>

第一组结果为 \[1, 1, 3, 4\]，比较 3+2+1=6 次；第二组第一趟无交换，只比较 3 次；空列表比较 0 次。提前停止使最好时间为 Θ(n)，最坏仍为 Θ(n²)，辅助空间 O(1)。严格大于才交换，保证相等项不互相越过。

**完整程序**

```python
def bubble_sort(values):
    end = len(values) - 1
    changed = True
    checks = 0
    while end > 0 and changed:
        changed = False
        for index in range(end):
            checks = checks + 1
            if values[index] > values[index + 1]:
                saved = values[index]
                values[index] = values[index + 1]
                values[index + 1] = saved
                changed = True
        end = end - 1
    return checks

values = [4, 1, 3, 1]
print(bubble_sort(values), values)
ordered = [1, 1, 3, 4]
print(bubble_sort(ordered), ordered)
print(bubble_sort([]))
```

**预期输出**

```text
6 [1, 1, 3, 4]
3 [1, 1, 3, 4]
0
```


</details>

### 练习 2

记录使用 key 与 tag 两个字段，依次为 2R、1S、2T、1U。编写 stable\_by\_key，只按整数 key 做稳定插入排序，返回新的外层列表，不修改输入列表或记录字段。输出新旧 tag 顺序，说明浅拷贝的边界。

<details>
<summary>提示</summary>

先复制外层列表；比较时读取记录的 key，移动整条记录引用，只在前一 key 严格更大时右移。

</details>

<details>
<summary>解答与检查</summary>

新 tag 顺序为 S、U、R、T，原顺序为 R、S、T、U。相同 key=1 的 S 在 U 前，key=2 的 R 在 T 前；没有按 tag 另排一次。新旧外层仍引用原记录，排序不修改字段，但以后修改某条共享记录仍会在两边可见。

**完整程序**

```python
def stable_by_key(records):
    result = records.copy()
    for index in range(1, len(result)):
        pending = result[index]
        cursor = index
        while cursor > 0 and result[cursor - 1]["key"] > pending["key"]:
            result[cursor] = result[cursor - 1]
            cursor = cursor - 1
        result[cursor] = pending
    return result

def record_tags(records):
    tags = []
    for record in records:
        tags.append(record["tag"])
    return tags

records = [{"key": 2, "tag": "R"}, {"key": 1, "tag": "S"}, {"key": 2, "tag": "T"}, {"key": 1, "tag": "U"}]
print(record_tags(stable_by_key(records)))
print(record_tags(records))
```

**预期输出**

```text
['S', 'U', 'R', 'T']
['R', 'S', 'T', 'U']
```


</details>

### 练习 3

把归并排序与首匹配二分组合为 sorted\_lookup(values, target)，返回含 sorted、index 字段的字典，保留原列表。对 \[8, 3, 8, 1\] 查找 8 和 4。说明 index 指向哪里，以及只查一次时为何未必比顺序查找更省工作。

<details>
<summary>提示</summary>

先取得新的有序列表，再在这份列表上二分。不要把新下标用于原列表读取，也不要遗漏排序阶段的成本。

</details>

<details>
<summary>解答与检查</summary>

有序结果为 \[1, 3, 8, 8\]，查找 8 返回 2，查找 4 返回 -1。这里 2 是有序副本中的首个匹配；原列表第一个 8 在下标 0。总成本包含 Θ(n log n) 的排序，单次无序查询可直接线性查找；需要多次查询时应复用已排好的副本。

**完整程序**

```python
def merge_sorted(left, right):
    result = []
    i = 0
    j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i = i + 1
        else:
            result.append(right[j])
            j = j + 1
    while i < len(left):
        result.append(left[i])
        i = i + 1
    while j < len(right):
        result.append(right[j])
        j = j + 1
    return result

def merge_pass(values, width):
    result = []
    for start in range(0, len(values), 2 * width):
        left = values[start:start + width]
        right = values[start + width:start + 2 * width]
        merged = merge_sorted(left, right)
        for value in merged:
            result.append(value)
    return result

def merge_sort(values):
    result = values.copy()
    width = 1
    while width < len(result):
        result = merge_pass(result, width)
        width = width * 2
    return result

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

def sorted_lookup(values, target):
    ordered = merge_sort(values)
    return {"sorted": ordered, "index": binary_first(ordered, target)}

values = [8, 3, 8, 1]
print(sorted_lookup(values, 8))
print(sorted_lookup(values, 4))
print(values)
```

**预期输出**

```text
{'sorted': [1, 3, 8, 8], 'index': 2}
{'sorted': [1, 3, 8, 8], 'index': -1}
[8, 3, 8, 1]
```


</details>

<a id="pitfalls"></a>

## 容易混淆的地方

- **只检查非降序，不检查元素是否被丢失、重复写入或去重。** 同时核对长度与每个值的出现次数；相等时合并也必须分别保留两项。
- **认为原地就一定稳定，或相等时不更新最小位置就能保证选择排序稳定。** 稳定性看相等关键字记录的相对次序；远距离交换仍可能跨过另一条相等记录。
- **覆盖待插值后才想保存，或把归并尾部不足一段当作无效数据。** 插入前保存 pending；合并单侧剩余项，切片按实际长度读取，不添加占位值。
- **把调试轨迹当作 O(1) 空间，或把排序后下标当作原位置。** 保存多份状态要单独计空间；下标属于实际查询的那份排列，保留原位置需额外设计。

<a id="self-check"></a>

## 离开这一章前

- [ ] 分别给空、单元素、全相等、已排序、逆序、含负数的列表运行全部排序。
- [ ] 手算选择与插入的每轮前缀，核对元素比较和右移的不同计数。
- [ ] 用带 tag 的重复关键字验证稳定性，而不只看数值输出。
- [ ] 对长度 3、5、9 的列表画出归并各轮宽度，确认末段没有丢失。
- [ ] 组合排序和查找时，写清输入副作用、下标归属、准备成本与能复用的结果。

## 本章边界

- 时间与空间沿用单位成本和单位引用模型；不把小规模演示当作性能基准。
- 手写四种入门排序；快速排序、堆排序、计数排序及完整比较排序下界留待后续。
- 归并用切片和新列表保持实现直观，峰值额外空间 O(n)，不宣称原地归并。
- 记录示例仅按整数 key 排序，不修改字段；不讨论通用比较器、并发修改和浮点特殊值。

## 选题来源与覆盖

来源含学生报告时，仅将其作为选题线索；具体机制仍需结合后续实验或权威资料核对。

- [大一小学期/Week\_3-Python/docs/readme.md](https://github.com/PKUanonym/REKCARC-TSC-UHT/blob/37cd19f7a9fb80dc846a7016b3fd482ed5fe7cc0/%E5%A4%A7%E4%B8%80%E5%B0%8F%E5%AD%A6%E6%9C%9F/Week_3-Python/docs/readme.md)（已提取可读文本，固定版本 37cd19f7a9fb）
- 主题 1：Python 基础语法的外部学习入口；位置：第 41–80 行。
- 主题 2：从基础语法到工具与应用的建议阅读顺序；位置：第 121–160 行。

## 参考资料与规则核对

上游入口用于确定学习方向；下面的参考资料用于核对语言语义、数据结构或算法分析规则，例题和练习由本项目重新设计。

- [Python 3.11：排序与稳定性](https://docs.python.org/3.11/howto/sorting.html)：核对 sorted 与 list.sort 的返回和修改语义，以及相等关键字的稳定性定义。
- [Algorithms 4/e：初等排序](https://algs4.cs.princeton.edu/21elementary/)：核对选择与插入的机制和成本；本章使用保存待插值的移动实现，自行设计例题与计数。
- [Algorithms 4/e：自底向上归并](https://algs4.cs.princeton.edu/code/javadoc/edu/princeton/cs/algs4/MergeBU.html)：核对非递归归并及线性额外空间；本章用切片和新列表实现并单独分析峰值，不移植 Java 代码。

**继续学习**：先独立完成自测，再记录仍需回读的步骤。

[上一章：怎样缩小候选范围：顺序查找与二分查找](11-searching.md) · [下一章：函数怎样调用自己：递归、返回与调用栈](13-recursion.md)

[教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [哈希表与图练习指引](../hash-graphs-practice.md) · [记录自己的学习](../learning-log-template.md)
