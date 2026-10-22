# 安排有向依赖：拓扑排序与 DAG 应用

[返回教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [哈希表与图练习指引](../hash-graphs-practice.md) · [拓扑排序与带权图练习指引](../weighted-graphs-practice.md)

[上一章：沿边系统探索：DFS、BFS 与无权最短路径](21-graph-traversal.md) · [下一章：比较路线总费用：带权最短路与松弛](23-weighted-shortest-paths.md)

[学习目标](#objectives) · [需要的基础](#prerequisites) · [例题](#examples) · [练习](#practice) · [自测](#self-check)

状态：**AI 初稿，可开始试学**。生成模型：Codex 当前会话（未记录具体模型型号）。

本章围绕资料中识别到的知识点重新编写；讲解、数值模型、例题与练习为 AI 原创组织，不是原课程题目或答案。主题出处只说明选题关联，不证明全部推导已经正确。

有些边表达可以走过去，有些边表达必须先做完。上一章的 DFS、BFS 能探索可达关系，却不自动给出满足所有先修条件的安排。本章把有向边 u→v 解释为 u 必须排在 v 前面，从检验一个候选次序开始，建立删除零入度顶点的 Kahn 算法，再用 DFS 的完成次序与灰色状态处理同一问题。最后把次序用于任务排程、路径计数和字典序选择，并让失败结果准确区分阻塞集合与实际有向环。

<a id="objectives"></a>

## 学完要能做到

- 检验完整拓扑序，并说明有向无环图与拓扑序存在性的等价关系。
- 维护剩余入度，用队列实现 Kahn 算法并解释阻塞集合。
- 用显式 DFS 帧、三种颜色和父边返回拓扑序或一条闭合环。
- 推导并行层次、最早完工时间、次序唯一性和 DAG 路径计数。

<a id="prerequisites"></a>

## 需要的基础

- 掌握第 20、21 章有向邻接表、DFS 发现与完成、队列游标。
- 能使用第 18 章最小堆，并按实际扫描和复制次数计算复杂度。
- 能区分排列、前缀、路径和闭合游走，以及空结果与失败。

## 先检查答案：每条依赖都必须向后

拓扑序是全体顶点的一次排列，使每条有向边的起点都在终点之前。编号只作身份，不代表先后。图 \[\[2\],\[2\],\[\]\] 可以排成 0、1、2，也可以是 1、0、2；0、2、1 不合法，因为 1→2 违反次序。只检查相邻两个位置不够，依赖边可能跨过许多位置。程序先建立位置表，再逐条检查原图边，同时拒绝重复、漏点和越界整数编号。

本章输入为编号 0 至 n−1 的合法有向邻接表，每行无重复项，函数不改变它。为表示“任务依赖自身”这一错误，本章额外接受自环；第 20 章构造器仍会拒绝自环，所以自环测试直接写出邻接表。无向边的两种方向会形成双向约束，不应把普通无向连接直接当作课程依赖。空图只有一种空排列，检查 \[\] 得到 True。

如果图含有向环，沿环每条边都要求位置严格增大，最后却回到原点，不可能满足。因此有环必无拓扑序。反过来，无环非空图必有零入度顶点：否则反复沿入边找前驱，有限个顶点中必有重复，便形成环。删除一个零入度点后剩余图仍无环，反复执行就能排完。这也给出了下一节算法的存在性依据。检验器耗时 O(n+a+1)、额外空间 O(n+1)，a 为邻接项总数；本章有向图的 a 就是边数。

**完整程序**

```python
def filled(n, value):
    result = []
    for i in range(n):
        result.append(value)
    return result

def topological_order_valid(adjacency, order):
    n = len(adjacency)
    if len(order) != n:
        return False
    position = filled(n, None)
    for i in range(n):
        vertex = order[i]
        if vertex < 0 or vertex >= n or position[vertex] is not None:
            return False
        position[vertex] = i
    for source in range(n):
        for target in adjacency[source]:
            if position[source] >= position[target]:
                return False
    return True

graph = [[2], [2], []]
print(topological_order_valid(graph, [1, 0, 2]))
print(topological_order_valid(graph, [0, 2, 1]))
print(topological_order_valid(graph, [0, 0, 2]))
print(topological_order_valid([[0]], [0]))
print(topological_order_valid([], []))
```

**预期输出**

```text
True
False
False
False
True
```


选题关联：来源主题 1（文末列出）。

## Kahn 算法：入度统计的是尚未完成的前驱

Kahn 算法先统计每个顶点的入度，将所有零入度顶点按编号放进队列。每次取队首作为下一个安排，扫描它的出边，把对应终点的剩余入度减一；某点刚降到零时才入队。关键不变式是：入度等于仍未处理的前驱数量。因此取出的点不存在未完成依赖，添加到结果末尾总是安全的。邻接行不做删除，变化的是独立的计数表。

对 \[\[2\],\[2\],\[3,4\],\[\],\[\]\]，初始队列为 0、1。处理 0 后，2 仍缺前驱 1；处理 1 后，2 才能入队。继续处理 2，3 和 4 同时就绪。程序返回 order 与 blocked；blocked 为空才代表整个 order 是完整答案。若队列耗尽仍有正入度点，它们的剩余子图必有环，order 只是成功移除的前缀。blocked 还可能包含环的后继，不能把列表中每一点都标成环内成员。

队列使用 head 游标，不用 pop(0)。每个顶点至多入队一次，每条边在初始计数和源点处理时各扫描至多一次，时间 O(n+a+1)。队列保留已处理前缀，直接作为返回的 order，连同计数和阻塞输出需 O(n+1) 空间。首次入队顺序使相同输入的结果可重复，但 FIFO 不是“每次选当前最小编号”；新加入的小编号可能排在旧的大编号后面。练习三会明确改变这个选择规则。

**完整程序**

```python
def filled(n, value):
    result = []
    for i in range(n):
        result.append(value)
    return result

def indegrees(adjacency):
    degree = filled(len(adjacency), 0)
    for neighbors in adjacency:
        for target in neighbors:
            degree[target] = degree[target] + 1
    return degree

def blocked_vertices(degree):
    blocked = []
    for vertex in range(len(degree)):
        if degree[vertex] > 0:
            blocked.append(vertex)
    return blocked

def kahn(adjacency):
    degree = indegrees(adjacency)
    queue = []
    for vertex in range(len(adjacency)):
        if degree[vertex] == 0:
            queue.append(vertex)
    head = 0
    while head < len(queue):
        source = queue[head]
        head = head + 1
        for target in adjacency[source]:
            degree[target] = degree[target] - 1
            if degree[target] == 0:
                queue.append(target)
    return {"order": queue, "blocked": blocked_vertices(degree)}

print(kahn([[2], [2], [3, 4], [], []]))
print(kahn([[1], [2], [1, 3], [], [5], []]))
print(kahn([]))
```

**预期输出**

```text
{'order': [0, 1, 2, 3, 4], 'blocked': []}
{'order': [0, 4, 5], 'blocked': [1, 2, 3]}
{'order': [], 'blocked': []}
```


选题关联：来源主题 1（文末列出）。

## 把剩余入度和待处理队列放在同一张轨迹中

只看最终次序容易漏掉入度更新错误。轨迹版在处理一个源点的全部出边之后，记录源点、尚未处理的队列片段和完整入度副本。例如处理 0 后，记录 \[0,\[1\],\[0,0,1,1,1\]\]，表示 1 已经就绪，而 2 还缺一个前驱。这里记录的是处理后的状态；若改成处理前截图，所有解释和预期输出都要相应改变。

待处理片段中的每个点入度必须为零；尚未入队的点只有在最后一条未完成入边被删除后才加入。已处理点的计数也保持零，但不会再次入队，因为本实现只在减法刚产生零时追加。轨迹应保存列表副本，不能把同一个不断变化的 degree 直接塞进所有记录，否则早期记录会被后续步骤覆盖。queue\[head:\] 同样生成当时剩余队列的独立切片。

正确性与普通 Kahn 相同，复杂度却不同。若实际处理 r 个顶点，每步复制长度 n 的计数和至多 n 的队列，轨迹版总时间 O(n+a+rn+1)，轨迹占用 O(rn+r+1)，最坏二次。不能因为核心扫描仍然逐边进行，就把包含快照的整个函数写成线性。教学中可用短图观察全部状态；正式求一次次序应使用上一节不保存快照的版本。输入图未被修改，截图只描述本轮算法状态。

**完整程序**

```python
def filled(n, value):
    result = []
    for i in range(n):
        result.append(value)
    return result

def indegrees(adjacency):
    degree = filled(len(adjacency), 0)
    for neighbors in adjacency:
        for target in neighbors:
            degree[target] = degree[target] + 1
    return degree

def blocked_vertices(degree):
    blocked = []
    for vertex in range(len(degree)):
        if degree[vertex] > 0:
            blocked.append(vertex)
    return blocked

def kahn_trace(adjacency):
    degree = indegrees(adjacency)
    queue = []
    for vertex in range(len(adjacency)):
        if degree[vertex] == 0:
            queue.append(vertex)
    head = 0
    trace = []
    while head < len(queue):
        source = queue[head]
        head = head + 1
        for target in adjacency[source]:
            degree[target] = degree[target] - 1
            if degree[target] == 0:
                queue.append(target)
        trace.append([source, queue[head:], degree.copy()])
    return {"order": queue, "blocked": blocked_vertices(degree), "trace": trace}

result = kahn_trace([[2], [2], [3, 4], [], []])
for event in result["trace"]:
    print(event)
print(result["blocked"])
```

**预期输出**

```text
[0, [1], [0, 0, 1, 1, 1]]
[1, [2], [0, 0, 0, 1, 1]]
[2, [3, 4], [0, 0, 0, 0, 0]]
[3, [4], [0, 0, 0, 0, 0]]
[4, [], [0, 0, 0, 0, 0]]
[]
```


选题关联：来源主题 1（文末列出）。

## DFS 逆完成序：灰色邻居给出真正的环

DFS 把顶点分成白色未发现、灰色正在栈中、黑色已经完成。显式帧保存顶点与下一邻居下标，延续上一章的逐边模拟。遇到白色邻居就设置父边并深入；遇到黑色邻居只继续扫描，它已经完成，不能据此报告环。遇到灰色邻居 v 时，v 是当前栈上的祖先，沿父边从当前点回到 v，再加上当前出边，就得到一条闭合有向环。

如果所有根都搜索完而没有灰色回边，把完成列表反转即可。对于 u→v，若 v 初见则必先探索并完成 v，随后完成 u；若 v 已黑，仍是 v 先完成；灰色情况已被拒绝。因此逆完成序中 u 总在 v 前面。必须从所有未见顶点启动 DFS，不能只检查起点可达部分，否则另一分量的环会被遗漏。空图返回空 order 和空 cycle，表示成功；遇环则返回空 order 与首尾相同的 cycle。

环输出如 \[1,2,1\]，每对相邻顶点都必须有原方向的边，不能把从父边读到的逆序直接返回。自环会返回 \[v,v\]。找到一条环即可证明失败，不保证找出所有环，也不声称它覆盖全部阻塞点。每个顶点进入、完成各一次，每个邻接项至多检查一次，恢复一条环最多 O(n)，总时间 O(n+a+1)、空间 O(n+1)。显式栈避免长依赖链消耗 Python 递归调用层数。

**完整程序**

```python
def filled(n, value):
    result = []
    for i in range(n):
        result.append(value)
    return result

def dfs_topology(adjacency):
    n = len(adjacency)
    color = filled(n, 0)
    parent = filled(n, None)
    finished = []
    for root in range(n):
        if color[root] == 0:
            color[root] = 1
            stack = [[root, 0]]
            while len(stack) > 0:
                frame = stack[-1]
                source = frame[0]
                if frame[1] == len(adjacency[source]):
                    stack.pop()
                    color[source] = 2
                    finished.append(source)
                else:
                    target = adjacency[source][frame[1]]
                    frame[1] = frame[1] + 1
                    if color[target] == 0:
                        parent[target] = source
                        color[target] = 1
                        stack.append([target, 0])
                    elif color[target] == 1:
                        reverse_path = []
                        current = source
                        while current != target:
                            reverse_path.append(current)
                            current = parent[current]
                        cycle = [target]
                        for i in range(len(reverse_path) - 1, -1, -1):
                            cycle.append(reverse_path[i])
                        cycle.append(target)
                        return {"order": [], "cycle": cycle}
    order = []
    for i in range(len(finished) - 1, -1, -1):
        order.append(finished[i])
    return {"order": order, "cycle": []}

print(dfs_topology([[1, 2], [3], [3], []]))
print(dfs_topology([[1], [2], [1, 3], []]))
print(dfs_topology([[0]]))
```

**预期输出**

```text
{'order': [0, 2, 1, 3], 'cycle': []}
{'order': [], 'cycle': [1, 2, 1]}
{'order': [], 'cycle': [0, 0]}
```


选题关联：来源主题 1（文末列出）。

## 分层执行：一次处理当前全部就绪任务

有些问题需要并行批次，而不是一个串行排列。把初始零入度点当作第零批，处理整批的出边，把刚就绪的点放进独立 following 列表；等当前批结束才切换。不能一边遍历 ready 一边把新点追加进去，否则同一轮会吸收本应下一轮的任务。各层合起来是一种拓扑序，层内点之间没有依赖边。

在每个任务都耗时一个单位、机器数量无限且没有额外资源冲突的模型中，层号等于到达该点的最长依赖链边数。证明可以按拓扑序归纳：无前驱点属于第零层，有前驱点必须等待最晚一层的前驱完成，所以层号为前驱最大层号加一。任何合法执行都不能突破这条最长链的下界，按批执行恰好达到它。因此层数是这个特定模型的最少完工轮数。

当任务耗时不同，层号就不再等于实际开始时间；例题一会逐边传播最早完成时间。若只有两台机器，即使同层有十个互不依赖任务，也不能同时运行，本章不解决资源受限调度。图含环时，layers 只有可执行的若干批，blocked 非空必须报告失败，不能把批数当整个项目工期。普通分层实现不复制全长快照，各点只加入一个批次，时间 O(n+a+1)，计数、工作列表及全部层输出共 O(n+1) 空间。

**完整程序**

```python
def filled(n, value):
    result = []
    for i in range(n):
        result.append(value)
    return result

def indegrees(adjacency):
    degree = filled(len(adjacency), 0)
    for neighbors in adjacency:
        for target in neighbors:
            degree[target] = degree[target] + 1
    return degree

def blocked_vertices(degree):
    blocked = []
    for vertex in range(len(degree)):
        if degree[vertex] > 0:
            blocked.append(vertex)
    return blocked

def topological_layers(adjacency):
    degree = indegrees(adjacency)
    ready = []
    for vertex in range(len(adjacency)):
        if degree[vertex] == 0:
            ready.append(vertex)
    layers = []
    while len(ready) > 0:
        layers.append(ready)
        following = []
        for source in ready:
            for target in adjacency[source]:
                degree[target] = degree[target] - 1
                if degree[target] == 0:
                    following.append(target)
        ready = following
    return {"layers": layers, "blocked": blocked_vertices(degree)}

print(topological_layers([[2], [2], [3, 4], [], []]))
print(topological_layers([[1], [0], []]))
print(topological_layers([]))
```

**预期输出**

```text
{'layers': [[0, 1], [2], [3, 4]], 'blocked': []}
{'layers': [[2]], 'blocked': [0, 1]}
{'layers': [], 'blocked': []}
```


选题关联：来源主题 1（文末列出）。

<a id="examples"></a>

## 跟着做：原创例题

### 例题 1

任务依赖为 \[\[2\],\[2\],\[3,4\],\[\],\[\]\]，耗时依次为 \[2,4,3,2,1\]。任务可无限并行且不能在前驱完成前开始，求各任务的最早开始、完成时间及整个项目工期。

1. 先用 Kahn 确认整张图无环；有环返回 None。
2. 0、1 没有前驱，均从 0 开始，分别在 2、4 完成。
3. 2 等待两个前驱，因此从 4 开始，在 7 完成。
4. 3、4 都从 7 开始，分别在 9、8 完成，最大完成时间为 9。

**结果与核对**

用 start\[v\] 保存已处理前驱的最大完成时间。处理 u 时其全部前驱已完成传播，finish\[u\]=start\[u\]+durations\[u\]，再向所有后继取最大值。输入 durations 长度为 n，元素为非负整数，零耗时允许；函数不负责验证这个契约。空项目工期为 0。归纳表明每一步既满足所有前驱约束，又未加入额外等待，所以得到最早工期。时间 O(n+a+1)、空间 O(n+1)；这里按整数算术单位成本计费，不计任意大整数的位成本。

**完整程序**

```python
def filled(n, value):
    result = []
    for i in range(n):
        result.append(value)
    return result

def indegrees(adjacency):
    degree = filled(len(adjacency), 0)
    for neighbors in adjacency:
        for target in neighbors:
            degree[target] = degree[target] + 1
    return degree

def blocked_vertices(degree):
    blocked = []
    for vertex in range(len(degree)):
        if degree[vertex] > 0:
            blocked.append(vertex)
    return blocked

def kahn(adjacency):
    degree = indegrees(adjacency)
    queue = []
    for vertex in range(len(adjacency)):
        if degree[vertex] == 0:
            queue.append(vertex)
    head = 0
    while head < len(queue):
        source = queue[head]
        head = head + 1
        for target in adjacency[source]:
            degree[target] = degree[target] - 1
            if degree[target] == 0:
                queue.append(target)
    return {"order": queue, "blocked": blocked_vertices(degree)}

def earliest_finish(adjacency, durations):
    result = kahn(adjacency)
    if len(result["blocked"]) > 0:
        return None
    n = len(adjacency)
    start = filled(n, 0)
    finish = filled(n, 0)
    total = 0
    for source in result["order"]:
        finish[source] = start[source] + durations[source]
        if finish[source] > total:
            total = finish[source]
        for target in adjacency[source]:
            if finish[source] > start[target]:
                start[target] = finish[source]
    return {"start": start, "finish": finish, "total": total}

print(earliest_finish([[2], [2], [3, 4], [], []], [2, 4, 3, 2, 1]))
print(earliest_finish([[1], [0]], [1, 1]))
print(earliest_finish([], []))
```

**预期输出**

```text
{'start': [0, 0, 4, 7, 7], 'finish': [2, 4, 7, 9, 8], 'total': 9}
None
{'start': [], 'finish': [], 'total': 0}
```


### 例题 2

对 \[\[1\],\[2\],\[1,3\],\[\],\[5\],\[\]\] 同时执行 Kahn 和 DFS。解释为什么阻塞集合有三个顶点，而给出的环只有两个不同顶点。

1. 初始 0、4 入度为零；处理 0 后，1 仍有来自 2 的入边。
2. 4 释放 5，最终可移除次序为 0、4、5，剩余 1、2、3。
3. DFS 从 0 经 1 到 2，2 指向仍在栈中的 1，形成 1→2→1。
4. 3 被来自 2 的依赖阻塞，却没有返回 1 或 2 的边，不能把它认作环内点。

**结果与核对**

Kahn 的 blocked 描述无法继续移除的部分，DFS 的 cycle 是具体的闭环证据。环上的点无法释放，而它们通过依赖链还会阻塞后继。删除哪条依赖属于业务决策，程序不能凭编号自动猜测。两个算法各耗时 O(n+a+1)、空间 O(n+1)；失败时均不把局部次序冒充全图答案。

**完整程序**

```python
def filled(n, value):
    result = []
    for i in range(n):
        result.append(value)
    return result

def indegrees(adjacency):
    degree = filled(len(adjacency), 0)
    for neighbors in adjacency:
        for target in neighbors:
            degree[target] = degree[target] + 1
    return degree

def blocked_vertices(degree):
    blocked = []
    for vertex in range(len(degree)):
        if degree[vertex] > 0:
            blocked.append(vertex)
    return blocked

def kahn(adjacency):
    degree = indegrees(adjacency)
    queue = []
    for vertex in range(len(adjacency)):
        if degree[vertex] == 0:
            queue.append(vertex)
    head = 0
    while head < len(queue):
        source = queue[head]
        head = head + 1
        for target in adjacency[source]:
            degree[target] = degree[target] - 1
            if degree[target] == 0:
                queue.append(target)
    return {"order": queue, "blocked": blocked_vertices(degree)}

def dfs_topology(adjacency):
    n = len(adjacency)
    color = filled(n, 0)
    parent = filled(n, None)
    finished = []
    for root in range(n):
        if color[root] == 0:
            color[root] = 1
            stack = [[root, 0]]
            while len(stack) > 0:
                frame = stack[-1]
                source = frame[0]
                if frame[1] == len(adjacency[source]):
                    stack.pop()
                    color[source] = 2
                    finished.append(source)
                else:
                    target = adjacency[source][frame[1]]
                    frame[1] = frame[1] + 1
                    if color[target] == 0:
                        parent[target] = source
                        color[target] = 1
                        stack.append([target, 0])
                    elif color[target] == 1:
                        reverse_path = []
                        current = source
                        while current != target:
                            reverse_path.append(current)
                            current = parent[current]
                        cycle = [target]
                        for i in range(len(reverse_path) - 1, -1, -1):
                            cycle.append(reverse_path[i])
                        cycle.append(target)
                        return {"order": [], "cycle": cycle}
    order = []
    for i in range(len(finished) - 1, -1, -1):
        order.append(finished[i])
    return {"order": order, "cycle": []}

graph = [[1], [2], [1, 3], [], [5], []]
print(kahn(graph))
print(dfs_topology(graph))
```

**预期输出**

```text
{'order': [0, 4, 5], 'blocked': [1, 2, 3]}
{'order': [], 'cycle': [1, 2, 1]}
```


<a id="practice"></a>

## 自己做：先完成再看解答

### 练习 1

判断一个 DAG 的拓扑序是否唯一；有环返回 None。分别检查链 \[\[1\],\[2\],\[\]\]、\[\[2\],\[2\],\[\]\] 和空图，返回一个次序以及 unique。

<details>
<summary>提示</summary>

观察 Kahn 每一步真正未处理的零入度点数量，即队列长度减 head；不要把已处理前缀也算进去。

</details>

<details>
<summary>解答与检查</summary>

若某步有两个就绪点，可以分别先选它们，得到不同合法次序；若每步只有一个，则每个位置都被迫确定。必须先确认能处理全部顶点，有环图没有拓扑序，不能报告“唯一”。空图恰有一个空排列，unique 为 True。计数检查为常数工作，时间 O(n+a+1)、空间 O(n+1)。

**完整程序**

```python
def filled(n, value):
    result = []
    for i in range(n):
        result.append(value)
    return result

def indegrees(adjacency):
    degree = filled(len(adjacency), 0)
    for neighbors in adjacency:
        for target in neighbors:
            degree[target] = degree[target] + 1
    return degree

def blocked_vertices(degree):
    blocked = []
    for vertex in range(len(degree)):
        if degree[vertex] > 0:
            blocked.append(vertex)
    return blocked

def topological_unique(adjacency):
    degree = indegrees(adjacency)
    queue = []
    for vertex in range(len(adjacency)):
        if degree[vertex] == 0:
            queue.append(vertex)
    head = 0
    unique = True
    while head < len(queue):
        if len(queue) - head > 1:
            unique = False
        source = queue[head]
        head = head + 1
        for target in adjacency[source]:
            degree[target] = degree[target] - 1
            if degree[target] == 0:
                queue.append(target)
    if len(queue) != len(adjacency):
        return None
    return {"order": queue, "unique": unique}

print(topological_unique([[1], [2], []]))
print(topological_unique([[2], [2], []]))
print(topological_unique([[1], [0]]))
print(topological_unique([]))
```

**预期输出**

```text
{'order': [0, 1, 2], 'unique': True}
{'order': [0, 1, 2], 'unique': False}
None
{'order': [], 'unique': True}
```


</details>

### 练习 2

给定 DAG 和起点，计算到每个顶点的有向路径条数。起点到自身的零边路径计作一条，不可达点为零；起点越界或全图有环都返回 None。检查 \[\[1,2\],\[3\],\[3\],\[\],\[\]\] 从 0 出发。

<details>
<summary>提示</summary>

初始化 count\[start\]=1，按拓扑序将源点已累积的条数加到每个后继。不要沿每条路线重新搜索整个后续图。

</details>

<details>
<summary>解答与检查</summary>

结果为 \[1,1,1,2,0\]。到 v 的非空路径按最后一条入边分类，各类互不重叠，因而相加；处理 v 时全部前驱已处理，计数已经完整。DAG 保证不会通过环产生无限条游走。单位算术模型下时间 O(n+a+1)、空间 O(n+1)，但路径数量可能指数增长，Python 大整数加法和存储还要计入位数成本。

**完整程序**

```python
def filled(n, value):
    result = []
    for i in range(n):
        result.append(value)
    return result

def indegrees(adjacency):
    degree = filled(len(adjacency), 0)
    for neighbors in adjacency:
        for target in neighbors:
            degree[target] = degree[target] + 1
    return degree

def blocked_vertices(degree):
    blocked = []
    for vertex in range(len(degree)):
        if degree[vertex] > 0:
            blocked.append(vertex)
    return blocked

def kahn(adjacency):
    degree = indegrees(adjacency)
    queue = []
    for vertex in range(len(adjacency)):
        if degree[vertex] == 0:
            queue.append(vertex)
    head = 0
    while head < len(queue):
        source = queue[head]
        head = head + 1
        for target in adjacency[source]:
            degree[target] = degree[target] - 1
            if degree[target] == 0:
                queue.append(target)
    return {"order": queue, "blocked": blocked_vertices(degree)}

def count_dag_paths(adjacency, start):
    n = len(adjacency)
    if start < 0 or start >= n:
        return None
    result = kahn(adjacency)
    if len(result["blocked"]) > 0:
        return None
    count = filled(n, 0)
    count[start] = 1
    for source in result["order"]:
        for target in adjacency[source]:
            count[target] = count[target] + count[source]
    return count

print(count_dag_paths([[1, 2], [3], [3], [], []], 0))
print(count_dag_paths([[1], [0], []], 2))
print(count_dag_paths([], 0))
```

**预期输出**

```text
[1, 1, 1, 2, 0]
None
None
```


</details>

### 练习 3

用最小堆代替 FIFO，返回字典序最小的拓扑序；有环返回 None。用 \[\[1\],\[\],\[\]\] 说明它与普通 Kahn 的结果可能不同。

<details>
<summary>提示</summary>

把所有当前零入度点放入第 18 章最小堆，每次取出最小编号；新释放的点也立即进入同一个堆。

</details>

<details>
<summary>解答与检查</summary>

普通 FIFO 先放入 0、2，处理 0 后才追加 1，得到 \[0,2,1\]；堆版本得到 \[0,1,2\]。任何合法次序的下一点必须来自当前就绪集合，取其中最小者可使当前位置最小，再对剩余图重复，构成字典序贪心证明。每点至多一次入堆和出堆，时间 O(n+a+n log(n+1)+1)、空间 O(n+1)。选择规则可重复不代表原图只有一种拓扑序。

**完整程序**

```python
def filled(n, value):
    result = []
    for i in range(n):
        result.append(value)
    return result

def indegrees(adjacency):
    degree = filled(len(adjacency), 0)
    for neighbors in adjacency:
        for target in neighbors:
            degree[target] = degree[target] + 1
    return degree

def blocked_vertices(degree):
    blocked = []
    for vertex in range(len(degree)):
        if degree[vertex] > 0:
            blocked.append(vertex)
    return blocked

def heap_swap(heap, left, right):
    saved = heap[left]
    heap[left] = heap[right]
    heap[right] = saved

def sift_up(heap, index):
    while index > 0:
        parent = (index - 1) // 2
        if heap[parent] <= heap[index]:
            return
        heap_swap(heap, parent, index)
        index = parent

def heap_push(heap, value):
    heap.append(value)
    sift_up(heap, len(heap) - 1)

def sift_down(heap, index, size):
    while 2 * index + 1 < size:
        child = 2 * index + 1
        right = child + 1
        if right < size and heap[right] < heap[child]:
            child = right
        if heap[index] <= heap[child]:
            return
        heap_swap(heap, index, child)
        index = child

def heap_pop(heap):
    if len(heap) == 0:
        return None
    smallest = heap[0]
    last = heap.pop()
    if len(heap) > 0:
        heap[0] = last
        sift_down(heap, 0, len(heap))
    return smallest

def topological_smallest(adjacency):
    degree = indegrees(adjacency)
    heap = []
    for vertex in range(len(adjacency)):
        if degree[vertex] == 0:
            heap_push(heap, vertex)
    order = []
    while len(heap) > 0:
        source = heap_pop(heap)
        order.append(source)
        for target in adjacency[source]:
            degree[target] = degree[target] - 1
            if degree[target] == 0:
                heap_push(heap, target)
    if len(order) != len(adjacency):
        return None
    return order

print(topological_smallest([[1], [], []]))
print(topological_smallest([[1], [0]]))
print(topological_smallest([]))
```

**预期输出**

```text
[0, 1, 2]
None
[]
```


</details>

<a id="pitfalls"></a>

## 容易混淆的地方

- **把 DFS 发现序、BFS 次序或 Kahn 的局部前缀当完整拓扑序。** 检验全体顶点恰出现一次，并检查所有原图边的方向；失败结果单独处理。
- **把 blocked 中所有点都称作环成员，或把黑色邻居当作 DFS 回边。** 阻塞可能沿环向后传播；当前栈上的灰色邻居才提供祖先回边证据。
- **把并行层数直接当任意任务系统的工期。** 层数结论要求单位耗时与无限资源；不同耗时要传播完成时间，有限机器还需额外调度。
- **把轨迹复制和大整数计数隐去，仍声称所有版本都严格线性。** 普通扫描、完整状态截图、路径计数的位成本应分别收费。

<a id="self-check"></a>

## 离开这一章前

- [ ] 用位置表检验次序，包含重复、漏点、越界、自环与空图。
- [ ] 手动解释每次入度减一对应哪一条已处理出边。
- [ ] 核查 DFS 环的每一条边，并区别环成员与受阻后继。
- [ ] 用最长依赖链解释分层与最早完工，写清资源模型。
- [ ] 为唯一性、字典序最小和路径计数分别说明不变式与失败约定。

## 本章边界

- 输入邻接表及编号类型由调用者保证合法，允许自环用于报告循环依赖，不做任意类型校验。
- 只找一条有向环，不求强连通分量、全部环或最少删边方案。
- 排程假设任务耗时非负、无资源冲突，不处理有限机器或动态依赖更新。
- 复杂度以单位整数操作、动态列表追加摊还成本计算，路径数量很大时需另计位复杂度。

## 选题来源与覆盖

来源含学生报告时，仅将其作为选题线索；具体机制仍需结合后续实验或权威资料核对。

- [大一小学期/Week\_3-Python/docs/readme.md](https://github.com/PKUanonym/REKCARC-TSC-UHT/blob/37cd19f7a9fb80dc846a7016b3fd482ed5fe7cc0/%E5%A4%A7%E4%B8%80%E5%B0%8F%E5%AD%A6%E6%9C%9F/Week_3-Python/docs/readme.md)（已提取可读文本，固定版本 37cd19f7a9fb）
- 主题 1：Python 基础语法的外部学习入口；位置：第 41–80 行。
- 主题 2：从基础语法到工具与应用的建议阅读顺序；位置：第 121–160 行。

## 参考资料与规则核对

上游入口用于确定学习方向；下面的参考资料用于核对语言语义、数据结构或算法分析规则，例题和练习由本项目重新设计。

- [NIST DADS：拓扑排序](https://xlinux.nist.gov/dads/HTML/topologicalSort.html)：核对按偏序安排项目的定义；本章图、数值和全部 Python 程序为原创教学示例。
- [Aalto CS-A1140：拓扑排序与 DFS](https://tarjotin.cs.aalto.fi/CS-A1140/2020/notes/graphs-topological.html)：核对有向无环条件、完成次序和灰色状态。这里使用显式帧恢复一条闭合环，并独立验证排程与计数练习。
- [Algorithms 4/e：TopologicalX](https://algs4.cs.princeton.edu/code/javadoc/edu/princeton/cs/algs4/TopologicalX.html)：核对队列式拓扑排序及存在性条件；本章返回阻塞前缀和剩余点，接口与 Java 实现不同，不将剩余点等同于环成员。

**继续学习**：先独立完成自测，再记录仍需回读的步骤。

[上一章：沿边系统探索：DFS、BFS 与无权最短路径](21-graph-traversal.md) · [下一章：比较路线总费用：带权最短路与松弛](23-weighted-shortest-paths.md)

[教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [哈希表与图练习指引](../hash-graphs-practice.md) · [拓扑排序与带权图练习指引](../weighted-graphs-practice.md) · [记录自己的学习](../learning-log-template.md)
