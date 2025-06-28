# 🚀 欢迎使用 agnflow

**⚡ 高效 Python 智能体工作流引擎**

agnflow 是一个轻量级、高性能的 Python 库，用于构建智能体工作流。凭借其极简的语法和强大的功能，您可以用几行代码创建复杂的智能体系统。

## 🎯 核心特性

### ⚡ **极简语法**
使用直观的操作符，5行代码构建智能体工作流。

### 🎨 **自动可视化流程图**
一行代码自动生成精美的流程图。

### 🔄 **运行时动态管理**
使用对称的连接/断开语法，在运行时添加或删除节点。

### 🚀 **高级流程控制**
支持同步/异步混合执行、分支、循环和蜂群智能体。

## 🚀 快速开始

```python
from agnflow import Node, Flow

# 定义节点
greet = Node("Greet", exec=lambda state: {"message": "Hello!"})
respond = Node("Respond", exec=lambda state: print(state["message"]))

# 构建并运行工作流
flow = Flow(greet >> respond)
flow.run({"data": "hello"})
```

## 📚 学习路径

- **[🚀 快速开始](getting-started.md)** - 几分钟内学习基础知识
- **[🧠 核心概念](core-concepts.md)** - 理解基本概念
- **[🔧 API 参考](api-reference.md)** - 完整的 API 文档
- **[💡 示例](examples.md)** - 即用示例

## 🎯 为什么选择 agnflow？

- **⚡ 轻量级** - 核心代码仅数百行
- **🎨 可视化** - 自动生成精美流程图
- **🔄 动态性** - 运行时动态增删节点
- **🤖 智能体友好** - 原生 LLM 集成支持
- **🚀 快速** - 最小开销，最大性能 