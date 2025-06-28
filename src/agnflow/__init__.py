"""
Agnflow - 一个简洁的工作流引擎

用于构建和执行基于节点的异步工作流。
支持智能体算法和工作流编排的集成。
"""

from agnflow.core.flow import Flow, Supervisor, Swarm
from agnflow.core.node import Node
from agnflow.agent.hitl.api import get_hitl_router
from agnflow.agent.hitl.cli import human_in_the_loop, hitl

__version__ = "0.1.4"

__all__ = [
    "Node",
    "Flow",
    "Supervisor",
    "Swarm",
    "get_hitl_router",
    "human_in_the_loop",
    "hitl",
]
