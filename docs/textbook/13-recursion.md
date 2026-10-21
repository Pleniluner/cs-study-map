# 函数怎样调用自己：递归、返回与调用栈

[返回教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md)

[上一章：怎样把数据排成顺序：选择、插入与归并排序](12-sorting.md) · [下一章：把问题分小再合起来：分治与递归归并](14-divide-and-conquer.md)

[学习目标](#objectives) · [需要的基础](#prerequisites) · [例题](#examples) · [练习](#practice) · [自测](#self-check)

状态：**AI 初稿，可开始试学**。生成模型：Codex 当前会话（未记录具体模型型号）。

本章围绕资料中识别到的知识点重新编写；讲解、数值模型、例题与练习为 AI 原创组织，不是原课程题目或答案。主题出处只说明选题关联，不证明全部推导已经正确。

第 5 章把计算组织成函数，第 8 章用栈处理后进先出的任务。现在把两者接起来：一个函数可以把较小的问题交给自己，等待答案回来后继续完成当前工作。递归的关键不是反复写同一个名字，而是明确函数承诺、直接解决的最小情况，以及每次调用怎样接近它。本章先追踪单条调用链，再观察分支调用的重复工作。我们会分别数全部调用和同时未返回的调用，避免把几行短代码误认为时间或空间很少。

<a id="objectives"></a>

## 学完要能做到

- 写清递归函数的输入约定、返回结果、基例与严格缩小的量。
- 按进入与返回两种顺序追踪局部参数和中间结果。
- 用下标处理同一列表，区分共享对象与每次调用的局部名字。
- 区分总调用数、最大栈深及输出记录的额外空间。
- 比较递归和循环，识别重复子问题与解释器深度限制。

<a id="prerequisites"></a>

## 需要的基础

- 掌握函数、return、局部名字、列表和栈，以及第 10 章的计数口径。
- 使用 Python 3.11+；计数参数和数位题只接受非负整数，列表题只读整数列表。
- 示例采用小规模输入和单位整数运算模型；数学上的可终止不保证任意规模都能在解释器内运行。

## 一、先写基例，再证明问题会变小

递归是函数直接或间接调用自身。本章先只用直接调用：countdown(n) 的约定是依次打印 n 到 1，再打印 stop，输入 n 为非负整数。n 等于 0 时不用求助更小的问题，可以立刻结束，这个直接解决的情况叫基例。基例也属于函数行为，不能只写一句“到这里停止”却漏掉约定的输出。

当 n 大于 0，先打印当前 n，再调用 countdown(n-1)。这次调用仍满足非负整数的前提，且参数严格少一。非负整数不可能无限严格下降，因此一定会到达 0。证明终止要同时具备有下界的量和每次调用的严格进展，只有一个看起来像停止条件的 if 还不够。

例如输入 3，进入各次调用时参数依次是 3、2、1、0。新的调用有自己的局部参数，不会把外层那份 n 直接改成零。最内层结束后控制权逐层回到调用处；本程序在递归调用后没有其他打印，于是依次返回，屏幕上不会自动再出现 1、2、3。

若递归时仍传入 n，永远到不了基例；若把负数交给这段只减一的程序，也不会走向零。本章通过输入约定排除这种用法，不把无限递归当作学习实验去运行。写程序前先用一句话说明“这次调用解决什么”，再检查所有分支都遵守同一承诺。

**完整程序**

```python
def countdown(n):
    if n == 0:
        print("stop")
        return
    print(n)
    countdown(n - 1)

countdown(3)
```

**预期输出**

```text
3
2
1
stop
```


选题关联：来源主题 1（文末列出）。

## 二、调用在等什么，返回就交回什么

用 factorial(n) 表示从 1 到 n 的整数乘积，约定 factorial(0) 为 1。n 大于 0 时，较小问题负责算到 n-1 的乘积，当前调用只需再乘 n。这个约定既给出基例，也说明如何从较小问题的正确答案得到当前答案；不能仅凭跑通一个输入就替代这层推理。

算 factorial(4) 时，外层保留 n=4，并等待 factorial(3) 的结果，后者又等待 factorial(2)。一直到 n=0 返回 1，才依次得到 1、2、6、24。调用向较小参数深入，结果沿相反方向返回；不是先把所有乘法都完成，再开始处理基例。

可以把每个尚未返回的调用看成一张工作卡，保存本次参数、局部名字和回来后要继续的位置。后放入的工作卡先完成，正是栈的顺序。这里是理解调用的模型，不是在声明 Python 栈帧的具体字节布局。不同卡上都叫 n、smaller 的名字，分别属于各自调用。

本实现对非负 n 调用 n+1 次，做 n 次乘法，同时最多保留 n+1 张这样的卡；因此单位运算模型下，时间和调用栈空间均为 Θ(n+1)。虽然正文只有几行，空间也不是 O(1)。实际大整数会越来越长，若讨论精确耗时与字节数，还需把数值位数纳入分析。

**完整程序**

```python
def factorial(n):
    if n == 0:
        return 1
    smaller = factorial(n - 1)
    return n * smaller

print(factorial(0), factorial(4))
```

**预期输出**

```text
1 24
```


选题关联：来源主题 1（文末列出）。

## 三、用位置表示剩余问题，接住子调用的结果

列表求和也能递归。sum\_from(values, index) 的承诺是返回从 index 到末尾的和，允许 index 等于长度，此时后缀为空，和为 0。否则先求下一位置开始的后缀和，再加当前项。外层 recursive\_sum 从 0 开始调用，空列表直接命中同一个基例，无需另造一套流程。

虽然 index 每次增加，但真正需要严格减少的量是剩余长度，也就是 len(values) 减 index。对合法的 0 到 n 之间的起点，每次少一个未处理位置，因此最多经过 n-index 次扩展就停止。递归的进展不一定表现为参数数字变小，必须选对衡量工作规模的量。

每一层把子调用的返回值存进 suffix，再返回当前项加 suffix。只调用子函数而忘记 return 或组合结果，会让上层拿到 None；在最内层打印一个正确数，也不等于把它返回给调用者。输入 \[-3, 5, 0, 2\] 的后缀从空后缀的和 0 开始，逐层得到 2、2、7、4。

各层共享同一个列表，但只读取，输入保持不变；各层的 index 和 suffix 则是局部状态。这里传下标，不反复建立 values\[1:\] 的切片副本，所以不会引入逐层复制的额外工作。即使没有复制，长度 n 的调用链仍需 Θ(n+1) 栈空间；共享输入不等于调用没有开销。

**完整程序**

```python
def sum_from(values, index):
    if index == len(values):
        return 0
    suffix = sum_from(values, index + 1)
    return values[index] + suffix

def recursive_sum(values):
    return sum_from(values, 0)

values = [-3, 5, 0, 2]
print(recursive_sum(values), values)
print(recursive_sum([]))
```

**预期输出**

```text
4 [-3, 5, 0, 2]
0
```


选题关联：来源主题 1（文末列出）。

## 四、能终止，还要放得下调用栈

解释器能保留的调用深度有限。一个函数在数学上会终止，仍可能在到达基例之前触及递归深度限制，出现 RecursionError。这个限制与解释器设置、外围调用等因素有关，不能把某个常见数字当成所有环境统一可用的层数，也不能用改大限制替代算法分析。

列表求和有很直接的循环版本：保留 total，每次加一个值，最后返回。它与递归版本处理同一批元素，采用相同的输入和返回约定；在本章小整数范围内答案相同。循环没有逐项累积尚未返回的函数调用，除结果整数外只维护固定数量状态，辅助空间为 O(1)。

递归能直接表达嵌套定义和分支结构，下一章的分治就会用到它；单条长链如果能用简单循环表达，循环通常更适合作为这里的实际实现。选择方式时，先比较清晰度、工作量与最大同时存活状态，而不是把“用了递归”当作更高级的标签。

下面用同一份列表分别调用两种版本，输出应相等，空输入也都返回 0。程序不提高递归限制，只用小样例核对语义。后续测试会探测实际调用深度与输入是否改变，而不是只看最后打印的数字；这种验证能发现把线性栈空间误说成常数的解释错误。

**完整程序**

```python
def sum_from(values, index):
    if index == len(values):
        return 0
    suffix = sum_from(values, index + 1)
    return values[index] + suffix

def recursive_sum(values):
    return sum_from(values, 0)

def iterative_sum(values):
    total = 0
    for value in values:
        total = total + value
    return total

values = [4, -1, 6]
print(recursive_sum(values), iterative_sum(values))
print(recursive_sum([]), iterative_sum([]))
```

**预期输出**

```text
9 9
0 0
```


选题关联：来源主题 1（文末列出）。

## 五、分支调用不等于同时保留整棵树

看一个会重复计算的定义：fib(0)=0、fib(1)=1，其他非负 n 的结果为前两项之和。下面的报告函数每次进入都算一次调用，两个基例分别返回自己的值和调用数 1；其他情况把两边的值相加，把两边调用数相加后再加当前这一次。

例如 n=4 的值是 3，总调用数是 9；n=6 的值是 8，总调用数已经到 25。fib(6) 需要 fib(5) 和 fib(4)，而 fib(5) 又会重新求 fib(4)。相同参数没有自动复用之前的结果，代码中只出现两个递归语句，不代表总共只调用两次，也不能据此宣称线性工作。

这段程序先完成左边，再开始右边，两边不会自动同时运行。求左边时，右边尚未展开；求右边时，左边只留下一个固定字段的结果。因此整棵调用树用来数总工作，一条尚未返回的路径用来数峰值栈深。n=6 虽有 25 次调用，函数自身同时存活的调用最多为 6 个。

若把调用总数记为 C(n)，则两个基例都为 1，其余为 C(n-1)+C(n-2)+1。它比单链求和增长快得多，重复子问题正是原因。本章只用很小的 n 展示这种代价，不把慢程序用于大规模计算；保存已算结果和动态规划留待后续，先学会识别重复工作。

**完整程序**

```python
def fib_report(n):
    if n < 2:
        return {"value": n, "calls": 1}
    left = fib_report(n - 1)
    right = fib_report(n - 2)
    return {"value": left["value"] + right["value"], "calls": 1 + left["calls"] + right["calls"]}

print(fib_report(4))
print(fib_report(6))
```

**预期输出**

```text
{'value': 3, 'calls': 9}
{'value': 8, 'calls': 25}
```


选题关联：来源主题 1（文末列出）。

<a id="examples"></a>

## 跟着做：原创例题

### 例题 1

追踪 factorial\_trace(3, events)，分别记录进入时的 n 和返回时的 n、结果。说明为什么返回记录中的 n 依次是 0、1、2、3，而不是全部为 0。

1. 先进入参数为 3、2、1、0 的四个调用，各自保留自己的参数。
2. n=0 直接得到基例结果 1，写入返回记录，再交回上一层。
3. n=1 收到 1 后得到 1；n=2 收到 1 后得到 2；n=3 收到 2 后得到 6。
4. 返回只回到直接调用者，并继续执行当时暂停的位置；外层局部 n 没有被内层覆盖。
5. events 是各层共享的调试列表，共记录八条事件，其存储要另外计入，不能当作无成本的观察。

**结果与核对**

进入顺序为 3、2、1、0，返回顺序为 0、1、2、3，最终答案为 6。四次调用对应八条进入或返回事件，事件条数不是调用条数。

**完整程序**

```python
def factorial_trace(n, events):
    events.append(["enter", n])
    if n == 0:
        result = 1
    else:
        smaller = factorial_trace(n - 1, events)
        result = n * smaller
    events.append(["leave", n, result])
    return result

events = []
result = factorial_trace(3, events)
for event in events:
    print(event)
print(result)
```

**预期输出**

```text
['enter', 3]
['enter', 2]
['enter', 1]
['enter', 0]
['leave', 0, 1]
['leave', 1, 1]
['leave', 2, 2]
['leave', 3, 6]
6
```


### 例题 2

递归求 \[-7, -2, -9, -2\] 的最大值，空列表返回 None，原输入不变。解释为什么不能把所有后缀的最大值都从 0 开始。

1. 外层先处理空列表；非空时，从下标 0 开始把求后缀最大值交给辅助函数。
2. 最后一项是非空后缀的基例，直接返回该项 -2，不再读取越界位置。
3. 向前返回时依次比较 -9 与 -2、-2 与 -2、-7 与 -2，答案一直保持 -2。
4. 用真实元素作基例才能适用于全负数；若偷偷放入 0，就把不存在的值混进了候选。
5. 每层只作一次比较，返回的是最大数值，不承诺某个重复最大值的下标；空输入 None 与合法结果 0 也不同。

**结果与核对**

非空结果为 -2，空输入为 None。长度 n 的非空列表有 n 次辅助调用、n-1 次值比较，最深 n 层；它没有比线性扫描少看元素。

**完整程序**

```python
def max_from(values, index):
    if index == len(values) - 1:
        return values[index]
    suffix = max_from(values, index + 1)
    if values[index] > suffix:
        return values[index]
    return suffix

def recursive_max(values):
    if len(values) == 0:
        return None
    return max_from(values, 0)

values = [-7, -2, -9, -2]
print(recursive_max(values), values)
print(recursive_max([]))
```

**预期输出**

```text
-2 [-7, -2, -9, -2]
None
```


<a id="practice"></a>

## 自己做：先完成再看解答

### 练习 1

对非负整数写 digit\_sum(n)，返回十进制各位之和。检查 5070、0 和 9，说明被缩小的量以及零的基例。

<details>
<summary>提示</summary>

个位由余数得到，其余数位由整除 10 得到；一位数已经可以直接回答。

</details>

<details>
<summary>解答与检查</summary>

结果为 12、0、9。n 小于 10 时直接返回 n；否则当前个位加其余数位之和。5070 依次变成 507、50、5，末尾的零不会阻止缩小。若输入有 d 位，调用数为 d，单位运算模型下时间和栈空间均为 Θ(d)，这里规模是数位数。

**完整程序**

```python
def digit_sum(n):
    if n < 10:
        return n
    return n % 10 + digit_sum(n // 10)

print(digit_sum(5070), digit_sum(0), digit_sum(9))
```

**预期输出**

```text
12 0 9
```


</details>

### 练习 2

写 count\_equal(values, target)，递归统计目标出现次数，不修改输入，不建立后缀切片。检查 \[2, 0, 2, -1, 2\] 中的 2，以及空列表。

<details>
<summary>提示</summary>

辅助函数接收起始下标；空后缀贡献 0，当前项相等时只额外加 1。

</details>

<details>
<summary>解答与检查</summary>

结果为 3 和 0。每个位置独立贡献一次，不能在第一次命中后直接返回，也不能把重复值去重。剩余长度每次减少一，n+1 次辅助调用覆盖全部位置和空后缀；时间与调用栈均为 Θ(n+1)。

**完整程序**

```python
def count_from(values, target, index):
    if index == len(values):
        return 0
    suffix = count_from(values, target, index + 1)
    if values[index] == target:
        return 1 + suffix
    return suffix

def count_equal(values, target):
    return count_from(values, target, 0)

values = [2, 0, 2, -1, 2]
print(count_equal(values, 2), count_equal([], 2))
print(values)
```

**预期输出**

```text
3 0
[2, 0, 2, -1, 2]
```


</details>

### 练习 3

写 is\_palindrome(values)，判断整数列表从两端读是否相同。辅助函数使用半开区间 \[lo, hi)，空表与单元素返回 True，不复制切片；检查 \[2, -1, 0, -1, 2\]、\[2, 3\] 和空表。

<details>
<summary>提示</summary>

长度不超过 1 时已完成；先比较 lo 与 hi-1，不同就直接返回 False，相同才递归到内部。

</details>

<details>
<summary>解答与检查</summary>

结果为 True、False、True。递归范围变成 \[lo+1, hi-1)，每次少两项，奇数长度最后留下中间一项。必须把内层布尔结果返回给外层；外侧相等不代表内部一定相等。最坏比较向下取整的 n/2 对，栈深仍为线性量级，发现首对不同则立即停止。

**完整程序**

```python
def palindrome_range(values, lo, hi):
    if hi - lo <= 1:
        return True
    if values[lo] != values[hi - 1]:
        return False
    return palindrome_range(values, lo + 1, hi - 1)

def is_palindrome(values):
    return palindrome_range(values, 0, len(values))

print(is_palindrome([2, -1, 0, -1, 2]))
print(is_palindrome([2, 3]), is_palindrome([]))
```

**预期输出**

```text
True
False True
```


</details>

<a id="pitfalls"></a>

## 容易混淆的地方

- **有基例就认为一定终止，却没有检查调用参数是否靠近它。** 给每条递归路径选一个有下界的整数规模，并证明它严格减少；同时写清输入前提。
- **只打印子调用的结果，或调用后忘记向外返回。** 打印是输出副作用，return 才把值交给直接调用者；需要组合时先保存子答案。
- **把整棵调用树的结点数当作同时占用的栈帧数。** 总调用数数所有进入事件，栈深数尚未返回的一条路径；顺序调用的兄弟分支不同时展开。
- **递归只传列表引用，就认为空间为常数，或盲目增大递归限制。** 共享输入仍需保存各层局部状态；先分析最长调用链，适合长链的简单任务可改用循环。

<a id="self-check"></a>

## 离开这一章前

- [ ] 为每个递归函数说清空输入或最小输入的直接答案。
- [ ] 用进入和返回两列追踪 factorial(3)，逐层标出本地 n。
- [ ] 检查每条分支是否返回约定类型，区分 None、0 和 False。
- [ ] 对同一个程序分别数全部调用与最大同时存活的调用。
- [ ] 用空表、单元素、全负数、重复值和内部不对称的列表检查答案与输入不变。

## 本章边界

- 递归程序用于理解机制，输入规模受解释器可用深度限制，不承诺任意大输入都能执行。
- 阶乘和数位程序采用整数单位运算模型，不把运算次数当作大整数真实耗时。
- 这里只讨论直接递归及顺序执行；不介绍异步、生成器、互相递归与异常展开。
- 朴素 Fibonacci 只演示重复子问题，记忆化和动态规划另设后续内容。

## 选题来源与覆盖

来源含学生报告时，仅将其作为选题线索；具体机制仍需结合后续实验或权威资料核对。

- [大一小学期/Week\_3-Python/docs/readme.md](https://github.com/PKUanonym/REKCARC-TSC-UHT/blob/37cd19f7a9fb80dc846a7016b3fd482ed5fe7cc0/%E5%A4%A7%E4%B8%80%E5%B0%8F%E5%AD%A6%E6%9C%9F/Week_3-Python/docs/readme.md)（已提取可读文本，固定版本 37cd19f7a9fb）
- 主题 1：Python 基础语法的外部学习入口；位置：第 41–80 行。
- 主题 2：从基础语法到工具与应用的建议阅读顺序；位置：第 121–160 行。

## 参考资料与规则核对

上游入口用于确定学习方向；下面的参考资料用于核对语言语义、数据结构或算法分析规则，例题和练习由本项目重新设计。

- [Python 3.11：函数定义与返回](https://docs.python.org/3.11/tutorial/controlflow.html#defining-functions)：核对每次函数调用的局部名字与 return 语义；本章调用轨迹和例题另行设计。
- [Python 3.11：解释器递归深度](https://docs.python.org/3.11/library/sys.html#sys.getrecursionlimit)：核对递归深度限制的含义，不假定固定可用层数，也不把增大限制当成算法改进。
- [Python 3.11：RecursionError](https://docs.python.org/3.11/library/exceptions.html#RecursionError)：核对超过解释器递归限制时的异常；正文使用可完成的小输入，不故意执行失控递归。

**继续学习**：先独立完成自测，再记录仍需回读的步骤。

[上一章：怎样把数据排成顺序：选择、插入与归并排序](12-sorting.md) · [下一章：把问题分小再合起来：分治与递归归并](14-divide-and-conquer.md)

[教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [记录自己的学习](../learning-log-template.md)
