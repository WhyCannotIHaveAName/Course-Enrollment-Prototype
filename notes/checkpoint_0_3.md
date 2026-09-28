需求文档已经整理为精简版本：[docs/requirements.md](C:\Users\sq8032004\Desktop\Course-Enrollment-Prototype\docs\requirements.md)。

现在文档只保留：

- 项目范围；
- 规则可信度；
- 核心术语；
- Lucky Draw、Early Bird 和 Drop 的状态变化；
- 第一版业务规则；
- 核心不变量；
- 尚未确定的问题。

重复的详细用例已删除。`git diff --check` 通过，我没有改动你的 `notes/` 文件。

# 第 0.3 课：技术栈是什么？

## 1. “技术栈”不是一种技术

技术栈是完成一个软件项目所使用的一组技术。

可以把我们的系统分成几层：

```text
学生或管理员发出 HTTP 请求
             ↓
FastAPI 接收并解析请求
             ↓
应用服务组织选课流程
             ↓
规则检查器判断是否允许
             ↓
SQLAlchemy 读写数据
             ↓
PostgreSQL 保存数据并执行事务
```

旁边还有一些辅助工具：

```text
Alembic        管理数据库结构变化
pytest         自动检查代码是否正确
Docker Compose 启动统一的数据库和应用环境
GitHub Actions 在每次提交后自动运行检查
Locust         模拟大量学生同时请求
```

每种工具只承担一部分责任。使用 FastAPI 并不会自动防止超选；最终仍需要我们的业务代码、数据库事务和约束共同保证正确性。

---

## 2. Python：编写程序的语言

Python 是我们直接阅读和编写的代码。

例如：

```python
def has_available_seat(enrolled: int, capacity: int) -> bool:
    return enrolled < capacity
```

选择 Python 的主要原因：

- 语法相对容易阅读；
- 适合学习后端、测试和算法；
- FastAPI、SQLAlchemy、pytest、Locust 都能使用 Python；
- 可以把更多精力放在选课规则与并发，而不是语言细节上。

它的代价是：Python 不是追求最高原始性能的语言。但这个项目的重点是数据库事务、请求竞争和正确性，因此这不是主要问题。

### 本机状态

你的电脑实际安装了 Python 3.13.5：

```text
C:\Users\sq8032004\AppData\Local\Programs\Python\Python313\python.exe
```

只是 `python` 和 `py` 命令入口没有正确配置。`pip` 可以找到该安装。

当前 FastAPI、SQLAlchemy、Alembic 和 pytest 的官方包信息均列出了 Python 3.13 支持，因此可以使用现有的 3.13.5，不必为了本项目另装旧版 Python。[FastAPI](https://pypi.org/project/fastapi/)、[SQLAlchemy](https://pypi.org/project/SQLAlchemy/)、[Alembic](https://pypi.org/project/alembic/)、[pytest](https://pypi.org/project/pytest/)

---

## 3. FastAPI：HTTP 接口层

用户不会直接调用 Python 函数，而是通过网络发送请求，例如：

```text
POST /sections/42/sign-up
GET  /requests/abc123
POST /lucky-draw/submissions
```

FastAPI 的任务是：

- 接收 HTTP 请求；
- 检查输入格式；
- 调用我们的业务代码；
- 把结果转换成 HTTP 响应；
- 根据代码生成可交互的 API 文档。

一个最小接口可能长这样：

```python
@app.get("/health")
def health():
    return {"status": "ok"}
```

其中：

- `GET` 是读取信息时常用的 HTTP 方法；
- `/health` 是访问路径；
- 函数返回的字典会被转换成 JSON。

FastAPI 不负责决定学生能不能选课。它只负责让外部请求进入系统，并把结果送回去。

---

## 4. PostgreSQL：真正保存系统状态的数据库

PostgreSQL 保存：

- 学生；
- Course；
- Section；
- Enrollment Round；
- Choice；
- Submission；
- Enrollment；
- Override；
- Audit Log。

我们选择 PostgreSQL，而不是只使用 SQLite，最重要的原因不是“它更高级”，而是它提供了我们需要学习和实验的能力：

- 数据库事务；
- 行锁；
- 并发请求；
- 唯一约束；
- 外键；
- 不同事务隔离级别；
- 查询计划和锁等待观察。

例如，两名学生同时争抢最后一个名额时，下面这种写法是不安全的：

```text
请求 A 读取：还剩 1 个名额
请求 B 读取：还剩 1 个名额
请求 A 创建 Enrollment
请求 B 创建 Enrollment
```

PostgreSQL 的事务和锁将帮助我们解决这个问题。

### 为什么不先用 SQLite？

SQLite 很适合小工具和简单测试，但它的并发与锁行为和 PostgreSQL 不同。如果开发时只在 SQLite 上验证，最重要的并发实验可能失真。

因此：

- 纯规则函数可以不连接数据库；
- 真正的集成测试和并发测试必须使用 PostgreSQL。

---

## 5. SQLAlchemy：Python 与数据库之间的工具

如果没有 SQLAlchemy，我们可能直接写：

```sql
SELECT * FROM enrollments WHERE student_id = 123;
```

使用 SQLAlchemy 后，可以通过 Python 对象和查询表达式操作数据。

它通常被称为 ORM：

> Object-Relational Mapping，即“对象—关系映射”。

简化理解：

```text
Python 中的 Enrollment 对象
            ↕
数据库中的 enrollments 表和记录
```

SQLAlchemy 帮助我们：

- 定义表与关系；
- 执行查询；
- 管理事务；
- 减少重复的数据库连接代码。

但它不会替我们理解数据库。我们仍然要学习：

- 什么是主键；
- 什么是外键；
- 什么是唯一约束；
- 什么时候开始和提交事务；
- 查询最终生成了什么 SQL。

官方 SQLAlchemy 说明也强调：事务边界需要由开发者明确决定，而不是 ORM 自动替开发者决定。[SQLAlchemy](https://pypi.org/project/SQLAlchemy/)

### 同步还是异步？

第一版建议使用**同步 SQLAlchemy**。

同步可以简单理解为：

> 发出数据库查询后，当前代码等待结果，再继续执行。

异步则允许等待数据库时处理其他任务，但会引入：

- `async` / `await`；
- 异步数据库驱动；
- 更复杂的事务边界；
- 更复杂的测试配置。

重要的是：

> 不使用异步，并不代表不能测试并发。

FastAPI 仍然可以同时处理多个请求，PostgreSQL 仍然会遇到真实事务竞争。我们要研究的是数据库正确性，不需要在第一天就增加异步复杂度。

---

## 6. Alembic：数据库结构的版本记录

假设第一天我们创建：

```text
students
courses
sections
```

后来增加：

```text
enrollments
```

再后来给 `sections` 增加：

```text
capacity
```

不能每次都删除数据库重新开始。Alembic 使用一系列迁移记录这些变化：

```text
迁移 001：创建 students 和 courses
迁移 002：创建 sections
迁移 003：给 sections 增加 capacity
```

它类似“数据库结构的 Git”，但并不完全等同于 Git。

Alembic 使我们能够：

- 从空数据库建立最新结构；
- 把旧结构升级为新结构；
- 必要时回滚某次结构变化；
- 让其他人在相同数据库结构上运行项目。

---

## 7. pytest：让代码自己证明行为

pytest 用来编写自动化测试。

例如：

```python
def test_section_with_free_seat_is_available():
    assert has_available_seat(enrolled=29, capacity=30) is True
```

这个测试表达了三个部分：

```text
输入：已录取 29，容量 30
操作：判断是否还有名额
预期：有名额
```

以后代码发生变化，pytest 会重新执行这个测试。若行为被意外破坏，它会立刻告诉我们。

我们将使用三类测试：

- **单元测试**：检查一个规则函数；
- **集成测试**：检查代码与真实 PostgreSQL 是否正确配合；
- **并发测试**：让多个请求同时竞争资源。

---

## 8. Docker Compose：统一运行环境

Docker 可以把应用和数据库放进相对独立、可重复的运行环境。

未来我们可以用一条命令启动：

```text
应用容器 + PostgreSQL 容器
```

它解决的是：

> 怎样让你、我、GitHub 和其他读者运行近似相同的环境？

它不解决业务正确性，也不会自动让系统更快。

当前电脑没有检测到 Docker。因此我们的安排可以是：

1. 先用现有 Python 创建最小 FastAPI 程序；
2. 在进入 PostgreSQL 数据模型之前安装并配置 Docker；
3. 再使用 Docker Compose 启动 PostgreSQL。

Docker 未安装不会阻止我们写第一段代码，但会阻止后面的真实 PostgreSQL 集成测试。

---

## 9. 其他工具暂时怎样选择？

我的第一版建议如下：

| 层次 | 选择 | 当前理由 |
|---|---|---|
| 编程语言 | Python 3.13 | 已安装，当前主要依赖支持 |
| Web 框架 | FastAPI | API 清晰、输入校验方便、自动生成文档 |
| 数据库 | PostgreSQL | 支持真实事务、约束和并发实验 |
| 数据库访问 | 同步 SQLAlchemy | 先降低复杂度，明确学习事务 |
| 数据库迁移 | Alembic | 可追踪 schema 变化 |
| 测试 | pytest | 与 Python 配合直接 |
| 虚拟环境 | Python `venv` | 内置工具，先不增加额外包管理器 |
| 包安装 | pip | 本机已有，第一阶段足够 |
| 数据库环境 | Docker Compose | 统一 PostgreSQL 运行环境 |
| 负载测试 | Locust | 继续使用 Python，减少语言切换 |
| 自动检查 | GitHub Actions | 每次提交自动运行测试 |
| 前端 | 暂不单独开发 | 先使用 FastAPI 自动 API 页面 |

`uv` 是另一种更现代、速度更快的 Python 项目和依赖管理工具，FastAPI 当前官方安装说明也优先展示它；但你的电脑尚未安装。第一版先用 Python 自带的 `venv` 和已有的 `pip`，能少学一个工具。[FastAPI 安装说明](https://pypi.org/project/fastapi/)

---

# 本轮小测验

### 问题 1

FastAPI、SQLAlchemy 和 PostgreSQL 分别负责什么？请各用一句话回答。

### 问题 2

如果 FastAPI 成功接收了两个同时到达的请求，它是否会自动保证最后一个名额不被两个人抢到？为什么？

### 问题 3

SQLAlchemy 是否意味着我们不需要学习 SQL 和数据库事务？为什么？

### 问题 4

Alembic 管理的是：

A. Python 源代码版本  
B. 数据库结构变化  
C. HTTP 请求顺序

### 问题 5

不使用 `async` 是否意味着系统无法处理并发请求？

### 问题 6

为什么核心并发集成测试不能只使用 SQLite？

---

# 讨论任务

请你回答：

1. 你是否接受上表中的初始技术栈？
2. 哪一项最难理解或最让你犹豫？
3. 你更希望第一段代码由哪种方式开始：

   - 我先演示一个最小 FastAPI 程序，你理解后自己重写；
   - 我只给结构和提示，由你从空文件开始写。

你回答后，我们进入这节课的编码部分：先修复项目内 Python 环境，不改系统全局设置，然后由你亲手完成第一个 `/health` 接口。

1. FastAPI让外部请求通过网络接入，再返回处理结果。SQLAlchemy是一个数据库，可以用来查询。PostgreSQL也是数据库。
2. 不能，FastAPI只负责数据的传入传出。
3. 不对，它只是封装了一部分功能。
4. B
5. 不对，应该有别的办法。
6. 不适合大规模并发实验。

我接受。说实话，我只能理解你的大概意思，整体架构对我来说有点太难了，我要慢慢学习。迄今为止我只知道Python，听说过SQL和API，其他几个都是第一次听，所以你说的很多东西我都觉得很难理解。我认为你应该先帮我配环境，然后开始写代码。写代码时，你应该先给讲解和示例，最好让我从空白文件开始写（当然你可以给提示），直到我写不下去了让你帮忙。