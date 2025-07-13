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
  
  [![Star](https://img.shields.io/github/stars/jianduo1/agnflow?style=social)](https://github.com/jianduo1/agnflow) [![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Docs](https://img.shields.io/badge/docs-latest-blue.svg)](https://jianduo1.github.io/agnflow/) [![PyPI](https://img.shields.io/badge/pypi-v0.1.4-blue.svg)](https://pypi.org/project/agnflow/) [![Downloads](https://img.shields.io/pypi/dm/agnflow)](https://pypi.org/project/agnflow/) [![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/) [![Discord](https://img.shields.io/badge/Discord-Chat-7289DA?style=flat&logo=discord&logoColor=white)](https://discord.com/channels/1388482307769237584/1388482308222357556)
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

<h1 id="english">English Documentation</h1>

## 🎯 Core Highlights

### ⚡ Minimalist Syntax - Build in 5 Lines

```python
from agnflow import Node, Flow
n1 = Node("hello", exec=lambda s: {"msg": "world"})
n2 = Node("world", exec=print)
state = {"data": "hello"}
Flow(n1 >> n2).run(state)  # Output: {"data": "hello", 'msg': 'world'}
```

### 🎨 **Automatic Flow Visualization**

```python
flow.render_mermaid(saved_file="flow.png")  # Directly generate image
```

### 🔄 **Runtime Node Management** ⭐️ **New Feature**

```python
# Add/Remove nodes at runtime
flow += new_node
flow -= old_node

# Symmetric connect/disconnect syntax
a >> b >> c    # Connect nodes
a - b - c      # Symmetrically disconnect
```

### 🚀 Advanced Flow Control

- Sync/Async Mixed: `n=Node(exec=sync_func, aexec=async_func)`
- Branch/Loop: `n1 >> [n2, n3] >> n1` (n1 points to n2 and n3, n2 and n3 point to n1)
- Swarm Agent: `s=Swarm(); s[n1, n2, n3] >> n4` (n1, n2, n3 are fully connected inside s)
- Parallel Flow: `pf=ParallelFlow(); pf[n1, n2, n3]` (Execute child nodes concurrently)
- Human Review: CLI/API intervention with `hitl`

### 🎨 Feature Showcase

|                                                        Complex Connection                                                         | Supervisor Agent                                                                                                                      |                                                         Runtime Management                                                          |
| :-------------------------------------------------------------------------------------------------------------------------------: | :------------------------------------------------------------------------------------------------------------------------------------ | :---------------------------------------------------------------------------------------------------------------------------------: |
|                                                `n1 >> [n2 >> n3, n3 >> n4] >> n5`                                                 | `s1[n1, n2, n3] >> n4`                                                                                                                |                                              `flow += new_node`<br>`flow -= old_node`                                               |
| <img src="https://raw.githubusercontent.com/jianduo1/agnflow/main/assets/node_mermaid.png" height="150" alt="Complex Connection"> | <img src="https://raw.githubusercontent.com/jianduo1/agnflow/main/assets/supervisor_mermaid.png" height="150" alt="Supervisor Agent"> | <img src="https://raw.githubusercontent.com/jianduo1/agnflow/main/assets/swarm_mermaid3.png" height="150" alt="Runtime Management"> |

### 🔄 Workflow Management

- **Dynamic Workflows**: Modify flows during runtime.
- **Visualize Changes**: Immediate mermaid diagram updates.
- **Save & Share**: Export workflows as images or JSON.

### 📦 Installation

```bash
pip install agnflow
```

### 🎯 Quick Start

```python
from agnflow import Node, Flow

# Define nodes
start = Node("start", lambda s: {"message": "Hello"})
process = Node("process", lambda s: {"message": s["message"] + " World"})
end = Node("end", print)

# Create workflow
flow = Flow(start >> process >> end)

# Run workflow
flow.run()  # Output: {'message': 'Hello World'}
```

### 📚 Documentation

Visit our [documentation](https://jianduo1.github.io/agnflow/) for:

- Detailed tutorials and examples
- API reference
- Best practices
- Advanced usage

### 🤝 Contributing

We welcome contributions! Please feel free to submit a Pull Request.

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<h1 id="chinese">中文文档</h1>

## 🎯 核心亮点

### ⚡ **极简语法 - 5 行代码构建**

```python
from agnflow import Node, Flow
n1 = Node("hello", exec=lambda s: {"msg": "world"})
n2 = Node("world", exec=print)
state = {"data": "hello"}
Flow(n1 >> n2).run(state)  # 输出: {"data": "hello", 'msg': 'world'}
```

### 🎨 **自动可视化流程图**

```python
flow.render_mermaid(saved_file="flow.png")  # 直接生成图片
```

### 🔄 **运行期动态节点管理** ⭐️ **新功能**

```python
# 运行期增删节点
flow += new_node
flow -= old_node

# 对称的连接/断开语法
a >> b >> c    # 建立连接
a - b - c      # 对称断开
```

### 🚀 高级流程控制

- 同步/异步混合: `n=Node(exec=sync_func, aexec=async_func)`
- 分支/循环: `n1 >> [n2, n3] >> n1`（n1 指向 n2 和 n3，n2 和 n3 指向 n1）
- 蜂群智能体: `s=Swarm(); s[n1, n2, n3] >> n4`（s 内部的 n1，n2，n3 全互连）
- 并行工作流: `pf=ParallelFlow(); pf[n1, n2, n3]`（并发执行多个子节点）
- 人工审核: CLI/API 介入 `hitl`

### 🎨 功能展示

|                                                        复杂连接                                                         | 监督者智能体                                                                                                                    |                                                         运行期管理                                                          |
| :---------------------------------------------------------------------------------------------------------------------: | :------------------------------------------------------------------------------------------------------------------------------ | :-------------------------------------------------------------------------------------------------------------------------: |
|                                           `n1 >> [n2 >> n3, n3 >> n4] >> n5`                                            | `s1[n1, n2, n3] >> n4`                                                                                                          |                                          `flow += new_node`<br>`flow -= old_node`                                           |
| <img src="https://raw.githubusercontent.com/jianduo1/agnflow/main/assets/node_mermaid.png" height="150" alt="复杂连接"> | <img src="https://raw.githubusercontent.com/jianduo1/agnflow/main/assets/supervisor_mermaid.png" height="150" alt="蜂群智能体"> | <img src="https://raw.githubusercontent.com/jianduo1/agnflow/main/assets/swarm_mermaid3.png" height="150" alt="运行期管理"> |

### 🔄 工作流管理

- **动态工作流**: 运行时修改工作流。
- **可视化更改**: 即时更新流程图。
- **保存与分享**: 导出工作流为图片或 JSON。

### 📦 安装

```bash
pip install agnflow
```

### 🎯 快速开始

```python
from agnflow import Node, Flow

# 定义节点
start = Node("start", lambda s: {"message": "Hello"})
process = Node("process", lambda s: {"message": s["message"] + " World"})
end = Node("end", print)

# 创建工作流
flow = Flow(start >> process >> end)

# 运行工作流
flow.run()  # 输出: {'message': 'Hello World'}
```

### 📚 文档

访问我们的[文档](https://jianduo1.github.io/agnflow/)获取：

- 详细教程和示例
- API 参考
- 最佳实践
- 高级用法

### 🤝 贡献

我们欢迎贡献！请随时提交 Pull Request。

### 📄 许可证

本项目基于 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

### 📞 联系方式与社区

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
