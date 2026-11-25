# 函数与对象的生命周期：C++ 值、引用和指针

[返回教材目录](index.md) · [C++ 练习与编译](../cpp-programming-practice.md)

[上一章：从源码到运行：C++ 类型、输入输出与控制流](37-cpp-basics.md) · [下一章：组织完整的小程序：C++ 文件、接口与测试](39-cpp-files-project.md)

[学习目标](#objectives) · [需要的基础](#prerequisites) · [例题](#examples) · [练习](#practice) · [自测](#self-check)

状态：**AI 初稿，可开始试学**。生成模型：Codex 当前会话（未记录具体模型型号）。

本章围绕资料中识别到的知识点重新编写；讲解、数值模型、例题与练习为 AI 原创组织，不是原课程题目或答案。主题出处只说明选题关联，不证明全部推导已经正确。

这一章继续程序设计基础的 C++ 单元，研究函数调用时到底复制了什么、哪些操作会改变调用者，以及一个名字仍能写出来时，它所指向的对象是否还活着。值、引用、指针和容器各自提供不同的接口承诺，不能只凭输出看起来相同就认为它们等价。我们用小额转移、数组搜索和返回容器建立可追踪的模型，再用构造与析构日志观察作用域退出。所有演示都在有效对象和合法范围内运行，不靠悬空访问或越界的偶然表现推导结论。

<a id="objectives"></a>

## 学完要能做到

- 通过调用前后状态区分传值、引用和指针参数，解释 const 约束的对象。
- 说明数组参数为什么还需要长度，以及空指针与空范围的区别。
- 根据对象的创建和销毁顺序解释作用域、生命周期与 RAII。
- 设计失败不改变调用者状态的函数，并正确处理参数指向同一对象的情况。
- 按值返回自有结果，识别不应返回的局部对象引用或地址。

<a id="prerequisites"></a>

## 需要的基础

- 第 37 章的 C++17 编译、基本类型、初始化、分支与循环。
- 第 5 章的参数和返回值概念；第 6 章的下标与半开范围可以辅助理解。
- 知道每段完整程序应放入自己的目录编译，不能直接拼接多个 main。

## 1. 参数是接口：传值建立独立对象

函数定义先写返回类型，再写名字和参数列表，最后给出函数体。下面 next\_value 接收一个 int 值并返回 int；调用它时，实际参数 value 的值用于初始化函数自己的形参对象。两边恰好同名，也不是同一个对象。函数内部的加一只修改形参；return 把结果交给调用表达式，调用者再决定保存在哪里。为避免超过类型范围，本例接口只承诺处理负 1000 到 1000 的输入，最大返回值 1001 可以表示。

编译器在调用处需要先看到函数声明。本例把定义放在 main 前面，一次提供声明与实现；多文件程序会把声明放入头文件，后续单元再展开。如果返回类型是 void，表示不提供返回值；非 void 的普通函数则要让每条正常完成的路径返回合适结果。不要给任意函数补一个 return 0 来消除诊断，而忽略它应当计算的含义。main 在这一点上有特殊规则，本书仍显式写出成功返回。

传值的优点是状态关系清楚：输入值被复制进来，结果由返回值带出去，调用者的整数保持不变。这不表示所有类型的复制都很便宜，也不表示复制一个指针就复制了它指向的对象。现在先追踪两个整数：调用前外面的值是 4，形参从 4 变成 5，函数返回 5；外面的 value 仍为 4，result 则为 5。这条状态说明比“函数把 value 加一了”更准确。

**完整程序（C++17）**

文件：`main.cpp`

```cpp
#include <iostream>
int next_value(int value) {
    ++value;
    return value;
}
int main() {
    int value{4};
    int result{next_value(value)};
    std::cout << value << ' ' << result << '\n';
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
4 5
```

**预期标准错误**

（无输出）

**退出状态**：`0`。


选题关联：来源主题 2（文末列出）。

## 2. 引用是别名，失败规则应先于修改

int 后的引用符号表示这里声明的是一个引用。初始化引用时把它绑定到已有对象；使用引用名读写，访问的就是所绑定对象。下面 alias 绑定 balance，没有增加一份余额。把 alias 赋值并不会让它重新绑定另一个对象，而是修改 balance。函数参数写成 int 的引用时，调用函数的普通变量便可以被函数修改，这种副作用应在接口说明中说清楚。

take 的输入约定是初始余额为 0 到 1000，amount 是任意可表示的 int。返回 true 表示扣减成功，false 表示不满足扣减条件且余额保持原值。先检查 amount 是否负数或大于余额，全部通过后再扣减。这让失败情况不必猜测“是否已经扣掉一半”。传引用本身不保证这条规则，顺序安排才保证。第二次尝试从 7 扣 8 被拒绝，输出 false 的默认数字形式 0，余额仍为 7。

只读的大对象参数常写成 const 引用：既表达通过该参数不修改对象，也避免为了读取而复制整个容器。const 约束的是这条访问路径，不是把对象从世界上所有地方冻结；若另有可写引用，原对象仍可能被修改。引用也不天然延长普通局部变量的生命，函数不能返回已经结束生命周期的局部对象引用。先理解“绑定谁、谁允许修改、对象何时销毁”这三个问题，再选择参数形式。

**完整程序（C++17）**

文件：`main.cpp`

```cpp
#include <iostream>
bool take(int& balance, int amount) {
    if (amount < 0 || amount > balance) {
        return false;
    }
    balance -= amount;
    return true;
}
int main() {
    int balance{10};
    int& alias{balance};
    bool first{take(alias, 3)};
    std::cout << first << ' ' << balance << '\n';
    bool second{take(balance, 8)};
    std::cout << second << ' ' << balance << '\n';
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
1 7
0 7
```

**预期标准错误**

（无输出）

**退出状态**：`0`。


选题关联：来源主题 2（文末列出）。

## 3. 指针保存定位信息，空值检查只是第一道条件

在表达式中，地址运算符取得已有对象的地址；声明中的星号表示指针类型，表达式中的星号则表示解引用。int 指针保存的是定位整数对象的信息，复制指针只复制定位信息，两个指针仍可访问同一个整数。nullptr 是空指针值，用来表达这里没有对象。下面 add\_one 接受空指针并返回失败，或者接受指向活着的可写 int 的指针；非空参数的有效性仍由调用者保证。

条件从左往右短路，因此检查为 nullptr 时不会继续解引用。函数再限制原值为 0 到 999，成功后加一，输出不会超过 1000。这里的边界检查保证算术安全，却不能验证任意非空地址是否真的指向有效对象。已经销毁的对象留下的地址可能非空，越界形成的地址也可能非空；“不为空就能读”是错误推理。本例只取得仍在 main 中存活的 value 的地址。

比较两种声明。const int\* view 允许 view 改指另一个整数，通过它只能读整数。int\* const fixed 则把指针本身固定在初始化时的地址，通过它可以修改所指的非 const 整数。看 const 修饰的是整数还是指针，就能判断哪一种修改被允许。样例中的 view 是前一种：add\_one 通过另一个可写指针把 value 改成 6，随后从 view 读取也得到 6。输出不打印具体地址，因为地址会随运行环境改变；检查“是否指向同一元素”才是本例稳定的性质。

**完整程序（C++17）**

文件：`main.cpp`

```cpp
#include <iostream>
bool add_one(int* value) {
    if (value == nullptr || *value < 0 || *value >= 1000) {
        return false;
    }
    ++*value;
    return true;
}
int main() {
    int value{5};
    const int* view{&value};
    bool changed{add_one(&value)};
    std::cout << changed << ' ' << *view << '\n';
    std::cout << add_one(nullptr) << '\n';
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
1 6
0
```

**预期标准错误**

（无输出）

**退出状态**：`0`。


选题关联：来源主题 2（文末列出）。

## 4. 数组、长度与借用范围

内置数组在声明时确定元素个数，下面的三个整数连续存放，有效下标是 0、1、2。数组作为这种函数实参时会转换为指向首元素的指针；函数单凭这个指针无法恢复原数组长度。因此 sum\_values 同时接收指针和 length，约定后者不超过 1000，所指范围中每个整数在负 1000 到 1000 之间，并且全部对象在调用期间活着。函数没有神奇办法检测调用者谎报的长度。

std::size\_t 是用于大小等用途的无符号整数类型，cstddef 提供该名字。循环用同种类型的 i 比较 length，避免混用负数下标。无符号数并不允许你安全地写负 1 下标；先处理空范围和边界仍是必要的。values\[i\] 表示访问第 i 项；在循环条件保证 i 严格小于 length 的前提下，它落在约定的半开范围内。累计和绝对值最多一百万，long long 足够。

本章允许 length 等于 0 时传 nullptr，因为循环不执行，也没有进行解引用或指针运算。若 length 非零，空指针绝不能充当数组。指向数组末尾后一位置的指针可参与合法的范围比较等特定操作，但不能解引用；超出允许范围的指针运算也不能通过“反正不读”来辩护。内置数组不会在下标访问时自动检查边界，日常还可以选择 std::array 或 std::vector 保留大小信息；它们的普通下标访问也仍要求调用者保证范围。

**完整程序（C++17）**

文件：`main.cpp`

```cpp
#include <cstddef>
#include <iostream>
long long sum_values(const int* values, std::size_t length) {
    long long sum{0};
    for (std::size_t i{0}; i < length; ++i) {
        sum += values[i];
    }
    return sum;
}
int main() {
    int values[]{2, -3, 7};
    std::cout << sum_values(values, 3) << '\n';
    std::cout << sum_values(nullptr, 0) << '\n';
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
6
0
```

**预期标准错误**

（无输出）

**退出状态**：`0`。


选题关联：来源主题 2（文末列出）。

## 5. 作用域、生命周期与自动清理

作用域决定在哪里可以用某个名字；生命周期描述运行时对象何时存在。本例中的局部对象在取得合适的存储并完成初始化时开始生命周期。正常离开块时，已构造的自动对象按构造完成的逆序销毁。把地址保存在块外的变量里，不会阻止块内对象销毁；因此指针名仍在作用域内，不代表其指向的对象还活着。静态局部对象通常能跨多次函数调用保留状态，但名字的可见范围仍局限于局部；本章不依靠全局或静态状态在函数间偷偷传结果。

下面用一个仅打印日志的 Trace 类型观察次序。struct 把数据成员 id 和相关函数放在一起；与类型同名的函数是构造函数，冒号后的初始化列表给 id 初值，这里的 explicit 阻止一个整数被隐式转换为 Trace，仍允许用花括号直接构造对象；名字前有波浪号的是析构函数，对象销毁时执行。结构体定义结尾也有分号。本例只直接构造两个局部对象，没有复制它们，所以日志可直接对应这两个对象。内部块结束先销毁 inner，work 正常返回时再销毁 outer，最后 main 输出已得到的整数结果。

RAII 把资源的持有交给对象：构造或其他受控操作取得资源，析构释放资源。标准库 vector 管理其元素存储，文件流管理打开的文件，这让正常离开作用域和正常异常展开时能够自动清理。本例日志只演示生命周期，并未实现真正的资源管理器。直接用 new 获得的资源不会因为保存地址的裸指针离开作用域就自动释放；初学时优先使用现成的拥有资源的类型。返回一个容器值是交出结果对象，返回局部容器内部地址则可能留下悬空借用，二者必须区分。

**完整程序（C++17）**

文件：`main.cpp`

```cpp
#include <iostream>
struct Trace {
    int id;
    explicit Trace(int value) : id{value} {
        std::cout << "open " << id << '\n';
    }
    ~Trace() {
        std::cout << "close " << id << '\n';
    }
};
int work() {
    Trace outer{1};
    {
        Trace inner{2};
        std::cout << "inside\n";
    }
    std::cout << "leaving\n";
    return 7;
}
int main() {
    int result{work()};
    std::cout << "result " << result << '\n';
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
open 1
open 2
inside
close 2
leaving
close 1
result 7
```

**预期标准错误**

（无输出）

**退出状态**：`0`。


选题关联：来源主题 2（文末列出）。

<a id="examples"></a>

## 跟着做：原创例题

### 例题 1

两个不同整数对象表示容量上限为 1000 的库存，初始为 9 和 2。设计 transfer 把 4 从左侧转到右侧，成功返回 true；库存非法、数量非法、容量不足或两个参数别名同一对象时，返回 false 且两边都不变。

1. 先检验两个引用实际绑定的地址是否相同，本例规定自转移一律拒绝。
2. 依次检验两个库存处于 0 到 1000，数量非负且不超过来源库存。
3. 目标剩余容量用 1000 减目标库存求得；检查通过之前不修改任何对象。
4. 从来源扣 4，给目标加 4，得到 5 和 6；再尝试以同一个 left 作两边，必须保留这组结果。

**结果与核对**

第一次输出 1 5 6，第二次输出 0 5 6。成功时总库存仍为 11，且两边都在范围内；失败时不仅返回 false，还要比较调用前后的两个值。拒绝别名是这个接口明确选择的规则，不能从“引用能修改外面”自动推导出正确的双对象更新。

**完整程序（C++17）**

文件：`main.cpp`

```cpp
#include <iostream>
bool transfer(int& from, int& to, int amount) {
    if (&from == &to || from < 0 || from > 1000 || to < 0 || to > 1000
        || amount < 0 || amount > from || amount > 1000 - to) {
        return false;
    }
    from -= amount;
    to += amount;
    return true;
}
int main() {
    int left{9};
    int right{2};
    bool moved{transfer(left, right, 4)};
    std::cout << moved << ' ' << left << ' ' << right << '\n';
    bool same{transfer(left, left, 1)};
    std::cout << same << ' ' << left << ' ' << right << '\n';
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
1 5 6
0 5 6
```

**预期标准错误**

（无输出）

**退出状态**：`0`。


### 例题 2

函数返回一个包含 4、6、8 的 vector，调用者复制这个容器，并把副本第一项改为 9。分别计算两个容器的总和与长度，解释局部容器为何可以按值返回。

1. vector 是保存可变长度元素的标准库容器，尖括号中的 int 表示元素类型；花括号列出三个初值。
2. 返回类型是 vector 的值，返回结果自身拥有存储；调用者并未借用已经消失的局部变量。
3. auto 根据初始化表达式推导类型，不表示变量没有静态类型；copy 由 original 复制构造，得到独立的整数元素。
4. total 用 const 引用只读访问容器；范围 for 依次把每个元素值复制给 value，累计后返回。

**结果与核对**

原容器总和为 18，副本总和为 23，长度都是 3。按值返回可能使用复制省略或移动等机制，具体优化不改变结果的有效性；不要靠打印复制次数定义本例答案。修改副本不改原容器，和把两个指针指向同一个数组的情况不同。为了让求和范围有保证，total 的使用约定仍是至多 1000 个、每项绝对值不超过 1000。

**完整程序（C++17）**

文件：`main.cpp`

```cpp
#include <iostream>
#include <vector>
std::vector<int> make_values() {
    std::vector<int> values{4, 6, 8};
    return values;
}
long long total(const std::vector<int>& values) {
    long long sum{0};
    for (int value : values) {
        sum += value;
    }
    return sum;
}
int main() {
    auto original{make_values()};
    auto copy{original};
    copy[0] = 9;
    std::cout << total(original) << ' ' << total(copy) << '\n';
    std::cout << original.size() << ' ' << copy.size() << '\n';
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
18 23
3 3
```

**预期标准错误**

（无输出）

**退出状态**：`0`。


<a id="practice"></a>

## 自己做：先完成再看解答

### 练习 1

写一个不返回结果值的 exchange 函数，交换两个 int 引用绑定的值。先交换 3 与 8，再把同一个变量传给两个参数；两种调用都应正确，不使用加减法交换。

<details>
<summary>提示</summary>

临时变量保存的是值的副本；考虑两个形参恰好指向同一对象时，每一步读到什么。

</details>

<details>
<summary>解答与检查</summary>

先保存 first 的旧值，再令 first 等于 second，最后令 second 等于保存值。不同对象得到 8 与 3；同一对象时每步都写回同样的值，仍为 8 与 3。只做 int 之间的复制，不依赖算术，因此不会因两个值相加超过范围而出错。这里允许别名；与库存例题拒绝别名相比，区别来自接口要求。

**完整程序（C++17）**

文件：`main.cpp`

```cpp
#include <iostream>
void exchange(int& first, int& second) {
    int saved{first};
    first = second;
    second = saved;
}
int main() {
    int first{3};
    int second{8};
    exchange(first, second);
    std::cout << first << ' ' << second << '\n';
    exchange(first, first);
    std::cout << first << ' ' << second << '\n';
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
8 3
8 3
```

**预期标准错误**

（无输出）

**退出状态**：`0`。


</details>

### 练习 2

实现只读 find\_first，接收一个借用的整数数组范围和目标，找到第一个相等元素就返回其地址，否则返回 nullptr。数组为 4、7、7，验证找到的是第一个 7；空范围允许空指针。

<details>
<summary>提示</summary>

返回的必须是调用者数组里的元素地址，不能返回函数中临时复制值的地址。

</details>

<details>
<summary>解答与检查</summary>

从零下标开始逐项比较，命中就返回该元素地址，因此重复的 7 返回下标 1 的元素。目标 9 和空范围都得到 nullptr；在解引用前先检查返回值。返回地址只在原数组仍活着、相应存储仍有效时可用，函数返回并不会延长数组生命周期。数组长度由调用者诚实提供，不超过实际范围；这里测试地址相等而不是输出地址数字。

**完整程序（C++17）**

文件：`main.cpp`

```cpp
#include <cstddef>
#include <iostream>
const int* find_first(const int* values, std::size_t length, int target) {
    for (std::size_t i{0}; i < length; ++i) {
        if (values[i] == target) {
            return &values[i];
        }
    }
    return nullptr;
}
int main() {
    int values[]{4, 7, 7};
    const int* found{find_first(values, 3, 7)};
    if (found != nullptr) {
        std::cout << *found << ' ' << (found == &values[1]) << '\n';
    }
    std::cout << (find_first(values, 3, 9) == nullptr) << '\n';
    std::cout << (find_first(nullptr, 0, 7) == nullptr) << '\n';
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
7 1
1
1
```

**预期标准错误**

（无输出）

**退出状态**：`0`。


</details>

### 练习 3

写 keep\_nonnegative，接收 const vector 引用，返回一个新的 vector，仅保留非负元素，顺序和重复次数不变。输入为负 2、0、5、负 1、5；检查原输入仍有五项，返回结果有三项。

<details>
<summary>提示</summary>

使用空结果容器并逐项 push\_back，通过值返回拥有存储的结果；不要返回局部结果的引用。

</details>

<details>
<summary>解答与检查</summary>

依次保留 0、5、5，不能去掉重复值或重新排序。push\_back 在末尾追加元素，可能引起重新分配，所以不要保存指向结果内部的指针并在后续追加后继续使用。返回容器值安全地把结果交给调用者，输入通过 const 引用读取。输出时只在相邻元素间写一个空格。first 初始为真，写出首项后变为假，此后每写一项都先输出分隔符。空输入和全负输入返回空 vector，且都不修改输入。

**完整程序（C++17）**

文件：`main.cpp`

```cpp
#include <iostream>
#include <vector>
std::vector<int> keep_nonnegative(const std::vector<int>& input) {
    std::vector<int> result;
    for (int value : input) {
        if (value >= 0) {
            result.push_back(value);
        }
    }
    return result;
}
int main() {
    const std::vector<int> input{-2, 0, 5, -1, 5};
    auto result{keep_nonnegative(input)};
    bool first{true};
    for (int value : result) {
        if (!first) {
            std::cout << ' ';
        }
        std::cout << value;
        first = false;
    }
    std::cout << '\n' << input.size() << ' ' << result.size() << '\n';
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
0 5 5
5 3
```

**预期标准错误**

（无输出）

**退出状态**：`0`。


</details>

<a id="pitfalls"></a>

## 容易混淆的地方

- **认为引用是副本，或者认为指针复制会复制整片数组。** 引用提供同一对象的别名；指针复制保存相同定位信息。要证明独立存储，需要核对实际容器的复制语义。
- **只要指针不是 nullptr 就可以解引用。** 还必须指向生命周期内的有效对象并满足访问权限；非空检查不能发现悬空指针或错误长度。
- **把作用域外保存的地址当成保活机制。** 保存地址不会延长普通局部对象的生命。返回拥有数据的值，或明确借用对象由调用者维持。
- **为节省复制，把局部结果改成引用返回。** 局部对象结束后该引用会悬空。先保证所有权正确，现代 C++ 的返回值机制可避免许多不必要复制。

<a id="self-check"></a>

## 离开这一章前

- [ ] 为传值、传引用和传指针分别画出调用前后对象关系。
- [ ] 解释为什么 nullptr 配零长度安全，但 nullptr 配一长度不满足数组接口。
- [ ] 逐行写出 Trace 的构造和析构顺序，说明返回结果为何仍可使用。
- [ ] 测试库存转移的容量上限、余额不足、负数量和别名，比较失败前后状态。
- [ ] 举出一次 vector 追加可能使旧指针失效的原因，并给出不保存该借用的写法。

## 本章边界

- 展示基本对象和借用规则，未展开继承、多态、移动构造实现、智能指针和完整的异常安全等级。
- 原始指针接口有调用者前置条件；测试不能验证任意地址是否有效，也不执行悬空访问或越界来猜结果。
- RAII 示例观察正常离开块和返回的析构顺序；异常展开在下一章衔接，强制终止进程不属于这里的自动清理保证。

## 选题来源与覆盖

来源含学生报告时，仅将其作为选题线索；具体机制仍需结合后续实验或权威资料核对。

- [大一上/程序设计基础/hw/编程手记/C++札记.docx](https://github.com/PKUanonym/REKCARC-TSC-UHT/blob/37cd19f7a9fb80dc846a7016b3fd482ed5fe7cc0/%E5%A4%A7%E4%B8%80%E4%B8%8A/%E7%A8%8B%E5%BA%8F%E8%AE%BE%E8%AE%A1%E5%9F%BA%E7%A1%80/hw/%E7%BC%96%E7%A8%8B%E6%89%8B%E8%AE%B0/C%2B%2B%E6%9C%AD%E8%AE%B0.docx)（已提取可读文本，固定版本 37cd19f7a9fb）
- 主题 1：C++ 编译诊断、初始化、输入输出与控制流的学习问题；位置：Word 正文。
- 主题 2：函数声明与参数传递、数组范围、指针及动态资源的学习问题；位置：Word 正文。

## 参考资料与规则核对

上游入口用于确定学习方向；下面的参考资料用于核对语言语义、数据结构或算法分析规则，例题和练习由本项目重新设计。

- [C++17 草案 N4659：dcl.ref](https://timsong-cpp.github.io/cppwp/n4659/dcl.ref)：核对引用绑定与别名规则，例题自行规定别名允许或拒绝的契约。
- [C++17 草案 N4659：conv.array](https://timsong-cpp.github.io/cppwp/n4659/conv.array)：核对数组到首元素指针的转换；额外长度及空范围约定由本项目定义。
- [C++17 草案 N4659：basic.life](https://timsong-cpp.github.io/cppwp/n4659/basic.life)：核对生命周期与访问有效性的关系，不实际执行悬空访问或越界。
- [C++17 草案 N4659：vector.modifiers](https://timsong-cpp.github.io/cppwp/n4659/vector.modifiers)：核对追加可能重新分配并使元素借用失效的条件。
- [C++17 草案 N4659：except.ctor](https://timsong-cpp.github.io/cppwp/n4659/except.ctor)：核对异常展开时已构造自动对象的销毁，正常作用域日志另由实际运行验证。

**继续学习**：先独立完成自测，再记录仍需回读的步骤。

[上一章：从源码到运行：C++ 类型、输入输出与控制流](37-cpp-basics.md) · [下一章：组织完整的小程序：C++ 文件、接口与测试](39-cpp-files-project.md)

[教材目录](index.md) · [C++ 练习与编译](../cpp-programming-practice.md) · [记录自己的学习](../learning-log-template.md)
