# 欢迎来到 agnflow

**agnflow** 是一个简洁的 Python 智能体工作流引擎，支持同步与异步节点、分支、循环、流程图渲染。

它追求极简、易用、可扩展，适合快速原型、定制化 LLM 工作流、Agent 任务流等场景。

## 功能特性

- **节点式工作流**：支持分支、循环、子流程
- **同步与异步**：支持同步与异步执行
- **流程图渲染**：支持 `dot` 和 `mermaid` 格式
- **代码简洁**：易于理解和扩展

## 快速开始

只需几行代码即可定义并运行一个工作流：

```python
from agnflow import Node, Flow

# 1. 定义节点
def hello_exec(state):
    print("hello", state)
    return {"msg": "world"}

def world_exec(state):
    print("world", state)

n1 = Node("hello", exec=hello_exec)
n2 = Node("world", exec=world_exec)

# 2. 连接节点
n1 >> n2

# 3. 构建并运行
flow = Flow(n1, name="demo")
flow.run({"msg": "hi"})
```

## 接下来

- 查看 [快速开始](getting-started.md) 页面了解更多使用方法。
- 深入 [API 参考](api.md) 了解 `Node` 和 `Flow` 的所有功能。 