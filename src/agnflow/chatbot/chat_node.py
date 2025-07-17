"""
继承关系
ChatNode/VisionNode -> WebNode -> Node -> Connection
"""

import json
import asyncio
from xmltodict import parse

from agnflow.chatbot.type import ChatOptions, Tool
from agnflow.core import Node
from agnflow.agent.llm import AiMsg, stream_llm, SysMsg, UserMsg, get_tool_prompt, prompt_format, tool_map
from agnflow.chatbot.web_node import WebNode

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


class ChatNode(WebNode):
    """流式对话节点"""

    async def aexec(
        self,
        conversation: str = "",
        user_message: str = "",
        options: ChatOptions = {},
        tool_map: dict = {},
        tool_context: dict = {},
        messages: list = [],
    ):
        # 📮 发送开始消息
        await self.send_text(type="start", content="")
        try:
            # 获取会话相关信息
            messages += UserMsg(user_message)  # 添加本轮用户消息
            tool_xml = ""  # 工具调用的XML片段缓存
            full_response = ""  # AI完整回复内容

            # 🟢根据选项添加系统提示
            if options.get("reasoning", False):
                # 推理模式，添加推理系统提示
                messages = SysMsg(reasoning_system_prompt) + UserMsg(messages)
            elif options.get("toolCall", False):
                # 工具调用模式，拼接工具系统提示
                tools = get_tool_prompt(*tool_map.values())
                prompt: str = prompt_format(prompt=tool_system_prompt, tools=tools, state_context=tool_context)
                messages = SysMsg(prompt) + UserMsg(messages)
            else:
                # 普通对话模式
                messages = UserMsg(messages)

            # 🔄流式获取LLM回复
            async for chunk_content in stream_llm(messages):
                full_response += chunk_content  # 累加完整回复

                # 🔵解析工具调用（如有）
                tool_xml += chunk_content  # 拼接XML片段
                if "<tool>" in tool_xml:
                    # 只保留最后一个<tool>标签之后的内容
                    tool_xml = tool_xml[tool_xml.index("<tool>") :]
                if "</tool>" in tool_xml:
                    # 截取完整的<tool>...</tool>片段
                    tool_xml = tool_xml[: tool_xml.index("</tool>") + len("</tool>")]
                    tool_dict = parse(tool_xml)  # 解析XML为字典
                    tool: Tool = tool_dict.get("tool", {})
                    name = tool.get("name")  # 工具名
                    args = tool.get("args", {})  # 工具参数
                    set_state = tool.get("set_state", "")  # 工具结果存储变量名
                    for k, v in args.items():
                        # 处理参数中引用状态变量的情况
                        if isinstance(v, dict) and v.get("get_state"):
                            _v = v.get("get_state", "").strip()
                            args[k] = tool_context.get(_v)
                    # 检查工具是否存在
                    if name in tool_map:
                        tool_func = tool_map[name]
                        for k, v in args.items():
                            # 工具参数类型转换（根据注解）
                            if tool_func.__annotations__.get(k):
                                typ = tool_func.__annotations__[k].__args__[0]
                                args[k] = typ(v)
                            else:
                                print(f"工具 {name} 参数 {k} 未找到注解")
                                raise ValueError(f"工具 {name} 参数 {k} 未找到注解")
                        # 支持同步/异步工具
                        if asyncio.iscoroutinefunction(tool_func):
                            result = await tool_func(**args)
                        else:
                            result = tool_func(**args)
                        # 工具结果存入上下文
                        if set_state:
                            tool_context[set_state] = result
                    else:
                        print(f"工具 {name} 未找到")
                    tool_xml = ""  # 清空XML缓存

                # 📮 发送中间消息（流式推送给前端）
                await self.send_text(type="chunk", content=chunk_content)

            # 📮 发送工具上下文消息（如有工具调用结果）
            if tool_context:
                chunk_content = f"<tool_context>{json.dumps(tool_context)}</tool_context>"
                full_response += chunk_content
                await self.send_text(type="chunk", content=chunk_content)

            # 更新消息历史
            messages += AiMsg(full_response)
            self.set_state("messages", messages)

            # 保存聊天记录到数据库（新结构：分别插入 user/ai）
            await self.save_message(conversation=conversation, role="user", content=user_message)
            await self.save_message(conversation=conversation, role="ai", content=full_response)
        except Exception as e:
            print(f"📮 发生错误: {e}")
        finally:
            # 📮 发送结束消息
            await self.send_text(type="end", content="")
