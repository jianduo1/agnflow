import json
import asyncio
from xmltodict import parse

from agnflow.chatbot.type import ChatState, Tool
from agnflow.core import Node
from agnflow.agent.llm import stream_llm, SysMsg, UserMsg, get_tool_prompt, prompt_format, tool_map
from agnflow.chatbot.chatbot_db import chat_db


md = str

reasoning_system_prompt: md = """
你是一个深度思考型AI。请严格按以下步骤执行：
1. 完全理解问题
2. 在内心完成所有推理（用户不可见）
3. 最终用以下格式输出：
<reasoning>详细推理步骤</reasoning>
<conclusion>简洁结论</conclusion>

"""

tool_system_prompt: md = """
# 你是深度思考型AI助手，你具备以下优秀能力：
- 模拟人类解题步骤，把思考过程可视化
- 分步拆解复杂问题，每个子问题可以独立调用工具解决
- 多次工具调用返回的中间结果，可以设置为状态变量，用于后续计算
- **需要多次调用工具的情况，必须分步骤用tool/name/args等标签完整描述工具调用情况**

## 你可以调用以下工具：
<tools>

## 当前状态变量上下文
<state_context>

## 状态变量管理规范
- 获取状态变量作为工具调用参数：
<get_state>var_name</get_state>
- 把工具调用返回的中间结果设置为状态变量：
<set_state>var_name</set_state>

## 经典示例：
- 假设可用工具为：add，mul
- 用户提问：1+(2*3)=?
- AI回答：
我先计算2*3，我将调用工具 mul，参数为：{"a": 2, "b": 3}，把结果6存储到状态变量 result1 中
<tool>
  <name>mul</name>
  <args>
    <a>2</a>
    <b>3</b>
  </args>
  <set_state>result1</set_state>
</tool>
然后计算1+result1，我将会调用工具add，参数为：{"a": 1, "b": result1}
<tool>
  <name>add</name>
  <args>
    <a>1</a>
    <b><get_state>result1</get_state></b>
  </args>
  <set_state>result2</set_state>
</tool>
所以1+(2*3)=<get_state>result2</get_state>

"""

class ChatNode(Node):
    """流式对话节点"""

    async def aexec(self, state: "ChatState"):
        conversation = state.get("conversation", "")
        user_message = state.get("user_message", "")
        websocket = state.get("websocket")
        options = state.get("options", {})
        tool_map = state.get("tool_map", {})

        tool_context = state.get("tool_context", {})
        messages = state.get("messages", [])
        messages.append({"role": "user", "content": user_message})
        tool_xml = ""
        full_response = ""
        # 🔴发送开始消息
        await websocket.send_text(json.dumps({"type": "start", "content": ""}))

        # 🟢根据选项添加系统提示
        if options.get("reasoning", False):
            messages = SysMsg(reasoning_system_prompt) + UserMsg(messages)
        elif options.get("toolCall", False):
            prompt = prompt_format(
                prompt=tool_system_prompt,
                tools=get_tool_prompt(*tool_map.values()),
                state_context=tool_context,
            )
            messages = SysMsg(prompt) + UserMsg(messages)
        else:
            messages = UserMsg(messages)

        async for chunk_content in stream_llm(messages):
            full_response += chunk_content

            # 🔵解析工具调用
            tool_xml += chunk_content
            if "<tool>" in tool_xml:
                tool_xml = tool_xml[tool_xml.index("<tool>") :]
            if "</tool>" in tool_xml:
                tool_xml = tool_xml[: tool_xml.index("</tool>") + len("</tool>")]
                tool_dict = parse(tool_xml)
                tool: Tool = tool_dict.get("tool", {})
                name = tool.get("name")
                args = tool.get("args", {})
                set_state = tool.get("set_state", "")
                for k, v in args.items():
                    # args = {"b": {"get_state": "result1"}}
                    if isinstance(v, dict) and v.get("get_state"):
                        _v = v.get("get_state", "").strip()
                        args[k] = tool_context.get(_v)
                # pprint(tool_dict)
                if name in tool_map:
                    tool_func = tool_map[name]
                    for k, v in args.items():
                        if tool_func.__annotations__.get(k):
                            # 工具参数类型注解 tool_func.__annotations__[k] : typing.Annotated[int, '乘数']
                            typ = tool_func.__annotations__[k].__args__[0]
                            args[k] = typ(v)
                        else:
                            print(f"工具 {name} 参数 {k} 未找到注解")
                            raise ValueError(f"工具 {name} 参数 {k} 未找到注解")
                    # 支持同步异步
                    if asyncio.iscoroutinefunction(tool_func):
                        result = await tool_func(**args)
                    else:
                        result = tool_func(**args)
                    if set_state:
                        tool_context[set_state] = result
                else:
                    print(f"工具 {name} 未找到")
                tool_xml = ""

            # 🔴发送中间消息
            await websocket.send_text(json.dumps({"type": "chunk", "content": chunk_content}))

        # 🔴发送工具上下文消息
        if tool_context:
            chunk_content = f"<tool_context>{json.dumps(tool_context)}</tool_context>"
            full_response += chunk_content
            await websocket.send_text(json.dumps({"type": "chunk", "content": chunk_content}))

        # 🔴发送结束消息
        await websocket.send_text(json.dumps({"type": "end", "content": ""}))

        messages.append({"role": "assistant", "content": full_response})
        state["messages"] = messages

        # 保存聊天记录到数据库（新结构：分别插入 user/ai）
        await chat_db.save_message(conversation, "user", user_message)
        await chat_db.save_message(conversation, "ai", full_response)
