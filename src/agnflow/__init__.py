"""
Agnflow - 一个简洁的工作流引擎

用于构建和执行基于节点的异步工作流。
"""

from .core import Node, Flow, Conn

__version__ = "0.1.0"
__all__ = ["Node", "Flow", "Conn"]

def hello() -> str:
    return "Hello from agnflow!"
