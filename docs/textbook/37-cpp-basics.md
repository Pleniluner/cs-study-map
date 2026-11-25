# 从源码到运行：C++ 类型、输入输出与控制流

[返回教材目录](index.md) · [C++ 练习与编译](../cpp-programming-practice.md)

[上一章：合并区间摘要：线段树与延迟更新](36-segment-tree.md) · [下一章：函数与对象的生命周期：C++ 值、引用和指针](38-cpp-functions-lifetime.md)

[学习目标](#objectives) · [需要的基础](#prerequisites) · [例题](#examples) · [练习](#practice) · [自测](#self-check)

状态：**AI 初稿，可开始试学**。生成模型：Codex 当前会话（未记录具体模型型号）。

本章围绕资料中识别到的知识点重新编写；讲解、数值模型、例题与练习为 AI 原创组织，不是原课程题目或答案。主题出处只说明选题关联，不证明全部推导已经正确。

这一章属于程序设计基础的 C++ 单元，先把“编辑器里的文字怎样成为可运行程序”说明白，再把已经学过的分支与循环落实到 C++17。你将亲自保存源文件、编译、输入数据，并分别核对结果和退出状态。沿途要区分编译错误、输入错误和算法错误：能生成可执行文件只完成了第一关。例子从固定输出走到有范围约束的数据汇总，练习再要求你解释运算类型、零输入和循环停止条件；无需先读完前面的全部算法章节。

<a id="objectives"></a>

## 学完要能做到

- 说明源码、目标文件与可执行文件的区别，独立使用 C++17 编译命令。
- 根据操作数类型预测整数除法、余数、显式转换和输出格式。
- 在使用输入值前检查读取和范围；分别核对标准输出、标准错误与退出状态。
- 把有界循环写成 C++，并证明空输入、最后一次迭代和计数边界的处理。

<a id="prerequisites"></a>

## 需要的基础

- 初等整数和小数运算，能理解正数、负数与余数。
- 第 4、5 章的顺序、分支、循环和函数概念可作预习；本章会解释所用 C++ 语法。
- 准备支持 C++17 的编译器，具体保存、编译与运行步骤见本章顶部的练习指引。

## 1. 从源文件到进程：编译成功还要运行核对

把程序保存为 main.cpp 时，磁盘上存的是文本。以 GCC 为例，预处理处理头文件等指令，编译把语言结构翻译为较低层表示，汇编生成目标文件，链接再把目标文件和所需库连接成可执行文件。常用的 g++ 命令可以连续完成这些步骤；加 -c 则停在目标文件。运行可执行文件是另一次操作，操作系统才会启动进程。不要把编辑器能显示颜色理解为已经编译，也不要在编译失败后误运行上次留下的旧文件。

#include 指示引入声明；iostream 提供本例使用的标准流接口。int main() 是这里的程序入口，括号表示参数列表，大括号包住函数体，语句末尾用分号。std 是标准库所在的命名空间，双冒号限定名字；直接写 std::cout 能清楚说明名字来源。输出运算符把右边内容送入流，字符串用双引号，反斜杠 n 表示换行字符。return 0 把成功状态交给宿主环境，屏幕上的 ready 才是标准输出，二者用途不同。

本书固定使用 C++17，并启用常见警告和把警告当作错误的检查选项。警告规则取决于编译器；这些选项有助于暴露问题，却不能证明所有运行路径正确。故意漏掉分号属于编译诊断；调用了一个只有声明、没有链接定义的普通函数，会在链接阶段遇到问题；把加法写成减法通常仍能编译，是逻辑问题。本例应输出一行 ready 并成功退出，下一步才有稳定基线可比较。

**完整程序（C++17）**

文件：`main.cpp`

```cpp
#include <iostream>
int main() {
    std::cout << "ready\n";
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
ready
```

**预期标准错误**

（无输出）

**退出状态**：`0`。


选题关联：来源主题 1（文末列出）。

## 2. 类型、初始化与范围：每个值都要有解释

变量声明同时给出类型和名字。int 适合本例的小整数，long long 用来保存更大的整数，double 保存浮点近似值，char 保存一个字符，bool 表示真假。下面用花括号初始化，强调值从哪里来；例如把 3.5 直接放入 int 的花括号初始化会因窄化而被拒绝。const 表示通过这个名字不能再修改该对象，适合单价等约定。char 的单引号与字符串的双引号不能随意互换。

C++ 不保证所有机器上的 int 都是 32 位。标准保证 int 至少有相应的 16 位取值能力，long long 至少有相应的 64 位取值能力；真正的上限应从实现或 numeric\_limits 查询。本书小计数限制到 1000，大金额或累计量使用 long long，并先根据输入范围算出最大结果。有符号整数算术超出可表示范围是未定义行为，不能把一次机器上的回绕结果当成语言规则。未初始化的普通局部整数也不能随意读取；统一显式初始化能让初始状态可追踪。

本例 7 份商品、每份 125 分，总额为 875 分。乘法的一方是 long long，所以先以相应的整数运算求值，再保存到 total。货币按整数分处理，避免把浮点误差带入精确金额。ratio 使用小数操作数得到 3.5；bool 的默认流输出为 1 或 0。这里四项输出依次说明金额、比值、等级和是否在预算内，先把它们算在纸上再运行。

**完整程序（C++17）**

文件：`main.cpp`

```cpp
#include <iostream>
int main() {
    int count{7};
    const long long price_cents{125};
    long long total{count * price_cents};
    double ratio{7.0 / 2.0};
    char grade{'A'};
    bool affordable{total <= 1000};
    std::cout << total << ' ' << ratio << ' ' << grade << ' ' << affordable << '\n';
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
875 3.5 A 1
```

**预期标准错误**

（无输出）

**退出状态**：`0`。


选题关联：来源主题 1（文末列出）。

## 3. 表达式先计算，赋值不会补回丢掉的小数

表达式的类型由操作数和运算规则决定，保存结果的变量不会倒过来改变已经完成的计算。两个整数相除仍做整数除法；7 除以 2 得到 3，即使随后赋给 double 也只是 3.0。要得到 3.5，可以在除法之前把一个操作数用 static\_cast 转成 double。这里的转换语法把目标类型写在尖括号中，括号内是原表达式；先转换再除法，另一方也按浮点运算处理。不要把“打印两位小数”误认为“改为浮点运算”。

C++17 的有符号整数除法向零截断，因此负 7 除以 3 得负 2，余数为负 1；满足被除数等于商乘除数加余数。判断偶数只需余数是否为零，不能把“奇数余数必须为 1”套到负数上。除数为零必须在求值前排除；本章固定或校验正除数，避免执行无效计算。运算符优先级并不等于你心里希望的顺序，括号能把意图写清楚。

同样，先用 int 做大乘法再赋给 long long 也来不及避免溢出。下面 70000 的字面量带 LL 后缀，使乘法在 long long 范围内完成，得到 4900000000。std::fixed 选用定点格式，再用头文件 iomanip 提供的 std::setprecision 指定小数点后的位数；它们改变流的格式状态，不改变已存的数值。多数十进制小数不能被二进制浮点精确表示，本章只使用易核对的显示结果，不把格式化输出当作精确实数证明。

**完整程序（C++17）**

文件：`main.cpp`

```cpp
#include <iomanip>
#include <iostream>
int main() {
    int total{7};
    int count{2};
    double average{static_cast<double>(total) / count};
    long long square{70000LL * 70000LL};
    std::cout << total / count << ' ' << -7 / 3 << ' ' << -7 % 3 << '\n';
    std::cout << std::fixed << std::setprecision(2) << average << '\n';
    std::cout << square << '\n';
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
3 -2 -1
3.50
4900000000
```

**预期标准错误**

（无输出）

**退出状态**：`0`。


选题关联：来源主题 1（文末列出）。

## 4. 输入也是一个可能失败的操作

std::cin 的提取运算符尝试把标准输入读成指定类型。它通常跳过前导空白；读取可能因没有数据、遇到不合适的字符或数值超出类型范围而失败。把整个读取表达式放进条件，检查其流状态后再使用变量。感叹号表示逻辑非，双竖线表示“或”且从左往右短路：一旦前面已经确定失败，就不再计算后面的条件。这里把读取失败、负秒数和超过一天统一处理为 INVALID。

程序有三种独立可观察结果：标准输出放成功的计算结果，标准错误放本例的诊断信息，退出状态区分成功与失败。终端常把两条流显示在一起；自动检查时仍应分别比较。本书约定本例失败返回 1，成功返回 0；这两个具体状态在本次 GCC 的 Windows 与 Linux 验收环境中检查。读取失败以后，流通常保持失败状态，不能不作处理就反复读取并期待恢复；最初的程序可以直接结束，后面再学习逐行解析。

本例只消费所需的一个整数，不宣称校验整份输入格式。比如数字后紧接其他字符，整数提取可能先接受数字前缀，余下字符仍在流里。第 39 章会用整行解析拒绝多余字段。本章的有效输入按题目要求只提供指定整数和空白。3661 秒拆成 1 小时、1 分钟、1 秒；0 和 86400 都允许，后者输出 24 小时而不是自动归到下一天。

**完整程序（C++17）**

文件：`main.cpp`

```cpp
#include <iostream>
int main() {
    long long seconds{0};
    if (!(std::cin >> seconds) || seconds < 0 || seconds > 86400) {
        std::cerr << "INVALID\n";
        return 1;
    }
    std::cout << seconds / 3600 << ' ' << seconds % 3600 / 60
              << ' ' << seconds % 60 << '\n';
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
3661
```

**预期输出**

```text
1 1 1
```

**预期标准错误**

（无输出）

**退出状态**：`0`。


选题关联：来源主题 1（文末列出）。

## 5. 用循环不变量约束状态的每一次变化

C++ 的 if 在条件为真时执行语句块，else 处理另一分支。for 的三个部分依次是初始化、继续条件和每轮后的更新；这里 ++i 表示把计数加一。先令 i 为 0，只在 i 小于 n 时读一项，每成功处理一项才前进，因此恰好读 n 项。while 则把初始化与更新放在循环外和循环体中，使用时必须主动检查有没有遗漏前进步骤。赋值用单等号，相等判断用双等号；把赋值误写进条件往往不是语法错误。

这段汇总程序的不变量是：每轮开始时，已处理的正好是前 i 项，sum 等于这些项的和，positive 等于其中严格为正的项数。先校验新值，再同时更新这两个摘要，最后前进到下一项。第 n 项处理完，i 等于 n，循环停止。n 为 0 时循环一次也不执行，初始的两个零就是正确结果。零值没有正性，所以不增加 positive。

输入项数限制为 0 到 1000，每项限制为负 1000 到 1000。累计和的绝对值不超过一百万，long long 能容纳；正数个数不超过 1000，int 足够。任一项缺失或不合法时，程序在输出摘要前退出，不把已算的一部分冒充完整结果。输入结束后多余内容本例不消费。运行样例时，依次得到和负 2、1、1、5、4；正数来自 3 与 4，因此最终输出 4 和 2。

**完整程序（C++17）**

文件：`main.cpp`

```cpp
#include <iostream>
int main() {
    int n{0};
    if (!(std::cin >> n) || n < 0 || n > 1000) {
        std::cerr << "INVALID\n";
        return 1;
    }
    long long sum{0};
    int positive{0};
    for (int i{0}; i < n; ++i) {
        int value{0};
        if (!(std::cin >> value) || value < -1000 || value > 1000) {
            std::cerr << "INVALID\n";
            return 1;
        }
        sum += value;
        if (value > 0) {
            ++positive;
        }
    }
    std::cout << sum << ' ' << positive << '\n';
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
5
-2 3 0 4 -1
```

**预期输出**

```text
4 2
```

**预期标准错误**

（无输出）

**退出状态**：`0`。


选题关联：来源主题 1（文末列出）。

<a id="examples"></a>

## 跟着做：原创例题

### 例题 1

把 245 件材料装入每箱 60 件的箱子。输入件数与容量，件数允许 0 到 1000000，容量允许 1 到 1000；输出满箱数、余件数与所需总箱数。非法输入诊断 INVALID，返回 1。

1. 先按容量作整数除法，245 除以 60 的商为 4。
2. 余数为 5，核对 4 乘 60 加 5 恰好等于 245。
3. 有余件才追加一个箱子，得到总箱数 5；整除时不能多加。
4. 零件数使商和余数都为零；容量为零必须在除法之前拒绝。

**结果与核对**

输出 4、5、5。最后一箱虽然没有装满，也算一个箱子。选择先除再按余数补一，避免习惯性使用“件数加容量减一”而忽略中间加法的范围。用总箱容量不小于件数且少一个箱子装不下反向检查；零件数单独核对为零箱。

**完整程序（C++17）**

文件：`main.cpp`

```cpp
#include <iostream>
int main() {
    long long items{0};
    long long capacity{0};
    if (!(std::cin >> items >> capacity) || items < 0 || items > 1000000
        || capacity < 1 || capacity > 1000) {
        std::cerr << "INVALID\n";
        return 1;
    }
    long long full{items / capacity};
    long long remaining{items % capacity};
    long long boxes{full};
    if (remaining != 0) {
        ++boxes;
    }
    std::cout << full << ' ' << remaining << ' ' << boxes << '\n';
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
245 60
```

**预期输出**

```text
4 5 5
```

**预期标准错误**

（无输出）

**退出状态**：`0`。


### 例题 2

读入项数 n 和 n 个整数，求平均值并保留两位小数。n 为 0 到 1000，各值为负 1000 到 1000；空组输出 EMPTY，非法或缺失数据输出诊断 INVALID 并失败。样例为 4 项：负 2、3、4、0。

1. 定义已处理项数 i 和累计和 sum，都从零开始。
2. while 每轮先读一项并校验，再加进 sum，最后把 i 加一。
3. 四项和为 5；先转成 double 再除以 4，得到 1.25。
4. 把 n 等于零的情形放在除法之前处理，避免把空组平均数伪造为零。

**结果与核对**

输出 1.25。n 等于 0 时应输出 EMPTY，这与四项全为零时输出 0.00 不同：前者没有样本，后者有样本且平均为零。循环计数每次只增加一，最多执行 n 次；任何中途失败都没有成功摘要输出。

**完整程序（C++17）**

文件：`main.cpp`

```cpp
#include <iomanip>
#include <iostream>
int main() {
    int n{0};
    if (!(std::cin >> n) || n < 0 || n > 1000) {
        std::cerr << "INVALID\n";
        return 1;
    }
    long long sum{0};
    int i{0};
    while (i < n) {
        int value{0};
        if (!(std::cin >> value) || value < -1000 || value > 1000) {
            std::cerr << "INVALID\n";
            return 1;
        }
        sum += value;
        ++i;
    }
    if (n == 0) {
        std::cout << "EMPTY\n";
    } else {
        std::cout << std::fixed << std::setprecision(2)
                  << static_cast<double>(sum) / n << '\n';
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

```text
4
-2 3 4 0
```

**预期输出**

```text
1.25
```

**预期标准错误**

（无输出）

**退出状态**：`0`。


<a id="practice"></a>

## 自己做：先完成再看解答

### 练习 1

输入整数摄氏温度，范围为负 100 到 100，按华氏温度等于摄氏温度乘九除五加三十二换算，显示一位小数。样例输入负 40。非法输入诊断 INVALID，返回 1。

<details>
<summary>提示</summary>

先检查九除五在代码中究竟是整数还是浮点运算，再考虑显示格式。

</details>

<details>
<summary>解答与检查</summary>

用 9.0 除以 5.0 得到浮点比例；先求 9 除以 5 的整数商再转换会永远丢掉 0.8。负 40 对应负 40.0，0 对应 32.0，100 对应 212.0，分别检查负数、偏移量与上边界。输入约定只给一个整数与空白，成功返回 0。

**完整程序（C++17）**

文件：`main.cpp`

```cpp
#include <iomanip>
#include <iostream>
int main() {
    int celsius{0};
    if (!(std::cin >> celsius) || celsius < -100 || celsius > 100) {
        std::cerr << "INVALID\n";
        return 1;
    }
    double fahrenheit{celsius * (9.0 / 5.0) + 32.0};
    std::cout << std::fixed << std::setprecision(1) << fahrenheit << '\n';
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
-40
```

**预期输出**

```text
-40.0
```

**预期标准错误**

（无输出）

**退出状态**：`0`。


</details>

### 练习 2

输入负 1000 到 1000 的一个整数，先输出 negative、zero 或 positive，再输出 even 或 odd，中间一个空格。零算偶数；样例为负 7。输入失败或越界时按 INVALID 失败。

<details>
<summary>提示</summary>

先用互斥的三分支决定符号，再独立用除以二的余数是否为零决定奇偶。

</details>

<details>
<summary>解答与检查</summary>

负 7 的余数为负 1，但仍是奇数，应输出 negative odd。零进入单独分支，输出 zero even；不能把非正都说成负数，也不能用余数等于 1 作为全部奇数的判据。把这两次判断分开，再用负三、负二、零、二、三逐个试运行，可以核对所有可能的符号与奇偶组合。

**完整程序（C++17）**

文件：`main.cpp`

```cpp
#include <iostream>
int main() {
    int value{0};
    if (!(std::cin >> value) || value < -1000 || value > 1000) {
        std::cerr << "INVALID\n";
        return 1;
    }
    if (value < 0) {
        std::cout << "negative ";
    } else if (value == 0) {
        std::cout << "zero ";
    } else {
        std::cout << "positive ";
    }
    if (value % 2 == 0) {
        std::cout << "even\n";
    } else {
        std::cout << "odd\n";
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

```text
-7
```

**预期输出**

```text
negative odd
```

**预期标准错误**

（无输出）

**退出状态**：`0`。


</details>

### 练习 3

输入 0 到 1000000000 的整数，输出其通常十进制表示的位数与各位数字之和；不计输入中多写的前导零。样例为 5070。零的位数约定为一。非法输入仍按 INVALID 失败。

<details>
<summary>提示</summary>

每次取除以十的余数作为末位，再整除十去掉末位；需要保证零也处理一次。

</details>

<details>
<summary>解答与检查</summary>

do-while 先执行一次循环体，再检查继续条件；零因此得到一位、数字和零。5070 依次取出 0、7、0、5，位数为 4，和为 12。非零 value 每次整除十都会缩短，最多处理十位。余数在 0 到 9，显式转成 int 安全，数字和至多 90。1000000000 得到 10 和 1，能检查上边界与连续零。

**完整程序（C++17）**

文件：`main.cpp`

```cpp
#include <iostream>
int main() {
    long long value{0};
    if (!(std::cin >> value) || value < 0 || value > 1000000000LL) {
        std::cerr << "INVALID\n";
        return 1;
    }
    int digits{0};
    int sum{0};
    do {
        sum += static_cast<int>(value % 10);
        value /= 10;
        ++digits;
    } while (value != 0);
    std::cout << digits << ' ' << sum << '\n';
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
5070
```

**预期输出**

```text
4 12
```

**预期标准错误**

（无输出）

**退出状态**：`0`。


</details>

<a id="pitfalls"></a>

## 容易混淆的地方

- **以为编译成功就说明算法、输入与边界都正确。** 编译只检查部分语言约束；还应分别核对正常结果、错误路径和终止条件，并避免运行旧的可执行文件。
- **先作整数除法，再赋给浮点变量就能恢复小数。** 计算已经向零截断；必须在除法之前转换操作数，显示位数不能恢复丢失信息。
- **输入变量有初值，就可以忽略读取失败继续计算。** 初值只是初始状态；读取失败后没有得到题目要求的数据，应按接口约定结束或恢复流状态。
- **认为负数的余数规则与先前 Python 章节完全相同。** 这里 C++17 商向零截断；用被除数等于商乘除数加余数核对，不把 Python 的向下整除规则照搬过来。

<a id="self-check"></a>

## 离开这一章前

- [ ] 不看样例，写出一次保存、编译和运行的具体操作，并解释每一步产物。
- [ ] 预测负 7 除以 3 的商与余数，说明转换前后计算 7 除以 2 的区别。
- [ ] 分别构造空输入、越界数和中途缺项，核对输出流、错误流与退出状态。
- [ ] 对 n 为 0、1、最大值追踪循环，并说明累计值为何不会超出所选类型。

## 本章边界

- 采用 GCC 风格的 C++17 命令；安装工具链与不同终端的输入方式见练习指引，未要求某个编辑器。
- 本章按题目约定读取指定数量的整数，尚不严格拒绝所有数字前缀或多余字段；整行解析在第 39 章处理。
- 仅介绍基础整数与浮点使用，未展开全部转换规则、求值次序、字符编码和数值误差分析。

## 选题来源与覆盖

来源含学生报告时，仅将其作为选题线索；具体机制仍需结合后续实验或权威资料核对。

- [大一上/程序设计基础/hw/编程手记/C++札记.docx](https://github.com/PKUanonym/REKCARC-TSC-UHT/blob/37cd19f7a9fb80dc846a7016b3fd482ed5fe7cc0/%E5%A4%A7%E4%B8%80%E4%B8%8A/%E7%A8%8B%E5%BA%8F%E8%AE%BE%E8%AE%A1%E5%9F%BA%E7%A1%80/hw/%E7%BC%96%E7%A8%8B%E6%89%8B%E8%AE%B0/C%2B%2B%E6%9C%AD%E8%AE%B0.docx)（已提取可读文本，固定版本 37cd19f7a9fb）
- 主题 1：C++ 编译诊断、初始化、输入输出与控制流的学习问题；位置：Word 正文。
- 主题 2：函数声明与参数传递、数组范围、指针及动态资源的学习问题；位置：Word 正文。

## 参考资料与规则核对

上游入口用于确定学习方向；下面的参考资料用于核对语言语义、数据结构或算法分析规则，例题和练习由本项目重新设计。

- [GCC：编译阶段与输出选项](https://gcc.gnu.org/onlinedocs/gcc/Overall-Options.html)：核对预处理、编译、汇编、链接及 -c 的含义；具体演示为本项目原创并实际构建。
- [C++17 草案 N4659：basic.fundamental](https://timsong-cpp.github.io/cppwp/n4659/basic.fundamental)：核对基础类型和可表示范围的实现相关性，不假定所有 int 都是 32 位。
- [C++17 草案 N4659：expr.mul](https://timsong-cpp.github.io/cppwp/n4659/expr.mul)：核对整数除法向零截断、余数关系及除零前置条件。
- [C++17 草案 N4659：istream.formatted.arithmetic](https://timsong-cpp.github.io/cppwp/n4659/istream.formatted.arithmetic)：核对数值提取和失败状态；固定条数读取与完整记录解析由正文区分。

**继续学习**：先独立完成自测，再记录仍需回读的步骤。

[上一章：合并区间摘要：线段树与延迟更新](36-segment-tree.md) · [下一章：函数与对象的生命周期：C++ 值、引用和指针](38-cpp-functions-lifetime.md)

[教材目录](index.md) · [C++ 练习与编译](../cpp-programming-practice.md) · [记录自己的学习](../learning-log-template.md)
