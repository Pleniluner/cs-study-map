# 人工神经网络

*依据本目录四次作业的批改标准、示例提交和测试程序整理；学习顺序从 NumPy 手写 MLP/CNN，过渡到正则化与 TensorFlow，再到 RNN、LSTM、GRU 和自注意力。*

---

## 📋 课程定位

本课程的价值在于亲手实现神经网络的前向传播、反向传播和参数更新，再理解框架如何封装这些过程。现有资料不是完整讲义，而是四次作业的评分标准、压缩包源码与测试程序，因此 README 按可见验收点恢复能力路线。

原 README 记录该年份“无考试、四次作业、最后有自主选题 Final Project”。这是历史课程经验，当前目录没有 Final Project 的任务书或提交件。

## 🎯 应掌握的知识

- 张量形状、批处理、计算图、链式法则和反向传播。
- Linear、ReLU、Sigmoid 的 forward/backward，以及梯度累积和参数更新。
- Euclidean loss、Softmax + cross-entropy 和数值稳定的 log-sum-exp 思想。
- SGD、mini-batch、学习率、momentum、weight decay、初始化与学习曲线。
- 二维卷积、padding、channel、池化、展平和卷积梯度。
- MLP 与 CNN 的归纳偏置、参数量、精度和运行时间比较。
- Dropout 与 Batch Normalization 在训练/推理阶段的不同行为。
- Vanilla RNN、GRU、LSTM 的状态和门控；双向、多层循环网络。
- 文本 embedding、变长序列、mask/self-attention 和注意力多样性惩罚。
- 实验可复现、梯度检查、消融、超参数搜索和错误分析。

## 📚 四次作业地图

| 作业 | 核心任务 | 归档材料 |
|---|---|---|
| HW1 | 用 NumPy 实现 MLP 层、激活、欧氏损失和 momentum/weight decay；比较一/两隐层及 ReLU/Sigmoid | [HW1 批改标准](hw/2018/HW1批改标准_536601614.pdf) |
| HW2 | 实现 Conv2D、AvgPool2D、SoftmaxCrossEntropyLoss 及反向传播；构造 CNN 与 MLP 对比 | [HW2 批改标准](hw/2018/HW2-批改标准_36600685.pdf)、[示例压缩包](hw/2018/HW2_136408023.zip) |
| HW3 | 在框架中实现 Batch Normalization、Dropout，并比较 MLP/CNN 的训练与推理 | [批改标准和测试程序](hw/2018/HW3批改标准和测试程序_295104010.zip) |
| HW4 | 实现 GRU/LSTM cell、双向 RNN、自注意力和惩罚项，用于文本分类 | [HW4 批改标准](hw/2018/HW4-批改标准1119_480806211.pdf) |

[hw/readme.md](hw/readme.md)保留了一个历史代码仓库线索；它不是当前目录的一部分，也不能替代独立实现和本地测试。

## 🔗 推荐学习顺序

~~~mermaid
flowchart LR
    accTitle: 人工神经网络学习顺序
    accDescr: 从张量与梯度开始，依次实现 MLP、优化器、CNN、正则化、循环单元和注意力，最后完成独立实验。
    tensor_gradient[张量 计算图与梯度] --> mlp_layers[MLP 层与激活]
    mlp_layers --> optimization[损失 优化与初始化]
    optimization --> convolution[CNN 卷积与池化]
    convolution --> regularization[Dropout 与 BatchNorm]
    regularization --> recurrent_cells[RNN GRU 与 LSTM]
    recurrent_cells --> attention[双向网络与注意力]
    attention --> independent_project[消融 复现与独立项目]
~~~

## ⚙️ 实现与验证主线

### 基础层与损失

每个层都保持统一接口：forward 保存反向所需状态，backward 接收上游梯度并返回输入梯度；可训练层还要计算参数梯度。先用极小张量手算，再用有限差分检查 Linear、卷积和损失。

### 卷积网络

明确输入、卷积核和输出的 NCHW 形状，逐项验证 padding、stride 和 bias。HW2 的测试关注 forward 与 backward 是否同时正确；只得到可训练的 loss 曲线不能证明卷积梯度正确。

### 正则化与序列模型

Dropout 在推理时必须关闭，BatchNorm 要区分 batch 统计和运行统计。RNN 作业应逐门检查 GRU/LSTM 公式，再验证变长序列、双向拼接、attention softmax 维度和 Frobenius 惩罚。

## 🔍 实验方法

1. 在训练前打印输入、标签、输出和每层参数的形状。
2. 用单样本和小 batch 做数值梯度检查。
3. 保存随机种子、数据划分、初始化、超参数和软件版本。
4. 同时绘制 train/validation loss 与 accuracy，检查过拟合和训练不稳定。
5. 比较模型时固定数据与训练预算，并同时报告参数量和运行时间。
6. 对 BatchNorm、Dropout、cell 类型和 attention 分别做消融，不一次改变多个因素。
7. 最终报告失败实验、边界条件和复现命令，而不只展示最好结果。

## ⚠️ 归档与环境说明

- HW3/HW4 代码明显使用 Session、placeholder、tf.app.flags 等旧式 TensorFlow API，当前版本可能不直接兼容；建议在隔离环境中锁定旧依赖。
- 两个 zip 是提交/测试归档，不是完整统一的课程代码库；解压时保留目录层次并检查重复的 macOS 元数据。
- HW1 只有批改标准，当前目录未附完整学生源码；不能据评分代码片段假定所有脚手架都存在。
- 评分标准中的准确率区间只用于历史验收，不是通用模型性能目标。
- 原 README 提到 Final Project，但本目录缺少题目、数据和报告；只能把“自主选题”视为归档经验。
- 所有作业应在副本中复现，保留本目录压缩包和标准原样。

## ✅ 完成标准

完成本项目后，学生应能够：

1. 从零实现 MLP 的 forward、backward、损失和带 momentum/weight decay 的更新。
2. 用数值梯度验证 Linear、卷积、池化和 Softmax 交叉熵。
3. 构造并公平比较 MLP 与 CNN，解释结构、参数和效果差异。
4. 正确实现 Dropout/BatchNorm 的训练与推理语义。
5. 推导并实现 Vanilla RNN、GRU、LSTM，正确处理变长序列。
6. 实现双向 RNN 与 self-attention，并检查注意力归一化和惩罚项。
7. 独立设计一组消融实验，交付可复现代码、曲线、结果和错误分析。
