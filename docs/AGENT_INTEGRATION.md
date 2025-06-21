# 智能体功能与工作流编排集成

## 概述

Agnflow 提供了两种使用智能体功能的方式：

1. **独立智能体** (`utils.py`) - 直接使用智能体算法
2. **工作流智能体** (`agents.py`) - 将智能体算法与工作流编排结合

## 两种方式的对比

### 1. 独立智能体 (utils.py)

**特点：**
- 直接使用智能体算法
- 不依赖工作流框架
- 简单直接，适合快速原型

**使用示例：**
```python
from agnflow.utils import create_react_agent, create_tao_agent

# 直接使用ReAct代理
react_agent = create_react_agent()
result = react_agent.solve("计算 15 + 27")

# 直接使用TAO代理
tao_agent = create_tao_agent()
result = tao_agent.solve("解释什么是机器学习")
```

### 2. 工作流智能体 (agents.py)

**特点：**
- 将智能体算法封装为工作流节点
- 支持复杂的流程编排
- 可视化、调试、监控友好

**使用示例：**
```python
from agnflow.agents import create_react_workflow, create_tao_workflow

# 使用ReAct工作流
react_workflow = create_react_workflow()
result = react_workflow.solve("计算 15 + 27")

# 使用TAO工作流
tao_workflow = create_tao_workflow()
result = tao_workflow.solve("解释什么是机器学习")
```

## 详细功能对比

| 功能 | 独立智能体 | 工作流智能体 |
|------|------------|--------------|
| **使用复杂度** | 简单 | 中等 |
| **流程控制** | 有限 | 强大 |
| **可视化** | 不支持 | 支持 |
| **调试** | 困难 | 容易 |
| **扩展性** | 中等 | 高 |
| **性能** | 高 | 中等 |
| **适用场景** | 快速原型、简单任务 | 复杂流程、生产环境 |

## 工作流智能体的优势

### 1. 可视化支持
```python
from agnflow.agents import create_react_workflow

workflow = create_react_workflow()

# 生成DOT格式可视化
dot_str = workflow.flow.render_dot("workflow.png")

# 生成Mermaid格式可视化
mermaid_str = workflow.flow.render_mermaid("workflow.png")
```

### 2. 复杂流程编排
```python
from agnflow.agents import create_llm_node, create_search_node, create_memory_node
from agnflow.core import Flow

# 创建自定义工作流
llm_node = create_llm_node("analysis")
search_node = create_search_node("research")
memory_node = create_memory_node("store")

# 构建复杂流程
llm_node >> "need_search" >> search_node >> "default" >> memory_node >> "default" >> llm_node
llm_node >> "final" >> "end"

flow = Flow(start=llm_node, name="complex_workflow")
```

### 3. 状态管理和调试
```python
# 工作流提供完整的状态管理
state = {
    "query": "用户问题",
    "iteration": 0,
    "thoughts": [],
    "actions": []
}

result = workflow.solve("问题", state)
print(f"最终状态: {state}")
```

## 基础节点类型

### 1. LLMNode - LLM调用节点
```python
from agnflow.agents import create_llm_node

llm_node = create_llm_node(
    name="my_llm",
    model="glm-4-flashx-250414",
    system_prompt="你是一个有用的助手",
    output_format="yaml"
)
```

### 2. SearchNode - 搜索节点
```python
from agnflow.agents import create_search_node

search_node = create_search_node(
    name="my_search",
    search_engine="duckduckgo"
)
```

### 3. MemoryNode - 记忆节点
```python
from agnflow.agents import create_memory_node

memory_node = create_memory_node(
    name="my_memory",
    max_messages=10
)
```

### 4. RAGNode - RAG节点
```python
from agnflow.agents import create_rag_node

rag_node = create_rag_node(name="my_rag")
```

### 5. ToolNode - 工具节点
```python
from agnflow.agents import create_tool_node

tool_node = create_tool_node(name="my_tools")
```

## 高级工作流类型

### 1. ReActWorkflow - 推理+行动工作流
```python
from agnflow.agents import create_react_workflow

workflow = create_react_workflow()
result = workflow.solve("复杂问题", max_iterations=5)
```

### 2. TAOWorkflow - 思考+行动+观察工作流
```python
from agnflow.agents import create_tao_workflow

workflow = create_tao_workflow()
result = workflow.solve("复杂问题", max_iterations=5)
```

### 3. CoTWorkflow - 思维链工作流
```python
from agnflow.agents import create_cot_workflow

workflow = create_cot_workflow(max_steps=5)
result = workflow.solve("需要推理的问题")
```

### 4. RAGWorkflow - 检索增强生成工作流
```python
from agnflow.agents import create_rag_workflow

workflow = create_rag_workflow()
result = workflow.solve("问题", documents=["文档1", "文档2"])
```

## 选择建议

### 使用独立智能体的场景：
- 快速原型开发
- 简单的智能体任务
- 对性能要求较高
- 不需要复杂流程控制

### 使用工作流智能体的场景：
- 复杂的业务流程
- 需要可视化和调试
- 生产环境部署
- 需要状态管理和监控
- 多步骤、多分支的智能体任务

## 迁移指南

### 从独立智能体迁移到工作流智能体：

```python
# 原来的代码
from agnflow.utils import create_react_agent
agent = create_react_agent()
result = agent.solve("问题")

# 迁移后的代码
from agnflow.agents import create_react_workflow
workflow = create_react_workflow()
result = workflow.solve("问题")
```

### 从工作流智能体迁移到独立智能体：

```python
# 原来的代码
from agnflow.agents import create_react_workflow
workflow = create_react_workflow()
result = workflow.solve("问题")

# 迁移后的代码
from agnflow.utils import create_react_agent
agent = create_react_agent()
result = agent.solve("问题")
```

## 总结

两种方式各有优势，可以根据具体需求选择：

- **独立智能体**：简单、高效、直接
- **工作流智能体**：强大、可视化、可扩展

Agnflow 支持两种方式并存，用户可以根据项目需求灵活选择。 