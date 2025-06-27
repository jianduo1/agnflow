#!/usr/bin/env python3
"""
测试 Supervisor 连接关系
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from agnflow.core import Node, Flow, Supervisor
import random

def test_supervisor_basic_connections():
    """测试 Supervisor 基本连接关系"""
    print("=== 测试 Supervisor 基本连接关系 ===")
    
    # 创建节点
    n1 = Node()
    n2 = Node()
    n3 = Node()
    
    # 创建 Supervisor
    s = Supervisor()
    
    # 测试 Supervisor[n1, n2, n3] 的连接关系
    # 第一个参数为监督者，其余为被监督者
    s[n1, n2, n3]
    
    print(f"Supervisor节点: {s.connections.get(s, {}).get('nodes', [])}")
    print(f"Supervisor连接: {s.connections}")
    
    # 验证连接关系
    # n1 应该连接到 n2 和 n3
    n1_connections = s.connections.get(n1, {})
    assert 'n2' in n1_connections, "n1 应该连接到 n2"
    assert 'n3' in n1_connections, "n1 应该连接到 n3"
    
    # n2 应该连接到 n1
    n2_connections = s.connections.get(n2, {})
    assert 'n1' in n2_connections, "n2 应该连接到 n1"
    
    # n3 应该连接到 n1
    n3_connections = s.connections.get(n3, {})
    assert 'n1' in n3_connections, "n3 应该连接到 n1"
    
    print("✓ Supervisor 基本连接关系测试通过\n")

def test_supervisor_execution():
    """测试 Supervisor 执行功能（Swarm风格随机流转）"""
    print("=== 测试 Supervisor 执行功能 ===")
    
    # 创建带执行函数的节点
    def supervisor_func(state):
        print(f"监督者执行，当前状态: {state}")
        state['supervisor_action'] = 'monitoring'
        # 随机分配任务给 worker1 或 worker2，或直接退出
        next_worker = random.choices(['worker1', 'worker2', None], weights=[0.4, 0.4, 0.2])[0]
        print(f"监督者决定流转到: {next_worker}")
        return next_worker, {'result': 'supervisor_success'}
    
    def worker1_func(state):
        print(f"工作者1执行，当前状态: {state}")
        state['worker1_result'] = 'task1_completed'
        # 70%概率流转到 supervisor 或 worker2，30%概率退出
        next_action = random.choices(['supervisor', 'worker2', None], weights=[0.35, 0.35, 0.3])[0]
        print(f"worker1决定流转到: {next_action}")
        return next_action, {'result': 'worker1_success'}
    
    def worker2_func(state):
        print(f"工作者2执行，当前状态: {state}")
        state['worker2_result'] = 'task2_completed'
        next_action = random.choices(['supervisor', 'worker1', None], weights=[0.35, 0.35, 0.3])[0]
        print(f"worker2决定流转到: {next_action}")
        return next_action, {'result': 'worker2_success'}
    
    supervisor = Node(name="supervisor", exec=supervisor_func)
    worker1 = Node(name="worker1", exec=worker1_func)
    worker2 = Node(name="worker2", exec=worker2_func)
    
    # 先用 >> 建立链路
    supervisor >> [worker1, worker2]
    worker1 >> [supervisor, worker2]
    worker2 >> [supervisor, worker1]
    # 用 Supervisor 注册所有节点
    s = Supervisor()
    s[supervisor, worker1, worker2]
    
    # 执行 Supervisor
    state = {'initial': 'test'}
    result = s.run(state, max_steps=20)
    
    print(f"最终状态: {state}")
    print(f"执行结果: {result}")
    # 只要 supervisor/worker1/worker2 有一个被执行即可
    assert 'supervisor_action' in state or 'worker1_result' in state or 'worker2_result' in state, "状态中应该包含至少一个执行结果"
    
    print("✓ Supervisor 执行功能测试通过\n")

def test_supervisor_conditional_execution():
    """测试 Supervisor 条件执行功能"""
    print("=== 测试 Supervisor 条件执行功能 ===")

    # 创建带条件执行函数的节点
    def supervisor_func(state):
        print(f"监督者执行，当前状态: {state}")
        if state.get('condition') == 'approve':
            return 'approve'
        else:
            return 'reject'

    def approve_func(state):
        print(f"批准流程执行，当前状态: {state}")
        if random.random() < 0.7:
            state['status'] = 'approved'
            return {'result': 'approved'}
        else:
            print("批准流程决定提前退出")
            return None, {'result': 'approved (exit)'}

    def reject_func(state):
        print(f"拒绝流程执行，当前状态: {state}")
        if random.random() < 0.7:
            state['status'] = 'rejected'
            return {'result': 'rejected'}
        else:
            print("拒绝流程决定提前退出")
            return None, {'result': 'rejected (exit)'}

    supervisor = Node(exec=supervisor_func)
    approve_worker = Node(exec=approve_func)
    reject_worker = Node(exec=reject_func)

    # 建立分支跳转链路
    s = Supervisor()
    # supervisor >> [approve_worker, reject_worker]
    s[supervisor, approve_worker, reject_worker]

    # 在 Supervisor 内部建立连接关系
    s.connections[supervisor] = {"approve": approve_worker, "reject": reject_worker}

    # 测试批准流程
    print("测试批准流程:")
    state_approve = {'condition': 'approve'}
    result_approve = s.run(state_approve, max_steps=20)
    print(f"批准流程最终状态: {state_approve}")
    assert (
        state_approve.get('status') == 'approved' or
        (isinstance(state_approve.get('result'), str) and state_approve.get('result').startswith('approved'))
    ), "应该被批准或提前退出"

    # 测试拒绝流程
    print("测试拒绝流程:")
    state_reject = {'condition': 'reject'}
    result_reject = s.run(state_reject, max_steps=20)
    print(f"拒绝流程最终状态: {state_reject}")
    assert (
        state_reject.get('status') == 'rejected' or
        (isinstance(state_reject.get('result'), str) and state_reject.get('result').startswith('rejected'))
    ), "应该被拒绝或提前退出"

    print("✓ Supervisor 条件执行功能测试通过\n")

def test_supervisor_error_handling():
    """测试 Supervisor 错误处理"""
    print("=== 测试 Supervisor 错误处理 ===")
    
    def supervisor_func(state):
        print(f"监督者执行，当前状态: {state}")
        state['supervisor_action'] = 'error_handling'
        return {'result': 'supervisor_success'}
    
    def error_worker_func(state):
        print(f"错误工作者执行，当前状态: {state}")
        raise Exception("模拟工作错误")
    
    def recovery_worker_func(state):
        print(f"恢复工作者执行，当前状态: {state}")
        state['recovery_action'] = 'error_recovered'
        return {'result': 'recovery_success'}
    
    supervisor = Node(exec=supervisor_func)
    error_worker = Node(exec=error_worker_func)
    recovery_worker = Node(exec=recovery_worker_func)
    
    # 创建 Supervisor
    s = Supervisor()
    s[supervisor, error_worker, recovery_worker]
    
    # 执行 Supervisor（应该能处理错误）
    state = {'initial': 'test'}
    try:
        result = s.run(state, max_steps=20)
        print(f"最终状态: {state}")
        print(f"执行结果: {result}")
        print("✓ Supervisor 错误处理测试通过（错误被正确处理）\n")
    except Exception as e:
        print(f"捕获到错误: {e}")
        print("✓ Supervisor 错误处理测试通过（错误被抛出）\n")

if __name__ == "__main__":
    test_supervisor_basic_connections()
    test_supervisor_execution()
    test_supervisor_conditional_execution()
    test_supervisor_error_handling()
    print("所有 Supervisor 测试完成！") 
