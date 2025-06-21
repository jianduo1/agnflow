# API 参考

本页提供 `agnflow` 主要类的 API 参考。

## `Flow` 类

`Flow` 类用于构建和执行工作流。

### `__init__(self, start_node: Node, name: str = "flow")`

初始化一个工作流。

- **`start_node`**: 工作流的起始节点。
- **`name`**: (可选) 工作流的名称。

### `run(self, initial_state: dict = None) -> dict`

同步执行工作流。

- **`initial_state`**: (可选) 工作流的初始状态字典。
- **返回**: 工作流执行完毕后的最终状态。

### `arun(self, initial_state: dict = None) -> dict`

异步执行工作流。

- **`initial_state`**: (可选) 工作流的初始状态字典。
- **返回**: 工作流执行完毕后的最终状态。

### `render_dot(self, saved_file: str = None) -> str`

将工作流渲染为 `dot` 格式。

- **`saved_file`**: (可选) 图片保存路径。如果提供，将生成图片文件。
- **返回**: `dot` 语言描述的字符串。

### `render_mermaid(self, saved_file: str = None) -> str`

将工作流渲染为 `mermaid` 格式。

- **`saved_file`**: (可选) 图片保存路径。如果提供，将生成图片文件。
- **返回**: `mermaid` 语言描述的字符串。

---

## `Node` 类

`Node` 类是工作流中的基本执行单元。

### `__init__(self, name: str, exec: callable = None, aexec: callable = None, max_retries: int = 0, wait: int = 0)`

初始化一个节点。

- **`name`**: 节点的唯一名称。
- **`exec`**: (可选) 节点的同步执行函数。
- **`aexec`**: (可选) 节点的异步执行函数。
- **`max_retries`**: (可选) 失败后的最大重试次数。
- **`wait`**: (可选) 每次重试之间的等待秒数。

### `__rshift__(self, other)`

定义节点连接，例如 `n1 >> n2`。

### 节点执行函数

#### 输入参数

`agnflow` 会根据函数签名自动从状态字典中注入参数。

```python
# 接收整个状态
def my_node(state: dict):
    ...

# 按名称接收特定参数
def my_node(user_id, message):
    ...
```

#### 返回值

函数的返回值会更新状态，并决定下一个执行的节点。

```python
# 方式1: 只返回新状态 (字典)
def my_node(state):
    return {"new_data": "value"}

# 方式2: 返回 action 和新状态 (元组)
def my_node(state):
    if state.get("condition"):
        return "success", {"result": "ok"}
    return "error", {"result": "fail"}

# 方式3: 只返回 action (字符串)
def my_node(state):
    return "next_step"

# 方式4: 返回 None
# 将结束整个工作流
def my_node(state):
    return None
``` 