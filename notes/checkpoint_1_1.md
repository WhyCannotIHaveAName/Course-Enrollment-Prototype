先纠正一个关键点：你的第 1 题有一半需要修正——PostgreSQL 才是数据库；SQLAlchemy 不是数据库，而是让 Python 与数据库交互的库。可以把 PostgreSQL 想成“仓库”，SQLAlchemy 是“仓库操作工具和翻译员”。其余答案方向正确；SQLite 的关键问题不是单纯“规模小”，而是它的并发和锁模型与 PostgreSQL 不同，无法忠实验证我们要研究的行锁与事务竞争。Python 开发环境已经配置完成，可以开始写第一段代码。

## 已完成的环境配置

仓库中新增了：

- [.gitignore](C:\Users\sq8032004\Desktop\Course-Enrollment-Prototype\.gitignore)
- [requirements.txt](C:\Users\sq8032004\Desktop\Course-Enrollment-Prototype\requirements.txt)
- [requirements-dev.txt](C:\Users\sq8032004\Desktop\Course-Enrollment-Prototype\requirements-dev.txt)
- `.venv/` 项目专属 Python 环境，已被 Git 忽略

已安装并验证：

- Python 3.13.5
- FastAPI 0.141.1
- SQLAlchemy 2.0.54
- Alembic 1.20.0
- psycopg 3.3.6
- pytest 9.1.1
- Ruff 0.16.9

`pip check` 的结果是：

```text
No broken requirements found.
```

也就是说，目前没有发现依赖冲突。

Docker Desktop 的下载安装长时间没有进度，因此我中止了这次安装。检查确认 Docker 没有进入已安装状态。它不影响我们编写第一个 FastAPI 程序；进入 PostgreSQL 阶段前再单独解决。

# 编码部分：第一个 HTTP 接口

我们的目标是：

```text
浏览器发送 GET /health
              ↓
FastAPI 调用 Python 函数
              ↓
返回 {"status": "ok"}
```

`/health` 通常叫作健康检查接口。它暂时不处理选课，只证明：

- Python 环境能运行；
- FastAPI 能启动；
- HTTP 请求能找到正确的函数；
- Python 返回值能转换成 JSON。

## 先看一个不同的示例

下面是 `/hello`，不是你要提交的 `/health`：

```python
from fastapi import FastAPI

app = FastAPI(title="Example")


@app.get("/hello")
def hello():
    return {"message": "hello"}
```

逐行解释：

```python
from fastapi import FastAPI
```

从安装好的 `fastapi` 包中导入 `FastAPI`。

```python
app = FastAPI(title="Example")
```

创建一个 FastAPI 应用对象。以后所有接口都会登记在这个 `app` 上。

```python
@app.get("/hello")
```

这叫装饰器。它告诉 FastAPI：

> 收到访问 `/hello` 的 GET 请求时，请调用下面的函数。

```python
def hello():
```

这是普通 Python 函数。函数名主要供代码内部使用，不是浏览器访问地址。

```python
return {"message": "hello"}
```

返回 Python 字典。FastAPI 会把它转换成 JSON：

```json
{"message": "hello"}
```

## 你的任务

请你自己创建：

```text
app/
├── __init__.py
└── main.py
```

`__init__.py` 暂时保持空白。它表示 `app` 目录是一个 Python 包。

在 `main.py` 中，从空白开始实现：

- 导入 `FastAPI`；
- 创建名为 `app` 的 FastAPI 应用；
- 应用标题为 `EnrollmentLab`；
- 注册 `GET /health`；
- 处理函数名由你决定；
- 返回：

```python
{"status": "ok"}
```

### 一级提示

你需要把示例中的三处内容换掉：

- 应用标题；
- URL 路径；
- 返回的字典。

不要直接增加数据库、测试或其他接口。

完成后告诉我。我会先读取你的代码，让你解释几个关键位置，然后帮你启动服务器验证。如果写不下去，可以直接说卡在哪一行，我会把提示提高到二级。