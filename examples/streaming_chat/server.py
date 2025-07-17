import importlib.resources
import json
from typing import Any, Callable, TypedDict
from pathlib import Path
from contextlib import asynccontextmanager
from redis.asyncio.client import PubSub
from agnflow.core import Node
from xmltodict import parse
import os

from agnflow.agent.llm import stream_llm, SysMsg, UserMsg, get_tool_prompt, prompt_format
from db import chat_db
import asyncio
import redis.asyncio as redis

# 聊天记录数据库文件路径
BASE_PATH = Path(__file__).parent

# Redis连接配置 - 支持环境变量
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

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
        messages = state.get("conversation_history", [])
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
                tool = tool_dict.get("tool", {})
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

        conversation_history = state.get("conversation_history", [])
        conversation_history.append({"role": "assistant", "content": full_response})
        state["conversation_history"] = conversation_history

        # 保存聊天记录到数据库（新结构：分别插入 user/ai）
        await chat_db.save_message(conversation, "user", user_message)
        await chat_db.save_message(conversation, "ai", full_response)


if __name__ == "__main__":
    import json
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse, JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    from agnflow.core import Flow
    import uvicorn

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
        conversation_history: list[str]  # 所有对话历史
        conversation: str  # 当前对话的ID
        user_message: str  # 当前对话的用户消息
        tool_map: dict[str, Callable]  # 工具调用映射
        tool_context: dict[str, Any]  # 工具调用上下文
        options: ChatOptions  # 聊天选项

    @asynccontextmanager
    async def lifespan(app):
        await chat_db.init_db()
        yield

    app = FastAPI(lifespan=lifespan)
    assets_path = importlib.resources.files("agnflow") / "assets"
    app.mount("/assets", StaticFiles(directory=str(assets_path)), name="assets")
    app.add_middleware(
        CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
    )

    @app.get("/zh")
    async def get_chat_interface():
        return FileResponse(assets_path / "index_zh.html")

    @app.get("/en")
    async def get_chat_interface_en():
        return FileResponse(assets_path / "index_en.html")

    @app.get("/api/conversations")
    async def get_conversations():
        rows = await chat_db.get_conversations()
        return JSONResponse([{"id": r[0], "created_at": r[1]} for r in rows])

    @app.post("/api/conversation")
    async def create_conversation():
        """创建会话"""
        conv_id = chat_db.create_conversation()
        return {"id": conv_id}

    @app.delete("/api/conversation/{conv_id}")
    async def delete_conversation(conv_id: str):
        """删除会话"""
        await chat_db.delete_conversation(conv_id)
        return {"status": "ok"}

    @app.get("/api/conversation/{conv_id}")
    async def get_conversation(conv_id: str):
        """获取会话历史记录"""
        messages = await chat_db.get_all_messages(conv_id)
        return JSONResponse(messages)

    @app.delete("/api/message/{msg_id}")
    async def delete_message(msg_id: int):
        await chat_db.delete_message(msg_id)
        return {"status": "ok"}

    # @app.websocket("/ws2")
    async def websocket_endpoint2(websocket: WebSocket):
        """WebSocket 连接端点"""
        await websocket.accept()

        # 前端需先发送会话ID
        data = await websocket.receive_text()
        msg = json.loads(data)
        conversation = msg.get("conversation")
        if not conversation:
            await websocket.close()
            return

        # 连接时自动加载历史记录并推送给前端
        for m in await chat_db.get_all_messages(conversation):
            msg = {"type": "history", **m}
            await websocket.send_text(json.dumps(msg))

        state_store = {"websocket": websocket, "conversation_history": [], "conversation": conversation}

        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)

                state_store["user_message"] = message.get("content", "")
                state_store["options"] = message.get("options", {})

                chat_node = ChatNode()
                flow = Flow()
                flow[chat_node]
                await flow.arun(state_store)
        except WebSocketDisconnect:
            pass

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()

        # 前端需先发送会话ID
        data = await websocket.receive_text()
        msg = json.loads(data)
        conversation = msg.get("conversation")
        if not conversation:
            await websocket.close()
            return

        # 连接时自动加载历史记录并推送给前端
        for m in await chat_db.get_all_messages(conversation):
            msg = {"type": "history", **m}
            await websocket.send_text(json.dumps(msg))

        state_store: ChatState = {
            "websocket": websocket,
            "conversation_history": [],
            "conversation": conversation,
            "tool_map": tool_map,
            "tool_context": {},
        }

        # 🔄 创建Redis pub/sub连接
        pubsub: PubSub = redis_client.pubsub()

        # 订阅会话频道
        channel_name = f"chat:{conversation}"
        await pubsub.subscribe(channel_name)

        # 📡 消息发布协程（事件发布者）
        async def publisher():
            try:
                while True:
                    data = await websocket.receive_text()
                    # 发布消息到Redis频道
                    await redis_client.publish(channel_name, data)
            except WebSocketDisconnect:
                # 断开时发布断开消息
                await redis_client.publish(channel_name, json.dumps({"type": "disconnect"}))

        # 📥 消息订阅协程（事件订阅者）
        async def subscriber():
            try:
                async for message in pubsub.listen():
                    if message["type"] == "message":
                        data = message["data"]
                        if data == '{"type": "disconnect"}':
                            break

                        # 处理接收到的消息
                        message_data = json.loads(data)
                        state_store["user_message"] = message_data.get("content", "")
                        state_store["options"] = message_data.get("options", {})

                        # 执行聊天处理
                        chat_node = ChatNode()
                        flow = Flow()
                        flow[chat_node]
                        await flow.arun(state_store)
            except Exception as e:
                print(f"订阅者错误: {e}")

        # 🚀 并发启动发布者和订阅者
        try:
            await asyncio.gather(publisher(), subscriber())
        finally:
            # 清理资源
            await pubsub.unsubscribe(channel_name)
            await pubsub.close()

    uvicorn.run(app, host="0.0.0.0", port=8000)
