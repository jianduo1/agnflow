# agnflow

[中文](README.md) | English 

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg) ![Docs: Latest](https://img.shields.io/badge/docs-latest-blue.svg)

A concise Python workflow engine supporting synchronous and asynchronous nodes, branching, loops, and flowchart rendering.

**agnflow** pursues simplicity, ease of use, and extensibility, suitable for rapid prototyping, customized LLM workflows, and Agent task flows.

## 1. TODO (Future Extension Directions)

- [ ] llm (supporting stream, multimodal, async, structured output)
- [ ] memory
- [ ] rag
- [ ] mcp tool
- [ ] ReAct (reasoning + action)
- [ ] TAO (thought + action + observation)
- [ ] ToT (Tree of Thought)
- [ ] CoT (Chain of Thought)
- [ ] hitl (human in the loop)
- [ ] supervisor swarm

> The above are future extensible intelligent agent/reasoning/tool integration directions. Contributions and suggestions are welcome.

## 2. Features
- Node-based workflows with support for branching, loops, and sub-flows
- Support for synchronous and asynchronous execution
- Support for flowchart rendering (dot/mermaid)
- Clean code, easy to extend

## 3. Installation

Recommended to use [rye](https://rye-up.com/) for dependency and virtual environment management:

```bash
rye sync
```

### 3.1 Flowchart Rendering Tools (Optional)

**Note: Generating images requires additional tools**

**Dot format image generation (Recommended):**
```bash
# macOS
brew install graphviz

# Ubuntu/Debian
sudo apt-get install graphviz

# CentOS/RHEL
sudo yum install graphviz

# Windows
# Download and install: https://graphviz.org/download/
```

**Mermaid format image generation:**
```bash
# Install mermaid-cli
npm install -g @mermaid-js/mermaid-cli

# Install puppeteer browser (for rendering)
npx puppeteer browsers install chrome-headless-shell
```

## 4. Quick Start

### 4.1 Define Nodes
```python
from agnflow import Node, Flow

def hello_exec(state):
    print("hello", state)
    return {"msg": "world"}

def world_exec(state):
    print("world", state)

n1 = Node("hello", exec=hello_exec)
n2 = Node("world", exec=world_exec)
n1 >> n2
```

### 4.2 Build and Run Workflow
```python
flow = Flow(n1, name="demo")
flow.run({"msg": "hi"})
```

### 4.3 Asynchronous Execution
```python
import asyncio
async def ahello(state):
    print("async hello", state)
    return {"msg": "async world"}
n1 = Node("hello", aexec=ahello)
flow = Flow(n1)
asyncio.run(flow.arun({"msg": "hi"}))
```

### 4.4 Render Flowchart
```python
print(flow.render_dot())      # Output dot format
print(flow.render_mermaid())  # Output mermaid format

# Save as image file
flow.render_dot(saved_file="./flow.png")      # Save dot format image
flow.render_mermaid(saved_file="./flow.png")  # Save mermaid format image
```

## 5. Node Connection Syntax

agnflow provides multiple flexible node connection methods:

### 5.1 Linear Connection
```python
# Method 1: Forward connection
a >> b >> c

# Method 2: Reverse connection  
c << b << a
```

### 5.2 Branch Connection
```python
# Branch based on node return value
a >> {"b": b, "c": c}
```

### 5.3 Complex Branching and Loops
```python
# Support nested branching and loops
a >> {"b": b >> {"b2": flow3}, "c": c >> {"a": a}}
```

### 5.4 Sub-flow Connection
```python
# Connect sub-flows
d1 >> flow >> d2
```

## 6. Complex Workflow Example

After running the example code `src/agnflow/example.py`, the following flowcharts will be generated:

Workflow definition:
```py
a >> {"b": b >> {"b2": flow3}, "c": c >> {"a": a}} 
d1 >> flow >> d2
```

### 6.1 Dot Format Flowchart
![Dot Flow](assets/flow_dot.png)

### 6.2 Mermaid Format Flowchart  
![Mermaid Flow](assets/flow_mermaid.png)

## 7. Reference Frameworks

agnflow references and benchmarks against the following mainstream intelligent agent/workflow frameworks:

![LangGraph](https://img.shields.io/badge/LangGraph-green.svg) ![LlamaIndex](https://img.shields.io/badge/LlamaIndex-green.svg) ![AutoGen](https://img.shields.io/badge/AutoGen-green.svg) ![Haystack](https://img.shields.io/badge/Haystack-green.svg) ![CrewAI](https://img.shields.io/badge/CrewAI-green.svg) ![FastGPT](https://img.shields.io/badge/FastGPT-green.svg) ![PocketFlow](https://img.shields.io/badge/PocketFlow-green.svg)

## 8. License
MIT 