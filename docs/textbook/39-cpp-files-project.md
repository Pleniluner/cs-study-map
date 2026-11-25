# 组织完整的小程序：C++ 文件、接口与测试

[返回教材目录](index.md) · [C++ 练习与编译](../cpp-programming-practice.md)

[上一章：函数与对象的生命周期：C++ 值、引用和指针](38-cpp-functions-lifetime.md)

[学习目标](#objectives) · [需要的基础](#prerequisites) · [例题](#examples) · [练习](#practice) · [自测](#self-check)

状态：**AI 初稿，可开始试学**。生成模型：Codex 当前会话（未记录具体模型型号）。

本章围绕资料中识别到的知识点重新编写；讲解、数值模型、例题与练习为 AI 原创组织，不是原课程题目或答案。主题出处只说明选题关联，不证明全部推导已经正确。

这一章把程序设计基础的 C++ 知识连成一个可复现的小项目：从文本文件读取学习时长，校验每条记录，计算摘要，再生成报告。与只在 main 中放几个固定数字相比，文件可能不存在、数据可能缺项、输出也可能失败；接口必须说明这些情况。我们会分开数据解析、摘要计算与文件操作，用同一计算代码处理内存中的测试文本和真实文件，再把构建与检查过程固定下来。读完后，你应能交付一组源文件、样例数据、明确的错误规则和实际运行证据。

<a id="objectives"></a>

## 学完要能做到

- 用文件流与 getline 正确处理空文件、末行无换行和读取失败。
- 拒绝数字前缀、多余字段、越界数与空白记录，并使失败保留原结果。
- 解释返回状态与异常的不同控制流，避免把普通流失败误认为自动抛出异常。
- 把声明、实现和入口分成多个文件，正确编译链接并定位漏链接错误。
- 完成原创汇总工具，核对正常、边界与失败路径及生成文件内容。

<a id="prerequisites"></a>

## 需要的基础

- 第 37 章的 C++17 类型、分支、循环和输入输出。
- 第 38 章的引用、const、struct、作用域与资源生命周期。
- 会在独立目录保存多个文件，并按顶部练习指引使用终端或自动检查命令。

## 1. 文件流与逐行读取：让读取动作控制循环

标准输入适合临时提供数据，文件让一次运行可以复现。fstream 中的 ifstream 打开输入文件，ofstream 打开输出文件；它们也是管理资源的对象，正常离开作用域时会清理关联资源。相对文件名相对于程序运行时的当前工作目录解释，不是自动相对于源码所在目录。下面先尝试打开 notes.txt，立刻检查状态；文件不存在时输出诊断并返回，而不是把它当作空文件。

std::string 管理一串字符。getline 从流中取得一行，消费换行分隔符但不把它放进字符串；空白行也可以成功读取，得到空字符串。把 getline 本身作为 while 条件，只有读到一行才计数。不要先判断尚未到 EOF 再读取，因为 EOF 状态通常要在尝试读取时才会设置，那种写法容易把失败的最后一次读取也当成数据。本例最多接受 1000 行，避免让 int 计数无约束增长。

循环结束后还要解释为什么结束。正常结束应看到 EOF，并且没有表示底层读取故障的 badbit；用 bad 检查故障状态，不能仅凭 eof 为真就认定成功。状态位可以同时存在，故障与 EOF 并存时仍须失败；没有 EOF 的失败也按读错误处理。本例统计的是成功取得的行，不是换行字符数：alpha 后一个空行，再有 beta，共三行；最后的 beta 即使没有换行也仍算一行。空文件有零行，而只有一个换行的文件有一条空行。这里不限制每行字符数，读取一行所需内存随其长度增长；示例文件很小，不能据此声称已经具备处理任意大文件的能力。

**完整程序（C++17）**

文件：`main.cpp`

```cpp
#include <fstream>
#include <iostream>
#include <string>
int main() {
    std::ifstream input{"notes.txt"};
    if (!input) {
        std::cerr << "cannot open input\n";
        return 1;
    }
    std::string line;
    int count{0};
    while (std::getline(input, line)) {
        if (count == 1000) {
            std::cerr << "too many lines\n";
            return 2;
        }
        ++count;
    }
    if (input.bad() || !input.eof()) {
        std::cerr << "read error\n";
        return 2;
    }
    std::cout << count << '\n';
    return 0;
}
```

**编译**（在本例独立目录内）

```sh
g++ -std=c++17 -Wall -Wextra -Wpedantic -Werror main.cpp -o lesson.exe
```

运行命令（PowerShell、Linux/macOS 终端）：`./lesson.exe`。按下面列出的标准输入和文件样例准备数据。

**运行前文件：`notes.txt`**

```text
alpha

beta
```

**标准输入**

（无输入）

**预期输出**

```text
3
```

**预期标准错误**

（无输出）

**退出状态**：`0`。


选题关联：来源主题 1（文末列出）。

## 2. 先解析完整记录，再提交一个有效值

第 37 章的整数提取可能只读走数字前缀。记录文件需要更严格的规则：本章每行恰好一个十进制整数，允许前后空白和正负号，但值必须在 0 到 1440；不允许空白行、小数、多余字段或数字后跟字母。sstream 提供 istringstream，把一行字符串当作可读取的流。先读候选 long long，再尝试读第二个非空白字段；第二次成功说明存在多余内容，应该拒绝。数值超出 long long 时第一次读取就失败。

候选值只在所有检查通过后转换为 int 并赋给输出引用。转换时已经证明它在 0 到 1440，因而可以表示。失败时不改 value，让调用者能明确决定如何处理旧结果；这里用 bool 返回成功与否，不以某个分钟值充当失败暗号，因为零分钟本身也是有效数据。程序把五种字符串直接放在范围循环的初值列表中，逐一执行同一个解析函数，不需要终端交互。

第一次带空白的 45 被接受，后面的 45x、两个数字、空字符串和 1441 都被拒绝；每次失败之后 value 仍为 45。观察这个不变性，能抓到“先写入调用者再发现尾部垃圾”的错误。当前使用标准流的默认十进制格式，不声称只接受纯数字字符：例如带加号或前导零的合法整数同样接受。规则应写在题目里，再由反例证明实现是否遵守，而不是从一次运行猜整个语法。

**完整程序（C++17）**

文件：`main.cpp`

```cpp
#include <iostream>
#include <sstream>
#include <string>
bool parse_minutes(const std::string& line, int& value) {
    std::istringstream row{line};
    long long candidate{0};
    std::string extra;
    if (!(row >> candidate) || (row >> extra) || candidate < 0 || candidate > 1440) {
        return false;
    }
    value = static_cast<int>(candidate);
    return true;
}
int main() {
    int value{99};
    for (const std::string line : {" 45 ", "45x", "45 60", "", "1441"}) {
        bool ok{parse_minutes(line, value)};
        std::cout << ok << ' ' << value << '\n';
    }
    return 0;
}
```

**编译**（在本例独立目录内）

```sh
g++ -std=c++17 -Wall -Wextra -Wpedantic -Werror main.cpp -o lesson.exe
```

运行命令（PowerShell、Linux/macOS 终端）：`./lesson.exe`。按下面列出的标准输入和文件样例准备数据。

**标准输入**

（无输入）

**预期输出**

```text
1 45
0 45
0 45
0 45
0 45
```

**预期标准错误**

（无输出）

**退出状态**：`0`。


选题关联：来源主题 1（文末列出）。

## 3. 状态返回与异常：两种失败要接得住

返回 bool 适合预期中的校验失败，调用者在紧接的分支决定继续还是终止。异常则从失败点转移到匹配的处理器，中间普通语句不再执行。下面 mean 对非正样本数抛出 invalid\_argument，调用处用 try 包住可能失败的操作，并用 const 引用捕获该异常；what 提供诊断文本。stdexcept 声明所需异常类型。本例约定 total 的绝对值不超过一百万、正 count 不超过 1000，不把整数转浮点当作精确实数运算。

第一次求 9 除以 3，正常输出 3。第二次样本数为零，在除法前抛出异常，因此不会初始化 second，也不会输出它；控制流进入 catch，向标准错误写 no samples 并返回失败状态。把函数调用与输出分开写，便于看清失败发生前究竟输出了什么。异常从函数传播时，对沿途正常展开的作用域，已构造的自动对象会按规则清理，这与上一章的 RAII 相衔接。

本章文件流保留默认异常设置。打开失败或格式提取失败通常通过状态位体现，不会仅因写了 try 就自动被捕获。因而后面的项目仍显式检查流状态，并用 bool 表示坏记录；这和演示 mean 的异常没有冲突。应选择一种可解释的接口，而不是无差别捕获所有异常后继续当成成功。输出文件写到一半失败时，析构清理文件资源也不能把原文件内容恢复，这又是资源释放与事务恢复的区别。

**完整程序（C++17）**

文件：`main.cpp`

```cpp
#include <iostream>
#include <stdexcept>
double mean(long long total, int count) {
    if (count <= 0) {
        throw std::invalid_argument{"no samples"};
    }
    return static_cast<double>(total) / count;
}
int main() {
    try {
        double first{mean(9, 3)};
        std::cout << first << '\n';
        double second{mean(0, 0)};
        std::cout << second << '\n';
    } catch (const std::invalid_argument& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
    return 0;
}
```

**编译**（在本例独立目录内）

```sh
g++ -std=c++17 -Wall -Wextra -Wpedantic -Werror main.cpp -o lesson.exe
```

运行命令（PowerShell、Linux/macOS 终端）：`./lesson.exe`。按下面列出的标准输入和文件样例准备数据。

**标准输入**

（无输入）

**预期输出**

```text
3
```

**预期标准错误**

```text
no samples
```

**退出状态**：`1`。


选题关联：来源主题 1（文末列出）。

## 4. 多文件接口：声明让调用可检查，定义让链接可完成

当解析、计算和文件操作都挤进 main，修改任何一步都难以独立核对。先用装箱函数练习最小的拆分：units.hpp 放函数声明，units.cpp 包含这个头文件并给出定义，main.cpp 同样包含头文件后调用。双引号包含本项目头文件；标准库仍使用相应头文件。调用者根据声明检查参数和返回类型，链接器再把调用与唯一的函数定义接起来。头文件不是可执行程序，不需要把它单独当作源文件编译。

头文件的条件编译保护由 ifndef、define 和 endif 组成，防止同一翻译单元重复包含同一组声明。它不负责在不同翻译单元之间消除重复函数定义。这里把普通非内联函数的定义只放在一个 cpp 文件中；不要把 units.cpp 又包含到 main.cpp，同时还把它单独编译，那会造成重复定义。实现文件也包含自己的头文件，能让声明与定义之间的不一致更早暴露。

两份 cpp 可以一次交给 g++ 编译链接，也可以先分别生成目标文件，再链接它们。只编译 main.cpp 而漏掉 units.cpp，编译阶段可能通过，链接仍找不到 boxes\_needed。这里继续采用失败不改 result 的接口：先检查件数和容量，再计算商，并把是否有余件转换成补充箱数。bool 参与这里的整数加法时，false 对应零，true 对应一；与上一章显式 if 的结果一致，样例仍得到五箱。

**完整程序（C++17）**

文件：`main.cpp`

```cpp
#include "units.hpp"
#include <iostream>
int main() {
    long long result{0};
    if (!boxes_needed(245, 60, result)) {
        return 1;
    }
    std::cout << result << '\n';
    return 0;
}
```

文件：`units.cpp`

```cpp
#include "units.hpp"
bool boxes_needed(long long items, long long capacity, long long& result) {
    if (items < 0 || items > 1000000 || capacity < 1 || capacity > 1000) {
        return false;
    }
    result = items / capacity + (items % capacity != 0);
    return true;
}
```

文件：`units.hpp`

```cpp
#ifndef STUDY_UNITS_HPP
#define STUDY_UNITS_HPP
bool boxes_needed(long long items, long long capacity, long long& result);
#endif
```

**编译**（在本例独立目录内）

```sh
g++ -std=c++17 -Wall -Wextra -Wpedantic -Werror main.cpp units.cpp -o lesson.exe
```

运行命令（PowerShell、Linux/macOS 终端）：`./lesson.exe`。按下面列出的标准输入和文件样例准备数据。

**标准输入**

（无输入）

**预期输出**

```text
5
```

**预期标准错误**

（无输出）

**退出状态**：`0`。


选题关联：来源主题 2（文末列出）。

## 5. 先写计算契约，再接入真实文件

最终项目的记录是每行一次学习时长，单位分钟，整数范围 0 到 1440，最多 366 行；空文件有效，空白行无效。输出摘要含记录数 count、总分钟 total 和最大单次时长 longest。零条记录的 longest 在内部用零占位，展示时写 NONE，区别于一条零分钟记录。单条上限不等于每日上限，因为本项目没有日期信息，不能把多个记录的和误称为某一天的合法时长。

Summary 把三个有意义的字段放在一起。summarize 接收 std::istream 引用，因此既能读取文件流，也能读取内存字符串流。它在局部 candidate 中逐条处理：已经接受的 count 条记录都是完整合法的，total 是它们的和，longest 是其中最大值；在空状态下保持约定的零。任何坏行、记录过多或读取故障都返回 false，并设置 error，保留调用者的 result。只有正常到达 EOF 且没有 badbit 读取故障，才一次赋值提交完整摘要，并清空旧错误信息。两种状态同时存在时仍返回失败，不能用 EOF 掩盖读取故障。

总分钟不超过 366 乘 1440，即 527040，使用 long long 足够。每行先完整解析再累计，因此不会把 45x 当作 45。行号等于已成功记录数加一，是因为程序在第一个坏行就停止，既没有跳过空行也没有忽略坏行。下面先用内存中的三行数据测试核心，得到 3、95、45，再接真实文件。测试核心不需要复制一份算法；另用纸笔或独立的简单列表统计核对预期，避免实现和测试共享同一个错误。

**完整程序（C++17）**

文件：`main.cpp`

```cpp
#include "summary.hpp"
#include <iostream>
#include <sstream>
int main() {
    std::istringstream input{"30\n45\n20\n"};
    Summary result;
    std::string error;
    if (!summarize(input, result, error)) {
        std::cerr << error << '\n';
        return 1;
    }
    std::cout << result.count << ' ' << result.total << ' ' << result.longest << '\n';
    return 0;
}
```

文件：`summary.cpp`

```cpp
#include "summary.hpp"
#include <sstream>
bool summarize(std::istream& input, Summary& result, std::string& error) {
    Summary candidate;
    std::string line;
    while (std::getline(input, line)) {
        if (candidate.count == 366) {
            error = "too many records";
            return false;
        }
        std::istringstream row{line};
        long long minutes{0};
        std::string extra;
        if (!(row >> minutes) || (row >> extra) || minutes < 0 || minutes > 1440) {
            error = "invalid line " + std::to_string(candidate.count + 1);
            return false;
        }
        ++candidate.count;
        candidate.total += minutes;
        if (minutes > candidate.longest) {
            candidate.longest = static_cast<int>(minutes);
        }
    }
    if (input.bad() || !input.eof()) {
        error = "read error";
        return false;
    }
    result = candidate;
    error.clear();
    return true;
}
```

文件：`summary.hpp`

```cpp
#ifndef STUDY_SUMMARY_HPP
#define STUDY_SUMMARY_HPP
#include <istream>
#include <string>
struct Summary {
    int count{0};
    long long total{0};
    int longest{0};
};
bool summarize(std::istream& input, Summary& result, std::string& error);
#endif
```

**编译**（在本例独立目录内）

```sh
g++ -std=c++17 -Wall -Wextra -Wpedantic -Werror main.cpp summary.cpp -o lesson.exe
```

运行命令（PowerShell、Linux/macOS 终端）：`./lesson.exe`。按下面列出的标准输入和文件样例准备数据。

**标准输入**

（无输入）

**预期输出**

```text
3 95 45
```

**预期标准错误**

（无输出）

**退出状态**：`0`。


选题关联：来源主题 2（文末列出）。

<a id="examples"></a>

## 跟着做：原创例题

### 例题 1

完成学习时长汇总工具：从当前目录的 sessions.txt 读取每行一个分钟整数，采用本章 0 到 1440、最多 366 行、空文件有效的契约。成功写 report.txt，标准输出 saved。样例文件依次为 30、45、20。

1. 先打开输入文件并检查；打不开返回 1，尚未打开输出文件。
2. 调用同一 summarize 核心，逐行接受三条记录，总和 95，最长 45；坏记录或读取失败返回 2。
3. 只有整个输入通过后才打开 report.txt；默认输出方式会截断已有内容。
4. 依次写 count、total、longest，显式关闭并检查写出状态；输出打开或写出失败返回 3，全部成功才打印 saved。

**结果与核对**

report.txt 的三行分别是 count 3、total 95、longest 45，程序成功返回 0。总和用 30 加 45 加 20 独立核对。空文件仍创建报告，记录数与总量为零，longest 为 NONE。打开输入或解析失败会保留原报告；但一旦开始打开并写输出，后续磁盘错误可能留下截断或部分内容，本例没有实现原子替换。

**完整程序（C++17）**

文件：`main.cpp`

```cpp
#include "summary.hpp"
#include <fstream>
#include <iostream>
int main() {
    std::ifstream input{"sessions.txt"};
    if (!input) {
        std::cerr << "cannot open input\n";
        return 1;
    }
    Summary result;
    std::string error;
    if (!summarize(input, result, error)) {
        std::cerr << error << '\n';
        return 2;
    }
    std::ofstream output{"report.txt"};
    if (!output) {
        std::cerr << "cannot open output\n";
        return 3;
    }
    output << "count " << result.count << '\n'
           << "total " << result.total << '\n' << "longest ";
    if (result.count == 0) {
        output << "NONE\n";
    } else {
        output << result.longest << '\n';
    }
    output.close();
    if (!output) {
        std::cerr << "write error\n";
        return 3;
    }
    std::cout << "saved\n";
    return 0;
}
```

文件：`summary.cpp`

```cpp
#include "summary.hpp"
#include <sstream>
bool summarize(std::istream& input, Summary& result, std::string& error) {
    Summary candidate;
    std::string line;
    while (std::getline(input, line)) {
        if (candidate.count == 366) {
            error = "too many records";
            return false;
        }
        std::istringstream row{line};
        long long minutes{0};
        std::string extra;
        if (!(row >> minutes) || (row >> extra) || minutes < 0 || minutes > 1440) {
            error = "invalid line " + std::to_string(candidate.count + 1);
            return false;
        }
        ++candidate.count;
        candidate.total += minutes;
        if (minutes > candidate.longest) {
            candidate.longest = static_cast<int>(minutes);
        }
    }
    if (input.bad() || !input.eof()) {
        error = "read error";
        return false;
    }
    result = candidate;
    error.clear();
    return true;
}
```

文件：`summary.hpp`

```cpp
#ifndef STUDY_SUMMARY_HPP
#define STUDY_SUMMARY_HPP
#include <istream>
#include <string>
struct Summary {
    int count{0};
    long long total{0};
    int longest{0};
};
bool summarize(std::istream& input, Summary& result, std::string& error);
#endif
```

**编译**（在本例独立目录内）

```sh
g++ -std=c++17 -Wall -Wextra -Wpedantic -Werror main.cpp summary.cpp -o lesson.exe
```

运行命令（PowerShell、Linux/macOS 终端）：`./lesson.exe`。按下面列出的标准输入和文件样例准备数据。

**运行前文件：`sessions.txt`**

```text
30
45
20
```

**标准输入**

（无输入）

**预期输出**

```text
saved
```

**预期标准错误**

（无输出）

**退出状态**：`0`。

**运行后文件：`report.txt`**

```text
count 3
total 95
longest 45
```


### 例题 2

复用同一个三文件项目，输入文件改为 30、45x、20 三行，运行前已有 report.txt，内容为 previous report。预测标准输出、标准错误、退出状态和报告是否改变。

1. 第一行被接受，局部候选摘要暂时为一条、30 分钟。
2. 第二行数字提取得到 45，但额外读取发现 x，判为第二行非法。
3. summarize 返回失败，调用者输出 invalid line 2 并返回 2。
4. 第三行不再处理，输出文件尚未打开，因此旧报告内容保持原样。

**结果与核对**

标准输出为空，标准错误为 invalid line 2，退出状态为 2，report.txt 仍是 previous report。只检查错误文字不够，还必须读取原报告确认没有提前截断。把坏行分别改成空白、两个数字、负 1 或 1441，也应按第一处失败行号拒绝；再把整个输入文件删除，得到的是打开失败而非空摘要。

**完整程序（C++17）**

文件：`main.cpp`

```cpp
#include "summary.hpp"
#include <fstream>
#include <iostream>
int main() {
    std::ifstream input{"sessions.txt"};
    if (!input) {
        std::cerr << "cannot open input\n";
        return 1;
    }
    Summary result;
    std::string error;
    if (!summarize(input, result, error)) {
        std::cerr << error << '\n';
        return 2;
    }
    std::ofstream output{"report.txt"};
    if (!output) {
        std::cerr << "cannot open output\n";
        return 3;
    }
    output << "count " << result.count << '\n'
           << "total " << result.total << '\n' << "longest ";
    if (result.count == 0) {
        output << "NONE\n";
    } else {
        output << result.longest << '\n';
    }
    output.close();
    if (!output) {
        std::cerr << "write error\n";
        return 3;
    }
    std::cout << "saved\n";
    return 0;
}
```

文件：`summary.cpp`

```cpp
#include "summary.hpp"
#include <sstream>
bool summarize(std::istream& input, Summary& result, std::string& error) {
    Summary candidate;
    std::string line;
    while (std::getline(input, line)) {
        if (candidate.count == 366) {
            error = "too many records";
            return false;
        }
        std::istringstream row{line};
        long long minutes{0};
        std::string extra;
        if (!(row >> minutes) || (row >> extra) || minutes < 0 || minutes > 1440) {
            error = "invalid line " + std::to_string(candidate.count + 1);
            return false;
        }
        ++candidate.count;
        candidate.total += minutes;
        if (minutes > candidate.longest) {
            candidate.longest = static_cast<int>(minutes);
        }
    }
    if (input.bad() || !input.eof()) {
        error = "read error";
        return false;
    }
    result = candidate;
    error.clear();
    return true;
}
```

文件：`summary.hpp`

```cpp
#ifndef STUDY_SUMMARY_HPP
#define STUDY_SUMMARY_HPP
#include <istream>
#include <string>
struct Summary {
    int count{0};
    long long total{0};
    int longest{0};
};
bool summarize(std::istream& input, Summary& result, std::string& error);
#endif
```

**编译**（在本例独立目录内）

```sh
g++ -std=c++17 -Wall -Wextra -Wpedantic -Werror main.cpp summary.cpp -o lesson.exe
```

运行命令（PowerShell、Linux/macOS 终端）：`./lesson.exe`。按下面列出的标准输入和文件样例准备数据。

**运行前文件：`report.txt`**

```text
previous report
```

**运行前文件：`sessions.txt`**

```text
30
45x
20
```

**标准输入**

（无输入）

**预期输出**

（无输出）

**预期标准错误**

```text
invalid line 2
```

**退出状态**：`2`。

**运行后文件：`report.txt`**

```text
previous report
```


<a id="practice"></a>

## 自己做：先完成再看解答

### 练习 1

另写一个宽容汇总器，从标准输入逐行读到 EOF，最多 366 行。每行仍须恰好一个 0 到 1440 的整数；坏行不终止而计入 rejected，合法行计入 accepted 并求总和。空白行算坏行。样例四行为 30、wrong、负 1、0。

<details>
<summary>提示</summary>

把每一行放进独立的字符串流；坏行只影响自己的流状态，外层输入流仍能读取下一行。

</details>

<details>
<summary>解答与检查</summary>

接受 30 与 0 两行，得到 accepted 为 2、总分钟 30、rejected 为 2。必须单独统计总行数以执行 366 行上限，不能只用合法行数限制文件。读取故障或超出上限仍失败且不输出最终摘要。逐行重建流避免在失败的同一个数字提取流里无限重试。这个接口有意区别于严格项目，报告时必须同时给出拒绝数，不能把部分数据伪装成完整合法输入。

**完整程序（C++17）**

文件：`main.cpp`

```cpp
#include <iostream>
#include <sstream>
#include <string>
int main() {
    int lines{0};
    int accepted{0};
    int rejected{0};
    long long total{0};
    std::string line;
    while (std::getline(std::cin, line)) {
        if (lines == 366) {
            std::cerr << "too many records\n";
            return 1;
        }
        ++lines;
        std::istringstream row{line};
        long long minutes{0};
        std::string extra;
        if (!(row >> minutes) || (row >> extra) || minutes < 0 || minutes > 1440) {
            ++rejected;
            continue;
        }
        ++accepted;
        total += minutes;
    }
    if (std::cin.bad() || !std::cin.eof()) {
        std::cerr << "read error\n";
        return 1;
    }
    std::cout << accepted << ' ' << total << ' ' << rejected << '\n';
    return 0;
}
```

**编译**（在本例独立目录内）

```sh
g++ -std=c++17 -Wall -Wextra -Wpedantic -Werror main.cpp -o lesson.exe
```

运行命令（PowerShell、Linux/macOS 终端）：`./lesson.exe`。按下面列出的标准输入和文件样例准备数据。

**标准输入**

```text
30
wrong
-1
0
```

**预期输出**

```text
2 30 2
```

**预期标准错误**

（无输出）

**退出状态**：`0`。


</details>

### 练习 2

为两个有效 Summary 编写 merge，合并计数、总分钟和最大值。两个输入都由本章严格核心产生，空摘要为三个零；若合并后超过 366 条，返回 false 且结果不变。允许 result 与任一输入是同一个对象。用 2 条共 75 分最长 45，合并 1 条 20 分。

<details>
<summary>提示</summary>

先检查计数是否能合并，在新的局部摘要里完成所有读取和计算，最后再写结果。

</details>

<details>
<summary>解答与检查</summary>

结果为 3 条、95 分、最长 45。用 366 减右侧计数作比较，输入已满足有效摘要前置条件，因此减法安全。局部 candidate 避免在结果与左侧或右侧别名时过早覆盖后续还要读取的字段。空摘要是合并的单位元素；样例第二次合并验证这一点。超过 366 条时必须比较原 result 的三个字段都保持不变。函数不负责修复手工伪造的不一致摘要。

**完整程序（C++17）**

文件：`main.cpp`

```cpp
#include <iostream>
struct Summary {
    int count{0};
    long long total{0};
    int longest{0};
};
bool merge(const Summary& left, const Summary& right, Summary& result) {
    if (left.count > 366 - right.count) {
        return false;
    }
    Summary candidate;
    candidate.count = left.count + right.count;
    candidate.total = left.total + right.total;
    candidate.longest = left.longest;
    if (right.longest > candidate.longest) {
        candidate.longest = right.longest;
    }
    result = candidate;
    return true;
}
int main() {
    Summary first{2, 75, 45};
    const Summary second{1, 20, 20};
    bool ok{merge(first, second, first)};
    std::cout << ok << ' ' << first.count << ' ' << first.total << ' ' << first.longest << '\n';
    Summary empty;
    Summary result;
    bool copied{merge(empty, first, result)};
    std::cout << copied << ' ' << result.count << ' ' << result.total << ' ' << result.longest << '\n';
    return 0;
}
```

**编译**（在本例独立目录内）

```sh
g++ -std=c++17 -Wall -Wextra -Wpedantic -Werror main.cpp -o lesson.exe
```

运行命令（PowerShell、Linux/macOS 终端）：`./lesson.exe`。按下面列出的标准输入和文件样例准备数据。

**标准输入**

（无输入）

**预期输出**

```text
1 3 95 45
1 3 95 45
```

**预期标准错误**

（无输出）

**退出状态**：`0`。


</details>

### 练习 3

完成另一个独立小项目：week.txt 每行有两个十进制整数字段，日编号和学习分钟之间至少有一个空白字符（例如空格或制表符）。数字可带正负号，按数值检查范围。日编号为 1 到 7，分钟为 0 到 1440；最多 366 行，同一天可多次出现，但累计不得超过 1440。拒绝空白行、多余字段及非法数值。全部合法后才写 weekly\_report.txt，固定七行，分别为日编号和总分钟；标准输出总分钟。样例是 1 30、2 45、1 20。

<details>
<summary>提示</summary>

用七项 std::array 保存各日总量，先检查日编号再减一作下标；相加前用剩余额度检查，全部读取完成后才打开输出。

</details>

<details>
<summary>解答与检查</summary>

先按空白读出一个完整的字段，再把它单独当作整数解析。1 +30 有两个字段，表示第一天 30 分钟。1+30 只有一个字段，转换整数后还剩加号和数字，应当拒绝。样例第一天为 50，第二天为 45，其余五天为零，总计 95。std::array 的模板参数给出元素类型和固定长度，空花括号使各项初始化为零；size 提供长度，普通下标仍不检查边界。输入为空也应生成七个零。失败发生在输入打开时返回 1，校验或读入时返回 2，输出打开或写入时返回 3；前两类保留旧报告。逐日上限使全周总量至多 10080，int 足够。已有输出在写出阶段仍可能受磁盘故障影响，和例题一样未实现原子替换。

**完整程序（C++17）**

文件：`main.cpp`

```cpp
#include <array>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
bool read_integer_field(std::istream& row, int& value) {
    std::string field;
    if (!(row >> field)) {
        return false;
    }
    std::istringstream number{field};
    int candidate{0};
    char trailing{};
    if (!(number >> candidate) || (number >> trailing)) {
        return false;
    }
    value = candidate;
    return true;
}

int main() {
    std::ifstream input{"week.txt"};
    if (!input) {
        std::cerr << "cannot open input\n";
        return 1;
    }
    std::array<int, 7> minutes{};
    std::string line;
    int lines{0};
    while (std::getline(input, line)) {
        if (lines == 366) {
            std::cerr << "too many records\n";
            return 2;
        }
        ++lines;
        std::istringstream row{line};
        int day{0};
        int value{0};
        std::string extra;
        if (!read_integer_field(row, day) || !read_integer_field(row, value)
            || (row >> extra) || day < 1 || day > 7
            || value < 0 || value > 1440) {
            std::cerr << "invalid line " << lines << '\n';
            return 2;
        }
        auto index{static_cast<std::size_t>(day - 1)};
        if (value > 1440 - minutes[index]) {
            std::cerr << "daily limit at line " << lines << '\n';
            return 2;
        }
        minutes[index] += value;
    }
    if (input.bad() || !input.eof()) {
        std::cerr << "read error\n";
        return 2;
    }
    std::ofstream output{"weekly_report.txt"};
    if (!output) {
        std::cerr << "cannot open output\n";
        return 3;
    }
    int total{0};
    for (std::size_t i{0}; i < minutes.size(); ++i) {
        output << i + 1 << ' ' << minutes[i] << '\n';
        total += minutes[i];
    }
    output.close();
    if (!output) {
        std::cerr << "write error\n";
        return 3;
    }
    std::cout << "total " << total << '\n';
    return 0;
}
```

**编译**（在本例独立目录内）

```sh
g++ -std=c++17 -Wall -Wextra -Wpedantic -Werror main.cpp -o lesson.exe
```

运行命令（PowerShell、Linux/macOS 终端）：`./lesson.exe`。按下面列出的标准输入和文件样例准备数据。

**运行前文件：`week.txt`**

```text
1 30
2 45
1 20
```

**标准输入**

（无输入）

**预期输出**

```text
total 95
```

**预期标准错误**

（无输出）

**退出状态**：`0`。

**运行后文件：`weekly_report.txt`**

```text
1 50
2 45
3 0
4 0
5 0
6 0
7 0
```


</details>

<a id="pitfalls"></a>

## 容易混淆的地方

- **用还没到 EOF 作为读取循环条件。** 应让 getline 的成功与否决定是否处理本轮，循环结束后再区分正常 EOF 和读取错误，末行无换行也应接受。
- **一开始就打开输出文件，认为失败时反正没有写内容。** 默认输出打开可能已经截断原文件；严格项目先验证整个输入，再打开输出，仍需说明写出失败不能回滚。
- **认为引入头文件就会自动把实现文件链接进来。** 头文件提供声明，构建命令仍要编译和链接实现文件；本章测试分别验证正常链接与漏实现时的失败。
- **把捕获异常当作所有输入错误的统一修复。** 默认流操作通常用状态报告失败；解析规则、异常传播和报告文件保护分别需要明确的控制流。

<a id="self-check"></a>

## 离开这一章前

- [ ] 给出空文件、单个空行、末行无换行的不同预期，并逐一运行。
- [ ] 让坏行出现在第二行，核对行号、退出状态、调用者摘要和旧报告内容。
- [ ] 分别按一次编译和分步编译链接两个方式构建多文件例子；解释漏掉实现文件时的诊断阶段。
- [ ] 比较严格汇总器与宽容汇总器，说明各自报告是否代表全部输入。
- [ ] 用直接列表求和与七天数组作为独立参照，核对上限、重复日期和生成文件。

## 本章边界

- 小项目处理本地小型文本记录，文件名固定；未实现命令行参数、编码探测、流式超长行限制或通用 CSV 解析。
- 写出失败可能留下部分报告；原子替换、并发访问、持久化保证与更完整的异常安全另列为后续工程内容。
- 本章按原程序设计基础课程补语言与工程单元，未覆盖整个面向对象课程、构建系统、包管理或大型项目测试。

## 选题来源与覆盖

来源含学生报告时，仅将其作为选题线索；具体机制仍需结合后续实验或权威资料核对。

- [大一上/程序设计基础/hw/编程手记/C++札记.docx](https://github.com/PKUanonym/REKCARC-TSC-UHT/blob/37cd19f7a9fb80dc846a7016b3fd482ed5fe7cc0/%E5%A4%A7%E4%B8%80%E4%B8%8A/%E7%A8%8B%E5%BA%8F%E8%AE%BE%E8%AE%A1%E5%9F%BA%E7%A1%80/hw/%E7%BC%96%E7%A8%8B%E6%89%8B%E8%AE%B0/C%2B%2B%E6%9C%AD%E8%AE%B0.docx)（已提取可读文本，固定版本 37cd19f7a9fb）
- 主题 1：C++ 编译诊断、初始化、输入输出与控制流的学习问题；位置：Word 正文。
- 主题 2：函数声明与参数传递、数组范围、指针及动态资源的学习问题；位置：Word 正文。

## 参考资料与规则核对

上游入口用于确定学习方向；下面的参考资料用于核对语言语义、数据结构或算法分析规则，例题和练习由本项目重新设计。

- [GCC：编译阶段与输出选项](https://gcc.gnu.org/onlinedocs/gcc/Overall-Options.html)：核对预处理、编译、汇编、链接及 -c 的含义；具体演示为本项目原创并实际构建。
- [C++17 草案 N4659：string.io](https://timsong-cpp.github.io/cppwp/n4659/string.io)：核对 getline、空行、末行和 EOF 语义；分钟记录格式及测试数据为原创。
- [C++17 草案 N4659：istream.formatted.arithmetic](https://timsong-cpp.github.io/cppwp/n4659/istream.formatted.arithmetic)：核对数值提取失败和范围处理，额外字段由项目主动检测。
- [C++17 草案 N4659：filebuf.members](https://timsong-cpp.github.io/cppwp/n4659/filebuf.members)：核对文件打开、截断与关闭行为；说明本项目不提供原子替换。
- [C++17 草案 N4659：basic.def.odr](https://timsong-cpp.github.io/cppwp/n4659/basic.def.odr)：核对声明、定义与翻译单元的关系，多文件示例仅使用普通非内联函数。
- [C++17 草案 N4659：except.ctor](https://timsong-cpp.github.io/cppwp/n4659/except.ctor)：核对异常传播和自动对象清理，普通文件流仍按默认状态位方式检查失败。

**继续学习**：先独立完成自测，再记录仍需回读的步骤。

[上一章：函数与对象的生命周期：C++ 值、引用和指针](38-cpp-functions-lifetime.md)

[教材目录](index.md) · [C++ 练习与编译](../cpp-programming-practice.md) · [记录自己的学习](../learning-log-template.md)
