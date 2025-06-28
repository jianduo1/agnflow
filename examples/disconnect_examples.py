#!/usr/bin/env python3
"""
断开连接功能示例

展示如何使用 - 运算符断开各种类型的连接关系
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'agnflow/src'))

from agnflow.core.connection import Connection
from agnflow.core.flow import Flow

def cleanup_global_state():
    """清理全局状态"""
    Connection.connections.clear()
    Connection.conntainer.clear()
    Connection.hidden_connections.clear()

def example_basic_disconnect():
    """示例1: 基本断开连接"""
    cleanup_global_state()
    print("=== 示例1: 基本断开连接 ===")
    
    # 创建节点
    a = Connection()
    b = Connection()
    c = Connection()
    
    # 建立连接
    a >> b >> c
    print(f"建立连接: {a} >> {b} >> {c}")
    print(f"连接状态: {a.connections}")
    
    # 断开连接
    a - b
    print(f"断开连接: {a} - {b}")
    print(f"断开后状态: {a.connections}")
    print()

def example_multiple_disconnect():
    """示例2: 断开多个连接"""
    cleanup_global_state()
    print("=== 示例2: 断开多个连接 ===")
    
    # 创建节点
    a = Connection()
    b = Connection()
    c = Connection()
    d = Connection()
    
    # 建立多个连接
    a >> b >> c >> d
    print(f"建立连接: {a} >> {b} >> {c} >> {d}")
    print(f"连接状态: {a.connections}")
    
    # 断开多个连接
    a - [b, c]
    print(f"断开连接: {a} - [{b}, {c}]")
    print(f"断开后状态: {a.connections}")
    print()

def example_container_disconnect():
    """示例3: 断开容器连接"""
    cleanup_global_state()
    print("=== 示例3: 断开容器连接 ===")
    
    # 创建节点和容器
    a = Connection()
    b = Connection()
    c = Connection()
    flow = Flow()
    
    # 建立容器连接
    flow[b, c]  # 将节点添加到容器
    a >> flow   # 连接到容器
    print(f"建立容器连接: {a} >> {flow}[{b}, {c}]")
    print(f"容器状态: {flow.conntainer}")
    print(f"显式连接: {a.connections}")
    print(f"隐式连接: {a.hidden_connections}")
    
    # 断开容器连接
    a - flow
    print(f"断开容器连接: {a} - {flow}")
    print(f"断开后显式连接: {a.connections}")
    print(f"断开后隐式连接: {a.hidden_connections}")
    print()

def example_chain_disconnect():
    """示例4: 断开链式连接"""
    cleanup_global_state()
    print("=== 示例4: 断开链式连接 ===")
    
    # 创建节点
    a = Connection()
    b = Connection()
    c = Connection()
    d = Connection()
    
    # 建立链式连接
    chain = a >> b >> c >> d
    print(f"建立链式连接: {chain.chains}")
    print(f"原始连接状态: {a.connections}")
    
    # 断开链式连接中的某个节点
    chain - c
    print(f"断开链式连接: {chain} - {c}")
    print(f"断开后状态: {a.connections}")
    print()

def example_chain_disconnect_symmetric():
    """示例4.5: 对称的链式断开连接"""
    cleanup_global_state()
    print("=== 示例4.5: 对称的链式断开连接 ===")
    
    # 创建节点
    a = Connection()
    b = Connection()
    c = Connection()
    d = Connection()
    
    # 建立链式连接
    a >> b >> c >> d
    print(f"建立连接: {a} >> {b} >> {c} >> {d}")
    print(f"连接状态: {a.connections}")
    
    # 对称的链式断开连接
    a - b - c
    print(f"链式断开: {a} - {b} - {c}")
    print(f"断开后状态: {a.connections}")
    print(f"断开后状态: {b.connections}")
    print()

def example_list_disconnect_symmetric():
    """示例4.6: 对称的列表断开连接"""
    cleanup_global_state()
    print("=== 示例4.6: 对称的列表断开连接 ===")
    
    # 创建节点
    a = Connection()
    b = Connection()
    c = Connection()
    d = Connection()
    
    # 建立连接
    a >> [b, c] >> d
    print(f"建立连接: {a} >> [{b}, {c}] >> {d}")
    print(f"连接状态: {a.connections}")
    print(f"隐式连接: {a.hidden_connections}")
    
    # 对称的列表断开连接
    a - [b, c]
    print(f"列表断开: {a} - [{b}, {c}]")
    print(f"断开后状态: {a.connections}")
    print(f"断开后隐式连接: {a.hidden_connections}")
    print()

def example_selective_disconnect():
    """示例5: 选择性断开连接"""
    cleanup_global_state()
    print("=== 示例5: 选择性断开连接 ===")
    
    # 创建节点
    a = Connection()
    b = Connection()
    c = Connection()
    d = Connection()
    
    # 建立复杂连接
    a >> b >> c
    a >> d
    print(f"建立复杂连接:")
    print(f"  {a} >> {b} >> {c}")
    print(f"  {a} >> {d}")
    print(f"连接状态: {a.connections}")
    
    # 选择性断开
    a - b  # 只断开 a 到 b 的连接
    print(f"选择性断开: {a} - {b}")
    print(f"断开后状态: {a.connections}")
    print()

def example_flow_complex_disconnect():
    """示例6: Flow 容器复杂断开"""
    cleanup_global_state()
    print("=== 示例6: Flow 容器复杂断开 ===")
    
    # 创建节点和容器
    a = Connection()
    b = Connection()
    c = Connection()
    d = Connection()
    flow1 = Flow()
    flow2 = Flow()
    
    # 建立复杂容器连接
    flow1[a, b]  # 容器1包含 a, b
    flow2[c, d]  # 容器2包含 c, d
    flow1 >> flow2  # 容器1连接到容器2
    print(f"建立复杂容器连接:")
    print(f"  {flow1}[{a}, {b}] >> {flow2}[{c}, {d}]")
    print(f"容器1状态: {flow1.conntainer}")
    print(f"容器2状态: {flow2.conntainer}")
    print(f"显式连接: {flow1.connections}")
    print(f"隐式连接: {flow1.hidden_connections}")
    
    # 断开容器间连接
    flow1 - flow2
    print(f"断开容器连接: {flow1} - {flow2}")
    print(f"断开后显式连接: {flow1.connections}")
    print(f"断开后隐式连接: {flow1.hidden_connections}")
    print()

def example_visualization():
    """示例7: 可视化断开连接效果"""
    cleanup_global_state()
    print("=== 示例7: 可视化断开连接效果 ===")
    
    # 创建节点
    a = Connection()
    b = Connection()
    c = Connection()
    d = Connection()
    
    # 建立连接
    a >> b >> c >> d
    print("原始连接图:")
    print(f"  {a} -> {b} -> {c} -> {d}")
    
    # 断开中间连接
    b - c
    print("断开 b - c 后:")
    print(f"  {a} -> {b}")
    print(f"  {c} -> {d}")
    print(f"连接状态: {a.connections}")
    print(f"连接状态: {b.connections}")
    print(f"连接状态: {c.connections}")
    print()

if __name__ == "__main__":
    example_basic_disconnect()
    example_multiple_disconnect()
    example_container_disconnect()
    example_chain_disconnect()
    example_chain_disconnect_symmetric()
    example_list_disconnect_symmetric()
    example_selective_disconnect()
    example_flow_complex_disconnect()
    example_visualization()
    
    print("🎉 所有断开连接示例演示完成！")
    print("\n总结:")
    print("- 使用 - 运算符可以断开各种类型的连接")
    print("- 支持断开单个连接: c1 - c2")
    print("- 支持断开多个连接: c1 - [c2, c3]")
    print("- 支持断开容器连接: c1 - flow")
    print("- 支持断开链式连接: chain - node")
    print("- 断开连接会同时清理显式连接和隐式连接")
    print("\n对称语法:")
    print("- 建立连接: a >> b >> c")
    print("- 断开连接: a - b - c")
    print("- 建立连接: a >> [b, c]")
    print("- 断开连接: a - [b, c]")
    print("- 语法完全对称，直观易懂！") 