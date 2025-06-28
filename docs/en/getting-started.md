# 🚀 Getting Started

Get up and running with agnflow in minutes.

## 📦 Installation

```bash
pip install agnflow
```

## 🎯 Basic Usage

### 1️⃣ Import and Create Nodes

```python
from agnflow import Node, Flow

# Create a synchronous node
greet = Node("Greet", exec=lambda state: {"message": "Hello, World!"})

# Create an asynchronous node
async def async_respond(state):
    await asyncio.sleep(1)
    print(state["message"])
    return {"status": "done"}

respond = Node("Respond", aexec=async_respond)
```

### 2️⃣ Connect Nodes

```python
# Linear connection
flow = Flow(greet >> respond)

# Or connect step by step
flow = Flow()
flow.add_node(greet)
flow.add_node(respond)
greet >> respond
```

### 3️⃣ Run the Workflow

```python
# Synchronous execution
state = {"data": "hello"}
result = flow.run(state)

# Asynchronous execution
import asyncio
result = asyncio.run(flow.arun(state))
```

## 🧠 Core Concepts

### 🔧 Nodes

Nodes are the building blocks of your workflow. Each node can:

- Execute synchronous or asynchronous functions
- Process and modify state
- Return results that affect the next node

```python
# Synchronous node
node = Node("name", exec=lambda state: {"key": "value"})

# Asynchronous node
node = Node("name", aexec=async_function)

# Node with custom name
node = Node("custom_name", exec=function)
```

### 🔗 Connections

Connect nodes using the `>>` operator:

```python
# Linear connection
a >> b >> c

# Branching
a >> [b, c] >> d

# Reverse connection
c << b << a
```

### 🌊 Flows

Flows are containers that manage nodes and their connections:

```python
# Create flow with nodes
flow = Flow(node1 >> node2 >> node3)

# Add nodes to existing flow
flow += new_node
flow[another_node]

# Remove nodes
flow -= node_to_remove
```

## 🚀 Advanced Features

### 🔄 Runtime Node Management

Add or remove nodes at runtime:

```python
# Add nodes
flow += new_node
flow[another_node]
flow += [node1, node2, node3]

# Remove nodes
flow -= old_node
flow -= [node1, node2]
```

### 🔗 Symmetric Connection/Disconnection

```python
# Build connections
a >> b >> c
a >> [b, c]

# Disconnect symmetrically
a - b - c
a - [b, c]
```

### 🎨 Visual Flowcharts

Generate beautiful flowcharts:

```python
# Generate Mermaid format
mermaid_code = flow.render_mermaid()

# Save as image
flow.render_mermaid(saved_file="workflow.png")

# Generate DOT format
dot_code = flow.render_dot()
```

## 📚 Next Steps

- **[🧠 Core Concepts](core-concepts.md)** - Learn about advanced features
- **[🔧 API Reference](api.md)** - Complete API documentation
- **[💡 Examples](examples.md)** - See more examples 