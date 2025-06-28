# 🔧 API Reference

Complete API documentation for agnflow.

## 🧩 Core Classes

### 🔧 Node

The fundamental building block of workflows.

```python
class Node:
    def __init__(self, name: str, exec=None, aexec=None, max_retries=1, wait=0)
```

**Parameters:**
- `name` (str): Node identifier
- `exec` (callable): Synchronous execution function
- `aexec` (callable): Asynchronous execution function
- `max_retries` (int): Maximum retry attempts, default 1
- `wait` (int): Retry interval in seconds, default 0

**Methods:**
- `run(state)`: Execute node synchronously
- `arun(state)`: Execute node asynchronously

### 🌊 Flow

Container for organizing and executing nodes.

```python
class Flow:
    def __init__(self, name: str = None)
```

**Parameters:**
- `name` (str): Flow name

**Methods:**
- `run(state, entry_action=None, max_steps=None)`: Execute flow synchronously
- `arun(state, entry_action=None, max_steps=None)`: Execute flow asynchronously
- `render_mermaid(saved_file=None, title=None)`: Generate Mermaid flowchart
- `render_dot(saved_file=None)`: Generate DOT flowchart

**Operators:**
- `flow[node]`: Add node
- `flow += node`: Add node
- `flow -= node`: Remove node

### 🐝 Swarm

Multi-agent coordination pattern where all nodes are connected to each other.

```python
class Swarm:
    def __init__(self, name: str = None)
```

**Parameters:**
- `name` (str): Swarm name

### 👨‍💼 Supervisor

Supervision pattern where the first node supervises others.

```python
class Supervisor:
    def __init__(self, name: str = None)
```

**Parameters:**
- `name` (str): Supervisor name

## 🔗 Connection Operators

### ➡️ Forward Connection

```python
a >> b
```

Connects node `a` to node `b` in forward direction.

### ⬅️ Reverse Connection

```python
a << b
```

Connects node `b` to node `a` in reverse direction.

### 🔀 Parallel Connection

```python
a >> [b, c, d]
```

Connects node `a` to multiple nodes `b`, `c`, and `d` in parallel.

### ❌ Disconnection

```python
a - b
a - [b, c, d]
```

Removes connections between nodes.

## ⚡ Execution Functions

### 🔄 Synchronous Execution

```python
def sync_function(state):
    # Process state
    return {"result": "processed"}
```

**Parameters:**
- `state` (dict): Current workflow state

**Returns:**
- `dict`: Updated state
- `tuple`: (action_name, state) for flow control

### ⚡ Asynchronous Execution

```python
async def async_function(state):
    # Async processing
    await asyncio.sleep(1)
    return {"result": "async processed"}
```

**Parameters:**
- `state` (dict): Current workflow state

**Returns:**
- `dict`: Updated state
- `tuple`: (action_name, state) for flow control

## 🎮 Flow Control Actions

### 🚪 Exit Flow

```python
return "exit", state
```

Terminates workflow execution.

### 🎯 Jump to Node

```python
return "node_name", state
```

Jumps to specified node.

### ⚠️ Error Handling

```python
return "error", {"error": "error message"}
```

Handles errors in workflow.

## 💾 State Management

### 📋 State Structure

```python
state = {
    "data": "workflow data",
    "step": 0,
    "results": [],
    "metadata": {}
}
```

### 🔄 State Updates

```python
def update_state(state):
    # Immutable update
    new_state = {**state, "step": state["step"] + 1}
    return new_state
```

## �� Visualization

### 📊 Mermaid Configuration

```python
flow.render_mermaid(
    saved_file="workflow.png",
    title="My Workflow"
)
```

**Parameters:**
- `saved_file` (str): Save file path
- `title` (str): Chart title

### 🔷 DOT Configuration

```python
flow.render_dot(
    saved_file="workflow.dot"
)
```

**Parameters:**
- `saved_file` (str): Save file path

## 🚀 Advanced Features

### 🔧 Dynamic Node Management

```python
# Add nodes
flow += Node("new_node", exec=my_function)

# Remove nodes
flow -= existing_node

# Batch operations
flow += [node1, node2, node3]
flow -= [old_node1, old_node2]
```

### 🎲 Conditional Connections

```python
# Condition-based connections
if condition:
    flow = Flow(a >> b)
else:
    flow = Flow(a >> c)

# Dynamic connections
flow = Flow(a >> (b if condition else c))
```

### 🛡️ Error Handling

```python
def robust_function(state):
    try:
        # Risky operation
        result = risky_operation()
        return {"success": True, "result": result}
    except Exception as e:
        return "error", {"error": str(e), "step": "robust_function"}

def error_handler(state):
    print(f"Error in {state['step']}: {state['error']}")
    return {"handled": True}
```

## ⚡ Performance Optimization

### 🔄 Async Execution

```python
# Use async execution for better performance
async def async_workflow():
    flow = Flow(async_node1 >> async_node2 >> async_node3)
    return await flow.arun(initial_state)

# Run async workflow
result = asyncio.run(async_workflow())
```

### 🔀 Parallel Processing

```python
# Execute multiple nodes in parallel
parallel_nodes = [Node(f"task_{i}", exec=task_function) for i in range(5)]
workflow = Flow(parallel_nodes >> combine_node)
```

### 🗄️ Caching Mechanism

```python
def cached_function(state):
    cache_key = hash(str(state))
    if cache_key in cache:
        return cache[cache_key]
    
    result = expensive_operation(state)
    cache[cache_key] = result
    return result
```

## 📚 Best Practices

### 💾 State Design

```python
# Good state design
state = {
    "data": "actual data",
    "metadata": {
        "created_at": "2024-01-01",
        "version": "1.0"
    },
    "results": [],
    "errors": []
}

# Avoid storing large data in state
# Avoid storing functions or complex objects in state
```

### 🛡️ Error Handling

```python
def safe_function(state):
    try:
        return process_safely(state)
    except ValueError as e:
        return {"error": "Invalid input", "details": str(e)}
    except Exception as e:
        return "error", {"error": "Unexpected error", "details": str(e)}
```

### 🔧 Resource Management

```python
def resource_aware_function(state):
    # Check resource availability
    if not check_resources():
        return "error", {"error": "Insufficient resources"}
    
    # Use resources
    result = use_resources(state)
    
    # Clean up resources
    cleanup_resources()
    
    return result
```

## 🔌 Extension and Customization

### 🧩 Custom Node Types

```python
class CustomNode(Node):
    def __init__(self, name, custom_param, **kwargs):
        super().__init__(name, **kwargs)
        self.custom_param = custom_param
    
    def run(self, state):
        # Custom logic
        return {"custom_result": self.custom_param}
```

### 🌊 Custom Flow Types

```python
class CustomFlow(Flow):
    def __init__(self, name=None, custom_config=None):
        super().__init__(name=name)
        self.custom_config = custom_config
    
    def custom_method(self):
        # Custom method
        pass
```

### 🔌 Plugin System

```python
def register_plugin(plugin_name, plugin_function):
    """Register plugin function"""
    plugins[plugin_name] = plugin_function

def use_plugin(plugin_name, state):
    """Use plugin function"""
    if plugin_name in plugins:
        return plugins[plugin_name](state)
    else:
        raise ValueError(f"Plugin {plugin_name} not found")
``` 