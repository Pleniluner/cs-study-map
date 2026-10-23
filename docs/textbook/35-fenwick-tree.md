# 动态维护前缀：树状数组与频次排名

[返回教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [哈希表与图练习指引](../hash-graphs-practice.md) · [拓扑排序与带权图练习指引](../weighted-graphs-practice.md)

[上一章：淘汰不再有用的候选：单调栈与单调队列](34-monotonic-structures.md) · [下一章：合并区间摘要：线段树与延迟更新](36-segment-tree.md)

[学习目标](#objectives) · [需要的基础](#prerequisites) · [例题](#examples) · [练习](#practice) · [自测](#self-check)

状态：**AI 初稿，可开始试学**。生成模型：Codex 当前会话（未记录具体模型型号）。

本章围绕资料中识别到的知识点重新编写；讲解、数值模型、例题与练习为 AI 原创组织，不是原课程题目或答案。主题出处只说明选题关联，不证明全部推导已经正确。

前缀和能快速回答静态区间和，但修改一个元素后，后面的许多前缀值都会变化。树状数组把前缀拆成少量二进制对齐的块，使修改与查询只访问对数个位置。本章先解释每个槽究竟保存哪一段，再实现单点增加、区间求和、线性构建与频次排名。所有公开下标从零开始、区间采用半开形式，内部编号从一开始，两套编号始终分开。

<a id="objectives"></a>

## 学完要能做到

- 解释 lowbit 与每个树状数组槽的区间含义。
- 实现单点增加、点赋值和前缀、区间求和，区别增量与新值。
- 证明线性构建正确，并用非负频次完成排名定位。
- 由差分推导范围加单点查与双树范围求和，核对停止边界。

<a id="prerequisites"></a>

## 需要的基础

- 第 6、10、11 章的列表、复杂度和二分边界。
- 第 18 章用列表表示树的编号习惯。
- 第 33 章的前缀和、差分与半开范围。

## lowbit：一个编号对应一块怎样的区间

对正整数 i，lowbit(i)=i &amp; −i 得到二进制中最低的那个 1 所代表的值。例如 12 的二进制为 1100，lowbit 是 4；13 为 1101，lowbit 是 1。符号 &amp; 表示逐位与，只有两边对应位都为 1 才保留。对正数取负的补码表示，在最低有效 1 以下仍全为零、该位仍为 1，更高位与原数互补，因此按位与只留下这一位。

Python 按位运算的语义相当于具有无限符号扩展的补码，不需要自行截断为某个机器字长。零的 lowbit 仍为零，若拿它推进编号，循环会停滞；所以内部使用正编号，前缀查询到零就结束。这里不是用数值大小猜块长，而是在利用编号的二进制结构。

定义 tree\[i\] 保存外部区间 \[i−lowbit(i),i) 的和。内部 i 是一个右边界编号，不是外部元素 i 的下标。前 stop 项可从右向左拆块：先取结束于 stop 的块，再减去块长，重复直到零。stop=13 对应 \[12,13)、\[8,12)、\[0,8)，块之间不重叠，拼起来恰为 \[0,13)。

每次减 lowbit 都清除最低的一个 1，最多执行与二进制位数相同的次数。prefix\_blocks 约定 stop 为非负整数，负数返回 None，零返回 \[\]；时间和输出空间 O(log(stop+1)+1)。学习时先把每个块画在数轴上，再写求和循环，能避免把外部下标、内部编号和区间终点混为一谈。本节只展示块分解，真正保存各块之和的结构从下一节开始。

**完整程序**

```python
def prefix_blocks(stop):
    if stop < 0:
        return None
    blocks = []
    i = stop
    while i > 0:
        low = i & -i
        blocks.append([i - low, i])
        i = i - low
    return blocks

print(prefix_blocks(13))
print(prefix_blocks(0), prefix_blocks(-1))
```

**预期输出**

```text
[[12, 13], [8, 12], [0, 8]]
[] None
```


选题关联：来源主题 1（文末列出）。

## 单点增加与前缀查询：沿两种方向访问块

长度 n 的树状数组使用 n+1 个槽，tree\[0\] 不存有效块，初始值全零。外部位置 index 的单点增加从内部编号 index+1 开始，每次把 delta 加到当前槽，再令 i 增加 lowbit(i)，直到超过 n。查询前 stop 项则从 i=stop 出发，累加槽值并减 lowbit(i)，直到零。

查询路径正是上一节的不重叠前缀分解。更新路径为什么相反地增加？当前块已经包含被修改的那一点；i+lowbit(i) 把它提升到更大的对齐块，其中也包含这点。沿此路径恰好访问所有包含该外部元素的块，其他槽代表不含它的区间，无需改变。于是每次更新之后，所有 tree\[i\] 的块和定义仍成立。

对四个位置依次增加 1、2、3、4，内部表成为 \[0,1,3,3,10\]。其中 tree\[4\] 汇总前四项，tree\[3\] 只保存第三项；查询前 3 项取 tree\[3\]+tree\[2\]=3+3=6。表格看上去不像原数组，不应直接把 tree\[index\] 当作当前位置值。

fenwick\_new 拒绝负长度，零长度合法。增加操作先检查位置，非法返回 False 且不改变结构；查询终点允许 0 与 n，越界返回 None。所有接口要求 state 来自本章构造器且未被调用者改坏，不在每次查询时重验整棵树。初始化 O(n+1)，每次增加或前缀查询 O(log(n+1)+1)，结构 O(n+1) 空间。示例逐点插入 n 项需 O(n log(n+1)+1) 时间，不能因为单次操作快就把建树也写成线性。

**完整程序**

```python
def fenwick_new(size):
    if size < 0:
        return None
    return {'size': size, 'tree': [0] * (size + 1)}

def fenwick_add(state, index, delta):
    if index < 0 or index >= state['size']:
        return False
    i = index + 1
    while i <= state['size']:
        state['tree'][i] = state['tree'][i] + delta
        i = i + (i & -i)
    return True

def fenwick_prefix(state, stop):
    if stop < 0 or stop > state['size']:
        return None
    total = 0
    i = stop
    while i > 0:
        total = total + state['tree'][i]
        i = i - (i & -i)
    return total

state = fenwick_new(4)
for i in range(4):
    fenwick_add(state, i, i + 1)
print(state['tree'])
print(fenwick_prefix(state, 3), fenwick_prefix(state, 0))
print(fenwick_add(state, 4, 8), fenwick_prefix(state, 5))
```

**预期输出**

```text
[0, 1, 3, 3, 10]
6 0
False None
```


选题关联：来源主题 1（文末列出）。

## 区间求和与点赋值：把接口语义写清楚

外部区间 \[start,stop) 的和仍是前 stop 项减前 start 项。树状数组只改变前缀信息的维护方式，没有改变第 33 章的相减恒等式。范围必须满足零起点、不倒置、不越过 n；空区间合法且和为零，非法返回 None。一般整数值允许为负，区间求和不要求前缀单调。

点赋值与点增加尤其容易混淆。若当前位置是 −2，要改为 7，应该增加 9，而不是增加 7。fenwick\_set 先查询这个单元素区间取得旧值，再把新值减旧值作为 delta 交给增加函数。无需额外维护一份同步原数组，也不会误把已经过时的输入快照当作当前值。

示例先得到 \[4,−2,5\]，查询 \[1,3) 为 3；把位置 1 设为 7 后，整段和为 16。连续两次设为同一个值，第二次增量为零，结果保持一致；连续两次增加同一个非零量则会重复累积。这种区别应从题目要求决定，不能靠函数名之外的猜测。

赋值在任何读取或写入前检查下标，非法返回 False。区间函数也先检查两个边界，所以不会拿某次失败查询的 None 做减法。空结构只允许 \[0,0) 查询，没有合法元素可赋值。点赋值由常数次对数操作组成，仍为 O(log(n+1)+1) 时间、O(1) 辅助空间；区间查询同阶。验证范围只需几个比较；若调用者手改内部 tree 或 size，函数没有承诺修复这类失效状态。

**完整程序**

```python
def fenwick_new(size):
    if size < 0:
        return None
    return {'size': size, 'tree': [0] * (size + 1)}

def fenwick_add(state, index, delta):
    if index < 0 or index >= state['size']:
        return False
    i = index + 1
    while i <= state['size']:
        state['tree'][i] = state['tree'][i] + delta
        i = i + (i & -i)
    return True

def fenwick_prefix(state, stop):
    if stop < 0 or stop > state['size']:
        return None
    total = 0
    i = stop
    while i > 0:
        total = total + state['tree'][i]
        i = i - (i & -i)
    return total

def fenwick_range(state, start, stop):
    if start < 0 or stop < start or stop > state['size']:
        return None
    return fenwick_prefix(state, stop) - fenwick_prefix(state, start)

def fenwick_set(state, index, value):
    if index < 0 or index >= state['size']:
        return False
    old = fenwick_range(state, index, index + 1)
    return fenwick_add(state, index, value - old)

state = fenwick_new(3)
fenwick_add(state, 0, 4)
fenwick_add(state, 1, -2)
fenwick_add(state, 2, 5)
print(fenwick_range(state, 1, 3))
print(fenwick_set(state, 1, 7), fenwick_range(state, 0, 3))
print(fenwick_range(state, 2, 2), fenwick_range(state, 2, 1))
```

**预期输出**

```text
3
True 16
0 None
```


选题关联：来源主题 1（文末列出）。

## 线性构建：把已经完成的小块交给父块

已有完整整数列表时，可以避免逐点增加。先令 tree=\[0\]+values 的独立副本，再按内部编号从小到大处理 i：把 tree\[i\] 加到 parent=i+lowbit(i)，若 parent 已超过 n 就不再传递。这里只向一个父块转交一次，而非沿更新路径转交所有祖先。

为什么这样足够？处理 i 之前，所有编号更小、应归入它的直接子块都已完成，并把各自整块之和传来。它们的范围互不重叠，加上最初放在 i 的那个元素，恰好组成 \[i−lowbit(i),i)。现在 tree\[i\] 已是最终块和，可以整体送给父块；更远祖先会在父块处理时收到它，避免重复计算。

对 \[4,−2,0,5,1\]，初始槽为 \[0,4,−2,0,5,1\]。编号 1 把 4 交给 2，编号 2 把已汇总的 2 交给 4，编号 3 再把 0 交给 4，最后得到 \[0,4,2,0,7,1\]。第五个槽仍只负责最后一项，并不要求根式的单一槽覆盖所有元素；整段查询会按前缀分解访问多个块。

parent 总比 i 大，这是递增处理能成立的依赖顺序。每个编号最多一次转交，连同复制与初始化，构建时间 O(n+1)、结构空间 O(n+1)。零长度得到 size=0、tree=\[0\]，与前几节接口兼容。values 后来变化不会自动改变树，树上的更新也不会改原列表；测试应分别检查不变量与输入独立性。线性构建和逐点构建得到同样的块值，但对拍两种实现不足以替代直接求每块之和的独立核验。

**完整程序**

```python
def fenwick_build(values):
    tree = [0] + values.copy()
    for i in range(1, len(tree)):
        parent = i + (i & -i)
        if parent < len(tree):
            tree[parent] = tree[parent] + tree[i]
    return {'size': len(values), 'tree': tree}

values = [4, -2, 0, 5, 1]
print(fenwick_build(values)['tree'])
print(fenwick_build([]))
print(values)
```

**预期输出**

```text
[0, 4, 2, 0, 7, 1]
{'size': 0, 'tree': [0]}
[4, -2, 0, 5, 1]
```


选题关联：来源主题 1（文末列出）。

## 非负频次的排名：沿二进制块定位第 k 项

假设桶号按顺序排列，每桶保存非负整数频次。第 rank 项使用从 1 开始的排名，求它落在哪个零起点桶。例 \[0,2,0,3\] 表示前两个元素在桶 1，后三个在桶 3；第 1 项落在 1，第 3 项落在 3。零频次桶允许跳过，空表或总频次为零时没有合法排名。

所有频次非负，前缀计数才不会下降。寻找的桶是第一个使包含它的前缀计数达到 rank 的位置。程序维护已跳过的前缀长度 position，以及尚需跨过的排名 remaining，从不超过 n 的最大二次幂开始尝试块长。若候选块累计数仍严格小于 remaining，就整块跳过并扣除其频次，否则保留当前位置；然后把步长减半。

每轮 position 是更大步长组成的边界，因此试探 following=position+step 时，tree\[following\] 正好覆盖尚未跳过的那一块。结束时 position 是计数仍不足原排名的最长前缀长度，也恰为答案的零起点桶号。比较必须严格：若一块刚好达到排名，目标仍在该块内，不能把它整个跳过。这个过程直接读取槽，而不是每轮再做一次前缀查询。

对上述频次找第 3 项：步长 4 时整块计数 5，不能跳过；步长 2 时前两桶计数 2，跳过后 position=2、remaining=1；步长 1 时下一桶计数为零，继续跳到 position=3。步长归零，答案就是桶 3。注意剩余排名减少的是桶内元素数，position 增加的是桶数，两种单位不可互换。

frequency\_new 完整拒绝负频次并复制输入。以后只用 frequency\_change 修改，它先检查下标及更新后非负，再同时改 counts 和内部树；失败不变。若错误允许 \[2,−2,2\]，前两桶的总数零会诱使程序整块跳过，尽管第一个前缀早已达到排名 1，正说明单调性不是可省略的形式条件。绕过专用接口调用通用增加函数可能破坏前提。构建 O(n+1)，一次修改或排名查询 O(log(n+1)+1)，空间 O(n+1)。没有按总频次展开元素，所以巨大计数不会分配同样多的元素槽；整数位数的算术成本仍须另计。

**完整程序**

```python
def fenwick_new(size):
    if size < 0:
        return None
    return {'size': size, 'tree': [0] * (size + 1)}

def fenwick_add(state, index, delta):
    if index < 0 or index >= state['size']:
        return False
    i = index + 1
    while i <= state['size']:
        state['tree'][i] = state['tree'][i] + delta
        i = i + (i & -i)
    return True

def fenwick_prefix(state, stop):
    if stop < 0 or stop > state['size']:
        return None
    total = 0
    i = stop
    while i > 0:
        total = total + state['tree'][i]
        i = i - (i & -i)
    return total

def fenwick_build(values):
    tree = [0] + values.copy()
    for i in range(1, len(tree)):
        parent = i + (i & -i)
        if parent < len(tree):
            tree[parent] = tree[parent] + tree[i]
    return {'size': len(values), 'tree': tree}

def frequency_new(counts):
    for count in counts:
        if count < 0:
            return None
    return {'counts': counts.copy(), 'bit': fenwick_build(counts)}

def frequency_change(state, index, delta):
    if index < 0 or index >= len(state['counts']):
        return False
    updated = state['counts'][index] + delta
    if updated < 0:
        return False
    state['counts'][index] = updated
    return fenwick_add(state['bit'], index, delta)

def frequency_select(state, rank):
    bit = state['bit']
    size = bit['size']
    if rank <= 0 or rank > fenwick_prefix(bit, size):
        return None
    step = 1
    while step * 2 <= size:
        step = step * 2
    position = 0
    remaining = rank
    while step > 0:
        following = position + step
        if following <= size and bit['tree'][following] < remaining:
            remaining = remaining - bit['tree'][following]
            position = following
        step = step // 2
    return position

state = frequency_new([0, 2, 0, 3])
print(frequency_select(state, 1), frequency_select(state, 3))
print(frequency_select(state, 0), frequency_select(state, 6))
print(frequency_change(state, 1, -3), state['counts'])
print(frequency_change(state, 1, -2), frequency_select(state, 1))
```

**预期输出**

```text
1 3
None None
False [0, 2, 0, 3]
True 3
```


选题关联：来源主题 1（文末列出）。

<a id="examples"></a>

## 跟着做：原创例题

### 例题 1

四个位置的测量计数为 \[3,0,5,2\]。先把位置 1 改为 4，再把位置 2 减少 2，随后查询 \[1,4) 与全段。说明原始输入为何不能继续充当当前值。

1. 用线性构建保存初始块和，原列表仍为初始快照。
2. 点赋值读取当前位置 1 的旧值 0，增加 4，逻辑列表变成 \[3,4,5,2\]。
3. 位置 2 增加 −2，逻辑列表变成 \[3,4,3,2\]。
4. 前缀相减得到 \[1,4) 的和 9、全段和 12；越界赋值在写入前被拒绝。

**结果与核对**

查询结果为 9 和 12，输入 \[3,0,5,2\] 不变。通用树允许负值，是否禁止某类业务计数变负应由另一个明确接口维护，本例两次修改都合法。设 n 项、q 次交错操作，线性构建后总时间 O(n+q log(n+1)+q+1)，空间 O(n+1)；独立测试直接更新一份列表，再逐区间求和。

**完整程序**

```python
def fenwick_new(size):
    if size < 0:
        return None
    return {'size': size, 'tree': [0] * (size + 1)}

def fenwick_add(state, index, delta):
    if index < 0 or index >= state['size']:
        return False
    i = index + 1
    while i <= state['size']:
        state['tree'][i] = state['tree'][i] + delta
        i = i + (i & -i)
    return True

def fenwick_prefix(state, stop):
    if stop < 0 or stop > state['size']:
        return None
    total = 0
    i = stop
    while i > 0:
        total = total + state['tree'][i]
        i = i - (i & -i)
    return total

def fenwick_build(values):
    tree = [0] + values.copy()
    for i in range(1, len(tree)):
        parent = i + (i & -i)
        if parent < len(tree):
            tree[parent] = tree[parent] + tree[i]
    return {'size': len(values), 'tree': tree}

def fenwick_range(state, start, stop):
    if start < 0 or stop < start or stop > state['size']:
        return None
    return fenwick_prefix(state, stop) - fenwick_prefix(state, start)

def fenwick_set(state, index, value):
    if index < 0 or index >= state['size']:
        return False
    old = fenwick_range(state, index, index + 1)
    return fenwick_add(state, index, value - old)

values = [3, 0, 5, 2]
state = fenwick_build(values)
fenwick_set(state, 1, 4)
fenwick_add(state, 2, -2)
print(fenwick_range(state, 1, 4), fenwick_range(state, 0, 4))
print(values)
print(fenwick_set(state, -1, 99))
```

**预期输出**

```text
9 12
[3, 0, 5, 2]
False
```


### 例题 2

初始 \[2,0,3,1\]，给 \[1,4) 加 2，再给 \[0,2) 加 −1。要求每次更新后可立即查某一个位置，如何把差分变成动态结构？

1. 相邻差构成 \[2,−2,3,−2\]，末尾再放 −1 作为停止哨兵，差分表长度 n+1。
2. 范围增加只改 start 处加 delta、stop 处减 delta；stop=n 时仍有合法哨兵槽。
3. 某位置的真实值是差分前 index+1 项之和，树状数组可立即返回这个前缀值。
4. 两次更新后各点为 \[1,1,5,3\]；空区间的开始与停止事件在同一位置相消。

**结果与核对**

最终四点为 1、1、5、3。difference\_add 的所有边界先检查，非法返回 False 且不变；点查询只允许 0 到 n−1，哨兵不是额外数据点。零长度仍有一项差分哨兵，允许空更新而无合法点查询。构建 O(n+1)，每次操作 O(log(n+2))，空间 O(n+1)。这里求前缀是为了恢复一个点，不能把差分树的前缀误当原列表区间总和。

**完整程序**

```python
def fenwick_new(size):
    if size < 0:
        return None
    return {'size': size, 'tree': [0] * (size + 1)}

def fenwick_add(state, index, delta):
    if index < 0 or index >= state['size']:
        return False
    i = index + 1
    while i <= state['size']:
        state['tree'][i] = state['tree'][i] + delta
        i = i + (i & -i)
    return True

def fenwick_prefix(state, stop):
    if stop < 0 or stop > state['size']:
        return None
    total = 0
    i = stop
    while i > 0:
        total = total + state['tree'][i]
        i = i - (i & -i)
    return total

def fenwick_build(values):
    tree = [0] + values.copy()
    for i in range(1, len(tree)):
        parent = i + (i & -i)
        if parent < len(tree):
            tree[parent] = tree[parent] + tree[i]
    return {'size': len(values), 'tree': tree}

def difference_new(values):
    differences = []
    previous = 0
    for value in values:
        differences.append(value - previous)
        previous = value
    differences.append(-previous)
    return {'size': len(values), 'bit': fenwick_build(differences)}

def difference_add(state, start, stop, delta):
    if start < 0 or stop < start or stop > state['size']:
        return False
    fenwick_add(state['bit'], start, delta)
    fenwick_add(state['bit'], stop, -delta)
    return True

def difference_point(state, index):
    if index < 0 or index >= state['size']:
        return None
    return fenwick_prefix(state['bit'], index + 1)

state = difference_new([2, 0, 3, 1])
difference_add(state, 1, 4, 2)
difference_add(state, 0, 2, -1)
print(difference_point(state, 0), difference_point(state, 1), difference_point(state, 2), difference_point(state, 3))
print(difference_add(state, 4, 4, 9), difference_point(state, 4))
print(difference_add(difference_new([]), 0, 0, 7))
```

**预期输出**

```text
1 1 5 3
True None
True
```


<a id="practice"></a>

## 自己做：先完成再看解答

### 练习 1

给定整数列表及包含所有值的严格升序坐标表，统计逆序对：较早位置的值严格大于较晚位置。求 \[3,1,3,0\]，坐标表 \[0,1,3\]。

<details>
<summary>提示</summary>

先二分求每个值的坐标秩，再从左向右维护已见频次。处理秩 r 时，已见总数减去截至 r 的前缀频次，得到严格更大者个数。

</details>

<details>
<summary>解答与检查</summary>

答案为 4。两次出现的 3 不互相构成逆序对，故查询终点要用 r+1，把相等值也从“更大”中排除。程序完整检查坐标严格递增和所有值确实存在，失败返回 None，未修改输入；空列表和空坐标返回 0。设 n 项、m 个坐标，含验证、二分和初始化，时间 O(m+n log(m+1)+n+1)，保存秩和树的空间 O(n+m+1)。坐标表是本题给定输入，若自行排序压缩，还须另计准备成本。

**完整程序**

```python
def fenwick_new(size):
    if size < 0:
        return None
    return {'size': size, 'tree': [0] * (size + 1)}

def fenwick_add(state, index, delta):
    if index < 0 or index >= state['size']:
        return False
    i = index + 1
    while i <= state['size']:
        state['tree'][i] = state['tree'][i] + delta
        i = i + (i & -i)
    return True

def fenwick_prefix(state, stop):
    if stop < 0 or stop > state['size']:
        return None
    total = 0
    i = stop
    while i > 0:
        total = total + state['tree'][i]
        i = i - (i & -i)
    return total

def inversion_count(values, coordinates):
    for i in range(1, len(coordinates)):
        if coordinates[i] <= coordinates[i - 1]:
            return None
    ranks = []
    for value in values:
        left = 0
        right = len(coordinates)
        while left < right:
            middle = (left + right) // 2
            if coordinates[middle] < value:
                left = middle + 1
            else:
                right = middle
        if left == len(coordinates) or coordinates[left] != value:
            return None
        ranks.append(left)
    bit = fenwick_new(len(coordinates))
    result = 0
    for i in range(len(ranks)):
        result = result + i - fenwick_prefix(bit, ranks[i] + 1)
        fenwick_add(bit, ranks[i], 1)
    return result

print(inversion_count([3, 1, 3, 0], [0, 1, 3]))
print(inversion_count([], []))
print(inversion_count([2], [0, 1, 3]))
print(inversion_count([1], [1, 1]))
```

**预期输出**

```text
4
0
None
None
```


</details>

### 练习 2

在允许交错操作的情况下实现范围增加与范围求和。沿用 \[2,0,3,1\] 的两次更新，查询 \[1,4) 和全段。请从零起点差分推导双树公式。

<details>
<summary>提示</summary>

差分 D\[i\] 会在前 stop 项里贡献 stop−i 次，前提是 i 在 \[0,stop)。因此前缀总和等于 stop 乘以这些差分之和，再减去 i×D\[i\] 之和。

</details>

<details>
<summary>解答与检查</summary>

两棵树分别维护 D\[i\] 与 i×D\[i\]，prefix(stop)=stop×B1.prefix(stop)−B2.prefix(stop)。范围增加在 l 加 delta、在 r 减 delta，第二棵相应加 l×delta、减 r×delta。最终查询为 9 和 10；空范围为 0。包括末尾哨兵的构建时间、空间均 O(n+1)，每次操作 O(log(n+2))。所有四次写入之前统一验证范围；不能混用从一开始的权重公式。此方法依赖加法和线性权重，不能直接换成区间最小值。

**完整程序**

```python
def fenwick_new(size):
    if size < 0:
        return None
    return {'size': size, 'tree': [0] * (size + 1)}

def fenwick_add(state, index, delta):
    if index < 0 or index >= state['size']:
        return False
    i = index + 1
    while i <= state['size']:
        state['tree'][i] = state['tree'][i] + delta
        i = i + (i & -i)
    return True

def fenwick_prefix(state, stop):
    if stop < 0 or stop > state['size']:
        return None
    total = 0
    i = stop
    while i > 0:
        total = total + state['tree'][i]
        i = i - (i & -i)
    return total

def fenwick_build(values):
    tree = [0] + values.copy()
    for i in range(1, len(tree)):
        parent = i + (i & -i)
        if parent < len(tree):
            tree[parent] = tree[parent] + tree[i]
    return {'size': len(values), 'tree': tree}

def dual_new(values):
    differences = []
    weighted = []
    previous = 0
    for i in range(len(values)):
        delta = values[i] - previous
        differences.append(delta)
        weighted.append(i * delta)
        previous = values[i]
    differences.append(-previous)
    weighted.append(-len(values) * previous)
    return {'size': len(values), 'plain': fenwick_build(differences), 'weighted': fenwick_build(weighted)}

def dual_add(state, start, stop, delta):
    if start < 0 or stop < start or stop > state['size']:
        return False
    fenwick_add(state['plain'], start, delta)
    fenwick_add(state['plain'], stop, -delta)
    fenwick_add(state['weighted'], start, start * delta)
    fenwick_add(state['weighted'], stop, -stop * delta)
    return True

def dual_prefix(state, stop):
    if stop < 0 or stop > state['size']:
        return None
    return stop * fenwick_prefix(state['plain'], stop) - fenwick_prefix(state['weighted'], stop)

def dual_range(state, start, stop):
    if start < 0 or stop < start or stop > state['size']:
        return None
    return dual_prefix(state, stop) - dual_prefix(state, start)

state = dual_new([2, 0, 3, 1])
dual_add(state, 1, 4, 2)
dual_add(state, 0, 2, -1)
print(dual_range(state, 1, 4), dual_range(state, 0, 4))
print(dual_range(state, 2, 2), dual_range(state, -1, 3))
print(dual_range(dual_new([]), 0, 0))
```

**预期输出**

```text
9 10
0 None
0
```


</details>

### 练习 3

非负频次表按桶号表示一个有序多重集合，返回下中位数和上中位数所在桶号。求 \[0,2,0,2\]；再给桶 3 增加一次。

<details>
<summary>提示</summary>

总数 N 非零时，两项的从一开始排名分别为 (N+1)//2 与 N//2+1。调用排名函数，不展开重复元素。

</details>

<details>
<summary>解答与检查</summary>

四项时返回 \[1,3\]；增加后五项返回 \[3,3\]。奇数项的两个排名相同，偶数项可能落在同桶，也可能落在不同桶；函数返回桶号，不计算两个桶值的算术平均。空集合返回 \[\]，频次创建和更新仍须通过非负接口。对 n 个桶，除已有构造外，一次查询 O(log(n+1)+1) 时间、O(1) 辅助空间；哪怕某桶频次很大，也不分配同样多的元素槽。

**完整程序**

```python
def fenwick_new(size):
    if size < 0:
        return None
    return {'size': size, 'tree': [0] * (size + 1)}

def fenwick_add(state, index, delta):
    if index < 0 or index >= state['size']:
        return False
    i = index + 1
    while i <= state['size']:
        state['tree'][i] = state['tree'][i] + delta
        i = i + (i & -i)
    return True

def fenwick_prefix(state, stop):
    if stop < 0 or stop > state['size']:
        return None
    total = 0
    i = stop
    while i > 0:
        total = total + state['tree'][i]
        i = i - (i & -i)
    return total

def fenwick_build(values):
    tree = [0] + values.copy()
    for i in range(1, len(tree)):
        parent = i + (i & -i)
        if parent < len(tree):
            tree[parent] = tree[parent] + tree[i]
    return {'size': len(values), 'tree': tree}

def frequency_new(counts):
    for count in counts:
        if count < 0:
            return None
    return {'counts': counts.copy(), 'bit': fenwick_build(counts)}

def frequency_change(state, index, delta):
    if index < 0 or index >= len(state['counts']):
        return False
    updated = state['counts'][index] + delta
    if updated < 0:
        return False
    state['counts'][index] = updated
    return fenwick_add(state['bit'], index, delta)

def frequency_select(state, rank):
    bit = state['bit']
    size = bit['size']
    if rank <= 0 or rank > fenwick_prefix(bit, size):
        return None
    step = 1
    while step * 2 <= size:
        step = step * 2
    position = 0
    remaining = rank
    while step > 0:
        following = position + step
        if following <= size and bit['tree'][following] < remaining:
            remaining = remaining - bit['tree'][following]
            position = following
        step = step // 2
    return position

def median_buckets(state):
    total = fenwick_prefix(state['bit'], len(state['counts']))
    if total == 0:
        return []
    lower = frequency_select(state, (total + 1) // 2)
    upper = frequency_select(state, total // 2 + 1)
    return [lower, upper]

state = frequency_new([0, 2, 0, 2])
print(median_buckets(state))
frequency_change(state, 3, 1)
print(median_buckets(state))
print(median_buckets(frequency_new([0, 0])))
```

**预期输出**

```text
[1, 3]
[3, 3]
[]
```


</details>

<a id="pitfalls"></a>

## 容易混淆的地方

- **从内部编号零开始更新，或把查询终点写成元素下标加错一次。** 更新外部 index 从 index+1 开始，前缀 stop 直接表示边界，零只作为停止条件。
- **把点赋值的新值直接当作增加量。** 先得到当前点值，再增加新旧之差；输入快照可能已经过时。
- **通用树支持负数，就认为频次排名也允许负数。** 排名要求前缀计数单调，构造和每次频次更新都必须保持非负。
- **省掉末尾差分槽，或两棵树中使用不同的编号约定。** 半开 stop 可以等于 n，差分需要 n+1 槽；权重 i 始终使用外部零起点编号。

<a id="self-check"></a>

## 离开这一章前

- [ ] 画出内部编号 1 到 8 各自覆盖的半开区间。
- [ ] 手算外部位置 2 更新时会改变哪些槽，并逐个核对是否包含该点。
- [ ] 解释线性构建时父编号为何总晚于子编号处理。
- [ ] 对频次 \[0,0,4,0\] 分别定位排名 1、4、5。
- [ ] 展开长度 3 的所有差分贡献，推导双树前缀公式而不背诵。

## 本章边界

- 接口约定整数参数和由构造器生成的有效状态，不提供任意类型转换或对内部破坏的自动修复。
- 本章仅实现一维加法结构与非负频次排名；二维树状数组、通用非可逆聚合和持久化版本尚未展开。
- 对数结论按单位整数操作计算；Python 大整数的按位与、加减乘、比较和存储需要额外位成本。

## 选题来源与覆盖

来源含学生报告时，仅将其作为选题线索；具体机制仍需结合后续实验或权威资料核对。

- [大一小学期/Week\_3-Python/docs/readme.md](https://github.com/PKUanonym/REKCARC-TSC-UHT/blob/37cd19f7a9fb80dc846a7016b3fd482ed5fe7cc0/%E5%A4%A7%E4%B8%80%E5%B0%8F%E5%AD%A6%E6%9C%9F/Week_3-Python/docs/readme.md)（已提取可读文本，固定版本 37cd19f7a9fb）
- 主题 1：Python 基础语法的外部学习入口；位置：第 41–80 行。
- 主题 2：从基础语法到工具与应用的建议阅读顺序；位置：第 121–160 行。

## 参考资料与规则核对

上游入口用于确定学习方向；下面的参考资料用于核对语言语义、数据结构或算法分析规则，例题和练习由本项目重新设计。

- [Python 3.11：整数的按位操作](https://docs.python.org/3.11/library/stdtypes.html#bitwise-operations-on-integer-types)：核对按位与及无限符号扩展补码语义；本章只新增已审读的 &amp; 语法，未引入第三方运行依赖。
- [Algorithms for Competitive Programming：Fenwick Tree](https://cp-algorithms.com/data_structures/fenwick.html)：核对块和、线性构建及范围操作的概念；本章重新采用外部零起点半开接口，推导加权差分并自定拒绝、空结构及排名更新规则，未移植页面代码或题目。

**继续学习**：先独立完成自测，再记录仍需回读的步骤。

[上一章：淘汰不再有用的候选：单调栈与单调队列](34-monotonic-structures.md) · [下一章：合并区间摘要：线段树与延迟更新](36-segment-tree.md)

[教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [哈希表与图练习指引](../hash-graphs-practice.md) · [拓扑排序与带权图练习指引](../weighted-graphs-practice.md) · [记录自己的学习](../learning-log-template.md)
