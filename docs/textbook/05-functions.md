# 把计算组织成函数：参数、返回值与局部名字

[返回教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md)

[上一章：程序怎样作选择和重复：顺序、分支与循环](04-control-flow.md) · [下一章：一组数据怎样按位置存取：数组与顺序表](06-arrays.md)

[学习目标](#objectives) · [需要的基础](#prerequisites) · [例题](#examples) · [练习](#practice) · [自测](#self-check)

状态：**AI 初稿，可开始试学**。生成模型：Codex 当前会话（未记录具体模型型号）。

本章围绕资料中识别到的知识点重新编写；讲解、数值模型、例题与练习为 AI 原创组织，不是原课程题目或答案。主题出处只说明选题关联，不证明全部推导已经正确。

上一章已经能写出有分支和循环的程序，但同一种计算经常需要换一组输入再做一次。如果每次都复制整段代码，修改规则时容易漏改，也难分辨哪部分负责计算、哪部分负责显示。本章把一段计算命名为函数，让输入通过参数进入、结果通过返回值出去。你会逐步追踪一次调用发生了什么，区分局部名字与外部名字，并把小函数组合成更清楚的程序。所有例子仍使用小整数和完整代码，不要求类、指针或递归知识。

<a id="objectives"></a>

## 学完要能做到

- 区分定义函数与调用函数，解释形参与实参在一次调用中的对应关系。
- 根据明确的输入范围设计函数，使用 return 把结果交给调用者。
- 区分屏幕输出与返回值，识别只打印却没有返回计算结果的情况。
- 逐步追踪局部名字，说明整数参数的重新赋值为什么不会改掉调用处的名字。
- 组合小函数并用零、边界、普通输入核对结果，检查每条需要的返回路径。

<a id="prerequisites"></a>

## 需要的基础

- 已经学习第 4 章的赋值、print、比较、缩进、分支、while、for 与 range。
- 会按语句顺序记录状态，理解整除的商、余数以及非负整数的加减乘法。
- 示例使用 Python 3.11 或更新版本，每个代码块单独运行。

## 一、定义一个动作，再用输入调用它

函数把一段计算与一个名字关联起来。下面的 increase\_by\_two 表示把给定整数增加 2。def 开始定义，后面依次是函数名、圆括号里的参数名和冒号，下一行的缩进块是函数体。number 是形参，表示这段计算需要一个输入；return 后面的表达式给出本次调用的结果。

执行到这个简单的 def 语句时，Python 建立函数并把函数名绑定到它，不会立刻执行函数体里的加法。随后 increase\_by\_two(5) 才发起调用：把整数 5 交给这次调用的 number，进入函数体，算出 7，再返回到原来的调用位置。写成 result = increase\_by\_two(5)，就是用返回的 7 给 result 赋值。

调用里的 5 叫实参；实参也可以是变量或表达式，例如 increase\_by\_two(3 + 2)。表达式先计算成值，再交给形参。名字相同并不是调用的要求：外部可以把自己的变量叫 initial，函数内部仍把收到的对象叫 number。先看参数位置的对应，再追踪函数里的计算，避免被名称迷惑。

函数名后面的圆括号在这里表示调用，不是装饰。只写函数名不会运行函数体。当前示例把定义放在调用之前，保证调用发生时这个名字已经存在。学习时可以把一次调用展开为“求实参、绑定形参、运行函数体、取得返回值”四步，再对照下方最后一行的输出。

**完整程序**

```python
def increase_by_two(number):
    return number + 2

result = increase_by_two(5)
print(result)
```

**预期输出**

```text
7
```


选题关联：来源主题 1（文末列出）。

## 二、参数传进什么，重新赋值改了谁

函数可以有多个参数。advance(position, step) 的两个名字依次表示起点和前进量；调用 advance(origin, 3) 时，origin 当前指向的对象交给 position，整数 3 交给 step。这是按位置传入，顺序属于函数约定。即使某次加法交换顺序恰好结果一样，也不能因此忽略一般函数的参数含义。

Python 调用会让形参绑定到传入的对象，不会自动把外部变量的名字交给函数去改。下面 origin 为整数 4，函数内先算 position + step 得到 7，再让局部的 position 指向 7。调用处的 origin 仍指向 4，因此最后同时打印 origin 与 result，会得到 4 和 7。

这里一定要说准“没有改变”的原因：例子使用整数，整数对象不可变；赋值重新绑定的是函数内的名字。不要把它简化成“Python 总是复制所有参数”，也不要推断任何函数都无法影响外部数据。以后传入列表等可变对象，函数可能通过共享对象修改其内容；这不属于本章输入范围。

形参还是接口的一部分。定义时声明两个必需参数，本章就总是给出两个实参，并使用约定的整数类型。少给参数、多给参数或传入不支持的类型，可能得到错误，不会由函数自动补出本题想要的值。写自己的函数前，先用一句话说明每个参数代表什么、允许什么范围，返回结果又代表什么。

**完整程序**

```python
def advance(position, step):
    position = position + step
    return position

origin = 4
result = advance(origin, 3)
print(origin, result)
```

**预期输出**

```text
4 7
```


选题关联：来源主题 1（文末列出）。

## 三、return 交回结果，print 只负责显示

屏幕上出现一个数字，不等于调用者拿到了这个数字。print 负责显示内容，return 负责结束当前函数调用并交回一个对象。若要让调用者继续计算、比较或保存结果，应明确返回该结果；是否显示，可以由调用处决定。这样同一个计算函数既能用于打印，也能用于后续计算。

下面 show\_double 在函数体内打印两倍值，却没有写 return。调用它时屏幕先出现 8；随后函数自然走到末尾，返回的是 None，表示这里没有给出具体计算结果。把这次调用赋给 shown，shown 就指向 None，不会自动收集刚才打印的字符。None 既不是整数 0，也不是字符串 "None"，只是 print 会把这个对象显示成 None。

double 则直接 return 两倍值。调用 double(4) 会返回 8，但这次调用本身不负责打印。将其赋给 returned，再运行 print(shown, returned)，才会在第二行看到 None 8。两个函数的计算式相同，结果传递方式却不同；这也是调试“明明已经显示答案，后面却算不了”的关键。

执行 return 后，当前函数中本来排在后面的普通语句不会继续执行，本章没有需要额外讨论的清理语法。在循环里执行 return 也会离开整个函数，不只是结束一轮循环。要返回完整的累加结果，通常先让循环结束，再在循环外 return；把它错误地缩进到循环内部，会在第一次遇到返回时提前结束。

**完整程序**

```python
def show_double(number):
    print(number * 2)

def double(number):
    return number * 2

shown = show_double(4)
returned = double(4)
print(shown, returned)
```

**预期输出**

```text
8
None 8
```


选题关联：来源主题 1（文末列出）。

## 四、局部名字与每次调用的独立状态

函数中的参数和通常的赋值建立局部名字，作用范围属于这次函数调用。下面 sum\_to 约定 n 为非负整数，使用局部 total 累加 1 到 n。外部也有一个叫 total 的名字，值为 99，但函数内的 total = 0 绑定的是局部名字，不会把外部的 99 改成 0。理解时给它们标上“外部”和“本次调用”，不要只按拼写相同就合并到一张表。

调用 sum\_to(3) 时建立本次的 n 和 total，三轮累计依次为 1、3、6，然后返回 6。再次调用 sum\_to(2) 时会重新运行 total = 0，得到新的累计过程 1、3，返回 3；它不会从前一次的 6 接着加。每次调用有各自的局部绑定，程序返回以后也不能依靠这个函数内部的名字访问上次结果，应使用明确交回的返回值。

这里的局部性来自函数，不是来自每一个缩进块。在同一个函数里，if 和 for 通常不会再建立一套独立的局部名字。循环后的 return total 能看到循环累加的 total，前提是它在本次运行路径中已经赋值。我们特意在循环前初始化，所以 n 为 0、循环一轮都没执行时也能返回 0。

Python 对名字作用范围有比这更多的规则，例如读取外层名字、global 和 nonlocal。本章不展开它们，而是采用容易验证的做法：需要什么值就通过参数传入，结果通过 return 传出，函数内不依赖可变的外部状态。这是本章示例的编写约定，不是在声称所有 Python 函数都必须这样写。

**完整程序**

```python
def sum_to(n):
    total = 0
    for number in range(1, n + 1):
        total = total + number
    return total

total = 99
print(sum_to(3), sum_to(2), total)
```

**预期输出**

```text
6 3 99
```


选题关联：来源主题 1（文末列出）。

## 五、把小函数组合起来，并写清输入约定

函数的价值不只是缩短代码，还在于让每部分任务能单独解释和检查。下面 is\_multiple 只回答“这个整数能否被指定正整数整除”，返回 True 或 False。count\_multiples 则负责遍历 1 到 limit，并调用这个判断函数来决定是否计数。外层函数不需要再次复制余数判断的实现，两个函数各自有明确的职责。

先写输入约定：number 和 limit 是非负整数，divisor 是正整数；is\_multiple 返回真假，count\_multiples 返回符合条件的数量。限制 divisor 为正排除了除以零。程序没有额外检查这些前提，因此传入零除数属于违反本章约定，不能把出错当成合法输入下的教材结论。输入约定不是自动验证代码，二者必须分清。

运行 count\_multiples(8, 3) 时，外层依次检查 1 到 8。每次调用 is\_multiple，暂时进入它的函数体，完成余数比较并返回，然后外层才决定本轮是否增加 count。只有 3 和 6 得到真，最终返回 2。整个过程不需要共享一个外部计数变量，也没有把内层函数的 return 当成外层函数的退出。

组合之前先测小函数，再测组合结果：is\_multiple(6, 3) 为真，is\_multiple(7, 3) 为假；上界为 0 时，count\_multiples 应返回 0。后面还会用整数地板除法 // 计算商：对于本章的非负被除数和正除数，它给出完整容纳多少组，例如 17 // 8 为 2，17 % 8 为 1。把商与余数结合，就能设计与前面分配单元相呼应的小函数。

**完整程序**

```python
def is_multiple(number, divisor):
    return number % divisor == 0

def count_multiples(limit, divisor):
    count = 0
    for number in range(1, limit + 1):
        if is_multiple(number, divisor):
            count = count + 1
    return count

print(count_multiples(8, 3))
```

**预期输出**

```text
2
```


选题关联：来源主题 1（文末列出）。

<a id="examples"></a>

## 跟着做：原创例题

### 例题 1

把第 3 章的分配单位换算组织成函数 required\_units(byte\_count, unit\_size)。输入字节数是非负整数，每单元字节数是正整数，返回足以容纳请求的最少完整单元数。每单元 8 字节时，求请求 17 字节所需单元数与剩余容量，再检查请求 16 字节和 0 字节的返回值。此题只算容量，不进行空闲区间搜索。

1. 先定义返回值的含义：只能分配整数个单元，容量不足时需要再补一个完整单元。
2. 对 17 和 8 做整数除法，完整商为 2，余数为 1，说明两个单元只有 16 字节，不足容纳请求。
3. 因余数非零，把商增加 1，得到需要 3 个单元；然后从函数返回这个整数。
4. 在调用处计算容量 3 乘 8 等于 24，再减请求 17，得到剩余容量 7 字节。
5. 请求 16 字节时商为 2、余数为 0，不再增加，仍须正常执行 return，得到 2。
6. 请求 0 字节时商和余数都为 0，本题约定不分配任何单元，返回 0；这不是对某个真实内存接口零大小请求行为的声明。

**结果与核对**

17 字节需要 3 个单元，剩余容量为 7 字节；16 字节需要 2 个单元；0 字节需要 0 个单元。最小性核对：3 个单元可容纳 17 字节，少一个只有 16 字节就不足。return 与 if 左对齐，保证余数为零时也能返回完整商。

**完整程序**

```python
def required_units(byte_count, unit_size):
    units = byte_count // unit_size
    if byte_count % unit_size != 0:
        units = units + 1
    return units

byte_count = 17
unit_size = 8
units = required_units(byte_count, unit_size)
unused = units * unit_size - byte_count
print(units, unused)
print(required_units(16, 8), required_units(0, 8))
```

**预期输出**

```text
3 7
2 0
```


### 例题 2

编写 square(number) 返回整数的平方，再编写 sum\_even\_squares(n)，返回 1 到 n 中所有偶数的平方和，n 为非负整数。第二个函数应调用第一个函数。外部另有 total = 100。求 n 为 6、0、2 时的返回值，并检查外部 total 是否改变。

1. square 只计算 number 乘自身并返回；sum\_even\_squares 初始化自己的局部 total 为 0。
2. 第一次调用以 n 为 6，依次检查整数 1 到 6，其中 1 不符合偶数条件，不调用平方函数。
3. 检查 2 时调用 square(2)，返回 4，外层的局部 total 从 0 变为 4；返回后继续下一轮。
4. 检查 4 时获得平方 16，局部 total 变为 20；检查 6 时获得平方 36，局部 total 变为 56。
5. 外层循环结束后返回 56。外部 total 与函数中的局部 total 是不同名字绑定，仍为 100。
6. 以 0 再调用时范围为空，返回初始化的 0；以 2 调用时只加入 4，返回 4，每次都重新初始化。

**结果与核对**

n 为 6、0、2 时依次返回 56、0、4。独立相加可核对 2×2 + 4×4 + 6×6 = 4 + 16 + 36 = 56。外部 total 保持 100。square 的 return 只结束它自己的一次调用，sum\_even\_squares 接到结果后继续运行。

**完整程序**

```python
def square(number):
    return number * number

def sum_even_squares(n):
    total = 0
    for number in range(1, n + 1):
        if number % 2 == 0:
            total = total + square(number)
    return total

total = 100
result = sum_even_squares(6)
print(result, total)
print(sum_even_squares(0), sum_even_squares(2))
```

**预期输出**

```text
56 100
0 4
```


<a id="practice"></a>

## 自己做：先完成再看解答

### 练习 1

编写 clamp\_to\_zero(number)：参数为整数，负数返回 0，零或正数返回原数。函数内部不要打印。在调用处分别显示输入 -4、0、6 的结果，说明为什么每条输入路径都会返回一个整数。

<details>
<summary>提示</summary>

可以在负数分支提前 return 0；走到分支之后的输入已经排除了负数，再 return 原数。

</details>

<details>
<summary>解答与检查</summary>

三个结果依次为 0、0、6。负数路径执行第一个 return 后离开函数；其余路径到达后面的 return number。最后一个 return 不能也缩进在负数分支里，否则零和正数可能走到函数末尾，得到 None。

**完整程序**

```python
def clamp_to_zero(number):
    if number < 0:
        return 0
    return number

print(clamp_to_zero(-4), clamp_to_zero(0), clamp_to_zero(6))
```

**预期输出**

```text
0 0 6
```


</details>

### 练习 2

编写 sum\_between(start, stop)，对半开整数范围从 start 到 stop 之前的所有数求和。两个参数都是整数，且 start 不大于 stop；相等时返回 0。给出 start=2、stop=6，start=3、stop=3，以及 start=-2、stop=2 的结果。使用循环，不调用现成求和函数。

<details>
<summary>提示</summary>

直接用 range(start, stop) 表达右端不包含。累计量在循环前设为 0，return 放在整个循环之后。

</details>

<details>
<summary>解答与检查</summary>

三个结果依次为 14、0、-2。第一个范围包含 2、3、4、5，总和 14；第二个没有任何项，保留初值 0；第三个包含 -2、-1、0、1，总和 -2。若把 return 放进循环，非空范围只处理第一项，空范围还可能返回 None。

**完整程序**

```python
def sum_between(start, stop):
    total = 0
    for number in range(start, stop):
        total = total + number
    return total

print(sum_between(2, 6), sum_between(3, 3), sum_between(-2, 2))
```

**预期输出**

```text
14 0 -2
```


</details>

### 练习 3

把第 4 章逐日累加任务封装成 days\_to\_reach(target)：target 为非负整数，第 k 天完成 k 个，返回首次累计达到或超过目标的最少天数，目标 0 返回 0。另写 sum\_to(n) 返回 1 到 n 的和，用它检查目标 16 的答案和前一天的总量，再测试目标 0、1、21。两个计算函数内部都不打印。

<details>
<summary>提示</summary>

在 days\_to\_reach 内维护自己的天数和总量，用 while 找到首次达到目标的状态。返回后，再由调用处用另一个函数核对前一天不足、当天足够。

</details>

<details>
<summary>解答与检查</summary>

目标 16 最少需要 6 天；sum\_to(6) 为 21，sum\_to(5) 为 15，满足当天足够而前一天不足。目标 0、1、21 的返回值依次为 0、1、6。目标 0 是特例，没有需要检查的前一天；其余输入可使用前一天与当天的总量夹住目标。每轮累计增加一个正整数，因而有限的非负目标可以达到。

**完整程序**

```python
def sum_to(n):
    total = 0
    for number in range(1, n + 1):
        total = total + number
    return total

def days_to_reach(target):
    if target == 0:
        return 0
    days = 0
    total = 0
    while total < target:
        days = days + 1
        total = total + days
    return days

days = days_to_reach(16)
print(days, sum_to(days), sum_to(days - 1))
print(days_to_reach(0), days_to_reach(1), days_to_reach(21))
```

**预期输出**

```text
6 21 15
0 1 6
```


</details>

<a id="pitfalls"></a>

## 容易混淆的地方

- **以为执行 def 就已经完成了函数体的计算。** 本章的定义先建立函数，后面的调用才传入具体实参并运行函数体。按每一次调用单独追踪，而不是在定义处代入一个想象的输入。
- **用 print 代替 return，以为赋值会取得屏幕上显示的数字。** 赋值取得调用的返回值，不会收集屏幕输出。函数没有显式返回计算结果时通常得到 None；把计算和显示分别写在函数内外核对。
- **只按名字拼写合并内外状态，或者认定函数总会复制传入对象。** 分别记录每次调用的形参与局部绑定。本章整数的重新赋值不会改掉外部名字，但可变对象的共享和修改需要在后续单独讨论。
- **把 return 缩进到循环内，或只在一种分支里返回结果。** 逐条列出合法输入的运行路径，检查完整循环结束后是否返回预期类型。零次循环和边界恰好相等的输入尤其容易暴露漏掉的返回。

<a id="self-check"></a>

## 离开这一章前

- [ ] 把 advance(4, 3) 展开成实参求值、形参绑定、函数体计算、返回四步，指出外部名字为什么没有被重绑。
- [ ] 遮住第三节输出，分别说明 show\_double 打印了什么、返回了什么，double 又返回了什么。
- [ ] 连续调用 sum\_to(3)、sum\_to(0)、sum\_to(2)，证明每次从自己的初始累计量开始。
- [ ] 对 required\_units 分别测试零请求、恰好一单元、刚超一单元，并说明最小性。
- [ ] 独立完成练习 3，先由函数给出天数，再用当天与前一天的总量检查边界。

## 本章边界

- 仅使用按位置传入的必需参数和单个返回对象；默认参数、关键字参数、可变参数和解包留待后续。
- 示例以整数、布尔值为主，不展开可变容器、闭包、global、nonlocal 或对象生命周期。
- 输入范围由题目明确约定，没有加入交互输入、类型检查、异常处理或完整接口防护。
- 本章不讲递归或真实调用栈布局；函数的局部状态不能直接当成第 2 章四槽玩具栈的实现。

## 选题来源与覆盖

来源含学生报告时，仅将其作为选题线索；具体机制仍需结合后续实验或权威资料核对。

- [大一小学期/Week\_3-Python/docs/readme.md](https://github.com/PKUanonym/REKCARC-TSC-UHT/blob/37cd19f7a9fb80dc846a7016b3fd482ed5fe7cc0/%E5%A4%A7%E4%B8%80%E5%B0%8F%E5%AD%A6%E6%9C%9F/Week_3-Python/docs/readme.md)（已提取可读文本，固定版本 37cd19f7a9fb）
- 主题 1：Python 基础语法的外部学习入口；位置：第 41–80 行。
- 主题 2：从基础语法到工具与应用的建议阅读顺序；位置：第 121–160 行。

## 语言与结构规则核对

上游入口用于确定学习方向；下面的参考资料用于核对语言或数据结构规则，例题和练习由本项目重新设计。

- [Python 3.11：定义和调用函数](https://docs.python.org/3.11/tutorial/controlflow.html#defining-functions)：核对 def、形参、函数调用以及未显式返回值时的 None。
- [Python 3.11：return 语句](https://docs.python.org/3.11/reference/simple_stmts.html#the-return-statement)：核对 return 结束当前函数调用并把结果交给调用者。
- [Python 3.11：名字与绑定](https://docs.python.org/3.11/reference/executionmodel.html#naming-and-binding)：核对参数和局部名字的作用范围；不把整数重新绑定推广成所有对象的复制。

**继续学习**：先独立完成自测，再记录仍需回读的步骤。

[上一章：程序怎样作选择和重复：顺序、分支与循环](04-control-flow.md) · [下一章：一组数据怎样按位置存取：数组与顺序表](06-arrays.md)

[教材目录](index.md) · [编程练习与运行](../programming-practice.md) · [数据结构练习指引](../data-structures-practice.md) · [记录自己的学习](../learning-log-template.md)
