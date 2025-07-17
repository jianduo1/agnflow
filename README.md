<div align="center">
  <h1>🚀 AgnFlow</h1>
  
  <strong>Efficient lightweight Python Agent Workflow Engine</strong>
  <br>
  <strong>高效轻量的 Python 智能体工作流引擎</strong>
  <br>
  
  <em>Support Sync/Async Nodes, Branching Loops, Visual Flowcharts | Build Agent Task Flows Fast</em>
  <br>
  <em>支持同步/异步节点、分支循环、可视化流程图 | 快速搭建 Agent 任务流</em>
  <br>
  
  [![Star](https://img.shields.io/github/stars/jianduo1/agnflow?style=social)](https://github.com/jianduo1/agnflow) [![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Docs](https://img.shields.io/badge/docs-latest-blue.svg)](https://jianduo1.github.io/agnflow/) [![PyPI](https://img.shields.io/badge/pypi-v0.1.4-blue.svg)](https://pypi.org/project/agnflow/) [![Downloads](https://img.shields.io/pypi/dm/agnflow)](https://pypi.org/project/agnflow/) [![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/) [![Discord](https://img.shields.io/badge/Discord-Chat-7289DA?style=flat&logo=discord&logoColor=white)](https://discord.com/channels/1388482307769237584/1388482308222357556) [![Frontend-AgnChat](https://img.shields.io/badge/frontend-AgnChat-ff69b4)](https://github.com/jianduo1/agnchat)
</div>

<div align="center">
  <br>
  <div style="display: flex; justify-content: center; flex-wrap: wrap;">
    <img src="https://raw.githubusercontent.com/jianduo1/agnflow/main/assets/rapid-dev/code.png" alt="agnflow Code Example" height="300" style="border-radius: 8px 0 0 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
    <img src="https://raw.githubusercontent.com/jianduo1/agnflow/main/assets/rapid-dev/log.png" alt="agnflow Log Output" height="300" style="border-radius: 0; box-shadow: none; margin-left: 1px;">
    <img src="https://raw.githubusercontent.com/jianduo1/agnflow/main/assets/rapid-dev/mermaid.png" alt="agnflow Mermaid Flowchart" height="300" style="border-radius: 0 8px 8px 0; box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin-left: 1px;">
  </div>
  <br>
  
  <em>💻 Code → 📊 Log → 🎨 Flowchart - Complete development agent workflow visualization in minutes</em>
  <br>
  <em>💻 代码 → 📊 日志 → 🎨 流程图 - 快速开发复杂的智能体工作流可视化</em>
  <br>
</div>

---

# English Documentation

### ⚡ Quick Start - Minimalist Syntax

```python
from typing import TypedDict
from agnflow import Node, Flow

# Define state
class State(TypedDict):
  message: str

# Define nodes
start = Node(
  name="start",
  exec=lambda s: ("process", {"message": "Hello"}) # Instantiate Node, specify exec
)
class ProcessNode(Node): # Inherit Node, override exec
  def exec(state: State):
    # Route to end node and update message state
    return "end", {"message": s["message"] + " World"}
process = ProcessNode() # No name specified, automatically gets variable name "process"
end = Node(exec=print) # Print state

# Create workflow
flow = Flow(start >> process >> end)

# Run workflow
state: State = {"message": ""}
flow.run(state)  # Output: {'message': 'Hello World'}
```

### 🤖 Static Web Chat Room Experience - Visit Backend Interface http://127.0.0.1:8000/en

```python
from agnflow.chatbot.server import Server

server = Server()
server.run()
```

<div align="center">
  <div style="display: flex; justify-content: center; flex-wrap: wrap; gap: 20px;">
    <img src="https://raw.githubusercontent.com/jianduo1/agnflow/main/assets/chatbot/thinking.en.png" alt="Deep Thinking Process" height="300" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
    <img src="https://raw.githubusercontent.com/jianduo1/agnflow/main/assets/chatbot/code.en.png" alt="Code Generation" height="300" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
  </div>
  <br>
  <em>🧠 Structured reasoning with step-by-step thinking process | 💻 Intelligent code generation with detailed explanations</em>
</div>

### 🎨 Automatic Flow Visualization

```python
flow.render_mermaid(saved_file="flow.png")  # Directly generate image
```

|                                                        Complex Connection                                                         | Supervisor Agent                                                                                                                      |                                                         Runtime Management                                                          |
| :-------------------------------------------------------------------------------------------------------------------------------: | :------------------------------------------------------------------------------------------------------------------------------------ | :---------------------------------------------------------------------------------------------------------------------------------: |
|                                                `n1 >> [n2 >> n3, n3 >> n4] >> n5`                                                 | `s1[n1, n2, n3] >> n4`                                                                                                                |                                              `flow += new_node`<br>`flow -= old_node`                                               |
| <img src="https://raw.githubusercontent.com/jianduo1/agnflow/main/assets/node_mermaid.png" height="150" alt="Complex Connection"> | <img src="https://raw.githubusercontent.com/jianduo1/agnflow/main/assets/supervisor_mermaid.png" height="150" alt="Supervisor Agent"> | <img src="https://raw.githubusercontent.com/jianduo1/agnflow/main/assets/swarm_mermaid3.png" height="150" alt="Runtime Management"> |

### 🔄 Runtime Node Management

```python
# Add/Remove nodes at runtime
flow += new_node
flow -= old_node

# Symmetric connect/disconnect syntax
a >> b >> c    # Connect nodes
a - b - c      # Symmetrically disconnect
```

### 🚀 Advanced Flow Control

- Sync/Async Mixed: `n = Node(exec=sync_func, aexec=async_func)`
- Branch/Loop: `n1 >> [n2, n3] >> n1` (n1 points to n2 and n3, n2 and n3 point to n1)
- Swarm Agent: `s = Swarm(); s[n1, n2, n3] >> n4` (n1, n2, n3 are fully connected inside s)
- Parallel Flow: `pf = ParallelFlow(); pf[n1, n2, n3]` (Execute child nodes concurrently)
- Human Review: CLI/API intervention with `hitl`

### 📦 Installation

```bash
pip install agnflow
```

---

# 中文文档

### 1. ⚡ 快速开始 - 极简语法

```python
from typing import TypedDict
from agnflow import Node, Flow

# 定义状态
class State(TypedDict):
  message: str

# 定义节点
start = Node(
  name="start",
  exec=lambda s: ("process", {"message": "Hello"}) # 实例化 Node，指定 exec
)
class ProcessNode(Node): # 继承 Node，重写 exec
  def exec(state: State):
    # 路由到 end 节点，并且更新 message 状态，
    return "end", {"message": s["message"] + " World"}
process = ProcessNode() #  没有指定 name 属性，自动获取实例化变量名 "process"
end = Node(exec=print) # 打印 state

# 创建工作流
flow = Flow(start >> process >> end)

# 运行工作流
state: State = {"message": ""}
flow.run(state)  # 输出: {'message': 'Hello World'}
```

### 2. 🤖 静态 Web 聊天室体验 - 访问后端接口 http://127.0.0.1:8000/zh

```python
from agnflow.chatbot.server import Server

server = Server()
server.run()
```

<div align="center">
  <div style="display: flex; justify-content: center; flex-wrap: wrap; gap: 20px;">
    <img src="https://raw.githubusercontent.com/jianduo1/agnflow/main/assets/chatbot/thinking.zh.png" alt="深度思考过程" height="300" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
    <img src="https://raw.githubusercontent.com/jianduo1/agnflow/main/assets/chatbot/code.zh.png" alt="代码生成" height="300" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
  </div>
  <br>
  <em>🧠 结构化推理，每一步都有清晰的思考过程 | 💻 智能代码生成，提供详细解释</em>
</div>

### 3. 🎨 **自动可视化流程图**

```python
flow.render_mermaid(saved_file="flow.png")  # 直接生成图片
```

|                                                        复杂连接                                                         | 监督者智能体                                                                                                                    |                                                         运行期管理                                                          |
| :---------------------------------------------------------------------------------------------------------------------: | :------------------------------------------------------------------------------------------------------------------------------ | :-------------------------------------------------------------------------------------------------------------------------: |
|                                           `n1 >> [n2 >> n3, n3 >> n4] >> n5`                                            | `s1[n1, n2, n3] >> n4`                                                                                                          |                                          `flow += new_node`<br>`flow -= old_node`                                           |
| <img src="https://raw.githubusercontent.com/jianduo1/agnflow/main/assets/node_mermaid.png" height="150" alt="复杂连接"> | <img src="https://raw.githubusercontent.com/jianduo1/agnflow/main/assets/supervisor_mermaid.png" height="150" alt="蜂群智能体"> | <img src="https://raw.githubusercontent.com/jianduo1/agnflow/main/assets/swarm_mermaid3.png" height="150" alt="运行期管理"> |

### 4. 🔄 运行期动态节点管理

```python
# 运行期增删节点
flow += new_node
flow -= old_node

# 对称的连接/断开语法
a >> b >> c    # 建立连接
a - b - c      # 对称断开
```

### 5. 🚀 高级流程控制

- 同步/异步混合: `n = Node(exec=sync_func, aexec=async_func)`
- 分支/循环: `n1 >> [n2, n3] >> n1`（n1 指向 n2 和 n3，n2 和 n3 指向 n1）
- 蜂群智能体: `s = Swarm(); s[n1, n2, n3] >> n4`（s 内部的 n1，n2，n3 全互连）
- 并行工作流: `pf = ParallelFlow(); pf[n1, n2, n3]`（并发执行多个子节点）
- 人工审核: CLI/API 介入 `hitl`

### 6. 📦 安装

```bash
pip install agnflow
```

---

# 📚 学习文档 Documentation

访问我们的[文档](https://jianduo1.github.io/agnflow/)获取：<br>
Visit our [documentation](https://jianduo1.github.io/agnflow/) for:

- 详细教程和示例 Detailed tutorials and examples
- API 参考 API reference
- 最佳实践 Best practices
- 高级用法 Advanced usage

# 🤝 贡献 Contributing

我们欢迎贡献！请随时提交 Pull Request。<br>
We welcome contributions! Please feel free to submit a Pull Request.

# 📄 许可证 License

本项目基于 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。<br>
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

# 📞 联系方式与社区

<div align="center">
  <p><strong>💬 加入我们的社区，参与讨论、提问和协作！</strong></p>
  
  <table align="center">
    <tr>
      <td align="center" style="padding: 0 20px;">
        <img src="https://raw.githubusercontent.com/jianduo1/agnflow/main/assets/wx.jpg" alt="个人微信二维码" width="150" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
        <br>
        <strong>个人微信</strong>
        <br>
        <em>直接联系维护者</em>
      </td>
      <td align="center" style="padding: 0 20px;">
        <img src="https://raw.githubusercontent.com/jianduo1/agnflow/main/assets/wxg.jpg" alt="社群微信群二维码" width="150" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
        <br>
        <strong>开发者社群</strong>
        <br>
        <em>加入我们的开发者社区</em>
      </td>
    </tr>
  </table>
  
  <p><em>欢迎随时联系我们，提出问题、建议或只是打个招呼！👋</em></p>
</div>

---

<div align="center">
  <strong>If you find this project helpful, please give it a ⭐️ Star!</strong>
  <br>
  <strong>如果这个项目对你有帮助，请给它一个 ⭐️ Star！</strong>
  <br>
  <em>Your support is my motivation to keep improving 💪</em>
  <br><br>
  <em>你的支持是我持续改进的动力 💪</em>
  <br><br>
</div>

---
