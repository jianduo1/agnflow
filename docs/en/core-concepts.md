# 🧠 Core Concepts

Learn the fundamental concepts of agnflow.

## 🔧 Node Types

### 🔧 Basic Nodes

Nodes are the fundamental building blocks of workflows:

```python
from agnflow import Node

# Synchronous node
sync_node = Node("sync", exec=lambda state: {"result": "done"})

# Asynchronous node
async def async_func(state):
    await asyncio.sleep(1)
    return {"result": "async done"}

async_node = Node("async", aexec=async_func)
```

### 🎯 Special Node Types

#### 🌊 Flow Nodes
Container nodes that can hold other nodes:

```python
from agnflow import Flow

# Create a flow container
flow = Flow()
flow[node1, node2, node3]

# Or create with initial nodes
flow = Flow(node1 >> node2 >> node3)
```

#### 🤖 Swarm Nodes
Special nodes for multi-agent coordination:

```python
from agnflow import Swarm, Supervisor

# Swarm - all nodes connected to each other
swarm = Swarm[node1, node2, node3]

# Supervisor - first node supervises others
supervisor = Supervisor[supervisor_node, worker1, worker2]
```

## 🔗 Connection Patterns

### ➡️ Linear Connections

```python
# Forward chaining
a >> b >> c

# Reverse chaining
c << b << a
```

### 🔀 Branching Connections

```python
# Parallel branching
a >> [b, c] >> d

# Conditional branching
a >> (b if condition else c) >> d
```

### 🔄 Looping Connections

```python
# Simple loop
a >> b >> a

# Loop with condition
a >> b >> (a if not_done else c)
```

## 🔄 Runtime Dynamic Management

### ➕ Adding Nodes

```python
# Add single node
flow += new_node

# Add using bracket syntax
flow[new_node]

# Add multiple nodes
flow += [node1, node2, node3]
```

### ➖ Removing Nodes

```python
# Remove single node
flow -= old_node

# Remove multiple nodes
flow -= [node1, node2]
```

### 🔗 Symmetric Operations

```python
# Build connections
a >> b >> c
a >> [b, c]

# Disconnect symmetrically
a - b - c
a - [b, c]
```

## 💾 State Management

### 🌊 State Flow

State flows through nodes and can be modified:

```python
def process_node(state):
    # Modify state
    state["processed"] = True
    state["timestamp"] = time.time()
    return state

node = Node("process", exec=process_node)
```

### 💾 State Persistence

State is automatically passed between nodes:

```python
# Initial state
initial_state = {"data": "hello", "step": 0}

# State flows through nodes
node1 = Node("step1", exec=lambda s: {**s, "step": s["step"] + 1})
node2 = Node("step2", exec=lambda s: {**s, "step": s["step"] + 1})

flow = Flow(node1 >> node2)
result = flow.run(initial_state)
# result: {"data": "hello", "step": 2}
```

## 🎮 Execution Control

### 🚪 Entry Points

Control where execution starts:

```python
# Start from specific node
flow.run(state, entry_action="node_name")

# Start from first node (default)
flow.run(state)
```

### ⏱️ Execution Limits

```python
# Limit execution steps
flow.run(state, max_steps=10)

# Async execution with limits
await flow.arun(state, max_steps=10)
```

## 🎨 Visualization

### 📊 Mermaid Flowcharts

```python
# Generate Mermaid code
mermaid = flow.render_mermaid()

# Save as image
flow.render_mermaid(saved_file="workflow.png", title="My Workflow")
```

### 🔷 DOT Flowcharts

```python
# Generate DOT code
dot = flow.render_dot()

# Save as image
flow.render_dot(saved_file="workflow.png")
```

## Advanced Patterns

### Human-in-the-Loop (HITL)

```python
from agnflow.agent.hitl.cli import human_in_the_loop

def review_node(state):
    result, approved = human_in_the_loop(
        "Please review this data", 
        input_data=state
    )
    if approved:
        return {"reviewed": True, "result": result}
    else:
        return "exit", {"reviewed": False}

review = Node("review", exec=review_node)
```

### Error Handling

```python
def robust_node(state):
    try:
        # Your logic here
        return {"success": True}
    except Exception as e:
        return "error", {"error": str(e)}

node = Node("robust", exec=robust_node)
```

### Conditional Execution

```python
def conditional_node(state):
    if state.get("condition"):
        return "branch_a"
    else:
        return "branch_b"

node = Node("conditional", exec=conditional_node)
``` 