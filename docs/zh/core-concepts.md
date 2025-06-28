# 🧠 核心概念

学习 agnflow 的基本概念。

## 🔧 节点类型

### 🔧 基础节点

节点是工作流的基本构建块：

```python
from agnflow import Node

# 同步节点
sync_node = Node("sync", exec=lambda state: {"result": "done"})

# 异步节点
async def async_func(state):
    await asyncio.sleep(1)
    return {"result": "async done"}

async_node = Node("async", aexec=async_func)
```

### 🎯 特殊节点类型

#### 🌊 工作流节点
可以包含其他节点的容器节点：

```python
from agnflow import Flow

# 创建工作流容器
flow = Flow()
flow[node1, node2, node3]

# 或者使用初始节点创建
flow = Flow(node1 >> node2 >> node3)
```

#### 🤖 蜂群节点
用于多智能体协调的特殊节点：

```python
from agnflow import Swarm, Supervisor

# 蜂群 - 所有节点相互连接
swarm = Swarm[node1, node2, node3]

# 监督者 - 第一个节点监督其他节点
supervisor = Supervisor[supervisor_node, worker1, worker2]
```

## 🔗 连接模式

### ➡️ 线性连接

```python
# 前向链接
a >> b >> c

# 反向链接
c << b << a
```

### 🔀 分支连接

```python
# 并行分支
a >> [b, c] >> d

# 条件分支
a >> (b if condition else c) >> d
```

### 🔄 循环连接

```python
# 简单循环
a >> b >> a

# 条件循环
a >> b >> (a if not_done else c)
```

## 🔄 运行时动态管理

### ➕ 添加节点

```python
# 添加单个节点
flow += new_node

# 使用括号语法添加
flow[new_node]

# 添加多个节点
flow += [node1, node2, node3]
```

### ➖ 移除节点

```python
# 移除单个节点
flow -= old_node

# 移除多个节点
flow -= [node1, node2]
```

### 🔗 对称操作

```python
# 构建连接
a >> b >> c
a >> [b, c]

# 对称断开
a - b - c
a - [b, c]
```

## 💾 状态管理

### 🌊 状态流

状态在节点间流动并可以被修改：

```python
def process_node(state):
    # 修改状态
    state["processed"] = True
    state["timestamp"] = time.time()
    return state

node = Node("process", exec=process_node)
```

### 💾 状态持久化

状态在节点间自动传递：

```python
# 初始状态
initial_state = {"data": "hello", "step": 0}

# 状态在节点间流动
node1 = Node("step1", exec=lambda s: {**s, "step": s["step"] + 1})
node2 = Node("step2", exec=lambda s: {**s, "step": s["step"] + 1})

flow = Flow(node1 >> node2)
result = flow.run(initial_state)
# result: {"data": "hello", "step": 2}
```

## 🎮 执行控制

### 🚪 入口点

控制执行从哪里开始：

```python
# 从特定节点开始
flow.run(state, entry_action="node_name")

# 从第一个节点开始（默认）
flow.run(state)
```

### ⏱️ 执行限制

```python
# 限制执行步数
flow.run(state, max_steps=10)

# 异步执行限制
await flow.arun(state, max_steps=10)
```

## 🎨 可视化

### 📊 Mermaid 流程图

```python
# 生成 Mermaid 代码
mermaid = flow.render_mermaid()

# 保存为图片
flow.render_mermaid(saved_file="workflow.png", title="My Workflow")
```

### 🔷 DOT 流程图

```python
# 生成 DOT 代码
dot = flow.render_dot()

# 保存为图片
flow.render_dot(saved_file="workflow.png")
```

## 高级模式

### 人机交互 (HITL)

```python
from agnflow.agent.hitl.cli import human_in_the_loop

def review_node(state):
    result, approved = human_in_the_loop(
        "请审查这些数据", 
        input_data=state
    )
    if approved:
        return {"reviewed": True, "result": result}
    else:
        return "exit", {"reviewed": False}

review = Node("review", exec=review_node)
```

### 错误处理

```python
def robust_node(state):
    try:
        # 您的逻辑
        return {"success": True}
    except Exception as e:
        return "error", {"error": str(e)}

node = Node("robust", exec=robust_node)
```

### 条件执行

```python
def conditional_node(state):
    if state.get("condition"):
        return "branch_a"
    else:
        return "branch_b"

node = Node("conditional", exec=conditional_node)
``` 