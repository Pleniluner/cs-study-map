# 贡献指南

项目首先服务维护者本人自学。欢迎指出教材中讲不清楚或计算错误的地方、补充原创例题、修正分类与导读，以及改进解析程序。

1. 说明对应的上游路径、具体问题和依据。
2. 分类修正优先修改 `config/courses.json` 或 `config/overrides.json`。
3. 修改程序后运行 `python -m unittest discover -s tests -v`。
4. 生成页面使用 `cs-study-map build`，再运行 `cs-study-map validate --tracked`。

不要提交原始课程文件、提取全文、密钥、个人学习隐私或缓存。生成目录由工具维护；分类修正请放到 overrides。教材修订请改 `catalog/chapters/` 对应结构化稿，学习路线请改 `config/curriculum.json`；重新生成阅读页并核对例题与解答。运行生成工具不要求执行上游课程代码。

公开 PR 的测试不使用模型密钥。修改工作流、解析规则和模型提示词时，请说明对范围、成本和已有分析有效性的影响。
