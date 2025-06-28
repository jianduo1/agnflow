# 🚀 快速开始

几分钟内上手 agnflow。

## 📦 安装

```bash
pip install agnflow
```

## 🎯 基本使用

### 1️⃣ 导入和创建节点

```python
from agnflow import Node, Flow

# 创建同步节点
greet = Node("Greet", exec=lambda state: {"message": "Hello, World!"})

# 创建异步节点
async def async_respond(state):
    await asyncio.sleep(1)
    print(state["message"])
    return {"status": "done"}

respond = Node("Respond", aexec=async_respond)
```

### 2️⃣ 连接节点

```python
# 线性连接
flow = Flow(greet >> respond)

# 或者逐步连接
flow = Flow()
flow.add_node(greet)
flow.add_node(respond)
greet >> respond
```

### 3️⃣ 运行工作流

```python
# 同步执行
state = {"data": "hello"}
result = flow.run(state)

# 异步执行
import asyncio
result = asyncio.run(flow.arun(state))
```

## 🧠 核心概念

### 🔧 节点

节点是工作流的构建块。每个节点可以：

- 执行同步或异步函数
- 处理和修改状态
- 返回影响下一个节点的结果

```python
# 同步节点
node = Node("name", exec=lambda state: {"key": "value"})

# 异步节点
node = Node("name", aexec=async_function)

# 带自定义名称的节点
node = Node("custom_name", exec=function)
```

### 🔗 连接

使用 `>>` 操作符连接节点：

```python
# 线性连接
a >> b >> c

# 分支
a >> [b, c] >> d

# 反向连接
c << b << a
```

### 🌊 工作流

工作流是管理节点及其连接的容器：

```python
# 使用节点创建工作流
flow = Flow(node1 >> node2 >> node3)

# 向现有工作流添加节点
flow += new_node
flow[another_node]

# 移除节点
flow -= node_to_remove
```

## 🚀 高级功能

### 🔄 运行时节点管理

在运行时添加或删除节点：

```python
# 添加节点
flow += new_node
flow[another_node]
flow += [node1, node2, node3]

# 删除节点
flow -= old_node
flow -= [node1, node2]
```

### 🔗 对称连接/断开

```python
# 构建连接
a >> b >> c
a >> [b, c]

# 对称断开
a - b - c
a - [b, c]
```

### 🎨 可视化流程图

生成精美的流程图：

```python
# 生成 Mermaid 格式
mermaid_code = flow.render_mermaid()

# 保存为图片
flow.render_mermaid(saved_file="workflow.png")

# 生成 DOT 格式
dot_code = flow.render_dot()
```

## 📚 下一步

- **[🧠 核心概念](core-concepts.md)** - 学习高级功能
- **[🔧 API 参考](api-reference.md)** - 完整 API 文档
- **[💡 示例](examples.md)** - 查看更多示例 