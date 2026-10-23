# 以最低总费用连接全图：最小生成树与并查集

[返回教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [哈希表与图练习指引](../hash-graphs-practice.md) · [拓扑排序与带权图练习指引](../weighted-graphs-practice.md)

[上一章：比较路线总费用：带权最短路与松弛](23-weighted-shortest-paths.md) · [下一章：枚举选择并排除无解分支：回溯与搜索剪枝](25-backtracking.md)

[学习目标](#objectives) · [需要的基础](#prerequisites) · [例题](#examples) · [练习](#practice) · [自测](#self-check)

状态：**AI 初稿，可开始试学**。生成模型：Codex 当前会话（未记录具体模型型号）。

本章围绕资料中识别到的知识点重新编写；讲解、数值模型、例题与练习为 AI 原创组织，不是原课程题目或答案。主题出处只说明选题关联，不证明全部推导已经正确。

把若干地点全部连接起来，目标可能是让铺设线路的总费用最低，而不是让某个起点到每个地点的路程最短。本章从这个目标差异出发，解释生成树、最小生成树和不连通图的最小生成森林。随后用割性质支持 Prim 的逐点扩展，用并查集支持 Kruskal 的逐边选择。负权、等权、孤立点和空图都会出现在例子中；练习进一步讨论固定分量数量与新增一条边后如何改善已有最优树。

<a id="objectives"></a>

## 学完要能做到

- 区分最短路树与最小生成树，并写清空图、不连通图和等权的约定。
- 用割性质及交换论证说明 Prim、Kruskal 的安全选边。
- 实现按大小合并与路径压缩的并查集，判断加边是否成环。
- 对最小生成森林、固定 k 个分量和新边改进进行边数、权重与结构核验。

<a id="prerequisites"></a>

## 需要的基础

- 掌握第 16–18 章树、堆，以及无向图的连通分量和邻接表。
- 理解第 23 章带权表示，并能区分单条边权与从源点累计的距离。
- 能用不变式和交换论证说明局部选择为何保持全局最优的可能性。

## 生成树优化的是所有选中边的总费用

对非空连通无向图，生成树覆盖全部顶点、连通且无环，恰有 n−1 条边；最小生成树 MST 在所有这样的树中使边权和最小。只检查 n−1 条边不够，还需要连通或无环的结构条件，否则可能一部分成环、另一部分断开。不连通图不存在覆盖全部顶点的一棵生成树，可以在每个连通分量内各求一棵，合起来叫最小生成森林。

本章输入是合法无向简单图，允许负权、零权和等权，不允许自环或重复边。边列表每条边只出现一次，统一按起点编号较小的方向记为 \[u,v,w\]；邻接表则在两端各存一个 \[邻居,权重\]，对称且同权。调用者保证这些条件，算法不重复校验。设无向边数 e、邻接项数 a，则 a=2e。空图返回零分量、零边、总权零的森林；单点图是一棵零边树。

三角图的边为 0—1 权 2、0—2 权 3、1—2 权 2。从 0 出发的最短路树选择前两条，总权 5；最小生成树选择 0—1 与 1—2，总权 4，但树中从 0 到 2 的费用变成 4，大于原图最短距离 3。二者目标不同，不能互相代替。下面 total\_weight 只求候选边列表的和，不验证它是不是树；对于 q 条候选边需 O(q+1) 时间和 O(1) 额外空间。结构检验会在后续算法和自动验收中另做。

**完整程序**

```python
def total_weight(edges):
    total = 0
    for edge in edges:
        total = total + edge[2]
    return total

shortest_path_tree = [[0, 1, 2], [0, 2, 3]]
minimum_spanning_tree = [[0, 1, 2], [1, 2, 2]]
print(total_weight(shortest_path_tree))
print(total_weight(minimum_spanning_tree))
print(total_weight([]))
```

**预期输出**

```text
5
4
0
```


选题关联：来源主题 1（文末列出）。

## Prim 与割性质：每次接入一条最便宜的跨界边

把顶点分成 S 和其余两部分，连接两边的边叫跨割边。若当前已选边都不跨这个割，任取权重最小的跨割边 x，都可以安全加入某个包含当前已选边的最优森林。交换证明如下：若已有最优解未含 x，加入 x 会形成环，环上另有跨割边 y。y 不属于当前已选边，且权重不小于 x；删 y 留 x 保持生成结构且费用不增。等权时结论是存在这样的最优解，不是每个最优解都必须包含 x。

Prim 令 S 为当前分量已经接入的顶点，key\[v\] 记录从 S 到外部顶点 v 的最小单条边权，parent\[v\] 记录该边另一端。每轮选择最小 key 的未用顶点，它对应一条最轻跨割边。接入后扫描出边，尝试用边自身权重改善邻居 key；不能使用 key\[u\]+w，那是最短路的累计语义。根没有选入边，所以不把根的初始零值加入总权。

扫描版若找不到已知 key 的候选，就从最小未用顶点启动新分量，并增加 components。对称输入保证此时上一分量已完成；所有点最终都会处理，孤立点也计一个分量。负边不会破坏“选最轻跨割边”的论证，零和负 key 都用 None 区分未连接。n 轮各扫描 n 个候选，所有邻接项扫描一次，时间 O(n²+a+1)，状态和输出 O(n+1)。同权时按编号选点、严格改进父边，结果确定但不承诺唯一最优树。

**完整程序**

```python
def filled(n, value):
    result = []
    for i in range(n):
        result.append(value)
    return result

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

def prim_forest(adjacency):
    n = len(adjacency)
    used = filled(n, False)
    key = filled(n, None)
    parent = filled(n, None)
    selected = []
    total = 0
    components = 0
    for step in range(n):
        best = None
        for vertex in range(n):
            if not used[vertex] and key[vertex] is not None:
                if best is None or key[vertex] < key[best]:
                    best = vertex
        if best is None:
            for vertex in range(n):
                if not used[vertex] and best is None:
                    best = vertex
            components = components + 1
            key[best] = 0
        used[best] = True
        if parent[best] is not None:
            selected.append([parent[best], best, key[best]])
            total = total + key[best]
        for edge in adjacency[best]:
            target = edge[0]
            if not used[target]:
                if key[target] is None or edge[1] < key[target]:
                    key[target] = edge[1]
                    parent[target] = best
    return {"edges": selected, "weight": total, "components": components}

graph = weighted_adjacency(4, [[0, 1, 2], [0, 2, 3], [1, 2, 2]], False)
print(prim_forest(graph))
print(prim_forest([]))
```

**预期输出**

```text
{'edges': [[0, 1, 2], [1, 2, 2]], 'weight': 4, 'components': 2}
{'edges': [], 'weight': 0, 'components': 0}
```


选题关联：来源主题 1（文末列出）。

## 并查集：用集合代表判断一条边是否成环

在一个森林中，如果新边两端已经通过已选边相连，加入它会形成环；若尚未相连，则能把两个分量合并。并查集维护每个顶点所在集合的代表，无需每次重新搜索整片森林。初始化时每点单独为根，parent\[v\]=v、size\[v\]=1、分量数为 n。find\_root 先沿父指针找到根，再把原来路径上的节点直接接到根，这叫路径压缩。

join 先找两端根；相同则返回 False，表示不能增加这条森林边。不同则把较小集合的根接到较大集合的根，更新新根的 size，分量数减一，返回 True。size 只有在根位置才代表当前集合大小，非根位置的旧数值不能拿来再次做集合大小判断。压缩第二遍要先保存原父亲再改指针，否则会丢失后续路径。

为什么按大小合并能控制高度？只有小树被接到大树时，其节点深度才可能增加一，同时所在集合大小至少翻倍。一个节点的深度增加至多 log₂n 次；路径压缩只会缩短路径。因此以 O(log(n+1)) 作为单次查找或合并的安全上界已经足够支持本章分析，初始化 O(n+1)、空间 O(n+1)。更细的反阿克曼均摊界留待后续，不把单次操作简单写成常数。并查集的父指针是辅助结构，不一定对应原图中的真实边，不能用它恢复图路径。

**完整程序**

```python
def new_dsu(n):
    parent = []
    size = []
    for vertex in range(n):
        parent.append(vertex)
        size.append(1)
    return {"parent": parent, "size": size, "components": n}

def find_root(dsu, vertex):
    root = vertex
    while dsu["parent"][root] != root:
        root = dsu["parent"][root]
    while vertex != root:
        following = dsu["parent"][vertex]
        dsu["parent"][vertex] = root
        vertex = following
    return root

def join(dsu, left, right):
    a = find_root(dsu, left)
    b = find_root(dsu, right)
    if a == b:
        return False
    if dsu["size"][a] < dsu["size"][b]:
        saved = a
        a = b
        b = saved
    dsu["parent"][b] = a
    dsu["size"][a] = dsu["size"][a] + dsu["size"][b]
    dsu["components"] = dsu["components"] - 1
    return True

dsu = new_dsu(5)
print(join(dsu, 0, 1))
print(join(dsu, 2, 3))
print(join(dsu, 1, 3))
print(join(dsu, 0, 2))
print(find_root(dsu, 3))
print(dsu["components"])
print(dsu["parent"])
```

**预期输出**

```text
True
True
True
False
0
2
[0, 0, 0, 0, 4]
```


选题关联：来源主题 1（文末列出）。

## Kruskal：按权重从小到大接受不会成环的边

Kruskal 不固定一个出发点，而是在全图按权重递增考虑边。用最小堆保存 \[权重,u,v\]，依次弹出；若 join 能合并两个集合，就把原格式 \[u,v,权重\] 记入结果并加到总权，否则跳过。每一次接受都把分量数减一，已选部分始终是森林。堆先比较权重，再比较两个端点，因此规范输入下同权处理次序可重复。

安全性仍来自割性质。考虑一条将要接受的边，取它某一端当前所在的整个集合为 S。比它更轻的跨割边不可能尚未被考虑；如果曾被接受，两端早已属于同一集合；如果曾被拒绝，其两端当时已相连，以后也不会重新分离。因此当前边是这个割的一条最轻边，加入后仍能扩展为最优生成森林。被拒绝的边则一定会让当前森林成环，不能加入。

本实现把所有输入边逐次入堆，最后取完，因而也能处理不连通图，不把“没有凑够 n−1 条边”误当算法崩溃。若最终有 c 个原图分量，森林恰含 n−c 条边；孤立点保留在分量计数里。堆操作 O(e log(e+1))，并查集采用上一节的单次对数上界，总时间 O(n+e log(e+1)+e log(n+1)+1)，空间 O(n+e+1)。这里没有声称使用线性建堆，也未套用更精细的并查集均摊界。输入边列表及其内层记录都不修改。

**完整程序**

```python
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

def new_dsu(n):
    parent = []
    size = []
    for vertex in range(n):
        parent.append(vertex)
        size.append(1)
    return {"parent": parent, "size": size, "components": n}

def find_root(dsu, vertex):
    root = vertex
    while dsu["parent"][root] != root:
        root = dsu["parent"][root]
    while vertex != root:
        following = dsu["parent"][vertex]
        dsu["parent"][vertex] = root
        vertex = following
    return root

def join(dsu, left, right):
    a = find_root(dsu, left)
    b = find_root(dsu, right)
    if a == b:
        return False
    if dsu["size"][a] < dsu["size"][b]:
        saved = a
        a = b
        b = saved
    dsu["parent"][b] = a
    dsu["size"][a] = dsu["size"][a] + dsu["size"][b]
    dsu["components"] = dsu["components"] - 1
    return True

def kruskal_forest(n, edges):
    heap = []
    for edge in edges:
        heap_push(heap, [edge[2], edge[0], edge[1]])
    dsu = new_dsu(n)
    selected = []
    total = 0
    while len(heap) > 0:
        entry = heap_pop(heap)
        if join(dsu, entry[1], entry[2]):
            selected.append([entry[1], entry[2], entry[0]])
            total = total + entry[0]
    return {"edges": selected, "weight": total, "components": dsu["components"]}

edges = [[0, 1, 2], [0, 2, 3], [1, 2, 2]]
print(kruskal_forest(4, edges))
print(edges)
print(kruskal_forest(0, []))
```

**预期输出**

```text
{'edges': [[0, 1, 2], [1, 2, 2]], 'weight': 4, 'components': 2}
[[0, 1, 2], [0, 2, 3], [1, 2, 2]]
{'edges': [], 'weight': 0, 'components': 0}
```


选题关联：来源主题 1（文末列出）。

## 负权、等权与断开的部分：核验森林而非硬凑一棵树

考虑六个顶点，边为 0—1 权 −2、1—2 权 0、0—2 权 0、3—4 权 5，5 孤立。Kruskal 接受 −2 的边，再从两条零权边中选一条连接 2；另一条会成环而被跳过。最后加入 3—4，得到三个分量、三条边、总权 3。用 1—2 代替 0—2 仍是同样费用的最优森林，不能因边集合不同就判另一个正确算法失败。

等权可能导致多个最优解，但不必然如此：一张本来就是树的图，即使各边同权，也只有这一棵生成树。所有权重互异是唯一性的充分条件，却不是必要条件。检测唯一性需要更多论证，本章只保证输出一个最优解。负权也不要求先加一个偏移量变正；选边和交换论证比较的是相对权重，Prim 与 Kruskal 都直接适用。

最短游走里负环可被反复绕行，使费用无限下降；生成森林要求无环，每条边至多取一次，所以不存在这种无限重复。验收应逐项确认选边来自原图、没有环、覆盖原图每个分量，边数为 n−c，并独立核对总权。只比较总权可能漏掉非法选边，只比较边数可能漏掉错误分组。本节沿用 Kruskal 的时间与空间界；为输出而另算一次求和需 O(n+1)，没有枚举所有生成树。

**完整程序**

```python
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

def new_dsu(n):
    parent = []
    size = []
    for vertex in range(n):
        parent.append(vertex)
        size.append(1)
    return {"parent": parent, "size": size, "components": n}

def find_root(dsu, vertex):
    root = vertex
    while dsu["parent"][root] != root:
        root = dsu["parent"][root]
    while vertex != root:
        following = dsu["parent"][vertex]
        dsu["parent"][vertex] = root
        vertex = following
    return root

def join(dsu, left, right):
    a = find_root(dsu, left)
    b = find_root(dsu, right)
    if a == b:
        return False
    if dsu["size"][a] < dsu["size"][b]:
        saved = a
        a = b
        b = saved
    dsu["parent"][b] = a
    dsu["size"][a] = dsu["size"][a] + dsu["size"][b]
    dsu["components"] = dsu["components"] - 1
    return True

def kruskal_forest(n, edges):
    heap = []
    for edge in edges:
        heap_push(heap, [edge[2], edge[0], edge[1]])
    dsu = new_dsu(n)
    selected = []
    total = 0
    while len(heap) > 0:
        entry = heap_pop(heap)
        if join(dsu, entry[1], entry[2]):
            selected.append([entry[1], entry[2], entry[0]])
            total = total + entry[0]
    return {"edges": selected, "weight": total, "components": dsu["components"]}

def total_weight(edges):
    total = 0
    for edge in edges:
        total = total + edge[2]
    return total

edges = [[0, 1, -2], [1, 2, 0], [0, 2, 0], [3, 4, 5]]
result = kruskal_forest(6, edges)
print(result)
print(len(result["edges"]) == 6 - result["components"])
print(total_weight([[0, 1, -2], [1, 2, 0], [3, 4, 5]]))
```

**预期输出**

```text
{'edges': [[0, 1, -2], [0, 2, 0], [3, 4, 5]], 'weight': 3, 'components': 3}
True
3
```


选题关联：来源主题 1（文末列出）。

<a id="examples"></a>

## 跟着做：原创例题

### 例题 1

对五个顶点和边 \[\[0,1,4\],\[0,2,2\],\[1,2,1\],\[1,3,3\],\[2,3,5\],\[2,4,7\],\[3,4,2\]\]，分别执行 Prim 与 Kruskal，说明选择顺序不同为何仍得到相同最优总权。

1. Prim 从 0 开始，先用权 2 的 0—2 接入 2。
2. 接下来以权 1 的 2—1 接入 1，再以权 3 的 1—3 接入 3，最后以权 2 的 3—4 接入 4。
3. Kruskal 按权考虑 1—2、0—2、3—4，再用 1—3 把两个现有部分连接。
4. 两者各选四条边且连通无环，总权都是 8；Prim 的选边权重不必递增。

**结果与核对**

Prim 每次选当前割上的最轻边，随着新点加入，下一条可用边可能更轻。Kruskal 则按全图权重顺序处理，两者的安全依据都来自割性质。程序保留各自选择顺序，Prim 的边端点方向也可能与规范输入相反，但仍代表同一无向边。比较结果时应忽略无向边方向，并核对总权及结构；不能要求输出列表逐项相同。示例建图 O(n+e+1)，两算法各按本章已分析的成本运行。

**完整程序**

```python
def filled(n, value):
    result = []
    for i in range(n):
        result.append(value)
    return result

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

def prim_forest(adjacency):
    n = len(adjacency)
    used = filled(n, False)
    key = filled(n, None)
    parent = filled(n, None)
    selected = []
    total = 0
    components = 0
    for step in range(n):
        best = None
        for vertex in range(n):
            if not used[vertex] and key[vertex] is not None:
                if best is None or key[vertex] < key[best]:
                    best = vertex
        if best is None:
            for vertex in range(n):
                if not used[vertex] and best is None:
                    best = vertex
            components = components + 1
            key[best] = 0
        used[best] = True
        if parent[best] is not None:
            selected.append([parent[best], best, key[best]])
            total = total + key[best]
        for edge in adjacency[best]:
            target = edge[0]
            if not used[target]:
                if key[target] is None or edge[1] < key[target]:
                    key[target] = edge[1]
                    parent[target] = best
    return {"edges": selected, "weight": total, "components": components}

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

def new_dsu(n):
    parent = []
    size = []
    for vertex in range(n):
        parent.append(vertex)
        size.append(1)
    return {"parent": parent, "size": size, "components": n}

def find_root(dsu, vertex):
    root = vertex
    while dsu["parent"][root] != root:
        root = dsu["parent"][root]
    while vertex != root:
        following = dsu["parent"][vertex]
        dsu["parent"][vertex] = root
        vertex = following
    return root

def join(dsu, left, right):
    a = find_root(dsu, left)
    b = find_root(dsu, right)
    if a == b:
        return False
    if dsu["size"][a] < dsu["size"][b]:
        saved = a
        a = b
        b = saved
    dsu["parent"][b] = a
    dsu["size"][a] = dsu["size"][a] + dsu["size"][b]
    dsu["components"] = dsu["components"] - 1
    return True

def kruskal_forest(n, edges):
    heap = []
    for edge in edges:
        heap_push(heap, [edge[2], edge[0], edge[1]])
    dsu = new_dsu(n)
    selected = []
    total = 0
    while len(heap) > 0:
        entry = heap_pop(heap)
        if join(dsu, entry[1], entry[2]):
            selected.append([entry[1], entry[2], entry[0]])
            total = total + entry[0]
    return {"edges": selected, "weight": total, "components": dsu["components"]}

edges = [[0, 1, 4], [0, 2, 2], [1, 2, 1], [1, 3, 3], [2, 3, 5], [2, 4, 7], [3, 4, 2]]
print(prim_forest(weighted_adjacency(5, edges, False)))
print(kruskal_forest(5, edges))
```

**预期输出**

```text
{'edges': [[0, 2, 2], [2, 1, 1], [1, 3, 3], [3, 4, 2]], 'weight': 8, 'components': 1}
{'edges': [[1, 2, 1], [0, 2, 2], [3, 4, 2], [1, 3, 3]], 'weight': 8, 'components': 1}
```


### 例题 2

Kruskal 依次考虑 0—1 权 1、1—2 权 2、0—2 权 3、2—3 权 10、1—3 权 11。逐步记录接受或跳过及剩余分量数，解释为什么不能简单取最小的三条边。

1. 接受 0—1，分量数从 4 降为 3。
2. 接受 1—2，分量数降为 2；此时 0、1、2 已在同一集合。
3. 0—2 虽便宜，却形成三角环，所以跳过，分量数不变。
4. 接受 2—3 后变为一个分量，总权 13；最后的 1—3 也被跳过。

**结果与核对**

最小三条边总权虽为 6，却把 3 留在外面且在另一部分成环，不是生成树。合法最优选择必须支付跨到 3 的连接费用。轨迹的每条事件保存动作、当前边和分量数，不复制整个并查集；额外 O(e+1) 事件空间仍包含在 Kruskal 的 O(n+e+1) 界内。

**完整程序**

```python
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

def new_dsu(n):
    parent = []
    size = []
    for vertex in range(n):
        parent.append(vertex)
        size.append(1)
    return {"parent": parent, "size": size, "components": n}

def find_root(dsu, vertex):
    root = vertex
    while dsu["parent"][root] != root:
        root = dsu["parent"][root]
    while vertex != root:
        following = dsu["parent"][vertex]
        dsu["parent"][vertex] = root
        vertex = following
    return root

def join(dsu, left, right):
    a = find_root(dsu, left)
    b = find_root(dsu, right)
    if a == b:
        return False
    if dsu["size"][a] < dsu["size"][b]:
        saved = a
        a = b
        b = saved
    dsu["parent"][b] = a
    dsu["size"][a] = dsu["size"][a] + dsu["size"][b]
    dsu["components"] = dsu["components"] - 1
    return True

def kruskal_trace(n, edges):
    heap = []
    for edge in edges:
        heap_push(heap, [edge[2], edge[0], edge[1]])
    dsu = new_dsu(n)
    selected = []
    total = 0
    events = []
    while len(heap) > 0:
        entry = heap_pop(heap)
        edge = [entry[1], entry[2], entry[0]]
        if join(dsu, entry[1], entry[2]):
            selected.append(edge)
            total = total + entry[0]
            events.append(["take", edge, dsu["components"]])
        else:
            events.append(["skip", edge, dsu["components"]])
    return {"edges": selected, "weight": total, "events": events}

result = kruskal_trace(4, [[0, 1, 1], [1, 2, 2], [0, 2, 3], [2, 3, 10], [1, 3, 11]])
for event in result["events"]:
    print(event)
print(result["weight"])
```

**预期输出**

```text
['take', [0, 1, 1], 3]
['take', [1, 2, 2], 2]
['skip', [0, 2, 3], 2]
['take', [2, 3, 10], 1]
['skip', [1, 3, 11], 1]
13
```


<a id="practice"></a>

## 自己做：先完成再看解答

### 练习 1

写只接受完整生成树的 minimum\_tree 包装函数。输入仍为合法无向图，空图或不连通返回 None，单点图返回总权零的树；分别检查空图、单点、两点无边和两点负权边。

<details>
<summary>提示</summary>

先求最小生成森林，再用 n 和 components 判断是否符合本题非空且连通的要求，不要只看选边数量。

</details>

<details>
<summary>解答与检查</summary>

空图在森林接口里成功，但本题明确不把它叫一棵树，因此返回 None；单点图有一个分量且零边，应成功。两点无边有两个分量，无法凭空补边；两点间权 −3 的唯一边直接成为最优树。包装仅增加 O(1) 检查，总成本与 Kruskal 相同。失败与总权恰为零的成功结果必须区分。

**完整程序**

```python
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

def new_dsu(n):
    parent = []
    size = []
    for vertex in range(n):
        parent.append(vertex)
        size.append(1)
    return {"parent": parent, "size": size, "components": n}

def find_root(dsu, vertex):
    root = vertex
    while dsu["parent"][root] != root:
        root = dsu["parent"][root]
    while vertex != root:
        following = dsu["parent"][vertex]
        dsu["parent"][vertex] = root
        vertex = following
    return root

def join(dsu, left, right):
    a = find_root(dsu, left)
    b = find_root(dsu, right)
    if a == b:
        return False
    if dsu["size"][a] < dsu["size"][b]:
        saved = a
        a = b
        b = saved
    dsu["parent"][b] = a
    dsu["size"][a] = dsu["size"][a] + dsu["size"][b]
    dsu["components"] = dsu["components"] - 1
    return True

def kruskal_forest(n, edges):
    heap = []
    for edge in edges:
        heap_push(heap, [edge[2], edge[0], edge[1]])
    dsu = new_dsu(n)
    selected = []
    total = 0
    while len(heap) > 0:
        entry = heap_pop(heap)
        if join(dsu, entry[1], entry[2]):
            selected.append([entry[1], entry[2], entry[0]])
            total = total + entry[0]
    return {"edges": selected, "weight": total, "components": dsu["components"]}

def minimum_tree(n, edges):
    result = kruskal_forest(n, edges)
    if n == 0 or result["components"] != 1:
        return None
    return result

print(minimum_tree(0, []))
print(minimum_tree(1, []))
print(minimum_tree(2, []))
print(minimum_tree(2, [[0, 1, -3]]))
```

**预期输出**

```text
None
{'edges': [], 'weight': 0, 'components': 1}
None
{'edges': [[0, 1, -3]], 'weight': -3, 'components': 1}
```


</details>

### 练习 2

求覆盖全部 n 个顶点、恰好 k 个分量的最小权森林。n 非空时要求 1≤k≤n，空图只接受 k=0；无法达到目标或 k 越界返回 None。检查四点图的 k=2、4 和一个无法连通的输入。

<details>
<summary>提示</summary>

Kruskal 每接受一条边，分量数减一；到达 k 时停止。即使还有负边，也不能越过题目要求的固定边数。

</details>

<details>
<summary>解答与检查</summary>

任何候选恰有 n−k 条边。按权接受的每条安全边，可在一个同样边数的最优森林中交换进去：若新增边形成环，删去环上跨当前分量的边；若不形成环，就删去最优森林中尚未固定的一条边。它们都不比当前边轻，否则早已被考虑且不会仍跨当前分量。因此逐步保留某个最优解，达到 k 即最优。k=n 必须返回空边集，即使有负边也不能多选。时间与空间采用完整 Kruskal 的安全上界；本实现仍先把全部边入堆。

**完整程序**

```python
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

def new_dsu(n):
    parent = []
    size = []
    for vertex in range(n):
        parent.append(vertex)
        size.append(1)
    return {"parent": parent, "size": size, "components": n}

def find_root(dsu, vertex):
    root = vertex
    while dsu["parent"][root] != root:
        root = dsu["parent"][root]
    while vertex != root:
        following = dsu["parent"][vertex]
        dsu["parent"][vertex] = root
        vertex = following
    return root

def join(dsu, left, right):
    a = find_root(dsu, left)
    b = find_root(dsu, right)
    if a == b:
        return False
    if dsu["size"][a] < dsu["size"][b]:
        saved = a
        a = b
        b = saved
    dsu["parent"][b] = a
    dsu["size"][a] = dsu["size"][a] + dsu["size"][b]
    dsu["components"] = dsu["components"] - 1
    return True

def minimum_k_forest(n, edges, k):
    if k < 0 or k > n or (n > 0 and k == 0):
        return None
    heap = []
    for edge in edges:
        heap_push(heap, [edge[2], edge[0], edge[1]])
    dsu = new_dsu(n)
    selected = []
    total = 0
    while len(heap) > 0 and dsu["components"] > k:
        entry = heap_pop(heap)
        if join(dsu, entry[1], entry[2]):
            selected.append([entry[1], entry[2], entry[0]])
            total = total + entry[0]
    if dsu["components"] != k:
        return None
    return {"edges": selected, "weight": total, "components": k}

edges = [[0, 1, -2], [1, 2, 1], [2, 3, 4], [0, 3, 8]]
print(minimum_k_forest(4, edges, 2))
print(minimum_k_forest(4, edges, 4))
print(minimum_k_forest(3, [[0, 1, 1]], 1))
print(minimum_k_forest(0, [], 0))
```

**预期输出**

```text
{'edges': [[0, 1, -2], [1, 2, 1]], 'weight': -1, 'components': 2}
{'edges': [], 'weight': 0, 'components': 4}
None
{'edges': [], 'weight': 0, 'components': 0}
```


</details>

### 练习 3

已知 tree 是原连通图的一棵最小生成树，加入一条原图不存在的新边，求新的最小生成树总权。输入 n≥2，新边端点不同且合法。用树 \[\[0,1,−5\],\[1,2,−2\],\[2,3,4\]\] 分别加入 0—3 权 1 和 0—2 权 −3。

<details>
<summary>提示</summary>

树上两端之间只有一条路径。新边形成唯一环，比较新边权与旧路径的最大边权；全为负数时不能把最大值初始化为 0。

</details>

<details>
<summary>解答与检查</summary>

原总权为 −3。加入 0—3 权 1 后替换权 4 的边，得到 −6；加入 0—2 权 −3 后替换权 −2 的边，得到 −4。若新边不更轻就保留原树。对任何包含新边的最优树，删新边得到一个割；旧树两端路径必有跨割边，其权不大于路径最大值，补入后不能优于旧 MST，因此新最优值不低于本次替换结果。下面只返回总权，不重建树；调用者保证旧树确为 MST。树路径搜索、建表和求和共 O(n+1) 时间与空间；无路径、越界或零边路径时辅助函数返回 None。

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

def total_weight(edges):
    total = 0
    for edge in edges:
        total = total + edge[2]
    return total

def forest_path_max(adjacency, start, target):
    n = len(adjacency)
    if start < 0 or start >= n or target < 0 or target >= n:
        return None
    stack = [[start, None, None]]
    while len(stack) > 0:
        entry = stack.pop()
        source = entry[0]
        if source == target:
            return entry[2]
        for edge in adjacency[source]:
            if edge[0] != entry[1]:
                maximum = entry[2]
                if maximum is None or edge[1] > maximum:
                    maximum = edge[1]
                stack.append([edge[0], source, maximum])
    return None

def improved_tree_weight(n, tree, new_edge):
    adjacency = weighted_adjacency(n, tree, False)
    maximum = forest_path_max(adjacency, new_edge[0], new_edge[1])
    total = total_weight(tree)
    if new_edge[2] < maximum:
        return total + new_edge[2] - maximum
    return total

tree = [[0, 1, -5], [1, 2, -2], [2, 3, 4]]
graph = weighted_adjacency(4, tree, False)
print(forest_path_max(graph, 0, 2))
print(improved_tree_weight(4, tree, [0, 3, 1]))
print(improved_tree_weight(4, tree, [0, 2, -3]))
print(improved_tree_weight(4, tree, [0, 3, 9]))
```

**预期输出**

```text
-2
-6
-4
-3
```


</details>

<a id="pitfalls"></a>

## 容易混淆的地方

- **用最短路树代替 MST，或在 Prim 中把 key 写成路径累计费用。** MST 优化全部选边总权，Prim 的 key 是接入集合的最小单条边权。
- **选最便宜的 n−1 条边就停止，不检查环或连通。** 用并查集保证接受边合并不同分量，并核对结果覆盖原图分量。
- **认为负边使 MST 失效，或认为出现等权就一定有多个最优解。** 负权可直接比较；等权可能产生选择，但唯一性取决于全图结构。
- **把并查集父指针当图路径，或把全负路径的最大边初始化为零。** 并查集只保存集合关系；真实树路径沿邻接表搜索，最大值使用 None 起始。

<a id="self-check"></a>

## 离开这一章前

- [ ] 手画三角图，分别计算最短路树和最小生成树的目标值。
- [ ] 用加一边形成环、删一边恢复树解释割性质，注明等权时的存在性结论。
- [ ] 检查并查集重复合并不改分量数，压缩不改所属集合。
- [ ] 对空图、孤立点、负权与同权，验证选边合法、无环、分量及 n−c 条边。
- [ ] 分别证明固定 k 的停止条件和新边替换规则，给出全负路径的测试。

## 本章边界

- 只处理合法整数权无向简单图；边列表使用每条边一次且 u 编号小于 v 的规范形式，邻接表保证对称。
- 输出一个最优森林，不枚举全部最优解、不判定唯一性，也不处理有向最小树形图。
- 并查集分析使用按大小合并的对数安全上界，未展开反阿克曼均摊证明。
- 新边改进要求旧输入已经是 MST，仅返回新总权；复杂度按单位整数操作计，不包含大整数位成本。

## 选题来源与覆盖

来源含学生报告时，仅将其作为选题线索；具体机制仍需结合后续实验或权威资料核对。

- [大一小学期/Week\_3-Python/docs/readme.md](https://github.com/PKUanonym/REKCARC-TSC-UHT/blob/37cd19f7a9fb80dc846a7016b3fd482ed5fe7cc0/%E5%A4%A7%E4%B8%80%E5%B0%8F%E5%AD%A6%E6%9C%9F/Week_3-Python/docs/readme.md)（已提取可读文本，固定版本 37cd19f7a9fb）
- 主题 1：Python 基础语法的外部学习入口；位置：第 41–80 行。
- 主题 2：从基础语法到工具与应用的建议阅读顺序；位置：第 121–160 行。

## 参考资料与规则核对

上游入口用于确定学习方向；下面的参考资料用于核对语言语义、数据结构或算法分析规则，例题和练习由本项目重新设计。

- [Algorithms 4/e：最小生成树](https://algs4.cs.princeton.edu/43mst/index.php)：通过搜索索引核对树、割性质、等权与负权；本章明确等权最轻边属于某个最优解，图例、轨迹及扩展练习为原创，不复制教材例题。
- [Algorithms 4/e：按大小合并](https://algs4.cs.princeton.edu/code/javadoc/edu/princeton/cs/algs4/WeightedQuickUnionUF.html)：核对集合接口和按大小合并的对数高度。本章另加完整路径压缩，但只使用不变差的单次对数安全上界，不声称官方无压缩实现包含压缩。
- [Algorithms 4/e：带路径减半的按大小合并](https://algs4.cs.princeton.edu/15uf/WeightedQuickUnionPathHalvingUF.java.html)：核对路径压缩只改变辅助父指针，不改变集合关系。本章采用先找根再完整压缩的两遍实现，并非页面的路径减半版本。

**继续学习**：先独立完成自测，再记录仍需回读的步骤。

[上一章：比较路线总费用：带权最短路与松弛](23-weighted-shortest-paths.md) · [下一章：枚举选择并排除无解分支：回溯与搜索剪枝](25-backtracking.md)

[教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [算法练习指引](../algorithms-practice.md) · [递归与分治练习指引](../recursion-practice.md) · [树与堆练习指引](../trees-practice.md) · [哈希表与图练习指引](../hash-graphs-practice.md) · [拓扑排序与带权图练习指引](../weighted-graphs-practice.md) · [记录自己的学习](../learning-log-template.md)
