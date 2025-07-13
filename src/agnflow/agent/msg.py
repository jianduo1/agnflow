import json
import base64
from typing import Annotated, Callable, Literal, List, Dict, get_args, overload, Any

from agnflow.utils.pprint import pprint


class Msg(List[Dict[Literal["user", "system", "assistant"], str]]):
    """消息列表类，支持链式操作
    UserMsg("你好") == [{"role": "user", "content": "你好"}]
    SysMsg("你是谁") == [{"role": "system", "content": "你是谁"}]
    AiMsg("我是AI") == [{"role": "assistant", "content": "我是AI"}]
    """

    role = ""
    type = None

    def __init_subclass__(cls, role: str, type: str = None) -> None:
        cls.role = role
        cls.type = type

    @overload
    def __init__(self, content: str): ...
    @overload
    def __init__(self, content: str, url: str = None): ...
    @overload
    def __init__(self, msg: "Msg"): ...

    def __init__(self, content_or_msg: Any = None, url: str = None):
        if isinstance(content_or_msg, Msg):
            messages = list(content_or_msg)
        elif self.type and url:
            # 处理本地图片或视频
            if not url.startswith("http"):
                with open(url, "rb") as img_file:
                    url = base64.b64encode(img_file.read()).decode("utf-8")

            if self.type == "image":
                content = [{"type": "image_url", "image_url": {"url": url}}, {"type": "text", "text": content_or_msg}]
            elif self.type == "video":
                content = []
                if url:
                    content.append({"type": "video_url", "video_url": {"url": url}})
                if content_or_msg:
                    content.append({"type": "text", "text": content_or_msg})
            elif self.type == "audio":
                content = [{"type": "input_audio", "input_audio": {"data": url, "format": "wav"}}]
            else:
                raise ValueError(f"不支持的类型: {self.type}")
            messages = [{"role": self.role, "content": content}]
        elif isinstance(content_or_msg, str):
            messages: List[Dict[str, str]] = [{"role": self.role, "content": content_or_msg}]
        else:
            messages = content_or_msg
        super().__init__(messages)

    def __add__(self, msg: "Msg") -> "Msg":
        """重载加法运算符，支持消息列表的合并"""
        if isinstance(msg, (Msg, list)):
            return Msg(list(self) + list(msg))
        else:
            raise TypeError(f"不支持的类型: {type(msg)}")


class UserMsg(Msg, role="user"):
    """用户消息类
    ```json
    [{
        "role": "user",
        "content": <content>
    }]
    ```
    """


class ImageMsg(Msg, role="user", type="image"):
    """图片消息类
    ```json
    [{
        "role": "user",
        "content": [
            {"type": "image", "image_url": {"url": <image_url>}},
            {"type": "text", "text": <text>}
        ]
    }]
    ```
    """


class VideoMsg(Msg, role="user", type="video"):
    """视频消息类
    ```json
    [{
        "role": "user",
        "content": [
            {"type": "video", "video_url": {"url": <video_url>}},
            {"type": "text", "text": <text>}
        ]
    }]
    ```
    """


class AudioMsg(Msg, role="user", type="audio"):
    """音频消息类
    ```json
    [{
        "role": "user",
        "content": [
            {"type": "input_audio", "input_audio": {"data": "<base64_string>", "format":"wav"}}
        ]
    }]
    ```
    """


class SysMsg(Msg, role="system"):
    """系统消息类
    ```json
    [{
        "role": "system",
        "content": <content>
    }]
    ```
    """


class AiMsg(Msg, role="assistant"):
    """助手消息类
    ```json
    [{
        "role": "assistant",
        "content": <content>
    }]
    ```
    """


tool_type_map = {
    int: "integer",
    float: "number",
    str: "string",
    bool: "boolean",
    list: "array",
    tuple: "array",
    dict: "object",
}


def inject_tool(func: Callable):
    properties = {}
    required = []
    for i, (name, typ) in enumerate(func.__annotations__.items()):
        if i >= func.__code__.co_argcount:
            continue
        args = get_args(typ)
        if len(args) != 2:
            continue
        properties[name] = {"type": tool_type_map[args[0]], "description": args[1]}
        if i >= func.__code__.co_argcount - len(func.__defaults__ or []):
            idx = i - (func.__code__.co_argcount - len(func.__defaults__ or []))
            properties[name]["default"] = func.__defaults__[idx]
        else:
            required.append(name)
    schema = {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": func.__doc__,
            "parameters": {"type": "object", "properties": properties, "required": required},
        },
    }
    func.schema = schema
    func.json_schema = json.dumps(schema, ensure_ascii=False)
    func.json_schema_pretty = json.dumps(schema, indent=2, ensure_ascii=False)
    return func


if __name__ == "__main__":
    msgs = (
        UserMsg("你好2")
        + SysMsg("你是谁2")
        + AiMsg("我是AI2")
        + ImageMsg("图片里面是什么", "https://www.baidu.com/img/flexible/logo/pc/result.png")
        + VideoMsg("视频里面是什么", "https://www.baidu.com/img/flexible/logo/pc/result.png")
    )
    # pprint(msgs)
    # print(AiMsg(UserMsg(Msg("123"))))

    @inject_tool
    def query_train_info(
        departure: Annotated[str, "出发城市或车站"],
        destination: Annotated[str, "目的地城市或车站"],
        date: Annotated[str, "要查询的火车日期"] = None,
    ) -> str:
        """根据用户提供的信息查询火车时刻"""
        return "火车时刻"

    # pprint(query_train_info.schema)
    # pprint(query_train_info.json_schema)

    # url = "assets/hello.mp3"
    # with open(url, "rb") as img_file:
    #     url = base64.b64encode(img_file.read()).decode("utf-8")
    # pprint(url)
