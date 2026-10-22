# 最后进入的先取出：栈与嵌套处理

[返回教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [哈希表与图练习指引](../hash-graphs-practice.md)

[上一章：相邻数据怎样连接：单链表与结点引用](07-linked-lists.md) · [下一章：先进入的先处理：队列与循环数组](09-queues.md)

[学习目标](#objectives) · [需要的基础](#prerequisites) · [例题](#examples) · [练习](#practice) · [自测](#self-check)

状态：**AI 初稿，可开始试学**。生成模型：Codex 当前会话（未记录具体模型型号）。

本章围绕资料中识别到的知识点重新编写；讲解、数值模型、例题与练习为 AI 原创组织，不是原课程题目或答案。主题出处只说明选题关联，不证明全部推导已经正确。

数组与链表说明了数据怎样组织，栈进一步约束允许怎样访问：新项从栈顶进入，也从栈顶取走，最后放入的先取出。第 2 章用四槽玩具栈演示过这种顺序，本章把它写成真正的 Python 程序，并把空栈行为、读取与删除、有限容量分别规定清楚。你会用栈逆序数据、保存可撤销状态，再检查括号是否正确嵌套。学习时始终画出从底到顶的有效内容，不用底层残留值猜测栈里还有什么；每个程序都能独立执行。

<a id="objectives"></a>

## 学完要能做到

- 按后进先出规则追踪一串入栈、出栈和只读栈顶操作。
- 为整数栈约定空操作结果，区分合法的零与 None。
- 用栈实现逆序与撤销，说明是否修改输入及为什么顺序正确。
- 使用栈检查括号前缀与最终状态，识别数量相同但次序错误的输入。
- 实现容量受限的入栈，并核对失败操作不改变原状态。

<a id="prerequisites"></a>

## 需要的基础

- 掌握第 6 章列表 append、pop、负下标和可变对象。
- 掌握函数返回值、条件与循环；字典配对表仅在最后一道练习使用。
- 会区分第 2 章教学机器和真实 Python 对象，不要求理解实际调用栈布局。

## 一、栈是一条访问规则

栈的核心规则是后进先出，常缩写为 LIFO。push 把一项放到栈顶，pop 移除并交回栈顶，peek 只读取栈顶。最早进入且尚未取出的项位于栈底。栈约束操作顺序，不规定一定用数组还是链表存储；同一规则可以有不同实现。

本章用列表末端作为栈顶，所以 append 入栈，不带下标的 pop() 出栈，非空时 stack\[-1\] 读取栈顶。打印列表时左边是底、右边是顶。下面原栈从底到顶为 3、7，压入 11 后顶变为 11，再弹出就取回 11，剩下 3、7。它不是按数值大小排序，即使新项很小，也应最先取出。

把列表当栈使用时，我们主动遵守只从末端进出的接口约定。虽然列表还支持在中间插入、删除，这些操作不属于本章栈接口；不能一边使用任意位置操作，一边仍按纯栈的顺序证明结果。栈中的重复值同样是多次独立加入的项，不会自动合并。

第 2 章规定了固定四槽容量及指令出错时的状态。本章的普通列表栈没有人为设置固定上限，有限容量会在练习里另行规定。两者共享后进先出规则，但存储与错误处理细节不同。解释程序前先说明采用哪套约定，不能把玩具机器的四槽限制套到这里。

**完整程序**

```python
stack = [3, 7]
stack.append(11)
value = stack.pop()
print(value, stack)
```

**预期输出**

```text
11 [3, 7]
```


选题关联：来源主题 1（文末列出）。

## 二、空栈与只读栈顶：先检查再访问

直接对空列表调用 pop 或读取 -1 下标都会报错。本章给整数栈设计两个保护函数：空栈时 peek 与 pop\_safe 都返回 None，且不改变栈；非空时前者只读，后者移除并返回末项。这是我们自己规定的接口，不是 Python 原生 pop 的空栈行为。

为了让 None 明确表示空，本组接口只接收整数数据。整数 0 是合法元素，不能把返回值放进“为真才成功”的判断里：0 为假却仍然可能是刚弹出的真实值。需要区分时用 result is None 检查空标记。若未来允许存入 None，就必须重新设计结果表示，不能继续沿用这个约定。

下面先对空栈读和弹，两次都得到 None，长度仍为零。依次加入 0、4 后，peek 返回 4，但长度仍为 2。随后两次 pop\_safe 分别移除 4、0，第三次才因栈空返回 None。判断成功与否要同时看返回值和栈是否实际减少了一项。

从列表末尾读取不需要搬移其他项；入栈和出栈也避免了头部操作的整体移位。在常见 CPython 列表实现中，长期连续追加的平均成本可摊还到常数量级，但个别扩容操作会更贵。这里不把打印整栈或复制整栈的成本计入一次栈顶访问，也不声称每次实际耗时完全相同。

**完整程序**

```python
def peek(stack):
    if len(stack) == 0:
        return None
    return stack[-1]

def pop_safe(stack):
    if len(stack) == 0:
        return None
    return stack.pop()

stack = []
print(peek(stack), pop_safe(stack), len(stack))
stack.append(0)
stack.append(4)
print(peek(stack), len(stack))
print(pop_safe(stack), pop_safe(stack), pop_safe(stack), len(stack))
```

**预期输出**

```text
None None 0
4 2
4 0 None 0
```


选题关联：来源主题 1（文末列出）。

## 三、用后进先出解释逆序

要把一组值按相反顺序读出，可以先按原顺序逐项压栈，再持续弹出。最后读入的一项最先弹出，倒数第二项接着弹出，直到第一项最后取出。这个结论来自操作顺序，不依赖整数大小、是否为负或是否重复。

下面 reversed\_copy 接收列表，建立自己的空栈与结果列表。先把 2、7、1 压入，栈顶是 1；三次弹出依次得到 1、7、2，每次放到结果末尾。函数返回新结果，输入列表不被修改。这里使用的是逐项放入的整数值，不是把原列表名字直接当成栈再把它清空。

两个循环各有清楚的进展：第一个遍历有限输入，第二个每轮成功弹出一项，栈长减少 1。第二个循环用非空条件保护 pop，所以不会在已经耗尽后多弹一次。空输入让两个循环都不执行，返回空列表；单元素输入只有一次入栈和一次出栈。

这个方法用额外空间换来简单的顺序解释。输入有 n 项，就做 n 次入栈和 n 次出栈，还建立结果列表；额外存储随 n 增长。第 6 章的左右交换可以原地逆序，而这里为了学习栈选择保留输入。两种方法的结果相似，但是否修改输入、占多少辅助空间需要分别说明。

**完整程序**

```python
def reversed_copy(values):
    stack = []
    for value in values:
        stack.append(value)
    result = []
    while len(stack) > 0:
        result.append(stack.pop())
    return result

values = [2, 7, 1]
print(reversed_copy(values), values)
print(reversed_copy([]))
```

**预期输出**

```text
[1, 7, 2] [2, 7, 1]
[]
```


选题关联：来源主题 1（文末列出）。

## 四、撤销：保存修改之前的状态

撤销的自然顺序也是后进先出：最近一次成功修改应最先被撤销。本章用一个整数状态表示简化的计数器，每次修改前先把旧状态压入 history，然后应用本次增量。撤销时从 history 弹出旧状态并恢复；历史为空时就没有更早状态可恢复。

下面状态从 0 开始，依次增加 4、-2、7。第一次修改前保存 0，状态变 4；第二次保存 4，状态变 2；第三次保存 2，状态变 9。因此 history 从底到顶为 0、4、2。第一次撤销取回 2，第二次取回 4，均按最近的修改倒着回退。

这里必须保存“修改之前”的状态。若先修改后入栈，第一次弹出只是当前值，看起来撤销没有发生。也不要为了撤销重新计算某个增量的反操作；不是每种修改都容易求逆，保存旧状态能直接恢复。本例只保存整数，不需要深拷贝，但未来若状态是可变对象，只保存同一引用可能无法保住历史内容。

这只是单步历史恢复模型，不包含重做、分支历史、持久化或多个用户同时操作。展示程序在每次 pop 之前检查是否还有历史，不会因多撤销一次访问空栈。若想限制保存数量，还需要明确丢弃哪一端以及用户能撤销多久，不能默默改变栈规则。

**完整程序**

```python
state = 0
history = []
for change in [4, -2, 7]:
    history.append(state)
    state = state + change
print(state, history)
if len(history) > 0:
    state = history.pop()
print(state, history)
if len(history) > 0:
    state = history.pop()
print(state, history)
```

**预期输出**

```text
9 [0, 4, 2]
2 [0, 4]
4 [0]
```


选题关联：来源主题 1（文末列出）。

## 五、括号匹配：每个前缀都要成立

现在输入改成只含圆括号的文本。for mark in text 会依次取得每个字符，与遍历列表的顺序类似。我们用栈保存尚未配对的左括号：遇到左括号就压入，遇到右括号必须有一个更早的左括号可弹出。这里栈里的元素是括号字符，直接使用列表操作，不沿用前面整数接口的 None 数据约定。

循环进行时，栈从底到顶表示当前前缀中尚未闭合的左括号。右括号到来时若栈空，说明它没有前面的搭档，立即返回 False。不能指望后面的左括号补救，因为嵌套要求左括号先出现。所以文本 )( 即使左右数量相等，也在第一个字符处就失败。

扫描结束后还要检查栈是否为空。如果留有左括号，说明有开启但尚未闭合的部分；例如 (() 不能只因扫描过程中没有遇到空栈就判为正确。空文本没有未配对项，本章约定为 True。若字符不是左括号或右括号，本函数明确返回 False，不把任意文本当作算术表达式解析。

下面 ()(()) 可以完整配对，)( 在前缀检查失败，(() 在最终检查失败。只处理一种括号时也能用一个深度计数器解决；这里使用栈是为下一步区分不同括号类型做准备。新增类型以后，仅检查数量就更加不够，还需要让最新未闭合括号的类型与当前右括号一致。

**完整程序**

```python
def balanced(text):
    stack = []
    for mark in text:
        if mark == "(":
            stack.append(mark)
        elif mark == ")":
            if len(stack) == 0:
                return False
            stack.pop()
        else:
            return False
    return len(stack) == 0

print(balanced("()(())"), balanced(")("), balanced("(()"))
```

**预期输出**

```text
True False False
```


选题关联：来源主题 1（文末列出）。

<a id="examples"></a>

## 跟着做：原创例题

### 例题 1

整数栈初始从底到顶为 \[8, 1\]。依次执行压入 5、弹出一次、只读栈顶、再连续弹出三次。使用本章 peek 与 pop\_safe 的空栈约定，列出每次返回值和最终内容，并说明只读操作是否消耗元素。

1. 压入 5 后，底到顶为 8、1、5，新的栈顶为 5。
2. 第一次 pop\_safe 返回 5，栈恢复为 8、1。
3. peek 读取末项 1，但不调用 pop，因此栈仍有两项。
4. 接着两次弹出分别返回 1、8，每次移除一项，之后栈为空。
5. 第三次额外弹出返回 None，空栈保持不变；这是约定的空结果，不是元素 0。

**结果与核对**

返回序列为 5、1、1、8、None；其中第二个值来自只读 peek，随后仍能弹出同一个 1。最终为 \[\]。成功入栈一次、成功出栈三次，与初始两项合计恰好耗尽。

**完整程序**

```python
def peek(stack):
    if len(stack) == 0:
        return None
    return stack[-1]

def pop_safe(stack):
    if len(stack) == 0:
        return None
    return stack.pop()

stack = [8, 1]
stack.append(5)
print(pop_safe(stack), stack)
print(peek(stack), stack)
print(pop_safe(stack), pop_safe(stack), pop_safe(stack), stack)
```

**预期输出**

```text
5 [8, 1]
1 [8, 1]
1 8 None []
```


### 例题 2

用栈检查 (()())，逐个字符给出未配对左括号的数量；再比较 )( 与空文本。为什么仅比较整个文本中两种括号的总数无法替代栈的前缀检查？

1. 开始时栈空。第一个左括号入栈，深度为 1；第二个左括号入栈，深度为 2。
2. 第三个字符为右括号，弹出最近的左括号，深度回到 1。
3. 第四个左括号入栈，深度为 2；第五个右括号弹出，深度为 1。
4. 第六个右括号弹出，深度回到 0；所有前缀都没有无搭档的右括号，结束时也没有剩余项。
5. 对于 )(，第一个字符就要求从空栈配对，立即失败；空文本没有字符要处理，最终空栈判为成功。

**结果与核对**

六个字符处理后的深度为 1、2、1、2、1、0；三个测试结果为 True、False、True。数量相等只是必要条件，)( 的总数相等却违反左括号必须先出现的规则。

**完整程序**

```python
def balanced(text):
    stack = []
    for mark in text:
        if mark == "(":
            stack.append(mark)
        elif mark == ")":
            if len(stack) == 0:
                return False
            stack.pop()
        else:
            return False
    return len(stack) == 0

print(balanced("(()())"), balanced(")("), balanced(""))
```

**预期输出**

```text
True False True
```


<a id="practice"></a>

## 自己做：先完成再看解答

### 练习 1

编写 take\_from\_stack(stack, limit)，最多弹出 limit 个整数，按取出顺序返回新列表。limit 是非负整数；栈可不足 limit 项。对 \[3, 6, 2\] 取 2 项，再从剩余栈取 0 项，并检查空栈取 5 项。

<details>
<summary>提示</summary>

只在取出数量未达到 limit 且栈非空时循环，每轮把一次 pop 的结果追加到新列表。

</details>

<details>
<summary>解答与检查</summary>

第一次得到 \[2, 6\]，原栈剩 \[3\]；取 0 项得到 \[\]，栈仍为 \[3\]。空栈取 5 项也返回 \[\]。若 limit 大于栈长，只会取尽已有元素，不多做一次空 pop；函数会修改输入栈。

**完整程序**

```python
def take_from_stack(stack, limit):
    result = []
    while len(result) < limit and len(stack) > 0:
        result.append(stack.pop())
    return result

stack = [3, 6, 2]
print(take_from_stack(stack, 2), stack)
print(take_from_stack(stack, 0), stack)
print(take_from_stack([], 5))
```

**预期输出**

```text
[2, 6] [3]
[] [3]
[]
```


</details>

### 练习 2

编写 push\_bounded(stack, value, capacity)。容量是正整数，栈长不超过容量；有空位时入栈并返回 True，满时返回 False 且完全不变。容量 2，依次尝试压入 1、4、7，弹出一项后再压入 7。核对每次成功与失败。

<details>
<summary>提示</summary>

先检查是否已满，再进行 append。失败分支必须出现在任何修改之前。

</details>

<details>
<summary>解答与检查</summary>

前三次结果为 True、True、False，栈为 \[1, 4\]；弹出 4 后，压入 7 成功，栈变为 \[1, 7\]。满栈时不能为了容纳新项偷偷删掉栈底，也不能先追加再忘记撤销。

**完整程序**

```python
def push_bounded(stack, value, capacity):
    if len(stack) == capacity:
        return False
    stack.append(value)
    return True

stack = []
print(push_bounded(stack, 1, 2), push_bounded(stack, 4, 2), push_bounded(stack, 7, 2))
print(stack)
removed = stack.pop()
accepted = push_bounded(stack, 7, 2)
print(removed, accepted, stack)
```

**预期输出**

```text
True True False
[1, 4]
4 True [1, 7]
```


</details>

### 练习 3

把匹配函数扩展到圆括号和方括号，其他字符一律返回 False。检查 (\[\])\[\]、(\[)\] 和 (。用一个字典把右括号映射到所需的左括号，说明为什么弹出的必须是最新未配对的类型。

<details>
<summary>提示</summary>

左括号直接压栈；右括号先检查栈非空，再比较弹出项与配对表。结束时仍须栈空。

</details>

<details>
<summary>解答与检查</summary>

结果为 True、False、False。(\[\])\[\] 的每次闭合都匹配栈顶；(\[)\] 在读到右圆括号时，栈顶却是左方括号，立即失败。最后一个测试留下未闭合项。字典 pairs\[mark\] 按右括号键取得应配对的左括号，不遍历整个栈找任意相同项。

**完整程序**

```python
def balanced_pairs(text):
    pairs = {")": "(", "]": "["}
    stack = []
    for mark in text:
        if mark == "(" or mark == "[":
            stack.append(mark)
        elif mark == ")" or mark == "]":
            if len(stack) == 0:
                return False
            if stack.pop() != pairs[mark]:
                return False
        else:
            return False
    return len(stack) == 0

print(balanced_pairs("([])[]"), balanced_pairs("([)]"), balanced_pairs("("))
```

**预期输出**

```text
True False False
```


</details>

<a id="pitfalls"></a>

## 容易混淆的地方

- **把列表左端误当栈顶，或把弹出理解为取最大值。** 本章明确右端为栈顶，只按最后加入且未移出的项判断，与大小无关。
- **把合法的零当成空结果，或未经检查直接读空栈的 -1。** 整数接口用 None 表示空；先检查空状态，不能用返回值的真假代替是否成功。
- **认为 peek 会移除元素，或者撤销时保存了修改后的状态。** peek 只读；撤销历史先保存旧状态再修改，才能按倒序恢复之前的值。
- **只数括号总量，忽略错误前缀、剩余左括号或类型不匹配。** 扫描中确保每个右括号匹配当前栈顶，扫描后确保栈空；两处条件缺一不可。

<a id="self-check"></a>

## 离开这一章前

- [ ] 对同一组含重复值的数据手算入栈出栈，明确每次的顶和底。
- [ ] 从空栈开始压入 0，验证它与空返回 None 能明确区分。
- [ ] 用三次不同增量手算撤销两次的状态，再运行核对历史栈。
- [ ] 分别构造前缀错误、结尾未闭合和类型交错三种括号反例。
- [ ] 验证容量为 1 的栈：压满、拒绝、弹空、再次压入，每次检查失败不改变内容。

## 本章边界

- 普通列表栈没有本章人为设定的固定上限；只有 push\_bounded 使用明确容量约束。
- peek 与 pop\_safe 的 None 空结果只用于整数栈，括号程序另用字符栈；不混用数据契约。
- 括号函数只识别规定的括号字符，不解析表达式、字符串引号或注释。
- 撤销示例只保存整数状态，不实现重做、深拷贝或并发；也不模拟 Python 真实调用栈。

## 选题来源与覆盖

来源含学生报告时，仅将其作为选题线索；具体机制仍需结合后续实验或权威资料核对。

- [大一小学期/Week\_3-Python/docs/readme.md](https://github.com/PKUanonym/REKCARC-TSC-UHT/blob/37cd19f7a9fb80dc846a7016b3fd482ed5fe7cc0/%E5%A4%A7%E4%B8%80%E5%B0%8F%E5%AD%A6%E6%9C%9F/Week_3-Python/docs/readme.md)（已提取可读文本，固定版本 37cd19f7a9fb）
- 主题 1：Python 基础语法的外部学习入口；位置：第 41–80 行。
- 主题 2：从基础语法到工具与应用的建议阅读顺序；位置：第 121–160 行。

## 参考资料与规则核对

上游入口用于确定学习方向；下面的参考资料用于核对语言语义、数据结构或算法分析规则，例题和练习由本项目重新设计。

- [Python 3.11：列表作为栈](https://docs.python.org/3.11/tutorial/datastructures.html#using-lists-as-stacks)：核对 append 与末端 pop 的后进先出行为，空保护为本章自定义接口。
- [Python 3.11：可变序列](https://docs.python.org/3.11/library/stdtypes.html#mutable-sequence-types)：核对 pop 的删除和返回含义；括号、撤销任务与数据均为原创。

**继续学习**：先独立完成自测，再记录仍需回读的步骤。

[上一章：相邻数据怎样连接：单链表与结点引用](07-linked-lists.md) · [下一章：先进入的先处理：队列与循环数组](09-queues.md)

[教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [哈希表与图练习指引](../hash-graphs-practice.md) · [记录自己的学习](../learning-log-template.md)
