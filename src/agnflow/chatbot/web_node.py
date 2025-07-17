from typing import get_origin, get_args, Literal, IO, Generic, Annotated
from json import dumps

from agnflow.core import Node
from agnflow.chatbot.chatbot_db import chat_db
from agnflow.core.type import StateType


class WebNode(Node[StateType], Generic[StateType]):
    """式对话节点

    功能：
    ⭐️ 支持WebSocket消息发送/接收
    ⭐️ 支持消息历史保存
    ⭐️ 支持前端卡片规范生成
    """

    async def send_text(self, type: str = "chunk", content: str = ""):
        """发送WebSocket消息"""
        from fastapi import WebSocket

        websocket: WebSocket = self.get_state("websocket", None)
        if websocket:
            await websocket.send_text(dumps({"type": type, "content": content}))

    async def recv_text(self):
        """接收WebSocket消息"""
        from fastapi import WebSocket

        websocket: WebSocket = self.get_state("websocket", None)
        if websocket:
            data: str = await websocket.receive_text()
            return data

    def update_messages(self, message: str):
        """更新消息历史"""
        messages = self.get_state("messages", [])
        messages += message
        self.set_state("messages", messages)

    async def save_message(self, conversation: str, role: str, content: str):
        """存消息到数据库"""
        await chat_db.save_message(conversation=conversation, role=role, content=content)

    async def get_history(self, conversation):
        """获取历史消息"""
        return await chat_db.get_all_messages(conversation=conversation)

    def get_agent_card_schema(self):
        """生成前端卡片规范"""
        import inspect
        from agnflow.chatbot.type import radio, checkbox, select, number, textarea, json, file, input

        sig = inspect.signature(self.aexec)
        ann = self.aexec.__annotations__
        
        # 使用新的 TypeVar 进行类型映射
        type_map = {
            input: "input",
            number: "number", 
            textarea: "textarea",
            json: "json",
            file: "file",
            select: "select",
            radio: "radio",
            checkbox: "checkbox",
            # 保留原有基础类型支持
            str: "input",
            int: "number",
            float: "number",
            bool: "checkbox",
            dict: "json",
            list: "textarea",
        }
        
        fields = []
        for name, param in sig.parameters.items():
            if name == "self":
                continue
                
            typ = ann.get(name, input)
            field_type = type_map.get(typ, "input")
            options = None
            label = name  # 默认使用参数名作为标签

            # 处理 Annotated 类型
            origin = get_origin(typ)
            if origin is Annotated:
                args = get_args(typ)
                if len(args) >= 2:
                    base_type = args[0]  # 实际类型
                    description = args[1]  # 描述文本
                    label = description  # 使用描述作为标签
                    
                    # 处理基础类型
                    field_type = type_map.get(base_type, "input")
                    
                    # 如果基础类型是 Literal，继续处理选项
                    if get_origin(base_type) is Literal:
                        field_type = "select"
                        options = list(get_args(base_type))
                    
                    # 处理文件类型
                    if base_type is IO or (hasattr(base_type, "__name__") and base_type.__name__ == "IO"):
                        field_type = "file"
                    # 处理 bool 类型，强制为 checkbox
                    if base_type is bool:
                        field_type = "checkbox"
                        options = None
            
            # 处理非 Annotated 的 Literal 类型
            elif origin is Literal:
                field_type = "select"
                options = list(get_args(typ))

            # 处理非 Annotated 的文件类型
            elif typ is IO or (hasattr(typ, "__name__") and typ.__name__ == "IO"):
                field_type = "file"
            # 处理 bool 类型，强制为 checkbox
            elif typ is bool:
                field_type = "checkbox"
                options = None

            # 允许通过 default 传递 options
            default = param.default if param.default is not inspect.Parameter.empty else None
            if isinstance(default, (list, tuple)) and field_type in ("select", "radio", "checkbox"):
                options = list(default)

            required = param.default is inspect.Parameter.empty
            field = {
                "name": name,
                "label": label,
                "type": field_type,
                "required": required,
                "placeholder": f"请输入{label}",
                "example": default,
                "default": default,
            }
            if options:
                field["options"] = options
            fields.append(field)
        return {
            "name": self.name,
            "label": self.__doc__,
            "fields": fields
        }