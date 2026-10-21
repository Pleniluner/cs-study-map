# 相邻数据怎样连接：单链表与结点引用

[返回教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md)

[上一章：一组数据怎样按位置存取：数组与顺序表](06-arrays.md) · [下一章：最后进入的先取出：栈与嵌套处理](08-stacks.md)

[学习目标](#objectives) · [需要的基础](#prerequisites) · [例题](#examples) · [练习](#practice) · [自测](#self-check)

状态：**AI 初稿，可开始试学**。生成模型：Codex 当前会话（未记录具体模型型号）。

本章围绕资料中识别到的知识点重新编写；讲解、数值模型、例题与练习为 AI 原创组织，不是原课程题目或答案。主题出处只说明选题关联，不证明全部推导已经正确。

顺序表把逻辑上的相邻元素安排在相邻下标里，插入删除往往需要搬动后面的内容。单链表换一种表示：每个结点保存自己的值，再保存通向下一个结点的引用，整条链从头引用开始。本章用只有两个字段的 Python 字典表示结点，先补必要语法，再逐步完成遍历、插入、删除和逆序。重点不是背代码，而是在每次修改链接前知道旧的后继在哪里，修改后还能从头找到哪些结点。所有例子都约定链有限、无环，并用输出的值序列核对结果。

<a id="objectives"></a>

## 学完要能做到

- 用 value 与 next 两个字段画出单链表，并区分结点值、结点引用和头引用。
- 从头逐结点遍历，说明为什么按序号访问通常需要经过前面的结点。
- 正确执行头插、已知结点后的插入及删除第一个匹配值。
- 解释函数何时修改共享结点，何时必须把新头引用接回调用者。
- 检查空链、单结点、重复值和首尾操作，保存后继后完成原地逆序。

<a id="prerequisites"></a>

## 需要的基础

- 掌握函数、循环以及第 6 章列表索引、append、可变对象共享。
- 知道 None 可以表示没有结果；本章把它用作没有后继或空链的标记。
- 不要求类、指针算术或手动申请释放内存；示例为 Python 3.11+。

## 一、用两个字段表示一个结点

结点需要同时保存数据和后继。本章用字典表示这两个带名字的字段：大括号包住记录，字符串键 value 对应整数，键 next 对应下一个结点或 None，冒号隔开键与值，逗号隔开两组字段。node\["value"\] 按键读取内容；它不同于列表的数字下标。这里仅使用固定字段，不展开字典的通用查找实现。

下面先创建末结点 tail，值为 9、后继为 None，再创建头结点 head，值为 4、后继指向 tail。逻辑顺序是 4 接着 9，再到结束标记。结点在物理内存里不必相邻，next 也不是“地址加一”；通过当前结点保存的引用，才能知道下一步去哪里。

head 是整条链的入口名字，并不是自动包含所有结点的容器。空链约定为 head 指向 None；非空链最后一个结点的 next 为 None。读取字段之前必须先确定当前不是 None。Python 的 is None、is not None 用来检查是否为这个特定的空标记；这里不要把值为 0 的结点误判为空。

字典也是可变对象。current = head 只让两个名字指向同一结点，随后修改 current 的 value，head 读到的值也会变化。下面从 4 改成 6，后继仍指向 9。这里的字典只是结点表示方法；它不把按字段访问变成按链表位置随机访问，也不意味着我们已经实现了完整的通用链表类。

**完整程序**

```python
tail = {"value": 9, "next": None}
head = {"value": 4, "next": tail}
print(head["value"], head["next"]["value"])
current = head
current["value"] = 6
print(head["value"])
```

**预期输出**

```text
4 9
6
```


选题关联：来源主题 1（文末列出）。

## 二、遍历：移动游标，不要丢掉入口

遍历从 current = head 开始。只要 current 不是 None，就读取当前 value，再把 current 改为当前 next。每轮沿一条链接前进，遇到末结点的空后继时停止。下面 chain\_values 把访问到的值依次放入新列表，用来观察逻辑顺序；它不改变原结点的 value 或 next，也不修改调用者的 head。

对 5 接着 8、再接着 5 的链，游标先后指向三个不同结点，输出 \[5, 8, 5\]。首尾值相同不代表是同一个结点，更不能看到第二个 5 就认为遍历已经回到了起点。是否结束由引用是否为 None 决定，不能靠值是否重复判断。

本章约定输入是有限、无环的单链表。因此每次前进都会走向尚未处理的后缀，最终到达 None。若误把某个 next 接回前面的结点，就制造了环，普通遍历可能永不结束；这属于结构被破坏，不在本章遍历函数的正常输入范围。测试时会另检查结点身份，防止只看值序列就漏掉环。

对链表的第 i 个位置，通常必须从头经过前 i 个结点，不能照搬数组按下标直接定位的办法。访问整条 n 结点链需要 n 次结点处理，游标本身只需常数个名字；本例为了打印还额外建立了 n 项列表。这部分观察开销要与链表本身的存储、遍历的辅助状态分开理解。

**完整程序**

```python
def chain_values(head):
    values = []
    current = head
    while current is not None:
        values.append(current["value"])
        current = current["next"]
    return values

third = {"value": 5, "next": None}
second = {"value": 8, "next": third}
head = {"value": 5, "next": second}
print(chain_values(head))
print(chain_values(None))
```

**预期输出**

```text
[5, 8, 5]
[]
```


选题关联：来源主题 1（文末列出）。

## 三、头插：返回新入口才能看到新结点

在头部插入整数，只需创建一个新结点，让它的 next 指向原来的 head，然后把新结点作为新头返回。先连接旧链，再更新入口，原链里的全部结点都能从新头继续访问。空链也适用：旧 head 为 None，新结点的后继自然为空，得到单结点链。

prepend 的参数 head 是局部名字。它返回新结点，并不会自动重绑调用者保存头引用的那个变量，因此调用处必须写 head = prepend(head, value)。如果只调用而不接回返回值，旧 head 仍指向原首结点，从这个入口看不到新插入的一项。对象修改和名字重新绑定又一次需要区分。

下面先头插 7，再保留旧入口 older，然后头插 3。新 head 能依次访问 3、7，而 older 仍从 7 开始。两条可观察的序列并不是两条完全独立的复制链，它们共享原来的 7 结点。若经由 older 修改该结点的值，从新 head 沿后继也会看到变化。

头插不需要先找到链尾，已有链再长也只增加一个结点、建立一条后继链接并返回新头。连续按 1、2、3 的顺序头插，会得到 3、2、1；如果要从列表构建同顺序的链，可以从列表末尾向前头插。这里的常数操作数忽略底层对象分配的具体耗时，不把每台机器上的运行时间说成完全相同。

**完整程序**

```python
def chain_values(head):
    values = []
    current = head
    while current is not None:
        values.append(current["value"])
        current = current["next"]
    return values

def prepend(head, value):
    return {"value": value, "next": head}

head = prepend(None, 7)
older = head
head = prepend(head, 3)
print(chain_values(head), chain_values(older))
```

**预期输出**

```text
[3, 7] [7]
```


选题关联：来源主题 1（文末列出）。

## 四、在已知结点后插入：先保留旧后继

假设已经拿到某个真实结点 node，要在它后面插入 value。新结点应当先接到 node 原来的后继，再让 node 的 next 改为新结点。修改前的关系是 node 接旧后继，修改后变成 node 接新结点接旧后继。链头没有改变，旧后缀也没有丢失。

顺序十分关键：如果先把 node 的 next 覆盖成新结点，然后才想读取“原后继”，读到的已经不是旧值。若把新结点再接到自己，就形成自环。下面通过创建字典时读取原 next 保存连接，再执行第二条写入语句，保证每个旧结点仍可到达。

insert\_after 接收结点引用，而不是某个序号或数据值。参数为 None 时没有可插入在其后的结点，本接口返回 False，并保持结构不变；真实结点则返回 True。它可以在尾结点之后插入，因为旧后继允许为 None。这里不会验证结点来自哪条链，调用者应传入自己要修改的那条链中的结点。

在已经知道 node 的前提下，改链接只涉及固定几项操作，不需要像顺序表一样搬移后缀。但若题目先要求“找到值为某数的结点，再在后面插入”，寻找本身可能要遍历整条链。不能把插入链接的常数代价推广成所有按值插入任务都是常数时间。

**完整程序**

```python
def chain_values(head):
    values = []
    current = head
    while current is not None:
        values.append(current["value"])
        current = current["next"]
    return values

def insert_after(node, value):
    if node is None:
        return False
    new_node = {"value": value, "next": node["next"]}
    node["next"] = new_node
    return True

tail = {"value": 9, "next": None}
head = {"value": 2, "next": tail}
print(insert_after(head, 4))
print(chain_values(head))
print(insert_after(None, 6))
```

**预期输出**

```text
True
[2, 4, 9]
False
```


选题关联：来源主题 1（文末列出）。

## 五、删除第一个匹配：头结点要单独处理

删除的意思是让目标结点退出从当前 head 可达的逻辑序列。本章按值删除第一个匹配项，允许值重复；找不到时保持原链。空链直接返回 None。若头结点已经匹配，没有前驱结点可改，因此返回原头的 next 作为新入口，调用者仍须接回这个返回值。

其余情况用 previous 和 current 两个游标。previous 总是 current 的前驱，初始分别指向头和第二结点。找到匹配时，把 previous 的 next 改接 current 的 next，然后立即返回原头；这就绕过一个结点，并保留它之后的整个后缀。没有匹配就先让前驱前进到当前，再让当前前进到后继。

删除末结点时，它的后继是 None，前驱改接 None 就成为新尾；删除唯一结点则由头匹配分支返回 None。没有匹配时只是移动局部游标，所有 next 不变。下面链为 4、7、9，删除 7 后得到 4、9，说明没有把尾部 9 一起弄丢。

改变链接不等于立刻销毁 Python 对象。若其他名字仍引用被移出的结点，它仍可能被访问；本章不手动释放内存，也不承诺另一个旧入口随新 head 自动更新。最坏需要逐个比较所有 n 个值，真正改链接只做一次；因此按值删除的总体查找成本仍随链长增长。

**完整程序**

```python
def chain_values(head):
    values = []
    current = head
    while current is not None:
        values.append(current["value"])
        current = current["next"]
    return values

def delete_first(head, target):
    if head is None:
        return None
    if head["value"] == target:
        return head["next"]
    previous = head
    current = head["next"]
    while current is not None:
        if current["value"] == target:
            previous["next"] = current["next"]
            return head
        previous = current
        current = current["next"]
    return head

tail = {"value": 9, "next": None}
middle = {"value": 7, "next": tail}
head = {"value": 4, "next": middle}
head = delete_first(head, 7)
print(chain_values(head))
```

**预期输出**

```text
[4, 9]
```


选题关联：来源主题 1（文末列出）。

<a id="examples"></a>

## 跟着做：原创例题

### 例题 1

从空链开始，依次头插 9、2、5，再在当前第二个结点之后插入 7。每次先画出链接，最后输出逻辑值序列。为什么头插输入顺序与最终顺序不同，为什么最后的插入不需要移动尾结点？

1. 初始 head 为 None，头插 9 后得到一个 next 为空的结点。
2. 头插 2 时，新结点接到旧头 9；头插 5 时再接到 2，得到 5、2、9。
3. 当前第二结点由 head 的 next 找到，它保存 2，原后继保存 9。
4. 先创建值为 7、后继为原 9 结点的新结点，再把 2 结点的 next 改到它。
5. 从头重新遍历，依次访问 5、2、7、9，最后到 None；原来的三个结点身份保持。

**结果与核对**

三次头插后为 \[5, 2, 9\]，再插入后为 \[5, 2, 7, 9\]。每次头插都放到旧首项之前，所以顺序反转。最后一次只改链接，9 仍是原结点，不需要搬到新的下标。

**完整程序**

```python
def chain_values(head):
    values = []
    current = head
    while current is not None:
        values.append(current["value"])
        current = current["next"]
    return values

def prepend(head, value):
    return {"value": value, "next": head}

def insert_after(node, value):
    if node is None:
        return False
    new_node = {"value": value, "next": node["next"]}
    node["next"] = new_node
    return True

head = None
for value in [9, 2, 5]:
    head = prepend(head, value)
print(chain_values(head))
insert_after(head["next"], 7)
print(chain_values(head))
```

**预期输出**

```text
[5, 2, 9]
[5, 2, 7, 9]
```


### 例题 2

从列表 \[6, 4, 6, 8\] 建立同顺序链表，依次删除第一个 6、再删除第一个 6、最后删除不存在的 9。给出每次结果，说明为何第一次删除只移出一个 6。构链时不修改输入列表。

1. make\_chain 从末下标向前扫描，按 8、6、4、6 头插，因此得到原列表顺序 6、4、6、8。
2. 第一次删除 6 时头就匹配，返回后继 4 作新头；后面的另一个 6 仍在链中。
3. 第二次删除 6 时头 4 不匹配，游标到第二结点命中，把 4 的 next 改接 8。
4. 删除 9 时检查 4 和 8 均不匹配，返回原头，保留所有链接。
5. 每次重新从返回的 head 遍历，长度依次为 3、2、2，没有把不存在的值误当成尾结点删除。

**结果与核对**

三次结果依次为 \[4, 6, 8\]、\[4, 8\]、\[4, 8\]。函数在第一次命中后立即返回，符合只删一项的契约；连续值相同也仍是不同结点。找不到时不仅值序列不变，原结点和链接也不变。

**完整程序**

```python
def chain_values(head):
    values = []
    current = head
    while current is not None:
        values.append(current["value"])
        current = current["next"]
    return values

def make_chain(values):
    head = None
    index = len(values) - 1
    while index >= 0:
        head = {"value": values[index], "next": head}
        index = index - 1
    return head

def delete_first(head, target):
    if head is None:
        return None
    if head["value"] == target:
        return head["next"]
    previous = head
    current = head["next"]
    while current is not None:
        if current["value"] == target:
            previous["next"] = current["next"]
            return head
        previous = current
        current = current["next"]
    return head

head = make_chain([6, 4, 6, 8])
for target in [6, 6, 9]:
    head = delete_first(head, target)
    print(chain_values(head))
```

**预期输出**

```text
[4, 6, 8]
[4, 8]
[4, 8]
```


<a id="practice"></a>

## 自己做：先完成再看解答

### 练习 1

编写 chain\_length(head)，遍历统计结点个数，不建立值列表，不修改任何链接。检查由 \[3, 3, -1\] 建立的链和空链。重复值为什么仍分别计数？

<details>
<summary>提示</summary>

使用独立游标，每成功访问一个非空结点就加一，然后沿 next 前进。

</details>

<details>
<summary>解答与检查</summary>

两条链的长度分别为 3 和 0。两个 3 占不同结点，因此各加一次；-1 是普通整数值，不是结束标记。空链初次检查就结束，保留计数 0。只移动局部游标，调用者的头及全部链接不变。

**完整程序**

```python
def make_chain(values):
    head = None
    index = len(values) - 1
    while index >= 0:
        head = {"value": values[index], "next": head}
        index = index - 1
    return head

def chain_length(head):
    count = 0
    current = head
    while current is not None:
        count = count + 1
        current = current["next"]
    return count

print(chain_length(make_chain([3, 3, -1])), chain_length(None))
```

**预期输出**

```text
3 0
```


</details>

### 练习 2

编写 append\_value(head, value)，只保存头引用时把整数加到链尾，并返回新头。检查 \[5, 1\] 末尾追加 5，以及空链追加 7。解释空链分支和非空链分支为何不同，不维护额外的长期尾引用。

<details>
<summary>提示</summary>

先创建后继为 None 的新结点。空链直接返回它；非空链沿 next 找到后继为空的结点，再修改其 next。

</details>

<details>
<summary>解答与检查</summary>

结果分别为 \[5, 1, 5\] 和 \[7\]。非空链的头不变，只有原尾结点多接一个后继；空链没有原尾，必须用新结点建立入口。只有头引用时，找尾需要遍历，不能把这整个函数说成常数时间。

**完整程序**

```python
def chain_values(head):
    values = []
    current = head
    while current is not None:
        values.append(current["value"])
        current = current["next"]
    return values

def make_chain(values):
    head = None
    index = len(values) - 1
    while index >= 0:
        head = {"value": values[index], "next": head}
        index = index - 1
    return head

def append_value(head, value):
    node = {"value": value, "next": None}
    if head is None:
        return node
    current = head
    while current["next"] is not None:
        current = current["next"]
    current["next"] = node
    return head

head = make_chain([5, 1])
head = append_value(head, 5)
single = append_value(None, 7)
print(chain_values(head), chain_values(single))
```

**预期输出**

```text
[5, 1, 5] [7]
```


</details>

### 练习 3

编写 reverse\_chain(head)，原地反转 \[2, 8, 4\] 的 next 链接，返回新头，不交换数据值、不新建结点。保存原头引用，检查它反转后是否成为尾结点。再说明空链和单结点的结果。

<details>
<summary>提示</summary>

维护已反转前缀的头 previous 和未处理后缀的头 current。覆盖 current 的 next 之前，先用 following 保存原后继。

</details>

<details>
<summary>解答与检查</summary>

链接逐步变为 2 接 None、8 接 2、4 接 8，最终返回 4，新顺序为 \[4, 8, 2\]。原头 2 现在的 next 为 None。若不先保存 following，反向改链后就会丢失未处理后缀。空链返回 None；单结点链返回原头引用，该结点的 next 仍为 None。

**完整程序**

```python
def chain_values(head):
    values = []
    current = head
    while current is not None:
        values.append(current["value"])
        current = current["next"]
    return values

def make_chain(values):
    head = None
    index = len(values) - 1
    while index >= 0:
        head = {"value": values[index], "next": head}
        index = index - 1
    return head

def reverse_chain(head):
    previous = None
    current = head
    while current is not None:
        following = current["next"]
        current["next"] = previous
        previous = current
        current = following
    return previous

head = make_chain([2, 8, 4])
old_head = head
head = reverse_chain(head)
print(chain_values(head), old_head["next"] is None)
print(chain_values(reverse_chain(None)), chain_values(reverse_chain(make_chain([7]))))
```

**预期输出**

```text
[4, 8, 2] True
[] [7]
```


</details>

<a id="pitfalls"></a>

## 容易混淆的地方

- **把相同的值当成同一个结点，或用值为零判断空链。** 值可以相同或为零；结点由引用区分，空链与末尾后继由 None 标记。
- **头插或删除头结点后没有接回返回的新头。** 函数的局部 head 不会重绑外部名字；应把返回值赋回调用者保存的入口。
- **覆盖 next 后再寻找旧后继，丢失后缀或形成自环。** 改链之前先保留还需要访问的旧引用，改完后从头核对可达结点及结束位置。
- **把已知前驱后的改链接成本当成任意查找删除的总成本。** 先分清是否已经拿到位置；按值查找、找前驱或只凭头找尾，都可能需要遍历。

<a id="self-check"></a>

## 离开这一章前

- [ ] 画出两个值相同但身份不同的结点，指出 head 与 next 各自保存什么。
- [ ] 头插两项后保留旧入口，解释它与新链共享哪一段。
- [ ] 逐步完成删除头、中、尾、唯一结点和不存在的值，核对新头与全部链接。
- [ ] 对连续重复值验证 delete\_first 每次只删除一个结点。
- [ ] 独立反转链，再反转一次；检查值顺序恢复、结点未丢失且末尾仍为 None。

## 本章边界

- 所有输入链都约定有限无环且有 value、next 字段；正文不实现环检测或任意损坏结构的恢复。
- 字典结点用于解释引用关系，不代表真实指针地址或低层内存布局。
- 只实现单链、无哨兵的入门版本；双向链、循环链及带长期尾引用的封装留待后续。
- 删除只改变可达关系，不承诺 Python 对象即时销毁；多个入口可能仍共享结点。

## 选题来源与覆盖

来源含学生报告时，仅将其作为选题线索；具体机制仍需结合后续实验或权威资料核对。

- [大一小学期/Week\_3-Python/docs/readme.md](https://github.com/PKUanonym/REKCARC-TSC-UHT/blob/37cd19f7a9fb80dc846a7016b3fd482ed5fe7cc0/%E5%A4%A7%E4%B8%80%E5%B0%8F%E5%AD%A6%E6%9C%9F/Week_3-Python/docs/readme.md)（已提取可读文本，固定版本 37cd19f7a9fb）
- 主题 1：Python 基础语法的外部学习入口；位置：第 41–80 行。
- 主题 2：从基础语法到工具与应用的建议阅读顺序；位置：第 121–160 行。

## 参考资料与规则核对

上游入口用于确定学习方向；下面的参考资料用于核对语言语义、数据结构或算法分析规则，例题和练习由本项目重新设计。

- [Python 3.11：字典](https://docs.python.org/3.11/tutorial/datastructures.html#dictionaries)：核对字典键值构造和按键读取；本章只用固定字段表示结点。
- [Python 3.11：对象、值与类型](https://docs.python.org/3.11/reference/datamodel.html#objects-values-and-types)：核对对象身份、可变性和引用关系；不依赖实际指针地址。
- [Open Data Structures：单链表](https://opendatastructures.org/newhtml/ods/latex/linkedlists.html)：核对结点后继、头部操作与遍历代价；本章自行设计无尾缓存、字典结点的入门实现。

**继续学习**：先独立完成自测，再记录仍需回读的步骤。

[上一章：一组数据怎样按位置存取：数组与顺序表](06-arrays.md) · [下一章：最后进入的先取出：栈与嵌套处理](08-stacks.md)

[教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [记录自己的学习](../learning-log-template.md)
