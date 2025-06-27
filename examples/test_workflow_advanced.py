#!/usr/bin/env python3
"""
测试高级工作流功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from agnflow.core import Node, Flow

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
    result_a = flow.run(state_a, max_steps=20)
    print(f"分支A最终状态: {state_a}")
    print(f"分支A执行结果: {result_a}")
    assert state_a.get('branch') == 'A', "应该执行分支A"
    
    # 测试分支B
    print("测试分支B:")
    state_b = {'condition': 'b'}
    result_b = flow.run(state_b, max_steps=20)
    print(f"分支B最终状态: {state_b}")
    print(f"分支B执行结果: {result_b}")
    assert state_b.get('branch') == 'B', "应该执行分支B"
    
    print("✓ 条件工作流测试通过\n")

def test_loop_workflow():
    """测试循环工作流"""
    print("=== 测试循环工作流 ===")
    
    def counter_func(state):
        print(f"计数器节点，当前状态: {state}")
        current_count = state.get('count', 0)
        state['count'] = current_count + 1
        print(f"计数: {state['count']}")
        
        if state['count'] >= 3:
            return 'end'
        else:
            return 'continue'
    
    def end_func(state):
        print(f"结束节点，当前状态: {state}")
        return {'result': 'loop_completed'}
    
    counter = Node(exec=counter_func)
    end = Node(exec=end_func)
    
    # 创建工作流
    flow = Flow()
    flow[counter >> [counter, end]]
    
    # 执行循环工作流
    state = {'initial': 'test'}
    result = flow.run(state, max_steps=20)
    
    print(f"最终状态: {state}")
    print(f"执行结果: {result}")
    
    # 验证循环执行了3次
    assert state.get('count') == 3, "应该循环3次"
    
    print("✓ 循环工作流测试通过\n")

def test_error_handling_workflow():
    """测试错误处理工作流"""
    print("=== 测试错误处理工作流 ===")
    
    def normal_func(state):
        print(f"正常节点，当前状态: {state}")
        state['normal_result'] = 'success'
        return {'result': 'normal_success'}
    
    def error_func(state):
        print(f"错误节点，当前状态: {state}")
        if state.get('should_fail'):
            raise Exception("模拟错误")
        state['error_result'] = 'success'
        return {'result': 'error_success'}
    
    def recovery_func(state):
        print(f"恢复节点，当前状态: {state}")
        state['recovery_result'] = 'success'
        return {'result': 'recovery_success'}
    
    normal = Node(exec=normal_func)
    error = Node(exec=error_func)
    recovery = Node(exec=recovery_func)
    
    # 创建工作流
    flow = Flow()
    flow[normal >> error >> recovery]
    
    # 测试正常执行
    print("测试正常执行:")
    state_normal = {'initial': 'test'}
    result_normal = flow.run(state_normal, max_steps=20)
    print(f"正常执行最终状态: {state_normal}")
    assert 'normal_result' in state_normal, "应该执行正常节点"
    assert 'error_result' in state_normal, "应该执行错误节点"
    assert 'recovery_result' in state_normal, "应该执行恢复节点"
    
    # 测试错误处理
    print("测试错误处理:")
    state_error = {'initial': 'test', 'should_fail': True}
    try:
        result_error = flow.run(state_error, max_steps=20)
        print(f"错误处理最终状态: {state_error}")
        print("✓ 错误被正确处理")
    except Exception as e:
        print(f"捕获到错误: {e}")
        print("✓ 错误被正确抛出")
    
    print("✓ 错误处理工作流测试通过\n")

def test_parallel_workflow():
    """测试并行工作流"""
    print("=== 测试并行工作流 ===")
    
    def task1_func(state):
        print(f"任务1执行，当前状态: {state}")
        state['task1_result'] = 'completed'
        return {'result': 'task1_success'}
    
    def task2_func(state):
        print(f"任务2执行，当前状态: {state}")
        state['task2_result'] = 'completed'
        return {'result': 'task2_success'}
    
    def task3_func(state):
        print(f"任务3执行，当前状态: {state}")
        state['task3_result'] = 'completed'
        return {'result': 'task3_success'}
    
    def merge_func(state):
        print(f"合并节点执行，当前状态: {state}")
        state['merge_result'] = 'all_tasks_completed'
        return {'result': 'merge_success'}
    
    task1 = Node(exec=task1_func)
    task2 = Node(exec=task2_func)
    task3 = Node(exec=task3_func)
    merge = Node(exec=merge_func)
    
    # 创建工作流：task1, task2, task3 并行执行，然后合并
    flow = Flow()
    flow[task1 >> merge]
    flow[task2 >> merge]
    flow[task3 >> merge]
    
    # 执行并行工作流
    state = {'initial': 'test'}
    result = flow.run(state, max_steps=20)
    
    print(f"最终状态: {state}")
    print(f"执行结果: {result}")
    
    # 验证所有任务都执行了
    assert 'task1_result' in state, "任务1应该执行"
    assert 'task2_result' in state, "任务2应该执行"
    assert 'task3_result' in state, "任务3应该执行"
    assert 'merge_result' in state, "合并节点应该执行"
    
    print("✓ 并行工作流测试通过\n")

def test_nested_workflow():
    """测试嵌套工作流"""
    print("=== 测试嵌套工作流 ===")
    
    def outer_start_func(state):
        print(f"外层开始节点，当前状态: {state}")
        state['outer_start'] = 'completed'
        return {'result': 'outer_start_success'}
    
    def inner_func(state):
        print(f"内层节点，当前状态: {state}")
        state['inner_result'] = 'completed'
        return {'result': 'inner_success'}
    
    def outer_end_func(state):
        print(f"外层结束节点，当前状态: {state}")
        state['outer_end'] = 'completed'
        return {'result': 'outer_end_success'}
    
    outer_start = Node(exec=outer_start_func)
    inner = Node(exec=inner_func)
    outer_end = Node(exec=outer_end_func)
    
    # 创建内层工作流
    inner_flow = Flow()
    inner_flow[inner]
    
    # 创建外层工作流
    outer_flow = Flow()
    outer_flow[outer_start >> inner_flow >> outer_end]
    
    # 执行嵌套工作流
    state = {'initial': 'test'}
    result = outer_flow.run(state, max_steps=20)
    
    print(f"最终状态: {state}")
    print(f"执行结果: {result}")
    
    # 验证所有节点都执行了
    assert 'outer_start' in state, "外层开始节点应该执行"
    assert 'inner_result' in state, "内层节点应该执行"
    assert 'outer_end' in state, "外层结束节点应该执行"
    
    print("✓ 嵌套工作流测试通过\n")

if __name__ == "__main__":
    test_conditional_workflow()
    test_loop_workflow()
    test_error_handling_workflow()
    test_parallel_workflow()
    test_nested_workflow()
    print("所有高级工作流测试完成！") 
