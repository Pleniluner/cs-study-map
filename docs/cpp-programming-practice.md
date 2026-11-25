# 程序设计基础：C++ 编译、练习与小项目

[按原课程学习](course-writing-plan.md#programming-f25722d2ba) · [教材目录](textbook/index.md) · [第 37 章](textbook/37-cpp-basics.md) · [第 38 章](textbook/38-cpp-functions-lifetime.md) · [第 39 章](textbook/39-cpp-files-project.md) · [验证记录](verification.md)

这三个单元属于“程序设计与软件工程 → 程序设计基础”，使用 **C++17**。每章有 5 节讲解、2 个原创例题、3 道练习及折叠解答，共 30 个可独立构建的程序。一个多文件程序仍算一个程序。第 4、5 章可以作为控制流和函数概念预习，无需先读完第 6–36 章的算法。

| 单元 | 学习顺序 | 必须留下的检查结果 |
| --- | --- | --- |
| 从源码到运行 | 保存源码 → 编译 → 运行 → 分别检查三种结果 | 标准输出、标准错误、退出状态；整数与浮点、零值和范围边界 |
| 函数与对象的生命周期 | 画对象关系 → 预测修改 → 追踪销毁 → 编译验证 | 调用者是否改变、别名规则、空范围、按值返回和析构次序 |
| 组织完整的小程序 | 定义记录格式 → 测试纯计算 → 拆分文件 → 接文件输入输出 | 正常、空文件、坏记录、缺失文件、输出失败及旧报告保护 |

## 准备编译器

教材采用 GCC 风格命令，先执行 `g++ --version` 确认编译器可用。本批在 Windows 的 GCC 13.2.0 上实际编译运行；仓库 CI 在 Ubuntu 的两个 Python 版本任务中也执行同一套 C++ 测试。Python 负责驱动检查，教材里的 C++ 程序仍由真实编译器构建。

现有编译器支持 C++17 即可，不依赖第三方 C++ 库。仅运行 Python 地图工具时无需 C++ 编译器；运行整个测试套件或 C++ 检查脚本时必须具备编译器，缺失时会明确失败，不跳过后声称通过。`CXX` 可指定一个 GCC 兼容的编译器可执行文件，不能把整条带选项的命令填进去。

Windows 如果装了多个带 MinGW 运行库的软件，应让选定编译器的 `bin` 目录在当前终端的 PATH 中优先；否则编译出的程序可能加载另一套 `libstdc++`。本批实测遇到并修正了这一情况。自动检查脚本只调整自己的编译、运行子进程环境，不修改系统设置。手动运行可以先在 PowerShell 设置：

```powershell
$cppBin = Split-Path (Get-Command g++).Source
$env:PATH = "$cppBin;$env:PATH"
```

## 每个例子放在独立目录

在本机被 Git 忽略的 `.local/` 内新建练习目录，把该例列出的源文件按名字保存，使用 UTF-8 文本。只复制代码框中的源码；文件名说明、标准输入和预期输出分开保存。不同例子都有自己的 `main.cpp`，不能把它们拼到一个文件里。

单文件例子：

```sh
g++ -std=c++17 -Wall -Wextra -Wpedantic -Werror main.cpp -o lesson.exe
```

第 39 章汇总项目的三个文件放在同一目录，编译两个 `.cpp`；头文件会被它们包含：

```sh
g++ -std=c++17 -Wall -Wextra -Wpedantic -Werror main.cpp summary.cpp -o lesson.exe
```

也可以分步编译、链接，理解每一步的产物：

```sh
g++ -std=c++17 -Wall -Wextra -Wpedantic -Werror -c main.cpp -o main.o
g++ -std=c++17 -Wall -Wextra -Wpedantic -Werror -c summary.cpp -o summary.o
g++ main.o summary.o -o lesson.exe
```

每一步成功后才执行下一步。`lesson.exe` 是本指引统一使用的输出文件名；Linux 上同样可以使用这个名字，不表示生成了 Windows 格式程序。运行方式都是 `./lesson.exe`。

## 输入、输出和文件要分别核对

没有标准输入的程序直接运行。需要固定数量整数的程序可运行后输入相应数字；输入完所需数量即可得到结果。读到 EOF 的程序建议使用输入文件，避免终端结束输入的差异。

Linux/macOS 终端把给定标准输入保存为 `input.txt`，再执行：

```sh
./lesson.exe < input.txt > actual.txt 2> errors.txt
echo $?
```

PowerShell 不支持同样的 `<` 输入重定向。保存好 `input.txt` 后可用：

```powershell
Get-Content -Raw -LiteralPath input.txt | ./lesson.exe
$LASTEXITCODE
```

PowerShell 的文本管道可能附加行结束符，普通整数输入不受影响；要严格复现空输入、最后一行没有换行、尾随空格等情况，使用下面的 Python 调用。替换 `input_bytes` 为题目规定的字节，空输入用 `b""`；运行目录必须是可执行文件和样例数据所在目录。

```python
import subprocess
from pathlib import Path

input_bytes = b"4\n-2 3 4 0\n"
result = subprocess.run(
    [str(Path("lesson.exe").resolve())],
    input=input_bytes, capture_output=True, timeout=10, check=False,
)
print("stdout:", repr(result.stdout.decode("utf-8")))
print("stderr:", repr(result.stderr.decode("utf-8")))
print("exit:", result.returncode)
```

章节的“运行前文件”必须事先按原文创建。空文件确实保存为零字节，不能用空白行代替；显示框里的换行通常也要保留。运行后打开“运行后文件”，逐项比较内容。Windows 文本流常写 CRLF，Linux 常写 LF；本项目以文本读回统一换行为 `\n` 后比较，仍保留尾随空格和末尾换行。标准输出与标准错误分别比较，不依赖终端混合显示的先后顺序。

## 验收用例

| 范围 | 至少改变这些输入或调用 | 应检查什么 |
| --- | --- | --- |
| 第 37 章 | 0、上界、负数、数字超出类型、缺项 | 除法前的检查、空组区别、失败没有成功摘要 |
| 第 38 章 | 同一对象传两次、空指针加零长度、容量上界、返回容器后修改副本 | 允许或拒绝别名的契约、失败状态保持、结果所有权 |
| 严格分钟汇总 | 空文件、单个零、末行无换行、空白行、`45x`、两个数字、367 行 | 首个坏行号、旧摘要与旧报告保持、NONE 与零不同 |
| 七日汇总 | 同一天多条、编号 0 或 8、累计超过 1440、空文件 | 合法下标、逐日上限、七行完整报告 |
| 构建与资源 | 漏掉实现文件、窄化初始化、给 const 赋值、捕获异常时离开作用域 | 诊断阶段、失败构建没有可执行文件、析构次序 |

用目录占据 `report.txt` 的名字可以稳定验证“输出打不开”，但不能因此声称已经模拟了磁盘写到中途失败。代码检查了关闭后的状态；磁盘故障、原子替换和恢复机制仍超出本批实测范围。教材从不通过运行越界或悬空解引用来求一个“标准答案”。

## 一次检查已审读的 30 个程序

在仓库根目录、安装本项目的 Python 环境执行：

```sh
python scripts/check_cpp_lessons.py
python -m unittest discover -s tests -p 'test_cpp*.py' -v
```

第一条从章节 JSON 逐个取出本批程序，使用临时目录编译，提供输入与文件样例，并比较标准输出、标准错误、退出状态及预期文件，最后输出编译器、选项和通过的程序列表。第二条增加输入边界、别名、生命周期、独立统计参照、单独编译链接、故意构建失败以及元数据和渲染检查。执行前应审读源码；它不是用于运行未知源码的安全沙箱。

普通 `cs-study-map build` 和 `validate` 不编译、不运行 C++。它们只检查 C++ 程序元数据与文件名，并生成代码框；Python 程序另外有语法检查。模型生成了 C++ 文本，不等于通过编译，更不等于完成语义或学习效果验收。
