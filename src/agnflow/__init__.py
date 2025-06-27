"""
Agnflow - 一个简洁的工作流引擎

用于构建和执行基于节点的异步工作流。
支持智能体算法和工作流编排的集成。
"""

from agnflow.core import Node, Flow, Supervisor,  Swarm

# 智能体工作流功能
try:
    from agnflow.agent.agents import (
        # 基础节点
        LLMNode, SearchNode, MemoryNode, RAGNode, ToolNode,
        # 高级工作流
        ReActWorkflow, TAOWorkflow, CoTWorkflow, RAGWorkflow,
        # 工厂函数
        create_llm_node, create_search_node, create_memory_node, 
        create_rag_node, create_tool_node,
        create_react_workflow, create_tao_workflow, 
        create_cot_workflow, create_rag_workflow
    )
    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False

# 工具函数
try:
    from agnflow.agent.utils import (
        call_llm, search_web_duckduckgo, search_web_brave,
        get_embedding, get_similarity,
        create_memory_system, create_rag_system, create_tool_manager,
        create_react_agent, create_tao_agent, create_tot_agent,
        create_cot_agent, create_hitl_agent, create_supervisor_swarm
    )
    UTILS_AVAILABLE = True
except ImportError:
    UTILS_AVAILABLE = False

__version__ = "0.1.2"

# 核心功能
__all__ = ["Node", "Flow", "Supervisor", "Swarm"]

# 如果智能体功能可用，添加到导出列表
if AGENTS_AVAILABLE:
    __all__.extend([
        "LLMNode", "SearchNode", "MemoryNode", "RAGNode", "ToolNode",
        "ReActWorkflow", "TAOWorkflow", "CoTWorkflow", "RAGWorkflow",
        "create_llm_node", "create_search_node", "create_memory_node",
        "create_rag_node", "create_tool_node",
        "create_react_workflow", "create_tao_workflow",
        "create_cot_workflow", "create_rag_workflow"
    ])

# 如果工具函数可用，添加到导出列表
if UTILS_AVAILABLE:
    __all__.extend([
        "call_llm", "search_web_duckduckgo", "search_web_brave",
        "get_embedding", "get_similarity",
        "create_memory_system", "create_rag_system", "create_tool_manager",
        "create_react_agent", "create_tao_agent", "create_tot_agent",
        "create_cot_agent", "create_hitl_agent", "create_supervisor_swarm"
    ])


def get_capabilities() -> dict:
    """获取当前安装的功能能力"""
    return {
        "core": True,
        "agents": AGENTS_AVAILABLE,
        "utils": UTILS_AVAILABLE,
        "version": __version__
    }
