from agnflow.core.node import Node
from agnflow.core.flow import Flow
from agnflow.agent.llm import UserMsg, call_llm

global log_zh
log_zh = lambda *x: ...
class ChatNode(Node):
    def exec(self, state):
        # 如果是第一次运行，初始化消息列表
        if "messages" not in state:
            state["messages"] = []
            print("🎉 欢迎来到聊天！输入 'exit' 结束对话。")

        # 获取用户输入
        user_input = input("\n👤 你: ")
        if user_input.lower() == 'exit':
            return 

        # 将用户消息添加到历史记录
        state["messages"]+=UserMsg(user_input)
        messages = state["messages"]
        if messages is None:
            return 
        # 用完整的对话历史调用 LLM
        response = call_llm(messages)

        if messages is None or response is None:
            print("\n👋 再见！")
            return   # 结束对话

        # 打印助手的回复
        print(f"\n🤖 助手: {response}")

        # 将助手消息添加到历史记录
        state["messages"].append({"role": "assistant", "content": response})

        return self.name

if __name__ == "__main__":
    chat = ChatNode()
    flow = Flow()
    flow[chat >> chat]

    state = {}
    flow.run(state)
