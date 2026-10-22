# 使用与运行

[返回项目](../README.md)

## 常用操作

| 命令 | 行为 |
| --- | --- |
| `cs-study-map sync` | 获取上游最新提交和完整文件索引 |
| `cs-study-map analyze --limit 6` | 最多尝试处理 6 份待识别资料 |
| `cs-study-map analyze --course 操作系统 --limit 2` | 限定课程；`--course` 可重复 |
| `cs-study-map analyze --path '大三下/操作系统/README.md'` | 限定精确上游路径，路径必须实际存在 |
| `cs-study-map build` | 从当前有效结果生成 Markdown |
| `cs-study-map study` | 离线查看本机学习进度及下一章 |
| `cs-study-map study --chapter 01-data-and-bytes --status reading` | 记录开始学习，进度保存在 `.local/` |
| `cs-study-map write --limit 1 --require-ai` | 根据学习路线生成最多 1 章原创教材并验证 |
| `cs-study-map write --chapter 01-data-and-bytes` | 只处理指定章节；输入未变时复用现有章节 |
| `cs-study-map validate --tracked` | 检查来源、页面链接及 Git 跟踪文件 |
| `cs-study-map run --limit 6` | 顺序执行同步、分析、生成、验证 |
| `cs-study-map fetch-updates --baseline-dir '<本地上游旧快照>'` | 按真实内容比对，只把新增/修改文件下载到忽略缓存 |

可用 `--root` 指定项目目录。模型调用前只读解析原资料，不执行课程程序、Notebook 单元、宏或构建脚本。`--limit` 限制尝试次数，解析失败也计入上限；接口故障会提前停止，避免重复请求。

<a id="study"></a>

## 本机学习进度

阅读教材不需要安装程序。安装后，`study` 命令可以保存个人状态和短笔记；它完全使用本机教材，不访问网络或调用 AI。仅查看进度不会新建或改写记录。

```bash
# 查看全部章节的进度与下一步
cs-study-map study
# 开始一章，也可只传 --chapter 查看本章自测清单
cs-study-map study --chapter 01-data-and-bytes --status reading
# 追加卡点，不改变已有完成状态或确认教材的新版本
cs-study-map study --chapter 01-data-and-bytes --note "高字节增加 1，整个数为什么增加 256？"
# 独立完成章末自测后，由自己标记完成
cs-study-map study --chapter 01-data-and-bytes --status completed
```

状态可选 `not-started`（未开始）、`reading`（学习中）、`review`（待复习）、`completed`（已完成自测）。可以随时改回 `reading` 或 `review`；改为 `not-started` 会重置该章状态并保留笔记。完成状态是个人确认，程序不会自动判分，也不会据此声称掌握全部知识。

进度和笔记写入 `.local/study-progress.json`，不会进入公开教材。命令输出仅含笔记数量，不回显笔记正文；较长的过程可另记在 `.local/study-log.md`。Git 仓库中只有确认进度文件被忽略后才允许保存。

记录状态时会保存本次学习的章节版本。正文修订后，旧的完成记录显示为“待复习”；来源或计划变化导致教材待复核时，也不会计入当前已完成数量。仅追加笔记不能消除这种提醒，复习后需重新明确标记完成。待编写章节无法记录学习状态，来源待复核的章节不能标记完成。

`next_chapter` 按教材顺序返回第一章未完成的章节；若它尚未编写或来源待复核，请先查看输出中的 `availability`，不要把它当作已有的新教材。移出路线的个人记录仍留在本机，输出中的 `archived_records` 表示其数量。

## 本地 API 配置

PowerShell 示例；将尖括号部分替换为你自己的服务信息，不要把密钥写入任何被 Git 跟踪的文件：

```powershell
$env:CS_STUDY_API_BASE = 'https://<模型服务地址>/v1'
$env:CS_STUDY_MODEL = '<服务提供的模型名称>'
$env:CS_STUDY_API_KEY = '<仅在本机设置的密钥>'
cs-study-map run --course 数据结构 --limit 2 --require-ai
```

Linux / macOS 使用对应的 `export` 环境变量。`.env.example` 仅说明变量，不会被自动加载。API 地址不能包含账号、密码、查询参数；远程地址使用 HTTPS，本机环回地址可用 HTTP。

## 本地 Codex 配置

安装支持所选模型的 Codex CLI 并完成登录，然后：

```powershell
$env:CS_STUDY_PROVIDER = 'codex'
$env:CS_STUDY_MODEL = '<你的 Codex 可用模型>'
# PATH 中的 codex 版本过旧时可指定当前版本的可执行文件：
# $env:CS_STUDY_CODEX_BIN = '<Codex 可执行文件绝对路径>'
cs-study-map run --course 程序设计基础 --limit 2 --require-ai
```

分类调用使用只读、临时会话，关闭用户配置、shell、应用、插件和子代理工具。它仅处理输入片段并返回 JSON；检测到工具调用的结果会被拒绝。工作流不会上传本机 Codex 登录凭据。

## GitHub 上自动运行

仓库 **Settings → Secrets and variables → Actions** 中设置：

| 类型 | 名称 | 用途 |
| --- | --- | --- |
| Secret | `CS_STUDY_API_KEY` | 模型服务密钥 |
| Variable | `CS_STUDY_API_BASE` | 服务基础地址，通常以 `/v1` 结尾 |
| Variable | `CS_STUDY_MODEL` | 模型名称 |
| Variable，可选 | `CS_STUDY_API_STYLE` | `chat`（默认）或 `responses` |

工作流默认最多尝试 6 份资料。手动触发时可设置 0–100 的处理上限，并可勾选“必须完成 AI 分析”：没有模型配置或分析失败时任务会失败，保留上一个已经发布的版本。

每日检查时间为 UTC 03:23（北京时间/新加坡时间 11:23）。GitHub 定时任务可能延迟，公开仓库 60 天无活动后可能被停用。最近运行结果以 Actions 页面为准。Fork 后需要自行启用工作流并配置模型，公共 PR 的测试不会获得模型密钥。

## 人工修正

在 `config/overrides.json` 的 `files` 中用精确上游路径作为键，可以覆盖 `subjects`、`resource_type`、`summary`。领域及类型必须来自 `config/taxonomy.json`。例如：

```json
{
  "files": {
    "上游实际路径/资料.md": {
      "subjects": ["systems"],
      "resource_type": "lab"
    }
  }
}
```

这些修正在每次生成页面时应用，不会被后续 AI 输出覆盖；路径移动后需要同步修改规则。课程层级的初始归类在 `config/courses.json` 维护。资料可以同时具有多个知识领域标签。

## 缓存与更新

教材写作范围在 `config/curriculum.json` 配置。每章包含学习者起点、教学范围和选题所依据的分析主题。写作模型只接收主题摘要，不接收上游原文；例题、练习和解答重新设计。来源不确定、尚未分析或已失效时，章节保持待编写，不会从文件名补全整章。教材正文保存在 `catalog/chapters/`，阅读版由 `build` 生成至 `docs/textbook/`。

编程章节使用 `"format": "python"`；省略时仍按原来的文字章节处理。讲解、例题和练习可以包含 `program` 对象，其 `code` 为完整 Python 源码，`output` 为准确标准输出；编程章节的每道例题和练习都必须提供。构建会保留缩进，将练习程序放在折叠解答里。运行方式见[编程练习指引](programming-practice.md)。

语言、数据结构与算法分析参考可在章节计划的 `references` 中记录 `title`、HTTPS `url` 和 `note`，生成时随稿保存快照。上游学习入口只说明选题关联；具体规则另用官方文档或作者提供的教材核对。校验与构建只检查代码语法，不执行模型生成的代码。本项目对第 4–18 章已经审读的原创程序另设测试，逐段核对输出、边界、结构不变式、对象身份、计数结论及实际调用深度；新章节仍需在发布前单独验算。

`write` 默认最多调用 1 次，允许 0–10；已存在且输入未变化的章节不会重复调用模型。程序核对字段、篇幅、引用及完整性，但不能自动保证学科结论正确，章节始终标为 `ai-draft`。来源、人工分类修正、教学范围或提示词改变后，旧稿会显示待复核，重新执行写作命令才会替换旧稿。直接编辑阅读页会被下一次 `build` 覆盖；内容修订请改对应的结构化章节，并保留来源说明。

本人的学习进度和私下笔记放在 `.local/`，可从[学习记录模板](learning-log-template.md)开始。公开教材可持续扩展，个人记录默认不公开。

`fetch-updates` 会读取旧快照并计算内容标识，排除相同内容仅改名或移动的文件。下载清单保存在 `.cache/updates/<上游提交>/manifest.json`，记录原路径、变动类型、实际缓存位置与校验状态。中断后重新运行同一命令会复用比较清单和已验证内容；若原快照内容已经更换，请先移走旧比较清单再重新比对。旧快照不会被改写。该命令不会把下载文件添加到 Git。

原资料缓存在 `.cache/blobs/`，每份文件下载后校验 Git blob SHA；提取片段保存在 `.cache/extracted/`。默认不上传缓存或原文作为 Actions artifact。

分析有效性同时取决于内容、路径/课程上下文、分类体系、提取设置和提示词。改变这些输入后，旧导读退出当前展示，重新进入分析队列。更换模型不会自动重做所有已有结果；需要重新分析时，可移除对应的 `catalog/analyses/<文件 id>.json` 后运行。模型请求超时或开始输出后失败不会被自动重放。

上游删除文件后，当前公开导航与对应导读会移除；普通 Git 提交历史仍保留历史版本。如需从历史中移除内容，应单独处理。

## 当前限制

- 不执行 OCR；扫描件或提取不足会标记失败并保留待识别状态。
- 不读取压缩包内部，不处理旧 DOC/PPT，也不运行二进制或源码。
- AI 依据引用检查只能验证它引用了已提供的位置，不能证明全部学科判断正确。
- 为控制体积和调用量，长资料按设置部分提取；导读会显示覆盖范围。
- 原始片段会发送给你配置的模型服务，供识别使用；公开 GitHub 仓库只保存摘要及证据位置。
