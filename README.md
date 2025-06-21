# agnflow

中文 | [English](README_en.md)

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg) ![Docs: Latest](https://img.shields.io/badge/docs-latest-blue.svg)

一个简洁的 Python 工作流引擎，支持同步与异步节点、分支、循环、流程图渲染。

**agnflow** 追求极简、易用、可扩展，适合快速原型、定制化 LLM 工作流、Agent 任务流等场景。

## 1. TODO（未来扩展方向）

- [ ] llm（支持stream，多模态，异步，structured output）
- [ ] memory
- [ ] rag
- [ ] mcp tool
- [ ] ReAct (reasoning + action)
- [ ] TAO (thought + action + observation)
- [ ] ToT (Tree of Thought)
- [ ] CoT (Chain of Thought)
- [ ] hitl (human in the loop)
- [ ] supervisor swarm

> 以上为未来可扩展的智能体/推理/工具集成方向，欢迎贡献和建议。

## 2. 特性
- 节点式工作流，支持分支、循环、子流程
- 支持同步与异步执行
- 支持流程图（dot/mermaid）渲染
- 代码简洁，易于扩展

## 3. 安装

推荐使用 [rye](https://rye-up.com/) 进行依赖和虚拟环境管理：

```bash
rye sync
```

### 3.1 流程图渲染工具（可选）

**注意：生成图片需要安装额外的工具**

**Dot格式图片生成（推荐）：**
```bash
# macOS
brew install graphviz

# Ubuntu/Debian
sudo apt-get install graphviz

# CentOS/RHEL
sudo yum install graphviz

# Windows
# 下载并安装：https://graphviz.org/download/
```

**Mermaid格式图片生成：**
```bash
# 安装 mermaid-cli
npm install -g @mermaid-js/mermaid-cli

# 安装 puppeteer 浏览器（用于渲染）
npx puppeteer browsers install chrome-headless-shell
```

## 4. 快速开始

### 4.1 定义节点
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

### 4.2 构建并运行工作流
```python
flow = Flow(n1, name="demo")
flow.run({"msg": "hi"})
```

### 4.3 异步执行
```python
import asyncio
async def ahello(state):
    print("async hello", state)
    return {"msg": "async world"}
n1 = Node("hello", aexec=ahello)
flow = Flow(n1)
asyncio.run(flow.arun({"msg": "hi"}))
```

### 4.4 绘制流程图
```python
print(flow.render_dot())      # 输出dot格式
print(flow.render_mermaid())  # 输出mermaid格式

# 保存为图片文件
flow.render_dot(saved_file="./flow.png")      # 保存dot格式图片
flow.render_mermaid(saved_file="./flow.png")  # 保存mermaid格式图片
```

## 5. 节点连接语法

agnflow 提供了多种灵活的节点连接方式：

### 5.1 线性连接
```python
# 方法1：正向连接
a >> b >> c

# 方法2：反向连接  
c << b << a
```

### 5.2 分支连接
```python
# 根据节点返回值进行分支
a >> {"b": b, "c": c}
```

### 5.3 复杂分支和循环
```python
# 支持嵌套分支和循环
a >> {"b": b >> {"b2": flow3}, "c": c >> {"a": a}}
```

### 5.4 子流程连接
```python
# 连接子流程
d1 >> flow >> d2
```

## 6. 复杂工作流示例

运行示例代码`src/agnflow/example.py`后，会生成以下流程图：

工作流定义：
```py
a >> {"b": b >> {"b2": flow3}, "c": c >> {"a": a}} 
d1 >> flow >> d2
```

### 6.1 Dot 格式流程图
![Dot Flow](assets/flow_dot.png)

### 6.2 Mermaid 格式流程图  
![Mermaid Flow](assets/flow_mermaid.png)


## 7. 参考框架

agnflow 参考和对标了以下主流智能体/工作流框架：

![LangGraph](https://img.shields.io/badge/LangGraph-green.svg) ![LlamaIndex](https://img.shields.io/badge/LlamaIndex-green.svg) ![PocketFlow](https://img.shields.io/badge/PocketFlow-green.svg) ![AutoGen](https://img.shields.io/badge/AutoGen-green.svg) ![Haystack](https://img.shields.io/badge/Haystack-green.svg) ![CrewAI](https://img.shields.io/badge/CrewAI-green.svg) ![FastGPT](https://img.shields.io/badge/FastGPT-green.svg) 

