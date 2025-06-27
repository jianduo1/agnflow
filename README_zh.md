<div align="center">
  <h1>agnflow</h1>
  <strong>一个简洁的 Python 智能体工作流引擎</strong>
  <br>
  <h3>
    <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License"></a>
    <a href="https://jianduo1.github.io/agnflow/"><img src="https://img.shields.io/badge/docs-latest-blue.svg" alt="Docs"></a>
    <a href="https://pypi.org/project/agnflow/"><img src="https://img.shields.io/badge/pypi-v0.1.2-blue.svg" alt="PyPI"></a>
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python Version"></a>
  </h3>
</div>

中文 | [English](README.md)

**agnflow** 追求极简、易用、可扩展，适合快速原型、定制化 LLM 工作流、Agent 任务流等场景。

## 🎯 核心功能展示

| 智能体类型 | 代码示例 | 流程图 |
|:----------:|:--------|:------:|
| **复杂节点连接** | `n1 >> [n2 >> n3, n3 >> n4] >> n5` | <img src="https://raw.githubusercontent.com/jianduo1/agnflow/main/assets/node_mermaid.png" height="150" alt="节点连接流程图"> |
| **复杂工作流连接** | `f1[n1 >> n2 >> f2[n3]] >> f3[n4]` | <img src="https://raw.githubusercontent.com/jianduo1/agnflow/main/assets/flow_mermaid.png" height="150" alt="工作流连接流程图"> |
| **监督者智能体**<br>*首节点与其余节点双向连接* | `s1[n1, n2, n3] >> n4` | <img src="https://raw.githubusercontent.com/jianduo1/agnflow/main/assets/supervisor_mermaid.png" height="150" alt="监督者智能体流程图"> |
| **基础蜂群连接**<br>*任意节点进行双向连接* | `s1[n1, n2, n3, n4]` | <img src="https://raw.githubusercontent.com/jianduo1/agnflow/main/assets/swarm_mermaid1.png" height="150" alt="基础蜂群连接流程图"> |
| **节点与蜂群连接** | `n1 >> s1[n2, n3] >> n4` | <img src="https://raw.githubusercontent.com/jianduo1/agnflow/main/assets/swarm_mermaid2.png" height="150" alt="节点与蜂群连接流程图"> |
| **多个蜂群连接** | `s1[n1, n2] >> s2[n3, n4]` | <img src="https://raw.githubusercontent.com/jianduo1/agnflow/main/assets/swarm_mermaid3.png" height="150" alt="多个蜂群连接流程图"> |

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
- [X] 👏🏻 supervisor swarm

> 以上为未来可扩展的智能体/推理/工具集成方向，欢迎贡献和建议。

## 2. 特性
- 节点式工作流，支持分支、循环、子流程
- 支持同步与异步执行
- 支持流程图（dot/mermaid）渲染
- 代码简洁，易于扩展

## 3. 安装

### 3.1 从 PyPI 安装（推荐）

```bash
# 使用 pip 安装
pip install agnflow

# 使用 rye 安装
rye add agnflow

# 使用 poetry 安装
poetry add agnflow

# 安装特定版本
pip install agnflow==0.1.0

# 安装最新开发版本
pip install --upgrade agnflow
```

### 3.2 从源码安装

推荐使用 [rye](https://rye-up.com/) 进行依赖和虚拟环境管理：

```bash
# 克隆仓库
git clone https://github.com/jianduo1/agnflow.git
cd agnflow

# 安装依赖
rye sync

# 开发模式安装
rye sync --dev
```

### 3.3 流程图渲染工具（可选）

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

### 3.4 开发环境

使用 rye 管理开发环境：

```bash
# 安装依赖
rye sync

# 运行测试
rye run test

# 代码格式化
rye run format

# 代码检查
rye run lint

# 运行示例
rye run example
```

### 3.5 发布到 PyPI

```bash
# 清理之前的构建
rye run clean

# 构建包
rye run build

# 上传到测试 PyPI（推荐先测试）
rye run upload-test

# 上传到正式 PyPI
rye run upload
```

**注意：** 首次上传到 PyPI 需要：
1. 在 [PyPI](https://pypi.org) 注册账号
2. 在 [TestPyPI](https://test.pypi.org) 注册账号
3. 配置 `~/.pypirc` 文件或使用环境变量

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

## 5. 节点函数详解

### 5.1 函数入参方式

agnflow 支持多种函数入参方式，会根据函数签名自动从状态中获取参数：

#### 方式 1: 接收整个状态
```python
def my_node(state):
    """接收整个状态字典"""
    print(f"收到状态: {state}")
    return {"result": "processed"}

n1 = Node("my_node", exec=my_node)
```

#### 方式 2: 按参数名自动注入
```python
def my_node(user_id, message, data):
    """根据参数名从状态中自动获取值"""
    print(f"用户ID: {user_id}")
    print(f"消息: {message}")
    print(f"数据: {data}")
    return {"processed": True}

# 调用时传入包含这些字段的状态
flow.run({
    "user_id": "123",
    "message": "hello",
    "data": {"key": "value"}
})
```

#### 方式 3: 混合方式
```python
def my_node(user_id, state):
    """混合方式：部分参数 + 整个状态"""
    print(f"用户ID: {user_id}")
    print(f"完整状态: {state}")
    return {"user_processed": True}
```

### 5.2 函数返回值方式

节点函数支持多种返回值格式：

#### 方式 1: 只返回新状态
```python
def my_node(state):
    """只更新状态，使用默认action"""
    return {"new_data": "value", "timestamp": time.time()}
```

#### 方式 2: 返回action和新状态
```python
def my_node(state):
    """返回action和更新后的状态"""
    if state.get("condition"):
        return "success", {"result": "success"}
    else:
        return "error", {"result": "error"}
```

#### 方式 3: 只返回action
```python
def my_node(state):
    """只返回action，不更新状态"""
    if state.get("condition"):
        return "success"
    else:
        return "error"
```

#### 方式 4: 返回None（结束工作流）
```python
def my_node(state):
    """返回None结束工作流"""
    if state.get("should_stop"):
        return None
    return "continue", {"step": "completed"}
```

### 5.3 异步节点函数

异步节点函数使用 `aexec` 参数，支持所有同步函数的特性：

```python
import asyncio

async def async_node(state):
    """异步节点函数"""
    await asyncio.sleep(0.1)  # 模拟异步操作
    return {"async_result": "done"}

async def async_node_with_action(user_id, state):
    """异步节点函数 - 混合参数 + action"""
    await asyncio.sleep(0.1)
    return "next", {"user_id": user_id, "processed": True}

# 创建异步节点
n1 = Node("async_node", aexec=async_node)
n2 = Node("async_node_with_action", aexec=async_node_with_action)

# 异步执行
asyncio.run(flow.arun({"user_id": "123"}))
```

### 5.4 节点类继承方式

除了函数方式，还可以通过继承 `Node` 类来创建节点：

```python
class MyNode(Node):
    def exec(self, state):
        """同步执行方法"""
        print(f"执行节点: {self.name}")
        return {"class_result": "success"}
    
    async def aexec(self, state):
        """异步执行方法"""
        print(f"异步执行节点: {self.name}")
        return {"async_class_result": "success"}

# 使用类节点
n1 = MyNode("my_class_node")
```

### 5.5 错误处理和重试

节点支持错误处理和重试机制：

```python
def risky_node(state):
    """可能出错的节点"""
    if random.random() < 0.5:
        raise Exception("随机错误")
    return {"success": True}

# 创建支持重试的节点
n1 = Node("risky_node", exec=risky_node, max_retries=3, wait=1)

# 自定义错误处理
class SafeNode(Node):
    def exec_fallback(self, state, exc):
        """自定义错误处理"""
        return "error", {"error": str(exc), "recovered": True}
    
    async def aexec_fallback(self, state, exc):
        """自定义异步错误处理"""
        return "error", {"error": str(exc), "recovered": True}
```

### 5.6 完整示例

```python
from agnflow import Node, Flow
import time

# 定义不同类型的节点函数
def start_node(user_id, message):
    """接收特定参数"""
    return "n2", {"user_id": user_id, "message": message}

def process_node(state):
    """接收整个状态"""
    processed = f"处理: {state['message']}"
    return "n3", {"processed": processed, "timestamp": time.time()}

def complete_node(result, state):
    """混合参数"""
    print(f"结果: {result}")
    print(f"状态: {state}")
    return {"final_result": "success"}

# 创建节点
n1 = Node("start", exec=start_node)
n2 = Node("process", exec=process_node)
n3 = Node("complete", exec=complete_node)

# 连接节点
n1 >> n2 >> n3

# 创建工作流
flow = Flow(n1, name="example_flow")

# 运行工作流
result = flow.run({
    "user_id": "123",
    "message": "Hello agnflow!"
})

print(f"工作流结果: {result}")
```

## 6. 节点连接语法

agnflow 提供了多种灵活的节点连接方式：

### 6.1 线性连接
```python
# 方法1：正向连接
a >> b >> c

# 方法2：反向连接  
c << b << a
```

### 6.2 分支连接
```python
# 根据节点返回值进行分支
a >> [b, c]
```

### 6.3 子流程连接
```python
# 连接子流程
d1 >> flow >> d2
```

## 7. 复杂工作流示例

运行示例代码`src/agnflow/example.py`后，会生成以下流程图：

工作流定义：
```py
a >> [b >> flow, c >> a]
d1 >> flow >> d2
```

### 7.1 Dot 格式流程图
![Dot Flow](assets/flow_dot.png)

### 7.2 Mermaid 格式流程图  
![Mermaid Flow](assets/flow_mermaid.png)

这些流程图展示了：
- 节点之间的连接关系
- 分支和循环结构
- 子流程的嵌套关系
- 工作流的整体执行路径

## 8. 参考框架

agnflow 参考和对标了以下主流智能体/工作流框架：

![LangGraph](https://img.shields.io/badge/LangGraph-green.svg) ![LlamaIndex](https://img.shields.io/badge/LlamaIndex-green.svg) ![AutoGen](https://img.shields.io/badge/AutoGen-green.svg) ![Haystack](https://img.shields.io/badge/Haystack-green.svg) ![CrewAI](https://img.shields.io/badge/CrewAI-green.svg) ![FastGPT](https://img.shields.io/badge/FastGPT-green.svg) ![PocketFlow](https://img.shields.io/badge/PocketFlow-green.svg)

## 9. 项目状态

### 📦 发布状态
- **PyPI**: ✅ [v0.1.2](https://pypi.org/project/agnflow/0.1.2/) 已发布
- **GitHub**: ✅ [开源仓库](https://github.com/jianduo1/agnflow)
- **文档**: ✅ [API 文档](docs/API.md) 完整
- **测试**: ✅ 功能测试通过

### 🔄 版本信息
- **当前版本**: 0.1.2
- **Python 支持**: 3.8+
- **许可证**: MIT
- **状态**: Beta

## 10. 许可证
MIT


