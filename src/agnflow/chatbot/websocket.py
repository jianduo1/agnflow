"""
┌────────────┐         ┌────────────┐
│  客户端A    │         │   客户端B   │
└─────┬──────┘         └─────┬──────┘
      │                      │
      │ WebSocket连接         │ WebSocket连接
      ▼                      ▼
┌─────────────────────────────────────┐
│           FastAPI后端服务            │
│ ┌──────────────┐   ┌──────────────┐ │
│ │ publisher()  │   │ subscriber() │ │
│ └─────┬────────┘   └─────┬────────┘ │
└───────┼──────────────────┼──────────┘
        │                  │
        │    发布/订阅消息   │
        ▼                  ▼
    ┌──────────────────────────┐
    │        Redis Pub/Sub     │
    └──────────────────────────┘
"""

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


async def publisher(state: ChatState):
    """发布者协程，将WebSocket消息发布到Redis频道"""
    channel = f"chat:{state['conversation']}"

    try:
        while True:
            data: dict = json.loads(await state["websocket"].receive_text())
            # 发布消息到Redis频道
            await redis_client.publish(channel=channel, message=json.dumps(data))
            # print(f"🟢 websocket -> redis 发布消息: \n{data}")
    except WebSocketDisconnect:
        # 断开时发布断开消息
        await redis_client.publish(channel=channel, message=json.dumps({"type": "disconnect"}))


async def subscriber(state: ChatState):
    """订阅者协程，从Redis频道接收消息并处理"""
    channel = f"chat:{state['conversation']}"

    pubsub: PubSub = redis_client.pubsub()
    await pubsub.subscribe(channel)
    try:
        async for message in pubsub.listen():
            # print(f"🟢 redis -> workflow 接收消息: \n{message}")
            if message["type"] == "message":
                data: str = message["data"]
                if data == '{"type": "disconnect"}':
                    break

                # 处理接收到的消息
                message_data: dict = json.loads(data)
                entry_action: str = message_data.get("entry_action", "chat_node")

                state["user_message"] = message_data.get("content", "")
                state["options"] = message_data.get("options", {})
                agent_nodes: list = state.get("agent_nodes", [])
                
                # 处理代理配置
                agent_config = message_data.get("agent_config", {})
                if agent_config:
                    for k, v in agent_config.items():
                        state[k] = v
                
                # 执行聊天处理
                chat_node = ChatNode()
                flow = Flow()
                flow[chat_node, *agent_nodes]
                await flow.arun(state, entry_action=entry_action)
    except Exception as e:
        print(f"订阅者错误: {e}")
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.aclose()


async def websocket_endpoint(websocket: WebSocket, agent_nodes: list = None):
    """WebSocket端点

    state 传递给 subscriber 然后传递给 chat_node和其他node，最后传递给 web_node
    """
    # 🔴接受连接
    await websocket.accept()

    # 🔴从前端接受会话ID {conversation: "会话ID"}
    data: str = await websocket.receive_text()
    msg: dict = json.loads(data)
    conversation: str = msg.get("conversation")
    if not conversation:
        await websocket.close()
        return

    # 🔴连接时自动加载历史记录并推送给前端 {"type": "history", "role": "user", "content": "用户消息"}
    for msg in await chat_db.get_all_messages(conversation):
        await websocket.send_text(json.dumps({"type": "history", **msg}))

    state: ChatState = {
        "websocket": websocket,  # 前端连接
        "messages": [], # 所有对话历史
        "conversation": conversation, # 当前对话的ID
        "tool_map": tool_map, # 工具调用映射
        "tool_context": {}, # 工具调用上下文
        "agent_nodes": agent_nodes, # 所有代理
        "options": {}, # 聊天选项
    }

    # 🔴并发启动发布者和订阅者
    await asyncio.gather(publisher(state=state), subscriber(state=state))

