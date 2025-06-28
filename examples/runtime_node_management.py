#!/usr/bin/env python3
"""
运行期动态节点管理示例

展示如何在运行时动态添加和删除节点
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from agnflow.core.connection import Connection
from agnflow.core.flow import Flow

def cleanup_global_state():
    """清理全局状态"""
    Connection.connections.clear()
    Connection.conntainer.clear()
    Connection.hidden_connections.clear()

def example_runtime_add_nodes():
    """示例1: 运行期添加节点"""
    cleanup_global_state()
    print("=== 示例1: 运行期添加节点 ===")
    
    # 创建初始节点
    a = Connection()
    b = Connection()
    flow = Flow()
    
    # 建立初始连接
    a >> flow[b]
    print(f"初始连接: {a} >> {flow}[{b}]")
    print(f"容器状态: {flow.conntainer}")
    
    # 运行期添加新节点
    c = Connection()
    d = Connection()
    
    # 方法1: 使用 += 运算符
    flow += c
    print(f"\n添加节点 c: flow += {c}")
    print(f"容器状态: {flow.conntainer}")
    
    # 方法2: 使用 [] 运算符
    flow[d]
    print(f"\n添加节点 d: flow[{d}]")
    print(f"容器状态: {flow.conntainer}")
    
    # 方法3: 添加多个节点
    e = Connection()
    f = Connection()
    flow += [e, f]
    print(f"\n添加多个节点: flow += [{e}, {f}]")
    print(f"容器状态: {flow.conntainer}")
    print()

def example_runtime_remove_nodes():
    """示例2: 运行期删除节点"""
    cleanup_global_state()
    print("=== 示例2: 运行期删除节点 ===")
    
    # 创建节点和容器
    a = Connection()
    b = Connection()
    c = Connection()
    d = Connection()
    flow = Flow()
    
    # 建立初始连接
    flow[a, b, c, d]
    print(f"初始容器: {flow.conntainer}")
    
    # 运行期删除节点
    flow -= b
    print(f"\n删除节点 b: flow -= {b}")
    print(f"容器状态: {flow.conntainer}")
    
    # 删除多个节点
    flow -= [c, d]
    print(f"\n删除多个节点: flow -= [{c}, {d}]")
    print(f"容器状态: {flow.conntainer}")
    print()

def example_symmetric_syntax():
    """示例3: 对称的连接/断开语法"""
    cleanup_global_state()
    print("=== 示例3: 对称的连接/断开语法 ===")
    
    # 创建节点
    a = Connection()
    b = Connection()
    c = Connection()
    d = Connection()
    
    # 建立连接
    a >> b >> c
    a >> [b, c]
    print(f"建立连接:")
    print(f"  {a} >> {b} >> {c}")
    print(f"  {a} >> [{b}, {c}]")
    print(f"连接状态: {a.connections}")
    
    # 对称断开连接
    a - b - c
    a - [b, c]
    print(f"\n对称断开连接:")
    print(f"  {a} - {b} - {c}")
    print(f"  {a} - [{b}, {c}]")
    print(f"断开后状态: {a.connections}")
    print()

def example_container_operations():
    """示例4: 容器操作"""
    cleanup_global_state()
    print("=== 示例4: 容器操作 ===")
    
    # 创建节点和容器
    a = Connection()
    b = Connection()
    c = Connection()
    flow = Flow()
    
    # 添加到容器
    flow[a, b]
    print(f"添加到容器: {flow}[{a}, {b}]")
    print(f"容器状态: {flow.conntainer}")
    
    # 从容器移除
    a - flow[a, b]
    print(f"\n从容器移除: {a} - {flow}[{a}, {b}]")
    print(f"容器状态: {flow.conntainer}")
    print()

def example_dynamic_workflow_modification():
    """示例5: 动态工作流修改"""
    cleanup_global_state()
    print("=== 示例5: 动态工作流修改 ===")
    
    # 创建初始工作流
    a = Connection()
    b = Connection()
    c = Connection()
    flow = Flow()
    
    # 建立初始工作流
    flow[a >> b]
    print(f"初始工作流: {flow}[{a} >> {b}]")
    print(f"容器状态: {flow.conntainer}")
    print(f"连接状态: {a.connections}")
    
    # 动态添加节点到工作流
    flow += c
    a >> c
    print(f"\n动态添加节点: flow += {c}, {a} >> {c}")
    print(f"容器状态: {flow.conntainer}")
    print(f"连接状态: {a.connections}")
    
    # 动态删除节点
    flow -= b
    a - b
    print(f"\n动态删除节点: flow -= {b}, {a} - {b}")
    print(f"容器状态: {flow.conntainer}")
    print(f"连接状态: {a.connections}")
    print()

if __name__ == "__main__":
    example_runtime_add_nodes()
    example_runtime_remove_nodes()
    example_symmetric_syntax()
    example_container_operations()
    example_dynamic_workflow_modification()
    
    print("🎉 运行期动态节点管理示例演示完成！")
    print("\n核心特性:")
    print("- 运行期添加节点: flow += node 或 flow[node]")
    print("- 运行期删除节点: flow -= node")
    print("- 对称语法: a >> b >> c 对应 a - b - c")
    print("- 支持批量操作: flow += [node1, node2]")
    print("- 容器操作: flow[a, b] 和 a - flow[a, b]") 