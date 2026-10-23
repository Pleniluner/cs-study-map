# cs-study-map · 给自己的计算机教材

简体中文 · [繁體中文](docs/readme/zh-TW.md) · [English](docs/readme/en.md) · [日本語](docs/readme/ja.md) · [Русский](docs/readme/ru.md) · [Français](docs/readme/fr.md) · [Deutsch](docs/readme/de.md) · [Italiano](docs/readme/it.md) · [Português](docs/readme/pt.md) · [Español](docs/readme/es.md) · [العربية](docs/readme/ar.md) · [한국어](docs/readme/ko.md)

把分散的计算机课程资料整理成可以循序学习、动手练习、回查来源的中文教材。

这是 Pleniluner 的个人自学项目：以 [REKCARC-TSC-UHT](https://github.com/PKUanonym/REKCARC-TSC-UHT) 为主要资料来源，追踪资料版本，识别知识点，再按先修关系重新组织讲解、原创例题、练习和自测。仓库同时提供阅读内容和维护这些内容的 Python 工具。

**[开始学习](docs/textbook/index.md)** · **[按课程选方向](docs/course-writing-plan.md)** · [查找资料](docs/index.md) · [运行说明](docs/usage.md) · [后续计划](docs/roadmap.md)

## 从哪里开始

直接打开 Markdown 即可阅读，无需安装程序或配置模型账号。

| 你想做什么 | 从这里进入 |
| --- | --- |
| 从基础概念开始试学 | [前三章试学指南](docs/study-guide.md)：字节、程序执行与内存分配 |
| 按顺序读教材 | [36 章教材索引](docs/textbook/index.md)：讲解、例题、练习解答与自测 |
| 按原课程安排学习 | [课程编写总表](docs/course-writing-plan.md)：先修、已有正文、待写单元与验收方式 |
| 运行例题和练习代码 | [编程练习指引](docs/programming-practice.md)：环境准备、运行步骤与预期输出 |
| 检查前三章的理解 | [综合练习](docs/unit-01-review.md)：6 道题、折叠解答与回读指引 |
| 查原始资料及导读 | [资料地图](docs/index.md)与[覆盖状态](docs/status.md) |
| 记录卡点和复习过程 | [学习记录模板](docs/learning-log-template.md)与[本机进度命令](docs/usage.md#study) |

建议先读讲解，自己推演例题，再完成练习和自测。编程题先预测输出，再运行程序、修改边界输入；遇到卡点时记下具体问题，回到对应章节核对。

## 已经写到哪里

目前有 **36 章中文教材草稿**。每章包含讲解、2 个原创例题、3 道练习及折叠解答、自测与来源说明。第 4–36 章使用 Python，合计提供 **330 段可独立运行的程序及预期输出**；验证方法和记录见[验证说明](docs/verification.md)。

| 章节 | 学习内容 |
| --- | --- |
| 1–5 | 二进制与字节、执行与栈、内存分配、控制结构、函数 |
| 6–12 | 数组、链表、栈、队列、算法分析、查找与排序 |
| 13–18 | 递归、分治、快速排序、树、二叉搜索树与堆 |
| 19–24 | 哈希表、图、DFS / BFS、拓扑排序、最短路与最小生成树 |
| 25–30 | 回溯、贪心、动态规划、背包、序列及区间与树形 DP |
| 31–36 | 字符串匹配、Trie、前缀和与窗口、单调结构、树状数组与线段树 |

这些内容仍是 **AI 教材初稿**，尚未经过学科专家或外部学习者试学验收。程序检查通过不等于所有讲解和学习效果已经得到验证。

后续按“原领域 → 原课程 → 课程内单元”扩展。[课程编写总表](docs/course-writing-plan.md)覆盖现有的 65 个课程／资料分组，并区分已有正文与待写内容；当前 36 章不代表完整课程体系。下一步优先补充程序设计基础的 C++ 语言与工程单元，其他方向按各自先修展开。具体缺口见[维护计划](docs/roadmap.md)，早期整理见[知识图与课程指南归档](docs/early-work/index.md)。

## 工具能做什么

- **追踪来源**：同步上游提交与文件索引，识别新增、修改、移动和删除，保留可回查的版本信息。
- **整理导读**：提取支持格式的文本，生成知识点、先修建议和练习建议，标明证据位置、提取范围及生成模型。
- **编写教材**：依据主题摘要和学习路线生成原创章节；来源或教学计划变化后，提示复核已有稿件。
- **保留人工判断**：通过配置覆盖自动分类，构建课程与领域导航。
- **记录学习**：离线保存个人进度、卡点和复习状态；章节更新后提示重新复习。

资料索引、有效 AI 导读和教材章节分别统计，当前覆盖以[状态页](docs/status.md)为准。支持文本、常见源码、可提取文本的 PDF、DOCX、PPTX 和 Notebook；扫描件 OCR、旧 DOC/PPT 与压缩包内部分析尚未支持。长资料可能只提取部分内容，导读会标明范围。

## 本地使用

需要 **Python 3.11 或更新版本**。在终端克隆仓库并创建虚拟环境：

```bash
git clone https://github.com/Pleniluner/cs-study-map.git
cd cs-study-map
python -m venv .venv
```

激活环境，按系统选择一条命令：

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# Linux / macOS
source .venv/bin/activate
```

安装后即可使用仓库已有内容，无需模型密钥：

```bash
python -m pip install -e .
cs-study-map study
cs-study-map validate --tracked
```

记录学习状态：

```bash
cs-study-map study --chapter 01-data-and-bytes --status reading
cs-study-map study --chapter 01-data-and-bytes --note "还需要练习从字节还原整数"
cs-study-map study --chapter 01-data-and-bytes --status completed
```

进度保存在被 Git 忽略的 `.local/study-progress.json` 中。`completed` 由学习者完成自测后自行确认；完整状态与版本复习规则见[运行说明](docs/usage.md#study)。

需要更新资料目录时运行：

```bash
cs-study-map run --limit 0
```

该命令联网获取上游文件元数据、重建导航并校验，不调用模型，也不下载原始资料全文。只想用已有数据重建阅读页，可运行 `cs-study-map build`。

## 可选：接入 AI 与自动更新

生成新导读和新章节时，可选择模型 API 或本机已登录的 Codex CLI：

| 方式 | 所需配置 |
| --- | --- |
| 模型 API | `CS_STUDY_API_BASE`、`CS_STUDY_MODEL`、`CS_STUDY_API_KEY` |
| Codex CLI | `CS_STUDY_PROVIDER=codex`、`CS_STUDY_MODEL`；必要时指定 `CS_STUDY_CODEX_BIN` |

API 支持 Chat Completions 和 Responses；默认 `chat`，可通过 `CS_STUDY_API_STYLE=responses` 切换。配置示例见 [docs/usage.md](docs/usage.md)，变量清单见 [.env.example](.env.example)；程序不会自动加载 `.env` 文件。

配置完成后，可小批量分析和写作：

```bash
cs-study-map analyze --course 程序设计基础 --limit 2 --require-ai
cs-study-map write --limit 1 --require-ai
```

分析会把提取片段发送给所配置的模型服务；教材写作使用主题摘要。`write` 会构建并校验输出，已存在且输入未变的章节会复用。写作范围由 [config/curriculum.json](config/curriculum.json) 控制。

[Sync study map 工作流](.github/workflows/sync.yml)配置为每日检查上游，也支持在 Actions 页面手动运行，默认每次最多分析 6 份资料、编写 1 章。未配置模型时仍同步目录，并报告 `not-configured`。Fork 后的模型配置与工作流启用步骤见[运行说明](docs/usage.md)。

## 维护与贡献

| 目录 | 内容 |
| --- | --- |
| `config/` | 来源、分类体系、课程映射、人工修正与教材计划 |
| `catalog/` | 文件元数据、分析结果、结构化教材与覆盖统计 |
| `docs/textbook/` | 生成的教材阅读页 |
| `docs/` | 课程与领域导航、练习指引、使用说明与计划 |
| `src/cs_study_map/` | 同步、提取、分析、教材写作、构建及校验代码 |
| `tests/` | 工具行为、教材程序与发布检查的测试 |
| `.github/workflows/` | 自动同步与 CI |
| `.cache/`、`.local/` | 被 Git 忽略的原资料缓存、个人进度及私下笔记 |

修改教材正文时，应编辑 `catalog/chapters/` 中对应的结构化稿件；直接修改生成的阅读页会被下次构建覆盖。分类纠错可以修改 `config/overrides.json`，具体格式见[运行说明](docs/usage.md)。

在仓库根目录复现构建与检查：

```bash
cs-study-map build
cs-study-map validate --tracked
python -m unittest discover -s tests -v
```

这些检查使用已有数据和本地测试样例，无需模型密钥。构建与校验不执行新生成的模型代码；教材程序由对应测试单独验证。项目现状与验证范围见[项目概况](docs/project-brief.md)。

欢迎通过 Issue 指出具体章节、分类或导读问题，通过 PR 提交修正。提交前请阅读[贡献指南](CONTRIBUTING.md)。

## 来源与许可

本项目由 Pleniluner 维护，与清华大学及上游维护者没有官方隶属关系。感谢 [REKCARC-TSC-UHT](https://github.com/PKUanonym/REKCARC-TSC-UHT) 的维护者和贡献者整理课程资料。

原创程序、教材文本和维护文档采用 [MIT 许可](LICENSE)。上游材料及其权利不因此改变；原始教材、课件、作业、学生源码和提取全文不随本仓库发布。具体出处、署名及许可边界见[来源说明](ATTRIBUTION.md)。
