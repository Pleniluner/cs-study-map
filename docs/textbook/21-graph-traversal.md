# 沿边系统探索：DFS、BFS 与无权最短路径

[返回教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [哈希表与图练习指引](../hash-graphs-practice.md)

[上一章：用顶点和边表达关系：图与存储表示](20-graphs.md)

[学习目标](#objectives) · [需要的基础](#prerequisites) · [例题](#examples) · [练习](#practice) · [自测](#self-check)

状态：**AI 初稿，可开始试学**。生成模型：Codex 当前会话（未记录具体模型型号）。

本章围绕资料中识别到的知识点重新编写；讲解、数值模型、例题与练习为 AI 原创组织，不是原课程题目或答案。主题出处只说明选题关联，不证明全部推导已经正确。

已经知道每个顶点的直接邻居后，下一步是沿边探索更远的位置。树遍历可以依赖无环、无共享的前提，图却会让多条路线汇合，也可能绕回起点。因此本章把“第一次发现”作为共同规则，再分别用栈和队列安排后续工作。我们会实现递归与显式栈 DFS、BFS 距离和路径恢复，最后访问多个连通部分。所有函数读取已有的合法邻接表，不把建图成本藏进遍历结论，也不在遍历期间修改图。

<a id="objectives"></a>

## 学完要能做到

- 解释 visited 或距离标记如何保证带环图终止并避免重复访问。
- 用显式帧模拟递归 DFS，保持同一邻接顺序下的发现次序与父边。
- 证明 BFS 首次发现时的距离最短，并恢复一条无权最短路径。
- 处理孤立点、无效起点、非连通图与多个起点，计算实际扫描成本。

<a id="prerequisites"></a>

## 需要的基础

- 掌握第 20 章编号、方向、邻接表、游走与路径约定。
- 掌握第 8、9 章栈和队列，以及第 13、16 章递归调用与树遍历。
- 知道列表游标不会删除前面的存储，能区分工作区与返回结果。

## 从树到图：发现时立刻标记

深度优先搜索 DFS 从一个顶点出发，先把某个尚未发现的邻居探索到底，再回到当前顶点继续下一个邻居。图中可能有环或共同邻居，若照搬树递归而不记录已发现状态，就可能反复绕圈。dfs\_visit 一进入便把 seen 设为 True，再记录发现次序；只有尚未发现的邻居才递归进入。父边只在第一次发现时设置，不会被后来的另一条边覆盖。

示例邻接表为 \[\[1,2\],\[3\],\[3\],\[0\],\[\]\]。从 0 先走 1，再走 3；3 的邻居 0 已见，于是返回。之后 0 才发现 2，而 2 指向的 3 也已见。发现顺序是 0、1、3、2，4 不可达。这里的 parent 是本次搜索选出的父亲，不是原图本来就只有一个父亲。根与不可达顶点的 parent 都为 None，必须结合 order 或可达状态区分。

filled 只用于重复填入布尔值、整数或 None 这些不可变标量，不能拿它复制可变邻接行。函数初始化长度为 n 的状态，随后每个可达顶点只进入一次，每个可达顶点的邻接项只扫描一次。若这些项共 aᵣ 个，时间 Θ(n+aᵣ+1)，最坏 O(n+a+1)，空间 O(n+1)，其中递归链可能长达 n。数学上必终止不等于 Python 能容纳任意深的调用；长链应使用下一节的循环版本，而不是提高递归限制。

**完整程序**

```python
def filled(n, value):
    result = []
    for i in range(n):
        result.append(value)
    return result

def dfs_visit(adjacency, vertex, seen, order, parent):
    seen[vertex] = True
    order.append(vertex)
    for neighbor in adjacency[vertex]:
        if not seen[neighbor]:
            parent[neighbor] = vertex
            dfs_visit(adjacency, neighbor, seen, order, parent)

def dfs_recursive(adjacency, start):
    seen = filled(len(adjacency), False)
    parent = filled(len(adjacency), None)
    order = []
    if 0 <= start < len(adjacency):
        dfs_visit(adjacency, start, seen, order, parent)
    return {"order": order, "parent": parent}

graph = [[1, 2], [3], [3], [0], []]
print(dfs_recursive(graph, 0))
print(dfs_recursive(graph, 4))
print(dfs_recursive(graph, -1))
```

**预期输出**

```text
{'order': [0, 1, 3, 2], 'parent': [None, 0, 0, 1, None]}
{'order': [4], 'parent': [None, None, None, None, None]}
{'order': [], 'parent': [None, None, None, None, None]}
```


选题关联：来源主题 1（文末列出）。

## 显式栈保存下一步：精确模拟递归

要保留递归 DFS 的顺序，栈中不能只写一个顶点，还要记住它的邻居处理到哪里。每个帧保存两个整数：当前顶点和下一邻居下标。栈顶帧相当于当前函数调用；找到新邻居时，先把父帧的游标向后移，再为孩子压入从零开始的新帧。孩子结束弹栈，父帧就能从原来的暂停点继续。

当游标等于该行长度时，所有出边都已检查，可以弹出帧。否则只看当前这一条边，已见则继续当前帧，未见则立刻标记、记录父边与发现次序，再深入孩子。这个逐边处理过程与递归 for 循环一一对应，所以相同起点和相同邻接顺序产生相同发现序列及 parent。把全部邻居一次性压栈并提前标记，可能预先占用本该由更深路径发现的顶点，不能仅靠反转邻居列表就宣称父边一定相同。

每次循环或者推进一个邻接项，或者完成一个顶点，因此总工作仍是 Θ(n+aᵣ+1)。同时存活的帧数不超过已发现顶点数，显式栈最坏 O(n)；seen、parent 和输出也需 O(n)。本版本没有 Python 递归调用，可以处理较长链，但仍受可用内存约束。示例不排序邻接行，得到的次序依赖输入排列；改变排列可能得到另一棵正确的搜索树，可达顶点集合保持不变。

**完整程序**

```python
def filled(n, value):
    result = []
    for i in range(n):
        result.append(value)
    return result

def dfs_stack(adjacency, start):
    seen = filled(len(adjacency), False)
    parent = filled(len(adjacency), None)
    order = []
    if start < 0 or start >= len(adjacency):
        return {"order": order, "parent": parent}
    seen[start] = True
    order.append(start)
    stack = [[start, 0]]
    while len(stack) > 0:
        frame = stack[len(stack) - 1]
        vertex = frame[0]
        position = frame[1]
        if position == len(adjacency[vertex]):
            stack.pop()
        else:
            neighbor = adjacency[vertex][position]
            frame[1] = position + 1
            if not seen[neighbor]:
                seen[neighbor] = True
                parent[neighbor] = vertex
                order.append(neighbor)
                stack.append([neighbor, 0])
    return {"order": order, "parent": parent}

graph = [[1, 2], [3], [3], [0], []]
print(dfs_stack(graph, 0))
print(dfs_stack([], 0))
print(graph)
```

**预期输出**

```text
{'order': [0, 1, 3, 2], 'parent': [None, 0, 0, 1, None]}
{'order': [], 'parent': []}
[[1, 2], [3], [3], [0], []]
```


选题关联：来源主题 1（文末列出）。

## 广度优先搜索：队列按距离逐层推进

广度优先搜索 BFS 使用先入先出的队列。起点距离为 0，所有尚未发现的顶点距离为 −1。取出距离 d 的顶点后，把它尚未发现的邻居标成 d+1 并入队。distance 同时承担距离和发现标记，赋值发生在入队之前，保证同一个顶点不会被两个已发现的前驱重复入队。根也要在开始时标记，否则环能把起点再次加入。

正确性来自队列的层次次序：距离 d 层的顶点总在 d+1 层之前处理，任何经由 d 层的新路线长度都是 d+1。如果某个首次发现的顶点还有更短路线，那么更短路线上的前驱应更早被处理，并已发现该点，产生矛盾。因此第一次写入的距离就是最少边数，之后不需要改小它。DFS 只保证找到可达顶点，不保持这种层次次序，父边也不保证构成最短路径。

本实现用列表和 head 游标模拟队列，不调用 pop(0) 搬移剩余元素。head 前面的元素仍在列表里，最后整个列表直接作为 order 返回，所以占用 O(r) 而非只按当前队列宽度收费；r 是可达顶点数。初始化全长距离和父边需 Θ(n)，扫描成本为 Θ(aᵣ)，总时间 Θ(n+aᵣ+1)。动态列表追加按摊还成本计算。示例的 3 可以经 1 或 2 到达，两条路线同长，按当前行顺序先发现它的是 1。

**完整程序**

```python
def filled(n, value):
    result = []
    for i in range(n):
        result.append(value)
    return result

def breadth_first(adjacency, start):
    distance = filled(len(adjacency), -1)
    parent = filled(len(adjacency), None)
    queue = []
    if 0 <= start < len(adjacency):
        distance[start] = 0
        queue.append(start)
    head = 0
    while head < len(queue):
        vertex = queue[head]
        head = head + 1
        for neighbor in adjacency[vertex]:
            if distance[neighbor] == -1:
                distance[neighbor] = distance[vertex] + 1
                parent[neighbor] = vertex
                queue.append(neighbor)
    return {"order": queue, "distance": distance, "parent": parent}

graph = [[1, 2], [3], [3], [0], []]
print(breadth_first(graph, 0))
print(breadth_first(graph, 4))
print(breadth_first([], 0))
```

**预期输出**

```text
{'order': [0, 1, 2, 3], 'distance': [0, 1, 1, 2, -1], 'parent': [None, 0, 0, 1, None]}
{'order': [4], 'distance': [-1, -1, -1, -1, 0], 'parent': [None, None, None, None, None]}
{'order': [], 'distance': [], 'parent': []}
```


选题关联：来源主题 1（文末列出）。

## 从父边恢复路径：一条最短路径不等于全部

BFS 首次发现 v 时，把当前顶点存为 parent\[v\]。沿父边从目标反向追踪，每一步距离减少一，最终到达起点并遇到 None，因此不会在父链上绕环。把收集到的顶点反转，就得到从起点到目标的一条路线。恢复后应核查每一对相邻顶点确有对应方向的边，且边数等于目标距离。

shortest\_path 对无效起点、无效目标或不可达目标返回空列表；合法的起点等于目标时返回只含该点的列表，表示长度零。BFS 原接口对无效起点返回空 order、全为 −1 的距离和全为 None 的父边。明确这些返回约定可以避免把不可达和“还没走一步”混为一谈，也防止负编号被当作 Python 倒数下标。

本程序先完成一次 BFS，再恢复目标路径。若路径有 p 个顶点，恢复需 Θ(p) 时间，反向临时列表和输出各占 O(p)；包括搜索状态的总空间 O(n+1)，搜索时间 Θ(n+aᵣ+1)。它没有实现发现目标后提前停止。两条等长最短路线存在时，邻接顺序决定保留哪一条，距离仍不变。这里最短指边数最少；若一条直达边耗时 100，两条边的绕路各耗时 1，BFS 仍偏向直达边，不能用来求任意权重下的最小总耗时。

**完整程序**

```python
def filled(n, value):
    result = []
    for i in range(n):
        result.append(value)
    return result

def breadth_first(adjacency, start):
    distance = filled(len(adjacency), -1)
    parent = filled(len(adjacency), None)
    queue = []
    if 0 <= start < len(adjacency):
        distance[start] = 0
        queue.append(start)
    head = 0
    while head < len(queue):
        vertex = queue[head]
        head = head + 1
        for neighbor in adjacency[vertex]:
            if distance[neighbor] == -1:
                distance[neighbor] = distance[vertex] + 1
                parent[neighbor] = vertex
                queue.append(neighbor)
    return {"order": queue, "distance": distance, "parent": parent}

def shortest_path(adjacency, start, target):
    n = len(adjacency)
    if start < 0 or start >= n or target < 0 or target >= n:
        return []
    result = breadth_first(adjacency, start)
    if result["distance"][target] == -1:
        return []
    reverse = []
    vertex = target
    while vertex is not None:
        reverse.append(vertex)
        vertex = result["parent"][vertex]
    path = []
    for i in range(len(reverse) - 1, -1, -1):
        path.append(reverse[i])
    return path

graph = [[1, 2], [3], [3], [0], []]
print(shortest_path(graph, 0, 3))
print(shortest_path(graph, 3, 2))
print(shortest_path(graph, 0, 4))
print(shortest_path(graph, 2, 2))
```

**预期输出**

```text
[0, 1, 3]
[3, 0, 2]
[]
[2]
```


选题关联：来源主题 1（文末列出）。

## 多个连通部分：共享标记形成搜索森林

单一起点只能覆盖它可达的部分。若想访问全图，可从编号小到大检查每个顶点，遇到未发现者就启动新搜索，所有搜索共用标记。每次启动得到一棵搜索树，合起来叫搜索森林。不能在每次启动时重置全图标记，否则会重复扫描已经完成的部分，也会失去分组意义。

对无向图，可达关系具有双向性，每轮恰好得到一个连通分量。components 以组号充当发现标记，发现时立即编号，使用 BFS 收集该组。一个孤立顶点也是独立分量；空图返回空标签和空分组。本节输入必须是合法无向邻接表，不在函数内重复验证对称性。组号由最小尚未编号顶点决定，组内顺序由 BFS 与邻接排列决定。

对有向图，相同的外层循环只能形成搜索森林，不能据此宣称求出了强连通分量。比如只有 1→0，从 0 开始先结束一棵树，随后从 1 开始又是一棵；这与把方向忽略后的连通划分也不同。强连通要求两两可互达，需要专门算法，本章不实现。无向版本整个过程中每顶点只入队一次，每邻接项只扫描一次，时间 Θ(n+a+1)，包括标签、各组输出与队列引用的空间 O(n+1)。外层循环并没有把复杂度再乘 n，因为内层只处理尚未发现的部分。

**完整程序**

```python
def filled(n, value):
    result = []
    for i in range(n):
        result.append(value)
    return result

def components(adjacency):
    label = filled(len(adjacency), -1)
    groups = []
    for start in range(len(adjacency)):
        if label[start] == -1:
            number = len(groups)
            label[start] = number
            queue = [start]
            head = 0
            while head < len(queue):
                vertex = queue[head]
                head = head + 1
                for neighbor in adjacency[vertex]:
                    if label[neighbor] == -1:
                        label[neighbor] = number
                        queue.append(neighbor)
            groups.append(queue)
    return {"label": label, "groups": groups}

graph = [[1], [0, 2], [1], [4], [3], []]
print(components(graph))
print(components([[]]))
print(components([]))
```

**预期输出**

```text
{'label': [0, 0, 0, 1, 1, 2], 'groups': [[0, 1, 2], [3, 4], [5]]}
{'label': [0], 'groups': [[0]]}
{'label': [], 'groups': []}
```


选题关联：来源主题 1（文末列出）。

<a id="examples"></a>

## 跟着做：原创例题

### 例题 1

对 \[\[1,2\],\[3\],\[3\],\[0\],\[\]\] 从 0 执行 DFS，记录每个顶点的进入和完成事件。说明为什么 3 完成后才进入 2，而原图并没有因此变成一条链。

1. 进入 0、1、3，三个帧依次叠在栈中。
2. 3 遇到已见的 0，不能再次进入；完成 3 后弹栈，1 也完成。
3. 回到 0 的下一邻居 2，进入它；3 已见，不再产生第二次进入。
4. 完成 2，最后完成 0；孤立且不可达的 4 没有事件。

**结果与核对**

每个可达顶点恰好一条进入和一条完成记录，共八条。父帧暂停、子帧完成再返回构成嵌套区间；原图的其他边仍存在，搜索事件只记录一次访问过程。下面用显式帧输出事件，时间 Θ(n+aᵣ+1)，事件输出 O(r)，其他状态 O(n+1)。完成次序不应直接当作本章未验证的课程安排。

**完整程序**

```python
def filled(n, value):
    result = []
    for i in range(n):
        result.append(value)
    return result

def dfs_events(adjacency, start):
    seen = filled(len(adjacency), False)
    events = []
    if start < 0 or start >= len(adjacency):
        return events
    seen[start] = True
    events.append(["enter", start])
    stack = [[start, 0]]
    while len(stack) > 0:
        frame = stack[len(stack) - 1]
        vertex = frame[0]
        position = frame[1]
        if position == len(adjacency[vertex]):
            events.append(["leave", vertex])
            stack.pop()
        else:
            neighbor = adjacency[vertex][position]
            frame[1] = position + 1
            if not seen[neighbor]:
                seen[neighbor] = True
                events.append(["enter", neighbor])
                stack.append([neighbor, 0])
    return events

graph = [[1, 2], [3], [3], [0], []]
print(dfs_events(graph, 0))
```

**预期输出**

```text
[['enter', 0], ['enter', 1], ['enter', 3], ['leave', 3], ['leave', 1], ['enter', 2], ['leave', 2], ['leave', 0]]
```


### 例题 2

对 \[\[1,2\],\[3\],\[3\],\[4\],\[\]\] 从 0 执行 BFS。每次处理完一个顶点，记录该顶点、尚未处理的队列和距离副本，确认 3 不会重复入队。

1. 处理 0 后队列为 1、2，二者距离均为 1。
2. 处理 1 时首次发现 3，写距离 2 并入队；此时待处理的是 2、3。
3. 处理 2 时见到 3 已有距离，不能再次入队，也不改其首次发现信息。
4. 处理 3 时发现距离为 3 的顶点 4，随后处理 4，队列清空。

**结果与核对**

最终距离 \[0,1,1,2,3\]。快照应保存副本，否则事后看到的会是同一份最终状态。bfs\_trace 每轮复制全长距离和队列后缀，若可达点有 r 个，时间上界 O(n+aᵣ+r(n+r)+1)，轨迹空间 O(r(n+r)+1)；最坏均会多出二次项。普通 BFS 不保存这些快照，仍保持线性界。

**完整程序**

```python
def filled(n, value):
    result = []
    for i in range(n):
        result.append(value)
    return result

def bfs_trace(adjacency, start):
    distance = filled(len(adjacency), -1)
    queue = []
    steps = []
    if 0 <= start < len(adjacency):
        distance[start] = 0
        queue.append(start)
    head = 0
    while head < len(queue):
        vertex = queue[head]
        head = head + 1
        for neighbor in adjacency[vertex]:
            if distance[neighbor] == -1:
                distance[neighbor] = distance[vertex] + 1
                queue.append(neighbor)
        steps.append([vertex, queue[head:], distance.copy()])
    return {"distance": distance, "steps": steps}

trace = bfs_trace([[1, 2], [3], [3], [4], []], 0)
for step in trace["steps"]:
    print(step)
print(trace["distance"])
```

**预期输出**

```text
[0, [1, 2], [0, 1, 1, -1, -1]]
[1, [2, 3], [0, 1, 1, 2, -1]]
[2, [3], [0, 1, 1, 2, -1]]
[3, [4], [0, 1, 1, 2, 3]]
[4, [], [0, 1, 1, 2, 3]]
[0, 1, 1, 2, 3]
```


<a id="practice"></a>

## 自己做：先完成再看解答

### 练习 1

写 vertices\_at\_distance，返回距起点恰好 k 条边的顶点，并按编号递增。k 为整数，负 k 返回空表；无效起点也返回空表。检查 k=0、2、−1 和不可达顶点。

<details>
<summary>提示</summary>

使用 BFS 距离，随后按编号扫描距离列表。先排除负 k，避免把 −1 的未发现标记当成一层。

</details>

<details>
<summary>解答与检查</summary>

在 \[\[2,1\],\[3\],\[3\],\[\],\[\]\] 中，从 0 出发距离 1 的结果为 \[1,2\]，虽然 BFS 入队顺序是 2 在前；距离 0 为 \[0\]，距离 2 为 \[3\]。正常查询时间 O(n+a+1)，状态与输出 O(n+1)，负 k 可直接常数返回。不可达的 4 不属于任何非负距离层。

**完整程序**

```python
def filled(n, value):
    result = []
    for i in range(n):
        result.append(value)
    return result

def breadth_first(adjacency, start):
    distance = filled(len(adjacency), -1)
    parent = filled(len(adjacency), None)
    queue = []
    if 0 <= start < len(adjacency):
        distance[start] = 0
        queue.append(start)
    head = 0
    while head < len(queue):
        vertex = queue[head]
        head = head + 1
        for neighbor in adjacency[vertex]:
            if distance[neighbor] == -1:
                distance[neighbor] = distance[vertex] + 1
                parent[neighbor] = vertex
                queue.append(neighbor)
    return {"order": queue, "distance": distance, "parent": parent}

def vertices_at_distance(adjacency, start, k):
    if k < 0:
        return []
    distance = breadth_first(adjacency, start)["distance"]
    result = []
    for vertex in range(len(adjacency)):
        if distance[vertex] == k:
            result.append(vertex)
    return result

graph = [[2, 1], [3], [3], [], []]
for k in [0, 1, 2, -1, 9]:
    print(k, vertices_at_distance(graph, 0, k))
```

**预期输出**

```text
0 [0]
1 [1, 2]
2 [3]
-1 []
9 []
```


</details>

### 练习 2

为有向或无向图计算可达矩阵，位置 s、t 为 1 表示从 s 能沿方向到达 t，否则为 0。零步也算可达，因此所有存在的顶点在对角线为 1。检查 \[\[1\],\[2\],\[\],\[\]\] 和空图。

<details>
<summary>提示</summary>

依次把每个顶点作为 BFS 起点，用非负距离填写一行。这次每个起点都需要独立状态，不能沿用连通分量的共享标记。

</details>

<details>
<summary>解答与检查</summary>

结果前三行分别为 \[1,1,1,0\]、\[0,1,1,0\]、\[0,0,1,0\]，孤立点行是 \[0,0,0,1\]。它表达多步可达，区别于对角线为零的本章邻接矩阵。做 n 次搜索，总时间上界 O(n(n+a)+1)，输出 O(n²+1)，除输出外临时搜索状态 O(n+1)。空图返回 \[\]，不凭空补一个顶点。

**完整程序**

```python
def filled(n, value):
    result = []
    for i in range(n):
        result.append(value)
    return result

def breadth_first(adjacency, start):
    distance = filled(len(adjacency), -1)
    parent = filled(len(adjacency), None)
    queue = []
    if 0 <= start < len(adjacency):
        distance[start] = 0
        queue.append(start)
    head = 0
    while head < len(queue):
        vertex = queue[head]
        head = head + 1
        for neighbor in adjacency[vertex]:
            if distance[neighbor] == -1:
                distance[neighbor] = distance[vertex] + 1
                parent[neighbor] = vertex
                queue.append(neighbor)
    return {"order": queue, "distance": distance, "parent": parent}

def reachability_matrix(adjacency):
    matrix = []
    for start in range(len(adjacency)):
        distance = breadth_first(adjacency, start)["distance"]
        row = []
        for value in distance:
            if value == -1:
                row.append(0)
            else:
                row.append(1)
        matrix.append(row)
    return matrix

for row in reachability_matrix([[1], [2], [], []]):
    print(row)
print(reachability_matrix([]))
```

**预期输出**

```text
[1, 1, 1, 0]
[0, 1, 1, 0]
[0, 0, 1, 0]
[0, 0, 0, 1]
[]
```


</details>

### 练习 3

写 multi\_source\_distances，给定起点列表，返回每个顶点距任一起点的最少边数，不可达为 −1。起点可重复，任何越界编号都使调用返回 None；无起点返回全 −1，空图与空起点返回 \[\]。

<details>
<summary>提示</summary>

先把所有合法起点的距离设为 0 并去重入队，再进行同一套 BFS 扩展。不能先把某个起点完整搜索完再加入下一个。

</details>

<details>
<summary>解答与检查</summary>

对无向链 0—1—2—3—4 加孤立点 5，以 \[0,4,0\] 为起点得到 \[0,1,2,1,0,-1\]。所有源同时处在第零层，按层展开保证得到各单源距离的最小有限值。设起点记录数为 s，时间 O(n+a+s+1)，状态 O(n+1)。有向图计算的是从任一源出发到各点的距离；若问题反问各点到最近站点，必须先反向图。

**完整程序**

```python
def filled(n, value):
    result = []
    for i in range(n):
        result.append(value)
    return result

def multi_source_distances(adjacency, sources):
    distance = filled(len(adjacency), -1)
    queue = []
    for start in sources:
        if start < 0 or start >= len(adjacency):
            return None
        if distance[start] == -1:
            distance[start] = 0
            queue.append(start)
    head = 0
    while head < len(queue):
        vertex = queue[head]
        head = head + 1
        for neighbor in adjacency[vertex]:
            if distance[neighbor] == -1:
                distance[neighbor] = distance[vertex] + 1
                queue.append(neighbor)
    return distance

graph = [[1], [0, 2], [1, 3], [2, 4], [3], []]
print(multi_source_distances(graph, [0, 4, 0]))
print(multi_source_distances(graph, []))
print(multi_source_distances(graph, [-1]))
print(multi_source_distances([], []))
```

**预期输出**

```text
[0, 1, 2, 1, 0, -1]
[-1, -1, -1, -1, -1, -1]
None
[]
```


</details>

<a id="pitfalls"></a>

## 容易混淆的地方

- **把标记推迟到出队，或在递归返回后才标记。** 发现时就标记；否则共同邻居重复入队，环还可能使递归无法结束。
- **用 DFS 父边长度当最短距离，或让 BFS 处理任意权重最短路。** DFS 不按距离分层；本章 BFS 最短性只对边数成立。
- **用一次搜索代表全图，或把有向搜索森林当强连通分量。** 单源只访问可达部分；无向分量和有向强连通是不同问题。
- **只计算活跃队列宽度，忽略游标前缀、全长状态和轨迹副本。** 按实际存活对象收费；普通遍历、完整输出和复制调试轨迹的空间分别计算。

<a id="self-check"></a>

## 离开这一章前

- [ ] 手画含环和共同邻居的图，逐步标出发现时刻及父边归属。
- [ ] 在同一邻接顺序下比对递归与显式帧 DFS 的次序和父边。
- [ ] 证明 BFS 首次发现距离最短，并检查恢复路径每条边和总长度。
- [ ] 对空图、孤立点、断开的部分与越界起点核对接口返回值。
- [ ] 用单源距离的逐点最小值验证多源 BFS，并解释有向图中的方向。

## 本章边界

- 输入保证为前章的合法无权邻接表，编号为整数，搜索期间不改图；分量函数仅用于无向模式。
- 递归 DFS 只用于小规模示例，长链使用显式栈；没有提高解释器递归限制。
- 只返回一条最短路径，不枚举全部路径，不求带权最短路、强连通或拓扑次序。
- 邻接排列影响访问次序与等长路径的父边选择，不影响单源可达集合及最短边数。

## 选题来源与覆盖

来源含学生报告时，仅将其作为选题线索；具体机制仍需结合后续实验或权威资料核对。

- [大一小学期/Week\_3-Python/docs/readme.md](https://github.com/PKUanonym/REKCARC-TSC-UHT/blob/37cd19f7a9fb80dc846a7016b3fd482ed5fe7cc0/%E5%A4%A7%E4%B8%80%E5%B0%8F%E5%AD%A6%E6%9C%9F/Week_3-Python/docs/readme.md)（已提取可读文本，固定版本 37cd19f7a9fb）
- 主题 1：Python 基础语法的外部学习入口；位置：第 41–80 行。
- 主题 2：从基础语法到工具与应用的建议阅读顺序；位置：第 121–160 行。

## 参考资料与规则核对

上游入口用于确定学习方向；下面的参考资料用于核对语言语义、数据结构或算法分析规则，例题和练习由本项目重新设计。

- [NIST DADS：深度优先搜索](https://xlinux.nist.gov/dads/HTML/depthfirst.html)：核对深度推进、发现与完成的区别；本章显式帧逐条扫描邻居，按实际程序验证与递归同序。
- [NIST DADS：广度优先搜索](https://xlinux.nist.gov/dads/HTML/breadthfirst.html)：核对队列安排与逐层推进；本章使用列表游标并计入保留前缀。
- [Open Data Structures：图遍历](https://opendatastructures.org/ods-python/12_3_Graph_Traversal.html)：核对单源访问、BFS 最少边数与父边恢复；图、数值、轨迹和 Python 实现重新设计，多源与矩阵练习另作性质验证。
- [Python 3.11：解释器递归深度](https://docs.python.org/3.11/library/sys.html#sys.getrecursionlimit)：区分终止证明与运行栈可容纳深度；长链验证使用循环版本，不提高递归限制。

**继续学习**：先独立完成自测，再记录仍需回读的步骤。

[上一章：用顶点和边表达关系：图与存储表示](20-graphs.md)

[教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [哈希表与图练习指引](../hash-graphs-practice.md) · [记录自己的学习](../learning-log-template.md)
