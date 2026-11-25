import copy
import json
import random
import subprocess
import unittest

from cs_study_map.cpp import cpp_program_lines, validate_cpp_program
from cs_study_map.storage import StudyError
from cs_study_map.textbook import CPP_BOOK_PROMPT_VERSION, validate_document
from scripts.check_cpp_lessons import CHAPTERS, FLAGS, ROOT, CppProgram, compiler, programs


class CppMetadataTests(unittest.TestCase):
    def setUp(self):
        self.program = copy.deepcopy(next(programs())[1])

    def test_rejects_paths_reserved_names_and_wrong_extensions(self):
        absolute_example = (ROOT / "main.cpp").as_posix()
        for name in ("../main.cpp", absolute_example, "sub/main.cpp", "Main.cpp", "con.cpp", "nul.hpp", "run.exe"):
            with self.subTest(name=name), self.assertRaises(StudyError):
                validate_cpp_program(dict(self.program, files={"main.cpp": "int main() {}", name: "x"}))

    def test_rejects_missing_fields_invalid_exit_and_markup(self):
        for field in self.program:
            bad = copy.deepcopy(self.program)
            del bad[field]
            with self.subTest(field=field), self.assertRaises(StudyError):
                validate_cpp_program(bad)
        for value in (True, -1, 126, "0"):
            with self.subTest(value=value), self.assertRaises(StudyError):
                validate_cpp_program(dict(self.program, exit_code=value))
        with self.assertRaises(StudyError):
            validate_cpp_program(dict(self.program, output="```cpp"))

    def test_metadata_validation_does_not_claim_compilation(self):
        # Structurally valid text is not promised to be valid C++; build never executes it.
        validate_cpp_program(dict(self.program, files={"main.cpp": "not valid C++"}))

    def test_cpp_rendering_preserves_files_streams_and_output_artifacts(self):
        program = next(p for n, p in programs() if n == "39-cpp-files-project/worked_examples/2")
        page = "\n".join(cpp_program_lines(program))
        self.assertEqual(page.count("```cpp"), 3)
        self.assertNotIn("```python", page)
        self.assertIn("main.cpp summary.cpp -o lesson.exe", page)
        self.assertIn("运行前文件：`report.txt`", page)
        self.assertIn("运行后文件：`report.txt`", page)
        self.assertIn("invalid line 2", page)
        self.assertIn("**退出状态**：`2`", page)

    def test_cpp_documents_require_programs_and_preserve_source_identity(self):
        for name in CHAPTERS:
            document = json.loads((ROOT / "catalog/chapters" / (name + ".json")).read_text(encoding="utf-8"))
            validate_document(document)
            self.assertEqual(document["prompt_version"], CPP_BOOK_PROMPT_VERSION)
            self.assertEqual(document["sources"][0]["analysis_id"], "087c523259f76448cca0")
            self.assertEqual(len(document["content"]["sections"]), 5)
            del document["content"]["exercises"][0]["program"]
            with self.assertRaises(StudyError):
                validate_document(document)


class CppLessonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.programs = dict(programs())
        cls.compiled = {}
        for label, program in cls.programs.items():
            built = CppProgram(program)
            cls.addClassCleanup(built.close)
            cls.compiled[label] = built

    def lesson(self, chapter, group, index):
        return self.compiled[f"{CHAPTERS[chapter - 37]}/{group}/{index}"]

    def check(self, result, stdout="", stderr="", status=0, artifacts=None):
        self.assertEqual(result["stdout"], stdout)
        self.assertEqual(result["stderr"], stderr)
        self.assertEqual(result["exit_code"], status)
        for name, content in (artifacts or {}).items():
            self.assertEqual(result["files"].get(name), content)

    def harness(self, chapter, group, index, code, includes=""):
        program = copy.deepcopy(self.lesson(chapter, group, index).program)
        prefix = program["files"]["main.cpp"].split("int main()", 1)[0]
        program["files"]["main.cpp"] = prefix + includes + "\nint main() {\n" + code + "\nreturn 0;\n}\n"
        program.update(stdin="", output="", stderr="", exit_code=0, fixtures={}, artifacts={})
        compiled = CppProgram(program)
        self.addCleanup(compiled.close)
        return compiled

    def test_all_30_published_programs_compile_and_match_every_result(self):
        self.assertEqual(len(self.compiled), 30)
        for label, built in self.compiled.items():
            with self.subTest(program=label):
                p = built.program
                self.assertEqual(built.compilation.stderr, "")
                self.check(built.run(), p["output"], p["stderr"], p["exit_code"], p["artifacts"])

    def test_seconds_bounds_and_failed_extraction(self):
        built = self.lesson(37, "sections", 4)
        for value in (0, 59, 60, 3599, 3600, 86399, 86400):
            self.check(built.run(str(value)), f"{value // 3600} {value // 60 % 60} {value % 60}\n")
        for text in ("", "x", "-1", "86401", "9" * 30):
            self.check(built.run(text), stderr="INVALID\n", status=1)

    def test_counted_sums_against_python_lists(self):
        rng = random.Random(37)
        cases = [[], [0], [-1000] * 1000, [1000] * 1000]
        cases += [[rng.randrange(-1000, 1001) for _ in range(n)] for n in range(1, 15)]
        built = self.lesson(37, "sections", 5)
        for values in cases:
            self.check(built.run(str(len(values)) + "\n" + " ".join(map(str, values))),
                       f"{sum(values)} {sum(v > 0 for v in values)}\n")

    def test_counted_sum_rejects_partial_results(self):
        built = self.lesson(37, "sections", 5)
        for text in ("-1", "1001", "2\n3", "2\n3 nope", "1\n1001", "1\n-1001"):
            self.check(built.run(text), stderr="INVALID\n", status=1)

    def test_boxes_against_capacity_coverage(self):
        built = self.lesson(37, "worked_examples", 1)
        for items, capacity in ((0, 1), (1, 1), (59, 60), (60, 60), (61, 60), (1000000, 1), (1000000, 999)):
            boxes = (items + capacity - 1) // capacity
            self.check(built.run(f"{items} {capacity}"), f"{items // capacity} {items % capacity} {boxes}\n")
            self.assertTrue(items == 0 or (boxes - 1) * capacity < items <= boxes * capacity)
        for text in ("3 0", "-1 2", "1 1001", "1000001 2", "7"):
            self.check(built.run(text), stderr="INVALID\n", status=1)

    def test_average_distinguishes_empty_zero_and_failure(self):
        built = self.lesson(37, "worked_examples", 2)
        for text, expected in (("0", "EMPTY\n"), ("2\n0 0", "0.00\n"), ("2\n-3 2", "-0.50\n"), ("1\n1000", "1000.00\n")):
            self.check(built.run(text), expected)
        for text in ("-1", "1001", "2\n1", "1\nx"):
            self.check(built.run(text), stderr="INVALID\n", status=1)

    def test_temperature_and_signed_parity(self):
        temperature = self.lesson(37, "exercises", 1)
        for value, expected in ((-100, "-148.0\n"), (0, "32.0\n"), (100, "212.0\n")):
            self.check(temperature.run(str(value)), expected)
        self.check(temperature.run("101"), stderr="INVALID\n", status=1)
        parity = self.lesson(37, "exercises", 2)
        for value in (-1000, -7, -1, 0, 1, 8, 1000):
            sign = "negative" if value < 0 else "positive" if value > 0 else "zero"
            self.check(parity.run(str(value)), f"{sign} {'even' if value % 2 == 0 else 'odd'}\n")

    def test_digits_against_decimal_representation(self):
        built = self.lesson(37, "exercises", 3)
        for value in (0, 1, 10, 100, 5070, 999999999, 1000000000):
            digits = str(value)
            self.check(built.run(str(value)), f"{len(digits)} {sum(map(int, digits))}\n")
        self.check(built.run("00017"), "2 8\n")
        self.check(built.run("1000000001"), stderr="INVALID\n", status=1)

    def test_value_and_reference_contracts(self):
        built = self.harness(38, "sections", 1, 'int x{-1000}; int y{next_value(x)}; std::cout << x << " " << y << "\\n";')
        self.check(built.run(), "-1000 -999\n")
        built = self.harness(38, "sections", 2, r'''
            for (int balance{0}; balance <= 20; ++balance) {
                for (int amount{-1}; amount <= 22; ++amount) {
                    int changed{balance}; bool ok{take(changed, amount)};
                    std::cout << ok << ' ' << changed << '\n';
                }
            }
        ''')
        expected = "".join(f"{int(0 <= a <= b)} {b - a if 0 <= a <= b else b}\n" for b in range(21) for a in range(-1, 23))
        self.check(built.run(), expected)

    def test_pointer_null_and_arithmetic_boundaries(self):
        built = self.harness(38, "sections", 3, r'''
            std::cout << add_one(nullptr) << '\n';
            for (int value : {-1, 0, 999, 1000}) {
                bool ok{add_one(&value)}; std::cout << ok << ' ' << value << '\n';
            }
        ''')
        self.check(built.run(), "0\n0 -1\n1 1\n1 1000\n0 1000\n")

    def test_array_empty_and_prefix_ranges(self):
        built = self.harness(38, "sections", 4, r'''
            const int data[]{-1000, 0, 7, 1000};
            for (std::size_t n{0}; n <= 4; ++n) { std::cout << sum_values(data, n) << '\n'; }
            std::cout << sum_values(nullptr, 0) << '\n';
        ''')
        values = [-1000, 0, 7, 1000]
        self.check(built.run(), "".join(f"{sum(values[:n])}\n" for n in range(5)) + "0\n")

    def test_destructors_run_during_caught_exception(self):
        built = self.harness(38, "sections", 5, r'''
            try { Trace first{3}; Trace second{4}; throw std::runtime_error{"stop"}; }
            catch (const std::runtime_error&) { std::cout << "caught\n"; }
        ''', '#include <stdexcept>\n')
        self.check(built.run(), "open 3\nopen 4\nclose 4\nclose 3\ncaught\n")

    def test_transfer_capacity_failure_and_aliasing(self):
        built = self.harness(38, "worked_examples", 1, r'''
            for (int from : {-1, 0, 1, 999, 1000, 1001}) {
                for (int to : {-1, 0, 1, 999, 1000, 1001}) {
                    for (int amount : {-1, 0, 1, 10, 1001}) {
                        int a{from}; int b{to}; bool ok{transfer(a, b, amount)};
                        std::cout << ok << ' ' << a << ' ' << b << '\n';
                    }
                }
            }
            int same{5}; bool ok{transfer(same, same, 0)};
            std::cout << ok << ' ' << same << '\n';
        ''')
        expected = ""
        for a in (-1, 0, 1, 999, 1000, 1001):
            for b in (-1, 0, 1, 999, 1000, 1001):
                for amount in (-1, 0, 1, 10, 1001):
                    ok = 0 <= a <= 1000 and 0 <= b <= 1000 and 0 <= amount <= a and b + amount <= 1000
                    expected += f"{int(ok)} {a - amount if ok else a} {b + amount if ok else b}\n"
        self.check(built.run(), expected + "0 5\n")

    def test_exchange_extremes_and_self_alias(self):
        built = self.harness(38, "exercises", 1, r'''
            int a{std::numeric_limits<int>::min()}; int b{std::numeric_limits<int>::max()};
            exchange(a,b); bool changed{a == std::numeric_limits<int>::max() && b == std::numeric_limits<int>::min()};
            exchange(a,a); std::cout << changed << ' ' << (a == std::numeric_limits<int>::max()) << '\n';
        ''', '#include <limits>\n')
        self.check(built.run(), "1 1\n")

    def test_find_first_returns_borrowed_element_and_empty_result(self):
        built = self.harness(38, "exercises", 2, r'''
            int values[]{2, 5, 2};
            for (int target : {2, 5, 7}) {
                const int* found{find_first(values, 3, target)};
                if (found == nullptr) { std::cout << -1 << '\n'; }
                else { std::cout << (found - values) << '\n'; }
            }
            std::cout << (find_first(nullptr, 0, 2) == nullptr) << '\n';
        ''')
        self.check(built.run(), "0\n1\n-1\n1\n")

    def test_filter_returns_independent_owned_results(self):
        built = self.harness(38, "exercises", 3, r'''
            for (const std::vector<int>& input : {std::vector<int>{}, std::vector<int>{-3,-1}, std::vector<int>{0,3,0,-1}}) {
                auto output{keep_nonnegative(input)};
                if (!output.empty()) { output[0] = 9; }
                std::cout << input.size() << ' ' << output.size() << ' ';
                if (!input.empty()) { std::cout << input[0]; }
                std::cout << '\n';
            }
        ''')
        self.check(built.run(), "0 0 \n2 0 -3\n4 3 0\n")

    def test_file_lines_empty_blank_unterminated_and_limit(self):
        built = self.lesson(39, "sections", 1)
        for text, count in (("", 0), ("\n", 1), ("a", 1), ("a\n", 1), ("a\n\nb", 3), ("x\n" * 1000, 1000)):
            self.check(built.run(fixtures={"notes.txt": text}), f"{count}\n")
        self.check(built.run(fixtures={}), stderr="cannot open input\n", status=1)
        self.check(built.run(fixtures={"notes.txt":"x\n"*1001}), stderr="too many lines\n", status=2)

    def test_strict_parser_rejects_prefixes_extra_fields_and_overflow(self):
        built = self.harness(39, "sections", 2, r'''
            std::string line;
            while (std::getline(std::cin,line)) {
                int value{77}; bool ok{parse_minutes(line,value)};
                std::cout << ok << ' ' << value << '\n';
            }
        ''')
        valid = ["0", "1440", " +15 ", "-0", "0007"]
        invalid = ["", " ", "12x", "1 2", "1.0", "1e2", "0x10", "-1", "1441", "9"*30]
        expected = "".join(f"1 {int(x)}\n" for x in valid) + "0 77\n"*len(invalid)
        self.check(built.run("\n".join(valid+invalid)+"\n"), expected)

    def test_multifile_separate_compile_and_link(self):
        built = self.lesson(39, "sections", 4)
        for name in ("main", "units"):
            run = subprocess.run([compiler(), *FLAGS, "-c", name+".cpp", "-o", name+".o"], cwd=built.root, capture_output=True, timeout=60, env=built.environment)
            self.assertEqual(run.returncode, 0, run.stderr)
        run = subprocess.run([compiler(), "main.o", "units.o", "-o", str(built.executable)], cwd=built.root, capture_output=True, timeout=60, env=built.environment)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.check(built.run(), "5\n")

    def test_missing_definition_and_invalid_sources_fail_compilation(self):
        program = copy.deepcopy(self.lesson(39, "sections", 4).program)
        del program["files"]["units.cpp"]
        cases = [program]
        for code in ('int main() { int x{3.5}; return x; }', 'int main() { const int x{1}; x = 2; return x; }'):
            cases.append(dict(program, files={"main.cpp":code}))
        for program in cases:
            built = CppProgram(program, allow_compile_failure=True)
            self.addCleanup(built.close)
            self.assertNotEqual(built.compilation.returncode, 0)
            self.assertTrue(built.compilation.stderr)
            self.assertFalse(built.executable.exists())

    def test_summary_against_independent_lists(self):
        built = self.harness(39, "sections", 5, r'''
            Summary result; std::string error;
            bool ok{summarize(std::cin,result,error)};
            std::cout << ok << ' ' << result.count << ' ' << result.total << ' ' << result.longest << '\n';
        ''')
        rng = random.Random(39)
        for values in ([], [0], [1440], [1440]*366, *[[rng.randrange(1441) for _ in range(n)] for n in range(1,12)]):
            self.check(built.run("\n".join(map(str,values))), f"1 {len(values)} {sum(values)} {max(values,default=0)}\n")

    def test_summary_failure_preserves_result_and_reports_stream_failure(self):
        built = self.harness(39, "sections", 5, r'''
            Summary result{1,7,7}; std::string error;
            std::istringstream bad{"3\nwrong\n"};
            bool ok{summarize(bad,result,error)};
            std::cout << ok << ' ' << result.count << ' ' << result.total << ' ' << result.longest << ' ' << error << '\n';
            std::istringstream failed{"3\n"}; failed.setstate(std::ios::badbit);
            ok = summarize(failed,result,error);
            std::cout << ok << ' ' << result.total << ' ' << error << '\n';
        ''')
        self.check(built.run(), "0 1 7 7 invalid line 2\n0 7 read error\n")

    def test_report_empty_zero_and_last_line_without_newline(self):
        built = self.lesson(39, "worked_examples", 1)
        for text, report in (("", "count 0\ntotal 0\nlongest NONE\n"), ("0", "count 1\ntotal 0\nlongest 0\n"), ("30\n45\n20", "count 3\ntotal 95\nlongest 45\n")):
            self.check(built.run(fixtures={"sessions.txt":text}), "saved\n", artifacts={"report.txt":report})

    def test_report_rejects_bad_missing_and_excessive_input_before_output(self):
        built = self.lesson(39, "worked_examples", 1)
        self.check(built.run(fixtures={"report.txt":"old\n"}), stderr="cannot open input\n", status=1, artifacts={"report.txt":"old\n"})
        for tail in ("", " ", "12x", "1 2", "-1", "1441", "9"*30):
            result = built.run(fixtures={"sessions.txt":"30\n"+tail+"\n", "report.txt":"old\n"})
            self.check(result, stderr="invalid line 2\n", status=2, artifacts={"report.txt":"old\n"})
        result = built.run(fixtures={"sessions.txt":"0\n"*367})
        self.check(result, stderr="too many records\n", status=2)
        self.assertNotIn("report.txt", result["files"])

    def test_report_output_open_failure(self):
        built = self.lesson(39, "worked_examples", 1)
        self.check(built.run(fixtures={"sessions.txt":"5\n"}, directories=("report.txt",)), stderr="cannot open output\n", status=3)

    def test_tolerant_parser_counting_and_limit(self):
        built = self.lesson(39, "exercises", 1)
        self.check(built.run("\n12x\n5\n1440\n "), "2 1445 3\n")
        self.check(built.run(""), "0 0 0\n")
        self.check(built.run("x\n"*367), stderr="too many records\n", status=1)

    def test_merge_aliases_and_failure_preservation(self):
        built = self.harness(39, "exercises", 2, r'''
            Summary a{1,10,10}; Summary b{2,60,40};
            bool ok{merge(a,b,b)}; std::cout << ok << ' ' << b.count << ' ' << b.total << ' ' << b.longest << '\n';
            Summary large{366,366,1}; Summary saved{1,7,7};
            ok = merge(large,a,saved); std::cout << ok << ' ' << saved.count << ' ' << saved.total << ' ' << saved.longest << '\n';
            Summary empty; ok = merge(empty,empty,empty);
            std::cout << ok << ' ' << empty.count << ' ' << empty.total << ' ' << empty.longest << '\n';
        ''')
        self.check(built.run(), "1 3 70 40\n0 1 7 7\n1 0 0 0\n")

    def test_weekly_project_against_day_buckets(self):
        built = self.lesson(39, "exercises", 3)
        cases = [[], [(1,1440)], [(7,1000),(1,30),(7,440),(1,20)], [(i,1440) for i in range(1,8)]]
        for records in cases:
            buckets = [sum(v for d,v in records if d == day) for day in range(1,8)]
            report = "".join(f"{i+1} {value}\n" for i,value in enumerate(buckets))
            self.check(built.run(fixtures={"week.txt":"\n".join(f"{d} {v}" for d,v in records)}), f"total {sum(buckets)}\n", artifacts={"weekly_report.txt":report})
        signed = built.run(fixtures={"week.txt": "+01\t+30\n 7    -0"})
        self.check(signed, "total 30\n", artifacts={"weekly_report.txt": "1 30\n2 0\n3 0\n4 0\n5 0\n6 0\n7 0\n"})

    def test_weekly_project_preserves_report_on_invalid_data(self):
        built = self.lesson(39, "exercises", 3)
        for tail in ("0 1", "8 1", "1 -1", "1 1441", "1 2 extra", "", "1", "1 3x", "1+30", "2-0", "2,30"):
            self.check(built.run(fixtures={"week.txt":"1 20\n"+tail+"\n", "weekly_report.txt":"old"}),
                       stderr="invalid line 2\n", status=2, artifacts={"weekly_report.txt":"old"})
        self.check(built.run(fixtures={"week.txt":"1 1440\n1 1\n"}), stderr="daily limit at line 2\n", status=2)
        self.check(built.run(fixtures={}), stderr="cannot open input\n", status=1)
        self.check(built.run(fixtures={"week.txt":""}, directories=("weekly_report.txt",)), stderr="cannot open output\n", status=3)


if __name__ == "__main__":
    unittest.main()
