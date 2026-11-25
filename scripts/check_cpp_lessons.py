"""Explicitly compile/run the reviewed C++ lessons; never called by build/validate.

Run from the repository root: python scripts/check_cpp_lessons.py
Requires a GCC-compatible C++17 compiler (CXX may name one executable).
"""

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from cs_study_map.cpp import validate_cpp_program

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ("37-cpp-basics", "38-cpp-functions-lifetime", "39-cpp-files-project")
FLAGS = ("-std=c++17", "-Wall", "-Wextra", "-Wpedantic", "-Werror", "-O0")


def compiler():
    name = os.environ.get("CXX", "g++")
    executable = shutil.which(name)
    if not executable:
        raise RuntimeError("C++17 compiler required: install g++ or set CXX to one compiler executable")
    return executable


def programs():
    for chapter in CHAPTERS:
        document = json.loads((ROOT / "catalog/chapters" / (chapter + ".json")).read_text(encoding="utf-8"))
        for group in ("sections", "worked_examples", "exercises"):
            for index, item in enumerate(document["content"][group], 1):
                yield f"{chapter}/{group}/{index}", item["program"]


class CppProgram:
    """Temporary build and fresh run directories for explicitly reviewed sources."""

    def __init__(self, program, allow_compile_failure=False):
        validate_cpp_program(program)
        self.program = program
        self.temporary = tempfile.TemporaryDirectory(prefix="cs-study-cpp-")
        self.root = Path(self.temporary.name)
        self.executable = self.root / "lesson.exe"
        try:
            for name, code in program["files"].items():
                (self.root / name).write_text(code, encoding="utf-8", newline="\n")
            self.command = [compiler(), *FLAGS, *(n for n in program["files"] if n.endswith(".cpp")), "-o", str(self.executable)]
            self.environment = dict(os.environ)
            # Match MinGW runtime DLLs to the selected compiler, even when another
            # toolchain appears earlier in the parent process's PATH.
            self.environment["PATH"] = str(Path(self.command[0]).parent) + os.pathsep + os.environ.get("PATH", "")
            self.compilation = subprocess.run(self.command, cwd=self.root, capture_output=True, text=True,
                                              encoding="utf-8", errors="replace", timeout=60, shell=False,
                                              env=self.environment)
            if self.compilation.returncode and not allow_compile_failure:
                raise RuntimeError("C++ compilation failed:\n" + self.compilation.stderr)
        except BaseException:
            self.close()
            raise

    def close(self):
        self.temporary.cleanup()

    def run(self, stdin=None, fixtures=None, directories=()):
        if self.compilation.returncode:
            raise RuntimeError("Cannot run a failed C++ build")
        fixtures = self.program["fixtures"] if fixtures is None else fixtures
        # Apply the same filename constraints to caller-supplied test fixtures.
        validate_cpp_program(dict(self.program, fixtures=fixtures, artifacts={name: "" for name in directories}))
        with tempfile.TemporaryDirectory(prefix="run-", dir=self.root) as temporary:
            directory = Path(temporary)
            for name, contents in fixtures.items():
                (directory / name).write_text(contents, encoding="utf-8", newline="\n")
            for name in directories:
                (directory / name).mkdir()
            result = subprocess.run([str(self.executable)], cwd=directory, capture_output=True,
                                    input=self.program["stdin"] if stdin is None else stdin,
                                    text=True, encoding="utf-8", errors="strict", timeout=10, shell=False,
                                    env=self.environment)
            files = {p.name: p.read_text(encoding="utf-8") for p in directory.iterdir()
                     if p.is_file() and p.suffix in {".txt", ".csv"}}
            return {"stdout": result.stdout, "stderr": result.stderr, "exit_code": result.returncode, "files": files}


def main():
    version = subprocess.run([compiler(), "--version"], capture_output=True, text=True,
                             encoding="utf-8", errors="replace", timeout=10, check=True).stdout.splitlines()[0]
    checked = []
    for label, program in programs():
        compiled = CppProgram(program)
        try:
            result = compiled.run()
            expected = {"stdout": program["output"], "stderr": program["stderr"], "exit_code": program["exit_code"]}
            for key, value in expected.items():
                if result[key] != value:
                    raise AssertionError(f"{label}: {key}: {result[key]!r} != {value!r}")
            for name, contents in program["artifacts"].items():
                if result["files"].get(name) != contents:
                    raise AssertionError(f"{label}: artifact mismatch: {name}")
            checked.append(label)
        finally:
            compiled.close()
    print(json.dumps({"compiler": version, "flags": FLAGS, "passed": len(checked), "programs": checked}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
