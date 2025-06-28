# 🚀 Welcome to agnflow

**⚡ Efficient Python Agent Workflow Engine**

agnflow is a lightweight, high-performance Python library for building intelligent agent workflows. With its minimalist syntax and powerful features, you can create complex agent systems in just a few lines of code.

## 🎯 Key Features

### ⚡ **Minimalist Syntax**
Build agent workflows in 5 lines of code with intuitive operators.

### 🎨 **Auto Visual Flowcharts**
Generate beautiful flowcharts automatically with one line of code.

### 🔄 **Runtime Dynamic Management**
Add or remove nodes at runtime with symmetric connection/disconnection syntax.

### 🚀 **Advanced Flow Control**
Support sync/async mixed execution, branching, looping, and swarm agents.

## 🚀 Quick Start

```python
from agnflow import Node, Flow

# Define nodes
greet = Node("Greet", exec=lambda state: {"message": "Hello!"})
respond = Node("Respond", exec=lambda state: print(state["message"]))

# Build and run workflow
flow = Flow(greet >> respond)
flow.run({"data": "hello"})
```

## 📚 Learning Path

- **[🚀 Getting Started](getting-started.md)** - Learn the basics in minutes
- **[🧠 Core Concepts](core-concepts.md)** - Understand the fundamental concepts
- **[�� API Reference](api-reference.md)** - Complete API documentation
- **[💡 Examples](examples.md)** - Ready-to-run examples

## 🎯 Why agnflow?
- **⚡ Lightweight**: Core code only hundreds of lines
- **🎨 Visual**: Auto-generate beautiful flowcharts
- **🔄 Dynamic**: Add/remove nodes at runtime
- **🤖 Agent-Friendly**: Native LLM integration support
- **🚀 Fast**: Minimal overhead, maximum performance 
