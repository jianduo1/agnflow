#!/usr/bin/env python3
"""
🔍 Redis Pub/Sub 功能测试脚本

用于验证Redis pub/sub模式在多副本环境下的工作状态
"""

import asyncio
import json
import redis.asyncio as redis
from datetime import datetime

# Redis连接配置
REDIS_URL = "redis://localhost:6379"
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

async def test_publisher(conversation_id: str, message: str):
    """📡 测试发布者功能"""
    print(f"📡 发布消息到频道: chat:{conversation_id}")
    print(f"📝 消息内容: {message}")
    
    # 发布消息到Redis频道
    await redis_client.publish(f"chat:{conversation_id}", message)
    print(f"✅ 消息已发布")

async def test_subscriber(conversation_id: str):
    """📥 测试订阅者功能"""
    print(f"📥 订阅频道: chat:{conversation_id}")
    
    # 创建pub/sub连接
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(f"chat:{conversation_id}")
    
    try:
        # 监听消息
        async for message in pubsub.listen():
            if message["type"] == "message":
                data = message["data"]
                print(f"📨 收到消息: {data}")
                
                # 解析消息
                try:
                    msg_data = json.loads(data)
                    print(f"📋 解析结果: {msg_data}")
                except json.JSONDecodeError:
                    print(f"⚠️ 消息格式错误: {data}")
                
                # 模拟处理消息
                print(f"🔄 处理消息中...")
                await asyncio.sleep(1)
                print(f"✅ 消息处理完成")
                break
    finally:
        await pubsub.unsubscribe(f"chat:{conversation_id}")
        await pubsub.close()

async def test_multiple_subscribers(conversation_id: str):
    """🧪 测试多个订阅者"""
    print(f"🧪 测试多个订阅者 - 频道: chat:{conversation_id}")
    
    # 创建多个订阅者
    subscribers = []
    for i in range(3):
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(f"chat:{conversation_id}")
        subscribers.append(pubsub)
    
    # 发布消息
    message = json.dumps({
        "type": "user_message",
        "content": "Hello from test!",
        "timestamp": datetime.now().isoformat()
    })
    
    print(f"📡 发布消息: {message}")
    await redis_client.publish(f"chat:{conversation_id}", message)
    
    # 等待所有订阅者接收消息
    received_count = 0
    for i, pubsub in enumerate(subscribers):
        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    print(f"📥 订阅者 {i+1} 收到消息: {message['data']}")
                    received_count += 1
                    break
        except Exception as e:
            print(f"❌ 订阅者 {i+1} 错误: {e}")
        finally:
            await pubsub.unsubscribe(f"chat:{conversation_id}")
            await pubsub.close()
    
    print(f"📊 总计 {received_count} 个订阅者收到消息")

async def test_channel_cleanup():
    """🧹 测试频道清理"""
    print("🧹 测试频道清理")
    
    # 获取所有聊天频道
    channels = await redis_client.pubsub_channels("chat:*")
    print(f"📋 当前活跃频道: {channels}")
    
    # 清理测试频道
    for channel in channels:
        if "test" in channel:
            await redis_client.publish(channel, json.dumps({"type": "cleanup"}))
            print(f"🗑️ 清理频道: {channel}")

async def main():
    """🚀 主测试函数"""
    print("🚀 开始Redis Pub/Sub测试")
    print("=" * 50)
    
    # 测试基本功能
    conversation_id = "test_conversation_001"
    
    # 1. 测试单个发布者-订阅者
    print("\n1️⃣ 测试单个发布者-订阅者")
    print("-" * 30)
    
    # 启动订阅者
    subscriber_task = asyncio.create_task(test_subscriber(conversation_id))
    await asyncio.sleep(0.5)  # 等待订阅者准备就绪
    
    # 发布消息
    message = json.dumps({
        "type": "user_message",
        "content": "Hello World!",
        "reasoning": False,
        "tool_call": False,
        "timestamp": datetime.now().isoformat()
    })
    await test_publisher(conversation_id, message)
    
    # 等待订阅者完成
    await subscriber_task
    
    # 2. 测试多个订阅者
    print("\n2️⃣ 测试多个订阅者")
    print("-" * 30)
    await test_multiple_subscribers(conversation_id)
    
    # 3. 测试频道清理
    print("\n3️⃣ 测试频道清理")
    print("-" * 30)
    await test_channel_cleanup()
    
    print("\n✅ 所有测试完成!")
    print("=" * 50)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc() 