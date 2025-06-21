#!/usr/bin/env python3
"""
测试 agnflow 包安装和基本功能
"""

def test_agnflow_import():
    """测试 agnflow 导入"""
    try:
        from agnflow import Node, Flow, Conn
        print("✅ agnflow 导入成功")
        print(f"   - Node: {Node}")
        print(f"   - Flow: {Flow}")
        print(f"   - Conn: {Conn}")
        return True
    except ImportError as e:
        print(f"❌ agnflow 导入失败: {e}")
        return False

def test_basic_workflow():
    """测试基本工作流"""
    try:
        from agnflow import Node, Flow
        
        def hello_exec(state):
            print(f"Hello from agnflow! State: {state}")
            return {"msg": "world"}
        
        def world_exec(state):
            print(f"World from agnflow! State: {state}")
            return {"result": "success"}
        
        # 创建节点
        n1 = Node("hello", exec=hello_exec)
        n2 = Node("world", exec=world_exec)
        
        # 连接节点
        n1 >> n2
        
        # 创建工作流
        flow = Flow(n1, name="test_flow")
        
        # 运行工作流
        result = flow.run({"data": "test"})
        
        print("✅ 基本工作流测试成功")
        print(f"   结果: {result}")
        return True
        
    except Exception as e:
        print(f"❌ 基本工作流测试失败: {e}")
        return False

def test_flowchart_rendering():
    """测试流程图渲染"""
    try:
        from agnflow import Node, Flow
        
        def node1(state):
            return "next", {"step": 1}
        
        def node2(state):
            return "end", {"step": 2}
        
        n1 = Node("start", exec=node1)
        n2 = Node("end", exec=node2)
        n1 >> {"next": n2}
        
        flow = Flow(n1, name="render_test")
        
        # 生成流程图
        dot_output = flow.render_dot()
        mermaid_output = flow.render_mermaid()
        
        print("✅ 流程图渲染测试成功")
        print(f"   Dot 输出长度: {len(dot_output)} 字符")
        print(f"   Mermaid 输出长度: {len(mermaid_output)} 字符")
        return True
        
    except Exception as e:
        print(f"❌ 流程图渲染测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始测试 agnflow 包...")
    print("=" * 50)
    
    # 测试导入
    import_success = test_agnflow_import()
    
    if import_success:
        # 测试基本工作流
        workflow_success = test_basic_workflow()
        
        # 测试流程图渲染
        render_success = test_flowchart_rendering()
        
        print("=" * 50)
        if workflow_success and render_success:
            print("🎉 所有测试通过！agnflow 包工作正常")
        else:
            print("⚠️  部分测试失败，请检查包安装")
    else:
        print("❌ 导入失败，请检查包是否正确安装")
    
    print("=" * 50) 