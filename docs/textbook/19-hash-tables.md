# 按键定位记录：哈希表、冲突与扩容

[返回教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [哈希表与图练习指引](../hash-graphs-practice.md) · [拓扑排序与带权图练习指引](../weighted-graphs-practice.md)

[上一章：让最值留在根部：二叉堆与优先队列](18-heaps.md) · [下一章：用顶点和边表达关系：图与存储表示](20-graphs.md)

[学习目标](#objectives) · [需要的基础](#prerequisites) · [例题](#examples) · [练习](#practice) · [自测](#self-check)

状态：**AI 初稿，可开始试学**。生成模型：Codex 当前会话（未记录具体模型型号）。

本章围绕资料中识别到的知识点重新编写；讲解、数值模型、例题与练习为 AI 原创组织，不是原课程题目或答案。主题出处只说明选题关联，不证明全部推导已经正确。

前一章把最小值放在堆顶，搜索树则利用键的大小排除一侧子树。现在换一种任务：给出一个编号，直接寻找与它关联的记录。哈希表先把键映射到有限个桶，再在选中的桶内确认原键。本章从可手算的取余开始，自己实现查询、更新、删除和扩容，最后用频次与两数配对连接实际问题。学习重点是映射必须一致、冲突必须处理，以及效率结论必须带上分布假设；桶号相同并不说明两个键相同。

<a id="objectives"></a>

## 学完要能做到

- 手算正负整数键的桶号，解释冲突与键相等的区别。
- 实现允许 None 值的映射，检查新增、覆盖和删除后的项数。
- 解释扩容为什么必须重算桶号，并区分期望、最坏与摊还成本。
- 用哈希记录已读前缀，完成频次统计、重复检测与两数配对。

<a id="prerequisites"></a>

## 需要的基础

- 掌握第 6 章列表、下标、引用和独立内层列表。
- 掌握第 5 章函数及第 10 章渐近记号与最好最坏分析，了解第 18 章列表操作的摊还口径。
- 能阅读前几章作为固定字段记录使用的字典；无需理解 Python 字典内部实现。

## 把键映射到桶：先明确输入契约

映射保存键与值的对应关系，每个键至多出现一次；同一值可以对应多个键。直接把编号当列表下标只适合编号范围小且稠密的情况。若编号很大或包含负数，就可以用 m 个桶，把键 k 放进 k 对 m 取余的桶。m 必须为正整数，本章所有键为整数，值为整数或 None；不支持任意字符串或可变对象作为键。

Python 在除数 m 为正时，余数位于 0 到 m−1。m=4 时，−3、1、5 都映射到 1；这是三个不同键发生冲突，不是覆盖同一键。无限多整数映射到有限桶时，不能指望完全避免冲突。查询时必须重复使用当前的映射规则，先定位桶，再核对原键。示例同时输出键和桶号，便于把负数余数与负下标区分开。

new\_table 返回一个固定字段记录：buckets 保存桶列表，size 保存实际键数。每轮 append 一个新的空列表，保证桶对象相互独立。每条记录用两个位置存放键和值。这里字典只承担两项元数据，真正按用户整数键寻找记录的过程由我们实现；这不是 Python dict 的内部模型。建空表需要 Θ(m) 时间与空间，不能因为还没有记录就写成常数。后文假定调用者不直接修改内部桶或已存键。

**完整程序**

```python
def bucket_index(key, capacity):
    return key % capacity

def new_table(capacity):
    buckets = []
    for i in range(capacity):
        buckets.append([])
    return {"buckets": buckets, "size": 0}

table = new_table(4)
for key in [-3, 1, 5, 6]:
    print(key, bucket_index(key, 4))
print(table)
```

**预期输出**

```text
-3 1
1 1
5 1
6 2
{'buckets': [[], [], [], []], 'size': 0}
```


选题关联：来源主题 1（文末列出）。

## 分离链接：在桶里确认原键

本章采用分离链接法：外层是桶数组，同一个桶容纳多条记录。这里桶的实现是 Python 列表；第 7 章的结点链表也能组织桶，算法分类不要求使用某一种内部表示。一次查询只检查选中的桶，其他桶可以跳过，因为每条记录都必须处在由自己的键算出的桶内。这就是查询正确性依赖的存储不变式。

entry\_index 顺序比较桶中记录的键，找到返回位置，否则返回 None。table\_get 再返回两个信息：是否存在，以及对应值。存在标记为真且值为 None，与存在标记为假且值为 None 意义不同。不能只用返回值是否为 None 判断命中，也不能把桶位置 0 当成未找到。因此代码使用明确的 None 判断，不依赖位置的真假值。

例子让 −3、1、5 同居桶 1，并给键 1 存 None。查 5 必须比较前三个键，查 9 也必须确认整个桶。若桶长为 L，最坏需要 L 次键比较，加上定位开销，时间 O(1+L)，工作区 O(1)。查到第一项时只比较一次；空桶零次。这里暂把整数取余和比较视作单位成本，若整数位数随输入增长，位运算成本还须单独计算。读取结果不会改变表的内容。

**完整程序**

```python
def bucket_index(key, capacity):
    return key % capacity

def new_table(capacity):
    buckets = []
    for i in range(capacity):
        buckets.append([])
    return {"buckets": buckets, "size": 0}

def entry_index(bucket, key):
    for i in range(len(bucket)):
        if bucket[i][0] == key:
            return i
    return None

def table_get(table, key):
    buckets = table["buckets"]
    bucket = buckets[bucket_index(key, len(buckets))]
    position = entry_index(bucket, key)
    if position is None:
        return [False, None]
    return [True, bucket[position][1]]

table = new_table(4)
table["buckets"][1] = [[-3, 8], [1, None], [5, 12]]
table["size"] = 3
print(table_get(table, 1))
print(table_get(table, 5))
print(table_get(table, 9))
```

**预期输出**

```text
[True, None]
[True, 12]
[False, None]
```


选题关联：来源主题 1（文末列出）。

## 写入与删除：键数只在结构变化时修改

写入同一键的新值叫覆盖，它只替换原记录的值，不新建第二条同键记录。table\_set 先定位并查桶，找到就覆盖并返回 False；只有缺失时才追加记录、增加 size 并返回 True。返回的布尔值表示是否新增，不表示操作成功与否。这个基础版本暂不自动扩容，后面会在它外面增加容量管理。

删除也先找原键，缺失时返回 False 并保持整份结构不变；找到后移除那条记录，键数减一。列表 pop(position) 会左移后面的记录，成本可能与桶长成正比。即使已经知道位置，也不能直接把列表中间删除说成常数。这里保留剩余记录在桶内的相对顺序，便于手工核对，但整个表不承诺键序或全局插入顺序。

示例把 2 和 5 放进容量为 3 的同一桶，再覆盖 2；键数仍为 2。删除 5 后只剩键 2，再删除 5 不应继续减数。正确性检查可分三步：每个键只出现一次，所在桶与当前容量一致，size 等于所有桶长度之和。查、写、删在不扩容时最坏都是 O(1+L)；列表末尾追加的分配成本采用摊还口径。键和值记录属于表内部，不向调用者提供可随意改键的句柄。

**完整程序**

```python
def bucket_index(key, capacity):
    return key % capacity

def new_table(capacity):
    buckets = []
    for i in range(capacity):
        buckets.append([])
    return {"buckets": buckets, "size": 0}

def entry_index(bucket, key):
    for i in range(len(bucket)):
        if bucket[i][0] == key:
            return i
    return None

def table_get(table, key):
    buckets = table["buckets"]
    bucket = buckets[bucket_index(key, len(buckets))]
    position = entry_index(bucket, key)
    if position is None:
        return [False, None]
    return [True, bucket[position][1]]

def table_set(table, key, value):
    buckets = table["buckets"]
    bucket = buckets[bucket_index(key, len(buckets))]
    position = entry_index(bucket, key)
    if position is not None:
        bucket[position][1] = value
        return False
    bucket.append([key, value])
    table["size"] = table["size"] + 1
    return True

def table_delete(table, key):
    buckets = table["buckets"]
    bucket = buckets[bucket_index(key, len(buckets))]
    position = entry_index(bucket, key)
    if position is None:
        return False
    bucket.pop(position)
    table["size"] = table["size"] - 1
    return True

table = new_table(3)
print(table_set(table, 2, 10), table_set(table, 5, 20))
print(table_set(table, 2, 30), table["size"])
print(table_delete(table, 5), table_delete(table, 5))
print(table)
```

**预期输出**

```text
True True
False 2
True False
{'buckets': [[], [], [[2, 30]]], 'size': 1}
```


选题关联：来源主题 1（文末列出）。

## 装载因子与重散列：搬家后地址要重算

令 n 为键数、m 为桶数，装载因子 α=n/m 是每桶平均记录数。它描述总体拥挤程度，不等于每个桶的长度。本章 hash\_put 调用基础写入后，只要 n 大于 m 就把容量加倍。它假定表从正容量新建，之后写入都走这个包装接口；删除不会缩容，覆盖已有键不会增加 n。这样正常写入结束后保持 α 不大于 1。

容量改变也改变取余结果，所以必须重新计算每条键的桶号。只在外层追加空桶会使一些旧记录无法按新规则找到。rehash 新建独立桶，然后按新容量直接追加现有记录。旧表已经保证键唯一，因此搬家时不必重新做查重；若调用普通插入逐条查桶，坏碰撞下本可线性的搬家也可能退化。程序复用内部键值记录，替换外层桶，size 不变，不复制值。

设旧容量为 m、新容量为 m′，一次重散列时间 Θ(m+m′+n)，新增桶和引用空间 O(m′+n)。倍增时为 O(m+n)，本次写入可能花线性时间。从固定初始容量出发连续新增，历次容量形成等比级数，搬家总成本可摊到各次新增。摊还是对一串操作的总成本分账，不是假设随机输入；它只约束扩容部分，不能消除桶扫描。删除后容量可能远大于当前键数，空间须按保留容量计算。示例扩到 4 后三个键仍同桶，提醒我们扩容不保证消灭冲突。

**完整程序**

```python
def bucket_index(key, capacity):
    return key % capacity

def new_table(capacity):
    buckets = []
    for i in range(capacity):
        buckets.append([])
    return {"buckets": buckets, "size": 0}

def entry_index(bucket, key):
    for i in range(len(bucket)):
        if bucket[i][0] == key:
            return i
    return None

def table_get(table, key):
    buckets = table["buckets"]
    bucket = buckets[bucket_index(key, len(buckets))]
    position = entry_index(bucket, key)
    if position is None:
        return [False, None]
    return [True, bucket[position][1]]

def table_set(table, key, value):
    buckets = table["buckets"]
    bucket = buckets[bucket_index(key, len(buckets))]
    position = entry_index(bucket, key)
    if position is not None:
        bucket[position][1] = value
        return False
    bucket.append([key, value])
    table["size"] = table["size"] + 1
    return True

def rehash(table, capacity):
    replacement = new_table(capacity)["buckets"]
    for bucket in table["buckets"]:
        for entry in bucket:
            index = bucket_index(entry[0], capacity)
            replacement[index].append(entry)
    table["buckets"] = replacement

def hash_put(table, key, value):
    added = table_set(table, key, value)
    if table["size"] > len(table["buckets"]):
        rehash(table, 2 * len(table["buckets"]))
    return added

table = new_table(2)
for key in [1, 5, 9]:
    hash_put(table, key, key + 10)
print(len(table["buckets"]), table["size"])
print(table["buckets"])
print(table_get(table, 5))
```

**预期输出**

```text
4 3
[[], [[1, 11], [5, 15], [9, 19]], [], []]
[True, 15]
```


选题关联：来源主题 1（文末列出）。

## 用实际比较次数区分期望与最坏

常见的哈希查询期望 O(1) 需要合适的散列分布与受控装载因子。更一般地，在适当均匀散列假设下可分析为期望 O(1+α)。本章固定使用取余，没有随机选择散列函数，不能对任意输入作这种保证。把所有键取成 m 的倍数就能使它们挤在桶 0，查询最后一项或同桶的缺失键需要 Θ(n) 次比较。

下面比较两个容量同为 8、键数同为 8 的表。分散表存 0 到 7，集中表存 0、8、16 直到 56，两者 α 都为 1。查询缺失键 64 时，两个表只在桶 0 的长度上不同，比较数分别为 1 和 8。hash\_probe 直接记录实际执行的键比较，不用秒表噪声推断渐近结论。若不断制造同桶的唯一键，连续新增的查重总次数可形成三角和，达到二次量级。

使用这种表前，应先决定是否需要按键排序、范围查询或最坏时间保证。哈希桶遍历不是排序；第 17 章搜索树的范围剪枝也不能直接迁移过来。演示程序没有实现随机散列、开放寻址或安全摘要，取余只是可核对的教学映射。后续应用即使写成单个外层循环，也要计入内部查询与写入：在分布假设下可以期望线性，按本实现的确定性最坏情况则可能二次。复杂度结论应说明自己采用哪一种口径。

**完整程序**

```python
def bucket_index(key, capacity):
    return key % capacity

def new_table(capacity):
    buckets = []
    for i in range(capacity):
        buckets.append([])
    return {"buckets": buckets, "size": 0}

def entry_index(bucket, key):
    for i in range(len(bucket)):
        if bucket[i][0] == key:
            return i
    return None

def table_get(table, key):
    buckets = table["buckets"]
    bucket = buckets[bucket_index(key, len(buckets))]
    position = entry_index(bucket, key)
    if position is None:
        return [False, None]
    return [True, bucket[position][1]]

def table_set(table, key, value):
    buckets = table["buckets"]
    bucket = buckets[bucket_index(key, len(buckets))]
    position = entry_index(bucket, key)
    if position is not None:
        bucket[position][1] = value
        return False
    bucket.append([key, value])
    table["size"] = table["size"] + 1
    return True

def hash_probe(table, key):
    buckets = table["buckets"]
    bucket = buckets[bucket_index(key, len(buckets))]
    comparisons = 0
    for entry in bucket:
        comparisons = comparisons + 1
        if entry[0] == key:
            return [True, comparisons]
    return [False, comparisons]

spread = new_table(8)
crowded = new_table(8)
for i in range(8):
    table_set(spread, i, i)
    table_set(crowded, i * 8, i)
print(hash_probe(spread, 64))
print(hash_probe(crowded, 64))
print(hash_probe(crowded, 56))
```

**预期输出**

```text
[False, 1]
[False, 8]
[True, 8]
```


选题关联：来源主题 1（文末列出）。

<a id="examples"></a>

## 跟着做：原创例题

### 例题 1

容量 4，依次写入 −3→10、1→None、5→20，把键 1 改成 7，再删除 −3。手算桶 1、键数及查询结果，解释 None 值为何不会破坏判断。

1. 三个键对 4 取余都是 1，按写入顺序进入同一桶，size 为 3。
2. 覆盖键 1 只改第二条记录的值，size 保持 3。
3. 删除 −3 移走桶首记录，其余记录前移，size 变为 2。
4. 查询 1 命中值 7，查询 −3 返回缺失标记；命中与值类型无关。

**结果与核对**

最后桶 1 为 \[\[1,7\],\[5,20\]\]，其他桶为空。覆盖返回 False 是没有新增，删除返回 True 是确实移除；它们不能混用同一种口头解释。用桶长度总和与键的余数反查最终结构，可同时发现漏减计数、误删同桶键和重复插入。

**完整程序**

```python
def bucket_index(key, capacity):
    return key % capacity

def new_table(capacity):
    buckets = []
    for i in range(capacity):
        buckets.append([])
    return {"buckets": buckets, "size": 0}

def entry_index(bucket, key):
    for i in range(len(bucket)):
        if bucket[i][0] == key:
            return i
    return None

def table_get(table, key):
    buckets = table["buckets"]
    bucket = buckets[bucket_index(key, len(buckets))]
    position = entry_index(bucket, key)
    if position is None:
        return [False, None]
    return [True, bucket[position][1]]

def table_set(table, key, value):
    buckets = table["buckets"]
    bucket = buckets[bucket_index(key, len(buckets))]
    position = entry_index(bucket, key)
    if position is not None:
        bucket[position][1] = value
        return False
    bucket.append([key, value])
    table["size"] = table["size"] + 1
    return True

def table_delete(table, key):
    buckets = table["buckets"]
    bucket = buckets[bucket_index(key, len(buckets))]
    position = entry_index(bucket, key)
    if position is None:
        return False
    bucket.pop(position)
    table["size"] = table["size"] - 1
    return True

table = new_table(4)
for pair in [[-3, 10], [1, None], [5, 20]]:
    table_set(table, pair[0], pair[1])
print(table_get(table, 1))
print(table_set(table, 1, 7), table_delete(table, -3))
print(table_get(table, 1), table_get(table, -3))
print(table)
```

**预期输出**

```text
[True, None]
False True
[True, 7] [False, None]
{'buckets': [[], [[1, 7], [5, 20]], [], []], 'size': 2}
```


### 例题 2

统计 \[4,−1,4,8,−1,4\] 中每个整数的频次，返回按首次出现次序排列的键与次数，不改变输入。

1. 表的键是读到的整数，值是已读前缀中的出现次数。
2. 缺失时写 1 并把键追加到 order；命中时加一，不重复记录次序。
3. 依次读完后，4 的次数为 3，−1 为 2，8 为 1。
4. 最后按 order 查询计数，避免把桶遍历次序误当输入次序。

**结果与核对**

结果为 \[\[4,3\],\[-1,2\],\[8,1\]\]。每次迭代后计数表精确代表已读前缀，因此扫描结束即可得到全表频次。若输入长 n、不同键 u，固定初始容量下存储 O(u+1)；分布假设下时间期望 O(n+1)，确定性最坏 O(n²+1)。空输入返回空列表。

**完整程序**

```python
def bucket_index(key, capacity):
    return key % capacity

def new_table(capacity):
    buckets = []
    for i in range(capacity):
        buckets.append([])
    return {"buckets": buckets, "size": 0}

def entry_index(bucket, key):
    for i in range(len(bucket)):
        if bucket[i][0] == key:
            return i
    return None

def table_get(table, key):
    buckets = table["buckets"]
    bucket = buckets[bucket_index(key, len(buckets))]
    position = entry_index(bucket, key)
    if position is None:
        return [False, None]
    return [True, bucket[position][1]]

def table_set(table, key, value):
    buckets = table["buckets"]
    bucket = buckets[bucket_index(key, len(buckets))]
    position = entry_index(bucket, key)
    if position is not None:
        bucket[position][1] = value
        return False
    bucket.append([key, value])
    table["size"] = table["size"] + 1
    return True

def rehash(table, capacity):
    replacement = new_table(capacity)["buckets"]
    for bucket in table["buckets"]:
        for entry in bucket:
            index = bucket_index(entry[0], capacity)
            replacement[index].append(entry)
    table["buckets"] = replacement

def hash_put(table, key, value):
    added = table_set(table, key, value)
    if table["size"] > len(table["buckets"]):
        rehash(table, 2 * len(table["buckets"]))
    return added

def frequency_pairs(values):
    table = new_table(2)
    order = []
    for value in values:
        found = table_get(table, value)
        if found[0]:
            hash_put(table, value, found[1] + 1)
        else:
            hash_put(table, value, 1)
            order.append(value)
    result = []
    for value in order:
        result.append([value, table_get(table, value)[1]])
    return result

values = [4, -1, 4, 8, -1, 4]
print(frequency_pairs(values))
print(values, frequency_pairs([]))
```

**预期输出**

```text
[[4, 3], [-1, 2], [8, 1]]
[4, -1, 4, 8, -1, 4] []
```


<a id="practice"></a>

## 自己做：先完成再看解答

### 练习 1

写 table\_profile，返回每桶长度、最长桶长度及总键数。容量 5，写入键 10、15、−5、1，各值为 0；再检查空表。函数不得修改表。

<details>
<summary>提示</summary>

逐桶读取长度，同时累加总量并更新当前最大值。不要把最大桶长当成平均装载因子。

</details>

<details>
<summary>解答与检查</summary>

桶长为 \[3,1,0,0,0\]，最长为 3，总量为 4；空表每桶均为零。扫描 m 个桶需 Θ(m) 时间，返回长度列表占 Θ(m) 空间，除此之外只需常数状态。总量应与 size 相等，可用来检查维护错误，但仅有这些数量还不能证明键唯一或桶号正确。

**完整程序**

```python
def bucket_index(key, capacity):
    return key % capacity

def new_table(capacity):
    buckets = []
    for i in range(capacity):
        buckets.append([])
    return {"buckets": buckets, "size": 0}

def entry_index(bucket, key):
    for i in range(len(bucket)):
        if bucket[i][0] == key:
            return i
    return None

def table_get(table, key):
    buckets = table["buckets"]
    bucket = buckets[bucket_index(key, len(buckets))]
    position = entry_index(bucket, key)
    if position is None:
        return [False, None]
    return [True, bucket[position][1]]

def table_set(table, key, value):
    buckets = table["buckets"]
    bucket = buckets[bucket_index(key, len(buckets))]
    position = entry_index(bucket, key)
    if position is not None:
        bucket[position][1] = value
        return False
    bucket.append([key, value])
    table["size"] = table["size"] + 1
    return True

def table_profile(table):
    lengths = []
    maximum = 0
    total = 0
    for bucket in table["buckets"]:
        length = len(bucket)
        lengths.append(length)
        total = total + length
        if length > maximum:
            maximum = length
    return {"lengths": lengths, "maximum": maximum, "total": total}

table = new_table(5)
for key in [10, 15, -5, 1]:
    table_set(table, key, 0)
print(table_profile(table))
print(table_profile(new_table(2)))
```

**预期输出**

```text
{'lengths': [3, 1, 0, 0, 0], 'maximum': 3, 'total': 4}
{'lengths': [0, 0], 'maximum': 0, 'total': 0}
```


</details>

### 练习 2

写 first\_repeat，返回扫描时第一个再次出现的整数，结果格式为 \[存在标记,键\]；没有重复返回 \[False,None\]。检查 \[−2,7,−2,7\]、\[1,2,3,2,1\] 和空表。

<details>
<summary>提示</summary>

读到当前值之前，表中只保存前面已经出现过的键。查到即返回，不需要先统计完整频次。

</details>

<details>
<summary>解答与检查</summary>

三个结果分别是 \[True,-2\]、\[True,2\] 和 \[False,None\]。这里选的是第二次出现位置最早的键，并非首次出现位置最早且最终会重复的键。发现前最多保存 u 个不同键，空间 O(u+1)；分布假设下期望时间 O(n+1)，最坏 O(n²+1)，提前返回时只读所需前缀。

**完整程序**

```python
def bucket_index(key, capacity):
    return key % capacity

def new_table(capacity):
    buckets = []
    for i in range(capacity):
        buckets.append([])
    return {"buckets": buckets, "size": 0}

def entry_index(bucket, key):
    for i in range(len(bucket)):
        if bucket[i][0] == key:
            return i
    return None

def table_get(table, key):
    buckets = table["buckets"]
    bucket = buckets[bucket_index(key, len(buckets))]
    position = entry_index(bucket, key)
    if position is None:
        return [False, None]
    return [True, bucket[position][1]]

def table_set(table, key, value):
    buckets = table["buckets"]
    bucket = buckets[bucket_index(key, len(buckets))]
    position = entry_index(bucket, key)
    if position is not None:
        bucket[position][1] = value
        return False
    bucket.append([key, value])
    table["size"] = table["size"] + 1
    return True

def rehash(table, capacity):
    replacement = new_table(capacity)["buckets"]
    for bucket in table["buckets"]:
        for entry in bucket:
            index = bucket_index(entry[0], capacity)
            replacement[index].append(entry)
    table["buckets"] = replacement

def hash_put(table, key, value):
    added = table_set(table, key, value)
    if table["size"] > len(table["buckets"]):
        rehash(table, 2 * len(table["buckets"]))
    return added

def first_repeat(values):
    table = new_table(2)
    for value in values:
        if table_get(table, value)[0]:
            return [True, value]
        hash_put(table, value, 1)
    return [False, None]

print(first_repeat([-2, 7, -2, 7]))
print(first_repeat([1, 2, 3, 2, 1]))
print(first_repeat([]))
```

**预期输出**

```text
[True, -2]
[True, 2]
[False, None]
```


</details>

### 练习 3

写 two\_sum\_indices(values,target)，返回两个不同位置 j、i，使 j 在 i 前且两值和为 target；优先最小的 i，再选最小的 j，无解返回 None。检查 \[6,2,6,4\] 与目标 10、\[3,3\] 与目标 6、\[3\] 与目标 6。

<details>
<summary>提示</summary>

当前位置 i 先查询补数 target−values\[i\]，再把当前值存入表。每个值只保留最早位置，覆盖会破坏第二条优先规则。

</details>

<details>
<summary>解答与检查</summary>

答案依次为 \[0,3\]、\[0,1\]、None。查询时表只包含严格早于 i 的位置，故不会把同一元素用两次；只在缺失时插入保证保存最早 j。外层从左到右首次命中保证最小 i。输入不变，空间 O(n+1)，在分布假设下期望线性，本取余实现最坏二次。可用独立的两层位置枚举验证优先规则。

**完整程序**

```python
def bucket_index(key, capacity):
    return key % capacity

def new_table(capacity):
    buckets = []
    for i in range(capacity):
        buckets.append([])
    return {"buckets": buckets, "size": 0}

def entry_index(bucket, key):
    for i in range(len(bucket)):
        if bucket[i][0] == key:
            return i
    return None

def table_get(table, key):
    buckets = table["buckets"]
    bucket = buckets[bucket_index(key, len(buckets))]
    position = entry_index(bucket, key)
    if position is None:
        return [False, None]
    return [True, bucket[position][1]]

def table_set(table, key, value):
    buckets = table["buckets"]
    bucket = buckets[bucket_index(key, len(buckets))]
    position = entry_index(bucket, key)
    if position is not None:
        bucket[position][1] = value
        return False
    bucket.append([key, value])
    table["size"] = table["size"] + 1
    return True

def rehash(table, capacity):
    replacement = new_table(capacity)["buckets"]
    for bucket in table["buckets"]:
        for entry in bucket:
            index = bucket_index(entry[0], capacity)
            replacement[index].append(entry)
    table["buckets"] = replacement

def hash_put(table, key, value):
    added = table_set(table, key, value)
    if table["size"] > len(table["buckets"]):
        rehash(table, 2 * len(table["buckets"]))
    return added

def two_sum_indices(values, target):
    earliest = new_table(2)
    for i in range(len(values)):
        other = table_get(earliest, target - values[i])
        if other[0]:
            return [other[1], i]
        if not table_get(earliest, values[i])[0]:
            hash_put(earliest, values[i], i)
    return None

print(two_sum_indices([6, 2, 6, 4], 10))
print(two_sum_indices([3, 3], 6))
print(two_sum_indices([3], 6))
```

**预期输出**

```text
[0, 3]
[0, 1]
None
```


</details>

<a id="pitfalls"></a>

## 容易混淆的地方

- **用桶号判断两个键相等，或用 None 值单独表示缺失。** 桶号只缩小候选范围，仍须比较原键；查询同时返回存在标记和值。
- **容量加倍后只增加空桶，不重新计算旧键位置。** 映射依赖当前容量，必须搬到新桶；搬家保持键数不变。
- **认为装载因子小就保证每次查询常数。** 平均桶长无法限制最长桶；固定取余可被同余键集中，最坏线性扫描。
- **把基础 table\_set 与自动扩容接口混用后，仍假定负载受控。** table\_set 只负责映射语义；需要容量策略时从新表开始统一使用 hash\_put。

<a id="self-check"></a>

## 离开这一章前

- [ ] 手算负整数键的非负桶号，再用实际输出核对。
- [ ] 覆盖、缺失删除和重散列后，逐键检查唯一性、位置与 size。
- [ ] 用同样键数构造均匀与集中两种分布，预测查询比较次数。
- [ ] 解释搬家摊还、桶扫描期望与单次最坏为什么是三个问题。
- [ ] 对两数配对举出一个会复用自身和一个会覆盖最早位置的反例。

## 本章边界

- 只实现整数键、整数或 None 值的教学映射，调用者保证正初始容量与内部结构完整。
- 未实现开放寻址、删除标记、随机散列、字符串散列或自动缩容；不复现 Python dict 内部布局。
- 整数算术按单位成本讨论，动态列表分配按摊还成本；大整数位复杂度另计。
- 无排序和稳定全局遍历顺序保证；安全摘要与密码存储不属于本章用途。

## 选题来源与覆盖

来源含学生报告时，仅将其作为选题线索；具体机制仍需结合后续实验或权威资料核对。

- [大一小学期/Week\_3-Python/docs/readme.md](https://github.com/PKUanonym/REKCARC-TSC-UHT/blob/37cd19f7a9fb80dc846a7016b3fd482ed5fe7cc0/%E5%A4%A7%E4%B8%80%E5%B0%8F%E5%AD%A6%E6%9C%9F/Week_3-Python/docs/readme.md)（已提取可读文本，固定版本 37cd19f7a9fb）
- 主题 1：Python 基础语法的外部学习入口；位置：第 41–80 行。
- 主题 2：从基础语法到工具与应用的建议阅读顺序；位置：第 121–160 行。

## 参考资料与规则核对

上游入口用于确定学习方向；下面的参考资料用于核对语言语义、数据结构或算法分析规则，例题和练习由本项目重新设计。

- [NIST DADS：散列函数](https://xlinux.nist.gov/dads/HTML/hash.html)：核对键映射到有限整数范围的定义；本章固定取余只作教学示范，不保证随机分布。
- [Open Data Structures：分离链接哈希表](https://opendatastructures.org/ods-python/5_1_ChainedHashTable_Hashin.html)：核对桶内查找、装载因子、扩容和分布假设。本章原创键值接口与取余实现没有采用书中的随机乘法散列，不能继承其期望保证。
- [Python 3.11：整数取余语义](https://docs.python.org/3.11/reference/expressions.html#binary-arithmetic-operations)：核对正除数下负整数键的非负余数；大整数位成本与单位操作模型另作区分。

**继续学习**：先独立完成自测，再记录仍需回读的步骤。

[上一章：让最值留在根部：二叉堆与优先队列](18-heaps.md) · [下一章：用顶点和边表达关系：图与存储表示](20-graphs.md)

[教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [哈希表与图练习指引](../hash-graphs-practice.md) · [拓扑排序与带权图练习指引](../weighted-graphs-practice.md) · [记录自己的学习](../learning-log-template.md)
