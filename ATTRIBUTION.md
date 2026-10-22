# 来源、署名与许可边界

本项目的主要资料来源是 [PKUanonym/REKCARC-TSC-UHT](https://github.com/PKUanonym/REKCARC-TSC-UHT)。感谢上游维护者和贡献者整理、维护课程资料。上游 README 记录了项目继承关系及贡献者，具体作品的作者和版权声明以原文件为准。

本仓库公开来源路径、内容标识、指向固定提交的链接、分类元数据、简短 AI 导读，以及基于主题重新编写的个人学习教材。自动写作命令向模型提供主题摘要，要求重新组织讲解和设计例题，不传入原题全文；交互编写时另查阅公开的权威规则与语言文档，具体参考列在章末。原始课件、教材、题目全文、学生源码、报告、模型输入全文及下载缓存不进入发布内容。目录元数据中的原始路径用于准确追溯来源。

初始 65 个课程目录的领域映射来自维护者先前的个人整理。它不代表上游官方分类或学校的教学安排。AI 生成的先修建议与练习建议不冒充原课程要求；每条导读注明模型和待人工核验状态。

编程章节另列 Python 官方文档作为语言语义核对来源，记录具体版本和核对范围。上游 Python 学习入口用于确定学习方向，不被当作控制结构或函数规则的原始讲解；章节中的场景、数值、程序和练习由本项目重新设计。

数据结构章节还参考作者发布的 [Open Data Structures](https://opendatastructures.org/) 核对链表与循环数组的基本规则。书中的原代码、题目和插图不随本仓库发布；本项目采用自己的字典结点、固定容量拒绝策略和原创练习，具体差异在各章参考说明中列出。基础语法入口与数据结构原理的证明分开标明。

算法分析、查找与排序章节另参考 Sedgewick 与 Wayne 的 [Algorithms 4/e 作者网站](https://algs4.cs.princeton.edu/home/)、[Cornell CS312 渐近复杂度讲义](https://www.cs.cornell.edu/courses/cs312/2003sp/lectures/lec12.html)及 Python 官方 `bisect`、排序文档，核对定义、接口与成本边界。计数模型、演示数据、追踪过程、练习及 Python 实现由本项目编写；未复制原书习题、Java 实现或图示，也没有把这些外部核对材料计为上游资料库的新导读。

递归、分治和快速排序章节继续参考 Python 官方函数与递归限制说明，并用 [NIST DADS 分治定义](https://xlinux.nist.gov/dads/HTML/divideAndConquer.html)、[Cornell CS2110 排序讲义](https://www.cs.cornell.edu/courses/cs2110/2025fa/lectures/lec07/)和 Algorithms 4/e 的分区说明核对概念。半开区间、固定末项基准、共享缓冲和长边循环均按本项目实际实现分析；调用轨迹、计数数据、练习与 Python 程序自行设计，不移植课程代码、动画或习题解答。

树、二叉搜索树和堆章节用 [NIST DADS 完全二叉树定义](https://xlinux.nist.gov/dads/HTML/completeBinaryTree.html)、Open Data Structures 的树与堆章节、Algorithms 4/e 的搜索树与优先队列说明，以及 [Python 3.11 heapq 文档](https://docs.python.org/3.11/library/heapq.html)核对形状、键序、接口与成本。本项目自行设计字典结点、示例树、删除轨迹、堆数组、练习和测试；图示由本项目示例生成，未复制原书图表或练习解答。空树高度、重复键和空堆返回约定按正文明确说明，未将这些参考核对计为上游资料库的新导读。

哈希表、图与基础图遍历章节参考 [NIST DADS 散列函数定义](https://xlinux.nist.gov/dads/HTML/hash.html)、[Open Data Structures 分离链接说明](https://opendatastructures.org/ods-python/5_1_ChainedHashTable_Hashin.html)、[图的表示](https://opendatastructures.org/ods-python/12_Graphs.html)与[图遍历](https://opendatastructures.org/ods-python/12_3_Graph_Traversal.html)，并核对 Python 3.11 取余和递归深度语义。桶记录、图实例、栈帧、队列轨迹和练习由本项目设计；固定取余不继承随机散列的期望保证，带查重的建图也单独计算成本。原书图表、代码与习题解答未纳入公开内容，参考核对不增加上游导读覆盖。

拓扑排序、带权最短路与最小生成树章节用 [NIST 拓扑排序定义](https://xlinux.nist.gov/dads/HTML/topologicalSort.html)、[Aalto DFS 拓扑排序说明](https://tarjotin.cs.aalto.fi/CS-A1140/2020/notes/graphs-topological.html)、[Algorithms 4/e 最短路](https://algs4.cs.princeton.edu/44sp/index.php)、[最小生成树](https://algs4.cs.princeton.edu/43mst/index.php)及作者的并查集接口说明核对适用条件。部分作者页面通过搜索索引读取，直接打开返回 403 或超时。图、数值、轨迹、Python 实现及练习重新设计；懒堆旧记录、展平边表、完整路径压缩和失败接口均按本项目代码分析，未移植 Java 程序、教材图表或习题解答。章节中的上游 Python 学习入口只用于选题关联，不作为图算法证明来源，也未增加上游导读覆盖。

核查时发现上游许可声明存在差异：根目录 [LICENSE](https://github.com/PKUanonym/REKCARC-TSC-UHT/blob/master/LICENSE) 为 CC BY-SA 4.0，而 [README 许可部分](https://github.com/PKUanonym/REKCARC-TSC-UHT#许可) 的链接指向 CC BY-NC-SA 4.0，并明确其他内容版权归各自作者。本项目不替上游消解这一差异，也不为上游材料重新许可。

本项目新编写的程序、教材文本、维护文档和可独立许可的原创贡献采用根目录 MIT 许可。来源材料、可能涉及第三方权利的内容及其许可条件不被该许可覆盖。AI 辅助注释不能改变来源材料的权利，也不保证其判断准确。需要引用或改编具体材料时，应查看该材料适用的声明。

发现出处错误、导读过度复述或不适合公开的信息，可通过本仓库 Issue 指明路径。维护者会核查并更正或移除当前展示内容；普通提交历史的处理需要另行评估。

## 早期 README 成果

[早期成果归档](docs/early-work/index.md)收录维护者先前在本地整理的总知识图、分类总览、60 份课程指南及教材 README，共 63 份。公开副本保留学习内容，并移除本地绝对路径；归档清单仅记录相对路径、公开副本大小与 SHA-256；此次提交是既有成果补录，提交日期不冒充创作日期。历史状态仍为早期文档自述；相对资料引用保留，本地绝对路径已移除，涉及来源材料的权利继续适用上述边界。
