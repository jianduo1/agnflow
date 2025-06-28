# 🔧 API 参考

agnflow 的完整 API 文档。

## 🧩 核心类

### 🔧 Node

工作流的基本构建块。

```python
class Node:
    def __init__(self, name: str, exec=None, aexec=None, max_retries=1, wait=0)
```

**参数:**
- `name` (str): 节点标识符
- `exec` (callable): 同步执行函数
- `aexec` (callable): 异步执行函数
- `max_retries` (int): 最大重试次数，默认1
- `wait` (int): 重试间隔时间（秒），默认0

**方法:**
- `run(state)`: 同步执行节点
- `arun(state)`: 异步执行节点

### 🌊 Flow

用于组织和执行节点的容器。

```python
class Flow:
    def __init__(self, name: str = None)
```

**参数:**
- `name` (str): 工作流名称

**方法:**
- `run(state, entry_action=None, max_steps=None)`: 同步执行工作流
- `arun(state, entry_action=None, max_steps=None)`: 异步执行工作流
- `render_mermaid(saved_file=None, title=None)`: 生成 Mermaid 流程图
- `render_dot(saved_file=None)`: 生成 DOT 流程图

**操作符:**
- `flow[node]`: 添加节点
- `flow += node`: 添加节点
- `flow -= node`: 移除节点

### 🐝 Swarm

多智能体协调模式，所有节点都相互连接。

```python
class Swarm:
    def __init__(self, name: str = None)
```

**参数:**
- `name` (str): 蜂群名称

### 👨‍💼 Supervisor

监督模式，第一个节点监督其他节点。

```python
class Supervisor:
    def __init__(self, name: str = None)
```

**参数:**
- `name` (str): 监督者名称

## 🔗 连接操作符

### ➡️ 前向连接

```python
a >> b
```

将节点 `a` 连接到节点 `b`，方向向前。

### ⬅️ 反向连接

```python
a << b
```

将节点 `b` 连接到节点 `a`，方向向后。

### 🔀 并行连接

```python
a >> [b, c, d]
```

将节点 `a` 并行连接到多个节点 `b`、`c` 和 `d`。

### ❌ 断开连接

```python
a - b
a - [b, c, d]
```

移除节点之间的连接。

## ⚡ 执行函数

### 🔄 同步执行

```python
def sync_function(state):
    # 处理状态
    return {"result": "processed"}
```

**参数:**
- `state` (dict): 当前工作流状态

**返回:**
- `dict`: 更新后的状态
- `tuple`: (action_name, state) 用于流程控制

### ⚡ 异步执行

```python
async def async_function(state):
    # 异步处理
    await asyncio.sleep(1)
    return {"result": "async processed"}
```

**参数:**
- `state` (dict): 当前工作流状态

**返回:**
- `dict`: 更新后的状态
- `tuple`: (action_name, state) 用于流程控制

## 🎮 流程控制动作

### 🚪 退出工作流

```python
return "exit", state
```

终止工作流执行。

### 🎯 跳转到节点

```python
return "node_name", state
```

跳转到指定节点。

### ⚠️ 错误处理

```python
return "error", {"error": "error message"}
```

处理工作流中的错误。

## 💾 状态管理

### 📋 状态结构

```python
state = {
    "data": "workflow data",
    "step": 0,
    "results": [],
    "metadata": {}
}
```

### 🔄 状态更新

```python
def update_state(state):
    # 不可变更新
    new_state = {**state, "step": state["step"] + 1}
    return new_state
```

## 🎨 可视化

### 📊 Mermaid 配置

```python
flow.render_mermaid(
    saved_file="workflow.png",
    title="My Workflow"
)
```

**参数:**
- `saved_file` (str): 保存文件路径
- `title` (str): 图表标题

### 🔷 DOT 配置

```python
flow.render_dot(saved_file="workflow.dot")
```

**参数:**
- `saved_file` (str): 保存文件路径

## 🚀 高级功能

### 🔧 动态节点管理

```python
# 添加节点
flow += Node("new_node", exec=my_function)

# 移除节点
flow -= existing_node

# 批量操作
flow += [node1, node2, node3]
flow -= [old_node1, old_node2]
```

### 🎲 条件连接

```python
# 基于条件的连接
if condition:
    flow = Flow(a >> b)
else:
    flow = Flow(a >> c)

# 动态连接
flow = Flow(a >> (b if condition else c))
```

### 🛡️ 错误处理

```python
def robust_function(state):
    try:
        # 可能失败的操作
        result = risky_operation()
        return {"success": True, "result": result}
    except Exception as e:
        return "error", {"error": str(e), "step": "robust_function"}

def error_handler(state):
    print(f"Error in {state['step']}: {state['error']}")
    return {"handled": True}
```

## ⚡ 性能优化

### 🔄 异步执行

```python
# 使用异步执行提高性能
async def async_workflow():
    flow = Flow(async_node1 >> async_node2 >> async_node3)
    return await flow.arun(initial_state)

# 运行异步工作流
result = asyncio.run(async_workflow())
```

### 🔀 并行处理

```python
# 并行执行多个节点
parallel_nodes = [Node(f"task_{i}", exec=task_function) for i in range(5)]
workflow = Flow(parallel_nodes >> combine_node)
```

### 🗄️ 缓存机制

```python
def cached_function(state):
    cache_key = hash(str(state))
    if cache_key in cache:
        return cache[cache_key]
    
    result = expensive_operation(state)
    cache[cache_key] = result
    return result
```

## 📚 最佳实践

### 💾 状态设计

```python
# 好的状态设计
state = {
    "data": "actual data",
    "metadata": {
        "created_at": "2024-01-01",
        "version": "1.0"
    },
    "results": [],
    "errors": []
}

# 避免在状态中存储大量数据
# 避免在状态中存储函数或复杂对象
```

### 🛡️ 错误处理

```python
def safe_function(state):
    try:
        return process_safely(state)
    except ValueError as e:
        return {"error": "Invalid input", "details": str(e)}
    except Exception as e:
        return "error", {"error": "Unexpected error", "details": str(e)}
```

### 🔧 资源管理

```python
def resource_aware_function(state):
    # 检查资源可用性
    if not check_resources():
        return "error", {"error": "Insufficient resources"}
    
    # 使用资源
    result = use_resources(state)
    
    # 清理资源
    cleanup_resources()
    
    return result
```

## 🔌 扩展和自定义

### 🧩 自定义节点类型

```python
class CustomNode(Node):
    def __init__(self, name, custom_param, **kwargs):
        super().__init__(name, **kwargs)
        self.custom_param = custom_param
    
    def run(self, state):
        # 自定义逻辑
        return {"custom_result": self.custom_param}
```

### 🌊 自定义工作流类型

```python
class CustomFlow(Flow):
    def __init__(self, name=None, custom_config=None):
        super().__init__(name=name)
        self.custom_config = custom_config
    
    def custom_method(self):
        # 自定义方法
        pass
```

### 🔌 插件系统

```python
def register_plugin(plugin_name, plugin_function):
    """注册插件函数"""
    plugins[plugin_name] = plugin_function

def use_plugin(plugin_name, state):
    """使用插件函数"""
    if plugin_name in plugins:
        return plugins[plugin_name](state)
    else:
        raise ValueError(f"Plugin {plugin_name} not found")
```