from typing import Annotated, Any, Literal, List, Dict, TypedDict, Union, overload
import os
import json
import yaml
from dotenv import load_dotenv
from openai import OpenAI
from langchain_qwq import ChatQwQ

load_dotenv()


class Msg(List[Dict[Literal["user", "system", "assistant"], str]]):
    """消息列表类，支持链式操作"""

    def __init__(self, msgs: "Msg"):
        super().__init__(msgs)

    def __add__(self, other: "Msg") -> "Msg":
        """重载加法运算符，支持消息列表的合并"""
        if isinstance(other, Msg):
            return Msg(list(self) + list(other))
        else:
            raise TypeError(f"不支持的类型: {type(other)}")


class UserMsg(Msg):
    """用户消息类，支持链式操作"""

    def __init__(self, content: str):
        super().__init__([{"user": content}])


class SysMsg(Msg):
    """系统消息类，支持链式操作"""

    def __init__(self, content: str):
        super().__init__([{"system": content}])


class AiMsg(Msg):
    """助手消息类，支持链式操作"""

    def __init__(self, content: str):
        super().__init__([{"assistant": content}])


def call_llm(
    user_prompt,
    system_prompt=None,
    model="glm-4-flashx-250414",
    output_format: Literal["yaml", "json", "text"] = "text",
):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    messages = [{"role": "user", "content": user_prompt}]
    if system_prompt:
        messages.insert(0, {"role": "system", "content": system_prompt})
    completion = client.chat.completions.create(model=model, messages=messages)
    res = completion.choices[0].message.content
    if output_format == "text":
        return res
    if output_format == "yaml":
        res = res.strip().removeprefix("```yaml").removesuffix("```").strip()
        return yaml.safe_load(res)
    elif output_format == "json":
        res = res.strip().removeprefix("```json").removesuffix("```").strip()
        return json.loads(res)
    raise ValueError(f"不支持的输出格式: {output_format}")


class JosnSchema(TypedDict):
    """可以通过doc或注解了解字段用途"""

    data: Annotated[str, "数据"]
    """数据"""


def llm_json_stream(
    message: str, json_schema: dict, history_msgs: List[Dict[str, Any]] = None, mdoel: Any = None, validation_func=None
):
    """
    双阶段流式输出：
    1. 第一阶段收集json（推理原因+合法性校验结果），仅用于校验。
    2. 校验通过后，第二阶段才流式输出实际内容。
    支持OpenAI、ChatQwQ等模型。
    """
    split_token = "---===---"

    if mdoel is None:
        raise ValueError("必须指定mdoel参数（OpenAI/ChatQwQ等）")
    if history_msgs is None:
        history_msgs = []
    if validation_func is None:

        def validation_func(x):
            return True

    # 组装消息格式
    if isinstance(mdoel, OpenAI):
        messages = history_msgs + [{"role": "user", "content": message}]
        prompt = f"请先以JSON格式输出如下schema的内容：{json.dumps(json_schema, ensure_ascii=False)}，然后输出正文内容。两部分之间用'{split_token}'分割。"
        messages[-1]["content"] = prompt + "\n" + messages[-1]["content"]
        response = mdoel.chat.completions.create(model="glm-4-flashx-250414", messages=messages, stream=True)
        buffer = ""
        json_block = ""
        in_json = True
        for chunk in response:
            delta = chunk.choices[0].delta.content or ""
            buffer += delta
            if in_json:
                json_block += delta
                if split_token in json_block:
                    json_str, rest = json_block.split(split_token, 1)
                    try:
                        json_obj = json.loads(json_str.strip())
                        if not validation_func(json_obj):
                            yield {"type": "error", "data": "JSON校验未通过"}
                            return
                        # 校验通过，开始流式输出正文
                        in_json = False
                        buffer = rest
                        break  # 跳出for，进入正文流式输出
                    except Exception as e:
                        yield {"type": "error", "data": f"JSON解析失败: {e}"}
                        return
        # 正文流式输出
        if buffer:
            yield {"type": "text", "data": buffer}
        for chunk in response:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                yield {"type": "text", "data": delta}
        return
    elif isinstance(mdoel, ChatQwQ):
        prompt = f"请先以JSON格式输出如下schema的内容：{json.dumps(json_schema, ensure_ascii=False)}，然后输出正文内容。两部分之间用'---'分割。"
        chat_input = message if isinstance(message, str) else json.dumps(message, ensure_ascii=False)
        full_prompt = prompt + "\n" + chat_input
        stream = mdoel.stream_chat(full_prompt, history=history_msgs)
        buffer = ""
        json_block = ""
        in_json = True
        stream_iter = iter(stream)
        while True:
            try:
                delta = next(stream_iter)
            except StopIteration:
                break
            buffer += delta
            if in_json:
                json_block += delta
                if split_token in json_block:
                    json_str, rest = json_block.split(split_token, 1)
                    try:
                        json_obj = json.loads(json_str.strip())
                        if not validation_func(json_obj):
                            yield {"type": "error", "data": "JSON校验未通过"}
                            return
                        in_json = False
                        buffer = rest
                        break
                    except Exception as e:
                        yield {"type": "error", "data": f"JSON解析失败: {e}"}
                        return
        # 正文流式输出
        if buffer:
            yield {"type": "text", "data": buffer}
        for delta in stream_iter:
            if delta:
                yield {"type": "text", "data": delta}
        return
    else:
        raise NotImplementedError(f"暂不支持的模型类型: {type(mdoel)}")


if __name__ == "__main__":
    # msgs = Msg([{"user": "你好"}]) + Msg([{"system": "你是谁"}]) + Msg([{"assistant": "我是AI"}])
    # msgs += UserMsg("你好2") + SysMsg("你是谁2") + AiMsg("我是AI2")
    # print("消息列表:", msgs)

    from openai import OpenAI

    def my_validation_func(js):
        return isinstance(js, dict) and js.get("valid") is True

    client = OpenAI()
    json_schema = {"reason": "str", "valid": "bool"}
    message = "请帮我写一个Python冒泡排序"
    print("OpenAI流式输出示例：")
    for chunk in llm_json_stream(
        message=message, json_schema=json_schema, history_msgs=[], mdoel=client, validation_func=my_validation_func
    ):
        if chunk["type"] == "json":
            print("校验信息：", chunk["data"])
        elif chunk["type"] == "text":
            print("正文流：", chunk["data"], end="", flush=True)
        elif chunk["type"] == "error":
            print("错误：", chunk["data"])

    # ChatQwQ 示例
    from langchain_qwq import ChatQwQ

    client2 = ChatQwQ(api_key="你的API_KEY")
    print("\nChatQwQ流式输出示例：")
    for chunk in llm_json_stream(
        message=message, json_schema=json_schema, history_msgs=[], mdoel=client2, validation_func=my_validation_func
    ):
        if chunk["type"] == "json":
            print("校验信息：", chunk["data"])
        elif chunk["type"] == "text":
            print("正文流：", chunk["data"], end="", flush=True)
        elif chunk["type"] == "error":
            print("错误：", chunk["data"])
