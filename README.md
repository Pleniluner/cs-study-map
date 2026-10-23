# cs-study-map · 给自己的计算机教材

| 简体中文 | [繁體中文](docs/readme/zh-TW.md) | [English](docs/readme/en.md) | [日本語](docs/readme/ja.md) | [Русский](docs/readme/ru.md) | [Français](docs/readme/fr.md) | [Deutsch](docs/readme/de.md) | [Italiano](docs/readme/it.md) | [Português](docs/readme/pt.md) | [Español](docs/readme/es.md) | [العربية](docs/readme/ar.md) | [한국어](docs/readme/ko.md) |

主要供本人自学：从 [REKCARC-TSC-UHT](https://github.com/PKUanonym/REKCARC-TSC-UHT) 识别可以学习的知识，按照先修关系重新组织成中文教材，补上概念讲解、原创例题、练习解答和自测。自动同步、分类与资料导读为教材选材和更新提供支持。

**[开始读教材](docs/textbook/index.md)** · [前三章试学指南](docs/study-guide.md) · [综合练习](docs/unit-01-review.md) · [编程练习与运行](docs/programming-practice.md) · [查找参考资料](docs/index.md) · [覆盖状态](docs/status.md) · [使用与运行](docs/usage.md) · [来源与许可](ATTRIBUTION.md)

项目仍在建设中。[项目概况与可复现成果](docs/project-brief.md)说明已有工具、验证依据与使用范围；[未完成清单与维护计划](docs/roadmap.md)记录已完成的第 25–30 章、后续课程缺口和软件维护任务，并分别列出现有成果与未来验收标准。

这是 Pleniluner 维护的个人学习项目，与清华大学及上游维护者没有官方隶属关系。公开仓库包含原创工具、教材草稿、来源索引和 AI 导读。原始教材、课件、作业、学生源码和提取全文不会随本仓库发布。

## 按三十章顺序学习

| 顺序 | 学什么 | 动手任务 |
| --- | --- | --- |
| 1 | [二进制、字节与小端序](docs/textbook/01-data-and-bytes.md) | 把一个数拆成字节，再从内存还原 |
| 2 | [寄存器、内存与栈](docs/textbook/02-execution-and-stack.md) | 逐步追踪玩具机器的状态变化 |
| 3 | [首次适应、拆分与合并](docs/textbook/03-first-fit.md) | 手算分配和释放，解释外部碎片 |
| 4 | [顺序、分支与循环](docs/textbook/04-control-flow.md) | 追踪变量、编写判断与重复计算，检查边界和停止条件 |
| 5 | [参数、返回值与函数](docs/textbook/05-functions.md) | 把计算拆成可组合的函数，区分打印、返回和局部名字 |
| 6 | [数组与顺序表](docs/textbook/06-arrays.md) | 追踪下标、共享与复制，手写插入删除的元素搬移 |
| 7 | [单链表与结点引用](docs/textbook/07-linked-lists.md) | 画出链接，完成插入、删除和原地逆序 |
| 8 | [栈与嵌套处理](docs/textbook/08-stacks.md) | 按后进先出实现撤销、受限入栈和括号匹配 |
| 9 | [队列与循环数组](docs/textbook/09-queues.md) | 追踪先进先出、空满与回绕，模拟轮流服务 |
| 10 | [算法分析与增长量级](docs/textbook/10-algorithm-analysis.md) | 先定计数口径，再推导循环次数、最好最坏与额外空间 |
| 11 | [顺序查找与二分查找](docs/textbook/11-searching.md) | 追踪半开区间、左右边界，处理重复值与缺失目标 |
| 12 | [选择、插入与归并排序](docs/textbook/12-sorting.md) | 检查排序过程、元素重数、稳定性与排序后查询 |
| 13 | [递归、返回与调用栈](docs/textbook/13-recursion.md) | 写清基例与缩小量，分别追踪总调用和峰值栈深 |
| 14 | [分治与递归归并](docs/textbook/14-divide-and-conquer.md) | 拆分半开区间、组合子答案，处理快速幂与逆序对 |
| 15 | [快速排序与三路划分](docs/textbook/15-quick-sort.md) | 验证分区、重复值与最坏情况，用短边递归控制栈深 |
| 16 | [树、二叉树与遍历](docs/textbook/16-trees.md) | 追踪高度、三种深度优先与逐层访问，检查镜像和完全性 |
| 17 | [二叉搜索树](docs/textbook/17-binary-search-trees.md) | 维护全局键序与增删链接，核对后继、范围查询和高度退化 |
| 18 | [二叉堆与优先队列](docs/textbook/18-heaps.md) | 实现上浮、下沉、线性建堆和堆排序，处理最大 k 项与多路归并 |
| 19 | [哈希表、冲突与扩容](docs/textbook/19-hash-tables.md) | 维护键值与独立桶，区分分布、最坏扫描和扩容摊还 |
| 20 | [图与存储表示](docs/textbook/20-graphs.md) | 建立有向和无向模型，核对邻接表、矩阵、度数与反向边 |
| 21 | [DFS、BFS 与无权最短路径](docs/textbook/21-graph-traversal.md) | 追踪发现与完成、栈帧和队列，恢复路径并处理连通分量与多源距离 |
| 22 | [拓扑排序与 DAG 应用](docs/textbook/22-topological-sort.md) | 维护剩余入度，恢复有向环，安排任务并计数路径 |
| 23 | [带权最短路与松弛](docs/textbook/23-weighted-shortest-paths.md) | 比较 Dijkstra、Bellman–Ford 和 DAG 次序，处理负权与限步路线 |
| 24 | [最小生成树与并查集](docs/textbook/24-minimum-spanning-trees.md) | 用割性质解释 Prim、Kruskal，核验森林并处理固定分量与新边 |
| 25 | [回溯与搜索剪枝](docs/textbook/25-backtracking.md) | 枚举选择、恢复路径状态，验证剪枝不会遗漏零值与重复项答案 |
| 26 | [贪心算法与交换论证](docs/textbook/26-greedy-algorithms.md) | 构造反例、证明区间选择，核验合并与前缀码的最优代价 |
| 27 | [动态规划入门](docs/textbook/27-dynamic-programming.md) | 定义状态与转移，处理不可达、恢复方案并检查压缩更新顺序 |
| 28 | [背包问题与方案计数](docs/textbook/28-knapsack.md) | 区分容量上限、恰好重量与使用次数，恢复方案并计数组合与序列 |
| 29 | [序列动态规划](docs/textbook/29-sequence-dp.md) | 比较 LCS、编辑距离、LIS 与连续子串，核对位置和对齐 |
| 30 | [区间与树形动态规划](docs/textbook/30-interval-tree-dp.md) | 恢复矩阵链和相邻合并，验证森林并求独立集、覆盖及计数 |

每章有实质讲解、2 个原创例题、3 道练习与折叠解答、自测以及选题来源。先按入门者的需要编排，后续根据本人的学习卡点调整。它还是 AI 教材初稿，尚未经过学科专家或学习者试学验收；现阶段不代表全部课程已经写成教材。

第一次阅读可先看[试学指南](docs/study-guide.md)，分清三章使用的不同存储单位；读完后用 [6 道综合练习](docs/unit-01-review.md)检查掌握情况，每题都有折叠解答与回读指引。已安装项目时，可用 `cs-study-map study` 查看本机进度，记录方法见[运行说明](docs/usage.md#study)。

前三章用纸笔建立模型，第 4、5 章学习控制结构与函数，第 6–9 章学习数组、链表、栈和队列，第 10–12 章继续学习算法分析、查找和排序，第 13–15 章学习递归、分治和快速排序，第 16–18 章学习树、二叉搜索树和堆，第 19–21 章学习哈希表、图和基础图遍历，第 22–24 章学习拓扑排序、带权最短路和最小生成树，第 25–27 章学习回溯与搜索剪枝、贪心算法和动态规划入门，第 28–30 章继续学习背包、序列、区间与树形动态规划。二十七个编程章节合计提供 270 段可独立运行的程序及预期输出，包含例题和练习的参考实现；先预测结果，再运行和改变边界输入。环境准备见[编程练习与运行](docs/programming-practice.md)，结构模型见[数据结构练习指引](docs/data-structures-practice.md)，计数与排序验证见[算法练习指引](docs/algorithms-practice.md)，递归过程见[递归与分治练习指引](docs/recursion-practice.md)，形状、键序和最值维护见[树与堆练习指引](docs/trees-practice.md)，冲突、方向和访问过程见[哈希表与图练习指引](docs/hash-graphs-practice.md)，依赖、路线费用和连接总价见[拓扑排序与带权图练习指引](docs/weighted-graphs-practice.md)，搜索、最优性证明和状态复用见[回溯、贪心与动态规划练习指引](docs/strategy-practice.md)，容量、对齐、切分与子树状态见[动态规划进阶练习指引](docs/advanced-dp-practice.md)。

## 可以做什么

- 按章节学习，在本机记录错题、卡点和下一步；学习记录默认放在被 Git 忽略的 `.local/`。
- 根据已识别知识点生成新的原创教材章节，保留所依据的资料版本；来源变化后提示复核。
- 按领域、课程和 AI 识别的知识点找到资料，并跳转到固定版本的上游原文件。
- 查看“这份资料学什么、建议先了解什么、可以尝试什么”，以及判断所引用的页码或文本位置。
- 定时检查上游更新，识别新增、修改、同内容移动和删除；复用未变化的分析结果。
- 通过人工修正文件覆盖自动分类，保留自己的判断。

AI 导读标明提取覆盖范围、生成模型和未人工核验状态。资料索引齐全与 AI 导读覆盖率分别统计；部分提取、暂不支持的格式和识别失败都会如实展示。

## 首次运行

需要 Python 3.11 或更新版本。

```bash
git clone https://github.com/Pleniluner/cs-study-map.git
cd cs-study-map
python -m venv .venv
# Linux / macOS:
source .venv/bin/activate
# Windows PowerShell 改用：.\.venv\Scripts\Activate.ps1
python -m pip install -e .
cs-study-map run --limit 0
```

这一步只获取文件元数据并生成导航，不需要模型密钥，也不会下载原始资料全文。接入 AI 后，再按需提取少量原资料进行分析，缓存保存在被 Git 忽略的 `.cache/` 中。

## AI 运行方式

支持两种方式，使用同一套结果校验与导读生成流程。

| 方式 | 用途 | 配置 |
| --- | --- | --- |
| 模型 API | GitHub Actions 持续分析，或本地运行 | `CS_STUDY_API_BASE`、`CS_STUDY_MODEL`、`CS_STUDY_API_KEY` |
| 本机 Codex CLI | 使用本机已有登录进行分类 | `CS_STUDY_PROVIDER=codex`、`CS_STUDY_MODEL`，可指定 `CS_STUDY_CODEX_BIN` |

API 适配器支持 Chat Completions 和 Responses 两种协议；默认 `chat`，可用 `CS_STUDY_API_STYLE=responses` 切换。模型名称必须是所用服务实际提供的名称。Codex 方式需要支持所选模型的当前版本 CLI，凭据由 CLI 自行管理。

```bash
cs-study-map analyze --course 程序设计基础 --limit 2 --require-ai
cs-study-map write --limit 1 --require-ai
cs-study-map build
cs-study-map validate
```

详细配置、PowerShell 示例和 GitHub 设置见 [运行说明](docs/usage.md)。

## 自动同步

GitHub Actions 每天检查一次，也可在 Actions 页面手动运行 **Sync study map**。工作流先检查上游变化，再在已配置模型时按预算生成导读和教材，验证通过后提交更新。每天默认最多分析 6 份材料、编写 1 章；教材范围由 `config/curriculum.json` 维护。

未配置模型时，工作流仍同步目录，并明确报告 `not-configured`；已有导读可继续浏览，发生变化的原资料会等待重新分析。它不会把文件名规则或模拟输出标为 AI 已完成。

所有人都可以直接浏览已经生成的学习地图，无需模型账号。Fork 后如需自动生成新导读，需要设置自己的模型接口；本机 Codex 登录不会上传到 GitHub。公开仓库长期无活动时，GitHub 可能停用定时工作流，可在 Actions 页面重新启用。

## 项目结构

```text
config/                  学习路线、来源、分类体系、课程映射、人工修正
catalog/                 文件元数据、分析结果、教材结构化稿与覆盖统计
docs/textbook/           可直接在 GitHub 阅读的教材
docs/                    课程/领域导航、学习记录模板及使用说明
src/cs_study_map/        同步、提取、AI 分类、教材编写与验证程序
tests/                   同步、失败恢复、来源约束和发布检查
.github/workflows/       自动同步与 CI
.cache/                  本机原文件和提取缓存，禁止提交
.local/                  本人的学习记录和未公开分析，禁止提交
```

初始分类映射来自个人已有的课程目录整理，属于可修正的起点。新课程会进入“待分类”。当前支持文本、常见源码、可提取文本的 PDF、DOCX、PPTX 和 Notebook；扫描件 OCR、旧 DOC/PPT、压缩包内分析尚未实现。PDF 默认最多提取前 8 页及总计 10,000 字符，不能据此声称已经读完一份长讲义。

## 验证与贡献

```bash
python -m unittest discover -s tests -v
cs-study-map validate --tracked
```

请通过 Issue 报告分类或导读错误，通过 PR 修改程序、分类映射或人工修正规则。请阅读 [贡献说明](CONTRIBUTING.md)。

本项目原创程序、教材文本与维护文档采用 MIT 许可；来源材料及其权利不因此改变，详见 [来源说明](ATTRIBUTION.md)。

早期成果：[总知识图与 60 份课程指南归档](docs/early-work/index.md)，保留项目建立当前 Git 仓库前的 README 与教材说明。
