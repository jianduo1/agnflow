from a2a.agent import Agent, AgentConfig
from a2a.message import Message
from a2a.integrations.openai import OpenAIClient  # 需安装扩展


class ChatGPTAgent(Agent):
    def __init__(self, agent_id: str, openai_api_key: str, endpoint: str = "http://localhost:8000"):
        # 配置智能体（支持聊天消息类型）
        config = AgentConfig(
            id=agent_id,
            name="ChatGPT智能体",
            description="使用OpenAI API处理自然语言请求",
            supported_message_types=[
                MessageType(
                    name="chat_request",
                    description="自然语言聊天请求",
                    schema={"type": "object", "properties": {"prompt": {"type": "string"}}, "required": ["prompt"]},
                )
            ],
        )
        super().__init__(config=config, endpoint=endpoint)
        self.openai_client = OpenAIClient(api_key=openai_api_key)

    async def handle_chat_request(self, message: Message):
        """调用OpenAI API处理聊天请求"""
        prompt = message.data.get("prompt", "你好")
        # 调用OpenAI ChatCompletion API
        response = await self.openai_client.chat_completion(
            model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}], max_tokens=200
        )
        return Message(
            type="chat_response",
            data={"reply": response.choices[0].message.content},
            correlation_id=message.correlation_id,
        )


# 启动智能体（需传入OpenAI API密钥）
async def run_chat_agent():
    api_key = "your-openai-api-key"  # 实际使用时从环境变量或配置文件获取
    agent = ChatGPTAgent(agent_id="chatgpt_agent_01", openai_api_key=api_key)
    await agent.start()


if __name__ == "__main__":
    import asyncio

    asyncio.run(run_chat_agent())
