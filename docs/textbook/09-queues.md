# 先进入的先处理：队列与循环数组

[返回教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md)

[上一章：最后进入的先取出：栈与嵌套处理](08-stacks.md) · [下一章：数据变多会怎样：算法分析与增长量级](10-algorithm-analysis.md)

[学习目标](#objectives) · [需要的基础](#prerequisites) · [例题](#examples) · [练习](#practice) · [自测](#self-check)

状态：**AI 初稿，可开始试学**。生成模型：Codex 当前会话（未记录具体模型型号）。

本章围绕资料中识别到的知识点重新编写；讲解、数值模型、例题与练习为 AI 原创组织，不是原课程题目或答案。主题出处只说明选题关联，不证明全部推导已经正确。

栈让最近加入的项先离开，排队处理任务通常需要相反的规则：先来先处理。本章先用小例子区分先进先出与后进先出，再用固定容量列表手写循环队列。我们会分别记录队首位置和有效数量，让释放过的槽位能够再次使用，并明确规定队满时拒绝、队空时返回空结果。你将追踪物理槽位与逻辑顺序的差别，解释为什么队首与下一写入位置相同还不能单独判断空满，最后用队列完成一个简化的轮流服务任务。

<a id="objectives"></a>

## 学完要能做到

- 按先进先出规则追踪队首、队尾及实际取出顺序。
- 用固定容量列表、head 和 size 表示循环队列并说明各字段含义。
- 正确计算回绕位置，处理空、满与容量为 1 的情况。
- 保证失败入队和空出队保持全部状态不变，区分合法零值与空结果。
- 用队列实现轮流服务与批量取出，并解释为何顺序正确、循环会结束。

<a id="prerequisites"></a>

## 需要的基础

- 掌握数组的容量与有效长度、字典字段、函数和列表共享修改。
- 理解正整数取余；本章会说明它如何把位置限制在固定范围。
- 读过第 8 章栈及空操作约定，能够分清 LIFO 与 FIFO。

## 一、先进先出：先看接口，再选存储

队列按先进先出工作，常缩写为 FIFO。enqueue 在队尾加入新项，dequeue 从队首移除最早加入且尚未取出的项；peek 只看队首。顺序由加入时间决定，与元素数值大小无关，重复值也保留为独立项。下面 12 比 7 先进入，后来加入 9，下一次仍应取出 12。

用列表的 append 入队、pop(0) 出队，很容易观察这种行为。下面得到取出值 12，剩余 \[7, 9\]；若误用不带下标的 pop()，取出的会是最新的 9，那实现的是栈式顺序。队列接口不能靠“反正都是列表”来决定具体端点。

简单表示也有代价。在顺序存放的列表中，删除首项后，后面的引用需要前移，长队列反复 pop(0) 会反复搬动许多项。本章先保留这个小程序帮助理解接口，再换成不搬动有效元素的循环数组表示。程序语句短，并不说明其处理成本不随队长变化。

标准库 collections.deque 提供适合两端操作的容器，实际应用中经常可直接使用；本章为看清状态变化，手写固定容量版本。还要区分满时规则：带 maxlen 的 deque 在某些追加操作中会丢弃另一端旧项，而本章队列满时拒绝新项。它们不是同一个接口约定，不能拿一个的结果替另一个判对错。

**完整程序**

```python
queue = [12, 7]
queue.append(9)
served = queue.pop(0)
print(served, queue)
```

**预期输出**

```text
12 [7, 9]
```


选题关联：来源主题 1（文末列出）。

## 二、固定槽位、队首与有效数量

循环队列用一份字典保存三个字段。data 是底层槽位列表，创建后长度不再改变；head 是当前队首的物理下标；size 是有效元素个数。容量 C 就取 len(data)，因此不额外保存一个可能与列表长度不一致的容量字段。有效数量必须在 0 到 C 之间。

new\_queue 接收整数容量。正容量时，使用 \[None\] \* capacity 建立固定数量的占位槽；零或负容量返回 None，表示创建失败，调用者不能把这个结果再传给入队函数。这里重复的是不可变的 None 引用，不存在多份内部可变列表被意外共享的问题。

队列为空时 size 为 0；队列已满时 size 为 C。不能通过数一数 None 来决定长度：有效范围由 head 与 size 定义，槽位是否清空只是本章实现的可读性约定。本章存入整数，包括 0 和负数，None 留给空槽与空出队结果，不作为合法数据。

为了显示逻辑顺序，queue\_values 从偏移 0 遍历到 size 之前，第 offset 项的物理下标为 head 加 offset 后对 C 取余。正容量的余数在 0 到 C 减 1 之间，越过末槽就回到开头。空队列的循环执行零次，得到 \[\]。显示函数会遍历并新建列表，它的线性成本不代表入队出队也要遍历整队。

**完整程序**

```python
def new_queue(capacity):
    if capacity <= 0:
        return None
    return {"data": [None] * capacity, "head": 0, "size": 0}

def queue_values(queue):
    values = []
    capacity = len(queue["data"])
    for offset in range(queue["size"]):
        index = (queue["head"] + offset) % capacity
        values.append(queue["data"][index])
    return values

queue = new_queue(3)
print(queue["data"], queue["head"], queue["size"])
print(queue_values(queue))
print(new_queue(0))
```

**预期输出**

```text
[None, None, None] 0 0
[]
None
```


选题关联：来源主题 1（文末列出）。

## 三、入队：先判满，再计算尾部空位

当前有 size 项，队首在 head，那么下一项应写入的物理位置是 head 加 size 后对容量取余。它不是每次都写在底层列表末尾，也不是读取最后一个非空槽再猜位置。只要状态合法且尚未满，这个位置就紧接当前逻辑队尾，并且没有占用仍有效的项。

enqueue 必须先检查 size 是否等于容量。若已满，返回 False，data、head、size 全部保持不变；不能先写入再判断，否则可能覆盖最早等待的元素。未满时才计算位置、写入新值，把 size 增加 1，返回 True。入队不会移动 head。

下面容量为 3，初始 head 为 0。依次加入 4、8、6 时，写入位置分别为 0、1、2，有效数量从 0 增到 3。再加入 10 会在满检查处拒绝，逻辑顺序仍是 \[4, 8, 6\]，不会默默把 4 丢掉。返回值与状态变化要分别核对：True 时应多一项，False 时应完全不变。

本章的函数都接收同一个队列字典，并通过字段更新修改共享对象；不需要返回整个队列让调用者替换。返回的布尔值只报告是否接受了新项。容量在创建后固定，操作过程中不调用 append 扩容，也不会靠整体移动元素找空位，所以成功入队只涉及常数次字段和槽位访问。

**完整程序**

```python
def new_queue(capacity):
    if capacity <= 0:
        return None
    return {"data": [None] * capacity, "head": 0, "size": 0}

def queue_values(queue):
    values = []
    capacity = len(queue["data"])
    for offset in range(queue["size"]):
        index = (queue["head"] + offset) % capacity
        values.append(queue["data"][index])
    return values

def enqueue(queue, value):
    capacity = len(queue["data"])
    if queue["size"] == capacity:
        return False
    index = (queue["head"] + queue["size"]) % capacity
    queue["data"][index] = value
    queue["size"] = queue["size"] + 1
    return True

queue = new_queue(3)
for value in [4, 8, 6]:
    enqueue(queue, value)
print(queue_values(queue))
print(enqueue(queue, 10), queue_values(queue))
```

**预期输出**

```text
[4, 8, 6]
False [4, 8, 6]
```


选题关联：来源主题 1（文末列出）。

## 四、出队：移动队首，不搬后面的项

dequeue 先检查 size。若为 0，就返回 None，不改变队首或槽位。非空时，从 data\[head\] 保存将要返回的值，把这个槽清为 None，再把 head 向前推进一格并取余，最后把 size 减少 1。保存值必须发生在清槽之前，否则原值已经被覆盖。

这个过程没有把其他有效元素向左搬动。取出后，逻辑队首改由新的 head 指向；物理列表可能开头出现空槽，但这不影响剩余元素按原加入顺序等待。以后入队会通过取余再次使用那些已经释放的槽位，不能把出现过的下标当成永久用完了。

下面容量 3，先加入 4、8。第一次出队返回 4，head 从 0 变 1，size 从 2 变 1，逻辑内容只剩 8。第二次返回 8，head 变 2，size 变 0；第三次出队返回 None，head 仍为 2。空队列的 head 不必归零，只要保持合法下标即可；下一次入队会从这个位置重新开始。

若出队结果为 0，它仍是成功取出的整数，不能用真假判断误认为队空。应看结果是否为 None，或在操作前按 size 判断。本章清槽有助于显示空位和解除旧数据引用，但空满判断始终看 size。初始建表需 C 个槽位，之后一次入队或出队不遍历 C 个槽位。

**完整程序**

```python
def new_queue(capacity):
    if capacity <= 0:
        return None
    return {"data": [None] * capacity, "head": 0, "size": 0}

def queue_values(queue):
    values = []
    capacity = len(queue["data"])
    for offset in range(queue["size"]):
        index = (queue["head"] + offset) % capacity
        values.append(queue["data"][index])
    return values

def enqueue(queue, value):
    capacity = len(queue["data"])
    if queue["size"] == capacity:
        return False
    index = (queue["head"] + queue["size"]) % capacity
    queue["data"][index] = value
    queue["size"] = queue["size"] + 1
    return True

def dequeue(queue):
    if queue["size"] == 0:
        return None
    index = queue["head"]
    value = queue["data"][index]
    queue["data"][index] = None
    queue["head"] = (index + 1) % len(queue["data"])
    queue["size"] = queue["size"] - 1
    return value

queue = new_queue(3)
enqueue(queue, 4)
enqueue(queue, 8)
first = dequeue(queue)
print(first, queue_values(queue), queue["head"], queue["size"])
second = dequeue(queue)
third = dequeue(queue)
print(second, third, queue["head"], queue["size"])
```

**预期输出**

```text
4 [8] 1 1
8 None 2 0
```


选题关联：来源主题 1（文末列出）。

## 五、回绕与不变式：物理顺序不等于排队顺序

容量为 4 时，物理下标只有 0、1、2、3。若 head 为 2、size 为 3，逻辑元素依次位于 2、3、0；下一写入位置是 1。取余把越界的计数折回合法下标，既保留先后关系，也让开头的空位再次参与使用。不要直接从 data 的第 0 项开始打印就认为那是队首。

下面先入队 11、22、33，再出队两次，剩余 33 位于下标 2。加入 44 时写到 3，加入 55 时回绕到 0。物理槽位变为 \[55, None, 33, 44\]，但逻辑队列是 \[33, 44, 55\]。从 head 开始按 size 取出三项，才能得到真正的等待顺序。

始终保持三项关系：head 在合法下标范围，size 在 0 到容量之间，逻辑第 k 项位于 head 加 k 后取余的位置。成功入队只在有效区间末尾增加一项；成功出队只去掉首项并缩短区间。失败操作完全不改这些状态，所以不会破坏之前等待的顺序。

下一写入位置等于 head 时，可能是 size 为 0 的空队列，也可能是 size 等于 C 的满队列。因此本实现保留 size 区分两者，能够使用全部 C 个槽；不要再混入“额外空出一个槽”的另一种循环队列设计。特别检查容量为 1 时，所有取余下标都为 0，依然必须靠 size 判断能否操作。

**完整程序**

```python
def new_queue(capacity):
    if capacity <= 0:
        return None
    return {"data": [None] * capacity, "head": 0, "size": 0}

def queue_values(queue):
    values = []
    capacity = len(queue["data"])
    for offset in range(queue["size"]):
        index = (queue["head"] + offset) % capacity
        values.append(queue["data"][index])
    return values

def enqueue(queue, value):
    capacity = len(queue["data"])
    if queue["size"] == capacity:
        return False
    index = (queue["head"] + queue["size"]) % capacity
    queue["data"][index] = value
    queue["size"] = queue["size"] + 1
    return True

def dequeue(queue):
    if queue["size"] == 0:
        return None
    index = queue["head"]
    value = queue["data"][index]
    queue["data"][index] = None
    queue["head"] = (index + 1) % len(queue["data"])
    queue["size"] = queue["size"] - 1
    return value

queue = new_queue(4)
for value in [11, 22, 33]:
    enqueue(queue, value)
dequeue(queue)
dequeue(queue)
enqueue(queue, 44)
enqueue(queue, 55)
print(queue["data"], queue["head"], queue["size"])
print(queue_values(queue))
```

**预期输出**

```text
[55, None, 33, 44] 2 3
[33, 44, 55]
```


选题关联：来源主题 1（文末列出）。

<a id="examples"></a>

## 跟着做：原创例题

### 例题 1

创建容量为 3 的循环队列，依次入队 7、1、9，尝试入队 5，然后出队一次，再入队 5，最后全部取出。列出拒绝操作、回绕后的物理槽位与逻辑内容，以及最终 head 和 size。

1. 前三次写入下标 0、1、2，head 为 0、size 为 3，队列已满。
2. 第一次尝试入队 5 被拒绝，返回 False，全部槽位和两个状态字段保持。
3. 出队返回 7，清空下标 0，head 改为 1、size 改为 2。
4. 再入队 5 时，写入位置为 1 加 2 对 3 取余，得到 0；物理内容为 5、1、9。
5. 逻辑顺序从下标 1 开始，所以是 1、9、5。逐个取出后 head 绕一整圈回到 1，size 为 0。

**结果与核对**

拒绝入队返回 False，第一次出队为 7，第二次入队 5 成功。随后取出序列为 \[1, 9, 5\]；最终 head 为 1、size 为 0，逻辑内容为空。末尾写入位置与 head 相同既可能空也可能满，size 消除了歧义。

**完整程序**

```python
def new_queue(capacity):
    if capacity <= 0:
        return None
    return {"data": [None] * capacity, "head": 0, "size": 0}

def queue_values(queue):
    values = []
    capacity = len(queue["data"])
    for offset in range(queue["size"]):
        index = (queue["head"] + offset) % capacity
        values.append(queue["data"][index])
    return values

def enqueue(queue, value):
    capacity = len(queue["data"])
    if queue["size"] == capacity:
        return False
    index = (queue["head"] + queue["size"]) % capacity
    queue["data"][index] = value
    queue["size"] = queue["size"] + 1
    return True

def dequeue(queue):
    if queue["size"] == 0:
        return None
    index = queue["head"]
    value = queue["data"][index]
    queue["data"][index] = None
    queue["head"] = (index + 1) % len(queue["data"])
    queue["size"] = queue["size"] - 1
    return value

queue = new_queue(3)
for value in [7, 1, 9]:
    enqueue(queue, value)
print(enqueue(queue, 5))
print(dequeue(queue))
print(enqueue(queue, 5))
print(queue["data"], queue_values(queue))
removed = []
while queue["size"] > 0:
    removed.append(dequeue(queue))
print(removed, queue["head"], queue["size"])
```

**预期输出**

```text
False
7
True
[5, 1, 9] [1, 9, 5]
[1, 9, 5] 1 0
```


### 例题 2

三个简化任务按剩余工作量 \[2, 1, 3\] 排队，每次取队首，执行一个单位；仍有剩余则放回队尾，否则完成。用队列记录每次取出的剩余量及完成发生在第几步，不要求任务名称。输入工作量均为正整数；空任务列表也应正常结束。

1. 创建容量为任务个数的队列，空任务列表则用容量 1。初始按 2、1、3 入队。
2. 第 1 步取出 2，做完后剩 1，回到尾部，队列变为 1、3、1。
3. 第 2 步取出 1 后完成；第 3 步取出 3，剩 2 回队尾，此时为 1、2。
4. 第 4 步取出 1 完成；第 5 步取出 2，剩 1 回队尾；第 6 步取出 1 完成。
5. 每次最多把刚取出的一项重新放回，所以先出队留下的空位足够；每步总剩余工作量减少 1，最终清空。
6. 函数把取出记录和完成步号放入带 served、finished 字段的字典返回；这两个字段保存列表，不是同一个计数。

**结果与核对**

取出时的剩余量依次为 \[2, 1, 3, 1, 2, 1\]，完成步号为 \[2, 4, 6\]。共服务 6 次，等于初始工作量 2+1+3。队列轮流处理而非一次耗尽首任务；空输入返回两份空记录。

**完整程序**

```python
def new_queue(capacity):
    if capacity <= 0:
        return None
    return {"data": [None] * capacity, "head": 0, "size": 0}

def queue_values(queue):
    values = []
    capacity = len(queue["data"])
    for offset in range(queue["size"]):
        index = (queue["head"] + offset) % capacity
        values.append(queue["data"][index])
    return values

def enqueue(queue, value):
    capacity = len(queue["data"])
    if queue["size"] == capacity:
        return False
    index = (queue["head"] + queue["size"]) % capacity
    queue["data"][index] = value
    queue["size"] = queue["size"] + 1
    return True

def dequeue(queue):
    if queue["size"] == 0:
        return None
    index = queue["head"]
    value = queue["data"][index]
    queue["data"][index] = None
    queue["head"] = (index + 1) % len(queue["data"])
    queue["size"] = queue["size"] - 1
    return value

def service_trace(jobs):
    capacity = len(jobs)
    if capacity == 0:
        capacity = 1
    queue = new_queue(capacity)
    for work in jobs:
        enqueue(queue, work)
    served = []
    finished = []
    steps = 0
    while queue["size"] > 0:
        work = dequeue(queue)
        served.append(work)
        steps = steps + 1
        if work > 1:
            enqueue(queue, work - 1)
        else:
            finished.append(steps)
    return {"served": served, "finished": finished}

trace = service_trace([2, 1, 3])
print(trace["served"])
print(trace["finished"])
```

**预期输出**

```text
[2, 1, 3, 1, 2, 1]
[2, 4, 6]
```


<a id="practice"></a>

## 自己做：先完成再看解答

### 练习 1

为循环队列编写 peek\_queue(queue)：非空时返回队首整数且完全不改变状态，空时返回 None。容量 2，加入 0、7，分别在初始、出队一次、再出队一次后查看队首与 size。

<details>
<summary>提示</summary>

队首物理位置由 head 给出，不一定是下标 0。先检查 size，再读取对应槽；不要推进 head。

</details>

<details>
<summary>解答与检查</summary>

三次查看结果与数量分别为 0 和 2、7 和 1、None 和 0。第一次的 0 是合法值；只有随后真正调用 dequeue 才减少数量。peek 不清槽、不更新 head，也不更新 size。

**完整程序**

```python
def new_queue(capacity):
    if capacity <= 0:
        return None
    return {"data": [None] * capacity, "head": 0, "size": 0}

def queue_values(queue):
    values = []
    capacity = len(queue["data"])
    for offset in range(queue["size"]):
        index = (queue["head"] + offset) % capacity
        values.append(queue["data"][index])
    return values

def enqueue(queue, value):
    capacity = len(queue["data"])
    if queue["size"] == capacity:
        return False
    index = (queue["head"] + queue["size"]) % capacity
    queue["data"][index] = value
    queue["size"] = queue["size"] + 1
    return True

def dequeue(queue):
    if queue["size"] == 0:
        return None
    index = queue["head"]
    value = queue["data"][index]
    queue["data"][index] = None
    queue["head"] = (index + 1) % len(queue["data"])
    queue["size"] = queue["size"] - 1
    return value

def peek_queue(queue):
    if queue["size"] == 0:
        return None
    return queue["data"][queue["head"]]

queue = new_queue(2)
enqueue(queue, 0)
enqueue(queue, 7)
print(peek_queue(queue), queue["size"])
dequeue(queue)
print(peek_queue(queue), queue["size"])
dequeue(queue)
print(peek_queue(queue), queue["size"])
```

**预期输出**

```text
0 2
7 1
None 0
```


</details>

### 练习 2

容量为 2，依次入队 3、6，出队一次，入队 9，尝试入队 12，再出队两次，最后入队 12。先手算所有取出值、被拒绝的操作及最终物理槽位、head、size、逻辑顺序，再写完整程序核对。

<details>
<summary>提示</summary>

每一步同时记两个视图：按下标排列的底层槽，以及从 head 开始的有效内容。队满失败时两个视图都不改变。

</details>

<details>
<summary>解答与检查</summary>

第一次 12 被拒绝。取出值依次为 3、6、9；取尽时 head 为 1，最后把 12 写到下标 1。最终底层为 \[None, 12\]，head 为 1、size 为 1，逻辑内容为 \[12\]。不能看到下标 0 为空就误以为队列为空。

**完整程序**

```python
def new_queue(capacity):
    if capacity <= 0:
        return None
    return {"data": [None] * capacity, "head": 0, "size": 0}

def queue_values(queue):
    values = []
    capacity = len(queue["data"])
    for offset in range(queue["size"]):
        index = (queue["head"] + offset) % capacity
        values.append(queue["data"][index])
    return values

def enqueue(queue, value):
    capacity = len(queue["data"])
    if queue["size"] == capacity:
        return False
    index = (queue["head"] + queue["size"]) % capacity
    queue["data"][index] = value
    queue["size"] = queue["size"] + 1
    return True

def dequeue(queue):
    if queue["size"] == 0:
        return None
    index = queue["head"]
    value = queue["data"][index]
    queue["data"][index] = None
    queue["head"] = (index + 1) % len(queue["data"])
    queue["size"] = queue["size"] - 1
    return value

queue = new_queue(2)
enqueue(queue, 3)
enqueue(queue, 6)
removed = [dequeue(queue)]
enqueue(queue, 9)
print(enqueue(queue, 12))
removed.append(dequeue(queue))
removed.append(dequeue(queue))
enqueue(queue, 12)
print(removed)
print(queue["data"], queue["head"], queue["size"], queue_values(queue))
```

**预期输出**

```text
False
[3, 6, 9]
[None, 12] 1 1 [12]
```


</details>

### 练习 3

编写 take\_from\_queue(queue, limit)，最多取出 limit 项，按 FIFO 顺序返回列表；limit 为非负整数，不足时取尽即可。容量 3，加入 \[5, 0, 8\]，依次取 2 项、0 项、5 项，并输出每次剩余内容。

<details>
<summary>提示</summary>

循环同时检查结果数量未达 limit 和队列非空，不根据取出值的真假决定是否继续。

</details>

<details>
<summary>解答与检查</summary>

三次返回分别为 \[5, 0\]、\[\]、\[8\]；剩余内容分别为 \[8\]、\[8\]、\[\]。零是合法队列元素，必须出现在第一次结果中。limit 为 0 时不改变状态，超过当前长度时也不会多做空出队。

**完整程序**

```python
def new_queue(capacity):
    if capacity <= 0:
        return None
    return {"data": [None] * capacity, "head": 0, "size": 0}

def queue_values(queue):
    values = []
    capacity = len(queue["data"])
    for offset in range(queue["size"]):
        index = (queue["head"] + offset) % capacity
        values.append(queue["data"][index])
    return values

def enqueue(queue, value):
    capacity = len(queue["data"])
    if queue["size"] == capacity:
        return False
    index = (queue["head"] + queue["size"]) % capacity
    queue["data"][index] = value
    queue["size"] = queue["size"] + 1
    return True

def dequeue(queue):
    if queue["size"] == 0:
        return None
    index = queue["head"]
    value = queue["data"][index]
    queue["data"][index] = None
    queue["head"] = (index + 1) % len(queue["data"])
    queue["size"] = queue["size"] - 1
    return value

def take_from_queue(queue, limit):
    result = []
    while len(result) < limit and queue["size"] > 0:
        result.append(dequeue(queue))
    return result

queue = new_queue(3)
for value in [5, 0, 8]:
    enqueue(queue, value)
print(take_from_queue(queue, 2), queue_values(queue))
print(take_from_queue(queue, 0), queue_values(queue))
print(take_from_queue(queue, 5), queue_values(queue))
```

**预期输出**

```text
[5, 0] [8]
[] [8]
[8] []
```


</details>

<a id="pitfalls"></a>

## 容易混淆的地方

- **直接读取底层下标 0 当成队首，忽略已经发生回绕。** 逻辑顺序始终从 head 出发，按 size 项逐个取余；物理列表的打印顺序只是槽位顺序。
- **只比较队首和下一写入位置，无法区分空与满。** 本实现保留 size，并使用全部容量；空看 size 为 0，满看 size 等于容量。
- **队满时先写入再判断，或者空出队仍推进 head。** 先检查能否操作，失败分支立即返回，保证底层数据与所有状态字段完全不变。
- **用出队结果的真假判断成功，或把标准库有界 deque 当成同一满队规则。** 整数 0 仍有效，空标记为 None；本实现满时拒绝，不能套用自动丢弃旧项的规则。

<a id="self-check"></a>

## 离开这一章前

- [ ] 用同一输入顺序分别模拟栈与队列，解释下一次取出的值为何不同。
- [ ] 画出容量 4、head 为 2、size 为 3 时每个逻辑位置对应的物理下标。
- [ ] 完整验证容量 1 的空出队、满入队失败、出空和再次入队。
- [ ] 对容量 2 连续运行多轮入队出队，检查值顺序、长度与失败时全部状态。
- [ ] 独立完成轮流服务例题，说明为何不超容量、总剩余量为何每步减少并最终结束。

## 本章边界

- 容量参数要求整数，非正值创建失败；其余函数只接收成功创建且字段保持合法的队列对象。
- 队列只存整数，None 表示空槽和空结果；本实现满时拒绝、不扩容、不自动覆盖。
- 不实现线程同步、阻塞等待、优先队列或持久化；轮流服务只是有限正整数任务的教学模型。
- 入队出队的常数操作数不包含初始建表和显示整个队列的成本；不在本章讨论缓存与并发性能。

## 选题来源与覆盖

来源含学生报告时，仅将其作为选题线索；具体机制仍需结合后续实验或权威资料核对。

- [大一小学期/Week\_3-Python/docs/readme.md](https://github.com/PKUanonym/REKCARC-TSC-UHT/blob/37cd19f7a9fb80dc846a7016b3fd482ed5fe7cc0/%E5%A4%A7%E4%B8%80%E5%B0%8F%E5%AD%A6%E6%9C%9F/Week_3-Python/docs/readme.md)（已提取可读文本，固定版本 37cd19f7a9fb）
- 主题 1：Python 基础语法的外部学习入口；位置：第 41–80 行。
- 主题 2：从基础语法到工具与应用的建议阅读顺序；位置：第 121–160 行。

## 参考资料与规则核对

上游入口用于确定学习方向；下面的参考资料用于核对语言语义、数据结构或算法分析规则，例题和练习由本项目重新设计。

- [Python 3.11：列表作为队列](https://docs.python.org/3.11/tutorial/datastructures.html#using-lists-as-queues)：核对 FIFO 及列表头部操作的搬移代价。
- [Python 3.11：collections.deque](https://docs.python.org/3.11/library/collections.html#collections.deque)：核对双端容器与 maxlen 的丢弃规则，明确它不同于本章满时拒绝的契约。
- [Open Data Structures：数组队列](https://opendatastructures.org/newhtml/ods/latex/arrays.html)：核对循环下标与逻辑区间；本章固定容量且拒绝满队列，不采用书中的动态扩容接口。

**继续学习**：先独立完成自测，再记录仍需回读的步骤。

[上一章：最后进入的先取出：栈与嵌套处理](08-stacks.md) · [下一章：数据变多会怎样：算法分析与增长量级](10-algorithm-analysis.md)

[教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [记录自己的学习](../learning-log-template.md)
