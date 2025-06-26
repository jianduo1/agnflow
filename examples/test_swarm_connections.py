#!/usr/bin/env python3
"""
测试 Swarm 连接关系
"""

import sys
import os
import random
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from agnflow.core import Node, Flow, Swarm

def test_swarm_basic_connections():
    """测试 Swarm 基本连接关系"""
    print("=== 测试 Swarm 基本连接关系 ===")
    
    # 创建节点
    n1 = Node()
    n2 = Node()
    n3 = Node()
    
    # 创建 Swarm
    s1 = Swarm()
    
    # 测试 Swarm[n1, n2, n3] 的连接关系
    s1[n1, n2, n3]
    
    print(f"Swarm节点: {s1.connections.get(s1, {}).get('nodes', [])}")
    print(f"Swarm连接: {s1.connections}")
    
    # 验证连接关系
    expected_connections = {
        'n1': ['n2', 'n3'],
        'n2': ['n1', 'n3'], 
        'n3': ['n1', 'n2']
    }
    
    for node_name, expected_targets in expected_connections.items():
        node = next((n for n in s1.connections.get(s1, {}).get('nodes', []) if n.name == node_name), None)
        if node:
            connections = s1.connections.get(node, {})
            actual_targets = list(connections.keys())
            print(f"{node_name} 的连接: {actual_targets}")
            assert set(actual_targets) == set(expected_targets), f"{node_name} 连接不匹配"
    
    print("✓ Swarm 基本连接关系测试通过\n")

def test_swarm_in_workflow():
    """测试 Swarm 在工作流中的使用"""
    print("=== 测试 Swarm 在工作流中的使用 ===")
    
    # 创建节点
    n1 = Node()
    n2 = Node()
    n3 = Node()
    n4 = Node()
    
    # 创建 Swarm
    s1 = Swarm()
    
    # 测试 n1 >> s1[n2, n3] >> n4 的连接关系
    workflow = n1 >> s1[n2, n3] >> n4
    
    print(f"工作流连接: {workflow.connectons}")
    
    # 验证连接关系
    # n1 应该连接到 s1
    n1_connections = workflow.connectons.get(n1, {})
    assert 's1' in n1_connections, "n1 应该连接到 s1"
    
    # s1 应该连接到 n4
    s1_connections = workflow.connectons.get(s1, {})
    assert 'n4' in s1_connections, "s1 应该连接到 n4"
    
    # s1 内部应该有 n2, n3 的相互连接
    s1_nodes = s1.connections.get(s1, {}).get('nodes', [])
    assert len(s1_nodes) == 2, "s1 应该包含 2 个节点"
    
    print("✓ Swarm 在工作流中的使用测试通过\n")

def test_swarm_composition():
    """测试 Swarm 组合使用"""
    print("=== 测试 Swarm 组合使用 ===")
    
    # 创建节点
    n1 = Node()
    n2 = Node()
    n3 = Node()
    n4 = Node()
    
    # 创建两个 Swarm
    s1 = Swarm()
    s2 = Swarm()
    
    # 测试 s1[n1, n2] >> s2[n3, n4] 的连接关系
    workflow = s1[n1, n2] >> s2[n3, n4]
    
    print(f"组合工作流连接: {workflow.connectons}")
    
    # 验证连接关系
    # s1 应该连接到 s2
    s1_connections = workflow.connectons.get(s1, {})
    assert 's2' in s1_connections, "s1 应该连接到 s2"
    
    # s1 内部应该有 n1, n2 的相互连接
    s1_nodes = s1.connections.get(s1, {}).get('nodes', [])
    assert len(s1_nodes) == 2, "s1 应该包含 2 个节点"
    
    # s2 内部应该有 n3, n4 的相互连接
    s2_nodes = s2.connections.get(s2, {}).get('nodes', [])
    assert len(s2_nodes) == 2, "s2 应该包含 2 个节点"
    
    print("✓ Swarm 组合使用测试通过\n")

def test_swarm_execution():
    """测试 Swarm 执行功能"""
    print("=== 测试 Swarm 执行功能 ===")
    
    # 创建带执行函数的节点
    def node1_func(state):
        print(f"💧执行节点1，当前状态: {state}")
        state['value'] = 10
        # 70%概率继续，30%概率退出
        if random.random() < 0.7:
            next_action = random.choice(["n2", "n3"])
            print(f"节点1决定流转到: {next_action}")
            return next_action, {'result': 'from n1'}
        else:
            print("节点1决定退出")
            return None, {'result': 'from n1 (exit)'}
    
    def node2_func(state):
        print(f"🔥执行节点2，当前状态: {state}")
        state['value'] *= 2
        if random.random() < 0.7:
            next_action = random.choice(["n1", "n3"])
            print(f"节点2决定流转到: {next_action}")
            return next_action, {'result': 'from n2'}
        else:
            print("节点2决定退出")
            return None, {'result': 'from n2 (exit)'}
    
    def node3_func(state):
        print(f"🌩 执行节点3，当前状态: {state}")
        state['value'] += 5
        if random.random() < 0.7:
            next_action = random.choice(["n1", "n2"])
            print(f"节点3决定流转到: {next_action}")
            return next_action, {'result': 'from n3'}
        else:
            print("节点3决定退出")
            return None, {'result': 'from n3 (exit)'}
    
    n1 = Node(exec=node1_func)
    n2 = Node(exec=node2_func)
    n3 = Node(exec=node3_func)
    
    # 创建 Swarm
    s1 = Swarm()
    s1[n1, n2, n3]
    
    # 执行 Swarm
    state = {'initial': 'test'}
    result = s1.run(state, max_steps=20)
    
    print(f"最终状态: {state}")
    print(f"执行结果: {result}")
    
    # 验证执行结果
    assert 'value' in state, "状态中应该包含 value"
    assert state['value'] > 0, "value 应该大于 0"
    
    print("✓ Swarm 执行功能测试通过\n")

if __name__ == "__main__":
    test_swarm_basic_connections()
    test_swarm_in_workflow()
    test_swarm_composition()
    test_swarm_execution()
    print("所有 Swarm 测试完成！") 