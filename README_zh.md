<div align="center">
  <h1>🚀 AgnFlow</h1>
  <strong>高效轻量的 Python 智能体工作流引擎</strong>
  <br>
  <em>支持同步/异步节点、分支循环、可视化流程图 | 快速搭建 Agent 任务流</em>
  <br><br>
  
  [![Star](https://img.shields.io/github/stars/jianduo1/agnflow?style=social)](https://github.com/jianduo1/agnflow) [![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE) [![Docs](https://img.shields.io/badge/docs-latest-blue.svg)](https://jianduo1.github.io/agnflow/) [![PyPI](https://img.shields.io/badge/pypi-v0.1.4-blue.svg)](https://pypi.org/project/agnflow/) [![Downloads](https://img.shields.io/pypi/dm/agnflow)](https://pypi.org/project/agnflow/) [![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/) [![Discord](https://img.shields.io/badge/Discord-Chat-7289DA?style=flat&logo=discord&logoColor=white)](https://discord.com/channels/1388482307769237584/1388482308222357556)
</div>


<div align="center">
  <br>
  <div style="display: flex; justify-content: center; flex-wrap: wrap;">
    <img src="https://raw.githubusercontent.com/jianduo1/agnflow/main/assets/rapid-dev/code-zh.png" alt="agnflow 代码示例" height="300" style="border-radius: 8px 0 0 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
    <img src="https://raw.githubusercontent.com/jianduo1/agnflow/main/assets/rapid-dev/log-zh.png" alt="agnflow 日志输出" height="300" style="border-radius: 0; box-shadow: none; margin-left: 1px;">
    <img src="https://raw.githubusercontent.com/jianduo1/agnflow/main/assets/rapid-dev/mermaid.png" alt="agnflow 流程图" height="300" style="border-radius: 0 8px 8px 0; box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin-left: 1px;">
  </div>
  <br>
  <em>💻 代码 → 📊 日志 → 🎨 流程图 - 快速开发复杂的智能体工作流可视化</em>
  <br><br>
</div>

---

## 🎯 核心亮点

### ⚡ **极简语法 - 5行代码构建**
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

### 🚀 **高级流程控制**
- **同步/异步混合**: `Node(aexec=async_func)`
- **分支/循环**: `n1 >> [n2, n3] >> n4`
- **蜂群智能体**: `s1[n1, n2, n3] >> n4`
- **人工审核**: CLI/API 介入

## 📦 快速开始

### 安装
```bash
pip install agnflow
```

### 基础用法
```python
from agnflow import Node, Flow
import asyncio

# 定义节点
greet = Node("Greet", exec=lambda state: {"message": "Hello!"})
async def async_respond(state):
    await asyncio.sleep(1)
    print(state["message"])
respond = Node("Respond", aexec=async_respond)

# 构建并运行工作流
flow = Flow(greet >> respond)
asyncio.run(flow.arun({"data": "hello"}))
```

## 🎨 功能展示

| 功能 | 代码示例 | 可视化 |
|:----:|:---------|:------:|
| **复杂连接** | `n1 >> [n2 >> n3, n3 >> n4] >> n5` | <img src="https://raw.githubusercontent.com/jianduo1/agnflow/main/assets/node_mermaid.png" height="150" alt="复杂连接"> |
| **监督者智能体** | `s1[n1, n2, n3] >> n4` | <img src="https://raw.githubusercontent.com/jianduo1/agnflow/main/assets/supervisor_mermaid.png" height="150" alt="蜂群智能体"> |
| **运行期管理** | `flow += new_node`<br>`flow -= old_node` | <img src="https://raw.githubusercontent.com/jianduo1/agnflow/main/assets/swarm_mermaid3.png" height="150" alt="运行期管理"> |

## 📚 文档

- **[📖 完整文档](https://jianduo1.github.io/agnflow/)** - 完整指南和API参考
- **[🚀 快速开始](https://jianduo1.github.io/agnflow/getting-started/)** - 几分钟内上手
- **[🔧 API参考](https://jianduo1.github.io/agnflow/api/)** - 详细API文档
- **[💡 示例代码](https://github.com/jianduo1/agnflow/tree/main/examples)** - 即用示例

## 🎯 为什么选择 agnflow？

- **⚡ 轻量**: 核心代码仅数百行
- **🎨 可视化**: 自动生成精美流程图
- **🔄 动态**: 运行期增删节点
- **🤖 智能体友好**: 原生LLM集成支持
- **🚀 快速**: 最小开销，最大性能

## 🛠️ 安装与依赖

### 基础安装
```bash
pip install agnflow
```

## 🤝 贡献

1. **Star & Fork** 本仓库
2. 提交 [Issue](https://github.com/jianduo1/agnflow/issues) 反馈问题
3. 提交 [PR](https://github.com/jianduo1/agnflow/pulls) 改进功能

**维护者**: [@jianduo1](https://github.com/jianduo1) | **许可证**: MIT

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

## 🔮 未来规划

### 🧠 **第一阶段：高级LLM集成 (v0.2.x)**
- **🔄 流式支持**: 实时LLM响应流式处理
- **🖼️ 多模态能力**: 文本、图像、音频、视频处理
- **⚡ 异步LLM操作**: 非阻塞LLM交互
- **📋 结构化输出**: JSON、XML和自定义模式输出
- **🔗 MCP工具集成**: 原生模型上下文协议支持
- **💾 记忆系统**: 短期和长期记忆管理
- **🔍 RAG集成**: 检索增强生成工作流

### 🤔 **第二阶段：推理框架 (v0.3.x)**
- **🔗 ReAct框架**: 推理+行动模式实现
- **🔄 TAO框架**: 思考+行动+观察循环
- **🌳 ToT框架**: 思维树推理
- **⛓️ CoT框架**: 思维链推理
- **🎯 多智能体推理**: 跨智能体的协作推理
- **📊 推理分析**: 性能指标和优化
<!-- 
### 🌐 **第三阶段：企业级与云原生 (v0.4.x)**
- **☁️ 云部署**: 一键部署到主流平台
- **🔄 分布式执行**: 多机工作流编排
- **📈 自动扩缩容**: 动态资源分配
- **🔐 企业安全**: SSO、LDAP和合规功能
- **📊 高级监控**: 实时工作流分析 
-->

### 🎨 **第四阶段：高级UI与生态 (v1.0.x)**
- **🖥️ 可视化工作流编辑器**: 交互式Web设计器
- **🔌 插件生态**: 可扩展的集成架构
- **📱 移动端支持**: 移动友好的工作流管理
- **🌍 多语言**: 国际化支持
- **🤝 社区中心**: 模板、示例和最佳实践

### ✅ **已完成功能** 👏🏻
- **👥 人工介入循环 (HITL)**: CLI/API干预能力
- **🐝 监督者蜂群**: 多智能体协调和管理
- **🔄 运行期节点管理**: 动态增删节点
- **🎨 可视化流程图**: 自动生成工作流图表
- **⚡ 同步/异步混合**: 混合执行模式
- **🌿 分支与循环**: 复杂工作流模式 

---

<div align="center">
  <strong>如果这个项目对你有帮助，请给它一个 ⭐️ Star！</strong>
  <br>
  <em>你的支持是我持续改进的动力 💪</em>
</div>