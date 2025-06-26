#!/usr/bin/env python3
"""
调试测试
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from agnflow.core import Node, Flow
import copy

def debug_simple_workflow():
    """调试简单工作流"""
    print("=== 调试简单工作流 ===")
    
    def node1_func(state):
        print(f"执行节点1，当前状态: {state}")
        state['value'] = 10
        return {'result': 'success'}
    
    def node2_func(state):
        print(f"执行节点2，当前状态: {state}")
        state['value'] *= 2
        return {'result': 'success'}
    
    n1 = Node(exec=node1_func)
    n2 = Node(exec=node2_func)
    
    # 创建工作流
    flow = Flow()
    flow[n1 >> n2]
    
    print(f"Flow节点: {flow.connections.get(flow, {}).get('nodes', [])}")
    print(f"Flow连接: {flow.connections}")
    print(f"起始节点: {flow._get_start_nodes()}")
    
    # 检查 connectons 是类变量还是实例变量
    print(f"\n=== 检查 connectons 类型 ===")
    print(f"connectons 是类变量: {hasattr(Flow, 'connectons')}")
    print(f"connectons 是实例变量: {hasattr(flow, 'connectons')}")
    print(f"connectons 在类中: {Flow.connections}")
    print(f"connectons 在实例中: {getattr(flow, 'connectons', '不存在')}")
    
    # 测试深拷贝
    print(f"\n=== 测试深拷贝 ===")
    flow_copy = copy.deepcopy(flow)
    print(f"原始 flow connectons: {flow.connections}")
    print(f"拷贝 flow connectons: {flow_copy.connections}")
    print(f"拷贝 flow 的起始节点: {flow_copy._get_start_nodes()}")
    
    # 检查方法是否存在
    print(f"\n=== 检查方法 ===")
    print(f"_run 方法存在: {hasattr(flow, '_run')}")
    print(f"_execute_workflow_sync 方法存在: {hasattr(flow, '_execute_workflow_sync')}")
    
    # 尝试直接调用 _execute_workflow_sync
    print("\n=== 直接调用 _execute_workflow_sync ===")
    try:
        result = flow._execute_workflow_sync({'initial': 'test'}, 10)
        print(f"直接调用结果: {result}")
    except Exception as e:
        print(f"直接调用出错: {e}")
        import traceback
        traceback.print_exc()
    
    # 尝试调用 _run
    print("\n=== 调用 _run ===")
    try:
        result = flow._run({'initial': 'test'}, 10)
        print(f"_run 结果: {result}")
    except Exception as e:
        print(f"_run 出错: {e}")
        import traceback
        traceback.print_exc()
    
    # 执行工作流
    print("\n=== 调用 run ===")
    state = {'initial': 'test'}
    result = flow.run(state, max_steps=20)
    
    print(f"最终状态: {state}")
    print(f"执行结果: {result}")

if __name__ == "__main__":
    debug_simple_workflow() 