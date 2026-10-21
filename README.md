# cs-study-map · 给自己的计算机教材

| 简体中文 | [繁體中文](docs/readme/zh-TW.md) | [English](docs/readme/en.md) | [日本語](docs/readme/ja.md) | [Русский](docs/readme/ru.md) | [Français](docs/readme/fr.md) | [Deutsch](docs/readme/de.md) | [Italiano](docs/readme/it.md) | [Português](docs/readme/pt.md) | [Español](docs/readme/es.md) | [العربية](docs/readme/ar.md) | [한국어](docs/readme/ko.md) |

主要供本人自学：从 [REKCARC-TSC-UHT](https://github.com/PKUanonym/REKCARC-TSC-UHT) 识别可以学习的知识，按照先修关系重新组织成中文教材，补上概念讲解、原创例题、练习解答和自测。自动同步、分类与资料导读为教材选材和更新提供支持。

**[开始读教材](docs/textbook/index.md)** · [三章试学指南](docs/study-guide.md) · [综合练习](docs/unit-01-review.md) · [查找参考资料](docs/index.md) · [覆盖状态](docs/status.md) · [使用与运行](docs/usage.md) · [来源与许可](ATTRIBUTION.md)

这是 Pleniluner 维护的个人学习项目，与清华大学及上游维护者没有官方隶属关系。公开仓库包含原创工具、教材草稿、来源索引和 AI 导读。原始教材、课件、作业、学生源码和提取全文不会随本仓库发布。

## 先从三章开始

| 顺序 | 学什么 | 动手任务 |
| --- | --- | --- |
| 1 | [二进制、字节与小端序](docs/textbook/01-data-and-bytes.md) | 把一个数拆成字节，再从内存还原 |
| 2 | [寄存器、内存与栈](docs/textbook/02-execution-and-stack.md) | 逐步追踪玩具机器的状态变化 |
| 3 | [首次适应、拆分与合并](docs/textbook/03-first-fit.md) | 手算分配和释放，解释外部碎片 |

每章有实质讲解、2 个原创例题、3 道练习与折叠解答、自测以及选题来源。先按入门者的需要编排，后续根据本人的学习卡点调整。它还是 AI 教材初稿，尚未经过学科专家或学习者试学验收；现阶段不代表全部课程已经写成教材。

第一次阅读可先看[试学指南](docs/study-guide.md)，分清三章使用的不同存储单位；读完后用 [6 道综合练习](docs/unit-01-review.md)检查掌握情况，每题都有折叠解答与回读指引。已安装项目时，可用 `cs-study-map study` 查看本机进度，记录方法见[运行说明](docs/usage.md#study)。

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
