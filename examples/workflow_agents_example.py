#!/usr/bin/env python3
"""
智能体工作流集成示例
展示如何使用工作流编排的智能体功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from agnflow.agents import (
    create_react_workflow, create_tao_workflow, create_cot_workflow, create_rag_workflow,
    create_llm_node, create_search_node, create_memory_node, create_rag_node, create_tool_node,
    LLMNode, SearchNode, MemoryNode, RAGNode, ToolNode
)
from agnflow.core import Flow
from agnflow.utils import create_tool_manager


def example_basic_nodes():
    """示例：基础节点使用"""
    print("## 基础节点示例")
    print("=" * 50)
    
    # 创建基础节点
    llm_node = create_llm_node("my_llm", system_prompt="你是一个有用的助手")
    search_node = create_search_node("my_search")
    memory_node = create_memory_node("my_memory")
    
    # 构建简单工作流
    llm_node >> "default" >> search_node >> "default" >> memory_node
    
    # 创建Flow
    flow = Flow(start=llm_node, name="basic_workflow")
    
    # 运行工作流
    state = {
        "prompt": "什么是人工智能？",
        "query": "人工智能最新发展",
        "memory_action": "add",
        "role": "user",
        "content": "询问了人工智能相关问题"
    }
    
    result = flow.run(state)
    print(f"工作流结果: {result}")
    print(f"LLM响应: {state.get('llm_response', 'N/A')}")
    print(f"搜索结果: {state.get('search_results', 'N/A')[:100]}...")
    print(f"记忆状态: {state.get('memory_status', 'N/A')}")


def example_react_workflow():
    """示例：ReAct工作流"""
    print("\n## ReAct工作流示例")
    print("=" * 50)
    
    # 创建工具管理器并注册一些工具
    tool_manager = create_tool_manager()
    
    def add_numbers(a, b):
        return a + b
    
    def multiply_numbers(a, b):
        return a * b
    
    tool_manager.register_tool("add", "将两个数字相加", add_numbers, {"a": "int", "b": "int"})
    tool_manager.register_tool("multiply", "将两个数字相乘", multiply_numbers, {"a": "int", "b": "int"})
    
    # 创建ReAct工作流
    react_workflow = create_react_workflow(tool_manager)
    
    # 解决问题
    result = react_workflow.solve("计算 15 + 27 的结果")
    
    print(f"ReAct工作流结果:")
    print(f"  最终结果: {result.get('final_result', 'N/A')}")
    print(f"  思考次数: {result.get('iterations', 0)}")
    print(f"  思考过程: {len(result.get('thoughts', []))} 步")
    print(f"  执行动作: {len(result.get('actions', []))} 次")


def example_tao_workflow():
    """示例：TAO工作流"""
    print("\n## TAO工作流示例")
    print("=" * 50)
    
    # 创建TAO工作流
    tao_workflow = create_tao_workflow()
    
    # 解决问题
    result = tao_workflow.solve("解释什么是机器学习")
    
    print(f"TAO工作流结果:")
    print(f"  最终结果: {result.get('final_result', 'N/A')}")
    print(f"  思考次数: {result.get('iterations', 0)}")
    print(f"  思考过程: {len(result.get('thoughts', []))} 步")
    print(f"  执行动作: {len(result.get('actions', []))} 次")
    print(f"  观察次数: {len(result.get('observations', []))} 次")


def example_cot_workflow():
    """示例：CoT工作流"""
    print("\n## CoT工作流示例")
    print("=" * 50)
    
    # 创建CoT工作流
    cot_workflow = create_cot_workflow(max_steps=3)
    
    # 解决问题
    result = cot_workflow.solve("如果我有5个苹果，给了朋友2个，然后又买了3个，现在我有多少个苹果？")
    
    print(f"CoT工作流结果:")
    print(f"  最终答案: {result.get('final_answer', 'N/A')}")
    print(f"  思考步骤: {result.get('steps', 0)}")
    print(f"  思考过程: {len(result.get('thoughts', []))} 步")


def example_rag_workflow():
    """示例：RAG工作流"""
    print("\n## RAG工作流示例")
    print("=" * 50)
    
    # 创建RAG工作流
    rag_workflow = create_rag_workflow()
    
    # 准备文档
    documents = [
        "人工智能是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。",
        "机器学习是人工智能的一个子领域，通过算法让计算机从数据中学习模式和规律。",
        "深度学习是机器学习的一个分支，使用多层神经网络来学习复杂的模式。",
        "自然语言处理是人工智能的一个重要应用领域，专注于让计算机理解和生成人类语言。"
    ]
    
    # 解决问题
    result = rag_workflow.solve("什么是机器学习？", documents)
    
    print(f"RAG工作流结果:")
    print(f"  答案: {result.get('answer', 'N/A')}")
    print(f"  检索文档数: {len(result.get('retrieved_documents', []))}")
    print(f"  查询嵌入: {result.get('query_embedding', 'N/A')}")


def example_custom_workflow():
    """示例：自定义工作流"""
    print("\n## 自定义工作流示例")
    print("=" * 50)
    
    # 创建自定义节点
    def custom_analysis_node(state):
        """自定义分析节点"""
        query = state.get("query", "")
        search_results = state.get("search_results", "")
        
        if query and search_results:
            analysis = f"分析查询 '{query}' 的搜索结果，找到了相关信息。"
            return {"analysis": analysis}
        return {"error": "缺少必要参数"}
    
    # 构建自定义工作流
    search_node = create_search_node("search")
    analysis_node = Node(name="analysis", exec=custom_analysis_node)
    llm_node = create_llm_node("summary", system_prompt="基于分析结果生成摘要")
    
    # 连接节点
    search_node >> "default" >> analysis_node >> "default" >> llm_node
    
    # 创建Flow
    flow = Flow(start=search_node, name="custom_workflow")
    
    # 运行工作流
    state = {
        "query": "Python编程语言",
        "prompt": "请总结搜索结果"
    }
    
    result = flow.run(state)
    print(f"自定义工作流结果: {result}")
    print(f"分析结果: {state.get('analysis', 'N/A')}")
    print(f"摘要: {state.get('llm_response', 'N/A')}")


def example_workflow_visualization():
    """示例：工作流可视化"""
    print("\n## 工作流可视化示例")
    print("=" * 50)
    
    # 创建一个复杂的工作流
    start_node = create_llm_node("start", system_prompt="开始分析")
    search_node = create_search_node("search")
    memory_node = create_memory_node("memory")
    end_node = create_llm_node("end", system_prompt="生成最终报告")
    
    # 构建分支工作流
    start_node >> "search" >> search_node >> "default" >> memory_node >> "default" >> end_node
    start_node >> "direct" >> end_node
    
    # 创建Flow
    flow = Flow(start=start_node, name="visualization_workflow")
    
    # 生成可视化
    print("生成DOT格式:")
    dot_str = flow.render_dot()
    print(dot_str[:200] + "..." if len(dot_str) > 200 else dot_str)
    
    print("\n生成Mermaid格式:")
    mermaid_str = flow.render_mermaid()
    print(mermaid_str[:200] + "..." if len(mermaid_str) > 200 else mermaid_str)


def main():
    """主函数"""
    print("智能体工作流集成示例")
    print("=" * 60)
    
    try:
        # 运行各种示例
        example_basic_nodes()
        example_react_workflow()
        example_tao_workflow()
        example_cot_workflow()
        example_rag_workflow()
        example_custom_workflow()
        example_workflow_visualization()
        
        print("\n" + "=" * 60)
        print("✅ 所有示例运行完成！")
        
    except Exception as e:
        print(f"❌ 示例运行出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 