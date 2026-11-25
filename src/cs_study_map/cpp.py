"""C++ lesson metadata and rendering. Validation never compiles or runs code."""

import re

from .storage import StudyError


def validate_cpp_program(program):
    fields = {"files", "stdin", "output", "stderr", "exit_code", "fixtures", "artifacts"}
    if not isinstance(program, dict) or set(program) != fields:
        raise StudyError("Invalid C++ program fields")
    names = set()
    for group, extensions, limit in [("files", "cpp|hpp", 8), ("fixtures", "txt|csv", 8), ("artifacts", "txt|csv", 8)]:
        files = program[group]
        if not isinstance(files, dict) or len(files) > limit:
            raise StudyError("Invalid C++ file collection")
        for name, content in files.items():
            if not isinstance(name, str) or not re.fullmatch(r"[a-z][a-z0-9_]*\.(?:" + extensions + ")", name):
                raise StudyError("C++ lesson filenames must be simple relative names")
            if name.split(".")[0] in {"con", "prn", "aux", "nul", *(f"com{i}" for i in range(1, 10)), *(f"lpt{i}" for i in range(1, 10))}:
                raise StudyError("Reserved C++ lesson filename")
            if group != "artifacts" and name in names:
                raise StudyError("Conflicting C++ lesson filename")
            names.add(name)
            if not isinstance(content, str) or len(content) > 16000 or "\x00" in content or "```" in content:
                raise StudyError("Invalid C++ lesson file text")
            if group == "files" and not content.strip():
                raise StudyError("Empty C++ source file")
        if sum(len(content) for content in files.values()) > 24000:
            raise StudyError("C++ lesson file collection too large")
    if "main.cpp" not in program["files"]:
        raise StudyError("C++ lesson needs main.cpp")
    for key in ("stdin", "output", "stderr"):
        if not isinstance(program[key], str) or len(program[key]) > 3000 or "\x00" in program[key] or "```" in program[key]:
            raise StudyError("Invalid C++ stream text")
    if type(program["exit_code"]) is not int or not 0 <= program["exit_code"] <= 125:
        raise StudyError("Invalid C++ expected exit code")


def cpp_program_lines(program):
    lines = ["", "**完整程序（C++17）**", ""]
    for name, code in program["files"].items():
        lines += [f"文件：`{name}`", "", "```cpp", code.rstrip(), "```", ""]
    units = " ".join(name for name in program["files"] if name.endswith(".cpp"))
    lines += ["**编译**（在本例独立目录内）", "", "```sh", f"g++ -std=c++17 -Wall -Wextra -Wpedantic -Werror {units} -o lesson.exe", "```", "",
              "运行命令（PowerShell、Linux/macOS 终端）：`./lesson.exe`。按下面列出的标准输入和文件样例准备数据。", ""]
    for name, content in program["fixtures"].items():
        lines += [f"**运行前文件：`{name}`**", "", *(["```text", content.rstrip("\n"), "```"] if content else ["（空文件）"]), ""]
    lines += ["**标准输入**", "", *(["```text", program["stdin"].rstrip("\n"), "```"] if program["stdin"] else ["（无输入）"]), "",
              "**预期输出**", "", *(["```text", program["output"].rstrip("\n"), "```"] if program["output"] else ["（无输出）"]), "",
              "**预期标准错误**", "", *(["```text", program["stderr"].rstrip("\n"), "```"] if program["stderr"] else ["（无输出）"]), "",
              f"**退出状态**：`{program['exit_code']}`。", ""]
    for name, content in program["artifacts"].items():
        lines += [f"**运行后文件：`{name}`**", "", *(["```text", content.rstrip("\n"), "```"] if content else ["（空文件）"]), ""]
    return lines
