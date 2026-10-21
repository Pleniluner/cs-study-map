"""Generate portable GitHub Markdown from public metadata only."""

import copy
import html
import re
from collections import Counter, defaultdict
from pathlib import PurePosixPath

from .ai import validate_result
from .github import source_url
from .pipeline import current_analysis
from .storage import StudyError, atomic_write, read_json, read_jsonl, write_json

TYPE_NAMES = {"lecture": "讲义", "exercise": "题目", "lab": "实验", "reference-code": "参考实现", "report": "报告", "reading": "阅读资料", "tool": "工具说明", "other": "其他"}


def md(value):
    value = html.escape(str(value), quote=False).replace("\n", " ").replace("\r", " ")
    return re.sub(r"([\\`*_[\]{}|])", r"\\\1", value)


def effective_result(project, record, analysis):
    result = copy.deepcopy(analysis["result"])
    override = project["overrides"].get("files", {}).get(record["path"], {})
    if set(override) - {"subjects", "resource_type", "summary"}:
        raise StudyError("Manual override contains unsupported fields")
    result.update(override)
    extraction = {"segments": [{"id": e["id"], "text": ""} for e in analysis["evidence"]]}
    validate_result(result, extraction, project["taxonomy"])
    return result, bool(override)


def build(project):
    root = project["root"]
    records = read_jsonl(root / "catalog/files.jsonl")
    state = read_json(root / "catalog/state.json")
    failures = read_json(root / "catalog/analysis-failures.json", {})
    live_ids = {r["id"] for r in records}
    analysis_dir = root / "catalog/analyses"
    if analysis_dir.exists():
        for path in analysis_dir.glob("*.json"):
            if re.fullmatch(r"[0-9a-f]{20}", path.stem) and path.stem not in live_ids:
                path.unlink()
    groups = defaultdict(list)
    counts = Counter()
    prepared = {}
    for r in records:
        analysis = current_analysis(project, r) if r["status"] == "pending" else None
        status = "analyzed" if analysis else r["status"]
        if not analysis and r["status"] == "pending" and failures.get(r["id"], {}).get("context_key"):
            status = "pending"  # failures remain queued, not falsely marked completed
        counts[status] += 1
        prepared[r["id"]] = (analysis, effective_result(project, r, analysis) if analysis else None)
        groups[r["course_id"]].append(r)
    generated = {}
    subject_courses = defaultdict(list)
    course_rows = []
    analyzed_by_subject = defaultdict(list)
    for course_id, resources in sorted(groups.items(), key=lambda item: item[1][0]["course_title"]):
        course = resources[0]
        analyzed = sum(bool(prepared[r["id"]][0]) for r in resources)
        supported = sum(r["status"] == "pending" for r in resources)
        title = course["course_title"]
        subject_courses[course["subject"]].append((course_id, title, len(resources), analyzed, supported))
        course_rows.append(f"| [{md(title)}](courses/{course_id}.md) | {md(project['taxonomy']['subjects'][course['subject']])} | {len(resources)} | {analyzed} / {supported} |")
        lines = [f"# {md(title)}", "", "[返回课程导航](../index.md)", "",
                 f"资料索引：{len(resources)} 份；当前可解析：{supported} 份；已生成 AI 导读：{analyzed} 份。", "",
                 "AI 导读基于可提取片段生成，尚未经学科专家逐条核验。建议基础与练习是学习建议。", "",
                 "## 已生成的导读", ""]
        if not analyzed:
            lines += ["本课程已建立来源索引，AI 导读仍在排队。下方链接可直接查看上游资料。", ""]
        for r in resources:
            analysis, effective = prepared[r["id"]]
            if not analysis:
                continue
            result, manual = effective
            url = source_url(state["repository"], analysis["source_commit"], r["path"])
            lines += [f"### {md(PurePosixPath(r['path']).name)}", "",
                      f"[原资料]({url}) · {TYPE_NAMES[result['resource_type']]} · {'部分提取' if analysis['coverage'] == 'partial' else '已提取可读文本'} · {'判断有不确定性' if result['uncertain'] else 'AI 自动判断'}", "",
                      md(result["summary"]), "", "**涉及知识**", ""]
            pointers = {e["id"]: e["locator"] for e in analysis["evidence"]}
            for topic in result["topics"]:
                evidence = "、".join(md(pointers[e]) for e in topic["evidence_ids"])
                lines.append(f"- {md(topic['name'])}（依据：{evidence}）")
            lines += ["", "**建议先了解**", ""]
            lines += ["- " + md(s) for s in result["suggested_prerequisites"]] or ["材料不足以给出具体建议。"]
            lines += ["", "**建议尝试**", ""]
            lines += ["- " + md(s) for s in result["suggested_exercises"]] or ["材料不足以给出具体建议。"]
            lines += ["", f"生成模型：{md(analysis['model'])}；人工修正：{'有' if manual else '无'}。", ""]
            for subject in result["subjects"]:
                analyzed_by_subject[subject].append((course_id, title, r, result))
        lines += ["## 全部资料索引", "", "“待识别”表示尚未得到有效 AI 结果；暂不支持的格式和构建产物仍保留来源链接。", "",
                  "| 文件 | 状态 |", "| --- | --- |"]
        for r in resources:
            analysis = prepared[r["id"]][0]
            label = "已有导读" if analysis else {"pending": "待识别", "unsupported": "暂不支持", "excluded": "不参与识别"}[r["status"]]
            lines.append(f"| [{md(r['path'])}]({source_url(state['repository'], state['commit'], r['path'])}) | {label} |")
        generated[f"docs/courses/{course_id}.md"] = "\n".join(lines) + "\n"
    index = ["# 计算机学习地图", "", "[项目说明](../README.md) · [运行与覆盖状态](status.md)", "",
             f"上游：[{md(state['repository'])}](https://github.com/{state['repository']})；索引版本：[`{state['commit'][:12]}`](https://github.com/{state['repository']}/commit/{state['commit']})。", "",
             f"共 {len(records)} 份文件，{len(groups)} 个课程/资料分组，{counts['analyzed']} 份有效 AI 导读。", "",
             "## 按领域浏览", ""]
    if (root / "config/curriculum.json").exists():
        index[2] += " · [开始读教材](textbook/index.md)"
    for identifier, title in project["taxonomy"]["subjects"].items():
        if subject_courses[identifier] or analyzed_by_subject[identifier]:
            index.append(f"- [{md(title)}](subjects/{identifier}.md)")
        lines = [f"# {md(title)}", "", "[返回导航](../index.md)", "", "## 课程入口", ""]
        for course_id, name, total, analyzed, supported in subject_courses[identifier]:
            lines.append(f"- [{md(name)}](../courses/{course_id}.md)：{total} 份资料，{analyzed} / {supported} 份可解析资料已有导读。")
        lines += ["", "## AI 识别到的相关资料", ""]
        for course_id, name, record, result in analyzed_by_subject[identifier]:
            lines += [f"- [{md(name)} / {md(PurePosixPath(record['path']).name)}](../courses/{course_id}.md)：{md(result['summary'])}"]
        if not analyzed_by_subject[identifier]:
            lines += ["尚无已通过结构与证据引用检查的 AI 导读。"]
        generated[f"docs/subjects/{identifier}.md"] = "\n".join(lines) + "\n"
    index += ["", "## 全部课程与分组", "", "分组名称来自目录及初始分类表；不能据此认定整门课程已经完整分析。", "",
              "| 课程 / 分组 | 初始领域 | 文件数 | AI 导读 / 可解析文件 |", "| --- | --- | ---: | ---: |", *course_rows]
    generated["docs/index.md"] = "\n".join(index) + "\n"
    valid_failures = {r["id"] for r in records if r["id"] in failures and not prepared[r["id"]][0]}
    status = ["# 运行与覆盖状态", "", "[返回导航](index.md)", "",
              f"- 索引对应上游提交：`{state['commit']}`", f"- 索引文件：{len(records)}", f"- 已生成且与当前内容匹配的 AI 导读：{counts['analyzed']}",
              f"- 等待识别（含失败后待重试）：{counts['pending']}", f"- 暂不支持的格式或大小：{counts['unsupported']}",
              f"- 构建产物等不参与识别：{counts['excluded']}", f"- 当前待重试记录：{len(valid_failures)}", "",
              "目录同步成功不代表 AI 已分析完全部资料。原资料变更后，旧导读会退出当前展示，等待重新分析。", "",
              "每条导读记录来源提交、内容标识、模型、提取覆盖范围与证据位置。模型判断仍可能出错，欢迎通过人工修正规则纠正。", "",
              "GitHub Actions 的运行记录显示最近检查时间。若未配置云端模型，工作流仍更新目录，并明确报告 AI 未配置；不会把规则分类冒充 AI 分析。", ""]
    generated["docs/status.md"] = "\n".join(status)
    old = read_json(root / "docs/generated-manifest.json", [])
    for relative in old:
        if relative not in generated and re.fullmatch(r"docs/(?:courses|subjects)/[a-z0-9-]+\.md", relative):
            (root / relative).unlink(missing_ok=True)
    for relative, contents in generated.items():
        atomic_write(root / relative, contents)
    write_json(root / "docs/generated-manifest.json", sorted(generated))
    write_json(root / "catalog/coverage.json", {"files": len(records), "groups": len(groups), **{k: counts[k] for k in ["analyzed", "pending", "unsupported", "excluded"]}})
    report = {"generated_pages": len(generated), "analyzed": counts["analyzed"], "pending": counts["pending"]}
    if (root / "config/curriculum.json").exists():
        from .textbook import build_textbook
        report["textbook"] = build_textbook(project)
    return report
