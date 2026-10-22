# 比较路线总费用：带权最短路与松弛

[返回教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [哈希表与图练习指引](../hash-graphs-practice.md) · [拓扑排序与带权图练习指引](../weighted-graphs-practice.md)

[上一章：安排有向依赖：拓扑排序与 DAG 应用](22-topological-sort.md) · [下一章：以最低总费用连接全图：最小生成树与并查集](24-minimum-spanning-trees.md)

[学习目标](#objectives) · [需要的基础](#prerequisites) · [例题](#examples) · [练习](#practice) · [自测](#self-check)

状态：**AI 初稿，可开始试学**。生成模型：Codex 当前会话（未记录具体模型型号）。

本章围绕资料中识别到的知识点重新编写；讲解、数值模型、例题与练习为 AI 原创组织，不是原课程题目或答案。主题出处只说明选题关联，不证明全部推导已经正确。

从宿舍到实验室，一条直达路线可能很慢，两段换乘反而更快。上一章之前学习的 BFS 只最小化边数；现在每条边带有整数费用，目标改为沿途费用之和最小。本章以松弛作为共同操作，先解释非负权下为何可以确定当前最近点，再分别实现扫描版和堆版 Dijkstra；有负权边时改用 Bellman–Ford。练习把父边恢复、DAG 次序和有限步数联系起来，让算法选择建立在明确的权重与结构条件上。

<a id="objectives"></a>

## 学完要能做到

- 区分边数最少、总权最小、不可达和负环导致的无有限最优值。
- 解释松弛的候选路径意义，并用非负权条件证明 Dijkstra 的确定步骤。
- 实现扫描与懒堆 Dijkstra，正确跳过旧记录并计算堆空间。
- 实现 Bellman–Ford、DAG 最短路和至多 k 条边的最小费用，区分各自的轮次含义。

<a id="prerequisites"></a>

## 需要的基础

- 掌握第 20、21 章方向、路径恢复和 BFS 的最少边数结论。
- 掌握第 18 章最小堆及第 22 章完整拓扑序。
- 能够按不变式区分暂定值与已确定值，并理解 None 与整数的不同语义。

## 带权表示：最短的量从边数改为费用和

加权邻接表的每项改为 \[终点,权重\]，输入边为 \[起点,终点,权重\]。顶点仍编号 0 至 n−1，n 是非负整数，每个有向端点对至多一条边，权重是整数；本章允许自环来讨论负环。构造器要求输入已经符合契约，直接创建独立邻接行并追加，不承担第 20 章的查重和非法端点拒绝。无向模式要求每条无向边只给一次且不含自环，程序写入两个方向；本章最短路主要使用有向模式。

示例有 0→1 费用 9，0→2 费用 2，2→1 费用 1。BFS 会给 1 选择一条直达边，但最小总费用是绕经 2 的 3。path\_weight 逐段查找对应方向的边，检查给定路线的费用；一条合法零边路线费用为 0，空路线、越界点或缺失边返回 None。它不是最短路算法，仅用于核验候选路线。若路线反复访问顶点，这个函数仍按游走计算费用。

零权边是正常连接，不能用 0 表示无边；负距离也可能合法，所以不能沿用 BFS 的 −1 不可达标记。本章以 None 表示尚未找到路线，起点距离为 0。负环指一圈边权和为负，从起点能到达它并继续到目标时，多绕几圈就能无限降低该目标的游走费用。本章不求带负环约束的最短简单路径。建图时间和空间 O(n+a+1)；路线核查会扫描所访问的邻接行，长度 p 的一般游走可达 O(p(n+1)+1) 时间，额外空间 O(1)。

**完整程序**

```python
def weighted_adjacency(n, edges, directed):
    adjacency = []
    for vertex in range(n):
        adjacency.append([])
    for edge in edges:
        source = edge[0]
        target = edge[1]
        weight = edge[2]
        adjacency[source].append([target, weight])
        if not directed:
            adjacency[target].append([source, weight])
    return adjacency

def path_weight(adjacency, path):
    if len(path) == 0:
        return None
    for vertex in path:
        if vertex < 0 or vertex >= len(adjacency):
            return None
    total = 0
    for i in range(1, len(path)):
        found = False
        for edge in adjacency[path[i - 1]]:
            if edge[0] == path[i]:
                total = total + edge[1]
                found = True
        if not found:
            return None
    return total

graph = weighted_adjacency(4, [[0, 1, 9], [0, 2, 2], [2, 1, 1]], True)
print(graph)
print(path_weight(graph, [0, 1]))
print(path_weight(graph, [0, 2, 1]))
print(path_weight(graph, [3]))
print(path_weight(graph, [1, 0]))
```

**预期输出**

```text
[[[1, 9], [2, 2]], [], [[1, 1]], []]
9
3
0
None
```


选题关联：来源主题 1（文末列出）。

## 松弛：用一条新路线尝试改小暂定距离

假设已知一条从起点到 u 的路线费用 distance\[u\]，再接 u→v 权重 w，便得到候选费用 distance\[u\]+w。若 v 尚不可达，或候选值严格更小，就更新 distance\[v\] 并把 parent\[v\] 设为 u，这一步叫松弛。源点为 None 时没有已知路线，不能把它当零相加，也不能凭一条负边制造可达性。relax 返回布尔值，告诉调用者是否真的改善。

松弛保持的事实是：每个有限距离都来自一条实际游走，因此它是最优值的上界，而不一定已经最优。示例先把 1 设为 9，再发现经 2 的费用 3，于是改写为 3。若另一条候选恰好也是 3，程序不改父边；严格比较能避免等长候选不断制造堆记录，也防止在零权环上仅为打破平局而重写父链。最终父链的正确性仍依赖外层算法的成功条件，不能把随意顺序执行几次松弛的数组直接当作最短路解。

一次松弛只访问常数个位置，单位整数算术下耗时和额外空间 O(1)。它会修改传入的 distance 与 parent，这是接口的预期行为，但不会修改图。Python 整数可以很大，若权重或路径和需要很多位，比较与加法还需额外位成本；本章示例使用整数以避免浮点 NaN、舍入和平局误差。后续三个算法的差别，主要在于按什么次序尝试这些松弛，以及何时能证明已经不需要改善。

**完整程序**

```python
def filled(n, value):
    result = []
    for i in range(n):
        result.append(value)
    return result

def relax(distance, parent, source, target, weight):
    if distance[source] is None:
        return False
    candidate = distance[source] + weight
    if distance[target] is None or candidate < distance[target]:
        distance[target] = candidate
        parent[target] = source
        return True
    return False

distance = [0, None, 2, None]
parent = filled(4, None)
print(relax(distance, parent, 0, 1, 9))
print(relax(distance, parent, 2, 1, 1))
print(relax(distance, parent, 2, 1, 1))
print(relax(distance, parent, 3, 1, -100))
print(distance)
print(parent)
```

**预期输出**

```text
True
True
False
False
[0, 3, 2, None]
[None, 2, None, None]
```


选题关联：来源主题 1（文末列出）。

## 扫描版 Dijkstra：为何能确定当前最近点

Dijkstra 每轮从未确定且距离有限的顶点中选暂定距离最小者，将它确定，再松弛它通向未确定点的边。扫描版用 used 标记已确定点，逐个检查全部顶点寻找最小值；相同距离按编号先后选择。若已经没有有限候选，剩余点全不可达，立即返回。输入起点是整数，越界返回 None；本章接口也会先扫描全图，任何负权边都返回 None，包括起点无法到达的部分。

为什么非负权允许确定？设已经确定的集合为 S，当前选中的 u 暂定距离最小。若有更短的起点到 u 路线，沿它找到第一个离开 S 的点 y，它的前驱在 S 内，处理前驱时应已给 y 一个不大于这段前缀的候选。后续边非负，使前缀不大于整条更短路线，于是 y 的暂定值比 u 更小，与选点规则矛盾。起点的零距离作为归纳起点，后续依次成立。

一旦存在负边，后半段路线可能使费用下降，前面的不等式就不成立。例如 0→1 为 2、0→2 为 5、2→1 为 −4，过早确定 1 会错过费用 1 的路线。本实现直接拒绝这类输入，不尝试重开已确定点。最坏进行 n 轮长度 n 的选点扫描，边检查 O(a)，时间 O(n²+a+1)，distance、parent、used 占 O(n+1)。只返回父边数组，不为每个目标复制一整条路线。

**完整程序**

```python
def filled(n, value):
    result = []
    for i in range(n):
        result.append(value)
    return result

def relax(distance, parent, source, target, weight):
    if distance[source] is None:
        return False
    candidate = distance[source] + weight
    if distance[target] is None or candidate < distance[target]:
        distance[target] = candidate
        parent[target] = source
        return True
    return False

def nonnegative_weights(adjacency):
    for neighbors in adjacency:
        for edge in neighbors:
            if edge[1] < 0:
                return False
    return True

def dijkstra_scan(adjacency, start):
    n = len(adjacency)
    if start < 0 or start >= n or not nonnegative_weights(adjacency):
        return None
    distance = filled(n, None)
    parent = filled(n, None)
    used = filled(n, False)
    distance[start] = 0
    for step in range(n):
        best = None
        for vertex in range(n):
            if not used[vertex] and distance[vertex] is not None:
                if best is None or distance[vertex] < distance[best]:
                    best = vertex
        if best is None:
            return {"distance": distance, "parent": parent}
        used[best] = True
        for edge in adjacency[best]:
            if not used[edge[0]]:
                relax(distance, parent, best, edge[0], edge[1])
    return {"distance": distance, "parent": parent}

graph = [[[1, 9], [2, 2]], [], [[1, 1]], []]
print(dijkstra_scan(graph, 0))
print(dijkstra_scan([[[1, 2], [2, 5]], [], [[1, -4]]], 0))
print(dijkstra_scan([], 0))
```

**预期输出**

```text
{'distance': [0, 3, 2, None], 'parent': [None, 2, 0, None]}
None
None
```


选题关联：来源主题 1（文末列出）。

## 懒堆 Dijkstra：旧候选留下，取出时核对

为避免每轮扫描全体顶点，可以让最小堆保存 \[暂定费用,顶点\]。列表按字典序比较，先费用、后编号。每次成功松弛就追加一个新记录；不用在堆内部寻找并修改旧记录。弹出时，若记录费用不等于 distance 中的当前值，它已经过期，直接跳过。只有费用仍匹配的记录才扫描该顶点出边。第 18 章的堆辅助函数在程序中完整展开，使本段可以独立执行。

例如 1 先以费用 9 入堆，随后被改进为 3，又入堆一次。费用 3 的记录先处理，之后弹出 9 时跳过。严格松弛不会把同一顶点同一费用重复入堆；在全图非负权条件下，有效弹出就是上一节的确定步骤，此后不会再变小，所以每个可达点的出边只在有效弹出时扫描一次。零权边及等长路线仍满足此结论。若去掉旧记录检查，算法可能反复扫描相同行，原有工作量分析就失效。

最多 a 次成功边松弛，加起点共至多 a+1 次入堆，堆中可能同时保留很多旧记录。采用逐次 heap\_push，安全时间界为 O(n+a+(a+1)log(a+2))，包含全图非负检查与状态初始化；空间 O(n+a+1)，不能写成堆始终只有 n 个元素。动态列表追加按摊还成本计。扫描版与堆版的距离应相同，等长路径可能选出不同父边，验收应比较路径合法性与费用，不把某个父边选择当唯一标准。

**完整程序**

```python
def filled(n, value):
    result = []
    for i in range(n):
        result.append(value)
    return result

def relax(distance, parent, source, target, weight):
    if distance[source] is None:
        return False
    candidate = distance[source] + weight
    if distance[target] is None or candidate < distance[target]:
        distance[target] = candidate
        parent[target] = source
        return True
    return False

def nonnegative_weights(adjacency):
    for neighbors in adjacency:
        for edge in neighbors:
            if edge[1] < 0:
                return False
    return True

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

def dijkstra_heap(adjacency, start):
    n = len(adjacency)
    if start < 0 or start >= n or not nonnegative_weights(adjacency):
        return None
    distance = filled(n, None)
    parent = filled(n, None)
    distance[start] = 0
    heap = []
    heap_push(heap, [0, start])
    while len(heap) > 0:
        entry = heap_pop(heap)
        source = entry[1]
        if entry[0] == distance[source]:
            for edge in adjacency[source]:
                if relax(distance, parent, source, edge[0], edge[1]):
                    heap_push(heap, [distance[edge[0]], edge[0]])
    return {"distance": distance, "parent": parent}

graph = [[[1, 9], [2, 2]], [], [[1, 1]], []]
print(dijkstra_heap(graph, 0))
print(dijkstra_heap([[[1, 0]], [[0, 0]]], 0))
print(dijkstra_heap([[], [[2, -1]], []], 0))
```

**预期输出**

```text
{'distance': [0, 3, 2, None], 'parent': [None, 2, 0, None]}
{'distance': [0, 0], 'parent': [None, 0]}
None
```


选题关联：来源主题 1（文末列出）。

## Bellman–Ford：允许负边，并检查可达负环

Bellman–Ford 不按当前距离永久确定顶点，而是反复扫描全部边进行松弛，最多做 n−1 轮。没有源可达负环时，任意最优游走可以删去非负环，得到至多 n−1 条边的最短简单路径。第一轮至少覆盖一条边的最优路线，第二轮至少覆盖两条，依次归纳，n−1 轮足够。本实现原地更新，同一轮可能顺着边排列传播多步，因此应说“至少覆盖”，不能说每轮恰好只增加一条边。

若一整轮没有改善，距离已经稳定，可提前结束。之后再扫描一遍：某条从有限距离源点出发的边还能改善，就报告 negative\_cycle 为 True。无可达负环时最短简单路径已被覆盖，不应再改善；有可达负环时，若环上所有边都不能改善，把不等式沿环相加会推出环权非负，产生矛盾。源点不可达的负环不会触发，因为它的距离仍是 None。

成功时返回距离、父边和 negative\_cycle=False；有源可达负环时返回 True 与空距离、空父边，拒绝交付部分答案。这不表示全图每个目标都可无限变小，只有负环能够到达的目标受影响，本章未细分这些点。起点越界返回 None。程序先用 O(n+a+1) 将邻接表展平为边表，再做完整轮次，避免每轮扫描许多空行；时间 O(n+na+1)、额外空间 O(n+a+1)。这份代码是完整边表轮次版，不是队列优化版，也不恢复负环本身。

**完整程序**

```python
def filled(n, value):
    result = []
    for i in range(n):
        result.append(value)
    return result

def relax(distance, parent, source, target, weight):
    if distance[source] is None:
        return False
    candidate = distance[source] + weight
    if distance[target] is None or candidate < distance[target]:
        distance[target] = candidate
        parent[target] = source
        return True
    return False

def bellman_ford(adjacency, start):
    n = len(adjacency)
    if start < 0 or start >= n:
        return None
    edges = []
    for source in range(n):
        for edge in adjacency[source]:
            edges.append([source, edge[0], edge[1]])
    distance = filled(n, None)
    parent = filled(n, None)
    distance[start] = 0
    changed = True
    rounds = 0
    while rounds < n - 1 and changed:
        changed = False
        for edge in edges:
            if relax(distance, parent, edge[0], edge[1], edge[2]):
                changed = True
        rounds = rounds + 1
    for edge in edges:
        source = edge[0]
        target = edge[1]
        if distance[source] is not None:
            candidate = distance[source] + edge[2]
            if distance[target] is None or candidate < distance[target]:
                return {"negative_cycle": True, "distance": [], "parent": []}
    return {"negative_cycle": False, "distance": distance, "parent": parent}

print(bellman_ford([[[1, 4], [2, 5]], [[2, -2]], [[3, 3]], []], 0))
print(bellman_ford([[[1, 1]], [[2, -3]], [[1, 1]]], 0))
print(bellman_ford([], 0))
```

**预期输出**

```text
{'negative_cycle': False, 'distance': [0, 4, 2, 5], 'parent': [None, 0, 1, 2]}
{'negative_cycle': True, 'distance': [], 'parent': []}
None
```


选题关联：来源主题 1（文末列出）。

<a id="examples"></a>

## 跟着做：原创例题

### 例题 1

对边 0→1=7、0→2=2、2→1=1、2→3=8、2→4=12、1→3=2、3→4=1，从 0 执行懒堆 Dijkstra，区分有效弹出和过期记录。

1. 先确定 0，生成 1 的费用 7 与 2 的费用 2。
2. 确定 2，改善 1 为 3，并生成 3 的 10 与 4 的 14。
3. 确定 1，把 3 改为 5；确定 3，把 4 改为 6；随后确定 4。
4. 最后弹出的 1 的 7、3 的 10、4 的 14 都已过期，跳过出边扫描。

**结果与核对**

距离依次为 \[0,3,2,5,6\]，父边为 \[None,2,0,1,3\]。有效弹出的费用非递减，过期事件不是第二次确定顶点。本例只为每次弹出保存一条常数长度事件，不复制整张距离表；事件数量 O(a+1)，因此时间界与懒堆算法相同，包含事件的空间仍为 O(n+a+1)。所有记录都处理完才结束，没有使用到达单一目标的提前停止。

**完整程序**

```python
def filled(n, value):
    result = []
    for i in range(n):
        result.append(value)
    return result

def relax(distance, parent, source, target, weight):
    if distance[source] is None:
        return False
    candidate = distance[source] + weight
    if distance[target] is None or candidate < distance[target]:
        distance[target] = candidate
        parent[target] = source
        return True
    return False

def nonnegative_weights(adjacency):
    for neighbors in adjacency:
        for edge in neighbors:
            if edge[1] < 0:
                return False
    return True

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

def dijkstra_heap_trace(adjacency, start):
    n = len(adjacency)
    if start < 0 or start >= n or not nonnegative_weights(adjacency):
        return None
    distance = filled(n, None)
    parent = filled(n, None)
    distance[start] = 0
    heap = []
    heap_push(heap, [0, start])
    events = []
    while len(heap) > 0:
        entry = heap_pop(heap)
        source = entry[1]
        if entry[0] == distance[source]:
            events.append(["settle", source, entry[0]])
            for edge in adjacency[source]:
                if relax(distance, parent, source, edge[0], edge[1]):
                    heap_push(heap, [distance[edge[0]], edge[0]])
        else:
            events.append(["skip", source, entry[0]])
    return {"distance": distance, "parent": parent, "events": events}

graph = [[[1, 7], [2, 2]], [[3, 2]], [[1, 1], [3, 8], [4, 12]], [[4, 1]], []]
result = dijkstra_heap_trace(graph, 0)
print(result["distance"])
print(result["parent"])
for event in result["events"]:
    print(event)
```

**预期输出**

```text
[0, 3, 2, 5, 6]
[None, 2, 0, 1, 3]
['settle', 0, 0]
['settle', 2, 2]
['settle', 1, 3]
['settle', 3, 5]
['settle', 4, 6]
['skip', 1, 7]
['skip', 3, 10]
['skip', 4, 14]
```


### 例题 2

一张图有边 0→1=2，以及另一部分 3→4=−3、4→3=1，顶点 2 孤立。从 0 和从 3 调用 Bellman–Ford，为什么结果不同？

1. 从 0 只能到达 0、1，3 和 4 的距离始终为 None。
2. 虽然 3→4→3 的总权为 −2，但从 0 无法到达，不能影响这个源的距离。
3. 改从 3 出发，绕一圈可使费用减少 2，n−1 轮后仍有可改善边。
4. 第二次调用报告源可达负环，并按接口返回空距离与父边。

**结果与核对**

从 0 得到 \[0,2,None,None,None\]；从 3 检测到负环。负权边本身不等于负环，某处有负环也不等于每个源都受影响。Dijkstra 的全图负权拒绝属于本教材的更强输入契约，不能拿它的拒绝结果推出“从 0 的最短路不存在”。两次 Bellman–Ford 各用独立状态，原图保持不变；最坏时间 O(n+na+1)、空间 O(n+a+1)。

**完整程序**

```python
def filled(n, value):
    result = []
    for i in range(n):
        result.append(value)
    return result

def relax(distance, parent, source, target, weight):
    if distance[source] is None:
        return False
    candidate = distance[source] + weight
    if distance[target] is None or candidate < distance[target]:
        distance[target] = candidate
        parent[target] = source
        return True
    return False

def bellman_ford(adjacency, start):
    n = len(adjacency)
    if start < 0 or start >= n:
        return None
    edges = []
    for source in range(n):
        for edge in adjacency[source]:
            edges.append([source, edge[0], edge[1]])
    distance = filled(n, None)
    parent = filled(n, None)
    distance[start] = 0
    changed = True
    rounds = 0
    while rounds < n - 1 and changed:
        changed = False
        for edge in edges:
            if relax(distance, parent, edge[0], edge[1], edge[2]):
                changed = True
        rounds = rounds + 1
    for edge in edges:
        source = edge[0]
        target = edge[1]
        if distance[source] is not None:
            candidate = distance[source] + edge[2]
            if distance[target] is None or candidate < distance[target]:
                return {"negative_cycle": True, "distance": [], "parent": []}
    return {"negative_cycle": False, "distance": distance, "parent": parent}

graph = [[[1, 2]], [], [], [[4, -3]], [[3, 1]]]
print(bellman_ford(graph, 0))
print(bellman_ford(graph, 3))
```

**预期输出**

```text
{'negative_cycle': False, 'distance': [0, 2, None, None, None], 'parent': [None, 0, None, None, None]}
{'negative_cycle': True, 'distance': [], 'parent': []}
```


<a id="practice"></a>

## 自己做：先完成再看解答

### 练习 1

为已经成功得到的最短路数组恢复一条到目标的路径。越界或不可达返回 \[\]，起点到自身返回单点列表。用本章三角图加孤立点，恢复从 0 到 1、3、0 的路径。

<details>
<summary>提示</summary>

先看 distance 是否为 None，再从目标沿 parent 追踪至 None，最后反转。parent 的 None 同时用于起点和不可达点，不能单靠它判断可达。

</details>

<details>
<summary>解答与检查</summary>

得到 \[0,2,1\]、\[\]、\[0\]。函数前提是数组来自成功的 Dijkstra、DAG 最短路或无可达负环的 Bellman–Ford，且未被修改，不负责修复任意伪造父链。每条父边应存在，路径权重和应等于目标距离。恢复 p 个顶点需 O(p+1) 时间和空间；示例包含扫描版搜索，总时间 O(n²+a+1)、空间 O(n+1)。

**完整程序**

```python
def filled(n, value):
    result = []
    for i in range(n):
        result.append(value)
    return result

def relax(distance, parent, source, target, weight):
    if distance[source] is None:
        return False
    candidate = distance[source] + weight
    if distance[target] is None or candidate < distance[target]:
        distance[target] = candidate
        parent[target] = source
        return True
    return False

def nonnegative_weights(adjacency):
    for neighbors in adjacency:
        for edge in neighbors:
            if edge[1] < 0:
                return False
    return True

def dijkstra_scan(adjacency, start):
    n = len(adjacency)
    if start < 0 or start >= n or not nonnegative_weights(adjacency):
        return None
    distance = filled(n, None)
    parent = filled(n, None)
    used = filled(n, False)
    distance[start] = 0
    for step in range(n):
        best = None
        for vertex in range(n):
            if not used[vertex] and distance[vertex] is not None:
                if best is None or distance[vertex] < distance[best]:
                    best = vertex
        if best is None:
            return {"distance": distance, "parent": parent}
        used[best] = True
        for edge in adjacency[best]:
            if not used[edge[0]]:
                relax(distance, parent, best, edge[0], edge[1])
    return {"distance": distance, "parent": parent}

def recover_path(distance, parent, target):
    if target < 0 or target >= len(distance) or distance[target] is None:
        return []
    reverse_path = []
    current = target
    while current is not None:
        reverse_path.append(current)
        current = parent[current]
    path = []
    for i in range(len(reverse_path) - 1, -1, -1):
        path.append(reverse_path[i])
    return path

result = dijkstra_scan([[[1, 9], [2, 2]], [], [[1, 1]], []], 0)
print(recover_path(result["distance"], result["parent"], 1))
print(recover_path(result["distance"], result["parent"], 3))
print(recover_path(result["distance"], result["parent"], 0))
print(recover_path(result["distance"], result["parent"], -1))
```

**预期输出**

```text
[0, 2, 1]
[]
[0]
[]
```


</details>

### 练习 2

利用拓扑排序为带负权边的 DAG 求单源最短路。起点越界或全图有环返回 None；没有起点可达路线的顶点距离为 None。检查 0→1=4、0→2=5、1→2=−2、2→3=3。

<details>
<summary>提示</summary>

先取每项的终点，构造无权邻接表并验证完整拓扑序，再按序松弛每条出边。负权不会破坏依赖先后关系。

</details>

<details>
<summary>解答与检查</summary>

得到距离 \[0,4,2,5\]。处理 v 时，所有可能作为最后一步的前驱都已经完成，取其候选最小值即可；图无环保证不需要返回重算，也不可能有负环。与 Dijkstra 按暂定费用选点不同，这里按结构次序处理，所以允许负边。复制无权邻接表、Kahn 和松弛总时间 O(n+a+1)，本实现额外空间 O(n+a+1)。即使环位于源不可达部分也返回 None，这是全图 DAG 契约。

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

def relax(distance, parent, source, target, weight):
    if distance[source] is None:
        return False
    candidate = distance[source] + weight
    if distance[target] is None or candidate < distance[target]:
        distance[target] = candidate
        parent[target] = source
        return True
    return False

def dag_shortest_paths(adjacency, start):
    n = len(adjacency)
    if start < 0 or start >= n:
        return None
    unweighted = []
    for neighbors in adjacency:
        row = []
        for edge in neighbors:
            row.append(edge[0])
        unweighted.append(row)
    result = kahn(unweighted)
    if len(result["blocked"]) > 0:
        return None
    distance = filled(n, None)
    parent = filled(n, None)
    distance[start] = 0
    for source in result["order"]:
        for edge in adjacency[source]:
            relax(distance, parent, source, edge[0], edge[1])
    return {"distance": distance, "parent": parent}

print(dag_shortest_paths([[[1, 4], [2, 5]], [[2, -2]], [[3, 3]], []], 0))
print(dag_shortest_paths([[], [[2, 1]], [[1, 1]]], 0))
print(dag_shortest_paths([[], []], 1))
```

**预期输出**

```text
{'distance': [0, 4, 2, 5], 'parent': [None, 0, 1, 2]}
None
{'distance': [None, 0], 'parent': [None, None]}
```


</details>

### 练习 3

求从起点出发至多使用 k 条边的最小游走费用，允许负权和负环；k 是非负整数，越界起点或负 k 返回 None。对 0→1=4、1→2=−2、0→2=9 比较 k 为 0、1、2。

<details>
<summary>提示</summary>

第 i 轮只从上一轮 previous 读取源距离，写入独立 current；current 初始复制 previous，保留少走几条边的选择。

</details>

<details>
<summary>解答与检查</summary>

结果分别为 \[0,None,None\]、\[0,4,9\]、\[0,4,2\]。归纳不变式是第 i 轮表示至多 i 条边；若原地读写，第一轮可能沿 0→1→2 连走两条，破坏步数上限。k 有限时负环也只能绕有限次，不需要负环报错。时间 O(n+k(n+a)+1)、空间 O(n+1)，每轮复制数组已计入。这里数的是边数或航段数，不是中转次数；如需恰好 k 条边，应去掉保留旧值的复制规则并重新定义状态。

**完整程序**

```python
def filled(n, value):
    result = []
    for i in range(n):
        result.append(value)
    return result

def at_most_k_edges(adjacency, start, k):
    n = len(adjacency)
    if start < 0 or start >= n or k < 0:
        return None
    previous = filled(n, None)
    previous[start] = 0
    for step in range(k):
        current = previous.copy()
        for source in range(n):
            if previous[source] is not None:
                for edge in adjacency[source]:
                    target = edge[0]
                    candidate = previous[source] + edge[1]
                    if current[target] is None or candidate < current[target]:
                        current[target] = candidate
        previous = current
    return previous

graph = [[[1, 4], [2, 9]], [[2, -2]], []]
for k in range(3):
    print(at_most_k_edges(graph, 0, k))
print(at_most_k_edges([[[1, -2]], [[0, 1]]], 0, 3))
print(at_most_k_edges(graph, 0, -1))
```

**预期输出**

```text
[0, None, None]
[0, 4, 9]
[0, 4, 2]
[-1, -3]
None
```


</details>

<a id="pitfalls"></a>

## 容易混淆的地方

- **沿用 BFS，把第一次发现或边数最少当作总费用最小。** 带权候选允许后续改善；Dijkstra 的确定步骤还要求非负权。
- **用 −1 表示不可达，或遇 None 时当零继续加权。** 负距离合法，None 表示没有已知路线，必须先检查再做算术。
- **堆中同一顶点出现多次就重复扩展，并把堆空间写成 O(n)。** 用当前距离过滤旧记录；懒删除可能保留 O(a) 条候选。
- **混淆全图负环、源可达负环与某目标受影响，或把原地轮次当严格步数。** 明确源与目标可达关系；有限边数动态规划使用前后两份数组。

<a id="self-check"></a>

## 离开这一章前

- [ ] 给出 BFS 与带权最短路不同的三角图，并核对路径费用。
- [ ] 指出 Dijkstra 证明中非负权用于哪一步，核查零权环不会改写等长父边。
- [ ] 用轨迹区分有效弹出与过期记录，按实际候选数量计算空间。
- [ ] 分别测试无负环、可达负环和不可达负环，以及空图与越界起点。
- [ ] 用 k=1 的反例解释同步数组为何必要，并比较 DAG 与一般图的处理次序。

## 本章边界

- 输入保证合法整数编号、整数权和无重复有向端点，允许有向自环；构造器不做任意输入校验。
- Dijkstra 按全图非负契约拒绝负边，Bellman–Ford 发现源可达负环后不交付部分距离或环证据。
- 恢复路径函数只接受成功算法生成的完整数组，不求全部等长路径或负环下的最短简单路径。
- 复杂度采用单位整数算术，不覆盖浮点误差、任意大整数位成本和动态图更新。

## 选题来源与覆盖

来源含学生报告时，仅将其作为选题线索；具体机制仍需结合后续实验或权威资料核对。

- [大一小学期/Week\_3-Python/docs/readme.md](https://github.com/PKUanonym/REKCARC-TSC-UHT/blob/37cd19f7a9fb80dc846a7016b3fd482ed5fe7cc0/%E5%A4%A7%E4%B8%80%E5%B0%8F%E5%AD%A6%E6%9C%9F/Week_3-Python/docs/readme.md)（已提取可读文本，固定版本 37cd19f7a9fb）
- 主题 1：Python 基础语法的外部学习入口；位置：第 41–80 行。
- 主题 2：从基础语法到工具与应用的建议阅读顺序；位置：第 121–160 行。

## 参考资料与规则核对

上游入口用于确定学习方向；下面的参考资料用于核对语言语义、数据结构或算法分析规则，例题和练习由本项目重新设计。

- [Algorithms 4/e：最短路径](https://algs4.cs.princeton.edu/44sp/index.php)：核对松弛、非负权贪心、DAG 次序和负环适用条件。页面由搜索索引读取；本章明确拒绝全部负权的 Dijkstra 接口、懒堆空间及同步限步实现均按原创代码重新分析。
- [Algorithms 4/e：BellmanFordSP](https://algs4.cs.princeton.edu/code/javadoc/edu/princeton/cs/algs4/BellmanFordSP.html)：核对允许正负零权及只报告源可达负环。官方为队列版本；本章为展平边表的完整轮次版本，空间另计 O(n+a)，并非照搬官方实现或复杂度。

**继续学习**：先独立完成自测，再记录仍需回读的步骤。

[上一章：安排有向依赖：拓扑排序与 DAG 应用](22-topological-sort.md) · [下一章：以最低总费用连接全图：最小生成树与并查集](24-minimum-spanning-trees.md)

[教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [哈希表与图练习指引](../hash-graphs-practice.md) · [拓扑排序与带权图练习指引](../weighted-graphs-practice.md) · [记录自己的学习](../learning-log-template.md)
