import json
import asyncio
import os
import redis.asyncio as redis
from redis.asyncio.client import PubSub
from fastapi import WebSocket, WebSocketDisconnect

from agnflow.chatbot.chatbot_db import chat_db
from agnflow.agent.llm import tool_map
from agnflow.core import Flow
from agnflow.chatbot.chat_node import ChatNode
from agnflow.chatbot.type import ChatState


# Redis连接配置 - 支持环境变量
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)


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
        "messages": [],
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
        await pubsub.aclose()

