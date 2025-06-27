# 快速开始

本页将向您展示 `agnflow` 的核心功能。

## 1. 安装

从 PyPI 安装 `agnflow`:

```bash
pip install agnflow
```

## 2. 定义节点

节点是工作流的基本单元。您可以定义一个简单的 Python 函数作为节点的执行逻辑。

```python
from agnflow import Node

def say_hello(state):
    name = state.get("name", "World")
    print(f"Hello, {name}!")
    return {"message_said": True}

hello_node = Node("say_hello", exec=say_hello)
```

### 异步节点

对于 I/O 密集型任务，您可以使用异步函数：

```python
import asyncio

async def async_hello(state):
    await asyncio.sleep(1)
    print("Async Hello!")

async_node = Node("async_hello", aexec=async_hello)
```

## 3. 连接节点

使用 `>>` 操作符来定义节点间的执行顺序。

```python
# 线性连接
n1 >> n2 >> n3

# 分支连接
# 节点 "a" 的返回值将决定下一个节点是 "b" 还是 "c"
a >> [b, c]

# 循环
# 节点 "c" 的返回值如果是 "a"，则会回到节点 "a"
c >> a
```

## 4. 构建并运行工作流

将起始节点传入 `Flow` 来构建工作流。

### 同步运行

```python
from agnflow import Flow

flow = Flow(start_node, name="my_workflow")
final_state = flow.run(initial_state={"name": "Alice"})
print(final_state)
```

### 异步运行

```python
import asyncio

flow = Flow(start_async_node)
final_state = asyncio.run(flow.arun({}))
```

## 5. 渲染流程图

您可以轻松地将工作流可视化。

```python
# 输出 dot 语言描述
print(flow.render_dot())

# 保存为 PNG 图片 (需要安装 graphviz)
flow.render_dot(saved_file="./flow.png")
```

![示例流程图](https://raw.githubusercontent.com/jianduo1/agnflow/main/assets/flow_dot.png) 