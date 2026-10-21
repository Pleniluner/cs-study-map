# 一组数据怎样按位置存取：数组与顺序表

[返回教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md)

[上一章：把计算组织成函数：参数、返回值与局部名字](05-functions.md) · [下一章：相邻数据怎样连接：单链表与结点引用](07-linked-lists.md)

[学习目标](#objectives) · [需要的基础](#prerequisites) · [例题](#examples) · [练习](#practice) · [自测](#self-check)

状态：**AI 初稿，可开始试学**。生成模型：Codex 当前会话（未记录具体模型型号）。

本章围绕资料中识别到的知识点重新编写；讲解、数值模型、例题与练习为 AI 原创组织，不是原课程题目或答案。主题出处只说明选题关联，不证明全部推导已经正确。

前两章能处理几个整数，也能把重复计算写成函数。若要保存一排测量值，再查找、修改或交换其中一项，给每项单独起名字就不方便了。本章先把数组理解为按连续下标排列的一组位置，用 Python 列表练习索引和遍历，再手工模拟固定容量顺序表的插入与删除。你会区分数据值、下标、有效长度和容量，并亲眼看见修改共享列表怎样影响调用者。每段程序都完整给出；先画出下标与值，再预测输出，最后改变边界输入运行。

<a id="objectives"></a>

## 学完要能做到

- 区分下标、元素值、有效长度与容量，准确说明哪些位置可以读取。
- 用列表索引、遍历和基本方法处理一组整数，解释空列表的行为。
- 区分共享同一列表、复制外层列表以及函数内修改元素。
- 按正确方向搬移元素，完成固定容量顺序表的插入与删除。
- 用空表、边界位置、重复值及负数核对程序，并说明主要操作的次数。

<a id="prerequisites"></a>

## 需要的基础

- 掌握第 4、5 章的变量、条件、循环、函数和返回值。
- 理解从 0 开始编号及半开范围；本章会解释列表的新语法。
- 示例使用 Python 3.11 或更新版本，只处理小规模整数数据。

## 一、数组的编号与 Python 列表

数组把元素按位置编号。长度为 n 时，本章采用的非负下标依次为 0 到 n 减 1，第一个元素不是下标 1。经典固定数组通常把同类型的元素按固定宽度连续存放，知道起点和元素宽度，就能计算某个下标对应的位置。这是存储模型，不要把元素值误当成地址，也不要假定每个整数只占一个字节。

这里使用 Python 的 list 作为可执行工具。方括号和逗号写出一个列表，values\[1\] 读取下标 1 的元素，len(values) 返回元素个数。values\[1\] = 5 只替换这个位置，不增加长度。空列表写成 \[\]，长度为 0，因此没有任何可直接读取的元素。读取不存在的下标会报 IndexError，不能因为程序想读就认为该位置已经存在。

Python 列表可以改变长度，不等同于 C 风格的固定数组。在 CPython 中，连续组织的是对象引用，整数对象本身不保证紧挨着存放。本章不推测 Python 对象的实际字节地址，只用下标追踪逻辑位置；后面另用长度变量模拟固定容量顺序表。

下面的四项从下标 0 排到 3。修改下标 1 后，6、9、4 保留，第二项变成 5。Python 也允许负下标，例如非空列表的 -1 表示最后一项；这不是访问列表前面的内存。本章手写的插入删除接口将显式拒绝负下标，避免与这种语言便利混淆。

**完整程序**

```python
values = [6, 2, 9, 4]
values[1] = 5
print(len(values), values[0], values[-1])
print(values)
```

**预期输出**

```text
4 6 4
[6, 5, 9, 4]
```


选题关联：来源主题 1（文末列出）。

## 二、遍历：什么时候要值，什么时候要下标

遍历就是按规则逐项访问。只关心值时，可以写 for value in values；需要知道位置或修改某个位置时，可以遍历 range(len(values))，再读取 values\[index\]。前一种循环中的 value 是每轮绑定的名字，并不是一个自动连接回原位置的窗口；仅把 value 重新赋成别的整数，不会替换列表里的元素。

下面处理 4、-2、4、1 四项，只统计正数。count 记录已经遇到的正数个数，total 记录这些正数之和。初始都为 0；扫描各项之后的状态依次为 1 与 4、1 与 4、2 与 8、3 与 9。两个 4 位于不同位置，都会被计算，不能因为数值相同就合并掉一项。

循环不变式可以沿用前面章节的说法：每轮开始时，统计量恰好对应已经访问过的前缀。当前项为正就把它纳入统计，否则保持原统计量。结束时整个列表都已扫描，因此结果覆盖全部元素。空列表不会进入循环，零个正数的个数和总和都为 0。

如果需要修改每一项，应通过合法下标赋值，但不要一边按位置前进，一边随意插入或删除元素；长度和位置可能同时改变，使某些项被跳过。以后要筛选元素时，优先先读原列表、把保留项放进新列表。此处每项只检查一次，处理次数随元素个数成正比，不需要额外猜测循环执行了多少轮。

**完整程序**

```python
values = [4, -2, 4, 1]
count = 0
total = 0
for value in values:
    if value > 0:
        count = count + 1
        total = total + value
print(count, total)
```

**预期输出**

```text
3 9
```


选题关联：来源主题 1（文末列出）。

## 三、添加与删除：值和位置不要混用

列表带有操作它自己的方法。values.append(10) 的点号表示对 values 这个列表调用 append，把一个新元素加到末尾；values.insert(1, 5) 在当前下标 1 之前插入 5，后面的项整体后移。append 和 insert 都原地修改列表，并返回 None，不能把调用结果重新赋给 values 后还指望它是原列表。

values.pop(2) 按下标删除一项，并返回被删除的值；省略下标的 pop() 删除末项。下面先把 10 加到 8、3、6 的后面，再在下标 1 插入 5，得到 8、5、3、6、10。此时下标 2 已经是 3，删除后返回 3，剩下 8、5、6、10。必须根据每一步更新后的下标判断下一步。

按位置删除不同于按值删除。remove(x) 会寻找并删除第一个等于 x 的元素，而 pop(i) 把 i 当作位置；本章主要使用后者，方便逐格追踪。直接 pop 空列表或越界位置会报错，接下来手写接口会先检查条件。Python 的 insert 对某些越界位置有调整规则，我们的教学接口则采用明确的有效区间，不能混用。

长度变化还会带来搬移代价：在顺序存放的模型里，从前面或中间插入删除，需要给后面的元素换位置。尾部追加通常省去这些搬移，但动态列表偶尔需要扩容。不要把“代码只有一行”当成“无论多长都只做一步”；下一节之后会把搬移循环真正写出来。

**完整程序**

```python
values = [8, 3, 6]
values.append(10)
values.insert(1, 5)
removed = values.pop(2)
print(removed, values)
```

**预期输出**

```text
3 [8, 5, 6, 10]
```


选题关联：来源主题 1（文末列出）。

## 四、可变对象：共享和复制的边界

第 5 章用整数说明重新绑定参数不会改掉调用处的名字。列表让我们看见另一种情况：alias = original 让两个名字指向同一列表，并没有复制其中的元素。通过 alias\[0\] 修改一个位置，original 读到的这个位置也会改变，因为被修改的是同一个对象，而非只改了一个名字的绑定。

下面 add\_to\_first 接收列表和增量，先检查是否非空，再修改首项。调用时传入 alias，函数内的 values 与外部两个名字共享对象；把首项由 2 改成 5，会同时反映到 original 和 alias。函数不需要返回整个列表才能产生这种影响。反过来，若仅在函数内写 values = \[\]，那只是把局部名字改指新列表，不会清空外面的原列表。

original.copy() 建立一个新的外层列表。这里在修改前复制，所以 separate 的首项仍为 2，之后向 separate 追加 8 也不增加 original 的长度。但 copy 是浅拷贝：如果元素本身又是可变列表，新旧外层仍可能引用同一个内部对象。本章主要存整数，不能把例子的独立修改推广为“所有层都已复制”。

编写函数时应说明它是否修改输入。让读者在函数调用之前画两条指向同一个列表的箭头，再画 separate 的独立外层，比单看变量名更容易解释结果。空列表的保护也必不可少，否则 values\[0\] 在没有首项时就已经越界，尚未来得及进行加法。

**完整程序**

```python
def add_to_first(values, amount):
    if len(values) > 0:
        values[0] = values[0] + amount

original = [2, 5]
alias = original
separate = original.copy()
add_to_first(alias, 3)
separate.append(8)
print(original, alias, separate)
```

**预期输出**

```text
[5, 5] [5, 5] [2, 5, 8]
```


选题关联：来源主题 1（文末列出）。

## 五、固定容量顺序表：先搬哪一项

现在规定一个固定容量模型：data 的 Python 列表长度就是槽位容量，size 才是有效元素个数；有效区间为从 0 到 size 之前。后面的 0 是占位值，不表示元素不存在的唯一标记。真实数据也可以等于 0，所以必须依据 size 判断有效范围。初始化后不再用 append 或 insert 改变底层列表长度。

下面容量为 6，有效内容为 4、7、9，size 为 3。在下标 1 插入 6，需先空出位置：把原下标 2 的 9 复制到 3，再把原下标 1 的 7 复制到 2，最后写入 6。搬移必须从右向左；若先把 7 写到下标 2，再读下标 2，读到的就不再是原来的 9。

插入位置允许从 0 到 size，包含末尾；前提是容量还有空位。删除已有位置则只允许从 0 到 size 减 1，并把其后的元素从左向右搬一格，最后减少 size。方向不同，目的相同：读取旧值之前不能先把它覆盖。一次插入在最前面可能搬 size 项，末尾插入则不搬原元素。

data\[:size\] 是切片，表示从头到 size 之前的部分，返回新的外层列表，适合显示有效内容。切片本身也要复制所选引用，因此打印用的切片成本不应算作单次基本读写的成本。下面记录 moves 为 2，size 增至 4；容量始终为 6，四个有效位置之后仍是占位区。

**完整程序**

```python
data = [4, 7, 9, 0, 0, 0]
size = 3
index = 1
cursor = size
moves = 0
while cursor > index:
    data[cursor] = data[cursor - 1]
    cursor = cursor - 1
    moves = moves + 1
data[index] = 6
size = size + 1
print(size, moves, data[:size])
```

**预期输出**

```text
4 2 [4, 6, 7, 9]
```


选题关联：来源主题 1（文末列出）。

<a id="examples"></a>

## 跟着做：原创例题

### 例题 1

容量为 6 的顺序表底层为 \[7, 2, 8, 0, 0, 0\]，有效长度为 3。先在下标 1 插入 5，再删除更新后的下标 2，最后尝试删除下标 -1。实现两个会返回新长度的函数；非法位置或插入满表时保持数据和长度不变。输入 size 始终是合法有效长度。

1. 插入前检查位置在 0 到 size 之间，且 size 小于容量；本次位置 1 和容量条件都符合。
2. 从右向左搬移：原下标 2 的 8 写到 3，原下标 1 的 2 写到 2，再把 5 写到 1。
3. 把返回的新长度 4 赋回 size，此时有效内容为 7、5、2、8，底层长度仍为 6。
4. 删除更新后的下标 2，把右边的 8 左移，原末位清为占位 0，返回新长度 3。
5. 负下标不属于本接口的合法位置，提前返回原长度，不进行任何写入。它不沿用 Python 负下标规则。

**结果与核对**

三次操作后的有效内容依次为 \[7, 5, 2, 8\]、\[7, 5, 8\]、\[7, 5, 8\]。插入增加一项、删除减少一项，拒绝操作不改变状态。函数修改了底层列表，但整数 size 仍须通过返回值更新。

**完整程序**

```python
def insert_at(data, size, index, value):
    if index < 0 or index > size or size == len(data):
        return size
    cursor = size
    while cursor > index:
        data[cursor] = data[cursor - 1]
        cursor = cursor - 1
    data[index] = value
    return size + 1

def erase_at(data, size, index):
    if index < 0 or index >= size:
        return size
    cursor = index
    while cursor < size - 1:
        data[cursor] = data[cursor + 1]
        cursor = cursor + 1
    data[size - 1] = 0
    return size - 1

data = [7, 2, 8, 0, 0, 0]
size = 3
size = insert_at(data, size, 1, 5)
print(size, data[:size])
size = erase_at(data, size, 2)
print(size, data[:size])
size = erase_at(data, size, -1)
print(size, data[:size])
```

**预期输出**

```text
4 [7, 5, 2, 8]
3 [7, 5, 8]
3 [7, 5, 8]
```


### 例题 2

编写 first\_index(values, target)，按下标从小到大查找第一个等于 target 的整数；找不到返回 -1，且不修改列表。对 \[5, 9, 5, 2\] 分别查找 5 和 7，再检查空列表。解释为什么有重复值时返回的是第一个位置。

1. 按 range(len(values)) 依次产生所有有效非负下标，尚未检查过的位置不预设答案。
2. 查找 5 时，下标 0 就满足比较，立即 return 0，所以后面下标 2 的相同值不会覆盖结果。
3. 查找 7 时依次比较 5、9、5、2，都不匹配，循环结束才返回 -1。
4. 空列表的范围为空，直接走到循环后的 return -1；整个函数没有给列表元素赋值。

**结果与核对**

输出依次为 0、-1、-1。-1 是本接口约定的未找到标记，不能直接拿它再次索引列表，否则 Python 会读取末项。最坏要检查所有 n 项；这与已经知道下标时直接读取一项不同。

**完整程序**

```python
def first_index(values, target):
    for index in range(len(values)):
        if values[index] == target:
            return index
    return -1

values = [5, 9, 5, 2]
print(first_index(values, 5), first_index(values, 7), first_index([], 5))
```

**预期输出**

```text
0 -1 -1
```


<a id="practice"></a>

## 自己做：先完成再看解答

### 练习 1

编写 largest(values)，返回整数列表的最大值；空列表返回 None，不修改输入，不调用 max。计算 \[-8, -3, -5\] 和空列表的结果，并说明为什么不能把当前最大值固定初始化为 0。

<details>
<summary>提示</summary>

先单独处理空列表，再用真实的首项初始化答案；逐个比较其余项。

</details>

<details>
<summary>解答与检查</summary>

结果为 -3 和 None。先用 -8 初始化，遇到 -3 更新，遇到 -5 保持。若从 0 开始，全负数会错误地保留一个根本不在列表中的 0。单元素列表没有后续项，直接返回首项。

**完整程序**

```python
def largest(values):
    if len(values) == 0:
        return None
    best = values[0]
    for index in range(1, len(values)):
        if values[index] > best:
            best = values[index]
    return best

print(largest([-8, -3, -5]), largest([]))
```

**预期输出**

```text
-3 None
```


</details>

### 练习 2

编写 nonnegative\_copy(values)，保持相对顺序，返回原列表中所有非负整数组成的新列表。原列表为 \[-2, 0, 5, -1, 5\]。输出结果和原列表，解释重复的 5 与零是否保留，并检查没有保留项的情况。

<details>
<summary>提示</summary>

从空的新列表开始，只向新列表 append，不在遍历过程中删除原列表元素。

</details>

<details>
<summary>解答与检查</summary>

结果为 \[0, 5, 5\]，原列表保持 \[-2, 0, 5, -1, 5\]。比较条件包含等于零，两个 5 是不同位置的两个有效项，都要保留。空输入或全部为负时返回新的空列表。

**完整程序**

```python
def nonnegative_copy(values):
    result = []
    for value in values:
        if value >= 0:
            result.append(value)
    return result

values = [-2, 0, 5, -1, 5]
print(nonnegative_copy(values), values)
print(nonnegative_copy([-4, -1]))
```

**预期输出**

```text
[0, 5, 5] [-2, 0, 5, -1, 5]
[]
```


</details>

### 练习 3

编写 reverse\_in\_place(values)，用左右两个下标交换元素，把 \[3, 8, 1, 6, 2\] 原地逆序，不使用 reverse、切片逆序或另一个结果列表。再检查空列表和 \[7\]。说明何时停止以及交换为何不会丢失旧值。

<details>
<summary>提示</summary>

左右从首末下标开始，左边仍在右边之前才交换；用临时变量保存即将被覆盖的一项。

</details>

<details>
<summary>解答与检查</summary>

两次交换后得到 \[2, 6, 1, 8, 3\]，中间的 1 不必动。左右每轮向内各走一步，最终相遇或交错。空列表的右下标为 -1，单元素的左右同为 0，都不会进入循环。函数原地修改并自然返回 None。

**完整程序**

```python
def reverse_in_place(values):
    left = 0
    right = len(values) - 1
    while left < right:
        saved = values[left]
        values[left] = values[right]
        values[right] = saved
        left = left + 1
        right = right - 1

values = [3, 8, 1, 6, 2]
empty = []
single = [7]
reverse_in_place(values)
reverse_in_place(empty)
reverse_in_place(single)
print(values, empty, single)
```

**预期输出**

```text
[2, 6, 1, 8, 3] [] [7]
```


</details>

<a id="pitfalls"></a>

## 容易混淆的地方

- **把容量当作有效长度，或把占位 0 当成空槽的唯一依据。** 固定容量模型只把前 size 项视为有效。真实元素也可以是 0，底层有槽位不表示其中都是有效数据。
- **从左向右执行插入搬移，覆盖后面还需要读取的旧值。** 插入时从右向左搬，删除时从左向右搬；每次写入前先判断源位置是否仍保存原值。
- **认为赋值给另一个名字就复制了列表，或把 append 的返回值当成列表。** 赋值建立共享绑定，copy 才新建外层；append 原地修改并返回 None。把返回值与对象变化分别核对。
- **把查找的 -1 结果直接用于索引，或把最大值初始化成零。** 先判断是否找到；负下标在 Python 中有独立含义。最大值应从实际元素初始化，并单独处理空输入。

<a id="self-check"></a>

## 离开这一章前

- [ ] 为四元素列表标出全部合法非负下标，解释 len 与最后下标的差别。
- [ ] 画出共享与 copy 后的引用关系，预测函数修改首项会影响哪些名字。
- [ ] 手算顺序表在头、中、尾插入的搬移次数，并实际检查满表拒绝后完全不变。
- [ ] 用含零、负数和重复值的列表验证查找、最大值和筛选。
- [ ] 独立逆序空表、单元素、奇数和偶数长度列表，再逆序一次确认恢复。

## 本章边界

- Python list 用于演示动态顺序结构，固定容量顺序表另用 size 模拟；不宣称 Python 整数对象连续存放。
- 只使用一维小整数列表；浅拷贝的嵌套共享仅作边界提醒，后续再讨论多维容器。
- 操作次数采用通常的单位成本模型；不在本章证明扩容摊还界或分析大整数的位运算成本。
- 手写接口要求 size 与底层容量一致；拒绝规定的越界或满表操作，但不负责验证任意类型及已损坏状态。

## 选题来源与覆盖

来源含学生报告时，仅将其作为选题线索；具体机制仍需结合后续实验或权威资料核对。

- [大一小学期/Week\_3-Python/docs/readme.md](https://github.com/PKUanonym/REKCARC-TSC-UHT/blob/37cd19f7a9fb80dc846a7016b3fd482ed5fe7cc0/%E5%A4%A7%E4%B8%80%E5%B0%8F%E5%AD%A6%E6%9C%9F/Week_3-Python/docs/readme.md)（已提取可读文本，固定版本 37cd19f7a9fb）
- 主题 1：Python 基础语法的外部学习入口；位置：第 41–80 行。
- 主题 2：从基础语法到工具与应用的建议阅读顺序；位置：第 121–160 行。

## 语言与结构规则核对

上游入口用于确定学习方向；下面的参考资料用于核对语言或数据结构规则，例题和练习由本项目重新设计。

- [Python 3.11：列表操作](https://docs.python.org/3.11/tutorial/datastructures.html#more-on-lists)：核对 append、insert、pop、remove、copy 的行为及原地修改的返回值。
- [Python 3.11：序列索引与切片](https://docs.python.org/3.11/library/stdtypes.html#sequence-types-list-tuple-range)：核对零基下标、负下标、切片及列表浅拷贝。
- [CPython 列表实现说明](https://docs.python.org/3.11/faq/design.html#how-are-lists-implemented-in-cpython)：区分连续的引用数组与被引用对象，不把实现描述推广为整数对象连续存放。

**继续学习**：先独立完成自测，再记录仍需回读的步骤。

[上一章：把计算组织成函数：参数、返回值与局部名字](05-functions.md) · [下一章：相邻数据怎样连接：单链表与结点引用](07-linked-lists.md)

[教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [记录自己的学习](../learning-log-template.md)
