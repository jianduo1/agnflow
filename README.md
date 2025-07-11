<div align="center">
  <h1>🚀 AgnFlow</h1>
  <strong>Efficient lightweight Python Agent Workflow Engine</strong>
  <br>
  <em>Support Sync/Async Nodes, Branching Loops, Visual Flowcharts | Build Agent Task Flows Fast</em>
  <br><br>
  
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
  <br><br>
</div>

---

## 🎯 Core Highlights

### ⚡ **Minimalist Syntax - Build in 5 Lines**
```python
from agnflow import Node, Flow
n1 = Node("hello", exec=lambda s: {"msg": "world"})
n2 = Node("world", exec=print)
state = {"data": "hello"}
Flow(n1 >> n2).run(state)  # Output: {"data": "hello", 'msg': 'world'}
```

### 🎨 **Auto Visual Flowcharts**
```python
flow.render_mermaid(saved_file="flow.png")  # Generate image directly
```

### 🔄 **Runtime Dynamic Node Management** ⭐️ **NEW**
```python
# Add/Remove nodes at runtime
flow += new_node
flow -= old_node

# Symmetric connection/disconnection
a >> b >> c    # Build connections
a - b - c      # Disconnect symmetrically
```

### 🚀 Advanced Flow Control

- Sync/Async Mixed: `n=Node(exec=sync_func, aexec=async_func)`
- Branching/Looping: `n1 >> [n2, n3] >> n1` (n1 points to n2 and n3, n2 and n3 point back to n1)
- Swarm Agents: `s=Swarm(); s[n1, n2, n3] >> n4` (n1, n2, n3 are fully connected inside s)
- Parallel Flow: `pf=ParallelFlow(); pf[n1, n2, n3]` (execute multiple child nodes concurrently)
- Human-in-the-Loop: CLI/API intervention

## 📦 Quick Start

### Installation
```bash
pip install agnflow
```

### Basic Usage
```python
from agnflow import Node, Flow
import asyncio

# Define nodes
greet = Node("Greet", exec=lambda state: {"message": "Hello!"})
async def async_respond(state):
    await asyncio.sleep(1)
    print(state["message"])
respond = Node("Respond", aexec=async_respond)

# Build and run workflow
flow = Flow(greet >> respond)
asyncio.run(flow.arun({"data": "hello"}))
```

## 🎨 Feature Showcase

| Feature | Code Example | Visual |
|:-------:|:-------------|:------:|
| **Complex Connections** | `n1 >> [n2 >> n3, n3 >> n4] >> n5` | <img src="https://raw.githubusercontent.com/jianduo1/agnflow/main/assets/node_mermaid.png" height="150" alt="Complex Connections"> |
| **Supervisor Agents** | `s1[n1, n2, n3] >> n4` | <img src="https://raw.githubusercontent.com/jianduo1/agnflow/main/assets/supervisor_mermaid.png" height="150" alt="Swarm Agents"> |
| **Runtime Management** | `flow += new_node`<br>`flow -= old_node` | <img src="https://raw.githubusercontent.com/jianduo1/agnflow/main/assets/swarm_mermaid3.png" height="150" alt="Runtime Management"> |

## 📚 Documentation

- **[📖 Full Documentation](https://jianduo1.github.io/agnflow/)** - Complete guides and API reference
- **[🚀 Quick Start Guide](https://jianduo1.github.io/agnflow/getting-started/)** - Get up and running in minutes
- **[🔧 API Reference](https://jianduo1.github.io/agnflow/api/)** - Detailed API documentation
- **[💡 Examples](https://github.com/jianduo1/agnflow/tree/main/examples)** - Ready-to-run examples

## 🎯 Why Choose agnflow?

- **⚡ Lightweight**: Core code only hundreds of lines
- **🎨 Visual**: Auto-generate beautiful flowcharts
- **🔄 Dynamic**: Add/remove nodes at runtime
- **🤖 Agent-Friendly**: Native LLM integration support
- **🚀 Fast**: Minimal overhead, maximum performance

## 🛠️ Installation & Dependencies

### Basic Installation
```bash
pip install agnflow
```


## 🤝 Contributing

1. **Star & Fork** this repository
2. Submit [Issues](https://github.com/jianduo1/agnflow/issues) for feedback
3. Submit [PRs](https://github.com/jianduo1/agnflow/pulls) for improvements

**Maintainer**: [@jianduo1](https://github.com/jianduo1) | **License**: MIT

### 📞 Contact & Community

<div align="center">
  <p><strong>💬 Join our community for discussions, questions, and collaboration!</strong></p>
  
  <table align="center">
    <tr>
      <td align="center" style="padding: 0 20px;">
        <img src="https://raw.githubusercontent.com/jianduo1/agnflow/main/assets/wx.jpg" alt="Personal WeChat QR Code" width="150" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
        <br>
        <strong>Personal WeChat</strong>
        <br>
        <em>Direct contact with maintainer</em>
      </td>
      <td align="center" style="padding: 0 20px;">
        <img src="https://raw.githubusercontent.com/jianduo1/agnflow/main/assets/wxg.jpg" alt="Community WeChat Group QR Code" width="150" style="border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
        <br>
        <strong>Community Group</strong>
        <br>
        <em>Join our developer community</em>
      </td>
    </tr>
  </table>
  
  <p><em>Feel free to reach out for questions, suggestions, or just to say hello! 👋</em></p>
</div>

# 8. 🔮 Future Roadmap

## 🧠 **Phase 1: Advanced LLM Integration (v0.2.x)**
- **🔄 Streaming Support**: Real-time LLM response streaming
- **🖼️ Multimodal Capabilities**: Text, image, audio, video processing
- **⚡ Async LLM Operations**: Non-blocking LLM interactions
- **📋 Structured Output**: JSON, XML, and custom schema outputs
- **🔗 MCP Tool Integration**: Native Model Context Protocol support
- **💾 Memory Systems**: Short-term and long-term memory management
- **🔍 RAG Integration**: Retrieval-Augmented Generation workflows

## 🤔 **Phase 2: Reasoning Frameworks (v0.3.x)**
- **🔗 ReAct Framework**: Reasoning + Action pattern implementation
- **🔄 TAO Framework**: Thought + Action + Observation cycles
- **🌳 ToT Framework**: Tree of Thoughts reasoning
- **⛓️ CoT Framework**: Chain of Thought reasoning
- **🎯 Multi-Agent Reasoning**: Collaborative reasoning across agents
- **📊 Reasoning Analytics**: Performance metrics and optimization
<!-- 
## 🌐 **Phase 3: Enterprise & Cloud (v0.4.x)**
- **☁️ Cloud Deployment**: One-click deployment to major platforms
- **🔄 Distributed Execution**: Multi-machine workflow orchestration
- **📈 Auto-scaling**: Dynamic resource allocation
- **🔐 Enterprise Security**: SSO, LDAP, and compliance features
- **📊 Advanced Monitoring**: Real-time workflow analytics 
-->

## 🎨 **Phase 4: Advanced UI & Ecosystem (v1.0.x)**
- **🖥️ Visual Workflow Editor**: Interactive web-based designer
- **🔌 Plugin Ecosystem**: Extensible architecture for integrations
- **📱 Mobile Support**: Mobile-friendly workflow management
- **🌍 Multi-language**: Internationalization support
- **🤝 Community Hub**: Templates, examples, and best practices

## ✅ **Completed Features** 👏🏻
- **👥 Human-in-the-Loop (HITL)**: CLI/API intervention capabilities
- **🐝 Supervisor Swarm**: Multi-agent coordination and management
- **🔄 Runtime Node Management**: Dynamic add/remove nodes
- **🎨 Visual Flowcharts**: Auto-generated workflow diagrams
- **⚡ Sync/Async Mixed**: Hybrid execution modes
- **🌿 Branching & Looping**: Complex workflow patterns

---

<div align="center">
  <strong>If this project helps you, please give it a ⭐️ Star!</strong>
  <br>
  <em>Your support is the motivation for my continuous improvement 💪</em>
</div>
