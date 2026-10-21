# 数据变多会怎样：算法分析与增长量级

[返回教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md)

[上一章：先进入的先处理：队列与循环数组](09-queues.md) · [下一章：怎样缩小候选范围：顺序查找与二分查找](11-searching.md)

[学习目标](#objectives) · [需要的基础](#prerequisites) · [例题](#examples) · [练习](#practice) · [自测](#self-check)

状态：**AI 初稿，可开始试学**。生成模型：Codex 当前会话（未记录具体模型型号）。

本章围绕资料中识别到的知识点重新编写；讲解、数值模型、例题与练习为 AI 原创组织，不是原课程题目或答案。主题出处只说明选题关联，不证明全部推导已经正确。

前几章已经能把一个算法写出来，也能用边界输入检查结果。接下来还要问：数据多一倍，主要工作会增加多少，额外需要保存多少内容？本章先明确输入规模和计数口径，再从循环推导精确次数，最后用增长量级概括趋势。我们不靠一次计时宣布某种方法永远更快，而是给出可重复核对的计数程序。学完后，你应能把正确性、终止性、工作量和空间分别说明，为比较查找与排序做好准备。

<a id="objectives"></a>

## 学完要能做到

- 说明输入规模、基本操作及计数中没有包含的工作。
- 分别推导顺序循环、矩形嵌套、三角嵌套与对半缩小的次数。
- 区分精确次数、O 上界、Θ 紧确量级和真实计时。
- 在相同输入规模下区分最好、最坏情况，不凭几个例子猜平均值。
- 说明额外空间是否包含输出，识别复制、切片与保存轨迹的开销。

<a id="prerequisites"></a>

## 需要的基础

- 掌握第 4–6 章的循环、函数、整数运算、列表及复制。
- 会按状态追踪有限循环；只需整数加乘与除法，本章补充指数和对数的直观含义。
- 程序使用 Python 3.11+；规模参数为非负整数，比较小规模整数时采用单位成本模型。

## 一、先定义规模，再决定数什么

算法分析先问输入有多大。对整数列表，本章用元素个数 n 作为规模，不用最大元素值；\[1000\] 的规模是 1，\[2, 2, 2\] 的规模是 3。若输入本身是一个表示规模的非负整数，则直接把它记作 n。不同问题可以有不同参数，必须先声明，不能看见变量名 n 就自动认定含义相同。

接着选定基本操作。下面统计正数时，只数 value 与 0 的比较，每访问一项增加一次 checks；结果 positive 则只在比较成立时增加。输入 \[7, -2, 0, 7\] 有两项为正，但做了四次比较。因此“得到几个结果”和“为得到结果做了几次工作”是两件事，重复的 7 也分别检查。

计数器本身、循环条件、字典构造和打印都没有计入 checks。这不表示这些工作没有成本，而是这个模型专门观察元素比较。只要每轮其他工作也为固定数量，就能用比较次数理解扫描的增长趋势；若每轮还复制整个列表，就必须另行计入，不能用一个计数器掩盖大操作。

本章把小整数加减、比较和合法列表下标读写当作单位工作，不把它们直接换算成纳秒。Python 整数可以变得很大，其运算成本会受位数影响；机器负载也会影响计时。空列表比较零次，但调用与返回仍有固定开销，所以零次基本操作不等于程序耗时为零。

**完整程序**

```python
def positive_report(values):
    positive = 0
    checks = 0
    for value in values:
        checks = checks + 1
        if value > 0:
            positive = positive + 1
    return {"positive": positive, "checks": checks}

report = positive_report([7, -2, 0, 7])
print(report["positive"], report["checks"])
print(positive_report([]))
```

**预期输出**

```text
2 4
{'positive': 0, 'checks': 0}
```


选题关联：来源主题 1（文末列出）。

## 二、顺序相加，嵌套逐层求和

两个先后执行的循环，如果各执行 n 次指定动作，总次数是 n 加 n，也就是 2n。它们不是彼此嵌套，不能相乘。下面 sequential 的两个循环都遍历 range(n)，n 为 4 时各加四次，最终为 8；n 为 0 时两个循环都不进入。

矩形嵌套则不同：外层每取一个 i，内层都完整取 n 个 j，所以共有 n 组、每组 n 次，共 n² 次。对 n 为 4，可以画四行四列的位置表，确认共有 16 对下标。这里包括 i 与 j 相等的对，也分别包括先后顺序相反的两对，因此不要误用“不重复配对”的公式。

若只考察 i 在 j 前面的不同位置，内层从 i 加 1 开始，到 n 之前结束。各行长度变为 n 减 1、n 减 2，一直到 0。把这串数正反相加，每对都是 n 减 1，共 n 对，所以原和为 n 乘以（n 减 1）再除以 2。n 为 4 时得到 3+2+1+0，也就是 6。

两个嵌套循环并不保证恰好 n² 次：内层范围可能固定、逐轮缩短，或者共享一个只前进的游标。应先写每轮究竟做几次，再求和。下面三个计数器都只数各自最内层的加一动作；外层末轮可能仍执行检查，却没有合法的内层位置。

**完整程序**

```python
def loop_counts(n):
    sequential = 0
    for i in range(n):
        sequential = sequential + 1
    for j in range(n):
        sequential = sequential + 1
    square = 0
    for i in range(n):
        for j in range(n):
            square = square + 1
    triangle = 0
    for i in range(n):
        for j in range(i + 1, n):
            triangle = triangle + 1
    return {"sequential": sequential, "square": square, "triangle": triangle}

print(loop_counts(4))
print(loop_counts(0))
```

**预期输出**

```text
{'sequential': 8, 'square': 16, 'triangle': 6}
{'sequential': 0, 'square': 0, 'triangle': 0}
```


选题关联：来源主题 1（文末列出）。

## 三、对半缩小为什么出现对数

把规模从 16 依次缩成 8、4、2、1，需要四次缩小。反向看，从 1 连续乘四个 2 正好得到 16，写作 2 的四次方。以 2 为底的对数 log₂16 就是 4：它回答把 2 乘多少次才能得到这个数。本章不要求计算任意小数对数，先用整数倍增和缩小理解。

half\_steps 使用整除，每轮 remaining 变为原来的一半向下取整，直到不大于 1。输入 19 时轨迹为 19、9、4、2、1，共四轮；不是把实际除法得到的小数一直保留下去。对正整数 n，若 2 的 k 次方不超过 n，而 2 的（k+1）次方超过 n，轮数正好是 k，也就是 log₂n 的向下取整。

终止性来自 remaining 在大于 1 时严格减少，并且一直是非负整数。0 和 1 初次检查便停止，返回 0；这两个输入单独处理，不去计算没有定义的 log₂0。判断条件若改为大于 0，或者改为向上取整，精确轮数就可能改变，所以“对半缩小”不足以唯一确定公式。

在这种模型里，n 从 16 增到 32，轮数只增加一次；逐项扫描却会从 16 次增到 32 次。对数增长由可排除的范围不断减半产生，并不是有 while 就一定如此。下一章二分查找也会缩小区间，但区间端点规则不同，应该重新证明其每一步。

**完整程序**

```python
def half_steps(n):
    remaining = n
    steps = 0
    while remaining > 1:
        remaining = remaining // 2
        steps = steps + 1
    return steps

for n in [0, 1, 2, 3, 16, 19]:
    print(n, half_steps(n))
```

**预期输出**

```text
0 0
1 0
2 1
3 1
16 4
19 4
```


选题关联：来源主题 1（文末列出）。

## 四、用 O 和 Θ 描述增长范围

精确次数适合核对某段实现，增长量级用于比较规模变大后的趋势。说 T(n) 属于 O(f(n))，意思是存在不随 n 改变的正的常数 c 和起点 n₀，使所有 n 至少为 n₀ 时都满足 T(n) 不超过 c 乘 f(n)。它给出渐近上界，不表示恰好执行 f(n) 次，也不直接等于最坏情况。

Θ 读作 theta，表示同时存在正的常数倍下界和上界，即增长被同一类函数夹住。例如 T(n)=3n+7，对 n 至少为 1，既不小于 3n，又不大于 10n，所以是 Θ(n)。它当然也属于 O(n²)，但这个更松的上界丢失了线性增长的信息；不能从 O(n²) 反推“必定二次增长”。

逐项扫描常见 Θ(n)，矩形和三角配对都为 Θ(n²)，前面的正整数对半缩小在 n 足够大时为 Θ(log n)。以后每层扫描 n 项、层数为对数量级，就会出现 Θ(n log n)。分析先得到实际工作表达式，再解释起主导作用的项；常数和低次项被忽略，只是在概括增长时忽略。

下面比较两条假定的工作量公式 3n+7 与 n²，不是在运行两种待测算法。n 为 2 时前者反而更大，到 8 时顺序改变。量级不能保证在任何小输入、任何机器上都更快，更不能把打印出的数字称为秒数。同属 Θ(n) 的两个实现仍可能有不同常数、复制次数和实际表现。

**完整程序**

```python
def linear_model(n):
    return 3 * n + 7

def quadratic_model(n):
    return n * n

for n in [2, 8, 32]:
    print(n, linear_model(n), quadratic_model(n))
```

**预期输出**

```text
2 13 4
8 31 64
32 103 1024
```


选题关联：来源主题 1（文末列出）。

## 五、输入情况与额外空间分别说明

输入规模相同，运行路径仍可能不同。下面从左到右寻找首个相等元素，每次相等比较计一次。列表 \[6, 1, 6, 3\] 长度都是 4：查找 6 首次就成功，只比较一次；查找 3 比较四次；查找 9 也比较四次，最后返回未找到。重复值时遇到第一项就返回，后面的相同项不会继续检查。

对非空长度 n，最好只需一次，最坏需 n 次；空输入则零次比较。于是可以分别写最好时间为 Θ(1)、最坏时间为 Θ(n)。这里“最好、最坏”选择输入情况，“O、Θ”描述所得函数的增长，是两个不同维度。平均情况还要指定目标出现在哪里、缺失概率等分布，不能直接把几次演示的结果平均后推广。

时间之外还要看同时保留的额外存储。此查找只维护几个名字和一个固定字段的结果字典，按单位存储模型是 O(1) 额外空间。若先复制整个列表再查，复制就需 Θ(n) 时间与空间；若把每步完整列表保存为调试轨迹，空间还可能继续增长，不能把调试版本的成本混同于原算法。

本书讨论额外空间时会说明是否计入返回结果。返回 n 项新列表，即使循环内只有一个累计值，包含输出时仍需 Θ(n) 空间；不计输出时才可能只需 O(1) 辅助状态。这里数的是同时存在的槽位或引用，不是精确字节，也不追踪 Python 大整数的位级成本。

**完整程序**

```python
def first_report(values, target):
    checks = 0
    for index in range(len(values)):
        checks = checks + 1
        if values[index] == target:
            return {"index": index, "checks": checks}
    return {"index": -1, "checks": checks}

values = [6, 1, 6, 3]
for target in [6, 3, 9]:
    print(first_report(values, target))
print(first_report([], 6))
```

**预期输出**

```text
{'index': 0, 'checks': 1}
{'index': 3, 'checks': 4}
{'index': -1, 'checks': 4}
{'index': -1, 'checks': 0}
```


选题关联：来源主题 1（文末列出）。

<a id="examples"></a>

## 跟着做：原创例题

### 例题 1

程序先扫描 n 项，每项记一次；再枚举所有 i 在 j 前面的不同下标对，每对记一次。n 为非负整数。求 n=6 的两部分与总次数，并给出一般表达式和增长量级。

1. 第一段独立扫描六项，记 scan=6；第二段不会重新执行第一段。
2. 配对各行有 5、4、3、2、1、0 项，共 15 对，每一对只在较小下标那行出现。
3. 两个阶段先后执行，总数为 6+15=21，不把两个阶段相乘。
4. 一般式为 n+n(n−1)/2，即 n(n+1)/2；n=0 时为 0，n=1 时为 1。
5. 对足够大的 n，平方项主导，所以指定动作总次数为 Θ(n²)；程序实际还有循环与返回开销。

**结果与核对**

n=6 时扫描 6 次、配对 15 次、合计 21 次。也可用 6×7÷2 反向核对；总计不是 36，也不是 90。

**完整程序**

```python
def scan_then_pairs(n):
    scan = 0
    for i in range(n):
        scan = scan + 1
    pairs = 0
    for i in range(n):
        for j in range(i + 1, n):
            pairs = pairs + 1
    return {"scan": scan, "pairs": pairs, "total": scan + pairs}

print(scan_then_pairs(6))
print(scan_then_pairs(0))
```

**预期输出**

```text
{'scan': 6, 'pairs': 15, 'total': 21}
{'scan': 0, 'pairs': 0, 'total': 0}
```


### 例题 2

一种分轮处理从 width=1 开始，只要 width 小于 n，就完整访问 n 项一次，再把 width 翻倍。n 为非负整数。计算 n=5、9、0 的轮数和访问次数，并解释它与向下整除的 half\_steps 为何不同。

1. n=5 时进入循环的 width 为 1、2、4，下一次变为 8 已不小于 5，共三轮。
2. 每轮固定访问五项，访问总数为 5×3=15；n=9 时 width 为 1、2、4、8，共四轮、36 次。
3. n=0 或 1 时，初始 width=1 就不满足条件，不做完整扫描，计数都为零。
4. 对 n 至少为 1，轮数是使 2 的 k 次方至少为 n 的最小整数 k，即 log₂n 向上取整。
5. n 至少为 2 时，每轮线性工作乘对数量级的轮数，得到 Θ(n log n)；half\_steps 采用向下整除，所以不能照搬其精确轮数。

**结果与核对**

三组结果分别为 3 轮 15 次、4 轮 36 次、0 轮 0 次。翻倍的是处理跨度，扫描长度始终是 n；这为后续自底向上归并的分轮分析提供模型。

**完整程序**

```python
def full_pass_work(n):
    width = 1
    rounds = 0
    visits = 0
    while width < n:
        for index in range(n):
            visits = visits + 1
        rounds = rounds + 1
        width = width * 2
    return {"rounds": rounds, "visits": visits}

for n in [5, 9, 0]:
    print(n, full_pass_work(n))
```

**预期输出**

```text
5 {'rounds': 3, 'visits': 15}
9 {'rounds': 4, 'visits': 36}
0 {'rounds': 0, 'visits': 0}
```


<a id="practice"></a>

## 自己做：先完成再看解答

### 练习 1

对非负整数 n，外层循环执行 n 次，每轮内层固定执行 3 次。写 fixed\_width(n) 返回内层动作总数，检查 n=7 与 n=0，并解释为何这段双层循环不是 Θ(n²)。

<details>
<summary>提示</summary>

不要把固定的 3 换成 n；先列出每轮内层长度，再相加。

</details>

<details>
<summary>解答与检查</summary>

n=7 时总数为 21，n=0 时为 0。一般是 3n，随 n 线性增长；外层的检查也只有线性数量，整体时间为 Θ(n)（对增长中的 n），额外只用固定数量计数器。

**完整程序**

```python
def fixed_width(n):
    visits = 0
    for row in range(n):
        for column in range(3):
            visits = visits + 1
    return visits

print(fixed_width(7), fixed_width(0))
```

**预期输出**

```text
21 0
```


</details>

### 练习 2

从位置 0 起处理 n 项，每批最多 batch\_size 项。n 是非负整数，batch\_size 是正整数；内层循环推进同一个 position，不在下一批重置。返回批数和成功访问数，检查 n=10、batch\_size=4 及空输入，并分析总工作。

<details>
<summary>提示</summary>

分别记录本批数量和全局位置。只有全局位置真的前进一次，才算访问一项。

</details>

<details>
<summary>解答与检查</summary>

10 项分为 4、4、2，共 3 批、10 次访问；空输入为 0 批 0 次。一般访问次数恰为 n，批数为向上取整的 n/batch\_size。虽然嵌套，position 总共只增加 n 次，外层批数也不超过 n，整体时间为 Θ(n+1)，固定数量计数器占 O(1) 额外空间。

**完整程序**

```python
def consume_batches(n, batch_size):
    position = 0
    batches = 0
    visits = 0
    while position < n:
        taken = 0
        while taken < batch_size and position < n:
            position = position + 1
            taken = taken + 1
            visits = visits + 1
        batches = batches + 1
    return {"batches": batches, "visits": visits}

print(consume_batches(10, 4))
print(consume_batches(0, 4))
```

**预期输出**

```text
{'batches': 3, 'visits': 10}
{'batches': 0, 'visits': 0}
```


</details>

### 练习 3

编写 prefix\_totals(values)，返回每个位置之前及该位置本身的整数累计和，不修改输入。检查 \[3, -1, 4\] 和空列表；分别说明包含返回列表、以及不包含返回列表时的额外空间。

<details>
<summary>提示</summary>

保留一个运行中的 total，每访问一项更新一次，再把当前总和加入结果列表。

</details>

<details>
<summary>解答与检查</summary>

结果为 \[3, 2, 6\]，空输入为 \[\]，原列表不变。每项一次累计与一次追加，总体时间为 Θ(n+1)。包含输出时额外空间为 Θ(n+1)，若单独排除返回列表，累计值与游标只占 O(1) 单位存储；不能因为只有一个累计变量就忽略 n 项输出。

**完整程序**

```python
def prefix_totals(values):
    result = []
    total = 0
    for value in values:
        total = total + value
        result.append(total)
    return result

values = [3, -1, 4]
print(prefix_totals(values), values)
print(prefix_totals([]))
```

**预期输出**

```text
[3, 2, 6] [3, -1, 4]
[]
```


</details>

<a id="pitfalls"></a>

## 容易混淆的地方

- **把输出数量、代码行数或一次测得的秒数当作基本操作次数。** 先声明规模和计数对象；一个语句可能复制很多项，仪器计数也不是完整执行时间。
- **看到两层循环就判为平方，或把两个先后阶段的次数相乘。** 逐轮列出内层范围；顺序阶段相加，共享游标与固定内层宽度需要单独分析。
- **把 O 当成精确等号或最坏情况的同义词，把 Θ 当成平均情况。** 输入情况与渐近符号分别说明；O 给上界，Θ 给匹配的上下界，平均分析另需概率模型。
- **忽略排序前检查、复制、切片、输出或调试轨迹的开销。** 分析完整流程，并说明峰值额外空间是否包含返回结果；局部操作快不等于全流程同样快。

<a id="self-check"></a>

## 离开这一章前

- [ ] 给自己的循环选一个基本操作，先手算再用计数器验证。
- [ ] 解释 2n、n²、n(n−1)/2 各对应哪一种下标范围。
- [ ] 分别追踪 n=1、7、8、9 的向下对半与向上倍增，指出轮数为何不同。
- [ ] 为长度相同的查找构造首项命中、末项命中和缺失三种情况。
- [ ] 对返回一个整数与返回 n 项列表的程序，分别列出输入、输出及其他同时存活的状态。

## 本章边界

- 采用小整数和单位槽位模型；不分析大整数位复杂度、缓存、分配器及精确字节数。
- 计数程序用于验证模型，不是实际运行时间的基准测试。
- 平均情况、摊还分析的完整证明、递归式与概率分析留待后续。
- 对数与量级描述用于规模增长；零和单元素的实际行为仍按代码分别核对。

## 选题来源与覆盖

来源含学生报告时，仅将其作为选题线索；具体机制仍需结合后续实验或权威资料核对。

- [大一小学期/Week\_3-Python/docs/readme.md](https://github.com/PKUanonym/REKCARC-TSC-UHT/blob/37cd19f7a9fb80dc846a7016b3fd482ed5fe7cc0/%E5%A4%A7%E4%B8%80%E5%B0%8F%E5%AD%A6%E6%9C%9F/Week_3-Python/docs/readme.md)（已提取可读文本，固定版本 37cd19f7a9fb）
- 主题 1：Python 基础语法的外部学习入口；位置：第 41–80 行。
- 主题 2：从基础语法到工具与应用的建议阅读顺序；位置：第 121–160 行。

## 参考资料与规则核对

上游入口用于确定学习方向；下面的参考资料用于核对语言语义、数据结构或算法分析规则，例题和练习由本项目重新设计。

- [Algorithms 4/e：算法分析](https://algs4.cs.princeton.edu/14analysis/)：核对成本模型、输入相关性与增长分析；本章计数对象、数据及实验程序自行设计。
- [Open Data Structures：数学背景](https://opendatastructures.org/ods-python/1_3_Mathematical_Background.html)：核对指数、对数与 O 上界；取整循环的精确次数按本章代码另行推导。
- [Cornell CS312：渐近复杂度](https://www.cs.cornell.edu/courses/cs312/2003sp/lectures/lec12.html)：核对 O、Θ 及最好最坏与平均输入模型的区分，不移植课程练习。

**继续学习**：先独立完成自测，再记录仍需回读的步骤。

[上一章：先进入的先处理：队列与循环数组](09-queues.md) · [下一章：怎样缩小候选范围：顺序查找与二分查找](11-searching.md)

[教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [记录自己的学习](../learning-log-template.md)
