"""Regression checks for real C++ stream failures and atomic summary updates."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
DRIVER = r'''
#include "summary.hpp"
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <streambuf>
#include <string>

class FailingBuffer : public std::streambuf {
    const std::string data{"11\n"};
    std::size_t position{0};
protected:
    int_type underflow() override {
        if (position == data.size()) {
            throw std::runtime_error{"simulated device failure"};
        }
        return traits_type::to_int_type(data[position]);
    }
    int_type uflow() override {
        int_type value{underflow()};
        ++position;
        return value;
    }
};

void inspect(std::istream& input) {
    Summary result{7, 49, 7};
    std::string error{"previous error"};
    bool ok{summarize(input, result, error)};
    std::cout << ok << ':' << result.count << ':' << result.total << ':'
              << result.longest << ':' << error << '\n';
}

int main(int argc, char* argv[]) {
    if (argc != 2) {
        return 1;
    }
    const std::string mode{argv[1]};
    if (mode == "device-failure") {
        FailingBuffer buffer;
        std::istream input{&buffer};
        inspect(input);
        return 0;
    }
    if (mode == "stdin") {
        inspect(std::cin);
        return 0;
    }
    std::istringstream input{"20\n"};
    if (mode == "bad-eof") {
        input.setstate(std::ios::badbit | std::ios::eofbit);
    } else if (mode == "bad") {
        input.setstate(std::ios::badbit);
    } else if (mode == "fail") {
        input.setstate(std::ios::failbit);
    } else {
        return 1;
    }
    inspect(input);
}
'''


class CppStreamContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which(os.environ.get("CXX", "g++"))
        if compiler is None:
            raise RuntimeError("C++ lesson checks require a C++17 compiler (set CXX to its executable).")
        cls.directory = tempfile.TemporaryDirectory(prefix="cpp-stream-contract-")
        cls.addClassCleanup(cls.directory.cleanup)
        cls.root = Path(cls.directory.name)
        cls.environment = dict(os.environ)
        # Use the selected compiler's DLLs when several MinGW installations coexist.
        cls.environment["PATH"] = str(Path(compiler).parent) + os.pathsep + os.environ.get("PATH", "")
        document = json.loads((ROOT / "catalog/chapters/39-cpp-files-project.json").read_text(encoding="utf-8"))
        files = document["content"]["worked_examples"][0]["program"]["files"].copy()
        files["main.cpp"] = DRIVER
        for name, content in files.items():
            (cls.root / name).write_text(content, encoding="utf-8")
        cls.executable = cls.root / "contract.exe"
        result = subprocess.run(
            [compiler, "-std=c++17", "-Wall", "-Wextra", "-Wpedantic", "-Werror",
             "main.cpp", "summary.cpp", "-o", str(cls.executable)],
            cwd=cls.root, capture_output=True, encoding="utf-8", timeout=45, env=cls.environment,
        )
        if result.returncode != 0 or result.stderr:
            raise AssertionError("C++ stream regression driver did not compile cleanly: " + result.stderr)

    def check(self, mode, output, stdin=""):
        result = subprocess.run([str(self.executable), mode], cwd=self.root,
                                input=stdin, capture_output=True, encoding="utf-8",
                                timeout=10, env=self.environment)
        self.assertEqual((result.returncode, result.stdout, result.stderr), (0, output, ""))

    def test_badbit_with_eofbit_is_not_success_and_preserves_result(self):
        self.check("bad-eof", "0:7:49:7:read error\n")

    def test_initial_failure_states_preserve_result(self):
        for mode in ("bad", "fail"):
            with self.subTest(mode=mode):
                self.check(mode, "0:7:49:7:read error\n")

    def test_device_failure_after_a_complete_record_does_not_commit_prefix(self):
        self.check("device-failure", "0:7:49:7:read error\n")

    def test_crlf_whitespace_sign_and_unterminated_last_line(self):
        self.check("stdin", "1:3:1485:1440:\n", "0\r\n\t+0045 \r\n1440")

    def test_empty_file_differs_from_one_zero_record_and_blank_line(self):
        for data, output in (("", "1:0:0:0:\n"), ("0", "1:1:0:0:\n"),
                             ("\n", "0:7:49:7:invalid line 1\n")):
            with self.subTest(data=data):
                self.check("stdin", output, data)

    def test_late_invalid_record_does_not_commit_valid_prefix(self):
        for suffix in ("45x", "45 60", "1.5", "0x10", "\t", "-1", "1441", "9" * 80):
            with self.subTest(suffix=suffix):
                self.check("stdin", "0:7:49:7:invalid line 3\n", "15\n20\n" + suffix)


if __name__ == "__main__":
    unittest.main()
