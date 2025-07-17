from typing import TypedDict, Callable, Any, Literal, TypeVar, IO

radio = TypeVar("radio", bound=list)
checkbox = TypeVar("checkbox", bound=list)
select = TypeVar("select", bound=str)
number = TypeVar("number", bound=int | float)
textarea = TypeVar("textarea", bound=str)
json = TypeVar("json", bound=dict)
file = TypeVar("file", bound=list)
image = TypeVar("image", bound=IO)
audio = TypeVar("audio", bound=IO)
video = TypeVar("video", bound=IO)
input = TypeVar("input", bound=str)
# print(type(radio))


class ChatOptions(TypedDict):
    reasoning: bool  # 是否开启推理
    toolCall: bool  # 是否开启工具调用
    imageDescription: bool  # 是否开启图像描述
    imageClassification: bool  # 是否开启图像分类
    visualReasoning: bool  # 是否开启视觉推理
    visualQA: bool  # 是否开启视觉问答
    imageSentiment: bool  # 是否开启图像情感分析


class ChatState(TypedDict):
    send_chunk: Callable  # 发送WebSocket消息
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
