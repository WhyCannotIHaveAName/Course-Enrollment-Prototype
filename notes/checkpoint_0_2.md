你的第一轮完成得很好，五道题全部正确。尤其是：

- 第 2 题意识到不变量与“检查时刻”有关；
- 第 4 题抓住了验收标准必须可观察、可量化；
- 第 5 题正确区分了“现实规则未知”和“原型自行作出的决定”。

我已审阅 [docs/requirements.md](C:\Users\sq8032004\Desktop\Course-Enrollment-Prototype\docs\requirements.md)，没有修改你的文字。

## 一、这份初稿做得好的地方

你已经完成了几个真正的需求分析动作：

- 明确列出了第一版范围和非目标；
- 区分了 Course、Section 和 Enrollment；
- 没有假装掌握所有 GC 规则；
- 记录了 Waitlist、扩容和 Override 等开放问题；
- 正确描述了 Lucky Draw 的“选入篮子—提交—抽签”过程；
- 意识到 Early Bird 与 Lucky Draw 的操作方式不同。

现在的问题不是内容太少，而是部分术语还承担了多个不同含义。我们先把这些概念拆开。

---

# 第 0.2 课：请求、提交与成功选课不是同一个状态

## 1. 为什么不能把它们都叫 Enrollment？

你在文档中把 `Enrollment` 定义为“学生成功加入某教学班”。这个方向是正确的。

但一次选课可能经历以下状态：

```text
学生点击按钮
    ↓
系统接受请求
    ↓
请求进入等待或抽签状态
    ↓
系统作出决定
    ↓
学生最终成功选上
```

只有最后一步才应该产生 Enrollment。

否则我们会遇到一个问题：

> Lucky Draw 中有 100 人提交了一门容量为 30 的课。抽签前究竟有 100 个 Enrollment，还是 0 个？

如果 Enrollment 表示“已经成功选上”，那么抽签前应该是 0；抽签完成后最多是 30。

因此需要区分至少三个概念：

### Choice：尚未提交的选择

学生把 Section 放入选课篮，但仍然可以修改。

它类似购物车里的商品，不代表订单已经提交。

### Submission：正式提交的抽签申请

学生点击 Submit 后形成的申请快照。

它表示：

> 请使用这组选择参加本轮 Lucky Draw。

它仍然不代表成功选课。

### Enrollment：最终有效的选课关系

学生最终成功进入某个 Section 后，才生成 Enrollment。

因此 Lucky Draw 的基本流程是：

```text
Choice
  ↓ Submit
Submission
  ↓ 抽签
Enrollment 或 Not Selected
```

Early Bird 的流程更短：

```text
Sign-up Request
      ↓ 检查与并发处理
Enrollment 或 Rejected
```

这两个流程最后都能产生 Enrollment，但产生 Enrollment 之前的状态不同。

---

## 2. 你发现了一个很重要的学分问题

你提供的真实观察是：

1. Lucky Draw 添加课程时检查时间冲突和学分上限；
2. 点击 Submit 时检查学分下限；
3. 抽签完成后，学生未必获得全部提交的课程；
4. 所以最终成功课程的学分可能低于下限。

例如：

```text
提交：课程 1、2、3，共 12 学分
抽签：只抽中课程 1、3，共 8 学分
```

这意味着：

```text
Lucky Draw 提交时学分 >= 12
```

可能是一个**提交条件**，但不能直接写成：

```text
任何时刻最终 Enrollment 的学分都必须 >= 12
```

否则系统自己的抽签结果就可能违反这个不变量。

这是需求分析里非常有价值的发现：

> “输入时检查的条件”不一定是“系统最终状态永远满足的不变量”。

因此，我们暂时应这样记录：

- **已观察到**：Lucky Draw 在 Submit 时执行学分下限检查；
- **已观察到**：抽签后最终获得的学分可能低于下限；
- **尚不确定**：现实系统之后如何处理低于下限的学生；
- **原型待决定**：我们是否仅在提交时检查下限，而允许抽签结果低于下限。

先记录事实，不急着替现实系统补出一个不存在的规则。

---

## 3. 当前用例里有一个状态错误

在 [UC-01](C:\Users\sq8032004\Desktop\Course-Enrollment-Prototype\docs\requirements.md:87) 中，你写道：

> 进入选课篮（Lucky Draw）或录取序列（Early Bird），该教学班已录取人数加 1。

这对 Early Bird 的成功结果可能成立，但对 Lucky Draw 不成立。

Lucky Draw 中：

- 加入选课篮：已录取人数不变；
- 点击 Submit：已录取人数仍然不变；
- 抽签成功：已录取人数才增加；
- 抽签失败：不产生 Enrollment。

因此不能让两个模式共用这一个结果。它们需要拆成不同用例。

---

## 4. “进入序列”也需要谨慎描述

你观察到 Early Bird 点击 Sign Up 后会进入抢课处理流程，但我们目前不知道后台究竟采用：

- 数据库锁；
- 普通请求并发；
- 消息队列；
- 单线程顺序处理；
- 或者其他机制。

因此，需求文档可以写：

> 系统接收并处理 Sign Up 请求；成功时创建 Enrollment。

暂时不要把后台实现写成已经确认的“队列”或“录取序列”。

“使用队列串行处理”属于未来可以比较的架构方案，不是已经确认的现实规则。

---

## 5. “管理员发起选课”存在歧义

[参与者定义](C:\Users\sq8032004\Desktop\Course-Enrollment-Prototype\docs\requirements.md:36) 中的：

> 管理员可以发起选课

可能有两种意思：

1. 管理员替某个学生选课；
2. 管理员创建并启动一轮选课活动。

根据你刚才的描述，你主要表达的是第二种。

建议以后使用更明确的词：

- **选课操作**：学生申请某个 Section；
- **选课轮次**：某段时间开放的 Lucky Draw 或 Early Bird；
- **启动选课轮次**：管理员使某轮选课进入开放状态。

这引出了一个新术语：

### Enrollment Round

一次具有开始时间、结束时间、模式和适用学生范围的选课活动。

例如：

```text
名称：Lucky Draw 1
模式：Lucky Draw
适用范围：非大一学生
状态：Open
开始时间：……
结束时间：……
```

你的简化建议很好：原型不必把五轮流程硬编码成自动序列。可以让管理员分别创建并启动 Enrollment Round。

这样，同一个系统既可以表达：

- Lucky Draw 1；
- Lucky Draw 2；
- Freshmen Lucky Draw；
- Early Bird 1；
- Early Bird 2；

又不需要为这五个名称分别写五套程序。

这是一种很常见的设计思想：

> 把相似的现实流程抽象成同一种可配置对象。

是否采用它仍需由你最终决定。

---

## 6. 其他需要修正但不着急扩写的地方

### Course 与完成课程

[Course 定义](C:\Users\sq8032004\Desktop\Course-Enrollment-Prototype\docs\requirements.md:42) 中写道：

> 已经修读过某课程的学生不能再次修读这门课。

这可能适合作为原型规则，但我们暂时不能把它写成普遍事实，因为现实中可能存在：

- 重修；
- 刷分；
- 可重复修读课程；
- 特殊批准。

可以保留，但应标为“原型设定”。

### Section 与获得学分

[Section 定义](C:\Users\sq8032004\Desktop\Course-Enrollment-Prototype\docs\requirements.md:48) 中写道，进入教学班就“获得学分”。

严格来说，选上课程并不等于已经获得学分。学生通常需要完成课程并取得成绩。

本原型不处理成绩，因此更准确的是：

> 成功选入任一 Section 后，该 Course 的学分计入本学期选课学分。

### Drop 时检查先修课

[退课用例](C:\Users\sq8032004\Desktop\Course-Enrollment-Prototype\docs\requirements.md:94) 中写了退课时检查先修条件。

如果我们不实现 Co-requisite，单纯退掉一门当前课程通常不会改变学生过去已经完成的先修课程。这里暂时只需保留学分下限检查，并将它标为“现实规则尚不确定”。

### Capacity 拼写

`capicity` 应改为 `capacity`。

概念上也可以写得更准确：

```text
active enrollment count <= section capacity
```

因为抽签申请、购物篮选择和候补记录都不应算作已经录取的人数。

---

# 本轮小测验

## 问题 1

某门 Section 容量为 30，共有 50 名学生把它加入 Lucky Draw 选课篮，但没有人点击 Submit。

此时：

- Choice 有多少个？
- Submission 有多少个？
- Enrollment 有多少个？

## 问题 2

50 人正式提交抽签申请，最终 30 人抽中。

抽签结束后：

- Submission 可以有多少个？
- Enrollment 最多有多少个？
- 哪一个数量必须受 `capacity = 30` 约束？

## 问题 3

某学生提交了 12 学分的 Lucky Draw 选择，最终只抽中 8 学分。

这是否一定违反了系统不变量？请结合“检查时刻”回答。

## 问题 4

管理员把一个 Section 的容量从 30 增加到 35，这更接近：

A. 学生 Override  
B. 修改 Section 配置  
C. Lucky Draw Submission

这个操作是否需要审计？为什么？

## 问题 5

“系统使用数据库队列按照请求到达顺序处理 Early Bird”属于：

A. 已确认业务规则  
B. 架构方案  
C. 核心不变量

---

# 本轮任务

这次不要试图补完整份文档，只修改概念和流程部分。

## 任务一：修正术语

修改以下内容：

1. 修正 Course 中“获得学分”的表述；
2. 将 Enrollment 定义为最终有效的选课关系；
3. 新增 `Enrollment Round`；
4. 新增 `Choice`；
5. 新增 `Submission`；
6. 明确管理员“发起选课”是创建或启动选课轮次；
7. 把“已修过课程不能重修”标为原型规则，而不是现实确认规则。

## 任务二：拆分用例

建议先调整为：

```text
UC-01：学生将 Section 加入 Lucky Draw 选课篮
UC-02：学生提交 Lucky Draw 申请
UC-03：系统执行 Lucky Draw
UC-04：学生提交 Early Bird Sign-up
UC-05：学生退课
UC-06：管理员处理 Override
```

每个用例只需要先写：

```text
参与者：
前置条件：
主要流程：
成功结果：
失败结果：
```

本轮只要求完整写出 `UC-01` 至 `UC-04`。退课和 Override 可以暂时留空。

## 任务三：暂缓业务规则表

先不要急着填 BR-01。等这些状态分清之后，我们下一课再把自然语言流程提炼成：

- 业务规则；
- 不变量；
- Given–When–Then 验收标准。

## 提示强度

这次我给的是一级到二级之间的提示。关键内容——每个用例到底什么时候产生 Choice、Submission 或 Enrollment——由你自己写。

完成后，请把五道小测验的答案发给我，并告诉我已经修改文件。我会继续只做审阅，先不替你改。

1. 50,0,0；
2. 50,30，enrollment；
3. 不违反，因为学分下限的检查时刻是提交submission时（而不是enrollment确定时），在提交时确实符合大于等于12学分的要求；
4. 我认为这接近于B，但一个已经发布的选课轮次能否进行修改，这部分技术知识我目前不确定。需要审计，防止出现管理员偏袒舞弊行为。
5. B。