# 用大小约束引导查找：二叉搜索树

[返回教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md)

[上一章：从链到层次：树、二叉树与遍历](16-trees.md) · [下一章：让最值留在根部：二叉堆与优先队列](18-heaps.md)

[学习目标](#objectives) · [需要的基础](#prerequisites) · [例题](#examples) · [练习](#practice) · [自测](#self-check)

状态：**AI 初稿，可开始试学**。生成模型：Codex 当前会话（未记录具体模型型号）。

本章围绕资料中识别到的知识点重新编写；讲解、数值模型、例题与练习为 AI 原创组织，不是原课程题目或答案。主题出处只说明选题关联，不证明全部推导已经正确。

上一章的二叉树只规定左右位置，查找一个值通常仍要扫描许多结点。本章给每棵子树加入大小约束，让一次比较能够排除整侧范围，形成二叉搜索树。我们用整数集合说明接口：每个不同键最多出现一次，重复插入保持原样，删除不存在的键也保持原样。随后追踪插入和三种删除情况，再比较同一组键以不同顺序插入后的高度。这里实现普通、不自动平衡的树，因此所有查找与修改成本都先用实际高度表示。

<a id="objectives"></a>

## 学完要能做到

- 用所有后代的范围描述搜索树约束，识别只看直接孩子的错误。
- 正确查找、插入和删除整数键，接回操作返回的新根。
- 用中序枚举、向下候选搜索和范围剪枝回答有序查询。
- 解释双孩子删除时的后继选择、链接更新与结点身份变化。
- 以高度分析最坏成本，并从严格递增列表一次构造高度受控的树。

<a id="prerequisites"></a>

## 需要的基础

- 掌握第 16 章二叉树、字典引用、递归返回、中序遍历和高度口径。
- 输入是有限无环、无共享子树的结构；除验证练习外，树操作入口必须满足搜索树约束。
- 键是整数，None 仅作空树或没有结果；本章使用不含重复键的集合语义。涉及 h 的复杂度针对非空树，空树操作为常数成本。
- 示例为 Python 3.11+，递归修改用于小树，不包含旋转或平衡维护。

## 一、大小约束必须覆盖整棵子树

二叉搜索树在每个结点保存 key、left、right。对任何结点，左子树所有键严格小于当前键，右子树所有键严格大于当前键，两侧自身也要满足同样条件。严格比较体现本章不存重复键的选择。其他实现可以合并计数或约定相等键的位置，但插入、查找、删除和验证必须使用同一套规则。

约束针对全部后代，不能只检查两个直接孩子。例如根 12 的左孩子是 5，5 的右孩子是 14；14 大于 5 看起来符合局部关系，却仍位于 12 的左子树，因此整树非法。祖先传下来的范围不能因为走到了下一层就忘掉。合法示例的左侧是 2、5、9，右侧是 15、18、21。

查找从根开始：相等就返回该键，目标较小只进入左侧，目标较大只进入右侧。寻找 15 时依次看 12、18、15；寻找 6 时看 12、5、9，随后落到空左位置，返回 None。排除另一侧的理由是全局范围约束，不是另一侧恰好看起来离目标更远；因此不能把普通二叉树直接交给这个函数。

循环每步沿一条孩子边下降，不修改结点。高度为 h 的非空树最多访问 h+1 个非空结点，最坏时间 O(h+1)，辅助状态 O(1)。程序一次访问可能做相等和大小两次比较，所以路径长度是结点访问数，不冒充精确比较数。返回的是整数键或 None，尚不支持以 None 为合法键，也不把结点引用作为稳定的对外句柄。

**完整程序**

```python
def bst_node(key):
    return {"key": key, "left": None, "right": None}

def sample_bst():
    root = bst_node(12)
    root["left"] = bst_node(5)
    root["right"] = bst_node(18)
    root["left"]["left"] = bst_node(2)
    root["left"]["right"] = bst_node(9)
    root["right"]["left"] = bst_node(15)
    root["right"]["right"] = bst_node(21)
    return root

def bst_find(root, key):
    current = root
    while current is not None:
        if key == current["key"]:
            return current["key"]
        if key < current["key"]:
            current = current["left"]
        else:
            current = current["right"]
    return None

root = sample_bst()
print(bst_find(root, 15), bst_find(root, 6))
print(bst_find(None, 15))
```

**预期输出**

```text
15 None
None
```


选题关联：来源主题 1（文末列出）。

## 二、插入后要把子树的新根接回来

插入沿用查找路径，直到空位置才建立新结点。bst\_insert 的承诺是：把 key 加入以 root 为入口的集合，并返回修改后这棵子树的入口。空树会变成一个新结点；非空树通常继续返回原根。因此调用者统一写成把返回值重新赋给 root，不能因为某次插入恰好不换根，就忽略这个接口约定。

向左递归时，返回的新入口要写回当前的 left，向右同理。只调用子函数而不接返回值，插入空孩子时建立的结点就无法从原树到达。到达相等键时本实现不分配结点、不增加副本，直接返回原根。重复插入 9 后，集合仍只有一个 9，结点数也不变。

用 \[12,5,18,2,9,15,21,9\] 依次构造，前七个键形成示例树，最后一次走到原来的 9 即结束。输入顺序决定形状，值集合相同并不意味着父子关系相同。整数列表只被读取，树中每个新键对应一次新的字典分配；树的整个存储为 Θ(n)，不是辅助调用栈的大小。

一次插入至多访问 h+1 个原有结点，再到空位置时分配新结点，时间和递归辅助空间均为 O(h+1)。若每次都插入当前最大值，新结点会接在最右端；连续构造 n 个递增键时，之前的访问数为 0、1、2 直到 n-1，相加为二次量级。不能把单次 O(h) 写完后直接断言建树为 O(n log n)，因为 h 也随插入顺序变化。

**完整程序**

```python
def bst_node(key):
    return {"key": key, "left": None, "right": None}

def bst_insert(root, key):
    if root is None:
        return bst_node(key)
    if key < root["key"]:
        root["left"] = bst_insert(root["left"], key)
    elif key > root["key"]:
        root["right"] = bst_insert(root["right"], key)
    return root

def bst_from_keys(keys):
    root = None
    for key in keys:
        root = bst_insert(root, key)
    return root

def bst_collect(root, output):
    if root is None:
        return
    bst_collect(root["left"], output)
    output.append(root["key"])
    bst_collect(root["right"], output)

def bst_keys(root):
    result = []
    bst_collect(root, result)
    return result

keys = [12, 5, 18, 2, 9, 15, 21, 9]
root = bst_from_keys(keys)
print(bst_keys(root))
print(keys)
print(bst_keys(bst_insert(None, 0)))
```

**预期输出**

```text
[2, 5, 9, 12, 15, 18, 21]
[12, 5, 18, 2, 9, 15, 21, 9]
[0]
```


选题关联：来源主题 1（文末列出）。

## 三、中序有序与只保留一个候选的查询

在合法搜索树中，中序先输出左侧所有较小键，再输出根，最后输出右侧所有较大键。两侧递归也有序，所以整段结果严格递增。这是搜索树约束与中序顺序共同得到的性质；中序算法本身没有做交换或排序。枚举 n 个键至少要输出 n 项，完整枚举的时间为 Θ(n+1)，结果空间为线性，调用栈另计 O(h+1)。

并非所有有序查询都需要先生成整份中序列表。floor 查询要求找不超过目标的最大键。当前键等于目标就可结束；当前键比目标大时，右侧也全部太大，只能往左；当前键较小时，它成为一个可行候选，但右侧仍可能存在更大的可行键，因此保存候选后继续往右。

对目标 16，从 12 出发先记候选 12，遇 18 改走左边，到 15 后更新候选为 15，再沿右空链接结束。目标 1 没有候选，返回 None；目标 12 则直接返回 12。每次丢弃的区域要么全不合条件，要么不可能超过已经保存的候选，这才说明最终候选最优。沿最左或最右路径也可分别找到最小和最大键。

floor 循环只保存当前结点与候选，最坏 O(h+1) 时间、O(1) 辅助空间。空输入立即返回 None。它不把相邻键误认为相邻内存位置，也不要求整数连续；负数、零或很大的键都按同一个比较规则工作。后面的范围练习会保留可能有答案的分支，并把输出数量计入成本。

**完整程序**

```python
def bst_node(key):
    return {"key": key, "left": None, "right": None}

def sample_bst():
    root = bst_node(12)
    root["left"] = bst_node(5)
    root["right"] = bst_node(18)
    root["left"]["left"] = bst_node(2)
    root["left"]["right"] = bst_node(9)
    root["right"]["left"] = bst_node(15)
    root["right"]["right"] = bst_node(21)
    return root

def bst_collect(root, output):
    if root is None:
        return
    bst_collect(root["left"], output)
    output.append(root["key"])
    bst_collect(root["right"], output)

def bst_keys(root):
    result = []
    bst_collect(root, result)
    return result

def bst_floor(root, key):
    candidate = None
    current = root
    while current is not None:
        if current["key"] == key:
            return current["key"]
        if current["key"] > key:
            current = current["left"]
        else:
            candidate = current["key"]
            current = current["right"]
    return candidate

root = sample_bst()
print(bst_keys(root))
print(bst_floor(root, 16), bst_floor(root, 1), bst_floor(root, 12))
```

**预期输出**

```text
[2, 5, 9, 12, 15, 18, 21]
15 None 12
```


选题关联：来源主题 1（文末列出）。

## 四、删除分为零个、一个和两个孩子

删除也返回修改后的子树入口。目标不存在时，走到空位置返回 None，沿路接回原有分支，集合和对象关系保持不变。找到目标后，若没有左孩子，就直接返回右孩子；右边也空时这正好返回 None。若左边存在而右边为空，则返回左孩子。父结点接回这个返回值，就绕过了被移除的结点。

两个孩子都存在时不能随便选一个孩子覆盖根，否则另一侧会丢失。这里找右子树的最小键，也叫当前键的中序后继：先走右边，再一直走左边。它大于当前键，又不大于右侧其他键；本章键唯一，所以复制这个键到当前位置后，只需在右子树中删去原来的后继键，就恢复严格有序关系。

后继没有左孩子，但可能有右孩子。递归删除它时会把其右孩子接给原来的父结点，不能直接把整个位置清空。示例删除 12，后继是 15，得到键集合 \[2,5,9,15,18,21\]。删除之后仍须把返回入口赋给 root，尤其是原根只有一个孩子或根就是唯一结点的情况。

本实现复制的是整数键，两个孩子的目标结点对象保留，但其中 key 会改变；被摘除的是右侧后继对象。因此外部保存的某个结点引用并不保证永久代表同一个键。字典离开树也不等于强制销毁，其他名字可能仍引用它。搜索、找后继和摘除沿同一高度范围的路径完成，总时间 O(h+1)、辅助栈 O(h+1)，并不自动恢复平衡。

**完整程序**

```python
def bst_node(key):
    return {"key": key, "left": None, "right": None}

def sample_bst():
    root = bst_node(12)
    root["left"] = bst_node(5)
    root["right"] = bst_node(18)
    root["left"]["left"] = bst_node(2)
    root["left"]["right"] = bst_node(9)
    root["right"]["left"] = bst_node(15)
    root["right"]["right"] = bst_node(21)
    return root

def bst_delete(root, key):
    if root is None:
        return None
    if key < root["key"]:
        root["left"] = bst_delete(root["left"], key)
    elif key > root["key"]:
        root["right"] = bst_delete(root["right"], key)
    else:
        if root["left"] is None:
            return root["right"]
        if root["right"] is None:
            return root["left"]
        successor = root["right"]
        while successor["left"] is not None:
            successor = successor["left"]
        root["key"] = successor["key"]
        root["right"] = bst_delete(root["right"], successor["key"])
    return root

def bst_collect(root, output):
    if root is None:
        return
    bst_collect(root["left"], output)
    output.append(root["key"])
    bst_collect(root["right"], output)

def bst_keys(root):
    result = []
    bst_collect(root, result)
    return result

root = sample_bst()
root = bst_delete(root, 12)
print(bst_keys(root), root["key"])
root = bst_delete(root, 99)
print(bst_keys(root))
print(bst_delete(None, 0))
```

**预期输出**

```text
[2, 5, 9, 15, 18, 21] 15
[2, 5, 9, 15, 18, 21]
None
```


选题关联：来源主题 1（文末列出）。

## 五、用真实路径看高度与最坏成本

搜索树没有要求每次比较把剩余结点数量减半。二分数组可以通过中间下标保证规模缩小，普通搜索树却由已经形成的形状决定下一侧大小。七个键以 \[12,5,18,2,9,15,21\] 插入时高度为 2；以 \[2,5,9,12,15,18,21\] 插入时高度为 6，两者中序完全相同，但寻找 21 的路径分别包含三个与七个结点。

下面的报告函数把真正经过的键依次放进 visited，并返回 found。找到目标或走到 None 就结束，记录不会改变搜索方向。对平衡形状，寻找 21 经过 12、18、21；对长链，则必须逐个经过所有七个键。报告多了路径列表，所以空间为 O(h+1)，前面普通循环查找自身仍只需常数辅助状态。

对 n 个非空结点，最坏高度是 n-1，查找、插入和删除都可能花线性时间，递归版本还可能触及解释器深度限制。若结构确实保持对数高度，这些操作才有对数上界。随机插入需要另外说明输入概率模型；不能把一次打乱顺序得到的较浅树当成任意后续更新的保证。

从已有严格递增序列按中点递归构造，可以一次获得高度受控的初始树；练习会实现这一点。它不意味着之后任意插入和删除仍保持平衡。真正持续维护高度需要额外规则，例如后续可以学习旋转与平衡搜索树。本章先把约束、返回入口和成本讲清，用可核对的路径解释何时快、何时退化。

**完整程序**

```python
def bst_node(key):
    return {"key": key, "left": None, "right": None}

def bst_insert(root, key):
    if root is None:
        return bst_node(key)
    if key < root["key"]:
        root["left"] = bst_insert(root["left"], key)
    elif key > root["key"]:
        root["right"] = bst_insert(root["right"], key)
    return root

def bst_from_keys(keys):
    root = None
    for key in keys:
        root = bst_insert(root, key)
    return root

def bst_find_report(root, key):
    visited = []
    current = root
    while current is not None:
        visited.append(current["key"])
        if key == current["key"]:
            return {"found": True, "visited": visited}
        if key < current["key"]:
            current = current["left"]
        else:
            current = current["right"]
    return {"found": False, "visited": visited}

for keys in [[12, 5, 18, 2, 9, 15, 21], [2, 5, 9, 12, 15, 18, 21]]:
    print(bst_find_report(bst_from_keys(keys), 21))
print(bst_find_report(None, 0))
```

**预期输出**

```text
{'found': True, 'visited': [12, 18, 21]}
{'found': True, 'visited': [2, 5, 9, 12, 15, 18, 21]}
{'found': False, 'visited': []}
```


选题关联：来源主题 1（文末列出）。

<a id="examples"></a>

## 跟着做：原创例题

### 例题 1

依次插入 \[12,5,18,2,9,15,21,16\]，保存根引用，然后删除 12。后继是否可能带孩子？列出新中序、根键和 18 的左孩子，并说明原根引用发生了什么。

1. 查到根 12 有两个孩子，进入右侧 18，再向左找到最小键 15。
2. 15 没有左孩子，但有右孩子 16；后继不是一定为叶子。
3. 把 15 复制到原根，再从原右子树删除键 15。
4. 删除原 15 时返回它的右孩子 16，接回 18 的 left；21 分支保持原样。
5. 原根对象仍在，但 key 由 12 变成 15；可达对象数减少一个，剩余键严格递增。

**结果与核对**

新中序为 \[2,5,9,15,16,18,21\]，根键为 15，18 的左孩子为 16。保存的根引用仍与新根相同，说明删除的是集合中的键，不承诺按键固定对象身份。

**完整程序**

```python
def bst_node(key):
    return {"key": key, "left": None, "right": None}

def bst_insert(root, key):
    if root is None:
        return bst_node(key)
    if key < root["key"]:
        root["left"] = bst_insert(root["left"], key)
    elif key > root["key"]:
        root["right"] = bst_insert(root["right"], key)
    return root

def bst_from_keys(keys):
    root = None
    for key in keys:
        root = bst_insert(root, key)
    return root

def bst_delete(root, key):
    if root is None:
        return None
    if key < root["key"]:
        root["left"] = bst_delete(root["left"], key)
    elif key > root["key"]:
        root["right"] = bst_delete(root["right"], key)
    else:
        if root["left"] is None:
            return root["right"]
        if root["right"] is None:
            return root["left"]
        successor = root["right"]
        while successor["left"] is not None:
            successor = successor["left"]
        root["key"] = successor["key"]
        root["right"] = bst_delete(root["right"], successor["key"])
    return root

def bst_collect(root, output):
    if root is None:
        return
    bst_collect(root["left"], output)
    output.append(root["key"])
    bst_collect(root["right"], output)

def bst_keys(root):
    result = []
    bst_collect(root, result)
    return result

root = bst_from_keys([12, 5, 18, 2, 9, 15, 21, 16])
saved = root
root = bst_delete(root, 12)
print(bst_keys(root))
print(root["key"], root["right"]["left"]["key"], root is saved)
```

**预期输出**

```text
[2, 5, 9, 15, 16, 18, 21]
15 16 True
```


### 例题 2

从 \[6,2,9,4,4\] 构造集合，依次删除 9、2、6、4、99。每次接回新根，输出中序，说明哪一步删除叶子、哪一步由唯一孩子接替，以及重复插入 4 的结果。

1. 重复插入 4 不增加结点，初始中序为 \[2,4,6,9\]。
2. 9 是叶子，删除后根的右入口变为 None，剩余 \[2,4,6\]。
3. 2 只有右孩子 4，用 4 接替根的左入口，剩余 \[4,6\]。
4. 6 只有左孩子 4，删除根时返回对象 4，根名字必须接收它。
5. 再删除唯一结点 4 得到空树；删除不存在的 99 继续保持空树。

**结果与核对**

五次删除后的中序依次为 \[2,4,6\]、\[4,6\]、\[4\]、\[\]、\[\]。重复键没有产生第二个 4；若忽略删除返回值，根变化时外部入口会错误地停留在旧对象。

**完整程序**

```python
def bst_node(key):
    return {"key": key, "left": None, "right": None}

def bst_insert(root, key):
    if root is None:
        return bst_node(key)
    if key < root["key"]:
        root["left"] = bst_insert(root["left"], key)
    elif key > root["key"]:
        root["right"] = bst_insert(root["right"], key)
    return root

def bst_from_keys(keys):
    root = None
    for key in keys:
        root = bst_insert(root, key)
    return root

def bst_delete(root, key):
    if root is None:
        return None
    if key < root["key"]:
        root["left"] = bst_delete(root["left"], key)
    elif key > root["key"]:
        root["right"] = bst_delete(root["right"], key)
    else:
        if root["left"] is None:
            return root["right"]
        if root["right"] is None:
            return root["left"]
        successor = root["right"]
        while successor["left"] is not None:
            successor = successor["left"]
        root["key"] = successor["key"]
        root["right"] = bst_delete(root["right"], successor["key"])
    return root

def bst_collect(root, output):
    if root is None:
        return
    bst_collect(root["left"], output)
    output.append(root["key"])
    bst_collect(root["right"], output)

def bst_keys(root):
    result = []
    bst_collect(root, result)
    return result

root = bst_from_keys([6, 2, 9, 4, 4])
print(bst_keys(root))
for key in [9, 2, 6, 4, 99]:
    root = bst_delete(root, key)
    print(bst_keys(root))
```

**预期输出**

```text
[2, 4, 6, 9]
[2, 4, 6]
[4, 6]
[4]
[]
[]
```


<a id="practice"></a>

## 自己做：先完成再看解答

### 练习 1

写 is\_bst(root)，验证严格左右大小约束，输入仍保证是合法的树形结构。用祖先传下的上下界检查，包含空树、正常示例、根 12 左侧出现后代 14，以及左孩子也为 12 的重复情况。

<details>
<summary>提示</summary>

None 表示没有该侧界限。走左边收紧上界为当前键，走右边收紧下界；相等也要拒绝。

</details>

<details>
<summary>解答与检查</summary>

正常示例与空树为 True，跨祖先范围的 14 和重复 12 都为 False。每个结点必须同时符合继承的下界与上界，不只检查父子关系。最坏访问全部结点，时间 O(n+1)，辅助栈 O(h+1)；这个函数检查键序，不检测环或共享对象。

**完整程序**

```python
def bst_node(key):
    return {"key": key, "left": None, "right": None}

def sample_bst():
    root = bst_node(12)
    root["left"] = bst_node(5)
    root["right"] = bst_node(18)
    root["left"]["left"] = bst_node(2)
    root["left"]["right"] = bst_node(9)
    root["right"]["left"] = bst_node(15)
    root["right"]["right"] = bst_node(21)
    return root

def bst_within(root, lower, upper):
    if root is None:
        return True
    key = root["key"]
    if lower is not None and key <= lower:
        return False
    if upper is not None and key >= upper:
        return False
    return bst_within(root["left"], lower, key) and bst_within(root["right"], key, upper)

def is_bst(root):
    return bst_within(root, None, None)

bad = bst_node(12)
bad["left"] = bst_node(5)
bad["left"]["right"] = bst_node(14)
duplicate = bst_node(12)
duplicate["left"] = bst_node(12)
print(is_bst(sample_bst()), is_bst(None))
print(is_bst(bad), is_bst(duplicate))
```

**预期输出**

```text
True True
False False
```


</details>

### 练习 2

写 bst\_range(root, lower, upper)，按递增顺序返回闭区间内全部键。lower 与 upper 为整数，反向区间返回空列表；检查示例区间 \[6,18\]、\[9,9\]、\[22,30\] 和 \[8,3\]，并跳过不可能有答案的子树。

<details>
<summary>提示</summary>

当前键大于下界时才需要左边，小于上界时才需要右边；先左、再当前、再右以保持输出顺序。

</details>

<details>
<summary>解答与检查</summary>

四组结果为 \[9,12,15,18\]、\[9\]、\[\]、\[\]。每个输出只追加一次，路径边界之外的子树被剪去；若输出 k 个键，时间 O(h+k+1)，辅助栈 O(h+1)，输出另占 O(k+1)。闭区间端点相等仍可能有一个答案。

**完整程序**

```python
def bst_node(key):
    return {"key": key, "left": None, "right": None}

def sample_bst():
    root = bst_node(12)
    root["left"] = bst_node(5)
    root["right"] = bst_node(18)
    root["left"]["left"] = bst_node(2)
    root["left"]["right"] = bst_node(9)
    root["right"]["left"] = bst_node(15)
    root["right"]["right"] = bst_node(21)
    return root

def bst_range_collect(root, lower, upper, result):
    if root is None:
        return
    key = root["key"]
    if key > lower:
        bst_range_collect(root["left"], lower, upper, result)
    if lower <= key and key <= upper:
        result.append(key)
    if key < upper:
        bst_range_collect(root["right"], lower, upper, result)

def bst_range(root, lower, upper):
    result = []
    if lower <= upper:
        bst_range_collect(root, lower, upper, result)
    return result

root = sample_bst()
print(bst_range(root, 6, 18))
print(bst_range(root, 9, 9))
print(bst_range(root, 22, 30), bst_range(root, 8, 3))
```

**预期输出**

```text
[9, 12, 15, 18]
[9]
[] []
```


</details>

### 练习 3

给定已经严格递增的整数列表，写 balanced\_bst(values) 按半开区间中点直接建立新树，不逐项调用插入，不切片，不修改输入。检查 \[-4,0,3,7,11,20\] 和空表，说明初始高度与后续更新的区别。

<details>
<summary>提示</summary>

空区间返回 None。中点成为根，左右分别使用 \[lo,middle) 和 \[middle+1,hi)，两个孩子入口接到新根。

</details>

<details>
<summary>解答与检查</summary>

六项输入建立根键 7 的树，中序恢复原列表，高度为 2；空表得到 None。每个位置新建一个结点，时间 Θ(n+1)，输出树占 Θ(n+1)，辅助栈 O(log(n+1)+1)。非空高度为 log₂n 向下取整；此构造依赖严格递增前提，不替调用者排序去重，也不保证以后修改仍平衡。

**完整程序**

```python
def bst_node(key):
    return {"key": key, "left": None, "right": None}

def bst_collect(root, output):
    if root is None:
        return
    bst_collect(root["left"], output)
    output.append(root["key"])
    bst_collect(root["right"], output)

def bst_keys(root):
    result = []
    bst_collect(root, result)
    return result

def bst_from_range(values, lo, hi):
    if lo == hi:
        return None
    middle = lo + (hi - lo) // 2
    root = bst_node(values[middle])
    root["left"] = bst_from_range(values, lo, middle)
    root["right"] = bst_from_range(values, middle + 1, hi)
    return root

def balanced_bst(values):
    return bst_from_range(values, 0, len(values))

values = [-4, 0, 3, 7, 11, 20]
root = balanced_bst(values)
print(root["key"], bst_keys(root))
print(values)
print(balanced_bst([]))
```

**预期输出**

```text
7 [-4, 0, 3, 7, 11, 20]
[-4, 0, 3, 7, 11, 20]
None
```


</details>

<a id="pitfalls"></a>

## 容易混淆的地方

- **只比较直接孩子就认为整树符合搜索约束。** 每个后代还受所有祖先范围约束，用上下界或完整中序严格性核对。
- **插入和删除只调用函数，不接回返回入口。** 空位置插入和根被孩子接替都会改变入口，要逐层写回子树根。
- **认为右侧最小后继一定没有孩子，删除时直接断开。** 后继可以有右孩子，摘除时必须接回它，避免丢掉整段子树。
- **把普通搜索树当成总能折半的查找，或假定结点引用永久绑定某个键。** 时间随实际高度变化；本章双孩子删除会复制键，身份契约另行说明。

<a id="self-check"></a>

## 离开这一章前

- [ ] 手画一个直接父子关系正确、祖先范围错误的反例。
- [ ] 对每次增删检查键集合、严格中序、可达对象数和所有链接。
- [ ] 检查空树、重复插入、缺失删除、根删除以及后继带右孩子。
- [ ] 比较同一键集合的不同插入顺序，分别数高度与真实访问路径。
- [ ] 说明范围输出量为何计入时间，以及一次中点构造为何不等于动态平衡。

## 本章边界

- 这是不自动平衡的整数集合，不实现重复计数、键值映射或稳定结点句柄。
- 所有递归操作仍受树高与解释器深度限制；未实现旋转、AVL 或红黑树。
- 输入树形结构合法由调用者保证，is\_bst 只检查键序；从列表构造要求严格递增。
- 复杂度以单位比较与引用操作计，输出列表和新增结点与辅助栈分别核算。

## 选题来源与覆盖

来源含学生报告时，仅将其作为选题线索；具体机制仍需结合后续实验或权威资料核对。

- [大一小学期/Week\_3-Python/docs/readme.md](https://github.com/PKUanonym/REKCARC-TSC-UHT/blob/37cd19f7a9fb80dc846a7016b3fd482ed5fe7cc0/%E5%A4%A7%E4%B8%80%E5%B0%8F%E5%AD%A6%E6%9C%9F/Week_3-Python/docs/readme.md)（已提取可读文本，固定版本 37cd19f7a9fb）
- 主题 1：Python 基础语法的外部学习入口；位置：第 41–80 行。
- 主题 2：从基础语法到工具与应用的建议阅读顺序；位置：第 121–160 行。

## 参考资料与规则核对

上游入口用于确定学习方向；下面的参考资料用于核对语言语义、数据结构或算法分析规则，例题和练习由本项目重新设计。

- [Open Data Structures：未平衡二叉搜索树](https://opendatastructures.org/ods-java/6_2_BinarySearchTree_Unbala.html)：核对全子树严格大小约束、路径查找与后继摘除；例子和 Python 实现自行设计。
- [Algorithms 4/e：二叉搜索树](https://algs4.cs.princeton.edu/32bst/)：核对有序查询、后继删除与高度成本；本章采用整数集合与复制键删除，不承诺稳定结点句柄或自动平衡。

**继续学习**：先独立完成自测，再记录仍需回读的步骤。

[上一章：从链到层次：树、二叉树与遍历](16-trees.md) · [下一章：让最值留在根部：二叉堆与优先队列](18-heaps.md)

[教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [记录自己的学习](../learning-log-template.md)
