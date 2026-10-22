# 从链到层次：树、二叉树与遍历

[返回教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [哈希表与图练习指引](../hash-graphs-practice.md)

[上一章：先分区再递归：快速排序与三路划分](15-quick-sort.md) · [下一章：用大小约束引导查找：二叉搜索树](17-binary-search-trees.md)

[学习目标](#objectives) · [需要的基础](#prerequisites) · [例题](#examples) · [练习](#practice) · [自测](#self-check)

状态：**AI 初稿，可开始试学**。生成模型：Codex 当前会话（未记录具体模型型号）。

本章围绕资料中识别到的知识点重新编写；讲解、数值模型、例题与练习为 AI 原创组织，不是原课程题目或答案。主题出处只说明选题关联，不证明全部推导已经正确。

链表把结点连成一条路，树允许从一个位置分出多条支路。文件目录、表达式和检索索引都可以借助层次关系组织，但具体结构必须先规定清楚。本章从有根树的父子关系进入左右有别的二叉树，用字典引用连接结点，再把前面的递归、栈和队列用于统计与遍历。我们会在同一棵六结点树上比较多种访问顺序，核对高度、返回值和空间口径。树上的值不自动有序；下一章才加入二叉搜索树的大小约束。

<a id="objectives"></a>

## 学完要能做到

- 画出根、父子、祖先、叶子与子树，区别结点身份和结点值。
- 统一按边计数深度与高度，并说明空树返回 -1 的编程约定。
- 实现三种深度优先遍历、显式栈中序和逐层遍历。
- 分别统计访问次数、峰值调用深度、遍历输出与层次工作区。
- 检查镜像、指定深度与完全性，保持有限无环且没有共享子树的前提。

<a id="prerequisites"></a>

## 需要的基础

- 掌握字典结点、None、列表、栈、队列以及第 13、14 章递归组合。
- Python 3.11+；结点值为整数，树有限、无环，非根结点只有一个父结点。
- 深度和高度按边数；根深度为 0，叶子高度为 0，空树高度约定为 -1。涉及 h 的空间上界针对非空树，空树为常数开销。

## 一、从一条链到左右两棵子树

有根树用根作为入口，每个非根结点恰有一个父结点，从根到它只有一条路径。沿父链接往上是祖先，沿子链接往下是后代；没有孩子的结点叫叶子。某个结点连同它的全部后代组成一棵子树。一般树可以有多个孩子，本章选择二叉树作为具体模型：每个结点最多有两个孩子，且明确区分左、右位置。

只有右孩子也是合法二叉树，不能因为缺少左孩子就把它自动移到左边。程序使用 value、left、right 三个字典字段，空子树用 None 表示；整个树为空时根也为 None。每次 tree\_node 调用新建一个字典，之后把已经创建的结点引用写入相应字段。值为零或负数与空引用没有关系。

示例根为 8，左孩子为 3，右孩子为 2；3 的两个孩子为 -1 和 6，2 只有右孩子 9。因此 8 有两个孩子，-1、6、9 是叶子，根到 9 的路径是 8、2、9。这里右孩子比根小完全合法，二叉树首先描述形状，不附带排序规则。两个结点也可以保存相同整数，仍是两个不同对象。

若把同一字典同时接到左右两边，就产生共享子结构；若再指回祖先，就产生环。它们不满足本章输入约定，后面的递归不会自动去重或检测环。检查结构时要按对象身份画边，不能仅凭值判断是否重复。对非空合法树，每个非根结点贡献一条父子边，所以 n 个结点恰有 n-1 条边。

**完整程序**

```python
def tree_node(value):
    return {"value": value, "left": None, "right": None}

def sample_tree():
    root = tree_node(8)
    root["left"] = tree_node(3)
    root["right"] = tree_node(2)
    root["left"]["left"] = tree_node(-1)
    root["left"]["right"] = tree_node(6)
    root["right"]["right"] = tree_node(9)
    return root

root = sample_tree()
print(root["value"], root["left"]["value"], root["right"]["value"])
print(root["left"]["left"]["value"], root["right"]["right"]["value"])
print(root["right"]["left"])
```

**预期输出**

```text
8 3 2
-1 9
None
```


选题关联：来源主题 1（文末列出）。

## 二、一次返回大小、高度和叶子数

深度描述结点离根多远，高度描述从当前结点向下最远能走多远。本章都数边：根深度为 0，示例叶子 9 深度为 2，整树高度为 2。不同教材可能把高度按结点层数计；比较公式前必须先统一单位。为让递推自然成立，程序约定空树高度为 -1，这个值不是一条实际路径长度。

tree\_stats 返回三个量。空树大小为 0、叶子数为 0；非空树大小是左大小加右大小再加根的 1，高度是左右高度的较大者再加 1。叶子必须两个孩子都为空，此时叶子数为 1；其他结点的叶子数才等于两侧相加。因此只有一个孩子的结点并不算叶子，不能用“缺一边”判断。

示例左子树有三个结点、高度 1、两片叶子；右子树有两个结点、高度 1、一片叶子。根组合成大小 6、高度 2、叶子数 3。每次把两个子结果保存在局部名字后复用，避免为了不同统计量反复遍历。算法只读原结点，返回的是新的统计记录。

每个非空结点处理一次，两个空分支也会调用基例。n 个结点有 n+1 个空孩子位置，因此总调用为 2n+1，单位字段操作模型下时间为 Θ(n+1)。高度 h 的非空树最多同时保留 h+1 个非空调用，再加一个空基例，峰值为 h+2；这是 Θ(h+1) 空间，而不是总调用数。退化长链仍可能超过解释器递归限制。

**完整程序**

```python
def tree_node(value):
    return {"value": value, "left": None, "right": None}

def sample_tree():
    root = tree_node(8)
    root["left"] = tree_node(3)
    root["right"] = tree_node(2)
    root["left"]["left"] = tree_node(-1)
    root["left"]["right"] = tree_node(6)
    root["right"]["right"] = tree_node(9)
    return root

def tree_stats(root):
    if root is None:
        return {"size": 0, "height": -1, "leaves": 0}
    left = tree_stats(root["left"])
    right = tree_stats(root["right"])
    height = left["height"]
    if right["height"] > height:
        height = right["height"]
    leaves = left["leaves"] + right["leaves"]
    if root["left"] is None and root["right"] is None:
        leaves = 1
    return {"size": 1 + left["size"] + right["size"],
            "height": 1 + height, "leaves": leaves}

print(tree_stats(sample_tree()))
print(tree_stats(tree_node(-4)))
print(tree_stats(None))
```

**预期输出**

```text
{'size': 6, 'height': 2, 'leaves': 3}
{'size': 1, 'height': 0, 'leaves': 1}
{'size': 0, 'height': -1, 'leaves': 0}
```


选题关联：来源主题 1（文末列出）。

## 三、前序、中序、后序只改变处理根的时机

深度优先遍历先深入一棵子树，再返回处理另一棵。固定先左后右后，处理当前根有三个位置：在左右子树之前是前序，在两棵子树之间是中序，在两棵子树之后是后序。顺序名称说的是“根何时加入输出”，不表示改变孩子链接，也不表示结点按数值大小访问。

对示例，前序先输出 8，再完整走 3 那一侧，最后走 2 那一侧，得到 8、3、-1、6、2、9。中序先得到左侧 -1、3、6，再是 8，最后为 2、9；后序则等左右完成才加入根，得到 -1、6、3、9、2、8。中序中的 8 后面出现 2，直接说明任意二叉树的中序不一定有序。

程序把 order 限定为 pre、in、post 三种字符串。tree\_walk 共享一个 output 列表，在对应位置 append；外层 traversal 每次新建空列表，因此多次调用不会把旧结果接进去。空结点直接返回，避免读取 None 的字段。若传其他字符串，本实现不主动报错，所以调用者必须遵守约定。

三种顺序都对每个结点输出一次，时间为 Θ(n+1)。结果列表占 Θ(n+1)，递归辅助栈另占 O(h+1)；若只讨论不含输出的空间，要明确排除哪一部分。这里不用“左结果加根加右结果”的反复列表拼接，否则长链可能引入二次复制成本。前序适合先记录父位置，后序适合先拿到两个子答案，中序会在下一章用于有序枚举。

**完整程序**

```python
def tree_node(value):
    return {"value": value, "left": None, "right": None}

def sample_tree():
    root = tree_node(8)
    root["left"] = tree_node(3)
    root["right"] = tree_node(2)
    root["left"]["left"] = tree_node(-1)
    root["left"]["right"] = tree_node(6)
    root["right"]["right"] = tree_node(9)
    return root

def tree_walk(root, order, output):
    if root is None:
        return
    if order == "pre":
        output.append(root["value"])
    tree_walk(root["left"], order, output)
    if order == "in":
        output.append(root["value"])
    tree_walk(root["right"], order, output)
    if order == "post":
        output.append(root["value"])

def traversal(root, order):
    output = []
    tree_walk(root, order, output)
    return output

root = sample_tree()
print(traversal(root, "pre"))
print(traversal(root, "in"))
print(traversal(root, "post"))
print(traversal(None, "in"))
```

**预期输出**

```text
[8, 3, -1, 6, 2, 9]
[-1, 3, 6, 8, 2, 9]
[-1, 6, 3, 9, 2, 8]
[]
```


选题关联：来源主题 1（文末列出）。

## 四、用显式栈保存尚未处理的祖先

中序需要先完成左边，但到达最左端后还得知道回到哪个祖先。递归用调用栈保存这个等待关系；循环版本把等待的结点放进列表 stack。current 表示还要向左探索的入口。只要 current 非空就把它压栈并走左边，直到遇到空位置，才弹出最近的等待者并输出它。

输出结点之后把 current 改成它的右孩子，然后重复相同过程。外层循环的条件是“current 非空或 stack 非空”，二者不能同时漏掉任何一个。只有 current 为空时，栈里仍可能有根或其他祖先；只有栈为空时，当前右子树也仍可能有工作。pop 从列表末尾取出，符合后进先出，不从表头删除。

以示例开头为例，依次压入 8、3、-1，遇空后弹出 -1；接着弹出 3，再转到它的右孩子 6。等左侧全部结束才弹出 8，随后探索右侧 2、9。每个结点恰好入栈一次、出栈一次，所以循环层层嵌套仍只有线性总工作，不应直接把两个 while 判成平方时间。

显式栈最多保存一条祖先路径，容量上界为 h+1，结果仍需线性空间。它避免 Python 的递归调用深度限制，但没有把所有树都变成常数空间；左倾长链会把整条路径压入栈。列表扩容按摊还成本计算，完整遍历为 Θ(n+1)。链接和字段都只读，验证时应检查输出以及原来的全部引用关系。

**完整程序**

```python
def tree_node(value):
    return {"value": value, "left": None, "right": None}

def sample_tree():
    root = tree_node(8)
    root["left"] = tree_node(3)
    root["right"] = tree_node(2)
    root["left"]["left"] = tree_node(-1)
    root["left"]["right"] = tree_node(6)
    root["right"]["right"] = tree_node(9)
    return root

def inorder_iterative(root):
    result = []
    stack = []
    current = root
    while current is not None or len(stack) > 0:
        while current is not None:
            stack.append(current)
            current = current["left"]
        current = stack.pop()
        result.append(current["value"])
        current = current["right"]
    return result

print(inorder_iterative(sample_tree()))
print(inorder_iterative(None))
```

**预期输出**

```text
[-1, 3, 6, 8, 2, 9]
[]
```


选题关联：来源主题 1（文末列出）。

## 五、逐层访问与完全二叉树的形状

广度优先遍历先访问深度较小的结点，同一深度按从左到右排列。本程序让 current 保存整层结点，处理它们时把存在的左、右孩子依次加入 following。完整处理当前层后才换到下一层，相当于按层批量使用先进先出的等待顺序。示例三层分别是 \[8\]、\[3,2\]、\[-1,6,9\]，空树没有任何层。

每个结点加入一层、处理一次，时间为 Θ(n+1)。设最宽一层有 w 个结点，current 与 following 同时存在时各不超过 w，工作区为 O(w+1)；返回的所有层列表合计仍占 Θ(n+1)。不能把包含输出的总空间也写成 O(w)。这里不使用从列表头部反复 pop 的做法，避免每次搬移后续元素。

二叉树的每一层最多有前一层两倍的结点，因此深度 d 最多有 2 的 d 次方个结点。完全二叉树要求最深层之前都填满，最深层从左到右连续占位；每一层都填满则是完美二叉树。术语在不同教材中可能不同，这里以这两条具体形状规则为准。完全不等于每个内部结点都有两个孩子。

示例在 2 的左位置留空，却在其右位置放了 9，所以不是完全二叉树。把 9 移到左位置后，六个位置按层连续，就满足完全性。非空完全二叉树满足 2 的 h 次方不超过 n，n 小于 2 的 h+1 次方，因此 h 为 log₂n 向下取整；任意二叉树却可退化成高度 n-1 的链。堆章节将利用完全形状保证对数高度。

**完整程序**

```python
def tree_node(value):
    return {"value": value, "left": None, "right": None}

def sample_tree():
    root = tree_node(8)
    root["left"] = tree_node(3)
    root["right"] = tree_node(2)
    root["left"]["left"] = tree_node(-1)
    root["left"]["right"] = tree_node(6)
    root["right"]["right"] = tree_node(9)
    return root

def tree_levels(root):
    result = []
    if root is None:
        return result
    current = [root]
    while len(current) > 0:
        values = []
        following = []
        for node in current:
            values.append(node["value"])
            if node["left"] is not None:
                following.append(node["left"])
            if node["right"] is not None:
                following.append(node["right"])
        result.append(values)
        current = following
    return result

print(tree_levels(sample_tree()))
print(tree_levels(tree_node(0)))
print(tree_levels(None))
```

**预期输出**

```text
[[8], [3, 2], [-1, 6, 9]]
[[0]]
[]
```


选题关联：来源主题 1（文末列出）。

<a id="examples"></a>

## 跟着做：原创例题

### 例题 1

根为 4、左孩子为 7、右孩子为 1，两个孩子都为叶子。分别记录进入非空调用、中序处理、离开非空调用，推导打印顺序、实际调用总数和峰值深度。

1. 根 4 进入后先调用左边；7 进入，两个空分支分别直接返回。
2. 7 在左右空调用之间记录 visit，离开后才轮到根的 visit。
3. 随后进入右叶子 1，完成它的 enter、visit、leave，最后根离开。
4. 三个非空结点各打印三条事件，共九条；空基例没有打印，但四次调用仍要计算。
5. 总调用为 7，最深同时保留根、叶子和空基例三个调用，高度则只有一条边。

**结果与核对**

事件顺序为 enter4、enter7、visit7、leave7、visit4、enter1、visit1、leave1、leave4。打印条数 9、调用数 7、峰值深度 3 描述不同对象，不应混用。

**完整程序**

```python
def tree_node(value):
    return {"value": value, "left": None, "right": None}

def inorder_events(root, events):
    if root is None:
        return
    events.append(["enter", root["value"]])
    inorder_events(root["left"], events)
    events.append(["visit", root["value"]])
    inorder_events(root["right"], events)
    events.append(["leave", root["value"]])

root = tree_node(4)
root["left"] = tree_node(7)
root["right"] = tree_node(1)
events = []
inorder_events(root, events)
for event in events:
    print(event)
```

**预期输出**

```text
['enter', 4]
['enter', 7]
['visit', 7]
['leave', 7]
['visit', 4]
['enter', 1]
['visit', 1]
['leave', 1]
['leave', 4]
```


### 例题 2

把六结点示例树原地镜像：每个结点交换左右孩子。保存原来值为 3 的左孩子引用，检查镜像后的中序、该引用的新位置，以及再镜像一次是否恢复原链接。

1. 先保存旧左引用，再让左指向旧右、右指向旧左，避免覆盖后丢失入口。
2. 对交换后的两棵子树分别继续镜像；空入口直接返回 None。
3. 根仍是同一个对象，原来值为 3 的对象成为根的右孩子。
4. 中序从原来的 \[-1,3,6,8,2,9\] 变成 \[9,2,8,6,3,-1\]，大小、高度和叶子数不变。
5. 再次对同一入口镜像，每条左右链接交换两次，恢复原来的结构和对象身份。

**结果与核对**

一次镜像改变链接、不新建结点，返回原入口。二次镜像后的中序恢复，原来的左孩子引用也回到左边；核对全部链接比只看重复值序列更可靠。算法时间 Θ(n+1)，递归辅助空间 O(h+1)。

**完整程序**

```python
def tree_node(value):
    return {"value": value, "left": None, "right": None}

def sample_tree():
    root = tree_node(8)
    root["left"] = tree_node(3)
    root["right"] = tree_node(2)
    root["left"]["left"] = tree_node(-1)
    root["left"]["right"] = tree_node(6)
    root["right"]["right"] = tree_node(9)
    return root

def tree_walk(root, order, output):
    if root is None:
        return
    if order == "pre":
        output.append(root["value"])
    tree_walk(root["left"], order, output)
    if order == "in":
        output.append(root["value"])
    tree_walk(root["right"], order, output)
    if order == "post":
        output.append(root["value"])

def traversal(root, order):
    output = []
    tree_walk(root, order, output)
    return output

def mirror_tree(root):
    if root is None:
        return None
    saved = root["left"]
    root["left"] = root["right"]
    root["right"] = saved
    mirror_tree(root["left"])
    mirror_tree(root["right"])
    return root

root = sample_tree()
saved = root["left"]
mirror_tree(root)
print(traversal(root, "in"), root["right"] is saved)
mirror_tree(root)
print(traversal(root, "in"), root["left"] is saved)
```

**预期输出**

```text
[9, 2, 8, 6, 3, -1] True
[-1, 3, 6, 8, 2, 9] True
```


<a id="practice"></a>

## 自己做：先完成再看解答

### 练习 1

写 leaf\_sum(root)，只累加叶子的整数值。检查六结点示例、单结点 -4 和空树，并说明为什么只缺一个孩子的结点不能直接加入总和。

<details>
<summary>提示</summary>

先判空，再判左右同时为空；其余情况组合左右子答案。

</details>

<details>
<summary>解答与检查</summary>

示例叶子为 -1、6、9，总和为 14；单结点结果 -4，空树为 0。值为 2 的结点仍有右孩子 9，不是叶子。每个结点至多处理一次，时间 Θ(n+1)，辅助栈 O(h+1)，负数不影响叶子的结构判断。

**完整程序**

```python
def tree_node(value):
    return {"value": value, "left": None, "right": None}

def sample_tree():
    root = tree_node(8)
    root["left"] = tree_node(3)
    root["right"] = tree_node(2)
    root["left"]["left"] = tree_node(-1)
    root["left"]["right"] = tree_node(6)
    root["right"]["right"] = tree_node(9)
    return root

def leaf_sum(root):
    if root is None:
        return 0
    if root["left"] is None and root["right"] is None:
        return root["value"]
    return leaf_sum(root["left"]) + leaf_sum(root["right"])

print(leaf_sum(sample_tree()))
print(leaf_sum(tree_node(-4)), leaf_sum(None))
```

**预期输出**

```text
14
-4 0
```


</details>

### 练习 2

写 nodes\_at\_depth(root, depth)，按从左到右返回指定深度的值。depth 为整数，负数或超过高度时返回空列表；检查示例深度 0、2、3、-1。不要为了取一层先保存全部层的输出。

<details>
<summary>提示</summary>

逐层推进，只保留当前与下一层。达到目标后才提取值；树先耗尽也可以结束。

</details>

<details>
<summary>解答与检查</summary>

结果依次为 \[8\]、\[-1,6,9\]、\[\]、\[\]。根深度为 0，depth 不是从 1 开始的层号。算法只展开目标层之前的结点，最坏线性时间；工作区受层宽约束，另外计入返回列表。输入值重复时，每个结点仍占一个结果位置。

**完整程序**

```python
def tree_node(value):
    return {"value": value, "left": None, "right": None}

def sample_tree():
    root = tree_node(8)
    root["left"] = tree_node(3)
    root["right"] = tree_node(2)
    root["left"]["left"] = tree_node(-1)
    root["left"]["right"] = tree_node(6)
    root["right"]["right"] = tree_node(9)
    return root

def nodes_at_depth(root, depth):
    if root is None or depth < 0:
        return []
    current = [root]
    level = 0
    while level < depth and len(current) > 0:
        following = []
        for node in current:
            if node["left"] is not None:
                following.append(node["left"])
            if node["right"] is not None:
                following.append(node["right"])
        current = following
        level = level + 1
    result = []
    for node in current:
        result.append(node["value"])
    return result

root = sample_tree()
for depth in [0, 2, 3, -1]:
    print(nodes_at_depth(root, depth))
```

**预期输出**

```text
[8]
[-1, 6, 9]
[]
[]
```


</details>

### 练习 3

写 is\_complete(root)，按最深层之前填满、最深层靠左的规则检查完全二叉树，约定空树也返回 True。检查原示例，以及把 9 从右位置移到左位置的结果。

<details>
<summary>提示</summary>

按层访问所有孩子位置，包括 None。首次空位置之后若再遇到非空结点，就有靠左填充的缺口。

</details>

<details>
<summary>解答与检查</summary>

原示例返回 False，移动后返回 True，空树返回 True。只把非空孩子入队会丢失缺口信息。本实现用列表和递增游标保存等待顺序，处理过的前缀仍保留，最坏 Θ(n+1) 时间和空间；不能因为逻辑队列可能较窄就把实际存储写成 O(w)。

**完整程序**

```python
def tree_node(value):
    return {"value": value, "left": None, "right": None}

def sample_tree():
    root = tree_node(8)
    root["left"] = tree_node(3)
    root["right"] = tree_node(2)
    root["left"]["left"] = tree_node(-1)
    root["left"]["right"] = tree_node(6)
    root["right"]["right"] = tree_node(9)
    return root

def is_complete(root):
    queue = [root]
    front = 0
    gap = False
    while front < len(queue):
        node = queue[front]
        front = front + 1
        if node is None:
            gap = True
        else:
            if gap:
                return False
            queue.append(node["left"])
            queue.append(node["right"])
    return True

root = sample_tree()
print(is_complete(root))
root["right"]["left"] = root["right"]["right"]
root["right"]["right"] = None
print(is_complete(root), is_complete(None))
```

**预期输出**

```text
False
True True
```


</details>

<a id="pitfalls"></a>

## 容易混淆的地方

- **把相同的值当成同一个结点，或把共享孩子当作普通树。** 树的约束针对对象与链接；每个非根对象只有一个父位置，值可以重复。
- **把高度、层数、递归峰值和事件条数写成同一个数。** 先明确边数约定，再分别计空基例、非空调用与打印事件。
- **把中序遍历自动当成有序序列。** 一般二叉树没有大小约束，示例的中序就不是递增。
- **把返回的所有层列表或未释放的队列前缀忽略不计。** 空间要跟实际仍存活对象对应，输出与辅助状态分别说明。

<a id="self-check"></a>

## 离开这一章前

- [ ] 画出六结点例子的五条边，并标注深度、高度和叶子。
- [ ] 遮住输出手算三种遍历及九条进入返回事件。
- [ ] 分别检查空树、单结点、左右倾链和重复值树。
- [ ] 用对象身份确认镜像两次恢复每条链接，普通遍历没有修改输入。
- [ ] 解释完全树的左侧缺口规则，以及层次输出和工作区的区别。

## 本章边界

- 输入必须已经是有限、无环且没有共享子树的合法二叉树，本章函数不负责识别任意对象图。
- 递归示例采用小树；长链应考虑显式栈，不提高解释器限制。
- 未实现一般多叉树、表达式解析或自动结构可视化，整数值不包含大小约束。
- 时间分析采用单位引用与整数操作，动态列表按摊还成本核算。

## 选题来源与覆盖

来源含学生报告时，仅将其作为选题线索；具体机制仍需结合后续实验或权威资料核对。

- [大一小学期/Week\_3-Python/docs/readme.md](https://github.com/PKUanonym/REKCARC-TSC-UHT/blob/37cd19f7a9fb80dc846a7016b3fd482ed5fe7cc0/%E5%A4%A7%E4%B8%80%E5%B0%8F%E5%AD%A6%E6%9C%9F/Week_3-Python/docs/readme.md)（已提取可读文本，固定版本 37cd19f7a9fb）
- 主题 1：Python 基础语法的外部学习入口；位置：第 41–80 行。
- 主题 2：从基础语法到工具与应用的建议阅读顺序；位置：第 121–160 行。

## 参考资料与规则核对

上游入口用于确定学习方向；下面的参考资料用于核对语言语义、数据结构或算法分析规则，例题和练习由本项目重新设计。

- [Open Data Structures：二叉树与遍历](https://opendatastructures.org/ods-java/6_1_BinaryTree_Basic_Binary.html)：核对边计高度、空基例与遍历概念；本章用原创字典模型、数值和轨迹，不移植 Java 实现。
- [NIST DADS：二叉树](https://xlinux.nist.gov/dads/HTML/binarytree.html)：核对空树、根和左右子树的递归定义；本章补充对象身份前提。
- [NIST DADS：完全二叉树](https://xlinux.nist.gov/dads/HTML/completeBinaryTree.html)：核对层填满与最深层靠左的形状规则；程序使用零基下标，不混用参考中的一起始索引。

**继续学习**：先独立完成自测，再记录仍需回读的步骤。

[上一章：先分区再递归：快速排序与三路划分](15-quick-sort.md) · [下一章：用大小约束引导查找：二叉搜索树](17-binary-search-trees.md)

[教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [哈希表与图练习指引](../hash-graphs-practice.md) · [记录自己的学习](../learning-log-template.md)
