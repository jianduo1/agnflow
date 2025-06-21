# agnflow API 文档

## 核心类

### Node

工作流中的基本执行单元。

#### 构造函数

```python
Node(name: str = None, exec: Callable = None, aexec: Callable = None, max_retries=1, wait=0)
```

**参数：**
- `name`: 节点名称，如果不提供则自动生成
- `exec`: 同步执行函数
- `aexec`: 异步执行函数
- `max_retries`: 最大重试次数，默认1
- `wait`: 重试间隔时间（秒），默认0

#### 执行函数签名

```python
def exec(state) -> str | dict | tuple[str, dict]:
    """
    同步执行函数
    
    Args:
        state: 当前状态字典
        
    Returns:
        str: 下一个节点的action
        dict: 更新后的状态
        tuple[str, dict]: (action, state) 元组
    """
    pass

async def aexec(state) -> str | dict | tuple[str, dict]:
    """
    异步执行函数
    
    Args:
        state: 当前状态字典
        
    Returns:
        str: 下一个节点的action
        dict: 更新后的状态
        tuple[str, dict]: (action, state) 元组
    """
    pass
```

### Flow

工作流容器，管理节点的执行顺序。

#### 构造函数

```python
Flow(start: Conn | None = None, name: str = None)
```

**参数：**
- `start`: 起始节点
- `name`: 工作流名称

#### 主要方法

```python
def run(self, state: dict) -> dict:
    """同步执行工作流"""
    pass

async def arun(self, state: dict) -> dict:
    """异步执行工作流"""
    pass

def render_dot(self, saved_file: str = None) -> str:
    """生成dot格式流程图"""
    pass

def render_mermaid(self, saved_file: str = None) -> str:
    """生成mermaid格式流程图"""
    pass
```

## 节点连接语法

### 线性连接

```python
# 正向连接
node1 >> node2 >> node3

# 反向连接
node3 << node2 << node1
```

### 分支连接

```python
# 根据返回值分支
node1 >> {"action1": node2, "action2": node3}

# 条件分支
node1 >> {"success": success_node, "error": error_node}
```

### 循环连接

```python
# 循环到自身
node1 >> {"continue": node1, "end": end_node}

# 循环到其他节点
node1 >> {"retry": node1, "next": node2}
```

### 子流程连接

```python
# 连接子流程
start_node >> sub_flow >> end_node
```

## 状态管理

### 状态注入

节点函数可以通过参数名自动从状态中获取值：

```python
def my_node(user_id, message, state):
    # user_id 和 message 会从 state 中自动获取
    # state 参数会接收整个状态字典
    pass
```

### 状态更新

节点函数可以通过返回值更新状态：

```python
def my_node(state):
    # 返回新状态
    return {"result": "processed", "timestamp": time.time()}
    
    # 返回action和新状态
    return "next_action", {"result": "processed"}
```

## 错误处理

### 重试机制

```python
# 设置重试次数和间隔
node = Node("retry_node", exec=my_func, max_retries=3, wait=1)
```

### 自定义错误处理

```python
class MyNode(Node):
    def exec_fallback(self, state, exc):
        # 自定义错误处理逻辑
        return "error_action", {"error": str(exc)}
    
    async def aexec_fallback(self, state, exc):
        # 自定义异步错误处理逻辑
        return "error_action", {"error": str(exc)}
```

## 流程图渲染

### Dot格式

```python
# 输出dot格式文本
dot_text = flow.render_dot()

# 保存为图片
flow.render_dot(saved_file="./flow.png")
```

### Mermaid格式

```python
# 输出mermaid格式文本
mermaid_text = flow.render_mermaid()

# 保存为图片
flow.render_mermaid(saved_file="./flow.png")
```

## 最佳实践

### 1. 节点设计

- 保持节点功能单一
- 使用有意义的节点名称
- 合理处理异常情况

### 2. 状态管理

- 避免在状态中存储过大的数据
- 使用类型提示提高代码可读性
- 保持状态结构的一致性

### 3. 错误处理

- 为关键节点设置重试机制
- 实现自定义错误处理逻辑
- 记录详细的错误信息

### 4. 性能优化

- 合理使用异步节点
- 避免在节点中执行耗时操作
- 考虑使用缓存机制 