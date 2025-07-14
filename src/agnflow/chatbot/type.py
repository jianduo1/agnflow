from typing import TypedDict, Callable, Any
from fastapi import WebSocket


class ChatOptions(TypedDict):
    reasoning: bool  # 是否开启推理
    toolCall: bool  # 是否开启工具调用
    imageDescription: bool  # 是否开启图像描述
    imageClassification: bool  # 是否开启图像分类
    visualReasoning: bool  # 是否开启视觉推理
    visualQA: bool  # 是否开启视觉问答
    imageSentiment: bool  # 是否开启图像情感分析

class ChatState(TypedDict):
    websocket: WebSocket  # 当前连接
    messages: list[str]  # 所有对话历史
    conversation: str  # 当前对话的ID
    user_message: str  # 当前对话的用户消息
    tool_map: dict[str, Callable]  # 工具调用映射
    tool_context: dict[str, Any]  # 工具调用上下文
    options: ChatOptions  # 聊天选项

class Tool(TypedDict):
    """工具"""
    name: str
    args: dict[str, Any]
    set_state: str
