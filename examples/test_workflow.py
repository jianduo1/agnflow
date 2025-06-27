#!/usr/bin/env python3
"""
测试基于 connectons 的流程执行
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'agnflow', 'src'))

from agnflow.core import Node, Flow

def test_basic_workflow():
    """测试基本工作流"""
    print("=== 测试基本工作流 ===")
    
    # 创建节点
    def node1_func(state):
        print(f"执行节点1，当前状态: {state}")
        state['value'] = 10
        return {'result': 'success'}
    
    def node2_func(state):
        print(f"执行节点2，当前状态: {state}")
        state['value'] *= 2
        return {'result': 'success'}
    
    def node3_func(state):
        print(f"执行节点3，当前状态: {state}")
        state['value'] += 5
        return {'result': 'success'}
    
    n1 = Node(exec=node1_func)
    n2 = Node(exec=node2_func)
    n3 = Node(exec=node3_func)
    
    # 创建工作流
    flow = Flow()
    flow[n1 >> n2 >> n3]
    
    # 打印调试信息
    print(f"Flow节点: {flow.connections.get(flow, {}).get('nodes', [])}")
    print(f"Flow连接: {flow.connections}")
    print(f"起始节点: {flow._get_start_nodes()}")
    
    # 执行工作流
    state = {'initial': 'test'}
    result = flow.run(state)
    
    print(f"最终状态: {state}")
    print(f"执行结果: {result}")
    print()

def test_conditional_workflow():
    """测试条件工作流"""
    print("=== 测试条件工作流 ===")
    
    def start_func(state):
        print(f"开始节点，当前状态: {state}")
        return 'branch_a' if state.get('condition') == 'a' else 'branch_b'
    
    def branch_a_func(state):
        print(f"分支A，当前状态: {state}")
        state['branch'] = 'A'
        return {'result': 'branch_a_success'}
    
    def branch_b_func(state):
        print(f"分支B，当前状态: {state}")
        state['branch'] = 'B'
        return {'result': 'branch_b_success'}
    
    def end_func(state):
        print(f"结束节点，当前状态: {state}")
        return {'result': 'workflow_completed'}
    
    start = Node(exec=start_func)
    branch_a = Node(exec=branch_a_func)
    branch_b = Node(exec=branch_b_func)
    end = Node(exec=end_func)
    
    # 创建工作流
    flow = Flow()
    flow[start >> [branch_a, branch_b] >> end]
    
    # 测试分支A
    print("测试分支A:")
    state_a = {'condition': 'a'}
    result_a = flow.run(state_a)
    print(f"分支A最终状态: {state_a}")
    print(f"分支A执行结果: {result_a}")
    print()
    
    # 测试分支B
    print("测试分支B:")
    state_b = {'condition': 'b'}
    result_b = flow.run(state_b)
    print(f"分支B最终状态: {state_b}")
    print(f"分支B执行结果: {result_b}")
    print()

def test_flow_composition():
    """测试工作流组合"""
    print("=== 测试工作流组合 ===")
    
    def sub_flow1_func(state):
        print(f"子工作流1，当前状态: {state}")
        state['sub1'] = 'completed'
        return {'result': 'sub1_success'}
    
    def sub_flow2_func(state):
        print(f"子工作流2，当前状态: {state}")
        state['sub2'] = 'completed'
        return {'result': 'sub2_success'}
    
    def main_func(state):
        print(f"主工作流，当前状态: {state}")
        state['main'] = 'completed'
        return {'result': 'main_success'}
    
    # 创建子工作流
    sub1 = Node(exec=sub_flow1_func)
    sub2 = Node(exec=sub_flow2_func)
    sub_flow = Flow()
    sub_flow[sub1 >> sub2]
    
    # 创建主工作流
    main = Node(exec=main_func)
    main_flow = Flow()
    main_flow[sub_flow >> main]
    
    # 执行主工作流
    state = {'test': 'composition'}
    result = main_flow.run(state)
    
    print(f"组合工作流最终状态: {state}")
    print(f"组合工作流执行结果: {result}")
    print()

if __name__ == "__main__":
    test_basic_workflow()
    test_conditional_workflow()
    test_flow_composition()
    print("所有测试完成！") 