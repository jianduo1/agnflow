# 💡 Examples

Practical examples demonstrating agnflow capabilities.

## 🎯 Basic Examples

### 📝 Simple Linear Workflow

```python
from agnflow import Node, Flow

# Define nodes
def step1(state):
    return {"data": "processed", "step": 1}

def step2(state):
    return {"data": state["data"], "step": 2, "final": True}

# Create nodes
node1 = Node("step1", exec=step1)
node2 = Node("step2", exec=step2)

# Build workflow
workflow = Flow(node1 >> node2)

# Execute
result = workflow.run({"initial": "data"})
print(result)  # {'data': 'processed', 'step': 2, 'final': True}
```

### 🔄 Parallel Processing

```python
from agnflow import Node, Flow

def process_a(state):
    return {"result_a": "A processed"}

def process_b(state):
    return {"result_b": "B processed"}

def combine(state):
    return {
        **state,
        "combined": f"{state['result_a']} + {state['result_b']}"
    }

# Create workflow with parallel branches
a = Node("process_a", exec=process_a)
b = Node("process_b", exec=process_b)
c = Node("combine", exec=combine)

workflow = Flow(a >> [b, c] >> c)
result = workflow.run({})
```

## 🚀 Advanced Examples

### 🔧 Dynamic Node Management

```python
from agnflow import Node, Flow

def add_data(state):
    return {"data": "new data"}

def process_data(state):
    return {"processed": state["data"]}

# Create initial workflow
workflow = Flow()
workflow[Node("start", exec=lambda s: {"step": "started"})]

# Add nodes dynamically
workflow += Node("add", exec=add_data)
workflow += Node("process", exec=process_data)

# Connect nodes
workflow["start"] >> workflow["add"] >> workflow["process"]

# Execute
result = workflow.run({})
```

### 🎲 Conditional Workflows

```python
from agnflow import Node, Flow

def check_condition(state):
    if state.get("condition"):
        return "branch_a"
    else:
        return "branch_b"

def branch_a(state):
    return {"path": "A", "result": "A processed"}

def branch_b(state):
    return {"path": "B", "result": "B processed"}

def finalize(state):
    return {"final": f"Completed via {state['path']}"}

# Create workflow with conditional branching
check = Node("check", exec=check_condition)
a = Node("branch_a", exec=branch_a)
b = Node("branch_b", exec=branch_b)
final = Node("finalize", exec=finalize)

workflow = Flow(check >> (a if True else b) >> final)
result = workflow.run({"condition": True})
```

### 👥 Human-in-the-Loop

```python
from agnflow import Node, Flow
from agnflow.agent.hitl.cli import human_in_the_loop

def generate_content(state):
    return {"content": "Generated content for review"}

def human_review(state):
    result, approved = human_in_the_loop(
        "Please review this content:",
        input_data=state["content"],
        options=["approve", "reject", "modify"]
    )
    
    if approved:
        return {"reviewed": True, "content": result}
    else:
        return "exit", {"reviewed": False}

def publish(state):
    return {"published": True, "content": state["content"]}

# Create HITL workflow
generate = Node("generate", exec=generate_content)
review = Node("review", exec=human_review)
publish = Node("publish", exec=publish)

workflow = Flow(generate >> review >> publish)
result = workflow.run({})
```

## 🤖 Multi-Agent Examples

### 🐝 Swarm Pattern

```python
from agnflow import Node, Swarm

def agent1(state):
    return {"agent1_result": "Task 1 completed"}

def agent2(state):
    return {"agent2_result": "Task 2 completed"}

def agent3(state):
    return {"agent3_result": "Task 3 completed"}

# Create swarm of agents
agent1_node = Node("agent1", exec=agent1)
agent2_node = Node("agent2", exec=agent2)
agent3_node = Node("agent3", exec=agent3)

swarm = Swarm[agent1_node, agent2_node, agent3_node]
result = swarm.run({"task": "collaborative task"})
```

### 👨‍💼 Supervisor Pattern

```python
from agnflow import Node, Supervisor

def supervisor(state):
    # Supervisor coordinates workers
    return {"supervision": "coordinating", "tasks": ["task1", "task2"]}

def worker1(state):
    return {"worker1_result": "Task 1 done"}

def worker2(state):
    return {"worker2_result": "Task 2 done"}

# Create supervisor-worker pattern
supervisor_node = Node("supervisor", exec=supervisor)
worker1_node = Node("worker1", exec=worker1)
worker2_node = Node("worker2", exec=worker2)

supervisor_flow = Supervisor[supervisor_node, worker1_node, worker2_node]
result = supervisor_flow.run({"project": "supervised project"})
```

## ⚠️ Error Handling Examples

### 🛡️ Robust Workflow

```python
from agnflow import Node, Flow

def risky_operation(state):
    try:
        # Risky operation that might fail
        result = 1 / 0
        return {"result": result}
    except Exception as e:
        return "error", {"error": str(e)}

def error_handler(state):
    print(f"Handling error: {state['error']}")
    return {"handled": True, "error": state["error"]}

def success_handler(state):
    return {"success": True, "result": state["result"]}

# Create error handling workflow
risky = Node("risky", exec=risky_operation)
error = Node("error", exec=error_handler)
success = Node("success", exec=success_handler)

workflow = Flow(risky >> (error if "error" in state else success))
result = workflow.run({})
```

### 🔄 Retry Mechanism

```python
from agnflow import Node, Flow
import time

def retry_operation(state, max_retries=3):
    retries = state.get("retries", 0)
    
    if retries >= max_retries:
        return "error", {"error": "Max retries exceeded"}
    
    try:
        # Simulate operation that might fail
        if time.time() % 2 < 1:  # 50% failure rate
            raise Exception("Random failure")
        
        return {"success": True, "attempts": retries + 1}
    except Exception as e:
        return {
            "retries": retries + 1,
            "last_error": str(e)
        }

def retry_node(state):
    return retry_operation(state)

# Create retry workflow
retry = Node("retry", exec=retry_node)
workflow = Flow(retry >> retry)  # Self-loop for retries

result = workflow.run({"retries": 0})
```

## ⚡ Async Examples

### 🔄 Async Nodes

```python
import asyncio
from agnflow import Node, Flow

async def async_operation(state):
    await asyncio.sleep(1)
    return {"async_result": "completed"}

async def async_combine(state):
    await asyncio.sleep(0.5)
    return {"combined": f"Async: {state['async_result']}"}

# Create async workflow
async_node = Node("async_op", aexec=async_operation)
async_combine_node = Node("async_combine", aexec=async_combine)

workflow = Flow(async_node >> async_combine_node)

# Execute asynchronously
result = asyncio.run(workflow.arun({}))
```

### 🔀 Mixed Sync/Async

```python
import asyncio
from agnflow import Node, Flow

def sync_operation(state):
    return {"sync_data": "processed"}

async def async_operation(state):
    await asyncio.sleep(1)
    return {"async_data": "processed"}

def combine_results(state):
    return {
        "combined": f"{state['sync_data']} + {state['async_data']}"
    }

# Create mixed workflow
sync_node = Node("sync", exec=sync_operation)
async_node = Node("async", aexec=async_operation)
combine_node = Node("combine", exec=combine_results)

workflow = Flow(sync_node >> async_node >> combine_node)
result = asyncio.run(workflow.arun({}))
```

## 🎨 Visualization Examples

### 📊 Generate Flowcharts

```python
from agnflow import Node, Flow

def step1(state):
    return {"step": 1}

def step2(state):
    return {"step": 2}

def step3(state):
    return {"step": 3}

# Create complex workflow
a = Node("step1", exec=step1)
b = Node("step2", exec=step2)
c = Node("step3", exec=step3)

workflow = Flow(a >> [b, c] >> b)

# Generate Mermaid chart
workflow.render_mermaid(saved_file="workflow.png", title="Complex Workflow")

# Generate DOT chart
workflow.render_dot(saved_file="workflow.dot")
```

## 💾 State Management Examples

### 🔢 Complex State Operations

```python
from agnflow import Node, Flow

def initialize_state(state):
    return {
        **state,
        "counter": 0,
        "history": [],
        "metadata": {"created": "now"}
    }

def increment_counter(state):
    new_counter = state["counter"] + 1
    new_history = state["history"] + [new_counter]
    
    return {
        **state,
        "counter": new_counter,
        "history": new_history
    }

def analyze_history(state):
    history = state["history"]
    return {
        **state,
        "analysis": {
            "total": len(history),
            "sum": sum(history),
            "average": sum(history) / len(history) if history else 0
        }
    }

# Create state management workflow
init = Node("init", exec=initialize_state)
increment = Node("increment", exec=increment_counter)
analyze = Node("analyze", exec=analyze_history)

workflow = Flow(init >> increment >> increment >> increment >> analyze)
result = workflow.run({})
```

### 💾 State Persistence

```python
import json
from agnflow import Node, Flow

def save_state(state):
    with open("workflow_state.json", "w") as f:
        json.dump(state, f)
    return state

def load_state(state):
    try:
        with open("workflow_state.json", "r") as f:
            loaded_state = json.load(f)
        return {**state, **loaded_state}
    except FileNotFoundError:
        return state

def process_with_persistence(state):
    return {"processed": True, "data": state.get("data", "default")}

# Create persistence workflow
load = Node("load", exec=load_state)
process = Node("process", exec=process_with_persistence)
save = Node("save", exec=save_state)

workflow = Flow(load >> process >> save)
result = workflow.run({"data": "important data"})
```

## ⚡ Performance Optimization Examples

### 🗄️ Caching Mechanism

```python
from agnflow import Node, Flow
import hashlib
import json

class Cache:
    def __init__(self):
        self._cache = {}
    
    def get(self, key):
        return self._cache.get(key)
    
    def set(self, key, value):
        self._cache[key] = value

cache = Cache()

def expensive_operation(state):
    # Generate cache key
    cache_key = hashlib.md5(
        json.dumps(state, sort_keys=True).encode()
    ).hexdigest()
    
    # Check cache
    cached_result = cache.get(cache_key)
    if cached_result:
        return {"result": cached_result, "cached": True}
    
    # Execute expensive operation
    result = sum(i**2 for i in range(10000))
    
    # Cache result
    cache.set(cache_key, result)
    
    return {"result": result, "cached": False}

# Create caching workflow
expensive = Node("expensive", exec=expensive_operation)
workflow = Flow(expensive)

# First execution (no cache)
result1 = workflow.run({"input": "data1"})

# Second execution (with cache)
result2 = workflow.run({"input": "data1"})
```

### 🔄 Parallel Optimization

```python
from agnflow import Node, Flow
import asyncio

async def parallel_task1(state):
    await asyncio.sleep(2)
    return {"task1": "completed"}

async def parallel_task2(state):
    await asyncio.sleep(3)
    return {"task2": "completed"}

async def parallel_task3(state):
    await asyncio.sleep(1)
    return {"task3": "completed"}

def combine_parallel_results(state):
    return {
        "all_tasks": [
            state.get("task1"),
            state.get("task2"),
            state.get("task3")
        ]
    }

# Create parallel optimization workflow
task1 = Node("task1", aexec=parallel_task1)
task2 = Node("task2", aexec=parallel_task2)
task3 = Node("task3", aexec=parallel_task3)
combine = Node("combine", exec=combine_parallel_results)

# Execute all tasks in parallel
workflow = Flow([task1, task2, task3] >> combine)
result = asyncio.run(workflow.arun({}))
``` 